"""Independent threshold inequalities and integration with native rail demand."""

from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import compare_main_feedback as variants
import h6_main_monitor_window as monitor


class MonitorTest(unittest.TestCase):
    def test_separate_rising_and_falling_limits(self):
        bad = monitor.screen(F("3.05"), F("3.3"), F("1.071"), F("1.23"))
        self.assertFalse(bad["necessary_ideal_window_exists"])
        self.assertEqual(F(bad["minimum_gain_exact"]), F("3.05") / F("1.071"))
        self.assertEqual(F(bad["maximum_gain_exact"]), F("3.3") / F("1.23"))

    def test_equality_is_feasible_without_float_rounding(self):
        row = monitor.screen(F(3), F(3), F(1), F(1))
        self.assertTrue(row["necessary_ideal_window_exists"])
        self.assertEqual(F(row["rising_margin_v_exact"]), 0)
        self.assertFalse(monitor.screen(F(3), F(3) - F(1, 10**70), F(1), F(1))["necessary_ideal_window_exists"])

    def test_divider_cannot_amplify_sense_above_the_rail(self):
        self.assertFalse(monitor.screen(F(".1"), F(".2"), F(1), F(1))["necessary_ideal_window_exists"])

    def test_negative_or_zero_rail_ceiling_is_retained_as_failure(self):
        for ceiling in (F(0), F(-1)):
            self.assertFalse(monitor.screen(F(3), ceiling, F(1), F(1))["necessary_ideal_window_exists"])

    def test_invalid_inputs_do_not_get_coerced_to_valid_bounds(self):
        for bad in (True, 1.0, "1", None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                monitor.screen(bad, F(3), F(1), F(1))
        for args in ((0, 3, 1, 1), (3, 3, 0, 1), (3, 3, 2, 1)):
            with self.assertRaises(ValueError):
                monitor.screen(*map(F, args))

    def test_candidate_failure_does_not_mean_all_ratios_fail(self):
        result = monitor.assess(floor=F("3.05"), selected_local_min=F("3.06"),
                                optimistic_local_min_ceiling=F("3.2"))
        row = next(r for r in result["rows"] if r["id"] == "candidate_tps389001")
        self.assertFalse(row["selected_feedback_pair"]["necessary_ideal_window_exists"])
        self.assertTrue(row["optimistic_continuous_feedback_ceiling"]["necessary_ideal_window_exists"])
        self.assertFalse(row["qualified"])
        self.assertFalse(result["qualified"])

    def test_absent_candidate_is_unknown_not_pass(self):
        result = monitor.assess(floor=F(3), selected_local_min=None, optimistic_local_min_ceiling=None)
        self.assertTrue(all(r["selected_feedback_pair"] is None and r["optimistic_continuous_feedback_ceiling"] is None for r in result["rows"]))

    def test_transcribed_threshold_derivations(self):
        rows = {r["id"]: r for r in monitor.load_reviewed_rows()}
        old = rows["candidate_tps389001"]
        self.assertEqual(F(old["falling_min_v"]), F("1.15") * F(".99"))
        self.assertEqual(F(old["rising_max_v"]), F("1.157") * F("1.01"))
        new = rows["candidate_tps3808eg01"]
        self.assertEqual(F(new["falling_min_v"]), F(".405") * F(".98"))
        self.assertEqual(F(new["rising_max_v"]), F(".405") * F("1.02") * F("1.025"))
        # Numeric static feasibility never upgrades a nominal timing row.
        self.assertIn("no maximum", old["timing"])
        self.assertIn("5%overdrive", new["timing"])
        for row in rows.values():
            self.assertEqual(len(row["source"]["pdf_sha256"]), 64)

    def test_altered_missing_and_symlinked_transcriptions_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.json"
            with patch.object(monitor, "ROWS_PATH", path), self.assertRaises(ValueError):
                monitor.load_reviewed_rows()
            path.write_bytes(monitor.ROWS_PATH.read_bytes() + b" ")
            with patch.object(monitor, "ROWS_PATH", path), self.assertRaisesRegex(ValueError, "changed"):
                monitor.load_reviewed_rows()
            link = Path(directory) / "link.json"
            link.symlink_to(monitor.ROWS_PATH)
            with patch.object(monitor, "ROWS_PATH", link), self.assertRaisesRegex(ValueError, "symlinked"):
                monitor.load_reviewed_rows()


@unittest.skipUnless(importlib.util.find_spec("edg"), "prepared EDG runtime needed")
class CoupledIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = variants.run()
        cls.rows = {r["id"]: r for r in cls.report["variants"]}

    def test_all_three_selected_voltage_pairs_fail_monitor_window(self):
        for name in ("ideal_feedback", "zero_efuse_loss", "low_loss_sourcing_target"):
            row = self.rows[name]
            self.assertEqual(row["selection"]["status"], "conditional_candidate")
            self.assertTrue(all(not r["selected_feedback_pair"]["necessary_ideal_window_exists"]
                                for r in row["monitor_window"]["rows"]))

    def test_only_zero_loss_hypothesis_has_tps3890_continuous_window(self):
        feasible = [(row["id"], r["id"]) for row in self.rows.values() for r in row["monitor_window"]["rows"]
                    if r["optimistic_continuous_feedback_ceiling"]["necessary_ideal_window_exists"]]
        self.assertEqual(feasible, [("zero_efuse_loss", "candidate_tps389001")])

    def test_loaded_local_not_consumer_or_nominal_voltage_is_used(self):
        row = self.rows["low_loss_sourcing_target"]
        screen = row["monitor_window"]
        low = F(row["selection"]["average_v_exact"][0]) - F(".01") - F("4.25") * F(".020")
        self.assertEqual(F(screen["selected_pair_local_min_v_exact"]), low)
        self.assertEqual(F(screen["derived_local_falling_floor_v_exact"]), F("3.03"))
        self.assertNotEqual(low, F("3.3"))

    def test_ideal_feedback_upper_ceiling_is_independent_hand_calculation(self):
        # Perfect feedback can at most produce3.29 V average under3.3 V
        # maximum and20-mVpp ripple. Existing50-mohm eFuse at4.25 A.
        value = self.rows["ideal_feedback"]["monitor_window"]["optimistic_local_min_ceiling_v_exact"]
        self.assertEqual(F(value), F("3.29") - F(".01") - F("4.25") * F(".05"))

    def test_source_hashes_and_all_original_requirements_remain(self):
        hashes = self.report["source_sha256"]
        self.assertIn(str(monitor.ROWS_PATH.relative_to(ROOT)), hashes)
        self.assertIn("hardware/verification/h6_main_monitor_window.py", hashes)
        self.assertEqual(len(self.report["invariant_demands"]["load_cases_a"]), 58)
        self.assertFalse(self.report["qualified"])


if __name__ == "__main__":
    unittest.main()
