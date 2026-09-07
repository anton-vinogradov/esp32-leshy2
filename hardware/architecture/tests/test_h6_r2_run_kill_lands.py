"""C&K exact SC solder-land transcription, not an exterior access approval."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_rf_tx_safety_evidence as generator


class RunKillLandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path, cls.text = next(iter(generator.footprint_outputs().items()))
        cls.pads = {n: tuple(float(v) for v in (x,y,w,h)) for n,x,y,w,h in re.findall(
            r'\(pad "(\d+)" smd rect \(at ([-\d.]+) ([-\d.]+)\) '
            r'\(size ([\d.]+) ([\d.]+)\)', cls.text)}

    def test_generator_matches_library(self):
        self.assertEqual(self.text, self.path.read_text())

    def test_independent_manufacturer_linear_dimensions(self):
        # C&K JS series VL01/14/26 p5 lower SC drawing, top component view.
        # Three 1-mm-wide lands; 8-mm outside span and 3-mm clear inner gap.
        length = (8.0 - 3.0) / 2
        centre = 3.0 / 2 + length / 2
        self.assertEqual({"1": (-2.5, centre, 1., length),
                          "2": (0., -centre, 1., length),
                          "3": (2.5, centre, 1., length)}, self.pads)

    def test_common_is_not_on_same_row_as_throws(self):
        self.assertLess(self.pads["2"][1], 0)
        self.assertGreater(self.pads["1"][1], 0)
        self.assertEqual(self.pads["1"][1], self.pads["3"][1])

    def test_courtyard_has_quarter_mm_copper_and_body_margin(self):
        self.assertIn('(start -4.500 -4.250) (end 4.500 4.250)', self.text)
        for x,y,w,h in self.pads.values():
            self.assertGreaterEqual(x-w/2, -4.25)
            self.assertLessEqual(x+w/2, 4.25)
            self.assertGreaterEqual(y-h/2, -4)
            self.assertLessEqual(y+h/2, 4)

    def test_geometry_does_not_mislabel_top_actuator_as_side_exiting(self):
        self.assertIn('top actuator, NOT side-exiting', self.text)
        self.assertIn('native access remains open', self.text)


if __name__ == "__main__":
    unittest.main()
