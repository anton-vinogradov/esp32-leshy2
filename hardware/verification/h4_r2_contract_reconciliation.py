#!/usr/bin/env python3
"""Reconcile the current R2 hardware contract with firmware-visible inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FW_ROOT = ROOT.parent / "esp32-leshy2-firmware"
PLAN = ROOT / "hardware/verification/h4-r2-prelayout-plan.json"
FREEZE = ROOT / "hardware/verification/generated/H4-R2-input-freeze.json"
H2_CONTRACT = ROOT / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
H2_M1 = ROOT / "hardware/ecad/generated/H2-R2-interboard-m1.json"
H3_DIGITAL = ROOT / "hardware/verification/generated/H3-R2-digital-interfaces.json"
H3_RESIDUALS = ROOT / "hardware/verification/generated/H3-R2-physical-residuals.json"
PREORDER = ROOT / "hardware/verification/preorder-verification-contract.json"
FW_H0 = FW_ROOT / "config/h0_r2_hardware_contract.json"
FW_H2 = FW_ROOT / "config/r2_h2_sync_gate.json"
FW_BSP_MODEL = FW_ROOT / "config/f2_r2_bsp_generation.json"
FW_BSP_CONSUMPTION = FW_ROOT / "config/f2_r2_bsp_consumption.json"
FW_BSP_MANIFEST = FW_ROOT / "generated/r2/source_manifest.json"
FW_BUILD = FW_ROOT / "config/f2_r2_build_qualification.json"
FW_DIGITAL = FW_ROOT / "config/h3_r2_digital_interfaces.json"
FW_ACCEPTANCE = FW_ROOT / "config/h3_r2_acceptance.json"
FW_FREEZE = FW_ROOT / "config/h4_r2_input_freeze.json"
FW_H3_IMPORTS = (
    FW_ROOT / "config/h3_r2_transition_contract.json",
    FW_ROOT / "config/h3_r2_handover_contract.json",
    FW_ROOT / "config/h3_r2_inrush_watchdog_contract.json",
    FW_DIGITAL,
    FW_ROOT / "config/h3_r2_rf_coexistence.json",
    FW_ROOT / "config/h3_r2_thermal_fault.json",
)
RECONCILIATION_OUTPUT = ROOT / "hardware/verification/generated/H4-R2-contract-reconciliation.json"
JOIN_OUTPUT = ROOT / "hardware/verification/generated/H4-R2-joined-crosscheck.json"
DOC_EN = ROOT / "docs/h4-r2-contract-reconciliation.md"
DOC_RU = ROOT / "docs/h4-r2-contract-reconciliation.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def h3_import_sources_current(imported: dict) -> bool:
    source = imported.get("source", {})
    rows = source.values() if source and "path" not in source else (source,)
    for row in rows:
        if not isinstance(row, dict) or "path" not in row or "sha256" not in row:
            return False
        path = FW_ROOT / row["path"]
        if not path.is_file() or sha256(path) != row["sha256"]:
            return False
    return True


def semantic_m1(rows: list[dict]) -> list[tuple[int, str, str]]:
    return [(row["contact"], row["net"], row["class"]) for row in rows]


def build() -> tuple[dict[Path, str], dict, dict]:
    plan = load(PLAN)
    freeze = load(FREEZE)
    h2 = load(H2_CONTRACT)
    h2_m1 = load(H2_M1)
    h3_digital = load(H3_DIGITAL)
    residuals = load(H3_RESIDUALS)
    preorder = load(PREORDER)
    fw_h0 = load(FW_H0)
    fw_h2 = load(FW_H2)
    fw_model = load(FW_BSP_MODEL)
    fw_consumption = load(FW_BSP_CONSUMPTION)
    fw_manifest = load(FW_BSP_MANIFEST)
    fw_build = load(FW_BUILD)
    fw_digital = load(FW_DIGITAL)
    fw_acceptance = load(FW_ACCEPTANCE)
    fw_freeze = load(FW_FREEZE)
    fw_h3 = [load(path) for path in FW_H3_IMPORTS]

    h2_domains = h2["r2_reconciliation"]["domain_contracts"]
    expected_counts = {row["id"]: len(row["pin_map"]) for row in h2_domains}
    generated = {row["id"]: row for row in fw_manifest["domains"]}
    coverage = []
    corrections = []
    for domain in h2_domains:
        domain_id = domain["id"]
        actual = generated[domain_id]["pins"]
        expected = expected_counts[domain_id]
        exact = generated[domain_id]["mapping"] == "exact_pins" and actual == expected
        coverage.append(
            {
                "domain": domain_id,
                "expected_h2_rows": expected,
                "generated_bsp_rows": actual,
                "missing_rows": expected - actual,
                "mapping": generated[domain_id]["mapping"],
                "exact": exact,
            }
        )
        if not exact:
            corrections.append(
                {
                    "id": f"FW-BSP-{len(corrections) + 1:03d}",
                    "domain": domain_id,
                    "finding": f"generated BSP exposes {actual}/{expected} current H2 pin rows as {generated[domain_id]['mapping']}",
                    "required_correction": "generate the complete canonical H2 domain pin map and make the owning target fail closed on exact mapping/count",
                    "owner": "H4-R2.2 + firmware F2-R2",
                }
            )

    h2_m1_rows = semantic_m1(h2_m1["contacts"])
    fw_m1_rows = semantic_m1(fw_h0["interboard"]["pin_map"])
    imported_h3_hashes_current = all(h3_import_sources_current(row) for row in fw_h3)
    steps = {row["id"]: row["status"] for row in plan["substeps"]}
    checks = {
        "plan_records_reconciliation_and_join_reviewed": plan["current_substep"] == "H4-R2.2" and steps["H4-R2.0.2"] == "reviewed" and steps["H4-R2.1"] == "reviewed" and steps["H4-R2.2"] == "current",
        "joined_input_freeze_is_reviewed_and_imported": freeze["status"] == "reviewed" and fw_freeze["status"] == "reviewed_hardware_contract_imported" and fw_freeze["source"]["sha256"] == sha256(FREEZE),
        "six_domain_h2_contract_is_exactly_imported": h2["bsp"]["domains"] == h2_domains == fw_h0["domain_contracts"],
        "six_domain_identities_match": [(row["id"], row["mpn"]) for row in h2_domains] == [(row["id"], row["mpn"]) for row in fw_h0["domains"]],
        "h2_sync_gate_selects_six_domain_authority": fw_h2["status"] == "reviewed_six_domain_h2_export" and fw_h2["r2_h2_synchronized"] is True,
        "m1_all_80_contacts_match_semantically": h2_m1_rows == fw_m1_rows and len(h2_m1_rows) == 80,
        "all_h3_contract_import_hashes_are_current": imported_h3_hashes_current,
        "digital_display_contract_matches": fw_digital["display"]["requested_clock_hz"] == h3_digital["display_timing"]["clock"]["requested_hz"] == 20_000_000 and fw_digital["display"]["actual_clock_hz"] == h3_digital["display_timing"]["clock"]["actual_hz"] == 20_000_000,
        "digital_usb_and_m1_contracts_match": fw_digital["usb_and_service_ownership"] == h3_digital["usb_and_service_ownership"] and fw_digital["m1"] == h3_digital["m1"],
        "digital_transport_contracts_match": fw_digital["transport_timing"] == h3_digital["transport_timing"],
        "f2_build_claim_is_bounded": fw_build["claims"]["all_target_compilation_and_link_passed"] is True and fw_build["claims"]["runtime_boot_proven"] is False and fw_build["claims"]["physical_hardware_proven"] is False,
        "single_i8080_obligation_is_retained": len(fw_acceptance["firmware_obligations"]) == 1 and fw_acceptance["firmware_obligations"][0]["owner"] == "F5/F6" and fw_acceptance["claims"]["i8080_target_implementation_proven"] is False,
        "all_physical_residuals_remain_owned": residuals["summary"]["physical_evidence_rows"] == 51 and residuals["summary"]["unassigned"] == 0,
        "no_release_authority_is_created": preorder["current_truth"]["order_authorized"] is False and not any(plan["authorization"][key] for key in ("component_purchase", "pcb_placement_and_routing", "fabrication")),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4-R2 contract reconciliation failed structurally: " + ", ".join(failed))
    if [row["domain"] for row in corrections] != ["c5", "pack", "safety"]:
        raise ValueError("unexpected H4-R2 BSP correction set")

    source_paths = (
        PLAN, FREEZE, H2_CONTRACT, H2_M1, H3_DIGITAL, H3_RESIDUALS,
        PREORDER, FW_H0, FW_H2, FW_BSP_MODEL, FW_BSP_CONSUMPTION,
        FW_BSP_MANIFEST, FW_BUILD, FW_DIGITAL, FW_ACCEPTANCE, FW_FREEZE,
        *FW_H3_IMPORTS,
    )
    reconciliation = {
        "schema_version": 1,
        "artifact": "H4-R2-contract-reconciliation",
        "marker": "H4-R2.0.2",
        "status": "reviewed_with_corrections_required",
        "source_sha256": {str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path("../esp32-leshy2-firmware") / path.relative_to(FW_ROOT)): sha256(path) for path in source_paths},
        "summary": {
            "domains": len(h2_domains),
            "hardware_pin_rows": sum(expected_counts.values()),
            "generated_bsp_pin_rows": sum(row["generated_bsp_rows"] for row in coverage),
            "missing_generated_bsp_rows": sum(row["missing_rows"] for row in coverage),
            "exact_generated_domains": sum(row["exact"] for row in coverage),
            "corrections_required": len(corrections),
            "retained_firmware_obligations": 1,
            "physical_residuals_carried": 51,
            "structural_check_failures": 0,
        },
        "domain_coverage": coverage,
        "checks": checks,
        "corrections_required": corrections,
        "retained_obligations": fw_acceptance["firmware_obligations"],
        "authorization": {"component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False},
        "next": {"marker": "H4-R2.1", "action": "run the joined cross-check and route every contradiction to H4-R2.2"},
    }
    joined = {
        "schema_version": 1,
        "artifact": "H4-R2-joined-crosscheck",
        "marker": "H4-R2.1",
        "status": "reviewed_corrections_required",
        "source": {"path": "hardware/verification/generated/H4-R2-contract-reconciliation.json", "sha256": hashlib.sha256((json.dumps(reconciliation, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()},
        "summary": {
            "structural_checks": len(checks),
            "structural_check_failures": 0,
            "cross_domain_contradictions": len(corrections),
            "unowned_contradictions": 0,
            "retained_firmware_obligations": 1,
            "physical_residuals_carried": 51,
        },
        "contradictions": corrections,
        "retained_obligations": fw_acceptance["firmware_obligations"],
        "authorization": {"component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False},
        "next": {"marker": "H4-R2.2", "action": "correct and regenerate the C5, Pack and Safety BSP boundaries without changing hardware"},
    }

    rows_en = "\n".join(f"| `{row['domain']}` | {row['expected_h2_rows']} | {row['generated_bsp_rows']} | {row['missing_rows']} | `{row['mapping']}` |" for row in coverage)
    rows_ru = rows_en
    en = f"""# H4-R2 hardware/firmware contract reconciliation

[Русский](h4-r2-contract-reconciliation.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Input freeze](h4-r2-input-freeze.md)

`H4-R2.0.2` and the joined `H4-R2.1` cross-check are reviewed. The six-domain H2 contract, all 80 M1 contacts, current H3 imports, USB/service ownership, the 20-MHz direct i8080 contract and target-build claim boundaries agree across repositories.

The review found one bounded implementation-class issue with three domain owners: the generated F2 BSP still represents only `{reconciliation['summary']['generated_bsp_pin_rows']}` of the `{reconciliation['summary']['hardware_pin_rows']}` current H2 controller rows. The missing `{reconciliation['summary']['missing_generated_bsp_rows']}` rows are firmware-generation omissions, not a hardware pinout change.

| Domain | H2 rows | Generated rows | Missing | Current mapping |
|---|---:|---:|---:|---|
{rows_en}

H4-R2.2 must regenerate complete exact maps for C5, Pack and Safety and make their owning targets fail closed on exact mapping/count. The separate F5/F6 display-driver obligation remains open by design; no H5/H6/H8 physical evidence is consumed.

**Current marker: `H4-R2.2`.** Purchase, placement, routing and fabrication remain unauthorized.

[Machine reconciliation](../hardware/verification/generated/H4-R2-contract-reconciliation.json) · [machine joined cross-check](../hardware/verification/generated/H4-R2-joined-crosscheck.json).
"""
    ru = f"""# Сверка контрактов железа и прошивки H4-R2

[English](h4-r2-contract-reconciliation.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Фиксация входов](h4-r2-input-freeze.ru.md)

`H4-R2.0.2` и объединённый cross-check `H4-R2.1` проведены ревью. Six-domain контракт H2, все 80 контактов M1, текущие импорты H3, владение USB/service, прямой i8080 на 20 МГц и границы утверждений target-build совпадают между репозиториями.

Ревью нашло одну ограниченную implementation-проблему с тремя владельцами доменов: сгенерированный BSP F2 пока представляет лишь `{reconciliation['summary']['generated_bsp_pin_rows']}` из `{reconciliation['summary']['hardware_pin_rows']}` текущих controller-строк H2. Недостающие `{reconciliation['summary']['missing_generated_bsp_rows']}` строк — пропуск генерации прошивки, а не изменение аппаратной распиновки.

| Домен | Строк H2 | Строк BSP | Не хватает | Текущее отображение |
|---|---:|---:|---:|---|
{rows_ru}

H4-R2.2 должен сгенерировать полные точные карты C5, Pack и Safety и заставить их target-проекты fail-closed проверять точный mapping/count. Отдельное обязательство F5/F6 по драйверу дисплея остаётся открытым намеренно; никакое физическое evidence H5/H6/H8 не поглощено.

**Текущий маркер: `H4-R2.2`.** Закупка, placement, routing и печать остаются запрещены.

[Машинная сверка](../hardware/verification/generated/H4-R2-contract-reconciliation.json) · [машинный объединённый cross-check](../hardware/verification/generated/H4-R2-joined-crosscheck.json).
"""
    outputs = {
        RECONCILIATION_OUTPUT: json.dumps(reconciliation, ensure_ascii=False, indent=2) + "\n",
        JOIN_OUTPUT: json.dumps(joined, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }
    return outputs, reconciliation, joined


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, reconciliation, joined = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H4-R2 contract artifacts: " + ", ".join(stale))
    print(f"ok: H4-R2.0.2/H4-R2.1 reviewed; {joined['summary']['cross_domain_contradictions']} owned corrections, next H4-R2.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
