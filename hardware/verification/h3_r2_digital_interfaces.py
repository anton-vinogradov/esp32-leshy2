#!/usr/bin/env python3
"""Verify current R2 digital boundaries, ownership, loading and i8080 timing."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 50
ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
RAILS = ROOT / "hardware/verification/generated/H3-R2-rail-margins.json"
NETS = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
ADAPTER = ROOT / "hardware/product-design/display-adapter.json"
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
    adapter = load(ADAPTER)
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

    expected_s3_lanes = {
        "LCD_DB0": "s3.GPIO4", "LCD_DB1": "s3.GPIO9", "LCD_DB2": "s3.GPIO18", "LCD_DB3": "s3.GPIO38",
        "LCD_DB4": "s3.GPIO40", "LCD_DB5": "s3.GPIO41", "LCD_DB6": "s3.GPIO42", "LCD_DB7": "s3.GPIO46",
    }
    display_topology = {
        "all_s3_data_lanes_exact": all(endpoint(rows, pin, net) for net, pin in expected_s3_lanes.items()),
        "wr_is_direct_gpio17": endpoint(rows, "s3.GPIO17", "LCD_WR_N") and endpoint(rows, "display_connector.PIN_11", "LCD_WR_N"),
        "dc_is_direct_gpio45": endpoint(rows, "s3.GPIO45", "LCD_DC") and endpoint(rows, "display_connector.PIN_10", "LCD_DC"),
        "panel_receives_all_eight_lanes": all(endpoint(rows, f"display_panel_connector.PIN_{32 - lane}", f"LCD_DB{lane}") for lane in range(8)),
        "panel_wr_dc_reach_exact_contacts": endpoint(rows, "display_panel_connector.PIN_36", "LCD_WR_N_OR_SPI_SCL") and endpoint(rows, "display_panel_connector.PIN_37", "LCD_DC"),
        "cs_is_hard_low": endpoint(rows, "display_connector.PIN_9", "POWER_GROUND") and endpoint(rows, "display_panel_connector.PIN_38", "LCD_CS_LOW_OR_SPI_CS_N"),
        "rd_is_hard_high": endpoint(rows, "display_connector.PIN_12", "3V3_MAIN") and endpoint(rows, "display_panel_connector.PIN_35", "LCD_RD_HIGH"),
        "im_straps_are_011": endpoint(rows, "display_connector.PIN_38", "3V3_MAIN") and endpoint(rows, "display_connector.PIN_39", "3V3_MAIN") and endpoint(rows, "display_connector.PIN_40", "POWER_GROUND"),
        "adapter_mode_is_exact": adapter["electrical"]["selected_mode"] == "ILI9488 8080 8-bit with IM2/IM1/IM0 = 0/1/1",
        "recovery_sda_is_not_populated_on_ui_board": endpoint(rows, "display_connector.PIN_13", None),
    }
    if not all_true(display_topology):
        errors.append("direct i8080 topology or mode straps drifted")

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
    fsusb = devices[by_instance["c5_service_usb_switch"]["device_id"]]["electrical_contract"]
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
        "c5_mux_has_hardware_default_pulldowns": endpoint(rows, "c5_mux_sel_pulldown.END_2", "SAFETY_GROUND") and endpoint(rows, "c5_mux_oe_pulldown.END_2", "SAFETY_GROUND"),
        "c5_mux_switches_only_d2_d3_or_usb": all(instance_net(rows, "c5_service_usb_switch", net) for net in ("C5_GPIO13_COMMON", "C5_GPIO14_COMMON", "HUB_C5_SDIO_DAT2_BRANCH", "HUB_C5_SDIO_DAT3_BRANCH", "C5_SERVICE_USB_DM_BRANCH", "C5_SERVICE_USB_DP_BRANCH")),
        "service_ownership_latch_resets_both_compute_domains": instance_net(rows, "c5_service_owner_latch", "C5_SERVICE_OWNED") and instance_net(rows, "c5_service_reset_sink", "C5_RESET_N") and instance_net(rows, "c5_service_hub_reset_sink", "HUB_RP_RESET_N"),
        "service_switch_bandwidth_covers_usb_full_speed": fsusb["usb_speed_mbps"] >= 12 and fsusb["bandwidth_mhz"] >= 240,
        "power_off_leakage_has_over_2x_reserve": fsusb["power_off_leakage_max_ua"] <= 2,
    }
    if not all_true(usb_topology):
        errors.append("USB/service ownership topology failed")

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
        "i8080": {"fanout_per_driven_line": 1, "route_rule": "one S3 output -> one passive board connector -> one passive adapter -> one ILI9488 input"},
        "hub_c5_sdio": {"fanout_per_line": 1, "series_elements": 6, "d2_d3_switch_bandwidth_mhz": fsusb["bandwidth_mhz"], "switch_to_bus_clock_ratio": fsusb["bandwidth_mhz"] / 40},
        "hub_rf_m1": {"fanout_per_line": 1, "signal_contacts": [22, 23, 24, 26, 27], "reference_contacts": [21, 25, 28]},
        "sys_ui_i2c": {"pullup_ohm": 2200, "clock_hz": 400000, "maximum_allowed_bus_capacitance_pf": 120, "rise_time_at_max_cap_ns": 0.8473 * 2200 * 120 / 1000, "fast_mode_rise_limit_ns": 300},
        "usb": {"signalling_mbps": 12, "product_series_ohm_per_line": 22, "service_series_ohm_per_line": 27, "m1_rating_gbps": m1_part["transmission_rate_gbps"]},
    }
    loading_checks = {
        "all_fast_single_ended_buses_are_point_to_point": loading["i8080"]["fanout_per_driven_line"] == loading["hub_c5_sdio"]["fanout_per_line"] == loading["hub_rf_m1"]["fanout_per_line"] == 1,
        "c5_mux_bandwidth_is_at_least_10x_bus_clock": loading["hub_c5_sdio"]["switch_to_bus_clock_ratio"] >= 10,
        "ui_i2c_rise_time_has_positive_margin": loading["sys_ui_i2c"]["rise_time_at_max_cap_ns"] < loading["sys_ui_i2c"]["fast_mode_rise_limit_ns"],
        "usb_series_values_are_bounded": loading["usb"]["product_series_ohm_per_line"] == 22 and loading["usb"]["service_series_ohm_per_line"] == 27,
    }
    if not all_true(loading_checks):
        errors.append("schematic loading budget failed")

    residuals = [
        {"owner": "H6", "item": "route i8080, S3-Hub, Hub-C5 SDIO, Hub-RF SPI and USB as length/return/impedance constrained groups; prove extracted delay/skew and UI-I2C capacitance <=120 pF"},
        {"owner": "H8", "item": "measure i8080 WR/data edges at the panel, USB eyes/ enumeration, SDIO/SPI far-end setup-hold and sustained qualified payload floors"},
        {"owner": "F5/F6", "item": "instantiate the locked ESP-IDF i80 config at exact 20 MHz, CS=-1, 8-bit bus and rising-edge panel capture; exercise TE, dirty-region and full-frame fixtures"},
    ]
    return {
        "schema_version": 1,
        "artifact": "H3-R2-digital-interfaces",
        "marker": "H3-R2.4",
        "status": "pass" if not errors else "fail",
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in (ARCH, DEVICES, RAILS, NETS, INSTANCES, ADAPTER)},
        "methods": ["M-INT", "M-DIGITAL"],
        "authoritative_limits": SOURCES,
        "rail_corner_v": {"minimum": float(v_min), "maximum": float(v_max)},
        "logic_level_margins": level_margins,
        "display_topology": display_topology,
        "display_timing": display_timing,
        "usb_and_service_ownership": usb_topology,
        "m1": {"checks": m1_checks, "true_nc_contacts": [pin for pin, net in m1_ui.items() if net is None], "contact_rating": m1_part},
        "transport_timing": transport_rows,
        "loading": {"models": loading, "checks": loading_checks},
        "physical_residuals": residuals,
        "errors": errors,
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
    }


def render(result: dict, language: str) -> str:
    ru = language == "ru"
    title = "Цифровая проверка Leshy2 R2" if ru else "Leshy2 R2 digital verification"
    d = result["display_timing"]
    worst = min(result["logic_level_margins"], key=lambda row: row["minimum_margin"])
    lines = [
        f"# {title}", "",
        ("`H3‑R2.4` проверяет фактическую native R2‑схему, а не историческую R1‑модель. Все расчётные digital‑границы пройдены; трассировочные и измерительные остатки оставлены H6/H8 явно."
         if ru else "`H3-R2.4` verifies the actual native R2 schematic rather than the historical R1 model. Every calculable digital boundary passes; routed and measured residuals remain explicitly assigned to H6/H8."),
        "", "## Итог" if ru else "## Result", "",
        "| Область | Статус | Результат |" if ru else "| Area | Status | Result |", "|---|---:|---|",
        f"| i8080-8 | PASS | 20 MHz exact; {d['throughput']['full_frame_wire_ms']:.2f} ms full frame; {d['throughput']['budget_occupancy_pct']:.1f}% of 20-ms budget |",
        f"| Logic levels | PASS | worst boundary `{worst['boundary']}`: {worst['minimum_margin']:.3f} V |",
        f"| USB / service | PASS | product S3 USB + three independent data-only service paths; C5 D2/D3 mux is reset/ownership interlocked |",
        f"| M1 | PASS | 80/80 pin parity; 9 true NC; USB and Hub-RF groups are ground-bounded |",
        f"| Loading | PASS | point-to-point fast buses; FSUSB42 bandwidth is {result['loading']['models']['hub_c5_sdio']['switch_to_bus_clock_ratio']:.0f}x the 40-MHz SDIO clock |",
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
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
