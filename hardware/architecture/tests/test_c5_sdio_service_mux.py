import copy
import importlib.util
import itertools
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
        self.assertEqual(("D+", "C5_GPIO14_COMMON"), (pins[8]["name"], pins[8]["net"]))
        self.assertEqual(("1D+", "C5_SERVICE_USB_DP_BRANCH"), (pins[1]["name"], pins[1]["net"]))
        self.assertEqual(("2D+", "HUB_C5_SDIO_DAT2_BRANCH"), (pins[3]["name"], pins[3]["net"]))
        self.assertEqual(("S", "C5_MUX_SEL_REQUEST"), (pins[9]["name"], pins[9]["net"]))

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
            self.assertIn("1D", row["location"])
            self.assertIn(row["initial_ohm"], (22, 33))
        for row in conditioning["sdio_pullups"]:
            if row["signal"] in ("DAT2", "DAT3"):
                self.assertIn("2D", row["location"])
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
        boot = result["boot_straps"]
        self.assertEqual({"GPIO27": 1, "GPIO28": 0}, boot["joint_download_boot_0"])
        self.assertEqual({"GPIO27": 1, "GPIO28": 1}, boot["application_boot"])
        self.assertFalse(boot["sampled_levels_and_timing_qualified"])

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

    def test_factory_route_is_schematic_only_even_with_complete_live_inventory(self):
        result = MODULE.build()
        route = result["production_mux_route"]
        self.assertEqual(("Texas Instruments", "TS3USB221ERSER", "C129313"),
                         (route["candidate"]["manufacturer"], route["candidate"]["mpn"],
                          route["candidate"]["jlcpcb_part_number"]))
        self.assertFalse(result["production_release_allowed"])
        self.assertTrue(result["mux_schematic_selection_allowed"])
        self.assertEqual((2998, 2993, 1),
                         (route["live_inventory"]["stock"],
                          route["live_inventory"]["available_order_quantity"],
                          route["live_inventory"]["moq"]))
        self.assertEqual("2026-09-14T00:03:22Z", route["live_inventory"]["checked_at"])
        self.assertEqual([0.3416, 0.2678, 0.2360, 0.1967, 0.1791, 0.1685],
                         [row["unit_price"] for row in route["live_inventory"]["price_tiers_usd"]])
        self.assertNotIn("live JLC stock-or-explicit-route, MOQ and price for TS3USB221ERSER/C129313",
                         result["open_gates"])

        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["production_mux_route"]["live_inventory"]["stock"] = None
        invalid = MODULE.build(contract=contract)
        self.assertIn("mux schematic selection requires a complete live stock/route, MOQ and price", invalid["errors"])

    def test_exact_detector_latch_routes_do_not_qualify_the_circuit(self):
        result = MODULE.build()
        implementation = result["ownership"]["detector_latch_implementation"]
        detector = implementation["detector"]
        latch = implementation["latch"]
        qualifier = implementation["release_qualifier"]
        self.assertFalse(result["detector_latch_release_allowed"])
        self.assertTrue(result["detector_latch_schematic_selection_allowed"])
        self.assertEqual(("DMN2056U-7", "C332302"),
                         (detector["mpn"], detector["jlcpcb_part_number"]))
        self.assertEqual(("SN74LVC1G74DCUR", "C70285"),
                         (latch["mpn"], latch["jlcpcb_part_number"]))
        self.assertEqual(("SN74LV20APWR", "C2862070"),
                         (qualifier["mpn"], qualifier["jlcpcb_part_number"]))
        self.assertEqual(
            ["SERVICE_VBUS_PRESENT_N", "C5_EN_LOW_PROOF",
             "HUB_SDIO_HIGH_Z_PROOF", "AON_SERVICE_RELEASE_REQ"],
            qualifier["used_gate"]["inputs"],
        )
        latch_pins = {row["name"]: row["net"] for row in latch["pin_topology"]}
        self.assertEqual("SERVICE_VBUS_PRESENT_N", latch_pins["PRE_N"])
        self.assertEqual("C5_SERVICE_CLEAR_N", latch_pins["CLR_N"])
        self.assertIsNone(latch_pins["Q_N"])
        self.assertLessEqual(detector["input_current_ua_nominal_at_5v"], 2.5)
        self.assertAlmostEqual(4.75 * 0.99 / 2,
                               detector["gate_voltage_v_resistor_only_min_at_4v75_with_1pct_divider"])
        self.assertFalse(detector["full_electrical_detection_qualified"])
        self.assertIn("gate leakage", detector["resistor_only_bound_excludes"])
        inventory = qualifier["live_inventory"]
        self.assertEqual((0, None, 21), (inventory["stock"], inventory["available_order_quantity"], inventory["moq"]))
        self.assertEqual(0.4265, inventory["preorder_estimate"]["unit_price"])
        self.assertEqual([], inventory["price_tiers_usd"])
        self.assertIsNone(inventory["lead_time_days"])
        self.assertEqual("2026-09-14T00:10:12Z", inventory["checked_at"])
        self.assertNotIn("exact factory-placeable service-VBUS detector/latch implementation",
                         result["open_gates"])

    def test_service_latch_rejects_missing_inventory_or_bypass_of_release_proofs(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        implementation = contract["ownership"]["detector_latch_implementation"]
        implementation["latch"]["live_inventory"]["stock"] = None
        result = MODULE.build(contract=contract)
        self.assertIn("detector/latch schematic selection requires complete stock or explicit Pre-order routes, MOQ and price",
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
        hsd2_plus = next(row for row in contract["mux"]["pin_topology"] if row["pin"] == 3)
        hsd2_plus["net"] = "HUB_C5_SDIO_DAT3_BRANCH"
        result = MODULE.build(contract=contract)
        self.assertIn("TS3USB221E RSE ten-contact topology or branch polarity is wrong", result["errors"])

    def test_all_64_states_match_actual_assigned_gate_inputs_not_equation_text(self):
        control = MODULE.build()["ownership"]["control_mapping"]
        for O, R, A, L, P, F in itertools.product((0, 1), repeat=6):
            values = dict(zip((control["inputs"][key]["net"] for key in "ORALPF"), (O, R, A, L, P, F)))
            values["AON_SAFE_3V3"] = 1
            for row in control["inverters"]:
                values[row["output"]] = int(not values[row["input"]])
            for row in control["nand_gates"][1:]:
                values[row["output"]] = int(not all(values[net] for net in row["inputs"]))
            allowed = bool(A and P and F and (O, R) in {(0, 0), (0, 1), (1, 0)})
            self.assertEqual(int(not allowed), values["C5_MUX_DISABLE"])
            self.assertEqual(int((O, L, R) != (0, 0, 1)), values["C5_SERVICE_HUB_HOLD"])

    def test_wrong_equations_missing_inputs_and_raw_q_n_are_rejected(self):
        for mutation in (
            lambda c: c["equations"].update(OE="O&!A"),
            lambda c: c["inputs"].pop("P"),
            lambda c: c["inputs"]["R"].update(net="C5_MUX_SEL"),
            lambda c: c["nand_gates"][3]["inputs"].__setitem__(0, "C5_SERVICE_FREE_DIAG"),
            lambda c: c.update(owner_q_n_used=True),
            lambda c: c["nand_gates"].pop(),
            lambda c: c["nand_gates"].append(copy.deepcopy(c["nand_gates"][0])),
            lambda c: c.update(kill_policy_changed=True),
            lambda c: c["reset_sinks"].update({"c5_service_hub_reset_sink.G1": "C5_SERVICE_HUB_HOLD"}),
        ):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            mutation(contract["ownership"]["control_mapping"])
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_duplicate_missing_and_old_mux_contacts_fail_closed(self):
        for mutation in (
            lambda rows: rows.append(copy.deepcopy(rows[0])),
            lambda rows: rows.pop(),
            lambda rows: rows[0].update(name="VCC", net="3V3_MAIN"),
            lambda rows: rows[0].update(pin=True),
        ):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            mutation(contract["mux"]["pin_topology"])
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_zero_stock_is_not_a_route_and_estimates_are_not_stocked_tiers(self):
        for field, value in (("route", "catalog card"), ("explicit_preorder_offered", False),
                             ("preorder_estimate", {}), ("moq", None), ("checked_at", ""),
                             ("price_is_estimate", False), ("stock", False)):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            inventory = contract["ownership"]["detector_latch_implementation"]["release_qualifier"]["live_inventory"]
            inventory[field] = value
            if field == "checked_at":
                # New-part route must carry its own timestamp, not inherit old detector evidence.
                inventory.pop("checked_at")
            self.assertTrue(MODULE.build(contract=contract)["errors"], (field, value))
        for value in (float("nan"), float("inf"), True, -1):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            contract["production_mux_route"]["live_inventory"]["price_tiers_usd"][0]["unit_price"] = value
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_no_schematic_or_inventory_state_can_authorize_functional_release(self):
        result = MODULE.build()
        self.assertTrue(result["open_gates"])
        self.assertTrue(all(value is False for value in result["qualification"].values()))
        for field in result["qualification"]:
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            contract["qualification"][field] = True
            self.assertTrue(MODULE.build(contract=contract)["errors"], field)
        for section in ("production_mux_route", "detector"):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            target = contract[section] if section != "detector" else contract["ownership"]["detector_latch_implementation"]
            target["production_release_allowed"] = True
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_boot_cannot_be_replaced_by_edge_straps_or_claimed_measured(self):
        for field, value in (("joint_download_boot_0", {"GPIO25": 1, "GPIO3": 0}),
                             ("hold_after_en_release_ms_min", 2),
                             ("sampled_levels_and_timing_qualified", True)):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            contract["boot_straps"][field] = value
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_reordered_or_unmeasured_waits_cannot_release_hub_early(self):
        for mutation in (
            lambda trace: trace.pop(2),
            lambda trace: trace.pop(5),
            lambda trace: trace.pop(7),
            lambda trace: trace[7].update(duration_ms=2.999),
            lambda trace: trace[6]["controls"].__setitem__(3, 0),
            lambda trace: trace[7].update(measured=True),
        ):
            contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
            mutation(contract["ownership"]["control_mapping"]["ordered_traces"]["service_to_runtime"])
            self.assertTrue(MODULE.build(contract=contract)["errors"])

    def test_missing_control_contract_and_empty_supplied_contract_do_not_use_defaults(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["ownership"].pop("control_mapping")
        self.assertTrue(MODULE.build(contract=contract)["errors"])
        self.assertTrue(MODULE.build(contract={})["errors"])

    def test_checked_in_generated_artifact_is_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render(result), MODULE.OUTPUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
