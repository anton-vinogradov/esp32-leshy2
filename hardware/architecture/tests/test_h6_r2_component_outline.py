"""Native board material masks must not invent a rectangular PCB or hide cuts."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("component_outline_renderer", ROOT / "hardware/layout/h6_r2_component_render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class Chain:
    def __init__(self, points): self.points = points
    def PointCount(self): return len(self.points)
    def CPoint(self, i): return SimpleNamespace(x=self.points[i][0], y=self.points[i][1])


class Polygons:
    outer = [(0, 0), (80, 0), (80, 150), (66.43, 150), (66.43, 148.8),
             (56.43, 148.8), (56.43, 150), (0, 150)]
    hole = [(26.5, 31.5), (53.5, 31.5), (53.5, 32.7), (26.5, 32.7)]
    def OutlineCount(self): return 1
    def COutline(self, i): return Chain(self.outer)
    def HoleCount(self, i): return 1
    def CHole(self, i, j): return Chain(self.hole)


class NativeBoardShapeTests(unittest.TestCase):
    def shape(self, valid=True, polygon_type=Polygons):
        api = SimpleNamespace(SHAPE_POLY_SET=polygon_type, ToMM=lambda value: value)
        calls = []
        def outlines(*args):
            calls.append(args)
            return valid
        board = SimpleNamespace(GetBoardPolygonOutlines=outlines)
        with patch.dict("sys.modules", {"pcbnew": api}):
            result = renderer.native_board_shape(board)
        self.assertEqual((False, None, False, False), calls[0][1:])
        return result

    def test_actual_native_notch_and_internal_slot_not_contract_rectangle(self):
        shape = self.shape()
        self.assertIn("66.430000 148.800000", shape["outer"])
        self.assertIn("56.430000 150.000000", shape["outer"])
        self.assertNotIn("26.500000 31.500000", shape["outer"])
        self.assertIn("26.500000 31.500000", shape["material"])
        self.assertEqual(2, shape["material"].count(" Z"))
        self.assertEqual(1, shape["outer"].count(" Z"))

    def test_invalid_or_empty_native_outline_never_falls_back_to_a_rectangle(self):
        with self.assertRaisesRegex(RuntimeError, "no rectangular render fallback"):
            self.shape(False)
        class Empty(Polygons):
            def OutlineCount(self): return 0
        with self.assertRaisesRegex(RuntimeError, "no board outline"):
            self.shape(polygon_type=Empty)

    def test_opening_and_opposite_face_clip_share_same_native_outer_contour(self):
        shape = self.shape()
        for face in ("outer", "inner"):
            output = renderer.panel("ui", face, "", "", [], "", "", shape)
            root = ET.fromstring("<svg>" + output + "</svg>")
            material = next(node for node in root.iter() if node.get("data-role") == "native-board-material")
            clip = next(node for node in root.iter() if node.tag == "clipPath").find("path")
            self.assertEqual(shape["material"], material.get("d"))
            self.assertEqual("evenodd", material.get("fill-rule"))
            self.assertEqual("M-8 -14H88V158H-8Z " + shape["outer"], clip.get("d"))
            self.assertNotIn("26.500000 31.500000", clip.get("d"))
            self.assertEqual(int(face == "inner"), output.count('transform="translate(80 0) scale(-1 1)"'))


if __name__ == "__main__":
    unittest.main()
