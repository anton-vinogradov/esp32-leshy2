"""Exact C5 USB/SDIO common-pair naming, without changing logical endpoints."""

from collections import Counter
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from hardware.ecad.h2_r2_native_kicad import (
    USB_SHARED_NATIVE_ALIASES,
    kicad_net_name,
    parenthesis_delta,
)
from hardware.layout import h6_r2_kicad_net_bindings as bindings


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "hardware/ecad/kicad/LESHY2-UI-R2"
PREFIX = "/UI_20_C5_WIFI_IR_SERVICE/"
EXPECTED_ALIASES = {
    "C5_GPIO13_COMMON": "C5_USB_SDIO_COMMON_N",
    "C5_GPIO14_COMMON": "C5_USB_SDIO_COMMON_P",
}
EXPECTED_PADS = {
    ("U14", "13"): PREFIX + "C5_USB_SDIO_COMMON_N",
    ("U14", "14"): PREFIX + "C5_USB_SDIO_COMMON_P",
    ("U22", "4"): PREFIX + "C5_USB_SDIO_COMMON_N",
    ("U22", "3"): PREFIX + "C5_USB_SDIO_COMMON_P",
}


def block_at(lines, start):
    depth = 0
    block = []
    for line in lines[start:]:
        block.append(line)
        depth += parenthesis_delta(line)
        if depth == 0:
            return "\n".join(block)
    raise ValueError("unterminated native form")


def c5_native_pads(text):
    result = {}
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith('\t(footprint '):
            continue
        footprint = block_at(lines, index)
        reference = re.search(r'\(property "Reference" "([^"\\]+)"', footprint)
        if not reference or reference[1] not in {"U14", "U22"}:
            continue
        fp_lines = footprint.splitlines()
        for pad_index, pad_line in enumerate(fp_lines):
            match = re.match(r'\t\t\(pad "([^"\\]+)" ', pad_line)
            if not match or (reference[1], match[1]) not in EXPECTED_PADS:
                continue
            pad = block_at(fp_lines, pad_index)
            net = re.search(r'\(net "([^"\\]+)"\)', pad)
            key = (reference[1], match[1])
            if key in result or net is None:
                raise ValueError("missing net or duplicate C5 common pad")
            result[key] = net[1]
    return result


class C5CommonUsbAliasTests(unittest.TestCase):
    def test_only_the_two_exact_common_names_are_aliased(self):
        self.assertEqual(EXPECTED_ALIASES, USB_SHARED_NATIVE_ALIASES)
        for canonical, native in EXPECTED_ALIASES.items():
            self.assertEqual(native, kicad_net_name(canonical))
        for untouched in (
            "C5_GPIO12_COMMON", "C5_GPIO13_COMMON_EXTRA", "C5_GPIO14",
            "C5_SDIO_DAT2", "HUB_C5_SDIO_DAT3_BRANCH", "LCD_DB0",
        ):
            self.assertEqual(untouched, kicad_net_name(untouched))

    def test_native_names_are_an_injective_pair_with_correct_polarity(self):
        self.assertEqual("C5_USB_SDIO_COMMON", kicad_net_name("C5_GPIO13_COMMON")[:-2])
        self.assertEqual("_N", kicad_net_name("C5_GPIO13_COMMON")[-2:])
        self.assertEqual("C5_USB_SDIO_COMMON", kicad_net_name("C5_GPIO14_COMMON")[:-2])
        self.assertEqual("_P", kicad_net_name("C5_GPIO14_COMMON")[-2:])
        rows = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())["rows"]
        canonical = {row["net"] for row in rows if row["disposition"] == "connected"}
        self.assertEqual(len(canonical), len({kicad_net_name(name) for name in canonical}))

    def test_canonical_four_endpoint_membership_stays_exact(self):
        rows = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())["rows"]
        actual = {(row["endpoint"], row["reference"], row["physical"], row["net"])
                  for row in rows if row.get("net") in EXPECTED_ALIASES}
        self.assertEqual({
            ("c5.GPIO13", "U14", "13", "C5_GPIO13_COMMON"),
            ("c5.GPIO14", "U14", "14", "C5_GPIO14_COMMON"),
            ("c5_service_usb_switch.D_MINUS", "U22", "4", "C5_GPIO13_COMMON"),
            ("c5_service_usb_switch.D_PLUS", "U22", "3", "C5_GPIO14_COMMON"),
        }, actual)

    def test_child_schematic_contains_two_labels_of_each_native_polarity(self):
        text = (PROJECT / "UI_20_C5_WIFI_IR_SERVICE.kicad_sch").read_text()
        labels = Counter(re.findall(r'\(label "([^"\\]+)"', text))
        for canonical, native in EXPECTED_ALIASES.items():
            self.assertEqual(0, labels[canonical])
            self.assertEqual(2, labels[native])

    def test_native_pad_nets_match_module_and_mux_polarity(self):
        text = (PROJECT / "LESHY2-UI-R2.kicad_pcb").read_text()
        self.assertEqual(EXPECTED_PADS, c5_native_pads(text))
        for old in EXPECTED_ALIASES:
            self.assertNotIn(PREFIX + old, text)
        for native in EXPECTED_ALIASES.values():
            self.assertEqual(2, text.count(f'(net "{PREFIX + native}")'))

    def test_swapped_or_unsuffixed_native_pad_names_are_detected(self):
        text = (PROJECT / "LESHY2-UI-R2.kicad_pcb").read_text()
        for bad in ("C5_USB_SDIO_COMMON_P", "C5_GPIO13_COMMON"):
            with self.subTest(bad=bad):
                mutated = text.replace('"' + PREFIX + 'C5_USB_SDIO_COMMON_N"',
                                       '"' + PREFIX + bad + '"', 1)
                self.assertNotEqual(EXPECTED_PADS, c5_native_pads(mutated))

    def test_current_xml_bindings_are_fresh_and_use_the_same_native_pair(self):
        self.assertEqual([], bindings.check())
        current = json.loads(bindings.OUTPUT.read_text())
        native = current["projects"]["LESHY2-UI-R2"]["canonical_to_kicad"]
        for canonical, alias in EXPECTED_ALIASES.items():
            self.assertEqual(PREFIX + alias, native[canonical])


class NetBindingChildFreshnessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        projects = {project: self.root / project / f"{project}.kicad_sch"
                    for project in ("LESHY2-UI-R2", "LESHY2-RF-R2")}
        schematics = []
        for project, root in projects.items():
            root.parent.mkdir()
            child = root.with_name("child.kicad_sch")
            for path in (root, child):
                path.write_text(f"(kicad_sch {path.name})\n")
                schematics.append(path)
            root.write_text('(kicad_sch (sheet (property "Sheetfile" "child.kicad_sch")))\n')
        self.child = schematics[1]
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({
            "status": "pass", "generated_files": [
                {"path": str(path.relative_to(self.root)), "sha256": bindings.sha256(path)}
                for path in schematics
            ],
        }))
        self.output = self.root / "bindings.json"
        paths = {key: self.root / f"{key}.json"
                 for key in ("INSTANCE_PATH", "NET_PATH", "SYMBOL_PATH")}
        for path in paths.values():
            path.write_text("{}\n")
        patcher = patch.multiple(bindings, ROOT=self.root, PROJECTS=projects,
                                 NATIVE_MANIFEST_PATH=self.manifest,
                                 OUTPUT=self.output, **paths)
        patcher.start()
        self.addCleanup(patcher.stop)
        logical = patch.object(bindings, "logical_pin_map", return_value=({}, set()))
        logical.start()
        self.addCleanup(logical.stop)
        self.output.write_text(json.dumps({
            "status": "pass", "marker": "H6.0.3-R1",
            "source_hashes": {str(path.relative_to(self.root)): bindings.sha256(path)
                              for path in bindings.source_paths()},
            "projects": {project: {"canonical_to_kicad": {}} for project in projects},
        }))

    def test_complete_current_child_hashes_pass(self):
        self.assertEqual([], bindings.check())

    def test_child_drift_fails_even_if_manifest_is_not_regenerated(self):
        before = self.manifest.read_bytes()
        self.child.write_text('(kicad_sch (label "WRONG"))\n')
        errors = bindings.check()
        self.assertEqual(before, self.manifest.read_bytes())
        self.assertTrue(any("native schematic manifest drift:" in error for error in errors), errors)

    def test_omitting_a_child_hash_is_not_a_freshness_waiver(self):
        artifact = json.loads(self.output.read_text())
        del artifact["source_hashes"][str(self.child.relative_to(self.root))]
        self.output.write_text(json.dumps(artifact))
        self.assertIn("binding source inventory does not cover the current native schematics",
                      bindings.check())

    def test_regenerated_manifest_does_not_restamp_old_bindings(self):
        self.child.write_text('(kicad_sch (label "CHANGED"))\n')
        manifest = json.loads(self.manifest.read_text())
        for row in manifest["generated_files"]:
            if row["path"] == str(self.child.relative_to(self.root)):
                row["sha256"] = bindings.sha256(self.child)
        self.manifest.write_text(json.dumps(manifest))
        self.assertTrue(any(error.startswith("source drift:") for error in bindings.check()))

    def test_omitted_child_manifest_entry_is_rejected(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["generated_files"] = [row for row in manifest["generated_files"]
                                       if row["path"] != str(self.child.relative_to(self.root))]
        self.manifest.write_text(json.dumps(manifest))
        self.assertIn("native schematic manifest inventory differs from actual project children",
                      bindings.check())

    def test_duplicate_child_manifest_entry_is_rejected(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["generated_files"].append(dict(manifest["generated_files"][1]))
        self.manifest.write_text(json.dumps(manifest))
        self.assertIn("duplicate native schematic manifest entry", bindings.check())

    def test_referenced_child_deleted_and_removed_from_manifest_is_rejected(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["generated_files"] = [row for row in manifest["generated_files"]
                                       if row["path"] != str(self.child.relative_to(self.root))]
        self.manifest.write_text(json.dumps(manifest))
        self.child.unlink()
        self.assertTrue(any("missing native schematic child:" in error
                            for error in bindings.check()))


if __name__ == "__main__":
    unittest.main()
