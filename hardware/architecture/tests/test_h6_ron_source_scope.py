"""Adversarial source-domain checks, independent of positive RON arithmetic."""

import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/verification"))
import h6_ron_source_scope as scope
from h6_power_corner_math import Interval


class RonSourceScopeTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "id": "test_ron_max",
            "mpn": "TPS259814LRPWR",
            "parameter": "RON",
            "value": "8.4",
            "unit": "mohm",
            "bound_kind": "max",
            "conditions": {
                "vin_v": ["2.7", "16"],
                "iout_a": ["3", "3"],
                "tj_c": ["-40", "125"],
            },
            "unmodeled_header_conditions": ["Published enable and control-pin conditions remain unmodeled."],
            "source": {
                "url": "https://www.ti.com/lit/gpn/TPS25981",
                "revision": "SLVSGG6C",
                "pdf_sha256": "a" * 64,
                "page": 8,
                "reviewed_on": "2026-09-20",
            },
        }

    def evaluate(self, **overrides):
        arguments = {
            "mpn": "TPS259814LRPWR",
            "vin": Interval("2.7", "16"),
            "tj": Interval("-40", "125"),
            "loads": [("table_current", Fraction(3))],
        }
        arguments.update(overrides)
        return scope.evaluate_row(self.row, **arguments)

    def test_covered_numeric_axes_do_not_qualify_the_physical_cell(self):
        report = self.evaluate()
        self.assertTrue(report["numeric_domains_covered"])
        self.assertIs(False, report["qualified"])
        self.assertEqual([], report["missing_source_domains"])
        self.assertEqual([], report["uncovered_load_cases"])
        self.assertEqual(Fraction(21, 2500), Fraction(report["source_max_ohm"]))

    def test_point_current_is_not_a_range_or_a_monotonic_guarantee(self):
        report = self.evaluate(loads=[
            ("lower_than_table", Fraction(2)),
            ("at_table", Fraction(3)),
            ("required_step", Fraction(17, 4)),
        ])
        self.assertFalse(report["numeric_domains_covered"])
        self.assertEqual(["lower_than_table", "required_step"], report["uncovered_load_cases"])
        self.assertIs(False, report["qualified"])

    def test_current_range_checks_every_individual_load(self):
        self.row["conditions"]["iout_a"] = ["0", "4.25"]
        report = self.evaluate(loads=[("off", Fraction(0)), ("steady", Fraction(2)), ("step", Fraction(17, 4))])
        self.assertTrue(report["numeric_domains_covered"])
        report = self.evaluate(loads=[("steady", Fraction(2)), ("beyond_step", Fraction(4250001, 1000000))])
        self.assertFalse(report["numeric_domains_covered"])
        self.assertEqual(["beyond_step"], report["uncovered_load_cases"])

    def test_full_vin_and_tj_intervals_must_be_contained(self):
        for overrides in (
            {"vin": Interval("2.699999", "16")},
            {"vin": Interval("2.7", "16.000001")},
            {"tj": Interval("-40.000001", "125")},
            {"tj": Interval("-40", "125.000001")},
        ):
            with self.subTest(overrides=overrides):
                report = self.evaluate(**overrides)
                self.assertFalse(report["numeric_domains_covered"])
                self.assertIs(False, report["qualified"])

    def test_typical_and_minimum_values_cannot_become_a_maximum(self):
        for kind in ("typ", "min"):
            with self.subTest(kind=kind):
                self.row["bound_kind"] = kind
                report = self.evaluate()
                self.assertEqual(kind, report["bound_kind"])
                self.assertIsNone(report["source_max_ohm"])
                self.assertFalse(report["numeric_domains_covered"])
                self.assertIs(False, report["qualified"])

    def test_milliohm_conversion_matches_explicit_ohms(self):
        milliohm = self.evaluate()
        self.row.update(value="0.0084", unit="ohm")
        ohm = self.evaluate()
        self.assertEqual(Fraction(milliohm["source_max_ohm"]), Fraction(ohm["source_max_ohm"]))

    def test_parameter_unit_bound_and_exact_mpn_mismatches_fail(self):
        for key, value in (("parameter", "VFB"), ("unit", "mV"), ("bound_kind", "guaranteed")):
            with self.subTest(key=key):
                row = copy.deepcopy(self.row)
                self.row[key] = value
                with self.assertRaises(ValueError):
                    self.evaluate()
                self.row = row
        with self.assertRaises(ValueError):
            self.evaluate(mpn="TPS259814ARPWR")

    def test_missing_or_unknown_row_fields_cannot_be_ignored(self):
        for key in tuple(self.row):
            with self.subTest(missing=key):
                row = copy.deepcopy(self.row)
                del self.row[key]
                with self.assertRaises(ValueError):
                    self.evaluate(mpn="TPS259814LRPWR")
                self.row = row
        self.row["qualified"] = True
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_nonfinite_nonstring_and_nonpositive_ron_values_fail(self):
        for value in ("NaN", "Infinity", "-Infinity", "-1", "0", True, False, 8.4, 8, None):
            with self.subTest(value=value):
                self.row["value"] = value
                with self.assertRaises(ValueError):
                    self.evaluate()

    def test_malformed_source_intervals_fail(self):
        original = copy.deepcopy(self.row["conditions"])
        for axis in original:
            for bounds in (["3", "2"], ["3"], ["3", "3", "3"], [True, "3"], ["NaN", "3"], ["3", "Infinity"], [3, 3], "3"):
                with self.subTest(axis=axis, bounds=bounds):
                    self.row["conditions"] = copy.deepcopy(original)
                    self.row["conditions"][axis] = bounds
                    with self.assertRaises(ValueError):
                        self.evaluate()

    def test_missing_or_extra_source_axis_is_invalid_not_unbounded(self):
        original = copy.deepcopy(self.row["conditions"])
        for axis in original:
            with self.subTest(axis=axis):
                self.row["conditions"] = copy.deepcopy(original)
                del self.row["conditions"][axis]
                with self.assertRaises(ValueError):
                    self.evaluate()
        self.row["conditions"] = {**original, "ambient_c": ["-40", "125"]}
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_invalid_application_domains_fail(self):
        for overrides in (
            {"vin": ["2.7", "16"]}, {"tj": None},
            {"vin": Interval("0", "16")}, {"vin": Interval("-1", "16")},
            {"tj": Interval("-273.150001", "125")},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.evaluate(**overrides)

    def test_primary_identity_is_complete_and_well_formed(self):
        original = copy.deepcopy(self.row["source"])
        for key in original:
            with self.subTest(missing=key):
                self.row["source"] = copy.deepcopy(original)
                del self.row["source"][key]
                with self.assertRaises(ValueError):
                    self.evaluate()
        for key, value in (
            ("url", "https://example.invalid/tps25981.pdf"), ("url", ""),
            ("revision", ""), ("pdf_sha256", "a" * 63), ("pdf_sha256", "g" * 64),
            ("page", True), ("page", 0), ("reviewed_on", "not-a-date"),
        ):
            with self.subTest(key=key, value=value):
                self.row["source"] = {**original, key: value}
                with self.assertRaises(ValueError):
                    self.evaluate()

    def test_negative_voltage_or_current_conditions_fail_but_negative_tj_is_valid(self):
        for axis in ("vin_v", "iout_a"):
            with self.subTest(axis=axis):
                original = copy.deepcopy(self.row["conditions"])
                self.row["conditions"][axis] = ["-1", "3"]
                with self.assertRaises(ValueError):
                    self.evaluate()
                self.row["conditions"] = original
        self.assertTrue(self.evaluate()["numeric_domains_covered"])

    def test_empty_duplicate_or_malformed_load_cases_fail(self):
        for loads in (
            [], [("duplicate", Fraction(3)), ("duplicate", Fraction(3))],
            [("", Fraction(3))], [(" ", Fraction(3))],
            [("negative", Fraction(-1))], [("boolean", True)],
            [("nonfinite", float("nan"))], [("float", 3.0)],
            [("missing_value",)],
        ):
            with self.subTest(loads=loads), self.assertRaises(ValueError):
                self.evaluate(loads=loads)

    def test_unmodeled_conditions_must_remain_explicit(self):
        for conditions in ([], "omitted", [""], [None], [True]):
            with self.subTest(conditions=conditions):
                self.row["unmodeled_header_conditions"] = conditions
                with self.assertRaises(ValueError):
                    self.evaluate()

    def test_evaluation_does_not_mutate_reviewed_rows(self):
        before = copy.deepcopy(self.row)
        self.evaluate(loads=[("out_of_domain", Fraction(17, 4))])
        self.assertEqual(before, self.row)

    def test_checked_in_source_rows_match_the_pinned_bytes(self):
        before = scope.ROWS_PATH.read_bytes()
        self.assertEqual(scope.REVIEWED_SHA256, hashlib.sha256(before).hexdigest())
        record = scope.load_reviewed_rows()
        self.assertEqual(json.loads(before), record)
        self.assertEqual(before, scope.ROWS_PATH.read_bytes())

    def test_altered_source_bytes_cannot_inherit_the_reviewed_hash(self):
        path = Mock()
        path.is_symlink.return_value = False
        path.is_file.return_value = True
        path.read_bytes.return_value = b'{"changed": true}'
        with patch.object(scope, "ROWS_PATH", path), self.assertRaisesRegex(ValueError, "changed"):
            scope.load_reviewed_rows()

    def test_missing_or_symlinked_reviewed_file_is_rejected(self):
        for symlink, exists in ((True, True), (False, False)):
            with self.subTest(symlink=symlink, exists=exists):
                path = Mock()
                path.is_symlink.return_value = symlink
                path.is_file.return_value = exists
                with patch.object(scope, "ROWS_PATH", path), self.assertRaises(ValueError):
                    scope.load_reviewed_rows()
                path.read_bytes.assert_not_called()

    def test_reviewed_loader_rejects_malformed_or_duplicate_rows(self):
        base = {
            "schema_version": 1,
            "scope": "Test-only bounded RON review",
            "screening_tj_c": ["-40", "125"],
            "temperature_basis": "Explicit test envelope",
            "rows": [self.row],
        }
        for rows in ([], [self.row, self.row], [None], [{}]):
            with self.subTest(rows=rows):
                raw = json.dumps({**base, "rows": rows}).encode("utf-8")
                path = Mock()
                path.is_symlink.return_value = False
                path.is_file.return_value = True
                path.read_bytes.return_value = raw
                with patch.object(scope, "ROWS_PATH", path), patch.object(scope, "REVIEWED_SHA256", hashlib.sha256(raw).hexdigest()):
                    with self.assertRaises(ValueError):
                        scope.load_reviewed_rows()

    def test_main_screen_keeps_all_loads_and_cannot_adopt_candidate(self):
        data = {
            "rail": {"nominal_v": "3.3", "load_max_v": "3.6"},
            "policy": {"raw_regulated_voltage_minimum_fraction_of_nominal": "0.95"},
            "efuse_mpn": "Texas Instruments TPS25974LRPWR",
            "cases": [("low_load", Fraction(2)), ("table", Fraction(3)), ("step", Fraction(17, 4))],
        }
        report = scope.assess_main(data)
        self.assertIs(False, report["qualified"])
        self.assertIs(False, report["supply_checked"])
        self.assertIs(False, report["replacement_adopted"])
        self.assertEqual("source_scope_screen_only", report["status"])
        self.assertEqual(["3.135", "3.6"], report["application"]["required_vin_v"])
        self.assertEqual([["low_load", "2"], ["table", "3"], ["step", "17/4"]], report["application"]["load_cases_a_exact"])
        for row in report["rows"]:
            self.assertEqual(3, row["checked_load_cases"])
            self.assertFalse(row["numeric_domains_covered"])
            self.assertEqual(["low_load", "step"], row["uncovered_load_cases"])
            self.assertIs(False, row["qualified"])
        data["efuse_mpn"] = "Texas Instruments TPS259814LRPWR"
        with self.assertRaisesRegex(ValueError, "native MAIN"):
            scope.assess_main(data)


if __name__ == "__main__":
    unittest.main()
