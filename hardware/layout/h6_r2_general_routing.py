#!/usr/bin/env python3
"""Audit the accepted H6.0.2 GENERAL_CONTROL + OSCILLATOR routing bootstrap.

The checked-in PCB files are the routed authority.  This guard regenerates the
exact unrouted placement in memory, proves that routing did not change it, and
then verifies that every added track/via belongs only to the one class released
to the automatic helper.  A fresh KiCad CLI DRC report is required when writing
the audit; later ``--check`` runs bind that evidence to the unchanged board
hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

try:
    import pcbnew  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("run with KiCad's bundled Python runtime") from exc

try:
    from hardware.layout.h6_r2_placement import (
        build as build_placement,
        placement_signature_bytes,
        placement_signature_from_board_bytes,
    )
    from hardware.layout.h6_r2_routing_session import expected_connection_count
except ModuleNotFoundError:  # direct script execution from the repository root
    from h6_r2_placement import (
        build as build_placement,
        placement_signature_bytes,
        placement_signature_from_board_bytes,
    )
    from h6_r2_routing_session import expected_connection_count


ROOT = Path(__file__).resolve().parents[2]
POLICY_AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
FREEZE = ROOT / "hardware/layout/h6-r2-placement-freeze.json"
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-general-routing-audit.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
MECHANICAL_REFERENCES = {"MH1", "MH2", "MH3", "MH4"}
ACCEPTED_CLASSES = ("GENERAL_CONTROL", "OSCILLATOR")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def board_path(project: str) -> Path:
    return ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"


def unconnected_count(board) -> int:
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


def footprint_state(board) -> dict[str, tuple[int, int, float, str]]:
    return {
        footprint.GetReference(): (
            footprint.GetPosition().x,
            footprint.GetPosition().y,
            round(footprint.GetOrientationDegrees(), 3),
            "B.Cu" if footprint.IsFlipped() else "F.Cu",
        )
        for footprint in board.GetFootprints()
        if footprint.GetReference() not in MECHANICAL_REFERENCES
    }


def frozen_state(freeze: dict, project: str) -> dict[str, tuple[int, int, float, str]]:
    board = next(row for row in freeze["boards"] if row["project"] == project)
    return {
        row["reference"]: (
            row["footprint_anchor_nm"][0],
            row["footprint_anchor_nm"][1],
            row["rotation_deg"],
            row["side"],
        )
        for row in board["placements"]
    }


def drc_evidence(path: Path, project: str, board_sha256: str) -> tuple[dict, list[str]]:
    report = load(path)
    errors = []
    if Path(report.get("source", "")).name != f"{project}.kicad_pcb":
        errors.append(f"{project}: DRC source does not name the audited board")
    if report.get("violations"):
        errors.append(f"{project}: DRC has {len(report['violations'])} violations")
    if report.get("schematic_parity"):
        errors.append(
            f"{project}: DRC has {len(report['schematic_parity'])} schematic-parity errors"
        )
    return {
        "tool": "KiCad CLI pcb drc",
        "kicad_version": report.get("kicad_version"),
        "checked_board_sha256": board_sha256,
        "violation_count": len(report.get("violations", [])),
        "schematic_parity_error_count": len(report.get("schematic_parity", [])),
        "visible_unconnected_item_count": len(report.get("unconnected_items", [])),
        "note": "KiCad JSON caps the visible unconnected-item list; native connectivity below is exact.",
    }, errors


def retained_drc_evidence(existing: dict, project: str, board_sha256: str) -> tuple[dict, list[str]]:
    rows = [row for row in existing.get("boards", []) if row.get("project") == project]
    if len(rows) != 1 or "drc" not in rows[0]:
        return {}, [f"{project}: no retained DRC evidence; rerun --write with both reports"]
    evidence = rows[0]["drc"]
    errors = []
    if evidence.get("checked_board_sha256") != board_sha256:
        errors.append(f"{project}: retained DRC evidence belongs to another board hash")
    if evidence.get("violation_count") != 0:
        errors.append(f"{project}: retained DRC evidence is not violation-free")
    if evidence.get("schematic_parity_error_count") != 0:
        errors.append(f"{project}: retained DRC evidence has parity errors")
    return evidence, errors


def route_metrics(board, allowed_nets: set[str]) -> tuple[dict, list[str]]:
    errors = []
    tracks = list(board.GetTracks())
    vias = [track for track in tracks if isinstance(track, pcbnew.PCB_VIA)]
    traces = [track for track in tracks if not isinstance(track, pcbnew.PCB_VIA)]
    routed_nets = {track.GetNetname() for track in tracks}
    protected = sorted(routed_nets - allowed_nets)
    if protected:
        errors.append(f"tracks/vias touch protected nets: {protected[:10]}")
    trace_layers = {board.GetLayerName(track.GetLayer()) for track in traces}
    allowed_layers = {"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"}
    forbidden_layers = sorted(trace_layers - allowed_layers)
    if forbidden_layers:
        errors.append(f"traces use reserved layers: {forbidden_layers}")
    length_by_layer = defaultdict(float)
    width_counts = Counter()
    for track in traces:
        layer = board.GetLayerName(track.GetLayer())
        length_by_layer[layer] += pcbnew.ToMM(track.GetLength())
        width_counts[round(pcbnew.ToMM(track.GetWidth()), 6)] += 1
    via_geometries = Counter(
        (
            round(pcbnew.ToMM(via.GetWidth(via.GetLayer())), 6),
            round(pcbnew.ToMM(via.GetDrillValue()), 6),
        )
        for via in vias
    )
    ordinary_copper_zones = [zone for zone in board.Zones() if not zone.GetIsRuleArea()]
    if ordinary_copper_zones:
        errors.append(
            f"GENERAL_CONTROL bootstrap unexpectedly contains {len(ordinary_copper_zones)} copper zones"
        )
    return {
        "routed_net_count": len(routed_nets),
        "track_item_count": len(tracks),
        "trace_count": len(traces),
        "via_count": len(vias),
        "used_trace_layers": sorted(trace_layers),
        "trace_length_mm_by_layer": {
            layer: round(length, 4) for layer, length in sorted(length_by_layer.items())
        },
        "trace_width_counts": [
            {"width_mm": width, "count": count}
            for width, count in sorted(width_counts.items())
        ],
        "via_geometry_counts": [
            {"diameter_mm": diameter, "drill_mm": drill, "count": count}
            for (diameter, drill), count in sorted(via_geometries.items())
        ],
        "ordinary_copper_zone_count": len(ordinary_copper_zones),
        "protected_routed_net_count": len(protected),
    }, errors


def build(ui_drc: Path | None = None, rf_drc: Path | None = None) -> dict:
    policy = load(POLICY_AUDIT)
    freeze = load(FREEZE)
    placement_outputs, placement_audit = build_placement()
    existing = load(OUTPUT) if OUTPUT.exists() else {}
    supplied_drc = {"LESHY2-UI-R2": ui_drc, "LESHY2-RF-R2": rf_drc}
    board_rows = []
    all_errors = []
    for project in PROJECTS:
        path = board_path(project)
        board_sha = sha256(path)
        board = pcbnew.LoadBoard(str(path))
        errors = []

        actual_placement = footprint_state(board)
        expected_placement = frozen_state(freeze, project)
        if actual_placement != expected_placement:
            changed = sorted(
                reference
                for reference in set(actual_placement) | set(expected_placement)
                if actual_placement.get(reference) != expected_placement.get(reference)
            )
            errors.append(f"placement differs from exact freeze: {changed[:10]}")

        seed_bytes = placement_outputs[path]
        actual_signature = hashlib.sha256(placement_signature_bytes(project, board)).hexdigest()
        seed_signature = hashlib.sha256(
            placement_signature_from_board_bytes(project, seed_bytes)
        ).hexdigest()
        if actual_signature != seed_signature:
            errors.append("non-routing board structure differs from the exact placement seed")

        allowed_by_class = {
            routing_class: {
                row["kicad_net"]
                for row in policy["rows"]
                if row["project"] == project
                and row["routing_class"] == routing_class
            }
            for routing_class in ACCEPTED_CLASSES
        }
        allowed_nets = set().union(*allowed_by_class.values())
        metrics, metric_errors = route_metrics(board, allowed_nets)
        errors.extend(f"{project}: {message}" for message in metric_errors)
        expected_connections_by_class = {
            routing_class: expected_connection_count(board, nets)
            for routing_class, nets in allowed_by_class.items()
        }
        expected_connections = sum(expected_connections_by_class.values())
        candidate_unconnected = unconnected_count(board)
        with tempfile.TemporaryDirectory(prefix="leshy2-general-seed-") as directory:
            seed_path = Path(directory) / f"{project}.kicad_pcb"
            seed_path.write_bytes(seed_bytes)
            seed_unconnected = unconnected_count(pcbnew.LoadBoard(str(seed_path)))
        resolved_connections = seed_unconnected - candidate_unconnected
        remaining_connections = expected_connections - resolved_connections
        if remaining_connections != 0:
            errors.append(
                f"{project}: {remaining_connections} accepted H6.0.2 connections remain"
            )
        if metrics["routed_net_count"] != len(allowed_nets):
            errors.append(
                f"{project}: routed {metrics['routed_net_count']} of {len(allowed_nets)} allowed nets"
            )

        report_path = supplied_drc[project]
        if report_path is not None:
            drc, drc_errors = drc_evidence(report_path, project, board_sha)
        else:
            drc, drc_errors = retained_drc_evidence(existing, project, board_sha)
        errors.extend(drc_errors)

        row = {
            "project": project,
            "board": str(path.relative_to(ROOT)),
            "board_sha256": board_sha,
            "placement_signature_sha256": actual_signature,
            "placement_unchanged": actual_placement == expected_placement,
            "accepted_classes": list(ACCEPTED_CLASSES),
            "allowed_net_count_by_class": {
                routing_class: len(nets)
                for routing_class, nets in allowed_by_class.items()
            },
            "allowed_net_count": len(allowed_nets),
            "expected_allowed_connection_count_by_class": expected_connections_by_class,
            "expected_allowed_connection_count": expected_connections,
            "resolved_allowed_connection_count": resolved_connections,
            "remaining_allowed_connection_count": remaining_connections,
            "seed_total_unconnected_count": seed_unconnected,
            "routed_total_unconnected_count": candidate_unconnected,
            **metrics,
            "drc": drc,
            "errors": errors,
        }
        board_rows.append(row)
        all_errors.extend(errors)

    return {
        "schema_version": 1,
        "artifact": "H6-R2 accepted H6.0.2 routing bootstrap audit",
        "marker": "H6.0.2-R1",
        "status": "pass" if not all_errors else "fail",
        "sources": {
            "routing_policy_audit": str(POLICY_AUDIT.relative_to(ROOT)),
            "routing_policy_audit_sha256": sha256(POLICY_AUDIT),
            "placement_freeze": str(FREEZE.relative_to(ROOT)),
            "placement_freeze_sha256": sha256(FREEZE),
        },
        "scope": {
            "completed": list(ACCEPTED_CLASSES),
            "not_completed": ["SAFETY_CONTROL", "ANALOG_AUDIO_SENSE"],
            "reserved_reference_layers": ["In1.Cu", "In4.Cu"],
            "statement": "This is a routing bootstrap inside H6.0.2, not completion of the phase or of either PCB.",
        },
        "summary": {
            "board_count": len(board_rows),
            "allowed_net_count": sum(row["allowed_net_count"] for row in board_rows),
            "expected_allowed_connection_count": sum(
                row["expected_allowed_connection_count"] for row in board_rows
            ),
            "resolved_allowed_connection_count": sum(
                row["resolved_allowed_connection_count"] for row in board_rows
            ),
            "remaining_allowed_connection_count": sum(
                row["remaining_allowed_connection_count"] for row in board_rows
            ),
            "track_item_count": sum(row["track_item_count"] for row in board_rows),
            "via_count": sum(row["via_count"] for row in board_rows),
            "drc_violation_count": sum(row["drc"].get("violation_count", -1) for row in board_rows),
            "error_count": len(all_errors),
        },
        "boards": board_rows,
        "errors": all_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--ui-drc", type=Path)
    parser.add_argument("--rf-drc", type=Path)
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    if args.write and (args.ui_drc is None or args.rf_drc is None):
        parser.error("--write requires --ui-drc and --rf-drc from the current boards")
    if args.check and (args.ui_drc is not None or args.rf_drc is not None):
        parser.error("--check uses board-hash-bound DRC evidence from the generated audit")
    artifact = build(
        args.ui_drc.resolve() if args.ui_drc else None,
        args.rf_drc.resolve() if args.rf_drc else None,
    )
    data = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    elif not OUTPUT.exists() or OUTPUT.read_bytes() != data:
        raise SystemExit("stale H6 GENERAL_CONTROL routing audit; rerun --write with fresh DRC reports")
    print(
        f"H6-R2 H6.0.2 routing {artifact['status']}: "
        f"{artifact['summary']['resolved_allowed_connection_count']}/"
        f"{artifact['summary']['expected_allowed_connection_count']} connections; "
        f"{artifact['summary']['drc_violation_count']} DRC violations"
    )
    return 0 if artifact["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
