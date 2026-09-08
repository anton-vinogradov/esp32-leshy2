"""Primary checkerboard polarity, isolated R2 repair, not mechanical acceptance."""

import ast
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_r2_holder_polarity as generator


def parse(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))

    def node(token):
        if token == "(":
            result = []
            for token in tokens:
                if token == ")":
                    return result
                result.append(node(token))
            raise ValueError("unterminated footprint")
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        return ast.literal_eval(token) if token.startswith('"') else token

    result = node(next(tokens))
    if next(tokens, None) is not None:
        raise ValueError("extra expression")
    return result


def children(node, key):
    return [item for item in node if isinstance(item, list) and item[0] == key]


def field(node, key):
    result = children(node, key)
    if len(result) != 1:
        raise ValueError(f"expected one {key}")
    return result[0][1:]


def checkerboard(footprint):
    # Independent manufacturer TOP view and unchanged project logical roles:
    # upper-left+,upper-right-; lower-left-,lower-right+. Numbers are project
    # contact identities, not numbers printed on the manufacturer drawing.
    expected = {"1": (-41.0, -9.55), "2": (41.0, -9.55),
                "3": (41.0, 9.55), "4": (-41.0, 9.55)}
    pads = children(footprint, "pad")
    if len(pads) != 4 or {pad[1] for pad in pads} != set(expected):
        raise ValueError("four unique holder contacts required")
    for pad in pads:
        if tuple(map(float, field(pad, "at"))) != expected[pad[1]]:
            raise ValueError("primary checkerboard polarity mismatch")


class HolderPolaritySourceTests(unittest.TestCase):
    def setUp(self):
        self.legacy = generator.LEGACY.read_text()
        self.current = generator.OUTPUT.read_text()
        self.fp = parse(self.current)

    def test_reproducer_owns_exactly_one_current_r2_file(self):
        before = generator.LEGACY.read_bytes()
        expected_path = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/Keystone-1048P-POLARITY-CORRECTED.kicad_mod"
        self.assertEqual({expected_path: self.current}, generator.build())
        self.assertEqual(before, generator.LEGACY.read_bytes())
        self.assertNotEqual(generator.LEGACY.parent, expected_path.parent)

    def test_independent_primary_top_view_checkerboard(self):
        checkerboard(self.fp)
        pads = {pad[1]: pad for pad in children(self.fp, "pad")}
        upper = sorted((float(field(pad, "at")[0]), name) for name, pad in pads.items()
                       if float(field(pad, "at")[1]) < 0)
        lower = sorted((float(field(pad, "at")[0]), name) for name, pad in pads.items()
                       if float(field(pad, "at")[1]) > 0)
        self.assertEqual(["1", "2"], [name for _, name in upper])
        self.assertEqual(["4", "3"], [name for _, name in lower])

    def test_same_end_positive_regression_and_partial_correction_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "checkerboard"):
            checkerboard(parse(self.legacy))
        for number, x in (("3", "-41.000"), ("4", "41.000")):
            bad = copy.deepcopy(self.fp)
            pad = next(p for p in children(bad, "pad") if p[1] == number)
            children(pad, "at")[0][1] = x
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, "checkerboard"):
                checkerboard(bad)
        for operation in ("missing", "duplicate"):
            bad = copy.deepcopy(self.fp)
            pad = children(bad, "pad")[0]
            bad.remove(pad) if operation == "missing" else bad.append(copy.deepcopy(pad))
            with self.subTest(operation=operation), self.assertRaisesRegex(ValueError, "four unique"):
                checkerboard(bad)

    def test_only_allowed_electrical_delta_is_positions_three_and_four(self):
        old = parse(self.legacy)
        new = copy.deepcopy(self.fp)
        old_pads = {p[1]: p for p in children(old, "pad")}
        new_pads = {p[1]: p for p in children(new, "pad")}
        self.assertEqual({"3", "4"}, {n for n in old_pads if old_pads[n] != new_pads[n]})
        for number in ("3", "4"):
            children(new_pads[number], "at")[0][1:] = field(old_pads[number], "at")
        # Names/warnings and the explicit body-vs-reserve display correction
        # are metadata/graphics. All electrical geometry remains byte-exact
        # apart from the already reviewed 3/4 polarity repair.
        new[1] = old[1]
        children(new, "descr")[0][1:] = field(old, "descr")
        for item in children(new, "fp_rect"):
            new.remove(item)
        old_body = children(old, "fp_rect")[0]
        new.insert(old.index(old_body), copy.deepcopy(old_body))
        self.assertEqual(old, new)

    def test_historical_file_and_generator_are_not_silently_rewritten(self):
        self.assertEqual("dbcec95dcfe56d7d1e1bd2631640c065c30b064adc02f4f9810d4fc38ee02a9e",
                         hashlib.sha256(generator.LEGACY.read_bytes()).hexdigest())
        historical_generator = ROOT / "hardware/ecad/h2_rf_pack_safety_aon.py"
        self.assertEqual("df8e778483634123d51b0dc33db39726e5b2afc5de1c84abab0e637a25b49852",
                         hashlib.sha256(historical_generator.read_bytes()).hexdigest())
        self.assertNotEqual(generator.LEGACY, generator.OUTPUT)

    def test_changed_legacy_geometry_requires_a_new_review_not_auto_inheritance(self):
        for old, new in (("4.000 6.000", "7.340 6.350"), ("-43.000", "-38.530"),
                         ('(pad "3"', '(pad "5"')):
            with self.subTest(change=new), self.assertRaisesRegex(ValueError, "Legacy1048P geometry changed"):
                generator.corrected_text(self.legacy.replace(old, new))

    def test_current_contacts_keep_four_logical_roles_and_numbers(self):
        material = json.loads((ROOT / "hardware/ecad/generated/H2-R2-contact-materialization.json").read_text())
        group = next(g for g in material["groups"] if g["device_id"] == "keystone_1048p")
        self.assertEqual("Keystone Electronics 1048P", group["mpn"])
        self.assertEqual({"SLOT0_POS": ["1"], "SLOT0_NEG": ["2"], "SLOT1_POS": ["3"], "SLOT1_NEG": ["4"]},
                         {c["contact"]: c["pads"] for c in group["contacts"]})
        self.assertEqual(4, group["footprint_named_pad_count"])

    def test_current_binding_and_regenerator_are_r2_only(self):
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        self.assertEqual("Leshy2_R2:Keystone-1048P-POLARITY-CORRECTED",
                         contract["footprint_overrides"]["Keystone Electronics 1048P"])
        self.assertFalse(contract["authorization"]["fabrication"])
        tree = ast.parse((ROOT / "hardware/ecad/regenerate_h2.py").read_text())
        assignments = {target.id: ast.literal_eval(node.value)
                       for node in tree.body if isinstance(node, ast.Assign)
                       for target in node.targets if isinstance(target, ast.Name) and target.id == "R2_FOOTPRINT_GENERATORS"}
        self.assertEqual(1, assignments["R2_FOOTPRINT_GENERATORS"].count("hardware/ecad/h2_r2_holder_polarity.py"))

    def test_explicit_mechanical_and_manufacturing_limits_remain_open(self):
        self.assertFalse(generator.MECHANICS_QUALIFIED)
        self.assertFalse(generator.PRODUCTION_RELEASE_AUTHORIZED)
        for text in ("POLARITY ONLY", "MECHANICS NOT QUALIFIED", "absent locator holes", "not a manufacturing-ready land pattern"):
            self.assertIn(text, field(self.fp, "descr")[0])
        self.assertFalse(any(children(pad, "drill") for pad in children(self.fp, "pad")))
        self.assertEqual({(4.0, 6.0)}, {tuple(map(float, field(pad, "size"))) for pad in children(self.fp, "pad")})
        self.assertEqual("6135bff212f9eab9ed8158febcbbd0d18b9479caac384a7f51f2818d1328e26b", generator.SOURCE_SHA256)
        self.assertIn("Rev A", generator.SOURCE_SECTION)


@unittest.skipUnless(importlib.util.find_spec("pcbnew"), "Requires KiCad Python")
class HolderPolarityNativeTests(unittest.TestCase):
    def test_production_second_cell_and_local_fuse_follow_primary_polarity(self):
        import pcbnew
        board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb"))
        fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
        holder = fps["BT1"]
        identity = holder.GetFPID()
        self.assertEqual("Leshy2_R2", str(identity.GetLibNickname()))
        self.assertEqual("Keystone-1048P-POLARITY-CORRECTED", str(identity.GetLibItemName()))
        expected = {"1": ((30.45, 126), "PACK_SLOT0_POSITIVE_RAW"),
                    "2": ((30.45, 44), "BATTERY_STACK_NEGATIVE_CELL_SIDE"),
                    "3": ((49.55, 44), "PACK_SLOT1_POSITIVE_RAW"),
                    "4": ((49.55, 126), "PACK_2S_MIDPOINT")}
        pads = {pad.GetNumber(): pad for pad in holder.Pads()}
        self.assertEqual(set(expected), set(pads))
        point = lambda pad: (round(pcbnew.ToMM(pad.GetPosition().x), 5), round(pcbnew.ToMM(pad.GetPosition().y), 5))
        for number, (xy, net) in expected.items():
            self.assertEqual(xy, point(pads[number]))
            self.assertEqual("/RF_02_PACK_SAFETY_AON/" + net, pads[number].GetNetname())
            self.assertTrue(pads[number].IsOnLayer(pcbnew.F_Cu))
            self.assertFalse(pads[number].IsOnLayer(pcbnew.B_Cu))
        fuse = {pad.GetNumber(): pad for pad in fps["F2"].Pads()}
        self.assertEqual(pads["3"].GetNetname(), fuse["1"].GetNetname())
        self.assertEqual("/RF_02_PACK_SAFETY_AON/BATTERY_STACK_POSITIVE", fuse["2"].GetNetname())
        # Placement regression bound, not proof of routed current capacity or
        # path length. The former opposite-end fuse was more than 80 mm away.
        self.assertLessEqual(math.dist(point(pads["3"]), point(fuse["1"])), 4.5)
        self.assertTrue(fuse["1"].IsOnLayer(pcbnew.B_Cu))
        self.assertFalse(fuse["1"].IsOnLayer(pcbnew.F_Cu))

    def test_relocated_buffer_keeps_local_vcc_bypass(self):
        import pcbnew
        board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb"))
        fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
        for ref, xy in {"U91": (71.5, 28.4), "C241": (76.6, 30.1)}.items():
            fp = fps[ref]
            self.assertTrue(fp.IsFlipped())
            self.assertEqual(0, fp.GetOrientationDegrees())
            self.assertEqual(xy, (round(pcbnew.ToMM(fp.GetPosition().x), 5), round(pcbnew.ToMM(fp.GetPosition().y), 5)))
        fuse = fps["F2"]
        self.assertTrue(fuse.IsFlipped())
        self.assertEqual(270, fuse.GetOrientationDegrees() % 360)
        self.assertEqual((53.37, 47.87), (round(pcbnew.ToMM(fuse.GetPosition().x), 5), round(pcbnew.ToMM(fuse.GetPosition().y), 5)))
        supply = next(p for p in fps["U91"].Pads() if p.GetNumber() == "14")
        bypass = next(p for p in fps["C241"].Pads() if p.GetNumber() == "1")
        self.assertEqual("/RF_02_PACK_SAFETY_AON/3V3_MAIN", supply.GetNetname())
        self.assertEqual(supply.GetNetname(), bypass.GetNetname())
        ground = next(p for p in fps["C241"].Pads() if p.GetNumber() == "2")
        self.assertEqual("/RF_01_USB_PD_CHARGE/POWER_GROUND", ground.GetNetname())
        self.assertLessEqual(pcbnew.ToMM((supply.GetPosition() - bypass.GetPosition()).EuclideanNorm()), 2.0)

    def test_loaded_footprint_preserves_historical_offset_pose_and_checkerboard(self):
        import pcbnew
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(generator.OUTPUT.parent), generator.OUTPUT.stem)
        self.assertIsNotNone(fp)
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(42.99), pcbnew.FromMM(85)))
        fp.SetOrientationDegrees(90)
        expected = {"1": (33.44, 126), "2": (33.44, 44), "3": (52.54, 44), "4": (52.54, 126)}
        for pad in fp.Pads():
            self.assertEqual(expected[pad.GetNumber()],
                             (round(pcbnew.ToMM(pad.GetPosition().x), 5), round(pcbnew.ToMM(pad.GetPosition().y), 5)))
            self.assertTrue(pad.IsOnLayer(pcbnew.F_Cu))
            self.assertFalse(pad.IsOnLayer(pcbnew.B_Cu))
            self.assertEqual(0, pad.GetDrillSize().x)


if __name__ == "__main__":
    unittest.main()
