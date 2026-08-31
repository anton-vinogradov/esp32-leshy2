#!/usr/bin/env python3

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "hardware/verification/h3_r2_rf_coexistence.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_rf_coexistence", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2RfCoexistenceTest(unittest.TestCase):
    def setUp(self):
        self.outputs, self.result = MODULE.build()

    def test_review_closes_all_calculable_rf_checks(self):
        self.assertEqual("H3-R2.5", self.result["marker"])
        self.assertEqual("pass", self.result["status"])
        self.assertGreaterEqual(self.result["summary"]["checks"], 50)
        self.assertTrue(all(self.result["checks"].values()))
        self.assertEqual([], self.result["errors"])

    def test_geometry_and_cable_contract_are_exact(self):
        summary = self.result["summary"]
        self.assertEqual((10, 5, 5), (summary["external_ports"], summary["front_ports"], summary["rear_ports"]))
        self.assertEqual(5, summary["microcoaxes"])
        self.assertGreaterEqual(summary["minimum_conservative_microcoax_slack_mm"], 5)
        lengths = [row["length_mm"] for row in self.result["microcoax"]["paths"]]
        self.assertEqual(2, lengths.count(30.0))
        self.assertEqual(3, lengths.count(60.0))

    def test_quiet_and_three_nrf_contracts_are_complete(self):
        summary = self.result["summary"]
        self.assertEqual(9, summary["active_signal_groups"])
        self.assertEqual(13, summary["quiet_contracts"])
        self.assertEqual(4, summary["nrf_role_modes"])
        self.assertEqual(8, summary["nrf_identity_permutations"])
        self.assertEqual(["nrf0", "nrf1", "nrf2"], self.result["nrf_concurrency"]["members"])

    def test_generated_files_are_current(self):
        for path, expected in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(expected, path.read_text(encoding="utf-8"), path)
        machine = json.loads(MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertFalse(machine["authorization"]["kicad_routing_or_fabrication"])
        self.assertFalse(machine["authorization"]["final_rf_performance_claim"])


if __name__ == "__main__":
    unittest.main()
