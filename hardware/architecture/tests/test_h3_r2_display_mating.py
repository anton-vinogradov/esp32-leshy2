"""Independent H3 functions survive distinct panel/FH34 contact numbers."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"hardware/verification/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ANALOG = load_module("h3_r2_analog_corners")
DIGITAL = load_module("h3_r2_digital_interfaces")


class H3R2DisplayMatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads((ROOT / "hardware/product-design/display-mount.json").read_text())
        # Golden physical FH34 contact functions, not derived from a generator
        # or panel_to_connector_pin_map. 50 is leftmost LEDA; 1 is rightmost GND.
        cls.contact_nets = {
            50: "LCD_LEDA_PROTECTED", 49: "LCD_LEDK", 48: "LCD_LEDK",
            44: "3V3_MAIN", 43: "3V3_MAIN", 42: "POWER_GROUND",
            19: "LCD_DB0", 20: "LCD_DB1", 21: "LCD_DB2", 22: "LCD_DB3",
            23: "LCD_DB4", 24: "LCD_DB5", 25: "LCD_DB6", 26: "LCD_DB7",
            17: None, 16: "3V3_MAIN", 15: "LCD_WR_N", 14: "LCD_DC",
            13: "POWER_GROUND", 11: "3V3_MAIN", 10: "3V3_MAIN", 9: "3V3_MAIN",
        }
        peripheral_nets = {
            "backlight_efuse.OUT": "LCD_LEDA_PROTECTED",
            "backlight_series_resistor.END_1": "LCD_LEDK",
            "backlight_series_resistor.END_2": "LCD_LEDK_LIMITED",
            "backlight_mosfet.D": "LCD_LEDK_LIMITED",
            "backlight_mosfet.S": "POWER_GROUND",
            "backlight_mosfet.G": "LCD_BACKLIGHT_GATE",
            "backlight_gate_pulldown.END_1": "LCD_BACKLIGHT_GATE",
            "s3.GPIO4": "LCD_DB0", "s3.GPIO9": "LCD_DB1", "s3.GPIO18": "LCD_DB2",
            "s3.GPIO38": "LCD_DB3", "s3.GPIO40": "LCD_DB4", "s3.GPIO41": "LCD_DB5",
            "s3.GPIO42": "LCD_DB6", "s3.GPIO46": "LCD_DB7",
            "s3.GPIO17": "LCD_WR_N", "s3.GPIO45": "LCD_DC",
        }
        nets = {f"display_connector.PIN_{pin}": net for pin, net in cls.contact_nets.items()}
        nets.update(peripheral_nets)
        cls.rows = [{"endpoint": endpoint, "instance": endpoint.split(".")[0], "net": net}
                    for endpoint, net in nets.items()]

    def test_manufacturer_contact_fixture_passes_both_independent_verifiers(self):
        for module in (ANALOG, DIGITAL):
            with self.subTest(module=module.__name__):
                checks = module.display_topology_checks(self.rows, self.design)
                self.assertTrue(all(checks.values()), checks)

    def test_old_identity_contact_numbering_does_not_pass(self):
        rows = copy.deepcopy(self.rows)
        for row in rows:
            if row["instance"] == "display_connector":
                old = int(row["endpoint"].rsplit("_", 1)[1])
                row["endpoint"] = f"display_connector.PIN_{51 - old}"
        for module in (ANALOG, DIGITAL):
            self.assertFalse(all(module.display_topology_checks(rows, self.design).values()))

    def test_each_analog_panel_contact_function_is_checked(self):
        # LEDA, both LEDK, VDDI40/41, VCI42, eight DB lanes and WR36.
        for contact in (50, 49, 48, 11, 10, 9, *range(19, 27), 15):
            with self.subTest(contact=contact):
                rows = copy.deepcopy(self.rows)
                next(row for row in rows if row["endpoint"] == f"display_connector.PIN_{contact}")["net"] = "WRONG_NET"
                self.assertFalse(all(ANALOG.display_topology_checks(rows, self.design).values()))

    def test_each_digital_panel_contact_function_is_checked(self):
        for contact in (*range(19, 27), 15, 14, 13, 16, 44, 43, 42, 17):
            with self.subTest(contact=contact):
                rows = copy.deepcopy(self.rows)
                next(row for row in rows if row["endpoint"] == f"display_connector.PIN_{contact}")["net"] = "WRONG_NET"
                self.assertFalse(all(DIGITAL.display_topology_checks(rows, self.design).values()))

    def test_missing_wrong_or_partial_bijection_fails_closed(self):
        good = self.design["electrical"]["panel_to_connector_pin_map"]
        swapped = dict(good)
        swapped["1"], swapped["2"] = swapped["2"], swapped["1"]
        variants = (None, {}, {str(n): str(n) for n in range(1, 51)},
                    {k: v for k, v in good.items() if k != "50"}, swapped,
                    {k: int(v) for k, v in good.items()})
        for module in (ANALOG, DIGITAL):
            for mapping in variants:
                design = copy.deepcopy(self.design)
                design["electrical"]["panel_to_connector_pin_map"] = mapping
                with self.subTest(module=module.__name__, mapping=mapping):
                    with self.assertRaisesRegex(ValueError, "bijection"):
                        module.display_topology_checks(self.rows, design)

    def test_panel_pin_map_cannot_redefine_verifier_function_expectations(self):
        design = copy.deepcopy(self.design)
        design["electrical"]["panel_pin_map"] = {"1": {"net": "WRONG_NET"}}
        for module in (ANALOG, DIGITAL):
            self.assertTrue(all(module.display_topology_checks(self.rows, design).values()))
        rows = copy.deepcopy(self.rows)
        next(row for row in rows if row["endpoint"] == "display_connector.PIN_50")["net"] = "WRONG_NET"
        self.assertFalse(ANALOG.display_topology_checks(rows, design)["backlight_anode_is_latch_protected"])

    def test_invalid_panel_pins_fail_closed(self):
        for module in (ANALOG, DIGITAL):
            for pin in (0, 51, -1, True, 1.0, "1"):
                with self.assertRaisesRegex(ValueError, "invalid physical"):
                    module.panel_endpoint(self.design, pin)


if __name__ == "__main__":
    unittest.main()
