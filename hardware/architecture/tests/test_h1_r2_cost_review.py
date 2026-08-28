import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_r2_cost_review.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_cost_review", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class H1R2CostReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.build(*MODULE.load())

    def test_review_passes(self):
        self.assertEqual(self.result["errors"], [])
        self.assertEqual(self.result["status"], "pass_review_with_open_cost_actions")

    def test_complete_bom_is_ranked(self):
        self.assertEqual(len(self.result["rows"]), 210)
        known = [
            row["line_burden_per_device_usd"]
            for row in self.result["rows"]
            if row["line_burden_per_device_usd"] is not None
        ]
        self.assertEqual(known, sorted(known, reverse=True))

    def test_cost_boundaries_are_explicit(self):
        summary = self.result["summary"]
        self.assertEqual(summary["quantity_100_priced_lines"], 198)
        self.assertEqual(summary["remaining_unpriced_base_lines"], 5)
        self.assertGreater(summary["planning_base_plus_post_pcba_usd_per_device"], 300)
        self.assertEqual(summary["trial_unmatched_lines"], 32)

    def test_display_upper_candidate_has_margin(self):
        fit = self.result["display_orientation_review"]["paper_fit"]
        self.assertEqual(fit["same_face_collisions"], 0)
        self.assertGreater(fit["minimum_opposing_clearance_mm"], fit["required_minimum_mm"])
        self.assertEqual(fit["gpio_change"], 0)
        self.assertEqual(fit["bom_change_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
