#!/usr/bin/env python3
"""Audit and render the five H6 R2 microcoax service corridors."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/layout/h6-r2-microcoax-service.json"
PLACEMENT = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
PLACEMENT_CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
H1 = ROOT / "hardware/product-design/h1-r2-placement.json"
H3 = ROOT / "hardware/verification/generated/H3-R2-rf-coexistence.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-microcoax-service-audit.json"
SVG = ROOT / "docs/images/h6-r2-microcoax-service.svg"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_distance(a: list[float], b: list[float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def point_segment_distance(point: tuple[float, float], a: list[float], b: list[float]) -> float:
    vx, vy = b[0] - a[0], b[1] - a[1]
    wx, wy = point[0] - a[0], point[1] - a[1]
    vv = vx * vx + vy * vy
    if vv == 0:
        return math.hypot(wx, wy)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / vv))
    return math.hypot(point[0] - (a[0] + t * vx), point[1] - (a[1] + t * vy))


def orient(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_intersect(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    values = (orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b))
    return values[0] * values[1] <= 0 and values[2] * values[3] <= 0


def segment_rect_distance(a: list[float], b: list[float], bbox: dict) -> float:
    x0, x1 = map(float, bbox["x"])
    y0, y1 = map(float, bbox["y"])
    aa, bb = tuple(a), tuple(b)
    if x0 <= aa[0] <= x1 and y0 <= aa[1] <= y1:
        return 0.0
    if x0 <= bb[0] <= x1 and y0 <= bb[1] <= y1:
        return 0.0
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    if any(segments_intersect(aa, bb, c, d) for c, d in edges):
        return 0.0
    point_to_rect = lambda p: math.hypot(max(x0 - p[0], 0, p[0] - x1), max(y0 - p[1], 0, p[1] - y1))
    return min(
        point_to_rect(aa),
        point_to_rect(bb),
        *(point_segment_distance(corner, a, b) for corner in corners),
    )


def boxes_overlap(a: dict, b: dict) -> bool:
    return not (
        a["x"][1] <= b["x"][0]
        or a["x"][0] >= b["x"][1]
        or a["y"][1] <= b["y"][0]
        or a["y"][0] >= b["y"][1]
    )


def point_rect_distance(point: tuple[float, float], bbox: dict) -> float:
    x0, x1 = map(float, bbox["x"])
    y0, y1 = map(float, bbox["y"])
    return math.hypot(max(x0 - point[0], 0, point[0] - x1), max(y0 - point[1], 0, point[1] - y1))


def expanded_box(centre: list[float], size: list[float], margin: float) -> dict:
    return {
        "x": [centre[0] - size[0] / 2 - margin, centre[0] + size[0] / 2 + margin],
        "y": [centre[1] - size[1] / 2 - margin, centre[1] + size[1] / 2 + margin],
    }


def farthest_window_distance(window: dict, point: list[float]) -> float:
    return max(
        math.hypot(x - point[0], y - point[1])
        for x in window["x"]
        for y in window["y"]
    )


def native_point(source: dict, local: list[float]) -> list[float]:
    """KiCad back-side placement reflects local Y before footprint rotation."""
    x, y = local
    if source["side"] == "B.Cu":
        y = -y
    angle = math.radians(-float(source["rotation_deg"]))
    anchor = source["footprint_anchor_mm"]
    return [round(anchor[0] + x * math.cos(angle) - y * math.sin(angle), 6),
            round(anchor[1] + x * math.sin(angle) + y * math.cos(angle), 6)]


def native_box(source: dict, local: dict) -> dict:
    corners = [native_point(source, [x, y]) for x in local["x"] for y in local["y"]]
    return {"x": [min(p[0] for p in corners), max(p[0] for p in corners)],
            "y": [min(p[1] for p in corners), max(p[1] for p in corners)]}


def corridor_geometry(row: dict) -> tuple[list[list[float]], float, float | None]:
    """Return sampled centreline, a length upper bound and analytic planar radius."""
    if "corridor_quadratic_control_mm" not in row:
        points = row["corridor_points_mm"]
        if "corridor_fillet_radius_mm" in row:
            return fillet_corridor(points, float(row["corridor_fillet_radius_mm"]), row.get("corridor_corner_radii_mm", {}))
        return points, sum(point_distance(a, b) for a, b in zip(points, points[1:])), None
    start, control, end = row["source_reference_mm"], row["corridor_quadratic_control_mm"], row["board_connector_mm"]
    count = 128  # even: the midpoint is the saddle; upper bound uses subcurve control polygons
    at = lambda t: [(1-t)**2*start[i]+2*t*(1-t)*control[i]+t*t*end[i] for i in range(2)]
    velocity = lambda t: [2*((1-t)*(control[i]-start[i])+t*(end[i]-control[i])) for i in range(2)]
    points = [at(i/count) for i in range(count+1)]
    upper = 0.0
    for i in range(count):
        a, b = points[i:i+2]
        v = velocity(i/count)
        q = [a[j]+v[j]/(2*count) for j in range(2)]
        upper += point_distance(a, q)+point_distance(q, b)
    v = velocity(0)
    acceleration = [2*(end[i]-2*control[i]+start[i]) for i in range(2)]
    norm = sum(x*x for x in acceleration)
    t = max(0.0, min(1.0, -sum(v[i]*acceleration[i] for i in range(2))/norm)) if norm else 0.0
    cross = abs(v[0]*acceleration[1]-v[1]*acceleration[0])
    radius = math.hypot(*velocity(t))**3/cross if cross else math.inf
    return points, upper, radius


def fillet_corridor(vertices: list[list[float]], radius: float, overrides: dict) -> tuple[list[list[float]], float, float | None]:
    """Replace corners with tangent circular arcs; sample with <=10 nm sagitta.

    The arc length is analytic. Clearance checks subtract the sampling tolerance
    so a chord cannot conceal a collision of the actual curved cable envelope.
    """
    trims = [0.0] * len(vertices)
    corners = {}
    for i in range(1, len(vertices)-1):
        a, c, b = vertices[i-1:i+2]
        before, after = point_distance(a, c), point_distance(c, b)
        if min(before, after) <= 1e-9:
            raise ValueError("duplicate corridor vertices")
        u = [(c[j]-a[j])/before for j in range(2)]
        v = [(b[j]-c[j])/after for j in range(2)]
        angle = math.acos(max(-1.0, min(1.0, sum(u[j]*v[j] for j in range(2)))))
        if angle < 1e-9:
            continue
        r = float(overrides.get(str(i), radius))
        if r <= 0 or angle >= math.pi-1e-6:
            raise ValueError("invalid radius or reversing corridor corner")
        trims[i] = r*math.tan(angle/2)
        start = [c[j]-u[j]*trims[i] for j in range(2)]
        end = [c[j]+v[j]*trims[i] for j in range(2)]
        sign = 1.0 if u[0]*v[1]-u[1]*v[0] > 0 else -1.0
        centre = [start[0]-sign*u[1]*r, start[1]+sign*u[0]*r]
        corners[i] = (start, end, centre, sign*angle, r)
    for i in range(len(vertices)-1):
        if trims[i]+trims[i+1] > point_distance(vertices[i], vertices[i+1])+1e-8:
            raise ValueError(f"radius tangent lengths do not fit corridor segment {i}")
    result = [vertices[0]]
    length = 0.0
    radii = []
    for i in range(1, len(vertices)-1):
        if i not in corners:
            continue
        start, end, centre, sweep, r = corners[i]
        length += point_distance(result[-1], start) + abs(sweep)*r
        result.append(start)
        # An even sample count includes the corner's true arc midpoint.
        count = max(2, 2*math.ceil(abs(sweep)/(4*math.acos(1-1e-5/r))))
        angle = math.atan2(start[1]-centre[1], start[0]-centre[0])
        result.extend([[centre[0]+r*math.cos(angle+sweep*j/count),
                        centre[1]+r*math.sin(angle+sweep*j/count)] for j in range(1, count)])
        result.append(end)
        radii.append(r)
    length += point_distance(result[-1], vertices[-1])
    result.append(vertices[-1])
    return result, length, min(radii) if radii else math.inf


def landing_obstacles(board: dict, support_instance: str | None = None) -> list[tuple[str, dict]]:
    """A front-mounted edge-launch connector also occupies the inner face at its lands."""
    obstacles = []
    for row in board["placements"]:
        if row["side"] == "B.Cu" and row["instance"] != support_instance:
            obstacles.append((row["instance"], row["courtyard_bbox_mm"]))
        elif row["side"] == "F.Cu":
            obstacles.extend((row["instance"] + ":opposite-face-land", box)
                             for box in row.get("opposite_face_keepout_bboxes_mm", []))
    return obstacles


def corridor_sampling_error(row: dict) -> float:
    if "corridor_fillet_radius_mm" in row:
        return 1e-5
    if "corridor_quadratic_control_mm" in row:
        a, q, b = row["source_reference_mm"], row["corridor_quadratic_control_mm"], row["board_connector_mm"]
        return math.hypot(*(2*(b[i]-2*q[i]+a[i]) for i in range(2)))/(8*128**2)
    return 0.0


def evaluate(contract: dict, placement: dict, placement_contract: dict, h1: dict, h3: dict) -> dict:
    errors: list[str] = []
    board = next(row for row in placement["boards"] if row["project"] == "LESHY2-UI-R2")
    placed = {row["instance"]: row for row in board["placements"]}
    expected = h1["antenna_bank_optimization"]["microcoax_by_path"]
    h3_paths = {row["path"]: row for row in h3["microcoax"]["paths"]}
    constraints = contract["common_constraints"]
    corridor_half_width = float(constraints["corridor_width_mm"]) / 2
    required_display_distance = corridor_half_width + float(constraints["minimum_corridor_edge_clearance_mm"])
    exclusions = constraints["display_exclusions"]
    saddle = constraints["retention_saddle"]
    saddle_centres: list[list[float]] = []
    path_results: list[dict] = []
    mounting = placement_contract["mechanical"]["mounting_holes"]
    mounting_centres = [tuple(point) for point in mounting["centres_mm"]]
    mounting_keepout_radius = float(mounting["head_keepout_radius_mm"])

    for row in contract["paths"]:
        path = row["path"]
        destination = placed.get(row["board_connector_instance"])
        if destination is None:
            errors.append(f"{path}: board connector is absent from native placement")
            continue
        datum = constraints["board_connector_datum"]
        if destination["footprint"] != datum["footprint"]:
            errors.append(f"{path}: board connector footprint has no reviewed mating-axis datum")
        actual_destination = native_point(destination, datum["axis_local_mm"])
        if any(abs(a - b) > 1e-6 for a, b in zip(actual_destination, row["board_connector_mm"])):
            errors.append(f"{path}: board connector mating axis differs from native placement")

        selected = expected.get(path)
        if selected is None:
            errors.append(f"{path}: cable is absent from accepted H1 selection")
        elif selected["mpn"] != row["cable_mpn"] or float(selected["length_mm"]) != float(row["selected_length_mm"]):
            errors.append(f"{path}: cable identity or length differs from accepted H1 selection")

        try:
            points, curve_length_upper, planar_radius = corridor_geometry(row)
        except ValueError as error:
            errors.append(f"{path}: {error}")
            continue
        sampling_error = corridor_sampling_error(row)
        if points[0] != row["source_reference_mm"]:
            errors.append(f"{path}: corridor does not start at its source reference")
        if points[-1] != row["board_connector_mm"]:
            errors.append(f"{path}: corridor does not end at its board connector")
        remainder = sum(point_distance(a, b) for a, b in zip(points[1:], points[2:]))
        if row["source_kind"] == "published_corner_window":
            source = placed.get(row["source_instance"])
            if source is None:
                errors.append(f"{path}: source module is absent from native placement")
                continue
            window = row["source_access_window_mm"]
            local_window = row.get("source_access_window_local_mm")
            if local_window is None:
                errors.append(f"{path}: source window has no footprint-local geometry")
            else:
                actual_window = native_box(source, local_window)
                if any(abs(actual_window[axis][i] - window[axis][i]) > 1e-6 for axis in ("x", "y") for i in (0, 1)):
                    errors.append(f"{path}: source access window differs from native placement transform")
            body = source["courtyard_bbox_mm"]
            if not (
                body["x"][0] <= window["x"][0] <= window["x"][1] <= body["x"][1]
                and body["y"][0] <= window["y"][0] <= window["y"][1] <= body["y"][1]
            ):
                errors.append(f"{path}: Ebyte connector access window leaves the module courtyard")
            conservative_length = curve_length_upper + farthest_window_distance(window, points[1]) - point_distance(points[0], points[1])
            source_basis = "farthest point of published-corner access window"
            actual_source_reference = row["source_reference_mm"]
        else:
            source = placed.get(row["source_instance"])
            if source is None:
                errors.append(f"{path}: source module is absent from native placement")
                continue
            local_axis = row.get("source_axis_local_mm")
            if local_axis is None:
                errors.append(f"{path}: exact module axis has no footprint-local coordinates")
                continue
            actual_source_reference = native_point(source, local_axis)
            if any(abs(a - b) > 1e-6 for a, b in zip(actual_source_reference, row["source_reference_mm"])):
                errors.append(f"{path}: source connector axis differs from native placement")
            conservative_length = curve_length_upper
            source_basis = "exact module connector axis"

        support = row.get("retention_support", {"kind": "pcb_solder_mask"})
        vertical_allowance = 0.0
        transition_span = 0.0
        if support["kind"] == "module_shield":
            height = float(support["surface_height_max_mm"])
            radius = float(support["vertical_transition_radius_mm"])
            # Two opposing circular arcs make a zero-slope height transition.
            # Budget one full board-to-shield rise at each end, conservatively.
            angle = math.acos(1-height/(2*radius))
            transition_span = 2*radius*math.sin(angle)
            vertical_allowance = 2*(2*radius*angle-transition_span)
            conservative_length += vertical_allowance
            occupied = height + float(constraints["cable_outer_diameter_mm"]) + float(saddle["maximum_finished_height_above_local_cable_mm"])
            if occupied > float(constraints["enclosure_clearance"]["route_prism_height_above_ui_inner_mm"]):
                errors.append(f"{path}: shield-supported cable exceeds the reserved height")
        if planar_radius is not None and planar_radius < float(constraints["formed_bend_radius_target_mm"]):
            errors.append(f"{path}: planar curve misses the formed bend-radius target")

        reserve = float(row["selected_length_mm"]) - conservative_length
        if reserve < float(constraints["minimum_relaxed_length_reserve_mm"]):
            errors.append(f"{path}: conservative relaxed reserve is only {reserve:.3f} mm")

        display_clearance = min(
            segment_rect_distance(a, b, exclusion["bbox_mm"])
            for a, b in zip(points, points[1:])
            for exclusion in exclusions
        ) - sampling_error
        if display_clearance < required_display_distance:
            errors.append(f"{path}: corridor enters the display slot/ZIF keepout")

        clip = row["retention_saddle_centre_mm"]
        saddle_centres.append(clip)
        clip_box = expanded_box(clip, saddle["clear_landing_size_mm"], float(saddle["courtyard_margin_mm"]))
        support_instance = support.get("instance") if support["kind"] == "module_shield" else None
        clip_hits = [name for name, box in landing_obstacles(board, support_instance) if boxes_overlap(clip_box, box)]
        if support_instance:
            support_row = placed[support_instance]
            support_box = native_box(support_row, support["safe_flat_local_bbox_mm"])
            if not all(support_box[axis][0] <= clip_box[axis][0] <= clip_box[axis][1] <= support_box[axis][1] for axis in ("x", "y")):
                clip_hits.append("outside-verified-shield-landing")
        board_bbox = contract["coordinate_system"]["board_bbox_mm"]
        if not all(board_bbox[axis][0] <= clip_box[axis][0] <= clip_box[axis][1] <= board_bbox[axis][1] for axis in ("x", "y")):
            clip_hits.append("outside-board")
        exclusion_hits = [
            exclusion["id"] for exclusion in exclusions if boxes_overlap(clip_box, exclusion["bbox_mm"])
        ]
        if clip_hits or exclusion_hits:
            errors.append(f"{path}: retention landing collision: {clip_hits + exclusion_hits}")

        route_mechanical_clearance = min(
            point_segment_distance(centre, a, b) - mounting_keepout_radius - corridor_half_width
            for a, b in zip(points, points[1:])
            for centre in mounting_centres
        ) - sampling_error
        clip_mechanical_clearance = min(
            point_rect_distance(
                centre,
                expanded_box(clip, saddle["clear_landing_size_mm"], float(saddle["courtyard_margin_mm"])),
            )
            - mounting_keepout_radius
            for centre in mounting_centres
        )
        if route_mechanical_clearance < 0:
            errors.append(f"{path}: cable corridor enters a stop or screw keepout")
        if clip_mechanical_clearance < 0:
            errors.append(f"{path}: retention saddle enters a stop or screw keepout")

        clip_index = min(range(len(points)), key=lambda i: point_distance(points[i], clip))
        if point_distance(points[clip_index], clip) > 1e-6:
            errors.append(f"{path}: retention saddle is not on the cable centreline")
        distance_before_clip = sum(point_distance(a, b) for a, b in zip(points[:clip_index], points[1 : clip_index + 1]))
        distance_after_clip = sum(point_distance(a, b) for a, b in zip(points[clip_index:], points[clip_index + 1 :]))
        minimum_free = float(constraints["connector_free_length_mm"])
        if min(distance_before_clip, distance_after_clip) < minimum_free:
            errors.append(f"{path}: retention saddle is too close to a connector")
        if min(distance_before_clip, distance_after_clip) < transition_span:
            errors.append(f"{path}: shield height transition does not fit the connector-free length")

        h3_row = h3_paths[path]
        if float(row["selected_length_mm"]) != float(h3_row["length_mm"]):
            errors.append(f"{path}: selected length differs from reviewed H3 path")

        path_results.append(
            {
                "path": path,
                "source_basis": source_basis,
                "source_reference_mm": actual_source_reference,
                "board_connector_mm": actual_destination,
                "cable_mpn": row["cable_mpn"],
                "selected_length_mm": float(row["selected_length_mm"]),
                "conservative_corridor_length_mm": round(conservative_length, 3),
                "minimum_relaxed_reserve_mm": round(reserve, 3),
                "minimum_display_exclusion_distance_mm": round(display_clearance, 3),
                "minimum_mechanical_keepout_clearance_mm": round(route_mechanical_clearance, 3),
                "retention_saddle_centre_mm": clip,
                "retention_landing_clear": not clip_hits and not exclusion_hits,
                "retention_support": support["kind"],
                "vertical_transition_length_allowance_mm": round(vertical_allowance, 3),
                "minimum_planar_bend_radius_mm": round(planar_radius, 3) if planar_radius is not None and math.isfinite(planar_radius) else None,
                "curve_sampling_error_bound_mm": round(sampling_error, 6),
                "planar_radius_scope": "nominal source-window centre; all actual source positions pending H6.0.7" if row["source_kind"] == "published_corner_window" else "fixed source and destination axes",
                "retention_mechanical_keepout_clearance_mm": round(clip_mechanical_clearance, 3),
                "source_free_length_mm": round(distance_before_clip, 3),
                "board_connector_free_length_mm": round(distance_after_clip, 3),
            }
        )

    if len({tuple(row) for row in saddle_centres}) != len(contract["paths"]):
        errors.append("retention saddle centres are not unique")

    antenna = contract["antenna_solder_inspection"]
    windows: list[dict] = []
    for board_name, ports in placement_contract["antenna_ports"].items():
        centres = sorted((float(x), name) for name, (x, _y) in ports.items())
        if len(centres) != int(antenna["ports_per_board"]):
            errors.append(f"{board_name}: antenna inspection count is not five")
        for (left, _), (right, _) in zip(centres, centres[1:]):
            gap = right - left - float(antenna["window_width_mm"])
            if gap < float(antenna["minimum_gap_between_adjacent_windows_mm"]):
                errors.append(f"{board_name}: adjacent antenna inspection windows are too close")
        for x, name in centres:
            windows.append({"board": board_name, "instance": name, "centre_x_mm": x})

    minimum_reserve = min(row["minimum_relaxed_reserve_mm"] for row in path_results)
    minimum_display_clearance = min(row["minimum_display_exclusion_distance_mm"] for row in path_results)
    minimum_mechanical_clearance = min(row["minimum_mechanical_keepout_clearance_mm"] for row in path_results)
    return {
        "schema_version": 1,
        "artifact": "H6-R2 microcoax service audit",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "source_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (CONTRACT, PLACEMENT, PLACEMENT_CONTRACT, H1, H3)
        },
        "summary": {
            "path_count": len(path_results),
            "thirty_mm_paths": sum(row["selected_length_mm"] == 30.0 for row in path_results),
            "sixty_mm_paths": sum(row["selected_length_mm"] == 60.0 for row in path_results),
            "retention_saddles": len(saddle_centres),
            "antenna_solder_windows": len(windows),
            "minimum_relaxed_reserve_mm": round(minimum_reserve, 3),
            "minimum_display_exclusion_distance_mm": round(minimum_display_clearance, 3),
            "minimum_mechanical_keepout_clearance_mm": round(minimum_mechanical_clearance, 3),
            "nominal_planar_radius_paths": sum(row["minimum_planar_bend_radius_mm"] is not None for row in path_results),
            "all_source_positions_planar_radius_verified": False,
            "source_window_radius_validation_pending": [row["path"] for row in contract["paths"] if row["source_kind"] == "published_corner_window"],
            "routing_may_start": not errors and contract["authorization"]["routing_start"],
        },
        "paths": path_results,
        "antenna_solder_windows": windows,
        "enclosure_clearance": constraints["enclosure_clearance"],
        "residual_physical_evidence": [
            "H6.0.7: validate R6 forming and the full corridor envelope for actual Ebyte axes throughout the selected source windows; current circular arcs use window centres",
            "confirm received E01 IPEX axes remain inside the published-corner service windows",
            "dry-fit all five received cable assemblies and confirm the 6-mm formed-radius target without connector preload",
            "recheck exact opposed-body and enclosure clearance from the assembled STEP in H6.0.7",
            "measure complete RF feeds during H8 bring-up"
        ],
        "errors": errors,
    }


def render(contract: dict, placement: dict, audit: dict) -> str:
    esc = html.escape
    board = next(row for row in placement["boards"] if row["project"] == "LESHY2-UI-R2")
    placed = {row["instance"]: row for row in board["placements"]}
    origin_x, origin_y, scale = 70.0, 150.0, 8.2
    colours = {
        "N24-0": "#0f766e",
        "S3-2G4": "#2563eb",
        "N24-1": "#7c3aed",
        "C5-2G4/5": "#dc2626",
        "N24-2": "#ea580c",
    }

    def sx(value: float) -> float:
        return origin_x + value * scale

    def sy(value: float) -> float:
        return origin_y + value * scale

    def text(x: float, y: float, value: str, size: float = 15, weight: str = "normal", anchor: str = "start", colour: str = "#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter,Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1460" height="910" viewBox="0 0 1460 910" data-marker="H6.0.3-R1" data-view="microcoax-service">',
        '<rect width="1460" height="910" fill="#ffffff"/>',
        text(70, 54, "Leshy2 - five relaxed microcoax service corridors", 31, "700"),
        text(70, 86, "Actual H6 footprint coordinates - one removable tape saddle per cable - ZIF and display slot stay accessible", 16, "500", colour="#526076"),
        text(origin_x, 126, "UI PCB - inner face - antenna edge and upper service volume", 17, "700", colour="#1d4ed8"),
        f'<rect x="{sx(0)}" y="{sy(0)}" width="{80*scale}" height="{62*scale}" rx="14" fill="#f8fafc" stroke="#334155" stroke-width="3"/>',
    ]

    for instance in ("s3", "c5", "nrf0", "nrf1", "nrf2", "display_connector"):
        row = placed[instance]
        bbox = row["courtyard_bbox_mm"]
        x, y = sx(bbox["x"][0]), sy(bbox["y"][0])
        w = (bbox["x"][1] - bbox["x"][0]) * scale
        h = (bbox["y"][1] - bbox["y"][0]) * scale
        is_display = instance == "display_connector"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="{"#fee2e2" if is_display else "#e2e8f0"}" stroke="{"#dc2626" if is_display else "#64748b"}" stroke-width="2"/>')
        if instance == "s3":
            parts.append(text(x + 10, y + 20, "S3 / " + row["reference"], 13, "700", colour="#334155"))
        else:
            parts.append(text(x + w / 2, y + h / 2 + 5, "ZIF" if is_display else row["reference"], 13, "700", "middle", "#991b1b" if is_display else "#334155"))

    for exclusion in contract["common_constraints"]["display_exclusions"]:
        bbox = exclusion["bbox_mm"]
        parts.append(f'<rect x="{sx(bbox["x"][0]):.1f}" y="{sy(bbox["y"][0]):.1f}" width="{(bbox["x"][1]-bbox["x"][0])*scale:.1f}" height="{(bbox["y"][1]-bbox["y"][0])*scale:.1f}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="7 5"/>')

    inspection_radius = float(contract["common_constraints"]["connector_inspection_radius_mm"])
    for row in contract["paths"]:
        colour = colours[row["path"]]
        points, _, _ = corridor_geometry(row)
        polyline = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in points)
        corridor_width = float(contract["common_constraints"]["corridor_width_mm"]) * scale
        cable_width = float(contract["common_constraints"]["cable_outer_diameter_mm"]) * scale
        parts.append(f'<polyline points="{polyline}" fill="none" stroke="{colour}" stroke-opacity="0.16" stroke-width="{corridor_width:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
        parts.append(f'<polyline points="{polyline}" fill="none" stroke="{colour}" stroke-width="{cable_width:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
        if "source_access_window_mm" in row:
            bbox = row["source_access_window_mm"]
            parts.append(f'<rect x="{sx(bbox["x"][0]):.1f}" y="{sy(bbox["y"][0]):.1f}" width="{(bbox["x"][1]-bbox["x"][0])*scale:.1f}" height="{(bbox["y"][1]-bbox["y"][0])*scale:.1f}" fill="none" stroke="{colour}" stroke-width="2" stroke-dasharray="5 4"/>')
        for endpoint in (row["source_reference_mm"], row["board_connector_mm"]):
            parts.append(f'<circle cx="{sx(endpoint[0]):.1f}" cy="{sy(endpoint[1]):.1f}" r="{inspection_radius*scale:.1f}" fill="none" stroke="{colour}" stroke-width="1.7" stroke-dasharray="5 4"/>')
            parts.append(f'<circle cx="{sx(endpoint[0]):.1f}" cy="{sy(endpoint[1]):.1f}" r="5" fill="#ffffff" stroke="{colour}" stroke-width="3"/>')
        clip = row["retention_saddle_centre_mm"]
        w, h = contract["common_constraints"]["retention_saddle"]["clear_landing_size_mm"]
        parts.append(f'<rect x="{sx(clip[0]-w/2):.1f}" y="{sy(clip[1]-h/2):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" rx="4" fill="#fef3c7" fill-opacity="0.92" stroke="#b45309" stroke-width="2"/>')
        parts.append(text(sx(clip[0]), sy(clip[1]) + 4, "S" if row.get("retention_support", {}).get("kind") == "module_shield" else "T", 11, "700", "middle", "#92400e"))

    parts.extend([
        text(80, 690, "T = 5 x 3 mm removable tape on clear PCB solder mask", 13, "600", colour="#92400e"),
        text(80, 714, "S = same tape on the documented flat S3 shield; keep its rim clear", 13, "600", colour="#92400e"),
        text(80, 739, "S3: native B-side connector below shield; gentle curve to upper U.FL", 13, "500", colour="#1d4ed8"),
        text(80, 764, "4.7 mm cable-height reservation includes shield, cable and tape", 13, "500", colour="#1d4ed8"),
        text(80, 789, "All five nominal curves: R >= 6 mm; Ebyte source-window forming", 13, "500", colour="#92400e"),
        text(80, 811, "remains an explicit H6.0.7 check at the actual connector axes", 13, "500", colour="#92400e"),
        text(760, 145, "DO NOT GUESS AN IPEX AXIS FOR THE THREE LONG PATHS", 14, "700", colour="#1d4ed8"),
        text(760, 180, "The Ebyte drawing puts IPEX in one corner but gives no centre dimension.", 14),
        text(760, 205, "Dashed source windows enclose that entire published corner.", 14),
        text(760, 230, "Length is checked from the farthest window point, not the drawn dot.", 14),
        text(760, 275, "ROUTE RESULT", 14, "700", colour="#1d4ed8"),
    ])

    y = 308
    for row in audit["paths"]:
        colour = colours[row["path"]]
        parts.append(f'<circle cx="776" cy="{y-5}" r="6" fill="{colour}"/>')
        parts.append(text(795, y, row["path"], 14, "700", colour=colour))
        parts.append(text(930, y, f"{row['selected_length_mm']:.0f} mm cable", 13, "600"))
        parts.append(text(1060, y, f"route <= {row['conservative_corridor_length_mm']:.2f} mm", 13))
        parts.append(text(1240, y, f"reserve {row['minimum_relaxed_reserve_mm']:.2f} mm", 13, "700", colour="#166534"))
        y += 38

    parts.extend([
        text(760, 525, "ASSEMBLY / ACCESS", 14, "700", colour="#1d4ed8"),
        '<circle cx="775" cy="555" r="14" fill="#2563eb"/>',
        text(775, 560, "1", 14, "700", "middle", "#ffffff"),
        text(805, 560, "Continuity-check and mate both ends vertically.", 14),
        '<circle cx="775" cy="598" r="14" fill="#2563eb"/>',
        text(775, 603, "2", 14, "700", "middle", "#ffffff"),
        text(805, 603, "Form a visible relaxed bow; never pull on a plug.", 14),
        '<circle cx="775" cy="641" r="14" fill="#2563eb"/>',
        text(775, 646, "3", 14, "700", "middle", "#ffffff"),
        text(805, 646, "Apply one removable saddle without flattening the cable.", 14),
        '<circle cx="775" cy="684" r="14" fill="#2563eb"/>',
        text(775, 689, "4", 14, "700", "middle", "#ffffff"),
        text(805, 689, "Inspect all 10 microcoax mates and 10 SMA solder windows.", 14),
        text(760, 750, "ENCLOSURE RULE", 14, "700", colour="#1d4ed8"),
        text(760, 783, "No rib, stop, screw, adhesive or loose hardware enters a corridor", 14),
        text(760, 808, "or its 6-mm connector inspection circle. The 11-mm sandwich", 14),
        text(760, 833, "must close with no cable pressure; assembled STEP rechecks this in H6.0.7.", 14),
        text(70, 876, f"nominal geometry: {audit['status']} - five clear saddles - minimum relaxed reserve {audit['summary']['minimum_relaxed_reserve_mm']:.2f} mm - H6.0.3 routing is current", 14, "700", colour="#166534" if audit["status"] == "pass" else "#b91c1c"),
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed outputs differ")
    args = parser.parse_args()
    contract = load(CONTRACT)
    placement = load(PLACEMENT)
    audit = evaluate(contract, placement, load(PLACEMENT_CONTRACT), load(H1), load(H3))
    audit_text = json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    svg_text = render(contract, placement, audit)
    if args.check:
        stale = []
        if not AUDIT.is_file() or AUDIT.read_text(encoding="utf-8") != audit_text:
            stale.append(str(AUDIT.relative_to(ROOT)))
        if not SVG.is_file() or SVG.read_text(encoding="utf-8") != svg_text:
            stale.append(str(SVG.relative_to(ROOT)))
        if stale:
            print("stale outputs: " + ", ".join(stale))
            return 1
    else:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        SVG.parent.mkdir(parents=True, exist_ok=True)
        AUDIT.write_text(audit_text, encoding="utf-8")
        SVG.write_text(svg_text, encoding="utf-8")
    print(
        "H6-R2 microcoax service "
        f"{audit['status']}: {audit['summary']['path_count']} paths; "
        f"{audit['summary']['retention_saddles']} clear saddles; "
        f"{audit['summary']['minimum_relaxed_reserve_mm']:.2f} mm minimum reserve"
    )
    if audit["errors"]:
        for error in audit["errors"]:
            print("- " + error)
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
