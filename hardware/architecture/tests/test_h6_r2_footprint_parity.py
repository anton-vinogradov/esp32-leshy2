import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_footprint_parity as audit


class FootprintParityTests(unittest.TestCase):
    def test_comparison_preserves_identical_numbered_pad_multiplicity(self):
        row = {"number": "SH", "at_mm": [1,2], "size_mm": [1,1]}
        result = audit.compare_pad_rows([row,row], [row])
        self.assertEqual([row], result["native_only"])
        self.assertEqual([], result["library_only"])

    def test_each_changed_geometry_field_is_detected(self):
        row = {"number":"1", "at_mm":[1,2], "size_mm":[1,1],
               "drill_mm":[0,0], "layers":[0], "shape":1, "attribute":0,
               "rotation_deg":0, "drill_shape":0, "roundrect_ratio":0}
        for field in row:
            changed = copy.deepcopy(row)
            changed[field] = "changed"
            with self.subTest(field=field):
                result = audit.compare_pad_rows([changed], [row])
                self.assertEqual([changed], result["native_only"])
                self.assertEqual([row], result["library_only"])

    def test_pad_order_is_not_a_geometry_difference(self):
        a, b = {"number":"1"}, {"number":"2"}
        self.assertEqual({"native_only":[],"library_only":[]},
                         audit.compare_pad_rows([a,b],[b,a]))

    def test_polygon_winding_and_start_do_not_create_drift(self):
        ring = [(0, 0), (30, 0), (30, 20), (0, 20)]
        expected = audit.canonical_ring(ring)
        for points in (ring[2:] + ring[:2], list(reversed(ring)), ring + [ring[0]]):
            self.assertEqual(expected, audit.canonical_ring(points))
        self.assertNotEqual(expected, audit.canonical_ring([(0, 0), (30, 0), (31, 20), (0, 20)]))

    @unittest.skipUnless(audit.pcbnew is not None, "requires KiCad's Python")
    def test_current_custom_pad_primitive_mutations_preserve_enum_and_size_but_fail(self):
        pcbnew = audit.pcbnew
        for name, number in (("TI-RPW0010A-VQFN-HR-10", "1"),
                             ("CMEJ-0413-42-SMT-TR", "2")):
            with self.subTest(footprint=name):
                board = pcbnew.BOARD()
                fp = pcbnew.FootprintLoad(str(ROOT / "hardware/ecad/libraries/Leshy2.pretty"), name)
                board.Add(fp)
                pad = next(p for p in fp.Pads() if p.GetNumber() == number)
                before = audit.pad_rows(fp)
                shape, size = int(pad.GetShape()), (pad.GetSize().x, pad.GetSize().y)
                # Change only the actual primitive geometry, never its anchor.
                polygon = pcbnew.SHAPE_POLY_SET()
                polygon.NewOutline()
                for x, y in ((-.1, -.1), (.8, -.1), (.8, .4), (-.1, .4)):
                    polygon.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
                pad.DeletePrimitivesList(pcbnew.F_Cu)
                pad.AddPrimitivePoly(pcbnew.F_Cu, polygon, 0, True)
                self.assertEqual(shape, int(pad.GetShape()))
                self.assertEqual(size, (pad.GetSize().x, pad.GetSize().y))
                after = audit.pad_rows(fp)
                old_fields = lambda rows: [{k: v for k, v in row.items() if k != "copper_by_layer"} for row in rows]
                self.assertEqual(old_fields(before), old_fields(after))
                delta = audit.compare_pad_rows(before, after)
                self.assertTrue(delta["native_only"])
                self.assertTrue(delta["library_only"])
                del pad, fp, polygon, board

    @unittest.skipUnless(audit.pcbnew is not None, "requires KiCad's Python")
    def test_offset_trapezoid_and_chamfer_changes_are_detected(self):
        pcbnew = audit.pcbnew
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(ROOT / "hardware/ecad/libraries/Leshy2.pretty"), "TI-RPW0010A-VQFN-HR-10")
        board.Add(fp)
        pad = next(p for p in fp.Pads() if p.GetNumber() == "2")
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
        cases = ((pcbnew.PAD_SHAPE_RECT, lambda: pad.SetOffset(pcbnew.VECTOR2I(100000, 0))),
                 (pcbnew.PAD_SHAPE_TRAPEZOID, lambda: pad.SetDelta(pcbnew.VECTOR2I(100000, 0))),
                 (pcbnew.PAD_SHAPE_CHAMFERED_RECT, lambda: pad.SetChamferRectRatio(pad.GetChamferRectRatio() + .1)),
                 (pcbnew.PAD_SHAPE_CHAMFERED_RECT, lambda: pad.SetChamferPositions(2)))
        for shape, mutate in cases:
            with self.subTest(shape=shape):
                pad.SetShape(shape)
                pad.SetChamferPositions(1)
                before = audit.pad_rows(fp)
                mutate()
                after = audit.pad_rows(fp)
                self.assertTrue(audit.compare_pad_rows(before, after)["native_only"])
        del pad, fp, board

    def test_published_report_is_hash_bound_to_actual_native_boards(self):
        data = json.loads(audit.OUTPUT.read_text())
        self.assertEqual([], data["errors"])
        self.assertEqual(1218, data["summary"]["native_footprints"])
        self.assertEqual(1218, data["summary"]["checked_footprints"])
        for board in data["boards"]:
            self.assertEqual(board["board_sha256"], hashlib.sha256((ROOT/board["board"]).read_bytes()).hexdigest())
            self.assertEqual(board["native_footprint_count"], len(set(board["checked_references"])))

    def test_no_success_claim_when_stored_pad_deviations_exist(self):
        data = json.loads(audit.OUTPUT.read_text())
        count = sum(len(b["deviations"]) for b in data["boards"])
        self.assertEqual(count, data["summary"]["footprints_with_pad_geometry_drift"])
        self.assertEqual("open_native_library_drift" if count or data["errors"] else "pass", data["status"])
        self.assertFalse(data["fabrication_ready"])


if __name__ == "__main__":
    unittest.main()
