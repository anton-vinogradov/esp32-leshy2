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
PLAN = ECAD / "h2-schematic-plan.json"


DEFERRED = [
    {"gate": "H3", "scope": "worst-case DC, startup/shutdown, handover, fault, transient, digital timing and pre-layout RF simulation"},
    {"gate": "firmware F3", "scope": "target skeleton builds, size/rollback checks and available emulator execution before fabrication"},
    {"gate": "H5", "scope": "received-part dimensional, drawing, lifecycle, connector and land-fit evidence"},
    {"gate": "H6", "scope": "PCB placement, stack-up, impedance, copper, thermal layout and complete DRC"},
    {"gate": "H8", "scope": "prototype bring-up, HIL, RF coexistence, power/fault injection, thermals and long-duration operation"},
]


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Пакет приёмки production ECAD H2"
        nav = "[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)"
        intro = "H2 принят пользователем как неизменяемый исходный материал H3. Приёмка означает согласие с production schematic-контрактом, а не разрешение KiCad layout, закупки или печати; позднее несоответствие повторно открывает затронутый gate."
        done_h = "## Что завершено"
        done = [
            "четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap",
            "независимое power/recovery/isolation/quiet-state/fault-shutdown ревью",
            "нулевой native ERC и 189 физически сопоставленных намеренных NC",
            "1 028 ledger-строк, 1 026 электрических identities, 266 root nets и 80 M1 contacts сверены",
            "130 controller allocations совпадают с KiCad; 125 MCU-контактов byte-identical в firmware F2",
        ]
        defer_h = "## Что сознательно остаётся за границей H2"
        defer = {"H3": "виртуальные worst-case и timing/transient проверки", "firmware F3": "сборка и emulator-прогон до заказа", "H5": "проверка полученных образцов и land-fit", "H6": "placement/routing/DRC", "H8": "физический bring-up и HIL"}
        close = "**Результат:** ✅ `H2.8.2` принят пользователем 24 августа 2026 года на hardware commit `25d9ee2` и firmware commit `900bb2b`. Следующий аппаратный маркер — `H3.0.1`."
    else:
        title = "# H2 production ECAD acceptance package"
        nav = "[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)"
        intro = "H2 was accepted by the user as the immutable H3 input. Acceptance means agreement with the production-schematic contract, not authorization for KiCad layout, purchasing or fabrication; a later mismatch reopens the affected gate."
        done_h = "## Completed"
        done = [
            "four complete native KiCad hierarchies: UI, RF/power, display adapter and LoRa Cap",
            "independent power/recovery/isolation/quiet-state/fault-shutdown review",
            "zero native ERC findings and 189 physically reconciled intentional NCs",
            "1,028 ledger rows, 1,026 electrical identities, 266 root nets and 80 M1 contacts reconciled",
            "130 controller allocations agree with KiCad; 125 MCU contacts are byte-identical in firmware F2",
        ]
        defer_h = "## Deliberately outside H2"
        defer = {"H3": "virtual worst-case and timing/transient verification", "firmware F3": "build and emulator execution before ordering", "H5": "received-sample and land-fit checks", "H6": "placement/routing/DRC", "H8": "physical bring-up and HIL"}
        close = "**Result:** ✅ `H2.8.2` was accepted by the user on 24 August 2026 at hardware commit `25d9ee2` and firmware commit `900bb2b`. The next hardware marker is `H3.0.1`."
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
    reviews = []
    for path in INPUTS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not str(data.get("status", "")).startswith("reviewed_") or data.get("open_findings") or data.get("open_paper_or_ecad_findings"):
            raise ValueError(f"{path.name} is not a closed reviewed prerequisite")
        reviews.append({"stage": data["stage"], "artifact": str(path.relative_to(REPO)), "status": "reviewed"})
    manifest = {
        "schema_version": 1,
        "stage": "H2.8.1",
        "status": "reviewed_h2_user_accepted",
        "source_hashes": {
            **{str(path.relative_to(REPO)): sha256(path) for path in INPUTS},
            str(PLAN.relative_to(REPO)): sha256(PLAN),
        },
        "reviewed_prerequisites": reviews,
        "acceptance_meaning": "accept the complete H2 production schematic as the immutable starting input for H3; later findings reopen affected gates",
        "acceptance_does_not_authorize": ["PCB placement/routing", "purchasing", "fabrication", "claim of physical prototype validation"],
        "deferred_gates": DEFERRED,
        "open_h2_technical_findings": [],
        "decision": {
            "stage": "H2.8.2",
            "status": "accepted_by_user",
            "date": acceptance["date"],
            "accepted_hardware_commit": acceptance["accepted_hardware_commit"],
            "accepted_firmware_commit": acceptance["accepted_firmware_commit"],
        },
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
        print(f"ok: H2 acceptance record is current; {manifest['decision']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
