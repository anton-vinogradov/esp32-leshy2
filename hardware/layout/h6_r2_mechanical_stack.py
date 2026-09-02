#!/usr/bin/env python3
"""Audit and render the local H6 R2 enclosure/fastener stack."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/layout/h6-r2-mechanical-stack.json"
PLACEMENT = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-mechanical-stack-audit.json"
SVG = ROOT / "docs/images/h6-r2-mechanical-stack.svg"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(row: dict) -> tuple[float, float, float]:
    nominal = float(row["nominal"])
    return nominal, nominal - float(row["minus"]), nominal + float(row["plus"])


def evaluate(contract: dict, placement: dict) -> dict:
    errors: list[str] = []
    stack = contract["tolerance_stack"]
    members = [
        "front_bearing_floor_mm",
        "ui_pcb_mm",
        "compression_stop_mm",
        "rf_pcb_mm",
        "rear_bearing_floor_mm",
    ]
    values = [bounds(stack[name]) for name in members]
    nominal = sum(value[0] for value in values)
    minimum = sum(value[1] for value in values)
    maximum = sum(value[2] for value in values)

    screw = contract["selected_hardware"]["screw"]
    screw_min, screw_max = map(float, screw["length_receipt_window_mm"])
    remaining_nominal = float(screw["length_below_head_nominal_mm"]) - nominal
    remaining_minimum = screw_min - maximum
    remaining_maximum = screw_max - minimum
    nut_min, nut_max = map(
        float, contract["selected_hardware"]["nut"]["height_design_range_mm"]
    )
    thread_beyond_nut_min = remaining_minimum - nut_max
    thread_beyond_nut_max = remaining_maximum - nut_min

    if remaining_minimum < float(stack["required_full_nut_engagement_mm"]):
        errors.append("worst-case screw length does not fully engage the maximum nut height")
    if thread_beyond_nut_min < float(stack["minimum_thread_beyond_nut_mm"]):
        errors.append("worst-case screw has too little thread beyond the nut")
    if thread_beyond_nut_max > float(stack["maximum_thread_beyond_nut_mm"]):
        errors.append("worst-case screw has too much thread beyond the nut")

    mechanical = contract["enclosure_local_geometry"]
    head_keepout_diameter = 8.0
    if mechanical["bearing_annulus_outside_diameter_mm"] > head_keepout_diameter:
        errors.append("bearing annulus exceeds the native PCB mounting keepout")
    if mechanical["front_head_recess"]["diameter_mm"] <= screw["head_diameter_mm"]:
        errors.append("front screw-head recess has no diametral clearance")
    if mechanical["front_head_recess"]["depth_mm"] < screw["head_height_mm"]:
        errors.append("front screw head is not recessed")

    pilot = mechanical["pilot_shoulder"]
    calculated_pilot_clearance = (
        mechanical["pcb_hole_diameter_mm"]
        - (pilot["diameter_nominal_mm"] + pilot["diameter_tolerance_mm"])
    )
    if calculated_pilot_clearance < pilot["minimum_diametral_clearance_mm"]:
        errors.append("pilot-to-PCB-hole minimum clearance is too small")

    nut_recess = mechanical["rear_captive_nut_recess"]
    free_depth_min = float(nut_recess["depth_mm"]) - nut_min
    tip_clearance_min = free_depth_min - thread_beyond_nut_max
    if tip_clearance_min < float(nut_recess["minimum_tip_clearance_to_outer_surface_mm"]):
        errors.append("screw tip can reach the rear exterior")

    placement_axes = {
        tuple(row["centre_mm"])
        for board in placement["boards"]
        for row in board["mechanical"]
    }
    contract_axes = {tuple(row) for row in contract["coordinate_system"]["mounting_axes_mm"]}
    if placement_axes != contract_axes:
        errors.append("mechanical axes differ from the two native H6 PCB files")
    if len(contract_axes) != 4:
        errors.append("exactly four distinct mounting axes are required")

    capture = mechanical["edge_capture"]
    if capture["segments_per_board"] != 4 or len(capture["y_segments_mm"]) != 2:
        errors.append("each PCB must retain four independent edge-capture segments")
    if contract["assembly"]["m1_structural_role"] != "none":
        errors.append("M1 must have no structural role")
    if not contract["assembly"]["parallel_mating_fixture_required"]:
        errors.append("parallel M1 mating fixture must remain mandatory")

    return {
        "schema_version": 1,
        "artifact": "H6-R2 mechanical stack audit",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "source_hashes": {
            str(CONTRACT.relative_to(ROOT)): sha256(CONTRACT),
            str(PLACEMENT.relative_to(ROOT)): sha256(PLACEMENT),
        },
        "stack": {
            "members": members,
            "under_head_to_nut_nominal_mm": round(nominal, 3),
            "under_head_to_nut_minimum_mm": round(minimum, 3),
            "under_head_to_nut_maximum_mm": round(maximum, 3),
            "thread_available_at_nut_nominal_mm": round(remaining_nominal, 3),
            "thread_available_at_nut_minimum_mm": round(remaining_minimum, 3),
            "thread_available_at_nut_maximum_mm": round(remaining_maximum, 3),
            "thread_beyond_nut_minimum_mm": round(thread_beyond_nut_min, 3),
            "thread_beyond_nut_maximum_mm": round(thread_beyond_nut_max, 3),
            "minimum_tip_clearance_to_outer_surface_mm": round(tip_clearance_min, 3),
        },
        "geometry": {
            "mounting_axis_count": len(contract_axes),
            "mounting_axes_match_native_pcbs": placement_axes == contract_axes,
            "bearing_annulus_inside_8mm_keepout": mechanical["bearing_annulus_outside_diameter_mm"] <= 8.0,
            "calculated_minimum_pilot_diametral_clearance_mm": round(calculated_pilot_clearance, 3),
            "capture_segments_per_board": capture["segments_per_board"],
            "m1_structural_role": contract["assembly"]["m1_structural_role"],
        },
        "selected_hardware": {
            key: value["mpn"] for key, value in contract["selected_hardware"].items()
        },
        "errors": errors,
    }


def render(contract: dict, audit: dict) -> str:
    esc = html.escape
    stack = audit["stack"]
    hardware = contract["selected_hardware"]

    def text(x: float, y: float, value: str, size: float = 15, weight: str = "normal", anchor: str = "start", colour: str = "#172033") -> str:
        return f'<text x="{x}" y="{y}" font-family="Inter,Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{esc(value)}</text>'

    z0 = 285
    scale = 16
    layers = [
        ("front bearing floor", 1.4, "#f4d06f"),
        ("UI PCB", 1.6, "#2563eb"),
        ("Ettinger stop", 11.0, "#dbeafe"),
        ("RF PCB", 1.6, "#2563eb"),
        ("rear bearing floor", 1.4, "#f4d06f"),
    ]
    x = 180
    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1460" height="960" viewBox="0 0 1460 960" data-marker="H6.0.1-R1" data-view="mechanical-stack">',
        '<rect width="1460" height="960" fill="#ffffff"/>',
        text(70, 62, "Leshy2 · H6.0.1 local mechanical stack", 32, "700"),
        text(70, 96, "20-mm nylon screw · captive nut · four exact 11-mm stops · M1 carries no enclosure load", 17, "500", colour="#526076"),
        text(70, 145, "SECTION THROUGH ONE OF FOUR IDENTICAL CORNER AXES", 15, "700", colour="#1d4ed8"),
        text(420, 182, f"clamped path {stack['under_head_to_nut_nominal_mm']:.1f} mm nominal", 15, "700", "middle"),
        text(420, 206, f"worst range {stack['under_head_to_nut_minimum_mm']:.2f}…{stack['under_head_to_nut_maximum_mm']:.2f} mm", 13, "500", "middle", "#526076"),
    ]
    parts.append(f'<line x1="120" y1="{z0}" x2="760" y2="{z0}" stroke="#cbd5e1" stroke-width="1"/>')
    for index, (label, thickness, colour) in enumerate(layers, start=1):
        width = thickness * scale
        parts.append(f'<rect x="{x:.1f}" y="{z0-42}" width="{width:.1f}" height="84" fill="{colour}" stroke="#334155" stroke-width="1.5"/>')
        parts.append(text(x + width / 2, z0 + 6, str(index), 14, "700", "middle"))
        x += width
    parts.extend([
        f'<line x1="{180-32}" y1="{z0}" x2="{x+70}" y2="{z0}" stroke="#7c3aed" stroke-width="8" stroke-linecap="round"/>',
        f'<circle cx="{180-32}" cy="{z0}" r="17" fill="#ede9fe" stroke="#7c3aed" stroke-width="3"/>',
        f'<polygon points="{x+5},{z0-24} {x+39},{z0-24} {x+55},{z0} {x+39},{z0+24} {x+5},{z0+24} {x-11},{z0}" fill="#ede9fe" stroke="#7c3aed" stroke-width="3"/>',
        text(148, z0 - 62, hardware["screw"]["mpn"], 13, "700", "middle", "#6d28d9"),
        text(x + 22, z0 - 62, hardware["nut"]["mpn"], 13, "700", "middle", "#6d28d9"),
        text(100, 366, "1  front bearing floor · 1.4 mm", 12.5, "600"),
        text(360, 366, "2  UI PCB · 1.6 mm", 12.5, "600"),
        text(575, 366, "3  Ettinger stop · 11.0 mm", 12.5, "600"),
        text(865, 366, "4  RF PCB · 1.6 mm", 12.5, "600"),
        text(1080, 366, "5  rear bearing floor · 1.4 mm", 12.5, "600"),
    ])

    box_y = 420
    cards = [
        (55, "FULL NUT ENGAGEMENT", f"min available thread {stack['thread_available_at_nut_minimum_mm']:.2f} mm", f"min tail {stack['thread_beyond_nut_minimum_mm']:.2f} mm", "#ecfdf5", "#059669"),
        (395, "BURIED TIP", f"rear tip clearance {stack['minimum_tip_clearance_to_outer_surface_mm']:.2f} mm", "no finger contact", "#eff6ff", "#2563eb"),
        (735, "INDEPENDENT CAPTURE", "4 pilot shoulders + 4 lips / PCB", "one loose screw does not load M1", "#fff7ed", "#ea580c"),
        (1075, "SERVICEABLE", "snap-retained nylon hex nut", "0.05 N·m diagonal seating", "#f5f3ff", "#7c3aed"),
    ]
    for cx, title, line1, line2, fill, stroke in cards:
        parts.append(f'<rect x="{cx}" y="{box_y}" width="300" height="132" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        parts.append(text(cx + 150, box_y + 34, title, 14, "700", "middle", stroke))
        parts.append(text(cx + 150, box_y + 72, line1, 13, "600", "middle"))
        parts.append(text(cx + 150, box_y + 100, line2, 12.5, "500", "middle", "#526076"))

    parts.extend([
        text(70, 615, "WHAT HOLDS WHAT", 15, "700", colour="#1d4ed8"),
        text(90, 660, "Clamp / Z", 15, "700", colour="#7c3aed"),
        text(250, 660, "screw → bearing floors → PCBs → 11-mm stops → nut", 15),
        text(90, 700, "Shear / X-Y", 15, "700", colour="#ea580c"),
        text(250, 700, "four 2.45-mm shell pilots inside the existing 2.70-mm PCB holes", 15),
        text(90, 740, "Separation", 15, "700", colour="#059669"),
        text(250, 740, "four edge-lip segments retain each PCB independently", 15),
        text(90, 780, "M1", 15, "700", colour="#dc2626"),
        text(250, 780, "electrical mating and alignment only · never used to pull the boards together", 15),
        text(70, 865, "H6.0.1 remains open only for the five microcoax service loops and their enclosure/inspection clearances.", 15, "600", colour="#526076"),
        text(70, 908, f"audit: {audit['status']} · four axes match both native PCBs · no fabrication or purchase authorized", 14, "700", colour="#166534" if audit["status"] == "pass" else "#b91c1c"),
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed outputs differ")
    args = parser.parse_args()
    contract = load(CONTRACT)
    placement = load(PLACEMENT)
    audit = evaluate(contract, placement)
    audit_text = json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    svg_text = render(contract, audit)
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
        "H6-R2 mechanical stack "
        f"{audit['status']}: {audit['geometry']['mounting_axis_count']} axes; "
        f"{audit['stack']['thread_available_at_nut_minimum_mm']:.2f} mm minimum nut thread; "
        f"{audit['stack']['minimum_tip_clearance_to_outer_surface_mm']:.2f} mm tip clearance"
    )
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
