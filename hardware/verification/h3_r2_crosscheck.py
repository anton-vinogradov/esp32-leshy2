#!/usr/bin/env python3
"""Close H3-R2 with one hash-bound cross-check and physical residual register."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "hardware/verification/h3-r2-verification-plan.json"
INPUTS = {
    "H3-R2.0/input-freeze": ROOT / "hardware/verification/generated/H3-R2-input-freeze.json",
    "H3-R2.0/parameter-provenance": ROOT / "hardware/verification/generated/H3-R2-parameter-provenance.json",
    "H3-R2.0/method-contract": ROOT / "hardware/verification/generated/H3-R2-method-contract.json",
    "H3-R2.1/power-states": ROOT / "hardware/verification/generated/H3-R2-power-state-register.json",
    "H3-R2.1/load-binding": ROOT / "hardware/verification/generated/H3-R2-load-binding.json",
    "H3-R2.1/rail-margins": ROOT / "hardware/verification/generated/H3-R2-rail-margins.json",
    "H3-R2.1/source-margins": ROOT / "hardware/verification/generated/H3-R2-source-margins.json",
    "H3-R2.1/result": ROOT / "hardware/verification/generated/H3-R2-dc-source-crosscheck.json",
    "H3-R2.2/sequences": ROOT / "hardware/verification/generated/H3-R2-transition-sequences.json",
    "H3-R2.2/handover": ROOT / "hardware/verification/generated/H3-R2-handover.json",
    "H3-R2.2/inrush-watchdog": ROOT / "hardware/verification/generated/H3-R2-inrush-watchdog.json",
    "H3-R2.2/result": ROOT / "hardware/verification/generated/H3-R2-transition-result.json",
    "H3-R2.3/audio": ROOT / "hardware/verification/generated/H3-VRF32-audio.json",
    "H3-R2.3/ir": ROOT / "hardware/verification/generated/H3-VRF33-ir.json",
    "H3-R2.3/battery": ROOT / "hardware/verification/generated/H3-VRF34-battery-analog.json",
    "H3-R2.3/airband": ROOT / "hardware/verification/generated/H3-R2-airband-corners.json",
    "H3-R2.3/result": ROOT / "hardware/verification/generated/H3-R2-analog-corners.json",
    "H3-R2.4/result": ROOT / "hardware/verification/generated/H3-R2-digital-interfaces.json",
    "H3-R2.5/result": ROOT / "hardware/verification/generated/H3-R2-rf-coexistence.json",
    "H3-R2.6/result": ROOT / "hardware/verification/generated/H3-R2-thermal-fault.json",
}
CROSSCHECK = ROOT / "hardware/verification/generated/H3-R2-crosscheck.json"
RESIDUALS = ROOT / "hardware/verification/generated/H3-R2-physical-residuals.json"
ACCEPTANCE = ROOT / "hardware/verification/generated/H3-R2-acceptance-package.json"
DOC_EN = ROOT / "docs/h3-r2-acceptance.md"
DOC_RU = ROOT / "docs/h3-r2-acceptance.ru.md"
RESIDUAL_DOC_EN = ROOT / "docs/physical-evidence-register-r2.md"
RESIDUAL_DOC_RU = ROOT / "docs/physical-evidence-register-r2.ru.md"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recorded_hashes(value: object) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and "/" in key and HEX64.fullmatch(child):
                found.append((key, child))
            else:
                found.extend(recorded_hashes(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(recorded_hashes(child))
    return found


def stages_from_prefix(text: str, default: tuple[str, ...] = ("H8",)) -> list[str]:
    prefix = text.split(":", 1)[0].upper()
    if prefix in {"H5", "H6", "H8"}:
        return [prefix]
    return list(default)


def evidence_contract(stage: str, residual: str) -> dict:
    if stage == "H5":
        return {
            "owner": "H5 exact received-part evidence",
            "artifact": "lot-identified photographs, dimensions, orientation and mating record for the exact received MPN",
            "pass_rule": f"the received item matches the selected identity and physical contract needed by: {residual}",
        }
    if stage == "H6":
        return {
            "owner": "H6 routed-design review",
            "artifact": "revision-bound placement/routing export, extracted values, DRC/solver output and reviewer sign-off",
            "pass_rule": f"the final routed geometry demonstrates this item without a waiver: {residual}",
        }
    return {
        "owner": "H8 assembled-prototype qualification",
        "artifact": "versioned non-destructive procedure, exact DUT/firmware identity, calibrated raw data and retained limit comparison",
        "pass_rule": f"the one assembled prototype passes this item at every admitted corner: {residual}",
    }


def build_residual_rows(rows: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    candidates: list[tuple[str, str, str, list[str], str]] = []

    def add(source: str, group: str, text: str, stages: list[str], classification: str = "ordinary_non_destructive") -> None:
        candidates.append((source, group, text, stages, classification))

    rails = rows["H3-R2.1/rail-margins"]
    for text in rails["physical_residuals"]:
        add("H3-R2.1", "rail-margins", text, stages_from_prefix(text))
    sources = rows["H3-R2.1/source-margins"]
    for text in sources["physical_residuals"]:
        if text.startswith("H3-R2.2"):
            continue
        add("H3-R2.1", "source-margins", text, stages_from_prefix(text))

    for key, group in (
        ("H3-R2.2/sequences", "startup-reset"),
        ("H3-R2.2/handover", "handover-brownout"),
        ("H3-R2.2/inrush-watchdog", "inrush-watchdog"),
    ):
        for text in rows[key]["physical_residuals"]:
            add("H3-R2.2", group, text, stages_from_prefix(text))

    analog = rows["H3-R2.3/result"]["residual_physical_only"]
    for group, values in analog.items():
        for value in values:
            if isinstance(value, dict):
                add("H3-R2.3", f"{group}/routed", value["h6_gate"], ["H6"])
                add("H3-R2.3", f"{group}/assembled", value["h8_gate"], ["H8"])
                continue
            stages = ["H5", "H8"] if value.startswith("verify received TSOP") else stages_from_prefix(value)
            classification = "safe_current_limited_fixture" if any(token in value.lower() for token in ("max17320", "cell simulator", "ntc fixture")) else "ordinary_non_destructive"
            add("H3-R2.3", group, value, stages, classification)

    firmware_obligations: list[dict] = []
    for row in rows["H3-R2.4/result"]["physical_residuals"]:
        owner = row["owner"]
        if owner in {"H6", "H8"}:
            add("H3-R2.4", "digital-interfaces", row["item"], [owner])
        else:
            firmware_obligations.append({
                "owner": owner,
                "obligation": row["item"],
                "handoff": "H4-R2 joined review and the owning firmware phase",
                "status": "implementation_evidence_required",
            })

    for source, key in (("H3-R2.5", "H3-R2.5/result"), ("H3-R2.6", "H3-R2.6/result")):
        for text in rows[key]["physical_residuals"]:
            add(source, "phase-result", text, stages_from_prefix(text))

    unique: list[tuple[str, str, str, list[str], str]] = []
    seen: set[str] = set()
    for row in candidates:
        if row[2] not in seen:
            seen.add(row[2])
            unique.append(row)
    registry = []
    for index, (source, group, residual, stages, classification) in enumerate(unique, start=1):
        registry.append({
            "id": f"H3-R2-PHY-{index:03d}",
            "source_workstream": source,
            "source_group": group,
            "residual": residual,
            "classification": classification,
            "closure_stages": stages,
            "evidence_contracts": {stage: evidence_contract(stage, residual) for stage in stages},
            "status": "physical_evidence_required",
        })
    return registry, firmware_obligations


def phase_table(russian: bool) -> str:
    rows = [
        ("H3-R2.0", "Inputs, provenance and methods", "2 projects · 22 sheets · 1,208 schematic instances · 789 nets · 251 exact groups · 9 methods"),
        ("H3-R2.1", "DC, rails, sources and charge", "2,266 legal states · 224 rail corners · 30.560% minimum reserve · 3.516 A maximum pack current"),
        ("H3-R2.2", "Transitions and faults", "14 ordered scenarios · 7,316 handover cases · 5 starts · 4 load steps · 10 watchdog/fault cases"),
        ("H3-R2.3", "Analog corners", "display, audio, IR, battery and Airband calculations pass; routed Airband tuning remains measured"),
        ("H3-R2.4", "Digital interfaces", "direct i8080-8 at exact 20 MHz · M1 80/80 parity · explicit USB/service ownership"),
        ("H3-R2.5", "RF and coexistence", "71 checks · 10 permanent antenna paths · 13 quiet contracts · all 3×nRF24 role/identity mixes"),
        ("H3-R2.6", "Thermal and single fault", "56 thermal profiles · 30 single faults · 25 checks · no unattended-runtime claim"),
    ]
    if russian:
        translations = {
            "Inputs, provenance and methods": "Входы, provenance и методы",
            "DC, rails, sources and charge": "DC, шины, источники и заряд",
            "Transitions and faults": "Переходы и faults",
            "Analog corners": "Аналоговые corners",
            "Digital interfaces": "Цифровые интерфейсы",
            "RF and coexistence": "RF и coexistence",
            "Thermal and single fault": "Thermal и single fault",
        }
        header = "| Workstream | Что проверено | Результат |\n|---|---|---|"
        body = [f"| `{marker}` | {translations[title]} | {result} |" for marker, title, result in rows]
    else:
        header = "| Workstream | Reviewed scope | Result |\n|---|---|---|"
        body = [f"| `{marker}` | {title} | {result} |" for marker, title, result in rows]
    return "\n".join((header, *body))


def residual_table(registry: list[dict], russian: bool) -> str:
    header = "| ID | Владелец | Источник | Остающееся физическое evidence |\n|---|---|---|---|" if russian else "| ID | Owner | Source | Remaining physical evidence |\n|---|---|---|---|"
    body = [f"| `{row['id']}` | `{'+'.join(row['closure_stages'])}` | `{row['source_workstream']}` | {row['residual']} |" for row in registry]
    return "\n".join((header, *body))


def build() -> tuple[dict[Path, str], dict]:
    plan = load(PLAN)
    rows = {name: load(path) for name, path in INPUTS.items()}
    artifact_rows = [
        {
            "workstream": name,
            "artifact": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "status": rows[name]["status"],
            "errors": len(rows[name].get("errors", [])),
        }
        for name, path in INPUTS.items()
    ]
    hash_checks = []
    for name, row in rows.items():
        for source, expected in recorded_hashes({key: row.get(key) for key in ("source_sha256", "source_hashes", "sources")}):
            path = ROOT / source
            hash_checks.append({
                "recorded_by": name,
                "source": source,
                "expected": expected,
                "actual": sha256(path) if path.is_file() else None,
                "matches": path.is_file() and sha256(path) == expected,
            })

    registry, firmware_obligations = build_residual_rows(rows)
    by_stage = {stage: sum(stage in row["closure_stages"] for row in registry) for stage in ("H5", "H6", "H8")}
    by_workstream = {stage: sum(row["source_workstream"] == stage for row in registry) for stage in ("H3-R2.1", "H3-R2.2", "H3-R2.3", "H3-R2.4", "H3-R2.5", "H3-R2.6")}
    workstreams = {row["id"]: row["status"] for row in plan["substeps"]}
    allowed_statuses = {"pass"} | {row["status"] for row in artifact_rows if row["status"].startswith("reviewed")}
    checks = {
        "plan_is_reviewed_at_h3_r2_7": plan["status"] == "reviewed" and plan["current_substep"] is None and workstreams["H3-R2.7"] == "reviewed",
        "all_seven_workstreams_are_reviewed": all(workstreams[f"H3-R2.{index}"] == "reviewed" for index in range(1, 8)),
        "all_twenty_current_artifacts_exist": len(artifact_rows) == 20,
        "all_artifact_statuses_pass_or_reviewed": all(row["status"] in allowed_statuses for row in artifact_rows),
        "all_artifact_error_lists_are_empty": all(row["errors"] == 0 for row in artifact_rows),
        "all_recorded_source_hashes_match": bool(hash_checks) and all(row["matches"] for row in hash_checks),
        "input_freeze_covers_the_exact_r2_h2_boundary": rows["H3-R2.0/input-freeze"]["accepted_hardware_input"] == "H2-R2.1.5" and rows["H3-R2.0/input-freeze"]["summary"]["projects"] == 2,
        "all_251_component_groups_have_provenance": rows["H3-R2.0/parameter-provenance"]["summary"]["owned_component_groups"] == 251,
        "all_methods_and_rules_are_frozen": rows["H3-R2.0/method-contract"]["summary"]["methods"] == 9 and rows["H3-R2.0/method-contract"]["summary"]["pass_fail_rules"] == 12,
        "dc_source_has_no_failed_state": rows["H3-R2.1/source-margins"]["summary"]["failed_states"] == 0,
        "all_transition_cases_pass": rows["H3-R2.2/handover"]["summary"]["passed_cases"] == 7316 and rows["H3-R2.2/handover"]["summary"]["failed_cases"] == 0,
        "analog_digital_rf_and_thermal_results_pass": all(rows[key]["status"] == "pass" for key in ("H3-R2.3/result", "H3-R2.4/result", "H3-R2.5/result", "H3-R2.6/result")),
        "physical_residual_ids_and_text_are_unique": len({row["id"] for row in registry}) == len(registry) == len({row["residual"] for row in registry}),
        "every_physical_residual_is_owned_by_h5_h6_or_h8": all(row["closure_stages"] and set(row["closure_stages"]) <= {"H5", "H6", "H8"} for row in registry),
        "every_physical_residual_has_an_evidence_contract": all(set(row["evidence_contracts"]) == set(row["closure_stages"]) for row in registry),
        "firmware_work_is_not_misclassified_as_physical_evidence": len(firmware_obligations) == 1 and firmware_obligations[0]["owner"] == "F5/F6",
        "no_release_authority_is_created": not any(plan["authorization"][key] for key in ("pcb_placement_and_routing", "fabrication", "purchasing")),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        mismatches = [f"{row['recorded_by']} -> {row['source']}" for row in hash_checks if not row["matches"]]
        suffix = f"; hash mismatches: {', '.join(mismatches)}" if mismatches else ""
        raise ValueError("H3-R2.7 cross-check failed: " + ", ".join(failed) + suffix)

    crosscheck = {
        "schema_version": 1,
        "artifact": "H3-R2-crosscheck",
        "marker": "H3-R2.7",
        "status": "reviewed",
        "source_sha256": {str(PLAN.relative_to(ROOT)): sha256(PLAN), **{str(path.relative_to(ROOT)): sha256(path) for path in INPUTS.values()}},
        "artifact_results": artifact_rows,
        "recorded_source_hash_checks": hash_checks,
        "summary": {
            "current_artifacts": len(artifact_rows),
            "recorded_source_hashes_checked": len(hash_checks),
            "hash_mismatches": sum(not row["matches"] for row in hash_checks),
            "checks": len(checks),
            "failed_checks": 0,
            "open_analytical_findings": 0,
        },
        "checks": checks,
        "firmware_obligations": firmware_obligations,
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False, "final_product_claim": False},
        "next": {"marker": "H4-R2.0.1", "action": "freeze the current mechanics, ECAD, H3 and firmware-R2 join inputs"},
        "errors": [],
    }
    residuals = {
        "schema_version": 1,
        "artifact": "H3-R2-physical-residuals",
        "marker": "H3-R2.7",
        "status": "reviewed_physical_only_residual_register",
        "source_sha256": {str(CROSSCHECK.relative_to(ROOT)): hashlib.sha256((json.dumps(crosscheck, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()},
        "summary": {"physical_evidence_rows": len(registry), "by_closure_stage": by_stage, "by_source_workstream": by_workstream, "unassigned": 0, "analytically_closed_by_h3": 0},
        "safety_boundary": {
            "one_prototype": "all H8 work targets the one assembled prototype; no sacrificial assembled unit is required",
            "non_destructive": "ordinary measurements, controlled operation, inspection and 24/48-hour soak; no drop, vibration or arbitrary cycle-count campaign",
            "fault_injection": "battery, NTC and destructive-state equivalents use current-limited simulators or emulators; real cells stay inside exact MPN limits and MAX17320 update endurance is not deliberately exhausted",
            "forbidden": "irreversible fuse/key burns, intentional real-cell abuse and claims of physical completion before the evidence exists",
        },
        "registry": registry,
        "firmware_obligations": firmware_obligations,
        "authorization": {"physical_evidence_complete": False, "fabrication": False, "purchasing": False},
    }
    acceptance = {
        "schema_version": 1,
        "artifact": "H3-R2-acceptance-package",
        "marker": "H3-R2.7",
        "stage": "H3",
        "baseline": "R2",
        "status": "reviewed",
        "source_sha256": {str(CROSSCHECK.relative_to(ROOT)): hashlib.sha256((json.dumps(crosscheck, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest(), str(RESIDUALS.relative_to(ROOT)): hashlib.sha256((json.dumps(residuals, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()},
        "result": {
            "analytical_scope_complete": True,
            "open_analytical_findings": 0,
            "physical_residuals": len(registry),
            "physical_residuals_owned": True,
            "firmware_obligations": len(firmware_obligations),
            "next_marker": "H4-R2.0.1",
        },
        "acceptance_meaning": [
            "every R2 electrical claim checkable before PCB placement has reproducible current evidence",
            "all recorded source hashes match and no analytical finding remains open",
            "every remaining physical uncertainty has an H5, H6 or H8 owner and an evidence contract",
            "firmware implementation work remains explicitly separate and joins at H4-R2",
        ],
        "acceptance_does_not_authorize": ["component purchase", "PCB placement or routing", "fabrication", "physical performance claims", "unattended-runtime claims"],
        "authorization": {"advance_to_h4_r2": True, "pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "open_findings": [],
        "pending_decisions": [],
    }

    residual_en = f"""# Physical evidence register · H3-R2

[Русский](physical-evidence-register-r2.ru.md) · [H3 report](h3-r2-acceptance.md) · [Roadmap](roadmap.md)

H3 leaves `{len(registry)}` physical-only evidence rows: `{by_stage['H5']}` involve H5 received-part evidence, `{by_stage['H6']}` involve H6 routed-design evidence and `{by_stage['H8']}` involve H8 measurements on the one assembled prototype. A row may intentionally have more than one owner when received identity and assembled behavior are distinct gates.

Nothing below is called passed. The registry requires no sacrificial assembled unit, drop test, vibration campaign or arbitrary connector-cycle campaign. Safe electrical faults use current-limited fixtures or emulators; real cells and the one MAX17320 remain inside their declared limits.

{residual_table(registry, False)}

One separate firmware obligation is intentionally not mislabelled as physical evidence: F5/F6 must instantiate and exercise the exact locked i8080 configuration. H4-R2 joins that obligation with the reviewed hardware boundary.

[Machine register](../hardware/verification/generated/H3-R2-physical-residuals.json).
"""
    residual_ru = f"""# Реестр физических evidence · H3-R2

[English](physical-evidence-register-r2.md) · [Отчёт H3](h3-r2-acceptance.ru.md) · [Роадмап](roadmap.ru.md)

После H3 остаётся `{len(registry)}` physical-only строк evidence: `{by_stage['H5']}` затрагивают проверку полученных деталей H5, `{by_stage['H6']}` — evidence разведённой платы H6, `{by_stage['H8']}` — измерения единственного собранного прототипа H8. У строки может быть несколько владельцев, когда identity полученной детали и поведение в сборке являются разными gates.

Ни один пункт ниже не назван пройденным. Реестр не требует расходуемого собранного устройства, drop-test, vibration campaign или произвольного числа циклов разъёмов. Безопасные электрические faults задаются current-limited fixture или emulator; реальные банки и единственный MAX17320 остаются внутри заявленных пределов.

{residual_table(registry, True)}

Одно отдельное firmware-обязательство намеренно не названо физическим evidence: F5/F6 должны создать и проверить точную зафиксированную конфигурацию i8080. H4-R2 объединит его с проведённой аппаратной границей.

[Машинный реестр](../hardware/verification/generated/H3-R2-physical-residuals.json).
"""
    report_en = f"""# H3-R2 result · virtual electrical verification

[Русский](h3-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Physical evidence register](physical-evidence-register-r2.md)

`H3-R2.7` closes the global H3 phase for the current R2 hardware. All `{len(artifact_rows)}` current evidence artifacts and `{len(hash_checks)}` recorded source hashes cross-check with zero mismatch and zero open analytical finding.

{phase_table(False)}

## What is complete

- Every electrical claim calculable before layout has a reproducible result on the exact H1-R2.38 / H2-R2.1.5 boundary.
- All legal power states, transitions, analog corners, digital interfaces, permanent RF paths, thermal profiles and single-fault cases pass their frozen paper rules.
- Every correction is already present in the current source and all dependent evidence has been regenerated.

## What remains physical

The [physical evidence register](physical-evidence-register-r2.md) contains `{len(registry)}` still-open rows with explicit H5/H6/H8 owners and pass rules. This is expected: routed impedance/parasitics, received-part identity and measurements on the one assembled prototype cannot be honestly closed on paper. The separate F5/F6 i8080 implementation obligation remains firmware work, not a disguised physical residual.

## Boundary and next stage

H3 approval does **not** authorize purchasing, PCB placement/routing, fabrication, final RF/thermal performance or unattended-runtime claims. The exact next marker is `H4-R2.0.1`: freeze and join the current mechanics, ECAD, H3 result and firmware-R2 evidence before H5.

[Machine cross-check](../hardware/verification/generated/H3-R2-crosscheck.json) · [Machine acceptance package](../hardware/verification/generated/H3-R2-acceptance-package.json)
"""
    report_ru = f"""# Итог H3-R2 · виртуальная электрическая проверка

[English](h3-r2-acceptance.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Реестр физических evidence](physical-evidence-register-r2.ru.md)

`H3-R2.7` закрывает глобальную фазу H3 для текущего железа R2. Все `{len(artifact_rows)}` актуальных evidence-artifacts и `{len(hash_checks)}` записанных source hashes сведены без единого mismatch и без открытого аналитического finding.

{phase_table(True)}

## Что завершено

- Каждое электрическое утверждение, рассчитываемое до разводки, имеет воспроизводимый результат на точной границе H1-R2.38 / H2-R2.1.5.
- Все разрешённые состояния питания, переходы, analog corners, цифровые интерфейсы, постоянные RF-тракты, thermal-профили и single-fault cases проходят зафиксированные бумажные правила.
- Все найденные исправления уже внесены в текущие источники, а зависимое evidence регенерировано.

## Что остаётся физическим

[Реестр физических evidence](physical-evidence-register-r2.ru.md) содержит `{len(registry)}` ещё открытых строк с явными владельцами и pass rules H5/H6/H8. Это нормально: routed impedance/parasitics, identity полученных деталей и измерения единственного собранного прототипа нельзя честно закрыть на бумаге. Отдельное обязательство F5/F6 по реализации i8080 остаётся работой прошивки, а не замаскированным физическим остатком.

## Граница и следующий этап

Проведённое H3 не разрешает закупку, PCB placement/routing, печать, заявления о конечных RF/thermal характеристиках или автономной работе. Точный следующий маркер — `H4-R2.0.1`: зафиксировать и объединить текущие mechanics, ECAD, итог H3 и firmware-R2 evidence перед H5.

[Машинный cross-check](../hardware/verification/generated/H3-R2-crosscheck.json) · [Машинный пакет приёмки](../hardware/verification/generated/H3-R2-acceptance-package.json)
"""
    outputs = {
        CROSSCHECK: json.dumps(crosscheck, ensure_ascii=False, indent=2) + "\n",
        RESIDUALS: json.dumps(residuals, ensure_ascii=False, indent=2) + "\n",
        ACCEPTANCE: json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: report_en,
        DOC_RU: report_ru,
        RESIDUAL_DOC_EN: residual_en,
        RESIDUAL_DOC_RU: residual_ru,
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
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H3-R2.7 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2 reviewed; {acceptance['result']['physical_residuals']} owned physical residuals, next H4-R2.0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
