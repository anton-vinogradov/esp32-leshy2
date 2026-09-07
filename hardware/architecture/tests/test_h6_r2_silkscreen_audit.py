"""Negative coverage for the native free-board user-silkscreen audit."""

import importlib.util
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_silkscreen_audit as audit


def expected(text="BOOT", at=(6, 12)):
    return {"instance": "s3_boot_button", "reference": "SW1", "text": text,
            "at_mm": list(at), "size_mm": 1.0, "thickness_mm": 0.15,
            "layer": "F.Silkscreen", "role": "user"}


def actual(text="BOOT", at=(6, 12), identity="text-1"):
    return {"id": identity, "text": text, "layer": "F.Silkscreen", "at_mm": list(at),
            "size_mm": [1.0, 1.0], "thickness_mm": 0.15, "angle_deg": 0,
            "visible": True, "mirrored": False, "horizontal_justify": 0, "vertical_justify": 0,
            "bbox_mm": {"x": [at[0] - 2, at[0] + 2], "y": [at[1] - .8, at[1] + .8]}}


class SilkscreenContractTests(unittest.TestCase):
    def test_correct_native_properties_match(self):
        errors, matches = audit.required_label_findings([expected()], [actual()])
        self.assertEqual([], errors)
        self.assertEqual("text-1", matches[0]["actual_id"])

    def test_missing_or_duplicate_native_label_fails(self):
        errors, _ = audit.required_label_findings([expected()], [])
        self.assertEqual("missing_required_label", errors[0]["kind"])
        errors, _ = audit.required_label_findings([expected()], [actual(), actual(identity="duplicate")])
        self.assertEqual("duplicate_required_label", errors[0]["kind"])

    def test_wrong_text_pose_layer_and_render_attributes_fail(self):
        for field, value, error_field in (
            ("text", "BOT", "text"), ("at_mm", [6, 13], "at_mm"),
            ("layer", "B.Silkscreen", "layer"), ("size_mm", [1.0, .8], "size_mm"),
            ("size_mm", [1.2, 1.2], "size_mm"), ("thickness_mm", .1, "thickness_mm"),
            ("angle_deg", 90, "angle_deg"), ("mirrored", True, "mirror_or_visibility"),
            ("visible", False, "mirror_or_visibility"), ("horizontal_justify", 1, "justification"),
        ):
            with self.subTest(field=field, value=value):
                row = actual()
                row[field] = value
                errors, _ = audit.required_label_findings([expected()], [row])
                self.assertIn(error_field, errors[0]["fields"])

    def test_repeated_boot_labels_use_different_native_text_objects(self):
        required = [expected(at=(6, 12)), expected(at=(74, 12))]
        native = [actual(at=(74, 12), identity="right"), actual(identity="left")]
        errors, matches = audit.required_label_findings(required, native)
        self.assertEqual([], errors)
        self.assertEqual(["left", "right"], [row["actual_id"] for row in matches])
        errors, _ = audit.required_label_findings(required, native[:1])
        self.assertTrue(errors)  # One BOOT cannot satisfy two banks.

    def test_geometry_is_candidate_review_not_false_scoped_pass(self):
        snapshot = {"project": "LESHY2-UI-R2", "placements": [], "texts": [actual()],
                    "obstacles": [{"kind": "front_courtyard_bbox", "reference": "SW3",
                                   "bbox_mm": {"x": [5, 7], "y": [11, 13]}}]}
        contract = {"board": {"width_mm": 80, "height_mm": 150, "corner_radius_mm": 2}}
        with patch.object(audit, "labels", return_value=[expected()]), \
                patch.object(audit, "antenna_signal_findings", return_value=[]):
            result = audit.audit_snapshot(snapshot, contract)
            self.assertEqual("review_required", result["status"])
            self.assertEqual([], result["errors"])
            self.assertEqual("front_courtyard_bbox", result["geometry_candidates"][0]["kind"])
            snapshot["texts"][0]["text"] = "WRONG"
            self.assertEqual("fail", audit.audit_snapshot(snapshot, contract)["status"])

    def test_changed_native_outline_cannot_pass_using_only_contract_dimensions(self):
        snapshot = {"project": "LESHY2-UI-R2", "placements": [], "texts": [actual()],
                    "obstacles": [], "native_outline_bbox_mm": {"x": [0, 75], "y": [0, 150]}}
        contract = {"board": {"width_mm": 80, "height_mm": 150, "corner_radius_mm": 2}}
        with patch.object(audit, "labels", return_value=[expected()]), \
                patch.object(audit, "antenna_signal_findings", return_value=[]):
            result = audit.audit_snapshot(snapshot, contract)
        self.assertEqual("fail", result["status"])
        self.assertEqual("native_outline_envelope_mismatch", result["errors"][0]["kind"])

    def test_missing_contract_antenna_and_its_label_do_not_reduce_audit_scope(self):
        contract = json.loads(audit.CONTRACT.read_text())
        del contract["antenna_ports"]["LESHY2-RF-R2"]["voice_external_sma"]
        snapshot = {"project": "LESHY2-RF-R2", "placements": [], "texts": [], "obstacles": []}
        bindings = audit.checked_net_bindings()["projects"][snapshot["project"]]["canonical_to_kicad"]
        result = audit.audit_snapshot(snapshot, contract, bindings)
        self.assertEqual("fail", result["status"])
        self.assertIn("antenna_scope_mismatch", {row["kind"] for row in result["errors"]})
        self.assertIn("required_label_binding_unavailable", {row["kind"] for row in result["errors"]})


class NetBindingAuthorityTests(unittest.TestCase):
    def test_current_authority_is_complete_and_hash_bound(self):
        bindings = audit.checked_net_bindings()
        self.assertEqual({"LESHY2-UI-R2", "LESHY2-RF-R2"}, set(bindings["projects"]))
        self.assertEqual(5, len(bindings["source_hashes"]))

    def test_stale_or_incomplete_authority_is_not_used(self):
        original = json.loads(audit.NET_BINDINGS.read_text())
        for case in ("status", "errors", "source", "stale", "project", "empty", "duplicate", "empty_net"):
            artifact = copy.deepcopy(original)
            if case == "status":
                artifact["status"] = "fail"
            elif case == "errors":
                artifact["errors"] = ["unresolved"]
            elif case == "source":
                artifact["source_hashes"].pop(next(iter(artifact["source_hashes"])))
            elif case == "stale":
                artifact["source_hashes"][next(iter(artifact["source_hashes"]))] = "0" * 64
            elif case == "project":
                del artifact["projects"]["LESHY2-RF-R2"]
            else:
                mapping = artifact["projects"]["LESHY2-RF-R2"]["canonical_to_kicad"]
                if case == "empty":
                    mapping.clear()
                elif case == "empty_net":
                    mapping[next(iter(mapping))] = ""
                else:
                    first, second = list(mapping)[:2]
                    mapping[second] = mapping[first]
            with self.subTest(case=case), patch.object(audit.json, "loads", return_value=artifact):
                with self.assertRaises(ValueError):
                    audit.checked_net_bindings()


class SilkscreenGeometryTests(unittest.TestCase):
    def test_courtyard_mask_drill_and_text_overlaps_are_reported(self):
        box = {"x": [5, 7], "y": [11, 13]}
        obstacles = [{"kind": kind, "bbox_mm": box} for kind in
                     ("front_courtyard_bbox", "front_pad_mask_bbox", "drill_bbox")]
        rows = [actual(), actual("RST", identity="other")]
        found, _ = audit.geometry_candidates(rows, obstacles, 80, 150)
        self.assertEqual({"front_courtyard_bbox", "front_pad_mask_bbox", "drill_bbox", "user_text_bbox_overlap"},
                         {row["kind"] for row in found})

    def test_assembly_exemption_does_not_waive_mask_drill_or_label_overlap(self):
        rows = [actual("DISPLAY · FPC ↑"), actual("SECOND", identity="second")]
        box = {"x": [5, 7], "y": [11, 13]}
        obstacles = [{"kind": kind, "bbox_mm": box} for kind in
                     ("display_panel_bbox", "front_pad_mask_bbox", "drill_bbox")]
        candidates, exemptions = audit.geometry_candidates(rows, obstacles, 80, 150,
                                                           assembly_texts={"DISPLAY · FPC ↑": [6, 12]})
        self.assertEqual(1, len(exemptions))
        self.assertEqual("display_panel_bbox", exemptions[0]["kind"])
        self.assertIn("drill_bbox", {row["kind"] for row in candidates})
        self.assertIn("front_pad_mask_bbox", {row["kind"] for row in candidates})
        self.assertIn("user_text_bbox_overlap", {row["kind"] for row in candidates})

    def test_wrongly_positioned_assembly_text_is_not_exempt(self):
        row = actual("DISPLAY · FPC ↑", at=(6, 12))
        candidates, exemptions = audit.geometry_candidates([row], [
            {"kind": "display_panel_bbox", "bbox_mm": row["bbox_mm"]}], 80, 150,
            assembly_texts={"DISPLAY · FPC ↑": [40, 21]})
        self.assertEqual([], exemptions)
        self.assertEqual("display_panel_bbox", candidates[0]["kind"])

    def test_tented_via_is_recorded_not_claimed_as_open_mask(self):
        row = actual()
        obstacle = {"kind": "via_drill_bbox", "front_tented": True, "bbox_mm": row["bbox_mm"]}
        candidates, exemptions = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertEqual([], candidates)
        self.assertEqual(1, len(exemptions))
        obstacle["front_tented"] = False
        candidates, exemptions = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertEqual([], exemptions)
        self.assertEqual("via_drill_bbox", candidates[0]["kind"])

    def test_courtyard_candidate_retains_distinction_from_fab_graphics(self):
        row = actual()
        obstacle = {"kind": "front_courtyard_bbox", "bbox_mm": row["bbox_mm"],
                    "fab_graphics_bbox_mm": {"x": [5, 7], "y": [13, 15]}}
        candidates, _ = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertFalse(candidates[0]["fab_graphics_bbox_overlap"])
        self.assertAlmostEqual(.2, candidates[0]["fab_graphics_bbox_gap_mm"])
        obstacle["fab_graphics_bbox_mm"] = row["bbox_mm"]
        candidates, _ = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertTrue(candidates[0]["fab_graphics_bbox_overlap"])

    def test_hidden_or_back_free_text_does_not_create_front_geometry_candidates(self):
        hidden, back = actual(), actual(identity="back")
        hidden["visible"], back["layer"] = False, "B.Silkscreen"
        candidates, _ = audit.geometry_candidates([hidden, back], [], 80, 150)
        self.assertEqual([], candidates)

    def test_full_text_box_not_anchor_must_fit_rounded_board(self):
        self.assertTrue(audit.within_outline({"x": [3, 5], "y": [3, 5]}, 80, 150, 2))
        self.assertFalse(audit.within_outline({"x": [-.1, 5], "y": [3, 5]}, 80, 150, 2))
        self.assertFalse(audit.within_outline({"x": [.1, 1], "y": [.1, 1]}, 80, 150, 2))
        row = actual(at=(.5, .5))
        candidates, _ = audit.geometry_candidates([row], [], 80, 150, 2)
        self.assertEqual("outer_outline_bbox", candidates[0]["kind"])

    def test_undersized_nonrequired_user_label_is_not_ignored(self):
        row = actual("ANY OTHER USER TEXT")
        row["thickness_mm"] = .1
        candidates, _ = audit.geometry_candidates([row], [], 80, 150)
        self.assertEqual("small_free_user_text", candidates[0]["kind"])


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Native extraction tests require KiCad Python")
class NativeSilkscreenExtractionTests(unittest.TestCase):
    def test_wrong_hierarchy_with_correct_leaf_name_fails_from_real_pad(self):
        import pcbnew
        project = "LESHY2-RF-R2"
        contract = json.loads(audit.CONTRACT.read_text())
        ledger = json.loads(audit.LEDGER.read_text())["rows"]
        bindings = audit.checked_net_bindings()["projects"][project]["canonical_to_kicad"]
        board = pcbnew.LoadBoard(str(ROOT / contract["boards"][project]["output"]))
        reference = next(row["reference"] for row in ledger
                         if row["project"] == project and row["instance"] == "voice_external_sma")
        footprint = next(fp for fp in board.GetFootprints() if fp.GetReference() == reference)
        pad = next(p for p in footprint.Pads() if p.GetNumber() == "1")
        wrong_name = "/WRONG/VOICE_U_EXTERNAL_RF_50R"
        wrong_net = pcbnew.NETINFO_ITEM(board, wrong_name)
        board.Add(wrong_net)
        pad.SetNet(wrong_net)
        snapshot = audit.native_snapshot(board, project, ledger, contract, pcbnew)
        row = next(row for row in snapshot["placements"] if row["instance"] == "voice_external_sma")
        self.assertEqual([wrong_name], row["signal_pad_nets"])
        result = audit.audit_snapshot(snapshot, contract, bindings)
        self.assertEqual("fail", result["status"])
        errors = [row for row in result["errors"] if row["kind"] == "antenna_signal_identity_mismatch"]
        self.assertEqual(1, len(errors))
        self.assertEqual([wrong_name], errors[0]["actual"])
        self.assertEqual(bindings["VOICE_U_EXTERNAL_RF_50R"], errors[0]["expected"])

    def test_native_object_properties_not_mockup_or_generated_audit(self):
        import pcbnew
        board = pcbnew.BOARD()
        text = pcbnew.PCB_TEXT(board)
        text.SetText("WRONG")
        text.SetLayer(pcbnew.B_SilkS)
        text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(7), pcbnew.FromMM(12)))
        text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8), pcbnew.FromMM(.8)))
        text.SetTextThickness(pcbnew.FromMM(.1))
        board.Add(text)
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        self.assertEqual("WRONG", snapshot["texts"][0]["text"])
        self.assertEqual([7, 12], snapshot["texts"][0]["at_mm"])
        errors, _ = audit.required_label_findings([expected()], snapshot["texts"])
        self.assertTrue(errors)
        text.SetText("BOOT")
        text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6), pcbnew.FromMM(12)))
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        errors, _ = audit.required_label_findings([expected()], snapshot["texts"])
        self.assertIn("layer", errors[0]["fields"])
        self.assertIn("size_mm", errors[0]["fields"])
        self.assertIn("thickness_mm", errors[0]["fields"])


if __name__ == "__main__":
    unittest.main()
