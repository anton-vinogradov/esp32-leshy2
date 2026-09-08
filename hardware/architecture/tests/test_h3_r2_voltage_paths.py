import copy
import unittest
from decimal import Decimal

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'hardware/verification'))
import h3_r2_rail_margins as model


class VoltageCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.rail = {"nominal_v": "3.3", "raw_average_min_v": "3.25", "raw_average_max_v": "3.4",
                     "ripple_pp_v": ".02", "efuse_ron_max_ohm": ".05", "distribution_drop_v": ".04",
                     "load_min_v": "3.0", "load_max_v": "3.6"}
        self.path = {"raw_net": "RAW", "protected_local_net": "PROTECTED", "consumer_location": "REMOTE",
                     "distribution_scope": "downstream_excludes_protection", "qualified": True,
                     "unqualified_reasons": [], "pg_sense_endpoint": "PG_TOP.1"}

    def calculate(self, load="3000"):
        return model.rail_voltage_result("SYNTHETIC", self.rail, load, load_case="test", voltage_path=self.path)

    def test_three_nodes_and_two_losses_are_independently_expected(self):
        row = self.calculate()
        self.assertEqual("3.240000", row["raw_min_v"])
        self.assertEqual("3.090000", row["protected_local_min_v"])
        self.assertEqual("3.050000", row["consumer_endpoint_min_v"])
        self.assertEqual(["0.150000", "0.040000"], [x["maximum_drop_v"] for x in row["series_path_losses"]])

    def test_tenfold_ron_changes_protected_and_endpoint_not_raw_or_high(self):
        before = self.calculate()
        self.rail["efuse_ron_max_ohm"] = ".5"
        after = self.calculate()
        self.assertEqual("pass", before["status"])
        self.assertEqual("fail", after["status"])
        for key in ("raw_min_v", "raw_max_v", "protected_local_max_v", "consumer_endpoint_max_v"):
            self.assertEqual(before[key], after[key], key)
        for key in ("protected_local_min_v", "consumer_endpoint_min_v"):
            self.assertEqual(Decimal("1.35"), Decimal(before[key]) - Decimal(after[key]), key)

    def test_downstream_loss_cannot_move_pg_sense_voltage(self):
        before = self.calculate()
        self.rail["distribution_drop_v"] = ".2"
        after = self.calculate()
        threshold = Decimal("3.07")
        self.assertEqual(before["protected_local_min_v"], after["protected_local_min_v"])
        self.assertEqual(before["pg_sense_endpoint"], after["pg_sense_endpoint"])
        self.assertTrue(Decimal(after["protected_local_min_v"]) > threshold)
        self.assertTrue(Decimal(before["consumer_endpoint_min_v"]) < threshold)
        self.assertEqual(Decimal(".16"), Decimal(before["endpoint_min_v"]) - Decimal(after["endpoint_min_v"]))

    def test_zero_load_and_full_load_have_same_safe_upper_bound(self):
        zero, full = self.calculate("0"), self.calculate("3000")
        self.assertEqual(zero["raw_min_v"], zero["protected_local_min_v"])
        self.assertEqual("0.000000", zero["series_path_losses"][0]["maximum_drop_v"])
        for row in (zero, full):
            self.assertEqual("3.410000", row["protected_local_max_v"])
            self.assertEqual("3.410000", row["consumer_endpoint_max_v"])

    def test_large_current_loss_does_not_hide_upper_voltage_failure(self):
        self.rail["load_max_v"] = "3.4"
        self.assertFalse(self.calculate()["checks"]["endpoint_below_load_maximum"])

    def test_missing_or_ambiguous_loss_partition_is_rejected(self):
        for value in (None, "includes_efuse", "unknown"):
            self.path["distribution_scope"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "partition"):
                self.calculate()

    def test_missing_negative_nonfinite_ron_or_current_is_not_zeroed(self):
        for field in ("efuse_ron_max_ohm", "distribution_drop_v"):
            old = self.rail[field]
            for value in ("-.1", "NaN", "Infinity", True):
                self.rail[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.calculate()
            del self.rail[field]
            with self.assertRaises(KeyError):
                self.calculate()
            self.rail[field] = old
        for load in ("-1", "NaN", "Infinity", True):
            with self.subTest(load=load), self.assertRaises(ValueError):
                self.calculate(load)

    def test_wrong_main_source_cannot_be_qualified_by_drop_math(self):
        self.rail["source"] = "https://www.ti.com/lit/ds/symlink/tps564252.pdf"
        row = model.rail_voltage_result("3V3_MAIN", self.rail, "100", load_case="test", voltage_path=self.path)
        self.assertEqual("pass", row["numerical_status"])
        self.assertEqual("review_required", row["status"])
        self.assertFalse(row["model_qualified"])
        self.assertIn("TPS566231PRQFR", row["unqualified_reasons"][0])

    def test_unqualified_path_cannot_report_pass_even_when_numbers_pass(self):
        self.path.update(qualified=False, unqualified_reasons=["declared RON not guaranteed for the fitted condition"])
        self.assertEqual("review_required", self.calculate()["status"])
        self.path["qualified"] = True
        with self.assertRaises(ValueError):
            self.calculate()

    def test_actual_profile_loads_and_h0_targets_are_separate_from_thermal(self):
        _, snapshot = model.build()
        self.assertEqual(224, len(snapshot["profile_voltage_corners"]))
        main = snapshot["voltage_corners"]["3V3_MAIN"]
        self.assertEqual("3046.000000", main["load_ma"])
        self.assertEqual("3.145013", main["raw_min_v"])
        self.assertEqual("2.992713", main["protected_local_min_v"])
        self.assertEqual("2.942713", main["endpoint_min_v"])
        self.assertEqual("3.299695", main["endpoint_max_v"])
        self.assertEqual("fail", main["numerical_status"])
        self.assertEqual("review_required", main["status"])
        targets = snapshot["declared_target_voltage_corners"]["3V3_MAIN"]
        self.assertEqual("2.907513", targets["H0_continuous"]["endpoint_min_v"])
        self.assertEqual("2.882513", targets["H0_step_resistive_snapshot_not_transient_proof"]["endpoint_min_v"])
        self.assertFalse(snapshot["production_release_authorized"])

    def test_declared_target_failure_cannot_hide_behind_passing_operating_profiles(self):
        profiles = [{"signal_group": "NONE", "group_mode": "NONE", "support_profile": "SUPPORT_WORST",
                     "loads_ma": {"SYNTHETIC": "3000"}}]
        result = model.voltage_load_cases({"rails": {"SYNTHETIC": self.rail}}, profiles,
                  {"SYNTHETIC": self.path}, {"SYNTHETIC": {"declared_step": "10000"}})
        self.assertEqual("pass", result["voltage_corners"]["SYNTHETIC"]["status"])
        self.assertEqual("fail", result["status"])
        self.assertEqual(["SYNTHETIC:declared_step"], result["voltage_numerical_failures"])


if __name__ == "__main__":
    unittest.main()
