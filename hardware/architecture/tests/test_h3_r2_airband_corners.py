import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "hardware/verification/generated/H3-R2-airband-corners.json"
SCRIPT = ROOT / "hardware/verification/h3_r2_airband_corners.py"


class H3R2AirbandCornerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_evidence_is_current(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_all_endpoint_corners_pass_the_reference_mask(self):
        self.assertEqual("pass", self.result["status"])
        self.assertEqual([], self.result["errors"])
        self.assertEqual(1024, self.result["method"]["corner_count"])
        self.assertGreater(self.result["minimum_margin_db"], 0.0)

    def test_factory_population_is_exact_and_current(self):
        population = self.result["factory_population"]
        self.assertEqual(18, population["fitted_parts"])
        self.assertEqual(10, population["distinct_mpns"])
        self.assertTrue(population["all_exact_mpns_stocked_standard_pcba_on_2026_08_31"])


if __name__ == "__main__":
    unittest.main()
