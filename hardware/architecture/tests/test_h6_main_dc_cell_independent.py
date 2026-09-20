"""Independent exact threshold oracle, not semiconductor qualification.

Enumerates deliberately wider E192 decades and expands the resistance stress
formula directly; it does not call the implementation's inverse or forward
current kernels. The signed-bias divider equations have separate SPICE tests.
"""
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import synthesize_main_dc_cell as cell
import synthesize_main_static_pair as static
import compare_main_current_limit as current


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class MainDcCellIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = current.load_current()
        cls.voltage_data = static.source.load_current()
        cls.choices = static.portfolio(cls.voltage_data, static.monitor_hypotheses(), F('.05'))
        cls.table = current.load_edg_table()

    @staticmethod
    def independent_resistance(nominal, tolerance, tcr, stress):
        low, high = nominal * (1-tolerance), nominal * (1+tolerance)
        if stress:
            # Sequential solder then load-life: each ±1% plus ±0.05 ohm.
            for _ in range(2):
                low, high = low * F('.99') - F('.05'), high * F('1.01') + F('.05')
        # -40..125 C around25 C: worst absolute displacement is100 C.
        thermal = tcr * 100 / 1000000
        return low * (1-thermal), high * (1+thermal)

    def test_wide_exact_enumeration_matches_every_candidate_and_optimum(self):
        hypotheses = {'1pct_100ppm': (F('.01'), F(100)),
                      '0.1pct_10ppm': (F('.001'), F(10)),
                      '0.05pct_10ppm': (F('.0005'), F(10))}
        native = {key: F(value) for key, value in self.native['requirements_a'].items()}
        checked = 0
        for group in self.choices['groups']:
            if group['selected_window_index'] is None:
                continue
            row = group['trials'][group['selected_window_index']]
            branches = row['loaded_diagnostic']['branch_current_a_exact']
            monitor = F(branches['monitor_top_current_a'][1])
            feedback = F(branches['feedback_top_current_a'][1])
            required = max(native['h0_step_a'] + monitor,
                           native['pf03_reserve_a'] + F('1.25') * monitor,
                           native['existing_inrush_a'] + monitor)
            ceiling = F(6) - feedback
            requirements = cell.current_requirements(self.native, row)
            self.assertEqual(F(requirements['required_lower_a']), required)
            self.assertEqual(F(requirements['strict_upper_a']), ceiling)
            self.assertLess(ceiling, 6)
            for name, (tolerance, tcr) in hypotheses.items():
                with self.subTest(divider=group['resistor_class'], rilm=name):
                    result = cell.threshold_portfolio(requirements, name, self.table)
                    expected = []
                    # Wider than the inverse domain; positive resistance and
                    # monotonic current exclude everything below/above it.
                    for bound in (F(10), F(10000)):
                        lo, hi = self.independent_resistance(bound, tolerance, tcr, False)
                        self.assertTrue(F(6585)*F('1.1')/lo >= ceiling or F(6585)/hi <= 5)
                    for nominal in sorted(v * 10**power for power in range(1, 4) for v in self.table):
                        margins = []
                        for stress in (False, True):
                            lo, hi = self.independent_resistance(nominal, tolerance, tcr, stress)
                            lower, upper = F(6585)*F('.9')/hi, F(6585)*F('1.1')/lo
                            if not (F(6585)/hi > 5 and lower >= required and upper < ceiling):
                                break
                            margins.extend((lower-required, ceiling-upper))
                        else:
                            expected.append((nominal, min(margins)))
                    actual = [(F(item['nominal_ohm']), F(item['minimum_margin_a_exact']))
                              for item in result['candidates']]
                    self.assertEqual(actual, expected)
                    self.assertTrue(expected)
                    best = max(expected, key=lambda item: (item[1], -item[0]))
                    self.assertEqual(F(result['selected_nominal_ohm']), best[0])
                    self.assertFalse(result['qualified'])
                    checked += 1
        self.assertEqual(checked, 6)
        self.assertEqual(current.snapshot(current.source_paths()), self.native['source_sha256'])
        self.assertEqual(static.source.snapshot(self.voltage_data['paths']), self.voltage_data['before'])


if __name__ == '__main__':
    unittest.main()
