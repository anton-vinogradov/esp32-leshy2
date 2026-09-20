"""Acceptance cannot turn incomplete or stale electrical evidence into PASS."""

import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from hardware.verification import h6_r2_acceptance_adapters as adapters


def power_result(checks):
    findings = [row["id"] for row in checks if not row["pass"]]
    return {
        "checks": checks, "findings": findings,
        "status": "review_required" if findings else "prerequisites_consistent_not_startup_proven",
        "startup_proven": False,
        "authorization": {"fabrication": False, "gate_closed": False},
        "unproven": ["Startup waveform not qualified."],
    }


class ElectricalAcceptanceTests(unittest.TestCase):
    def firmware_result(self, **changes):
        result = {"status": "pass", "qualified": False, "runtime_driver_implemented": False,
                  "gpio_modes_proven": False, "pull_modes_proven": False, "errors": [], **changes}
        module = SimpleNamespace(build=lambda: result)
        with patch.object(adapters, "_snapshot", return_value={"guarded": "unchanged"}), \
             patch.object(adapters, "firmware_evidence_checker", return_value=module):
            return adapters.run_check("electrical.firmware_evidence_binding")

    def test_exact_firmware_binding_cannot_qualify_runtime_or_circuit(self):
        result = self.firmware_result()
        self.assertEqual("unqualified", result["verdict"])
        self.assertFalse(result["details"]["gate_closed"])
        self.assertFalse(result["details"]["runtime_driver_implemented"])

    def test_wrong_physical_to_logical_mapping_is_a_failed_prerequisite(self):
        result = self.firmware_result(status="fail", errors=["P17/raw15 is not P12/logical12"])
        self.assertEqual("fail", result["verdict"])
        self.assertIn("P17", result["findings"][0])

    def test_firmware_binding_claim_inflation_and_hidden_errors_are_rejected(self):
        for mutation in ({"qualified": True}, {"runtime_driver_implemented": True},
                         {"gpio_modes_proven": True}, {"pull_modes_proven": True},
                         {"errors": ["ignored mismatch"]}, {"status": "fail"},
                         {"status": "invented"}, {"errors": "not a list"}):
            with self.subTest(mutation=mutation):
                self.assertEqual("fail", self.firmware_result(**mutation)["verdict"])

    def test_current_evidence_is_checked_without_native_execution(self):
        with patch.object(adapters.semantics, "build", side_effect=AssertionError("native build forbidden")), \
             patch.object(adapters.semantics, "command", side_effect=AssertionError("native command forbidden")):
            for ident in adapters.CHECKS:
                with self.subTest(check=ident):
                    result = adapters.run_check(ident)
                    self.assertEqual({"verdict", "scope", "findings", "details"}, set(result))
                    self.assertIn(result["verdict"], {"fail", "unqualified"})
                    self.assertIn(result["details"]["evidence_status"],
                                  {"current_and_validated", "recomputed_and_validated"})
                    self.assertIs(False, result["details"]["gate_closed"])
                    self.assertTrue(result["findings"])

    def altered_audit(self, mutate):
        original_load = adapters.semantics.load
        audit = copy.deepcopy(original_load(adapters.semantics.OUTPUT))
        mutate(audit)

        def load(path):
            return audit if path == adapters.semantics.OUTPUT else original_load(path)

        return patch.object(adapters.semantics, "load", side_effect=load)

    def test_deleted_native_source_hash_is_rejected_by_both_consumers(self):
        with self.altered_audit(lambda audit: audit["source_hashes"].pop(next(iter(audit["source_hashes"])))):
            for ident in ("electrical.typed_erc", "electrical.source_triage"):
                with self.subTest(check=ident):
                    result = adapters.run_check(ident)
                    self.assertEqual("fail", result["verdict"])
                    self.assertIn("stale", result["findings"][0])

    def test_forged_review_coverage_is_not_accepted(self):
        def mutate(audit):
            audit["coverage"]["reviewed_unique_pins"] += 1

        with self.altered_audit(mutate):
            result = adapters.run_check("electrical.typed_erc")
        self.assertEqual("fail", result["verdict"])
        self.assertIn("coverage", result["findings"][0])

    def test_changed_triage_source_hash_is_rejected(self):
        original_load = adapters.triage.load
        review = copy.deepcopy(original_load(adapters.triage.TRIAGE))
        review["source_sha256"][adapters.triage.LEDGER] = "0" * 64
        with patch.object(adapters.triage, "load", side_effect=lambda path:
                          review if path == adapters.triage.TRIAGE else original_load(path)):
            result = adapters.run_check("electrical.source_triage")
        self.assertEqual("fail", result["verdict"])
        self.assertIn("stale source hash", result["findings"][0])

    def test_missing_evidence_is_unqualified(self):
        with patch.object(adapters, "_snapshot", side_effect=FileNotFoundError("required.json")):
            result = adapters.run_check("electrical.typed_erc")
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual("missing_required_data", result["details"]["evidence_status"])

    def test_missing_firmware_checkout_cannot_clear_binding(self):
        with patch.object(adapters, "_snapshot", side_effect=FileNotFoundError("firmware checker")):
            result = adapters.run_check("electrical.firmware_evidence_binding")
        self.assertEqual("unqualified", result["verdict"])
        self.assertFalse(result["details"]["gate_closed"])

    def test_input_change_during_validation_is_rejected(self):
        with patch.object(adapters, "_snapshot", side_effect=[{"input": "before"}, {"input": "after"}]), \
             patch.dict(adapters._RUNNERS, {"electrical.typed_erc": lambda:
                        ("unqualified", ["Open."], {"gate_closed": False})}):
            result = adapters.run_check("electrical.typed_erc")
        self.assertEqual("fail", result["verdict"])
        self.assertIn("inputs changed", result["findings"][0])

    def run_power_fixture(self, *checks):
        with patch.object(adapters.power, "build", return_value=power_result(list(checks))):
            return adapters.run_check("electrical.power_startup")

    def test_consistent_prerequisites_do_not_prove_startup(self):
        result = self.run_power_fixture({"id": "main_feedback_target", "pass": True, "detail": "Matches."})
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual([], result["details"]["failed_prerequisites"])
        self.assertIs(False, result["details"]["startup_proven"])

    def test_wrong_feedback_target_is_a_failed_prerequisite(self):
        result = self.run_power_fixture({"id": "main_feedback_target", "pass": False,
                                         "detail": "Declared 5 V differs from fitted 3.222 V."})
        self.assertEqual("fail", result["verdict"])
        self.assertEqual(["main_feedback_target"], result["details"]["failed_prerequisites"])

    def test_declared_five_volts_cannot_override_fitted_main_divider(self):
        data = {name: json.loads((adapters.ROOT / path).read_text(encoding="utf-8"))
                for name, path in adapters.power.INPUTS.items()}
        original = adapters.power.evaluate(data)
        self.assertNotIn("main_feedback_target", original["findings"])
        data["h3"]["rails"]["3V3_MAIN"]["nominal_v"] = 5.0
        changed = adapters.power.evaluate(data)
        feedback = next(row for row in changed["checks"] if row["id"] == "main_feedback_target")
        self.assertFalse(feedback["pass"])
        self.assertAlmostEqual(3.222, feedback["observed"])
        with patch.object(adapters.power, "build", return_value=changed):
            result = adapters.run_check("electrical.power_startup")
        self.assertEqual("fail", result["verdict"])
        self.assertIn("main_feedback_target", result["details"]["failed_prerequisites"])

    def test_unregistered_model_is_unqualified_not_a_proven_circuit_fault(self):
        result = self.run_power_fixture({
            "id": "h3_converter_source_is_installed_part", "pass": False,
            "detail": "Independent model registration missing.",
            "observed": {"native_identity_matches": True,
                         "declared_operating_domain_is_supported": True,
                         "independently_registered_binding_matches": False},
        })
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual([], result["details"]["failed_prerequisites"])

    def test_future_unclassified_obligation_cannot_pass(self):
        result = self.run_power_fixture({"id": "future_model_requirement", "pass": False,
                                         "detail": "No reviewed classification yet."})
        self.assertEqual("unqualified", result["verdict"])
        self.assertEqual(["future_model_requirement"], result["details"]["unqualified_prerequisites"])


if __name__ == "__main__":
    unittest.main()
