import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h3_r2_transition_sequences.py"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-transition-sequences.json"


class H3R2TransitionSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("14 scenarios", result.stdout)

    def test_every_transition_and_topology_check_passes(self):
        self.assertEqual("reviewed_startup_shutdown_reset_and_recovery", self.report["status"])
        self.assertEqual(14, self.report["summary"]["scenarios"])
        self.assertEqual(14, self.report["summary"]["passed_scenarios"])
        self.assertEqual(0, self.report["summary"]["topology_failures"])
        self.assertEqual([], self.report["errors"])
        self.assertTrue(all(row["status"] == "pass" for row in self.report["scenarios"]))

    def test_s3_fault_ui_is_separate_from_hazardous_reset_paths(self):
        self.assertTrue(self.report["net_checks"]["S3_RESET_KILL_GATE_exact"])
        scenario = next(row for row in self.report["scenarios"] if row["id"] == "SEQ-10")
        self.assertFalse(scenario["actual_final"]["permit"])
        self.assertFalse(scenario["actual_final"]["hazardous_enabled"])
        self.assertTrue(scenario["actual_final"]["s3_available"])
        self.assertFalse(scenario["actual_final"]["s3_reset_asserted"])

    def test_auto_restart_paths_remain_blocked(self):
        for sequence_id in ("SEQ-02", "SEQ-04", "SEQ-05", "SEQ-07", "SEQ-08", "SEQ-09", "SEQ-11", "SEQ-12", "SEQ-13"):
            scenario = next(row for row in self.report["scenarios"] if row["id"] == sequence_id)
            self.assertFalse(scenario["actual_final"]["permit"], sequence_id)
            self.assertFalse(scenario["actual_final"]["hazardous_enabled"], sequence_id)

    def test_exact_timing_contract_is_bound(self):
        timing = self.report["timing"]
        self.assertEqual({"min": 12, "typ": 20, "max": 28}, timing["supervisor_ct_open_reset_delay_ms"])
        self.assertEqual({"min": 1.44, "typ": 1.6, "max": 1.76}, timing["watchdog_timeout_s"])
        self.assertEqual({"min": 180, "typ": 200, "max": 220}, timing["watchdog_assert_time_ms"])
        self.assertGreater(timing["rearm_rc"]["analytical_kill_margin_ms"], 0)

    def test_authorization_stops_before_layout_or_order(self):
        authorization = self.report["authorization"]
        self.assertFalse(authorization["pcb_placement_or_routing"])
        self.assertFalse(authorization["purchasing"])
        self.assertFalse(authorization["fabrication"])


if __name__ == "__main__":
    unittest.main()
