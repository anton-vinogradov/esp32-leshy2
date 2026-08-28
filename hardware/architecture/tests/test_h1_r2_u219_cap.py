import copy
import csv
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/architecture/h1_r2_u219_cap.py"
SPEC = importlib.util.spec_from_file_location("h1_r2_u219_cap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2U219CapTests(unittest.TestCase):
    def setUp(self):
        self.model = MODULE.load_json(MODULE.SOURCE)
        self.base = MODULE.load_json(MODULE.BASE)

    def errors_for(self, model=None, base=None):
        return MODULE.validate(model or self.model, base or self.base)

    def test_checked_in_contract_and_generated_evidence_are_current(self):
        self.assertEqual([], self.errors_for())
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_u214_and_u219_are_same_slot_mutually_exclusive_profiles(self):
        accessories = self.model["accessories"]
        self.assertEqual("exactly_one", accessories["slot_population"])
        self.assertEqual("forbidden", accessories["hot_profile_change"])
        self.assertEqual("branch_off_and_pin10_disconnected", accessories["unknown_or_unsigned_profile"])
        self.assertEqual([84.0, 24.0, 19.7], accessories["u219"]["envelope_mm"])
        self.assertEqual(96, accessories["u219"]["listed_5v_current_ma"])
        self.assertEqual("POWER_EN", accessories["u219"]["official_pin_table"]["8"])
        self.assertEqual("NFC_CS", accessories["u219"]["official_pin_table"]["10"])
        self.assertEqual("CC_CS", accessories["u219"]["official_pin_table"]["14"])
        self.assertEqual("SCL", accessories["u219"]["official_pin_table"]["3"])
        self.assertEqual("SDA", accessories["u219"]["official_pin_table"]["4"])
        self.assertIn("BLANK/undocumented-current", accessories["u219"]["official_pin_table"]["7"])
        self.assertEqual(
            {"7"},
            {
                pin for pin, role in accessories["u219"]["official_pin_table"].items()
                if "undocumented-current" in role
            },
        )

    def test_u219_scl_sda_reuse_existing_isolated_rf_rp_i2c(self):
        i2c = self.model["shared_i2c_contract"]
        self.assertEqual("rear RF RP2354B I2C1 domain", i2c["owner"])
        self.assertIn("contact 3 SCL", i2c["scl"])
        self.assertIn("RF RP GPIO29", i2c["scl"])
        self.assertIn("contact 4 SDA", i2c["sda"])
        self.assertIn("RF RP GPIO28", i2c["sda"])
        self.assertIn("TCA4307DGKR", i2c["scl"])
        self.assertIn("TCA4307DGKR", i2c["sda"])
        self.assertIn("no new GPIO", i2c["isolation"])

    def test_shared_spi_owner_is_rear_rf_rp_not_hub_rp(self):
        spi = self.model["shared_spi_contract"]
        self.assertEqual("rear RF RP2354B PIO/SPI domain", spi["owner"])
        self.assertNotIn("rear Hub", spi["owner"])

    def test_pin10_is_disconnected_by_aon_hardware_until_qualified(self):
        pin10 = self.model["pin_10_bidirectional_boundary"]
        self.assertEqual("SN74CBTLV1G125DCKR", pin10["switch_mpn"])
        self.assertEqual("SN74LVC1G06DCKR", pin10["aon_enable"]["inverter_mpn"])
        self.assertEqual("AON_SAFE_3V3", pin10["aon_enable"]["supply"])
        self.assertIn("10 kOhm to AON_SAFE_3V3", pin10["aon_enable"]["switch_oe_pull"])
        self.assertIn("disconnects pin 10", pin10["aon_enable"]["loss_behavior"])
        self.assertIn("u214_return_buffer channel 1 on contact 10", pin10["supersedes"])
        self.assertIn("u214_series_busy 22-Ohm resistor", pin10["supersedes"])
        self.assertIn("u214_return_buffer channels 2..4", pin10["preserves"])

    def test_pin8_reuses_protected_output_and_fails_low(self):
        pin8 = self.model["pin_8_power_boundary"]
        self.assertEqual(8, pin8["connector_contact"])
        self.assertEqual("RP GPIO14", pin8["host_gpio"])
        self.assertEqual("low", pin8["fail_safe_default"])
        self.assertIn("u214_host_buffer_a.1Y", pin8["existing_path_reused"])
        self.assertTrue(any("configured low" in row for row in pin8["requirements"]))
        self.assertTrue(any("FAULT_KILL" in row for row in pin8["requirements"]))
        power = self.model["protected_5v_boundary"]
        self.assertEqual(96, power["u219_listed_load_ma"])
        self.assertIn("TPS259470", power["protection"])
        self.assertIn("do not energize", power["contact_7_gate"])
        self.assertIn("reject the U219 profile", power["failure_rule"])

    def test_jlc_orderability_uses_can_presale_not_displayed_stock(self):
        parts = self.model["jlcpcb_live_surface"]["parts"]
        self.assertEqual(
            {"C131992", "C7828", "C47546", "C34731"},
            {row["jlc_number"] for row in parts},
        )
        for row in parts:
            self.assertGreater(row["can_presale_number"], 0)
            self.assertEqual(1, row["moq"])
            self.assertEqual("SMT", row["assembly_type"])
            self.assertTrue(row["standard_pcba"])

        unavailable = copy.deepcopy(self.model)
        unavailable["jlcpcb_live_surface"]["parts"][0]["can_presale_number"] = 0
        unavailable["jlcpcb_live_surface"]["parts"][0]["displayed_stock"] = 999999
        errors = self.errors_for(unavailable)
        self.assertTrue(any("available-order quantity" in error for error in errors), errors)

    def test_ev_n9_is_independent_physical_evidence_and_not_authorization(self):
        evidence = self.model["nfc_field_evidence"]
        self.assertEqual("EV_N9_U219_NFC", evidence["signal"])
        self.assertIn("never identity", evidence["function"])
        self.assertIn("never authorization", evidence["function"])
        self.assertEqual(
            {
                "TCA9535 evidence_mask.P12 diagnostic input",
                "existing evidence_or_4.K2 spare cathode",
                "existing evidence_or_4.A_COMMON -> ANY_TX_AON_N",
            },
            set(evidence["digital_fanout"]),
        )
        path = " ".join(evidence["analog_path"])
        for token in ("printed loop", "BAT54S,215", "full-wave", "LMV331IDBVR", "open-collector"):
            self.assertIn(token, path)
        self.assertIn("DNP C0G", evidence["pickup"]["tuning"])
        self.assertIn("unsafe failure", evidence["polarity"]["open_or_false_negative"])

    def test_u219_radio_policy_is_conservatively_restricted(self):
        policy = self.model["radio_policy"]
        self.assertEqual(
            {"SFSTXON", "STX", "PATABLE write", "TX FIFO write"},
            set(policy["cc1101"]["forbidden_commands"]),
        )
        self.assertIn("unconditionally forbidden", policy["cc1101"]["hardware_tx_evidence"])
        self.assertEqual(
            {"tag write", "card emulation", "field-on without EV_N9 lease"},
            set(policy["nfc"]["forbidden"]),
        )
        self.assertIn("blocked until", policy["nfc"]["runtime_enable"])

    def test_fixed_bom_delta_and_evt5_math_are_reproducible(self):
        bom = self.model["bom_delta"]
        self.assertAlmostEqual(0.4520, bom["pin10_new_active_usd_per_device"], places=4)
        self.assertAlmostEqual(0.2325, bom["nfc_evidence_new_active_usd_per_device"], places=4)
        self.assertAlmostEqual(0.7585, bom["fixed_added_usd_per_device"], places=4)
        self.assertAlmostEqual(0.7430, bom["net_fixed_usd_per_device"], places=4)
        self.assertAlmostEqual(3.7150, bom["trial_lot_5_net_fixed_usd"], places=4)
        rows = list(csv.DictReader(io.StringIO(MODULE.render_csv(self.model))))
        self.assertEqual("0.7430", rows[-1]["line_per_device_usd"])
        self.assertEqual("3.7150", rows[-1]["line_evt5_usd"])
        self.assertEqual(1, sum(row["change"] == "DNP" for row in rows))

    def test_specimen_vna_and_hil_gates_are_not_overclaimed(self):
        self.assertFalse(self.model["scope"]["production_or_hil_claim"])
        gates = self.model["acceptance_gates"]
        self.assertGreaterEqual(len(gates), 6)
        self.assertTrue(all(not row["closed"] for row in gates))
        requirements = " ".join(row["requirement"] for row in gates)
        for token in ("RF_SW1", "VNA", "no-false-negative", "CC1101 command/register trace"):
            self.assertIn(token, requirements)
        self.assertNotIn("contacts 3, 4 and 7", requirements)


if __name__ == "__main__":
    unittest.main()
