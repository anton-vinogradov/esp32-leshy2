"""Independent nominal Grove datum fixtures; no native-placement qualification.

Seeed/NS-Tech 320110032.pdf sheet 1 and official Seeed OPL commit b0035c51
register the body against two solder-land rows. Existing solder lands are
deliberately unchanged; these tests must also run without KiCad installed.
"""

import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
ECAD = ROOT / "hardware/ecad"
FOOTPRINT = ECAD / "libraries/Leshy2.pretty/1125R-SMT-4P.kicad_mod"
EVIDENCE = ROOT / "hardware/layout/h6-r2-grove-geometry-evidence.json"
sys.path.insert(0, str(ECAD))
import h2_rf_u214_m5_ext as generator  # noqa: E402


# Fixed pre-correction copper contract, not derived from the generator.
PADS = [
    ('1', 3.0, -3.815, 1.010, 2.740),
    ('2', 1.0, -3.815, 1.010, 2.740),
    ('3', -1.0, -3.815, 1.010, 2.740),
    ('4', -3.0, -3.815, 1.010, 2.740),
    ('', -5.405, 3.685, 1.500, 3.000),
    ('', 5.405, 3.685, 1.500, 3.000),
]


def rectangle(source, layer):
    lines = [line for line in source.splitlines()
             if '(fp_rect ' in line and f'(layer "{layer}")' in line]
    if len(lines) != 1:
        raise ValueError(f"expected one {layer} rectangle")
    points = re.findall(r'\((?:start|end) ([-\d.]+) ([-\d.]+)\)', lines[0])
    return tuple(float(value) for point in points for value in point)


def b_point(point, anchor, rotation):
    """Independent KiCad B-side mirror, then clockwise-positive rotation."""
    x, y = point[0], -point[1]
    angle = math.radians(-rotation)
    return (anchor[0] + x * math.cos(angle) - y * math.sin(angle),
            anchor[1] + x * math.sin(angle) + y * math.cos(angle))


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class GroveGeometryTests(unittest.TestCase):
    def setUp(self):
        self.source = FOOTPRINT.read_text()
        self.evidence = json.loads(EVIDENCE.read_text())

    def test_generator_and_controlled_library_agree(self):
        self.assertEqual({FOOTPRINT: self.source}, generator.footprint_outputs())
        self.assertEqual(hashlib.sha256(FOOTPRINT.read_bytes()).hexdigest(),
                         self.evidence['footprint_sha256'])

    def test_all_six_original_pad_records_are_unchanged(self):
        actual = [line.strip() for line in self.source.splitlines() if '(pad ' in line]
        expected = [
            f'(pad "{name}" smd rect (at {x:.3f} {y:.3f}) '
            f'(size {w:.3f} {h:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"))'
            for name, x, y, w, h in PADS
        ]
        self.assertEqual(expected, actual)
        self.assertNotIn('(model ', self.source, 'do not borrow an unreviewed 3D body')

    def test_body_registers_to_both_independent_official_cad_rows(self):
        signal_offset = -3.815 - (-4.79970)
        anchor_offset = 3.685 - 2.69838
        self.assertAlmostEqual(.98470, signal_offset)
        self.assertAlmostEqual(.98662, anchor_offset)
        self.assertAlmostEqual(.00192, anchor_offset - signal_offset)
        bounds = rectangle(self.source, 'F.Fab')
        self.assertEqual((-6.0, -3.565, 6.0, 5.535), bounds)
        body_y = (bounds[1] + bounds[3]) / 2
        for offset in (signal_offset, anchor_offset):
            self.assertLess(abs(body_y - offset), .002)
        self.assertAlmostEqual(12.0, bounds[2] - bounds[0])
        self.assertAlmostEqual(9.10, bounds[3] - bounds[1])

    def test_old_centred_body_fails_the_independent_fixture(self):
        old_body_y = 0.0
        self.assertGreater(abs(old_body_y - .98470), .98)
        self.assertGreater(abs(old_body_y - .98662), .98)
        self.assertNotEqual((-6.0, -4.55, 6.0, 4.55), rectangle(self.source, 'F.Fab'))

    def test_engineering_courtyard_covers_body_and_all_lands(self):
        courtyard = rectangle(self.source, 'F.CrtYd')
        self.assertEqual((-6.45, -5.55, 6.45, 5.85), courtyard)
        objects = [rectangle(self.source, 'F.Fab')]
        objects += [(x-w/2, y-h/2, x+w/2, y+h/2) for _, x, y, w, h in PADS]
        margins = []
        for obj in objects:
            margins.extend((obj[0]-courtyard[0], obj[1]-courtyard[1],
                            courtyard[2]-obj[2], courtyard[3]-obj[3]))
        self.assertGreaterEqual(min(margins), .25)
        self.assertAlmostEqual(.295, min(margins))
        self.assertIn('not a manufacturer PCB-edge datum', self.source)

    def test_b180_mouth_faces_bottom_and_preserves_nominal_copper_margin(self):
        anchor = (57, 144.30)
        centre = b_point((0, .985), anchor, 180)
        mouth = b_point((0, 5.535), anchor, 180)
        self.assertGreater(mouth[1], centre[1])
        self.assertAlmostEqual(149.835, mouth[1])
        max_copper = max(b_point((x+dx*w/2, y+dy*h/2), anchor, 180)[1]
                         for _, x, y, w, h in PADS for dx in (-1, 1) for dy in (-1, 1))
        self.assertAlmostEqual(149.485, max_copper)
        self.assertAlmostEqual(.515, 150-max_copper)
        self.assertLess(b_point((0, 5.535), anchor, 0)[1],
                        b_point((0, .985), anchor, 0)[1])

    def test_rotating_at_old_anchor_still_puts_copper_outside_board(self):
        maximum = 145.45 + 3.685 + 3.0/2
        self.assertAlmostEqual(150.635, maximum)
        self.assertGreater(maximum, 150)

    def test_native_candidate_is_rejected_not_relabelled_as_pass(self):
        candidate = self.evidence['native_candidate_review']
        self.assertEqual([57.0, 144.30], candidate['anchor_mm'])
        self.assertEqual('B.Cu', candidate['side'])
        self.assertEqual(180, candidate['rotation_deg'])
        self.assertEqual('rejected_collision', candidate['status'])
        self.assertFalse(candidate['accepted_for_native_integration'])
        conflicts = candidate['same_side_courtyard_intersections']
        self.assertEqual({'J1', 'C29', 'U2'}, {item['reference'] for item in conflicts})
        for item in conflicts:
            self.assertTrue(overlap(candidate['observed_kicad_courtyard_bbox_mm'],
                                    item['observed_kicad_courtyard_bbox_mm']))

    def test_evidence_preserves_geometry_only_and_nominal_precision_boundary(self):
        self.assertEqual('1125R-SMT-4P', self.evidence['mpn'])
        self.assertFalse(self.evidence['pads_or_mpn_changed'])
        self.assertFalse(self.evidence['native_files_modified'])
        self.assertFalse(self.evidence['fabrication_ready'])
        self.assertEqual('controlled_library_geometry_corrected_native_integration_pending',
                         self.evidence['status'])
        self.assertIn('not manufacturing tolerance', self.evidence['alignment']['precision_limit'])
        self.assertTrue(all(row['url'].startswith('https://') for row in self.evidence['evidence']))


if __name__ == '__main__':
    unittest.main()
