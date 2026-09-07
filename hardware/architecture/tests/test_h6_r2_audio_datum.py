"""Regress the proven audio land correction without claiming a finished notch."""

import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_ui_audio_codec_headset as generator


class AudioDatumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path, cls.text = next(iter(generator.footprint_outputs().items()))
        cls.review = json.loads((ROOT / "hardware/layout/h6-r2-audio-datum-review.json").read_text())
        cls.pads = {
            n: tuple(float(v) for v in (x, y, w, h))
            for n, x, y, w, h in re.findall(
                r'\(pad "(\d+)" smd rect \(at ([-\d.]+) ([-\d.]+)\) '
                r'\(size ([\d.]+) ([\d.]+)\)', cls.text)
        }

    def test_generator_matches_controlled_library(self):
        self.assertEqual(self.text, self.path.read_text())

    def test_six_contacts_and_land_sizes_preserved(self):
        self.assertEqual(set("123456"), set(self.pads))
        for values in self.pads.values():
            self.assertEqual((1.7, 1.5), values[2:])

    def test_independently_transcribed_longitudinal_drawing_dimensions(self):
        # Independent primary-drawing numbers, not the JSON's expected values.
        datum_y = {"1": 2.75, "2": 9.30, "3": 5.50, "4": 2.75, "5": 11.50, "6": 10.55}
        for number, drawing_y in datum_y.items():
            self.assertAlmostEqual(drawing_y - 5.75, self.pads[number][1])

    def test_switch_tail_rows_are_not_symmetric(self):
        self.assertAlmostEqual(.95, self.pads["5"][1] - self.pads["6"][1])
        self.assertAlmostEqual(2.20, self.pads["5"][1] - self.pads["2"][1])

    def test_asymmetric_x_columns_follow_linear_drawing_dimensions(self):
        for n in "245":
            self.assertAlmostEqual(-3.35 - (1.75 - 1.7 / 2), self.pads[n][0])
        for n in "136":
            self.assertAlmostEqual(3.45 + (1.75 - 1.7 / 2), self.pads[n][0])
        self.assertAlmostEqual(8.60, self.pads["1"][0] - self.pads["4"][0])

    def test_copper_envelope_contains_all_lands(self):
        self.assertIn('(start -5.300 -6.000) (end 5.400 6.750)', self.text)
        for x, y, w, h in self.pads.values():
            self.assertGreaterEqual(x - w / 2, -5.3)
            self.assertLessEqual(x + w / 2, 5.4)
            self.assertGreaterEqual(y - h / 2, -6)
            self.assertLessEqual(y + h / 2, 6.75)

    def test_partial_correction_cannot_claim_fabrication_readiness(self):
        self.assertIn("UNQUALIFIED", self.text)
        self.assertIn("not a fabrication-ready footprint", self.text)
        self.assertNotIn('(layer "Edge.Cuts")', self.text)
        self.assertFalse(self.review["production_release_authorized"])
        self.assertFalse(self.review["native_board_updated"])
        self.assertFalse(self.review["land_geometry"]["electrical_numbering_changed"])
        self.assertEqual(3, len(self.review["errata_to_earlier_review"]))


if __name__ == "__main__":
    unittest.main()
