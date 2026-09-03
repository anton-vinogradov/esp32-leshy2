#!/usr/bin/env python3
"""Validate a helper SES and import it into a disposable KiCad board copy.

This tool deliberately refuses a board that already contains copper tracks. It
is the H6.0.2 bootstrap guard; later manual routing must use a geometry-aware
delta checker instead of weakening this condition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
MAX_SPECCTRA_ROUNDING_NM = 100


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def session_nets(text: str) -> set[str]:
    matches = re.finditer(
        r'(?m)^      \(net (?:("(?:\\.|[^"\\])*")|([^\s()]+))',
        text,
    )
    names = set()
    for match in matches:
        if match.group(1):
            names.add(json.loads(match.group(1)))
        else:
            names.add(match.group(2))
    return names


def footprint_state(board) -> dict:
    return {
        footprint.GetReference(): (
            footprint.GetPosition().x,
            footprint.GetPosition().y,
            round(footprint.GetOrientation().AsDegrees(), 6),
            footprint.IsFlipped(),
        )
        for footprint in board.GetFootprints()
    }


def placement_rounding(before: dict, after: dict) -> tuple[list[str], int]:
    rounded = []
    max_delta = 0
    if set(before) != set(after):
        return sorted(set(before) ^ set(after)), 2
    for reference, old in before.items():
        new = after[reference]
        delta = max(abs(old[0] - new[0]), abs(old[1] - new[1]))
        if old[2:] != new[2:] or delta > MAX_SPECCTRA_ROUNDING_NM:
            return [reference], max(delta, MAX_SPECCTRA_ROUNDING_NM + 1)
        if delta:
            rounded.append(reference)
            max_delta = max(max_delta, delta)
    return rounded, max_delta


def restore_placement(board, state: dict, pcbnew) -> None:
    for footprint in board.GetFootprints():
        old = state[footprint.GetReference()]
        footprint.SetPosition(pcbnew.VECTOR2I(old[0], old[1]))


def expected_connection_count(board, net_names: set[str]) -> int:
    pad_counts = {name: 0 for name in net_names}
    for pad in board.GetPads():
        name = pad.GetNetname()
        if name in pad_counts:
            pad_counts[name] += 1
    missing = sorted(name for name, count in pad_counts.items() if count < 2)
    if missing:
        raise SystemExit(f"allowed nets have fewer than two physical pads: {missing[:10]}")
    return sum(count - 1 for count in pad_counts.values())


def unconnected_count(board) -> int:
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


def validate_and_import(
    workspace_dir: Path,
    project: str,
    session_path: Path,
    output_board: Path,
) -> dict:
    try:
        import pcbnew  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit("run with KiCad's bundled Python 3.9 runtime") from exc

    manifest_path = workspace_dir / "routing-workspace-manifest.json"
    manifest = load(manifest_path)
    audit = load(AUDIT)
    entries = [entry for entry in manifest["projects"] if entry["project"] == project]
    if len(entries) != 1:
        raise SystemExit(f"{project}: exactly one workspace manifest entry is required")
    entry = entries[0]
    board_path = ROOT / entry["board"]
    dsn_path = Path(entry["dsn"])
    if sha256(board_path) != entry["board_sha256"]:
        raise SystemExit(f"{project}: source board changed after DSN export")
    if sha256(dsn_path) != entry["dsn_sha256"]:
        raise SystemExit(f"{project}: disposable DSN changed after export")

    allowed_classes = set(manifest["allowed_classes"])
    allowed_nets = {
        row["kicad_net"]
        for row in audit["rows"]
        if row["project"] == project and row["routing_class"] in allowed_classes
    }
    proposed_nets = session_nets(session_path.read_text(encoding="utf-8"))
    prohibited = sorted(proposed_nets - allowed_nets)
    if prohibited:
        raise SystemExit(f"{project}: SES contains protected nets: {prohibited[:10]}")
    if not proposed_nets:
        raise SystemExit(f"{project}: SES contains no routed nets")

    board = pcbnew.LoadBoard(str(board_path))
    if list(board.GetTracks()):
        raise SystemExit(f"{project}: bootstrap importer requires a track-free source board")
    expected_connections = expected_connection_count(board, allowed_nets)
    source_unconnected_count = unconnected_count(board)
    before = footprint_state(board)
    if not pcbnew.ImportSpecctraSES(board, str(session_path)):
        raise SystemExit(f"{project}: KiCad rejected the SES")
    after = footprint_state(board)
    rounded, max_delta = placement_rounding(before, after)
    if max_delta > MAX_SPECCTRA_ROUNDING_NM:
        raise SystemExit(
            f"{project}: SES changed footprint placement beyond "
            f"{MAX_SPECCTRA_ROUNDING_NM} nm: {rounded[:10]}"
        )
    restore_placement(board, before, pcbnew)
    if footprint_state(board) != before:
        raise SystemExit(f"{project}: could not restore exact source footprint coordinates")
    candidate_unconnected_count = unconnected_count(board)
    resolved_connections = source_unconnected_count - candidate_unconnected_count
    remaining_connections = expected_connections - resolved_connections
    if resolved_connections < 0 or remaining_connections < 0:
        raise SystemExit(
            f"{project}: native connectivity changed impossibly; "
            f"expected={expected_connections}, resolved={resolved_connections}"
        )

    tracks = list(board.GetTracks())
    imported_nets = {track.GetNetname() for track in tracks}
    protected_imports = sorted(imported_nets - allowed_nets)
    if protected_imports:
        raise SystemExit(f"{project}: imported copper touches protected nets: {protected_imports[:10]}")
    if imported_nets != proposed_nets:
        missing = sorted(proposed_nets - imported_nets)
        extra = sorted(imported_nets - proposed_nets)
        raise SystemExit(f"{project}: SES/import net mismatch; missing={missing[:10]}, extra={extra[:10]}")
    routable_layers = set(manifest["routable_layers"])
    route_layers = {
        board.GetLayerName(track.GetLayer())
        for track in tracks
        if not isinstance(track, pcbnew.PCB_VIA)
    }
    forbidden_layers = sorted(route_layers - routable_layers)
    if forbidden_layers:
        raise SystemExit(f"{project}: imported traces use reserved layers: {forbidden_layers}")

    output_board.parent.mkdir(parents=True, exist_ok=True)
    if not pcbnew.SaveBoard(str(output_board), board):
        raise SystemExit(f"{project}: could not save disposable imported board")
    report = {
        "schema_version": 1,
        "artifact": "H6-R2 disposable routing-session import audit",
        "status": "pass",
        "project": project,
        "source_board": entry["board"],
        "source_board_sha256": entry["board_sha256"],
        "dsn_sha256": entry["dsn_sha256"],
        "session": str(session_path),
        "session_sha256": sha256(session_path),
        "output_board": str(output_board),
        "output_board_sha256": sha256(output_board),
        "allowed_classes": sorted(allowed_classes),
        "routable_layers": sorted(routable_layers),
        "used_trace_layers": sorted(route_layers),
        "allowed_net_count": len(allowed_nets),
        "expected_allowed_connection_count": expected_connections,
        "resolved_allowed_connection_count": resolved_connections,
        "remaining_allowed_connection_count": remaining_connections,
        "source_total_unconnected_count": source_unconnected_count,
        "candidate_total_unconnected_count": candidate_unconnected_count,
        "routed_net_count": len(imported_nets),
        "track_item_count": len(tracks),
        "via_count": sum(isinstance(track, pcbnew.PCB_VIA) for track in tracks),
        "placement_unchanged": True,
        "specctra_rounding_corrected_footprints": len(rounded),
        "maximum_corrected_rounding_nm": max_delta,
        "protected_net_import_count": 0,
    }
    report_path = output_board.with_suffix(".import-audit.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-dir", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--output-board", type=Path, required=True)
    args = parser.parse_args()
    report = validate_and_import(
        args.workspace_dir.resolve(),
        args.project,
        args.session.resolve(),
        args.output_board.resolve(),
    )
    print(
        f"H6-R2 routing session pass: {report['project']}; "
        f"{report['routed_net_count']} allowed nets; {report['track_item_count']} track items; "
        f"{report['via_count']} vias; {report['resolved_allowed_connection_count']} connections resolved; "
        f"{report['remaining_allowed_connection_count']} remain; placement unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
