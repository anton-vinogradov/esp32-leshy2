"""Conditional current-limit arithmetic and source integrity, not circuit proof."""
from contextlib import nullcontext, redirect_stdout
from copy import deepcopy
from decimal import Decimal
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
import compare_main_current_limit as tool

# Explicit dependency injection for pure unit tests, not a production E192
# replacement. The installed-runtime test below checks the actual pinned table.
TEST_TABLE = tuple(F(1) + F(i, 100) for i in range(192))


class CurrentLimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = tool.load_current()
        cls.inputs = {key: json.loads((ROOT / path).read_text(), parse_float=Decimal)
                      for key, path in tool.power.INPUTS.items()}

    def test_current_inputs_and_separate_existing_findings(self):
        current = self.current
        self.assertEqual(F("4.25"), current["required_lower_a"])
        self.assertEqual(F("3.8075"), F(current["requirements_a"]["pf03_reserve_a"]))
        self.assertEqual(F("3.117079"), F(current["requirements_a"]["existing_inrush_a"]))
        for ident in ("main_pg_resistor_only_window_feasible", "aon_ron_test_condition_binding",
                      "h3_converter_source_is_installed_part"):
            self.assertIn(ident, current["baseline_power_review"]["findings"])
        self.assertEqual(current["source_sha256"], tool.snapshot(tool.source_paths()))

    def test_fitted_and_h1_drift_cases_remain_distinct(self):
        rows = tool.compare(self.current, lambda _: F(1150))["comparisons"]
        by_key = {(r["id"], r["budget"]): r for r in rows}
        initial = "initial_plus_tcr"
        stress = "additional_solder_and_load_life_diagnostic"
        self.assertFalse(by_key["current_fitted", initial]["numerical_constraints_met"])
        self.assertTrue(by_key["h1_intended_not_fitted", initial]["numerical_constraints_met"])
        self.assertFalse(by_key["h1_intended_not_fitted", stress]["numerical_constraints_met"])
        for row in rows:
            if row["id"].startswith("synthesized_for_"):
                self.assertTrue(row["numerical_constraints_met"])
            self.assertFalse(row["qualified"])
        self.assertAlmostEqual(float(F(by_key["h1_intended_not_fitted", stress]["current_a_exact"][0])),
                               4.211921853184821)

    def test_exact_strict_upper_bound_not_valley_limit(self):
        spec = {**self.current["spec"], "initial_tolerance_fraction": "0",
                "tcr_ppm_per_c": "0", "gain_tolerance_fraction": "0", "equation_constant_a_ohm": "6000"}
        window = tool.inverse(3, 6, spec, ())
        self.assertEqual((F(1000), F(2000)), (window.minimum_ohm, window.maximum_ohm))
        self.assertFalse(tool.forward(1000, spec, (), 3, 6)["numerical_constraints_met"])
        self.assertTrue(tool.forward(2000, spec, (), 3, 6)["numerical_constraints_met"])
        current = {**self.current, "spec": spec, "required_lower_a": F(3)}
        with patch.dict(tool.BUDGETS, {"initial": ()}, clear=True):
            with self.assertRaisesRegex(ValueError, "open/closed"):
                tool.compare(current, lambda _: F(1000))
            self.assertEqual("2000", tool.compare(current, lambda _: F(2000))["selections"][0]["selected_nominal_ohm"])

    def test_open_point_window_is_empty(self):
        spec = {**self.current["spec"], "initial_tolerance_fraction": "0",
                "tcr_ppm_per_c": "0", "gain_tolerance_fraction": "0"}
        data = {**self.current, "spec": spec, "required_lower_a": F(6)}
        result = tool.compare(data, lambda _: self.fail("empty open interval reached EDG"))
        self.assertTrue(all(not r["continuous_feasible"] for r in result["selections"]))

    def test_none_from_selector_is_not_infeasibility(self):
        rows = tool.compare(self.current, lambda _: None)["selections"]
        self.assertTrue(all(r["continuous_feasible"] for r in rows))
        self.assertTrue(all(r["status"] == "preferred_selector_found_no_candidate" for r in rows))

    def test_selector_type_range_and_independent_forward_fail_closed(self):
        for bad in (True, 1150, 1150.0, "1150", F(0), F(1060), F(1650)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                tool.compare(self.current, lambda _: bad)
        # Corrupt only the inverse proposal bounds; the independent forward gate remains.
        with patch.object(tool, "inverse", return_value=tool.NominalWindow(F(1000), F(2000))):
            with self.assertRaisesRegex(ValueError, "independent forward"):
                tool.compare(self.current, lambda _: F(1650))

    def test_finite_positive_bounds_and_accuracy_domain_are_required(self):
        for bad in (True, 4.25, "NaN", "Infinity", "-1", "0"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                tool.inverse(bad, 6, self.current["spec"], ())
        with self.assertRaisesRegex(ValueError, "accuracy domain"):
            tool.forward(10000, self.current["spec"], (), F(1), F(6))
        with self.assertRaisesRegex(ValueError, "decimal kernel"):
            tool.forward(F(10000, 3), self.current["spec"], (), F(1), F(6))

    def test_requirement_mutations_cannot_relax_admission(self):
        mutations = [
            lambda d: d["h3"]["policy"].update(steady_current_reserve_minimum_percent=20),
            lambda d: d["h0"]["power_rebaseline"]["h1_required_envelope"].update(step_a_min=3),
            lambda d: d["h3"]["rails"]["3V3_MAIN"]["conditioned_model"]["converter_current"].update(rated_output_a="6.1"),
            lambda d: d["inrush"]["startup_envelopes"].append(deepcopy(next(r for r in d["inrush"]["startup_envelopes"] if r["rail"] == "3V3_MAIN"))),
            lambda d: d["inrush"].update(startup_envelopes=[r for r in d["inrush"]["startup_envelopes"] if r["rail"] != "3V3_MAIN"]),
        ]
        for mutate in mutations:
            data = deepcopy(self.inputs)
            mutate(data)
            with self.assertRaises(ValueError):
                tool.extract(data, self.current["baseline_power_review"])
        with self.assertRaisesRegex(ValueError, "6 A continuous"):
            tool.compare({**self.current, "strict_upper_a": F("6.1")}, lambda _: F(1150))

    def test_missing_stale_or_deleted_baseline_source_membership_fails(self):
        for mutation in ("delete", "stale", "empty"):
            report = deepcopy(self.current["baseline_power_review"])
            key = next(iter(report["source_sha256"]))
            if mutation == "delete": del report["source_sha256"][key]
            elif mutation == "stale": report["source_sha256"][key] = "0" * 64
            else: report["source_sha256"] = {}
            with self.subTest(mutation=mutation), patch.object(tool.power, "build", return_value=report):
                with self.assertRaisesRegex(ValueError, "baseline power source"):
                    tool.load_current()

    def test_actual_topology_rewire_is_rejected(self):
        data = {key: json.loads((ROOT / p).read_text()) for key, p in tool.power.INPUTS.items()}
        next(r for r in data["nets"]["rows"] if r["endpoint"] == "main_efuse_rilm.END_2")["net"] = "3V3_MAIN"
        report = tool.power.evaluate(data)
        report["source_sha256"] = self.current["baseline_power_review"]["source_sha256"]
        with patch.object(tool.power, "build", return_value=report):
            with self.assertRaisesRegex(ValueError, "topology"):
                tool.load_current()

    def test_stale_regenerated_inrush_is_rejected(self):
        build = tool.inrush.build
        def changed():
            outputs, result, transition = build()
            result["startup_envelopes"].pop()
            return outputs, result, transition
        with patch.object(tool.inrush, "build", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "differs from current"):
                tool.load_current()

    def test_missing_path_and_source_change_are_rejected(self):
        paths = tool.source_paths()
        with patch.object(tool, "source_paths", return_value=paths + [ROOT / "missing-current-limit-source"]):
            with self.assertRaisesRegex(ValueError, "missing"):
                tool.load_current()
        data = deepcopy(self.current)
        with patch.object(tool, "load_current", return_value=data), patch.object(tool, "snapshot", return_value={}):
            with self.assertRaisesRegex(ValueError, "sources changed"):
                tool.run(lambda _: F(1150), lambda: TEST_TABLE)

    def test_output_keeps_baseline_unqualified_and_does_not_mutate_inputs(self):
        before = deepcopy(self.current)
        with patch.object(tool, "load_current", return_value=self.current):
            result = tool.run(lambda _: F(1150), lambda: TEST_TABLE)
        self.assertEqual(before, self.current)
        self.assertEqual(before["baseline_power_review"], result["baseline_power_review"])
        self.assertEqual("not_qualified", result["status"])
        for flag in ("qualified", "production_mpn_selected", "startup_proven", "gate_closed"):
            self.assertIs(result[flag], False)
        self.assertFalse(result["portfolio_selection"]["qualified"])
        self.assertEqual(list(tool.BUDGETS), result["portfolio_selection"]["budgets"])
        self.assertIn("tools/edg_feedback_pair.py", result["source_sha256"])

    def test_portfolio_complete_enumeration_and_cross_budget_score(self):
        result = tool.portfolio(self.current, TEST_TABLE)
        self.assertEqual([str(v) for v in range(1100, 1170, 10)],
                         [row["nominal_ohm"] for row in result["candidates"]])
        self.assertEqual([3], result["domain"]["decade_exponents"])
        scores = {}
        for row in result["candidates"]:
            self.assertEqual(list(tool.BUDGETS), [c["budget"] for c in row["checks"]])
            self.assertTrue(all(c["numerical_constraints_met"] for c in row["checks"]))
            self.assertTrue(all(c["qualified"] is False for c in row["checks"]))
            scores[row["nominal_ohm"]] = min(F(c[key]) for c in row["checks"]
                for key in ("lower_margin_a_exact", "strict_upper_margin_a_exact"))
            self.assertEqual(scores[row["nominal_ohm"]], F(row["minimum_margin_a_exact"]))
        self.assertEqual(max(scores.values()), F(result["minimum_margin_a_exact"]))
        self.assertEqual(max(scores, key=lambda n: (scores[n], -F(n))), result["selected_nominal_ohm"])
        tool.validate_portfolio(self.current, result, TEST_TABLE)

    def test_portfolio_omitted_best_fabricated_score_budget_and_authority_rejected(self):
        original = tool.portfolio(self.current, TEST_TABLE)
        for mutation in ("omit_best", "score", "selection", "omit_budget", "authority", "boundary", "count"):
            result = deepcopy(original)
            if mutation == "omit_best":
                result["candidates"] = [r for r in result["candidates"]
                                        if r["nominal_ohm"] != result["selected_nominal_ohm"]]
                result["candidate_count"] -= 1
            elif mutation == "score": result["minimum_margin_a_exact"] = "1"
            elif mutation == "selection": result["selected_nominal_ohm"] = "1100"
            elif mutation == "omit_budget": result["candidates"][0]["checks"].pop()
            elif mutation == "authority": result["qualified"] = True
            elif mutation == "boundary": result["domain"]["minimum_exclusive"] = False
            else: result["candidate_count"] += 1
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "exact replay"):
                tool.validate_portfolio(self.current, result, TEST_TABLE)

    def test_portfolio_strict_boundary_closed_floor_and_exact_tie_break(self):
        spec = {**self.current["spec"], "initial_tolerance_fraction": "0",
                "tcr_ppm_per_c": "0", "gain_tolerance_fraction": "0", "equation_constant_a_ohm": "6000"}
        data = {**self.current, "spec": spec, "required_lower_a": F(3)}
        table = tuple([F(1), F("1.2"), F("1.5"), F(2)]
                      + [F(3)+F(i, 100) for i in range(188)])
        with patch.dict(tool.BUDGETS, {"first": (), "second": ()}, clear=True):
            result = tool.portfolio(data, table)
            self.assertEqual(["1200", "1500", "2000"], [r["nominal_ohm"] for r in result["candidates"]])
            self.assertEqual("1200", result["selected_nominal_ohm"])
            self.assertEqual("1", result["minimum_margin_a_exact"])
            self.assertEqual("0", result["candidates"][-1]["minimum_margin_a_exact"])
            empty = tool.portfolio({**data, "required_lower_a": F(6)}, table)
            self.assertEqual([], empty["candidates"])
            self.assertIsNone(empty["selected_nominal_ohm"])
            self.assertFalse(empty["domain"]["continuous_feasible"])

    def test_portfolio_exact_decades_and_invalid_tables(self):
        decades, values = tool.finite_nominals(F("0.99"), F(10), TEST_TABLE)
        self.assertEqual([-1, 0, 1], decades)
        self.assertEqual(F(1), values[0])
        self.assertEqual(F(10), values[-1])
        self.assertEqual(193, len(values))
        for table in (TEST_TABLE[:-1], TEST_TABLE + (F(3),), tuple(reversed(TEST_TABLE)),
                      (True, *TEST_TABLE[1:]), (F(0), *TEST_TABLE[1:]),
                      (TEST_TABLE[1], *TEST_TABLE[1:])):
            with self.subTest(table=table[:2]), self.assertRaisesRegex(ValueError, "E192 table"):
                tool.portfolio(self.current, table)

    def test_portfolio_independent_forward_rejects_unsafe_inverse_domain(self):
        with patch.object(tool, "inverse", return_value=tool.NominalWindow(F(1000), F(2000))):
            with self.assertRaisesRegex(ValueError, "independent forward"):
                tool.portfolio(self.current, TEST_TABLE)

    def test_changed_installed_table_cannot_publish(self):
        with patch.object(tool, "load_current", return_value=self.current):
            tables = iter((TEST_TABLE, TEST_TABLE[:-1]))
            with self.assertRaisesRegex(ValueError, "table changed"):
                tool.run(lambda _: F(1150), lambda: next(tables))

    def test_cli_error_never_returns_a_previous_result(self):
        output = StringIO()
        with patch.object(tool, "keep_awake", side_effect=ValueError("caffeine unavailable")), redirect_stdout(output):
            self.assertEqual(2, tool.main())
        result = json.loads(output.getvalue())
        self.assertEqual("execution_error", result["status"])
        self.assertIsNone(result["report"])
        self.assertFalse(result["qualified"])

    def test_cli_source_change_before_publication_cannot_publish(self):
        output = StringIO()
        with patch.object(tool, "keep_awake", return_value=nullcontext()), \
             patch.object(tool, "run", return_value={"source_sha256": self.current["source_sha256"]}), \
             patch.object(tool, "snapshot", return_value={}), redirect_stdout(output):
            self.assertEqual(2, tool.main())
        result = json.loads(output.getvalue())
        self.assertIn("before publication", result["error"])
        self.assertIsNone(result["report"])


@unittest.skipUnless(importlib.util.find_spec("edg"), "prepared EDG runtime required")
class InstalledEdgTests(unittest.TestCase):
    def test_real_edg_choice_and_exact_forward_replay(self):
        data = tool.load_current()
        first = tool.compare(data)
        self.assertEqual(first, tool.compare(data))
        self.assertTrue(all(r["status"] == "conditional_candidate" for r in first["selections"]))
        for selection in first["selections"]:
            self.assertTrue(tool.forward(F(selection["selected_nominal_ohm"]), data["spec"],
                tool.BUDGETS[selection["budget"]], data["required_lower_a"], data["strict_upper_a"])["numerical_constraints_met"])
        self.assertTrue(all(r["selected_nominal_ohm"] == "1100" for r in first["selections"]))
        table = tool.load_edg_table()
        self.assertEqual(table, tool.load_edg_table())
        result = tool.portfolio(data, table)
        self.assertEqual(result, tool.portfolio(data, table))
        self.assertEqual(["1100", "1110", "1130", "1140", "1150"],
                         [row["nominal_ohm"] for row in result["candidates"]])
        self.assertEqual("1130", result["selected_nominal_ohm"])
        self.assertGreater(F(result["minimum_margin_a_exact"]),
                           F(result["candidates"][0]["minimum_margin_a_exact"]))
        tool.validate_portfolio(data, result, table)

    def test_changed_installed_numerical_source_is_rejected(self):
        for relative in tool.edg_runtime.EDG_SOURCE_SHA256:
            with self.subTest(relative=relative), patch.dict(tool.edg_runtime.EDG_SOURCE_SHA256, {relative: "0"*64}):
                with self.assertRaisesRegex(ValueError, "unreviewed EDG numerical source"):
                    tool.load_edg_table()


if __name__ == "__main__":
    unittest.main()
