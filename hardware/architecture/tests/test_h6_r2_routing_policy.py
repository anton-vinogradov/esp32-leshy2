import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_routing_policy.py"
WORKSPACE_SCRIPT = ROOT / "hardware/layout/h6_r2_routing_workspace.py"
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
        self.assertEqual(858, self.audit["summary"]["project_net_count"])
        self.assertEqual(823, self.audit["summary"]["global_canonical_net_count"])
        self.assertEqual(0, self.audit["summary"]["unclassified_net_count"])
        self.assertEqual(0, self.audit["summary"]["unexpected_net_count"])
        self.assertEqual(858, sum(self.audit["class_counts"].values()))

    def test_automatic_helper_is_fail_closed(self):
        self.assertEqual(["GENERAL_CONTROL"], self.audit["automatic_helper"]["allowed_classes"])
        protected = set(self.audit["automatic_helper"]["locked_or_ignored_classes"])
        self.assertEqual(set(self.contract["classes"]) - {"GENERAL_CONTROL"}, protected)
        for row in self.audit["rows"]:
            if row["routing_class"] != "GENERAL_CONTROL":
                self.assertFalse(row["route_mode"].startswith("automatic"), row["canonical_net"])

    def test_usb_and_display_groups_are_exact(self):
        self.assertEqual(12, self.audit["summary"]["usb_pair_count"])
        self.assertEqual(4, self.audit["summary"]["external_usb_port_count"])
        self.assertEqual(10, self.audit["summary"]["display_i8080_net_count"])
        display = {row["canonical_net"] for row in self.audit["rows"] if row["routing_class"] == "DISPLAY_I8080"}
        self.assertEqual({"LCD_DC", "LCD_WR_N", *(f"LCD_DB{i}" for i in range(8))}, display)
        self.assertTrue(all(row["routing_class"] == "USB_DIFFERENTIAL" for row in self.audit["rows"] if "USB_DM" in row["canonical_net"] or "USB_DP" in row["canonical_net"] or row["canonical_net"].startswith(("USB2_DM", "USB2_DP"))))

    def test_stackup_identity_and_core_thickness_are_not_ambiguous(self):
        stack = self.audit["stackup_binding"]
        self.assertEqual("JLC06161H-3313", stack["official_stackup_id"])
        self.assertEqual(1.6, stack["finished_thickness_mm"])
        self.assertEqual(0.55, stack["core_each_mm"])
        self.assertIn("pending H6.0.4", stack["exact_trace_geometry_status"])

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


if __name__ == "__main__":
    unittest.main()
