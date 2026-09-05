import json
import subprocess
import unittest
from pathlib import Path


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

    def test_each_route_has_one_clear_independent_saddle(self):
        self.assertEqual(5, self.audit["summary"]["retention_saddles"])
        centres = []
        for row in self.audit["paths"]:
            self.assertTrue(row["retention_landing_clear"], row["path"])
            self.assertGreaterEqual(row["source_free_length_mm"], 5.0, row["path"])
            self.assertGreaterEqual(row["board_connector_free_length_mm"], 5.0, row["path"])
            centres.append(tuple(row["retention_saddle_centre_mm"]))
        self.assertEqual(5, len(set(centres)))

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
