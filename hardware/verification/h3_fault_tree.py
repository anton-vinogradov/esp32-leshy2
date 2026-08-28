#!/usr/bin/env python3
"""Build the H3.6.2 single-fault containment and recovery review."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
H2_FAULT_PATH = REPO / "hardware/ecad/generated/H2-REV55-fault-kill.json"
TRANSITION_PATH = REPO / "hardware/verification/generated/H3-VRF24-watchdog-fault-display.json"
THERMAL_PATH = REPO / "hardware/verification/generated/H3-VRF61-thermal-model.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF62-fault-tree.json"
DOC_EN = REPO / "docs/single-fault-review.md"
DOC_RU = REPO / "docs/single-fault-review.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Decimal, quantum: str = "0.0001") -> str:
    return str(value.quantize(Decimal(quantum), rounding=ROUND_HALF_UP))


def fault(
    identifier: str,
    domain: str,
    mode: str,
    detection: str,
    primary: str,
    independent: str,
    result: str,
    recovery: str,
    classification: str = "contained",
    deadline_ms: int | None = 100,
) -> dict:
    return {
        "id": identifier,
        "domain": domain,
        "single_fault": mode,
        "detection": detection,
        "primary_path": primary,
        "independent_or_fail_safe_path": independent,
        "safe_result": result,
        "recovery": recovery,
        "classification": classification,
        "analytical_deadline_ms_max": deadline_ms,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    h2 = json.loads(H2_FAULT_PATH.read_text(encoding="utf-8"))
    transition = json.loads(TRANSITION_PATH.read_text(encoding="utf-8"))
    thermal = json.loads(THERMAL_PATH.read_text(encoding="utf-8"))
    safety = candidate["safety_contract"]
    instances = candidate["instances"]

    net_members = {
        (row["project"], row["net"]): set(row["instances"])
        for row in h2["reviewed_nets"]
    }

    def has(project: str, net: str, required: set[str]) -> bool:
        return required <= net_members.get((project, net), set())

    faults = [
        fault("SF-01", "physical command", "RUN moved to KILL or RUN conductor opens",
              "RUN_EDGE falls", "safe_run_fault_iso pulls FAULT_ASSERT_N low",
              "the second switch throw also requests protected-pack shutdown",
              "all TX gates become safe; C5/RP reset; no automatic restart",
              "condition safe, then physical KILL-to-RUN"),
        fault("SF-02", "physical command", "RUN_LOOP_RAW is shorted in the permissive state",
              "operator selects KILL and POWER_COMMAND_OFF_N falls",
              "safe_fault_reset_buffer channel 3 pulls FAULT_ASSERT_N low",
              "pack_admission independently receives the same KILL command",
              "the single masking short cannot defeat KILL",
              "service the switch/harness before physical re-arm"),
        fault("SF-03", "fault plane", "FAULT_ASSERT_N pull-up opens",
              "the wired plane falls through the 1-MOhm backup pull-down",
              "SAFE_CLEAR_N clears RUN_PERMIT", "endpoint pull-downs and direct reset sinks remain",
              "safe latched shutdown", "service, then physical KILL-to-RUN", deadline_ms=0),
        fault("SF-04", "fault plane", "FAULT_ASSERT_N is stuck low",
              "FAULT_ASSERT_SENSE remains low and RUN_PERMIT cannot set",
              "latch stays cleared", "direct reset and endpoint gates also stay asserted",
              "safe no-start", "service is required; software cannot override", deadline_ms=0),
        fault("SF-05", "fault plane", "FAULT_ASSERT_N is stuck at the permissive level before RUN",
              "P11 reads high through 100 kOhm while SAFETY_FAULT_REQUEST is held low",
              "the safety controller refuses every lease and re-arm admission",
              "the sense resistor prevents an expander-pin fault from dominating the plane",
              "safe no-admission with S3 held in fault/reset mode",
              "KILL plus service; the proof repeats at every physical re-arm",
              classification="detected_no_admission", deadline_ms=0),
        fault("SF-06", "application", "S3 application or system heartbeat stops",
              "TPS3435 window or safety-controller heartbeat monitor expires",
              "watchdog WDO_N clears the latch", "controller request remains an independent source",
              "bounded hard shutdown and retained reason", "physical KILL-to-RUN", deadline_ms=1760),
        fault("SF-07", "safety controller", "safety-controller firmware hangs",
              "WDI edges stop", "independent TPS3435 WDO_N clears RUN_PERMIT",
              "off-safe pulls do not depend on the controller",
              "bounded hard shutdown", "physical KILL-to-RUN", deadline_ms=1760),
        fault("SF-08", "AON supply", "AON voltage browns out or disappears",
              "TPS3808 POR_N asserts", "asynchronous latch clear",
              "reset-gate pull-ups, endpoint pull-downs and eFuse loss behavior are safe",
              "immediate safe state; final journal write may be unavailable",
              "next boot shows the explicit AON-loss fallback", deadline_ms=0),
        fault("SF-09", "primary latch", "RUN_PERMIT latch/output is stuck permissive",
              "latch/output readback mismatch or surviving TX evidence",
              "persistent SAFETY_FAULT_REQUEST pulls FAULT_ASSERT_N low",
              "direct C5/RP reset, nRF/CC backup gates, voice eFuse clamp and branch gates bypass RUN_PERMIT",
              "hazardous endpoints lose command or power",
              "physical KILL-to-RUN after service"),
        fault("SF-10", "processor reset", "one primary C5 or RP reset driver is stuck released",
              "fault assertion plus reset/rail evidence mismatch",
              "RUN_PERMIT path requests reset", "separate FAULT_ASSERT_N open-drain sink reaches the same EN/RUN node",
              "processor held reset by the independent sink",
              "physical KILL-to-RUN after service"),
        fault("SF-11", "processor reset", "one direct FAULT_ASSERT_N reset sink is stuck released",
              "fault assertion plus reset/rail evidence mismatch",
              "the separate RUN_PERMIT inverter and NMOS path asserts reset",
              "endpoint gates also remove transmitter power/commands",
              "processor and transmitters remain contained",
              "physical KILL-to-RUN after service"),
        fault("SF-12", "nRF24 power", "primary nRF rail gate is stuck high",
              "post-gate enable/evidence disagrees with RUN_PERMIT",
              "FAULT_ASSERT_N drives nrf_backup_gate low", "CE gates and Ioff buffers also default safe",
              "all three nRF24 rails/CE paths are contained without losing full-mix capability",
              "physical KILL-to-RUN after service"),
        fault("SF-13", "nRF24 power", "nRF backup gate is stuck high",
              "startup/fault-injection proof detects the final-enable mismatch",
              "the independent RUN_PERMIT-qualified primary gate falls",
              "CE gates and endpoint pull-down remain",
              "nRF group remains off for the single backup-gate fault",
              "physical KILL-to-RUN after service"),
        fault("SF-14", "nRF24 power", "nRF load switch is shorted on",
              "rail discharge/current proof or unexpected radio evidence",
              "three independent CE gates fall low", "host/return Ioff isolation and lease enforcement remain",
              "a switch short alone cannot command TX; actual TX is caught by physical evidence",
              "KILL and service; no further TX lease"),
        fault("SF-15", "CC1101 power", "primary CC rail gate is stuck high",
              "post-gate enable/evidence mismatch", "FAULT_ASSERT_N drives cc_backup_gate low",
              "SPI/GDO isolation and endpoint pull-down remain",
              "CC rail and command path become safe", "physical KILL-to-RUN after service"),
        fault("SF-16", "CC1101 power", "CC backup gate or load switch is stuck permissive",
              "startup/fault-injection proof or unexpected RF evidence",
              "RUN_PERMIT primary gate and isolated control path fall safe",
              "physical TX evidence catches any surviving carrier",
              "the fault alone cannot create an authorized command",
              "KILL and service; no further TX lease"),
        fault("SF-17", "voice power", "voice buck enable is stuck permissive",
              "voice rail/PG or TX evidence survives primary shutdown",
              "FAULT_ASSERT_N clamps TPS25974 EN/UVLO through safe_fault_reset_buffer",
              "hardware PTT remains receive-safe high",
              "protected voice rail and PTT become safe", "physical KILL-to-RUN after service"),
        fault("SF-18", "voice power", "voice eFuse fault clamp is stuck released",
              "fault-injection proof detects protected-rail mismatch",
              "RUN_PERMIT gate disables the upstream voice buck", "hardware PTT-off path remains",
              "voice transmitter loses rail or PTT", "physical KILL-to-RUN after service"),
        fault("SF-19", "voice PTT", "module-side PTT is stuck active",
              "voice RF detector asserts EV_N6/ANY_TX_AON_N",
              "persistent fault request removes the voice eFuse rail",
              "the primary buck gate also falls with RUN_PERMIT",
              "uncommanded voice TX is energy-bounded", "physical KILL-to-RUN after service"),
        fault("SF-20", "external power", "common external 5-V converter gate is stuck on",
              "branch readiness/current or external TX evidence mismatch",
              "each branch SN74LVC2G08 input receives direct FAULT_ASSERT_N",
              "each connector has its own true-reverse-blocking eFuse",
              "U214 and Unit branches both turn off independently of the common buck",
              "physical KILL-to-RUN after service"),
        fault("SF-21", "external branch", "one branch gate/eFuse is stuck permissive",
              "branch readiness/current or missing qualified evidence",
              "the common RUN_PERMIT-qualified converter is disabled",
              "the other branch remains isolated and unknown accessories receive no TX lease",
              "the single failed branch cannot retain base-supplied power after common shutdown",
              "KILL and service; accessory modes blocked"),
        fault("SF-22", "IR transmitter", "IR carrier safety gate is stuck permissive",
              "optical EV_N7 evidence or carrier mismatch",
              "direct FAULT_ASSERT_N resets C5", "C5 reset removes the shared TPS22919 emitter/receiver rail",
              "IR emitter loses both command and supply", "physical KILL-to-RUN after service"),
        fault("SF-23", "IR transmitter", "IR TPS22919 load switch is shorted on",
              "rail discharge/current proof or unexpected optical evidence",
              "RUN_PERMIT carrier gate falls", "MOSFET gate pull-down and C5 reset remain",
              "a rail short alone cannot produce optical TX", "KILL and service"),
        fault("SF-24", "TX supervision", "actual RF/IR TX occurs without a valid lease",
              "one EV_N source and ANY_TX_AON_N assert",
              "controller holds SAFETY_FAULT_REQUEST low", "persistent request survives the primary latch-path mismatch",
              "all transmitter gates are shut and the source identity is journaled",
              "physical KILL-to-RUN after service"),
        fault("SF-25", "TX evidence", "one comparator/output is stuck active-low",
              "one source bit remains asserted with no admitted TX",
              "conservative fault request", "aggregate ANY_TX_AON_N and front LED do not need software",
              "safe nuisance shutdown", "service, then physical KILL-to-RUN"),
        fault("SF-26", "TX evidence", "one comparator/output is stuck inactive or unreadable",
              "pre-TX evidence proof fails to toggle or private evidence I2C is unreadable",
              "proof-mandatory mode receives no lease", "normal endpoint gate remains off-safe",
              "safe no-admission for the affected transmitter",
              "service before the mode is available", classification="detected_no_admission"),
        fault("SF-27", "thermal sensing", "one NTC is open or shorted",
              "ADC code is outside the valid thermistor window",
              "safety controller requests hard fault", "watchdog covers a controller hang",
              "all hazardous power/TX is shut down", "service, then physical KILL-to-RUN"),
        fault("SF-28", "thermal sensing", "one NTC is plausibly stuck in-range",
              "startup trend/cross-zone plausibility and H8-correlated rate checks",
              "unattended admission uses bounded energy/time even with one unavailable zone",
              "converter/eFuse/chip thermal protections remain",
              "the sensor fault alone cannot create heat; the affected high-power profile is blocked",
              "service before unattended/high-power use", classification="detected_no_admission", deadline_ms=None),
        fault("SF-29", "power protection", "one eFuse/load path fails open",
              "PG/current/rail mismatch", "the affected domain loses power",
              "other rails remain protected and no automatic retry is allowed",
              "safe loss of function", "service required", deadline_ms=0),
        fault("SF-30", "fault record", "power disappears during journal commit",
              "neither CRC slot has a newer valid commit marker",
              "hardware loss behavior is already safe",
              "next boot selects the last valid slot or explicit power-loss fallback",
              "no fabricated cause is shown", "read-only service export, then physical recovery", deadline_ms=0),
    ]

    fault_pullup = instances["fault_assert_pullup"] == "yageo_rc0402fr_0710kl"
    fault_pulldown = instances["fault_assert_backup_pulldown"] == "yageo_rc0402fr_071ml"
    sense_series = instances["fault_assert_sense_series"] == "yageo_rc0402fr_07100kl"
    healthy_fault_v = Decimal("3.3") * Decimal("1000000") / Decimal("1010000")
    checks = {
        "h2_fault_review_is_closed": h2["status"] == "reviewed_watchdog_thermal_fault_and_hardware_shutdown",
        "h2_selected_nets_are_complete": h2["reviewed_net_count"] >= 61,
        "fault_plane_has_primary_and_backup_consumers": has(
            "LESHY2-RF", "FAULT_ASSERT_N",
            {"safe_gate_b", "safe_fault_reset_buffer", "nrf_backup_gate", "cc_backup_gate", "ext_branch_gate"},
        ),
        "ui_has_direct_c5_fault_reset": has(
            "LESHY2-UI", "FAULT_ASSERT_N", {"m1_ui_plug", "safe_c5_fault_reset_buffer"}
        ),
        "fault_plane_readback_is_series_isolated": has(
            "LESHY2-RF", "FAULT_ASSERT_SENSE", {"fault_assert_sense_series", "evidence_mask"}
        ),
        "second_switch_throw_reaches_fault_buffer": has(
            "LESHY2-RF", "POWER_COMMAND_OFF_N",
            {"power_command_switch", "pack_admission", "safe_fault_reset_buffer"},
        ),
        "nrf_primary_and_backup_gates_are_distinct": has(
            "LESHY2-RF", "NRF_GROUP_PWR_EN_PRIMARY", {"safe_gate_a", "nrf_backup_gate"}
        ) and has(
            "LESHY2-RF", "NRF_GROUP_PWR_EN_SAFE", {"nrf_backup_gate", "nrf_power_switch"}
        ),
        "cc_primary_and_backup_gates_are_distinct": has(
            "LESHY2-RF", "CC_PWR_EN_PRIMARY", {"safe_gate_b", "cc_backup_gate"}
        ) and has(
            "LESHY2-RF", "CC_PWR_EN_SAFE", {"cc_backup_gate", "cc_power_switch"}
        ),
        "voice_has_independent_efuse_clamp": has(
            "LESHY2-RF", "VOICE_EFUSE_BACKUP_EN_N",
            {"safe_fault_reset_buffer", "voice_efuse_en_pullup", "voice_efuse"},
        ),
        "c5_primary_and_direct_reset_paths_are_distinct": has(
            "LESHY2-UI", "C5_RESET_KILL_GATE", {"safe_c5_reset_buffer", "safe_reset_sink_a"}
        ) and has(
            "LESHY2-UI", "C5_RESET_N", {"safe_c5_fault_reset_buffer", "safe_reset_sink_a", "c5"}
        ),
        "fault_bias_exact_parts_are_fitted": fault_pullup and fault_pulldown and sense_series,
        "healthy_fault_level_exceeds_3v_logic_high": healthy_fault_v > Decimal("3.0"),
        "fault_plane_startup_proof_is_mandatory": "must also read low" in safety["watchdog"]["fault_plane_proof"],
        "fault_request_is_persistent_after_primary_failure": "holds SAFETY_FAULT_REQUEST low continuously" in safety["watchdog"]["persistent_fault_request"],
        "only_physical_rearm_is_allowed": "only re-arm action is a physical KILL-to-RUN edge" in safety["latch_logic"]["rearm"],
        "nine_physical_tx_evidence_channels_remain": len(safety["evidence"]["channels"]) == 9,
        "fault_matrix_includes_new_plane_proof": len(safety["fault_matrix"]) == 11,
        "watchdog_max_deadline_is_1760ms": transition["watchdog"]["timeout_s"]["max"] == 1.76,
        "transition_review_has_no_failed_fault_scenario": transition["summary"]["failed_scenarios"] == 0,
        "thermal_review_has_no_open_analytical_finding": thermal["review_summary"]["unresolved_analytical_findings"] == 0,
        "all_faults_have_detection_and_two_paths": all(
            row["detection"] and row["primary_path"] and row["independent_or_fail_safe_path"]
            for row in faults
        ),
        "all_faults_end_contained_or_no_admission": all(
            row["classification"] in {"contained", "detected_no_admission"} for row in faults
        ),
        "all_faults_have_explicit_recovery": all(row["recovery"] for row in faults),
        "no_software_rearm_is_claimed": all("software re-arm" not in row["recovery"] for row in faults),
        "safety_improvement_uses_no_new_mpn_or_gpio": safety["independent_containment"]["new_mpn_count"] == 0
        and safety["independent_containment"]["gpio_delta"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.6.2 checks failed: " + ", ".join(failed))

    corrections = [
        {
            "id": "H3.6.2-F01",
            "finding": "a stuck-permissive RUN_PERMIT latch or primary endpoint gate could preserve transmitter power",
            "correction": "separate direct FAULT_ASSERT_N reset sinks, nRF/CC backup gates, voice eFuse clamp, expansion-branch qualification and the shared reset-off IR rail were fitted",
            "cost_delta_usd_at_100": q(Decimal(str(safety["independent_containment"]["cost_delta_usd_at_100"]))),
        },
        {
            "id": "H3.6.2-F02",
            "finding": "a FAULT_ASSERT_N line stuck permissive was latent before transmitter admission",
            "correction": "unused TCA9535 P11 and its existing resistor position became a 100-kOhm series-isolated startup proof input",
            "cost_delta_usd_at_100": "0.0000",
        },
        {
            "id": "H3.6.2-F03",
            "finding": "RUN_LOOP_RAW shorted permissive could mask the RUN-side KILL path",
            "correction": "the second SPDT throw now reaches FAULT_ASSERT_N through the already fitted spare SN74LVC3G07 channel as well as requesting pack shutdown",
            "cost_delta_usd_at_100": "0.0000",
        },
    ]
    residual = [
        "H6: physically separate RUN_PERMIT and FAULT_ASSERT_N routing, their local buffers and endpoint gate returns; verify no single via/pad short joins both paths",
        "H8: inject every SF-01..SF-30 case at accessible pads and verify rail fall, no RF/optical output, retained reason and physical-only re-arm",
        "H8: calibrate evidence thresholds and prove stuck-active, stuck-inactive and unreadable evidence behavior for all nine channels",
        "H8: measure watchdog, reset, eFuse, QOD and transmitter-energy deadlines; analytical 0/100/1760-ms classes are upper-level contracts, not measured closure",
        "H8: interrupt every two-slot flash-journal write boundary and verify last-valid-slot or explicit AON-loss fallback",
        "H3.6.3: bound the uninterrupted unattended interval because FAULT_ASSERT_N proof is service-interrupting and therefore occurs at physical re-arm, not continuously; it does not damage hardware",
    ]
    non_claims = [
        "two simultaneous independent faults or a first latent safety fault followed by a second hazard",
        "common physical damage that shorts both independent shutdown routes or bypasses a protected rail directly",
        "guaranteed final diagnostic write after complete AON loss",
        "production-safe timing, RF silence or temperature without H6 layout and H8 measured fault injection",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.6.2",
        "status": "reviewed_single_fault_containment_and_recovery",
        "method": "deterministic FMEA over fault sources, primary shutdown, an electrically separate or fail-safe containment path, retained reason and physical recovery",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, H2_FAULT_PATH, TRANSITION_PATH, THERMAL_PATH)
        },
        "fault_plane": {
            "healthy_nominal_v": q(healthy_fault_v),
            "bias": "10-kOhm AON pull-up plus 1-MOhm fail-low pull-down",
            "proof": safety["watchdog"]["fault_plane_proof"].rsplit("; ", 1)[0]
            + "; it is service-interrupting, not hardware-damaging, and no mid-session proof is claimed",
            "sense": "TCA9535 P11 through 100-kOhm series isolation",
            "service_interrupting_proof_boundary": "every physical KILL-to-RUN; never silently re-arms during a running session; interrupts service but does not damage hardware",
        },
        "faults": faults,
        "corrections": corrections,
        "checks": checks,
        "open_findings": [],
        "pending_decisions": [],
        "residual_physical_only": residual,
        "non_claims": non_claims,
        "review_summary": {
            "single_fault_cases": len(faults),
            "checks": len(checks),
            "failed": 0,
            "corrected_findings": len(corrections),
            "unresolved_analytical_findings": 0,
            "incremental_bom_usd_at_100": q(Decimal(str(safety["independent_containment"]["cost_delta_usd_at_100"]))),
            "status": "reviewed",
        },
        "next": {
            "stage": "H3.6.3",
            "action": "verify the bounded 24-to-48-hour unattended operating envelope, including the maximum interval between service-interrupting fault-plane proofs",
        },
    }
    return {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(manifest, russian=False),
        DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Проверка единичных отказов · historical R1"
        intro = (
            f"`H3.6.2` проведён ревью: {manifest['review_summary']['single_fault_cases']} сценариев и "
            f"{manifest['review_summary']['checks']} машинных checks проходят. Точный маркер — `H3.6.3`."
        )
        explanation = (
            "Для каждого отказа указаны обнаружение, основной путь отключения, независимый или fail-safe путь, "
            "безопасный результат и восстановление. Проверка fault-plane на границе KILL → RUN прерывает работу, "
            "но не повреждает железо. Автоматического повторного запуска нет."
        )
        headers = "| Область | Единичный отказ | Результат |\n|---|---|---|"
        rows = "\n".join(
            f"| {row['domain']} | {row['single_fault']} | {row['safe_result']} |" for row in manifest["faults"]
        )
        corrected = "## Исправлено\n\n" + "\n".join(
            f"- `{row['id']}` — {row['correction']}" for row in manifest["corrections"]
        )
        limits = "## Граница результата\n\nНе заявляются: " + "; ".join(manifest["non_claims"]) + "."
        evidence = "[Машинное evidence](../hardware/verification/generated/H3-VRF62-fault-tree.json)."
    else:
        title = "# Single-fault review · historical R1"
        intro = (
            f"`H3.6.2` is reviewed: {manifest['review_summary']['single_fault_cases']} scenarios and "
            f"{manifest['review_summary']['checks']} machine checks pass. The exact marker is `H3.6.3`."
        )
        explanation = (
            "Every fault records detection, the primary shutdown path, an independent or fail-safe path, "
            "the safe result and recovery. The KILL-to-RUN fault-plane proof is service-interrupting but does not "
            "damage hardware. Automatic restart is forbidden."
        )
        headers = "| Domain | Single fault | Result |\n|---|---|---|"
        rows = "\n".join(
            f"| {row['domain']} | {row['single_fault']} | {row['safe_result']} |" for row in manifest["faults"]
        )
        corrected = "## Corrections\n\n" + "\n".join(
            f"- `{row['id']}` — {row['correction']}" for row in manifest["corrections"]
        )
        limits = "## Result boundary\n\nNot claimed: " + "; ".join(manifest["non_claims"]) + "."
        evidence = "[Machine evidence](../hardware/verification/generated/H3-VRF62-fault-tree.json)."
    return "\n\n".join((title, intro, explanation, headers + "\n" + rows, corrected, limits, evidence)) + "\n"


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
        stale = [
            str(path.relative_to(REPO))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale H3.6.2 artifacts: " + ", ".join(stale))
    print(
        f"ok: H3.6.2 reviewed; {manifest['review_summary']['single_fault_cases']} cases, "
        f"{manifest['review_summary']['checks']} checks, next H3.6.3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
