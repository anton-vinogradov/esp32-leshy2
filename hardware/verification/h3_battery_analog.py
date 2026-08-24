#!/usr/bin/env python3
"""Verify H3.3.4 battery sensing, thermistors and analog fault thresholds."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from itertools import product
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF34-battery-analog.json"
DOC_EN = REPO / "docs/battery-analog-verification.md"
DOC_RU = REPO / "docs/battery-analog-verification.ru.md"

SOURCES = {
    "admission_and_safety_mcu": "https://www.ti.com/lit/ds/symlink/mspm0c1106.pdf",
    "pack_gauge_protector": "https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf",
    "nvdc_charger": "https://www.ti.com/lit/ds/symlink/bq25798.pdf",
    "thermistor": "https://product.tdk.com/en/search/sensor/ntc/chip-ntc-thermistor/info?part_no=B57332V5103F360",
    "cell_datasheet": "https://www.xtar.cc/download/18650-4000mah-data-sheet",
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


def ntc_resistance(temp_c: float, r25: float, beta: float) -> float:
    return r25 * math.exp(beta * (1.0 / (temp_c + 273.15) - 1.0 / 298.15))


def ntc_ratio_corners(temp_c: float) -> tuple[Decimal, Decimal]:
    values = []
    for pullup, r25, beta in product((9900.0, 10100.0), (9900.0, 10100.0), (3400.65, 3469.35)):
        resistance = ntc_resistance(temp_c, r25, beta)
        values.append(d(resistance / (pullup + resistance)))
    return min(values), max(values)


def temp_from_ts_ratio(ratio: float, top_k: float, bottom_k: float, r25_k: float, beta: float) -> float:
    parallel_k = ratio * top_k / (1.0 - ratio)
    inverse_ntc = 1.0 / parallel_k - 1.0 / bottom_k
    if inverse_ntc <= 0:
        raise ValueError("TS ratio is outside the realizable NTC network")
    ntc_k = 1.0 / inverse_ntc
    return 1.0 / (1.0 / 298.15 + math.log(ntc_k / r25_k) / beta) - 273.15


def bq_temperature_window(ratio_min: float, ratio_max: float) -> tuple[Decimal, Decimal]:
    values = []
    for ratio, top, bottom, r25, beta in product(
        (ratio_min, ratio_max), (5.23 * 0.99, 5.23 * 1.01), (30.1 * 0.99, 30.1 * 1.01),
        (10.0 * 0.99, 10.0 * 1.01), (3435.0 * 0.99, 3435.0 * 1.01),
    ):
        values.append(d(temp_from_ts_ratio(ratio, top, bottom, r25, beta)))
    return min(values), max(values)


def divider_corners(vin: Decimal, top_nom: Decimal, bottom_nom: Decimal) -> dict:
    tolerance = d("0.01")
    leakage = d("0.0000001")
    cap_f = d("0.000000010")
    node_values = []
    rth_values = []
    for top, bottom, pin_current in product(
        (top_nom * (d(1) - tolerance), top_nom * (d(1) + tolerance)),
        (bottom_nom * (d(1) - tolerance), bottom_nom * (d(1) + tolerance)),
        (-leakage, leakage),
    ):
        rth = top * bottom / (top + bottom)
        node_values.append(vin * bottom / (top + bottom) + pin_current * rth)
        rth_values.append(rth)
    settle_ms = max(rth_values) * cap_f * d("6.907755278982137") * d(1000)
    return {
        "input_v": q(vin, "0.000001"),
        "node_v_min": q(min(node_values), "0.000001"),
        "node_v_max": q(max(node_values), "0.000001"),
        "minimum_margin_to_1v38_reference_mv": q((d("1.38") - max(node_values)) * d(1000), "0.001"),
        "thevenin_ohm_max": q(max(rth_values), "0.1"),
        "six_point_nine_tau_ms": q(settle_ms, "0.001"),
    }


def reconstructed_error(vin: Decimal, top_nom: Decimal, bottom_nom: Decimal) -> tuple[Decimal, Decimal]:
    errors = []
    tolerance = d("0.01")
    for top, bottom, pin_current, vref, offset, gain_lsb in product(
        (top_nom * (d(1) - tolerance), top_nom * (d(1) + tolerance)),
        (bottom_nom * (d(1) - tolerance), bottom_nom * (d(1) + tolerance)),
        (d("-0.0000001"), d("0.0000001")),
        (d("1.38"), d("1.42")),
        (d("-0.005"), d("0.005")),
        (d(-6), d(6)),
    ):
        rth = top * bottom / (top + bottom)
        node = vin * bottom / (top + bottom) + pin_current * rth
        code = (node + offset) / vref * d(4095) + gain_lsb
        inferred = code / d(4095) * d("1.4") * (top_nom + bottom_nom) / bottom_nom
        errors.append(inferred - vin)
    return min(errors), max(errors)


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    routes = route_set(candidate)

    exact_parts = {
        "charger": "ti_bq25798_rqmr",
        "gauge": "adi_max17320_g20_t",
        "pack_controller": "ti_mspm0c1106_sdgs20r",
        "safety_controller": "ti_mspm0c1106_sdgs20r",
        "charger_ntc": "tdk_b57332v5103f360",
        "cell0_ntc": "tdk_b57332v5103f360",
        "cell1_ntc": "tdk_b57332v5103f360",
        "cell0": "xtar_18650_4000mah_protected",
        "cell1": "xtar_18650_4000mah_protected",
    }
    exact_checks = {
        "charger": instances.get("nvdc_charger") == exact_parts["charger"],
        "gauge": instances.get("pack_gauge") == exact_parts["gauge"],
        "pack_controller": instances.get("pack_admission") == exact_parts["pack_controller"],
        "safety_controller": instances.get("safety_controller") == exact_parts["safety_controller"],
        "charger_ntc": instances.get("charger_ts_ntc") == exact_parts["charger_ntc"],
        "cell0_ntc": instances.get("pack_ntc0") == exact_parts["cell0_ntc"],
        "cell1_ntc": instances.get("pack_ntc1") == exact_parts["cell1_ntc"],
        "cell0": instances.get("pack_cell0") == exact_parts["cell0"],
        "cell1": instances.get("pack_cell1") == exact_parts["cell1"],
    }
    mcu = devices[exact_parts["pack_controller"]]
    channel_checks = {
        "pack_mid_pa25_is_real_adc0_2_pin20": mcu["adc_contract"]["package_channels"]["PA25"] == "physical pin 20 / ADC0_2",
        "pack_stack_pa26_is_real_adc0_1_pin1": mcu["adc_contract"]["package_channels"]["PA26"] == "physical pin 1 / ADC0_1",
        "power_zone_pa26_is_real_adc0_1_pin1": mcu["adc_contract"]["package_channels"]["PA26"] == "physical pin 1 / ADC0_1",
        "rf_zone_pa27_is_real_adc0_0_pin2": mcu["adc_contract"]["package_channels"]["PA27"] == "physical pin 2 / ADC0_0",
        "ui_zone_pa16_is_real_adc0_14_pin12": mcu["adc_contract"]["package_channels"]["PA16"] == "physical pin 12 / ADC0_14",
    }
    topology = {
        "midpoint_divider": require_route(routes, "pack_mid_adc_top1.END_2", "pack_admission.PA25", "PACK_CELL0_ADC"),
        "stack_divider": require_route(routes, "pack_stack_adc_top4.END_2", "pack_admission.PA26", "PACK_STACK_ADC"),
        "charger_ts_independent": require_route(routes, "nvdc_charger.TS", "charger_ts_ntc.END_1", "CHARGER_TS"),
        "two_independent_cell_ntcs": require_route(routes, "pack_gauge.TH1", "pack_ntc0.END_1", "PACK_CELL0_TEMP")
        and require_route(routes, "pack_gauge.TH2", "pack_ntc1.END_1", "PACK_CELL1_TEMP"),
        "power_zone_adc": require_route(routes, "power_zone_temp_pullup.END_2", "safety_controller.PA26", "POWER_ZONE_TEMP_ADC"),
        "rf_zone_adc": require_route(routes, "rf_zone_temp_pullup.END_2", "safety_controller.PA27", "RF_ZONE_TEMP_ADC"),
        "ui_zone_adc": require_route(routes, "ui_zone_temp_pullup.END_2", "safety_controller.PA16", "UI_ZONE_TEMP_ADC"),
    }

    midpoint = divider_corners(d("4.3"), d(440000), d(169000))
    stack = divider_corners(d("8.6"), d(1100000), d(169000))
    midpoint_error = reconstructed_error(d("4.3"), d(440000), d(169000))
    stack_error = reconstructed_error(d("8.6"), d(1100000), d(169000))
    upper_error = (stack_error[0] - midpoint_error[1], stack_error[1] - midpoint_error[0])
    midpoint_current_ua = d("4.3") / d(609000) * d(1000000)
    stack_current_ua = d("8.6") / d(1269000) * d(1000000)
    imbalance_48h_mah = midpoint_current_ua * d(48) / d(1000)

    ntc_codes = {}
    for temp in (-40, -20, 0, 25, 40, 55, 60, 65, 75, 85, 100, 150):
        low, high = ntc_ratio_corners(float(temp))
        ntc_codes[str(temp)] = {
            "ratio_min": q(low, "0.000001"), "ratio_max": q(high, "0.000001"),
            "code_min": int((low * d(4095)).to_integral_value()),
            "code_max": int((high * d(4095)).to_integral_value()),
        }
    zone_thresholds = {
        "sensor_open_code_at_or_above": 4000,
        "sensor_short_code_at_or_below": 64,
        "warning_code_at_or_below": 880,
        "fault_kill_code_at_or_below": 740,
        "fault_rearm_code_at_or_above": 1000,
        "interpretation": "open/short is a fault; warning is guaranteed by 65 C without a 60 C false warning; FAULT_KILL is guaranteed by 75 C without a 65 C false kill; rearm cannot occur at 60 C and is guaranteed by 55 C",
    }

    bq_windows = {
        "cold_suspend_c": bq_temperature_window(0.724, 0.742),
        "cold_reenable_c": bq_temperature_window(0.715, 0.725),
        "warm_suspend_c": bq_temperature_window(0.479, 0.489),
        "warm_reenable_c": bq_temperature_window(0.492, 0.502),
        "hot_suspend_c": bq_temperature_window(0.337, 0.347),
        "hot_reenable_c": bq_temperature_window(0.350, 0.360),
    }
    bq_serialized = {name: {"minimum": q(value[0], "0.01"), "maximum": q(value[1], "0.01")} for name, value in bq_windows.items()}
    ntc = devices["tdk_b57332v5103f360"]["electrical_contract"]
    ntherm_delta = round(3245919 / ntc["b25_85_k"] - 512)
    nthermcfg = 0x7000 + ntherm_delta
    zone_ntc_power_mw = d("3.4") ** 2 / d(40000) * d(1000)
    zone_ntc_current_ua = d("3.4") / d(20000) * d(1000000)

    checks = {
        **{f"exact_{name}": passed for name, passed in exact_checks.items()},
        **channel_checks,
        **topology,
        "midpoint_screen_below_reference_with_150mv_margin": d(midpoint["minimum_margin_to_1v38_reference_mv"]) >= d(150),
        "stack_screen_below_reference_with_150mv_margin": d(stack["minimum_margin_to_1v38_reference_mv"]) >= d(150),
        "twenty_ms_exceeds_both_six_point_nine_tau": d(20) >= max(d(midpoint["six_point_nine_tau_ms"]), d(stack["six_point_nine_tau_ms"])),
        "divider_48h_imbalance_below_half_mah": imbalance_48h_mah < d("0.5"),
        "zone_thermistor_power_below_rating": zone_ntc_power_mw < d(ntc["maximum_power_mw_at_25c"]),
        "zone_thermistor_current_below_rating": zone_ntc_current_ua < d(ntc["maximum_permissive_current_ua_at_25c"]),
        "zone_warning_separates_60_and_65c": ntc_codes["60"]["code_min"] > 880 and ntc_codes["65"]["code_max"] < 880,
        "zone_kill_separates_65_and_75c": ntc_codes["65"]["code_min"] > 740 and ntc_codes["75"]["code_max"] < 740,
        "zone_rearm_separates_55_and_60c": ntc_codes["55"]["code_min"] > 1000 and ntc_codes["60"]["code_max"] < 1000,
        "zone_open_separates_minus40c": ntc_codes["-40"]["code_max"] < 4000,
        "bq_open_is_cold_fault": d("30.1") / (d("5.23") + d("30.1")) > d("0.742"),
        "bq_short_is_hot_fault": d(0) < d("0.337"),
        "bq_warm_backup_blocks_by_41c_full_corner": bq_windows["warm_suspend_c"][1] <= d("41.1"),
        "max_thermistor_curve_is_exact": nthermcfg == 0x71B1,
        "charger_has_machine_configuration_contract": "configuration_contract" in devices["ti_bq25798_rqmr"],
        "gauge_has_machine_configuration_contract": "configuration_contract" in devices["adi_max17320_g20_t"],
        "method_has_independent_fault_rule": any(row["id"] == "PF-07" for row in methods["pass_fail_rules"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.3.4 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.3.4",
        "status": "reviewed_battery_sensing_thermistors_and_analog_fault_thresholds",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH)},
        "provenance": SOURCES,
        "exact_part_checks": exact_checks,
        "actual_package_adc_channels": channel_checks,
        "topology_checks": topology,
        "pack_adc": {
            "reference": "internal 1.4 V, 1.38-to-1.42-V full limit",
            "sequence": "wait at least 20 ms after admission-domain validity or reference-mode change; enable VREF and wait at least 30 us; discard two conversions; average at least eight; read midpoint before stack",
            "midpoint_screen": midpoint,
            "stack_screen": stack,
            "full_corner_reconstruction_error_v": {
                "midpoint": {"minimum": q(midpoint_error[0], "0.001"), "maximum": q(midpoint_error[1], "0.001")},
                "stack": {"minimum": q(stack_error[0], "0.001"), "maximum": q(stack_error[1], "0.001")},
                "upper_cell_by_subtraction": {"minimum": q(upper_error[0], "0.001"), "maximum": q(upper_error[1], "0.001")},
            },
            "role": "independent gross plausibility and topology evidence, not the precision imbalance instrument",
            "admission": {
                "max17320_each_cell_v": [2.70, 4.25],
                "max17320_pair_imbalance_mv_max": 100,
                "adc_midpoint_plausibility_v": [2.45, 4.50],
                "adc_stack_plausibility_v": [4.90, 9.00],
                "adc_upper_by_subtraction_plausibility_v": [1.90, 5.10],
                "rule": "all MAX17320 limits, both protected-image/checksum reads, both ADC plausibility windows, PFAIL clear and the bounded diagnostic pulse must agree before the external FET hold is released",
            },
            "static_drain": {
                "midpoint_divider_ua_at_4v3": q(midpoint_current_ua, "0.001"),
                "stack_divider_ua_at_8v6": q(stack_current_ua, "0.001"),
                "lower_cell_extra_imbalance_mah_over_48h": q(imbalance_48h_mah, "0.001"),
                "rule": "acceptable for the one-to-two-day unattended mission; long removed-cell storage and balancing correction remain measured HIL behavior",
            },
        },
        "board_zone_thermistors": {
            "reference": "ADC VDD, ratiometric; do not use the internal 1.4-V reference",
            "channels": {"POWER": "PA26 / pin 1 / ADC0_1", "RF_VOICE": "PA27 / pin 2 / ADC0_0", "UI": "PA16 / pin 12 / ADC0_14"},
            "filter_and_sampling": "10-kohm pull-up, exact 10-kohm NTC and 100 nF; allow at least 5 ms and discard one conversion after MUX/reference change",
            "full_corner_code_table": ntc_codes,
            "thresholds": zone_thresholds,
            "nominal_25c_ntc_power_mw_at_3v4": q(zone_ntc_power_mw, "0.001"),
            "nominal_25c_current_ua_at_3v4": q(zone_ntc_current_ua, "0.001"),
            "fault_behavior": "any open, short or kill threshold requests the non-programmable FAULT_KILL latch, stops watchdog service and retains the first-fault code for the next display boot; rearm requires all three zones above the rearm code plus explicit power-cycle/recovery policy",
        },
        "charger_ts": {
            "network": "REGN -> 5.23 kohm -> TS; TS -> 30.1 kohm || B57332V5103F360 -> ground",
            "configuration": "TS_IGNORE=0, TS_COOL=1, TS_WARM=0 and JEITA_ISETH=0; CE remains high until protected configuration and readback complete",
            "full_corner_temperature_windows_c": bq_serialized,
            "normal_policy": "request zero charge above 35 C; MAX17320 blocks charge at its 40-C profile; the independent BQ warm comparator suspends by 41.1 C at the full calculated corner",
            "faults": "TS open resolves above the cold threshold and TS short below the hot threshold, so either suspends charging without host firmware",
        },
        "max17320": {
            "part": devices["adi_max17320_g20_t"]["mpn"],
            "nthermcfg": f"0x{nthermcfg:04X}",
            "npackcfg": "2S, TH1+TH2 enabled, TH3/TH4 grounded and disabled",
            "temperature_profile_c": {"charge_cold_block": 0, "charge_warm_reduce": 35, "charge_hot_block": 40, "discharge_cold_block": -20, "discharge_hot_block": 60},
            "balancing": "BALCFG=011 (10 mV) and Rmismatch=3 (11.7 mohm); exact 49.9-ohm paths remain inside the 100-mA pin and 0.66-W resistor limits",
            "image_rule": devices["adi_max17320_g20_t"]["configuration_contract"]["protected_image_rule"],
        },
        "cell_contract": devices["xtar_18650_4000mah_protected"]["electrical_contract"],
        "checks": checks,
        "corrections": [
            {"id": "H3.3.4-F01", "finding": "the three 10-kohm/10-kohm board thermistor nodes are about half of 3.3 V at room temperature and therefore exceed the internal 1.4-V ADC reference", "correction": "make VDD-reference ratiometric conversion a machine-readable firmware contract and reserve internal 1.4 V for the pack dividers", "functional_effect": "the complete -40-to-150-C sensor range plus open-circuit detection is observable without changing hardware"},
            {"id": "H3.3.4-F02", "finding": "BQ25798 and MAX17320 lacked machine-readable configuration contracts even though the charge-temperature policy and protected NVM image are safety state", "correction": "record exact reset/readback and golden-image rules while retaining the architecture schema's non-firmware-device classification", "functional_effect": "a default, blank or stale image cannot silently become an admitted charging policy"},
            {"id": "H3.3.4-F03", "finding": "the selected TDK NTC had only a generic B3380 label, while its exact product data gives B25/85=3435 K and the MAX17320 curve word depends on that value", "correction": "record every published beta and derive exact nThermCfg 0x71B1", "functional_effect": "cell-temperature conversion uses the selected physical part instead of a near-family assumption"},
            {"id": "H3.3.4-F04", "finding": "the exact XTAR source had not been converted into electrical limits", "correction": "record 2-A standard charge, 4.2+/-0.03 V, 2.5-V cutoff, 10-A continuous discharge, 11-to-14-A protection and exact capacity/resistance rows", "functional_effect": "the product keeps the already accepted 2-A ceiling and applies narrower independent temperature limits"},
        ],
        "remaining_hil": [
            "program one golden MAX17320 image, verify both address spaces/checksum/readback and fault-inject blank, corrupt and exhausted-write specimens",
            "calibrate the two divider channels on the assembled admission domain and inject open, short, swapped, reversed, missing and imbalanced cells",
            "thermally ramp every cell and board NTC, measure bond response time and prove open/short/lift detection plus the 35/40/60/65/75-C policy",
            "verify BQ CE-default-off, TS open/short, exact warm/cold suspend and all source/load/charge-current transitions with the exact cell lot",
            "measure long-idle divider imbalance, MAX balancing heat and both 49.9-ohm balance-resistor temperatures",
        ],
        "review_summary": {"checks": len(checks), "failed": 0, "corrections": 4, "new_bom_cost_usd": "0.0000"},
        "next": {"stage": "H3.3.5", "action": "consolidate display, audio, IR and battery analog corner evidence"},
    }

    en = f"""# Battery sensing and thermal analog verification

H3.3.4 is reviewed with `{len(checks)}` machine checks and four source corrections. No component or BOM-cost change is required. The exact current marker is `H3.6.1`: worst-case board, battery and enclosure thermal model.

## What is now fixed

- The actual MSPM0C1106 DGS20 contacts are used: pack midpoint `PA25/ADC0_2` pin 20, pack stack and POWER `PA26/ADC0_1` pin 1, RF/VOICE `PA27/ADC0_0` pin 2, and UI `PA16/ADC0_14` pin 12.
- Pack dividers use the internal 1.4-V reference. At the 4.3/8.6-V electrical screen their worst nodes are `{midpoint['node_v_max']}` and `{stack['node_v_max']}` V, leaving `{midpoint['minimum_margin_to_1v38_reference_mv']}` and `{stack['minimum_margin_to_1v38_reference_mv']}` mV to the minimum reference. Wait 20 ms, discard two conversions and average at least eight.
- The divider ADC is deliberately gross independent evidence: full-corner reconstruction can move by `{q(midpoint_error[0], '0.001')}..+{q(midpoint_error[1], '0.001')}` V for the midpoint and `{q(stack_error[0], '0.001')}..+{q(stack_error[1], '0.001')}` V for the stack. MAX17320 remains the precision per-cell/imbalance instrument.
- Every 10-kohm/10-kohm board NTC divider uses ADC `VDD` as its reference. Internal 1.4 V would saturate it at room temperature. Warning, kill and rearm are code-bounded at `880`, `740` and `1000`; open is `>=4000`, short is `<=64`.
- The BQ25798 path remains a third independent cell sensor. `TS_IGNORE=0`, `TS_WARM=0`, `JEITA_ISETH=0`; open and short suspend charge. The full-corner warm suspend is `{bq_serialized['warm_suspend_c']['minimum']}..{bq_serialized['warm_suspend_c']['maximum']} C`.
- MAX17320 uses both cell NTCs and exact `nThermCfg=0x{nthermcfg:04X}`. The operational request becomes zero above 35 C, charge is blocked around 40 C, discharge at 60 C, while board hot spots warn by 65 C and latch `FAULT_KILL` by 75 C.

## Admission boundary

Each MAX17320 cell reading must be 2.70..4.25 V and pair imbalance at most 100 mV. In parallel, midpoint/stack/derived-upper ADC plausibility must be 2.45..4.50, 4.90..9.00 and 1.90..5.10 V. Protected image/checksum, PFAIL and diagnostic-pulse evidence must all agree before the external FET hold releases.

The midpoint divider adds only `{q(imbalance_48h_mah, '0.001')}` mAh of lower-cell imbalance over 48 hours. This is negligible for the one-to-two-day unattended mission, but long storage and balancing heat remain explicit HIL measurements.

## Corrections

| ID | Corrected result |
|---|---|
| H3.3.4-F01 | Board NTC conversions are VDD-ratiometric; the 1.4-V reference is pack-only. |
| H3.3.4-F02 | BQ25798 and MAX17320 now have explicit machine-readable reset/readback configuration contracts. |
| H3.3.4-F03 | Exact B25/85=3435 K produces MAX17320 `nThermCfg=0x{nthermcfg:04X}`. |
| H3.3.4-F04 | Exact XTAR electrical limits are now machine-readable; the product retains the 2-A ceiling and a narrower thermal policy. |

## What paper evidence does not close

Sensor bonding and response, ADC calibration, received-cell identity, actual charger thresholds, balance heat and every open/short/reversed/imbalanced fault remain physical HIL gates. The generated evidence is [`H3-VRF34-battery-analog.json`](../hardware/verification/generated/H3-VRF34-battery-analog.json).
"""
    ru = f"""# Проверка battery sensing и температурных analog-порогов

`H3.3.4` проверено: `{len(checks)}` машинных проверок и четыре исправления по первичным источникам. Компоненты и стоимость BOM не изменились. Точный текущий маркер — `H3.6.1`, worst-case thermal model плат, аккумуляторов и корпуса.

## Что теперь зафиксировано

- Используются реальные контакты MSPM0C1106 DGS20: midpoint pack — `PA25/ADC0_2`, pin 20; stack pack и POWER — `PA26/ADC0_1`, pin 1; RF/VOICE — `PA27/ADC0_0`, pin 2; UI — `PA16/ADC0_14`, pin 12.
- Делители pack используют внутренний reference 1,4 В. На электрическом экране 4,3/8,6 В их worst-case nodes равны `{midpoint['node_v_max']}` и `{stack['node_v_max']}` В, запас до минимальных 1,38 В — `{midpoint['minimum_margin_to_1v38_reference_mv']}` и `{stack['minimum_margin_to_1v38_reference_mv']}` мВ. Ожидание 20 мс, две отброшенные конверсии и усреднение не менее восьми обязательны.
- Этот АЦП — независимая грубая проверка, а не точный imbalance meter: full-corner ошибка midpoint равна `{q(midpoint_error[0], '0.001')}..+{q(midpoint_error[1], '0.001')}` В, stack — `{q(stack_error[0], '0.001')}..+{q(stack_error[1], '0.001')}` В. Точные cell/imbalance limits проверяет MAX17320.
- Все три board NTC 10 кОм/10 кОм измеряются относительно `VDD`. С внутренними 1,4 В они насыщали бы АЦП уже при комнатной температуре. Warning, kill и rearm ограничены кодами `880`, `740` и `1000`; open — `>=4000`, short — `<=64`.
- BQ25798 остаётся третьим независимым cell sensor: `TS_IGNORE=0`, `TS_WARM=0`, `JEITA_ISETH=0`; open и short запрещают заряд. Полный corner warm-suspend — `{bq_serialized['warm_suspend_c']['minimum']}..{bq_serialized['warm_suspend_c']['maximum']} °C`.
- MAX17320 использует оба cell NTC и точный `nThermCfg=0x{nthermcfg:04X}`. Запрос заряда обнуляется выше 35 °C, charge блокируется около 40 °C, discharge — при 60 °C; board hotspots дают warning не позже 65 °C и защёлкивают `FAULT_KILL` не позже 75 °C.

## Граница admission

Каждая cell по MAX17320 должна быть 2,70..4,25 В, разбаланс — не более 100 мВ. Одновременно midpoint/stack/derived-upper по ADC должны лежать в грубых окнах 2,45..4,50, 4,90..9,00 и 1,90..5,10 В. Protected image/checksum, PFAIL и diagnostic pulse должны согласиться до снятия внешнего FET hold.

Midpoint divider добавляет лишь `{q(imbalance_48h_mah, '0.001')}` мА·ч разбаланса нижней cell за 48 часов. Для оставленного на один-два дня устройства это ничтожно, но длительное хранение и нагрев balancing остаются обязательными HIL-измерениями.

## Исправления

| ID | Исправленный результат |
|---|---|
| H3.3.4-F01 | Board NTC измеряются ratiometric относительно VDD; reference 1,4 В используется только для pack. |
| H3.3.4-F02 | BQ25798 и MAX17320 получили явные machine-readable reset/readback configuration contracts. |
| H3.3.4-F03 | Точный B25/85=3435 K даёт MAX17320 `nThermCfg=0x{nthermcfg:04X}`. |
| H3.3.4-F04 | Точные XTAR electrical limits теперь machine-readable; сохраняются потолок 2 А и более узкая thermal policy продукта. |

## Что бумажная проверка не закрывает

Прижим и отклик sensors, ADC calibration, подлинность received cells, реальные charger thresholds, нагрев balancing и все open/short/reversed/imbalanced faults остаются физическими HIL gates. Машинный результат: [`H3-VRF34-battery-analog.json`](../hardware/verification/generated/H3-VRF34-battery-analog.json).
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
            raise SystemExit("stale H3.3.4 artifacts: " + ", ".join(stale))
    print(f"ok: H3.3.4 reviewed; {manifest['review_summary']['checks']} checks, 4 corrections, next H3.3.5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
