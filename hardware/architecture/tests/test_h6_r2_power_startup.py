import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h6_r2_power_startup.py"
CURRENT_OPEN_FINDINGS = {
    "rilm_matches_accepted_h1", "main_pf03_current_reserve", "main_h0_step_floor",
    "main_existing_inrush_model_headroom", "h3_converter_source_is_installed_part",
    "main_pg_assertion_headroom", "aon_ron_test_condition_binding",
}


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

    def test_current_h3_binds_fitted_tcr_corner_not_initial_only(self):
        check = self.check("h3_current_limit_bound_to_fitted_rilm")
        self.assertTrue(check["pass"])
        observed = check["observed"]
        self.assertAlmostEqual(3.072960761422677, observed["fitted_initial_plus_tcr_lower_a"], places=10)
        self.assertAlmostEqual(3.1036903690369, observed["initial_only_lower_a"], places=10)
        self.data["h3"]["rails"]["3V3_MAIN"]["protection_min_a"] = observed["initial_only_lower_a"]
        self.assertFalse(self.check("h3_current_limit_bound_to_fitted_rilm")["pass"])

    def test_same_scalar_cannot_inherit_changed_tcr_conditions(self):
        protection = self.data["h3"]["rails"]["3V3_MAIN"]["conditioned_model"]["protection"]
        for field, value in (("tcr_ppm_per_c", "25"), ("temperature_c", ["0", "85"]),
                             ("reference_temperature_c", "20"), ("gain_tolerance_fraction", "0.05")):
            before = protection[field]
            with self.subTest(field=field):
                protection[field] = value
                self.assertFalse(self.check("h3_current_limit_bound_to_fitted_rilm")["pass"])
            protection[field] = before

    def test_rilm_replacement_cannot_inherit_fitted_tcr(self):
        row = next(row for row in self.data["instances"]["rows"] if row["instance"] == "main_efuse_rilm")
        row["mpn"] = "unreviewed-1650-ohm-replacement"
        self.assertFalse(self.check("h3_current_limit_bound_to_fitted_rilm")["pass"])

    def test_tcr_correction_does_not_qualify_startup_or_positive_margin(self):
        result = self.result()
        current = result["current_limit"]
        self.assertLess(current["fitted_initial_plus_tcr_lower_a"], current["h1_model_lower_a"])
        self.assertGreater(current["fitted_initial_plus_tcr_upper_a"], current["h1_model_upper_a"])
        self.assertTrue(self.check("h3_current_limit_bound_to_fitted_rilm")["pass"])
        self.assertFalse(self.check("main_existing_inrush_model_headroom")["pass"])
        self.assertFalse(result["startup_proven"])

    def test_reusable_current_math_is_hash_bound(self):
        self.assertIn("hardware/verification/h6_power_corner_math.py", self.module.build()["source_sha256"])

    def test_main_power_good_includes_pin_leakage(self):
        self.resistor("main_efuse_pg_top", "45_3kohm_1pct_0402_test_resistor")
        self.resistor("main_efuse_pg_bottom", "30kohm_1pct_0402_test_resistor")
        self.data["margins"]["voltage_corners"]["3V3_MAIN"]["endpoint_min_v"] = "3.108510"
        check = self.check("main_pg_assertion_headroom")
        self.assertFalse(check["pass"])
        self.assertAlmostEqual(3.170574212121, check["observed"]["required_output_v"])

    def test_pg_samples_protected_local_not_consumer_endpoint(self):
        row = self.data["margins"]["voltage_corners"]["3V3_MAIN"]
        row.update(protected_local_min_v="3.20", endpoint_min_v="2.90",
                   nodes={"protected_local_net": "3V3_MAIN"})
        with patch.object(self.module, "admits_current", return_value=True):
            check = self.check("main_pg_assertion_headroom")
        self.assertTrue(check["pass"])
        self.assertAlmostEqual(3.20, check["observed"]["admitted_output_min_v"])
        # PG success never proves the separate 2.90-V consumer endpoint safe.
        self.assertFalse(self.result()["startup_proven"])

    def test_old_endpoint_cannot_substitute_for_missing_pg_node(self):
        row = self.data["margins"]["voltage_corners"]["3V3_MAIN"]
        row.pop("protected_local_min_v", None)
        row["endpoint_min_v"] = "3.25"
        with patch.object(self.module, "admits_current", return_value=True):
            check = self.check("main_pg_assertion_headroom")
        self.assertFalse(check["pass"])
        self.assertIsNone(check["observed"]["provisional_protected_local_min_v"])

    def test_pg_cannot_qualify_a_provisional_rail_by_positive_arithmetic(self):
        row = self.data["margins"]["voltage_corners"]["3V3_MAIN"]
        row.update(protected_local_min_v="3.25", nodes={"protected_local_net": "3V3_MAIN"})
        check = self.check("main_pg_assertion_headroom")
        self.assertTrue(check["observed"]["numerical_headroom_only"])
        self.assertFalse(check["observed"]["current_rail_envelope_admitted"])
        self.assertFalse(check["pass"])

    def test_pg_node_must_agree_with_native_sense_path(self):
        row = self.data["margins"]["voltage_corners"]["3V3_MAIN"]
        row.update(protected_local_min_v="3.25", nodes={"protected_local_net": "3V3_MAIN"})
        self.row("main_efuse_pg_top.END_1")["net"] = "MAIN_RAW_3V3"
        with patch.object(self.module, "admits_current", return_value=True):
            self.assertFalse(self.check("main_pg_assertion_headroom")["pass"])

    def test_pg_rejects_nonfinite_or_untyped_voltage(self):
        row = self.data["margins"]["voltage_corners"]["3V3_MAIN"]
        row["nodes"] = {"protected_local_net": "3V3_MAIN"}
        for value in (None, True, "nan", "inf", "bad", {}):
            with self.subTest(value=value):
                row["protected_local_min_v"] = value
                with patch.object(self.module, "admits_current", return_value=True):
                    self.assertFalse(self.check("main_pg_assertion_headroom")["pass"])

    def test_valley_trip_threshold_is_not_continuous_current_rating(self):
        self.resistor("main_efuse_rilm", "1_06kohm_1pct_0402_test_resistor")
        check = self.check("main_efuse_high_below_buck_limit")
        self.assertGreater(check["observed"], 6.0)
        self.assertLess(check["observed"], 6.1)
        self.assertFalse(check["pass"])

    def test_main_hardware_identity_cannot_use_old_converter_source(self):
        self.data["h3"]["rails"]["3V3_MAIN"]["source"] = "https://www.ti.com/lit/ds/symlink/tps564252.pdf"
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])


    def synthetic_converter_review(self):
        # Test-only registry entry to exercise invalidation.  This does not
        # review the current H3 model or create a production accepted binding.
        model = self.data["h3"]["rails"]["3V3_MAIN"]
        model["source"] = self.module.EVIDENCE["main_buck"]["url"]
        model["converter_operating_conditions"] = {
            "input_voltage_v": [3.0, 18.0], "junction_temperature_c": [-40, 125],
        }
        model["converter_model_review_id"] = "SYNTHETIC_TEST_ONLY"
        _, observed = self.module.main_converter_model_binding(self.data)
        self.module.REVIEWED_MAIN_CONVERTER_MODELS["SYNTHETIC_TEST_ONLY"] = copy.deepcopy(observed["current_binding"])
        self.addCleanup(self.module.REVIEWED_MAIN_CONVERTER_MODELS.clear)
        self.assertTrue(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_current_model_binding_closes_only_one_of_eight_findings(self):
        self.assertEqual({}, self.module.REVIEWED_MAIN_CONVERTER_MODELS)
        result = self.result()
        self.assertEqual(CURRENT_OPEN_FINDINGS, set(result["findings"]))
        check = self.check("h3_converter_source_is_installed_part")
        self.assertTrue(check["observed"]["native_identity_matches"])
        self.assertFalse(check["pass"])
        self.assertFalse(check["observed"]["independently_registered_binding_matches"])

    def test_url_substring_is_not_primary_evidence(self):
        self.synthetic_converter_review()
        self.data["h3"]["rails"]["3V3_MAIN"]["source"] = "https://example.invalid/not-reviewed/tps566231.pdf"
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_exact_ti_url_alone_does_not_review_model(self):
        self.data["h3"]["rails"]["3V3_MAIN"]["source"] = self.module.EVIDENCE["main_buck"]["url"]
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_self_declared_review_id_or_binding_is_not_registered_review(self):
        self.data["h3"]["rails"]["3V3_MAIN"].update({
            "source": self.module.EVIDENCE["main_buck"]["url"],
            "converter_model_review_id": "user-says-reviewed",
            "model_binding": {"pass": True, "mpn": "TPS566231PRQFR"},
            "converter_operating_conditions": {"input_voltage_v": [3, 18], "junction_temperature_c": [-40, 125]},
        })
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_synthetic_registry_binding_does_not_authorize_startup(self):
        self.synthetic_converter_review()
        result = self.result()
        self.assertEqual(CURRENT_OPEN_FINDINGS - {"h3_converter_source_is_installed_part"}, set(result["findings"]))
        self.assertFalse(result["startup_proven"])
        self.assertEqual({"fabrication": False, "gate_closed": False}, result["authorization"])

    def test_same_pads_with_different_native_mpn_cannot_inherit_review(self):
        self.synthetic_converter_review()
        native = next(row for row in self.data["instances"]["rows"] if row["instance"] == "main_buck")
        native["mpn"] = "TPS566231RQFR"
        check = self.check("h3_converter_source_is_installed_part")
        self.assertFalse(check["pass"])
        self.assertFalse(check["observed"]["native_identity_matches"])

    def test_changed_native_device_id_cannot_inherit_review(self):
        self.synthetic_converter_review()
        native = next(row for row in self.data["instances"]["rows"] if row["instance"] == "main_buck")
        native["device_id"] = "synthetic_pin_compatible_part"
        self.data["devices"]["devices"][native["device_id"]] = copy.deepcopy(
            self.data["devices"]["devices"]["ti_tps566231p_rqfr"])
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_register_mpn_must_match_native_exact_variant(self):
        self.synthetic_converter_review()
        self.data["devices"]["devices"]["ti_tps566231p_rqfr"]["mpn"] = "TPS566231RQFR"
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_current_native_pg_contact_must_still_match_registered_application(self):
        self.synthetic_converter_review()
        self.row("main_buck.PG")["net"] = "POWER_GROUND"
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_duplicate_native_converter_cannot_be_silently_selected(self):
        self.synthetic_converter_review()
        native = next(row for row in self.data["instances"]["rows"] if row["instance"] == "main_buck")
        self.data["instances"]["rows"].append(copy.deepcopy(native))
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_changed_numerical_model_invalidates_registry_hash(self):
        self.synthetic_converter_review()
        self.data["h3"]["rails"]["3V3_MAIN"]["raw_average_min_v"] += .001
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_changed_read_conditions_require_new_independent_review(self):
        self.synthetic_converter_review()
        self.data["h3"]["rails"]["3V3_MAIN"]["converter_operating_conditions"]["input_voltage_v"] = [4, 12]
        check = self.check("h3_converter_source_is_installed_part")
        self.assertTrue(check["observed"]["declared_operating_domain_is_supported"])
        self.assertFalse(check["pass"])

    def test_unsupported_missing_or_nonfinite_operating_conditions_fail_closed(self):
        self.synthetic_converter_review()
        for conditions in (None, {}, {"input_voltage_v": [2.9, 18], "junction_temperature_c": [-40, 125]},
                           {"input_voltage_v": [3, 18.1], "junction_temperature_c": [-40, 125]},
                           {"input_voltage_v": [3, 18], "junction_temperature_c": [-41, 125]},
                           {"input_voltage_v": [3, 18], "junction_temperature_c": [-40, 126]},
                           {"input_voltage_v": [12, 3], "junction_temperature_c": [-40, 125]},
                           {"input_voltage_v": [True, 18], "junction_temperature_c": [-40, 125]},
                           {"input_voltage_v": [float("nan"), 18], "junction_temperature_c": [-40, 125]}):
            with self.subTest(conditions=conditions):
                self.data["h3"]["rails"]["3V3_MAIN"]["converter_operating_conditions"] = conditions
                check = self.check("h3_converter_source_is_installed_part")
                self.assertFalse(check["pass"])
                self.assertFalse(check["observed"]["declared_operating_domain_is_supported"])

    def test_changed_fitted_support_value_invalidates_application_hash(self):
        self.synthetic_converter_review()
        self.resistor("main_fb_top", "43_7kohm_1pct_0402_synthetic_different_tolerance")
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_changed_admitted_load_floor_invalidates_application_hash(self):
        self.synthetic_converter_review()
        self.data["h0"]["power_rebaseline"]["h1_required_envelope"]["step_a_min"] += .01
        self.assertFalse(self.check("h3_converter_source_is_installed_part")["pass"])

    def test_binding_revision_cannot_be_silently_changed(self):
        self.synthetic_converter_review()
        self.module.REVIEWED_MAIN_CONVERTER_MODELS["SYNTHETIC_TEST_ONLY"]["primary_revision"] = "unreviewed-later-revision"
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
