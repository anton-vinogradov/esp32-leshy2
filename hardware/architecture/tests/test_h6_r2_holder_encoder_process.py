"""Independent geometry checks; NOT component solder-joint/production acceptance.

Alps EC11E catalog update2510 p2 Drawing2 (exact MPN listed on p1):
https://tech.alpsalpine.com/cms.media/product_catalog_ec_01_ec11e_en_611f078659.pdf
JLC finished-hole/slot capabilities, checked2026-09-07:
https://jlcpcb.com/capabilities/pcb-capabilities
Keystone-authored1048P Rev A individual drawing, not a new Rev B claim:
https://file.aichiplink.com/r/datasheets/keystoneelectronics-1048p-datasheets-1060.pdf
"""

from fractions import Fraction as F
import importlib.util
import itertools
import json
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "hardware/layout/h6-r2-holder-encoder-geometry-evidence.json"
CANDIDATE = ROOT / "hardware/layout/candidates/EC11E18244AU-JLC-OVAL-CANDIDATE.kicad_mod"
_spec = importlib.util.spec_from_file_location(
    "encoder_dimension_fixture", Path(__file__).with_name("test_h6_r2_encoder_geometry.py"))
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)
parse, children, field = _fixture.parse, _fixture.children, _fixture.field


def inside_stadium(x, y, width, length):
    """Exact rational comparison with an aligned, closed vertical obround."""
    x, y, width, length = (F(str(v)) for v in (x, y, width, length))
    if width <= 0 or length < width:
        raise ValueError("requires positive vertical stadium dimensions")
    excess_y = max(abs(y) - (length - width) / 2, F(0))
    return x*x + excess_y*excess_y <= (width / 2)**2


def reference_corners_inside(width, length, centre_allowance):
    # Expected1.6x2.7 is independently transcribed from Alps' upper limits,
    # not read back from the proposed oval or generated evidence arithmetic.
    for sx, sy, tx, ty in itertools.product((-1, 1), repeat=4):
        x = sx*F("0.8") + tx*F(str(centre_allowance))
        y = sy*F("1.35") + ty*F(str(centre_allowance))
        if not inside_stadium(x, y, width, length):
            return False
    return True


class HolderEncoderProcessEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads(EVIDENCE.read_text())
        self.encoder, self.holder = self.evidence["devices"]
        self.process = self.encoder["process_candidate"]
        self.node = parse(CANDIDATE.read_text())

    def test_exact_centres_and_seven_contacts_are_not_changed_by_process_candidate(self):
        pads = children(self.node, "pad")
        self.assertEqual(7, len(pads))
        self.assertTrue(all(p[2] == "thru_hole" for p in pads))
        expected = {"A": [-2.5, 7.5], "B": [2.5, 7.5], "C": [0, 7.5],
                    "D": [-2.5, -7], "E": [2.5, -7]}
        self.assertEqual(sorted([*expected, "MP", "MP"]), sorted(p[1] for p in pads))
        for name, xy in expected.items():
            p, = [p for p in pads if p[1] == name]
            self.assertEqual(xy, list(map(float, field(p, "at"))))
            self.assertEqual(["1.05"], field(p, "drill"))
            self.assertEqual(["2", "2"], field(p, "size"))
        mounts = [p for p in pads if p[1] == "MP"]
        self.assertEqual([[-6.25, 0], [6.25, 0]], sorted(
            list(map(float, field(p, "at"))) for p in mounts))
        for p in mounts:
            self.assertEqual(["oval", "2.2", "4.8"], field(p, "drill"))
            self.assertEqual(["3.2", "5.8"], field(p, "size"))
        self.assertFalse(children(self.node, "model"))

    def test_finished_slot_and_relative_centre_all_endpoint_corners(self):
        self.assertEqual([1.6, 2.7], self.process["manufacturer_reference_rectangle_max_mm"])
        self.assertEqual([2.2, 4.8], self.process["nominal_plated_oval_mm"])
        self.assertEqual({"minus": .08, "plus": .13}, self.process["finished_size_tolerance_mm"])
        self.assertEqual(.05, self.process["factory_hole_position_allowance_each_axis_mm"])
        self.assertEqual(.1, self.process["additional_registration_allowance_each_axis_mm"])
        self.assertEqual(.15, self.process["total_relative_centre_allowance_each_axis_mm"])
        for w, length in itertools.product((F("2.12"), F("2.33")),
                                            (F("4.72"), F("4.93"))):
            with self.subTest(width=w, length=length):
                self.assertTrue(reference_corners_inside(w, length, F(".15")))
        self.assertEqual(F(".9425"), F(".95")**2 + F(".20")**2)
        self.assertEqual(F("1.1236"), F("1.06")**2)
        actual_margin = 1.06 - math.sqrt(.9425)
        self.assertGreater(actual_margin, .0891)
        self.assertLess(actual_margin, .0892)
        self.assertEqual(.0891, self.process["minimum_corner_radial_margin_mm_rounded_down"])

    def test_reference_interior_samples_and_every_finished_size_corner(self):
        for sx, sy in itertools.product((F(-1), F("-.5"), F(0), F(".5"), F(1)), repeat=2):
            for tx, ty in itertools.product((F("-.15"), F(".15")), repeat=2):
                self.assertTrue(inside_stadium(sx*F(".8") + tx,
                                               sy*F("1.35") + ty, "2.12", "4.72"))

    def test_old_equal_bbox_obround_is_not_rectangle_inclusion(self):
        self.assertFalse(reference_corners_inside("1.6", "2.7", 0))
        self.assertFalse(reference_corners_inside("1.52", "2.62", ".05"))

    def test_ignored_registration_or_fabrication_tolerance_cannot_appear_safe(self):
        # The smaller variant is adequate only without the additional0.10 budget.
        self.assertTrue(reference_corners_inside("1.92", "4.32", ".05"))
        self.assertFalse(reference_corners_inside("1.92", "4.32", ".15"))
        # A different nominal oval passes but its finished lower-size corner fails.
        self.assertTrue(reference_corners_inside("1.8", "4.2", ".05"))
        self.assertFalse(reference_corners_inside("1.72", "4.12", ".05"))

    def test_slot_ratio_and_annulus_do_not_borrow_nominal_hole_clearance(self):
        self.assertGreaterEqual(F("4.8"), 2*F("2.2"))
        self.assertGreaterEqual(F("4.72"), 2*F("2.33"))
        annulus = .5 - .13/2 - math.sqrt(2)*.05
        self.assertGreater(annulus, .3642)
        self.assertLess(annulus, .3643)
        self.assertGreater(annulus, .254)  # JLC even2oz recommended PTH annulus
        self.assertEqual(.3642, self.process["conservative_copper_annulus_min_mm_rounded_down"])

    def test_signal_hole_literal_interval_requires_specific_precision_process(self):
        lower, upper = F("1.0"), F("1.1")
        self.assertEqual((lower, upper), (F("1.05")-F(".05"), F("1.05")+F(".05")))
        # Ordinary process requires nominal>=1.08 AND nominal<=.97: impossible.
        self.assertGreater(lower + F(".08"), upper - F(".13"))
        signal = self.process["signal_holes"]
        self.assertEqual(1.05, signal["nominal_mm"])
        self.assertEqual([1, 1.1], signal["required_finished_interval_mm"])
        self.assertIn("multilayer ENIG", signal["process"])
        self.assertIn("not yet adopted", signal["fabrication_note_required"])

    def test_insertion_proof_is_not_a_release_or_strength_claim(self):
        self.assertFalse(self.evidence["fabrication_ready"])
        self.assertFalse(self.process["accepted_for_production"])
        self.assertFalse(self.process["binding_changed"])
        self.assertIn("solder_joint_and_native_integration_open", self.process["status"])
        self.assertIn("NOT ACCEPTED FOR PRODUCTION", field(self.node, "descr")[0])
        self.assertIn("exceeds Alps aperture maxima", field(self.node, "descr")[0])
        contract = (ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text()
        self.assertNotIn(self.node[1], contract)
        self.assertNotIn("lug_thickness_mm", self.process)

    def test_holder_recovered_locator_is_relative_to_named_edge_not_unlocated(self):
        d = self.holder["individual_drawing_review"]
        self.assertEqual("A", d["revision"])
        locator = d["small_locator_offset_from_right_smt_outer_edge"]
        self.assertEqual(".323", locator["inch_label"])
        self.assertEqual(8.22, locator["metric_label_mm"])
        self.assertIn("right outside edge", locator["direction"])
        self.assertEqual(F("8.2042"), F(".323")*F("25.4"))
        self.assertEqual([7.34, 6.35], d["four_smt_land_minimum_size_mm"])
        self.assertEqual(14.859, d["derived_body_height_mm"])
        self.assertEqual(F("14.859"), F(".585")*F("25.4"))
        reviewed = [e for e in self.holder["evidence"] if e.get("visually_reviewed")]
        self.assertEqual(1, len(reviewed))
        self.assertEqual("6135bff212f9eab9ed8158febcbbd0d18b9479caac384a7f51f2818d1328e26b",
                         reviewed[0]["pdf_sha256"])

    def test_holder_symmetry_is_not_promoted_to_dimensioned_drilling(self):
        d = self.holder["individual_drawing_review"]
        self.assertIsNone(d["full_body_registered_hole_coordinate_set"])
        reg = d["plausible_centred_registration_not_accepted"]
        self.assertFalse(reg["drilling_authorized"])
        self.assertEqual([34.78, 17.505], reg["small_locator_centre_mm"])
        self.assertEqual(F("34.78"), F(86)/2-F("8.22"))
        self.assertEqual(F("17.505"), F("19.11")/2+F("7.95"))
        self.assertFalse(self.holder["candidate_created"])
        self.assertIsNone(self.holder["dimensioned_catalog_constraints"][
            "small_locator_longitudinal_coordinate_mm"])
        self.assertFalse(self.holder["evidence"][-1]["visually_reviewed"])
        self.assertIn("Rev B", self.holder["unresolved"][0])


if __name__ == "__main__":
    unittest.main()
