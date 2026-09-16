#!/usr/bin/env python3
"""Read-only, additive routing-candidate checks; never DRC or qualification.

``complete`` refers only to the selected nets. Native KiCad is imported only
when grading; parsing and preservation helpers also work in ordinary Python.
The geometry signature hashes native integer coordinates without UUIDs, with
segment endpoints normalized so direction and item order do not affect it.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

if __package__:
    from .h6_r2_routing_workspace import matching_close
else:
    from h6_r2_routing_workspace import matching_close


LAYERS = {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"}
COPPER = {"segment", "via", "arc"}
UUID = re.compile(r'\(uuid\s+"([^"\s]+)"\)')
NET_FIELD = re.compile(r'\(net\s+("(?:\\.|[^"\\])*"|[0-9]+)\s*\)')


def forms(text: str) -> list[tuple[str, str]]:
    start = text.index("(kicad_pcb")
    end = matching_close(text, start)
    if text[:start].strip() or text[end:].strip():
        raise ValueError("extra content outside board")
    pos, result = start + len("(kicad_pcb"), []
    while pos < end - 1:
        if text[pos].isspace():
            pos += 1
            continue
        if text[pos] != "(":
            raise ValueError("unexpected top-level atom")
        stop = matching_close(text, pos)
        block = text[pos:stop]
        match = re.match(r'\(([^\s()]+)', block)
        if match is None:
            raise ValueError("missing form kind")
        result.append((match.group(1), block))
        pos = stop
    return result


def raw_copper(items: list[tuple[str, str]]) -> dict:
    rows = {}
    for kind, block in items:
        if kind not in COPPER:
            continue
        ids = UUID.findall(block)
        if len(ids) != 1 or ids[0] in rows:
            raise ValueError("missing/duplicate copper UUID")
        rows[ids[0]] = (kind, block)
    return rows


def _check(failures: Counter, ok: bool, category: str) -> None:
    if not ok:
        failures[category] += 1


def _raw_checks(old_text: str, new_text: str, failures: Counter) -> tuple[dict, dict]:
    old_forms, new_forms = forms(old_text), forms(new_text)
    old_raw, new_raw = raw_copper(old_forms), raw_copper(new_forms)
    _check(failures, [x for x in old_forms if x[0] not in COPPER] ==
           [x for x in new_forms if x[0] not in COPPER], "noncopper_raw_changed")
    for key, value in old_raw.items():
        _check(failures, new_raw.get(key) == value, "original_copper_raw_changed_or_missing")
    for text in (old_text, new_text):
        ids = UUID.findall(text)
        _check(failures, len(ids) == len(set(ids)), "global_duplicate_uuid")
    return old_raw, new_raw


def _validate_rows(rows: list[dict]) -> set[str]:
    if not isinstance(rows, list) or not rows:
        raise ValueError("selected rows must be a nonempty list")
    names = set()
    for row in rows:
        name, endpoints, remaining = (row[key] for key in
                                      ("kicad_net", "exact_ref_pads", "remaining_connections"))
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("selected net names must be nonempty and unique")
        if (not isinstance(endpoints, list) or not endpoints or
                any(not isinstance(pad, str) or not pad for pad in endpoints)):
            raise ValueError("exact_ref_pads must contain endpoint strings")
        if type(remaining) is not int or remaining < 0:
            raise ValueError("remaining_connections must be a nonnegative integer")
        names.add(name)
    return names


def _item_uuid(item) -> str:
    try:
        return item.m_Uuid.AsString()
    except AttributeError:
        return item.GetUuid().AsString()


def _xy(point) -> tuple[int, int]:
    return (point.x, point.y)


def _native_copper(board, pcbnew) -> dict:
    rows = {}
    for item in board.GetTracks():
        key = _item_uuid(item)
        if key in rows:
            raise ValueError("duplicate native copper UUID")
        sig = (item.GetClass(), item.GetNetname(), item.GetNetCode(),
               item.GetLayer(), item.IsLocked(), _xy(item.GetStart()), _xy(item.GetEnd()))
        if isinstance(item, pcbnew.PCB_VIA):
            sig += (item.GetWidth(item.TopLayer()), item.GetDrillValue(),
                    item.GetViaType(), item.TopLayer(), item.BottomLayer())
        else:
            sig += (item.GetWidth(),)
            if isinstance(item, pcbnew.PCB_ARC):
                sig += (_xy(item.GetMid()),)
        rows[key] = sig
    return rows


def _pads(board) -> Counter:
    return Counter((_item_uuid(fp), fp.GetReference(), _item_uuid(p), p.GetNumber(),
                    p.GetNetname(), p.GetNetCode())
                   for fp in board.GetFootprints() for p in fp.Pads())


def _remaining_by_net(board, pcbnew) -> dict[str, int]:
    """Same native pad-component count as remaining_for_net, in one board pass.

    Net zero (unassigned pads) is not an electrical net and is excluded.
    Native total unconnected count is checked separately, including dangling
    copper that has no pad endpoint.
    """
    components = {str(name): set() for name in board.GetNetsByName().keys() if str(name)}
    connectivity = board.GetConnectivity()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            name = pad.GetNetname()
            if not name:
                continue
            signature = tuple(sorted(_item_uuid(item) for item in
                                     connectivity.GetConnectedItems(pad)
                                     if isinstance(item, pcbnew.PAD))) or (_item_uuid(pad),)
            components.setdefault(name, set()).add(signature)
    return {name: max(0, len(groups) - 1) for name, groups in components.items()}


def _connectivity_checks(before: dict, after: dict, rows: list[dict], failures: Counter) -> dict:
    per_net = {name: [before.get(name, 0), after.get(name, 0)]
               for name in sorted(before.keys() | after.keys())}
    _check(failures, before.keys() == after.keys(), "native_net_inventory_changed")
    regressions = {name: pair for name, pair in per_net.items() if pair[1] > pair[0]}
    failures.update({"all_net_connectivity_regressed": len(regressions)} if regressions else {})
    for row in rows:
        _check(failures, row["kicad_net"] in before and
               before[row["kicad_net"]] == row["remaining_connections"], "allowlist_baseline_remaining")
    selected = [sum(counts.get(row["kicad_net"], 0) for row in rows) for counts in (before, after)]
    return dict(per_net=per_net, all_net_regressions=regressions,
                selected_remaining=selected, selected_complete=selected[1] == 0)


def _geometry_signature(items: list[tuple]) -> str:
    payload = json.dumps(sorted(items), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def drc_selected_open(report, uuid_nets, selected):
    """Independently bind CLI missing-connection findings to native item UUIDs.

    Unknown/malformed findings fail closed; descriptions are localized and are
    deliberately not parsed. Other nets may remain open in a scoped benchmark.
    """
    findings = report.get("unconnected_items")
    if not isinstance(findings, list):
        raise ValueError("Native DRC missing unconnected_items")
    selected_open = 0
    for finding in findings:
        items = finding.get("items") if isinstance(finding, dict) else None
        if not isinstance(items, list) or len(items) < 2:
            raise ValueError("Malformed DRC missing-connection finding")
        nets = []
        for item in items:
            uid = item.get("uuid") if isinstance(item, dict) else None
            if not isinstance(uid, str) or uid not in uuid_nets:
                raise ValueError("DRC missing-connection item is not bound to native copper/pads")
            nets.append(uuid_nets[uid])
        selected_open += bool(set(nets) & selected)
    return selected_open


def grade_candidate(baseline: Path, candidate: Path, rows: list[dict], expected_sha256: str) -> dict:
    """Grade additive copper without writing either file or any project settings.

    ``candidate_pass`` requires positive total and selected-net progress in
    addition to preservation, recipe and all-net connectivity checks. A passing
    candidate still needs separate DRC and electrical review. Malformed input or
    native load failures return a rejected report with an error string.
    """
    result = dict(candidate_pass=False, preservation_recipe_pass=False,
                  routing_status="rejected", drc_checked=False, electrically_qualified=False)
    failures = Counter()
    try:
        allowed = _validate_rows(rows)
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("expected_sha256 must be a lowercase SHA256 digest")
        old_bytes, new_bytes = baseline.read_bytes(), candidate.read_bytes()
        _check(failures, hashlib.sha256(old_bytes).hexdigest() == expected_sha256, "baseline_hash")
        old_raw, new_raw = _raw_checks(old_bytes.decode("utf-8"), new_bytes.decode("utf-8"), failures)

        import pcbnew  # type: ignore  # Deliberately lazy; caller selects native Python.

        old, new = pcbnew.LoadBoard(str(baseline)), pcbnew.LoadBoard(str(candidate))
        old.BuildConnectivity()
        new.BuildConnectivity()
        old_native, new_native = _native_copper(old, pcbnew), _native_copper(new, pcbnew)
        _check(failures, set(old_native) == set(old_raw) and set(new_native) == set(new_raw),
               "raw_native_copper_inventory")
        # KiCad may silently reassign a track to the net of a touching pad.
        # Native connectivity alone would then accept a mislabeled source file.
        for raw, native in ((old_raw, old_native), (new_raw, new_native)):
            for uid, (_, block) in raw.items():
                matches = NET_FIELD.findall(block)
                if len(matches) != 1 or uid not in native:
                    failures["raw_native_net_disagreement"] += 1
                    continue
                declared = json.loads(matches[0])
                expected = native[uid][1] if isinstance(declared, str) else native[uid][2]
                _check(failures, declared == expected, "raw_native_net_disagreement")
        for key, value in old_native.items():
            _check(failures, new_native.get(key) == value, "original_copper_native_changed_or_missing")
        _check(failures, _pads(old) == _pads(new), "native_pad_ref_net_changed")
        endpoints = defaultdict(list)
        for fp in old.GetFootprints():
            for pad in fp.Pads():
                endpoints[pad.GetNetname()].append(f"{fp.GetReference()}.{pad.GetNumber()}")
        for row in rows:
            _check(failures, sorted(endpoints[row["kicad_net"]]) == sorted(row["exact_ref_pads"]),
                   "allowlist_endpoints")

        added = set(new_raw) - set(old_raw)
        metrics = Counter(new_tracks=0, new_vias=0)
        length, geometry = 0, []
        for item in new.GetTracks():
            if _item_uuid(item) not in added:
                continue
            kind, name = new_raw[_item_uuid(item)][0], item.GetNetname()
            _check(failures, name in allowed, "new_net_outside_allowlist")
            if isinstance(item, pcbnew.PCB_VIA):
                metrics["new_vias"] += 1
                diameter, drill = item.GetWidth(item.TopLayer()), item.GetDrillValue()
                _check(failures, kind == "via" and item.GetViaType() == pcbnew.VIATYPE_THROUGH and
                       (item.TopLayer(), item.BottomLayer()) == (pcbnew.F_Cu, pcbnew.B_Cu) and
                       diameter == 400000 and drill == 200000, "new_via_recipe")
                geometry.append((kind, name, _xy(item.GetPosition()), diameter, drill,
                                 int(item.GetViaType()), new.GetLayerName(item.TopLayer()),
                                 new.GetLayerName(item.BottomLayer())))
            else:
                metrics["new_tracks"] += 1
                length += item.GetLength()
                start, end = sorted((_xy(item.GetStart()), _xy(item.GetEnd())))
                layer = new.GetLayerName(item.GetLayer())
                _check(failures, kind == "segment" and not isinstance(item, pcbnew.PCB_ARC) and
                       item.GetWidth() == 150000 and layer in LAYERS and start != end, "new_segment_recipe")
                geometry.append((kind, name, layer, item.GetWidth(), start, end,
                                 _xy(item.GetMid()) if isinstance(item, pcbnew.PCB_ARC) else ()))
        result.update(_connectivity_checks(_remaining_by_net(old, pcbnew),
                                           _remaining_by_net(new, pcbnew), rows, failures))
        before, after = (b.GetConnectivity().GetUnconnectedCount(False) for b in (old, new))
        _check(failures, after <= before, "total_connectivity_regressed")
        result["preservation_recipe_pass"] = not failures
        _check(failures, after < before and result["selected_remaining"][1] <
               result["selected_remaining"][0], "no_positive_progress")
        result.update(native_unconnected=[before, after], resolved_connections=before-after,
                      board_complete=after == 0, copper_objects=[len(old_raw), len(new_raw)],
                      **metrics, new_trace_length_mm=round(length / 1e6, 6),
                      added_geometry_signature=_geometry_signature(geometry), candidate_pass=not failures)
        if result["candidate_pass"]:
            result["routing_status"] = "complete" if result["selected_complete"] else "partial"
        elif set(failures) == {"no_positive_progress"}:
            result["routing_status"] = "no_progress"
    except Exception as exc:
        failures["input_or_native_error"] += 1
        result.update(error=f"{type(exc).__name__}: {exc}", preservation_recipe_pass=False)
    result["failures"] = dict(failures)
    return result
