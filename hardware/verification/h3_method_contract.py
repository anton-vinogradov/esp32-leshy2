#!/usr/bin/env python3
"""Freeze reproducible H3 calculation methods and pass/fail policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
FREEZE = REPO / "hardware/verification/generated/H3-VRF01-input-freeze.json"
INVENTORY = REPO / "hardware/verification/generated/H3-VRF02-parameter-inventory.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
DOC_EN = REPO / "docs/verification-methods.md"
DOC_RU = REPO / "docs/verification-methods.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


METHODS = [
    {
        "id": "interval_corner",
        "applies_to": ["H3.1", "H3.3", "H3.4"],
        "method": "Decimal interval arithmetic over min/max tolerances plus explicit discrete operating modes",
        "anti_shortcut": "typical values may be reported but can never prove a pass",
    },
    {
        "id": "dc_network",
        "applies_to": ["H3.1"],
        "method": "closed-form KCL/KVL and efficiency/loss envelopes evaluated at every legal source/load state",
        "anti_shortcut": "rail loads may not be hidden in an aggregate unexplained allowance",
    },
    {
        "id": "bounded_transient",
        "applies_to": ["H3.2", "H3.3"],
        "method": "piecewise-linear or datasheet behavioral state model with Decimal time base, explicit initial conditions and dt/dt2 convergence check",
        "anti_shortcut": "a waveform without input provenance, timestep convergence and threshold markers is non-evidence",
    },
    {
        "id": "state_fault_exploration",
        "applies_to": ["H3.2", "H3.6"],
        "method": "deterministic enumeration of legal states, single faults, watchdog deadlines and recovery transitions",
        "anti_shortcut": "nominal happy-path simulation cannot close a safety requirement",
    },
    {
        "id": "digital_static_timing",
        "applies_to": ["H3.4"],
        "method": "level/pull/leakage/back-power predicates and worst-case timing/occupancy algebra for each interface",
        "anti_shortcut": "logic-family labels do not replace VIH/VIL/VOH/VOL and power-off behavior",
    },
    {
        "id": "rf_prelayout_budget",
        "applies_to": ["H3.5"],
        "method": "source-to-antenna 50-ohm loss/mismatch budget plus reference-plane, corridor, isolation and coexistence constraints",
        "anti_shortcut": "pre-layout calculation cannot claim final impedance, isolation or radiated performance; those remain H6/H8",
    },
    {
        "id": "lumped_thermal",
        "applies_to": ["H3.1", "H3.3", "H3.6"],
        "method": "worst-case dissipation and bounded thermal-resistance/capacitance network for board, enclosure and cells",
        "anti_shortcut": "unknown enclosure or interface resistance is a range, never a guessed scalar",
    },
    {
        "id": "evidence_crosscheck",
        "applies_to": ["H3.7"],
        "method": "machine join from every requirement and H2 net/device identity to an H3 result and downstream physical measurement",
        "anti_shortcut": "an unlinked result does not close a requirement",
    },
]


PASS_FAIL = [
    {
        "id": "PF-01",
        "rule": "Every normal and allowed degraded corner stays inside manufacturer recommended operating conditions; absolute maximum ratings are never design targets.",
    },
    {
        "id": "PF-02",
        "rule": "Steady rail/source current has at least 25% reserve over the enumerated worst-case load; exceptions require a named transient-only rating and separate H3.2 proof.",
    },
    {
        "id": "PF-03",
        "rule": "A regulated rail retains at least 5% of nominal-voltage headroom after source tolerance, distribution loss and steady droop, while every load remains inside its own supply range.",
    },
    {
        "id": "PF-04",
        "rule": "Worst-case timing and shared-resource occupancy use no more than 80% of the allocated deadline/budget; independent dedicated buses are checked for latency but are not combined artificially.",
    },
    {
        "id": "PF-05",
        "rule": "Power-off, reset and quiet-state combinations produce no back-power or unintended transmitter enable; any non-zero injection must remain below the exact published limit with 2x analytical reserve.",
    },
    {
        "id": "PF-06",
        "rule": "Predicted silicon junction temperature remains at least 20 C below the applicable maximum; battery charge/discharge temperature remains at least 10 C inside the exact cell/charger operating boundary.",
    },
    {
        "id": "PF-07",
        "rule": "Every enumerated single fault reaches a bounded-energy safe state without relying on the same firmware domain that may have failed, while a retained diagnostic reason remains recoverable.",
    },
    {
        "id": "PF-08",
        "rule": "Transient numerical evidence must agree at dt and dt/2 within 10% of the remaining pass margin; otherwise the timestep is reduced or the result fails unresolved.",
    },
    {
        "id": "PF-09",
        "rule": "RF pre-layout results pass only as layout constraints and loss/isolation budgets; final 50-ohm, matching, VNA, spectrum and coexistence claims remain H6/H8 measurements.",
    },
    {
        "id": "PF-10",
        "rule": "A missing min/max tolerance, applicability condition or model provenance is a fail/unresolved result, never an assumed pass.",
    },
]


def build() -> tuple[dict[Path, str], dict]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if inventory.get("status") != "reviewed_inventory_complete_lifecycle_choice_resolved":
        raise ValueError("H3.0.2 is not reviewed")
    if inventory.get("open_decisions"):
        raise ValueError("H3.0.2 still has an open decision")
    manifest = {
        "schema_version": 1,
        "stage": "H3.0.3",
        "status": "reviewed_reproducible_methods_and_pass_fail_frozen",
        "source_hashes": {
            str(FREEZE.relative_to(REPO)): sha256(FREEZE),
            str(INVENTORY.relative_to(REPO)): sha256(INVENTORY),
        },
        "toolchain": {
            "required_python": ">=3.12,<3.15",
            "verified_runtime": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "runtime_acceptance": sys.version_info >= (3, 12) and sys.version_info < (3, 15),
            "third_party_python_dependencies": [],
            "numeric_core": "decimal.Decimal, precision 34, ROUND_HALF_EVEN; integer/rational arithmetic where exact",
            "artifact_formats": ["canonical JSON", "CSV", "SVG"],
            "randomness": "forbidden for acceptance; Monte Carlo may illustrate but cannot replace enumerated worst cases",
            "network": "forbidden during regeneration; external documents are provenance inputs, not runtime dependencies",
        },
        "input_contract": {
            "required_for_every_numeric_input": ["name", "value or min/nom/max", "unit", "source URL/document", "applicability", "temperature/mode", "derivation if calculated"],
            "missing_limit_disposition": "unresolved_fail",
            "typical_value_disposition": "informative_only_unless_the_requirement_itself_is_typical",
            "rounding": "round only for presentation; evaluate pass/fail before presentation rounding",
        },
        "methods": METHODS,
        "pass_fail_rules": PASS_FAIL,
        "reproducibility": {
            "each_calculator_must_emit": ["input hashes", "method id", "all corners/states", "worst corner", "numeric margin", "pass/fail/unresolved", "residual physical gate"],
            "each_calculator_must_support": ["--write", "--check", "self-test or unit-test coverage"],
            "regeneration_order": "H3-VRF01 -> H3-VRF02 -> H3-VRF03 -> numbered H3 calculation artifacts",
            "acceptance_is_invalidated_by": ["input hash drift", "toolchain contract drift", "unresolved parameter", "failed margin", "unassigned physical-only uncertainty"],
        },
        "summary": {
            "methods": len(METHODS),
            "pass_fail_rules": len(PASS_FAIL),
            "third_party_runtime_dependencies": 0,
            "open_method_questions": 0,
        },
        "open_findings": [],
    }
    if not manifest["toolchain"]["runtime_acceptance"]:
        raise ValueError(f"unsupported Python runtime: {manifest['toolchain']['verified_runtime']}")
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Как проверяется железо до изготовления"
        nav = "[English](verification-methods.md) · [На главную](../README.ru.md) · [Виртуальная проверка](virtual-verification.ru.md) · [Параметры](parameter-model-register.ru.md)"
        intro = "H3 использует воспроизводимые worst-case расчёты, а не оптимистичные typical-значения. Каждый результат показывает входные источники, проверенные состояния, худший corner, численный запас и физическую проверку, которая всё ещё нужна после изготовления."
        method_h = "## Методы"
        headers = "| Область | Метод | Что запрещено подменять |\n|---|---|---|"
        rule_h = "## Единые правила прохождения"
        rules = "\n".join(f"- `{r['id']}` — {r['rule']}" for r in manifest["pass_fail_rules"])
        tool_h = "## Воспроизводимость"
        tool = "Расчётное ядро использует только Python standard library, `Decimal` с фиксированной точностью и JSON/CSV/SVG. Сеть и случайность не участвуют в acceptance; каждый генератор обязан иметь режимы `--write` и `--check`, входные SHA-256 и тесты."
        marker = "**Статус:** `H3.0.3` завершено и проверено. Текущий точный маркер — `H3.4.1`, digital levels/defaults и no-back-power."
        evidence = "[Машинный контракт методов](../hardware/verification/generated/H3-VRF03-method-contract.json)."
    else:
        title = "# How hardware is verified before fabrication"
        nav = "[Русский](verification-methods.ru.md) · [Home](../README.md) · [Virtual verification](virtual-verification.md) · [Parameters](parameter-model-register.md)"
        intro = "H3 uses reproducible worst-case analysis rather than optimistic typical values. Every result exposes input sources, evaluated states, the worst corner, numeric margin and the physical check still required after fabrication."
        method_h = "## Methods"
        headers = "| Scope | Method | Forbidden shortcut |\n|---|---|---|"
        rule_h = "## Common pass rules"
        rules = "\n".join(f"- `{r['id']}` — {r['rule']}" for r in manifest["pass_fail_rules"])
        tool_h = "## Reproducibility"
        tool = "The calculation core uses only the Python standard library, fixed-precision `Decimal`, and JSON/CSV/SVG. Network access and randomness do not participate in acceptance; every generator must provide `--write` and `--check`, input SHA-256 and tests."
        marker = "**Status:** `H3.0.3` is reviewed. The current exact marker is `H3.4.1`, digital levels/defaults and no-back-power."
        evidence = "[Machine method contract](../hardware/verification/generated/H3-VRF03-method-contract.json)."
    rows = "\n".join(
        f"| {', '.join(method['applies_to'])} | {method['method']} | {method['anti_shortcut']} |"
        for method in manifest["methods"]
    )
    return "\n\n".join((title, nav, intro, method_h, headers + "\n" + rows, rule_h, rules, tool_h, tool, marker, evidence)) + "\n"


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
        print(f"ok: H3.0.3 methods current; {manifest['summary']['methods']} methods, {manifest['summary']['pass_fail_rules']} pass rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
