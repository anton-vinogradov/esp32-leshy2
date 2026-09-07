"""Bounded source-triage checks: no KiCad launch or production mutation."""

import copy
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
        self.hashes = {**self.review["source_sha256"], **self.audit["source_hashes"]}

    def check(self):
        return triage.validate(self.review, self.audit, self.ledger, self.material, self.hashes)

    def assert_rejected(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            self.check()

    def test_exact_current_warning_and_conflict_coverage_is_only_triage(self):
        result = self.check()
        self.assertEqual(21, result["power_findings"])
        self.assertEqual(1, result["explained_conflicts"])
        self.assertEqual(96, result["source_path_endpoints"])
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
        self.assert_rejected("coverage is not exact 21")

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


if __name__ == "__main__":
    unittest.main()
