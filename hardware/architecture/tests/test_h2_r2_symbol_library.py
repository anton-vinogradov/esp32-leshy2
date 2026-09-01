import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_symbol_library.py"
LIBRARY = ROOT / "hardware/ecad/libraries/leshy2_r2.kicad_sym"
MANIFEST = ROOT / "hardware/ecad/generated/H2-R2-controlled-symbol-library.json"


class H2R2SymbolLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.symbols = {row["device_id"]: row for row in cls.manifest["symbols"]}

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("232 controlled R2 symbols", result.stdout)

    def test_library_boundary_is_complete_and_pre_net(self):
        self.assertEqual("pass", self.manifest["status"])
        self.assertEqual([], self.manifest["errors"])
        library = self.manifest["library"]
        self.assertEqual("Leshy2_R2", library["id"])
        self.assertEqual(232, library["symbol_count"])
        self.assertEqual(1532, library["pin_count"])
        self.assertEqual(3, library["external_interface_metadata_count"])
        self.assertTrue(self.manifest["authorization"]["controlled_symbol_library"])
        self.assertFalse(self.manifest["authorization"]["native_schematic_nets"])

    def test_every_pin_number_is_unique_and_matches_one_footprint_pad(self):
        for symbol in self.manifest["symbols"]:
            numbers = [pin["number"] for pin in symbol["pin_map"]]
            self.assertEqual(len(numbers), len(set(numbers)), symbol["device_id"])
            self.assertTrue(all(pin["contacts"] for pin in symbol["pin_map"]))

    def test_shared_switch_contact_is_one_aliased_pad_pin(self):
        switch = self.symbols["alps_skrtlae010"]
        pad1 = next(pin for pin in switch["pin_map"] if pin["number"] == "1")
        self.assertEqual("C1/C2", pad1["name"])
        self.assertEqual(["C1", "C2"], pad1["contacts"])
        self.assertEqual(2, switch["pin_count"])

    def test_on_module_receptacles_are_metadata_not_false_pins(self):
        expected = {
            "ebyte_e01_ml01sp4": ["ANT"],
            "esp32_c5_wroom_1u_n8r8": ["ANT1"],
            "esp32_s3_wroom_1u_n16r8": ["ANT"],
        }
        actual = {
            device_id: symbol["external_interfaces"]
            for device_id, symbol in self.symbols.items()
            if symbol["external_interfaces"]
        }
        self.assertEqual(expected, actual)
        for device_id, names in expected.items():
            pin_names = {pin["name"] for pin in self.symbols[device_id]["pin_map"]}
            self.assertTrue(set(names).isdisjoint(pin_names))

    def test_nc_roles_generate_no_connect_pins(self):
        c5 = self.symbols["esp32_c5_wroom_1u_n8r8"]
        for number in ("19", "20", "22"):
            pin = next(row for row in c5["pin_map"] if row["number"] == number)
            self.assertEqual("no_connect", pin["type"])

    def test_kicad_can_parse_and_resave_library_when_cli_is_available(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is not installed")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "validated.kicad_sym"
            result = subprocess.run(
                [cli, "sym", "upgrade", "--force", "--output", str(output), str(LIBRARY)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
