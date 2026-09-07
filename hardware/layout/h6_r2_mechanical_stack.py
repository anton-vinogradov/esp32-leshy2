#!/usr/bin/env python3
"""Audit and render the local H6 R2 enclosure/fastener stack."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
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


def evaluate_mounting_axes(contract: dict, placement: dict) -> dict:
    """Require all four axes on EACH PCB in the assembled front-view frame.

    Native UI X is world X. Native RF X is viewed from the rear exterior and
    maps to width-X when the two B sides face one another. A union of native
    axes cannot establish this: the other PCB would hide a missing hole.
    These are placement-audit observations; the native placement-signature
    check remains responsible for binding that report to the actual boards.
    """
    errors = []
    projects = ("LESHY2-UI-R2", "LESHY2-RF-R2")
    width = contract["coordinate_system"]["board_outline_mm"][0]

    def point(value):
        if (not isinstance(value, (list, tuple)) or len(value) != 2
                or any(isinstance(v, bool) or not isinstance(v, (int, float))
                       or not math.isfinite(v) for v in value)):
            return None
        return tuple(value)

    expected_rows = contract["coordinate_system"].get("mounting_axes_mm", [])
    expected = [point(row) for row in expected_rows]
    valid_expected = (len(expected) == 4 and None not in expected
                      and len(set(expected)) == 4)
    if not valid_expected:
        errors.append("exactly four finite distinct assembly mounting axes are required")
    valid_width = (not isinstance(width, bool) and isinstance(width, (int, float))
                   and math.isfinite(width) and width > 0)
    if not valid_width:
        errors.append("assembly board width must be finite and positive")

    boards = placement.get("boards", [])
    if len(boards) != 2 or sorted(b.get("project", "") for b in boards) != sorted(projects):
        errors.append("mounting axes require exactly one UI and one RF placement report")
    results = []
    for project in projects:
        found = [b for b in boards if b.get("project") == project]
        rows = found[0].get("mechanical", []) if len(found) == 1 else []
        ids = [row.get("id") for row in rows]
        native = [point(row.get("centre_mm")) for row in rows]
        valid_native = (len(rows) == 4 and set(ids) == {"MH1", "MH2", "MH3", "MH4"}
                        and None not in native and len(set(native)) == 4)
        world = [
            (width - xy[0], xy[1]) if project == "LESHY2-RF-R2" else xy
            for xy in native
        ] if valid_native and valid_width else []
        matches = bool(valid_expected and valid_native and valid_width
                       and set(world) == set(expected))
        if not matches:
            errors.append(f"{project}: four unique mounting holes do not match the assembly axes")
        results.append({
            "project": project,
            "native_to_assembly": "xw=width-x, yw=y" if project == "LESHY2-RF-R2" else "xw=x, yw=y",
            "hole_count": len(rows),
            "world_axes_mm": [list(xy) for xy in sorted(world)],
            "matches_assembly_axes": matches,
        })
    return {"status": "fail" if errors else "pass", "boards": results, "errors": errors}


def evaluate_connector_fit(contract: dict) -> dict:
    fit = contract["antenna_connector_fit"]
    slot_nominal, slot_minimum, slot_maximum = bounds(fit["slot_gap_mm"])
    required = float(fit["minimum_required_assembly_clearance_mm"])
    rows = []
    for project, member in fit["pcb_stack_members"].items():
        pcb_nominal, pcb_minimum, pcb_maximum = bounds(contract["tolerance_stack"][member])
        minimum_clearance = round(slot_minimum - pcb_maximum, 9)
        rows.append({
            "project": project,
            "pcb_stack_member": member,
            "pcb_thickness_nominal_mm": pcb_nominal,
            "pcb_thickness_range_mm": [round(pcb_minimum, 3), round(pcb_maximum, 3)],
            "assembly_clearance_nominal_mm": round(slot_nominal - pcb_nominal, 3),
            "assembly_clearance_minimum_mm": round(minimum_clearance, 3),
            "assembly_clearance_maximum_mm": round(slot_maximum - pcb_minimum, 3),
            "worst_case_interference_mm": round(max(0.0, -minimum_clearance), 3),
            "all_declared_corners_fit": minimum_clearance >= required,
        })
    unresolved = [row["project"] for row in rows if not row["all_declared_corners_fit"]]
    return {
        "status": "requires_confirmation" if unresolved else "pass",
        "checked_on": fit["checked_on"],
        "scope": "undeformed SMA slot versus finished PCB thickness; no prong flexibility assumed",
        "mpns": fit["mpns"],
        "slot_gap_nominal_mm": slot_nominal,
        "slot_gap_range_mm": [round(slot_minimum, 3), round(slot_maximum, 3)],
        "minimum_required_assembly_clearance_mm": required,
        "rows": rows,
        "sources": fit["sources"],
        "release_gate": {
            **fit["release_gate"],
            "status": "open" if unresolved else "closed_by_tolerance_geometry",
            "blocks_production_release": bool(unresolved),
            "unresolved_projects": unresolved,
            "routing_may_continue": True,
        },
    }


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

    mounting = evaluate_mounting_axes(contract, placement)
    errors.extend(mounting["errors"])
    contract_axes = {tuple(row) for row in contract["coordinate_system"]["mounting_axes_mm"]}

    capture = mechanical["edge_capture"]
    if capture["segments_per_board"] != 4 or len(capture["y_segments_mm"]) != 2:
        errors.append("each PCB must retain four independent edge-capture segments")
    if contract["assembly"]["m1_structural_role"] != "none":
        errors.append("M1 must have no structural role")
    if not contract["assembly"]["parallel_mating_fixture_required"]:
        errors.append("parallel M1 mating fixture must remain mandatory")

    thermal = contract["battery_thermal_contacts"]
    rf_board = next(
        row for row in placement["boards"] if row["project"] == "LESHY2-RF-R2"
    )
    placed = {row["instance"]: row for row in rf_board["placements"]}
    holder = placed[thermal["holder_instance"]]
    holder_x, holder_y = holder["footprint_anchor_mm"]
    half_spacing = float(thermal["holder_cell_axis_spacing_mm"]) / 2
    expected_centres = [
        [round(holder_x - half_spacing, 3), round(holder_y, 3)],
        [round(holder_x + half_spacing, 3), round(holder_y, 3)],
    ]
    actual_centres = []
    contact_beds_contain_ntcs = True
    gap_pad = contract["selected_hardware"]["cell_ntc_gap_pad"]
    for instance, expected in zip(thermal["ntc_instances_by_cell"], expected_centres):
        row = placed[instance]
        actual = [round(value, 3) for value in row["courtyard_centre_mm"]]
        actual_centres.append(actual)
        if actual != expected:
            errors.append(f"{instance} is not centred below its holder cell axis")
        if row["side"] != thermal["required_side"]:
            errors.append(f"{instance} is not on the holder-facing PCB side")
        bbox = row["courtyard_bbox_mm"]
        if (
            bbox["x"][1] - bbox["x"][0] > float(gap_pad["width_mm"])
            or bbox["y"][1] - bbox["y"][0] > float(gap_pad["length_mm"])
        ):
            contact_beds_contain_ntcs = False
            errors.append(f"{instance} courtyard does not fit below its 5x5-mm contact pad")
    accepted = {
        (row["instance"], row["owner"])
        for row in rf_board["accepted_same_face_overlaps"]
    }
    expected_overlaps = {
        (instance, thermal["holder_instance"])
        for instance in thermal["ntc_instances_by_cell"]
    }
    if not expected_overlaps.issubset(accepted):
        errors.append("direct-cell NTCs are not explicitly nested in the holder windows")
    nominal_compression = 100 * (
        float(thermal["ntc_maximum_height_mm"])
        + float(gap_pad["thickness_nominal_mm"])
        - float(thermal["holder_cell_floor_nominal_above_pcb_mm"])
    ) / float(gap_pad["thickness_nominal_mm"])
    if not (
        float(thermal["nominal_pad_compression_minimum_percent"])
        <= nominal_compression
        <= float(thermal["nominal_pad_compression_maximum_percent"])
    ):
        errors.append("nominal cell-to-NTC pad compression is outside its design window")

    return {
        "schema_version": 1,
        "artifact": "H6-R2 mechanical stack audit",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "status_scope": "fasteners, enclosure capture and direct cell thermal contacts; connector fit is reported separately",
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
            "mounting_axes_match_native_pcbs": mounting["status"] == "pass",
            "mounting_axes_by_board": mounting["boards"],
            "mounting_axis_scope": "each native placement report transformed to assembly coordinates; current PCB binding requires the separate native placement-signature check",
            "bearing_annulus_inside_8mm_keepout": mechanical["bearing_annulus_outside_diameter_mm"] <= 8.0,
            "calculated_minimum_pilot_diametral_clearance_mm": round(calculated_pilot_clearance, 3),
            "capture_segments_per_board": capture["segments_per_board"],
            "m1_structural_role": contract["assembly"]["m1_structural_role"],
        },
        "selected_hardware": {
            key: value["mpn"] for key, value in contract["selected_hardware"].items()
        },
        "battery_thermal_contacts": {
            "holder_instance": thermal["holder_instance"],
            "ntc_instances_by_cell": thermal["ntc_instances_by_cell"],
            "required_side": thermal["required_side"],
            "expected_cell_axis_centres_mm": expected_centres,
            "actual_ntc_centres_mm": actual_centres,
            "contact_beds_contain_ntc_courtyards": contact_beds_contain_ntcs,
            "exact_gap_pad_mpn": gap_pad["mpn"],
            "nominal_gap_pad_compression_percent": round(nominal_compression, 1),
            "accepted_holder_window_overlaps": len(expected_overlaps & accepted),
            "electrically_insulating_contact": True,
        },
        "connector_fit": evaluate_connector_fit(contract),
        "errors": errors,
    }


def render(contract: dict, audit: dict) -> str:
    esc = html.escape
    stack = audit["stack"]
    hardware = contract["selected_hardware"]
    fit = audit["connector_fit"]
    minimum_fit = min(row["assembly_clearance_minimum_mm"] for row in fit["rows"])
    fit_colour = "#b45309" if fit["release_gate"]["blocks_production_release"] else "#166534"

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
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1460" height="1310" viewBox="0 0 1460 1310" data-marker="{esc(contract["marker"])}" data-view="mechanical-stack">',
        '<rect width="1460" height="1310" fill="#ffffff"/>',
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
        text(70, 835, "DIRECT CELL TEMPERATURE · TWO IDENTICAL CONTACTS", 15, "700", colour="#1d4ed8"),
        '<rect x="90" y="957" width="500" height="24" fill="#2563eb" stroke="#1e3a8a" stroke-width="2"/>',
        text(340, 975, "RF PCB · HOLDER SIDE", 12, "700", "middle", "#ffffff"),
        '<rect x="300" y="936" width="48" height="21" rx="3" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>',
        text(324, 951, "NTC", 11, "700", "middle", "#991b1b"),
        '<rect x="287" y="879" width="74" height="57" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2.5"/>',
        text(324, 904, "5 × 5", 12, "700", "middle", "#92400e"),
        text(324, 922, "× 3 mm", 12, "700", "middle", "#92400e"),
        '<rect x="218" y="840" width="212" height="39" rx="19" fill="#e2e8f0" stroke="#475569" stroke-width="2.5"/>',
        text(324, 866, "18650 CELL", 13, "700", "middle"),
        text(660, 872, "BT1 open channel", 14, "700", colour="#334155"),
        text(660, 902, "one board-fitted 0603 NTC below each cell axis", 14),
        text(660, 932, "TG-A3500-5-5-3.0: insulating, tacky, 3.5 W/mK", 14),
        text(660, 962, f"nominal compression {audit['battery_thermal_contacts']['nominal_gap_pad_compression_percent']:.1f}% · cells installed last", 14),
        '<rect x="70" y="1020" width="1310" height="164" rx="14" fill="#fffbeb" stroke="#d97706" stroke-width="2"/>',
        text(95, 1054, f"SMA FIT: {fit['status']} · ПРОВЕРКА ПОСАДКИ SMA", 17, "700", colour=fit_colour),
        text(95, 1088, f"slot 1.75 ± 0.10 mm · both PCBs 1.60 ± 0.16 mm · worst clearance {minimum_fit:.2f} mm", 16, "600", colour=fit_colour),
        text(95, 1120, "Negative clearance means possible interference; confirm finished thickness / permitted fit before production release.", 15),
        text(95, 1152, "Допуски допускают натяг: до выпуска подтвердить конечную толщину PCB или допустимую посадку у поставщика.", 15),
        text(70, 1225, "H6.0.3 routing continues; SMA fit remains a separate production-release gate.", 15, "600", colour="#526076"),
        text(70, 1268, f"fastener / cell-contact audit: {audit['status']} · no fabrication or purchase authorized", 14, "700", colour="#166534" if audit["status"] == "pass" else "#b91c1c"),
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
        f"{audit['battery_thermal_contacts']['accepted_holder_window_overlaps']} direct cell contacts; "
        f"{audit['stack']['thread_available_at_nut_minimum_mm']:.2f} mm minimum nut thread; "
        f"{audit['stack']['minimum_tip_clearance_to_outer_surface_mm']:.2f} mm tip clearance; "
        f"SMA fit {audit['connector_fit']['status']}"
    )
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
