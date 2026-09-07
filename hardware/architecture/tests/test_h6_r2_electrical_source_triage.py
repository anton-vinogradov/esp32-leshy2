"""Bounded source-triage checks: no KiCad launch or production mutation."""

import copy
import hashlib
import json
import unittest

from hardware.verification import h6_r2_electrical_source_triage as triage


class ElectricalSourceTriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = (
            triage.load(triage.TRIAGE), triage.load(triage.AUDIT),
            triage.load(triage.LEDGER), triage.load(triage.MATERIAL),
        )

    def setUp(self):
        self.review, self.audit, self.ledger, self.material = copy.deepcopy(self.documents)
        # Unit fixtures model a matching filesystem. The read-only --check CLI
        # independently computes actual file digests rather than trusting these.
        # Source regeneration may be in progress; model the seven-map hash
        # surface here without mutating or claiming freshness of the real audit.
        self.audit["source_hashes"].update({p: value for p, value in self.review["source_sha256"].items() if p != triage.LEDGER})
        self.hashes = {**self.review["source_sha256"], **self.audit["source_hashes"]}

    def check(self):
        return triage.validate(self.review, self.audit, self.ledger, self.material, self.hashes)

    def assert_rejected(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            self.check()

    def refresh(self):
        return triage.refresh_observations(self.review, self.audit, self.ledger, self.material, self.hashes)

    def update_fixture_native_content_digest(self, project):
        content = json.dumps(project["native_erc"], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        project["erc_content_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()

    def rf_air_violation(self):
        project = next(p for p in self.audit["projects"] if p["project"] == "LESHY2-RF-R2")
        violation = next(v for s in project["native_erc"]["sheets"] for v in s.get("violations", []) if any("Symbol U53 " in i["description"] for i in v["items"]))
        return project, violation

    def test_exact_current_warning_and_conflict_coverage_is_only_triage(self):
        result = self.check()
        self.assertEqual(22, result["power_findings"])
        self.assertEqual(1, result["explained_conflicts"])
        self.assertEqual(102, result["source_path_endpoints"])
        self.assertIs(False, result["gate_closed"])

    def test_stale_or_missing_source_digest_is_rejected(self):
        self.hashes[triage.LEDGER] = "0" * 64
        self.assert_rejected("stale source hash")
        del self.review["source_sha256"][triage.LEDGER]
        self.assert_rejected("source hash coverage")

    def test_stale_native_audit_is_rejected_even_when_triage_hashes_match(self):
        native_only = next(p for p in self.audit["source_hashes"] if p not in self.review["source_sha256"])
        self.hashes[native_only] = "0" * 64
        self.assert_rejected("native audit stale")

    def test_native_source_cannot_be_deleted_to_hide_staleness(self):
        native_only = next(p for p in self.audit["source_hashes"] if p not in self.review["source_sha256"])
        del self.audit["source_hashes"][native_only]
        self.assert_rejected("native audit source hash coverage incomplete")

    def test_shared_pad_aliases_must_be_declared_and_on_the_same_net(self):
        group = next(g for g in self.material["groups"] if g["device_id"] == "alps_skrtlae010")
        group["shared_electrical_pads"] = {}
        self.assert_rejected("undeclared or inconsistent shared")
        group["shared_electrical_pads"] = {"1": ["C1", "C2"]}
        row = next(r for r in self.ledger["rows"] if r["instance"] == "rf_rp_boot_button" and r["contact"] == "C2")
        row["net"] = "WRONG_ALIAS_NET"
        self.assert_rejected("undeclared or inconsistent shared")

    def test_unknown_reported_pin_is_rejected(self):
        self.review["findings"][0]["pins"][0]["pin"] = "999"
        self.assert_rejected("unknown reported pin")

    def test_reported_net_or_contact_mismatch_is_rejected(self):
        self.review["findings"][0]["net"] = "NOT_POWER_GROUND"
        self.assert_rejected("reported pin/net mismatch")
        self.review["findings"][0]["net"] = "POWER_GROUND"
        self.review["findings"][0]["pins"][0]["contact"] = "3V3"
        self.assert_rejected("contact mismatch")

    def test_native_uuid_cannot_be_replaced_by_another_pin(self):
        self.review["findings"][0]["pins"][0]["uuid"] = "invented-pin-uuid"
        self.assert_rejected("power-warning coverage mismatch")

    def test_missing_or_duplicated_warning_is_rejected(self):
        self.review["findings"].pop()
        self.assert_rejected("power-warning coverage mismatch")
        self.review["findings"].append(copy.deepcopy(self.review["findings"][0]))
        self.assert_rejected("duplicate power-net")

    def test_native_coverage_cannot_be_shrunk_with_the_triage(self):
        project = self.audit["projects"][0]
        for sheet in project["native_erc"]["sheets"]:
            if sheet.get("violations"):
                sheet["violations"].pop()
                break
        project["erc_count_by_type"]["power_pin_not_driven"] -= 1
        self.update_fixture_native_content_digest(project)
        self.assert_rejected("coverage is not exact 22")

    def test_source_path_net_and_pad_must_match_exact_endpoint(self):
        node = self.review["findings"][0]["source_path"][0]
        node["net"] = "3V3_MAIN"
        self.assert_rejected("source-path pin/net mismatch")
        node["net"] = "POWER_GROUND"
        node["pads"] = ["999"]
        self.assert_rejected("source-path pin/net mismatch")

    def test_empty_source_path_or_obligations_is_rejected(self):
        row = self.review["findings"][0]
        row["source_path"] = []
        self.assert_rejected("source path is missing")
        row["source_path"] = copy.deepcopy(self.documents[0]["findings"][0]["source_path"])
        row["remaining_obligations"] = []
        self.assert_rejected("obligations missing")

    def test_false_gate_pass_and_production_authorization_are_rejected(self):
        self.review["summary"]["whole_electrical_gate_pass"] = True
        self.assert_rejected("whole gate pass")
        self.review["summary"]["whole_electrical_gate_pass"] = False
        self.review["authorization"]["fabrication"] = True
        self.assert_rejected("must not authorize")

    def test_per_net_clearance_claim_is_rejected(self):
        self.review["findings"][0]["disposition"] = "cleared"
        self.assert_rejected("falsely cleared")

    def test_unknown_classification_and_false_summary_are_rejected(self):
        self.review["findings"][0]["classification"] = "whole_rail_validated"
        self.assert_rejected("unknown power-triage classification")
        self.review["findings"][0]["classification"] = "external_return_boundary"
        self.review["summary"]["native_power_findings"] = 20
        self.assert_rejected("summary mismatch")

    def test_conflict_cannot_be_removed_or_globally_suppressed(self):
        self.review["conflicts"] = []
        self.assert_rejected("conflict explanation missing")
        self.review["conflicts"] = copy.deepcopy(self.documents[0]["conflicts"])
        self.review["conflicts"][0]["disposition"] = "globally_waived"
        self.assert_rejected("must not suppress ERC")

    def test_acdrv_pin_or_configuration_change_invalidates_explanation(self):
        self.review["conflicts"][0]["pins"][0]["pin"] = "24"
        self.assert_rejected("exact driver pins changed")
        self.review["conflicts"] = copy.deepcopy(self.documents[0]["conflicts"])
        self.review["conflicts"][0]["source_path"] = [n for n in self.review["conflicts"][0]["source_path"] if n["contact"] != "VAC1"]
        self.assert_rejected("VBUS-only configuration evidence incomplete")

    def test_native_conflict_uuid_and_manufacturer_evidence_are_required(self):
        self.review["conflicts"][0]["pins"][0]["uuid"] = "invented"
        self.assert_rejected("unexplained or changed native")
        self.review["conflicts"] = copy.deepcopy(self.documents[0]["conflicts"])
        self.review["conflicts"][0]["evidence"] = [e for e in self.review["conflicts"][0]["evidence"] if "url" not in e]
        self.assert_rejected("manufacturer configuration evidence missing")

    def test_native_connectivity_change_or_exclusion_is_rejected(self):
        self.audit["projects"][0]["native_connectivity_unchanged"] = False
        self.assert_rejected("connectivity is not verified")
        self.audit["projects"][0]["native_connectivity_unchanged"] = True
        violation = next(v for s in self.audit["projects"][0]["native_erc"]["sheets"] for v in s.get("violations", []))
        violation["excluded"] = True
        self.assert_rejected("finding is excluded")

    def test_source_paths_cannot_escape_repository(self):
        for path in ("../outside.json", "/etc/passwd"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unsafe source"):
                triage.digest_relative(path)

    def test_all_seven_reviewed_maps_are_required(self):
        expected = {f"hardware/verification/h6-electrical-pins-{name}.json" for name in ("power", "digital", "logic", "analog", "protection", "interfaces", "passives")}
        self.assertEqual(expected, triage.MAPS)
        for path in expected:
            with self.subTest(path=path):
                audit = copy.deepcopy(self.audit)
                del audit["source_hashes"][path]
                with self.assertRaisesRegex(ValueError, "native audit source hash coverage"):
                    triage.refresh_observations(self.review, audit, self.ledger, self.material, self.hashes)

    def test_air_bias_path_has_real_tps22919_and_both_choke_ends(self):
        row = next(r for r in self.review["findings"] if r["net"] == "AIR_LNA_OUT_BIASED")
        self.assertEqual("rf_bias_choke_feed_model_gap", row["classification"])
        self.assertEqual(("U53", "3", "RF_OUT_DC_IN"), tuple(row["pins"][0][k] for k in ("reference", "pin", "contact")))
        expected = {
            ("U60", "IN", ("1",), "3V3_MAIN"),
            ("U60", "ON", ("3",), "AIR_RX_EN"),
            ("U60", "VOUT", ("6",), "3V3_AIR_SWITCHED"),
            ("L23", "END_1", ("1",), "3V3_AIR_SWITCHED"),
            ("L23", "END_2", ("2",), "AIR_LNA_OUT_BIASED"),
            ("U53", "RF_OUT_DC_IN", ("3",), "AIR_LNA_OUT_BIASED"),
        }
        self.assertEqual(expected, {(n["reference"], n["contact"], tuple(n["pads"]), n["net"]) for n in row["source_path"]})
        self.assertTrue(any(e.get("url") == "https://www.minicircuits.com/WebStore/dashboardPdf?model=PGA-103%2B" and "choke" in e["section"] for e in row["evidence"]))
        source = next(r for r in self.ledger["rows"] if r["project"] == "LESHY2-RF-R2" and r["reference"] == "U60" and r["contact"] == "VOUT")
        self.assertEqual("ti_tps22919_dckr", source["device_id"])

    def test_refresh_changes_only_hashes_and_reported_pins(self):
        self.review["source_sha256"][triage.LEDGER] = "0" * 64
        audio = next(r for r in self.review["findings"] if r["net"] == "AUDIO_GROUND")
        audio["pins"] = [{"reference": "old-representative", "uuid": "old-observation"}]
        before = copy.deepcopy(self.review)
        refreshed = self.refresh()
        self.assertEqual(before, self.review, "refresh must not mutate its input")
        self.assertEqual(self.hashes[triage.LEDGER], refreshed["source_sha256"][triage.LEDGER])
        observed = next(r for r in refreshed["findings"] if r["net"] == "AUDIO_GROUND")["pins"][0]
        self.assertEqual(("U40", "3", "voice_audio_mux"), tuple(observed[k] for k in ("reference", "pin", "instance")))
        refreshed["source_sha256"] = before["source_sha256"]
        for key in ("findings", "conflicts"):
            for old, new in zip(before[key], refreshed[key]):
                new["pins"] = old["pins"]
        self.assertEqual(before, refreshed, "no paths, explanations, obligations, metadata or gate decisions may change")

    def test_refresh_rejects_stale_native_inputs_even_if_triage_was_stale(self):
        self.review["source_sha256"][triage.LEDGER] = "0" * 64
        path = next(p for p in self.audit["source_hashes"] if p not in triage.REQUIRED_SOURCES)
        self.hashes[path] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native audit stale source hash"):
            self.refresh()

    def test_refresh_rejects_new_net_without_auto_explanation(self):
        project, violation = self.rf_air_violation()
        violation["items"][0]["description"] = "Symbol U60 Pin 1 [IN, Power input, Line]"
        self.update_fixture_native_content_digest(project)
        before = copy.deepcopy(self.review)
        with self.assertRaisesRegex(ValueError, "project/type/net set changed"):
            self.refresh()
        self.assertEqual(before, self.review)

    def test_refresh_rejects_removed_reviewed_net(self):
        project, violation = self.rf_air_violation()
        sheet = next(s for s in project["native_erc"]["sheets"] if violation in s.get("violations", []))
        sheet["violations"].remove(violation)
        project["erc_count_by_type"]["power_pin_not_driven"] -= 1
        self.update_fixture_native_content_digest(project)
        with self.assertRaisesRegex(ValueError, "project/type/net set changed"):
            self.refresh()

    def test_refresh_rejects_changed_source_path_not_just_changed_representative(self):
        endpoint = next(r for r in self.ledger["rows"] if r["instance"] == "air_lna_bias_choke" and r["contact"] == "END_1")
        endpoint["net"] = "WRONG_SUPPLY"
        with self.assertRaisesRegex(ValueError, "source-path pin/net mismatch"):
            self.refresh()

    def test_all_source_path_nodes_bind_exact_device_and_mpn(self):
        _, endpoints = triage.indexes(self.ledger, self.material)
        nodes = [n for row in [*self.review["findings"], *self.review["conflicts"]] for n in row["source_path"]]
        self.assertEqual(102, len(nodes))
        for node in nodes:
            key = tuple(node[k] for k in ("project", "reference", "instance", "contact"))
            self.assertEqual((endpoints[key]["device_id"], endpoints[key]["mpn"]), (node["device_id"], node["mpn"]))

    def test_refresh_never_populates_or_corrects_missing_path_identity(self):
        for field in ("device_id", "mpn"):
            for value in (None, "wrong-exact-part"):
                with self.subTest(field=field, value=value):
                    node = self.review["findings"][0]["source_path"][0]
                    old = node[field]
                    if value is None:
                        del node[field]
                    else:
                        node[field] = value
                    before = copy.deepcopy(self.review)
                    self.assert_rejected("source-path exact device/MPN identity mismatch")
                    with self.assertRaisesRegex(ValueError, "source-path exact device/MPN identity mismatch"):
                        self.refresh()
                    self.assertEqual(before, self.review)
                    node[field] = old

    def test_refresh_rejects_changed_mpn_with_same_device_contacts_pads_and_nets(self):
        group = next(g for g in self.material["groups"] if g["device_id"] == "ti_tps22919_dckr")
        group["mpn"] = "different exact load-switch MPN"
        # Model an otherwise fresh native audit; old triage hashes may be stale.
        # Identity must stop a refresh even when net-level observations agree.
        self.review["source_sha256"][triage.MATERIAL] = "0" * 64
        before = copy.deepcopy(self.review)
        with self.assertRaisesRegex(ValueError, "source-path exact device/MPN identity mismatch"):
            self.refresh()
        self.assertEqual(before, self.review)

    def test_refresh_rejects_device_swap_even_if_mpn_pads_contacts_and_nets_match(self):
        original_id = "ti_tps22919_dckr"
        other_id = "test_same_pad_load_switch"
        group = copy.deepcopy(next(g for g in self.material["groups"] if g["device_id"] == original_id))
        group["device_id"] = other_id
        self.material["groups"].append(group)
        for row in self.ledger["rows"]:
            if row["instance"] == "airband_power_switch":
                self.assertEqual(original_id, row["device_id"])
                row["device_id"] = other_id
        self.review["source_sha256"][triage.LEDGER] = "0" * 64
        before = copy.deepcopy(self.review)
        with self.assertRaisesRegex(ValueError, "source-path exact device/MPN identity mismatch"):
            self.refresh()
        self.assertEqual(before, self.review)

    def test_refresh_rejects_fabricated_native_uuid_report(self):
        _, violation = self.rf_air_violation()
        violation["items"][0]["uuid"] = "invented"
        with self.assertRaisesRegex(ValueError, "observation content changed"):
            self.refresh()

    def test_refresh_rejects_unknown_or_duplicate_native_pin(self):
        project, violation = self.rf_air_violation()
        violation["items"][0]["description"] = "Symbol U53 Pin 999 [UNKNOWN, Power input, Line]"
        self.update_fixture_native_content_digest(project)
        with self.assertRaisesRegex(ValueError, "unknown native reported pin"):
            self.refresh()
        violation["items"][0]["description"] = "Symbol U60 Pin 2 [GND, Power input, Line]"
        self.update_fixture_native_content_digest(project)
        with self.assertRaisesRegex(ValueError, "duplicate native project/type/net"):
            self.refresh()

    def test_refresh_rejects_new_conflict_and_cannot_clear_the_gate(self):
        project = next(p for p in self.audit["projects"] if p["project"] == "LESHY2-RF-R2")
        violation = next(v for s in project["native_erc"]["sheets"] for v in s.get("violations", []) if v["type"] == "pin_to_pin")
        violation["type"] = "unconnected_pin"
        del project["erc_count_by_type"]["pin_to_pin"]
        project["erc_count_by_type"]["unconnected_pin"] = 1
        self.update_fixture_native_content_digest(project)
        with self.assertRaisesRegex(ValueError, "project/type/net set changed"):
            self.refresh()
        self.audit = copy.deepcopy(self.documents[1])
        self.audit["source_hashes"].update({p: value for p, value in self.review["source_sha256"].items() if p != triage.LEDGER})
        self.review["summary"]["whole_electrical_gate_pass"] = True
        with self.assertRaisesRegex(ValueError, "whole gate pass"):
            self.refresh()

    def test_refresh_never_invents_missing_reason_or_obligations(self):
        self.review["findings"][0]["reason"] = ""
        with self.assertRaisesRegex(ValueError, "missing triage reason"):
            self.refresh()


if __name__ == "__main__":
    unittest.main()
