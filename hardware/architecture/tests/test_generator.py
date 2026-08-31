import copy
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "generate.py"
SPEC = importlib.util.spec_from_file_location("architecture_generate", MODULE_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


class ArchitectureValidationTests(unittest.TestCase):
    def setUp(self):
        self.database, self.candidates = GENERATOR.load_sources()

    def errors_for(self, candidates=None):
        return GENERATOR.validate_sources(self.database, candidates or self.candidates)

    def test_checked_in_sources_are_valid(self):
        self.assertEqual([], self.errors_for())

    def test_rejects_destructive_or_industrial_qualification_in_current_candidate(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["qualification_gaps"].append(
            "connector retention must be proven over repeated cycles"
        )
        errors = self.errors_for(candidates)
        self.assertTrue(
            any(
                "prohibited destructive/industrial qualification phrase"
                in error
                for error in errors
            ),
            errors,
        )

    def test_pre_kicad_plan_preserves_sole_prototype_manifest_and_gate(self):
        roadmap = json.loads(
            (GENERATOR.REPO_ROOT / "hardware/verification/hardware-roadmap-state.json")
            .read_text(encoding="utf-8")
        )
        h5 = json.loads(
            (GENERATOR.REPO_ROOT / "hardware/verification/h5-component-evidence-plan.json")
            .read_text(encoding="utf-8")
        )
        plan = (
            GENERATOR.REPO_ROOT / "hardware/procurement/pre-kicad-sample-plan.md"
        ).read_text(encoding="utf-8")
        plan_normalized = " ".join(plan.split())
        self.assertEqual("H3-R2.4", roadmap["current_substep"])
        self.assertEqual("R2", roadmap["baseline"])
        self.assertEqual("H5.0.3-R1", h5["current_substep"])
        self.assertIn("H5.0.1-R1", h5["reviewed_artifacts"])
        self.assertIn("H5.0.2-R1", h5["reviewed_artifacts"])
        self.assertIn("H5.0.3", h5["superseded_current_artifacts"])
        self.assertIn("H5.0.3-R1", h5["current_artifacts"])
        self.assertFalse(h5["authorization"]["sample_or_component_purchase"])
        self.assertIn("superseded", plan)
        self.assertIn("no separate engineering-sample or H5 coupon order", plan_normalized)
        self.assertIn("sole prototype order", plan_normalized)
        self.assertIn("remain unauthorized", plan)
        for device_id in ("nicerf_sa818s_u_v18", "nicerf_sa818s_v_v18"):
            voice = self.database["devices"][device_id]
            self.assertEqual([35.6, 19.0, 3.2], voice["maximum_dimensions_mm"])
            self.assertEqual(18, len(voice["contacts"]))

    def test_hwfw_target_integration_contract_matches_architecture(self):
        contract = json.loads(
            (GENERATOR.REPO_ROOT / "hardware/architecture/target-integration-contract.json")
            .read_text(encoding="utf-8")
        )
        candidate = next(c for c in self.candidates if c["id"] == contract["hardware_architecture"])
        self.assertEqual("LESHY2-HWFW-1", contract["contract_id"])
        self.assertEqual(2, contract["schema"])
        self.assertEqual("h2_0_3_reviewed", contract["review_status"])

        for controller in contract["controllers"]:
            device_id = candidate["instances"][controller["instance"]]
            self.assertEqual(controller["mpn"], self.database["devices"][device_id]["mpn"])

        allocation_net = {
            f"{row['instance']}.{row['contact']}": row["net"]
            for row in candidate["allocations"]
        }
        resources = {row["id"]: row for row in candidate["resource_contracts"]}
        for transport in contract["transports"]:
            resource_id = transport.get("hardware_resource")
            if resource_id:
                self.assertIn(resource_id, resources)
                self.assertIn("20 MHz", resources[resource_id]["deadline"])
                self.assertIn(">=1.5 MB/s", resources[resource_id]["deadline"])
            for endpoints in transport["pins"].values():
                nets = {allocation_net[endpoint] for endpoint in endpoints}
                self.assertEqual(1, len(nets), endpoints)

        hardware_groups = {
            row["id"] for row in candidate["signal_group_policy"]["groups"]
        }
        for row in contract["signal_groups"]:
            if row["hardware"] is not None:
                self.assertIn(row["hardware"], hardware_groups)
        evidence = candidate["safety_contract"]["evidence"]
        self.assertEqual(
            [
                "S3_RF", "C5_RF", "NRF0_RF", "NRF1_RF", "NRF2_RF",
                "CC_RF", "VOICE_RF", "IR_OPTICAL", "LORA_EXT_RF",
            ],
            evidence["channels"],
        )

        cap = json.loads(
            (GENERATOR.REPO_ROOT / "hardware/accessories/leshy2-lora-cap-01.json")
            .read_text(encoding="utf-8")
        )
        for profile in contract["lora_cap_profiles"]:
            variant = cap["variants"][profile["assembly"]]
            module = self.database["devices"][variant["module"]]["mpn"]
            self.assertEqual(profile["module"], module)
            self.assertIn(
                f"{profile['allowed_frequency_mhz'][0]}–{profile['allowed_frequency_mhz'][1]} MHz",
                variant["band_label"],
            )

    def test_exact_m1_pair_locality_and_contact_budget_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["interboard_contract"]
        pair = contract["connector_pair"]
        self.assertEqual(80, pair["positions"])
        self.assertEqual(11, pair["mated_height_mm"])
        self.assertEqual(
            "hirose_fx8c_80p_sv1_92",
            candidate["instances"][pair["ui_instance"]],
        )
        self.assertEqual(
            "hirose_fx8c_80s_sv5_92",
            candidate["instances"][pair["rf_power_instance"]],
        )
        pin_map = contract["pin_map"]
        self.assertEqual(list(range(1, 81)), [row["contact"] for row in pin_map])
        self.assertEqual(7, sum(row["net"] == "3V3_MAIN" for row in pin_map))
        self.assertEqual(0, sum(row["signal_class"] == "reserved" for row in pin_map))
        accounting = contract["accounting"]
        self.assertEqual(
            accounting["power_ground_contacts"],
            sum(row["net"] == "POWER_GROUND" for row in pin_map),
        )
        self.assertEqual(
            accounting["audio_ground_contacts"],
            sum(row["net"] == "AUDIO_GROUND" for row in pin_map),
        )
        self.assertEqual(
            accounting["safety_ground_contacts"],
            sum(row["net"] == "SAFETY_GROUND" for row in pin_map),
        )
        mapped = {row["net"] for row in pin_map}
        self.assertTrue(
            {
                "S3_USB_DM", "S3_USB_DP", "RUN_PERMIT", "FAULT_ASSERT_N",
                "UI_ENCODER_PUSH_N",
                "ENCODER_A", "ENCODER_B", "S3_RESET_KILL_GATE",
                "UI_ZONE_TEMP_ADC", "FAULT_LATCH_SENSE_AON",
                "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2",
                "EV_N5_CC", "EV_N6_VOICE", "EV_N8_LORA_EXT",
                "MIC_RAW", "SPEAKER_AMP_EN",
            } <= mapped
        )
        by_contact = {row["contact"]: row for row in pin_map}
        self.assertEqual("EV_N2_NRF0", by_contact[29]["net"])
        self.assertEqual("EV_N3_NRF1", by_contact[30]["net"])
        self.assertEqual("EV_N4_NRF2", by_contact[33]["net"])
        self.assertEqual("EV_N5_CC", by_contact[58]["net"])
        self.assertEqual("FAULT_LATCH_SENSE_AON", by_contact[77]["net"])
        self.assertEqual("EV_N6_VOICE", by_contact[79]["net"])
        self.assertEqual("EV_N8_LORA_EXT", by_contact[80]["net"])
        self.assertEqual(
            {"net": "MIC_RAW", "direction": "RF→UI", "signal_class": "audio"},
            {key: by_contact[48][key] for key in ("net", "direction", "signal_class")},
        )
        self.assertEqual("AUDIO_GROUND", by_contact[49]["net"])
        self.assertEqual("SPEAKER_AMP_EN", by_contact[78]["net"])
        locality = contract["physical_locality"]
        self.assertNotIn("microphone", locality["ui_control_board"])
        self.assertTrue(
            any(item.startswith("microphone") for item in locality["rf_power_board"])
        )
        self.assertNotIn("TX_KILL", mapped)
        self.assertTrue(
            {
                "USB_C_VBUS_RAW", "PD_PPHV", "PROTECTED_PACK_POSITIVE",
                "IR_TX_CARRIER", "SPEAKER_BTL_P", "SPEAKER_BTL_N",
            }.isdisjoint(mapped)
        )
        for device_id in (
            "hirose_fx8c_80p_sv1_92",
            "hirose_fx8c_80s_sv5_92",
        ):
            device = self.database["devices"][device_id]
            self.assertEqual("active", device["lifecycle"])
            self.assertEqual(80, len(device["contacts"]))
            self.assertIn("hirose.com", device["source"]["url"])
            self.assertEqual(100, device["cost"]["target_quantity"])

        s3_evidence_routes = [
            route for route in candidate["fixed_routes"]
            if route["from"] == "evidence_cmp_a.OUT1"
            or route["to"] == "evidence_cmp_a.OUT1"
        ]
        self.assertTrue(s3_evidence_routes)
        self.assertEqual({"EV_N0_S3"}, {route["net"] for route in s3_evidence_routes})

        for language in (False, True):
            rendered = GENERATOR.render_public_interconnect(
                self.database, self.candidates, russian=language
            )
            self.assertIn("FX8C-80P-SV1(92)", rendered)
            self.assertIn("FX8C-80S-SV5(92)", rendered)
            self.assertIn("SMT", rendered)
            self.assertIn(
                "не сквозные гребёнки" if language else "not through-hole pin headers",
                rendered,
            )
            self.assertIn(
                "четыре совмещённые стойки/винта"
                if language
                else "Four aligned board standoffs and screws",
                rendered,
            )
            self.assertIn("| `80` |", rendered)

    def test_exact_ten_external_sma_bodies_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        expected = {
            "s3_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
            "c5_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
            "receiver_fmsw_external_sma": "gct_rfpc_sma31_fn_175_a",
            "receiver_amlw_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf0_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf1_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf2_external_sma": "gct_rfpc_sma31_fn_175_a",
            "cc_external_sma": "gct_rfpc_sma31_fn_175_a",
            "voice_external_sma": "gct_rfpc_sma31_fn_175_a",
            "voice_v_external_sma": "gct_rfpc_sma31_fn_175_a",
        }
        self.assertEqual(10, len(expected))
        for instance, device_id in expected.items():
            self.assertEqual(device_id, candidate["instances"][instance])
            device = self.database["devices"][device_id]
            contract = device["electrical_contract"]
            self.assertEqual(6, contract["maximum_frequency_ghz"])
            self.assertEqual(50, contract["impedance_ohm"])
            self.assertEqual("IP67 mated and unmated", contract["ingress_protection"])
            self.assertIn("1.6-mm PCB", contract["mounting"])
            self.assertEqual(5, len(device["contacts"]))
            self.assertIn("gct.co", device["source"]["url"])
            self.assertEqual(100, device["cost"]["target_quantity"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(
            ("s3_rf_coupler.RF_OUT", "s3_external_rp_sma.RF", "S3_EXTERNAL_RF_50R"),
            routes,
        )
        for instance in expected:
            for contact in (
                "GROUND_TOP_LEFT", "GROUND_TOP_RIGHT",
                "GROUND_BOTTOM_LEFT", "GROUND_BOTTOM_RIGHT",
            ):
                self.assertTrue(any(
                    route[0] == f"{instance}.{contact}"
                    and route[1] == "abstract:rf-ground-dedicated-via"
                    for route in routes
                ))

        planes = candidate["interboard_contract"]["antenna_connector_planes"]
        self.assertEqual(
            "reviewed_exact_gct_outward_face_mounting_geometry",
            planes["status"],
        )
        self.assertEqual("outward_front", planes["ui_outer_face"]["face"])
        self.assertEqual("outward_rear", planes["rf_power_outer_face"]["face"])
        self.assertEqual(4, len(planes["ui_outer_face"]["ports"]))
        self.assertEqual(6, len(planes["rf_power_outer_face"]["ports"]))
        self.assertEqual(11.0, planes["separation"]["interboard_channel_mm"])
        self.assertEqual(14.2, planes["separation"]["outer_pcb_face_separation_mm"])
        self.assertEqual(20.55, planes["separation"]["antenna_centre_plane_separation_mm"])
        self.assertFalse(
            planes["separation"]["interboard_channel_contains_connector_bodies"]
        )

    def test_i8_generated_bom_inventory_exposes_every_current_gap(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual(
            "i8_paper_procurement_feasibility_reviewed_target_input_not_bom_freeze",
            candidate["bom_audit"]["status"],
        )
        lines = GENERATOR._target_bom_lines(self.database, candidate)
        self.assertEqual(1052, sum(line["quantity"] for line in lines))
        self.assertEqual(210, len(lines))
        self.assertEqual(
            0,
            sum(line["orderable_evidence"] == "missing" for line in lines),
        )
        self.assertEqual(
            9,
            sum(line["cost_evidence"] == "missing" for line in lines),
        )
        self.assertEqual(
            201,
            sum(line["cost_evidence"] == "present" for line in lines),
        )
        self.assertEqual(
            1038,
            sum(
                line["quantity"]
                for line in lines
                if line["cost_evidence"] == "present"
            ),
        )
        self.assertEqual(
            0,
            sum(line["alternate_evidence"] == "missing" for line in lines),
        )
        self.assertEqual(
            9,
            sum(bool(line["cost_gate_status"]) for line in lines),
        )
        self.assertEqual(
            {
                "SUB-RF",
                "SUB-PWR-PASSIVE",
                "SUB-CTRL-PASSIVE",
                "SUB-DISCRETE-PROT",
                "SUB-LOGIC-ANALOG",
                "SUB-PWR-SAFETY",
                "SUB-COMPUTE-RF",
                "SUB-MECH-OPTICAL",
            },
            {line["alternate_policy_class"] for line in lines},
        )

        display = self.database["devices"]["qdtech_hmx035ctft_001"]
        self.assertEqual(2, len(display["prototype_specimen_sources"]))
        self.assertEqual(
            "unresolved_production_panel_factory_quote_required",
            display["procurement_gate"]["status"],
        )
        self.assertIn(
            "no_drop_in_substitute",
            display["alternates"]["disposition"],
        )
        self.assertIn(
            "complete-donor geometry",
            display["donor_outline_source"]["scope"],
        )
        donor = display["prototype_donor_route"]
        self.assertEqual(
            "rejected_procurement_route_legacy_evidence_only",
            donor["status"],
        )
        self.assertEqual(0, donor["recommended_sample_quantity"])
        self.assertEqual(0.0, donor["published_sample_material_usd"])
        self.assertIn(
            "standalone raw-assembly orderable MPN",
            donor["does_not_close"],
        )

        gap_quantities = {
            row["id"]: row["quantity"]
            for row in candidate["bom_audit"]["required_uninstantiated_parts"]
        }
        self.assertNotIn("external_sma_bodies", gap_quantities)
        self.assertNotIn("nrf_rf_cable_assemblies", gap_quantities)
        self.assertNotIn("rf_cable_assemblies", gap_quantities)
        self.assertNotIn("m5_connector_bodies", gap_quantities)
        self.assertNotIn("actual_tx_threshold_networks", gap_quantities)
        self.assertEqual(12, gap_quantities["external_antenna_kit"])
        physical_gates = {
            row["id"]: row["resolution_gate"]["status"]
            for row in candidate["bom_audit"]["required_uninstantiated_parts"]
        }
        self.assertEqual(
            {
                "external_antenna_kit": "profile_variant_bom_and_hil_required",
            },
            physical_gates,
        )

        rendered = GENERATOR.render_target_bom_review(self.database, self.candidates)
        self.assertIn("**1053** architecture instances", rendered)
        self.assertIn("**1052** supplied/costed placements", rendered)
        self.assertIn("**210/210** used lines", rendered)
        self.assertIn("**210/210** lines", rendered)
        self.assertIn("**201/210** lines", rendered)
        self.assertIn("**1038/1052** supplied placements", rendered)
        self.assertIn("USD 251.9207", rendered)
        self.assertIn("12", rendered)
        self.assertIn("quantity_100_rfq_required", rendered)
        self.assertIn("retail_only_no_quantity_100_tier", rendered)
        self.assertIn("SUB-RF", rendered)
        self.assertIn("SUB-MECH-OPTICAL", rendered)
        self.assertIn("assembly-internal evidence node", rendered)
        self.assertIn("display_touch_controller", rendered)
        self.assertIn("Physical purchase families with explicit resolution gates", rendered)
        self.assertIn("I8 paper procurement-feasibility scope reviewed", rendered)
        self.assertNotIn("received_mate_and_routed_length_coupon_required", rendered)
        self.assertIn("Samtec HLE-107-02-G-DV-PE-LC", rendered)
        self.assertIn("profile_variant_bom_and_hil_required", rendered)
        self.assertNotIn(
            "sitronix_st77922",
            {line["device_id"] for line in lines},
        )
        self.assertIn("HMX035CTFT-001", rendered)
        self.assertIn("narrow screen", rendered)
        self.assertIn("PCB placement/routing, fabrication and purchasing remain unauthorized", rendered)

        cap_socket = self.database["devices"]["samtec_hle_107_02_g_dv_pe_lc"]
        self.assertIn("138 shown", cap_socket["orderable_source"]["document"])
        self.assertIn("locking-clip suffixes", cap_socket["availability_note"])
        self.assertEqual("not_drop_in_approved", cap_socket["alternate_gate"]["status"])

    def test_i9_joint_projection_classifies_every_abstract_endpoint(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        audit = candidate["i9_projection_audit"]
        self.assertEqual(
            "paper_reviewed_joint_target_projection",
            audit["status"],
        )
        policy = audit["fixed_route_abstract_policy"]
        classified = {
            endpoint
            for row in policy["classes"]
            for endpoint in row["endpoints"]
        }
        occurrences = [
            endpoint
            for route in candidate["fixed_routes"]
            for endpoint in (route["from"], route["to"])
            if endpoint.startswith("abstract:")
        ]
        self.assertEqual(44, policy["expected_unique_endpoint_count"])
        self.assertEqual(1313, policy["expected_occurrence_count"])
        self.assertEqual(set(occurrences), classified)
        self.assertEqual([], audit["unresolved_owner_decisions"])
        self.assertNotIn(
            "g3_physical_purchase_resolution_gate",
            {row["id"] for row in policy["classes"]},
        )

    def test_g2f_3i_records_joint_pre_schematic_review_without_authorizing_kicad(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual(
            "target_architecture_pre_schematic_reviewed",
            candidate["status"],
        )
        review = candidate["pre_schematic_review"]
        self.assertEqual("reviewed", review["status"])
        self.assertEqual("coherent_target_architecture", review["result"])
        self.assertEqual("not_granted_by_this_review", review["kicad_authorization"])
        self.assertIn(
            "cross-repository hardware/firmware integration contract",
            review["scope"],
        )
        rendered = GENERATOR.render_ledger(self.database, self.candidates)
        self.assertIn("историческая single-RP R1/G2F проекция", rendered)
        self.assertIn("отменяет её authority для текущей распиновки", rendered)
        pinout = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("историческая single-RP R1/G2F распиновка", pinout)
        self.assertIn("это не current R2 authority", pinout)

    def test_h1_r2_current_four_face_projection_is_current_and_complete(self):
        script = GENERATOR.REPO_ROOT / "hardware/product-design/h1_r2_layout.py"
        result = subprocess.run(
            [sys.executable, str(script), "--check"],
            cwd=GENERATOR.REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        rendered = (
            GENERATOR.REPO_ROOT
            / "docs/images/h1-r2-four-faces.svg"
        ).read_text(encoding="utf-8")
        for token in (
            "ER-TFT035IPS-6",
            "Cap-Bus slot · U214 / U219",
            "Keystone 1048P",
            "WI-FI/BLE",
            "WI-FI/15.4",
            "nRF24-1",
            "nRF24-2",
            "nRF24-3",
            "AIR/FM RX",
            "AM/LW RX",
            'data-instance="ui_dpad_up" data-direct-press="true"',
            'data-instance="ui_dpad_down" data-direct-press="true"',
            'data-instance="ui_dpad_left" data-direct-press="true"',
            'data-instance="ui_dpad_right" data-direct-press="true"',
            'data-instance="ui_dpad_ok" data-direct-press="true"',
            "RUN",
            "KILL",
            "PTT",
            "four matched PCB faces",
            "outer · user-facing silk",
            "inner · viewed after turning over · no silkscreen",
            "ACTIVE 48.96×73.44",
            "SUB-GHz",
            "V/U TX",
            "FAULT",
            "HEADSET",
            "CTIA",
            "SPEAKER",
            "MICROPHONE",
            "POWER + USB",
            "S3 RST",
            "S3 BOOT",
            "C5 RST",
            "C5 BOOT",
            "RP RST",
            "RP BOOT",
            "github.com/anton-vinogradov/esp32-leshy2",
        ):
            self.assertIn(token, rendered)

        projection = (
            GENERATOR.REPO_ROOT
            / "hardware/architecture/generated/G2F-3I-principled-projection.mmd"
        ).read_text(encoding="utf-8")
        for token in (
            'VOICE_V -->|"short controlled 50-Ohm line"| VOICE_V_EXTERNAL_SMA',
            "DET_VOICE_V --> EVIDENCE_CMP_VOICE_V",
            "EVIDENCE_CMP_VOICE_V --> EVIDENCE_MASK",
        ):
            self.assertIn(token, projection)
        self.assertNotIn("SPEAKER / GRILLE", rendered)
        self.assertNotIn('data-interface-kind="acoustic-opening"', rendered)
        for connector_silkscreen in ("2.4 GHz RP-SMA", "2.4/5 GHz RP-SMA", "2.4 GHz SMA"):
            self.assertNotIn(connector_silkscreen, rendered)
        navigation = (
            GENERATOR.REPO_ROOT
            / "docs/images/navigation-cluster.svg"
        ).read_text(encoding="utf-8")
        for token in (
            'data-view="series-navigation-cluster"',
            'data-design-id="L2-NAV-5B-001-A"',
            'data-manufacturing-class="serial-components-only"',
            "Five exact series buttons",
            "OMRON B3S-1100P",
        ):
            self.assertIn(token, navigation)
        internal = (
            GENERATOR.REPO_ROOT
            / "docs/images/internal-board-layout.svg"
        ).read_text(encoding="utf-8")
        for token in (
            "Leshy2 — dimensioned inner-board placement",
            "Numbered physical devices",
            'data-inner-silkscreen="none"',
            "Inner PCB faces contain no silkscreen text",
            "M2.5 hole/head keep-out",
            "antenna arrows reference outer-face ports",
            'data-view="mirrored-x"',
            "AS02404PO",
            "CMEJ-0413-42-SMT-TR",
            "JS102011SCQN",
            "TPS3435CAKAGDDFR",
            "SKRTLAE010",
            "FTSH-105-01-L-DV-K-P-TR",
            "Texas Instruments TMUX1136DGSR",
            "TCA4307DGKR",
            "Sunlord MWSA0503S-2R2MT",
            "Murata GRM31CR71E106MA12L",
            'data-zone="cc-reference-rf-network"',
            'data-opposing-pairs="46"',
            'data-min-z-clearance-mm="3.31"',
            'data-opposing-cable-pairs="2"',
            'data-rf-pcb-topology-guides="10"',
            'data-route-state="pre-ecad-topology-only"',
            'data-nrf-cable-reserves="3"',
            'data-nrf-reserve-opposing-pairs="6"',
            'data-encoder-through-features="7"',
            'data-voice-v-rf-endpoint-distance-mm="45.57"',
            'data-voice-u-rf-endpoint-distance-mm="47.33"',
            'data-path="S3-2G4"',
            'data-path="RX-FM/SW"',
            'data-path="RX-AM/LW"',
            'data-path="C5-2G4/5"',
            'data-path="N24-0"',
            'data-path="CC-SUB"',
            'data-path="N24-1"',
            'data-path="VOICE-VHF"',
            'data-path="VOICE-UHF"',
            'data-path="N24-2"',
            "Antenna-to-radio map · all ten paths",
            "solid green/cyan = direct cable projection · dashed blue = future 50 Ω PCB mainline",
            "module · no RF land; output is built-in U.FL",
            "module · ANT1 U.FL active; ANT2 land disabled",
            "PCB re-entry · feeds TX coupler and outer RP-SMA",
            'id="module-integrated-rf-connectors" data-count="5" data-exact-position-count="2" data-schematic-position-count="3"',
            'id="board-rf-cable-to-trace-handoffs" data-count="5"',
            'data-relation="module-output-and-cable-start"',
            'data-relation="physical-cable-end-and-pcb-trace-start"',
            "ring on S3/C5 = module U.FL · ring on nRF = module IPEX · numbered ring = board U.FL",
            "outward RP-SMA · antenna screws on here",
            "outward connector / through-hole tail clearance on the opposite face: ≥1.5 mm",
            "all mechanically significant bodies are accounted",
        ):
            self.assertIn(token, internal)
        self.assertNotIn('data-layer="pcb-silkscreen"', internal)
        self.assertEqual(2, internal.count('data-connector-bodies="omitted-outer-face"'))
        for forbidden_inner_silk in (
            "54 · MIC",
            "AS02404PO · speaker · side grille",
            "RUN/KILL request",
            "S3/C5 recovery controls and DBG10",
            "RP recovery controls and DBG10",
            "WI-FI/BLE",
        ):
            self.assertNotIn(forbidden_inner_silk, internal)
        self.assertIn('id="outer-antenna-datum-annotations" data-layer="drawing-annotation"', internal)
        self.assertEqual(
            [14.6, 18.1, 2.5],
            self.database["devices"]["ebyte_e01_ml01sp4"]["maximum_dimensions_mm"],
        )
        self.assertEqual(
            [35.6, 19.0, 3.2],
            self.database["devices"]["nicerf_sa818s_u_v18"]["maximum_dimensions_mm"],
        )
        self.assertEqual(
            [3.1, 5.05, 1.1],
            self.database["devices"]["ti_tmux1136_dgsr"]["maximum_dimensions_mm"],
        )
        self.assertEqual(
            [3.1, 5.05, 1.1],
            self.database["devices"]["tca4307dgkr"]["maximum_dimensions_mm"],
        )
        sandwich = (
            GENERATOR.REPO_ROOT
            / "docs/images/sandwich-section.svg"
        ).read_text(encoding="utf-8")
        for token in (
            'data-view="true-sections"',
            "Leshy2 — two physical cross-sections",
            "Each panel is one physical cut plane; zones are never combined.",
            "ER-TFT035IPS-6 + ER-TPC035-6",
            "FX8C M1 · exact 11-mm board-to-board gap",
            "AS02404PO",
            "2× 18650",
            "M5Stack U214",
            'id="section-u214" data-cut-y-mm="29"',
            'id="section-battery" data-cut-y-mm="82"',
            "No battery appears",
            "No installed Cap appears",
        ):
            self.assertIn(token, sandwich)

    def test_rejects_unclassified_i9_abstract_or_owner_decision(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        policy = candidate["i9_projection_audit"]["fixed_route_abstract_policy"]
        removed = policy["classes"][0]["endpoints"].pop()
        self.assertIn(
            f"I9 unclassified abstract endpoints ['{removed}']",
            "\n".join(self.errors_for(candidates)),
        )

        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["i9_projection_audit"]["unresolved_owner_decisions"] = [
            "test undecided owner"
        ]
        self.assertIn(
            "I9 has unresolved owner decisions",
            "\n".join(self.errors_for(candidates)),
        )

    def test_rejects_incomparable_or_undocumented_cost_evidence(self):
        cases = (
            ({"currency": "EUR"}, "cost currency must be USD"),
            ({"target_quantity": 99}, "cost target quantity must be 1 or 100"),
            ({"unit_price_usd": 0}, "cost unit price must be positive"),
            (
                {"source": {"document": "test", "url": "http://example.com", "checked": "2026-08-19"}},
                "cost source must use HTTPS",
            ),
            (
                {"source": {"document": "test", "url": "https://example.com", "checked": "19-08-2026"}},
                "cost source checked date must be YYYY-MM-DD",
            ),
        )
        for update, expected in cases:
            with self.subTest(expected=expected):
                database = copy.deepcopy(self.database)
                database["devices"]["esp32_s3_wroom_1u_n16r2"]["cost"].update(update)
                errors = GENERATOR.validate_sources(database, self.candidates)
                self.assertIn(expected, "\n".join(errors))

    def test_rejects_invalid_or_conflicting_cost_gate(self):
        cases = (
            ({"status": "invented"}, "unknown cost_gate status"),
            ({"reason": ""}, "cost_gate missing reason"),
            (
                {"source": {"document": "test", "url": "http://example.com", "checked": "2026-08-19"}},
                "cost_gate source must use HTTPS",
            ),
            (
                {"source": {"document": "test", "url": "https://example.com", "checked": "19-08-2026"}},
                "cost_gate source checked date must be YYYY-MM-DD",
            ),
        )
        for update, expected in cases:
            with self.subTest(expected=expected):
                database = copy.deepcopy(self.database)
                database["devices"]["m5_u214"]["cost_gate"].update(update)
                errors = GENERATOR.validate_sources(database, self.candidates)
                self.assertIn(expected, "\n".join(errors))

        database = copy.deepcopy(self.database)
        database["devices"]["m5_u214"]["cost"] = copy.deepcopy(
            database["devices"]["esp32_s3_wroom_1u_n16r2"]["cost"]
        )
        errors = GENERATOR.validate_sources(database, self.candidates)
        self.assertIn("cost and cost_gate are mutually exclusive", "\n".join(errors))

    def test_rejects_invalid_bom_non_purchase_boundary(self):
        cases = (
            (
                [{"instance": "missing", "parent_instance": "display", "reason": "test"}],
                "unknown instance 'missing'",
            ),
            (
                [{"instance": "display", "parent_instance": "display", "reason": "test"}],
                "instance cannot parent itself",
            ),
            (
                [
                    {"instance": "display_touch_controller", "parent_instance": "display", "reason": "test"},
                    {"instance": "display_touch_controller", "parent_instance": "display", "reason": "duplicate"},
                ],
                "duplicate BOM non-purchase instance",
            ),
        )
        for rows, expected in cases:
            with self.subTest(expected=expected):
                candidates = copy.deepcopy(self.candidates)
                candidate = next(c for c in candidates if c["id"] == "G2F-3I")
                candidate["bom_audit"]["non_purchase_instances"] = rows
                self.assertIn(expected, "\n".join(self.errors_for(candidates)))

    def test_rejects_incomplete_physical_purchase_resolution_gate(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        gaps = candidate["bom_audit"]["required_uninstantiated_parts"]
        del gaps[0]["resolution_gate"]["acceptance"]
        self.assertIn(
            "resolution gate missing acceptance",
            "\n".join(self.errors_for(candidates)),
        )

        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        gaps = candidate["bom_audit"]["required_uninstantiated_parts"]
        gaps[0]["resolution_gate"]["status"] = "generic_tbd"
        self.assertIn(
            "unsupported resolution gate status 'generic_tbd'",
            "\n".join(self.errors_for(candidates)),
        )

    def test_rejects_incomplete_or_duplicate_substitution_policy(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        classes = candidate["bom_audit"]["substitution_policy"]["classes"]
        omitted = classes[0]["device_ids"].pop()
        errors = "\n".join(self.errors_for(candidates))
        self.assertIn("BOM substitution policy omits current purchase lines", errors)
        self.assertIn(omitted, errors)

        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        classes = candidate["bom_audit"]["substitution_policy"]["classes"]
        duplicate = classes[0]["device_ids"][0]
        classes[1]["device_ids"].append(duplicate)
        self.assertIn(
            f"duplicate BOM substitution member {duplicate}",
            "\n".join(self.errors_for(candidates)),
        )

        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        classes = candidate["bom_audit"]["substitution_policy"]["classes"]
        classes[0]["device_ids"].append("sitronix_st77922")
        self.assertIn(
            "BOM substitution policy contains non-purchase lines",
            "\n".join(self.errors_for(candidates)),
        )

    def test_exact_polarized_holder_and_three_ntc_contract_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0077", contract["battery_holder_decision"])
        self.assertIn("Keystone Electronics 1048P", contract["battery_holder_profile"])
        self.assertIn("protected button-top", contract["battery_holder_profile"])
        self.assertIn("thermally worst slot", contract["battery_thermal_coupling"])
        self.assertNotIn(
            "mechanical reverse-insertion blocking and all NTC cell coupling",
            contract["remaining_i3"],
        )
        self.assertEqual("keystone_1048p", candidate["instances"]["pack_holder"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("pack_holder.SLOT0_POS", "pack_fuse0.END_1", "PACK_SLOT0_POSITIVE_RAW"),
            ("pack_holder.SLOT0_NEG", "pack_gauge.GND", "PACK_LOCAL_GND"),
            ("pack_holder.SLOT1_NEG", "abstract:protected-2s-midpoint", "PACK_2S_MIDPOINT"),
            ("pack_holder.SLOT1_POS", "pack_fuse1.END_1", "PACK_SLOT1_POSITIVE_RAW"),
        ):
            self.assertIn(route, routes)

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("Keystone Electronics 1048P", rendered)
        self.assertIn("indexed thermally worst-slot contact", rendered)

    def test_exact_2n7002dw_sot363_pin_and_channel_map_cannot_regress(self):
        expected_pin_map = {
            "1": "S2", "2": "G2", "3": "D1",
            "4": "S1", "5": "G1", "6": "D2",
        }
        device = self.database["devices"]["diodes_2n7002dw_7_f"]
        self.assertEqual(
            expected_pin_map,
            {str(row["physical"]): contact for contact, row in device["contacts"].items()},
        )
        self.assertEqual(expected_pin_map, device["pinout_invariant"]["physical_pin_to_contact"])

        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["sot363_2n7002dw_contract"]
        self.assertEqual("C83571", contract["jlcpcb_part"])
        self.assertEqual(expected_pin_map, contract["physical_pin_to_contact"])
        self.assertEqual(
            {"pack_hold", "pack_status_buffer", "safe_reset_sink_a", "safe_reset_sink_b"},
            set(contract["instances"]),
        )
        self.assertEqual(
            {"G1": "S3_RESET_KILL_GATE", "S1": "SAFETY_GROUND", "D1": "S3_RESET_N"},
            contract["instances"]["safe_reset_sink_a"]["channel_1"],
        )
        self.assertEqual(
            {"G2": "SAFETY_GROUND", "S2": "SAFETY_GROUND", "D2": "NO_CONNECT"},
            contract["instances"]["safe_reset_sink_b"]["channel_2"],
        )

        broken_database = copy.deepcopy(self.database)
        broken_database["devices"]["diodes_2n7002dw_7_f"]["contacts"]["S2"]["physical"] = "6"
        errors = GENERATOR.validate_sources(broken_database, self.candidates)
        self.assertTrue(any("SOT363 physical pin map" in error for error in errors), errors)

        broken_candidates = copy.deepcopy(self.candidates)
        broken = next(c for c in broken_candidates if c["id"] == "G2F-3I")
        broken["sot363_2n7002dw_contract"]["instances"]["pack_hold"]["channel_2"]["D2"] = "SYS_INT_N"
        errors = GENERATOR.validate_sources(self.database, broken_candidates)
        self.assertTrue(any("pack_hold channel-to-net map" in error for error in errors), errors)

    def test_exact_max17320_2s_support_and_safe_status_interface_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0100", contract["manager_support_decision"])
        self.assertIn("CELL1/CELL2/CELL3", contract["manager_support_profile"])
        self.assertIn("Paper electrical closure does not replace", contract["manager_support_profile"])

        expected_instances = {
            "pack_in_res": "panasonic_erj_p08f10r0v",
            "pack_in_bypass": "yageo_cc0402krx7r9bb104",
            "pack_cp_cap": "murata_grm188r71e474ka12d",
            "pack_aoldo_cap": "murata_grm188r71e474ka12d",
            "pack_reg3_cap": "murata_grm188r71e474ka12d",
            "pack_reg2_cap": "murata_grm188r71e474ka12d",
            "pack_cell1_rbal": "panasonic_erj_p08f49r9v",
            "pack_batts_rbal": "panasonic_erj_p08f49r9v",
            "pack_cell1_filter_cap": "yageo_cc0402krx7r9bb104",
            "pack_batts_filter_cap": "yageo_cc0402krx7r9bb104",
            "pack_pckp_res": "yageo_rc0402fr_071kl",
            "pack_chg_gate_cap": "yageo_cc0402krx7r9bb104",
            "pack_dis_gate_cap": "yageo_cc0402krx7r9bb104",
            "pack_hold_pullup": "yageo_rc0402fr_0710kl",
            "pack_hold_release_pulldown": "yageo_rc0402fr_0710kl",
            "pack_alrt_pullup": "yageo_rc0402fr_0710kl",
            "pack_status_buffer": "diodes_2n7002dw_7_f",
            "pack_pfail_pullup": "yageo_rc0402fr_0710kl",
            "pack_irq_gate_pulldown": "yageo_rc0402fr_0710kl",
            "pack_gauge_scl_pullup": "yageo_rc0402fr_0710kl",
            "pack_gauge_sda_pullup": "yageo_rc0402fr_0710kl",
            "pack_admission_bulk_cap": "murata_grm188r60j106me47d",
            "pack_admission_bypass": "yageo_cc0402krx7r9bb104",
            "pack_admission_reset_pullup": "yageo_rc0402fr_0747kl",
            "pack_admission_reset_cap": "murata_grm155r71h103ka88d",
            "power_command_switch": "ck_js102011scqn",
            "power_command_pullup": "yageo_rc0402fr_0747kl",
            "power_command_filter": "yageo_cc0402krx7r9bb104",
            "run_loop_pullup": "yageo_rc0402fr_0710kl",
            "run_loop_filter": "yageo_cc0402krx7r9bb104",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("abstract:qualified-2s-positive", "pack_in_res.END_1", "BATTERY_STACK_POSITIVE"),
            ("pack_gauge.CP", "pack_cp_cap.END_1", "PACK_CHARGE_PUMP"),
            ("pack_cp_cap.END_2", "pack_gauge.IN", "PACK_GAUGE_IN"),
            ("pack_gauge.CELL1", "pack_gauge.CELL2", "PACK_CELL1_SENSE"),
            ("pack_gauge.CELL2", "pack_gauge.CELL3", "PACK_CELL1_SENSE"),
            ("pack_holder.SLOT0_NEG", "pack_shunt.END_1", "BATTERY_STACK_NEGATIVE_CELL_SIDE"),
            ("pack_shunt.END_2", "abstract:power-ground", "POWER_GROUND"),
            ("pack_gauge.PFAIL", "pack_status_buffer.G1", "PACK_PFAIL_RAW"),
            ("pack_status_buffer.D1", "pack_admission.PA16", "PACK_PFAIL_N"),
            ("pack_admission.PA23", "pack_status_buffer.G2", "PACK_SYS_INT_REQ"),
            ("pack_status_buffer.D2", "s3.GPIO45", "SYS_INT_N"),
            ("pack_admission.VDD", "power_command_pullup.END_1", "PACK_ADMISSION_VDD"),
            ("power_command_pullup.END_2", "pack_admission.PA24", "POWER_COMMAND_OFF_N"),
            ("power_command_pullup.END_2", "power_command_switch.THROW_B", "POWER_COMMAND_OFF_N"),
            ("power_command_switch.COMMON", "abstract:power-ground", "POWER_GROUND"),
            ("abstract:AON_SAFE_3V3", "run_loop_pullup.END_1", "AON_SAFE_3V3"),
            ("run_loop_pullup.END_2", "power_command_switch.THROW_A", "RUN_LOOP_RAW"),
            ("run_loop_pullup.END_2", "safe_conditioner.1A", "RUN_LOOP_RAW"),
            ("power_command_pullup.END_2", "power_command_filter.END_1", "POWER_COMMAND_OFF_N"),
            ("power_command_filter.END_2", "abstract:power-ground", "POWER_GROUND"),
            ("pack_gauge.TH3", "pack_gauge.GND", "PACK_TH3_UNUSED_LOW"),
            ("pack_gauge.TH4", "pack_gauge.GND", "PACK_TH4_UNUSED_LOW"),
        ):
            self.assertIn(route, routes)

        route_text = "\n".join(
            f"{route['from']} {route['to']} {route['net']}"
            for route in candidate["fixed_routes"]
        )
        self.assertNotIn("abstract:exact-value-hold-gate-pullup", route_text)
        self.assertNotIn("abstract:pack-admission reset-safe open-drain IRQ circuit", route_text)

        balance = self.database["devices"]["panasonic_erj_p08f49r9v"]["electrical_contract"]
        self.assertGreater(
            balance["rated_power_w"],
            balance["max_2s_cell1_balance_dissipation_w_at_4_3v"],
        )

        command_switch = self.database["devices"]["ck_js102011scqn"]
        self.assertEqual("C&K JS102011SCQN", command_switch["mpn"])
        self.assertEqual("active_orderable", command_switch["lifecycle"])
        self.assertEqual([8.5, 3.5, 3.6], command_switch["dimensions_mm"])
        self.assertEqual(
            "low-current command input only; never carries cell, SYS, charge or load current",
            command_switch["electrical_contract"]["use"],
        )

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "Panasonic ERJ-P08F49R9V<br/>49.9-Ohm 0.66-W bottom-cell balancing resistor",
            "Panasonic ERJ-P08F49R9V<br/>49.9-Ohm 0.66-W top-cell balancing resistor",
            "Diodes Incorporated 2N7002DW-7-F<br/>dual PFAIL level translator and passive-drain system IRQ",
            "Yageo RC0402FR-0747KL<br/>47-kOhm admission-controller NRST pull-up resistor",
        ):
            self.assertIn(label, rendered)

    def test_principled_pinout_is_derived_from_current_leading_budget(self):
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("| `s3` | `ESP32-S3-WROOM-1U-N16R8` | 33 | 0 | 0 | 33 |", rendered)
        self.assertIn("| `c5` | `ESP32-C5-WROOM-1U-N8R8` | 14 | 6 | 1 | 21 |", rendered)
        self.assertIn("| `rp` | `SC1512-A4` |", rendered)
        self.assertIn("| 48 | 0 | 0 | 48 |", rendered)
        self.assertIn("`RP=0 free`", rendered)
        self.assertIn("GPIO30", rendered)
        self.assertIn("QSPI_SS_USB_BOOT", rendered)

    def test_principled_diagram_names_each_physical_device_and_role(self):
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("flowchart TD", rendered)
        self.assertIn("Отрисовываемый атлас физических устройств", rendered)
        required_labels = (
            "HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3.5-inch QSPI IPS display and capacitive-touch assembly",
            "Sitronix ST77922<br/>integrated display plus capacitive-touch TDDI COG",
            "Hirose DM3AT-SF-PEJM5<br/>push-push microSD card connector",
            "Everest Semiconductor ES8311<br/>mono ADC/DAC audio codec",
            "TLV9061IDBVR<br/>active high-impedance capture buffer",
            "Texas Instruments TMUX1136DGSR<br/>dual differential RX-bypass/codec speaker selector",
            "Texas Instruments TS5A63157DCKR<br/>electret/codec transmit-audio selector",
            "Texas Instruments SN74LVC2G08DCUR<br/>direct-AUDIO_ARM dual selector-request gate",
            "Diodes Incorporated PAM8302AAYCR<br/>reset-off mono Class-D speaker amplifier",
            "Texas Instruments TPS3839K33DBZR<br/>3.08-V 200-ms codec interface supervisor",
            "Same Sky CMEJ-0413-42-SMT-TR<br/>top-port analog electret microphone",
            "PUI Audio AS02404PO<br/>24-by-12-mm 4-Ohm internal loudspeaker",
            "Texas Instruments TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path",
            "onsemi CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM",
            "Texas Instruments TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection",
            "Texas Instruments BQ25798RQMR<br/>2S-configured buck-boost charger and NVDC system power path",
            "Analog Devices MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing",
            "Texas Instruments MSPM0C1106SDGS20R<br/>fail-closed pair admission, watchdog and service bridge",
            "Texas Instruments CSD87313DMS<br/>fully-switching common-drain CHG/DIS power pair",
            "Littelfuse 0451005.MRL<br/>slot-0 independent 5-A fast fuse",
            "Littelfuse 0451005.MRL<br/>slot-1 independent 5-A fast fuse",
            "Vishay WSL25125L000FEA<br/>5-mOhm Kelvin current shunt",
            "TDK B57332V5103F360<br/>cell-0 temperature sensor",
            "TDK B57332V5103F360<br/>cell-1 temperature sensor",
            "Keystone Electronics 1048P<br/>polarized dual protected-button-top 18650 retention and four independent contacts",
            "XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #0",
            "XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #1",
            "Diodes Incorporated 2N7002DW-7-F<br/>reset-default ALRT hold and explicit release",
            "onsemi BAV70LT1G<br/>AOLDO/fixture source isolation",
            "Diodes Incorporated BAT54-7-F<br/>admitted-system source isolation and priority",
            "Texas Instruments TPUL2G223BQBR<br/>non-retriggerable pulse limiter and refractory lockout",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% diagnostic-pulse timing resistor",
            "Murata GRM31C5C1H224JE02L<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor",
            "Yageo RC0402FR-07620KL<br/>620-kOhm 1% refractory-lockout timing resistor",
            "TDK C1608X7R1C105K080AC<br/>1-uF 16-V X7R refractory-lockout timing capacitor",
            "Yageo CC0402KRX7R9BB104<br/>100-nF 50-V X7R one-shot bypass capacitor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-trigger fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-gate fail-low resistor",
            "Diodes Incorporated DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET",
            "Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #0",
            "Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #1",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #0",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #1",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% midpoint-divider bottom resistor",
            "Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R midpoint ADC filter capacitor",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #0",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #1",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #2",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #3",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #4",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% stack-divider bottom resistor",
            "Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R stack ADC filter capacitor",
            "Texas Instruments TPS629203DRLR<br/>low-IQ always-on 3.3-V safety converter",
            "Sunlord WPN201612H2R2MT<br/>2.2-uH shielded AON converter inductor",
            "Yageo RC0402FR-0742K2L<br/>42.2-kOhm 1% AON mode/configuration resistor",
            "TDK CGA5L1X7R1E475K160AC<br/>4.7-uF 25-V X7R AON input capacitor",
            "Murata GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON raw-output capacitor",
            "Texas Instruments TPS25961DRVR<br/>independent AON overvoltage/current/short cutoff",
            "Yageo RC0402FR-07240KL<br/>240-kOhm 1% AON eFuse current-limit resistor",
            "Yageo RC0402FR-07196KL<br/>196-kOhm 1% AON eFuse OVLO top resistor",
            "Murata GRM188R60J106ME47D<br/>10-uF 6.3-V X5R protected-AON output capacitor",
            "Yageo RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% AON POR pull-up resistor",
            "Texas Instruments TPS564252DRLR<br/>feedback-set 3.222-V 4-A main converter",
            "Sunlord MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main-converter bulk input capacitor",
            "Yageo CC0402KRX7R9BB104<br/>100-nF 50-V X7R main-converter HF input capacitor",
            "Vishay TNPW040243K7BEED<br/>43.7-kOhm 0.1% main feedback top resistor",
            "Vishay TNPW040210K0BEED<br/>10-kOhm 0.1% main feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G main feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #1",
            "Texas Instruments TPS25974LRPWR<br/>main latch-off overvoltage circuit-breaker eFuse with protected PG",
            "Yageo RT0402BRD07191KL<br/>191-kOhm 0.1% main eFuse OVLO top resistor",
            "Yageo RT0402BRD07100KL<br/>100-kOhm 0.1% main eFuse OVLO bottom resistor",
            "Yageo RC0402FR-07100KL<br/>100-kOhm 1% main-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% wired-low power-fault pull-up resistor",
            "Texas Instruments TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter",
            "Sunlord MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice-converter bulk input capacitor",
            "Yageo CC0402KRX7R9BB104<br/>100-nF 50-V X7R voice-converter HF input capacitor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor",
            "Yageo RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G voice feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #1",
            "Texas Instruments TPS25974LRPWR<br/>voice latch-off overvoltage circuit-breaker eFuse with protected PG",
            "UNI-ROYAL 0402WGF2703TCE<br/>270-kOhm 1% voice eFuse OVLO top resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice power-good pull-up resistor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice PG-qualifier base resistor",
            "Diodes Incorporated MMBT3904-7-F<br/>voice-rail enable-qualified PG fault transistor",
            "Texas Instruments TPS564252DRLR<br/>fixed 5.0-V 4-A accessory converter",
            "Sunlord MWSA0503S-4R7MT<br/>4.7-uH accessory-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory-converter bulk input capacitor",
            "Yageo CC0402KRX7R9BB104<br/>100-nF 50-V X7R accessory-converter HF input capacitor",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% accessory feedback top resistor",
            "Yageo RC0402FR-0730KL<br/>30-kOhm 1% accessory feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G accessory feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #1",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory power-good pull-up resistor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% accessory PG-qualifier base resistor",
            "Diodes Incorporated MMBT3904-7-F<br/>accessory-rail enable-qualified PG fault transistor",
            "Texas Instruments TPS259470LRPWR<br/>true-reverse-blocking latch-off accessory eFuse and current monitor",
            "Yageo RC0402FR-071K82L<br/>1.82-kOhm 1% eFuse current-limit resistor",
            "Murata GRM155R71H472KA01D<br/>4.7-nF 50-V X7R eFuse startup-slew capacitor",
            "Murata GRM188R71E224KA88D<br/>220-nF 25-V X7R post-start transient-timer capacitor",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% eFuse OVLO top resistor",
            "Yageo RC0402FR-0747KL<br/>47-kOhm 1% eFuse OVLO bottom resistor",
            "Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse input capacitor",
            "Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse output capacitor",
            "Yageo RC0603FR-071KL<br/>1-kOhm 1% protected-output discharge resistor",
            "Texas Instruments TPS22919DCKR<br/>three-radio nRF quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>CC1101 quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>microSD quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>ES8311 quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>Si4732 quiet-state load switch",
            "SN74LVC3G34DCUR<br/>three-channel Ioff SCK/CMD/CS card-side buffer",
            "Texas Instruments SN74LVC1G125DCKR<br/>CS-gated Ioff DAT0/MISO return buffer",
            "Texas Instruments TPD4E05U06DQAR<br/>four-channel low-capacitance microSD signal ESD array A",
            "Texas Instruments TPD4E05U06DQAR<br/>four-channel low-capacitance microSD supply/signal/detect ESD array B",
            "TDK C1608X7R1C105K080AC<br/>1-uF storage-switch input bypass capacitor",
            "Murata GRM21BR60J226ME39L<br/>22-uF switched-card bulk capacitor",
            "Panasonic ERJ-2RKF22R0X<br/>22-Ohm buffered-card clock source-series resistor",
            "Panasonic ERJ-2RKF22R0X<br/>22-Ohm card-MISO buffer source-series resistor",
            "Yageo RC0603FR-071KL<br/>1-kOhm card-detect input series resistor",
            "Yageo CC0402KRX7R9BB104<br/>100-nF card-detect hardware filter capacitor",
            "Vishay TSOP75238TR<br/>38-kHz AGC2 demodulating IR receiver",
            "Vishay TSMP95000TT<br/>30-to-60-kHz carrier-learning IR receiver",
            "Vishay VSMY14940<br/>side-view 940-nm consumer IR transmit emitter",
            "TLV9061IDBVR<br/>AON physical-optical transimpedance amplifier",
        )
        for label in required_labels:
            self.assertIn(label, rendered)
        for forbidden in (
            "display + separate microSD",
            "codec + Si4732-A10-GSR",
            "dual RX + TX IR frontend",
            "nRF24 #0",
        ):
            self.assertNotIn(forbidden, rendered)
        self.assertIn("SN74LVC1G06DCKR", rendered)

    def test_target_readme_principled_diagrams_stay_vertical_and_current(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        overview_instances = (
            "s3", "c5", "rp", "display", "sd", "slow_io", "ui_matrix_io",
            "codec", "receiver", "nrf0", "nrf1", "nrf2", "cc", "voice",
            "u214", "product_usb_connector", "product_usb_protector",
            "pd_vbus_tvs", "pd_controller", "nvdc_charger", "pack_holder", "pack_gauge",
            "aon_buck", "main_buck", "voice_buck", "ext_buck",
            "ir_demod", "ir_carrier", "ir_emitter",
        )
        current_mpn_tokens = set()
        for instance in overview_instances:
            device_id = candidate["instances"][instance]
            mpn = self.database["devices"][device_id]["mpn"]
            part_tokens = [
                token.strip("(),")
                for token in mpn.split()
                if any(character.isdigit() for character in token)
            ]
            current_mpn_tokens.add(max(part_tokens, key=len))

        raw_projection = (
            GENERATOR.REPO_ROOT
            / "hardware/architecture/generated/G2F-3I-principled-projection.mmd"
        ).read_text(encoding="utf-8")

        def assert_individual_mpn_nodes(expected: dict[str, str], context: str) -> None:
            for mpn in set(expected.values()):
                required = sum(1 for value in expected.values() if value == mpn)
                actual = len(
                    re.findall(
                        rf'^  [A-Z0-9_]+\["[^"\n]*{re.escape(mpn)}<br/>',
                        raw_projection,
                        re.MULTILINE,
                    )
                )
                self.assertGreaterEqual(
                    actual,
                    required,
                    f"{context}: expected {required} individual {mpn} nodes, found {actual}",
                )

        def assert_no_implicit_mermaid_nodes(diagram: str, context: str) -> None:
            declared = set(
                re.findall(r'^\s{0,2}([A-Z][A-Z0-9_]*)\s*(?:\[|\()', diagram, re.MULTILINE)
            )
            for line in diagram.splitlines():
                if not any(token in line for token in ("-->", "<-->", "-.->", "~~~")):
                    continue
                unlabeled = re.sub(r'\|".*?"\|', "", line)
                referenced = set(
                    re.findall(r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]*)(?![A-Z0-9_])", unlabeled)
                )
                self.assertLessEqual(
                    referenced,
                    declared,
                    f"{context}: implicit Mermaid nodes {sorted(referenced - declared)} in {line}",
                )

        architecture_svg = (
            GENERATOR.REPO_ROOT / "docs/images/h0-r2-functional-architecture.svg"
        ).read_text(encoding="utf-8")
        for doc_name in ("docs/hardware.md", "docs/hardware.ru.md"):
            public_doc = (GENERATOR.REPO_ROOT / doc_name).read_text(encoding="utf-8")
            self.assertIn("images/h0-r2-functional-architecture.svg", public_doc, doc_name)
            self.assertEqual([], re.findall(r"```mermaid\n(.*?)```", public_doc, re.DOTALL), doc_name)
        for token in ("ESP32-S3-WROOM-1U-N16R8", "ESP32-C5-WROOM-1U-N8R8", "SC1512-A4"):
            self.assertIn(token, architecture_svg)
        for token in ("FRONT · UI / RADIO PCB", "REAR · RF / POWER PCB", "M1", "NO ONBOARD VIDEO RX"):
            self.assertIn(token, architecture_svg)
            self.assertNotIn("CVBS", architecture_svg)
            for mpn_token in current_mpn_tokens:
                self.assertIn(
                    mpn_token,
                    raw_projection,
                    f"raw projection: missing current MPN token {mpn_token}",
                )
            storage_nodes = {
                "SWSD": "TPS22919DCKR",
                "SD": "DM3AT-SF-PEJM5",
                "SDHBUF": "SN74LVC3G34DCUR",
                "SDMBUF": "SN74LVC1G125DCKR",
                "SDESDA": "TPD4E05U06DQAR",
                "SDESDB": "TPD4E05U06DQAR",
                "SDINCAP": "C1608X7R1C105K080AC",
                "SDBULK": "GRM21BR60J226ME39L",
                "SDHFCAP": "CC0402KRX7R9BB104",
                "SDHBUFCAP": "CC0402KRX7R9BB104",
                "SDMBUFCAP": "CC0402KRX7R9BB104",
                "SDONPD": "RC0402FR-0710KL",
                "SDSCKPD": "RC0402FR-0710KL",
                "SDD0PU": "RC0402FR-0710KL",
                "SDD1PU": "RC0402FR-0710KL",
                "SDHCS": "RC0402FR-0710KL",
                "LCDHCS": "RC0402FR-0710KL",
                "SDCPUCMD": "RC0402FR-0710KL",
                "SDCPUD0": "RC0402FR-0710KL",
                "SDCPUD1": "RC0402FR-0710KL",
                "SDCPUD2": "RC0402FR-0710KL",
                "SDCPUD3": "RC0402FR-0710KL",
                "SDSCKR": "ERJ-2RKF22R0X",
                "SDCMDR": "ERJ-2RKF22R0X",
                "SDCSR": "ERJ-2RKF22R0X",
                "SDMISOR": "ERJ-2RKF22R0X",
                "SDDETR": "RC0603FR-071KL",
                "SDDETPU": "RC0402FR-0710KL",
                "SDDETC": "CC0402KRX7R9BB104",
            }
            assert_individual_mpn_nodes(storage_nodes, f"{doc_name}: storage")
            touch_nodes = {
                "LCDTDDI": "Sitronix ST77922",
                "TPIRQPU": "RC0402FR-0710KL",
                "TPIRQ": "SN74LVC1G07DCKR",
            }
            assert_individual_mpn_nodes(touch_nodes, f"{doc_name}: touch")
            pack_support_nodes = {
                "PACKINR": "ERJ-P08F10R0V",
                "PACKINC": "CC0402KRX7R9BB104",
                "PACKCPC": "GRM188R71E474KA12D",
                "PACKAOC": "GRM188R71E474KA12D",
                "PACKR3C": "GRM188R71E474KA12D",
                "PACKR2C": "GRM188R71E474KA12D",
                "PACKRB1": "ERJ-P08F49R9V",
                "PACKRB4": "ERJ-P08F49R9V",
                "PACKCF1": "CC0402KRX7R9BB104",
                "PACKCF4": "CC0402KRX7R9BB104",
                "PACKPCKR": "RC0402FR-071KL",
                "PACKCGC": "CC0402KRX7R9BB104",
                "PACKDGC": "CC0402KRX7R9BB104",
                "PACKHOLDPU": "RC0402FR-0710KL",
                "PACKRELDPD": "RC0402FR-0710KL",
                "PACKALRTPU": "RC0402FR-0710KL",
                "PACKSTAT": "2N7002DW-7-F",
                "PACKPFAILPU": "RC0402FR-0710KL",
                "PACKIRQPD": "RC0402FR-0710KL",
                "PACKSCLPU": "RC0402FR-0710KL",
                "PACKSDAPU": "RC0402FR-0710KL",
                "PACKMCUBULK": "GRM188R60J106ME47D",
                "PACKMCUHF": "CC0402KRX7R9BB104",
                "PACKRSTPU": "RC0402FR-0747KL",
                "PACKRSTC": "GRM155R71H103KA88D",
            }
            assert_individual_mpn_nodes(pack_support_nodes, f"{doc_name}: pack support")
            self.assertIn("SN74LVC1G06DCKR", raw_projection, doc_name)
            self.assertIn("SN74LVC1G07DCKR", raw_projection, doc_name)

        atlas = GENERATOR.render_principled_pinout(self.database, self.candidates)
        atlas_diagrams = re.findall(r"```mermaid\n(.*?)```", atlas, re.DOTALL)
        self.assertGreater(len(atlas_diagrams), 10)
        for diagram in atlas_diagrams:
            self.assertLess(len(diagram), GENERATOR.MERMAID_RENDER_LIMIT)
            assert_no_implicit_mermaid_nodes(diagram, "generated atlas")
        self.assertNotIn("```text", atlas)

    def test_public_hardware_pages_link_the_exact_pin_assignment(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")

        def contacts(instance, prefixes):
            selected = {
                row["contact"]
                for row in candidate["allocations"]
                if row["instance"] == instance
                and any(row["net"].startswith(prefix) for prefix in prefixes)
            }
            return ",".join(sorted(selected, key=GENERATOR.natural_contact_key))

        for instance, prefixes in (
            ("s3", ("S3_C5_",)),
            ("c5", ("S3_C5_",)),
            ("s3", ("S3_RP_", "RP_ALERT_")),
            ("rp", ("S3_RP_", "RP_ALERT_")),
            ("s3", ("DISPLAY_SD_", "SD_SPI_", "LCD_")),
            ("s3", ("I2S_", "SYS_I2C_")),
            ("s3", ("UNIT_",)),
            ("c5", ("IR_",)),
            ("rp", ("NRF0_",)),
            ("rp", ("NRF1_",)),
            ("rp", ("NRF2_",)),
            ("rp", ("CC_",)),
            ("rp", ("VOICE_", "PTT_")),
            ("rp", ("U214_",)),
        ):
            self.assertTrue(contacts(instance, prefixes), f"{instance}: {prefixes}")

        for doc_name in ("docs/hardware.md", "docs/hardware.ru.md"):
            public_doc = (GENERATOR.REPO_ROOT / doc_name).read_text(encoding="utf-8")
            self.assertIn("h0-r2-functional-architecture.svg", public_doc, doc_name)
            self.assertIn("43 used / 5 free" if doc_name.endswith("hardware.md") else "43 занято / 5 свободно", public_doc)

    def test_target_readmes_remain_product_sites_not_review_ledgers(self):
        for readme_name in ("README.md", "README.ru.md"):
            readme = (GENERATOR.REPO_ROOT / readme_name).read_text(encoding="utf-8")
            for ledger_prefix in ("DEC-", "REV-", "FND-", "IMP-"):
                self.assertNotIn(ledger_prefix, readme, readme_name)
            for stale_heading in ("## Development state", "## Состояние разработки"):
                self.assertNotIn(stale_heading, readme, readme_name)
            for wide_table_heading in (
                "| Principled group |",
                "| Принципиальная группа |",
            ):
                self.assertNotIn(wide_table_heading, readme, readme_name)
            for process_path in ("docs/status", "docs/review", "docs/stages"):
                self.assertNotIn(process_path, readme, readme_name)
            self.assertIn("docs/hardware", readme, readme_name)
            self.assertIn("docs/safety", readme, readme_name)

    def test_target_readmes_keep_parallel_user_cell_behavior(self):
        expected = {
            "docs/hardware.md": (
                "user-supplied protected 18650", "operate in parallel", "One cell can run",
                "USB is the only alternate", "MSPM0C1106SDGS20R",
            ),
            "docs/hardware.ru.md": (
                "защищённых пользовательских 18650", "соединены параллельно", "работать от одного",
                "альтернативный источник питания — USB", "MSPM0C1106SDGS20R",
            ),
        }
        for doc_name, phrases in expected.items():
            public_doc = (GENERATOR.REPO_ROOT / doc_name).read_text(encoding="utf-8")
            normalized = " ".join(public_doc.split()).lower()
            for phrase in phrases:
                self.assertIn(phrase.lower(), normalized, doc_name)

    def test_sink_only_30w_pd_front_end_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0063", contract["decision"])
        self.assertEqual("DEC-0065", contract["battery_decision"])
        self.assertEqual("DEC-0066", contract["manager_decision"])
        self.assertEqual("DEC-0067", contract["manager_circuit_decision"])
        self.assertIn("supervised 2S", contract["battery_topology"])
        self.assertIn("both cells required", contract["battery_topology"])
        self.assertIn("MAX17320G20+T", contract["battery_manager"])
        self.assertIn("MSPM0C1106SDGS20R", contract["battery_manager"])
        self.assertIn("refuses any cell", contract["battery_recovery_policy"])
        self.assertIn("prequal are disabled", contract["battery_recovery_policy"])
        self.assertEqual(
            ["5V fallback at advertised Type-C current (<=3A)", "9V@3A", "15V@2A"],
            contract["sink_pdos"],
        )
        self.assertEqual(30, contract["maximum_input_power_w"])
        self.assertIn("source mode", contract["disabled"])
        self.assertIn("20V PDO", contract["disabled"])
        self.assertIn("USB Full-Speed", contract["usb2_data"])
        self.assertIn("22-Ohm series resistors", contract["usb2_data"])
        self.assertIn("SYS_INT_N", contract["host_control"])
        self.assertIn("without consuming a dedicated GPIO", contract["host_control"])
        self.assertEqual("DEC-0078", contract["diagnostic_decision"])
        self.assertIn("non-retriggerable", contract["diagnostic_load_profile"])
        self.assertIn("28.7-40.7 ms", contract["diagnostic_load_profile"])
        self.assertIn("25-50 ms", contract["diagnostic_load_profile"])
        self.assertIn("PA25/ADC0_2", contract["admission_adc_profile"])
        self.assertIn("PA26/ADC0_1", contract["admission_adc_profile"])
        self.assertIn("PA16/ADC0_14", contract["admission_adc_profile"])
        self.assertIn("PA27/ADC0_0", contract["admission_adc_profile"])
        self.assertEqual("DEC-0079", contract["battery_cell_decision"])
        self.assertIn("XTAR 18650 4000mAh", contract["battery_cell_profile"])
        self.assertIn("28.8Wh", contract["battery_cell_profile"])
        self.assertIn("2A", contract["charge_limit"])
        self.assertEqual("DEC-0080", contract["source_sequence_decision"])
        self.assertEqual("DEC-0081", contract["internal_rail_protection_decision"])
        self.assertIn("TPS25961DRVR", contract["internal_rail_protection_profile"])
        self.assertIn("TPS25974LRPWR", contract["internal_rail_protection_profile"])
        self.assertEqual("DEC-0082", contract["paper_closure_decision"])
        self.assertIn("paper electrical scope reviewed", contract["paper_closure_status"])
        self.assertTrue(all("HIL" in item or "procurement" in item for item in contract["remaining_i3"]))
        self.assertEqual(0.85, contract["source_power_reserve"]["paper_efficiency_factor"])
        self.assertEqual(25.5, contract["source_power_reserve"]["best_case_pdo_sys_w"]["15V_2A"])

        expected_instances = {
            "pd_controller": "ti_tps25751d_refr",
            "pd_config_eeprom": "onsemi_cat24c512wi_gt3",
            "pd_vbus_tvs": "ti_tvs2200_drvr",
            "nvdc_charger": "ti_bq25798_rqmr",
            "pack_power_fet": "ti_csd87313dms",
            "pack_fuse0": "littelfuse_0451005_mrl",
            "pack_fuse1": "littelfuse_0451005_mrl",
            "pack_shunt": "vishay_wsl25125l000fea",
            "pack_ntc0": "tdk_b57332v5103f360",
            "pack_ntc1": "tdk_b57332v5103f360",
            "pack_holder": "keystone_1048p",
            "pack_cell0": "xtar_18650_4000mah_protected",
            "pack_cell1": "xtar_18650_4000mah_protected",
            "safe_por_pullup": "yageo_rc0402fr_0710kl",
            "pack_hold": "diodes_2n7002dw_7_f",
            "pack_supply_or": "onsemi_bav70lt1g",
            "pack_system_diode": "diodes_bat54_7_f",
            "pack_diag_timer": "ti_tpul2g223_bqbr",
            "pack_diag_lockout_res": "yageo_rc0402fr_07620kl",
            "pack_diag_lockout_cap": "tdk_c1608x7r1c105k080ac",
            "pack_diag_switch": "diodes_dmn2056u_7",
            "pack_diag_res0": "bourns_crm2512_fx_20r0elf",
            "pack_diag_res1": "bourns_crm2512_fx_20r0elf",
            "pack_mid_adc_filter": "murata_grm155r71h103ka88d",
            "pack_stack_adc_filter": "murata_grm155r71h103ka88d",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        holder = self.database["devices"]["keystone_1048p"]
        self.assertEqual([86.0, 39.8, 14.86], holder["dimensions_mm"])
        self.assertEqual(
            {"SLOT0_POS", "SLOT0_NEG", "SLOT1_POS", "SLOT1_NEG"},
            set(holder["contacts"]),
        )

        tps = self.database["devices"]["ti_tps25751d_refr"]
        self.assertEqual("23/24/25", tps["contacts"]["VBUS_IN"]["physical"])
        self.assertEqual("20/21/22", tps["contacts"]["PPHV"]["physical"])
        self.assertEqual("8 (fixed I2C target data)", tps["contacts"]["I2Ct_SDA"]["physical"])
        charger = self.database["devices"]["ti_bq25798_rqmr"]
        self.assertEqual("2/3", charger["contacts"]["VBUS"]["physical"])
        self.assertEqual("22/23", charger["contacts"]["BAT"]["physical"])
        timer = self.database["devices"]["ti_tpul2g223_bqbr"]
        self.assertEqual("5", timer["contacts"]["CH2_Q"]["physical"])
        self.assertEqual("16", timer["contacts"]["VCC"]["physical"])
        cell = self.database["devices"]["xtar_18650_4000mah_protected"]
        self.assertEqual("button-top positive end", cell["contacts"]["POS"]["physical"])
        self.assertEqual([69.7, 18.7, 18.7], cell["dimensions_mm"])
        self.assertIn("does not publish a separate ordering code", cell["ordering_identity_note"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(
            ("pd_controller.PPHV", "nvdc_charger.VBUS", "PD_NEGOTIATED_VBUS"),
            routes,
        )
        self.assertIn(
            ("pd_controller.GPIO0", "pd_config_eeprom.WP", "PD_EEPROM_WP"),
            routes,
        )
        self.assertIn(
            ("pd_controller.GPIO1", "nvdc_charger.CE", "CHARGE_EN_N"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.CHG", "pack_power_fet.G1", "PACK_CHG_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.DIS", "pack_power_fet.G2", "PACK_DIS_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_power_fet.S2", "nvdc_charger.BAT", "PROTECTED_PACK_POSITIVE"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.ZVC", "abstract:no-connect", "PACK_ZVC_UNUSED"),
            routes,
        )
        self.assertIn(
            ("pack_diag_timer.CH1_Q", "pack_diag_switch.G", "PACK_DIAG_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_diag_timer.CH2_Q_N", "pack_diag_timer.CH1_CLR_N", "PACK_DIAG_REFRACTORY_CLEAR_N"),
            routes,
        )
        self.assertIn(
            ("pack_diag_timer.CH1_Q", "pack_diag_timer.CH2_T_N", "PACK_DIAG_PULSE_ACTIVE"),
            routes,
        )
        self.assertIn(
            ("pack_cell0.POS", "pack_holder.SLOT0_POS", "PACK_SLOT0_POSITIVE_RAW"),
            routes,
        )
        self.assertIn(
            ("pack_cell1.NEG", "pack_holder.SLOT1_NEG", "PACK_2S_MIDPOINT"),
            routes,
        )
        self.assertIn(
            ("aon_buck.PG", "safe_supervisor.MR_N", "AON_PG_N"),
            routes,
        )
        self.assertIn(
            ("safe_supervisor.RESET_N", "main_buck.EN", "POR_N"),
            routes,
        )
        self.assertIn(
            ("safe_por_pullup.END_2", "safe_supervisor.RESET_N", "POR_N"),
            routes,
        )
        self.assertNotIn(
            ("abstract:main-rail-enable-after-source-admission", "main_buck.EN", "MAIN_3V3_EN"),
            routes,
        )
        self.assertIn(
            ("abstract:qualified-2s-positive", "pack_diag_res0.END_1", "BATTERY_STACK_POSITIVE"),
            routes,
        )
        self.assertNotIn(
            ("pack_gauge.CHG", "abstract:exact high-side charge FET gate", "PACK_CHG_GATE"),
            routes,
        )
        admission = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "pack_admission"
        }
        self.assertEqual("PACK_CELL0_ADC", admission["PA25"]["net"])
        self.assertEqual("PACK_STACK_ADC", admission["PA26"]["net"])
        self.assertEqual("POWER_COMMAND_OFF_N", admission["PA24"]["net"])
        self.assertEqual("GPIO_IRQ", admission["PA24"]["controller"])
        self.assertEqual(
            {"PA27", "PA30"},
            set(candidate["free_gpio"]["pack_admission"]),
        )
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn(
            "Budget: **13 used + 3 reserved + 2 free = 18 exposed GPIO**.",
            rendered,
        )
        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertIn("pd_controller.I2Ct_SDA", s3["GPIO1"]["peers"])
        self.assertIn("pd_controller.I2Ct_SCL", s3["GPIO2"]["peers"])
        self.assertIn("pd_controller.I2Ct_IRQ", s3["GPIO45"]["peers"])
        self.assertEqual([], candidate["free_gpio"]["s3"])

    def test_exact_mspm0c1106_memory_update_and_recovery_contract_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertNotIn("ti_mspm0c1104_sdgs20r", self.database["devices"])
        device = self.database["devices"]["ti_mspm0c1106_sdgs20r"]
        self.assertEqual("Texas Instruments MSPM0C1106SDGS20R", device["mpn"])
        self.assertEqual(64, device["memory_contract"]["flash_kb"])
        self.assertEqual(8, device["memory_contract"]["sram_kb"])
        self.assertIn("HYBRID_BSL", device["controller_capabilities"])
        self.assertIn("IWDT", device["controller_capabilities"])
        self.assertEqual("16 (PA20 / SWCLK)", device["contacts"]["PA20_SWCLK"]["physical"])
        self.assertEqual("15 (PA19 / SWDIO)", device["contacts"]["PA19_SWDIO"]["physical"])
        self.assertEqual("14", device["contacts"]["PA18"]["physical"])
        self.assertEqual("13", device["contacts"]["PA17"]["physical"])
        self.assertEqual("5 (PA1 / NRST)", device["contacts"]["PA1_NRST"]["physical"])
        self.assertEqual("1", device["contacts"]["PA26"]["physical"])
        self.assertEqual("2", device["contacts"]["PA27"]["physical"])
        self.assertEqual("3", device["contacts"]["PA30"]["physical"])

        routes = {
            (row["from"], row["to"], row["net"])
            for row in candidate["fixed_routes"]
        }
        for route in (
            ("pack_admission.PA17", "abstract:TP_PACK_UART_TX", "PACK_ADMISSION_UART_TX"),
            ("pack_admission.PA18", "abstract:TP_PACK_UART_RX", "PACK_ADMISSION_UART_RX"),
            ("pack_admission.PA19_SWDIO", "abstract:TP_PACK_SWDIO", "PACK_ADMISSION_SWDIO"),
            ("pack_admission.PA20_SWCLK", "abstract:TP_PACK_SWCLK", "PACK_ADMISSION_SWCLK"),
        ):
            self.assertIn(route, routes)

        contract = candidate["mspm0_memory_update_contract"]
        for region in (
            "0x0000-0x3FFF",
            "0x4000-0x97FF",
            "0x9800-0xEFFF",
            "0xF000-0xFFFF",
        ):
            self.assertIn(region, contract["flash_layout"])
        self.assertIn("physical RUN=KILL", contract["update_sequence"])
        self.assertIn("TX evidence quiet", contract["update_sequence"])
        self.assertIn("inactive slot", contract["update_sequence"])
        self.assertIn("automatic rollback", device["memory_contract"]["production_update"])
        self.assertIn("irreversible key/debug lock is not enabled", contract["open_recovery"])
        self.assertIn("+USD 0.748 per complete device", contract["cost"])

        for instance in ("pack_admission", "safety_controller"):
            self.assertEqual(
                "ti_mspm0c1106_sdgs20r",
                candidate["instances"][instance],
            )
            allocation = {
                row["contact"]: row
                for row in candidate["allocations"]
                if row["instance"] == instance
            }
            self.assertEqual("UART1", allocation["PA17"]["controller"])
            self.assertEqual("UART1", allocation["PA18"]["controller"])

        pack = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "pack_admission"
        }
        self.assertEqual("PACK_PFAIL_N", pack["PA16"]["net"])
        self.assertEqual("PACK_CELL0_ADC", pack["PA25"]["net"])
        self.assertEqual("PACK_STACK_ADC", pack["PA26"]["net"])
        safety = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "safety_controller"
        }
        self.assertEqual("POWER_FAULT_N", safety["PA30"]["net"])
        self.assertEqual("UI_ZONE_TEMP_ADC", safety["PA16"]["net"])
        self.assertEqual("POWER_ZONE_TEMP_ADC", safety["PA26"]["net"])
        self.assertEqual("RF_ZONE_TEMP_ADC", safety["PA27"]["net"])

    def test_exact_bq25798_passive_profile_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0075", contract["charger_passive_decision"])
        self.assertIn("2S at 750kHz", contract["charger_passive_profile"])
        self.assertIn("Twelve independent", contract["charger_passive_profile"])
        self.assertIn("44.2k/100k ILIM", contract["charger_passive_profile"])
        self.assertIn("direct non-ignored charger TS", contract["charger_passive_profile"])
        self.assertNotIn("exact product USB-C receptacle", contract["remaining_i3"])
        self.assertNotIn("exact product USB-C receptacle", contract["deferred_i4"])
        charger = self.database["devices"]["ti_bq25798_rqmr"]["configuration_contract"]
        self.assertEqual(60, charger["thermal_regulation_c"])
        self.assertEqual(85, charger["thermal_shutdown_c"])
        self.assertIn("masked readback", charger["temperature_control_register"])
        self.assertIn("TREG=60 C", contract["thermal_fault_policy"])

        expected_instances = {
            "charger_inductor": "sunlord_mwsa0503s_2r2mt",
            "charger_vbus_cap0": "murata_grm31cr71e106ma12l",
            "charger_vbus_cap1": "murata_grm31cr71e106ma12l",
            "charger_vbus_hf_cap": "yageo_cc0402krx7r9bb104",
            "charger_pmid_cap0": "murata_grm31cr71e106ma12l",
            "charger_pmid_cap1": "murata_grm31cr71e106ma12l",
            "charger_pmid_cap2": "murata_grm31cr71e106ma12l",
            "charger_pmid_hf_cap": "yageo_cc0402krx7r9bb104",
            "charger_sys_cap0": "murata_grm31cr71e106ma12l",
            "charger_sys_cap1": "murata_grm31cr71e106ma12l",
            "charger_sys_cap2": "murata_grm31cr71e106ma12l",
            "charger_sys_cap3": "murata_grm31cr71e106ma12l",
            "charger_sys_cap4": "murata_grm31cr71e106ma12l",
            "charger_sys_hf_cap": "yageo_cc0402krx7r9bb104",
            "charger_bat_cap0": "murata_grm31cr71e106ma12l",
            "charger_bat_cap1": "murata_grm31cr71e106ma12l",
            "charger_btst1_cap": "murata_grm155r71e473ka88d",
            "charger_btst2_cap": "murata_grm155r71e473ka88d",
            "charger_regn_cap": "tdk_cga5l1x7r1e475k160ac",
            "charger_sdrv_cap": "kemet_c0402c102k5ractu",
            "charger_prog_res": "uniroyal_0402wgf8201tce",
            "charger_batp_res": "yageo_rc0402fr_07100rl",
            "charger_ts_top": "uniroyal_0402wgf5231tce",
            "charger_ts_bottom": "yageo_rc0402fr_0730k1l",
            "charger_ts_ntc": "tdk_b57332v5103f360",
            "charger_ilim_top": "yageo_rc0402fr_0744k2l",
            "charger_ilim_bottom": "yageo_rc0402fr_07100kl",
            "pd_local_scl_pullup": "uniroyal_0402wgf2201tce",
            "pd_local_sda_pullup": "uniroyal_0402wgf2201tce",
            "charger_int_pullup": "yageo_rc0402fr_0710kl",
            "charger_ce_pullup": "yageo_rc0402fr_0710kl",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("nvdc_charger.SW1", "charger_inductor.END_1", "CHARGER_SW1"),
            ("charger_inductor.END_2", "nvdc_charger.SW2", "CHARGER_SW2"),
            ("nvdc_charger.PROG", "charger_prog_res.END_1", "CHARGER_PROG_2S_750KHZ"),
            ("pack_power_fet.S2", "charger_batp_res.END_1", "PROTECTED_PACK_POSITIVE"),
            ("nvdc_charger.TS", "charger_ts_ntc.END_1", "CHARGER_TS"),
            ("nvdc_charger.ILIM_HIZ", "charger_ilim_bottom.END_1", "CHARGER_ILIM_HIZ"),
            ("pd_controller.LDO_3V3", "pd_local_scl_pullup.END_1", "PD_LOCAL_3V3"),
            ("nvdc_charger.REGN", "charger_ce_pullup.END_1", "CHARGER_REGN"),
            ("nvdc_charger.VBUS", "nvdc_charger.VAC1", "CHARGER_VBUS_SENSE"),
            ("nvdc_charger.VBUS", "nvdc_charger.VAC2", "CHARGER_VBUS_SENSE"),
            ("nvdc_charger.D_PLUS", "abstract:no-connect", "CHARGER_DP_NC"),
            ("nvdc_charger.D_MINUS", "abstract:no-connect", "CHARGER_DM_NC"),
        ):
            self.assertIn(route, routes)

        pd_gpio1 = next(
            row
            for row in candidate["allocations"]
            if row["instance"] == "pd_controller" and row["contact"] == "GPIO1"
        )
        self.assertEqual("od", pd_gpio1["direction"])
        self.assertIn("Hi-Z reset", pd_gpio1["reset_proof"])

    def test_exact_tps25751_eeprom_support_profile_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0076", contract["pd_support_decision"])
        self.assertIn("hardware SafeMode", contract["pd_support_profile"])
        self.assertIn("both VBUS and VBUS_IN", contract["pd_support_profile"])
        self.assertNotIn(
            "TPS25751 and CAT24C512 surrounding passives and configuration straps",
            contract["remaining_i3"],
        )

        expected_instances = {
            "pd_vin_cap": "murata_grm188r60j106me47d",
            "pd_ldo3v3_cap": "murata_grm188r60j106me47d",
            "pd_ldo1v5_cap": "murata_grm188r60j106me47d",
            "pd_pphv_cap0": "murata_grm32er71e226ke15l",
            "pd_pphv_cap1": "murata_grm32er71e226ke15l",
            "pd_pphv_cap2": "murata_grm32er71e226ke15l",
            "pd_pphv_cap3": "murata_grm32er71e226ke15l",
            "pd_vbus_cap": "tdk_cga5l1x7r1e475k160ac",
            "pd_cc1_cap": "murata_grm1555c1h221ja01d",
            "pd_cc2_cap": "murata_grm1555c1h221ja01d",
            "pd_eeprom_bypass": "yageo_cc0402krx7r9bb104",
            "pd_eeprom_wp_pullup": "yageo_rc0402fr_0710kl",
            "pd_local_scl_pullup": "uniroyal_0402wgf2201tce",
            "pd_local_sda_pullup": "uniroyal_0402wgf2201tce",
            "sys_i2c_scl_pullup": "uniroyal_0402wgf2201tce",
            "sys_i2c_sda_pullup": "uniroyal_0402wgf2201tce",
            "sys_int_pullup": "yageo_rc0402fr_0710kl",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])
        self.assertNotIn("charger_scl_pullup", candidate["instances"])
        self.assertNotIn("charger_sda_pullup", candidate["instances"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("product_usb_connector.B9_VBUS", "pd_controller.VBUS", "USB_C_VBUS_RAW"),
            ("product_usb_connector.B9_VBUS", "pd_controller.VBUS_IN", "USB_C_VBUS_RAW"),
            ("pd_controller.LDO_3V3", "pd_controller.ADCIN1", "PD_ADCIN1_SAFE_MODE_HIGH"),
            ("pd_controller.ADCIN2", "abstract:power-ground", "PD_ADCIN2_SAFE_MODE_LOW"),
            ("pd_controller.PP5V", "abstract:power-ground", "POWER_GROUND"),
            ("abstract:AON_SAFE_3V3", "pd_controller.VIN_3V3", "AON_SAFE_3V3"),
            ("pd_controller.LDO_3V3", "pd_config_eeprom.VCC", "PD_LOCAL_3V3"),
            ("pd_config_eeprom.VSS", "abstract:power-ground", "POWER_GROUND"),
            ("pd_eeprom_wp_pullup.END_2", "pd_config_eeprom.WP", "PD_EEPROM_WP"),
            ("pd_local_scl_pullup.END_2", "nvdc_charger.SCL", "PD_LOCAL_I2C_SCL"),
            ("sys_i2c_sda_pullup.END_2", "s3.GPIO1", "SYS_I2C_SDA"),
            ("sys_int_pullup.END_2", "s3.GPIO45", "SYS_INT_N"),
            ("pd_controller.DRAIN_30", "pd_controller.DRAIN_PAD", "PD_DRAIN_COPPER"),
        ):
            self.assertIn(route, routes)

        pd_gpio0 = next(
            row
            for row in candidate["allocations"]
            if row["instance"] == "pd_controller" and row["contact"] == "GPIO0"
        )
        self.assertEqual("od", pd_gpio0["direction"])
        self.assertIn("authorized", pd_gpio0["reset_proof"])
        self.assertTrue(
            self.database["devices"]["onsemi_cat24c512wi_gt3"][
                "externally_programmed_memory"
            ]
        )
        eeprom_service = next(
            item for item in candidate["services"] if item["instance"] == "pd_config_eeprom"
        )
        self.assertIn("ReadyForPatch", eeprom_service["method"])
        self.assertIn("never drives LDO_3V3 externally", eeprom_service["method"])

    def test_exact_protected_product_usb_port_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0083", contract["product_usb_decision"])
        self.assertIn("TPD4S201RUKR", contract["product_usb_profile"])
        self.assertIn("369-471 pF", contract["product_usb_profile"])
        self.assertIn("without consuming a GPIO", contract["product_usb_profile"])
        self.assertIn("22-Ohm series resistors", contract["product_usb_profile"])
        self.assertIn("reserved DNP", contract["product_usb_profile"])

        expected_instances = {
            "product_usb_connector": "jae_dx07s016ja1r1500",
            "product_usb_protector": "ti_tpd4s201_rukr",
            "product_usb_dp_series": "panasonic_erj_2rkf22r0x",
            "product_usb_dm_series": "panasonic_erj_2rkf22r0x",
            "product_usb_vbias_cap": "yageo_cc0603krx7r0bb104",
            "product_usb_vpwr_cap": "tdk_c1608x7r1c105k080ac",
            "product_usb_fault_pullup": "yageo_rc0402fr_0710kl",
            "pd_cc1_cap": "murata_grm1555c1h221ja01d",
            "pd_cc2_cap": "murata_grm1555c1h221ja01d",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("product_usb_connector.A5_CC1", "product_usb_protector.C_CC1", "USB_C_CC1_CONNECTOR"),
            ("product_usb_connector.B5_CC2", "product_usb_protector.C_CC2", "USB_C_CC2_CONNECTOR"),
            ("product_usb_protector.CC1", "pd_controller.CC1", "USB_C_CC1_PROTECTED"),
            ("product_usb_protector.CC2", "pd_controller.CC2", "USB_C_CC2_PROTECTED"),
            ("product_usb_protector.SBU1", "product_usb_dp_series.END_1", "S3_USB_DP"),
            ("product_usb_dp_series.END_2", "s3.GPIO20", "S3_USB_DP_LOCAL"),
            ("product_usb_protector.SBU2", "product_usb_dm_series.END_1", "S3_USB_DM"),
            ("product_usb_dm_series.END_2", "s3.GPIO19", "S3_USB_DM_LOCAL"),
            ("product_usb_protector.RPD_G1", "product_usb_protector.C_CC1", "USB_C_CC1_CONNECTOR"),
            ("product_usb_protector.RPD_G2", "product_usb_protector.C_CC2", "USB_C_CC2_CONNECTOR"),
            ("product_usb_protector.VBIAS", "product_usb_vbias_cap.END_1", "USB_PROTECTOR_VBIAS"),
            ("pd_controller.LDO_3V3", "product_usb_protector.VPWR", "PD_LOCAL_3V3"),
            ("product_usb_protector.FLT", "abstract:TP_USB_PROTECTOR_FAULT_N", "USB_PROTECTOR_FAULT_N"),
            ("product_usb_connector.A8_SBU1", "abstract:no-connect", "NO_CONNECT"),
            ("product_usb_connector.B8_SBU2", "abstract:no-connect", "NO_CONNECT"),
        ):
            self.assertIn(route, routes)

        self.assertFalse(
            any(
                route["from"].startswith("abstract:product-usb-c")
                or route["to"].startswith("abstract:product-usb-c")
                for route in candidate["fixed_routes"]
            )
        )
        self.assertIn(
            "USB Full-Speed RC tuning, signal-integrity, ESD and short-to-VBUS HIL",
            contract["deferred_i4"],
        )

    def test_exact_fixed_downstream_rail_tree_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0068", contract["rail_decision"])
        self.assertIn("independent fixed", contract["rail_tree"])
        self.assertIn("TPS629203DRLR", contract["aon_rail"])
        self.assertIn("three independent TPS564252DRLR", contract["application_rails"])
        self.assertEqual("DEC-0072", contract["converter_passive_decision"])
        self.assertIn("TNPW040243K7BEED/TNPW040210K0BEED", contract["converter_passive_profile"])
        self.assertIn("68k/12k", contract["converter_passive_profile"])
        self.assertIn("220k/30k", contract["converter_passive_profile"])
        self.assertEqual("DEC-0073", contract["converter_control_passive_decision"])
        self.assertIn("Ten physical resistor positions", contract["converter_control_passive_profile"])
        self.assertIn("directly to admitted SYS", contract["converter_control_passive_profile"])
        self.assertEqual("DEC-0069", contract["external_protection_decision"])
        self.assertIn("TPS259470LRPWR", contract["external_protection"])
        self.assertIn("latch-off", contract["external_protection"])
        self.assertNotIn("TPS259470ARPWR", contract["external_protection"])

        expected_instances = {
            "aon_buck": "ti_tps629203_drlr",
            "aon_inductor": "sunlord_wpn201612h2r2mt",
            "aon_mode_res": "yageo_rc0402fr_0742k2l",
            "aon_input_cap": "tdk_cga5l1x7r1e475k160ac",
            "aon_output_cap": "murata_grm31cr71a226ke15l",
            "aon_efuse": "ti_tps25961_drvr",
            "aon_efuse_rilim": "yageo_rc0402fr_07240kl",
            "aon_efuse_ovlo_top": "yageo_rc0402fr_07196kl",
            "aon_efuse_ovlo_bottom": "yageo_rc0402fr_07100kl",
            "aon_efuse_input_cap": "yageo_cc0402krx7r9bb104",
            "aon_efuse_output_cap": "murata_grm188r60j106me47d",
            "aon_pg_pullup": "yageo_rc0402fr_0747kl",
            "main_buck": "ti_tps564252_drlr",
            "main_inductor": "sunlord_mwsa0503s_3r3mt",
            "main_input_cap": "murata_grm32er71e226ke15l",
            "main_hf_input_cap": "yageo_cc0402krx7r9bb104",
            "main_fb_top": "vishay_tnpw040243k7beed",
            "main_fb_bottom": "vishay_tnpw040210k0beed",
            "main_ff_cap": "kemet_c0402c330j5gactu",
            "main_output_cap0": "murata_grm32er71e226ke15l",
            "main_output_cap1": "murata_grm32er71e226ke15l",
            "main_efuse": "ti_tps25974l_rpwr",
            "main_efuse_rilm": "uniroyal_0402wgf1651tce",
            "main_efuse_dvdt_cap": "murata_grm155r71h472ka01d",
            "main_efuse_itimer_cap": "murata_grm1555c1h121ja01d",
            "main_efuse_ovlo_top": "yageo_rt0402brd07191kl",
            "main_efuse_ovlo_bottom": "yageo_rt0402brd07100kl",
            "main_efuse_pg_top": "yageo_rc0402fr_0745k3l",
            "main_efuse_pg_bottom": "yageo_rc0402fr_0730kl",
            "main_efuse_output_cap": "murata_grm188r60j106me47d",
            "main_en_pulldown": "yageo_rc0402fr_07100kl",
            "power_fault_pullup": "yageo_rc0402fr_0710kl",
            "voice_buck": "ti_tps564252_drlr",
            "voice_inductor": "sunlord_mwsa0503s_3r3mt",
            "voice_input_cap": "murata_grm32er71e226ke15l",
            "voice_hf_input_cap": "yageo_cc0402krx7r9bb104",
            "voice_fb_top": "yageo_rc0402fr_0768kl",
            "voice_fb_bottom": "yageo_rc0402fr_0712kl",
            "voice_ff_cap": "kemet_c0402c330j5gactu",
            "voice_output_cap0": "murata_grm32er71e226ke15l",
            "voice_output_cap1": "murata_grm32er71e226ke15l",
            "voice_efuse": "ti_tps25974l_rpwr",
            "voice_efuse_rilm": "yageo_rc0402fr_073k32l",
            "voice_efuse_dvdt_cap": "murata_grm155r71h472ka01d",
            "voice_efuse_itimer_cap": "murata_grm1555c1h121ja01d",
            "voice_efuse_ovlo_top": "uniroyal_0402wgf2703tce",
            "voice_efuse_ovlo_bottom": "yageo_rc0402fr_07100kl",
            "voice_efuse_pg_top": "yageo_rc0402fr_0768kl",
            "voice_efuse_pg_bottom": "yageo_rc0402fr_0733kl",
            "voice_efuse_output_cap": "murata_grm188r60j106me47d",
            "voice_en_pulldown": "yageo_rc0402fr_0710kl",
            "voice_pg_pullup": "yageo_rc0402fr_0710kl",
            "voice_pg_base_res": "yageo_rc0402fr_0768kl",
            "voice_pg_qualifier": "diodes_mmbt3904_7_f",
            "ext_buck": "ti_tps564252_drlr",
            "ext_inductor": "sunlord_mwsa0503s_4r7mt",
            "ext_buck_input_cap": "murata_grm32er71e226ke15l",
            "ext_buck_hf_input_cap": "yageo_cc0402krx7r9bb104",
            "ext_buck_fb_top": "yageo_rc0402fr_07220kl",
            "ext_buck_fb_bottom": "yageo_rc0402fr_0730kl",
            "ext_buck_ff_cap": "kemet_c0402c330j5gactu",
            "ext_buck_output_cap0": "murata_grm32er71e226ke15l",
            "ext_buck_output_cap1": "murata_grm32er71e226ke15l",
            "ext_en_pulldown": "yageo_rc0402fr_0710kl",
            "ext_pg_pullup": "yageo_rc0402fr_0710kl",
            "ext_pg_base_res": "yageo_rc0402fr_0768kl",
            "ext_pg_qualifier": "diodes_mmbt3904_7_f",
            "ext_efuse": "ti_tps259470l_rpwr",
            "ext_rilm": "yageo_rc0402fr_071k82l",
            "ext_dvdt_cap": "murata_grm155r71h472ka01d",
            "ext_itimer_cap": "murata_grm188r71e224ka88d",
            "ext_ovlo_top": "yageo_rc0402fr_07169kl",
            "ext_ovlo_bottom": "yageo_rc0402fr_0747kl",
            "ext_input_cap": "murata_grm21br71e225ke11l",
            "ext_output_cap": "murata_grm21br71e225ke11l",
            "ext_bleeder": "yageo_rc0603fr_071kl",
            "nrf_power_switch": "ti_tps22919_dckr",
            "cc_power_switch": "ti_tps22919_dckr",
            "sd_power_switch": "ti_tps22919_dckr",
            "codec_power_switch": "ti_tps22919_dckr",
            "receiver_power_switch": "ti_tps22919_dckr",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        buck = self.database["devices"]["ti_tps564252_drlr"]
        self.assertEqual("4", buck["contacts"]["PG"]["physical"])
        self.assertNotIn("BST", buck["contacts"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for destination in ("aon_buck.VIN", "main_buck.VIN", "voice_buck.VIN", "ext_buck.VIN"):
            self.assertIn(("nvdc_charger.SYS", destination, "NVDC_SYS"), routes)
        self.assertIn(("voice_efuse.OUT", "voice.VCC", "VVOICE_4V"), routes)
        self.assertIn(("aon_efuse.OUT", "abstract:AON_SAFE_3V3", "AON_SAFE_3V3"), routes)
        self.assertIn(("main_efuse.OUT", "abstract:3V3_MAIN", "3V3_MAIN"), routes)
        self.assertIn(
            ("ext_efuse.OUT", "u214_connector.PIN_7", "5V_U214_PROTECTED"),
            routes,
        )
        self.assertIn(
            ("u214_connector.PIN_7", "u214.5V_IN", "5V_U214_PROTECTED"),
            routes,
        )
        self.assertIn(("ext_efuse.ILM", "ext_rilm.END_1", "EXT_EFUSE_ILM_SET"), routes)
        self.assertIn(("ext_efuse.DVDT", "ext_dvdt_cap.END_1", "EXT_EFUSE_DVDT"), routes)
        self.assertIn(("ext_efuse.ITIMER", "ext_itimer_cap.END_1", "EXT_EFUSE_ITIMER"), routes)
        self.assertIn(("ext_efuse.OUT", "ext_bleeder.END_1", "5V_U214_PROTECTED"), routes)
        self.assertIn(("aon_buck.MODE_SCONF", "aon_mode_res.END_1", "AON_MODE_SET"), routes)
        self.assertIn(("nvdc_charger.SYS", "aon_buck.EN", "NVDC_SYS"), routes)
        self.assertIn(("aon_pg_pullup.END_2", "aon_buck.PG", "AON_PG_N"), routes)
        self.assertIn(("main_fb_top.END_2", "main_buck.FB", "MAIN_3V3_FB"), routes)
        self.assertIn(("voice_fb_top.END_2", "voice_buck.FB", "VOICE_4V_FB"), routes)
        self.assertIn(("ext_buck_fb_top.END_2", "ext_buck.FB", "EXT_5V_FB"), routes)
        for output_cap in (
            "main_output_cap0",
            "main_output_cap1",
            "voice_output_cap0",
            "voice_output_cap1",
            "ext_buck_output_cap0",
            "ext_buck_output_cap1",
        ):
            self.assertTrue(any(output_cap in endpoint for route in routes for endpoint in route[:2]))
        self.assertIn("immediately at startup", contract["external_protection"])
        self.assertIn("post-start 2A transient", contract["external_protection"])
        self.assertNotIn(
            "ext-5v-passive-discharge",
            {
                endpoint
                for route in candidate["fixed_routes"]
                for endpoint in (route["from"], route["to"])
            },
        )
        self.assertIn(("nrf_power_switch.VOUT", "nrf2.VCC", "3V3_NRF_GROUP"), routes)

        self.assertEqual("DEC-0070", contract["switched_pg_qualification_decision"])
        self.assertIn("EN high plus PG low", contract["switched_pg_qualification"])
        self.assertIn(
            ("voice_efuse.PG", "voice_pg_qualifier.E", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertIn(
            ("voice_pg_base_res.END_2", "voice_pg_qualifier.B", "VOICE_PG_QUAL_BASE"),
            routes,
        )
        self.assertIn(
            ("voice_pg_pullup.END_2", "voice_efuse.PG", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertIn(
            ("voice_pg_qualifier.C", "abstract:power-current-thermal-fault", "POWER_FAULT_N"),
            routes,
        )
        self.assertIn(
            ("ext_buck.PG", "ext_pg_qualifier.E", "EXT_5V_PG_N"),
            routes,
        )
        self.assertIn(
            ("ext_pg_base_res.END_2", "ext_pg_qualifier.B", "EXT_PG_QUAL_BASE"),
            routes,
        )
        self.assertIn(
            ("ext_pg_pullup.END_2", "ext_buck.PG", "EXT_5V_PG_N"),
            routes,
        )
        self.assertIn(
            ("ext_pg_qualifier.C", "abstract:power-current-thermal-fault", "POWER_FAULT_N"),
            routes,
        )
        self.assertNotIn(
            ("voice_buck.PG", "abstract:power-current-thermal-fault", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertNotIn(
            ("ext_buck.PG", "abstract:power-current-thermal-fault", "EXT_5V_PG_N"),
            routes,
        )

    def test_i7_external_expansion_power_and_signal_boundary_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["external_expansion_contract"]
        self.assertEqual("DEC-0098", contract["decision"])
        self.assertIn("paper_reviewed", contract["status"])
        self.assertIn("TPS259470LRPWR", contract["branch_power"])
        self.assertIn("TXS0102DCUR", contract["unit_signals"])
        self.assertIn("TCA4307DGKR", contract["u214_signals"])
        self.assertIn("presence or identity contact", contract["identity_and_hot_plug"])
        self.assertIn("Samtec HLE-107-02-G-DV-PE-LC", contract["connector_truth"])
        self.assertIn("pass-through entry", contract["connector_truth"])
        self.assertIn("vertical", contract["connector_truth"])
        self.assertIn("Y=17..41 mm", contract["connector_truth"])
        self.assertIn("4.5 mm per side", contract["connector_truth"])
        self.assertIn("Current-lot post section", contract["connector_truth"])
        self.assertIn("concrete device", contract["high_throughput_boundary"])

        expected = {
            "ext_request_or": "nexperia_74lvc1g32gv_125",
            "ext_branch_gate": "ti_sn74lvc2g08_dcur",
            "u214_supervisor": "ti_tps3808g33_dbvr",
            "unit_supervisor": "ti_tps3808g33_dbvr",
            "unit_efuse": "ti_tps259470l_rpwr",
            "u214_i2c_iso": "tca4307dgkr",
            "u214_host_buffer_a": "nexperia_74lvc126apw_118",
            "u214_host_buffer_b": "nexperia_74lvc126apw_118",
            "u214_return_buffer": "nexperia_74lvc126apw_118",
            "unit_signal_iso": "ti_txs0102_dcur",
            "u214_esd_a": "ti_tpd4e05u06_dqar",
            "u214_esd_b": "ti_tpd4e05u06_dqar",
            "u214_esd_c": "ti_tpd4e05u06_dqar",
            "unit_esd": "ti_tpd4e05u06_dqar",
            "unit_connector": "seeed_1125r_smt_4p",
            "u214_connector": "samtec_hle_107_02_g_dv_pe_lc",
        }
        for instance, device_id in expected.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        connector = self.database["devices"]["samtec_hle_107_02_g_dv_pe_lc"]
        self.assertEqual("Samtec HLE-107-02-G-DV-PE-LC", connector["mpn"])
        self.assertEqual([17.78, 5.08, 7.62], connector["dimensions_mm"])
        self.assertEqual([17.78, 3.81], connector["mechanical_contract"]["opposite_face_pth_keepout_mm"])
        for pin in range(1, 15):
            self.assertEqual(
                2,
                sum(
                    endpoint == f"u214_connector.PIN_{pin}"
                    for route in candidate["fixed_routes"]
                    for endpoint in (route["from"], route["to"])
                ),
            )

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(("slow_io.P05", "ext_request_or.1B", "UNIT_5V_REQ"), routes)
        self.assertIn(("slow_io.P17", "ext_request_or.1A", "U214_5V_REQ"), routes)
        self.assertIn(("ext_branch_gate.1Y", "ext_efuse.EN_UVLO", "U214_5V_EN_SAFE"), routes)
        self.assertIn(("ext_branch_gate.2Y", "unit_efuse.EN_UVLO", "UNIT_5V_EN_SAFE"), routes)
        self.assertIn(("unit_efuse.OUT", "unit_connector.5V", "5V_UNIT_PROTECTED"), routes)
        self.assertIn(("unit_esd.D1_PLUS", "unit_connector.SIG0", "UNIT_CONNECTOR_SIG0"), routes)
        self.assertIn(("unit_esd.D1_MINUS", "unit_connector.SIG1", "UNIT_CONNECTOR_SIG1"), routes)
        self.assertIn(("unit_connector.GND", "abstract:power-ground", "POWER_GROUND"), routes)
        self.assertIn(("unit_supervisor.RESET_N", "slow_io.P26", "UNIT_READY"), routes)
        self.assertNotIn(
            "abstract:accessory-present",
            {endpoint for route in candidate["fixed_routes"] for endpoint in (route["from"], route["to"])},
        )
        quiet = {item["id"] for item in candidate["quiet_state_policy"]["contracts"]}
        self.assertIn("U214_CAP_QUIET", quiet)
        self.assertIn("UNIT_PORT_QUIET", quiet)
        self.assertNotIn("U214_EXT_QUIET", quiet)
        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])

    def test_run_kill_watchdog_and_tx_evidence_contract_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["safety_contract"]

        self.assertEqual("product RUN/KILL and unattended watchdog architecture", contract["decision"])
        self.assertEqual(
            "paper_reviewed_exact_watchdog_controller_thermal_and_fault_ui_paths",
            contract["status"],
        )
        self.assertEqual(
            ["c5.EN", "rp.RUN", "s3.EN through a separate bounded fault-reset request"],
            contract["reset_fanout"]["targets"],
        )
        self.assertIn("KILL-to-RUN", contract["latch_logic"]["rearm"])
        self.assertIn("automatic restart is forbidden", contract["latch_logic"]["rearm"])
        self.assertIn("0x2B", contract["watchdog"]["controller"])
        self.assertIn("TPS3435CAKAGDDFR", contract["watchdog"]["independent_timer"])
        self.assertIn("plain-language primary cause", contract["fault_ui"]["required_screen"])
        self.assertIn("three additional exact TDK", contract["thermal_supervision"]["sensors"])
        self.assertEqual(9, len(contract["tx_gate_map"]))
        self.assertEqual(
            [
                "S3_RF",
                "C5_RF",
                "NRF0_RF",
                "NRF1_RF",
                "NRF2_RF",
                "CC_RF",
                "VOICE_RF",
                "IR_OPTICAL",
                "LORA_EXT_RF",
            ],
            contract["evidence"]["channels"],
        )
        self.assertIn("0x20", contract["evidence"]["source_mask"])
        self.assertEqual(
            "0x20",
            self.database["devices"]["ti_tca9535_pwr"]
            ["i2c_7bit_address_by_a2a1a0"]["000"],
        )
        self.assertIn("ANY_TX_AON_N", contract["evidence"]["aggregate"])
        self.assertIn("each EV_N[0..8]", contract["evidence"]["per_path_indicators"])
        self.assertIn("receive-only", contract["evidence"]["per_path_indicators"])
        self.assertIn("5-V stock level", contract["evidence"]["external_cap_input"])
        self.assertEqual("DEC-0101", contract["evidence"]["electrical_decision"])

        required_instances = {
            "safe_supervisor": "ti_tps3808g33_dbvr",
            "safety_controller": "ti_mspm0c1106_sdgs20r",
            "safety_watchdog": "ti_tps3435cakagddfr",
            "safe_conditioner": "nexperia_74lvc2g14gv_125",
            "safe_rearm_buffer": "ti_sn74lvc1g17_dckr",
            "safe_latch": "ti_sn74lvc1g74_dcur",
            "safe_reset_buffer": "ti_sn74lvc1g06_dckr",
            "safe_c5_reset_buffer": "ti_sn74lvc1g06_dckr",
            "safe_c5_fault_reset_buffer": "ti_sn74lvc1g07_dckr",
            "safe_fault_reset_buffer": "ti_sn74lvc3g07_dcur",
            "safe_reset_sink_a": "diodes_2n7002dw_7_f",
            "safe_reset_sink_b": "diodes_2n7002dw_7_f",
            "safe_gate_a": "ti_sn74lvc08a_pwr",
            "safe_gate_b": "ti_sn74lvc08a_pwr",
            "ir_safe_gate": "ti_sn74lvc1g08_dckr",
            "nrf_backup_gate": "ti_sn74lvc1g08_dckr",
            "cc_backup_gate": "ti_sn74lvc1g08_dckr",
            "safe_ptt_or": "nexperia_74lvc1g32gv_125",
            "det_s3": "adi_ltc5532_es6_trmpbf",
            "det_c5": "adi_ltc5532_es6_trmpbf",
            "det_nrf0": "adi_ad8314acpz_rl7",
            "det_nrf1": "adi_ad8314acpz_rl7",
            "det_nrf2": "adi_ad8314acpz_rl7",
            "nrf0_rf_jumper": "te_2118651_2",
            "nrf1_rf_jumper": "te_2118651_2",
            "nrf2_rf_jumper": "te_2118651_2",
            "nrf0_rf_board_connector": "hirose_ufl_r_smt_1_10",
            "nrf1_rf_board_connector": "hirose_ufl_r_smt_1_10",
            "nrf2_rf_board_connector": "hirose_ufl_r_smt_1_10",
            "det_cc": "adi_ad8314acpz_rl7",
            "det_voice": "adi_ad8314acpz_rl7",
            "det_ir": "vishay_vemd1060x01",
            "evidence_cmp_a": "ti_tlv1824_pwr",
            "evidence_cmp_b": "ti_tlv1824_pwr",
            "evidence_cmp_voice": "ti_tlv1821_dckr",
            "ext_evidence_buffer": "ti_sn74lvc1g07_dckr",
            "evidence_mask": "ti_tca9535_pwr",
            "evidence_main_isolator": "ti_sn74lvc3g07_dcur",
            "fault_assert_backup_pulldown": "yageo_rc0402fr_071ml",
            "fault_assert_sense_series": "yageo_rc0402fr_07100kl",
            "power_zone_ntc": "tdk_b57332v5103f360",
            "rf_zone_ntc": "tdk_b57332v5103f360",
            "ui_zone_ntc": "tdk_b57332v5103f360",
        }
        for instance, device_id in required_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        mask = self.database["devices"]["ti_tca9535_pwr"]
        self.assertEqual("13", mask["contacts"]["P10"]["physical"])
        self.assertEqual("24", mask["contacts"]["VCC"]["physical"])
        self.assertEqual(5.0, mask["electrical_contract"]["io_input_tolerance_v_max"])
        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("u214_connector.PIN_5", "u214_esd_c.D2_MINUS", "U214_PIN5_PROFILE"),
            ("ext_evidence_input_series.END_2", "ext_evidence_buffer.A", "U214_PIN5_SENSE"),
            ("ext_evidence_buffer.Y", "evidence_mask.P10", "EV_N8_LORA_EXT"),
            ("ext_evidence_buffer.Y", "evidence_or_4.K1", "EV_N8_LORA_EXT"),
            ("ext_tx_led.K", "ext_evidence_buffer.Y", "EV_N8_LORA_EXT"),
            ("evidence_or_4.A_COMMON", "safety_controller.PA22", "ANY_TX_AON_N"),
        ):
            self.assertIn(route, routes)
        self.assertNotIn("evidence_mask_p11_pulldown", candidate["instances"])
        self.assertIn(
            ("fault_assert_pullup.END_2", "fault_assert_sense_series.END_1", "FAULT_ASSERT_N"),
            routes,
        )
        self.assertIn(
            ("fault_assert_sense_series.END_2", "evidence_mask.P11", "FAULT_ASSERT_SENSE"),
            routes,
        )
        self.assertIn(
            ("power_command_pullup.END_2", "safe_fault_reset_buffer.3A", "POWER_COMMAND_OFF_N"),
            routes,
        )
        self.assertIn(
            ("safe_fault_reset_buffer.3Y", "fault_assert_pullup.END_2", "FAULT_ASSERT_N"),
            routes,
        )
        self.assertIn(
            ("safe_c5_fault_reset_buffer.Y", "c5.EN", "C5_RESET_N"),
            routes,
        )
        self.assertIn(
            ("safe_fault_reset_buffer.1Y", "rp.RUN", "RP_RESET_N"),
            routes,
        )
        for port in range(12, 18):
            self.assertEqual(
                "yageo_rc0402fr_0710kl",
                candidate["instances"][f"evidence_mask_p{port}_pulldown"],
            )
            self.assertIn(
                (f"evidence_mask.P{port}", f"evidence_mask_p{port}_pulldown.END_1", f"EVIDENCE_MASK_UNUSED_P{port}"),
                routes,
            )

        rp = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "rp"
        }
        self.assertEqual("RP_ANY_TX_N", rp["GPIO22"]["net"])
        self.assertEqual("i", rp["GPIO22"]["direction"])
        self.assertNotIn("evidence_mask.SDA", rp["GPIO28"]["peers"])
        self.assertNotIn("evidence_mask.SCL", rp["GPIO29"]["peers"])
        safety = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "safety_controller"
        }
        self.assertIn("evidence_mask.SDA", safety["PA4"]["peers"])
        self.assertIn("evidence_mask.SCL", safety["PA2"]["peers"])
        self.assertEqual("SAFETY_WATCHDOG_WDI", safety["PA6"]["net"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "TPS3808G33DBVR<br/>AON rail supervisor and power-on reset",
            "MSPM0C1106SDGS20R<br/>independent MSPM0 watchdog, thermal and TX-lease controller",
            "TPS3435CAKAGDDFR<br/>independent 1.6-s timeout watchdog",
            "SN74LVC1G17DCKR<br/>SN74LVC1G17 physical re-arm Schmitt buffer",
            "SN74LVC1G74DCUR<br/>asynchronous RUN_PERMIT / FAULT_KILL latch",
            "LTC5532ES6#TRMPBF<br/>S3 2.4-GHz RF power detector",
            "SN74LVC1G07DCKR<br/>5-V-tolerant non-inverting open-drain LoRa Cap evidence boundary",
            "TCA9535PWR<br/>AON 16-bit evidence source mask on the private safety I2C bus",
            "SN74LVC3G07DCUR<br/>triple AON-to-main open-drain evidence isolator",
        ):
            self.assertIn(label, rendered)

    def test_exact_actual_tx_thresholds_and_domain_isolation_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        instances = candidate["instances"]
        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }

        channels = {
            "s3": ("evidence_cmp_a", "IN1_P", "OUT1", "EV_THRESH_0_S3", "EV_N0_S3", "yageo_rc0402fr_0710kl"),
            "c5": ("evidence_cmp_a", "IN2_P", "OUT2", "EV_THRESH_1_C5", "EV_N1_C5", "yageo_rc0402fr_0710kl"),
            "nrf0": ("evidence_cmp_b", "IN1_P", "OUT1", "EV_THRESH_2_NRF0", "EV_N2_NRF0", "yageo_rc0402fr_0710kl"),
            "nrf1": ("evidence_cmp_b", "IN2_P", "OUT2", "EV_THRESH_3_NRF1", "EV_N3_NRF1", "yageo_rc0402fr_0710kl"),
            "nrf2": ("evidence_cmp_b", "IN3_P", "OUT3", "EV_THRESH_4_NRF2", "EV_N4_NRF2", "yageo_rc0402fr_0710kl"),
            "cc": ("evidence_cmp_b", "IN4_P", "OUT4", "EV_THRESH_5_CC", "EV_N5_CC", "yageo_rc0402fr_0710kl"),
            "voice": ("evidence_cmp_voice", "IN_P", "OUT", "EV_THRESH_6_VOICE", "EV_N6_VOICE", "yageo_rc0402fr_0710kl"),
            "ir": ("evidence_cmp_a", "IN3_P", "OUT3", "EV_THRESH_7_IR", "EV_N7_IR", "yageo_rc0402fr_0712kl"),
        }
        for channel, (comparator, input_p, output, threshold_net, output_net, bottom_device) in channels.items():
            self.assertEqual("yageo_rc0402fr_07100kl", instances[f"{channel}_evidence_threshold_top"])
            self.assertEqual(bottom_device, instances[f"{channel}_evidence_threshold_bottom"])
            self.assertEqual("yageo_rc0402fr_071ml", instances[f"{channel}_evidence_hysteresis"])
            self.assertEqual("yageo_rc0402fr_0710kl", instances[f"{channel}_evidence_output_pullup"])
            self.assertIn(
                (f"{channel}_evidence_threshold_top.END_2", f"{comparator}.{input_p}", threshold_net),
                routes,
            )
            self.assertIn(
                (f"{comparator}.{output}", f"{channel}_evidence_hysteresis.END_1", output_net),
                routes,
            )
            self.assertIn(
                (f"{channel}_evidence_output_pullup.END_2", f"{comparator}.{output}", output_net),
                routes,
            )
            self.assertEqual("liteon_ltst_c190krkt", instances[f"{channel}_tx_led"])
            self.assertEqual("uniroyal_0402wgf2201tce", instances[f"{channel}_tx_led_series"])
            self.assertIn(
                (f"{channel}_tx_led.K", f"{comparator}.{output}", output_net),
                routes,
            )

        def trip_values(bottom_ohm):
            top_ohm = 100_000.0
            feedback_ohm = 1_000_000.0
            pullup_ohm = 10_000.0
            open_top = 1.0 / (1.0 / top_ohm + 1.0 / (feedback_ohm + pullup_ohm))
            assert_threshold = 3.3 * bottom_ohm / (bottom_ohm + open_top)
            low_bottom = 1.0 / (1.0 / bottom_ohm + 1.0 / feedback_ohm)
            clear_threshold = 3.3 * low_bottom / (top_ohm + low_bottom)
            return assert_threshold, clear_threshold

        rf_assert, rf_clear = trip_values(10_000.0)
        ir_assert, ir_clear = trip_values(12_000.0)
        self.assertAlmostEqual(0.327, rf_assert, places=3)
        self.assertAlmostEqual(0.297, rf_clear, places=3)
        self.assertAlmostEqual(0.384, ir_assert, places=3)
        self.assertAlmostEqual(0.350, ir_clear, places=3)

        for instance in ("evidence_cmp_a_bypass", "evidence_cmp_b_bypass", "evidence_cmp_voice_bypass", "evidence_mask_bypass", "evidence_main_isolator_bypass"):
            self.assertEqual("yageo_cc0402krx7r9bb104", instances[instance])
        self.assertEqual("ti_sn74lvc3g07_dcur", instances["evidence_main_isolator"])
        isolator = self.database["devices"]["ti_sn74lvc3g07_dcur"]
        self.assertEqual("1", isolator["contacts"]["1A"]["physical"])
        self.assertEqual("7", isolator["contacts"]["1Y"]["physical"])
        self.assertIn("Ioff", isolator["electrical_contract"]["partial_power_down"])

        for route in (
            ("evidence_cmp_a.OUT2", "evidence_main_isolator.1A", "EV_N1_C5"),
            ("evidence_main_isolator.1Y", "c5.GPIO23", "C5_RF_TX_EVIDENCE_N"),
            ("evidence_cmp_a.OUT3", "evidence_main_isolator.2A", "EV_N7_IR"),
            ("evidence_main_isolator.2Y", "c5.GPIO24", "IR_TX_EVIDENCE_N"),
            ("evidence_or_4.A_COMMON", "evidence_main_isolator.3A", "ANY_TX_AON_N"),
            ("evidence_main_isolator.3Y", "rp.GPIO22", "RP_ANY_TX_N"),
            ("safety_controller.PA4", "evidence_mask.SDA", "SAFETY_EVIDENCE_I2C_SDA"),
            ("safety_controller.PA2", "evidence_mask.SCL", "SAFETY_EVIDENCE_I2C_SCL"),
        ):
            self.assertIn(route, routes)
        self.assertFalse(
            any(
                route["from"] in {"evidence_cmp_a.OUT2", "evidence_cmp_a.OUT3"}
                and route["to"] in {"c5.GPIO23", "c5.GPIO24"}
                for route in candidate["fixed_routes"]
            )
        )
        self.assertNotIn(
            "actual_tx_threshold_networks",
            {row["id"] for row in candidate["bom_audit"]["required_uninstantiated_parts"]},
        )

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "Yageo RC0402FR-07100KL<br/>s3 first-population 100-kOhm threshold upper resistor",
            "Yageo RC0402FR-0712KL<br/>ir first-population 12-kOhm threshold lower resistor",
            "SN74LVC3G07DCUR<br/>triple AON-to-main open-drain evidence isolator",
            "Yageo RC0402FR-0710KL<br/>10-kOhm main-domain RP ANY-TX pull-up resistor",
        ):
            self.assertIn(label, rendered)

    def test_i6_three_nrf_exact_electrical_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["nrf_electrical_contract"]
        self.assertEqual("DEC-0091", contract["decision"])
        self.assertIn("paper_reviewed_i6_nrf_subblock", contract["status"])
        self.assertIn("100-ms", contract["startup_shutdown"])
        self.assertIn("channels 0, 100 and 125", " ".join(contract["remaining_hil"]))
        self.assertIn(">=30mA transient", candidate["power_contract"]["aon_rail"])

        required = {
            "nrf0_host_buffer": "nexperia_74lvc126apw_118",
            "nrf0_return_buffer": "nexperia_74lvc2g126dp_125",
            "nrf1_host_buffer": "nexperia_74lvc126apw_118",
            "nrf1_return_buffer": "nexperia_74lvc2g126dp_125",
            "nrf2_host_buffer": "nexperia_74lvc126apw_118",
            "nrf2_return_buffer": "nexperia_74lvc2g126dp_125",
            "nrf0_coupler": "ttm_dc2337j5010ahf",
            "nrf1_coupler": "ttm_dc2337j5010ahf",
            "nrf2_coupler": "ttm_dc2337j5010ahf",
            "det_nrf0": "adi_ad8314acpz_rl7",
            "det_nrf1": "adi_ad8314acpz_rl7",
            "det_nrf2": "adi_ad8314acpz_rl7",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        coupler = self.database["devices"]["ttm_dc2337j5010ahf"]
        self.assertEqual([2000, 4000], coupler["electrical_contract"]["operating_band_mhz"])
        self.assertEqual(
            [2400, 2525],
            coupler["electrical_contract"]["nrf_channel_0_to_125_coverage_mhz"],
        )
        self.assertEqual("1", coupler["contacts"]["RF_IN"]["physical"])
        self.assertEqual("6", coupler["contacts"]["RF_OUT"]["physical"])
        detector = self.database["devices"]["adi_ad8314acpz_rl7"]
        self.assertEqual([100, 2700], detector["electrical_contract"]["frequency_response_mhz"])
        self.assertEqual(5.7, detector["electrical_contract"]["maximum_active_current_ma"])
        self.assertEqual("6", detector["contacts"]["V_UP"]["physical"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for radio in range(3):
            prefix = f"nrf{radio}"
            self.assertIn(
                (f"{prefix}.ANT", f"{prefix}_rf_jumper.END_A", f"NRF{radio}_MODULE_RF_50R"),
                routes,
            )
            self.assertIn(
                (f"{prefix}_rf_jumper.END_B", f"{prefix}_rf_board_connector.CENTER", f"NRF{radio}_MODULE_RF_50R"),
                routes,
            )
            self.assertIn(
                (f"{prefix}_coupler.COUPLED_FWD", f"det_nrf{radio}.RFIN", f"NRF{radio}_FORWARD_RF_SAMPLE"),
                routes,
            )
            self.assertIn(
                (f"{prefix}_return_buffer.1Y", f"{prefix}_miso_series.END_1", f"NRF{radio}_MISO_BUFFERED"),
                routes,
            )
            self.assertIn(
                (f"{prefix}_host_buffer.4Y", f"{prefix}_mosi_series.END_1", f"NRF{radio}_MOSI_BUFFERED"),
                routes,
            )

        direct_peers = {
            peer
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp"
            for peer in allocation.get("peers", [])
            if peer.startswith(("nrf0.", "nrf1.", "nrf2."))
        }
        self.assertEqual(set(), direct_peers)
        self.assertIn(
            ("nrf_evidence_hold_diode.K", "det_nrf2.ENBL", "NRF_EVIDENCE_HOLD"),
            routes,
        )

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "Nexperia 74LVC126APW,118<br/>CE/CSN/SCK/MOSI switched-rail Ioff buffer",
            "Nexperia 74LVC2G126DP,125<br/>MISO/IRQ switched-rail Ioff buffer",
            "TTM Technologies DC2337J5010AHF<br/>full-band forward-power directional coupler",
            "Analog Devices AD8314ACPZ-RL7<br/>nRF0 2.4-GHz RF power detector",
        ):
            self.assertIn(label, rendered)

    def test_i6_native_s3_c5_exact_rf_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["native_rf_electrical_contract"]
        self.assertEqual("DEC-0092", contract["decision"])
        self.assertIn("paper_reviewed_i6_s3_c5_native_rf_subblock", contract["status"])
        self.assertIn("ANT2", contract["band_coverage"])
        self.assertIn("<=0.4 dB", contract["performance_budget"])

        required = {
            "s3_rf_jumper": "te_2118651_2",
            "s3_rf_board_connector": "hirose_ufl_r_smt_1_10",
            "c5_rf_jumper": "te_2118651_2",
            "c5_rf_board_connector": "hirose_ufl_r_smt_1_10",
            "s3_rf_coupler": "kyocera_avx_cp0603q5425entr",
            "c5_rf_coupler": "kyocera_avx_cp0603q5425entr",
            "s3_detector_input_cap": "murata_grm1555c1h390ja01d",
            "c5_detector_input_cap": "murata_grm1555c1h390ja01d",
            "s3_detector_feedback_res": "yageo_rc0402fr_0710kl",
            "s3_detector_ground_res": "yageo_rc0402fr_0710kl",
            "c5_detector_feedback_res": "yageo_rc0402fr_0710kl",
            "c5_detector_ground_res": "yageo_rc0402fr_0710kl",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        coupler = self.database["devices"]["kyocera_avx_cp0603q5425entr"]
        self.assertEqual([[2400, 2496], [4900, 5950]], coupler["electrical_contract"]["bands_mhz"])
        self.assertEqual(0.2, coupler["electrical_contract"]["mainline_loss_max_db"]["2400_2496"])
        self.assertEqual(0.4, coupler["electrical_contract"]["mainline_loss_max_db"]["4900_5950"])
        self.assertEqual("manufacturer top-view IN land", coupler["contacts"]["RF_IN"]["physical"])
        self.assertEqual("manufacturer top-view 50 OHM land", coupler["contacts"]["TERMINATION_50R"]["physical"])

        connector = self.database["devices"]["hirose_ufl_r_smt_1_10"]
        self.assertEqual(6, connector["electrical_contract"]["frequency_max_ghz"])
        self.assertEqual("1", connector["contacts"]["CENTER"]["physical"])
        jumper = self.database["devices"]["te_2118651_2"]
        self.assertEqual(30.0, jumper["electrical_contract"]["cable_length_mm"])
        self.assertEqual(9, jumper["electrical_contract"]["frequency_max_ghz"])
        self.assertEqual("right-angle UMCC GEN 1 plug A", jumper["contacts"]["END_A"]["physical"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("s3.ANT", "s3_rf_jumper.END_A", "S3_MODULE_RF_50R"),
            ("s3_rf_jumper.END_B", "s3_rf_board_connector.CENTER", "S3_MODULE_RF_50R"),
            ("s3_rf_board_connector.CENTER", "s3_rf_coupler.RF_IN", "S3_MODULE_RF_50R"),
            ("s3_rf_coupler.COUPLED_FWD", "s3_detector_input_cap.END_1", "S3_FORWARD_RF_SAMPLE_RAW"),
            ("s3_detector_input_cap.END_2", "det_s3.RFIN", "S3_FORWARD_RF_SAMPLE"),
            ("c5.ANT1", "c5_rf_jumper.END_A", "C5_MODULE_RF_50R"),
            ("c5_rf_jumper.END_B", "c5_rf_board_connector.CENTER", "C5_MODULE_RF_50R"),
            ("c5.ANT2", "abstract:no-connect", "C5_ANT2_DISABLED_NC"),
            ("c5_rf_board_connector.CENTER", "c5_rf_coupler.RF_IN", "C5_RF_MAINLINE_IN_50R"),
            ("c5_rf_coupler.COUPLED_FWD", "c5_detector_input_cap.END_1", "C5_FORWARD_RF_SAMPLE_RAW"),
            ("c5_detector_input_cap.END_2", "det_c5.RFIN", "C5_FORWARD_RF_SAMPLE"),
        ):
            self.assertIn(route, routes)

        self.assertFalse(any(
            route["from"] in {"abstract:S3-qualified-RF-tap", "abstract:C5-qualified-RF-tap"}
            for route in candidate["fixed_routes"]
        ))
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "TE Connectivity 2118651-2<br/>S3 exact 30-mm UMCC Gen1 module jumper",
            "TE Connectivity 2118651-2<br/>C5 exact 30-mm UMCC Gen1 module jumper",
            "CP0603Q5425ENTR<br/>S3 2.4-GHz forward-power directional coupler",
            "CP0603Q5425ENTR<br/>C5 2.4/5-GHz forward-power directional coupler",
            "U.FL-R-SMT-1(80)<br/>S3 module-jumper board receptacle",
            "U.FL-R-SMT-1(80)<br/>C5 module-jumper board receptacle",
            'S3_RF_COUPLER -->|"-20-dB forward sample"| S3_DETECTOR_INPUT_CAP',
            'C5_RF_COUPLER -->|"-20/-13-dB forward sample"| C5_DETECTOR_INPUT_CAP',
        ):
            self.assertIn(token, rendered)

    def test_i6_cc1101_exact_rf_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["cc_rf_electrical_contract"]
        self.assertEqual("DEC-0093", contract["decision"])
        self.assertIn("paper_reviewed_i6_cc1101_subblock", contract["status"])
        self.assertIn("00 isolation", contract["band_selection"])
        self.assertIn("never authorize TX", contract["evidence"])

        required = {
            "cc_host_buffer": "nexperia_74lvc126apw_118",
            "cc_return_buffer": "nexperia_74lvc126apw_118",
            "cc_band_buffer": "nexperia_74lvc2g126dp_125",
            "cc_crystal": "abracon_abm8_26mhz_10_d_1_g_t",
            "cc_balun": "ttm_b0310j50100ahf",
            "cc_switch_a": "infineon_bgs13sn8e6327xtsa1",
            "cc_switch_b": "infineon_bgs13sn8e6327xtsa1",
            "cc_rf_esd": "littelfuse_sesd0402x1un_0020_090",
            "cc_detector_tap_cap": "murata_gjm1555c1hr47bb01d",
            "det_cc": "adi_ad8314acpz_rl7",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        switch = self.database["devices"]["infineon_bgs13sn8e6327xtsa1"]
        self.assertEqual(
            {"00": "isolation", "10": "RF1", "01": "RF2", "11": "RF3"},
            switch["electrical_contract"]["truth_table"],
        )
        self.assertEqual("3", switch["contacts"]["V1"]["physical"])
        self.assertEqual("2", switch["contacts"]["V2"]["physical"])
        self.assertEqual("6", switch["contacts"]["RFIN"]["physical"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("slow_io.P03", "cc_band_buffer.1A", "CC_BAND_V1_REQ"),
            ("slow_io.P04", "cc_band_buffer.2A", "CC_BAND_V2_REQ"),
            ("cc_band_v1_series.END_2", "cc_switch_a.V1", "CC_BAND_V1"),
            ("cc_band_v1_series.END_2", "cc_switch_b.V1", "CC_BAND_V1"),
            ("cc_switch_a.RF1", "cc_315_l10_in.END_1", "CC_RF_315_IN"),
            ("cc_315_l10_out.END_2", "cc_switch_b.RF1", "CC_RF_315_OUT"),
            ("cc_switch_a.RF2", "cc_433_l15.END_1", "CC_RF_433_IN"),
            ("cc_433_l15.END_2", "cc_switch_b.RF2", "CC_RF_433_OUT"),
            ("cc_switch_a.RF3", "cc_868_915_l10.END_1", "CC_RF_868_915_IN"),
            ("cc_868_915_l10.END_2", "cc_switch_b.RF3", "CC_RF_868_915_OUT"),
            ("cc_detector_tap_cap.END_2", "det_cc.RFIN", "CC_RF_SAMPLE"),
            ("cc_evidence_hold_diode.K", "det_cc.ENBL", "CC_EVIDENCE_HOLD"),
            ("det_cc.V_UP", "evidence_cmp_b.IN4_N", "CC_DETECT_V"),
        ):
            self.assertIn(route, routes)

        direct_cc_peers = {
            peer
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp"
            for peer in allocation.get("peers", [])
            if peer.startswith("cc.")
        }
        self.assertEqual(set(), direct_cc_peers)
        self.assertFalse(any(
            route["from"] == "abstract:CC-qualified-RF-tap"
            for route in candidate["fixed_routes"]
        ))
        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])
        self.assertIn("P05", candidate["contact_accounting"]["slow_io"]["used"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "BGS13SN8E6327XTSA1<br/>transceiver-side three-band SP3T isolator",
            "BGS13SN8E6327XTSA1<br/>antenna-side three-band SP3T isolator",
            "B0310J50100AHF<br/>300-MHz-to-1-GHz 50-to-100-Ohm RF balun",
            "ABM8-26.000MHZ-10-D-1-G-T<br/>CC1101 exact 26-MHz reference crystal",
            "GJM1555C1HR47BB01D<br/>actual-TX high-impedance RF sample capacitor",
            "SESD0402X1UN-0020-090<br/>external CC RF line ultra-low-capacitance ESD diode",
        ):
            self.assertIn(token, rendered)

    def test_i6_dual_sa818s_exact_rf_endpoints_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["voice_rf_electrical_contract"]
        self.assertEqual("DEC-0094", contract["decision"])
        self.assertEqual("paper_reviewed_h2_dual_sa818s_machine_design_hil_open", contract["status"])
        self.assertIn("independent", contract["evidence"])
        self.assertIn("never authorize", contract["failure_semantics"])
        self.assertIn("consumes no P05", contract["filter_reopen_gate"])

        required = {
            "voice": "nicerf_sa818s_u_v18",
            "voice_v": "nicerf_sa818s_v_v18",
            "voice_rf_esd": "nexperia_pesd24vy1bsf",
            "voice_detector_series_attenuator": "yageo_rc0402fr_075k1l",
            "voice_detector_match": "yageo_rc0402fr_0752r3l",
            "voice_detector_filter": "murata_grm1555c1h121ja01d",
            "voice_detector_bypass": "yageo_cc0402krx7r9bb104",
            "voice_evidence_hold_diode": "diodes_bat54_7_f",
            "voice_evidence_hold_cap": "tdk_c1608x7r1c105k080ac",
            "voice_evidence_hold_pulldown": "yageo_rc0402fr_0710kl",
            "det_voice": "adi_ad8314acpz_rl7",
            "det_voice_v": "adi_ad8314acpz_rl7",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        esd = self.database["devices"]["nexperia_pesd24vy1bsf"]
        self.assertEqual(24, esd["electrical_contract"]["reverse_stand_off_v"])
        self.assertEqual(0.17, esd["electrical_contract"]["typical_capacitance_pf"])
        self.assertEqual("1", esd["contacts"]["K1"]["physical"])
        self.assertEqual("2", esd["contacts"]["K2"]["physical"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("voice.ANT", "voice_external_sma.RF", "VOICE_U_EXTERNAL_RF_50R"),
            ("voice.ANT", "voice_rf_esd.K1", "VOICE_U_EXTERNAL_RF_50R"),
            ("voice.ANT", "voice_detector_series_attenuator.END_1", "VOICE_U_EXTERNAL_RF_50R"),
            ("voice_detector_series_attenuator.END_2", "det_voice.RFIN", "VOICE_U_RF_SAMPLE"),
            ("det_voice.RFIN", "voice_detector_match.END_1", "VOICE_U_RF_SAMPLE"),
            ("voice_evidence_hold_diode.K", "det_voice.ENBL", "VOICE_EVIDENCE_HOLD"),
            ("det_voice.V_UP", "evidence_cmp_voice.IN_N", "VOICE_DETECT_V"),
            ("voice_v.ANT", "voice_v_external_sma.RF", "VOICE_V_EXTERNAL_RF_50R"),
            ("voice_v.ANT", "voice_v_rf_esd.K1", "VOICE_V_EXTERNAL_RF_50R"),
            ("voice_v_detector_series_attenuator.END_2", "det_voice_v.RFIN", "VOICE_V_RF_SAMPLE"),
            ("det_voice_v.V_UP", "evidence_cmp_voice_v.IN_N", "VOICE_V_DETECT_V"),
        ):
            self.assertIn(route, routes)

        self.assertFalse(any(
            route["from"] == "abstract:VOICE-qualified-RF-tap"
            for route in candidate["fixed_routes"]
        ))
        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])
        self.assertIn("P05", candidate["contact_accounting"]["slow_io"]["used"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "PESD24VY1BSF<br/>24-V ultra-low-capacitance external voice RF ESD diode",
            "RC0402FR-075K1L<br/>actual-TX 5.1-kOhm RF series sampler",
            "RC0402FR-0752R3L<br/>AD8314 52.3-Ohm detector input shunt",
            "AD8314ACPZ-RL7<br/>SA818S-U UHF RF power detector",
            "AD8314ACPZ-RL7<br/>SA818S-V VHF RF power detector",
        ):
            self.assertIn(token, rendered)

    def test_i6_exact_ir_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["ir_endpoint_contract"]
        self.assertEqual("DEC-0095", contract["decision"])
        self.assertIn("paper_reviewed_exact_dual_receiver", contract["status"])
        self.assertIn("no new GPIO or slow-I/O", contract["owner_and_pins"])
        self.assertIn("never creates measured carrier provenance", contract["robust_receive"])
        self.assertIn("never authorizes TX", contract["actual_optical_evidence"])

        required = {
            "ir_demod": "vishay_tsop75238tr",
            "ir_carrier": "vishay_tsmp95000tt",
            "ir_return_buffer": "nexperia_74lvc2g126dp_125",
            "ir_emitter": "vishay_vsmy14940",
            "ir_emitter_limit": "fh_rs_06k47r0ft",
            "ir_tx_mosfet": "diodes_dmn2056u_7",
            "ir_tx_carrier_pulldown": "yageo_rc0402fr_0710kl",
            "det_ir": "vishay_vemd1060x01",
            "ir_evidence_amp": "ti_tlv9061_idbvr",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        c5 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "c5"
        }
        self.assertEqual("IR_RX_DEMOD", c5["GPIO0"]["net"])
        self.assertEqual("IR_RX_CARRIER", c5["GPIO1"]["net"])
        self.assertEqual("IR_FRONTEND_PWR_EN", c5["GPIO4"]["net"])
        self.assertEqual("IR_TX_CARRIER", c5["GPIO6"]["net"])
        self.assertEqual("IR_TX_EVIDENCE_N", c5["GPIO24"]["net"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("ir_demod.OUT", "ir_return_buffer.1A", "IR_DEMOD_LOCAL_N"),
            ("ir_carrier.CARRIER_OUT", "ir_return_buffer.2A", "IR_CARRIER_LOCAL_N"),
            ("ir_emitter_limit.END_2", "ir_emitter.ANODE", "IR_LED_ANODE_LIMITED"),
            ("c5.GPIO6", "ir_safe_gate.A", "IR_TX_CARRIER"),
            ("ir_safe_gate.A", "ir_tx_carrier_pulldown.END_1", "IR_TX_CARRIER"),
            ("safe_latch.Q", "ir_safe_gate.B", "RUN_PERMIT"),
            ("ir_safe_gate.Y", "ir_tx_gate_series.END_1", "IR_TX_CARRIER_SAFE"),
            ("det_ir.CATHODE", "ir_evidence_amp.IN_MINUS", "IR_OPTICAL_SUM"),
            ("ir_evidence_amp.OUT", "evidence_cmp_a.IN3_N", "IR_DETECT_V"),
        ):
            self.assertIn(route, routes)

        localization = candidate["safety_contract"]["evidence"]["physical_localization"]
        self.assertIn("no detector analog signal", localization)
        self.assertIn("no IR carrier", localization)
        ir_gate = self.database["devices"]["ti_sn74lvc1g08_dckr"]
        self.assertEqual("1", ir_gate["contacts"]["A"]["physical"])
        self.assertEqual("4", ir_gate["contacts"]["Y"]["physical"])
        voice_cmp = self.database["devices"]["ti_tlv1821_dckr"]
        self.assertEqual("1", voice_cmp["contacts"]["OUT"]["physical"])
        self.assertEqual("5", voice_cmp["contacts"]["VPLUS"]["physical"])

        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])
        self.assertIn("P05", candidate["contact_accounting"]["slow_io"]["used"])
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "TSOP75238TR<br/>38-kHz AGC2 demodulating IR receiver",
            "TSMP95000TT<br/>30-to-60-kHz carrier-learning IR receiver",
            "VSMY14940<br/>side-view 940-nm consumer IR transmit emitter",
            "TLV9061IDBVR<br/>AON physical-optical transimpedance amplifier",
        ):
            self.assertIn(token, rendered)

    def test_i6_exact_si4732_dual_input_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["receiver_rf_electrical_contract"]
        self.assertEqual("DEC-0096", contract["decision"])
        self.assertIn("paper_reviewed_i6_exact_si4732", contract["status"])
        self.assertIn("no RF switch", contract["scope"])
        self.assertIn("non-50-Ohm", contract["ami_path"])
        self.assertIn("Arbitrary long coax is forbidden", contract["external_pod_contract"])

        required = {
            "receiver": "skyworks_si4732_a10_gsr",
            "receiver_fmi_esd": "littelfuse_sesd0402x1un_0020_090",
            "receiver_fmi_match_inductor": "murata_lqw15an56ng00d",
            "receiver_fmi_coupling_cap": "murata_grm1555c1h102ja01d",
            "receiver_ami_esd": "littelfuse_sesd0402x1un_0020_090",
            "receiver_ami_coupling_cap": "murata_grm155r71a474ke01d",
        }
        for instance, device_id in required.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        receiver = self.database["devices"]["skyworks_si4732_a10_gsr"]
        self.assertEqual("active_orderable", receiver["lifecycle"])
        self.assertEqual("C2155558", receiver["assembly_contract"]["jlcpcb_part_number"])
        self.assertEqual(
            {
                "LOUT_DFS": "1",
                "GPO3_DCLK": "2",
                "GPO2_INTB": "3",
                "GPO1": "4",
                "NC": "5",
                "FMI": "6",
                "RFGND": "7",
                "AMI": "8",
                "RST": "9",
                "SENB": "10",
                "SCLK": "11",
                "SDIO": "12",
                "RCLK": "13",
                "VDD": "14",
                "GND": "15",
                "ROUT_DOUT": "16",
            },
            {
                name: contact["physical"]
                for name, contact in receiver["contacts"].items()
            },
        )

        inductor = self.database["devices"]["murata_lqw15an56ng00d"]
        self.assertEqual(56, inductor["electrical_contract"]["inductance_nh"])
        self.assertEqual("active_factory_stocked_standard_pcba", inductor["lifecycle"])
        self.assertIn("orderable_source", inductor)

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("receiver_fmsw_external_sma.RF", "receiver_fmi_esd.K", "RX_FMSW_BOUNDARY_RF"),
            ("receiver_fmi_esd.A", "abstract:rf-ground-dedicated-via", "RX_FMSW_ESD_GROUND"),
            ("receiver_fmi_match_inductor.END_2", "receiver_fmi_coupling_cap.END_1", "RX_FMSW_MATCHED_RF"),
            ("receiver_fmi_coupling_cap.END_2", "receiver.FMI", "RX_FMI_RF"),
            ("receiver_amlw_external_sma.RF", "receiver_ami_esd.K", "RX_AMLW_BOUNDARY_RF"),
            ("receiver_ami_coupling_cap.END_2", "receiver.AMI", "RX_AMI_RF"),
        ):
            self.assertIn(route, routes)

        self.assertFalse(any(
            endpoint in {
                "abstract:RX-FM-SW-SMA-front-end",
                "abstract:RX-AM-LW-loop-pod",
            }
            for route in candidate["fixed_routes"]
            for endpoint in (route["from"], route["to"])
        ))
        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])
        self.assertIn("P05", candidate["contact_accounting"]["slow_io"]["used"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "LQW15AN56NG00D<br/>56-nH high-Q FM first target on FM/SW port",
            "GRM1555C1H102JA01D<br/>1-nF C0G FMI AC-coupling capacitor",
            "GRM155R71A474KE01D<br/>0.47-uF AMI AC-coupling capacitor",
            "GCT RFPC-SMA31-FN-175-A<br/>dedicated non-50-Ohm AM/LW loop-pod standard-SMA jack",
        ):
            self.assertIn(token, rendered)

    def test_i6_consolidated_one_group_qualification_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["i6_consolidated_qualification_contract"]
        self.assertEqual("DEC-0097", contract["decision"])
        self.assertIn("paper_reviewed_i6_consolidated", contract["status"])
        self.assertEqual(
            "prohibited",
            contract["runtime_invariant"]["cross_group_simultaneous_runtime"],
        )
        self.assertIn(
            "never_runtime_permission",
            contract["runtime_invariant"]["cross_group_lab_injection"],
        )

        self.assertEqual(
            [group["id"] for group in candidate["signal_group_policy"]["groups"]],
            contract["covered_signal_groups"],
        )
        self.assertEqual(
            {
                "FX-I6-CFG",
                "FX-I6-CONDUCTED",
                "FX-I6-OTA",
                "FX-I6-N24-T1",
                "FX-I6-OPTICAL",
                "FX-I6-DIGITAL",
                "FX-I6-FAULT",
                "FX-I6-THERMAL",
            },
            {fixture["id"] for fixture in contract["fixtures"]},
        )
        self.assertIn("UI <=100 ms", contract["acceptance"]["no_stall"])
        self.assertIn("actual-TX", contract["acceptance"]["transition"])
        self.assertIn("false negative", contract["acceptance"]["evidence"])
        self.assertIn("not_executed", contract["physical_evidence_state"])

        quiet_ids = candidate["quiet_state_policy"]["required_contracts"]
        self.assertNotIn("RECEIVER_AUDIO_QUIET", quiet_ids)
        for quiet_id in (
            "RECEIVER_QUIET",
            "CODEC_AUDIO_QUIET",
            "VOICE_INTERFACE_QUIET",
        ):
            self.assertIn(quiet_id, quiet_ids)
        self.assertEqual(
            set(quiet_ids),
            {
                quiet["id"]
                for quiet in candidate["quiet_state_policy"]["contracts"]
            },
        )

        for endpoint_contract in (
            candidate["native_rf_electrical_contract"],
            candidate["cc_rf_electrical_contract"],
            candidate["voice_rf_electrical_contract"],
            candidate["ir_endpoint_contract"],
            candidate["receiver_rf_electrical_contract"],
        ):
            remaining = " ".join(endpoint_contract["remaining_hil"])
            self.assertIn("foreign signal group", remaining)
            self.assertIn("Laboratory characterization only", remaining)

        repo = Path(__file__).resolve().parents[3]
        for relative in (
            "drafts/project-history-2026-08-19/review/architecture/RFQ-0001-zero-based-rf-zoning-coexistence.md",
            "drafts/project-history-2026-08-19/review/architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md",
        ):
            text = (repo / relative).read_text()
            self.assertIn("LAB-CHAR", text)
            self.assertNotIn("only one exact contained pair may become `Q`", text)

    def test_qspi_display_decision_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertEqual("DISPLAY_SD_SPI_D1", s3["GPIO4"]["net"])
        self.assertEqual("io", s3["GPIO4"]["direction"])
        self.assertIn("high-Z", s3["GPIO4"]["sharing_proof"])
        self.assertEqual("LCD_QSPI_D2", s3["GPIO41"]["net"])
        self.assertEqual("LCD_QSPI_D3", s3["GPIO42"]["net"])
        self.assertNotIn("GPIO41", candidate["free_gpio"]["s3"])
        self.assertNotIn("GPIO42", candidate["free_gpio"]["s3"])
        display_contract = next(
            item for item in candidate["resource_contracts"]
            if item["id"] == "DISPLAY_SD_SPI"
        )
        self.assertIn("<=1 ms", display_contract["arbitration"])
        self.assertNotIn("256 B", display_contract["arbitration"])

    def test_inner_face_package_heights_are_manufacturer_bounded(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        expected = {
            "slow_io": (0.60, "RGJ0032A"),
            "codec": (0.60, "Revision 17.0"),
            "nvdc_charger": (1.00, "RQM0029A"),
            "pack_admission": (1.10, "DGS0020A"),
            "safety_controller": (1.10, "DGS0020A"),
            "aon_buck": (0.60, "DRL0008A"),
            "main_buck": (0.60, "DRL0006A"),
            "voice_buck": (0.60, "DRL0006A"),
            "ext_buck": (0.60, "DRL0006A"),
            "product_usb_protector": (0.80, "RUK0020B"),
            "pd_controller": (0.80, "REF0038A"),
            "speaker_amp": (0.63, "U-DFN3030-8 Type E"),
        }
        for instance, (height, basis) in expected.items():
            device = self.database["devices"][candidate["instances"][instance]]
            self.assertEqual(height, device["dimensions_mm"][2], instance)
            self.assertIn(basis, device["mechanical_height_basis"], instance)

    def test_exact_hmx_display_electrical_fit_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("qdtech_hmx035ctft_001", candidate["instances"]["display"])
        self.assertEqual(
            "hirose_df40c_2_0_40ds_0_4v_51", candidate["instances"]["display_connector"]
        )
        self.assertEqual(
            "hirose_df40c_40dp_0_4v_51", candidate["instances"]["display_adapter_plug"]
        )
        self.assertEqual(
            "hirose_fh34srj_40s_0_5sh_99", candidate["instances"]["display_panel_connector"]
        )
        self.assertEqual("ti_tps2553drvr_1", candidate["instances"]["backlight_efuse"])
        self.assertEqual(
            "yageo_rc0402jr_070rl",
            candidate["instances"]["backlight_series_resistor"],
        )

        display = self.database["devices"][candidate["instances"]["display"]]
        self.assertEqual(
            "HMX035CTFT-001 (QDtech schematic assembly marking)", display["mpn"]
        )
        self.assertEqual([54.5, 83.0, 3.2], display["dimensions_mm"])
        self.assertEqual([320, 480], display["pixel_resolution"])
        self.assertEqual([48.96, 73.44], display["active_area_mm"])
        self.assertEqual(
            [2.77, 2.15], display["active_area_offset_from_body_top_left_mm"]
        )
        self.assertEqual([49.96, 74.44], display["viewing_area_mm"])
        self.assertEqual(
            [2.27, 1.65], display["viewing_area_offset_from_body_top_left_mm"]
        )
        self.assertEqual([54.5, 83.0], display["effective_touch_area_mm"])
        self.assertEqual(
            [54.5, 101.5, 10.0], display["donor_module_dimensions_mm_published_pdf"]
        )
        self.assertEqual(10.5, display["donor_module_depth_current_product_page_mm"])
        self.assertIn("screen body", display["mechanical_dimension_scope"])
        self.assertIn("excluding flex and adhesive", display["mechanical_dimension_scope"])
        expected_physical = {
            "TP_I2C_SCL": "1",
            "TP_I2C_SDA": "2",
            "TP_INT": "3",
            "TP_RESET": "4 (TP_RESXP)",
            "QSPI_CS": "9 (CS)",
            "QSPI_D1": "10 (RS)",
            "QSPI_CLK": "11 (WR)",
            "QSPI_D0": "13 (SDA)",
            "RESET": "15",
            "QSPI_D2": "17 (DB0)",
            "QSPI_D3": "18 (DB1)",
            "LEDA": "33",
            "IM0": "38",
            "IM1": "39",
            "IM2": "40",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, display["contacts"][contact]["physical"])

        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertEqual(
            [
                "sd_miso_series.END_2",
                "sd_host_d1_pullup.END_1",
                "display_connector.PIN_10",
            ],
            s3["GPIO4"]["peers"],
        )
        self.assertIn("sd_host_buffer.1A", s3["GPIO18"]["peers"])
        self.assertIn("display_connector.PIN_11", s3["GPIO18"]["peers"])
        self.assertIn("sd_host_buffer.2A", s3["GPIO46"]["peers"])
        self.assertIn("display_connector.PIN_13", s3["GPIO46"]["peers"])
        self.assertEqual("display_connector.PIN_9", s3["GPIO38"]["peers"][0])
        self.assertIn("lcd_host_cs_pullup.END_1", s3["GPIO38"]["peers"])
        self.assertEqual("ENCODER_A", s3["GPIO39"]["net"])
        self.assertEqual("i", s3["GPIO39"]["direction"])
        self.assertEqual("PCNT0", s3["GPIO39"]["controller"])
        self.assertIn("encoder.A", s3["GPIO39"]["peers"])
        self.assertEqual("ENCODER_B", s3["GPIO47"]["net"])
        self.assertEqual("PCNT0", s3["GPIO47"]["controller"])
        self.assertIn("touch_irq_buffer.Y", s3["GPIO45"]["peers"])
        self.assertEqual(["backlight_gate_series.END_1"], s3["GPIO40"]["peers"])
        self.assertEqual(["display_connector.PIN_17"], s3["GPIO41"]["peers"])
        self.assertEqual(["display_connector.PIN_18"], s3["GPIO42"]["peers"])
        self.assertNotIn("LCD_DC", {row["net"] for row in s3.values()})
        self.assertEqual([], candidate["free_gpio"]["s3"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(("slow_io.P06", "display_connector.PIN_15", "LCD_RST_N"), routes)
        self.assertIn(("slow_io.P07", "display_connector.PIN_4", "TOUCH_RST_N"), routes)
        self.assertIn(("display_connector.PIN_3", "touch_irq_buffer.A", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertIn(("display.TP_INT", "display_touch_controller.TP_INT", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertIn(("touch_irq_pullup.END_2", "display_connector.PIN_3", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertIn(("touch_irq_buffer.Y", "abstract:SYS_INT_N_WIRED_LOW", "SYS_INT_N"), routes)
        self.assertIn(("abstract:3V3_MAIN", "display_connector.PIN_39", "LCD_IM1_HIGH"), routes)
        self.assertIn(("display_connector.PIN_38", "abstract:power-ground", "LCD_IM0_LOW"), routes)
        self.assertIn(("display_connector.PIN_40", "abstract:power-ground", "LCD_IM2_LOW"), routes)
        self.assertIn(("backlight_efuse.OUT", "display_connector.PIN_33", "LCD_LEDA_PROTECTED"), routes)
        self.assertIn(("display_connector.PIN_34", "backlight_series_resistor.END_1", "LCD_LEDK"), routes)
        self.assertIn(("backlight_series_resistor.END_2", "backlight_mosfet.D", "LCD_LEDK_LIMITED"), routes)

        display_contract = candidate["display_contract"]
        self.assertEqual("DEC-0084", display_contract["decision"])
        self.assertIn("back-power", display_contract["logic_supply"])
        self.assertIn("174-to-234-mA", display_contract["backlight"])
        self.assertIn("at least 120 ms", display_contract["reset_defaults"])
        self.assertIn("power cycling", display_contract["fault_behavior"])

    def test_exact_isolated_microsd_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["storage_contract"]
        self.assertEqual("DEC-0085", contract["decision"])
        self.assertIn("no GPIO", contract["paper_cost_delta_usd_at_100_excluding_socket"])
        self.assertIn("back-power", contract["powered_off_isolation"])
        self.assertIn("DAT0-DAT3", contract["pulls_and_series"])
        self.assertIn("CLK, CMD, DAT0-DAT3, VDD and card-detect", contract["esd"])
        self.assertIn("SPI mode", contract["sequence"])
        self.assertIn("unexpected-removal", " ".join(contract["remaining_hil"]))

        expected_instances = {
            "sd": "hirose_dm3at_sf_pejm5",
            "sd_power_switch": "ti_tps22919_dckr",
            "sd_host_buffer": "ti_sn74lvc3g34_dcur",
            "sd_miso_buffer": "ti_sn74lvc1g125_dckr",
            "sd_esd_a": "ti_tpd4e05u06_dqar",
            "sd_esd_b": "ti_tpd4e05u06_dqar",
            "sd_power_bulk_cap": "murata_grm21br60j226me39l",
            "sd_sck_series": "panasonic_erj_2rkf22r0x",
            "sd_cmd_series": "panasonic_erj_2rkf22r0x",
            "sd_cs_series": "panasonic_erj_2rkf22r0x",
            "sd_miso_series": "panasonic_erj_2rkf22r0x",
            "sd_detect_series": "yageo_rc0603fr_071kl",
        }
        for instance, device in expected_instances.items():
            self.assertEqual(device, candidate["instances"][instance])

        socket = self.database["devices"][candidate["instances"]["sd"]]
        self.assertEqual("Hirose DM3AT-SF-PEJM5", socket["mpn"])
        self.assertEqual("switch A", socket["contacts"]["DETECT_A"]["physical"])
        self.assertEqual("switch B", socket["contacts"]["DETECT_B"]["physical"])

        host_buffer = self.database["devices"][candidate["instances"]["sd_host_buffer"]]
        self.assertEqual("1", host_buffer["contacts"]["1A"]["physical"])
        self.assertEqual("7", host_buffer["contacts"]["1Y"]["physical"])
        miso_buffer = self.database["devices"][candidate["instances"]["sd_miso_buffer"]]
        self.assertEqual("1", miso_buffer["contacts"]["OE_N"]["physical"])
        self.assertEqual("4", miso_buffer["contacts"]["Y"]["physical"])
        esd = self.database["devices"][candidate["instances"]["sd_esd_a"]]
        self.assertEqual("3", esd["contacts"]["GND_3"]["physical"])
        self.assertEqual("8", esd["contacts"]["GND_8"]["physical"])

        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertIn("sd_miso_buffer.OE_N", s3["GPIO5"]["peers"])
        self.assertIn("sd_host_buffer.1A", s3["GPIO18"]["peers"])
        self.assertIn("sd_host_buffer.2A", s3["GPIO46"]["peers"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("abstract:3V3_MAIN", "sd_power_switch.IN", "3V3_MAIN"),
            ("sd_power_switch.VOUT", "sd.VDD", "SD_CARD_3V3"),
            ("sd_power_switch.QOD", "sd_power_switch.VOUT", "SD_CARD_3V3"),
            ("sd_host_buffer.1Y", "sd_sck_series.END_1", "SD_CLK_BUFFERED"),
            ("sd_host_buffer.2Y", "sd_cmd_series.END_1", "SD_CMD_BUFFERED"),
            ("sd_host_buffer.3Y", "sd_cs_series.END_1", "SD_CS_BUFFERED_N"),
            ("sd.DAT0", "sd_miso_buffer.A", "SD_DAT0_MISO_PROTECTED"),
            ("sd_miso_buffer.Y", "sd_miso_series.END_1", "SD_MISO_BUFFERED"),
            ("sd_card_cmd_pullup.END_2", "sd.CMD", "SD_CMD_PROTECTED"),
            ("sd_card_dat0_pullup.END_2", "sd.DAT0", "SD_DAT0_MISO_PROTECTED"),
            ("sd_card_dat1_pullup.END_2", "sd.DAT1", "SD_DAT1_PROTECTED"),
            ("sd_card_dat2_pullup.END_2", "sd.DAT2", "SD_DAT2_PROTECTED"),
            ("sd_card_dat3_pullup.END_2", "sd.CD_DAT3", "SD_DAT3_CS_PROTECTED_N"),
            ("sd.DETECT_B", "abstract:power-ground", "POWER_GROUND"),
            ("sd.DETECT_A", "sd_detect_series.END_1", "SD_CARD_DETECT_RAW_N"),
            ("sd_detect_series.END_2", "slow_io.P21", "SD_CARD_DETECT_N"),
            ("sd.SHIELD", "abstract:power-ground-multivia", "SD_SHIELD_GROUND"),
        ):
            self.assertIn(route, routes)

        for endpoint in (
            "sd_esd_a.D1_PLUS",
            "sd_esd_a.D1_MINUS",
            "sd_esd_a.D2_PLUS",
            "sd_esd_a.D2_MINUS",
            "sd_esd_b.D1_PLUS",
            "sd_esd_b.D1_MINUS",
            "sd_esd_b.D2_PLUS",
            "sd_esd_b.D2_MINUS",
        ):
            self.assertTrue(any(route[1] == endpoint for route in routes), endpoint)

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "SN74LVC3G34DCUR<br/>three-channel Ioff SCK/CMD/CS card-side buffer",
            "Texas Instruments SN74LVC1G125DCKR<br/>CS-gated Ioff DAT0/MISO return buffer",
            "Texas Instruments TPD4E05U06DQAR<br/>four-channel low-capacitance microSD signal ESD array A",
            "Murata GRM21BR60J226ME39L<br/>22-uF switched-card bulk capacitor",
        ):
            self.assertIn(label, rendered)

    def test_exact_es8311_digital_fit_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("everest_es8311_qfn20", candidate["instances"]["codec"])

        codec = self.database["devices"][candidate["instances"]["codec"]]
        self.assertEqual("Everest Semiconductor ES8311", codec["mpn"])
        expected_physical = {
            "CCLK": "1",
            "MCLK": "2",
            "SCLK": "6 (SCLK/DMIC_SCL)",
            "ASDOUT": "7",
            "LRCK": "8",
            "DSDIN": "9",
            "OUTP": "12",
            "OUTN": "13",
            "MIC1N": "17",
            "MIC1P": "18 (MIC1P/DMIC_SDA)",
            "CDATA": "19",
            "CE": "20",
            "EPAD": "21 (exposed thermal pad)",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, codec["contacts"][contact]["physical"])

        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertIn("codec_i2c_iso.1A", s3["GPIO1"]["peers"])
        self.assertIn("codec_i2c_iso.2A", s3["GPIO2"]["peers"])
        self.assertEqual(["codec_i2s_bclk_iso.A"], s3["GPIO15"]["peers"])
        self.assertEqual(["codec_i2s_ws_iso.A"], s3["GPIO16"]["peers"])
        self.assertEqual(["codec_i2s_dout_iso.A"], s3["GPIO17"]["peers"])
        self.assertIn("codec_i2s_din_iso.Y", s3["GPIO0"]["peers"])
        self.assertIn("s3_boot_pullup.END_2", s3["GPIO0"]["peers"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(
            ("slow_io.P10", "codec_power_switch.ON", "CODEC_PWR_EN"),
            routes,
        )
        self.assertNotIn("CODEC_EN", {route["net"] for route in candidate["fixed_routes"]})
        self.assertIn(
            ("codec_ce_pullup.END_2", "codec.CE", "CODEC_I2C_ADDR_0X19"),
            routes,
        )
        self.assertIn(("codec.MCLK", "abstract:no-connect", "CODEC_MCLK_NC"), routes)
        self.assertIn(("codec.OUTP", "audio_speaker_selector.S1A", "CODEC_DAC_OUT_P"), routes)
        self.assertIn(("codec.OUTN", "audio_speaker_selector.S2A", "CODEC_DAC_OUT_N"), routes)
        self.assertIn(("slow_io.P27", "audio_rx_mux.S", "RX_AUDIO_SOURCE_SEL"), routes)
        self.assertIn(("speaker_input_p_gain.END_2", "speaker_amp.IN_PLUS", "PAM_AUDIO_IN_P"), routes)
        self.assertIn(("speaker_input_n_gain.END_2", "speaker_amp.IN_MINUS", "PAM_AUDIO_IN_N"), routes)
        self.assertIn(("voice_mic_coupling.END_2", "voice.MIC_IN", "VOICE_U_MIC_IN"), routes)
        self.assertIn(("voice_v_mic_coupling.END_2", "voice_v.MIC_IN", "VOICE_V_MIC_IN"), routes)
        self.assertIn(("audio_safe_gate.1Y", "audio_speaker_selector.SEL1", "AUDIO_SPK_SEL_SAFE"), routes)
        self.assertIn(("audio_safe_gate.1Y", "audio_speaker_selector.SEL2", "AUDIO_SPK_SEL_SAFE"), routes)
        self.assertIn(("audio_safe_gate.2Y", "audio_tx_selector.IN", "AUDIO_TX_SEL_SAFE"), routes)
        self.assertIn("P27", candidate["contact_accounting"]["slow_io"]["used"])
        self.assertEqual({}, candidate["contact_accounting"]["slow_io"]["reserved"])
        self.assertEqual([], candidate["free_gpio"]["s3"])
        self.assertEqual("AUDIO_ARM", s3["GPIO6"]["net"])
        self.assertEqual(
            [
                "audio_safe_gate.1B",
                "audio_safe_gate.2B",
                "codec_i2s_din_boot_gate.B",
            ],
            s3["GPIO6"]["peers"],
        )
        expected_audio_instances = {
            "audio_rx_mux": "ti_sn74lvc1g3157_dbvr",
            "audio_capture_buffer": "ti_tlv9061_idbvr",
            "audio_speaker_selector": "ti_tmux1136_dgsr",
            "audio_tx_selector": "ti_ts5a63157_dckr",
            "audio_safe_gate": "ti_sn74lvc2g08_dcur",
            "speaker_amp": "diodes_pam8302a_aycr",
        }
        for instance, device_id in expected_audio_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

    def test_tac5111_reference_uses_exact_exposed_contacts(self):
        codec = self.database["devices"]["ti_tac5111_irger"]
        self.assertEqual("Texas Instruments TAC5111IRGER", codec["mpn"])
        self.assertEqual("reference_only", codec["qualification"])
        expected_physical = {
            "DREG": "1",
            "BCLK": "2",
            "FSYNC": "3",
            "DOUT": "4",
            "DIN": "5",
            "IOVDD": "6",
            "SCL": "7",
            "SDA": "8",
            "ADDR": "13",
            "IN1P": "15",
            "IN1M": "16",
            "OUT1M": "19",
            "OUT1P": "20",
            "AVDD": "23",
            "VREF": "24",
            "VSS_THERMAL": "exposed thermal pad",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, codec["contacts"][contact]["physical"])
        for corner in ("VSS_A1", "VSS_A2", "VSS_A3", "VSS_A4"):
            self.assertIn(corner, codec["contacts"])

    def test_complete_audio_path_references_use_exact_order_codes_and_contacts(self):
        expected = {
            "ti_tmux1136_dgsr": (
                "Texas Instruments TMUX1136DGSR",
                {"SEL1": "1", "S1A": "2", "GND": "3", "S2A": "4", "SEL2": "5", "D2": "6", "S2B": "7", "VDD": "8", "S1B": "9", "D1": "10"},
            ),
            "ti_ts5a63157_dckr": (
                "Texas Instruments TS5A63157DCKR",
                {"NO": "1", "GND": "2", "NC": "3", "COM": "4", "VCC": "5", "IN": "6"},
            ),
            "ti_tlv9061_idbvr": (
                "TLV9061IDBVR",
                {"OUT": "1", "V_MINUS": "2", "IN_PLUS": "3", "IN_MINUS": "4", "V_PLUS": "5"},
            ),
            "ti_sn74lvc2g08_dcur": (
                "Texas Instruments SN74LVC2G08DCUR",
                {"1A": "1", "1B": "2", "2Y": "3", "GND": "4", "2A": "5", "2B": "6", "1Y": "7", "VCC": "8"},
            ),
            "ti_sn74lvc1g3157_dbvr": (
                "Texas Instruments SN74LVC1G3157DBVR",
                {"B2": "1", "GND": "2", "B1": "3", "A_COM": "4", "VCC": "5", "S": "6"},
            ),
            "diodes_pam8302a_aycr": (
                "Diodes Incorporated PAM8302AAYCR",
                {"SD": "1", "NC": "2", "IN_PLUS": "3", "IN_MINUS": "4", "VO_PLUS": "5", "VDD": "6", "GND": "7", "VO_MINUS": "8"},
            ),
        }
        for device_id, (mpn, contacts) in expected.items():
            with self.subTest(device=device_id):
                device = self.database["devices"][device_id]
                self.assertEqual(mpn, device["mpn"])
                self.assertIn(
                    device["qualification"],
                    ("reference_only", "verified_reference", "verified_candidate"),
                )
                for contact, physical in contacts.items():
                    self.assertEqual(physical, device["contacts"][contact]["physical"])

        expected_orderable_urls = {
            "ti_tmux1136_dgsr": "https://www.ti.com/product/TMUX1136/part-details/TMUX1136DGSR",
            "ti_ts5a63157_dckr": "https://www.ti.com/product/TS5A63157/part-details/TS5A63157DCKR",
            "ti_tlv9061_idbvr": "https://www.ti.com/product/TLV9061/part-details/TLV9061IDBVR",
            "ti_sn74lvc2g08_dcur": "https://www.ti.com/product/SN74LVC2G08/part-details/SN74LVC2G08DCUR",
            "ti_sn74lvc1g3157_dbvr": "https://www.ti.com/product/SN74LVC1G3157/part-details/SN74LVC1G3157DBVR",
        }
        for device_id, url in expected_orderable_urls.items():
            with self.subTest(orderable_device=device_id):
                self.assertEqual(url, self.database["devices"][device_id]["orderable_source"]["url"])

    def test_i5_exact_audio_receiver_endpoint_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["audio_receiver_contract"]
        self.assertEqual("DEC-0090", contract["decision"])
        self.assertEqual(
            "paper_reviewed_i5_exact_endpoints_hil_open",
            contract["status"],
        )

        slow = candidate["contact_accounting"]["slow_io"]
        self.assertEqual(set(), set(slow["free"]))
        self.assertIn("P05", set(slow["used"]))
        self.assertIn("P03", slow["used"])
        self.assertIn("P04", slow["used"])
        self.assertEqual({}, slow["reserved"])
        self.assertEqual(
            {"P00", "P01", "P02", "P10", "P11", "P12", "P13", "P14", "P15", "P24", "P27"},
            set(slow["used"]) & {"P00", "P01", "P02", "P10", "P11", "P12", "P13", "P14", "P15", "P24", "P27"},
        )

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("slow_io.P00", "audio_capture_selector.IN", "AUDIO_CAPTURE_MIC_SEL"),
            ("slow_io.P01", "speaker_amp.SD", "SPEAKER_AMP_EN"),
            ("headset_detect_series.END_2", "slow_io.P02", "HEADSET_ABSENT"),
            ("headset_control_io.P0", "headset_mic_selector.IN", "HEADSET_INTERNAL_MIC_SEL"),
            ("codec_supervisor.RESET_N", "codec_i2c_iso.1C", "CODEC_READY"),
            ("codec_supervisor.RESET_N", "codec_i2s_din_boot_gate.A", "CODEC_READY"),
            ("s3.GPIO6", "codec_i2s_din_boot_gate.B", "AUDIO_ARM"),
            ("codec_i2s_din_boot_gate.Y", "codec_i2s_din_iso.OE", "CODEC_DIN_READY"),
            ("receiver_supervisor.RESET_N", "receiver.RST", "RX_RST_N"),
            ("receiver_supervisor.RESET_N", "receiver_i2c_iso.1C", "RECEIVER_READY"),
            ("safe_ptt_or.1Y", "voice_control_mux_b.D1", "VOICE_PTT_SAFE_N"),
            ("voice_control_mux_b.S1A", "voice.PTT", "VOICE_U_PTT_N"),
            ("voice_control_mux_b.S1B", "voice_v.PTT", "VOICE_V_PTT_N"),
            ("voice_hl_driver.Y", "voice.HL", "VOICE_HL_OPEN_DRAIN"),
            ("voice_hl_driver.Y", "voice_v.HL", "VOICE_HL_OPEN_DRAIN"),
            ("voice_band_io.P0", "voice_control_mux_a.SEL1", "VOICE_V_SELECT"),
            ("voice_pd_gate.1Y", "voice.PD", "VOICE_U_PD"),
            ("voice_pd_gate.2Y", "voice_v.PD", "VOICE_V_PD"),
        ):
            self.assertIn(route, routes)

        self.assertEqual(
            "same_sky_sj_43504_smt_tr", candidate["instances"]["headphone_jack"]
        )
        self.assertEqual(
            "ti_tca9534a_pwr", candidate["instances"]["headset_control_io"]
        )
        self.assertIn(
            ("abstract:3V3_MAIN", "headset_control_io.A0", "HEADSET_IO_ADDR_A0_HIGH"),
            routes,
        )
        self.assertIn(
            ("headset_control_io.A1", "abstract:audio-ground", "HEADSET_IO_ADDR_A1_LOW"),
            routes,
        )
        self.assertIn(
            ("headset_control_io.A2", "abstract:audio-ground", "HEADSET_IO_ADDR_A2_LOW"),
            routes,
        )
        for pin in range(1, 8):
            self.assertIn(
                (
                    f"headset_control_io.P{pin}",
                    f"headset_control_p{pin}_pulldown.END_1",
                    f"HEADSET_IO_SPARE_P{pin}",
                ),
                routes,
            )
        self.assertFalse(
            any(
                route[0] == "slow_io.P02" and route[1] == "headset_mic_selector.IN"
                for route in routes
            )
        )
        self.assertIn("detect-only P02", contract["control_budget"])
        self.assertIn("0x39", contract["control_budget"])

        self.assertFalse(
            any(
                route[0] == "slow_io.P14" and route[1] == "voice.HL"
                for route in routes
            )
        )
        self.assertFalse(
            any(
                route[0] == "safe_ptt_or.1Y" and route[1] == "voice.PTT"
                for route in routes
            )
        )

        exact_i5_instances = {
            "codec",
            "codec_power_switch",
            "codec_supervisor",
            "codec_i2c_iso",
            "codec_i2s_bclk_iso",
            "codec_i2s_ws_iso",
            "codec_i2s_dout_iso",
            "codec_i2s_din_iso",
            "codec_i2s_din_boot_gate",
            "receiver",
            "receiver_power_switch",
            "receiver_supervisor",
            "receiver_i2c_iso",
            "receiver_irq_iso",
            "receiver_clock",
            "voice",
            "voice_v",
            "voice_supervisor",
            "voice_io_power_switch",
            "voice_band_io",
            "voice_band_inverter",
            "voice_pd_gate",
            "voice_control_mux_a",
            "voice_control_mux_b",
            "voice_audio_mux",
            "voice_hl_driver",
            "audio_capture_selector",
            "audio_capture_buffer",
            "audio_speaker_selector",
            "audio_tx_selector",
            "audio_safe_gate",
            "speaker_amp",
            "speaker",
            "microphone",
            "headphone_jack",
            "headphone_esd",
        }
        endpoints = {endpoint for route in routes for endpoint in route[:2]}
        for instance in sorted(exact_i5_instances):
            device = self.database["devices"][candidate["instances"][instance]]
            for contact in device["contacts"]:
                with self.subTest(instance=instance, contact=contact):
                    self.assertIn(f"{instance}.{contact}", endpoints)

    def test_rejects_duplicate_json_key_before_validation(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            GENERATOR.reject_duplicate_keys([("GPIO0", {}), ("GPIO0", {})])

    def test_rejects_module_internal_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].append("GPIO15")
        errors = self.errors_for(candidates)
        self.assertTrue(any("GPIO15" in error and "unknown GPIO" in error for error in errors), errors)

    def test_rejects_duplicate_allocation(self):
        candidates = copy.deepcopy(self.candidates)
        candidates[0]["allocations"].append(copy.deepcopy(candidates[0]["allocations"][0]))
        errors = self.errors_for(candidates)
        self.assertTrue(any("duplicate allocation" in error for error in errors), errors)

    def test_rejects_integrated_nrf_antenna_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["antenna_policy"]["integrated_pcb_antenna_baseline"] = True
        candidate["antenna_policy"]["nrf_dedicated_sma_count"] = 2
        candidate["instances"]["nrf2"] = "ebyte_e01_ml01s"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("integrated_pcb_antenna_baseline must be False" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("nrf_dedicated_sma_count must be 3" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("nrf2 must use the factory-stocked PA/LNA IPEX production module" in error for error in errors),
            errors,
        )

    def test_rejects_ten_sma_identity_or_si4732_split_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["antenna_policy"]["base_onboard_sma_count"] = 8
        candidate["antenna_policy"]["base_onboard_sma_paths"].remove("RX-AM/LW")
        candidate["antenna_policy"]["si4732_port_topology"] = "shared_switched_port"
        candidate["antenna_policy"]["si4732_shared_switch"] = True
        candidate["antenna_policy"]["si4732_ami_external_profile"] = "generic_long_coax"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("base_onboard_sma_count must be 10" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("base_onboard_sma_paths must be" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_port_topology must be 'dedicated_fmi_and_ami'" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_shared_switch must be False" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_ami_external_profile must be" in error for error in errors),
            errors,
        )

    def test_rejects_external_sma_polarity_decision_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        policy = candidate["antenna_policy"]
        policy["external_connector_decision"] = "IMP-0042"
        policy["device_connector_by_path"]["N24-0"] = "rp_sma_jack_pin_center"
        policy["antenna_mate_by_path"]["C5-2G4/5"] = "sma_plug_pin_center"
        policy["antenna_qualification_gate"]["minimum_orderable_qualified_mpns_per_group"] = 1
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("external_connector_decision must be 'DEC-0050'" in error for error in errors),
            errors,
        )
        self.assertTrue(any("device_connector_by_path must be" in error for error in errors), errors)
        self.assertTrue(any("antenna_mate_by_path must be" in error for error in errors), errors)
        self.assertTrue(any("antenna_qualification_gate must be" in error for error in errors), errors)

    def test_rejects_profiled_antenna_kit_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        policy = candidate["antenna_policy"]
        policy["kit_profile_decision"] = "IMP-0043"
        policy["availability_check_gate"] = "continuous_stock_polling"
        policy["full_field_kit_physical_items"] = 9
        policy["kit_profiles"]["nrf24"]["shared_exact_mpn"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(any("kit_profile_decision must be 'DEC-0055'" in error for error in errors), errors)
        self.assertTrue(any("availability_check_gate must be 'exact_mpn_selection'" in error for error in errors), errors)
        self.assertTrue(any("full_field_kit_physical_items must be 12" in error for error in errors), errors)
        self.assertTrue(any("kit_profiles must be" in error for error in errors), errors)

    def test_exact_sa818s_modules_do_not_regress_to_fictional_contacts(self):
        for device_id in ("nicerf_sa818s_u_v18", "nicerf_sa818s_v_v18"):
            voice = self.database["devices"][device_id]
            self.assertNotIn("SQ", voice["contacts"])
            self.assertNotIn("UPDATE", voice["contacts"])
            self.assertNotIn("VOXEN", voice["contacts"])
            self.assertIn("AUDIO_ON", voice["contacts"])
        for candidate in self.candidates:
            self.assertFalse(
                any(row["net"] == "VOICE_SQ" for row in candidate["allocations"]),
                candidate["id"],
            )

    def test_leading_voice_and_receiver_paths_use_exact_exposed_contacts(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("nicerf_sa818s_u_v18", candidate["instances"]["voice"])
        self.assertEqual("nicerf_sa818s_v_v18", candidate["instances"]["voice_v"])
        self.assertEqual("skyworks_si4732_a10_gsr", candidate["instances"]["receiver"])
        voice_services = {s["instance"]: set(s["contacts"]) for s in candidate["services"] if s["instance"] in {"voice", "voice_v"}}
        self.assertEqual({"voice", "voice_v"}, set(voice_services))
        self.assertTrue(all(contacts == {"UART_TX", "UART_RX", "PD"} for contacts in voice_services.values()))
        endpoints = {
            route[endpoint]
            for route in candidate["fixed_routes"]
            for endpoint in ("from", "to")
        }
        self.assertIn("voice.PD", endpoints)
        self.assertIn("voice_v.PD", endpoints)
        self.assertIn("receiver.FMI", endpoints)
        self.assertIn("receiver.AMI", endpoints)
        self.assertIn("receiver.GPO2_INTB", endpoints)

    def test_rf_micro_connector_provenance_stays_device_specific(self):
        s3 = self.database["devices"]["esp32_s3_wroom_1u_n16r2"]["rf_connector"]
        c5 = self.database["devices"]["esp32_c5_wroom_1u_n8r8"]["rf_connector"]
        nrf = self.database["devices"]["ebyte_e01_ml01sp4"]["rf_connector"]
        expected_families = ["Hirose U.FL", "I-PEX MHF I", "Amphenol AMC"]
        self.assertEqual(expected_families, s3["compatible_mating_families"])
        self.assertEqual(expected_families, c5["compatible_mating_families"])
        self.assertEqual(
            ["UMCC generation 1", "Hirose U.FL plug", "I-PEX MHF I plug"],
            nrf["compatible_mating_families"],
        )
        self.assertEqual(
            "manufacturer_drawing_locates_connector_gen1_mate_fit_hil_open",
            nrf["qualification"],
        )
        self.assertIn("manufacturer drawing fixes", nrf["finding"])

    def test_rejects_allocated_strap_without_proof(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        row = next(a for a in candidate["allocations"] if a["instance"] == "c5" and a["contact"] == "GPIO3")
        row.pop("strap_proof")
        errors = self.errors_for(candidates)
        self.assertTrue(any("strap without strap_proof" in error for error in errors), errors)

    def test_rejects_unaccounted_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].remove("GPIO24")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted GPIO" in error and "GPIO24" in error for error in errors), errors)

    def test_rejects_missing_recovery_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        service = next(s for s in candidate["services"] if s["instance"] == "rp")
        service["contacts"].remove("SWDIO")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing service contacts" in error and "SWDIO" in error for error in errors), errors)

    def test_accepts_one_complete_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        self.assertIn("GPIO11", service["contacts"])
        self.assertIn("GPIO12", service["contacts"])
        self.assertEqual([], self.errors_for(candidates))

    def test_rejects_partial_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        service["contacts"].remove("GPIO12")
        service["contacts"].remove("GPIO14")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing one complete service alternative" in error for error in errors), errors)

    def test_rejects_unaccounted_slow_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["contact_accounting"]["slow_io"]["used"].remove("P27")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted allocatable contacts" in error and "P27" in error for error in errors), errors)

    def test_rejects_scheduled_resource_without_arbitration(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["sharing"] == "scheduled")
        resource.pop("arbitration")
        errors = self.errors_for(candidates)
        self.assertTrue(any("scheduled resource lacks arbitration" in error for error in errors), errors)

    def test_rejects_radio_resource_made_shared(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["id"] == "NRF1_SPI")
        resource["sharing"] = "scheduled"
        resource["arbitration"] = "invalid regression fixture"
        errors = self.errors_for(candidates)
        self.assertTrue(any("exclusive resource NRF1_SPI is not dedicated" in error for error in errors), errors)

    def test_rejects_missing_required_resource_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["resource_contracts"] = [
            r for r in candidate["resource_contracts"] if r["id"] != "S3_C5_IPC"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing required resource contracts" in error and "S3_C5_IPC" in error for error in errors), errors)

    def test_rejects_controller_not_available_on_exact_device(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        candidate["controllers"]["c5"].append("IMAGINARY_SPI9")
        candidate["allocations"][32]["controller"] = "IMAGINARY_SPI9"
        errors = self.errors_for(candidates)
        self.assertTrue(any("unavailable controllers" in error and "IMAGINARY_SPI9" in error for error in errors), errors)

    def test_rejects_pio_pin_outside_selected_b_package_window(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        row = next(
            allocation
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp" and allocation["net"] == "NRF0_MISO"
        )
        power_row = next(
            allocation
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp" and allocation["net"] == "NRF_GROUP_PWR_EN"
        )
        row["contact"] = "GPIO15"
        power_row["contact"] = "GPIO30"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("NRF0" not in error and "outside GPIO16..GPIO47" in error for error in errors),
            errors,
        )

    def test_rejects_missing_shared_pio_window_selection(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["controller_gpio_windows"] = [
            window
            for window in candidate["controller_gpio_windows"]
            if "PIO0_SM0_RF_SPI" not in window["controllers"]
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("PIO0_GPIO_BASE missing GPIO-window selection" in error for error in errors),
            errors,
        )

    def test_rejects_overbooked_dma_capacity(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        capacity = next(
            item for item in candidate["capacity_contracts"] if item["id"] == "RP_DMA_CHANNELS"
        )
        capacity["claims"][0]["units"] += 1
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("14 claimed + 3 reserve != 16 available" in error for error in errors),
            errors,
        )

    def test_rejects_fixed_mux_contact_drift(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        mux = next(item for item in candidate["mux_contracts"] if item["id"] == "RP_UART1_GNSS")
        mux["contacts"][1] = "GPIO42"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("RP_UART1_GNSS" not in error and "declared contacts" in error for error in errors),
            errors,
        )

    def test_complete_local_controls_ptt_and_run_kill_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["ui_control_contract"]
        self.assertEqual("DEC-0086", contract["decision"])
        self.assertEqual(
            {
                "D-PAD UP", "D-PAD DOWN", "D-PAD LEFT", "D-PAD RIGHT", "OK",
                "BACK", "OPT", "F1", "F2", "ENCODER PUSH",
                "F3", "F4", "F5", "F6", "F7", "F8",
            },
            set(contract["ordinary_inputs"]["controls"]),
        )
        self.assertEqual(
            {
                "P00": "D-PAD UP", "P01": "D-PAD DOWN",
                "P02": "D-PAD LEFT", "P03": "D-PAD RIGHT", "P04": "OK",
                "P05": "BACK", "P06": "OPT", "P07": "F3",
                "P10": "F1", "P11": "F2", "P12": "ENCODER PUSH",
                "P13": "F4", "P14": "F5", "P15": "F6",
                "P16": "F7", "P17": "F8",
            },
            contract["ordinary_inputs"]["input_map"],
        )
        self.assertIn(
            "row drive, matrix scanning and ghost-key handling are eliminated",
            contract["ordinary_inputs"]["firmware_contract"],
        )
        self.assertIn("RP GPIO21", contract["dedicated_controls"]["ptt"])
        self.assertIn("only physical RUN/KILL control", contract["dedicated_controls"]["run_kill"])
        self.assertIn("No separate STOP or RE-ARM", contract["dedicated_controls"]["run_kill"])
        self.assertNotIn("stop", contract["dedicated_controls"])
        self.assertNotIn("rearm", contract["dedicated_controls"])

        self.assertEqual("ti_tca9539_pwr", candidate["instances"]["ui_matrix_io"])
        self.assertEqual("alps_ec11e18244au", candidate["instances"]["encoder"])
        self.assertEqual("ti_sn74lvc1g07_dckr", candidate["instances"]["touch_irq_buffer"])
        for instance in (
            "ui_dpad_up", "ui_dpad_down", "ui_dpad_left", "ui_dpad_right",
            "ui_dpad_ok",
            "ui_switch_back", "ui_switch_opt", "ui_switch_f1", "ui_switch_f2",
            "ui_switch_f3", "ui_switch_f4", "ui_switch_f5", "ui_switch_f6",
            "ui_switch_f7", "ui_switch_f8",
            "ptt_switch",
        ):
            self.assertEqual("omron_b3s_1100p", candidate["instances"][instance])
        self.assertEqual("ck_js102011scqn", candidate["instances"]["power_command_switch"])
        self.assertNotIn("stop_switch", candidate["instances"])
        self.assertNotIn("rearm_switch", candidate["instances"])
        self.assertEqual("ti_tpd8e003_dqdr", candidate["instances"]["ui_matrix_esd"])
        self.assertEqual("ti_tpd8e003_dqdr", candidate["instances"]["front_function_esd"])
        self.assertEqual("ti_tpd4e05u06_dqar", candidate["instances"]["rear_control_esd"])
        self.assertEqual("ti_tpd4e05u06_dqar", candidate["instances"]["encoder_ptt_esd"])
        self.assertEqual("ti_tpd4e05u06_dqar", candidate["instances"]["safety_control_esd"])
        self.assertEqual(
            "direct finger press; no separate cap or plunger",
            self.database["devices"]["omron_b3s_1100p"]["electrical_contract"]["user_interface"],
        )
        run_kill = self.database["devices"]["ck_js102011scqn"]
        self.assertEqual([8.5, 3.5, 3.6], run_kill["dimensions_mm"])
        self.assertIn("low-current command input only", run_kill["electrical_contract"]["use"])
        input_io = self.database["devices"]["ti_tca9539_pwr"]
        self.assertEqual("4", input_io["contacts"]["P00"]["physical"])
        self.assertEqual("1", input_io["contacts"]["INT_N"]["physical"])
        self.assertEqual(
            [
                "P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07",
                "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17",
            ],
            input_io["allocatable_contacts"],
        )
        self.assertEqual("0x74", input_io["i2c_7bit_address_by_a1a0"]["00"])
        self.assertEqual("0x77", input_io["i2c_7bit_address_by_a1a0"]["11"])
        self.assertIn("ti_sn74lvc1g06_dckr", self.database["devices"])
        self.assertEqual(
            "ti_sn74lvc1g07_dckr", candidate["instances"]["touch_irq_buffer"]
        )
        self.assertEqual(
            "sitronix_st77922", candidate["instances"]["display_touch_controller"]
        )
        self.assertEqual(
            "yageo_rc0402fr_0710kl", candidate["instances"]["touch_irq_pullup"]
        )
        st77922 = self.database["devices"]["sitronix_st77922"]
        self.assertEqual("die pad 31", st77922["contacts"]["TP_INT"]["physical"])
        self.assertEqual("0x38", st77922["assembly_contract"]["touch_i2c_7bit_address"])
        self.assertEqual(
            "active-low on the exact ES3C35P/HMX035CTFT-001 reference",
            st77922["assembly_contract"]["touch_irq"],
        )

        allocations = {
            (row["instance"], row["contact"]): row
            for row in candidate["allocations"]
        }
        self.assertEqual("PCNT0", allocations[("s3", "GPIO39")]["controller"])
        self.assertEqual("PCNT0", allocations[("s3", "GPIO47")]["controller"])
        self.assertEqual("PTT_BUTTON_N", allocations[("rp", "GPIO21")]["net"])
        self.assertEqual([], candidate["free_gpio"]["s3"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(("ui_matrix_io.P00", "ui_matrix_esd.IO1", "UI_DPAD_UP_N"), routes)
        self.assertIn(("ui_matrix_io.P04", "ui_matrix_esd.IO5", "UI_DPAD_OK_N"), routes)
        self.assertIn(("ui_matrix_io.INT_N", "abstract:SYS_INT_N_WIRED_LOW", "SYS_INT_N"), routes)
        self.assertIn(("abstract:power-ground", "ui_matrix_io.A0", "UI_INPUT_ADDR_A0_LOW"), routes)
        self.assertIn(("abstract:power-ground", "ui_matrix_io.A1", "UI_INPUT_ADDR_A1_LOW"), routes)
        self.assertIn(("s3.EN", "ui_matrix_io.RESET_N", "S3_RESET_N"), routes)
        self.assertIn(("abstract:safety-ground", "evidence_mask.A2", "EVIDENCE_ADDR_A2_LOW"), routes)
        for contact, instance, net in (
            ("P00", "ui_dpad_up", "UI_DPAD_UP_N"),
            ("P01", "ui_dpad_down", "UI_DPAD_DOWN_N"),
            ("P02", "ui_dpad_left", "UI_DPAD_LEFT_N"),
            ("P03", "ui_dpad_right", "UI_DPAD_RIGHT_N"),
            ("P04", "ui_dpad_ok", "UI_DPAD_OK_N"),
        ):
            self.assertIn((f"ui_matrix_io.{contact}", f"{instance}.SIDE_A_1", net), routes)
            self.assertIn((f"{instance}.SIDE_B_1", "abstract:power-ground", "POWER_GROUND"), routes)
        for contact, instance, net in (
            ("P07", "ui_switch_f3", "UI_F3_N"),
            ("P10", "ui_switch_f1", "UI_F1_N"),
            ("P11", "ui_switch_f2", "UI_F2_N"),
            ("P13", "ui_switch_f4", "UI_F4_N"),
            ("P14", "ui_switch_f5", "UI_F5_N"),
            ("P15", "ui_switch_f6", "UI_F6_N"),
            ("P16", "ui_switch_f7", "UI_F7_N"),
            ("P17", "ui_switch_f8", "UI_F8_N"),
        ):
            self.assertIn((f"ui_matrix_io.{contact}", f"{instance}.SIDE_A_1", net), routes)
            self.assertIn((f"{instance}.SIDE_B_1", "abstract:power-ground", "POWER_GROUND"), routes)
        self.assertIn(("ui_matrix_io.P12", "encoder.SW1", "UI_ENCODER_PUSH_N"), routes)
        self.assertIn(("ui_matrix_io.P10", "front_function_esd.IO1", "UI_F1_N"), routes)
        self.assertIn(("ui_matrix_io.P17", "front_function_esd.IO7", "UI_F8_N"), routes)
        self.assertIn(("ui_matrix_io.P12", "rear_control_esd.D1_PLUS", "UI_ENCODER_PUSH_N"), routes)
        self.assertIn(("ptt_series.END_2", "rp.GPIO21", "PTT_BUTTON_N"), routes)
        self.assertIn(("abstract:3V3_MAIN", "ptt_pullup.END_1", "3V3_MAIN"), routes)
        self.assertIn(("run_loop_pullup.END_2", "power_command_switch.THROW_A", "RUN_LOOP_RAW"), routes)
        self.assertIn(("power_command_pullup.END_2", "power_command_switch.THROW_B", "POWER_COMMAND_OFF_N"), routes)
        self.assertIn(("power_command_switch.COMMON", "abstract:power-ground", "POWER_GROUND"), routes)
        self.assertIn(("run_loop_pullup.END_2", "safety_control_esd.D1_PLUS", "RUN_LOOP_RAW"), routes)
        self.assertIn(("safe_conditioner.1Y", "safe_rearm_delay_res.END_1", "RUN_EDGE"), routes)
        self.assertIn(("safe_rearm_buffer.Y", "safe_latch.CLK", "SAFE_REARM_CLK"), routes)
        self.assertIn(("display.TP_INT", "display_touch_controller.TP_INT", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertIn(("touch_irq_pullup.END_2", "display_connector.PIN_3", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertIn(("display_connector.PIN_3", "touch_irq_buffer.A", "LCD_TOUCH_INT_RAW_N"), routes)
        self.assertEqual([], candidate["contact_accounting"]["slow_io"]["free"])
        self.assertIn("P05", candidate["contact_accounting"]["slow_io"]["used"])
        self.assertEqual({}, candidate["contact_accounting"]["ui_matrix_io"]["reserved"])
        self.assertEqual(16, len(candidate["contact_accounting"]["ui_matrix_io"]["used"]))

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "F1 ultra-low-current ordinary control", "F8 ultra-low-current ordinary control",
            "hold-to-talk PTT control", "single maintained low-current RUN/KILL switch",
            "B3S-1100P", "JS102011SCQN", "TPD8E003DQDR", "Sitronix ST77922",
            "active-low ST77922 touch node",
            'POWER_COMMAND_SWITCH -->|"RUN throw"| RUN_LOOP',
            "TCA9539PWR", "interrupt-capable 16-bit direct-control input expander",
            "independent UP navigation button",
            "independent DOWN navigation button",
            "independent LEFT navigation button",
            "independent RIGHT navigation button",
            "independent OK confirmation button",
        ):
            self.assertIn(token, rendered)
        self.assertNotIn("PTT_SWITCH --> PTT_PULLUP --> PTT_FILTER_CAP", rendered)
        self.assertNotIn("STOP_SWITCH", rendered)
        self.assertNotIn("REARM_SWITCH", rendered)
        self.assertIn("SN74LVC1G06DCKR", rendered)
        self.assertIn("SN74LVC1G07DCKR", rendered)

    def test_dec0059_restores_full_s3_c5_service_on_1bit_sdio(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        allocations = {
            (row["instance"], row["contact"]): row
            for row in candidate["allocations"]
        }

        self.assertEqual("SDMMC_SLOT1_1BIT", allocations[("s3", "GPIO10")]["controller"])
        self.assertEqual("SDIO_SLAVE", allocations[("c5", "GPIO9")]["controller"])
        self.assertEqual("S3_C5_SDIO_D1_IRQ", allocations[("s3", "GPIO13")]["net"])
        self.assertEqual("UART0", allocations[("s3", "GPIO43")]["controller"])
        self.assertEqual("S3_UART_SERVICE_RX", allocations[("s3", "GPIO44")]["net"])
        self.assertEqual("USB_SERIAL_JTAG", allocations[("c5", "GPIO13")]["controller"])
        self.assertEqual("C5_USB_DP", allocations[("c5", "GPIO14")]["net"])
        self.assertEqual("I2C1_OR_UART1_OR_GPIO", allocations[("s3", "GPIO7")]["controller"])
        self.assertEqual([], candidate["free_gpio"]["s3"])

        services = {
            item["instance"]: set(item["contacts"])
            for item in candidate["services"]
        }
        self.assertTrue({"GPIO19", "GPIO20", "GPIO43", "GPIO44"} <= services["s3"])
        self.assertTrue({"GPIO11", "GPIO12", "GPIO13", "GPIO14"} <= services["c5"])

        muxes = {item["id"]: item for item in candidate["mux_contracts"]}
        self.assertEqual(["GPIO7", "GPIO8", "GPIO9", "GPIO10"], muxes["C5_FIXED_SDIO"]["contacts"])
        self.assertEqual(["GPIO13", "GPIO14"], muxes["C5_NATIVE_USB"]["contacts"])
        self.assertEqual(["GPIO43", "GPIO44"], muxes["S3_UART0_SERVICE"]["contacts"])

        ipc = next(
            item for item in candidate["resource_contracts"]
            if item["id"] == "S3_C5_IPC"
        )
        self.assertIn("1-bit SDIO at 20 MHz raw 2.5 MB/s", ipc["deadline"])
        self.assertIn("eFuse revision v1.2 or later", ipc["proof_gate"])
        self.assertIn("C54951858", ipc["proof_gate"])
        self.assertIn("4-bit fallback only if this gate fails", ipc["proof_gate"])

        c5 = self.database["devices"]["esp32_c5_wroom_1u_n8r8"]
        self.assertIn(
            "revision v1.2 or later",
            c5["controller_notes"]["SDIO_SILICON_FLOOR"],
        )
        self.assertEqual("v1.2", c5["silicon_revision_requirement"]["production_minimum"])
        self.assertEqual("v1.0", c5["silicon_revision_requirement"]["engineering_only"])
        self.assertEqual(["v0.1", "unknown"], c5["silicon_revision_requirement"]["rejected"])
        self.assertIn("MD/lot identity", c5["silicon_revision_requirement"]["incoming_inspection"])
        self.assertIn(
            "docs.espressif.com",
            c5["silicon_revision_requirement"]["source"]["url"],
        )

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("1-bit SDIO: S3 GPIO10,GPIO11,GPIO12,GPIO13", rendered)
        self.assertNotIn("4-bit SDIO: S3", rendered)

    def test_c5_procurement_identity_is_single_and_fail_closed(self):
        invariant = json.loads(
            (GENERATOR.REPO_ROOT / "hardware/architecture/c5-procurement-invariant.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("C5-PROCUREMENT-IDENTITY-1", invariant["invariant_id"])
        self.assertEqual(
            "ESP32-C5-WROOM-1U-N8R8", invariant["official_identity"]["mpn"]
        )
        route = invariant["active_supplier_route"]
        self.assertEqual("Espressif Systems", route["manufacturer"])
        self.assertEqual("C54951858", route["jlcpcb_part_number"])
        self.assertEqual("ESP32-C5-WROOM-1U-N8R8-V1.2", route["supplier_order_code"])
        self.assertEqual("Standard PCBA", route["pcba_surface"])
        self.assertEqual((460, 440, 1), (route["stock"], route["available_order_quantity"], route["moq"]))
        policy = invariant["silicon_revision_policy"]
        self.assertEqual("v1.2", policy["production_floor"])
        self.assertEqual(["v1.0"], policy["engineering_only"])
        self.assertEqual(["v0.1", "unknown"], policy["rejected"])
        self.assertEqual(
            {"MD_IDENTITY", "EFUSE_SILICON_REVISION"},
            {row["id"] for row in invariant["incoming_inspection"]["checks"]},
        )
        self.assertEqual(
            ["C51950748"],
            [row["jlcpcb_part_number"] for row in invariant["forbidden_active_routes"]],
        )

    def test_i7_exact_three_domain_service_recovery_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["service_recovery_contract"]
        self.assertEqual("DEC-0099", contract["decision"])
        self.assertIn("paper_reviewed_i7", contract["status"])
        self.assertIn("FSUSB42MUX", contract["usb"])
        self.assertIn("00 S3, 01 C5 and 10 RP", contract["debug"])
        self.assertIn("never fight a push-pull source", contract["reset"])

        required_instances = {
            "c5_service_usb_connector": "gct_usb4105_gf_a",
            "rp_service_usb_connector": "gct_usb4105_gf_a",
            "c5_service_usb_switch": "onsemi_fsusb42_mux",
            "rp_service_usb_switch": "onsemi_fsusb42_mux",
            "s3_dbg_header": "samtec_ftsh_105_01_l_dv_k_p_tr",
            "c5_dbg_header": "samtec_ftsh_105_01_l_dv_k_p_tr",
            "rp_dbg_header": "samtec_ftsh_105_01_l_dv_k_p_tr",
            "s3_reset_button": "alps_skrtlae010",
            "s3_boot_button": "alps_skrtlae010",
            "c5_reset_button": "alps_skrtlae010",
            "c5_boot_button": "alps_skrtlae010",
            "rp_reset_button": "alps_skrtlae010",
            "rp_boot_button": "alps_skrtlae010",
            "safe_reset_buffer": "ti_sn74lvc1g06_dckr",
            "safe_reset_sink_a": "diodes_2n7002dw_7_f",
            "safe_reset_sink_b": "diodes_2n7002dw_7_f",
        }
        for instance, device_id in required_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (row["from"], row["to"], row["net"])
            for row in candidate["fixed_routes"]
        }
        for route in (
            ("c5_service_usb_switch.HSD1_PLUS", "c5_service_usb_dp_series.END_1", "C5_SERVICE_USB_DP_SWITCHED"),
            ("rp_service_usb_switch.HSD1_PLUS", "rp_service_usb_dp_series.END_1", "RP_SERVICE_USB_DP_SWITCHED"),
            ("s3_dbg_reset_series.END_2", "s3.EN", "S3_RESET_N"),
            ("c5_dbg_boot_series.END_2", "c5.GPIO28", "C5_BOOT_N"),
            ("rp_dbg_boot_series.END_2", "rp.QSPI_SS_USB_BOOT", "RP_USB_BOOT_N"),
            ("safe_latch.Q", "safe_reset_buffer.A", "RUN_PERMIT"),
            ("safe_reset_sink_a.D1", "s3.EN", "S3_RESET_N"),
            ("safe_reset_sink_a.D2", "c5.EN", "C5_RESET_N"),
            ("safe_reset_sink_b.D1", "rp.RUN", "RP_RESET_N"),
        ):
            self.assertIn(route, routes)

        for domain in ("c5", "rp"):
            connector = f"{domain}_service_usb_connector"
            vbus_routes = [
                row for row in candidate["fixed_routes"]
                if row["from"].startswith(f"{connector}.")
                and "VBUS" in row["from"]
            ]
            serialized = " ".join(str(row) for row in vbus_routes)
            self.assertNotIn("3V3", serialized)
            self.assertNotIn("charger", serialized.lower())
            self.assertIn("vbus_bleeder", serialized)

        self.assertNotEqual(
            "ti_sn74lvc3g34_dcur", candidate["instances"]["safe_reset_buffer"]
        )
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "GCT USB4105-GF-A",
            "Samtec FTSH-105-01-L-DV-K-P-TR",
            "Alps Alpine SKRTLAE010",
            "onsemi FSUSB42MUX",
            "SN74LVC1G06DCKR",
            "2N7002DW-7-F",
        ):
            self.assertIn(token, rendered)

    def test_exact_main_slow_io_and_i4_closure_do_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["slow_io_contract"]
        device = self.database["devices"][candidate["instances"]["slow_io"]]

        self.assertEqual("DEC-0089", contract["decision"])
        self.assertEqual("0x22", device["electrical_contract"]["selected_address"])
        self.assertEqual(400, device["electrical_contract"]["maximum_i2c_khz"])
        self.assertEqual("verified_exact_main_slow_io_core", device["qualification"])
        self.assertIn("below 0.2 V", contract["reset"])
        self.assertIn("0x2A", contract["pack_system_target"])
        self.assertIn("FPC is service-only", contract["interface_boundary"])
        self.assertIn("0x2A", candidate["power_contract"]["pack_system_i2c_target"])

        expected_instances = {
            "slow_io_vcci_bypass": "yageo_cc0402krx7r9bb104",
            "slow_io_vccp_bypass": "yageo_cc0402krx7r9bb104",
            "slow_io_bulk_cap": "tdk_c1608x7r1c105k080ac",
            "slow_io_reset_pullup": "yageo_rc0402fr_0710kl",
            "slow_io_fault_sense_iso": "ti_sn74lvc1g07_dckr",
            "slow_io_fault_sense_pullup": "yageo_rc0402fr_0710kl",
            "slow_io_s3_evidence_iso": "ti_sn74lvc1g07_dckr",
            "slow_io_s3_evidence_pullup": "yageo_rc0402fr_0710kl",
            "fault_led_series": "uniroyal_0402wgf2201tce",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("abstract:3V3_MAIN", "slow_io.VCCI", "3V3_MAIN"),
            ("abstract:3V3_MAIN", "slow_io.VCCP", "3V3_MAIN"),
            ("slow_io.ADDR", "abstract:power-ground", "SLOW_IO_ADDR_LOW"),
            ("slow_io_reset_pullup.END_2", "slow_io.RESET", "SLOW_IO_RESET_N"),
            ("slow_io.RESET", "abstract:TP_SLOW_IO_RESET_N", "SLOW_IO_RESET_N"),
            ("slow_io.SCL", "s3.GPIO2", "SYS_I2C_SCL"),
            ("slow_io.SDA", "s3.GPIO1", "SYS_I2C_SDA"),
            ("slow_io.INT", "s3.GPIO45", "SYS_INT_N"),
            ("safe_latch.Q_N", "slow_io_fault_sense_iso.A", "FAULT_LATCH_SENSE_AON"),
            ("slow_io_fault_sense_iso.Y", "slow_io.P22", "FAULT_LATCH_SENSE"),
            ("evidence_cmp_a.OUT1", "slow_io_s3_evidence_iso.A", "EV_N0_S3"),
            ("slow_io_s3_evidence_iso.Y", "slow_io.P23", "S3_RF_TX_EVIDENCE_N"),
            ("sd_miso_series.END_2", "s3.GPIO4", "DISPLAY_SD_SPI_D1"),
            ("product_usb_connector.SHIELD", "abstract:power-ground", "USB_C_SHIELD"),
            ("safe_latch.Q_N", "fault_led_series.END_1", "FAULT_LATCH_SENSE_AON"),
            ("fault_led_series.END_2", "fault_led.A", "FAULT_LED_A"),
        ):
            self.assertIn(route, routes)
        encoder_allocations = {
            row["net"]: set(row["peers"])
            for row in candidate["allocations"]
            if row["net"] in {"ENCODER_A", "ENCODER_B"}
        }
        self.assertIn("encoder_a_pullup.END_2", encoder_allocations["ENCODER_A"])
        self.assertIn("encoder_b_pullup.END_2", encoder_allocations["ENCODER_B"])
        self.assertNotIn("encoder_a_pullup.END_1", encoder_allocations["ENCODER_A"])
        self.assertNotIn("encoder_b_pullup.END_1", encoder_allocations["ENCODER_B"])
        for instance in (
            "ui_dpad_up", "ui_dpad_down", "ui_dpad_left", "ui_dpad_right", "ui_dpad_ok"
        ):
            self.assertIn(
                (f"{instance}.GROUND", "abstract:power-ground", "POWER_GROUND"),
                routes,
            )
        self.assertNotIn(("safe_latch.Q", "slow_io.P22", "FAULT_LATCH_SENSE"), routes)
        self.assertNotIn(("evidence_cmp_a.OUT1", "slow_io.P23", "S3_RF_TX_EVIDENCE_N"), routes)

        internal_bus = next(
            resource
            for resource in candidate["resource_contracts"]
            if resource["id"] == "S3_INTERNAL_I2C"
        )
        for address in ("0x20", "0x22", "0x2A", "0x2B", "0x38", "0x74"):
            self.assertIn(address, internal_bus["proof_gate"])
        self.assertIn("safety_controller", internal_bus["clients"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for token in (
            "main slow-I/O VCCI bypass capacitor",
            "AON-powered open-drain FAULT-sense domain isolator",
            "AON-powered open-drain S3-evidence domain isolator",
            "physical FAULT-indicator current limit",
            "SLOW_IO_RESET_N",
        ):
            self.assertIn(token, rendered)

        for token in (
            "Yageo CC0402KRX7R9BB104<br/>100-nF main slow-I/O VCCI bypass capacitor",
            "TDK C1608X7R1C105K080AC<br/>1-uF main slow-I/O local bulk capacitor",
            "SN74LVC1G07DCKR<br/>AON-powered open-drain FAULT-sense domain isolator",
            "SN74LVC1G07DCKR<br/>AON-powered open-drain S3-evidence domain isolator",
            "UNI-ROYAL 0402WGF2201TCE<br/>2.2-kOhm physical FAULT-indicator current limit",
        ):
            self.assertIn(token, rendered, token)

    def test_rejects_missing_required_mux_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["mux_contracts"] = [
            mux for mux in candidate["mux_contracts"] if mux["id"] != "C5_FIXED_SDIO"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("missing required mux contracts" in error and "C5_FIXED_SDIO" in error for error in errors),
            errors,
        )

    def test_rejects_full_mix_that_allows_peer_standby(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["peer_standby_forbidden"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("full mix must forbid peer standby" in error for error in errors),
            errors,
        )

    def test_rejects_missing_required_quiet_state_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["quiet_state_policy"]["contracts"] = [
            contract
            for contract in candidate["quiet_state_policy"]["contracts"]
            if contract["id"] != "N24_QUIET"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("missing required quiet-state contracts" in error and "N24_QUIET" in error for error in errors),
            errors,
        )

    def test_rejects_full_mix_without_observer_hil(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["rf_acceptance"]["external_observer_fixture"] = ""
        group["rf_acceptance"]["hil_required"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("full mix RF acceptance missing external_observer_fixture" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("full mix RF acceptance must require HIL" in error for error in errors),
            errors,
        )

    def test_rejects_div_pre_hil_as_production_acceptance(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["rf_acceptance"]["fixture_levels"] = ["L0_DIV_DIV_PRE_HIL"]
        group["rf_acceptance"]["production_acceptance_level"] = "L0_DIV_DIV_PRE_HIL"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("must separate L0 DIV pre-HIL from T1 target HIL" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("production RF acceptance must require T1_TARGET" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
