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

    def test_exact_polarized_holder_and_three_ntc_contract_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0077", contract["battery_holder_decision"])
        self.assertIn("Keystone Electronics 1048P", contract["battery_holder_profile"])
        self.assertIn("protected button-top", contract["battery_holder_profile"])
        self.assertIn("thermally worst slot", contract["battery_thermal_coupling"])
        self.assertNotIn(
            "mechanical reverse-insertion blocking and all NTC cell coupling",
            contract["remaining_i3"],
        )
        self.assertEqual("keystone_1048p", candidate["instances"]["pack_holder"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("pack_holder.SLOT0_POS", "pack_fuse0.END_1", "PACK_SLOT0_POSITIVE_RAW"),
            ("pack_holder.SLOT0_NEG", "pack_gauge.GND", "PACK_LOCAL_GND"),
            ("pack_holder.SLOT1_NEG", "abstract:protected-2s-midpoint", "PACK_2S_MIDPOINT"),
            ("pack_holder.SLOT1_POS", "pack_fuse1.END_1", "PACK_SLOT1_POSITIVE_RAW"),
        ):
            self.assertIn(route, routes)

        rendered = GENERATOR.render_principled_pinout(self.database, self.candidates)
        self.assertIn("Keystone Electronics 1048P", rendered)
        self.assertIn("indexed thermally worst-slot contact", rendered)

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
            "Keystone Electronics 1048P<br/>polarized dual protected-button-top 18650 retention and four independent contacts",
            "XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #0",
            "XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #1",
            "Diodes Incorporated 2N7002DW-7-F<br/>reset-default ALRT hold and explicit release",
            "onsemi BAV70LT1G<br/>AOLDO/fixture source isolation",
            "Diodes Incorporated BAT54-7-F<br/>admitted-system source isolation and priority",
            "Texas Instruments TPUL2G223BQBR<br/>non-retriggerable pulse limiter and refractory lockout",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% diagnostic-pulse timing resistor",
            "Murata GRM31C5C1H224JE02L<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor",
            "Yageo RC0402FR-07620KL<br/>620-kOhm 1% refractory-lockout timing resistor",
            "TDK C1608X7R1C105K080AC<br/>1-uF 16-V X7R refractory-lockout timing capacitor",
            "TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R one-shot bypass capacitor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-trigger fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-gate fail-low resistor",
            "Diodes Incorporated DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET",
            "Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #0",
            "Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #1",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #0",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #1",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% midpoint-divider bottom resistor",
            "Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R midpoint ADC filter capacitor",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #0",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #1",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #2",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #3",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #4",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% stack-divider bottom resistor",
            "Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R stack ADC filter capacitor",
            "Texas Instruments TPS629203DRLR<br/>low-IQ always-on 3.3-V safety converter",
            "Sunlord WPN201612H2R2MT<br/>2.2-uH shielded AON converter inductor",
            "Yageo RC0402FR-0742K2L<br/>42.2-kOhm 1% AON mode/configuration resistor",
            "TDK CGA5L1X7R1E475K160AC<br/>4.7-uF 25-V X7R AON input capacitor",
            "Murata GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON raw-output capacitor",
            "Texas Instruments TPS25961DRVR<br/>independent AON overvoltage/current/short cutoff",
            "Yageo RC0402FR-07240KL<br/>240-kOhm 1% AON eFuse current-limit resistor",
            "Yageo RC0402FR-07196KL<br/>196-kOhm 1% AON eFuse OVLO top resistor",
            "Murata GRM188R60J106ME47D<br/>10-uF 6.3-V X5R protected-AON output capacitor",
            "Yageo RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% AON POR pull-up resistor",
            "Texas Instruments TPS564252DRLR<br/>fixed 3.3-V 4-A main converter",
            "Sunlord MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main-converter bulk input capacitor",
            "TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R main-converter HF input capacitor",
            "Yageo RC0402FR-0745K3L<br/>45.3-kOhm 1% main feedback top resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% main feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G main feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #1",
            "Texas Instruments TPS25974LRPWR<br/>main latch-off overvoltage circuit-breaker eFuse with protected PG",
            "Yageo RT0402BRD07191KL<br/>191-kOhm 0.1% main eFuse OVLO top resistor",
            "Yageo RT0402BRD07100KL<br/>100-kOhm 0.1% main eFuse OVLO bottom resistor",
            "Yageo RC0402FR-07100KL<br/>100-kOhm 1% main-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% wired-low power-fault pull-up resistor",
            "Texas Instruments TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter",
            "Sunlord MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice-converter bulk input capacitor",
            "TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R voice-converter HF input capacitor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor",
            "Yageo RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G voice feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #1",
            "Texas Instruments TPS25974LRPWR<br/>voice latch-off overvoltage circuit-breaker eFuse with protected PG",
            "Yageo RC0402FR-07270KL<br/>270-kOhm 1% voice eFuse OVLO top resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice power-good pull-up resistor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice PG-qualifier base resistor",
            "Diodes Incorporated MMBT3904-7-F<br/>voice-rail enable-qualified PG fault transistor",
            "Texas Instruments TPS564252DRLR<br/>fixed 5.0-V 4-A accessory converter",
            "Sunlord MWSA0503S-4R7MT<br/>4.7-uH accessory-rail power inductor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory-converter bulk input capacitor",
            "TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R accessory-converter HF input capacitor",
            "Yageo RC0402FR-07220KL<br/>220-kOhm 1% accessory feedback top resistor",
            "Yageo RC0402FR-0730KL<br/>30-kOhm 1% accessory feedback bottom resistor",
            "KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G accessory feed-forward capacitor",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #0",
            "Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #1",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory-enable fail-low resistor",
            "Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory power-good pull-up resistor",
            "Yageo RC0402FR-0768KL<br/>68-kOhm 1% accessory PG-qualifier base resistor",
            "Diodes Incorporated MMBT3904-7-F<br/>accessory-rail enable-qualified PG fault transistor",
            "Texas Instruments TPS259470LRPWR<br/>true-reverse-blocking latch-off accessory eFuse and current monitor",
            "Yageo RC0402FR-072K21L<br/>2.21-kOhm 1% eFuse current-limit resistor",
            "Murata GRM155R71H472KA01D<br/>4.7-nF 50-V X7R eFuse startup-slew capacitor",
            "Murata GRM188R71E224KA88D<br/>220-nF 25-V X7R post-start transient-timer capacitor",
            "Yageo RC0402FR-07169KL<br/>169-kOhm 1% eFuse OVLO top resistor",
            "Yageo RC0402FR-0747KL<br/>47-kOhm 1% eFuse OVLO bottom resistor",
            "Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse input capacitor",
            "Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse output capacitor",
            "Yageo RC0603FR-071KL<br/>1-kOhm 1% protected-output discharge resistor",
            "Texas Instruments TPS22919DCKR<br/>three-radio nRF quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>CC1101 quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>microSD quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>ES8311 quiet-state load switch",
            "Texas Instruments TPS22919DCKR<br/>Si4732 quiet-state load switch",
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
                "two individually replaceable exact",
                "XTAR 18650 4000mAh",
                "28.8 Wh",
                "both are required",
                "admits the pair",
                "0.57…0.88 A",
                "no more than `50 ms`",
                "one non-retriggerable hardware channel",
                "at least `350 ms`",
                "not a full-load qualification claim",
            ),
            "README.ru.md": (
                "контролируемая батарея 2S",
                "две отдельно заменяемые exact",
                "XTAR 18650 4000mAh",
                "28,8 Вт·ч",
                "нужны обе",
                "допускает пару",
                "0,57…0,88 А",
                "не дольше `50 мс`",
                "один non-retriggerable аппаратный канал",
                "на `350 мс`",
                "не обещание полной проверки под нагрузкой",
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
        self.assertIn("USB Full-Speed", contract["usb2_data"])
        self.assertIn("22-Ohm series resistors", contract["usb2_data"])
        self.assertIn("GPIO47", contract["host_control"])
        self.assertEqual("DEC-0078", contract["diagnostic_decision"])
        self.assertIn("non-retriggerable", contract["diagnostic_load_profile"])
        self.assertIn("28.7-40.7 ms", contract["diagnostic_load_profile"])
        self.assertIn("25-50 ms", contract["diagnostic_load_profile"])
        self.assertIn("PA25/A2", contract["admission_adc_profile"])
        self.assertIn("PA26/A1", contract["admission_adc_profile"])
        self.assertIn("forbids injection current", contract["admission_adc_profile"])
        self.assertEqual("DEC-0079", contract["battery_cell_decision"])
        self.assertIn("XTAR 18650 4000mAh", contract["battery_cell_profile"])
        self.assertIn("28.8Wh", contract["battery_cell_profile"])
        self.assertIn("2A", contract["charge_limit"])
        self.assertEqual("DEC-0080", contract["source_sequence_decision"])
        self.assertEqual("DEC-0081", contract["internal_rail_protection_decision"])
        self.assertIn("TPS25961DRVR", contract["internal_rail_protection_profile"])
        self.assertIn("TPS25974LRPWR", contract["internal_rail_protection_profile"])
        self.assertEqual("DEC-0082", contract["paper_closure_decision"])
        self.assertIn("paper electrical scope reviewed", contract["paper_closure_status"])
        self.assertTrue(all("HIL" in item or "procurement" in item for item in contract["remaining_i3"]))
        self.assertEqual(0.85, contract["source_power_reserve"]["paper_efficiency_factor"])
        self.assertEqual(25.5, contract["source_power_reserve"]["best_case_pdo_sys_w"]["15V_2A"])

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
            "pack_holder": "keystone_1048p",
            "pack_cell0": "xtar_18650_4000mah_protected",
            "pack_cell1": "xtar_18650_4000mah_protected",
            "safe_por_pullup": "yageo_rc0402fr_0710kl",
            "pack_hold": "diodes_2n7002dw_7_f",
            "pack_supply_or": "onsemi_bav70lt1g",
            "pack_system_diode": "diodes_bat54_7_f",
            "pack_diag_timer": "ti_tpul2g223_bqbr",
            "pack_diag_lockout_res": "yageo_rc0402fr_07620kl",
            "pack_diag_lockout_cap": "tdk_c1608x7r1c105k080ac",
            "pack_diag_switch": "diodes_dmn2056u_7",
            "pack_diag_res0": "bourns_crm2512_fx_20r0elf",
            "pack_diag_res1": "bourns_crm2512_fx_20r0elf",
            "pack_mid_adc_filter": "murata_grm155r71h103ka88d",
            "pack_stack_adc_filter": "murata_grm155r71h103ka88d",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        holder = self.database["devices"]["keystone_1048p"]
        self.assertEqual([86.0, 39.8, 14.86], holder["dimensions_mm"])
        self.assertEqual(
            {"SLOT0_POS", "SLOT0_NEG", "SLOT1_POS", "SLOT1_NEG"},
            set(holder["contacts"]),
        )

        tps = self.database["devices"]["ti_tps25751d_refr"]
        self.assertEqual("23/24/25", tps["contacts"]["VBUS_IN"]["physical"])
        self.assertEqual("20/21/22", tps["contacts"]["PPHV"]["physical"])
        self.assertEqual("8 (fixed I2C target data)", tps["contacts"]["I2Ct_SDA"]["physical"])
        charger = self.database["devices"]["ti_bq25798_rqmr"]
        self.assertEqual("2/3", charger["contacts"]["VBUS"]["physical"])
        self.assertEqual("22/23", charger["contacts"]["BAT"]["physical"])
        timer = self.database["devices"]["ti_tpul2g223_bqbr"]
        self.assertEqual("5", timer["contacts"]["CH2_Q"]["physical"])
        self.assertEqual("16", timer["contacts"]["VCC"]["physical"])
        cell = self.database["devices"]["xtar_18650_4000mah_protected"]
        self.assertEqual("button-top positive end", cell["contacts"]["POS"]["physical"])
        self.assertEqual([69.7, 18.7, 18.7], cell["dimensions_mm"])
        self.assertIn("does not publish a separate ordering code", cell["ordering_identity_note"])

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
        self.assertIn(
            ("pack_diag_timer.CH1_Q", "pack_diag_switch.G", "PACK_DIAG_GATE"),
            routes,
        )
        self.assertIn(
            ("pack_diag_timer.CH2_Q_N", "pack_diag_timer.CH1_CLR_N", "PACK_DIAG_REFRACTORY_CLEAR_N"),
            routes,
        )
        self.assertIn(
            ("pack_diag_timer.CH1_Q", "pack_diag_timer.CH2_T_N", "PACK_DIAG_PULSE_ACTIVE"),
            routes,
        )
        self.assertIn(
            ("pack_cell0.POS", "pack_holder.SLOT0_POS", "PACK_SLOT0_POSITIVE_RAW"),
            routes,
        )
        self.assertIn(
            ("pack_cell1.NEG", "pack_holder.SLOT1_NEG", "PACK_2S_MIDPOINT"),
            routes,
        )
        self.assertIn(
            ("aon_buck.PG", "safe_supervisor.MR_N", "AON_PG_N"),
            routes,
        )
        self.assertIn(
            ("safe_supervisor.RESET_N", "main_buck.EN", "POR_N"),
            routes,
        )
        self.assertIn(
            ("safe_por_pullup.END_2", "safe_supervisor.RESET_N", "POR_N"),
            routes,
        )
        self.assertNotIn(
            ("abstract:main-rail-enable-after-source-admission", "main_buck.EN", "MAIN_3V3_EN"),
            routes,
        )
        self.assertIn(
            ("abstract:qualified-2s-positive", "pack_diag_res0.END_1", "PACK_DIAG_LOAD_POSITIVE"),
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
        self.assertEqual("PACK_CELL0_ADC", admission["PA25_A2"]["net"])
        self.assertEqual("PACK_STACK_ADC", admission["PA26_A1"]["net"])
        self.assertNotIn("PA24_A3", admission)
        self.assertEqual(
            {"PA24_A3", "PA27_A0", "PA28_A5"},
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

    def test_exact_bq25798_passive_profile_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0075", contract["charger_passive_decision"])
        self.assertIn("2S at 750kHz", contract["charger_passive_profile"])
        self.assertIn("Twelve independent", contract["charger_passive_profile"])
        self.assertIn("44.2k/100k ILIM", contract["charger_passive_profile"])
        self.assertIn("direct non-ignored charger TS", contract["charger_passive_profile"])
        self.assertNotIn("exact product USB-C receptacle", contract["remaining_i3"])
        self.assertNotIn("exact product USB-C receptacle", contract["deferred_i4"])

        expected_instances = {
            "charger_inductor": "sunlord_mwsa0503s_2r2mt",
            "charger_vbus_cap0": "murata_grm31cr71e106ma12l",
            "charger_vbus_cap1": "murata_grm31cr71e106ma12l",
            "charger_vbus_hf_cap": "tdk_c1005x7r1h104k050bb",
            "charger_pmid_cap0": "murata_grm31cr71e106ma12l",
            "charger_pmid_cap1": "murata_grm31cr71e106ma12l",
            "charger_pmid_cap2": "murata_grm31cr71e106ma12l",
            "charger_pmid_hf_cap": "tdk_c1005x7r1h104k050bb",
            "charger_sys_cap0": "murata_grm31cr71e106ma12l",
            "charger_sys_cap1": "murata_grm31cr71e106ma12l",
            "charger_sys_cap2": "murata_grm31cr71e106ma12l",
            "charger_sys_cap3": "murata_grm31cr71e106ma12l",
            "charger_sys_cap4": "murata_grm31cr71e106ma12l",
            "charger_sys_hf_cap": "tdk_c1005x7r1h104k050bb",
            "charger_bat_cap0": "murata_grm31cr71e106ma12l",
            "charger_bat_cap1": "murata_grm31cr71e106ma12l",
            "charger_btst1_cap": "murata_grm155r71e473ka88d",
            "charger_btst2_cap": "murata_grm155r71e473ka88d",
            "charger_regn_cap": "tdk_cga5l1x7r1e475k160ac",
            "charger_sdrv_cap": "kemet_c0402c102k5ractu",
            "charger_prog_res": "yageo_rc0402fr_078k2l",
            "charger_batp_res": "yageo_rc0402fr_07100rl",
            "charger_ts_top": "yageo_rc0402fr_075k23l",
            "charger_ts_bottom": "yageo_rc0402fr_0730k1l",
            "charger_ts_ntc": "tdk_b57332v5103f360",
            "charger_ilim_top": "yageo_rc0402fr_0744k2l",
            "charger_ilim_bottom": "yageo_rc0402fr_07100kl",
            "pd_local_scl_pullup": "yageo_rc0402fr_072k2l",
            "pd_local_sda_pullup": "yageo_rc0402fr_072k2l",
            "charger_int_pullup": "yageo_rc0402fr_0710kl",
            "charger_ce_pullup": "yageo_rc0402fr_0710kl",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("nvdc_charger.SW1", "charger_inductor.END_1", "CHARGER_SW1"),
            ("charger_inductor.END_2", "nvdc_charger.SW2", "CHARGER_SW2"),
            ("nvdc_charger.PROG", "charger_prog_res.END_1", "CHARGER_PROG_2S_750KHZ"),
            ("pack_power_fet.S2", "charger_batp_res.END_1", "PROTECTED_PACK_POSITIVE"),
            ("nvdc_charger.TS", "charger_ts_ntc.END_1", "CHARGER_TS"),
            ("nvdc_charger.ILIM_HIZ", "charger_ilim_bottom.END_1", "CHARGER_ILIM_HIZ"),
            ("pd_controller.LDO_3V3", "pd_local_scl_pullup.END_1", "PD_LOCAL_3V3"),
            ("nvdc_charger.REGN", "charger_ce_pullup.END_1", "CHARGER_REGN"),
            ("nvdc_charger.VBUS", "nvdc_charger.VAC1", "CHARGER_VBUS_SENSE"),
            ("nvdc_charger.VBUS", "nvdc_charger.VAC2", "CHARGER_VBUS_SENSE"),
            ("nvdc_charger.D_PLUS", "abstract:no-connect", "CHARGER_DP_NC"),
            ("nvdc_charger.D_MINUS", "abstract:no-connect", "CHARGER_DM_NC"),
        ):
            self.assertIn(route, routes)

        pd_gpio1 = next(
            row
            for row in candidate["allocations"]
            if row["instance"] == "pd_controller" and row["contact"] == "GPIO1"
        )
        self.assertEqual("od", pd_gpio1["direction"])
        self.assertIn("Hi-Z reset", pd_gpio1["reset_proof"])

    def test_exact_tps25751_eeprom_support_profile_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0076", contract["pd_support_decision"])
        self.assertIn("hardware SafeMode", contract["pd_support_profile"])
        self.assertIn("both VBUS and VBUS_IN", contract["pd_support_profile"])
        self.assertNotIn(
            "TPS25751 and CAT24C512 surrounding passives and configuration straps",
            contract["remaining_i3"],
        )

        expected_instances = {
            "pd_vin_cap": "murata_grm188r60j106me47d",
            "pd_ldo3v3_cap": "murata_grm188r60j106me47d",
            "pd_ldo1v5_cap": "murata_grm188r60j106me47d",
            "pd_pphv_cap0": "murata_grm32er71e226ke15l",
            "pd_pphv_cap1": "murata_grm32er71e226ke15l",
            "pd_pphv_cap2": "murata_grm32er71e226ke15l",
            "pd_pphv_cap3": "murata_grm32er71e226ke15l",
            "pd_vbus_cap": "tdk_cga5l1x7r1e475k160ac",
            "pd_cc1_cap": "murata_grm1555c1h221ja01d",
            "pd_cc2_cap": "murata_grm1555c1h221ja01d",
            "pd_eeprom_bypass": "tdk_c1005x7r1h104k050bb",
            "pd_eeprom_wp_pullup": "yageo_rc0402fr_0710kl",
            "pd_local_scl_pullup": "yageo_rc0402fr_072k2l",
            "pd_local_sda_pullup": "yageo_rc0402fr_072k2l",
            "sys_i2c_scl_pullup": "yageo_rc0402fr_072k2l",
            "sys_i2c_sda_pullup": "yageo_rc0402fr_072k2l",
            "sys_int_pullup": "yageo_rc0402fr_0710kl",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])
        self.assertNotIn("charger_scl_pullup", candidate["instances"])
        self.assertNotIn("charger_sda_pullup", candidate["instances"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("product_usb_connector.B9_VBUS", "pd_controller.VBUS", "USB_C_VBUS_RAW"),
            ("product_usb_connector.B9_VBUS", "pd_controller.VBUS_IN", "USB_C_VBUS_RAW"),
            ("pd_controller.LDO_3V3", "pd_controller.ADCIN1", "PD_ADCIN1_SAFE_MODE_HIGH"),
            ("pd_controller.ADCIN2", "abstract:power-ground", "PD_ADCIN2_SAFE_MODE_LOW"),
            ("pd_controller.PP5V", "abstract:power-ground", "POWER_GROUND"),
            ("abstract:AON_SAFE_3V3", "pd_controller.VIN_3V3", "AON_SAFE_3V3"),
            ("pd_controller.LDO_3V3", "pd_config_eeprom.VCC", "PD_LOCAL_3V3"),
            ("pd_config_eeprom.VSS", "abstract:power-ground", "POWER_GROUND"),
            ("pd_eeprom_wp_pullup.END_2", "pd_config_eeprom.WP", "PD_EEPROM_WP"),
            ("pd_local_scl_pullup.END_2", "nvdc_charger.SCL", "PD_LOCAL_I2C_SCL"),
            ("sys_i2c_sda_pullup.END_2", "s3.GPIO1", "SYS_I2C_SDA"),
            ("sys_int_pullup.END_2", "s3.GPIO37", "SYS_INT_N"),
            ("pd_controller.DRAIN_30", "pd_controller.DRAIN_PAD", "PD_DRAIN_COPPER"),
        ):
            self.assertIn(route, routes)

        pd_gpio0 = next(
            row
            for row in candidate["allocations"]
            if row["instance"] == "pd_controller" and row["contact"] == "GPIO0"
        )
        self.assertEqual("od", pd_gpio0["direction"])
        self.assertIn("authorized", pd_gpio0["reset_proof"])
        self.assertTrue(
            self.database["devices"]["onsemi_cat24c512wi_gt3"][
                "externally_programmed_memory"
            ]
        )
        eeprom_service = next(
            item for item in candidate["services"] if item["instance"] == "pd_config_eeprom"
        )
        self.assertIn("ReadyForPatch", eeprom_service["method"])
        self.assertIn("never drives LDO_3V3 externally", eeprom_service["method"])

    def test_exact_protected_product_usb_port_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0083", contract["product_usb_decision"])
        self.assertIn("TPD4S201RUKR", contract["product_usb_profile"])
        self.assertIn("369-471 pF", contract["product_usb_profile"])
        self.assertIn("without consuming a GPIO", contract["product_usb_profile"])
        self.assertIn("22-Ohm series resistors", contract["product_usb_profile"])
        self.assertIn("reserved DNP", contract["product_usb_profile"])

        expected_instances = {
            "product_usb_connector": "jae_dx07s016ja1r1500",
            "product_usb_protector": "ti_tpd4s201_rukr",
            "product_usb_dp_series": "panasonic_erj_2rkf22r0x",
            "product_usb_dm_series": "panasonic_erj_2rkf22r0x",
            "product_usb_vbias_cap": "tdk_c1608x7s2a104k080ab",
            "product_usb_vpwr_cap": "tdk_c1608x7r1c105k080ac",
            "product_usb_fault_pullup": "yageo_rc0402fr_0710kl",
            "pd_cc1_cap": "murata_grm1555c1h221ja01d",
            "pd_cc2_cap": "murata_grm1555c1h221ja01d",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for route in (
            ("product_usb_connector.A5_CC1", "product_usb_protector.C_CC1", "USB_C_CC1_CONNECTOR"),
            ("product_usb_connector.B5_CC2", "product_usb_protector.C_CC2", "USB_C_CC2_CONNECTOR"),
            ("product_usb_protector.CC1", "pd_controller.CC1", "USB_C_CC1_PROTECTED"),
            ("product_usb_protector.CC2", "pd_controller.CC2", "USB_C_CC2_PROTECTED"),
            ("product_usb_protector.SBU1", "product_usb_dp_series.END_1", "USB2_DP_PROTECTED"),
            ("product_usb_dp_series.END_2", "s3.GPIO20", "S3_USB_DP"),
            ("product_usb_protector.SBU2", "product_usb_dm_series.END_1", "USB2_DM_PROTECTED"),
            ("product_usb_dm_series.END_2", "s3.GPIO19", "S3_USB_DM"),
            ("product_usb_protector.RPD_G1", "product_usb_protector.C_CC1", "USB_C_CC1_CONNECTOR"),
            ("product_usb_protector.RPD_G2", "product_usb_protector.C_CC2", "USB_C_CC2_CONNECTOR"),
            ("product_usb_protector.VBIAS", "product_usb_vbias_cap.END_1", "USB_PROTECTOR_VBIAS"),
            ("pd_controller.LDO_3V3", "product_usb_protector.VPWR", "PD_LOCAL_3V3"),
            ("product_usb_protector.FLT", "abstract:TP_USB_PROTECTOR_FAULT_N", "USB_PROTECTOR_FAULT_N"),
            ("product_usb_connector.A8_SBU1", "abstract:no-connect", "NO_CONNECT"),
            ("product_usb_connector.B8_SBU2", "abstract:no-connect", "NO_CONNECT"),
        ):
            self.assertIn(route, routes)

        self.assertFalse(
            any(
                route["from"].startswith("abstract:product-usb-c")
                or route["to"].startswith("abstract:product-usb-c")
                for route in candidate["fixed_routes"]
            )
        )
        self.assertIn(
            "USB Full-Speed RC tuning, signal-integrity, ESD and short-to-VBUS HIL",
            contract["deferred_i4"],
        )

    def test_exact_fixed_downstream_rail_tree_does_not_regress(self):
        candidate = next(c for c in self.candidates if c["id"] == "G2F-3I")
        contract = candidate["power_contract"]
        self.assertEqual("DEC-0068", contract["rail_decision"])
        self.assertIn("independent fixed", contract["rail_tree"])
        self.assertIn("TPS629203DRLR", contract["aon_rail"])
        self.assertIn("three independent TPS564252DRLR", contract["application_rails"])
        self.assertEqual("DEC-0072", contract["converter_passive_decision"])
        self.assertIn("45.3k/10k", contract["converter_passive_profile"])
        self.assertIn("68k/12k", contract["converter_passive_profile"])
        self.assertIn("220k/30k", contract["converter_passive_profile"])
        self.assertEqual("DEC-0073", contract["converter_control_passive_decision"])
        self.assertIn("Ten physical resistor positions", contract["converter_control_passive_profile"])
        self.assertIn("directly to admitted SYS", contract["converter_control_passive_profile"])
        self.assertEqual("DEC-0069", contract["external_protection_decision"])
        self.assertIn("TPS259470LRPWR", contract["external_protection"])
        self.assertIn("latch-off", contract["external_protection"])
        self.assertNotIn("TPS259470ARPWR", contract["external_protection"])

        expected_instances = {
            "aon_buck": "ti_tps629203_drlr",
            "aon_inductor": "sunlord_wpn201612h2r2mt",
            "aon_mode_res": "yageo_rc0402fr_0742k2l",
            "aon_input_cap": "tdk_cga5l1x7r1e475k160ac",
            "aon_output_cap": "murata_grm31cr71a226ke15l",
            "aon_efuse": "ti_tps25961_drvr",
            "aon_efuse_rilim": "yageo_rc0402fr_07240kl",
            "aon_efuse_ovlo_top": "yageo_rc0402fr_07196kl",
            "aon_efuse_ovlo_bottom": "yageo_rc0402fr_07100kl",
            "aon_efuse_input_cap": "tdk_c1005x7r1h104k050bb",
            "aon_efuse_output_cap": "murata_grm188r60j106me47d",
            "aon_pg_pullup": "yageo_rc0402fr_0747kl",
            "main_buck": "ti_tps564252_drlr",
            "main_inductor": "sunlord_mwsa0503s_3r3mt",
            "main_input_cap": "murata_grm32er71e226ke15l",
            "main_hf_input_cap": "tdk_c1005x7r1h104k050bb",
            "main_fb_top": "yageo_rc0402fr_0745k3l",
            "main_fb_bottom": "yageo_rc0402fr_0710kl",
            "main_ff_cap": "kemet_c0402c330j5gactu",
            "main_output_cap0": "murata_grm32er71e226ke15l",
            "main_output_cap1": "murata_grm32er71e226ke15l",
            "main_efuse": "ti_tps25974l_rpwr",
            "main_efuse_rilm": "yageo_rc0402fr_071k65l",
            "main_efuse_dvdt_cap": "murata_grm155r71h472ka01d",
            "main_efuse_itimer_cap": "murata_grm1555c1h121ja01d",
            "main_efuse_ovlo_top": "yageo_rt0402brd07191kl",
            "main_efuse_ovlo_bottom": "yageo_rt0402brd07100kl",
            "main_efuse_pg_top": "yageo_rc0402fr_0745k3l",
            "main_efuse_pg_bottom": "yageo_rc0402fr_0730kl",
            "main_efuse_output_cap": "murata_grm188r60j106me47d",
            "main_en_pulldown": "yageo_rc0402fr_07100kl",
            "power_fault_pullup": "yageo_rc0402fr_0710kl",
            "voice_buck": "ti_tps564252_drlr",
            "voice_inductor": "sunlord_mwsa0503s_3r3mt",
            "voice_input_cap": "murata_grm32er71e226ke15l",
            "voice_hf_input_cap": "tdk_c1005x7r1h104k050bb",
            "voice_fb_top": "yageo_rc0402fr_0768kl",
            "voice_fb_bottom": "yageo_rc0402fr_0712kl",
            "voice_ff_cap": "kemet_c0402c330j5gactu",
            "voice_output_cap0": "murata_grm32er71e226ke15l",
            "voice_output_cap1": "murata_grm32er71e226ke15l",
            "voice_efuse": "ti_tps25974l_rpwr",
            "voice_efuse_rilm": "yageo_rc0402fr_073k32l",
            "voice_efuse_dvdt_cap": "murata_grm155r71h472ka01d",
            "voice_efuse_itimer_cap": "murata_grm1555c1h121ja01d",
            "voice_efuse_ovlo_top": "yageo_rc0402fr_07270kl",
            "voice_efuse_ovlo_bottom": "yageo_rc0402fr_07100kl",
            "voice_efuse_pg_top": "yageo_rc0402fr_0768kl",
            "voice_efuse_pg_bottom": "yageo_rc0402fr_0733kl",
            "voice_efuse_output_cap": "murata_grm188r60j106me47d",
            "voice_en_pulldown": "yageo_rc0402fr_0710kl",
            "voice_pg_pullup": "yageo_rc0402fr_0710kl",
            "voice_pg_base_res": "yageo_rc0402fr_0768kl",
            "voice_pg_qualifier": "diodes_mmbt3904_7_f",
            "ext_buck": "ti_tps564252_drlr",
            "ext_inductor": "sunlord_mwsa0503s_4r7mt",
            "ext_buck_input_cap": "murata_grm32er71e226ke15l",
            "ext_buck_hf_input_cap": "tdk_c1005x7r1h104k050bb",
            "ext_buck_fb_top": "yageo_rc0402fr_07220kl",
            "ext_buck_fb_bottom": "yageo_rc0402fr_0730kl",
            "ext_buck_ff_cap": "kemet_c0402c330j5gactu",
            "ext_buck_output_cap0": "murata_grm32er71e226ke15l",
            "ext_buck_output_cap1": "murata_grm32er71e226ke15l",
            "ext_en_pulldown": "yageo_rc0402fr_0710kl",
            "ext_pg_pullup": "yageo_rc0402fr_0710kl",
            "ext_pg_base_res": "yageo_rc0402fr_0768kl",
            "ext_pg_qualifier": "diodes_mmbt3904_7_f",
            "ext_efuse": "ti_tps259470l_rpwr",
            "ext_rilm": "yageo_rc0402fr_072k21l",
            "ext_dvdt_cap": "murata_grm155r71h472ka01d",
            "ext_itimer_cap": "murata_grm188r71e224ka88d",
            "ext_ovlo_top": "yageo_rc0402fr_07169kl",
            "ext_ovlo_bottom": "yageo_rc0402fr_0747kl",
            "ext_input_cap": "murata_grm21br71e225ke11l",
            "ext_output_cap": "murata_grm21br71e225ke11l",
            "ext_bleeder": "yageo_rc0603fr_071kl",
            "nrf_power_switch": "ti_tps22919_dckr",
            "cc_power_switch": "ti_tps22919_dckr",
            "sd_power_switch": "ti_tps22919_dckr",
            "codec_power_switch": "ti_tps22919_dckr",
            "receiver_power_switch": "ti_tps22919_dckr",
        }
        for instance, device_id in expected_instances.items():
            self.assertEqual(device_id, candidate["instances"][instance])

        buck = self.database["devices"]["ti_tps564252_drlr"]
        self.assertEqual("4", buck["contacts"]["PG"]["physical"])
        self.assertNotIn("BST", buck["contacts"])

        routes = {
            (route["from"], route["to"], route["net"])
            for route in candidate["fixed_routes"]
        }
        for destination in ("aon_buck.VIN", "main_buck.VIN", "voice_buck.VIN", "ext_buck.VIN"):
            self.assertIn(("nvdc_charger.SYS", destination, "NVDC_SYS"), routes)
        self.assertIn(("voice_efuse.OUT", "voice.VCC", "VVOICE_4V"), routes)
        self.assertIn(("aon_efuse.OUT", "abstract:AON_SAFE_3V3", "AON_SAFE_3V3"), routes)
        self.assertIn(("main_efuse.OUT", "abstract:3V3_MAIN", "3V3_MAIN"), routes)
        self.assertIn(("ext_efuse.OUT", "u214.5V_IN", "5V_EXT_PROTECTED"), routes)
        self.assertIn(("ext_efuse.ILM", "ext_rilm.END_1", "EXT_EFUSE_ILM_SET"), routes)
        self.assertIn(("ext_efuse.DVDT", "ext_dvdt_cap.END_1", "EXT_EFUSE_DVDT"), routes)
        self.assertIn(("ext_efuse.ITIMER", "ext_itimer_cap.END_1", "EXT_EFUSE_ITIMER"), routes)
        self.assertIn(("ext_efuse.OUT", "ext_bleeder.END_1", "5V_EXT_PROTECTED"), routes)
        self.assertIn(("aon_buck.MODE_SCONF", "aon_mode_res.END_1", "AON_MODE_SET"), routes)
        self.assertIn(("nvdc_charger.SYS", "aon_buck.EN", "AON_BUCK_EN"), routes)
        self.assertIn(("aon_pg_pullup.END_2", "aon_buck.PG", "AON_PG_N"), routes)
        self.assertIn(("main_fb_top.END_2", "main_buck.FB", "MAIN_3V3_FB"), routes)
        self.assertIn(("voice_fb_top.END_2", "voice_buck.FB", "VOICE_4V_FB"), routes)
        self.assertIn(("ext_buck_fb_top.END_2", "ext_buck.FB", "EXT_5V_FB"), routes)
        for output_cap in (
            "main_output_cap0",
            "main_output_cap1",
            "voice_output_cap0",
            "voice_output_cap1",
            "ext_buck_output_cap0",
            "ext_buck_output_cap1",
        ):
            self.assertTrue(any(output_cap in endpoint for route in routes for endpoint in route[:2]))
        self.assertIn("immediately at startup", contract["external_protection"])
        self.assertIn("post-start 2A transient", contract["external_protection"])
        self.assertNotIn(
            "ext-5v-passive-discharge",
            {
                endpoint
                for route in candidate["fixed_routes"]
                for endpoint in (route["from"], route["to"])
            },
        )
        self.assertIn(("nrf_power_switch.VOUT", "nrf2.VCC", "3V3_NRF_GROUP"), routes)

        self.assertEqual("DEC-0070", contract["switched_pg_qualification_decision"])
        self.assertIn("EN high plus PG low", contract["switched_pg_qualification"])
        self.assertIn(
            ("voice_efuse.PG", "voice_pg_qualifier.E", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertIn(
            ("voice_pg_base_res.END_2", "voice_pg_qualifier.B", "VOICE_PG_QUAL_BASE"),
            routes,
        )
        self.assertIn(
            ("voice_pg_pullup.END_2", "voice_efuse.PG", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertIn(
            ("voice_pg_qualifier.C", "abstract:power-current-thermal-fault", "VOICE_4V_FAULT_QUAL_N"),
            routes,
        )
        self.assertIn(
            ("ext_buck.PG", "ext_pg_qualifier.E", "EXT_5V_PG_N"),
            routes,
        )
        self.assertIn(
            ("ext_pg_base_res.END_2", "ext_pg_qualifier.B", "EXT_PG_QUAL_BASE"),
            routes,
        )
        self.assertIn(
            ("ext_pg_pullup.END_2", "ext_buck.PG", "EXT_5V_PG_N"),
            routes,
        )
        self.assertIn(
            ("ext_pg_qualifier.C", "abstract:power-current-thermal-fault", "EXT_5V_FAULT_QUAL_N"),
            routes,
        )
        self.assertNotIn(
            ("voice_buck.PG", "abstract:power-current-thermal-fault", "VOICE_4V_PG_N"),
            routes,
        )
        self.assertNotIn(
            ("ext_buck.PG", "abstract:power-current-thermal-fault", "EXT_5V_PG_N"),
            routes,
        )

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
            ("slow_io.P10", "codec_power_switch.ON", "CODEC_PWR_EN"),
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
