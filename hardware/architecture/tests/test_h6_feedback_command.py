"""Selector/adapter tests; passing these does not qualify the current circuit."""

from contextlib import redirect_stdout
from copy import deepcopy
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
import synthesize_main_feedback as tool

I = tool.Interval


class FeedbackCommandTest(unittest.TestCase):
    def evaluate(self, minimum, maximum, chooser, factors=None, leakage=None):
        return tool.evaluate(I(1, 1), I(1000, 1000), factors or I(1, 1),
                             minimum, maximum, leakage or I(0, 0), chooser)

    def test_future_feasible_input_does_not_expect_present_infeasibility(self):
        result = self.evaluate(2, 3, lambda _: F(1500))
        self.assertEqual(result["status"], "conditional_candidate")
        self.assertFalse(result["qualified"])
        self.assertEqual(result["average_v_exact"], ["5/2", "5/2"])

    def test_infeasible_input_does_not_call_selector(self):
        def forbidden(_):
            self.fail("an infeasible interval must not reach EDG")
        result = self.evaluate("1.99", "2.01", forbidden, factors=I(".9", "1.1"))
        self.assertEqual(result["status"], "conditional_infeasible")
        self.assertIsNone(result["selected_nominal_ohm"])

    def test_no_discrete_result_is_not_reported_as_continuous_infeasibility(self):
        result = self.evaluate("2.0001", "2.0002", lambda _: None)
        self.assertTrue(result["continuous_feasible"])
        self.assertEqual(result["status"], "preferred_selector_found_no_candidate")

    def test_selector_candidates_at_inclusive_bounds(self):
        for nominal in (F(1000), F(2000)):
            result = self.evaluate(2, 3, lambda _: nominal)
            self.assertEqual(result["status"], "conditional_candidate")

    def test_bad_or_outside_candidates_are_execution_errors_not_results(self):
        for value in (F(999), F(2001), F(0), F(-1), True, 1000, 1000.0, "1000"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.evaluate(2, 3, lambda _: value)

    def test_unbounded_domain_is_not_sent_to_arbitrary_catalog_search(self):
        result = self.evaluate(1, 1, lambda _: self.fail("unbounded search"), leakage=I("-.001", "-.001"))
        self.assertEqual(result["status"], "unsupported_search_domain")

    def test_report_mutations_fail_including_deleted_hash_and_load_case(self):
        current = {"source_sha256": {"one": "abc", "two": "def"},
                   "profile_voltage_corners": [{"load_case": "one"}, {"load_case": "two"}]}
        tool.verify_regenerated_report(deepcopy(current), current)
        for mutate in (lambda x: x["source_sha256"].pop("one"),
                       lambda x: x["source_sha256"].clear(),
                       lambda x: x["profile_voltage_corners"].pop(),
                       lambda x: x["profile_voltage_corners"].append(x["profile_voltage_corners"][0]),
                       lambda x: x["source_sha256"].update(one="stale")):
            saved = deepcopy(current)
            mutate(saved)
            with self.assertRaises(ValueError):
                tool.verify_regenerated_report(saved, current)

    def test_error_cannot_publish_old_success_path(self):
        stream = StringIO()
        with patch.object(tool, "run", side_effect=ValueError("stale")), redirect_stdout(stream):
            self.assertEqual(tool.main(), 2)
        result = json.loads(stream.getvalue())
        self.assertEqual(result["status"], "execution_error")
        self.assertIsNone(result["report"])

    def test_current_source_adapter_covers_profiles_and_declared_targets(self):
        data = tool.load_current()
        self.assertEqual(max(current for _, current in data["cases"]), F("4.25"))
        self.assertGreater(len(data["cases"]), 2)
        self.assertEqual(data["before"], tool.snapshot(data["paths"]))


@unittest.skipUnless(importlib.util.find_spec("edg"), "prepared EDG runtime needed")
class EdgSelectorIntegrationTest(unittest.TestCase):
    def test_exact_decade_point_is_not_dropped_by_edg_power_range(self):
        for nominal in (1, 10, 100, 1000, 10000, 100000):
            with self.subTest(nominal=nominal):
                result = tool.evaluate(I(1, 1), I(nominal, nominal), I(1, 1), 2, 2, I(0, 0))
                self.assertEqual(F(result["selected_nominal_ohm"]), nominal)

    def test_search_halo_cannot_accept_nominal_outside_exact_requirements(self):
        with self.assertRaisesRegex(ValueError, "independent exact forward check"):
            tool.evaluate(I(1, 1), I(1000, 1000), I(1, 1),
                          "2.0000000000001", "2.0000000000002", I(0, 0))

    def test_actual_edg_has_no_nominal_in_a_tiny_gap(self):
        result = tool.evaluate(I(1, 1), I(1000, 1000), I(1, 1), "2.0001", "2.0002", I(0, 0))
        self.assertEqual(result["status"], "preferred_selector_found_no_candidate")

    def test_current_full_requirements_are_not_satisfied_by_partial_candidate(self):
        report = tool.run()
        self.assertEqual(report["full_requirements"]["status"], "conditional_infeasible")
        self.assertIsNone(report["full_requirements"]["selected_nominal_ohm"])
        self.assertEqual(report["raw_only_diagnostic_not_a_solution"]["status"], "conditional_candidate")
        self.assertFalse(report["qualified"])

    def test_source_change_during_run_is_rejected(self):
        snapshot = tool.snapshot
        calls = 0

        def changed(paths):
            nonlocal calls
            calls += 1
            values = snapshot(paths)
            if calls > 1:
                values["injected-source-change"] = "new"
            return values

        with patch.object(tool, "snapshot", changed), self.assertRaisesRegex(ValueError, "sources changed"):
            tool.run()


if __name__ == "__main__":
    unittest.main()
