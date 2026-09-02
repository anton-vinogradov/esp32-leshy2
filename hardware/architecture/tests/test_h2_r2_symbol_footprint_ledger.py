import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_symbol_footprint_ledger.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"
DEVICES = ROOT / "hardware/architecture/devices.json"


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class H2R2SymbolFootprintLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(OUTPUT.read_text(encoding="utf-8"))
        cls.devices = json.loads(DEVICES.read_text(encoding="utf-8"))["devices"]

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("245 board groups", result.stdout)

    def test_exact_group_boundary_is_complete(self):
        self.assertEqual("H2-R2.1.2", self.ledger["marker"])
        self.assertEqual("pass", self.ledger["status"])
        summary = self.ledger["summary"]
        self.assertEqual(251, summary["component_group_count"])
        self.assertEqual(245, summary["board_component_group_count"])
        self.assertEqual(6, summary["explicit_non_pcba_group_count"])
        self.assertEqual(245, summary["symbol_identity_count"])
        self.assertEqual(245, summary["footprint_identity_count"])
        self.assertEqual(1617, summary["logical_contact_count"])
        self.assertEqual(0, summary["unresolved_groups"])

    def test_contacts_are_hash_bound_to_current_device_evidence(self):
        for row in self.ledger["groups"]:
            contacts = self.devices[row["device_id"]].get("contacts", {})
            self.assertEqual(contacts, row["contact_map"], row["device_id"])
            self.assertEqual(
                canonical_sha256(contacts), row["contact_map_sha256"], row["device_id"]
            )
            if row["symbol_id"]:
                self.assertTrue(contacts, row["device_id"])

    def test_every_board_group_has_one_symbol_and_footprint_identity(self):
        board = [row for row in self.ledger["groups"] if row["symbol_id"]]
        self.assertEqual(len(board), len({row["symbol_id"] for row in board}))
        self.assertTrue(all(row["symbol_id"].startswith("Leshy2_R2:") for row in board))
        self.assertTrue(all(row["footprint"] for row in board))
        self.assertTrue(all(row["native_sheet_affinity"] for row in board))

    def test_off_board_groups_have_no_false_pcb_footprint(self):
        external = {
            row["device_id"]: row
            for row in self.ledger["groups"]
            if not row["symbol_id"]
        }
        self.assertEqual(
            {
                "davies_1227_j",
                "eastrising_er_tft035ips_6_ctp",
                "m5_u214",
                "te_1_2118651_0",
                "te_2118651_2",
                "xtar_18650_4000mah_protected",
            },
            set(external),
        )
        self.assertTrue(all(row["footprint"] is None for row in external.values()))
        self.assertIn("off-board U.FL-to-U.FL", external["te_2118651_2"]["ecad_disposition"])
        self.assertIn("off-board U.FL-to-U.FL", external["te_1_2118651_0"]["ecad_disposition"])

    def test_historical_package_hints_never_become_topology_authority(self):
        self.assertTrue(self.ledger["historical_hint_sources"])
        self.assertTrue(
            all(source["authority"] is False for source in self.ledger["historical_hint_sources"])
        )
        for row in self.ledger["groups"]:
            self.assertTrue(
                all(not sheet.startswith(("LESHY2-UI", "LESHY2-RF")) for sheet in row["native_sheet_affinity"]),
                row["device_id"],
            )
        self.assertEqual(5, self.ledger["summary"]["historical_package_conflicts_resolved"])

    def test_all_new_local_geometries_are_materialized(self):
        materialized = [
            row for row in self.ledger["groups"]
            if row["footprint_definition"]
            and row["footprint_definition"]["status"] == "current_exact_local_definition_materialized"
        ]
        self.assertEqual(7, len(materialized))
        self.assertEqual(
            {
                "hirose_fh34srj_50s_0_5sh_50",
                "coilcraft_wbc1_1tlc",
                "coilcraft_wbc16_1tlc",
                "prodtech_pspmaa0605h_2r2m_anp",
                "ti_tps566231p_rqfr",
                "leshy2_nfc_pickup_loop_r2",
                "leshy2_pcb_testpoint_pad_1mm_r2",
            },
            {row["device_id"] for row in materialized},
        )
        self.assertIn(
            "Leshy2_R2:FH34SRJ-50S-0.5SH-50",
            {row["footprint"] for row in materialized},
        )
        self.assertEqual(7, self.ledger["summary"]["new_exact_footprint_geometries_materialized"])

    def test_authorization_remains_net_and_kicad_free(self):
        self.assertEqual([], self.ledger["errors"])
        self.assertEqual(0, self.ledger["summary"]["schematic_symbols_or_footprint_files_created"])
        self.assertEqual(0, self.ledger["summary"]["native_schematic_nets_created"])
        auth = self.ledger["authorization"]
        self.assertTrue(auth["exact_group_ledger"])
        for key in (
            "symbol_or_footprint_files",
            "schematic_nets",
            "kicad_project_creation",
            "pcb_placement_or_routing",
            "fabrication",
            "ordering",
        ):
            self.assertFalse(auth[key])


if __name__ == "__main__":
    unittest.main()
