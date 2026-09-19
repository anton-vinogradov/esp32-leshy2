"""Fail-closed adapter tests; no KiCad runtime or production writes required."""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from hardware.layout import h6_r2_acceptance_adapters as adapters


class LayoutAcceptanceAdapterTests(unittest.TestCase):
    def test_registry_import_does_not_load_native_runtime(self):
        code = ("from hardware.layout import h6_r2_acceptance_adapters as a; "
                "import sys; assert 'pcbnew' not in sys.modules; "
                "assert len(a.CHECKS) == 5")
        subprocess.run([sys.executable, "-c", code], cwd=adapters.ROOT, check=True)

    def test_unknown_id_is_not_a_successful_empty_check(self):
        with self.assertRaises(ValueError):
            adapters.run_check("unknown")

    def test_native_import_or_missing_prerequisite_fails_closed(self):
        for error in (ImportError("pcbnew"), SystemExit("KiCad required"), FileNotFoundError("source")):
            with self.subTest(error=type(error).__name__), patch.object(adapters, "_module", side_effect=error):
                result = adapters.run_check("footprint-parity")
                self.assertEqual("fail", result["verdict"])
                self.assertTrue(result["details"]["prerequisite_error"])

    def test_cached_dependency_requires_exact_fresh_source_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_bytes(b"current")
            report = {"source_hashes": {"source.json": hashlib.sha256(b"current").hexdigest()}}
            adapters._verify_source_hashes(report, {"source.json"}, root)
            for broken in ({"source_hashes": {}},
                           {"source_hashes": {"source.json": hashlib.sha256(b"older").hexdigest()}},
                           {"source_hashes": {**report["source_hashes"], "extra": "0" * 64}}):
                with self.subTest(broken=broken), self.assertRaises(ValueError):
                    adapters._verify_source_hashes(broken, {"source.json"}, root)

    def _placement_fixture(self, root, stored=b"fresh", native=b"matching"):
        audit_path = root / "placement.json"
        audit_path.write_bytes(stored)
        audit = {"status": "pass", "errors": [], "boards": [
            {"project": project, "output": f"hardware/ecad/kicad/{project}/{project}.kicad_pcb",
             "placement_signature_sha256": hashlib.sha256(b"matching").hexdigest()}
            for project in sorted(adapters.PROJECTS)]}
        freeze = SimpleNamespace(verify=Mock(return_value=[]))
        modules = {
            "h6_r2_kicad_net_bindings": SimpleNamespace(check=lambda: []),
            "h6_r2_placement": SimpleNamespace(
                AUDIT_PATH=audit_path, build=lambda: ({audit_path: b"fresh"}, audit),
                pcbnew=SimpleNamespace(LoadBoard=lambda _: object()),
                placement_signature_bytes=lambda project, board: native),
            "h6_r2_placement_freeze": freeze,
        }
        return modules, freeze

    def test_matching_cached_report_still_requires_current_native_board(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            modules, freeze = self._placement_fixture(root, native=b"moved footprint")
            with patch.object(adapters, "ROOT", root), patch.object(adapters, "_module", side_effect=modules.__getitem__):
                result = adapters.run_check("mechanical-stack")
            self.assertEqual("fail", result["verdict"])
            self.assertIn("native placement signature", result["findings"][0])
            freeze.verify.assert_not_called()

    def test_stale_placement_report_cannot_be_reused_for_mechanics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            modules, _ = self._placement_fixture(root, stored=b"older report")
            with patch.object(adapters, "ROOT", root), patch.object(adapters, "_module", side_effect=modules.__getitem__):
                result = adapters.run_check("mechanical-stack")
            self.assertEqual("fail", result["verdict"])
            self.assertIn("cached placement report", result["findings"][0])

    def test_matching_placement_checks_both_projects_and_freeze(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            modules, freeze = self._placement_fixture(root)
            with patch.object(adapters, "ROOT", root), patch.object(adapters, "_module", side_effect=modules.__getitem__):
                report = adapters._fresh_placement()
            self.assertEqual(adapters.PROJECTS, {b["project"] for b in report["boards"]})
            freeze.verify.assert_called_once_with()

    def test_parity_rejects_reported_pass_with_native_pad_drift(self):
        report = {"status": "pass", "errors": [],
                  "source_library_sha256": {"fixture": "1" * 64}, "copper_polygon_error_mm": .001,
                  "summary": {"native_footprints": 2, "checked_footprints": 2,
                              "footprints_with_pad_geometry_drift": 0, "lookup_errors": 0},
                  "boards": [{"project": project, "board": project + ".kicad_pcb", "board_sha256": "2" * 64,
                              "native_footprint_count": 1,
                              "checked_references": ["J1"], "deviations": []}
                             for project in sorted(adapters.PROJECTS)]}
        result = adapters._footprint_result(report)
        self.assertEqual("pass", result["verdict"])
        self.assertEqual(report["source_library_sha256"], result["details"]["source_library_sha256"])
        report["boards"][0]["deviations"] = [{"reference": "J1"}]
        self.assertEqual("fail", adapters._footprint_result(report)["verdict"])

    def test_planar_mechanical_pass_is_separate_from_unqualified_assembly(self):
        report = {"status": "review_required", "errors": [],
                  "fastener_and_planar_checks_status": "pass", "production_release_ready": False,
                  "battery_thermal_contacts": {"physical_contact_proved": False},
                  "connector_fit": {"status": "requires_confirmation"},
                  "geometry": {"mounting_axis_count": 4}}
        result = adapters._mechanical_result(report)
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual("pass", result["details"]["scoped_verdict"])
        changed = copy.deepcopy(report)
        changed["production_release_ready"] = True
        self.assertEqual("unqualified", adapters._mechanical_result(changed)["verdict"])
        report["errors"] = ["mount axis moved"]
        self.assertEqual("fail", adapters._mechanical_result(report)["verdict"])

    def test_nominal_cable_pass_does_not_qualify_all_source_positions(self):
        report = {"status": "pass", "errors": [], "summary": {
            "path_count": 5, "minimum_relaxed_reserve_mm": 5.2,
            "all_source_positions_planar_radius_verified": False}}
        result = adapters._microcoax_result(report)
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual("pass", result["details"]["scoped_verdict"])
        report["summary"]["path_count"] = 4
        self.assertEqual("fail", adapters._microcoax_result(report)["verdict"])

    def test_silk_candidate_is_not_a_proven_failure_or_a_pass(self):
        report = {"status": "review_required", "interface_coverage": {"errors": []},
                  "boards": [{"project": project, "errors": [], "required_count": 1,
                              "matched_count": 1, "geometry_candidates": [{"kind": "bbox"}]}
                             for project in sorted(adapters.PROJECTS)]}
        self.assertEqual("unqualified", adapters._silkscreen_result(report)["verdict"])
        report["boards"][0]["errors"] = ["wrong physical label"]
        self.assertEqual("fail", adapters._silkscreen_result(report)["verdict"])

    def test_sma_geometry_pass_retains_explicit_process_boundary(self):
        report = {"status": "no_candidates_in_screened_scope", "geometry_error_count": 0,
                  "summary": {"connector_count": 10, "pad_count": 50,
                              "native_foreign_pad_contact_count": 0, "screening_candidate_count": 0},
                  "boards": [{"project": project, "errors": []} for project in sorted(adapters.PROJECTS)]}
        result = adapters._sma_result(report)
        self.assertEqual("pass", result["verdict"])
        self.assertFalse(result["details"]["solder_process_qualified"])
        report["summary"]["native_foreign_pad_contact_count"] = 1
        self.assertEqual("fail", adapters._sma_result(report)["verdict"])


if __name__ == "__main__":
    unittest.main()
