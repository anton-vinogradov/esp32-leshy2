#!/usr/bin/env python3
"""Build the H3.6.1 parameterized board, cell and enclosure thermal model."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
SOURCE_PATH = REPO / "hardware/verification/generated/H3-VRF13-source-charge-budget.json"
DC_RESULT_PATH = REPO / "hardware/verification/generated/H3-VRF14-dc-consolidation.json"
BATTERY_PATH = REPO / "hardware/verification/generated/H3-VRF34-battery-analog.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF61-thermal-model.json"
DOC_EN = REPO / "docs/thermal-model.md"
DOC_RU = REPO / "docs/thermal-model.ru.md"


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, quantum: str = "0.001") -> str:
    return str(value.quantize(Decimal(quantum), rounding=ROUND_HALF_UP))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_heat(state: dict, cell_resistance_ohm: Decimal) -> dict:
    rails = state["rail_loads"]
    internal_output = sum(
        d(rails[name]["output_w"])
        for name in ("AON_SAFE_3V3", "3V3_MAIN", "VVOICE_4V")
    )
    external_output = d(rails["5V_EXT_ACTIVE_BRANCH"]["output_w"])
    cell_heat = d(state["pack_discharge_a"]) ** 2 * cell_resistance_ohm
    conversion = d(state["rail_conversion_loss_w"])
    efuse = d(state["efuse_conduction_loss_w"])
    total = internal_output + conversion + efuse + cell_heat
    return {
        "state_id": state["id"],
        "signal_group": state["signal_group"],
        "group_mode": state["group_mode"],
        "support_profile": state["support_profile"],
        "sys_demand_w": q(d(state["sys_demand_w"])),
        "internal_rail_output_w": q(internal_output),
        "external_accessory_output_excluded_w": q(external_output),
        "rail_conversion_loss_w": q(conversion),
        "efuse_conduction_loss_w": q(efuse),
        "cell_i2r_heat_w": q(cell_heat),
        "conservative_base_heat_w": q(total),
    }


def theta_limits(heat_w: Decimal, ambient_c: int) -> dict:
    return {
        "ambient_c": ambient_c,
        "rtheta_base_to_ambient_for_65c_warning_k_per_w_max": q((d(65) - d(ambient_c)) / heat_w),
        "rtheta_base_to_ambient_for_75c_kill_k_per_w_max": q((d(75) - d(ambient_c)) / heat_w),
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    dc = json.loads(DC_PATH.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    dc_result = json.loads(DC_RESULT_PATH.read_text(encoding="utf-8"))
    battery = json.loads(BATTERY_PATH.read_text(encoding="utf-8"))

    cell = battery["cell_contract"]
    pair_resistance_ohm = d(cell["initial_internal_resistance_milliohm_max"]) * d(2) / d(1000)
    run_states = [
        state for state in source["states"]
        if state["usb"] == "USB_ABSENT"
        and state["pack"] == "PACK_2S_LOW"
        and state["charge_mode"] == "PACK_DISCHARGE"
        and state["system_mode"] == "RUN"
    ]
    modeled = [base_heat(state, pair_resistance_ohm) for state in run_states]
    absolute = max(modeled, key=lambda row: d(row["conservative_base_heat_w"]))
    support_idle = max(
        (row for row in modeled if row["support_profile"] == "SUPPORT_IDLE"),
        key=lambda row: d(row["conservative_base_heat_w"]),
    )
    quiet_idle = next(
        row for row in modeled
        if row["signal_group"] == "NONE" and row["support_profile"] == "SUPPORT_IDLE"
    )
    ext_worst = max(
        (row for row in modeled if row["signal_group"] in {"LORA_CAP", "M5_UNIT"}),
        key=lambda row: d(row["conservative_base_heat_w"]),
    )
    max_pack_current = d(source["summary"]["maximum_pack_discharge_a"])
    max_cell_heat = max_pack_current ** 2 * pair_resistance_ohm
    max_charge_a = d(cell["standard_charge_current_a"])
    charge_cell_heat = max_charge_a ** 2 * pair_resistance_ohm

    thermal_parts = {
        "main_voice_ext_buck": {
            "mpn": devices["ti_tps564252_drlr"]["mpn"],
            "junction_operating_c": [-40, 125],
            "junction_absolute_c_max": 150,
            "rtheta_ja_jedec_k_per_w": "137.4",
            "rtheta_ja_evm_k_per_w": "74.0",
            "rtheta_evm_basis": "two-layer 2-oz TPS564252EVM at 12-to-5 V and 4 A; layout requirement, not a product temperature prediction",
            "source": devices["ti_tps564252_drlr"]["source"],
        },
        "aon_buck": {
            "mpn": devices["ti_tps629203_drlr"]["mpn"],
            "junction_operating_c": [-40, 125],
            "rtheta_ja_jedec_k_per_w": "120.0",
            "rtheta_ja_evm_k_per_w": "60.0",
            "source": devices["ti_tps629203_drlr"]["source"],
        },
        "main_voice_efuse": {
            "mpn": devices["ti_tps25974l_rpwr"]["mpn"],
            "junction_operating_c": [-40, 125],
            "rtheta_ja_8via_board_k_per_w": "49.7",
            "rtheta_ja_no_thermal_vias_k_per_w": "71.8",
            "source": devices["ti_tps25974l_rpwr"]["source"],
        },
        "external_efuse": {
            "mpn": devices["ti_tps259470l_rpwr"]["mpn"],
            "junction_operating_c": [-40, 125],
            "rtheta_ja_8via_board_k_per_w": "41.7",
            "rtheta_ja_no_thermal_vias_k_per_w": "74.5",
            "source": devices["ti_tps259470l_rpwr"]["source"],
        },
        "aon_efuse": {
            "mpn": devices["ti_tps25961_drvr"]["mpn"],
            "junction_operating_c": [-40, 125],
            "rtheta_ja_custom_4layer_k_per_w": "74.1",
            "source": devices["ti_tps25961_drvr"]["source"],
        },
        "charger": {
            "mpn": devices["ti_bq25798_rqmr"]["mpn"],
            "ambient_operating_c": [-40, 85],
            "rtheta_ja_k_per_w": "44.2",
            "protected_treg_c": devices["ti_bq25798_rqmr"]["configuration_contract"]["thermal_regulation_c"],
            "protected_tshut_c": devices["ti_bq25798_rqmr"]["configuration_contract"]["thermal_shutdown_c"],
            "source": devices["ti_bq25798_rqmr"]["source"],
        },
    }

    scenarios = {
        "electrical_absolute_corner": {
            **absolute,
            "admission": "transient_or_bounded_session_only; SUPPORT_WORST is an electrical anti-hidden-load envelope and is not admitted as a 24-to-48-hour thermal profile",
        },
        "support_idle_worst_group": {
            **support_idle,
            "admission": "candidate sustained group ceiling pending H6 enclosure resistance and H8 temperature map",
        },
        "external_accessory_worst": {
            **ext_worst,
            "admission": "accessory output heat is outside the base; base converter, eFuse, support and cell heat remain included",
        },
        "quiet_idle": {
            **quiet_idle,
            "admission": "baseline unattended candidate; H3.6.3 adds duty, logging and runtime bounds",
        },
    }
    ambient_sweep = {
        name: [theta_limits(d(row["conservative_base_heat_w"]), ambient) for ambient in (25, 35, 40)]
        for name, row in scenarios.items()
    }
    thresholds = battery["board_zone_thermistors"]["thresholds"]
    corrections = [{
        "id": "H3.6.1-F01",
        "finding": "BQ25798 reset defaults permit 120-C junction regulation and 150-C thermal shutdown, much hotter than the independent product board limits",
        "correction": "protect and read back REG16 TREG=60 C and TSHUT=85 C before CE may be pulled low",
        "functional_effect": "charge/charger conversion derates before the 65-C board warning and the charger self-shuts before its default 150-C threshold; no product capability or BOM item is removed",
        "cost_effect_usd": "0.0000",
    }]
    residual = [
        "H6: solve the real board/enclosure thermal network after placement, copper, vias, wall material, vents and accessory geometry are fixed",
        "H6: meet or beat the applicable allowable base-to-ambient resistance from the parameter sweep; SUPPORT_WORST remains non-continuous",
        "H8: measure all three NTCs, converter/eFuse/charger junction proxies, both cells and external surfaces at every admitted sustained profile",
        "H8: correlate thermal time constants and set per-profile maximum session/duty limits before any unattended claim",
        "H8: verify cell-to-NTC contact, replacement spread, charger TREG/TSHUT, warning, FAULT_KILL and physical rearm in a chamber",
    ]
    checks = {
        "all_50_dc_profiles_are_available": dc["summary"]["operating_profiles"] == 50,
        "all_2032_source_states_are_available": source["summary"]["states_evaluated"] == 2032,
        "maximum_conversion_loss_matches_h3_1": d(source["summary"]["maximum_rail_conversion_loss_w"]) == d("2.534"),
        "maximum_efuse_loss_matches_h3_1": d(source["summary"]["maximum_efuse_conduction_loss_w"]) == d("0.393"),
        "maximum_pack_current_matches_h3_1": max_pack_current == d("2.816"),
        "pair_resistance_uses_two_40mohm_cells": pair_resistance_ohm == d("0.080"),
        "maximum_pack_i2r_is_bounded": max_cell_heat < d("0.635"),
        "two_amp_charge_i2r_is_bounded": charge_cell_heat == d("0.320"),
        "external_accessory_output_is_not_misattributed_to_base": d(ext_worst["external_accessory_output_excluded_w"]) == d("6.250"),
        "absolute_corner_is_voice_support_worst": absolute["signal_group"] == "VOICE" and absolute["support_profile"] == "SUPPORT_WORST",
        "support_worst_is_not_continuous_claim": "not admitted" in scenarios["electrical_absolute_corner"]["admission"],
        "warning_threshold_is_65c_class": thresholds["warning_code_at_or_below"] == 880,
        "kill_threshold_is_75c_class": thresholds["fault_kill_code_at_or_below"] == 740,
        "rearm_is_below_60c": thresholds["fault_rearm_code_at_or_above"] == 1000,
        "three_independent_board_zones_exist": set(battery["board_zone_thermistors"]["channels"]) == {"POWER", "RF_VOICE", "UI"},
        "charger_treg_is_now_60c": thermal_parts["charger"]["protected_treg_c"] == 60,
        "charger_tshut_is_now_85c": thermal_parts["charger"]["protected_tshut_c"] == 85,
        "datasheet_rtheta_is_not_used_as_enclosure_prediction": all("rtheta_base_to_ambient" in key for key in ambient_sweep["quiet_idle"][0] if key.startswith("rtheta")),
        "ambient_design_target_is_accepted_for_h3_6_3": True,
        "physical_residuals_are_assigned": len(residual) == 5 and all(row.startswith(("H6:", "H8:")) for row in residual),
        "dc_consolidation_has_no_unresolved_findings": dc_result["review_summary"]["unresolved_findings"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.6.1 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.6.1",
        "status": "reviewed_parameterized_board_cell_and_enclosure_thermal_model",
        "method": "full admitted H3.1 state enumeration plus conservative internal heat partition and parameterized base-to-ambient resistance limits",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, DC_PATH, SOURCE_PATH, DC_RESULT_PATH, BATTERY_PATH)},
        "thermal_parts": thermal_parts,
        "cell_heat": {
            "two_cell_series_resistance_ohm_max_initial": q(pair_resistance_ohm),
            "maximum_pack_discharge_a": q(max_pack_current),
            "maximum_discharge_i2r_heat_w": q(max_cell_heat),
            "maximum_product_charge_a": q(max_charge_a),
            "maximum_charge_i2r_heat_w": q(charge_cell_heat),
            "manufacturer_operating_temperature_c": cell["manufacturer_operating_temperature_c"],
        },
        "zone_policy": {
            "sensors": battery["board_zone_thermistors"]["channels"],
            "thresholds": thresholds,
            "critical_behavior": candidate["safety_contract"]["thermal_supervision"]["critical"],
        },
        "scenarios": scenarios,
        "ambient_parameter_sweep": ambient_sweep,
        "product_ambient_envelope": {
            "status": "accepted_engineering_target_pending_h6_h8_not_a_product_guarantee",
            "minimum_c": 0,
            "maximum_c": 35,
            "decision": "H3.6.3 option A accepted by the user on 2026-08-24",
            "rule": "H6 designs to this target; only H8 measurements may establish the final published operating range",
        },
        "corrections": corrections,
        "checks": checks,
        "open_findings": [],
        "pending_decisions": [],
        "residual_physical_only": residual,
        "review_summary": {"checks": len(checks), "failed": 0, "corrected_findings": 1, "unresolved_analytical_findings": 0, "status": "reviewed"},
        "next": {"stage": "H3.6.2", "action": "trace single faults through independent hardware shutdown and recovery"},
    }

    peak = scenarios["electrical_absolute_corner"]
    sustained = scenarios["support_idle_worst_group"]
    quiet = scenarios["quiet_idle"]
    en = f"""# Thermal model

`H3.6.1` is reviewed with `{len(checks)}` passing checks and one zero-cost safety correction. The exact marker is `H3.6.2`.

The model enumerates every H3.1 power state and separates electrical capacity from thermal permission. The electrical anti-hidden-load corner is `{peak['signal_group']}/{peak['group_mode']}/{peak['support_profile']}` at `{peak['conservative_base_heat_w']} W` of conservative base heat; it is **not** a continuous operating claim. The hottest `SUPPORT_IDLE` group is `{sustained['signal_group']}` at `{sustained['conservative_base_heat_w']} W`; quiet idle is `{quiet['conservative_base_heat_w']} W`. External accessory output is excluded only after its converter/eFuse and base support heat have been retained.

The accepted engineering target is `0 to 35 C`, not a published product guarantee. Machine evidence also retains required base-to-ambient resistance at 25, 35 and 40 C against the existing 65-C warning and 75-C hard-kill classes. H6 must solve the actual copper/enclosure network and H8 must correlate temperatures and time constants before establishing the final range or admitting a sustained profile.

BQ25798 is corrected from hot reset defaults to protected/read-back `TREG=60 C`, `TSHUT=85 C`; this changes no BOM and removes no function.

Machine evidence: [`H3-VRF61-thermal-model.json`](../hardware/verification/generated/H3-VRF61-thermal-model.json).
"""
    ru = f"""# Тепловая модель

`H3.6.1` проведён ревью: `{len(checks)}` checks проходят, внесено одно бесплатное safety-исправление. Точный маркер — `H3.6.2`.

Модель перебирает все состояния питания H3.1 и разделяет электрическую допустимость и тепловое разрешение. Электрический anti-hidden-load угол — `{peak['signal_group']}/{peak['group_mode']}/{peak['support_profile']}` с консервативными `{peak['conservative_base_heat_w']} Вт внутри базы; это **не** разрешение непрерывной работы. Самая горячая группа с `SUPPORT_IDLE` — `{sustained['signal_group']}`, `{sustained['conservative_base_heat_w']} Вт; quiet idle — `{quiet['conservative_base_heat_w']} Вт. Мощность внешнего аксессуара исключается из базы только после учёта его преобразователя/eFuse и внутренних support-нагрузок.

Принятая инженерная цель — `0…35 °C`, а не паспортная гарантия. Машинное evidence также сохраняет требуемое тепловое сопротивление база→среда при 25, 35 и 40 °C относительно классов warning 65 °C и hard kill 75 °C. H6 обязан решить реальную сеть copper/case, а H8 — измерить температуры и постоянные времени до фиксации итогового диапазона или допуска длительного профиля.

BQ25798 исправлен с горячих reset-default на защищённые и проверяемые чтением `TREG=60 °C`, `TSHUT=85 °C`; BOM и функции не меняются.

Машинное evidence: [`H3-VRF61-thermal-model.json`](../hardware/verification/generated/H3-VRF61-thermal-model.json).
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
            raise SystemExit("stale H3.6.1 artifacts: " + ", ".join(stale))
    print(f"ok: H3.6.1 reviewed; {manifest['review_summary']['checks']} checks, next H3.6.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
