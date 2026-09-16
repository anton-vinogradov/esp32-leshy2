"""Read-only, copy-only repair planning; never launches an engine or DRC.

Native evidence is required before explicit collateral rip authority is emitted.
The original board, not the partial candidate, remains the preservation baseline.
Engine diagnostics are suggestions only; native connectivity defines the targets.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from .h6_r2_route_candidate import _native_copper, _validate_rows, grade_candidate


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _json_digest(value):
    try:
        return _digest(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                  allow_nan=False).encode())
    except (TypeError, ValueError) as exc:
        raise ValueError("Inputs must be finite JSON values") from exc


def _name(value):
    # KRT arguments are patterns. Refuse names that could widen their scope or
    # be interpreted as options; these reviewed cases use literal plain names.
    if (not isinstance(value, str) or not value or value[0] in "!-"
            or any(c in value for c in "*?[]")
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("Expected an exact non-pattern net name")
    return value


def _case_scope(case):
    if not isinstance(case, dict):
        raise ValueError("Case must be an object")
    project = case.get("project")
    if not isinstance(project, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", project):
        raise ValueError("Invalid case project")
    if not isinstance(case.get("id"), str) or not case["id"]:
        raise ValueError("Case id is required")
    try:
        selected = _validate_rows(case["nets"])
        for name in selected:
            _name(name)
        for row in case["nets"]:
            if row.get("project", project) != project:
                raise ValueError("Mixed-project scope is not supported")
        relative = f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
        expected = case["baseline_sha256"][relative]
    except (KeyError, TypeError) as exc:
        raise ValueError("Malformed reviewed case") from exc
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Expected original-board SHA256 is required")
    return selected, relative, expected


def plan_from_evidence(case, summary, evidence):
    """Pure policy gate over evidence produced by :func:`derive_repair_plan`.

    This does not establish native preservation by itself. Callers with files
    must use derive_repair_plan, which obtains and verifies the evidence.
    """
    selected, relative, expected = _case_scope(case)
    case_hash, summary_hash = _json_digest(case), _json_digest(summary)
    if not isinstance(summary, dict) or not isinstance(evidence, dict):
        raise ValueError("Summary and native evidence must be objects")
    if evidence.get("preservation_recipe_pass") is not True:
        raise ValueError("Native preservation/recipe proof is required")
    if evidence.get("baseline_sha256") != expected:
        raise ValueError("Original board differs from the reviewed baseline")
    candidate_hash = evidence.get("candidate_sha256")
    if not isinstance(candidate_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", candidate_hash):
        raise ValueError("Candidate SHA256 is required")
    maps = []
    for field in ("original_copper_by_net", "candidate_copper_by_net", "remaining_by_net"):
        mapping = evidence.get(field)
        if (not isinstance(mapping, dict) or not mapping
                or any(not isinstance(n, str) or type(v) is not int or v < 0
                       for n, v in mapping.items())):
            raise ValueError(f"Invalid native {field}")
        maps.append(mapping)
    original, candidate, remaining = maps
    known = set(original)
    if set(candidate) != known or set(remaining) != known or not selected <= known:
        raise ValueError("Native net inventories disagree with the reviewed scope")
    if any(candidate[n] < count for n, count in original.items()):
        raise ValueError("Original copper inventory was reduced")

    reported = set()
    for field in ("failed_single", "open_single", "failed_multipoint", "pad_pairs_open"):
        entries = summary.get(field, [])
        if not isinstance(entries, list):
            raise ValueError(f"Malformed {field}")
        for entry in entries:
            if field in ("failed_single", "open_single"):
                name = _name(entry)
            else:
                if not isinstance(entry, dict):
                    raise ValueError(f"Malformed {field} entry")
                name = _name(entry.get("net_name" if field == "failed_multipoint" else "net"))
            if name not in selected:
                raise ValueError("Reported failure is outside the selected scope: " + name)
            if not remaining[name]:
                raise ValueError("Engine failure is stale against native connectivity: " + name)
            reported.add(name)
    if not reported:
        raise ValueError("No valid engine failures")
    failed = {n for n in selected if remaining[n]}
    if any(original[n] for n in failed):
        raise ValueError("Repair target contains original copper")

    blockers = summary.get("blockers")
    if not isinstance(blockers, list):
        raise ValueError("Blocker evidence is required")
    eligible, excluded, links = set(), {}, set()
    for entry in blockers:
        if not isinstance(entry, dict):
            raise ValueError("Malformed blocker entry")
        target = _name(entry.get("net"))
        if target not in failed:
            raise ValueError("Blocker target is not a selected native failure: " + target)
        victims = entry.get("blocked_by")
        if not isinstance(victims, list):
            raise ValueError("Malformed blocked_by list")
        for victim in victims:
            if not isinstance(victim, dict):
                raise ValueError("Malformed blocker identity")
            name = _name(victim.get("net"))
            if name not in known:
                raise ValueError("Unknown blocker net: " + name)
            if name not in selected:
                excluded[name] = "outside_reviewed_scope"
            elif original[name]:
                excluded[name] = "contains_original_copper"
            elif not candidate[name]:
                excluded[name] = "no_candidate_copper"
            else:
                eligible.add(name)
                links.add((target, name))
    if not eligible:
        raise ValueError("No eligible new-only copper blockers")
    failed, eligible = sorted(failed), sorted(eligible)
    return {
        "schema_version": 1, "case": case["id"], "project": case["project"],
        "board_relative": relative, "candidate_only": True,
        "baseline_sha256": expected, "candidate_sha256": candidate_hash,
        "case_semantic_sha256": case_hash, "engine_summary_semantic_sha256": summary_hash,
        "original_native_copper_objects": sum(original.values()),
        "original_copper_preserved": True, "scope_widened": False,
        "failed_nets": failed, "rip_existing_nets": eligible,
        "unreported_native_open_nets": sorted(set(failed) - reported),
        "selected_remaining_before_repair": sum(remaining[n] for n in selected),
        "excluded_blockers": [{"net": n, "reason": excluded[n]} for n in sorted(excluded)],
        "blocker_links": [{"failed_net": a, "blocker_net": b} for a, b in sorted(links)],
        "router_scope_arguments": ["--nets", *failed, "--rip-existing-nets", *eligible],
        "required_environment": {n: "0" for n in (
            "KICAD_RIP_PREEXISTING", "KICAD_RECONCILE_RIP_ESCALATION",
            "KICAD_FINALIZE_RIP", "KICAD_PLANE_FINALIZE")},
        "acceptance": "Regrade against the immutable original board and full case; require no connectivity regression from the partial candidate, restored project/rules, native DRC/parity, ROI containment, and all selected connections complete before geometry acceptance.",
        "drc_checked": False, "electrically_qualified": False, "production_authorization": False,
    }


def derive_repair_plan(baseline: Path, candidate: Path, case: dict, summary: dict) -> dict:
    """Obtain native preservation/connectivity evidence without writing files."""
    import pcbnew  # type: ignore  # Caller chooses native KiCad Python.

    baseline, candidate = Path(baseline), Path(candidate)
    _, _, expected = _case_scope(case)
    original_bytes, candidate_bytes = baseline.read_bytes(), candidate.read_bytes()
    if _digest(original_bytes) != expected:
        raise ValueError("Original board differs from the reviewed baseline")
    grade = grade_candidate(baseline, candidate, case["nets"], expected)
    if not grade.get("candidate_pass") or not grade.get("preservation_recipe_pass"):
        raise ValueError("Partial candidate failed native preservation/recipe checks: "
                         + json.dumps(grade.get("failures", {}), sort_keys=True))
    old, new = pcbnew.LoadBoard(str(baseline)), pcbnew.LoadBoard(str(candidate))
    old.BuildConnectivity()
    new.BuildConnectivity()

    def counts(board):
        found = Counter({str(n): 0 for n in board.GetNetsByName().keys()})
        found.update(item[1] for item in _native_copper(board, pcbnew).values())
        # Zones are frozen by the grader's raw non-copper check. They still
        # count as copper here, so a zone-backed net can never gain rip rights.
        found.update(z.GetNetname() for z in board.Zones() if not z.GetIsRuleArea())
        return dict(found)

    remaining = {n: pair[1] for n, pair in grade["per_net"].items()}
    original, current = counts(old), counts(new)
    # KiCad exposes the empty net in its inventory; it has no electrical pads.
    for name in original.keys() | current.keys():
        remaining.setdefault(name, 0)
    if baseline.read_bytes() != original_bytes or candidate.read_bytes() != candidate_bytes:
        raise ValueError("Board changed during read-only native verification")
    return plan_from_evidence(case, summary, {
        "baseline_sha256": expected, "candidate_sha256": _digest(candidate_bytes),
        "preservation_recipe_pass": True, "original_copper_by_net": original,
        "candidate_copper_by_net": current, "remaining_by_net": remaining,
    })
