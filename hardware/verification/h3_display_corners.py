#!/usr/bin/env python3
"""Verify H3.3.1 display supply, backlight and direct-QSPI paper corners."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF31-display.json"
DOC_EN = REPO / "docs/display-electrical-verification.md"
DOC_RU = REPO / "docs/display-electrical-verification.ru.md"

SOURCES = {
    "display_controller": "https://dl.espressif.com/AE/esp-iot-solution/ST77922_SPEC_V0.1.pdf",
    "donor_schematic": "https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf",
    "donor_specification": "https://www.lcdwiki.com/res/ES3C35P/3.5inch_IPS_ESP32-S3_Specification_V1.0.pdf",
    "main_converter": "https://www.ti.com/lit/ds/symlink/tps564252.pdf",
    "main_efuse": "https://www.ti.com/lit/ds/symlink/tps2597.pdf",
    "backlight_switch": "https://www.ti.com/lit/ds/symlink/tps2553.pdf",
    "precision_resistors": "https://www.vishay.com/docs/28758/tnpw_e3.pdf",
}


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_set(candidate: dict) -> set[tuple[str, str, str]]:
    return {(row["from"], row["to"], row["net"]) for row in candidate["fixed_routes"]}


def require_route(routes: set[tuple[str, str, str]], start: str, end: str, net: str) -> bool:
    return (start, end, net) in routes or (end, start, net) in routes


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    routes = route_set(candidate)
    pin_rows = {(row["instance"], row["contact"], row["net"]) for row in candidate["allocations"]}

    exact_parts = {
        "display": "qdtech_hmx035ctft_001",
        "display_panel_connector": "hirose_fh34srj_40s_0_5sh_99",
        "main_fb_top": "vishay_tnpw040243k7beed",
        "main_fb_bottom": "vishay_tnpw040210k0beed",
        "backlight_efuse": "ti_tps2553drvr_1",
        "backlight_efuse_ilim": "yageo_rc0402fr_07133kl",
        "backlight_series_resistor": "yageo_rc0402jr_070rl",
        "backlight_mosfet": "diodes_dmn2056u_7",
        "backlight_gate_series": "yageo_rc0402fr_07100rl",
    }
    exact_part_checks = {name: instances.get(name) == device for name, device in exact_parts.items()}

    topology_checks = {
        "common_vddi_source": require_route(routes, "abstract:3V3_MAIN", "display_connector.PIN_6", "LCD_VDDI_3V3"),
        "common_vdd_source": require_route(routes, "abstract:3V3_MAIN", "display_connector.PIN_7", "LCD_VDD_3V3"),
        "fixed_im1_high": require_route(routes, "abstract:3V3_MAIN", "display_connector.PIN_39", "LCD_IM1_HIGH"),
        "backlight_anode_protected": require_route(routes, "backlight_efuse.OUT", "display_connector.PIN_33", "LCD_LEDA_PROTECTED"),
        "joined_cathode_link": all(
            require_route(routes, f"display_connector.PIN_{pin}", "backlight_series_resistor.END_1", "LCD_LEDK")
            for pin in (34, 35, 36)
        ),
        "cathode_pwm_sink": require_route(routes, "backlight_series_resistor.END_2", "backlight_mosfet.D", "LCD_LEDK_LIMITED"),
        "reset_fail_low": require_route(routes, "display_connector.PIN_15", "display_reset_pulldown.END_1", "LCD_RST_N")
        and require_route(routes, "display_panel_connector.PIN_15", "display.RESET", "LCD_RST_N"),
        "touch_reset_fail_low": require_route(routes, "display_connector.PIN_4", "touch_reset_pulldown.END_1", "TOUCH_RST_N")
        and require_route(routes, "display_panel_connector.PIN_4", "display.TP_RESET", "TOUCH_RST_N"),
        "direct_qspi_d2": ("s3", "GPIO41", "LCD_QSPI_D2") in pin_rows
        and require_route(routes, "display_connector.PIN_17", "display_adapter_plug.PIN_17", "LCD_QSPI_D2")
        and require_route(routes, "display_panel_connector.PIN_17", "display.QSPI_D2", "LCD_QSPI_D2"),
        "direct_qspi_d3": ("s3", "GPIO42", "LCD_QSPI_D3") in pin_rows
        and require_route(routes, "display_connector.PIN_18", "display_adapter_plug.PIN_18", "LCD_QSPI_D3")
        and require_route(routes, "display_panel_connector.PIN_18", "display.QSPI_D3", "LCD_QSPI_D3"),
    }
    if not all(exact_part_checks.values()) or not all(topology_checks.values()):
        failed = [name for name, passed in {**exact_part_checks, **topology_checks}.items() if not passed]
        raise ValueError("H3.3.1 exact topology failed: " + ", ".join(failed))

    top = devices[instances["main_fb_top"]]["electrical_contract"]
    bottom = devices[instances["main_fb_bottom"]]["electrical_contract"]
    vref = d("0.600")
    vref_tol = d("0.015")
    rt = d(top["resistance_ohm"])
    rb = d(bottom["resistance_ohm"])
    rt_tol = d(top["tolerance_pct"]) / d(100)
    rb_tol = d(bottom["tolerance_pct"]) / d(100)
    nominal = vref * (d(1) + rt / rb)
    raw_average_min = vref * (d(1) - vref_tol) * (d(1) + rt * (d(1) - rt_tol) / (rb * (d(1) + rb_tol)))
    raw_average_max = vref * (d(1) + vref_tol) * (d(1) + rt * (d(1) + rt_tol) / (rb * (d(1) - rb_tol)))
    ripple_pp = d("0.020")
    raw_endpoint_min = raw_average_min - ripple_pp / d(2)
    raw_endpoint_max = raw_average_max + ripple_pp / d(2)
    protected_path_drop_budget = d("0.050")
    connector_min = raw_endpoint_min - protected_path_drop_budget
    connector_max = raw_endpoint_max
    vdd_min = d("2.65")
    vdd_max = d("3.30")
    vddi_min = d("1.65")
    vddi_max = d("3.30")

    qspi_hz = d("40000000")
    qspi_period_ns = d("1000000000") / qspi_hz
    qspi_half_ns = qspi_period_ns / d(2)
    datasheet_cycle_ns = d("16")
    datasheet_half_ns = d("7")
    cs_setup_hold_ns = d("25")
    datasheet_cs_ns = d("19")
    quantum_ms = d("1")
    quantum_bytes = qspi_hz * d(4) / d(8) * quantum_ms / d(1000)
    quantum_pixels_rgb565 = quantum_bytes / d(2)
    full_frame_bytes = d(320 * 480 * 2)
    full_frame_payload_ms = full_frame_bytes / (qspi_hz * d(4) / d(8)) * d(1000)

    backlight_reference_ma = d("120")
    backlight_ilim_min_ma = d("174")
    backlight_ilim_max_ma = d("234")
    backlight_headroom_ma = backlight_ilim_min_ma - backlight_reference_ma
    backlight_headroom_pct = backlight_headroom_ma / backlight_reference_ma * d(100)
    switch_ron_max_ohm_25c = d("0.085")
    switch_drop_mv = backlight_reference_ma / d(1000) * switch_ron_max_ohm_25c * d(1000)
    switch_loss_mw = (backlight_reference_ma / d(1000)) ** 2 * switch_ron_max_ohm_25c * d(1000)

    checks = {
        **{f"exact_{name}": passed for name, passed in exact_part_checks.items()},
        **topology_checks,
        "raw_rail_below_display_max": raw_endpoint_max <= vdd_max and raw_endpoint_max <= vddi_max,
        "protected_connector_above_display_min": connector_min >= vdd_min and connector_min >= vddi_min,
        "qspi_write_cycle_margin": qspi_period_ns >= datasheet_cycle_ns,
        "qspi_high_low_margin": qspi_half_ns >= datasheet_half_ns,
        "qspi_cs_margin": cs_setup_hold_ns >= datasheet_cs_ns,
        "backlight_fault_threshold_above_reference": backlight_ilim_min_ma > backlight_reference_ma,
        "method_has_worst_case_rule": any(row["id"] == "PF-02" for row in methods["pass_fail_rules"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.3.1 checks failed: " + ", ".join(failed))

    old_cost = sum(
        d(devices[key]["cost"]["unit_price_usd"])
        for key in ("yageo_rc0402fr_0745k3l", "yageo_rc0402fr_0710kl", "panasonic_erj_p08f10r0v")
    )
    new_cost = sum(d(devices[key]["cost"]["unit_price_usd"]) for key in exact_parts.values() if key in {
        "vishay_tnpw040243k7beed", "vishay_tnpw040210k0beed", "yageo_rc0402jr_070rl"
    })

    manifest = {
        "schema_version": 1,
        "stage": "H3.3.1",
        "status": "reviewed_display_supply_backlight_and_direct_qspi",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH)},
        "provenance": SOURCES,
        "exact_part_checks": exact_part_checks,
        "topology_checks": topology_checks,
        "supply_corner": {
            "feedback_vref_v": "0.600",
            "feedback_vref_tolerance_percent": "1.5",
            "feedback_top": {"mpn": devices[instances["main_fb_top"]]["mpn"], "ohm": str(top["resistance_ohm"]), "tolerance_percent": str(top["tolerance_pct"])},
            "feedback_bottom": {"mpn": devices[instances["main_fb_bottom"]]["mpn"], "ohm": str(bottom["resistance_ohm"]), "tolerance_percent": str(bottom["tolerance_pct"])},
            "nominal_v": q(nominal, "0.000001"),
            "raw_average_v": {"min": q(raw_average_min, "0.000001"), "max": q(raw_average_max, "0.000001")},
            "mandatory_ripple_vpp_max": q(ripple_pp, "0.000"),
            "raw_endpoint_v": {"min": q(raw_endpoint_min, "0.000001"), "max": q(raw_endpoint_max, "0.000001")},
            "protected_path_and_distribution_drop_budget_v": q(protected_path_drop_budget, "0.000"),
            "display_connector_v": {"min": q(connector_min, "0.000001"), "max": q(connector_max, "0.000001")},
            "st77922_recommended_vddi_v": {"min": q(vddi_min), "max": q(vddi_max)},
            "st77922_recommended_vdd_v": {"min": q(vdd_min), "max": q(vdd_max)},
            "upper_margin_mv": q((vdd_max - connector_max) * d(1000), "0.001"),
            "lower_vdd_margin_mv": q((connector_min - vdd_min) * d(1000), "0.001"),
            "vddi_not_above_vdd_rule": "both contacts are the same protected source and must remain a short matched branch with shared local decoupling",
        },
        "backlight_corner": {
            "donor_reference_current_ma": q(backlight_reference_ma),
            "power_path_reference_correction": "QDtech R31 is 0R in the joined LEDK path; R33=10R is the donor Q4 gate resistor",
            "selected_ledk_link": devices[instances["backlight_series_resistor"]]["mpn"],
            "selected_gate_resistor_ohm": 100,
            "tps2553_latched_current_limit_ma": {"min": q(backlight_ilim_min_ma), "max": q(backlight_ilim_max_ma)},
            "minimum_fault_threshold_headroom_ma": q(backlight_headroom_ma),
            "minimum_fault_threshold_headroom_percent": q(backlight_headroom_pct),
            "switch_drop_at_120ma_mv_25c_max_ron": q(switch_drop_mv),
            "switch_loss_at_120ma_mw_25c_max_ron": q(switch_loss_mw),
            "interpretation": "TPS2553 bounds and latches a fault; it is not an LED-current regulator. Actual panel current/brightness remains a specimen HIL measurement.",
        },
        "qspi_corner": {
            "selected_initial_write_clock_hz": int(qspi_hz),
            "datasheet_theoretical_write_clock_hz_max": 62500000,
            "period_ns": q(qspi_period_ns),
            "period_margin_over_16ns_min_ns": q(qspi_period_ns - datasheet_cycle_ns),
            "high_low_ns": q(qspi_half_ns),
            "high_low_margin_over_7ns_min_ns": q(qspi_half_ns - datasheet_half_ns),
            "required_cs_setup_and_hold_ns": q(cs_setup_hold_ns),
            "cs_margin_over_19ns_min_ns": q(cs_setup_hold_ns - datasheet_cs_ns),
            "maximum_nonpreemptible_quantum_ms": q(quantum_ms),
            "payload_per_quantum_bytes": int(quantum_bytes),
            "rgb565_pixels_per_quantum": int(quantum_pixels_rgb565),
            "full_frame_payload_only_ms": q(full_frame_payload_ms),
            "touch_i2c_hz_max": 400000,
            "reset_pulse_us_min": 10,
            "display_reset_cancel_ms": 120,
            "touch_reset_cancel_ms": 100,
            "rise_fall_time_ns_max": 15,
            "rule": "start at 40 MHz, enforce at least 25 ns CS setup/hold and <=1-ms dirty/tile bursts; any faster clock remains HIL-qualified only",
        },
        "checks": checks,
        "corrections": [
            {
                "id": "H3.3.1-F01",
                "finding": "the former 3.318-V nominal divider could reach about 3.424 V before ripple and exceeded the ST77922 3.3-V recommended maximum",
                "correction": "replace it with exact 43.7-kOhm/10-kOhm 0.1% feedback and require no more than 20 mVpp ripple",
                "functional_effect": "the display connector envelope is 3.109-to-3.286 V after the explicit protected-path drop budget",
            },
            {
                "id": "H3.3.1-F02",
                "finding": "the donor 10-Ohm gate resistor was previously misread as a 10-Ohm series LEDK power resistor, which would drop about 1.2 V at 120 mA",
                "correction": "use the donor-equivalent 0-Ohm R31 LEDK link and retain the Leshy2 100-Ohm MOSFET gate-damping resistor",
                "functional_effect": "the artificial backlight voltage loss is removed while the independent latch-off fault bound remains",
            },
        ],
        "cost_delta_usd_at_100": {
            "old_three_instances": q(old_cost, "0.0000"),
            "new_three_instances": q(new_cost, "0.0000"),
            "delta_per_board": q(new_cost - old_cost, "0.0000"),
            "scope": "two precision main-feedback resistors plus the corrected LEDK link; distribution, tax and assembly excluded",
        },
        "residual_physical_only": [
            "measure protected-rail ripple and connector voltage at every accepted load and temperature corner",
            "confirm HMX035CTFT-001 tail, ST77922 identity, VDD/VDDI ramp equality and reset/readback on received specimens",
            "measure QSPI edges, CS-high high-Z/contention and shared-microSD throughput before raising the 40-MHz initial cap",
            "measure actual panel backlight current, brightness, PWM EMI, temperature and TPS2553 latch recovery",
        ],
        "review_summary": {"checks": len(checks), "failed_checks": len(failed), "corrected_findings": 2, "unresolved_findings": 0, "status": "reviewed"},
        "next": {"stage": "H3.3.2", "action": "verify codec, microphone, headset and speaker gain/noise/power corners"},
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    s = manifest["supply_corner"]
    b = manifest["backlight_corner"]
    qspi = manifest["qspi_corner"]
    cost = manifest["cost_delta_usd_at_100"]
    if russian:
        title = "# Электрическая проверка дисплея"
        nav = "[English](display-electrical-verification.md) · [На главную](../README.ru.md) · [Принципиальные схемы](schematics.ru.md) · [Виртуальная проверка](virtual-verification.ru.md)"
        intro = "H3.3.1 проверяет одну полную цепочку: питание ST77922 → силовой тракт подсветки → direct-QSPI/touch timing. Это расчётное ревью серийных деталей и реальных контактов; измерения сырого HMX035CTFT-001 остаются HIL."
        supply_h = "## Питание"
        supply = (
            f"- Серийные `{s['feedback_top']['mpn']}` / `{s['feedback_bottom']['mpn']}` задают `{s['nominal_v']} В` nominal.\n"
            f"- С учётом ±1,5% VREF, ±0,1% резисторов и обязательных `{s['mandatory_ripple_vpp_max']} Вpp` raw endpoint равен `{s['raw_endpoint_v']['min']}…{s['raw_endpoint_v']['max']} В`.\n"
            f"- После отдельного `{s['protected_path_and_distribution_drop_budget_v']} В` drop budget на разъёме остаётся `{s['display_connector_v']['min']}…{s['display_connector_v']['max']} В`: запас до VDD min `{s['lower_vdd_margin_mv']} мВ`, до общего 3,3-В max `{s['upper_margin_mv']} мВ`."
        )
        backlight_h = "## Подсветка"
        backlight = (
            "Донорская схема была прочитана неверно: `R31=0R` стоит в общем LEDK-тракте, а `R33=10R` — в затворе Q4. "
            f"Теперь силовой путь использует `{b['selected_ledk_link']}`. TPS2553 не регулирует яркость: он аппаратно защёлкивает fault в диапазоне `{b['tps2553_latched_current_limit_ma']['min']}…{b['tps2553_latched_current_limit_ma']['max']} мА`, оставляя минимум `{b['minimum_fault_threshold_headroom_percent']}%` над 120-мА донорским режимом. Реальный ток и яркость измеряются на образце."
        )
        qspi_h = "## Direct-QSPI и touch"
        qspi_text = (
            f"Начальный предел — `{qspi['selected_initial_write_clock_hz'] // 1000000} МГц`: период `{qspi['period_ns']} нс` против datasheet minimum 16 нс; high/low `{qspi['high_low_ns']} нс` против 7 нс. "
            f"CS получает не менее `{qspi['required_cs_setup_and_hold_ns']} нс` setup/hold. Один непрерываемый 1-мс квант переносит до `{qspi['payload_per_quantum_bytes']}` байт / `{qspi['rgb565_pixels_per_quantum']}` RGB565-пикселей; полный кадр занимает теоретически `{qspi['full_frame_payload_only_ms']} мс`, поэтому меню и водопад работают грязными областями, а не full-frame redraw. Touch остаётся ≤400 кГц."
        )
        corrected_h = "## Исправлено ревью"
        corrected = "1. Убран потенциальный выход ST77922 за 3,3 В.\n2. Убран ошибочный 10-омный силовой резистор, отнимавший бы около 1,2 В у подсветки."
        remaining_h = "## Что остаётся физическим"
        remaining = "\n".join(
            (
                "- измерить ripple защищённой шины и напряжение на разъёме во всех принятых углах нагрузки и температуры",
                "- на полученных HMX035CTFT-001 подтвердить хвост, ST77922, одинаковый ramp VDD/VDDI, reset и readback",
                "- до повышения начального предела 40 МГц измерить QSPI edges, CS-high high-Z/contention и throughput общей microSD",
                "- измерить реальный ток/яркость подсветки, PWM EMI, температуру и восстановление защёлки TPS2553",
            )
        )
        marker = f"Три замены добавляют `{cost['delta_per_board']} USD` на устройство при количестве 100. **H3.3.1 проверено; текущий точный маркер — `H3.5.1`.**"
        evidence = "[Машинный пакет H3-VRF31](../hardware/verification/generated/H3-VRF31-display.json)."
    else:
        title = "# Display electrical verification"
        nav = "[Русский](display-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)"
        intro = "H3.3.1 checks one complete chain: ST77922 supply → backlight power path → direct-QSPI/touch timing. This is a paper review of serial parts and real contacts; raw HMX035CTFT-001 specimen measurements remain HIL."
        supply_h = "## Supply"
        supply = (
            f"- Serial `{s['feedback_top']['mpn']}` / `{s['feedback_bottom']['mpn']}` set `{s['nominal_v']} V` nominal.\n"
            f"- With ±1.5% VREF, ±0.1% resistors and mandatory `{s['mandatory_ripple_vpp_max']} Vpp`, the raw endpoint is `{s['raw_endpoint_v']['min']}…{s['raw_endpoint_v']['max']} V`.\n"
            f"- After the separate `{s['protected_path_and_distribution_drop_budget_v']} V` path budget the connector retains `{s['display_connector_v']['min']}…{s['display_connector_v']['max']} V`: `{s['lower_vdd_margin_mv']} mV` above VDD minimum and `{s['upper_margin_mv']} mV` below the common 3.3-V maximum."
        )
        backlight_h = "## Backlight"
        backlight = (
            "The donor schematic had been misread: `R31=0R` is in the common LEDK path while `R33=10R` is in Q4's gate. "
            f"The power path now uses `{b['selected_ledk_link']}`. TPS2553 does not regulate brightness: it latches a fault at `{b['tps2553_latched_current_limit_ma']['min']}…{b['tps2553_latched_current_limit_ma']['max']} mA`, retaining at least `{b['minimum_fault_threshold_headroom_percent']}%` over the donor's 120-mA mode. Actual current and brightness remain specimen measurements."
        )
        qspi_h = "## Direct QSPI and touch"
        qspi_text = (
            f"The initial cap is `{qspi['selected_initial_write_clock_hz'] // 1000000} MHz`: `{qspi['period_ns']} ns` period versus 16 ns minimum; `{qspi['high_low_ns']} ns` high/low versus 7 ns. "
            f"CS gets at least `{qspi['required_cs_setup_and_hold_ns']} ns` setup/hold. One non-preemptible 1-ms quantum carries up to `{qspi['payload_per_quantum_bytes']}` bytes / `{qspi['rgb565_pixels_per_quantum']}` RGB565 pixels; a full frame is `{qspi['full_frame_payload_only_ms']} ms` payload-only, so menus and waterfall use dirty regions rather than full-frame redraw. Touch remains ≤400 kHz."
        )
        corrected_h = "## Corrected by review"
        corrected = "1. Removed the possible ST77922 excursion above 3.3 V.\n2. Removed the mistaken 10-ohm power resistor that would have taken about 1.2 V from the backlight."
        remaining_h = "## What remains physical"
        remaining = "\n".join(f"- {row}" for row in manifest["residual_physical_only"])
        marker = f"The three replacements add `{cost['delta_per_board']} USD` per unit at quantity 100. **H3.3.1 is reviewed; the exact current marker is `H3.5.1`.**"
        evidence = "[Machine H3-VRF31 package](../hardware/verification/generated/H3-VRF31-display.json)."
    return "\n\n".join((title, nav, intro, supply_h, supply, backlight_h, backlight, qspi_h, qspi_text, corrected_h, corrected, remaining_h, remaining, marker, evidence)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H3.3.1 reviewed; {manifest['review_summary']['checks']} checks, 0 unresolved findings, next H3.3.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
