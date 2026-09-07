"""Reject the historical supply-net alias that isolated S3 and C5 power pins."""

import json
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = "LESHY2-UI-R2"
CANONICAL_SUPPLY = "3V3_MAIN"
NATIVE_SUPPLY = "/UI_10_S3_DISPLAY_TOUCH/3V3_MAIN"
EXPECTED_PINS = {
    "s3.3V3": ("U1", "2"),
    "c5.3V3": ("U14", "2"),
    "s3_supply_bypass.END_1": ("C6", "1"),
}


class H2R2ModulePowerTests(unittest.TestCase):
    def test_module_and_bypass_supply_pins_use_the_exact_canonical_rail(self):
        ledger = json.loads(
            (ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json")
            .read_text(encoding="utf-8")
        )["rows"]
        for endpoint, (reference, pin) in EXPECTED_PINS.items():
            with self.subTest(endpoint=endpoint):
                matches = [row for row in ledger if row["endpoint"] == endpoint]
                self.assertEqual(1, len(matches))
                row = matches[0]
                self.assertEqual(PROJECT, row["project"])
                self.assertEqual(reference, row["reference"])
                self.assertEqual(pin, row["physical"])
                self.assertEqual("connected", row["disposition"])
                # Do not strip a path or take its basename: the historical
                # /UI_10_S3_CORE_MEMORY_BOOT/3V3_MAIN is a different net.
                self.assertEqual(CANONICAL_SUPPLY, row["net"])

    def test_exported_native_netlist_connects_all_three_pins_to_the_current_rail(self):
        cli = shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("kicad-cli is not installed")

        work = ROOT / "work"
        work.mkdir(exist_ok=True)
        schematic = ROOT / "hardware/ecad/kicad" / PROJECT / f"{PROJECT}.kicad_sch"
        with tempfile.TemporaryDirectory(prefix="h2-module-power-", dir=work) as directory:
            output = Path(directory) / "module-power.xml"
            result = subprocess.run(
                [
                    cli, "sch", "export", "netlist", "--format", "kicadxml",
                    "-o", str(output), str(schematic),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            netlist = ET.parse(output).getroot()

        # Inspect the KiCad export, not a constructed net name derived from
        # the ledger. Exact comparison rejects both a separate historical
        # net and the escaped {slash} alias seen in the faulty native board.
        net_membership = {}
        for net in netlist.findall("./nets/net"):
            for node in net.findall("node"):
                endpoint = (node.get("ref"), node.get("pin"))
                net_membership.setdefault(endpoint, []).append(net.get("name"))
        for reference_pin in EXPECTED_PINS.values():
            with self.subTest(reference_pin=reference_pin):
                self.assertEqual([NATIVE_SUPPLY], net_membership.get(reference_pin))


if __name__ == "__main__":
    unittest.main()
