import json
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
REPORT_SCRIPT = ROOT / "hardware/architecture/h0_r2_report.py"
INTERCONNECT_SCRIPT = ROOT / "hardware/architecture/h0_r2_interconnect.py"


class H0R2ArchitectureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_review_identity_and_next_marker(self):
        self.assertEqual("H0-R2", self.data["id"])
        self.assertEqual("reviewed_functional_architecture_i8080_and_r2_interboard_reconciled", self.data["status"])
        self.assertEqual("H1-R2.0", self.data["next_marker"])

    def test_s3_uses_every_real_n16r8_gpio_once(self):
        allowed = self.data["s3"]["available_gpio"]
        assigned = [row["gpio"] for row in self.data["s3"]["pin_map"]]
        self.assertEqual(33, len(allowed))
        self.assertEqual(sorted(allowed), sorted(assigned))
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertTrue({35, 36, 37}.isdisjoint(assigned))

    def test_direct_ui_and_encoder_never_cross_ipc(self):
        ui = self.data["s3"]["ui_contract"]
        self.assertIn("TCA9539PWR", ui["ordinary_buttons"])
        self.assertIn("directly to S3", ui["ordinary_buttons"])
        self.assertIn("PCNT", ui["encoder"])
        self.assertIn("RF RP", ui["ptt_exception"])

    def test_display_is_direct_i8080_and_clock_is_legal(self):
        display = self.data["display_contract"]
        self.assertEqual(24_000_000, display["selected_clock_hz"])
        self.assertLessEqual(display["selected_clock_hz"], display["controller_limit_hz"])
        self.assertEqual(24.0, display["payload_mb_s"])
        calculated = display["full_frame_bytes"] / (display["payload_mb_s"] * 1_000_000) * 1000
        self.assertAlmostEqual(display["full_frame_wire_ms"], calculated, places=6)
        self.assertIn("i8080", display["interface"])
        self.assertIn("4-wire serial", display["fallback"])
        self.assertIn("not QSPI", display["fallback"])
        lcd = [row["net"] for row in self.data["s3"]["pin_map"] if row["net"].startswith("LCD_DB")]
        self.assertEqual([f"LCD_DB{i}" for i in range(8)], sorted(lcd, key=lambda x: int(x[6:])))

    def test_onboard_video_path_is_explicitly_absent(self):
        accepted = self.data["accepted_scope"]
        self.assertIn("No onboard analog or digital video receiver", accepted["video_boundary"])
        self.assertNotIn("video_contract", self.data)
        reserve = [row for row in self.data["s3"]["pin_map"] if row["direction"] == "reserve"]
        self.assertEqual(6, len(reserve))

    def test_hub_has_real_reserve_and_no_duplicate_gpio(self):
        hub = self.data["hub_rp"]
        groups = hub["pin_groups"]
        gpios = [gpio for group in groups for gpio in group["gpios"]]
        reserve = next(group for group in groups if group["role"] == "uncommitted electrical reserve")
        committed = [gpio for group in groups if group is not reserve for gpio in group["gpios"]]
        self.assertEqual(hub["gpio_budget"]["used"], len(committed))
        self.assertEqual(len(gpios), len(set(gpios)))
        self.assertEqual(48, hub["gpio_budget"]["available"])
        self.assertEqual(hub["gpio_budget"]["free"], len(reserve["gpios"]))
        self.assertEqual(1, hub["gpio_budget"]["free"])
        self.assertEqual(list(range(48)), sorted(gpios))

    def test_interboard_map_closes_current_and_mechanics(self):
        m1 = self.data["interboard_rebaseline"]
        rows = m1["pin_map"]
        self.assertEqual(list(range(1, 81)), [row["contact"] for row in rows])
        classes = [row["class"] for row in rows]
        self.assertEqual(14, classes.count("main_power"))
        self.assertEqual(10, classes.count("reserve"))
        self.assertEqual(14, classes.count("main_return"))
        self.assertLess(m1["main_current"]["step_per_contact_a"], m1["main_current"]["contact_rating_a"])
        self.assertIn("compression stops", m1["mechanical_load_path"])
        self.assertIn("electrical/alignment only", m1["mechanical_load_path"])

    def test_interboard_carries_only_intentional_crossings_not_local_payloads(self):
        m1 = self.data["interboard_rebaseline"]
        nets = [row["net"] for row in m1["pin_map"]]
        contract = m1["locality_contract"]
        for prefix in contract["forbidden_payload_prefixes"]:
            self.assertFalse(
                any(net.startswith(prefix) for net in nets),
                f"board-local payload unexpectedly crosses M1: {prefix}",
            )
        self.assertEqual("NC_35", nets[34])
        self.assertEqual("S3_RESET_KILL_GATE", nets[35])
        self.assertEqual(
            {"HUB_RF_ALERT_N", "HUB_RF_CS_N", "HUB_RF_SCK", "HUB_RF_MOSI", "HUB_RF_MISO"},
            {row["net"] for row in m1["pin_map"] if row["class"] == "ipc"},
        )
        self.assertEqual(
            {"S3_USB_DM", "S3_USB_DP"},
            {row["net"] for row in m1["pin_map"] if row["class"] == "usb2"},
        )
        self.assertEqual(
            {"ENCODER_A", "ENCODER_B", "UI_ENCODER_PUSH_N"},
            {row["net"] for row in m1["pin_map"] if row["class"] == "ui"},
        )

    def test_airband_is_mandatory_receive_only_and_reuses_the_receiver_port(self):
        accepted = self.data["accepted_scope"]["airband_acceptance"]
        air = self.data["airband_contract"]
        self.assertIn("Mandatory receive-only", accepted)
        self.assertEqual([118.0, 137.0], air["user_range_mhz"])
        self.assertEqual([6.0, 25.0], air["frequency_plan"]["if_range_mhz"])
        self.assertEqual([87.0, 106.0], air["frequency_plan"]["image_range_mhz"])
        self.assertIn("existing outward", air["antenna_port"])
        self.assertIn("no eleventh", air["antenna_port"])
        self.assertIn("transmit", " ".join(air["performance_boundary"]["excluded"]).lower())

    def test_airband_controls_are_fail_low_and_consume_only_two_rear_pins(self):
        air = self.data["airband_contract"]
        self.assertIn("pulled low", air["control"]["gp35"])
        self.assertIn("defaults", air["control"]["gp36"])
        groups = self.data["rf_rp"]["pin_groups"]
        roles = {tuple(group["gpios"]): group["role"] for group in groups}
        self.assertIn("AIR_RX_EN", roles[(35,)])
        self.assertIn("AIR_RX_MODE", roles[(36,)])

    def test_rear_gpio_budget_exposes_removed_video_controls_as_reserve(self):
        rear = self.data["rf_rp"]
        groups = rear["pin_groups"]
        gpios = [gpio for group in groups for gpio in group["gpios"]]
        reserve = next(group for group in groups if group["role"] == "uncommitted electrical reserve")
        committed = [gpio for group in groups if group is not reserve for gpio in group["gpios"]]
        self.assertEqual(43, rear["gpio_budget"]["used"])
        self.assertEqual(5, rear["gpio_budget"]["free"])
        self.assertEqual(rear["gpio_budget"]["used"], len(committed))
        self.assertEqual(list(range(48)), sorted(gpios))
        self.assertEqual(len(gpios), len(set(gpios)))
        self.assertEqual({32, 33, 34, 37, 38}, set(reserve["gpios"]))

    def test_airband_factory_bom_is_exact_and_costed(self):
        bom = self.data["airband_factory_bom_delta"]
        incremental = sum(row["qty"] * row["unit_price"] for row in bom["lines"])
        self.assertAlmostEqual(bom["active_incremental_unit_cost"], incremental, places=4)
        exact = {row["mpn"] for row in bom["lines"]}
        self.assertEqual(
            {"LT5560EDD#TRPBF", "PGA-103+", "SI5351A-B-GTR", "HMC544AETR", "SI4732-A10-GSR"},
            exact,
        )
        self.assertIn("0 exact matches", bom["filter_route"]["jlcpcb_search_result"])
        self.assertIn("serial high-Q LC passives", bom["filter_route"]["production_implementation"])

    def test_r2_power_contract_invalidates_the_old_2p5a_envelope(self):
        power = self.data["power_rebaseline"]
        self.assertIn("historical only", power["r1_status"])
        self.assertGreaterEqual(power["h1_required_envelope"]["continuous_3v3_main_a_min"], 3.5)
        self.assertGreaterEqual(power["h1_required_envelope"]["step_a_min"], 4.0)
        self.assertGreaterEqual(power["airband_increment"]["reserved_current_ma"], 150)

    def test_every_transport_has_positive_margin_contract(self):
        for transport in self.data["transport_contracts"]:
            self.assertGreater(transport["raw_payload_mb_s"], transport["qualified_payload_floor_mb_s"])
            self.assertGreater(transport["qualified_payload_floor_mb_s"], 0)

    def test_no_accepted_capability_is_dropped(self):
        self.assertEqual([], self.data["exit_review"]["capability_loss"])
        ids = {item["id"] for item in self.data["retained_capabilities"]}
        required = {
            "UI", "DISPLAY", "NATIVE-S3", "NATIVE-C5", "IR",
            "NRF24-X3", "SUB-GHZ", "VOICE", "CAP-SLOT", "BROADCAST-RX",
            "AUDIO", "STORAGE", "M5-UNIT", "SAFETY", "SERVICE",
        }
        self.assertEqual(required, ids)

    def test_public_report_outputs_are_generated_from_the_contract(self):
        spec = importlib.util.spec_from_file_location("h0_r2_report", REPORT_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual(module.render_svg(self.data), module.SVG.read_text(encoding="utf-8"))
        self.assertEqual(module.render_report(self.data, False), module.REPORT_EN.read_text(encoding="utf-8"))
        self.assertEqual(module.render_report(self.data, True), module.REPORT_RU.read_text(encoding="utf-8"))
        self.assertIn("AIR_RX_EN", module.REPORT_EN.read_text(encoding="utf-8"))
        self.assertIn("Зеркальный диапазон", module.REPORT_RU.read_text(encoding="utf-8"))

    def test_interconnect_page_is_generated_from_the_exact_80_contact_map(self):
        spec = importlib.util.spec_from_file_location("h0_r2_interconnect", INTERCONNECT_SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual(module.render(self.data, False), module.EN.read_text(encoding="utf-8"))
        self.assertEqual(module.render(self.data, True), module.RU.read_text(encoding="utf-8"))
        self.assertIn("0.3036 A/contact", module.EN.read_text(encoding="utf-8"))
        self.assertIn("`10` NC reserve", module.EN.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
