"""An enumerated audit is not an assembly release; current silk is hash-bound."""

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(name):
    return json.loads((ROOT / name).read_text())


class InterfaceReviewTests(unittest.TestCase):
    def test_all_native_j_references_are_enumerated_once(self):
        review = load("hardware/layout/h6-r2-connector-review-findings.json")
        ledger = load("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"]
        expected = {(r["project"], r["reference"]) for r in ledger if r["reference"].startswith("J")}
        rows = review["interfaces"]
        keys = [(r["board"], r["reference"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(expected, {key for key in keys if key[1].startswith("J")})
        self.assertEqual(31, len(expected))
        self.assertEqual(74, len(rows))
        native = {(r["project"], r["reference"]): r for r in ledger}
        for r in rows:
            row = native[r["board"], r["reference"]]
            self.assertEqual(row["instance"], r["instance"])
            self.assertEqual(row["mpn"], r["mpn"])
            self.assertIn("verified_scope", r)
            self.assertIn("remaining", r)

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
        self.assertEqual(53, sum(row["required_count"] for row in audit["boards"]))
        for path, digest in audit["inputs_sha256"].items():
            self.assertFalse(Path(path).is_absolute())
            self.assertEqual(digest, hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), path)
        for row in audit["boards"]:
            self.assertFalse(row["errors"])
            self.assertFalse(row["geometry_candidates"])
            self.assertEqual(row["required_count"], row["matched_count"])


if __name__ == "__main__":
    unittest.main()
