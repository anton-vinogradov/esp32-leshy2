"""M1 mates in assembled coordinates, not between two untransformed PCB views.

Primary evidence reviewed 2026-09-07:
Hirose EDC3-151087-22 / EDC3-151023-22 sheet 1, mounting-side patterns
(document ids 0000988829 / 0000988573), and D31612_en pp5/10/15:
https://www.hirose.com/en/product/document?documentid=D31612_en&documenttype=Catalog&lang=en&series=FX8C
The P/S polarity marks are on opposite local rows. Their different SMT-tail
and locating-boss Y offsets are NOT an offset between the mating body axes.
These tests guard source geometry and all native electrical assignments;
the normal H6 placement --check owns propagation into current PCB poses.
No assembled-body/STEP or manufacture-readiness claim is made here.
"""

import ast
import json
import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
LIBRARY = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_Hirose_FX8.pretty")
PARTS = {
    "m1_ui_plug": ("LESHY2-UI-R2", "J18", "hirose_fx8c_80p_sv1_92",
                   "Hirose FX8C-80P-SV1(92)", "Hirose_FX8-80P-SV_2x40_P0.6mm"),
    "m1_rf_receptacle": ("LESHY2-RF-R2", "J12", "hirose_fx8c_80s_sv5_92",
                         "Hirose FX8C-80S-SV5(92)", "Hirose_FX8-80S-SV_2x40_P0.6mm"),
}
EXPECTED_OVERRIDES = {
    "m1_rf_receptacle": ([37.5, 122.25], 180.0),
    "unit_bleeder": ([25.25, 127.5], 0.0),
    "unit_output_cap": ([22.3, 128.5], 90.0),
}
EXPECTED_NETS = {str(n): None for n in range(1, 81)}
for n in list(range(1, 17)) + list(range(65, 77)):
    EXPECTED_NETS[str(n)] = "POWER_GROUND" if n % 2 else "3V3_MAIN"
EXPECTED_NETS.update({str(n): net for n, net in enumerate([
    "AON_SAFE_3V3", "POWER_GROUND", "AON_SAFE_3V3", "POWER_GROUND",
    "POWER_GROUND", "HUB_RF_ALERT_N", "HUB_RF_CS_N", "HUB_RF_SCK",
    "POWER_GROUND", "HUB_RF_MOSI", "HUB_RF_MISO", "POWER_GROUND",
    "S3_USB_DM", "S3_USB_DP", "POWER_GROUND", "HUB_SAFE_I2C_SDA_MAIN",
    "HUB_SAFE_I2C_SCL_MAIN", "POWER_GROUND", "FAULT_KILL",
    "S3_RESET_KILL_GATE", "RUN_PERMIT", "FAULT_ASSERT_N", "UI_ZONE_TEMP_ADC",
    "POWER_GROUND", "EV_N0_S3", "EV_N1_C5", "EV_N2_NRF0", "EV_N3_NRF1",
    "EV_N4_NRF2", "EV_N7_IR", "POWER_GROUND", "EV_N5_CC", "EV_N6_VOICE",
    "EV_N8_LORA_EXT", "ENCODER_A", "ENCODER_B", "UI_ENCODER_PUSH_N",
    "POWER_GROUND", "C5_MUX_SEL_REQUEST", "C5_SERVICE_PATH_ACK",
    "AON_SERVICE_RELEASE_REQ", "C5_SERVICE_OWNED", "HUB_AON_ALERT_N",
], 17)})


def load(relative):
    return json.loads((ROOT / relative).read_text())


def functions():
    names = {"service_button_target", "target_for_instance", "target_side",
             "_balanced_form_end", "rectangles_overlap"}
    tree = ast.parse(SCRIPT.read_text())
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected} == names
    namespace = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SCRIPT), "exec"), namespace)
    return namespace


def pads(text, balanced_end):
    result = []
    for match in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)', text):
        form = text[match.start():balanced_end(text, match.start())]
        at = re.search(r'\(at ([-\d.]+) ([-\d.]+)', form)
        drill = re.search(r'\(drill ([-\d.]+)\)', form)
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', form)
        result.append({"number": match[1], "kind": match[2],
                       "xy": [float(at[1]), float(at[2])],
                       "drill": float(drill[1]) if drill else None,
                       "net": net[1] if net else ""})
    return result


def native_point(local, anchor, side, rotation):
    """Independent KiCad transform: reflect local Y for B, then rotate -angle."""
    x, y = local
    if side == "B.Cu":
        y = -y
    theta = math.radians(-rotation)
    return (anchor[0] + x * math.cos(theta) - y * math.sin(theta),
            anchor[1] + x * math.sin(theta) + y * math.cos(theta))


def assembly_point(native, rear, width=80.0):
    return (width - native[0] if rear else native[0], native[1])


class M1MatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fn = functions()
        cls.frozen = {(b["project"], r["instance"]): r
                      for b in load("hardware/layout/h6-r2-placement-freeze.json")["boards"]
                      for r in b["placements"]}
        cls.ledger = load("hardware/ecad/generated/H2-R2-native-net-ledger.json")["rows"]
        cls.bindings = load("hardware/layout/generated/H6-R2-kicad-net-bindings.json")["projects"]

    def setUp(self):
        self.contract = json.loads(CONTRACT.read_text())

    def target(self, instance):
        project, reference, *_ = PARTS[instance]
        return self.fn["target_for_instance"](project, instance, reference, self.contract, {}, self.frozen)

    def footprint_pads(self, instance):
        path = LIBRARY / (PARTS[instance][-1] + ".kicad_mod")
        if not path.exists():
            self.skipTest("KiCad standard footprint library not installed")
        return pads(path.read_text(), self.fn["_balanced_form_end"])

    def test_exact_three_overrides_are_locked_and_use_native_anchors(self):
        for instance, (anchor, rotation) in EXPECTED_OVERRIDES.items():
            with self.subTest(instance=instance):
                row = self.contract["placement_overrides"][instance]
                self.assertEqual("rear-inner", row["frame"])
                self.assertEqual(anchor, row["anchor_mm"])
                self.assertNotIn("centre_mm", row)
                self.assertEqual(rotation, row["rotation_deg"])
                self.assertTrue(row["mechanical_locked"])
        self.assertNotIn("m1_ui_plug", self.contract["placement_overrides"])

    def test_override_wins_over_old_frozen_receptacle_pose(self):
        target = self.target("m1_rf_receptacle")
        self.assertEqual([37.5, 122.25], target["anchor"])
        self.assertEqual(180, target["rotation"])
        self.assertEqual("B.Cu", self.fn["target_side"](target))
        self.assertTrue(target["mechanical_locked"])
        self.assertTrue(target["rotation_locked"])
        self.assertNotIn("exact_anchor_nm", target)
        self.assertNotIn("frozen", target)

    def test_ui_plug_remains_at_unchanged_reviewed_native_datum(self):
        target = self.target("m1_ui_plug")
        self.assertEqual([42.5, 122.25], target["centre"])
        self.assertEqual(0, target["rotation"])
        self.assertEqual("B.Cu", self.fn["target_side"](target))
        self.assertTrue(target["frozen"])

    def test_exact_part_identity_and_primary_nominal_height_are_unchanged(self):
        devices = load("hardware/architecture/devices.json")["devices"]
        instances = load("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"]
        for instance, (project, reference, device_id, mpn, _) in PARTS.items():
            row = next(r for r in instances if r["instance"] == instance)
            self.assertEqual((project, reference, device_id),
                             (row["project"], row["reference"], row["device_id"]))
            self.assertEqual(mpn, devices[device_id]["mpn"])
            height_key = ("mated_height_with_fx8c_80s_sv5_mm" if instance == "m1_ui_plug"
                          else "mated_height_with_fx8c_80p_sv1_mm")
            # D31612_en p5: row FX8C-##P-SV1, column FX8C-##S-SV5.
            self.assertEqual(11, devices[device_id]["electrical_contract"][height_key])
        assembly = load("hardware/product-design/assembly-coordinate-model.json")
        self.assertEqual([80, 150], assembly["board_outline_mm"])
        self.assertEqual(11, assembly["stack"]["interboard_gap_mm"])
        self.assertIn("xw=80-x", assembly["frames"]["rear-outer"]["world_transform"])
        self.assertIn("yw=y", assembly["frames"]["rear-outer"]["world_transform"])

    def test_all_eighty_pairs_match_independent_signal_map_and_native_bindings(self):
        self.assertEqual({str(n) for n in range(1, 81)}, set(EXPECTED_NETS))
        self.assertEqual(71, sum(net is not None for net in EXPECTED_NETS.values()))
        for instance, (project, reference, *_rest) in PARTS.items():
            rows = [r for r in self.ledger if r["instance"] == instance]
            self.assertEqual(80, len(rows))
            self.assertEqual(EXPECTED_NETS, {r["physical"]: r["net"] for r in rows})
            self.assertEqual({"connected"}, {r["disposition"] for r in rows if r["net"]})
            text = (ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb").read_text()
            reference_at = text.index(f'(property "Reference" "{reference}"')
            start = text.rfind("(footprint ", 0, reference_at)
            form = text[start:self.fn["_balanced_form_end"](text, start)]
            actual = [p for p in pads(form, self.fn["_balanced_form_end"]) if p["number"]]
            self.assertEqual(80, len(actual))
            expected = {number: self.bindings[project]["canonical_to_kicad"][net] if net else ""
                        for number, net in EXPECTED_NETS.items()}
            self.assertEqual(expected, {p["number"]: p["net"] for p in actual})

    def test_all_numbered_lands_follow_opposed_polarized_rows(self):
        pad_maps = {}
        for instance in PARTS:
            numbered = [p for p in self.footprint_pads(instance) if p["number"]]
            self.assertEqual(80, len(numbered))
            self.assertEqual({"smd"}, {p["kind"] for p in numbered})
            pad_maps[instance] = {int(p["number"]): p for p in numbered}
        for n in range(1, 81):
            with self.subTest(pin=n):
                x = -11.7 + ((n - 1) // 2) * 0.6
                p = pad_maps["m1_ui_plug"][n]["xy"]
                s = pad_maps["m1_rf_receptacle"][n]["xy"]
                self.assertAlmostEqual(x, p[0])
                self.assertAlmostEqual(x, s[0])
                self.assertAlmostEqual(2.7 if n % 2 else -2.7, p[1])
                self.assertAlmostEqual(-2.85 if n % 2 else 2.85, s[1])
                ui = assembly_point(native_point(p, [42.5, 122.25], "B.Cu", 0), False)
                rf = assembly_point(native_point(s, [37.5, 122.25], "B.Cu", 180), True)
                self.assertAlmostEqual(ui[0], rf[0])
                self.assertAlmostEqual(-0.15 if n % 2 else 0.15, rf[1] - ui[1])
                self.assertEqual(ui[1] < 122.25, rf[1] < 122.25)

    def test_body_centres_match_only_after_real_rear_assembly_transform(self):
        rf = self.target("m1_rf_receptacle")
        ui_axis = assembly_point((42.5, 122.25), False)
        self.assertEqual(ui_axis, assembly_point(rf["anchor"], True))
        # Negative controls: legacy X/Y or simply comparing native axes fails.
        self.assertNotEqual(ui_axis, assembly_point((42.5, 122.5), True))
        self.assertNotEqual(ui_axis, assembly_point(rf["anchor"], False))

    def test_unrotated_receptacle_cannot_mate_same_numbered_corner(self):
        p1 = assembly_point(native_point((-11.7, 2.7), (42.5, 122.25), "B.Cu", 0), False)
        for wrong in (0, 90, 270):
            with self.subTest(rotation=wrong):
                s1 = assembly_point(native_point((-11.7, -2.85), (37.5, 122.25), "B.Cu", wrong), True)
                self.assertGreater(math.dist(p1, s1), 0.2)

    def test_two_unplated_locators_follow_primary_asymmetry_not_common_screw_axes(self):
        expected = {
            "m1_ui_plug": [((-14.1, 1.5), 1.1, (28.4, 120.75)),
                           ((14.1, 1.5), 0.7, (56.6, 120.75))],
            "m1_rf_receptacle": [((-14.1, -1.8), 1.1, (51.6, 120.45)),
                                 ((14.1, -1.8), 0.7, (23.4, 120.45))],
        }
        for instance, entries in expected.items():
            holes = sorted((p for p in self.footprint_pads(instance) if not p["number"]), key=lambda p: p["xy"][0])
            self.assertEqual(2, len(holes))
            anchor, angle = ([42.5, 122.25], 0) if instance == "m1_ui_plug" else ([37.5, 122.25], 180)
            for actual, (local, diameter, native) in zip(holes, entries):
                self.assertEqual("np_thru_hole", actual["kind"])
                self.assertEqual(list(local), actual["xy"])
                self.assertEqual(diameter, actual["drill"])
                self.assertEqual("", actual["net"])
                computed = native_point(actual["xy"], anchor, "B.Cu", angle)
                self.assertAlmostEqual(native[0], computed[0])
                self.assertAlmostEqual(native[1], computed[1])

    def test_xy_fix_does_not_claim_generic_step_is_exact_stack_evidence(self):
        reason = self.contract["placement_overrides"]["m1_rf_receptacle"]["reason"]
        self.assertIn("generic FX8 STEP", reason)
        self.assertIn("unresolved", reason)
        self.assertIn("H6.0.7", reason)

    def test_exact_three_courtyards_keep_the_full_policy_gap_to_current_neighbors(self):
        board = next(b for b in load("hardware/layout/generated/H6-R2-placement-audit.json")["boards"]
                     if b["project"] == "LESHY2-RF-R2")
        # Exact KiCad GetCourtyard bounds, including the native polygon/stroke
        # envelope; merely bounding GraphicalItems undercounts by 0.02 mm/side.
        half_sizes = {"m1_rf_receptacle": (15.845, 4.245),
                      "unit_bleeder": (1.525, 0.775),
                      "unit_output_cap": (1.025, 1.745)}
        proposed = {}
        for instance, (hx, hy) in half_sizes.items():
            x, y = self.contract["placement_overrides"][instance]["anchor_mm"]
            proposed[instance] = {"x": [x - hx, x + hx], "y": [y - hy, y + hy]}
        obstacles = {r["instance"]: r["courtyard_bbox_mm"] for r in board["placements"]
                     if r["side"] == "B.Cu" and r["instance"] not in proposed}
        obstacles.update(proposed)
        gap = self.contract["board"]["minimum_courtyard_gap_mm"]
        self.assertEqual(0.1, gap)
        for instance, rect in proposed.items():
            for owner, other in obstacles.items():
                if owner == instance:
                    continue
                with self.subTest(instance=instance, neighbor=owner):
                    self.assertFalse(self.fn["rectangles_overlap"](rect, other, gap))

    def test_previous_cap_candidate_fails_real_stroke_inclusive_gap(self):
        board = next(b for b in load("hardware/layout/generated/H6-R2-placement-audit.json")["boards"]
                     if b["project"] == "LESHY2-RF-R2")
        c78 = next(r["courtyard_bbox_mm"] for r in board["placements"]
                   if r["instance"] == "main_input_cap_1")
        old = {"x": [22.25 - 1.025, 22.25 + 1.025],
               "y": [128.5 - 1.745, 128.5 + 1.745]}
        self.assertTrue(self.fn["rectangles_overlap"](old, c78, 0.1))
        corrected = {"x": [22.3 - 1.025, 22.3 + 1.025], "y": old["y"]}
        self.assertFalse(self.fn["rectangles_overlap"](corrected, c78, 0.1))


if __name__ == "__main__":
    unittest.main()
