import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_placement.py"
SVG = ROOT / "docs/images/h6-r2-exact-placement.svg"
KICAD_PYTHON = Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/"
    "Versions/3.9/bin/python3"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class H6R2PlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_exact_placement_closes_every_schematic_instance(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual(
            {
                "board_count": 2,
                "copper_layers_per_board": 6,
                "schematic_instance_count": 1208,
                "placed_instance_count": 1208,
                "hard_conflict_count": 0,
                "placement_failure_count": 0,
                "net_or_footprint_error_count": 0,
                "routing_authorized": False,
                "routing_started": False,
            },
            self.audit["summary"],
        )
        boards = {row["project"]: row for row in self.audit["boards"]}
        self.assertEqual(428, boards["LESHY2-UI-R2"]["placed_instance_count"])
        self.assertEqual(780, boards["LESHY2-RF-R2"]["placed_instance_count"])

    def test_native_board_hashes_and_six_layer_headers_match_the_audit(self):
        for board in self.audit["boards"]:
            path = ROOT / board["output"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(board["sha256"], sha256(path), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn('(0 "F.Cu" signal)', text)
            self.assertIn('(4 "In1.Cu" signal)', text)
            self.assertIn('(6 "In2.Cu" signal)', text)
            self.assertIn('(8 "In3.Cu" signal)', text)
            self.assertIn('(10 "In4.Cu" signal)', text)
            self.assertIn('(2 "B.Cu" signal)', text)
            self.assertEqual(
                board["placed_instance_count"],
                text.count('property "Leshy2Instance"'),
                "every schematic footprint must retain its exact hierarchy identity",
            )

    def test_user_critical_datums_are_exact_and_symmetric(self):
        expected_x = [14.0, 25.75, 37.5, 49.25, 61.0]
        for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            self.assertEqual(
                expected_x,
                [point[0] for point in self.contract["antenna_ports"][project].values()],
            )
            self.assertTrue(
                all(point[1] == 0.0 for point in self.contract["antenna_ports"][project].values())
            )
        display = self.contract["mechanical"]["display_bed"]
        self.assertEqual([9.23, 65.77], display["panel_bbox_mm"]["x"])
        self.assertEqual([19.0, 103.96], display["panel_bbox_mm"]["y"])
        self.assertEqual(5.0, display["minimum_relaxed_slack_mm"])
        self.assertEqual(
            [37.5, 35.4],
            self.contract["placement_overrides"]["display_connector"]["centre_mm"],
        )
        self.assertEqual(90.0, self.contract["placement_overrides"]["encoder"]["rotation_deg"])

    def test_factory_stack_candidate_is_the_current_1p6_mm_six_layer_stack(self):
        stack = self.contract["board"]["factory_stack_candidate"]
        self.assertEqual("JLCPCB", stack["manufacturer"])
        self.assertEqual("JLC06161H-3313", stack["official_stackup_id"])
        self.assertEqual(1.6, stack["order_thickness_mm"])
        self.assertEqual(1.54, stack["calculator_finished_thickness_mm"])
        self.assertEqual(10, stack["calculator_finished_thickness_tolerance_percent"])
        self.assertEqual(0.035, stack["outer_copper_mm"])
        self.assertEqual(0.0152, stack["inner_copper_mm"])
        self.assertEqual("3313 x1, 0.0994 mm nominal", stack["outer_prepreg"])
        self.assertEqual("2116 x1, 0.1088 mm nominal", stack["inner_prepreg"])
        self.assertEqual(0.55, stack["core_each_mm"])
        self.assertEqual("https://jlcpcb.com/pcb-impedance-calculator/", stack["source"])
        self.assertEqual("2026-09-03", stack["verified_at"])

    def test_generation_is_byte_reproducible_when_kicad_python_is_available(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        result = subprocess.run(
            [str(KICAD_PYTHON), str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("1208/1208 positions; 0 hard conflicts; 0 unplaced", result.stdout)

    def test_kicad_cli_parses_both_native_boards(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            for board in self.audit["boards"]:
                source = ROOT / board["output"]
                output = Path(directory) / f"{board['project']}.csv"
                result = subprocess.run(
                    [
                        cli,
                        "pcb",
                        "export",
                        "pos",
                        "--side",
                        "both",
                        "--format",
                        "csv",
                        "--units",
                        "mm",
                        "-o",
                        str(output),
                        str(source),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertEqual(0, result.returncode, result.stdout)
                self.assertTrue(output.is_file(), board["project"])

    def test_preview_is_current_and_states_that_routing_has_not_started(self):
        self.assertTrue(SVG.is_file())
        text = SVG.read_text(encoding="utf-8")
        self.assertIn("H6.0.1 exact-footprint placement", text)
        self.assertIn("routing not started", text)
        self.assertIn("428 positions", text)
        self.assertIn("780 positions", text)


if __name__ == "__main__":
    unittest.main()
