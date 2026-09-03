import json
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from hardware.ecad.h2_r2_native_kicad import kicad_net_name


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_native_kicad.py"
CONTRACT = ROOT / "hardware/ecad/h2-r2-native-kicad-contract.json"
MANIFEST = ROOT / "hardware/ecad/generated/H2-R2-native-kicad-projects.json"
PROJECT_ROOT = ROOT / "hardware/ecad/kicad"
INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
SYMBOLS = ROOT / "hardware/ecad/generated/H2-R2-controlled-symbol-library.json"
NETS = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"


class H2R2NativeKiCadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.instances = json.loads(INSTANCES.read_text(encoding="utf-8"))["rows"]
        cls.symbols = {
            row["device_id"]: row
            for row in json.loads(SYMBOLS.read_text(encoding="utf-8"))["symbols"]
        }
        cls.nets = json.loads(NETS.read_text(encoding="utf-8"))["rows"]

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("2 native projects, 22 sheets, 1208 symbols, 4306 pins", result.stdout)

    def test_exact_project_sheet_instance_and_pin_totals_close(self):
        self.assertEqual("pass", self.manifest["status"])
        self.assertEqual([], self.manifest["errors"])
        summary = self.manifest["summary"]
        self.assertEqual(2, summary["project_count"])
        self.assertEqual(22, summary["project_graph_sheet_count"])
        self.assertEqual(18, summary["populated_sheet_count"])
        self.assertEqual(1208, summary["fitted_symbol_instance_count"])
        self.assertEqual(4306, summary["physical_symbol_pin_count"])
        self.assertEqual(4068, summary["connected_physical_pin_count"])
        self.assertEqual(238, summary["explicit_no_connect_physical_pin_count"])
        self.assertEqual(5, summary["external_module_interface_annotation_count"])
        self.assertEqual(789, summary["canonical_net_count"])

    def test_every_controlled_physical_pin_has_one_connected_or_nc_target(self):
        rows_by_instance = {}
        for row in self.nets:
            rows_by_instance.setdefault(row["instance"], []).append(row)
        physical = connected = no_connect = 0
        for instance in self.instances:
            logical_rows = rows_by_instance[instance["instance"]]
            for pin in self.symbols[instance["device_id"]]["pin_map"]:
                candidates = [
                    row for row in logical_rows if row["contact"] in pin["contacts"]
                ]
                self.assertTrue(candidates, f"{instance['instance']}.{pin['number']}")
                targets = {(row["disposition"], row.get("net")) for row in candidates}
                self.assertEqual(1, len(targets), f"{instance['instance']}.{pin['number']}")
                disposition, net = next(iter(targets))
                physical += 1
                if disposition == "connected":
                    connected += 1
                    self.assertTrue(net)
                else:
                    no_connect += 1
                    self.assertEqual("no_connect", disposition)
                    self.assertIsNone(net)
        self.assertEqual((4306, 4068, 238), (physical, connected, no_connect))

    def test_module_receptacles_are_annotations_not_false_pcb_pins(self):
        external = [
            item
            for sheet in self.manifest["sheets"]
            for item in sheet["external_module_interfaces"]
        ]
        self.assertEqual(
            {
                "s3.ANT",
                "c5.ANT1",
                "nrf0.ANT",
                "nrf1.ANT",
                "nrf2.ANT",
            },
            {item["endpoint"] for item in external},
        )
        self.assertTrue(all("no Leshy2 PCB pad" in item["representation"] for item in external))

    def test_two_schematic_projects_are_complete_and_h2_manifest_stops_before_pcb(self):
        expected = {
            "LESHY2-UI-R2": (9, 428),
            "LESHY2-RF-R2": (13, 780),
        }
        actual = {row["id"]: (row["sheet_count"], row["instance_count"]) for row in self.manifest["projects"]}
        self.assertEqual(expected, actual)
        for project_id in expected:
            directory = PROJECT_ROOT / project_id
            self.assertTrue((directory / f"{project_id}.kicad_pro").is_file())
            self.assertTrue((directory / f"{project_id}.kicad_sch").is_file())
            self.assertTrue((directory / "sym-lib-table").is_file())
            self.assertTrue((directory / "fp-lib-table").is_file())
            # H2 itself did not authorize PCB generation. A later H6 board may
            # now live beside the reviewed schematic without rewriting that
            # historical phase boundary.
        self.assertEqual(0, self.manifest["summary"]["pcb_file_count"])

    def test_native_projects_preserve_production_board_rules(self):
        for project_id in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            project = json.loads(
                (PROJECT_ROOT / project_id / f"{project_id}.kicad_pro").read_text(
                    encoding="utf-8"
                )
            )
            rules = project["board"]["design_settings"]["rules"]
            self.assertEqual(0.15, rules["min_clearance"])
            self.assertEqual(0.20, rules["min_copper_edge_clearance"])
            self.assertEqual(0.20, rules["min_through_hole_diameter"])
            self.assertEqual(0.40, rules["min_via_diameter"])
            self.assertEqual(0.20, project["net_settings"]["classes"][0]["via_drill"])

    def test_usb_physical_labels_are_native_kicad_pairs(self):
        self.assertEqual("S3_USB_P", kicad_net_name("S3_USB_DP"))
        self.assertEqual("S3_USB_N", kicad_net_name("S3_USB_DM"))
        self.assertEqual(
            "C5_SERVICE_USB_CONNECTOR_P",
            kicad_net_name("C5_SERVICE_USB_DP_CONNECTOR"),
        )
        self.assertEqual(
            "C5_SERVICE_USB_CONNECTOR_N",
            kicad_net_name("C5_SERVICE_USB_DM_CONNECTOR"),
        )
        self.assertEqual("LCD_DB0", kicad_net_name("LCD_DB0"))

    def test_project_local_references_remain_unique(self):
        counts = Counter((row["project"], row["reference"]) for row in self.instances)
        self.assertFalse([key for key, count in counts.items() if count != 1])

    def test_authorization_stops_before_pcb_fabrication_or_order(self):
        self.assertEqual(
            {
                "native_kicad_project_creation": True,
                "native_schematic_symbols_and_nets": True,
                "pcb_placement_or_routing": False,
                "fabrication": False,
                "ordering": False,
            },
            self.manifest["authorization"],
        )
        source_paths = {row["path"] for row in self.manifest["sources"].values()}
        self.assertTrue(all("H2-instance-ledger" not in path for path in source_paths))
        self.assertTrue(all("LESHY2-UI/" not in path and "LESHY2-RF/" not in path for path in source_paths))

    def test_kicad_parses_all_roots_and_exports_exact_components(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is not installed")
        expected = {row["id"]: row["instance_count"] for row in self.manifest["projects"]}
        with tempfile.TemporaryDirectory() as directory:
            for project_id, component_count in expected.items():
                output = Path(directory) / f"{project_id}.xml"
                schematic = PROJECT_ROOT / project_id / f"{project_id}.kicad_sch"
                result = subprocess.run(
                    [cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(output), str(schematic)],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertEqual(0, result.returncode, result.stdout)
                tree = ET.parse(output)
                components = tree.getroot().findall("./components/comp")
                self.assertEqual(component_count, len(components), project_id)
                self.assertEqual(component_count, len({row.get("ref") for row in components}), project_id)

    def test_kicad_native_erc_is_empty_for_both_roots(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is not installed")
        with tempfile.TemporaryDirectory() as directory:
            for project in self.manifest["projects"]:
                project_id = project["id"]
                report = Path(directory) / f"{project_id}-erc.json"
                schematic = PROJECT_ROOT / project_id / f"{project_id}.kicad_sch"
                result = subprocess.run(
                    [
                        cli, "sch", "erc", "--format", "json", "--severity-all",
                        "--exit-code-violations", "-o", str(report), str(schematic),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertEqual(0, result.returncode, result.stdout)
                erc = json.loads(report.read_text(encoding="utf-8"))
                violations = [
                    violation
                    for sheet in erc.get("sheets", [])
                    for violation in sheet.get("violations", [])
                ]
                self.assertEqual([], violations, project_id)


if __name__ == "__main__":
    unittest.main()
