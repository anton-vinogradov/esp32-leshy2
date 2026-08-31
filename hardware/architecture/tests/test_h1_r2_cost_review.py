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

    def test_accepted_all_in_one_target_gap_is_not_hidden(self):
        summary = self.result["summary"]
        self.assertEqual(summary["base_bom_lines"], 209)
        self.assertGreater(summary["base_fitted_placements"], 1049)
        self.assertEqual(summary["community_complete_device_target_usd"], 260)
        self.assertEqual(summary["community_electronics_target_usd"], [189, 216])
        self.assertAlmostEqual(
            summary["paper_qualified_no_loss_savings_usd"], 10.4192, places=4
        )
        self.assertGreater(
            summary["additional_savings_to_electronics_target_usd"][0],
            35,
        )
        self.assertLess(summary["pre_pcba_margin_to_complete_ceiling_usd"], 0)
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("Принятая ценовая граница all-in-one", ru)
        self.assertIn("отдельный `Core` сейчас не проектируется", ru)
        self.assertIn("1096", ru)
        self.assertIn("пересинтез", ru)

    def test_cost_feasibility_separates_all_in_one_from_modular_entry(self):
        feasibility = self.result["cost_feasibility"]
        all_in_one = feasibility["same_all_in_one_result"]
        modular = feasibility["modular_entry_result"]
        accepted = feasibility["accepted_strategy"]
        self.assertGreaterEqual(all_in_one["electronics_working_range_usd"][0], 180)
        self.assertGreater(all_in_one["repeatable_complete_base_working_range_usd"][0], 200)
        self.assertLessEqual(modular["repeatable_complete_target_usd"][0], 150)
        self.assertGreaterEqual(modular["repeatable_complete_target_usd"][1], 150)
        self.assertEqual(modular["status"], "deferred_post_evt1_no_current_hardware_variant")
        self.assertEqual(accepted["current_repeatable_complete_target_usd"], [220, 260])
        self.assertIn("do not create a separate Core", accepted["core_rule"])
        savings = {
            row["id"]: row for row in feasibility["working_architecture_savings"]
        }
        self.assertEqual(
            savings["controls-holder-recovery"]["status"],
            "reviewed_no_loss_saving_rejected",
        )
        self.assertEqual(
            savings["controls-holder-recovery"]["working_savings_usd"],
            [0, 0],
        )
        self.assertTrue(all(
            row["status"] == "analysis_only_not_qualified"
            for key, row in savings.items()
            if key != "controls-holder-recovery"
        ))
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("Почему ESP32-DIV заметно дешевле", ru)
        self.assertIn("Те же встроенные пользовательские функции", ru)
        self.assertIn("Модульная community-база", ru)

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
        headers = by_id["samtec_ftsh_105_01_l_dv_k_p_tr"]
        self.assertEqual(4, headers["quantity_per_device"])
        self.assertEqual(20, headers["quantity_historical_capture"])
        detector = by_id["adi_ad8314armz_reel"]
        self.assertEqual("adi_ad8314acpz_rl7", detector["source_device_id"])
        self.assertEqual("C652687", detector["jlcpcb_part"])
        self.assertEqual(6, detector["quantity_per_device"])
        self.assertAlmostEqual(11.6388, detector["line_burden_per_device_usd"])
        self.assertIn("MOQ 4", detector["historical_capture_route"])

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

    def test_every_current_top_20_group_has_a_mass_market_verdict(self):
        ranked = self.result["combined_top_20_rows"]
        audit = self.result["top_20_mass_market_audit"]
        self.assertEqual(len(audit), 20)
        self.assertEqual(
            {row["mpn"] for row in ranked},
            {row["current_mpn"] for row in audit},
        )
        self.assertEqual(
            self.result["summary"]["top_20_mass_market_retained_groups"], 20
        )
        self.assertEqual(
            self.result["summary"]["top_20_qualification_candidate_groups"], 0
        )
        self.assertEqual(
            self.result["summary"]["top_20_rejected_candidate_groups"], 6
        )
        self.assertAlmostEqual(
            self.result["summary"]["top_20_unaccepted_paper_saving_usd"],
            89.1273,
            places=4,
        )
        self.assertAlmostEqual(
            self.result["summary"]["top_20_rejected_paper_saving_usd"],
            89.1273,
            places=4,
        )
        self.assertTrue(all(row["checked_on"] == "2026-08-29" for row in audit))
        rejected = [row for row in audit if "candidate_rejected" in row["verdict"]]
        self.assertEqual(len(rejected), 6)
        self.assertTrue(all(row["decision_on"] == "2026-08-30" for row in rejected))
        self.assertEqual(
            self.result["top_20_user_decision"]["decision"],
            "retain_all_current_groups",
        )
        self.assertIn(
            "two separate ANT-433-CW-QW-SMA",
            self.result["top_20_user_decision"]["quantity_rule"],
        )
        market_csv = MODULE.render_top20_market_csv(self.result)
        self.assertEqual(len(market_csv.strip().splitlines()), 21)
        self.assertIn("functional_delta", market_csv.splitlines()[0])

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
            "rejected_current_5_plus_5_mechanical_envelope_and_factory_route",
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
            "accepted_same_device_msop_explicit_factory_route_and_physical_fit",
        )
        self.assertEqual(
            candidates["Analog Devices AD8314ARMZ-REEL"]["jlcpcb_part"],
            "C652687",
        )
        self.assertEqual(
            candidates["Hirose U.FL-R-SMT-1(80)"]["status"],
            "accepted_stocked_exact_packaging_variant",
        )
        self.assertEqual(
            candidates["Hirose U.FL-R-SMT-1(80)"]["jlcpcb_part"],
            "C88374",
        )
        self.assertEqual(
            candidates["MYOUNG BH-18650-B1BA002"]["status"],
            "not_accepted_single_cell_and_protected_length_unproven",
        )
        self.assertEqual(
            candidates["Tag-Connect TC2050-IDC board footprint"]["status"],
            "not_accepted_for_exact_one_evt1_cost_and_debug_ergonomics",
        )

    def test_cost_queue_does_not_present_open_work_as_finished(self):
        lanes = {
            row["id"]: row["queue_status"]
            for row in self.result["optimization_lanes"]
        }
        self.assertEqual(lanes["external-antenna-kit"], "active")
        self.assertEqual(lanes["factory-preorder-penalty"], "accepted")
        self.assertEqual(lanes["main-rf-mechanics"], "accepted")
        self.assertEqual(lanes["native-rf-jumpers"], "accepted")
        self.assertEqual(lanes["rf-evidence-detectors"], "accepted")
        self.assertEqual(lanes["ordinary-controls"], "accepted")
        self.assertEqual(lanes["battery-holder"], "accepted")
        self.assertEqual(lanes["service-headers"], "accepted")
        self.assertEqual(lanes["display-production-route"], "accepted")


if __name__ == "__main__":
    unittest.main()
