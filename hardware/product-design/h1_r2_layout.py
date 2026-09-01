#!/usr/bin/env python3
"""Validate and render the incremental H1-R2 physical placement."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import textwrap
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-placement.json"
BASE_PATH = REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-placement-audit.json"
SVG_PATH = REPO / "docs/images/h1-r2-inner-placement.svg"
EXTERNAL_SVG_PATH = REPO / "docs/images/h1-r2-external-layout.svg"
SERVICE_SVG_PATH = REPO / "docs/images/h1-r2-service-access.svg"
COMPLETE_INNER_SVG_PATH = REPO / "docs/images/h1-r2-inner-complete.svg"
INNER_UI_SVG_PATH = REPO / "docs/images/h1-r2-inner-ui.svg"
INNER_RF_SVG_PATH = REPO / "docs/images/h1-r2-inner-rf.svg"
INNER_SECTIONS_SVG_PATH = REPO / "docs/images/h1-r2-inner-sections.svg"
FOUR_FACES_SVG_PATH = REPO / "docs/images/h1-r2-four-faces.svg"
COMPONENT_LEGEND_SVG_PATH = REPO / "docs/images/h1-r2-component-legend.svg"
EN_DOC_PATH = REPO / "docs/h1-r2-physical-layout.md"
RU_DOC_PATH = REPO / "docs/h1-r2-physical-layout.ru.md"
SOURCE_TABLE_PATH = REPO / "hardware/product-design/generated/H1-physical-source-table.json"
U219_SOURCE_PATH = REPO / "hardware/architecture/h1-r2-u219-cap.json"
DUAL_RP_PINOUT_PATH = REPO / "hardware/architecture/h1-r2-dual-rp-pinout.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
PUBLIC_ASSET_REV = "h1-r2.38-direct-zif-2"
BOTTOM_SILK_OWNER_BASELINE_MM = 145.1
BOTTOM_SILK_ROLE_BASELINE_MM = 147.0


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def legacy_generator():
    """Load the established R1 drawing engine as a reusable geometric base."""
    product_design = str(Path(__file__).resolve().parent)
    if product_design not in sys.path:
        sys.path.insert(0, product_design)
    import g3_clamshell  # type: ignore

    return g3_clamshell


def bbox(item: dict, model: dict) -> dict:
    x, y = item["world_xy_mm"]
    w, h, z = item["size_mm"]
    if item["frame"] == "ui-inner":
        zr = [model["stack"]["ui_inner_z_mm"], model["stack"]["ui_inner_z_mm"] + z]
    elif item["frame"] == "rf-inner":
        zr = [model["stack"]["rf_inner_z_mm"] - z, model["stack"]["rf_inner_z_mm"]]
    elif item["frame"] in {"rf-outer-face", "rf-outer-right-edge", "rear-outer"}:
        zr = [
            model["stack"]["rf_inner_z_mm"] + model["stack"]["rf_pcb_thickness_mm"],
            model["stack"]["rf_inner_z_mm"] + model["stack"]["rf_pcb_thickness_mm"] + z,
        ]
    elif item["frame"] == "ui-outer-face":
        ui_outer = model["stack"]["ui_inner_z_mm"] - model["stack"]["ui_pcb_thickness_mm"]
        zr = [ui_outer - z, ui_outer]
    else:
        raise ValueError(f'unsupported placement frame: {item["frame"]}')
    return {"x": [x, x + w], "y": [y, y + h], "z": zr}


def courtyard_bbox(item: dict) -> dict | None:
    """Return a source-backed XY assembly envelope when one is registered."""
    box = item.get("courtyard_world_bbox_mm")
    if box is None:
        return None
    return {"x": list(box["x"]), "y": list(box["y"])}


def overlaps(a: dict, b: dict) -> bool:
    return (
        a["x"][0] < b["x"][1]
        and a["x"][1] > b["x"][0]
        and a["y"][0] < b["y"][1]
        and a["y"][1] > b["y"][0]
    )


def z_clearance(a: dict, b: dict) -> float:
    if a["z"][1] <= b["z"][0]:
        return b["z"][0] - a["z"][1]
    if b["z"][1] <= a["z"][0]:
        return a["z"][0] - b["z"][1]
    return -min(a["z"][1], b["z"][1]) + max(a["z"][0], b["z"][0])


def rectangle_distance(a: dict, b: dict) -> float:
    """Shortest planar distance between two closed axis-aligned rectangles."""
    dx = max(a["x"][0] - b["x"][1], b["x"][0] - a["x"][1], 0.0)
    dy = max(a["y"][0] - b["y"][1], b["y"][0] - a["y"][1], 0.0)
    return math.hypot(dx, dy)


def contains(outer: dict, inner: dict) -> bool:
    return (
        outer["x"][0] <= inner["x"][0]
        and outer["x"][1] >= inner["x"][1]
        and outer["y"][0] <= inner["y"][0]
        and outer["y"][1] >= inner["y"][1]
    )


def mmcx_service_audit(model: dict, base: dict, placed: list[dict]) -> dict:
    """Audit the vertical rear-face SMT MMCX and its user-access envelope."""
    del base, placed  # The accepted connector has no tail inside the sandwich.
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mount = mmcx["mounting"]
    x, y = mmcx["world_xy_mm"]
    width, depth, body_height = mmcx["size_mm"]
    axis_x, axis_y = mount["mounting_axis_world_xy_mm"]
    errors: list[str] = []

    if abs(axis_x - (x + width / 2)) > 1e-6 or abs(axis_y - (y + depth / 2)) > 1e-6:
        errors.append("vertical MMCX mounting axis is not centred in its SMT body")
    if mount["through_board_tail"]:
        errors.append("vertical MMCX unexpectedly declares a through-board tail")
    board_w, board_h = model["board_mm"]
    if x < 0 or y < 0 or x + width > board_w or y + depth > board_h:
        errors.append("vertical MMCX body leaves the RF outer-face PCB outline")

    service_radius = mount["external_plug_service_keepout_diameter_mm"] / 2
    service_keepout = {
        "x": [axis_x - service_radius, axis_x + service_radius],
        "y": [axis_y - service_radius, axis_y + service_radius],
    }
    installed_connector_clearances = []
    handling_envelope_clearances = []
    physical_plug_clearances = []
    mmcx_body_box = {"x": [x, x + width], "y": [y, y + depth]}
    plug = mount["controlled_right_angle_plug_reference"]
    plug_half_width = plug["connector_head_width_max_mm"] / 2
    physical_plug_box = {
        "x": [axis_x - plug["strain_relief_run_max_mm"], axis_x + plug_half_width],
        "y": [axis_y - plug_half_width, axis_y + plug_half_width],
    }

    def rectangle_distance(a: dict, b: dict) -> float:
        dx = max(a["x"][0] - b["x"][1], b["x"][0] - a["x"][1], 0.0)
        dy = max(a["y"][0] - b["y"][1], b["y"][0] - a["y"][1], 0.0)
        return math.hypot(dx, dy)

    def point_to_rectangle_distance(px: float, py: float, box: dict) -> float:
        dx = max(box["x"][0] - px, px - box["x"][1], 0.0)
        dy = max(box["y"][0] - py, py - box["y"][1], 0.0)
        return math.hypot(dx, dy)

    for centre, path in zip(
        model["antenna_bank_optimization"]["rear_x_centres_mm"],
        model["antenna_bank_optimization"]["rear_paths"],
    ):
        sma_box = {"x": [centre - 10.2 / 2, centre + 10.2 / 2], "y": [0.0, 6.0]}
        body_clearance = rectangle_distance(mmcx_body_box, sma_box)
        handling_clearance = point_to_rectangle_distance(axis_x, axis_y, sma_box) - service_radius
        physical_plug_clearance = rectangle_distance(physical_plug_box, sma_box)
        installed_connector_clearances.append({"path": path, "clearance_mm": round(body_clearance, 3)})
        handling_envelope_clearances.append({"path": path, "clearance_mm": round(handling_clearance, 3)})
        physical_plug_clearances.append({"path": path, "clearance_mm": round(physical_plug_clearance, 3)})
        if body_clearance + 1e-6 < model["stack"]["minimum_opposing_clearance_mm"]:
            errors.append(f"MMCX installed body leaves only {body_clearance:.3f} mm to rear antenna {path}")
        if physical_plug_clearance + 1e-6 < model["stack"]["minimum_opposing_clearance_mm"]:
            errors.append(f"MMCX right-angle plug leaves only {physical_plug_clearance:.3f} mm to rear antenna {path}")
    handling_overlaps = [row for row in handling_envelope_clearances if row["clearance_mm"] < 0]
    actual_handling_overlaps = {row["path"] for row in handling_overlaps}
    expected_handling_overlaps = set(model["antenna_bank_optimization"]["allowed_handling_overlaps"])
    if actual_handling_overlaps != expected_handling_overlaps:
        errors.append(
            "MMCX handling-envelope overlaps do not match the model: "
            f"expected {sorted(expected_handling_overlaps)}, got {sorted(actual_handling_overlaps)}"
        )

    u214_clearance = mount["u214_near_edge_y_mm"] - service_keepout["y"][1]
    if u214_clearance + 1e-6 < mount["minimum_u214_clearance_mm"]:
        errors.append(f"MMCX service envelope leaves only {u214_clearance:.3f} mm to U214")
    physical_plug_u214_clearance = mount["u214_near_edge_y_mm"] - physical_plug_box["y"][1]
    if physical_plug_u214_clearance + 1e-6 < mount["minimum_u214_clearance_mm"]:
        errors.append(
            f"MMCX right-angle plug leaves only {physical_plug_u214_clearance:.3f} mm to U214"
        )
    if physical_plug_box["x"][0] < 0 or physical_plug_box["x"][1] > board_w:
        errors.append("MMCX right-angle plug and strain relief leave the rear PCB plan")
    mounting_keepout_clearances = []
    for hole_x, hole_y in ((5.0, 11.0), (70.0, 11.0)):
        clearance = point_to_rectangle_distance(hole_x, hole_y, physical_plug_box) - 4.0
        mounting_keepout_clearances.append(
            {"hole_world_xy_mm": [hole_x, hole_y], "clearance_mm": round(clearance, 3)}
        )
        if clearance + 1e-6 < model["stack"]["minimum_opposing_clearance_mm"]:
            errors.append(
                f"MMCX right-angle plug leaves only {clearance:.3f} mm to mounting keep-out at {(hole_x, hole_y)}"
            )
    return {
        "status": "pass" if not errors else "fail",
        "mpn": mmcx["mpn"],
        "drawing_source": next(row["drawing_url"] for row in model["factory_evidence"] if row["mpn"] == mmcx["mpn"]),
        "installed_body_world_bbox_mm": {
            "x": [round(x, 3), round(x + width, 3)],
            "y": [round(y, 3), round(y + depth, 3)],
            "z_above_outer_pcb": [0.0, body_height],
        },
        "mounting_axis_world_xy_mm": [axis_x, axis_y],
        "through_board_tail": False,
        "opposing_body_hits": [],
        "external_service_keepout": {
            "diameter_mm": mount["external_plug_service_keepout_diameter_mm"],
            "outward_length_mm": mount["external_plug_service_keepout_length_mm"],
            "world_xy_bbox_mm": service_keepout,
        },
        "rear_antenna_connector_clearances": installed_connector_clearances,
        "minimum_rear_antenna_connector_clearance_mm": min(row["clearance_mm"] for row in installed_connector_clearances),
        "handling_envelope_clearances": handling_envelope_clearances,
        "handling_envelope_overlaps": handling_overlaps,
        "handling_envelope_semantics": "temporary finger approach only; not a static installed body",
        "controlled_right_angle_plug_reference": plug,
        "right_angle_plug_world_bbox_mm": physical_plug_box,
        "right_angle_plug_clearances": physical_plug_clearances,
        "minimum_right_angle_plug_clearance_mm": min(row["clearance_mm"] for row in physical_plug_clearances),
        "right_angle_plug_u214_clearance_mm": round(physical_plug_u214_clearance, 3),
        "right_angle_plug_mounting_keepout_clearances": mounting_keepout_clearances,
        "fixed_installation_sequence": model["antenna_bank_optimization"]["installation_sequence"],
        "u214_service_clearance_mm": round(u214_clearance, 3),
        "factory_assembly": "Extended SMT; Economic and Standard PCBA",
        "later_hil": [
            "received connector-to-antenna mating and retention",
            "U214 Cap insertion with the FPV plug fitted",
            "ordinary plug mating, finger access and antenna strain-relief inspection",
        ],
        "errors": errors,
    }


def silkscreen_audit(model: dict) -> dict:
    """Reject outer-face antenna or board-ID silk hidden by product geometry."""
    font_px = float(model["antenna_silkscreen"]["font_size_px"])
    px_per_mm = 3.7
    def text_box(row: dict) -> dict:
        row_font_px = float(row.get("font_size_px", font_px))
        row_text_height = row_font_px / px_per_mm * 1.15
        width = max(1.0, len(row["text"]) * row_font_px * 0.60 / px_per_mm)
        return {
            "x": [row["x_mm"] - width / 2, row["x_mm"] + width / 2],
            "y": [row["baseline_y_mm"] - row_text_height, row["baseline_y_mm"] + row_text_height * 0.18],
        }

    def expanded(box: dict, margin: float) -> dict:
        return {
            "x": [box["x"][0] - margin, box["x"][1] + margin],
            "y": [box["y"][0] - margin, box["y"][1] + margin],
        }

    def hits_circle(box: dict, cx: float, cy: float, radius: float) -> bool:
        nearest_x = min(max(cx, box["x"][0]), box["x"][1])
        nearest_y = min(max(cy, box["y"][0]), box["y"][1])
        return math.hypot(nearest_x - cx, nearest_y - cy) < radius

    rows = {
        "front": model["antenna_silkscreen"]["front"],
        "rear": model["antenna_silkscreen"]["rear"],
    }
    expected = {
        "front": set(model["antenna_bank_optimization"]["front_paths"]),
        "rear": set(model["antenna_bank_optimization"]["rear_paths"]),
    }
    errors: list[str] = []
    boxes: dict[str, list[dict]] = {"front": [], "rear": []}
    for face, face_rows in rows.items():
        paths = {row["path"] for row in face_rows if "path" in row}
        if paths != expected[face]:
            errors.append(f"{face} antenna-silk paths differ from the physical antenna bank")
        for row in face_rows:
            box = text_box(row)
            boxes[face].append({"text": row["text"], "box_mm": box})
            if box["x"][0] < 0 or box["x"][1] > 75 or box["y"][0] < 0 or box["y"][1] > 150:
                errors.append(f'{face} silk "{row["text"]}" leaves the PCB outline')
            forbidden = [
                {"name": "RF body strip", "box": {"x": [0.0, 75.0], "y": [0.0, 6.0]}},
            ]
            if face == "front":
                forbidden.append({"name": "display", "box": {"x": [9.23, 65.77], "y": [10.5, 95.46]}})
            else:
                forbidden.extend(
                    [
                        {"name": "installed U214", "box": {"x": [-4.5, 79.5], "y": [17.0, 41.0]}},
                    ]
                )
            for item in forbidden:
                if overlaps(box, item["box"]):
                    errors.append(f'{face} silk "{row["text"]}" is hidden by {item["name"]}')
            for hole_x, hole_y in ((5.0, 11.0), (70.0, 11.0), (5.0, 145.0), (70.0, 145.0)):
                if hits_circle(box, hole_x, hole_y, 4.0):
                    errors.append(f'{face} silk "{row["text"]}" enters mounting keep-out')
        for index, first in enumerate(boxes[face]):
            for second in boxes[face][index + 1:]:
                if overlaps(expanded(first["box_mm"], 0.25), expanded(second["box_mm"], 0.25)):
                    errors.append(f'{face} silk "{first["text"]}" overlaps "{second["text"]}"')
    identity_boxes: dict[str, list[dict]] = {"front": [], "rear": []}
    identity = model["hardware_identification"]
    if identity["documentation_marker_printed"]:
        errors.append("documentation work marker must never become PCB silkscreen")
    for face, face_rows in identity["silkscreen"].items():
        forbidden = (
            [
                {"name": "display", "box": {"x": [9.23, 65.77], "y": [10.5, 95.46]}},
                {"name": "front controls/indicators", "box": {"x": [0.0, 75.0], "y": [104.0, 150.0]}},
            ]
            if face == "front"
            else [
                {"name": "rear product bodies", "box": {"x": [0.0, 75.0], "y": [0.0, 132.0]}},
            ]
        )
        for row in face_rows:
            box = text_box(row)
            identity_boxes[face].append({"text": row["text"], "box_mm": box})
            if model["marker"] in row["text"]:
                errors.append(f'{face} identity silk prints documentation marker {model["marker"]}')
            if box["x"][0] < 0 or box["x"][1] > 75 or box["y"][0] < 0 or box["y"][1] > 150:
                errors.append(f'{face} identity silk "{row["text"]}" leaves the PCB outline')
            for item in forbidden:
                if overlaps(box, item["box"]):
                    errors.append(f'{face} identity silk "{row["text"]}" is hidden by {item["name"]}')
            for hole_x, hole_y in ((5.0, 11.0), (70.0, 11.0), (5.0, 145.0), (70.0, 145.0)):
                if hits_circle(box, hole_x, hole_y, 4.0):
                    errors.append(f'{face} identity silk "{row["text"]}" enters mounting keep-out')
        for index, first in enumerate(identity_boxes[face]):
            for second in identity_boxes[face][index + 1:]:
                if overlaps(expanded(first["box_mm"], 0.25), expanded(second["box_mm"], 0.25)):
                    errors.append(f'{face} identity silk "{first["text"]}" overlaps "{second["text"]}"')
    return {
        "status": "pass" if not errors else "fail",
        "faces": boxes,
        "identity": identity_boxes,
        "errors": errors,
    }


def effective_inner_entries(model: dict, base: dict, placed: list[dict]) -> list[dict]:
    """Return the retained seed and R2 placements as one collision population."""
    replaced = {
        instance
        for entry in placed
        for instance in entry["item"].get("replaces", [])
    }
    entries = [
        {
            "id": row["instance"],
            "frame": row["source_frame"],
            "bbox": row["world_bbox_mm"],
            "kind": "fixed_body",
            "origin": "retained_base",
        }
        for row in base["rows"]
        if row["source_frame"] in {"ui-inner", "rf-inner"}
        and row["instance"] not in replaced
    ]
    entries.extend(
        {
            "id": entry["item"]["id"],
            "frame": entry["item"]["frame"],
            "bbox": entry["bbox"],
            "kind": entry["item"]["kind"],
            "origin": "r2",
        }
        for entry in placed
        if entry["item"]["frame"] in {"ui-inner", "rf-inner"}
    )
    return entries


def through_hole_sma_candidate_audit(model: dict, entries: list[dict]) -> dict:
    """Test the cheaper DreamLNK pair against the accepted 5+5 geometry."""
    candidate = model["antenna_bank_optimization"]["through_hole_candidate_review"]
    body_w, body_d = map(float, candidate["outer_face_body_plan_mm"])
    edge_offset = float(candidate["board_edge_to_body_front_mm"])
    pin = candidate["pin_pattern"]
    pin_radius = float(pin["inner_pin_and_solder_keepout_radius_mm"])
    body_centre_y = edge_offset + float(pin["body_centre_from_board_edge_mm"])
    min_clearance = float(model["stack"]["minimum_opposing_clearance_mm"])
    mount = model["mechanical_retention"]["compression_stops"]
    mount_radius = 4.0

    def point_to_box_distance(px: float, py: float, box: dict) -> float:
        dx = max(box["x"][0] - px, px - box["x"][1], 0.0)
        dy = max(box["y"][0] - py, py - box["y"][1], 0.0)
        return math.hypot(dx, dy)

    pin_hits: list[dict] = []
    body_mounting_hits: list[dict] = []
    face_rows = (
        ("front", "ui-inner", model["antenna_bank_optimization"]["front_x_centres_mm"], model["antenna_bank_optimization"]["front_paths"]),
        ("rear", "rf-inner", model["antenna_bank_optimization"]["rear_x_centres_mm"], model["antenna_bank_optimization"]["rear_paths"]),
    )
    for face, frame, centres, paths in face_rows:
        face_entries = [row for row in entries if row["frame"] == frame and row["kind"] in {"fixed_body", "reserve"}]
        for centre_x, path in zip(centres, paths):
            body = {
                "x": [centre_x - body_w / 2, centre_x + body_w / 2],
                "y": [edge_offset, edge_offset + body_d],
            }
            for axis_x, axis_y in mount["axes"][:2]:
                clearance = point_to_box_distance(axis_x, axis_y, body) - mount_radius
                if clearance + 1e-6 < min_clearance:
                    body_mounting_hits.append(
                        {
                            "face": face,
                            "path": path,
                            "compression_stop_axis_mm": [axis_x, axis_y],
                            "clearance_mm": round(clearance, 3),
                        }
                    )
            pin_centres = [
                [round(centre_x + dx, 3), round(body_centre_y + dy, 3)]
                for dx, dy in pin["pin_centres_from_body_centre_mm"]
            ]
            for entry in face_entries:
                nearest = min(point_to_box_distance(px, py, entry["bbox"]) for px, py in pin_centres)
                clearance = nearest - pin_radius
                if clearance < 0:
                    pin_hits.append(
                        {
                            "face": face,
                            "path": path,
                            "body": entry["id"],
                            "clearance_to_protected_pin_keepout_mm": round(clearance, 3),
                        }
                    )
    errors = []
    if body_mounting_hits:
        errors.append("outer connector bodies enter the accepted upper compression-stop head keep-outs")
    if pin_hits:
        errors.append("through-hole pin/solder keep-outs intersect current inner-face bodies or reserves")
    if "manualWeld" in candidate["factory_surface"]:
        errors.append("written factory assembly acceptance and exact-one manual-weld quote are absent")
    return {
        "status": "rejected_current_5_plus_5_mechanical_envelope_and_factory_route" if errors else "pass",
        "standard_mpn": candidate["standard_mpn"],
        "reverse_mpn": candidate["reverse_mpn"],
        "jlcpcb_parts": candidate["jlcpcb_parts"],
        "manufacturer_sources": candidate["manufacturer_sources"],
        "outer_face_body_plan_mm": candidate["outer_face_body_plan_mm"],
        "pin_pattern": pin,
        "compression_stop_keepout_radius_mm": mount_radius,
        "body_mounting_hits": body_mounting_hits,
        "inner_pin_keepout_hits": pin_hits,
        "factory_surface": candidate["factory_surface"],
        "selection_result": "retain GCT RFPC-SMA31/32-FN-175-A; the cheaper pair is not a drop-in no-loss replacement",
        "errors": errors,
    }


def physical_feature_audit(model: dict, entries: list[dict]) -> dict:
    """Audit explicit keepouts/reserves without pretending they are components."""
    minimum = model["stack"]["minimum_opposing_clearance_mm"]
    board_w, board_h = model["board_mm"]
    by_id = {entry["id"]: entry for entry in entries}
    placement_by_id = {row["id"]: row for row in model["placements"]}
    errors: list[str] = []
    unresolved: list[dict] = []
    results: list[dict] = []
    known_kinds = {"keepout", "placement_reserve", "copper_feature_reserve", "external_swept_volume"}
    for feature in model.get("physical_features", []):
        kind = feature.get("kind")
        if kind not in known_kinds:
            errors.append(f'{feature.get("id", "unnamed feature")}: unsupported physical-feature kind {kind}')
            continue
        box = feature.get("world_bbox_mm")
        if box is None:
            if kind != "copper_feature_reserve" or not feature.get("geometry_status"):
                errors.append(f'{feature["id"]}: unresolved geometry lacks an explicit gate')
            unresolved.append({"id": feature["id"], "kind": kind, "gate": feature.get("geometry_status")})
            results.append({"id": feature["id"], "kind": kind, "world_bbox_mm": None, "minimum_clearance_mm": None})
            continue
        if kind != "external_swept_volume" and (box["x"][0] < 0 or box["y"][0] < 0 or box["x"][1] > board_w or box["y"][1] > board_h):
            errors.append(f'{feature["id"]}: feature leaves the PCB outline')
        members = set(feature.get("members", []))
        member_errors = []
        for member in members:
            entry = by_id.get(member)
            if not entry:
                member_errors.append(f"missing member {member}")
            else:
                allocation_box = courtyard_bbox(placement_by_id[member]) or entry["bbox"]
                if entry["frame"] != feature["frame"] or not contains(box, allocation_box):
                    member_errors.append(f"member {member} leaves its allocation")
        errors.extend(f'{feature["id"]}: {message}' for message in member_errors)
        clearances = []
        if kind in {"keepout", "placement_reserve"}:
            allowed = members | set(feature.get("allowed_instances", []))
            for entry in entries:
                if entry["frame"] != feature["frame"] or entry["id"] in allowed:
                    continue
                if entry["kind"] != "fixed_body":
                    continue
                gap = rectangle_distance(box, entry["bbox"])
                clearances.append({"instance": entry["id"], "clearance_mm": round(gap, 3)})
                if gap + 1e-6 < minimum:
                    errors.append(
                        f'{feature["id"]}: only {gap:.3f} mm to {entry["id"]}; {minimum:.3f} mm required'
                    )
        results.append(
            {
                "id": feature["id"],
                "kind": kind,
                "world_bbox_mm": box,
                "members": sorted(members),
                "minimum_clearance_mm": min((row["clearance_mm"] for row in clearances), default=None),
            }
        )
    return {
        "status": "pass" if not errors else "fail",
        "features": results,
        "unresolved_geometry": unresolved,
        "errors": errors,
    }


def u219_contract_audit(model: dict) -> dict:
    """Cross-check the physical bodies against the accepted U219 architecture overlay."""
    source = REPO / model["cap_bus_slot"]["architecture_source"]
    contract = load(source)
    errors: list[str] = []
    u219 = model["cap_bus_slot"]["profiles"]["u219"]
    if u219["envelope_mm"] != contract["accessories"]["u219"]["envelope_mm"]:
        errors.append("U219 physical envelope differs from the accepted architecture overlay")
    expected = {
        "u219_pin10_switch": (contract["pin_10_bidirectional_boundary"]["switch_mpn"], [2.9, 2.65]),
        "u219_pin10_oe_driver": (contract["pin_10_bidirectional_boundary"]["aon_enable"]["inverter_mpn"], [2.9, 2.65]),
        "u219_field_bridge_a": ("BAT54S,215", [3.8, 3.5]),
        "u219_field_bridge_b": ("BAT54S,215", [3.8, 3.5]),
        "u219_field_comparator": ("LMV331IDBVR", [3.55, 3.5]),
        "u219_pin10_oe_pullup": ("0402WGF1002TCE", [1.5, 1.0]),
        "u219_pin10_command_pulldown": ("0402WGF1002TCE", [1.5, 1.0]),
        "u219_pin10_switch_bypass": ("Yageo CC0402KRX7R9BB104", [1.5, 1.0]),
        "u219_pin10_driver_bypass": ("Yageo CC0402KRX7R9BB104", [1.5, 1.0]),
        "u219_field_input_r_p": ("0402WGF1001TCE", [1.5, 1.0]),
        "u219_field_input_r_n": ("0402WGF1001TCE", [1.5, 1.0]),
        "u219_field_env_cap": ("Murata GRM155R71H103KA88D", [1.5, 1.0]),
        "u219_field_discharge": ("0402WGF1003TCE", [1.5, 1.0]),
        "u219_field_threshold_top": ("0402WGF1003TCE", [1.5, 1.0]),
        "u219_field_threshold_bottom": ("0402WGF1002TCE", [1.5, 1.0]),
        "u219_field_hysteresis": ("0402WGF1004TCE", [1.5, 1.0]),
        "u219_field_output_pullup": ("0402WGF1002TCE", [1.5, 1.0]),
        "u219_field_comparator_bypass": ("Yageo CC0402KRX7R9BB104", [1.5, 1.0]),
    }
    placed = {row["id"]: row for row in model["placements"]}
    courtyard_entries = []
    for instance, (mpn, expected_size) in expected.items():
        row = placed.get(instance)
        if not row or row.get("mpn") != mpn or row.get("kind") != "fixed_body":
            errors.append(f"{instance}: exact U219 host body is absent or has the wrong MPN")
            continue
        cbox = courtyard_bbox(row)
        if row.get("courtyard_xy_mm") != expected_size or cbox is None:
            errors.append(f"{instance}: source-backed H1 courtyard is absent or has the wrong size")
            continue
        measured_size = [
            round(cbox["x"][1] - cbox["x"][0], 3),
            round(cbox["y"][1] - cbox["y"][0], 3),
        ]
        if measured_size != expected_size:
            errors.append(f"{instance}: courtyard dimensions disagree with its world envelope")
        body = bbox(row, model)
        if not contains(cbox, body):
            errors.append(f"{instance}: maximum full package leaves its courtyard")
        if "source-backed H1 fit evidence" not in row.get("courtyard_status", ""):
            errors.append(f"{instance}: courtyard status overclaims or lacks source-backed H1 evidence")
        if "0.25 mm" not in row.get("courtyard_basis", ""):
            errors.append(f"{instance}: courtyard lacks the accepted 0.25-mm assembly margin")
        courtyard_entries.append((instance, cbox))
    for index, (left_id, left_box) in enumerate(courtyard_entries):
        for right_id, right_box in courtyard_entries[index + 1:]:
            if overlaps(left_box, right_box):
                errors.append(f"U219 courtyards overlap: {left_id} / {right_id}")
    return {
        "status": "pass" if not errors else "fail",
        "source": str(source.relative_to(REPO)),
        "profile": contract["accessories"]["u219"]["profile"],
        "fixed_body_instances": sorted(expected),
        "source_backed_courtyard_instances": sorted(instance for instance, _ in courtyard_entries),
        "errors": errors,
    }


def tx_evidence_physical_audit(model: dict) -> dict:
    """Prove that every accepted onboard TX path owns a real detector island."""
    placed = {row["id"]: row for row in model["placements"]}
    devices = load(DEVICES_PATH)["devices"]
    minimum = float(model["stack"]["minimum_opposing_clearance_mm"])
    mount_radius = 4.0
    mount_axes = model["mechanical_retention"]["compression_stops"]["axes"]
    errors: list[str] = []

    expected = {
        "s3_rf_coupler_r2": ("CP0603Q5425ENTR", "ui-inner", [2.1, 1.34]),
        "det_s3_r2": ("LTC5532ES6#TRMPBF", "ui-inner", [3.4, 2.1]),
        "c5_rf_coupler_r2": ("CP0603Q5425ENTR", "ui-inner", [2.1, 1.34]),
        "det_c5_r2": ("LTC5532ES6#TRMPBF", "ui-inner", [3.4, 2.1]),
        "nrf0_coupler_r2": ("DC2337J5010AHF", "ui-inner", [2.53, 1.77]),
        "det_nrf0_r2": ("AD8314ARMZ-REEL", "ui-inner", [5.65, 3.7]),
        "nrf1_coupler_r2": ("DC2337J5010AHF", "ui-inner", [2.53, 1.77]),
        "det_nrf1_r2": ("AD8314ARMZ-REEL", "ui-inner", [5.65, 3.7]),
        "nrf2_coupler_r2": ("DC2337J5010AHF", "ui-inner", [2.53, 1.77]),
        "det_nrf2_r2": ("AD8314ARMZ-REEL", "ui-inner", [5.65, 3.7]),
        "det_cc_r2": ("AD8314ARMZ-REEL", "rf-inner", [5.65, 3.7]),
        "det_voice_r2": ("AD8314ARMZ-REEL", "rf-inner", [5.65, 3.7]),
        "det_voice_v_r2": ("AD8314ARMZ-REEL", "rf-inner", [3.7, 5.65]),
    }
    actual_scope = {
        row["id"] for row in model["placements"]
        if row["id"] in expected
        or row["id"].startswith("det_") and row["id"].endswith("_r2")
        or row["id"].startswith("nrf") and row["id"].endswith("_coupler_r2")
    }
    if actual_scope != set(expected):
        errors.append("R2 TX-evidence detector/coupler scope is incomplete or contains an unregistered body")

    fixed_results = []
    for instance, (mpn, frame, courtyard_size) in expected.items():
        row = placed.get(instance)
        if not row:
            errors.append(f"{instance}: accepted TX-evidence body is missing")
            continue
        if row.get("kind") != "fixed_body" or row.get("mpn") != mpn or row.get("frame") != frame:
            errors.append(f"{instance}: exact MPN, frame or fixed-body identity drifted")
            continue
        cbox = courtyard_bbox(row)
        if row.get("courtyard_xy_mm") != courtyard_size or cbox is None:
            errors.append(f"{instance}: source-backed full-package courtyard is absent or wrong")
            continue
        measured = [
            round(cbox["x"][1] - cbox["x"][0], 3),
            round(cbox["y"][1] - cbox["y"][0], 3),
        ]
        if measured != courtyard_size or not contains(cbox, bbox(row, model)):
            errors.append(f"{instance}: package body leaves or disagrees with its courtyard")
        if "source-backed H1 fit evidence" not in row.get("courtyard_status", ""):
            errors.append(f"{instance}: courtyard status lacks source-backed H1 evidence")
        if "0.25 mm" not in row.get("courtyard_basis", ""):
            errors.append(f"{instance}: courtyard lacks the accepted 0.25-mm assembly margin")
        fixed_results.append({"id": instance, "mpn": mpn, "frame": frame, "courtyard_world_bbox_mm": cbox})

    selected = devices.get("adi_ad8314armz_reel", {})
    route = selected.get("factory_route", {})
    expected_contacts = {"RFIN", "ENBL", "VSET", "FLTR", "COMM", "V_UP", "V_DN", "VPOS"}
    if (
        selected.get("mpn") != "Analog Devices AD8314ARMZ-REEL"
        or selected.get("dimensions_mm") != [5.15, 3.2, 1.1]
        or set(selected.get("contacts", {})) != expected_contacts
        or route.get("jlcpcb_part") != "C652687"
        or route.get("assembly_type") != "SMT Assembly; Extended; Standard PCBA"
        or route.get("presale_moq", 999) > route.get("required_quantity_per_device", 0)
        or route.get("presale_available_quantity", 0) < route.get("required_quantity_per_device", 0)
    ):
        errors.append("AD8314ARMZ-REEL exact package, pins or JLCPCB Standard-PCBA route is not closed")

    expected_features = {
        "s3_tx_evidence_island_reserve": {"s3_rf_board_connector_r2", "s3_rf_coupler_r2", "det_s3_r2"},
        "c5_tx_evidence_island_reserve": {"c5_rf_board_connector_r2", "c5_rf_coupler_r2", "det_c5_r2"},
        "nrf0_tx_evidence_island_reserve": {"nrf0_rf_board_connector_r2", "nrf0_coupler_r2", "det_nrf0_r2"},
        "nrf1_tx_evidence_island_reserve": {"nrf1_rf_board_connector_r2", "nrf1_coupler_r2", "det_nrf1_r2"},
        "nrf2_tx_evidence_island_reserve": {"nrf2_rf_board_connector_r2", "nrf2_coupler_r2", "det_nrf2_r2"},
        "cc_tx_evidence_island_reserve": {"cc_r2", "det_cc_r2"},
        "uhf_tx_evidence_island_reserve": {"det_voice_r2"},
        "vhf_tx_evidence_island_reserve": {"det_voice_v_r2"},
    }
    feature_by_id = {row["id"]: row for row in model.get("physical_features", [])}
    reserve_results = []

    def point_to_box_distance(px: float, py: float, box: dict) -> float:
        dx = max(box["x"][0] - px, px - box["x"][1], 0.0)
        dy = max(box["y"][0] - py, py - box["y"][1], 0.0)
        return math.hypot(dx, dy)

    for feature_id, members in expected_features.items():
        feature = feature_by_id.get(feature_id)
        if not feature or feature.get("kind") != "placement_reserve" or set(feature.get("members", [])) != members:
            errors.append(f"{feature_id}: complete local TX-evidence allocation is absent or wrong")
            continue
        box = feature["world_bbox_mm"]
        for member in members:
            row = placed.get(member)
            if row is None:
                errors.append(f"{feature_id}: {member} is absent from the physical model")
                continue
            allocation = courtyard_bbox(row) or bbox(row, model)
            if not contains(box, allocation):
                errors.append(f"{feature_id}: {member} leaves its local allocation")
        mount_clearance = min(
            point_to_box_distance(axis_x, axis_y, box) - mount_radius
            for axis_x, axis_y in mount_axes
        )
        if mount_clearance + 1e-6 < minimum:
            errors.append(f"{feature_id}: only {mount_clearance:.3f} mm to a compression-stop keep-out")
        reserve_results.append({
            "id": feature_id,
            "members": sorted(members),
            "world_bbox_mm": box,
            "minimum_compression_stop_clearance_mm": round(mount_clearance, 3),
        })

    return {
        "status": "pass" if not errors else "fail",
        "detector_count": 8,
        "coupler_count": 5,
        "local_island_count": len(expected_features),
        "selected_detector_device_id": "adi_ad8314armz_reel",
        "selected_detector_factory_route": route,
        "fixed_bodies": fixed_results,
        "local_islands": reserve_results,
        "errors": errors,
    }


def cap_bus_slot_audit(model: dict, base: dict) -> dict:
    """Validate mutually exclusive U214/U219 envelopes and the current rear geometry."""
    slot = model["cap_bus_slot"]
    profiles = slot["profiles"]
    errors: list[str] = []
    if slot["population"] != "exactly_one" or set(profiles) != {"u214", "u219"}:
        errors.append("Cap-Bus slot must contain exactly one mutually exclusive U214 or U219 profile")
    plan = slot["world_plan_bbox_mm"]
    for name, profile in profiles.items():
        world = profile["world_bbox_mm"]
        if world["x"] != plan["x"] or world["y"] != plan["y"]:
            errors.append(f"{name}: Cap profile no longer shares the common slot plan")
        expected_top = round(slot["host_outer_plane_z_mm"] + profile["envelope_mm"][2], 3)
        if round(world["z"][1], 3) != expected_top:
            errors.append(f"{name}: installed Z envelope does not match its official height")
    if slot["maximum_installed_profile"] != "u219":
        errors.append("U219 must remain the maximum-height Cap profile")

    u219_box = profiles["u219"]["world_bbox_mm"]
    battery = base["accessory_envelopes"]["battery_holder"]
    encoder = next(row for row in base["rows"] if row["instance"] == "encoder_knob")["world_bbox_mm"]
    antenna_y = base["longitudinal_zones"]["antenna_connector_zone_y_mm"]
    calculated = {
        "battery_pad_span": battery["pad_span_y_mm"][0] - u219_box["y"][1],
        "battery_holder_body": battery["body_y_mm"][0] - u219_box["y"][1],
        "encoder_knob": encoder["y"][0] - u219_box["y"][1],
        "main_antenna_body_strip": u219_box["y"][0] - antenna_y[1],
    }
    for name, expected in slot["clearance_targets_mm"].items():
        if name == "minimum":
            continue
        actual = round(calculated[name], 3)
        if abs(actual - expected) > 0.011:
            errors.append(f"Cap-slot {name} clearance changed from {expected:.3f} to {actual:.3f} mm")
        if actual + 1e-6 < slot["clearance_targets_mm"]["minimum"]:
            errors.append(f"Cap-slot {name} clearance is only {actual:.3f} mm")
    rear = slot["rear_depth_reference_mm"]
    calculated_rear_max = max(
        u219_box["z"][1],
        battery["z_mm"][1],
        encoder["z"][1],
    )
    if abs(calculated_rear_max - rear["current_maximum_top_z"]) > 1e-6:
        errors.append("U219 unexpectedly changes the selected rear-depth envelope")
    return {
        "status": "pass" if not errors else "fail",
        "population": slot["population"],
        "profiles": profiles,
        "calculated_clearances_mm": {name: round(value, 3) for name, value in calculated.items()},
        "u219_height_delta_vs_u214_mm": round(u219_box["z"][1] - profiles["u214"]["world_bbox_mm"]["z"][1], 3),
        "u219_margin_below_battery_holder_top_mm": round(battery["z_mm"][1] - u219_box["z"][1], 3),
        "u219_margin_below_current_rear_max_mm": round(calculated_rear_max - u219_box["z"][1], 3),
        "calculated_rear_max_z_mm": round(calculated_rear_max, 3),
        "open_geometry_gates": slot["open_geometry_gates"],
        "errors": errors,
    }


def audit(model: dict, base: dict) -> dict:
    board_w, board_h = model["board_mm"]
    minimum = model["stack"]["minimum_opposing_clearance_mm"]
    new = []
    errors = []
    cap_evidence_register = base.get("cap_evidence_coordinate_register", {})
    expected_cap_evidence = legacy_generator().CAP_EVIDENCE_COORDINATE_INSTANCE_DEVICES
    registered_cap_evidence = {
        row.get("instance"): row.get("device_key")
        for row in cap_evidence_register.get("instances", [])
    }
    if cap_evidence_register.get("status") != "pass":
        errors.append("base Cap/evidence coordinate register is absent or failed")
    if cap_evidence_register.get("expected_instance_count") != len(expected_cap_evidence):
        errors.append("base Cap/evidence coordinate-register scope count drifted")
    if cap_evidence_register.get("resolved_instance_count") != len(expected_cap_evidence):
        errors.append("base Cap/evidence coordinate register is incomplete")
    if registered_cap_evidence != expected_cap_evidence:
        errors.append("base Cap/evidence coordinate register differs from current exact G2F")
    if any(
        not row.get("coordinate_mm")
        or not row.get("source_envelope_mm")
        or not row.get("placement_courtyard_bbox_mm")
        for row in cap_evidence_register.get("instances", [])
    ):
        errors.append("base Cap/evidence register lacks coordinate/envelope/courtyard data")
    dual_rp = load(DUAL_RP_PINOUT_PATH)
    for placement_key, authority_key in (("front_rp_gpio", "hub_rp"), ("rear_rp_gpio", "rf_rp")):
        placement_budget = model.get("functional_partition", {}).get(placement_key, {})
        authority_budget = dual_rp.get(authority_key, {}).get("gpio_budget", {})
        if (
            placement_budget.get("used") != authority_budget.get("used")
            or placement_budget.get("free") != authority_budget.get("reserve")
        ):
            errors.append(f"{placement_key}: physical model GPIO budget differs from exact dual-RP authority")
    drawing_refs: dict[str, list[str]] = {}
    for item in model["placements"]:
        drawing_ref = str(item.get("drawing_ref", ""))
        drawing_refs.setdefault(drawing_ref, []).append(item["id"])
        b = bbox(item, model)
        new.append({"item": item, "bbox": b})
        if item["frame"] in {"ui-inner", "rf-inner"}:
            if b["x"][0] < 0 or b["y"][0] < 0 or b["x"][1] > board_w or b["y"][1] > board_h:
                errors.append(f"{item['id']} leaves the PCB outline")
    duplicate_refs = {
        ref: instances for ref, instances in drawing_refs.items()
        if not ref or len(instances) != 1
    }
    if duplicate_refs:
        errors.append(f"placement drawing references are not globally unique: {duplicate_refs}")

    physical_bodies = [
        x for x in new if x["item"]["kind"] in {"fixed_body", "reserve"}
    ]
    replaced = {
        instance
        for entry in new
        for instance in entry["item"].get("replaces", [])
    }
    same_face = []
    for entry in physical_bodies:
        item, b = entry["item"], entry["bbox"]
        allowed = set(item.get("allowed_instances", []))
        for row in base["rows"]:
            if row["source_frame"] != item["frame"]:
                continue
            if row["instance"] in replaced:
                continue
            if row["instance"] in allowed:
                continue
            if overlaps(b, row["world_bbox_mm"]):
                same_face.append([item["id"], row["instance"]])
        for other in physical_bodies:
            if other["item"]["id"] <= item["id"] or other["item"]["frame"] != item["frame"]:
                continue
            if (
                other["item"]["id"] in allowed
                or item["id"] in set(other["item"].get("allowed_instances", []))
            ):
                continue
            if overlaps(b, other["bbox"]):
                same_face.append([item["id"], other["item"]["id"]])
    if same_face:
        errors.extend(f"same-face collision: {a} / {b}" for a, b in same_face)

    effective = effective_inner_entries(model, base, new)
    ui_entries = [entry for entry in effective if entry["frame"] == "ui-inner"]
    rf_entries = [entry for entry in effective if entry["frame"] == "rf-inner"]
    intentional_mates = {
        frozenset(pair) for pair in model["mechanical_retention"].get("intentional_opposing_mates", [])
    }
    cross = []
    mated = []
    for ui_entry in ui_entries:
        for rf_entry in rf_entries:
            if not overlaps(ui_entry["bbox"], rf_entry["bbox"]):
                continue
            gap = z_clearance(ui_entry["bbox"], rf_entry["bbox"])
            pair = frozenset((ui_entry["id"], rf_entry["id"]))
            if pair in intentional_mates:
                mated.append(
                    {"ui": ui_entry["id"], "rf": rf_entry["id"], "overlap_mm": round(-gap, 3)}
                )
                continue
            cross.append(
                {
                    "ui": ui_entry["id"],
                    "rf": rf_entry["id"],
                    "ui_origin": ui_entry["origin"],
                    "rf_origin": rf_entry["origin"],
                    "clearance_mm": round(gap, 3),
                }
            )
            if gap < minimum:
                errors.append(
                    f'opposing clearance {ui_entry["id"]} / {rf_entry["id"]} is {gap:.3f} mm'
                )
    min_cross = min((x["clearance_mm"] for x in cross), default=None)
    if len(model["current_h1_blockers_ru"]) != len(model["current_h1_blockers"]):
        errors.append("bilingual current H1 blockers are out of sync")
    expected_dependent_h1 = 0 if model.get("status") == "reviewed" else 1
    if len(model["dependent_h1_work"]) != expected_dependent_h1:
        errors.append(
            "physical layout dependent H1 work must match its review status"
        )
    if len(model["dependent_h1_work_ru"]) != len(model["dependent_h1_work"]):
        errors.append("bilingual dependent H1 work is out of sync")
    relocated_c5 = next((row for row in model["placements"] if row["id"] == "c5_dbg_header_r2"), None)
    if not relocated_c5 or relocated_c5.get("replaces") != ["c5_dbg_header"]:
        errors.append("the relocated C5 DBG10 is missing")
    if any(row.get("stage") == "H1" for row in model["downstream_verification"]):
        errors.append("a downstream physical verification item is still owned by H1")
    features = physical_feature_audit(model, effective)
    errors.extend(features["errors"])
    u219_contract = u219_contract_audit(model)
    errors.extend(u219_contract["errors"])
    tx_evidence = tx_evidence_physical_audit(model)
    errors.extend(tx_evidence["errors"])
    cap_slot = cap_bus_slot_audit(model, base)
    errors.extend(cap_slot["errors"])
    silk = silkscreen_audit(model)
    errors.extend(silk["errors"])
    through_hole_candidate = through_hole_sma_candidate_audit(model, effective)
    sma_mounting = model["antenna_bank_optimization"].get("main_sma_mounting", {})
    if sma_mounting.get("standard_mpn") != "GCT RFPC-SMA31-FN-175-A":
        errors.append("main standard-SMA dual-face mounting identity drifted")
    if sma_mounting.get("reverse_mpn") != "GCT RFPC-SMA32-FN-175-A":
        errors.append("main RP-SMA dual-face mounting identity drifted")
    if any(
        sma_mounting.get("pcb_thickness_mm") != thickness
        for thickness in (
            model["stack"]["ui_pcb_thickness_mm"],
            model["stack"]["rf_pcb_thickness_mm"],
        )
    ):
        errors.append("main SMA board-thickness option differs from the PCB stack")
    expected_component_lands = [
        {"role": "RF", "centre_xy_mm": [0.0, -1.65], "size_mm": [1.87, 3.3]},
        {"role": "GROUND_LEFT", "centre_xy_mm": [-2.55, -1.65], "size_mm": [1.6, 3.3]},
        {"role": "GROUND_RIGHT", "centre_xy_mm": [2.55, -1.65], "size_mm": [1.6, 3.3]},
    ]
    expected_opposite_lands = [
        {"role": "GROUND_LEFT", "centre_xy_mm": [-2.55, -1.65], "size_mm": [1.6, 3.3]},
        {"role": "GROUND_RIGHT", "centre_xy_mm": [2.55, -1.65], "size_mm": [1.6, 3.3]},
    ]
    if sma_mounting.get("component_face_lands") != expected_component_lands:
        errors.append("main SMA component-face exact land contract drifted")
    if sma_mounting.get("opposite_face_lands") != expected_opposite_lands:
        errors.append("main SMA opposite-face exact land contract drifted")
    if sma_mounting.get("board_edge_y_mm") != 0.0:
        errors.append("main SMA board-edge origin drifted")
    if sma_mounting.get("body_gap_mm", {}).get("nominal") != 1.75:
        errors.append("main SMA 1.75-mm body-gap option drifted")
    if "one PCB face" not in sma_mounting.get("substitution_rule", ""):
        errors.append("main SMA substitution gate no longer rejects one-face mounting")
    assembly_process = sma_mounting.get("assembly_process_gate", {})
    if set(assembly_process) != {"factory_route", "fallback_route", "acceptance_record"}:
        errors.append("main SMA dual-face assembly-process qualification drifted")
    elif "five visibly wetted rectangular joints" not in assembly_process["acceptance_record"]:
        errors.append("main SMA assembly acceptance no longer proves all five joints")
    hobby_verification = sma_mounting.get("hobby_grade_preorder_verification", {})
    if (
        set(hobby_verification) != {"scope", "design_analysis_inputs", "structural_requirements", "checks"}
        or "no drop" not in hobby_verification.get("scope", "")
        or "prescribed mating-cycle count" not in hobby_verification.get("scope", "")
        or "design-analysis input" not in hobby_verification.get("design_analysis_inputs", "")
        or "strain relief" not in hobby_verification.get("structural_requirements", "")
        or "geometry" not in hobby_verification.get("checks", "")
        or "continuity" not in hobby_verification.get("checks", "")
    ):
        errors.append("main SMA hobby-grade pre-order verification contract drifted")
    if "drop_profile" in sma_mounting:
        errors.append("main SMA destructive drop profile is forbidden")
    gates = sma_mounting.get("verification_gates", {})
    if set(gates) != {"H5", "H7", "H8"}:
        errors.append("main SMA documentary/assembly/hobby-verification gates drifted")
    retention = model["mechanical_retention"]
    if retention["compression_stops"]["count"] != 4:
        errors.append("M1 retention requires four compression stops")
    if retention["compression_stops"]["exact_working_length_mm"] != model["stack"]["interboard_gap_mm"]:
        errors.append("compression-stop length differs from the interboard gap")
    if retention["anti_shear_datums_min"] < 2:
        errors.append("M1 retention requires at least two anti-shear datums")
    holder = model["battery_holder_mechanics"]
    if holder["mounting"] != "SMT" or holder["manufacturer_body_mm"][0] >= holder["pcb_pad_span_mm"][0]:
        errors.append("Keystone 1048P body/pad-span model is invalid")
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "fail" if errors else "pass_with_open_h1_blockers" if model["current_h1_blockers"] else "pass",
        "structural_status": "pass" if not errors else "fail",
        "base_model": model["base_model"],
        "new_fixed_body_count": sum(x["item"]["kind"] == "fixed_body" for x in new),
        "new_reserve_count": sum(x["item"]["kind"] == "reserve" for x in new),
        "placement_drawing_reference_count": len(drawing_refs),
        "duplicate_placement_drawing_references": duplicate_refs,
        "replaced_seed_instances": sorted(replaced),
        "same_face_collisions": same_face,
        "opposing_overlap_count": len(cross),
        "minimum_opposing_clearance_mm": min_cross,
        "required_opposing_clearance_mm": minimum,
        "opposing_overlaps": cross,
        "intentional_opposing_mates": mated,
        "physical_features": features,
        "u219_contract": u219_contract,
        "tx_evidence_physical_register": tx_evidence,
        "cap_bus_slot": cap_slot,
        "cap_evidence_coordinate_register": cap_evidence_register,
        "silkscreen": silk,
        "main_sma_mounting": sma_mounting,
        "through_hole_sma_candidate": through_hole_candidate,
        "mechanical_retention": retention,
        "battery_holder_mechanics": holder,
        "relocated_c5_dbg_header": relocated_c5["id"] if relocated_c5 else None,
        "errors": errors,
        "current_h1_blockers": model["current_h1_blockers"],
        "dependent_h1_work": model["dependent_h1_work"],
        "downstream_verification": model["downstream_verification"],
        "placements": [
            {
                "id": x["item"]["id"],
                "kind": x["item"]["kind"],
                "frame": x["item"]["frame"],
                "mpn": x["item"].get("mpn"),
                "role": x["item"]["role"],
                "world_bbox_mm": x["bbox"],
            }
            for x in new
        ],
    }


def render_svg(model: dict, base: dict, result: dict) -> str:
    height = max(850, 220 + len(model["placements"]) * 59)
    scale = 3.20
    ox = {"ui-inner": 70.0, "rf-inner": 410.0}
    oy = 122.0
    board_w, board_h = model["board_mm"]
    colours = {
        "hub_rp": ("#dcfce7", "#15803d"),
        "airband": ("#fef3c7", "#b45309"),
        "fpv": ("#dbeafe", "#1d4ed8"),
    }

    def esc(value: object) -> str:
        return html.escape(str(value))

    def rect(x: float, y: float, w: float, h: float, **attrs: object) -> str:
        tail = " ".join(f'{k.replace("_", "-")}="{esc(v)}"' for k, v in attrs.items())
        return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" {tail}/>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="{height}" viewBox="0 0 1380 {height}">',
        f'<rect width="1380" height="{height}" fill="#ffffff"/>',
        f'<text x="40" y="42" font-family="sans-serif" font-size="26" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} inner placement</text>',
        '<text x="40" y="70" font-family="sans-serif" font-size="13" fill="#526076">World-scale engineering view · both inner faces are shown directly after turning each PCB over · numbered marks are documentation, never inner-face silkscreen.</text>',
    ]
    for frame, title in (("ui-inner", "UI PCB · inner · turned-over view"), ("rf-inner", "RF / power PCB · inner · turned-over view")):
        x0 = ox[frame]
        out.append(f'<text x="{x0 + board_w * scale / 2:.2f}" y="96" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="#172033">{esc(title)}</text>')
        out.append(rect(x0, oy, board_w * scale, board_h * scale, fill="#f8fafc", stroke="#334155", stroke_width="2"))
        for row in base["rows"]:
            if row["source_frame"] != frame:
                continue
            if row["instance"] in set(result["replaced_seed_instances"]):
                continue
            b = row["world_bbox_mm"]
            x = b["x"][0]
            x = board_w - b["x"][1]
            out.append(rect(x0 + x * scale, oy + b["y"][0] * scale, (b["x"][1] - b["x"][0]) * scale, (b["y"][1] - b["y"][0]) * scale, fill="#e2e8f0", stroke="#cbd5e1", stroke_width="0.7"))

        for item in model["placements"]:
            if item["frame"] != frame:
                continue
            x, y = item["world_xy_mm"]
            w, h, _ = item["size_mm"]
            x = board_w - x - w
            family = "airband" if item["id"].startswith("airband") else "hub_rp"
            fill, stroke = colours[family]
            dash = "6 4" if item["kind"] == "reserve" else "none"
            out.append(rect(x0 + x * scale, oy + y * scale, w * scale, h * scale, rx="3", fill=fill, fill_opacity="0.92", stroke=stroke, stroke_width="2", stroke_dasharray=dash))
            label = item["drawing_ref"]
            tx = x0 + (x + w / 2) * scale
            ty = oy + (y + h / 2) * scale
            font = 11 if w >= 6 else 8.5
            out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="{font}" font-weight="700" fill="{stroke}">{esc(label)}</text>')

    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/></marker></defs>')

    note_x = 730
    out.extend([
        f'<text x="{note_x}" y="112" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Placed devices and allocations</text>',
    ])
    y = 140
    for item in model["placements"]:
        ref = item["drawing_ref"]
        mpn = item.get("mpn") or "physical reserve"
        role = item["role"]
        out.append(f'<text x="{note_x}" y="{y}" font-family="sans-serif" font-size="11.5" font-weight="700" fill="#172033">{esc(ref)} · {esc(mpn)}</text>')
        role_lines = textwrap.wrap(role, width=44, break_long_words=False, break_on_hyphens=False)
        for offset, line in enumerate(role_lines):
            out.append(f'<text x="{note_x + 25}" y="{y + 17 + offset * 14}" font-family="sans-serif" font-size="10.5" fill="#526076">{esc(line)}</text>')
        y += 31 + len(role_lines) * 14
    audit_x = 1100
    out.extend([
        f'<text x="{audit_x}" y="112" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Machine audit</text>',
        f'<text x="{audit_x}" y="142" font-family="sans-serif" font-size="12" fill="#166534">✓ same-face collisions: {len(result["same_face_collisions"])}</text>',
        f'<text x="{audit_x}" y="164" font-family="sans-serif" font-size="12" fill="#166534">✓ opposing crossings: {result["opposing_overlap_count"]}</text>',
        f'<text x="{audit_x}" y="186" font-family="sans-serif" font-size="12" fill="#166534">✓ minimum Z clearance: {result["minimum_opposing_clearance_mm"]:.2f} mm</text>',
        f'<text x="{audit_x}" y="208" font-family="sans-serif" font-size="12" fill="#526076">required: {result["required_opposing_clearance_mm"]:.2f} mm</text>',
        f'<text x="{audit_x}" y="248" font-family="sans-serif" font-size="15" font-weight="700" fill="#172033">Line key</text>',
        f'<line x1="{audit_x}" y1="270" x2="{audit_x + 34}" y2="270" stroke="#0f766e" stroke-width="3"/>',
        f'<text x="{audit_x + 44}" y="274" font-family="sans-serif" font-size="11" fill="#526076">50 Ω RF PCB trace</text>',
        f'<line x1="{audit_x}" y1="294" x2="{audit_x + 34}" y2="294" stroke="#7c3aed" stroke-width="3"/>',
        f'<text x="{audit_x + 44}" y="298" font-family="sans-serif" font-size="11" fill="#526076">75 Ω CVBS PCB trace</text>',
        f'<text x="{audit_x}" y="344" font-family="sans-serif" font-size="13.5" font-weight="700" fill="#b42318">H1 mock-up blockers: {len(model["current_h1_blockers"])} · structural audit {result["structural_status"]}</text>',
    ])
    y = 370
    for gate in model["current_h1_blockers"]:
        gate_lines = textwrap.wrap(gate, width=38, break_long_words=False, break_on_hyphens=False)
        for offset, line in enumerate(gate_lines):
            prefix = "• " if offset == 0 else "  "
            out.append(f'<text x="{audit_x}" y="{y}" font-family="sans-serif" font-size="10.5" fill="#9a3412">{esc(prefix + line)}</text>')
            y += 15
        y += 6
    out.append(f'<text x="{audit_x}" y="{y + 10}" font-family="sans-serif" font-size="14" font-weight="700" fill="#526076">Final H1 acceptance input</text>')
    y += 36
    for gate in model["dependent_h1_work"]:
        gate_lines = textwrap.wrap(gate, width=38, break_long_words=False, break_on_hyphens=False)
        for offset, line in enumerate(gate_lines):
            prefix = "• " if offset == 0 else "  "
            out.append(f'<text x="{audit_x}" y="{y}" font-family="sans-serif" font-size="10.5" fill="#526076">{esc(prefix + line)}</text>')
            y += 15
        y += 6
    out.append('</svg>')
    return "\n".join(out) + "\n"


def render_external_svg(model: dict) -> str:
    """Reuse the mature exterior drawing and add every accepted R2 interface."""
    legacy = legacy_generator()
    devices, _candidate, instances, *_rest = legacy.load()
    legacy.FRONT_RF = tuple(
        (centre, path, "RP-SMA" if path in {"S3-2G4", "C5-2G4/5"} else "SMA")
        for centre, path in zip(
            model["antenna_bank_optimization"]["front_x_centres_mm"],
            model["antenna_bank_optimization"]["front_paths"],
        )
    )
    legacy.REAR_RF = tuple(
        (centre, path, "SMA")
        for centre, path in zip(
            model["antenna_bank_optimization"]["rear_x_centres_mm"],
            model["antenna_bank_optimization"]["rear_paths"],
        )
    )
    silk_rows = model["antenna_silkscreen"]["front"] + model["antenna_silkscreen"]["rear"]
    legacy.RF_USER_LABEL_LINES = {row["path"]: (row["text"],) for row in silk_rows}
    legacy.RF_COMPACT_LABEL_POSITIONS = {
        row["path"]: (row["x_mm"], row["baseline_y_mm"]) for row in silk_rows
    }
    # All USB-C openings are redrawn below from one role-aware primitive.
    # Removing only their legacy bottom projections prevents duplicate arrows
    # and makes powered versus data-only ports visually unambiguous.
    usb_instances = {
        "c5_service_usb_connector", "product_usb_connector", "rp_service_usb_connector"
    }
    legacy.EDGE_INTERFACES = tuple(
        row for row in legacy.EDGE_INTERFACES if row[0] not in usb_instances
    )
    svg = legacy.render_external(devices, instances)
    marker = html.escape(model["marker"])
    svg = svg.replace(
        'data-review-gate="H1.3.1" data-review-status="reviewed"',
        f'data-marker="{marker}" data-review-status="reviewed"',
    ).replace(
        'data-review-status="ready-for-user-acceptance"',
        'data-review-status="reviewed"',
    ).replace(
        "Leshy2 — dimensioned external layout",
        f"Leshy2 — {marker} current external layout",
    ).replace(
        "Text on a PCB face but outside component outlines is intended silkscreen; text outside PCB faces or inside outlines is drawing annotation.",
        "Reviewed R2 exterior. PCB-face free text is silkscreen; drawing notes and arrows are annotations.",
    ).replace(
        "M5Stack U214 · installed worst-case · 84×24 mm",
        "Cap-Bus slot · U214 / U219 · 84×24 mm",
    )
    scale = 3.7
    front = (80.0, 150.0)
    rear = (465.0, 150.0)

    def px(origin: tuple[float, float], mm: float) -> float:
        return origin[0] + mm * scale

    def py(origin: tuple[float, float], mm: float) -> float:
        return origin[1] + mm * scale

    def label(x: float, y: float, value: str, anchor: str = "start", size: float = 5.3) -> str:
        return (
            f'<text data-layer="pcb-silkscreen" x="{x:.1f}" y="{y:.1f}" '
            f'font-family="sans-serif" font-size="{size}" font-weight="bold" '
            f'text-anchor="{anchor}" fill="#1d4ed8">{html.escape(value)}</text>'
        )

    # The legacy exterior used a separate 149-mm baseline for the microphone,
    # microSD and M5 labels.  Normalize every bottom-edge interface to the same
    # two-row grid used by USB: owner at 145.1 mm, role/single label at 147.0 mm.
    # These are actual PCB-silkscreen positions; outward arrows remain drawing
    # annotation and are deliberately excluded from the baseline rule.
    bottom_role_y = py(front, BOTTOM_SILK_ROLE_BASELINE_MM)
    for value in ("MICROPHONE", "microSD", "M5 UNIT"):
        svg = re.sub(
            rf'(<text data-layer="pcb-silkscreen" x="[^"]+" )y="[^"]+"([^>]*>{re.escape(value)}</text>)',
            rf'\1y="{bottom_role_y:.1f}" data-edge="bottom" data-silk-row="role"\2',
            svg,
        )

    additions = [
        f'<g id="h1-r2-external-delta" data-marker="{marker}" data-state="in-progress">',
    ]
    for face, origin in (("front", front), ("rear", rear)):
        for row in model["hardware_identification"]["silkscreen"][face]:
            if row["render_by"] != "r2":
                continue
            additions.append(
                label(
                    px(origin, row["x_mm"]),
                    py(origin, row["baseline_y_mm"]),
                    row["text"],
                    "middle",
                    row["font_size_px"],
                )
                .replace("#1d4ed8", "#172033")
                .replace("<text ", f'<text data-role="board-identification" data-face="{face}" ')
            )
    usb_ports = (
        (front, 16.47, "hub_service_usb_connector", "HUB RP", "DATA USB", False),
        (front, 31.47, "c5_service_usb_connector", "C5", "DATA USB", False),
        (rear, 16.47, "product_usb_connector", "S3", "POWER + USB", True),
        (rear, 37.47, "rp_service_usb_connector", "RF RP", "DATA USB", False),
    )
    for origin, cx, instance, owner, role, powered in usb_ports:
        stroke = "#16a34a" if powered else "#2563eb"
        additions.extend(
            [
                f'<path d="M{px(origin,cx):.1f} {py(origin,150):.1f} V{py(origin,158):.1f}" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrow)" data-instance="{instance}" data-mpn="USB4105-GF-A" data-port-role="{"power-and-data" if powered else "data-only"}"/>',
                label(px(origin,cx), py(origin,BOTTOM_SILK_OWNER_BASELINE_MM), owner, "middle", 4.7)
                .replace("#1d4ed8", stroke)
                .replace("<text ", '<text data-edge="bottom" data-silk-row="owner" '),
                label(px(origin,cx), py(origin,BOTTOM_SILK_ROLE_BASELINE_MM), role, "middle", 4.2)
                .replace("#1d4ed8", stroke)
                .replace("<text ", '<text data-edge="bottom" data-silk-row="role" '),
            ]
        )
    for item in model["placements"]:
        if item["id"] not in {"hub_reset_button", "hub_boot_button"}:
            continue
        x, y = item["world_xy_mm"]
        w, h, _z = item["size_mm"]
        cy = y + h / 2
        visible = item["external_interface"]["label"]
        additions.extend(
            [
                # Hub uses the exact same Alps side switch and 1.2-mm DIV-like
                # protective recess as S3/C5/RF-RP.  Keep all three layers so
                # the exterior does not make one identical MPN look like a
                # different control: inner-mounted body, recess and actuator.
                f'<rect x="{px(front,x):.1f}" y="{py(front,y):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" rx="1" fill="none" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="2 2" data-instance="{item["id"]}" data-mpn="SKRTLAE010" data-projection="inner-mounted-side-switch"/>',
                f'<rect x="{px(front,73.3):.1f}" y="{py(front,cy-2.5):.1f}" width="{2.5*scale:.1f}" height="{5.0*scale:.1f}" rx="2" fill="none" stroke="#ea580c" stroke-width="1.5" stroke-dasharray="3 2" data-instance="{item["id"]}" data-part="protective-recess" data-recess-mm="1.2"/>',
                f'<path d="M{px(front,73.8):.1f} {py(front,cy-1.4):.1f} V{py(front,cy+1.4):.1f}" stroke="#7c3aed" stroke-width="4" stroke-linecap="square" data-instance="{item["id"]}" data-part="side-actuator" data-recessed="true"/>',
                f'<path d="M{px(front,82):.1f} {py(front,cy):.1f} L{px(front,73.8):.1f} {py(front,cy):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>',
                label(px(front,68), py(front,cy), visible, "middle", 4.2).replace("#1d4ed8", "#7c3aed"),
            ]
        )
    additions.append('</g>')
    return svg.replace("</svg>", "\n".join(additions) + "\n</svg>")


def render_service_svg(model: dict) -> str:
    """Draw the complete four-domain USB and eight-button recovery surface."""
    esc = html.escape
    scale = 3.35
    board_w, board_h = model["board_mm"]
    front = (110.0, 125.0)
    rear = (520.0, 125.0)

    def x(origin: tuple[float, float], mm: float) -> float:
        return origin[0] + mm * scale

    def y(origin: tuple[float, float], mm: float) -> float:
        return origin[1] + mm * scale

    def t(px: float, py: float, value: str, size=11, weight="normal", anchor="start", colour="#172033", silk=False) -> str:
        layer = ' data-layer="pcb-silkscreen"' if silk else ""
        return f'<text{layer} x="{px:.1f}" y="{py:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 38, f'Leshy2 — {model["marker"]} external service access', 24, "bold"),
        t(30, 66, "Four independent USB paths, eight recessed recovery controls and four internal keyed DBG10 fallbacks.", 12, colour="#526076"),
    ]
    for origin, title in ((front, "Front / UI face"), (rear, "Rear / battery face")):
        out.extend(
            [
                t(x(origin, board_w/2), 105, title, 16, "bold", "middle"),
                f'<rect x="{x(origin,0):.1f}" y="{y(origin,0):.1f}" width="{board_w*scale:.1f}" height="{board_h*scale:.1f}" rx="7" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
            ]
        )

    # Side controls: exact accepted positions. Text inside the PCB outline is
    # the actual outer-face silkscreen; the red arrows are drawing annotation.
    controls = [
        (front, "left", 117.25, "S3 RST"), (front, "left", 124.25, "S3 BOOT"),
        (front, "right", 117.25, "C5 RST"), (front, "right", 124.25, "C5 BOOT"),
        (front, "right", 132.25, "HUB RST"), (front, "right", 139.25, "HUB BOOT"),
        (rear, "left", 108.25, "RF RP RST"), (rear, "left", 115.25, "RF RP BOOT"),
    ]
    for origin, side, cy, visible in controls:
        edge = 0.0 if side == "left" else board_w
        outside = -9.0 if side == "left" else board_w + 9.0
        anchor = "start" if side == "left" else "end"
        label_x = 3.2 if side == "left" else board_w - 3.2
        out.append(f'<rect x="{x(origin,edge-0.7 if side=="left" else edge-0.5):.1f}" y="{y(origin,cy-1.8):.1f}" width="{1.2*scale:.1f}" height="{3.6*scale:.1f}" rx="2" fill="#ede9fe" stroke="#7c3aed" data-recessed="true" data-mpn="SKRTLAE010"/>')
        out.append(f'<path d="M{x(origin,edge):.1f} {y(origin,cy):.1f} L{x(origin,outside):.1f} {y(origin,cy):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(t(x(origin,label_x), y(origin,cy-0.7), visible, 7.0, "bold", anchor, "#6d28d9", True))

    # Exact user connectors. All four USB openings now face the bottom edge.
    # Service VBUS remains sense-only and cannot power Leshy2.
    bottom_ports = [
        (front, 16.47, "hub_service_usb_connector", "HUB RP", "DATA USB", "data only", False),
        (front, 31.47, "c5_service_usb_connector", "C5", "DATA USB", "data only", False),
        (rear, 16.47, "product_usb_connector", "S3", "POWER + USB", "native USB + power/charge", True),
        (rear, 37.47, "rp_service_usb_connector", "RF RP", "DATA USB", "data only", False),
    ]
    for origin, cx, instance, owner, role, note, powered in bottom_ports:
        stroke = "#16a34a" if powered else "#2563eb"
        out.append(f'<path d="M{x(origin,cx):.1f} {y(origin,board_h):.1f} L{x(origin,cx):.1f} {y(origin,board_h)+34:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)" data-instance="{instance}" data-mpn="USB4105-GF-A" data-port-role="{"power-and-data" if powered else "data-only"}"/>')
        out.append(t(x(origin,cx), y(origin,BOTTOM_SILK_OWNER_BASELINE_MM), owner, 6.7, "bold", "middle", stroke, True))
        out.append(t(x(origin,cx), y(origin,BOTTOM_SILK_ROLE_BASELINE_MM), role, 6.2, "bold", "middle", stroke, True))
        out.append(t(x(origin,cx), y(origin,board_h)+50, note, 7.2, anchor="middle", colour="#526076"))
    out.extend(
        [
            t(940, 130, "Recovery map", 18, "bold"),
            t(940, 164, "S3", 13, "bold", colour="#6d28d9"), t(990, 164, "USB / POWER + RST + BOOT", 11),
            t(940, 196, "C5", 13, "bold", colour="#6d28d9"), t(990, 196, "SERVICE USB + RST + BOOT", 11),
            t(940, 228, "RF RP", 13, "bold", colour="#6d28d9"), t(990, 228, "SERVICE USB + RUN + USB_BOOT", 11),
            t(940, 260, "HUB RP", 13, "bold", colour="#6d28d9"), t(1010, 260, "SERVICE USB + RUN + USB_BOOT", 11),
            t(940, 315, "Inside after opening", 17, "bold"),
            t(940, 348, "4× FTSH-105-01-L-DV-K-P-TR keyed DBG10", 11, "bold"),
            t(940, 376, "S3/C5: UART0 · RESET · BOOT", 10),
            t(940, 402, "RF RP/Hub RP: SWD · RUN · USB_BOOT", 10),
            t(940, 452, "Port policy", 17, "bold"),
            t(940, 484, "• USB / POWER is the sole powered USB port", 10),
            t(940, 510, "• C5, RF RP and Hub VBUS are sense-only", 10),
            t(940, 536, "• every RST/BOOT control is recessed and independent", 10),
            t(940, 562, "• Pack and Safety use isolated internal fixtures", 10),
            t(940, 620, "Exact live JLCPCB routes · 2026-08-27", 14, "bold", colour="#166534"),
            t(940, 650, "USB4105-GF-A · C3020560 · 3,712 pcs", 10),
            t(940, 676, "SKRTLAE010 · C110293 · 49,305 pcs", 10),
            t(940, 702, "FTSH-105-01-L-DV-K-P-TR · C2932107 · 11,433 pcs", 10),
        ]
    )
    out.append('</svg>')
    return "\n".join(out) + "\n"


def complete_inner_rows(model: dict, base: dict, source_table: dict, result: dict) -> list[dict]:
    """Merge unchanged registered R1 bodies with every explicit R2 body/reserve."""
    sources = {row["instance"]: row for row in source_table["rows"]}
    replaced = set(result["replaced_seed_instances"])
    rows: list[dict] = []
    for row in base["rows"]:
        if row["source_frame"] not in {"ui-inner", "rf-inner"}:
            continue
        if row["instance"] in replaced:
            continue
        source = sources[row["instance"]]
        rows.append(
            {
                "id": row["instance"],
                "frame": row["source_frame"],
                "bbox": row["world_bbox_mm"],
                "mpn": source["mpn"],
                "role": source["role"],
                "kind": "fixed_body",
                "origin": "current registered body",
            }
        )
    for item in model["placements"]:
        if item["frame"] not in {"ui-inner", "rf-inner"}:
            continue
        b = bbox(item, model)
        rows.append(
            {
                "id": item["id"],
                "frame": item["frame"],
                "bbox": b,
                "mpn": item.get("mpn") or "PHYSICAL RESERVE",
                "role": item["role"],
                "kind": item["kind"],
                "origin": "R2 placement",
            }
        )
    return sorted(rows, key=lambda row: (row["frame"], row["bbox"]["y"][0], row["bbox"]["x"][0], row["id"]))


def located_physical_features(model: dict, frame: str) -> list[dict]:
    """Return drawable non-component geometry; unresolved copper stays a gate."""
    return [
        feature for feature in model.get("physical_features", [])
        if feature["frame"] == frame and feature.get("world_bbox_mm") is not None
    ]


def r2_antenna_topology(model: dict, rows: list[dict]) -> dict:
    """Return the one truthful R2 antenna-media model used by every inner view.

    Coordinates are physical world millimetres.  PCB segments express topology,
    never finished KiCad geometry.  Removable microcoaxes are separate objects.
    """
    row_by_id = {row["id"]: row for row in rows}
    port_centres = {
        path: (centre, 0.0)
        for path, centre in zip(
            model["antenna_bank_optimization"]["front_paths"]
            + model["antenna_bank_optimization"]["rear_paths"],
            model["antenna_bank_optimization"]["front_x_centres_mm"]
            + model["antenna_bank_optimization"]["rear_x_centres_mm"],
        )
    }

    def centre(instance: str) -> tuple[float, float]:
        box = row_by_id[instance]["bbox"]
        return ((box["x"][0] + box["x"][1]) / 2, (box["y"][0] + box["y"][1]) / 2)

    pcb_segments: list[dict] = []
    cables: list[dict] = []
    connectors: list[dict] = []

    front_sources = {
        "N24-0": ("nrf0_r2", "nrf0_rf_board_connector_r2", "IPEX"),
        "S3-2G4": ("s3", "s3_rf_board_connector_r2", "U.FL"),
        "N24-1": ("nrf1_r2", "nrf1_rf_board_connector_r2", "IPEX"),
        "C5-2G4/5": ("c5", "c5_rf_board_connector_r2", "U.FL"),
        "N24-2": ("nrf2_r2", "nrf2_rf_board_connector_r2", "IPEX"),
    }
    front_couplers = {
        "S3-2G4": "s3_rf_coupler_r2",
        "C5-2G4/5": "c5_rf_coupler_r2",
    }
    for path, (source_id, connector_id, source_kind) in front_sources.items():
        cable_spec = model["antenna_bank_optimization"]["microcoax_by_path"][path]
        source_point = centre(source_id)
        connector_point = centre(connector_id)
        trace_points = [connector_point]
        if path in front_couplers:
            trace_points.append(centre(front_couplers[path]))
        trace_points.append(port_centres[path])
        pcb_segments.append(
            {
                "frame": "ui-inner",
                "path": path,
                "branch": "main",
                "points": trace_points,
                "medium": "controlled-50-ohm-pcb",
                "stroke": "#2563eb",
                "width": 1.7,
                "dash": None,
            }
        )
        cables.append(
            {
                "frame": "ui-inner",
                "path": path,
                "points": [source_point, connector_point],
                "medium": "removable-microcoax",
                "device_id": cable_spec["device_id"],
                "mpn": cable_spec["mpn"],
                "length_mm": cable_spec["length_mm"],
                "stroke": "#0f766e",
                "width": 3.2,
            }
        )
        connectors.extend(
            [
                {"frame": "ui-inner", "path": path, "point": source_point, "part": "module-rf-connector", "kind": source_kind},
                {"frame": "ui-inner", "path": path, "point": connector_point, "part": "board-ufl", "kind": "U.FL"},
            ]
        )

    # Two voice feeds are controlled 50-ohm traces from module contact 12.
    for path, source_id in (("VOICE-VHF", "voice_v"), ("VOICE-UHF", "voice")):
        pcb_segments.append(
            {
                "frame": "rf-inner", "path": path, "branch": "main",
                "points": [centre(source_id), port_centres[path]],
                "medium": "controlled-50-ohm-pcb", "stroke": "#2563eb", "width": 1.7, "dash": None,
            }
        )

    # CC1101 reaches 50 ohms through its selected matching branch; the straight
    # guide must not imply that the RF IC pin itself is a 50-ohm endpoint.
    pcb_segments.append(
        {
            "frame": "rf-inner", "path": "CC-SUB", "branch": "matched-main",
            "points": [centre("cc_r2"), port_centres["CC-SUB"]],
            "medium": "matched-rf-pcb-topology", "stroke": "#2563eb", "width": 1.7, "dash": None,
        }
    )

    # AMI is deliberately not presented as a 50-ohm feed.  The external ferrite
    # pod reaches the Si4732 high-impedance AMI input through ESD and AC coupling.
    pcb_segments.append(
        {
            "frame": "rf-inner", "path": "RX-AM/LW", "branch": "ami",
            "points": [port_centres["RX-AM/LW"], centre("receiver_r2")],
            "medium": "high-impedance-ami-pcb", "stroke": "#7c3aed", "width": 1.9, "dash": None,
        }
    )

    # FM/SW and Airband share one SMA, then split.  Direct FM/SW bypasses the
    # powered converter chain; Airband passes the reserved BPF/IF cell, LNA and
    # mixer before the selector.  SI5351 supplies the separate 112-MHz LO.
    selector = centre("airband_selector")
    receiver = centre("receiver_r2")
    pcb_segments.extend(
        [
            {
                "frame": "rf-inner", "path": "RX-FM/SW", "branch": "direct-fm-sw",
                "points": [port_centres["RX-FM/SW"], selector, receiver],
                "medium": "direct-fm-sw-pcb", "stroke": "#2563eb", "width": 1.7, "dash": None,
            },
            {
                "frame": "rf-inner", "path": "RX-FM/SW", "branch": "converted-airband",
                "points": [port_centres["RX-FM/SW"], centre("airband_lna"), centre("airband_mixer"), selector],
                "medium": "converted-airband-rf-if-pcb", "stroke": "#ea580c", "width": 2.0, "dash": None,
            },
            {
                "frame": "rf-inner", "path": "RX-FM/SW", "branch": "airband-lo",
                "points": [centre("airband_lo"), centre("airband_mixer")],
                "medium": "112-mhz-local-oscillator-pcb", "stroke": "#ea580c", "width": 1.5, "dash": "4 3",
            },
        ]
    )
    return {"pcb_segments": pcb_segments, "cables": cables, "connectors": connectors}


def r2_microcoax_audit(model: dict, rows: list[dict], topology: dict) -> dict:
    """Prove every selected cable reaches without pretending the nRF axis is centred.

    S3/C5 retain source-backed connector axes from the accepted module drawings.
    For each E01-ML01SP4, the farthest point of the complete maximum module body
    is deliberately used.  The published IPEX socket lies inside that body, so a
    positive result is conservative even before its received-lot mate is checked.
    """
    row_by_id = {row["id"]: row for row in rows}
    candidate = load(CANDIDATE_PATH)
    devices = load(DEVICES_PATH)["devices"]
    cable_by_path = {row["path"]: row for row in topology["cables"]}
    source_by_path = {
        "N24-0": ("nrf0_r2", "nrf0_rf_board_connector_r2", "nrf0_rf_jumper"),
        "S3-2G4": ("s3", "s3_rf_board_connector_r2", "s3_rf_jumper"),
        "N24-1": ("nrf1_r2", "nrf1_rf_board_connector_r2", "nrf1_rf_jumper"),
        "C5-2G4/5": ("c5", "c5_rf_board_connector_r2", "c5_rf_jumper"),
        "N24-2": ("nrf2_r2", "nrf2_rf_board_connector_r2", "nrf2_rf_jumper"),
    }
    exact_native_axes = {
        "S3-2G4": [21.0, 24.46],
        "C5-2G4/5": [66.0, 24.38],
    }
    entries = []
    errors = []
    for path, (source_id, connector_id, candidate_instance) in source_by_path.items():
        source_box = row_by_id[source_id]["bbox"]
        connector_box = row_by_id[connector_id]["bbox"]
        connector_point = [
            (connector_box["x"][0] + connector_box["x"][1]) / 2,
            (connector_box["y"][0] + connector_box["y"][1]) / 2,
        ]
        if path in exact_native_axes:
            source_point = exact_native_axes[path]
            projection = math.hypot(
                source_point[0] - connector_point[0],
                source_point[1] - connector_point[1],
            )
            projection_basis = "exact module connector axis to board-U.FL centre"
        else:
            projection = max(
                math.hypot(x - connector_point[0], y - connector_point[1])
                for x in source_box["x"]
                for y in source_box["y"]
            )
            source_point = None
            projection_basis = "farthest maximum-module-envelope corner to board-U.FL centre"
        cable = cable_by_path[path]
        selected_device_id = candidate["instances"][candidate_instance]
        selected = devices[selected_device_id]
        length = float(selected["electrical_contract"]["cable_length_mm"])
        slack = length - projection
        if selected_device_id != cable["device_id"]:
            errors.append(f"{path}: candidate and placement cable identities differ")
        if selected["mpn"] != cable["mpn"] or length != float(cable["length_mm"]):
            errors.append(f"{path}: selected cable MPN/length differs from placement contract")
        if slack < 5.0:
            errors.append(f"{path}: conservative cable slack is only {slack:.3f} mm")
        entries.append({
            "path": path,
            "source_instance": source_id,
            "board_connector_instance": connector_id,
            "selected_device_id": selected_device_id,
            "mpn": selected["mpn"],
            "length_mm": length,
            "projection_mm": round(projection, 3),
            "minimum_conservative_slack_mm": round(slack, 3),
            "projection_basis": projection_basis,
            "source_connector_point_mm": source_point,
            "board_connector_point_mm": connector_point,
        })
    return {
        "status": "pass" if not errors else "fail",
        "paths": entries,
        "path_count": len(entries),
        "thirty_mm_paths": sum(row["length_mm"] == 30.0 for row in entries),
        "sixty_mm_paths": sum(row["length_mm"] == 60.0 for row in entries),
        "minimum_conservative_slack_mm": min(row["minimum_conservative_slack_mm"] for row in entries),
        "received_only_gate": "connector mating, bend radius, strain relief and routed service loop remain J4-F/H8 physical evidence",
        "errors": errors,
    }


def render_complete_inner_svg(model: dict, base: dict, source_table: dict, result: dict) -> str:
    """Render every mechanically registered inner body with an exact legend."""
    legacy = legacy_generator()
    rows = complete_inner_rows(model, base, source_table, result)
    board_w, board_h = model["board_mm"]
    scale = 3.65
    ui = (65.0, 130.0)
    rf = (440.0, 130.0)
    origins = {"ui-inner": ui, "rf-inner": rf}
    columns = 4
    legend_rows = math.ceil(len(rows) / columns)
    row_h = 50
    legend_y = 760
    height = legend_y + legend_rows * row_h + 100
    width = 1900
    esc = html.escape

    def sx(origin: tuple[float, float], world_x: float, body_w: float = 0.0) -> float:
        return origin[0] + (board_w - world_x - body_w) * scale

    def sy(origin: tuple[float, float], world_y: float) -> float:
        return origin[1] + world_y * scale

    def t(x: float, y: float, value: str, size=10, weight="normal", anchor="start", colour="#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" data-marker="{esc(model["marker"])}" data-view="both-inner-faces-mirrored" data-inner-silkscreen="none">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        t(30, 40, f'Leshy2 — {model["marker"]} complete inner-body map', 24, "bold"),
        t(30, 68, "Each PCB is shown exactly as viewed after turning it over. Numbers are drawing references; inner faces contain no silkscreen.", 12, colour="#526076"),
    ]
    for frame, title in (("ui-inner", "UI PCB · inner · turned-over view"), ("rf-inner", "RF / power PCB · inner · turned-over view")):
        origin = origins[frame]
        out.append(t(origin[0] + board_w*scale/2, 110, title, 16, "bold", "middle"))
        out.append(f'<rect x="{origin[0]:.1f}" y="{origin[1]:.1f}" width="{board_w*scale:.1f}" height="{board_h*scale:.1f}" rx="7" fill="#f8fafc" stroke="#334155" stroke-width="2"/>')
        for hole_x, hole_y in legacy.HOLES:
            out.append(f'<circle cx="{sx(origin,hole_x):.1f}" cy="{sy(origin,hole_y):.1f}" r="{legacy.MOUNT_KEEPOUT_R*scale:.1f}" fill="none" stroke="#f97316" stroke-dasharray="5 3"/>')
        for feature in located_physical_features(model, frame):
            box = feature["world_bbox_mm"]
            feature_w = box["x"][1] - box["x"][0]
            feature_h = box["y"][1] - box["y"][0]
            stroke = "#dc2626" if feature["kind"] == "keepout" else "#7c3aed"
            out.append(
                f'<rect x="{sx(origin,box["x"][0],feature_w):.2f}" y="{sy(origin,box["y"][0]):.2f}" '
                f'width="{feature_w*scale:.2f}" height="{feature_h*scale:.2f}" rx="2" fill="{stroke}" '
                f'fill-opacity="0.06" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="5 3" '
                f'data-physical-feature="{esc(feature["id"])}" data-feature-kind="{feature["kind"]}"/>'
            )

    topology = r2_antenna_topology(model, rows)
    out.append('<g id="antenna-pcb-topology" data-topology-source="r2" data-route-state="pre-ecad-topology-only">')
    for segment in topology["pcb_segments"]:
        origin = origins[segment["frame"]]
        points = " ".join(f'{sx(origin,x):.1f},{sy(origin,y):.1f}' for x, y in segment["points"])
        dash = f' stroke-dasharray="{segment["dash"]}"' if segment["dash"] else ""
        out.append(
            f'<polyline points="{points}" fill="none" stroke="{segment["stroke"]}" '
            f'stroke-width="{segment["width"]}"{dash} data-path="{esc(segment["path"])}" '
            f'data-branch="{esc(segment["branch"])}" data-medium="{esc(segment["medium"])}"/>'
        )
    out.append('</g>')

    numbers = {row["id"]: index for index, row in enumerate(rows, 1)}
    for row in rows:
        origin = origins[row["frame"]]
        b = row["bbox"]
        w = b["x"][1] - b["x"][0]
        h = b["y"][1] - b["y"][0]
        vx = sx(origin, b["x"][0], w)
        vy = sy(origin, b["y"][0])
        if row["kind"] == "reserve":
            fill, stroke, dash = "#fff7ed", "#ea580c", ' stroke-dasharray="6 4"'
        elif row["origin"] == "R2 placement":
            fill, stroke, dash = "#dbeafe", "#2563eb", ""
        else:
            fill, stroke, dash = "#eef2f6", "#94a3b8", ""
        out.append(f'<rect x="{vx:.2f}" y="{vy:.2f}" width="{w*scale:.2f}" height="{h*scale:.2f}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1"{dash} data-instance="{esc(row["id"])}" data-mpn="{esc(row["mpn"])}"/>')
        font = 6.8 if min(w, h) >= 1.6 else 4.8
        out.append(t(vx+w*scale/2, vy+h*scale/2+font/3, str(numbers[row["id"]]), font, "bold", "middle", stroke))

    # Flexible microcoax and its two connector ends sit above the board bodies;
    # keeping them separate from the under-body PCB topology is intentional.
    out.append('<g id="antenna-removable-media" data-topology-source="r2">')
    for cable in topology["cables"]:
        origin = origins[cable["frame"]]
        points = " ".join(f'{sx(origin,x):.1f},{sy(origin,y):.1f}' for x, y in cable["points"])
        out.append(
            f'<polyline points="{points}" fill="none" stroke="{cable["stroke"]}" '
            f'stroke-width="{cable["width"]}" stroke-linecap="round" '
            f'data-path="{esc(cable["path"])}" data-medium="{esc(cable["medium"])}"/>'
        )
    for connector in topology["connectors"]:
        origin = origins[connector["frame"]]
        x, y = connector["point"]
        out.append(
            f'<circle cx="{sx(origin,x):.1f}" cy="{sy(origin,y):.1f}" r="4.0" fill="#ffffff" '
            f'stroke="#0f766e" stroke-width="1.5" data-path="{esc(connector["path"])}" '
            f'data-part="{esc(connector["part"])}" data-connector-kind="{esc(connector["kind"])}"/>'
        )
        out.append(f'<circle cx="{sx(origin,x):.1f}" cy="{sy(origin,y):.1f}" r="1.3" fill="#d97706"/>')
    out.append('</g>')

    rf_origin = origins["rf-inner"]
    # Exact outward interfaces attached to R2 bodies.
    out.append(f'<path d="M{sx(ui,0):.1f} {sy(ui,137.47):.1f} L{sx(ui,-8):.1f} {sy(ui,137.47):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    for cy in (132.25, 139.25):
        out.append(f'<path d="M{sx(ui,75):.1f} {sy(ui,cy):.1f} L{sx(ui,83):.1f} {sy(ui,cy):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    out.append(f'<path d="M{sx(rf_origin,75):.1f} {sy(rf_origin,101.3):.1f} L{sx(rf_origin,83):.1f} {sy(rf_origin,101.3):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')

    out.extend(
        [
            t(30, 720, f'Numbered registered bodies · {len(rows)} total', 17, "bold"),
            t(410, 720, f'R2 structural audit: pass · {len(model["current_h1_blockers"])} open H1 geometry gates · {result["minimum_opposing_clearance_mm"]:.2f} mm minimum opposing gap', 12, "bold", colour="#166534"),
        ]
    )
    column_width = 460
    for index, row in enumerate(rows):
        col = index // legend_rows
        slot = index % legend_rows
        lx = 30 + col * column_width
        ly = legend_y + slot * row_h
        colour = "#1d4ed8" if row["origin"] == "R2 placement" and row["kind"] != "reserve" else "#9a3412" if row["kind"] == "reserve" else "#172033"
        out.append(t(lx, ly, f'{numbers[row["id"]]:03d}  {row["mpn"]}', 8.2, "bold", colour=colour))
        role_lines = textwrap.wrap(row["role"], width=58, break_long_words=False, break_on_hyphens=False)[:2]
        for line_no, line in enumerate(role_lines):
            out.append(t(lx+28, ly+13+line_no*11, line, 7.4, colour="#526076"))
    out.append('</svg>')
    return "\n".join(out) + "\n"


def render_component_legend_svg(model: dict, base: dict, source_table: dict, result: dict) -> str:
    """Render the complete numbered-body legend without repeating either PCB view."""
    rows = complete_inner_rows(model, base, source_table, result)
    columns = 4
    slots = math.ceil(len(rows) / columns)
    width = 1900
    column_width = 465
    row_height = 50
    first_y = 212
    height = first_y + slots * row_height + 55

    def text(x: float, y: float, value: str, size=10, weight="normal", colour="#172033") -> str:
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{colour}">{html.escape(value)}</text>'
        )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" data-marker="{html.escape(model["marker"])}" '
        f'data-view="numbered-component-legend">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        text(30, 42, f'Leshy2 · {model["marker"]} · numbered component legend', 24, "bold"),
        text(30, 72, f'{len(rows)} unique drawing references · MPN or explicit physical reserve · role in the target device', 12, colour="#526076"),
        text(30, 100, 'Bodies — blue: R2 placement · grey: retained register · orange: physical reserve', 11, colour="#526076"),
        text(30, 126, 'Non-component geometry — red: exact PTH keepout · violet: bounded placement island', 11, colour="#526076"),
    ]
    feature_y = 150
    for feature in model.get("physical_features", []):
        location = feature.get("world_bbox_mm")
        location_text = (
            f'X {location["x"][0]:.3g}…{location["x"][1]:.3g} · Y {location["y"][0]:.3g}…{location["y"][1]:.3g} mm'
            if location else "UNLOCATED — explicit H1 geometry gate"
        )
        colour = "#dc2626" if feature["kind"] == "keepout" else "#7c3aed" if location else "#9a3412"
        out.append(text(30, feature_y, f'{feature["id"]} · {feature["kind"]} · {location_text}', 9.0, "bold", colour))
        feature_y += 17
    for index, row in enumerate(rows):
        column = index // slots
        slot = index % slots
        x = 30 + column * column_width
        y = first_y + slot * row_height
        if row["kind"] == "reserve":
            colour = "#9a3412"
        elif row["origin"] == "R2 placement":
            colour = "#1d4ed8"
        else:
            colour = "#172033"
        out.append(text(x, y, f'{index + 1:03d}  {row["mpn"]}', 8.5, "bold", colour))
        role_lines = textwrap.wrap(row["role"], width=61, break_long_words=False, break_on_hyphens=False)[:2]
        for line_number, line in enumerate(role_lines):
            out.append(text(x + 28, y + 14 + line_number * 11, line, 7.4, colour="#526076"))
    out.append('</svg>')
    return "\n".join(out) + "\n"


def render_inner_face_svg(
    model: dict,
    base: dict,
    source_table: dict,
    result: dict,
    frame: str,
) -> str:
    """Render one readable inner face; keep the combined map machine-only."""
    legacy = legacy_generator()
    all_rows = complete_inner_rows(model, base, source_table, result)
    rows = [row for row in all_rows if row["frame"] == frame]
    numbers = {row["id"]: index for index, row in enumerate(all_rows, 1)}
    board_w, board_h = model["board_mm"]
    scale, ox, oy = 5.6, 80.0, 165.0
    width, height = 1160, 1110
    is_ui = frame == "ui-inner"
    face_name = "UI / radio PCB" if is_ui else "RF / power PCB"
    paths = model["antenna_bank_optimization"]["front_paths" if is_ui else "rear_paths"]
    centres = model["antenna_bank_optimization"]["front_x_centres_mm" if is_ui else "rear_x_centres_mm"]

    def sx(world_x: float, body_w: float = 0.0) -> float:
        return ox + (board_w - world_x - body_w) * scale

    def sy(world_y: float) -> float:
        return oy + world_y * scale

    def text(x: float, y: float, value: str, size=10, weight="normal", anchor="start", colour="#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" data-marker="{html.escape(model["marker"])}" data-frame="{frame}" data-inner-silkscreen="none">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(35, 40, f'Leshy2 · {model["marker"]} · {face_name} inner face', 24, "bold"),
        text(35, 68, "Direct view after physically turning the PCB over. Numbers are drawing references; this face has no silkscreen.", 12, colour="#526076"),
        text(ox + board_w*scale/2, 105, "ANTENNA EDGE · five board-local RF paths", 13, "bold", "middle", "#1d4ed8"),
        f'<rect x="{ox}" y="{oy}" width="{board_w*scale:.1f}" height="{board_h*scale:.1f}" rx="7" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
    ]
    for centre, path in zip(centres, paths):
        port_x = sx(centre)
        out.extend([
            f'<rect x="{port_x-5.1*scale:.1f}" y="{oy-6*scale:.1f}" width="{10.2*scale:.1f}" height="{6*scale:.1f}" rx="3" fill="#eef2f6" stroke="#667085" stroke-width="1.5"/>',
            text(port_x, oy-7*scale, path, 8.2, "bold", "middle", "#1d4ed8" if is_ui else "#9a3412"),
        ])
    for hole_x, hole_y in legacy.HOLES:
        out.append(f'<circle cx="{sx(hole_x):.1f}" cy="{sy(hole_y):.1f}" r="{legacy.MOUNT_KEEPOUT_R*scale:.1f}" fill="none" stroke="#f97316" stroke-dasharray="5 3"/>')
    for feature in located_physical_features(model, frame):
        box = feature["world_bbox_mm"]
        feature_w = box["x"][1] - box["x"][0]
        feature_h = box["y"][1] - box["y"][0]
        stroke = "#dc2626" if feature["kind"] == "keepout" else "#7c3aed"
        out.append(
            f'<rect x="{sx(box["x"][0],feature_w):.2f}" y="{sy(box["y"][0]):.2f}" '
            f'width="{feature_w*scale:.2f}" height="{feature_h*scale:.2f}" rx="2" fill="{stroke}" '
            f'fill-opacity="0.06" stroke="{stroke}" stroke-width="1.4" stroke-dasharray="6 4" '
            f'data-physical-feature="{html.escape(feature["id"])}" data-feature-kind="{feature["kind"]}"/>'
        )

    topology = r2_antenna_topology(model, all_rows)
    out.append('<g id="antenna-pcb-topology" data-topology-source="r2" data-route-state="pre-ecad-topology-only">')
    for segment in topology["pcb_segments"]:
        if segment["frame"] != frame:
            continue
        points = " ".join(f'{sx(x):.1f},{sy(y):.1f}' for x, y in segment["points"])
        dash = f' stroke-dasharray="{segment["dash"]}"' if segment["dash"] else ""
        out.append(
            f'<polyline points="{points}" fill="none" stroke="{segment["stroke"]}" '
            f'stroke-width="{segment["width"]}"{dash} data-path="{html.escape(segment["path"])}" '
            f'data-branch="{html.escape(segment["branch"])}" data-medium="{html.escape(segment["medium"])}"/>'
        )
    out.append('</g>')

    for row in rows:
        b = row["bbox"]
        body_w = b["x"][1] - b["x"][0]
        body_d = b["y"][1] - b["y"][0]
        vx, vy = sx(b["x"][0], body_w), sy(b["y"][0])
        if row["kind"] == "reserve":
            fill, stroke, dash = "#fff7ed", "#ea580c", ' stroke-dasharray="6 4"'
        elif row["origin"] == "R2 placement":
            fill, stroke, dash = "#dbeafe", "#2563eb", ""
        else:
            fill, stroke, dash = "#eef2f6", "#94a3b8", ""
        out.append(f'<rect x="{vx:.2f}" y="{vy:.2f}" width="{body_w*scale:.2f}" height="{body_d*scale:.2f}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1"{dash} data-instance="{html.escape(row["id"])}" data-mpn="{html.escape(row["mpn"])}"/>')
        font = 7.0 if min(body_w, body_d) >= 1.6 else 4.8
        if row["id"] == "display_connector":
            # This is drawing annotation, not production silkscreen.  The direct
            # display connector is deliberately called out because its long,
            # shallow outline is otherwise easy to mistake for a passive or a
            # mechanical keepout in the complete inner-face mock-up.
            centre_x = vx + body_w * scale / 2
            out.append(text(centre_x, vy + 8.2, f'{numbers[row["id"]]} · 50-pin ZIF', 7.2, "bold", "middle", stroke))
            out.append(text(centre_x, vy + 17.0, "DISPLAY FPC", 6.4, "bold", "middle", stroke))
        else:
            out.append(text(vx + body_w*scale/2, vy + body_d*scale/2 + font/3, str(numbers[row["id"]]), font, "bold", "middle", stroke))

    # Removable microcoax and its two connector ends are physical objects above
    # the PCB; draw them after the body layer. Rear paths have no such cables.
    out.append('<g id="antenna-removable-media" data-topology-source="r2">')
    for cable in topology["cables"]:
        if cable["frame"] != frame:
            continue
        points = " ".join(f'{sx(x):.1f},{sy(y):.1f}' for x, y in cable["points"])
        out.append(
            f'<polyline points="{points}" fill="none" stroke="{cable["stroke"]}" '
            f'stroke-width="{cable["width"]}" stroke-linecap="round" '
            f'data-path="{html.escape(cable["path"])}" data-medium="{html.escape(cable["medium"])}"/>'
        )
    for connector in topology["connectors"]:
        if connector["frame"] != frame:
            continue
        x, y = connector["point"]
        mpn = ' data-mpn="U.FL-R-SMT-1(80)"' if connector["part"] == "board-ufl" else ""
        out.append(
            f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="6.3" fill="#ffffff" stroke="#0f766e" '
            f'stroke-width="2" data-path="{html.escape(connector["path"])}" '
            f'data-part="{html.escape(connector["part"])}" data-connector-kind="{html.escape(connector["kind"])}"{mpn}/>'
        )
        out.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="2.0" fill="#d97706"/>')
    out.append('</g>')
    note_x = 550
    island_rows = model["functional_partition"]["ui_board" if is_ui else "rf_power_board"]
    out.extend([
        text(note_x, 125, "Functional islands on this PCB", 18, "bold"),
        text(note_x, 158, f'{len(rows)} registered bodies · zero same-face collisions', 12, "bold", colour="#166534"),
    ])
    note_y = 196
    for island in island_rows:
        out.append(text(note_x, note_y, f'• {island}', 12, colour="#334155"))
        note_y += 28
    out.extend([
        text(note_x, note_y+20, "Line key", 16, "bold"),
        f'<line x1="{note_x}" y1="{note_y+48}" x2="{note_x+44}" y2="{note_y+48}" stroke="#2563eb" stroke-width="1.7"/>',
        text(note_x+56, note_y+52, "board-local RF topology; matching and final geometry belong to KiCad", 10, colour="#526076"),
    ])
    if is_ui:
        out.extend(
            [
                f'<line x1="{note_x}" y1="{note_y+70}" x2="{note_x+44}" y2="{note_y+70}" stroke="#0f766e" stroke-width="3.2" stroke-linecap="round"/>',
                text(note_x+56, note_y+74, "straight removable microcoax: 30 mm S3/C5 · 60 mm nRF", 10, colour="#526076"),
            ]
        )
        key_tail_y = note_y + 92
    else:
        out.extend(
            [
                text(note_x, note_y+76, "No U.FL or removable RF cable on this PCB.", 10, "bold", colour="#166534"),
                f'<line x1="{note_x}" y1="{note_y+98}" x2="{note_x+44}" y2="{note_y+98}" stroke="#ea580c" stroke-width="2"/>',
                text(note_x+56, note_y+102, "powered converted-Airband RF/IF branch and 112-MHz LO", 10, colour="#526076"),
                f'<line x1="{note_x}" y1="{note_y+120}" x2="{note_x+44}" y2="{note_y+120}" stroke="#7c3aed" stroke-width="1.9"/>',
                text(note_x+56, note_y+124, "high-impedance Si4732 AMI path; not a 50-ohm antenna feed", 10, colour="#526076"),
            ]
        )
        key_tail_y = note_y + 142
    out.extend(
        [
            text(note_x, key_tail_y, "Body key", 16, "bold"),
            f'<rect x="550" y="{key_tail_y+16:.1f}" width="28" height="18" fill="#eef2f6" stroke="#94a3b8"/>',
            text(590, key_tail_y+30, "retained registered body", 10, colour="#526076"),
            f'<rect x="550" y="{key_tail_y+48:.1f}" width="28" height="18" fill="#dbeafe" stroke="#2563eb"/>',
            text(590, key_tail_y+62, "explicit R2 placement", 10, colour="#526076"),
            f'<rect x="550" y="{key_tail_y+80:.1f}" width="28" height="18" fill="#fff7ed" stroke="#ea580c" stroke-dasharray="5 3"/>',
            text(590, key_tail_y+94, "controlled physical reserve", 10, colour="#526076"),
            f'<rect x="550" y="{key_tail_y+112:.1f}" width="28" height="18" fill="#7c3aed" fill-opacity="0.06" stroke="#7c3aed" stroke-dasharray="5 3"/>',
            text(590, key_tail_y+126, "placement island; outline is not a component", 10, colour="#526076"),
            f'<rect x="550" y="{key_tail_y+144:.1f}" width="28" height="18" fill="#dc2626" fill-opacity="0.06" stroke="#dc2626" stroke-dasharray="5 3"/>',
            text(590, key_tail_y+158, "exact keepout; must remain empty", 10, colour="#526076"),
            text(note_x, key_tail_y+188, "U219 accessory pickup loop: registered full-slot feature; no internal-coil coordinate is assumed.", 10, "bold", colour="#166534"),
            text(note_x, 1000, "The complete numbered register remains generated for machine review.", 10, colour="#526076"),
            text(note_x, 1020, "The public page uses these two readable one-board maps.", 10, colour="#526076"),
            '</svg>',
        ]
    )
    return "\n".join(out) + "\n"


def render_inner_sections_svg(model: dict, base: dict, source_table: dict, result: dict) -> str:
    """Render true X/Z cuts through Cap-Bus, Airband/power and service zones."""
    rows = complete_inner_rows(model, base, source_table, result)
    board_w, _board_h = model["board_mm"]
    cuts = (
        (29.0, "A–A · Cap-Bus / U219 host islands", True),
        (65.0, "B–B · Airband / 3V3_MAIN", False),
        (101.0, "C–C · controls / service", False),
    )
    x_scale = 5.4
    z_scale = 14.0
    panel_w = 660
    width = 2020
    top = 135.0
    legend_y = 735
    height = 1390
    esc = html.escape

    def t(x: float, y: float, value: str, size=10, weight="normal", anchor="start", colour="#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" data-marker="{esc(model["marker"])}" data-view="true-x-z-sections">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 38, f'Leshy2 — {model["marker"]} R2 inner sandwich sections', 24, "bold"),
        t(30, 66, "Horizontal X and front-to-rear Z use registered millimetre scales. U214 and U219 outlines are mutually exclusive profiles, never simultaneous hardware.", 12, colour="#526076"),
    ]
    legend_entries: list[tuple[int, dict]] = []
    reference = 1
    for panel_index, (cut_y, title, show_cap_profiles) in enumerate(cuts):
        panel_x = 25 + panel_index * panel_w
        ox = panel_x + 75

        def px(mm: float) -> float:
            return ox + mm*x_scale

        def pz(mm: float) -> float:
            return top + mm*z_scale

        out.extend(
            [
                t(panel_x, 112, title, 17, "bold"),
                t(panel_x, 134, f'cut Y={cut_y:.1f} mm · view from antenna edge along +Y', 10, colour="#526076"),
                f'<rect x="{px(0):.1f}" y="{pz(3.2):.1f}" width="{board_w*x_scale:.1f}" height="{1.6*z_scale:.1f}" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5" data-board="ui"/>',
                f'<rect x="{px(0):.1f}" y="{pz(15.8):.1f}" width="{board_w*x_scale:.1f}" height="{1.6*z_scale:.1f}" fill="#ffedd5" stroke="#ea580c" stroke-width="1.5" data-board="rf"/>',
                f'<rect x="{px(0):.1f}" y="{pz(4.8):.1f}" width="{board_w*x_scale:.1f}" height="{11.0*z_scale:.1f}" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="5 4"/>',
                t(px(-2), pz(4.0), "UI", 9, "bold", "end", "#166534"),
                t(px(-2), pz(16.6), "RF", 9, "bold", "end", "#c2410c"),
                t(px(30.0), pz(10.6), "exact 11-mm board gap", 9, "bold", "middle", "#526076"),
            ]
        )
        if show_cap_profiles:
            for profile_name, colour, dash in (("u219", "#ea580c", ""), ("u214", "#2563eb", ' stroke-dasharray="6 4"')):
                profile = model["cap_bus_slot"]["profiles"][profile_name]
                box = profile["world_bbox_mm"]
                out.append(
                    f'<rect x="{px(box["x"][0]):.1f}" y="{pz(box["z"][0]):.1f}" '
                    f'width="{(box["x"][1]-box["x"][0])*x_scale:.1f}" height="{(box["z"][1]-box["z"][0])*z_scale:.1f}" '
                    f'rx="3" fill="{colour}" fill-opacity="0.05" stroke="{colour}" stroke-width="1.5"{dash} '
                    f'data-cap-profile="{profile_name}" data-population="mutually-exclusive"/>'
                )
                out.append(t(px(37.5), pz(box["z"][1])-5, f'{profile_name.upper()} · {profile["envelope_mm"][2]:.3f} mm high', 8.0, "bold", "middle", colour))
            out.append(t(panel_x, 690, "U219 is +4.413 mm vs U214, yet remains 1.0 mm below the battery holder and 1.3 mm below the rear maximum.", 8.7, "bold", colour="#9a3412"))
        for feature in located_physical_features(model, "rf-inner"):
            box = feature["world_bbox_mm"]
            if not (box["y"][0] <= cut_y <= box["y"][1]):
                continue
            colour = "#dc2626" if feature["kind"] == "keepout" else "#7c3aed"
            out.append(
                f'<line x1="{px(box["x"][0]):.1f}" y1="{pz(15.45):.1f}" x2="{px(box["x"][1]):.1f}" y2="{pz(15.45):.1f}" '
                f'stroke="{colour}" stroke-width="3" stroke-dasharray="5 3" data-physical-feature="{esc(feature["id"])}"/>'
            )
        for row in rows:
            b = row["bbox"]
            if not (b["y"][0] <= cut_y <= b["y"][1]):
                continue
            z0, z1 = b["z"]
            w = b["x"][1] - b["x"][0]
            fill = "#dbeafe" if row["origin"] == "R2 placement" else "#eef2f6"
            stroke = "#2563eb" if row["origin"] == "R2 placement" else "#64748b"
            dash = ' stroke-dasharray="6 4"' if row["kind"] == "reserve" else ""
            if row["kind"] == "reserve":
                fill, stroke = "#fff7ed", "#ea580c"
            out.append(f'<rect x="{px(b["x"][0]):.1f}" y="{pz(z0):.1f}" width="{w*x_scale:.1f}" height="{max((z1-z0)*z_scale,3):.1f}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{dash} data-instance="{esc(row["id"])}"/>')
            out.append(t(px((b["x"][0]+b["x"][1])/2), pz((z0+z1)/2)+3, str(reference), 7.0, "bold", "middle", stroke))
            legend_entries.append((reference, row))
            reference += 1
        out.extend(
            [
                f'<line x1="{px(0):.1f}" y1="{pz(18.8):.1f}" x2="{px(board_w):.1f}" y2="{pz(18.8):.1f}" stroke="#334155"/>',
                f'<line x1="{px(0):.1f}" y1="{pz(18.5):.1f}" x2="{px(0):.1f}" y2="{pz(19.1):.1f}" stroke="#334155"/>',
                f'<line x1="{px(board_w):.1f}" y1="{pz(18.5):.1f}" x2="{px(board_w):.1f}" y2="{pz(19.1):.1f}" stroke="#334155"/>',
                t(px(board_w/2), pz(18.55), "75-mm PCB", 9, "bold", "middle", "#334155"),
            ]
        )

    out.extend(
        [
            t(35, legend_y-35, "Bodies crossed by the three planes", 17, "bold"),
            t(500, legend_y-35, f'Structural audit: pass · {result["minimum_opposing_clearance_mm"]:.2f} mm minimum opposing gap · {len(model["current_h1_blockers"])} explicit H1 geometry gates remain', 11, "bold", colour="#166534"),
        ]
    )
    per_col = math.ceil(len(legend_entries)/4)
    for index, (ref, row) in enumerate(legend_entries):
        col = index // per_col
        slot = index % per_col
        lx = 35 + col*490
        ly = legend_y + slot*54
        out.append(t(lx, ly, f'{ref:02d}  {row["mpn"]}', 8.8, "bold"))
        role_lines = textwrap.wrap(row["role"], width=58, break_long_words=False, break_on_hyphens=False)[:2]
        for line_no, line in enumerate(role_lines):
            out.append(t(lx+26, ly+13+line_no*11, line, 7.4, colour="#526076"))
    out.append('</svg>')
    return "\n".join(out) + "\n"


def render_retitled_legacy_view(model: dict, renderer: str) -> str:
    """Keep unaffected established geometry but mark it as current R2 work."""
    legacy = legacy_generator()
    devices, _candidate, instances, *_rest = legacy.load()
    svg = getattr(legacy, renderer)(devices, instances)
    marker = model["marker"]
    svg = svg.replace("Leshy2 — two physical cross-sections", f"Leshy2 — {marker} exterior-zone cross-sections")
    svg = svg.replace("Leshy2 — true top view from the antenna edge", f"Leshy2 — {marker} antenna-edge view")
    if renderer == "render_top_edge":
        mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
        axis_x = mmcx["mounting"]["mounting_axis_world_xy_mm"][0]
        drawing_x = 120.0 + (axis_x + 4.5) * 8.0
        drawing_z = 145.0 + 20.575 * 8.0
        addition = (
            f'<g id="fpv-mmcx-top-edge" data-instance="fpv_mmcx" data-mpn="DL-MMCX-KWE-90" '
            f'data-total-rear-port-count="6">'
            f'<circle cx="{drawing_x:.1f}" cy="{drawing_z:.1f}" r="48.0" fill="none" '
            f'stroke="#2563eb" stroke-width="1.4" stroke-dasharray="7 4" data-service-diameter-mm="12"/>'
            f'<ellipse cx="{drawing_x:.1f}" cy="{drawing_z:.1f}" rx="14.0" ry="14.0" '
            f'fill="#dbeafe" stroke="#1d4ed8" stroke-width="2" data-path="FPV-5G8-RX"/>'
            f'<text x="{drawing_x:.1f}" y="{drawing_z-54:.1f}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="8.5" font-weight="700" fill="#1d4ed8">FPV RX 5.8G · MMCX</text>'
            '</g>'
        )
        svg = svg.replace("</svg>", addition + "\n</svg>")
    return svg.replace("<svg ", f'<svg data-marker="{html.escape(marker)}" data-review-status="reviewed" ', 1)


def render_mmcx_service_svg_legacy(model: dict, result: dict) -> str:
    service = result["mmcx_service"]
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mount = mmcx["mounting"]
    esc = html.escape
    green = "#0f766e"
    blue = "#2563eb"
    orange = "#ea580c"
    ink = "#172033"
    muted = "#526076"
    plan_scale = 6.6
    plan_x = 60.0
    edge_y = 175.0
    axis_x = plan_x + mount["mounting_axis_world_xy_mm"][0] * plan_scale
    nrf_x = plan_x + 29.9 * plan_scale
    vhf_x = plan_x + 45.1 * plan_scale
    body_clearance_by_path = {
        row["path"]: row["clearance_mm"]
        for row in service["rear_antenna_connector_clearances"]
    }
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="930" viewBox="0 0 900 930">',
        '<rect width="900" height="930" fill="#ffffff"/>',
        '<defs><marker id="redArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/></marker></defs>',
        f'<text x="32" y="42" font-family="sans-serif" font-size="25" font-weight="700" fill="{ink}">Leshy2 · {esc(model["marker"])} top-edge MMCX proof</text>',
        f'<text x="32" y="70" font-family="sans-serif" font-size="13" fill="{muted}">DL-MMCX-KWE-90 · C2894793 · exact connector; dashed circle is the installation handling envelope.</text>',
        f'<text x="40" y="112" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">1 · RF OUTER FACE · looking from the rear</text>',
        f'<rect x="{plan_x:.1f}" y="{edge_y:.1f}" width="{75*plan_scale:.1f}" height="250" rx="8" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
        f'<line x1="{plan_x:.1f}" y1="{edge_y:.1f}" x2="{plan_x+75*plan_scale:.1f}" y2="{edge_y:.1f}" stroke="{ink}" stroke-width="3"/>',
        f'<text x="{plan_x+8:.1f}" y="{edge_y+24:.1f}" font-family="sans-serif" font-size="12" fill="{muted}">RF PCB · antenna edge Y=0</text>',
        f'<circle cx="{nrf_x:.1f}" cy="{edge_y+25:.1f}" r="{5.1*plan_scale:.1f}" fill="#fff7ed" stroke="#ea580c" stroke-width="1.6" data-path="N24-1"/>',
        f'<circle cx="{vhf_x:.1f}" cy="{edge_y+25:.1f}" r="{5.1*plan_scale:.1f}" fill="#fff7ed" stroke="#ea580c" stroke-width="1.6" data-path="VOICE-VHF"/>',
        f'<circle cx="{axis_x:.1f}" cy="{edge_y+12:.1f}" r="{6*plan_scale:.1f}" fill="none" stroke="{orange}" stroke-width="2" stroke-dasharray="8 5" data-service-diameter-mm="12"/>',
        f'<rect x="{axis_x-1.8*plan_scale:.1f}" y="{edge_y:.1f}" width="{3.6*plan_scale:.1f}" height="{3.6*plan_scale:.1f}" rx="3" fill="#dbeafe" stroke="{blue}" stroke-width="2"/>',
        f'<rect x="{axis_x-1.15*plan_scale:.1f}" y="{edge_y-3*plan_scale:.1f}" width="{2.3*plan_scale:.1f}" height="{3*plan_scale:.1f}" rx="3" fill="#bfdbfe" stroke="{blue}" stroke-width="2"/>',
        f'<line x1="{axis_x:.1f}" y1="{edge_y-3*plan_scale:.1f}" x2="{axis_x:.1f}" y2="132" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        f'<text x="{nrf_x:.1f}" y="{edge_y+82:.1f}" text-anchor="end" font-family="sans-serif" font-size="10" font-weight="700" fill="#9a3412">nRF24-2</text>',
        f'<text x="{axis_x:.1f}" y="{edge_y+82:.1f}" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="700" fill="{blue}">FPV RX · 5.8 GHz</text>',
        f'<text x="{vhf_x:.1f}" y="{edge_y+82:.1f}" text-anchor="start" font-family="sans-serif" font-size="10" font-weight="700" fill="#9a3412">VHF VOICE</text>',
        f'<text x="{axis_x+16:.1f}" y="132" text-anchor="start" font-family="sans-serif" font-size="11" font-weight="700" fill="#dc2626">antenna / plug points upward</text>',
        f'<text x="70" y="455" font-family="sans-serif" font-size="12" fill="{green}">✓ Installed-body clearance: nRF24-2 {body_clearance_by_path["N24-1"]:.1f} mm · VHF {body_clearance_by_path["VOICE-VHF"]:.1f} mm</text>',
        f'<text x="70" y="480" font-family="sans-serif" font-size="11" fill="{orange}">⚠ Ø12 handling envelope overlaps both adjacent SMA bodies: fit the flexible FPV antenna first.</text>',
        f'<text x="70" y="505" font-family="sans-serif" font-size="12" fill="{muted}">Installed body X {service["installed_body_world_bbox_mm"]["x"][0]:.1f}…{service["installed_body_world_bbox_mm"]["x"][1]:.1f} mm · axis ({service["mounting_axis_world_xy_mm"][0]:.1f}, {service["mounting_axis_world_xy_mm"][1]:.1f}) mm</text>',
        f'<text x="40" y="545" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">2 · SECTION ALONG ANTENNA AXIS</text>',
        f'<rect x="230" y="650" width="440" height="40" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>',
        f'<text x="245" y="676" font-family="sans-serif" font-size="11" fill="{muted}">RF PCB · 1.6 mm</text>',
        f'<rect x="412" y="614" width="76" height="36" rx="3" fill="#dbeafe" stroke="{blue}" stroke-width="2"/>',
        f'<rect x="426" y="554" width="48" height="60" rx="5" fill="#bfdbfe" stroke="{blue}" stroke-width="2"/>',
        f'<line x1="450" y1="554" x2="450" y2="515" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        f'<rect x="438" y="690" width="8" height="44" fill="#ccfbf1" stroke="{green}" stroke-width="2"/>',
        f'<line x1="405" y1="554" x2="495" y2="554" stroke="{orange}" stroke-width="2" stroke-dasharray="6 4"/>',
        f'<text x="520" y="570" font-family="sans-serif" font-size="11" fill="{orange}">≥ {mount["minimum_sidewall_free_diameter_mm"]:.1f}-mm antenna-edge aperture</text>',
        f'<text x="520" y="593" font-family="sans-serif" font-size="10" fill="{orange}">Ø12 × 20-mm outward plug corridor</text>',
        f'<text x="40" y="790" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">3 · TAIL / OPPOSING-SIDE CHECK</text>',
        f'<text x="40" y="822" font-family="sans-serif" font-size="12" fill="{muted}">2.80 ± 0.15-mm pins through 1.60-mm PCB → nominal 1.20 mm into the 11-mm interboard gap.</text>',
        f'<text x="40" y="850" font-family="sans-serif" font-size="12" fill="{green}">✓ Tail keepout opposing-body hits: {len(service["opposing_body_hits"])} · factory route: wave soldering</text>',
        f'<text x="40" y="880" font-family="sans-serif" font-size="11" fill="{orange}">H5 locks geometry/instructions; H7/H8 verify mating, retention, aperture and strain relief after arrival.</text>',
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_mmcx_service_svg(model: dict, result: dict) -> str:
    """Show the vertical rear-face MMCX in true plan and side views."""
    service = result["mmcx_service"]
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mount = mmcx["mounting"]
    scale, ox, oy = 7.0, 80.0, 130.0
    axis_x, axis_y = mount["mounting_axis_world_xy_mm"]
    body_x, body_y = mmcx["world_xy_mm"]
    body_w, body_d, body_h = mmcx["size_mm"]
    plug = mount["controlled_right_angle_plug_reference"]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="880" viewBox="0 0 980 880">',
        '<rect width="980" height="880" fill="#ffffff"/>',
        '<defs><marker id="redArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#dc2626"/></marker></defs>',
        f'<text x="32" y="42" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {html.escape(model["marker"])} rear-face FPV connector</text>',
        '<text x="32" y="70" font-family="sans-serif" font-size="13" fill="#526076">Molex 73415-2063 · C588480 · vertical SMT MMCX; dashed circle is the Ø12-mm handling envelope.</text>',
        '<text x="80" y="108" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">1 · REAR OUTER FACE · user looking at the battery side</text>',
        f'<rect x="{ox}" y="{oy}" width="{75*scale}" height="{54*scale}" rx="8" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
    ]
    for centre, path in zip(
        model["antenna_bank_optimization"]["rear_x_centres_mm"],
        model["antenna_bank_optimization"]["rear_paths"],
    ):
        out.extend([
            f'<rect x="{ox+(centre-5.1)*scale:.1f}" y="{oy:.1f}" width="{10.2*scale:.1f}" height="{6*scale:.1f}" rx="3" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5" data-path="{html.escape(path)}"/>',
            f'<text x="{ox+centre*scale:.1f}" y="{oy+54:.1f}" text-anchor="middle" font-family="sans-serif" font-size="8" font-weight="700" fill="#9a3412">{html.escape(path)}</text>',
        ])
    out.extend([
        f'<circle cx="{ox+axis_x*scale:.1f}" cy="{oy+axis_y*scale:.1f}" r="{6*scale:.1f}" fill="none" stroke="#ea580c" stroke-width="2" stroke-dasharray="8 5"/>',
        f'<rect x="{ox+body_x*scale:.1f}" y="{oy+body_y*scale:.1f}" width="{body_w*scale:.1f}" height="{body_d*scale:.1f}" rx="3" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>',
        f'<path d="M{ox+axis_x*scale:.1f} {oy+axis_y*scale:.1f} H{ox+(axis_x-plug["strain_relief_run_max_mm"])*scale:.1f}" stroke="#0f766e" stroke-width="{plug["strain_relief_width_max_mm"]*scale:.1f}" stroke-linecap="round" data-part="controlled-right-angle-plug-envelope"/>',
        f'<circle cx="{ox+axis_x*scale:.1f}" cy="{oy+axis_y*scale:.1f}" r="{plug["connector_head_width_max_mm"]*scale/2:.1f}" fill="#ffffff" stroke="#0f766e" stroke-width="2"/>',
        f'<text x="{ox+axis_x*scale:.1f}" y="{oy+16.0*scale:.1f}" text-anchor="middle" font-family="sans-serif" font-size="10" font-weight="700" fill="#1d4ed8">FPV RX · 5.8 GHz</text>',
        f'<rect x="{ox-4.5*scale:.1f}" y="{oy+17*scale:.1f}" width="{84*scale:.1f}" height="{24*scale:.1f}" rx="8" fill="#fff7ed" fill-opacity="0.72" stroke="#ea580c" stroke-width="2" data-accessory-slot="cap-bus" data-population="u214-or-u219"/>',
        f'<text x="{ox+37.5*scale:.1f}" y="{oy+30*scale:.1f}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#9a3412">removable U214 / U219 Cap slot</text>',
        f'<text x="80" y="530" font-family="sans-serif" font-size="13" fill="#0f766e">✓ static RA plug to nearest SMA: {service["minimum_right_angle_plug_clearance_mm"]:.2f} mm · required {mount["minimum_u214_clearance_mm"]:.1f} mm</text>',
        f'<text x="80" y="560" font-family="sans-serif" font-size="13" fill="#0f766e">✓ static RA plug to shared Cap slot: {service["right_angle_plug_u214_clearance_mm"]:.2f} mm</text>',
        f'<text x="80" y="590" font-family="sans-serif" font-size="13" fill="#9a3412">△ dashed Ø12 is temporary finger approach; overlaps {", ".join(x["path"] for x in service["handling_envelope_overlaps"])}; H7/H8 inspect access after arrival</text>',
        '<text x="80" y="635" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">2 · TRUE SIDE SECTION</text>',
        '<rect x="250" y="730" width="460" height="28" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>',
        '<text x="265" y="750" font-family="sans-serif" font-size="11" fill="#526076">RF PCB · 1.6 mm</text>',
        f'<rect x="444" y="{730-body_h*18:.1f}" width="72" height="{body_h*18:.1f}" rx="5" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>',
        f'<line x1="480" y1="{730-body_h*18:.1f}" x2="480" y2="625" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        '<text x="530" y="665" font-family="sans-serif" font-size="12" fill="#dc2626">plug / antenna points out of the rear face</text>',
        '<text x="80" y="815" font-family="sans-serif" font-size="13" fill="#0f766e">✓ SMT-only: no pins or keepout enter the 11-mm interboard gap.</text>',
        '<text x="80" y="845" font-family="sans-serif" font-size="12" fill="#526076">H5 locks geometry/instructions; H7/H8 verify plug, Cap insertion, access, retention and strain after arrival.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def _prefixed_svg_body(svg: str, prefix: str) -> str:
    """Inline a generated SVG panel without duplicate DOM identifiers."""
    body = svg[svg.find(">") + 1:svg.rfind("</svg>")]
    body = re.sub(r'<rect width="100%" height="100%" fill="#ffffff"\s*/>', "", body)
    body = re.sub(r'id="([^"]+)"', lambda match: f'id="{prefix}-{match.group(1)}"', body)
    body = re.sub(r'url\(#([^\)]+)\)', lambda match: f'url(#{prefix}-{match.group(1)})', body)
    body = re.sub(r'href="#([^"]+)"', lambda match: f'href="#{prefix}-{match.group(1)}"', body)
    return body


def render_four_faces_svg(model: dict, external_svg: str, inner_ui_svg: str, inner_rf_svg: str) -> str:
    """Place each directly viewed, physically turned-over inner face below its exterior."""
    external = _prefixed_svg_body(external_svg, "ext")
    inner_ui = _prefixed_svg_body(inner_ui_svg, "ui")
    inner_rf = _prefixed_svg_body(inner_rf_svg, "rf")
    # The standalone inner-face drawings carry explanatory legends to the right
    # of the 75-mm board.  The four-face comparison intentionally embeds only
    # the matched physical projection; keeping a clipped legend fragment here
    # makes the source-board comparison harder to read.
    inner_ui = inner_ui.split('<text x="550.0" y="125.0"', 1)[0]
    inner_rf = inner_rf.split('<text x="550.0" y="125.0"', 1)[0]

    def text(x: float, y: float, value: str, size=18, weight="normal", anchor="start", colour="#172033") -> str:
        return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="1500" viewBox="0 0 1050 1500" data-view="four-faces-matched-columns">',
        '<defs><clipPath id="front-external-content"><rect x="106" y="145" width="328" height="615"/></clipPath><clipPath id="rear-external-content"><rect x="616" y="145" width="328" height="615"/></clipPath></defs>',
        '<rect width="1050" height="1500" fill="#ffffff"/>',
        text(40, 42, f'Leshy2 · {model["marker"]} · four matched PCB faces', 26, "bold"),
        text(40, 70, "Outer face above; the inner face is shown exactly as viewed after physically turning the PCB over.", 13, colour="#526076"),
        text(270, 104, "FRONT / UI PCB", 18, "bold", "middle", "#1d4ed8"),
        text(780, 104, "REAR / RF-POWER PCB", 18, "bold", "middle", "#166534"),
        text(270, 130, "outer · user-facing silk", 12, "bold", "middle", "#526076"),
        text(780, 130, "outer · user-facing silk", 12, "bold", "middle", "#526076"),
        f'<g clip-path="url(#front-external-content)" data-panel="front-external"><svg x="45" y="145" width="450" height="615" viewBox="45 90 350 660" preserveAspectRatio="xMidYMid meet" overflow="hidden">{external}</svg></g>',
        f'<g clip-path="url(#rear-external-content)" data-panel="rear-external"><svg x="555" y="145" width="450" height="615" viewBox="430 90 350 660" preserveAspectRatio="xMidYMid meet" overflow="hidden">{external}</svg></g>',
        text(270, 790, "inner · viewed after turning over · no silkscreen", 12, "bold", "middle", "#526076"),
        text(780, 790, "inner · viewed after turning over · no silkscreen", 12, "bold", "middle", "#526076"),
        f'<svg x="45" y="805" width="450" height="650" viewBox="70 95 440 940" preserveAspectRatio="xMidYMid meet" overflow="hidden">{inner_ui}</svg>',
        f'<svg x="555" y="805" width="450" height="650" viewBox="70 95 440 940" preserveAspectRatio="xMidYMid meet" overflow="hidden">{inner_rf}</svg>',
        text(525, 1480, "Matched physical columns · 75 × 150 mm PCBs · not authorization for KiCad", 12, "bold", "middle", "#b42318"),
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_doc_legacy(model: dict, result: dict, ru: bool) -> str:
    if ru:
        title = f'# {model["marker"]} · физическая перекомпоновка'
        intro = "Это текущий проверяемый результат H1, а не журнал решений и не разрешение начинать KiCad."
        state = "В принятую 75×150-мм систему координат добавлены второй Hub RP, его полный независимый внешний recovery-набор, активные корпуса Airband, расширенная 24×11-мм ячейка настройки фильтра, видеодекодер FPV и двойная взаимоисключающая post-PCBA-зона K331/AWM666V."
        audit_heading = "## Что уже проверено"
        open_heading = "## Что блокирует H1 сейчас"
        dependent_heading = "## Зависимая работа H1"
        downstream_heading = "## Последующая проверка — не блокирует H1"
        factory_heading = "## Точные фабричные позиции"
        bullets = [
            f'- Коллизии корпусов на одной стороне: `{len(result["same_face_collisions"])}`.',
            f'- Намеренных встречных XY-проекций: `{result["opposing_overlap_count"]}`; минимальный Z-зазор `{result["minimum_opposing_clearance_mm"]:.2f} мм` при требовании `{result["required_opposing_clearance_mm"]:.2f} мм`.',
            '- Исправлено найденное расхождение H0↔H1: Hub RP получил четвёртый независимый data-only `HUB SERVICE USB`, две утопленные боковые кнопки `HUB RST/BOOT` и четвёртый внутренний DBG10. Hub и C5 используют один и тот же точный `SKRTLAE010`, поэтому генератор показывает одинаковые корпус, защитную выемку и утопленный толкатель.',
            '- Все четыре независимых USB теперь направлены в нижний торец: основной `USB / POWER` и три data-only service-порта S3/C5, RF RP и Hub RP сохраняют раздельные тракты.',
            '- Десять основных SMA разделены 5+5 между UI- и RF-платами; отдельный MMCX FPV расположен ниже заднего ряда. Радио, ответвители и цепи контроля фактической передачи остаются локальны своим разъёмам; новых межплатных RF-переходов нет.',
            '- Обе внутренние стороны показаны ровно так, как их видно после физического переворота платы; прежняя инкрементальная картинка ошибочно переворачивала только RF-плату.',
            '- Двойная post-PCBA-зона K331/AWM666V проверена с резервом 30×24×8 мм; после переноса C5 DBG10 минимальный встречный зазор составляет 1,05 мм.',
            '- Основной K331 использует толерантную 14-pad посадку, а точная вложенная посадка AWM666V служит деградированным fallback; устанавливается ровно один модуль.',
            '- JLCPCB подтвердила отсутствие K331 в Parts Library и Global Sourcing и не нашла прямой замены. Обычный PCBA BOM не содержит приёмника; Consigned Parts остаётся необязательным последующим упрощением.',
            '- JLCPCB готова рассмотреть процедуру function test для 5 В, channel-select и CVBS. Проверка реализуемости и цена относятся к H5/H6/H7 и не блокируют текущую физическую модель.',
            '- Контролируемый fallback `AWM666V RX` размером 26,16×16,38×3,70 мм и его рекомендованная посадка входят в ту же ячейку; он не заменяет K331 автоматически из-за семи каналов вместо 24 и отсутствия публичного маршрута JLCPCB.',
            '- Точная линейная антенна TBS5G8MMCXA подключается к отдельному MMCX; между ANT IN K331 и MMCX запланирована прямая 50-омная PCB-дорожка без U.FL.',
            '- Исправленная геометрия `DL-MMCX-KWE-90`: 3,6 мм корпуса находятся на RF-плате, ствол выступает за верхний антенный торец на 3,0 мм; выводы входят в межплатный просвет номинально на 1,2 мм, а их keepout не пересекает встречные корпуса.',
            '- Корпус MMCX оставляет 2,07 мм до ближайших SMA `CC-SUB` и `VOICE-VHF`; Ø12-мм временная зона пальцев пересекает только их handling-envelope. Контролируемый угловой штекер сохраняет 2,40 мм до SMA и 4,80 мм до U214; H5 проверяет полученные детали, порядок установки, снятие, удержание и нагрузку антенны.',
            '- Hub остаётся на UI-плате рядом со storage/audio/broadcast; RF-модуль FPV и видеодекодер расположены вместе на RF-плате.',
            '- Для Airband получен [номинально проходящий, но открытый по stress синтез](h1-airband-filter.ru.md); увеличенная ячейка содержит альтернативные/DNP-площадки, H3 проверяет bounded-оценку, H6 — routed extraction до заказа, H8 — финальный VNA-state.',
        ]
        table_header = "| Роль | Точный MPN | JLCPCB | Статус выбора | Текущий маршрут |\n|---|---|---|---|---|"
        blockers = model["current_h1_blockers_ru"]
        dependent = model["dependent_h1_work_ru"]
        downstream = [f'**{row["stage"]}:** {row["requirement_ru"]}' for row in model["downstream_verification"]]
    else:
        title = f'# {model["marker"]} · physical re-layout'
        intro = "This is the current verified H1 result, not a decision diary and not authorization to start KiCad."
        state = "The second Hub RP, its complete independent external recovery set, Airband active bodies, an expanded 24 × 11 mm filter-tuning cell, the FPV video decoder and a mutually exclusive post-PCBA K331/AWM666V bay are placed in the accepted 75 × 150 mm coordinate system."
        audit_heading = "## Already verified"
        open_heading = "## What blocks H1 now"
        dependent_heading = "## Dependent H1 work"
        downstream_heading = "## Later verification — does not block H1"
        factory_heading = "## Exact factory parts"
        bullets = [
            f'- Same-face body collisions: `{len(result["same_face_collisions"])}`.',
            f'- Intentional opposing XY projections: `{result["opposing_overlap_count"]}`; minimum Z clearance is `{result["minimum_opposing_clearance_mm"]:.2f} mm` against `{result["required_opposing_clearance_mm"]:.2f} mm` required.',
            '- The discovered H0↔H1 mismatch is corrected: Hub RP now has the fourth independent data-only `HUB SERVICE USB`, two recessed side `HUB RST/BOOT` controls and the fourth internal DBG10. Hub and C5 use the same exact `SKRTLAE010`, so the generator renders the same body, protective recess and recessed actuator.',
            '- All four independent USB openings now face the bottom edge: the main `USB / POWER` and the three data-only service paths for C5, RF RP and Hub RP remain electrically independent.',
            '- The ten main SMA ports are split 5+5 between the UI and RF PCBs; the separate FPV MMCX sits below the rear row. Radios, couplers and physical-TX evidence remain local to their connectors, with no new interboard RF transition.',
            '- Both inner faces are shown exactly as viewed after physically turning each PCB over; the earlier incremental view incorrectly turned only the RF PCB.',
            '- The dual post-PCBA K331/AWM666V bay is checked as a 30 × 24 × 8 mm reserve; relocating C5 DBG10 leaves 1.05 mm minimum opposing clearance.',
            '- Primary K331 uses a tolerant 14-pad land and the exact nested AWM666V land is a degraded fallback; exactly one receiver is installed.',
            '- JLCPCB confirmed that K331 is absent from both Parts Library and Global Sourcing and found no direct replacement. The normal PCBA BOM omits the receiver; Consigned Parts remains an optional later simplification.',
            '- JLCPCB can review a later 5 V, channel-select and CVBS function-test procedure. Feasibility and quotation belong to H5/H6/H7 and do not block the present physical model.',
            '- The controlled 26.16 × 16.38 × 3.70 mm `AWM666V RX` fallback and its recommended land pattern fit the same bay; it does not replace K331 automatically because it has seven channels instead of 24 and no public JLCPCB route.',
            '- The exact linear TBS5G8MMCXA antenna mates with the distinct MMCX; K331 ANT IN reaches it over one direct 50-ohm PCB trace without U.FL.',
            '- Corrected `DL-MMCX-KWE-90` geometry keeps 3.6 mm of body on the RF PCB and projects only the 3.0-mm barrel beyond the top antenna edge; its pins enter the interboard gap by a nominal 1.2 mm and the tail keepout meets no opposing body.',
            '- The MMCX body leaves 2.07 mm to the nearest `CC-SUB` and `VOICE-VHF` SMA bodies; only its temporary Ø12 finger envelope overlaps their handling envelopes. The controlled right-angle plug retains 2.40 mm to SMA and 4.80 mm to U214; H5 locks the sourced geometry and deterministic sequence before order, while H7/H8 inspect received fit, retention and antenna strain after arrival.',
            '- Hub remains on the UI board beside storage/audio/broadcast; the FPV RF module and decoder remain together on the RF board.',
            '- Airband now has a [nominally passing but stress-open synthesis](h1-airband-filter.md); the enlarged cell carries alternate/DNP pads, H3 checks bounded estimates, H6 routed extraction before order and H8 the final VNA state.',
        ]
        table_header = "| Role | Exact MPN | JLCPCB | Selection status | Current route |\n|---|---|---|---|---|"
        blockers = model["current_h1_blockers"]
        dependent = model["dependent_h1_work"]
        downstream = [f'**{row["stage"]}:** {row["requirement"]}' for row in model["downstream_verification"]]
    lines = [
        title,
        "",
        intro,
        "",
        state,
        "",
        f"![H1-R2 current external layout](images/h1-r2-external-layout.svg?rev={PUBLIC_ASSET_REV})",
        "",
        "![H1-R2 complete internal layout](images/h1-r2-inner-complete.svg)",
        "",
        f"![H1-R2 external service access](images/h1-r2-service-access.svg?rev={PUBLIC_ASSET_REV})",
        "",
        "![H1-R2 inner sandwich sections](images/h1-r2-inner-sections.svg)",
        "",
        "![H1-R2 antenna-edge view](images/h1-r2-antenna-edge.svg)",
        "",
        "![H1-R2 exterior-zone sandwich sections](images/h1-r2-sandwich-sections.svg)",
        "",
        "![H1-R2 placement delta](images/h1-r2-inner-placement.svg)",
        "",
        "![H1-R2 MMCX placement and service proof](images/h1-r2-mmcx-service.svg)",
        "",
        audit_heading,
        "",
    ]
    lines.extend(bullets)
    lines.extend(["", factory_heading, "", table_header])
    for row in model["factory_evidence"]:
        role = row.get("role_ru", row["role"]) if ru else row["role"]
        route = row.get("availability_ru", row["availability"]) if ru else row["availability"]
        status = row.get("selection_status_ru", row["selection_status"]) if ru else row["selection_status"]
        factory_ref = f'[`{row["jlcpcb_part"]}`]({row["url"]})' if row["jlcpcb_part"] else '—'
        lines.append(f'| {role} | `{row["mpn"]}` | {factory_ref} | {status} | {route} |')
    lines.extend(["", open_heading, ""])
    lines.extend(f"- {gate}" for gate in blockers)
    lines.extend(["", dependent_heading, ""])
    lines.extend(f"- {gate}" for gate in dependent)
    lines.extend(["", downstream_heading, ""])
    lines.extend(f"- {gate}" for gate in downstream)
    marker = f'> Итоговый маркер: **{model["marker"]}**. H1 принято 2026-08-30.' if ru else f'> Final result marker: **{model["marker"]}**. H1 was reviewed on 2026-08-30.'
    lines.extend(["", marker, ""])
    return "\n".join(lines)


def render_doc(model: dict, result: dict, ru: bool) -> str:
    """Publish the present product state without the design-decision diary."""
    if ru:
        title = f'# {model["marker"]} · рабочая компоновка целевого устройства'
        intro = (
            "Полная проверяемая физическая модель двух плат 75×150 мм принята 2026-08-30; H1 закрыто. "
            "Все корпуса, Cap-профили, внешний объём U219-антенны и медные резервы сведены без открытых geometry-gates. "
            "Это не разрешает трассировку KiCad: сначала в R2 H2 должны быть закрыты перечисленные ниже электрические prerequisites."
        )
        outside = "## Что увидит пользователь"
        inside = "## Что находится внутри"
        verified = "## Проверено генератором"
        factory = "## Точные фабричные позиции"
        blocker = "## Итог H1"
        component_legend_heading = "## Легенда компонентов"
        board_names = ("Передняя UI/radio-плата", "Задняя RF/power-плата")
        bullets = [
            "Десять основных SMA разделены симметрично `5 + 5`; каждый радиотракт остаётся на плате своего разъёма.",
            f"Выбранные GCT `RFPC-SMA31/32-FN-175-A` не держатся на одной стороне: корпус охватывает торец 1,6-мм платы, на стороне установки припаиваются RF-пята и две земляные лапы, на противоположной — ещё две земляные лапы. Это тот же двусторонний принцип, который виден в [ESP32-DIV v2]({model['antenna_bank_optimization']['main_sma_mounting']['comparison_url']}); односторонняя замена запрещена.",
            "На передней плате две точные 30-мм перемычки S3/C5 и три точные 60-мм перемычки nRF соединяют IPEX/U.FL радиоисточников с платными U.FL; дальше до SMA идут локальные контролируемые PCB-тракты.",
            "На задней плате U.FL и съёмных RF-кабелей нет: voice и FM/SW идут локальными RF-трактами, AM/LW — отдельным высокоомным AMI-трактом, а Airband — через питаемую ветвь преобразования и селектор.",
            "В общий слот устанавливается ровно один модуль: U214 (84×24×15,287 мм) или optional U219 (84×24×19,7 мм). U219 выше на 4,413 мм, но остаётся на 1,0 мм ниже держателя батарей и на 1,3 мм ниже максимального заднего габарита.",
            "Все пользовательские подписи являются читаемой шелкографией; внутренние стороны плат шелкографии не содержат.",
            "На внешней стороне каждой платы печатаются стабильные role/revision `UI PCB · R2-EVT1 · REV A` и `RF/PWR PCB · R2-EVT1 · REV A`; изменяемый рабочий маркер H1-R2.xx на PCB не печатается.",
            "Три nRF24 полностью перенесены на переднюю плату вместе с буферами, safety-gate и отдельным `TLV1824PWR`.",
            "Бортовой видеоприёмник, декодер, MMCX и их резервы удалены: за экраном и между антеннами нет скрытого post-PCBA модуля.",
            "FM/SW/AM/LW/Airband, CC1101, два voice-тракта и аудио локальны задней плате; S3 напрямую ведёт i8080-8, энкодер и USB, а кнопки — через локальный TCA9539PWR. После замыкания reset/service-трактов свободным электрическим резервом остаются шесть GPIO.",
            "Экран физически развёрнут шлейфом к антенному торцу, как у ESP32-DIV; шлейф входит прямо в 50-контактный ZIF на UI-плате, а firmware разворачивает изображение и touch на 180°. Все линии дисплея и touch остаются локальными S3; C5 к панели не подключён.",
            "Крепление — это конкретный стек корпуса: цельная полка и рамка в передней половине корпуса, вырубная рамка PSA толщиной 0,10–0,20 мм, четыре коротких угловых ребра корпуса и вырубная закрытоячеистая прокладка 0,5–1,0 мм с целевым сжатием 15–30 %. Прокладка давит только на безопасную заднюю зону панели; FPC и ZIF нагрузки не несут.",
            "У ESP32-DIV v2 сырой 2,8-дюймовый дисплей лежит прямо на основной PCB: четыре отверстия Ø1,2 мм позиционируют его рамку, а 18-контактный FPC припаян к длинным SMD-площадкам без ZIF. В открытых исходниках DIV не задан отдельный стек клея, пены или винтов дисплея. Leshy2 перенимает точное ложе и защиту от сдвига, но сохраняет обслуживаемый ненагруженный ZIF.",
        ]
        audit_lines = [
            f'Коллизии корпусов на одной стороне: `{len(result["same_face_collisions"])}`.',
            f'Минимальный встречный Z-зазор: `{result["minimum_opposing_clearance_mm"]:.2f} мм` при требовании `{result["required_opposing_clearance_mm"]:.2f} мм`.',
            f'Полное TX-evidence: `{result["tx_evidence_physical_register"]["detector_count"]}` точных детекторов, `{result["tx_evidence_physical_register"]["coupler_count"]}` coupler и `{result["tx_evidence_physical_register"]["local_island_count"]}` локальных островов проходят fail-closed аудит; шесть AD8314 используют принятый `AD8314ARMZ-REEL` / `C652687`.',
            f'Длина microcoax: две 30-мм перемычки native-radio и три 60-мм перемычки nRF имеют не меньше `{result["rf_microcoax"]["minimum_conservative_slack_mm"]:.2f} мм` расчётного запаса; каждый nRF проверен до самого дальнего угла полного корпуса SP4, а не до предположенной оси IPEX.',
            "C5 DBG10 расположен рядом с S3 DBG10 и не пересекается с соседними корпусами.",
            f'GPIO: передний RP `{model["functional_partition"]["front_rp_gpio"]["used"]}/48`, резерв `{model["functional_partition"]["front_rp_gpio"]["free"]}`; задний RP `{model["functional_partition"]["rear_rp_gpio"]["used"]}/48`, резерв `{model["functional_partition"]["rear_rp_gpio"]["free"]}`; S3 использует 27 из 33 GPIO.',
            "M1: все 80 контактов распределены — 31 сигнал, 14 main-power, 2 AON, 24 возврата и 9 настоящих NC-резервов.",
            "Механика M1: четыре 11,00-мм compression-stop, два противосдвиговых упора и независимые захваты плат; разъём не несёт ударную или изгибающую нагрузку.",
            "Шелкография антенн: генератор подтвердил отсутствие пересечений с SMA, Cap-Bus-слотом, дисплеем и монтажными keep-out.",
            "Точная посадка десяти SMA следует чертежам A1: прямоугольная RF-пята `1,87×3,30 мм` в `x=0`, четыре прямоугольные земляные лапы `1,60×3,30 мм` в `x=±2,55 мм`, край платы `y=0`. H5 фиксирует двусторонний процесс пайки, H7 осматривает все пять паек каждого разъёма на единственном собранном прототипе, H8 выполняет обычную сборку/разборку, continuity/inspection и повторную проверку каждого RF-тракта без искусственного старения, падений и vibration-программы.",
            f'Cap-Bus: взаимоисключающие профили U214/U219 и все восемь целевых зазоров проходят; все 18 точных корпусов U219, их source-backed courtyards, NFC pickup-loop и внешний swept volume штатной 108-мм антенны зарегистрированы fail-closed. Открытых H1 geometry-gates: `{len(model["current_h1_blockers"])}`.',
            "Экран `ER-TFT035IPS-6` + `ER-TPC035-6` и прямой UI-платный `FH34SRJ-50S-0.5SH(50)` зафиксированы; 1,00-мм ZIF оставляет 10,00 мм до противоположной плоскости платы, оба DF40 и отдельная плата-адаптер удалены, а сам разъём не несёт нагрузку панели.",
        ]
        route_col = "Текущая доступность/маршрут"
    else:
        title = f'# {model["marker"]} · working target-device placement'
        intro = (
            "The complete verifiable physical model of the two 75 × 150 mm PCBs was accepted on 2026-08-30; H1 is reviewed. "
            "Every body, Cap profile, external U219 antenna volume and copper reserve is registered with no open geometry gate. "
            "This does not authorize KiCad routing: the R2 H2 electrical prerequisites listed below must close first."
        )
        outside = "## What the user sees"
        inside = "## What is inside"
        verified = "## Generator-verified"
        factory = "## Exact factory parts"
        blocker = "## H1 result"
        component_legend_heading = "## Component legend"
        board_names = ("Front UI/radio PCB", "Rear RF/power PCB")
        bullets = [
            "Ten main SMA ports are split symmetrically `5 + 5`; every radio path remains on the PCB that carries its connector.",
            f"The selected GCT `RFPC-SMA31/32-FN-175-A` bodies are not retained by one PCB face: each shell straddles the 1.6-mm board edge, with one RF plus two ground lands on the component face and two more shell-ground lands on the opposite face. This is the same dual-face principle visible in [ESP32-DIV v2]({model['antenna_bank_optimization']['main_sma_mounting']['comparison_url']}); a one-face substitute is forbidden.",
            "On the front PCB, two exact 30-mm S3/C5 and three exact 60-mm nRF removable microcoax jumpers connect the radio-source IPEX/U.FL sockets to board U.FL sockets; controlled board-local PCB paths continue from there to SMA.",
            "The rear PCB has no U.FL or removable RF cable: voice and FM/SW use board-local RF paths, AM/LW uses a separate high-impedance AMI path, and Airband uses the powered conversion branch and selector.",
            "Exactly one accessory occupies the common slot: U214 (84 × 24 × 15.287 mm) or optional U219 (84 × 24 × 19.7 mm). U219 is 4.413 mm taller, yet remains 1.0 mm below the battery holder and 1.3 mm below the selected rear maximum.",
            "All user-facing labels are readable silkscreen; neither inner PCB face carries silkscreen.",
            "Each outer face prints a stable board role/revision — `UI PCB · R2-EVT1 · REV A` and `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never printed on a PCB.",
            "All three nRF24 islands move to the front PCB with their buffers, safety gate and a dedicated second `TLV1824PWR`.",
            "The onboard video receiver, decoder, MMCX and physical reserves are removed: no hidden post-PCBA module remains behind the display or between the antennas.",
            "FM/SW/AM/LW/Airband, CC1101, both voice paths and audio are rear-local; S3 directly owns i8080-8, encoder and USB, with buttons on its local TCA9539PWR path. Six GPIO remain uncommitted electrical reserve after reset and service closure.",
            "The panel is physically turned with its flex toward the antenna edge, as on ESP32-DIV; the tail enters one direct 50-contact ZIF on the UI PCB and firmware rotates display output and touch by 180°. All display and touch lines remain S3-local; C5 has no panel connection.",
            "Retention is a concrete enclosure stack: an integral front-shell ledge and bezel, a die-cut 0.10–0.20-mm PSA frame, four short integral corner ribs and a die-cut 0.5–1.0-mm closed-cell pad at 15–30% target compression. The pad touches only a safe rear-panel zone; neither the FPC nor ZIF carries panel load.",
            "ESP32-DIV v2 seats its raw 2.8-inch display directly on the main PCB: four 1.2-mm holes locate the display frame while the 18-contact FPC is soldered to long SMD lands without a ZIF. Its public sources do not define a separate adhesive, foam or display-screw stack. Leshy2 adopts the exact bed and anti-shear location, but retains a serviceable non-load-bearing ZIF.",
        ]
        audit_lines = [
            f'Same-face body collisions: `{len(result["same_face_collisions"])}`.',
            f'Minimum opposing Z clearance: `{result["minimum_opposing_clearance_mm"]:.2f} mm` against `{result["required_opposing_clearance_mm"]:.2f} mm` required.',
            f'Complete TX evidence: `{result["tx_evidence_physical_register"]["detector_count"]}` exact detectors, `{result["tx_evidence_physical_register"]["coupler_count"]}` couplers and `{result["tx_evidence_physical_register"]["local_island_count"]}` bounded local islands pass fail-closed audit; all six AD8314 positions use the accepted `AD8314ARMZ-REEL` / `C652687`.',
            f'Microcoax reach: two 30-mm native-radio and three 60-mm nRF paths have at least `{result["rf_microcoax"]["minimum_conservative_slack_mm"]:.2f} mm` paper slack, with each nRF checked against the farthest corner of the complete SP4 envelope rather than a guessed IPEX axis.',
            "C5 DBG10 is relocated beside S3 DBG10 and intersects no adjacent body.",
            f'GPIO: front RP `{model["functional_partition"]["front_rp_gpio"]["used"]}/48` with `{model["functional_partition"]["front_rp_gpio"]["free"]}` free; rear RP `{model["functional_partition"]["rear_rp_gpio"]["used"]}/48` with `{model["functional_partition"]["rear_rp_gpio"]["free"]}` free; S3 uses 27 of 33 GPIO.',
            "M1: all 80 contacts are assigned — 31 signals, 14 main-power, 2 AON, 24 returns and 9 true NC reserves.",
            "M1 mechanics: four 11.00-mm compression stops, two anti-shear datums and independent PCB capture; the connector carries no impact or bending load.",
            "Antenna silkscreen: the generator proves no overlap with SMA bodies, the Cap-Bus slot, the display or mounting keep-outs.",
            "The exact ten-SMA land pattern follows the A1 drawings: one rectangular 1.87 × 3.30-mm RF land at x=0, four rectangular 1.60 × 3.30-mm shell lands at x=±2.55 mm and board edge y=0. H5 locks the dual-face soldering process, H7 inspects all five joints per connector on the one assembled prototype, and H8 performs ordinary assembly/disassembly, continuity/inspection and every path-specific RF check without artificial ageing, drops or a vibration programme.",
            f'Cap-Bus: mutually exclusive U214/U219 profiles and all eight target clearances pass; all 18 exact U219 bodies, their source-backed courtyards, the NFC pickup loop and the external swept volume of the supplied 108-mm antenna are registered fail-closed. Open H1 geometry gates: `{len(model["current_h1_blockers"])}`.',
            "The `ER-TFT035IPS-6` + `ER-TPC035-6` assembly and direct UI-board `FH34SRJ-50S-0.5SH(50)` are fixed; the 1.00-mm ZIF leaves 10.00 mm to the opposing PCB plane, both DF40 parts and the adapter PCB are removed, and the connector carries no panel load.",
        ]
        route_col = "Current availability/route"
    lines = [
        title, "", intro, "", outside, "",
        f"![Four matched PCB faces](images/h1-r2-four-faces.svg?rev={PUBLIC_ASSET_REV})", "",
        component_legend_heading, "",
        f"![Numbered component legend](images/h1-r2-component-legend.svg?rev={PUBLIC_ASSET_REV})", "",
        f"[Detailed exterior at full scale](images/h1-r2-external-layout.svg?rev={PUBLIC_ASSET_REV})", "",
        f"![External service access](images/h1-r2-service-access.svg?rev={PUBLIC_ASSET_REV})", "",
        inside, "",
        f"![Direct display ZIF and mechanical retention](images/display-mount.svg?rev={PUBLIC_ASSET_REV})", "",
        f"[{board_names[0]} · full-scale inner view](images/h1-r2-inner-ui.svg)", "",
        f"[{board_names[1]} · full-scale inner view](images/h1-r2-inner-rf.svg)", "",
    ]
    lines.extend(f"- {row}" for row in bullets)
    lines.extend(["", "![True inner sandwich sections](images/h1-r2-inner-sections.svg)", "", verified, ""])
    lines.extend(f"- {row}" for row in audit_lines)
    lines.extend(["", factory, "", f"| {'Роль' if ru else 'Role'} | MPN | JLCPCB | {route_col} |", "|---|---|---|---|"])
    for row in model["factory_evidence"]:
        role = row.get("role_ru", row["role"]) if ru else row["role"]
        route = row.get("availability_ru", row["availability"]) if ru else row["availability"]
        ref = f'[`{row["jlcpcb_part"]}`]({row["url"]})' if row["jlcpcb_part"] else "—"
        lines.append(f'| {role} | `{row["mpn"]}` | {ref} | {route} |')
    blockers = model["current_h1_blockers_ru"] if ru else model["current_h1_blockers"]
    acceptance = model["dependent_h1_work_ru"] if ru else model["dependent_h1_work"]
    lines.extend(["", blocker, ""])
    if blockers:
        lines.extend(f"- {row}" for row in blockers)
    else:
        lines.append("- Новых блокеров геометрии корпусов нет." if ru else "- No additional physical-body geometry blockers remain.")
    lines.extend(f"- {row}" for row in acceptance)
    r2_gates = model["pre_r2_h2_gates_ru"] if ru else model["pre_r2_h2_gates"]
    lines.extend(["", "### Preconditions before R2 H2 / KiCad" if not ru else "### Preconditions до R2 H2 / KiCad", ""])
    lines.extend(f"- {row}" for row in r2_gates)
    marker = f'> Итоговый маркер: **{model["marker"]}**. H1 принято 2026-08-30.' if ru else f'> Final result marker: **{model["marker"]}**. H1 was reviewed on 2026-08-30.'
    lines.extend(["", marker, ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model = load(MODEL_PATH)
    base = load(BASE_PATH)
    source_table = load(SOURCE_TABLE_PATH)
    result = audit(model, base)
    complete_rows = complete_inner_rows(model, base, source_table, result)
    antenna_topology = r2_antenna_topology(model, complete_rows)
    result["antenna_topology"] = antenna_topology
    result["rf_microcoax"] = r2_microcoax_audit(model, complete_rows, antenna_topology)
    result["errors"].extend(result["rf_microcoax"]["errors"])
    if result["errors"]:
        result["status"] = "fail"
    external_svg = render_external_svg(model)
    inner_ui_svg = render_inner_face_svg(model, base, source_table, result, "ui-inner")
    inner_rf_svg = render_inner_face_svg(model, base, source_table, result, "rf-inner")
    outputs = {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        SVG_PATH: render_svg(model, base, result),
        EXTERNAL_SVG_PATH: external_svg,
        SERVICE_SVG_PATH: render_service_svg(model),
        COMPLETE_INNER_SVG_PATH: render_complete_inner_svg(model, base, source_table, result),
        INNER_UI_SVG_PATH: inner_ui_svg,
        INNER_RF_SVG_PATH: inner_rf_svg,
        INNER_SECTIONS_SVG_PATH: render_inner_sections_svg(model, base, source_table, result),
        FOUR_FACES_SVG_PATH: render_four_faces_svg(model, external_svg, inner_ui_svg, inner_rf_svg),
        COMPONENT_LEGEND_SVG_PATH: render_component_legend_svg(model, base, source_table, result),
        EN_DOC_PATH: render_doc(model, result, False),
        RU_DOC_PATH: render_doc(model, result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if args.check:
        for path, content in outputs.items():
            if not path.exists() or path.read_text() != content:
                print(f"stale generated artifact: {path.relative_to(REPO)}")
                return 1
    if result["errors"]:
        for error in result["errors"]:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
