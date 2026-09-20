"""A commanded-state connectivity path is not a voltage/damage guarantee."""

import copy
import unittest
from unittest.mock import patch

from hardware.verification import h6_r2_power_domain_crossings as gate
from hardware.verification import h6_r2_acceptance_adapters as adapters


class PowerDomainCrossingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = {key: gate.load(gate.ROOT / path) for key, path in gate.INPUTS.items()}
        cls.pin_reviews = gate.semantics.reviewed_maps([gate.load(p) for p in gate.semantics.MAPS], cls.original["material"]["groups"])
        cls.state = gate.state_snapshot()

    def setUp(self):
        self.data = copy.deepcopy(self.original)
        self.reviews = copy.deepcopy(self.pin_reviews)

    def run_gate(self, **kwargs):
        return gate.evaluate(self.data, self.reviews, self.state, **kwargs)

    def endpoint(self, name):
        return next(r for r in self.data["nets"]["rows"] if r["endpoint"] == name)

    def crossing(self, report, name):
        return next(r for r in report["crossings"] if r["receiver"]["instance"] + "." + r["receiver"]["contact"] == name)

    def proof(self):
        return {"device_id": "esp32_c5_wroom_1u_n8r8", "mpn": "ESP32-C5-WROOM-1U-N8R8", "pads": ["21", "23"],
                "supply_contacts": ["3V3"], "parameter": "powered_off_input_voltage_tolerance", "supply_v": ["0", "0"],
                "input_v": ["0", "3.6"], "source": {"path": "work/synthetic-input-proof.pdf", "sha256": "a" * 64,
                "url": "https://example.invalid/fixture-only", "revision": "test", "selector": "input VCC=0 row", "reviewed_on": "2026-09-20"}}

    def test_current_scan_finds_both_c5_inputs_without_claiming_damage(self):
        result = self.run_gate()
        for endpoint, net in (("c5.GPIO23", "EV_N1_C5"), ("c5.GPIO24", "EV_N7_IR")):
            row = self.crossing(result, endpoint)
            self.assertEqual(net, row["net"])
            self.assertEqual("missing_off_state_tolerance", row["finding_kind"])
            self.assertEqual("3V3_MAIN", row["receiver_supply"]["domain"])
            self.assertTrue(any(r["kind"] == "resistor_to_live_rail" for r in row["sources"]))
            self.assertFalse(row["pin_voltage_bounded"])
            self.assertFalse(row["numerical_incompatibility_proven"])
        self.assertFalse(result["qualified"])
        self.assertFalse(result["physical_rail_state_proven"])
        self.assertGreater(result["scanned_instances"], 1000)
        gate.validate_result(result)

    def test_arbitrary_renamed_native_net_is_still_detected(self):
        for row in self.data["nets"]["rows"]:
            if row["net"] == "EV_N1_C5":
                row["net"] = "RENAMED_ANY_SIGNAL"
        self.assertEqual("RENAMED_ANY_SIGNAL", self.crossing(self.run_gate(), "c5.GPIO23")["net"])

    def test_missing_receiver_contact_cannot_silently_reduce_coverage(self):
        self.data["nets"]["rows"].remove(self.endpoint("c5.GPIO23"))
        with self.assertRaisesRegex(ValueError, "contact coverage"):
            self.run_gate()

    def test_added_receiver_is_discovered_not_closed_world_by_ev_list(self):
        source = next(r for r in self.data["instances"]["rows"] if r["instance"] == "c5")
        new = {**source, "instance": "extra_main_receiver", "reference": "U999"}
        self.data["instances"]["rows"].append(new)
        rows = [r for r in self.data["nets"]["rows"] if r["instance"] == "c5"]
        self.data["nets"]["rows"].extend({**r, "instance": new["instance"], "reference": new["reference"],
                                         "endpoint": new["instance"] + "." + r["contact"]} for r in rows)
        self.assertEqual("EV_N1_C5", self.crossing(self.run_gate(), "extra_main_receiver.GPIO23")["net"])

    def test_open_drain_without_live_pullup_is_not_high_source(self):
        # Move only the actual comparator and receiver to an otherwise empty
        # local net. No LED/resistor/TCA GPIO is silently followed into it.
        self.endpoint("evidence_cmp_a.OUT2")["net"] = "OD_ONLY"
        self.endpoint("c5.GPIO23")["net"] = "OD_ONLY"
        self.assertFalse(any(r["net"] == "OD_ONLY" for r in self.run_gate()["crossings"]))

    def test_live_pullup_is_detected_even_with_only_open_drain_driver(self):
        for endpoint in ("evidence_cmp_a.OUT2", "c5.GPIO23", "c5_evidence_output_pullup.END_2"):
            self.endpoint(endpoint)["net"] = "OD_PLUS_RESISTOR"
        row = self.crossing(self.run_gate(), "c5.GPIO23")
        self.assertEqual(["resistor_to_live_rail"], [r["kind"] for r in row["sources"]])

    def test_main_pullup_does_not_become_aon_source(self):
        for endpoint in ("evidence_cmp_a.OUT2", "c5.GPIO23", "c5_evidence_output_pullup.END_2"):
            self.endpoint(endpoint)["net"] = "OD_PLUS_MAIN_RESISTOR"
        self.endpoint("c5_evidence_output_pullup.END_1")["net"] = "3V3_MAIN"
        self.assertFalse(any(r["net"] == "OD_PLUS_MAIN_RESISTOR" for r in self.run_gate()["crossings"]))

    def test_direct_live_output_is_discovered_without_a_resistor(self):
        self.endpoint("safe_latch.Q_N")["net"] = "ARBITRARY_DIRECT"
        self.endpoint("slow_io.P07")["net"] = "ARBITRARY_DIRECT"
        row = self.crossing(self.run_gate(), "slow_io.P07")
        self.assertEqual("potential_direct_high_drive", row["sources"][0]["kind"])

    def test_input_tied_directly_to_assumed_live_rail_is_discovered(self):
        self.endpoint("c5.GPIO23")["net"] = "AON_SAFE_3V3"
        row = self.crossing(self.run_gate(), "c5.GPIO23")
        source = next(r for r in row["sources"] if r["kind"] == "assumed_live_rail")
        self.assertEqual("AON_SAFE_3V3", source["net"])
        self.assertFalse(source["physical_voltage_proven"])
        self.assertFalse(row["pin_voltage_bounded"])

    def test_same_net_name_on_unconnected_boards_is_not_a_connection(self):
        self.endpoint("safe_latch.Q_N")["net"] = "TWO_LOCAL_LABELS"
        self.endpoint("c5.GPIO23")["net"] = "TWO_LOCAL_LABELS"
        self.assertFalse(any(r["net"] == "TWO_LOCAL_LABELS" for r in self.run_gate()["crossings"]))

    def test_m1_mismatch_cannot_join_unrelated_nets(self):
        self.endpoint("m1_ui_plug.P42")["net"] = "WRONG_MATE"
        with self.assertRaisesRegex(ValueError, "M1 canonical"):
            self.run_gate()

    def test_grounded_inputs_are_not_falsely_live_from_bias_resistors(self):
        self.assertFalse(any(r["net"] in gate.GROUND for r in self.run_gate()["crossings"]))

    def test_live_receiver_is_not_reported_as_commanded_off(self):
        self.endpoint("c5.3V3")["net"] = "AON_SAFE_3V3"
        self.assertFalse(any(r["receiver"]["instance"] == "c5" for r in self.run_gate()["crossings"]))

    def test_multi_supply_signal_ownership_is_explicitly_unknown(self):
        rows = self.run_gate()["unknown_supply_ownership"]
        self.assertTrue(any(r["receiver"]["net"] == "RF_SLOW_IO_ALERT" and r["receiver"]["instance"] == "rf_rp" for r in rows))
        self.assertTrue(any(r["receiver"]["net"] == "HUB_AON_ALERT_N" and r["receiver"]["instance"] == "hub_rp" for r in rows))

    def test_generic_output_ioff_prose_never_clears_input_review(self):
        self.data["devices"]["devices"]["esp32_c5_wroom_1u_n8r8"]["electrical_contract"] = {"partial_power_down": "Ioff supports outputs at VCC=0"}
        self.assertEqual("missing_off_state_tolerance", self.crossing(self.run_gate(), "c5.GPIO23")["finding_kind"])

    def test_exact_input_evidence_is_not_an_unmodeled_voltage_proof(self):
        proof = self.proof()
        result = self.run_gate(proofs=[proof], proof_hashes={proof["source"]["path"]: proof["source"]["sha256"]})
        row = self.crossing(result, "c5.GPIO23")
        self.assertEqual("off_state_input_evidence_requires_voltage_review", row["finding_kind"])
        self.assertFalse(row["qualified"])
        self.assertFalse(row["pin_voltage_bounded"])

    def test_stale_wrong_mpn_output_or_supply_proof_is_rejected(self):
        for field, value, error in (("mpn", "WRONG", "MPN"), ("parameter", "output_ioff", "input tolerance"),
                                    ("supply_v", ["3.3", "3.3"], "input tolerance"),
                                    ("supply_contacts", ["EN"], "supply ownership")):
            with self.subTest(field=field):
                proof = self.proof()
                proof[field] = value
                with self.assertRaisesRegex(ValueError, error):
                    self.run_gate(proofs=[proof], proof_hashes={proof["source"]["path"]: "a" * 64})
        with self.assertRaisesRegex(ValueError, "stale off-state"):
            self.run_gate(proofs=[self.proof()], proof_hashes={"work/synthetic-input-proof.pdf": "b" * 64})

    def test_duplicate_proofs_and_nonfinite_domains_are_rejected(self):
        proof = self.proof()
        hashes = {proof["source"]["path"]: "a" * 64}
        with self.assertRaisesRegex(ValueError, "duplicate off-state"):
            self.run_gate(proofs=[proof, proof], proof_hashes=hashes)
        for value in (["0", "NaN"], ["0", "Infinity"], ["3", "0"], [False, "1"]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_gate(proofs=[{**proof, "input_v": value}], proof_hashes=hashes)

    def test_native_and_material_duplicates_fail_closed(self):
        mutations = [lambda: self.data["nets"]["rows"].append(copy.deepcopy(self.endpoint("c5.GPIO23"))),
                     lambda: self.data["instances"]["rows"].append(copy.deepcopy(self.data["instances"]["rows"][0])),
                     lambda: self.data["material"]["groups"][0]["contacts"].append(copy.deepcopy(self.data["material"]["groups"][0]["contacts"][0]))]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.data = copy.deepcopy(self.original)
                mutate()
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    self.run_gate()

    def test_reviewed_supply_type_loss_is_unknown_not_assumed_off(self):
        del self.reviews["esp32_c5_wroom_1u_n8r8"]["pins"]["2"]
        result = self.run_gate()
        self.assertFalse(any(r["receiver"]["instance"] == "c5" for r in result["crossings"]))
        self.assertTrue(any(r["receiver"]["instance"] == "c5" for r in result["unknown_supply_ownership"]))

    def test_ledger_provenance_missing_or_stale_is_rejected(self):
        contracts = {key: gate.load(gate.ROOT / path) for key, path in gate.LEDGER_CONTRACTS.items()}
        hashes = gate.snapshot()
        del self.data["nets"]["sources"]["instances"]
        with self.assertRaisesRegex(ValueError, "membership"):
            gate.validate_provenance(self.data, contracts, hashes)
        self.data = copy.deepcopy(self.original)
        self.data["material"]["sources"]["device_register"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale"):
            gate.validate_provenance(self.data, contracts, hashes)

    def test_stale_h3_prerequisite_is_not_a_state_authority(self):
        original_load = gate.load
        def stale(path):
            result = original_load(path)
            if path == gate.freeze.OUTPUT:
                result["source_sha256"].pop(next(iter(result["source_sha256"])))
            return result
        with patch.object(gate, "load", side_effect=stale), self.assertRaisesRegex(ValueError, "stale H3"):
            gate.state_snapshot()

    def test_changed_sources_mid_build_are_rejected(self):
        before = gate.snapshot()
        with patch.object(gate, "snapshot", side_effect=[before, {}]), self.assertRaisesRegex(ValueError, "changed during"):
            gate.build()

    def test_result_cannot_self_qualify_or_assert_damage(self):
        for key in ("qualified", "physical_rail_state_proven", "gate_closed"):
            result = self.run_gate()
            result[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                gate.validate_result(result)
        result = self.run_gate()
        result["crossings"][0]["numerical_incompatibility_proven"] = True
        with self.assertRaises(ValueError):
            gate.validate_result(result)

    def test_existing_acceptance_registry_runs_the_read_only_screen(self):
        result = adapters.run_check("electrical.power_domain_crossings")
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual("recomputed_and_validated", result["details"]["evidence_status"])
        self.assertFalse(result["details"]["gate_closed"])
        self.assertTrue(result["details"]["crossings"])


if __name__ == "__main__":
    unittest.main()
