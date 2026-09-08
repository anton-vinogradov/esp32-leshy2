import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_inrush_watchdog.py"


class H3R2InrushWatchdogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h3_r2_inrush_watchdog", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.outputs, cls.manifest, cls.result = cls.module.build()

    def test_generated_artifacts_are_current(self):
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)

    def test_fitted_main_current_exposes_startup_and_load_step_failures(self):
        summary = self.manifest["summary"]
        self.assertEqual(5, summary["startup_envelopes"])
        self.assertEqual(4, summary["passed_startup_envelopes"])
        self.assertEqual(4, summary["load_step_rails"])
        self.assertEqual(3, summary["passed_load_step_rails"])
        self.assertGreater(summary["pcb_capacitor_instances"], 100)
        self.assertEqual(["3V3_MAIN"], [row["rail"] for row in self.manifest["startup_envelopes"] if row["status"] != "pass"])
        main = next(row for row in self.manifest["startup_envelopes"] if row["rail"] == "3V3_MAIN")
        self.assertEqual("3117.079", main["combined_current_ma"])
        self.assertEqual("3072.961", main["effective_hardware_min_ma"])
        self.assertLess(Decimal(main["current_margin_ma"]), 0)

    def test_u214_470uf_reservoir_is_inside_the_checked_envelope(self):
        admission = self.manifest["external_accessory_admission"]
        self.assertEqual(470, admission["official_u214_capacitance_uf"])
        self.assertEqual(705, admission["admitted_external_capacitance_uf"])
        external = [row for row in self.manifest["startup_envelopes"] if row["rail"].startswith("5V_")]
        self.assertEqual(2, len(external))
        self.assertTrue(all(Decimal(row["current_margin_ma"]) > 0 for row in external))

    def test_watchdog_deadline_and_topology_are_exact(self):
        watchdog = self.manifest["watchdog"]
        self.assertEqual("Texas Instruments TPS3435CAKAGDDFR", watchdog["mpn"])
        self.assertEqual(500, watchdog["device_startup_time_us_max"])
        self.assertEqual({"min": 0, "typ": 0, "max": 0}, watchdog["watchdog_startup_delay_ms"])
        self.assertEqual({"min": 1440, "typ": 1600, "max": 1760}, watchdog["timeout_ms"])
        self.assertLessEqual(Decimal(watchdog["deadline_fraction_percent"]), Decimal(80))
        self.assertTrue(all(watchdog["checks"].values()))
        self.assertTrue(all(self.manifest["topology_checks"].values()))

    def test_fault_led_uses_latched_fault_kill(self):
        self.assertTrue(self.manifest["topology_checks"]["fault_led_series.END_1"])
        correction = next(row for row in self.manifest["corrected_findings"] if row["id"] == "H3-R2.2.3-F01")
        self.assertIn("FAULT_KILL", correction["after"])

    def test_fault_record_is_power_cut_monotonic_and_has_endurance(self):
        record = self.manifest["fault_record"]
        self.assertEqual(2, record["slots"])
        self.assertEqual(1024, record["sector_bytes_each"])
        self.assertGreaterEqual(record["minimum_fault_commits"], 200_000)
        self.assertIn("commit marker", " ".join(record["commit_order"]))
        self.assertIn("not guaranteed", record["complete_aon_loss"])

    def test_dt_and_half_dt_preserve_the_result(self):
        convergence = self.manifest["convergence"]
        self.assertTrue(convergence["same_pass_fail"])
        self.assertLessEqual(Decimal(convergence["maximum_ramp_time_difference_ms"]), Decimal(convergence["dt_ms"]))

    def test_equal_current_failure_is_repeatable_not_divergence(self):
        row = self.module.ramp_rounding_comparison(Decimal("4.226"), Decimal(".01"), Decimal(".005"), False)
        self.assertEqual("fail", row["current_classification_dt"])
        self.assertEqual("fail", row["current_classification_dt2"])
        self.assertTrue(row["same_result"])
        self.assertIn("not timestep simulation", row["scope"])
        self.assertEqual("4.230000", row["ramp_ms"])
        self.assertEqual("4.230000", row["ramp_dt2_ms"])
        main = next(row for row in self.manifest["convergence"]["rows"] if row["rail"] == "3V3_MAIN")
        self.assertTrue(main["same_result"])
        self.assertEqual("fail", main["current_classification_dt"])
        for missing in (None, 0, 1, "fail"):
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                self.module.ramp_rounding_comparison(Decimal(1), Decimal(".01"), Decimal(".005"), missing)

    def test_h3_r2_2_crosscheck_retains_provisional_checks_without_closure(self):
        self.assertEqual("review_required", self.result["status"])
        self.assertFalse(self.result["current_analytical_scope_complete"])
        self.assertEqual({"inrush", "load_steps"}, {key for key, value in self.result["checks"].items() if not value})
        self.assertGreater(self.result["accepted_results"]["analytical_failures"], 0)
        self.assertEqual(0, self.result["accepted_results"]["automatic_restarts"])
        self.assertEqual("H3-R2.3", self.result["next"]["marker"])
        self.assertFalse(self.result["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])
        self.assertFalse(self.result["authorization"]["fabrication"])


if __name__ == "__main__":
    unittest.main()
