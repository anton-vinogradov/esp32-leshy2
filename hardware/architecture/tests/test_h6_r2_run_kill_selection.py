"""Independent exact SA selection/nominal land review; no fabrication claim.

C&K JS Series VL01/14/26 p1 ordering, p4 exact SA drawing, p5 retained SC.
The standard footprint uses a documented engineering land-width/corner margin.
No H1/H2 generated outputs or native PCB files are written or qualified here.
"""

import ast
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
LIBRARY = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
FOOTPRINT_ID = "Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN"
FOOTPRINT = LIBRARY / "Button_Switch_SMD.pretty/SW_SPDT_CK_JS102011SAQN.kicad_mod"
EVIDENCE = ROOT / "hardware/procurement/h6-js102011saqn-selection-review.json"


def sexpr(text):
    """Parse the public footprint syntax without needing a running KiCad UI."""
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))
    def item(token):
        if token == "(":
            result = []
            for child in tokens:
                if child == ")":
                    return result
                result.append(item(child))
            raise ValueError("unterminated footprint expression")
        if token == ")":
            raise ValueError("unexpected closing parenthesis")
        return ast.literal_eval(token) if token.startswith('"') else token
    result = item(next(tokens))
    if next(tokens, None) is not None:
        raise ValueError("extra footprint expression")
    return result


def children(node, key):
    return [value for value in node if isinstance(value, list) and value[0] == key]


def field(node, key):
    matches = children(node, key)
    if len(matches) != 1:
        raise ValueError(f"expected one {key}")
    return matches[0][1:]


def xy(node, key):
    return tuple(map(float, field(node, key)))


def validate_nominal_geometry(fp):
    """Exact independent physical fixture, not inferred from the selected file."""
    if fp[:2] != ["footprint", "SW_SPDT_CK_JS102011SAQN"]:
        raise ValueError("wrong exact SA footprint")
    pads = children(fp, "pad")
    if len(pads) != 5:
        raise ValueError("SA needs exactly three conductors and two locator holes")
    electrical = [p for p in pads if p[1]]
    if Counter(p[1] for p in electrical) != Counter(["1", "2", "3"]):
        raise ValueError("SA physical contact numbers changed")
    for p in electrical:
        expected_x = {"1": -2.5, "2": 0.0, "3": 2.5}[p[1]]
        if p[2:4] != ["smd", "roundrect"]:
            raise ValueError("SA must have SMT roundrect lands")
        if xy(p, "at") != (expected_x, -(4.0 - 2.5 / 2)):
            raise ValueError("SA registered manufacturer land centre changed")
        if xy(p, "size") != (1.25, 2.5) or field(p, "roundrect_rratio") != ["0.2"]:
            raise ValueError("reviewed engineering land size/corners changed")
        if set(field(p, "layers")) != {"F.Cu", "F.Paste", "F.Mask"}:
            raise ValueError("SA assembly land layers changed")
        if children(p, "drill"):
            raise ValueError("electrical land is not a drilled contact")
    holes = [p for p in pads if not p[1]]
    if Counter(xy(p, "at") for p in holes) != Counter([(-3.4, 0.0), (3.4, 0.0)]):
        raise ValueError("SA locator registration changed")
    for p in holes:
        if p[2:4] != ["np_thru_hole", "circle"]:
            raise ValueError("SA locators must be non-plated, non-electrical holes")
        if xy(p, "size") != (.9, .9) or field(p, "drill") != ["0.9"]:
            raise ValueError("SA manufacturer hole diameter changed")
        if set(field(p, "layers")) != {"*.Cu", "*.Mask"}:
            raise ValueError("SA locator layers changed")
    fab = {(xy(line, "start"), xy(line, "end")) for line in children(fp, "fp_line")
           if field(line, "layer") == ["F.Fab"]}
    body_edges = {((-4.5, -1.8), (-4.5, 1.8)),
                  ((-4.5, -1.8), (4.5, -1.8)),
                  ((4.5, -1.8), (4.5, 1.8)),
                  ((4.5, 1.8), (-4.5, 1.8))}
    actuator = {((-2.0, 3.8), (-2.0, 1.8)),
                ((-.5, 1.8), (-.5, 3.8)),
                ((-.5, 3.8), (-2.0, 3.8))}
    if not (body_edges | actuator).issubset(fab):
        raise ValueError("SA body or side-actuator datum changed")


class RunKillSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.devices = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]
        cls.cost = json.loads((ROOT / "hardware/product-design/h1-r2-cost-review.json").read_text())
        cls.binding = json.loads((ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json").read_text())
        cls.evidence = json.loads(EVIDENCE.read_text())

    def test_retained_sc_is_top_actuated_and_has_total_height(self):
        old = self.devices["ck_js102011scqn"]
        self.assertEqual("C&K JS102011SCQN", old["mpn"])
        self.assertIn("vertical", old["kind"])
        self.assertIn("top_actuator", old["kind"])
        self.assertNotIn("right_angle", old["kind"])
        self.assertEqual([8.5, 3.5, 5.5], old["dimensions_mm"])
        self.assertIn("3.5-mm body", old["mechanical_height_basis"])
        self.assertEqual("2026-09-07", old["source"]["checked"])

    def test_exact_contacts_and_electrical_contract_preserve_sc_semantics(self):
        old, new = (self.devices[key] for key in ("ck_js102011scqn", "ck_js102011saqn"))
        expected = {"THROW_A": {"physical": "1", "role": "switch_contact"},
                    "COMMON": {"physical": "2 / C", "role": "switch_common"},
                    "THROW_B": {"physical": "3", "role": "switch_contact"}}
        self.assertEqual(expected, old["contacts"])
        self.assertEqual(expected, new["contacts"])
        self.assertEqual(old["electrical_contract"], new["electrical_contract"])
        self.assertEqual([9.0, 3.6, 3.5], new["dimensions_mm"])
        self.assertFalse(new["programmable"])

    def test_r2_replacement_does_not_mutate_the_old_identity(self):
        replacement = self.cost["r2_device_replacements"]["ck_js102011scqn"]
        self.assertEqual("ck_js102011saqn", replacement["device_id"])
        self.assertEqual(self.devices["ck_js102011saqn"]["mpn"], replacement["mpn"])
        self.assertEqual(FOOTPRINT_ID, self.binding["footprint_overrides"][replacement["mpn"]])
        self.assertEqual(["RF_50_TX_SAFETY_EVIDENCE"],
                         self.binding["sheet_affinity_overrides"][replacement["device_id"]])

    def test_price_bases_remain_separate(self):
        new = self.devices["ck_js102011saqn"]
        replacement = self.cost["r2_device_replacements"]["ck_js102011scqn"]
        self.assertEqual(100, new["cost"]["target_quantity"])
        self.assertEqual(.5426, new["cost"]["unit_price_usd"])
        self.assertEqual(.5426, replacement["unit_price_usd"])
        self.assertEqual(.8593, replacement["quantity_one_unit_price_usd"])
        comparison = replacement["cost_comparison"]
        for basis in ("same_day_jlcpcb_quantity_one", "same_day_jlcpcb_quantity_100"):
            row = comparison[basis]
            self.assertEqual(Decimal(str(row["former_sc"])) - Decimal(str(row["selected_sa"])),
                             Decimal(str(row["component_saving_per_device"])))
        historical = comparison["historical_quantity_100_planning"]
        self.assertEqual(Decimal("0.2397"), Decimal(str(historical["former_sc_digikey_2026_08_19"]))
                         - Decimal(str(historical["selected_sa_jlcpcb_2026_09_07"])))

    def test_live_exact_factory_route_matches_source_evidence(self):
        route = self.devices["ck_js102011saqn"]["factory_route"]
        evidence = self.evidence["jlcpcb_evidence"]
        server = evidence["server_purchase_fields"]
        self.assertEqual("C221660", route["jlcpcb_part"])
        self.assertEqual("C&K", route["manufacturer"])
        self.assertEqual("SMT Assembly", route["assembly_type"])
        self.assertEqual("Economic and Standard", route["pcba_type"])
        self.assertEqual("2026-09-07T20:32:07Z", route["checked_at_utc"])
        self.assertEqual(route["checked_at_utc"], self.evidence["checked_at_utc"])
        self.assertEqual(route["stock"], server["overseasStockCount"])
        self.assertEqual(route["available_order_quantity"], server["canPresaleNumber"])
        self.assertEqual(1, route["moq"])
        self.assertGreater(route["available_order_quantity"], route["moq"])
        self.assertEqual(13, route["preorder_minimum_beyond_available_stock"])
        self.assertEqual(route["price_tiers_usd"], evidence["price_tiers"])
        self.assertEqual("1", server["isBuyComponent"])
        self.assertTrue(server["allowPostFlag"])
        self.assertIsNone(server["noBuyReason"])

    def test_source_selection_cannot_claim_native_or_fabrication_approval(self):
        self.assertEqual("selected_source_only_native_integration_open", self.evidence["status"])
        for key in ("fabrication_ready", "ordering_authorized"):
            self.assertFalse(self.evidence[key])
        geometry = self.evidence["standard_footprint_review"]
        for key in ("drop_in_for_sc", "native_placement_verified", "assembled_step_verified", "fabrication_ready"):
            self.assertFalse(geometry[key])
        self.assertIn("native_integration_open", self.devices["ck_js102011saqn"]["qualification"])
        self.assertFalse(self.evidence["factory_placeable_alternative_reviewed"]["selected"])

    def footprint(self):
        self.assertTrue(FOOTPRINT.is_file(), "reviewed standard KiCad library is required")
        return sexpr(FOOTPRINT.read_text())

    def test_standard_sa_all_five_features_match_independent_nominal_fixture(self):
        validate_nominal_geometry(self.footprint())

    def test_widened_lands_are_an_explicit_engineering_difference(self):
        review = self.evidence["standard_footprint_review"]
        self.assertEqual([1.25, 2.5], review["standard_land_size_mm"])
        for row in review["manufacturer_land_rows_mm"]:
            self.assertEqual([1.2, 2.5], row["size"])
        self.assertEqual(Decimal("0.025"), (Decimal("1.25") - Decimal("1.20")) / 2)
        self.assertEqual(.25, review["standard_roundrect_radius_mm"])
        self.assertIn("not identical manufacturer artwork", review["engineering_land_difference"])

    def test_wrong_hole_position_or_diameter_is_rejected(self):
        original = self.footprint()
        for key, values in (("at", ["3.3", "0"]), ("drill", ["1.0"])):
            fp = deepcopy(original)
            hole = next(p for p in children(fp, "pad") if not p[1])
            children(hole, key)[0][1:] = values
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_nominal_geometry(fp)

    def test_reversed_contacts_or_missing_locator_are_rejected(self):
        fp = self.footprint()
        first = next(p for p in children(fp, "pad") if p[1] == "1")
        third = next(p for p in children(fp, "pad") if p[1] == "3")
        first[1], third[1] = "3", "1"
        with self.assertRaises(ValueError):
            validate_nominal_geometry(fp)
        fp = self.footprint()
        fp.remove(next(p for p in children(fp, "pad") if not p[1]))
        with self.assertRaises(ValueError):
            validate_nominal_geometry(fp)

    def test_wrong_land_y_or_electrical_locator_is_rejected(self):
        fp = self.footprint()
        pad = next(p for p in children(fp, "pad") if p[1] == "2")
        children(pad, "at")[0][1:] = ["0", "2.75"]
        with self.assertRaises(ValueError):
            validate_nominal_geometry(fp)
        fp = self.footprint()
        hole = next(p for p in children(fp, "pad") if not p[1])
        hole[1], hole[2] = "MP", "thru_hole"
        with self.assertRaises(ValueError):
            validate_nominal_geometry(fp)


if __name__ == "__main__":
    unittest.main()
