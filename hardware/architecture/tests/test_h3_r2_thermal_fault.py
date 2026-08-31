#!/usr/bin/env python3

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "hardware/verification/h3_r2_thermal_fault.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_thermal_fault", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2ThermalFaultTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.result = MODULE.build()

    def test_all_current_r2_checks_pass(self):
        self.assertEqual("H3-R2.6", self.result["marker"])
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(25, self.result["summary"]["checks"])
        self.assertTrue(all(self.result["checks"].values()))
        self.assertEqual([], self.result["errors"])

    def test_thermal_envelope_covers_every_profile(self):
        thermal = self.result["thermal"]
        self.assertEqual(56, len(thermal["profiles"]))
        self.assertEqual(28, self.result["summary"]["sustained_profiles"])
        self.assertEqual("SUPPORT_IDLE", thermal["worst_sustained_profile"]["support_profile"])
        self.assertEqual("SUPPORT_WORST", thermal["electrical_absolute_profile"]["support_profile"])
        self.assertLessEqual(max(row["external_5v_current_a"] for row in thermal["profiles"] if row["support_profile"] == "SUPPORT_IDLE"), 1.0)

    def test_single_fault_and_unattended_boundaries_are_explicit(self):
        faults = self.result["single_fault"]["faults"]
        self.assertEqual(30, len(faults))
        self.assertEqual({"contained", "detected_no_admission"}, {row["classification"] for row in faults})
        self.assertEqual(1760, max(row["maximum_analytical_detection_ms"] or 0 for row in faults))
        self.assertEqual("EVERY_48_H", self.result["unattended"]["full_fault_plane_proof"]["default"])
        self.assertTrue(self.result["unattended"]["runtime_claim"].startswith("none"))

    def test_generated_files_are_current_and_not_release_authority(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)
        machine = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertFalse(machine["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(machine["authorization"]["fabrication"])
        self.assertFalse(machine["authorization"]["final_product_claim"])


if __name__ == "__main__":
    unittest.main()
