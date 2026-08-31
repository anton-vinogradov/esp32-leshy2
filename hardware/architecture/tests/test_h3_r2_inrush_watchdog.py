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

    def test_every_generated_start_and_load_step_passes(self):
        summary = self.manifest["summary"]
        self.assertEqual(5, summary["startup_envelopes"])
        self.assertEqual(summary["startup_envelopes"], summary["passed_startup_envelopes"])
        self.assertEqual(4, summary["load_step_rails"])
        self.assertEqual(summary["load_step_rails"], summary["passed_load_step_rails"])
        self.assertGreater(summary["pcb_capacitor_instances"], 100)
        self.assertTrue(all(row["status"] == "pass" for row in self.manifest["startup_envelopes"]))

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

    def test_h3_r2_2_crosscheck_closes_without_authorizing_layout(self):
        self.assertEqual("reviewed_h3_r2_2_power_transitions_complete", self.result["status"])
        self.assertTrue(all(self.result["checks"].values()))
        self.assertEqual(0, self.result["accepted_results"]["analytical_failures"])
        self.assertEqual(0, self.result["accepted_results"]["automatic_restarts"])
        self.assertEqual("H3-R2.3", self.result["next"]["marker"])
        self.assertFalse(self.result["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])
        self.assertFalse(self.result["authorization"]["fabrication"])


if __name__ == "__main__":
    unittest.main()
