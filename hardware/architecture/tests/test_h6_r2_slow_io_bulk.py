"""Finite bulk ownership and BOTH supply pads; no analog qualification."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
EVIDENCE = ROOT / "hardware/layout/h6-r2-slow-io-bulk-review.json"


def selected_rules(contract):
    rows = [r for r in contract["placement_policy"]["critical_pad_pairs"]
            if r["first_instance"] == "slow_io_bulk_cap"]
    expected = {("1", "27"), ("1", "31")}
    actual = [(r.get("first_pad_number"), r.get("second_pad_number")) for r in rows]
    if len(rows) != 2 or set(actual) != expected:
        raise ValueError("both unique physical supply endpoints required")
    if any(r["project"] != "LESHY2-RF-R2" or r["second_instance"] != "slow_io"
           or r["canonical_net"] != "3V3_MAIN" or r["maximum_distance_mm"] != 7.5 for r in rows):
        raise ValueError("exact bulk endpoint net and limit required")
    return rows


class SlowIoBulkSourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text())
        self.evidence = json.loads(EVIDENCE.read_text())

    def test_exact_existing_part_is_internal_and_mechanically_locked(self):
        row = self.contract["placement_overrides"]["slow_io_bulk_cap"]
        self.assertEqual("rear-inner", row["frame"])
        self.assertEqual([61.275, 82.125], row["anchor_mm"])
        self.assertEqual(90, row["rotation_deg"])
        self.assertIs(row["mechanical_locked"], True)
        self.assertEqual("hardware/layout/h6-r2-slow-io-bulk-review.json", row["evidence"])
        self.assertEqual("C259", self.evidence["component"]["reference"])
        self.assertEqual("TDK C1608X7R1C105K080AC", self.evidence["component"]["mpn"])
        self.assertEqual("C230", self.evidence["required_joint_dependency"]["reference"])

    def test_owner_and_both_actual_pads_have_independent_limits(self):
        policy = self.contract["placement_policy"]
        self.assertEqual("slow_io", policy["locality_owner_overrides"]["slow_io_bulk_cap"])
        self.assertEqual(2.5, policy["locality_max_gap_mm"]["slow_io_bulk_cap"])
        self.assertEqual(2, len(selected_rules(self.contract)))

    def test_missing_duplicate_or_generic_shortest_pair_is_rejected(self):
        for mutation in ("missing", "duplicate", "generic"):
            bad = copy.deepcopy(self.contract)
            rows = bad["placement_policy"]["critical_pad_pairs"]
            mine = [r for r in rows if r["first_instance"] == "slow_io_bulk_cap"]
            if mutation == "missing":
                rows.remove(mine[1])
            elif mutation == "duplicate":
                mine[1]["second_pad_number"] = mine[0]["second_pad_number"]
            else:
                mine[1].pop("second_pad_number")
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "physical supply"):
                selected_rules(bad)

    def test_numerical_evidence_and_open_qualification_boundary(self):
        at = self.evidence["candidate"]["supply_pad_1_mm"]
        for pair in self.evidence["actual_supply_pairs"]:
            self.assertAlmostEqual(pair["candidate_mm"], math.dist(at, pair["second_pad_mm"]), places=5)
            self.assertLessEqual(pair["candidate_mm"], pair["maximum_mm"])
        self.assertIs(self.evidence["joint_native_DRC_pass_claimed"], False)
        self.assertIs(self.evidence["manufacturing_or_runtime_qualification_claimed"], False)
        self.assertEqual(2, len(self.evidence["unchanged_local_bypasses"]))
        self.assertEqual(0, self.evidence["native_silk_screen"]["violations"])


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Requires KiCad Python")
class SlowIoBulkActualPadTests(unittest.TestCase):
    def setUp(self):
        import pcbnew
        sys.path.insert(0, str(ROOT / "hardware/layout"))
        import h6_r2_placement
        self.pcbnew, self.producer = pcbnew, h6_r2_placement
        self.contract = json.loads(CONTRACT.read_text())
        self.contract["placement_policy"]["critical_pad_pairs"] = selected_rules(self.contract)
        self.board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb"))
        self.fps = {f.GetReference(): f for f in self.board.GetFootprints()}
        self.cap = self.fps["C259"]
        self.cap.SetOrientationDegrees(90)
        self.cap.SetPosition(pcbnew.VECTOR2I_MM(61.275, 82.125))
        self.bindings = json.loads((ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json").read_text())["projects"]["LESHY2-RF-R2"]["canonical_to_kicad"]

    def audit(self):
        entries = {"slow_io_bulk_cap": {"fp": self.cap, "row": {"reference": "C259"}},
                   "slow_io": {"fp": self.fps["U106"], "row": {"reference": "U106"}}}
        return self.producer.critical_pad_pair_audit("LESHY2-RF-R2", entries, self.contract, self.bindings)

    def test_real_candidate_pad_geometry_passes_both_powers(self):
        result = self.audit()
        self.assertEqual("pass", result["status"])
        self.assertEqual({"27", "31"}, {r["second_pad"] for r in result["rows"]})
        self.assertEqual([5.42, 7.355], [r["pad_centre_distance_mm"] for r in result["rows"]])

    def test_old_remote_pose_fails_both_endpoints(self):
        self.cap.SetOrientationDegrees(0)
        self.cap.SetPosition(self.pcbnew.VECTOR2I_MM(70.125, 59.875))
        self.assertEqual(2, self.audit()["violation_count"])

    def test_far_supply_drift_fails_even_when_near_supply_still_passes(self):
        self.cap.SetPosition(self.pcbnew.VECTOR2I_MM(61.775, 82.125))
        result = self.audit()
        self.assertEqual(1, result["violation_count"])
        self.assertEqual("31", result["violations"][0]["second_pad"])

    def test_wrong_pad_net_is_an_error_not_a_shortest_pair_fallback(self):
        pad = next(p for p in self.fps["U106"].Pads() if p.GetNumber() == "31")
        pad.SetNetCode(self.board.FindNet(self.bindings["POWER_GROUND"]).GetNetCode())
        self.assertEqual("fail", self.audit()["status"])
        self.assertTrue(self.audit()["errors"])

    def silk_collisions(self):
        p = self.pcbnew
        # Candidate fixture depends on the separately reviewed audio relocation.
        self.fps["C230"].SetOrientationDegrees(180)
        self.fps["C230"].SetPosition(p.VECTOR2I_MM(12, 93.65))
        strokes = []
        for fp in self.board.GetFootprints():
            for item in list(fp.GraphicalItems()) + list(fp.GetFields()):
                if item.GetLayer() == p.B_SilkS and (not hasattr(item, "IsVisible") or item.IsVisible()):
                    strokes.append((fp.GetReference(), item.GetEffectiveShape()))
        masks = [(fp.GetReference(), q.GetEffectiveShape(p.B_Cu), max(0, q.GetSolderMaskExpansion(p.B_Cu)))
                 for fp in self.board.GetFootprints() for q in fp.Pads() if q.IsOnLayer(p.B_Mask)]
        own = [shape for ref, shape in strokes if ref == "C259"]
        self.assertEqual(2, len(own))
        failures = []
        for shape in own:
            for ref, target in strokes:
                if ref != "C259" and shape.Collide(target, p.FromMM(.15)):
                    failures.append(("silk", ref))
            for ref, target, expansion in masks:
                if shape.Collide(target, p.FromMM(.15) + expansion):
                    failures.append(("mask", ref))
        for ref, shape in strokes:
            if ref != "C259":
                for owner, target, expansion in masks:
                    if owner == "C259" and shape.Collide(target, p.FromMM(.15) + expansion):
                        failures.append(("neighbor_silk", ref))
        return failures

    def test_actual_candidate_silk_and_mask_clearances_not_courtyard_proxy(self):
        self.assertEqual([], self.silk_collisions())

    def test_shift_into_R2_is_rejected_by_actual_silk_mask_geometry(self):
        self.cap.SetPosition(self.pcbnew.VECTOR2I_MM(59.865, 84.325))
        findings = self.silk_collisions()
        self.assertTrue(findings)
        self.assertTrue(any(ref == "R2" for _, ref in findings))


if __name__ == "__main__":
    unittest.main()
