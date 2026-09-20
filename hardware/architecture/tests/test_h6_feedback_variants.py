"""Full-demand variant comparison checks, separate from the EDG pair solver."""

from contextlib import nullcontext, redirect_stdout
from copy import deepcopy
from decimal import Decimal as D
from fractions import Fraction as F
import importlib.util
from io import StringIO
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import compare_main_feedback as tool


class VariantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(tool.VARIANTS.read_text())
        cls.data = tool.source.load_current()

    def test_requirement_cannot_be_overridden_inside_variant(self):
        for key, value in (("load_min_v", "2.8"), ("load_max_v", "3.5"), ("load_a", "0"),
                           ("ripple_pp_v", "0"), ("qualified", True)):
            config = deepcopy(self.config)
            config["variants"][1][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "may not override"):
                tool.validate_variants(config)

    def test_negative_boolean_nonfinite_and_float_loss_budgets_fail(self):
        for value in ("-0.01", True, False, "NaN", "Infinity", 0.01, None):
            for key in ("efuse_ron_ohm", "distribution_drop_v"):
                config = deepcopy(self.config)
                config["variants"][1][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    tool.validate_variants(config)

    def test_missing_baseline_duplicate_ids_and_search_domains_fail(self):
        mutations = [lambda c: c["variants"].pop(0),
                     lambda c: c["variants"].append(deepcopy(c["variants"][0])),
                     lambda c: c.update(series=True),
                     lambda c: c.update(parallel_impedance_ohm=["0", "10000"]),
                     lambda c: c.update(parallel_impedance_ohm=["10000", "5000"]),
                     lambda c: c["variants"][0].update(efuse_ron_ohm="0.001")]
        for mutation in mutations:
            config = deepcopy(self.config)
            mutation(config)
            with self.assertRaises(ValueError):
                tool.validate_variants(config)

    def test_source_requirements_and_inputs_are_not_mutated(self):
        original = deepcopy(self.data)
        config = deepcopy(self.config)
        demand = tool.demands(self.data)
        result = tool.compare(self.data, config, pair_solver=lambda *a, **kw: {
            "status": "preferred_selector_found_no_candidate", "qualified": False})
        self.assertEqual(original, self.data)
        self.assertEqual(config, self.config)
        self.assertEqual(result["invariant_demands"]["consumer_min_v"], str(demand["consumer_min_v"]))
        self.assertEqual(result["invariant_demands"]["load_cases_a"], [[n, str(i)] for n, i in self.data["cases"]])

    def test_required_average_uses_declared_peak_not_only_operating_profile(self):
        demand = tool.demands(self.data)
        self.assertEqual(tool.required_average(demand, D(".05"), D(".05")), (D("3.2725"), D("3.29")))
        self.assertEqual(tool.required_average(demand, D(".02"), D(".03")), (D("3.125"), D("3.29")))

    def test_consumer_checker_catches_full_requirement_failure(self):
        demand = tool.demands(self.data)
        with self.assertRaisesRegex(ValueError, "consumer"):
            tool.check_consumers(("3.13", "3.26"), demand, D(".05"), D(".05"))
        result = tool.check_consumers(("3.13", "3.26"), demand, D(".02"), D(".03"))
        self.assertEqual(F(result["lower_margin_v_exact"]), F(".005"))
        self.assertEqual(result["checked_load_cases"], len(self.data["cases"]))
        with self.assertRaisesRegex(ValueError, "raw voltage"):
            tool.check_consumers(("3.28", "3.291"), demand, D(".02"), D(".03"))

    def test_reference_uncertainty_alone_proves_ideal_resistors_cannot_fix_baseline(self):
        # Independent ideal-divider condition: same fixed gain must be >=
        # required_low/Vref_low and <= required_high/Vref_high.
        self.assertGreater(F("3.2725") / F(".591"), F("3.29") / F(".609"))
        result = tool.compare(self.data, self.config, pair_solver=lambda *a, **kw: {
            "status": "preferred_selector_found_no_candidate", "qualified": False})
        rows = {r["id"]: r for r in result["variants"]}
        self.assertEqual(rows["ideal_resistors_only"]["selection"]["status"], "conditional_infeasible")
        self.assertEqual(rows["ideal_reference_only"]["selection"]["status"], "conditional_infeasible")
        self.assertFalse(rows["current"]["qualified"])

    def test_execution_error_cannot_return_previous_report(self):
        output = StringIO()
        with patch.object(tool, "run", side_effect=ValueError("evidence drift")), \
                patch.object(tool, "keep_awake", return_value=nullcontext()), redirect_stdout(output):
            self.assertEqual(tool.main(), 2)
        self.assertIsNone(json.loads(output.getvalue())["report"])

    def test_cancellation_uses_owned_sleep_scope_and_returns_no_report(self):
        output = StringIO()
        with patch.object(tool, "run", side_effect=KeyboardInterrupt()), \
                patch.object(tool, "keep_awake", return_value=nullcontext()) as awake, redirect_stdout(output):
            self.assertEqual(tool.main(), 130)
        awake.assert_called_once()
        self.assertEqual(json.loads(output.getvalue())["status"], "cancelled")
        self.assertIsNone(json.loads(output.getvalue())["report"])


@unittest.skipUnless(importlib.util.find_spec("edg"), "prepared EDG runtime needed")
class VariantIntegrationTest(unittest.TestCase):
    def test_real_edg_compares_seven_hypotheses_and_checks_each_load_case(self):
        report = tool.run()
        rows = {r["id"]: r for r in report["variants"]}
        self.assertEqual(len(rows), 7)
        self.assertEqual(report["status"], "not_qualified")
        for name in ("current", "ideal_resistors_only", "ideal_reference_only", "zero_distribution_loss"):
            self.assertEqual(rows[name]["selection"]["status"], "conditional_infeasible")
        for name in ("ideal_feedback", "zero_efuse_loss", "low_loss_sourcing_target"):
            row = rows[name]
            self.assertEqual(row["selection"]["status"], "conditional_candidate")
            self.assertFalse(row["qualified"])
            self.assertFalse(row["selection"]["qualified"])
            self.assertEqual(row["consumer_check"]["checked_load_cases"], 58)
            self.assertGreaterEqual(F(row["consumer_check"]["lower_margin_v_exact"]), 0)
            self.assertGreaterEqual(F(row["consumer_check"]["upper_raw_margin_v_exact"]), 0)

    def test_changed_source_cannot_publish_candidate(self):
        snapshot = tool.source.snapshot
        calls = 0

        def changed(paths):
            nonlocal calls
            calls += 1
            result = snapshot(paths)
            if calls == 4:
                result["injected-change"] = "invalid"
            return result

        with patch.object(tool.source, "snapshot", changed), self.assertRaisesRegex(ValueError, "source changed"):
            tool.run()


if __name__ == "__main__":
    unittest.main()
