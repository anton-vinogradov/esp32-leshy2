"""Independent centre/body regressions; no exact-land or thermal approval."""

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_r2_holder_polarity as holder


def parse(text):
    # Share only the syntax parser, not expected geometry, with polarity tests.
    path = ROOT / "hardware/architecture/tests/test_h6_r2_holder_polarity.py"
    spec = importlib.util.spec_from_file_location("holder_polarity_syntax", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse(text), module.children, module.field


class HolderCenteringSourceTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text())
        self.fp, self.children, self.field = parse(holder.OUTPUT.read_text())

    def test_requested_board_x_axis_not_whole_board_y_symmetrization(self):
        self.assertEqual(80.0, self.contract["board"]["width_mm"])
        self.assertEqual([40.0, 85.0], self.contract["mechanical"]["rear_battery_holder"]["centre_mm"])
        row = self.contract["placement_overrides"]["pack_holder"]
        self.assertEqual([40.0, 85.0], row["centre_mm"])
        self.assertEqual("rear-outer", row["frame"])
        self.assertEqual(90.0, row["rotation_deg"])
        self.assertIs(row["mechanical_locked"], True)
        self.assertNotIn("without moving the routed interboard", row["reason"])

    def test_both_ntcs_follow_nominal_cell_axes_without_thermal_claim(self):
        rows = self.contract["placement_overrides"]
        for instance, x in (("pack_ntc0", 30.45), ("pack_ntc1", 49.55)):
            row = rows[instance]
            self.assertEqual([x, 85.0], row["centre_mm"])
            self.assertEqual(90.0, row["rotation_deg"])
            self.assertEqual("rear-outer", row["frame"])
            self.assertEqual("pack_holder", row["allowed_same_face_overlap_owner"])
            self.assertIs(row["mechanical_locked"], True)
            self.assertIn("H6-CELL-NTC-HEIGHT-FIT", row["reason"])
        thermal = json.loads((ROOT / "hardware/layout/h6-r2-mechanical-stack.json").read_text())["battery_thermal_contacts"]
        self.assertEqual("open", thermal["release_gate"]["status"])
        self.assertIsNone(thermal["holder_cell_floor_nominal_above_pcb_mm"])

    def test_only_plastic_body_is_fab_and_pad_span_is_dashed_reference(self):
        rectangles = {self.field(r, "layer")[0]: r for r in self.children(self.fp, "fp_rect")}
        self.assertEqual({"F.Fab", "Dwgs.User"}, set(rectangles))
        expected = {"F.Fab": ((-38.53, -19.89), (38.53, 19.89), "default"),
                    "Dwgs.User": ((-43.0, -19.9), (43.0, 19.9), "dash")}
        for layer, (start, end, stroke_type) in expected.items():
            rect = rectangles[layer]
            self.assertEqual(start, tuple(map(float, self.field(rect, "start"))))
            self.assertEqual(end, tuple(map(float, self.field(rect, "end"))))
            stroke = self.children(rect, "stroke")[0]
            self.assertEqual([stroke_type], self.field(stroke, "type"))
        self.assertEqual((77.06, 39.78), holder.BODY_SIZE_MM)
        self.assertIs(holder.BODY_REGISTRATION_QUALIFIED, False)
        self.assertIs(holder.MECHANICS_QUALIFIED, False)
        self.assertIs(holder.PRODUCTION_RELEASE_AUTHORIZED, False)

    def test_no_new_holes_or_manufacturer_land_adoption(self):
        expected = {"1": (-41, -9.55), "2": (41, -9.55), "3": (41, 9.55), "4": (-41, 9.55)}
        pads = self.children(self.fp, "pad")
        self.assertEqual(4, len(pads))
        self.assertEqual(set(expected), {pad[1] for pad in pads})
        for pad in pads:
            self.assertEqual(["smd", "rect"], pad[2:4])
            self.assertEqual(expected[pad[1]], tuple(map(float, self.field(pad, "at"))))
            self.assertEqual((4.0, 6.0), tuple(map(float, self.field(pad, "size"))))
            self.assertEqual(["F.Cu", "F.Paste", "F.Mask"], self.field(pad, "layers"))
            self.assertFalse(self.children(pad, "drill"))
        self.assertNotIn('"Edge.Cuts"', holder.OUTPUT.read_text())

    def test_h1_holder_views_share_one_centred_axis(self):
        path = ROOT / "hardware/product-design/g3_clamshell.py"
        spec = importlib.util.spec_from_file_location("holder_centering_h1", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.assertEqual(0.0, module.PACK_HOLDER_X_OFFSET)
        self.assertEqual(40.0, module.PACK_HOLDER_CENTRE_X)
        self.assertAlmostEqual(40.0, module.PACK_HOLDER_BODY_X + module.PACK_HOLDER_BODY_W / 2)
        self.assertAlmostEqual(40.0, module.PACK_HOLDER_PAD_X + 39.8 / 2)
        self.assertEqual(module.PACK_HOLDER_PAD_X, module.PACK_HOLDER_DRAWING_X)
        self.assertEqual((30.45, 49.55), module.PACK_CELL_CENTRES_X)

    def test_internal_fuse_and_small_radio_shifts_preserve_strict_locality(self):
        rows = self.contract["placement_overrides"]
        expected = {"pack_fuse1": ([53.37, 47.87], 270),
                    "voice_v": ([40.05, 53.5], 90),
                    "voice": ([13.1, 50.3], 90),
                    "pack_shunt": ([26.575, 43.975], 90)}
        for instance, (anchor, rotation) in expected.items():
            row = rows[instance]
            self.assertEqual("rear-inner", row["frame"])
            self.assertEqual(anchor, row["anchor_mm"])
            self.assertEqual(rotation, row["rotation_deg"])
            self.assertIs(row["mechanical_locked"], True)
        policy = self.contract["placement_policy"]
        self.assertEqual(2.0, policy["locality_max_gap_mm"]["pack_fuse1"])
        self.assertEqual("PACK_SLOT1_POSITIVE_RAW", policy["locality_anchor_net_by_instance"]["pack_fuse1"])

    def test_kelvin_via_relief_is_only_three_geometry_fields(self):
        rows = json.loads((ROOT / "hardware/layout/h6-r2-manual-copper.json").read_text())["routes"]
        row = next(r for r in rows if r["id"] == "RF-EXT-BUCK-FEEDBACK-SENSE")
        self.assertEqual("5V_EXT_PREPROTECT", row["canonical_net"])
        self.assertEqual(5, len(row["segments"]))
        self.assertEqual(2, len(row["vias"]))
        self.assertEqual([29.4, 128.65], row["segments"][2]["end_mm"])
        self.assertEqual([29.4, 128.65], row["segments"][3]["start_mm"])
        self.assertEqual({"at_mm": [29.4, 128.65], "diameter_mm": 0.4, "drill_mm": 0.2}, row["vias"][1])
        self.assertEqual([32.2, 127.5], row["segments"][2]["start_mm"])
        self.assertEqual([30.075, 128.605], row["segments"][3]["end_mm"])
        self.assertEqual(["In3.Cu", "B.Cu"], [r["layer"] for r in row["segments"][2:4]])
        self.assertEqual([0.15, 0.15], [r["width_mm"] for r in row["segments"][2:4]])


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Requires KiCad Python")
class HolderCenteringNativeGeometryTests(unittest.TestCase):
    def test_native_body_nominal_extents_and_checkerboard_at_centred_pose(self):
        import pcbnew as p
        fp = p.FootprintLoad(str(holder.OUTPUT.parent), holder.OUTPUT.stem)
        fp.SetOrientationDegrees(90)
        fp.SetPosition(p.VECTOR2I(p.FromMM(40), p.FromMM(85)))
        xy = lambda v: (round(p.ToMM(v.x), 6), round(p.ToMM(v.y), 6))
        bodies = [s for s in fp.GraphicalItems() if type(s).__name__ == "PCB_SHAPE" and s.GetLayer() == p.F_Fab]
        self.assertEqual(1, len(bodies))
        self.assertEqual((20.11, 123.53), xy(bodies[0].GetStart()))
        self.assertEqual((59.89, 46.47), xy(bodies[0].GetEnd()))
        expected = {"1": (30.45, 126), "2": (30.45, 44), "3": (49.55, 44), "4": (49.55, 126)}
        self.assertEqual(expected, {pad.GetNumber(): xy(pad.GetPosition()) for pad in fp.Pads()})


if __name__ == "__main__":
    unittest.main()
