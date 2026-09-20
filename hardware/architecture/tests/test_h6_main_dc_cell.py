"""Known-branch DC screening guards; these do not qualify an actual cell."""
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
import synthesize_main_dc_cell as cell


class CandidateLawTests(unittest.TestCase):
    def test_replacement_law_cannot_inherit_fitted_part_or_inclusive_domain(self):
        for key, value in (('equation_constant_a_ohm', '5747'),
                           ('configured_accuracy_domain_min_a_exclusive', '1.74'),
                           ('gain_tolerance_fraction', '.05')):
            spec = cell.candidate_spec('1pct_100ppm')
            spec[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'candidate-specific'):
                cell.validate_candidate_spec(spec)
        with self.assertRaises(ValueError):
            cell.candidate_spec('ideal')

    def test_rational_input_types_fail_closed(self):
        for value in (True, 4.25, 'NaN', 'Infinity'):
            with self.subTest(value=value), self.assertRaises((ValueError, ZeroDivisionError)):
                cell.exact(value)


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class DcCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = cell.current.load_current()
        cls.static = cell.static.run()
        cls.table = cell.current.load_edg_table()
        cls.result = cell.combine(cls.static, cls.native, cls.table)

    def test_separate_branch_ownership_changes_each_selected_pairs_current_demands(self):
        self.assertEqual(len(self.result['groups']), 2)
        requirements = []
        for group in self.result['groups']:
            selected = group['selected_static_pair']
            req = cell.current_requirements(self.native, selected)
            requirements.append(req)
            monitor = F(selected['loaded_diagnostic']['branch_current_a_exact']['monitor_top_current_a'][1])
            feedback = F(selected['loaded_diagnostic']['branch_current_a_exact']['feedback_top_current_a'][1])
            self.assertEqual(F(req['required_lower_a']), F('4.25')+monitor)
            self.assertEqual(F(req['strict_upper_a']), 6-feedback)
            self.assertEqual(F(req['protected_demands_a']['pf03_reserve_a']), F('3.8075')+F('1.25')*monitor)
            self.assertEqual(F(req['protected_demands_a']['existing_inrush_dc_proxy_a']), F('3.117079')+monitor)
            self.assertFalse(req['unknown_auxiliary_currents_included'])
        self.assertNotEqual(requirements[0]['monitor_branch_max_a'], requirements[1]['monitor_branch_max_a'])
        self.assertNotEqual(requirements[0]['feedback_branch_max_a'], requirements[1]['feedback_branch_max_a'])
        self.assertLess(F(requirements[0]['strict_upper_a']), F(requirements[1]['strict_upper_a']))

    def test_complete_intersection_and_strict_configured_forward_checks(self):
        cell.validate_combination(self.static, self.native, self.table, self.result)
        for group in self.result['groups']:
            self.assertEqual([row['selected_nominal_ohm'] for row in group['rilm_portfolios']], ['1260', '1270', '1270'])
            self.assertEqual([row['candidate_count'] for row in group['rilm_portfolios']], [1, 3, 3])
            for row in group['rilm_portfolios']:
                self.assertFalse(row['domain']['maximum_inclusive'])
                self.assertEqual(row['budgets'], list(cell.current.BUDGETS))
                for candidate in row['candidates']:
                    for check in candidate['checks']:
                        self.assertGreater(F(check['configured_min_a_exact']), 5)
                        self.assertTrue(check['numerical_constraints_met'])
                        self.assertFalse(check['qualified'])

    def test_exact_configured_boundary_is_excluded_before_forward(self):
        req = self.result['groups'][0]['requirements']
        row = cell.threshold_portfolio(req, '1pct_100ppm', self.table)
        boundary = F(row['domain']['nominal_ohm_exact'][1])
        with patch.object(cell.current, 'finite_nominals', return_value=([3], [boundary])), \
                patch.object(cell.current, 'forward', side_effect=AssertionError('strict boundary admitted')):
            rejected = cell.threshold_portfolio(req, '1pct_100ppm', self.table)
        self.assertEqual(rejected['candidate_count'], 0)
        self.assertIsNone(rejected['selected_nominal_ohm'])

    def test_load_limited_upper_is_inclusive_not_mislabeled_configured_boundary(self):
        native = deepcopy(self.native)
        native['requirements_a']['h0_step_a'] = '4.7'
        native['required_lower_a'] = F('4.7')
        req = cell.current_requirements(native, self.result['groups'][0]['selected_static_pair'])
        row = cell.threshold_portfolio(req, '0.1pct_10ppm', self.table)
        self.assertTrue(row['domain']['maximum_inclusive'])

    def test_missing_candidates_altered_selection_and_weakened_demands_fail_replay(self):
        for mutation in ('omit', 'selection', 'demand'):
            changed = deepcopy(self.result)
            group = changed['groups'][0]
            if mutation == 'omit':
                group['rilm_portfolios'][1]['candidates'].pop()
            elif mutation == 'selection':
                group['rilm_portfolios'][1]['selected_nominal_ohm'] = '1260'
            else:
                group['requirements']['required_lower_a'] = '4'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'differs from replay'):
                cell.validate_combination(self.static, self.native, self.table, changed)

    def test_unknown_auxiliaries_or_old_findings_cannot_be_erased_or_qualified(self):
        self.assertEqual(len(self.result['baseline_power_review']['findings']), 8)
        self.assertEqual(self.result['baseline_power_review'], self.native['baseline_power_review'])
        self.assertFalse(self.result['divider_lifetime_covered'])
        for mutate in (lambda r: r.update(qualified=True), lambda r: r.update(full_dc_cell_proven=True),
                       lambda r: r['unresolved_branches'].clear(),
                       lambda r: r['unresolved_branches'][0].update(current_max_a='0', bound_established=True),
                       lambda r: r['baseline_power_review']['findings'].clear()):
            changed = deepcopy(self.result)
            mutate(changed)
            with self.subTest(mutate=mutate), self.assertRaisesRegex(ValueError, 'differs from replay'):
                cell.validate_combination(self.static, self.native, self.table, changed)

    def test_wrong_k_weakened_requirements_or_missing_stress_budget_fail(self):
        req = self.result['groups'][0]['requirements']
        spec = cell.candidate_spec('1pct_100ppm')
        spec['equation_constant_a_ohm'] = '5747'
        with patch.object(cell, 'candidate_spec', return_value=spec), self.assertRaisesRegex(ValueError, 'candidate-specific'):
            cell.threshold_portfolio(req, '1pct_100ppm', self.table)
        for key, value in (('strict_upper_a', '6'), ('required_lower_a', '4')):
            changed = {**req, key: value}
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'inconsistent'):
                cell.threshold_portfolio(changed, '1pct_100ppm', self.table)
        with patch.dict(cell.current.BUDGETS, {'initial_plus_tcr': ()}, clear=True), self.assertRaisesRegex(ValueError, 'both original'):
            cell.threshold_portfolio(req, '1pct_100ppm', self.table)

    def test_source_change_during_run_and_runtime_change_cannot_publish_candidate(self):
        snapshot = cell.current.snapshot
        calls = 0
        def changed(paths):
            nonlocal calls
            calls += 1
            return snapshot(paths) if calls == 1 else {}
        with patch.object(cell.static, 'run', return_value=self.static), \
                patch.object(cell.current, 'load_current', return_value=self.native), \
                patch.object(cell.current, 'snapshot', side_effect=changed), \
                self.assertRaisesRegex(ValueError, 'sources changed'):
            cell.run()
        with patch.object(cell.static, 'run', return_value=self.static), \
                patch.object(cell.current, 'load_current', return_value=self.native), \
                patch.object(cell.current, 'load_edg_table', side_effect=[self.table, ()]), \
                self.assertRaisesRegex(ValueError, 'runtime/table changed'):
            cell.run()

    def test_prepublication_source_or_runtime_error_leaves_no_result(self):
        for cause in ('sources', 'runtime'):
            stream = StringIO()
            hashes = cell.current.snapshot(cell.source_paths())
            if cause == 'sources':
                hashes = {**hashes, 'missing-source': 'stale'}
            runtime = ValueError('changed EDG runtime') if cause == 'runtime' else None
            with tempfile.TemporaryDirectory(dir=ROOT/'work') as folder, \
                    patch.object(cell.tempfile, 'mkdtemp', return_value=folder), \
                    patch.object(cell, 'keep_awake', return_value=nullcontext()), \
                    patch.object(cell, 'run', return_value={'source_sha256': hashes}), \
                    patch.object(cell.static.pair, '_load_edg', side_effect=runtime), redirect_stdout(stream):
                self.assertEqual(cell.main(), 2)
                self.assertFalse((Path(folder)/'result.json').exists())
            self.assertIsNone(json.loads(stream.getvalue())['report'])


if __name__ == '__main__':
    unittest.main()
