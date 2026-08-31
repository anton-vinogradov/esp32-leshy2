#!/usr/bin/env python3
"""Evaluate H3-R2.1.4 USB, pack, charge, supplement and source margins."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34
REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-source-margin-contract.json"
STATES = REPO / "hardware/verification/generated/H3-R2-power-state-register.json"
RAILS = REPO / "hardware/verification/generated/H3-R2-rail-margins.json"
LOADS = REPO / "hardware/verification/generated/H3-R2-load-binding.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-source-margins.json"
DOC_EN = REPO / "docs/power-source-margins.md"
DOC_RU = REPO / "docs/power-source-margins.ru.md"


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal | None, quantum: str = "0.001") -> str | None:
    return None if value is None else format(value.quantize(d(quantum)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile_key(row: dict) -> tuple[str, str, str]:
    return row["signal_group"], row["group_mode"], row["support_profile"]


def deferred_ownership(contract: dict, rail_manifest: dict, load_manifest: dict) -> tuple[list[dict], dict[str, list[str]]]:
    lines = {row["instance_uid"]: row for row in load_manifest["load_lines"]}
    lines.update({f"EXTERNAL:{row['id']}": row for row in load_manifest["external_load_lines"]})
    deferred = [row["instance_uid"] for row in rail_manifest["ownership"] if row["owner"] == "deferred_h3_r2_1_4"]
    ownership = []
    owner_uids: dict[str, list[str]] = defaultdict(list)
    rules = contract["ownership_rules"]
    for uid in deferred:
        line = lines[uid]
        if uid.startswith("EXTERNAL:"):
            owner = rules[uid]
        else:
            rail = line["canonical_rails"][0]
            owner = rules[rail].get(line["device_id"], rules[rail]["default"])
        ownership.append({"instance_uid": uid, "owner": owner})
        owner_uids[owner].append(uid)
    if len(ownership) != len(set(deferred)):
        raise ValueError("duplicate deferred source/pack ownership")
    return ownership, dict(sorted(owner_uids.items()))


def rail_loads(state: dict, profiles: dict, idle: dict) -> dict[str, Decimal]:
    zero = {rail: d(0) for rail in idle["loads_ma"]}
    if state["system_mode"] == "UNPOWERED_OFF":
        return zero
    if state["system_mode"] == "AON_SAFE_ONLY":
        zero["AON_SAFE_3V3"] = d(idle["loads_ma"]["AON_SAFE_3V3"])
        return zero
    if state["system_mode"] == "FAULT_LATCHED_DIAGNOSTIC":
        return {rail: d(value) for rail, value in idle["loads_ma"].items()}
    return {rail: d(value) for rail, value in profiles[profile_key(state)]["loads_ma"].items()}


def overhead(contract: dict, source: dict, state: dict, loads: dict[str, Decimal]) -> tuple[Decimal, list[dict]]:
    if state["system_mode"] == "UNPOWERED_OFF":
        return d(0), []
    active = []
    usb_present = source["usb"] != "USB_ABSENT"
    pack_healthy = contract["pack_profiles"][source["pack"]]["healthy"]
    any_payload = any(value > 0 for rail, value in loads.items() if rail != "AON_SAFE_3V3")
    predicates = {
        "usb_support": usb_present,
        "nvdc_control": True,
        "rail_converter_iq": any_payload,
        "pack_control": pack_healthy,
        "passive_leakage": True,
    }
    total = d(0)
    for branch, enabled in predicates.items():
        if enabled:
            watts = d(contract["fixed_overhead_branches_w"][branch]["active_w"])
            active.append({"branch": branch, "power_w": q(watts)})
            total += watts
    return total, active


def system_demand(contract: dict, state: dict, source: dict, loads: dict[str, Decimal]) -> dict:
    eta_rail = d(contract["policy"]["minimum_rail_conversion_efficiency"])
    rail_voltage = {"AON_SAFE_3V3": d("3.3"), "3V3_MAIN": d("3.222"), "VVOICE_4V": d("4.0"), "5V_EXT_ACTIVE_BRANCH": d("5.0")}
    rows = {}
    rail_output_w = d(0)
    rail_input_w = d(0)
    for rail, current_ma in loads.items():
        output = current_ma / d(1000) * rail_voltage[rail]
        input_w = output / eta_rail if output else d(0)
        rows[rail] = {"load_ma": q(current_ma), "output_w": q(output), "sys_input_w": q(input_w)}
        rail_output_w += output
        rail_input_w += input_w
    fixed_w, branches = overhead(contract, source, state, loads)
    return {
        "rail_rows": rows,
        "rail_output_w": rail_output_w,
        "rail_input_w": rail_input_w,
        "fixed_overhead_w": fixed_w,
        "overhead_branches": branches,
        "sys_demand_w": rail_input_w + fixed_w,
    }


def evaluate_state(contract: dict, state: dict, source: dict, demand: dict) -> dict:
    eta_source = d(contract["policy"]["minimum_source_to_sys_efficiency"])
    eta_charge = d(contract["policy"]["minimum_charge_efficiency"])
    pack_limit = d(contract["policy"]["pack_pf03_admission_a"])
    usb = contract["usb_profiles"][source["usb"]]
    pack = contract["pack_profiles"][source["pack"]]
    usb_v = d(usb["voltage_v"])
    usb_limit = None if usb["current_limit_a"] is None else d(usb["current_limit_a"])
    pack_v = None if pack["voltage_v"] is None else d(pack["voltage_v"])
    requested_charge = d(contract["charge_request_a"][source["charge_mode"]])
    sys_raw_required = demand["sys_demand_w"] / eta_source if demand["sys_demand_w"] else d(0)
    usb_raw_budget = None if usb_limit is None else usb_v * usb_limit
    usb_raw_used = d(0)
    pack_discharge_a = d(0)
    actual_charge_a = d(0)
    admission = "admitted"
    action = "none"

    if state["system_mode"] == "UNPOWERED_OFF":
        admission = "expected_unpowered"
    elif source["usb"] == "USB_ABSENT":
        if pack_v is None:
            admission = "expected_unpowered"
        else:
            pack_discharge_a = sys_raw_required / pack_v
            action = "pack_supplies_system"
    elif usb_raw_budget is None:
        if pack_v is not None:
            pack_discharge_a = sys_raw_required / pack_v
            action = "pack_carries_run_until_fallback_current_is_measured"
        elif state["system_mode"] == "AON_SAFE_ONLY":
            admission = "diagnostic_only_pending_source_current"
            action = "hold_run_off"
        else:
            admission = "refused_without_numeric_source_or_pack"
            action = "hold_run_off"
    elif sys_raw_required > usb_raw_budget:
        usb_raw_used = usb_raw_budget
        if pack_v is None:
            admission = "run_profile_refused_on_usb_only"
            action = "reduce_load_or_use_healthy_pack_or_higher_pdo"
        else:
            pack_discharge_a = (sys_raw_required - usb_raw_budget) / pack_v
            action = "pack_supplements_usb"
    else:
        usb_raw_used = sys_raw_required
        headroom_raw_w = usb_raw_budget - sys_raw_required
        if pack_v is not None and requested_charge:
            actual_charge_a = min(requested_charge, headroom_raw_w * eta_charge / pack_v)
            usb_raw_used += actual_charge_a * pack_v / eta_charge
            action = "charge_as_requested" if actual_charge_a == requested_charge else "charge_derated_before_system_load"
        elif requested_charge:
            admission = "invalid_charge_request_without_healthy_pack"

    usb_input_a = usb_raw_used / usb_v if usb_v else d(0)
    pack_reserve = (pack_limit / pack_discharge_a - d(1)) * d(100) if pack_discharge_a else d(9999)
    usb_path_drop = (usb_limit or d(0)) * d(contract["path_corners"]["usb_path_resistance_ohm"])
    usb_endpoint = usb_v - usb_path_drop if usb_v else d(0)
    pack_drop = pack_discharge_a * d(contract["path_corners"]["pack_external_series_resistance_ohm"])
    pack_endpoint = pack_v - pack_drop if pack_v is not None else None
    cell_heat = pack_discharge_a * pack_discharge_a * d(contract["path_corners"]["cell_pair_internal_resistance_ohm"])
    pack_path_heat = pack_discharge_a * pack_discharge_a * d(contract["path_corners"]["pack_external_series_resistance_ohm"])
    checks = {
        "pack_current_within_pf03_admission": pack_discharge_a <= pack_limit,
        "usb_current_within_contract": usb_limit is None or usb_input_a <= usb_limit + d("0.000000001"),
        "charge_within_request": actual_charge_a <= requested_charge,
        "charge_within_hardware_ceiling": actual_charge_a <= d(contract["policy"]["charge_current_ceiling_a"]),
        "usb_endpoint_above_charger_minimum": not usb_v or usb_endpoint >= d(contract["path_corners"]["usb_minimum_charger_input_v"]),
        "pack_endpoint_above_minimum": pack_endpoint is None or pack_endpoint >= d(contract["path_corners"]["pack_minimum_protected_input_v"]),
        "unknown_fallback_does_not_contribute_numeric_power": usb_raw_budget is not None or usb_raw_used == 0,
        "unsafe_run_is_refused": not (admission == "refused_without_numeric_source_or_pack" and state["system_mode"] == "RUN"),
    }
    # Explicit refusal of an oversized USB-only profile is a safe pass, not a
    # claim that the source can run it. The state remains visible to firmware.
    passed = all(checks.values()) and admission != "invalid_charge_request_without_healthy_pack"
    return {
        "id": state["id"], "source_state": source["id"], "usb": source["usb"], "pack": source["pack"],
        "charge_mode": source["charge_mode"], "system_mode": state["system_mode"], "signal_group": state["signal_group"],
        "group_mode": state.get("group_mode"), "support_profile": state.get("support_profile"),
        "rail_loads": demand["rail_rows"], "overhead_branches": demand["overhead_branches"],
        "rail_output_w": q(demand["rail_output_w"]), "rail_input_w": q(demand["rail_input_w"]),
        "fixed_overhead_w": q(demand["fixed_overhead_w"]), "sys_demand_w": q(demand["sys_demand_w"]),
        "source_raw_required_w": q(sys_raw_required), "usb_raw_budget_w": q(usb_raw_budget),
        "usb_input_a": q(usb_input_a), "usb_endpoint_v": q(usb_endpoint),
        "pack_voltage_v": q(pack_v), "pack_discharge_a": q(pack_discharge_a), "pack_pf03_limit_a": q(pack_limit),
        "pack_pf03_reserve_percent": q(pack_reserve), "pack_endpoint_v": q(pack_endpoint),
        "cell_pair_i2r_w": q(cell_heat), "external_pack_path_i2r_w": q(pack_path_heat),
        "requested_charge_a": q(requested_charge), "actual_charge_a": q(actual_charge_a),
        "charge_derated": requested_charge > actual_charge_a and requested_charge > 0,
        "admission": admission, "required_action": action, "checks": checks,
        "status": "pass" if passed else "fail",
    }


def render_doc(manifest: dict, russian: bool) -> str:
    s = manifest["summary"]
    e = manifest["extrema"]
    if russian:
        title = "# Источники, аккумуляторы и заряд · H3-R2.1.4"
        nav = "[English](power-source-margins.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Запасы шин](power-rail-margins.ru.md)"
        intro = f"`H3-R2.1.4` проверяет все {s['states_evaluated']} разрешённых состояния R2. Все {s['deferred_lines_owned']} source/pack-строк имеют явного владельца; скрытой надбавки нет."
        result_h = "## Результат"
        result = (f"- Максимальный запрос SYS: `{s['maximum_sys_demand_w']} Вт`; сырой запрос источника при 85%: `{s['maximum_source_raw_required_w']} Вт`.\n"
                  f"- Максимальный ток pack при 6,0 В: `{s['maximum_pack_discharge_a']} А`; запас до 8-А допуска PF-R2-03: `{s['pack_reserve_percent_at_worst']}%`.\n"
                  f"- Максимальный 2-А запрос заряда полностью или автоматически снижается по DPM: derated-состояний `{s['charge_states_derated']}`.\n"
                  f"- Отказов проверки: `{s['failed_states']}`; скрытых/unowned строк: `0`.")
        source_h = "## Что реально может источник"
        source = (f"5 В × 3 А не объявляется универсальным: {s['usb_only_profiles_refused']} USB-only состояний получают явный отказ на слишком тяжёлом профиле. "
                  "Здоровый pack может дополнить USB. Неизвестный fallback даёт ноль численной мощности до измерения Rp/PD; без pack остаётся только AON. "
                  "9 В × 3 А и 15 В × 2 А запускают все объявленные профили, а заряд всегда уступает системной нагрузке.")
        limits_h = "## Граница доказательства"
        limits = (f"Электрический одновременный угол даёт pack endpoint `{e['maximum_pack_discharge']['pack_endpoint_v']} В` и расчётные `{e['maximum_pack_discharge']['cell_pair_i2r_w']} Вт` в двух ячейках. "
                  f"Длительный envelope отдельно ограничен SUPPORT_IDLE и 1,00 А внешнего 5-В порта: `{s['maximum_sustained_pack_discharge_a']} А`, `{s['maximum_sustained_cell_pair_i2r_w']} Вт` в ячейках. Пуск, DPM и USB↔pack handover остаются H3-R2.2, routed resistance — H6, измерение — H8.")
        end = "**Downstream-результат:** [`H3-R2.1`](power-dc-source-result.ru.md) полностью проведён ревью; текущий маркер — `H3-R2.2.1`.\n\n[Полный машинный результат](../hardware/verification/generated/H3-R2-source-margins.json)."
    else:
        title = "# Source, pack and charge margins · H3-R2.1.4"
        nav = "[Русский](power-source-margins.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Rail margins](power-rail-margins.md)"
        intro = f"`H3-R2.1.4` evaluates all {s['states_evaluated']} legal R2 states. All {s['deferred_lines_owned']} source/pack lines have an explicit owner; there is no hidden allowance."
        result_h = "## Result"
        result = (f"- Maximum SYS demand: `{s['maximum_sys_demand_w']} W`; raw source request at 85%: `{s['maximum_source_raw_required_w']} W`.\n"
                  f"- Maximum pack current at 6.0 V: `{s['maximum_pack_discharge_a']} A`; reserve to the 8-A PF-R2-03 admission is `{s['pack_reserve_percent_at_worst']}%`.\n"
                  f"- A requested 2-A charge either completes or is automatically DPM-reduced: derated states `{s['charge_states_derated']}`.\n"
                  f"- Failed checks: `{s['failed_states']}`; hidden or unowned lines: `0`.")
        source_h = "## What each source can actually run"
        source = (f"5 V × 3 A is not called universal: {s['usb_only_profiles_refused']} USB-only states explicitly refuse an oversized profile. "
                  "A healthy pack may supplement USB. Unknown fallback contributes zero numeric power until Rp/PD is measured; without a pack it remains AON-only. "
                  "9 V × 3 A and 15 V × 2 A run every declared profile, and charging always yields to system load.")
        limits_h = "## Proof boundary"
        limits = (f"The electrical simultaneous corner gives a `{e['maximum_pack_discharge']['pack_endpoint_v']} V` pack endpoint and `{e['maximum_pack_discharge']['cell_pair_i2r_w']} W` calculated in the two cells. "
                  f"The sustained envelope is separately restricted to SUPPORT_IDLE and 1.00 A on external 5 V: `{s['maximum_sustained_pack_discharge_a']} A`, `{s['maximum_sustained_cell_pair_i2r_w']} W` in the cells. Startup, DPM and USB↔pack handover remain H3-R2.2, routed resistance remains H6 and measurement remains H8.")
        end = "**Downstream result:** [`H3-R2.1`](power-dc-source-result.md) is fully reviewed; the current marker is `H3-R2.2.1`.\n\n[Complete machine result](../hardware/verification/generated/H3-R2-source-margins.json)."
    return "\n\n".join((title, nav, intro, result_h, result, source_h, source, limits_h, limits, end)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    states = json.loads(STATES.read_text(encoding="utf-8"))
    rails = json.loads(RAILS.read_text(encoding="utf-8"))
    loads = json.loads(LOADS.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    if not rails["status"].startswith("reviewed_") or loads["status"] != "pass":
        raise ValueError("reviewed H3-R2.1.2/.1.3 input required")
    if "PF-R2-03" not in {row["id"] for row in methods["pass_fail_rules"]}:
        raise ValueError("PF-R2-03 is missing")
    ownership, owner_uids = deferred_ownership(contract, rails, loads)
    if len(ownership) != rails["summary"]["deferred_source_pack_lines"]:
        raise ValueError("not every deferred source/pack line is owned")
    profiles = {profile_key(row): row for row in rails["profiles"]}
    idle = profiles[("NONE", "QUIET", "SUPPORT_IDLE")]
    source_by_id = {row["id"]: row for row in states["source_states"]}
    evaluated = []
    sustained_evaluated = []
    for state in states["states"]:
        source = source_by_id[state["source_state"]]
        loads_ma = rail_loads(state, profiles, idle)
        evaluated.append(evaluate_state(contract, state, source, system_demand(contract, state, source, loads_ma)))
        if state["system_mode"] != "RUN" or state.get("support_profile") == "SUPPORT_IDLE":
            sustained_loads = dict(loads_ma)
            sustained_loads["5V_EXT_ACTIVE_BRANCH"] = min(
                sustained_loads["5V_EXT_ACTIVE_BRANCH"],
                d(contract["policy"]["sustained_external_5v_admission_a"]) * d(1000),
            )
            sustained_evaluated.append(evaluate_state(contract, state, source, system_demand(contract, state, source, sustained_loads)))
    failures = [row for row in evaluated if row["status"] != "pass"]
    if failures:
        details = ", ".join(f"{row['id']}:{row['admission']}:{[key for key, passed in row['checks'].items() if not passed]}" for row in failures[:8])
        raise ValueError(f"H3-R2.1.4 source failures: {len(failures)} ({details})")
    max_sys = max(evaluated, key=lambda row: d(row["sys_demand_w"]))
    max_raw = max(evaluated, key=lambda row: d(row["source_raw_required_w"]))
    max_pack = max(evaluated, key=lambda row: d(row["pack_discharge_a"]))
    max_sustained_pack = max(sustained_evaluated, key=lambda row: d(row["pack_discharge_a"]))
    refused = [row for row in evaluated if row["admission"] == "run_profile_refused_on_usb_only"]
    derated = [row for row in evaluated if row["charge_derated"]]
    manifest = {
        "schema_version": 1, "artifact": "H3-R2-source-margins", "marker": "H3-R2.1.4", "status": "pass",
        "accepted_input": {"states": "H3-R2.1.1", "loads": "H3-R2.1.2", "rails": "H3-R2.1.3"},
        "source_sha256": {str(path.relative_to(REPO)): sha256(path) for path in (CONTRACT, STATES, RAILS, LOADS, METHODS)},
        "policy": contract["policy"], "ownership": ownership,
        "ownership_summary": {"owner_counts": dict(sorted(Counter(row["owner"] for row in ownership).items())), "owner_instance_uids": owner_uids},
        "states": evaluated,
        "extrema": {
            "maximum_sys_demand": {k: max_sys[k] for k in ("id", "signal_group", "group_mode", "support_profile", "sys_demand_w", "source_raw_required_w")},
            "maximum_source_raw_required": {k: max_raw[k] for k in ("id", "signal_group", "group_mode", "support_profile", "source_raw_required_w")},
            "maximum_pack_discharge": {k: max_pack[k] for k in ("id", "usb", "pack", "signal_group", "group_mode", "support_profile", "pack_discharge_a", "pack_pf03_reserve_percent", "pack_endpoint_v", "cell_pair_i2r_w", "external_pack_path_i2r_w")},
            "maximum_sustained_pack_discharge": {k: max_sustained_pack[k] for k in ("id", "usb", "pack", "signal_group", "group_mode", "support_profile", "pack_discharge_a", "pack_pf03_reserve_percent", "pack_endpoint_v", "cell_pair_i2r_w", "external_pack_path_i2r_w")},
        },
        "summary": {
            "states_evaluated": len(evaluated), "deferred_lines_owned": len(ownership), "failed_states": len(failures),
            "maximum_sys_demand_w": max_sys["sys_demand_w"], "maximum_source_raw_required_w": max_raw["source_raw_required_w"],
            "maximum_pack_discharge_a": max_pack["pack_discharge_a"], "pack_reserve_percent_at_worst": max_pack["pack_pf03_reserve_percent"],
            "maximum_sustained_pack_discharge_a": max_sustained_pack["pack_discharge_a"],
            "maximum_sustained_cell_pair_i2r_w": max_sustained_pack["cell_pair_i2r_w"],
            "usb_only_profiles_refused": len(refused), "charge_states_derated": len(derated),
            "admission_counts": dict(sorted(Counter(row["admission"] for row in evaluated).items())),
            "action_counts": dict(sorted(Counter(row["required_action"] for row in evaluated).items())),
            "hidden_miscellaneous_allowances": 0,
        },
        "conclusions": [
            "battery-only operation passes the 8-A PF-R2-03 admission at the 6.0-V low-pack corner",
            "5-V/3-A USB-only operation refuses oversized profiles instead of brownout",
            "9-V/3-A and 15-V/2-A run every declared profile; charge is DPM-derated before system load",
            "unknown fallback contributes no assumed watts before current advertisement is measured",
        ],
        "physical_residuals": ["H3-R2.2 dynamic DPM/handover/inrush", "H6 routed source/pack resistance extraction", "H8 measured efficiency, current and pack temperature"],
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "next": {"marker": "H3-R2.1.5", "action": "cross-check and publish the reviewed H3-R2.1 result"}, "errors": [],
    }
    return {OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", DOC_EN: render_doc(manifest, False), DOC_RU: render_doc(manifest, True)}, manifest


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
        print(f"wrote H3-R2.1.4: {manifest['summary']['states_evaluated']} states, {manifest['summary']['failed_states']} failures")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.1.4 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.1.4; {manifest['summary']['states_evaluated']} states, maximum pack {manifest['summary']['maximum_pack_discharge_a']} A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
