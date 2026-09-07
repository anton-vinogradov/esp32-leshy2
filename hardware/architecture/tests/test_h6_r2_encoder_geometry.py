"""Dimension fixture, NOT a release test for the unqualified EC11 slot shape.

Independent numerical expectations from Alps EC11E catalog update2510 p2,
Drawing No.2 (exact EC11E18244AU listed on p1), checked2026-09-07:
https://tech.alpsalpine.com/cms.media/product_catalog_ec_01_ec11e_en_611f078659.pdf
The illustration and mounting-side pattern both put A/C/B below the shaft.
No pixel measurement or unrelated EC11E09444A8 locating holes are imported.
"""

import copy
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "hardware/layout/candidates/EC11E18244AU-UNQUALIFIED-SLOTS.kicad_mod"
EVIDENCE = ROOT / "hardware/layout/h6-r2-holder-encoder-geometry-evidence.json"
SIGNALS = {"A": [-2.5, 7.5], "C": [0, 7.5], "B": [2.5, 7.5],
           "D": [-2.5, -7], "E": [2.5, -7]}


def parse(source):
    stack, roots = [], []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', source):
        if token == "(":
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError("unbalanced close")
            stack.pop()
        else:
            if not stack:
                raise ValueError("atom outside expression")
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or len(roots) != 1:
        raise ValueError("unbalanced or multiple roots")
    return roots[0]


def children(node, kind):
    return [p for p in node[1:] if isinstance(p, list) and p[0] == kind]


def field(node, kind):
    matches = children(node, kind)
    if len(matches) != 1:
        raise ValueError(f"expected one {kind}")
    return matches[0][1:]


class EncoderGeometryCandidateTests(unittest.TestCase):
    def setUp(self):
        self.node = parse(CANDIDATE.read_text())
        self.evidence = json.loads(EVIDENCE.read_text())
        self.encoder, self.holder = self.evidence["devices"]

    def assert_centres(self, node):
        pads = children(node, "pad")
        self.assertEqual(7, len(pads))
        self.assertTrue(all(p[2] == "thru_hole" for p in pads))
        self.assertEqual(sorted([*SIGNALS, "MP", "MP"]), sorted(p[1] for p in pads))
        for name, xy in SIGNALS.items():
            actual = [p for p in pads if p[1] == name]
            self.assertEqual(1, len(actual))
            self.assertEqual(xy, list(map(float, field(actual[0], "at"))))
        mounts = [list(map(float, field(p, "at"))) for p in pads if p[1] == "MP"]
        self.assertEqual([[-6.25, 0], [6.25, 0]], sorted(mounts))

    def test_all_seven_centres_match_exact_drawing_without_extra_locators(self):
        self.assert_centres(self.node)
        self.assertEqual(["F.Cu"], field(self.node, "layer"))
        self.assertEqual(["through_hole"], field(self.node, "attr"))
        self.assertEqual([], children(self.node, "model"), "do not borrow another MPN's STEP")

    def test_primary_fixture_is_independent_of_engineering_pad_allowances(self):
        f = self.encoder["dimension_fixture"]
        self.assertEqual(SIGNALS, f["signal_centres_mm"])
        self.assertEqual([[-6.25, 0], [6.25, 0]], f["mounting_lug_centres_mm"])
        self.assertEqual({"nominal": 12.5, "minus": .05, "plus": .05}, f["mounting_lug_pitch_mm"])
        self.assertEqual({"nominal": 1, "minus": 0, "plus": .1}, f["signal_hole_diameter_mm"])
        self.assertEqual({"nominal": 1.5, "minus": 0, "plus": .1}, f["mounting_aperture_width_mm"])
        self.assertEqual({"nominal": 2.6, "minus": 0, "plus": .1}, f["mounting_aperture_height_mm"])
        for pad in children(self.node, "pad"):
            self.assertEqual(["*.Cu", "*.Mask"], field(pad, "layers"))
            if pad[1] == "MP":
                self.assertEqual(["oval", "1.6", "2.7"], field(pad, "drill"))
                self.assertEqual([2.6, 3.7], list(map(float, field(pad, "size"))))
            else:
                self.assertEqual(["1.1"], field(pad, "drill"))
                self.assertEqual([2, 2], list(map(float, field(pad, "size"))))

    def test_candidate_is_not_a_production_binding_or_a_slot_qualification(self):
        c = self.encoder["candidate"]
        self.assertFalse(c["accepted_for_production"])
        self.assertFalse(c["binding_changed"])
        self.assertEqual("open", c["slot_profile_qualification"])
        self.assertFalse(self.evidence["fabrication_ready"])
        self.assertIn("NOT ACCEPTED FOR PRODUCTION", field(self.node, "descr")[0])
        self.assertIn("UNQUALIFIED", self.node[1])
        contract = (ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text()
        self.assertNotIn(self.node[1], contract)

    def test_old_eleven_point_two_pitch_fails_the_dimension_fixture(self):
        node = copy.deepcopy(self.node)
        mounts = [p for p in children(node, "pad") if p[1] == "MP"]
        children(mounts[0], "at")[0][1] = "-5.6"
        children(mounts[1], "at")[0][1] = "5.6"
        with self.assertRaises(AssertionError):
            self.assert_centres(node)

    def test_mirrored_a_b_and_extra_locating_hole_are_rejected(self):
        for mutation in ("mirror", "extra_locator"):
            node = copy.deepcopy(self.node)
            if mutation == "mirror":
                for p in children(node, "pad"):
                    at = children(p, "at")[0]
                    at[1] = str(-float(at[1]))
            else:
                node.append(["pad", "", "np_thru_hole", "circle", ["at", "3", "2.5"]])
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                self.assert_centres(node)

    def test_holder_unlocated_hole_is_not_turned_into_guessed_drilling(self):
        h = self.holder
        self.assertFalse(h["candidate_created"])
        self.assertIsNone(h["dimensioned_catalog_constraints"]["small_locator_longitudinal_coordinate_mm"])
        self.assertIsNone(h["dimensioned_catalog_constraints"]["full_body_registered_hole_coordinate_set"])
        self.assertEqual([7.3, 6.4], h["dimensioned_catalog_constraints"]["four_smt_land_minimum_size_mm"])
        self.assertTrue(h["unresolved"])
        self.assertFalse(h["evidence"][-1]["visually_reviewed"])


if __name__ == "__main__":
    unittest.main()
