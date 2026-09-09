"""Finite interface-label completeness, independent of label placement generation.

The ledger/catalog identify physical interfaces; a separately reviewed contract
identifies their labels. Optional native snapshots prove that those labels are
real visible SilkS PCB_TEXT, not Fab drawings or renderer reference fallbacks.
This does not qualify typography clearance, assembly, electrical function or H6.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = "hardware/layout/h6-r2-interface-label-coverage.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
EXPECTED_INTERFACE_COUNTS = {PROJECTS[0]: 52, PROJECTS[1]: 24}
SILK_LAYERS = {"F.Silkscreen", "B.Silkscreen"}


def load_contract(root=ROOT):
    return json.loads((Path(root) / CONTRACT_PATH).read_text())


def is_interface(row, devices):
    """Catch additions by physical reference class OR actual catalog kind.

    IC buffers, internal thermistors and passive RF networks are not interfaces
    simply because their descriptions mention a receiver, speaker or connector.
    """
    if re.fullmatch(r"(?:J|SW|MK|LS|BT|TP)\d+", row.get("reference", "")):
        return True
    kind = devices.get(row.get("device_id"), {}).get("kind", "")
    return bool(re.search(
        r"(?:^|_)(?:receptacle|jack|socket|plug|connector|debug_header|"
        r"tact_switch|slide_switch|encoder|microphone|loudspeaker|holder|"
        r"testpoint|status_led)(?:_|$)", kind)
        or re.search(r"_(?:ir_(?:learning_)?receiver|ir_emitter|printed_pickup_loop)$", kind))


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _point(value):
    return isinstance(value, (list, tuple)) and len(value) == 2 and all(map(_number, value))


def _identity(project, label):
    return (project, label.get("instance"), label.get("reference"),
            label.get("text"), label.get("layer"), label.get("source_project", project))


def check_coverage(ledger_rows, devices, labels_by_project, native_snapshots=None,
                   contract=None, projects=None):
    """Return errors, never an assembly pass.

    ``devices`` is devices.json['devices']; label dicts use the labels() API.
    ``native_snapshots`` is project -> native_snapshot() result. ``projects``
    may explicitly select one board for audit_snapshot integration; the full
    ledger/contract inventory is still checked. Omitted native data gives only
    a semantic-plan result, never a native-coverage result.
    """
    contract = load_contract() if contract is None else contract
    selected = tuple(PROJECTS if projects is None else projects)
    errors = []

    def error(kind, **detail):
        errors.append({"kind": kind, **detail})

    result = {"status": "review_required", "native_checked": native_snapshots is not None,
              "required_interface_count": 0, "matched_interface_count": 0,
              "required_label_count": 0, "matched_label_count": 0,
              "native_matched_label_count": 0, "errors": errors,
              "production_release_authorized": False}
    if (not selected or len(selected) != len(set(selected)) or not set(selected) <= set(PROJECTS)
            or not isinstance(ledger_rows, list) or not isinstance(devices, dict)
            or not isinstance(labels_by_project, dict) or set(labels_by_project) != set(selected)):
        error("invalid_coverage_inputs")
        return result
    if (not isinstance(contract, dict) or contract.get("schema_version") != 1
            or contract.get("expected_interface_counts") != EXPECTED_INTERFACE_COUNTS
            or contract.get("production_release_authorized") is not False
            or not isinstance(contract.get("interfaces"), list)
            or not isinstance(contract.get("assembly_contexts"), list)):
        error("invalid_coverage_contract")
        return result

    actual = {}
    by_instance = {}
    for row in ledger_rows:
        key = (row.get("project"), row.get("reference"))
        owner = (row.get("project"), row.get("instance"))
        if key in actual or owner in by_instance:
            error("duplicate_ledger_identity", project=key[0], reference=key[1])
        actual[key] = row
        by_instance[owner] = row
        device = devices.get(row.get("device_id"))
        if not isinstance(device, dict) or row.get("mpn") != device.get("mpn"):
            error("ledger_catalog_identity_mismatch", project=key[0], reference=key[1])
    inferred = {key for key, row in actual.items() if is_interface(row, devices)}
    for project, count in EXPECTED_INTERFACE_COUNTS.items():
        if sum(key[0] == project for key in inferred) != count:
            error("physical_interface_count_mismatch", project=project, expected=count)

    records = contract["interfaces"] + contract["assembly_contexts"]
    keys = [(r.get("project"), r.get("reference")) for r in contract["interfaces"]]
    if len(keys) != len(set(keys)):
        error("duplicate_contract_interface")
    if set(keys) != inferred:
        error("interface_inventory_mismatch", missing=sorted(inferred-set(keys)), extra=sorted(set(keys)-inferred))
    all_record_keys = [(r.get("project"), r.get("reference")) for r in records]
    if len(all_record_keys) != len(set(all_record_keys)):
        error("duplicate_contract_owner")

    expected = Counter()
    optional = Counter()
    owners = {}
    for record in records:
        key = record.get("project"), record.get("reference")
        row = actual.get(key)
        if (row is None or any(row.get(k) != record.get(k) for k in ("instance", "device_id"))
                or devices.get(record.get("device_id"), {}).get("kind") != record.get("device_kind")):
            error("contract_ledger_identity_mismatch", project=key[0], reference=key[1])
        if not record.get("role") or not record.get("rationale") or record.get("component_side") not in {"F.Cu", "B.Cu"}:
            error("incomplete_interface_record", project=key[0], reference=key[1])
        requirements = record.get("labels")
        if (not isinstance(requirements, list) or not requirements
                or not any(not s.get("optional", False) for s in requirements)):
            error("interface_has_no_label_requirement", project=key[0], reference=key[1])
            continue
        for spec in requirements:
            project = spec.get("project", key[0])
            reference = spec.get("reference", key[1])
            source_project = spec.get("source_project", project)
            count = spec.get("count", 1)
            if (project not in PROJECTS or spec.get("layer") not in SILK_LAYERS
                    or not isinstance(spec.get("text"), str) or not spec["text"]
                    or type(count) is not int or count < 1
                    or type(spec.get("optional", False)) is not bool
                    or source_project != key[0]
                    or reference != (key[1] if project == key[0] else key[0][7:9]+":"+key[1])):
                error("invalid_label_requirement", project=key[0], reference=key[1])
                continue
            if project not in selected:
                continue
            identity = (project, record["instance"], reference, spec["text"], spec["layer"], source_project)
            if identity in expected or identity in optional:
                error("duplicate_label_requirement", identity=identity)
            (optional if spec.get("optional", False) else expected)[identity] += count
            owners[identity] = key

    observed = Counter()
    planned = []
    # These non-interface annotations retain their existing separate checks.
    auxiliary = {"board_legal_notice", "board_branding"}
    for project in selected:
        if not isinstance(labels_by_project[project], list):
            error("invalid_label_list", project=project)
            continue
        for label in labels_by_project[project]:
            if not isinstance(label, dict):
                error("invalid_label_record", project=project)
                continue
            if label.get("instance") in auxiliary and label.get("reference") is None:
                continue
            identity = _identity(project, label)
            observed[identity] += 1
            planned.append((project, label, identity))
            if not _point(label.get("at_mm")):
                error("invalid_label_position", identity=identity)
    for identity, count in expected.items():
        if observed[identity] != count:
            error("required_label_count_mismatch", identity=identity, expected=count, actual=observed[identity])
    for identity, count in observed.items():
        if identity not in expected and identity not in optional:
            error("unexpected_label_identity", identity=identity)
        elif identity in optional and count > optional[identity]:
            error("duplicate_optional_label", identity=identity)
    result["required_label_count"] = sum(expected.values())
    result["matched_label_count"] = sum(min(observed[key], count) for key, count in expected.items())
    # Count the physical owners whose required labels appear in this selected
    # output scope. UI includes the RF microphone's cross-board user label.
    selected_interfaces = {owners[i] for i in expected} & set(keys)
    result["required_interface_count"] = len(selected_interfaces)
    for key in selected_interfaces:
        required = [identity for identity in expected if owners[identity] == key]
        if required and all(observed[i] == expected[i] for i in required):
            result["matched_interface_count"] += 1

    if native_snapshots is not None:
        if not isinstance(native_snapshots, dict) or set(native_snapshots) != set(selected):
            error("native_snapshot_scope_mismatch")
        else:
            for project in selected:
                snap = native_snapshots[project]
                if snap.get("project") != project or not isinstance(snap.get("placements"), list) or not isinstance(snap.get("texts"), list):
                    error("invalid_native_snapshot", project=project)
                    continue
                if snap.get("errors") or snap.get("extraction_errors"):
                    error("native_snapshot_contains_errors", project=project)
                native = {}
                for row in snap["placements"]:
                    ref = row.get("reference")
                    if ref in native:
                        error("duplicate_native_reference", project=project, reference=ref)
                    native[ref] = row
                for record in records:
                    if record["project"] != project:
                        continue
                    row = native.get(record["reference"], {})
                    ledger = actual.get((project, record["reference"]), {})
                    if (row.get("instance") != record["instance"]
                            or row.get("side") != record["component_side"]
                            or row.get("footprint") != ledger.get("footprint")):
                        error("native_interface_identity_or_side_mismatch", project=project, reference=record["reference"])
                texts = snap["texts"]
                used = set()
                names = {(i[3], i[4]) for i in set(expected) | set(optional) if i[0] == project}
                for target_project, label, identity in planned:
                    if target_project != project or identity not in owners:
                        continue
                    matches = [i for i, t in enumerate(texts)
                               if t.get("text") == label["text"] and t.get("layer") == label["layer"]
                               and _point(t.get("at_mm")) and _point(label.get("at_mm"))
                               and all(abs(a-b) <= .00001 for a, b in zip(t["at_mm"], label["at_mm"]))]
                    if len(matches) != 1 or matches[0] in used:
                        error("native_label_missing_or_duplicate", identity=identity)
                        continue
                    index = matches[0]
                    used.add(index)
                    t = texts[index]
                    if t.get("visible") is not True or t.get("mirrored") is not (label["layer"] == "B.Silkscreen"):
                        error("native_label_hidden_or_unreadable", identity=identity)
                    elif identity in expected:
                        result["native_matched_label_count"] += 1
                for i, t in enumerate(texts):
                    if (t.get("text"), t.get("layer")) in names and i not in used:
                        error("extra_native_interface_label", project=project, text=t.get("text"))
    if not errors:
        result["status"] = "pass_scoped_native" if native_snapshots is not None else "pass_scoped_semantic_plan"
    return result
