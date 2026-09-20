"""Joint static corner diagnostics: no test qualifies a replacement power cell."""
from contextlib import nullcontext, redirect_stdout
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import synthesize_main_static_pair as tool


def nominal_fixture(reference, required, top, bottom, impedance, leakage):
    """Test fixture only, not an alternate production preferred-number solver."""
    rt, rb = (F(44200), F(10100)) if reference.maximum < 1 else (F('10.5'), F(10000))
    checked = tool.pair.verify_candidate(rt, rb, reference, required, top, bottom, impedance)
    return dict(status='conditional_candidate', qualified=False,
                selected_nominal_ohm_exact={'top': str(rt), 'bottom': str(rb)}, **checked)


class StaticPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tool.source.load_current()
        cls.monitors = {row['id']: row for row in tool.monitor_hypotheses()}

    def test_current_demands_and_hysteresis_reference_preserved(self):
        demand = tool.compare.demands(self.data)
        self.assertEqual(len(demand['cases']), 58)
        self.assertEqual(max(i for _, i in demand['cases']), F('4.25'))
        self.assertEqual(tuple(map(F, (demand['consumer_min_v'], demand['consumer_max_v'], demand['ripple_half_v']))),
                         (F(3), F('3.3'), F('.01')))
        monitor = self.monitors['tps3703a7330']
        self.assertEqual(monitor['falling'], F('3.047517'))
        self.assertEqual(monitor['rising'], F('3.115206864'))
        self.assertEqual(monitor['ov_falling'], F('3.531')*F('.993')*F('.992'))

    def test_3890_native_distribution_continuously_infeasible_before_selector(self):
        for kind in tool.CLASSES:
            result = tool.synthesize(self.data, kind, F('.05'), self.monitors['tps389001'],
                                     solver=lambda *args: self.fail('impossible continuous window reached EDG'))
            self.assertEqual(result['status'], 'continuous_joint_infeasible')
            self.assertLess(F(result['continuous_joint_margin_v_exact']), 0)
            self.assertFalse(result['qualified'])

    def test_both_actual_nominals_and_all_load_cases_get_exact_validation(self):
        row = tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), self.monitors['tps3703a7330'],
                              solver=nominal_fixture)
        self.assertEqual(row['status'], 'conditional_joint_candidate')
        self.assertEqual(row['consumer_check']['checked_load_cases'], 58)
        self.assertEqual(set(row['headroom_v_exact']), {'consumer_lower', 'raw_upper', 'raw_lower',
                                                       'monitor_falling', 'monitor_rising', 'monitor_ov_false_fault'})
        self.assertTrue(all(F(value) > 0 for value in row['headroom_v_exact'].values()))
        self.assertGreater(F(row['monitor_divider_load_upper_a_exact']), F('.0003'))
        self.assertFalse(row['divider_load_admitted_to_current_budget'])
        self.assertFalse(row['qualified'])

    def test_claimed_good_corner_cannot_hide_bad_or_changed_resistor(self):
        for mutate in (lambda row: row['average_v_exact'].__setitem__(0, '3.2'),
                       lambda row: row['selected_nominal_ohm_exact'].__setitem__('top', '100000')):
            def corrupt(*args):
                row = nominal_fixture(*args)
                mutate(row)
                return row
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), self.monitors['tps3703a7330'], solver=corrupt)

    def test_overvoltage_false_fault_is_not_ignored(self):
        monitor = {**self.monitors['tps3703a7330'], 'ov_falling': F(3)}
        with self.assertRaisesRegex(ValueError, 'headroom'):
            tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), monitor, solver=nominal_fixture)

    def test_invalid_distribution_or_undeclared_class_is_rejected(self):
        for kind, drop in (('ideal', F('.05')), ('0.1pct_10ppm', F('-.01')), ('0.1pct_10ppm', .05)):
            with self.subTest(kind=kind, drop=drop), self.assertRaises(ValueError):
                tool.synthesize(self.data, kind, drop, self.monitors['tps3703a7330'])

    def test_no_match_is_bounded_search_not_infeasibility(self):
        row = tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), self.monitors['tps3703a7330'],
                              solver=lambda *args: {'status': 'preferred_selector_found_no_candidate'})
        self.assertEqual(row['status'], 'bounded_edg_search_no_pair')
        self.assertGreater(F(row['continuous_joint_margin_v_exact']), 0)

    def test_run_preserves_native_default_separates_ron_and_current_limit(self):
        before = deepcopy(self.data)
        with patch.object(tool.source, 'load_current', return_value=self.data), \
                patch.object(tool.pair, '_load_edg'), \
                patch.object(tool, 'synthesize', return_value={'qualified': False}) as synthesis:
            report = tool.run()
        self.assertEqual(before, self.data)
        self.assertEqual(synthesis.call_count, 4)
        self.assertTrue(all(call.args[2] == F('.05') for call in synthesis.call_args_list))
        self.assertEqual(report['checked_load_cases'], 58)
        self.assertTrue(report['distribution_is_native'])
        self.assertEqual(report['status'], 'not_qualified')
        self.assertFalse(report['qualified'])
        self.assertFalse(report['current_limit_model_combined'])
        candidate_scope = report['ron_source_scope']['rows'][1]
        self.assertIn('iout_a', candidate_scope['missing_source_domains'])
        self.assertFalse(candidate_scope['qualified'])
        self.assertIn('tools/synthesize_main_static_pair.py', report['source_sha256'])
        self.assertEqual(report['selector']['installed_implementation_sha256'], tool.pair.EDG_SOURCE_SHA256)

    def test_changed_installed_runtime_after_all_rows_is_rejected(self):
        completed = []
        def row(*args):
            completed.append(args[1])
            return {'qualified': False}
        def stale_runtime():
            self.assertEqual(len(completed), 4)
            raise ValueError('unreviewed EDG numerical source after calculation')
        with patch.object(tool.source, 'load_current', return_value=self.data), \
                patch.object(tool, 'synthesize', side_effect=row), \
                patch.object(tool.pair, '_load_edg', side_effect=stale_runtime), \
                self.assertRaisesRegex(ValueError, 'after calculation'):
            tool.run()

    def test_sources_changed_during_run_rejected(self):
        snapshot = tool.source.snapshot
        calls = 0
        def changed(paths):
            nonlocal calls
            calls += 1
            return snapshot(paths) if calls == 1 else {}
        with patch.object(tool.source, 'load_current', return_value=self.data), \
                patch.object(tool.source, 'snapshot', side_effect=changed), \
                patch.object(tool.pair, '_load_edg'), \
                patch.object(tool, 'synthesize', return_value={'qualified': False}), \
                self.assertRaisesRegex(ValueError, 'Sources changed'):
            tool.run()

    def test_error_or_cancel_does_not_publish_report(self):
        for error, code, status in ((ValueError('stale'), 2, 'execution_error'),
                                     (KeyboardInterrupt(), 130, 'cancelled')):
            stream = StringIO()
            with patch.object(sys, 'argv', ['static-pair']), patch.object(tool, 'run', side_effect=error), \
                    patch.object(tool, 'keep_awake', return_value=nullcontext()), redirect_stdout(stream):
                self.assertEqual(tool.main(), code)
            self.assertEqual(json.loads(stream.getvalue())['status'], status)
            self.assertIsNone(json.loads(stream.getvalue())['report'])

    def test_sources_changed_before_publication_leaves_no_result_file(self):
        stream = StringIO()
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as directory, \
                patch.object(sys, 'argv', ['static-pair']), \
                patch.object(tool.tempfile, 'mkdtemp', return_value=directory), \
                patch.object(tool, 'keep_awake', return_value=nullcontext()), \
                patch.object(tool, 'run', return_value={'source_sha256': {'tools/synthesize_main_static_pair.py': 'stale'}}), \
                redirect_stdout(stream):
            self.assertEqual(tool.main(), 2)
            self.assertFalse((Path(directory)/'result.json').exists())
        response = json.loads(stream.getvalue())
        self.assertIsNone(response['report'])
        self.assertIn('before report publication', response['error'])

    def test_changed_installed_runtime_before_publication_leaves_no_report(self):
        stream = StringIO()
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as directory, \
                patch.object(sys, 'argv', ['static-pair']), \
                patch.object(tool.tempfile, 'mkdtemp', return_value=directory), \
                patch.object(tool, 'keep_awake', return_value=nullcontext()), \
                patch.object(tool, 'run', return_value={'source_sha256': {}}), \
                patch.object(tool.pair, '_load_edg', side_effect=ValueError('unreviewed EDG numerical source')), \
                redirect_stdout(stream):
            self.assertEqual(tool.main(), 2)
            self.assertFalse((Path(directory)/'result.json').exists())
        response = json.loads(stream.getvalue())
        self.assertIsNone(response['report'])
        self.assertIn('unreviewed EDG', response['error'])


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class StaticPairEdgTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tool.source.load_current()
        cls.monitors = {row['id']: row for row in tool.monitor_hypotheses()}

    def test_ready_edg_near_unity_seed_and_exact_margins(self):
        for kind in tool.CLASSES:
            row = tool.synthesize(self.data, kind, F('.05'), self.monitors['tps3703a7330'])
            self.assertEqual(row['status'], 'conditional_joint_candidate')
            self.assertIn('initial_decade_retry', row['monitor_pair']['selector'])
            self.assertEqual(row['feedback']['selected_nominal_ohm_exact'], {'top': '44200', 'bottom': '10100'})
            self.assertEqual(row['monitor_pair']['selected_nominal_ohm_exact'], {'top': '21/2', 'bottom': '10000'})
            self.assertTrue(all(F(value) > 0 for value in row['headroom_v_exact'].values()))
            self.assertFalse(row['qualified'])

    def test_3890_alternate_distribution_is_only_an_explicit_hypothesis(self):
        row = tool.synthesize(self.data, '0.05pct_10ppm', F('.03'), self.monitors['tps389001'])
        self.assertEqual(row['status'], 'conditional_joint_candidate')
        self.assertEqual(row['monitor_pair']['selected_nominal_ohm_exact'], {'top': '20000', 'bottom': '12000'})
        self.assertEqual(row['distribution_drop_v_exact'], '3/100')
        self.assertTrue(all(F(value) > 0 for value in row['headroom_v_exact'].values()))
        self.assertFalse(row['qualified'])


if __name__ == '__main__':
    unittest.main()
