import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from hardware.layout.h6_r2_routing_drc_delta import item_net, violation_fingerprint
from hardware.layout.h6_r2_routing_session import placement_rounding, session_nets


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
SCRIPT = ROOT / "hardware/layout/h6_r2_routing_policy.py"
RULES_SCRIPT = ROOT / "hardware/layout/h6_r2_kicad_rules.py"
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
        self.assertEqual(
            {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"},
            set(self.audit["automatic_helper"]["routable_layers"]),
        )
        self.assertEqual(
            {"In1.Cu", "In4.Cu"},
            set(self.audit["automatic_helper"]["reserved_reference_layers"]),
        )
        self.assertGreaterEqual(self.audit["automatic_helper"]["via_costs"], 100)
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
        usb_names = [
            row["kicad_net"]
            for row in self.audit["rows"]
            if row["routing_class"] == "USB_DIFFERENTIAL"
        ]
        self.assertTrue(all(name.endswith(("_P", "_N")) for name in usb_names))
        self.assertEqual(
            {name[:-2] for name in usb_names if name.endswith("_P")},
            {name[:-2] for name in usb_names if name.endswith("_N")},
        )

    def test_stackup_identity_and_core_thickness_are_not_ambiguous(self):
        stack = self.audit["stackup_binding"]
        self.assertEqual("JLC06161H-3313", stack["official_stackup_id"])
        self.assertEqual(1.6, stack["order_thickness_mm"])
        self.assertEqual(1.54, stack["calculator_finished_thickness_mm"])
        self.assertEqual(0.55, stack["core_each_mm"])
        self.assertIn("bound to the current JLCPCB calculator", stack["exact_trace_geometry_status"])
        self.assertEqual(0.134874, stack["outer_layer_geometries"]["RF_50R_CPWG"]["trace_width_mm"])
        self.assertEqual(0.1524, stack["outer_layer_geometries"]["RF_50R_CPWG"]["coplanar_gap_mm"])
        self.assertEqual(0.134874, stack["outer_layer_geometries"]["USB_90R_DIFFERENTIAL"]["trace_width_mm"])
        self.assertEqual(0.1524, stack["outer_layer_geometries"]["USB_90R_DIFFERENTIAL"]["pair_gap_mm"])

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

        rules = subprocess.run(
            ["python3", str(RULES_SCRIPT), "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, rules.returncode, rules.stdout)
        self.assertIn("exact RF/USB outer-layer geometry", rules.stdout)

    def test_kicad_rules_bind_exact_calculator_geometry(self):
        for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
            path = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_dru"
            text = path.read_text(encoding="utf-8")
            self.assertIn("JLC06161H-3313", text)
            self.assertIn("5.31mil width 6.00mil gap", text)
            self.assertIn("(constraint track_width (min 5.31mil) (opt 5.31mil) (max 5.31mil))", text)
            self.assertIn("(constraint diff_pair_gap (min 6.00mil) (opt 6.00mil) (max 6.00mil))", text)
            self.assertIn('(layer inner)', text)
            self.assertIn('(constraint disallow track via)', text)

    def test_session_and_drc_guards_parse_machine_artifacts(self):
        self.assertEqual(
            {"/UI/ONE", "PLAIN_TWO"},
            session_nets('      (net "/UI/ONE"\n      (net PLAIN_TWO\n'),
        )
        rounded, delta = placement_rounding(
            {"U1": (100, 200, 90.0, True)},
            {"U1": (101, 200, 90.0, True)},
        )
        self.assertEqual(["U1"], rounded)
        self.assertEqual(1, delta)
        self.assertEqual("/UI/ONE", item_net("Track [/UI/ONE] on F.Cu"))
        violation = {
            "type": "clearance",
            "description": "too close",
            "items": [{"uuid": "b"}, {"uuid": "a"}],
        }
        self.assertEqual(
            ("clearance", "too close", ("a", "b")),
            violation_fingerprint(violation),
        )

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
            self.assertEqual(["In1.Cu", "In4.Cu"], manifest["reserved_reference_layers"])
            self.assertEqual(250, manifest["via_costs"])
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
                self.assertIn("(layer_rule In1.Cu\n      (active off)", dsn)
                self.assertIn("(layer_rule In4.Cu\n      (active off)", dsn)
                self.assertIn("(layer_rule In2.Cu\n      (active on)", dsn)
                self.assertIn("(via_costs 250)", dsn)
                self.assertIn("(layer In1.Cu\n      (type power)", dsn)
                self.assertIn("(layer In4.Cu\n      (type power)", dsn)


if __name__ == "__main__":
    unittest.main()
