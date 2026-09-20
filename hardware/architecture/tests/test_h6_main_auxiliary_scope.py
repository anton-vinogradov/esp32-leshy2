"""Interface/source/unknown-accounting guards, not new component qualification."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import main_auxiliary_scope as aux


class SourceScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = aux.load_reviewed()
        cls.rows = {row['id']: row for row in cls.fixture['rows']}

    def test_maximum_admits_only_matching_parameter_conditions_not_cell_or_minimum(self):
        row = self.rows['tps3703_idd']
        result = aux.evaluate_source(row, mpn=row['mpn'], axes={'vdd_v': ['2.7', '3.6'], 'ta_c': ['-40', '125']},
                                     conditions=row['header_conditions'])
        self.assertTrue(result['numeric_domains_covered'])
        self.assertTrue(result['parameter_maximum_admitted'])
        self.assertEqual(result['actual_current_max_a'], '0.000007')
        self.assertIsNone(result['actual_current_min_a'])
        self.assertFalse(result['qualified'])
        self.assertNotEqual(result['actual_current_max_a'], row['typical'])

    def test_numeric_coverage_without_header_conditions_does_not_admit_actual_current(self):
        row = self.rows['tps3703_idd']
        result = aux.evaluate_source(row, mpn=row['mpn'], axes=row['numeric_domains'], conditions={})
        self.assertTrue(result['numeric_domains_covered'])
        self.assertEqual(set(result['unreviewed_conditions']), set(row['header_conditions']))
        self.assertFalse(result['parameter_maximum_admitted'])
        self.assertIsNone(result['actual_current_max_a'])

    def test_wrong_conditions_or_missing_axis_fail_closed(self):
        row = self.rows['tps3703_idd']
        for axes, conditions, key in (({'vdd_v': ['3.3', '3.3']}, row['header_conditions'], 'missing_axes'),
                                     (row['numeric_domains'], {**row['header_conditions'], 'mr': 'ground'}, 'mismatched_conditions')):
            result = aux.evaluate_source(row, mpn=row['mpn'], axes=axes, conditions=conditions)
            self.assertTrue(result[key])
            self.assertIsNone(result['actual_current_max_a'])
        with self.assertRaisesRegex(ValueError, 'MPN'):
            aux.evaluate_source(row, mpn='similar device', axes=row['numeric_domains'], conditions={})
        for axes, conditions in (({**row['numeric_domains'], 'tj_c': ['-40', '125']}, {}),
                                  (row['numeric_domains'], {'unknown': 'open'})):
            with self.assertRaisesRegex(ValueError, 'unknown'):
                aux.evaluate_source(row, mpn=row['mpn'], axes=axes, conditions=conditions)

    def test_point_conditions_cannot_be_extrapolated_or_used_powered_off(self):
        for name, axes in (('tps259814_iq_on', {'vin_v': ['3.1', '3.3'], 'tj_c': ['-40', '125']}),
                           ('tps3703_reset_leakage', {'vdd_v': ['3.3', '3.3'], 'reset_v': ['3.3', '3.3'], 'ta_c': ['-40', '125']}),
                           ('tps3703_reset_leakage', {'vdd_v': ['0', '0'], 'reset_v': ['3.3', '3.3'], 'ta_c': ['-40', '125']}),
                           ('tps3703_idd', {'vdd_v': ['0', '0'], 'ta_c': ['-40', '125']})):
            row = self.rows[name]
            with self.subTest(row=name, axes=axes):
                result = aux.evaluate_source(row, mpn=row['mpn'], axes=axes, conditions=row['header_conditions'])
                self.assertFalse(result['numeric_domains_covered'])
                self.assertIsNone(result['actual_current_max_a'])

    def test_invalid_exact_values_and_changed_fixture_rejected(self):
        for interval in ([0, 1], ['1', '0'], ['NaN', '1'], ['Infinity', '1']):
            with self.subTest(interval=interval), self.assertRaises((ValueError, ZeroDivisionError)):
                aux.bounds(interval)
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as directory:
            path = Path(directory)/'fixture.json'
            path.write_bytes(aux.ROWS_PATH.read_bytes()+b' ')
            with patch.object(aux, 'ROWS_PATH', path), self.assertRaisesRegex(ValueError, 'changed'):
                aux.load_reviewed()


class NativeAuxiliaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = aux.current.load_current()
        cls.context = aux.load_context(cls.native['source_sha256'])
        cls.fixture = aux.load_reviewed()
        cls.dc = {'qualified': False, 'source_applicability': False, 'status': 'not_qualified',
                  'full_dc_cell_proven': False, 'source_sha256': cls.native['source_sha256'],
                  'unresolved_branches': [{'id': name, 'supply_node': 'raw_converter_output' if name == 'replacement_efuse_iq' else None,
                                           'current_max_a': None, 'bound_established': False} for name in aux.BRANCHES],
                  'groups': [{'divider_class': 'synthetic_protocol_fixture_not_a_candidate', 'monitor': 'tps3703a7330',
                              'selected_static_pair': {'loaded_diagnostic': {
                                  'status': 'conditional_static_pass', 'qualified': False, 'source_applicability': False,
                                  'checked_load_cases': 58, 'raw_v_exact': ['3.2', '3.3'],
                                  'cases': [{'bounds_exact': {'local_v': ['3.1', '3.29']}} for _ in range(58)]}}}]}
        cls.result = aux.assess_current(cls.dc)

    def test_interface_rejects_drop_in_even_at_same_pg_pin(self):
        interface = self.result['replacement_interface']
        self.assertFalse(interface['drop_in_allowed'])
        self.assertFalse(interface['candidate_wiring_declared'])
        self.assertEqual(len(interface['pins']), 10)
        pg, changed = (next(p for p in interface['pins'] if p['physical'] == n) for n in ('3', '4'))
        self.assertFalse(pg['role_or_type_changed'])
        self.assertFalse(pg['functional_equivalence_proven'])
        self.assertTrue(changed['role_or_type_changed'])
        self.assertEqual((changed['native_function'], changed['candidate_function']), ('PGTH', 'FLT'))
        self.assertEqual(changed['native_net'], 'MAIN_EFUSE_PGTH')

    def test_missing_swapped_mistyped_candidate_pins_or_native_net_rejected(self):
        for mutation in ('omit', 'swap', 'type'):
            interface = deepcopy(self.fixture['replacement_interface'])
            if mutation == 'omit':
                interface['pins'].pop()
            elif mutation == 'swap':
                interface['pins'][2]['physical'], interface['pins'][3]['physical'] = '4', '3'
            else:
                interface['pins'][3]['type'] = 'analog_input'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'reviewed source'):
                aux.validate_candidate_interface(interface, self.context['main_efuse'])
        native = deepcopy(self.context['main_efuse'])
        native[0]['net'] = '3V3_MAIN'
        with self.assertRaisesRegex(ValueError, 'native pin'):
            aux.validate_candidate_interface(self.fixture['replacement_interface'], native)

    def test_exact_nodes_remain_distinct_and_unknown_is_not_zero(self):
        self.assertEqual(len({aux.classify_branch(n, 'POWER_GROUND')['accounting_lane'] for n in aux.NODES}), 4)
        unknown = aux.classify_branch(None, 'POWER_GROUND')
        self.assertIsNone(unknown['accounting_lane'])
        self.assertFalse(unknown['ownership_known'])
        for supply, ground in (('3V3', 'POWER_GROUND'), ('3V3_MAIN', 'AUDIO_GROUND'), ('3V3_MAIN', '')):
            with self.assertRaisesRegex(ValueError, 'unknown/wrong'):
                aux.classify_branch(supply, ground)

    def test_closed_world_branch_membership_type_owner_and_raw_iq_guard(self):
        keys = {'id', 'owner', 'kind', 'supply_node', 'return_node', 'current_max_a', 'bound_established', 'diagnostic_budget_a'}
        records = [{k: v for k, v in row.items() if k in keys} for row in self.result['branches']]
        for mutation in ('missing', 'duplicate', 'orphan', 'type', 'owner', 'iq_node', 'zero', 'close_unknown'):
            changed = deepcopy(records)
            if mutation == 'missing': changed.pop()
            elif mutation == 'duplicate': changed[1] = deepcopy(changed[0])
            elif mutation == 'orphan': changed[-1]['id'] = 'new_unnamed_branch'
            elif mutation == 'type': changed[0]['kind'] = 'pullup_current'
            elif mutation == 'owner': changed[0]['owner'] = None
            elif mutation == 'iq_node': changed[2]['supply_node'] = '3V3_MAIN'
            elif mutation == 'zero': changed[0]['current_max_a'] = '0'
            else: changed[-1]['supply_node'] = 'MAIN_RAW_3V3'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                aux.validate_branches(changed)
        records[0]['diagnostic_budget_a'] = '0.000007'
        checked = aux.validate_branches(records)
        self.assertIsNone(checked[0]['current_max_a'])
        self.assertFalse(checked[0]['bound_established'])

    def test_live_and_off_scopes_keep_unknowns_and_native_pullup_not_added_again(self):
        row = self.result['groups'][0]
        self.assertEqual([r['numeric_domains_covered'] for r in row['monitor_supply_scopes']], [True, True, True, False])
        self.assertFalse(row['efuse_iq_scope']['numeric_domains_covered'])
        for result in row['monitor_supply_scopes']+row['reset_leakage_scopes']+[row['efuse_iq_scope']]:
            self.assertIsNone(result['actual_current_max_a'])
            self.assertFalse(result['qualified'])
        self.assertFalse(any(r['numeric_domains_covered'] for r in row['reset_leakage_scopes']))
        self.assertEqual(F(row['native_pullup_low_output_diagnostic_max_a']), F('3.29')/9900)
        self.assertFalse(row['native_pullup_added_again'])
        self.assertEqual(self.result['native_fault_pullup']['supply_node'], '3V3_MAIN')
        self.assertFalse(self.result['native_fault_pullup']['counted_again'])
        self.assertFalse(self.result['native_fault_pullup']['native_budget_coverage_proven'])
        self.assertFalse(self.result['full_inventory_known'])
        self.assertIsNone(self.result['actual_auxiliary_total_a'])

    def test_upstream_unknowns_monitor_identity_and_coverage_cannot_be_weakened(self):
        for mutation in ('unknown', 'iq_node', 'monitor', 'cases', 'qualified'):
            changed = deepcopy(self.dc)
            if mutation == 'unknown': changed['unresolved_branches'].pop()
            elif mutation == 'iq_node': changed['unresolved_branches'][2]['supply_node'] = '3V3_MAIN'
            elif mutation == 'monitor': changed['groups'][0]['monitor'] = 'another_part'
            elif mutation == 'cases': changed['groups'][0]['selected_static_pair']['loaded_diagnostic']['cases'].pop()
            else: changed['qualified'] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                aux.assess_current(changed)

    def test_native_pullup_wrong_rail_or_endpoint_rejected(self):
        for key, value in (('net', 'AON_SAFE_3V3'), ('contact', 'END_2')):
            context = deepcopy(self.context)
            contact = next(r for r in context['power_fault_pullup'] if str(r['physical']) == '1')
            contact[key] = value
            with patch.object(aux, 'load_context', return_value=context), self.assertRaisesRegex(ValueError, 'R266'):
                aux.assess_current(self.dc)

    def test_native_resistor_value_and_tolerance_are_bound_to_live_devices(self):
        for kind in ('4k7ohm_1pct_resistor', '100ohm_1pct_resistor', '10kohm_5pct_resistor'):
            context = deepcopy(self.context)
            context['devices'][self.fixture['native_fault_pullup']['device_id']]['kind'] = kind
            with self.subTest(kind=kind), patch.object(aux, 'load_context', return_value=context), \
                    self.assertRaises(ValueError):
                aux.assess_current(self.dc)

    def test_aon_source_scope_follows_guarded_live_requirement_not_old_literal(self):
        context = deepcopy(self.context)
        context['required_aon_v'] = ['2.7', '6']
        with patch.object(aux, 'load_context', return_value=context):
            result = aux.assess_current(self.dc)
        self.assertEqual(result['live_aon_hypothesis_v'], ['2.7', '6'])
        aon = result['groups'][0]['monitor_supply_scopes'][2]
        self.assertEqual(aon['application_axes']['vdd_v'], ['2.7', '6'])
        self.assertFalse(aon['numeric_domains_covered'])

    def test_stale_loader_hashes_and_fixture_change_during_assessment_rejected(self):
        changed = dict(self.native['source_sha256'])
        changed[next(iter(changed))] = '0'*64
        with self.assertRaisesRegex(ValueError, 'provenance changed'):
            aux.load_context(changed)
        original = aux.current.snapshot
        counts = 0
        def snapshot(paths):
            nonlocal counts
            if paths == aux.source_paths():
                counts += 1
                if counts == 2: return {}
            return original(paths)
        with patch.object(aux.current, 'snapshot', side_effect=snapshot), self.assertRaisesRegex(ValueError, 'sources changed'):
            aux.assess_current(self.dc)


if __name__ == '__main__':
    unittest.main()
