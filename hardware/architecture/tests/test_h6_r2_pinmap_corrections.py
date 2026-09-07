"""Independent manufacturer pad numbers, not self-consistency with a generated library."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
# Package-specific primary pin tables, reviewed 2026-09-07:
# TI SCES351Y p3 (DCK), TI SCES640L p3 (DCU), Nexperia 74LVC1G32 Rev16.1 Table3.
EXPECTED = {
    "ti_sn74lvc1g17_dckr": {"NC": "1", "A": "2", "GND": "3", "Y": "4", "VCC": "5"},
    "ti_txs0102_dcur": {"B2": "1", "GND": "2", "VCCA": "3", "A2": "4", "A1": "5", "OE": "6", "VCCB": "7", "B1": "8"},
    "nexperia_74lvc1g32gv_125": {"1B": "1", "1A": "2", "GND": "3", "1Y": "4", "VCC": "5"},
}


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class H6R2PinmapCorrectionTests(unittest.TestCase):
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
