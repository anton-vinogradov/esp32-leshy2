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
        self.assertIn("| `s3` | `ESP32-S3-WROOM-1U-N16R2` | 32 | 3 | 1 | 36 |", rendered)
        self.assertIn("| `c5` | `ESP32-C5-WROOM-1U-N8R8` | 14 | 6 | 1 | 21 |", rendered)
        self.assertIn("| `rp` | `RP2354B A4", rendered)
        self.assertIn("| 48 | 0 | 0 | 48 |", rendered)
        self.assertIn("`RP=0 free`", rendered)
        self.assertIn("GPIO30", rendered)
        self.assertIn("QSPI_SS_USB_BOOT", rendered)

    def test_principled_diagram_names_each_physical_device_and_role(self):
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("flowchart TD", rendered)
        self.assertIn("Layout-only invisible spine", rendered)
        required_labels = (
            "HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3.5-inch QSPI IPS display and capacitive-touch assembly",
            "Hirose DM3AT-SF-PEJM5<br/>push-push microSD card connector",
            "Everest Semiconductor ES8311<br/>mono ADC/DAC audio codec",
            "Texas Instruments TLV9061IDBVR<br/>active high-impedance capture buffer",
            "Texas Instruments TMUX1136DGSR<br/>dual differential speaker-path selector",
            "Texas Instruments TS5A63157DCKR<br/>electret/codec transmit-audio selector",
            "Texas Instruments SN74LVC2G08DCUR<br/>reset-safe dual selector-request gate",
            "Diodes Incorporated PAM8302AASCR<br/>mono Class-D speaker amplifier",
            "Texas Instruments TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path",
            "onsemi CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM",
            "Texas Instruments TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection",
            "Texas Instruments BQ25798RQMR<br/>2S-configured buck-boost charger and NVDC system power path",
            "Analog Devices MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing",
            "Texas Instruments MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge",
            "Texas Instruments CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair",
            "Littelfuse 0451005.MRL<br/>slot-0 independent 5-A fast fuse",
            "Littelfuse 0451005.MRL<br/>slot-1 independent 5-A fast fuse",
            "Vishay WSL25125L000FEA<br/>5-mOhm Kelvin current shunt",
            "TDK B57332V5103F360<br/>cell-0 temperature sensor",
            "TDK B57332V5103F360<br/>cell-1 temperature sensor",
            "Diodes Incorporated 2N7002DW-7-F<br/>reset-default ALRT hold and explicit release",
            "onsemi BAV70LT1G<br/>AOLDO/fixture source isolation",
            "Diodes Incorporated BAT54-7-F<br/>admitted-system source isolation and priority",
            "MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver",
        )
        for label in required_labels:
            self.assertIn(label, rendered)
        for forbidden in (
            "display + separate microSD",
            "codec + Si4732-A10-GS",
            "dual RX + TX IR frontend",
            "nRF24 #0",
        ):
            self.assertNotIn(forbidden, rendered)

    def test_target_readme_principled_diagrams_stay_vertical_and_current(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        current_mpn_tokens = set()
        for device_id in candidate["instances"].values():
            mpn = self.database["devices"][device_id]["mpn"]
            part_tokens = [
                token.strip("(),")
                for token in mpn.split()
                if any(character.isdigit() for character in token)
            ]
            current_mpn_tokens.add(max(part_tokens, key=len))

        for readme_name in ("README.md", "README.ru.md"):
            readme = (GENERATOR.REPO_ROOT / readme_name).read_text(encoding="utf-8")
            section = (
                "Principled solution design"
                if readme_name == "README.md"
                else "Принципиальный дизайн решения"
            )
            diagram_start = readme.index("```mermaid", readme.index(section))
            diagram_end = readme.index("```", diagram_start + len("```mermaid"))
            diagram = readme[diagram_start:diagram_end]
            self.assertIn("flowchart TD", diagram, readme_name)
            self.assertIn("Layout-only invisible spine", diagram, readme_name)
            for mpn_token in current_mpn_tokens:
                self.assertIn(
                    mpn_token,
                    diagram,
                    f"{readme_name}: missing current MPN token {mpn_token}",
                )

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
            self.assertIn("S3 `32", normalized, readme_name)
            self.assertIn("C5 `14/6/1`", normalized, readme_name)
            self.assertIn("RP `48/0/0`", normalized, readme_name)
            for group in expected_groups:
                self.assertIn(group, normalized, f"{readme_name}: {group}")

    def test_target_readmes_remain_product_sites_not_review_ledgers(self):
        for readme_name in ("README.md", "README.ru.md"):
            readme = (GENERATOR.REPO_ROOT / readme_name).read_text(encoding="utf-8")
            for ledger_prefix in ("DEC-", "REV-", "FND-", "IMP-"):
                self.assertNotIn(ledger_prefix, readme, readme_name)
            for stale_heading in ("## Development state", "## Состояние разработки"):
                self.assertNotIn(stale_heading, readme, readme_name)
            for wide_table_heading in (
                "| Principled group |",
                "| Принципиальная группа |",
            ):
                self.assertNotIn(wide_table_heading, readme, readme_name)
            self.assertIn("<details>", readme, readme_name)
            self.assertIn("docs/status/current-state", readme, readme_name)

    def test_target_readmes_keep_accepted_supervised_2s_behavior(self):
        expected = {
            "README.md": (
                "supervised 2S battery",
                "two individually replaceable qualified 18650 cells",
                "both are required",
                "admits the pair",
            ),
            "README.ru.md": (
                "контролируемая батарея 2S",
                "две отдельно заменяемые квалифицированные 18650",
                "нужны обе",
                "допускает пару",
            ),
        }
        for readme_name, phrases in expected.items():
            readme = (GENERATOR.REPO_ROOT / readme_name).read_text(encoding="utf-8")
            normalized = " ".join(readme.split()).lower()
            for phrase in phrases:
                self.assertIn(phrase.lower(), normalized, readme_name)

    def test_sink_only_30w_pd_front_end_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0063", contract["decision"])
        self.assertEqual("DEC-0065", contract["battery_decision"])
        self.assertEqual("DEC-0066", contract["manager_decision"])
        self.assertEqual("DEC-0067", contract["manager_circuit_decision"])
        self.assertIn("supervised 2S", contract["battery_topology"])
        self.assertIn("both cells required", contract["battery_topology"])
        self.assertIn("MAX17320G20+T", contract["battery_manager"])
        self.assertIn("MSPM0C1104SDGS20R", contract["battery_manager"])
        self.assertIn("refuses any cell", contract["battery_recovery_policy"])
        self.assertIn("prequal are disabled", contract["battery_recovery_policy"])
        self.assertEqual(
            ["5V fallback at advertised Type-C current (<=3A)", "9V@3A", "15V@2A"],
            contract["sink_pdos"],
        )
        self.assertEqual(30, contract["maximum_input_power_w"])
        self.assertIn("source mode", contract["disabled"])
        self.assertIn("20V PDO", contract["disabled"])
        self.assertIn("GPIO19/20 remain direct", contract["usb2_data"])
        self.assertIn("GPIO47", contract["host_control"])

        expected_instances = {
            "pd_controller": "ti_tps25751d_refr",
            "pd_config_eeprom": "onsemi_cat24c512wi_gt3",
            "pd_vbus_tvs": "ti_tvs2200_drvr",
            "nvdc_charger": "ti_bq25798_rqmr",
            "pack_power_fet": "ti_csd87313dmst",
            "pack_fuse0": "littelfuse_0451005_mrl",
            "pack_fuse1": "littelfuse_0451005_mrl",
            "pack_shunt": "vishay_wsl25125l000fea",
            "pack_ntc0": "tdk_b57332v5103f360",
            "pack_ntc1": "tdk_b57332v5103f360",
            "pack_hold": "diodes_2n7002dw_7_f",
            "pack_supply_or": "onsemi_bav70lt1g",
            "pack_system_diode": "diodes_bat54_7_f",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        tps = self.database["devices"]["ti_tps25751d_refr"]
        self.assertEqual("23/24/25", tps["contacts"]["VBUS_IN"]["physical"])
        self.assertEqual("20/21/22", tps["contacts"]["PPHV"]["physical"])
        self.assertEqual("8 (fixed I2C target data)", tps["contacts"]["I2Ct_SDA"]["physical"])
        charger = self.database["devices"]["ti_bq25798_rqmr"]
        self.assertEqual("2/3", charger["contacts"]["VBUS"]["physical"])
        self.assertEqual("22/23", charger["contacts"]["BAT"]["physical"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        self.assertIn(
            ("pd_controller.PPHV", "nvdc_charger.VBUS", "PD_NEGOTIATED_VBUS"),
            routes,
        )
        self.assertIn(
            ("pd_controller.GPIO0", "pd_config_eeprom.WP", "PD_EEPROM_WP"),
            routes,
        )
        self.assertIn(
            ("pd_controller.GPIO1", "nvdc_charger.CE", "CHARGE_EN_N"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.CHG", "pack_power_fet.G1", "PACK_CHG_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.DIS", "pack_power_fet.G2", "PACK_DIS_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_power_fet.S2", "nvdc_charger.BAT", "PROTECTED_PACK_POSITIVE"),
            routes,
        )
        self.assertIn(
            ("pack_gauge.ZVC", "abstract:no-connect", "PACK_ZVC_UNUSED"),
            routes,
        )
        self.assertNotIn(
            ("pack_gauge.CHG", "abstract:exact high-side charge FET gate", "PACK_CHG_GATE"),
            routes,
        )
        admission = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "pack_admission"
        }
        self.assertEqual("PACK_CELL0_ADC", admission["PA24_A3"]["net"])
        self.assertEqual("PACK_STACK_ADC", admission["PA25_A2"]["net"])
        self.assertEqual(
            {"PA26_A1", "PA27_A0", "PA28_A5"},
            set(candidate["free_gpio"]["pack_admission"]),
        )
        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn(
            "Budget: **12 used + 3 reserved + 3 free = 18 exposed GPIO**.",
            rendered,
        )
        s3 = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "s3"
        }
        self.assertIn("pd_controller.I2Ct_SDA", s3["GPIO1"]["peers"])
        self.assertIn("pd_controller.I2Ct_SCL", s3["GPIO2"]["peers"])
        self.assertIn("pd_controller.I2Ct_IRQ", s3["GPIO37"]["peers"])
        self.assertEqual(["GPIO47"], candidate["free_gpio"]["s3"])

    def test_i2_hard_stop_and_tx_evidence_contract_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["safety_contract"]

        self.assertEqual("DEC-0061", contract["decision"])
        self.assertEqual("paper_reviewed_i2", contract["status"])
        self.assertEqual(
            ["s3.EN", "c5.EN", "rp.RUN"],
            contract["reset_fanout"]["targets"],
        )
        self.assertEqual(9, len(contract["tx_gate_map"]))
        self.assertEqual(
            [
                "S3_RF",
                "C5_RF",
                "NRF0_RF",
                "NRF1_RF",
                "NRF2_RF",
                "CC_RF",
                "VOICE_RF",
                "IR_OPTICAL",
            ],
            contract["evidence"]["channels"],
        )
        self.assertIn("0x20", contract["evidence"]["source_mask"])
        self.assertIn("RP_ANY_TX_N", contract["evidence"]["aggregate"])

        required_instances = {
            "safe_supervisor": "ti_tps3808g33_dbvr",
            "safe_conditioner": "nexperia_74lvc2g14gw_125",
            "safe_por_or": "nexperia_74lvc1g32gv_125",
            "safe_latch": "ti_sn74lvc1g74_dcur",
            "safe_reset_buffer": "ti_sn74lvc3g34_dcur",
            "safe_gate_a": "ti_sn74lvc08a_pwr",
            "safe_gate_b": "ti_sn74lvc08a_pwr",
            "safe_ptt_or": "nexperia_74lvc1g32gv_125",
            "det_s3": "adi_ltc5532_es6_trmpbf",
            "det_c5": "adi_ltc5532_es6_trmpbf",
            "det_nrf0": "adi_ltc5532_es6_trmpbf",
            "det_nrf1": "adi_ltc5532_es6_trmpbf",
            "det_nrf2": "adi_ltc5532_es6_trmpbf",
            "det_cc": "adi_ltc5507_es6_trmpbf",
            "det_voice": "adi_ltc5507_es6_trmpbf",
            "det_ir": "vishay_vemd1060x01",
            "evidence_cmp_a": "ti_tlv1824_pwr",
            "evidence_cmp_b": "ti_tlv1824_pwr",
            "evidence_mask": "ti_tca9534a_pwr",
        }
        for instance, device_id in required_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        rp = {
            row["contact"]: row
            for row in candidate["allocations"]
            if row["instance"] == "rp"
        }
        self.assertEqual("RP_ANY_TX_N", rp["GPIO22"]["net"])
        self.assertEqual("i", rp["GPIO22"]["direction"])
        self.assertIn("evidence_mask.SDA", rp["GPIO28"]["peers"])
        self.assertIn("evidence_mask.SCL", rp["GPIO29"]["peers"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        for label in (
            "TPS3808G33DBVR<br/>AON rail supervisor and power-on reset",
            "SN74LVC1G74DCUR<br/>asynchronous latched hard STOP",
            "LTC5532ES6#TRMPBF<br/>S3 2.4-GHz RF power detector",
            "TCA9534APWR<br/>eight-bit evidence source mask on local RP I2C0",
        ):
            self.assertIn(label, rendered)

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
        self.assertEqual(["GPIO47"], candidate["free_gpio"]["s3"])

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
        self.assertIn(("codec.OUTP", "audio_speaker_selector.S1A", "CODEC_DAC_OUT_P"), routes)
        self.assertIn(("codec.OUTN", "audio_speaker_selector.S2A", "CODEC_DAC_OUT_N"), routes)
        self.assertIn(("slow_io.P27", "audio_rx_mux.S", "RX_AUDIO_SOURCE_SEL"), routes)
        self.assertIn(("audio_speaker_selector.D1", "speaker_amp.IN_PLUS", "PAM_AUDIO_IN_P"), routes)
        self.assertIn(("audio_speaker_selector.D2", "speaker_amp.IN_MINUS", "PAM_AUDIO_IN_M"), routes)
        self.assertIn(("audio_tx_selector.COM", "voice.MIC_IN", "VOICE_MIC_IN"), routes)
        self.assertIn(("audio_safe_gate.1Y", "audio_speaker_selector.SEL1", "AUDIO_SPK_SEL_SAFE"), routes)
        self.assertIn(("audio_safe_gate.1Y", "audio_speaker_selector.SEL2", "AUDIO_SPK_SEL_SAFE"), routes)
        self.assertIn(("audio_safe_gate.2Y", "audio_tx_selector.IN", "AUDIO_TX_SEL_SAFE"), routes)
        self.assertIn("P27", candidate["contact_accounting"]["slow_io"]["used"])
        self.assertEqual({}, candidate["contact_accounting"]["slow_io"]["reserved"])
        self.assertEqual(["GPIO47"], candidate["free_gpio"]["s3"])
        self.assertEqual("AUDIO_ARM", s3["GPIO6"]["net"])
        self.assertEqual(["audio_safe_gate.1B", "audio_safe_gate.2B"], s3["GPIO6"]["peers"])
        expected_audio_instances = {
            "audio_rx_mux": "ti_sn74lvc1g3157_dbvr",
            "audio_capture_buffer": "ti_tlv9061_idbvr",
            "audio_speaker_selector": "ti_tmux1136_dgsr",
            "audio_tx_selector": "ti_ts5a63157_dckr",
            "audio_safe_gate": "ti_sn74lvc2g08_dcur",
            "speaker_amp": "diodes_pam8302a_ascr",
        }
        for instance, device_id in expected_audio_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

    def test_tac5111_reference_uses_exact_exposed_contacts(self):
        codec = self.database["devices"]["ti_tac5111_irger"]
        self.assertEqual("Texas Instruments TAC5111IRGER", codec["mpn"])
        self.assertEqual("reference_only", codec["qualification"])
        expected_physical = {
            "DREG": "1",
            "BCLK": "2",
            "FSYNC": "3",
            "DOUT": "4",
            "DIN": "5",
            "IOVDD": "6",
            "SCL": "7",
            "SDA": "8",
            "ADDR": "13",
            "IN1P": "15",
            "IN1M": "16",
            "OUT1M": "19",
            "OUT1P": "20",
            "AVDD": "23",
            "VREF": "24",
            "VSS_THERMAL": "exposed thermal pad",
        }
        for contact, physical in expected_physical.items():
            self.assertEqual(physical, codec["contacts"][contact]["physical"])
        for corner in ("VSS_A1", "VSS_A2", "VSS_A3", "VSS_A4"):
            self.assertIn(corner, codec["contacts"])

    def test_complete_audio_path_references_use_exact_order_codes_and_contacts(self):
        expected = {
            "ti_tmux1136_dgsr": (
                "Texas Instruments TMUX1136DGSR",
                {"SEL1": "1", "S1A": "2", "GND": "3", "S2A": "4", "SEL2": "5", "D2": "6", "S2B": "7", "VDD": "8", "S1B": "9", "D1": "10"},
            ),
            "ti_ts5a63157_dckr": (
                "Texas Instruments TS5A63157DCKR",
                {"NO": "1", "GND": "2", "NC": "3", "COM": "4", "VCC": "5", "IN": "6"},
            ),
            "ti_tlv9061_idbvr": (
                "Texas Instruments TLV9061IDBVR",
                {"OUT": "1", "V_MINUS": "2", "IN_PLUS": "3", "IN_MINUS": "4", "V_PLUS": "5"},
            ),
            "ti_sn74lvc2g08_dcur": (
                "Texas Instruments SN74LVC2G08DCUR",
                {"1A": "1", "1B": "2", "2Y": "3", "GND": "4", "2A": "5", "2B": "6", "1Y": "7", "VCC": "8"},
            ),
            "ti_sn74lvc1g3157_dbvr": (
                "Texas Instruments SN74LVC1G3157DBVR",
                {"B2": "1", "GND": "2", "B1": "3", "A_COM": "4", "VCC": "5", "S": "6"},
            ),
            "diodes_pam8302a_ascr": (
                "Diodes Incorporated PAM8302AASCR",
                {"SD": "1", "NC": "2", "IN_PLUS": "3", "IN_MINUS": "4", "VO_PLUS": "5", "VDD": "6", "GND": "7", "VO_MINUS": "8"},
            ),
        }
        for device_id, (mpn, contacts) in expected.items():
            with self.subTest(device=device_id):
                device = self.database["devices"][device_id]
                self.assertEqual(mpn, device["mpn"])
                self.assertIn(device["qualification"], ("reference_only", "verified_reference"))
                for contact, physical in contacts.items():
                    self.assertEqual(physical, device["contacts"][contact]["physical"])

        expected_orderable_urls = {
            "ti_tmux1136_dgsr": "https://www.ti.com/product/TMUX1136/part-details/TMUX1136DGSR",
            "ti_ts5a63157_dckr": "https://www.ti.com/product/TS5A63157/part-details/TS5A63157DCKR",
            "ti_tlv9061_idbvr": "https://www.ti.com/product/TLV9061/part-details/TLV9061IDBVR",
            "ti_sn74lvc2g08_dcur": "https://www.ti.com/product/SN74LVC2G08/part-details/SN74LVC2G08DCUR",
            "ti_sn74lvc1g3157_dbvr": "https://www.ti.com/product/SN74LVC1G3157/part-details/SN74LVC1G3157DBVR",
        }
        for device_id, url in expected_orderable_urls.items():
            with self.subTest(orderable_device=device_id):
                self.assertEqual(url, self.database["devices"][device_id]["orderable_source"]["url"])

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

    def test_rejects_profiled_antenna_kit_regression(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        policy = candidate["antenna_policy"]
        policy["kit_profile_decision"] = "IMP-0043"
        policy["availability_check_gate"] = "continuous_stock_polling"
        policy["full_field_kit_physical_items"] = 9
        policy["kit_profiles"]["nrf24"]["shared_exact_mpn"] = False
        errors = self.errors_for(candidates)
        self.assertTrue(any("kit_profile_decision must be 'DEC-0055'" in error for error in errors), errors)
        self.assertTrue(any("availability_check_gate must be 'exact_mpn_selection'" in error for error in errors), errors)
        self.assertTrue(any("full_field_kit_physical_items must be 12" in error for error in errors), errors)
        self.assertTrue(any("kit_profiles must be" in error for error in errors), errors)

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
        service["contacts"].remove("GPIO14")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing one complete service alternative" in error for error in errors), errors)

    def test_rejects_unaccounted_slow_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["contact_accounting"]["slow_io"]["used"].remove("P27")
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

    def test_dec0059_restores_full_s3_c5_service_on_1bit_sdio(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        allocations = {
            (row["instance"], row["contact"]): row
            for row in candidate["allocations"]
        }

        self.assertEqual("SDMMC_SLOT1_1BIT", allocations[("s3", "GPIO10")]["controller"])
        self.assertEqual("SDIO_SLAVE", allocations[("c5", "GPIO9")]["controller"])
        self.assertEqual("S3_C5_SDIO_D1_IRQ", allocations[("s3", "GPIO13")]["net"])
        self.assertEqual("UART0", allocations[("s3", "GPIO43")]["controller"])
        self.assertEqual("S3_UART_SERVICE_RX", allocations[("s3", "GPIO44")]["net"])
        self.assertEqual("USB_SERIAL_JTAG", allocations[("c5", "GPIO13")]["controller"])
        self.assertEqual("C5_USB_DP", allocations[("c5", "GPIO14")]["net"])
        self.assertEqual("I2C1_OR_UART1_OR_GPIO", allocations[("s3", "GPIO7")]["controller"])
        self.assertEqual(["GPIO47"], candidate["free_gpio"]["s3"])

        services = {
            item["instance"]: set(item["contacts"])
            for item in candidate["services"]
        }
        self.assertTrue({"GPIO19", "GPIO20", "GPIO43", "GPIO44"} <= services["s3"])
        self.assertTrue({"GPIO11", "GPIO12", "GPIO13", "GPIO14"} <= services["c5"])

        muxes = {item["id"]: item for item in candidate["mux_contracts"]}
        self.assertEqual(["GPIO7", "GPIO8", "GPIO9", "GPIO10"], muxes["C5_FIXED_SDIO"]["contacts"])
        self.assertEqual(["GPIO13", "GPIO14"], muxes["C5_NATIVE_USB"]["contacts"])
        self.assertEqual(["GPIO43", "GPIO44"], muxes["S3_UART0_SERVICE"]["contacts"])

        ipc = next(
            item for item in candidate["resource_contracts"]
            if item["id"] == "S3_C5_IPC"
        )
        self.assertIn("1-bit SDIO at 20 MHz raw 2.5 MB/s", ipc["deadline"])
        self.assertIn("4-bit fallback only if this gate fails", ipc["proof_gate"])

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("1-bit SDIO: S3 GPIO10,GPIO11,GPIO12,GPIO13", rendered)
        self.assertNotIn("4-bit SDIO: S3", rendered)

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
