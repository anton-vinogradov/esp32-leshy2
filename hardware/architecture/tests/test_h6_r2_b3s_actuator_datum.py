"""Review-only B3S datum candidate: exact nominal drawing, not PCB release.

No KiCad installation is required. The 16 native poses are a named immutable
measurement snapshot, not a claim that future boards still have those poses.
"""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
REVIEW = ROOT / "hardware/layout/h6-r2-b3s-actuator-datum-review.json"
CANDIDATE = ROOT / "hardware/layout/candidates/B3S-1100P-ACTUATOR-DATUM-CANDIDATE.kicad_mod"
PRODUCTION = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/B3S-1100P.kicad_mod"
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_r2_b3s_actuator_datum as current_generator


def parse(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))

    def node(token):
        if token == "(":
            result = []
            for token in tokens:
                if token == ")":
                    return result
                result.append(node(token))
            raise ValueError("unterminated footprint")
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        return ast.literal_eval(token) if token.startswith('"') else token

    result = node(next(tokens))
    if next(tokens, None) is not None:
        raise ValueError("extra expression")
    return result


def children(node, key):
    return [x for x in node if isinstance(x, list) and x[0] == key]


def field(node, key):
    values = children(node, key)
    if len(values) != 1:
        raise ValueError(f"expected exactly one {key}")
    return values[0][1:]


def xy(node, key):
    return tuple(map(float, field(node, key)))


def f_point(anchor, angle, local):
    """Independent quarter-turn native F-side transform, not placement code."""
    x, y = local
    dx, dy = {0: (x, y), 90: (y, -x), 180: (-x, -y), 270: (-y, x)}[angle]
    return [round(anchor[0] + dx, 6), round(anchor[1] + dy, 6)]


def validate_pads(footprint):
    expected = {"4": (-3.98, -3.17), "3": (3.98, -3.17),
                "2": (-3.98, 1.33), "1": (3.98, 1.33), "5": (0, 3.17)}
    pads = children(footprint, "pad")
    if Counter(p[1] for p in pads) != Counter(expected.keys()):
        raise ValueError("exact five physical contacts required")
    for pad in pads:
        size = (1.3, 1.7) if pad[1] == "5" else (1.55, 1.3)
        if pad[2:4] != ["smd", "rect"] or xy(pad, "at") != expected[pad[1]]:
            raise ValueError("preserved physical pad pattern changed")
        if xy(pad, "size") != size or field(pad, "layers") != ["F.Cu", "F.Paste", "F.Mask"]:
            raise ValueError("preserved pad size/layers changed")


class B3SActuatorDatumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CANDIDATE.read_text()
        cls.fp = parse(cls.text)
        cls.review = json.loads(REVIEW.read_text())

    def test_candidate_not_bound_as_production(self):
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        self.assertIn('"OMRON B3S-1100P": "Leshy2_R2:B3S-1100P"', json.dumps(contract))
        self.assertEqual("B3S-1100P-ACTUATOR-DATUM-CANDIDATE", self.fp[1])
        self.assertIn("REVIEW CANDIDATE ONLY", self.text)
        self.assertFalse(self.review["production_release_authorized"])
        self.assertFalse(self.review["native_boards_modified_by_this_review"])

    def test_preserved_pad_geometry_and_numbering(self):
        validate_pads(self.fp)

    def test_production_pad_records_byte_identical(self):
        pad_lines = lambda text: [line for line in text.splitlines() if line.lstrip().startswith('(pad ')]
        self.assertEqual(pad_lines(PRODUCTION.read_text()), pad_lines(self.text))

    def test_reject_changed_ground_registration(self):
        bad = parse(self.text.replace('(at 0.000 3.170)', '(at 0.000 3.180)'))
        with self.assertRaisesRegex(ValueError, "pad pattern"):
            validate_pads(bad)

    def test_primary_nominal_land_pattern_rounding_is_explicit(self):
        pads = {p[1]: p for p in children(self.fp, "pad")}
        top, bottom = xy(pads["4"], "at")[1], xy(pads["2"], "at")[1]
        self.assertAlmostEqual(4.5, bottom - top)
        axis_y = (top + bottom) / 2
        self.assertAlmostEqual(-.92, axis_y)
        primary_column = ((9.5 + 6.4) / 2) / 2
        self.assertAlmostEqual(.005, xy(pads["3"], "at")[0] - primary_column)
        primary_ground_y = (3.25 + 4.95) / 2
        self.assertAlmostEqual(-.01, xy(pads["5"], "at")[1] - axis_y - primary_ground_y)

    def test_body_is_primary_6_by_6point6_about_actuator(self):
        body = next(r for r in children(self.fp, "fp_rect") if field(r, "layer") == ["F.Fab"])
        lo, hi = xy(body, "start"), xy(body, "end")
        self.assertAlmostEqual(6.0, hi[0] - lo[0])
        self.assertAlmostEqual(6.6, hi[1] - lo[1])
        self.assertEqual((0, -.92), tuple(round((a + b) / 2, 6) for a, b in zip(lo, hi)))
        self.assertEqual((-3, -4.22), lo)
        self.assertEqual((3, 2.38), hi)

    def test_plunger_has_exact_explicit_axis_and_nominal_diameter(self):
        circle, = children(self.fp, "fp_circle")
        self.assertEqual((0, -.92), xy(circle, "center"))
        self.assertEqual((1.65, -.92), xy(circle, "end"))
        self.assertEqual(["F.Fab"], field(circle, "layer"))
        prop = next(p for p in children(self.fp, "property") if p[1] == "Leshy2ActuatorAxisLocalMm")
        self.assertEqual("0,-0.92", prop[2])

    def test_courtyard_is_preserved_but_not_used_as_actuator(self):
        courtyard = next(r for r in children(self.fp, "fp_rect") if field(r, "layer") == ["F.CrtYd"])
        self.assertEqual((-5, -4.62), xy(courtyard, "start"))
        self.assertEqual((5, 4.28), xy(courtyard, "end"))
        courtyard_y = (-4.62 + 4.28) / 2
        self.assertAlmostEqual(-.75, -.92 - courtyard_y)

    def test_all_sixteen_snapshot_controls_have_unique_exact_identity(self):
        rows = self.review["instances"]
        self.assertEqual(16, len(rows))
        self.assertEqual(16, len({(r["board"], r["reference"]) for r in rows}))
        self.assertEqual({"LESHY2-UI-R2": 15, "LESHY2-RF-R2": 1}, dict(Counter(r["board"] for r in rows)))
        expected = {f"ui_switch_f{i}" for i in range(1, 9)} | {
            "ui_switch_back", "ui_switch_opt", "ui_dpad_up", "ui_dpad_down",
            "ui_dpad_left", "ui_dpad_right", "ui_dpad_ok", "ptt_switch"}
        self.assertEqual(expected, {r["instance"] for r in rows})

    def test_observed_and_computed_axes_use_actuator_not_fab_or_courtyard(self):
        for row in self.review["instances"]:
            with self.subTest(instance=row["instance"]):
                angle = row["rotation_deg"]
                self.assertEqual("F.Cu", row["side"])
                self.assertEqual(row["observed_actuator_mm"], f_point(row["native_anchor_mm"], angle, (0, -.92)))
                self.assertEqual(row["observed_courtyard_centre_mm"], f_point(row["native_anchor_mm"], angle, (0, -.17)))
                self.assertEqual(row["desired_axis_mm"], f_point(row["same_rotation_anchor_for_desired_axis_mm"], angle, (0, -.92)))
                self.assertEqual(row["axis_deviation_from_desired_mm"], [round(a-b, 6) for a,b in zip(row["observed_actuator_mm"], row["desired_axis_mm"])])

    def test_current_function_pairs_are_shifted_not_physically_mirrored(self):
        rows = {r["instance"]: r for r in self.review["instances"]}
        for n in range(1, 5):
            left, right = rows[f"ui_switch_f{n}"], rows[f"ui_switch_f{n+4}"]
            self.assertAlmostEqual(39.25, (left["observed_actuator_mm"][0] + right["observed_actuator_mm"][0]) / 2)
            self.assertEqual(90, right["rotation_deg"])

    def test_same_rotation_right_shift_is_rejected_for_real_copper_not_only_courtyard(self):
        for row in self.review["instances"]:
            if row["instance"] not in {f"ui_switch_f{i}" for i in range(5, 9)}:
                continue
            anchor_x = row["same_rotation_anchor_for_desired_axis_mm"][0]
            maximum_x = anchor_x + 3.17 + 1.7/2
            self.assertAlmostEqual(80.34, maximum_x)
            self.assertGreater(maximum_x, 80)
            self.assertEqual("rejected_at_same_rotation_pad5_outside_board", row["relocation_status"])
            alternative = row["alternative_geometry_only"]
            self.assertEqual(row["desired_axis_mm"], f_point(alternative["anchor_mm"], 270, (0, -.92)))
            self.assertEqual("not_accepted_no_collision_or_routing_qualification", alternative["status"])

    def test_ptt_reflection_and_datum_are_separate_corrections(self):
        row = next(r for r in self.review["instances"] if r["instance"] == "ptt_switch")
        self.assertEqual([7.5, 65.75], row["observed_actuator_mm"])
        self.assertEqual([72.5, 66.5], row["desired_axis_mm"])
        self.assertEqual([72.5, 67.42], row["same_rotation_anchor_for_desired_axis_mm"])

    def test_contradictory_ck_header_does_not_become_verified_switch_direction(self):
        item = self.review["independent_run_kill_review"]
        self.assertFalse(item["direction_verified"])
        self.assertIn("contradicted", item["derived_expected_orientation"]["basis"])
        self.assertEqual(["1", "2"], item["established"]["run_closed_pins"])
        self.assertEqual(["2", "3"], item["established"]["kill_closed_pins"])

    def test_candidate_hash_matches_own_evidence(self):
        self.assertEqual(self.review["candidate_sha256"], hashlib.sha256(CANDIDATE.read_bytes()).hexdigest())


class B3SCurrentSourceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text())
        cls.overrides = cls.contract["placement_overrides"]
        cls.fp = parse(PRODUCTION.read_text())
        # Independent reviewed native F-side anchors, not returned by a layout
        # generator. The accepted visible positions survive the datum change.
        cls.expected = {
            "ui_switch_f1": ((5.52, 22.5), 90, (4.6, 22.5)),
            "ui_switch_f2": ((5.52, 36), 90, (4.6, 36)),
            "ui_switch_f3": ((5.52, 49.5), 90, (4.6, 49.5)),
            "ui_switch_f4": ((5.52, 63), 90, (4.6, 63)),
            "ui_switch_f5": ((74.48, 22.5), 270, (75.4, 22.5)),
            "ui_switch_f6": ((74.48, 36), 270, (75.4, 36)),
            "ui_switch_f7": ((74.48, 49.5), 270, (75.4, 49.5)),
            "ui_switch_f8": ((74.48, 63), 270, (75.4, 63)),
            "ui_dpad_left": ((29.5, 133.32), 0, (29.5, 132.4)),
            "ui_dpad_ok": ((40, 133.32), 0, (40, 132.4)),
            "ui_dpad_right": ((50.5, 133.32), 0, (50.5, 132.4)),
            "ui_dpad_up": ((40, 122.82), 0, (40, 121.9)),
            "ui_dpad_down": ((40, 143.82), 0, (40, 142.9)),
            "ui_switch_back": ((14.3, 133.32), 0, (14.3, 132.4)),
            "ui_switch_opt": ((65.7, 133.32), 0, (65.7, 132.4)),
            "ptt_switch": ((72.1, 67.42), 0, (72.1, 66.5)),
        }

    def test_current_generator_owns_only_one_r2_footprint(self):
        outputs = current_generator.build()
        self.assertEqual({PRODUCTION}, set(outputs))
        self.assertEqual(PRODUCTION.read_text(), outputs[PRODUCTION])
        self.assertEqual((0, -.92), current_generator.ACTUATOR_AXIS_LOCAL_MM)
        self.assertEqual((6, 6.6), current_generator.BODY_SIZE_MM)

    def test_current_pad_records_keep_exact_electrical_pattern(self):
        validate_pads(self.fp)
        self.assertEqual(children(parse(CANDIDATE.read_text()), "pad"), children(self.fp, "pad"))

    def test_current_geometry_matches_reviewed_candidate_without_using_its_id(self):
        candidate = parse(CANDIDATE.read_text())
        self.assertEqual("B3S-1100P", self.fp[1])
        for tag in ("fp_rect", "fp_circle", "fp_line"):
            self.assertEqual(children(candidate, tag), children(self.fp, tag))
        properties = {p[1]:p[2] for p in children(self.fp, "property")}
        self.assertEqual("0,-0.92", properties["Leshy2ActuatorAxisLocalMm"])

    def test_all_sixteen_poses_are_explicit_mechanically_locked_anchors(self):
        self.assertEqual(16, len(self.expected))
        for name,(anchor,angle,axis) in self.expected.items():
            with self.subTest(instance=name):
                row=self.overrides[name]
                self.assertNotIn("centre_mm", row)
                self.assertEqual(list(anchor), row["anchor_mm"])
                self.assertEqual(angle, row["rotation_deg"])
                self.assertTrue(row["mechanical_locked"])
                self.assertEqual(list(axis), row["actuator_axis_native_mm"])
                self.assertEqual(list(axis), f_point(anchor,angle,(0,-.92)))
                self.assertEqual("rear-outer" if name=="ptt_switch" else "front-outer", row["frame"])

    def test_right_keys_physically_mirror_left_and_keep_all_copper_on_board(self):
        for n in range(1,5):
            left=self.overrides[f"ui_switch_f{n}"]
            right=self.overrides[f"ui_switch_f{n+4}"]
            self.assertAlmostEqual(80, left["actuator_axis_native_mm"][0]+right["actuator_axis_native_mm"][0])
            self.assertEqual(270,right["rotation_deg"])
            for row in (left,right):
                for pad in children(self.fp,"pad"):
                    x,y=f_point(row["anchor_mm"],row["rotation_deg"],xy(pad,"at"))
                    width,height=xy(pad,"size")
                    self.assertGreaterEqual(x-height/2,.25)
                    self.assertLessEqual(x+height/2,79.75)

    def test_ptt_offset_retains_copper_and_rejects_the_original_via_short(self):
        row=self.overrides["ptt_switch"]
        evidence=row["retained_copper_clearance"]
        self.assertEqual("CHARGER_SW1",evidence["net"])
        self.assertEqual([69.355,68.4],evidence["via_xy_mm"])
        self.assertEqual([72.5,67.42],evidence["rejected_anchor_mm"])
        self.assertEqual("2",evidence["ptt_pad"])
        # Via centre is level with the rectangular pad: exact gap is X only.
        pad_right=row["anchor_mm"][0]-3.98+1.55/2
        gap=69.355-.4/2-pad_right
        self.assertAlmostEqual(.26,gap)
        self.assertAlmostEqual(gap,evidence["nominal_copper_clearance_mm"])
        self.assertGreaterEqual(gap,evidence["reviewed_minimum_mm"])
        old_pad_right=72.5-3.98+1.55/2
        self.assertLess(69.355-.4/2-old_pad_right,0)


if __name__ == "__main__":
    unittest.main()
