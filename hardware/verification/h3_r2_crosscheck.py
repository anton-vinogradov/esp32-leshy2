#!/usr/bin/env python3
"""Close H3-R2 with one hash-bound cross-check and physical residual register."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h3_r2_current_scope import apply_scope, admits_current, scope_notice


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
CURRENT_POWER_INPUTS = {
    "H3-R2.1/rail-margins": "H3-R2-rail-margins", "H3-R2.1/source-margins": "H3-R2-source-margins",
    "H3-R2.1/result": "H3-R2-dc-source-crosscheck", "H3-R2.2/sequences": "H3-R2-transition-sequences",
    "H3-R2.2/handover": "H3-R2-handover", "H3-R2.2/inrush-watchdog": "H3-R2-inrush-watchdog",
    "H3-R2.2/result": "H3-R2-transition-result", "H3-R2.3/result": "H3-R2-analog-corners",
    "H3-R2.4/result": "H3-R2-digital-interfaces", "H3-R2.5/result": "H3-R2-rf-coexistence",
    "H3-R2.6/result": "H3-R2-thermal-fault",
}


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
    match = re.match(r"^\s*(H5|H6|H8)(?=\b|:)", text, flags=re.IGNORECASE)
    if match:
        return [match.group(1).upper()]
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
        ("H3-R2.0", "Inputs, provenance and methods", "2 projects · 22 sheets · 1,208 schematic instances · 788 nets · 250 exact groups · 9 methods"),
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
            "provisional_numerical_errors": len(rows[name].get("provisional_numerical_errors", rows[name].get("errors", []))),
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
    allowed_statuses = {"pass", "review_required",
        "reviewed_audio_analog_corners_after_four_source_corrections",
        "reviewed_ir_corners_after_four_source_corrections",
        "reviewed_battery_sensing_thermistors_and_analog_fault_thresholds"}
    checks = {
        "plan_is_reviewed_at_h3_r2_7": plan["status"] == "reviewed" and plan["current_substep"] is None and workstreams["H3-R2.7"] == "reviewed",
        "all_seven_workstreams_are_reviewed": all(workstreams[f"H3-R2.{index}"] == "reviewed" for index in range(1, 8)),
        "all_twenty_current_artifacts_exist": len(artifact_rows) == 20,
        "all_artifact_statuses_are_known_diagnostics": all(row["status"] in allowed_statuses for row in artifact_rows),
        "all_provisional_numerical_error_lists_are_empty": all(row["provisional_numerical_errors"] == 0 for row in artifact_rows),
        "all_recorded_source_hashes_match": bool(hash_checks) and all(row["matches"] for row in hash_checks),
        "input_freeze_covers_the_exact_r2_h2_boundary": rows["H3-R2.0/input-freeze"]["accepted_hardware_input"] == "H2-R2.1.5" and rows["H3-R2.0/input-freeze"]["summary"]["projects"] == 2,
        "all_250_component_groups_have_provenance": rows["H3-R2.0/parameter-provenance"]["summary"]["owned_component_groups"] == 250,
        "all_methods_and_rules_are_frozen": rows["H3-R2.0/method-contract"]["summary"]["methods"] == 9 and rows["H3-R2.0/method-contract"]["summary"]["pass_fail_rules"] == 12,
        "dc_source_has_no_failed_state": rows["H3-R2.1/source-margins"]["summary"]["failed_states"] == 0,
        "all_transition_cases_pass": rows["H3-R2.2/handover"]["summary"]["passed_cases"] == 7316 and rows["H3-R2.2/handover"]["summary"]["failed_cases"] == 0,
        "analog_digital_rf_and_thermal_numerical_checks": all(rows[key].get("current_power_scope", {}).get("numerical_checks_pass") is True for key in ("H3-R2.3/result", "H3-R2.4/result", "H3-R2.5/result", "H3-R2.6/result")),
        "physical_residual_ids_and_text_are_unique": len({row["id"] for row in registry}) == len(registry) == len({row["residual"] for row in registry}),
        "every_physical_residual_is_owned_by_h5_h6_or_h8": all(row["closure_stages"] and set(row["closure_stages"]) <= {"H5", "H6", "H8"} for row in registry),
        "every_physical_residual_has_an_evidence_contract": all(set(row["evidence_contracts"]) == set(row["closure_stages"]) for row in registry),
        "firmware_work_is_not_misclassified_as_physical_evidence": len(firmware_obligations) == 1 and firmware_obligations[0]["owner"] == "F5/F6",
        "no_release_authority_is_created": not any(plan["authorization"][key] for key in ("pcb_placement_and_routing", "fabrication", "purchasing")),
    }
    failed = [name for name, passed in checks.items() if not passed]

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
            "failed_checks": len(failed),
            "open_analytical_findings": 0,
        },
        "checks": checks,
        "firmware_obligations": firmware_obligations,
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False, "final_product_claim": False},
        "next": {"marker": "H3-current-power-model-correction", "action": "correct and verify current power applicability before phase closure"},
        "errors": [],
    }
    crosscheck["errors"] = failed
    apply_scope(crosscheck, __file__, {"current_power_inputs": all(
        admits_current(rows[key], artifact) for key, artifact in CURRENT_POWER_INPUTS.items())}, numerical_ok=not failed)
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
    apply_scope(residuals, __file__, {"crosscheck_inputs": crosscheck["current_power_scope"]["status"] == "pass"})
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
            "the implemented H3 pre-layout analytical models have reproducible current evidence",
            "all recorded source hashes match and no finding remains open within those model checks",
            "each physical uncertainty in the H3 register has an H5, H6 or H8 owner and an evidence contract",
            "firmware implementation work remains explicitly separate and joins at H4-R2",
        ],
        "coverage_limit": {
            "native_physical_pin_electrical_semantics_verified": False,
            "production_gate": "H6-NATIVE-ELECTRICAL-SEMANTICS",
            "reason": "passive-pin ERC and existing analytical models do not prove rail-driver completeness or exclude output conflicts; a reviewed physical-pin type map and fresh electrical checks are required",
        },
        "acceptance_does_not_authorize": ["component purchase", "PCB placement or routing", "fabrication", "physical performance claims", "unattended-runtime claims"],
        "authorization": {"advance_to_h4_r2": True, "pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "open_findings": [],
        "pending_decisions": [],
    }

    apply_scope(acceptance, __file__, {"crosscheck_inputs": crosscheck["current_power_scope"]["status"] == "pass"})
    acceptance["result"].update(analytical_scope_complete=acceptance["current_analytical_scope_complete"],
        open_analytical_findings=len(crosscheck["errors"]), next_marker="H3-current-power-model-correction")
    acceptance["open_findings"] = list(crosscheck["errors"])
    acceptance["acceptance_meaning"] = [
        "Current analytical applicability is explicitly separate from retained provisional algebra and topology",
        "Open current power-model findings remain analytical, in addition to the existing physical evidence registry",
        "The historical H3 closure is not transferred to the unqualified current power cell",
    ]
    residual_en = f"""# Physical evidence register · H3-R2

[Русский](physical-evidence-register-r2.ru.md) · [H3 report](h3-r2-acceptance.md)

{scope_notice(residuals)}

This existing physical registry contains {len(registry)} open rows (H5: {by_stage['H5']}, H6: {by_stage['H6']}, H8: {by_stage['H8']}; multiple owners are possible). These are **not the only remaining findings**: current power-model applicability and numerical failures remain analytical and are listed separately in the H3 result. No row below is passed by regeneration.

{residual_table(registry, False)}

The registry requires no sacrificial assembled unit or drop/vibration campaign. Safe fault checks require current-limited fixtures; real cells remain within their declared limits. The exact i8080 implementation remains a separate firmware obligation.
"""
    residual_ru = f"""# Реестр физических evidence · H3-R2

[English](physical-evidence-register-r2.md) · [Отчёт H3](h3-r2-acceptance.ru.md)

{scope_notice(residuals, True)}

В существующем физическом реестре {len(registry)} открытых строк (H5: {by_stage['H5']}, H6: {by_stage['H6']}, H8: {by_stage['H8']}; владельцев может быть несколько). Это **не все оставшиеся вопросы**: применимость нынешней модели питания и численные нарушения остаются аналитическими и перечислены отдельно в итоге H3. Перегенерация не закрывает строки ниже.

{residual_table(registry, True)}

Реестр не требует расходуемого собранного образца или испытаний падением/вибрацией. Безопасная проверка faults требует ограничения тока; реальные банки остаются в своих пределах. Точная реализация i8080 — отдельное обязательство прошивки.
"""
    report_en = f"""# H3-R2 · current electrical diagnostics

[Русский](h3-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

{scope_notice(acceptance)}

This publication recomputes {len(artifact_rows)} evidence artifacts and checks {len(hash_checks)} source bindings. Source mismatches: {sum(not item['matches'] for item in hash_checks)}. Open aggregate findings: {len(crosscheck['errors'])}. Current applicability is **not** inherited from historical H3 closure.

## Current analytical work

Raw supply, protected local supply and consumer endpoints are separate. The retained MAIN model still uses parameters for a different converter, has unqualified current/protection and thermal limits, and the AON resistance is not bound to the fitted setting. Existing numerical calculations are provisional, not permission to treat these inputs as qualified. The supervisor assertion maximum and minimum hysteresis also remain unspecified.

{chr(10).join("- " + name + ": " + rows[name]['status'] for name in CURRENT_POWER_INPUTS)}

## Separate physical and firmware evidence

The [physical registry](physical-evidence-register-r2.md) retains {len(registry)} open rows with explicit owners. Those rows do not replace the analytical findings above. The F5/F6 i8080 implementation and `H6-NATIVE-ELECTRICAL-SEMANTICS` gate remain separate obligations; this report does not close them.

The next work is correction and verification of the current power model. Fresh diagnostics and matching hashes do not advance a phase or authorize hardware operation.

[Machine cross-check](../hardware/verification/generated/H3-R2-crosscheck.json)
"""
    report_ru = f"""# H3-R2 · текущая электрическая диагностика

[English](h3-r2-acceptance.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

{scope_notice(acceptance, True)}

Публикация пересчитывает {len(artifact_rows)} evidence-artifacts и проверяет {len(hash_checks)} привязок к источникам. Несовпадений хешей: {sum(not item['matches'] for item in hash_checks)}. Открытых агрегированных findings: {len(crosscheck['errors'])}. Применимость к нынешнему железу **не наследуется** из исторического закрытия H3.

## Текущая аналитическая работа

Исходное питание, питание после защиты и напряжение на потребителе разделены. Сохранённая MAIN-модель ещё использует параметры другого преобразователя, неподтверждённые токовые/защитные и тепловые пределы; сопротивление AON не привязано к установленной настройке. Существующие расчёты предварительны, а не разрешение считать эти входы подтверждёнными. Максимум времени утверждения reset и минимум гистерезиса supervisor также не заданы.

{chr(10).join("- " + name + ": " + rows[name]['status'] for name in CURRENT_POWER_INPUTS)}

## Отдельные физические evidence и прошивка

[Физический реестр](physical-evidence-register-r2.ru.md) сохраняет {len(registry)} открытых строк с явными владельцами. Они не заменяют аналитические вопросы выше. Реализация i8080 F5/F6 и проверка `H6-NATIVE-ELECTRICAL-SEMANTICS` остаются отдельными обязательствами; этот отчёт их не закрывает.

Следующая работа — исправление и проверка нынешней модели питания. Свежие диагностика и хеши не означают переход фазы или разрешение включать железо.

[Машинный cross-check](../hardware/verification/generated/H3-R2-crosscheck.json)
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
    print(f"H3-R2 current diagnostic {acceptance['status']}; {acceptance['result']['open_analytical_findings']} open analytical findings; {acceptance['result']['physical_residuals']} physical residuals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
