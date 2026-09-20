"""Fail closed when any selected EV load or declared frontier changes."""

import copy
import unittest

from hardware.verification import h6_r2_ev_load_fixture as fixture
from hardware.verification import h6_r2_c5_isolation_candidate as candidate


class EVLoadFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = {key: fixture.crossings.load(fixture.crossings.ROOT / path) for key, path in fixture.crossings.INPUTS.items()}
        cls.reviews = fixture.crossings.semantics.reviewed_maps(
            [fixture.crossings.load(path) for path in fixture.crossings.semantics.MAPS], cls.baseline["material"]["groups"])

    def setUp(self):
        self.data = copy.deepcopy(self.baseline)

    def row(self, endpoint):
        return next(row for row in self.data["nets"]["rows"] if row["endpoint"] == endpoint)

    def test_current_exact_values_membership_and_false_authority(self):
        result = fixture.extract(self.data, self.reviews)
        self.assertEqual(["c5", "ir"], [row["id"] for row in result["channels"]])
        for channel in result["channels"]:
            self.assertEqual(["10000", "2200", "1000000", "100000", "10000"],
                [channel[key] for key in ("pullup_ohm", "led_series_ohm", "hysteresis_ohm", "threshold_top_ohm", "diode_or_pullup_ohm")])
            self.assertEqual(9, len(channel["ev_members"]))
            self.assertEqual(4, len(channel["threshold_members"]))
            self.assertEqual(2, len(channel["led_anode_members"]))
        self.assertEqual(["10000", "12000"], [row["threshold_bottom_ohm"] for row in result["channels"]])
        self.assertEqual(8, len(result["shared_any_node"]["members"]))
        self.assertEqual(10, len(result["shared_any_node"]["diode_cathode_frontier"]))
        self.assertFalse(result["qualified"])
        self.assertFalse(result["full_EV_qualified"])
        self.assertFalse(result["shared_any_node"]["other_ev_loads_traversed"])
        self.assertTrue(result["unresolved"])
        self.assertEqual(self.baseline, self.data)
        result["components"].clear()
        self.assertTrue(fixture.extract(self.data, self.reviews)["components"])

    def test_removed_duplicate_and_extra_ev_loads_rejected(self):
        for mutation in ("remove", "duplicate", "extra"):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(self.baseline)
                if mutation == "extra":
                    self.row("c5_evidence_main_pullup.END_1")["net"] = "EV_N1_C5"
                else:
                    row = self.row("c5_tx_led.K")
                    if mutation == "remove":
                        self.data["nets"]["rows"].remove(row)
                    else:
                        self.data["nets"]["rows"].append(copy.deepcopy(row))
                with self.assertRaises(ValueError):
                    fixture.extract(self.data, self.reviews)

    def test_m1_wrong_contact_shared_net_or_h0_assignment_rejected(self):
        for endpoint, field, value in (("m1_ui_plug.P42", "net", "EV_N7_IR"),
                ("m1_rf_receptacle.P46", "physical", "42"), ("m1_ui_plug.P42", "reference", "J99")):
            with self.subTest(endpoint=endpoint, field=field):
                self.data = copy.deepcopy(self.baseline)
                self.row(endpoint)[field] = value
                with self.assertRaises(ValueError):
                    fixture.extract(self.data, self.reviews)
        self.data = copy.deepcopy(self.baseline)
        next(row for row in self.data["h0"]["interboard_rebaseline"]["pin_map"] if row["contact"] == 42)["net"] = "EV_N7_IR"
        with self.assertRaisesRegex(ValueError, "H0 M1"):
            fixture.extract(self.data, self.reviews)

    def test_pullup_led_polarity_hysteresis_and_threshold_routes_rejected(self):
        endpoints = ("c5_evidence_output_pullup.END_1", "ir_tx_led_series.END_1", "c5_tx_led.A",
                     "ir_evidence_hysteresis.END_2", "c5_evidence_threshold_bottom.END_2",
                     "ir_evidence_threshold_top.END_1", "evidence_cmp_a.IN3_N", "evidence_cmp_a.IN2_P")
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.data = copy.deepcopy(self.baseline)
                self.row(endpoint)["net"] = "WRONG"
                with self.assertRaisesRegex(ValueError, "contact/net/type"):
                    fixture.extract(self.data, self.reviews)

    def test_extra_threshold_anode_and_aggregate_loads_rejected(self):
        for net in ("EV_THRESH_7_IR", "C5_TX_LED_A", "ANY_TX_AON_N"):
            with self.subTest(net=net):
                self.data = copy.deepcopy(self.baseline)
                self.row("c5_evidence_main_pullup.END_1")["net"] = net
                with self.assertRaisesRegex(ValueError, "membership"):
                    fixture.extract(self.data, self.reviews)

    def test_shared_pullup_and_each_diode_frontier_connection_rejected(self):
        for endpoint in ("any_tx_aon_pullup.END_1", "any_tx_aon_pullup.END_2", "safety_controller.PA22",
                         "slow_io_s3_evidence_iso.A", "evidence_or_0.K1", "evidence_or_3.K2",
                         "evidence_or_4.A_COMMON", "evidence_or_4.K2"):
            with self.subTest(endpoint=endpoint):
                self.data = copy.deepcopy(self.baseline)
                self.row(endpoint)["net"] = "WRONG"
                with self.assertRaisesRegex(ValueError, "contact/net/type"):
                    fixture.extract(self.data, self.reviews)

    def test_exact_resistor_kind_mpn_reference_and_sources_required(self):
        for mutation in ("kind", "mpn", "reference", "source"):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(self.baseline)
                device = self.data["devices"]["devices"]["yageo_rc0402fr_0710kl"]
                if mutation in ("kind", "mpn"):
                    device[mutation] = "WRONG"
                elif mutation == "reference":
                    next(row for row in self.data["instances"]["rows"] if row["instance"] == "any_tx_aon_pullup")["reference"] = "R999"
                    for row in self.data["nets"]["rows"]:
                        if row["instance"] == "any_tx_aon_pullup":
                            row["reference"] = "R999"
                else:
                    device["source"] = {}
                with self.assertRaises(ValueError):
                    fixture.extract(self.data, self.reviews)

    def test_driver_type_supply_and_reviewed_mpn_must_match(self):
        reviews = copy.deepcopy(self.reviews)
        reviews["ti_tlv1824_pwr"]["pins"]["1"]["type"] = "output"
        with self.assertRaisesRegex(ValueError, "contact/net/type"):
            fixture.extract(self.data, reviews)
        reviews = copy.deepcopy(self.reviews)
        reviews["ti_tca9535_pwr"]["mpn"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "reviewed MPN"):
            fixture.extract(self.data, reviews)
        for endpoint in ("evidence_mask.VCC", "safety_controller.VDD", "evidence_cmp_a.VPLUS", "c5.3V3"):
            with self.subTest(endpoint=endpoint):
                self.data = copy.deepcopy(self.baseline)
                self.row(endpoint)["net"] = "WRONG"
                with self.assertRaisesRegex(ValueError, "contact/net/type"):
                    fixture.extract(self.data, self.reviews)

    def test_overlay_and_stale_provenance_rejected(self):
        overlay = candidate.make_candidate(self.data, self.reviews, "main_schmitt")
        with self.assertRaisesRegex(ValueError, "baseline native"):
            fixture.extract(overlay, self.reviews)
        self.data["nets"]["sources"]["instances"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale"):
            fixture.extract(self.data, self.reviews)


if __name__ == "__main__":
    unittest.main()
