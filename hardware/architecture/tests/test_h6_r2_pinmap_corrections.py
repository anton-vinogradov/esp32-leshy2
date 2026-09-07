"""Independent manufacturer pad numbers, not self-consistency with a generated library."""

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
# Package-specific primary pin tables, reviewed 2026-09-07:
# TI SCES351Y p3 (DCK), TI SCES640L p3 (DCU), Nexperia 74LVC1G32 Rev16.1 Table3.
EXPECTED = {
    "ti_sn74lvc1g17_dckr": {"NC": "1", "A": "2", "GND": "3", "Y": "4", "VCC": "5"},
    "ti_txs0102_dcur": {"B2": "1", "GND": "2", "VCCA": "3", "A2": "4", "A1": "5", "OE": "6", "VCCB": "7", "B1": "8"},
    "nexperia_74lvc1g32gv_125": {"1B": "1", "1A": "2", "GND": "3", "1Y": "4", "VCC": "5"},
    "ti_tps3839k33_dbzr": {"GND": "1", "RESET_N": "2", "VDD": "3"},
    "omron_b3s_1100p": {"SIDE_A_1": "4", "SIDE_A_2": "3", "SIDE_B_1": "2", "SIDE_B_2": "1", "GROUND": "5"},
}


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class H6R2PinmapCorrectionTests(unittest.TestCase):
    def test_connector_contacts_are_conductors_not_panel_specific_internal_ncs(self):
        device = read("hardware/architecture/devices.json")["devices"]["hirose_fh34srj_50s_0_5sh_50"]
        self.assertEqual({f"PIN_{n}" for n in range(1, 51)}, set(device["contacts"]))
        self.assertEqual({"signal"}, {c["role"] for c in device["contacts"].values()})

    def test_native_generation_rejects_a_connected_inherent_nc_symbol_pin(self):
        from hardware.ecad.h2_r2_native_kicad import endpoint_target
        rows = [{"contact": "PIN_4", "disposition": "connected", "net": "TOUCH_RST_N"}]
        pin = {"number": "4", "contacts": ["PIN_4"], "type": "no_connect"}
        with self.assertRaisesRegex(ValueError, "inherent no_connect"):
            endpoint_target(rows, "display_connector", pin)
        pin["type"] = "passive"
        self.assertEqual(("connected", "TOUCH_RST_N"), endpoint_target(rows, "display_connector", pin))
        rows[0].update(disposition="no_connect", net=None)
        self.assertEqual(("no_connect", None), endpoint_target(rows, "display_connector", pin))

    def test_microsd_switch_letters_and_ufl_ground_land_count_are_not_guessed(self):
        material = read("hardware/ecad/h2-r2-contact-materialization-contract.json")
        aliases = next(v for v in material.values() if isinstance(v, dict) and "hirose_dm3at_sf_pejm5" in v)
        self.assertEqual(["10"], aliases["hirose_dm3at_sf_pejm5"]["DETECT_A"])
        self.assertEqual(["9"], aliases["hirose_dm3at_sf_pejm5"]["DETECT_B"])
        from hardware.ecad.h2_r2_contact_materialization import resolve_footprint, parse_pads
        groups = read("hardware/ecad/generated/H2-R2-contact-materialization.json")["groups"]
        ufl = next(g for g in groups if g["device_id"] == "hirose_ufl_r_smt_1_10")
        path, _ = resolve_footprint(ufl["footprint"])
        pads, _ = parse_pads(path)
        self.assertEqual(2, pads["2"]["occurrences"])
        self.assertEqual(1, pads["1"]["occurrences"])

    def test_service_usb_esd_uses_drt3_not_sot23(self):
        # TI SLVSAC2G DRT drawing 4206292-2/D; land pattern 4211172/A.
        from hardware.ecad.h2_r2_contact_materialization import resolve_footprint
        overrides = read("hardware/ecad/h2-r2-symbol-footprint-contract.json")["footprint_overrides"]
        footprint = overrides["Texas Instruments TPD2EUSB30ADRTR"]
        self.assertEqual("Package_TO_SOT_SMD:Texas_DRT-3", footprint)
        path, _ = resolve_footprint(footprint)
        text = path.read_text()
        for number, x, y in (("1", -0.35, 0.425), ("2", 0.35, 0.425), ("3", 0.0, -0.425)):
            block = re.search(r'\(pad "' + number + r'"\s+smd[\s\S]*?\(at ([\d.-]+) ([\d.-]+)\)[\s\S]*?\(size ([\d.-]+) ([\d.-]+)\)', text)
            self.assertIsNotNone(block)
            self.assertEqual((x, y, 0.3, 0.3), tuple(float(v) for v in block.groups()))
        devices = read("hardware/architecture/devices.json")["devices"]
        self.assertEqual([1.0, 0.8, 0.5], devices["ti_tpd2eusb30a_drtr"]["dimensions_mm"])

    def test_omron_manufacturer_numbers_keep_the_same_physical_switch_sides(self):
        # Omron en-b3s p2 TOP view. New current footprint; historical library is immutable.
        text = (ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/B3S-1100P.kicad_mod").read_text()
        pads = {n: (float(x), float(y)) for n, x, y in re.findall(r'\(pad "(\d+)" smd rect \(at ([\d.-]+) ([\d.-]+)\)', text)}
        self.assertEqual({"4": (-3.98, -3.17), "3": (3.98, -3.17), "2": (-3.98, 1.33), "1": (3.98, 1.33), "5": (0.0, 3.17)}, pads)
        device = read("hardware/architecture/devices.json")["devices"]["omron_b3s_1100p"]
        for pair, y in zip(device["internally_common_contacts"], (-3.17, 1.33)):
            self.assertEqual([y, y], [pads[device["contacts"][c]["physical"]][1] for c in pair])

    def test_source_and_materialized_pad_maps_match_package_specific_tables(self):
        devices = read("hardware/architecture/devices.json")["devices"]
        material = {row["device_id"]: row for row in read("hardware/ecad/generated/H2-R2-contact-materialization.json")["groups"]}
        for device, expected in EXPECTED.items():
            with self.subTest(device=device):
                self.assertEqual(expected, {name: row["physical"] for name, row in devices[device]["contacts"].items()})
                self.assertEqual(expected, {row["contact"]: row["physical"] for row in material[device]["contacts"]})

    def test_corrected_physical_pins_retain_logical_functions(self):
        rows = {row["endpoint"]: row for row in read("hardware/ecad/generated/H2-R2-native-net-ledger.json")["rows"]}
        expected = {
            "safe_rearm_buffer.A": ("2", "SAFE_REARM_DELAY"),
            "safe_rearm_buffer.NC": ("1", None),
            "unit_signal_iso.VCCA": ("3", "3V3_MAIN"),
            "unit_signal_iso.GND": ("2", "POWER_GROUND"),
            "unit_signal_iso.A1": ("5", "M5_UNIT_SIG0"),
            "unit_signal_iso.A2": ("4", "M5_UNIT_SIG1"),
            "unit_signal_iso.B1": ("8", "UNIT_CONNECTOR_SIG0"),
            "unit_signal_iso.B2": ("1", "UNIT_CONNECTOR_SIG1"),
            "unit_signal_iso.OE": ("6", "UNIT_READY"),
        }
        for endpoint, pair in expected.items():
            with self.subTest(endpoint=endpoint):
                self.assertEqual(pair, (rows[endpoint]["physical"], rows[endpoint]["net"]))

    def test_internal_flash_supply_is_not_an_external_qspi_signal_no_connect(self):
        rows = {row["endpoint"]: row for row in read("hardware/ecad/generated/H2-R2-native-net-ledger.json")["rows"]}
        for owner in ("hub_rp", "rf_rp"):
            with self.subTest(owner=owner):
                supply = rows[f"{owner}.QSPI_IOVDD"]
                self.assertEqual(("69", "connected", "3V3_MAIN"), (supply["physical"], supply["disposition"], supply["net"]))
                self.assertEqual("3V3_MAIN", rows[f"{owner}_qspi_iovdd_bypass.END_1"]["net"])
                self.assertEqual("POWER_GROUND", rows[f"{owner}_qspi_iovdd_bypass.END_2"]["net"])
                for signal in ("QSPI_SD0", "QSPI_SD1", "QSPI_SD2", "QSPI_SD3", "QSPI_SCLK"):
                    self.assertEqual("no_connect", rows[f"{owner}.{signal}"]["disposition"])

    def test_flash_decoupling_is_measured_to_pad69_not_the_nearest_other_supply(self):
        policy = read("hardware/layout/h6-r2-placement-contract.json")["placement_policy"]
        audit = read("hardware/layout/generated/H6-R2-placement-audit.json")
        actual = [row for board in audit["boards"] for row in board["critical_pad_pairs"]["rows"]]
        for owner in ("hub_rp", "rf_rp"):
            cap = f"{owner}_qspi_iovdd_bypass"
            expected = [row for row in policy["critical_pad_pairs"] if row["first_instance"] == owner and row["second_instance"] == cap]
            self.assertEqual(1, len(expected))
            self.assertEqual("69", expected[0]["first_pad_number"])
            self.assertEqual("1", expected[0]["second_pad_number"])
            pairs = [row for row in actual if row["first_instance"] == owner and row["second_instance"] == cap]
            self.assertEqual(1, len(pairs))
            self.assertEqual(("69", "1"), (pairs[0]["first_pad"], pairs[0]["second_pad"]))
            self.assertLessEqual(pairs[0]["pad_centre_distance_mm"], 3.0)


if __name__ == "__main__":
    unittest.main()
