import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class H3R2ParameterProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(
            (ROOT / "hardware/verification/generated/H3-R2-parameter-provenance.json").read_text(encoding="utf-8")
        )

    def test_exact_r2_counts_and_ownership(self):
        summary = self.result["summary"]
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(242, summary["component_groups"])
        self.assertEqual(237, summary["board_component_groups"])
        self.assertEqual(5, summary["explicit_non_pcba_groups"])
        self.assertEqual(1187, summary["fitted_board_instances"])
        self.assertEqual(242, summary["owned_component_groups"])
        self.assertEqual(242, summary["model_method_candidates"])
        self.assertEqual(0, summary["errors"])
        self.assertEqual(0, summary["open_decisions"])

    def test_every_group_has_provenance_and_no_silent_model(self):
        rows = self.result["rows"]
        self.assertEqual(242, len(rows))
        self.assertEqual(242, len({row["device_id"] for row in rows}))
        for row in rows:
            self.assertTrue(row["mpn"], row["device_id"])
            self.assertTrue(row["source"]["url"], row["device_id"])
            self.assertTrue(row["source"]["checked"], row["device_id"])
            self.assertTrue(row["required_parameter_groups"], row["device_id"])
            self.assertTrue(row["model_method_candidate"], row["device_id"])
            self.assertEqual("candidate_pending_H3-R2.0.3", row["model_method_state"])
            self.assertTrue(row["owner_workstreams"], row["device_id"])

    def test_factory_catalog_gaps_are_exact_and_bounded(self):
        findings = {row["device_id"]: row for row in self.result["bounded_source_findings"]}
        self.assertEqual(
            {"chilisin_cs0805_r27j_s", "suzhou_liming_3225_27_00_10_10_10_a"},
            set(findings),
        )
        self.assertTrue(all(row["owner"] == "H3-R2.3" for row in findings.values()))
        self.assertEqual(2, self.result["summary"]["bounded_source_findings"])
        self.assertTrue(self.result["authorization"]["advance_to_method_freeze"])
        self.assertFalse(self.result["authorization"]["placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])

    def test_dynamic_safety_chain_is_owned_by_h3_r2_2(self):
        required = {
            "murata_grm21br71e225ke11l",
            "nexperia_74lvc2g14gv_125",
            "ti_sn74lvc1g17_dckr",
            "ti_sn74lvc1g74_dcur",
            "ti_tps3435cakagddfr",
            "ti_tps3808g33_dbvr",
            "yageo_rc0402fr_07100kl",
        }
        rows = {row["device_id"]: row for row in self.result["rows"]}
        self.assertTrue(all("H3-R2.2" in rows[device_id]["owner_workstreams"] for device_id in required))

    def test_source_hashes_and_public_pages_are_current(self):
        for relative, expected in self.result["source_sha256"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, relative)
        for relative in ("docs/parameter-model-register.md", "docs/parameter-model-register.ru.md"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("H3-R2.0.2", page, relative)
            self.assertIn("242", page, relative)
            self.assertIn("1187", page, relative)
            self.assertNotIn("# H3 parameters and models · historical R1", page, relative)


if __name__ == "__main__":
    unittest.main()
