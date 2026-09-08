"""Historical interface evidence and current identities have separate authority.

The Sep-7 observation is immutable. Three exact later selections reconcile its
identity coverage to current R2, but do not promote old poses/findings to a fresh
mechanical pass. Current silkscreen retains its separate live-input hash gate.
"""

import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT_PATH = "hardware/layout/h6-r2-connector-review-findings.json"
SNAPSHOT_SHA256 = "8dd449e5a8f704b25c193149690991e71c490edee9497f75d8eaa4125bc1be81"

# Closed list, not an automatic allowance for every future cost substitution.
# A new MPN change needs its own explicit transition and evidence review.
ACCEPTED_TRANSITIONS = {
    ("LESHY2-RF-R2", "SW5"): {
        "instance": "power_command_switch",
        "old_device": "ck_js102011scqn", "old_mpn": "C&K JS102011SCQN",
        "new_device": "ck_js102011saqn", "new_mpn": "C&K JS102011SAQN",
        "footprint": "Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN",
        "evidence": "hardware/procurement/h6-js102011saqn-selection-review.json",
        "selection_field": "selected_mpn", "selection_value": "JS102011SAQN",
        "primary": "https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-js-series-datasheet?assetguid=aba42b08-0d2c-423b-813d-a2faa5a3bb14",
        "former_field": "previous_mpn_retained_for_history", "former_value": "JS102011SCQN",
    },
    ("LESHY2-RF-R2", "U83"): {
        "instance": "headphone_jack",
        "old_device": "same_sky_sj_43504_smt_tr", "old_mpn": "Same Sky SJ-43504-SMT-TR",
        "new_device": "same_sky_sj_43515ts_smt_tr", "new_mpn": "Same Sky SJ-43515TS-SMT-TR",
        "footprint": "Leshy2_R2:SJ-43515TS-SMT-TR",
        "evidence": "hardware/procurement/h6-sj43515ts-selection-review.json",
        "selection_field": "selected_mpn", "selection_value": "SJ-43515TS-SMT-TR",
        "primary": "https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf",
        "former_field": "historical_device_retained", "former_value": "same_sky_sj_43504_smt_tr",
    },
    ("LESHY2-UI-R2", "U23"): {
        "instance": "ir_carrier",
        "old_device": "vishay_tsmp95000tt", "old_mpn": "Vishay TSMP95000TT",
        "new_device": "vishay_tsmp95000tr", "new_mpn": "Vishay TSMP95000TR",
        "footprint": "Leshy2:Vishay-Heimdall-SMD-TR",
        "evidence": "hardware/procurement/h6-tsmp95000tr-candidate-review.json",
        "selection_field": "candidate_mpn", "selection_value": "TSMP95000TR",
        "primary": "https://www.vishay.com/docs/82907/tsmp95000.pdf",
        "former_field": "former_mpn", "former_value": "Vishay TSMP95000TT",
    },
}


def load(name):
    return json.loads((ROOT / name).read_text())


class InterfaceReviewTests(unittest.TestCase):
    def assert_identity_coverage(self, review, ledger, devices, replacements, evidence):
        expected = {(r["project"], r["reference"]) for r in ledger if r["reference"].startswith("J")}
        rows = review["interfaces"]
        keys = [(r["board"], r["reference"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(expected, {key for key in keys if key[1].startswith("J")})
        self.assertEqual(31, len(expected))
        self.assertEqual(74, len(rows))
        native = {(r["project"], r["reference"]): r for r in ledger}
        self.assertEqual(len(ledger), len(native), "duplicate current native reference")
        seen_transitions = set()
        for r in rows:
            key = r["board"], r["reference"]
            self.assertIn(key, native)
            row = native[key]
            self.assertEqual(row["instance"], r["instance"])
            self.assertEqual(devices[r["device_id"]]["mpn"], r["mpn"], "archived exact identity lost")
            self.assertEqual(devices[row["device_id"]]["mpn"], row["mpn"], "current exact identity drifted")
            transition = ACCEPTED_TRANSITIONS.get(key)
            if transition is None:
                self.assertEqual(row["mpn"], r["mpn"], "unreviewed MPN transition")
                self.assertEqual(row["device_id"], r["device_id"], "unreviewed device transition")
            else:
                seen_transitions.add(key)
                self.assertEqual(transition["instance"], r["instance"])
                self.assertEqual(transition["old_device"], r["device_id"])
                self.assertEqual(transition["old_mpn"], r["mpn"])
                self.assertEqual(transition["new_device"], row["device_id"])
                self.assertEqual(transition["new_mpn"], row["mpn"])
                self.assertEqual(transition["footprint"], row["footprint"])
                selected = replacements[transition["old_device"]]
                self.assertEqual(transition["new_device"], selected["device_id"])
                self.assertEqual(transition["new_mpn"], selected["mpn"])
                self.assertEqual(transition["evidence"], selected["evidence"])
                proof = evidence[transition["evidence"]]
                self.assertEqual(transition["selection_value"], proof[transition["selection_field"]])
                self.assertEqual(transition["former_value"], proof[transition["former_field"]])
                self.assertEqual(transition["primary"], proof["manufacturer_evidence"]["url"])
                self.assertTrue(proof["checked"])
                self.assertTrue(proof["status"].startswith("selected"))
            self.assertIn("verified_scope", r)
            self.assertIn("remaining", r)
        self.assertEqual(set(ACCEPTED_TRANSITIONS), seen_transitions)

    def identity_inputs(self):
        return (
            load(SNAPSHOT_PATH),
            load("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"],
            load("hardware/architecture/devices.json")["devices"],
            load("hardware/product-design/h1-r2-cost-review.json")["r2_device_replacements"],
            {t["evidence"]: load(t["evidence"]) for t in ACCEPTED_TRANSITIONS.values()},
        )

    def test_all_native_j_references_are_enumerated_once_with_reviewed_identity_transitions(self):
        self.assert_identity_coverage(*self.identity_inputs())

    def test_immutable_observation_is_not_rewritten_to_current_mpn_or_pose(self):
        self.assertEqual(SNAPSHOT_SHA256, hashlib.sha256((ROOT / SNAPSHOT_PATH).read_bytes()).hexdigest())
        review = load(SNAPSHOT_PATH)
        self.assertEqual("H6-R2-CONNECTOR-REVIEW-2026-09-07", review["id"])
        self.assertEqual("2026-09-07T16:24:49Z", review["checked_at_utc"])

    def test_unknown_transition_and_missing_evidence_do_not_pass(self):
        original = self.identity_inputs()
        for mutation in ("unknown_mpn", "wrong_accepted_identity", "wrong_selection", "missing_evidence", "wrong_primary", "missing_row", "duplicate_row"):
            with self.subTest(mutation=mutation):
                review, ledger, devices, replacements, evidence = copy.deepcopy(original)
                audio = next(r for r in ledger if r["instance"] == "headphone_jack")
                audio_proof = ACCEPTED_TRANSITIONS[("LESHY2-RF-R2", "U83")]["evidence"]
                if mutation == "unknown_mpn":
                    other = next(r for r in ledger if r["instance"] == "product_usb_connector")
                    # Even a real, registered part is not automatically an
                    # accepted substitute for a different interface instance.
                    other["device_id"] = "gct_usb4105_gf_a"
                    other["mpn"] = devices[other["device_id"]]["mpn"]
                elif mutation == "wrong_accepted_identity":
                    audio["device_id"] = "same_sky_sj_43504_smt_tr"
                    audio["mpn"] = "Same Sky SJ-43504-SMT-TR"
                elif mutation == "wrong_selection":
                    evidence[audio_proof]["selected_mpn"] = "SJ-43516-SMT-TR"
                elif mutation == "missing_evidence":
                    replacements["same_sky_sj_43504_smt_tr"]["evidence"] = ""
                elif mutation == "wrong_primary":
                    evidence[audio_proof]["manufacturer_evidence"]["url"] = "https://example.invalid/catalog"
                elif mutation == "missing_row":
                    review["interfaces"].pop()
                elif mutation == "duplicate_row":
                    review["interfaces"].append(copy.deepcopy(review["interfaces"][0]))
                with self.assertRaises(AssertionError):
                    self.assert_identity_coverage(review, ledger, devices, replacements, evidence)

    def test_snapshot_never_claims_complete_metrology_or_release(self):
        review = load("hardware/layout/h6-r2-connector-review-findings.json")
        self.assertFalse(review["whole_interface_gate_pass"])
        self.assertTrue(review["provenance"]["immutable_observation"])
        for key in ("full_connector_metrology_complete", "electrical_pinmap_revalidated",
                    "closed_sandwich_access_proven"):
            self.assertFalse(review["coverage"][key])
        mechanical = load("hardware/layout/h6-r2-interface-review-findings.json")
        self.assertFalse(mechanical["manufacturing_released"])
        self.assertFalse(mechanical["production_modified_by_this_review"])
        for digest in review["provenance"]["boards_sha256"].values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_published_user_silkscreen_matches_current_inputs(self):
        audit = load("hardware/layout/generated/H6-R2-user-silkscreen-audit.json")
        self.assertEqual("pass_scoped", audit["status"])
        self.assertFalse(audit["production_release_authorized"])
        # 63 interface labels plus one approved use notice on each outer face.
        self.assertEqual(65, sum(row["required_count"] for row in audit["boards"]))
        for path, digest in audit["inputs_sha256"].items():
            self.assertFalse(Path(path).is_absolute())
            self.assertEqual(digest, hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), path)
        for row in audit["boards"]:
            self.assertFalse(row["errors"])
            self.assertFalse(row["geometry_candidates"])
            self.assertEqual(row["required_count"], row["matched_count"])


if __name__ == "__main__":
    unittest.main()
