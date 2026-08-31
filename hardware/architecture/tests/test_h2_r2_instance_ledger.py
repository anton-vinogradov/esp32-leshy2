import json
import subprocess
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_instance_ledger.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"


class H2R2InstanceLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.rows = cls.ledger["rows"]

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("1185 exact fitted R2 instances", result.stdout)

    def test_all_groups_quantities_projects_and_sheets_close(self):
        self.assertEqual("pass", self.ledger["status"])
        self.assertEqual([], self.ledger["errors"])
        summary = self.ledger["summary"]
        self.assertEqual(1185, summary["fitted_board_instance_count"])
        self.assertEqual(234, summary["component_group_count"])
        self.assertEqual(23, summary["project_graph_sheet_count"])
        self.assertEqual(len(summary["sheet_counts"]), summary["populated_sheet_count"])
        self.assertEqual(
            {"L2-DISP-ADP-001-B", "LESHY2-RF-R2", "LESHY2-UI-R2"},
            set(summary["project_counts"]),
        )
        self.assertNotIn("controlled_symbol_library", self.ledger["sources"])

    def test_references_and_project_local_names_are_unique(self):
        for field in ("instance", "reference"):
            counts = Counter((row["project"], row[field]) for row in self.rows)
            self.assertFalse([key for key, count in counts.items() if count != 1])

    def test_two_rp_domains_and_service_paths_are_independent(self):
        names = {row["instance"]: row for row in self.rows}
        for prefix, project, sheet in (
            ("hub_rp", "LESHY2-UI-R2", "UI_30_HUB_RP_CORE_SERVICE"),
            ("rf_rp", "LESHY2-RF-R2", "RF_10_RP2354_CORE_SERVICE"),
        ):
            self.assertEqual("rp2354b_a4", names[prefix]["device_id"])
            self.assertEqual(project, names[prefix]["project"])
            self.assertEqual(sheet, names[prefix]["sheet"])
            for suffix in ("clock", "service_usb_switch", "dbg_header"):
                self.assertIn(f"{prefix}_{suffix}", names)

    def test_removed_r1_only_bodies_are_absent(self):
        device_ids = {row["device_id"] for row in self.rows}
        self.assertTrue(
            {
                "adi_ad8314acpz_rl7", "microchip_24aa02uidt_i_ot",
                "samtec_tsw_107_07_g_d", "ti_sn74lvc1g123_dctr",
                "ti_tps7a2033_pdbvr", "ttm_dc0710j5020ahf",
            }.isdisjoint(device_ids)
        )
        names = {row["instance"] for row in self.rows}
        self.assertTrue(
            {"rf_detector", "evidence_monostable", "identity", "local_regulator"}.isdisjoint(names)
        )

    def test_current_replacements_and_pack_boundary_are_present(self):
        by_name = {row["instance"]: row for row in self.rows}
        self.assertEqual("adi_ad8314armz_reel", by_name["det_nrf0"]["device_id"])
        self.assertEqual("hirose_fh34srj_50s_0_5sh_50", by_name["display_panel_connector"]["device_id"])
        self.assertEqual("ti_tca9803_dgkr", by_name["hub_safe_i2c_boundary"]["device_id"])
        self.assertEqual("RF_02_PACK_SAFETY_AON", by_name["hub_safe_i2c_boundary"]["sheet"])
        self.assertNotIn("evidence_mask_p17_pulldown", by_name)
        self.assertEqual(
            "yageo_rc0402fr_0710kl",
            by_name["safety_s3_reset_pulldown"]["device_id"],
        )
        self.assertEqual(
            "RF_50_TX_SAFETY_EVIDENCE",
            by_name["safety_s3_reset_pulldown"]["sheet"],
        )

    def test_complete_airband_chain_is_allocated_to_one_rear_sheet(self):
        by_name = {row["instance"]: row for row in self.rows}
        expected = {
            "air_input_selector": "adi_hmc544aetr",
            "air_path_selector": "adi_hmc544aetr",
            "air_lna": "minicircuits_pga_103_plus",
            "air_mixer": "adi_lt5560edd_trpbf",
            "air_lo": "skyworks_si5351a_b_gtr",
            "air_mixer_input_transformer": "coilcraft_wbc1_1tlc",
            "air_mixer_output_transformer": "coilcraft_wbc16_1tlc",
        }
        for instance, device_id in expected.items():
            self.assertEqual(device_id, by_name[instance]["device_id"])
            self.assertEqual("LESHY2-RF-R2", by_name[instance]["project"])
            self.assertEqual("RF_21_BROADCAST_AIRBAND_RX", by_name[instance]["sheet"])

    def test_historical_source_is_explicitly_non_authoritative(self):
        source = self.ledger["sources"]["historical_instance_hints"]
        self.assertFalse(source["authority"])
        self.assertTrue(all(row["historical_topology_authority"] is False for row in self.rows))
        self.assertEqual(0, self.ledger["summary"]["native_schematic_nets_created"])


if __name__ == "__main__":
    unittest.main()
