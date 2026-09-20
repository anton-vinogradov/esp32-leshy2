"""Independent tests for conditional EDG pair selection, never qualification."""

from fractions import Fraction as F
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import edg_feedback_pair as tool

I = tool.Interval


class EdgFeedbackPairTest(unittest.TestCase):
    def args(self):
        return [I(1, 1), I(2, 2), I(1, 1), I(1, 1), I(50, 50), I(0, 0)]

    def test_incompatible_reference_output_envelope_skips_edg(self):
        args = self.args()
        args[:2] = I(".591", ".609"), I("3.2725", "3.29")
        with patch.object(tool, "_find_pair", side_effect=AssertionError("must skip EDG")):
            result = tool.synthesize_pair(*args)
        self.assertEqual(result["status"], "conditional_infeasible")
        self.assertGreater(F(result["required_ratio_exact"][0]), F(result["required_ratio_exact"][1]))
        self.assertFalse(result["selector"]["executed"])
        self.assertFalse(result["qualified"])

    def test_no_match_is_distinct_from_proven_infeasible(self):
        with patch.object(tool, "_find_pair", return_value=None):
            result = tool.synthesize_pair(*self.args())
        self.assertEqual(result["status"], "preferred_selector_found_no_candidate")
        self.assertIsNone(result["selected_nominal_ohm_exact"])
        self.assertNotIn("continuous_feasible", result)
        self.assertFalse(result["qualified"])

    def test_common_symmetric_tolerance_encloses_both_asymmetric_factors(self):
        args = self.args()
        args[2:4] = I(".999", "1.002"), I(".997", "1.001")
        with patch.object(tool, "_find_pair", return_value=None) as find:
            result = tool.synthesize_pair(*args)
        self.assertEqual(find.call_args.args[2], F(3, 1000))
        self.assertEqual(result["common_symmetric_tolerance_fraction_exact"], "3/1000")

    def test_nonzero_leakage_is_explicitly_unsupported(self):
        for leakage in (I(0, ".000001"), I("-.000001", 0), I(1, 1)):
            args = self.args()
            args[-1] = leakage
            with self.subTest(leakage=leakage), self.assertRaisesRegex(NotImplementedError, "nonzero leakage"):
                tool.synthesize_pair(*args)

    def test_invalid_domains_fail_before_edg(self):
        for position in range(5):
            for value in (I(0, 1), I(-1, 1), None, (1, 1)):
                args = self.args()
                args[position] = value
                with self.subTest(position=position, value=value), self.assertRaises(ValueError):
                    tool.synthesize_pair(*args)
        for value in (None, (0, 0), 0):
            args = self.args()
            args[-1] = value
            with self.assertRaises(ValueError):
                tool.synthesize_pair(*args)
        for series in (True, 0, 13, "192", 192.0):
            with self.subTest(series=series), self.assertRaises(ValueError):
                tool.synthesize_pair(*self.args(), series=series)
        args = self.args()
        args[2] = I(1, 2)
        with self.assertRaisesRegex(ValueError, "shared symmetric enclosure"):
            tool.synthesize_pair(*args)

    def test_exact_checker_uses_voltage_and_parallel_impedance_corners(self):
        result = tool.verify_candidate(F(100), F(100), I(1, 2), I("1.9", "4.2"),
                                       I(".9", "1.1"), I(1, 1), I(47, 53))
        self.assertEqual(result["average_v_exact"], ["19/10", "21/5"])
        self.assertEqual(result["parallel_impedance_ohm_exact"], ["900/19", "1100/21"])
        for limits, impedance in ((I("1.9000000000001", "4.2"), I(47, 53)),
                                  (I("1.9", "4.1999999999999"), I(47, 53)),
                                  (I("1.9", "4.2"), I(48, 53)),
                                  (I("1.9", "4.2"), I(47, 52))):
            with self.subTest(limits=limits, impedance=impedance), self.assertRaisesRegex(ValueError, "independent exact"):
                tool.verify_candidate(F(100), F(100), I(1, 2), limits,
                                      I(".9", "1.1"), I(1, 1), impedance)

    def test_exact_checker_requires_positive_rational_nominals(self):
        for value in (True, 100, 100.0, "100", F(0), F(-100)):
            for position in (0, 1):
                pair = [F(100), F(100)]
                pair[position] = value
                with self.subTest(value=value, position=position), self.assertRaises(ValueError):
                    tool.verify_candidate(*pair, *self.args()[:-1])

    def test_search_proposal_is_independently_rejected(self):
        for pair in ((F(101), F(100)), (F(200), F(200))):
            with patch.object(tool, "_find_pair", return_value=pair), self.assertRaisesRegex(ValueError, "independent exact"):
                tool.synthesize_pair(*self.args())

    def test_import_does_not_require_edg(self):
        spec = importlib.util.spec_from_file_location("pair_without_edg", tool.__file__)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"edg": None}), patch.object(tool.metadata, "distribution", side_effect=AssertionError("lazy import")):
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.synthesize_pair))


@unittest.skipUnless(importlib.util.find_spec("edg"), "prepared EDG 0.5.2 runtime needed")
class EdgFeedbackPairIntegrationTest(unittest.TestCase):
    def test_ready_solver_selects_both_values_without_subprocess(self):
        with patch.object(subprocess, "Popen", side_effect=AssertionError("no JVM/subprocess")):
            result = tool.synthesize_pair(I(1, 1), I(2, 2), I(1, 1), I(1, 1), I(50, 50), I(0, 0))
        self.assertEqual(result["status"], "conditional_candidate")
        self.assertEqual(result["selected_nominal_ohm_exact"], {"top": "100", "bottom": "100"})
        self.assertEqual(result["average_v_exact"], ["2", "2"])
        self.assertEqual(result["parallel_impedance_ohm_exact"], ["50", "50"])
        self.assertEqual(len(result["selector"]["source_sha256"]), 3)
        self.assertFalse(result["qualified"])

    def test_ready_solver_no_match_is_not_an_infeasibility_proof(self):
        with patch.object(subprocess, "Popen", side_effect=AssertionError("no JVM/subprocess")):
            result = tool.synthesize_pair(I(1, 1), I(3, 3), I(1, 1), I(1, 1), I(1, 2), I(0, 0), series=3)
        self.assertEqual(result["status"], "preferred_selector_found_no_candidate")

    def test_ready_solver_unequal_pair_has_independent_asymmetric_factor_corners(self):
        result = tool.synthesize_pair(I(1, 1), I("8.9", "9.5"), I(".99", "1.01"),
                                      I(".995", "1.005"), I(80, 100), I(0, 0), series=24)
        self.assertEqual(result["selected_nominal_ohm_exact"], {"top": "820", "bottom": "100"})
        self.assertEqual(result["average_v_exact"], ["3041/335", "9277/995"])
        self.assertEqual(result["parallel_impedance_ohm_exact"], ["807741/9113", "832341/9287"])

    def test_search_halo_never_relaxes_exact_voltage_or_impedance(self):
        for voltage, impedance in ((I("2.0000000000001", "2.0000000000002"), I(50, 50)),
                                   (I(2, 2), I("50.000000000001", "50.000000000002"))):
            with self.subTest(voltage=voltage, impedance=impedance), self.assertRaisesRegex(ValueError, "independent exact"):
                tool.synthesize_pair(I(1, 1), voltage, I(1, 1), I(1, 1), impedance, I(0, 0))

    def test_unreviewed_sources_fail_closed(self):
        with patch.dict(tool.EDG_SOURCE_SHA256, {"edg/core/Range.py": "0" * 64}), self.assertRaisesRegex(ValueError, "unreviewed EDG"):
            tool.synthesize_pair(I(1, 1), I(2, 2), I(1, 1), I(1, 1), I(50, 50), I(0, 0))


if __name__ == "__main__":
    unittest.main()
