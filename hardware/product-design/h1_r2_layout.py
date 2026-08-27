#!/usr/bin/env python3
"""Validate and render the incremental H1-R2 physical placement."""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
import textwrap
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-placement.json"
BASE_PATH = REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-placement-audit.json"
SVG_PATH = REPO / "docs/images/h1-r2-inner-placement.svg"
MMCX_SVG_PATH = REPO / "docs/images/h1-r2-mmcx-service.svg"
EXTERNAL_SVG_PATH = REPO / "docs/images/h1-r2-external-layout.svg"
SERVICE_SVG_PATH = REPO / "docs/images/h1-r2-service-access.svg"
COMPLETE_INNER_SVG_PATH = REPO / "docs/images/h1-r2-inner-complete.svg"
INNER_UI_SVG_PATH = REPO / "docs/images/h1-r2-inner-ui.svg"
INNER_RF_SVG_PATH = REPO / "docs/images/h1-r2-inner-rf.svg"
INNER_SECTIONS_SVG_PATH = REPO / "docs/images/h1-r2-inner-sections.svg"
EN_DOC_PATH = REPO / "docs/h1-r2-physical-layout.md"
RU_DOC_PATH = REPO / "docs/h1-r2-physical-layout.ru.md"
SOURCE_TABLE_PATH = REPO / "hardware/product-design/generated/H1-physical-source-table.json"


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
    elif item["frame"] == "rf-outer-right-edge":
        zr = [
            model["stack"]["rf_inner_z_mm"] + model["stack"]["rf_pcb_thickness_mm"],
            model["stack"]["rf_inner_z_mm"] + model["stack"]["rf_pcb_thickness_mm"] + z,
        ]
    else:
        zr = [model["stack"]["rf_inner_z_mm"], model["stack"]["rf_inner_z_mm"] + z]
    return {"x": [x, x + w], "y": [y, y + h], "z": zr}


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
            "plug insertion cycles, finger access and antenna strain",
        ],
        "errors": errors,
    }


def audit(model: dict, base: dict) -> dict:
    board_w, board_h = model["board_mm"]
    minimum = model["stack"]["minimum_opposing_clearance_mm"]
    new = []
    errors = []
    for item in model["placements"]:
        b = bbox(item, model)
        new.append({"item": item, "bbox": b})
        if item["frame"] in {"ui-inner", "rf-inner"}:
            if b["x"][0] < 0 or b["y"][0] < 0 or b["x"][1] > board_w or b["y"][1] > board_h:
                errors.append(f"{item['id']} leaves the PCB outline")

    fixed = [x for x in new if x["item"]["kind"] == "fixed_body"]
    replaced = {
        instance
        for entry in new
        for instance in entry["item"].get("replaces", [])
    }
    same_face = []
    for entry in fixed:
        item, b = entry["item"], entry["bbox"]
        for row in base["rows"]:
            if row["source_frame"] != item["frame"]:
                continue
            if row["instance"] in replaced:
                continue
            if overlaps(b, row["world_bbox_mm"]):
                same_face.append([item["id"], row["instance"]])
        for other in fixed:
            if other["item"]["id"] <= item["id"] or other["item"]["frame"] != item["frame"]:
                continue
            if overlaps(b, other["bbox"]):
                same_face.append([item["id"], other["item"]["id"]])
    if same_face:
        errors.extend(f"same-face collision: {a} / {b}" for a, b in same_face)

    cross = []
    for entry in new:
        item, b = entry["item"], entry["bbox"]
        if item["frame"] not in {"ui-inner", "rf-inner"}:
            continue
        opposite = "rf-inner" if item["frame"] == "ui-inner" else "ui-inner"
        for row in base["rows"]:
            if row["source_frame"] != opposite or not overlaps(b, row["world_bbox_mm"]):
                continue
            if row["instance"] in replaced:
                continue
            gap = z_clearance(b, row["world_bbox_mm"])
            cross.append({"new": item["id"], "base": row["instance"], "clearance_mm": round(gap, 3)})
            if gap < minimum:
                errors.append(f"opposing clearance {item['id']} / {row['instance']} is {gap:.3f} mm")
    min_cross = min((x["clearance_mm"] for x in cross), default=None)
    if len(model["current_h1_blockers"]) != 1:
        errors.append("physical layout must expose exactly the one present H1 blocker")
    if len(model["current_h1_blockers_ru"]) != len(model["current_h1_blockers"]):
        errors.append("bilingual current H1 blockers are out of sync")
    if len(model["dependent_h1_work"]) != 1:
        errors.append("physical layout must expose the one dependent H1 rendering task")
    if len(model["dependent_h1_work_ru"]) != len(model["dependent_h1_work"]):
        errors.append("bilingual dependent H1 work is out of sync")
    if any(row.get("stage") == "H1" for row in model["downstream_verification"]):
        errors.append("a downstream physical verification item is still owned by H1")
    mmcx_service = mmcx_service_audit(model, base, new)
    errors.extend(mmcx_service["errors"])
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "pass" if not errors else "fail",
        "base_model": model["base_model"],
        "new_fixed_body_count": len(fixed),
        "new_reserve_count": sum(x["item"]["kind"] == "reserve" for x in new),
        "replaced_seed_instances": sorted(replaced),
        "same_face_collisions": same_face,
        "opposing_overlap_count": len(cross),
        "minimum_opposing_clearance_mm": min_cross,
        "required_opposing_clearance_mm": minimum,
        "opposing_overlaps": cross,
        "mmcx_service": mmcx_service,
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
        '<text x="40" y="70" font-family="sans-serif" font-size="13" fill="#526076">World-scale engineering view · both opened inner faces are mirrored · numbered marks are documentation, never inner-face silkscreen.</text>',
    ]
    for frame, title in (("ui-inner", "UI PCB · inner · mirrored"), ("rf-inner", "RF / power PCB · inner · mirrored")):
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
            family = "airband" if item["id"].startswith("airband") else "fpv" if item["id"].startswith("fpv") else "hub_rp"
            fill, stroke = colours[family]
            dash = "6 4" if item["kind"] == "reserve" else "none"
            out.append(rect(x0 + x * scale, oy + y * scale, w * scale, h * scale, rx="3", fill=fill, fill_opacity="0.92", stroke=stroke, stroke_width="2", stroke_dasharray=dash))
            label = item["drawing_ref"]
            tx = x0 + (x + w / 2) * scale
            ty = oy + (y + h / 2) * scale
            font = 11 if w >= 6 else 8.5
            out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="{font}" font-weight="700" fill="{stroke}">{esc(label)}</text>')

    # The vertical FPV connector is projected through the RF board outline.
    # It has no through-board tail; its plan marker only explains the RF path.
    rf_x = ox["rf-inner"]
    mmcx = next(item for item in model["placements"] if item["id"] == "fpv_mmcx")
    mmcx_mount = mmcx["mounting"]
    mmcx_body = mmcx["size_mm"][0] * scale
    mmcx_axis_x = rf_x + (board_w - mmcx_mount["mounting_axis_world_xy_mm"][0]) * scale
    mmcx_axis_y = oy + mmcx_mount["mounting_axis_world_xy_mm"][1] * scale
    fpv = next(item for item in model["placements"] if item["id"] == "fpv_receiver_bay")
    dec = next(item for item in model["placements"] if item["id"] == "fpv_decoder")
    fpv_x = rf_x + (board_w - fpv["world_xy_mm"][0] - fpv["size_mm"][0]) * scale
    fpv_cy = oy + (fpv["world_xy_mm"][1] + fpv["size_mm"][1] / 2) * scale
    dec_x = ox["ui-inner"] + (board_w - dec["world_xy_mm"][0] - dec["size_mm"][0]) * scale
    dec_cy = oy + (dec["world_xy_mm"][1] + dec["size_mm"][1] / 2) * scale
    out.extend([
        rect(mmcx_axis_x - mmcx_body / 2, mmcx_axis_y - mmcx_body / 2, mmcx_body, mmcx_body, rx="2", fill="#dbeafe", stroke="#1d4ed8", stroke_width="2"),
        f'<circle cx="{mmcx_axis_x:.2f}" cy="{mmcx_axis_y:.2f}" r="{6*scale:.2f}" fill="none" stroke="#ea580c" stroke-width="1.4" stroke-dasharray="6 4"/>',
        f'<circle cx="{mmcx_axis_x:.2f}" cy="{mmcx_axis_y:.2f}" r="3.2" fill="#ffffff" stroke="#0f766e" stroke-width="2"/>',
        f'<text x="{mmcx_axis_x:.2f}" y="{mmcx_axis_y - 7:.2f}" text-anchor="middle" font-family="sans-serif" font-size="8" font-weight="700" fill="#1d4ed8">7</text>',
        f'<text x="{mmcx_axis_x:.2f}" y="{mmcx_axis_y + mmcx_body/2 + 14:.2f}" text-anchor="middle" font-family="sans-serif" font-size="8" font-weight="700" fill="#1d4ed8">rear-face FPV 5.8G</text>',
        f'<path d="M {mmcx_axis_x:.2f} {mmcx_axis_y:.2f} L {fpv_x:.2f} {fpv_cy:.2f}" stroke="#0f766e" stroke-width="3" fill="none"/>',
        f'<path d="M {fpv_x + fpv["size_mm"][0] * scale:.2f} {fpv_cy:.2f} L {rf_x-20:.2f} {fpv_cy:.2f} L {ox["ui-inner"]+board_w*scale+20:.2f} {dec_cy:.2f} L {dec_x:.2f} {dec_cy:.2f}" stroke="#7c3aed" stroke-width="3" fill="none" stroke-dasharray="7 4" data-medium="one-75-ohm-cvbs-through-m1"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/></marker></defs>',
    ])

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
        f'<text x="{audit_x}" y="344" font-family="sans-serif" font-size="15" font-weight="700" fill="#9a3412">Blocks H1 now</text>',
    ])
    y = 370
    for gate in model["current_h1_blockers"]:
        gate_lines = textwrap.wrap(gate, width=38, break_long_words=False, break_on_hyphens=False)
        for offset, line in enumerate(gate_lines):
            prefix = "• " if offset == 0 else "  "
            out.append(f'<text x="{audit_x}" y="{y}" font-family="sans-serif" font-size="10.5" fill="#9a3412">{esc(prefix + line)}</text>')
            y += 15
        y += 6
    out.append(f'<text x="{audit_x}" y="{y + 10}" font-family="sans-serif" font-size="14" font-weight="700" fill="#526076">Dependent H1 work</text>')
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
    legacy.RF_USER_LABEL_LINES = {
        "N24-0": ("nRF1",),
        "S3-2G4": ("S3 · 2.4G",),
        "N24-1": ("nRF2",),
        "C5-2G4/5": ("C5 · 2.4/5G",),
        "N24-2": ("nRF3",),
        "RX-FM/SW": ("FM/SW/AIR RX",),
        "RX-AM/LW": ("AM/LW RX",),
        "CC-SUB": ("SUB-G RX/TX",),
        "VOICE-VHF": ("VHF RX/TX",),
        "VOICE-UHF": ("UHF RX/TX",),
    }
    svg = legacy.render_external(devices, instances)
    marker = html.escape(model["marker"])
    svg = svg.replace(
        'data-review-gate="H1.3.1" data-review-status="reviewed"',
        f'data-marker="{marker}" data-review-status="in-progress"',
    ).replace(
        "Leshy2 — dimensioned external layout",
        f"Leshy2 — {marker} current external layout",
    ).replace(
        "Text on a PCB face but outside component outlines is intended silkscreen; text outside PCB faces or inside outlines is drawing annotation.",
        "Current R2 exterior. PCB-face free text is silkscreen; drawing notes and arrows are annotations. H1 remains in progress.",
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

    additions = [
        f'<g id="h1-r2-external-delta" data-marker="{marker}" data-state="in-progress">',
        # The mid-mount USB body is on UI-inner. Only its bottom opening,
        # outward direction and user-readable outer-face silk belong here.
        f'<rect x="{px(front,12.0):.1f}" y="{py(front,147.4):.1f}" width="{8.94*scale:.1f}" height="{2.6*scale:.1f}" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1.6" data-instance="hub_service_usb_connector" data-mpn="USB4105-GF-A"/>',
        f'<path d="M{px(front,16.47):.1f} {py(front,150):.1f} V{py(front,158):.1f}" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrow)"/>',
        label(px(front,16.47), py(front,146.2), "HUB SERVICE USB", "middle"),
    ]
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
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    axis_x, axis_y = mmcx["mounting"]["mounting_axis_world_xy_mm"]
    body = mmcx["size_mm"][0]
    plug = mmcx["mounting"]["controlled_right_angle_plug_reference"]
    fpv_x, fpv_y = mmcx["world_xy_mm"]
    additions.extend(
        [
            f'<rect x="{px(rear,fpv_x):.1f}" y="{py(rear,fpv_y):.1f}" width="{body*scale:.1f}" height="{body*scale:.1f}" rx="2" fill="#dbeafe" stroke="#2563eb" stroke-width="1.6" data-instance="fpv_mmcx" data-mpn="73415-2063"/>',
            f'<path d="M{px(rear,axis_x):.1f} {py(rear,axis_y):.1f} H{px(rear,axis_x - plug["strain_relief_run_max_mm"]):.1f}" stroke="#0f766e" stroke-width="{plug["strain_relief_width_max_mm"]*scale:.1f}" stroke-linecap="round" data-part="controlled-right-angle-plug-envelope" data-reference-mpn="{html.escape(plug["mpn"])}"/>',
            f'<circle cx="{px(rear,axis_x):.1f}" cy="{py(rear,axis_y):.1f}" r="{plug["connector_head_width_max_mm"]*scale/2:.1f}" fill="#fff" stroke="#0f766e" stroke-width="1.5"/>',
            f'<path d="M{px(rear,axis_x - 4):.1f} {py(rear,axis_y):.1f} H{px(rear,axis_x - 10):.1f}" stroke="#dc2626" stroke-width="1.4" marker-end="url(#arrow)"/>',
            label(px(rear,axis_x), py(rear,15.6), "FPV RX 5.8G", "middle", 5.2),
            '</g>',
        ]
    )
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
        (front, 16.47, "HUB SERVICE USB", "data only", 146.0),
        (front, 31.47, "C5 SERVICE USB", "data only", 149.0),
        (rear, 16.47, "USB / POWER", "S3 native + power/charge", 149.0),
        (rear, 37.47, "RF RP SERVICE USB", "data only", 149.0),
    ]
    for origin, cx, visible, note, silk_y in bottom_ports:
        out.append(f'<rect x="{x(origin,cx)-12.5:.1f}" y="{y(origin,board_h)-3:.1f}" width="25" height="12" rx="5" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5" data-mpn="USB4105-GF-A"/>')
        out.append(f'<path d="M{x(origin,cx):.1f} {y(origin,board_h):.1f} L{x(origin,cx):.1f} {y(origin,board_h)+34:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(t(x(origin,cx), y(origin,silk_y), visible, 6.7, "bold", "middle", "#1d4ed8", True))
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
        t(30, 68, "Both boards are physically turned over and therefore mirrored. Numbers are drawing references; inner faces contain no silkscreen.", 12, colour="#526076"),
    ]
    for frame, title in (("ui-inner", "UI PCB · inner · mirrored"), ("rf-inner", "RF / power PCB · inner · mirrored")):
        origin = origins[frame]
        out.append(t(origin[0] + board_w*scale/2, 110, title, 16, "bold", "middle"))
        out.append(f'<rect x="{origin[0]:.1f}" y="{origin[1]:.1f}" width="{board_w*scale:.1f}" height="{board_h*scale:.1f}" rx="7" fill="#f8fafc" stroke="#334155" stroke-width="2"/>')
        for hole_x, hole_y in legacy.HOLES:
            out.append(f'<circle cx="{sx(origin,hole_x):.1f}" cy="{sy(origin,hole_y):.1f}" r="{legacy.MOUNT_KEEPOUT_R*scale:.1f}" fill="none" stroke="#f97316" stroke-dasharray="5 3"/>')

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

    # Existing ten antenna topologies are kept as topology guides, not claims
    # of routed production copper. FPV gets its own direct trace pair.
    out.append('<g id="antenna-topology" data-route-state="pre-ecad-topology-only">')
    for guide in legacy.ANTENNA_TOPOLOGY_GUIDES:
        origin = origins[guide.frame]
        points = " ".join(f'{sx(origin,x):.1f},{sy(origin,y):.1f}' for x, y in guide.points)
        out.append(f'<polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="1.4" stroke-dasharray="4 3" data-path="{esc(guide.path)}"/>')
    out.append('</g>')
    fpv = next(item for item in model["placements"] if item["id"] == "fpv_receiver_bay")
    decoder = next(item for item in model["placements"] if item["id"] == "fpv_decoder")
    rf_origin = origins["rf-inner"]
    fpv_x, fpv_y = fpv["world_xy_mm"]
    fpv_w, fpv_h, _ = fpv["size_mm"]
    dec_x, dec_y = decoder["world_xy_mm"]
    dec_w, dec_h, _ = decoder["size_mm"]
    edge_x = sx(rf_origin, 75.0)
    fpv_vx = sx(rf_origin, fpv_x, fpv_w)
    dec_vx = sx(rf_origin, dec_x, dec_w)
    out.extend(
        [
            f'<path d="M{edge_x:.1f} {sy(rf_origin,101.3):.1f} L{fpv_vx:.1f} {sy(rf_origin,fpv_y+fpv_h/2):.1f}" stroke="#0f766e" stroke-width="2.6" fill="none" data-medium="50-ohm-pcb"/>',
            f'<path d="M{fpv_vx+fpv_w*scale:.1f} {sy(rf_origin,fpv_y+fpv_h/2):.1f} L{dec_vx:.1f} {sy(rf_origin,dec_y+dec_h/2):.1f}" stroke="#7c3aed" stroke-width="2.6" fill="none" data-medium="75-ohm-cvbs-pcb"/>',
        ]
    )
    # Exact outward interfaces attached to R2 bodies.
    out.append(f'<path d="M{sx(ui,0):.1f} {sy(ui,137.47):.1f} L{sx(ui,-8):.1f} {sy(ui,137.47):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    for cy in (132.25, 139.25):
        out.append(f'<path d="M{sx(ui,75):.1f} {sy(ui,cy):.1f} L{sx(ui,83):.1f} {sy(ui,cy):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    out.append(f'<path d="M{sx(rf_origin,75):.1f} {sy(rf_origin,101.3):.1f} L{sx(rf_origin,83):.1f} {sy(rf_origin,101.3):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')

    out.extend(
        [
            t(30, 720, f'Numbered registered bodies · {len(rows)} total', 17, "bold"),
            t(410, 720, f'R2 machine audit: zero same-face collisions · {result["minimum_opposing_clearance_mm"]:.2f} mm minimum opposing gap', 12, "bold", colour="#166534"),
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
    source_ids = {
        "N24-0": "nrf0_rf_board_connector_r2",
        "S3-2G4": "s3_rf_board_connector_r2",
        "N24-1": "nrf1_rf_board_connector_r2",
        "C5-2G4/5": "c5_rf_board_connector_r2",
        "N24-2": "nrf2_rf_board_connector_r2",
        "RX-FM/SW": "receiver_r2",
        "RX-AM/LW": "receiver_r2",
        "CC-SUB": "cc_r2",
        "VOICE-VHF": "voice_v",
        "VOICE-UHF": "voice",
    }

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
        text(35, 68, "PCB is physically turned over: X is mirrored. Numbers are drawing references; this face has no silkscreen.", 12, colour="#526076"),
        text(ox + board_w*scale/2, 105, "ANTENNA EDGE · five direct source-board ports", 13, "bold", "middle", "#1d4ed8"),
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
    row_by_id = {row["id"]: row for row in rows}
    out.append('<g id="antenna-topology" data-route-state="pre-ecad-topology-only">')
    for centre, path in zip(centres, paths):
        source = row_by_id[source_ids[path]]
        b = source["bbox"]
        source_x = sx(b["x"][0], b["x"][1] - b["x"][0]) + (b["x"][1] - b["x"][0])*scale/2
        source_y = sy((b["y"][0] + b["y"][1]) / 2)
        port_x = sx(centre)
        out.append(f'<polyline points="{source_x:.1f},{source_y:.1f} {port_x:.1f},{sy(18):.1f} {port_x:.1f},{oy:.1f}" fill="none" stroke="#2563eb" stroke-width="1.4" stroke-dasharray="5 4" data-path="{html.escape(path)}"/>')
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
        out.append(text(vx + body_w*scale/2, vy + body_d*scale/2 + font/3, str(numbers[row["id"]]), font, "bold", "middle", stroke))
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
        f'<line x1="{note_x}" y1="{note_y+48}" x2="{note_x+44}" y2="{note_y+48}" stroke="#2563eb" stroke-width="1.6" stroke-dasharray="5 4"/>',
        text(note_x+56, note_y+52, "source-to-port topology; final copper belongs to KiCad", 10, colour="#526076"),
        text(note_x, note_y+92, "Body key", 16, "bold"),
        '<rect x="550" y="{:.1f}" width="28" height="18" fill="#eef2f6" stroke="#94a3b8"/>'.format(note_y+108),
        text(590, note_y+122, "retained registered body", 10, colour="#526076"),
        '<rect x="550" y="{:.1f}" width="28" height="18" fill="#dbeafe" stroke="#2563eb"/>'.format(note_y+140),
        text(590, note_y+154, "explicit R2 placement", 10, colour="#526076"),
        '<rect x="550" y="{:.1f}" width="28" height="18" fill="#fff7ed" stroke="#ea580c" stroke-dasharray="5 3"/>'.format(note_y+172),
        text(590, note_y+186, "controlled physical reserve", 10, colour="#526076"),
        text(note_x, 1000, "The complete numbered register remains generated for machine review.", 10, colour="#526076"),
        text(note_x, 1020, "The public page uses these two readable one-board maps.", 10, colour="#526076"),
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def render_inner_sections_svg(model: dict, base: dict, source_table: dict, result: dict) -> str:
    """Render true X/Z cuts through the R2 Airband/power and FPV zones."""
    rows = complete_inner_rows(model, base, source_table, result)
    board_w, _board_h = model["board_mm"]
    cuts = ((65.0, "A–A · Airband / 3V3_MAIN"), (101.0, "B–B · analog FPV / service"))
    x_scale = 6.8
    z_scale = 20.0
    panel_w = 700
    top = 150.0
    height = 1000
    esc = html.escape

    def t(x: float, y: float, value: str, size=10, weight="normal", anchor="start", colour="#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="{height}" viewBox="0 0 1500 {height}" data-marker="{esc(model["marker"])}" data-view="true-x-z-sections">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 38, f'Leshy2 — {model["marker"]} R2 inner sandwich sections', 24, "bold"),
        t(30, 66, "Horizontal X and front-to-rear Z use registered millimetre scales. Each panel is one real Y cut; unrelated zones are never merged.", 12, colour="#526076"),
    ]
    legend_entries: list[tuple[int, dict]] = []
    reference = 1
    for panel_index, (cut_y, title) in enumerate(cuts):
        panel_x = 35 + panel_index * panel_w
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
                t(px(37.5), pz(10.6), "exact 11-mm board gap", 9, "bold", "middle", "#526076"),
            ]
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
            t(35, 610, "Bodies crossed by the two planes", 17, "bold"),
            t(500, 610, f'Integrated audit: {result["minimum_opposing_clearance_mm"]:.2f} mm minimum opposing gap against {result["required_opposing_clearance_mm"]:.2f} mm required', 11, "bold", colour="#166534"),
        ]
    )
    per_col = math.ceil(len(legend_entries)/3)
    for index, (ref, row) in enumerate(legend_entries):
        col = index // per_col
        slot = index % per_col
        lx = 35 + col*480
        ly = 640 + slot*38
        out.append(t(lx, ly, f'{ref:02d}  {row["mpn"]}', 8.8, "bold"))
        out.append(t(lx+26, ly+13, row["role"], 7.4, colour="#526076"))
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
    return svg.replace("<svg ", f'<svg data-marker="{html.escape(marker)}" data-review-status="in-progress" ', 1)


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
        f'<text x="40" y="880" font-family="sans-serif" font-size="11" fill="{orange}">H5 verifies received mating/retention, final edge aperture, insertion cycles and antenna strain.</text>',
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
        f'<rect x="{ox-4.5*scale:.1f}" y="{oy+17*scale:.1f}" width="{84*scale:.1f}" height="{24*scale:.1f}" rx="8" fill="#fff7ed" fill-opacity="0.72" stroke="#ea580c" stroke-width="2" data-accessory="U214"/>',
        f'<text x="{ox+37.5*scale:.1f}" y="{oy+30*scale:.1f}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#9a3412">removable U214 Cap zone</text>',
        f'<text x="80" y="530" font-family="sans-serif" font-size="13" fill="#0f766e">✓ static RA plug to nearest SMA: {service["minimum_right_angle_plug_clearance_mm"]:.2f} mm · required {mount["minimum_u214_clearance_mm"]:.1f} mm</text>',
        f'<text x="80" y="560" font-family="sans-serif" font-size="13" fill="#0f766e">✓ static RA plug to U214: {service["right_angle_plug_u214_clearance_mm"]:.2f} mm</text>',
        f'<text x="80" y="590" font-family="sans-serif" font-size="13" fill="#9a3412">△ dashed Ø12 is temporary finger approach; overlaps {", ".join(x["path"] for x in service["handling_envelope_overlaps"])} and closes ergonomically in H5</text>',
        '<text x="80" y="635" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">2 · TRUE SIDE SECTION</text>',
        '<rect x="250" y="730" width="460" height="28" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>',
        '<text x="265" y="750" font-family="sans-serif" font-size="11" fill="#526076">RF PCB · 1.6 mm</text>',
        f'<rect x="444" y="{730-body_h*18:.1f}" width="72" height="{body_h*18:.1f}" rx="5" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>',
        f'<line x1="480" y1="{730-body_h*18:.1f}" x2="480" y2="625" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        '<text x="530" y="665" font-family="sans-serif" font-size="12" fill="#dc2626">plug / antenna points out of the rear face</text>',
        '<text x="80" y="815" font-family="sans-serif" font-size="13" fill="#0f766e">✓ SMT-only: no pins or keepout enter the 11-mm interboard gap.</text>',
        '<text x="80" y="845" font-family="sans-serif" font-size="12" fill="#526076">H5 verifies the received plug, U214 insertion, finger access, retention and antenna strain together.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def render_doc_legacy(model: dict, result: dict, ru: bool) -> str:
    if ru:
        title = f'# {model["marker"]} · физическая перекомпоновка'
        intro = "Это текущий проверяемый результат H1, а не журнал решений и не разрешение начинать KiCad."
        state = "В принятую 75×150-мм систему координат добавлены второй Hub RP, его полный независимый внешний recovery-набор, активные корпуса Airband, расширенная 24×11-мм ячейка настройки фильтра, видеодекодер FPV и сменная зона ведущего серийного кандидата AKK K331. Резерв не превращён в точный корпус до получения контролируемых размеров AKK."
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
            '- На UI-плате остаются четыре SMA, а на RF-плате в один антенный торец помещаются шесть SMA и отдельный MMCX FPV: точные корпуса дают зазоры 0,7 мм и поля платы по 3,0 мм. Радио, ответвители и цепи контроля фактической передачи не переносятся; новых RF-переходов и потерь в тракте нет.',
            '- Обе внутренние стороны теперь зеркалятся при физическом перевороте платы; прежняя инкрементальная картинка ошибочно зеркалила только RF-плату.',
            '- AKK-брендированный размерный кадр у продавца задаёт номинал платы K331 28,7×23,1 мм; коллизии проверены с консервативным резервом 30×24×4 мм без изменения контура платы и внешних зон аккумуляторов/U214.',
            '- Функциональная распиновка K331 принята, но резерв не считается точным корпусом: максимальные XYZ, посадочное место и reflow/packaging должны прийти из контролируемого документа AKK.',
            '- JLCPCB подтвердила отсутствие K331 в Parts Library и Global Sourcing и не нашла прямой замены. Выбран фабричный маршрут: оригинальная поставка AKK через Consigned Parts; application и финальный DFM по Gerber/BOM/CPL относятся к последующим этапам.',
            '- JLCPCB готова рассмотреть процедуру function test для 5 В, channel-select и CVBS. Проверка реализуемости и цена относятся к H5/H6/H7 и не блокируют текущую физическую модель.',
            '- Контролируемый fallback `AWM666V RX` размером 26,16×16,38×3,70 мм и его рекомендованная посадка входят в ту же ячейку; он не заменяет K331 автоматически из-за семи каналов вместо 24 и отсутствия публичного маршрута JLCPCB.',
            '- Точная линейная антенна TBS5G8MMCXA подключается к отдельному MMCX; между ANT IN K331 и MMCX запланирована прямая 50-омная PCB-дорожка без U.FL.',
            '- Исправленная геометрия `DL-MMCX-KWE-90`: 3,6 мм корпуса находятся на RF-плате, ствол выступает за верхний антенный торец на 3,0 мм; выводы входят в межплатный просвет номинально на 1,2 мм, а их keepout не пересекает встречные корпуса.',
            '- Для антенного торца закреплён минимальный свободный диаметр 4,5 мм и внешний коридор подключения Ø12×20 мм. Корпус MMCX оставляет по 0,7 мм до соседних SMA `nRF24-2` и `VHF VOICE`; Ø12-мм монтажная оболочка их перекрывает, поэтому гибкая 102-мм антенна FPV ставится первой. H5 проверяет полученные разъёмы, порядок установки, снятие, удержание и нагрузку антенны.',
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
        state = "The second Hub RP, its complete independent external recovery set, Airband active bodies, an expanded 24 × 11 mm filter-tuning cell, the FPV video decoder and a replaceable bay for the leading serial AKK K331 candidate are placed in the accepted 75 × 150 mm coordinate system. The reserve is not promoted to a fixed body before AKK-controlled dimensions exist."
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
            '- The UI board retains four SMA while the RF board packs six SMA plus the distinct FPV MMCX onto one antenna edge: exact bodies preserve 0.7-mm gaps and 3.0-mm board margins. No radio, coupler or physical-TX evidence chain moves, and no RF transition or link-budget loss is added.',
            '- Both inner faces are now mirrored when each PCB is physically turned over; the earlier incremental view incorrectly mirrored only the RF PCB.',
            '- An AKK-branded dimensioned reseller image gives a 28.7 × 23.1 mm nominal K331 board; collision checks use a conservative 30 × 24 × 4 mm reserve without changing the PCB outline or battery/U214 exterior zones.',
            '- K331 functional pin fit is accepted, but the reserve is not a fixed body: maximum XYZ, land pattern and reflow/packaging must come from an AKK-controlled document.',
            '- JLCPCB confirmed that K331 is absent from both Parts Library and Global Sourcing and found no direct replacement. The selected factory route is genuine AKK supply through Consigned Parts; its application and final Gerber/BOM/CPL DFM are later gates.',
            '- JLCPCB can review a later 5 V, channel-select and CVBS function-test procedure. Feasibility and quotation belong to H5/H6/H7 and do not block the present physical model.',
            '- The controlled 26.16 × 16.38 × 3.70 mm `AWM666V RX` fallback and its recommended land pattern fit the same bay; it does not replace K331 automatically because it has seven channels instead of 24 and no public JLCPCB route.',
            '- The exact linear TBS5G8MMCXA antenna mates with the distinct MMCX; K331 ANT IN reaches it over one direct 50-ohm PCB trace without U.FL.',
            '- Corrected `DL-MMCX-KWE-90` geometry keeps 3.6 mm of body on the RF PCB and projects only the 3.0-mm barrel beyond the top antenna edge; its pins enter the interboard gap by a nominal 1.2 mm and the tail keepout meets no opposing body.',
            '- The antenna edge has a 4.5-mm minimum free aperture and a Ø12×20-mm exterior handling corridor. The MMCX body leaves 0.7 mm to each adjacent `nRF24-2` and `VHF VOICE` SMA; its Ø12-mm handling envelope overlaps them, so the flexible 102-mm FPV antenna is fitted first. H5 verifies received parts, installation/removal order, retention and antenna strain.',
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
        "![H1-R2 current external layout](images/h1-r2-external-layout.svg)",
        "",
        "![H1-R2 complete internal layout](images/h1-r2-inner-complete.svg)",
        "",
        "![H1-R2 external service access](images/h1-r2-service-access.svg)",
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
    marker = f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.' if ru else f'> Exact current marker: **{model["marker"]}**. H1 remains in progress.'
    lines.extend(["", marker, ""])
    return "\n".join(lines)


def render_doc(model: dict, result: dict, ru: bool) -> str:
    """Publish the present product state without the design-decision diary."""
    if ru:
        title = f'# {model["marker"]} · компоновка готового устройства'
        intro = (
            "Текущая физическая модель двух плат 75×150 мм. Это проверяемый результат H1, "
            "но ещё не разрешение начинать KiCad: точный production-пакет K331 остаётся единственным открытым входом."
        )
        outside = "## Что увидит пользователь"
        inside = "## Что находится внутри"
        verified = "## Проверено генератором"
        factory = "## Точные фабричные позиции"
        blocker = "## Текущий блокер H1"
        board_names = ("Передняя UI/radio-плата", "Задняя RF/power-плата")
        bullets = [
            "Десять основных SMA разделены симметрично `5 + 5`; каждый радиотракт остаётся на плате своего разъёма.",
            "Отдельный вертикальный MMCX `FPV RX · 5.8 GHz` расположен ниже равномерного ряда из пяти задних SMA и над U214; ответный угловой штекер с кабелем уходит вдоль платы.",
            "Все пользовательские подписи являются читаемой шелкографией; внутренние стороны плат шелкографии не содержат.",
            "Три nRF24 полностью перенесены на переднюю плату вместе с буферами, safety-gate и отдельным `TLV1824PWR`.",
            "K331 остаётся на задней плате, а `TVP5150AM1PBS` — на передней рядом с S3: через M1 проходит только один 75-омный CVBS, не 11-линейная LCD_CAM-шина.",
            "FM/SW/AM/LW/Airband, CC1101, два voice-тракта и аудио локальны задней плате; дисплей и кнопки остаются прямыми интерфейсами S3.",
        ]
        audit_lines = [
            f'Коллизии корпусов на одной стороне: `{len(result["same_face_collisions"])}`.',
            f'Минимальный встречный Z-зазор: `{result["minimum_opposing_clearance_mm"]:.2f} мм` при требовании `{result["required_opposing_clearance_mm"]:.2f} мм`.',
            f'FPV MMCX: корпус оставляет `{result["mmcx_service"]["minimum_rear_antenna_connector_clearance_mm"]:.2f} мм` до ближайшего SMA; контролируемый угловой штекер — `{result["mmcx_service"]["minimum_right_angle_plug_clearance_mm"]:.2f} мм` до SMA и `{result["mmcx_service"]["right_angle_plug_u214_clearance_mm"]:.2f} мм` до U214. Ø12 — только временная зона пальцев и остаётся H5-проверкой.',
            "GPIO: передний RP `45/48`, задний RP `45/48`; резерв — по 3 линии. K331 RSSI официально помечен NC.",
            "M1: 9 устаревших сигналов освобождены, 1 контакт занят CVBS, 8 сигнальных контактов остаются резервом.",
        ]
        route_col = "Текущая доступность/маршрут"
    else:
        title = f'# {model["marker"]} · finished-device placement'
        intro = (
            "Current physical model of the two 75 × 150 mm PCBs. This is a verifiable H1 result, "
            "not authorization to start KiCad: the controlled K331 production package remains the sole open input."
        )
        outside = "## What the user sees"
        inside = "## What is inside"
        verified = "## Generator-verified"
        factory = "## Exact factory parts"
        blocker = "## Current H1 blocker"
        board_names = ("Front UI/radio PCB", "Rear RF/power PCB")
        bullets = [
            "Ten main SMA ports are split symmetrically `5 + 5`; every radio path remains on the PCB that carries its connector.",
            "The separate vertical `FPV RX · 5.8 GHz` MMCX sits below the evenly pitched five-SMA rear row and above U214; its mating right-angle plug and cable run parallel to the PCB.",
            "All user-facing labels are readable silkscreen; neither inner PCB face carries silkscreen.",
            "All three nRF24 islands move to the front PCB with their buffers, safety gate and a dedicated second `TLV1824PWR`.",
            "K331 remains rear-local while `TVP5150AM1PBS` moves beside S3: M1 carries one 75-ohm CVBS signal, not the 11-line LCD_CAM bus.",
            "FM/SW/AM/LW/Airband, CC1101, both voice paths and audio are rear-local; display and buttons remain direct S3 interfaces.",
        ]
        audit_lines = [
            f'Same-face body collisions: `{len(result["same_face_collisions"])}`.',
            f'Minimum opposing Z clearance: `{result["minimum_opposing_clearance_mm"]:.2f} mm` against `{result["required_opposing_clearance_mm"]:.2f} mm` required.',
            f'FPV MMCX: the jack body leaves `{result["mmcx_service"]["minimum_rear_antenna_connector_clearance_mm"]:.2f} mm` to the nearest SMA; the controlled right-angle plug leaves `{result["mmcx_service"]["minimum_right_angle_plug_clearance_mm"]:.2f} mm` to SMA and `{result["mmcx_service"]["right_angle_plug_u214_clearance_mm"]:.2f} mm` to U214. Ø12 is only a temporary finger-approach zone and remains an H5 ergonomic check.',
            "GPIO: front RP `45/48`, rear RP `45/48`; each retains 3 free lines. K331 RSSI is officially marked NC.",
            "M1: 9 obsolete signals are released, 1 contact carries CVBS and 8 signal contacts remain spare.",
        ]
        route_col = "Current availability/route"
    lines = [
        title, "", intro, "", outside, "",
        "![Current complete exterior](images/h1-r2-external-layout.svg)", "",
        "![External service access](images/h1-r2-service-access.svg)", "",
        inside, "",
        f"### {board_names[0]}", "", "![Front PCB inner face](images/h1-r2-inner-ui.svg)", "",
        f"### {board_names[1]}", "", "![Rear PCB inner face](images/h1-r2-inner-rf.svg)", "",
    ]
    lines.extend(f"- {row}" for row in bullets)
    lines.extend(["", "![True inner sandwich sections](images/h1-r2-inner-sections.svg)", "", "![Rear-face FPV connector proof](images/h1-r2-mmcx-service.svg)", "", verified, ""])
    lines.extend(f"- {row}" for row in audit_lines)
    lines.extend(["", factory, "", f"| {'Роль' if ru else 'Role'} | MPN | JLCPCB | {route_col} |", "|---|---|---|---|"])
    for row in model["factory_evidence"]:
        role = row.get("role_ru", row["role"]) if ru else row["role"]
        route = row.get("availability_ru", row["availability"]) if ru else row["availability"]
        ref = f'[`{row["jlcpcb_part"]}`]({row["url"]})' if row["jlcpcb_part"] else "—"
        lines.append(f'| {role} | `{row["mpn"]}` | {ref} | {route} |')
    blockers = model["current_h1_blockers_ru"] if ru else model["current_h1_blockers"]
    lines.extend(["", blocker, ""])
    lines.extend(f"- {row}" for row in blockers)
    marker = f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.' if ru else f'> Exact current marker: **{model["marker"]}**. H1 remains in progress.'
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
    outputs = {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        SVG_PATH: render_svg(model, base, result),
        MMCX_SVG_PATH: render_mmcx_service_svg(model, result),
        EXTERNAL_SVG_PATH: render_external_svg(model),
        SERVICE_SVG_PATH: render_service_svg(model),
        COMPLETE_INNER_SVG_PATH: render_complete_inner_svg(model, base, source_table, result),
        INNER_UI_SVG_PATH: render_inner_face_svg(model, base, source_table, result, "ui-inner"),
        INNER_RF_SVG_PATH: render_inner_face_svg(model, base, source_table, result, "rf-inner"),
        INNER_SECTIONS_SVG_PATH: render_inner_sections_svg(model, base, source_table, result),
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
