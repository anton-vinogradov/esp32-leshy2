import importlib.util
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_r2_layout.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_layout", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2LayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(MODULE.MODEL_PATH.read_text())
        cls.base = json.loads(MODULE.BASE_PATH.read_text())
        cls.audit = MODULE.audit(cls.model, cls.base)
        source_table = json.loads(MODULE.SOURCE_TABLE_PATH.read_text())
        complete_rows = MODULE.complete_inner_rows(
            cls.model, cls.base, source_table, cls.audit
        )
        antenna_topology = MODULE.r2_antenna_topology(cls.model, complete_rows)
        cls.audit["antenna_topology"] = antenna_topology
        cls.audit["rf_microcoax"] = MODULE.r2_microcoax_audit(
            cls.model, complete_rows, antenna_topology
        )
        cls.audit["errors"].extend(cls.audit["rf_microcoax"]["errors"])
        if cls.audit["errors"]:
            cls.audit["status"] = "fail"

    def test_incremental_placement_passes(self):
        self.assertEqual("H1-R2.39", self.model["marker"])
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual("pass", self.audit["structural_status"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual([], self.audit["same_face_collisions"])
        self.assertEqual(88, len(self.audit["opposing_overlaps"]))
        self.assertEqual(
            [{"ui": "m1_ui_plug", "rf": "m1_rf_receptacle", "overlap_mm": 3.8}],
            self.audit["intentional_opposing_mates"],
        )
        self.assertGreaterEqual(
            self.audit["minimum_opposing_clearance_mm"],
            self.audit["required_opposing_clearance_mm"],
        )

    def test_display_mount_is_s3_only_and_names_physical_retention(self):
        legacy = MODULE.legacy_generator()
        design = json.loads(legacy.DISPLAY_MOUNT_DESIGN_PATH.read_text())
        self.assertEqual(
            {
                "display_bus_owner": "s3",
                "touch_host_owner": "s3",
                "c5_display_or_touch_connection": "none",
            },
            design["electrical"]["owner_contract"],
        )
        svg = legacy.render_display_mount(design)
        self.assertNotIn('data-route="display-to-owner"', svg)
        self.assertNotIn('data-owner="C5"', svg)
        self.assertIn('data-mechanical-part="display_psa_rectangle"', svg)
        self.assertIn('data-mechanical-part="ui_pcb_display_bed"', svg)
        self.assertNotIn('data-mechanical-part="front_shell_corner_locators"', svg)
        self.assertNotIn("closed-cell foam preload", svg)
        self.assertIn("FPC FREE ZONE", svg)
        self.assertIn('data-fpc-route="single-fold-relaxed-loop-internal-slot-zif"', svg)
        self.assertIn('data-slack="relaxed"', svg)
        self.assertIn("One 180° fold, no twist", svg)
        self.assertIn("rounded 27.0 × 1.2-mm slot", svg)
        self.assertIn("PSA pressing comes last", svg)
        self.assertIn("3M 4910SQ-2(5)", svg)
        self.assertIn("folded-FPC stack ≤0.714 mm", svg)
        self.assertEqual(design["orientation"]["fpc_exit_direction_board_axis"], "-Y")
        route = design["mechanical_retention"]["fpc_route_side_section"]
        self.assertEqual([50.8, 50.8], route["stock_psa_rectangle_size_mm"])
        self.assertEqual([14.6, 44.46], route["stock_psa_rectangle_position_mm"])
        self.assertFalse(route["tail_under_psa"])
        self.assertFalse(route["tail_bears_on_bare_pcb_edge"])
        self.assertFalse(route["hard_crease_allowed"])
        self.assertIsNone(route["minimum_bend_radius_mm"])
        div_reference = design["mechanical_retention"]["esp32_div_v2_reference"]
        self.assertEqual(div_reference["retention_evidence_status"], "unknown_from_public_sources")
        self.assertIn("four empty 1.2-mm holes", div_reference["in_plane_location"])
        self.assertIn("18-contact", div_reference["electrical_connection"])
        self.assertIn("exact stock display PSA and folded FPC", svg)

    def test_every_fixed_body_has_exact_mpn(self):
        for item in self.model["placements"]:
            if item["kind"] == "fixed_body":
                self.assertTrue(item["mpn"], item["id"])

    def test_every_onboard_tx_path_has_a_physical_detector_island(self):
        register = self.audit["tx_evidence_physical_register"]
        self.assertEqual("pass", register["status"])
        self.assertEqual(8, register["detector_count"])
        self.assertEqual(5, register["coupler_count"])
        self.assertEqual(8, register["local_island_count"])
        self.assertEqual("adi_ad8314armz_reel", register["selected_detector_device_id"])
        self.assertEqual("C652687", register["selected_detector_factory_route"]["jlcpcb_part"])
        self.assertEqual(13, len(register["fixed_bodies"]))
        self.assertEqual(8, len(register["local_islands"]))
        self.assertTrue(all(
            row["minimum_compression_stop_clearance_mm"] >= 0.7
            for row in register["local_islands"]
        ))

        broken = copy.deepcopy(self.model)
        broken["placements"] = [
            row for row in broken["placements"] if row["id"] != "det_nrf1_r2"
        ]
        failed = MODULE.audit(broken, self.base)
        self.assertIn(
            "R2 TX-evidence detector/coupler scope is incomplete or contains an unregistered body",
            failed["errors"],
        )

    def test_physical_gpio_budgets_are_bound_to_exact_dual_rp_authority(self):
        self.assertEqual({"used": 46, "free": 2}, self.model["functional_partition"]["front_rp_gpio"])
        self.assertEqual({"used": 43, "free": 5}, self.model["functional_partition"]["rear_rp_gpio"])
        broken = copy.deepcopy(self.model)
        broken["functional_partition"]["rear_rp_gpio"] = {"used": 45, "free": 3}
        failed = MODULE.audit(broken, self.base)
        self.assertIn(
            "rear_rp_gpio: physical model GPIO budget differs from exact dual-RP authority",
            failed["errors"],
        )

    def test_every_drawn_item_has_one_unique_compact_reference(self):
        refs = [item["drawing_ref"] for item in self.model["placements"]]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertTrue(all(len(ref) <= 2 for ref in refs))
        self.assertEqual(len(refs), self.audit["placement_drawing_reference_count"])
        self.assertEqual({}, self.audit["duplicate_placement_drawing_references"])

    def test_onboard_video_bodies_and_reserves_are_absent(self):
        names = " ".join(
            [str(row.get("id", "")) + " " + str(row.get("mpn", "")) for row in self.model["placements"]]
        ).lower()
        for token in ("fpv", "k331", "awm666", "tvp5150", "mmcx"):
            self.assertNotIn(token, names)
        self.assertEqual([], self.model["trace_corridors"])

    def test_h1_blockers_are_separate_from_dependent_and_later_work(self):
        self.assertEqual([], self.model["current_h1_blockers"])
        self.assertEqual(
            len(self.model["current_h1_blockers"]),
            len(self.model["current_h1_blockers_ru"]),
        )
        self.assertEqual([], self.model["pre_r2_h2_gates"])
        self.assertEqual([], self.model["pre_r2_h2_gates_ru"])
        self.assertEqual("reviewed", self.model["status"])
        self.assertEqual([], self.model["dependent_h1_work"])
        self.assertEqual("2026-09-05", self.model["reviewed_on"])
        self.assertEqual(
            {"H5/H6 then H7"},
            {row["stage"] for row in self.model["downstream_verification"]},
        )
        self.assertEqual(self.model["current_h1_blockers"], self.audit["current_h1_blockers"])
        self.assertEqual(self.model["dependent_h1_work"], self.audit["dependent_h1_work"])

    def test_base_cap_evidence_register_is_exact_complete_and_fail_closed(self):
        register = self.audit["cap_evidence_coordinate_register"]
        self.assertEqual("pass", register["status"])
        self.assertEqual(43, register["expected_instance_count"])
        self.assertEqual(43, register["resolved_instance_count"])
        self.assertEqual(43, len(register["instances"]))
        self.assertTrue(all(row["placement_courtyard_bbox_mm"] for row in register["instances"]))

        broken = copy.deepcopy(self.base)
        broken["cap_evidence_coordinate_register"]["instances"][0]["device_key"] = "wrong-device"
        failed = MODULE.audit(self.model, broken)
        self.assertIn(
            "base Cap/evidence coordinate register differs from current exact G2F",
            failed["errors"],
        )

        broken = copy.deepcopy(self.base)
        broken["cap_evidence_coordinate_register"]["instances"].pop()
        failed = MODULE.audit(self.model, broken)
        self.assertIn(
            "base Cap/evidence coordinate register differs from current exact G2F",
            failed["errors"],
        )

    def test_u219_cap_profile_and_only_source_proven_host_bodies_are_registered(self):
        slot = self.audit["cap_bus_slot"]
        self.assertEqual("pass", slot["status"])
        self.assertEqual("exactly_one", slot["population"])
        self.assertEqual([84.0, 24.0, 15.287], slot["profiles"]["u214"]["envelope_mm"])
        self.assertEqual([84.0, 24.0, 19.7], slot["profiles"]["u219"]["envelope_mm"])
        self.assertAlmostEqual(4.413, slot["u219_height_delta_vs_u214_mm"])
        self.assertAlmostEqual(1.0, slot["u219_margin_below_battery_holder_top_mm"])
        self.assertAlmostEqual(1.3, slot["u219_margin_below_current_rear_max_mm"])
        self.assertEqual(
            {
                "battery_pad_span": 1.0,
                "battery_holder_body": 5.47,
                "encoder_knob": 2.0,
                "main_antenna_body_strip": 11.0,
            },
            slot["calculated_clearances_mm"],
        )
        expected = {
            "u219_pin10_switch": "SN74CBTLV1G125DCKR",
            "u219_pin10_oe_driver": "SN74LVC1G06DCKR",
            "u219_field_bridge_a": "BAT54S,215",
            "u219_field_bridge_b": "BAT54S,215",
            "u219_field_comparator": "LMV331IDBVR",
            "u219_pin10_oe_pullup": "0402WGF1002TCE",
            "u219_pin10_command_pulldown": "0402WGF1002TCE",
            "u219_pin10_switch_bypass": "Yageo CC0402KRX7R9BB104",
            "u219_pin10_driver_bypass": "Yageo CC0402KRX7R9BB104",
            "u219_field_input_r_p": "0402WGF1001TCE",
            "u219_field_input_r_n": "0402WGF1001TCE",
            "u219_field_env_cap": "Murata GRM155R71H103KA88D",
            "u219_field_discharge": "0402WGF1003TCE",
            "u219_field_threshold_top": "0402WGF1003TCE",
            "u219_field_threshold_bottom": "0402WGF1002TCE",
            "u219_field_hysteresis": "0402WGF1004TCE",
            "u219_field_output_pullup": "0402WGF1002TCE",
            "u219_field_comparator_bypass": "Yageo CC0402KRX7R9BB104",
        }
        placed = {row["id"]: row for row in self.model["placements"]}
        self.assertEqual(set(expected), set(self.audit["u219_contract"]["fixed_body_instances"]))
        self.assertEqual(set(expected), set(self.audit["u219_contract"]["source_backed_courtyard_instances"]))
        for instance, mpn in expected.items():
            self.assertEqual(mpn, placed[instance]["mpn"])
            self.assertIsNotNone(placed[instance]["courtyard_xy_mm"])
            self.assertIn("source-backed H1 fit evidence", placed[instance]["courtyard_status"])

        self.assertEqual([2.4, 2.15, 1.1], placed["u219_pin10_switch"]["size_mm"])
        self.assertEqual([2.4, 2.15, 1.1], placed["u219_pin10_oe_driver"]["size_mm"])
        self.assertEqual([3.0, 2.5, 1.1], placed["u219_field_bridge_a"]["size_mm"])
        self.assertEqual([3.0, 2.5, 1.1], placed["u219_field_bridge_b"]["size_mm"])
        self.assertEqual([3.05, 3.0, 1.45], placed["u219_field_comparator"]["size_mm"])

    def test_u219_source_backed_courtyard_overlap_is_rejected(self):
        broken = copy.deepcopy(self.model)
        driver = next(row for row in broken["placements"] if row["id"] == "u219_pin10_oe_driver")
        driver["courtyard_world_bbox_mm"] = {"x": [41.8, 44.7], "y": [21.5, 24.15]}
        failed = MODULE.audit(broken, self.base)
        self.assertEqual("fail", failed["structural_status"])
        self.assertTrue(any("U219 courtyards overlap" in row for row in failed["errors"]))

    def test_non_component_geometry_is_typed_and_complete(self):
        physical = self.audit["physical_features"]
        self.assertEqual("pass", physical["status"])
        by_id = {row["id"]: row for row in physical["features"]}
        self.assertEqual("keepout", by_id["cap_socket_pth_keepout"]["kind"])
        self.assertEqual("placement_reserve", by_id["u219_pin10_island_reserve"]["kind"])
        self.assertEqual("placement_reserve", by_id["u219_nfc_evidence_island_reserve"]["kind"])
        self.assertEqual("copper_feature_reserve", by_id["u219_nfc_pickup_loop"]["kind"])
        self.assertEqual({"x": [4.0, 76.0], "y": [17.8, 40.2]}, by_id["u219_nfc_pickup_loop"]["world_bbox_mm"])
        self.assertEqual([], physical["unresolved_geometry"])
        self.assertEqual("external_swept_volume", by_id["u219_installed_antenna_sweep"]["kind"])
        self.assertGreaterEqual(by_id["cap_socket_pth_keepout"]["minimum_clearance_mm"], 0.7)

    def test_no_video_connector_occupies_the_rear_outer_plane(self):
        external = [row for row in self.model["placements"] if row["frame"] == "rf-outer-face"]
        self.assertFalse(any("video" in row["role"].lower() for row in external))

    def test_unified_opposing_audit_catches_a_new_to_new_violation(self):
        broken = copy.deepcopy(self.model)
        comparator = next(row for row in broken["placements"] if row["id"] == "u219_field_comparator")
        header = next(row for row in broken["placements"] if row["id"] == "c5_dbg_header_r2")
        comparator["world_xy_mm"] = header["world_xy_mm"]
        comparator["size_mm"][2] = 10.5
        failed = MODULE.audit(broken, self.base)
        self.assertEqual("fail", failed["structural_status"])
        self.assertTrue(any("opposing clearance c5_dbg_header_r2 / u219_field_comparator" in row for row in failed["errors"]))

    def test_c5_dbg10_is_relocated_with_direct_service_access(self):
        header = next(x for x in self.model["placements"] if x["id"] == "c5_dbg_header_r2")
        self.assertEqual(["c5_dbg_header"], header["replaces"])
        self.assertEqual([15.5, 104.0], header["world_xy_mm"])
        self.assertEqual("FTSH-105-01-L-DV-K-P-TR", header["mpn"])
        self.assertEqual("c5_dbg_header_r2", self.audit["relocated_c5_dbg_header"])
        self.assertGreaterEqual(
            self.audit["minimum_opposing_clearance_mm"],
            self.audit["required_opposing_clearance_mm"],
        )

    def test_factory_rows_include_current_identity(self):
        by_mpn = {row["mpn"]: row for row in self.model["factory_evidence"]}
        self.assertEqual("C39843328", by_mpn["SC1512-A4"]["jlcpcb_part"])
        self.assertEqual(2, by_mpn["SC1512-A4"]["quantity_per_device"])
        self.assertEqual(10, by_mpn["SC1512-A4"]["evt5_quantity"])
        self.assertIn("A4", by_mpn["SC1512-A4"]["identity_gate"])
        self.assertTrue(all("accepted" in row for row in self.model["factory_evidence"]))
        for removed in ("TVP5150AM1PBS", "73415-2063", "K331", "TPS7A2018PDBVR"):
            self.assertNotIn(removed, by_mpn)

    def test_hub_has_a_fourth_independent_recovery_set(self):
        placed = {row["id"]: row for row in self.model["placements"]}
        self.assertEqual("USB4105-GF-A", placed["hub_service_usb_connector"]["mpn"])
        self.assertEqual("FTSH-105-01-L-DV-K-P-TR", placed["hub_dbg_header"]["mpn"])
        self.assertEqual("SKRTLAE010", placed["hub_reset_button"]["mpn"])
        self.assertEqual("SKRTLAE010", placed["hub_boot_button"]["mpn"])
        self.assertEqual("bottom", placed["hub_service_usb_connector"]["external_interface"]["side"])
        self.assertEqual([12.0, 142.65], placed["hub_service_usb_connector"]["world_xy_mm"])
        self.assertEqual("right", placed["hub_reset_button"]["external_interface"]["side"])
        self.assertEqual("right", placed["hub_boot_button"]["external_interface"]["side"])

        evidence = {row["mpn"]: row for row in self.model["factory_evidence"]}
        self.assertEqual("C3020560", evidence["USB4105-GF-A"]["jlcpcb_part"])
        self.assertEqual("C110293", evidence["SKRTLAE010"]["jlcpcb_part"])
        self.assertEqual("C2932107", evidence["FTSH-105-01-L-DV-K-P-TR"]["jlcpcb_part"])
        for mpn in ("USB4105-GF-A", "SKRTLAE010", "FTSH-105-01-L-DV-K-P-TR"):
            self.assertTrue(evidence[mpn]["accepted"])
            self.assertEqual("2026-08-27", evidence[mpn]["checked"])

    def test_hub_role_keeps_audio_and_broadcast_on_rear_rp(self):
        hub = next(row for row in self.model["placements"] if row["id"] == "hub_rp")
        self.assertIn("S3/C5/rear-RP fan-out", hub["role"])
        self.assertIn("three independent nRF24", hub["role"])
        self.assertIn("microSD", hub["role"])
        self.assertNotIn("audio", hub["role"].lower())
        self.assertNotIn("broadcast", hub["role"].lower())

    def test_main_sma_rows_are_even_and_no_secondary_video_port_exists(self):
        rear = self.model["antenna_bank_optimization"]["rear_x_centres_mm"]
        self.assertEqual([10.6, 25.3, 40.0, 54.7, 69.4], rear)
        self.assertEqual(
            self.model["antenna_bank_optimization"]["front_x_centres_mm"], rear
        )
        self.assertFalse(self.model["antenna_bank_optimization"]["separate_rear_face_video_connector"])

    def test_main_sma_mounts_straddle_and_solder_to_both_pcb_faces(self):
        mounting = self.audit["main_sma_mounting"]
        self.assertEqual("GCT RFPC-SMA31-FN-175-A", mounting["standard_mpn"])
        self.assertEqual("GCT RFPC-SMA32-FN-175-A", mounting["reverse_mpn"])
        self.assertEqual(1.6, mounting["pcb_thickness_mm"])
        self.assertEqual(0.0, mounting["board_edge_y_mm"])
        self.assertEqual(1.75, mounting["body_gap_mm"]["nominal"])
        self.assertEqual([0.0, -1.65], mounting["component_face_lands"][0]["centre_xy_mm"])
        self.assertEqual([1.87, 3.3], mounting["component_face_lands"][0]["size_mm"])
        self.assertEqual(
            [[-2.55, -1.65], [2.55, -1.65]],
            [row["centre_xy_mm"] for row in mounting["opposite_face_lands"]],
        )
        self.assertIn("both PCB faces", mounting["mechanical_principle"])
        self.assertIn("one PCB face", mounting["substitution_rule"])
        self.assertEqual({"H5", "H7", "H8"}, set(mounting["verification_gates"]))
        self.assertIn("factory DFM acceptance", mounting["assembly_process_gate"]["factory_route"])
        self.assertIn("owner post-PCBA soldering is forbidden", mounting["assembly_process_gate"]["fallback_route"])
        self.assertNotIn("drop_profile", mounting)
        hobby = mounting["hobby_grade_preorder_verification"]
        self.assertIn("no drop", hobby["scope"])
        self.assertIn("prescribed mating-cycle count", hobby["scope"])
        self.assertIn("design-analysis input", hobby["design_analysis_inputs"])
        self.assertIn("strain relief", hobby["structural_requirements"])
        self.assertIn("continuity", hobby["checks"])
        for name in ("RFPC-SMA31-FN-175-A", "RFPC-SMA32-FN-175-A"):
            footprint = (REPO / f"hardware/ecad/libraries/Leshy2.pretty/{name}.kicad_mod").read_text()
            self.assertIn('(pad "1" smd rect (at 0.000 -1.650) (size 1.870 3.300)', footprint)
            self.assertIn('(pad "2" smd rect (at -2.550 -1.650) (size 1.600 3.300)', footprint)
            self.assertIn('(pad "5" smd rect (at 2.550 -1.650) (size 1.600 3.300)', footprint)
            self.assertNotIn("roundrect_rratio", footprint)
            self.assertIn('(fp_rect (start -4.500 -2.800) (end 4.500 12.400)', footprint)
            self.assertIn('(fp_rect (start -4.850 -3.150) (end 4.850 12.750)', footprint)

    def test_cheaper_through_hole_sma_pair_is_not_a_drop_in_replacement(self):
        candidate = self.audit["through_hole_sma_candidate"]
        self.assertEqual(
            "rejected_current_5_plus_5_mechanical_envelope_and_factory_route",
            candidate["status"],
        )
        self.assertEqual(["C914554", "C914553"], candidate["jlcpcb_parts"])
        self.assertEqual([9.7, 9.7], candidate["outer_face_body_plan_mm"])
        self.assertEqual([5.08, 5.08], candidate["pin_pattern"]["ground_pitch_xy_mm"])
        self.assertEqual(4, len(candidate["body_mounting_hits"]))
        self.assertGreaterEqual(len(candidate["inner_pin_keepout_hits"]), 5)
        self.assertIn("retain GCT", candidate["selection_result"])

    def test_outer_antenna_silkscreen_is_not_hidden(self):
        self.assertEqual("pass", self.audit["silkscreen"]["status"])
        self.assertEqual([], self.audit["silkscreen"]["errors"])
        self.assertEqual(5, len(self.audit["silkscreen"]["faces"]["front"]))
        self.assertEqual(5, len(self.audit["silkscreen"]["faces"]["rear"]))

    def test_board_identity_is_stable_silkscreen_not_the_work_marker(self):
        identity = self.model["hardware_identification"]
        self.assertFalse(identity["documentation_marker_printed"])
        self.assertEqual("R2", identity["design_generation"])
        self.assertEqual("EVT1", identity["prototype_stage"])
        self.assertEqual(2, len(self.audit["silkscreen"]["identity"]["front"]))
        self.assertEqual(3, len(self.audit["silkscreen"]["identity"]["rear"]))
        all_text = [
            row["text"]
            for face in identity["silkscreen"].values()
            for row in face
        ]
        self.assertIn("ESP32-LESHY2 · UI PCB · R2-EVT1 · REV A", all_text)
        self.assertIn("RF/PWR PCB · R2-EVT1 · REV A", all_text)
        self.assertTrue(all(self.model["marker"] not in row for row in all_text))

    def test_m1_and_battery_holder_have_independent_mechanical_load_paths(self):
        retention = self.audit["mechanical_retention"]
        holder = self.audit["battery_holder_mechanics"]
        self.assertEqual(4, retention["compression_stops"]["count"])
        self.assertEqual(11.0, retention["compression_stops"]["exact_working_length_mm"])
        self.assertGreaterEqual(retention["anti_shear_datums_min"], 2)
        self.assertEqual("SMT", holder["mounting"])
        self.assertEqual(77.06, holder["manufacturer_body_mm"][0])
        self.assertEqual(86.0, holder["pcb_pad_span_mm"][0])
        self.assertIn("no drop", retention["h5_proof"])
        self.assertIn("no artificial ageing", holder["h5_proof"])

    def test_r2_antenna_topology_distinguishes_every_physical_medium(self):
        source_table = json.loads(MODULE.SOURCE_TABLE_PATH.read_text())
        rows = MODULE.complete_inner_rows(self.model, self.base, source_table, self.audit)
        topology = MODULE.r2_antenna_topology(self.model, rows)
        self.assertEqual(12, len(topology["pcb_segments"]))
        self.assertEqual(5, len(topology["cables"]))
        self.assertEqual(10, len(topology["connectors"]))
        self.assertEqual(
            set(self.model["antenna_bank_optimization"]["front_paths"]),
            {row["path"] for row in topology["pcb_segments"] if row["frame"] == "ui-inner"},
        )
        self.assertEqual(
            set(self.model["antenna_bank_optimization"]["rear_paths"]),
            {row["path"] for row in topology["pcb_segments"] if row["frame"] == "rf-inner"},
        )
        by_medium = {row["medium"] for row in topology["pcb_segments"]}
        self.assertIn("high-impedance-ami-pcb", by_medium)
        self.assertIn("matched-rf-pcb-topology", by_medium)
        self.assertIn("converted-airband-rf-if-pcb", by_medium)
        self.assertIn("112-mhz-local-oscillator-pcb", by_medium)
        self.assertTrue(all(row["frame"] == "ui-inner" for row in topology["cables"]))

    def test_generated_artifacts_are_current(self):
        source_table = json.loads(MODULE.SOURCE_TABLE_PATH.read_text())
        expected = {
            MODULE.AUDIT_PATH: json.dumps(self.audit, indent=2, ensure_ascii=False) + "\n",
            MODULE.SVG_PATH: MODULE.render_svg(self.model, self.base, self.audit),
            MODULE.EXTERNAL_SVG_PATH: MODULE.render_external_svg(self.model),
            MODULE.SERVICE_SVG_PATH: MODULE.render_service_svg(self.model),
            MODULE.COMPLETE_INNER_SVG_PATH: MODULE.render_complete_inner_svg(
                self.model, self.base, source_table, self.audit
            ),
            MODULE.INNER_UI_SVG_PATH: MODULE.render_inner_face_svg(
                self.model, self.base, source_table, self.audit, "ui-inner"
            ),
            MODULE.INNER_RF_SVG_PATH: MODULE.render_inner_face_svg(
                self.model, self.base, source_table, self.audit, "rf-inner"
            ),
            MODULE.INNER_SECTIONS_SVG_PATH: MODULE.render_inner_sections_svg(
                self.model, self.base, source_table, self.audit
            ),
            MODULE.COMPONENT_LEGEND_SVG_PATH: MODULE.render_component_legend_svg(
                self.model, self.base, source_table, self.audit
            ),
            MODULE.EN_DOC_PATH: MODULE.render_doc(self.model, self.audit, False),
            MODULE.RU_DOC_PATH: MODULE.render_doc(self.model, self.audit, True),
        }
        expected[MODULE.FOUR_FACES_SVG_PATH] = MODULE.render_four_faces_svg(
            self.model,
            expected[MODULE.EXTERNAL_SVG_PATH],
            expected[MODULE.INNER_UI_SVG_PATH],
            expected[MODULE.INNER_RF_SVG_PATH],
        )
        for path, content in expected.items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(content, path.read_text(), path)
        self.assertNotIn("[`None`]", expected[MODULE.EN_DOC_PATH])
        self.assertNotIn("[`None`]", expected[MODULE.RU_DOC_PATH])
        self.assertIn("Four independent USB paths", expected[MODULE.SERVICE_SVG_PATH])
        self.assertIn(">HUB RP</text>", expected[MODULE.SERVICE_SVG_PATH])
        self.assertIn(">DATA USB</text>", expected[MODULE.SERVICE_SVG_PATH])
        self.assertNotIn('data-instance="fpv_mmcx"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertNotIn('FPV 5G8', expected[MODULE.EXTERNAL_SVG_PATH])
        for instance in ("hub_reset_button", "hub_boot_button"):
            self.assertIn(
                f'data-instance="{instance}" data-mpn="SKRTLAE010" '
                'data-projection="inner-mounted-side-switch"',
                expected[MODULE.EXTERNAL_SVG_PATH],
            )
            self.assertIn(
                f'data-instance="{instance}" data-part="side-actuator" '
                'data-recessed="true"',
                expected[MODULE.EXTERNAL_SVG_PATH],
            )
        self.assertIn('data-view="both-inner-faces-mirrored"', expected[MODULE.COMPLETE_INNER_SVG_PATH])
        self.assertIn('data-inner-silkscreen="none"', expected[MODULE.COMPLETE_INNER_SVG_PATH])
        self.assertIn('data-view="four-faces-matched-columns"', expected[MODULE.FOUR_FACES_SVG_PATH])
        self.assertIn('clip-path="url(#front-external-content)"', expected[MODULE.FOUR_FACES_SVG_PATH])
        self.assertIn('clip-path="url(#rear-external-content)"', expected[MODULE.FOUR_FACES_SVG_PATH])
        self.assertIn('data-view="numbered-component-legend"', expected[MODULE.COMPONENT_LEGEND_SVG_PATH])
        self.assertIn('226 unique drawing references', expected[MODULE.COMPONENT_LEGEND_SVG_PATH])
        self.assertIn('data-physical-feature="cap_socket_pth_keepout"', expected[MODULE.INNER_RF_SVG_PATH])
        self.assertIn('data-physical-feature="u219_nfc_evidence_island_reserve"', expected[MODULE.COMPLETE_INNER_SVG_PATH])
        self.assertIn('u219_nfc_pickup_loop · copper_feature_reserve · X 4…76 · Y 17.8…40.2 mm', expected[MODULE.COMPONENT_LEGEND_SVG_PATH])
        self.assertIn('data-cap-profile="u214"', expected[MODULE.INNER_SECTIONS_SVG_PATH])
        self.assertIn('data-cap-profile="u219"', expected[MODULE.INNER_SECTIONS_SVG_PATH])
        self.assertNotIn('data-physical-feature="u219_nfc_pickup_loop"', expected[MODULE.INNER_RF_SVG_PATH])
        self.assertEqual(5, expected[MODULE.INNER_UI_SVG_PATH].count('data-medium="removable-microcoax"'))
        self.assertEqual(5, expected[MODULE.INNER_UI_SVG_PATH].count('data-part="board-ufl"'))
        self.assertEqual(5, expected[MODULE.INNER_UI_SVG_PATH].count('data-part="module-rf-connector"'))
        self.assertEqual(2, expected[MODULE.INNER_RF_SVG_PATH].count('data-medium="controlled-50-ohm-pcb"'))
        self.assertEqual(1, expected[MODULE.INNER_RF_SVG_PATH].count('data-medium="high-impedance-ami-pcb"'))
        self.assertEqual(1, expected[MODULE.INNER_RF_SVG_PATH].count('data-medium="matched-rf-pcb-topology"'))
        self.assertEqual(1, expected[MODULE.INNER_RF_SVG_PATH].count('data-medium="converted-airband-rf-if-pcb"'))
        self.assertEqual(1, expected[MODULE.INNER_RF_SVG_PATH].count('data-medium="112-mhz-local-oscillator-pcb"'))
        self.assertNotIn('data-medium="removable-microcoax"', expected[MODULE.INNER_RF_SVG_PATH])
        self.assertIn("No U.FL or removable RF cable on this PCB", expected[MODULE.INNER_RF_SVG_PATH])
        self.assertIn('data-topology-source="r2"', expected[MODULE.COMPLETE_INNER_SVG_PATH])
        self.assertIn('data-port-role="power-and-data"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertIn('data-port-role="data-only"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertNotIn('data-interface-shape="usb-c-receptacle"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertNotIn('data-interface-shape="usb-c-receptacle"', expected[MODULE.SERVICE_SVG_PATH])
        self.assertNotIn('data-part="usb-c-tongue"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertEqual(4, expected[MODULE.EXTERNAL_SVG_PATH].count('data-mpn="USB4105-GF-A"'))
        self.assertEqual(4, expected[MODULE.SERVICE_SVG_PATH].count('data-mpn="USB4105-GF-A"'))
        role_baseline = 150.0 + MODULE.BOTTOM_SILK_ROLE_BASELINE_MM * 3.7
        owner_baseline = 150.0 + MODULE.BOTTOM_SILK_OWNER_BASELINE_MM * 3.7
        external = expected[MODULE.EXTERNAL_SVG_PATH]
        self.assertEqual(7, external.count('data-edge="bottom" data-silk-row="role"'))
        self.assertEqual(4, external.count('data-edge="bottom" data-silk-row="owner"'))
        self.assertEqual(7, external.count(f'y="{role_baseline:.1f}"'))
        self.assertEqual(4, external.count(f'y="{owner_baseline:.1f}"'))
        self.assertIn(
            f"h1-r2-four-faces.svg?rev={MODULE.PUBLIC_ASSET_REV}",
            expected[MODULE.EN_DOC_PATH],
        )
        self.assertIn(
            f"h1-r2-service-access.svg?rev={MODULE.PUBLIC_ASSET_REV}",
            expected[MODULE.RU_DOC_PATH],
        )

    def test_right_edge_service_silkscreen_uses_one_column(self):
        root = ET.fromstring(MODULE.render_external_svg(self.model))
        namespace = "{http://www.w3.org/2000/svg}"
        labels = {
            node.text: node
            for node in root.iter(f"{namespace}text")
            if node.text in {"C5 RST", "C5 BOOT", "HUB RST", "HUB BOOT"}
        }
        self.assertEqual(4, len(labels))
        self.assertEqual({350.1}, {float(node.attrib["x"]) for node in labels.values()})


if __name__ == "__main__":
    unittest.main()
