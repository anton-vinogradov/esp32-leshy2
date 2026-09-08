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
        self.assertEqual({str(path.relative_to(ROOT)) for path in audit.net_binding_source_paths(ROOT)},
                         set(bindings["source_hashes"]))
        self.assertIn("hardware/ecad/kicad/LESHY2-UI-R2/UI_20_C5_WIFI_IR_SERVICE.kicad_sch",
                      bindings["source_hashes"])

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
            original_loads = json.loads
            source_text = audit.NET_BINDINGS.read_text()
            def modified_binding_only(text, *args, **kwargs):
                return artifact if text == source_text else original_loads(text, *args, **kwargs)
            with self.subTest(case=case), patch.object(audit.json, "loads", side_effect=modified_binding_only):
                with self.assertRaises(ValueError):
                    audit.checked_net_bindings()


class SilkscreenGeometryTests(unittest.TestCase):
    def test_close_mask_without_bbox_overlap_is_not_silently_passed(self):
        row = actual()
        obstacle = {"kind": "front_pad_mask_bbox", "pad": "SW8.5",
                    "bbox_mm": {"x": [5, 7], "y": [12.85, 14]}}
        self.assertFalse(audit.overlaps(row["bbox_mm"], obstacle["bbox_mm"]))
        candidates, _ = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertEqual(1, len(candidates))  # .05-mm conservative gap needs native refinement.

    def test_exact_mask_measurement_requires_fresh_geometry_and_minimum_gap(self):
        row = actual()
        obstacle = {"kind": "front_pad_mask_bbox", "pad": "SW8.5", "bbox_mm": row["bbox_mm"]}
        proof = {"status": "measured", "method": "native_stroke_shape_to_pad_mask",
                 "gap_lower_mm": .239819, "gap_upper_mm": .239820,
                 "inputs_sha256": audit.clearance_witness(row, obstacle)}
        obstacle["native_text_clearances"] = {row["id"]: proof}
        candidates, resolved = audit.geometry_candidates([row], [obstacle], 80, 150)
        self.assertEqual([], candidates)
        self.assertEqual(1, len(resolved))
        for field, value in (("status", "unsupported"), ("inputs_sha256", "stale"),
                             ("method", "bbox"), ("gap_lower_mm", .039819),
                             ("gap_lower_mm", float("nan")), ("gap_lower_mm", True),
                             ("gap_upper_mm", .3)):
            bad = copy.deepcopy(obstacle)
            bad["native_text_clearances"][row["id"]][field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(1, len(audit.geometry_candidates([row], [bad], 80, 150)[0]))
        for key, value in (("at_mm", [6.1, 12]), ("size_mm", [1.1, 1.0]),
                           ("thickness_mm", .16), ("angle_deg", 1), ("text", "OTHER")):
            bad = dict(row, **{key: value})
            with self.subTest(stale_text=key):
                self.assertIsNone(audit.checked_mask_clearance(bad, obstacle))
        bad = copy.deepcopy(obstacle)
        bad["bbox_mm"]["x"][1] += .1
        self.assertIsNone(audit.checked_mask_clearance(row, bad))

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
    def microphone_and_owner(self, at=(6, 114.95)):
        import pcbnew
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(audit.MIC_LIBRARY.parent), audit.MIC_LIBRARY.stem)
        fp.SetFPID(pcbnew.LIB_ID("Leshy2", audit.MIC_LIBRARY.stem))
        fp.SetReference("MK1")
        fp.SetValue("Same Sky CMEJ-0413-42-SMT-TR")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(8), pcbnew.FromMM(112)))
        fp.SetOrientationDegrees(180)
        text = pcbnew.PCB_TEXT(board)
        text.SetText("RF RP")
        text.SetLayer(pcbnew.F_SilkS)
        text.SetPosition(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in at)))
        text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
        text.SetTextThickness(pcbnew.FromMM(.15))
        board.Add(text)
        return board, fp, text

    def test_primary_maximum_circle_and_actual_strokes_resolve_only_clear_text(self):
        import pcbnew
        for at, clear in (((6, 114.95), True), ((6, 109.3), True), ((6, 114.2), False), ((8, 112), False)):
            board, fp, text = self.microphone_and_owner(at)
            if at == (6, 109.3):
                text.SetText("RST")
            snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            obstacle = next(o for o in snapshot["obstacles"] if o["kind"] == "front_courtyard_bbox")
            proof = audit.checked_circle_clearance(snapshot["texts"][0], obstacle)
            self.assertIsNotNone(proof)
            self.assertEqual(2.1, obstacle["reviewed_circle_body"]["radius_max_mm"])
            candidates, resolved = audit.geometry_candidates(snapshot["texts"], snapshot["obstacles"], 80, 150)
            with self.subTest(at=at):
                if clear:
                    self.assertGreaterEqual(proof["gap_lower_mm"], .15)
                    self.assertFalse(any(r["kind"] == "front_courtyard_bbox" for r in candidates))
                    self.assertTrue(any("native_maximum_body_gap_mm" in r for r in resolved))
                else:
                    self.assertEqual(0, proof["gap_lower_mm"])
                    self.assertIn("front_courtyard_bbox", {r["kind"] for r in candidates})
        # Required BOOT text remains separate and closer to the same owner axis.
        board, fp, owner = self.microphone_and_owner()
        action = pcbnew.PCB_TEXT(board)
        action.SetText("BOOT")
        action.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6), pcbnew.FromMM(116.3)))
        action.SetTextSize(owner.GetTextSize())
        action.SetTextThickness(owner.GetTextThickness())
        self.assertFalse(owner.GetEffectiveTextShape().Collide(action.GetEffectiveTextShape(), pcbnew.FromMM(.199)))

    def test_circle_refinement_is_bound_to_current_geometry_identity_and_primary(self):
        import pcbnew
        board, fp, text = self.microphone_and_owner()
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        obstacle = next(o for o in snapshot["obstacles"] if o["kind"] == "front_courtyard_bbox")
        for key, value in (("radius_max_mm", 2.0), ("centre_mm", [8, 112.1]),
                           ("primary_url", "unreviewed"), ("native_geometry_matches_library", False)):
            bad = copy.deepcopy(obstacle)
            bad["reviewed_circle_body"][key] = value
            self.assertIsNone(audit.checked_circle_clearance(snapshot["texts"][0], bad))
        moved_text = copy.deepcopy(snapshot["texts"][0])
        moved_text["at_mm"][1] -= .1
        self.assertIsNone(audit.checked_circle_clearance(moved_text, obstacle))
        fab = next(g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab)
        fab.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(5.9), pcbnew.FromMM(112)))
        changed = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        self.assertNotIn("reviewed_circle_body", next(o for o in changed["obstacles"] if o["kind"] == "front_courtyard_bbox"))
        self.assertIn("front_courtyard_bbox", {r["kind"] for r in audit.geometry_candidates(changed["texts"], changed["obstacles"], 80, 150)[0]})
        for identity in ("different MPN", "CMEJ-0413-42-SMT-TR"):
            board, fp, text = self.microphone_and_owner()
            fp.SetValue(identity)
            changed = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            self.assertNotIn("reviewed_circle_body", next(o for o in changed["obstacles"] if o["kind"] == "front_courtyard_bbox"))

    def test_circular_body_rotation_translation_and_front_back_are_native(self):
        import pcbnew
        for angle in (0, 90, 180, 270):
            board, fp, text = self.microphone_and_owner()
            fp.SetOrientationDegrees(angle)
            fp.Move(pcbnew.VECTOR2I(pcbnew.FromMM(3), pcbnew.FromMM(-2)))
            snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            obstacle = next(o for o in snapshot["obstacles"] if o["kind"] == "front_courtyard_bbox")
            self.assertEqual([11, 110], obstacle["reviewed_circle_body"]["centre_mm"])
            fp.Flip(fp.GetPosition(), False)
            snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            self.assertFalse(any("reviewed_circle_body" in o for o in snapshot["obstacles"]))

    def test_actual_text_pair_gap_cannot_be_reused_for_changed_text_or_pose(self):
        import pcbnew
        board, fp, owner = self.microphone_and_owner()
        action = pcbnew.PCB_TEXT(board)
        action.SetText("BOOT")
        action.SetLayer(pcbnew.F_SilkS)
        action.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6), pcbnew.FromMM(116.3)))
        action.SetTextSize(owner.GetTextSize())
        action.SetTextThickness(owner.GetTextThickness())
        board.Add(action)
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        def check(value):
            return audit.geometry_candidates(value["texts"], [], 80, 150,
                                             text_pair_clearances=value.get("native_text_pair_clearances"))
        candidates, resolved = check(snapshot)
        self.assertEqual([], candidates)
        self.assertEqual(1, len(resolved))
        self.assertGreaterEqual(resolved[0]["native_text_gap_mm"][0], .199999)
        for field, value in (("at_mm", [6, 114.96]), ("text", "WRONG"), ("thickness_mm", .2)):
            bad = copy.deepcopy(snapshot)
            bad["texts"][0][field] = value
            self.assertEqual(1, len(check(bad)[0]))
        bad = copy.deepcopy(snapshot)
        bad.pop("native_text_pair_clearances")
        self.assertEqual(1, len(check(bad)[0]))
        action.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6), pcbnew.FromMM(116.1)))
        negative = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        self.assertEqual(1, len(check(negative)[0]))

    def b3s_and_hub_text(self, y=138):
        import pcbnew
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(audit.B3S_LIBRARY.parent), "B3S-1100P")
        fp.SetFPID(pcbnew.LIB_ID("Leshy2_R2", "B3S-1100P"))
        fp.SetReference("SW8")
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(14.3), pcbnew.FromMM(133.32)))
        text = pcbnew.PCB_TEXT(board)
        text.SetText("HUB RP")
        text.SetLayer(pcbnew.F_SilkS)
        text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(14.87), pcbnew.FromMM(y)))
        text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
        text.SetTextThickness(pcbnew.FromMM(.15))
        board.Add(text)
        return board, fp, text

    def test_hub_ground_pad_native_strokes_old_gap_fails_shared_new_row_passes(self):
        import pcbnew
        board, fp, text = self.b3s_and_hub_text()
        pad = next(p for p in fp.Pads() if p.GetNumber() == "5")
        for y, expected_gap, count in ((138, .039819, 1), (138.2, .239819, 0)):
            text.SetPosition(pcbnew.VECTOR2I(text.GetPosition().x, pcbnew.FromMM(y)))
            proof = audit.native_stroke_mask_clearance(text, pad, pcbnew)
            self.assertEqual("measured", proof["status"])
            self.assertAlmostEqual(expected_gap, proof["gap_lower_mm"], places=6)
            snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            candidates, resolved = audit.geometry_candidates(snapshot["texts"], snapshot["obstacles"], 80, 150)
            self.assertEqual(count, len(candidates))
            self.assertTrue(any(r["kind"] == "front_courtyard_bbox" and "resolution_reason" in r for r in resolved))
            if count == 0:
                mask = next(r for r in resolved if r["kind"] == "front_pad_mask_bbox")
                self.assertGreaterEqual(mask["native_mask_gap_mm"][0], .15)
        pad.SetLocalSolderMaskMargin(pcbnew.FromMM(.1))
        self.assertAlmostEqual(.139819, audit.native_stroke_mask_clearance(text, pad, pcbnew)["gap_lower_mm"], places=6)

    def test_unsupported_mask_shapes_and_negative_expansion_keep_candidate(self):
        import pcbnew
        board, fp, text = self.b3s_and_hub_text(138.2)
        pad = next(p for p in fp.Pads() if p.GetNumber() == "5")
        pad.SetShape(pcbnew.PAD_SHAPE_TRAPEZOID)
        self.assertEqual("unsupported", audit.native_stroke_mask_clearance(text, pad, pcbnew)["status"])
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetLocalSolderMaskMargin(pcbnew.FromMM(-.01))
        self.assertEqual("unsupported", audit.native_stroke_mask_clearance(text, pad, pcbnew)["status"])
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        candidates, _ = audit.geometry_candidates(snapshot["texts"], snapshot["obstacles"], 80, 150)
        self.assertIn("front_pad_mask_bbox", {r["kind"] for r in candidates})

    def test_b3s_resolution_rejects_stale_library_native_fab_or_snapshot_geometry(self):
        import pcbnew
        board, fp, text = self.b3s_and_hub_text(138.2)
        snapshot = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        obstacle = next(o for o in snapshot["obstacles"] if o["kind"] == "front_courtyard_bbox")
        self.assertIn("reviewed_body", obstacle)
        bad = copy.deepcopy(obstacle)
        bad["fab_graphics_bbox_mm"]["y"][1] += .1
        self.assertIsNone(audit.reviewed_body_clearance(snapshot["texts"][0], bad))
        with patch.object(audit, "B3S_LIBRARY_SHA256", "0" * 64):
            stale = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
            self.assertNotIn("reviewed_body", next(o for o in stale["obstacles"] if o["kind"] == "front_courtyard_bbox"))
        rect = next(g for g in fp.GraphicalItems() if isinstance(g, pcbnew.PCB_SHAPE)
                    and g.GetLayer() == pcbnew.F_Fab and g.GetShape() == pcbnew.SHAPE_T_RECT)
        rect.SetEnd(pcbnew.VECTOR2I(rect.GetEnd().x, rect.GetEnd().y + pcbnew.FromMM(.1)))
        stale = audit.native_snapshot(board, "LESHY2-RF-R2", [], {}, pcbnew)
        self.assertNotIn("reviewed_body", next(o for o in stale["obstacles"] if o["kind"] == "front_courtyard_bbox"))
        found, _ = audit.geometry_candidates(stale["texts"], stale["obstacles"], 80, 150)
        self.assertIn("front_courtyard_bbox", {r["kind"] for r in found})

    def test_b3s_labels_use_native_rotation_and_flip_not_contract_pose(self):
        import pcbnew
        from h6_r2_user_silkscreen import b3s_actuator_axis
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty"), "B3S-1100P")
        fp.SetFPID(pcbnew.LIB_ID("Leshy2_R2", "B3S-1100P"))
        fp.SetReference("SW4")
        board.Add(fp)
        anchor = pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20))
        fp.SetPosition(anchor)
        ledger = [{"project": "LESHY2-RF-R2", "instance": "ptt_switch", "reference": "SW4"}]
        for flipped in (False, True):
            if flipped:
                fp.Flip(anchor, False)
            for angle in (0, 90, 180, 270):
                fp.SetOrientationDegrees(angle)
                row = audit.native_snapshot(board, "LESHY2-RF-R2", ledger, {}, pcbnew)["placements"][0]
                self.assertEqual("B.Cu" if flipped else "F.Cu", row["side"])
                self.assertAlmostEqual(angle % 360, row["rotation_deg"] % 360)
                # Independent native point: midpoint of the two same-X contacts
                # then translate half the two contact-column separation to X=0.
                pads = {p.GetNumber(): p.GetPosition() for p in fp.Pads()}
                actual_axis = tuple(sum(pcbnew.ToMM(getattr(pads[n], axis)) for n in ("1", "2", "3", "4")) / 4
                                    for axis in ("x", "y"))
                for actual, expected_axis in zip(b3s_actuator_axis(row), actual_axis):
                    self.assertAlmostEqual(expected_axis, actual, places=6)

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
