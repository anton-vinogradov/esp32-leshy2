import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class H3R2MethodContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(
            (ROOT / "hardware/verification/generated/H3-R2-method-contract.json").read_text(encoding="utf-8")
        )

    def test_complete_method_and_rule_surface(self):
        summary = self.result["summary"]
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(239, summary["parameter_rows"])
        self.assertEqual(239, summary["assigned_parameter_rows"])
        self.assertEqual(9, summary["parameter_classes"])
        self.assertEqual(7, summary["workstreams"])
        self.assertEqual(9, summary["methods"])
        self.assertEqual(12, summary["pass_fail_rules"])
        self.assertEqual(166, summary["explicit_unresolved_until_extraction"])
        self.assertEqual(0, summary["open_method_questions"])
        self.assertEqual(0, summary["errors"])

    def test_every_assignment_is_fail_closed_and_owned(self):
        known = {row["id"] for row in self.result["methods"]}
        assignments = self.result["parameter_method_assignments"]
        self.assertEqual(239, len(assignments))
        for row in assignments:
            self.assertTrue(row["owner_workstreams"], row["device_id"])
            self.assertTrue(row["method_ids"], row["device_id"])
            self.assertTrue(set(row["method_ids"]).issubset(known), row["device_id"])
            if row["parameter_state"] == "explicit_extraction_queue":
                self.assertEqual("unresolved_fail", row["missing_parameter_disposition"])

    def test_reproducibility_and_authorization_are_fail_closed(self):
        self.assertTrue(self.result["toolchain"]["runtime_accepted"])
        self.assertEqual([], self.result["toolchain"]["third_party_runtime_dependencies"])
        self.assertEqual("forbidden", self.result["toolchain"]["network_during_regeneration"])
        self.assertEqual("forbidden", self.result["toolchain"]["acceptance_randomness"])
        self.assertTrue(self.result["authorization"]["advance_to_h3_r2_1"])
        self.assertFalse(self.result["authorization"]["placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])
        self.assertFalse(self.result["authorization"]["fabrication"])

    def test_hashes_and_public_docs_are_current(self):
        for relative, expected in self.result["source_sha256"].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), relative)
        for relative in ("docs/verification-methods.md", "docs/verification-methods.ru.md"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("H3-R2.0.3", page, relative)
            self.assertIn("239", page, relative)
            self.assertNotIn("historical R1", page, relative)


if __name__ == "__main__":
    unittest.main()
