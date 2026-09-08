"""Independent fitted-MAIN arithmetic/identity tests; no output publication."""
import copy
import json
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/verification"))
import h3_r2_rail_margins as model


class FittedMainModelTests(unittest.TestCase):
    def setUp(self):
        self.rail = json.loads(model.CONTRACT.read_text())["rails"]["3V3_MAIN"]
        self.devices = json.loads(model.DEVICES.read_text())["devices"]
        self.native = json.loads(model.INSTANCES.read_text())["rows"]
        self.nets = json.loads(model.NETS.read_text())["rows"]

    def build(self):
        return model.fitted_main_model(self.rail, self.devices, self.native, self.nets)

    def test_decimal_feedback_matches_independent_rational_corners(self):
        result = self.build()
        low = F(999, 1000) * (1 - F(25, 1000000) * 105)
        high = F(1001, 1000) * (1 + F(25, 1000000) * 105)
        expected = {"minimum": F(591, 1000) * (1 + F(437, 100) * low / high),
                    "maximum": F(609, 1000) * (1 + F(437, 100) * high / low)}
        for side, value in expected.items():
            self.assertLess(abs(F(result["raw_average_v"][side]) - value), F(1, 10**45))
        self.assertEqual("20", result["feedback_scope"]["reference_temperature_c"])
        self.assertFalse(result["qualified"])

    def test_rilm_initial_and_tcr_are_distinct_native1650_intervals(self):
        corners = self.build()["protection_corners"]
        for name, factor in (("initial_only", F(101, 100)), ("initial_plus_tcr", F(101, 100)**2)):
            minimum = F(5747) * F(9, 10) / (1650 * factor)
            self.assertLess(abs(F(corners[name]["trip_current_a"]["minimum"]) - minimum), F(1, 10**45))
        self.assertLess(D(corners["initial_plus_tcr"]["trip_current_a"]["minimum"]), D("3.046") * D("1.25"))
        self.assertLess(D(corners["initial_only"]["trip_current_a"]["minimum"]), D("4.25"))
        self.assertNotIn("drift_budgets", self.build()["protection_scope"])

    def test_same_pads_different_mpn_cannot_inherit_model(self):
        for mutate_device in (False, True):
            rows = copy.deepcopy(self.native)
            row = next(row for row in self.native if row["instance"] == "main_buck")
            row["mpn"] = "TPS566231S-not-the-fitted-part"
            if mutate_device:
                self.devices["ti_tps566231p_rqfr"]["mpn"] = row["mpn"]
            with self.subTest(mutate_device=mutate_device), self.assertRaisesRegex(ValueError, "identity"):
                self.build()
            self.native = rows

    def test_device_id_reference_and_duplicate_instance_rejected(self):
        for field, value in (("device_id", "different_same_pads"), ("reference", "U200"), ("project", "LESHY2-UI-R2")):
            original = copy.deepcopy(self.native)
            next(row for row in self.native if row["instance"] == "main_buck")[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.build()
            self.native = original
        self.native.append(copy.deepcopy(next(row for row in self.native if row["instance"] == "main_fb_top")))
        with self.assertRaises(ValueError):
            self.build()

    def test_raw_feedback_cannot_move_after_latchoff_efuse(self):
        next(row for row in self.nets if row["endpoint"] == "main_fb_top.END_1")["net"] = "3V3_MAIN"
        with self.assertRaisesRegex(ValueError, "topology"):
            self.build()

    def test_pad_number_disconnection_and_duplicate_endpoint_rejected(self):
        for field, value in (("physical", "50"), ("disposition", "no_connect"), ("contact", "END_2")):
            original = copy.deepcopy(self.nets)
            next(row for row in self.nets if row["endpoint"] == "main_fb_top.END_1")[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.build()
            self.nets = original
        self.nets.append(copy.deepcopy(next(row for row in self.nets if row["endpoint"] == "main_efuse_rilm.END_1")))
        with self.assertRaises(ValueError):
            self.build()

    def test_divider_values_tolerance_tcr_and20c_reference_fail_closed(self):
        key = "vishay_tnpw040243k7beed"
        for field, value in (("resistance_ohm", 43200), ("tolerance_pct", 0), ("temperature_coefficient_ppm_per_c", 0)):
            original = copy.deepcopy(self.devices)
            self.devices[key]["electrical_contract"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.build()
            self.devices = original
        self.rail["conditioned_model"]["feedback_resistors"]["reference_temperature_c"] = "25"
        with self.assertRaises(ValueError):
            self.build()

    def test_missing_tcr_and_nonfinite_values_are_not_zeroed(self):
        electrical = self.devices["vishay_tnpw040210k0beed"]["electrical_contract"]
        for value in ("NaN", "Infinity", True, -1):
            electrical["temperature_coefficient_ppm_per_c"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.build()
        del electrical["temperature_coefficient_ppm_per_c"]
        with self.assertRaises(KeyError):
            self.build()

    def test_primary_test_vin_and_qualification_cannot_self_widen(self):
        for section, key, value in (("vfb_test_conditions", "input_voltage_v", "6"),
                ("vfb_test_conditions", "actual_input_domain_qualification", True),
                ("engineering_budgets", "qualified", True), ("primary", "url", "https://example.com/TPS566231")):
            original = copy.deepcopy(self.rail)
            self.rail["conditioned_model"][section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                self.build()
            self.rail = original
        self.rail["conditioned_model"]["qualified"] = True
        with self.assertRaises(ValueError):
            self.build()

    def test_stale_scalar_old_protection_and_valley_as_rating_rejected(self):
        for key, value in (("raw_average_min_v", "3.168510"), ("protection_min_a", "4.3399"),
                           ("converter_min_a", "6.1"), ("converter_theta_ja_k_per_w", "74")):
            original = copy.deepcopy(self.rail)
            self.rail[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.build()
            self.rail = original

    def test_model_does_not_mutate_inputs(self):
        before = copy.deepcopy((self.rail, self.devices, self.native, self.nets))
        self.build()
        self.assertEqual(before, (self.rail, self.devices, self.native, self.nets))

    def test_four_reference_loss_budgets_match_independent_fractions(self):
        result = model.main_thermal_result(self.rail, D(3750), {"signal_group": "H0", "group_mode": "continuous", "support_profile": "design_target"}, self.build())
        self.assertEqual(4, len(result["reference_loss_budgets"]))
        for row in result["reference_loss_budgets"]:
            allowed = (F(105) - F(row["ambient_c"])) / F(row["reference_theta_ja_k_per_w"])
            self.assertLessEqual(abs(F(row["allowable_chip_loss_w"]) - allowed), F(1, 2000000))
            self.assertFalse(row["our_pcb_qualified"])
            self.assertFalse(row["is_efficiency_prediction"])
        self.assertIsNone(result["converter_predicted_tj_c"])
        self.assertIsNone(result["efuse_predicted_tj_c"])
        self.assertIsNone(result["minimum_efficiency"])
        self.assertEqual("review_required", result["status"])

    def test_thermal_budget_cannot_become_our_board_prediction(self):
        fitted = self.build()
        fitted["thermal_loss_budget_contract"]["our_pcb_thermal_resistance_qualified"] = True
        with self.assertRaises(ValueError):
            model.main_thermal_result(self.rail, D(3750), {}, fitted)
        with self.assertRaises(ValueError):
            model.thermal_result("3V3_MAIN", self.rail, D(3750), {}, D(".85"), D(35), D(20))

    def test_current_h0_and_all56_profile_nodes_remain_unqualified(self):
        _, result = model.build()
        self.assertEqual(224, len(result["profile_voltage_corners"]))
        main = [row for row in result["profile_voltage_corners"] if row["rail"] == "3V3_MAIN"]
        self.assertEqual(56, len(main))
        self.assertTrue(all(row["status"] == "review_required" for row in main))
        targets = result["declared_target_voltage_corners"]["3V3_MAIN"]
        self.assertEqual("2.907513", targets["H0_continuous"]["endpoint_min_v"])
        self.assertEqual("2.882513", targets["H0_step_resistive_snapshot_not_transient_proof"]["endpoint_min_v"])
        self.assertEqual("fail", result["worst_current_by_rail"]["3V3_MAIN"]["numerical_status"])
        self.assertIsNone(result["summary"]["minimum_junction_margin_c"])
        self.assertFalse(any(result["authorization"].values()))
        self.assertEqual("review_required", result["status"])


if __name__ == "__main__":
    unittest.main()
