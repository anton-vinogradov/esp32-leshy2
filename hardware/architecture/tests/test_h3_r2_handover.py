import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_handover.py"


class H3R2HandoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h3_r2_handover", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.outputs, cls.manifest = cls.module.build()

    def test_generated_artifacts_are_current(self):
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)

    def test_complete_transition_register_passes(self):
        summary = self.manifest["summary"]
        self.assertEqual("reviewed_usb_pack_handover_dpm_brownout_and_source_loss", self.manifest["status"])
        self.assertGreater(summary["transition_cases"], 1000)
        self.assertEqual(summary["transition_cases"], summary["passed_cases"])
        self.assertEqual(0, summary["failed_cases"])
        self.assertEqual(0, summary["unsafe_admissions"])
        self.assertEqual(0, summary["automatic_restarts"])

    def test_exact_nvdc_topology_and_protected_config_are_bound(self):
        self.assertTrue(all(self.manifest["topology_checks"].values()))
        self.assertTrue(all(self.manifest["configuration_checks"].values()))
        config = self.manifest["configuration"]
        self.assertFalse(config["reverse_power_modes"]["en_otg"])
        self.assertFalse(config["reverse_power_modes"]["en_backup"])
        self.assertEqual(7.0, config["minimum_system_voltage_v"])

    def test_dpm_and_source_loss_have_explicit_safe_outcomes(self):
        summary = self.manifest["summary"]
        self.assertGreater(summary["dpm_cases"], 0)
        self.assertGreater(summary["usb_detach_to_pack_cases"], 0)
        self.assertGreater(summary["pack_loss_cases"], 0)
        self.assertGreater(summary["usb_only_source_loss_cases"], 0)
        self.assertEqual(6, summary["brownout_cases"])

    def test_physical_waveforms_are_not_claimed_analytically(self):
        boundary = self.manifest["proof_boundary"]
        self.assertIn("absolute SYS droop", boundary["not_claimed"])
        self.assertIn("H8", boundary["h8_acceptance"])
        self.assertGreater(len(self.manifest["physical_residuals"]), 0)

    def test_authorization_stops_before_layout_or_order(self):
        authorization = self.manifest["authorization"]
        self.assertFalse(authorization["pcb_placement_or_routing"])
        self.assertFalse(authorization["purchasing"])
        self.assertFalse(authorization["fabrication"])


if __name__ == "__main__":
    unittest.main()
