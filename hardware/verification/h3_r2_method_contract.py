#!/usr/bin/env python3
"""Freeze reproducible R2 verification methods, tolerances and pass rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-method-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
FREEZE = REPO / "hardware/verification/generated/H3-R2-input-freeze.json"
PARAMETERS = REPO / "hardware/verification/generated/H3-R2-parameter-provenance.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
DOC_EN = REPO / "docs/verification-methods.md"
DOC_RU = REPO / "docs/verification-methods.ru.md"

SOURCES = (CONTRACT, FREEZE, PARAMETERS)

CLASS_METHODS = {
    "passive_corner": ["M-INT"],
    "connector_interconnect": ["M-INT"],
    "radio_rf": ["M-INT", "M-RF"],
    "analog_peripheral": ["M-INT", "M-ANALOG"],
    "programmable_controller": ["M-INT", "M-DIGITAL"],
    "digital_interface": ["M-INT", "M-DIGITAL"],
    "power_safety_active": ["M-INT", "M-DC", "M-TRANS", "M-THERMAL"],
    "electromechanical_or_load": ["M-INT", "M-STATE"],
    "general_component": ["M-INT"],
}

WORKSTREAM_METHODS = {
    "H3-R2.1": ["M-DC", "M-STATE"],
    "H3-R2.2": ["M-TRANS", "M-STATE"],
    "H3-R2.3": ["M-ANALOG", "M-TRANS", "M-THERMAL"],
    "H3-R2.4": ["M-DIGITAL"],
    "H3-R2.5": ["M-RF", "M-STATE"],
    "H3-R2.6": ["M-THERMAL", "M-STATE"],
    "H3-R2.7": ["M-XCHECK"],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    contract = load(CONTRACT)
    plan = load(PLAN)
    freeze = load(FREEZE)
    parameters = load(PARAMETERS)
    errors: list[str] = []

    statuses = {row.get("id"): row.get("status") for row in plan.get("substeps", [])}
    progress_valid = (
        plan.get("current_substep") == "H3-R2.0.3" and statuses.get("H3-R2.0.3") == "current"
    ) or (
        str(plan.get("current_substep", "")).startswith("H3-R2.") and statuses.get("H3-R2.0.3") == "reviewed"
    ) or (
        plan.get("status") == "reviewed" and plan.get("current_substep") is None and statuses.get("H3-R2.0.3") == "reviewed"
    )
    if not progress_valid:
        errors.append("H3 plan does not expose current or reviewed H3-R2.0.3")
    if freeze.get("status") != "pass" or parameters.get("status") != "pass":
        errors.append("H3-R2.0.1 or H3-R2.0.2 input is not passing")
    if parameters.get("summary", {}).get("open_decisions") != 0:
        errors.append("parameter provenance still has an open decision")

    methods = contract.get("methods", [])
    pass_rules = contract.get("pass_fail_rules", [])
    method_ids = [row.get("id") for row in methods]
    if len(method_ids) != len(set(method_ids)):
        errors.append("duplicate method id")
    rule_ids = [row.get("id") for row in pass_rules]
    if len(rule_ids) != len(set(rule_ids)):
        errors.append("duplicate pass/fail rule id")
    method_set = set(method_ids)
    expected_workstreams = {f"H3-R2.{index}" for index in range(1, 8)}
    covered_workstreams = {item for row in methods for item in row.get("workstreams", [])}
    if covered_workstreams != expected_workstreams:
        errors.append("methods do not cover all seven R2 workstreams")
    for row in methods:
        if not row.get("method") or not row.get("anti_shortcut") or not row.get("workstreams"):
            errors.append(f"incomplete method: {row.get('id')}")

    assignments: list[dict] = []
    use_count: Counter[str] = Counter()
    for row in parameters.get("rows", []):
        assigned = set(CLASS_METHODS.get(row.get("parameter_class"), []))
        for owner in row.get("owner_workstreams", []):
            assigned.update(WORKSTREAM_METHODS.get(owner, []))
        unknown = assigned - method_set
        if unknown:
            errors.append(f"unknown method assignment for {row.get('device_id')}: {sorted(unknown)}")
        if not assigned:
            errors.append(f"no method assignment for {row.get('device_id')}")
        use_count.update(assigned)
        assignments.append({
            "device_id": row.get("device_id"),
            "parameter_class": row.get("parameter_class"),
            "owner_workstreams": row.get("owner_workstreams"),
            "method_ids": sorted(assigned),
            "parameter_state": row.get("parameter_state"),
            "missing_parameter_disposition": "unresolved_fail" if row.get("parameter_state") == "explicit_extraction_queue" else "evaluate_authoritative_corners",
        })
    if set(CLASS_METHODS) != set(parameters.get("summary", {}).get("parameter_classes", {})):
        errors.append("parameter-class method map is incomplete or contains a stale class")
    if set(WORKSTREAM_METHODS) != expected_workstreams:
        errors.append("workstream method map is incomplete")

    expected = contract.get("expected", {})
    actual = {
        "parameter_rows": len(assignments),
        "parameter_classes": len(CLASS_METHODS),
        "workstreams": len(covered_workstreams),
        "methods": len(methods),
        "pass_fail_rules": len(pass_rules),
    }
    if actual != expected:
        errors.append(f"method-contract counts differ: {actual} != {expected}")

    runtime_ok = (3, 12) <= sys.version_info[:2] < (3, 15)
    if not runtime_ok:
        errors.append("current Python runtime is outside the frozen range")
    sources = {str(path.relative_to(REPO)): digest(path) for path in SOURCES}
    payload = json.dumps({"sources": sources, "contract": contract, "assignments": assignments}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "artifact": "H3-R2-method-contract",
        "marker": "H3-R2.0.3",
        "status": "pass" if not errors else "fail",
        "accepted_input": "H3-R2.0.2",
        "input_freeze_sha256": freeze.get("freeze_sha256"),
        "parameter_register_sha256": parameters.get("register_sha256"),
        "method_contract_sha256": hashlib.sha256(payload).hexdigest(),
        "source_sha256": sources,
        "toolchain": {
            **contract.get("toolchain", {}),
            "verified_runtime": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "runtime_accepted": runtime_ok,
        },
        "tolerance_policy": contract.get("tolerance_policy", {}),
        "methods": methods,
        "pass_fail_rules": pass_rules,
        "reproducibility": contract.get("reproducibility", {}),
        "parameter_method_assignments": assignments,
        "summary": {
            **actual,
            "assigned_parameter_rows": sum(bool(row["method_ids"]) for row in assignments),
            "method_usage": dict(sorted(use_count.items())),
            "explicit_unresolved_until_extraction": sum(row["missing_parameter_disposition"] == "unresolved_fail" for row in assignments),
            "open_method_questions": 0,
            "errors": len(errors),
        },
        "authorization": {
            **contract.get("authorization", {}),
            "advance_to_h3_r2_1": not errors,
        },
        "errors": errors,
    }


def render_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def render_doc(result: dict, ru: bool) -> str:
    summary = result["summary"]
    if ru:
        title = "# Как проверяется железо R2 до изготовления"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Параметры](parameter-model-register.ru.md) · [English](verification-methods.md)"
        intro = "Статус `H3-R2.0.3`: ✅ reviewed. Проверка R2 использует воспроизводимые worst-case методы, а не оптимистичные typical-значения. Каждый будущий результат обязан показать источники, состояния/corners, худший случай, численный запас и физический residual."
        method_h = "## Методы R2"
        headers = ("ID", "Workstreams", "Метод", "Запрещённая подмена")
        rules_h = "## Единые pass/fail rules"
        tool_h = "## Воспроизводимость"
        tool = f"Все `{summary['parameter_rows']}` групп получили хотя бы один метод; используются `{summary['methods']}` методов и `{summary['pass_fail_rules']}` общих rules. Runtime — `{result['toolchain']['verified_runtime']}`, только standard library, `Decimal` precision 50/Fraction, hash-bound JSON/CSV/SVG. Сеть, случайность и незакреплённый внешний solver не участвуют в acceptance."
        queue_h = "## Что ещё не является pass"
        queue = f"У `{summary['explicit_unresolved_until_extraction']}` групп параметры ещё извлекаются из точных источников. Контракт метода закрыт, но их расчёты обязаны вернуть `unresolved_fail`, пока нет min/max, unit и applicability."
        boundary = "Следующий шаг — H3-R2.1: power/DC/source/charge/state расчёты. Placement, routing, закупка и печать остаются запрещены."
        machine = f"[Машинный контракт методов и {summary['assigned_parameter_rows']} назначений](../hardware/verification/generated/H3-R2-method-contract.json). Исторический `H3-VRF03` не является authority R2."
    else:
        title = "# How R2 hardware is verified before fabrication"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Parameters](parameter-model-register.md) · [Русский](verification-methods.ru.md)"
        intro = "`H3-R2.0.3` status: ✅ reviewed. R2 verification uses reproducible worst-case methods rather than optimistic typical values. Every future result must expose sources, states/corners, worst case, numeric margin and its physical residual."
        method_h = "## R2 methods"
        headers = ("ID", "Workstreams", "Method", "Forbidden shortcut")
        rules_h = "## Common pass/fail rules"
        tool_h = "## Reproducibility"
        tool = f"All `{summary['parameter_rows']}` groups have at least one method; the contract defines `{summary['methods']}` methods and `{summary['pass_fail_rules']}` common rules. Runtime is `{result['toolchain']['verified_runtime']}` with standard library only, Decimal precision 50/Fraction and hash-bound JSON/CSV/SVG. Network access, randomness and an unbound external solver cannot participate in acceptance."
        queue_h = "## What is not yet a pass"
        queue = f"`{summary['explicit_unresolved_until_extraction']}` groups still require exact parameter extraction. The method contract is closed, but their calculations must return `unresolved_fail` until min/max, unit and applicability are bound."
        boundary = "The next step is H3-R2.1 power/DC/source/charge/state analysis. Placement, routing, purchasing and fabrication remain forbidden."
        machine = f"[Machine method contract and {summary['assigned_parameter_rows']} assignments](../hardware/verification/generated/H3-R2-method-contract.json). Historical `H3-VRF03` is not R2 authority."
    method_rows = "\n".join(
        f"| `{row['id']}` | {', '.join(row['workstreams'])} | {row['method']} | {row['anti_shortcut']} |"
        for row in result["methods"]
    )
    rules = "\n".join(f"- `{row['id']}` — {row['rule']}" for row in result["pass_fail_rules"])
    return "\n\n".join((
        title, nav, intro, method_h,
        "| " + " | ".join(headers) + " |\n|---|---|---|---|\n" + method_rows,
        rules_h, rules, tool_h, tool, queue_h, queue, "> " + boundary, machine,
    )) + "\n"


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
    outputs = {OUTPUT: render_json(result), DOC_EN: render_doc(result, False), DOC_RU: render_doc(result, True)}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(
            f"wrote H3-R2.0.3 method contract {result['method_contract_sha256'][:12]}: "
            f"{result['summary']['methods']} methods, {result['summary']['parameter_rows']} assignments"
        )
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: R2 methods, tolerances, tools and pass/fail rules are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
