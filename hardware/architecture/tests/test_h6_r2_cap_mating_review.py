"""Keep uncertain Cap maps distinguishable from accepted production contacts."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class CapMatingReviewTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((ROOT / "hardware/layout/h6-r2-cap-mating-review.json").read_text())

    def test_four_conditional_maps_are_bijective_but_none_is_selected(self):
        self.assertFalse(self.review["production_map_modified"])
        self.assertEqual("unresolved_mating_view_handedness", self.review["status"])
        maps = self.review["conditional_maps_not_approved"]
        pose = self.review["selected_connector"]["reviewed_native_pose"]
        observed = []
        for name, candidate in maps.items():
            if name == "coordinate_rule":
                continue
            mapping = candidate["logical_to_pad"]
            observed.append(tuple(mapping))
            self.assertEqual(list(range(1, 15)), sorted(mapping))
            for edge in ("upper", "lower"):
                logical = candidate[f"{edge}_native_cavity_row_logical_contacts"]
                pads = pose[f"{edge}_row_pad_numbers_left_to_right"]
                self.assertEqual(pads, [mapping[n-1] for n in logical])
        self.assertEqual(4, len(set(observed)))
        self.assertNotIn(tuple(range(1, 15)), observed)

    def test_physical_tail_and_mating_rows_are_not_interchanged(self):
        pose = self.review["selected_connector"]["reviewed_native_pose"]
        self.assertAlmostEqual(7.62, pose["tail_row_y_mm"][1] - pose["tail_row_y_mm"][0])
        self.assertAlmostEqual(2.54, pose["mating_cavity_row_y_mm"][1] - pose["mating_cavity_row_y_mm"][0])
        self.assertEqual([1, 3, 5, 7, 9, 11, 13], pose["upper_row_pad_numbers_left_to_right"])
        self.assertEqual([2, 4, 6, 8, 10, 12, 14], pose["lower_row_pad_numbers_left_to_right"])

    def test_release_plan_exposes_the_mating_blocker_without_authorizing_an_order(self):
        plan = json.loads((ROOT / "hardware/verification/h6-layout-release-plan.json").read_text())
        self.assertFalse(plan["authorization"]["fabrication"])
        self.assertFalse(plan["authorization"]["purchase"])
        finding = next(r for r in plan["current_evidence"]["reopened_interface_findings"]
                       if r["id"] == "H6-CAP-PHYSICAL-MATING")
        self.assertEqual("hardware/layout/h6-r2-cap-mating-review.json", finding["evidence"])
        self.assertTrue(any("reopened_interface_findings" in r
                            for r in plan["current_evidence"]["remaining_before_substep_exit"]))


if __name__ == "__main__":
    unittest.main()
