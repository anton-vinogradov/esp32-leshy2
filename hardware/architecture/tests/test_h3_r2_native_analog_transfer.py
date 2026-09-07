"""Current native substitutions cannot inherit a fresh-hash historical PASS."""

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("analog_transfer", ROOT / "hardware/verification/h3_r2_analog_corners.py")
ANALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALOG)


class NativeAnalogTransferTests(unittest.TestCase):
    def setUp(self):
        self.candidate = ANALOG.load(ANALOG.CANDIDATE)
        self.devices = ANALOG.load(ANALOG.DEVICES)["devices"]
        self.instances = ANALOG.load(ANALOG.NATIVE_INSTANCES)["rows"]
        self.rows = ANALOG.load(ANALOG.NATIVE_NETS)["rows"]
        self.leaves = {"audio": ANALOG.load(ANALOG.AUDIO), "ir": ANALOG.load(ANALOG.IR)}

    def evaluate(self):
        return ANALOG.native_leaf_transfers(self.candidate, self.devices, self.instances, self.rows, self.leaves)

    def assert_review(self, domain):
        result = self.evaluate()[domain]
        self.assertEqual(result["status"], "review_required", result)
        self.assertFalse(all(result["checks"].values()))
        self.assertIs(result["fabrication_ready"], False)

    def test_current_exact_native_boundary_has_only_scoped_equivalence(self):
        result = self.evaluate()
        for domain in ("ir", "audio"):
            self.assertEqual(result[domain]["status"], "bounded_electrical_equivalence_verified", result[domain])
            self.assertTrue(all(result[domain]["checks"].values()))
            self.assertFalse(result[domain]["fabrication_ready"])
            self.assertGreaterEqual(len(result[domain]["not_transferred"]), 3)

    def test_primary_pin_function_fixture_is_independent_of_guard(self):
        # Two manufacturer p.2 circuit diagrams: tip is 2, NOT sleeve1;
        # current TS has no physical6. Vishay 82907 p.2 has both grounds1/4.
        expected = {
            "headphone_jack": {"1": ("SLEEVE", "HEADSET_MIC_RAW"), "2": ("TIP", "HEADPHONE_LEFT_TIP"),
                               "3": ("RING1", "HEADPHONE_RIGHT_RING1"), "4": ("RING2", "AUDIO_GROUND"),
                               "5": ("TIP_SWITCH", "HEADSET_SWITCH_STATE")},
            "ir_carrier": {"1": ("GND_1", "POWER_GROUND"), "2": ("VS", "IR_CARRIER_VS"),
                           "3": ("CARRIER_OUT", "IR_CARRIER_LOCAL_N"), "4": ("GND_4", "POWER_GROUND")},
        }
        for instance, pins in expected.items():
            rows = [row for row in self.rows if row["instance"] == instance]
            self.assertEqual(len(rows), len(pins))
            self.assertEqual({row["physical"]: (row["contact"], row["net"]) for row in rows}, pins)

    def test_no_plug_divider_is_tip_switch_not_microphone_switch(self):
        from fractions import Fraction
        # Independent worst-case 1% resistors; high Z P02. Not a new hardware
        # measurement or an assertion that firmware has executed this input mode.
        ratio = Fraction(99000, 99000 + 10100 + 10100)
        self.assertGreater(ratio, Fraction(7, 10))
        self.assertAlmostEqual(float(ratio), 0.830536912751678)
        device = self.devices["same_sky_sj_43515ts_smt_tr"]["electrical_contract"]
        self.assertEqual(device["tip_switch_closed_without_plug_physical_pads"], ["2", "5"])
        device["tip_switch_closed_without_plug_physical_pads"] = ["1", "5"]
        self.assert_review("audio")

    def test_wrong_inserted_switch_state_requires_review(self):
        self.devices["same_sky_sj_43515ts_smt_tr"]["electrical_contract"]["tip_switch_open_with_plug_physical_pads"] = ["3", "5"]
        self.assert_review("audio")

    def test_removed_legacy_contact_must_really_have_been_unused(self):
        next(route for route in self.candidate["fixed_routes"] if route["from"] == "headphone_jack.RING1_SWITCH")["to"] = "slow_io.P03"
        self.assert_review("audio")

    def test_phantom_native_nc6_is_not_accepted(self):
        row = copy.deepcopy(next(row for row in self.rows if row["endpoint"] == "headphone_jack.TIP_SWITCH"))
        row.update(endpoint="headphone_jack.RING1_SWITCH", contact="RING1_SWITCH", physical="6", net=None, disposition="no_connect")
        self.rows.append(row)
        self.assert_review("audio")

    def test_source_contacts_cannot_silently_add_nc6(self):
        self.devices["same_sky_sj_43515ts_smt_tr"]["contacts"]["RING1_SWITCH"] = {"physical": "6", "role": "signal"}
        self.assert_review("audio")

    def test_each_current_physical_contact_field_is_bound(self):
        original = copy.deepcopy(self.rows)
        for domain, instance in (("ir", "ir_carrier"), ("audio", "headphone_jack")):
            targets = [row["endpoint"] for row in original if row["instance"] == instance]
            for endpoint in targets:
                for field in ("endpoint", "instance", "contact", "physical", "role", "net", "project", "reference", "device_id", "disposition"):
                    with self.subTest(endpoint=endpoint, field=field):
                        self.rows = copy.deepcopy(original)
                        next(row for row in self.rows if row["endpoint"] == endpoint)[field] = "WRONG"
                        self.assert_review(domain)

    def test_duplicate_or_missing_contacts_fail_closed(self):
        original = copy.deepcopy(self.rows)
        for domain, instance in (("ir", "ir_carrier"), ("audio", "headphone_jack")):
            for duplicate in (False, True):
                self.rows = copy.deepcopy(original)
                row = next(row for row in self.rows if row["instance"] == instance)
                if duplicate:
                    self.rows.append(copy.deepcopy(row))
                else:
                    self.rows.remove(row)
                self.assert_review(domain)

    def test_native_instance_identity_and_uniqueness_are_required(self):
        original = copy.deepcopy(self.instances)
        for domain, instance in (("ir", "ir_carrier"), ("audio", "headphone_jack")):
            for field in ("device_id", "mpn", "project", "reference", "duplicate", "missing"):
                with self.subTest(domain=domain, field=field):
                    self.instances = copy.deepcopy(original)
                    row = next(row for row in self.instances if row["instance"] == instance)
                    if field == "duplicate":
                        self.instances.append(copy.deepcopy(row))
                    elif field == "missing":
                        self.instances.remove(row)
                    else:
                        row[field] = "WRONG"
                    self.assert_review(domain)

    def test_matching_ids_cannot_hide_wrong_manufacturer_mpn(self):
        self.devices["vishay_tsmp95000tr"]["mpn"] = "Vishay ANOTHER_PART"
        next(row for row in self.instances if row["instance"] == "ir_carrier")["mpn"] = "Vishay ANOTHER_PART"
        self.assert_review("ir")

    def test_both_registers_agreeing_on_changed_ir_rating_is_not_enough(self):
        for device in ("vishay_tsmp95000tr", "vishay_tsmp95000tt"):
            self.devices[device]["electrical_contract"]["supply_v"] = [3.0, 5.5]
        self.assert_review("ir")

    def test_changed_source_pin_assignment_is_not_an_equivalent_tape_change(self):
        self.devices["vishay_tsmp95000tr"]["contacts"]["VS"]["physical"] = "3"
        self.assert_review("ir")

    def test_missing_or_changed_primary_evidence_fails_closed(self):
        for domain, device in (("ir", "vishay_tsmp95000tr"), ("audio", "same_sky_sj_43515ts_smt_tr")):
            self.devices[device]["source"]["url"] = "https://example.com/catalog-placeholder"
            self.assert_review(domain)

    def test_unknown_substitution_cannot_inherit_pass(self):
        self.candidate["instances"]["ir_carrier"] = "vishay_tsmp95000tr"
        self.assert_review("ir")

    def test_leaf_identity_missing_or_integer_true_is_not_reviewed(self):
        for domain, instance in (("ir", "ir_carrier"), ("audio", "headphone_jack")):
            self.leaves[domain]["checks"]["exact_" + instance] = 1
            self.assert_review(domain)

    def test_empty_leaf_checks_do_not_vacuously_pass(self):
        for value in ({}, None, [], {"x": 1}, {"x": False}):
            self.assertFalse(ANALOG.all_true(value))
        self.assertTrue(ANALOG.all_true({"x": True}))

    def test_analog_detector_resistor_substitution_requires_review(self):
        next(row for row in self.instances if row["instance"] == "headset_detect_series")["device_id"] = "yageo_rc0402fr_07100kl"
        self.assert_review("audio")

    def test_ir_supply_or_pullup_pin_and_net_change_requires_review(self):
        for endpoint in ("ir_carrier_supply_res.END_1", "ir_carrier_pullup.END_2", "ir_return_buffer.2A"):
            next(row for row in self.rows if row["endpoint"] == endpoint)["net"] = "3V3_MAIN"
            self.assert_review("ir")

    def test_extra_node_load_is_not_silently_transferred(self):
        for domain, net in (("ir", "IR_CARRIER_VS"), ("audio", "HEADSET_ABSENT")):
            row = copy.deepcopy(next(row for row in self.rows if row["net"] == net))
            row.update(instance="new_load", endpoint="new_load.IN", contact="IN")
            self.rows.append(row)
            self.assert_review(domain)

    def test_missing_detector_element_is_not_accepted(self):
        self.rows = [row for row in self.rows if row["endpoint"] != "headset_absent_pulldown.END_2"]
        self.assert_review("audio")

    def test_build_and_render_cannot_turn_failed_binding_into_pass(self):
        transfers = self.evaluate()
        transfers["audio"]["checks"]["complete_current_native_contact_map"] = False
        transfers["audio"]["status"] = "review_required"
        with patch.object(ANALOG, "native_leaf_transfers", return_value=transfers):
            result = ANALOG.build()
        self.assertEqual(result["status"], "fail")
        self.assertFalse(result["leaf_evidence"]["audio"]["checks"]["current_native_substitution_is_bound"])
        self.assertTrue(any("audio current-native substitution requires review" in error for error in result["errors"]))
        for language in ("en", "ru"):
            text = ANALOG.render(result, language)
            self.assertIn("| Аудио / audio | REVIEW REQUIRED |", text)
            self.assertNotIn("Every calculable check passes", text)
            self.assertNotIn("Only physical properties remain", text)
            self.assertNotIn("Все расчётные проверки пройдены", text)


if __name__ == "__main__":
    unittest.main()
