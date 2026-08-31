#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h4_r2_correction_closure.py"
SPEC = importlib.util.spec_from_file_location("h4_r2_correction_closure", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H4R2CorrectionClosureTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.result = MODULE.build()

    def test_every_h2_controller_row_is_generated_exactly(self):
        summary = self.result["summary"]
        self.assertEqual((173, 173, 38), (summary["h2_controller_rows"], summary["generated_bsp_rows"], summary["restored_rows"]))
        self.assertEqual(6, summary["exact_domains"])
        self.assertEqual(0, summary["remaining_contradictions"])
        self.assertTrue(all(row["exact"] for row in self.result["domain_coverage"]))

    def test_corrected_bsp_was_built_for_every_target_configuration(self):
        summary = self.result["summary"]
        self.assertEqual((12, 60, 16, 16, 0), (summary["qualified_configurations"], summary["verified_artifacts"], summary["verified_maps"], summary["passed_size_gates"], summary["build_warnings"]))
        self.assertTrue(all(self.result["target_fail_closed_guards"].values()))
        self.assertTrue(all(self.result["checks"].values()))

    def test_open_work_and_release_boundary_are_preserved(self):
        self.assertEqual(1, self.result["summary"]["retained_firmware_obligations"])
        self.assertEqual(51, self.result["summary"]["physical_residuals_carried"])
        self.assertEqual("H4-R2.3", self.result["next"]["marker"])
        self.assertFalse(any(self.result["authorization"].values()))

    def test_generated_outputs_are_current(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
