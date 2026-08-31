import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_native_inventory.py"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-inventory.json"


def load_module():
    spec = importlib.util.spec_from_file_location("h2_r2_native_inventory", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class H2R2NativeInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.actual = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_generated_inventory_is_current_and_clean(self):
        self.assertEqual(self.module.build(), self.actual)
        self.assertEqual("pass", self.actual["status"])
        self.assertEqual([], self.actual["errors"])

    def test_native_project_graph_has_no_historical_cap_board(self):
        self.assertEqual(
            ["LESHY2-UI-R2", "LESHY2-RF-R2", "L2-DISP-ADP-001-B"],
            [row["id"] for row in self.actual["projects"]],
        )
        self.assertEqual(23, self.actual["summary"]["sheet_count"])
        self.assertNotIn(
            "LESHY2-LORA-CAP-01",
            {row["id"] for row in self.actual["projects"]},
        )

    def test_all_six_domains_have_one_native_owner(self):
        owners = []
        for project in self.actual["projects"]:
            for sheet in project["sheets"]:
                if sheet.get("domain_owner"):
                    owners.append(sheet["domain_owner"])
                owners.extend(sheet.get("domain_owners", []))
        self.assertCountEqual(
            ["s3", "c5", "hub_rp", "rf_rp", "pack", "safety"], owners
        )

    def test_exact_component_group_and_pack_delta_are_frozen(self):
        self.assertEqual(239, self.actual["summary"]["component_group_count"])
        self.assertEqual(1195, self.actual["summary"]["component_quantity_per_product"])
        groups = {row["device_id"]: row for row in self.actual["component_groups"]}
        self.assertEqual("TCA9803DGKR", groups["ti_tca9803_dgkr"]["mpn"])
        self.assertEqual("C2687966", groups["ti_tca9803_dgkr"]["jlcpcb_part_number"])
        self.assertEqual(25, groups["uniroyal_0402wgf2201tce"]["quantity_per_product"])
        self.assertEqual(7, groups["samsung_cl05a105ka5nqnc"]["quantity_per_product"])
        self.assertEqual(2, groups["samsung_cl05b104ko5nnnc"]["quantity_per_product"])

    def test_inventory_does_not_claim_schematic_or_order_authority(self):
        auth = self.actual["authorization"]
        self.assertTrue(auth["native_source_and_sheet_inventory"])
        for key in (
            "schematic_symbols_or_nets",
            "kicad_project_creation",
            "pcb_placement_or_routing",
            "fabrication",
            "ordering",
        ):
            self.assertFalse(auth[key])
        self.assertEqual(0, self.actual["summary"]["native_schematic_symbols_created"])
        self.assertEqual(0, self.actual["summary"]["native_schematic_nets_created"])

    def test_cli_check_is_reproducible(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("239 exact component groups", result.stdout)


if __name__ == "__main__":
    unittest.main()
