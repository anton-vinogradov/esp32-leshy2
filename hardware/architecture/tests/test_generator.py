import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "generate.py"
SPEC = importlib.util.spec_from_file_location("architecture_generate", MODULE_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


class ArchitectureValidationTests(unittest.TestCase):
    def setUp(self):
        self.database, self.candidates = GENERATOR.load_sources()

    def errors_for(self, candidates=None):
        return GENERATOR.validate_sources(self.database, candidates or self.candidates)

    def test_checked_in_sources_are_valid(self):
        self.assertEqual([], self.errors_for())

    def test_principled_pinout_is_derived_from_current_leading_budget(self):
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("| `s3` | `ESP32-S3-WROOM-1U-N16R2` | 31 | 3 | 2 | 36 |", rendered)
        self.assertIn("| `c5` | `ESP32-C5-WROOM-1U-N8R8` | 14 | 6 | 1 | 21 |", rendered)
        self.assertIn("| `rp` | `RP2354B A4", rendered)
        self.assertIn("| 48 | 0 | 0 | 48 |", rendered)
        self.assertIn("`RP=0 free`", rendered)
        self.assertIn("GPIO30", rendered)
        self.assertIn("QSPI_SS_USB_BOOT", rendered)

    def test_target_readmes_publish_the_current_principled_pin_groups(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")

        def contacts(instance, prefixes):
            selected = {
                row["contact"]
                for row in candidate["allocations"]
                if row["instance"] == instance
                and any(row["net"].startswith(prefix) for prefix in prefixes)
            }
            return ",".join(sorted(selected, key=GENERATOR.natural_contact_key))

        expected_groups = (
            f"S3 `{contacts('s3', ('S3_C5_',))}`; C5 `{contacts('c5', ('S3_C5_',))}`",
            f"S3 `{contacts('s3', ('S3_RP_', 'RP_ALERT_'))}`; RP `{contacts('rp', ('S3_RP_', 'RP_ALERT_'))}`",
            f"S3 `{contacts('s3', ('DISPLAY_SD_', 'SD_SPI_', 'LCD_'))}`",
            f"S3 `{contacts('s3', ('I2S_', 'SYS_I2C_'))}`",
            f"S3 `{contacts('s3', ('UNIT_',))}`",
            f"C5 `{contacts('c5', ('IR_',))}`",
            f"RP `{contacts('rp', ('NRF0_',))}`",
            f"RP `{contacts('rp', ('NRF1_',))}`",
            f"RP `{contacts('rp', ('NRF2_',))}`",
            f"RP `{contacts('rp', ('CC_',))}`",
            f"RP `{contacts('rp', ('VOICE_', 'PTT_'))}`",
            f"RP `{contacts('rp', ('U214_',))}`",
        )
        for readme_name in ("README.md", "README.ru.md"):
            readme = (GENERATOR.REPO_ROOT / readme_name).read_text(encoding="utf-8")
            normalized = " ".join(readme.split())
            self.assertIn("DEC-0051", normalized, readme_name)
            self.assertIn("S3 `31", normalized, readme_name)
            self.assertIn("C5 `14/6/1`", normalized, readme_name)
            self.assertIn("RP `48/0/0`", normalized, readme_name)
            for group in expected_groups:
                self.assertIn(group, normalized, f"{readme_name}: {group}")

    def test_qspi_display_decision_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertEqual("DISPLAY_SD_SPI_D1", s3["GPIO4"]["net"])
        self.assertEqual("io", s3["GPIO4"]["direction"])
        self.assertIn("high-Z", s3["GPIO4"]["sharing_proof"])
        self.assertEqual("LCD_QSPI_D2", s3["GPIO41"]["net"])
        self.assertEqual("LCD_QSPI_D3", s3["GPIO42"]["net"])
        self.assertNotIn("GPIO41", candidate["free_gpio"]["s3"])
        self.assertNotIn("GPIO42", candidate["free_gpio"]["s3"])
        display_contract = next(
            item for item in candidate["resource_contracts"]
            if item["id"] == "DISPLAY_SD_SPI"
        )
        self.assertIn("<=1 ms", display_contract["arbitration"])
        self.assertNotIn("256 B", display_contract["arbitration"])

    def test_exact_hmx_display_electrical_fit_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("qdtech_hmx035ctft_001", candidate["instances"]["display"])

        display = self.database["devices"][candidate["instances"]["display"]]
        self.assertEqual(
            "HMX035CTFT-001 (QDtech schematic assembly marking)", display["mpn"]
        )
        expected_physical = {
            "TP_I2C_SCL": "1",
            "TP_I2C_SDA": "2",
            "TP_INT": "3",
            "TP_RESET": "4 (TP_RESXP)",
            "QSPI_CS": "9 (CS)",
            "QSPI_D1": "10 (RS)",
            "QSPI_CLK": "11 (WR)",
            "QSPI_D0": "13 (SDA)",
            "RESET": "15",
            "QSPI_D2": "17 (DB0)",
            "QSPI_D3": "18 (DB1)",
            "LEDA": "33",
            "IM0": "38",
            "IM1": "39",
            "IM2": "40",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, display["contacts"][contact]["physical"])

        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertEqual(["sd.DAT0", "display.QSPI_D1"], s3["GPIO4"]["peers"])
        self.assertIn("display.QSPI_CLK", s3["GPIO35"]["peers"])
        self.assertIn("display.QSPI_D0", s3["GPIO36"]["peers"])
        self.assertEqual("display.QSPI_CS", s3["GPIO38"]["peers"][0])
        self.assertEqual("LCD_TOUCH_INT", s3["GPIO39"]["net"])
        self.assertEqual("i", s3["GPIO39"]["direction"])
        self.assertEqual("GPIO_IRQ", s3["GPIO39"]["controller"])
        self.assertEqual(["display.TP_INT"], s3["GPIO39"]["peers"])
        self.assertEqual(["display.QSPI_D2"], s3["GPIO41"]["peers"])
        self.assertEqual(["display.QSPI_D3"], s3["GPIO42"]["peers"])
        self.assertNotIn("LCD_DC", {row["net"] for row in s3.values()})
        self.assertEqual(["GPIO6", "GPIO43"], candidate["free_gpio"]["s3"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(("slow_io.P06", "display.RESET", "LCD_RST_N"), routes)
        self.assertIn(("slow_io.P07", "display.TP_RESET", "TOUCH_RST_N"), routes)
        self.assertIn(("abstract:qualified-display-3v3", "display.IM1", "LCD_IM1_HIGH"), routes)
        self.assertIn(("display.IM0", "abstract:display-ground", "LCD_IM0_LOW"), routes)
        self.assertIn(("display.IM2", "abstract:display-ground", "LCD_IM2_LOW"), routes)

    def test_exact_es8311_digital_fit_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("everest_es8311_qfn20", candidate["instances"]["codec"])

        codec = self.database["devices"][candidate["instances"]["codec"]]
        self.assertEqual("Everest Semiconductor ES8311", codec["mpn"])
        expected_physical = {
            "CCLK": "1",
            "MCLK": "2",
            "SCLK": "6 (SCLK/DMIC_SCL)",
            "ASDOUT": "7",
            "LRCK": "8",
            "DSDIN": "9",
            "OUTP": "12",
            "OUTN": "13",
            "MIC1N": "17",
            "MIC1P": "18 (MIC1P/DMIC_SDA)",
            "CDATA": "19",
            "CE": "20",
            "EPAD": "21 (exposed thermal pad)",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, codec["contacts"][contact]["physical"])

        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertIn("codec.CDATA", s3["GPIO1"]["peers"])
        self.assertIn("codec.CCLK", s3["GPIO2"]["peers"])
        self.assertEqual(["codec.SCLK"], s3["GPIO15"]["peers"])
        self.assertEqual(["codec.LRCK"], s3["GPIO16"]["peers"])
        self.assertEqual(["codec.DSDIN"], s3["GPIO17"]["peers"])
        self.assertEqual(["codec.ASDOUT"], s3["GPIO18"]["peers"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(
            ("slow_io.P10", "abstract:codec-power-switch-enable", "CODEC_PWR_EN"),
            routes,
        )
        self.assertNotIn("CODEC_EN", {route["net"] for route in candidate["fixed_routes"]})
        self.assertIn(
            ("abstract:codec-address-high-3v3", "codec.CE", "CODEC_I2C_ADDR_0X19"),
            routes,
        )
        self.assertIn(("codec.MCLK", "abstract:no-connect", "CODEC_MCLK_NC"), routes)
        self.assertIn(
            ("codec.OUTP", "abstract:qualified-codec-differential-output-routing", "CODEC_DAC_OUT_P"),
            routes,
        )
        self.assertIn(
            ("codec.OUTN", "abstract:qualified-codec-differential-output-routing", "CODEC_DAC_OUT_N"),
            routes,
        )
        self.assertEqual(["GPIO6", "GPIO43"], candidate["free_gpio"]["s3"])

    def test_rejects_duplicate_json_key_before_validation(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            GENERATOR.reject_duplicate_keys([("GPIO0", {}), ("GPIO0", {})])

    def test_rejects_module_internal_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].append("GPIO15")
        errors = self.errors_for(candidates)
        self.assertTrue(any("GPIO15" in error and "unknown GPIO" in error for error in errors), errors)

    def test_rejects_duplicate_allocation(self):
        candidates = copy.deepcopy(self.candidates)
        candidates[0]["allocations"].append(copy.deepcopy(candidates[0]["allocations"][0]))
        errors = self.errors_for(candidates)
        self.assertTrue(any("duplicate allocation" in error for error in errors), errors)

    def test_rejects_integrated_nrf_antenna_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["antenna_policy"]["integrated_pcb_antenna_baseline"] = True
        candidate["antenna_policy"]["nrf_dedicated_sma_count"] = 2
        candidate["instances"]["nrf2"] = "ebyte_e01_ml01s"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("integrated_pcb_antenna_baseline must be False" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("nrf_dedicated_sma_count must be 3" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("nrf2 must use compact IPEX reference" in error for error in errors),
            errors,
        )

    def test_rejects_nine_sma_identity_or_si4732_split_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["antenna_policy"]["base_onboard_sma_count"] = 8
        candidate["antenna_policy"]["base_onboard_sma_paths"].remove("RX-AM/LW")
        candidate["antenna_policy"]["si4732_port_topology"] = "shared_switched_port"
        candidate["antenna_policy"]["si4732_shared_switch"] = True
        candidate["antenna_policy"]["si4732_ami_external_profile"] = "generic_long_coax"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("base_onboard_sma_count must be 9" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("base_onboard_sma_paths must be" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_port_topology must be 'dedicated_fmi_and_ami'" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_shared_switch must be False" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("si4732_ami_external_profile must be" in error for error in errors),
            errors,
        )

    def test_rejects_external_sma_polarity_decision_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        policy = candidate["antenna_policy"]
        policy["external_connector_decision"] = "IMP-0042"
        policy["device_connector_by_path"]["N24-0"] = "rp_sma_jack_pin_center"
        policy["antenna_mate_by_path"]["C5-2G4/5"] = "sma_plug_pin_center"
        policy["antenna_qualification_gate"]["minimum_orderable_qualified_mpns_per_group"] = 1
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("external_connector_decision must be 'DEC-0050'" in error for error in errors),
            errors,
        )
        self.assertTrue(any("device_connector_by_path must be" in error for error in errors), errors)
        self.assertTrue(any("antenna_mate_by_path must be" in error for error in errors), errors)
        self.assertTrue(any("antenna_qualification_gate must be" in error for error in errors), errors)

    def test_exact_sa518_does_not_regress_to_a_fictional_sq_pin(self):
        voice = self.database["devices"]["nicerf_sa518_v11"]
        self.assertNotIn("SQ", voice["contacts"])
        self.assertIn("AUDIO_ON", voice["contacts"])
        self.assertIn("UPDATE", voice["contacts"])
        for candidate in self.candidates:
            self.assertFalse(
                any(row["net"] == "VOICE_SQ" for row in candidate["allocations"]),
                candidate["id"],
            )

    def test_leading_voice_and_receiver_paths_use_exact_exposed_contacts(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        self.assertEqual("nicerf_sa518_v11", candidate["instances"]["voice"])
        self.assertEqual("skyworks_si4732_a10_gs", candidate["instances"]["receiver"])
        voice_service = next(s for s in candidate["services"] if s["instance"] == "voice")
        self.assertEqual({"UPDATE", "UART_TX", "UART_RX", "PD"}, set(voice_service["contacts"]))
        endpoints = {
            route[endpoint]
            for route in candidate["fixed_routes"]
            for endpoint in ("from", "to")
        }
        self.assertIn("voice.UPDATE", endpoints)
        self.assertIn("voice.PD", endpoints)
        self.assertIn("receiver.FMI", endpoints)
        self.assertIn("receiver.AMI", endpoints)
        self.assertIn("receiver.GPO2_INTB", endpoints)

    def test_rf_micro_connector_provenance_stays_device_specific(self):
        s3 = self.database["devices"]["esp32_s3_wroom_1u_n16r2"]["rf_connector"]
        c5 = self.database["devices"]["esp32_c5_wroom_1u_n8r8"]["rf_connector"]
        nrf = self.database["devices"]["ebyte_e01_ml01ipx"]["rf_connector"]
        expected_families = ["Hirose U.FL", "I-PEX MHF I", "Amphenol AMC"]
        self.assertEqual(expected_families, s3["compatible_mating_families"])
        self.assertEqual(expected_families, c5["compatible_mating_families"])
        self.assertEqual([], nrf["compatible_mating_families"])
        self.assertEqual(
            "exact_mating_family_unproven_requires_specimen_gate",
            nrf["qualification"],
        )
        self.assertEqual("FND-0057", nrf["finding"])

    def test_rejects_allocated_strap_without_proof(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        row = next(a for a in candidate["allocations"] if a["instance"] == "c5" and a["contact"] == "GPIO3")
        row.pop("strap_proof")
        errors = self.errors_for(candidates)
        self.assertTrue(any("strap without strap_proof" in error for error in errors), errors)

    def test_rejects_unaccounted_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].remove("GPIO24")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted GPIO" in error and "GPIO24" in error for error in errors), errors)

    def test_rejects_missing_recovery_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        service = next(s for s in candidate["services"] if s["instance"] == "rp")
        service["contacts"].remove("SWDIO")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing service contacts" in error and "SWDIO" in error for error in errors), errors)

    def test_accepts_one_complete_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        self.assertIn("GPIO11", service["contacts"])
        self.assertIn("GPIO12", service["contacts"])
        self.assertEqual([], self.errors_for(candidates))

    def test_rejects_partial_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        service["contacts"].remove("GPIO12")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing one complete service alternative" in error for error in errors), errors)

    def test_rejects_unaccounted_slow_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["contact_accounting"]["slow_io"]["reserved"].pop("P27")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted allocatable contacts" in error and "P27" in error for error in errors), errors)

    def test_rejects_scheduled_resource_without_arbitration(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["sharing"] == "scheduled")
        resource.pop("arbitration")
        errors = self.errors_for(candidates)
        self.assertTrue(any("scheduled resource lacks arbitration" in error for error in errors), errors)

    def test_rejects_radio_resource_made_shared(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["id"] == "NRF1_SPI")
        resource["sharing"] = "scheduled"
        resource["arbitration"] = "invalid regression fixture"
        errors = self.errors_for(candidates)
        self.assertTrue(any("exclusive resource NRF1_SPI is not dedicated" in error for error in errors), errors)

    def test_rejects_missing_required_resource_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["resource_contracts"] = [
            r for r in candidate["resource_contracts"] if r["id"] != "S3_C5_IPC"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing required resource contracts" in error and "S3_C5_IPC" in error for error in errors), errors)

    def test_rejects_controller_not_available_on_exact_device(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        candidate["controllers"]["c5"].append("IMAGINARY_SPI9")
        candidate["allocations"][32]["controller"] = "IMAGINARY_SPI9"
        errors = self.errors_for(candidates)
        self.assertTrue(any("unavailable controllers" in error and "IMAGINARY_SPI9" in error for error in errors), errors)

    def test_rejects_pio_pin_outside_selected_b_package_window(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        row = next(
            allocation
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp" and allocation["net"] == "NRF0_MISO"
        )
        power_row = next(
            allocation
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp" and allocation["net"] == "NRF_GROUP_PWR_EN"
        )
        row["contact"] = "GPIO15"
        power_row["contact"] = "GPIO30"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("NRF0" not in error and "outside GPIO16..GPIO47" in error for error in errors),
            errors,
        )

    def test_rejects_missing_shared_pio_window_selection(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["controller_gpio_windows"] = [
            window
            for window in candidate["controller_gpio_windows"]
            if "PIO0_SM0_RF_SPI" not in window["controllers"]
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("PIO0_GPIO_BASE missing GPIO-window selection" in error for error in errors),
            errors,
        )

    def test_rejects_overbooked_dma_capacity(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        capacity = next(
            item for item in candidate["capacity_contracts"] if item["id"] == "RP_DMA_CHANNELS"
        )
        capacity["claims"][0]["units"] += 1
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("14 claimed + 3 reserve != 16 available" in error for error in errors),
            errors,
        )

    def test_rejects_fixed_mux_contact_drift(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        mux = next(item for item in candidate["mux_contracts"] if item["id"] == "RP_UART1_GNSS")
        mux["contacts"][1] = "GPIO42"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("RP_UART1_GNSS" not in error and "declared contacts" in error for error in errors),
            errors,
        )

    def test_rejects_missing_required_mux_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["mux_contracts"] = [
            mux for mux in candidate["mux_contracts"] if mux["id"] != "C5_FIXED_SDIO"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("missing required mux contracts" in error and "C5_FIXED_SDIO" in error for error in errors),
            errors,
        )

    def test_rejects_full_mix_that_allows_peer_standby(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["peer_standby_forbidden"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("full mix must forbid peer standby" in error for error in errors),
            errors,
        )

    def test_rejects_missing_required_quiet_state_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["quiet_state_policy"]["contracts"] = [
            contract
            for contract in candidate["quiet_state_policy"]["contracts"]
            if contract["id"] != "N24_QUIET"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("missing required quiet-state contracts" in error and "N24_QUIET" in error for error in errors),
            errors,
        )

    def test_rejects_full_mix_without_observer_hil(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["rf_acceptance"]["external_observer_fixture"] = ""
        group["rf_acceptance"]["hil_required"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("full mix RF acceptance missing external_observer_fixture" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("full mix RF acceptance must require HIL" in error for error in errors),
            errors,
        )

    def test_rejects_div_pre_hil_as_production_acceptance(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        group = next(
            group
            for group in candidate["signal_group_policy"]["groups"]
            if group["id"] == "SG-N24"
        )
        group["rf_acceptance"]["fixture_levels"] = ["L0_DIV_DIV_PRE_HIL"]
        group["rf_acceptance"]["production_acceptance_level"] = "L0_DIV_DIV_PRE_HIL"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("must separate L0 DIV pre-HIL from T1 target HIL" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("production RF acceptance must require T1_TARGET" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
