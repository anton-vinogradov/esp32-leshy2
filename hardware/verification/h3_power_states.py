#!/usr/bin/env python3
"""Enumerate every legal Leshy2 source, charge and operating state for H3.1."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
INTEGRATION = REPO / "hardware/architecture/target-integration-contract.json"
POWER_REVIEW = REPO / "hardware/ecad/generated/H2-REV51-power-paths.json"
QUIET_REVIEW = REPO / "hardware/ecad/generated/H2-REV54-quiet-state.json"
CHARGE_REVIEW = REPO / "hardware/ecad/generated/H2-RF01-usb-pd-charge.json"
METHODS = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF11-power-state-register.json"
DOC_EN = REPO / "docs/power-state-register.md"
DOC_RU = REPO / "docs/power-state-register.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


USB_PROFILES = [
    {"id": "USB_ABSENT", "voltage_v": 0, "current_limit_a": 0, "power_w": 0, "negotiated": False},
    {
        "id": "USB_5V_FALLBACK",
        "voltage_v": 5,
        "current_limit_a": "source-advertised Type-C current, <=3 A",
        "power_w": "source-dependent",
        "negotiated": False,
        "rule": "without a healthy pack, AON/PD diagnostics only until input-current and DPM headroom are proven",
    },
    {"id": "USB_5V_3A", "voltage_v": 5, "current_limit_a": 3, "power_w": 15, "negotiated": True},
    {"id": "USB_9V_3A", "voltage_v": 9, "current_limit_a": 3, "power_w": 27, "negotiated": True},
    {"id": "USB_15V_2A", "voltage_v": 15, "current_limit_a": 2, "power_w": 30, "negotiated": True},
]

PACK_PROFILES = [
    {"id": "PACK_ABSENT", "healthy": False, "isolated": False, "voltage_v": None},
    {"id": "PACK_ISOLATED", "healthy": False, "isolated": True, "voltage_v": None},
    {"id": "PACK_2S_LOW", "healthy": True, "isolated": False, "voltage_v": 6.0},
    {"id": "PACK_2S_NOMINAL", "healthy": True, "isolated": False, "voltage_v": 7.2},
    {"id": "PACK_2S_FULL", "healthy": True, "isolated": False, "voltage_v": 8.4},
]

GROUP_MODES = {
    "NONE": [{"mode": "QUIET", "tx_count": 0, "extra_rails": []}],
    "S3_RF": [
        {"mode": "2G4_RX_OR_SCAN", "tx_count": 0, "extra_rails": []},
        {"mode": "2G4_TX_MAX", "tx_count": 1, "extra_rails": []},
    ],
    "C5_RF": [
        {"mode": "2G4_RX", "tx_count": 0, "extra_rails": []},
        {"mode": "2G4_TX_MAX", "tx_count": 1, "extra_rails": []},
        {"mode": "5G_RX", "tx_count": 0, "extra_rails": []},
        {"mode": "5G_TX_MAX", "tx_count": 1, "extra_rails": []},
        {"mode": "802154_RX", "tx_count": 0, "extra_rails": []},
        {"mode": "802154_TX_MAX", "tx_count": 1, "extra_rails": []},
    ],
    "NRF24": [
        {"mode": "3PRX", "tx_count": 0, "rx_count": 3, "identity_permutations": 1, "extra_rails": ["NRF_SWITCHED_3V3"]},
        {"mode": "1PTX_2PRX", "tx_count": 1, "rx_count": 2, "identity_permutations": 3, "extra_rails": ["NRF_SWITCHED_3V3"]},
        {"mode": "2PTX_1PRX", "tx_count": 2, "rx_count": 1, "identity_permutations": 3, "extra_rails": ["NRF_SWITCHED_3V3"]},
        {"mode": "3PTX", "tx_count": 3, "rx_count": 0, "identity_permutations": 1, "extra_rails": ["NRF_SWITCHED_3V3"]},
    ],
    "CC1101": [
        {"mode": "RX", "tx_count": 0, "extra_rails": ["CC_SWITCHED_3V3"]},
        {"mode": "TX_MAX", "tx_count": 1, "extra_rails": ["CC_SWITCHED_3V3"]},
    ],
    "VOICE": [
        {"mode": "RX", "tx_count": 0, "extra_rails": ["VVOICE_4V"]},
        {"mode": "PTT_TX_MAX", "tx_count": 1, "extra_rails": ["VVOICE_4V"]},
    ],
    "IR": [
        {"mode": "LEARN_OR_RAW_RX", "tx_count": 0, "extra_rails": ["IR_RX_SWITCHED_3V3"]},
        {"mode": "TX_MAX_DUTY_ENVELOPE", "tx_count": 1, "extra_rails": ["IR_TX_FROM_3V3_MAIN"]},
    ],
    "LORA_CAP": [
        {"mode": "STOCK_U214_RX_GNSS_ONLY", "tx_count": 0, "extra_rails": ["5V_U214_PROTECTED"]},
        {"mode": "LESHY_CAP_RX", "tx_count": 0, "extra_rails": ["5V_U214_PROTECTED"]},
        {"mode": "LESHY_CAP_TX_MAX", "tx_count": 1, "extra_rails": ["5V_U214_PROTECTED"]},
    ],
    "M5_UNIT": [
        {"mode": "QUALIFIED_PROFILE_RX_OR_PASSIVE", "tx_count": 0, "extra_rails": ["5V_UNIT_PROTECTED"]},
        {"mode": "QUALIFIED_PROFILE_TX_MAX", "tx_count": 1, "extra_rails": ["5V_UNIT_PROTECTED"]},
    ],
    "BROADCAST_RX": [
        {"mode": "FM_AM_SW_LW_RX", "tx_count": 0, "extra_rails": ["RX_SWITCHED_3V3", "CODEC_SWITCHED_3V3"]},
    ],
}

SUPPORT_PROFILES = [
    {
        "id": "SUPPORT_IDLE",
        "concurrent": ["S3/C5/RP idle", "display on at minimum useful backlight", "touch/menu", "storage idle", "audio idle"],
    },
    {
        "id": "SUPPORT_WORST",
        "concurrent": ["S3/C5/RP peak compute", "display maximum backlight", "waterfall update", "microSD write", "audio path at group-legal maximum", "all ten indicators on"],
    },
]

REJECTED_PACK_CONDITIONS = [
    {"id": "ONE_CELL_ONLY", "result": "pack admission and charging rejected; USB may independently power the product"},
    {"id": "CELL_MISMATCH", "result": "pack isolated; service fault recorded"},
    {"id": "REVERSED_CELL", "result": "pack isolated; no charging or run from pack"},
    {"id": "OPEN_FUSE_OR_PROTECTION_TRIP", "result": "pack isolated; USB may independently power the product"},
    {"id": "PACK_TEMPERATURE_INVALID", "result": "charging inhibited; unsafe discharge causes pack isolation"},
    {"id": "UNQUALIFIED_OR_UNPROTECTED_CELL", "result": "installation is outside the product contract and must not be admitted"},
]


def charge_modes(usb: dict, pack: dict) -> list[str]:
    if usb["id"] == "USB_ABSENT":
        return ["PACK_DISCHARGE"] if pack["healthy"] else ["POWERLESS"]
    if usb["id"] == "USB_5V_FALLBACK":
        if pack["healthy"]:
            return ["CHARGE_INHIBITED_UNTIL_DPM_HEADROOM", "PACK_SUPPLEMENT_IF_REQUIRED"]
        return ["USB_LIMITED_NO_CHARGE"]
    if not pack["healthy"]:
        return ["USB_SYSTEM_SUPPLY_NO_CHARGE"]
    if pack["id"] == "PACK_2S_FULL":
        return ["CHARGE_TERMINATED", "RECHARGE_IF_THRESHOLD_REACHED"]
    return ["CHARGE_DISABLED", "CHARGE_INITIAL_1A", "CHARGE_MAX_2A_IF_HEADROOM"]


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    integration = json.loads(INTEGRATION.read_text(encoding="utf-8"))
    quiet = json.loads(QUIET_REVIEW.read_text(encoding="utf-8"))
    charge = json.loads(CHARGE_REVIEW.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    if methods.get("status") != "reviewed_reproducible_methods_and_pass_fail_frozen":
        raise ValueError("H3.0.3 is not reviewed")
    if charge["summary"]["configured_cell_count"] != 2:
        raise ValueError("accepted charger is not configured for 2S")
    accepted_pdos = candidate["power_contract"]["sink_pdos"]
    if accepted_pdos != ["5V fallback at advertised Type-C current (<=3A)", "9V@3A", "15V@2A"]:
        raise ValueError(f"unexpected accepted PDOs: {accepted_pdos}")

    groups = [row["firmware"] for row in integration["signal_groups"]]
    if groups != list(GROUP_MODES):
        raise ValueError(f"signal-group drift: {groups} != {list(GROUP_MODES)}")
    if not quiet["signal_group_policy"]["exclusive"] or quiet["signal_group_policy"]["internal_full_mix_exception"] != ["SG-N24"]:
        raise ValueError("quiet-state signal-group policy drift")

    source_states = []
    for usb in USB_PROFILES:
        for pack in PACK_PROFILES:
            for charge_mode in charge_modes(usb, pack):
                usb_present = usb["id"] != "USB_ABSENT"
                source_available = usb_present or pack["healthy"]
                run_allowed = source_available and not (
                    usb["id"] == "USB_5V_FALLBACK" and not pack["healthy"]
                )
                source_states.append(
                    {
                        "id": f"SRC-{len(source_states):03d}",
                        "usb": usb["id"],
                        "pack": pack["id"],
                        "charge_mode": charge_mode,
                        "aon_available": source_available,
                        "run_allowed": run_allowed,
                        "nvdc_sources": [x for x, enabled in (("USB", usb_present), ("PACK", pack["healthy"])) if enabled],
                    }
                )

    operating_profiles = []
    for group, modes in GROUP_MODES.items():
        for mode in modes:
            for support in SUPPORT_PROFILES:
                operating_profiles.append(
                    {
                        "signal_group": group,
                        "group_mode": mode["mode"],
                        "tx_count": mode["tx_count"],
                        "rx_count": mode.get("rx_count"),
                        "identity_permutations": mode.get("identity_permutations", 1),
                        "extra_rails": mode["extra_rails"],
                        "support_profile": support["id"],
                    }
                )

    states = []
    for source in source_states:
        if not source["aon_available"]:
            states.append({"id": f"PWR-{len(states):04d}", "source_state": source["id"], "system_mode": "UNPOWERED_OFF", "signal_group": "NONE"})
            continue
        states.append({"id": f"PWR-{len(states):04d}", "source_state": source["id"], "system_mode": "AON_SAFE_ONLY", "signal_group": "NONE"})
        if source["run_allowed"]:
            states.append({"id": f"PWR-{len(states):04d}", "source_state": source["id"], "system_mode": "FAULT_LATCHED_DIAGNOSTIC", "signal_group": "NONE"})
            for profile in operating_profiles:
                states.append({"id": f"PWR-{len(states):04d}", "source_state": source["id"], "system_mode": "RUN", **profile})

    violations = []
    for row in states:
        if row["system_mode"] != "RUN" and row["signal_group"] != "NONE":
            violations.append(f"{row['id']}: inactive mode has active group")
        if row["system_mode"] == "RUN" and row["signal_group"] not in GROUP_MODES:
            violations.append(f"{row['id']}: unknown group")
    nrf_modes = {row["mode"] for row in GROUP_MODES["NRF24"]}
    if nrf_modes != {"3PRX", "1PTX_2PRX", "2PTX_1PRX", "3PTX"}:
        violations.append("nRF24 full-mix set incomplete")
    if violations:
        raise ValueError("state invariant failures: " + "; ".join(violations[:10]))

    manifest = {
        "schema_version": 1,
        "stage": "H3.1.1",
        "status": "reviewed_all_legal_source_charge_and_operating_states_enumerated",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE, INTEGRATION, POWER_REVIEW, QUIET_REVIEW, CHARGE_REVIEW, METHODS)
        },
        "source_contract": {
            "external_source": "sole sink-only S3 USB-C; C5 and RP service USB VBUS are sense-only and never power the product",
            "usb_profiles": USB_PROFILES,
            "pack_topology": "two protected removable 18650 cells in series; 6.0 to 8.4 V; both cells required",
            "pack_profiles": PACK_PROFILES,
            "charger": "BQ25798 2S NVDC; starts conservatively at 1 A and is capped at 2 A subject to measured source/load/thermal headroom",
            "rejected_pack_conditions": REJECTED_PACK_CONDITIONS,
        },
        "operating_contract": {
            "top_level_active_group_count_max": 1,
            "groups": GROUP_MODES,
            "support_profiles": SUPPORT_PROFILES,
            "nrf24_internal_exception": "all three radios stay concurrently active in each required 3PRX/1PTX+2PRX/2PTX+1PRX/3PTX mix",
            "fault_mode": "AON safety plus restricted S3 local fault renderer/read-only record; no RF/IR/external-5V enable and no FAULT_KILL clear",
        },
        "source_states": source_states,
        "operating_profiles": operating_profiles,
        "states": states,
        "summary": {
            "usb_profiles": len(USB_PROFILES),
            "pack_profiles": len(PACK_PROFILES),
            "source_charge_states": len(source_states),
            "signal_groups": len(GROUP_MODES),
            "group_modes": sum(len(modes) for modes in GROUP_MODES.values()),
            "support_profiles": len(SUPPORT_PROFILES),
            "operating_profiles": len(operating_profiles),
            "legal_states": len(states),
            "rejected_pack_conditions": len(REJECTED_PACK_CONDITIONS),
            "invariant_violations": len(violations),
        },
        "next": {
            "stage": "H3.1.2",
            "action": "attach min/nom/max current and conversion-loss envelopes to every rail/load in every enumerated state",
        },
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
        title = "# Состояния питания Leshy2 · historical R1"
        nav = "[English](power-state-register.md) · [На главную](../README.ru.md) · [Питание](power-architecture.ru.md) · [Методы](verification-methods.ru.md)"
        intro = "Перед расчётом токов H3 перечисляет все допустимые источники, режимы зарядки и одновременные нагрузки. Так редкий режим не исчезнет внутри одной строки «максимальная мощность»."
        source_h = "## Источники"
        source = "Единственный внешний источник — sink-only USB-C: 5 В fallback с объявленным источником током, 5 В × 3 А, 9 В × 3 А или 15 В × 2 А. Автономный источник — только полный последовательный pack из двух защищённых 18650, 6,0–8,4 В. Один элемент не является рабочим режимом."
        coverage_h = "## Полнота"
        coverage = (
            f"- `{s['source_charge_states']}` сочетаний USB/pack/charge.\n"
            f"- `{s['signal_groups']}` взаимоисключающих signal groups и `{s['group_modes']}` внутренних режимов.\n"
            f"- `{s['operating_profiles']}` профилей нагрузки и `{s['legal_states']}` полных легальных состояний.\n"
            f"- `{s['rejected_pack_conditions']}` явно отклоняемых состояний pack; нарушений инвариантов: `{s['invariant_violations']}`."
        )
        nrf_h = "## Одновременная работа"
        nrf = "Одновременно активна только одна верхнеуровневая группа. Исключение находится внутри `SG-N24`: все три nRF24 остаются активными в `3PRX`, `1PTX+2PRX`, `2PTX+1PRX` и `3PTX`. Экран, waterfall, storage и разрешённый audio считаются параллельной поддерживающей нагрузкой и не исчезают из worst case."
        marker = "**Статус:** `H3.1.1` завершено и проверено. Текущий маркер — `H3.6.1`, worst-case thermal model плат, аккумуляторов и корпуса."
        evidence = "[Полный машинный реестр состояний](../hardware/verification/generated/H3-VRF11-power-state-register.json)."
    else:
        title = "# Leshy2 power states · historical R1"
        nav = "[Русский](power-state-register.ru.md) · [Home](../README.md) · [Power](power-architecture.md) · [Methods](verification-methods.md)"
        intro = "Before calculating current, H3 enumerates every allowed source, charge and concurrent-load state so a rare condition cannot disappear into one ‘maximum power’ row."
        source_h = "## Sources"
        source = "The sole external source is sink-only USB-C: 5 V fallback at source-advertised current, 5 V × 3 A, 9 V × 3 A or 15 V × 2 A. The autonomous source is only a complete series pack of two protected 18650 cells at 6.0–8.4 V. One cell is not an operating mode."
        coverage_h = "## Coverage"
        coverage = (
            f"- `{s['source_charge_states']}` USB/pack/charge combinations.\n"
            f"- `{s['signal_groups']}` mutually exclusive signal groups and `{s['group_modes']}` internal modes.\n"
            f"- `{s['operating_profiles']}` load profiles and `{s['legal_states']}` complete legal states.\n"
            f"- `{s['rejected_pack_conditions']}` explicitly rejected pack conditions; invariant violations: `{s['invariant_violations']}`."
        )
        nrf_h = "## Concurrent operation"
        nrf = "Only one top-level signal group is active at a time. The exception is internal to `SG-N24`: all three nRF24 radios remain active in `3PRX`, `1PTX+2PRX`, `2PTX+1PRX` and `3PTX`. Display, waterfall, storage and group-legal audio remain concurrent support loads in the worst case."
        marker = "**Status:** `H3.1.1` is complete and checked. Current marker is `H3.6.1`, worst-case board, battery and enclosure thermal model."
        evidence = "[Complete machine state register](../hardware/verification/generated/H3-VRF11-power-state-register.json)."
    return "\n\n".join((title, nav, intro, source_h, source, coverage_h, coverage, nrf_h, nrf, marker, evidence)) + "\n"


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
        print(f"ok: H3.1.1 states current; {s['source_charge_states']} source/charge, {s['legal_states']} legal, 0 invariant violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
