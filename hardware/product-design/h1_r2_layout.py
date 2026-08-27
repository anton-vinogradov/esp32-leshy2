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
INNER_SECTIONS_SVG_PATH = REPO / "docs/images/h1-r2-inner-sections.svg"
ANTENNA_EDGE_SVG_PATH = REPO / "docs/images/h1-r2-antenna-edge.svg"
SANDWICH_SVG_PATH = REPO / "docs/images/h1-r2-sandwich-sections.svg"
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
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mount = mmcx["mounting"]
    board_edge = mount["board_edge_x_mm"]
    x, y = mmcx["world_xy_mm"]
    length, width, body_height = mmcx["size_mm"]
    axis_x, axis_y = mount["mounting_axis_world_xy_mm"]
    rf_inner = model["stack"]["rf_inner_z_mm"]
    pcb_thickness = model["stack"]["rf_pcb_thickness_mm"]
    rf_outer = rf_inner + pcb_thickness
    pin_nominal = mount["pin_projection_below_board_mm"]
    pin_maximum = pin_nominal + mount["pin_projection_tolerance_mm"]
    nominal_tip = rf_outer - pin_nominal
    worst_tip = rf_outer - pin_maximum
    keepout_x, keepout_y = mount["rf_inner_tail_keepout_world_xy_mm"]
    keepout = {
        "x": keepout_x,
        "y": keepout_y,
        "z": [worst_tip, rf_inner],
    }
    errors: list[str] = []

    def close(a: float, b: float) -> bool:
        return abs(a - b) < 1e-6

    if not close(x, board_edge - mount["body_inboard_mm"]):
        errors.append("MMCX square body is not registered to the PCB edge")
    if not close(x + length, board_edge + mount["barrel_outboard_mm"]):
        errors.append("MMCX barrel projection does not match the manufacturer drawing")
    if not close(axis_x, x + mount["square_body_mm"] / 2) or not close(axis_y, y + width / 2):
        errors.append("MMCX mounting axis is not centred in the 3.6-mm square body")
    if not close(pin_nominal - pcb_thickness, mount["tail_projection_into_interboard_gap_mm"]):
        errors.append("MMCX solder-tail projection into the interboard gap is inconsistent")
    radial_clearance = (mount["minimum_sidewall_free_diameter_mm"] - mount["barrel_diameter_mm"]) / 2
    if radial_clearance + 1e-6 < mount["minimum_sidewall_radial_clearance_mm"]:
        errors.append("MMCX sidewall aperture does not preserve the required radial clearance")
    if mount["external_plug_service_keepout_diameter_mm"] < mount["minimum_sidewall_free_diameter_mm"]:
        errors.append("MMCX plug service keepout is smaller than the wall aperture")

    axis_z = rf_outer + body_height / 2
    aperture_radius = mount["minimum_sidewall_free_diameter_mm"] / 2
    service_radius = mount["external_plug_service_keepout_diameter_mm"] / 2
    aperture_keepout = {
        "x": [board_edge, x + length],
        "y": [axis_y - aperture_radius, axis_y + aperture_radius],
        "z": [axis_z - aperture_radius, axis_z + aperture_radius],
    }
    external_service_keepout = {
        "x": [x + length, x + length + mount["external_plug_service_keepout_length_mm"]],
        "y": [axis_y - service_radius, axis_y + service_radius],
        "z": [axis_z - service_radius, axis_z + service_radius],
    }

    def overlaps_3d(a: dict, b: dict) -> bool:
        return overlaps(a, b) and a["z"][0] < b["z"][1] and a["z"][1] > b["z"][0]

    accessory_hits: list[dict] = []
    for name, envelope in base["accessory_envelopes"].items():
        accessory = {"x": envelope["x_mm"], "y": envelope["y_mm"], "z": envelope["z_mm"]}
        zones = [
            zone
            for zone, candidate in (
                ("sidewall_aperture", aperture_keepout),
                ("plug_service", external_service_keepout),
            )
            if overlaps_3d(candidate, accessory)
        ]
        if zones:
            accessory_hits.append({"id": name, "zones": zones})
            errors.append(f"MMCX exterior service keepout intersects accessory {name}: {', '.join(zones)}")

    opposing: list[dict] = []
    candidates = [
        {"id": row["instance"], "frame": row["source_frame"], "bbox": row["world_bbox_mm"]}
        for row in base["rows"]
        if row["source_frame"] == "ui-inner"
    ]
    candidates.extend(
        {"id": entry["item"]["id"], "frame": entry["item"]["frame"], "bbox": entry["bbox"]}
        for entry in placed
        if entry["item"]["frame"] == "ui-inner"
    )
    for candidate in candidates:
        if not overlaps(keepout, candidate["bbox"]):
            continue
        clearance = z_clearance(keepout, candidate["bbox"])
        opposing.append({"id": candidate["id"], "clearance_mm": round(clearance, 3)})
        if clearance < model["stack"]["minimum_opposing_clearance_mm"]:
            errors.append(
                f"MMCX tail/service keepout collides with {candidate['id']} at {clearance:.3f} mm"
            )
    return {
        "status": "pass" if not errors else "fail",
        "mpn": mmcx["mpn"],
        "drawing_source": next(
            row["drawing_url"] for row in model["factory_evidence"] if row["mpn"] == mmcx["mpn"]
        ),
        "installed_body_world_bbox_mm": {
            "x": [round(x, 3), round(x + length, 3)],
            "y": [round(y, 3), round(y + width, 3)],
            "z": [round(rf_outer, 3), round(rf_outer + body_height, 3)],
        },
        "board_edge_x_mm": board_edge,
        "mounting_axis_world_xy_mm": [axis_x, axis_y],
        "inboard_body_mm": mount["body_inboard_mm"],
        "outboard_barrel_mm": mount["barrel_outboard_mm"],
        "nominal_tail_tip_z_mm": round(nominal_tip, 3),
        "worst_case_tail_tip_z_mm": round(worst_tip, 3),
        "nominal_tail_projection_into_gap_mm": mount["tail_projection_into_interboard_gap_mm"],
        "tail_keepout_world_bbox_mm": keepout,
        "opposing_body_hits": opposing,
        "sidewall_minimum_free_diameter_mm": mount["minimum_sidewall_free_diameter_mm"],
        "sidewall_radial_clearance_mm": round(radial_clearance, 3),
        "sidewall_aperture_world_bbox_mm": aperture_keepout,
        "external_service_keepout": {
            "diameter_mm": mount["external_plug_service_keepout_diameter_mm"],
            "outward_length_mm": mount["external_plug_service_keepout_length_mm"],
            "world_bbox_mm": external_service_keepout,
        },
        "accessory_hits": accessory_hits,
        "factory_assembly": "Wave Soldering; Economic and Standard PCBA",
        "later_hil": [
            "received connector-to-antenna mating and retention",
            "final enclosure aperture tolerance",
            "plug insertion cycles and cable strain",
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
    if len(model["current_h1_blockers"]) != 2:
        errors.append("physical layout must expose exactly the two present H1 blockers")
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

    # Physical device-right becomes viewer-left on the mirrored RF inner face.
    rf_x = ox["rf-inner"]
    mmcx = next(item for item in model["placements"] if item["id"] == "fpv_mmcx")
    mmcx_w = mmcx["size_mm"][0] * scale
    mmcx_h = mmcx["size_mm"][1] * scale
    mmcx_y = oy + mmcx["world_xy_mm"][1] * scale
    mmcx_mount = mmcx["mounting"]
    mmcx_outboard_w = mmcx_mount["barrel_outboard_mm"] * scale
    mmcx_inboard_w = mmcx_mount["body_inboard_mm"] * scale
    mmcx_axis_x = rf_x + (board_w - mmcx_mount["mounting_axis_world_xy_mm"][0]) * scale
    mmcx_axis_y = oy + mmcx_mount["mounting_axis_world_xy_mm"][1] * scale
    fpv = next(item for item in model["placements"] if item["id"] == "fpv_receiver_bay")
    dec = next(item for item in model["placements"] if item["id"] == "fpv_decoder")
    fpv_x = rf_x + (board_w - fpv["world_xy_mm"][0] - fpv["size_mm"][0]) * scale
    fpv_cy = oy + (fpv["world_xy_mm"][1] + fpv["size_mm"][1] / 2) * scale
    dec_x = rf_x + (board_w - dec["world_xy_mm"][0] - dec["size_mm"][0]) * scale
    dec_cy = oy + (dec["world_xy_mm"][1] + dec["size_mm"][1] / 2) * scale
    out.extend([
        rect(rf_x, mmcx_y, mmcx_inboard_w, mmcx_h, rx="2", fill="#dbeafe", stroke="#1d4ed8", stroke_width="2"),
        rect(rf_x - mmcx_outboard_w, mmcx_y + 0.18 * mmcx_h, mmcx_outboard_w, 0.64 * mmcx_h, rx="2", fill="#bfdbfe", stroke="#1d4ed8", stroke_width="2"),
        f'<circle cx="{mmcx_axis_x:.2f}" cy="{mmcx_axis_y:.2f}" r="3.2" fill="#ffffff" stroke="#0f766e" stroke-width="2"/>',
        f'<text x="{mmcx_axis_x:.2f}" y="{mmcx_axis_y - 7:.2f}" text-anchor="middle" font-family="sans-serif" font-size="8" font-weight="700" fill="#1d4ed8">7</text>',
        f'<path d="M {rf_x - mmcx_outboard_w:.2f} {mmcx_y + mmcx_h / 2:.2f} L {rf_x - mmcx_outboard_w - 18:.2f} {mmcx_y + mmcx_h / 2:.2f}" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>',
        f'<text x="{rf_x - mmcx_outboard_w - 22:.2f}" y="{mmcx_y + mmcx_h / 2 - 2:.2f}" text-anchor="end" font-family="sans-serif" font-size="9" font-weight="700" fill="#dc2626">finished-device RIGHT side</text>',
        f'<path d="M {mmcx_axis_x:.2f} {mmcx_axis_y:.2f} L {fpv_x:.2f} {fpv_cy:.2f}" stroke="#0f766e" stroke-width="3" fill="none"/>',
        f'<path d="M {fpv_x + fpv["size_mm"][0] * scale:.2f} {fpv_cy:.2f} L {dec_x:.2f} {dec_cy:.2f}" stroke="#7c3aed" stroke-width="3" fill="none"/>',
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
        # The rotated mid-mount USB body is on UI-inner. Only its side opening,
        # outward direction and user-readable outer-face silk belong here.
        f'<rect x="{px(front,-1.2):.1f}" y="{py(front,133.0):.1f}" width="{2.6*scale:.1f}" height="{8.94*scale:.1f}" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1.6" data-instance="hub_service_usb_connector" data-mpn="USB4105-GF-A"/>',
        f'<path d="M{px(front,0):.1f} {py(front,137.47):.1f} L{px(front,-8):.1f} {py(front,137.47):.1f}" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrow)"/>',
        label(px(front,2.2), py(front,136.3), "HUB SERVICE USB"),
    ]
    for item in model["placements"]:
        if item["id"] not in {"hub_reset_button", "hub_boot_button"}:
            continue
        x, y = item["world_xy_mm"]
        _w, h, _z = item["size_mm"]
        cy = y + h / 2
        visible = item["external_interface"]["label"]
        additions.extend(
            [
                f'<rect x="{px(front,74.2):.1f}" y="{py(front,y-0.25):.1f}" width="{1.2*scale:.1f}" height="{(h+0.5)*scale:.1f}" rx="2" fill="none" stroke="#ea580c" stroke-dasharray="3 2" data-instance="{item["id"]}" data-recess-mm="1.2"/>',
                f'<path d="M{px(front,75):.1f} {py(front,cy):.1f} L{px(front,83):.1f} {py(front,cy):.1f}" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrow)"/>',
                label(px(front,72.9), py(front,cy+0.5), visible, "end"),
            ]
        )
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mx, my = mmcx["world_xy_mm"]
    _mw, mh, _mz = mmcx["size_mm"]
    additions.extend(
        [
            f'<rect x="{px(rear,mx):.1f}" y="{py(rear,my):.1f}" width="{(75-mx)*scale:.1f}" height="{mh*scale:.1f}" rx="2" fill="#dbeafe" stroke="#2563eb" stroke-width="1.6" data-instance="fpv_mmcx" data-mpn="DL-MMCX-KWE-90"/>',
            f'<rect x="{px(rear,75):.1f}" y="{py(rear,my+0.65):.1f}" width="{3.0*scale:.1f}" height="{(mh-1.3)*scale:.1f}" rx="3" fill="#bfdbfe" stroke="#2563eb" stroke-width="1.6"/>',
            f'<path d="M{px(rear,78):.1f} {py(rear,my+mh/2):.1f} L{px(rear,86):.1f} {py(rear,my+mh/2):.1f}" stroke="#dc2626" stroke-width="1.6" marker-end="url(#arrow)"/>',
            label(px(rear,70.6), py(rear,my-1.0), "FPV RX 5.8G", "end", 5.8),
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

    # Exact user connectors. The Hub port is side-facing; the other three are
    # bottom-facing. Service VBUS remains sense-only and cannot power Leshy2.
    bottom_ports = [
        (front, 31.47, "C5 SERVICE USB", "data only"),
        (rear, 16.47, "USB / POWER", "S3 native + power/charge"),
        (rear, 37.47, "RF RP SERVICE USB", "data only"),
    ]
    for origin, cx, visible, note in bottom_ports:
        out.append(f'<rect x="{x(origin,cx)-12.5:.1f}" y="{y(origin,board_h)-3:.1f}" width="25" height="12" rx="5" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5" data-mpn="USB4105-GF-A"/>')
        out.append(f'<path d="M{x(origin,cx):.1f} {y(origin,board_h):.1f} L{x(origin,cx):.1f} {y(origin,board_h)+34:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(t(x(origin,cx), y(origin,board_h)-4, visible, 6.7, "bold", "middle", "#1d4ed8", True))
        out.append(t(x(origin,cx), y(origin,board_h)+50, note, 7.2, anchor="middle", colour="#526076"))
    hub_y = 137.47
    out.extend(
        [
            f'<rect x="{x(front,-1.0):.1f}" y="{y(front,133.0):.1f}" width="{2.4*scale:.1f}" height="{8.94*scale:.1f}" rx="4" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5" data-mpn="USB4105-GF-A"/>',
            f'<path d="M{x(front,0):.1f} {y(front,hub_y):.1f} L{x(front,-10):.1f} {y(front,hub_y):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>',
            t(x(front,2.5), y(front,135.8), "HUB SERVICE USB", 6.7, "bold", "start", "#1d4ed8", True),
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
    return svg.replace("<svg ", f'<svg data-marker="{html.escape(marker)}" data-review-status="in-progress" ', 1)


def render_mmcx_service_svg(model: dict, result: dict) -> str:
    service = result["mmcx_service"]
    mmcx = next(x for x in model["placements"] if x["id"] == "fpv_mmcx")
    mount = mmcx["mounting"]
    esc = html.escape
    green = "#0f766e"
    blue = "#2563eb"
    orange = "#ea580c"
    ink = "#172033"
    muted = "#526076"
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1030" viewBox="0 0 900 1030">',
        '<rect width="900" height="1030" fill="#ffffff"/>',
        '<defs><marker id="redArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/></marker></defs>',
        f'<text x="32" y="42" font-family="sans-serif" font-size="25" font-weight="700" fill="{ink}">Leshy2 · {esc(model["marker"])} MMCX placement and service proof</text>',
        f'<text x="32" y="70" font-family="sans-serif" font-size="13" fill="{muted}">DL-MMCX-KWE-90 · C2894793 · exact body geometry; enclosure values are minimum keepouts, not a final wall design.</text>',
        f'<text x="40" y="112" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">1 · TOP / PLAN · looking at the RF outer face from the rear</text>',
        '<rect x="40" y="145" width="330" height="250" rx="8" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
        f'<text x="55" y="172" font-family="sans-serif" font-size="12" fill="{muted}">RF PCB</text>',
        f'<line x1="370" y1="135" x2="370" y2="405" stroke="{ink}" stroke-width="3"/>',
        f'<text x="370" y="425" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{ink}">PCB edge X=75.0</text>',
        f'<rect x="334" y="230" width="36" height="72" rx="3" fill="#dbeafe" stroke="{blue}" stroke-width="2"/>',
        f'<rect x="370" y="243" width="30" height="46" rx="4" fill="#bfdbfe" stroke="{blue}" stroke-width="2"/>',
        f'<circle cx="352" cy="266" r="6" fill="#ffffff" stroke="{green}" stroke-width="2"/>',
        f'<text x="352" y="217" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="{blue}">3.6-mm square body on PCB</text>',
        f'<text x="385" y="326" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="{blue}">3.0 mm outboard</text>',
        f'<line x1="400" y1="266" x2="650" y2="266" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        f'<text x="525" y="250" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="#dc2626">device RIGHT · plug insertion</text>',
        f'<rect x="400" y="206" width="250" height="120" rx="60" fill="none" stroke="{orange}" stroke-width="2" stroke-dasharray="8 5"/>',
        f'<text x="525" y="349" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{orange}">12-mm Ø × 20-mm outward service corridor</text>',
        f'<text x="40" y="473" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">Manufacturer drawing → installed envelope</text>',
        f'<text x="40" y="500" font-family="sans-serif" font-size="12" fill="{muted}">6.60 ± 0.20 mm total · SQ3.60 body · Ø3.50 interface</text>',
        f'<text x="40" y="522" font-family="sans-serif" font-size="12" fill="{muted}">4 × SQ0.50 ± 0.05 posts · 2.00 × 2.00 mm pitch</text>',
        f'<text x="40" y="544" font-family="sans-serif" font-size="12" fill="{muted}">World X {service["installed_body_world_bbox_mm"]["x"][0]:.1f}…{service["installed_body_world_bbox_mm"]["x"][1]:.1f}; axis ({service["mounting_axis_world_xy_mm"][0]:.1f}, {service["mounting_axis_world_xy_mm"][1]:.1f}) mm</text>',
        f'<text x="40" y="600" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">2 · SECTION ALONG MMCX AXIS · looking from device bottom</text>',
        f'<rect x="70" y="710" width="430" height="40" fill="#f1f5f9" stroke="#334155" stroke-width="2"/>',
        f'<text x="85" y="736" font-family="sans-serif" font-size="11" fill="{muted}">RF PCB · 1.6 mm</text>',
        f'<line x1="500" y1="635" x2="500" y2="810" stroke="{ink}" stroke-width="3"/>',
        f'<text x="500" y="832" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{ink}">device side plane</text>',
        f'<rect x="464" y="650" width="36" height="60" rx="3" fill="#dbeafe" stroke="{blue}" stroke-width="2"/>',
        f'<rect x="500" y="664" width="60" height="32" rx="5" fill="#bfdbfe" stroke="{blue}" stroke-width="2"/>',
        f'<rect x="476" y="750" width="8" height="44" fill="#ccfbf1" stroke="{green}" stroke-width="2"/>',
        f'<line x1="560" y1="680" x2="760" y2="680" stroke="#dc2626" stroke-width="2.5" marker-end="url(#redArrow)"/>',
        f'<text x="660" y="663" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="#dc2626">outward mating direction</text>',
        f'<line x1="560" y1="650" x2="560" y2="710" stroke="{orange}" stroke-width="2" stroke-dasharray="6 4"/>',
        f'<text x="580" y="724" font-family="sans-serif" font-size="11" fill="{orange}">≥ {mount["minimum_sidewall_free_diameter_mm"]:.1f}-mm free wall aperture</text>',
        f'<text x="580" y="746" font-family="sans-serif" font-size="10" fill="{orange}">0.5-mm radial minimum around Ø3.50</text>',
        f'<text x="40" y="890" font-family="sans-serif" font-size="16" font-weight="700" fill="{ink}">3 · TAIL / OPPOSING-SIDE CHECK</text>',
        f'<text x="40" y="918" font-family="sans-serif" font-size="12" fill="{muted}">2.80 ± 0.15-mm pins through 1.60-mm PCB → nominal 1.20 mm into the 11-mm interboard gap.</text>',
        f'<text x="40" y="944" font-family="sans-serif" font-size="12" fill="{green}">✓ Tail keepout opposing-body hits: {len(service["opposing_body_hits"])} · factory route: wave soldering</text>',
        f'<text x="40" y="970" font-family="sans-serif" font-size="11" fill="{orange}">H5 later verifies received mating/retention, final enclosure tolerance, insertion cycles and cable strain.</text>',
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_doc(model: dict, result: dict, ru: bool) -> str:
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
            '- Исправлено найденное расхождение H0↔H1: Hub RP получил четвёртый независимый data-only `HUB SERVICE USB`, две утопленные боковые кнопки `HUB RST/BOOT` и четвёртый внутренний DBG10. Все три повторно используемых MPN имеют живые точные карточки JLCPCB.',
            '- Обе внутренние стороны теперь зеркалятся при физическом перевороте платы; прежняя инкрементальная картинка ошибочно зеркалила только RF-плату.',
            '- AKK-брендированный размерный кадр у продавца задаёт номинал платы K331 28,7×23,1 мм; коллизии проверены с консервативным резервом 30×24×4 мм без изменения контура платы и внешних зон аккумуляторов/U214.',
            '- Функциональная распиновка K331 принята, но резерв не считается точным корпусом: максимальные XYZ, посадочное место и reflow/packaging должны прийти из контролируемого документа AKK.',
            '- Контролируемый fallback `AWM666V RX` размером 26,16×16,38×3,70 мм и его рекомендованная посадка входят в ту же ячейку; он не заменяет K331 автоматически из-за семи каналов вместо 24 и отсутствия публичного маршрута JLCPCB.',
            '- Точная линейная антенна TBS5G8MMCXA подключается к отдельному MMCX; между ANT IN K331 и MMCX запланирована прямая 50-омная PCB-дорожка без U.FL.',
            '- Исправленная геометрия `DL-MMCX-KWE-90`: 3,6 мм корпуса находятся на RF-плате, ствол выступает за правую кромку на 3,0 мм; выводы входят в межплатный просвет номинально на 1,2 мм, а их keepout не пересекает встречные корпуса.',
            '- Для боковой стенки закреплён минимальный свободный диаметр 4,5 мм, для подключения — свободный внешний коридор Ø12×20 мм. Полученный экземпляр, финальный допуск стенки, удержание и нагрузку кабеля проверяет H5.',
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
            '- The discovered H0↔H1 mismatch is corrected: Hub RP now has the fourth independent data-only `HUB SERVICE USB`, two recessed side `HUB RST/BOOT` controls and the fourth internal DBG10. All three reused MPNs have live exact JLCPCB cards.',
            '- Both inner faces are now mirrored when each PCB is physically turned over; the earlier incremental view incorrectly mirrored only the RF PCB.',
            '- An AKK-branded dimensioned reseller image gives a 28.7 × 23.1 mm nominal K331 board; collision checks use a conservative 30 × 24 × 4 mm reserve without changing the PCB outline or battery/U214 exterior zones.',
            '- K331 functional pin fit is accepted, but the reserve is not a fixed body: maximum XYZ, land pattern and reflow/packaging must come from an AKK-controlled document.',
            '- The controlled 26.16 × 16.38 × 3.70 mm `AWM666V RX` fallback and its recommended land pattern fit the same bay; it does not replace K331 automatically because it has seven channels instead of 24 and no public JLCPCB route.',
            '- The exact linear TBS5G8MMCXA antenna mates with the distinct MMCX; K331 ANT IN reaches it over one direct 50-ohm PCB trace without U.FL.',
            '- Corrected `DL-MMCX-KWE-90` geometry keeps 3.6 mm of body on the RF PCB and projects only the 3.0-mm barrel beyond the right edge; its pins enter the interboard gap by a nominal 1.2 mm and the tail keepout meets no opposing body.',
            '- The side wall now has a 4.5-mm minimum free aperture and the plug a clear Ø12×20-mm exterior service corridor. H5 later verifies the received mating pair, final wall tolerance, retention and cable strain.',
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
        INNER_SECTIONS_SVG_PATH: render_inner_sections_svg(model, base, source_table, result),
        ANTENNA_EDGE_SVG_PATH: render_retitled_legacy_view(model, "render_top_edge"),
        SANDWICH_SVG_PATH: render_retitled_legacy_view(model, "render_sandwich"),
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
