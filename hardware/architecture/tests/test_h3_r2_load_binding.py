import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class H3R2LoadBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / "hardware/verification/generated/H3-R2-load-binding.json").read_text(encoding="utf-8"))

    def test_every_discovered_instance_has_one_line(self):
        summary = self.result["summary"]
        self.assertEqual("pass", self.result["status"])
        self.assertGreater(summary["power_connected_instances"], 250)
        self.assertEqual(summary["power_connected_instances"], summary["bound_instance_lines"])
        self.assertEqual(595, summary["direct_power_connected_instances"])
        self.assertEqual(16, summary["indirect_powered_instances"])
        self.assertEqual(0, summary["unbound_power_connected_instances"])
        self.assertEqual(0, summary["duplicate_instance_lines"])
        self.assertEqual(0, summary["source_missing"])
        self.assertEqual(0, summary["hidden_miscellaneous_allowances"])
        self.assertEqual(17, summary["reviewed_power_nets_required"])
        self.assertEqual(0, summary["reviewed_power_nets_missing"])
        self.assertEqual(0, summary["errors"])

    def test_rails_profiles_and_external_contracts_are_complete(self):
        rails = self.result["summary"]["canonical_rail_bindings"]
        for rail in ("AON_SAFE_3V3", "3V3_MAIN", "VVOICE_4V", "5V_EXT_ACTIVE_BRANCH", "PACK_DIRECT", "SOURCE_OVERHEAD"):
            self.assertIn(rail, rails)
        profiles = self.result["summary"]["profile_bindings"]
        for profile in ("SUPPORT", "NRF24", "CC1101", "IR", "BROADCAST_RX", "BROADCAST_RX_AIRBAND", "VOICE", "DISPLAY", "STORAGE", "CAP_SLOT", "M5_UNIT"):
            self.assertIn(profile, profiles)
        self.assertEqual(6, len(self.result["external_load_lines"]))

    def test_every_line_is_source_bound_and_fail_closed(self):
        for row in self.result["load_lines"]:
            self.assertTrue(row["rail_bindings"], row["id"])
            self.assertTrue(row["canonical_rails"], row["id"])
            self.assertTrue(row["source"]["url"], row["id"])
            self.assertIn(row["parameter_owner"], ("H3-R2.1.3", "H3-R2.1.4"))
            self.assertIn(row["parameter_state"], (
                "candidate_current_seed_requires_applicability_review",
                "explicit_parameter_extraction_required",
                "exact_nonload_parameter_extraction_required",
            ))

    def test_hashes_and_no_downstream_authorization(self):
        for relative, expected in self.result["source_sha256"].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), relative)
        self.assertTrue(self.result["authorization"]["advance_to_h3_r2_1_3"])
        self.assertFalse(self.result["authorization"]["numeric_dc_pass_claim"])
        self.assertFalse(self.result["authorization"]["placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])
        self.assertFalse(self.result["authorization"]["fabrication"])


if __name__ == "__main__":
    unittest.main()
