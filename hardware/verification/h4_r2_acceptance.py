#!/usr/bin/env python3
"""Publish the global H4-R2 joined pre-layout gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FW_ROOT = ROOT.parent / "esp32-leshy2-firmware"
PLAN = ROOT / "hardware/verification/h4-r2-prelayout-plan.json"
FREEZE = ROOT / "hardware/verification/generated/H4-R2-input-freeze.json"
DIAGNOSTIC = ROOT / "hardware/verification/generated/H4-R2-contract-reconciliation.json"
JOINED = ROOT / "hardware/verification/generated/H4-R2-joined-crosscheck.json"
CORRECTION = ROOT / "hardware/verification/generated/H4-R2-correction-closure.json"
H2_M1 = ROOT / "hardware/ecad/generated/H2-R2-interboard-m1.json"
H3_ACCEPTANCE = ROOT / "hardware/verification/generated/H3-R2-acceptance-package.json"
H3_RESIDUALS = ROOT / "hardware/verification/generated/H3-R2-physical-residuals.json"
HW_ROADMAP = ROOT / "hardware/verification/hardware-roadmap-state.json"
H5_PLAN = ROOT / "hardware/verification/h5-component-evidence-plan.json"
PREORDER = ROOT / "hardware/verification/preorder-verification-contract.json"
FW_CORRECTION = FW_ROOT / "config/h4_r2_correction_closure.json"
FW_ROADMAP = FW_ROOT / "config/firmware_roadmap_state.json"
FW_ACCEPTANCE = FW_ROOT / "config/h3_r2_acceptance.json"
OUTPUT = ROOT / "hardware/verification/generated/H4-R2-acceptance-package.json"
DOC_EN = ROOT / "docs/h4-r2-acceptance.md"
DOC_RU = ROOT / "docs/h4-r2-acceptance.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    if path.is_relative_to(ROOT):
        return str(path.relative_to(ROOT))
    return str(Path("../esp32-leshy2-firmware") / path.relative_to(FW_ROOT))


def _build_live_acceptance() -> tuple[dict[Path, str], dict]:
    plan = load(PLAN)
    freeze = load(FREEZE)
    diagnostic = load(DIAGNOSTIC)
    joined = load(JOINED)
    correction = load(CORRECTION)
    m1 = load(H2_M1)
    h3 = load(H3_ACCEPTANCE)
    residuals = load(H3_RESIDUALS)
    hw_roadmap = load(HW_ROADMAP)
    h5 = load(H5_PLAN)
    preorder = load(PREORDER)
    fw_correction = load(FW_CORRECTION)
    fw_roadmap = load(FW_ROADMAP)
    fw_acceptance = load(FW_ACCEPTANCE)
    steps = {row["id"]: row["status"] for row in plan["substeps"]}

    checks = {
        "all_h4_r2_substeps_are_reviewed": plan["status"] == "reviewed" and plan["current_substep"] == "H4-R2.3" and all(status == "reviewed" for status in steps.values()),
        "joined_input_snapshot_is_complete": freeze["status"] == "reviewed" and freeze["summary"]["total_inputs"] == 24 and freeze["summary"]["failed_checks"] == 0,
        "original_gap_remains_auditable": diagnostic["summary"]["hardware_pin_rows"] == 173 and diagnostic["summary"]["generated_bsp_pin_rows"] == 135 and diagnostic["summary"]["missing_generated_bsp_rows"] == 38,
        "joined_review_owned_every_contradiction": joined["summary"]["cross_domain_contradictions"] == 3 and joined["summary"]["unowned_contradictions"] == 0,
        "all_joined_contradictions_are_closed": correction["status"] == "reviewed" and correction["summary"]["generated_bsp_rows"] == 173 and correction["summary"]["remaining_contradictions"] == 0 and correction["summary"]["failed_checks"] == 0,
        "all_eighty_m1_contacts_remain_exact": len(m1["contacts"]) == 80 and m1["status"] == "pass",
        "h3_has_no_analytical_finding": h3["status"] == "reviewed" and h3["result"]["open_analytical_findings"] == 0,
        "all_physical_residuals_have_exact_downstream_owners": residuals["summary"]["physical_evidence_rows"] == 51 and residuals["summary"]["unassigned"] == 0 and residuals["summary"]["by_closure_stage"] == {"H5": 1, "H6": 5, "H8": 46},
        "firmware_import_matches_hardware_correction": fw_correction["status"] == "reviewed_hardware_correction_imported" and fw_correction["source"]["sha256"] == sha256(CORRECTION) and fw_correction["reviewed_boundary"]["remaining_contradictions"] == 0,
        "firmware_i8080_obligation_stays_open": len(fw_acceptance["firmware_obligations"]) == 1 and fw_acceptance["firmware_obligations"][0]["owner"] == "F5/F6" and fw_acceptance["claims"]["i8080_target_implementation_proven"] is False,
        "both_roadmaps_advance_to_current_h5_work": hw_roadmap["current_stage"] == "H5" and hw_roadmap["current_substep"] == "H5.0.3-R1" and fw_roadmap["hardware_boundary"]["current_hardware_stage"] == "H5" and fw_roadmap["hardware_boundary"]["current_hardware_substep"] == "H5.0.3-R1",
        "h5_accepts_h4_without_spend_authority": h5["stage"] == "H5" and h5["current_substep"] == "H5.0.3-R1" and "H4 joined pre-layout gate reviewed" in h5["accepted_inputs"] and h5["authorization"]["sample_or_component_purchase"] is False and h5["authorization"]["pcb_placement_and_routing"] is False and h5["authorization"]["fabrication"] is False,
        "preorder_gate_remains_closed": preorder["current_truth"]["order_authorized"] is False,
        "h4_creates_no_purchase_layout_or_fabrication_authority": not any(plan["authorization"][key] for key in ("component_purchase", "pcb_placement_and_routing", "fabrication")),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H4-R2 global acceptance failed: " + ", ".join(failed))

    sources = (
        PLAN, FREEZE, DIAGNOSTIC, JOINED, CORRECTION, H2_M1, H3_ACCEPTANCE,
        H3_RESIDUALS, HW_ROADMAP, H5_PLAN, PREORDER, FW_CORRECTION,
        FW_ROADMAP, FW_ACCEPTANCE,
    )
    result = {
        "schema_version": 1,
        "artifact": "H4-R2-acceptance-package",
        "marker": "H4-R2.3",
        "status": "reviewed",
        "source_sha256": {relative(path): sha256(path) for path in sources},
        "result": {
            "joined_inputs": 24,
            "compute_domains": 6,
            "h2_controller_rows": 173,
            "generated_bsp_rows": 173,
            "m1_contacts": 80,
            "qualified_target_configurations": 12,
            "cross_domain_contradictions_remaining": 0,
            "open_analytical_findings": 0,
            "physical_residuals_transferred": 51,
            "physical_residuals_by_stage": {"H5": 1, "H6": 5, "H8": 46},
            "firmware_obligations_transferred": 1,
            "failed_checks": 0,
        },
        "checks": checks,
        "handoff": {
            "H5": "exact production identity, current factory route and received-part evidence; current H5.0.3-R1",
            "H6": "routed geometry, extracted values, production outputs and independent DFM/CPL review",
            "F5/F6": "instantiate and exercise the exact direct 20-MHz i8080 target configuration",
            "H8": "ordinary non-destructive measurement on the sole assembled prototype",
        },
        "claims": {
            "joined_prelayout_gate_reviewed": True,
            "current_hardware_and_firmware_contracts_agree": True,
            "virtual_prelayout_blocker_open": False,
            "physical_hardware_proven": False,
            "routing_proven": False,
            "component_purchase_authorized": False,
            "pcb_placement_and_routing_authorized": False,
            "fabrication_authorized": False,
        },
        "next": {
            "stage": "H5",
            "marker": "H5.0.3-R1",
            "action": "finish the exact-one-prototype component/factory evidence route without silent substitution",
        },
    }
    en = """# H4-R2 global result · joined pre-layout gate

[Русский](h4-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Stage results](stage-results.md#h4)

**H4-R2 is reviewed.** The current mechanics, native ECAD, virtual electrical evidence and hardware-visible firmware boundary now form one consistent pre-layout package. No cross-domain contradiction remains.

```text
H1 mechanics ─┐
H2 ECAD ──────┼─> H4 joined gate ──> H5 identity/factory evidence
H3 analysis ──┤                    ├─> H6 routed proof
FW BSP/build ─┘                    └─> H8 physical measurements
```

## Result at a glance

| Joined evidence | Reviewed result |
|---|---:|
| Hash-bound inputs | 24 |
| Compute domains | 6 |
| H2 controller rows represented in BSP | 173 / 173 |
| M1 contacts reconciled | 80 / 80 |
| Qualified target configurations | 12 / 12 |
| Remaining cross-domain contradictions | 0 |
| Open analytical findings | 0 |

The audit first found a real 38-row BSP-generation omission in C5, Pack and Safety. The original `135/173` diagnostic remains preserved; H4-R2.2 then restored all rows, added fail-closed mapping/count guards and requalified 60 artifacts, 16 maps and 16 size gates without warnings.

## What deliberately remains open

H4 transfers, rather than hides, all **51 physical residuals**: 1 to H5, 5 to H6 and 46 to H8. F5/F6 still owns one direct-i8080 implementation obligation. Runtime boot, routed geometry and measurements on the sole assembled prototype are therefore not claimed here.

H4 does **not** authorize component purchase, PCB placement/routing or fabrication. The current hardware work is **`H5.0.3-R1`**, completing the exact-one-prototype component/factory route without silent substitution.

[Machine acceptance package](../hardware/verification/generated/H4-R2-acceptance-package.json) · [BSP correction](h4-r2-correction-closure.md) · [input freeze](h4-r2-input-freeze.md).
"""
    ru = """# Глобальный итог H4-R2 · объединённый pre-layout gate

[English](h4-r2-acceptance.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Результаты этапов](stage-results.ru.md#h4)

**H4-R2 проведён ревью.** Текущие mechanics, native ECAD, виртуальные электрические evidence и видимая железу граница прошивки теперь образуют один согласованный pre-layout package. Междоменных противоречий не осталось.

```text
H1 mechanics ─┐
H2 ECAD ──────┼─> H4 joined gate ──> H5 identity/factory evidence
H3 analysis ──┤                    ├─> H6 routed proof
FW BSP/build ─┘                    └─> H8 physical measurements
```

## Результат кратко

| Объединённое evidence | Результат ревью |
|---|---:|
| Входов, связанных hashes | 24 |
| Вычислительных доменов | 6 |
| Controller-строк H2 в BSP | 173 / 173 |
| Сверенных контактов M1 | 80 / 80 |
| Квалифицированных target-конфигураций | 12 / 12 |
| Оставшихся междоменных противоречий | 0 |
| Открытых аналитических findings | 0 |

Аудит сначала нашёл реальный пропуск генерации 38 BSP-строк C5, Pack и Safety. Исходная диагностика `135/173` сохранена; затем H4-R2.2 восстановил все строки, добавил fail-closed проверки mapping/count и повторно квалифицировал 60 artifacts, 16 maps и 16 size gates без warnings.

## Что намеренно остаётся открытым

H4 передаёт, а не прячет, все **51 physical-остаток**: 1 в H5, 5 в H6 и 46 в H8. У F5/F6 остаётся одно обязательство по реализации direct i8080. Поэтому runtime boot, разведённая геометрия и измерения единственного собранного прототипа здесь не заявлены.

H4 **не** разрешает закупку компонентов, PCB placement/routing или печать. Текущая аппаратная работа — **`H5.0.3-R1`**: завершить маршрут компонентов/фабрики для ровно одного прототипа без молчаливых замен.

[Машинный пакет приёмки](../hardware/verification/generated/H4-R2-acceptance-package.json) · [исправление BSP](h4-r2-correction-closure.ru.md) · [фиксация входов](h4-r2-input-freeze.ru.md).
"""
    outputs = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }
    return outputs, result


def build() -> tuple[dict[Path, str], dict]:
    """Validate the immutable global H4-R2 acceptance snapshot."""

    result = load(OUTPUT)
    reviewed = result.get("result", {})
    if (
        result.get("marker") != "H4-R2.3"
        or result.get("status") != "reviewed"
        or reviewed.get("joined_inputs") != 24
        or reviewed.get("h2_controller_rows") != 173
        or reviewed.get("generated_bsp_rows") != 173
        or reviewed.get("m1_contacts") != 80
        or reviewed.get("qualified_target_configurations") != 12
        or reviewed.get("cross_domain_contradictions_remaining") != 0
        or reviewed.get("open_analytical_findings") != 0
        or reviewed.get("physical_residuals_transferred") != 51
        or reviewed.get("failed_checks") != 0
        or not all(result.get("checks", {}).values())
        or result.get("next", {}).get("marker") != "H5.0.3-R1"
    ):
        raise ValueError("invalid immutable H4-R2.3 acceptance snapshot")
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
            raise SystemExit("stale H4-R2 acceptance artifacts: " + ", ".join(stale))
    print("ok: H4-R2 reviewed; 0 contradictions, 51 owned physical residuals, current H5.0.3-R1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
