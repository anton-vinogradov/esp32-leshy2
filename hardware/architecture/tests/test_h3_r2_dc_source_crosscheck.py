import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_dc_source_crosscheck.py"


class H3R2DcSourceCrosscheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h3_r2_dc_source_crosscheck", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.outputs, cls.manifest = cls.module.build()

    def test_generated_artifacts_are_current(self):
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)

    def test_all_cross_checks_pass(self):
        self.assertEqual(15, len(self.manifest["checks"]))
        self.assertTrue(all(self.manifest["checks"].values()))
        self.assertEqual(
            "reviewed_h3_r2_1_worst_case_dc_source_charge_and_power_states",
            self.manifest["status"],
        )

    def test_full_ownership_partition_is_reconciled(self):
        coverage = self.manifest["coverage"]
        self.assertEqual(2266, coverage["legal_states"])
        self.assertEqual(56, coverage["operating_profiles"])
        self.assertEqual(224, coverage["rail_profiles"])
        self.assertEqual(619, coverage["physical_and_external_loads"])
        self.assertEqual(544, coverage["direct_numeric_rail_owners"])
        self.assertEqual(75, coverage["source_pack_owners"])

    def test_published_result_and_authorization_boundary(self):
        result = self.manifest["result"]
        self.assertEqual("30.560", result["minimum_rail_current_reserve_percent"])
        self.assertEqual("3.516", result["maximum_pack_discharge_a"])
        self.assertEqual(14, result["usb_only_profiles_refused"])
        self.assertFalse(any(self.manifest["authorization"].values()))
        self.assertEqual("H3-R2.2.1", self.manifest["next"]["marker"])


if __name__ == "__main__":
    unittest.main()
