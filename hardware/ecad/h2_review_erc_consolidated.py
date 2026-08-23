#!/usr/bin/env python3
"""Publish the H2.6.4 consolidated ERC/no-connect review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_review_erc_snapshot import ECAD, REPO, sha256


GENERATED = ECAD / "generated"
OUTPUT = GENERATED / "H2-REV64-erc-consolidated.json"
DOC_EN = REPO / "docs/erc-review.md"
DOC_RU = REPO / "docs/erc-review.ru.md"
INPUTS = (
    ("H2.6.1", GENERATED / "H2-REV61-native-erc.json"),
    ("H2.6.2", GENERATED / "H2-REV62-no-connects.json"),
    ("H2.6.3", GENERATED / "H2-REV63-erc-clean.json"),
)


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Итог ERC и NC-ревью Leshy2"
        nav = "[English](erc-review.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Все NC](no-connects.ru.md)"
        intro = "H2.6 закрыт на полной четырёхпроектной KiCad-иерархии, а не на отдельных листах."
        headers = "| Проверка | Результат |\n|---|---|"
        rows = [
            "| Native ERC | 4 проекта · 0 ошибок · 0 предупреждений |",
            f"| Намеренные NC | {manifest['closure']['intentional_no_connects']} физических контактов · у каждого есть pin, marker и причина |",
            f"| Локальные символы | {manifest['closure']['generated_symbol_definitions']} сравнений вынесены из шумного KiCad-правила в точную проверку общей библиотеки |",
            "| Исключения ERC | только `lib_symbol_mismatch`; других ignored rules нет |",
        ]
        close = "✅ **Проведено ревью:** необъяснённых ERC/NC findings нет. H2.6 завершён; текущий шаг — H2.7, сквозная сверка контактов и сетей с H1, pin ledger, M1 и firmware F2."
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV64-erc-consolidated.json)."
    else:
        title = "# Leshy2 consolidated ERC and NC review"
        nav = "[Русский](erc-review.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [All NCs](no-connects.md)"
        intro = "H2.6 is closed on the complete four-project KiCad hierarchy, not isolated sheets."
        headers = "| Check | Result |\n|---|---|"
        rows = [
            "| Native ERC | 4 projects · 0 errors · 0 warnings |",
            f"| Intentional NCs | {manifest['closure']['intentional_no_connects']} physical contacts · each has a pin, marker and rationale |",
            f"| Local symbols | {manifest['closure']['generated_symbol_definitions']} comparisons moved from the noisy KiCad rule into an exact shared-library check |",
            "| ERC exclusions | only `lib_symbol_mismatch`; no other ignored rules |",
        ]
        close = "✅ **Reviewed:** no unexplained ERC/NC finding remains. H2.6 is complete; the current step is H2.7, end-to-end contact/net reconciliation against H1, the pin ledger, M1 and firmware F2."
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV64-erc-consolidated.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(rows), close, evidence)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    reviews = []
    corrected = []
    data_by_stage = {}
    for stage, path in INPUTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("stage") != stage or not str(data.get("status", "")).startswith("reviewed_") or data.get("open_findings"):
            raise ValueError(f"{path.name} is not a closed {stage} review")
        data_by_stage[stage] = data
        reviews.append({"stage": stage, "artifact": str(path.relative_to(REPO)), "status": "reviewed"})
        corrected.extend({"stage": stage, **row} for row in data.get("corrected_findings", []))
    snapshot = data_by_stage["H2.6.1"]
    nc = data_by_stage["H2.6.2"]
    clean = data_by_stage["H2.6.3"]
    if snapshot["summary"]["native_error_or_warning_count"] or clean["checks"]["native_error_or_warning_count"]:
        raise ValueError("native ERC is not clean")
    manifest = {
        "schema_version": 1,
        "stage": "H2.6.4",
        "status": "reviewed_h2_6_erc_and_no_connect_closure",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for _, path in INPUTS},
        "subreviews": reviews,
        "corrected_findings": corrected,
        "closure": {
            "projects": snapshot["summary"]["project_count"],
            "native_errors_or_warnings": 0,
            "intentional_no_connects": nc["summary"]["intentional_no_connects"],
            "generated_symbol_definitions": snapshot["summary"]["suppressed_generated_library_comparisons"],
            "missing_contacts_markers_or_rationales": 0,
            "unexplained_findings": 0,
            "next_substep": "H2.7 — reconcile schematic contacts/nets with H1, pin ledger, M1 and firmware F2",
        },
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


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
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.6.4 consolidated review is current; {manifest['closure']['unexplained_findings']} open findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
