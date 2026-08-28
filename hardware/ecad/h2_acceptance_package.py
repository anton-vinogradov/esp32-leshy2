#!/usr/bin/env python3
"""Publish the H2 acceptance boundary and the explicit project-owner decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_review_canonical_inventories import ECAD, REPO, sha256


GENERATED = ECAD / "generated"
OUTPUT = GENERATED / "H2-REV81-acceptance-package.json"
DOC_EN = REPO / "docs/h2-acceptance.md"
DOC_RU = REPO / "docs/h2-acceptance.ru.md"
INPUTS = (
    GENERATED / "H2-REV56-safety-consolidated.json",
    GENERATED / "H2-REV64-erc-consolidated.json",
    GENERATED / "H2-REV75-hwfw-consolidated.json",
)
INVENTORY_PATH = GENERATED / "H2-REV71-canonical-inventories.json"
CONTACTS_PATH = GENERATED / "H2-REV72-physical-contacts.json"
NETS_PATH = GENERATED / "H2-REV73-named-nets-m1.json"
NO_CONNECTS_PATH = GENERATED / "H2-REV62-no-connects.json"
PLAN = ECAD / "h2-schematic-plan.json"


DEFERRED = [
    {"gate": "H3", "scope": "worst-case DC, startup/shutdown, handover, fault, transient, digital timing and pre-layout RF simulation"},
    {"gate": "firmware F3", "scope": "target skeleton builds, size/rollback checks and available emulator execution before fabrication"},
    {"gate": "H5", "scope": "received-part dimensional, drawing, lifecycle, connector and land-fit evidence"},
    {"gate": "H6", "scope": "PCB placement, stack-up, impedance, copper, thermal layout and complete DRC"},
    {"gate": "H8", "scope": "prototype bring-up, HIL, RF coexistence, power/fault injection, thermals and long-duration operation"},
]


def render_doc(manifest: dict, final_counts: dict, russian: bool) -> str:
    if russian:
        title = "# Исторический пакет приёмки production ECAD H2 · R1"
        nav = "[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)"
        intro = "Этот принятый пакет сохранён как воспроизводимое evidence прежней одно-RP архитектуры R1. Он не является текущей R2-архитектурой и не разрешает R2 KiCad, закупку или печать."
        done_h = "## Что завершено"
        done = [
            "четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap",
            "независимое power/recovery/isolation/quiet-state/fault-shutdown ревью",
            f"нулевой native ERC и {final_counts['intentional_no_connects']} физически сопоставленных намеренных NC",
            f"{final_counts['ledger_rows']:,} ledger-строк, {final_counts['reconciled_electrical_identities']:,} сопоставленных электрических identities, {final_counts['root_named_nets']} root nets и {final_counts['m1_physical_contacts']} M1 contacts сверены".replace(",", " "),
            "130 controller allocations совпадают с KiCad; 125 MCU-контактов семантически идентичны в firmware F2, а импорт помечен fail-closed historical R1",
            "два независимых SA818S-V/U тракта имеют собственные SMA и TX evidence; one-hot selector не расходует новый MCU или M1 contact",
        ]
        defer_h = "## Что сознательно остаётся за границей H2"
        defer = {"H3": "виртуальные worst-case и timing/transient проверки", "firmware F3": "сборка и emulator-прогон до заказа", "H5": "проверка полученных образцов и land-fit", "H6": "placement/routing/DRC", "H8": "физический bring-up и HIL"}
        close = f"**Исторический результат:** ✅ ревизия `H2.8.2-R1` была принята пользователем {manifest['decision']['date']} и остаётся связанной SHA-256. Она явно запрещена как authority для R2. Текущий аппаратный маркер — `H1-R2.30`."
    else:
        title = "# Historical H2 production ECAD acceptance package · R1"
        nav = "[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)"
        intro = "This accepted package is retained as reproducible evidence for the former single-RP R1 architecture. It is not the current R2 architecture and does not authorize R2 KiCad, purchasing or fabrication."
        done_h = "## Completed"
        done = [
            "four complete native KiCad hierarchies: UI, RF/power, display adapter and LoRa Cap",
            "independent power/recovery/isolation/quiet-state/fault-shutdown review",
            f"zero native ERC findings and {final_counts['intentional_no_connects']} physically reconciled intentional NCs",
            f"{final_counts['ledger_rows']:,} ledger rows, {final_counts['reconciled_electrical_identities']:,} reconciled electrical identities, {final_counts['root_named_nets']} root nets and {final_counts['m1_physical_contacts']} M1 contacts reconciled",
            "130 controller allocations agree with KiCad; 125 MCU contacts are semantically identical in firmware F2 and the import is marked fail-closed historical R1",
            "two independent SA818S-V/U paths have separate SMA and TX evidence; the one-hot selector consumes no new MCU or M1 contact",
        ]
        defer_h = "## Deliberately outside H2"
        defer = {"H3": "virtual worst-case and timing/transient verification", "firmware F3": "build and emulator execution before ordering", "H5": "received-sample and land-fit checks", "H6": "placement/routing/DRC", "H8": "physical bring-up and HIL"}
        close = f"**Historical result:** ✅ revision `H2.8.2-R1` was accepted by the user on {manifest['decision']['date']} and remains SHA-256 bound. It is explicitly forbidden as R2 authority. The current hardware marker is `H1-R2.30`."
    done_text = "\n".join(f"- {item}" for item in done)
    deferred_text = "\n".join(f"- `{row['gate']}` — {defer[row['gate']]}" for row in manifest["deferred_gates"])
    evidence = "[Машинный пакет](../hardware/ecad/generated/H2-REV81-acceptance-package.json)." if russian else "[Machine package](../hardware/ecad/generated/H2-REV81-acceptance-package.json)."
    return "\n\n".join((title, nav, intro, done_h + "\n\n" + done_text, defer_h + "\n\n" + deferred_text, close, evidence)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    h28 = next(row for row in plan["substeps"] if row["id"] == "H2.8")
    decision_row = next(row for row in h28["children"] if row["id"] == "H2.8.2")
    if plan.get("status") != "reviewed" or decision_row.get("status") != "reviewed":
        raise ValueError("H2 plan does not record explicit H2.8.2 user acceptance")
    acceptance = plan.get("acceptance", {})
    if acceptance.get("status") != "accepted_by_user":
        raise ValueError("H2 plan acceptance record is absent")
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    contacts = json.loads(CONTACTS_PATH.read_text(encoding="utf-8"))
    nets = json.loads(NETS_PATH.read_text(encoding="utf-8"))
    no_connects = json.loads(NO_CONNECTS_PATH.read_text(encoding="utf-8"))
    final_counts = {
        "ledger_rows": inventory["summary"]["h2_instance_rows"],
        "reconciled_electrical_identities": contacts["summary"]["reconciled_electrical_identities"],
        "root_named_nets": nets["summary"]["root_named_nets"],
        "m1_physical_contacts": nets["summary"]["m1_physical_contacts"],
        "intentional_no_connects": no_connects["summary"]["intentional_no_connects"],
    }
    reviews = []
    for path in INPUTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not str(data.get("status", "")).startswith("reviewed_") or data.get("open_findings") or data.get("open_paper_or_ecad_findings"):
            raise ValueError(f"{path.name} is not a closed reviewed prerequisite")
        reviews.append({"stage": data["stage"], "artifact": str(path.relative_to(REPO)), "status": "reviewed"})
    manifest = {
        "schema_version": 1,
        "stage": "H2.8.1-R1",
        "status": "reviewed_h2_user_accepted",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "source_hashes": {
            **{str(path.relative_to(REPO)): sha256(path) for path in INPUTS},
            **{str(path.relative_to(REPO)): sha256(path) for path in (INVENTORY_PATH, CONTACTS_PATH, NETS_PATH, NO_CONNECTS_PATH)},
            str(PLAN.relative_to(REPO)): sha256(PLAN),
        },
        "final_counts": final_counts,
        "reviewed_prerequisites": reviews,
        "acceptance_meaning": "accept the complete H2 production schematic as the immutable starting input for H3; later findings reopen affected gates",
        "acceptance_does_not_authorize": ["PCB placement/routing", "purchasing", "fabrication", "claim of physical prototype validation"],
        "deferred_gates": DEFERRED,
        "open_h2_technical_findings": [],
        "decision": {
            "stage": "H2.8.2-R1",
            "status": "accepted_by_user",
            "date": acceptance["date"],
            "baseline_binding": "source_hashes_in_this_artifact",
            "supersedes": acceptance["supersedes"],
        },
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, final_counts, False),
        DOC_RU: render_doc(manifest, final_counts, True),
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
        print(f"ok: H2 acceptance record is current; {manifest['decision']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
