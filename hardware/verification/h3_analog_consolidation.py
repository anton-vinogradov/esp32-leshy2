#!/usr/bin/env python3
"""Consolidate H3.3 display, audio, IR and battery analog evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
INPUTS = {
    "display": REPO / "hardware/verification/generated/H3-VRF31-display.json",
    "audio": REPO / "hardware/verification/generated/H3-VRF32-audio.json",
    "ir": REPO / "hardware/verification/generated/H3-VRF33-ir.json",
    "battery": REPO / "hardware/verification/generated/H3-VRF34-battery-analog.json",
}
OUTPUT = REPO / "hardware/verification/generated/H3-VRF35-analog-consolidation.json"
DOC_EN = REPO / "docs/analog-corner-result.md"
DOC_RU = REPO / "docs/analog-corner-result.ru.md"


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.0001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    rows = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    display, audio, ir, battery = (rows[name] for name in ("display", "audio", "ir", "battery"))

    check_counts = {name: len(row["checks"]) for name, row in rows.items()}
    correction_counts = {name: len(row["corrections"]) for name, row in rows.items()}
    total_checks = sum(check_counts.values())
    total_corrections = sum(correction_counts.values())
    total_cost = (
        d(display["cost_delta_usd_at_100"]["delta_per_board"])
        + d(audio["cost_delta_usd_at_100"]["total_delta_per_board"])
        + d(ir["cost_delta_usd_at_100"]["total_delta_per_board"])
        + d(battery["review_summary"]["new_bom_cost_usd"])
    )
    correction_ids = [finding["id"] for row in rows.values() for finding in row["corrections"]]
    hil = {
        "display": display["residual_physical_only"],
        "audio": audio["residual_physical_only"],
        "ir": ir["residual_physical_only"],
        "battery": battery["remaining_hil"],
    }

    midpoint_error = battery["pack_adc"]["full_corner_reconstruction_error_v"]["midpoint"]
    stack_error = battery["pack_adc"]["full_corner_reconstruction_error_v"]["stack"]
    upper_error = battery["pack_adc"]["full_corner_reconstruction_error_v"]["upper_cell_by_subtraction"]
    admission = battery["pack_adc"]["admission"]
    max_cell_low, max_cell_high = (d(value) for value in admission["max17320_each_cell_v"])
    stack_low, stack_high = max_cell_low * 2, max_cell_high * 2

    temperature_ladder = {
        "charge_request_zero_c": 35,
        "bq_warm_backup_full_corner_max_c": d(battery["charger_ts"]["full_corner_temperature_windows_c"]["warm_suspend_c"]["maximum"]),
        "speaker_mute_c": d(audio["speaker"]["speaker_operating_environment_c_max"]),
        "cell_discharge_block_c": d(battery["max17320"]["temperature_profile_c"]["discharge_hot_block"]),
        "board_warning_guaranteed_c": 65,
        "ir_local_tx_limit_c": d(ir["transmit"]["local_tx_temperature_limit_c"]),
        "board_fault_kill_guaranteed_c": 75,
    }
    checks = {
        "all_leaf_checks_pass": all(all(row["checks"].values()) for row in rows.values()),
        "all_leaf_stages_are_exact": [row["stage"] for row in rows.values()] == ["H3.3.1", "H3.3.2", "H3.3.3", "H3.3.4"],
        "all_leaf_review_statuses_are_closed": all(str(row["status"]).startswith("reviewed") for row in rows.values()),
        "display_has_no_open_findings": display["open_findings"] == [],
        "audio_has_no_open_findings": audio["open_findings"] == [],
        "ir_has_no_open_findings": ir["open_findings"] == [],
        "battery_reports_zero_failed_checks": battery["review_summary"]["failed"] == 0,
        "leaf_check_count_is_153": total_checks == 153,
        "correction_ids_are_unique": len(correction_ids) == len(set(correction_ids)),
        "fourteen_corrections_are_preserved": total_corrections == 14,
        "cost_delta_remains_below_half_dollar": total_cost < d("0.50"),
        "display_and_ir_use_same_main_rail_minimum": d(display["supply_corner"]["display_connector_v"]["min"]) == d(ir["transmit"]["main_rail_v"]["minimum"]),
        "main_rail_analytical_load_remains_at_or_below_budget": d(audio["main_rail_crosscheck"]["worst_profile_load_ma"]) <= d(2500),
        "display_quantum_is_at_most_one_ms": d(display["qspi_corner"]["maximum_nonpreemptible_quantum_ms"]) <= d(1),
        "ir_optical_trip_is_not_slower_than_mark_limit": "exceeds 20 ms" in ir["transmit"]["stuck_evidence_rule"] and ir["transmit"]["single_mark_ms_max"] == 20,
        "pack_midpoint_window_contains_full_corner_valid_cells": d(admission["adc_midpoint_plausibility_v"][0]) <= max_cell_low + d(midpoint_error["minimum"]) and d(admission["adc_midpoint_plausibility_v"][1]) >= max_cell_high + d(midpoint_error["maximum"]),
        "pack_stack_window_contains_full_corner_valid_pair": d(admission["adc_stack_plausibility_v"][0]) <= stack_low + d(stack_error["minimum"]) and d(admission["adc_stack_plausibility_v"][1]) >= stack_high + d(stack_error["maximum"]),
        "pack_upper_window_contains_subtraction_corner": d(admission["adc_upper_by_subtraction_plausibility_v"][0]) <= max_cell_low + d(upper_error["minimum"]) and d(admission["adc_upper_by_subtraction_plausibility_v"][1]) >= max_cell_high + d(upper_error["maximum"]),
        "temperature_ladder_is_monotonic": d(35) < temperature_ladder["bq_warm_backup_full_corner_max_c"] < temperature_ladder["speaker_mute_c"] < temperature_ladder["cell_discharge_block_c"] < d(65) < temperature_ladder["ir_local_tx_limit_c"] + d("0.001"),
        "ir_limit_does_not_exceed_board_kill": temperature_ladder["ir_local_tx_limit_c"] <= d(temperature_ladder["board_fault_kill_guaranteed_c"]),
        "all_seventeen_physical_residuals_are_preserved": sum(len(values) for values in hil.values()) == 17,
        "no_physical_residual_is_empty": all(value.strip() for values in hil.values() for value in values),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.3.5 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.3.5",
        "status": "reviewed_analog_corner_consolidation",
        "input_hashes": {str(path.relative_to(REPO)): sha256(path) for path in INPUTS.values()},
        "leaf_summary": {
            name: {"stage": row["stage"], "status": row["status"], "checks": check_counts[name], "corrections": correction_counts[name]}
            for name, row in rows.items()
        },
        "consolidated": {
            "leaf_checks": total_checks,
            "consolidation_checks": len(checks),
            "failed_checks": 0,
            "source_corrections": total_corrections,
            "unresolved_analytical_findings": 0,
            "bom_delta_usd_at_quantity_100": q(total_cost),
            "physical_hil_residuals": sum(len(values) for values in hil.values()),
        },
        "shared_rail_contract": {
            "display_and_ir_minimum_v": display["supply_corner"]["display_connector_v"]["min"],
            "analytical_main_load_ma": audio["main_rail_crosscheck"]["worst_profile_load_ma"],
            "main_budget_ma": "2500.000",
            "hardware_reserve_percent": audio["main_rail_crosscheck"]["hardware_reserve_percent"],
            "rule": "the 7-mA analytical allocation margin is not a production tolerance claim; H3.6 thermal and H8 measured current must remain <=2.5 A, otherwise current allowances or functionality are reopened before layout/order",
        },
        "temperature_precedence_c": {key: str(value) for key, value in temperature_ladder.items()},
        "timing_precedence": {
            "display_nonpreemptible_ms_max": display["qspi_corner"]["maximum_nonpreemptible_quantum_ms"],
            "ir_single_mark_ms_max": ir["transmit"]["single_mark_ms_max"],
            "ir_continuous_evidence_trip_ms": 20,
            "rule": "display work is sliced to <=1 ms and cannot defer the independent IR evidence trip; active-radio buses remain independent",
        },
        "physical_hil_residuals": hil,
        "checks": checks,
        "correction_ids": correction_ids,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.6.1", "action": "build the worst-case board, battery and enclosure thermal model"},
    }

    en = f"""# Consolidated analog-corner result

H3.3 is reviewed: all four leaf packages and `{total_checks}` leaf checks pass, followed by `{len(checks)}` consolidation checks. Fourteen source corrections are closed, no analytical finding remains open and the total quantity-100 BOM delta is only `{q(total_cost)} USD`. The exact current marker is `H3.6.1`.

## Closed analytical envelope

| Path | Reviewed result |
|---|---|
| Display | 3.108510..3.285658 V connector supply; 40-MHz initial QSPI; dirty/tile work sliced to <=1 ms |
| Audio | 4-ohm speaker corner, complete capture/playback/TX paths and 625-mA branch; playback mutes above 50 C |
| IR | >=20-mA characterized optical point, <=50.513-mA conservative instantaneous current, 20-ms mark/trip and 75-C local limit |
| Battery/thermal | exact DGS20 ADC contacts, independent MAX/BQ/ADC evidence, 35-C charge-request cutoff, 40-C charge block, 60-C cell-discharge block and 65/75-C board warning/kill |

The temperature rules are deliberately ordered: charge request zero at 35 C, BQ backup no later than 41.03 C, speaker mute at 50 C, cell discharge block at 60 C, board warning by 65 C and `FAULT_KILL`/IR local ceiling at 75 C. The display quantum is shorter than every safety deadline and no radio FIFO shares its bus.

## Shared-rail caveat

The enumerated 3V3_MAIN profile is `2493 mA` against a `2500 mA` analytical allocation. Its hardware protection reserve is still `{audio['main_rail_crosscheck']['hardware_reserve_percent']}%`, but the 7-mA paper gap is not manufacturing margin. H3.6 and H8 must measure <=2.5 A; an excess reopens allowances or functionality before layout or ordering.

## Physical boundary retained

All 17 physical-only items remain explicit HIL gates: display signal integrity/current/optics, audio gain/noise/acoustics/RF immunity, IR coupling/range/IEC 62471/temperature, and battery identity/calibration/sensor response/charge thresholds/balance heat. H3.3 does not turn those into paper passes.

Machine evidence: [`H3-VRF35-analog-consolidation.json`](../hardware/verification/generated/H3-VRF35-analog-consolidation.json).
"""
    ru = f"""# Сводный результат analog corners

`H3.3` проверено: проходят все четыре leaf-пакета, `{total_checks}` их checks и `{len(checks)}` сводных checks. Закрыты четырнадцать source-исправлений, незакрытых аналитических findings нет, суммарная дельта BOM на количестве 100 — лишь `{q(total_cost)} USD`. Точный текущий маркер — `H3.6.1`.

## Закрытый аналитический envelope

| Тракт | Проверенный результат |
|---|---|
| Display | 3,108510..3,285658 В на connector; начальные 40 МГц QSPI; dirty/tile работа нарезана на <=1 мс |
| Audio | corner 4-омного speaker, полные capture/playback/TX paths и ветка 625 мА; playback выключается выше 50 °C |
| IR | >=20 мА гарантированного characterization point, <=50,513 мА conservative instantaneous current, mark/trip 20 мс и local limit 75 °C |
| Battery/thermal | точные DGS20 ADC contacts, независимые MAX/BQ/ADC evidence, отключение запроса заряда при 35 °C, charge block 40 °C, cell-discharge block 60 °C и board warning/kill 65/75 °C |

Температурные правила намеренно упорядочены: нулевой запрос заряда при 35 °C, BQ backup не позже 41,03 °C, mute динамика при 50 °C, блок discharge cell при 60 °C, warning платы не позже 65 °C и `FAULT_KILL`/IR ceiling при 75 °C. Display quantum короче каждого safety deadline, и ни один radio FIFO не делит с ним bus.

## Оговорка общей шины

Перечисленный профиль 3V3_MAIN равен `2493 мА` при аналитическом allowance `2500 мА`. Аппаратный reserve защиты остаётся `{audio['main_rail_crosscheck']['hardware_reserve_percent']}%`, но бумажные 7 мА — не производственный допуск. H3.6 и H8 должны измерить <=2,5 А; превышение до layout или заказа повторно открывает allowances либо функции.

## Сохранённая физическая граница

Все 17 physical-only пунктов остаются HIL gates: signal integrity/current/optics дисплея; gain/noise/acoustics/RF immunity audio; coupling/range/IEC 62471/temperature IR; identity/calibration/sensor response/charge thresholds/balance heat аккумуляторов. H3.3 не превращает их в бумажные passes.

Машинное evidence: [`H3-VRF35-analog-consolidation.json`](../hardware/verification/generated/H3-VRF35-analog-consolidation.json).
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
            raise SystemExit("stale H3.3.5 artifacts: " + ", ".join(stale))
    print(f"ok: H3.3 reviewed; {manifest['consolidated']['leaf_checks']} leaf + {manifest['consolidated']['consolidation_checks']} consolidation checks, next H3.6.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
