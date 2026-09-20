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

    def test_feedback_impedance_window_must_be_positive_ordered_exact(self):
        for window in ((F(1000), F(500)), (F(0), F(1000)), (500, 1000), (F(500),)):
            with self.subTest(window=window), self.assertRaises(ValueError):
                tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), self.monitors['tps3703a7330'],
                                fb_impedance_ohm=window)

    def test_no_match_is_bounded_search_not_infeasibility(self):
        row = tool.synthesize(self.data, '0.1pct_10ppm', F('.05'), self.monitors['tps3703a7330'],
                              solver=lambda *args: {'status': 'preferred_selector_found_no_candidate'})
        self.assertEqual(row['status'], 'bounded_edg_search_no_pair')
        self.assertGreater(F(row['continuous_joint_margin_v_exact']), 0)

    def test_run_preserves_native_default_separates_ron_and_current_limit(self):
        before = deepcopy(self.data)
        with patch.object(tool.source, 'load_current', return_value=self.data), \
                patch.object(tool.pair, '_load_edg'), \
                patch.object(tool, 'portfolio', return_value={}), patch.object(tool, 'verify_portfolio', return_value={}), \
                patch.object(tool, 'synthesize', return_value={'status': 'continuous_joint_infeasible', 'qualified': False}) as synthesis:
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
        self.assertIn('tools/compare_main_current_limit.py', report['source_sha256'])
        self.assertEqual(report['selector']['installed_implementation_sha256'], tool.pair.EDG_SOURCE_SHA256)

    def test_changed_installed_runtime_after_all_rows_is_rejected(self):
        completed = []
        def row(*args, **kwargs):
            completed.append(args[1])
            return {'status': 'continuous_joint_infeasible', 'qualified': False}
        def stale_runtime():
            self.assertEqual(len(completed), 4)
            raise ValueError('unreviewed EDG numerical source after calculation')
        with patch.object(tool.source, 'load_current', return_value=self.data), \
                patch.object(tool, 'portfolio', return_value={}), patch.object(tool, 'verify_portfolio', return_value={}), \
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
                patch.object(tool, 'portfolio', return_value={}), patch.object(tool, 'verify_portfolio', return_value={}), \
                patch.object(tool, 'synthesize', return_value={'status': 'continuous_joint_infeasible', 'qualified': False}), \
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


class LoadedPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tool.source.load_current()
        cls.monitor = next(row for row in tool.monitor_hypotheses() if row['id'] == 'tps3703a7330')
        cls.row = tool.synthesize(cls.data, '0.1pct_10ppm', F('.05'), cls.monitor, solver=nominal_fixture)

    def test_point_kcl_and_feedback_branch_bypasses_efuse(self):
        point = tool.loaded_point(*map(F, (1, 4, 1, 0, 2, 3, 0, 1, 1)))
        self.assertEqual(point['raw_v'], 5)
        self.assertEqual(point['local_v'], F(10, 3))
        self.assertEqual(point['sense_v'], 2)
        self.assertEqual(point['monitor_top_current_a'], F(2, 3))
        self.assertEqual(point['efuse_current_a'], F(5, 3))
        self.assertEqual(point['converter_current_a'], F(8, 3))
        changed = tool.loaded_point(*map(F, (1, 8, 2, 0, 2, 3, 0, 1, 1)))
        self.assertEqual(point['local_v'], changed['local_v'])
        self.assertEqual(point['efuse_current_a'], changed['efuse_current_a'])
        self.assertEqual(point['converter_current_a']-changed['converter_current_a'], F(1, 2))

    def test_ripple_changes_feedback_branch_by_total_resistance(self):
        base = tool.loaded_point(*map(F, (1, 4, 1, 0, 2, 3, 0, 1, 1)))
        point = tool.loaded_point(*map(F, (1, 4, 1, 0, 2, 3, 0, 1, 1)), raw_ripple_v=F('.01'))
        self.assertEqual(point['raw_v']-base['raw_v'], F('.01'))
        self.assertEqual(point['feedback_top_current_a']-base['feedback_top_current_a'], F('.002'))

    def test_signed_injection_is_preserved_not_clamped(self):
        point = tool.loaded_point(*map(F, (1, 4, 1, 0, 2, 3, -2, 1, 1)))
        self.assertEqual(point['local_v'], F(13, 3))
        self.assertEqual(point['monitor_top_current_a'], F(-1, 3))
        empty = tool.loaded_point(*map(F, (1, 4, 1, 0, 2, 3, -2, 0, 1)))
        self.assertGreater(empty['local_v'], empty['raw_v'])
        self.assertEqual(empty['efuse_current_a'], F(-1, 6))

    def test_point_domains_fail_closed(self):
        valid = list(map(F, (1, 4, 1, 0, 2, 3, 0, 1, 1)))
        for index, bad in ((0, 1.0), (2, F(0)), (7, F(-1)), (8, F(-1))):
            values = valid.copy()
            values[index] = bad
            with self.subTest(index=index, bad=bad), self.assertRaises(ValueError):
                tool.loaded_point(*values)

    def test_unknown_bias_is_not_an_implicit_zero(self):
        unknown = tool.loaded_diagnostic(self.data, self.row, self.monitor, None, tool.Interval(0, 0))
        self.assertEqual(unknown['status'], 'not_evaluated_unknown_bias')
        self.assertFalse(unknown['source_applicability'])
        self.assertFalse(unknown['qualified'])
        with self.assertRaises(ValueError):
            tool.loaded_diagnostic(self.data, self.row, self.monitor, [0, 0], tool.Interval(0, 0))

    def test_explicit_zero_bias_adds_both_branches_without_moving_feedback_load(self):
        before = deepcopy(self.data)
        result = tool.loaded_diagnostic(self.data, self.row, self.monitor, tool.Interval(0, 0), tool.Interval(0, 0))
        self.assertEqual(result['status'], 'conditional_static_pass')
        self.assertEqual(result['checked_load_cases'], 58)
        self.assertEqual([r['name'] for r in result['cases']], [name for name, _ in self.data['cases']])
        peak = next(r for r in result['cases'] if F(r['native_load_a_exact']) == F('4.25'))
        efuse = F(peak['bounds_exact']['efuse_current_a'][1])
        source = F(peak['bounds_exact']['converter_current_a'][1])
        self.assertGreater(efuse, F('4.25'))
        self.assertGreater(source, efuse)
        self.assertEqual(before, self.data)
        self.assertFalse(result['source_applicability'])
        self.assertFalse(result['qualified'])
        self.assertEqual(result['actual_source_bias_bounds_a'], {'feedback': None, 'sense': None})

    def test_declared_signed_bias_rejects_original_candidate(self):
        result = tool.loaded_diagnostic(self.data, self.row, self.monitor,
                                        tool.Interval('-.000001', '.000001'), tool.Interval('-.0000015', '.0000015'))
        self.assertEqual(result['status'], 'conditional_static_fail')
        self.assertIn('raw_upper', result['failed_checks'])
        self.assertIn('monitor_rising_sense', result['failed_checks'])
        self.assertAlmostEqual(float(F(result['raw_v_exact'][1])), 3.3390990249767154)
        self.assertEqual(result['checked_load_cases'], 58)
        self.assertEqual(self.row['status'], 'conditional_joint_candidate')
        self.assertFalse(result['qualified'])

    def test_reverse_branch_operating_domain_is_not_accepted(self):
        result = tool.loaded_diagnostic(self.data, self.row, self.monitor,
                                        tool.Interval(0, 0), tool.Interval('-.001', '-.001'))
        self.assertFalse(result['physical_operating_domain'])
        self.assertIn('unsupported_reverse_current_or_nonpositive_voltage', result['failed_checks'])
        self.assertLess(F(result['branch_current_a_exact']['monitor_top_current_a'][0]), 0)


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


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class ImpedancePortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tool.source.load_current()
        cls.monitors = tool.monitor_hypotheses()
        cls.result = tool.portfolio(cls.data, cls.monitors, F('.05'))

    def test_all_twelve_windows_baseline_failures_and_first_passing_policy(self):
        report = self.result
        proof = tool.verify_portfolio(self.data, self.monitors, F('.05'), report)
        self.assertEqual(report['trial_count'], 12)
        self.assertEqual(report['windows_ohm_exact'], [['5000', '10000'], ['500', '1000'], ['50', '100']])
        self.assertEqual([g['selected_window_index'] for g in report['groups']], [None, None, 2, 1])
        for group in report['groups'][2:]:
            self.assertEqual(group['trials'][0]['loaded_diagnostic_status'], 'conditional_static_fail')
            self.assertEqual(group['trials'][0]['feedback']['selected_nominal_ohm_exact'], {'top': '44200', 'bottom': '10100'})
            selected = group['trials'][group['selected_window_index']]
            self.assertEqual(selected['loaded_diagnostic_status'], 'conditional_static_pass')
            self.assertEqual(selected['loaded_diagnostic']['checked_load_cases'], 58)
            self.assertFalse(selected['loaded_diagnostic']['source_applicability'])
            self.assertFalse(selected['qualified'])
        self.assertEqual(proof['complete_fixed_trial_count'], 12)
        self.assertTrue(proof['e192_membership_checked'])
        self.assertFalse(proof['qualified'])

    def test_missing_group_window_and_reordered_domain_fail(self):
        for mutate in (lambda r: r['groups'].pop(), lambda r: r['groups'][0]['trials'].pop(),
                       lambda r: r['windows_ohm_exact'].reverse()):
            changed = deepcopy(self.result)
            mutate(changed)
            with self.subTest(mutate=mutate), self.assertRaisesRegex(ValueError, 'portfolio domain'):
                tool.verify_portfolio(self.data, self.monitors, F('.05'), changed)

    def test_skipped_first_passing_window_fails(self):
        changed = deepcopy(self.result)
        changed['groups'][3]['selected_window_index'] = 2
        with self.assertRaisesRegex(ValueError, 'first passing selection'):
            tool.verify_portfolio(self.data, self.monitors, F('.05'), changed)

    def test_fabricated_pass_or_weakened_bias_budget_fails(self):
        for mutation in ('pass', 'bias'):
            changed = deepcopy(self.result)
            if mutation == 'pass':
                changed['groups'][2]['trials'][0]['loaded_diagnostic_status'] = 'conditional_static_pass'
                changed['groups'][2]['trials'][0]['loaded_diagnostic']['status'] = 'conditional_static_pass'
                changed['groups'][2]['selected_window_index'] = 0
            else:
                changed['bias_budgets_a_exact']['feedback'] = ['0', '0']
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'Portfolio differs'):
                tool.verify_portfolio(self.data, self.monitors, F('.05'), changed)

    def test_weakened_load_or_voltage_demand_cannot_survive_replay(self):
        for mutation in ('load', 'voltage'):
            changed = deepcopy(self.result)
            if mutation == 'load':
                changed['load_cases_a_exact'] = [[name, '4'] if F(current) == F('4.25') else [name, current]
                                               for name, current in changed['load_cases_a_exact']]
            else:
                changed['invariant_demands']['consumer_max_v'] = '3.4'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'Portfolio differs'):
                tool.verify_portfolio(self.data, self.monitors, F('.05'), changed)

    def test_continuous_nominal_cannot_masquerade_as_pinned_e192(self):
        changed = deepcopy(self.result)
        trial = changed['groups'][3]['trials'][1]
        trial['feedback']['selected_nominal_ohm_exact']['top'] = '4421'
        # This continuous value really passes the declared loaded physics.
        diagnostic = tool.loaded_diagnostic(self.data, trial, self.monitors[1],
                                             tool.Interval('-.000001', '.000001'), tool.Interval('-.0000015', '.0000015'))
        self.assertEqual(diagnostic['status'], 'conditional_static_pass')
        with self.assertRaisesRegex(ValueError, 'not a pinned E192 member'):
            tool.verify_portfolio(self.data, self.monitors, F('.05'), changed)


if __name__ == '__main__':
    unittest.main()
