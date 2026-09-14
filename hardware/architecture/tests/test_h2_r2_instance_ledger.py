import copy
import hashlib
import importlib.util
import json
import subprocess
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_instance_ledger.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
SPEC = importlib.util.spec_from_file_location("h2_r2_instance_ledger", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


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
        self.assertIn("1208 exact R2 board instances", result.stdout)

    def test_all_groups_quantities_projects_and_sheets_close(self):
        self.assertEqual("pass", self.ledger["status"])
        self.assertEqual([], self.ledger["errors"])
        summary = self.ledger["summary"]
        self.assertEqual(1208, summary["fitted_board_instance_count"])
        self.assertEqual(244, summary["component_group_count"])
        self.assertEqual(22, summary["project_graph_sheet_count"])
        self.assertEqual(len(summary["sheet_counts"]), summary["populated_sheet_count"])
        self.assertEqual(
            {"LESHY2-RF-R2", "LESHY2-UI-R2"},
            set(summary["project_counts"]),
        )
        self.assertNotIn("controlled_symbol_library", self.ledger["sources"])

    def test_references_and_project_local_names_are_unique(self):
        for field in ("instance", "reference"):
            counts = Counter((row["project"], row[field]) for row in self.rows)
            self.assertFalse([key for key, count in counts.items() if count != 1])

    def test_four_usb_ports_share_one_part_without_losing_their_owners(self):
        # A smaller group count alone could hide a missing or misallocated port.
        # This is the current R2 population, not the immutable 33908 audit.
        ports = [row for row in self.rows if row["device_id"] == "gct_usb4105_gf_a"]
        self.assertEqual(4, len(ports))
        self.assertEqual(
            {
                ("LESHY2-RF-R2", "J1", "product_usb_connector", "RF_01_USB_PD_CHARGE"),
                ("LESHY2-RF-R2", "J4", "rf_rp_service_usb_connector", "RF_10_RP2354_CORE_SERVICE"),
                ("LESHY2-UI-R2", "J9", "c5_service_usb_connector", "UI_20_C5_WIFI_IR_SERVICE"),
                ("LESHY2-UI-R2", "J11", "hub_rp_service_usb_connector", "UI_30_HUB_RP_CORE_SERVICE"),
            },
            {(row["project"], row["reference"], row["instance"], row["sheet"]) for row in ports},
        )
        self.assertEqual({"GCT USB4105-GF-A"}, {row["mpn"] for row in ports})
        self.assertEqual(
            {"Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"},
            {row["footprint"] for row in ports},
        )
        self.assertNotIn("jae_dx07s016ja1r1500", {row["device_id"] for row in self.rows})

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
        self.assertEqual("hirose_fh34srj_50s_0_5sh_50", by_name["display_connector"]["device_id"])
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

    def test_empty_reference_overrides_preserve_all_1208_frozen_references_and_output_bytes(self):
        frozen = sorted((row["project"], row["instance"], row["reference"]) for row in self.rows)
        self.assertEqual(1208, len(frozen))
        self.assertEqual(
            "216e588158c69e18ff7f60999b14a26ea543388b2c705a98cc6fd89513b60250",
            hashlib.sha256(json.dumps(frozen, separators=(",", ":")).encode()).hexdigest(),
        )
        original = copy.deepcopy(self.rows)
        assigned = MODULE.assign_references(list(reversed(self.rows)), {})
        self.assertEqual(original, assigned)
        self.assertEqual(original, self.rows)
        self.assertIsNot(self.rows[0], assigned[0])
        # Missing optional field and an explicit empty mapping produce the same
        # entire artifact, not merely the same references or counts.
        real_load = MODULE.load
        for explicit_empty in (False, True):
            contract = copy.deepcopy(real_load(MODULE.CONTRACT))
            contract.pop("reference_overrides", None)
            if explicit_empty:
                contract["reference_overrides"] = {}
            with mock.patch.object(MODULE, "load", side_effect=lambda path: (
                contract if path == MODULE.CONTRACT else real_load(path)
            )):
                result = MODULE.build()
            self.assertEqual([], result["errors"])
            self.assertEqual(OUTPUT.read_bytes(),
                             (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())

    def appended_reference_fixture(self):
        project = "LESHY2-UI-R2"
        rows = copy.deepcopy(self.rows)
        overrides = {project: {}}
        for prefix, suffix in (("U", "logic"), ("C", "bypass")):
            source = next(row for row in rows if row["reference_prefix"] == prefix
                          and row["sheet"] == "UI_20_C5_WIFI_IR_SERVICE")
            row = dict(source)
            instance = f"c5_service_candidate_{suffix}"
            row.update(instance=instance, instance_uid=f"{project}:{instance}")
            row.pop("reference")
            number = max(int(item["reference"][len(prefix):]) for item in self.rows
                         if item["project"] == project and item["reference_prefix"] == prefix) + 1
            overrides[project][instance] = f"{prefix}{number}"
            rows.append(row)
        return rows, overrides

    def test_two_inserted_ui20_rows_with_append_refs_preserve_every_existing_row(self):
        rows, overrides = self.appended_reference_fixture()
        original = copy.deepcopy(rows)
        assigned = MODULE.assign_references(rows, overrides)
        self.assertEqual(1210, len(assigned))
        old = {row["instance_uid"]: row for row in self.rows}
        self.assertEqual(old, {row["instance_uid"]: row for row in assigned if row["instance_uid"] in old})
        self.assertEqual(rows, original)
        self.assertEqual(
            overrides["LESHY2-UI-R2"],
            {row["instance"]: row["reference"] for row in assigned if row["instance_uid"] not in old},
        )
        naive = MODULE.assign_references(rows, {})
        shifted = [row for row in naive if row["instance_uid"] in old
                   and row["reference"] != old[row["instance_uid"]]["reference"]]
        self.assertEqual({"U", "C"}, {row["reference_prefix"] for row in shifted})
        self.assertEqual({"LESHY2-UI-R2"}, {row["project"] for row in shifted})

    def test_reference_overrides_reject_auto_and_explicit_collisions_without_mutation(self):
        rows, overrides = self.appended_reference_fixture()
        overrides["LESHY2-UI-R2"]["c5_service_candidate_logic"] = "U1"
        original = copy.deepcopy(rows)
        with self.assertRaisesRegex(ValueError, "duplicate project-local reference"):
            MODULE.assign_references(rows, overrides)
        self.assertEqual(original, rows)
        # Two explicit rows must also not receive one appended reference.
        second = dict(rows[-2])
        second.update(instance="c5_service_candidate_logic_two",
                      instance_uid="LESHY2-UI-R2:c5_service_candidate_logic_two")
        rows.append(second)
        overrides["LESHY2-UI-R2"].update(c5_service_candidate_logic="U999",
                                          c5_service_candidate_logic_two="U999")
        with self.assertRaisesRegex(ValueError, "duplicate project-local reference"):
            MODULE.assign_references(rows, overrides)

    def test_reference_overrides_reject_stale_owner_prefix_zero_and_malformed_values(self):
        row = self.rows[0]
        project, instance, prefix = row["project"], row["instance"], row["reference_prefix"]
        for invalid in (f"{prefix}0", f"{prefix}01", f"{prefix}-1", f"{prefix}1.0",
                        f"{prefix.lower()}1", f" {prefix}1", f"{prefix}1\n", "U1A", "", 1, None):
            with self.subTest(reference=invalid), self.assertRaisesRegex(ValueError, "invalid explicit reference"):
                MODULE.assign_references(self.rows, {project: {instance: invalid}})
        wrong_prefix = "C" if prefix != "C" else "U"
        with self.assertRaisesRegex(ValueError, "prefix mismatch"):
            MODULE.assign_references(self.rows, {project: {instance: f"{wrong_prefix}999"}})
        with self.assertRaisesRegex(ValueError, "missing instance"):
            MODULE.assign_references(self.rows, {project: {"not_an_allocated_instance": "U999"}})
        with self.assertRaisesRegex(ValueError, "unknown project"):
            MODULE.assign_references(self.rows, {"LESHY2-UNKNOWN": {instance: f"{prefix}999"}})
        for invalid in (None, [], {project: []}):
            with self.subTest(overrides=invalid), self.assertRaises(ValueError):
                MODULE.assign_references(self.rows, invalid)
        with self.assertRaisesRegex(ValueError, "duplicate project-local instance"):
            MODULE.assign_references(self.rows + [dict(row)], {})

    def test_reference_override_failure_is_a_failed_build_not_an_admission(self):
        real_load = MODULE.load
        contract = copy.deepcopy(real_load(MODULE.CONTRACT))
        contract["reference_overrides"] = {"LESHY2-UI-R2": {"missing_instance": "U999"}}
        with mock.patch.object(MODULE, "load", side_effect=lambda path: (
            contract if path == MODULE.CONTRACT else real_load(path)
        )):
            result = MODULE.build()
        self.assertEqual("fail", result["status"])
        self.assertTrue(any("invalid reference allocation" in error for error in result["errors"]))
        self.assertEqual(1208, result["summary"]["fitted_board_instance_count"])
        self.assertEqual(self.ledger["authorization"], result["authorization"])


if __name__ == "__main__":
    unittest.main()
