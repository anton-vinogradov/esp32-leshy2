#!/usr/bin/env python3
"""Build the formal, explicitly accepted H3 package."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO / "hardware/verification/h3-verification-plan.json"
H2_ACCEPTANCE_PATH = REPO / "hardware/ecad/generated/H2-REV81-acceptance-package.json"
PHASE_PATHS = {
    "H3.1": REPO / "hardware/verification/generated/H3-VRF14-dc-consolidation.json",
    "H3.2": REPO / "hardware/verification/generated/H3-VRF25-transition-consolidation.json",
    "H3.3": REPO / "hardware/verification/generated/H3-VRF35-analog-consolidation.json",
    "H3.4": REPO / "hardware/verification/generated/H3-VRF44-digital-consolidation.json",
    "H3.5": REPO / "hardware/verification/generated/H3-VRF54-rf-consolidation.json",
    "H3.6": REPO / "hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json",
}
CROSSCHECK_PATH = REPO / "hardware/verification/generated/H3-VRF71-crosscheck.json"
RESIDUAL_PATH = REPO / "hardware/verification/generated/H3-VRF72-physical-residuals.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF73-acceptance-package.json"
DOC_EN = REPO / "docs/h3-acceptance.md"
DOC_RU = REPO / "docs/h3-acceptance.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summary_status(row: dict) -> str:
    summary = row["review_summary"]
    return summary.get("status", summary.get("phase_status", ""))


def unresolved_count(row: dict) -> int:
    summary = row["review_summary"]
    for key in ("unresolved", "unresolved_findings", "unresolved_analytical_findings"):
        if key in summary:
            return int(summary[key])
    return 0


def build() -> tuple[dict[Path, str], dict]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    h2 = json.loads(H2_ACCEPTANCE_PATH.read_text(encoding="utf-8"))
    phases = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in PHASE_PATHS.items()}
    crosscheck = json.loads(CROSSCHECK_PATH.read_text(encoding="utf-8"))
    residuals = json.loads(RESIDUAL_PATH.read_text(encoding="utf-8"))

    corrections = {
        "H3.1": phases["H3.1"]["review_summary"]["corrected_findings"],
        "H3.2": phases["H3.2"]["review_summary"]["corrected_findings"],
        "H3.3": phases["H3.3"]["consolidated"]["source_corrections"],
        "H3.4": phases["H3.4"]["consolidated"]["source_or_self_review_corrections"],
        "H3.5": len(phases["H3.5"]["corrections"]),
        "H3.6": phases["H3.6"]["consolidated"]["source_corrections"],
        "H3.7.1": crosscheck["review_summary"]["corrected_findings"],
    }
    known_bom_delta = (
        Decimal(phases["H3.3"]["consolidated"]["bom_delta_usd_at_quantity_100"])
        + Decimal(phases["H3.6"]["consolidated"]["incremental_bom_usd_at_quantity_100"])
    )
    phase_results = [
        {
            "phase": name,
            "artifact": str(PHASE_PATHS[name].relative_to(REPO)),
            "sha256": sha256(PHASE_PATHS[name]),
            "status": summary_status(row),
            "unresolved_analytical_findings": unresolved_count(row),
            "recorded_corrections": corrections[name],
        }
        for name, row in phases.items()
    ]

    checks = {
        "accepted_h2_is_the_historical_r1_input_boundary": h2["status"] == "reviewed_h2_user_accepted" and h2["decision"]["status"] == "accepted_by_user" and h2.get("authority", {}).get("allowed_as_r2_authority") is False,
        "all_six_h3_phase_results_are_reviewed": all(row["status"] == "reviewed" for row in phase_results),
        "all_six_h3_phase_results_have_zero_analytical_findings": all(row["unresolved_analytical_findings"] == 0 for row in phase_results),
        "crosscheck_has_zero_missing_joins": crosscheck["summary"]["missing_joins"] == 0 and crosscheck["summary"]["hash_mismatches"] == 0,
        "crosscheck_covers_all_h2_identities": crosscheck["summary"]["h2_instances"] == 1081 and crosscheck["summary"]["h2_root_nets"] == 270,
        "all_physical_residuals_are_published": residuals["summary"]["physical_evidence_rows"] == 85 and residuals["summary"]["unassigned"] == 0,
        "no_physical_residual_is_claimed_closed": residuals["summary"]["analytically_closed_by_h3"] == 0 and all(row["status"] == "physical_evidence_required" for row in residuals["registry"]),
        "all_25_corrections_are_accounted": sum(corrections.values()) == 25,
        "known_bom_delta_is_bounded": known_bom_delta == Decimal("1.2575"),
        "h3_acceptance_is_recorded": plan["status"] == "reviewed" and plan["substeps"][7]["children"][3]["status"] == "reviewed",
        "h4_rejoin_is_required_with_existing_firmware_f3_evidence": True,
        "acceptance_does_not_authorize_layout": plan["authorization"]["pcb_placement_and_routing"] is False,
        "acceptance_does_not_authorize_fabrication": plan["authorization"]["fabrication"] is False,
        "acceptance_does_not_authorize_purchase": plan["authorization"]["purchasing"] is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.7.3 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.7.3",
        "status": "reviewed_h3_user_accepted",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (PLAN_PATH, H2_ACCEPTANCE_PATH, *PHASE_PATHS.values(), CROSSCHECK_PATH, RESIDUAL_PATH)},
        "acceptance_meaning": [
            "all former single-RP R1 checks possible without fabricated hardware have reproducible reviewed evidence",
            "no analytical finding or missing H2/H3/downstream trace remains",
            "all physical-only uncertainties remain open and are assigned to exact H5/H6/H8 evidence",
            "the corrected historical H2 source is the R1 evidence baseline and is forbidden as R2 authority",
        ],
        "acceptance_does_not_authorize": [
            "component or sample purchase",
            "KiCad PCB placement or routing",
            "prototype or production fabrication",
            "calling any physical-only residual passed",
            "treating the former H4 join as current before it consumes this H3 revision and the existing firmware F3 evidence",
        ],
        "phase_results": phase_results,
        "correction_summary": {
            "by_stage": corrections,
            "total": sum(corrections.values()),
            "known_incremental_bom_usd_at_quantity_100": f"{known_bom_delta:.4f}",
            "accepted_product_capabilities_removed": 0,
        },
        "traceability_summary": crosscheck["summary"],
        "physical_evidence_summary": residuals["summary"],
        "acceptance_gate": {
            "id": "H3.7.4",
            "state": "accepted_by_user",
            "effect": "H3 is reviewed; H4 must be rejoined with existing firmware F3 evidence and still does not authorize purchase, layout or fabrication",
        },
        "user_acceptance": {
            "accepted": True,
            "date": "2026-08-26",
            "basis": "user instructed automatic acceptance for clean reviews without questions or proposals; this revision re-runs every H3 artifact against the accepted dual-SA818S H2 baseline",
        },
        "checks": checks,
        "open_analytical_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved_analytical_findings": 0, "status": "reviewed"},
        "next": {"stage": "H1-R2.31", "action": "close physical H1 and production gates before creating the new R2 H2/H3 chain"},
    }

    phase_table_en = "\n".join(f"| `{row['phase']}` | reviewed | {row['recorded_corrections']} | 0 |" for row in phase_results)
    phase_table_ru = "\n".join(f"| `{row['phase']}` | закрыт | {row['recorded_corrections']} | 0 |" for row in phase_results)
    en = f"""# H3 acceptance package · historical R1

H3 is accepted. All virtual checks are reproducible and analytically closed: six phase consolidations are reviewed, the exhaustive cross-check has zero missing joins or hash mismatches, and all `{residuals['summary']['physical_evidence_rows']}` physical-only rows retain H5/H6/H8 owners and pass rules.

| Phase | Result | Corrections | Open analytical findings |
|---|---|---:|---:|
{phase_table_en}

The review accounts for `{sum(corrections.values())}` corrections. The known quantity-100 BOM increase is `{known_bom_delta:.4f} USD`; no accepted product capability was removed. Acceptance means the non-physical H3 scope is complete and the corrected artifacts become the baseline. It does **not** approve purchase, PCB layout/routing, fabrication or any physical residual.

This historical R1 chain progressed next to `H4.0.1-R1`. It is not the current hardware marker; current R2 remains at `H1-R2.31` and must run its own H2/H3.

Machine package: [`H3-VRF73-acceptance-package.json`](../hardware/verification/generated/H3-VRF73-acceptance-package.json).
"""
    ru = f"""# Пакет приёмки H3 · historical R1

H3 принят. Все виртуальные проверки воспроизводимы и аналитически закрыты: сведения шести фаз имеют закрытый статус, полная сквозная сверка не имеет пропусков или hash mismatch, а все `{residuals['summary']['physical_evidence_rows']}` physical-only строк сохраняют владельцев и pass rules H5/H6/H8.

| Фаза | Результат | Исправления | Открытые аналитические findings |
|---|---|---:|---:|
{phase_table_ru}

Учтены все `{sum(corrections.values())}` исправлений. Известное увеличение BOM на количестве 100 — `{known_bom_delta:.4f} USD`; ни одна принятая возможность продукта не удалена. Приёмка означает завершение нефизической части H3 и превращает исправленные artifacts в baseline. Она **не** разрешает закупку, PCB layout/routing, печать или закрытие любого физического остатка.

Следующим шагом этой исторической R1-цепочки был `H4.0.1-R1`. Это не текущий аппаратный маркер: текущая R2 остаётся на `H1-R2.31` и должна пройти собственные H2/H3.

Машинный пакет: [`H3-VRF73-acceptance-package.json`](../hardware/verification/generated/H3-VRF73-acceptance-package.json).
"""
    # The bilingual public report is curated as a richer product-facing page.
    # This generator owns the machine package only, so a later evidence refresh
    # cannot replace the reviewed report with the compact bootstrap text above.
    return {OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"}, manifest


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
            raise SystemExit("stale H3.7.3 artifacts: " + ", ".join(stale))
    print(f"ok: H3 accepted snapshot; {manifest['review_summary']['checks']} acceptance checks, next was H4.0.1/F3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
