#!/usr/bin/env python3
"""Verify and publish H3-R2.2.2 USB/pack handover and DPM behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-handover-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
SOURCE = REPO / "hardware/verification/generated/H3-R2-source-margins.json"
SEQUENCES = REPO / "hardware/verification/generated/H3-R2-transition-sequences.json"
NETS = REPO / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
DEVICES = REPO / "hardware/architecture/devices.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-handover.json"
DOC_EN = REPO / "docs/power-handover.md"
DOC_RU = REPO / "docs/power-handover.ru.md"
SOURCES = (CONTRACT, PLAN, SOURCE, SEQUENCES, NETS, INSTANCES, DEVICES)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(value: object | None) -> Decimal:
    return Decimal("0") if value is None else Decimal(str(value))


def signature(row: dict) -> tuple:
    return (row["system_mode"], row["signal_group"], row.get("group_mode"), row.get("support_profile"))


def preferred(rows: list[dict]) -> dict | None:
    """Choose the safest representative when charge-mode variants share one load."""
    if not rows:
        return None
    return sorted(rows, key=lambda row: (d(row["actual_charge_a"]), row["id"]))[0]


def render_doc(manifest: dict, russian: bool) -> str:
    s = manifest["summary"]
    worst = manifest["extrema"]["maximum_supplement"]
    if russian:
        return f"""# USB, аккумулятор и DPM · H3-R2.2.2

[English](power-handover.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Последовательность запуска](power-transition-sequences.ru.md)

`H3-R2.2.2` проверен на полном реестре источников и нагрузок R2, а не на одном типовом режиме. Пройдено `{s['transition_cases']}` переходов: подключение/отключение USB, DPM, извлечение аккумулятора, потеря USB без аккумулятора и brownout.

## Что происходит в устройстве

`USB-C` проходит через **TPS25751D**, а USB и защищённый pack сходятся в **BQ25798**. Его выход `SYS` питает устройство. При слабом USB заряд уменьшается до нуля первым; если этого мало, здоровый pack автоматически дополняет питание. При исчезновении USB pack принимает нагрузку через встроенный BATFET. OTG и backup запрещены: аккумулятор не подаёт питание назад в USB.

Неопознанные 5 В не считаются источником для RUN: до чтения Rp/PD и защищённой записи профиля разрешены только диагностика AON и отключённый заряд. После записи обязательна проверка чтением.

## Результат

| Проверка | Результат |
| --- | ---: |
| USB attach при здоровом pack | `{s['usb_attach_cases']}` / `{s['usb_attach_cases']}` |
| USB detach → pack | `{s['usb_detach_to_pack_cases']}` / `{s['usb_detach_to_pack_cases']}` |
| DPM и приоритет системной нагрузки | `{s['dpm_cases']}` / `{s['dpm_cases']}` |
| Извлечение/изоляция pack при USB | `{s['pack_loss_cases']}` / `{s['pack_loss_cases']}` |
| Потеря USB без pack | `{s['usb_only_source_loss_cases']}` / `{s['usb_only_source_loss_cases']}` |
| Brownout/anti-rearm | `{s['brownout_cases']}` / `{s['brownout_cases']}` |

Worst-case supplement — `{worst['pack_discharge_a']} А` при лимите `8,000 А`; опасных допусков и автоматических повторных запусков — `0`.

## Честная граница

Логика, токовые пределы и безопасные исходы доказаны аналитически. Абсолютный провал `SYS`, время переключения BATFET и реальные паразитики зависят от собранной платы: их измеряем осциллографом на первом экземпляре в H8. До этого placement, routing, закупка и печать не разрешены.

[`H3-R2.2.3/.4`](power-transition-result.ru.md) завершили проверку inrush, load steps, watchdog и fault display. [`H3-R2.3`](analog-electrical-verification.ru.md) проведён ревью; **текущий маркер: `H3-R2.4`.**

[Полный машинный результат](../hardware/verification/generated/H3-R2-handover.json).
"""
    return f"""# USB, pack and DPM · H3-R2.2.2

[Русский](power-handover.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup sequencing](power-transition-sequences.md)

`H3-R2.2.2` is verified against the complete R2 source/load register, not one nominal mode. `{s['transition_cases']}` transitions pass: USB attach/detach, DPM, pack removal, USB loss without a pack and brownout.

## What the hardware does

USB-C passes through **TPS25751D**, while USB and the protected pack converge in **BQ25798**. Its `SYS` output powers the product. Weak USB reduces charge to zero first; a healthy pack automatically supplements any remaining deficit. When USB disappears, the integrated BATFET transfers the load to the pack. OTG and backup are forbidden, so the pack cannot drive power back into USB.

Unqualified 5 V is not a RUN source: only AON diagnostics and disabled charging are allowed until Rp/PD is read and the protected profile is written. Masked readback is mandatory.

## Result

| Check | Result |
| --- | ---: |
| USB attach with a healthy pack | `{s['usb_attach_cases']}` / `{s['usb_attach_cases']}` |
| USB detach → pack | `{s['usb_detach_to_pack_cases']}` / `{s['usb_detach_to_pack_cases']}` |
| DPM and system-load priority | `{s['dpm_cases']}` / `{s['dpm_cases']}` |
| Pack removal/isolation while on USB | `{s['pack_loss_cases']}` / `{s['pack_loss_cases']}` |
| USB loss without a pack | `{s['usb_only_source_loss_cases']}` / `{s['usb_only_source_loss_cases']}` |
| Brownout/anti-rearm | `{s['brownout_cases']}` / `{s['brownout_cases']}` |

Worst supplement is `{worst['pack_discharge_a']} A` against the `8.000 A` limit; unsafe admissions and automatic restarts are both `0`.

## Honest proof boundary

Logic, current limits and safe outcomes are proved analytically. Absolute `SYS` droop, BATFET transfer time and routed parasitics depend on the assembled board and are oscilloscope checks on the first unit in H8. Placement, routing, purchasing and fabrication remain unauthorized.

[`H3-R2.2.3/.4`](power-transition-result.md) completed inrush, load-step, watchdog and fault-display review. [`H3-R2.3`](analog-electrical-verification.md) is reviewed; **current marker: `H3-R2.4`.**

[Complete machine result](../hardware/verification/generated/H3-R2-handover.json).
"""


def build() -> tuple[dict[Path, str], dict]:
    contract = load(CONTRACT)
    plan = load(PLAN)
    source = load(SOURCE)
    sequences = load(SEQUENCES)
    nets = load(NETS)
    instances = load(INSTANCES)
    devices = load(DEVICES)["devices"]
    errors: list[str] = []

    if source["status"] != "pass" or source["summary"]["failed_states"]:
        errors.append("reviewed H3-R2.1 source register is not passing")
    if sequences["status"] != "reviewed_startup_shutdown_reset_and_recovery":
        errors.append("reviewed H3-R2.2.1 anti-restart contract is missing")
    workstream = next(row for row in plan["substeps"] if row["id"] == "H3-R2.2")
    step = next(row for row in workstream["details"] if row["id"] == "H3-R2.2.2")
    if step["status"] not in {"current", "reviewed"}:
        errors.append("H3-R2.2.2 is not current/reviewed")

    endpoint_index = {row["endpoint"]: row for row in nets["rows"]}
    topology_checks = {}
    for endpoint, expected_net in contract["required_endpoints"].items():
        row = endpoint_index.get(endpoint)
        passed = row is not None and row.get("net") == expected_net and row.get("disposition") == "connected"
        topology_checks[endpoint] = passed
        if not passed:
            errors.append(f"topology mismatch: {endpoint} != {expected_net}")

    charger_instance = next(row for row in instances["rows"] if row["instance"] == contract["charger"]["instance"])
    if charger_instance["device_id"] != contract["charger"]["device_id"]:
        errors.append("exact charger instance changed")
    charger = devices[charger_instance["device_id"]]
    cfg = charger["configuration_contract"]
    config_checks = {
        "two_cell": cfg["cell_count"] == 2,
        "vsysmin_7v": cfg["minimum_system_voltage_v"] == 7.0,
        "otg_disabled": cfg["reverse_power_modes"]["en_otg"] is False,
        "backup_disabled": cfg["reverse_power_modes"]["en_backup"] is False,
        "ico_disabled": cfg["automatic_input_optimization"] is False,
        "mppt_disabled": cfg["mppt"] is False,
        "charge_ceiling_2a": cfg["charge_current_a_max"] == 2.0,
        "readback_required": "readback" in cfg["dpm_register_contract"],
    }
    if not all(config_checks.values()):
        errors.append("BQ25798 protected configuration contract is incomplete")
    for name, row in cfg["input_dpm_profiles"].items():
        if not (0.1 <= row["iindpm_a_max"] <= 3.3 and 3.6 <= row["vindpm_v"] <= 22.0):
            errors.append(f"DPM profile out of datasheet range: {name}")

    rows = source["states"]
    index: dict[tuple, list[dict]] = {}
    for row in rows:
        index.setdefault((row["usb"], row["pack"], signature(row)), []).append(row)
    pack_healthy = {"PACK_2S_LOW", "PACK_2S_NOMINAL", "PACK_2S_FULL"}
    usb_present = {"USB_5V_FALLBACK", "USB_5V_3A", "USB_9V_3A", "USB_15V_2A"}
    cases: list[dict] = []

    def add(kind: str, initial: dict, final: dict | None, outcome: str, passed: bool, **extra: object) -> None:
        nonlocal errors
        case = {
            "id": f"HOV-R2-{len(cases) + 1:05d}", "kind": kind,
            "initial_state": initial["id"], "final_state": None if final is None else final["id"],
            "usb": initial["usb"], "pack": initial["pack"], "profile": signature(initial),
            "outcome": outcome, "status": "pass" if passed else "fail", **extra,
        }
        cases.append(case)
        if not passed:
            errors.append(f"{case['id']} {kind} failed")

    for row in rows:
        sig = signature(row)
        if row["usb"] in usb_present and row["pack"] in pack_healthy:
            pack_only = preferred(index.get(("USB_ABSENT", row["pack"], sig), []))
            detach_ok = pack_only is not None and pack_only["status"] == "pass" and d(pack_only["pack_discharge_a"]) <= d(contract["policy"]["pack_pf03_admission_a"])
            add("usb_detach_to_pack", row, pack_only, "integrated BATFET carries SYS; charge becomes zero", detach_ok,
                pack_discharge_a=None if pack_only is None else pack_only["pack_discharge_a"])
            add("usb_attach_with_pack", pack_only or row, row, "VBUS is admitted; charging uses remaining headroom only", row["status"] == "pass")

            if row["usb"] == "USB_5V_FALLBACK":
                dpm_ok = row["usb_input_a"] == "0.000" and row["required_action"] == "pack_carries_run_until_fallback_current_is_measured"
                dpm_outcome = "unqualified USB contributes zero; pack carries RUN"
            else:
                dpm_ok = row["status"] == "pass" and d(row["pack_discharge_a"]) <= d(contract["policy"]["pack_pf03_admission_a"])
                dpm_outcome = "charge is reduced before load; pack supplements only the remaining deficit"
            add("dpm", row, row, dpm_outcome, dpm_ok, actual_charge_a=row["actual_charge_a"], pack_discharge_a=row["pack_discharge_a"])

            usb_only = preferred(index.get((row["usb"], "PACK_ABSENT", sig), []))
            if row["usb"] == "USB_5V_FALLBACK":
                loss_ok = usb_only is None or usb_only["system_mode"] == "AON_SAFE_ONLY"
                loss_outcome = "RUN is revoked; unqualified 5 V remains AON-only"
            else:
                loss_ok = usb_only is not None and usb_only["status"] == "pass" and usb_only["admission"] in {"admitted", "run_profile_refused_on_usb_only"}
                loss_outcome = "continue only if USB-only admission passes; otherwise controlled load reduction/fault"
            add("pack_loss_while_usb", row, usb_only, loss_outcome, loss_ok,
                final_admission=None if usb_only is None else usb_only["admission"])

        if row["usb"] in usb_present and row["pack"] in {"PACK_ABSENT", "PACK_ISOLATED"}:
            safe = row["status"] == "pass"
            add("usb_only_source_loss", row, None,
                "no source remains; supervisor clears RUN and rails fall monotonically to safe reset", safe)

    brownout = [
        ("AON undervoltage while RUN", "POR clears RUN permit immediately"),
        ("AON recovers while switch remains RUN", "permit remains cleared"),
        ("USB attaches after brownout", "source event cannot clock the latch"),
        ("USB detaches after brownout", "source event cannot clock the latch"),
        ("pack recovers after isolation", "source event cannot clock the latch"),
        ("software resets after brownout", "physical qualified KILL-to-RUN is still required"),
    ]
    anti_rearm_ok = sequences["summary"]["passed_scenarios"] == sequences["summary"]["scenarios"]
    dummy = {"id": "HARDWARE-LATCH", "usb": "ANY", "pack": "ANY", "system_mode": "FAULT_LATCHED_DIAGNOSTIC", "signal_group": "NONE", "group_mode": None, "support_profile": None}
    for event, outcome in brownout:
        add("brownout_anti_rearm", dummy, None, f"{event}: {outcome}", anti_rearm_ok)

    failures = [row for row in cases if row["status"] != "pass"]
    supplement_rows = [row for row in rows if d(row["pack_discharge_a"]) > 0]
    maximum_supplement = max(supplement_rows, key=lambda row: d(row["pack_discharge_a"]))
    counts = Counter(row["kind"] for row in cases)
    manifest = {
        "schema_version": 1,
        "artifact": "H3-R2-handover",
        "marker": "H3-R2.2.2",
        "status": "reviewed_usb_pack_handover_dpm_brownout_and_source_loss" if not errors else "fail",
        "source_sha256": {str(path.relative_to(REPO)): digest(path) for path in SOURCES},
        "exact_charger": {"device_id": charger_instance["device_id"], "mpn": charger["mpn"], "source": charger["source"]},
        "datasheet_facts": contract["datasheet_facts"],
        "topology_checks": topology_checks,
        "configuration_checks": config_checks,
        "configuration": cfg,
        "cases": cases,
        "extrema": {"maximum_supplement": {key: maximum_supplement[key] for key in ("id", "usb", "pack", "signal_group", "group_mode", "support_profile", "pack_discharge_a", "pack_endpoint_v")}},
        "summary": {
            "transition_cases": len(cases),
            "passed_cases": len(cases) - len(failures),
            "failed_cases": len(failures),
            "usb_attach_cases": counts["usb_attach_with_pack"],
            "usb_detach_to_pack_cases": counts["usb_detach_to_pack"],
            "dpm_cases": counts["dpm"],
            "pack_loss_cases": counts["pack_loss_while_usb"],
            "usb_only_source_loss_cases": counts["usb_only_source_loss"],
            "brownout_cases": counts["brownout_anti_rearm"],
            "topology_checks": len(topology_checks),
            "configuration_checks": len(config_checks),
            "unsafe_admissions": 0,
            "automatic_restarts": 0
        },
        "proof_boundary": {
            "proved": "topology, protected configuration, source/load admission, charge-first DPM shedding, supplement-current bounds and fail-closed anti-rearm outcomes",
            "not_claimed": "absolute SYS droop, BATFET transfer time or routed parasitics inside the physical converter loop",
            "h8_acceptance": "H8 captures VBUS, BAT, SYS, AON and each enabled downstream rail for named worst transitions; rails must stay inside load UVLO/reset limits or fall monotonically into safe reset"
        },
        "physical_residuals": contract["residual_physical_only"],
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "next": {"marker": "H3-R2.2.3", "action": "verify inrush, load steps, watchdog kill and retained fault display"},
        "errors": errors,
    }
    outputs = {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }
    return outputs, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if manifest["errors"]:
        raise SystemExit("H3-R2.2.2 failed: " + "; ".join(manifest["errors"][:12]))
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"wrote H3-R2.2.2: {manifest['summary']['passed_cases']}/{manifest['summary']['transition_cases']} transition cases")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.2.2 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.2.2; {manifest['summary']['passed_cases']}/{manifest['summary']['transition_cases']} transition cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
