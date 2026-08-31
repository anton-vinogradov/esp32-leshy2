#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h4_r2_contract_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("h4_r2_contract_reconciliation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H4R2ContractReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.reconciliation, self.joined = MODULE.build()

    def test_hardware_contract_and_imports_are_structurally_equal(self):
        self.assertTrue(all(self.reconciliation["checks"].values()))
        self.assertEqual(0, self.reconciliation["summary"]["structural_check_failures"])
        self.assertEqual(6, self.reconciliation["summary"]["domains"])

    def test_current_generated_bsp_gap_is_exact_and_owned(self):
        summary = self.reconciliation["summary"]
        self.assertEqual((173, 135, 38), (summary["hardware_pin_rows"], summary["generated_bsp_pin_rows"], summary["missing_generated_bsp_rows"]))
        self.assertEqual(["c5", "pack", "safety"], [row["domain"] for row in self.reconciliation["corrections_required"]])
        self.assertEqual(0, self.joined["summary"]["unowned_contradictions"])

    def test_obligations_and_release_boundary_remain_open(self):
        self.assertEqual(1, self.joined["summary"]["retained_firmware_obligations"])
        self.assertEqual(51, self.joined["summary"]["physical_residuals_carried"])
        self.assertEqual("H4-R2.2", self.joined["next"]["marker"])
        self.assertFalse(any(self.joined["authorization"].values()))

    def test_generated_outputs_are_current(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
