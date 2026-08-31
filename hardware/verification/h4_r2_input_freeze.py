#!/usr/bin/env python3
"""Freeze the current R2 mechanics, ECAD, H3 and firmware inputs for H4."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FW_ROOT = ROOT.parent / "esp32-leshy2-firmware"
PLAN = ROOT / "hardware/verification/h4-r2-prelayout-plan.json"
HW_INPUTS = {
    "roadmap": ROOT / "hardware/verification/hardware-roadmap-state.json",
    "h0_authority": ROOT / "hardware/architecture/generated/H0-R2-authority-gate.json",
    "h1_physical": ROOT / "hardware/product-design/generated/H1-R2-placement-audit.json",
    "h2_kicad": ROOT / "hardware/ecad/generated/H2-R2-native-kicad-projects.json",
    "h2_hwfw": ROOT / "hardware/ecad/generated/H2-R2-hwfw-contract.json",
    "h2_m1": ROOT / "hardware/ecad/generated/H2-R2-interboard-m1.json",
    "h3_acceptance": ROOT / "hardware/verification/generated/H3-R2-acceptance-package.json",
    "h3_crosscheck": ROOT / "hardware/verification/generated/H3-R2-crosscheck.json",
    "h3_residuals": ROOT / "hardware/verification/generated/H3-R2-physical-residuals.json",
    "preorder": ROOT / "hardware/verification/preorder-verification-contract.json",
}
FW_INPUTS = {
    "roadmap": FW_ROOT / "config/firmware_roadmap_state.json",
    "h0_contract": FW_ROOT / "config/h0_r2_hardware_contract.json",
    "h2_sync": FW_ROOT / "config/r2_h2_sync_gate.json",
    "h3_transition": FW_ROOT / "config/h3_r2_transition_contract.json",
    "h3_handover": FW_ROOT / "config/h3_r2_handover_contract.json",
    "h3_inrush_watchdog": FW_ROOT / "config/h3_r2_inrush_watchdog_contract.json",
    "h3_digital": FW_ROOT / "config/h3_r2_digital_interfaces.json",
    "h3_rf": FW_ROOT / "config/h3_r2_rf_coexistence.json",
    "h3_thermal": FW_ROOT / "config/h3_r2_thermal_fault.json",
    "h3_acceptance": FW_ROOT / "config/h3_r2_acceptance.json",
    "f2_targets": FW_ROOT / "config/f2_r2_target_projects.json",
    "f2_bsp": FW_ROOT / "config/f2_r2_bsp_generation.json",
    "f2_consumption": FW_ROOT / "config/f2_r2_bsp_consumption.json",
    "f2_builds": FW_ROOT / "config/f2_r2_build_qualification.json",
}
OUTPUT = ROOT / "hardware/verification/generated/H4-R2-input-freeze.json"
DOC_EN = ROOT / "docs/h4-r2-input-freeze.md"
DOC_RU = ROOT / "docs/h4-r2-input-freeze.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    plan = load(PLAN)
    hw = {name: load(path) for name, path in HW_INPUTS.items()}
    fw = {name: load(path) for name, path in FW_INPUTS.items()}
    steps = {row["id"]: row["status"] for row in plan["substeps"]}
    h3_import_sources = fw["h3_acceptance"]["sources"]
    imported_hash_checks = {
        name: sha256(FW_ROOT / row["path"]) == row["sha256"]
        for name, row in h3_import_sources.items()
    }
    checks = {
        "h4_plan_exposes_reviewed_input_freeze": plan["status"] == "current" and steps["H4-R2.0.1"] == "reviewed" and plan["current_substep"] == "H4-R2.2",
        "hardware_roadmap_is_at_h4_r2_2": hw["roadmap"]["current_stage"] == "H4" and hw["roadmap"]["current_substep"] == "H4-R2.2",
        "h0_h1_and_h2_boundaries_pass": hw["h0_authority"]["status"] == "pass_current_r2_h2_reconciled" and hw["h1_physical"]["status"] == "pass" and all(hw[key]["status"] == "pass" for key in ("h2_kicad", "h2_hwfw", "h2_m1")),
        "h3_r2_is_reviewed_without_analytical_finding": hw["h3_acceptance"]["status"] == "reviewed" and hw["h3_acceptance"]["result"]["open_analytical_findings"] == 0,
        "all_51_physical_residuals_remain_open_and_owned": hw["h3_residuals"]["summary"]["physical_evidence_rows"] == 51 and hw["h3_residuals"]["summary"]["unassigned"] == 0 and all(row["status"] == "physical_evidence_required" for row in hw["h3_residuals"]["registry"]),
        "firmware_roadmap_tracks_the_same_h4_marker": fw["roadmap"]["hardware_boundary"]["current_hardware_stage"] == "H4" and fw["roadmap"]["hardware_boundary"]["current_hardware_substep"] == "H4-R2.2",
        "firmware_h2_gate_is_current_six_domain_r2": fw["h2_sync"]["status"] == "reviewed_six_domain_h2_export",
        "firmware_h3_acceptance_import_matches_hardware": all(imported_hash_checks.values()) and fw["h3_acceptance"]["hardware_marker"] == "H3-R2.7",
        "firmware_h3_import_keeps_the_i8080_obligation_open": len(fw["h3_acceptance"]["firmware_obligations"]) == 1 and fw["h3_acceptance"]["firmware_obligations"][0]["owner"] == "F5/F6" and not fw["h3_acceptance"]["claims"]["i8080_target_implementation_proven"],
        "firmware_f2_r2_target_and_bsp_evidence_is_reviewed": fw["f2_targets"]["status"] == "reviewed_structure" and fw["f2_bsp"]["status"] == "reviewed_generated_boundary" and fw["f2_consumption"]["status"] == "reviewed",
        "firmware_f2_r2_build_qualification_is_reviewed": fw["f2_builds"]["status"] == "reviewed_target_build_qualification",
        "all_twenty_four_join_inputs_exist": len(HW_INPUTS) + len(FW_INPUTS) == 24 and all(path.is_file() for path in (*HW_INPUTS.values(), *FW_INPUTS.values())),
        "no_order_layout_or_fabrication_authority": not any(plan["authorization"][key] for key in ("component_purchase", "pcb_placement_and_routing", "fabrication")) and hw["preorder"]["current_truth"]["order_authorized"] is False,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4-R2.0.1 input freeze failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "artifact": "H4-R2-input-freeze",
        "marker": "H4-R2.0.1",
        "status": "reviewed",
        "source_sha256": {
            "hardware/verification/h4-r2-prelayout-plan.json": sha256(PLAN),
            **{f"hardware/{name}": sha256(path) for name, path in HW_INPUTS.items()},
            **{f"firmware/{name}": sha256(path) for name, path in FW_INPUTS.items()},
        },
        "input_groups": {
            "mechanics": ["hardware/h0_authority", "hardware/h1_physical"],
            "ecad": ["hardware/h2_kicad", "hardware/h2_hwfw", "hardware/h2_m1"],
            "electrical": ["hardware/h3_acceptance", "hardware/h3_crosscheck", "hardware/h3_residuals"],
            "firmware_boundary": [f"firmware/{name}" for name in FW_INPUTS],
            "release_safety": ["hardware/preorder", "hardware/roadmap"],
        },
        "summary": {
            "hardware_inputs": len(HW_INPUTS),
            "firmware_inputs": len(FW_INPUTS),
            "total_inputs": len(HW_INPUTS) + len(FW_INPUTS),
            "cross_repository_h3_hashes_checked": len(imported_hash_checks),
            "cross_repository_h3_hash_mismatches": sum(not value for value in imported_hash_checks.values()),
            "physical_residuals_carried": 51,
            "firmware_obligations_carried": 1,
            "checks": len(checks),
            "failed_checks": 0,
        },
        "checks": checks,
        "boundary": {
            "firmware_phase": fw["roadmap"]["phase"],
            "firmware_current_substep": fw["roadmap"]["current_substep"],
            "historical_r1_execution_evidence": "regression-only; not current dual-RP proof",
            "physical_evidence": "still open under H5/H6/H8; not consumed by the H4 input freeze",
        },
        "authorization": {"joined_read_only_review": True, "component_purchase": False, "pcb_placement_and_routing": False, "fabrication": False},
        "errors": [],
        "next": {"marker": "H4-R2.0.2", "action": "reconcile every hardware-visible firmware contract and retained implementation obligation"},
    }
    en = f"""# H4-R2 joined-input freeze

[Русский](h4-r2-input-freeze.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [H3 result](h3-r2-acceptance.md)

`H4-R2.0.1` is reviewed. The joined pre-layout gate now has one hash-bound input set: `{manifest['summary']['hardware_inputs']}` hardware artifacts and `{manifest['summary']['firmware_inputs']}` firmware artifacts (`{manifest['summary']['total_inputs']}` total). All `{manifest['summary']['cross_repository_h3_hashes_checked']}` cross-repository H3 import hashes match.

The freeze carries the reviewed H1-R2.37 mechanics, native H2-R2.1.5 ECAD, H3-R2.7 analytical result, current six-domain firmware contracts and reviewed F2-R2 target/BSP/build evidence. Historical R1 F3/F4 execution remains regression-only and cannot prove the current dual-RP topology.

It also carries all `51` still-open physical rows and the explicit F5/F6 i8080 implementation obligation. Nothing is silently treated as completed. Purchase, placement, routing and fabrication remain unauthorized.

H4-R2.0.2/H4-R2.1 subsequently found one owned C5/Pack/Safety BSP-generation gap. **Current marker: `H4-R2.2`.**

[Machine freeze](../hardware/verification/generated/H4-R2-input-freeze.json).
"""
    ru = f"""# Фиксация объединённых входов H4-R2

[English](h4-r2-input-freeze.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Итог H3](h3-r2-acceptance.ru.md)

`H4-R2.0.1` проведён ревью. Объединённый pre-layout gate теперь имеет один hash-bound набор: `{manifest['summary']['hardware_inputs']}` hardware-artifacts и `{manifest['summary']['firmware_inputs']}` firmware-artifacts (всего `{manifest['summary']['total_inputs']}`). Все `{manifest['summary']['cross_repository_h3_hashes_checked']}` cross-repository hashes импорта H3 совпадают.

Фиксация переносит проведённые mechanics H1-R2.37, native ECAD H2-R2.1.5, аналитический итог H3-R2.7, текущие six-domain firmware-контракты и проведённое F2-R2 target/BSP/build evidence. Историческое R1 execution-evidence F3/F4 остаётся только regression и не доказывает текущую dual-RP топологию.

Также перенесены все `51` ещё открытых physical-строк и явное обязательство F5/F6 по реализации i8080. Ничто молча не названо завершённым. Закупка, placement, routing и печать остаются запрещены.

Затем H4-R2.0.2/H4-R2.1 нашли один назначенный пробел генерации BSP C5/Pack/Safety. **Текущий маркер: `H4-R2.2`.**

[Машинная фиксация](../hardware/verification/generated/H4-R2-input-freeze.json).
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
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H4-R2.0.1 artifacts: " + ", ".join(stale))
    print(f"ok: H4-R2.0.1 reviewed; {manifest['summary']['total_inputs']} frozen inputs, next H4-R2.0.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
