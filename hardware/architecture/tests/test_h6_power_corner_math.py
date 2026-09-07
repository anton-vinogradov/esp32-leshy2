"""Independent arithmetic and domain checks, not circuit qualification."""

from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h6_power_corner_math.py"
spec = importlib.util.spec_from_file_location("h6_power_corner_math_test", SCRIPT)
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)
D = Decimal
I = math.Interval


class H6PowerCornerMathTest(unittest.TestCase):
    def assertDecimalNear(self, actual, expected, tolerance="1e-35"):
        with localcontext() as context:
            context.prec = 60
            self.assertLessEqual(abs(actual - D(expected)), D(tolerance))

    def assertEncloses(self, outer, inner):
        self.assertLessEqual(outer.minimum, inner.minimum)
        self.assertGreaterEqual(outer.maximum, inner.maximum)

    def test_interval_accepts_exact_point_and_signed_bounds(self):
        self.assertEqual(I("1.25", D("1.25")), I(D("1.25"), D("1.25")))
        self.assertEqual(I(-1, 2).minimum, D(-1))

    def test_interval_rejects_nonfinite_binary_and_invalid_inputs(self):
        for bad in ("NaN", "sNaN", "Infinity", "-Infinity", "nonsense", True, 0.1, None):
            for pair in ((bad, "1"), ("0", bad)):
                with self.subTest(pair=pair), self.assertRaises(ValueError):
                    I(*pair)
        with self.assertRaises(ValueError):
            I("2", "1")

    def test_resistor_initial_and_temperature_factors_are_composed(self):
        self.assertEqual(math.resistor_interval("1000", ".01", "100", "-40", "125"),
                         I("980.1", "1020.1"))

    def test_resistor_largest_temperature_excursion_can_be_cold(self):
        self.assertEqual(math.resistor_interval("1000", "0", "100", "-55", "35"),
                         I("992", "1008"))
        self.assertEqual(math.resistor_interval("1000", "0", "100", "10", "30",
                                                reference_temperature_c="20"),
                         I("999", "1001"))

    def test_named_solder_and_life_budgets_preserve_absolute_ohm(self):
        budgets = (math.ResistanceDriftBudget("solder", ".01", ".05"),
                   math.ResistanceDriftBudget("load life", ".01", ".05"))
        self.assertEqual(math.resistor_interval("1150", ".01", "100", "-40", "125", budgets),
                         I("1104.5869065", "1196.7961165"))
        self.assertEqual(math.resistor_interval("1180", ".01", "100", "-40", "125", budgets),
                         I("1133.4047868", "1228.0142368"))
        self.assertEqual(math.resistor_interval("1", "0", "0", "25", "25",
                                                [math.ResistanceDriftBudget("absolute", ".01", ".05")]),
                         I(".94", "1.06"))

    def test_drift_sequence_is_explicit_not_silently_reordered(self):
        percent = math.ResistanceDriftBudget("fraction only", ".1")
        absolute = math.ResistanceDriftBudget("absolute only", "0", "1")
        self.assertEqual(math.resistor_interval(100, 0, 0, 25, 25, [percent, absolute]), I(89, 111))
        self.assertEqual(math.resistor_interval(100, 0, 0, 25, 25, [absolute, percent]), I("89.1", "111.1"))

    def test_duplicate_untyped_or_empty_stress_budget_is_rejected(self):
        for name in ("", " ", None, 4):
            with self.subTest(name=name), self.assertRaises(ValueError):
                math.ResistanceDriftBudget(name, 0)
        for budgets in (None, {"life": ".01"}, ["life"],
                        [math.ResistanceDriftBudget("life", 0), math.ResistanceDriftBudget(" life ", 0)]):
            with self.subTest(budgets=budgets), self.assertRaises(ValueError):
                math.resistor_interval(1000, 0, 0, 25, 25, budgets)

    def test_stress_budget_rejects_invalid_magnitude_or_collapsed_resistance(self):
        for fraction, absolute in (("-1", "0"), ("1", "0"), ("0", "-.01"), ("NaN", "0")):
            with self.subTest(fraction=fraction, absolute=absolute), self.assertRaises(ValueError):
                math.ResistanceDriftBudget("invalid", fraction, absolute)
        with self.assertRaises(ValueError):
            math.resistor_interval(1, 0, 0, 25, 25, [math.ResistanceDriftBudget("collapse", 0, 1)])

    def test_resistor_rejects_degenerate_physical_domain(self):
        cases = [(0, 0, 0, 25, 25), (-1, 0, 0, 25, 25), (1000, 1, 0, 25, 25),
                 (1000, "-.01", 0, 25, 25), (1000, 0, -1, 25, 25),
                 (1000, 0, 0, 50, 25), (1000, 0, 10000, 25, 125),
                 ("Infinity", 0, 0, 25, 25), (1000, 0, 0, "NaN", 25)]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                math.resistor_interval(*args)

    def test_larger_resistor_uncertainties_cannot_narrow_bounds(self):
        base = math.resistor_interval(1000, ".01", 100, -40, 85)
        for wider in (math.resistor_interval(1000, ".02", 100, -40, 85),
                      math.resistor_interval(1000, ".01", 200, -40, 85),
                      math.resistor_interval(1000, ".01", 100, -55, 125),
                      math.resistor_interval(1000, ".01", 100, -40, 85,
                                             [math.ResistanceDriftBudget("life", ".01", ".05")])):
            with self.subTest(wider=wider):
                self.assertEncloses(wider, base)

    def test_efuse_equation_units_and_gain_are_independent_of_resistor(self):
        self.assertEqual(math.efuse_current_interval(I(1000, 1000)), I("5.1723", "6.3217"))
        self.assertEqual(math.efuse_current_interval(I(1000, 2000), "0", "6000"), I(3, 6))

    def test_efuse_full_stress_example_is_not_nominal_or_datasheet_row_scaling(self):
        # R bounds are independent literal values, not re-derived using the helper under test.
        result = math.efuse_current_interval(I("1104.5869065", "1196.7961165"))
        self.assertDecimalNear(result.minimum, "4.321788756405946", "1e-14")
        self.assertDecimalNear(result.maximum, "5.723135013460347", "1e-14")

    def test_efuse_interval_widens_with_gain_or_resistance_uncertainty(self):
        base = math.efuse_current_interval(I(1100, 1200))
        self.assertEncloses(math.efuse_current_interval(I(1100, 1200), ".2"), base)
        self.assertEncloses(math.efuse_current_interval(I(1000, 1300)), base)

    def test_efuse_rejects_unphysical_or_untyped_inputs(self):
        for resistance in (I(0, 1), I(-1, 1), (1000, 1000), None):
            with self.subTest(resistance=resistance), self.assertRaises(ValueError):
                math.efuse_current_interval(resistance)
        for tolerance in ("-1", "1", "NaN"):
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                math.efuse_current_interval(I(1000, 1000), tolerance)
        for constant in (0, -1, "Infinity"):
            with self.subTest(constant=constant), self.assertRaises(ValueError):
                math.efuse_current_interval(I(1000, 1000), equation_constant_a_ohm=constant)

    def test_pg_rise_and_fall_have_separate_reference_and_leakage_corners(self):
        thresholds = math.power_good_thresholds(I("1.178", "1.23"), I("1.071", "1.13"),
                                               I(44847, 45753), I(29700, 30300), I("-.000001", ".000001"))
        self.assertDecimalNear(thresholds.rising_v.minimum, "2.876709633663366336633663366336633663366336633663366337")
        self.assertDecimalNear(thresholds.rising_v.maximum, "3.170574212121212121212121212121212121212121212121212121")
        self.assertDecimalNear(thresholds.falling_v.minimum, "2.611339039603960396039603960396039603960396039603960396")
        self.assertDecimalNear(thresholds.falling_v.maximum, "2.916523707070707070707070707070707070707070707070707071")

    def test_negative_leakage_can_reverse_the_top_resistor_derivative(self):
        self.assertEqual(math.divider_threshold_interval(I(1, 1), I(10, 20), I(100, 100), I("-.02", "-.015")),
                         I(".8", ".95"))
        self.assertEqual(math.divider_threshold_interval(I(1, 1), I(10, 20), I(100, 100), I("-.02", ".02")),
                         I(".8", "1.6"))

    def test_positive_sink_leakage_increases_required_rail_voltage(self):
        without = math.divider_threshold_interval(I(1, 1), I(10, 10), I(100, 100))
        sinking = math.divider_threshold_interval(I(1, 1), I(10, 10), I(100, 100), I(".01", ".01"))
        self.assertEqual(without, I("1.1", "1.1"))
        self.assertEqual(sinking, I("1.2", "1.2"))

    def test_divider_endpoint_envelope_contains_independent_rational_interior_samples(self):
        result = math.divider_threshold_interval(I(1, 2), I(10, 30), I(50, 100), I("-.03", ".02"))
        # Fraction arithmetic independently samples interiors, including the derivative sign change.
        for v in (Fraction(1), Fraction(3, 2), Fraction(2)):
            for top in (10, 20, 30):
                for bottom in (50, 75, 100):
                    for leakage in (Fraction(-3, 100), Fraction(-1, 100), Fraction(2, 100)):
                        value = v * (1 + Fraction(top, bottom)) + leakage * top
                        self.assertLessEqual(Fraction(result.minimum), value)
                        self.assertGreaterEqual(Fraction(result.maximum), value)

    def test_divider_uncertainty_widening_is_monotonic(self):
        base = math.divider_threshold_interval(I(1, 1), I(10, 20), I(50, 100))
        for wider in (math.divider_threshold_interval(I(".9", "1.1"), I(10, 20), I(50, 100)),
                      math.divider_threshold_interval(I(1, 1), I(9, 21), I(49, 101)),
                      math.divider_threshold_interval(I(1, 1), I(10, 20), I(50, 100), I("-.01", ".01"))):
            self.assertEncloses(wider, base)

    def test_pg_envelopes_need_not_be_disjoint_same_device_hysteresis(self):
        result = math.power_good_thresholds(I(1, 2), I(".9", "1.9"), I(100, 100), I(100, 100))
        self.assertEqual(result.rising_v, I(2, 4))
        self.assertEqual(result.falling_v, I("1.8", "3.8"))
        self.assertGreater(result.falling_v.maximum, result.rising_v.minimum)

    def test_divider_invalid_denominators_reference_or_leakage_are_rejected(self):
        valid = [I(1, 2), I(10, 20), I(50, 100)]
        for index in range(3):
            for invalid in (I(0, 1), I(-1, 1), None):
                args = list(valid)
                args[index] = invalid
                with self.subTest(index=index, invalid=invalid), self.assertRaises(ValueError):
                    math.divider_threshold_interval(*args)
        with self.assertRaises(ValueError):
            math.divider_threshold_interval(*valid, leakage_a=(0, 1))

    def test_algebraic_negative_divider_result_is_not_clamped(self):
        self.assertEqual(math.divider_threshold_interval(I(1, 1), I(10, 10), I(10, 10), I(-1, -1)), I(-8, -8))

    def test_series_drop_uses_maximum_load_and_resistance_for_low_corner(self):
        self.assertEqual(math.rail_series_drop_interval(I("3.2", "3.4"), I(1, 2), I(".02", ".05"), I(".01", ".03")),
                         I("3.07", "3.37"))

    def test_zero_series_loss_is_valid_but_negative_voltage_is_not_hidden(self):
        self.assertEqual(math.rail_series_drop_interval(I(3, 4), I(0, 0), I(0, 0)), I(3, 4))
        self.assertEqual(math.rail_series_drop_interval(I(1, 1), I(2, 2), I(1, 1)), I(-1, -1))

    def test_series_drop_rejects_negative_physical_terms(self):
        values = [I(3, 4), I(1, 2), I(".01", ".02"), I(0, 0)]
        for index in range(4):
            args = list(values)
            args[index] = I(-1, 1)
            with self.subTest(index=index), self.assertRaises(ValueError):
                math.rail_series_drop_interval(*args)
        with self.assertRaises(ValueError):
            math.rail_series_drop_interval(I(0, 1), *values[1:])

    def test_more_series_loss_cannot_increase_low_voltage_corner(self):
        base = math.rail_series_drop_interval(I(3, 4), I(1, 2), I(".01", ".02"))
        wider = math.rail_series_drop_interval(I(3, 4), I(1, 3), I(".01", ".03"), I(0, ".1"))
        self.assertEncloses(wider, base)

    def test_capacitor_initial_and_temperature_bounds_are_separate_factors(self):
        self.assertEqual(math.capacitance_interval("4.7e-9", ".10", ".15"), I("3.5955e-9", "5.9455e-9"))

    def test_charging_current_bounds_not_typical_slew_constant(self):
        result = math.capacitor_slew_interval(I("1.4e-6", "5.7e-6"), I("3.5955e-9", "5.9455e-9"))
        self.assertDecimalNear(result.minimum, "235.4722058699857034732150365822891262299217895887646119")
        self.assertDecimalNear(result.maximum, "1585.314977054651647893199833124739257405089695452649145")

    def test_inrush_has_farads_times_volts_per_second_units(self):
        self.assertEqual(math.inrush_current_interval(I("80e-6", "100e-6"), I(100, 200)), I(".008", ".020"))
        slew = math.capacitor_slew_interval(I("1.4e-6", "5.7e-6"), I("3.5955e-9", "5.9455e-9"))
        result = math.inrush_current_interval(I("91.11e-6", "91.11e-6"), slew)
        self.assertDecimalNear(result.maximum, "0.1444380475594493116395494367959949937421777221526908636")

    def test_larger_control_capacitance_slows_both_slew_bounds(self):
        base = math.capacitor_slew_interval(I(1, 2), I(2, 4))
        larger_cap = math.capacitor_slew_interval(I(1, 2), I(4, 8))
        larger_current = math.capacitor_slew_interval(I(2, 4), I(2, 4))
        self.assertLess(larger_cap.minimum, base.minimum)
        self.assertLess(larger_cap.maximum, base.maximum)
        self.assertGreater(larger_current.minimum, base.minimum)
        self.assertGreater(larger_current.maximum, base.maximum)
        small_load = math.inrush_current_interval(I(1, 2), base)
        large_load = math.inrush_current_interval(I(2, 4), base)
        self.assertGreater(large_load.minimum, small_load.minimum)
        self.assertGreater(large_load.maximum, small_load.maximum)

    def test_capacitor_uncertainty_widens_capacitance_and_slew_bounds(self):
        narrow = math.capacitance_interval("1e-9", ".1")
        wide = math.capacitance_interval("1e-9", ".2", ".15")
        self.assertEncloses(wide, narrow)
        self.assertEncloses(math.capacitor_slew_interval(I(1, 2), wide), math.capacitor_slew_interval(I(1, 2), narrow))

    def test_capacitor_rejects_zero_negative_or_collapsing_parameters(self):
        for args in ((0, 0, 0), (-1, 0, 0), (1, -1, 0), (1, 1, 0),
                     (1, 0, -1), (1, 0, 1), ("NaN", 0, 0), (1, "Infinity", 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                math.capacitance_interval(*args)

    def test_slew_and_inrush_reject_degenerate_physical_intervals(self):
        for function in (math.capacitor_slew_interval, math.inrush_current_interval):
            for index in (0, 1):
                for invalid in (I(0, 1), I(-1, 1), None):
                    args = [I(1, 2), I(1, 2)]
                    args[index] = invalid
                    with self.subTest(function=function.__name__, index=index, invalid=invalid), self.assertRaises(ValueError):
                        function(*args)

    def test_helpers_do_not_depend_on_or_mutate_callers_decimal_precision(self):
        expected = math.efuse_current_interval(I("1104.5869065", "1196.7961165"))
        with localcontext() as context:
            context.prec = 6
            context.rounding = ROUND_FLOOR
            actual = math.efuse_current_interval(I("1104.5869065", "1196.7961165"))
            self.assertEqual(context.prec, 6)
            self.assertEqual(context.rounding, ROUND_FLOOR)
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
