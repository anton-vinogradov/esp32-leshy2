#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h4_r2_acceptance.py"
SPEC = importlib.util.spec_from_file_location("h4_r2_acceptance", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H4R2AcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.result = MODULE.build()

    def test_joined_gate_is_complete(self):
        reviewed = self.result["result"]
        self.assertEqual((24, 6, 173, 173, 80, 12), (reviewed["joined_inputs"], reviewed["compute_domains"], reviewed["h2_controller_rows"], reviewed["generated_bsp_rows"], reviewed["m1_contacts"], reviewed["qualified_target_configurations"]))
        self.assertEqual(0, reviewed["cross_domain_contradictions_remaining"])
        self.assertEqual(0, reviewed["open_analytical_findings"])
        self.assertTrue(all(self.result["checks"].values()))

    def test_residuals_are_transferred_not_closed(self):
        reviewed = self.result["result"]
        self.assertEqual(51, reviewed["physical_residuals_transferred"])
        self.assertEqual({"H5": 1, "H6": 5, "H8": 46}, reviewed["physical_residuals_by_stage"])
        self.assertEqual(1, reviewed["firmware_obligations_transferred"])
        self.assertFalse(self.result["claims"]["physical_hardware_proven"])

    def test_release_authority_is_not_created(self):
        claims = self.result["claims"]
        self.assertFalse(claims["component_purchase_authorized"])
        self.assertFalse(claims["pcb_placement_and_routing_authorized"])
        self.assertFalse(claims["fabrication_authorized"])
        self.assertEqual(("H5", "H5.0.3-R1"), (self.result["next"]["stage"], self.result["next"]["marker"]))

    def test_generated_outputs_are_current(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
