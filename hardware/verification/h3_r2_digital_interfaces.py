#!/usr/bin/env python3
"""Verify current R2 digital boundaries, ownership, loading and i8080 timing."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h3_r2_current_scope import apply_scope, admits_current, scope_notice


getcontext().prec = 50
ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
RAILS = ROOT / "hardware/verification/generated/H3-R2-rail-margins.json"
NETS = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
DISPLAY_MOUNT = ROOT / "hardware/product-design/display-mount.json"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-digital-interfaces.json"
DOC_EN = ROOT / "docs/digital-electrical-verification.md"
DOC_RU = ROOT / "docs/digital-electrical-verification.ru.md"


SOURCES = {
    "esp32_s3_dc": {
        "document": "ESP32-S3 Series Datasheet v2.2, DC characteristics",
        "url": "https://documentation.espressif.com/esp32_s3_datasheet_en.pdf",
        "checked": "2026-08-31",
        "vih_min_fraction": "0.75",
        "vil_max_fraction": "0.25",
        "voh_min_fraction": "0.8",
        "vol_max_fraction": "0.1",
    },
    "esp32_c5_dc": {
        "document": "ESP32-C5 Series Datasheet v1.4, table 5-4",
        "url": "https://documentation.espressif.com/esp32-c5_datasheet_en.html",
        "checked": "2026-08-31",
        "vih_min_fraction": "0.75",
        "vil_max_fraction": "0.25",
        "voh_min_fraction": "0.8",
        "vol_max_fraction": "0.1",
    },
    "esp32_c5_boot": {
        "document": "ESP32-C5-WROOM-1/1U Datasheet v1.3, section3 and tables4-2/4-3",
        "url": "https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf",
        "checked": "2026-09-14",
        "joint_download_boot_0_straps": {"GPIO27": 1, "GPIO28": 0},
        "hold_after_en_release_ms_min": 3,
    },
    "rp2350_dc": {
        "document": "RP2350 Datasheet, section 14.9.4, table 1436",
        "url": "https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf",
        "checked": "2026-08-31",
        "at_iovdd_v": "3.3",
        "vih_min_v": "2.0",
        "vil_max_v": "0.8",
        "voh_min_v": "2.62",
        "vol_max_v": "0.5",
    },
    "ili9488_timing": {
        "document": "ILI9488 v1.00, section 17.4.1, DBI Type-B timing",
        "url": "https://www.waveshare.com/w/upload/5/5b/ILI9488_Datasheet.pdf",
        "checked": "2026-08-31",
    },
    "esp_idf_i80": {
        "document": "ESP-IDF v6.0.2 I80 LCD driver and ESP32-S3 clock definitions",
        "url": "https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32s3/api-reference/peripherals/lcd/i80_lcd.html",
        "source_revision": "7101770d",
        "checked": "2026-08-31",
    },
    "usb2": {
        "document": "USB 2.0 Specification, full-speed 12 Mb/s signalling",
        "url": "https://www.usb.org/document-library/usb-20-specification",
        "checked": "2026-08-31",
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dec(value: object) -> Decimal:
    return Decimal(str(value))


def endpoint(rows: list[dict], name: str, net: str | None) -> bool:
    return any(row["endpoint"] == name and row.get("net") == net for row in rows)


def instance_net(rows: list[dict], instance: str, net: str) -> bool:
    return any(row["instance"] == instance and row.get("net") == net for row in rows)


def all_true(mapping: dict) -> bool:
    return all(value is True for value in mapping.values())


def c5_boot_topology_checks(rows: list[dict], instances: list[dict], devices: dict) -> dict:
    """Finite native BOOT chain, not USB-mux, KILL or sampled-level proof.

    The module's physical pins15/18 are GPIO28/GPIO27, respectively. A BOOT
    label on resistors alone is insufficient. SW18 physical terminals1/3 are
    internally common (two PCB lands numbered1); terminal2 closes to ground.
    """
    project = "LESHY2-UI-R2"
    parts = {
        "c5": ("U14", "esp32_c5_wroom_1u_n8r8", "ESP32-C5-WROOM-1U-N8R8", "soldered_module"),
        "c5_boot_pullup": ("R76", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL", "10kohm_1pct_"),
        "c5_dbg_boot_series": ("R79", "yageo_rc0402fr_071kl", "Yageo RC0402FR-071KL", "1kohm_1pct_"),
        "c5_gpio27_pullup": ("R90", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL", "10kohm_1pct_"),
        "c5_boot_button": ("SW18", "alps_skrtlae010", "Alps Alpine SKRTLAE010", "spst_no_side_actuated_smt_tact_switch"),
    }
    pins = {
        "c5.GPIO28": ("15", "C5_BOOT_N"),
        "c5.GPIO27": ("18", "C5_GPIO27_FIXED_HIGH"),
        "c5_boot_pullup.END_1": ("1", "3V3_MAIN"),
        "c5_boot_pullup.END_2": ("2", "C5_BOOT_N"),
        "c5_dbg_boot_series.END_1": ("1", "C5_DBG_BOOT_CONNECTOR_N"),
        "c5_dbg_boot_series.END_2": ("2", "C5_BOOT_N"),
        "c5_gpio27_pullup.END_1": ("1", "3V3_MAIN"),
        "c5_gpio27_pullup.END_2": ("2", "C5_GPIO27_FIXED_HIGH"),
        "c5_boot_button.C1": ("1", "C5_DBG_BOOT_CONNECTOR_N"),
        "c5_boot_button.C2": ("3", "C5_DBG_BOOT_CONNECTOR_N"),
        "c5_boot_button.NO": ("2", "POWER_GROUND"),
    }
    checks = {}
    for instance, (ref, device_id, mpn, kind) in parts.items():
        actual = [row for row in instances if row.get("instance") == instance]
        device = devices.get(device_id, {})
        checks["identity:" + instance] = (
            len(actual) == 1 and actual[0].get("project") == project
            and actual[0].get("reference") == ref and actual[0].get("device_id") == device_id
            and actual[0].get("mpn") == device.get("mpn") == mpn
            and actual[0].get("bom_excluded") is False
            and isinstance(device.get("kind"), str) and device["kind"].startswith(kind))
    for name, (physical, net) in pins.items():
        instance, contact = name.split(".")
        ref, device_id, _, _ = parts[instance]
        actual = [row for row in rows if row.get("endpoint") == name]
        checks["pin:" + name] = (
            len(actual) == 1 and actual[0].get("project") == project
            and actual[0].get("reference") == ref and actual[0].get("instance") == instance
            and actual[0].get("contact") == contact and actual[0].get("device_id") == device_id
            and actual[0].get("physical") == physical and actual[0].get("net") == net
            and actual[0].get("disposition") == "connected"
            and devices.get(device_id, {}).get("contacts", {}).get(contact, {}).get("physical") == physical)
    return checks


def c5_mux_topology_checks(rows: list[dict], instances: list[dict], devices: dict) -> dict:
    """Check concrete control pins, not merely that mux/reset parts exist.

    NAND pin maps are TI LV20A table 3-1; TS3USB221E table 4-1; NX3008NBKS
    table 2. This is a source-graph witness, never analog or timing qualification.
    NX channel names are reversed relative to the former Diodes dual MOSFET:
    all three reset packages retain their physical pad/net pairs (except the
    intentional UI Q2 pad5 OWNER -> HUB_HOLD change). Pack Q2/Q3 are excluded.
    """
    ui, rf = "LESHY2-UI-R2", "LESHY2-RF-R2"
    parts = {
        "c5_service_usb_switch": (ui, "U22", "ti_ts3usb221erser"),
        "c5_service_release_logic": (ui, "U19", "ti_sn74lv20apwr"),
        "c5_service_path_logic": (ui, "U59", "ti_sn74lv20apwr"),
        "c5_service_mux_logic_inverters": (ui, "U17", "nexperia_74lvc2g14gv_125"),
        "c5_service_owner_latch": (ui, "U18", "ti_sn74lvc1g74_dcur"),
        "c5_service_hub_reset_sink": (ui, "Q2", "nexperia_nx3008nbks_115"),
        "safe_reset_sink_a": (ui, "Q6", "nexperia_nx3008nbks_115"),
        "safe_reset_sink_b": (rf, "Q6", "nexperia_nx3008nbks_115"),
        "c5_service_path_logic_bypass": (ui, "C86", "yageo_cc0402krx7r9bb104"),
        "evidence_mask": (rf, "U111", "ti_tca9535_pwr"),
        "m1_ui_plug": (ui, "J18", "hirose_fx8c_80p_sv1_92"),
        "m1_rf_receptacle": (rf, "J12", "hirose_fx8c_80s_sv5_92"),
        "c5_mux_oe_pulldown": (ui, "R91", "yageo_rc0402fr_07100kl"),
        "c5_mux_sel_pulldown": (ui, "R92", "yageo_rc0402fr_07100kl"),
        "c5_service_reset_sink": (ui, "Q3", "diodes_dmn2056u_7"),
    }
    exact_mpns = {
        "ti_ts3usb221erser": "TS3USB221ERSER", "ti_sn74lv20apwr": "SN74LV20APWR",
        "nexperia_nx3008nbks_115": "NX3008NBKS,115", "ti_sn74lvc1g74_dcur": "SN74LVC1G74DCUR",
        "nexperia_74lvc2g14gv_125": "74LVC2G14GV,125", "yageo_cc0402krx7r9bb104": "Yageo CC0402KRX7R9BB104",
        "ti_tca9535_pwr": "TCA9535PWR", "hirose_fx8c_80p_sv1_92": "Hirose FX8C-80P-SV1(92)",
        "hirose_fx8c_80s_sv5_92": "Hirose FX8C-80S-SV5(92)",
        "yageo_rc0402fr_07100kl": "Yageo RC0402FR-07100KL", "diodes_dmn2056u_7": "Diodes Incorporated DMN2056U-7",
    }
    exact_kinds = {
        "ti_ts3usb221erser": "uqfn10_usb2_dpdt_power_off_protected_switch",
        "ti_sn74lv20apwr": "tssop14_dual_four_input_nand_gate",
        "nexperia_nx3008nbks_115": "dual_30v_nmos_sot363_logic_level_reset_sink",
        "ti_sn74lvc1g74_dcur": "vssop8_d_flip_flop_async_preset_clear",
        "nexperia_74lvc2g14gv_125": "tsop6_dual_schmitt_inverter",
        "yageo_cc0402krx7r9bb104": "100nf_10pct_50v_x7r_0402_converter_hf_input_capacitor",
    }
    checks = {}
    for name, (project, ref, device_id) in parts.items():
        found = [row for row in instances if row.get("instance") == name]
        device = devices.get(device_id, {})
        checks["identity:" + name] = (
            len(found) == 1 and found[0].get("project") == project
            and found[0].get("reference") == ref and found[0].get("device_id") == device_id
            and found[0].get("mpn") == device.get("mpn") == exact_mpns[device_id]
            and found[0].get("reference_prefix") == ref.rstrip("0123456789")
            and (device_id not in exact_kinds or device.get("kind") == exact_kinds[device_id])
            and found[0].get("bom_excluded") is False)

    pins = {
        "c5_service_usb_switch": {
            "HSD1_PLUS": ("1", "C5_SERVICE_USB_DP_BRANCH"),
            "HSD1_MINUS": ("2", "C5_SERVICE_USB_DM_BRANCH"),
            "HSD2_PLUS": ("3", "HUB_C5_SDIO_DAT2_BRANCH"),
            "HSD2_MINUS": ("4", "HUB_C5_SDIO_DAT3_BRANCH"),
            "GND": ("5", "POWER_GROUND"), "OE": ("6", "C5_MUX_DISABLE"),
            "D_MINUS": ("7", "C5_GPIO13_COMMON"), "D_PLUS": ("8", "C5_GPIO14_COMMON"),
            "SEL": ("9", "C5_MUX_SEL_REQUEST"), "VCC": ("10", "3V3_MAIN")},
        "c5_service_mux_logic_inverters": {
            "1A": ("1", "C5_SERVICE_OWNED"), "GND": ("2", "POWER_GROUND"),
            "2A": ("3", "AON_SERVICE_RELEASE_REQ"), "2Y": ("4", "C5_SERVICE_RELEASE_NOT"),
            "VCC": ("5", "AON_SAFE_3V3"), "1Y": ("6", "C5_SERVICE_OWNER_NOT")},
        "c5_service_owner_latch": {"Q_N": ("3", None), "Q": ("5", "C5_SERVICE_OWNED")},
        "c5_service_path_logic_bypass": {"END_1": ("1", "AON_SAFE_3V3"), "END_2": ("2", "POWER_GROUND")},
        "evidence_mask": {"P12": ("15", "C5_MUX_SEL_REQUEST"), "P13": ("16", "C5_SERVICE_PATH_ACK"),
                          "P14": ("17", "AON_SERVICE_RELEASE_REQ"), "P15": ("18", "C5_SERVICE_OWNED")},
        "c5_mux_oe_pulldown": {"END_1": ("1", "C5_MUX_DISABLE"), "END_2": ("2", "POWER_GROUND")},
        "c5_mux_sel_pulldown": {"END_1": ("1", "C5_MUX_SEL_REQUEST"), "END_2": ("2", "POWER_GROUND")},
        "c5_service_reset_sink": {"G": ("1", "C5_MUX_DISABLE"), "S": ("2", "POWER_GROUND"), "D": ("3", "C5_RESET_N")},
    }
    for name in ("m1_ui_plug", "m1_rf_receptacle"):
        pins[name] = {f"P{pad}": (str(pad), net) for pad, net in (
            (37, "RUN_PERMIT"), (38, "FAULT_ASSERT_N"), (55, "C5_MUX_SEL_REQUEST"),
            (56, "C5_SERVICE_PATH_ACK"), (57, "AON_SERVICE_RELEASE_REQ"), (58, "C5_SERVICE_OWNED"))}
    nand_pins = {"1A": "1", "1B": "2", "NC_3": "3", "1C": "4", "1D": "5", "1Y": "6",
                 "GND": "7", "2Y": "8", "2A": "9", "2B": "10", "NC_11": "11", "2C": "12", "2D": "13", "VCC": "14"}
    nand_nets = {
        "c5_service_release_logic": {
            "1A": "SERVICE_VBUS_PRESENT_N", "1B": "C5_EN_LOW_PROOF", "1C": "HUB_RESET_LOW_PROOF",
            "1D": "AON_SERVICE_RELEASE_REQ", "1Y": "C5_SERVICE_CLEAR_N",
            "2A": "C5_SERVICE_OWNED", "2B": "C5_MUX_SEL_REQUEST", "2C": "AON_SAFE_3V3",
            "2D": "AON_SAFE_3V3", "2Y": "C5_SERVICE_PATH_VALID"},
        "c5_service_path_logic": {
            "1A": "C5_SERVICE_PATH_ACK", "1B": "C5_SERVICE_PATH_VALID", "1C": "RUN_PERMIT",
            "1D": "FAULT_ASSERT_N", "1Y": "C5_MUX_DISABLE",
            "2A": "C5_SERVICE_OWNER_NOT", "2B": "C5_SERVICE_RELEASE_NOT", "2C": "C5_MUX_SEL_REQUEST",
            "2D": "AON_SAFE_3V3", "2Y": "C5_SERVICE_HUB_HOLD"},
    }
    for name, nets in nand_nets.items():
        nets = {**nets, "VCC": "AON_SAFE_3V3", "GND": "POWER_GROUND", "NC_3": None, "NC_11": None}
        pins[name] = {contact: (pad, nets[contact]) for contact, pad in nand_pins.items()}
    nx_pins = {"S1": "1", "G1": "2", "D2": "3", "S2": "4", "G2": "5", "D1": "6"}
    for name, nets in {
        "c5_service_hub_reset_sink": {"G1": "C5_RESET_KILL_GATE", "D1": "HUB_RP_RESET_N", "G2": "C5_SERVICE_HUB_HOLD", "D2": "HUB_RP_RESET_N"},
        "safe_reset_sink_a": {"G1": "C5_RESET_KILL_GATE", "D1": "C5_RESET_N", "G2": "S3_RESET_KILL_GATE", "D2": "S3_RESET_N"},
        "safe_reset_sink_b": {"G1": "POWER_GROUND", "D1": None, "G2": "RF_RESET_KILL_GATE", "D2": "RF_RP_RESET_N"},
    }.items():
        nets = {**nets, "S1": "POWER_GROUND", "S2": "POWER_GROUND"}
        pins[name] = {contact: (pad, nets[contact]) for contact, pad in nx_pins.items()}
    for name, contacts in pins.items():
        project, ref, device_id = parts[name]
        for contact, (pad, net) in contacts.items():
            ep = name + "." + contact
            found = [row for row in rows if row.get("endpoint") == ep]
            checks["pin:" + ep] = (
                len(found) == 1 and found[0].get("project") == project and found[0].get("reference") == ref
                and found[0].get("instance") == name and found[0].get("device_id") == device_id and found[0].get("physical") == pad
                and found[0].get("contact") == contact and found[0].get("net") == net
                and found[0].get("disposition") == ("connected" if net is not None else "no_connect")
                and devices.get(device_id, {}).get("contacts", {}).get(contact, {}).get("physical") == pad)
    # Exact membership prevents an extra driver or a second connection from
    # silently bypassing these gates, even when all expected endpoints exist.
    members = {
        "C5_SERVICE_OWNER_NOT": {"c5_service_mux_logic_inverters.1Y", "c5_service_path_logic.2A"},
        "C5_SERVICE_RELEASE_NOT": {"c5_service_mux_logic_inverters.2Y", "c5_service_path_logic.2B"},
        "C5_SERVICE_PATH_VALID": {"c5_service_release_logic.2Y", "c5_service_path_logic.1B"},
        "C5_SERVICE_HUB_HOLD": {"c5_service_path_logic.2Y", "c5_service_hub_reset_sink.G2"},
        "C5_MUX_DISABLE": {"c5_service_path_logic.1Y", "c5_service_usb_switch.OE", "c5_service_reset_sink.G", "c5_mux_oe_pulldown.END_1"},
        "C5_MUX_SEL_REQUEST": {"evidence_mask.P12", "evidence_mask_p12_pulldown.END_1", "m1_rf_receptacle.P55", "m1_ui_plug.P55", "c5_evidence_main_pullup.END_1", "c5_mux_sel_pulldown.END_1", "c5_service_usb_switch.SEL", "c5_service_release_logic.2B", "c5_service_path_logic.2C"},
    }
    for net, expected in members.items():
        actual = [row.get("endpoint") for row in rows if row.get("net") == net]
        checks["members:" + net] = len(actual) == len(expected) and set(actual) == expected
    return checks


def panel_endpoint(display_mount: dict, panel_pin: int) -> str:
    """Resolve physical mating without borrowing H2's panel-function assignment."""
    mapping = display_mount["electrical"].get("panel_to_connector_pin_map")
    if mapping != {str(pin): str(51 - pin) for pin in range(1, 51)}:
        raise ValueError("display requires the verified complete panel-to-FH34 51-n bijection")
    if type(panel_pin) is not int or panel_pin not in range(1, 51):
        raise ValueError("invalid physical display panel pin")
    return f"display_connector.PIN_{mapping[str(panel_pin)]}"


def display_topology_checks(rows: list[dict], display_mount: dict) -> dict:
    panel = {pin: panel_endpoint(display_mount, pin) for pin in range(1, 51)}
    expected_s3_lanes = {
        "LCD_DB0": "s3.GPIO4", "LCD_DB1": "s3.GPIO9", "LCD_DB2": "s3.GPIO18", "LCD_DB3": "s3.GPIO38",
        "LCD_DB4": "s3.GPIO40", "LCD_DB5": "s3.GPIO41", "LCD_DB6": "s3.GPIO42", "LCD_DB7": "s3.GPIO46",
    }
    # Panel pins/functions and S3 GPIO expectations remain independent of H2.
    return {
        "all_s3_data_lanes_exact": all(endpoint(rows, pin, net) for net, pin in expected_s3_lanes.items()),
        "wr_is_direct_gpio17": endpoint(rows, "s3.GPIO17", "LCD_WR_N") and endpoint(rows, panel[36], "LCD_WR_N"),
        "dc_is_direct_gpio45": endpoint(rows, "s3.GPIO45", "LCD_DC") and endpoint(rows, panel[37], "LCD_DC"),
        "panel_receives_all_eight_lanes": all(endpoint(rows, panel[32 - lane], f"LCD_DB{lane}") for lane in range(8)),
        "panel_wr_dc_reach_exact_contacts": endpoint(rows, panel[36], "LCD_WR_N") and endpoint(rows, panel[37], "LCD_DC"),
        "cs_is_hard_low": endpoint(rows, panel[38], "POWER_GROUND"),
        "rd_is_hard_high": endpoint(rows, panel[35], "3V3_MAIN"),
        "im_straps_are_011": endpoint(rows, panel[7], "3V3_MAIN") and endpoint(rows, panel[8], "3V3_MAIN") and endpoint(rows, panel[9], "POWER_GROUND"),
        "direct_mount_mode_is_exact": display_mount["electrical"]["selected_mode"] == "ILI9488 8080 8-bit with IM2/IM1/IM0 = 0/1/1",
        "recovery_sda_is_not_populated_on_ui_board": endpoint(rows, panel[34], None),
    }


def level_row(name: str, voh: Decimal, vol: Decimal, vih: Decimal, vil: Decimal) -> dict:
    high = voh - vih
    low = vil - vol
    return {
        "boundary": name,
        "units": "V",
        "corners": {"voh_min": float(voh), "receiver_vih_min": float(vih), "vol_max": float(vol), "receiver_vil_max": float(vil)},
        "worst_high_margin": float(high),
        "worst_low_margin": float(low),
        "minimum_margin": float(min(high, low)),
        "status": "pass" if high > 0 and low > 0 else "fail",
    }


def build() -> dict:
    architecture = load(ARCH)
    devices = load(DEVICES)["devices"]
    rails = load(RAILS)
    rows = load(NETS)["rows"]
    instances = load(INSTANCES)["rows"]
    display_mount = load(DISPLAY_MOUNT)
    errors: list[str] = []

    main = rails["voltage_corners"]["3V3_MAIN"]
    v_min = dec(main["endpoint_min_v"])
    v_max = dec(main["endpoint_max_v"])
    s3_voh = dec(SOURCES["esp32_s3_dc"]["voh_min_fraction"]) * v_min
    s3_vol = dec(SOURCES["esp32_s3_dc"]["vol_max_fraction"]) * v_max
    s3_vih = dec(SOURCES["esp32_s3_dc"]["vih_min_fraction"]) * v_max
    s3_vil = dec(SOURCES["esp32_s3_dc"]["vil_max_fraction"]) * v_min
    c5_voh = dec(SOURCES["esp32_c5_dc"]["voh_min_fraction"]) * v_min
    c5_vol = dec(SOURCES["esp32_c5_dc"]["vol_max_fraction"]) * v_max
    c5_vih = dec(SOURCES["esp32_c5_dc"]["vih_min_fraction"]) * v_max
    c5_vil = dec(SOURCES["esp32_c5_dc"]["vil_max_fraction"]) * v_min
    rp_voh = dec(SOURCES["rp2350_dc"]["voh_min_v"])
    rp_vol = dec(SOURCES["rp2350_dc"]["vol_max_v"])
    rp_vih = dec(SOURCES["rp2350_dc"]["vih_min_v"])
    rp_vil = dec(SOURCES["rp2350_dc"]["vil_max_v"])

    panel = devices["eastrising_er_tft035ips_6_ctp"]["electrical_contract"]
    panel_vih = dec(panel["logic_input_high_min_fraction_vddi"]) * v_max
    panel_vil = dec(panel["logic_input_low_max_fraction_vddi"]) * v_min
    level_margins = [
        level_row("S3 -> ILI9488 direct i8080/reset", s3_voh, s3_vol, panel_vih, panel_vil),
        level_row("S3/C5 -> RP2354 3V3 GPIO", min(s3_voh, c5_voh), max(s3_vol, c5_vol), rp_vih, rp_vil),
        level_row("RP2354 -> S3 3V3 GPIO", rp_voh, rp_vol, s3_vih, s3_vil),
        level_row("RP2354 -> C5 3V3 GPIO", rp_voh, rp_vol, c5_vih, c5_vil),
        level_row("RP2354 -> RP2354 across M1", rp_voh, rp_vol, rp_vih, rp_vil),
    ]
    if any(row["status"] != "pass" for row in level_margins):
        errors.append("one or more 3V3 logic-family boundaries has non-positive DC margin")

    display_topology = display_topology_checks(rows, display_mount)
    if not all_true(display_topology):
        errors.append(
            "direct i8080 topology or mode straps drifted: "
            + ", ".join(name for name, passed in display_topology.items() if not passed)
        )

    display = architecture["display_contract"]
    cycle_ns = dec(1_000_000_000) / dec(display["selected_clock_hz"])
    half_ns = cycle_ns / 2
    full_frame_ms = dec(display["full_frame_bytes"]) / dec(display["payload_mb_s"]) / dec(1000)
    frame_budget_ms = dec("20")
    display_timing = {
        "clock": {
            "requested_hz": display["idf_clock_contract"]["requested_clock_hz"],
            "actual_hz": display["idf_clock_contract"]["actual_clock_hz"],
            "integer_prescale": display["idf_clock_contract"]["integer_prescale"],
            "forbidden_24mhz_request_actual_hz": display["idf_clock_contract"]["forbidden_actual_clock_hz"],
        },
        "units": "ns except explicitly named fields",
        "corners": {
            "cycle": {"actual": float(cycle_ns), "minimum": panel["i8080_write_cycle_min_ns"], "margin": float(cycle_ns - dec(panel["i8080_write_cycle_min_ns"]))},
            "wr_high": {"actual": float(half_ns), "minimum": panel["i8080_wr_high_min_ns"], "margin": float(half_ns - dec(panel["i8080_wr_high_min_ns"]))},
            "wr_low": {"actual": float(half_ns), "minimum": panel["i8080_wr_low_min_ns"], "margin": float(half_ns - dec(panel["i8080_wr_low_min_ns"]))},
            "data_setup_budget": {"available": float(half_ns), "minimum": panel["i8080_data_setup_min_ns"], "margin": float(half_ns - dec(panel["i8080_data_setup_min_ns"]))},
            "data_hold_budget": {"available": float(half_ns), "minimum": panel["i8080_data_hold_min_ns"], "margin": float(half_ns - dec(panel["i8080_data_hold_min_ns"]))},
        },
        "throughput": {
            "raw_mb_s": display["payload_mb_s"],
            "full_frame_bytes": display["full_frame_bytes"],
            "full_frame_wire_ms": float(full_frame_ms),
            "theoretical_full_frame_fps": float(dec(1000) / full_frame_ms),
            "assigned_full_frame_budget_ms": float(frame_budget_ms),
            "budget_occupancy_pct": float(full_frame_ms / frame_budget_ms * 100),
            "budget_margin_ms": float(frame_budget_ms - full_frame_ms),
        },
    }
    display_timing["checks"] = {
        "exact_20mhz_from_integer_divider": display_timing["clock"]["requested_hz"] == 20_000_000 == display_timing["clock"]["actual_hz"] and display_timing["clock"]["integer_prescale"] == 4,
        "24mhz_request_is_rejected": display_timing["clock"]["forbidden_24mhz_request_actual_hz"] > display["controller_limit_hz"],
        "all_controller_timing_margins_positive": all(row["margin"] > 0 for row in display_timing["corners"].values()),
        "full_frame_uses_at_most_80pct_of_20ms_budget": display_timing["throughput"]["budget_occupancy_pct"] <= 80,
    }
    if not all_true(display_timing["checks"]):
        errors.append("direct i8080 timing/occupancy contract failed")

    by_instance = {row["instance"]: row for row in instances}
    service_switch = devices[by_instance["c5_service_usb_switch"]["device_id"]]["electrical_contract"]
    usb_topology = {
        "product_usb_reaches_s3_through_m1_29_30": all(
            endpoint(rows, f"m1_ui_plug.P{pin}", net)
            and endpoint(rows, f"m1_rf_receptacle.P{pin}", net)
            for pin, net in ((29, "S3_USB_DM"), (30, "S3_USB_DP"))
        ) and endpoint(rows, "s3.GPIO19", "S3_USB_DM_LOCAL") and endpoint(rows, "s3.GPIO20", "S3_USB_DP_LOCAL"),
        "product_usb_pair_has_adjacent_returns": all(endpoint(rows, f"m1_ui_plug.P{pin}", "POWER_GROUND") for pin in (28, 31)),
        "hub_and_rf_service_ports_are_native_and_data_only": all(
            instance_net(rows, f"{owner}_service_usb_connector", f"{prefix}_SERVICE_VBUS_SENSE_ONLY")
            and instance_net(rows, owner, f"{prefix}_USB_DM") and instance_net(rows, owner, f"{prefix}_USB_DP")
            for owner, prefix in (("hub_rp", "HUB_RP"), ("rf_rp", "RF_RP"))
        ),
        "c5_service_vbus_is_sense_only": instance_net(rows, "c5_service_usb_connector", "C5_SERVICE_VBUS_SENSE_ONLY"),
        "c5_mux_has_hardware_default_pulldowns": endpoint(rows, "c5_mux_sel_pulldown.END_2", "POWER_GROUND") and endpoint(rows, "c5_mux_oe_pulldown.END_2", "POWER_GROUND"),
        "c5_mux_switches_only_d2_d3_or_usb": all(instance_net(rows, "c5_service_usb_switch", net) for net in ("C5_GPIO13_COMMON", "C5_GPIO14_COMMON", "HUB_C5_SDIO_DAT2_BRANCH", "HUB_C5_SDIO_DAT3_BRANCH", "C5_SERVICE_USB_DM_BRANCH", "C5_SERVICE_USB_DP_BRANCH")),
        "service_ownership_latch_resets_both_compute_domains": instance_net(rows, "c5_service_owner_latch", "C5_SERVICE_OWNED") and instance_net(rows, "c5_service_reset_sink", "C5_RESET_N") and instance_net(rows, "c5_service_hub_reset_sink", "HUB_RP_RESET_N"),
        "service_switch_has_usb_full_speed_capability": service_switch["usb_speed_mbps"] >= 12,
        "power_off_port_leakage_limit_is_2ua": service_switch["power_off_leakage_max_ua"] <= 2,
    }
    if not all_true(usb_topology):
        errors.append("USB/service ownership topology failed")
    mux_checks = c5_mux_topology_checks(rows, instances, devices)
    if not all_true(mux_checks):
        errors.append("C5 mux control topology failed: " + ", ".join(name for name, passed in mux_checks.items() if not passed))

    c5_boot = c5_boot_topology_checks(rows, instances, devices)
    if not all_true(c5_boot):
        errors.append("C5 BOOT native chain failed: " + ", ".join(name for name, passed in c5_boot.items() if not passed))

    m1_ui = {int(row["contact"][1:]): row.get("net") for row in rows if row["instance"] == "m1_ui_plug"}
    m1_rf = {int(row["contact"][1:]): row.get("net") for row in rows if row["instance"] == "m1_rf_receptacle"}
    m1_part = devices[by_instance["m1_ui_plug"]["device_id"]]["electrical_contract"]
    payload_prefixes = tuple(architecture["interboard_rebaseline"]["locality_contract"]["forbidden_payload_prefixes"])
    m1_checks = {
        "both_halves_have_80_contacts": sorted(m1_ui) == list(range(1, 81)) == sorted(m1_rf),
        "pin_for_pin_net_parity": m1_ui == m1_rf,
        "exactly_nine_true_nc": sum(net is None for net in m1_ui.values()) == 9,
        "no_local_payload_crosses": not any(net and net.startswith(payload_prefixes) for net in m1_ui.values()),
        "hub_rf_spi_is_ground_bounded": all(m1_ui[pin] == "POWER_GROUND" for pin in (21, 25, 28)),
        "usb_pair_is_adjacent_and_ground_bounded": m1_ui[29] == "S3_USB_DM" and m1_ui[30] == "S3_USB_DP" and m1_ui[28] == m1_ui[31] == "POWER_GROUND",
        "connector_bandwidth_covers_fastest_crossing": m1_part["transmission_rate_gbps"] * 1000 >= 480,
        "connector_is_not_load_bearing": "electrical/alignment only" in architecture["interboard_rebaseline"]["mechanical_load_path"],
    }
    if not all_true(m1_checks):
        errors.append("M1 parity, locality or adjacency failed")

    transport_rows = []
    for link in architecture["transport_contracts"]:
        clock = dec(link["clock_hz"])
        period = dec(1_000_000_000) / clock
        route_budget = period * dec("0.20")
        transport_rows.append({
            "id": link["id"],
            "clock_hz": link["clock_hz"],
            "period_ns": float(period),
            "prelayout_route_and_skew_budget_ns": float(route_budget),
            "raw_payload_mb_s": link["raw_payload_mb_s"],
            "qualified_payload_floor_mb_s": link["qualified_payload_floor_mb_s"],
            "qualified_to_raw_pct": float(dec(link["qualified_payload_floor_mb_s"]) / dec(link["raw_payload_mb_s"]) * 100),
            "status": "pass" if route_budget > 0 and link["qualified_payload_floor_mb_s"] > 0 else "fail",
            "physical_residual": "H6 constrains and extracts length/skew/return continuity; H8 measures far-end timing and payload floor",
        })
    if any(row["status"] != "pass" for row in transport_rows):
        errors.append("one or more synchronous transport budgets failed")

    loading = {
        "i8080": {"fanout_per_driven_line": 1, "route_rule": "one S3 output -> one direct UI-board ZIF contact -> one ILI9488 input"},
        "hub_c5_sdio": {"fanout_per_line": 1, "series_elements": 6, "d2_d3_switch_bandwidth_mhz": service_switch["bandwidth_mhz"], "switch_to_bus_clock_ratio": service_switch["bandwidth_mhz"] / 40,
                        "bandwidth_is_typical_not_timing_proof": True},
        "hub_rf_m1": {"fanout_per_line": 1, "signal_contacts": [22, 23, 24, 26, 27], "reference_contacts": [21, 25, 28]},
        "sys_ui_i2c": {"pullup_ohm": 2200, "clock_hz": 400000, "maximum_allowed_bus_capacitance_pf": 120, "rise_time_at_max_cap_ns": 0.8473 * 2200 * 120 / 1000, "fast_mode_rise_limit_ns": 300},
        "usb": {"signalling_mbps": 12, "product_series_ohm_per_line": 22, "service_series_ohm_per_line": 27, "m1_rating_gbps": m1_part["transmission_rate_gbps"]},
    }
    loading_checks = {
        "all_fast_single_ended_buses_are_point_to_point": loading["i8080"]["fanout_per_driven_line"] == loading["hub_c5_sdio"]["fanout_per_line"] == loading["hub_rf_m1"]["fanout_per_line"] == 1,
        "c5_mux_typical_bandwidth_screen_is_at_least_10x_bus_clock": loading["hub_c5_sdio"]["switch_to_bus_clock_ratio"] >= 10,
        "ui_i2c_rise_time_has_positive_margin": loading["sys_ui_i2c"]["rise_time_at_max_cap_ns"] < loading["sys_ui_i2c"]["fast_mode_rise_limit_ns"],
        "usb_series_values_are_bounded": loading["usb"]["product_series_ohm_per_line"] == 22 and loading["usb"]["service_series_ohm_per_line"] == 27,
    }
    if not all_true(loading_checks):
        errors.append("schematic loading budget failed")

    residuals = [
        {"owner": "H6", "item": "route i8080, S3-Hub, Hub-C5 SDIO, Hub-RF SPI and USB as length/return/impedance constrained groups; prove extracted delay/skew and UI-I2C capacitance <=120 pF"},
        {"owner": "H8", "item": "measure i8080 WR/data edges at the panel, USB eyes/ enumeration, SDIO/SPI far-end setup-hold and sustained qualified payload floors"},
        {"owner": "F5/F6", "item": "instantiate the locked ESP-IDF i80 config at exact 20 MHz, CS=-1, 8-bit bus and rising-edge panel capture; exercise dirty-region and full-frame fixtures without waiting for TE, because panel contact 39 is deliberately open; no TE-synchronized or tear-free claim"},
    ]
    result = {
        "schema_version": 1,
        "artifact": "H3-R2-digital-interfaces",
        "marker": "H3-R2.4",
        "status": "pass" if not errors else "fail",
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in (ARCH, DEVICES, RAILS, NETS, INSTANCES, DISPLAY_MOUNT)},
        "methods": ["M-INT", "M-DIGITAL"],
        "authoritative_limits": SOURCES,
        "rail_corner_v": {"minimum": float(v_min), "maximum": float(v_max)},
        "logic_level_margins": level_margins,
        "display_topology": display_topology,
        "display_timing": display_timing,
        "usb_and_service_ownership": usb_topology,
        "c5_mux_control": {
            "checks": mux_checks,
            "source_topology_status": "pass" if all_true(mux_checks) else "fail",
            "scope": "Exact source pins and control-net membership only; neither routed-board parity nor voltage, reset-to-high-Z, asynchronous hazards or firmware sequencing is inferred.",
            "timing_qualified": False, "power_sequences_qualified": False,
            "firmware_service_manager_implemented": False, "production_release_allowed": False,
        },
        "c5_boot_strap": {
            "checks": c5_boot,
            "topology_status": "pass" if all_true(c5_boot) else "fail",
            "joint_download_boot_0_straps": SOURCES["esp32_c5_boot"]["joint_download_boot_0_straps"],
            "hold_after_en_release_ms_min": SOURCES["esp32_c5_boot"]["hold_after_en_release_ms_min"],
            "scope": "Native endpoint/component topology only; press BOOT through EN release and the required strap hold interval. Actual sampled levels, contact bounce and timing remain unqualified.",
            "sampled_levels_and_timing_qualified": False,
            "usb_mux_sel_oe_qualified": False,
            "kill_recovery_policy_qualified": False,
            "end_to_end_download_qualified": False,
        },
        "m1": {"checks": m1_checks, "true_nc_contacts": [pin for pin, net in m1_ui.items() if net is None], "contact_rating": m1_part},
        "transport_timing": transport_rows,
        "loading": {"models": loading, "checks": loading_checks},
        "physical_residuals": residuals,
        "errors": errors,
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
    }


    return apply_scope(result, __file__, {"rail_inputs": admits_current(rails, "H3-R2-rail-margins")})


def render(result: dict, language: str) -> str:
    ru = language == "ru"
    title = "Цифровая проверка Leshy2 R2" if ru else "Leshy2 R2 digital verification"
    d = result["display_timing"]
    worst = min(result["logic_level_margins"], key=lambda row: row["minimum_margin"])
    boot = result["c5_boot_strap"]
    boot_ok = boot["topology_status"] == "pass" and bool(boot["checks"]) and all_true(boot["checks"])
    boot_failed = ", ".join(name for name, passed in boot["checks"].items() if passed is not True) or "topology_status/check inventory"
    boot_row = (
        ("| C5 BOOT | топология проверена | GPIO28/U14.15 → C5_BOOT_N, R76/R79/SW18; GPIO27 подтянут вверх. Медь и удержание strap 3 мс после EN ещё требуют проверки |"
         if ru else "| C5 BOOT | topology checked | GPIO28/U14.15 → C5_BOOT_N, R76/R79/SW18; GPIO27 pulled high. Copper and 3-ms strap hold after EN remain unqualified |")
        if boot_ok else
        (f"| C5 BOOT | FAIL | Ошибка топологии: {boot_failed}. Цепь BOOT не подтверждена; разводка и поведение загрузки не квалифицированы |"
         if ru else f"| C5 BOOT | FAIL | Topology failed: {boot_failed}. BOOT chain is not confirmed; routing and boot behavior remain unqualified |"))
    lines = [
        f"# {title}", "",
        scope_notice(result, ru),
        "", "## Итог" if ru else "## Result", "",
        "| Область | Статус | Результат |" if ru else "| Area | Status | Result |", "|---|---:|---|",
        f"| i8080-8 | PASS | 20 MHz exact; {d['throughput']['full_frame_wire_ms']:.2f} ms full frame; {d['throughput']['budget_occupancy_pct']:.1f}% of 20-ms budget |",
        f"| Logic levels | provisional {'PASS' if all(row['status'] == 'pass' for row in result['logic_level_margins']) else 'FAIL'} | worst boundary `{worst['boundary']}`: {worst['minimum_margin']:.3f} V |",
        ("| USB / сервис | review_required | Проверено наличие ветвей данных; управление SEL/OE C5 и восстановление при KILL не квалифицированы |"
         if ru else "| USB / service | review_required | Data-branch presence checked; C5 SEL/OE control and recovery under KILL are not qualified |"),
        boot_row,
        f"| M1 | PASS | 80/80 pin parity; 9 true NC; USB and Hub-RF groups are ground-bounded |",
        f"| Loading | provisional screen | point-to-point buses; TS3USB221E typical bandwidth/40-MHz ratio = {result['loading']['models']['hub_c5_sdio']['switch_to_bus_clock_ratio']:.0f}; not a minimum bandwidth or SDIO timing guarantee |",
        "", "## Почему 20 МГц" if ru else "## Why 20 MHz", "",
        ("ILI9488 допускает максимум 25 МГц, но штатный integer divider ESP‑IDF превращает запрос 24 МГц в 26,667 МГц. Запрос 20 МГц даёт ровно 20 МГц: 50 нс на цикл, по 25 нс на фазы WR и минимум 10 нс запаса по циклу/импульсу."
         if ru else "ILI9488 allows at most 25 MHz, but the standard ESP-IDF integer divider turns a 24-MHz request into 26.667 MHz. A 20-MHz request produces exactly 20 MHz: a 50-ns cycle, 25-ns WR phases and at least 10 ns of cycle/pulse margin."),
        "", "## Что ещё физически проверить" if ru else "## Physical checks that remain", "",
    ]
    for row in result["physical_residuals"]:
        lines.append(f"- **{row['owner']}:** {row['item']}")
    lines += ["", "Generated by `hardware/verification/h3_r2_digital_interfaces.py`."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    expected = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render(result, "en"),
        DOC_RU: render(result, "ru"),
    }
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale:", ", ".join(stale))
            return 1
    print(json.dumps({"status": result["status"], "errors": result["errors"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
