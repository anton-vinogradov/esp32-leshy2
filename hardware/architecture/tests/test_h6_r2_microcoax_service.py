import json
import copy
import math
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from hardware.layout import h6_r2_microcoax_service as service


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-microcoax-service.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-microcoax-service-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_microcoax_service.py"
SVG = ROOT / "docs/images/h6-r2-microcoax-service.svg"


class H6R2MicrocoaxServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_five_routes_pass_with_relaxed_length(self):
        self.assertEqual("pass", self.audit["status"])
        self.assertEqual([], self.audit["errors"])
        self.assertEqual(5, self.audit["summary"]["path_count"])
        self.assertEqual(2, self.audit["summary"]["thirty_mm_paths"])
        self.assertEqual(3, self.audit["summary"]["sixty_mm_paths"])
        self.assertGreaterEqual(self.audit["summary"]["minimum_relaxed_reserve_mm"], 5.0)

    def test_nominal_radius_checks_do_not_claim_all_source_window_positions(self):
        self.assertEqual(5, self.audit["summary"]["nominal_planar_radius_paths"])
        self.assertFalse(self.audit["summary"]["all_source_positions_planar_radius_verified"])
        self.assertEqual(["N24-0", "N24-1", "N24-2"], self.audit["summary"]["source_window_radius_validation_pending"])
        for row in self.audit["paths"]:
            self.assertGreaterEqual(row["minimum_planar_bend_radius_mm"], 6.0)
            self.assertGreater(row["curve_sampling_error_bound_mm"], 0)

    def test_fillet_uses_real_tangent_arcs_and_rejects_short_legs(self):
        points, length, radius = service.fillet_corridor([[0, 10], [0, 0], [10, 0]], 6, {})
        self.assertAlmostEqual(8 + 3*math.pi, length)
        self.assertEqual(6, radius)
        self.assertGreater(len(points), 100)
        self.assertNotIn([0, 0], points)
        with self.assertRaisesRegex(ValueError, "tangent lengths"):
            service.fillet_corridor([[0, 5], [0, 0], [5, 0]], 6, {})

    def test_each_route_has_one_clear_independent_saddle(self):
        self.assertEqual(5, self.audit["summary"]["retention_saddles"])
        centres = []
        for row in self.audit["paths"]:
            self.assertTrue(row["retention_landing_clear"], row["path"])
            self.assertGreaterEqual(row["source_free_length_mm"], 5.0, row["path"])
            self.assertGreaterEqual(row["board_connector_free_length_mm"], 5.0, row["path"])
            centres.append(tuple(row["retention_saddle_centre_mm"]))
        self.assertEqual(5, len(set(centres)))

    def test_s3_source_uses_native_back_side_transform_and_relaxed_shield_curve(self):
        row = next(row for row in self.audit["paths"] if row["path"] == "S3-2G4")
        self.assertEqual([31.0, 23.615], row["source_reference_mm"])
        self.assertEqual("module_shield", row["retention_support"])
        self.assertGreaterEqual(row["minimum_planar_bend_radius_mm"], 6.0)
        self.assertGreater(row["vertical_transition_length_allowance_mm"], 1.5)
        self.assertGreaterEqual(row["minimum_relaxed_reserve_mm"], 5.0)
        self.assertLessEqual(row["conservative_corridor_length_mm"], 25.0)

    def test_source_axis_and_corner_checks_reject_wrong_native_orientation(self):
        placement = service.load(service.PLACEMENT)
        board = next(row for row in placement["boards"] if row["project"] == "LESHY2-UI-R2")
        for row in board["placements"]:
            if row["instance"] == "c5":
                row["rotation_deg"] = 0.0
            elif row["instance"] == "nrf0":
                row["rotation_deg"] = 90.0
        result = service.evaluate(self.contract, placement, service.load(service.PLACEMENT_CONTRACT),
                                  service.load(service.H1), service.load(service.H3))
        self.assertTrue(any("C5-2G4/5: source connector axis differs" in error for error in result["errors"]))
        self.assertTrue(any("N24-0: source access window differs" in error for error in result["errors"]))

    def test_destinations_use_mating_axes_not_asymmetric_courtyard_centres(self):
        rows = {row["path"]: row for row in self.audit["paths"]}
        self.assertEqual([20.0, 3.48], rows["S3-2G4"]["board_connector_mm"])
        self.assertEqual([57.575, 10.55], rows["C5-2G4/5"]["board_connector_mm"])
        self.assertEqual([4.25, 3.875], rows["N24-0"]["board_connector_mm"])

    def test_s3_reposition_retains_exact_cable_and_full_z_allowance(self):
        row = next(row for row in self.contract["paths"] if row["path"] == "S3-2G4")
        self.assertEqual("TE Connectivity 2118651-2", row["cable_mpn"])
        self.assertEqual(30.0, row["selected_length_mm"])
        self.assertEqual([20.0, 3.48], row["board_connector_mm"])
        points, planar_upper, radius = service.corridor_geometry(row)
        self.assertEqual([25.15, 13.54875], row["retention_saddle_centre_mm"])
        for actual, expected in zip(points[64], row["retention_saddle_centre_mm"]):
            self.assertAlmostEqual(actual, expected)
        support = row["retention_support"]
        self.assertEqual(3.35, support["surface_height_max_mm"])
        self.assertEqual(7.0, support["vertical_transition_radius_mm"])
        angle = math.acos(1 - 3.35 / 14)
        z_allowance = 2 * (14 * angle - 14 * math.sin(angle))
        self.assertAlmostEqual(1.6043046603067346, z_allowance)
        reserve = 30 - planar_upper - z_allowance
        self.assertAlmostEqual(5.440879462291754, reserve)
        self.assertGreaterEqual(reserve, 5.0)
        self.assertGreaterEqual(radius, 6.0)
        # The old unreviewed farther-left location cannot be accepted merely
        # because its straight chord is shorter than the nominal cable.
        wrong = copy.deepcopy(row)
        wrong["board_connector_mm"] = [17.2, 3.48]
        _, wrong_length, _ = service.corridor_geometry(wrong)
        self.assertLess(30 - wrong_length - z_allowance, 5.0)

    def test_n24_left_endpoint_extends_existing_fillet_not_cable_length(self):
        row = next(row for row in self.contract["paths"] if row["path"] == "N24-0")
        self.assertEqual("TE Connectivity 1-2118651-0", row["cable_mpn"])
        self.assertEqual(60.0, row["selected_length_mm"])
        self.assertEqual([4.25, 3.875], row["board_connector_mm"])
        self.assertEqual(row["board_connector_mm"], row["corridor_points_mm"][-1])
        self.assertEqual(6.0, row["corridor_fillet_radius_mm"])
        points, length, radius = service.corridor_geometry(row)
        previous = copy.deepcopy(row)
        previous["corridor_points_mm"][-1] = [5.25, 3.875]
        _, previous_length, previous_radius = service.corridor_geometry(previous)
        self.assertAlmostEqual(1.0, length - previous_length)
        self.assertEqual(previous_radius, radius)
        self.assertEqual([4.25, 3.875], points[-1])

    def test_front_side_sma_lands_block_a_back_side_tape_landing(self):
        board = {"placements": [{"instance": "edge_sma", "side": "F.Cu",
                 "courtyard_bbox_mm": {"x": [0, 10], "y": [-12, -1]},
                 "opposite_face_keepout_bboxes_mm": [{"x": [2, 4], "y": [0, 3.3]}]}]}
        obstacles = service.landing_obstacles(board)
        self.assertEqual(["edge_sma:opposite-face-land"], [name for name, _ in obstacles])
        self.assertTrue(service.boxes_overlap(service.expanded_box([3, 3], [5, 3], 0.25), obstacles[0][1]))

    def test_shield_support_exception_rejects_a_landing_outside_flat_subset(self):
        contract = copy.deepcopy(self.contract)
        row = next(row for row in contract["paths"] if row["path"] == "S3-2G4")
        row["retention_support"]["safe_flat_local_bbox_mm"] = {"x": [-8, -7], "y": [-1, 1]}
        result = service.evaluate(contract, service.load(service.PLACEMENT),
                                  service.load(service.PLACEMENT_CONTRACT), service.load(service.H1), service.load(service.H3))
        self.assertEqual("fail", result["status"])
        self.assertTrue(any("outside-verified-shield-landing" in error for error in result["errors"]))

    def test_shield_height_includes_tolerance_cable_and_tape(self):
        contract = copy.deepcopy(self.contract)
        contract["common_constraints"]["enclosure_clearance"]["route_prism_height_above_ui_inner_mm"] = 4.5
        result = service.evaluate(contract, service.load(service.PLACEMENT),
                                  service.load(service.PLACEMENT_CONTRACT), service.load(service.H1), service.load(service.H3))
        self.assertTrue(any("exceeds the reserved height" in error for error in result["errors"]))

    def test_display_slot_and_zif_stay_accessible(self):
        required = (
            self.contract["common_constraints"]["corridor_width_mm"] / 2
            + self.contract["common_constraints"]["minimum_corridor_edge_clearance_mm"]
        )
        for row in self.audit["paths"]:
            self.assertGreaterEqual(
                row["minimum_display_exclusion_distance_mm"], required, row["path"]
            )

    def test_full_corridors_and_saddles_clear_all_mounting_keepouts(self):
        self.assertGreaterEqual(
            self.audit["summary"]["minimum_mechanical_keepout_clearance_mm"], 0.0
        )
        for row in self.audit["paths"]:
            self.assertGreaterEqual(
                row["minimum_mechanical_keepout_clearance_mm"], 0.0, row["path"]
            )
            self.assertGreaterEqual(
                row["retention_mechanical_keepout_clearance_mm"], 0.0, row["path"]
            )
        nrf2 = next(row for row in self.audit["paths"] if row["path"] == "N24-2")
        self.assertGreaterEqual(nrf2["minimum_mechanical_keepout_clearance_mm"], 0.3)

    def test_nrf_paths_use_windows_not_invented_exact_axes(self):
        paths = {row["path"]: row for row in self.contract["paths"]}
        for name in ("N24-0", "N24-1", "N24-2"):
            self.assertEqual("published_corner_window", paths[name]["source_kind"])
            self.assertIn("source_access_window_mm", paths[name])
        self.assertEqual(
            "exact_module_axis", paths["S3-2G4"]["source_kind"]
        )
        self.assertEqual(
            "exact_module_axis", paths["C5-2G4/5"]["source_kind"]
        )

    def test_all_ten_antenna_solder_windows_exist(self):
        self.assertEqual(10, self.audit["summary"]["antenna_solder_windows"])
        self.assertEqual(
            {"LESHY2-UI-R2", "LESHY2-RF-R2"},
            {row["board"] for row in self.audit["antenna_solder_windows"]},
        )

    def test_antenna_window_pass_does_not_qualify_native_solder_access(self):
        audit = service.evaluate(self.contract, service.load(service.PLACEMENT),
                                 service.load(service.PLACEMENT_CONTRACT),
                                 service.load(service.H1), service.load(service.H3))
        self.assertEqual("pass", audit["status"])
        self.assertTrue(audit["summary"]["routing_may_start"])
        self.assertEqual("nominal microcoax geometry and contract antenna-window count/pitch only",
                         audit["status_scope"])
        self.assertEqual({
            "status": "count_and_pitch_only",
            "position_basis": "placement_contract.antenna_ports",
            "native_solder_access_verified_by_this_audit": False,
        }, audit["antenna_solder_window_scope"])
        residual = " ".join(audit["residual_physical_evidence"])
        for obligation in ("solder-land", "component-body", "soldering-tool", "fillet visibility"):
            self.assertIn(obligation, residual)

    def test_antenna_scope_does_not_weaken_count_or_pitch_gates(self):
        for defect in ("missing_port", "insufficient_pitch"):
            placement_contract = service.load(service.PLACEMENT_CONTRACT)
            ports = placement_contract["antenna_ports"]["LESHY2-RF-R2"]
            names = sorted(ports, key=lambda name: ports[name][0])
            if defect == "missing_port":
                del ports[names[-1]]
                expected_error = "antenna inspection count is not five"
            else:
                ports[names[1]][0] = ports[names[0]][0] + 10.0
                expected_error = "adjacent antenna inspection windows are too close"
            audit = service.evaluate(self.contract, service.load(service.PLACEMENT),
                                     placement_contract, service.load(service.H1), service.load(service.H3))
            with self.subTest(defect=defect):
                self.assertEqual("fail", audit["status"])
                self.assertFalse(audit["summary"]["routing_may_start"])
                self.assertTrue(any(expected_error in error for error in audit["errors"]))
                self.assertIs(False, audit["antenna_solder_window_scope"]["native_solder_access_verified_by_this_audit"])

    def test_generated_languages_keep_solder_access_outside_window_pass(self):
        audit = service.evaluate(self.contract, service.load(service.PLACEMENT),
                                 service.load(service.PLACEMENT_CONTRACT),
                                 service.load(service.H1), service.load(service.H3))
        for language in service.DOCS:
            sections = service.document_sections(self.contract, audit, language)
            with self.subTest(language=language):
                self.assertIn("native_solder_access_verified_by_this_audit: false", sections["status"])
                self.assertIn("placement contract", sections["clearance"])
                self.assertNotIn("placement freeze", sections["clearance"])
                self.assertIn("H6-R2-sma-solder-access-audit.json", sections["clearance"])
                self.assertIn("не являются подтверждением" if language == "ru" else "are not factory",
                              sections["clearance"])

    def test_both_document_tables_equal_current_audit_not_old_spacing(self):
        for language, path in service.DOCS.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(language=language):
                self.assertEqual(text, service.render_document(text, self.contract, self.audit, language))
                unit = "мм" if language == "ru" else "mm"
                for row in self.audit["paths"]:
                    cells = next(line for line in text.splitlines() if line.startswith(f"| `{row['path']}` |"))
                    for key in ("conservative_corridor_length_mm", "minimum_relaxed_reserve_mm", "minimum_planar_bend_radius_mm"):
                        number = f"{row[key]:.3f}".replace(".", "," if language == "ru" else ".")
                        self.assertIn(number + " " + unit, cells)
                for stale in ("11.75", "11,75", "9.257", "9,257", "5.436", "5,436", "13.135", "13,135", "1.879", "1,879"):
                    self.assertNotIn(stale, text)

    def test_document_updates_derived_reserve_radius_and_axis(self):
        changed = copy.deepcopy(self.audit)
        row = next(row for row in changed["paths"] if row["path"] == "S3-2G4")
        row.update(minimum_relaxed_reserve_mm=5.678, minimum_planar_bend_radius_mm=123.456,
                   board_connector_mm=[21.123, 4.567])
        changed["summary"]["minimum_relaxed_reserve_mm"] = 5.678
        for language in service.DOCS:
            sections = service.document_sections(self.contract, changed, language)
            separator = "," if language == "ru" else "."
            for number in ("5.678", "123.456", "21.123", "4.567"):
                self.assertIn(number.replace(".", separator), sections["results"])
            self.assertIn("5.68 mm minimum reserve", sections["reproduce"])

    def test_document_pitch_uses_both_contract_banks_not_h1_mockup(self):
        changed = copy.deepcopy(self.audit)
        window = next(row for row in changed["antenna_solder_windows"]
                      if row["board"] == "LESHY2-RF-R2" and row["centre_x_mm"] == 25.3)
        window["centre_x_mm"] = 24.6  # RF minimum becomes 14.0; UI stays 14.7.
        for language in service.DOCS:
            section = service.document_sections(self.contract, changed, language)["clearance"]
            separator = "," if language == "ru" else "."
            self.assertIn("14.000".replace(".", separator), section)
            self.assertIn("4.000".replace(".", separator), section)

    def test_document_keeps_radius_and_height_qualification_open(self):
        for language, path in service.DOCS.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn("all_source_positions_planar_radius_verified: false", text)
            self.assertIn("H6.0.7", text)
            self.assertIn("STEP", text)
            self.assertIn("4,58" if language == "ru" else "4.58", text)
            self.assertIn("4,70" if language == "ru" else "4.70", text)
        changed = copy.deepcopy(self.audit)
        changed["status"] = "fail"
        for language in service.DOCS:
            sections = service.document_sections(self.contract, changed, language)
            self.assertIn("`fail`", sections["status"])
            self.assertIn("microcoax service fail:", sections["reproduce"])
            self.assertNotIn("`pass`", sections["status"])

    def test_document_markers_fail_closed_and_prose_is_preserved(self):
        source = service.DOCS["en"].read_text(encoding="utf-8")
        sentinel = "\nAn independently reviewed assembly note.\n"
        self.assertTrue(service.render_document(source + sentinel, self.contract, self.audit, "en").endswith(sentinel))
        start = "<!-- BEGIN GENERATED MICROCOAX results -->"
        end = "<!-- END GENERATED MICROCOAX results -->"
        for malformed in (source.replace(start, ""), source + start, source.replace(end, ""),
                          source.replace(start, "TMP").replace(end, start).replace("TMP", end)):
            with self.subTest(malformed=malformed[-60:]), self.assertRaises(ValueError):
                service.render_document(malformed, self.contract, self.audit, "en")
        with self.assertRaises(ValueError):
            service.render_document(source, self.contract, self.audit, "unknown")

    def test_cli_check_rejects_stale_document_without_writing_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            doc = root / "docs/h6-r2-microcoax-service.md"
            doc.parent.mkdir()
            text = service.DOCS["en"].read_text(encoding="utf-8")
            stale = text.replace("196.607 mm", "13.135 mm")
            self.assertNotEqual(text, stale)
            doc.write_text(stale, encoding="utf-8")
            out = StringIO()
            with patch.object(service, "ROOT", root), patch.object(service, "DOCS", {"en": doc}), \
                    patch.object(service, "evaluate", return_value=self.audit), \
                    patch("sys.argv", [str(SCRIPT), "--check"]), redirect_stdout(out):
                self.assertEqual(1, service.main())
            self.assertIn("stale outputs: docs/h6-r2-microcoax-service.md", out.getvalue())
            self.assertEqual(stale, doc.read_text(encoding="utf-8"))

    def test_outputs_are_reproducible_and_preview_is_explanatory(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        preview = SVG.read_text(encoding="utf-8")
        self.assertIn("five relaxed microcoax service corridors", preview)
        self.assertIn("do not guess an ipex axis", preview.lower())
        self.assertIn("H6.0.3 routing is current", preview)


if __name__ == "__main__":
    unittest.main()
