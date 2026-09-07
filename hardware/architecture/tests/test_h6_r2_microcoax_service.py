import json
import copy
import math
import subprocess
import unittest
from pathlib import Path

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
        self.assertEqual([22.0, 3.48], rows["S3-2G4"]["board_connector_mm"])
        self.assertEqual([57.575, 10.55], rows["C5-2G4/5"]["board_connector_mm"])
        self.assertEqual([5.25, 3.875], rows["N24-0"]["board_connector_mm"])

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
