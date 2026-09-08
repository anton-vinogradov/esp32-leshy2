"""Keep datasheet typical values distinct from specified safety bounds."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class SupervisorSourceLimitsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.device = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]["ti_tps3808g33_dbvr"]
        cls.limits = cls.device["electrical_contract"]

    def test_fixed_hysteresis_has_no_published_minimum(self):
        self.assertEqual({"min": None, "typ": 1.0, "max": 2.5},
                         self.limits["fixed_threshold_hysteresis_percent"])

    def test_sense_assertion_is_typical_not_a_guaranteed_maximum(self):
        self.assertIsNone(self.limits["sense_to_reset_assertion_max_us"])
        timing = self.limits["sense_to_reset_assertion_us"]
        self.assertEqual({"min": None, "typ": 20, "max": None},
                         {key: timing[key] for key in ("min", "typ", "max")})
        for condition in ("1.05*VIT", "0.95*VIT", "100kohm", "50pF", "TJ=25C"):
            self.assertIn(condition, timing["conditions"])

    def test_reset_release_bounds_are_not_confused_with_assertion_time(self):
        self.assertEqual("open", self.limits["ct_configuration"])
        self.assertEqual({"min": 12, "typ": 20, "max": 28}, self.limits["reset_delay_ms"])
        self.assertEqual(3.07, self.limits["fixed_threshold_nominal_v"])
        self.assertEqual(1.5, self.limits["fixed_threshold_accuracy_percent_full_temperature"])

    def test_exact_component_and_primary_revision_are_preserved(self):
        self.assertEqual("TPS3808G33DBVR", self.device["mpn"])
        self.assertEqual("https://www.ti.com/lit/ds/symlink/tps3808.pdf", self.device["source"]["url"])
        self.assertEqual("SBVS050N", self.limits["limit_classification_review"]["source_revision"])
        self.assertEqual(["6.5, page 6", "6.6, page 7"], self.limits["limit_classification_review"]["sections"])


if __name__ == "__main__":
    unittest.main()
