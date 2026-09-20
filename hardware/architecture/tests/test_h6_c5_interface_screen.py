"""Admit only pinned source conditions; static arithmetic never qualifies PCB."""

import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from hardware.verification import h6_r2_c5_interface_screen as screen
from hardware.verification import h6_r2_c5_isolation_candidate as candidate


class StaticInterfaceTests(unittest.TestCase):
    def run_point(self, **kwargs):
        point = dict(buffer_v=["3.3", "3.3"], receiver_v=["3.3", "3.3"], temperature_c=["25", "25"])
        return screen.static_screen(**(point | kwargs))

    def test_reference_point_exact_arithmetic_not_qualification(self):
        result = self.run_point()
        self.assertEqual("conditional_static_screen", result["status"])
        self.assertEqual({"high_margin_v_exact": "29/40", "low_margin_v_exact": "29/40",
                          "upper_voltage_margin_v_exact": "3/10", "lower_voltage_margin_v_exact": "3/10",
                          "known_receiver_input_current_ua_exact": "1/20",
                          "voltage_and_logic_compatible_under_assumptions": True}, result["numerical"])
        for field in ("qualified", "delivered_rail_proven", "gpio_mode_proven"):
            self.assertIs(False, result[field])
        self.assertTrue(result["assumptions"])

    def test_five_volt_driver_not_mislabeled_compatible_with_c5(self):
        result = self.run_point(buffer_v=["5", "5"])
        self.assertTrue(all(result["conditions"].values()))
        self.assertEqual("-7/5", result["numerical"]["upper_voltage_margin_v_exact"])
        self.assertFalse(result["numerical"]["voltage_and_logic_compatible_under_assumptions"])
        self.assertFalse(result["qualified"])

    def test_lower_driver_cannot_satisfy_receiver_high_threshold(self):
        result = self.run_point(buffer_v=["1.65", "1.65"])
        self.assertEqual("-37/40", result["numerical"]["high_margin_v_exact"])
        self.assertFalse(result["numerical"]["voltage_and_logic_compatible_under_assumptions"])

    def test_dc_table_never_extrapolated_to_recommended_envelope(self):
        for kwargs, field in (({"receiver_v": ["3", "3.3"]}, "receiver_dc_supply"),
                              ({"receiver_v": ["3.222", "3.222"]}, "receiver_dc_supply"),
                              ({"temperature_c": ["-40", "85"]}, "receiver_dc_temperature"),
                              ({"temperature_c": ["85", "85"]}, "receiver_dc_temperature"),
                              ({"buffer_v": ["1.64", "3.3"]}, "buffer_supply"),
                              ({"temperature_c": ["25", "126"]}, "buffer_temperature"),
                              ({"total_static_load_ua": "100.0001"}, "conditional_static_load_budget"),
                              ({"total_static_load_ua": "0.049"}, "receiver_known_input_current_within_budget")):
            with self.subTest(kwargs=kwargs):
                result = self.run_point(**kwargs)
                self.assertEqual("source_conditions_uncovered", result["status"])
                self.assertFalse(result["conditions"][field])
                self.assertIsNone(result["numerical"])
                self.assertFalse(result["qualified"])

    def test_invalid_and_nonfinite_stimuli_fail_closed(self):
        for kwargs in ({"buffer_v": [True, "3.3"]}, {"buffer_v": [3.3, "3.3"]},
                       {"receiver_v": ["3.4", "3.3"]}, {"receiver_v": ["NaN", "3.3"]},
                       {"buffer_v": ["0", "3.3"]}, {"temperature_c": ["-274", "25"]},
                       {"total_static_load_ua": "-1"}, {"total_static_load_ua": "Infinity"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.run_point(**kwargs)

    def test_mutating_stimulus_or_result_does_not_poison_future_calls(self):
        voltage = ["3.3", "3.3"]
        result = self.run_point(buffer_v=voltage)
        voltage[0] = "5"
        self.assertEqual(["3.3", "3.3"], result["stimulus"]["buffer_v"])
        result["assumptions"].clear()
        self.assertTrue(self.run_point()["assumptions"])

    def test_changed_missing_or_symlinked_transcription_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.json"
            path.write_text(screen.SOURCES.read_text() + " ")
            with patch.object(screen, "SOURCES", path), self.assertRaisesRegex(ValueError, "changed"):
                screen.load_review()
            missing = Path(directory) / "missing.json"
            with patch.object(screen, "SOURCES", missing), self.assertRaisesRegex(ValueError, "missing"):
                screen.load_review()
            link = Path(directory) / "link.json"
            link.symlink_to(screen.SOURCES)
            with patch.object(screen, "SOURCES", link), self.assertRaisesRegex(ValueError, "symlinked"):
                screen.load_review()

    def test_proof_is_only_exact_input_at_zero_supply_not_generic_ioff(self):
        proof, = screen.off_input_proofs("main_schmitt")
        self.assertEqual(("SN74LVC1G17DCKR", ["2"], ["VCC"], ["0", "0"], ["0", "5.5"]),
                         (proof["mpn"], proof["pads"], proof["supply_contacts"], proof["supply_v"], proof["input_v"]))
        self.assertEqual("powered_off_input_voltage_tolerance", proof["parameter"])
        self.assertEqual(screen.REVIEWED_SHA256, proof["source"]["sha256"])
        self.assertEqual((), screen.off_input_proofs("aon_open_drain"))
        with self.assertRaisesRegex(ValueError, "unknown"):
            screen.off_input_proofs("unknown")


class NativeInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = {key: candidate.crossings.load(candidate.ROOT / path) for key, path in candidate.crossings.INPUTS.items()}
        cls.reviews = candidate.crossings.semantics.reviewed_maps(
            [candidate.crossings.load(p) for p in candidate.crossings.semantics.MAPS], cls.baseline["material"]["groups"])

    def setUp(self):
        self.overlay = candidate.make_candidate(self.baseline, self.reviews, "main_schmitt")

    def check(self, reviews=None):
        return screen.review_candidate(self.overlay, reviews or self.reviews, "main_schmitt")

    def row(self, endpoint):
        return next(r for r in self.overlay["nets"]["rows"] if r["project"] == candidate.PROJECT and r["endpoint"] == endpoint)

    def test_native_net_screen_separates_table_point_and_actual_nominal(self):
        before = candidate.digest(self.overlay)
        result = self.check()
        self.assertEqual(before, candidate.digest(self.overlay))
        self.assertEqual("3.222", result["declared_main_nominal_v"])
        self.assertEqual("source_conditions_uncovered", result["declared_voltage_module_temperature_envelope"]["status"])
        self.assertEqual("conditional_static_screen", result["datasheet_reference_point_not_current_nominal"]["status"])
        self.assertEqual({"GPIO23", "GPIO24"}, {c["receiver"] for c in result["channels"]})
        self.assertTrue(all(c["only_expected_output_loads"] for c in result["channels"]))
        self.assertFalse(result["additional_output_loads_present"])
        for field in ("qualified", "gpio_mode_proven", "actual_off_pin_voltage_bounded"):
            self.assertIs(False, result[field])
        self.assertTrue(result["off_input_source_evidence_available"])
        self.assertIn("offline", result["source_mode"])

    def test_extra_output_load_is_rejected(self):
        self.row("c5_evidence_output_pullup.END_2")["net"] = "EXP_C5_RF_TX_EVIDENCE_N"
        with self.assertRaisesRegex(ValueError, "unexpected isolated output loads"):
            self.check()

    def test_wrong_buffer_supply_or_channel_rejected(self):
        for endpoint, net in (("exp_c5_rf_schmitt.VCC", "AON_SAFE_3V3"),
                              ("exp_c5_rf_schmitt.GND", "AON_SAFE_3V3"),
                              ("exp_c5_rf_schmitt.A", "EV_N7_IR"),
                              ("c5.3V3", "AON_SAFE_3V3")):
            with self.subTest(endpoint=endpoint):
                self.overlay = candidate.make_candidate(self.baseline, self.reviews, "main_schmitt")
                self.row(endpoint)["net"] = net
                with self.assertRaisesRegex(ValueError, "supply|channel"):
                    self.check()

    def test_wrong_physical_contact_or_receiver_type_rejected(self):
        self.row("c5.GPIO23")["physical"] = "23"
        with self.assertRaisesRegex(ValueError, "physical"):
            self.check()
        self.overlay = candidate.make_candidate(self.baseline, self.reviews, "main_schmitt")
        reviews = copy.deepcopy(self.reviews)
        reviews["esp32_c5_wroom_1u_n8r8"]["pins"]["21"]["type"] = "output"
        with self.assertRaisesRegex(ValueError, "pin/type"):
            self.check(reviews)

    def test_wrong_exact_mpn_rejected(self):
        # Net rows carry device_id; authoritative MPN is in instances/material.
        instance = next(r for r in self.overlay["instances"]["rows"] if r["instance"] == "exp_c5_rf_schmitt")
        instance["mpn"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "identity"):
            self.check()

    def test_source_scope_and_outputs_never_claim_hardware_or_runtime_validation(self):
        self.assertTrue(screen.load_review()["unresolved"])
        old = screen.review_candidate(self.baseline, self.reviews, "aon_open_drain")
        self.assertFalse(old["qualified"])
        self.assertIn("slew", old["reason"])
        with self.assertRaisesRegex(ValueError, "unknown"):
            screen.review_candidate(self.overlay, self.reviews, "unknown")


if __name__ == "__main__":
    unittest.main()
