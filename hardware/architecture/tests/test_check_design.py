"""Acceptance runner negatives: test the judge, not just a good PCB."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from threading import Event, Lock

from tools.check_design import (MISSING, assess, builtin_check, cli, decode_result, run_process,
                                run_checks, source_snapshot, strict_json)


def result(verdict='pass'):
    return {'verdict': verdict, 'scope': 'fixture-only check',
            'findings': [] if verdict == 'pass' else ['deliberate fixture finding'],
            'details': {}}


class ProtocolTests(unittest.TestCase):
    def test_bootstrap_error_and_cancel_cannot_look_like_design_failure(self):
        for exc, code, status in ((ValueError('invalid source'), 2, 'error'),
                                  (KeyboardInterrupt('stop'), 130, 'cancelled')):
            output = io.StringIO()
            with self.subTest(status=status), patch('tools.check_design.main', side_effect=exc), \
                 redirect_stdout(output), redirect_stderr(io.StringIO()):
                self.assertEqual(cli(), code)
            observed = json.loads(output.getvalue())
            self.assertEqual(observed['status'], status)
            self.assertIsNone(observed['report'])
            self.assertFalse(observed['engineering_accepted'])

    def test_good_scoped_result(self):
        self.assertEqual(decode_result(json.dumps(result()), 0), result())

    def test_nonzero_process_cannot_supply_pass(self):
        for code in (1, 2, -9):
            with self.subTest(code=code), self.assertRaises(ValueError):
                decode_result(json.dumps(result()), code)

    def test_malformed_and_ambiguous_json(self):
        valid = json.dumps(result())
        for value in ('', '{}', '[]', 'null', 'true', valid + valid,
                      'notice\n' + valid, valid + '\nnotice', valid[:-1],
                      valid.replace('"details": {}', '"details": {"x":NaN}'),
                      valid.replace('"details": {}', '"details": {"x":Infinity}'),
                      valid.replace('"details": {}', '"details": {"x":[1e999]}'),
                      valid.replace('"details": {}', '"details": {"x":{"y":-1e999}}'),
                      valid.replace('"details": {}', '"details": {"x":1,"x":2}'),
                      valid.replace('"verdict": "pass"', '"verdict":"fail","verdict":"pass"')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_result(value, 0)

    def test_result_semantics_are_not_truthiness(self):
        changes = ({'verdict': True}, {'verdict': 'review_required'},
                   {'verdict': 'unqualified'}, {'findings': ['hidden finding']},
                   {'scope': ''}, {'scope': False}, {'details': []},
                   {'findings': 'none'}, {'findings': ['']}, {'extra': 'ignored?'})
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                decode_result(json.dumps({**result(), **change}), 0)


class AssessmentTests(unittest.TestCase):
    def test_fixture_pass_is_not_fabrication_authorization(self):
        report = assess({'test': {}}, [{'id': 'test', **result()}], True)
        self.assertEqual(report['status'], 'pass_scoped')
        self.assertTrue(report['engineering_accepted'])
        self.assertFalse(report['production_promoted'])
        self.assertFalse(report['fabrication_authorized'])

    def test_every_nonpass_verdict_blocks(self):
        for verdict in ('fail', 'unqualified', 'error'):
            report = assess({'test': {}}, [{'id': 'test', **result(verdict)}], True)
            self.assertEqual(report['status'], 'error' if verdict == 'error' else 'not_accepted')
            self.assertFalse(report['engineering_accepted'])

    def test_coverage_is_closed_world(self):
        good = {'id': 'test', **result()}
        for specs, rows in (({}, []), ({'test': {}}, []),
                            ({'test': {}}, [good, good]),
                            ({'test': {}, 'missing': {}}, [good]),
                            ({'wrong': {}}, [good])):
            with self.subTest(specs=specs, rows=rows), self.assertRaises(ValueError):
                assess(specs, rows, True)

    def test_missing_implementation_cannot_self_approve(self):
        check_id = next(iter(MISSING))
        with self.assertRaises(ValueError):
            assess({check_id: {}}, [{'id': check_id, **result()}], True)
        self.assertEqual(assess({check_id: {}}, [{'id': check_id, **result('unqualified')}], True)['status'], 'not_accepted')

    def test_source_change_overrides_all_passes(self):
        report = assess({'test': {}}, [{'id': 'test', **result()}], False)
        self.assertEqual(report['status'], 'error')
        self.assertFalse(report['engineering_accepted'])


class InputTests(unittest.TestCase):
    def test_changes_additions_deletions_and_tools_are_guarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('hardware', 'tools'):
                (root / name).mkdir()
            source = root / 'hardware' / 'part.json'
            source.write_text('one')
            initial = source_snapshot(root)
            source.write_text('two')
            self.assertNotEqual(initial, source_snapshot(root))
            source.write_text('one')
            added = root / 'tools' / 'checker.py'
            added.write_text('checker')
            changed = source_snapshot(root)
            self.assertNotEqual(initial, changed)
            source.unlink()
            self.assertNotEqual(changed, source_snapshot(root))

    def test_symlink_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'hardware').mkdir()
            (root / 'outside').write_text('outside')
            (root / 'hardware' / 'link').symlink_to(root / 'outside')
            with self.assertRaises(ValueError):
                source_snapshot(root)

    def test_directory_symlink_cannot_hide_input_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'hardware').mkdir()
            (root / 'outside').mkdir()
            (root / 'outside' / 'part').write_text('external')
            (root / 'hardware' / 'link').symlink_to(root / 'outside', target_is_directory=True)
            with self.assertRaises(ValueError):
                source_snapshot(root)


class NativeConnectivityTests(unittest.TestCase):
    def check_fixture(self, remaining, listed=0):
        """An empty/truncated CLI list cannot override native connectivity."""
        connectivity = SimpleNamespace(GetUnconnectedCount=lambda _: remaining)
        board = SimpleNamespace(BuildConnectivity=lambda: None,
                                GetConnectivity=lambda: connectivity)
        native = SimpleNamespace(LoadBoard=lambda _: board)
        report = {'violations': [], 'schematic_parity': [],
                  'unconnected_items': [{}] * listed}
        drc = SimpleNamespace(PROJECTS=['fixture'], run_drc=lambda *args: report,
                              validate_provenance=lambda *args: None)
        with patch.dict(sys.modules, {'pcbnew': native, 'hardware.layout.h6_r2_drc': drc}), \
             patch('tools.check_design.ROOT', Path('/fixture')), \
             patch('tools.check_design.sha', return_value='fixture-only-hash'):
            return builtin_check('native.drc', Path('/fixture/work/evidence'))

    def test_native_opens_fail_even_when_drc_list_is_empty(self):
        observed = self.check_fixture(7)
        self.assertEqual(observed['verdict'], 'fail')
        self.assertEqual(observed['details']['fixture']['native_remaining_connections'], 7)

    def test_both_native_and_cli_must_be_clean(self):
        self.assertEqual(self.check_fixture(0)['verdict'], 'pass')
        self.assertEqual(self.check_fixture(0, listed=1)['verdict'], 'fail')

    def test_invalid_native_count_is_not_zero(self):
        for count in (False, True, None, -1, 0.0, '0'):
            with self.subTest(count=count), self.assertRaises(ValueError):
                self.check_fixture(count)


class ProcessTests(unittest.TestCase):
    def run_fixture(self, code, timeout=5):
        with tempfile.TemporaryDirectory() as tmp:
            return run_process([sys.executable, '-c', code], Path(tmp), 'fixture', timeout)[0]

    def test_separate_stderr_and_exact_stdout(self):
        payload = json.dumps(result())
        observed = self.run_fixture(f'import sys; print("diagnostic",file=sys.stderr); print({payload!r})')
        self.assertEqual(observed, result())

    def test_crash_cannot_reuse_printed_pass(self):
        payload = json.dumps(result())
        observed = self.run_fixture(f'import sys; print({payload!r}); sys.exit(3)')
        self.assertEqual(observed['verdict'], 'error')

    def test_timeout_kills_descendants_not_just_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            marker = folder / 'orphan-was-alive'
            child = f'import time; from pathlib import Path; time.sleep(1.0); Path({str(marker)!r}).touch()'
            parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{child!r}]); time.sleep(5)'
            observed, _ = run_process([sys.executable, '-c', parent], folder, 'fixture', .2)
            self.assertEqual(observed['verdict'], 'error')
            time.sleep(1.1)
            self.assertFalse(marker.exists())

    def test_missing_executable_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            observed, _ = run_process(['/not/a/real/executable'], Path(tmp), 'fixture', 1)
            self.assertEqual(observed['verdict'], 'error')

    def test_successful_parent_cannot_leave_a_background_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            marker = folder / 'late-write'
            child = f'import time; from pathlib import Path; time.sleep(1); Path({str(marker)!r}).touch()'
            parent = f'import subprocess,sys; subprocess.Popen([sys.executable,"-c",{child!r}]); print({json.dumps(result())!r})'
            observed, _ = run_process([sys.executable, '-c', parent], folder, 'fixture', 5)
            self.assertEqual(observed['verdict'], 'error')
            time.sleep(1.1)
            self.assertFalse(marker.exists())

    def test_parallel_python_and_serial_native_lanes(self):
        counts = {'active': 0, 'native': 0, 'peak': 0, 'native_peak': 0}
        lock = Lock()
        def execute(command, folder, scope, timeout, processes=None):
            native = folder.name.startswith('native')
            with lock:
                counts['active'] += 1
                counts['native'] += int(native)
                counts['peak'] = max(counts['peak'], counts['active'])
                counts['native_peak'] = max(counts['native_peak'], counts['native'])
            time.sleep(.1)
            with lock:
                counts['active'] -= 1
                counts['native'] -= int(native)
            return result(), .1
        checks = {name: {'runtime': 'kicad' if name.startswith('native') else 'python', 'scope': 'fixture'}
                  for name in ('native1', 'python1', 'native2', 'python2')}
        with tempfile.TemporaryDirectory() as tmp, patch('tools.check_design.run_process', side_effect=execute):
            rows = run_checks(checks, Path(tmp), Path(sys.executable), 5, 4)
        self.assertEqual([r['id'] for r in rows], list(checks))
        self.assertGreaterEqual(counts['peak'], 2)
        self.assertEqual(counts['native_peak'], 1)

    def test_native_concurrency_can_be_increased_but_remains_bounded(self):
        counts = {'active': 0, 'peak': 0}
        lock = Lock()
        def execute(command, folder, scope, timeout, processes):
            with lock:
                counts['active'] += 1
                counts['peak'] = max(counts['peak'], counts['active'])
            time.sleep(.1)
            with lock:
                counts['active'] -= 1
            return result(), .1
        checks = {f'native{i}': {'runtime': 'kicad', 'scope': 'fixture'} for i in range(4)}
        with tempfile.TemporaryDirectory() as tmp, patch('tools.check_design.run_process', side_effect=execute):
            run_checks(checks, Path(tmp), Path(sys.executable), 5, 4, native_jobs=2)
        self.assertEqual(counts['peak'], 2)

    def test_cancel_stops_active_and_queued_checks(self):
        started = Event()
        original = run_process
        registries = []
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            marker = folder / 'late-write'
            code = f'import time; from pathlib import Path; time.sleep(2); Path({str(marker)!r}).touch()'
            def execute(command, evidence, scope, timeout, processes):
                registries.append(processes)
                started.set()
                return original([sys.executable, '-c', code], evidence, scope, 30, processes)
            def interrupt(futures):
                self.assertTrue(started.wait(2))
                raise KeyboardInterrupt('synthetic user stop')
            checks = {f'native{i}': {'runtime': 'kicad', 'scope': 'fixture'} for i in range(5)}
            begin = time.monotonic()
            with patch('tools.check_design.run_process', side_effect=execute), \
                 patch('tools.check_design.as_completed', side_effect=interrupt), \
                 self.assertRaises(KeyboardInterrupt):
                run_checks(checks, folder, Path(sys.executable), 30, 3)
            self.assertLess(time.monotonic() - begin, 3)
            self.assertTrue(all(r.cancel_event.is_set() and r.active_count == 0 for r in registries))
            time.sleep(2.1)
            self.assertFalse(marker.exists())

    def test_evidence_changed_after_completed_check_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            def execute(command, folder, scope, timeout, processes):
                (folder / 'proof').write_text('original')
                if folder.name == 'second':
                    (directory / 'first' / 'proof').write_text('changed')
                return result(), .1
            checks = {name: {'runtime': 'python', 'scope': 'fixture'} for name in ('first', 'second')}
            with patch('tools.check_design.run_process', side_effect=execute):
                rows = run_checks(checks, directory, Path(sys.executable), 5, 1)
            self.assertEqual(rows[0]['verdict'], 'error')
            self.assertIn('changed', rows[0]['findings'][0])


if __name__ == '__main__':
    unittest.main()
