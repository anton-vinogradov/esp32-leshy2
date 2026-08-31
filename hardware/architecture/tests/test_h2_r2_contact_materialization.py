import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_contact_materialization.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-contact-materialization.json"


class H2R2ContactMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.groups = {row["device_id"]: row for row in cls.artifact["groups"]}

    def contact(self, device_id, name):
        return next(
            row for row in self.groups[device_id]["contacts"] if row["contact"] == name
        )

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("1599 board contacts", result.stdout)
        self.assertIn("zero errors", result.stdout)

    def test_every_contact_and_named_pad_is_accounted_for(self):
        self.assertEqual("H2-R2.1.3", self.artifact["marker"])
        self.assertEqual("pass", self.artifact["status"])
        self.assertEqual([], self.artifact["errors"])
        summary = self.artifact["summary"]
        self.assertEqual(234, summary["board_component_group_count"])
        self.assertEqual(1656, summary["source_ledger_logical_contact_count"])
        self.assertEqual(1599, summary["board_logical_contact_count"])
        self.assertEqual(1596, summary["pcb_footprint_contact_count"])
        self.assertEqual(3, summary["external_on_module_interface_count"])
        self.assertEqual(0, summary["unresolved_error_count"])
        for group in self.artifact["groups"]:
            self.assertEqual(group["logical_contact_count"], len(group["contacts"]))
            self.assertTrue(group["footprint_sha256"], group["device_id"])

    def test_corrected_esp_module_pads_are_physical(self):
        c5 = self.groups["esp32_c5_wroom_1u_n8r8"]
        self.assertEqual(["19"], self.contact(c5["device_id"], "NC_19")["pads"])
        self.assertEqual(["20"], self.contact(c5["device_id"], "NC_20")["pads"])
        self.assertEqual(["22"], self.contact(c5["device_id"], "NC_22")["pads"])
        self.assertEqual(["1", "28", "29", "30", "32"], self.contact(c5["device_id"], "GND")["pads"])
        s3 = "esp32_s3_wroom_1u_n16r8"
        for number in (28, 29, 30):
            self.assertEqual([str(number)], self.contact(s3, f"NC_{number}")["pads"])

    def test_module_rf_receptacles_are_not_invented_carrier_pads(self):
        expected = {
            ("ebyte_e01_ml01sp4", "ANT"),
            ("esp32_c5_wroom_1u_n8r8", "ANT1"),
            ("esp32_s3_wroom_1u_n16r8", "ANT"),
        }
        actual = {
            (group["device_id"], contact["contact"])
            for group in self.artifact["groups"]
            for contact in group["contacts"]
            if contact["disposition"] == "external_on_module_interface"
        }
        self.assertEqual(expected, actual)
        for device_id, contact in actual:
            self.assertEqual([], self.contact(device_id, contact)["pads"])

    def test_switch_common_lands_and_merged_power_pads_are_explicit(self):
        self.assertEqual(["1"], self.contact("alps_skrtlae010", "C1")["pads"])
        self.assertEqual(["1"], self.contact("alps_skrtlae010", "C2")["pads"])
        self.assertEqual(
            {"1": ["C1", "C2"]},
            self.groups["alps_skrtlae010"]["shared_electrical_pads"],
        )
        tps = "ti_tps25751d_refr"
        self.assertEqual(["20"], self.contact(tps, "PPHV")["pads"])
        self.assertEqual(["23"], self.contact(tps, "VBUS_IN")["pads"])
        self.assertEqual(["39"], self.contact(tps, "GND_PAD")["pads"])
        self.assertEqual(["40"], self.contact(tps, "DRAIN_PAD")["pads"])

    def test_new_hirose_footprint_is_exact_and_complete(self):
        group = self.groups["hirose_fh34srj_50s_0_5sh_50"]
        self.assertEqual(52, group["footprint_named_pad_count"])
        self.assertEqual(52, group["footprint_pad_occurrence_count"])
        self.assertEqual(["MP1", "MP2"], group["mechanical_only_pads"])
        for number in range(1, 51):
            self.assertEqual([str(number)], self.contact(group["device_id"], f"PIN_{number}")["pads"])
        geometry = self.artifact["new_local_footprint_geometry"][group["device_id"]]
        self.assertEqual(50, geometry["positions"])
        self.assertEqual(0.5, geometry["pitch_mm"])
        self.assertEqual([27.0, 3.8, 1.0], geometry["body_mm"])
        self.assertEqual([0.3, 0.8], geometry["contact_pad_mm"])

    def test_airband_transformers_use_the_official_six_pad_land_pattern(self):
        for device_id in ("coilcraft_wbc1_1tlc", "coilcraft_wbc16_1tlc"):
            group = self.groups[device_id]
            self.assertEqual(6, group["footprint_named_pad_count"])
            self.assertEqual(6, group["footprint_pad_occurrence_count"])
            for number, contact in enumerate(
                ("SEC_A", "SEC_CT", "SEC_B", "PRI_A", "PRI_CT", "PRI_B"), start=1
            ):
                self.assertEqual([str(number)], self.contact(device_id, contact)["pads"])
            geometry = self.artifact["new_local_footprint_geometry"][device_id]
            self.assertEqual(6, geometry["positions"])
            self.assertEqual(1.52, geometry["pitch_mm"])
            self.assertEqual([4.45, 4.19, 3.05], geometry["body_max_mm"])

    def test_scope_remains_pre_net_and_pre_layout(self):
        auth = self.artifact["authorization"]
        self.assertTrue(auth["exact_contact_materialization"])
        self.assertTrue(auth["footprint_files"])
        for key in (
            "symbol_library",
            "schematic_nets",
            "kicad_project_creation",
            "pcb_placement_or_routing",
            "fabrication",
            "ordering",
        ):
            self.assertFalse(auth[key])


if __name__ == "__main__":
    unittest.main()
