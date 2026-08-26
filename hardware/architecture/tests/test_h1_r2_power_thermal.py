import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/product-design/h1_r2_power_thermal.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_power_thermal", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2PowerThermalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = MODULE.load()
        cls.audit = MODULE.audit(cls.model)

    def test_six_domains_and_every_signal_group_are_bounded(self):
        self.assertEqual(6, len(self.model["six_compute_domains"]))
        self.assertEqual(12, len(self.audit["groups"]))
        self.assertEqual("AIRBAND_RX", self.audit["worst_main_group"]["group"])
        self.assertEqual("pass_architecture_with_h3_dynamic_thermal_gate", self.audit["status"])
        self.assertFalse(self.audit["failures"])

    def test_main_rail_meets_the_rebaseline_contract(self):
        margin = self.audit["main_margin"]
        self.assertGreaterEqual(margin["accepted_continuous_a"], 3.5)
        self.assertGreaterEqual(margin["accepted_step_a"], 4.0)
        self.assertGreater(margin["continuous_margin_a"], 0.9)
        self.assertGreaterEqual(self.audit["efuse_threshold_a"]["guaranteed_minimum"], margin["accepted_step_a"])

    def test_switching_parts_have_real_current_headroom(self):
        cell = self.model["main_power_cell"]
        self.assertGreater(cell["inductor"]["saturation_rating_a"], cell["converter"]["valley_current_limit_a"]["maximum"])
        self.assertGreater(cell["inductor"]["rms_rating_a"], self.audit["main_margin"]["accepted_continuous_a"])
        self.assertLess(self.audit["efuse_threshold_a"]["guaranteed_maximum"], cell["converter"]["valley_current_limit_a"]["minimum"])

    def test_factory_selected_parts_have_exact_identity_and_route(self):
        cell = self.model["main_power_cell"]
        for key in ("converter", "inductor", "efuse", "efuse_threshold_resistor", "input_capacitors", "vcc_capacitor", "bootstrap_capacitor", "bootstrap_link"):
            row = cell[key]
            self.assertTrue(row["mpn"])
            self.assertTrue(row["manufacturer"])
            self.assertTrue(row["jlcpcb_part"].startswith("C"))
            self.assertIn("pieces", row["availability"])

    def test_thermal_claim_is_a_gate_not_an_unproved_prediction(self):
        bounds = self.audit["thermal_bounds"]
        self.assertLessEqual(bounds["required_converter_efficiency_at_admitted_continuous"], 0.90)
        self.assertIn("not a predicted value", bounds["interpretation"])
        self.assertGreaterEqual(len(self.audit["h3_required_evidence"]), 5)

    def test_generated_artifacts_are_current(self):
        expected = {
            MODULE.AUDIT_PATH: json.dumps(self.audit, indent=2, ensure_ascii=False) + "\n",
            MODULE.SVG_PATH: MODULE.render_svg(self.model, self.audit),
            MODULE.EN_DOC_PATH: MODULE.render_doc(self.model, self.audit, False),
            MODULE.RU_DOC_PATH: MODULE.render_doc(self.model, self.audit, True),
        }
        for path, content in expected.items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
