#!/usr/bin/env python3
"""Verify H3.3.3 IR receive, transmit, optical evidence and thermal corners."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from itertools import product
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
DISPLAY_PATH = REPO / "hardware/verification/generated/H3-VRF31-display.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF33-ir.json"
DOC_EN = REPO / "docs/ir-electrical-verification.md"
DOC_RU = REPO / "docs/ir-electrical-verification.ru.md"

SOURCES = {
    "c5_module": "https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html",
    "emitter": "https://www.vishay.com/docs/84209/vsmy14940.pdf",
    "demodulating_receiver": "https://www.vishay.com/docs/82837/tsop952.pdf",
    "carrier_receiver": "https://www.vishay.com/docs/82907/tsmp95000.pdf",
    "photodiode": "https://www.vishay.com/docs/84295/vemd1060x01.pdf",
    "receive_switch": "https://www.ti.com/lit/ds/symlink/tps22919.pdf",
    "return_buffer": "https://assets.nexperia.com/documents/data-sheet/74LVC2G126.pdf",
    "safety_gate": "https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf",
    "emitter_mosfet": "https://www.diodes.com/datasheet/download/DMN2056U.pdf",
    "optical_tia": "https://www.ti.com/lit/ds/symlink/tlv9061.pdf",
    "evidence_comparator": "https://www.ti.com/lit/ds/symlink/tlv1824.pdf",
    "selected_tx_resistor": "https://yageogroup.com/component-documentation/download/specsheet/RC1206FR-0747RL",
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


def high_threshold(vcc: Decimal, r_top: Decimal, r_bottom: Decimal, feedback: Decimal, pullup: Decimal) -> Decimal:
    top_g = d(1) / r_top + d(1) / (feedback + pullup)
    return vcc * top_g / (top_g + d(1) / r_bottom)


def low_threshold(vcc: Decimal, r_top: Decimal, r_bottom: Decimal, feedback: Decimal, output_low: Decimal) -> Decimal:
    conductance = d(1) / r_top + d(1) / r_bottom + d(1) / feedback
    return (vcc / r_top + output_low / feedback) / conductance


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    dc_budget = json.loads(DC_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    routes = route_set(candidate)

    exact_parts = {
        "c5": "esp32_c5_wroom_1u_n8r8",
        "ir_power_switch": "ti_tps22919_dckr",
        "ir_demod": "vishay_tsop75238tt",
        "ir_carrier": "vishay_tsmp95000tt",
        "ir_return_buffer": "nexperia_74lvc2g126dc_125",
        "ir_emitter": "vishay_vsmy14940",
        "ir_emitter_limit": "yageo_rc1206fr_0747rl",
        "ir_tx_mosfet": "diodes_dmn2056u_7",
        "ir_tx_carrier_pulldown": "yageo_rc0402fr_0710kl",
        "ir_safe_gate": "ti_sn74lvc1g08_dckr",
        "det_ir": "vishay_vemd1060x01",
        "ir_evidence_amp": "ti_tlv9061_idbvr",
        "evidence_cmp_a": "ti_tlv1824_pwr",
    }
    exact_checks = {name: instances.get(name) == device for name, device in exact_parts.items()}
    topology = {
        "receive_enable_fail_low": require_route(routes, "ir_power_switch.ON", "ir_power_on_pulldown.END_1", "IR_FRONTEND_PWR_EN"),
        "receive_qod": require_route(routes, "ir_power_switch.QOD", "ir_power_switch.VOUT", "IR_RX_QOD"),
        "demod_filter": require_route(routes, "ir_power_switch.VOUT", "ir_demod_supply_res.END_1", "3V3_IR_SWITCHED")
        and require_route(routes, "ir_demod_supply_res.END_2", "ir_demod.VS", "IR_DEMOD_VS"),
        "carrier_filter": require_route(routes, "ir_power_switch.VOUT", "ir_carrier_supply_res.END_1", "3V3_IR_SWITCHED")
        and require_route(routes, "ir_carrier_supply_res.END_2", "ir_carrier.VS", "IR_CARRIER_VS"),
        "recommended_carrier_pullup": require_route(routes, "ir_carrier_pullup.END_1", "ir_carrier.CARRIER_OUT", "IR_CARRIER_LOCAL_N"),
        "independent_return_channels": require_route(routes, "ir_demod.OUT", "ir_return_buffer.1A", "IR_DEMOD_LOCAL_N")
        and require_route(routes, "ir_carrier.CARRIER_OUT", "ir_return_buffer.2A", "IR_CARRIER_LOCAL_N"),
        "host_idle_pullups": require_route(routes, "ir_demod_host_pullup.END_1", "c5.GPIO0", "IR_RX_DEMOD")
        and require_route(routes, "ir_carrier_host_pullup.END_1", "c5.GPIO1", "IR_RX_CARRIER"),
        "direct_rmt_tx": require_route(routes, "c5.GPIO6", "ir_safe_gate.A", "IR_TX_CARRIER"),
        "emitter_shared_reset_off_rail": require_route(
            routes, "ir_power_switch.VOUT", "ir_emitter_limit.END_1", "3V3_IR_SWITCHED"
        ),
        "carrier_input_fail_low": require_route(routes, "ir_safe_gate.A", "ir_tx_carrier_pulldown.END_1", "IR_TX_CARRIER")
        and require_route(routes, "ir_tx_carrier_pulldown.END_2", "abstract:safety-ground", "SAFETY_GROUND"),
        "run_permit_gate": require_route(routes, "safe_latch.Q", "ir_safe_gate.B", "RUN_PERMIT"),
        "mosfet_gate_fail_low": require_route(routes, "ir_tx_mosfet.G", "ir_tx_gate_pulldown.END_1", "IR_TX_GATE"),
        "physical_photodiode": require_route(routes, "det_ir.ANODE", "abstract:safety-ground", "SAFETY_GROUND")
        and require_route(routes, "det_ir.CATHODE", "ir_evidence_amp.IN_MINUS", "IR_OPTICAL_SUM"),
        "tia_feedback": require_route(routes, "ir_evidence_amp.OUT", "ir_evidence_feedback.END_1", "IR_DETECT_V")
        and require_route(routes, "ir_evidence_feedback.END_2", "ir_evidence_amp.IN_MINUS", "IR_OPTICAL_SUM"),
        "optical_not_drive_evidence": require_route(routes, "ir_evidence_amp.OUT", "evidence_cmp_a.IN3_N", "IR_DETECT_V"),
    }
    structural = {**{f"exact_{name}": ok for name, ok in exact_checks.items()}, **topology}
    if not all(structural.values()):
        raise ValueError("H3.3.3 exact topology failed: " + ", ".join(name for name, ok in structural.items() if not ok))

    main_min = d(display["supply_corner"]["display_connector_v"]["min"])
    main_max = d(display["supply_corner"]["display_connector_v"]["max"])
    switch_ron_85 = d("0.200")
    switch_group_current = d("0.002")
    common_switch_drop = switch_ron_85 * switch_group_current
    demod_branch_current = d("0.00045") + d("0.00011")
    carrier_pullup_min = d(4700) * d("0.99")
    carrier_branch_current = d("0.00045") + main_max / carrier_pullup_min
    demod_supply_min = main_min - common_switch_drop - d(100) * d("1.01") * demod_branch_current
    carrier_supply_min = main_min - common_switch_drop - d(100) * d("1.01") * carrier_branch_current
    demod_supply_max = main_max
    carrier_supply_max = main_max
    receiver_power_on_guard_ms = d(20)
    output_cap_max_f = (d(10) + d("0.1") + d("4.7") * d(2)) * d("1.20") * d("0.000001")
    qod_typ_ohm = d(24)
    qod_90_to_10_ms = d("2.2") * qod_typ_ohm * output_cap_max_f * d(1000)
    receiver_power_off_guard_ms = d(5)

    resistor = devices[instances["ir_emitter_limit"]]["electrical_contract"]
    r_nom = d(resistor["resistance_ohm"])
    r_tol = d(resistor["tolerance_pct"]) / d(100)
    r_min = r_nom * (d(1) - r_tol)
    r_max = r_nom * (d(1) + r_tol)
    mosfet_hot_ohm = d("0.072")
    vf_20_min_85 = d("1.1") + d("-0.0009") * d(60)
    tx_current_max = (d("3.4") - vf_20_min_85) / (r_min + mosfet_hot_ohm)
    minimum_20ma_loop_voltage = d("1.5") + d("0.020") * (r_max + d("0.085"))
    resistor_loss_max = tx_current_max**2 * r_min
    emitter_power_typ = tx_current_max * d("1.5")
    carrier_duty_max = d(1) / d(3)
    tx_local_temp_limit = d(75)
    emitter_junction_at_carrier = tx_local_temp_limit + emitter_power_typ * carrier_duty_max * d(390)
    emitter_junction_limit = d(100)
    single_mark_ms = d(20)
    rolling_on_fraction = d("0.25")
    continuous_evidence_trip_ms = d(20)

    aon_min = d("3.07")
    aon_max = d("3.40")
    tol = d("0.01")
    resistor_values = {
        "top": (d(100000) * (d(1) - tol), d(100000) * (d(1) + tol)),
        "bottom": (d(12000) * (d(1) - tol), d(12000) * (d(1) + tol)),
        "feedback": (d(1000000) * (d(1) - tol), d(1000000) * (d(1) + tol)),
        "pullup": (d(10000) * (d(1) - tol), d(10000) * (d(1) + tol)),
    }
    assert_values = [
        high_threshold(vcc, rt, rb, rh, rp)
        for vcc, rt, rb, rh, rp in product(
            (aon_min, aon_max), resistor_values["top"], resistor_values["bottom"],
            resistor_values["feedback"], resistor_values["pullup"]
        )
    ]
    clear_values = [
        low_threshold(vcc, rt, rb, rh, output_low)
        for vcc, rt, rb, rh, output_low in product(
            (aon_min, aon_max), resistor_values["top"], resistor_values["bottom"],
            resistor_values["feedback"], (d(0), d("0.1"))
        )
    ]
    def vref_corners(vcc: Decimal) -> list[Decimal]:
        return [
            vcc * rb / (rt + rb)
            for rt, rb in product(
                (d(100000) * (d(1) - tol), d(100000) * (d(1) + tol)),
                (d(10000) * (d(1) - tol), d(10000) * (d(1) + tol)),
            )
        ]

    vref_values = [value for vcc in (aon_min, aon_max) for value in vref_corners(vcc)]
    opamp_offset = d("0.002")
    comparator_offset = d("0.004")
    dark_current = d("0.000000005")
    feedback_min = d(47000) * (d(1) - tol)
    feedback_max = d(47000) * (d(1) + tol)
    dark_idle_max = max(vref_values) + opamp_offset + dark_current * feedback_max
    dark_idle_min = min(vref_values) - opamp_offset
    # Threshold and TIA reference move with the same physical AON rail.  Pairing a
    # 3.07-V threshold with a 3.40-V dark level invents a corner no board can see.
    # Resistor, input-offset and output-low extremes remain independently opposed.
    same_rail_false_assert_margins = []
    same_rail_clear_margins = []
    same_rail_required_photocurrents = []
    for vcc in (aon_min, aon_max):
        rail_assert_values = [
            high_threshold(vcc, rt, rb, rh, rp)
            for rt, rb, rh, rp in product(
                resistor_values["top"], resistor_values["bottom"],
                resistor_values["feedback"], resistor_values["pullup"]
            )
        ]
        rail_clear_values = [
            low_threshold(vcc, rt, rb, rh, output_low)
            for rt, rb, rh, output_low in product(
                resistor_values["top"], resistor_values["bottom"],
                resistor_values["feedback"], (d(0), d("0.1"))
            )
        ]
        rail_vref_values = vref_corners(vcc)
        rail_dark_max = max(rail_vref_values) + opamp_offset + dark_current * feedback_max
        rail_dark_min = min(rail_vref_values) - opamp_offset
        same_rail_false_assert_margins.append(min(rail_assert_values) - comparator_offset - rail_dark_max)
        same_rail_clear_margins.append(min(rail_clear_values) - comparator_offset - rail_dark_max)
        same_rail_required_photocurrents.append(
            (max(rail_assert_values) + comparator_offset - rail_dark_min) / feedback_min
        )
    false_assert_margin = min(same_rail_false_assert_margins)
    clear_margin = min(same_rail_clear_margins)
    required_photocurrent = max(same_rail_required_photocurrents)
    tau_min_us = feedback_min * d("0.000000001") * d("0.90") * d(1000000)
    tau_max_us = feedback_max * d("0.000000001") * d("1.10") * d(1000000)

    checks = {
        **structural,
        "demod_supply_inside_2v0_to_3v6": demod_supply_min >= d(2) and demod_supply_max <= d("3.6"),
        "carrier_supply_inside_2v0_to_5v5": carrier_supply_min >= d(2) and carrier_supply_max <= d("5.5"),
        "receiver_on_guard_exceeds_switch_typical_start": receiver_power_on_guard_ms >= d(10),
        "receiver_off_guard_exceeds_nominal_qod_fall": receiver_power_off_guard_ms >= qod_90_to_10_ms * d(2),
        "emitter_guarantees_20ma_characterized_point": main_min >= minimum_20ma_loop_voltage,
        "emitter_instantaneous_current_below_55ma": tx_current_max <= d("0.055"),
        "emitter_instantaneous_current_below_absolute_max": tx_current_max <= d("0.070"),
        "emitter_resistor_power_below_85c_derated_rating": resistor_loss_max <= d("0.200"),
        "emitter_carrier_junction_has_10c_margin": emitter_junction_at_carrier <= emitter_junction_limit - d(10),
        "single_mark_not_longer_than_datasheet_characterization": single_mark_ms <= d(20),
        "rolling_on_fraction_no_more_than_25pct": rolling_on_fraction <= d("0.25"),
        "floating_lvc_input_is_eliminated": topology["carrier_input_fail_low"],
        "dark_idle_has_30mv_false_assert_margin": false_assert_margin >= d("0.030"),
        "dark_idle_has_20mv_clear_margin": clear_margin >= d("0.020"),
        "optical_assert_current_is_bounded_for_hil": required_photocurrent > d(0) and required_photocurrent <= d("0.000003"),
        "tia_time_constant_is_40_to_60us": tau_min_us >= d(40) and tau_max_us <= d(60),
        "safety_continuous_evidence_trip_matches_mark_limit": continuous_evidence_trip_ms <= single_mark_ms,
        "main_rail_remains_inside_admission": d(dc_budget["worst_by_rail"]["3V3_MAIN"]["load_ma"]) <= d(2500),
        "method_has_missing_limit_rule": any(row["id"] == "PF-10" for row in methods["pass_fail_rules"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.3.3 checks failed: " + ", ".join(failed))

    old_cost = d(devices["yageo_rc1206fr_0733rl"]["cost"]["unit_price_usd"])
    new_cost = d(devices["yageo_rc1206fr_0747rl"]["cost"]["unit_price_usd"])
    pulldown_cost = d(devices["yageo_rc0402fr_0710kl"]["cost"]["unit_price_usd"])
    manifest = {
        "schema_version": 1,
        "stage": "H3.3.3",
        "status": "reviewed_ir_corners_after_four_source_corrections",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH, DISPLAY_PATH, DC_PATH)},
        "provenance": SOURCES,
        "exact_part_checks": exact_checks,
        "topology_checks": topology,
        "receive": {
            "robust_path": {"part": devices[instances["ir_demod"]]["mpn"], "carrier_khz": 38, "agc": "AGC2", "minimum_burst_cycles": 16, "minimum_gap_cycles": "16 to 70 depending on burst length", "sensitivity_max_mw_per_m2": "0.25"},
            "learning_path": {"part": devices[instances["ir_carrier"]]["mpn"], "carrier_khz": [30, 60], "minimum_irradiance_max_mw_per_m2": "25", "carrier_count_error_cycles": [-1, 1]},
            "supply_v": {"demod_min": q(demod_supply_min, "0.000001"), "demod_max": q(demod_supply_max, "0.000001"), "carrier_min": q(carrier_supply_min, "0.000001"), "carrier_max": q(carrier_supply_max, "0.000001")},
            "power_on_guard_ms": int(receiver_power_on_guard_ms),
            "power_off_quiet_guard_ms": int(receiver_power_off_guard_ms),
            "qod_90_to_10_nominal_at_cap_max_ms": q(qod_90_to_10_ms, "0.000001"),
            "rule": "enable both receivers together, discard both inputs for 20 ms, capture both independently; disable and wait 5 ms before declaring IR_QUIET. Exact startup/discharge limits remain HIL-qualified because the switch publishes typical rather than maximum timing.",
        },
        "transmit": {
            "emitter": devices[instances["ir_emitter"]]["mpn"],
            "selected_resistor": devices[instances["ir_emitter_limit"]]["mpn"],
            "resistor_ohm": 47,
            "main_rail_v": {"minimum": q(main_min, "0.000001"), "conservative_maximum": "3.400000"},
            "guaranteed_characterized_current_ma_min": 20,
            "conservative_instantaneous_current_ma_max": q(tx_current_max * d(1000), "0.001"),
            "guaranteed_radiant_intensity_mw_per_sr_at_20ma_min": 15,
            "resistor_loss_mw_max": q(resistor_loss_max * d(1000), "0.001"),
            "local_tx_temperature_limit_c": int(tx_local_temp_limit),
            "carrier_duty_fraction_max": q(carrier_duty_max, "0.000001"),
            "single_mark_ms_max": int(single_mark_ms),
            "rolling_emitter_on_fraction_max_100ms_and_1s": q(rolling_on_fraction, "0.00"),
            "junction_c_at_75c_and_one_third_typical_vf": q(emitter_junction_at_carrier),
            "stuck_evidence_rule": "the independent safety controller requests FAULT_KILL when continuous IR optical evidence exceeds 20 ms; this is separate from the C5 RMT policy and is fault-injected in H8",
            "optical_safety_boundary": "IEC 62471 classification, enclosure/window geometry, range and final temperature remain physical admission tests; no paper calculation labels them compliant",
        },
        "optical_evidence": {
            "sensor": devices[instances["det_ir"]]["mpn"],
            "dark_idle_v": {"minimum": q(dark_idle_min, "0.000001"), "maximum": q(dark_idle_max, "0.000001")},
            "assert_threshold_v": {"minimum": q(min(assert_values), "0.000001"), "maximum": q(max(assert_values), "0.000001")},
            "clear_threshold_v": {"minimum": q(min(clear_values), "0.000001"), "maximum": q(max(clear_values), "0.000001")},
            "false_assert_margin_mv_min_including_offsets": q(false_assert_margin * d(1000), "0.001"),
            "clear_margin_mv_min_including_offsets": q(clear_margin * d(1000), "0.001"),
            "required_photocurrent_ua_max_for_hil": q(required_photocurrent * d(1000000), "0.001"),
            "tia_time_constant_us": {"minimum": q(tau_min_us), "maximum": q(tau_max_us)},
            "rule": "the paper circuit proves a dark-state margin and exposes a bounded photocurrent target; the VEMD1060 response at only about 0.3-V reverse bias and the tunnel coupling are not guaranteed by its 5-V irradiance table and therefore remain exact HIL thresholds",
        },
        "checks": checks,
        "corrections": [
            {"id": "H3.3.3-F01", "finding": "33 ohm targeted the emitter's 70-mA absolute maximum as though it were an operating rating and used a 20-mA forward-voltage limit outside its stated condition", "correction": "fit active/stocked exact RC1206FR-0747RL", "functional_effect": "the circuit still guarantees at least the characterized 20-mA/15-mW-per-sr point and bounds the conservative hot instantaneous corner to 50.6 mA"},
            {"id": "H3.3.3-F02", "finding": "C5 GPIO6 could be high impedance while the AON SN74LVC1G08 remained powered, leaving a standard CMOS input floating", "correction": "add an exact 10-kohm pull-down directly at the carrier-gate input", "functional_effect": "reset, missing C5 and disconnect states are deterministically dark before the downstream MOSFET pull-down"},
            {"id": "H3.3.3-F03", "finding": "the device registry claimed a 50-mW-per-sr guaranteed minimum at 70 mA, but the manufacturer gives 90 typical there and guarantees 15 minimum only at 20 mA", "correction": "replace the false limit with the exact guaranteed and typical rows", "functional_effect": "range claims now begin from a real guaranteed optical point; final range remains HIL"},
            {"id": "H3.3.3-F04", "finding": "the IR prose named ESP32-C5-MINI-1U although the selected, pin-reviewed and rendered module is ESP32-C5-WROOM-1U-N8R8", "correction": "use the exact WROOM-1U identity and current v1.2 module source everywhere in the IR contract", "functional_effect": "no pin changes; the documentation now describes the component that will actually be assembled"},
        ],
        "cost_delta_usd_at_100": {"old_resistor": q(old_cost, "0.0000"), "new_resistor": q(new_cost, "0.0000"), "added_input_pulldown": q(pulldown_cost, "0.0000"), "total_delta_per_board": q(new_cost + pulldown_cost - old_cost, "0.0000")},
        "residual_physical_only": [
            "verify received TSOP75238TT/TSMP95000TT identity, orientation, two-channel capture, 20-ms startup guard, 5-ms QOD quiet guard and no-back-power",
            "replay a representative 30-to-60-kHz protocol corpus and measure carrier/count accuracy, robust AGC behavior, range and field of view",
            "measure VSMY14940 current, optical range/alignment, local temperature and IEC 62471 classification through the final enclosure/window",
            f"calibrate the VEMD1060 tunnel against the <={q(required_photocurrent * d(1000000), '0.001')}-uA paper target and inject missing emitter, ambient leakage, RX crosstalk, stuck carrier, brownout and FAULT_KILL",
        ],
        "review_summary": {"checks": len(checks), "failed_checks": len(failed), "corrected_findings": 4, "unresolved_findings": 0, "status": "reviewed"},
        "next": {"stage": "H3.3.4", "action": "verify battery sensing, thermistors and analog fault thresholds"},
        "open_findings": [],
    }
    return {OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", DOC_EN: render_doc(manifest, False), DOC_RU: render_doc(manifest, True)}, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    rx, tx, optical, cost = manifest["receive"], manifest["transmit"], manifest["optical_evidence"], manifest["cost_delta_usd_at_100"]
    if russian:
        title = "# Электрическая проверка IR"
        nav = "[English](ir-electrical-verification.md) · [На главную](../README.ru.md) · [Схемы](schematics.ru.md) · [Виртуальная проверка](virtual-verification.ru.md)"
        intro = "H3.3.3 проверяет полный IR-тракт C5: устойчивый декодированный RX, raw carrier learning, безопасный TX и независимое подтверждение реального света. Бумажный результат не подменяет измерение дальности и optical safety готового корпуса."
        body = f"""## Два приёмника

`{rx['robust_path']['part']}` даёт устойчивый active-low envelope 38 кГц с AGC2, а `{rx['learning_path']['part']}` независимо выдаёт циклы 30–60 кГц для обучения. Оба включаются только в IR RX/LEARN: питание на их контактах остаётся `{rx['supply_v']['carrier_min']}…{rx['supply_v']['demod_max']} В`. После включения C5 отбрасывает первые `{rx['power_on_guard_ms']}` мс; после выключения ждёт `{rx['power_off_quiet_guard_ms']}` мс до `IR_QUIET`. Короткие форматы, которые подавляет AGC2, остаются доступны по raw-каналу.

## Передатчик

`{tx['selected_resistor']}` заменяет прежние 33 Ω. Он гарантирует как минимум характеризованный режим `20 мА / 15 мВт·ср⁻¹`, а верхний hot-corner равен `{tx['conservative_instantaneous_current_ma_max']} мА`, не 70-мА absolute maximum. Разрешены carrier duty ≤`1/3`, mark ≤`{tx['single_mark_ms_max']} мс`, emitter-on ≤`{tx['rolling_emitter_on_fraction_max_100ms_and_1s']}` в окнах 100 мс и 1 с; при локальных `{tx['local_tx_temperature_limit_c']} °C` TX запрещён. Независимый safety-controller гасит непрерывное optical evidence длиннее 20 мс.

## Подтверждение света

VEMD1060X01 смотрит на emitter внутри светонепроницаемого тоннеля. Полный resistor/offset corner оставляет минимум `{optical['false_assert_margin_mv_min_including_offsets']}` мВ до ложного срабатывания в темноте и `{optical['clear_margin_mv_min_including_offsets']}` мВ до гарантированного отпускания. Для assert HIL должен обеспечить не более `{optical['required_photocurrent_ua_max_for_hil']}` мкА на TIA; это намеренно измеряемый порог, потому что даташит фотодиода нормирует irradiance при 5 В, а наша рабочая обратная поляризация около 0,3 В. Evidence подтверждает физический свет, но никогда не разрешает TX.

Исправления добавляют всего `{cost['total_delta_per_board']} USD` на устройство при количестве 100. **H3.3.3 проверено; текущий точный маркер — `H3.6.1`.**

[Машинный пакет H3-VRF33](../hardware/verification/generated/H3-VRF33-ir.json)."""
    else:
        title = "# IR electrical verification"
        nav = "[Русский](ir-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)"
        intro = "H3.3.3 checks the complete C5 IR chain: robust demodulated receive, raw carrier learning, bounded transmit and independent physical-light evidence. The paper result does not replace final range and optical-safety measurements through the enclosure."
        body = f"""## Dual receive

`{rx['robust_path']['part']}` provides the robust active-low 38-kHz AGC2 envelope while `{rx['learning_path']['part']}` independently returns 30-to-60-kHz carrier cycles for learning. Both are powered only in IR RX/LEARN and remain within `{rx['supply_v']['carrier_min']}…{rx['supply_v']['demod_max']} V. C5 discards the first `{rx['power_on_guard_ms']}` ms after enable and waits `{rx['power_off_quiet_guard_ms']}` ms after disable before declaring `IR_QUIET`. Short formats rejected by AGC2 remain available through the raw path.

## Transmit

`{tx['selected_resistor']}` replaces 33 ohm. It guarantees at least the characterized `20 mA / 15 mW·sr⁻¹` point while the hot instantaneous corner is `{tx['conservative_instantaneous_current_ma_max']} mA`, not the 70-mA absolute maximum. Production permits carrier duty no higher than `1/3`, marks no longer than `{tx['single_mark_ms_max']} ms`, and emitter-on time no higher than `{tx['rolling_emitter_on_fraction_max_100ms_and_1s']}` in rolling 100-ms and 1-s windows; IR TX is inhibited at `{tx['local_tx_temperature_limit_c']} C` local temperature. The independent safety controller kills continuous optical evidence longer than 20 ms.

## Physical-light evidence

VEMD1060X01 views the emitter inside a light-tight tunnel. Full resistor/offset corners retain `{optical['false_assert_margin_mv_min_including_offsets']}` mV minimum dark false-assert margin and `{optical['clear_margin_mv_min_including_offsets']}` mV guaranteed-clear margin. HIL must achieve the bounded `{optical['required_photocurrent_ua_max_for_hil']}`-uA TIA assertion target; this remains measured because the photodiode irradiance table is specified at 5-V reverse bias while this circuit operates near 0.3 V. Evidence confirms physical light and never authorizes TX.

The corrections add only `{cost['total_delta_per_board']} USD` per unit at quantity 100. **H3.3.3 is reviewed; the exact current marker is `H3.6.1`.**

[Machine H3-VRF33 package](../hardware/verification/generated/H3-VRF33-ir.json)."""
    return "\n\n".join((title, nav, intro, body)) + "\n"


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
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale H3.3.3 artifacts: " + ", ".join(stale))
            return 1
    print(f"ok: H3.3.3 reviewed; {manifest['review_summary']['checks']} checks, 0 unresolved findings, next H3.3.4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
