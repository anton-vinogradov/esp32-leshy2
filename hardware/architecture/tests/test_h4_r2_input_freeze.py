#!/usr/bin/env python3

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "hardware/verification/h4_r2_input_freeze.py"
SPEC = importlib.util.spec_from_file_location("h4_r2_input_freeze", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H4R2InputFreezeTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.manifest = MODULE.build()

    def test_joined_input_set_is_complete_and_hash_bound(self):
        self.assertEqual("reviewed", self.manifest["status"])
        self.assertEqual(24, self.manifest["summary"]["total_inputs"])
        self.assertEqual(0, self.manifest["summary"]["cross_repository_h3_hash_mismatches"])
        self.assertTrue(all(self.manifest["checks"].values()))

    def test_open_work_is_preserved(self):
        self.assertEqual(51, self.manifest["summary"]["physical_residuals_carried"])
        self.assertEqual(1, self.manifest["summary"]["firmware_obligations_carried"])
        self.assertEqual("H4-R2.0.2", self.manifest["next"]["marker"])

    def test_generated_files_are_current_and_not_release_authority(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)
        machine = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertFalse(machine["authorization"]["component_purchase"])
        self.assertFalse(machine["authorization"]["pcb_placement_and_routing"])
        self.assertFalse(machine["authorization"]["fabrication"])


if __name__ == "__main__":
    unittest.main()
