import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from hardware.layout.h6_r2_routing_drc_delta import item_net, violation_fingerprint
from hardware.layout.h6_r2_kicad_net_bindings import logical_pin_map, pcb_net_name
from hardware.layout.h6_r2_routing_policy import (
    C5_SHARED_PROJECT,
    C5_SHARED_SHEET,
    C5_SHARED_USB_PAIR,
    C5_SHARED_USB_STEM,
    c5_shared_pair_errors,
    classify,
    pair_key,
)
from hardware.layout.h6_r2_routing_session import (
    MAX_SPECCTRA_ROUNDING_NM,
    expected_connection_count,
    placement_rounding,
    session_nets,
)


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_routing_policy.py"
RULES_SCRIPT = ROOT / "hardware/layout/h6_r2_kicad_rules.py"
WORKSPACE_SCRIPT = ROOT / "hardware/layout/h6_r2_routing_workspace.py"
PLACEMENT_FREEZE = ROOT / "hardware/layout/h6-r2-placement-freeze.json"
PLACEMENT_FREEZE_SCRIPT = ROOT / "hardware/layout/h6_r2_placement_freeze.py"
GENERAL_ROUTING_AUDIT = ROOT / "hardware/layout/generated/H6-R2-general-routing-audit.json"
GENERAL_ROUTING_SCRIPT = ROOT / "hardware/layout/h6_r2_general_routing.py"
ROUTING_RENDER_SCRIPT = ROOT / "hardware/layout/h6_r2_routing_render.py"
CURRENT_ROUTING_AUDIT = ROOT / "hardware/layout/generated/H6-R2-current-routing-audit.json"
CURRENT_ROUTING_SCRIPT = ROOT / "hardware/layout/h6_r2_current_routing.py"
MANUAL_COPPER_CONTRACT = ROOT / "hardware/layout/h6-r2-manual-copper.json"
MANUAL_COPPER_AUDIT = ROOT / "hardware/layout/generated/H6-R2-manual-copper-audit.json"
MANUAL_COPPER_SCRIPT = ROOT / "hardware/layout/h6_r2_manual_copper.py"
RELEASE_PLAN = ROOT / "hardware/verification/h6-layout-release-plan.json"
KICAD_PYTHON = Path(
    "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/"
    "Versions/3.9/bin/python3"
)


class H6R2RoutingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_every_physical_net_is_classified_once(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual(822, self.audit["summary"]["project_net_count"])
        self.assertEqual(788, self.audit["summary"]["global_canonical_net_count"])
        self.assertEqual(0, self.audit["summary"]["unclassified_net_count"])
        self.assertEqual(0, self.audit["summary"]["unexpected_net_count"])
        self.assertEqual(822, sum(self.audit["class_counts"].values()))

    def test_automatic_helper_is_fail_closed(self):
        self.assertEqual(["GENERAL_CONTROL"], self.audit["automatic_helper"]["allowed_classes"])
        protected = set(self.audit["automatic_helper"]["locked_or_ignored_classes"])
        self.assertEqual(set(self.contract["classes"]) - {"GENERAL_CONTROL"}, protected)
        self.assertEqual(
            {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"},
            set(self.audit["automatic_helper"]["routable_layers"]),
        )
        self.assertEqual(
            {"In1.Cu", "In4.Cu"},
            set(self.audit["automatic_helper"]["reserved_reference_layers"]),
        )
        self.assertGreaterEqual(self.audit["automatic_helper"]["via_costs"], 100)
        for row in self.audit["rows"]:
            if row["routing_class"] != "GENERAL_CONTROL":
                self.assertFalse(row["route_mode"].startswith("automatic"), row["canonical_net"])

    def test_usb_and_display_groups_are_exact(self):
        self.assertEqual(13, self.audit["summary"]["usb_pair_count"])
        self.assertEqual(4, self.audit["summary"]["external_usb_port_count"])
        self.assertEqual(10, self.audit["summary"]["display_i8080_net_count"])
        self.assertEqual(10, self.audit["summary"]["reviewed_rf_edge_transition_count"])
        transitions = self.contract["classes"]["RF_CONTROLLED"]["reviewed_outer_layer_transitions"]
        self.assertEqual(1, transitions["maximum_through_vias_per_net"])
        self.assertEqual(0.5, transitions["signal_via_diameter_mm"])
        self.assertEqual(0.25, transitions["signal_via_drill_mm"])
        self.assertEqual(
            {
                "C5_EXTERNAL_RF_50R",
                "CC_EXTERNAL_RF_50R",
                "NRF0_EXTERNAL_RF_50R",
                "NRF1_EXTERNAL_RF_50R",
                "NRF2_EXTERNAL_RF_50R",
                "RX_AMLW_BOUNDARY_RF",
                "RX_FMSW_BOUNDARY_RF",
                "S3_EXTERNAL_RF_50R",
                "VOICE_U_EXTERNAL_RF_50R",
                "VOICE_V_EXTERNAL_RF_50R",
            },
            set(transitions["allowed_canonical_nets"]),
        )
        display = {row["canonical_net"] for row in self.audit["rows"] if row["routing_class"] == "DISPLAY_I8080"}
        self.assertEqual({"LCD_DC", "LCD_WR_N", *(f"LCD_DB{i}" for i in range(8))}, display)
        self.assertTrue(all(row["routing_class"] == "USB_DIFFERENTIAL" for row in self.audit["rows"] if "USB_DM" in row["canonical_net"] or "USB_DP" in row["canonical_net"] or row["canonical_net"].startswith(("USB2_DM", "USB2_DP"))))
        usb_names = [
            row["kicad_net"]
            for row in self.audit["rows"]
            if row["routing_class"] == "USB_DIFFERENTIAL"
        ]
        self.assertTrue(all(name.endswith(("_P", "_N")) for name in usb_names))
        self.assertEqual(
            {name[:-2] for name in usb_names if name.endswith("_P")},
            {name[:-2] for name in usb_names if name.endswith("_N")},
        )

    def test_duplicate_ground_pads_and_literal_slashes_survive_pcb_binding(self):
        ui_pins, _ = logical_pin_map("LESHY2-UI-R2")
        self.assertEqual(
            {"POWER_GROUND"},
            {ui_pins[("U1", pin)] for pin in ("1", "40", "41")},
        )
        self.assertEqual(
            "/UI_10_S3_DISPLAY_TOUCH/{slash}UI_10_S3_CORE_MEMORY_BOOT{slash}3V3_MAIN",
            pcb_net_name("/UI_10_S3_DISPLAY_TOUCH//UI_10_S3_CORE_MEMORY_BOOT/3V3_MAIN"),
        )

    def test_shared_c5_usb_sdio_pair_is_explicit_and_manual_only(self):
        self.assertEqual({
            "C5_GPIO13_COMMON": ("N", "DAT3", "GPIO13", "13", "D_MINUS", "4"),
            "C5_GPIO14_COMMON": ("P", "DAT2", "GPIO14", "14", "D_PLUS", "3"),
        }, C5_SHARED_USB_PAIR)
        common = self.audit["shared_usb_sdio_pair"]
        self.assertEqual(C5_SHARED_PROJECT, common["project"])
        self.assertEqual(C5_SHARED_USB_STEM, common["pair_stem"])
        self.assertEqual("USB_DIFFERENTIAL", common["routing_class"])
        self.assertEqual("manual_only", common["route_mode"])
        rows = {row["canonical_net"]: row for row in self.audit["rows"]
                if row["project"] == C5_SHARED_PROJECT}
        for name, (polarity, sdio, *_pins) in C5_SHARED_USB_PAIR.items():
            self.assertEqual("USB_DIFFERENTIAL", classify(name, set(), set()))
            self.assertEqual((C5_SHARED_USB_STEM, polarity), pair_key(name))
            self.assertEqual("USB_DIFFERENTIAL", rows[name]["routing_class"])
            self.assertEqual("manual_only", rows[name]["route_mode"])
            self.assertEqual(sdio, common["members"][polarity]["sdio_signal"])
            self.assertEqual(f"/{C5_SHARED_SHEET}/{C5_SHARED_USB_STEM}_{polarity}",
                             rows[name]["kicad_net"])
        # The exception is exact: a similar GPIO name is not a USB alias.
        self.assertEqual("GENERAL_CONTROL", classify("C5_GPIO12_COMMON", set(), set()))
        self.assertIsNone(pair_key("C5_GPIO12_COMMON"))
        self.assertEqual(("C5_SERVICE_USB_DX_CONNECTOR", "N"),
                         pair_key("C5_SERVICE_USB_DM_CONNECTOR"))

    def test_shared_c5_guard_accepts_only_actual_four_endpoints(self):
        ledger = json.loads((ROOT / self.contract["inputs"]["net_ledger"]).read_text())
        bindings = json.loads((ROOT / self.contract["inputs"]["net_bindings"]).read_text())
        self.assertEqual([], c5_shared_pair_errors(ledger["rows"], bindings["projects"]))
        originals = [row for row in ledger["rows"] if row["net"] in C5_SHARED_USB_PAIR]
        self.assertEqual(4, len(originals))
        for index in range(4):
            with self.subTest(missing=index):
                rows = copy.deepcopy(originals)
                rows.pop(index)
                self.assertTrue(c5_shared_pair_errors(rows, bindings["projects"]))
            for field in ("project", "sheet", "reference", "instance", "device_id",
                          "contact", "physical", "disposition", "endpoint", "net"):
                with self.subTest(index=index, changed=field):
                    rows = copy.deepcopy(originals)
                    rows[index][field] = "wrong"
                    self.assertTrue(c5_shared_pair_errors(rows, bindings["projects"]))
        self.assertTrue(c5_shared_pair_errors([], bindings["projects"]))
        self.assertTrue(c5_shared_pair_errors(originals + [originals[0]], bindings["projects"]))
        swapped = copy.deepcopy(originals)
        for row in swapped:
            row["net"] = ("C5_GPIO14_COMMON" if row["net"] == "C5_GPIO13_COMMON"
                          else "C5_GPIO13_COMMON")
        self.assertTrue(c5_shared_pair_errors(swapped, bindings["projects"]))

    def test_shared_c5_guard_rejects_wrong_native_alias_or_board(self):
        ledger = json.loads((ROOT / self.contract["inputs"]["net_ledger"]).read_text())
        bindings = json.loads((ROOT / self.contract["inputs"]["net_bindings"]).read_text())
        for name, (polarity, *_rest) in C5_SHARED_USB_PAIR.items():
            for native in (name, f"/{C5_SHARED_SHEET}/{C5_SHARED_USB_STEM}_{'P' if polarity == 'N' else 'N'}"):
                with self.subTest(name=name, wrong_alias=native):
                    projects = copy.deepcopy(bindings["projects"])
                    projects[C5_SHARED_PROJECT]["canonical_to_kicad"][name] = native
                    self.assertTrue(c5_shared_pair_errors(ledger["rows"], projects))
            projects = copy.deepcopy(bindings["projects"])
            projects["LESHY2-RF-R2"]["canonical_to_kicad"][name] = "unexpected"
            self.assertTrue(c5_shared_pair_errors(ledger["rows"], projects))
        self.assertTrue(c5_shared_pair_errors(ledger["rows"], {}))

    def test_stackup_identity_and_core_thickness_are_not_ambiguous(self):
        stack = self.audit["stackup_binding"]
        self.assertEqual("JLC06161H-3313", stack["official_stackup_id"])
        self.assertEqual(1.6, stack["order_thickness_mm"])
        self.assertEqual(1.54, stack["calculator_finished_thickness_mm"])
        self.assertEqual(0.55, stack["core_each_mm"])
        self.assertIn("bound to the current JLCPCB calculator", stack["exact_trace_geometry_status"])
        self.assertEqual(0.134874, stack["outer_layer_geometries"]["RF_50R_CPWG"]["trace_width_mm"])
        self.assertEqual(0.1524, stack["outer_layer_geometries"]["RF_50R_CPWG"]["coplanar_gap_mm"])
        self.assertEqual(0.134874, stack["outer_layer_geometries"]["USB_90R_DIFFERENTIAL"]["trace_width_mm"])
        self.assertEqual(0.1524, stack["outer_layer_geometries"]["USB_90R_DIFFERENTIAL"]["pair_gap_mm"])

    def test_known_sensitive_lines_cannot_fall_into_the_automatic_class(self):
        assigned = {
            (row["project"], row["canonical_net"]): row["routing_class"]
            for row in self.audit["rows"]
        }
        self.assertEqual("RF_CONTROLLED", assigned[("LESHY2-RF-R2", "AIR_LO_CLK_RAW")])
        self.assertEqual("SAFETY_CONTROL", assigned[("LESHY2-UI-R2", "NRF_EVIDENCE_HOLD")])
        self.assertEqual("SAFETY_CONTROL", assigned[("LESHY2-RF-R2", "PACK_CHG_GATE")])
        self.assertEqual("ANALOG_AUDIO_SENSE", assigned[("LESHY2-RF-R2", "USB_C_CC1_CONNECTOR")])
        self.assertEqual("CLOCKED_DIGITAL", assigned[("LESHY2-UI-R2", "IR_TX_CARRIER")])

    def test_generated_artifacts_are_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("0 unclassified", result.stdout)

        rules = subprocess.run(
            ["python3", str(RULES_SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, rules.returncode, rules.stdout)
        self.assertIn("exact RF/USB outer-layer geometry", rules.stdout)

        renders = subprocess.run(
            ["python3", str(ROUTING_RENDER_SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, renders.returncode, renders.stdout)
        self.assertIn("2 routing SVGs + 4 component faces and overview are current", renders.stdout)

    def test_routing_report_embeds_both_real_board_views(self):
        for document in (
            ROOT / "docs/h6-r2-routing-policy.md",
            ROOT / "docs/h6-r2-routing-policy.ru.md",
        ):
            text = document.read_text(encoding="utf-8")
            self.assertIn("images/h6-r2-routing-ui.svg", text)
            self.assertIn("images/h6-r2-routing-rf.svg", text)

    def test_live_80mm_routing_checkpoint_is_hash_bound_and_non_closing(self):
        audit = json.loads(CURRENT_ROUTING_AUDIT.read_text(encoding="utf-8"))
        self.assertEqual("H6.0.3-R1", audit["marker"])
        self.assertEqual("pass_progress", audit["status"])
        self.assertFalse(audit["phase_complete"])
        self.assertEqual(857, audit["summary"]["track_via_item_count"])
        self.assertEqual(197, audit["summary"]["resolved_connection_count"])
        self.assertEqual(3071, audit["summary"]["current_total_unconnected_count"])
        self.assertEqual(232, audit["summary"]["analog_remaining_connection_count"])
        self.assertEqual(311, audit["summary"]["placement_locality_pair_count"])
        self.assertEqual(0, audit["summary"]["placement_locality_violation_count"])
        size = audit["board_size_review"]
        self.assertEqual("retain_80x150_mm", size["decision"])
        # Corrected interfaces and the outward ordinary-SMT audio body change
        # side occupancy without removing fitted parts or expanding the PCB.
        self.assertEqual(60.229, size["maximum_same_face_courtyard_occupancy_percent"])
        self.assertEqual([85.0, 150.0], size["expansion_candidate_if_triggered_mm"])
        self.assertEqual(5, len(size["requalification_after_any_outline_or_anchor_change"]))
        boards = {row["project"]: row for row in audit["boards"]}
        self.assertEqual(0, boards["LESHY2-UI-R2"]["drc"]["violation_count"])
        self.assertEqual(0, boards["LESHY2-RF-R2"]["drc"]["violation_count"])
        self.assertEqual([], boards["LESHY2-RF-R2"]["drc"]["violation_types"])
        self.assertEqual(0, audit["summary"]["assigned_drc_exception_count"])
        for row in boards.values():
            self.assertEqual([], row["errors"])
            self.assertEqual(64, len(row["board_sha256"]))
            self.assertEqual(
                row["current_total_unconnected_count"],
                sum(
                    state["remaining_connection_count"]
                    for state in row["classes"].values()
                ),
            )
        placement = json.loads((ROOT / "hardware/layout/generated/H6-R2-placement-audit.json").read_text())
        pad_pair_count = placement["summary"]["critical_pad_pair_count"]
        self.assertEqual(pad_pair_count, audit["summary"]["placement_critical_pad_pair_count"])
        for document, count_phrase in (
            (ROOT / "docs/h6-r2-current-routing.md", f"{pad_pair_count} actual pad-centre pairs"),
            (ROOT / "docs/h6-r2-current-routing.ru.md", f"набор из {pad_pair_count} точных проверок"),
        ):
            text = document.read_text(encoding="utf-8")
            self.assertIn("images/h6-r2-routing-ui.svg", text)
            self.assertIn("images/h6-r2-routing-rf.svg", text)
            self.assertIn(count_phrase, text)

    def test_live_routing_reports_keep_production_and_typed_erc_scopes_separate(self):
        triage = json.loads((ROOT / "hardware/verification/h6-electrical-source-triage.json").read_text())
        self.assertEqual("triaged_not_cleared", triage["status"])
        self.assertEqual(24, triage["summary"]["native_total_findings"])
        self.assertEqual(22, triage["summary"]["native_power_findings"])
        self.assertFalse(triage["summary"]["whole_electrical_gate_pass"])
        for filename, required in (
            ("h6-r2-current-routing.md", ("production library still uses `passive`",
                                          "only to isolated schematic copies", "24 findings", "do not suppress ERC",
                                          "have not been promoted to the production library")),
            ("h6-r2-current-routing.ru.md", ("библиотека по-прежнему использует `passive`",
                                             "только к изолированным копиям схем", "24 замечания", "не подавляют ERC",
                                             "типы не перенесены в рабочую библиотеку")),
        ):
            text = (ROOT / "docs" / filename).read_text()
            with self.subTest(filename=filename):
                for phrase in (*required, "22 `power_pin_not_driven`", "ACDRV1/ACDRV2",
                               "SA818S H/L", "`triaged_not_cleared`", "`review_required`",
                               "../hardware/verification/h6-electrical-source-triage.json"):
                    self.assertIn(phrase, text)

    def test_live_led_summary_uses_current_reviewed_routes_and_excludes_fault(self):
        audit = json.loads(MANUAL_COPPER_AUDIT.read_text(encoding="utf-8"))
        routes = [row for row in audit["routes"]
                  if row["project"] == "LESHY2-UI-R2" and "reviewed_proposal" in row]
        names = {row["canonical_net"] for row in routes}
        self.assertNotIn("FAULT_LED_A", names)
        segments = sum(row["segment_count"] for row in routes)
        vias = sum(row["via_count"] for row in routes)
        for filename, required in (
            ("h6-r2-current-routing.md", (f"cover {len(routes)} nets", f"{segments} traces",
                                          f"{vias} through vias", "`FAULT_LED_A` is excluded")),
            ("h6-r2-current-routing.ru.md", (f"{len(routes)} сетей", f"{segments} дорожек",
                                             f"{vias} сквозных via", "`FAULT_LED_A` в этот набор не входит")),
        ):
            page = (ROOT / "docs" / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                for phrase in (*required, *[f"`{name}`" for name in names], "`SAFETY_CONTROL`"):
                    self.assertIn(phrase, page)

    def test_reviewed_manual_power_routes_are_reproducible_and_drc_bound(self):
        contract = json.loads(MANUAL_COPPER_CONTRACT.read_text(encoding="utf-8"))
        audit = json.loads(MANUAL_COPPER_AUDIT.read_text(encoding="utf-8"))
        self.assertEqual("in_progress", contract["status"])
        self.assertEqual("pass", audit["status"])
        self.assertEqual([], audit["errors"])
        self.assertEqual(115, audit["summary"]["route_count"])
        self.assertEqual(682, audit["summary"]["segment_count"])
        self.assertEqual(197, audit["summary"]["resolved_connection_count"])
        self.assertEqual(175, audit["summary"]["via_count"])
        self.assertEqual(86, audit["summary"]["manual_only_route_count"])
        self.assertEqual(20, audit["summary"]["local_ground_join_route_count"])
        self.assertEqual(9, audit["summary"]["reviewed_general_control_proposal_route_count"])
        self.assertTrue(
            {row["routing_class"] for row in audit["routes"]}
            == {
                "ANALOG_AUDIO_SENSE",
                "GENERAL_CONTROL",
                "GROUND_REFERENCE",
                "OSCILLATOR",
                "POWER_BRANCH",
                "PRIMARY_POWER",
                "RF_CONTROLLED",
                "SWITCHING_NODE",
            }
        )
        self.assertEqual(
            {"B.Cu", "F.Cu", "In1.Cu", "In2.Cu", "In3.Cu"},
            {layer for row in audit["routes"] for layer in row["layers"]},
        )
        current = json.loads(CURRENT_ROUTING_AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(0, current["summary"]["drc_violation_count"])
        if KICAD_PYTHON.is_file():
            result = subprocess.run(
                [str(KICAD_PYTHON), str(MANUAL_COPPER_SCRIPT), "--check"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertIn("115 routes; 682 segments; 197 resolved connections", result.stdout)

    def test_corrected_rf_packages_withdraw_only_the_exact_invalidated_routes(self):
        contract = json.loads(MANUAL_COPPER_CONTRACT.read_text(encoding="utf-8"))
        audit = json.loads(MANUAL_COPPER_AUDIT.read_text(encoding="utf-8"))
        rework = contract["rf_package_rework"]
        expected = {
            "RF-AIRBAND-T1-SEC-CT",
            "RF-AIRBAND-T1-SEC-N",
            "RF-CC1101-UNBALANCED-MATCH",
            *(f"UI-{module}-{suffix}" for module in ("C5", "S3")
              for suffix in ("COUPLED-SAMPLE", "COUPLER-TERM", "EXTERNAL-RF", "MODULE-RF")),
            *(f"UI-NRF{index}-{suffix}" for index in range(3)
              for suffix in ("COUPLER-TERM", "EXTERNAL-RF", "FORWARD-SAMPLE", "MODULE-RF")),
        }
        withdrawn = rework["withdrawn_route_ids"]
        self.assertEqual(23, len(withdrawn))
        self.assertEqual(expected, set(withdrawn))
        self.assertEqual(
            {"LESHY2-UI-R2": {"U3", "U16", "U36", "U40", "U44"},
             "LESHY2-RF-R2": {"U29", "U56", "U57"}},
            {project: set(refs) for project, refs in rework["affected_references"].items()},
        )
        self.assertEqual(8, sum(len(refs) for refs in rework["affected_references"].values()))
        active = [row["id"] for row in contract["routes"]]
        replayed = [row["id"] for row in audit["routes"]]
        self.assertEqual(115, len(active))
        self.assertEqual(115, len(set(active)))
        self.assertEqual(115, len(replayed))
        self.assertEqual(set(active), set(replayed))
        self.assertTrue(expected.isdisjoint(active))
        self.assertTrue(expected.isdisjoint(replayed))
        self.assertIs(False, rework["release_authorized"])
        for document in (contract, audit):
            self.assertEqual(
                {"routing_in_progress": True, "fabrication": False, "ordering": False},
                document["authorization"],
            )

    def test_h6_release_substep_ids_are_unique_and_end_at_h609(self):
        plan = json.loads(RELEASE_PLAN.read_text(encoding="utf-8"))
        ids = [row["id"] for row in plan["substeps"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual("H6.0.9-R1", ids[-1])

    def test_kicad_rules_bind_exact_calculator_geometry(self):
        for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            path = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_dru"
            text = path.read_text(encoding="utf-8")
            self.assertIn("JLC06161H-3313", text)
            self.assertIn("5.31mil width 6.00mil gap", text)
            self.assertIn("(constraint track_width (min 5.31mil) (opt 5.31mil) (max 5.31mil))", text)
            self.assertIn("(constraint diff_pair_gap (min 6.00mil) (opt 6.00mil) (max 6.00mil))", text)
            self.assertIn('(layer inner)', text)
            self.assertIn('H6 reviewed RF edge-launch trace reaches centre land', text)
            self.assertIn('H6 controlled-impedance vias only on reviewed edge launches', text)
            self.assertIn('(constraint disallow track)', text)
            self.assertIn('(constraint disallow via)', text)
            self.assertNotIn('(constraint disallow track via)', text)

    def test_shared_c5_pair_has_real_usb_width_gap_layer_and_via_rules(self):
        path = ROOT / f"hardware/ecad/kicad/{C5_SHARED_PROJECT}/{C5_SHARED_PROJECT}.kicad_dru"
        text = path.read_text()
        rules = text.split('(rule "')
        for title, constraints in (
            ("H6 outer USB 90R", ("(layer outer)", "(constraint track_width", "(constraint diff_pair_gap")),
            ("H6 controlled-impedance tracks stay on outer layers", ("(layer inner)", "(constraint disallow track)")),
            ("H6 controlled-impedance vias only on reviewed edge launches", ("A.Type == 'Via'", "(constraint disallow via)")),
        ):
            selected = [rule for rule in rules if rule.startswith(title)]
            self.assertEqual(1, len(selected), title)
            for polarity in ("N", "P"):
                self.assertIn(f"A.NetName == '/{C5_SHARED_SHEET}/{C5_SHARED_USB_STEM}_{polarity}'", selected[0])
            for constraint in constraints:
                self.assertIn(constraint, selected[0])

    def test_session_and_drc_guards_parse_machine_artifacts(self):
        self.assertEqual(
            {"/UI/ONE", "PLAIN_TWO"},
            session_nets('      (net "/UI/ONE"\n      (net PLAIN_TWO\n'),
        )
        rounded, delta = placement_rounding(
            {"U1": (100, 200, 90.0, True)},
            {"U1": (101, 200, 90.0, True)},
        )
        self.assertEqual(["U1"], rounded)
        self.assertEqual(1, delta)
        rounded, delta = placement_rounding(
            {"MK1": (100, 200, 0.0, True)},
            {"MK1": (100 + MAX_SPECCTRA_ROUNDING_NM, 200, 0.0, True)},
        )
        self.assertEqual(["MK1"], rounded)
        self.assertEqual(MAX_SPECCTRA_ROUNDING_NM, delta)
        rounded, delta = placement_rounding(
            {"MK1": (100, 200, 0.0, True)},
            {"MK1": (100 + MAX_SPECCTRA_ROUNDING_NM + 1, 200, 0.0, True)},
        )
        self.assertEqual(["MK1"], rounded)
        self.assertEqual(MAX_SPECCTRA_ROUNDING_NM + 1, delta)
        rounded, delta = placement_rounding(
            {"U1": (100, 200, 0.0, True)},
            {"U1": (100, 200, 90.0, True)},
        )
        self.assertEqual(["U1"], rounded)
        self.assertGreater(delta, MAX_SPECCTRA_ROUNDING_NM)

        class Pad:
            def __init__(self, net):
                self.net = net

            def GetNetname(self):
                return self.net

        class Board:
            def GetPads(self):
                return [Pad("A"), Pad("A"), Pad("A"), Pad("B"), Pad("B"), Pad("OTHER")]

        self.assertEqual(3, expected_connection_count(Board(), {"A", "B"}))
        self.assertEqual("/UI/ONE", item_net("Track [/UI/ONE] on F.Cu"))
        violation = {
            "type": "clearance",
            "description": "too close",
            "items": [{"uuid": "b"}, {"uuid": "a"}],
        }
        self.assertEqual(
            ("clearance", "too close", ("a", "b")),
            violation_fingerprint(violation),
        )

    def test_exact_placement_freeze_and_general_bootstrap_are_complete(self):
        freeze = json.loads(PLACEMENT_FREEZE.read_text(encoding="utf-8"))
        self.assertEqual("pass", freeze["freeze"]["status"])
        self.assertEqual(1208, freeze["freeze"]["footprint_count"])
        rows = [row for board in freeze["boards"] for row in board["placements"]]
        self.assertEqual(1208, len(rows))
        self.assertTrue(all(len(row["footprint_anchor_nm"]) == 2 for row in rows))
        self.assertNotIn("placement_freeze_sha256", freeze["sources"])
        s3_detector_cap = next(
            row
            for board in freeze["boards"]
            if board["project"] == "LESHY2-UI-R2"
            for row in board["placements"]
            if row["instance"] == "s3_detector_input_cap"
        )
        self.assertEqual([30.6, 4.95], s3_detector_cap["footprint_anchor_mm"])
        self.assertEqual(0.0, s3_detector_cap["rotation_deg"])
        reviewed_nrf0 = {
            row["instance"]: row
            for board in freeze["boards"]
            if board["project"] == "LESHY2-UI-R2"
            for row in board["placements"]
            if row["instance"]
            in {"det_nrf0", "nrf0_coupler", "nrf0_coupler_termination", "nrf0_detector_match"}
        }
        self.assertEqual([11.7, 13.6], reviewed_nrf0["det_nrf0"]["footprint_anchor_mm"])
        self.assertEqual(-90.0, reviewed_nrf0["det_nrf0"]["rotation_deg"])
        self.assertEqual([10.8, 9.0], reviewed_nrf0["nrf0_coupler"]["footprint_anchor_mm"])
        self.assertEqual(0.0, reviewed_nrf0["nrf0_coupler"]["rotation_deg"])
        self.assertEqual(
            [13.5, 7.5], reviewed_nrf0["nrf0_coupler_termination"]["footprint_anchor_mm"]
        )
        self.assertEqual([13.1, 9.5], reviewed_nrf0["nrf0_detector_match"]["footprint_anchor_mm"])
        nrf1_coupler = next(
            row
            for board in freeze["boards"]
            if board["project"] == "LESHY2-UI-R2"
            for row in board["placements"]
            if row["instance"] == "nrf1_coupler"
        )
        self.assertEqual([42.315, 18.835], nrf1_coupler["footprint_anchor_mm"])
        self.assertEqual(180.0, nrf1_coupler["rotation_deg"])
        reviewed_nrf2 = {
            row["instance"]: row
            for board in freeze["boards"]
            if board["project"] == "LESHY2-UI-R2"
            for row in board["placements"]
            if row["instance"] in {"det_nrf2", "nrf2_coupler", "nrf2_coupler_termination"}
        }
        self.assertEqual(180.0, reviewed_nrf2["det_nrf2"]["rotation_deg"])
        self.assertEqual(-90.0, reviewed_nrf2["nrf2_coupler"]["rotation_deg"])
        self.assertEqual([69.075, 15.9], reviewed_nrf2["nrf2_coupler_termination"]["footprint_anchor_mm"])

        routing = json.loads(GENERAL_ROUTING_AUDIT.read_text(encoding="utf-8"))
        self.assertEqual("pass", routing["status"])
        self.assertEqual(288, routing["summary"]["allowed_net_count"])
        self.assertEqual(652, routing["summary"]["expected_allowed_connection_count"])
        self.assertEqual(652, routing["summary"]["resolved_allowed_connection_count"])
        self.assertEqual(0, routing["summary"]["remaining_allowed_connection_count"])
        self.assertEqual(0, routing["summary"]["drc_violation_count"])
        self.assertEqual(0, routing["summary"]["error_count"])
        self.assertEqual(
            {"ANALOG_AUDIO_SENSE"},
            set(routing["scope"]["not_completed"]),
        )
        for board in routing["boards"]:
            self.assertTrue(board["placement_unchanged"])
            self.assertEqual(0, board["protected_routed_net_count"])
            self.assertEqual(0, board["ordinary_copper_zone_count"])
            self.assertEqual(0, board["remaining_allowed_connection_count"])
            self.assertEqual(0, board["drc"]["violation_count"])
            self.assertEqual(0, board["drc"]["schematic_parity_error_count"])
            self.assertEqual(
                {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"},
                set(board["used_trace_layers"]),
            )

    def test_native_placement_and_routing_guards_are_current(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        for script, expected in (
            (PLACEMENT_FREEZE_SCRIPT, "1208 exact anchors"),
            (GENERAL_ROUTING_SCRIPT, "historical routing evidence preserved; current H6.0.3-R1"),
            (CURRENT_ROUTING_SCRIPT, "857 copper items; 197 resolved; 3071 remain"),
        ):
            result = subprocess.run(
                [str(KICAD_PYTHON), str(script), "--check"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            self.assertIn(expected, result.stdout)

    def test_temporary_dsn_workspace_replaces_the_permissive_default_class(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [str(KICAD_PYTHON), str(WORKSPACE_SCRIPT), "--output-dir", directory],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            manifest = json.loads((Path(directory) / "routing-workspace-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(["GENERAL_CONTROL"], manifest["allowed_classes"])
            self.assertEqual(12, len(manifest["freerouting_ignore_classes"]))
            self.assertEqual(["In1.Cu", "In4.Cu"], manifest["reserved_reference_layers"])
            self.assertEqual(250, manifest["via_costs"])
            for project in manifest["projects"]:
                dsn = Path(project["dsn"]).read_text(encoding="utf-8")
                self.assertNotIn("(class kicad_default", dsn)
                self.assertEqual(project["emitted_class_count"], dsn.count("(class "))
                self.assertEqual(project["physical_net_count"], sum(project["class_counts"].values()))
                self.assertEqual(project["helper_net_count"], dsn.count("\n    (net "))
                self.assertEqual(
                    project["physical_net_count"],
                    project["helper_net_count"] + project["omitted_protected_net_count"],
                )
                self.assertEqual(project["class_counts"]["GENERAL_CONTROL"], project["helper_net_count"])
                for polarity in ("N", "P"):
                    self.assertNotIn(f"(net /{C5_SHARED_SHEET}/{C5_SHARED_USB_STEM}_{polarity}", dsn)
                self.assertIn("(layer_rule In1.Cu\n      (active off)", dsn)
                self.assertIn("(layer_rule In4.Cu\n      (active off)", dsn)
                self.assertIn("(layer_rule In2.Cu\n      (active on)", dsn)
                self.assertIn("(via_costs 250)", dsn)
                self.assertIn("(layer In1.Cu\n      (type power)", dsn)
                self.assertIn("(layer In4.Cu\n      (type power)", dsn)


if __name__ == "__main__":
    unittest.main()
