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
        self.assertTrue(result["selection"]["jlcpcb_remains_primary"])
        self.assertTrue(all(result["checks"].values()))
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_prepared_message_cannot_be_mistaken_for_sent_or_ordered(self):
        page = (REPO / "hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md").read_text(encoding="utf-8")
        self.assertIn("prepared, not authorized to send", page)
        self.assertIn("not an order request", page)
        self.assertIn("H5-EVR07", page)


if __name__ == "__main__":
    unittest.main()
