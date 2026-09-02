import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_rail_margins.py"
RESULT = REPO / "hardware/verification/generated/H3-R2-rail-margins.json"


class H3R2RailMarginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h3_r2_rail_margins", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.outputs, cls.manifest = cls.module.build()

    def test_generated_artifacts_are_current(self):
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)

    def test_every_load_line_has_one_owner(self):
        summary = self.manifest["ownership_summary"]
        self.assertEqual(629, summary["physical_and_external_lines"])
        self.assertEqual(629, summary["numeric_or_deferred_owner_lines"])
        self.assertEqual(0, summary["unowned_lines"])
        self.assertEqual(0, summary["hidden_miscellaneous_allowances"])

    def test_current_voltage_and_steady_thermal_margins_pass(self):
        self.assertTrue(all(row["status"] == "pass" for row in self.manifest["worst_current_by_rail"].values()))
        self.assertTrue(all(row["status"] == "pass" for row in self.manifest["voltage_corners"].values()))
        self.assertTrue(all(row["status"] == "pass" for row in self.manifest["steady_thermal_by_rail"].values()))

    def test_r2_main_rail_uses_real_four_amp_converter(self):
        main = self.manifest["worst_current_by_rail"]["3V3_MAIN"]
        self.assertEqual("4.000", main["converter_min_a"])
        self.assertEqual("3046.000", main["load_ma"])
        self.assertIn("3PTX", main["profile"])
        self.assertEqual("154.000", main["margin_to_pf03_boundary_ma"])

    def test_external_port_separates_electrical_and_sustained_limits(self):
        electrical = self.manifest["worst_current_by_rail"]["5V_EXT_ACTIVE_BRANCH"]
        thermal = self.manifest["steady_thermal_by_rail"]["5V_EXT_ACTIVE_BRANCH"]
        self.assertEqual("1250.000", electrical["load_ma"])
        self.assertEqual("1000.000", thermal["sustained_load_ma"])
        self.assertGreaterEqual(float(thermal["converter_junction_margin_c"]), 20.0)


if __name__ == "__main__":
    unittest.main()
