#!/usr/bin/env python3
"""Regenerate and verify reviewed manual H6.0.3 copper.

The placement generator remains the immutable source of component positions.
This layer adds only explicitly reviewed routes from the manual-copper contract;
automatic helpers may suggest geometry, but they never write the live boards.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from collections import defaultdict
from pathlib import Path

import pcbnew  # type: ignore

from h6_r2_placement import build as build_placement


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "hardware/layout/h6-r2-manual-copper.json"
POLICY_PATH = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
ROUTING_CONTRACT_PATH = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT_PATH = ROOT / "hardware/layout/generated/H6-R2-manual-copper-audit.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
# A finite reviewed experiment, not permission to replay arbitrary autorouter
# output. Keep complete net paths: a matching basename in another sheet is not
# the same electrical endpoint. Adding another net requires a source review.
REVIEWED_GENERAL_PROPOSALS = frozenset({
    ("LESHY2-UI-R2", "NRF0_TX_LED_A", "/UI_11_STORAGE_CONTROLS_INDICATORS/NRF0_TX_LED_A"),
    ("LESHY2-UI-R2", "S3_TX_LED_A", "/UI_11_STORAGE_CONTROLS_INDICATORS/S3_TX_LED_A"),
})
REVIEWED_PROPOSAL_MODE = "automatic_helper_allowed_then_manual_review"
REVIEWED_PROPOSAL_LAYERS = frozenset({"F.Cu", "In2.Cu", "In3.Cu", "B.Cu"})
# The current DSN recipe in h6_r2_routing_workspace.class_block uses 150 um
# clearance and Via[0-5]_400:200_um. These are recipe constraints, NOT a claim
# that the candidate meets clearances: fresh native DRC remains mandatory.
REVIEWED_PROPOSAL_CLEARANCE_MM = 0.15
REVIEWED_PROPOSAL_VIA_MM = (0.4, 0.2)


def proposal_geometry_sha256(route: dict) -> str:
    """Bind the hand-review decision to its exact net and explicit geometry."""
    payload = {key: route[key] for key in (
        "project", "canonical_net", "kicad_net", "routing_class", "segments", "vias",
    )}
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _finite_number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _proposal_point(value) -> bool:
    return isinstance(value, list) and len(value) == 2 and all(_finite_number(v) for v in value)


def validate_reviewed_proposal(route: dict, policy: dict, project: str,
                               routing_contract: dict | None) -> None:
    """Fail closed before mutating a board; this is not a DRC/promotion gate.

    A reviewer must supply the literal decision AND its geometry hash. The
    caller separately preserves existing copper/placement, verifies native
    connectivity and runs fresh DRC before promoting any proposed copper.
    """
    label = route.get("id", "<missing route id>")

    def reject(message):
        raise ValueError(f"{label}: reviewed GENERAL_CONTROL proposal {message}")

    identity = (project, route.get("canonical_net"), route.get("kicad_net"))
    if route.get("project") != project or identity not in REVIEWED_GENERAL_PROPOSALS:
        reject("is outside the finite UI LED allow-list")
    if (route.get("routing_class") != "GENERAL_CONTROL"
            or any(policy.get(key) != route.get(key)
                   for key in ("project", "canonical_net", "kicad_net", "routing_class"))
            or policy.get("route_mode") != REVIEWED_PROPOSAL_MODE):
        reject("does not have the exact current policy binding/mode")
    if not isinstance(route.get("id"), str) or not route["id"].strip():
        reject("needs a non-empty route id")
    if not isinstance(route.get("reason"), str) or not route["reason"].strip():
        reject("needs a written review reason")
    if type(route.get("expected_resolved_connections")) is not int or route["expected_resolved_connections"] != 1:
        reject("must resolve exactly one connection")
    if not isinstance(routing_contract, dict):
        reject("requires the current routing contract")
    general = routing_contract.get("classes", {}).get("GENERAL_CONTROL", {})
    helper = routing_contract.get("automatic_helper", {})
    if (general.get("route_mode") != REVIEWED_PROPOSAL_MODE
            or type(general.get("nominal_track_width_mm")) not in (int, float)
            or general["nominal_track_width_mm"] != 0.15
            or helper.get("allowed_classes") != ["GENERAL_CONTROL"]
            or sorted(helper.get("routable_layers", [])) != sorted(REVIEWED_PROPOSAL_LAYERS)
            or sorted(helper.get("reserved_reference_layers", [])) != ["In1.Cu", "In4.Cu"]):
        reject("requires the reviewed 0.15 mm / four signal-layer policy recipe")
    review = route.get("reviewed_proposal")
    if (not isinstance(review, dict)
            or set(review) != {"decision", "minimum_clearance_mm", "geometry_sha256"}
            or review.get("decision") != "hand-reviewed proposal"
            or not _finite_number(review.get("minimum_clearance_mm"))
            or review["minimum_clearance_mm"] != REVIEWED_PROPOSAL_CLEARANCE_MM):
        reject("requires an explicit hand-review decision and the 0.15 mm clearance recipe")
    segments, vias = route.get("segments"), route.get("vias")
    if (not isinstance(segments, list) or not segments or not isinstance(vias, list)
            or any(key in route for key in ("path_mm", "layer", "width_mm"))):
        reject("requires explicit segments and vias without a competing shorthand path")
    for segment in segments:
        if (not isinstance(segment, dict)
                or set(segment) != {"layer", "width_mm", "start_mm", "end_mm"}
                or segment.get("layer") not in REVIEWED_PROPOSAL_LAYERS
                or not _finite_number(segment.get("width_mm"))
                or segment["width_mm"] != general["nominal_track_width_mm"]
                or not _proposal_point(segment.get("start_mm"))
                or not _proposal_point(segment.get("end_mm"))):
            reject("has unsupported segment geometry, width or layer")
        if math.dist(segment["start_mm"], segment["end_mm"]) < 1e-6:
            reject("has a zero-length segment")
    for via in vias:
        if (not isinstance(via, dict)
                or not {"at_mm", "diameter_mm", "drill_mm"} <= set(via)
                or not set(via) <= {"at_mm", "diameter_mm", "drill_mm", "type"}
                or via.get("type", "through") != "through"
                or not _proposal_point(via.get("at_mm"))
                or not _finite_number(via.get("diameter_mm"))
                or not _finite_number(via.get("drill_mm"))
                or (via["diameter_mm"], via["drill_mm"]) != REVIEWED_PROPOSAL_VIA_MM):
            reject("requires through vias with the exact 0.4 / 0.2 mm recipe")
    if review.get("geometry_sha256") != proposal_geometry_sha256(route):
        reject("geometry changed since its hand-review decision")


def preflight_reviewed_proposals(routes: list[dict], policy_rows: dict,
                                routing_contract: dict | None,
                                project: str | None = None) -> None:
    """Check the complete proposed batch before adding even its first trace."""
    seen_nets, seen_ids = set(), set()
    all_ids = [route.get("id") for route in routes]
    for route in routes:
        if route.get("routing_class") != "GENERAL_CONTROL" and "reviewed_proposal" not in route:
            continue
        scope = project if project is not None else route.get("project")
        key = (scope, route.get("kicad_net"))
        validate_reviewed_proposal(route, policy_rows.get(key, {}), scope, routing_contract)
        if key in seen_nets or route["id"] in seen_ids or all_ids.count(route["id"]) != 1:
            raise ValueError(f"{route['id']}: duplicate reviewed GENERAL_CONTROL proposal net/id")
        seen_nets.add(key)
        seen_ids.add(route["id"])


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def board_path(project: str) -> Path:
    return ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"


def item_uuid(item) -> str:
    try:
        return item.m_Uuid.AsString()
    except Exception:
        return item.GetUuid().AsString()


def remaining_for_net(board, net_name: str) -> int:
    board.BuildConnectivity()
    connectivity = board.GetConnectivity()
    components = set()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetname() != net_name:
                continue
            connected = connectivity.GetConnectedItems(pad)
            signature = tuple(
                sorted(
                    item_uuid(item)
                    for item in connected
                    if isinstance(item, pcbnew.PAD)
                )
            ) or (item_uuid(pad),)
            components.add(signature)
    return max(0, len(components) - 1)


def copper_signature(board) -> list[tuple]:
    rows = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            at = item.GetPosition()
            rows.append(
                (
                    "via",
                    item.GetNetname(),
                    round(pcbnew.ToMM(at.x), 6),
                    round(pcbnew.ToMM(at.y), 6),
                    round(pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)), 6),
                    round(pcbnew.ToMM(item.GetDrillValue()), 6),
                )
            )
        else:
            start, end = item.GetStart(), item.GetEnd()
            a = (round(pcbnew.ToMM(start.x), 6), round(pcbnew.ToMM(start.y), 6))
            b = (round(pcbnew.ToMM(end.x), 6), round(pcbnew.ToMM(end.y), 6))
            rows.append(
                (
                    "track",
                    item.GetNetname(),
                    board.GetLayerName(item.GetLayer()),
                    round(pcbnew.ToMM(item.GetWidth()), 6),
                    min(a, b),
                    max(a, b),
                )
            )
    return sorted(rows)


def add_routes(
    board,
    routes: list[dict],
    policy_rows: dict[tuple[str, str], dict],
    project: str,
    rf_transitions: dict,
    routing_contract: dict | None = None,
) -> list[dict]:
    preflight_reviewed_proposals(routes, policy_rows, routing_contract, project)
    results = []
    for route in routes:
        net_name = route["kicad_net"]
        policy = policy_rows.get((project, net_name))
        if policy is None:
            raise ValueError(f"{route['id']}: net is absent from routing policy")
        if policy["routing_class"] != route["routing_class"]:
            raise ValueError(f"{route['id']}: routing-class mismatch")
        if (route["routing_class"] != "GENERAL_CONTROL"
                and policy["route_mode"] not in {"manual_only", "plane_or_local_pour_manual"}):
            raise ValueError(
                f"{route['id']}: reviewed manifest only accepts manual routes and "
                "explicit local ground joins"
            )
        net = board.FindNet(net_name)
        if net is None:
            raise ValueError(f"{route['id']}: missing board net {net_name}")
        if "segments" in route:
            segments = route["segments"]
        else:
            path = [tuple(map(float, point)) for point in route["path_mm"]]
            if len(path) < 2:
                raise ValueError(f"{route['id']}: path needs at least two points")
            segments = [
                {
                    "layer": route["layer"],
                    "width_mm": route["width_mm"],
                    "start_mm": start,
                    "end_mm": end,
                }
                for start, end in zip(path, path[1:])
            ]
        if not segments:
            raise ValueError(f"{route['id']}: route has no segments")
        vias = route.get("vias", [])
        if route["routing_class"] in {"RF_CONTROLLED", "USB_DIFFERENTIAL"} and vias:
            allowed = set(rf_transitions["allowed_canonical_nets"])
            if route["canonical_net"] not in allowed:
                raise ValueError(
                    f"{route['id']}: controlled-impedance via is not an approved edge-launch transition"
                )
            maximum = int(rf_transitions["maximum_through_vias_per_net"])
            if len(vias) > maximum:
                raise ValueError(
                    f"{route['id']}: {len(vias)} signal vias exceed the approved maximum {maximum}"
                )
            expected_geometry = (
                float(rf_transitions["signal_via_diameter_mm"]),
                float(rf_transitions["signal_via_drill_mm"]),
            )
            for via_row in vias:
                geometry = (
                    float(via_row["diameter_mm"]),
                    float(via_row["drill_mm"]),
                )
                if geometry != expected_geometry:
                    raise ValueError(
                        f"{route['id']}: controlled-impedance via {geometry} does not match "
                        f"approved {expected_geometry} geometry"
                    )
        before = remaining_for_net(board, net_name)
        lengths = []
        layers = set()
        widths = set()
        for segment in segments:
            layer_name = segment["layer"]
            layer = board.GetLayerID(layer_name)
            if layer < 0:
                raise ValueError(f"{route['id']}: missing layer {layer_name}")
            start = tuple(map(float, segment["start_mm"]))
            end = tuple(map(float, segment["end_mm"]))
            if math.dist(start, end) < 1e-6:
                raise ValueError(f"{route['id']}: zero-length segment")
            width = float(segment["width_mm"])
            track = pcbnew.PCB_TRACK(board)
            track.SetNetCode(net.GetNetCode())
            track.SetLayer(layer)
            track.SetWidth(pcbnew.FromMM(width))
            track.SetStart(pcbnew.VECTOR2I_MM(*start))
            track.SetEnd(pcbnew.VECTOR2I_MM(*end))
            board.Add(track)
            lengths.append(math.dist(start, end))
            layers.add(layer_name)
            widths.add(width)
        for via_row in vias:
            if via_row.get("type", "through") != "through":
                raise ValueError(f"{route['id']}: only through vias are supported")
            at = tuple(map(float, via_row["at_mm"]))
            diameter = float(via_row["diameter_mm"])
            drill = float(via_row["drill_mm"])
            if drill <= 0 or diameter <= drill:
                raise ValueError(f"{route['id']}: invalid via diameter/drill")
            via = pcbnew.PCB_VIA(board)
            via.SetNetCode(net.GetNetCode())
            via.SetPosition(pcbnew.VECTOR2I_MM(*at))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetWidth(pcbnew.FromMM(diameter))
            via.SetDrill(pcbnew.FromMM(drill))
            board.Add(via)
        after = remaining_for_net(board, net_name)
        resolved = before - after
        expected = route["expected_resolved_connections"]
        if resolved != expected:
            raise ValueError(
                f"{route['id']}: resolved {resolved} connections, expected {expected}"
            )
        results.append(
            {
                "id": route["id"],
                "project": project,
                "canonical_net": route["canonical_net"],
                "kicad_net": net_name,
                "routing_class": route["routing_class"],
                "route_mode": policy["route_mode"],
                "layers": sorted(layers),
                "widths_mm": sorted(widths),
                "segment_count": len(segments),
                "via_count": len(vias),
                "length_mm": round(sum(lengths), 4),
                "resolved_connections": resolved,
                "reason": route["reason"],
            }
        )
        if "reviewed_proposal" in route:
            results[-1]["reviewed_proposal"] = dict(route["reviewed_proposal"])
    return results


def build() -> tuple[dict[str, object], dict]:
    contract = load(CONTRACT_PATH)
    policy = load(POLICY_PATH)
    routing_contract = load(ROUTING_CONTRACT_PATH)
    rf_transitions = routing_contract["classes"]["RF_CONTROLLED"]["reviewed_outer_layer_transitions"]
    policy_rows = {
        (row["project"], row["kicad_net"]): row for row in policy["rows"]
    }
    # Validate before project filtering: a typo/foreign project must not make a
    # reviewed route disappear silently from the replay or its audit.
    preflight_reviewed_proposals(contract["routes"], policy_rows, routing_contract)
    placement_outputs, placement_audit = build_placement()
    board_outputs: dict[Path, bytes] = {}
    route_results = []
    board_rows = []
    with tempfile.TemporaryDirectory(prefix="leshy2-h603-copper-") as directory:
        temp_root = Path(directory)
        for project in PROJECTS:
            output = board_path(project)
            staged = temp_root / f"{project}.kicad_pcb"
            staged.write_bytes(placement_outputs[output])
            board = pcbnew.LoadBoard(str(staged))
            project_routes = [
                route for route in contract["routes"] if route["project"] == project
            ]
            rows = add_routes(board, project_routes, policy_rows, project, rf_transitions,
                              routing_contract)
            route_results.extend(rows)
            if not pcbnew.SaveBoard(str(staged), board):
                raise SystemExit(f"{project}: save failed")
            data = staged.read_bytes()
            board_outputs[output] = data
            board_rows.append(
                {
                    "project": project,
                    "board": str(output.relative_to(ROOT)),
                    "route_count": len(rows),
                    "segment_count": sum(row["segment_count"] for row in rows),
                    "via_count": sum(row["via_count"] for row in rows),
                    "resolved_connection_count": sum(
                        row["resolved_connections"] for row in rows
                    ),
                    "copper_signature": copper_signature(board),
                }
            )
    audit = {
        "schema_version": 1,
        "artifact": "H6.0.3 reviewed manual-copper audit",
        "marker": contract["marker"],
        "status": "pass",
        "sources": {
            "contract": str(CONTRACT_PATH.relative_to(ROOT)),
            "contract_sha256": sha256(CONTRACT_PATH),
            "routing_policy": str(POLICY_PATH.relative_to(ROOT)),
            "routing_policy_sha256": sha256(POLICY_PATH),
            "routing_contract": str(ROUTING_CONTRACT_PATH.relative_to(ROOT)),
            "routing_contract_sha256": sha256(ROUTING_CONTRACT_PATH),
            "placement_status": placement_audit["status"],
        },
        "summary": {
            "route_count": len(route_results),
            "segment_count": sum(row["segment_count"] for row in route_results),
            "resolved_connection_count": sum(
                row["resolved_connections"] for row in route_results
            ),
            "via_count": sum(row["via_count"] for row in route_results),
            "manual_only_route_count": sum(
                row["route_mode"] == "manual_only" for row in route_results
            ),
            "local_ground_join_route_count": sum(
                row["route_mode"] == "plane_or_local_pour_manual"
                for row in route_results
            ),
            "reviewed_general_control_proposal_route_count": sum(
                "reviewed_proposal" in row for row in route_results
            ),
        },
        "boards": board_rows,
        "routes": route_results,
        "authorization": contract["authorization"],
        "errors": [],
    }
    return {**board_outputs, AUDIT_PATH: json.dumps(audit, indent=2, ensure_ascii=False).encode() + b"\n"}, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh-derived", action="store_true",
                      help="verify native copper, then refresh only the derived audit; never rewrite a PCB")
    args = parser.parse_args()
    outputs, audit = build()
    if args.write:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    else:
        stale = []
        expected_boards = {
            Path(row["board"]): row["copper_signature"] for row in audit["boards"]
        }
        for relative, expected in expected_boards.items():
            path = ROOT / relative
            if not path.exists():
                stale.append(f"{relative}: missing")
                continue
            actual = copper_signature(pcbnew.LoadBoard(str(path)))
            if actual != [tuple(row) for row in expected]:
                stale.append(f"{relative}: copper signature differs")
        expected_audit = outputs[AUDIT_PATH]
        if not args.refresh_derived and (not AUDIT_PATH.exists() or AUDIT_PATH.read_bytes() != expected_audit):
            stale.append(str(AUDIT_PATH.relative_to(ROOT)))
        if stale:
            raise SystemExit("stale H6 manual-copper outputs: " + ", ".join(stale))
        if args.refresh_derived:
            AUDIT_PATH.write_bytes(expected_audit)
    print(
        f"H6-R2 manual copper {audit['status']}: "
        f"{audit['summary']['route_count']} routes; "
        f"{audit['summary']['segment_count']} segments; "
        f"{audit['summary']['resolved_connection_count']} resolved connections"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
