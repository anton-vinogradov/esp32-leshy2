#!/usr/bin/env python3
"""Read-only design acceptance: execution success is not engineering acceptance.

One command rebuilds scoped audits from current Leshy2 inputs. Missing checks
remain unqualified; a passed scoped check never authorizes manufacture. Detailed
evidence stays under work/. This runner does not modify boards or fix findings.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout
import fcntl
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from threading import Event, Semaphore
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
KICAD_PYTHON = Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3')
from hardware.layout.h6_r2_parallel_process import ProcessRegistry
ADAPTERS = ('hardware.verification.h6_r2_acceptance_adapters',
            'hardware.layout.h6_r2_acceptance_adapters')
VERDICTS = {'pass', 'fail', 'unqualified', 'error'}
# Coverage is deliberately closed-world. Implementing an adapter does not
# implicitly qualify the other electrical, mechanical or production domains.
MISSING = {
    'coverage.pin-voltage-and-state': 'All exact pins: operating voltage/current, logic levels, unpowered states and source conduction across both boards.',
    'coverage.routed-power-and-loops': 'Actual copper: loaded rail drop, bottlenecks, decoupling ownership, converter loops and Kelvin feedback.',
    'coverage.signal-integrity-and-rf': 'Actual stackup, reference returns, USB/SDIO/display timing, RF transitions and coexistence.',
    'coverage.assembled-geometry': 'Complete tolerance-aware assembly, FPC bend/contact side, Cap mapping, holder/encoder geometry and NTC compression.',
    'coverage.manufacturing-package': 'Accepted-board-to-Gerber/drill/BOM/CPL parity and current exact-part factory availability.',
    'coverage.prototype-behavior': 'Measured power/startup, recovery, KILL, thermal and RF behavior within declared conditions.',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Non-finite JSON constant: ' + value)
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('Non-finite JSON number: ' + value)
        return number
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant,
                      parse_float=finite_float)


def decode_result(stdout, returncode):
    if returncode != 0:
        raise ValueError(f'Checker process exit code {returncode}; no result accepted')
    value = strict_json(stdout)
    if not isinstance(value, dict) or set(value) != {'verdict', 'scope', 'findings', 'details'}:
        raise ValueError('Checker must emit exactly the acceptance-result object')
    if not isinstance(value['verdict'], str) or value['verdict'] not in VERDICTS:
        raise ValueError('Unknown checker verdict')
    if not isinstance(value['scope'], str) or not value['scope'].strip():
        raise ValueError('Missing explicit check scope')
    if not isinstance(value['findings'], list) or any(not isinstance(s, str) or not s.strip() for s in value['findings']):
        raise ValueError('Findings must be nonempty strings')
    if not isinstance(value['details'], dict):
        raise ValueError('Details must be an object')
    if (value['verdict'] == 'pass') != (not value['findings']):
        raise ValueError('PASS cannot hide findings; non-PASS requires a reason')
    return value


def registry():
    result = {}
    for name in ADAPTERS:
        module = importlib.import_module(name)
        for check_id, spec in module.CHECKS.items():
            if check_id in result or spec.get('runtime') not in {'python', 'kicad'}:
                raise ValueError('Duplicate check or unsupported runtime: ' + check_id)
            result[check_id] = {**spec, 'adapter': name}
    builtin = {
        'native.inventory': {'runtime': 'kicad', 'scope': 'Complete assigned native component identities against independent current H2 ledgers.'},
        'native.drc': {'runtime': 'kicad', 'scope': 'Fresh native DRC, schematic parity and complete-board connectivity on both production boards.'},
    }
    for check_id, spec in {**builtin, **{k: {'scope': v, 'runtime': None} for k, v in MISSING.items()}}.items():
        if check_id in result:
            raise ValueError('Duplicate built-in check: ' + check_id)
        result[check_id] = {**spec, 'adapter': None}
    return result


def source_snapshot(root=ROOT):
    """Guard inputs AND membership, including new/deleted files, not just PCBs.

    Auditors separately prove freshness of any consumed derived evidence. This
    guard detects changes during execution; it does not bless old cached data.
    """
    paths = []
    # These are installed runtimes/caches, not sources of the registered audits.
    # Do not traverse the unrelated historical tscircuit node_modules tree.
    excluded_dirs = {'__pycache__', 'node_modules', '.venv'}
    for folder in (root / 'hardware', root / 'tools'):
        if folder.is_symlink():
            raise ValueError('Acceptance input root cannot be a symlink')
        for current, directories, files in os.walk(folder, followlinks=False):
            directories[:] = [name for name in directories if name not in excluded_dirs]
            for name in [*directories, *files]:
                path = Path(current) / name
                if path.is_symlink():
                    raise ValueError('Acceptance inputs cannot contain symlinks: ' + str(path))
                if path.is_file() and path.name != '.DS_Store' and path.suffix not in {'.pyc', '.kicad_prl', '.lck'}:
                    if not path.resolve().is_relative_to(root.resolve()):
                        raise ValueError('Acceptance input escapes repository: ' + str(path))
                    paths.append(path)
    if not paths:
        raise ValueError('No design inputs found')
    return {str(p.relative_to(root)): sha(p) for p in sorted(paths)}


def assess(specs, rows, inputs_unchanged):
    ids = [row.get('id') for row in rows]
    if not specs or len(ids) != len(set(ids)) or set(ids) != set(specs):
        raise ValueError('Acceptance requires exactly one result for every declared check')
    for row in rows:
        decode_result(json.dumps({key: row[key] for key in ('verdict', 'scope', 'findings', 'details')}, allow_nan=False), 0)
        if row['id'] in MISSING and row['verdict'] != 'unqualified':
            raise ValueError('An unimplemented mandatory check cannot pass')
    counts = dict(Counter(row['verdict'] for row in rows))
    status = 'error' if not inputs_unchanged or counts.get('error') else 'not_accepted' if counts.get('fail') or counts.get('unqualified') else 'pass_scoped'
    return {'status': status, 'checks': len(rows), 'verdict_counts': counts,
            'inputs_unchanged': inputs_unchanged,
            'engineering_accepted': status == 'pass_scoped',
            'production_promoted': False, 'fabrication_authorized': False,
            'model_decisions_in_run': 0,
            'blocked_checks': [r['id'] for r in rows if r['verdict'] != 'pass']}


def error_result(scope, message):
    return {'verdict': 'error', 'scope': scope, 'findings': [message], 'details': {}}


def run_process(command, folder, scope, timeout, processes=None):
    """Reuse the tested process registry; stdout is an exact JSON protocol."""
    started = time.monotonic()
    processes = processes if processes is not None else ProcessRegistry(grace_seconds=.5)
    try:
        execution = processes.run(command, folder / 'stdout.log', timeout, cwd=ROOT,
                                  env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                                  stderr_log=folder / 'stderr.log')
        if execution['exit_code'] != 0:
            raise ValueError(f'Checker execution {execution["exit_code"]}; no result accepted')
        if execution.get('orphaned_descendants'):
            raise ValueError('Checker left background descendants; process group stopped')
        result = decode_result((folder / 'stdout.log').read_text(), execution['returncode'])
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        result = error_result(scope, str(exc))
    return result, time.monotonic() - started


def evidence_snapshot(folder):
    files = sorted(folder.rglob('*'))
    if any(path.is_symlink() for path in files):
        raise ValueError('Evidence cannot contain symlinks')
    return {str(path.relative_to(folder)): sha(path) for path in files if path.is_file()}


def run_checks(checks, directory, kicad_python, timeout, jobs, native_jobs=1):
    """Parallel checks with separately bounded native KiCad concurrency.

    Every checker owns its subprocess group and evidence directory. Completion
    order never changes result ordering or acceptance requirements.
    """
    native_lane = Semaphore(native_jobs)
    processes = ProcessRegistry(Event(), grace_seconds=.5)
    def execute(item):
        check_id, spec = item
        folder = directory / check_id
        folder.mkdir()
        if check_id in MISSING:
            result = {'verdict': 'unqualified', 'scope': spec['scope'],
                      'findings': ['Mandatory coverage not implemented/qualified by this entrypoint.'],
                      'details': {'implemented': False}}
            elapsed = 0.0
        else:
            runtime = kicad_python if spec['runtime'] == 'kicad' else Path(sys.executable)
            command = [str(runtime), str(Path(__file__).resolve()), '--worker', check_id,
                       '--evidence-directory', str(folder)]
            if spec['runtime'] == 'kicad' or spec.get('native'):
                with native_lane:
                    result, elapsed = run_process(command, folder, spec['scope'], timeout, processes)
            else:
                result, elapsed = run_process(command, folder, spec['scope'], timeout, processes)
        return {'id': check_id, **result, 'seconds': round(elapsed, 3),
                'evidence_sha256': evidence_snapshot(folder)}
    results = {}
    pool = ThreadPoolExecutor(max_workers=jobs)
    pending = {}
    try:
        pending = {pool.submit(execute, item): item[0] for item in checks.items()}
        for index, future in enumerate(as_completed(pending), 1):
            row = future.result()
            results[row['id']] = row
            print(f'[{index}/{len(checks)}] {row["id"]}: {row["verdict"]}', file=sys.stderr, flush=True)
    except BaseException:
        processes.cancel_all()
        for future in pending:
            future.cancel()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    rows = [results[check_id] for check_id in checks]
    for row in rows:
        if evidence_snapshot(directory / row['id']) != row['evidence_sha256']:
            row.update(error_result(row['scope'], 'Checker evidence changed after validation'))
    return rows


def builtin_check(check_id, evidence):
    if check_id == 'native.inventory':
        from hardware.layout.h6_r2_component_inventory import build
        report = build()
        findings = [json.dumps(row, sort_keys=True) for row in report['findings']]
        return {'verdict': 'fail' if findings else 'pass', 'scope': report['scope'],
                'findings': findings, 'details': report['summary']}
    if check_id == 'native.drc':
        import pcbnew
        from hardware.layout.h6_r2_drc import PROJECTS, run_drc, validate_provenance
        findings, details = [], {}
        for project in PROJECTS:
            path = evidence / (project + '-drc.json')
            report = run_drc(project, path)
            validate_provenance(path, project)
            counts = {key: len(report[key]) for key in ('violations', 'schematic_parity', 'unconnected_items')}
            board = pcbnew.LoadBoard(str(ROOT / f'hardware/ecad/kicad/{project}/{project}.kicad_pcb'))
            board.BuildConnectivity()
            remaining = board.GetConnectivity().GetUnconnectedCount(False)
            if type(remaining) is not int or remaining < 0:
                raise ValueError('Invalid native connectivity count')
            details[project] = {**counts, 'native_remaining_connections': remaining,
                               'unconnected_items_may_be_report_limited': True,
                               'report': str(path.relative_to(ROOT)), 'sha256': sha(path)}
            for key, count in counts.items():
                if count:
                    findings.append(f'{project}: {count} {key}')
            if remaining:
                findings.append(f'{project}: {remaining} remaining connections from native connectivity (not the capped DRC list)')
        return {'verdict': 'fail' if findings else 'pass', 'scope': 'Both complete native boards: DRC, schematic parity and remaining connectivity.',
                'findings': findings, 'details': details}
    raise ValueError('Unknown built-in check: ' + check_id)


def worker(check_id, evidence):
    checks = registry()
    spec = checks[check_id]
    try:
        with redirect_stdout(sys.stderr):
            result = (importlib.import_module(spec['adapter']).run_check(check_id)
                      if spec['adapter'] else builtin_check(check_id, evidence))
        decode_result(json.dumps(result, allow_nan=False), 0)
    except Exception as exc:
        import traceback
        traceback.print_exc(file=sys.stderr)
        result = error_result(spec['scope'], f'{type(exc).__name__}: {exc}')
    print(json.dumps(result, allow_nan=False))


def safe_work():
    path = ROOT / 'work'
    path.mkdir(exist_ok=True)
    if path.is_symlink() or path.resolve().parent != ROOT.resolve():
        raise ValueError('Evidence must stay in the repository work directory')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-python', type=Path, default=KICAD_PYTHON)
    parser.add_argument('--timeout', type=int, default=180, help='Per-check timeout, seconds')
    parser.add_argument('--jobs', type=int, default=min(8, max(1, (os.cpu_count() or 2) - 2)),
                        help='Parallel independent checks')
    parser.add_argument('--native-jobs', type=int,
                        help='Native KiCad concurrency; default=min(4,jobs), serial baseline=1')
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    parser.add_argument('--evidence-directory', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.native_jobs is None:
        args.native_jobs = min(4, args.jobs)
    if args.timeout <= 0:
        parser.error('Timeout must be positive')
    if not 1 <= args.jobs <= 64:
        parser.error('Jobs must be in 1..64')
    if not 1 <= args.native_jobs <= min(8, args.jobs):
        parser.error('Native jobs must be in 1..min(8,jobs)')
    work = safe_work()
    if args.worker:
        directory = args.evidence_directory
        if directory is None or not directory.is_dir() or not directory.resolve().is_relative_to(work.resolve()) or directory.is_symlink():
            parser.error('Worker requires an existing evidence directory under work/')
        worker(args.worker, directory)
        return 0
    started = time.monotonic()
    def interrupted(signum, frame):
        raise KeyboardInterrupt('Acceptance cancelled')
    signal.signal(signal.SIGTERM, interrupted)
    # Share the existing native validation lock; independent checks continue
    # after a design finding, but no concurrent validation alters the evidence.
    with (work / 'h6-validation.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(2, 'Another native validation is running.\n')
        checks = registry()
        directory = Path(tempfile.mkdtemp(prefix='design-check-', dir=work))
        before = source_snapshot()
        from tools.route_board import keep_awake
        awake = {}
        with keep_awake(awake, directory):
            rows = run_checks(checks, directory, args.kicad_python, args.timeout, args.jobs, args.native_jobs)
        after = source_snapshot()
        summary = assess(checks, rows, before == after)
        summary['seconds'] = round(time.monotonic() - started, 3)
        report = {'schema_version': 1, 'scope': 'Current Leshy2 read-only acceptance; not a circuit synthesizer or fabrication release.',
                  'summary': summary, 'source_sha256': before, 'checks': rows,
                  'changed_inputs': sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k)),
                  'caffeinate': awake,
                  'runtime': {'python': sys.version, 'kicad_python': str(args.kicad_python),
                              'parallel_jobs': args.jobs, 'native_jobs': args.native_jobs,
                              'logical_cpu_count': os.cpu_count()}}
        output = directory / 'result.json'
        with output.open('x') as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')
        # Console output describes exactly the persisted result, not a parallel
        # status calculation or a cached previous success.
        if strict_json(output.read_text()) != report:
            raise ValueError('Saved acceptance report does not match the run')
        print(json.dumps({**summary, 'report': str(output.relative_to(ROOT)), 'report_sha256': sha(output)}))
        return 2 if summary['status'] == 'error' else 0 if summary['status'] == 'pass_scoped' else 1


def cli():
    try:
        return main()
    except (Exception, KeyboardInterrupt) as exc:
        # Bootstrap/persistence faults must not masquerade as a design finding
        # (exit 1), nor point to a previous run's report. Context managers above
        # release the lock, caffeinate assertion and owned process groups.
        import traceback
        traceback.print_exc(file=sys.stderr)
        cancelled = isinstance(exc, KeyboardInterrupt)
        print(json.dumps({'status': 'cancelled' if cancelled else 'error',
                          'error': f'{type(exc).__name__}: {exc}', 'report': None,
                          'engineering_accepted': False, 'production_promoted': False,
                          'fabrication_authorized': False}))
        return 130 if cancelled else 2


if __name__ == '__main__':
    raise SystemExit(cli())
