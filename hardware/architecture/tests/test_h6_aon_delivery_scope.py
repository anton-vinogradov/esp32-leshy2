"""Independent AON forward/inverse arithmetic and guarded application checks."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import aon_delivery_scope as aon
import synthesize_main_dc_cell as cell


class InverseLossTests(unittest.TestCase):
    ARGS = dict(raw_average_min_v='3.267', ripple_pp_v='.020', distribution_drop_v='.025',
                consumer_min_v='2.7', main_max_v='3.3', load_a='.0721')

    def test_independent_exact_budget_and_boundary(self):
        result = aon.inverse_ron(**self.ARGS)
        self.assertEqual(F(result['required_consumer_floor_v_exact']), 3)
        self.assertEqual(F(result['headroom_v_exact']), F('.232'))
        resistance = F(result['required_max_ron_ohm_exact'])
        self.assertEqual(resistance, F(2320, 721))
        self.assertEqual(F('3.267')-F('.01')-F('.025')-F('.0721')*resistance, 3)
        self.assertLess(F('3.267')-F('.01')-F('.025')-F('.0721')*(resistance+F('.001')), 3)
        self.assertTrue(result['feasible_nonnegative_ron'])
        self.assertFalse(result['qualified'])

    def test_consumer_requirement_can_dominate_logic_floor(self):
        result = aon.inverse_ron(**{**self.ARGS, 'consumer_min_v': '3.1'})
        self.assertEqual(F(result['required_consumer_floor_v_exact']), F('3.1'))
        self.assertEqual(F(result['required_max_ron_ohm_exact']), F('.132')/F('.0721'))

    def test_negative_budget_is_not_clamped_into_a_feasible_part(self):
        result = aon.inverse_ron(**{**self.ARGS, 'consumer_min_v': '3.5'})
        self.assertLess(F(result['required_max_ron_ohm_exact']), 0)
        self.assertFalse(result['feasible_nonnegative_ron'])

    def test_zero_load_is_unbounded_only_when_voltage_budget_nonnegative(self):
        for floor, feasible in [('2.7', True), ('3.5', False)]:
            result = aon.inverse_ron(**{**self.ARGS, 'consumer_min_v': floor, 'load_a': '0'})
            self.assertIsNone(result['required_max_ron_ohm_exact'])
            self.assertIs(result['feasible_nonnegative_ron'], feasible)

    def test_invalid_unknown_or_nonfinite_budgets_rejected(self):
        for key, value in [('load_a', '-.1'), ('load_a', None), ('load_a', True),
                           ('ripple_pp_v', '-.01'), ('distribution_drop_v', '-.01'),
                           ('raw_average_min_v', 'NaN'), ('main_max_v', 'Infinity')]:
            with self.subTest(key=key, value=value), self.assertRaises((ValueError, TypeError)):
                aon.inverse_ron(**{**self.ARGS, key: value})

    def test_source_fixture_byte_change_is_not_trusted(self):
        with patch.object(Path, 'read_bytes', return_value=b'{}'), self.assertRaisesRegex(ValueError, 'review'):
            aon.load_reviewed()


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class AonApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Full current command is also the integration under test.
        cls.full = cell.run()
        cls.result = cls.full['aon_delivery_scope']

    def test_profile_membership_and_legacy_source_envelopes(self):
        result = self.result
        self.assertEqual(result['profile_count'], 56)
        self.assertEqual(set(result['envelopes']), {'legacy_h3_raw_2pct', 'source_conditioned_vset_1pct'})
        legacy = result['envelopes']['legacy_h3_raw_2pct']
        source = result['envelopes']['source_conditioned_vset_1pct']
        self.assertEqual(list(map(F, legacy['consumer_envelope_v_exact'])), [F('3.181696'), F('3.376')])
        self.assertEqual(list(map(F, source['consumer_envelope_v_exact'])), [F('3.214696'), F('3.343')])
        expected_ids = {p['load_case'] for p in cell.current.source.h3.build()[1]['profile_voltage_corners']
                        if p['rail'] == 'AON_SAFE_3V3'}
        for name, envelope in result['envelopes'].items():
            self.assertEqual(len(envelope['profiles']), 56)
            self.assertEqual({p['load_case'] for p in envelope['profiles']}, expected_ids)
            raw_min, raw_max = ((F('3.224'), F('3.376')) if name == 'legacy_h3_raw_2pct'
                                else (F('3.257'), F('3.343')))
            for row in envelope['profiles']:
                current = F(row['load_ma'])/1000
                exact = row['exact_bounds']
                self.assertEqual(F(exact['raw_min_v']), raw_min)
                self.assertEqual(F(exact['raw_max_v']), raw_max)
                self.assertEqual(F(exact['protected_local_min_v']), raw_min-current*F('.240'))
                self.assertEqual(F(exact['consumer_endpoint_min_v']), raw_min-current*F('.240')-F('.025'))
                self.assertEqual(F(exact['consumer_endpoint_max_v']), raw_max)
                self.assertFalse(row['model_qualified'])

    def test_all_profile_ron_budgets_agree_with_independent_equation(self):
        for name, envelope in self.result['envelopes'].items():
            raw_min = F('3.224') if name == 'legacy_h3_raw_2pct' else F('3.257')
            currents = {r['load_case']: F(r['load_ma'])/1000 for r in envelope['profiles']}
            for group in envelope['fault_bus_by_divider']:
                source_scope = next(g for g in self.full['auxiliary_scope']['groups']
                                    if g['divider_class'] == group['divider_class'])
                floor = max(F('2.7'), F(source_scope['protected_voltage_v_exact'][1])-F('.3'))
                expected = {name: (raw_min-F('.025')-floor)/current for name,current in currents.items()}
                self.assertEqual(len(group['ron_inverse_cases']), 56)
                self.assertEqual(F(group['minimum_required_max_ron_ohm_exact']), min(expected.values()))
                self.assertEqual(set(group['witness_ids']), {k for k,v in expected.items() if v==min(expected.values())})
                self.assertIsNone(group['actual_ron_max_ohm'])
                self.assertFalse(group['screen']['qualified'])
                self.assertTrue(group['screen']['zero_current_diagnostic']['all_corners_high_compatible'])

    def test_original_requirement_screen_is_preserved_not_replaced_by_projection(self):
        for group in self.full['candidate_topologies']['fault_bus_screens'].values():
            original = group['common_source_temperature_hypothesis']
            self.assertEqual(original['stimulus']['aon_v'], ['2.7', '3.6'])
            self.assertFalse(original['zero_current_diagnostic']['all_corners_high_compatible'])

    def test_every_candidate_is_linked_without_promoting_zero_added_load(self):
        expected = {r['validation']['candidate_sha256'] for r in self.full['candidate_topologies']['candidates']}
        variants = self.result['candidate_variants']
        self.assertEqual(len(variants), 18)
        self.assertEqual({r['candidate_sha256'] for r in variants}, expected)
        self.assertEqual(sum(r['monitor_supply_node']=='AON_SAFE_3V3' for r in variants), 6)
        for row in variants:
            self.assertIsNone(row['actual_extra_aon_current_a'])
            self.assertEqual(row['modeled_added_aon_current_a'], '0')
            self.assertTrue(row['zero_added_load_diagnostic'])
        self.assertFalse(self.result['qualified'])
        self.assertFalse(self.result['native_current_inventory_qualified'])
        self.assertFalse(self.result['configuration_source_conditions_proven'])

    def test_upstream_source_changes_rejected(self):
        altered_hashes = dict(self.full['source_sha256'])
        altered_hashes['hardware/verification/h3-r2-rail-margin-contract.json'] = '0'*64
        with self.assertRaises(ValueError):
            aon.assess_current(self.full, source_hashes=altered_hashes)

    def test_original_requirement_screens_cannot_disappear_or_be_weakened(self):
        for mutation in ('missing', 'qualified', 'narrowed', 'candidate_ref'):
            altered = deepcopy(self.full)
            portfolio = altered['candidate_topologies']
            if mutation == 'missing':
                del portfolio['fault_bus_screens']
            elif mutation == 'candidate_ref':
                portfolio['candidates'][0]['fault_bus_screen_ref'] = 'different_divider'
            else:
                screen = next(iter(portfolio['fault_bus_screens'].values()))['common_source_temperature_hypothesis']
                if mutation == 'qualified':
                    screen['qualified'] = True
                else:
                    screen['stimulus']['aon_v'] = ['3.2', '3.4']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                aon.assess_current(altered, source_hashes=self.full['source_sha256'])

    def test_variants_cannot_disappear_duplicate_or_lose_binding(self):
        for mutation in ('missing', 'duplicate', 'digest'):
            altered = deepcopy(self.full)
            candidates = altered['candidate_topologies']['candidates']
            if mutation == 'missing':
                candidates.pop()
            elif mutation == 'duplicate':
                candidates[-1] = deepcopy(candidates[0])
            else:
                candidates[0]['fault_bus_binding']['candidate_sha256'] = '0'*64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                aon.assess_current(altered, source_hashes=self.full['source_sha256'])


if __name__ == '__main__':
    unittest.main()
