"""Guard the scope and independent residual checks of the existing SPICE runner."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools import probe_evidence_spice as probe


class EvidenceSpiceProbeTests(unittest.TestCase):
    def fixture(self):
        values = {key: "1000" for key in ("pullup_ohm", "led_series_ohm", "hysteresis_ohm",
                  "threshold_top_ohm", "threshold_bottom_ohm", "diode_or_pullup_ohm")}
        return {"full_EV_qualified": False, "channels": [{"id": key, **values} for key in ("c5", "ir")]}

    def test_exact_stimulus_grid_preserves_model_and_samples_stated_corner(self):
        model = ["* exact vendor placeholder", ".subckt untouched a b", ".ends"]
        cases = probe.make_cases(self.fixture(), model)
        self.assertEqual(13, len(cases))
        self.assertEqual("known-divider", cases[0]["id"])
        self.assertEqual({(name, v, state) for name in ("c5", "ir") for v in (2.7, 3.3, 3.6)
                          for state in ("low", "high")},
                         {(c["channel"], c["aon_v"], c["state"]) for c in cases[1:]})
        for c in cases[1:]:
            self.assertEqual(model, c["request"]["netlist"][1:4])
            self.assertEqual({990.0}, set(c["resistors_ohm"].values()))
            self.assertTrue(any(line.startswith("rledshort ") for line in c["request"]["netlist"]))
            self.assertTrue(any(line.startswith("rorshort ") for line in c["request"]["netlist"]))

    def test_fixture_must_be_unqualified_and_cover_exact_two_channels(self):
        data = self.fixture()
        data["full_EV_qualified"] = True
        with self.assertRaisesRegex(ValueError, "cannot qualify"):
            probe.make_cases(data, [])
        data = self.fixture()
        data["channels"].pop()
        with self.assertRaisesRegex(ValueError, "coverage"):
            probe.make_cases(data, [])
        data = self.fixture()
        data["channels"][0]["pullup_ohm"] = "nan"
        with self.assertRaisesRegex(ValueError, "invalid resistive"):
            probe.make_cases(data, [])

    def test_known_divider_is_a_separate_numeric_control(self):
        case = probe.make_cases(self.fixture(), [])[0]
        self.assertTrue(probe.validate_values(case, {"v(out)": 1.65})["known_divider_pass"])
        with self.assertRaisesRegex(ValueError, "divider"):
            probe.validate_values(case, {"v(out)": 1.5})

    def test_numeric_proof_requires_exact_finite_vector_coverage(self):
        case = probe.make_cases(self.fixture(), [])[0]
        for values in ({}, {"v(out)": 1.65, "extra": 0}, {"v(out)": float("nan")}, {"v(out)": True}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                probe.validate_values(case, values)

    def test_fixed_hand_calculation_and_wrong_current_are_independent_checks(self):
        case = probe.make_cases(self.fixture(), [])[1]
        case["aon_v"] = 3.3
        case["resistors_ohm"] = {key: 1000.0 for key in case["resistors_ohm"]}
        # Threshold=(3.3+0.15)/3=1.15 V. Three feed resistors give9.45 mA,
        # feedback gives1 mA, total10.45 mA. This is an arithmetic fixture,
        # not a source-qualified TLV182x load point.
        values = {"v(ev)": 0.15, "v(threshold)": 1.15, "i(vsense)": 0.01045}
        checked = probe.validate_values(case, values)
        self.assertLess(abs(checked["output_kcl_residual_a"]), 1e-12)
        self.assertTrue(checked["legacy_0_1v_assumption_exceeded_in_this_stress"])
        for vector, value in (("i(vsense)", -0.01045), ("v(threshold)", 0.5), ("i(vsense)", 0.00945)):
            bad = copy.deepcopy(values)
            bad[vector] = value
            with self.subTest(vector=vector, value=value), self.assertRaisesRegex(ValueError, "KCL"):
                probe.validate_values(case, bad)

    def test_changed_or_missing_model_never_falls_back_to_invented_model(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.zip"
            with self.assertRaisesRegex(ValueError, "missing"):
                probe.load_model(path)
            path.write_bytes(b"not the reviewed archive")
            with self.assertRaisesRegex(ValueError, "changed"):
                probe.load_model(path)

    def test_scope_excludes_false_whole_network_and_poweroff_claims(self):
        self.assertTrue(any("Other diode" in x and "not modeled" in x for x in probe.LIMITATIONS))
        self.assertTrue(any("No power-off" in x for x in probe.LIMITATIONS))
        self.assertTrue(any("not exact TLV1824PWR" in x for x in probe.LIMITATIONS))
        self.assertTrue(any("not electrical/physical acceptance" in x for x in probe.LIMITATIONS))


@unittest.skipUnless(probe.DEFAULT_LIBRARY.is_file() and probe.DEFAULT_MODEL.is_file(), "prepared native SPICE/model required")
class NativeEVSpiceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        before = probe.sources(probe.DEFAULT_MODEL, probe.DEFAULT_LIBRARY)
        cls.native = probe.load_fixture(before)
        cls.case = next(c for c in probe.make_cases(cls.native, probe.load_model(probe.DEFAULT_MODEL)) if c["id"] == "c5-3.6-low")

    def worker(self, request):
        process = subprocess.run([sys.executable, "-B", str(probe.ROOT / "tools/ngspice_worker.py")],
                                 input=json.dumps(request), text=True, capture_output=True, timeout=30, cwd=probe.ROOT)
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        return json.loads(process.stdout)["values"]

    def test_actual_model_output_satisfies_independent_current_balance(self):
        values = self.worker(self.case["request"])
        result = probe.validate_values(self.case, values)
        self.assertTrue(result["model_polarity_smoke_pass"])

    def test_omitting_shared_or_load_from_actual_deck_is_detected(self):
        request = copy.deepcopy(self.case["request"])
        request["netlist"] = [line for line in request["netlist"] if not line.startswith("rorshort ")]
        values = self.worker(request)
        with self.assertRaisesRegex(ValueError, "KCL"):
            probe.validate_values(self.case, values)

    def test_changed_assembled_series_resistor_is_detected(self):
        request = copy.deepcopy(self.case["request"])
        request["netlist"] = ["rledshort aon ev 22000" if line.startswith("rledshort ") else line for line in request["netlist"]]
        values = self.worker(request)
        with self.assertRaisesRegex(ValueError, "KCL"):
            probe.validate_values(self.case, values)


if __name__ == "__main__":
    unittest.main()
