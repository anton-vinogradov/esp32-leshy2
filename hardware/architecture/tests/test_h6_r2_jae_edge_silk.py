"""JAE edge-silk-only variant: independently pin all unchanged native geometry.

Expected geometry hash was taken from the reviewed KiCad 10.0.5 standard source
SHA256 6f6c1ac1efdec9479814ac5d8ea8a4453387b58099cae99fb835fc09e2a6dd00.
It is deliberately not recomputed from the generator or the new local variant.
JAE SJ121836 Rev.3 p2 sets local PCB edge -1.95 + 5.05 = 3.10 mm.
These checks do not authorize manufacture or replace actual-board native DRC.
"""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
NAME = "USB_C_Receptacle_JAE_DX07S016JA1R1500_EdgeSilk"
PATH = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty" / (NAME + ".kicad_mod")
GEOMETRY_SHA256 = "540794435d1da1cab216785cf7caca940a0b3348438e75408d93519ea1b35cb8"


def parse(text):
    stack, roots = [], []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
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
    values = children(node, kind)
    if len(values) != 1:
        raise ValueError(f"expected one {kind}")
    return values[0][1:]


def invariant_geometry(node):
    # Properties (including the original F.Fab Value), every pad occurrence,
    # drills, masks/paste, UUIDs, all Fab/CrtYd geometry and 3D remain included.
    return [part for part in node[2:] if not (
        isinstance(part, list) and (part[0] == "descr" or (
            part[0] == "fp_line" and field(part, "layer") == ["F.SilkS"])))]


def generator():
    spec = importlib.util.spec_from_file_location("jae_edge_silk", ROOT / "hardware/ecad/h2_r2_jae_edge_silk.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JAEEdgeSilkTests(unittest.TestCase):
    def setUp(self):
        self.node = parse(PATH.read_text())

    def assert_invariant_geometry(self, node):
        canonical = json.dumps(invariant_geometry(node), separators=(",", ":")).encode()
        self.assertEqual(GEOMETRY_SHA256, hashlib.sha256(canonical).hexdigest())

    def assert_edge_silk(self, node):
        lines = [line for line in children(node, "fp_line") if field(line, "layer") == ["F.SilkS"]]
        expected = {
            (-4.58, -1.215, -4.58, -.36), (4.58, -1.215, 4.58, -.36),
            (-4.58, 2.76, -4.58, 2.88), (4.58, 2.76, 4.58, 2.88),
        }
        self.assertEqual(4, len(lines))
        actual = set()
        for line in lines:
            actual.add(tuple(map(float, field(line, "start") + field(line, "end"))))
            stroke = children(line, "stroke")[0]
            self.assertEqual(["0.12"], field(stroke, "width"))
            self.assertEqual(["solid"], field(stroke, "type"))
        self.assertEqual(expected, actual)

    def test_exact_project_local_binding_preserves_mpn(self):
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        self.assertEqual("Leshy2_R2:" + NAME, contract["footprint_overrides"]["JAE DX07S016JA1R1500"])
        self.assertEqual(["footprint", NAME], self.node[:2])
        self.assertIn("KiCad CC-BY-SA 4.0 with Libraries Exception", field(self.node, "descr")[0])
        self.assertIn("source SHA256 6f6c1ac1", field(self.node, "descr")[0])

    def test_all_non_silk_native_content_matches_independent_reviewed_source_hash(self):
        self.assert_invariant_geometry(self.node)
        pads = children(self.node, "pad")
        self.assertEqual(24, len(pads))
        self.assertEqual(2, sum(p[2] == "np_thru_hole" for p in pads))

    def test_only_three_reviewed_silk_strokes_change(self):
        self.assert_edge_silk(self.node)
        # B180 at the reviewed anchor maps this local +Y toward bottom edge.
        self.assertAlmostEqual(150.0, 146.9 + (-1.95 + 5.05))
        self.assertAlmostEqual(.16, 150.0 - (146.9 + 2.88 + .12 / 2))
        self.assertGreater(.16, .15)

    def test_reproduces_reviewed_installed_source_without_touching_global_library(self):
        gen = generator()
        if not gen.DEFAULT_SOURCE.is_file():
            self.skipTest("supply content-pinned KiCad source with generator --source on this host")
        before = gen.DEFAULT_SOURCE.read_bytes()
        self.assertEqual(PATH.read_text(), gen.build(before))
        self.assertEqual(before, gen.DEFAULT_SOURCE.read_bytes())

    def test_unreviewed_or_already_modified_source_is_rejected(self):
        gen = generator()
        with self.assertRaisesRegex(ValueError, "unreviewed JAE source"):
            gen.build(PATH.read_bytes())
        with self.assertRaisesRegex(ValueError, "unreviewed JAE source"):
            gen.build(b'(footprint "unreviewed")\n')

    def test_guard_detects_pad_drill_mask_and_model_changes(self):
        for kind in ("pad", "drill", "mask", "model"):
            with self.subTest(kind=kind):
                node = copy.deepcopy(self.node)
                pads = children(node, "pad")
                if kind == "pad":
                    children(pads[0], "at")[0][1] = "9.99"
                elif kind == "drill":
                    drilled = next(p for p in pads if children(p, "drill"))
                    children(drilled, "drill")[0][-1] = "0.01"
                elif kind == "mask":
                    pad = next(p for p in pads if p[2] == "smd")
                    children(pad, "layers")[0].remove("F.Mask")
                else:
                    children(node, "model")[0][1] = "wrong.step"
                with self.assertRaises(AssertionError):
                    self.assert_invariant_geometry(node)

    def test_guard_detects_fab_courtyard_and_duplicate_pad_changes(self):
        for kind in ("F.Fab", "F.CrtYd", "duplicate"):
            with self.subTest(kind=kind):
                node = copy.deepcopy(self.node)
                if kind == "duplicate":
                    node.append(copy.deepcopy(children(node, "pad")[0]))
                else:
                    line = next(line for line in children(node, "fp_line") if field(line, "layer") == [kind])
                    children(line, "end")[0][2] = "2.88"
                with self.assertRaises(AssertionError):
                    self.assert_invariant_geometry(node)

    def test_guard_rejects_untrimmed_or_excessively_removed_silk(self):
        for kind in ("long", "missing", "width"):
            with self.subTest(kind=kind):
                node = copy.deepcopy(self.node)
                line = next(line for line in children(node, "fp_line") if field(line, "end") == ["-4.58", "2.88"])
                if kind == "long":
                    children(line, "end")[0][2] = "3.71"
                elif kind == "missing":
                    node.remove(line)
                else:
                    children(children(line, "stroke")[0], "width")[0][1] = "0.45"
                with self.assertRaises(AssertionError):
                    self.assert_edge_silk(node)


if __name__ == "__main__":
    unittest.main()
