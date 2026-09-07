"""IR physical land, body datum and optical-axis regressions.

Literal expectations are from Vishay 84209 Rev1.6 pp5/6, 82907 Rev1.0
pp2/4/6/7 and 82494 Rev2.4 pp2/7/8/9, reviewed 2026-09-07. Body-to-land
offsets are nominal seating constructions, not measured placement tolerances.
No test claims that the current native PCB has integrated these definitions.
"""

import copy
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
ECAD = ROOT / "hardware/ecad"
LIBRARY = ECAD / "libraries/Leshy2.pretty"
sys.path.insert(0, str(ECAD))
from h2_ui_c5_radio_ir_service import ir_footprint_outputs, footprint_outputs, footprint_for, pins_for

try:
    import pcbnew
except ImportError:
    pcbnew = None


def parse(source):
    stack, roots = [], []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', source):
        if token == "(":
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError("unbalanced close")
            stack.pop()
        else:
            if not stack:
                raise ValueError("atom outside expression")
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    if stack or len(roots) != 1:
        raise ValueError("unbalanced or multiple roots")
    return roots[0]


def children(node, kind):
    return [part for part in node[1:] if isinstance(part, list) and part[0] == kind]


def field(node, kind):
    rows = children(node, kind)
    if len(rows) != 1:
        raise ValueError(f"expected one {kind}")
    return rows[0][1:]


def load(name):
    return parse((LIBRARY / f"{name}.kicad_mod").read_text())


class IRFootprintTests(unittest.TestCase):
    def assert_lands(self, node, coordinates, size):
        pads = children(node, "pad")
        self.assertEqual(len(coordinates), len(pads))
        self.assertEqual(set(coordinates), {p[1] for p in pads})
        for p in pads:
            self.assertEqual(["smd", "rect"], p[2:4])
            self.assertEqual(coordinates[p[1]], tuple(map(float, field(p, "at"))))
            self.assertEqual(size, tuple(map(float, field(p, "size"))))
            self.assertEqual(["F.Cu", "F.Paste", "F.Mask"], field(p, "layers"))

    def assert_rectangle(self, node, layer, start, end):
        rects = [r for r in children(node, "fp_rect") if field(r, "layer") == [layer]]
        self.assertEqual(1, len(rects))
        self.assertEqual(start, tuple(map(float, field(rects[0], "start"))))
        self.assertEqual(end, tuple(map(float, field(rects[0], "end"))))

    def test_only_three_controlled_ir_files_are_reproducible(self):
        outputs = ir_footprint_outputs()
        self.assertEqual({"VSMY14940.kicad_mod", "Vishay-Heimdall-SMD-TT.kicad_mod",
                          "Vishay-Heimdall-SMD-TR.kicad_mod"}, {p.name for p in outputs})
        for path, source in outputs.items():
            self.assertEqual(source, path.read_text(), str(path))

    def test_emitter_recommended_lands_not_body_terminations(self):
        self.assert_lands(load("VSMY14940"), {"1": (-1.35, 0), "2": (1.35, 0)}, (.9, 1.4))

    def test_old_emitter_dimensions_and_duplicate_pad_are_rejected(self):
        original = load("VSMY14940")
        for change in ("pitch", "size", "duplicate", "layer"):
            node = copy.deepcopy(original)
            p = children(node, "pad")[0]
            if change == "pitch":
                children(p, "at")[0][1] = "-.9"
            elif change == "size":
                children(p, "size")[0][1:] = ["1.2", "1.0"]
            elif change == "duplicate":
                node.append(copy.deepcopy(p))
            else:
                children(p, "layers")[0][1] = "B.Cu"
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.assert_lands(node, {"1": (-1.35, 0), "2": (1.35, 0)}, (.9, 1.4))

    def test_receiver_lands_preserve_physical_pin_order(self):
        expected = {"1": (-1.905, 0), "2": (-.635, 0), "3": (.635, 0), "4": (1.905, 0)}
        for name in ("Vishay-Heimdall-SMD-TT", "Vishay-Heimdall-SMD-TR"):
            self.assert_lands(load(name), expected, (.8, 1.8))

    def test_body_datums_are_not_falsely_centred_on_pad_row(self):
        self.assert_rectangle(load("VSMY14940"), "F.Fab", (-1.5, -1.96), (1.5, .55))
        self.assert_rectangle(load("VSMY14940"), "F.CrtYd", (-2.05, -2.21), (2.05, .95))
        self.assert_rectangle(load("Vishay-Heimdall-SMD-TR"), "F.Fab", (-3.4, -.5), (3.4, 2.7))
        self.assert_rectangle(load("Vishay-Heimdall-SMD-TT"), "F.Fab", (-3.4, -2.4), (3.4, .6))

    def test_centered_receiver_body_regression_is_rejected(self):
        node = load("Vishay-Heimdall-SMD-TR")
        r = [r for r in children(node, "fp_rect") if field(r, "layer") == ["F.Fab"]][0]
        children(r, "start")[0][2] = "-1.6"
        children(r, "end")[0][2] = "1.6"
        with self.assertRaises(AssertionError):
            self.assert_rectangle(node, "F.Fab", (-3.4, -.5), (3.4, 2.7))

    def test_current_tt_and_tr_are_not_interchangeably_named(self):
        self.assertIn("optical axis +Z", field(load("Vishay-Heimdall-SMD-TT"), "descr")[0])
        self.assertIn("optical axis +Y", field(load("Vishay-Heimdall-SMD-TR"), "descr")[0])

    def test_historical_hint_is_preserved_separate_from_current_r2_override(self):
        self.assertEqual("Leshy2:Vishay-Heimdall-SMD-TT", footprint_for("ir_demod", "vishay_tsop75238tr"))
        self.assertEqual("Leshy2:Vishay-Heimdall-SMD-TT", footprint_for("ir_carrier", "vishay_tsmp95000tt"))
        self.assertNotIn(LIBRARY / "Vishay-Heimdall-SMD-TR.kicad_mod", footprint_outputs())
        self.assertIn(LIBRARY / "Vishay-Heimdall-SMD-TR.kicad_mod", ir_footprint_outputs())

    def test_electrical_contact_numbering_is_unchanged(self):
        data = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]
        for instance, key, names in (
            ("ir_emitter", "vishay_vsmy14940", {"ANODE": "1", "CATHODE": "2"}),
            ("ir_demod", "vishay_tsop75238tr", {"GND_1": "1", "VS": "2", "OUT": "3", "GND_4": "4"}),
            ("ir_carrier", "vishay_tsmp95000tt", {"GND_1": "1", "VS": "2", "CARRIER_OUT": "3", "GND_4": "4"}),
        ):
            self.assertEqual(names, {p.name: p.number for p in pins_for(instance, data[key])})


@unittest.skipIf(pcbnew is None, "requires KiCad Python; text/geometry tests still run")
class NativeIROpticalAxisTests(unittest.TestCase):
    def test_b_side_rotation_uses_actual_kicad_graphic_transform(self):
        # Flip exactly as production placement does, then inspect the explicit
        # Fab optical rays. Incorrect opposite rotation must point inward.
        for name, angle, length in (("VSMY14940", 270, 1.41),
                                    ("Vishay-Heimdall-SMD-TR", 90, 1.50)):
            for opposite in (False, True):
                board = pcbnew.BOARD()
                fp = pcbnew.FootprintLoad(str(LIBRARY), name)
                self.assertIsNotNone(fp)
                board.Add(fp)
                fp.Flip(pcbnew.VECTOR2I(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
                fp.SetOrientationDegrees((angle + (180 if opposite else 0)) % 360)
                rays = []
                for g in fp.GraphicalItems():
                    if not isinstance(g, pcbnew.PCB_SHAPE) or g.GetShape() != pcbnew.SHAPE_T_SEGMENT:
                        continue
                    a, b = pcbnew.ToMM(g.GetStart()), pcbnew.ToMM(g.GetEnd())
                    if abs(abs(b[0] - a[0]) - length) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
                        rays.append(b[0] - a[0])
                self.assertEqual(1 if name == "VSMY14940" else 2, len(rays))
                self.assertTrue(all(dx > 0 if opposite else dx < 0 for dx in rays))


if __name__ == "__main__":
    unittest.main()
