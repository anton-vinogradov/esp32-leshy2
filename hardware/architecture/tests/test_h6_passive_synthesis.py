"""Independent forward checks for conditional inverse divider arithmetic."""

from decimal import ROUND_FLOOR, localcontext
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/verification"))
from h6_power_corner_math import Interval, resistor_interval
from h6_passive_synthesis import feedback_top_window


I = Interval
F = Fraction


def forward_values(nominal, reference, bottom, factors, leakage, interiors=False):
    """Evaluate the forward circuit equation, without inverse bound algebra."""
    domains = []
    for interval in (reference, bottom, factors, leakage):
        low, high = F(interval.minimum), F(interval.maximum)
        domains.append((low, (low + high) / 2, high) if interiors else (low, high))
    return [vref * (1 + nominal * factor / rb) + current * nominal * factor
            for vref, rb, factor, current in product(*domains)]


class H6PassiveSynthesisTest(unittest.TestCase):
    def test_ideal_window_has_exact_bounds_and_inclusive_positive_endpoints(self):
        args = (I(1, 1), I(100, 100), I(".9", "1.1"), 2, 3, I(0, 0))
        result = feedback_top_window(*args)
        self.assertTrue(result.feasible)
        self.assertEqual(result.minimum_ohm, F(1000, 9))
        self.assertEqual(result.maximum_ohm, F(2000, 11))
        for nominal in (result.minimum_ohm, result.maximum_ohm):
            values = forward_values(nominal, args[0], args[1], args[2], args[5])
            self.assertGreaterEqual(min(values), 2)
            self.assertLessEqual(max(values), 3)
        self.assertLess(min(forward_values(result.minimum_ohm - F(1, 1000),
                                          args[0], args[1], args[2], args[5])), 2)
        self.assertGreater(max(forward_values(result.maximum_ohm + F(1, 1000),
                                             args[0], args[1], args[2], args[5])), 3)

    def test_initial_tolerance_can_collapse_nonempty_physical_resistance_window(self):
        exact = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), "1.99", "2.01", I(0, 0))
        self.assertEqual((exact.minimum_ohm, exact.maximum_ohm), (F(99), F(101)))
        uncertain = feedback_top_window(I(1, 1), I(100, 100), I(".9", "1.1"), "1.99", "2.01", I(0, 0))
        self.assertFalse(uncertain.feasible)
        self.assertEqual((uncertain.minimum_ohm, uncertain.maximum_ohm), (F(110), F(1010, 11)))
        self.assertEqual(uncertain.infeasible_reason, "incompatible_corner_bounds")

    def test_positive_point_solution_is_valid_but_zero_only_is_not(self):
        point = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), 2, 2, I(0, 0))
        self.assertTrue(point.feasible)
        self.assertEqual((point.minimum_ohm, point.maximum_ohm), (F(100), F(100)))
        zero = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), 1, 1, I(0, 0))
        self.assertFalse(zero.feasible)
        self.assertEqual(zero.infeasible_reason, "no_strictly_positive_resistance")

    def test_inverted_requirements_are_infeasible_not_reordered(self):
        result = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), 3, 2, I(0, 0))
        self.assertFalse(result.feasible)
        self.assertEqual(result.infeasible_reason, "required_minimum_exceeds_maximum")

    def test_negative_upper_resistance_is_preserved_as_infeasibility(self):
        result = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), ".5", ".9", I(0, 0))
        self.assertFalse(result.feasible)
        self.assertEqual(result.minimum_ohm, 0)
        self.assertEqual(result.maximum_ohm, -10)

    def test_negative_leakage_reverses_slope_and_bound_direction(self):
        result = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), ".8", ".9", I("-.02", "-.02"))
        self.assertTrue(result.feasible)
        self.assertEqual((result.minimum_ohm, result.maximum_ohm), (F(10), F(20)))

    def test_mixed_slope_signs_bound_the_same_positive_nominal(self):
        result = feedback_top_window(I(1, 1), I(100, 100), I(1, 1), ".8", "1.6", I("-.02", ".02"))
        self.assertTrue(result.feasible)
        self.assertEqual((result.minimum_ohm, result.maximum_ohm), (F(0), F(20)))

    def test_zero_slopes_are_unbounded_only_when_the_constant_fits(self):
        args = (I(1, 1), I(100, 100), I(".9", "1.1"))
        allowed = feedback_top_window(*args, 1, 1, I("-.01", "-.01"))
        self.assertTrue(allowed.feasible)
        self.assertIsNone(allowed.maximum_ohm)
        blocked = feedback_top_window(*args, ".9", ".99", I("-.01", "-.01"))
        self.assertFalse(blocked.feasible)
        self.assertEqual(blocked.infeasible_reason, "zero_slope_corner_outside_requirements")
        mixed = feedback_top_window(*args, 1, 2, I("-.01", 0))
        self.assertTrue(mixed.feasible)
        self.assertEqual(mixed.maximum_ohm, F(1000, 11))
        self.assertFalse(feedback_top_window(*args, "1.1", 2, I("-.01", 0)).feasible)

    def test_composed_initial_and_tcr_factors_match_independent_forward_cases(self):
        bottom = resistor_interval(10000, ".001", 25, -40, 125, reference_temperature_c=20)
        factors = resistor_interval(1, ".001", 25, -40, 125, reference_temperature_c=20)
        args = (I(".591", ".609"), bottom, factors)
        raw = feedback_top_window(*args, "3.07090", "3.29", I(0, 0))
        self.assertTrue(raw.feasible)
        self.assertLessEqual(raw.minimum_ohm, 43200)
        self.assertGreaterEqual(raw.maximum_ohm, 43200)
        # Enumerate the primitive signs and temperatures, not the factor bounds.
        resistors = {}
        for name, nominal in (("top", 43200), ("bottom", 10000)):
            resistors[name] = [nominal * (1 + F(sign, 1000)) *
                               (1 + tcr_sign * F(25, 1000000) * (temperature - 20))
                               for sign, tcr_sign, temperature in product((-1, 1), (-1, 1), (-40, 125))]
        corners = [v * (1 + rt / rb) for v, rt, rb in product(
            (F(591, 1000), F(609, 1000)), resistors["top"], resistors["bottom"])]
        self.assertEqual(len(corners), 128)
        self.assertGreaterEqual(min(corners), F("3.07090"))
        self.assertLessEqual(max(corners), F("3.29"))
        full = feedback_top_window(*args, "3.2725", "3.29", I(0, 0))
        self.assertFalse(full.feasible)
        self.assertGreater(full.minimum_ohm, full.maximum_ohm)

    def test_forward_corner_and_interior_grid_agrees_with_inverse_membership(self):
        reference, bottom, factors = I(1, 2), I(50, 100), I(".9", "1.1")
        for leakage, limits in product((I(0, 0), I("-.03", ".02"), I("-.06", "-.05")),
                                       ((".5", "4"), ("1.5", "3"), ("-2", "-.5"))):
            result = feedback_top_window(reference, bottom, factors, *limits, leakage)
            for nominal in map(F, (0, "0.1", 1, 10, 50, 100, 1000)):
                values = forward_values(nominal, reference, bottom, factors, leakage, interiors=True)
                forward_accepts = nominal > 0 and F(limits[0]) <= min(values) and max(values) <= F(limits[1])
                inverse_accepts = (result.feasible and nominal > 0 and nominal >= result.minimum_ohm
                                   and (result.maximum_ohm is None or nominal <= result.maximum_ohm))
                with self.subTest(leakage=leakage, limits=limits, nominal=nominal):
                    self.assertEqual(inverse_accepts, forward_accepts)

    def test_exact_rational_boundary_does_not_depend_on_decimal_context(self):
        args = (I(".591", ".609"), I(9970, 10030), I(".999", "1.001"), "3.1", "3.3", I(0, 0))
        expected = feedback_top_window(*args)
        with localcontext() as context:
            context.prec = 3
            context.rounding = ROUND_FLOOR
            self.assertEqual(expected, feedback_top_window(*args))
            self.assertEqual(context.prec, 3)
            self.assertEqual(context.rounding, ROUND_FLOOR)
        self.assertIsInstance(expected.minimum_ohm, Fraction)
        self.assertIsInstance(expected.maximum_ohm, Fraction)

    def test_invalid_scalar_types_and_nonfinite_bounds_fail_closed(self):
        for invalid in (True, 0.1, None, "NaN", "sNaN", "Infinity", "bad", F(1, 2)):
            for position in (3, 4):
                args = [I(1, 1), I(100, 100), I(1, 1), 2, 3, I(0, 0)]
                args[position] = invalid
                with self.subTest(position=position, invalid=invalid), self.assertRaises(ValueError):
                    feedback_top_window(*args)

    def test_invalid_physical_intervals_and_missing_leakage_fail_closed(self):
        for position in range(3):
            for invalid in (I(0, 1), I(-1, 1), (1, 1), None):
                args = [I(1, 1), I(100, 100), I(1, 1), 2, 3, I(0, 0)]
                args[position] = invalid
                with self.subTest(position=position, invalid=invalid), self.assertRaises(ValueError):
                    feedback_top_window(*args)
        for invalid in (None, (0, 0), 0):
            with self.subTest(leakage=invalid), self.assertRaises(ValueError):
                feedback_top_window(I(1, 1), I(100, 100), I(1, 1), 2, 3, invalid)
        with self.assertRaises(TypeError):
            feedback_top_window(I(1, 1), I(100, 100), I(1, 1), 2, 3)
        for bounds in ((2, 1), ("NaN", 1), (0.1, 1), (False, 1)):
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                feedback_top_window(I(1, 1), I(100, 100), I(*bounds), 2, 3, I(0, 0))


if __name__ == "__main__":
    unittest.main()
