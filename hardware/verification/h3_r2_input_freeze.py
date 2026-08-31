#!/usr/bin/env python3
"""Freeze reviewed H2-R2 inputs and the complete H3-R2 verification matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-input-freeze-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
H1 = REPO / "hardware/product-design/h1-r2-placement.json"
INVENTORY = REPO / "hardware/ecad/generated/H2-R2-native-inventory.json"
LEDGER = REPO / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"
CONTACTS = REPO / "hardware/ecad/generated/H2-R2-contact-materialization.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NETS = REPO / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
KICAD = REPO / "hardware/ecad/generated/H2-R2-native-kicad-projects.json"
HWFW = REPO / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
M1 = REPO / "hardware/ecad/generated/H2-R2-interboard-m1.json"
AUTHORITY = REPO / "hardware/architecture/generated/H0-R2-authority-gate.json"
PREORDER = REPO / "hardware/verification/preorder-verification-contract.json"
H2_CONSOLIDATED = REPO / "hardware/ecad/generated/H2-REV75-hwfw-consolidated.json"
H2_ACCEPTANCE = REPO / "hardware/ecad/generated/H2-REV81-acceptance-package.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-input-freeze.json"
DOC_EN = REPO / "docs/h3-r2-input-freeze.md"
DOC_RU = REPO / "docs/h3-r2-input-freeze.ru.md"

SOURCES = (
    CONTRACT, H0, H1, INVENTORY, LEDGER, CONTACTS, INSTANCES, NETS,
    KICAD, HWFW, M1, AUTHORITY, H2_CONSOLIDATED, H2_ACCEPTANCE,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(contract: dict | None = None) -> dict:
    contract = contract or load(CONTRACT)
    plan = load(PLAN)
    inventory = load(INVENTORY)
    kicad = load(KICAD)
    hwfw = load(HWFW)
    m1 = load(M1)
    authority = load(AUTHORITY)
    preorder = load(PREORDER)
    errors: list[str] = []
    expected = contract.get("expected", {})

    actual = {
        "projects": kicad.get("summary", {}).get("project_count"),
        "sheets": kicad.get("summary", {}).get("project_graph_sheet_count"),
        "fitted_symbols": kicad.get("summary", {}).get("fitted_symbol_instance_count"),
        "physical_pins": kicad.get("summary", {}).get("physical_symbol_pin_count"),
        "canonical_nets": kicad.get("summary", {}).get("canonical_net_count"),
        "domains": hwfw.get("summary", {}).get("domain_count"),
        "controller_pins": hwfw.get("summary", {}).get("controller_pin_rows"),
        "cross_project_nets": hwfw.get("summary", {}).get("cross_project_net_count"),
        "cross_sheet_nets": hwfw.get("summary", {}).get("cross_sheet_net_count"),
        "m1_contacts": m1.get("summary", {}).get("physical_contacts"),
        "m1_true_nc": m1.get("summary", {}).get("no_connect_reserve_contacts"),
    }
    if actual != expected:
        errors.append("reviewed H2-R2 counts differ from the H3 input-freeze contract")

    if plan.get("accepted_input", {}).get("stage") != "H2-R2.1.5":
        errors.append("H3 plan does not accept reviewed H2-R2.1.5")
    statuses = {row.get("id"): row.get("status") for row in plan.get("substeps", [])}
    current_h3 = str(plan.get("current_substep", ""))
    phase_closed = plan.get("status") == "reviewed" and plan.get("current_substep") is None
    if not (current_h3.startswith("H3-R2.") or phase_closed) or statuses.get("H3-R2.0.1") != "reviewed":
        errors.append("H3 plan does not preserve reviewed input freeze before parameter provenance")
    if kicad.get("status") != "pass" or hwfw.get("status") != "pass":
        errors.append("native KiCad or hardware/firmware reconciliation is not passing")
    if authority.get("status") != "pass_current_r2_h2_reconciled" or not authority.get("r2_h2_authoritative"):
        errors.append("current R2 H2 authority gate is not open")
    gates = {row.get("id"): row.get("status") for row in preorder.get("gates", [])}
    if gates.get("P2_R2_PRODUCTION_SCHEMATIC") != "reviewed" or gates.get("P3_R2_VIRTUAL_ELECTRICAL") not in {"in_progress", "reviewed"}:
        errors.append("pre-order contract does not expose reviewed P2 and current P3")
    if preorder.get("current_truth", {}).get("order_authorized") is not False:
        errors.append("input freeze must not authorize an order")

    inventory_sheets = [
        sheet["id"]
        for project in inventory.get("projects", [])
        for sheet in project.get("sheets", [])
    ]
    matrix_sheets = [
        sheet
        for workstream in contract.get("workstreams", [])
        for sheet in workstream.get("sheets", [])
    ]
    inventory_devices = {row["device_id"] for row in inventory.get("component_groups", [])}
    shared_dependencies = [
        (workstream["id"], device_id)
        for workstream in contract.get("workstreams", [])
        for device_id in workstream.get("shared_parameter_dependencies", [])
    ]
    if sorted(matrix_sheets) != sorted(inventory_sheets):
        errors.append("H3 matrix does not cover the exact 23-sheet native graph")
    if len(matrix_sheets) != len(set(matrix_sheets)):
        errors.append("a native sheet has more than one primary H3 workstream")
    if len(shared_dependencies) != len(set(shared_dependencies)):
        errors.append("a workstream repeats a shared parameter dependency")
    unknown_dependencies = sorted({device_id for _, device_id in shared_dependencies} - inventory_devices)
    if unknown_dependencies:
        errors.append("shared parameter dependencies are not exact inventory groups: " + ", ".join(unknown_dependencies))
    workstream_ids = [row.get("id") for row in contract.get("workstreams", [])]
    if workstream_ids != [f"H3-R2.{index}" for index in range(1, 8)]:
        errors.append("H3 matrix must contain ordered workstreams H3-R2.1 through H3-R2.7")
    required_domains = {"s3", "c5", "hub_rp", "rf_rp", "pack", "safety"}
    matrix_domains = {
        domain
        for workstream in contract.get("workstreams", [])
        for domain in workstream.get("domains", [])
    }
    if matrix_domains != required_domains:
        errors.append("H3 matrix does not cover all six compute domains")
    for row in contract.get("workstreams", []):
        for field in ("title", "models", "pass_rule", "physical_residual_owner"):
            if not row.get(field):
                errors.append(f"{row.get('id', 'unknown')} lacks {field}")

    sources = {
        str(path.relative_to(REPO)): digest(path)
        for path in SOURCES
    }
    freeze_payload = json.dumps(
        {"sources": sources, "matrix": contract.get("workstreams", [])},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "schema_version": 1,
        "artifact": "H3-R2-input-freeze",
        "marker": "H3-R2.0.1",
        "status": "pass" if not errors else "fail",
        "accepted_hardware_input": contract.get("accepted_hardware_input"),
        "freeze_sha256": hashlib.sha256(freeze_payload).hexdigest(),
        "source_sha256": sources,
        "summary": {
            **actual,
            "workstream_count": len(contract.get("workstreams", [])),
            "matrix_sheet_assignments": len(matrix_sheets),
            "unique_matrix_sheets": len(set(matrix_sheets)),
            "shared_parameter_dependencies": len(shared_dependencies),
            "covered_domains": sorted(matrix_domains),
            "errors": len(errors),
        },
        "workstreams": contract.get("workstreams", []),
        "authorization": contract.get("authorization", {}),
        "errors": errors,
    }


def render_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def render_doc(result: dict, ru: bool) -> str:
    summary = result["summary"]
    if ru:
        title = "# H3-R2.0.1 · фиксация входов виртуальной проверки"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](h3-r2-input-freeze.md)"
        intro = (
            f"Проведено ревью точного входа H2-R2.1.5: `{summary['projects']}` проекта, "
            f"`{summary['sheets']}` листа, `{summary['fitted_symbols']}` устанавливаемых symbols, "
            f"`{summary['physical_pins']}` физических pins и `{summary['canonical_nets']}` nets. "
            "Все входы захешированы; любое изменение закрывает воспроизводимость до повторной генерации."
        )
        headers = ("Работа", "Основной охват", "Листы", "Критерий")
        boundary = "Этот шаг разрешает только расчёты и симуляцию. Placement, routing, закупка и печать остаются запрещены."
    else:
        title = "# H3-R2.0.1 · virtual-verification input freeze"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h3-r2-input-freeze.ru.md)"
        intro = (
            f"The exact H2-R2.1.5 input is reviewed: `{summary['projects']}` projects, "
            f"`{summary['sheets']}` sheets, `{summary['fitted_symbols']}` fitted symbols, "
            f"`{summary['physical_pins']}` physical pins and `{summary['canonical_nets']}` nets. "
            "Every input is hash-bound; any change closes reproducibility until regeneration."
        )
        headers = ("Workstream", "Primary scope", "Sheets", "Pass rule")
        boundary = "This step authorizes analysis and simulation only. Placement, routing, purchasing and fabrication remain forbidden."
    rows = "\n".join(
        f"| `{row['id']}` | {row['title']} | {len(row['sheets'])} + {len(row.get('shared_parameter_dependencies', []))} shared parameter groups | {row['pass_rule']} |"
        for row in result["workstreams"]
    )
    return "\n".join([
        title, "", nav, "", intro, "", f"Freeze SHA-256: `{result['freeze_sha256']}`", "",
        "| " + " | ".join(headers) + " |", "|---|---|---:|---|", rows, "", f"> {boundary}", "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    outputs = {
        OUTPUT: render_json(result),
        DOC_EN: render_doc(result, False),
        DOC_RU: render_doc(result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(
            f"wrote H3-R2.0.1 freeze {result['freeze_sha256'][:12]}: "
            f"{result['summary']['workstream_count']} workstreams, "
            f"{result['summary']['unique_matrix_sheets']} sheets"
        )
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items()
             if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: reviewed H2 inputs and all 23 native sheets are frozen for H3-R2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
