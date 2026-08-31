#!/usr/bin/env python3
"""Close the three owned H4-R2 BSP corrections against built firmware."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FW_ROOT = ROOT.parent / "esp32-leshy2-firmware"
PLAN = ROOT / "hardware/verification/h4-r2-prelayout-plan.json"
DIAGNOSTIC = ROOT / "hardware/verification/generated/H4-R2-contract-reconciliation.json"
JOINED = ROOT / "hardware/verification/generated/H4-R2-joined-crosscheck.json"
FREEZE = ROOT / "hardware/verification/generated/H4-R2-input-freeze.json"
H2 = ROOT / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
PREORDER = ROOT / "hardware/verification/preorder-verification-contract.json"
FW_H0 = FW_ROOT / "config/h0_r2_hardware_contract.json"
FW_MODEL = FW_ROOT / "config/f2_r2_bsp_generation.json"
FW_MANIFEST = FW_ROOT / "generated/r2/source_manifest.json"
FW_CONSUMPTION = FW_ROOT / "config/f2_r2_bsp_consumption.json"
FW_BUILD = FW_ROOT / "config/f2_r2_build_qualification.json"
FW_ACCEPTANCE = FW_ROOT / "config/h3_r2_acceptance.json"
FW_TARGETS = {
    "s3": FW_ROOT / "targets/s3/main/app_main.c",
    "c5": FW_ROOT / "targets/c5/main/app_main.c",
    "rf_rp": FW_ROOT / "targets/rf_rp/main.c",
    "hub_rp": FW_ROOT / "targets/hub_rp/main.c",
    "pack": FW_ROOT / "targets/pack/main.c",
    "safety": FW_ROOT / "targets/safety/main.c",
}
OUTPUT = ROOT / "hardware/verification/generated/H4-R2-correction-closure.json"
DOC_EN = ROOT / "docs/h4-r2-correction-closure.md"
DOC_RU = ROOT / "docs/h4-r2-correction-closure.ru.md"
EXPECTED_COUNTS = {
    "s3": 33,
    "c5": 14,
    "rf_rp": 48,
    "hub_rp": 48,
    "pack": 13,
    "safety": 17,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract_hash(rows: list[dict]) -> str:
    normalized = []
    for row in rows:
        contact = row.get("contact")
        gpio = row.get("gpio")
        if gpio is None and isinstance(contact, str):
            match = re.match(r"^(?:GPIO|PA)(\d+)", contact)
            if match:
                gpio = int(match.group(1))
        if not isinstance(gpio, int):
            raise ValueError(f"H2 row has no numeric controller contact: {row!r}")
        normalized.append(
            {
                "contact": contact or f"GPIO{gpio}",
                "gpio": gpio,
                "net": row["net"],
                "peripheral": row.get("peripheral") or row.get("controller"),
                "endpoint": row.get("endpoint"),
                "gate": row.get("gate") or row.get("reset_proof") or row.get("sharing_proof"),
                "direction": row["direction"],
            }
        )
    payload = json.dumps(
        normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_blob(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=FW_ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ValueError(f"cannot read firmware build source {commit}:{relative}")
    return result.stdout


def relative(path: Path) -> str:
    if path.is_relative_to(ROOT):
        return str(path.relative_to(ROOT))
    return str(Path("../esp32-leshy2-firmware") / path.relative_to(FW_ROOT))


def _build_live_correction() -> tuple[dict[Path, str], dict]:
    plan = load(PLAN)
    diagnostic = load(DIAGNOSTIC)
    joined = load(JOINED)
    freeze = load(FREEZE)
    h2 = load(H2)
    preorder = load(PREORDER)
    fw_h0 = load(FW_H0)
    model = load(FW_MODEL)
    manifest = load(FW_MANIFEST)
    consumption = load(FW_CONSUMPTION)
    qualification = load(FW_BUILD)
    acceptance = load(FW_ACCEPTANCE)

    h2_domains = h2["r2_reconciliation"]["domain_contracts"]
    expected = {row["id"]: row for row in h2_domains}
    generated = {row["id"]: row for row in manifest["domains"]}
    model_domains = {row["id"]: row for row in model["domains"]}
    coverage = []
    for domain_id, count in EXPECTED_COUNTS.items():
        source = expected[domain_id]
        current = generated[domain_id]
        row = {
            "domain": domain_id,
            "h2_rows": len(source["pin_map"]),
            "generated_rows": current["pins"],
            "mapping": current["mapping"],
            "h2_pin_contract_sha256": contract_hash(source["pin_map"]),
            "generated_pin_contract_sha256": current["pin_contract_sha256"],
        }
        row["exact"] = (
            row["h2_rows"] == row["generated_rows"] == count
            and row["mapping"] == "exact_pins"
            and row["h2_pin_contract_sha256"] == row["generated_pin_contract_sha256"]
        )
        coverage.append(row)

    generated_files_current = all(
        (FW_ROOT / row["path"]).is_file()
        and (FW_ROOT / row["path"]).stat().st_size == row["bytes"]
        and sha256(FW_ROOT / row["path"]) == row["sha256"]
        for row in manifest["files"]
    )
    target_guards = {
        domain_id: (
            "L2_R2_MAPPING_EXACT_PINS" in path.read_text(encoding="utf-8")
            and f"pin_count != UINT16_C({EXPECTED_COUNTS[domain_id]})"
            in path.read_text(encoding="utf-8")
        )
        for domain_id, path in FW_TARGETS.items()
    }
    build_commit = qualification["repo_commit"]
    build_commit_contains_current_bsp = (
        git_blob(build_commit, "generated/r2/source_manifest.json")
        == FW_MANIFEST.read_bytes()
        and git_blob(build_commit, "config/f2_r2_bsp_generation.json")
        == FW_MODEL.read_bytes()
    )
    jobs = qualification["jobs"]
    checks = {
        "h4_plan_advances_after_reviewed_correction": plan["current_substep"] == "H4-R2.3" and {row["id"]: row["status"] for row in plan["substeps"]}["H4-R2.2"] == "reviewed",
        "diagnostic_snapshot_retains_original_gap": diagnostic["summary"]["hardware_pin_rows"] == 173 and diagnostic["summary"]["generated_bsp_pin_rows"] == 135 and diagnostic["summary"]["missing_generated_bsp_rows"] == 38,
        "joined_snapshot_has_three_owned_corrections": joined["summary"]["cross_domain_contradictions"] == 3 and joined["summary"]["unowned_contradictions"] == 0 and [row["domain"] for row in joined["contradictions"]] == ["c5", "pack", "safety"],
        "joined_freeze_is_current": freeze["status"] == "reviewed" and freeze["summary"]["failed_checks"] == 0,
        "h2_and_firmware_projection_are_identical": h2_domains == fw_h0["domain_contracts"],
        "all_six_generated_contracts_are_exact": list(generated) == list(EXPECTED_COUNTS) and all(row["exact"] for row in coverage) and sum(row["generated_rows"] for row in coverage) == 173,
        "generation_model_selects_complete_h2_maps": model["status"] == "reviewed_generated_h2_boundary" and model["source"]["hardware_marker"] == "H2-R2.1.5" and all(model_domains[domain_id] == {"id": domain_id, "mapping": "exact_pins", "source_domain_id": domain_id} for domain_id in EXPECTED_COUNTS),
        "generation_source_hash_is_current": model["source"]["sha256"] == sha256(FW_H0) and manifest["source"] == model["source"],
        "all_generated_files_match_manifest": generated_files_current,
        "one_generated_domain_is_consumed_per_target": consumption["status"] == "reviewed" and [row["id"] for row in consumption["projects"]] == list(EXPECTED_COUNTS),
        "all_targets_fail_closed_on_exact_map_and_count": all(target_guards.values()),
        "qualification_build_commit_contains_corrected_bsp": build_commit_contains_current_bsp,
        "all_twelve_target_builds_passed_after_correction": qualification["claims"]["all_target_compilation_and_link_passed"] is True and qualification["totals"]["build_runs"] == 12 and qualification["totals"]["artifacts"] == 60 and qualification["totals"]["maps"] == 16 and qualification["totals"]["size_gates"] == 16 and len(jobs) == 12 and not any(job["warnings"] for job in jobs),
        "build_claim_stays_bounded": qualification["claims"]["runtime_boot_proven"] is False and qualification["claims"]["physical_hardware_proven"] is False,
        "display_implementation_obligation_remains_open": len(acceptance["firmware_obligations"]) == 1 and acceptance["firmware_obligations"][0]["owner"] == "F5/F6" and acceptance["claims"]["i8080_target_implementation_proven"] is False,
        "no_purchase_layout_or_fabrication_authority": preorder["current_truth"]["order_authorized"] is False and not any(plan["authorization"][key] for key in ("component_purchase", "pcb_placement_and_routing", "fabrication")),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4-R2.2 correction closure failed: " + ", ".join(failed))

    sources = (
        PLAN, DIAGNOSTIC, JOINED, FREEZE, H2, PREORDER, FW_H0, FW_MODEL,
        FW_MANIFEST, FW_CONSUMPTION, FW_BUILD, FW_ACCEPTANCE, *FW_TARGETS.values(),
    )
    result = {
        "schema_version": 1,
        "artifact": "H4-R2-correction-closure",
        "marker": "H4-R2.2",
        "status": "reviewed",
        "source_sha256": {relative(path): sha256(path) for path in sources},
        "summary": {
            "domains": 6,
            "h2_controller_rows": 173,
            "generated_bsp_rows": 173,
            "restored_rows": 38,
            "exact_domains": 6,
            "remaining_contradictions": 0,
            "qualified_configurations": 12,
            "verified_artifacts": 60,
            "verified_maps": 16,
            "passed_size_gates": 16,
            "build_warnings": 0,
            "retained_firmware_obligations": 1,
            "physical_residuals_carried": 51,
            "failed_checks": 0,
        },
        "domain_coverage": coverage,
        "target_fail_closed_guards": target_guards,
        "qualified_firmware_commit": build_commit,
        "checks": checks,
        "retained_obligations": acceptance["firmware_obligations"],
        "authorization": {
            "component_purchase": False,
            "pcb_placement_and_routing": False,
            "fabrication": False,
        },
        "next": {
            "marker": "H4-R2.3",
            "action": "publish the joined R2 pre-layout gate and transfer exact residual ownership to H5/H6/H8",
        },
    }
    rows = "\n".join(
        f"| `{row['domain']}` | {row['h2_rows']} | {row['generated_rows']} | `{row['mapping']}` | ✅ |"
        for row in coverage
    )
    en = f"""# H4-R2.2 BSP correction closure

[Русский](h4-r2-correction-closure.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Diagnostic](h4-r2-contract-reconciliation.md)

The three owned firmware-generation corrections are closed without changing the hardware pinout. The generated BSP now represents all **173/173** reviewed H2 controller rows; every target rejects an incomplete mapping/count before normal work.

| Domain | H2 rows | BSP rows | Mapping | Result |
|---|---:|---:|---|---|
{rows}

The corrected BSP was compiled and linked in all **12** locked debug/release configurations. The qualification verified **60 artifacts, 16 map files and 16 size gates**, with no build warnings. This proves source-level target integration and linking; it does not claim runtime boot or physical hardware.

The separate F5/F6 direct-i8080 implementation obligation and all 51 H5/H6/H8 physical residuals remain open. Purchase, placement, routing and fabrication remain unauthorized.

**Current marker: `H4-R2.3`.**

[Machine closure](../hardware/verification/generated/H4-R2-correction-closure.json).
"""
    ru = f"""# Закрытие исправлений BSP H4-R2.2

[English](h4-r2-correction-closure.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Диагностика](h4-r2-contract-reconciliation.ru.md)

Три назначенных исправления firmware-generation закрыты без изменения аппаратной распиновки. Сгенерированный BSP теперь представляет все **173/173** проведённых H2 controller-строк; каждый target отказывается от нормального старта при неполном mapping/count.

| Домен | Строк H2 | Строк BSP | Mapping | Итог |
|---|---:|---:|---|---|
{rows}

Исправленный BSP скомпилирован и слинкован во всех **12** закреплённых конфигурациях debug/release. Квалификация проверила **60 artifacts, 16 map-файлов и 16 size gates** без build warnings. Это доказывает интеграцию и линковку target-кода, но не runtime boot и не физическое железо.

Отдельное обязательство F5/F6 по direct i8080 и все 51 physical-остаток H5/H6/H8 остаются открытыми. Закупка, placement, routing и печать не разрешены.

**Текущий маркер: `H4-R2.3`.**

[Машинное закрытие](../hardware/verification/generated/H4-R2-correction-closure.json).
"""
    outputs = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }
    return outputs, result


def build() -> tuple[dict[Path, str], dict]:
    """Validate the immutable H4-R2.2 correction and build snapshot."""

    result = load(OUTPUT)
    summary = result.get("summary", {})
    if (
        result.get("marker") != "H4-R2.2"
        or result.get("status") != "reviewed"
        or (summary.get("h2_controller_rows"), summary.get("generated_bsp_rows"), summary.get("restored_rows")) != (173, 173, 38)
        or summary.get("remaining_contradictions") != 0
        or (summary.get("qualified_configurations"), summary.get("verified_artifacts"), summary.get("verified_maps"), summary.get("passed_size_gates")) != (12, 60, 16, 16)
        or not all(result.get("checks", {}).values())
        or not all(result.get("target_fail_closed_guards", {}).values())
    ):
        raise ValueError("invalid immutable H4-R2.2 correction snapshot")
    return {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
    }, result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, result = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale H4-R2.2 correction artifacts: " + ", ".join(stale))
    print(
        "ok: H4-R2.2 reviewed; 173/173 H2 rows and 12/12 target builds, "
        "next H4-R2.3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
