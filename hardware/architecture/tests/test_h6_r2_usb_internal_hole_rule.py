"""The GCT locator exception is finite; unrelated geometry keeps normal DRC."""
import copy
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
import h6_r2_kicad_rules as rules


class Item(SimpleNamespace):
    def memberOfFootprint(self, selector):
        return selector in (self.ref, self.library)


def rule_body():
    return rules.BASE_RULES["LESHY2-RF-R2"].split(
        '(rule "RF J1 exact GCT locator to GND internal hole geometry"', 1)[1].split("# TI's", 1)[0]


def matches(a, b):
    # Evaluate the actual emitted finite condition, not a parallel predicate.
    # Only its documented string comparisons, conjunction/disjunction and
    # memberOfFootprint calls occur here; KiCad parses it again during real DRC.
    condition = re.search(r'\(condition "([^"]+)"\)', rule_body()).group(1)
    expression = condition.replace("&&", "and").replace("||", "or").replace("0.65mm", "0.65")
    return eval(expression, {"__builtins__": {}}, {"A": a, "B": b})


class UsbInternalHoleRuleTests(unittest.TestCase):
    def fixture(self, number="A1"):
        common = dict(Type="Pad", ref="J1", library="Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal")
        hole = Item(**common, Pad_Type="NPTH, mechanical", Pad_Number="", Hole_Size_X=.65, Hole_Size_Y=.65, NetName="")
        copper = Item(**common, Pad_Type="SMD", Pad_Number=number, Hole_Size_X=0, Hole_Size_Y=0,
                      NetName="/RF_01_USB_PD_CHARGE/POWER_GROUND")
        return hole, copper

    def test_four_exact_ground_names_and_both_operand_orders(self):
        for number in ("A1", "B12", "A12", "B1"):
            a, b = self.fixture(number)
            self.assertTrue(matches(a, b)); self.assertTrue(matches(b, a))
        self.assertIn("(constraint hole_clearance (min 0.19mm))", rule_body())
        self.assertNotIn("severity", rule_body())
        self.assertNotIn("exact GCT locator", rules.BASE_RULES["LESHY2-UI-R2"])

    def test_wrong_reference_library_type_hole_or_net_does_not_get_exception(self):
        mutations = [("ref", "J4"), ("ref", "U5"), ("library", "Other:USB"), ("Type", "Track")]
        for operand in (0, 1):
            for field, value in mutations:
                pair = self.fixture(); setattr(pair[operand], field, value)
                with self.subTest(operand=operand, field=field):
                    self.assertFalse(matches(*pair)); self.assertFalse(matches(*reversed(pair)))
        for field, value in (("Pad_Type", "Through-hole"), ("Pad_Number", "SH"),
                             ("Hole_Size_X", .66), ("Hole_Size_Y", .66)):
            a,b = self.fixture(); setattr(a,field,value)
            self.assertFalse(matches(a,b)); self.assertFalse(matches(b,a))
        for field, value in (("Pad_Type", "Through-hole"), ("Pad_Number", "A4"),
                             ("Pad_Number", "SH"), ("NetName", "/foreign/GND")):
            a,b = self.fixture(); setattr(b,field,value)
            self.assertFalse(matches(a,b)); self.assertFalse(matches(b,a))

    def test_nominal_package_rule_is_explicitly_not_factory_qualification(self):
        source = rules.BASE_RULES["LESHY2-RF-R2"]
        self.assertIn("nominal manufacturer pattern, not factory DFM qualification", source)
        self.assertEqual(1, source.count("(constraint hole_clearance (min 0.19mm))"))
        self.assertIn("(A.Reference == 'J4' && B.Reference == 'J4')", source)
        self.assertIn("(constraint hole_clearance (min 0.09mm))", source)


if __name__ == "__main__":
    unittest.main()
