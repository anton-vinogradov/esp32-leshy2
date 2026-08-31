import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h3_r2_digital_interfaces.py"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-digital-interfaces.json"


def load_module():
    spec = importlib.util.spec_from_file_location("h3_r2_digital_interfaces", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class H3R2DigitalInterfacesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.result = cls.module.build()

    def test_current_result_passes_and_checked_artifact_matches(self):
        self.assertEqual("pass", self.result["status"])
        self.assertEqual([], self.result["errors"])
        self.assertEqual(self.result, json.loads(OUTPUT.read_text(encoding="utf-8")))

    def test_every_logic_boundary_has_positive_high_and_low_margin(self):
        for row in self.result["logic_level_margins"]:
            self.assertGreater(row["worst_high_margin"], 0, row["boundary"])
            self.assertGreater(row["worst_low_margin"], 0, row["boundary"])

    def test_i8080_uses_exact_safe_divider_and_rejects_old_request(self):
        timing = self.result["display_timing"]
        self.assertEqual(20_000_000, timing["clock"]["actual_hz"])
        self.assertEqual(4, timing["clock"]["integer_prescale"])
        self.assertGreater(timing["clock"]["forbidden_24mhz_request_actual_hz"], 25_000_000)
        self.assertTrue(all(timing["checks"].values()))

    def test_m1_and_service_ownership_are_deterministic(self):
        self.assertTrue(all(self.result["m1"]["checks"].values()))
        self.assertEqual([60, 61, 62, 63, 64, 77, 78, 79, 80], self.result["m1"]["true_nc_contacts"])
        self.assertTrue(all(self.result["usb_and_service_ownership"].values()))

    def test_negative_level_margin_fails_closed(self):
        row = self.module.level_row("negative fixture", self.module.dec("1.9"), self.module.dec("0.9"), self.module.dec("2.0"), self.module.dec("0.8"))
        self.assertEqual("fail", row["status"])
        self.assertLess(row["minimum_margin"], 0)


if __name__ == "__main__":
    unittest.main()
