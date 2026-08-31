#!/usr/bin/env python3
"""Enumerate every legal R2 source, charge and operating state."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-power-state-contract.json"
FREEZE = REPO / "hardware/verification/generated/H3-R2-input-freeze.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
HWFW = REPO / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-power-state-register.json"
DOC_EN = REPO / "docs/power-state-register.md"
DOC_RU = REPO / "docs/power-state-register.ru.md"
SOURCES = (CONTRACT, FREEZE, METHODS, H0, HWFW)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge_modes(usb: dict, pack: dict) -> list[str]:
    if usb["id"] == "USB_ABSENT":
        return ["PACK_DISCHARGE"] if pack["healthy"] else ["POWERLESS"]
    if usb["id"] == "USB_5V_FALLBACK":
        return ["CHARGE_INHIBITED_UNTIL_DPM_HEADROOM", "PACK_SUPPLEMENT_IF_REQUIRED"] if pack["healthy"] else ["USB_LIMITED_NO_CHARGE"]
    if not pack["healthy"]:
        return ["USB_SYSTEM_SUPPLY_NO_CHARGE"]
    if pack["id"] == "PACK_2S_FULL":
        return ["CHARGE_TERMINATED", "RECHARGE_IF_THRESHOLD_REACHED"]
    return ["CHARGE_DISABLED", "CHARGE_INITIAL_1A", "CHARGE_MAX_2A_IF_HEADROOM"]


def build() -> dict:
    contract = load(CONTRACT)
    freeze = load(FREEZE)
    methods = load(METHODS)
    h0 = load(H0)
    errors: list[str] = []
    if freeze.get("status") != "pass" or methods.get("status") != "pass":
        errors.append("H3-R2 input freeze or method contract is not passing")
    if h0.get("status") != "reviewed_functional_architecture_i8080_and_r2_interboard_reconciled":
        errors.append("H0-R2 authority is not reviewed")
    method_ids = {row["id"] for row in methods.get("methods", [])}
    if not {"M-INT", "M-DC", "M-STATE"}.issubset(method_ids):
        errors.append("required R2 state/DC methods are absent")

    usb_profiles = contract["source_profiles"]["usb"]
    pack_profiles = contract["source_profiles"]["pack"]
    source_states: list[dict] = []
    for usb in usb_profiles:
        for pack in pack_profiles:
            for charge_mode in charge_modes(usb, pack):
                usb_present = usb["id"] != "USB_ABSENT"
                source_available = usb_present or pack["healthy"]
                run_allowed = source_available and not (usb["id"] == "USB_5V_FALLBACK" and not pack["healthy"])
                source_states.append({
                    "id": f"SRC-R2-{len(source_states):03d}",
                    "usb": usb["id"],
                    "pack": pack["id"],
                    "charge_mode": charge_mode,
                    "aon_available": source_available,
                    "run_allowed": run_allowed,
                    "nvdc_sources": [name for name, enabled in (("USB", usb_present), ("PACK", pack["healthy"])) if enabled],
                })

    operating_profiles: list[dict] = []
    for group in contract["signal_groups"]:
        for mode in group["modes"]:
            for support in contract["support_profiles"]:
                operating_profiles.append({
                    "signal_group": group["id"],
                    "group_mode": mode["id"],
                    "hardware": group["hardware"],
                    "tx_count": mode.get("tx_count", 0),
                    "rx_count": mode.get("rx_count"),
                    "identity_permutations": mode.get("identity_permutations", 1),
                    "cap_profile": mode.get("profile"),
                    "support_profile": support["id"],
                })

    states: list[dict] = []
    for source in source_states:
        if not source["aon_available"]:
            states.append({"id": f"PWR-R2-{len(states):04d}", "source_state": source["id"], "system_mode": "UNPOWERED_OFF", "signal_group": "NONE"})
            continue
        states.append({"id": f"PWR-R2-{len(states):04d}", "source_state": source["id"], "system_mode": "AON_SAFE_ONLY", "signal_group": "NONE"})
        if source["run_allowed"]:
            states.append({"id": f"PWR-R2-{len(states):04d}", "source_state": source["id"], "system_mode": "FAULT_LATCHED_DIAGNOSTIC", "signal_group": "NONE"})
            for profile in operating_profiles:
                states.append({"id": f"PWR-R2-{len(states):04d}", "source_state": source["id"], "system_mode": "RUN", **profile})

    group_modes = {row["id"]: {mode["id"] for mode in row["modes"]} for row in contract["signal_groups"]}
    if group_modes.get("NRF24") != set(contract["invariants"]["nrf24_required_mixes"]):
        errors.append("nRF24 full-concurrency state set is incomplete")
    if "U219_CC1101_NFC_RX_ONLY" not in group_modes.get("LORA_CAP", set()):
        errors.append("accepted receive-only U219 Cap profile is absent")
    if "AIRBAND_118_137_RX" not in group_modes.get("BROADCAST_RX", set()):
        errors.append("mandatory Airband receive state is absent")
    for row in states:
        if row["system_mode"] != "RUN" and row["signal_group"] != "NONE":
            errors.append(f"{row['id']}: inactive mode has an active group")
        if row["system_mode"] == "RUN" and row["signal_group"] not in group_modes:
            errors.append(f"{row['id']}: unknown active group")

    state_mode_counts = Counter(row["system_mode"] for row in states)
    sources = {str(path.relative_to(REPO)): digest(path) for path in SOURCES}
    payload = json.dumps({"sources": sources, "contract": contract, "states": states}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "artifact": "H3-R2-power-state-register",
        "marker": "H3-R2.1.1",
        "status": "pass" if not errors else "fail",
        "accepted_input": "H3-R2.0.3",
        "state_register_sha256": hashlib.sha256(payload).hexdigest(),
        "source_sha256": sources,
        "source_contract": contract["source_profiles"],
        "operating_contract": {
            "signal_groups": contract["signal_groups"],
            "support_profiles": contract["support_profiles"],
            "invariants": contract["invariants"],
        },
        "rejected_pack_conditions": contract["rejected_pack_conditions"],
        "source_states": source_states,
        "operating_profiles": operating_profiles,
        "states": states,
        "summary": {
            "usb_profiles": len(usb_profiles),
            "pack_profiles": len(pack_profiles),
            "source_charge_states": len(source_states),
            "signal_groups": len(group_modes),
            "group_modes": sum(len(modes) for modes in group_modes.values()),
            "support_profiles": len(contract["support_profiles"]),
            "operating_profiles": len(operating_profiles),
            "legal_states": len(states),
            "run_source_states": sum(row["run_allowed"] for row in source_states),
            "state_mode_counts": dict(sorted(state_mode_counts.items())),
            "rejected_pack_conditions": len(contract["rejected_pack_conditions"]),
            "invariant_violations": len(errors),
        },
        "authorization": {
            "advance_to_h3_r2_1_2": not errors,
            "placement_or_routing": False,
            "purchasing": False,
            "fabrication": False
        },
        "next": {"marker": "H3-R2.1.2", "action": "bind every powered R2 instance to an explicit worst-case rail-load line"},
        "errors": errors,
    }


def render_doc(result: dict, ru: bool) -> str:
    s = result["summary"]
    if ru:
        title = "# Состояния питания R2"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Методы](verification-methods.ru.md) · [English](power-state-register.md)"
        intro = f"`H3-R2.1.1` прошёл ревью. Реестр детерминированно перечисляет `{s['source_charge_states']}` состояния источников/заряда, `{s['operating_profiles']}` рабочих профиля и `{s['legal_states']}` полных разрешённых состояния R2."
        details_h = "## Что вошло"
        details = "- единственный питающий USB-C: absent, неизвестный 5-V fallback, 5 V × 3 A, 9 V × 3 A и 15 V × 2 A;\n- pack: отсутствует, изолирован, 2S low/nominal/full;\n- все десять signal groups, включая три nRF24 во всех 3R/1T2R/2T1R/3T сочетаниях;\n- оба взаимоисключающих Cap-профиля: U214 и receive-only U219;\n- FM/SW, AM/LW и обязательный receive-only Airband как взаимоисключающие подрежимы BROADCAST_RX;\n- safe-only и latched-fault состояния без payload-передачи."
        rule_h = "## Важная граница"
        rule = "Это доказательство полноты состояний, а не достаточности тока. Следующий точный маркер `H3-R2.1.2` связывает каждый питаемый компонент с явной worst-case нагрузкой; неизвестный ток обязан дать `unresolved_fail`, а не скрытый запас."
        evidence = "[Полный машинный реестр](../hardware/verification/generated/H3-R2-power-state-register.json)."
    else:
        title = "# R2 power states"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Methods](verification-methods.md) · [Русский](power-state-register.ru.md)"
        intro = f"`H3-R2.1.1` is reviewed. The deterministic register enumerates `{s['source_charge_states']}` source/charge states, `{s['operating_profiles']}` operating profiles and `{s['legal_states']}` complete legal R2 states."
        details_h = "## Included surface"
        details = "- sole powered USB-C: absent, unknown 5-V fallback, 5 V × 3 A, 9 V × 3 A and 15 V × 2 A;\n- pack absent, isolated, 2S low/nominal/full;\n- all ten signal groups, including all three nRF24 paths in 3R/1T2R/2T1R/3T combinations;\n- mutually exclusive U214 and receive-only U219 Cap profiles;\n- mutually exclusive FM/SW, AM/LW and mandatory receive-only Airband submodes;\n- safe-only and latched-fault modes with no payload transmission."
        rule_h = "## Important boundary"
        rule = "This proves state completeness, not current sufficiency. Exact marker `H3-R2.1.2` now binds every powered instance to an explicit worst-case rail-load line; an unknown current must produce `unresolved_fail`, never a hidden allowance."
        evidence = "[Complete machine register](../hardware/verification/generated/H3-R2-power-state-register.json)."
    return "\n\n".join((title, nav, intro, details_h, details, rule_h, rule, evidence)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    outputs = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(result, False),
        DOC_RU: render_doc(result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"wrote H3-R2.1.1: {result['summary']['legal_states']} legal states")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: H3-R2.1.1 power-state register is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
