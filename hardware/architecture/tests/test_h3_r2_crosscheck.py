#!/usr/bin/env python3

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "hardware/verification/h3_r2_crosscheck.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_crosscheck", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2CrosscheckTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.acceptance = MODULE.build()
        self.crosscheck = json.loads(self.outputs[MODULE.CROSSCHECK])
        self.residuals = json.loads(self.outputs[MODULE.RESIDUALS])

    def test_phase_closes_without_an_analytical_finding(self):
        self.assertEqual("reviewed", self.acceptance["status"])
        self.assertTrue(self.acceptance["result"]["analytical_scope_complete"])
        self.assertEqual(0, self.acceptance["result"]["open_analytical_findings"])
        self.assertEqual("H4-R2.0.1", self.acceptance["result"]["next_marker"])

    def test_all_current_artifacts_and_recorded_hashes_match(self):
        self.assertEqual(20, self.crosscheck["summary"]["current_artifacts"])
        self.assertGreater(self.crosscheck["summary"]["recorded_source_hashes_checked"], 50)
        self.assertEqual(0, self.crosscheck["summary"]["hash_mismatches"])
        self.assertTrue(all(self.crosscheck["checks"].values()))

    def test_every_remaining_physical_row_is_owned_but_open(self):
        registry = self.residuals["registry"]
        self.assertEqual(51, len(registry))
        self.assertTrue(all(row["status"] == "physical_evidence_required" for row in registry))
        self.assertTrue(all(set(row["closure_stages"]) <= {"H5", "H6", "H8"} for row in registry))
        self.assertEqual(0, self.residuals["summary"]["unassigned"])

    def test_firmware_obligation_is_not_hidden_in_physical_registry(self):
        obligations = self.crosscheck["firmware_obligations"]
        self.assertEqual(1, len(obligations))
        self.assertEqual("F5/F6", obligations[0]["owner"])
        self.assertNotIn(obligations[0]["obligation"], {row["residual"] for row in self.residuals["registry"]})

    def test_generated_files_are_current_and_not_release_authority(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)
        self.assertFalse(self.acceptance["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(self.acceptance["authorization"]["purchasing"])
        self.assertFalse(self.acceptance["authorization"]["fabrication"])


if __name__ == "__main__":
    unittest.main()
