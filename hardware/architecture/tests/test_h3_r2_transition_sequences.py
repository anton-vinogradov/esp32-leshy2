import copy
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h3_r2_transition_sequences.py"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-transition-sequences.json"
SPEC = importlib.util.spec_from_file_location("h3_transition_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2TransitionSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Source-only replay; the separate --check test still binds published outputs.
        _, cls.report = MODULE.build()

    def test_nx_halves_preserve_exact_physical_reset_nets(self):
        nets = MODULE.load(MODULE.NETS)["rows"]
        instances = MODULE.load(MODULE.INSTANCES)["rows"]
        devices = MODULE.load(MODULE.DEVICES)["devices"]
        checks = MODULE.reset_sink_physical_checks(nets, instances, devices)
        self.assertEqual(17, len(checks))
        self.assertTrue(all(checks.values()), checks)
        contract = MODULE.load(MODULE.CONTRACT)
        self.assertEqual("S3_RESET_KILL_GATE", contract["required_endpoints"]["safe_reset_sink_a.G2"])
        self.assertNotIn("safe_reset_sink_a.G1", contract["required_net_members"]["S3_RESET_KILL_GATE"])
        for name in ("safe_reset_sink_a", "safe_reset_sink_b"):
            actual = [row for row in nets if row["instance"] == name]
            # A name-only change cannot pass if either the physical pad or net
            # is wrong; a duplicated endpoint must not disappear into a dict.
            for row in actual:
                for key, wrong in (("physical", "99"), ("net", "WRONG_NET"),
                                   ("device_id", "diodes_2n7002dw_7_f"), ("reference", "Q2")):
                    broken = copy.deepcopy(nets)
                    next(value for value in broken if value["endpoint"] == row["endpoint"])[key] = wrong
                    self.assertFalse(all(MODULE.reset_sink_physical_checks(broken, instances, devices).values()))
            broken = nets + [copy.deepcopy(actual[0])]
            self.assertFalse(all(MODULE.reset_sink_physical_checks(broken, instances, devices).values()))
        old_pin_map = copy.deepcopy(devices)
        contacts = old_pin_map["nexperia_nx3008nbks_115"]["contacts"]
        for left, right in (("G1", "G2"), ("D1", "D2"), ("S1", "S2")):
            contacts[left]["physical"], contacts[right]["physical"] = contacts[right]["physical"], contacts[left]["physical"]
        self.assertFalse(all(MODULE.reset_sink_physical_checks(nets, instances, old_pin_map).values()))

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
        self.assertEqual("review_required", self.report["status"])
        self.assertEqual(14, self.report["summary"]["scenarios"])
        self.assertEqual(14, self.report["summary"]["passed_scenarios"])
        self.assertEqual(0, self.report["summary"]["topology_failures"])
        self.assertEqual([], self.report["provisional_numerical_errors"])
        self.assertIn("applicability:supervisor_assertion_bound", self.report["errors"])
        self.assertIn("applicability:supervisor_hysteresis_bound", self.report["errors"])
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
