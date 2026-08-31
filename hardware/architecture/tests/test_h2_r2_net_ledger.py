import json
import subprocess
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_net_ledger.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
DEFINITIONS = ROOT / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"
H0 = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
DUAL_RP = ROOT / "hardware/architecture/h1-r2-dual-rp-pinout.json"


class H2R2NetLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.rows = cls.ledger["rows"]
        cls.by_endpoint = {row["endpoint"]: row for row in cls.rows}

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("4323 current R2 endpoints reconciled", result.stdout)

    def test_every_current_instance_contact_occurs_once(self):
        instances = json.loads(INSTANCES.read_text(encoding="utf-8"))["rows"]
        definitions = {
            row["device_id"]: row
            for row in json.loads(DEFINITIONS.read_text(encoding="utf-8"))["groups"]
        }
        expected = {
            f"{instance['instance']}.{contact}"
            for instance in instances
            for contact in definitions[instance["device_id"]]["contact_map"]
        }
        self.assertEqual(expected, set(self.by_endpoint))
        self.assertEqual(4323, len(expected))
        self.assertFalse([
            endpoint for endpoint, count in Counter(row["endpoint"] for row in self.rows).items()
            if count != 1
        ])

    def test_summary_closes_without_unresolved_or_hidden_external_contacts(self):
        summary = self.ledger["summary"]
        self.assertEqual("pass", self.ledger["status"])
        self.assertEqual([], self.ledger["errors"])
        self.assertEqual(4323, summary["endpoint_count"])
        self.assertEqual(4063, summary["connected_endpoint_count"])
        self.assertEqual(260, summary["no_connect_endpoint_count"])
        self.assertEqual(0, summary["external_interface_endpoint_count"])
        self.assertEqual(0, summary["unresolved_endpoint_count"])
        self.assertEqual(826, summary["unique_net_count"])

    def test_m1_contacts_match_on_both_projects(self):
        for position in range(1, 81):
            front = self.by_endpoint[f"m1_ui_plug.P{position}"]
            rear = self.by_endpoint[f"m1_rf_receptacle.P{position}"]
            self.assertEqual(front["disposition"], rear["disposition"])
            self.assertEqual(front["net"], rear["net"])
            self.assertIn(front["origin"], {"current_h0_m1_map", "current_h0_m1_explicit_nc"})

    def test_current_s3_and_dual_rp_gpio_maps_are_exact(self):
        h0 = json.loads(H0.read_text(encoding="utf-8"))
        aliases = self.ledger["canonical_net_aliases"]
        for row in h0["s3"]["pin_map"]:
            endpoint = self.by_endpoint[f"s3.GPIO{row['gpio']}"]
            if row["direction"] == "reserve":
                self.assertIsNone(endpoint["net"])
                self.assertEqual("current_h0_reserved_gpio_explicit_nc", endpoint["origin"])
            else:
                self.assertEqual(aliases.get(row["net"], row["net"]), endpoint["net"])
                self.assertEqual("current_h0_s3_pin_map", endpoint["origin"])
        dual = json.loads(DUAL_RP.read_text(encoding="utf-8"))
        for owner in ("hub_rp", "rf_rp"):
            for row in dual[owner]["pin_map"]:
                endpoint = self.by_endpoint[f"{owner}.GPIO{row['gpio']}"]
                if row["direction"] == "reserve":
                    self.assertIsNone(endpoint["net"])
                    self.assertEqual("current_h1_reserved_gpio_explicit_nc", endpoint["origin"])
                else:
                    self.assertEqual(aliases.get(row["net"], row["net"]), endpoint["net"])
                    self.assertEqual("current_h1_dual_rp_pin_map", endpoint["origin"])

    def test_both_stacked_flash_buses_are_explicit_board_no_connects(self):
        contacts = ("QSPI_SD3", "QSPI_SCLK", "QSPI_SD0", "QSPI_SD2", "QSPI_SD1")
        for owner in ("hub_rp", "rf_rp"):
            for contact in contacts:
                row = self.by_endpoint[f"{owner}.{contact}"]
                self.assertEqual("no_connect", row["disposition"])
                self.assertIsNone(row["net"])
                self.assertEqual("current_exact_stacked_flash_no_connect", row["origin"])

    def test_pack_safety_and_display_current_overrides_are_not_historical(self):
        origins = Counter(row["origin"] for row in self.rows)
        self.assertEqual(7, origins["current_pack_safety_boundary"])
        self.assertEqual(8, origins["current_pack_safety_decoupling"])
        self.assertEqual(97, origins["current_display_adapter_map"])
        self.assertEqual(24, origins["current_display_adapter_explicit_nc"])
        self.assertEqual(
            "HUB_SAFE_I2C_SDA_MAIN",
            self.by_endpoint["hub_safe_i2c_boundary.SDAA"]["net"],
        )

    def test_functional_route_aliases_resolve_to_one_physical_net(self):
        aliases = self.ledger["canonical_net_aliases"]
        self.assertEqual("AON_RAW_3V3", aliases["AON_EFUSE_EN"])
        self.assertEqual("POWER_GROUND", aliases["PACK_SHUNT_CSN"])
        self.assertEqual("FAULT_KILL", aliases["FAULT_LATCH_SENSE_AON"])
        self.assertEqual("RX_RST_N", aliases["RECEIVER_READY"])
        for row in self.rows:
            self.assertNotIn("route_alias_conflict", row["origin"])

    def test_airband_is_fail_direct_fail_off_and_power_coherent(self):
        expected = {
            "airband_power_switch.ON": "AIR_RX_EN",
            "airband_power_switch.VOUT": "3V3_AIR_SWITCHED",
            "air_input_selector.RFC": "RX_FMSW_BOUNDARY_RF",
            "air_input_selector.RF1": "AIR_DIRECT_RAW_RF",
            "air_input_selector.RF2": "AIR_BPF_IN_RF",
            "air_input_selector.A": "AIR_RX_MODE",
            "air_input_selector.B": "AIR_RX_MODE_N",
            "air_path_selector.RF1": "AIR_DIRECT_RF",
            "air_path_selector.RF2": "AIR_CONVERTED_RF",
            "air_path_selector.A": "AIR_RX_MODE",
            "air_path_selector.B": "AIR_RX_MODE_N",
            "air_lo.VDD": "3V3_AIR_SWITCHED",
            "air_lo.VDDO": "3V3_AIR_SWITCHED",
            "air_lo.SDA": "AIR_LO_I2C_SDA",
            "air_lo.SCL": "AIR_LO_I2C_SCL",
            "rf_rp.GPIO28": "AIR_LO_I2C_SDA",
            "rf_rp.GPIO29": "AIR_LO_I2C_SCL",
            "receiver_fmi_match_inductor.END_1": "AIR_RX_SELECTED_RF",
        }
        for endpoint, net in expected.items():
            self.assertEqual(net, self.by_endpoint[endpoint]["net"], endpoint)
            self.assertEqual("connected", self.by_endpoint[endpoint]["disposition"])
        self.assertEqual("no_connect", self.by_endpoint["airband_power_switch.NC"]["disposition"])
        self.assertEqual("no_connect", self.by_endpoint["airband_mode_inverter.2Y"]["disposition"])

    def test_historical_sources_remain_non_authoritative_hints(self):
        for name, source in self.ledger["sources"].items():
            if name.startswith("historical_"):
                self.assertFalse(source["authority"])
        historical = [row for row in self.rows if row["origin"].startswith("reconciled_historical")]
        self.assertEqual(3315, len(historical))
        self.assertTrue(all(row["historical_topology_authority"] is False for row in historical))
        self.assertFalse(self.ledger["authorization"]["kicad_project_creation"])


if __name__ == "__main__":
    unittest.main()
