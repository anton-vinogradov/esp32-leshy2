#!/usr/bin/env python3
"""Publish the H2.7.5 physical/net/HW-to-FW reconciliation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_review_canonical_inventories import ECAD, REPO, sha256


GENERATED = ECAD / "generated"
OUTPUT = GENERATED / "H2-REV75-hwfw-consolidated.json"
DOC_EN = REPO / "docs/hwfw-reconciliation.md"
DOC_RU = REPO / "docs/hwfw-reconciliation.ru.md"
INPUTS = (
    ("H2.7.1", GENERATED / "H2-REV71-canonical-inventories.json"),
    ("H2.7.2", GENERATED / "H2-REV72-physical-contacts.json"),
    ("H2.7.3", GENERATED / "H2-REV73-named-nets-m1.json"),
    ("H2.7.4", GENERATED / "H2-REV74-firmware-contract.json"),
)


def render_doc(manifest: dict, russian: bool) -> str:
    c = manifest["closure"]
    if russian:
        title = "# Сквозная сверка железа и прошивки Leshy2"
        nav = "[English](hwfw-reconciliation.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)"
        intro = "H2.7 связывает физический H1, production ECAD и вход firmware F2 одним проверяемым контрактом."
        headers = "| Граница | Проверено | Результат |\n|---|---:|---|"
        rows = [
            f"| H1 ↔ instance ledger ↔ symbols | {c['ledger_rows']} строк / {c['electrical_identities']} identities | 0 MPN/contact mismatches |",
            f"| root hierarchy nets | {c['root_named_nets']} | все присутствуют в native netlists |",
            f"| M1 UI ↔ RF | {c['m1_contacts']} контактов / {c['m1_unique_nets']} nets | построчно идентичны |",
            f"| architecture ↔ KiCad | {c['controller_allocations']} allocations | 0 pin/net mismatches |",
            f"| H2 export ↔ firmware F2 | {c['firmware_contacts']} MCU-контактов | семантически идентичны; firmware-копия fail-closed как historical R1; временные pins запрещены |",
        ]
        russian_corrections = {
            "H2.7.2-F01": "instance ledger называл число логических функций числом физических контактов в десяти expanded-pad/module случаях → теперь каждая строка отдельно хранит logical_contact_count и physical_pcb_contact_count, а contact_count означает реальные lands корпуса или модуля",
            "H2.7.4-F01": "PACK UART назывался PACK_SERVICE_UART_TX/RX в allocations, но PACK_ADMISSION_UART_TX/RX в KiCad, fixture pads и fixed routes → allocations и firmware F2 переведены на уже установленное каноническое имя PACK_ADMISSION_UART_TX/RX",
        }
        corrections = "## Исправленные несоответствия\n\n" + "\n".join(f"- `{row['id']}` — {russian_corrections[row['id']]}" for row in manifest["corrected_findings"])
        close = "✅ **Проведено ревью:** H2.7 закрыт, сквозных несоответствий не осталось."
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV75-hwfw-consolidated.json)."
    else:
        title = "# Leshy2 end-to-end hardware/firmware reconciliation"
        nav = "[Русский](hwfw-reconciliation.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)"
        intro = "H2.7 binds physical H1, production ECAD and the firmware F2 input into one verifiable contract."
        headers = "| Boundary | Reviewed | Result |\n|---|---:|---|"
        rows = [
            f"| H1 ↔ instance ledger ↔ symbols | {c['ledger_rows']} rows / {c['electrical_identities']} identities | 0 MPN/contact mismatches |",
            f"| root hierarchy nets | {c['root_named_nets']} | all present in native netlists |",
            f"| M1 UI ↔ RF | {c['m1_contacts']} contacts / {c['m1_unique_nets']} nets | row-for-row identical |",
            f"| architecture ↔ KiCad | {c['controller_allocations']} allocations | 0 pin/net mismatches |",
            f"| H2 export ↔ firmware F2 | {c['firmware_contacts']} MCU contacts | semantically identical; firmware copy is fail-closed as historical R1; temporary pins forbidden |",
        ]
        corrections = "## Corrected mismatches\n\n" + "\n".join(f"- `{row['id']}` — {row['finding']} → {row['correction']}" for row in manifest["corrected_findings"])
        close = "✅ **Reviewed:** H2.7 is closed with no end-to-end mismatch remaining."
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV75-hwfw-consolidated.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(rows), corrections, close, evidence)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    data = {}
    corrected = []
    subreviews = []
    for stage, path in INPUTS:
        review = json.loads(path.read_text(encoding="utf-8"))
        if review.get("stage") != stage or not str(review.get("status", "")).startswith("reviewed_") or review.get("open_findings"):
            raise ValueError(f"{path.name} is not a closed {stage} review")
        data[stage] = review
        subreviews.append({"stage": stage, "artifact": str(path.relative_to(REPO)), "status": "reviewed"})
        corrected.extend({"stage": stage, **row} for row in review.get("corrected_findings", []))
    contacts = data["H2.7.2"]["summary"]
    nets = data["H2.7.3"]["summary"]
    firmware = data["H2.7.4"]["summary"]
    manifest = {
        "schema_version": 1,
        "stage": "H2.7.5",
        "status": "reviewed_h2_7_end_to_end_reconciliation",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for _, path in INPUTS},
        "subreviews": subreviews,
        "corrected_findings": corrected,
        "closure": {
            "ledger_rows": contacts["ledger_rows"],
            "electrical_identities": contacts["reconciled_electrical_identities"],
            "root_named_nets": nets["root_named_nets"],
            "m1_contacts": nets["m1_physical_contacts"],
            "m1_unique_nets": nets["m1_unique_nets"],
            "controller_allocations": firmware["architecture_allocations"],
            "firmware_contacts": firmware["firmware_bsp_contacts"],
            "mpn_contact_net_or_firmware_mismatches": 0,
            "next_substep": "H2.8.1 — prepare the formal H2 acceptance package and deferred-gate boundary",
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
        print(f"ok: H2.7.5 reconciliation is current; {manifest['closure']['mpn_contact_net_or_firmware_mismatches']} mismatches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
