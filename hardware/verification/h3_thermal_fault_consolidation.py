#!/usr/bin/env python3
"""Consolidate H3.6 thermal, single-fault and unattended-operation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
THERMAL_PATH = REPO / "hardware/verification/generated/H3-VRF61-thermal-model.json"
FAULT_PATH = REPO / "hardware/verification/generated/H3-VRF62-fault-tree.json"
UNATTENDED_PATH = REPO / "hardware/verification/generated/H3-VRF63-unattended-envelope.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json"
DOC_EN = REPO / "docs/thermal-fault-result.md"
DOC_RU = REPO / "docs/thermal-fault-result.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(value: object) -> Decimal:
    return Decimal(str(value))


def build() -> tuple[dict[Path, str], dict]:
    thermal = json.loads(THERMAL_PATH.read_text(encoding="utf-8"))
    fault = json.loads(FAULT_PATH.read_text(encoding="utf-8"))
    unattended = json.loads(UNATTENDED_PATH.read_text(encoding="utf-8"))
    leaves = (thermal, fault, unattended)

    leaf_checks = sum(row["review_summary"]["checks"] for row in leaves)
    corrected_findings = (
        thermal["review_summary"]["corrected_findings"]
        + fault["review_summary"]["corrected_findings"]
    )
    physical_residuals = list(dict.fromkeys(
        item
        for row in (thermal, fault)
        for item in row["residual_physical_only"]
        if item.startswith(("H5:", "H6:", "H8:"))
    ))
    for item in unattended["h6_h8_required_evidence"]:
        if item not in physical_residuals:
            physical_residuals.append(item)

    downstream = {
        "H4": [
            "join H3.6 safety-policy evidence to firmware F3 target/emulator behavior without treating host logic as peripheral or board proof",
            "verify the firmware consumes the exact ambient, self-test enum, fault cause and physical-rearm contract before the joined pre-layout gate closes",
        ],
        "H5": [
            "inspect received thermistor, cell-holder, connector and enclosure-contact geometry where documentary evidence cannot prove physical contact or fit",
        ],
        "H6": [
            "physically separate RUN_PERMIT and FAULT_ASSERT_N routes, buffers, returns and vulnerable pads/vias",
            "solve the final copper/enclosure thermal network and meet the profile-specific 35-C base-to-ambient resistance ceilings",
        ],
        "H8": [
            "inject all SF-01 through SF-30 cases and measure shutdown, retained cause, no-output and physical-rearm behavior",
            "run chamber, 24/48-hour qualified-USB and battery-to-protected-cutoff tests without converting results into uptime promises",
            "qualify three-zone sensing, all self-test settings, evidence channels, journals and final per-profile duty/session limits",
        ],
    }

    ambient = unattended["ambient_design_target"]
    self_test = unattended["fault_plane_self_test_setting"]
    value_by_id = {row["id"]: row for row in self_test["values"]}
    deadlines = [
        row["analytical_deadline_ms_max"]
        for row in fault["faults"]
        if row["analytical_deadline_ms_max"] is not None
    ]
    checks = {
        "all_three_leaf_reviews_are_closed": all(row["review_summary"]["status"] == "reviewed" for row in leaves),
        "all_leaf_fail_counts_are_zero": all(row["review_summary"]["failed"] == 0 for row in leaves),
        "all_leaf_analytical_findings_are_closed": all(row["review_summary"]["unresolved_analytical_findings"] == 0 for row in leaves),
        "all_leaf_open_findings_are_empty": all(not row["open_findings"] for row in leaves),
        "all_leaf_decisions_are_closed": all(not row["pending_decisions"] for row in leaves),
        "leaf_check_total_is_70": leaf_checks == 70,
        "four_source_corrections_are_preserved": corrected_findings == 4,
        "all_30_single_fault_cases_are_preserved": fault["review_summary"]["single_fault_cases"] == 30 and len(fault["faults"]) == 30,
        "fault_cases_end_contained_or_no_admission": all(row["classification"] in {"contained", "detected_no_admission"} for row in fault["faults"]),
        "maximum_analytical_shutdown_class_is_1760ms": max(deadlines) == 1760,
        "three_independent_thermal_zones_are_preserved": set(thermal["zone_policy"]["sensors"]) == {"POWER", "RF_VOICE", "UI"},
        "ambient_target_matches_leaf_models": thermal["product_ambient_envelope"]["minimum_c"] == ambient["design_target_c"]["minimum"] == 0 and thermal["product_ambient_envelope"]["maximum_c"] == ambient["design_target_c"]["maximum"] == 35,
        "ambient_target_is_not_published_guarantee": "not a published" in ambient["status"],
        "support_worst_is_not_sustained": "not admitted" in thermal["scenarios"]["electrical_absolute_corner"]["admission"] and "SUPPORT_WORST" in unattended["sustained_operation_policy"]["excluded"][0],
        "voice_35c_thermal_ceiling_matches_leaf": d(ambient["h6_base_to_ambient_rtheta_k_per_w_max_at_35c"]["voice_support_idle_worst_group"]) == d("5.446"),
        "fault_plane_proof_is_physical_rearm_bound": "physical KILL-to-RUN" in fault["fault_plane"]["destructive_test_boundary"],
        "self_test_default_is_48h": self_test["default"] == "EVERY_48_H" and value_by_id["EVERY_48_H"]["active_session_seconds"] == 172800,
        "self_test_24h_and_startup_only_are_explicit": value_by_id["EVERY_24_H"]["active_session_seconds"] == 86400 and value_by_id["STARTUP_ONLY"]["active_session_seconds"] is None,
        "self_test_cannot_extend_after_s3_loss": any("cannot extend" in text for text in self_test["invariants"]),
        "proof_deadline_revokes_tx_before_fault": self_test["deadline_sequence"][0].startswith("revoke every TX lease") and self_test["deadline_sequence"][-1].startswith("hold SAFETY_FAULT_REQUEST"),
        "usb_never_relaxes_safety": "never relaxes" in unattended["accepted_product_policy"]["usb_rule"],
        "no_runtime_or_autonomy_claim_is_made": unattended["accepted_product_policy"]["runtime_claim"].startswith("none") and all("runtime" not in row.lower() or "guaranteed" in row.lower() for row in unattended["non_claims"]),
        "all_residuals_are_physical_and_assigned": len(physical_residuals) >= 12 and all(row.startswith(("H5:", "H6:", "H8:")) for row in physical_residuals),
        "downstream_consumers_cover_h4_h5_h6_h8": set(downstream) == {"H4", "H5", "H6", "H8"},
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.6.4 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.6.4",
        "status": "reviewed_thermal_fault_and_unattended_consolidation",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (THERMAL_PATH, FAULT_PATH, UNATTENDED_PATH)
        },
        "consolidated": {
            "leaf_packages": 3,
            "leaf_checks": leaf_checks,
            "consolidation_checks": len(checks),
            "single_fault_cases": fault["review_summary"]["single_fault_cases"],
            "source_corrections": corrected_findings,
            "incremental_bom_usd_at_quantity_100": fault["review_summary"]["incremental_bom_usd_at_100"],
            "unresolved_analytical_findings": 0,
            "physical_residuals": len(physical_residuals),
        },
        "closed_contract": {
            "ambient_engineering_target_c": ambient["design_target_c"],
            "ambient_is_product_guarantee": False,
            "sustained_candidate": "SUPPORT_IDLE plus one active top-level signal group, subject to H6/H8 qualification",
            "excluded_from_sustained": unattended["sustained_operation_policy"]["excluded"],
            "long_operation_source": unattended["accepted_product_policy"]["extended_operation_guidance"],
            "runtime_claim": unattended["accepted_product_policy"]["runtime_claim"],
            "self_test_default": self_test["default"],
            "self_test_values": self_test["values"],
            "fault_recovery": "retained first cause plus physical KILL-to-RUN; no software or automatic re-arm",
        },
        "downstream_evidence": downstream,
        "checks": checks,
        "open_findings": [],
        "pending_decisions": [],
        "residual_physical_only": physical_residuals,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.7.1", "action": "cross-check every H3 result against H2 and downstream consumers"},
    }

    en = f"""# Thermal, fault and extended-operation result

H3.6 is closed: three leaf packages contribute `{leaf_checks}` passing checks and this consolidation adds `{len(checks)}` cross-domain checks. All `{fault['review_summary']['single_fault_cases']}` single-fault cases finish contained or with no admission; no analytical finding or policy decision remains open. The exact current marker is `H3.7.1`.

The engineering ambient target is `0 to 35 °C`, not a published guarantee. Only `SUPPORT_IDLE` with one active top-level signal group may proceed toward sustained-profile qualification; `SUPPORT_WORST`, continuous or unleased TX, unknown accessories and unreadable safety sensors are excluded. H6 must meet the final thermal and route-separation constraints, and H8 must measure the product.

Long operation uses a qualified USB-PD source and carries no uptime or battery-autonomy promise. The local full-self-test setting offers 24 hours, default 48 hours and warned startup-only proof; it cannot weaken watchdog, thermal, power-fault or TX-lease behavior. Proof expiry records `FAULT_PLANE_PROOF_DUE`, revokes leases and requires physical `KILL` to `RUN` recovery.

`{len(physical_residuals)}` remaining items are physical-only and assigned to H5, H6 or H8. This result does not authorize purchase, KiCad placement/routing or fabrication.

Machine evidence: [`H3-VRF64-thermal-fault-consolidation.json`](../hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json).
"""
    ru = f"""# Сводный результат thermal, fault и длительной работы

H3.6 закрыт: три leaf-пакета дают `{leaf_checks}` проходящих checks, а сведение добавляет `{len(checks)}` сквозных checks. Все `{fault['review_summary']['single_fault_cases']}` single-fault сценариев заканчиваются containment или запретом допуска; незакрытых аналитических findings и решений нет. Точный текущий маркер — `H3.7.1`.

Инженерная цель среды — `0…35 °C`, а не опубликованная гарантия. К квалификации длительного профиля допускается только `SUPPORT_IDLE` с одной активной верхнеуровневой сигнальной группой; исключены `SUPPORT_WORST`, непрерывный или unleased TX, неизвестные аксессуары и нечитаемые safety sensors. H6 обязан выполнить итоговые thermal- и route-separation ограничения, H8 — измерить изделие.

Для долгой работы используется квалифицированный USB-PD без обещания uptime или автономности. Локальная настройка полной самопроверки предлагает 24 часа, 48 часов по умолчанию и предупреждаемый режим «только при запуске»; она не ослабляет watchdog, thermal, power-fault или TX leases. Просрочка proof сохраняет `FAULT_PLANE_PROOF_DUE`, снимает leases и требует физического восстановления `KILL`→`RUN`.

Оставшиеся `{len(physical_residuals)}` пунктов являются только физическими и назначены H5, H6 или H8. Результат не разрешает закупку, KiCad placement/routing или печать.

Машинное evidence: [`H3-VRF64-thermal-fault-consolidation.json`](../hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json).
"""
    return {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }, manifest


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
            raise SystemExit("stale H3.6.4 artifacts: " + ", ".join(stale))
    print(
        "ok: H3.6 reviewed; "
        f"{manifest['consolidated']['leaf_checks']} leaf + "
        f"{manifest['consolidated']['consolidation_checks']} consolidation checks, next H3.7.1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
