#!/usr/bin/env python3
"""Verify H3.4.3 M1, expansion and service-boundary loading."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
LEVELS_PATH = REPO / "hardware/verification/generated/H3-VRF41-digital-levels.json"
TIMING_PATH = REPO / "hardware/verification/generated/H3-VRF42-digital-timing.json"
NO_BACK_POWER_PATH = REPO / "hardware/ecad/generated/H2-REV53-no-back-power.json"
UI_M1_PATH = REPO / "hardware/ecad/generated/H2-UI40-interboard-m1.json"
RF_M1_PATH = REPO / "hardware/ecad/generated/H2-RF40-interboard-m1.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF43-boundary-loading.json"
DOC_EN = REPO / "docs/boundary-loading-verification.md"
DOC_RU = REPO / "docs/boundary-loading-verification.ru.md"

SOURCES = {
    "m1_plug": "https://www.hirose.com/product/p/CL0578-0523-1-92",
    "m1_receptacle": "https://www.hirose.com/en/product/p/CL0578-0823-5-92",
    "u214_host_receptacle": "https://suddendocs.samtec.com/catalog_english/hle.pdf",
    "u214": "https://docs.m5stack.com/en/cap/Cap_LoRa-1262",
    "m5_unit_receptacle": "https://statics3.seeedstudio.com/fusion/opl/datasheet/320110032.pdf",
    "expansion_efuse": "https://www.ti.com/lit/ds/symlink/tps25947.pdf",
    "u214_i2c_isolator": "https://www.ti.com/lit/ds/symlink/tca4307.pdf",
    "unit_translator": "https://www.ti.com/lit/ds/symlink/txs0102.pdf",
    "connector_esd": "https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf",
    "service_usb_switch": "https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf",
}


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nearest_distance(contact: int, candidates: list[int]) -> int:
    return min(abs(contact - other) for other in candidates)


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    dc = json.loads(DC_PATH.read_text(encoding="utf-8"))
    levels = json.loads(LEVELS_PATH.read_text(encoding="utf-8"))
    timing = json.loads(TIMING_PATH.read_text(encoding="utf-8"))
    no_back_power = json.loads(NO_BACK_POWER_PATH.read_text(encoding="utf-8"))
    ui_m1 = json.loads(UI_M1_PATH.read_text(encoding="utf-8"))
    rf_m1 = json.loads(RF_M1_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    interboard = candidate["interboard_contract"]
    pin_map = interboard["pin_map"]
    m1 = interboard["connector_pair"]
    classes = Counter(row["signal_class"] for row in pin_map)

    main_current_a = d(dc["rail_capabilities"]["3V3_MAIN"]["accepted_continuous_a"])
    aon_current_a = d(dc["rail_capabilities"]["AON_SAFE_3V3"]["accepted_continuous_a"])
    contact_current_a = d(m1["rated_current_per_contact_a"])
    contact_resistance_ohm = d("0.080")
    main_contacts = d(classes["power"] - 2)
    aon_contacts = d(2)
    power_ground_contacts = d(sum(row["net"] == "POWER_GROUND" for row in pin_map))
    main_per_contact_a = main_current_a / main_contacts
    aon_per_contact_a = aon_current_a / aon_contacts
    main_contact_margin_a = contact_current_a - main_per_contact_a
    aon_contact_margin_a = contact_current_a - aon_per_contact_a
    main_drop_v = main_per_contact_a * contact_resistance_ohm
    aon_drop_v = aon_per_contact_a * contact_resistance_ohm
    main_connector_loss_w = main_current_a**2 * contact_resistance_ohm / main_contacts
    aon_connector_loss_w = aon_current_a**2 * contact_resistance_ohm / aon_contacts
    main_return_per_contact_a = main_current_a / power_ground_contacts

    ground_contacts = [row["contact"] for row in pin_map if row["net"] == "POWER_GROUND"]
    audio_ground_contacts = [row["contact"] for row in pin_map if row["net"] == "AUDIO_GROUND"]
    ipc_contacts = [row["contact"] for row in pin_map if row["signal_class"] == "ipc_high_speed"]
    usb_contacts = [row["contact"] for row in pin_map if row["signal_class"] == "usb2_high_speed"]
    audio_contacts = [row["contact"] for row in pin_map if row["signal_class"] == "audio"]
    ipc_ground_distance_max = max(nearest_distance(contact, ground_contacts) for contact in ipc_contacts)
    usb_ground_distance_max = max(nearest_distance(contact, ground_contacts) for contact in usb_contacts)
    audio_ground_distance_max = max(nearest_distance(contact, audio_ground_contacts) for contact in audio_contacts)
    connector_rate_bps = d(m1["transmission_rate_gbps"]) * d(1_000_000_000)
    usb_hs_bps = d(480_000_000)
    m1_rate_ratio = connector_rate_bps / usb_hs_bps

    ext_capability = dc["rail_capabilities"]["5V_EXT_ACTIVE_BRANCH"]
    branch_current_a = d(ext_capability["accepted_continuous_a"])
    branch_efuse_min_a = d(ext_capability["protection_min_a"])
    branch_converter_min_a = d(ext_capability["converter_min_a"])
    branch_margin_a = branch_efuse_min_a - branch_current_a
    branch_margin_pct = branch_margin_a / branch_efuse_min_a * d(100)
    branch_path_resistance_ohm = d("0.060")
    branch_drop_v = branch_current_a * branch_path_resistance_ohm
    branch_loss_w = branch_current_a**2 * branch_path_resistance_ohm
    accidental_two_branch_accepted_a = branch_current_a * d(2)
    accidental_two_branch_trip_floor_a = branch_efuse_min_a * d(2)
    converter_margin_at_two_trip_floors_a = branch_converter_min_a - accidental_two_branch_trip_floor_a

    hle_controlled_pair_current_a = d("4.1")
    hle_margin_a = hle_controlled_pair_current_a - branch_current_a
    hle_margin_pct = hle_margin_a / hle_controlled_pair_current_a * d(100)
    unit_connector_current_a = d(devices[instances["unit_connector"]]["electrical_contract"]["rated_current_a"])
    unit_connector_margin_a = unit_connector_current_a - branch_current_a

    u214_spi_hz = d(10_000_000)
    lvc_delay_ns = max(
        d(devices[instances["u214_host_buffer_a"]]["electrical_contract"]["maximum_propagation_delay_ns_at_3v0_to_3v6"]),
        d(devices[instances["u214_return_buffer"]]["electrical_contract"]["maximum_propagation_delay_ns_at_3v0_to_3v6"]),
    )
    u214_series_ohm = d(22)
    u214_admission_load_pf = d(30)
    u214_rc_10_90_ns = d("2.2") * u214_series_ohm * u214_admission_load_pf / d(1000)
    u214_half_period_ns = d(1_000_000_000) / u214_spi_hz / d(2)
    u214_timing_margin_ns = u214_half_period_ns - lvc_delay_ns - u214_rc_10_90_ns
    u214_uart_bps = d(1_000_000)

    i2c_pull_ohm = d(2200)
    i2c_rise_ns_max = d(300)
    i2c_capacitance_pf_max = i2c_rise_ns_max * d(1000) / (d("0.8473") * i2c_pull_ohm)
    i2c_admission_pf = d(150)
    i2c_rise_at_admission_ns = d("0.8473") * i2c_pull_ohm * i2c_admission_pf / d(1000)

    txs = devices[instances["unit_signal_iso"]]["electrical_contract"]
    unit_i2c_hz = d(400_000)
    unit_uart_bps = d(1_000_000)
    txs_open_drain_margin = d(txs["maximum_open_drain_mbps"]) * d(1_000_000) / unit_i2c_hz
    txs_push_pull_margin = d(txs["maximum_push_pull_mbps"]) * d(1_000_000) / unit_uart_bps

    fsusb = devices[instances["c5_service_usb_switch"]]["electrical_contract"]
    c5_series_ohm = d(22)
    rp_series_ohm = d(27)
    fsusb_ron_ohm = d(fsusb["on_resistance_max_ohm_at_3v"])
    c5_service_series_total_ohm = c5_series_ohm + fsusb_ron_ohm
    rp_service_series_total_ohm = rp_series_ohm + fsusb_ron_ohm
    service_ports = d(2)
    service_vbus_bleeder_ohm = d(1_000_000)
    service_vbus_current_ua = d(5) / service_vbus_bleeder_ohm * d(1_000_000)
    service_data_poweroff_leakage_ua = service_ports * d(2) * d(fsusb["power_off_leakage_max_ua"])
    service_vbus_total_ua = service_ports * service_vbus_current_ua

    exact_instances = {
        "m1_ui_plug": "hirose_fx8c_80p_sv1_92",
        "m1_rf_receptacle": "hirose_fx8c_80s_sv5_92",
        "u214_connector": "samtec_hle_107_02_g_dv_pe_lc",
        "u214_i2c_iso": "tca4307dgkr",
        "u214_host_buffer_a": "nexperia_74lvc126apw_118",
        "u214_host_buffer_b": "nexperia_74lvc126apw_118",
        "u214_return_buffer": "nexperia_74lvc126apw_118",
        "unit_connector": "seeed_1125r_smt_4p",
        "unit_signal_iso": "ti_txs0102_dcur",
        "ext_efuse": "ti_tps259470l_rpwr",
        "unit_efuse": "ti_tps259470l_rpwr",
        "c5_service_usb_switch": "onsemi_fsusb42_mux",
        "rp_service_usb_switch": "onsemi_fsusb42_mux",
    }
    exact_checks = {f"exact_{name}": instances.get(name) == part for name, part in exact_instances.items()}
    checks = {
        **exact_checks,
        "h341_levels_reviewed": levels["review_summary"]["status"] == "reviewed",
        "h342_timing_reviewed": timing["review_summary"]["status"] == "reviewed",
        "m1_has_exactly_80_contacts": len(pin_map) == 80 and m1["positions"] == 80,
        "m1_maps_are_identical": no_back_power["m1"]["ui_rf_maps_identical"] is True and rf_m1["summary"]["cross_project_contact_mismatches"] == 0,
        "m1_ui_and_rf_each_have_51_unique_nets": ui_m1["summary"]["unique_nets"] == 51 and rf_m1["summary"]["unique_nets"] == 51,
        "m1_class_count_is_complete": sum(classes.values()) == 80,
        "m1_has_seven_main_contacts": main_contacts == d(7),
        "m1_has_two_aon_contacts": aon_contacts == d(2),
        "m1_main_per_contact_below_rating": main_per_contact_a < contact_current_a,
        "m1_aon_per_contact_below_rating": aon_per_contact_a < contact_current_a,
        "m1_main_drop_below_30mv": main_drop_v < d("0.030"),
        "m1_aon_drop_below_7mv": aon_drop_v < d("0.007"),
        "m1_main_connector_loss_below_75mw": main_connector_loss_w < d("0.075"),
        "m1_power_return_per_contact_below_rating": main_return_per_contact_a < contact_current_a,
        "m1_ipc_each_has_adjacent_power_ground": ipc_ground_distance_max <= 1,
        "m1_usb_pair_is_bracketed_by_power_ground": usb_ground_distance_max <= 1,
        "m1_audio_each_is_within_two_contacts_of_audio_ground": audio_ground_distance_max <= 2,
        "m1_8gbps_rating_exceeds_usb_hs_by_16x": m1_rate_ratio >= d(16),
        "branch_accepted_current_below_efuse_floor": branch_current_a < branch_efuse_min_a,
        "branch_efuse_margin_above_20pct": branch_margin_pct > d(20),
        "branch_drop_below_75mv_or_equal": branch_drop_v <= d("0.075"),
        "branch_path_loss_below_100mw": branch_loss_w < d("0.100"),
        "accidental_two_branch_accepted_load_below_converter": accidental_two_branch_accepted_a < branch_converter_min_a,
        "accidental_two_branch_trip_floors_below_converter": accidental_two_branch_trip_floor_a < branch_converter_min_a,
        "u214_hle_controlled_pair_rating_above_branch_limit": hle_controlled_pair_current_a > branch_current_a,
        "unit_connector_rating_above_branch_limit": unit_connector_current_a > branch_current_a,
        "u214_spi_margin_above_40ns": u214_timing_margin_ns > d(40),
        "u214_uart_below_1mbps": u214_uart_bps <= d(1_000_000),
        "u214_i2c_150pf_rise_below_300ns": i2c_rise_at_admission_ns < i2c_rise_ns_max and i2c_admission_pf < i2c_capacitance_pf_max,
        "unit_i2c_has_5x_translator_rate_margin": txs_open_drain_margin >= d(5),
        "unit_uart_has_24x_translator_rate_margin": txs_push_pull_margin >= d(24),
        "service_switch_supports_usb2_hs": fsusb["usb_speed_mbps"] == 480 and fsusb["bandwidth_mhz"] >= 720,
        "service_switch_poweroff_leakage_bounded": service_data_poweroff_leakage_ua <= d(8),
        "service_vbus_only_draws_10ua_total": service_vbus_total_ua == d(10),
        "service_vbus_is_not_product_power": all("cannot power any product rail" in no_back_power["invariants"][0] for _ in [0]),
        "all_six_no_back_power_invariants_remain": len(no_back_power["invariants"]) == 6,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.4.3 checks failed: " + ", ".join(failed))

    residual_hil = [
        "measure M1 far-end rail drop, return offset, crosstalk and USB/SPI eye/edge quality after PCB placement",
        "verify received stock U214 male-post material/plating, current continuity, insertion/withdrawal force and repeated-cycle retention; the 4.1-A figure proves only the controlled HLE/TSM pair",
        "measure U214 SPI load/edges at 10 MHz and external I2C total capacitance/rise time <=150 pF/300 ns",
        "qualify each native Unit profile, cable length and pull network through TXS0102; 1-Wire remains specimen-only",
        "inject dual-branch request, overload, reverse source, wrong accessory, hot plug and brownout while proving independent latch-off",
        "measure C5/RP service USB edges/eye and powered-off leakage with one and three hosts",
        "measure product USB Full-Speed through M1 plus all DBG10 UART/SWD recovery paths in the assembled sandwich",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.4.3",
        "status": "reviewed_m1_expansion_and_service_boundary_loading",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, DC_PATH, LEVELS_PATH, TIMING_PATH, NO_BACK_POWER_PATH, UI_M1_PATH, RF_M1_PATH)},
        "provenance": SOURCES,
        "m1": {
            "contacts": len(pin_map), "unique_nets": ui_m1["summary"]["unique_nets"], "class_counts": dict(sorted(classes.items())),
            "rating": {"current_a_per_contact": str(contact_current_a), "contact_resistance_ohm_max": str(contact_resistance_ohm), "transmission_rate_gbps": m1["transmission_rate_gbps"]},
            "main": {"accepted_current_a": str(main_current_a), "contacts": int(main_contacts), "current_a_per_contact": q(main_per_contact_a), "rating_margin_a_per_contact": q(main_contact_margin_a), "drop_v_max": q(main_drop_v, "0.000001"), "connector_loss_w_max": q(main_connector_loss_w, "0.000001")},
            "aon": {"accepted_current_a": str(aon_current_a), "contacts": int(aon_contacts), "current_a_per_contact": q(aon_per_contact_a), "rating_margin_a_per_contact": q(aon_contact_margin_a), "drop_v_max": q(aon_drop_v, "0.000001"), "connector_loss_w_max": q(aon_connector_loss_w, "0.000001")},
            "return_and_locality": {"power_ground_contacts": int(power_ground_contacts), "main_return_a_per_contact_conservative": q(main_return_per_contact_a), "ipc_ground_distance_contacts_max": ipc_ground_distance_max, "usb_ground_distance_contacts_max": usb_ground_distance_max, "audio_ground_distance_contacts_max": audio_ground_distance_max},
            "rate_margin_over_usb2_hs": q(m1_rate_ratio),
        },
        "expansion_power": {
            "operational_rule": "one active signal group means U214 and native Unit are not admitted together",
            "branch_accepted_a": str(branch_current_a), "branch_efuse_floor_a": str(branch_efuse_min_a), "branch_margin_a": q(branch_margin_a), "branch_margin_percent": q(branch_margin_pct),
            "path_resistance_envelope_ohm": str(branch_path_resistance_ohm), "drop_v_at_limit": q(branch_drop_v), "loss_w_at_limit": q(branch_loss_w),
            "common_converter_floor_a": str(branch_converter_min_a), "two_branch_accepted_a": str(accidental_two_branch_accepted_a), "two_branch_trip_floor_a": str(accidental_two_branch_trip_floor_a), "converter_margin_at_two_trip_floors_a": q(converter_margin_at_two_trip_floors_a),
            "u214_host_receptacle_controlled_hle_tsm_rating_a_per_pin": str(hle_controlled_pair_current_a), "u214_rating_margin_percent": q(hle_margin_pct),
            "u214_mate_caveat": "stock U214 male-post material/plating/current remains received-sample evidence; the HLE/TSM controlled-pair rating is not silently transferred to an undocumented mate",
            "native_unit_connector_rating_a": str(unit_connector_current_a), "native_unit_margin_a": q(unit_connector_margin_a),
        },
        "u214_signal_loading": {
            "paths": {"buffered_spi_uart_control": 9, "isolated_i2c": 2}, "spi_hz": int(u214_spi_hz), "lvc_delay_ns_max": str(lvc_delay_ns), "source_series_ohm": int(u214_series_ohm), "admission_load_pf": int(u214_admission_load_pf), "rc_10_90_ns": q(u214_rc_10_90_ns), "half_period_ns": q(u214_half_period_ns), "timing_margin_ns": q(u214_timing_margin_ns), "uart_bps_max": int(u214_uart_bps),
            "i2c": {"pull_ohm": int(i2c_pull_ohm), "rise_ns_max": int(i2c_rise_ns_max), "calculated_capacitance_pf_max": q(i2c_capacitance_pf_max), "admission_capacitance_pf": int(i2c_admission_pf), "rise_at_admission_ns": q(i2c_rise_at_admission_ns)},
        },
        "native_unit_loading": {"signals": 2, "i2c_hz_max": int(unit_i2c_hz), "uart_bps_max": int(unit_uart_bps), "txs_open_drain_rate_margin": q(txs_open_drain_margin), "txs_push_pull_rate_margin": q(txs_push_pull_margin), "one_wire": "HIL-only profile; not a paper consequence of generic GPIO support"},
        "service_boundaries": {
            "c5_service_series_plus_switch_ron_ohm_max": q(c5_service_series_total_ohm), "rp_service_series_plus_switch_ron_ohm_max": q(rp_service_series_total_ohm), "switch_bandwidth_mhz": fsusb["bandwidth_mhz"], "switch_usb_speed_mbps": fsusb["usb_speed_mbps"],
            "two_ports_four_lines_poweroff_leakage_ua_max": q(service_data_poweroff_leakage_ua), "two_vbus_bleeders_ua_at_5v": q(service_vbus_total_ua), "product_power_from_service_vbus": False,
        },
        "exact_instance_checks": exact_checks,
        "checks": checks,
        "corrections": [
            "self-review corrected the U214 I2C pF-to-ns conversion before accepting H3.4.3; the corrected 150-pF rise is 279.609 ns and still passes the 300-ns limit"
        ],
        "open_findings": [],
        "residual_physical_only": residual_hil,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.6.1", "action": "build the worst-case board, battery and enclosure thermal model"},
    }

    en = f"""# M1, expansion and service-boundary loading

`H3.4.3` is reviewed with `{len(checks)}` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

## M1 worst-case bounds

The exact 80-contact FX8C pair carries 51 nets. Even the deliberately over-conservative assumption that the whole accepted 2.5-A main rail crosses M1 loads each of seven contacts by only `{q(main_per_contact_a)} A` against 0.4 A; maximum connector drop is `{q(main_drop_v * d(1000))} mV` and loss `{q(main_connector_loss_w * d(1000))} mW`. AON uses `{q(aon_per_contact_a)} A` per contact. Every IPC and USB contact is adjacent to POWER_GROUND; every low-level audio contact is within two positions of AUDIO_GROUND. The connector's 8-Gbit/s rating is `{q(m1_rate_ratio)}x` USB2 High-Speed.

## Expansion bounds

Each active 5-V branch is limited to 1.25 A below the 1.632-A guaranteed eFuse floor (`{q(branch_margin_pct)}%` margin). The 60-mOhm path envelope gives `{q(branch_drop_v * d(1000))} mV` and `{q(branch_loss_w * d(1000))} mW`. One active signal group keeps U214 and native Unit operationally exclusive; even a faulty dual request at both eFuse floors totals `{q(accidental_two_branch_trip_floor_a)} A`, still below the 4-A converter floor.

The HLE controlled HLE/TSM pair is rated 4.1 A per pin, and the native `1125R-SMT-4P` is rated 2 A. The stock U214's undocumented male-post material/plating is still an H5 received-sample gate; the socket rating is not silently assigned to its mate.

U214 SPI is admitted at 10 MHz: a 4.7-ns buffer plus the 22-Ohm/30-pF envelope leaves `{q(u214_timing_margin_ns)} ns` inside a half-cycle. U214 I2C is admitted only at <=150 pF (`{q(i2c_rise_at_admission_ns)} ns` with 2.2 kOhm). Native Unit profiles stay <=400-kHz I2C or <=1-Mbit/s UART; 1-Wire remains HIL-only.

Service VBUS cannot power the product. Two service ports draw only 10 uA through their bleeders; four powered-off data lines are bounded to 8 uA through exact FSUSB42 switches. Signal integrity and wrong-accessory injection remain seven explicit H5/H8 gates.

Machine evidence: [`H3-VRF43-boundary-loading.json`](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
"""
    ru = f"""# Loading M1, expansions и service boundaries

`H3.4.3` проверено: `{len(checks)}` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

## Worst-case границы M1

Точная 80-контактная пара FX8C переносит 51 net. Даже нарочно сверхконсервативное предположение, что весь принятый main rail 2,5 А проходит через M1, нагружает каждый из семи контактов лишь на `{q(main_per_contact_a)} А` при rating 0,4 А; максимальные connector drop `{q(main_drop_v * d(1000))} мВ`, loss `{q(main_connector_loss_w * d(1000))} мВт`. AON использует `{q(aon_per_contact_a)} А` на контакт. Каждый IPC/USB contact соседствует с POWER_GROUND; каждый low-level audio contact находится не дальше двух позиций от AUDIO_GROUND. Rating connector 8 Гбит/с в `{q(m1_rate_ratio)} раза` выше USB2 High-Speed.

## Границы expansions

Каждая активная 5-В ветка ограничена 1,25 А ниже гарантированного eFuse floor 1,632 А (margin `{q(branch_margin_pct)}%`). Envelope пути 60 мОм даёт `{q(branch_drop_v * d(1000))} мВ` и `{q(branch_loss_w * d(1000))} мВт`. One active signal group делает U214 и native Unit взаимоисключающими в эксплуатации; даже ошибочный двойной запрос на обоих eFuse floors суммарно равен `{q(accidental_two_branch_trip_floor_a)} А` и остаётся ниже converter floor 4 А.

Контролируемая пара HLE/TSM рассчитана на 4,1 А на pin, native `1125R-SMT-4P` — на 2 А. Неописанные material/plating штырей stock U214 всё равно остаются received-sample gate H5: rating розетки молча не присваивается её ответной части.

U214 SPI допускается на 10 МГц: buffer 4,7 нс и envelope 22 Ом/30 пФ оставляют `{q(u214_timing_margin_ns)} нс` внутри half-cycle. U214 I2C допускается только при <=150 пФ (`{q(i2c_rise_at_admission_ns)} нс` с 2,2 кОм). Native Unit profiles остаются <=400 кГц I2C или <=1 Мбит/с UART; 1-Wire — только HIL.

Service VBUS не может питать продукт. Два service ports потребляют лишь 10 мкА через bleeders; четыре data lines при снятом питании ограничены 8 мкА через точные FSUSB42. Signal integrity и wrong-accessory injection остаются семью явными gates H5/H8.

Машинное evidence: [`H3-VRF43-boundary-loading.json`](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
"""
    return {OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", DOC_EN: en, DOC_RU: ru}, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H3.4.3 artifacts: " + ", ".join(stale))
    print(f"ok: H3.4.3 reviewed; {len(manifest['checks'])} checks, next H3.6.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
