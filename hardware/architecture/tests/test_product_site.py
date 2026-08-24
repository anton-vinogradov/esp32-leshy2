import re
import subprocess
import sys
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
        "docs/stage-results.md",
        "docs/stage-results.ru.md",
        "docs/power-architecture.md",
        "docs/power-architecture.ru.md",
        "docs/interface-isolation.md",
        "docs/interface-isolation.ru.md",
        "docs/quiet-state.md",
        "docs/quiet-state.ru.md",
        "docs/fault-shutdown.md",
        "docs/fault-shutdown.ru.md",
        "docs/safety-review.md",
        "docs/safety-review.ru.md",
        "docs/service-recovery.md",
        "docs/service-recovery.ru.md",
        "docs/no-connects.md",
        "docs/no-connects.ru.md",
        "docs/erc-review.md",
        "docs/erc-review.ru.md",
        "docs/hwfw-reconciliation.md",
        "docs/hwfw-reconciliation.ru.md",
        "docs/h2-acceptance.md",
        "docs/h2-acceptance.ru.md",
        "docs/virtual-verification.md",
        "docs/virtual-verification.ru.md",
        "docs/parameter-model-register.md",
        "docs/parameter-model-register.ru.md",
        "docs/verification-methods.md",
        "docs/verification-methods.ru.md",
        "docs/power-state-register.md",
        "docs/power-state-register.ru.md",
        "docs/dc-power-budget.md",
        "docs/dc-power-budget.ru.md",
        "docs/source-charge-budget.md",
        "docs/source-charge-budget.ru.md",
        "docs/dc-verification-result.md",
        "docs/dc-verification-result.ru.md",
        "docs/power-transition-startup.md",
        "docs/power-transition-startup.ru.md",
        "docs/power-handover.md",
        "docs/power-handover.ru.md",
        "docs/inrush-load-step.md",
        "docs/inrush-load-step.ru.md",
        "docs/watchdog-fault-display.md",
        "docs/watchdog-fault-display.ru.md",
        "docs/power-transition-result.md",
        "docs/power-transition-result.ru.md",
        "docs/display-electrical-verification.md",
        "docs/display-electrical-verification.ru.md",
        "docs/audio-electrical-verification.md",
        "docs/audio-electrical-verification.ru.md",
        "docs/ir-electrical-verification.md",
        "docs/ir-electrical-verification.ru.md",
        "docs/battery-analog-verification.md",
        "docs/battery-analog-verification.ru.md",
        "docs/analog-corner-result.md",
        "docs/analog-corner-result.ru.md",
        "docs/digital-levels-verification.md",
        "docs/digital-levels-verification.ru.md",
        "docs/digital-timing-verification.md",
        "docs/digital-timing-verification.ru.md",
        "docs/boundary-loading-verification.md",
        "docs/boundary-loading-verification.ru.md",
        "docs/digital-verification-result.md",
        "docs/digital-verification-result.ru.md",
        "docs/rf-feed-constraints.md",
        "docs/rf-feed-constraints.ru.md",
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
            if not any(token in name for token in ("roadmap", "stage-results")) and not name.startswith("README"):
                self.assertNotIn("проведено ревью", page, name)

    def test_roadmap_reports_current_truth_and_complete_route(self):
        pages = {
            "docs/roadmap.md": (
                "Current hardware stage: H3", "H1 accepted",
                "F3 target boot/emulation is not closed",
                "H2.2.5",
                "H9. Manufacturing release", "Production ECAD",
            ),
            "docs/roadmap.ru.md": (
                "Текущий аппаратный этап: H3", "H1 принят",
                "F3 не закрыт", "H2.2.5",
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
            "README.md": ("Roadmap and current position", "Hardware is at H3", "printing/fabrication"),
            "README.ru.md": ("Роадмап и текущая позиция", "Железо находится на H3", "печать/на фабрику"),
        }
        for name, tokens in landing_pages.items():
            page = self.read(name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")
            for stage in range(10):
                self.assertIn(f"H{stage} ·", page, f"{name}: missing H{stage}")

    def test_landing_page_is_a_product_front_door(self):
        expectations = {
            "README.md": (
                "⭐ Leshy2",
                "What Leshy2 is",
                "Target device mockup",
                "Roadmap and current position",
                "Principle diagrams and electrical implementation",
                "Stage results",
            ),
            "README.ru.md": (
                "⭐ Leshy2",
                "Что такое Leshy2",
                "Макет целевого устройства",
                "Роадмап и текущая позиция",
                "Принципиальные схемы и электрическая реализация",
                "Результаты этапов",
            ),
        }
        for name, tokens in expectations.items():
            page = self.read(name)
            self.assertEqual(1, page.count("⭐"), name)
            self.assertIn("docs/images/current-clamshell.svg", page, name)
            for token in tokens:
                self.assertIn(token, page, f"{name}: {token}")

    def test_hardware_stages_are_strictly_sequential(self):
        import json

        state = json.loads(
            self.read("hardware/verification/hardware-roadmap-state.json")
        )
        expected = {int(row["id"][1:]): row["status"] for row in state["stages"]}
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
            for stage, status in expected.items():
                if status == "reviewed":
                    self.assertIn(reviewed, rows[stage], f"{name}: H{stage}")
                elif status == "current":
                    self.assertIn(
                        "Current" if name == "README.md" else "Сейчас",
                        rows[stage],
                        f"{name}: H{stage}",
                    )
                else:
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
        import json

        pages = ("README.md", "README.ru.md", "docs/roadmap.md", "docs/roadmap.ru.md")
        state = json.loads(
            self.read("hardware/verification/hardware-roadmap-state.json")
        )
        current_substep = state["current_substep"]
        markers = {}
        for name in pages:
            page = self.read(name)
            found = re.findall(r"<!-- current-substep: (H\d+(?:\.\d+)+) -->", page)
            self.assertEqual(1, len(found), name)
            markers[name] = found[0]
            self.assertIn(f"`{found[0]}`", page, name)
            self.assertRegex(
                page,
                rf"\*\*(?:Exact marker|Точный маркер): `{re.escape(found[0])}`\*\*",
                name,
            )
            self.assertIn("commit", page, name)

        self.assertEqual({current_substep}, set(markers.values()))
        for name in ("README.md", "README.ru.md"):
            page = self.read(name)
            for substep in ("H1.8", "H2.0.1", "H2.0.2", "H2.0.3", "H2.8"):
                self.assertIn(f"`{substep}`", page, f"{name}: {substep}")

    def test_mockup_has_staged_user_review_gates(self):
        gates = ("H1.3.1", "H1.4.1", "H1.5.1", "H1.7.1", "H1.8")
        for name in ("docs/roadmap.md",):
            page = self.read(name)
            for gate in gates:
                self.assertIn(f"`{gate}`", page, f"{name}: {gate}")
            self.assertIn("accepted by the user", page, name)
            self.assertIn("reopens", page, name)

        for name in ("docs/roadmap.ru.md",):
            page = self.read(name)
            for gate in gates:
                self.assertIn(f"`{gate}`", page, f"{name}: {gate}")
            self.assertIn("пользовательское согласование", page, name)
            self.assertIn("повторно открывает", page, name)

    def test_h2_schematic_plan_starts_only_authorized_work(self):
        import json

        plan = json.loads(self.read("hardware/ecad/h2-schematic-plan.json"))
        self.assertEqual("H2", plan["stage"])
        self.assertEqual("reviewed", plan["status"])
        self.assertIsNone(plan["current_substep"])
        self.assertEqual("H2.8.2", plan["completed_substep"])
        self.assertEqual("accepted_by_user", plan["acceptance"]["status"])
        self.assertEqual("accepted", plan["accepted_input"]["status"])
        self.assertEqual("H1.8", plan["accepted_input"]["physical_design_gate"])
        self.assertTrue(plan["authorization"]["production_schematic"])
        self.assertTrue(plan["authorization"]["symbol_and_footprint_library_work"])
        self.assertFalse(plan["authorization"]["pcb_placement_and_routing"])
        self.assertFalse(plan["authorization"]["fabrication"])
        self.assertFalse(plan["authorization"]["purchasing"])
        self.assertEqual(4, len(plan["projects"]))
        self.assertEqual(
            28,
            sum(len(sheets) for sheets in plan["proposed_sheet_graphs"].values()),
        )
        self.assertEqual(
            ["H2.0.1", "H2.0.2", "H2.0.3"],
            [item["id"] for item in plan["substeps"][0]["children"]],
        )
        self.assertEqual("reviewed", plan["substeps"][1]["status"])
        self.assertEqual(
            [f"H2.2.{index}" for index in range(1, 11)],
            [item["id"] for item in plan["substeps"][2]["children"]],
        )
        self.assertEqual("reviewed", plan["substeps"][2]["children"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][3]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][4]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][5]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][6]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][7]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][8]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["children"][9]["status"])
        self.assertEqual("reviewed", plan["substeps"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["status"])
        self.assertEqual(
            [f"H2.3.{index}" for index in range(1, 14)],
            [item["id"] for item in plan["substeps"][3]["children"]],
        )
        self.assertEqual("reviewed", plan["substeps"][3]["children"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][3]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][4]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][5]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][6]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][7]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][8]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][9]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][10]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][11]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][12]["status"])
        self.assertFalse(
            any(
                item["status"] == "waiting"
                for item in plan["substeps"][3]["children"][12:]
            )
        )
        self.assertEqual("reviewed", plan["substeps"][4]["status"])
        self.assertTrue(
            all(item["status"] == "reviewed" for item in plan["substeps"][4]["children"])
        )
        self.assertTrue(
            all(item["status"] == "reviewed" for item in plan["substeps"])
        )
        self.assertTrue(
            all(
                child["status"] == "reviewed"
                for item in plan["substeps"]
                for child in item.get("children", [])
            )
        )
        sheet_contract = json.loads(
            self.read("hardware/ecad/H2-sheet-contract.json")
        )
        binding = sheet_contract["inventory_binding"]
        self.assertEqual("reviewed_against_complete_h2_0_1_inventory", binding["status"])
        self.assertEqual(1035, binding["registered_inventory_rows"])
        self.assertEqual(
            {
                "LESHY2-UI": 377,
                "LESHY2-RF": 628,
                "L2-DISP-ADP-001-A": 2,
                "LESHY2-LORA-CAP-01": 28,
            },
            binding["project_row_counts"],
        )
        self.assertEqual(4, len(binding["intentionally_component_empty_sheets"]))
        self.assertEqual(24, len(binding["sheet_row_counts"]))
        self.assertEqual(1035, sum(binding["sheet_row_counts"].values()))

    def test_h3_plan_and_accepted_input_freeze_are_current(self):
        import hashlib
        import json

        plan = json.loads(
            self.read("hardware/verification/h3-verification-plan.json")
        )
        state = json.loads(
            self.read("hardware/verification/hardware-roadmap-state.json")
        )
        freeze = json.loads(
            self.read("hardware/verification/generated/H3-VRF01-input-freeze.json")
        )
        inventory = json.loads(
            self.read("hardware/verification/generated/H3-VRF02-parameter-inventory.json")
        )
        methods = json.loads(
            self.read("hardware/verification/generated/H3-VRF03-method-contract.json")
        )
        power_states = json.loads(
            self.read("hardware/verification/generated/H3-VRF11-power-state-register.json")
        )
        dc_budget = json.loads(
            self.read("hardware/verification/generated/H3-VRF12-dc-budget.json")
        )
        source_budget = json.loads(
            self.read("hardware/verification/generated/H3-VRF13-source-charge-budget.json")
        )
        dc_result = json.loads(
            self.read("hardware/verification/generated/H3-VRF14-dc-consolidation.json")
        )
        audio = json.loads(
            self.read("hardware/verification/generated/H3-VRF32-audio.json")
        )
        ir = json.loads(
            self.read("hardware/verification/generated/H3-VRF33-ir.json")
        )
        self.assertEqual("H3", plan["stage"])
        self.assertEqual("H3.5.2", plan["current_substep"])
        self.assertEqual(plan["current_substep"], state["current_substep"])
        self.assertEqual("reviewed", plan["substeps"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][0]["children"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][0]["children"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][0]["children"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][1]["children"][0]["status"])
        self.assertTrue(all(row["status"] == "reviewed" for row in plan["substeps"][1]["children"]))
        self.assertEqual("reviewed", plan["substeps"][2]["status"])
        self.assertTrue(all(row["status"] == "reviewed" for row in plan["substeps"][2]["children"]))
        self.assertEqual("reviewed", plan["substeps"][3]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][3]["status"])
        self.assertEqual("reviewed", plan["substeps"][3]["children"][4]["status"])
        self.assertEqual("reviewed", plan["substeps"][4]["status"])
        self.assertEqual("reviewed", plan["substeps"][4]["children"][0]["status"])
        self.assertEqual("reviewed", plan["substeps"][4]["children"][1]["status"])
        self.assertEqual("reviewed", plan["substeps"][4]["children"][2]["status"])
        self.assertEqual("reviewed", plan["substeps"][4]["children"][3]["status"])
        self.assertEqual("current", plan["substeps"][5]["status"])
        self.assertEqual("reviewed", plan["substeps"][5]["children"][0]["status"])
        self.assertEqual("current", plan["substeps"][5]["children"][1]["status"])
        self.assertEqual(16, freeze["summary"]["verification_domains"])
        self.assertEqual(0, freeze["summary"]["unassigned_virtual_checks"])
        self.assertEqual(0, freeze["summary"]["unassigned_physical_checks"])
        self.assertEqual(1035, inventory["summary"]["registered_instances"])
        self.assertEqual(217, inventory["summary"]["used_device_types"])
        self.assertEqual(0, inventory["summary"]["source_missing"])
        self.assertEqual(71, inventory["summary"]["used_types_with_structured_electrical_contract"])
        self.assertEqual(146, inventory["summary"]["used_types_requiring_parameter_extraction"])
        self.assertEqual(2, inventory["summary"]["official_h3_source_overrides"])
        self.assertEqual(1, inventory["summary"]["lifecycle_decisions"])
        self.assertEqual(0, inventory["summary"]["open_decisions"])
        self.assertEqual([], inventory["open_decisions"])
        self.assertEqual("H3-NRF24-LIFECYCLE", inventory["resolved_choices"][0]["id"])
        self.assertEqual("A", inventory["resolved_choices"][0]["selected_option"])
        self.assertEqual(8, methods["summary"]["methods"])
        self.assertEqual(10, methods["summary"]["pass_fail_rules"])
        self.assertEqual(0, methods["summary"]["third_party_runtime_dependencies"])
        self.assertEqual(0, methods["summary"]["open_method_questions"])
        self.assertEqual(43, power_states["summary"]["source_charge_states"])
        self.assertEqual(10, power_states["summary"]["signal_groups"])
        self.assertEqual(25, power_states["summary"]["group_modes"])
        self.assertEqual(50, power_states["summary"]["operating_profiles"])
        self.assertEqual(2032, power_states["summary"]["legal_states"])
        self.assertEqual(6, power_states["summary"]["rejected_pack_conditions"])
        self.assertEqual(0, power_states["summary"]["invariant_violations"])
        self.assertEqual(200, dc_budget["summary"]["rail_profiles_evaluated"])
        self.assertEqual(0, dc_budget["summary"]["failed_profiles"])
        self.assertEqual(2, dc_budget["summary"]["corrected_findings"])
        self.assertEqual(2032, source_budget["summary"]["states_evaluated"])
        self.assertEqual(0, source_budget["summary"]["failed_states"])
        self.assertEqual(14, source_budget["summary"]["source_limited_profiles_explicitly_refused"])
        self.assertEqual("reviewed", dc_result["review_summary"]["phase_status"])
        self.assertEqual(0, dc_result["review_summary"]["unresolved_findings"])
        self.assertEqual(43, audio["review_summary"]["checks"])
        self.assertEqual(4, audio["review_summary"]["corrected_findings"])
        self.assertEqual(0, audio["review_summary"]["unresolved_findings"])
        self.assertEqual(46, ir["review_summary"]["checks"])
        self.assertEqual(4, ir["review_summary"]["corrected_findings"])
        self.assertEqual(0, ir["review_summary"]["unresolved_findings"])
        for relative, expected in freeze["source_hashes"].items():
            actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, relative)
        for artifact in (inventory, methods, power_states, dc_budget, source_budget, dc_result, audio, ir):
            for relative, expected in artifact["source_hashes"].items():
                actual = hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()
                self.assertEqual(expected, actual, relative)
        self.assertFalse(plan["authorization"]["pcb_placement_and_routing"])
        self.assertFalse(plan["authorization"]["fabrication"])
        self.assertFalse(plan["authorization"]["purchasing"])

    def test_h2_1_kicad_scaffold_is_complete_and_contains_no_pcb(self):
        import json

        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-kicad-scaffold.json")
        )
        self.assertEqual("H2.1", manifest["stage"])
        self.assertEqual("reviewed_scaffold", manifest["status"])
        self.assertEqual(4, manifest["summary"]["project_count"])
        self.assertEqual(4, manifest["summary"]["physical_board_count"])
        self.assertEqual(28, manifest["summary"]["sheet_file_count"])
        self.assertEqual(0, manifest["summary"]["pcb_files_created"])
        for relative in manifest["generated_files"]:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)
        for project in manifest["projects"]:
            directory = REPO_ROOT / "hardware/ecad/kicad" / project["id"]
            self.assertTrue((directory / project["project_file"]).is_file())
            self.assertTrue((directory / project["root_file"]).is_file())
            self.assertTrue((directory / project["symbol_table"]).is_file())
            self.assertTrue((directory / project["footprint_table"]).is_file())
        self.assertEqual([], list((REPO_ROOT / "hardware/ecad").rglob("*.kicad_pcb")))

    def test_h2_2_1_ui_root_hierarchy_is_complete_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_root.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI-root-interface.json")
        )
        self.assertEqual("H2.2.1", manifest["stage"])
        self.assertEqual("reviewed_ui_root_hierarchy", manifest["status"])
        self.assertEqual(
            {
                "child_sheet_count": 9,
                "cross_sheet_net_count": 95,
                "root_hierarchical_pin_count": 232,
                "child_hierarchical_label_count": 232,
                "known_child_stub_erc_violations": 0,
                "implemented_child_sheet_count": 9,
                "circuit_symbols_placed": 390,
                "suppressed_generated_library_copy_checks": 390,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        root = self.read("hardware/ecad/kicad/LESHY2-UI/LESHY2-UI.kicad_sch")
        self.assertEqual(9, root.count("\n\t(sheet\n"))
        self.assertEqual(232, root.count("\n\t\t(pin \""))
        self.assertEqual(327, root.count("\n\t(wire\n"))
        self.assertEqual(232, root.count("\n\t(junction "))
        self.assertNotIn("\n\t(label \"", root)
        self.assertNotIn("\n\t(global_label \"", root)
        for row in manifest["sheets"]:
            child = self.read(
                f"hardware/ecad/kicad/LESHY2-UI/{row['id']}.kicad_sch"
            )
            self.assertEqual(
                row["interface_count"],
                child.count("\n\t(hierarchical_label \""),
            )
        for net in (
            "3V3_MAIN", "AON_SAFE_3V3", "S3_USB_DP", "S3_USB_DM",
            "SYS_I2C_SDA", "SYS_I2C_SCL", "FAULT_LATCH_SENSE_AON",
            "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2", "EV_N5_CC",
            "EV_N6_VOICE", "EV_N8_LORA_EXT",
        ):
            self.assertIn(net, {row["name"] for row in manifest["nets"]})

    def test_h2_instance_ledger_accounts_every_circuit_instance(self):
        import json

        ledger = json.loads(
            self.read("hardware/ecad/generated/H2-instance-ledger.json")
        )
        self.assertEqual("H2.0.1", ledger["stage"])
        self.assertEqual(2, ledger["schema_version"])
        self.assertEqual("reviewed_complete_circuit_inventory", ledger["status"])
        summary = ledger["summary"]
        self.assertEqual(1035, summary["registered_inventory_rows"])
        self.assertEqual(1007, summary["main_candidate_instances"])
        self.assertEqual(26, summary["lora_cap_common_instances"])
        self.assertEqual(2, summary["lora_cap_alternative_module_instances"])
        self.assertEqual(182, summary["h1_dimensioned_instances"])
        self.assertEqual(825, summary["schematic_only_main_instances"])
        self.assertEqual(995, summary["main_board_fitted_components"])
        self.assertEqual(6, summary["main_fitted_interconnect_assemblies"])
        self.assertEqual(6, summary["main_external_mating_products"])
        self.assertEqual(28, summary["lora_cap_rows"])
        self.assertEqual(27, summary["lora_cap_components_per_assembled_variant"])
        self.assertEqual(24, summary["owning_sheets_used"])
        self.assertEqual(
            "UI_21_FM_AM_RECEIVER",
            next(row["sheet"] for row in ledger["rows"] if row["instance"] == "receiver"),
        )
        self.assertEqual(0, summary["rows_without_mpn"])
        self.assertEqual(0, summary["rows_without_manufacturer_evidence"])
        self.assertEqual(0, summary["rows_without_sheet_owner"])
        rows = ledger["rows"]
        self.assertEqual(len(rows), len({row["instance_uid"] for row in rows}))
        candidate = json.loads(
            self.read("hardware/architecture/candidates/G2F-3I.json")
        )
        self.assertEqual(
            set(candidate["instances"]),
            {
                row["instance"]
                for row in rows
                if row["project"] != "LESHY2-LORA-CAP-01"
            },
        )
        self.assertEqual(
            {
                "LESHY2-UI": 377,
                "LESHY2-RF": 628,
                "L2-DISP-ADP-001-A": 2,
                "LESHY2-LORA-CAP-01": 28,
            },
            {
                project: sum(row["project"] == project for row in rows)
                for project in {row["project"] for row in rows}
            },
        )
        self.assertEqual(
            ["encoder_knob"],
            [row["instance"] for row in rows if row["contact_count"] == 0],
        )
        self.assertTrue(
            all(row["manufacturer_evidence"]["url"] for row in rows)
        )
        self.assertTrue(
            all(
                row["footprint_source_status"] == "no_product_footprint_interface_only"
                for row in rows
                if row["electrical_disposition"]
                == "external_mating_product_interface_only"
            )
        )

    def test_h2_3_1_rf_power_root_hierarchy_is_complete_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_root.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF-root-interface.json")
        )
        self.assertEqual("H2.3.1", manifest["stage"])
        self.assertEqual("reviewed_rf_power_root_hierarchy", manifest["status"])
        self.assertEqual(
            {
                "child_sheet_count": 12,
                "cross_sheet_net_count": 157,
                "root_hierarchical_pin_count": 381,
                "child_hierarchical_label_count": 381,
                "known_child_stub_erc_violations": 0,
                "implemented_child_sheet_count": 12,
                "circuit_symbols_placed": 682,
                "suppressed_generated_library_copy_checks": 682,
                "known_deferred_fixture_erc_violations": 0,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        root = self.read("hardware/ecad/kicad/LESHY2-RF/LESHY2-RF.kicad_sch")
        self.assertEqual(12, root.count("\n\t(sheet\n"))
        self.assertEqual(381, root.count("\n\t\t(pin \""))
        self.assertEqual(538, root.count("\n\t(wire\n"))
        self.assertEqual(381, root.count("\n\t(junction "))
        self.assertIn('\t(paper "A0" portrait)', root)
        for row in manifest["sheets"]:
            child = self.read(
                f"hardware/ecad/kicad/LESHY2-RF/{row['id']}.kicad_sch"
            )
            self.assertEqual(
                row["interface_count"],
                child.count("\n\t(hierarchical_label \""),
            )
        m1 = next(row for row in manifest["sheets"] if row["id"] == "RF_40_INTERBOARD_M1")
        self.assertEqual(51, m1["interface_count"])

    def test_h2_3_2_exact_usb_pd_charge_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_usb_pd_charge.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF01-usb-pd-charge.json")
        )
        self.assertEqual("H2.3.2", manifest["stage"])
        self.assertEqual("reviewed_exact_usb_pd_charge_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 52,
                "schematic_symbols": 52,
                "board_fitted_symbols": 52,
                "hierarchical_interfaces": 12,
                "physical_package_pads": 208,
                "usb_c_electrical_contacts": 17,
                "usb_port_protector_pads": 21,
                "pd_controller_copper_contacts": 34,
                "vbus_tvs_package_pads": 7,
                "charger_package_pads": 29,
                "configured_cell_count": 2,
                "switching_frequency_khz": 750,
                "intentional_no_connect_pins": 10,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {
                "nvdc_charger.D_MINUS",
                "nvdc_charger.D_PLUS",
                "nvdc_charger.QON",
                "nvdc_charger.STAT",
                "product_usb_connector.A8_SBU1",
                "product_usb_connector.B8_SBU2",
                "product_usb_protector.NC_16",
                "product_usb_protector.NC_17",
                "product_usb_protector.NC_19",
                "product_usb_protector.NC_20",
            },
            set(manifest["intentional_no_connect_endpoints"]),
        )
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_01_USB_PD_CHARGE.kicad_sch"
        )
        self.assertEqual(52, sheet.count("\n\t(symbol\n"))
        self.assertEqual(
            manifest["summary"]["hierarchical_interfaces"],
            sheet.count("\n\t(hierarchical_label \""),
        )
        self.assertEqual(10, sheet.count("\n\t(no_connect "))
        self.assertTrue(all(row["footprint"] for row in manifest["instances"]))

    def test_h2_3_3_exact_pack_safety_aon_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_pack_safety_aon.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF02-pack-safety-aon.json")
        )
        self.assertEqual("H2.3.3", manifest["stage"])
        self.assertEqual("reviewed_exact_pack_safety_aon_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 61,
                "schematic_symbols": 61,
                "board_fitted_symbols": 59,
                "external_cell_interface_symbols": 2,
                "hierarchical_interfaces": 14,
                "physical_package_or_interface_contacts": 198,
                "board_physical_pads": 194,
                "pack_gauge_package_pads": 25,
                "admission_mcu_package_pins": 20,
                "pack_fet_package_pads": 9,
                "diagnostic_timer_package_pads": 17,
                "permanent_admission_service_signals": 5,
                "intentional_no_connect_pins": 6,
                "custom_footprints": 4,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {
                "pack_admission.PA27",
                "pack_admission.PA30",
                "pack_diag_timer.CH1_Q_N",
                "pack_diag_timer.CH2_Q",
                "pack_gauge.ZVC",
                "pack_system_diode.NC",
            },
            set(manifest["intentional_no_connect_endpoints"]),
        )
        self.assertEqual([], manifest["known_deferred_fixture_labels"])
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_02_PACK_SAFETY_AON.kicad_sch"
        )
        self.assertEqual(61, sheet.count("\n\t(symbol\n"))
        self.assertEqual(14, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(6, sheet.count("\n\t(no_connect "))
        admission = next(
            row for row in manifest["instances"] if row["instance"] == "pack_admission"
        )
        self.assertEqual(20, admission["pin_count"])
        self.assertEqual(
            "Package_SO:Texas_DGS0020A_TSSOP-20_3x5.1mm_P0.5mm",
            admission["footprint"],
        )

    def test_h2_3_4_exact_main_rails_domain_gates_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_main_rails_domain_gates.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF03-main-rails-domain-gates.json")
        )
        self.assertEqual("H2.3.4", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_main_rails_domain_gates_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 69,
                "schematic_symbols": 69,
                "board_fitted_symbols": 69,
                "hierarchical_interfaces": 21,
                "physical_package_contacts": 186,
                "aon_buck_package_pins": 8,
                "aon_efuse_package_pads": 7,
                "main_efuse_package_pads": 10,
                "external_efuse_package_pads": 10,
                "independent_switchmode_domains": 3,
                "intentional_no_connect_pins": 3,
                "custom_package_contact_footprints": 2,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {"aon_buck.FB_VSET", "ext_efuse.AUXOFF", "ext_evidence_buffer.NC"},
            set(manifest["intentional_no_connect_endpoints"]),
        )
        self.assertEqual([], manifest["known_deferred_fixture_labels"])
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_03_MAIN_RAILS_DOMAIN_GATES.kicad_sch"
        )
        self.assertEqual(69, sheet.count("\n\t(symbol\n"))
        self.assertEqual(21, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(3, sheet.count("\n\t(no_connect "))
        self.assertTrue(all(row["footprint"] for row in manifest["instances"]))

    def test_h2_3_5_exact_rp2354_core_service_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_rp2354_core_service.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF30-rp2354-core-service.json")
        )
        self.assertEqual("H2.3.5", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_rp2354_core_service_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 48,
                "schematic_symbols": 48,
                "board_fitted_symbols": 48,
                "hierarchical_interfaces": 52,
                "physical_package_contacts": 219,
                "rp2354_package_contacts": 81,
                "dedicated_100nf_supply_bypasses": 14,
                "reference_4_7uf_caps": 4,
                "intentional_no_connect_pins": 13,
                "custom_footprints": 1,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {
                "rp.QSPI_SD3", "rp.QSPI_SCLK", "rp.QSPI_SD0",
                "rp.QSPI_SD2", "rp.QSPI_SD1",
                "rp_service_usb_switch.HSD2_PLUS",
                "rp_service_usb_switch.HSD2_MINUS",
                "rp_service_usb_connector.A8_SBU1",
                "rp_service_usb_connector.B8_SBU2",
                "rp_dbg_esd.NC_6", "rp_dbg_esd.NC_7",
                "rp_dbg_esd.NC_9", "rp_dbg_esd.NC_10",
            },
            set(manifest["intentional_no_connect_endpoints"]),
        )
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_30_RP2354_CORE_SERVICE.kicad_sch"
        )
        self.assertEqual(48, sheet.count("\n\t(symbol\n"))
        self.assertEqual(
            manifest["summary"]["hierarchical_interfaces"],
            sheet.count("\n\t(hierarchical_label \""),
        )
        self.assertEqual(13, sheet.count("\n\t(no_connect "))
        rp = next(row for row in manifest["instances"] if row["instance"] == "rp")
        self.assertEqual(81, rp["pin_count"])
        self.assertTrue(all(row["footprint"] for row in manifest["instances"]))

    def test_h2_3_6_exact_three_nrf24_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_nrf24_x3.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF31-nrf24-x3.json")
        )
        self.assertEqual("H2.3.6", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_three_nrf24_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 105,
                "schematic_symbols": 108,
                "board_fitted_symbols": 102,
                "hierarchical_interfaces": 33,
                "physical_package_contacts": 311,
                "nrf_carrier_pads": 24,
                "factory_rf_assembly_boundaries": 3,
                "independent_spi_paths": 3,
                "independent_rf_paths": 3,
                "intentional_no_connect_pins": 2,
                "custom_footprints": 3,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {"nrf_evidence_hold_diode.NC", "nrf_power_switch.NC"},
            set(manifest["intentional_no_connect_endpoints"]),
        )
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_31_NRF24_X3.kicad_sch"
        )
        self.assertEqual(108, sheet.count("\n\t(symbol\n"))
        self.assertEqual(33, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(2, sheet.count("\n\t(no_connect "))
        for radio in ("nrf0", "nrf1", "nrf2"):
            module = next(
                row for row in manifest["instances"] if row["instance"] == radio
            )
            boundary = next(
                row for row in manifest["instances"]
                if row["instance"] == f"{radio}_factory_ipex"
            )
            self.assertEqual(8, module["pin_count"])
            self.assertTrue(module["footprint"])
            self.assertFalse(boundary["board_fitted"])
            self.assertFalse(boundary["ledger_component"])
        self.assertIn("RF_31_NRF24_X3", self.read("docs/schematics.md"))
        self.assertIn("RF_31_NRF24_X3", self.read("docs/schematics.ru.md"))

    def test_h2_3_7_exact_subghz_voice_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_subghz_voice.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF32-subghz-voice.json")
        )
        self.assertEqual("H2.3.7", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_electrical_subghz_voice_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 116,
                "schematic_symbols": 116,
                "board_fitted_symbols": 116,
                "hierarchical_interfaces": 32,
                "physical_package_contacts": 363,
                "cc1101_package_contacts": 21,
                "sa518_module_contacts": 20,
                "independent_rf_paths": 2,
                "intentional_no_connect_pins": 11,
                "known_deferred_fixture_boundaries": 0,
                "custom_footprints": 3,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {
                "cc_balun.DNC_5", "cc_balun.DNC_6", "cc_host_buffer.4Y",
                "cc_power_switch.NC", "cc_return_buffer.4Y", "voice.NC_15",
                "voice.NC_5", "voice.NC_6", "voice.VOXEN",
                "voice_hl_driver.NC", "voice_io_power_switch.NC",
            },
            set(manifest["intentional_no_connect_endpoints"]),
        )
        self.assertEqual([], manifest["known_deferred_fixture_labels"])
        cc_switch = next(
            row for row in manifest["instances"] if row["instance"] == "cc_power_switch"
        )
        self.assertEqual(6, cc_switch["pin_count"])
        voice = next(row for row in manifest["instances"] if row["instance"] == "voice")
        self.assertEqual("h5_received_module_land_fit_required", voice["footprint_status"])
        self.assertTrue(all(row["footprint"] for row in manifest["instances"]))
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_32_SUBGHZ_VOICE.kicad_sch"
        )
        self.assertEqual(116, sheet.count("\n\t(symbol\n"))
        self.assertEqual(32, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(11, sheet.count("\n\t(no_connect "))
        self.assertIn("RF_32_SUBGHZ_VOICE", self.read("docs/schematics.md"))
        self.assertIn("RF_32_SUBGHZ_VOICE", self.read("docs/schematics.ru.md"))

    def test_h2_3_8_exact_u214_m5_expansion_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_u214_m5_ext.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF34-u214-m5-ext.json")
        )
        self.assertEqual("H2.3.8", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_u214_m5_expansion_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 53,
                "schematic_symbols": 53,
                "board_fitted_symbols": 52,
                "external_mating_product_symbols": 1,
                "hierarchical_interfaces": 27,
                "physical_package_or_interface_contacts": 228,
                "board_physical_contacts": 214,
                "u214_cap_bus_contacts": 14,
                "native_unit_contacts": 4,
                "independent_protected_power_branches": 2,
                "intentional_no_connect_pins": 22,
                "custom_footprints": 1,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        cap = next(row for row in manifest["instances"] if row["instance"] == "u214")
        self.assertFalse(cap["board_fitted"])
        self.assertEqual("", cap["footprint"])
        host = next(
            row for row in manifest["instances"]
            if row["instance"] == "u214_connector"
        )
        self.assertTrue(host["board_fitted"])
        self.assertIn("Samtec_HLE-107", host["footprint"])
        unit = next(
            row for row in manifest["instances"]
            if row["instance"] == "unit_connector"
        )
        self.assertEqual("Leshy2:1125R-SMT-4P", unit["footprint"])
        self.assertEqual(3, len(manifest["connector_cad_cross_checks"]))
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_34_U214_M5_EXT.kicad_sch"
        )
        self.assertEqual(53, sheet.count("\n\t(symbol\n"))
        self.assertEqual(27, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(22, sheet.count("\n\t(no_connect "))
        self.assertIn("RF_34_U214_M5_EXT", self.read("docs/schematics.md"))
        self.assertIn("RF_34_U214_M5_EXT", self.read("docs/schematics.ru.md"))

    def test_h2_3_9_exact_rear_controls_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_rear_controls.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF35-rear-controls.json")
        )
        self.assertEqual("H2.3.9", manifest["stage"])
        self.assertEqual("reviewed_exact_rear_controls_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 8,
                "schematic_symbols": 7,
                "board_fitted_symbols": 7,
                "external_mechanical_mating_items": 1,
                "hierarchical_interfaces": 6,
                "board_physical_contacts": 36,
                "independent_direct_control_paths": 4,
                "intentional_no_connect_pins": 12,
                "custom_footprints_added": 0,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            [
                {
                    "instance": "encoder_knob",
                    "mpn": "Davies Molding 1227-J",
                    "role": "exact soft-touch knob over rear encoder",
                    "schematic_symbol": False,
                    "board_footprint": False,
                }
            ],
            manifest["external_mechanical_mating_items"],
        )
        encoder = next(
            row for row in manifest["instances"] if row["instance"] == "encoder"
        )
        self.assertIn("EC11E-Switch", encoder["footprint"])
        self.assertEqual(5, encoder["pin_count"])
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_35_REAR_CONTROLS.kicad_sch"
        )
        self.assertEqual(7, sheet.count("\n\t(symbol\n"))
        self.assertEqual(6, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(12, sheet.count("\n\t(no_connect "))
        self.assertNotIn("STOP", sheet)
        self.assertNotIn("REARM", sheet)
        self.assertIn("RF_35_REAR_CONTROLS", self.read("docs/schematics.md"))
        self.assertIn("RF_35_REAR_CONTROLS", self.read("docs/schematics.ru.md"))

    def test_h2_3_10_exact_audio_io_amplifier_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_audio_io_amp.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF36-audio-io-amp.json")
        )
        self.assertEqual("H2.3.10", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_audio_io_amplifier_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 14,
                "schematic_symbols": 14,
                "board_fitted_symbols": 13,
                "fitted_interconnect_assemblies": 1,
                "hierarchical_interfaces": 7,
                "physical_package_or_interface_contacts": 34,
                "board_component_contacts": 32,
                "floating_btl_output_branches": 2,
                "intentional_no_connect_pins": 1,
                "custom_footprints": 3,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        amplifier = next(
            row for row in manifest["instances"] if row["instance"] == "speaker_amp"
        )
        self.assertIn("PAM8302AAYCR", amplifier["mpn"])
        self.assertIn("UDFN3030", amplifier["footprint"])
        speaker = next(
            row for row in manifest["instances"] if row["instance"] == "speaker"
        )
        self.assertEqual("fitted_interconnect_assembly", speaker["electrical_disposition"])
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_36_AUDIO_IO_AMP.kicad_sch"
        )
        self.assertEqual(14, sheet.count("\n\t(symbol\n"))
        self.assertEqual(7, sheet.count("\n\t(hierarchical_label \""))
        self.assertEqual(1, sheet.count("\n\t(no_connect "))
        self.assertIn("RF_36_AUDIO_IO_AMP", self.read("docs/schematics.md"))
        self.assertIn("RF_36_AUDIO_IO_AMP", self.read("docs/schematics.ru.md"))

    def test_h2_3_11_exact_rf_interboard_m1_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_interboard_m1.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        rf = json.loads(
            self.read("hardware/ecad/generated/H2-RF40-interboard-m1.json")
        )
        ui = json.loads(
            self.read("hardware/ecad/generated/H2-UI40-interboard-m1.json")
        )
        self.assertEqual("H2.3.11", rf["stage"])
        self.assertEqual("reviewed_exact_rf_interboard_m1_sheet", rf["status"])
        self.assertEqual(
            {
                "ledger_instances": 1,
                "schematic_symbols": 1,
                "board_fitted_symbols": 1,
                "physical_contacts": 80,
                "unique_nets": 51,
                "hierarchical_interfaces": 51,
                "power_ground_contacts": 20,
                "main_3v3_contacts": 7,
                "reserved_contacts": 0,
                "cross_project_contact_mismatches": 0,
                "intentional_no_connect_pins": 0,
                "pcb_files_created": 0,
            },
            rf["summary"],
        )
        self.assertEqual(ui["contacts"], rf["contacts"])
        self.assertEqual(list(range(1, 81)), [row["contact"] for row in rf["contacts"]])
        connector = rf["instances"][0]
        self.assertIn("FX8C-80S-SV5", connector["mpn"])
        self.assertIn("Hirose_FX8-80S-SV", connector["footprint"])
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_40_INTERBOARD_M1.kicad_sch"
        )
        self.assertEqual(1, sheet.count("\n\t(symbol\n"))
        self.assertEqual(51, sheet.count("\n\t(hierarchical_label \""))
        self.assertIn("RF_40_INTERBOARD_M1", self.read("docs/schematics.md"))
        self.assertIn("RF_40_INTERBOARD_M1", self.read("docs/schematics.ru.md"))

    def test_h2_3_12_exact_rf_tx_safety_evidence_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_tx_safety_evidence.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF50-tx-safety-evidence.json")
        )
        self.assertEqual("H2.3.12", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_rf_tx_safety_evidence_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 101,
                "schematic_symbols": 101,
                "board_fitted_symbols": 101,
                "hierarchical_interfaces": 74,
                "physical_contacts": 380,
                "rf_detector_channels": 5,
                "comparator_channels": 5,
                "independent_watchdogs": 2,
                "tx_gate_packages": 3,
                "evidence_mask_inputs": 9,
                "custom_footprints": 1,
                "intentional_no_connect_pins": 22,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            22, len(set(manifest["intentional_no_connect_endpoints"]))
        )
        for instance in manifest["instances"]:
            self.assertTrue(instance["footprint"], instance["instance"])
        detector = next(
            row for row in manifest["instances"] if row["instance"] == "det_nrf0"
        )
        self.assertIn("LFCSP-8-1EP_3x2mm", detector["footprint"])
        self.assertEqual(9, detector["pin_count"])
        footprint = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/JS102011SCQN.kicad_mod"
        )
        self.assertIn("8.5x3.5-mm", footprint)
        self.assertEqual(3, footprint.count("\n\t(pad \""))
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_50_TX_SAFETY_EVIDENCE.kicad_sch"
        )
        self.assertEqual(101, sheet.count("\n\t(symbol\n"))
        self.assertEqual(
            manifest["summary"]["hierarchical_interfaces"],
            sheet.count("\n\t(hierarchical_label \""),
        )
        self.assertEqual(22, sheet.count("\n\t(no_connect "))
        self.assertIn("RF_50_TX_SAFETY_EVIDENCE", self.read("docs/schematics.md"))
        self.assertIn("RF_50_TX_SAFETY_EVIDENCE", self.read("docs/schematics.ru.md"))

    def test_h2_3_13_exact_rf_testpoints_sheet_is_reviewed(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_rf_testpoints_manufacturing.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check", "--kicad-check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-RF60-testpoints-manufacturing.json")
        )
        self.assertEqual("H2.3.13", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_rf_testpoints_manufacturing_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 0,
                "schematic_symbols": 52,
                "board_fitted_symbols": 52,
                "bom_symbols": 0,
                "physical_test_pads": 52,
                "hierarchical_interfaces": 52,
                "programming_recovery_pads": 13,
                "rf_evidence_pads": 6,
                "intentional_no_connect_pins": 0,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            manifest["summary"]["physical_test_pads"],
            len({row["symbol_uuid"] for row in manifest["instances"]}),
        )
        self.assertTrue(all(row["mpn"] is None for row in manifest["instances"]))
        self.assertTrue(all(not row["in_bom"] for row in manifest["instances"]))
        self.assertEqual(
            "TestPoint:TestPoint_Pad_D1.0mm",
            {row["footprint"] for row in manifest["instances"]}.pop(),
        )
        sheet = self.read(
            "hardware/ecad/kicad/LESHY2-RF/RF_60_TESTPOINTS_MANUFACTURING.kicad_sch"
        )
        self.assertEqual(
            manifest["summary"]["schematic_symbols"],
            sheet.count("\n\t(symbol\n"),
        )
        self.assertEqual(
            manifest["summary"]["hierarchical_interfaces"],
            sheet.count("\n\t(hierarchical_label \""),
        )
        self.assertEqual(
            manifest["summary"]["schematic_symbols"]
            - manifest["summary"]["bom_symbols"],
            sheet.count("\n\t\t(in_bom no)"),
        )
        self.assertIn("RF_60_TESTPOINTS_MANUFACTURING", self.read("docs/schematics.md"))
        self.assertIn("RF_60_TESTPOINTS_MANUFACTURING", self.read("docs/schematics.ru.md"))

    def test_h2_2_2_exact_s3_core_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_s3_core.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI10-S3-core.json")
        )
        self.assertEqual("H2.2.2", manifest["stage"])
        self.assertEqual("reviewed_exact_s3_core_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 32,
                "schematic_symbols": 33,
                "assembly_interface_symbols": 1,
                "s3_carrier_pads": 41,
                "hierarchical_interfaces": 39,
                "intentional_no_connect_pins": 7,
                "custom_footprints": 3,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            {str(index) for index in range(1, 42)},
            set(manifest["s3_pad_contract"]["pads"]),
        )
        self.assertEqual(
            33,
            len({row["symbol_uuid"] for row in manifest["instances"]}),
        )
        sma = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/RFPC-SMA32-FN-175-A.kicad_mod"
        )
        self.assertEqual(3, sma.count('(layers "F.Cu" "F.Paste" "F.Mask")'))
        self.assertEqual(2, sma.count('(layers "B.Cu" "B.Paste" "B.Mask")'))

    def test_h2_2_3_exact_display_touch_storage_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_display_touch_storage.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI11-display-touch-storage.json")
        )
        self.assertEqual("H2.2.3", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_display_touch_storage_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 49,
                "schematic_symbols": 49,
                "board_fitted_symbols": 47,
                "external_assembly_interface_symbols": 2,
                "display_contacts": 40,
                "microsd_socket_contacts": 11,
                "hierarchical_interfaces": 18,
                "intentional_no_connect_pins": 33,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            "3V3_MAIN", manifest["physical_net_aliases_collapsed"]["LCD_VDDI_3V3"]
        )
        self.assertEqual(
            "POWER_GROUND", manifest["physical_net_aliases_collapsed"]["SD_SHIELD_GROUND"]
        )
        sd = next(row for row in manifest["instances"] if row["instance"] == "sd")
        self.assertIn("DM3AT-SF-PEJM5", sd["footprint"])
        self.assertEqual(49, len({row["symbol_uuid"] for row in manifest["instances"]}))

    def test_h2_2_4_exact_controls_indicators_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_controls_indicators.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI12-controls-indicators.json")
        )
        self.assertEqual("H2.2.4", manifest["stage"])
        self.assertEqual("reviewed_exact_controls_indicators_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 71,
                "schematic_symbols": 71,
                "board_fitted_symbols": 71,
                "hierarchical_interfaces": 45,
                "slow_io_contacts": 33,
                "matrix_io_contacts": 24,
                "serial_tactile_switches": 15,
                "actual_tx_indicators": 9,
                "fault_indicators": 1,
                "custom_footprints": 3,
                "intentional_no_connect_pins": 3,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            "SAFETY_GROUND",
            manifest["physical_net_aliases_collapsed"]["FAULT_LED_K"],
        )
        self.assertEqual(
            [
                "front_function_esd.IO8",
                "slow_io_fault_sense_iso.NC",
                "slow_io_s3_evidence_iso.NC",
            ],
            manifest["intentional_no_connect_endpoints"],
        )
        self.assertEqual(71, len({row["symbol_uuid"] for row in manifest["instances"]}))
        instances = {row["instance"] for row in manifest["instances"]}
        self.assertIn("fault_led", instances)
        self.assertNotIn("any_tx_led", instances)
        b3s = self.read("hardware/ecad/libraries/Leshy2.pretty/B3S-1100P.kicad_mod")
        self.assertTrue(all(f'(pad "{number}"' in b3s for number in range(1, 6)))

    def test_h2_2_5_exact_audio_codec_headset_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_audio_codec_headset.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI13-audio-codec-headset.json")
        )
        self.assertEqual("H2.2.5", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_audio_codec_headset_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 104,
                "schematic_symbols": 104,
                "board_fitted_symbols": 104,
                "hierarchical_interfaces": 24,
                "codec_contacts": 21,
                "headset_contacts": 6,
                "analog_selectors": 5,
                "io_isolators_and_boot_gate": 6,
                "custom_footprints": 1,
                "intentional_no_connect_pins": 8,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            [
                "codec.MCLK",
                "codec_power_switch.NC",
                "headphone_esd.D2_MINUS",
                "headphone_esd.NC_10",
                "headphone_esd.NC_6",
                "headphone_esd.NC_7",
                "headphone_esd.NC_9",
                "headphone_jack.RING1_SWITCH",
            ],
            manifest["intentional_no_connect_endpoints"],
        )
        aliases = manifest["physical_net_aliases_collapsed"]
        self.assertEqual("CODEC_DAC_OUT_P", aliases["CODEC_HP_L_RAW"])
        self.assertEqual("3V3_CODEC_SWITCHED", aliases["CODEC_QOD"])
        self.assertEqual("AUDIO_GROUND", aliases["HEADSET_RING2_GROUND"])
        self.assertEqual(104, len({row["symbol_uuid"] for row in manifest["instances"]}))
        jack = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/SJ-43504-SMT-TR.kicad_mod"
        )
        self.assertTrue(all(f'(pad "{number}"' in jack for number in range(1, 7)))

    def test_h2_2_6_exact_c5_radio_ir_service_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_c5_radio_ir_service.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI20-c5-radio-ir-service.json")
        )
        self.assertEqual("H2.2.6", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_c5_radio_ir_service_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 60,
                "schematic_symbols": 61,
                "board_fitted_symbols": 59,
                "hierarchical_interfaces": 18,
                "c5_carrier_pads": 32,
                "factory_rf_assembly_boundaries": 1,
                "ir_receiver_channels": 2,
                "custom_footprints": 6,
                "intentional_no_connect_pins": 18,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertIn("c5.ANT2", manifest["intentional_no_connect_endpoints"])
        self.assertIn("c5.NC_PSRAM_GPIO15", manifest["intentional_no_connect_endpoints"])
        self.assertEqual(
            61, len({row["symbol_uuid"] for row in manifest["instances"]})
        )
        module = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/ESP32-C5-WROOM-1U.kicad_mod"
        )
        self.assertTrue(all(f'(pad "{number}"' in module for number in range(1, 33)))
        self.assertIn('"c5_factory_ant1"', json.dumps(manifest))

    def test_h2_2_7_exact_fm_am_receiver_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_fm_am_receiver.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI21-fm-am-receiver.json")
        )
        self.assertEqual("H2.2.7", manifest["stage"])
        self.assertEqual("reviewed_exact_fm_am_receiver_sheet", manifest["status"])
        self.assertEqual(
            {
                "ledger_instances": 32,
                "schematic_symbols": 32,
                "board_fitted_symbols": 32,
                "hierarchical_interfaces": 8,
                "receiver_contacts": 16,
                "external_receive_ports": 2,
                "custom_footprints": 2,
                "intentional_no_connect_pins": 4,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            ["receiver.GPO1", "receiver.NC", "receiver_irq_iso.NC", "receiver_power_switch.NC"],
            manifest["intentional_no_connect_endpoints"],
        )
        aliases = manifest["physical_net_aliases_collapsed"]
        self.assertEqual("POWER_GROUND", aliases["RX_FMSW_SMA_RF_GROUND"])
        self.assertEqual("POWER_GROUND", aliases["RX_AMLW_ESD_GROUND"])
        crystal = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/FC-135-Q13FC13500005.kicad_mod"
        )
        self.assertIn('(pad "1" smd roundrect (at -1.250 0.000)', crystal)
        self.assertIn('(pad "2" smd roundrect (at 1.250 0.000)', crystal)

    def test_h2_2_8_exact_ui_interboard_m1_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_interboard_m1.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI40-interboard-m1.json")
        )
        self.assertEqual("H2.2.8", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_ui_interboard_m1_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 1,
                "schematic_symbols": 1,
                "board_fitted_symbols": 1,
                "physical_contacts": 80,
                "unique_nets": 51,
                "hierarchical_interfaces": 51,
                "power_ground_contacts": 20,
                "main_3v3_contacts": 7,
                "reserved_contacts": 0,
                "intentional_no_connect_pins": 0,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(list(range(1, 81)), [row["contact"] for row in manifest["contacts"]])
        self.assertEqual(80, len({row["symbol_pin"] for row in manifest["contacts"]}))
        self.assertEqual(
            "Connector_Hirose_FX8:Hirose_FX8-80P-SV_2x40_P0.6mm",
            manifest["instances"][0]["footprint"],
        )

    def test_h2_2_9_exact_ui_tx_safety_evidence_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_tx_safety_evidence.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI50-tx-safety-evidence.json")
        )
        self.assertEqual("H2.2.9", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_ui_tx_safety_evidence_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 28,
                "schematic_symbols": 28,
                "board_fitted_symbols": 28,
                "hierarchical_interfaces": 18,
                "physical_contacts": 83,
                "rf_detector_channels": 2,
                "optical_detector_channels": 1,
                "comparator_channels": 4,
                "reset_sink_channels": 2,
                "custom_footprints": 1,
                "intentional_no_connect_pins": 1,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(
            ["evidence_cmp_a.OUT4"], manifest["intentional_no_connect_endpoints"]
        )
        schematic = self.read(
            "hardware/ecad/kicad/LESHY2-UI/UI_50_TX_SAFETY_EVIDENCE.kicad_sch"
        )
        self.assertNotIn("S3_RF_TX_EVIDENCE_AON_N", schematic)
        footprint = self.read(
            "hardware/ecad/libraries/Leshy2.pretty/VEMD1060X01.kicad_mod"
        )
        self.assertIn('(pad "1" smd roundrect (at -0.800 0.000)', footprint)
        self.assertIn('(pad "2" smd roundrect (at 0.800 0.000)', footprint)

    def test_h2_2_10_exact_ui_testpoints_sheet_is_reviewed_and_current(self):
        import json

        script = REPO_ROOT / "hardware/ecad/h2_ui_testpoints_manufacturing.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = json.loads(
            self.read("hardware/ecad/generated/H2-UI60-testpoints-manufacturing.json")
        )
        self.assertEqual("H2.2.10", manifest["stage"])
        self.assertEqual(
            "reviewed_exact_ui_testpoints_manufacturing_sheet", manifest["status"]
        )
        self.assertEqual(
            {
                "ledger_instances": 0,
                "schematic_symbols": 11,
                "board_fitted_symbols": 11,
                "bom_symbols": 0,
                "physical_test_pads": 11,
                "hierarchical_interfaces": 11,
                "intentional_no_connect_pins": 0,
                "pcb_files_created": 0,
            },
            manifest["summary"],
        )
        self.assertEqual(11, len({row["symbol_uuid"] for row in manifest["instances"]}))
        self.assertTrue(all(row["mpn"] is None for row in manifest["instances"]))
        self.assertTrue(all(not row["in_bom"] for row in manifest["instances"]))
        self.assertEqual(
            "TestPoint:TestPoint_Pad_D1.0mm",
            {row["footprint"] for row in manifest["instances"]}.pop(),
        )

    def test_h2_hwfw_export_has_all_target_pins_and_service_boundaries(self):
        import json

        export = json.loads(
            self.read("hardware/ecad/generated/H2-hwfw-contract.json")
        )
        self.assertEqual("H2.0.3", export["stage"])
        self.assertEqual("reviewed_hwfw_export", export["status"])
        self.assertEqual("LESHY2-H2-HWFW-1", export["export_id"])
        self.assertFalse(export["bsp"]["temporary_pin_assignments_allowed"])
        self.assertEqual(125, export["bsp"]["total_allocated_contacts"])
        self.assertEqual(
            {"S3": 33, "C5": 14, "RP": 48, "PACK": 13, "SAFETY": 17},
            {
                domain["domain"]: domain["allocated_contact_count"]
                for domain in export["bsp"]["domains"]
            },
        )
        integration = export["integration_contract"]
        self.assertEqual(2, integration["schema"])
        self.assertEqual("h2_0_3_reviewed", integration["review_status"])
        service = integration["physical_service"]
        self.assertEqual(
            ["USB / POWER", "C5 SERVICE USB", "RP SERVICE USB"],
            [row["label"] for row in service["external_usb"]],
        )
        self.assertEqual(6, len(service["external_side_controls"]))
        self.assertTrue(
            all(row["access"] == "open_sandwich_only" for row in service["internal_fallback_headers"])
        )

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
            'data-review-gate="H1.3.1" data-review-status="reviewed"',
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
            "Леший",
            "ESP32-LESHY2",
            "github.com/anton-vinogradov/esp32-leshy2",
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
            "FAULT",
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
            "S3 RST",
            "S3 BOOT",
            "C5 RST",
            "C5 BOOT",
            "RP RST",
            "RP BOOT",
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

    def test_mockup_text_regions_do_not_regress_into_known_collisions(self):
        import xml.etree.ElementTree as ET

        namespace = "{http://www.w3.org/2000/svg}"

        service = ET.fromstring(self.read("docs/images/service-access.svg"))
        self.assertEqual("0 0 1300 690", service.attrib["viewBox"])
        rear = next(
            node
            for node in service.iter(f"{namespace}rect")
            if node.attrib.get("data-face") == "rear-outer"
        )
        rear_right = float(rear.attrib["x"]) + float(rear.attrib["width"])
        note_text = {
            node.text: float(node.attrib["x"])
            for node in service.iter(f"{namespace}text")
            if node.text in {"S3", "C5", "RP", "Port roles", "Inside after opening"}
        }
        self.assertEqual(5, len(note_text))
        self.assertGreaterEqual(min(note_text.values()) - rear_right, 40.0)
        service_buttons = {
            node.attrib["data-instance"]: node
            for node in service.iter(f"{namespace}rect")
            if node.attrib.get("data-recessed") == "true"
        }
        service_labels = {
            node.attrib["data-instance"]: node
            for node in service.iter(f"{namespace}text")
            if node.attrib.get("data-role") == "service-control-label"
        }
        self.assertEqual(set(service_buttons), set(service_labels))
        for instance, label in service_labels.items():
            button = service_buttons[instance]
            button_centre = float(button.attrib["y"]) + float(button.attrib["height"]) / 2
            label_centre = float(label.attrib["y"]) - float(label.attrib["font-size"]) / 3
            self.assertAlmostEqual(button_centre, label_centre, places=1, msg=instance)

        internal = ET.fromstring(self.read("docs/images/internal-board-layout.svg"))
        internal_text = list(internal.iter(f"{namespace}text"))
        inner_title = next(
            node
            for node in internal_text
            if node.text == "Front/display PCB — inner side (not user-facing)"
        )
        self.assertGreaterEqual(float(inner_title.attrib["y"]), 100.0)
        for number in ("34", "35", "36"):
            self.assertEqual(1, sum(node.text == number for node in internal_text))

        adapter = ET.fromstring(self.read("docs/images/display-adapter.svg"))
        display_fpc = next(
            node
            for node in adapter.iter(f"{namespace}text")
            if node.text == "DISPLAY FPC"
        )
        self.assertEqual("end", display_fpc.attrib["text-anchor"])
        self.assertGreaterEqual(float(display_fpc.attrib["x"]), 80.0)

        external = ET.fromstring(self.read("docs/images/current-clamshell.svg"))
        holder_labels = [
            node
            for node in external.iter(f"{namespace}text")
            if node.text and node.text.startswith("Keystone 1048P")
        ]
        self.assertEqual(1, len(holder_labels))
        self.assertGreaterEqual(float(holder_labels[0].attrib["y"]), 610.0)

    def test_external_face_acceptance_package_is_complete(self):
        import json

        package = json.loads(
            self.read("hardware/product-design/generated/H1-external-face-acceptance.json")
        )
        self.assertEqual("H1.3.0", package["stage"])
        self.assertEqual("H1.3.1", package["review_gate"])
        self.assertEqual("reviewed", package["status"])
        self.assertEqual("L2-ASM-COORD-001-A", package["coordinate_model"])
        self.assertEqual([75.0, 150.0], package["front"]["board_outline_mm"])
        self.assertEqual([75.0, 150.0], package["rear"]["board_outline_mm"])
        self.assertEqual(
            {"text": "Леший", "position_mm": [37.5, 99.5], "font_size_px_at_drawing_scale": 10.5},
            package["front"]["product_silkscreen"],
        )
        self.assertEqual(
            {"text": "ESP32-LESHY2", "position_mm": [37.5, 136.0], "font_size_px_at_drawing_scale": 7.5},
            package["rear"]["product_silkscreen"],
        )
        self.assertEqual(
            {
                "text": "github.com/anton-vinogradov/esp32-leshy2",
                "position_mm": [37.5, 142.0],
                "font_size_px_at_drawing_scale": 5.0,
            },
            package["rear"]["project_url_silkscreen"],
        )
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
        status_indicators = package["front"]["status_indicators"]
        self.assertEqual(9, len(indicators))
        self.assertEqual(1, len(status_indicators))
        self.assertEqual("fault_led", status_indicators[0]["instance"])
        self.assertEqual("FAULT_KILL hardware latch", status_indicators[0]["source"])
        self.assertEqual(
            {(row, column) for row in (1, 2) for column in range(1, 6)},
            {
                (item["row"], item["column"])
                for item in indicators + status_indicators
            },
        )
        self.assertTrue(all(package["machine_checks"].values()))
        self.assertEqual(4, len(package["front"]["service_side_controls"]))
        self.assertEqual(2, len(package["rear"]["service_side_controls"]))
        self.assertEqual(
            {"s3_dbg_header", "c5_dbg_header", "rp_dbg_header"},
            {
                item["instance"]
                for item in package["internal_fallback_diagnostics"]["headers"]
            },
        )

    def test_cross_view_acceptance_reconciles_physical_and_pin_fit(self):
        import json

        package = json.loads(
            self.read("hardware/product-design/generated/H1-cross-view-acceptance.json")
        )
        self.assertEqual("H1.7.0", package["stage"])
        self.assertEqual("reviewed", package["status"])
        self.assertEqual("H1.7.1", package["review_gate"])
        self.assertEqual(
            {"gate": "H1.8", "status": "accepted", "date": "2026-08-23"},
            {
                key: package["final_acceptance"][key]
                for key in ("gate", "status", "date")
            },
        )
        physical = package["physical_fit"]
        self.assertEqual("paper_geometry_passed", physical["result"])
        self.assertEqual(131, physical["inner_body_count"])
        self.assertEqual(133, physical["total_inner_component_count_including_adapter"])
        self.assertEqual(3.31, physical["minimum_opposing_pair"]["remaining_z_clearance_mm"])
        self.assertTrue(physical["five_rf_microcoaxes_accounted"])
        self.assertEqual(9, physical["nine_outward_rf_ports"])
        pins = package["pin_resource_fit"]
        self.assertEqual("paper_pin_and_contact_fit_passed", pins["result"])
        self.assertEqual(33, pins["direct_allocation_counts"]["s3"])
        self.assertEqual([], pins["free_gpio"]["s3"])
        self.assertEqual(["GPIO5"], pins["free_gpio"]["c5"])
        self.assertEqual(24, pins["main_slow_io"]["used"])
        self.assertEqual(16, pins["ui_input_expander"]["used"])
        self.assertEqual(7, len(pins["headset_control_expander"]["pulled_local_reserves"]))
        self.assertEqual({"positions": 80, "assigned": 80, "reserved_no_connect": 0}, pins["m1"])
        self.assertFalse(package["not_claimed"]["production_schematic_complete"])
        self.assertTrue(package["not_claimed"]["production_schematic_authorized"])
        self.assertFalse(
            package["not_claimed"]["pcb_placement_and_routing_authorized"]
        )
        self.assertFalse(package["not_claimed"]["purchase_authorized"])
        for name in ("docs/hardware.md", "docs/hardware.ru.md"):
            page = self.read(name).replace(",", ".")
            for token in (
                "H1-cross-view-acceptance.json", "3.31", "0.7", "80", "GPIO5",
            ):
                self.assertIn(token, page, f"{name}: {token}")

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
            "Front/display PCB — inner side (not user-facing)",
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
            "SKRTLAE010",
            "FTSH-105-01-L-DV-K-P-TR",
            "TE Connectivity 2118651-2",
            'data-instance="s3_rf_jumper" data-projected-chord-mm="14.78" data-assembly-length-mm="30.00" data-unprojected-slack-mm="15.22"',
            'data-instance="c5_rf_jumper" data-projected-chord-mm="15.50" data-assembly-length-mm="30.00" data-unprojected-slack-mm="14.50"',
            " · SPK",
            'data-inner-body-count="131"',
            'data-max-inner-height-mm="8.95"',
            'data-min-single-body-clearance-mm="2.05"',
            'data-display-adapter-opposing-pairs="5"',
            'data-min-display-adapter-clearance-mm="6.00"',
            'data-opposing-pairs="35"',
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
            "all 131 inner bodies checked individually; tallest 8.95 mm; opposite-plane remainder 2.05 mm",
            "complete 3.80-mm display adapter: 5 opposing crossings; minimum Z gap 6.00 mm",
            "opposing inner faces: 35 non-mating XY pairs checked; minimum Z gap 3.31 mm",
            "RF coax: 2 direct exact-endpoint projections + 3 nRF module-face reserves; all five 30-mm assemblies accounted",
            "nRF reserve crossings: 5; minimum Z gap 5.20 mm",
            "EC11E through-board features: 7 checked; 2 opposing crossings; minimum Z gap 4.20 mm",
            "limiting pair: 21 3.5-mm CTIA headset TRRS mid-mount connector / 120 protected-pack branch fuse #0",
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
            self.assertIn("current-clamshell.svg?layout=19", page)
            self.assertIn("navigation-cluster.svg?layout=1", page)
            self.assertIn("internal-board-layout.svg?layout=18", page)
            self.assertIn("sandwich-section.svg?layout=11", page)
            self.assertIn("top-edge-view.svg?layout=5", page)
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
        self.assertEqual(131, audit["inner_body_count"])
        self.assertEqual(133, audit["total_inner_component_count_including_adapter"])
        self.assertTrue(audit["all_inner_bodies_have_sourced_positive_height"])
        self.assertTrue(audit["no_inner_body_exceeds_gap"])
        self.assertTrue(audit["no_inner_body_violates_minimum_clearance"])
        self.assertEqual(8.95, audit["tallest_inner_body"]["height_mm"])
        self.assertEqual(2.05, audit["tallest_inner_body"]["remaining_to_opposite_pcb_plane_mm"])
        self.assertEqual(131, len(audit["individual_body_clearances"]))
        self.assertTrue(
            all(
                row["remaining_to_opposite_pcb_plane_mm"] >= 0.7
                for row in audit["individual_body_clearances"]
            )
        )
        self.assertEqual(35, audit["opposing_non_mating_pair_count"])
        self.assertEqual(3.31, audit["minimum_opposing_pair"]["remaining_z_clearance_mm"])
        self.assertEqual(35, len(audit["opposing_non_mating_pairs"]))
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
            'data-x-scale-px-per-mm="7.5"',
            'data-z-scale-px-per-mm="7.5"',
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
            "CAP · INSERT ↑ / REMOVE ↓",
            "No installed Cap appears",
            "Keystone Electronics 1048P + 2× 18650",
            "CELLS · INSERT ↑ / REMOVE ↓",
            "Complete opposing-body Z clearance",
            "Dimensioned architecture projection",
        ):
            self.assertIn(token, layout)

    def test_top_edge_view_has_true_axes_and_both_antenna_banks(self):
        layout = self.read("docs/images/top-edge-view.svg")
        for token in (
            'data-view="top-edge" data-look-direction="antenna-edge-to-bottom" data-rf-mounting="opposed-outer-faces" data-x-scale-px-per-mm="8.0" data-z-scale-px-per-mm="8.0"',
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
                "SKRTLAE010",
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

    def test_landing_pages_show_all_layout_views_and_link_exact_principle_diagrams(self):
        for name, schematics in (
            ("README.md", "docs/schematics.md"),
            ("README.ru.md", "docs/schematics.ru.md"),
        ):
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
            self.assertEqual(0, landing.count("```mermaid"), name)
            self.assertIn(schematics, landing, name)
            self.assertIn("docs/pinout", landing, name)
            self.assertIn("docs/interconnect", landing, name)

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
