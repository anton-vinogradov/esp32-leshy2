"""A newly frozen wrong coordinate must still fail the owner's product intent."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("placement_intent", ROOT / "hardware/layout/h6_r2_placement_intent.py")
INTENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTENT)


def fixture():
    def item(x, y, side="F.Cu", angle=0, actuator=None):
        return {"anchor_mm": [x, y], "side": side, "rotation_deg": angle,
                "actuator_mm": actuator, "pad1_nets": []}
    ui = {"J5": item(61.005, 140.075, "B.Cu", 180)}
    rf = {"BT1": item(40, 85, angle=90), "R33": item(30.45, 85), "R34": item(49.55, 85),
          "SW3": item(8, 80), "SW4": item(72.1, 67.42, actuator=[72.1, 66.5]),
          "U83": item(.8, 100, "B.Cu")}
    for board, ref, x in ((rf, "J1", 16.47), (rf, "J4", 37.47), (ui, "J9", 26.1), (ui, "J11", 14.87)):
        board[ref] = {**item(x, 146.325, "B.Cu", 180),
                      "footprint": "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
                      "value": "GCT USB4105-GF-A"}
    rf["BT1"]["fab_stroke_bounds_mm"] = [20.06, 46.42, 59.94, 123.58]
    rf["MK1"] = {**item(47, 147.4, side="B.Cu"),
                 "footprint": "Leshy2:CMEJ-0413-42-SMT-TR",
                 "value": "Same Sky CMEJ-0413-42-SMT-TR"}
    for board, refs in ((ui, ("J12", "J3", "J14", "J7", "J16")),
                        (rf, ("J9", "J8", "J5", "J6", "J7"))):
        for x, ref in zip((10.6, 25.3, 40, 54.7, 69.4), refs):
            board[ref] = item(x, 0, angle=180)
    rf["J6"]["pad1_nets"] = ["/RF_20_CC1101_VOICE_TX/VOICE_U_EXTERNAL_RF_50R"]
    rf["J7"]["pad1_nets"] = ["/RF_20_CC1101_VOICE_TX/VOICE_V_EXTERNAL_RF_50R"]
    for n, y in enumerate((22.5, 36, 49.5, 63)):
        ui[f"SW{9+n}"] = item(5.52, y, angle=90, actuator=[4.6, y])
        ui[f"SW{13+n}"] = item(74.48, y, angle=-90, actuator=[75.4, y])
    return {"boards": dict(zip(INTENT.PROJECTS, (ui, rf))),
            "microphone_labels": {INTENT.PROJECTS[0]: [mic_label()], INTENT.PROJECTS[1]: []},
            "bottom_edges": {INTENT.PROJECTS[0]: notch_edges()},
            "assembly_registration": {INTENT.PROJECTS[0]: {
                "status": "pass_scoped_native_registration", "required_count": 5, "observed_count": 5}}}


def mic_label():
    return {"text": "MIC", "at_mm": [33, 148.9], "layer": "F.Silkscreen",
            "size_mm": [1, 1], "thickness_mm": .15, "angle_deg": 0,
            "visible": True, "mirrored": False, "default_stroke_font": True,
            "bold": False, "italic": False, "horizontal_justify": 0, "vertical_justify": 0}


def notch_edges():
    # Accepted open route, independently listed; no placement generator import.
    return [
        ["line", [78, 150], [66.43, 150]],
        ["line", [66.43, 150], [66.43, 149.4]],
        ["arc", [66.43, 149.4], [66.254264, 148.975736], [65.83, 148.8]],
        ["line", [65.83, 148.8], [57.03, 148.8]],
        ["arc", [57.03, 148.8], [56.605736, 148.975736], [56.43, 149.4]],
        ["line", [56.43, 149.4], [56.43, 150]],
        ["line", [56.43, 150], [2, 150]],
    ]


class PlacementIntentTests(unittest.TestCase):
    def test_every_usb_identity_pose_and_presence_is_independently_required(self):
        for project, ref in ((0, "J9"), (0, "J11"), (1, "J1"), (1, "J4")):
            for mutation in ("missing", "mpn", "footprint", "x", "recess", "side", "rotation"):
                snapshot = fixture(); ports = snapshot["boards"][INTENT.PROJECTS[project]]
                if mutation == "missing":
                    del ports[ref]
                elif mutation == "mpn":
                    ports[ref]["value"] = "JAE DX07S016JA1R1500"
                elif mutation == "footprint":
                    ports[ref]["footprint"] = "Leshy2_R2:USB_C_Receptacle_JAE_DX07S016JA1R1500_EdgeSilk"
                elif mutation == "x":
                    ports[ref]["anchor_mm"][0] += 1
                elif mutation == "recess":
                    ports[ref]["anchor_mm"][1] -= .2
                elif mutation == "side":
                    ports[ref]["side"] = "F.Cu"
                else:
                    ports[ref]["rotation_deg"] = 0
                with self.subTest(project=project, ref=ref, mutation=mutation):
                    self.assertIn("four exact GCT USB ports inside the sandwich with uniform nominal flush mouths",
                                  INTENT.evaluate(snapshot)["failed_requirements"])

    def test_missing_real_speaker_body_is_not_covered_by_an_electrical_termination(self):
        snapshot = fixture()
        snapshot.pop("assembly_registration")
        self.assertTrue(any("speaker body" in name for name in INTENT.evaluate(snapshot)["failed_requirements"]))

    def test_independent_acceptable_layout(self):
        self.assertEqual("pass", INTENT.evaluate(fixture())["status"])

    def rejected(self, project, ref, key, value, phrase):
        snapshot = fixture()
        snapshot["boards"][INTENT.PROJECTS[project]][ref][key] = value
        result = INTENT.evaluate(snapshot)
        self.assertEqual("fail", result["status"])
        self.assertTrue(any(phrase in name for name in result["failed_requirements"]))

    def test_wrong_holder_freeze_does_not_waive_centering(self):
        self.rejected(1, "BT1", "anchor_mm", [42.99, 85], "holder centered")

    def test_holder_and_ntcs_cannot_move_together_away_from_accepted_y85(self):
        snapshot = fixture()
        for ref in ("BT1", "R33", "R34"):
            snapshot["boards"][INTENT.PROJECTS[1]][ref]["anchor_mm"][1] = 65
        snapshot["boards"][INTENT.PROJECTS[1]]["BT1"]["fab_stroke_bounds_mm"] = [20.06, 26.42, 59.94, 103.58]
        self.assertIn("holder centered on rear PCB, not shifted to clear another part",
                      INTENT.evaluate(snapshot)["failed_requirements"])

    def test_holder_body_must_share_its_accepted_y_not_only_width(self):
        self.rejected(1, "BT1", "fab_stroke_bounds_mm", [20.06, 26.42, 59.94, 103.58],
                      "real body")

    def test_reserve_is_not_rendered_as_the_real_holder(self):
        self.rejected(1, "BT1", "fab_stroke_bounds_mm", [20.1, 42, 59.9, 128], "86mm land reserve")

    def test_external_support_packing_shortcut_is_rejected(self):
        snapshot = fixture()
        snapshot["boards"][INTENT.PROJECTS[1]]["C144"] = {"side": "F.Cu"}
        self.assertIn("no ordinary RF support components moved outside merely to solve packing",
                      INTENT.evaluate(snapshot)["failed_requirements"])

    def test_ntc_must_follow_cell_not_old_holder_position(self):
        self.rejected(1, "R33", "anchor_mm", [33.44, 85], "NTCs")

    def test_wrong_encoder_side_not_fixed_by_mirroring_svg(self):
        self.rejected(1, "SW3", "anchor_mm", [71, 50.25], "encoder on LEFT")

    def test_encoder_height_is_not_a_frozen_accidental_coordinate(self):
        for y in (50.25, 75, 85):
            snapshot = fixture()
            snapshot["boards"][INTENT.PROJECTS[1]]["SW3"]["anchor_mm"][1] = y
            self.assertEqual("pass", INTENT.evaluate(snapshot)["status"])

    def test_ptt_should_not_be_mirrored_with_encoder(self):
        self.rejected(1, "SW4", "actuator_mm", [7.9, 66.5], "PTT on RIGHT")

    def test_ordinary_smt_is_not_permission_for_external_audio(self):
        self.rejected(1, "U83", "side", "F.Cu", "headset jack body BETWEEN")

    def test_microphone_requires_original_inner_lower_edge_intent_not_any_outward_pose(self):
        for mutation in ("missing", "old-F", "old-XY-inner", "F-bottom", "B-upper",
                         "wrong-X", "unknown-package", "wrong-part", "wrong-angle"):
            snapshot = fixture()
            rf = snapshot["boards"][INTENT.PROJECTS[1]]
            if mutation == "missing":
                del rf["MK1"]
            elif mutation == "old-F":
                rf["MK1"].update(side="F.Cu", anchor_mm=[8, 112], rotation_deg=180)
            elif mutation == "old-XY-inner":
                rf["MK1"]["anchor_mm"] = [8, 112]
            elif mutation == "F-bottom":
                rf["MK1"]["side"] = "F.Cu"
            elif mutation == "B-upper":
                rf["MK1"]["anchor_mm"][1] = 112
            elif mutation == "wrong-X":
                rf["MK1"]["anchor_mm"][0] = 33
            elif mutation == "unknown-package":
                rf["MK1"]["footprint"] = "Other:bottom-port"
            elif mutation == "wrong-part":
                rf["MK1"]["value"] = "Another same-size microphone"
            else:
                rf["MK1"]["rotation_deg"] = 180
            with self.subTest(mutation=mutation):
                self.assertIn("exact microphone inside RF at the lower-edge acoustic corridor",
                              INTENT.evaluate(snapshot)["failed_requirements"])

    def test_microphone_corridor_and_maximum_body_rim_are_independent_finite_bounds(self):
        for x in (46.75, 47, 47.25):
            for y in (147.1, 147.4, 147.6):
                snapshot = fixture()
                snapshot["boards"][INTENT.PROJECTS[1]]["MK1"]["anchor_mm"] = [x, y]
                snapshot["microphone_labels"][INTENT.PROJECTS[0]][0]["at_mm"][0] = 80-x
                with self.subTest(x=x, y=y):
                    self.assertEqual("pass", INTENT.evaluate(snapshot)["status"])
        for at in ([46.749, 147.4], [47.251, 147.4], [47, 147.099], [47, 147.601]):
            self.rejected(1, "MK1", "anchor_mm", at, "lower-edge acoustic corridor")

    def test_mic_label_is_exactly_one_front_readable_cross_board_annotation(self):
        expected = "one readable UI front MIC label follows the RF microphone through the assembly transform"
        for key, value in (("text", "MICROPHONE"), ("at_mm", [47, 148.9]),
                           ("at_mm", [33, 148.0]), ("layer", "B.Silkscreen"),
                           ("size_mm", [.9, 1]), ("size_mm", [1, 1.1]),
                           ("thickness_mm", .12), ("angle_deg", 180),
                           ("visible", False), ("mirrored", True), ("bold", True),
                           ("italic", True), ("default_stroke_font", False),
                           ("horizontal_justify", 1), ("vertical_justify", -1)):
            snapshot = fixture()
            snapshot["microphone_labels"][INTENT.PROJECTS[0]][0][key] = value
            with self.subTest(key=key, value=value):
                self.assertIn(expected, INTENT.evaluate(snapshot)["failed_requirements"])
        for mutation in ("missing", "duplicate", "extra-RF", "old-full-word"):
            snapshot = fixture()
            labels = snapshot["microphone_labels"][INTENT.PROJECTS[0]]
            if mutation == "missing": labels.clear()
            elif mutation == "duplicate": labels.append(copy.deepcopy(labels[0]))
            elif mutation == "extra-RF": snapshot["microphone_labels"][INTENT.PROJECTS[1]].append(mic_label())
            else: labels.append({**mic_label(), "text": "MICROPHONE"})
            with self.subTest(mutation=mutation):
                self.assertIn(expected, INTENT.evaluate(snapshot)["failed_requirements"])

    def test_mic_label_follows_actual_native_x_not_a_constant_or_source_claim(self):
        snapshot = fixture()
        snapshot["boards"][INTENT.PROJECTS[1]]["MK1"]["anchor_mm"][0] = 47.2
        self.assertEqual("fail", INTENT.evaluate(snapshot)["status"])
        snapshot["microphone_labels"][INTENT.PROJECTS[0]][0]["at_mm"][0] = 32.8
        self.assertEqual("pass", INTENT.evaluate(snapshot)["status"])

    def test_native_mic_text_extraction_reads_real_text_presentation_without_writes(self):
        try:
            import pcbnew
        except ImportError:
            self.skipTest("requires KiCad Python for in-memory native text extraction")
        board = pcbnew.BOARD()
        item = pcbnew.PCB_TEXT(board)
        item.SetText("MIC")
        item.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(33), pcbnew.FromMM(148.9)))
        item.SetLayer(pcbnew.F_SilkS)
        item.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
        item.SetTextThickness(pcbnew.FromMM(.15))
        item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        item.SetMirrored(False)
        item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        item.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        board.Add(item)
        self.assertEqual([mic_label()], INTENT.native_microphone_labels(board, pcbnew))
        item.SetVisible(False)
        item.SetMirrored(True)
        item.SetLayer(pcbnew.B_SilkS)
        actual = INTENT.native_microphone_labels(board, pcbnew)
        self.assertEqual(1, len(actual))
        self.assertFalse(actual[0]["visible"])
        self.assertTrue(actual[0]["mirrored"])
        self.assertNotEqual("F.Silkscreen", actual[0]["layer"])

    def test_jae_reference_overhang_is_not_user_accepted_overhang(self):
        self.rejected(1, "J1", "anchor_mm", [16.47, 146.9], "USB")

    def test_excessive_usb_recess_also_fails(self):
        self.rejected(1, "J1", "anchor_mm", [16.47, 140], "USB")

    def test_card_inward_shift_cannot_remove_press_access(self):
        self.rejected(0, "J5", "anchor_mm", [61.005, 138], "microSD")

    def test_card_x_must_align_with_actual_notch_not_only_pass_y(self):
        self.rejected(0, "J5", "anchor_mm", [10, 140.075], "accessible at notch")

    def test_missing_closed_duplicate_or_moved_native_notch_fails(self):
        for mutation in ("missing", "closed", "duplicate", "shifted", "floor-moved"):
            snapshot = fixture()
            edges = snapshot["bottom_edges"][INTENT.PROJECTS[0]]
            if mutation == "missing":
                edges.clear()
            elif mutation == "closed":
                edges.append(["line", [56.43, 150], [66.43, 150]])
            elif mutation == "duplicate":
                edges.append(copy.deepcopy(edges[2]))
            elif mutation == "shifted":
                for edge in edges:
                    for point in edge[1:]:
                        point[0] += 1
            else:
                edges[3][1][1] += .1
            with self.subTest(mutation=mutation):
                self.assertIn("actual native microSD notch is open at the reviewed bottom-edge datum",
                              INTENT.evaluate(snapshot)["failed_requirements"])

    def test_native_edge_observation_uses_actual_arcs_and_ignores_remote_fpc(self):
        class Shape:
            def __init__(self, row, layer=44):
                self.row, self.layer = row, layer
            def GetLayer(self): return self.layer
            def GetShape(self): return 1 if self.row[0] == "line" else 2
            def point(self, index):
                return SimpleNamespace(x=self.row[index][0], y=self.row[index][1])
            def GetStart(self): return self.point(1)
            def GetEnd(self): return self.point(-1)
            def GetArcMid(self): return self.point(2)
        api = SimpleNamespace(PCB_SHAPE=Shape, Edge_Cuts=44, SHAPE_T_SEGMENT=1,
                              SHAPE_T_ARC=2, ToMM=lambda x: x)
        shapes = [Shape(row) for row in notch_edges()]
        shapes += [Shape(["line", [26.5, 31.5], [53.5, 31.5]]),
                   Shape(["line", [56.43, 150], [66.43, 150]], layer=49)]
        board = SimpleNamespace(GetDrawings=lambda: shapes)
        edges = INTENT.native_bottom_edges(board, api)
        self.assertEqual(7, len(edges))
        result = INTENT.checked_native_notch(edges)
        self.assertTrue(result["pass"])
        self.assertAlmostEqual(61.43, result["axis_x_mm"])
        shapes[2].row = copy.deepcopy(shapes[2].row)
        shapes[2].row[2][1] += .1
        self.assertFalse(INTENT.checked_native_notch(INTENT.native_bottom_edges(board, api))["pass"])

    def test_button_geometry_not_anchor_symmetry_is_compared(self):
        self.rejected(0, "SW13", "actuator_mm", [74.65, 22.5], "F1/F5")

    def test_narrow_antennas_and_role_swap_are_detected(self):
        self.rejected(1, "J6", "anchor_mm", [51.75, 0], "SMA")
        self.rejected(1, "J6", "pad1_nets", ["/RF_20_CC1101_VOICE_TX/VOICE_V_EXTERNAL_RF_50R"], "signal identities")

    def test_missing_strategic_component_fails_closed(self):
        snapshot = fixture()
        del snapshot["boards"][INTENT.PROJECTS[1]]["SW3"]
        with self.assertRaises(KeyError):
            INTENT.evaluate(snapshot)

    def test_published_report_records_requirements_not_just_inventory(self):
        path = ROOT / "hardware/layout/generated/H6-R2-placement-intent.json"
        if not path.is_file():
            self.skipTest("report is generated during joint native integration")
        report = json.loads(path.read_text())
        self.assertEqual("pass", report["status"])
        self.assertGreaterEqual(len(report["checks"]), 20)
        self.assertEqual([], report["failed_requirements"])


if __name__ == "__main__":
    unittest.main()
