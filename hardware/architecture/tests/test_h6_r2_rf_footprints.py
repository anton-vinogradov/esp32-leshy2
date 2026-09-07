"""Primary-drawing RF land regressions, independent of generated native boards.

Checked 2026-09-07. These tests validate lands and top-view orientation, not RF
performance, stackup, stencil approval or undocumented internal DC continuity.
The literal expectations below are transcribed from manufacturer drawings:

* TTM B0310J50100AHF Rev.F pp1/4 (top/bottom views and mounting footprint):
  https://cdn.ttm.com/repository/products/wireless-xinger/balun-transformers/B0310J50100AHF/B0310J50100AHF.pdf
* TTM DC2337J5010AHF Rev.H p2 (numbering/Configuration 1), and the current
  manufacturer's linked DCxxJ5010_15_20x_Mounting_Footprint_240910 DXF,
  PCB_Land_Pattern layer (not Component_Pads or PCB_Solder_Stencil):
  https://cdn.ttm.com/repository/products/wireless-xinger/footprints/DCxxJ5010_15_20x.dxf
* KYOCERA AVX TDS-RFM-0055 Rev2 p6/printed69 (CP0603, not CP0302):
  https://datasheets.kyocera-avx.com/cp0302.pdf
* Coilcraft Document424-1/2, revised06/14/22, schematic B/land pattern:
  https://www.coilcraft.com/getmedia/f685d903-2563-4c96-8ba6-f82a58883aeb/wbc.pdf
"""

import copy
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
LIBRARY = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty"
OVERRIDES = {
    "TTM Technologies B0310J50100AHF": "B0310J50100AHF",
    "TTM Technologies DC2337J5010AHF": "DC2337J5010AHF",
    "KYOCERA AVX CP0603Q5425ENTR": "CP0603Q5425ENTR",
    "WBC1-1TLC": "WBC1-1TLC",
    "WBC16-1TLC": "WBC16-1TLC",
}

# Library footprints are top views. The TTM BOTTOM VIEW cannot be copied into
# F.Cu even when the final instance will be mounted on B.Cu; KiCad flips it.
TTM_BALUN = {
    "1": (.660, -.495), "2": (0, -.495), "3": (-.660, -.495),
    "4": (-.660, .495), "5": (0, .495), "6": (.660, .495),
}
TTM_COUPLER = {
    "1": (.6604, -.4953), "2": (0, -.4953), "3": (-.6604, -.4953),
    "4": (-.6604, .4953), "5": (0, .4953), "6": (.6604, .4953),
}
# CP's portrait terminal diagram is rotated CW into the landscape land drawing.
# Manufacturer numbers: IN=1, OUT=2, CPL=3, TERM(50 OHM)=4.
CP_COUPLER = {
    "IN": (-.625, -.350), "OUT": (.625, -.350),
    "CPL": (-.625, .350), "TERM": (.625, .350),
}
# WBC portrait land drawing rotated CCW, preserving chirality. The 3.05-mm
# dimension is center-to-center, not the gap between 1.14-mm-long lands.
WBC_TRANSFORMER = {
    "1": (-1.525, 1.520), "2": (-1.525, 0), "3": (-1.525, -1.520),
    "4": (1.525, -1.520), "5": (1.525, 0), "6": (1.525, 1.520),
}


def parse(source):
    """Small independent S-expression reader; keep duplicate pad nodes visible."""
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
    values = children(node, kind)
    if len(values) != 1:
        raise ValueError(f"expected one {kind}")
    return values[0][1:]


def load(name):
    return parse((LIBRARY / f"{name}.kicad_mod").read_text())


class RFLandPatternTests(unittest.TestCase):
    def assert_lands(self, node, expected, size):
        pads = children(node, "pad")
        self.assertEqual(len(expected), len(pads), "duplicate/extra physical pad")
        self.assertEqual(set(expected), {p[1] for p in pads})
        self.assertEqual(["F.Cu"], field(node, "layer"))
        for pad in pads:
            self.assertEqual(["smd", "rect"], pad[2:4])
            at = list(map(float, field(pad, "at")))
            self.assertEqual(2, len(at), "do not silently rotate anisotropic pad")
            for actual, wanted in zip(at, expected[pad[1]]):
                self.assertAlmostEqual(wanted, actual, places=6, msg=pad[1])
            self.assertEqual(list(size), list(map(float, field(pad, "size"))))
            self.assertEqual(["F.Cu", "F.Paste", "F.Mask"], field(pad, "layers"))

    def test_exact_mpn_overrides_select_reviewed_not_legacy_footprints(self):
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        for mpn, name in OVERRIDES.items():
            with self.subTest(mpn=mpn):
                self.assertEqual(f"Leshy2_R2:{name}", contract["footprint_overrides"][mpn])
                self.assertEqual(["footprint", name], load(name)[:2])

    def test_ttm_balun_uses_recommended_lands_not_body_termination_dimensions(self):
        self.assert_lands(load("B0310J50100AHF"), TTM_BALUN, (.410, .330))

    def test_ttm_coupler_uses_current_dxf_copper_not_stencil_layer(self):
        self.assert_lands(load("DC2337J5010AHF"), TTM_COUPLER, (.4064, .3302))

    def test_cp_ports_follow_long_axis_and_manufacturer_number_mapping(self):
        node = load("CP0603Q5425ENTR")
        self.assert_lands(node, CP_COUPLER, (.500, .400))
        description = field(node, "descr")[0]
        self.assertIn("IN=manufacturer1, OUT=2, CPL=3, TERM=4", description)

    def test_wbc_both_exact_parts_follow_counterclockwise_rotated_land_drawing(self):
        for name in ("WBC1-1TLC", "WBC16-1TLC"):
            with self.subTest(name=name):
                self.assert_lands(load(name), WBC_TRANSFORMER, (1.140, .760))

    def test_wbc_schematic_b_has_no_primary_center_tap_on_pad5(self):
        devices = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]
        topology = json.loads((ROOT / "hardware/ecad/h2-r2-topology-overrides.json").read_text())
        for device_id in ("coilcraft_wbc1_1tlc", "coilcraft_wbc16_1tlc"):
            with self.subTest(device_id=device_id):
                device = devices[device_id]
                self.assertEqual({"physical": "5", "role": "nc"}, device["contacts"]["NC_5"])
                self.assertNotIn("PRI_CT", device["contacts"])
                self.assertEqual("Coilcraft Document 424-1, schematic B", device["electrical_contract"]["manufacturer_schematic"])
                self.assertEqual(["4", "6"], device["electrical_contract"]["primary_winding_pins"])
                self.assertEqual(["1", "2", "3"], device["electrical_contract"]["secondary_winding_pins"])
                self.assertEqual("5", device["electrical_contract"]["unconnected_pin"])
        # Check the source topology, not a stale generated netlist.
        mappings = [value for value in topology.values() if isinstance(value, dict)]
        for instance in ("air_mixer_input_transformer", "air_mixer_output_transformer"):
            owners = [value for value in mappings if f"{instance}.NC_5" in value]
            self.assertEqual(1, len(owners))
            self.assertIsNone(owners[0][f"{instance}.NC_5"])
            self.assertNotIn(f"{instance}.PRI_CT", owners[0])

    def test_orientation_markers_are_on_documented_side_not_mirrored(self):
        for name in OVERRIDES.values():
            with self.subTest(name=name):
                node = load(name)
                marks = [m for m in children(node, "fp_circle") if field(m, "layer") == ["F.Fab"]]
                self.assertEqual(1, len(marks))
                x, y = map(float, field(marks[0], "center"))
                if name.startswith("WBC"):
                    self.assertLess(x, 0)
                    self.assertGreater(y, 0)  # pin1 bottom-left after CCW rotation
                    silk = [m for m in children(node, "fp_circle") if field(m, "layer") == ["F.SilkS"]]
                    self.assertEqual(1, len(silk), "WBC assembly pin1 marker required")
                    sx, sy = map(float, field(silk[0], "center"))
                    self.assertLess(sx, 0)
                    self.assertGreater(sy, 0)
                elif name.startswith("CP"):
                    self.assertLess(x, 0)
                    self.assertLess(y, 0)  # manufacturer's white IN corner
                else:
                    self.assertGreater(x, 0)  # top-view dot near pins1/6
                    self.assertAlmostEqual(0, y)

    def test_no_invented_transmission_lines_vias_or_internal_dc_links(self):
        for name in OVERRIDES.values():
            with self.subTest(name=name):
                node = load(name)
                self.assertEqual(["smd"], field(node, "attr"))
                for part in node[1:]:
                    if isinstance(part, list) and part[0].startswith("fp_"):
                        self.assertNotIn("Cu", field(part, "layer")[0])
                self.assertFalse(children(node, "zone"))
                self.assertFalse(children(node, "net_tie_pad_groups"))
                self.assertFalse(children(node, "segment"))

    def test_courtyards_enclose_copper_and_body(self):
        for name in OVERRIDES.values():
            with self.subTest(name=name):
                node = load(name)
                court = [r for r in children(node, "fp_rect") if field(r, "layer") == ["F.CrtYd"]]
                self.assertEqual(1, len(court))
                lo = list(map(float, field(court[0], "start")))
                hi = list(map(float, field(court[0], "end")))
                for pad in children(node, "pad"):
                    for axis, (at, extent) in enumerate(zip(map(float, field(pad, "at")), map(float, field(pad, "size")))):
                        self.assertLess(lo[axis], at - extent / 2)
                        self.assertGreater(hi[axis], at + extent / 2)
                for body in children(node, "fp_rect"):
                    if field(body, "layer") == ["F.Fab"]:
                        for axis, value in enumerate(map(float, field(body, "start"))):
                            self.assertLess(lo[axis], value)
                        for axis, value in enumerate(map(float, field(body, "end"))):
                            self.assertGreater(hi[axis], value)

    def test_guard_rejects_ttm_bottom_view_mirror_even_if_pad_set_and_size_match(self):
        node = load("B0310J50100AHF")
        for pad in children(node, "pad"):
            at = children(pad, "at")[0]
            at[1] = str(-float(at[1]))
        with self.assertRaises(AssertionError):
            self.assert_lands(node, TTM_BALUN, (.410, .330))

    def test_guard_rejects_cp_short_axis_through_ports(self):
        node = load("CP0603Q5425ENTR")
        pads = {pad[1]: pad for pad in children(node, "pad")}
        pads["OUT"][1], pads["CPL"][1] = "CPL", "OUT"
        with self.assertRaises(AssertionError):
            self.assert_lands(node, CP_COUPLER, (.500, .400))

    def test_guard_rejects_wbc_gap_as_center_pitch(self):
        node = load("WBC1-1TLC")
        for pad in children(node, "pad"):
            at = children(pad, "at")[0]
            at[1] = str(2.285 if float(at[1]) > 0 else -2.285)
        with self.assertRaises(AssertionError):
            self.assert_lands(node, WBC_TRANSFORMER, (1.140, .760))

    def test_guard_rejects_duplicate_physical_pad_hidden_by_dictionary(self):
        node = load("WBC16-1TLC")
        node.append(copy.deepcopy(children(node, "pad")[0]))
        with self.assertRaises(AssertionError):
            self.assert_lands(node, WBC_TRANSFORMER, (1.140, .760))


if __name__ == "__main__":
    unittest.main()
