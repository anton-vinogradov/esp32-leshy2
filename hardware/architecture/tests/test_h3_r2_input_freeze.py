import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h3_r2_input_freeze.py"
SPEC = importlib.util.spec_from_file_location("h3_r2_input_freeze", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class H3R2InputFreezeTest(unittest.TestCase):
    def without_reviewed_c5_control_eco(self, current):
        """Reverse only the declared ECO after proving every current endpoint.

        This is not a new golden baseline. Historical tuples below come from
        the pre-ECO graph; the two original SHA256 expectations stay unchanged.
        Work snapshots and mutable source contracts are not test authorities.
        """
        rows = copy.deepcopy(current)
        ui, rf = "LESHY2-UI-R2", "LESHY2-RF-R2"
        ui20 = "UI_20_C5_WIFI_IR_SERVICE"
        checked_fields = ("endpoint", "instance", "project", "sheet", "reference",
                          "device_id", "contact", "physical", "role", "net", "disposition")

        def part(name, project, sheet, ref, device, pins):
            actual = [row for row in rows if row["instance"] == name]
            self.assertEqual(len(pins), len(actual), name)
            index = {}
            for contact, physical, role, net in pins:
                matches = [row for row in actual if row["endpoint"] == name + "." + contact]
                self.assertEqual(1, len(matches), (name, contact))
                row = matches[0]
                self.assertEqual(
                    (name + "." + contact, name, project, sheet, ref, device,
                     contact, physical, role, net, "connected" if net is not None else "no_connect"),
                    tuple(row.get(key) for key in checked_fields), (name, contact))
                index[contact] = row
            return index

        nand_contacts = ("1A", "1B", "NC_3", "1C", "1D", "1Y", "GND",
                         "2Y", "2A", "2B", "NC_11", "2C", "2D", "VCC")

        def nand_pins(nets):
            return [(contact, str(pad),
                     "power" if contact in ("GND", "VCC") else
                     "no_connect" if contact.startswith("NC_") else "signal", net)
                    for pad, (contact, net) in enumerate(zip(nand_contacts, nets), 1)]

        added_logic = part("c5_service_path_logic", ui, ui20, "U59", "ti_sn74lv20apwr", nand_pins((
            "C5_SERVICE_PATH_ACK", "C5_SERVICE_PATH_VALID", None, "RUN_PERMIT", "FAULT_ASSERT_N",
            "C5_MUX_DISABLE", "POWER_GROUND", "C5_SERVICE_HUB_HOLD", "C5_SERVICE_OWNER_NOT",
            "C5_SERVICE_RELEASE_NOT", None, "C5_MUX_SEL_REQUEST", "AON_SAFE_3V3", "AON_SAFE_3V3")))
        added_bypass = part("c5_service_path_logic_bypass", ui, ui20, "C86", "yageo_cc0402krx7r9bb104", (
            ("END_1", "1", "power", "AON_SAFE_3V3"), ("END_2", "2", "power", "POWER_GROUND")))
        added = list(added_logic.values()) + list(added_bypass.values())
        self.assertEqual((16, 14, 2), (len(added), sum(row["disposition"] == "connected" for row in added),
                                      sum(row["disposition"] == "no_connect" for row in added)))
        rows = [row for row in rows if row["instance"] not in (
            "c5_service_path_logic", "c5_service_path_logic_bypass")]

        # TI physical pads and signal roles replace the onsemi layout. SEL is
        # now wired to REQUEST; all six switched data nets retain their roles.
        mux_map = {
            "HSD1_PLUS": ("1", "7", "C5_SERVICE_USB_DP_BRANCH"),
            "HSD1_MINUS": ("2", "6", "C5_SERVICE_USB_DM_BRANCH"),
            "HSD2_PLUS": ("3", "9", "HUB_C5_SDIO_DAT2_BRANCH"),
            "HSD2_MINUS": ("4", "8", "HUB_C5_SDIO_DAT3_BRANCH"),
            "GND": ("5", "5", "POWER_GROUND"), "OE": ("6", "10", "C5_MUX_DISABLE"),
            "D_MINUS": ("7", "4", "C5_GPIO13_COMMON"), "D_PLUS": ("8", "3", "C5_GPIO14_COMMON"),
            "SEL": ("9", "2", "C5_MUX_SEL_REQUEST"), "VCC": ("10", "1", "3V3_MAIN"),
        }
        mux = part("c5_service_usb_switch", ui, ui20, "U22", "ti_ts3usb221erser", [
            (contact, physical, "power" if contact in ("GND", "VCC") else "signal", net)
            for contact, (physical, _, net) in mux_map.items()])
        for contact, row in mux.items():
            row.update(device_id="onsemi_fsusb42_mux", physical=mux_map[contact][1])
            if contact in ("SEL", "OE"):
                row["role"] = "strap"
        mux["SEL"]["net"] = "C5_MUX_SEL"

        # NX names reverse the old Diodes channels. Physical KILL/reset pads
        # remain identical; only UI Q2 pad5 deliberately changes OWNER->HOLD.
        nx_contacts = ("S1", "G1", "D2", "S2", "G2", "D1")
        former_contacts = ("S2", "G2", "D1", "S1", "G1", "D2")
        nx_parts = (
            ("c5_service_hub_reset_sink", ui, ui20, "Q2", (
                "POWER_GROUND", "C5_RESET_KILL_GATE", "HUB_RP_RESET_N", "POWER_GROUND",
                "C5_SERVICE_HUB_HOLD", "HUB_RP_RESET_N")),
            ("safe_reset_sink_a", ui, "UI_50_FRONT_POWER_SAFETY", "Q6", (
                "POWER_GROUND", "C5_RESET_KILL_GATE", "S3_RESET_N", "POWER_GROUND",
                "S3_RESET_KILL_GATE", "C5_RESET_N")),
            ("safe_reset_sink_b", rf, "RF_50_TX_SAFETY_EVIDENCE", "Q6", (
                "POWER_GROUND", "POWER_GROUND", "RF_RP_RESET_N", "POWER_GROUND",
                "RF_RESET_KILL_GATE", None)),
        )
        for name, project, sheet, ref, nets in nx_parts:
            nx = part(name, project, sheet, ref, "nexperia_nx3008nbks_115", [
                (contact, str(pad), "signal", net)
                for pad, (contact, net) in enumerate(zip(nx_contacts, nets), 1)])
            for current_contact, former_contact in zip(nx_contacts, former_contacts):
                row = nx[current_contact]
                row.update(endpoint=name + "." + former_contact, contact=former_contact,
                           device_id="diodes_2n7002dw_7_f")
                if name == "c5_service_hub_reset_sink" and row["physical"] == "5":
                    row["net"] = "C5_SERVICE_OWNED"

        inverter = part("c5_service_mux_logic_inverters", ui, ui20, "U17", "nexperia_74lvc2g14gv_125", (
            ("1A", "1", "signal", "C5_SERVICE_OWNED"), ("GND", "2", "power", "POWER_GROUND"),
            ("2A", "3", "signal", "AON_SERVICE_RELEASE_REQ"), ("2Y", "4", "signal", "C5_SERVICE_RELEASE_NOT"),
            ("VCC", "5", "power", "AON_SAFE_3V3"), ("1Y", "6", "signal", "C5_SERVICE_OWNER_NOT")))
        for contact, historical_net in (("1A", "C5_SERVICE_PATH_ACK"), ("2A", "C5_MUX_DISABLE_N"),
                                        ("2Y", "C5_MUX_DISABLE"), ("1Y", "C5_SERVICE_PATH_ACK_N")):
            inverter[contact]["net"] = historical_net
        release = part("c5_service_release_logic", ui, ui20, "U19", "ti_sn74lv20apwr", nand_pins((
            "SERVICE_VBUS_PRESENT_N", "C5_EN_LOW_PROOF", None, "HUB_RESET_LOW_PROOF", "AON_SERVICE_RELEASE_REQ",
            "C5_SERVICE_CLEAR_N", "POWER_GROUND", "C5_SERVICE_PATH_VALID", "C5_SERVICE_OWNED",
            "C5_MUX_SEL_REQUEST", None, "AON_SAFE_3V3", "AON_SAFE_3V3", "AON_SAFE_3V3")))
        for row in release.values():
            row["device_id"] = "nexperia_74hc20pw_118"
        release["2Y"]["net"] = "C5_MUX_DISABLE_N"
        release["2B"]["net"] = "C5_SERVICE_PATH_ACK_N"
        selector_pull = part("c5_mux_sel_pulldown", ui, ui20, "R92", "yageo_rc0402fr_07100kl", (
            ("END_1", "1", "analog", "C5_MUX_SEL_REQUEST"), ("END_2", "2", "power", "POWER_GROUND")))
        selector_pull["END_1"]["net"] = "C5_MUX_SEL"
        return rows

    def test_current_freeze_covers_every_sheet_and_domain(self):
        result = MODULE.build()
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["errors"])
        self.assertEqual(22, result["summary"]["unique_matrix_sheets"])
        self.assertEqual(7, result["summary"]["workstream_count"])
        self.assertEqual(12, result["summary"]["shared_parameter_dependencies"])
        self.assertEqual(
            ["c5", "hub_rp", "pack", "rf_rp", "s3", "safety"],
            result["summary"]["covered_domains"],
        )
        self.assertFalse(result["authorization"]["pcb_placement_or_routing"])
        self.assertFalse(result["authorization"]["purchasing"])
        self.assertFalse(result["authorization"]["fabrication"])

    def test_duplicate_or_missing_sheet_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["workstreams"][1]["sheets"].append(contract["workstreams"][0]["sheets"][0])
        result = MODULE.build(contract)
        self.assertEqual("fail", result["status"])
        self.assertIn("a native sheet has more than one primary H3 workstream", result["errors"])

    def test_reviewed_counts_cannot_be_relabeled(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["expected"]["canonical_nets"] += 1
        result = MODULE.build(contract)
        self.assertIn("reviewed H2-R2 counts differ from the H3 input-freeze contract", result["errors"])

    def test_exact_ts_jack_nc6_removal_explains_one_pin_delta(self):
        contract = MODULE.load(MODULE.CONTRACT)
        review = contract["native_contact_count_change_review"]
        self.assertEqual(4321, contract["expected"]["physical_pins"])
        self.assertEqual([4306, 4305], review["physical_pins_before_after"])
        self.assertEqual([4302, 4301], review["logical_endpoints_before_after"])
        self.assertEqual([236, 235], review["explicit_nc_before_after"])
        self.assertEqual((0, 0), (review["removed_connected_endpoints"], review["added_endpoints"]))
        nets = MODULE.load(MODULE.NETS)
        # Later GPIO28 connects one existing NC; the C5 control ECO adds
        # U59/C86: 16 pins, 14 connected, 2 NC. Jack history stays unchanged.
        self.assertEqual((4317, 4081, 236), tuple(nets["summary"][key] for key in (
            "endpoint_count", "connected_endpoint_count", "no_connect_endpoint_count")))
        jack = [row for row in nets["rows"] if row["instance"] == "headphone_jack"]
        # Primary SJ-4351X-SMT p.2: TS has only terminals1..5, all used.
        expected = {"1": "HEADSET_MIC_RAW", "2": "HEADPHONE_LEFT_TIP", "3": "HEADPHONE_RIGHT_RING1",
                    "4": "AUDIO_GROUND", "5": "HEADSET_SWITCH_STATE"}
        self.assertEqual(5, len(jack))
        self.assertEqual(expected, {row["physical"]: row["net"] for row in jack})
        self.assertTrue(all(row["disposition"] == "connected" and row["device_id"] == "same_sky_sj_43515ts_smt_tr" for row in jack))
        self.assertNotIn("headphone_jack.RING1_SWITCH", {row["endpoint"] for row in nets["rows"]})
        kicad = MODULE.load(MODULE.KICAD)["summary"]
        self.assertEqual((4321, 4085, 236), tuple(kicad[key] for key in (
            "physical_symbol_pin_count", "connected_physical_pin_count", "explicit_no_connect_physical_pin_count")))

    def test_connected_functions_preserved_outside_reviewed_interface_corrections(self):
        # Fixed reviewed849a350 baseline, not a digest regenerated from the
        # current input or a test requiring a mutable Git HEAD.
        fields = ("endpoint", "project", "sheet", "reference", "contact", "physical", "role", "net", "disposition")
        current = MODULE.load(MODULE.NETS)["rows"]
        self.assertEqual(4081, sum(row.get("disposition") == "connected" for row in current))
        # Reverse this finite later ECO before the existing BOOT/S3/jack
        # normalization. Nothing outside the declared rows is removed.
        connected = [row for row in self.without_reviewed_c5_control_eco(current)
                     if row.get("disposition") == "connected"]
        self.assertEqual(4067, len(connected))
        boot = [row for row in connected if row["endpoint"] == "c5.GPIO28"]
        self.assertEqual(1, len(boot))
        self.assertEqual(("LESHY2-UI-R2", "U14", "15", "C5_BOOT_N"),
                         tuple(boot[0][key] for key in ("project", "reference", "physical", "net")))
        # Check the reviewed pre-correction function set with its original
        # digest; do not recalculate a golden hash from today's entire input.
        connected.remove(boot[0])
        # The later S3 ROM-UART correction exchanges only these four net
        # assignments, without changing the module, physical pads or counts.
        # Assert today's exact mapping before restoring the historical tuple
        # for this preservation proof. Dedicated-path tests cover the new nets.
        s3_swap = {
            7: ("7", "S3_HUB_D2", "S3_UART_SERVICE_TX"),
            8: ("12", "S3_HUB_D3", "S3_UART_SERVICE_RX"),
            43: ("37", "S3_UART_SERVICE_TX", "S3_HUB_D2"),
            44: ("36", "S3_UART_SERVICE_RX", "S3_HUB_D3"),
        }
        for gpio, (physical, current_net, historical_net) in s3_swap.items():
            matches = [row for row in connected if row["endpoint"] == f"s3.GPIO{gpio}"]
            self.assertEqual(1, len(matches))
            row = matches[0]
            self.assertEqual(("LESHY2-UI-R2", "U1", "esp32_s3_wroom_1u_n16r8", physical, current_net),
                             tuple(row[key] for key in ("project", "reference", "device_id", "physical", "net")))
            row["net"] = historical_net
        rows = sorted(tuple(row.get(key) for key in fields) for row in connected)
        self.assertEqual(4066, len(rows))
        payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode()
        self.assertEqual("33a9708e0db86040572f2eb85758252f2c8e568299376582b13a4ae6a3ff3571",
                         hashlib.sha256(payload).hexdigest())
        # Only the product receptacle's shell-mechanics description changed.
        # Normalize that one proven metadata delta, never any net or contact,
        # to keep the original pre-NC6 electrical-function proof meaningful.
        shell = [row for row in connected if row["endpoint"] == "product_usb_connector.SHIELD"]
        self.assertEqual(1, len(shell))
        self.assertEqual("gct_usb4105_gf_a", shell[0]["device_id"])
        self.assertEqual("four through-hole shell stakes", shell[0]["physical"])
        shell[0]["physical"] = "four 0.9-mm through-hole shell board locks"
        normalized = sorted(tuple(row.get(key) for key in fields) for row in connected)
        digest = hashlib.sha256(json.dumps(normalized, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        self.assertEqual("a8bc48ee64e32a8354904d1619552a35a2f669adc5da5a5efa09e5721b8c9e0d", digest)
        self.assertEqual(digest, MODULE.load(MODULE.CONTRACT)["native_contact_count_change_review"]["connected_tuple_sha256"])

    def test_c5_normalization_refuses_changes_outside_its_declared_current_mapping(self):
        current = MODULE.load(MODULE.NETS)["rows"]
        # One representative of each changed package/path; an incorrect pin,
        # net, role or owner must fail before historical normalization can hide it.
        endpoints = ("c5_service_path_logic.1C", "c5_service_path_logic.NC_3",
                     "c5_service_path_logic_bypass.END_1", "c5_service_usb_switch.SEL",
                     "c5_service_hub_reset_sink.G2", "safe_reset_sink_a.D1",
                     "safe_reset_sink_b.D1", "c5_service_mux_logic_inverters.1A",
                     "c5_service_release_logic.2B", "c5_mux_sel_pulldown.END_1")
        for endpoint in endpoints:
            for field in ("physical", "net", "role", "device_id", "project", "reference"):
                with self.subTest(endpoint=endpoint, field=field):
                    rows = copy.deepcopy(current)
                    next(row for row in rows if row["endpoint"] == endpoint)[field] = "UNREVIEWED"
                    with self.assertRaises(AssertionError):
                        self.without_reviewed_c5_control_eco(rows)
        for mutation in ("missing", "duplicate", "extra"):
            with self.subTest(mutation=mutation):
                rows = copy.deepcopy(current)
                added = next(row for row in rows if row["endpoint"] == "c5_service_path_logic.NC_3")
                if mutation == "missing":
                    rows.remove(added)
                else:
                    extra = copy.deepcopy(added)
                    if mutation == "extra":
                        extra.update(endpoint="c5_service_path_logic.EXTRA", contact="EXTRA", physical="15")
                    rows.append(extra)
                with self.assertRaises(AssertionError):
                    self.without_reviewed_c5_control_eco(rows)

    def test_pre_removal_physical_count_is_rejected(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["expected"]["physical_pins"] = 4306
        self.assertIn("reviewed H2-R2 counts differ from the H3 input-freeze contract", MODULE.build(contract)["errors"])

    def test_unknown_shared_parameter_dependency_fails_closed(self):
        contract = copy.deepcopy(MODULE.load(MODULE.CONTRACT))
        contract["workstreams"][1]["shared_parameter_dependencies"].append("missing_device")
        result = MODULE.build(contract)
        self.assertTrue(any("shared parameter dependencies" in error for error in result["errors"]))

    def test_checked_in_outputs_are_current(self):
        result = MODULE.build()
        self.assertEqual(MODULE.render_json(result), MODULE.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, False), MODULE.DOC_EN.read_text(encoding="utf-8"))
        self.assertEqual(MODULE.render_doc(result, True), MODULE.DOC_RU.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
