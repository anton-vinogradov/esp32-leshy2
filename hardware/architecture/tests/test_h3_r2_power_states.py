import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class H3R2PowerStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / "hardware/verification/generated/H3-R2-power-state-register.json").read_text(encoding="utf-8"))

    def test_complete_state_surface(self):
        summary = self.result["summary"]
        self.assertEqual("pass", self.result["status"])
        self.assertEqual(43, summary["source_charge_states"])
        self.assertEqual(10, summary["signal_groups"])
        self.assertEqual(28, summary["group_modes"])
        self.assertEqual(56, summary["operating_profiles"])
        self.assertEqual(2266, summary["legal_states"])
        self.assertEqual(0, summary["invariant_violations"])

    def test_r2_added_and_concurrent_modes_are_present(self):
        profiles = {(row["signal_group"], row["group_mode"]) for row in self.result["operating_profiles"]}
        for mode in ("3PRX", "1PTX_2PRX", "2PTX_1PRX", "3PTX"):
            self.assertIn(("NRF24", mode), profiles)
        self.assertIn(("LORA_CAP", "U219_CC1101_NFC_RX_ONLY"), profiles)
        self.assertIn(("BROADCAST_RX", "AIRBAND_118_137_RX"), profiles)

    def test_non_run_modes_never_carry_payload_group(self):
        for row in self.result["states"]:
            if row["system_mode"] != "RUN":
                self.assertEqual("NONE", row["signal_group"], row["id"])

    def test_hashes_and_authorization(self):
        for relative, expected in self.result["source_sha256"].items():
            self.assertEqual(expected, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), relative)
        self.assertTrue(self.result["authorization"]["advance_to_h3_r2_1_2"])
        self.assertFalse(self.result["authorization"]["placement_or_routing"])
        self.assertFalse(self.result["authorization"]["purchasing"])
        self.assertFalse(self.result["authorization"]["fabrication"])

    def test_public_pages_are_current_r2(self):
        for relative in ("docs/power-state-register.md", "docs/power-state-register.ru.md"):
            page = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("H3-R2.1.1", page)
            self.assertNotIn("historical R1", page)


if __name__ == "__main__":
    unittest.main()
