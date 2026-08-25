#!/usr/bin/env python3
"""Build the joined H4 mechanical/electrical/firmware pre-layout gate."""

from __future__ import annotations

import argparse
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


def report(joined: dict, russian: bool) -> str:
    residuals = joined["physical_residuals"]
    corrections = joined["corrections"]
    if russian:
        return f"""# Итог H4 · объединённый pre-layout gate

[English](h4-prelayout-gate-report.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

H4 проведён и закрыт. Принятая механика H1, production ECAD H2, виртуальные проверки H3 и исполнимые результаты firmware F3 сведены в одну проверяемую границу. После исправления трёх документальных несоответствий открытых виртуально проверяемых противоречий нет.

```mermaid
flowchart LR
  H1["H1<br/>механика"] --> H4["✅ H4<br/>единый pre-layout gate"]
  H2["H2<br/>ECAD"] --> H4
  H3["H3<br/>виртуальная электрика"] --> H4
  F3["F3<br/>сборки и эмуляция"] --> H4
  H4 --> H5["▶️ H5<br/>сначала поиск данных,<br/>затем только необходимые образцы"]
```

| Проверенная граница | Результат |
|---|---:|
| H1 M1 | 80 из 80 назначены; NC нет |
| H2 electrical identities / root nets | 1 046 / 268 |
| HW↔FW BSP | 5 доменов, 125 контактов, побайтно одинаковый контракт |
| Firmware F3 | 52 воспроизводимых artifacts; 10 memory gates; точный QEMU для S3 |
| H3 physical-only registry | {residuals['total']} строк; H5={residuals['by_stage']['H5']}, H6={residuals['by_stage']['H6']}, H8={residuals['by_stage']['H8']} |

## Что исправлено

| Finding | Исправление | Влияние |
|---|---|---|
| `{corrections[0]['id']}` | Удалено устаревшее утверждение о четырёх NC M1; источник и производные artifacts перегенерированы | Нет изменения распиновки, схемы или BOM |
| `{corrections[1]['id']}` | Публичные итоговые счётчики H2 привязаны к текущим machine artifacts | Только документация и traceability |
| `{corrections[2]['id']}` | Публичный счётчик intentional NC обновлён с 189 до текущих 191 | Только документация и traceability |

## Что H4 не доказывает

- Не закрывает ни одну из {residuals['total']} физических проверок: их владельцы H5/H6/H8 сохранены.
- Не доказывает boot четырёх non-S3 target, реальные peripherals, RF/антенны, тепловой режим, механический fit полученных деталей или flash rollback.
- Не разрешает закупку, PCB placement/routing или fabrication.

Следующая точная позиция — `H5.0.1`: сначала исчерпать документацию, производителя и серийные замены для девяти H5 residuals; закупка появится только для того, что нельзя доказать иначе, и потребует отдельного одобрения стоимости.

Машинные evidence: [`H4.1`](../hardware/verification/generated/H4-PLG11-joined-review.json), [`H4.2`](../hardware/verification/generated/H4-PLG12-correction-closure.json), [`H4.3`](../hardware/verification/generated/H4-PLG13-acceptance-package.json).
"""
    return f"""# H4 result · joined pre-layout gate

[Русский](h4-prelayout-gate-report.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

H4 is reviewed and closed. Accepted H1 mechanics, H2 production ECAD, H3 virtual verification and executable firmware F3 results now form one checkable boundary. Three documentation-only contradictions were corrected; no virtually testable contradiction remains open.

```mermaid
flowchart LR
  H1["H1<br/>mechanics"] --> H4["✅ H4<br/>joined pre-layout gate"]
  H2["H2<br/>ECAD"] --> H4
  H3["H3<br/>virtual electrical"] --> H4
  F3["F3<br/>builds and emulation"] --> H4
  H4 --> H5["▶️ H5<br/>research first,<br/>samples only if necessary"]
```

| Reviewed boundary | Result |
|---|---:|
| H1 M1 | 80 of 80 assigned; no NC |
| H2 electrical identities / root nets | 1,046 / 268 |
| HW↔FW BSP | 5 domains, 125 contacts, byte-identical contract |
| Firmware F3 | 52 reproducible artifacts; 10 memory gates; exact S3 QEMU |
| H3 physical-only registry | {residuals['total']} rows; H5={residuals['by_stage']['H5']}, H6={residuals['by_stage']['H6']}, H8={residuals['by_stage']['H8']} |

## Corrections

| Finding | Correction | Effect |
|---|---|---|
| `{corrections[0]['id']}` | Removed the stale four-M1-NC narrative and regenerated every derivative | No pinout, schematic or BOM change |
| `{corrections[1]['id']}` | Bound public H2 totals to the current machine artifacts | Documentation and traceability only |
| `{corrections[2]['id']}` | Updated the public intentional-NC count from 189 to the current 191 | Documentation and traceability only |

## What H4 does not prove

- None of the {residuals['total']} physical checks is closed; every H5/H6/H8 owner remains intact.
- Non-S3 boot, real peripherals, RF/antennas, thermal behavior, received-part fit and flash rollback remain physical gates.
- Purchase, PCB placement/routing and fabrication remain unauthorized.

The next exact position is `H5.0.1`: exhaust manufacturer documents and serial alternatives for the nine H5 residuals first. Only evidence that cannot be obtained otherwise may enter a separately cost-approved sample proposal.

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
    pinned_f3 = plan["firmware_f3_evidence"]["commit"]
    public_text = "\n".join(
        (REPO / name).read_text(encoding="utf-8")
        for name in ("README.md", "README.ru.md", "docs/stage-results.md", "docs/stage-results.ru.md", "docs/roadmap.md", "docs/roadmap.ru.md")
    )

    checks = {
        "h1_is_accepted": h1["status"] == "reviewed" and h1["final_acceptance"]["status"] == "accepted",
        "h1_machine_geometry_passed": h1["physical_fit"]["result"] == "paper_geometry_passed" and h1["physical_fit"]["all_external_machine_checks"] is True,
        "h1_m1_is_fully_assigned": h1["pin_resource_fit"]["m1"] == {"positions": 80, "assigned": 80, "reserved_no_connect": 0},
        "h1_m1_narrative_matches_machine_count": "M1 is 80 assigned / 0 reserved / 0 no-connect" in h1["pin_resource_fit"]["summary"],
        "h1_service_access_is_complete": h1["artifacts"]["external_service_access"]["external_usb_ports"] == 3 and h1["artifacts"]["external_service_access"]["external_recovery_buttons"] == 6 and h1["artifacts"]["external_service_access"]["internal_dbg10_headers"] == 3,
        "h2_is_accepted_and_closed": h2_acceptance["status"] == "reviewed_h2_user_accepted" and not h2_acceptance["open_h2_technical_findings"],
        "h2_final_counts_match_current_artifacts": h2_acceptance["final_counts"] == {"ledger_rows": 1048, "reconciled_electrical_identities": 1046, "root_named_nets": 268, "m1_physical_contacts": 80, "intentional_no_connects": 191},
        "h1_h2_firmware_domain_counts_match": {key: h1_counts[key] for key in expected_domains} == h2_domains == project_counts == expected_domains,
        "h2_bsp_contains_no_temporary_pins": h2_contract["bsp"]["temporary_pin_assignments_allowed"] is False,
        "h2_bsp_total_is_125": h2_contract["bsp"]["total_allocated_contacts"] == 125,
        "hardware_and_firmware_contracts_are_byte_identical": H2_CONTRACT.read_bytes() == FW_CONTRACT.read_bytes(),
        "integration_views_are_identical": h2_contract["integration_contract"] == fw_integration,
        "firmware_generation_hashes_current": fw_generation["source_identity"]["source_sha256"] == sha256(FW_CONTRACT) and fw_generation["source_identity"]["integration_sha256"] == sha256(FW_INTEGRATION),
        "firmware_generation_counts_match_contract": fw_generation["expected_counts"] | {"domains": 5, "allocated_contacts": 125, "unique_nets": 112, "transports": 4, "signal_groups": 10} == fw_generation["expected_counts"] and all(fw_generation["expected_counts"][key] == value for key, value in {"domains": 5, "allocated_contacts": 125, "unique_nets": 112, "transports": 4, "signal_groups": 10}.items()),
        "generated_bsp_manifest_is_current": fw_manifest["source_sha256"] == sha256(FW_CONTRACT) and fw_manifest["allocated_contacts"] == 125 and manifest_files_current,
        "all_five_targets_consume_generated_bsp_without_invented_pins": set(fw_projects) == {"s3", "c5", "rp", "pack", "safety"} and fw_consumption["claims"]["temporary_or_hand_authored_pins"] is False,
        "h3_is_accepted_and_analytically_closed": h3_acceptance["status"] == "reviewed_h3_user_accepted" and h3_acceptance["review_summary"]["unresolved_analytical_findings"] == 0,
        "h3_acceptance_hashes_are_current": source_hashes_are_current(h3_acceptance["source_hashes"], REPO),
        "all_85_physical_residuals_remain_open_and_owned": len(h3_residuals["registry"]) == 85 and h3_residuals["summary"]["unassigned"] == 0 and all(row["status"] == "physical_evidence_required" and set(row["closure_stages"]) == set(row["evidence_contracts"]) for row in h3_residuals["registry"]),
        "physical_residual_stage_counts_match": dict(residual_stages) == {"H5": 9, "H6": 9, "H8": 78},
        "firmware_f3_is_reviewed": f3["status"] == "reviewed" and f3["claims"]["f3_exit_criteria_pass"] is True,
        "firmware_f3_input_hashes_are_current": all(sha256(FW_REPO / row["path"]) == row["sha256"] for row in f3["inputs"].values()),
        "firmware_f3_exact_claim_boundary_is_honest": f3["claims"]["s3_exact_virtual_execution_proven"] is True and f3["claims"]["non_s3_target_boot_proven"] is False and f3["claims"]["physical_peripherals_proven"] is False and f3["claims"]["physical_flash_or_rollback_proven"] is False,
        "firmware_f3_counts_match_review": f3["result"]["byte_reproducible_artifacts"] == 52 and f3["result"]["image_and_linked_memory_gates"] == 10 and f3["result"]["static_rollback_topologies"] == 5 and f3["result"]["physical_runs"] == 0,
        "firmware_f3_has_all_five_physical_gates": {row["target"] for row in f3["target_closure"]} == {"s3", "c5", "rp", "pack", "safety"} and all(row["physical_gate"] for row in f3["target_closure"]),
        "pinned_f3_commit_is_in_current_firmware_history": git_commit_is_available_and_in_current_history(pinned_f3),
        "preorder_contract_is_identical_across_repositories": PREORDER.read_bytes() == FW_PREORDER.read_bytes(),
        "preorder_virtual_gates_are_reviewed": all(next(row for row in preorder["gates"] if row["id"] == f"P{index}_{suffix}")["status"] == "reviewed" for index, suffix in ((0, "REQUIREMENTS_ARCHITECTURE"), (1, "MECHANICAL_DESIGN"), (2, "CURRENT_SCHEMATIC"), (3, "VIRTUAL_ELECTRICAL"), (4, "EXECUTABLE_FIRMWARE_MODEL"), (5, "TARGET_BUILDS_EMULATION"), (6, "PRE_LAYOUT_REVIEW"))),
        "orders_layout_and_fabrication_remain_blocked": plan["authorization"] == {"joined_read_only_review": True, "component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False} and next(row for row in preorder["gates"] if row["id"] == "P7_ENGINEERING_SAMPLE_ORDER")["status"] == "not_authorized" and next(row for row in preorder["gates"] if row["id"] == "P8_KICAD_LAYOUT_AND_PROTOTYPE_PCB")["status"] == "not_authorized",
        "h4_plan_records_all_substeps_reviewed": plan["status"] == "reviewed" and all(row["status"] == "reviewed" and all(child["status"] == "reviewed" for child in row.get("children", [])) for row in plan["substeps"]),
        "public_h2_totals_are_current": all(token not in public_text for token in ("1,026", "1 026", "1,033", "1 033", "1,035", "1 035", "266 root nets", "189 physical NC", "189 физических NC", "all 189 intentional NC")) and "1,046 electrical identities" in public_text and "1 046 электрических identities" in public_text and "all 191 intentional NCs" in public_text,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4 joined checks failed: " + ", ".join(failed))

    corrections = [
        {
            "id": "H4-JOIN-001",
            "finding": "H1 machine counts said 80 assigned M1 contacts while its inherited narrative still claimed four reserved/no-connect contacts",
            "source_correction": "hardware/architecture/candidates/G2F-3I.json now states 80 assigned / 0 reserved / 0 no-connect and all H1/H2/H3 derivatives were regenerated",
            "functional_effect": "none; the accepted 80-contact electrical mapping did not change",
            "cost_effect_usd": "0.0000",
        },
        {
            "id": "H4-JOIN-002",
            "finding": "the product-facing H2 summaries retained superseded inventory, identity and root-net totals",
            "source_correction": "H2 acceptance now derives final counts from H2-REV71/72/73 and every public summary uses 1048 / 1046 / 268",
            "functional_effect": "none; documentation and traceability now match current generated ECAD evidence",
            "cost_effect_usd": "0.0000",
        },
        {
            "id": "H4-JOIN-003",
            "finding": "the product-facing H2 summaries retained the superseded count of 189 intentional no-connect contacts while the current native register contains 191",
            "source_correction": "H2 acceptance now derives the NC count from H2-REV62 and all public summaries use 191",
            "functional_effect": "none; the KiCad no-connect markers and rationales were already present and reviewed",
            "cost_effect_usd": "0.0000",
        },
    ]
    sources = (PLAN, PREORDER, H1, H2_ACCEPTANCE, H2_INVENTORY, H2_CONTACTS, H2_NETS, H2_CONTRACT, H3_ACCEPTANCE, H3_RESIDUALS, FW_CONTRACT, FW_INTEGRATION, FW_GENERATION, FW_CONSUMPTION, FW_SOURCE_MANIFEST, FW_F3, FW_PREORDER)
    joined = {
        "schema_version": 1,
        "stage": "H4.1",
        "status": "reviewed",
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
        "firmware_f3_commit": pinned_f3,
        "firmware_f3_result": f3["result"],
        "physical_residuals": {"total": len(h3_residuals["registry"]), "by_stage": dict(residual_stages), "closed_by_h4": 0},
        "checks": checks,
        "corrections": corrections,
        "open_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks), "failed": 0, "corrected_findings": len(corrections), "unresolved": 0, "status": "reviewed"},
        "authorization": {"component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False},
        "next": {"stage": "H4.2", "action": "prove that every joined-review contradiction is corrected at source and all affected evidence is regenerated"},
    }
    correction = {
        "schema_version": 1,
        "stage": "H4.2",
        "status": "reviewed",
        "source_hashes": {relative(JOIN_OUTPUT): hashlib.sha256((json.dumps(joined, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()},
        "corrections": corrections,
        "summary": {"detected": len(corrections), "corrected_at_source": len(corrections), "regenerated": len(corrections), "open": 0, "functional_changes": 0, "bom_delta_usd": "0.0000"},
        "checks": {"all_findings_have_source_corrections": all(row["source_correction"] for row in corrections), "all_findings_are_nonfunctional": all(row["functional_effect"].startswith("none") for row in corrections), "joined_review_is_clean_after_regeneration": joined["review_summary"]["unresolved"] == 0},
        "open_findings": [],
        "pending_decisions": [],
        "next": {"stage": "H4.3", "action": "accept the joined boundary while preserving all physical-only gates and prohibitions"},
    }
    acceptance = {
        "schema_version": 1,
        "stage": "H4.3",
        "status": "reviewed_h4_complete",
        "source_hashes": {
            relative(JOIN_OUTPUT): correction["source_hashes"][relative(JOIN_OUTPUT)],
            relative(CORRECTION_OUTPUT): hashlib.sha256((json.dumps(correction, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest(),
        },
        "acceptance_meaning": [
            "all currently possible H1/H2/H3/F3 cross-domain checks are joined and reproducible",
            "no virtually testable blocker or contract mismatch remains before H5",
            "all physical-only uncertainties retain exact H5/H6/H8 evidence owners",
        ],
        "acceptance_does_not_authorize": ["component or sample purchase", "PCB placement or routing", "prototype or production fabrication", "calling physical-only behavior proven"],
        "physical_residual_summary": joined["physical_residuals"],
        "correction_summary": correction["summary"],
        "open_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks) + len(correction["checks"]), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "acceptance_basis": "automatic acceptance authorized by the project owner for clean reviews without a functional, material-cost or safety decision",
        "next": {"stage": "H5.0.1", "action": "exhaust documentary and serial-replacement evidence before proposing any physical sample purchase"},
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
    print(f"ok: H4 reviewed; {acceptance['review_summary']['checks']} joined checks, 0 unresolved, next H5.0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
