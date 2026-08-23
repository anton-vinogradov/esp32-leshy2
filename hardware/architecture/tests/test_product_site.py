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
        "docs/lora-cap.md",
        "docs/lora-cap.ru.md",
        "docs/roadmap.md",
        "docs/roadmap.ru.md",
        "docs/physical-source-register.md",
        "docs/physical-source-register.ru.md",
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
                "docs/status", "docs/stages",
            ):
                self.assertNotIn(forbidden, page, f"{name}: {forbidden}")
            if "roadmap" not in name and not name.startswith("README"):
                self.assertNotIn("проведено ревью", page, name)

    def test_roadmap_reports_current_truth_and_complete_route(self):
        pages = {
            "docs/roadmap.md": (
                "Current hardware stage: H1", "not accepted",
                "F3 target boot/emulation is not closed",
                "no current production ECAD schematic",
                "H9. Manufacturing release", "Production ECAD",
            ),
            "docs/roadmap.ru.md": (
                "Текущий аппаратный этап: H1", "целостный мокап не принят",
                "F3 не закрыт", "не создана",
                "H9. Производственный release",
                "Production ECAD",
            ),
        }
        for name, tokens in pages.items():
            page = " ".join(self.read(name).split())
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for stage in range(10):
                self.assertIn(f"H{stage}", page, f"{name}: missing H{stage}")

        self.assertIn("docs/roadmap.md", self.read("README.md"))
        self.assertIn("docs/roadmap.ru.md", self.read("README.ru.md"))
        landing_pages = {
            "README.md": ("Roadmap and current position", "Hardware is at H1", "printing/fabrication"),
            "README.ru.md": ("Роадмап и текущая позиция", "Железо находится на H1", "печать/на фабрику"),
        }
        for name, tokens in landing_pages.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for stage in range(10):
                self.assertIn(f"H{stage} ·", page, f"{name}: missing H{stage}")

    def test_hardware_stages_are_strictly_sequential(self):
        for name, reviewed in (
            ("README.md", "Reviewed"),
            ("README.ru.md", "Проведено ревью"),
        ):
            page = self.read(name)
            rows = {
                int(stage): row
                for stage, row in re.findall(
                    r"^\| \**H(\d+) ·([^\n]+)$", page, flags=re.MULTILINE
                )
            }
            self.assertEqual(set(range(10)), set(rows), name)
            self.assertIn(reviewed, rows[0], name)
            self.assertIn("Current" if name == "README.md" else "Сейчас", rows[1], name)
            for stage in range(2, 10):
                self.assertNotIn(reviewed, rows[stage], f"{name}: H{stage}")

    def test_interconnect_page_distinguishes_mechanical_fit_from_ecad(self):
        expectations = {
            "docs/interconnect.md": (
                "Every inter-board net listed below crosses only inside the single M1 body",
                "The five RF microcoaxes",
                "not a claim that copper is already routed",
            ),
            "docs/interconnect.ru.md": (
                "Все перечисленные ниже межплатные цепи проходят только внутри единого корпуса",
                "Отдельно проверены пять RF-коаксиалов",
                "не заявлением, что медь уже разведена",
            ),
        }
        for name, tokens in expectations.items():
            page = " ".join(self.read(name).split())
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_current_hardware_substep_is_visible_and_synchronized(self):
        pages = ("README.md", "README.ru.md", "docs/roadmap.md", "docs/roadmap.ru.md")
        markers = {}
        for name in pages:
            page = self.read(name)
            found = re.findall(r"<!-- current-substep: (H\d+(?:\.\d+)+) -->", page)
            self.assertEqual(1, len(found), name)
            markers[name] = found[0]
            self.assertIn(f"`{found[0]}`", page, name)
            self.assertEqual(1, page.count(f"▶️ **`{found[0]}`"), name)
            self.assertIn("commit", page, name)

        self.assertEqual({"H1.3.1"}, set(markers.values()))
        for name in ("README.md", "README.ru.md"):
            page = self.read(name)
            for substep in ("H1.0", "H1.1.1", "H1.1.2", "H1.1.3", "H1.8"):
                self.assertIn(f"`{substep}`", page, f"{name}: {substep}")

    def test_mockup_has_staged_user_review_gates(self):
        gates = ("H1.3.1", "H1.4.1", "H1.5.1", "H1.7.1", "H1.8")
        for name in ("README.md", "docs/roadmap.md"):
            page = self.read(name)
            for gate in gates:
                self.assertIn(f"`{gate}`", page, f"{name}: {gate}")
            self.assertIn("user review gate", page, name)
            self.assertIn("reopens", page, name)

        for name in ("README.ru.md", "docs/roadmap.ru.md"):
            page = self.read(name)
            for gate in gates:
                self.assertIn(f"`{gate}`", page, f"{name}: {gate}")
            self.assertIn("пользовательское согласование", page, name)
            self.assertIn("повторно открывает", page, name)

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
            "Text on a PCB face but outside component outlines is intended silkscreen",
            'data-coordinate-model="L2-ASM-COORD-001-A"',
            'data-review-gate="H1.3.1" data-review-status="awaiting-user"',
            'data-face="front-outer" data-board-mm="75x150"',
            'data-face="rear-outer" data-board-mm="75x150"',
            'data-layer="pcb-silkscreen"',
            "HMX035CTFT-001",
            "ACTIVE 48.96×73.44 mm · 320×480 · 2:3",
            "54.5×83.0×3.2 mm LCD/CTP body",
            "M5Stack U214",
            "HLE-107-02-G-DV-PE-LC",
            "insert ⊗ · remove ⊙",
            "Keystone 1048P",
            'data-instance="ui_dpad_up" data-direct-press="true"',
            'data-instance="ui_dpad_down" data-direct-press="true"',
            'data-instance="ui_dpad_left" data-direct-press="true"',
            'data-instance="ui_dpad_right" data-direct-press="true"',
            'data-instance="ui_dpad_ok" data-direct-press="true"',
            'data-instance="ui_switch_f1" data-direct-press="true"',
            'data-instance="ui_switch_f2" data-direct-press="true"',
            'data-instance="ui_switch_f3" data-direct-press="true"',
            'data-instance="ui_switch_f4" data-direct-press="true"',
            'data-instance="ui_switch_f5" data-direct-press="true"',
            'data-instance="ui_switch_f6" data-direct-press="true"',
            'data-instance="ui_switch_f7" data-direct-press="true"',
            'data-instance="ui_switch_f8" data-direct-press="true"',
            "RUN",
            "KILL",
            "PTT",
            "physical actual-TX evidence for each built-in transmitting path",
            "form two aligned rows of five",
            "M2.5 hole/head keep-outs",
            'id="front-outer-rf-bank" data-mount-face="ui-pcb-outer"',
            'id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer"',
            "both RF connector banks mount on the outward PCB faces",
            "GCT RFPC-SMA31-FN-175-A",
            "GCT RFPC-SMA32-FN-175-A",
            "WI-FI/BLE",
            "2.4 GHz",
            "WI-FI/15.4",
            "2.4/5 GHz",
            "nRF24-1",
            "SUB-GHz",
            "VHF/UHF",
            "TX ACTIVE",
            "HEADSET",
            "CTIA",
            "C5 SERVICE USB",
            "MICROPHONE",
            "SPEAKER",
            "microSD",
            "POWER",
            "USB / POWER",
            "RP SERVICE USB",
            "M5 UNIT",
        ):
            self.assertIn(token, layout)
        self.assertNotIn("SPEAKER / GRILLE", layout)
        self.assertNotIn('data-interface-kind="acoustic-opening"', layout)
        for connector_silkscreen in ("2.4 GHz RP-SMA", "2.4/5 GHz RP-SMA", "2.4 GHz SMA"):
            self.assertNotIn(connector_silkscreen, layout)
        for process_token in ("G3-0001", "not G7", "not KiCad", "Working projection"):
            self.assertNotIn(process_token, layout)
        self.assertIn(
            'data-instance="ptt_switch" data-direct-press="true"', layout
        )
        self.assertIn("Navigation is five exact OMRON B3S-1100P direct buttons", layout)
        self.assertNotIn('data-manufacturing-class="custom-actuator"', layout)
        self.assertNotIn("supplier MPN does not apply", layout)
        self.assertIn('data-instance="encoder_knob" data-selected-part="true"', layout)
        self.assertIn("Davies 1227-J is the exact encoder knob", layout)
        self.assertNotIn("STOP actuator", layout)
        self.assertNotIn("RE-ARM", layout)

    def test_external_face_acceptance_package_is_complete(self):
        import json

        package = json.loads(
            self.read("hardware/product-design/generated/H1-external-face-acceptance.json")
        )
        self.assertEqual("H1.3.0", package["stage"])
        self.assertEqual("H1.3.1", package["review_gate"])
        self.assertEqual("awaiting_user_review", package["status"])
        self.assertEqual("L2-ASM-COORD-001-A", package["coordinate_model"])
        self.assertEqual([75.0, 150.0], package["front"]["board_outline_mm"])
        self.assertEqual([75.0, 150.0], package["rear"]["board_outline_mm"])
        self.assertEqual([320, 480], package["front"]["display"]["pixels"])
        self.assertEqual([48.96, 73.44], package["front"]["display"]["active_area_mm"])
        function_keys = package["front"]["function_key_columns"]
        self.assertEqual("OMRON B3S-1100P", function_keys["mpn"])
        self.assertEqual(["F1", "F2", "F3", "F4"], function_keys["left"])
        self.assertEqual(["F5", "F6", "F7", "F8"], function_keys["right"])
        self.assertEqual(1.85, function_keys["display_clearance_mm"])
        self.assertEqual(4.5, function_keys["top_mounting_keepout_clearance_mm"])
        self.assertEqual(0, function_keys["free_expander_inputs_after_placement"])
        self.assertEqual(4, len(package["front"]["antenna_ports"]))
        self.assertEqual(5, len(package["rear"]["antenna_ports"]))
        self.assertEqual(15, len(package["front"]["controls"]))
        self.assertEqual(2, len(package["rear"]["controls"]))
        self.assertEqual(
            {f"ui_switch_f{index}" for index in range(1, 9)},
            {
                item["instance"]
                for item in package["front"]["controls"]
                if item["instance"].startswith("ui_switch_f")
            },
        )
        self.assertFalse(
            any(item["instance"].startswith("ui_switch_f") for item in package["rear"]["controls"])
        )
        self.assertTrue(
            any(
                item["instance"] == "microphone" and item["edge"] == "bottom"
                for item in package["front"]["edge_interfaces"]
            )
        )
        self.assertFalse(
            any(
                item["instance"] == "microphone"
                for item in package["rear"]["edge_interfaces"]
            )
        )
        indicators = package["front"]["tx_indicators"]
        self.assertEqual(10, len(indicators))
        self.assertEqual(
            {(row, column) for row in (1, 2) for column in range(1, 6)},
            {(item["row"], item["column"]) for item in indicators},
        )
        self.assertTrue(all(package["machine_checks"].values()))

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
        candidate_policy = candidate["audio_receiver_contract"]["broadcast_transmit_policy"]
        self.assertIn("no custom transmitter", candidate_policy)
        self.assertIn("not a current product capability", candidate_policy)
        self.assertIn("receive-only", candidate_policy)
        self.assertIn(
            "Вещательная передача FM/AM/SW/LW не является возможностью устройства",
            self.read("docs/hardware.ru.md"),
        )
        self.assertIn(
            "FM/AM/SW/LW broadcast transmission is not a device capability",
            self.read("docs/hardware.md"),
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
            'data-instance="s3_rf_jumper" data-projected-chord-mm="14.78" data-assembly-length-mm="30.00" data-unprojected-slack-mm="15.22"',
            'data-instance="c5_rf_jumper" data-projected-chord-mm="15.50" data-assembly-length-mm="30.00" data-unprojected-slack-mm="14.50"',
            " · SPK",
            'data-inner-body-count="130"',
            'data-max-inner-height-mm="8.95"',
            'data-min-single-body-clearance-mm="2.05"',
            'data-display-adapter-opposing-pairs="5"',
            'data-min-display-adapter-clearance-mm="6.00"',
            'data-opposing-pairs="36"',
            'data-intentional-mates="1"',
            'data-min-z-clearance-mm="3.31"',
            'data-rf-cable-routes="2"',
            'data-rf-pcb-topology-guides="9"',
            'data-route-state="pre-ecad-topology-only"',
            'data-nrf-cable-reserves="3"',
            'data-opposing-cable-pairs="2"',
            'data-nrf-reserve-opposing-pairs="5"',
            'data-encoder-through-features="7"',
            'data-cable-od-max-mm="1.13"',
            'data-functional-zones="1"',
            'data-voice-rf-endpoint-distance-mm="32.92"',
            'data-path="S3-2G4"',
            'data-path="RX-FM/SW"',
            'data-path="RX-AM/LW"',
            'data-path="C5-2G4/5"',
            'data-path="N24-0"',
            'data-path="CC-SUB"',
            'data-path="N24-1"',
            'data-path="VOICE-V/U"',
            'data-path="N24-2"',
            "Antenna-to-radio map · all nine paths",
            "solid green/cyan = direct cable projection · dashed blue = future 50 Ω PCB mainline",
            "module · no RF land; output is built-in U.FL",
            "module · ANT1 U.FL active; ANT2 land disabled",
            "PCB re-entry · feeds TX coupler and outer RP-SMA",
            'id="module-integrated-rf-connectors" data-count="5" data-exact-position-count="2" data-schematic-position-count="3"',
            'id="board-rf-cable-to-trace-handoffs" data-count="5"',
            'data-medium="removable-microcoax"',
            'data-medium="controlled-50-ohm-pcb"',
            "ring on S3/C5 = module U.FL · ring on nRF = module IPEX · numbered ring = board U.FL",
            "outward RP-SMA · antenna screws on here",
            "all 130 inner bodies checked individually; tallest 8.95 mm; opposite-plane remainder 2.05 mm",
            "complete 3.80-mm display adapter: 5 opposing crossings; minimum Z gap 6.00 mm",
            "opposing inner faces: 36 non-mating XY pairs checked; minimum Z gap 3.31 mm",
            "RF coax: 2 direct exact-endpoint projections + 3 nRF module-face reserves; all five 30-mm assemblies accounted",
            "nRF reserve crossings: 5; minimum Z gap 5.20 mm",
            "EC11E through-board features: 7 checked; 2 opposing crossings; minimum Z gap 4.20 mm",
            "limiting pair: 20 3.5-mm CTIA headset TRRS mid-mount connector / 119 protected-pack branch fuse #0",
            "TCA9534APWR",
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
        ):
            self.assertNotIn(forbidden_inner_silk, layout)
        self.assertIn('id="outer-antenna-datum-annotations" data-layer="drawing-annotation"', layout)
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
            self.assertIn("current-clamshell.svg?layout=16", page)
            self.assertIn("navigation-cluster.svg?layout=1", page)
            self.assertIn("internal-board-layout.svg?layout=18", page)
            self.assertIn("sandwich-section.svg?layout=10", page)
            self.assertIn("top-edge-view.svg?layout=4", page)
            self.assertLess(
                page.index("current-clamshell.svg"),
                page.index("internal-board-layout.svg"),
            )
            self.assertLess(
                page.index("internal-board-layout.svg"),
                page.index("top-edge-view.svg"),
            )
        import json

        coordinate_table = json.loads(
            self.read("hardware/product-design/generated/H1-unified-coordinate-table.json")
        )
        audit = coordinate_table["interboard_fit_audit"]
        self.assertEqual("paper_geometry_passed", audit["result"])
        self.assertEqual(130, audit["inner_body_count"])
        self.assertEqual(132, audit["total_inner_component_count_including_adapter"])
        self.assertTrue(audit["all_inner_bodies_have_sourced_positive_height"])
        self.assertTrue(audit["no_inner_body_exceeds_gap"])
        self.assertTrue(audit["no_inner_body_violates_minimum_clearance"])
        self.assertEqual(8.95, audit["tallest_inner_body"]["height_mm"])
        self.assertEqual(2.05, audit["tallest_inner_body"]["remaining_to_opposite_pcb_plane_mm"])
        self.assertEqual(130, len(audit["individual_body_clearances"]))
        self.assertTrue(
            all(
                row["remaining_to_opposite_pcb_plane_mm"] >= 0.7
                for row in audit["individual_body_clearances"]
            )
        )
        self.assertEqual(36, audit["opposing_non_mating_pair_count"])
        self.assertEqual(3.31, audit["minimum_opposing_pair"]["remaining_z_clearance_mm"])
        self.assertEqual(36, len(audit["opposing_non_mating_pairs"]))
        self.assertTrue(
            all(
                row["remaining_z_clearance_mm"] >= 0.7
                for row in audit["opposing_non_mating_pairs"]
            )
        )
        self.assertEqual(11.0, audit["intentional_mate"]["mated_height_mm"])
        self.assertEqual(3.8, audit["display_adapter_assembly"]["complete_height_from_ui_inner_mm"])
        self.assertEqual(5, audit["display_adapter_assembly"]["opposing_pair_count"])
        self.assertEqual(6.0, audit["display_adapter_assembly"]["minimum_opposing_z_clearance_mm"])
        self.assertEqual(
            7.77,
            audit["minimum_native_rf_cable_direct_projection_crossing"][
                "remaining_z_clearance_mm"
            ],
        )
        self.assertEqual(2, len(audit["native_rf_cable_direct_projection_crossings"]))
        interconnect = coordinate_table["physical_interconnect_clearance_audit"]
        self.assertEqual(
            "paper_keepouts_passed_final_ecad_and_h5_open", interconnect["result"]
        )
        self.assertEqual(80, interconnect["m1_interboard_connector"]["contact_count"])
        coax = interconnect["rf_microcoax"]
        self.assertEqual(2, coax["direct_endpoint_projection_count"])
        self.assertEqual(2, coax["direct_projection_opposing_crossing_count"])
        self.assertEqual("H5_open", coax["native_slack_bend_and_retention_status"])
        self.assertEqual(
            [14.781343, 15.50061],
            [row["projected_chord_mm"] for row in coax["native_direct_projections"]],
        )
        self.assertEqual(3, coax["conservative_nrf_module_face_reserve_count"])
        self.assertTrue(coax["all_five_feed_assemblies_accounted"])
        self.assertEqual(5.2, coax["minimum_nrf_reserve_opposing_crossing"]["remaining_z_clearance_mm"])
        native_chains = coax["native_feed_chain_after_green_cable"]
        self.assertEqual(["s3", "c5"], [row["owner"] for row in native_chains])
        self.assertTrue(
            all(
                row["green_cable_ends_at"] == "Hirose U.FL-R-SMT-1(10)"
                and row["user_antenna_connector_mpn"] == "GCT RFPC-SMA32-FN-175-A"
                for row in native_chains
            )
        )
        antenna_topology = interconnect["antenna_source_to_port_topology"]
        self.assertEqual(
            "all_nine_onboard_paths_accounted_topology_only",
            antenna_topology["result"],
        )
        self.assertEqual(9, antenna_topology["guide_count"])
        medium_boundaries = antenna_topology["rendered_medium_boundaries"]
        self.assertEqual(5, medium_boundaries["module_integrated_connector_count"])
        self.assertEqual(2, medium_boundaries["exact_module_integrated_connector_count"])
        self.assertEqual(
            3,
            medium_boundaries["schematic_position_module_integrated_connector_count"],
        )
        self.assertEqual(5, medium_boundaries["cable_to_pcb_handoff_count"])
        self.assertEqual(
            "rendered_schematically_exact_axis_H5_open",
            medium_boundaries["nrf_module_connector_axis"],
        )
        self.assertEqual(
            {
                "S3-2G4", "RX-FM/SW", "RX-AM/LW", "C5-2G4/5",
                "N24-0", "CC-SUB", "N24-1", "VOICE-V/U", "N24-2",
            },
            {row["path"] for row in antenna_topology["guides"]},
        )
        through = interconnect["outer_face_through_board_features"]
        self.assertEqual(7, through["encoder_feature_count"])
        self.assertEqual(4.2, through["minimum_encoder_opposing_crossing"]["remaining_z_clearance_mm"])
        self.assertEqual("not_yet_proven_pre_kicad", interconnect["pcb_copper_and_vias"]["result"])

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
            "Samtec HLE-107-02-G-DV-PE-LC",
            'id="section-u214" data-cut-y-mm="29" data-contains="u214-no-battery"',
            'id="section-battery" data-cut-y-mm="82" data-contains="battery-no-u214"',
            "No battery appears",
            "No installed Cap appears",
            "Keystone Electronics 1048P + 2× 18650",
            "Complete opposing-body Z clearance",
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
            "installed U214 worst-case · symmetric 4.5-mm side overhang",
            "FX8C M1 · 11-mm board gap",
            "antenna centre planes are separated by 20.55 mm",
            "HMX035CTFT-001",
            "M5Stack U214",
            "Keystone Electronics 1048P",
            "Nominal maximum selected-part depth: 38.1 mm",
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
                "HLE-107-02-G-DV-PE-LC",
            ):
                self.assertIn(token, diagrams)

    def test_exact_lora_cap_is_product_facing_and_keeps_one_device_per_node(self):
        for page_name in ("docs/lora-cap.md", "docs/lora-cap.ru.md"):
            page = self.read(page_name)
            self.assertEqual(3, page.count("```mermaid"), page_name)
            for token in (
                "LESHY2-LORA-CAP-01-EU868",
                "LESHY2-LORA-CAP-01-US915",
                "NiceRF LoRa1262-868",
                "NiceRF LoRa1262-915",
                "DC0710J5020AHF",
                "AD8314ACPZ-RL7",
                "TLV1821DCKR",
                "SN74LVC1G123DCTR",
                "SN74LVC1G06DCKR",
                "24AA02UIDT-I/OT",
                "TPS7A2033PDBVR",
                "EXT_TX_EVIDENCE_N",
            ):
                self.assertIn(token, page, f"{page_name}: {token}")
            for combined in (
                "AD8314ACPZ-RL7 + TLV1821DCKR",
                "SN74LVC1G123DCTR + SN74LVC1G06DCKR",
                "LoRa1262-868 or LoRa1262-915<br/>",
            ):
                self.assertNotIn(combined, page, f"{page_name}: {combined}")

        layout = self.read("docs/images/lora-cap-layout.svg")
        self.assertEqual(27, layout.count("data-instance="))
        for token in (
            "exact-device envelope projection",
            "every numbered outline is one physical device",
            "OUTER FACE",
            "accessible silkscreen is green",
            "INNER FACE",
            "mirrored from outer face",
            "no silkscreen",
            "DOCUMENTATION LEGEND · not PCB silkscreen",
            "RF / antenna outward",
            "mating ⊗",
        ):
            self.assertIn(token, layout)

    def test_landing_pages_show_all_layout_views_and_principle_diagrams_inline(self):
        for name in ("README.md", "README.ru.md"):
            landing = self.read(name)
            for image in (
                "docs/images/current-clamshell.svg",
                "docs/images/navigation-cluster.svg",
                "docs/images/display-adapter.svg",
                "docs/images/internal-board-layout.svg",
                "docs/images/sandwich-section.svg",
                "docs/images/top-edge-view.svg",
            ):
                self.assertIn(image, landing, name)
            self.assertGreaterEqual(landing.count("```mermaid"), 10, name)
            self.assertIn("HMX035CTFT-001", landing, name)
            self.assertIn("C&K JS102011SCQN", landing, name)

    def test_navigation_cluster_uses_only_series_controls(self):
        drawing = self.read("docs/images/navigation-cluster.svg")
        for token in (
            'data-view="series-navigation-cluster"',
            'data-design-id="L2-NAV-5B-001-A"',
            'data-manufacturing-class="serial-components-only"',
            "Five exact series buttons",
            "OMRON B3S-1100P",
            "UP",
            "DOWN",
            "LEFT",
            "RIGHT",
            "OK",
        ):
            self.assertIn(token, drawing)

    def test_project_history_is_archived_outside_public_docs(self):
        archive = REPO_ROOT / "drafts/project-history-2026-08-19"
        self.assertTrue((archive / "review/README.md").is_file())
        self.assertTrue((archive / "status/current-state.md").is_file())
        self.assertTrue((archive / "stages/03-target-product-design.md").is_file())
        self.assertTrue((archive / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
