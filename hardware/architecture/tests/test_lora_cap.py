import copy
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "hardware/accessories/generate.py"
SPEC = importlib.util.spec_from_file_location("lora_cap_generate", MODULE_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


class LoraCapTests(unittest.TestCase):
    def setUp(self):
        self.accessory, self.database = GENERATOR.load_sources()

    def errors_for(self, accessory=None):
        return GENERATOR.validate_sources(accessory or self.accessory, self.database)

    def test_checked_in_source_and_generated_artifacts_are_current(self):
        self.assertEqual([], self.errors_for())
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--check"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_two_exact_regional_assemblies_share_one_mechanical_contract(self):
        variants = self.accessory["variants"]
        self.assertEqual(
            {
                "LESHY2-LORA-CAP-01-EU868": "nicerf_lora1262_868",
                "LESHY2-LORA-CAP-01-US915": "nicerf_lora1262_915",
            },
            {name: row["module"] for name, row in variants.items()},
        )
        self.assertEqual([84.0, 24.0, 1.6], self.accessory["assembly"]["pcb_mm"])
        self.assertEqual(56.0, self.accessory["assembly"]["retention_pitch_mm"])
        for variant in variants.values():
            module = self.database["devices"][variant["module"]]
            self.assertEqual([16.0, 16.0, 2.1], module["dimensions_mm"])
            self.assertIn("integrated", module["electrical_contract"]["rf_switch"])
            self.assertEqual(16, len(module["contacts"]))

    def test_cap_bus_has_no_new_host_gpio_and_pin5_fails_released(self):
        pins = self.accessory["pin_contract"]
        self.assertEqual(list(range(1, 15)), [row["pin"] for row in pins])
        self.assertEqual("NC", pins[0]["custom_cap"])
        self.assertEqual("NC", pins[1]["custom_cap"])
        self.assertEqual("IDENTITY_SCL", pins[2]["custom_cap"])
        self.assertEqual("IDENTITY_SDA", pins[3]["custom_cap"])
        self.assertEqual("EXT_TX_EVIDENCE_N", pins[4]["custom_cap"])
        self.assertIn("released high", self.accessory["evidence_contract"]["output"])
        self.assertEqual(
            "ti_sn74lvc1g06_dckr",
            self.accessory["common_instances"]["evidence_driver"],
        )

    def test_physical_evidence_is_sampled_at_the_final_feed(self):
        routes = {
            (route["from"], route["to"], route["net"])
            for route in self.accessory["fixed_routes"]
        }
        for required in (
            ("variant_module.ANT", "rf_coupler.RF_IN", "LORA_RF_PRE_EVIDENCE"),
            ("rf_coupler.RF_OUT", "rf_sma.RF", "LORA_RF_FINAL_50R"),
            ("rf_coupler.COUPLED_FWD", "rf_detector.RFIN", "LORA_RF_FORWARD_SAMPLE"),
            ("rf_detector.V_UP", "evidence_comparator.IN_P", "RF_FORWARD_LEVEL"),
            ("evidence_comparator.OUT", "evidence_monostable.B", "RF_DETECTED_HIGH"),
            ("evidence_monostable.Q", "evidence_driver.A", "EVIDENCE_PULSE_HIGH"),
            ("evidence_driver.Y", "cap_header.PIN_5", "EXT_TX_EVIDENCE_N"),
        ):
            self.assertIn(required, routes)
        contract = self.accessory["evidence_contract"]
        self.assertEqual([10.0, 18.0], contract["pulse_acceptance_ms"])
        self.assertLessEqual(contract["host_poll_period_max_ms"], 5.0)
        self.assertGreaterEqual(
            contract["host_post_revoke_grace_max_ms"],
            contract["pulse_acceptance_ms"][1],
        )
        self.assertIn("never grants authorization", contract["security_boundary"])

    def test_identity_is_not_authorization(self):
        identity = self.accessory["identity_contract"]
        self.assertEqual("24AA02UIDT-I/OT", identity["device"])
        self.assertIn("only", identity["meaning"])
        for token in ("signed host manifest", "HIL qualification", "live evidence"):
            self.assertIn(token, identity["authorization"])

    def test_custom_accessory_cost_is_not_added_to_base_bom(self):
        base_candidate = GENERATOR.load_json(
            REPO_ROOT / "hardware/architecture/candidates/G2F-3I.json"
        )
        base_devices = set(base_candidate["instances"].values())
        for variant in self.accessory["variants"].values():
            self.assertNotIn(variant["module"], base_devices)
            known, gates = GENERATOR.known_variant_cost(
                self.accessory, self.database, variant
            )
            self.assertGreater(known, 9.0)
            self.assertLess(known, 13.0)
            self.assertEqual(1, len(gates))
            self.assertIn("LoRa1262", gates[0])

    def test_validator_rejects_non_inverting_evidence_driver(self):
        accessory = copy.deepcopy(self.accessory)
        accessory["common_instances"]["evidence_driver"] = "ti_sn74lvc1g07_dckr"
        errors = self.errors_for(accessory)
        self.assertTrue(any("inverting open-drain" in error for error in errors), errors)

    def test_validator_rejects_a_new_or_missing_cap_bus_pin(self):
        accessory = copy.deepcopy(self.accessory)
        accessory["pin_contract"].pop()
        errors = self.errors_for(accessory)
        self.assertTrue(any("pins 1..14" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
