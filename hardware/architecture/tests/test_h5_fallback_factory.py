import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]


class H5FallbackFactoryTests(unittest.TestCase):
    def test_generated_fallback_readiness_is_current_and_fail_closed(self):
        subprocess.run(
            [sys.executable, "hardware/verification/h5_fallback_factory.py", "--check"],
            cwd=REPO,
            check=True,
        )
        result = json.loads(
            (REPO / "hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json").read_text(encoding="utf-8")
        )
        self.assertEqual("H5-EVR08", result["artifact"])
        self.assertEqual("pcbway", result["selection"]["first_fallback"])
        self.assertEqual("seeed-fusion", result["selection"]["second_source_pcba"])
        self.assertTrue(result["selection"]["jlcpcb_remains_pcba_reference"])
        self.assertFalse(result["selection"]["jlcpcb_remains_primary_full_device_factory"])
        self.assertEqual("primary_pcba_candidate_with_owner_final_assembly", result["primary_disposition"]["role"])
        self.assertEqual(2, result["primary_disposition"]["pcba_minimum_quantity"])
        self.assertFalse(result["primary_disposition"]["complete_enclosure_final_device_assembly"])
        self.assertTrue(all(result["checks"].values()))
        self.assertTrue(result["primary_disposition"]["owner_final_assembly_accepted"])
        self.assertEqual("optional_full_device_inquiry_response_open_pcba_path_unblocked", result["status"])
        self.assertEqual("message_sent", result["contact"]["result"])
        self.assertEqual("2026-09-02", result["contact"]["sent_on"])
        self.assertEqual("vinogradov.anton@gmail.com", result["contact"]["from"])
        self.assertEqual("service@pcbway.com", result["contact"]["to"])
        self.assertTrue(result["contact"]["information_only"])
        self.assertFalse(result["contact"]["commercial_action_created"])
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_sent_message_cannot_be_mistaken_for_an_order(self):
        page = (REPO / "hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md").read_text(encoding="utf-8")
        self.assertIn("sent on 2026-09-02", page)
        self.assertIn("vinogradov.anton@gmail.com", page)
        self.assertIn("service@pcbway.com", page)
        self.assertIn("not an order request", page)
        self.assertIn("H5-EVR07", page)


if __name__ == "__main__":
    unittest.main()
