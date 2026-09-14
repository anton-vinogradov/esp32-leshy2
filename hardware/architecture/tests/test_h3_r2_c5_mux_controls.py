"""Finite C5 control graph mutations, not analog/sequence qualification.

The positive fixture is literal test data, independent of the checker and H2
generators. Physical maps: TI TS3USB221E table 4-1, SN74LV20A table 3-1,
Nexperia NX3008NBKS table 2. The NX channel names deliberately differ from
the former Diodes part while retaining the reviewed physical reset paths.
"""

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/verification/h3_r2_digital_interfaces.py"
UI, RF = "LESHY2-UI-R2", "LESHY2-RF-R2"

# project, reference, device id, exact MPN, functional kind, reference prefix.
PARTS = {
    "c5_service_usb_switch": (UI, "U22", "ti_ts3usb221erser", "TS3USB221ERSER",
                              "uqfn10_usb2_dpdt_power_off_protected_switch", "U"),
    "c5_service_release_logic": (UI, "U19", "ti_sn74lv20apwr", "SN74LV20APWR",
                                 "tssop14_dual_four_input_nand_gate", "U"),
    "c5_service_path_logic": (UI, "U59", "ti_sn74lv20apwr", "SN74LV20APWR",
                              "tssop14_dual_four_input_nand_gate", "U"),
    "c5_service_mux_logic_inverters": (UI, "U17", "nexperia_74lvc2g14gv_125", "74LVC2G14GV,125",
                                       "tsop6_dual_schmitt_inverter", "U"),
    "c5_service_owner_latch": (UI, "U18", "ti_sn74lvc1g74_dcur", "SN74LVC1G74DCUR",
                               "vssop8_d_flip_flop_async_preset_clear", "U"),
    "c5_service_hub_reset_sink": (UI, "Q2", "nexperia_nx3008nbks_115", "NX3008NBKS,115",
                                  "dual_30v_nmos_sot363_logic_level_reset_sink", "Q"),
    "safe_reset_sink_a": (UI, "Q6", "nexperia_nx3008nbks_115", "NX3008NBKS,115",
                           "dual_30v_nmos_sot363_logic_level_reset_sink", "Q"),
    "safe_reset_sink_b": (RF, "Q6", "nexperia_nx3008nbks_115", "NX3008NBKS,115",
                           "dual_30v_nmos_sot363_logic_level_reset_sink", "Q"),
    "c5_service_path_logic_bypass": (UI, "C86", "yageo_cc0402krx7r9bb104", "Yageo CC0402KRX7R9BB104",
                                     "100nf_10pct_50v_x7r_0402_converter_hf_input_capacitor", "C"),
    "evidence_mask": (RF, "U111", "ti_tca9535_pwr", "TCA9535PWR", None, "U"),
    "m1_ui_plug": (UI, "J18", "hirose_fx8c_80p_sv1_92", "Hirose FX8C-80P-SV1(92)", None, "J"),
    "m1_rf_receptacle": (RF, "J12", "hirose_fx8c_80s_sv5_92", "Hirose FX8C-80S-SV5(92)", None, "J"),
    "c5_mux_oe_pulldown": (UI, "R91", "yageo_rc0402fr_07100kl", "Yageo RC0402FR-07100KL", None, "R"),
    "c5_mux_sel_pulldown": (UI, "R92", "yageo_rc0402fr_07100kl", "Yageo RC0402FR-07100KL", None, "R"),
    "c5_service_reset_sink": (UI, "Q3", "diodes_dmn2056u_7", "Diodes Incorporated DMN2056U-7", None, "Q"),
}

# Entries are contact, physical pad, net. Explicit NC rows are required.
PINS = {
    "c5_service_usb_switch": [
        ("HSD1_PLUS", "1", "C5_SERVICE_USB_DP_BRANCH"),
        ("HSD1_MINUS", "2", "C5_SERVICE_USB_DM_BRANCH"),
        ("HSD2_PLUS", "3", "HUB_C5_SDIO_DAT2_BRANCH"),
        ("HSD2_MINUS", "4", "HUB_C5_SDIO_DAT3_BRANCH"),
        ("GND", "5", "POWER_GROUND"), ("OE", "6", "C5_MUX_DISABLE"),
        ("D_MINUS", "7", "C5_GPIO13_COMMON"), ("D_PLUS", "8", "C5_GPIO14_COMMON"),
        ("SEL", "9", "C5_MUX_SEL_REQUEST"), ("VCC", "10", "3V3_MAIN"),
    ],
    "c5_service_release_logic": [
        ("1A", "1", "SERVICE_VBUS_PRESENT_N"), ("1B", "2", "C5_EN_LOW_PROOF"),
        ("NC_3", "3", None), ("1C", "4", "HUB_RESET_LOW_PROOF"),
        ("1D", "5", "AON_SERVICE_RELEASE_REQ"), ("1Y", "6", "C5_SERVICE_CLEAR_N"),
        ("GND", "7", "POWER_GROUND"), ("2Y", "8", "C5_SERVICE_PATH_VALID"),
        ("2A", "9", "C5_SERVICE_OWNED"), ("2B", "10", "C5_MUX_SEL_REQUEST"),
        ("NC_11", "11", None), ("2C", "12", "AON_SAFE_3V3"),
        ("2D", "13", "AON_SAFE_3V3"), ("VCC", "14", "AON_SAFE_3V3"),
    ],
    "c5_service_path_logic": [
        ("1A", "1", "C5_SERVICE_PATH_ACK"), ("1B", "2", "C5_SERVICE_PATH_VALID"),
        ("NC_3", "3", None), ("1C", "4", "RUN_PERMIT"),
        ("1D", "5", "FAULT_ASSERT_N"), ("1Y", "6", "C5_MUX_DISABLE"),
        ("GND", "7", "POWER_GROUND"), ("2Y", "8", "C5_SERVICE_HUB_HOLD"),
        ("2A", "9", "C5_SERVICE_OWNER_NOT"), ("2B", "10", "C5_SERVICE_RELEASE_NOT"),
        ("NC_11", "11", None), ("2C", "12", "C5_MUX_SEL_REQUEST"),
        ("2D", "13", "AON_SAFE_3V3"), ("VCC", "14", "AON_SAFE_3V3"),
    ],
    "c5_service_mux_logic_inverters": [
        ("1A", "1", "C5_SERVICE_OWNED"), ("GND", "2", "POWER_GROUND"),
        ("2A", "3", "AON_SERVICE_RELEASE_REQ"), ("2Y", "4", "C5_SERVICE_RELEASE_NOT"),
        ("VCC", "5", "AON_SAFE_3V3"), ("1Y", "6", "C5_SERVICE_OWNER_NOT"),
    ],
    "c5_service_owner_latch": [("Q_N", "3", None), ("Q", "5", "C5_SERVICE_OWNED")],
    "c5_service_hub_reset_sink": [
        ("S1", "1", "POWER_GROUND"), ("G1", "2", "C5_RESET_KILL_GATE"),
        ("D2", "3", "HUB_RP_RESET_N"), ("S2", "4", "POWER_GROUND"),
        ("G2", "5", "C5_SERVICE_HUB_HOLD"), ("D1", "6", "HUB_RP_RESET_N"),
    ],
    "safe_reset_sink_a": [
        ("S1", "1", "POWER_GROUND"), ("G1", "2", "C5_RESET_KILL_GATE"),
        ("D2", "3", "S3_RESET_N"), ("S2", "4", "POWER_GROUND"),
        ("G2", "5", "S3_RESET_KILL_GATE"), ("D1", "6", "C5_RESET_N"),
    ],
    "safe_reset_sink_b": [
        ("S1", "1", "POWER_GROUND"), ("G1", "2", "POWER_GROUND"),
        ("D2", "3", "RF_RP_RESET_N"), ("S2", "4", "POWER_GROUND"),
        ("G2", "5", "RF_RESET_KILL_GATE"), ("D1", "6", None),
    ],
    "c5_service_path_logic_bypass": [
        ("END_1", "1", "AON_SAFE_3V3"), ("END_2", "2", "POWER_GROUND"),
    ],
    "evidence_mask": [
        ("P12", "15", "C5_MUX_SEL_REQUEST"), ("P13", "16", "C5_SERVICE_PATH_ACK"),
        ("P14", "17", "AON_SERVICE_RELEASE_REQ"), ("P15", "18", "C5_SERVICE_OWNED"),
    ],
    "c5_mux_oe_pulldown": [("END_1", "1", "C5_MUX_DISABLE"), ("END_2", "2", "POWER_GROUND")],
    "c5_mux_sel_pulldown": [("END_1", "1", "C5_MUX_SEL_REQUEST"), ("END_2", "2", "POWER_GROUND")],
    "c5_service_reset_sink": [("G", "1", "C5_MUX_DISABLE"), ("S", "2", "POWER_GROUND"), ("D", "3", "C5_RESET_N")],
}
for _connector in ("m1_ui_plug", "m1_rf_receptacle"):
    PINS[_connector] = [
        ("P37", "37", "RUN_PERMIT"), ("P38", "38", "FAULT_ASSERT_N"),
        ("P55", "55", "C5_MUX_SEL_REQUEST"), ("P56", "56", "C5_SERVICE_PATH_ACK"),
        ("P57", "57", "AON_SERVICE_RELEASE_REQ"), ("P58", "58", "C5_SERVICE_OWNED"),
    ]

# Remote/local boundary endpoints complete exact SEL/OE membership. Their
# identities are independently recorded, not synthesized by the checker.
BOUNDARY = [
    (RF, "R255", "yageo_rc0402fr_0710kl", "evidence_mask_p12_pulldown.END_1", "1", "C5_MUX_SEL_REQUEST"),
    (UI, "R87", "yageo_rc0402fr_0710kl", "c5_evidence_main_pullup.END_1", "1", "C5_MUX_SEL_REQUEST"),
]


def fixture():
    rows, instances, devices = [], [], {}
    for name, (project, ref, device_id, mpn, kind, prefix) in PARTS.items():
        instances.append(dict(instance=name, project=project, reference=ref,
                              device_id=device_id, mpn=mpn, reference_prefix=prefix,
                              bom_excluded=False))
        device = devices.setdefault(device_id, dict(mpn=mpn, kind=kind, contacts={}))
        for contact, physical, net in PINS[name]:
            device["contacts"][contact] = {"physical": physical}
            rows.append(dict(endpoint=f"{name}.{contact}", instance=name,
                             project=project, reference=ref, device_id=device_id,
                             contact=contact, physical=physical, net=net,
                             disposition="connected" if net is not None else "no_connect"))
    for project, ref, device_id, endpoint, physical, net in BOUNDARY:
        name, contact = endpoint.split(".")
        rows.append(dict(endpoint=endpoint, instance=name, project=project,
                         reference=ref, device_id=device_id, contact=contact,
                         physical=physical, net=net, disposition="connected"))
        devices.setdefault(device_id, {"contacts": {}})["contacts"][contact] = {"physical": physical}
    return rows, instances, devices


class C5MuxControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("c5_mux_controls_digital", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def setUp(self):
        self.rows, self.instances, self.devices = fixture()

    def checks(self):
        return self.module.c5_mux_topology_checks(self.rows, self.instances, self.devices)

    def row(self, endpoint):
        return next(row for row in self.rows if row["endpoint"] == endpoint)

    def assert_rejected(self):
        checks = self.checks()
        self.assertTrue(checks)
        self.assertFalse(self.module.all_true(checks), checks)

    def test_independent_positive_fixture_is_accepted(self):
        checks = self.checks()
        self.assertTrue(checks)
        self.assertTrue(self.module.all_true(checks), checks)
        self.assertTrue(all(type(value) is bool for value in checks.values()))

    def test_every_checked_pin_requires_unique_complete_identity(self):
        for instance, contacts in PINS.items():
            for contact, _, _ in contacts:
                endpoint = f"{instance}.{contact}"
                for field, value in (("project", "WRONG"), ("reference", "U999"),
                                     ("instance", "other"), ("device_id", "other"),
                                     ("contact", "OTHER"), ("physical", "999"),
                                     ("net", "WRONG"), ("disposition", "unassigned")):
                    with self.subTest(endpoint=endpoint, field=field):
                        self.setUp()
                        self.row(endpoint)[field] = value
                        self.assert_rejected()
                for mutation in ("missing", "duplicate"):
                    with self.subTest(endpoint=endpoint, mutation=mutation):
                        self.setUp()
                        row = self.row(endpoint)
                        if mutation == "missing":
                            self.rows.remove(row)
                        else:
                            self.rows.append(copy.deepcopy(row))
                        self.assert_rejected()

    def test_exact_mpn_prefix_and_bom_presence_cannot_change(self):
        for name in PARTS:
            for mutation in ("missing", "duplicate", "mpn", "prefix", "kind", "excluded"):
                if mutation == "kind" and PARTS[name][4] is None:
                    continue  # Boundary parts have exact MPN, not kind authority here.
                with self.subTest(instance=name, mutation=mutation):
                    self.setUp()
                    row = next(row for row in self.instances if row["instance"] == name)
                    if mutation == "missing":
                        self.instances.remove(row)
                    elif mutation == "duplicate":
                        self.instances.append(copy.deepcopy(row))
                    elif mutation == "mpn":
                        row["mpn"] = self.devices[row["device_id"]]["mpn"] = "OTHER"
                    elif mutation == "prefix":
                        row["reference_prefix"] = "X"
                    elif mutation == "kind":
                        self.devices[row["device_id"]]["kind"] = "unrelated_part"
                    else:
                        row["bom_excluded"] = True
                    self.assert_rejected()

    def test_old_pulldown_only_selector_is_rejected(self):
        self.row("c5_service_usb_switch.SEL")["net"] = "C5_MUX_SEL"
        self.row("c5_mux_sel_pulldown.END_1")["net"] = "C5_MUX_SEL"
        self.assert_rejected()

    def test_remote_selector_source_cannot_disappear(self):
        for endpoint in ("evidence_mask.P12", "m1_rf_receptacle.P55", "m1_ui_plug.P55"):
            with self.subTest(endpoint=endpoint):
                self.setUp()
                self.rows.remove(self.row(endpoint))
                self.assert_rejected()

    def test_ti_physical_pad_map_cannot_follow_old_onsemi_pad_numbers(self):
        for contact, old_pad in (("VCC", "1"), ("SEL", "2"), ("OE", "10")):
            with self.subTest(contact=contact):
                self.setUp()
                self.row("c5_service_usb_switch." + contact)["physical"] = old_pad
                # Changing the device map as well must not make this acceptable.
                self.devices["ti_ts3usb221erser"]["contacts"][contact]["physical"] = old_pad
                self.assert_rejected()

    def test_raw_q_n_cannot_replace_the_inverted_q_hold_input(self):
        self.row("c5_service_owner_latch.Q_N").update(
            net="C5_SERVICE_OWNER_NOT", disposition="connected")
        self.row("c5_service_mux_logic_inverters.1Y").update(net=None, disposition="no_connect")
        self.assert_rejected()

    def test_each_nand_veto_is_required(self):
        for contact in ("1A", "1B", "1C", "1D"):
            with self.subTest(contact=contact):
                self.setUp()
                self.row("c5_service_path_logic." + contact)["net"] = "AON_SAFE_3V3"
                self.assert_rejected()

    def test_duplicate_and_extra_oe_drivers_are_rejected(self):
        for mutation in ("duplicate", "additional"):
            with self.subTest(mutation=mutation):
                self.setUp()
                row = copy.deepcopy(self.row("c5_service_path_logic.1Y"))
                if mutation == "additional":
                    row.update(endpoint="foreign_driver.Y", instance="foreign_driver", reference="U999")
                self.rows.append(row)
                self.assert_rejected()

    def test_partial_nx_channel_swap_is_rejected_on_each_reset_package(self):
        for instance in ("c5_service_hub_reset_sink", "safe_reset_sink_a", "safe_reset_sink_b"):
            for pair in (("G1", "G2"), ("D1", "D2")):
                with self.subTest(instance=instance, pair=pair):
                    self.setUp()
                    a, b = (self.row(instance + "." + contact) for contact in pair)
                    # Q2 drains share a net: swap the physical channel mapping,
                    # not just equal reset labels, to expose a partial conversion.
                    a["physical"], b["physical"] = b["physical"], a["physical"]
                    self.assert_rejected()

    def test_each_common_kill_gate_and_reset_drain_is_retained(self):
        for endpoint in ("c5_service_hub_reset_sink.G1", "safe_reset_sink_a.G1",
                         "safe_reset_sink_a.G2", "safe_reset_sink_b.G2",
                         "safe_reset_sink_a.D1", "safe_reset_sink_a.D2", "safe_reset_sink_b.D2"):
            with self.subTest(endpoint=endpoint):
                self.setUp()
                self.row(endpoint).update(net=None, disposition="no_connect")
                self.assert_rejected()

    def test_current_regenerated_ledgers_match_the_exact_source_graph(self):
        rows = self.module.load(self.module.NETS)["rows"]
        instances = self.module.load(self.module.INSTANCES)["rows"]
        devices = self.module.load(self.module.DEVICES)["devices"]
        checks = self.module.c5_mux_topology_checks(rows, instances, devices)
        self.assertTrue(checks)
        self.assertTrue(self.module.all_true(checks),
                        [name for name, passed in checks.items() if not passed])

    def test_source_topology_does_not_claim_timing_firmware_or_release(self):
        result = self.module.build()
        control = result["c5_mux_control"]
        for field in ("timing_qualified", "power_sequences_qualified",
                      "firmware_service_manager_implemented", "production_release_allowed"):
            self.assertIs(False, control[field], field)
        self.assertIs(False, result["authorization"]["fabrication"])
        self.assertIs(False, result["authorization"]["final_product_claim"])


if __name__ == "__main__":
    unittest.main()
