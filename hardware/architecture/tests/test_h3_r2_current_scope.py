"""Adversarial scope validation and a write-free current H3 DAG exercise."""
import copy
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/verification"))
import h3_r2_current_scope as scope
import regenerate_h3_r2 as regenerate


class CurrentScopeUnitTests(unittest.TestCase):
    artifact = "H3-R2-source-margins"

    def qualified_fixture(self):
        result = {"artifact": self.artifact, "status": "pass", "errors": [],
                  "rows": [{"voltage": "3.1", "status": "pass"}],
                  "source_sha256": {p: scope.digest(ROOT / p) for p in scope.DIRECT_SOURCES[self.artifact]}}
        return scope.apply_scope(result, ROOT / scope.PRODUCERS[self.artifact],
                                 {key: True for key in scope.REQUIREMENTS[self.artifact]})

    def test_exact_qualified_fixture_can_be_admitted_without_authorizing_hardware(self):
        result = self.qualified_fixture()
        self.assertTrue(scope.admits_current(result, self.artifact))
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_current_unqualified_is_publishable_and_preserves_provisional_numbers(self):
        result = self.qualified_fixture()
        algebra = copy.deepcopy(result["rows"])
        scope.apply_scope(result, ROOT / scope.PRODUCERS[self.artifact],
                          {"rail_inputs": False, "source_model_binding": True})
        self.assertEqual("review_required", result["status"])
        self.assertEqual(algebra, result["rows"])
        self.assertEqual("provisional_pass", result["current_power_scope"]["numerical_status"])
        self.assertIn("applicability:rail_inputs", result["errors"])
        self.assertFalse(scope.admits_current(result, self.artifact))

    def test_legacy_pass_without_current_scope_is_not_admitted(self):
        self.assertFalse(scope.admits_current({"artifact": self.artifact, "status": "pass", "errors": []}, self.artifact))

    def test_required_hash_omission_from_both_copies_is_rejected(self):
        for omitted in scope.required_sources(self.artifact):
            result = self.qualified_fixture()
            del result["source_sha256"][omitted]
            del result["current_power_scope"]["source_sha256"][omitted]
            with self.subTest(omitted=omitted):
                self.assertFalse(scope.admits_current(result, self.artifact))

    def test_tampered_or_stale_hash_and_wrong_artifact_rejected(self):
        result = self.qualified_fixture()
        name = "hardware/verification/generated/H3-R2-rail-margins.json"
        result["source_sha256"][name] = result["current_power_scope"]["source_sha256"][name] = "0" * 64
        self.assertFalse(scope.admits_current(result, self.artifact))
        self.assertFalse(scope.admits_current(self.qualified_fixture(), "H3-R2-rail-margins"))

    def test_false_qualified_flags_omission_and_integer_bool_rejected(self):
        for change in ("omit", "integer", "extra", "unknown"):
            result = self.qualified_fixture()
            checks = result["current_power_scope"]["applicability_checks"]
            if change == "omit":
                del checks["rail_inputs"]
            elif change == "extra":
                checks["not_a_reviewed_requirement"] = True
            else:
                checks["rail_inputs"] = 1 if change == "integer" else None
            with self.subTest(change=change):
                self.assertFalse(scope.admits_current(result, self.artifact))

    def test_status_only_and_cleared_findings_cannot_restore_qualification(self):
        result = self.qualified_fixture()
        scope.apply_scope(result, ROOT / scope.PRODUCERS[self.artifact],
                          {"rail_inputs": False, "source_model_binding": True})
        result.update(status="pass", errors=[], open_analytical_findings=[], current_analytical_scope_complete=True)
        result["current_power_scope"].update(status="pass", open_findings=[], current_analytical_scope_complete=True)
        self.assertFalse(scope.admits_current(result, self.artifact))

    def test_provisional_failure_and_authority_tampering_rejected(self):
        result = self.qualified_fixture()
        result["errors"] = ["declared_target_voltage"]
        scope.apply_scope(result, ROOT / scope.PRODUCERS[self.artifact],
                          {key: True for key in scope.REQUIREMENTS[self.artifact]})
        self.assertEqual("provisional_fail", result["current_power_scope"]["numerical_status"])
        self.assertFalse(scope.admits_current(result, self.artifact))
        result = self.qualified_fixture()
        result["authorization"]["fabrication"] = True
        self.assertFalse(scope.admits_current(result, self.artifact))

    def test_unrelated_io_errors_are_not_caught_as_diagnostics(self):
        with patch.object(Path, "read_bytes", side_effect=PermissionError("blocked")):
            with self.assertRaises(PermissionError):
                self.qualified_fixture()


def build_in_memory():
    """Use actual producers/inputs, replacing only reads of newly built outputs."""
    overlay = {}
    original = Path.read_bytes

    def read_bytes(path):
        return overlay[path.resolve()] if path.resolve() in overlay else original(path)

    def read_text(path, encoding=None, errors=None):
        return read_bytes(path).decode(encoding or "utf-8", errors or "strict")

    with patch.object(Path, "read_bytes", read_bytes), patch.object(Path, "read_text", read_text), \
            patch.object(Path, "write_text", side_effect=AssertionError("canonical write forbidden")), \
            patch.object(Path, "write_bytes", side_effect=AssertionError("canonical write forbidden")):
        for relative in regenerate.SCRIPTS:
            module = importlib.import_module(Path(relative).stem)
            built = module.build()
            if isinstance(built, tuple):
                outputs = built[0]
            else:
                outputs = {module.OUTPUT: json.dumps(built, ensure_ascii=False, indent=2) + "\n"}
                if hasattr(module, "render"):
                    outputs.update({module.DOC_EN: module.render(built, "en"), module.DOC_RU: module.render(built, "ru")})
                elif hasattr(module, "render_doc"):
                    outputs.update({module.DOC_EN: module.render_doc(built, False), module.DOC_RU: module.render_doc(built, True)})
            for path, content in outputs.items():
                overlay[path.resolve()] = content.encode()
        # With all outputs virtually published, verify direct binding coverage.
        for path, content in overlay.items():
            if path.suffix != ".json":
                continue
            result = json.loads(content)
            if "current_power_scope" in result:
                required = scope.required_sources(result["artifact"])
                if not required.issubset(result["current_power_scope"]["source_sha256"]):
                    raise AssertionError("missing direct source in " + result["artifact"])
                for name, expected in result["current_power_scope"]["source_sha256"].items():
                    if scope.digest(ROOT / name) != expected:
                        raise AssertionError("stale direct source " + name)
    return overlay


class CurrentPowerDAGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build_in_memory()
        cls.results = {json.loads(data)["artifact"]: json.loads(data) for path, data in cls.outputs.items()
                       if path.suffix == ".json" and "artifact" in json.loads(data)}

    def test_all_fourteen_power_dependents_are_current_unqualified_not_stale_pass(self):
        self.assertEqual(14, len(scope.REQUIREMENTS))
        for artifact in scope.REQUIREMENTS:
            result = self.results[artifact]
            with self.subTest(artifact=artifact):
                self.assertEqual("review_required", result["status"])
                self.assertFalse(result["current_analytical_scope_complete"])
                self.assertFalse(result["production_release_authorized"])
                self.assertFalse(result["battery_energization_authorized"])
                self.assertTrue(result["errors"])
                self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_corrected_main_numbers_and_targets_are_not_replaced_to_get_pass(self):
        result = self.results["H3-R2-rail-margins"]
        row = result["voltage_corners"]["3V3_MAIN"]
        self.assertEqual("2.956210", row["endpoint_min_v"])
        self.assertEqual("3.006210", row["protected_local_min_v"])
        self.assertEqual("3.285658", row["endpoint_max_v"])
        self.assertEqual("fail", row["numerical_status"])
        self.assertEqual(224, len(result["profile_voltage_corners"]))
        self.assertIn("TPS566231", result["observed_main_converter"]["mpn"])
        self.assertFalse(result["current_power_scope"]["applicability_checks"]["main_raw_model"])

    def test_typical_supervisor_limits_cannot_be_guaranteed_bounds(self):
        result = self.results["H3-R2-transition-sequences"]
        self.assertIsNone(result["timing"]["supervisor_assertion_max_us"])
        self.assertEqual(20, result["timing"]["supervisor_assertion_typ_us"])
        self.assertIsNone(result["timing"]["supervisor_hysteresis_percent"]["min"])
        self.assertIn("applicability:supervisor_assertion_bound", result["errors"])
        self.assertIn("applicability:supervisor_hysteresis_bound", result["errors"])

    def test_acceptance_and_bilingual_reports_cannot_claim_analytical_closure(self):
        acceptance = self.results["H3-R2-acceptance-package"]
        self.assertFalse(acceptance["result"]["analytical_scope_complete"])
        self.assertGreater(acceptance["result"]["open_analytical_findings"], 0)
        for filename in ("h3-r2-acceptance.md", "h3-r2-acceptance.ru.md", "power-rail-margins.md", "power-rail-margins.ru.md"):
            text = self.outputs[ROOT / "docs" / filename].decode()
            with self.subTest(filename=filename):
                self.assertIn("review_required", text)
                self.assertNotIn("zero open finding", text)
                self.assertNotIn("fully reviewed", text)
                self.assertNotIn("within `None", text)

    def test_strict_cli_checks_qualification_only_after_complete_diagnostic_dag(self):
        package = self.results["H3-R2-acceptance-package"]
        for strict, expected in ((False, 0), (True, 2)):
            argv = ["regenerate_h3_r2", "--check"] + (["--require-qualified"] if strict else [])
            with patch.object(sys, "argv", argv), patch.object(regenerate.subprocess, "run") as run, \
                    patch.object(Path, "read_text", return_value=json.dumps(package)), \
                    patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(expected, regenerate.main())
                self.assertEqual(len(regenerate.SCRIPTS), run.call_count)
                self.assertTrue(all(call.kwargs["check"] for call in run.call_args_list))

    def test_transition_reports_retain_localized_navigation_and_engineering_context(self):
        expected = {
            "power-handover.ru.md": ("Группа сценариев", "Число модельных случаев", "BATFET", "Rp/PD", "Применимость"),
            "inrush-load-step.ru.md": ("Худшая нагрузка", "Численное сравнение", "C12", "dV/dt", "Сходимость"),
            "power-transition-result.ru.md": ("Группа модели", "Число рассмотренных случаев", "FAULT_KILL", "KILL→RUN", "применимости"),
        }
        for filename, fragments in expected.items():
            text = self.outputs[ROOT / "docs" / filename].decode()
            with self.subTest(filename=filename):
                for fragment in ("[English]", "[Главная]", "[Роадмап]", "review_required", *fragments):
                    self.assertIn(fragment, text)
                for raw_key in ("usb_attach_cases", "startup_scenarios", "fault_scenarios", "Enumerated cases", "Provisional starts:"):
                    self.assertNotIn(raw_key, text)
                self.assertTrue(all(line == line.rstrip() for line in text.splitlines()))
            en = self.outputs[ROOT / "docs" / filename.replace(".ru.md", ".md")].decode()
            for fragment in ("[Русский]", "[Home]", "[Roadmap]", "review_required"):
                self.assertIn(fragment, en)

    def test_real_generator_failure_still_stops_dag(self):
        with patch.object(sys, "argv", ["regenerate_h3_r2", "--check"]), \
                patch.object(regenerate.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "producer")), \
                patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(subprocess.CalledProcessError):
                regenerate.main()

    def test_numerical_state_failure_is_published_not_swallowed_or_raised(self):
        module = importlib.import_module("h3_r2_source_margins")
        original = module.evaluate_state

        def fail_state(*args, **kwargs):
            row = original(*args, **kwargs)
            row["status"] = "fail"
            return row

        with patch.object(module, "evaluate_state", side_effect=fail_state):
            outputs, result = module.build()
        self.assertIn(module.OUTPUT, outputs)
        self.assertEqual("review_required", result["status"])
        self.assertEqual("provisional_fail", result["current_power_scope"]["numerical_status"])
        self.assertEqual(2266, result["summary"]["failed_states"])
        self.assertEqual(2266, len(result["provisional_numerical_errors"]))
        self.assertTrue(all(error.startswith("source-state:") for error in result["provisional_numerical_errors"]))


if __name__ == "__main__":
    unittest.main()
