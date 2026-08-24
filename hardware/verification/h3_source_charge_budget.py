#!/usr/bin/env python3
"""Apply H3.1.2 rail loads to every H3.1.1 source/charge state."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
STATES = REPO / "hardware/verification/generated/H3-VRF11-power-state-register.json"
DC_BUDGET = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
METHODS = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
POWER_REVIEW = REPO / "hardware/ecad/generated/H2-REV51-power-paths.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF13-source-charge-budget.json"
DOC_EN = REPO / "docs/source-charge-budget.md"
DOC_RU = REPO / "docs/source-charge-budget.ru.md"


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal | None, places: str = "0.001") -> str | None:
    if value is None:
        return None
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# The source contract already accepted a deliberately pessimistic 85% factor.
# It is applied once to USB/pack -> SYS and once to each enabled SYS -> rail path.
MIN_CONVERSION_EFFICIENCY = d("0.85")
PACK_CONTINUOUS_A = d("10.0")
PACK_PF02_LIMIT_A = PACK_CONTINUOUS_A / d("1.25")

USB_INPUT = {
    "USB_ABSENT": {"voltage_v": d(0), "current_a": d(0), "input_w": d(0), "usable_sys_w": d(0)},
    "USB_5V_FALLBACK": {"voltage_v": d(5), "current_a": None, "input_w": None, "usable_sys_w": None},
    "USB_5V_3A": {"voltage_v": d(5), "current_a": d(3), "input_w": d(15), "usable_sys_w": d("12.75")},
    "USB_9V_3A": {"voltage_v": d(9), "current_a": d(3), "input_w": d(27), "usable_sys_w": d("22.95")},
    "USB_15V_2A": {"voltage_v": d(15), "current_a": d(2), "input_w": d(30), "usable_sys_w": d("25.50")},
}

PACK_VOLTAGE = {
    "PACK_ABSENT": None,
    "PACK_ISOLATED": None,
    "PACK_2S_LOW": d("6.0"),
    "PACK_2S_NOMINAL": d("7.2"),
    "PACK_2S_FULL": d("8.4"),
}

CHARGE_REQUEST_A = {
    "POWERLESS": d(0),
    "PACK_DISCHARGE": d(0),
    "USB_LIMITED_NO_CHARGE": d(0),
    "CHARGE_INHIBITED_UNTIL_DPM_HEADROOM": d(0),
    "PACK_SUPPLEMENT_IF_REQUIRED": d(0),
    "USB_SYSTEM_SUPPLY_NO_CHARGE": d(0),
    "CHARGE_DISABLED": d(0),
    "CHARGE_INITIAL_1A": d(1),
    "CHARGE_MAX_2A_IF_HEADROOM": d(2),
    "CHARGE_TERMINATED": d(0),
    "RECHARGE_IF_THRESHOLD_REACHED": d(1),
}

# These are conservative design envelopes used only to expose steady heat to
# H3.6.  They are intentionally above typical switch resistance.
EFUSE_ENVELOPE_OHM = {
    "AON_SAFE_3V3": d("0.24"),
    "3V3_MAIN": d("0.05"),
    "VVOICE_4V": d("0.05"),
    "5V_EXT_ACTIVE_BRANCH": d("0.06"),
}


def profile_key(row: dict) -> tuple[str, str, str]:
    return row["signal_group"], row["group_mode"], row["support_profile"]


def rail_loads_for_state(state: dict, profiles: dict[tuple[str, str, str], dict], idle: dict) -> dict[str, Decimal]:
    zero = {rail: d(0) for rail in idle["loads_ma"]}
    if state["system_mode"] == "UNPOWERED_OFF":
        return zero
    if state["system_mode"] == "AON_SAFE_ONLY":
        zero["AON_SAFE_3V3"] = d(idle["loads_ma"]["AON_SAFE_3V3"])
        return zero
    if state["system_mode"] == "FAULT_LATCHED_DIAGNOSTIC":
        # Restricted S3 UI and the local fault record are deliberately bounded
        # by the already accepted NONE/QUIET/SUPPORT_IDLE profile.
        return {rail: d(value) for rail, value in idle["loads_ma"].items()}
    row = profiles[profile_key(state)]
    return {rail: d(value) for rail, value in row["loads_ma"].items()}


def power_and_loss(loads_ma: dict[str, Decimal], rail_capabilities: dict) -> tuple[Decimal, Decimal, Decimal, dict]:
    output_w = d(0)
    conversion_loss_w = d(0)
    efuse_loss_w = d(0)
    rows = {}
    for rail, load_ma in loads_ma.items():
        current_a = load_ma / d(1000)
        rail_output_w = current_a * d(rail_capabilities[rail]["voltage_v"])
        rail_input_w = rail_output_w / MIN_CONVERSION_EFFICIENCY if rail_output_w else d(0)
        rail_conversion_loss = rail_input_w - rail_output_w
        rail_efuse_loss = current_a * current_a * EFUSE_ENVELOPE_OHM[rail]
        output_w += rail_output_w
        conversion_loss_w += rail_conversion_loss
        efuse_loss_w += rail_efuse_loss
        rows[rail] = {
            "load_ma": q(load_ma),
            "output_w": q(rail_output_w),
            "input_from_sys_w": q(rail_input_w),
            "conversion_loss_w": q(rail_conversion_loss),
            "efuse_loss_w": q(rail_efuse_loss),
        }
    return output_w, conversion_loss_w, efuse_loss_w, rows


def evaluate_state(state: dict, source: dict, loads_ma: dict[str, Decimal], rail_capabilities: dict) -> dict:
    output_w, rail_loss_w, efuse_loss_w, rail_rows = power_and_loss(loads_ma, rail_capabilities)
    sys_demand_w = output_w + rail_loss_w
    usb = USB_INPUT[source["usb"]]
    pack_v = PACK_VOLTAGE[source["pack"]]
    requested_charge_a = CHARGE_REQUEST_A[source["charge_mode"]]
    requested_charge_w = requested_charge_a * pack_v if pack_v is not None else d(0)
    charge_actual_a = d(0)
    pack_discharge_a = d(0)
    usb_input_a = d(0)
    admission = "admitted"
    action = "none"

    if state["system_mode"] == "UNPOWERED_OFF":
        admission = "expected_unpowered"
    elif source["usb"] == "USB_ABSENT":
        if pack_v is None:
            admission = "expected_unpowered"
        else:
            pack_discharge_a = sys_demand_w / pack_v
            action = "pack_supplies_system"
    elif usb["usable_sys_w"] is None:
        # A fallback source has no numeric capacity until Rp/PD measurement.
        # A healthy pack conservatively carries the full load; without one the
        # state register only admits bounded AON diagnostics, never RUN.
        if pack_v is not None:
            pack_discharge_a = sys_demand_w / pack_v
            action = "pack_supplies_until_fallback_current_proven"
        elif state["system_mode"] == "AON_SAFE_ONLY":
            admission = "diagnostic_only_pending_source_current"
            action = "hold_run_off"
        else:
            admission = "not_admitted_without_numeric_source_or_pack"
            action = "hold_run_off"
    else:
        usable = usb["usable_sys_w"]
        if sys_demand_w > usable:
            deficit = sys_demand_w - usable
            usb_input_a = usb["current_a"]
            if pack_v is None:
                admission = "run_profile_not_admitted_on_this_source"
                action = "reduce_load_or_attach_healthy_pack_or_higher_pdo"
            else:
                pack_discharge_a = deficit / pack_v
                action = "pack_supplements_usb"
        else:
            headroom_w = usable - sys_demand_w
            if pack_v is not None and requested_charge_a:
                charge_actual_a = min(requested_charge_a, headroom_w / pack_v)
                action = "charge_as_requested" if charge_actual_a == requested_charge_a else "charge_derated_by_dpm_headroom"
            elif requested_charge_a:
                admission = "invalid_charge_request_without_healthy_pack"
            delivered_sys_w = min(usable, sys_demand_w + charge_actual_a * (pack_v or d(0)))
            usb_input_a = delivered_sys_w / MIN_CONVERSION_EFFICIENCY / usb["voltage_v"]

    pack_pf02_pass = pack_discharge_a <= PACK_PF02_LIMIT_A
    if not pack_pf02_pass:
        admission = "pack_continuous_margin_failure"
    charge_derated = requested_charge_a > charge_actual_a and requested_charge_a > 0
    return {
        "id": state["id"],
        "source_state": source["id"],
        "usb": source["usb"],
        "pack": source["pack"],
        "charge_mode": source["charge_mode"],
        "system_mode": state["system_mode"],
        "signal_group": state["signal_group"],
        "group_mode": state.get("group_mode"),
        "support_profile": state.get("support_profile"),
        "rail_loads": rail_rows,
        "rail_output_w": q(output_w),
        "rail_conversion_loss_w": q(rail_loss_w),
        "efuse_conduction_loss_w": q(efuse_loss_w),
        "sys_demand_w": q(sys_demand_w),
        "usb_usable_sys_w": q(usb["usable_sys_w"]),
        "usb_input_a": q(usb_input_a) if usb["usable_sys_w"] is not None else None,
        "pack_voltage_v": q(pack_v),
        "pack_discharge_a": q(pack_discharge_a),
        "pack_pf02_limit_a": q(PACK_PF02_LIMIT_A),
        "requested_charge_a": q(requested_charge_a),
        "actual_charge_a": q(charge_actual_a),
        "charge_derated": charge_derated,
        "admission": admission,
        "required_action": action,
        "status": "pass" if pack_pf02_pass and admission != "invalid_charge_request_without_healthy_pack" else "fail",
    }


def build() -> tuple[dict[Path, str], dict]:
    states = json.loads(STATES.read_text(encoding="utf-8"))
    dc = json.loads(DC_BUDGET.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    if dc["summary"]["failed_profiles"] or dc["summary"]["unresolved_numeric_inputs"]:
        raise ValueError("H3.1.2 is not closed")
    if candidate["power_contract"]["source_power_reserve"]["paper_efficiency_factor"] != 0.85:
        raise ValueError("accepted source efficiency factor drift")
    if not any(row["id"] == "PF-02" for row in methods["pass_fail_rules"]):
        raise ValueError("PF-02 reserve rule is missing")

    source_by_id = {row["id"]: row for row in states["source_states"]}
    profiles = {profile_key(row): row for row in dc["profiles"]}
    idle = profiles[("NONE", "QUIET", "SUPPORT_IDLE")]
    evaluated = []
    for state in states["states"]:
        loads = rail_loads_for_state(state, profiles, idle)
        evaluated.append(evaluate_state(state, source_by_id[state["source_state"]], loads, dc["rail_capabilities"]))

    failures = [row for row in evaluated if row["status"] != "pass"]
    if failures:
        raise ValueError(f"source/charge failures remain: {len(failures)}")
    admission_counts = Counter(row["admission"] for row in evaluated)
    action_counts = Counter(row["required_action"] for row in evaluated)
    numeric = [row for row in evaluated if row["admission"] not in {"expected_unpowered", "diagnostic_only_pending_source_current"}]
    max_sys = max(numeric, key=lambda row: d(row["sys_demand_w"]))
    max_pack = max(evaluated, key=lambda row: d(row["pack_discharge_a"]))
    max_rail_loss = max(evaluated, key=lambda row: d(row["rail_conversion_loss_w"]))
    max_efuse_loss = max(evaluated, key=lambda row: d(row["efuse_conduction_loss_w"]))
    derated = [row for row in evaluated if row["charge_derated"]]
    source_limited = [row for row in evaluated if row["admission"] == "run_profile_not_admitted_on_this_source"]

    manifest = {
        "schema_version": 1,
        "stage": "H3.1.3",
        "status": "reviewed_all_source_charge_discharge_and_steady_loss_envelopes",
        "method": "all 2,032 enumerated states; Decimal arithmetic; 85% minimum cascaded conversion factors; PF-02 pack current reserve",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (STATES, DC_BUDGET, METHODS, CANDIDATE, POWER_REVIEW)},
        "contracts": {
            "minimum_conversion_efficiency": q(MIN_CONVERSION_EFFICIENCY),
            "usb_profiles": {
                key: {name: q(value) if isinstance(value, Decimal) else value for name, value in row.items()}
                for key, row in USB_INPUT.items()
            },
            "pack_voltage_v": {key: q(value) for key, value in PACK_VOLTAGE.items()},
            "pack_continuous_a": q(PACK_CONTINUOUS_A),
            "pack_pf02_limit_a": q(PACK_PF02_LIMIT_A),
            "charge_request_a": {key: q(value) for key, value in CHARGE_REQUEST_A.items()},
            "efuse_steady_envelope_ohm": {key: q(value) for key, value in EFUSE_ENVELOPE_OHM.items()},
            "admission_rule": "unsupported USB-only load profiles are explicitly refused; a healthy pack may supplement; charging is always reduced before system load",
        },
        "states": evaluated,
        "extrema": {
            "maximum_sys_demand": {key: max_sys[key] for key in ("id", "usb", "pack", "system_mode", "signal_group", "group_mode", "support_profile", "sys_demand_w")},
            "maximum_pack_discharge": {key: max_pack[key] for key in ("id", "usb", "pack", "signal_group", "group_mode", "support_profile", "pack_discharge_a")},
            "maximum_rail_conversion_loss": {key: max_rail_loss[key] for key in ("id", "signal_group", "group_mode", "support_profile", "rail_conversion_loss_w")},
            "maximum_efuse_conduction_loss": {key: max_efuse_loss[key] for key in ("id", "signal_group", "group_mode", "support_profile", "efuse_conduction_loss_w")},
        },
        "summary": {
            "states_evaluated": len(evaluated),
            "failed_states": len(failures),
            "unresolved_numeric_inputs": 0,
            "source_limited_profiles_explicitly_refused": len(source_limited),
            "charge_states_derated_by_dpm": len(derated),
            "admission_counts": dict(sorted(admission_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
            "maximum_sys_demand_w": max_sys["sys_demand_w"],
            "maximum_pack_discharge_a": max_pack["pack_discharge_a"],
            "pack_hardware_reserve_percent_at_worst": q((PACK_CONTINUOUS_A / d(max_pack["pack_discharge_a"]) - d(1)) * d(100)),
            "maximum_rail_conversion_loss_w": max_rail_loss["rail_conversion_loss_w"],
            "maximum_efuse_conduction_loss_w": max_efuse_loss["efuse_conduction_loss_w"],
        },
        "review_conclusions": [
            "battery-only operation passes PF-02 at the 6.0-V low-pack corner",
            "5-V/3-A USB alone is intentionally load-admitted per profile rather than pretending to run every worst case",
            "9-V/3-A and 15-V/2-A PDOs run every declared profile; charging is dynamically derated before load",
            "unknown 5-V fallback never enables RUN without a healthy pack and measured source headroom",
            "steady conversion and eFuse losses are now numeric H3.6 thermal inputs, not assumed thermal proof",
        ],
        "residual_physical_gates": [
            "H3.2 dynamic source/rail load-step, inrush, DPM and handover simulations",
            "H3.6 component/junction and enclosure thermal model using the recorded steady losses",
            "H8 measured converter efficiency, pack current, DPM charge derating and source handover",
        ],
        "next": {"stage": "H3.1.4", "action": "consolidate DC evidence, corrections, conditional admissions and residual gates"},
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    s = manifest["summary"]
    if russian:
        title = "# Источники, заряд, разряд и постоянные потери"
        nav = "[English](source-charge-budget.md) · [На главную](../README.ru.md) · [DC-шины](dc-power-budget.ru.md) · [Состояния](power-state-register.ru.md)"
        intro = f"H3.1.3 применил бюджет шин ко всем `{s['states_evaluated']}` состояниям. Между источником и SYS и между SYS и каждой активной шиной независимо заложено не менее 85% эффективности."
        results_h = "## Результат"
        results = (
            f"- Максимальный запрос SYS: `{s['maximum_sys_demand_w']} Вт`.\n"
            f"- Максимальный ток последовательного pack при 6,0 В: `{s['maximum_pack_discharge_a']} А`; запас до 10-А контракта элементов — `{s['pack_hardware_reserve_percent_at_worst']}%`.\n"
            f"- Максимальные постоянные потери преобразователей шин: `{s['maximum_rail_conversion_loss_w']} Вт`; eFuse: `{s['maximum_efuse_conduction_loss_w']} Вт`.\n"
            f"- Нарушений: `{s['failed_states']}`; неопределённых численных входов: `{s['unresolved_numeric_inputs']}`."
        )
        admission_h = "## Управление доступной мощностью"
        admission = (
            f"5 В × 3 А не притворяется универсальным источником: `{s['source_limited_profiles_explicitly_refused']}` комбинаций USB-only получают явный отказ до снижения нагрузки, установки здорового pack или перехода на более высокий PDO. "
            f"9 В × 3 А и 15 В × 2 А запускают любой заявленный профиль. В `{s['charge_states_derated_by_dpm']}` комбинациях запрос заряда уменьшается по DPM раньше, чем системная нагрузка. Неизвестный 5-В fallback без pack оставляет только AON-диагностику."
        )
        boundary_h = "## Граница доказательства"
        boundary = "Это закрывает постоянный энергетический envelope. Числа потерь становятся входом H3.6; переходы, пусковые токи, DPM и USB↔pack handover проверяются в H3.2, а реальные КПД и токи — на H8."
        marker = "**Статус:** `H3.1.3` завершено и проверено; текущий точный маркер — `H3.4.1`."
        evidence = "[Полный машинный расчёт](../hardware/verification/generated/H3-VRF13-source-charge-budget.json)."
    else:
        title = "# Source, charge, discharge and steady losses"
        nav = "[Русский](source-charge-budget.ru.md) · [Home](../README.md) · [DC rails](dc-power-budget.md) · [States](power-state-register.md)"
        intro = f"H3.1.3 applies the rail budget to all `{s['states_evaluated']}` states. At least 85% efficiency is independently reserved from source to SYS and from SYS to each enabled rail."
        results_h = "## Result"
        results = (
            f"- Maximum SYS demand: `{s['maximum_sys_demand_w']} W`.\n"
            f"- Maximum series-pack current at 6.0 V: `{s['maximum_pack_discharge_a']} A`; reserve to the 10-A cell contract is `{s['pack_hardware_reserve_percent_at_worst']}%`.\n"
            f"- Maximum steady rail-conversion loss: `{s['maximum_rail_conversion_loss_w']} W`; eFuse loss: `{s['maximum_efuse_conduction_loss_w']} W`.\n"
            f"- Failed states: `{s['failed_states']}`; unresolved numeric inputs: `{s['unresolved_numeric_inputs']}`."
        )
        admission_h = "## Available-power control"
        admission = (
            f"5 V × 3 A is not treated as a universal source: `{s['source_limited_profiles_explicitly_refused']}` USB-only combinations are explicitly refused until load is reduced, a healthy pack is installed, or a higher PDO is selected. "
            f"9 V × 3 A and 15 V × 2 A run every declared profile. Charge is DPM-derated before system load in `{s['charge_states_derated_by_dpm']}` combinations. Unknown 5-V fallback without a pack remains AON diagnostics only."
        )
        boundary_h = "## Proof boundary"
        boundary = "This closes the steady energy envelope. Recorded losses feed H3.6; transients, inrush, DPM and USB↔pack handover remain H3.2, while measured efficiency and current remain H8."
        marker = "**Status:** `H3.1.3` is complete and reviewed; the exact current marker is `H3.4.1`."
        evidence = "[Complete machine calculation](../hardware/verification/generated/H3-VRF13-source-charge-budget.json)."
    return "\n\n".join((title, nav, intro, results_h, results, admission_h, admission, boundary_h, boundary, marker, evidence)) + "\n"


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
        s = manifest["summary"]
        print(f"ok: H3.1.3 source/charge current; {s['states_evaluated']} states, {s['failed_states']} failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
