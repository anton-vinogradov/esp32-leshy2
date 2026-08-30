import copy
import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_input_freeze.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_input_freeze", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2InputFreezeTest(unittest.TestCase):
    def test_current_freeze_covers_every_sheet_and_domain(self):
        result = MODULE.build()
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["errors"])
        self.assertEqual(23, result["summary"]["unique_matrix_sheets"])
        self.assertEqual(7, result["summary"]["workstream_count"])
        self.assertEqual(
            ["c5", "hub_rp", "pack", "rf_rp", "s3", "safety"],
            result["summary"]["covered_domains"],
        )
        self.assertFalse(result["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(result["authorization"]["purchasing"])
        self.assertFalse(result["authorization"]["fabrication"])

    def test_duplicate_or_missing_sheet_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["workstreams"][1]["sheets"].append(contract["workstreams"][0]["sheets"][0])
        result = MODULE.build(contract)
        self.assertEqual("fail", result["status"])
        self.assertIn("a native sheet has more than one primary H3 workstream", result["errors"])

    def test_reviewed_counts_cannot_be_relabeled(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["expected"]["canonical_nets"] += 1
        result = MODULE.build(contract)
        self.assertIn("reviewed H2-R2 counts differ from the H3 input-freeze contract", result["errors"])

    def test_checked_in_outputs_are_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render_json(result), MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, False), MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, True), MODULE.DOC_RU.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
