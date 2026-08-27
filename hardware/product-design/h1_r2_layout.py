#!/usr/bin/env python3
"""Validate and render the incremental H1-R2 physical placement."""

from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-placement.json"
BASE_PATH = REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-placement-audit.json"
SVG_PATH = REPO / "docs/images/h1-r2-inner-placement.svg"
MMCX_SVG_PATH = REPO / "docs/images/h1-r2-mmcx-service.svg"
EN_DOC_PATH = REPO / "docs/h1-r2-physical-layout.md"
RU_DOC_PATH = REPO / "docs/h1-r2-physical-layout.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


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
        '<text x="40" y="70" font-family="sans-serif" font-size="13" fill="#526076">World-scale engineering view · RF board is mirrored · numbered marks are documentation, never inner-face silkscreen.</text>',
    ]
    for frame, title in (("ui-inner", "UI PCB · inner"), ("rf-inner", "RF / power PCB · inner · mirrored")):
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
            if frame == "rf-inner":
                x = board_w - b["x"][1]
            out.append(rect(x0 + x * scale, oy + b["y"][0] * scale, (b["x"][1] - b["x"][0]) * scale, (b["y"][1] - b["y"][0]) * scale, fill="#e2e8f0", stroke="#cbd5e1", stroke_width="0.7"))

        for item in model["placements"]:
            if item["frame"] != frame:
                continue
            x, y = item["world_xy_mm"]
            w, h, _ = item["size_mm"]
            if frame == "rf-inner":
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
        state = "В принятую 75×150-мм систему координат добавлены второй Hub RP, активные корпуса Airband, расширенная 24×11-мм ячейка настройки его фильтра, видеодекодер FPV и сменная зона ведущего серийного кандидата AKK K331. Резерв не превращён в точный корпус до получения контролируемых размеров AKK."
        audit_heading = "## Что уже проверено"
        open_heading = "## Что блокирует H1 сейчас"
        dependent_heading = "## Зависимая работа H1"
        downstream_heading = "## Последующая проверка — не блокирует H1"
        factory_heading = "## Точные фабричные позиции"
        bullets = [
            f'- Коллизии корпусов на одной стороне: `{len(result["same_face_collisions"])}`.',
            f'- Намеренных встречных XY-проекций: `{result["opposing_overlap_count"]}`; минимальный Z-зазор `{result["minimum_opposing_clearance_mm"]:.2f} мм` при требовании `{result["required_opposing_clearance_mm"]:.2f} мм`.',
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
        state = "The second Hub RP, Airband active bodies, an expanded 24 × 11 mm tuning cell for its filter, the FPV video decoder and a replaceable bay for the leading serial AKK K331 candidate are placed in the accepted 75 × 150 mm coordinate system. The reserve is not promoted to a fixed body before AKK-controlled dimensions exist."
        audit_heading = "## Already verified"
        open_heading = "## What blocks H1 now"
        dependent_heading = "## Dependent H1 work"
        downstream_heading = "## Later verification — does not block H1"
        factory_heading = "## Exact factory parts"
        bullets = [
            f'- Same-face body collisions: `{len(result["same_face_collisions"])}`.',
            f'- Intentional opposing XY projections: `{result["opposing_overlap_count"]}`; minimum Z clearance is `{result["minimum_opposing_clearance_mm"]:.2f} mm` against `{result["required_opposing_clearance_mm"]:.2f} mm` required.',
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
        "![H1-R2 inner placement](images/h1-r2-inner-placement.svg)",
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
    result = audit(model, base)
    outputs = {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        SVG_PATH: render_svg(model, base, result),
        MMCX_SVG_PATH: render_mmcx_service_svg(model, result),
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
