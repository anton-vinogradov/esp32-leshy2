import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/architecture/h1_r2_dual_rp_pinout.py"
SOURCE = ROOT / "hardware/architecture/h1-r2-dual-rp-pinout.json"
H0 = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
SPEC = importlib.util.spec_from_file_location("h1_r2_dual_rp_pinout", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H1R2DualRPPinoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.h0 = json.loads(H0.read_text(encoding="utf-8"))

    def test_exact_maps_close_all_96_gpio_without_changing_h0_budgets(self):
        audit = MODULE.build(self.source, self.h0)
        self.assertEqual([], audit["errors"])
        self.assertEqual("H1-R2.31", audit["marker"])
        self.assertEqual(96, audit["summary"]["gpio_rows"])
        self.assertEqual((46, 2, 43, 5), (
            audit["summary"]["hub_gpio_used"], audit["summary"]["hub_gpio_reserve"],
            audit["summary"]["rf_gpio_used"], audit["summary"]["rf_gpio_reserve"],
        ))
        for domain in ("hub_rp", "rf_rp"):
            self.assertEqual(list(range(48)), [row["gpio"] for row in self.source[domain]["pin_map"]])
            self.assertTrue(all(row["reset"] for row in self.source[domain]["pin_map"]))

    def test_h0_functional_groups_partition_each_rp_gpio_bank(self):
        for domain in ("hub_rp", "rf_rp"):
            gpios = [
                gpio
                for group in self.h0[domain]["pin_groups"]
                for gpio in group["gpios"]
            ]
            self.assertEqual(48, len(gpios), domain)
            self.assertEqual(set(range(48)), set(gpios), domain)

        broken_h0 = copy.deepcopy(self.h0)
        broken_h0["rf_rp"]["pin_groups"][5]["gpios"].append(29)
        errors = MODULE.validate(
            self.source, broken_h0, MODULE.load(MODULE.C5_MUX), MODULE.load(MODULE.U219)
        )
        self.assertIn(
            "rf_rp: reviewed H0 functional groups must partition GPIO0..47 exactly once",
            errors,
        )

    def test_m1_binding_is_exact_and_directionally_symmetric(self):
        self.assertEqual(
            [
                ("HUB_RF_ALERT_N", 22, 17, 19),
                ("HUB_RF_CS_N", 23, 16, 25),
                ("HUB_RF_SCK", 24, 13, 26),
                ("HUB_RF_MOSI", 26, 14, 24),
                ("HUB_RF_MISO", 27, 15, 27),
            ],
            [(row["net"], row["contact"], row["hub_gpio"], row["rf_gpio"])
             for row in self.source["m1_binding"]],
        )

    def test_resource_budgets_close_with_real_reserve(self):
        hub, rf = self.source["hub_rp"], self.source["rf_rp"]
        self.assertEqual((8, 4, 14, 2), (
            hub["pio_budget"]["used_state_machines"], hub["pio_budget"]["reserve_state_machines"],
            hub["dma_budget"]["used_channels"], hub["dma_budget"]["reserve_channels"],
        ))
        self.assertEqual((7, 5, 12, 4), (
            rf["pio_budget"]["used_state_machines"], rf["pio_budget"]["reserve_state_machines"],
            rf["dma_budget"]["used_channels"], rf["dma_budget"]["reserve_channels"],
        ))

    def test_s3_rom_uart_has_dedicated_pins_without_qualification_claim(self):
        self.assertEqual([], MODULE.validate_s3_rom_uart_routing(self.source, self.h0))
        self.assertNotIn("s3_rom_uart_isolation", self.source)
        routing = self.source["s3_rom_uart_routing"]
        self.assertEqual({"tx": 43, "rx": 44}, routing["uart0_gpio"])
        self.assertEqual({"S3_HUB_D2": 7, "S3_HUB_D3": 8}, routing["hub_data_gpio"])
        self.assertTrue(all(value is False for value in routing["qualification"].values()))
        s3 = {row["gpio"]: row for row in self.h0["s3"]["pin_map"]}
        for gpio, expected in {
            7: ("S3_HUB_D2", "SPI3", "io"), 8: ("S3_HUB_D3", "SPI3", "io"),
            43: ("S3_UART_SERVICE_TX", "UART0_TX", "out"),
            44: ("S3_UART_SERVICE_RX", "UART0_RX", "in"),
        }.items():
            self.assertEqual(expected, tuple(s3[gpio][key] for key in ("net", "peripheral", "direction")))
        hub = {row["gpio"]: row for row in self.source["hub_rp"]["pin_map"]}
        self.assertEqual("S3 GPIO7 through GPIO matrix", hub[2]["endpoint"])
        self.assertEqual("S3 GPIO8 through GPIO matrix", hub[3]["endpoint"])
        candidate = MODULE.load(MODULE.G2F)
        for russian in (False, True):
            page = MODULE.render_public(self.source, candidate, russian)
            self.assertIn(routing["verification_gate"], page)
            self.assertIn(routing["service_result"], page)
            self.assertNotIn("through ROM-UART isolation", page)

    def test_s3_rom_uart_rejects_old_map_or_wrong_peripheral_direction(self):
        old = copy.deepcopy(self.h0)
        rows = {row["gpio"]: row for row in old["s3"]["pin_map"]}
        for first, second in ((7, 43), (8, 44)):
            for key in ("net", "peripheral", "direction"):
                rows[first][key], rows[second][key] = rows[second][key], rows[first][key]
        self.assertTrue(MODULE.validate_s3_rom_uart_routing(self.source, old))
        for gpio in (7, 8, 43, 44):
            for key, wrong in (("gpio", 99), ("net", "WRONG"),
                               ("peripheral", "UART1"), ("direction", "reserve")):
                with self.subTest(gpio=gpio, key=key):
                    broken = copy.deepcopy(self.h0)
                    next(row for row in broken["s3"]["pin_map"] if row["gpio"] == gpio)[key] = wrong
                    self.assertTrue(MODULE.validate_s3_rom_uart_routing(self.source, broken))

    def test_s3_rom_uart_rejects_duplicate_absent_and_aliased_h0_rows(self):
        for gpio in (7, 8, 43, 44):
            for mutation in ("duplicate", "absent", "aliased_net"):
                with self.subTest(gpio=gpio, mutation=mutation):
                    broken = copy.deepcopy(self.h0)
                    rows = broken["s3"]["pin_map"]
                    row = next(row for row in rows if row["gpio"] == gpio)
                    if mutation == "duplicate":
                        rows.append(copy.deepcopy(row))
                    elif mutation == "absent":
                        rows.remove(row)
                    else:
                        rows.append(dict(row, gpio=99))
                    self.assertTrue(MODULE.validate_s3_rom_uart_routing(self.source, broken))

    def test_s3_rom_uart_rejects_mismatched_hub_pair_or_lost_startup_guards(self):
        for gpio in (2, 3):
            for key, value in (("net", "S3_HUB_D3" if gpio == 2 else "S3_HUB_D2"),
                               ("endpoint", "S3 GPIO43 through ROM-UART isolation"),
                               ("controller", "GPIO"), ("direction", "out"),
                               ("reset", "input/high-Z")):
                with self.subTest(gpio=gpio, key=key):
                    broken = copy.deepcopy(self.source)
                    broken["hub_rp"]["pin_map"][gpio][key] = value
                    self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))
            for duplicate in (False, True):
                broken = copy.deepcopy(self.source)
                rows = broken["hub_rp"]["pin_map"]
                row = next(row for row in rows if row["gpio"] == gpio)
                rows.append(copy.deepcopy(row)) if duplicate else rows.remove(row)
                self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))

    def test_s3_rom_uart_rejects_missing_or_false_topology_metadata(self):
        routing = self.source["s3_rom_uart_routing"]
        for key in routing:
            with self.subTest(missing=key):
                broken = copy.deepcopy(self.source)
                del broken["s3_rom_uart_routing"][key]
                self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))
        for key, wrong in (("mode", "shared_gpio"), ("uart0_gpio", {"tx": 7, "rx": 8}),
                           ("hub_data_gpio", {"S3_HUB_D2": 43, "S3_HUB_D3": 44}),
                           ("uart0_shared_with_hub", True), ("requires_rom_uart_isolator", True),
                           ("uart0_shared_with_hub", 0)):
            with self.subTest(key=key, wrong=wrong):
                broken = copy.deepcopy(self.source)
                broken["s3_rom_uart_routing"][key] = wrong
                self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))
        for group, wrong in (("requirements", False), ("qualification", True)):
            for key in routing[group]:
                broken = copy.deepcopy(self.source)
                broken["s3_rom_uart_routing"][group][key] = wrong
                self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))
        broken = copy.deepcopy(self.source)
        del broken["s3_rom_uart_routing"]
        self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))
        broken = copy.deepcopy(self.source)
        broken["s3_rom_uart_isolation"] = {}
        self.assertTrue(MODULE.validate_s3_rom_uart_routing(broken, self.h0))

    def test_full_validator_applies_s3_rom_uart_cross_join(self):
        broken = copy.deepcopy(self.h0)
        next(row for row in broken["s3"]["pin_map"] if row["gpio"] == 43)["peripheral"] = "UART1_TX"
        errors = MODULE.validate(self.source, broken, MODULE.load(MODULE.C5_MUX), MODULE.load(MODULE.U219))
        self.assertTrue(any("dedicated ROM-UART/Hub H0 assignment" in error for error in errors))

    def test_rear_cap_pins_are_exact_one_u214_u219_profile(self):
        rf = {row["gpio"]: row for row in self.source["rf_rp"]["pin_map"]}
        self.assertEqual(("CAP_PIN10_BUSY_OR_NFC_CS_N", "io"), (rf[12]["net"], rf[12]["direction"]))
        self.assertIn("SN74CBTLV1G125", rf[12]["endpoint"])
        self.assertIn("U219 NFC_CS_N", rf[12]["endpoint"])
        self.assertIn("U219 POWER_EN", rf[14]["endpoint"])
        self.assertEqual(("CAP_IRQ", "in"), (rf[13]["net"], rf[13]["direction"]))
        self.assertNotIn("IRQ_N", rf[13]["endpoint"])
        self.assertEqual(("CAP_I2C_SDA", "io"), (rf[30]["net"], rf[30]["direction"]))
        self.assertIn("TCA4307DGKR", rf[30]["endpoint"])
        self.assertIn("U214/U219 contact 4 SDA", rf[30]["endpoint"])
        self.assertEqual(("CAP_I2C_SCL", "od"), (rf[31]["net"], rf[31]["direction"]))
        self.assertIn("U214/U219 contact 3 SCL", rf[31]["endpoint"])
        self.assertIn("U219 RF_SW0", rf[40]["endpoint"])
        self.assertIn("U219 CC1101 GDO0", rf[41]["endpoint"])
        self.assertIn("U219 CC1101_CS_N", rf[47]["endpoint"])

    def test_historical_gate_closure_is_not_current_c5_qualification(self):
        audit = MODULE.build(self.source, self.h0)
        self.assertFalse(audit["authority"]["r2_h2_authorized"])
        self.assertEqual("engineering_schematic_join_not_functionally_qualified",
                         audit["authority"]["c5_electrical_join_status"])
        self.assertEqual("historical_2026-08-30_not_current_C5_qualification",
                         audit["authority"]["h2_gate_history_scope"])
        current = audit["authority"]["current_c5_join"]
        self.assertEqual("TS3USB221ERSER", current["mux_mpn"])
        self.assertEqual("SN74LV20APWR", current["nand_mpn"])
        self.assertEqual(2, current["nand_package_count"])
        self.assertEqual("explicit JLCPCB Pre-order", current["nand_route"])
        self.assertTrue(all(value is False for value in current["qualification"].values()))
        resolved = " ".join(audit["authority"]["resolved_h2_gates"])
        self.assertIn("C11355", resolved)
        self.assertIn("SN74LVC1G74DCUR", resolved)
        self.assertIn("TCA9803DGKR", resolved)
        self.assertEqual([], audit["authority"]["remaining_h2_gates"])
        c5 = [row for row in self.source["hub_rp"]["pin_map"] if row["net"].startswith("C5_SDIO_")]
        self.assertEqual(6, len(c5))
        self.assertIn("C5 GPIO9 / module pad 11", c5[0]["endpoint"])
        self.assertIn("TS3USB221E 2D+", c5[4]["endpoint"])
        self.assertIn("TS3USB221E 2D-", c5[5]["endpoint"])
        hub = {row["gpio"]: row for row in self.source["hub_rp"]["pin_map"]}
        self.assertIn("TCA9803DGKR SDAA", hub[42]["endpoint"])
        self.assertIn("TCA9803DGKR SCLA", hub[43]["endpoint"])
        self.assertIn("no external B-side pull-up", hub[42]["reset"])

    def test_c5_join_rejects_retired_branch_and_false_current_acceptance(self):
        c5, u219 = MODULE.load(MODULE.C5_MUX), MODULE.load(MODULE.U219)
        for gpio in (11, 12):
            broken = copy.deepcopy(self.source)
            broken["hub_rp"]["pin_map"][gpio]["endpoint"] = broken["hub_rp"]["pin_map"][gpio]["endpoint"].replace("TS3USB221E 2D", "FSUSB42 HSD2")
            self.assertTrue(MODULE.validate(broken, self.h0, c5, u219))
        for key, wrong in (("c5_electrical_join_status", "closed and materialized"),
                           ("h2_gate_history_scope", "current_closed"),
                           ("current_c5_join", {})):
            broken = copy.deepcopy(self.source)
            broken["authority_chain"][key] = wrong
            self.assertTrue(MODULE.validate(broken, self.h0, c5, u219))
        for key in self.source["authority_chain"]["current_c5_join"]["qualification"]:
            for wrong in (True, 0):
                broken = copy.deepcopy(self.source)
                broken["authority_chain"]["current_c5_join"]["qualification"][key] = wrong
                self.assertTrue(MODULE.validate(broken, self.h0, c5, u219))

    def test_c5_join_reuses_actual_control_and_procurement_validation(self):
        c5, u219 = MODULE.load(MODULE.C5_MUX), MODULE.load(MODULE.U219)
        broken = copy.deepcopy(c5)
        broken["production_mux_route"]["candidate"]["mpn"] = "FSUSB42MUX"
        self.assertTrue(MODULE.validate(self.source, self.h0, broken, u219))
        broken = copy.deepcopy(c5)
        broken["ownership"]["control_mapping"]["equations"]["SEL"] = "!O&R"
        self.assertTrue(MODULE.validate(self.source, self.h0, broken, u219))
        broken = copy.deepcopy(c5)
        qualifier = broken["ownership"]["detector_latch_implementation"]["release_qualifier"]
        qualifier["live_inventory"]["explicit_preorder_offered"] = False
        self.assertTrue(MODULE.validate(self.source, self.h0, broken, u219))

    def test_current_render_does_not_requalify_retired_c5_or_reset_map(self):
        candidate = MODULE.load(MODULE.G2F)
        for russian in (False, True):
            page = MODULE.render_public(self.source, candidate, russian)
            self.assertIn("TS3USB221ERSER/C129313", page)
            self.assertIn("SN74LV20APWR/C2862070", page)
            self.assertIn("Pre-order", page)
            self.assertIn("2026-08-30", page)
            self.assertIn("NX3008NBKS,115", page)
            self.assertNotIn("FSUSB42 HSD2", page)
            self.assertNotIn("materialized in accepted native", page)
            self.assertNotIn("материализованы в принятой native", page)

    def test_pin_or_budget_regression_fails_closed(self):
        broken = copy.deepcopy(self.source)
        broken["hub_rp"]["pin_map"][13]["net"] = "WRONG_NET"
        broken["hub_rp"]["dma_budget"]["used_channels"] = 13
        errors = MODULE.validate(
            broken, self.h0, MODULE.load(MODULE.C5_MUX), MODULE.load(MODULE.U219)
        )
        self.assertIn("HUB_RF_SCK: endpoint net does not match both RP pin maps", errors)
        self.assertIn("hub_rp: DMA used count does not match allocations", errors)

    def test_real_rp_identity_fixed_mux_and_pio_windows_fail_closed(self):
        c5 = MODULE.load(MODULE.C5_MUX)
        u219 = MODULE.load(MODULE.U219)

        invented = copy.deepcopy(self.source)
        invented["rp_identity"]["silicon"] = "INVENTED"
        self.assertIn(
            "RP2354B identity must join the registered SC1512-A4/A4 device",
            MODULE.validate(invented, self.h0, c5, u219),
        )

        bad_i2c = copy.deepcopy(self.source)
        bad_i2c["rf_rp"]["pin_map"][30]["controller"] = "I2C0"
        self.assertTrue(any(
            "violates RP2350 fixed mux I2C1 SDA" in error
            for error in MODULE.validate(bad_i2c, self.h0, c5, u219)
        ))

        bad_pio = copy.deepcopy(self.source)
        bad_pio["hub_rp"]["pio_budget"]["gpio_windows"][0]["base"] = 0
        self.assertTrue(any(
            "outside declared PIO0 base-0 window" in error
            for error in MODULE.validate(bad_pio, self.h0, c5, u219)
        ))

    def test_direction_reset_and_audio_isolation_mutations_fail_closed(self):
        c5 = MODULE.load(MODULE.C5_MUX)
        u219 = MODULE.load(MODULE.U219)

        bad_direction = copy.deepcopy(self.source)
        bad_direction["rf_rp"]["pin_map"][26]["direction"] = "out"
        self.assertIn(
            "HUB_RF_SCK: Hub/RF direction pair is not electrically symmetric",
            MODULE.validate(bad_direction, self.h0, c5, u219),
        )

        unsafe_reset = copy.deepcopy(self.source)
        unsafe_reset["hub_rp"]["pin_map"][36]["reset"] = "unsafe-but-nonempty"
        self.assertIn(
            "hub_rp GPIO36: reset state is not fail-closed/high-Z",
            MODULE.validate(unsafe_reset, self.h0, c5, u219),
        )

        no_audio_isolation = copy.deepcopy(self.source)
        no_audio_isolation["rf_rp"]["pin_map"][0]["endpoint"] = "direct ES8311 BCLK"
        self.assertTrue(any(
            "rf_rp GPIO0: audio path lacks reset-off" in error
            for error in MODULE.validate(no_audio_isolation, self.h0, c5, u219)
        ))

    def test_generated_audit_and_public_pages_are_current(self):
        audit = MODULE.build(self.source, self.h0)
        self.assertEqual(MODULE.render_json(audit), MODULE.OUTPUT.read_text(encoding="utf-8"))
        candidate = json.loads(MODULE.G2F.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_public(self.source, candidate, False), MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_public(self.source, candidate, True), MODULE.DOC_RU.read_text(encoding="utf-8"))
        self.assertIn("TS3USB221ERSER/C129313", MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertIn("TCA9803DGKR/C2687966", MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertIn("S3 GPIO7 through GPIO matrix", MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertIn("Dedicated S3 ROM-UART routing", MODULE.DOC_EN.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
