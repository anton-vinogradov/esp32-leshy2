"""Source-only regression for distinct LCD-tail and FH34 contact numbering.

No generated artifact is rewritten. The golden world-net list was read from
the native UI J1 before the coordinated manufacturer-number correction.
"""

import copy
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LEDGER = load_module("h2_r2_display_mating_ledger", "hardware/ecad/h2_r2_net_ledger.py")
G3 = load_module("h2_r2_display_mating_g3", "hardware/product-design/g3_clamshell.py")


class DisplayMatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads((ROOT / "hardware/product-design/display-mount.json").read_text())
        cls.topology = json.loads((ROOT / "hardware/ecad/h2-r2-topology-overrides.json").read_text())
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-net-ledger-contract.json").read_text())
        cls.aliases = contract["canonical_net_aliases"]
        cls.footprint = (ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/FH34SRJ-50S-0.5SH-50.kicad_mod").read_text()
        cls.pads = {
            number: (float(x), float(y))
            for number, x, y in re.findall(
                r'\(pad "([^"]+)" smd \w+ \(at ([\d.-]+) ([\d.-]+)\)', cls.footprint
            )
        }
        cls.devices, cls.candidate, cls.instances, *_ = G3.load()

    def sources(self, design=None, topology=None):
        return {
            "h0": {}, "dual_rp": {}, "c5_mux": {}, "pack_safety_boundary": {},
            "display_mount": self.design if design is None else design,
            "h1_routes": {}, "_h1_route_index": {}, "_h1_allocation_index": {},
            "_h1_route_net_aliases": {},
            "topology": self.topology if topology is None else topology,
        }

    def test_complete_manufacturer_to_tail_bijection(self):
        for panel in range(1, 51):
            contact = f"PIN_{51 - panel}"
            self.assertEqual(str(panel), LEDGER.display_panel_position(self.design, contact))
        self.assertEqual(50, len(set(self.design["electrical"]["panel_to_connector_pin_map"].values())))

    def test_manufacturer_numbering_on_unchanged_lands(self):
        self.assertEqual({str(n) for n in range(1, 51)} | {"MP1", "MP2"}, set(self.pads))
        for contact in range(1, 51):
            self.assertEqual((12.25 - (contact - 1) * 0.5, -1.65), self.pads[str(contact)])
        self.assertEqual((-13.05, 1.65), self.pads["MP1"])
        self.assertEqual((13.05, 1.65), self.pads["MP2"])
        self.assertIn('(start 12.600 -2.250)', self.footprint)
        self.assertNotIn('(start -12.600 -2.250)', self.footprint)

    def test_all_fifty_world_land_nets_are_preserved(self):
        # Native UI J1 before correction: B.Cu rot0, anchor[40,35.4],
        # old tail-numbered pad1 at[27.75,37.05], pad50 at[52.25,37.05].
        expected = [
            "LCD_LEDA_PROTECTED", "LCD_LEDK", "LCD_LEDK", None, None, None,
            "3V3_MAIN", "3V3_MAIN", "POWER_GROUND", "LCD_RST_N",
            *(["POWER_GROUND"] * 14),
            "LCD_DB7", "LCD_DB6", "LCD_DB5", "LCD_DB4", "LCD_DB3", "LCD_DB2", "LCD_DB1", "LCD_DB0",
            None, None, "3V3_MAIN", "LCD_WR_N", "LCD_DC", "POWER_GROUND", None,
            "3V3_MAIN", "3V3_MAIN", "3V3_MAIN", "POWER_GROUND",
            "SYS_UI_I2C_SCL", "SYS_UI_I2C_SDA", "LCD_TOUCH_INT_RAW_N", "TOUCH_RST_N",
            "POWER_GROUND", "POWER_GROUND", "POWER_GROUND",
        ]
        self.assertEqual(50, len(expected))
        for panel, expected_net in enumerate(expected, 1):
            contact = str(51 - panel)
            x, y = self.pads[contact]
            self.assertAlmostEqual(27.75 + (panel - 1) * 0.5, 40.0 + x)
            self.assertAlmostEqual(37.05, 35.4 - y)  # B.Cu local-Y reflection
            net, origin = LEDGER.current_override("display_connector", f"PIN_{contact}", self.sources(), self.aliases)
            self.assertEqual(expected_net, net, f"panel {panel} -> FH34 {contact}")
            self.assertIsNotNone(origin)

    def test_five_topology_straps_use_manufacturer_positions(self):
        actual = {k: v for k, v in self.topology["endpoint_overrides"].items() if k.startswith("display_connector.")}
        self.assertEqual({
            "display_connector.PIN_44": "3V3_MAIN", "display_connector.PIN_43": "3V3_MAIN",
            "display_connector.PIN_42": "POWER_GROUND", "display_connector.PIN_16": "3V3_MAIN",
            "display_connector.PIN_13": "POWER_GROUND",
        }, actual)

    def test_current_display_mechanical_validation_passes(self):
        self.assertEqual([], G3.validate_display_mount_design(self.design, self.devices, self.candidate, self.instances))

    def test_identity_missing_partial_duplicate_or_changed_maps_fail_closed(self):
        expected = self.design["electrical"]["panel_to_connector_pin_map"]
        candidates = [None, {}, {str(n): str(n) for n in range(1, 51)}]
        partial = dict(expected); partial.pop("1"); candidates.append(partial)
        duplicate = dict(expected); duplicate["1"] = duplicate["2"]; candidates.append(duplicate)
        swapped = dict(expected); swapped["1"], swapped["2"] = swapped["2"], swapped["1"]; candidates.append(swapped)
        wrong_type = dict(expected); wrong_type["1"] = 50; candidates.append(wrong_type)
        for mapping in candidates:
            with self.subTest(mapping=mapping):
                design = copy.deepcopy(self.design)
                design["electrical"]["panel_to_connector_pin_map"] = mapping
                with self.assertRaisesRegex(ValueError, "bijection"):
                    # PIN44 has a topology override: invalid mapping must fail
                    # before that early-return path, not only for data pins.
                    LEDGER.current_override("display_connector", "PIN_44", self.sources(design), self.aliases)
                errors = G3.validate_display_mount_design(design, self.devices, self.candidate, self.instances)
                self.assertTrue(any("bijection" in e for e in errors), errors)

    def test_invalid_manufacturer_contact_fails_closed(self):
        for contact in ("PIN_0", "PIN_51", "PIN_01", "PIN_-1", "PIN_1.0", "PIN_x"):
            with self.subTest(contact=contact), self.assertRaisesRegex(ValueError, "invalid FH34"):
                LEDGER.display_panel_position(self.design, contact)

    def test_old_identity_orientation_is_rejected(self):
        design = copy.deepcopy(self.design)
        design["orientation"]["connector_pin_1_world_side"] = "board left / world x-min"
        design["orientation"]["connector_pin_50_world_side"] = "board right / world x-max"
        errors = G3.validate_display_mount_design(design, self.devices, self.candidate, self.instances)
        self.assertTrue(any("connector pin 1 must mate tail pin 50" in e for e in errors))
        self.assertTrue(any("connector pin 50 must mate tail pin 1" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
