#!/usr/bin/env python3
"""Review H2.5.5 watchdog, thermal supervision and FAULT_KILL fan-out."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path

from h2_review_power_paths import (
    CANDIDATE_PATH,
    ECAD,
    LEDGER_PATH,
    PROJECTS,
    REPO,
    export_project,
    instance_reference_maps,
    sha256,
)
from h2_ui_audio_codec_headset import endpoint_nets


GENERATED = ECAD / "generated"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
OUTPUT_MANIFEST = GENERATED / "H2-REV55-fault-kill.json"
OUTPUT_DOC_EN = REPO / "docs/fault-shutdown.md"
OUTPUT_DOC_RU = REPO / "docs/fault-shutdown.ru.md"

REVIEWED_NETS = {
    "LESHY2-RF": (
        "AON_SAFE_3V3", "RUN_LOOP_RAW", "RUN_EDGE", "SAFE_REARM_DELAY",
        "SAFE_REARM_CLK", "FAULT_ASSERT_N", "SAFE_CLEAR_N",
        "FAULT_ASSERT_SENSE",
        "SAFETY_WATCHDOG_WDI", "POR_N", "FAULT_LATCH_SENSE_AON", "RUN_PERMIT",
        "RF_RESET_KILL_GATE", "S3_RESET_KILL_GATE", "S3_FAULT_RESET_REQUEST",
        "SAFETY_FAULT_REQUEST", "POWER_COMMAND_OFF_N", "POWER_ZONE_TEMP_ADC", "RF_ZONE_TEMP_ADC",
        "UI_ZONE_TEMP_ADC", "POWER_FAULT_N", "ANY_TX_AON_N", "RP_ANY_TX_N",
        "NRF0_CE_SAFE", "NRF1_CE_SAFE", "NRF2_CE_SAFE",
        "NRF_GROUP_PWR_EN_PRIMARY", "NRF_GROUP_PWR_EN_SAFE",
        "CC_PWR_EN_PRIMARY", "CC_PWR_EN_SAFE", "VOICE_DOMAIN_EN_SAFE",
        "VOICE_EFUSE_BACKUP_EN_N", "VOICE_PTT_SAFE_N",
        "EXT_ANY_5V_EN_SAFE", "U214_5V_EN_SAFE", "UNIT_5V_EN_SAFE",
        "EV_N0_S3", "EV_N1_C5", "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2",
        "EV_N5_CC", "EV_N6_VOICE", "EV_N7_IR", "EV_N8_LORA_EXT",
    ),
    "LESHY2-UI": (
        "RUN_PERMIT", "FAULT_ASSERT_N", "C5_RESET_KILL_GATE", "S3_RESET_KILL_GATE",
        "S3_RESET_N", "C5_RESET_N", "IR_TX_CARRIER_SAFE", "UI_ZONE_TEMP_ADC",
        "EV_N0_S3", "EV_N1_C5", "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2",
        "EV_N5_CC", "EV_N6_VOICE", "EV_N7_IR", "EV_N8_LORA_EXT",
    ),
}

CRITICAL_INSTANCES = (
    "power_command_switch", "safe_supervisor", "safety_controller", "safety_watchdog",
    "safe_conditioner", "safe_rearm_buffer", "safe_latch", "safe_reset_buffer", "safe_reset_sink_a",
    "safe_reset_sink_b", "safe_c5_reset_buffer", "safe_c5_fault_reset_buffer",
    "safe_fault_reset_buffer", "safe_gate_a", "safe_gate_b", "nrf_backup_gate",
    "cc_backup_gate", "fault_assert_backup_pulldown", "voice_efuse_en_pullup", "safe_ptt_or",
    "fault_assert_sense_series",
    "safety_fault_request_iso", "safety_s3_reset_iso", "power_zone_ntc",
    "rf_zone_ntc", "ui_zone_ntc", "evidence_mask", "evidence_main_isolator",
    "fault_led",
)


def expected_members(candidate: dict, ledger: dict, sheet_contract: dict, project: str) -> dict[str, set[str]]:
    local = {row["instance"] for row in ledger["rows"] if row["project"] == project}
    root_name = "UI" if project == "LESHY2-UI" else "RF"
    root = json.loads((GENERATED / f"H2-{root_name}-root-interface.json").read_text(encoding="utf-8"))
    interface_order = [net for sheet in root["sheets"] for net in sheet["interfaces"]]
    endpoints, _, _ = endpoint_nets(candidate, local, interface_order)
    by_net: dict[str, set[str]] = defaultdict(set)
    for (instance, _), net in endpoints.items():
        by_net[net].add(instance)
    for point in sheet_contract["test_point_contracts"]:
        if point["project"] == project:
            by_net[point["net"]].add(point["id"])
    m1_instance = "m1_ui_plug" if project == "LESHY2-UI" else "m1_rf_receptacle"
    for contact in candidate["interboard_contract"]["pin_map"]:
        by_net[contact["net"]].add(m1_instance)
    return by_net


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    sheet_contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    safety = candidate["safety_contract"]
    if safety["latch_logic"]["rearm"] != (
        "the only re-arm action is a physical KILL-to-RUN edge clocking fixed D=1. A 100-kOhm/2.2-uF RC and SN74LVC1G17 Schmitt buffer delay and clean that edge beyond the TPS3808 28-ms maximum POR window; a held RUN state cannot re-arm after a fault, and automatic restart is forbidden"
    ):
        raise ValueError("physical-only re-arm contract drifted")
    if len(safety["tx_gate_map"]) != 9 or len(safety["evidence"]["channels"]) != 9:
        raise ValueError("nine TX gate/evidence channels must remain explicit")
    if len(safety["fault_matrix"]) != 11:
        raise ValueError("fault matrix must retain eleven reviewed source classes")

    reference_maps, details = instance_reference_maps()
    actual_nets = {}
    stats = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h255-") as temp_dir:
        for project in REVIEWED_NETS:
            actual_nets[project], stats[project] = export_project(
                project, PROJECTS[project], Path(temp_dir) / f"{project}.xml"
            )

    reviewed = []
    for project, names in REVIEWED_NETS.items():
        expected = expected_members(candidate, ledger, sheet_contract, project)
        ref_map = reference_maps[project]
        for net in names:
            refs = actual_nets[project].get(net, set())
            if not refs:
                raise ValueError(f"{project} safety net is absent: {net}")
            unknown = sorted(refs - ref_map.keys())
            if unknown:
                raise ValueError(f"{project}/{net} has unmapped references: {unknown}")
            actual = {ref_map[ref] for ref in refs}
            if actual != expected.get(net, set()):
                raise ValueError(
                    f"{project}/{net} membership drifted; "
                    f"missing={sorted(expected.get(net, set()) - actual)}, "
                    f"extra={sorted(actual - expected.get(net, set()))}"
                )
            reviewed.append({"project": project, "net": net, "instances": sorted(actual)})

    parts = []
    for instance in CRITICAL_INSTANCES:
        row = details.get(instance)
        if not row or not row.get("mpn") or not row.get("footprint"):
            raise ValueError(f"safety component lacks exact MPN/footprint: {instance}")
        parts.append({
            "instance": instance, "reference": row["reference"],
            "mpn": row["mpn"], "footprint": row["footprint"],
        })

    physical_pads = {
        row["instance"]
        for name in ("H2-UI60-testpoints-manufacturing.json", "H2-RF60-testpoints-manufacturing.json")
        for row in json.loads((GENERATED / name).read_text(encoding="utf-8"))["instances"]
    }
    required_pads = set(safety["test_points"])
    if not required_pads <= physical_pads:
        raise ValueError(f"safety contract lacks physical pads: {sorted(required_pads - physical_pads)}")

    manifest = {
        "schema_version": 1,
        "stage": "H2.5.5",
        "status": "reviewed_watchdog_thermal_fault_and_hardware_shutdown",
        "method": "exact complete-KiCad-netlist membership review from physical RUN/KILL and watchdog through latch, reset/gate fan-out, thermal/evidence sensing and diagnostic pads",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, LEDGER_PATH, SHEET_CONTRACT_PATH,
                         PROJECTS["LESHY2-UI"], PROJECTS["LESHY2-RF"])
        },
        "hierarchy_exports": stats,
        "corrected_findings": [
            {
                "id": "H2.5.5-F01",
                "severity": "hil_blocking",
                "finding": "the safety contract promised watchdog, latch and safe-gate observation points but 15 distinct electrical nodes had no physical copper pad",
                "correction": "RF60 now contains 52 BOM-free pads; WDO_N uses the shared FAULT_ASSERT_N pad, FAULT_KILL uses its implemented FAULT_LATCH_SENSE_AON name and RP reset uses TP_RP_RESET_N",
                "evidence": "every normalized safety_contract.test_points identifier is instantiated on UI60 or RF60 and every selected safety net matches the complete KiCad hierarchy",
            },
            {
                "id": "H3.6.2-F01",
                "severity": "single_fault_containment",
                "finding": "the former fan-out reused RUN_PERMIT-derived qualification for every hazardous endpoint, so one stuck-permissive latch or primary gate was not independently contained",
                "correction": "M1 contact 34 now carries direct FAULT_ASSERT_N; separate C5/RP reset sinks, nRF/CC backup gates, the voice eFuse clamp and independent expansion-branch inputs bypass the primary latch path",
                "evidence": "the primary enable nets, final safe enables and direct fault plane all have distinct exact component membership in the complete UI and RF KiCad hierarchies",
            },
        ],
        "reviewed_net_count": len(reviewed),
        "reviewed_nets": reviewed,
        "critical_components": parts,
        "physical_safety_test_point_count": len(required_pads),
        "fault_matrix": safety["fault_matrix"],
        "shutdown_chain": [
            "maintained RUN/KILL, open run loop, TPS3435 WDO_N or isolated safety-controller request pulls FAULT_ASSERT_N low",
            "FAULT_ASSERT_N asynchronously clears the SN74LVC1G74 RUN_PERMIT latch; software cannot set or re-arm it",
            "the primary RUN_PERMIT path and electrically separate FAULT_ASSERT_N path both disable nRF24 and CC rails, voice power/PTT and both expansion branches",
            "independent C5 and RP fault-reset sinks assert; the shared IR rail falls with C5 reset, while S3 receives a bounded fault-reset request and may only run the signed fault-only renderer while UI temperature is safe",
            "three NTC zones, aggregate power fault and nine physical-TX evidence channels remain visible to the independent AON safety controller",
            "restart requires all release conditions safe plus a physical KILL-to-RUN cycle",
        ],
        "review_boundary": {
            "complete": [
                "the independent MSPM0 safety controller, TPS3435 watchdog, AON supervisor, asynchronous latch and backup endpoint gates are exact fitted parts",
                "all selected fault, temperature, evidence, reset and safe-gate nets match actual complete KiCad netlists",
                "all contractually required safety measurements now terminate on physical copper",
            ],
            "deferred": [
                "watchdog timing, NTC thresholds/placement and rail-fall timing simulation in H3",
                "fault-only renderer, retained record and lease state-machine execution in firmware F3",
                "open/short/stuck/high-temperature/unauthorized-TX fault injection and visible-screen behavior in H8",
            ],
        },
    }
    return {
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        OUTPUT_DOC_EN: render_doc(manifest, russian=False),
        OUTPUT_DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Аварийное отключение Leshy2"
        nav = "[English](fault-shutdown.md) · [На главную](../README.ru.md) · [Тихое состояние](quiet-state.ru.md)"
        intro = "Аварийное выключение не зависит от S3, меню или основного приложения и не перезапускает передатчики автоматически."
        headers = "| Источник | Аппаратный результат |\n|---|---|"
        rows = [
            "| RUN переведён в KILL или провод оборван | асинхронный latch; TX/power gates safe; C5/RP reset |",
            "| heartbeat отсутствует/неверен | TPS3435 либо lease-monitor защёлкивает fault |",
            "| TX без действующей lease | physical evidence защёлкивает fault |",
            "| POWER или RF/VOICE перегрет | всё опасное off; cool UI показывает причину |",
            "| UI/DISPLAY перегрет | UI тоже off; остаётся независимый янтарный FAULT LED |",
            "| AON brownout | supervisor и off-safe pulls удерживают безопасное состояние |",
        ]
        result = f"## Результат H2.5.5\n\n✅ **Проведено ревью:** {manifest['reviewed_net_count']} safety-цепей проверены по полным KiCad-netlist; все {manifest['physical_safety_test_point_count']} требуемые точки диагностики теперь существуют как медь."
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV55-fault-kill.json)."
    else:
        title = "# Leshy2 fault shutdown"
        nav = "[Русский](fault-shutdown.ru.md) · [Home](../README.md) · [Quiet state](quiet-state.md)"
        intro = "Emergency shutdown does not depend on S3, the menu or the main application and never restarts transmitters automatically."
        headers = "| Source | Hardware result |\n|---|---|"
        rows = [
            "| RUN moved to KILL or conductor opens | asynchronous latch; TX/power gates safe; C5/RP reset |",
            "| heartbeat missing or invalid | TPS3435 or lease monitor latches the fault |",
            "| TX without a valid lease | physical evidence latches the fault |",
            "| POWER or RF/VOICE overheats | every hazardous path off; cool UI reports the cause |",
            "| UI/DISPLAY overheats | UI also off; independent amber FAULT LED remains |",
            "| AON brownout | supervisor and off-safe pulls hold the safe state |",
        ]
        result = f"## H2.5.5 result\n\n✅ **Reviewed:** {manifest['reviewed_net_count']} safety nets match complete KiCad netlists; all {manifest['physical_safety_test_point_count']} required diagnostic points now exist as copper."
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV55-fault-kill.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(rows), result, evidence)) + "\n"


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
        stale = [path for path, content in outputs.items()
                 if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.5.5 fault-shutdown review is current; {manifest['reviewed_net_count']} nets reviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
