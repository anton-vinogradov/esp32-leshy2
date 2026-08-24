#!/usr/bin/env python3
"""Consolidate H2.5.1-H2.5.5 evidence and close H2.5.6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_review_power_paths import ECAD, REPO, sha256


GENERATED = ECAD / "generated"
OUTPUT_MANIFEST = GENERATED / "H2-REV56-safety-consolidated.json"
OUTPUT_DOC_EN = REPO / "docs/safety-review.md"
OUTPUT_DOC_RU = REPO / "docs/safety-review.ru.md"
INPUTS = (
    ("H2.5.1", GENERATED / "H2-REV51-power-paths.json", "power sources, admission, charging and rails"),
    ("H2.5.2", GENERATED / "H2-REV52-recovery-paths.json", "reset, boot, service and recovery"),
    ("H2.5.3", GENERATED / "H2-REV53-no-back-power.json", "no-back-power boundaries"),
    ("H2.5.4", GENERATED / "H2-REV54-quiet-state.json", "quiet state and unused-interface isolation"),
    ("H2.5.5", GENERATED / "H2-REV55-fault-kill.json", "watchdog, thermal faults and hardware shutdown"),
)


def build() -> tuple[dict[Path, str], dict]:
    reviews = []
    findings = []
    deferred = []
    for stage, path, scope in INPUTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("stage") != stage or not str(data.get("status", "")).startswith("reviewed_"):
            raise ValueError(f"{path.name} is not a closed reviewed {stage} artifact")
        if data.get("open_findings"):
            raise ValueError(f"{stage} still contains open findings")
        local_findings = data.get("corrected_findings", [])
        if not local_findings:
            raise ValueError(f"{stage} lacks explicit corrected-finding accounting")
        reviews.append({
            "stage": stage, "scope": scope, "artifact": str(path.relative_to(REPO)),
            "status": "reviewed", "corrected_finding_count": len(local_findings),
        })
        findings.extend({"stage": stage, **row} for row in local_findings)
        deferred.extend({"stage": stage, "item": item} for item in data["review_boundary"]["deferred"])

    ids = [row["id"] for row in findings]
    if len(ids) != len(set(ids)):
        raise ValueError("corrected finding ids are not unique")
    if len(findings) < len(INPUTS):
        raise ValueError(
            f"expected at least one corrected finding per reviewed substage, got {len(findings)}"
        )

    manifest = {
        "schema_version": 1,
        "stage": "H2.5.6",
        "status": "reviewed_h2_5_independent_safety_paths_closed",
        "method": "consolidation of five independently regenerated, machine-checkable complete-hierarchy review artifacts",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for _, path, _ in INPUTS},
        "subreviews": reviews,
        "corrected_findings": findings,
        "open_paper_or_ecad_findings": [],
        "deferred_measured_gates": deferred,
        "closure": {
            "result": "H2.5 reviewed",
            "meaning": "the paper architecture and complete native KiCad hierarchy agree for the selected safety-critical paths",
            "does_not_mean": "simulation, PCB layout, prototype HIL or production release is complete",
            "next_substep": "H2.6 — close native ERC and account every intentional no-connect",
        },
    }
    return {
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        OUTPUT_DOC_EN: render_doc(manifest, russian=False),
        OUTPUT_DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Итог safety-ревью Leshy2"
        nav = "[English](safety-review.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)"
        intro = "H2.5 закрыт: выбранные safety-критичные тракты совпадают с полной native KiCad-иерархией. Это ещё не заменяет симуляцию, layout и физический HIL."
        headers = "| Шаг | Область | Статус |\n|---|---|---|"
        scopes = {
            "H2.5.1": "источники, допуск, заряд и шины",
            "H2.5.2": "reset, boot, service и recovery",
            "H2.5.3": "границы no-back-power",
            "H2.5.4": "quiet state и изоляция",
            "H2.5.5": "watchdog, thermal и FAULT_KILL",
        }
        result = "## Исправленные несоответствия\n\n" + "\n".join(
            f"- `{row['id']}` — {row['finding']} → {row['correction']}" for row in manifest["corrected_findings"]
        )
        close = "## Результат H2.5.6\n\n✅ **Проведено ревью:** открытых paper/ECAD findings нет. Следующий точный шаг — H2.6, полное закрытие ERC и каждого намеренного NC."
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV56-safety-consolidated.json)."
    else:
        title = "# Leshy2 consolidated safety review"
        nav = "[Русский](safety-review.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)"
        intro = "H2.5 is closed: the selected safety-critical paths agree with the complete native KiCad hierarchy. This does not replace simulation, layout or physical HIL."
        headers = "| Step | Scope | Status |\n|---|---|---|"
        scopes = {row["stage"]: row["scope"] for row in manifest["subreviews"]}
        result = "## Corrected findings\n\n" + "\n".join(
            f"- `{row['id']}` — {row['finding']} → {row['correction']}" for row in manifest["corrected_findings"]
        )
        close = "## H2.5.6 result\n\n✅ **Reviewed:** no paper/ECAD findings remain open. The next exact step is H2.6, complete ERC closure and accounting for every intentional NC."
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV56-safety-consolidated.json)."
    rows = "\n".join(f"| `{row['stage']}` | {scopes[row['stage']]} | ✅ reviewed |" for row in manifest["subreviews"])
    return "\n\n".join((title, nav, intro, headers + "\n" + rows, result, close, evidence)) + "\n"


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
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items()
                 if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.5.6 consolidation is current; {len(manifest['corrected_findings'])} findings corrected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
