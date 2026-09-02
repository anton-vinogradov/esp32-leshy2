import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-mechanical-stack.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-mechanical-stack-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_mechanical_stack.py"
SVG = ROOT / "docs/images/h6-r2-mechanical-stack.svg"


class H6R2MechanicalStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_stack_passes_at_all_declared_tolerance_corners(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual([], self.audit["errors"])
        self.assertGreaterEqual(
            self.audit["stack"]["thread_available_at_nut_minimum_mm"], 2.0
        )
        self.assertGreaterEqual(
            self.audit["stack"]["thread_beyond_nut_minimum_mm"], 0.15
        )
        self.assertLessEqual(
            self.audit["stack"]["thread_beyond_nut_maximum_mm"], 2.1
        )
        self.assertGreaterEqual(
            self.audit["stack"]["minimum_tip_clearance_to_outer_surface_mm"], 0.08
        )

    def test_exact_hardware_and_native_axes_are_locked(self):
        self.assertEqual("50M025045P020", self.audit["selected_hardware"]["screw"])
        self.assertEqual("04M025045HN", self.audit["selected_hardware"]["nut"])
        self.assertEqual("007.02.611", self.audit["selected_hardware"]["compression_stop"])
        self.assertTrue(self.audit["geometry"]["mounting_axes_match_native_pcbs"])
        self.assertEqual(4, self.audit["geometry"]["mounting_axis_count"])

    def test_m1_is_not_structural_and_each_board_has_independent_capture(self):
        self.assertEqual("none", self.audit["geometry"]["m1_structural_role"])
        self.assertEqual(4, self.audit["geometry"]["capture_segments_per_board"])
        self.assertGreaterEqual(
            self.audit["geometry"]["calculated_minimum_pilot_diametral_clearance_mm"],
            0.15,
        )

    def test_outputs_are_reproducible(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def test_preview_explains_each_load_path(self):
        text = SVG.read_text(encoding="utf-8")
        self.assertIn("WHAT HOLDS WHAT", text)
        self.assertIn("M1 carries no enclosure load", text)
        self.assertIn("one loose screw does not load M1", text)


if __name__ == "__main__":
    unittest.main()
