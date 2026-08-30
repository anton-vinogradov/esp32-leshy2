import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/architecture/c5_sdio_service_mux.py"
SPEC = importlib.util.spec_from_file_location("c5_sdio_service_mux", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class C5SdioServiceMuxTest(unittest.TestCase):
    def test_exact_c5_module_pads_and_mux_polarity(self):
        result = MODULE.build()
        self.assertEqual([], result["errors"])
        self.assertEqual(
            {
                "SDIO_DAT1": ("GPIO7", 9),
                "SDIO_DAT0": ("GPIO8", 10),
                "SDIO_CLK": ("GPIO9", 11),
                "SDIO_CMD": ("GPIO10", 12),
                "SDIO_DAT3_USB_DM": ("GPIO13", 13),
                "SDIO_DAT2_USB_DP": ("GPIO14", 14),
            },
            {row["signal"]: (row["gpio"], row["module_pad"]) for row in result["c5_signal_map"]},
        )
        pins = {row["pin"]: row for row in result["mux_pin_topology"]}
        self.assertEqual(("D+", "C5_GPIO14_COMMON"), (pins[3]["name"], pins[3]["net"]))
        self.assertEqual(("HSD1+", "C5_SERVICE_USB_DP_BRANCH"), (pins[7]["name"], pins[7]["net"]))
        self.assertEqual(("HSD2+", "HUB_C5_SDIO_DAT2_BRANCH"), (pins[9]["name"], pins[9]["net"]))

    def test_conditioning_is_branch_local_and_complete(self):
        result = MODULE.build()
        conditioning = result["branch_conditioning"]
        self.assertEqual({"CLK", "CMD", "DAT0", "DAT1", "DAT2", "DAT3"},
                         {row["signal"] for row in conditioning["sdio_series"]})
        self.assertEqual({"CMD", "DAT0", "DAT1", "DAT2", "DAT3"},
                         {row["signal"] for row in conditioning["sdio_pullups"]})
        for row in conditioning["sdio_pullups"]:
            self.assertEqual(10_000, row["value_ohm"])
        for row in conditioning["usb_series"]:
            self.assertIn("HSD1", row["location"])
            self.assertIn(row["initial_ohm"], (22, 33))
        for row in conditioning["sdio_pullups"]:
            if row["signal"] in ("DAT2", "DAT3"):
                self.assertIn("HSD2", row["location"])
                self.assertIn("disconnected", row["location"])
        self.assertIsNone(conditioning["sdio_clock_bias"]["fitted_pull"])
        self.assertIn("not populated", conditioning["sdio_clock_bias"]["dnp_footprint"])

    def test_clk_pullup_is_rejected_but_series_footprint_remains(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        conditioning = contract["branch_conditioning"]
        conditioning["sdio_pullups"].append({
            "signal": "CLK", "gpio": "GPIO9", "value_ohm": 10000,
            "location": "direct SDIO branch",
        })
        result = MODULE.build(contract=contract)
        self.assertIn("SDIO pull-ups must be fitted on CMD and DAT0..DAT3 only", result["errors"])
        self.assertIn("CLK", {row["signal"] for row in result["branch_conditioning"]["sdio_series"]})

    def test_edge_straps_and_fail_safe_hardware_ownership(self):
        result = MODULE.build()
        straps = {row["gpio"]: row for row in result["edge_straps"]["contacts"]}
        self.assertEqual((26, 1), (straps["GPIO25"]["module_pad"], straps["GPIO25"]["latched_value"]))
        self.assertEqual((5, 0), (straps["GPIO3"]["module_pad"], straps["GPIO3"]["latched_value"]))
        self.assertGreaterEqual(result["edge_straps"]["hold_after_c5_en_release_ms_min"], 3)
        self.assertTrue(result["ownership"]["latch"]["firmware_cannot_override"])
        service = next(row for row in result["ownership"]["states"] if row["state"] == "SERVICE_USB")
        self.assertEqual((1, 0, "high-Z", 0, 0),
                         (service["c5_en"], service["hub_run"], service["hub_sdio"], service["mux_oe"], service["mux_sel"]))
        self.assertIn("board power input", result["ownership"]["service_vbus"]["forbidden"])

    def test_performance_separates_bringup_from_target_acceptance(self):
        result = MODULE.build()
        performance = result["performance"]
        self.assertEqual((20_000_000, 10.0),
                         (performance["bringup_clock_hz"], performance["bringup_raw_mb_s"]))
        self.assertEqual((40_000_000, 20.0),
                         (performance["target_clock_hz"], performance["target_raw_mb_s"]))
        self.assertEqual((7.5, 40_000_000),
                         (performance["qualified_payload_floor_mb_s"], performance["qualification_frequency_hz"]))
        self.assertTrue(result["h0_integration"]["target_clock_explicit"])
        self.assertTrue(result["h0_integration"]["hil_frequency_semantics_explicit"])
        self.assertNotIn("top-level H0 promotion of 40 MHz target and 7.5 MB/s-at-40-MHz semantics",
                         result["open_gates"])

    def test_factory_route_is_accepted_only_with_complete_live_inventory(self):
        result = MODULE.build()
        route = result["production_mux_route"]
        self.assertEqual(("onsemi", "FSUSB42MUX", "C11355"),
                         (route["candidate"]["manufacturer"], route["candidate"]["mpn"],
                          route["candidate"]["jlcpcb_part_number"]))
        self.assertTrue(result["production_release_allowed"])
        self.assertEqual((66_698, 66_045, 1),
                         (route["live_inventory"]["stock"],
                          route["live_inventory"]["available_order_quantity"],
                          route["live_inventory"]["moq"]))
        self.assertEqual(0.3179, route["live_inventory"]["price_tiers_usd"][0]["unit_price"])
        self.assertNotIn("live JLC stock-or-explicit-route, MOQ and price for FSUSB42MUX/C11355",
                         result["open_gates"])

        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["production_mux_route"]["live_inventory"]["stock"] = None
        invalid = MODULE.build(contract=contract)
        self.assertIn("production mux cannot be accepted without live stock/route, MOQ and price", invalid["errors"])

    def test_exact_service_vbus_detector_latch_is_factory_accepted_and_fail_safe(self):
        result = MODULE.build()
        implementation = result["ownership"]["detector_latch_implementation"]
        detector = implementation["detector"]
        latch = implementation["latch"]
        qualifier = implementation["release_qualifier"]
        self.assertTrue(result["detector_latch_release_allowed"])
        self.assertEqual(("DMN2056U-7", "C332302"),
                         (detector["mpn"], detector["jlcpcb_part_number"]))
        self.assertEqual(("SN74LVC1G74DCUR", "C70285"),
                         (latch["mpn"], latch["jlcpcb_part_number"]))
        self.assertEqual(("74HC20PW,118", "C546719"),
                         (qualifier["mpn"], qualifier["jlcpcb_part_number"]))
        self.assertEqual(
            ["SERVICE_VBUS_PRESENT_N", "C5_EN_LOW_PROOF",
             "HUB_SDIO_HIGH_Z_PROOF", "AON_SERVICE_RELEASE_REQ"],
            qualifier["used_gate"]["inputs"],
        )
        latch_pins = {row["name"]: row["net"] for row in latch["pin_topology"]}
        self.assertEqual("SERVICE_VBUS_PRESENT_N", latch_pins["PRE_N"])
        self.assertEqual("C5_SERVICE_CLEAR_N", latch_pins["CLR_N"])
        self.assertLessEqual(detector["input_current_ua_nominal_at_5v"], 2.5)
        self.assertGreaterEqual(detector["gate_voltage_v_min_at_4v75_with_1pct_divider"], 2.35)
        self.assertNotIn("exact factory-placeable service-VBUS detector/latch implementation",
                         result["open_gates"])

    def test_service_latch_rejects_missing_inventory_or_bypass_of_release_proofs(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        implementation = contract["ownership"]["detector_latch_implementation"]
        implementation["latch"]["live_inventory"]["stock"] = None
        result = MODULE.build(contract=contract)
        self.assertIn("detector/latch cannot be accepted without complete live routes, MOQ and price",
                      result["errors"])
        self.assertFalse(result["detector_latch_release_allowed"])

        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        used_gate = contract["ownership"]["detector_latch_implementation"]["release_qualifier"]["used_gate"]
        used_gate["inputs"][-1] = "C5_FIRMWARE_RELEASE"
        result = MODULE.build(contract=contract)
        self.assertIn("release qualifier must be the exact four-condition NAND", result["errors"])

    def test_wrong_mux_branch_or_c5_pad_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["c5_module"]["signals"][4]["module_pad"] = 14
        result = MODULE.build(contract=contract)
        self.assertIn("GPIO13 module pad differs from devices.json", result["errors"])
        self.assertIn("C5 fixed SDIO/USB signal-to-module-pad map is incomplete or wrong", result["errors"])

        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        hsd2_plus = next(row for row in contract["mux"]["pin_topology"] if row["pin"] == 9)
        hsd2_plus["net"] = "HUB_C5_SDIO_DAT3_BRANCH"
        result = MODULE.build(contract=contract)
        self.assertIn("FSUSB42 MSOP-10 pin topology or branch polarity is wrong", result["errors"])

    def test_checked_in_generated_artifact_is_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render(result), MODULE.OUTPUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
