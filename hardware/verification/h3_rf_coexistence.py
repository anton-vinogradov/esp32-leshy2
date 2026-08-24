#!/usr/bin/env python3
"""Verify H3.5.3 one-group isolation, quiet state and full 3x nRF concurrency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
POWER_PATH = REPO / "hardware/verification/generated/H3-VRF11-power-state-register.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
LEVEL_PATH = REPO / "hardware/verification/generated/H3-VRF41-digital-levels.json"
TIMING_PATH = REPO / "hardware/verification/generated/H3-VRF42-digital-timing.json"
LAYOUT_PATH = REPO / "hardware/verification/generated/H3-VRF52-rf-layout-constraints.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF53-rf-coexistence.json"
DOC_EN = REPO / "docs/rf-coexistence.md"
DOC_RU = REPO / "docs/rf-coexistence.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    power = json.loads(POWER_PATH.read_text(encoding="utf-8"))
    dc = json.loads(DC_PATH.read_text(encoding="utf-8"))
    levels = json.loads(LEVEL_PATH.read_text(encoding="utf-8"))
    timing = json.loads(TIMING_PATH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))

    policy = candidate["signal_group_policy"]
    quiet_policy = candidate["quiet_state_policy"]
    i6 = candidate["i6_consolidated_qualification_contract"]
    groups = {row["id"]: row for row in policy["groups"]}
    quiet = {row["id"]: row for row in quiet_policy["contracts"]}
    group_to_operating = {
        "SG-N24": "NRF24",
        "SG-S3-24": "S3_RF",
        "SG-C5-NATIVE": "C5_RF",
        "SG-CC": "CC1101",
        "SG-VOICE": "VOICE",
        "SG-BROADCAST": "BROADCAST_RX",
        "SG-U214": "LORA_CAP",
        "SG-IR": "IR",
        "SG-EXT-*": "M5_UNIT",
    }
    group_to_quiet = {
        "SG-N24": ["N24_QUIET"],
        "SG-S3-24": ["S3_RF_QUIET"],
        "SG-C5-NATIVE": ["C5_RF_QUIET"],
        "SG-CC": ["CC_QUIET"],
        "SG-VOICE": ["VOICE_QUIET", "VOICE_INTERFACE_QUIET"],
        "SG-BROADCAST": ["RECEIVER_QUIET"],
        "SG-U214": ["U214_CAP_QUIET"],
        "SG-IR": ["IR_QUIET"],
        "SG-EXT-*": ["UNIT_PORT_QUIET"],
    }
    radio_quiet_ids = sorted({item for values in group_to_quiet.values() for item in values})
    support_quiet_ids = ["CODEC_AUDIO_QUIET", "STORAGE_QUIET", "SERVICE_IPC_QUIET"]

    matrix = []
    for group_id in i6["covered_signal_groups"]:
        own = set(group_to_quiet[group_id])
        matrix.append({
            "signal_group": group_id,
            "operating_group": group_to_operating[group_id],
            "active_members": groups[group_id]["members"],
            "required_foreign_quiet_contracts": [item for item in radio_quiet_ids if item not in own],
            "support_contract": "UI/safety/thermal remain available; audio/storage/service run only when profile-declared and otherwise use their quiet contracts",
        })

    nrf = groups["SG-N24"]
    operating_profiles = power["operating_profiles"]
    nrf_profiles = [row for row in operating_profiles if row["signal_group"] == "NRF24"]
    required_modes = {"3PRX", "1PTX_2PRX", "2PTX_1PRX", "3PTX"}
    required_mixes = {"3PRX", "1PTX+2PRX", "2PTX+1PRX", "3PTX"}
    nrf_permutations = sum(row["identity_permutations"] for row in power["operating_contract"]["groups"]["NRF24"])
    nrf_dc = [row for row in dc["profiles"] if row["signal_group"] == "NRF24"]
    nrf_corridors = [row for row in layout["path_corridors"] if row["id"].startswith("N24-")]
    exclusive = set(candidate["exclusive_resource_contracts"])
    timing_checks = timing["checks"]
    level_checks = levels["checks"]

    transition = [
        "revoke the current group lease and close every software TX request",
        "wait for every current-group physical actual-TX evidence source to become inactive; inbound-energy false positives may delay but never bypass this gate",
        "stop protocol engines, scans, polling, PIO/DMA and periodic logs; park active controls in their stated safe levels",
        "disable digital OEs/isolation, then remove the old switched rail and prove its discharge/quiet contract",
        "if any state, identity, timeout or evidence result is unknown: enter NONE, keep every TX disarmed and require a fresh physical KILL-to-RUN re-arm",
        "admit only the selected new group's exact manifest, power it, honor POR/supervisor timing and complete identity/self-test",
        "load region, antenna/feed-loss, power and duty profile; arm TX only after all preceding gates pass",
    ]
    acceptance = {
        "top_level_runtime": "exactly zero or one signal group; cross-group simultaneous operation is prohibited",
        "quiet": i6["acceptance"]["quiet"],
        "no_stall": i6["acceptance"]["no_stall"],
        "nrf_full_mix": "T1 target plus independent observer must prove each identity permutation at 3PRX, 1PTX+2PRX, 2PTX+1PRX and 3PTX with no hidden standby or RX gap; every peer receiver must stay within the profile's 3-dB degradation limit",
        "lab_injection": "cross-group interference injection is allowed only as contained Laboratory characterization/fault evidence and never becomes runtime permission",
        "fault": i6["acceptance"]["fault"],
    }

    checks = {
        "h352_is_reviewed": layout["review_summary"]["status"] == "reviewed",
        "one_top_level_group_is_hard_limit": power["operating_contract"]["top_level_active_group_count_max"] == 1 and i6["runtime_invariant"]["top_level_active_group_count_max"] == 1,
        "cross_group_runtime_is_prohibited": i6["runtime_invariant"]["cross_group_simultaneous_runtime"] == "prohibited",
        "unknown_fails_to_none_and_tx_disarmed": i6["runtime_invariant"]["unknown_or_timeout_result"] == "NONE_and_all_TX_disarmed",
        "default_group_is_none": policy["default_group"] == "NONE" and quiet_policy["default_state"] == "QUIET",
        "all_nine_signal_groups_covered": set(groups) == set(i6["covered_signal_groups"]) == set(group_to_operating),
        "all_operating_groups_mapped": set(group_to_operating.values()) == set(power["operating_contract"]["groups"]) - {"NONE"},
        "all_13_quiet_contracts_present": set(quiet) == set(quiet_policy["required_contracts"]) and len(quiet) == 13,
        "all_radio_quiet_contracts_mapped": set(radio_quiet_ids) == set(quiet) - set(support_quiet_ids),
        "every_group_has_all_foreign_quiet_contracts": all(len(row["required_foreign_quiet_contracts"]) == len(radio_quiet_ids) - len(group_to_quiet[row["signal_group"]]) for row in matrix),
        "digital_quiet_review_is_closed": level_checks["all_13_quiet_contracts_reviewed"] and level_checks["all_required_quiet_groups_present"],
        "digital_no_back_power_is_closed": level_checks["six_no_back_power_invariants_preserved"] and levels["review_scope"]["analytical_findings_open"] == 0,
        "nrf_has_three_members": nrf["members"] == ["nrf0", "nrf1", "nrf2"],
        "nrf_full_mix_is_required": nrf["full_mix"] is True and set(nrf["required_role_mixes"]) == required_mixes,
        "nrf_peer_standby_is_forbidden": nrf["peer_standby_forbidden"] is True and "no peer standby" in nrf["mode"],
        "nrf_all_four_modes_are_power_profiles": {row["group_mode"] for row in nrf_profiles} == required_modes,
        "nrf_both_support_profiles_are_covered": {row["support_profile"] for row in nrf_profiles} == {"SUPPORT_IDLE", "SUPPORT_WORST"},
        "nrf_eight_identity_permutations": nrf_permutations == 8,
        "nrf_power_profiles_cover_16_identity_mode_support_cases": sum(row["identity_permutations"] for row in nrf_profiles) == 16,
        "nrf_dc_covers_all_modes_and_support_profiles": {(row["group_mode"], row["support_profile"]) for row in nrf_dc} == {(m, s) for m in required_modes for s in ("SUPPORT_IDLE", "SUPPORT_WORST")},
        "nrf_all_dc_profiles_pass": all(row["status"] == "pass" for row in nrf_dc),
        "nrf_three_independent_spi_resources": {"NRF0_SPI", "NRF1_SPI", "NRF2_SPI"}.issubset(exclusive),
        "nrf_timing_has_bounded_three_drains": timing_checks["nrf_three_serial_drains_below_80us"] and timing_checks["nrf_service_budget_below_fifo_guard"],
        "nrf_three_isolated_digital_paths": all(level_checks[f"exact_nrf{i}_host_buffer"] and level_checks[f"exact_nrf{i}_return_buffer"] for i in range(3)),
        "nrf_three_independent_rf_corridors": len(nrf_corridors) == 3 and len({row["external_connector_instance"] for row in nrf_corridors}) == 3,
        "nrf_production_requires_target_observer_hil": nrf["rf_acceptance"]["hil_required"] is True and nrf["rf_acceptance"]["production_acceptance_level"] == "T1_TARGET",
        "paper_does_not_overclaim_same_channel_isolation": nrf["rf_acceptance"]["same_near_channel_isolated_sensitivity_guaranteed"] is False,
        "lab_injection_does_not_expand_runtime": "never_runtime_permission" in i6["runtime_invariant"]["cross_group_lab_injection"],
        "transition_starts_with_tx_revoke_and_ends_with_explicit_arm": "revoke" in transition[0] and "arm TX only" in transition[-1],
        "no_stall_contract_names_ui_and_nrf": "nRF FIFO" in acceptance["no_stall"] and "UI <=100 ms" in acceptance["no_stall"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.5.3 checks failed: " + ", ".join(failed))

    residual = [
        "run the signed-configuration L1 isolated baseline and L2 foreign-interface quiet/desense matrix for every signal group",
        "run FX-I6-N24-T1 with target plus independent observer for all eight radio-identity permutations at both support loads, all admitted channels/rates/powers and antenna poses",
        "prove inactive rails discharge, I/O remains high-Z, native S3/C5 radios emit no background packet/scan/advertising and service clocks have no periodic activity",
        "capture raw IRQ/FIFO/PIO/DMA/IPC/UI/storage/audio timing while each active group faces maximum valid support-plane aggression",
        "inject cross-group blocking, evidence false-positive, reset/brownout/stuck-line and KILL/FAULT_KILL faults only inside the contained Laboratory fixture",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.5.3",
        "status": "reviewed_one_group_quiet_and_three_nrf_concurrency_model",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, POWER_PATH, DC_PATH, LEVEL_PATH, TIMING_PATH, LAYOUT_PATH)},
        "summary": {"signal_groups": len(matrix), "quiet_contracts": len(quiet), "nrf_role_modes": 4, "nrf_identity_permutations": nrf_permutations, "checks": len(checks)},
        "group_quiet_matrix": matrix,
        "support_quiet_contracts": support_quiet_ids,
        "transition_order": transition,
        "acceptance": acceptance,
        "checks": checks,
        "corrections": [],
        "open_findings": [],
        "residual_physical_only": residual,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.5.4", "action": "consolidate RF pre-layout rules and all residual physical measurements"},
    }

    group_rows = "\n".join(f"| {row['signal_group']} | {', '.join(row['active_members'])} | {len(row['required_foreign_quiet_contracts'])} |" for row in matrix)
    en = f"""# RF coexistence model

`H3.5.3` is reviewed with `{len(checks)}` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

| Active group | Active members | Foreign RF/IR quiet contracts |
|---|---|---:|
{group_rows}

Runtime admits at most one top-level signal group. Display/UI, safety, telemetry and explicitly profile-declared audio/storage/service work are support planes, not a second radio group; their clocks and rails remain bounded or quiet. Cross-group interference injection exists only in the contained Laboratory test layer.

`SG-N24` is the deliberate internal exception. All three radios stay active with independent SPI/PIO/DMA, digital isolation and antenna corridors. The matrix covers four role mixes, eight radio-identity permutations and both idle/worst support loads. Paper review does **not** claim same/near-channel isolation: production acceptance still requires the T1 target plus independent observer and the within-3-dB peer-receive rule, with no hidden standby or RX gap.

Machine evidence: [`H3-VRF53-rf-coexistence.json`](../hardware/verification/generated/H3-VRF53-rf-coexistence.json).
"""
    ru = f"""# Модель RF coexistence

`H3.5.3` проведён ревью: `{len(checks)}` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

| Активная группа | Активные участники | Quiet contracts чужих RF/IR |
|---|---|---:|
{group_rows}

Runtime допускает максимум одну верхнеуровневую группу сигналов. Display/UI, safety, telemetry и явно объявленные профилем audio/storage/service — supporting planes, а не вторая радиогруппа; их clocks и rails ограничены или затихают. Cross-group injection существует только внутри изолированного тестового слоя «Лаборатория».

`SG-N24` — намеренное внутреннее исключение. Все три радио остаются активны и имеют независимые SPI/PIO/DMA, digital isolation и антенные corridors. Матрица покрывает четыре role mixes, восемь перестановок ролей по радиомодулям и оба support loads. Бумажное ревью **не** заявляет same/near-channel isolation: production acceptance всё ещё требует T1 target плюс независимый observer, правило деградации peer RX не более 3 дБ и отсутствие скрытого standby/RX gap.

Машинное evidence: [`H3-VRF53-rf-coexistence.json`](../hardware/verification/generated/H3-VRF53-rf-coexistence.json).
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
            raise SystemExit("stale H3.5.3 artifacts: " + ", ".join(stale))
    print(f"ok: H3.5.3 reviewed; {len(manifest['checks'])} checks, next H3.5.4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
