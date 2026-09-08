"""Independent manufacturer geometry and current-R2-only TRRS regressions.

Same Sky SJ-4351X-SMT 2024-09-12 p2 PCB TOP VIEW and TS circuit.
These source tests do not certify native placement, audio performance or release.
"""

import copy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/ecad"))
import h2_r2_audio_footprint as footprint
from h2_r2_contact_materialization import automatic_pads, parse_pads
from h2_r2_native_inventory import r2_cost_base_rows
from h2_r2_net_ledger import route_indexes, routed_current_net

try:
    import pcbnew
except ImportError:
    pcbnew = None

DEVICE = "same_sky_sj_43515ts_smt_tr"
OLD_DEVICE = "same_sky_sj_43504_smt_tr"


def read_json(relative):
    return json.loads((ROOT / relative).read_text())


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


class SJ43515TSSourceTests(unittest.TestCase):
    def assert_exact_geometry(self, node):
        pads = children(node, "pad")
        named = [p for p in pads if p[1]]
        self.assertEqual(7, len(pads))
        self.assertEqual(5, len(named))
        self.assertEqual({"1", "2", "3", "4", "5"}, {p[1] for p in named})
        expected = {
            "1": ((.6, 3.5), (2, 3)), "2": ((13, 3.5), (2, 3)),
            "3": ((5.3, -3.5), (2, 3)), "4": ((3.5, 3.5), (2, 3)),
            "5": ((17, -.8), (3, 2)),
        }
        for p in named:
            self.assertEqual(["smd", "rect"], p[2:4])
            xy, size = expected[p[1]]
            self.assertEqual(xy, tuple(map(float, field(p, "at"))))
            self.assertEqual(size, tuple(map(float, field(p, "size"))))
            self.assertEqual(["F.Cu", "F.Paste", "F.Mask"], field(p, "layers"))
            self.assertFalse(children(p, "drill"))
        holes = [p for p in pads if not p[1]]
        self.assertEqual({(4.5, 0), (11.5, 0)},
                         {tuple(map(float, field(p, "at"))) for p in holes})
        for p in holes:
            self.assertEqual(["np_thru_hole", "circle"], p[2:4])
            self.assertEqual([1.9], list(map(float, field(p, "drill"))))
            self.assertEqual([1.9, 1.9], list(map(float, field(p, "size"))))
        graphics = children(node, "fp_rect") + children(node, "fp_line")
        self.assertTrue(all(field(g, "layer") != ["Edge.Cuts"] for g in graphics))
        court = [g for g in children(node, "fp_rect") if field(g, "layer") == ["F.CrtYd"]]
        self.assertEqual(1, len(court))
        self.assertEqual((-1.75, -5.25), tuple(map(float, field(court[0], "start"))))
        self.assertEqual((18.75, 5.25), tuple(map(float, field(court[0], "end"))))
        fab = [g for g in children(node, "fp_rect") if field(g, "layer") == ["F.Fab"]]
        self.assertEqual({((0, -3), (15.5, 3.8)), ((-1.5, -2.5), (0, 2.5))},
                         {(tuple(map(float, field(g, "start"))),
                           tuple(map(float, field(g, "end")))) for g in fab})

    def test_exact_manufacturer_lands_and_non_electrical_locators(self):
        self.assert_exact_geometry(parse(footprint.OUTPUT.read_text()))

    def test_reproducible_single_r2_library_file(self):
        self.assertEqual(footprint.build(), footprint.OUTPUT.read_text())
        self.assertEqual("SJ-43515TS-SMT-TR", parse(footprint.build())[1])
        self.assertEqual("Leshy2_R2.pretty", footprint.OUTPUT.parent.name)

    def test_geometry_regressions_are_detected(self):
        original = parse(footprint.build())
        for mutation in ("number", "duplicate", "pad6", "pitch", "size", "mirror", "plated", "hole", "cutout"):
            with self.subTest(mutation=mutation):
                node = copy.deepcopy(original)
                pads = children(node, "pad")
                if mutation == "number":
                    pads[0][1], pads[1][1] = pads[1][1], pads[0][1]
                elif mutation == "duplicate":
                    node.append(copy.deepcopy(pads[0]))
                elif mutation == "pad6":
                    pads[4][1] = "6"
                elif mutation == "pitch":
                    children(pads[0], "at")[0][1] = "0"
                elif mutation == "size":
                    children(pads[4], "size")[0][1:] = ["2", "3"]
                elif mutation == "mirror":
                    children(pads[2], "at")[0][2] = "3.5"
                elif mutation == "plated":
                    pads[-1][2] = "thru_hole"
                elif mutation == "hole":
                    children(pads[-1], "drill")[0][1] = "1.5"
                elif mutation == "cutout":
                    children(children(node, "fp_line")[0], "layer")[0][1] = "Edge.Cuts"
                with self.assertRaises(AssertionError):
                    self.assert_exact_geometry(node)

    def assert_contact_contract(self, device):
        self.assertEqual("Same Sky SJ-43515TS-SMT-TR", device["mpn"])
        self.assertEqual({"SLEEVE": "1", "TIP": "2", "RING1": "3", "RING2": "4", "TIP_SWITCH": "5"},
                         {name: row["physical"] for name, row in device["contacts"].items()})
        electrical = device["electrical_contract"]
        self.assertEqual("CTIA/AHJ", electrical["product_wiring_standard"])
        for field_name in ("tip_switch_closed_without_plug_physical_pads", "tip_switch_open_with_plug_physical_pads"):
            self.assertEqual(["2", "5"], electrical[field_name])

    def test_current_five_contact_contract_and_historical_six_contact_device(self):
        devices = read_json("hardware/architecture/devices.json")["devices"]
        self.assert_contact_contract(devices[DEVICE])
        self.assertEqual("Same Sky SJ-43504-SMT-TR", devices[OLD_DEVICE]["mpn"])
        self.assertEqual("6", devices[OLD_DEVICE]["contacts"]["RING1_SWITCH"]["physical"])

    def test_reviewed_interface_types_are_exact_five_passive_contacts(self):
        mappings = read_json("hardware/verification/h6-electrical-pins-interfaces.json")["devices"]
        rows = [row for row in mappings if row["device_id"] == DEVICE]
        self.assertEqual(1, len(rows))
        row = rows[0]
        device = read_json("hardware/architecture/devices.json")["devices"][DEVICE]
        self.assertEqual(device["mpn"], row["mpn"])
        self.assertEqual({"1", "2", "3", "4", "5"}, set(row["pins"]))
        self.assertEqual({"passive"}, {pin["type"] for pin in row["pins"].values()})
        self.assertTrue(all(pin["reason"] for pin in row["pins"].values()))
        self.assertEqual([], row["unresolved"])
        self.assertEqual(footprint.SOURCE_URL, row["evidence"][0]["url"])
        self.assertIn("p2", row["evidence"][0]["section"])
        self.assertEqual("2026-09-08", row["evidence"][0]["checked"])
        historical = [row for row in mappings if row["device_id"] == OLD_DEVICE]
        # The retired part remains in the historical device register, not the
        # current typed-ERC map (which rejects unknown current-R2 device IDs).
        self.assertEqual([], historical)
        old_device = read_json("hardware/architecture/devices.json")["devices"][OLD_DEVICE]
        self.assertEqual("6", old_device["contacts"]["RING1_SWITCH"]["physical"])

    def test_current_interface_reviews_all_bind_to_current_materialized_devices(self):
        from hardware.verification.h6_r2_electrical_semantics import reviewed_maps
        fragment = read_json("hardware/verification/h6-electrical-pins-interfaces.json")
        groups = read_json("hardware/ecad/generated/H2-R2-contact-materialization.json")["groups"]
        reviews = reviewed_maps([fragment], groups)
        self.assertIn(DEVICE, reviews)
        self.assertNotIn(OLD_DEVICE, reviews)

    def test_wrong_switch_pole_and_phantom_contact_are_rejected(self):
        original = read_json("hardware/architecture/devices.json")["devices"][DEVICE]
        for mutation in ("pole", "contact6", "swap_tip_sleeve"):
            with self.subTest(mutation=mutation):
                device = copy.deepcopy(original)
                if mutation == "pole":
                    device["electrical_contract"]["tip_switch_closed_without_plug_physical_pads"] = ["1", "5"]
                elif mutation == "contact6":
                    device["contacts"]["RING1_SWITCH"] = {"physical": "6", "role": "no_connect"}
                else:
                    device["contacts"]["SLEEVE"]["physical"] = "2"
                    device["contacts"]["TIP"]["physical"] = "1"
                with self.assertRaises(AssertionError):
                    self.assert_contact_contract(device)

    def test_materializer_sees_five_real_pads_and_no_contact_exception(self):
        device = read_json("hardware/architecture/devices.json")["devices"][DEVICE]
        pads, ignored = parse_pads(footprint.OUTPUT)
        self.assertEqual(2, ignored)
        self.assertEqual({"1", "2", "3", "4", "5"}, set(pads))
        claimed = []
        for name, row in device["contacts"].items():
            resolved, method = automatic_pads(name, row["physical"], set(pads))
            self.assertEqual([row["physical"]], resolved)
            self.assertEqual("exact_physical_pad_name", method)
            claimed.extend(resolved)
        self.assertEqual(sorted(pads), sorted(claimed))

    def test_current_replacement_and_sheet_are_explicit_not_historical_rewrite(self):
        cost = read_json("hardware/product-design/h1-r2-cost-review.json")
        old = [{"device_id": OLD_DEVICE, "mpn": "Same Sky SJ-43504-SMT-TR", "quantity": "1", "scope": "base_product", "placements": "headphone_jack"}]
        # This miniature population contains only audio. Passing the complete
        # replacement registry would correctly invoke USB's missing-port guard.
        projected = r2_cost_base_rows(old, {
            "r2_device_replacements": {OLD_DEVICE: cost["r2_device_replacements"][OLD_DEVICE]},
        })
        self.assertEqual(1, len(projected))
        self.assertEqual(DEVICE, projected[0]["device_id"])
        self.assertEqual(1, projected[0]["quantity_per_device"])
        self.assertEqual(OLD_DEVICE, projected[0]["historical_capture_route"])
        contract = read_json("hardware/ecad/h2-r2-symbol-footprint-contract.json")
        self.assertEqual("Leshy2_R2:SJ-43515TS-SMT-TR", contract["footprint_overrides"]["Same Sky SJ-43515TS-SMT-TR"])
        self.assertEqual(["RF_22_AUDIO_CODEC_IO"], contract["sheet_affinity_overrides"][DEVICE])

    def test_five_preserved_endpoint_nets_still_have_current_route_authority(self):
        contract = read_json("hardware/ecad/h2-r2-net-ledger-contract.json")
        routes = read_json(contract["reconciled_historical_hints"]["route_contract"])
        index, _, aliases = route_indexes(routes, contract["canonical_net_aliases"])
        for contact, expected in {"SLEEVE": "HEADSET_MIC_RAW", "TIP": "HEADPHONE_LEFT_TIP", "RING1": "HEADPHONE_RIGHT_RING1", "TIP_SWITCH": "HEADSET_SWITCH_STATE"}.items():
            net, origin = routed_current_net("headphone_jack." + contact, index, contract["canonical_net_aliases"], aliases)
            self.assertEqual(expected, net)
            self.assertIsNotNone(origin)
        topology = read_json(contract["authority"]["topology"])
        self.assertEqual("AUDIO_GROUND", topology["endpoint_overrides"]["headphone_jack.RING2"])

    def test_procurement_route_is_explicit_preorder_not_claimed_stock(self):
        device = read_json("hardware/architecture/devices.json")["devices"][DEVICE]
        route = device["factory_route"]
        self.assertEqual("C5353507", route["jlcpcb_part"])
        self.assertEqual("SMT Assembly", route["assembly_type"])
        self.assertIn("Standard", route["pcba_type"])
        self.assertEqual(4, route["minimum_preorder_quantity"])
        self.assertGreater(route["available_preorder_quantity"], 0)
        self.assertEqual(9.5124, round(route["minimum_preorder_quantity"] * route["unit_price_usd_at_moq"], 4))
        self.assertFalse(route["order_or_allocation_made"])
        review = read_json(route["evidence"])
        self.assertFalse(review["fabrication_authorized"])
        self.assertFalse(review["jlcpcb_evidence"]["immediate_assembly_stock_confirmed"])

    def test_audio4_pose_contract_keeps_anchor_distinct_from_courtyard(self):
        proposal = read_json("hardware/layout/h6-r2-audio-placement-proposal.json")
        rows = proposal["placement_overrides"]
        self.assertEqual({"headphone_jack", "voice_io_power_input_cap", "audio_capture_selector_bypass", "evidence_or_4"}, set(rows))
        jack = rows["headphone_jack"]
        self.assertEqual("rear-outer", jack["frame"])
        self.assertEqual([.8, 99], jack["anchor_mm"])
        self.assertNotIn("centre_mm", jack)
        self.assertEqual(0, jack["rotation_deg"])
        crosscheck = next(r for r in proposal["native_pose_crosscheck"] if r["reference"] == "U83")
        self.assertEqual([9.3, 99], crosscheck["courtyard_centre_mm"])

    @unittest.skipIf(pcbnew is None, "Run with KiCad Python for native footprint parser/transform")
    def test_native_f0_pad_mask_drill_and_left_mouth_datum(self):
        board = pcbnew.BOARD()
        fp = pcbnew.FootprintLoad(str(footprint.OUTPUT.parent), footprint.OUTPUT.stem)
        self.assertIsNotNone(fp)
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(.8), pcbnew.FromMM(99)))
        fp.SetOrientationDegrees(0)
        self.assertEqual(pcbnew.F_Cu, fp.GetLayer())
        named = {p.GetNumber(): p for p in fp.Pads() if p.GetNumber()}
        self.assertEqual({"1", "2", "3", "4", "5"}, set(named))
        left_copper = min(pcbnew.ToMM(p.GetBoundingBox().GetLeft()) for p in named.values())
        self.assertAlmostEqual(.4, left_copper, places=5)
        holes = [p for p in fp.Pads() if not p.GetNumber()]
        self.assertEqual(2, len(holes))
        for p in holes:
            self.assertEqual(pcbnew.PAD_ATTRIB_NPTH, p.GetAttribute())
        centre = fp.GetCourtyard(fp.GetLayer()).BBox().GetCenter()
        self.assertAlmostEqual(9.3, pcbnew.ToMM(centre.x), places=5)
        self.assertAlmostEqual(99, pcbnew.ToMM(centre.y), places=5)
        # The native F.Fab nose rectangle is left of the body. Drawing edges
        # include stroke width, so endpoints (not the stroked bbox) set datum.
        fab_rects = [g for g in fp.GraphicalItems() if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() == pcbnew.F_Fab and g.GetShape() == pcbnew.SHAPE_T_RECT]
        left = min(min(pcbnew.ToMM(g.GetStart().x), pcbnew.ToMM(g.GetEnd().x)) for g in fab_rects)
        self.assertAlmostEqual(-.7, left, places=5)


if __name__ == "__main__":
    unittest.main()
