import copy
import json
import subprocess
import unittest
from pathlib import Path

from hardware.layout.h6_r2_mechanical_stack import (
    evaluate, evaluate_connector_fit, evaluate_mounting_axes,
)


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-mechanical-stack.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-mechanical-stack-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_mechanical_stack.py"
SVG = ROOT / "docs/images/h6-r2-mechanical-stack.svg"
PLACEMENT = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
KICAD_PYTHON = Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3")


class H6R2MechanicalStackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.placement = json.loads(PLACEMENT.read_text(encoding="utf-8"))

    def test_each_board_mounting_set_is_transformed_independently(self):
        result = evaluate_mounting_axes(self.contract, self.placement)
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["errors"])
        self.assertEqual(2, len(result["boards"]))
        for row in result["boards"]:
            self.assertEqual(4, row["hole_count"])
            self.assertTrue(row["matches_assembly_axes"])
            self.assertEqual([[5.0, 11.0], [5.0, 145.0], [75.0, 11.0], [75.0, 145.0]],
                             row["world_axes_mm"])

    def test_one_or_all_missing_mounts_cannot_be_hidden_by_other_board(self):
        for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            for count in (1, 4):
                with self.subTest(project=project, count=count):
                    placement = copy.deepcopy(self.placement)
                    board = next(b for b in placement["boards"] if b["project"] == project)
                    del board["mechanical"][:count]
                    result = evaluate(self.contract, placement)
                    self.assertEqual("fail", result["status"])
                    self.assertFalse(result["geometry"]["mounting_axes_match_native_pcbs"])
                    self.assertTrue(any(project in e for e in result["errors"]))

    def test_moved_duplicated_and_relabelled_mounts_fail_closed(self):
        for mode in ("moved", "extra_duplicate", "duplicate_coordinate", "duplicate_id"):
            for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
                with self.subTest(mode=mode, project=project):
                    placement = copy.deepcopy(self.placement)
                    rows = next(b for b in placement["boards"] if b["project"] == project)["mechanical"]
                    if mode == "moved":
                        rows[0]["centre_mm"][0] += 0.1
                    elif mode == "extra_duplicate":
                        rows.append(copy.deepcopy(rows[0]))
                    elif mode == "duplicate_coordinate":
                        rows[1]["centre_mm"] = list(rows[0]["centre_mm"])
                    else:
                        rows[1]["id"] = rows[0]["id"]
                    result = evaluate_mounting_axes(self.contract, placement)
                    self.assertEqual("fail", result["status"])
                    self.assertTrue(any(project in e for e in result["errors"]))

    def test_asymmetric_fixture_requires_real_rf_reflection_not_equal_native_axes(self):
        # Deliberately asymmetric synthetic fixture distinguishes identity from
        # physical X reflection; the current symmetric four-hole layout cannot.
        contract = copy.deepcopy(self.contract)
        contract["coordinate_system"]["mounting_axes_mm"][0] = [6.0, 11.0]
        placement = copy.deepcopy(self.placement)
        ui, rf = (next(b for b in placement["boards"] if b["project"] == project)
                  for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"))
        ui["mechanical"][0]["centre_mm"] = [6.0, 11.0]
        # Native RF MH2 is the counterpart of UI MH1, not RF MH1.
        rf["mechanical"][1]["centre_mm"] = [74.0, 11.0]
        self.assertEqual("pass", evaluate_mounting_axes(contract, placement)["status"])
        rf["mechanical"] = copy.deepcopy(ui["mechanical"])
        self.assertEqual("fail", evaluate_mounting_axes(contract, placement)["status"])

    def test_missing_duplicate_or_unknown_board_report_fails_closed(self):
        for mode in ("missing", "duplicate", "unknown"):
            placement = copy.deepcopy(self.placement)
            if mode == "missing":
                placement["boards"].pop()
            elif mode == "duplicate":
                placement["boards"][1] = copy.deepcopy(placement["boards"][0])
            else:
                placement["boards"][1]["project"] = "UNREVIEWED-PCB"
            with self.subTest(mode=mode):
                self.assertEqual("fail", evaluate_mounting_axes(self.contract, placement)["status"])

    def test_nonfinite_or_malformed_mount_coordinates_are_not_accepted(self):
        for xy in ([float("nan"), 11], [float("inf"), 11], [True, 11], [5], [5, "11"], None):
            placement = copy.deepcopy(self.placement)
            placement["boards"][0]["mechanical"][0]["centre_mm"] = xy
            with self.subTest(xy=xy):
                self.assertEqual("fail", evaluate_mounting_axes(self.contract, placement)["status"])

    def test_native_m1_all_eighty_lands_mate_in_physical_frame(self):
        if not KICAD_PYTHON.is_file():
            self.skipTest("KiCad bundled pcbnew Python is unavailable")
        # Unlike the separate source-pattern M1 tests, read all actual native
        # pad positions and poses. Neither board is saved, even for negatives.
        code = r'''
import math
from pathlib import Path
import pcbnew
root = Path.cwd()
boards = {}
for short in ("UI", "RF"):
    project = "LESHY2-" + short + "-R2"
    boards[short] = pcbnew.LoadBoard(str(root / "hardware/ecad/kicad" / project / (project + ".kicad_pcb")))
ui = next(f for f in boards["UI"].GetFootprints() if f.GetReference() == "J18")
rf = next(f for f in boards["RF"].GetFootprints() if f.GetReference() == "J12")
def xy(v):
    return pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)
def mates():
    assert ui.GetLayer() == rf.GetLayer() == pcbnew.B_Cu
    assert ui.GetOrientationDegrees() % 360 == 0
    assert rf.GetOrientationDegrees() % 360 == 180
    ux, uy = xy(ui.GetPosition()); rx, ry = xy(rf.GetPosition())
    assert math.isclose(ux, 80-rx, abs_tol=1e-6) and math.isclose(uy, ry, abs_tol=1e-6)
    up = {p.GetNumber(): p for p in ui.Pads() if p.GetNumber()}
    rp = {p.GetNumber(): p for p in rf.Pads() if p.GetNumber()}
    assert set(up) == set(rp) == {str(n) for n in range(1, 81)}
    for number in up:
        assert up[number].GetAttribute() == rp[number].GetAttribute() == pcbnew.PAD_ATTRIB_SMD
        x1,y1 = xy(up[number].GetPosition()); x2,y2 = xy(rp[number].GetPosition())
        assert math.isclose(x1,80-x2,abs_tol=1e-6)
        # Primary P/S solder tails differ by0.15; this is not a body-axis gap.
        assert math.isclose(y2-y1,-0.15 if int(number)%2 else 0.15,abs_tol=1e-6)
    return True
assert mates()
rf.SetOrientationDegrees(0)
try:
    mates()
except AssertionError:
    pass
else:
    raise AssertionError("unrotated RF connector was accepted")
rf.SetOrientationDegrees(180)
position = rf.GetPosition()
rf.SetPosition(pcbnew.VECTOR2I(position.x + pcbnew.FromMM(0.25), position.y))
try:
    mates()
except AssertionError:
    pass
else:
    raise AssertionError("misregistered RF connector was accepted")
print("80 native same-number pairs and two in-memory negative controls passed; no PCB saved")
'''
        result = subprocess.run([str(KICAD_PYTHON), "-c", code], cwd=ROOT, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("80 native same-number pairs", result.stdout)

    def test_stack_passes_at_all_declared_tolerance_corners(self):
        self.assertEqual("review_required", self.audit["status"])
        self.assertEqual("pass", self.audit["fastener_and_planar_checks_status"])
        self.assertFalse(self.audit["production_release_ready"])
        self.assertEqual([], self.audit["errors"])
        self.assertGreaterEqual(
            self.audit["stack"]["thread_available_at_nut_minimum_mm"], 2.0
        )
        self.assertGreaterEqual(
            self.audit["stack"]["thread_beyond_nut_minimum_mm"], 0.15
        )
        self.assertLessEqual(
            self.audit["stack"]["thread_beyond_nut_maximum_mm"], 2.1
        )
        self.assertGreaterEqual(
            self.audit["stack"]["minimum_tip_clearance_to_outer_surface_mm"], 0.08
        )

    def test_exact_hardware_and_native_axes_are_locked(self):
        self.assertEqual("50M025045P020", self.audit["selected_hardware"]["screw"])
        self.assertEqual("04M025045HN", self.audit["selected_hardware"]["nut"])
        self.assertEqual("007.02.611", self.audit["selected_hardware"]["compression_stop"])
        self.assertEqual(
            "TG-A3500-5-5-3.0",
            self.audit["selected_hardware"]["cell_ntc_gap_pad"],
        )
        self.assertTrue(self.audit["geometry"]["mounting_axes_match_native_pcbs"])
        self.assertEqual(4, self.audit["geometry"]["mounting_axis_count"])

    def test_m1_is_not_structural_and_each_board_has_independent_capture(self):
        self.assertEqual("none", self.audit["geometry"]["m1_structural_role"])
        self.assertEqual(4, self.audit["geometry"]["capture_segments_per_board"])
        self.assertGreaterEqual(
            self.audit["geometry"]["calculated_minimum_pilot_diametral_clearance_mm"],
            0.15,
        )

    def test_ntc_xy_placement_does_not_prove_physical_thermal_contact(self):
        thermal = self.audit["battery_thermal_contacts"]
        self.assertEqual(
            [[33.44, 85.0], [52.54, 85.0]],
            thermal["actual_ntc_centres_mm"],
        )
        self.assertEqual(
            thermal["expected_cell_axis_centres_mm"],
            thermal["actual_ntc_centres_mm"],
        )
        self.assertEqual("F.Cu", thermal["required_side"])
        self.assertEqual(2, thermal["accepted_holder_window_overlaps"])
        self.assertTrue(thermal["contact_beds_contain_ntc_courtyards"])
        self.assertTrue(thermal["electrically_insulating_material_required"])
        self.assertFalse(thermal["physical_contact_proved"])
        self.assertIsNone(thermal["nominal_gap_pad_compression_percent"])
        self.assertIsNone(thermal["holder_cell_floor_nominal_above_pcb_mm"])
        self.assertEqual("requires_confirmation", thermal["status"])
        self.assertEqual("H6-CELL-NTC-HEIGHT-FIT", thermal["release_gate"]["id"])
        self.assertTrue(thermal["release_gate"]["blocks_production_release"])
        self.assertTrue(thermal["release_gate"]["blocks_battery_energization"])
        self.assertFalse(self.audit["battery_energization_authorized"])

    def test_retaining_post_dimension_cannot_reappear_as_cell_floor(self):
        for value in (3.3, 3.43, 3.0, float("nan"), True):
            contract = copy.deepcopy(self.contract)
            contract["battery_thermal_contacts"]["holder_cell_floor_nominal_above_pcb_mm"] = value
            with self.subTest(value=value):
                result = evaluate(contract, self.placement)
                self.assertEqual("fail", result["status"])
                self.assertIsNone(result["battery_thermal_contacts"]["nominal_gap_pad_compression_percent"])
                self.assertFalse(result["production_release_ready"])

    def test_unverified_contact_gate_cannot_be_disabled(self):
        for key, value in (("status", "closed"), ("blocks_production_release", False),
                           ("blocks_battery_energization", False)):
            contract = copy.deepcopy(self.contract)
            contract["battery_thermal_contacts"]["release_gate"][key] = value
            with self.subTest(key=key):
                self.assertEqual("fail", evaluate(contract, self.placement)["status"])

    def test_reproducible_open_report_is_not_release_acceptance(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check", "--require-release-ready"],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("thermal contact unverified", result.stdout)

    def test_nominal_sma_fit_does_not_hide_worst_case_interference(self):
        fit = self.audit["connector_fit"]
        self.assertEqual("requires_confirmation", fit["status"])
        self.assertEqual("2026-09-07", fit["checked_on"])
        self.assertEqual([1.65, 1.85], fit["slot_gap_range_mm"])
        self.assertEqual(2, len(fit["rows"]))
        for row in fit["rows"]:
            self.assertEqual([1.44, 1.76], row["pcb_thickness_range_mm"])
            self.assertEqual(0.15, row["assembly_clearance_nominal_mm"])
            self.assertEqual(-0.11, row["assembly_clearance_minimum_mm"])
            self.assertEqual(0.41, row["assembly_clearance_maximum_mm"])
            self.assertEqual(0.11, row["worst_case_interference_mm"])
            self.assertFalse(row["all_declared_corners_fit"])
        gate = fit["release_gate"]
        self.assertEqual("H6-SMA-FINISHED-THICKNESS-FIT", gate["id"])
        self.assertEqual("open", gate["status"])
        self.assertTrue(gate["blocks_production_release"])
        self.assertTrue(gate["routing_may_continue"])
        self.assertEqual(
            ["LESHY2-UI-R2", "LESHY2-RF-R2"], gate["unresolved_projects"]
        )
        self.assertIn("connector fit is reported separately", self.audit["status_scope"])
        self.assertFalse(self.contract["authorization"]["fabrication"])

    def test_sma_fit_uses_each_pcb_tolerance_independently(self):
        candidate = copy.deepcopy(self.contract)
        candidate["tolerance_stack"]["ui_pcb_mm"]["plus"] = 0.02
        result = evaluate_connector_fit(candidate)
        rows = {row["project"]: row for row in result["rows"]}
        self.assertEqual(0.03, rows["LESHY2-UI-R2"]["assembly_clearance_minimum_mm"])
        self.assertTrue(rows["LESHY2-UI-R2"]["all_declared_corners_fit"])
        self.assertEqual(-0.11, rows["LESHY2-RF-R2"]["assembly_clearance_minimum_mm"])
        self.assertEqual(["LESHY2-RF-R2"], result["release_gate"]["unresolved_projects"])
        self.assertEqual("requires_confirmation", result["status"])
        self.assertTrue(result["release_gate"]["blocks_production_release"])

        candidate["tolerance_stack"]["ui_pcb_mm"]["plus"] = 0.05
        boundary = evaluate_connector_fit(candidate)["rows"][0]
        self.assertEqual(0.0, boundary["assembly_clearance_minimum_mm"])
        self.assertTrue(boundary["all_declared_corners_fit"])

    def test_outputs_are_reproducible(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def test_preview_explains_each_load_path(self):
        text = SVG.read_text(encoding="utf-8")
        self.assertIn("WHAT HOLDS WHAT", text)
        self.assertIn("M1 carries no enclosure load", text)
        self.assertIn("one loose screw does not load M1", text)
        self.assertIn("CELL TEMPERATURE", text)
        self.assertIn("CONCEPT ONLY", text)
        self.assertIn("compression unknown", text)
        self.assertNotIn("nominal compression 20.0%", text)
        self.assertIn("TG-A3500-5-5-3.0", text)
        self.assertIn("do not install cells", text)
        self.assertIn("SMA FIT: requires_confirmation", text)
        self.assertIn("worst clearance -0.11 mm", text)


if __name__ == "__main__":
    unittest.main()
