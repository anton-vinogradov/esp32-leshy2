import importlib.util
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_source_margins.py"


class H3R2SourceMarginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h3_r2_source_margins", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.outputs, cls.manifest = cls.module.build()

    def test_generated_artifacts_are_current(self):
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(content, path.read_text(encoding="utf-8"), path)

    def test_all_deferred_source_pack_lines_have_one_owner(self):
        ownership = self.manifest["ownership"]
        self.assertEqual(77, len(ownership))
        self.assertEqual(77, len({row["instance_uid"] for row in ownership}))
        self.assertIn("pack_source", self.manifest["ownership_summary"]["owner_counts"])
        self.assertEqual(0, self.manifest["summary"]["hidden_miscellaneous_allowances"])

    def test_all_legal_states_are_safe_or_explicitly_refused(self):
        self.assertEqual(2266, self.manifest["summary"]["states_evaluated"])
        self.assertEqual(0, self.manifest["summary"]["failed_states"])
        self.assertEqual(14, self.manifest["summary"]["usb_only_profiles_refused"])
        refused = [row for row in self.manifest["states"] if row["admission"] == "run_profile_refused_on_usb_only"]
        self.assertTrue(refused)
        self.assertTrue(all(row["usb"] == "USB_5V_3A" for row in refused))

    def test_pack_electrical_and_sustained_envelopes_are_distinct(self):
        electrical = self.manifest["extrema"]["maximum_pack_discharge"]
        sustained = self.manifest["extrema"]["maximum_sustained_pack_discharge"]
        self.assertLessEqual(float(electrical["pack_discharge_a"]), 8.0)
        self.assertGreaterEqual(float(electrical["pack_endpoint_v"]), 5.4)
        self.assertLess(float(sustained["pack_discharge_a"]), float(electrical["pack_discharge_a"]))
        self.assertLess(float(sustained["cell_pair_i2r_w"]), float(electrical["cell_pair_i2r_w"]))

    def test_charge_yields_to_system_load_and_fallback_assumes_zero_watts(self):
        self.assertGreater(self.manifest["summary"]["charge_states_derated"], 0)
        fallback = [row for row in self.manifest["states"] if row["usb"] == "USB_5V_FALLBACK"]
        self.assertTrue(fallback)
        self.assertTrue(all(row["usb_raw_budget_w"] is None for row in fallback))
        self.assertTrue(all(row["usb_input_a"] == "0.000" for row in fallback))


if __name__ == "__main__":
    unittest.main()
