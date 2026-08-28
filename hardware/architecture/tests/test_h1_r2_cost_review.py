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
        self.assertAlmostEqual(
            summary["planning_base_plus_post_pcba_usd_for_trial"],
            summary["planning_base_plus_post_pcba_usd_per_device"] * 5,
            places=3,
        )
        self.assertEqual(summary["trial_unmatched_lines"], 32)

    def test_trial_projection_keeps_fitted_quantity(self):
        by_id = {row["device_id"]: row for row in self.result["rows"]}
        buttons = by_id["omron_b3s_1100p"]
        self.assertEqual(buttons["quantity_per_device"], 16)
        self.assertEqual(buttons["quantity_trial"], 80)
        self.assertAlmostEqual(
            buttons["planning_trial_line_usd"],
            buttons["line_burden_per_device_usd"] * 5,
        )

    def test_display_upper_candidate_has_margin(self):
        display = self.result["display_orientation_review"]
        fit = display["paper_fit"]
        self.assertEqual(display["current_upper_adapter_board_xy_mm"], [24.75, 1.0])
        self.assertIn("antenna edge", display["accepted_rule"])
        self.assertEqual(fit["same_face_collisions"], 0)
        self.assertGreater(fit["minimum_opposing_clearance_mm"], fit["required_minimum_mm"])
        self.assertEqual(fit["gpio_change"], 0)
        self.assertEqual(fit["bom_change_usd"], 0.0)

    def test_stocked_candidate_policy_is_conservative(self):
        policy = self.result["accepted_cost_reduction_policy"]
        self.assertIn("pre-order", policy["primary_target"])
        self.assertIn("exact or no worse", policy["stocked_replacement_rule"])
        self.assertIn("shared protective frame", policy["antenna_mechanics_rule"])

        candidates = {
            row["candidate_mpn"]: row
            for row in self.result["current_stocked_candidate_checks"]
        }
        self.assertEqual(
            candidates["Nexperia 74LVC2G126DP,125"]["status"],
            "qualified_stocked_candidate_for_next_atomic_replacement",
        )
        self.assertEqual(
            candidates["OMRON B3S-1000P"]["status"],
            "not_accepted_missing_ground_terminal",
        )
        self.assertEqual(
            candidates["HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5"]["status"],
            "leading_stocked_pair_pending_controlled_drawing",
        )


if __name__ == "__main__":
    unittest.main()
