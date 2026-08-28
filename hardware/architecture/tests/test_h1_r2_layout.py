import importlib.util
import json
import unittest
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

    def test_incremental_placement_passes(self):
        self.assertEqual("H1-R2.29", self.model["marker"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual([], self.audit["same_face_collisions"])
        self.assertEqual(37, len(self.audit["opposing_overlaps"]))
        self.assertGreaterEqual(
            self.audit["minimum_opposing_clearance_mm"],
            self.audit["required_opposing_clearance_mm"],
        )

    def test_every_fixed_body_has_exact_mpn(self):
        for item in self.model["placements"]:
            if item["kind"] == "fixed_body":
                self.assertTrue(item["mpn"], item["id"])

    def test_every_drawn_item_has_one_unique_compact_reference(self):
        refs = [item["drawing_ref"] for item in self.model["placements"]]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertTrue(all(len(ref) <= 2 for ref in refs))

    def test_fpv_bay_is_a_dual_post_pcba_reserve_not_a_fake_component(self):
        bay = next(x for x in self.model["placements"] if x["id"] == "fpv_receiver_bay")
        self.assertEqual("reserve", bay["kind"])
        self.assertIsNone(bay["mpn"])
        self.assertEqual("AKK K331", bay["candidate_mpn"])
        self.assertEqual("AWM666V RX", bay["alternate_mpn"])
        self.assertEqual([30.0, 24.0, 8.0], bay["size_mm"])
        self.assertEqual("dual mutually exclusive post-PCBA land", bay["attachment"]["architecture"])
        self.assertEqual("exactly one receiver module", bay["attachment"]["population_rule"])
        self.assertEqual(14, bay["attachment"]["primary"]["contact_count"])
        self.assertEqual([26.16, 16.38, 3.7], bay["attachment"]["fallback"]["body_mm"])
        self.assertEqual(0, bay["attachment"]["normal_pcba_bom_additions"])
        self.assertIn("no live stub", bay["attachment"]["rf_selection"])

    def test_h1_blockers_are_separate_from_dependent_and_later_work(self):
        self.assertEqual(0, len(self.model["current_h1_blockers"]))
        self.assertEqual(1, len(self.model["dependent_h1_work"]))
        self.assertIn("explicitly accept the generated complete R2", self.model["dependent_h1_work"][0])
        self.assertEqual({"H5/H6/H7", "H5/H7", "H5/H8"}, {row["stage"] for row in self.model["downstream_verification"]})
        self.assertEqual(self.model["current_h1_blockers"], self.audit["current_h1_blockers"])
        self.assertEqual(self.model["dependent_h1_work"], self.audit["dependent_h1_work"])

    def test_c5_dbg10_is_relocated_clear_of_the_enlarged_fpv_bay(self):
        header = next(x for x in self.model["placements"] if x["id"] == "c5_dbg_header_r2")
        self.assertEqual(["c5_dbg_header"], header["replaces"])
        self.assertEqual([15.5, 104.0], header["world_xy_mm"])
        self.assertEqual("FTSH-105-01-L-DV-K-P-TR", header["mpn"])
        self.assertEqual("c5_dbg_header_r2", self.audit["relocated_c5_dbg_header"])
        self.assertGreaterEqual(self.audit["minimum_opposing_clearance_mm"], 1.05)

    def test_factory_rows_include_current_identity(self):
        by_mpn = {row["mpn"]: row for row in self.model["factory_evidence"]}
        self.assertEqual("C3824301", by_mpn["TVP5150AM1PBS"]["jlcpcb_part"])
        self.assertEqual("C588480", by_mpn["73415-2063"]["jlcpcb_part"])
        self.assertEqual("C39843328", by_mpn["SC1512-A4"]["jlcpcb_part"])
        self.assertIsNone(by_mpn["K331"]["jlcpcb_part"])
        self.assertFalse(by_mpn["K331"]["accepted"])
        self.assertIn("post-PCBA", by_mpn["K331"]["assembly"])
        self.assertEqual("unavailable", self.model["k331_factory_route"]["exact_parts_library"])
        self.assertEqual("unavailable", self.model["k331_factory_route"]["global_sourcing"])
        self.assertIsNone(self.model["k331_factory_route"]["confirmed_drop_in_alternative"])
        self.assertIn("post-PCBA manual installation", self.model["k331_factory_route"]["selected_route"])
        self.assertTrue(all("accepted" in row for row in self.model["factory_evidence"]))
        self.assertTrue(by_mpn["TPS7A2018PDBVR"]["accepted"])
        self.assertIn("2,225 pieces", by_mpn["TPS7A2018PDBVR"]["availability"])

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

    def test_mmcx_uses_manufacturer_body_and_mounting_geometry(self):
        mmcx = next(x for x in self.model["placements"] if x["id"] == "fpv_mmcx")
        self.assertEqual([42.62, 8.07], mmcx["world_xy_mm"])
        self.assertEqual([4.46, 4.46, 5.0], mmcx["size_mm"])
        self.assertEqual("straight vertical SMT jack", mmcx["mounting"]["connector_style"])
        self.assertEqual([44.85, 10.3], mmcx["mounting"]["mounting_axis_world_xy_mm"])
        self.assertFalse(mmcx["mounting"]["through_board_tail"])
        self.assertEqual(6.0, mmcx["mounting"]["rated_frequency_ghz"])
        evidence = next(x for x in self.model["factory_evidence"] if x["mpn"] == mmcx["mpn"])
        self.assertTrue(evidence["accepted"])
        self.assertIn("molex.com", evidence["manufacturer_url"])
        self.assertIn("molex.com", evidence["drawing_url"])
        self.assertIn("Extended SMT", evidence["assembly"])

    def test_mmcx_tail_and_service_keepouts_pass(self):
        service = self.audit["mmcx_service"]
        self.assertEqual(
            self.base["stack"]["rf_pcb_thickness_mm"],
            self.model["stack"]["rf_pcb_thickness_mm"],
        )
        self.assertEqual("pass", service["status"])
        self.assertEqual([], service["errors"])
        self.assertEqual([], service["opposing_body_hits"])
        self.assertFalse(service["through_board_tail"])
        self.assertEqual(12.0, service["external_service_keepout"]["diameter_mm"])
        self.assertGreaterEqual(service["minimum_rear_antenna_connector_clearance_mm"], 0.7)
        self.assertEqual(
            {"CC-SUB", "VOICE-VHF"},
            {row["path"] for row in service["handling_envelope_overlaps"]},
        )
        self.assertEqual(
            "temporary finger approach only; not a static installed body",
            service["handling_envelope_semantics"],
        )
        self.assertGreaterEqual(service["minimum_right_angle_plug_clearance_mm"], 0.7)
        self.assertGreaterEqual(service["right_angle_plug_u214_clearance_mm"], 0.7)
        self.assertEqual(
            "FXP831.09.0100C",
            service["controlled_right_angle_plug_reference"]["mpn"],
        )
        self.assertAlmostEqual(0.7, service["u214_service_clearance_mm"])

    def test_rear_main_sma_row_is_even_and_fpv_sits_below_it(self):
        rear = self.model["antenna_bank_optimization"]["rear_x_centres_mm"]
        self.assertEqual([8.1, 22.8, 37.5, 52.2, 66.9], rear)
        self.assertEqual(
            self.model["antenna_bank_optimization"]["front_x_centres_mm"], rear
        )
        axis_x, axis_y = self.model["antenna_bank_optimization"]["fpv_mmcx_axis_world_xy_mm"]
        self.assertAlmostEqual((rear[2] + rear[3]) / 2, axis_x)
        self.assertGreater(axis_y, 6.0)

    def test_outer_antenna_silkscreen_is_not_hidden(self):
        self.assertEqual("pass", self.audit["silkscreen"]["status"])
        self.assertEqual([], self.audit["silkscreen"]["errors"])
        self.assertEqual(5, len(self.audit["silkscreen"]["faces"]["front"]))
        self.assertEqual(6, len(self.audit["silkscreen"]["faces"]["rear"]))

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
            MODULE.MMCX_SVG_PATH: MODULE.render_mmcx_service_svg(self.model, self.audit),
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
        self.assertIn('data-instance="fpv_mmcx"', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertIn('>FPV 5G8</text>', expected[MODULE.EXTERNAL_SVG_PATH])
        self.assertIn('5G8', expected[MODULE.EXTERNAL_SVG_PATH])
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
        self.assertIn('163 drawing references', expected[MODULE.COMPONENT_LEGEND_SVG_PATH])
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


if __name__ == "__main__":
    unittest.main()
