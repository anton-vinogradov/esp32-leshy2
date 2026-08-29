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
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("Что ещё нельзя считать бесплатным", ru)
        self.assertIn("Murata GJM1555C1H101JB01D", ru)
        self.assertIn("TX2400-JW-5", ru)

    def test_complete_bom_is_ranked(self):
        self.assertEqual(len(self.result["rows"]), 210)
        mpns = [row["mpn"] for row in self.result["rows"]]
        self.assertEqual(len(mpns), len(set(mpns)))
        known = [
            row["line_burden_per_device_usd"]
            for row in self.result["rows"]
            if row["line_burden_per_device_usd"] is not None
        ]
        self.assertEqual(known, sorted(known, reverse=True))

    def test_cost_boundaries_are_explicit(self):
        summary = self.result["summary"]
        self.assertEqual(summary["quantity_100_priced_lines"], 201)
        self.assertEqual(summary["remaining_unpriced_base_lines"], 5)
        self.assertGreater(summary["planning_base_plus_post_pcba_usd_per_device"], 270)
        self.assertAlmostEqual(
            summary["planning_base_plus_post_pcba_usd_for_procurement_target"],
            summary["planning_base_plus_post_pcba_usd_per_device"],
            places=3,
        )
        self.assertEqual(summary["procurement_target_device_quantity"], 1)
        self.assertEqual(summary["historical_cost_capture_device_quantity"], 5)
        self.assertEqual(summary["historical_capture_unmatched_lines"], 27)
        self.assertAlmostEqual(
            summary["planning_base_plus_post_pcba_usd_for_ten_devices"],
            10 * summary["planning_base_plus_post_pcba_usd_per_device"],
            places=3,
        )
        self.assertGreater(summary["top_40_share_pct"], 75)
        self.assertGreater(
            summary["planning_plus_known_antenna_usd_per_device"], 400
        )
        display = next(
            row for row in self.result["rows"]
            if row["device_id"] == "eastrising_er_tft035ips_6_ctp"
        )
        self.assertEqual(display["line_burden_per_device_usd"], 14.91)
        self.assertEqual(display["planning_procurement_line_usd"], 14.91)

    def test_community_target_gap_is_not_hidden(self):
        summary = self.result["summary"]
        self.assertEqual(summary["base_bom_lines"], 208)
        self.assertEqual(summary["base_fitted_placements"], 1049)
        self.assertEqual(summary["community_complete_device_target_usd"], 150)
        self.assertEqual(summary["community_electronics_target_usd"], [108, 125])
        self.assertAlmostEqual(
            summary["paper_qualified_no_loss_savings_usd"], 24.5068, places=4
        )
        self.assertGreater(
            summary["remaining_gap_to_complete_device_target_before_pcb_pcba_enclosure_usd"],
            100,
        )
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("Контроль цели $150", ru)
        self.assertIn("1049", ru)
        self.assertIn("архитектур", ru)

    def test_trial_projection_keeps_fitted_quantity(self):
        by_id = {row["device_id"]: row for row in self.result["rows"]}
        buttons = by_id["omron_b3s_1100p"]
        self.assertEqual(buttons["quantity_per_device"], 16)
        self.assertEqual(buttons["quantity_procurement_target"], 16)
        self.assertEqual(buttons["quantity_historical_capture"], 80)
        self.assertEqual(buttons["quantity_ten_devices"], 160)
        self.assertAlmostEqual(
            buttons["planning_ten_devices_line_usd"],
            10 * buttons["line_burden_per_device_usd"],
        )
        self.assertAlmostEqual(
            buttons["planning_procurement_line_usd"],
            buttons["line_burden_per_device_usd"],
        )
        rp = by_id["rp2354b_a4"]
        self.assertEqual(2, rp["quantity_per_device"])
        self.assertEqual(2, rp["quantity_procurement_target"])
        self.assertEqual(10, rp["quantity_historical_capture"])
        self.assertEqual("C39843328", rp["jlcpcb_part"])

    def test_external_antennas_are_grouped_by_mpn(self):
        rows = self.result["antenna_rows"]
        mpns = [row["mpn"] for row in rows]
        self.assertEqual(len(mpns), len(set(mpns)))
        by_mpn = {row["mpn"]: row for row in rows}
        self.assertEqual(by_mpn["TX2400-JW-5"]["quantity"], 3)
        self.assertEqual(by_mpn["001-0012"]["quantity"], 2)
        self.assertEqual(
            self.result["summary"]["antenna_unpriced_positions"], 4
        )

    def test_unified_top_20_is_one_prototype_ranked_cost(self):
        rows = self.result["combined_top_20_rows"]
        self.assertEqual(len(rows), 20)
        costs = [row["group_cost_per_prototype_usd"] for row in rows]
        self.assertEqual(costs, sorted(costs, reverse=True))
        self.assertEqual(rows[0]["mpn"], "SMA-W100RX2")
        self.assertEqual(rows[0]["quantity_per_prototype"], 1)
        self.assertAlmostEqual(rows[0]["group_cost_per_prototype_usd"], 35.95)
        self.assertLess(max(costs), 40.0)
        self.assertGreater(self.result["summary"]["combined_top_20_share_pct"], 60)

        csv_text = MODULE.render_top20_csv(self.result)
        self.assertEqual(len(csv_text.strip().splitlines()), 21)
        self.assertIn("group_cost_per_prototype_usd", csv_text.splitlines()[0])

    def test_display_upper_candidate_has_margin(self):
        display = self.result["display_orientation_review"]
        fit = display["paper_fit"]
        self.assertEqual(display["current_upper_adapter_board_xy_mm"], [22.25, 1.0])
        self.assertIn("antenna edge", display["accepted_rule"])
        self.assertEqual(fit["same_face_collisions"], 0)
        self.assertGreater(fit["minimum_opposing_clearance_mm"], fit["required_minimum_mm"])
        self.assertEqual(fit["gpio_change"], 0)
        self.assertEqual(fit["bom_change_usd"], 0.0)

    def test_stocked_candidate_policy_is_conservative(self):
        policy = self.result["accepted_cost_reduction_policy"]
        self.assertIn("pre-order", policy["primary_target"])
        self.assertIn("exact or no worse", policy["stocked_replacement_rule"])
        self.assertIn("through-board soldered load path", policy["antenna_mechanics_rule"])

        candidates = {
            row["candidate_mpn"]: row
            for row in self.result["current_stocked_candidate_checks"]
        }
        self.assertEqual(
            candidates["Nexperia 74LVC2G126DP,125"]["status"],
            "accepted_stocked_exact_family_package_variant",
        )
        self.assertEqual(
            candidates["YAGEO CC0402KRX7R9BB104"]["status"],
            "accepted_stocked_exact_parametric_replacement",
        )
        self.assertEqual(
            candidates["OMRON B3S-1000P"]["status"],
            "not_accepted_missing_ground_terminal",
        )
        self.assertEqual(
            candidates["HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5"]["status"],
            "rejected_wrong_board_normal_orientation",
        )
        self.assertEqual(
            candidates["DreamLNK SMA-KWE902 / SMA-KWE901"]["status"],
            "qualified_pending_full_5_plus_5_placement_and_assembly_gate",
        )
        self.assertEqual(
            candidates["Hirose DF40C(2.0)-40DS-0.4V(51)"]["jlcpcb_part"],
            "C597934",
        )
        self.assertEqual(
            candidates["Texas Instruments CSD87313DMS"]["jlcpcb_part"],
            "C2863848",
        )
        self.assertEqual(
            candidates["Vishay TSOP75238TR"]["status"],
            "accepted_stocked_exact_tape_presentation_variant_with_placement_gate",
        )
        self.assertIn("CPL rotation", candidates["Vishay TSOP75238TR"]["why"])
        self.assertEqual(
            candidates["Murata LQW15AN56NG00D"]["jlcpcb_part"],
            "C167482",
        )
        self.assertEqual(
            candidates["Analog Devices AD8314ARMZ-REEL"]["status"],
            "qualified_same_device_pending_six_body_placement_gate",
        )
        self.assertEqual(
            candidates["Analog Devices AD8314ARMZ-REEL"]["jlcpcb_part"],
            "C652687",
        )

    def test_cost_queue_does_not_present_open_work_as_finished(self):
        lanes = {
            row["id"]: row["queue_status"]
            for row in self.result["optimization_lanes"]
        }
        self.assertEqual(lanes["external-antenna-kit"], "active")
        self.assertEqual(lanes["factory-preorder-penalty"], "accepted")
        self.assertEqual(lanes["main-rf-mechanics"], "active")
        self.assertEqual(lanes["native-rf-jumpers"], "accepted")
        self.assertEqual(lanes["rf-evidence-detectors"], "active")
        self.assertEqual(lanes["ordinary-controls"], "waiting")
        self.assertEqual(lanes["battery-holder"], "waiting")
        self.assertEqual(lanes["service-headers"], "waiting")
        self.assertEqual(lanes["display-production-route"], "accepted")


if __name__ == "__main__":
    unittest.main()
