"""Recess geometry and its stage authorization are independent, narrow checks."""
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_microsd_recess as recess

try:
    import pcbnew
except ImportError:
    pcbnew = None
if pcbnew is not None:
    import h6_r2_placement as placement
    import h6_r2_stage_placement_update as stage

EXPECTED = {
    "sd": ("J5", [61.005, 140.075], 180),
    "sd_esd_a": ("U6", [59.645, 128.405], 90),
    "sd_esd_b": ("U7", [63.145, 128.405], 90),
    "sd_card_cmd_pullup": ("R39", [56.825, 130.2], 0),
    "sd_card_dat1_pullup": ("R41", [66.075, 130.2], 0),
    "sd_card_dat2_pullup": ("R42", [62.075, 130.315], 0),
    "sd_card_dat3_pullup": ("R43", [59.825, 130.315], 0),
}


def contract():
    return json.loads((ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text())


class MicroSDRecessGeometryTests(unittest.TestCase):
    def test_seven_exact_existing_parts_are_locked_without_mpn_net_changes(self):
        c = contract()
        rows = {r["instance"]: r for r in json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json").read_text())["rows"]}
        for instance, (ref, anchor, angle) in EXPECTED.items():
            with self.subTest(instance=instance):
                row = c["placement_overrides"][instance]
                self.assertEqual(ref, rows[instance]["reference"])
                self.assertEqual("LESHY2-UI-R2", rows[instance]["project"])
                self.assertEqual(anchor, row["anchor_mm"])
                self.assertEqual(angle, row["rotation_deg"])
                self.assertEqual("ui-inner", row["frame"])
                self.assertIs(row["mechanical_locked"], True)
                self.assertIn(recess.FEATURE_ID, row["reason"])

    def test_card_axis_uses_mounting_drawing_not_anchor_centre(self):
        c = contract()
        f = recess.feature(c, recess.PROJECT)
        self.assertEqual(61.43, f["card_axis_x_mm"])
        self.assertAlmostEqual(61.43, c["placement_overrides"]["sd"]["anchor_mm"][0] + .425)
        self.assertEqual({"x": [56.43, 66.43], "y": [148.8, 150]}, f["bbox_mm"])
        self.assertEqual(.6, f["internal_radius_mm"])

    def test_nominal_lock_push_eject_preserve_full_manufacturer_travel(self):
        c = contract(); f = recess.feature(c, recess.PROJECT)
        datum = c["placement_overrides"]["sd"]["mechanical_datum"]
        self.assertAlmostEqual(148.2, 140.075 + 8.125)
        for key, length, expected in (("card_locked_y_mm", 17.55, 149.8),
                                      ("card_overstroke_y_mm", 16.75, 149.0),
                                      ("card_ejected_y_mm", 21.55, 153.8)):
            self.assertAlmostEqual(expected, f[key])
            self.assertAlmostEqual(expected, f["shell_mouth_y_mm"] + length - datum["body_length_mm"])
        self.assertAlmostEqual(.8, f["card_locked_y_mm"] - f["card_overstroke_y_mm"])
        self.assertAlmostEqual(4, f["card_ejected_y_mm"] - f["card_locked_y_mm"])
        for phase, y in (("locked", 149.8), ("overstroke", 149.0), ("ejected", 153.8)):
            self.assertAlmostEqual(y, datum["native_shell_mouth_y_mm"] + datum[f"card_{phase}_beyond_shell_mm"])
            self.assertAlmostEqual(y, c["board"]["height_mm"] + datum[f"card_{phase}_beyond_pcb_edge_mm"])
        self.assertNotIn("card_locked_protrusion_mm", datum)
        self.assertNotIn("card_ejected_protrusion_mm", datum)
        self.assertIs(datum["card_positions_are_nominal_not_tolerance_bounds"], True)
        self.assertIs(f["positions_are_nominal_not_tolerance_bounds"], True)
        self.assertIs(f["manufacturer_mandates_pcb_notch"], False)

    def test_notch_is_open_to_bottom_with_two_exact_tangent_quarter_arcs(self):
        p = recess.bottom_edge_primitives(contract(), recess.PROJECT)
        self.assertEqual(7, len(p))
        self.assertEqual((78, 150), p[0][1])
        self.assertEqual((2, 150), p[-1][-1])
        for a, b in zip(p, p[1:]):
            self.assertEqual(a[-1], b[1])
        arcs = [q for q in p if q[0] == "gr_arc"]
        self.assertEqual(2, len(arcs))
        for arc, centre in zip(arcs, ((65.83, 149.4), (57.03, 149.4))):
            for point in arc[1:]:
                self.assertAlmostEqual(.6, math.dist(point, centre))
        for q in p:
            for x, y in q[1:]:
                self.assertTrue(2 <= x <= 78 and 148.8 <= y <= 150)

    def test_rf_outline_and_fpc_slot_are_not_part_of_the_allowance(self):
        c = contract()
        self.assertEqual([("gr_line", (78, 150), (2, 150))], recess.bottom_edge_primitives(c, "LESHY2-RF-R2"))
        self.assertEqual({"x": [26.5, 53.5], "y": [31.5, 32.7]}, c["mechanical"]["display_slot"]["bbox_mm"])
        self.assertEqual(.6, c["mechanical"]["display_slot"]["end_radius_mm"])

    def test_wrong_identity_radius_axis_size_or_readiness_flags_fail_closed(self):
        for key, value in (("id", "any-cutout"), ("internal_radius_mm", .59),
                           ("card_axis_x_mm", 61.005), ("internal_radius_mm", True),
                           ("positions_are_nominal_not_tolerance_bounds", False),
                           ("manufacturer_mandates_pcb_notch", True)):
            c = contract(); c["mechanical"]["microsd_recess"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                recess.feature(c, recess.PROJECT)


@unittest.skipIf(pcbnew is None, "KiCad Python required for native edge guard")
class MicroSDRecessStageTests(unittest.TestCase):
    def setUp(self):
        self.c = contract()
        self.allowance = {"feature_id": recess.FEATURE_ID,
                          "source_contract_sha256": hashlib.sha256(placement.CONTRACT_PATH.read_bytes()).hexdigest()}
        old = copy.deepcopy(self.c); del old["mechanical"]["microsd_recess"]
        self.old = self.native(old)
        self.new = self.native(self.c)

    def native(self, c):
        board = pcbnew.BOARD()
        placement.configure_board(board, c, recess.PROJECT)
        placement.add_capsule_slot(board, c["mechanical"]["display_slot"]["bbox_mm"])
        return placement.board_bytes("test-recess", board).decode()

    def check(self, old=None, new=None, allowance=None, project=None):
        return stage.reviewed_edge_cut_changes(old or self.old, new or self.new,
            self.allowance if allowance is None else allowance, project or recess.PROJECT, self.c)

    def test_exact_one_to_seven_delta_keeps_every_other_edge(self):
        old, new = self.check()
        self.assertEqual((1, 7), (len(old), len(new)))
        self.assertEqual(12, len(stage.edge_cut_forms(self.old)))
        self.assertEqual(18, len(stage.edge_cut_forms(self.new)))

    def test_absent_allowance_rejects_cutout_change(self):
        with self.assertRaisesRegex(ValueError, "unreviewed Edge.Cuts"):
            stage.reviewed_edge_cut_changes(self.old, self.new, None, recess.PROJECT, self.c)

    def test_wrong_feature_contract_hash_project_or_extra_key_is_rejected(self):
        for allowance in ({}, {**self.allowance, "feature_id": "all"},
                          {**self.allowance, "source_contract_sha256": "0" * 64},
                          {**self.allowance, "allow_all": True}):
            with self.subTest(allowance=allowance), self.assertRaises(ValueError):
                self.check(allowance=allowance)
        with self.assertRaises(ValueError):
            self.check(project="LESHY2-RF-R2")

    def test_an_added_edge_or_fpc_change_cannot_hide_in_allowed_notch(self):
        for extra in ('(gr_line (start 20 20) (end 22 20) (stroke (width .05) (type default)) (layer "Edge.Cuts"))',
                      stage.edge_cut_forms(self.new)[0][1]):
            altered = self.new.rstrip()[:-1] + extra + ')'
            with self.subTest(extra=extra[:40]), self.assertRaises(ValueError):
                self.check(new=altered)
        moved = copy.deepcopy(self.c)
        moved["mechanical"]["display_slot"]["bbox_mm"]["y"] = [31.6, 32.8]
        with self.assertRaises(ValueError):
            self.check(new=self.native(moved))

    def test_edge_width_or_missing_original_is_rejected(self):
        wrong = self.new.replace('(width 0.05)', '(width 0.06)', 1)
        self.assertNotEqual(wrong, self.new)
        with self.assertRaises(ValueError):
            self.check(new=wrong)
        with self.assertRaises(ValueError):
            self.check(old=self.new)


if __name__ == "__main__":
    unittest.main()
