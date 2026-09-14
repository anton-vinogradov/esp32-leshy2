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
        self.assertEqual(609, summary["direct_power_connected_instances"])
        self.assertEqual(16, summary["indirect_powered_instances"])
        self.assertEqual(625, summary["power_connected_instances"])
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
        for profile in ("SUPPORT", "NRF24", "CC1101", "IR", "BROADCAST_RX", "BROADCAST_RX_AIRBAND", "VOICE", "DISPLAY_BACKLIGHT", "STORAGE", "CAP_SLOT", "M5_UNIT"):
            self.assertIn(profile, profiles)
        self.assertEqual(6, len(self.result["external_load_lines"]))
        self.assertIn("DISPLAY", {row["profile"] for row in self.result["external_load_lines"]})

    def test_two_added_c5_instances_have_exact_separate_aon_owners(self):
        # Stable instance UIDs, not sequential LOAD ids (which shift on insert).
        for instance, reference, device_id, state in (
            ("c5_service_path_logic", "U59", "ti_sn74lv20apwr",
             "candidate_current_seed_requires_applicability_review"),
            ("c5_service_path_logic_bypass", "C86", "yageo_cc0402krx7r9bb104",
             "exact_nonload_parameter_extraction_required"),
        ):
            rows = [row for row in self.result["load_lines"]
                    if row["instance_uid"] == "LESHY2-UI-R2:" + instance]
            self.assertEqual(1, len(rows), instance)
            row = rows[0]
            self.assertEqual((reference, device_id), (row["reference"], row["device_id"]))
            self.assertEqual(["AON_SAFE_3V3"], row["canonical_rails"])
            self.assertEqual(["ALWAYS_ON"], row["profiles"])
            self.assertEqual("H3-R2.1.3", row["parameter_owner"])
            self.assertEqual(state, row["parameter_state"])

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
