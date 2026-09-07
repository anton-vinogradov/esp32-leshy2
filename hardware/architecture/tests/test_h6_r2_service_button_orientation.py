"""Mechanical actuation, not portrait/landscape, determines service-button pose."""

import ast
import copy
import json
import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
FOOTPRINT_NAME = "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010"
EXPECTED = {
    "LESHY2-UI-R2": {
        "s3_reset_button": ("left", 90.0, 117.25),
        "s3_boot_button": ("left", 90.0, 124.25),
        "c5_reset_button": ("right", 270.0, 117.25),
        "c5_boot_button": ("right", 270.0, 124.25),
        "hub_rp_reset_button": ("right", 270.0, 131.5),
        "hub_rp_boot_button": ("right", 270.0, 138.0),
    },
    "LESHY2-RF-R2": {
        "rf_rp_reset_button": ("left", 90.0, 108.25),
        "rf_rp_boot_button": ("left", 90.0, 115.25),
    },
}


def pure_functions():
    names = {
        "service_button_target", "service_button_placement_errors",
        "target_for_instance", "target_side", "desired_rotation", "rect_size",
        "correction_rotations", "correction_centres", "candidate_centres",
    }
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == names
    namespace = {"math": math}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SCRIPT), "exec"), namespace)
    return namespace


class ServiceButtonOrientationTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.fn = pure_functions()

    def target(self, project, instance, frozen=None):
        return self.fn["target_for_instance"](
            project, instance, "SW_TEST", self.contract, {}, frozen or {}
        )

    def rows(self, project):
        return [
            {"instance": instance, "footprint": FOOTPRINT_NAME,
             "side": "B.Cu", "rotation_deg": angle,
             "courtyard_centre_mm": [1.7 if edge == "left" else 78.3, y]}
            for instance, (edge, angle, y) in EXPECTED[project].items()
        ]

    def test_contract_covers_exactly_all_eight_native_service_switches(self):
        policy = self.contract["service_buttons"]
        self.assertEqual("alps_skrtlae010", policy["device_id"])
        self.assertEqual(FOOTPRINT_NAME, policy["footprint"])
        self.assertEqual("B.Cu", policy["side"])
        self.assertEqual(1.7, policy["courtyard_edge_inset_mm"])
        self.assertLessEqual(policy["maximum_along_edge_correction_mm"], 1.0)
        self.assertEqual(set(EXPECTED), set(policy["by_project"]))
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json").read_text())
        actual = {(row["project"], row["instance"]) for row in ledger["rows"]
                  if row["device_id"] == "alps_skrtlae010"}
        self.assertEqual({(p, i) for p, rows in EXPECTED.items() for i in rows}, actual)
        for project, rows in EXPECTED.items():
            self.assertEqual(set(rows), set(policy["by_project"][project]))

    def test_target_uses_the_outward_actuator_not_bounding_box_aspect_ratio(self):
        # Alps Drawing No.1: nose opposes the three electrical lands.
        # KiCad library F.Fab nose=(0,+2.04), electrical-pad row y=-0.9.
        # Native B.Cu mirrors Y; KiCad positive angles rotate clockwise in xy.
        for project, rows in EXPECTED.items():
            for instance, (edge, angle, y) in rows.items():
                with self.subTest(instance=instance):
                    target = self.target(project, instance)
                    self.assertEqual(angle, target["rotation"])
                    self.assertEqual("B.Cu", self.fn["target_side"](target))
                    self.assertEqual([1.7 if edge == "left" else 78.3, y], target["centre"])
                    radians = math.radians(target["rotation"])
                    outward = (-math.sin(radians), -math.cos(radians))
                    self.assertAlmostEqual(-1 if edge == "left" else 1, outward[0])
                    self.assertAlmostEqual(0, outward[1])
                    misleading = {0.0: {"size": (1, 7)}, 90.0: {"size": (7, 1)}}
                    self.assertEqual(angle, self.fn["desired_rotation"](misleading, target))

    def test_named_library_actuator_is_opposite_electrical_lands(self):
        footprint = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/") / (
            "Button_Switch_SMD.pretty/SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010.kicad_mod"
        )
        if not footprint.exists():
            self.skipTest("KiCad footprint library not installed")
        text = footprint.read_text(encoding="utf-8")
        self.assertRegex(text, r'\(start -1 2\.04\)\s*\(end 1 2\.04\)[\s\S]*?\(layer "F\.Fab"\)')
        for number, y in (("1", -0.9), ("2", -0.9), ("MP", 1.05)):
            matches = re.findall(r'\(pad "' + number + r'" smd \w+\s*\(at [-\d.]+ ([-\d.]+)\)', text)
            self.assertTrue(matches)
            self.assertEqual({y}, {float(value) for value in matches})

    def test_actuator_overhang_and_guide_holes_have_actual_edge_clearance(self):
        # F.CrtYd centre is y=+0.125.  Mirroring and rotating reverses it
        # on the left/right banks; a 1.7 mm courtyard inset is NOT the anchor.
        for edge, sign, centre in (("left", -1, 1.7), ("right", 1, 78.3)):
            with self.subTest(edge=edge):
                anchor = centre - sign * 0.125
                nose = anchor + sign * 2.04
                overhang = -nose if sign < 0 else nose - 80
                self.assertAlmostEqual(0.215, overhang)
                self.assertGreater(overhang, 0.2)  # nominal documented travel
                hole_edge_margin = (anchor if sign < 0 else 80 - anchor) - 0.45
                self.assertAlmostEqual(1.375, hole_edge_margin)
                mounting_pad_outer = anchor + sign * (1.05 + 0.45)
                pad_margin = mounting_pad_outer if sign < 0 else 80 - mounting_pad_outer
                self.assertAlmostEqual(0.325, pad_margin)

    def test_bad_frozen_quarter_turn_and_inward_facing_poses_do_not_win(self):
        for angle in (0.0, 90.0, 180.0):
            frozen = {("LESHY2-UI-R2", "hub_rp_boot_button"): {
                "side": "B.Cu", "rotation_deg": angle,
                "courtyard_centre_mm": [77, 138], "footprint_anchor_nm": [77_000_000, 138_125_000],
                "method": "nearest exact-footprint correction",
            }}
            target = self.target("LESHY2-UI-R2", "hub_rp_boot_button", frozen)
            self.assertEqual(270.0, target["rotation"])
            self.assertEqual([78.3, 138.0], target["centre"])
            self.assertNotIn("exact_anchor_nm", target)
            self.assertFalse(target.get("frozen", False))

    def test_correct_frozen_pose_remains_exact_and_locked(self):
        row = {"side": "B.Cu", "rotation_deg": 270.0,
               "courtyard_centre_mm": [78.3, 137.75],
               "footprint_anchor_nm": [78_175_000, 137_750_000], "method": "reviewed"}
        target = self.target("LESHY2-UI-R2", "hub_rp_boot_button",
                             {("LESHY2-UI-R2", "hub_rp_boot_button"): row})
        self.assertTrue(target["frozen"])
        self.assertEqual(row["footprint_anchor_nm"], target["exact_anchor_nm"])

    def test_collision_fallback_cannot_rotate_or_move_away_from_edge(self):
        target = self.target("LESHY2-UI-R2", "hub_rp_boot_button")
        self.assertEqual((270.0,), self.fn["correction_rotations"](270.0, target))
        centres = list(self.fn["correction_centres"](tuple(target["centre"]), target, self.contract["board"]))
        self.assertEqual(9, len(centres))
        self.assertEqual({78.3}, {x for x, _ in centres})
        self.assertEqual({137 + n / 4 for n in range(9)}, {y for _, y in centres})
        self.assertEqual((0.0, 90.0), self.fn["correction_rotations"](0.0, {}))

    def test_bad_manual_override_is_rejected_not_silently_applied(self):
        self.contract["placement_overrides"]["hub_rp_boot_button"] = {
            "frame": "ui-inner", "rotation_deg": 90, "centre_mm": [78.3, 138], "reason": "bad"}
        with self.assertRaisesRegex(ValueError, "edge actuator datum"):
            self.target("LESHY2-UI-R2", "hub_rp_boot_button")

    def test_audit_rejects_missing_wrong_angle_side_package_and_edge_location(self):
        project = "LESHY2-UI-R2"
        baseline = self.rows(project)
        check = self.fn["service_button_placement_errors"]
        self.assertEqual([], check(project, baseline, self.contract))
        for field, value in (("rotation_deg", 0), ("rotation_deg", 90),
                             ("side", "F.Cu"), ("footprint", "Wrong:Package"),
                             ("courtyard_centre_mm", [77, 138]),
                             ("courtyard_centre_mm", [78.3, 140])):
            with self.subTest(field=field, value=value):
                rows = copy.deepcopy(baseline)
                rows[-1][field] = value
                self.assertEqual(1, len(check(project, rows, self.contract)))
        self.assertEqual(1, len(check(project, baseline[:-1], self.contract)))


if __name__ == "__main__":
    unittest.main()
