#!/usr/bin/env python3
"""Bind every R2 power-connected fitted instance to an explicit load line."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-load-binding-contract.json"
STATES = REPO / "hardware/verification/generated/H3-R2-power-state-register.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
PARAMETERS = REPO / "hardware/verification/generated/H3-R2-parameter-provenance.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NETS = REPO / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
DEVICES = REPO / "hardware/architecture/devices.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-load-binding.json"
DOC_EN = REPO / "docs/power-load-binding.md"
DOC_RU = REPO / "docs/power-load-binding.ru.md"
SOURCES = (CONTRACT, STATES, METHODS, PARAMETERS, INSTANCES, NETS, DEVICES)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference_prefix(reference: str) -> str:
    match = re.match(r"([A-Za-z]+)", reference)
    return match.group(1).upper() if match else "OTHER"


def current_candidates(value: Any, prefix: str = "") -> list[dict]:
    found: list[dict] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if "current" in key.lower() and isinstance(item, (int, float)):
                found.append({"path": path, "value": item})
            else:
                found.extend(current_candidates(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(current_candidates(item, f"{prefix}[{index}]"))
    return found


def main_disposition(prefix: str, instance: str, contract: dict) -> str:
    disposition = contract["reference_dispositions"].get(prefix, "other_power_connected_part")
    if prefix == "U" and any(token in instance for token in contract["source_path_instance_tokens"]):
        return "conversion_or_protection_path"
    return disposition


def build() -> dict:
    contract = load(CONTRACT)
    states = load(STATES)
    methods = load(METHODS)
    parameters = load(PARAMETERS)
    instances = load(INSTANCES)
    nets = load(NETS)
    devices = load(DEVICES)["devices"]
    errors: list[str] = []
    if states.get("status") != "pass" or states.get("marker") != "H3-R2.1.1":
        errors.append("H3-R2.1.1 state register is not passing")
    if methods.get("status") != "pass":
        errors.append("H3-R2 method contract is not passing")

    parameter_by_device = {row["device_id"]: row for row in parameters["rows"]}
    instance_by_key = {
        (row["project"], row["sheet"], row["reference"], row["instance"], row["device_id"]): row
        for row in instances["rows"]
    }
    rail_nets = contract["rail_nets"]
    missing_reviewed_nets = sorted(set(contract["required_reviewed_power_nets"]) - set(rail_nets))
    if missing_reviewed_nets:
        errors.append(f"reviewed H2 power nets missing from binding contract: {missing_reviewed_nets}")
    connected: dict[tuple, set[str]] = defaultdict(set)
    for row in nets["rows"]:
        net = row.get("net")
        if net in rail_nets:
            key = (row["project"], row["sheet"], row["reference"], row["instance"], row["device_id"])
            connected[key].add(net)

    lines: list[dict] = []
    for key in sorted(connected):
        project, sheet, reference, instance, device_id = key
        inventory = instance_by_key.get(key)
        parameter = parameter_by_device.get(device_id)
        device = devices.get(device_id)
        if inventory is None:
            errors.append(f"power-connected instance missing from instance ledger: {key}")
            continue
        if parameter is None or device is None:
            errors.append(f"power-connected instance lacks exact parameter/device source: {key}")
            continue
        bindings = [
            {"net": net, **rail_nets[net]}
            for net in sorted(connected[key])
        ]
        canonical_rails = sorted({row["rail"] for row in bindings})
        profiles = sorted({row["profile"] for row in bindings})
        prefix = reference_prefix(reference)
        candidates = current_candidates(device.get("electrical_contract", {}))
        accounting = sorted({row.get("accounting", "direct") for row in bindings})
        parameter_state = "candidate_current_seed_requires_applicability_review" if candidates else "explicit_parameter_extraction_required"
        if prefix in {"C", "L", "FB", "Y", "X", "SW"}:
            parameter_state = "exact_nonload_parameter_extraction_required"
        lines.append({
            "id": f"LOAD-{len(lines) + 1:04d}",
            "instance_uid": inventory["instance_uid"],
            "project": project,
            "sheet": sheet,
            "reference": reference,
            "instance": instance,
            "device_id": device_id,
            "mpn": inventory["mpn"],
            "quantity": 1,
            "rail_bindings": bindings,
            "canonical_rails": canonical_rails,
            "profiles": profiles,
            "accounting": accounting,
            "disposition": main_disposition(prefix, instance, contract),
            "parameter_state": parameter_state,
            "candidate_current_fields": candidates,
            "source": parameter["source"],
            "parameter_owner": "H3-R2.1.3" if "SOURCE_OVERHEAD" not in canonical_rails and "PACK_DIRECT" not in canonical_rails else "H3-R2.1.4",
        })

    indirect_keys: set[tuple] = set()
    for indirect in contract["indirect_powered_instances"]:
        matches = [
            (key, row) for key, row in instance_by_key.items()
            if row["project"] == indirect["project"] and row["instance"] == indirect["instance"]
        ]
        if len(matches) != 1:
            errors.append(f"indirect powered instance does not resolve exactly once: {indirect}")
            continue
        key, inventory = matches[0]
        if key in connected:
            errors.append(f"indirect powered instance is already directly rail-bound: {key}")
            continue
        parameter = parameter_by_device.get(inventory["device_id"])
        device = devices.get(inventory["device_id"])
        if parameter is None or device is None:
            errors.append(f"indirect powered instance lacks exact parameter/device source: {key}")
            continue
        indirect_keys.add(key)
        candidates = current_candidates(device.get("electrical_contract", {}))
        lines.append({
            "id": f"LOAD-{len(lines) + 1:04d}",
            "instance_uid": inventory["instance_uid"],
            "project": inventory["project"],
            "sheet": inventory["sheet"],
            "reference": inventory["reference"],
            "instance": inventory["instance"],
            "device_id": inventory["device_id"],
            "mpn": inventory["mpn"],
            "quantity": 1,
            "rail_bindings": [{
                "net": f"INDIRECT:{inventory['instance']}",
                "rail": indirect["rail"],
                "profile": indirect["profile"],
                "accounting": indirect["accounting"],
            }],
            "canonical_rails": [indirect["rail"]],
            "profiles": [indirect["profile"]],
            "accounting": [indirect["accounting"]],
            "disposition": "indirect_powered_consumer",
            "parameter_state": "candidate_current_seed_requires_applicability_review" if candidates else "explicit_parameter_extraction_required",
            "candidate_current_fields": candidates,
            "source": parameter["source"],
            "parameter_owner": "H3-R2.1.3",
        })

    external = []
    for row in contract["external_loads"]:
        external.append({
            **row,
            "parameter_state": "explicit_parameter_extraction_required",
            "source_state": "exact selected product or enforced port admission contract",
        })

    duplicate_uids = [uid for uid, count in Counter(row["instance_uid"] for row in lines).items() if count != 1]
    if duplicate_uids:
        errors.append(f"duplicate load lines: {duplicate_uids[:5]}")
    expected_keys = set(connected) | indirect_keys
    emitted_keys = {(row["project"], row["sheet"], row["reference"], row["instance"], row["device_id"]) for row in lines}
    missing = expected_keys - emitted_keys
    if missing:
        errors.append(f"unbound power-connected instances: {len(missing)}")
    source_missing = [row["id"] for row in lines if not row["source"].get("url")]
    if source_missing:
        errors.append(f"load lines without source URL: {source_missing[:5]}")

    dispositions = Counter(row["disposition"] for row in lines)
    rail_counts = Counter(rail for row in lines for rail in row["canonical_rails"])
    profile_counts = Counter(profile for row in lines for profile in row["profiles"])
    parameter_counts = Counter(row["parameter_state"] for row in lines)
    sources = {str(path.relative_to(REPO)): digest(path) for path in SOURCES}
    payload = json.dumps({"sources": sources, "lines": lines, "external": external}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "artifact": "H3-R2-load-binding",
        "marker": "H3-R2.1.2",
        "status": "pass" if not errors else "fail",
        "accepted_input": "H3-R2.1.1",
        "binding_sha256": hashlib.sha256(payload).hexdigest(),
        "source_sha256": sources,
        "policy": contract["binding_policy"],
        "load_lines": lines,
        "external_load_lines": external,
        "summary": {
            "power_connected_instances": len(expected_keys),
            "direct_power_connected_instances": len(connected),
            "indirect_powered_instances": len(indirect_keys),
            "bound_instance_lines": len(lines),
            "external_load_lines": len(external),
            "unbound_power_connected_instances": len(missing),
            "duplicate_instance_lines": len(duplicate_uids),
            "source_missing": len(source_missing),
            "dispositions": dict(sorted(dispositions.items())),
            "canonical_rail_bindings": dict(sorted(rail_counts.items())),
            "profile_bindings": dict(sorted(profile_counts.items())),
            "parameter_states": dict(sorted(parameter_counts.items())),
            "hidden_miscellaneous_allowances": 0,
            "reviewed_power_nets_required": len(contract["required_reviewed_power_nets"]),
            "reviewed_power_nets_missing": len(missing_reviewed_nets),
            "errors": len(errors),
        },
        "authorization": {
            "advance_to_h3_r2_1_3": not errors,
            "numeric_dc_pass_claim": False,
            "placement_or_routing": False,
            "purchasing": False,
            "fabrication": False,
        },
        "next": {"marker": "H3-R2.1.3", "action": "extract exact applicable current, DCR, leakage and effective-capacitance corners, then evaluate rail margins"},
        "errors": errors,
    }


def render_doc(result: dict, ru: bool) -> str:
    s = result["summary"]
    dispositions = "\n".join(f"| `{key}` | {value} |" for key, value in s["dispositions"].items())
    if ru:
        title = "# Привязка нагрузок питания R2"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Состояния](power-state-register.ru.md) · [English](power-load-binding.md)"
        intro = f"`H3-R2.1.2` прошёл структурное ревью: все `{s['power_connected_instances']}` устанавливаемых экземпляра, касающихся одной из учитываемых шин, получили ровно по одной явной строке. Добавлены `{s['external_load_lines']}` внешних load contracts. Непривязанных строк — `{s['unbound_power_connected_instances']}`, скрытых miscellaneous allowances — `{s['hidden_miscellaneous_allowances']}`."
        table_h = "## Что именно привязано"
        headers = "| Disposition | Строк |\n|---|---:|"
        boundary_h = "## Что ещё не является pass"
        boundary = "Это ревью полноты учёта, не численный DC-pass. Для каждой строки без применимого exact maximum `H3-R2.1.3` обязан извлечь параметр из закреплённого manufacturer source либо вернуть `unresolved_fail`. Child rails RP/codec/pack отмечены отдельно и не могут считаться второй раз поверх полного device total."
        next_text = "**Downstream-результат:** [`H3-R2.1.3`](power-rail-margins.ru.md) провёл worst-case ревью напряжения/тока шин, защит и установившегося нагрева; текущий маркер — `H3-R2.1.4`."
        evidence = "[Полный машинный реестр строк](../hardware/verification/generated/H3-R2-load-binding.json)."
    else:
        title = "# R2 power-load binding"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [States](power-state-register.md) · [Русский](power-load-binding.ru.md)"
        intro = f"`H3-R2.1.2` passes structural review: all `{s['power_connected_instances']}` fitted instances touching an accounted rail have exactly one explicit line. The register adds `{s['external_load_lines']}` external load contracts. Unbound lines: `{s['unbound_power_connected_instances']}`; hidden miscellaneous allowances: `{s['hidden_miscellaneous_allowances']}`."
        table_h = "## Bound surface"
        headers = "| Disposition | Lines |\n|---|---:|"
        boundary_h = "## What is not yet a pass"
        boundary = "This reviews accounting completeness, not numeric DC margin. For every line without an applicable exact maximum, `H3-R2.1.3` must extract the parameter from its bound manufacturer source or return `unresolved_fail`. RP/codec/pack child rails are explicit and cannot be counted again on top of the owning device total."
        next_text = "**Downstream result:** [`H3-R2.1.3`](power-rail-margins.md) completed worst-case rail voltage/current, protection and steady-thermal review; the current marker is `H3-R2.1.4`."
        evidence = "[Complete machine line register](../hardware/verification/generated/H3-R2-load-binding.json)."
    return "\n\n".join((title, nav, intro, table_h, headers + "\n" + dispositions, boundary_h, boundary, next_text, evidence)) + "\n"


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
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(result, False),
        DOC_RU: render_doc(result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"wrote H3-R2.1.2: {result['summary']['bound_instance_lines']} bound instances, {result['summary']['external_load_lines']} external lines")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: H3-R2.1.2 load binding is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
