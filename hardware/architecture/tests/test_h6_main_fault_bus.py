"""Independent threshold/KCL expectations and native binding mutations."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from itertools import product
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import main_fault_bus as bus
import main_candidate_topology as topology
import synthesize_main_dc_cell as cell

AXES = dict(main_v=['3', '3.3'], aon_v=['2.7', '3.6'],
            resistance_ohm=['9900', '10100'], temperature_c=['-40', '85'])


class FaultScreenTests(unittest.TestCase):
    def test_changed_source_bytes_require_review(self):
        with patch.object(Path, 'read_bytes', return_value=b'{}'), self.assertRaisesRegex(ValueError, 'review'):
            bus.load_reviewed()

    def test_independent_uniform_interval_and_zero_load_conflict(self):
        result = bus.screen(**AXES)
        interval = result['uniform_current_interval']
        # Most demanding upper-input corner: MAIN3.3,AON2.7,R9900.
        # Most demanding logic-high corner: MAIN3.0,AON3.6,R10100.
        self.assertEqual(F(interval['minimum_a_exact']), F('0.3')/9900)
        self.assertEqual(F(interval['maximum_a_exact']), F('0.48')/10100)
        self.assertFalse(interval['empty'])
        self.assertTrue(interval['sufficient_not_necessary'])
        self.assertTrue(result['thresholds_admitted'])
        self.assertIsNone(result['actual_total_signed_current_a'])
        self.assertFalse(result['qualified'])

    def test_same_rail_nominal_is_not_a_blanket_problem(self):
        result = bus.screen(**{**AXES, 'main_v': ['3.3', '3.3'], 'aon_v': ['3.3', '3.3']})
        bounds = result['uniform_current_interval']
        self.assertLess(F(bounds['minimum_a_exact']), 0)
        self.assertGreater(F(bounds['maximum_a_exact']), 0)

    def test_uniform_bounds_cover_independent_interior_grid(self):
        bounds = bus.screen(**AXES)['uniform_current_interval']
        currents = tuple(F(bounds[key]) for key in ('minimum_a_exact', 'maximum_a_exact'))
        for main, aon, resistance, current in product(
                map(F, ('3', '3.071', '3.3')), map(F, ('2.7', '3.111', '3.6')),
                map(F, ('9900', '10007', '10100')), currents):
            voltage = main-resistance*current
            self.assertGreaterEqual(voltage, F('.7')*max(main, aon))
            self.assertLessEqual(voltage, min(F('5.5'), aon+F('.3')))

    def test_empty_uniform_interval_does_not_assert_actual_hardware_failure(self):
        result = bus.screen(**{**AXES, 'main_v': ['2', '3.3']})
        self.assertTrue(result['uniform_current_interval']['empty'])
        self.assertIsNone(result['actual_total_signed_current_a'])
        self.assertFalse(result['qualified'])

    def test_temperature_coverage_is_not_silently_narrowed(self):
        result = bus.screen(**{**AXES, 'temperature_c': ['-40', '125']})
        self.assertFalse(result['thresholds_admitted'])
        self.assertFalse(result['qualified'])

    def test_off_is_not_admitted_as_operational_gpio(self):
        for domain in ('main_v', 'aon_v'):
            result = bus.screen(**{**AXES, domain: ['0', '0']})
            self.assertFalse(result['thresholds_admitted'])
            self.assertIsNone(result['actual_total_signed_current_a'])

    def test_invalid_or_implicit_axes_rejected(self):
        for name, values in [('resistance_ohm', ['0', '1']), ('resistance_ohm', ['-1', '1']),
                             ('main_v', ['3.3', '3']), ('main_v', [3, 3.3]),
                             ('aon_v', None), ('temperature_c', ['NaN', '85']),
                             ('main_v', ['-1', '3'])]:
            with self.subTest(name=name, values=values), self.assertRaises((ValueError, TypeError, AssertionError)):
                bus.screen(**{**AXES, name: values})

    def test_five_volt_pin_or_invented_signed_leakage_rejected(self):
        for mutation in ('pin_type', 'leakage', 'mode', 'supply'):
            fixture = bus.load_reviewed()
            msp = fixture['receivers'][1]
            if mutation == 'pin_type':
                msp['pin_function']['kind'] = 'ODIO'
            elif mutation == 'leakage':
                msp['leakage_rows'][0]['minimum'] = '-0.00000005'
            elif mutation == 'mode':
                msp['gpio_mode_proven'] = True
            else:
                msp['supplies'][0]['net'] = '3V3_MAIN'
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                bus.screen(**AXES, fixture=fixture)


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class FaultBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = cell.current.load_current()
        cls.static = cell.static.run()
        cls.dc = cell.combine(cls.static, cls.native, cell.current.load_edg_table())
        cls.baseline = topology.load_baseline(cls.native['source_sha256'])
        group = cls.dc['groups'][0]
        cls.candidate = topology.build_candidate(cls.baseline, group, group['rilm_portfolios'][0], '3V3_MAIN')

    def assess(self, candidate):
        return bus.assess_candidate(candidate, **AXES)

    def refresh_digest(self, candidate):
        # Deliberately forge a fresh content receipt to exercise semantic binding
        # guards themselves, not merely the earlier stale-digest rejection.
        candidate['validation']['candidate_sha256'] = topology.digest(
            {k: v for k, v in candidate.items() if k != 'validation'})

    def test_binding_is_readonly_and_binds_same_complete_candidate(self):
        candidate = deepcopy(self.candidate)
        result = self.assess(candidate)
        self.assertEqual(candidate, self.candidate)
        self.assertEqual(result['binding']['candidate_sha256'], candidate['validation']['candidate_sha256'])

    def test_wrong_receiver_supply_pin_type_and_ground_rejected(self):
        mutations = [('safety_controller', 'PA30', 'physical', '2'),
                     ('safety_controller', 'PA30', 'type', 'open_collector'),
                     ('safety_controller', 'VDD', 'net', '3V3_MAIN'),
                     ('slow_io', 'VCCP', 'net', 'AON_SAFE_3V3'),
                     ('slow_io', 'GND', 'net', 'SIGNAL_GROUND'),
                     ('power_fault_pullup', 'END_1', 'net', 'AON_SAFE_3V3')]
        for instance, contact, field, value in mutations:
            candidate = deepcopy(self.candidate)
            pin = next(p for p in candidate['pins'] if p['instance'] == instance and p['contact'] == contact)
            pin[field] = value
            self.refresh_digest(candidate)
            with self.subTest(instance=instance, field=field), self.assertRaises((ValueError, AssertionError)):
                self.assess(candidate)

    def test_missing_duplicate_or_extra_fault_endpoint_rejected(self):
        for mutation in ('missing', 'duplicate', 'extra'):
            candidate = deepcopy(self.candidate)
            pin = next(p for p in candidate['pins'] if p['instance'] == 'ext_efuse' and p['contact'] == 'FLT')
            if mutation == 'missing':
                candidate['pins'].remove(pin)
            elif mutation == 'duplicate':
                candidate['pins'].append(deepcopy(pin))
            else:
                candidate['pins'].append({**deepcopy(pin), 'instance': 'surprise', 'endpoint': 'surprise.FLT'})
            self.refresh_digest(candidate)
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                self.assess(candidate)

    def test_stale_content_receipt_is_not_trusted(self):
        candidate = deepcopy(self.candidate)
        candidate['parameters']['monitor_supply_node'] = 'AON_SAFE_3V3'
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.assess(candidate)

    def test_narrowed_resistor_tolerance_cannot_be_used_for_native_pullup(self):
        with self.assertRaisesRegex(ValueError, 'tolerance'):
            bus.assess_candidate(self.candidate, **{**AXES, 'resistance_ohm': ['10000', '10000']})

    def test_parent_applies_bound_screen_to_all_eighteen_variants(self):
        dc = deepcopy(self.dc)
        dc['auxiliary_scope'] = cell.auxiliary.assess_current(dc, source_hashes=self.native['source_sha256'])
        portfolio = cell.build_topology_portfolio(dc, self.native['source_sha256'])
        self.assertEqual(len(portfolio['fault_bus_screens']), 2)
        self.assertEqual(len(portfolio['candidates']), 18)
        for candidate in portfolio['candidates']:
            screen = portfolio['fault_bus_screens'][candidate['fault_bus_screen_ref']]
            self.assertTrue(screen['common_source_temperature_hypothesis']['thresholds_admitted'])
            self.assertFalse(screen['prior_temperature_hypothesis']['thresholds_admitted'])
            self.assertEqual(candidate['fault_bus_binding']['candidate_sha256'],
                             candidate['validation']['candidate_sha256'])
            self.assertFalse(candidate['output_bus']['loaded_logic_proven'])
            self.assertFalse(candidate['qualified'])


if __name__ == '__main__':
    unittest.main()
