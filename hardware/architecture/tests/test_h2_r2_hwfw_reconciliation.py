import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_hwfw_reconciliation.py"
EXPORT = ROOT / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
M1 = ROOT / "hardware/ecad/generated/H2-R2-interboard-m1.json"
AUTHORITY = ROOT / "hardware/architecture/generated/H0-R2-authority-gate.json"


class H2R2HardwareFirmwareReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = json.loads(EXPORT.read_text(encoding="utf-8"))
        cls.m1 = json.loads(M1.read_text(encoding="utf-8"))
        cls.authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))

    def test_generator_is_current(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("6 domains, 173 controller pins", result.stdout)

    def test_every_controller_pin_resolves_exactly_or_at_a_named_boundary(self):
        self.assertEqual("pass", self.export["status"])
        self.assertEqual([], self.export["errors"])
        rows = self.export["r2_reconciliation"]["pin_reconciliation"]
        self.assertEqual(173, len(rows))
        self.assertEqual(
            {"exact", "conditioned_boundary", "explicit_no_connect"},
            {row["resolution"] for row in rows},
        )
        self.assertEqual(14, sum(row["resolution"] == "conditioned_boundary" for row in rows))
        self.assertFalse([row for row in rows if row["resolution"] == "mismatch"])

    def test_every_cross_project_net_uses_a_registered_connector_pair(self):
        rows = self.export["r2_reconciliation"]["cross_project_nets"]
        self.assertEqual(51, len(rows))
        self.assertTrue(all(row["boundary_evidence"] for row in rows))
        for row in rows:
            for boundary in row["boundary_evidence"]:
                self.assertEqual(2, len(boundary["endpoint_instances"]), row)

    def test_cross_sheet_counts_match_native_projects(self):
        self.assertEqual(
            {
                "LESHY2-UI-R2": 110,
                "LESHY2-RF-R2": 126,
                "L2-DISP-ADP-001-B": 0,
            },
            self.export["r2_reconciliation"]["native_kicad"]["cross_sheet_net_counts"],
        )
        self.assertEqual(236, self.export["summary"]["cross_sheet_net_count"])

    def test_exact_80_contact_m1_and_current_authority_pass(self):
        self.assertEqual(80, self.m1["summary"]["physical_contacts"])
        self.assertEqual(10, self.m1["summary"]["no_connect_reserve_contacts"])
        self.assertEqual(10, self.m1["summary"]["explicit_reserve_class_contacts"])
        self.assertEqual([], self.m1["errors"])
        self.assertEqual("pass_current_r2_h2_reconciled", self.authority["status"])
        self.assertTrue(self.authority["r2_h2_authoritative"])
        self.assertTrue(all(self.authority["r2_h2_compatibility"].values()))

    def test_authorization_stops_before_layout_or_order(self):
        self.assertTrue(self.export["authorization"]["hardware_firmware_machine_authority"])
        self.assertFalse(self.export["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(self.export["authorization"]["fabrication"])
        self.assertFalse(self.export["authorization"]["ordering"])


if __name__ == "__main__":
    unittest.main()
