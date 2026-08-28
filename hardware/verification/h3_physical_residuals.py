#!/usr/bin/env python3
"""Publish every physical-only residual from the six reviewed H3 phases."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
INPUTS = {
    "H3.1": REPO / "hardware/verification/generated/H3-VRF14-dc-consolidation.json",
    "H3.2": REPO / "hardware/verification/generated/H3-VRF25-transition-consolidation.json",
    "H3.3": REPO / "hardware/verification/generated/H3-VRF35-analog-consolidation.json",
    "H3.4": REPO / "hardware/verification/generated/H3-VRF44-digital-consolidation.json",
    "H3.5": REPO / "hardware/verification/generated/H3-VRF54-rf-consolidation.json",
    "H3.6": REPO / "hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json",
}
CROSSCHECK_PATH = REPO / "hardware/verification/generated/H3-VRF71-crosscheck.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF72-physical-residuals.json"
DOC_EN = REPO / "docs/physical-evidence-register.md"
DOC_RU = REPO / "docs/physical-evidence-register.ru.md"

AM_LW_CAPACITANCE_RESIDUAL = (
    "measure RX-AM/LW total capacitance <=19.500 pF external to the Si4732 "
    "input with the received SMA, PCB and exact pod"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(phase: str, row: dict) -> list[tuple[str, str]]:
    if phase == "H3.3":
        return [(group, text) for group, values in row["physical_hil_residuals"].items() for text in values]
    if phase == "H3.4":
        return [(group, text) for group, values in row["physical_hil_residuals"].items() for text in values]
    return [("phase", text) for text in row["residual_physical_only"]]


def assigned_stages(text: str) -> list[str]:
    normalized = text.upper()
    if normalized.startswith("H5:"):
        return ["H5"]
    if normalized.startswith("H6:"):
        return ["H6"]
    if normalized.startswith("H8:"):
        return ["H8"]
    lower = text.lower()
    stages: set[str] = set()
    if text == AM_LW_CAPACITANCE_RESIDUAL:
        return ["H5", "H6", "H8"]
    if any(token in lower for token in ("received ", "received-lot", "specimen", "mating/retention", "material/plating", "identity/cmd6")):
        stages.add("H5")
    if any(token in lower for token in ("field-solve", "routed path", "fabricator stack-up", "no drc", "impedance coupon", "copper, placement", "extract am/lw")):
        stages.add("H6")
    if "h6/h8" in lower:
        stages.update(("H6", "H8"))
    physical_verbs = ("measure", "capture", "inject", "qualify", "scope", "run ", "exercise", "verify", "confirm", "prove", "replay", "calibrate", "thermally ramp", "program ", "fault-inject", "derate", "inspect")
    if any(token in lower for token in physical_verbs) and not (stages == {"H6"} and any(token in lower for token in ("routed path", "no drc", "field-solve"))):
        stages.add("H8")
    if not stages:
        stages.add("H8")
    return sorted(stages)


def test_class(text: str) -> str:
    lower = text.lower()
    if any(
        token in lower
        for token in (
            "drop test",
            "drop profile",
            "drop qualification",
            "drop inspection",
            "mechanical endurance",
            "mating-cycle endurance",
            "insertion/removal endurance",
        )
    ):
        return "potentially_damaging_dvt"
    if any(token in lower for token in ("max17320", "cell simulator", "ntc fixture")):
        return "safe_fault_injection"
    return "ordinary_qualification"


def evidence_contract(stage: str, text: str, classification: str) -> dict:
    if text == AM_LW_CAPACITANCE_RESIDUAL and stage == "H5":
        return {
            "owner": "H5 received-component evidence",
            "required_artifact": "lot-identified photographs plus dimensional/mating records for the exact received edge SMA and controlled pod constituents",
            "pass_rule": "the received SMA and every controlled pod constituent match their selected identities and physical envelopes; H5 does not claim total assembled-path capacitance",
        }
    if text == AM_LW_CAPACITANCE_RESIDUAL and stage == "H6":
        return {
            "owner": "H6 PCB placement/routing review",
            "required_artifact": "final stack-up, routed AM/LW geometry, extracted parasitic-capacitance budget and reviewer sign-off tied to the production PCB revision",
            "pass_rule": "the routed geometry preserves a <=19.500 pF external-AMI budget without waiver; the final populated-path measurement remains assigned to H8",
        }
    if stage == "H5":
        return {
            "owner": "H5 received-component evidence",
            "required_artifact": "lot-identified photographs, dimensional/mating records and raw measurement file tied to the exact received MPN",
            "pass_rule": f"the received specimen directly demonstrates this item: {text}; a mismatch reopens the owning H1/H2/H3 result",
        }
    if stage == "H6":
        return {
            "owner": "H6 PCB placement/routing review",
            "required_artifact": "final stack-up plus placement/routing export, solver/DRC output and reviewer sign-off tied to the production PCB revision",
            "pass_rule": f"the final routed design demonstrates this item with no waived contradiction: {text}; otherwise the upstream design reopens before fabrication",
        }
    if classification == "potentially_damaging_dvt":
        return {
            "owner": "H8 potentially damaging DVT qualification",
            "required_artifact": "versioned procedure, dedicated-prototype identity, calibrated-instrument raw data, pre/post inspection, computed limit comparison and retained pass/fail log",
            "pass_rule": f"a dedicated prototype passes this potentially damaging DVT case: {text}; no production-intent or sole bring-up unit is consumed, and any failure reopens the owning result",
        }
    if classification == "safe_fault_injection":
        return {
            "owner": "H8 safe fault-injection qualification",
            "required_artifact": "versioned HIL/emulator/fixture procedure, current-limited fixture identity, exact DUT/firmware identity, raw readback or waveform data and retained pass/fail log",
            "pass_rule": f"the safe device/fixture path demonstrates this case without exhausting NVM or abusing real cells outside their exact MPN limits: {text}; any failure reopens the owning result",
        }
    return {
        "owner": "H8 physical qualification",
        "required_artifact": "versioned HIL procedure, calibrated-instrument raw data, exact DUT/firmware identity, computed limit comparison and retained pass/fail log",
        "pass_rule": f"the populated device passes this measured or injected case at every admitted corner: {text}; any failure reopens the owning result and blocks release",
    }


def build() -> tuple[dict[Path, str], dict]:
    phases = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    crosscheck = json.loads(CROSSCHECK_PATH.read_text(encoding="utf-8"))
    raw = [(phase, group, text) for phase, row in phases.items() for group, text in flatten(phase, row)]
    resolved_internal = [
        {"source_phase": phase, "text": text, "resolved_by": text.split()[0]}
        for phase, _group, text in raw
        if text.startswith(("H3.2 ", "H3.6 "))
    ]
    unresolved = [(phase, group, text) for phase, group, text in raw if not text.startswith(("H3.2 ", "H3.6 "))]

    registry = []
    for index, (phase, group, text) in enumerate(unresolved, start=1):
        stages = assigned_stages(text)
        classification = test_class(text)
        registry.append({
            "id": f"H3-PHY-{index:03d}",
            "source_phase": phase,
            "source_artifact": str(INPUTS[phase].relative_to(REPO)),
            "source_group": group,
            "residual": text,
            "test_class": classification,
            "closure_stages": stages,
            "evidence_contracts": {stage: evidence_contract(stage, text, classification) for stage in stages},
            "status": "physical_evidence_required",
        })

    by_stage = {stage: sum(stage in row["closure_stages"] for row in registry) for stage in ("H5", "H6", "H8")}
    by_phase = {phase: sum(row["source_phase"] == phase for row in registry) for phase in INPUTS}
    checks = {
        "all_six_phase_consolidations_are_reviewed": all(row["review_summary"].get("status", row["review_summary"].get("phase_status")) == "reviewed" for row in phases.values()),
        "h3_7_1_crosscheck_is_clean": crosscheck["review_summary"]["status"] == "reviewed" and crosscheck["summary"]["missing_joins"] == 0 and crosscheck["summary"]["hash_mismatches"] == 0,
        "raw_consolidated_residual_count_is_88": len(raw) == 88,
        "three_internal_h3_dependencies_are_already_resolved": len(resolved_internal) == 3 and {row["resolved_by"] for row in resolved_internal} == {"H3.2", "H3.6"},
        "all_85_remaining_physical_residuals_are_published": len(registry) == 85,
        "residual_ids_are_unique": len({row["id"] for row in registry}) == len(registry),
        "residual_texts_are_unique": len({row["residual"] for row in registry}) == len(registry),
        "every_residual_has_exact_source": all(row["source_artifact"] and row["source_phase"] in INPUTS for row in registry),
        "every_residual_is_assigned_to_h5_h6_or_h8": all(row["closure_stages"] and set(row["closure_stages"]) <= {"H5", "H6", "H8"} for row in registry),
        "every_residual_has_owner_artifact_and_pass_rule": all(all(contract["owner"] and contract["required_artifact"] and contract["pass_rule"] for contract in row["evidence_contracts"].values()) for row in registry),
        "every_phase_retains_at_least_one_physical_residual": all(by_phase.values()),
        "no_internal_h3_dependency_remains_open": not any(row["residual"].startswith("H3.") for row in registry),
        "registry_does_not_claim_physical_completion": all(row["status"] == "physical_evidence_required" for row in registry),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.7.2 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.7.2",
        "status": "reviewed_complete_physical_only_residual_register",
        "method": "flatten the physical-only output of every H3 phase consolidation, remove only H3-internal dependencies already closed, preserve exact provenance and assign an evidence owner plus pass rule",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (*INPUTS.values(), CROSSCHECK_PATH)},
        "summary": {
            "raw_consolidated_rows": len(raw),
            "resolved_h3_internal_rows": len(resolved_internal),
            "physical_evidence_rows": len(registry),
            "by_closure_stage": by_stage,
            "by_source_phase": by_phase,
            "unassigned": 0,
            "analytically_closed_by_h3": 0,
        },
        "verification_safety_boundary": {
            "safe_fault_injection": "MAX17320 exhaustion/failed-copy and pack/NTC electrical faults use an emulator or current-limited fixture; real cells stay inside exact MPN voltage, current and temperature limits",
            "potentially_damaging_dvt": "mechanical drop and connector/holder cycle qualification runs only on dedicated prototypes that may be consumed or damaged",
            "forbidden": "irreversible locks, key/security-fuse burns and intentional real-cell abuse outside exact MPN limits",
        },
        "resolved_h3_internal": resolved_internal,
        "registry": registry,
        "checks": checks,
        "open_findings": [],
        "pending_decisions": [],
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.7.3", "action": "prepare the formal H3 acceptance package without claiming physical qualification"},
    }

    def table(language: str) -> str:
        if language == "ru":
            header = "| ID | Этап | Источник | Требуемое физическое evidence |\n|---|---|---|---|"
        else:
            header = "| ID | Gate | Source | Required physical evidence |\n|---|---|---|---|"
        rows = [f"| `{row['id']}` | `{'+'.join(row['closure_stages'])}` | `{row['source_phase']}` | {row['residual']} |" for row in registry]
        return "\n".join((header, *rows))

    en = f"""# Physical evidence register · historical R1

H3.7.2 is closed. The six H3 phase consolidations contain 88 residual rows: three were H3-internal dependencies already closed by H3.2/H3.6, and all remaining `{len(registry)}` are published below. `{by_stage['H5']}` belong to H5 received-part evidence, `{by_stage['H6']}` to H6 final placement/routing evidence and `{by_stage['H8']}` to H8 populated-device qualification. None is silently called analytically complete.

Each machine row also carries its exact source artifact, responsible gate, required artifact and pass rule. A mismatch reopens the owning result rather than becoming a layout or test waiver. This register does not authorize purchase, layout or fabrication. The historical R1 progression marker is `H3.7.3`.

Safe fault injection and potentially damaging qualification are separate. MAX17320 exhaustion/failed-copy and pack/NTC electrical faults use an emulator or current-limited fixture; real cells remain inside their exact MPN voltage, current and temperature limits. Mechanical drop and connector/holder cycle qualification runs only on dedicated DVT prototypes that may be consumed. A 24/48-hour powered endurance run is ordinary non-destructive qualification. Irreversible locks, key/security-fuse burns and intentional real-cell abuse remain forbidden.

{table('en')}

Machine evidence: [`H3-VRF72-physical-residuals.json`](../hardware/verification/generated/H3-VRF72-physical-residuals.json).
"""
    ru = f"""# Реестр физических evidence · historical R1

H3.7.2 закрыт. В сведениях шести фаз H3 было 88 residual-строк: три являлись внутренними зависимостями H3, уже закрытыми H3.2/H3.6, а все оставшиеся `{len(registry)}` опубликованы ниже. `{by_stage['H5']}` назначены H5 received-part evidence, `{by_stage['H6']}` — H6 final placement/routing evidence, `{by_stage['H8']}` — H8 qualification собранного устройства. Ни одна не названа аналитически закрытой.

Каждая машинная строка содержит точный исходный artifact, ответственный gate, обязательный artifact и pass rule. Несоответствие повторно открывает исходный результат, а не превращается в waiver разводки или теста. Реестр не разрешает закупку, layout или печать. Исторический маркер прогресса R1 — `H3.7.3`.

Безопасный fault injection отделён от потенциально повреждающей qualification. Исчерпание/failed-copy MAX17320 и электрические faults pack/NTC задаются emulator или current-limited fixture; реальные банки остаются внутри ограничений точного MPN по напряжению, току и температуре. Механические drop- и cycle-тесты разъёмов/держателя выполняются только на выделенных DVT-прототипах, которые могут быть повреждены. 24/48-часовой прогон под питанием — обычная неразрушающая qualification. Необратимые locks, прожиг ключей/security-fuse и намеренное издевательство над реальными банками запрещены.

{table('ru')}

Машинное evidence: [`H3-VRF72-physical-residuals.json`](../hardware/verification/generated/H3-VRF72-physical-residuals.json).
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
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H3.7.2 artifacts: " + ", ".join(stale))
    print(f"ok: H3.7.2 reviewed; {manifest['summary']['physical_evidence_rows']} physical rows, next H3.7.3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
