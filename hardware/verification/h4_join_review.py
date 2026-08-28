#!/usr/bin/env python3
"""Build the joined H4 mechanical/electrical/firmware pre-layout gate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
FW_REPO = REPO.parent / "esp32-leshy2-firmware"
GEN = REPO / "hardware/verification/generated"

PLAN = REPO / "hardware/verification/h4-prelayout-plan.json"
PREORDER = REPO / "hardware/verification/preorder-verification-contract.json"
FW_PREORDER = FW_REPO / "config/preorder_verification_contract.json"
H1 = REPO / "hardware/product-design/generated/H1-cross-view-acceptance.json"
H2_ACCEPTANCE = REPO / "hardware/ecad/generated/H2-REV81-acceptance-package.json"
H2_INVENTORY = REPO / "hardware/ecad/generated/H2-REV71-canonical-inventories.json"
H2_CONTACTS = REPO / "hardware/ecad/generated/H2-REV72-physical-contacts.json"
H2_NETS = REPO / "hardware/ecad/generated/H2-REV73-named-nets-m1.json"
H2_CONTRACT = REPO / "hardware/ecad/generated/H2-hwfw-contract.json"
H3_ACCEPTANCE = REPO / "hardware/verification/generated/H3-VRF73-acceptance-package.json"
H3_RESIDUALS = REPO / "hardware/verification/generated/H3-VRF72-physical-residuals.json"
FW_CONTRACT = FW_REPO / "config/hardware_bsp_contract.json"
FW_INTEGRATION = FW_REPO / "config/hardware_integration_contract.json"
FW_GENERATION = FW_REPO / "config/bsp_generation_input.json"
FW_CONSUMPTION = FW_REPO / "config/bsp_target_consumption.json"
FW_SOURCE_MANIFEST = FW_REPO / "generated/source_manifest.json"
FW_F3 = FW_REPO / "config/f3_4_review.json"

JOIN_OUTPUT = GEN / "H4-PLG11-joined-review.json"
CORRECTION_OUTPUT = GEN / "H4-PLG12-correction-closure.json"
ACCEPTANCE_OUTPUT = GEN / "H4-PLG13-acceptance-package.json"
DOC_EN = REPO / "docs/h4-prelayout-gate-report.md"
DOC_RU = REPO / "docs/h4-prelayout-gate-report.ru.md"

FIRMWARE_BSP_AUTHORITY = {
    "baseline": "R1",
    "lifecycle": "historical_single_rp_import",
    "allowed_as_r2_authority": False,
    "superseded_by": "config/h0_r2_hardware_contract.json",
    "r2_sync_gate": "config/r2_h2_sync_gate.json",
}
FIRMWARE_INTEGRATION_AUTHORITY = {
    "baseline": "R1",
    "lifecycle": "historical_single_rp_integration_contract",
    "allowed_as_r2_authority": False,
    "superseded_by": "config/h0_r2_hardware_contract.json",
    "r2_sync_gate": "config/r2_h2_sync_gate.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return "../esp32-leshy2-firmware/" + str(path.relative_to(FW_REPO))


def git_commit_is_available_and_in_current_history(commit: str) -> bool:
    if not commit or len(commit) != 40:
        return False
    exists = subprocess.run(
        ["git", "-C", str(FW_REPO), "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    ancestor = subprocess.run(
        ["git", "-C", str(FW_REPO), "merge-base", "--is-ancestor", commit, "HEAD"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    return exists and ancestor


def source_hashes_are_current(rows: dict, base: Path) -> bool:
    return all((base / name).exists() and sha256(base / name) == expected for name, expected in rows.items())


def expected_historical_firmware_copy(hardware_contract: dict) -> dict:
    expected = copy.deepcopy(hardware_contract)
    expected["authority"] = copy.deepcopy(FIRMWARE_BSP_AUTHORITY)
    integration = copy.deepcopy(expected["integration_contract"])
    integration["authority"] = copy.deepcopy(FIRMWARE_INTEGRATION_AUTHORITY)
    expected["integration_contract"] = integration
    return expected


def report(joined: dict, russian: bool) -> str:
    residuals = joined["physical_residuals"]
    counts = joined["counts"]
    if russian:
        return f"""# Исторический итог H4 · объединённый pre-layout gate R1

[English](h4-prelayout-gate-report.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

Этот воспроизводимый снимок закрывает только прежнюю одно-RP архитектуру R1. Он сохранён как evidence и не является разрешением или исходником для текущего dual-RP H0/H1-R2. Текущий R2 явно заменяет эту границу и должен повторно пройти собственные H2–H4 после завершения точной распиновки.

```mermaid
flowchart LR
  H1["H1<br/>механика"] --> H4["✅ H4<br/>единый pre-layout gate"]
  H2["H2<br/>ECAD"] --> H4
  H3["H3<br/>виртуальная электрика"] --> H4
  F3["F3<br/>сборки и эмуляция"] --> H4
  H4 --> R2["▶️ H1-R2.31<br/>точная dual-RP распиновка"]
```

| Проверенная граница | Результат |
|---|---:|
| H1 M1 | 80 из 80 назначены; NC нет |
| H2 electrical identities / root nets | {counts['h2_reconciled_electrical_identities']} / {counts['h2_root_nets']} |
| HW↔FW BSP | 5 доменов, 125 контактов, семантически одинаковый контракт; firmware-копия fail-closed historical R1 |
| Firmware F3 | 52 воспроизводимых artifacts; 10 memory gates; точный QEMU для S3 |
| H3 physical-only registry | {residuals['total']} строк; H5={residuals['by_stage']['H5']}, H6={residuals['by_stage']['H6']}, H8={residuals['by_stage']['H8']} |

## Что доказано историческим join

| Граница | Результат |
|---|---|
| Два voice-модуля | `SA818S-V` и `SA818S-U` присутствуют как независимые RF-тракты с аппаратным one-hot выбором |
| Контракт прошивки | Дополнительные пять контактов принадлежат локальной аппаратной логике; публичный BSP сохраняет 125 MCU-контактов и не получает временных pin assignments |
| Evidence F3 | Старые executable results повторно связаны только с неизменившейся MCU-границей; реальные voice-модули остаются физическим gate |

## Что исторический H4 не доказывает

- Не закрывает ни одну из {residuals['total']} физических проверок: их владельцы H5/H6/H8 сохранены.
- Не доказывает boot четырёх non-S3 target, реальные peripherals, RF/антенны, тепловой режим, механический fit полученных деталей или flash rollback.
- Не описывает dual-RP R2, `U219`, текущий C5 SDIO/USB mux или новую точную распиновку.
- Не разрешает закупку, PCB placement/routing или fabrication.

Текущая позиция проекта — `H1-R2.31`: точные dual-RP GPIO/M1 и C5 SDIO/USB mux закрыты. Новый R2 H2 остаётся закрыт до завершения физических H1-блокеров и всех production-gate. Старый переход к `H5.0.1-R1` отменён сменой архитектуры.

Машинные evidence: [`H4.1`](../hardware/verification/generated/H4-PLG11-joined-review.json), [`H4.2`](../hardware/verification/generated/H4-PLG12-correction-closure.json), [`H4.3`](../hardware/verification/generated/H4-PLG13-acceptance-package.json).
"""
    return f"""# Historical H4 result · joined R1 pre-layout gate

[Русский](h4-prelayout-gate-report.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This reproducible snapshot closes only the former single-RP R1 architecture. It is retained as evidence and is not an authority or authorization for the current dual-RP H0/H1-R2 design. Current R2 explicitly supersedes this boundary and must repeat its own H2–H4 after exact pinout closure.

```mermaid
flowchart LR
  H1["H1<br/>mechanics"] --> H4["✅ H4<br/>joined pre-layout gate"]
  H2["H2<br/>ECAD"] --> H4
  H3["H3<br/>virtual electrical"] --> H4
  F3["F3<br/>builds and emulation"] --> H4
  H4 --> R2["▶️ H1-R2.31<br/>exact dual-RP pinout"]
```

| Reviewed boundary | Result |
|---|---:|
| H1 M1 | 80 of 80 assigned; no NC |
| H2 electrical identities / root nets | {counts['h2_reconciled_electrical_identities']} / {counts['h2_root_nets']} |
| HW↔FW BSP | 5 domains, 125 contacts, semantically identical contract; firmware copy is fail-closed historical R1 |
| Firmware F3 | 52 reproducible artifacts; 10 memory gates; exact S3 QEMU |
| H3 physical-only registry | {residuals['total']} rows; H5={residuals['by_stage']['H5']}, H6={residuals['by_stage']['H6']}, H8={residuals['by_stage']['H8']} |

## What the historical join proves

| Boundary | Result |
|---|---|
| Two voice modules | `SA818S-V` and `SA818S-U` are independent RF paths with hardware one-hot selection |
| Firmware contract | Five added contacts belong to local hardware logic; the public BSP remains at 125 MCU contacts with no temporary pin assignments |
| F3 evidence | Existing executable results are rejoined only across the unchanged MCU boundary; real voice modules remain a physical gate |

## What historical H4 does not prove

- None of the {residuals['total']} physical checks is closed; every H5/H6/H8 owner remains intact.
- Non-S3 boot, real peripherals, RF/antennas, thermal behavior, received-part fit and flash rollback remain physical gates.
- It does not describe dual-RP R2, `U219`, the current C5 SDIO/USB mux or the new exact pinout.
- Purchase, PCB placement/routing and fabrication remain unauthorized.

The current project position is `H1-R2.31`: exact dual-RP GPIO/M1 and the C5 SDIO/USB mux are closed. The new R2 H2 remains closed until the physical H1 blockers and all production gates close. The former transition to `H5.0.1-R1` was cancelled by the architecture change.

Machine evidence: [`H4.1`](../hardware/verification/generated/H4-PLG11-joined-review.json), [`H4.2`](../hardware/verification/generated/H4-PLG12-correction-closure.json), [`H4.3`](../hardware/verification/generated/H4-PLG13-acceptance-package.json).
"""


def build() -> tuple[dict[Path, str], dict]:
    plan = load(PLAN)
    preorder = load(PREORDER)
    h1 = load(H1)
    h2_acceptance = load(H2_ACCEPTANCE)
    h2_inventory = load(H2_INVENTORY)
    h2_contacts = load(H2_CONTACTS)
    h2_nets = load(H2_NETS)
    h2_contract = load(H2_CONTRACT)
    h3_acceptance = load(H3_ACCEPTANCE)
    h3_residuals = load(H3_RESIDUALS)
    fw_contract = load(FW_CONTRACT)
    fw_integration = load(FW_INTEGRATION)
    fw_generation = load(FW_GENERATION)
    fw_consumption = load(FW_CONSUMPTION)
    fw_manifest = load(FW_SOURCE_MANIFEST)
    f3 = load(FW_F3)

    h1_counts = h1["pin_resource_fit"]["direct_allocation_counts"]
    h2_domains = {row["instance"]: row["allocated_contact_count"] for row in h2_contract["bsp"]["domains"]}
    fw_projects = fw_consumption["projects"]
    expected_domains = {"s3": 33, "c5": 14, "rp": 48, "pack_admission": 13, "safety_controller": 17}
    project_counts = {
        "s3": fw_projects["s3"]["contacts"],
        "c5": fw_projects["c5"]["contacts"],
        "rp": fw_projects["rp"]["contacts"],
        "pack_admission": fw_projects["pack"]["contacts"],
        "safety_controller": fw_projects["safety"]["contacts"],
    }
    manifest_files_current = all(
        (FW_REPO / row["path"]).exists() and sha256(FW_REPO / row["path"]) == row["sha256"]
        for row in fw_manifest["files"]
    )
    residual_stages = Counter(stage for row in h3_residuals["registry"] for stage in row["closure_stages"])
    pinned_f3_revision = plan["firmware_f3_evidence"]["revision"]
    expected_fw_contract = expected_historical_firmware_copy(h2_contract)

    checks = {
        "h1_is_accepted": h1["status"] == "reviewed" and h1["final_acceptance"]["status"] == "accepted",
        "h1_machine_geometry_passed": h1["physical_fit"]["result"] == "paper_geometry_passed" and h1["physical_fit"]["all_external_machine_checks"] is True,
        "h1_m1_is_fully_assigned": h1["pin_resource_fit"]["m1"] == {"positions": 80, "assigned": 80, "reserved_no_connect": 0},
        "h1_m1_narrative_matches_machine_count": "M1 is 80 assigned / 0 reserved / 0 no-connect" in h1["pin_resource_fit"]["summary"],
        "h1_service_access_is_complete": h1["artifacts"]["external_service_access"]["external_usb_ports"] == 3 and h1["artifacts"]["external_service_access"]["external_recovery_buttons"] == 6 and h1["artifacts"]["external_service_access"]["internal_dbg10_headers"] == 3,
        "h2_is_accepted_and_closed": h2_acceptance["status"] == "reviewed_h2_user_accepted" and not h2_acceptance["open_h2_technical_findings"],
        "h2_final_counts_match_current_artifacts": h2_acceptance["final_counts"] == {"ledger_rows": 1081, "reconciled_electrical_identities": 1079, "root_named_nets": 270, "m1_physical_contacts": 80, "intentional_no_connects": 202},
        "h1_h2_firmware_domain_counts_match": {key: h1_counts[key] for key in expected_domains} == h2_domains == project_counts == expected_domains,
        "h2_bsp_contains_no_temporary_pins": h2_contract["bsp"]["temporary_pin_assignments_allowed"] is False,
        "h2_bsp_total_is_125": h2_contract["bsp"]["total_allocated_contacts"] == 125,
        "hardware_and_firmware_contracts_are_semantically_identical_with_fail_closed_firmware_authority": fw_contract == expected_fw_contract,
        "firmware_integration_view_matches_the_fail_closed_bsp_import": fw_integration == expected_fw_contract["integration_contract"],
        "firmware_generation_hashes_current": fw_generation["source_identity"]["source_sha256"] == sha256(FW_CONTRACT) and fw_generation["source_identity"]["integration_sha256"] == sha256(FW_INTEGRATION),
        "firmware_generation_counts_match_contract": fw_generation["expected_counts"] | {"domains": 5, "allocated_contacts": 125, "unique_nets": 112, "transports": 4, "signal_groups": 10} == fw_generation["expected_counts"] and all(fw_generation["expected_counts"][key] == value for key, value in {"domains": 5, "allocated_contacts": 125, "unique_nets": 112, "transports": 4, "signal_groups": 10}.items()),
        "generated_bsp_manifest_is_current": fw_manifest["source_sha256"] == sha256(FW_CONTRACT) and fw_manifest["allocated_contacts"] == 125 and manifest_files_current,
        "all_five_targets_consume_generated_bsp_without_invented_pins": set(fw_projects) == {"s3", "c5", "rp", "pack", "safety"} and fw_consumption["claims"]["temporary_or_hand_authored_pins"] is False,
        "h3_is_accepted_and_analytically_closed": h3_acceptance["status"] == "reviewed_h3_user_accepted" and h3_acceptance["review_summary"]["unresolved_analytical_findings"] == 0,
        "h3_acceptance_hashes_are_current": source_hashes_are_current(h3_acceptance["source_hashes"], REPO),
        "all_85_physical_residuals_remain_open_and_owned": len(h3_residuals["registry"]) == 85 and h3_residuals["summary"]["unassigned"] == 0 and all(row["status"] == "physical_evidence_required" and set(row["closure_stages"]) == set(row["evidence_contracts"]) for row in h3_residuals["registry"]),
        "physical_residual_stage_counts_match": dict(residual_stages) == {"H5": 9, "H6": 10, "H8": 78},
        "firmware_f3_is_reviewed": f3["status"] == "reviewed" and f3["claims"]["f3_exit_criteria_pass"] is True,
        "firmware_f3_input_hashes_are_current": all(sha256(FW_REPO / row["path"]) == row["sha256"] for row in f3["inputs"].values()),
        "firmware_f3_exact_claim_boundary_is_honest": f3["claims"]["s3_exact_virtual_execution_proven"] is True and f3["claims"]["non_s3_target_boot_proven"] is False and f3["claims"]["physical_peripherals_proven"] is False and f3["claims"]["physical_flash_or_rollback_proven"] is False,
        "firmware_f3_counts_match_review": f3["result"]["byte_reproducible_artifacts"] == 52 and f3["result"]["image_and_linked_memory_gates"] == 10 and f3["result"]["static_rollback_topologies"] == 5 and f3["result"]["physical_runs"] == 0,
        "firmware_f3_has_all_five_physical_gates": {row["target"] for row in f3["target_closure"]} == {"s3", "c5", "rp", "pack", "safety"} and all(row["physical_gate"] for row in f3["target_closure"]),
        "firmware_f3_revision_is_source_hash_bound": pinned_f3_revision == "source-hash-bound-precommit-revision",
        "preorder_contract_is_identical_across_repositories": PREORDER.read_bytes() == FW_PREORDER.read_bytes(),
        "preorder_virtual_gates_are_reviewed": all(next(row for row in preorder["gates"] if row["id"] == f"P{index}_{suffix}")["status"] == "reviewed" for index, suffix in ((0, "REQUIREMENTS_ARCHITECTURE"), (1, "MECHANICAL_DESIGN"), (2, "CURRENT_SCHEMATIC"), (3, "VIRTUAL_ELECTRICAL"), (4, "EXECUTABLE_FIRMWARE_MODEL"), (5, "TARGET_BUILDS_EMULATION"), (6, "PRE_LAYOUT_REVIEW"))),
        "orders_layout_and_fabrication_remain_blocked": plan["authorization"] == {"joined_read_only_review": True, "component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False} and next(row for row in preorder["gates"] if row["id"] == "P7_ENGINEERING_SAMPLE_ORDER")["status"] == "not_authorized" and next(row for row in preorder["gates"] if row["id"] == "P8_KICAD_LAYOUT_AND_PROTOTYPE_PCB")["status"] == "not_authorized",
        "h4_plan_records_all_substeps_reviewed": plan["status"] == "reviewed" and all(row["status"] == "reviewed" and all(child["status"] == "reviewed" for child in row.get("children", [])) for row in plan["substeps"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4 joined checks failed: " + ", ".join(failed))

    corrections = []
    sources = (PLAN, PREORDER, H1, H2_ACCEPTANCE, H2_INVENTORY, H2_CONTACTS, H2_NETS, H2_CONTRACT, H3_ACCEPTANCE, H3_RESIDUALS, FW_CONTRACT, FW_INTEGRATION, FW_GENERATION, FW_CONSUMPTION, FW_SOURCE_MANIFEST, FW_F3, FW_PREORDER)
    joined = {
        "schema_version": 1,
        "stage": "H4.1-R1",
        "status": "reviewed",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "method": "machine join of accepted mechanics, production ECAD, virtual electrical evidence, target-visible BSP consumption and firmware F3 execution boundaries",
        "source_hashes": {relative(path): sha256(path) for path in sources},
        "counts": {
            "h1_dimensioned_instances": h1["physical_fit"]["source_registered_instances"],
            "h2_ledger_rows": h2_inventory["summary"]["h2_instance_rows"],
            "h2_reconciled_electrical_identities": h2_contacts["summary"]["reconciled_electrical_identities"],
            "h2_root_nets": h2_nets["summary"]["root_named_nets"],
            "m1_contacts": h2_nets["summary"]["m1_physical_contacts"],
            "firmware_bsp_contacts": h2_contract["bsp"]["total_allocated_contacts"],
        },
        "firmware_f3_revision": pinned_f3_revision,
        "firmware_f3_result": f3["result"],
        "physical_residuals": {"total": len(h3_residuals["registry"]), "by_stage": dict(residual_stages), "closed_by_h4": 0},
        "checks": checks,
        "corrections": corrections,
        "open_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks), "failed": 0, "corrected_findings": len(corrections), "unresolved": 0, "status": "reviewed"},
        "authorization": {"component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False},
        "next": {"stage": "H4.2-R1", "action": "prove that the repeated dual-SA818S join contains no stale source or open virtual contradiction"},
    }
    correction = {
        "schema_version": 1,
        "stage": "H4.2-R1",
        "status": "reviewed",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "source_hashes": {relative(JOIN_OUTPUT): hashlib.sha256((json.dumps(joined, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()},
        "corrections": corrections,
        "summary": {"detected": len(corrections), "corrected_at_source": len(corrections), "regenerated": len(corrections), "open": 0, "functional_changes": 0, "bom_delta_usd": "0.0000"},
        "checks": {"no_new_join_findings": not corrections, "joined_review_is_clean_after_regeneration": joined["review_summary"]["unresolved"] == 0},
        "open_findings": [],
        "pending_decisions": [],
        "next": {"stage": "H4.3-R1", "action": "accept the joined boundary while preserving all physical-only gates and prohibitions"},
    }
    acceptance = {
        "schema_version": 1,
        "stage": "H4.3-R1",
        "status": "reviewed_h4_complete",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "reviewed_at": "2026-08-26",
        "source_hashes": {
            relative(JOIN_OUTPUT): correction["source_hashes"][relative(JOIN_OUTPUT)],
            relative(CORRECTION_OUTPUT): hashlib.sha256((json.dumps(correction, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest(),
        },
        "acceptance_meaning": [
            "all former single-RP R1 H1/H2/H3/F3 cross-domain checks are joined and reproducible",
            "no virtually testable blocker or contract mismatch remained in the superseded R1 snapshot",
            "all physical-only uncertainties retain exact H5/H6/H8 evidence owners",
        ],
        "acceptance_does_not_authorize": ["component or sample purchase", "PCB placement or routing", "prototype or production fabrication", "calling physical-only behavior proven"],
        "physical_residual_summary": joined["physical_residuals"],
        "correction_summary": correction["summary"],
        "open_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks) + len(correction["checks"]), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "acceptance_basis": "automatic acceptance authorized by the project owner for clean reviews without a functional, material-cost or safety decision",
        "next": {"stage": "H1-R2.31", "action": "close physical H1 blockers and all production gates before starting R2 H2"},
    }
    outputs = {
        JOIN_OUTPUT: json.dumps(joined, ensure_ascii=False, indent=2) + "\n",
        CORRECTION_OUTPUT: json.dumps(correction, ensure_ascii=False, indent=2) + "\n",
        ACCEPTANCE_OUTPUT: json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: report(joined, False),
        DOC_RU: report(joined, True),
    }
    return outputs, acceptance


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, acceptance = build()
    if args.write:
        GEN.mkdir(parents=True, exist_ok=True)
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
            print(f"wrote {relative(path)}")
    else:
        stale = [relative(path) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H4 artifacts: " + ", ".join(stale))
    print(f"ok: historical R1 H4 reviewed; {acceptance['review_summary']['checks']} joined checks, 0 unresolved; current H1-R2.31")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
