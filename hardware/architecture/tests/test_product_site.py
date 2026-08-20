import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class ProductSiteTests(unittest.TestCase):
    PUBLIC_PAGES = (
        "README.md",
        "README.ru.md",
        "docs/hardware.md",
        "docs/hardware.ru.md",
        "docs/antennas.md",
        "docs/antennas.ru.md",
        "docs/schematics.md",
        "docs/schematics.ru.md",
        "docs/interconnect.md",
        "docs/interconnect.ru.md",
        "docs/pinout.md",
        "docs/pinout.ru.md",
        "docs/memory.md",
        "docs/memory.ru.md",
        "docs/safety.md",
        "docs/safety.ru.md",
    )

    def read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_public_site_contains_only_product_pages(self):
        docs_markdown = {
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.glob("docs/**/*.md")
        }
        self.assertEqual(set(self.PUBLIC_PAGES[2:]), docs_markdown)

        for name in self.PUBLIC_PAGES:
            page = self.read(name)
            for forbidden in (
                "DEC-", "FND-", "REV-", "IMP-", "docs/review",
                "docs/status", "docs/stages", "проведено ревью",
            ):
                self.assertNotIn(forbidden, page, f"{name}: {forbidden}")

    def test_all_local_public_links_exist(self):
        for name in self.PUBLIC_PAGES:
            page_path = REPO_ROOT / name
            page = page_path.read_text(encoding="utf-8")
            for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", page):
                if target.startswith(("http://", "https://", "#")):
                    continue
                resolved = (page_path.parent / re.split(r"[?#]", target, maxsplit=1)[0]).resolve()
                self.assertTrue(resolved.exists(), f"{name}: missing {target}")

    def test_s3_memory_and_boot_contract_is_public(self):
        for name in ("docs/memory.md", "docs/memory.ru.md"):
            page = self.read(name)
            for token in (
                "ESP32-S3-WROOM-1U-N16R8", "16", "8", "GPIO0",
                "GPIO18", "GPIO45", "GPIO46", "ECC", "BOOT",
                "CONFIG_SPIRAM_ECC_ENABLE=y", "0x780000", "self-test",
            ):
                self.assertIn(token, page, f"{name}: {token}")
            self.assertRegex(page, r"7[.,]5")

    def test_all_in_one_update_and_open_recovery_are_public(self):
        expected = {
            "docs/safety.md": (
                "one bundle", "owner/release-signed manifest", "RUN=KILL",
                "12 seconds", "16.7-second TBYB", "MSPM0C1106SDGS20R",
                "16-KiB", "22-KiB", "UART1", "not enabled by default",
            ),
            "docs/safety.ru.md": (
                "один bundle", "owner/release-signed manifest", "RUN=KILL",
                "12 секундам", "16,7 с", "MSPM0C1106SDGS20R",
                "16 КиБ", "22 КиБ", "UART1", "не включается по умолчанию",
            ),
        }
        for name, tokens in expected.items():
            page = " ".join(self.read(name).split())
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_layout_is_product_facing(self):
        layout = self.read("docs/images/current-clamshell.svg")
        for token in (
            "Leshy2 — dimensioned external layout",
            "Text outside component outlines is intended PCB silkscreen",
            'data-layer="pcb-silkscreen"',
            "HMX035CTFT-001",
            "M5Stack U214",
            "SSW-107-02-S-D",
            "insert ⊗ · remove ⊙",
            "Keystone 1048P",
            'data-part="single-D-pad-cross"',
            "RUN",
            "KILL",
            "PTT",
            "physical actual-TX evidence for each transmitting path",
            "form one front line below the display",
            "M2.5 hole/head keep-outs",
            'id="front-outer-rf-bank" data-mount-face="ui-pcb-outer"',
            'id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer"',
            "both RF connector banks mount on the outward PCB faces",
            "GCT RFPC-SMA31-FN-175-A",
            "GCT RFPC-SMA32-FN-175-A",
            "WI-FI/BLE",
            "2.4 GHz RP-SMA",
            "WI-FI/15.4",
            "2.4/5 GHz RP-SMA",
            "nRF24-1",
            "2.4 GHz SMA",
            "SUB-GHz",
            "VHF/UHF",
            "TX ACTIVE",
            "HEADPHONES",
            "LINE OUT",
            "C5 SERVICE USB",
            "MICROPHONE",
            "SPEAKER / GRILLE",
            'data-interface-kind="acoustic-opening"',
            "microSD",
            "SPEAKER",
            "GRILLE",
            "POWER",
            "USB / POWER",
            "RP SERVICE USB",
            "M5 UNIT",
        ):
            self.assertIn(token, layout)
        for process_token in ("G3-0001", "not G7", "not KiCad", "Working projection"):
            self.assertNotIn(process_token, layout)
        self.assertIn(
            'data-instance="ptt_switch" data-direct-press="true"', layout
        )
        self.assertIn('data-manufacturing-class="custom-actuator"', layout)
        self.assertIn("supplier MPN does not apply", layout)
        self.assertIn('data-instance="encoder_knob" data-selected-part="true"', layout)
        self.assertIn("Davies 1227-J is the exact encoder knob", layout)
        self.assertNotIn("STOP actuator", layout)
        self.assertNotIn("RE-ARM", layout)

    def test_antenna_kit_is_product_facing_and_machine_accounted(self):
        import json

        manifest = json.loads(
            (REPO_ROOT / "hardware/architecture/antenna-kit.json").read_text(
                encoding="utf-8"
            )
        )
        candidate = json.loads(
            (REPO_ROOT / "hardware/architecture/candidates/G2F-3I.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(12, manifest["physical_item_count"])
        self.assertEqual(12, manifest["exact_target_item_count"])
        self.assertEqual(12, manifest["paper_alternate_item_count"])
        self.assertEqual(11, manifest["supply_independent_alternate_item_count"])
        self.assertEqual(0, manifest["hil_qualified_alternate_item_count"])
        self.assertEqual(12, sum(item["quantity"] for item in manifest["items"]))
        self.assertEqual(12, sum("alternate" in item for item in manifest["items"]))
        self.assertEqual(
            11,
            sum(
                item["alternate"]["manufacturer_independent_from_first_target"]
                for item in manifest["items"]
            ),
        )
        self.assertTrue(
            all("hil_open" in item["alternate"]["status"] for item in manifest["items"])
        )
        self.assertEqual(9, manifest["maximum_simultaneously_connected"])
        self.assertEqual(
            candidate["antenna_policy"]["full_field_kit_physical_items"],
            manifest["physical_item_count"],
        )
        self.assertEqual(
            candidate["antenna_policy"]["max_simultaneously_connected"],
            manifest["maximum_simultaneously_connected"],
        )
        self.assertEqual(
            manifest["physical_item_count"],
            next(
                item["quantity"]
                for item in candidate["bom_audit"]["required_uninstantiated_parts"]
                if item["id"] == "external_antenna_kit"
            ),
        )
        self.assertEqual(0, sum(item["mpn"] is None for item in manifest["items"]))
        self.assertEqual(
            2,
            sum(item["mpn"] == "ANT-433-CW-QW-SMA" for item in manifest["items"]),
        )
        self.assertEqual(
            {"WI-FI/BLE", "WI-FI/15.4"},
            {
                item["port_label"]
                for item in manifest["items"]
                if item["termination"] == "RP-SMA male"
            },
        )
        for name in ("docs/antennas.md", "docs/antennas.ru.md"):
            page = self.read(name)
            for token in (
                "001-0012", "TX2400-JW-5", "ANT-315-CW-HW-SMA",
                "ANT-433-CW-QW-SMA", "TI.08.C.0112", "AN0155H13",
                "SMA-W100RX2", "L2-ANT-AM-LW-001", "3061990901",
                "GW.05.0153", "W1010", "UHX-328ASA2B",
                "UHX-325ASAXB", "GHX-221ASA3B", "SPWB24150",
                "AN0435H25", "SCANSMA 25-1300", "L2-ANT-AM-LW-ALT01",
            ):
                self.assertIn(token, page)

        pod = json.loads(
            (REPO_ROOT / "hardware/architecture/am-lw-pod.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("L2-ANT-AM-LW-001", pod["assembly_id"])
        self.assertFalse(pod["interface"]["power_required"])
        self.assertFalse(pod["interface"]["gpio_required"])
        self.assertEqual("3061990901", pod["electrical_design"]["core"]["mpn"])
        self.assertEqual(
            "RF2-154-T-17-50-G", pod["interface"]["connector_mpn"]
        )
        self.assertEqual("L2-ANT-AM-LW-ALT01", pod["paper_alternate"]["assembly_id"])
        self.assertEqual("3061990891", pod["paper_alternate"]["core"]["mpn"])
        self.assertEqual(
            "CONSMA013.062-G", pod["paper_alternate"]["connector"]["mpn"]
        )
        self.assertEqual(
            300,
            pod["electrical_design"]["winding"]["inductance_target_uh_at_100khz"],
        )

    def test_internal_layout_is_dimensioned_and_separates_devices(self):
        layout = self.read("docs/images/internal-board-layout.svg")
        for token in (
            "Leshy2 — dimensioned inner-board placement",
            "Inner PCB faces contain no silkscreen text",
            "Numbered physical devices",
            "UI/control PCB",
            "RF/power PCB",
            "antenna arrows reference outer-face ports",
            "M2.5 hole/head keep-out",
            "FX8C-80P-SV1(92)",
            "FX8C-80S-SV5(92)",
            "AS02404PO",
            "CMEJ-0413-42-SMT-TR",
            "JS102011SCQN",
            "TPS3435CAKAGDDFR",
            "TDK B57332V5103F360",
            "CODEC_READY and AUDIO_ARM gate protecting S3 boot GPIO0",
            "1125R-SMT-4P",
            "SKQGADE010",
            "FTSH-105-01-L-DV-K-P-TR",
            "TE Connectivity 2118651-2",
            'data-instance="s3_rf_jumper" data-centreline-mm="30.01"',
            'data-instance="c5_rf_jumper" data-centreline-mm="30.03"',
            "67 · SPK",
        ):
            self.assertIn(token, layout)
        self.assertIn('data-view="mirrored-x"', layout)
        self.assertIn('data-inner-silkscreen="none"', layout)
        self.assertNotIn('data-layer="pcb-silkscreen"', layout)
        self.assertEqual(2, layout.count('data-connector-bodies="omitted-outer-face"'))
        for forbidden_inner_silk in (
            "54 · MIC",
            "AS02404PO · speaker · side grille",
            "RUN/KILL request",
            "S3/C5 recovery controls and DBG10",
            "RP recovery controls and DBG10",
            "WI-FI/BLE",
            "nRF24-1",
        ):
            self.assertNotIn(forbidden_inner_silk, layout)
        bounds = re.search(
            r'id="validated-clearances" data-legend-bottom="([0-9.]+)" data-top="([0-9.]+)"',
            layout,
        )
        self.assertIsNotNone(bounds)
        self.assertGreaterEqual(float(bounds.group(2)) - float(bounds.group(1)), 24.0)
        for path in (
            "README.md", "README.ru.md", "docs/hardware.md", "docs/hardware.ru.md"
        ):
            page = self.read(path)
            self.assertIn("current-clamshell.svg?layout=12", page)
            self.assertIn("internal-board-layout.svg?layout=9", page)
            self.assertIn("sandwich-section.svg?layout=9", page)
            self.assertIn("top-edge-view.svg?layout=3", page)
            self.assertLess(
                page.index("current-clamshell.svg"),
                page.index("internal-board-layout.svg"),
            )
            self.assertLess(
                page.index("internal-board-layout.svg"),
                page.index("top-edge-view.svg"),
            )

    def test_sandwich_section_uses_registered_component_depths(self):
        layout = self.read("docs/images/sandwich-section.svg")
        for token in (
            'data-view="true-sections"',
            "Leshy2 — two physical cross-sections",
            "Each panel is one physical cut plane; zones are never combined.",
            "HMX035CTFT-001",
            "FX8C M1 · exact 11-mm board-to-board gap",
            "AS02404PO",
            "Keystone Electronics 1048P",
            "M5Stack U214",
            "Samtec SSW-107-02-S-D",
            'id="section-u214" data-cut-y-mm="29" data-contains="u214-no-battery"',
            'id="section-battery" data-cut-y-mm="82" data-contains="battery-controls-no-u214"',
            "No battery appears",
            "No U214 appears",
            "Keystone Electronics 1048P + 2× 18650",
            "Dimensioned architecture projection",
        ):
            self.assertIn(token, layout)

    def test_top_edge_view_has_true_axes_and_both_antenna_banks(self):
        layout = self.read("docs/images/top-edge-view.svg")
        for token in (
            'data-view="top-edge" data-look-direction="antenna-edge-to-bottom" data-rf-mounting="opposed-outer-faces"',
            "true top view from the antenna edge",
            "Looking along board +Y",
            'id="front-antenna-bank" data-count="4"',
            'id="rear-antenna-bank" data-count="5"',
            'data-mount-face="ui-pcb-outer"',
            'data-mount-face="rf-pcb-outer"',
            'data-board-gap-mm="11" data-antenna-bodies="none"',
            'data-y-collapsed="true"',
            "base PCB · 75 mm",
            "U214 · 84 mm · symmetric 4.5-mm side overhang",
            "FX8C M1 · 11-mm board gap",
            "antenna centre planes are separated by 20.55 mm",
            "HMX035CTFT-001",
            "M5Stack U214",
            "Keystone Electronics 1048P",
            "Nominal maximum selected-part depth: 44.9 mm",
        ):
            self.assertIn(token, layout)

    def test_principle_component_diagrams_are_public_and_discoverable(self):
        for hardware, schematics in (
            ("docs/hardware.md", "docs/schematics.md"),
            ("docs/hardware.ru.md", "docs/schematics.ru.md"),
        ):
            landing = self.read(hardware)
            diagrams = self.read(schematics)
            self.assertIn(f"]({Path(schematics).name})", landing)
            self.assertGreaterEqual(diagrams.count("```mermaid"), 10)
            for token in (
                "HMX035CTFT-001",
                "CMEJ-0413-42-SMT-TR",
                "AS02404PO",
                "SKQGADE010",
                "FTSH-105-01-L-DV-K-P-TR",
                "USB4105-GF-A",
                "JS102011SCQN",
                "MSPM0C1106SDGS20R",
                "TPS3435CAKAGDDFR",
                "1125R-SMT-4P",
                "SSW-107-02-S-D",
            ):
                self.assertIn(token, diagrams)

    def test_landing_pages_show_all_layout_views_and_principle_diagrams_inline(self):
        for name in ("README.md", "README.ru.md"):
            landing = self.read(name)
            for image in (
                "docs/images/current-clamshell.svg",
                "docs/images/internal-board-layout.svg",
                "docs/images/sandwich-section.svg",
                "docs/images/top-edge-view.svg",
            ):
                self.assertIn(image, landing, name)
            self.assertGreaterEqual(landing.count("```mermaid"), 10, name)
            self.assertIn("HMX035CTFT-001", landing, name)
            self.assertIn("C&K JS102011SCQN", landing, name)

    def test_project_history_is_archived_outside_public_docs(self):
        archive = REPO_ROOT / "drafts/project-history-2026-08-19"
        self.assertTrue((archive / "review/README.md").is_file())
        self.assertTrue((archive / "status/current-state.md").is_file())
        self.assertTrue((archive / "stages/03-target-product-design.md").is_file())
        self.assertTrue((archive / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
