import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h6_r2_power_startup.py"


class H6R2NativePowerStartupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h6_r2_power_startup_test", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.base = {name: json.loads((ROOT / path).read_text()) for name, path in cls.module.INPUTS.items()}

    def setUp(self):
        self.data = copy.deepcopy(self.base)

    def row(self, endpoint):
        return next(row for row in self.data["nets"]["rows"] if row["endpoint"] == endpoint)

    def result(self):
        return self.module.evaluate(self.data)

    def check(self, ident):
        return next(row for row in self.result()["checks"] if row["id"] == ident)

    def resistor(self, instance, kind):
        device = next(row["device_id"] for row in self.data["instances"]["rows"] if row["instance"] == instance)
        self.data["devices"]["devices"][device]["kind"] = kind

    def test_current_native_pin_and_support_paths_are_reviewed(self):
        checks = self.result()["checks"]
        structural = [row for row in checks if row["id"].startswith(("identity:", "pin:", "path:"))]
        self.assertGreater(len(structural), 60)
        self.assertTrue(all(row["pass"] for row in structural), [row for row in structural if not row["pass"]])

    def test_own_output_enable_deadlock_is_rejected(self):
        self.row("aon_efuse.EN_UVLO")["net"] = "AON_SAFE_3V3"
        self.assertFalse(self.check("pin:aon_efuse.EN_UVLO")["pass"])

    def test_main_enable_cannot_depend_on_main_output(self):
        self.row("main_buck.EN")["net"] = "3V3_MAIN"
        self.assertFalse(self.check("pin:main_buck.EN")["pass"])

    def test_missing_supervisor_supply_is_rejected(self):
        self.row("safe_supervisor.VDD")["disposition"] = "no_connect"
        self.assertFalse(self.check("pin:safe_supervisor.VDD")["pass"])

    def test_manufacturer_pin_number_change_is_rejected(self):
        self.data["devices"]["devices"]["ti_tps566231p_rqfr"]["contacts"]["EN"]["physical"] = "2"
        self.assertFalse(self.check("pin:main_buck.EN")["pass"])

    def test_native_pin_number_change_is_rejected(self):
        self.row("main_buck.FB")["physical"] = "3"
        self.assertFalse(self.check("pin:main_buck.FB")["pass"])

    def test_explicit_aon_vset_open_is_allowed_only_in_correct_mode(self):
        self.assertTrue(self.check("aon_vset_configuration")["pass"])
        self.assertTrue(self.check("pin:aon_buck.FB_VSET")["pass"])
        self.resistor("aon_mode_res", "34kohm_1pct_0402_test_resistor")
        self.assertFalse(self.check("aon_vset_configuration")["pass"])

    def test_bootstrap_return_cannot_be_ground(self):
        self.row("main_buck_bootstrap_link.END_2")["net"] = "POWER_GROUND"
        self.assertFalse(self.check("path:main_buck_bootstrap_link")["pass"])

    def test_feedback_cannot_sample_protected_instead_of_raw_output(self):
        self.row("main_fb_top.END_1")["net"] = "3V3_MAIN"
        self.assertFalse(self.check("path:main_fb_top")["pass"])

    def test_current_1650_value_cannot_inherit_1180_threshold(self):
        self.resistor("main_efuse_rilm", "1_65kohm_1pct_0402_test_resistor")
        self.data["h1"]["main_power_cell"]["efuse_threshold_resistor"]["resistance_ohm"] = 1180
        self.data["h3"]["rails"]["3V3_MAIN"]["protection_min_a"] = 4.3399
        result = self.result()
        self.assertIn("rilm_matches_accepted_h1", result["findings"])
        self.assertIn("h3_current_limit_bound_to_fitted_rilm", result["findings"])
        self.assertAlmostEqual(3.168316831683, result["current_limit"]["direct_row_resistor_tolerance_scaled_min_a"])

    def test_positive_current_remainder_is_not_25_percent_reserve(self):
        self.resistor("main_efuse_rilm", "1_65kohm_1pct_0402_test_resistor")
        self.data["margins"]["worst_current_by_rail"]["3V3_MAIN"]["load_ma"] = "3046.000"
        check = self.check("main_pf03_current_reserve")
        self.assertGreater(check["observed"]["model_lower_a"], 3.046)
        self.assertFalse(check["pass"])

    def test_main_power_good_includes_pin_leakage(self):
        self.resistor("main_efuse_pg_top", "45_3kohm_1pct_0402_test_resistor")
        self.resistor("main_efuse_pg_bottom", "30kohm_1pct_0402_test_resistor")
        self.data["margins"]["voltage_corners"]["3V3_MAIN"]["endpoint_min_v"] = "3.108510"
        check = self.check("main_pg_assertion_headroom")
        self.assertFalse(check["pass"])
        self.assertAlmostEqual(3.170574212121, check["observed"]["required_output_v"])

    def test_main_hardware_identity_cannot_use_old_converter_source(self):
        self.data["h3"]["rails"]["3V3_MAIN"]["source"] = "https://www.ti.com/lit/ds/symlink/tps564252.pdf"
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_aon_ron_bound_must_use_fitted_rilim_condition(self):
        self.resistor("aon_efuse_rilim", "240kohm_1pct_0402_test_resistor")
        self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = .240
        self.assertFalse(self.check("aon_ron_test_condition_binding")["pass"])

    def test_larger_claimed_aon_ron_does_not_verify_unknown_resistor_condition(self):
        self.resistor("aon_efuse_rilim", "240kohm_1pct_0402_test_resistor")
        for claimed in (.241, .455, .456, 1.0):
            with self.subTest(claimed=claimed):
                self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = claimed
                check = self.check("aon_ron_test_condition_binding")
                self.assertFalse(check["pass"])
                self.assertIsNone(check["observed"]["reviewed_table_max_ohm"])
                self.assertEqual("unreviewed_rilim_condition", check["observed"]["rilim_condition_status"])

    def test_other_aon_typical_rows_cannot_be_promoted_to_maximum(self):
        for kind in ("100kohm_1pct_0402_test_resistor", "250kohm_1pct_0402_test_resistor"):
            with self.subTest(kind=kind):
                self.resistor("aon_efuse_rilim", kind)
                self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = .500
                self.assertFalse(self.check("aon_ron_test_condition_binding")["pass"])

    def test_reviewed_aon_nominal_condition_requires_its_actual_maximum(self):
        # Synthetic input only: recognizing the existing datasheet row is not
        # authorization to adopt this resistor or clear other power checks.
        self.resistor("aon_efuse_rilim", "34_48kohm_1pct_0402_test_resistor")
        self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = .239
        self.assertFalse(self.check("aon_ron_test_condition_binding")["pass"])
        self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = .240
        check = self.check("aon_ron_test_condition_binding")
        self.assertTrue(check["pass"])
        self.assertEqual(.240, check["observed"]["reviewed_table_max_ohm"])
        self.assertFalse(self.result()["startup_proven"])

    def test_reviewed_aon_condition_cannot_accept_nonfinite_bound(self):
        self.resistor("aon_efuse_rilim", "34_48kohm_1pct_0402_test_resistor")
        for claimed in (float("nan"), float("inf"), -.240):
            with self.subTest(claimed=claimed):
                self.data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"] = claimed
                self.assertFalse(self.check("aon_ron_test_condition_binding")["pass"])

    def test_duplicate_native_endpoint_is_not_silently_overwritten(self):
        self.data["nets"]["rows"].append(copy.deepcopy(self.row("main_buck.EN")))
        with self.assertRaisesRegex(ValueError, "duplicate native endpoint"):
            self.result()

    def test_audit_never_authorizes_startup_or_production(self):
        result = self.result()
        self.assertFalse(result["startup_proven"])
        self.assertEqual({"fabrication": False, "gate_closed": False}, result["authorization"])
        self.assertGreater(len(result["unproven"]), 4)

    def test_review_integrity_pass_does_not_clear_findings(self):
        result = self.result()
        self.module.validate_result(result)
        self.assertFalse(result["startup_proven"])
        self.assertFalse(result["authorization"]["gate_closed"])

    def test_missing_finding_is_invalid_review(self):
        result = self.result()
        result["checks"][0]["pass"] = False
        result["findings"] = []
        with self.assertRaisesRegex(ValueError, "findings are incomplete"):
            self.module.validate_result(result)

    def test_false_release_claim_is_invalid_review(self):
        result = self.result()
        result["startup_proven"] = True
        with self.assertRaisesRegex(ValueError, "cannot prove startup"):
            self.module.validate_result(result)


if __name__ == "__main__":
    unittest.main()
