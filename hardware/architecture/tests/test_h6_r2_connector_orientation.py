"""Bottom-edge connector mouths are fixed physical datums, not bounding boxes."""

import ast
import json
import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
LIBRARY = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
GCT_FOOTPRINT = "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"
JAE_FOOTPRINT = "Leshy2_R2:USB_C_Receptacle_JAE_DX07S016JA1R1500_EdgeSilk"
SD_FOOTPRINT = "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5"
EXPECTED = {
    "product_usb_connector": ("LESHY2-RF-R2", "J1", "rear-inner", [16.47, 146.9], JAE_FOOTPRINT),
    "hub_rp_service_usb_connector": ("LESHY2-UI-R2", "J11", "ui-inner", [14.87, 146.325], GCT_FOOTPRINT),
    "c5_service_usb_connector": ("LESHY2-UI-R2", "J9", "ui-inner", [26.1, 146.325], GCT_FOOTPRINT),
    "rf_rp_service_usb_connector": ("LESHY2-RF-R2", "J4", "rear-inner", [37.47, 146.325], GCT_FOOTPRINT),
    "sd": ("LESHY2-UI-R2", "J5", "ui-inner", [61.005, 141.875], SD_FOOTPRINT),
}
SUPPORT = {
    "sd_esd_a": ("U6", [59.645, 130.205], 90.0),
    "sd_esd_b": ("U7", [63.145, 130.205], 90.0),
    "sd_card_cmd_pullup": ("R39", [56.825, 132.0], 0.0),
    "sd_card_dat1_pullup": ("R41", [66.075, 132.0], 0.0),
}


def rectangle_gap(a, b):
    dx = max(a["x"][0] - b["x"][1], b["x"][0] - a["x"][1], 0)
    dy = max(a["y"][0] - b["y"][1], b["y"][0] - a["y"][1], 0)
    return math.hypot(dx, dy)


def native_b_point(local, anchor, rotation):
    """KiCad B-face reflection followed by its clockwise-positive XY angle."""
    x, y = local[0], -local[1]
    theta = math.radians(-rotation)
    return (anchor[0] + x * math.cos(theta) - y * math.sin(theta),
            anchor[1] + x * math.sin(theta) + y * math.cos(theta))


def functions():
    names = {"service_button_target", "target_for_instance", "target_side",
             "desired_rotation", "rect_size", "correction_rotations", "is_edge_interface"}
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == names
    namespace = {"math": math}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SCRIPT), "exec"), namespace)
    return tree, namespace


class ConnectorOrientationTests(unittest.TestCase):
    def setUp(self):
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate placement-contract key: {key}")
                result[key] = value
            return result
        self.contract = json.loads(CONTRACT.read_text(), object_pairs_hook=unique_keys)
        self.tree, self.fn = functions()

    def target(self, instance, frozen=None):
        project, ref, _, _, _ = EXPECTED[instance]
        return self.fn["target_for_instance"](project, instance, ref, self.contract, {}, frozen or {})

    def footprint_text(self, name):
        library, footprint = name.split(":")
        root = ROOT / "hardware/ecad/libraries" if library == "Leshy2_R2" else LIBRARY
        path = root / (library + ".pretty") / (footprint + ".kicad_mod")
        self.assertTrue(path.is_file(), f"exact native footprint library required: {path}")
        return path.read_text()

    def test_exact_five_native_references_and_packages_are_covered(self):
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json").read_text())
        rows = {row["instance"]: row for row in ledger["rows"]}
        for instance, (project, reference, _, _, footprint) in EXPECTED.items():
            with self.subTest(instance=instance):
                self.assertEqual(project, rows[instance]["project"])
                self.assertEqual(reference, rows[instance]["reference"])
                self.assertEqual(footprint, rows[instance]["footprint"])
        self.assertEqual({key for key, row in EXPECTED.items() if row[4] == GCT_FOOTPRINT},
                         {row["instance"] for row in ledger["rows"] if row["mpn"] == "GCT USB4105-GF-A"})

    def test_contract_uses_locked_anchors_not_courtyard_centres(self):
        for instance, (_, _, frame, anchor, _) in EXPECTED.items():
            with self.subTest(instance=instance):
                row = self.contract["placement_overrides"][instance]
                self.assertEqual(frame, row["frame"])
                self.assertEqual(anchor, row["anchor_mm"])
                self.assertNotIn("centre_mm", row)
                self.assertEqual(180, row["rotation_deg"])
                self.assertTrue(row["mechanical_locked"])
                self.assertEqual("reviewed outward connector mouth datum", row["method"])
                self.assertEqual("2026-09-07", row["mechanical_datum"]["checked"])
                self.assertIn("https://", row["mechanical_datum"]["source_url"])

    def test_wrong_frozen_pose_cannot_win_over_manufacturer_datum(self):
        for instance, (project, _, _, anchor, _) in EXPECTED.items():
            for old_angle in (0, 90, 270):
                with self.subTest(instance=instance, old_angle=old_angle):
                    frozen = {(project, instance): {
                        "side": "B.Cu", "rotation_deg": old_angle,
                        "courtyard_centre_mm": [20, 145],
                        "footprint_anchor_nm": [20_000_000, 145_000_000], "method": "old frozen pose"}}
                    target = self.target(instance, frozen)
                    self.assertEqual(anchor, target["anchor"])
                    self.assertEqual(180, target["rotation"])
                    self.assertEqual("B.Cu", self.fn["target_side"](target))
                    self.assertTrue(target["mechanical_locked"])
                    self.assertTrue(target["rotation_locked"])
                    self.assertNotIn("frozen", target)
                    self.assertNotIn("exact_anchor_nm", target)

    def test_bottom_mouth_axis_survives_b_side_reflection(self):
        for instance in EXPECTED:
            target = self.target(instance)
            anchor = target["anchor"]
            local = self.contract["placement_overrides"][instance]["mechanical_datum"]["local_mouth_axis"]
            x, y = native_b_point(local, anchor, target["rotation"])
            self.assertAlmostEqual(anchor[0], x)
            self.assertAlmostEqual(anchor[1] + 1, y)
            # The previous B0 is inward; previous SD B90 is sideways.
            old = native_b_point(local, anchor, 90 if instance == "sd" else 0)
            self.assertLess(old[1], y)

    def test_fixed_connector_cannot_fall_back_to_quarter_turn_or_repacking(self):
        expression = next(node.value for node in ast.walk(self.tree)
                          if isinstance(node, ast.Assign) and len(node.targets) == 1
                          and ast.unparse(node.targets[0]) == "entry['hard']")
        for instance in EXPECTED:
            target = self.target(instance)
            self.assertEqual((180,), self.fn["correction_rotations"](180, target))
            target["placement_method"] = None
            namespace = {"target": target, "entry": {"row": {"instance": instance}}, "hard_locked": set()}
            self.assertTrue(eval(compile(ast.Expression(expression), str(SCRIPT), "eval"), namespace))
        # The actual hard-conflict branch commits a finding and continues;
        # correction_centres/nearest-grid search must not execute for these.
        branch = next(node for node in ast.walk(self.tree)
                      if isinstance(node, ast.If) and ast.unparse(node.test) == "entry['hard']"
                      and any(isinstance(child, ast.Continue) for child in node.body))
        self.assertIn("conflicts.append", ast.unparse(branch))
        self.assertNotIn("correction_centres", ast.unparse(branch))

    def test_anchor_and_centre_ambiguity_is_rejected(self):
        instance = "sd"
        row = self.contract["placement_overrides"][instance]
        row["centre_mm"] = list(row["anchor_mm"])
        with self.assertRaisesRegex(ValueError, "exactly one anchor or centre"):
            self.target(instance)
        del row["centre_mm"]
        del row["anchor_mm"]
        with self.assertRaisesRegex(ValueError, "exactly one anchor or centre"):
            self.target(instance)

    def test_exact_gct_library_pcb_edge_and_electrical_tail_orientation(self):
        text = self.footprint_text(GCT_FOOTPRINT)
        self.assertRegex(text, r'\(start 5 3\.675\)\s*\(end -5 3\.675\)[\s\S]*?\(layer "Dwgs\.User"\)')
        self.assertIn('(fp_text user "PCB Edge"', text)
        rows = re.findall(r'\(pad "(?:A|B)\d+" smd \w+\s*\(at [-\d.]+ ([-\d.]+)\)', text)
        self.assertEqual(16, len(rows))
        self.assertEqual({-3.68}, {float(y) for y in rows})
        for instance in EXPECTED:
            if EXPECTED[instance][4] != GCT_FOOTPRINT:
                continue
            target = self.target(instance)
            datum = self.contract["placement_overrides"][instance]["mechanical_datum"]
            mouth = native_b_point([0, datum["local_pcb_edge_y_mm"]], target["anchor"], 180)
            self.assertAlmostEqual(self.contract["board"]["height_mm"], mouth[1])
            tail = native_b_point([0, -3.68], target["anchor"], 180)
            self.assertAlmostEqual(142.645, tail[1])
            self.assertLess(tail[1], mouth[1])

    def test_exact_jae_locator_datum_overhang_and_copper_edge_clearance(self):
        text = self.footprint_text(JAE_FOOTPRINT)
        self.assertRegex(text, r'\(pad "" np_thru_hole circle\s*\(at -3 -1\.95\)')
        self.assertRegex(text, r'\(pad "" np_thru_hole oval\s*\(at 3 -1\.95\)')
        self.assertRegex(text, r'\(start -4\.47 3\.6\)\s*\(end 4\.47 3\.6\)[\s\S]*?\(layer "F\.Fab"\)')
        datum = self.contract["placement_overrides"]["product_usb_connector"]["mechanical_datum"]
        self.assertAlmostEqual(3.1, datum["local_locator_datum_y_mm"] +
                               datum["pcb_edge_offset_from_locator_datum_mm"])
        target = self.target("product_usb_connector")
        edge = native_b_point([0, datum["local_pcb_edge_y_mm"]], target["anchor"], 180)[1]
        mouth = native_b_point([0, datum["local_shell_mouth_y_mm"]], target["anchor"], 180)[1]
        self.assertAlmostEqual(self.contract["board"]["height_mm"], edge)
        self.assertAlmostEqual(150.5, mouth)
        self.assertAlmostEqual(datum["shell_overhang_mm"], mouth - edge)
        pads = re.findall(r'\(pad "[^"]*" (?:smd|thru_hole) \w+\s*'
                          r'\(at [-\d.]+ ([-\d.]+)\)\s*\(size [-\d.]+ ([-\d.]+)\)', text)
        self.assertEqual(22, len(pads))
        copper_max = max(target["anchor"][1] + float(y) + float(height) / 2 for y, height in pads)
        self.assertAlmostEqual(datum["native_maximum_copper_y_mm"], copper_max)
        self.assertAlmostEqual(datum["minimum_copper_edge_clearance_mm"], edge - copper_max)

    def test_exact_sd_library_shell_and_card_directions(self):
        text = self.footprint_text(SD_FOOTPRINT)
        self.assertRegex(text, r'\(start 6\.925 8\.125\)\s*\(end 6\.925 -7\.825\)[\s\S]*?\(layer "F\.Fab"\)')
        contacts = re.findall(r'\(pad "[1-8]" smd \w+\s*\(at [-\d.]+ ([-\d.]+)\)', text)
        self.assertEqual(8, len(contacts))
        self.assertEqual({-7.725}, {float(y) for y in contacts})
        target = self.target("sd")
        datum = self.contract["placement_overrides"]["sd"]["mechanical_datum"]
        mouth = native_b_point([0, datum["local_shell_mouth_y_mm"]], target["anchor"], 180)
        self.assertAlmostEqual(150, mouth[1])
        self.assertAlmostEqual(134.15, native_b_point([0, -7.725], target["anchor"], 180)[1])
        self.assertIn("project-selected flush", datum["placement_policy"])

    def test_card_ejection_and_inward_push_are_not_confused(self):
        datum = self.contract["placement_overrides"]["sd"]["mechanical_datum"]
        self.assertAlmostEqual(4, datum["card_ejected_length_mm"] - datum["card_locked_length_mm"])
        self.assertAlmostEqual(4, datum["card_ejection_travel_from_lock_mm"])
        self.assertAlmostEqual(0.8, datum["card_locked_length_mm"] - datum["card_over_stroke_length_mm"])
        self.assertAlmostEqual(0.8, datum["card_push_stroke_from_lock_mm"])
        self.assertAlmostEqual(1.6, datum["card_locked_length_mm"] - datum["body_length_mm"])
        self.assertAlmostEqual(5.6, datum["card_ejected_length_mm"] - datum["body_length_mm"])
        self.assertAlmostEqual(151.6, datum["native_shell_mouth_y_mm"] + datum["card_locked_protrusion_mm"])
        self.assertAlmostEqual(155.6, datum["native_shell_mouth_y_mm"] + datum["card_ejected_protrusion_mm"])
        self.assertIn("finger/card access", datum["access_scope"])

    def test_actual_edge_exception_is_explicit_not_a_packing_escape(self):
        for instance in EXPECTED:
            target = self.target(instance)
            self.assertTrue(self.fn["is_edge_interface"](instance, target, self.contract))
            self.assertIn("board-edge", target["direction"])
            self.assertTrue(target["mechanical_locked"])

    def test_only_four_reviewed_sd_support_parts_have_explicit_local_corrections(self):
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        board = next(row for row in audit["boards"] if row["project"] == "LESHY2-UI-R2")
        rows = {row["instance"]: row for row in board["placements"]}
        for instance, (reference, anchor, rotation) in SUPPORT.items():
            with self.subTest(instance=instance):
                override = self.contract["placement_overrides"][instance]
                self.assertEqual("ui-inner", override["frame"])
                self.assertEqual(anchor, override["anchor_mm"])
                self.assertEqual(rotation, override["rotation_deg"])
                self.assertTrue(override["mechanical_locked"])
                self.assertEqual(reference, rows[instance]["reference"])
                self.assertEqual("B.Cu", rows[instance]["side"])
                self.assertEqual(rotation, rows[instance]["rotation_deg"])
        # Removing duplicate earlier -35/-25 entries must not change the
        # effective, already accepted current charger scheduling priorities.
        for instance in ("charger_pmid_hf_cap", "charger_regn_cap", "charger_vbus_hf_cap"):
            self.assertEqual(-90, self.contract["placement_policy"]["locality_order"][instance])

    def test_sd_and_local_support_clear_unchanged_inner_face_courtyards(self):
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        board = next(row for row in audit["boards"] if row["project"] == "LESHY2-UI-R2")
        rows = {row["instance"]: row for row in board["placements"]}
        # Actual KiCad B180 courtyard including its stroke. Card motion is
        # outside this box and covered separately, not silently omitted.
        candidates = {"sd": {"x": [53.08, 68.87], "y": [133.01, 150.8]}}
        for instance, (_, anchor, _) in SUPPORT.items():
            row = rows[instance]
            delta = [a - b for a, b in zip(anchor, row["footprint_anchor_mm"])]
            candidates[instance] = {
                axis: [value + delta[index] for value in row["courtyard_bbox_mm"][axis]]
                for index, axis in enumerate(("x", "y"))}
        obstacles = {name: row["courtyard_bbox_mm"] for name, row in rows.items()
                     if row["side"] == "B.Cu" and name not in candidates}
        minimum = self.contract["board"]["minimum_courtyard_gap_mm"]
        for name, box in candidates.items():
            for other, obstacle in (obstacles | candidates).items():
                if name == other:
                    continue
                with self.subTest(instance=name, obstacle=other):
                    self.assertGreaterEqual(rectangle_gap(box, obstacle) + 1e-6, minimum)


if __name__ == "__main__":
    unittest.main()
