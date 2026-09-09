#!/usr/bin/env python3
"""Read-only native user-label contract check and conservative geometry screening.

Run with KiCad's Python.  Bounding-box candidates are NOT native DRC violations:
letters contain empty space and courtyards are assembly reservations, not bodies.
This audit deliberately cannot certify connector access or production readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile

from h6_r2_user_silkscreen import ANTENNA_INTERFACES, antenna_signal_findings, labels
from h6_r2_kicad_net_bindings import source_paths as net_binding_source_paths


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
LEDGER = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NET_BINDINGS = ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json"
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-user-silkscreen-audit.json"
POSITION_TOLERANCE_MM = 0.01
DIMENSION_TOLERANCE_MM = 0.001
MIN_FONT_MM = 1.0
MIN_STROKE_MM = 0.15
MIN_MASK_GAP_MM = 0.15
SILK_LAYERS = {"F.Silkscreen", "B.Silkscreen"}
SPEAKER_BODY = ROOT / "hardware/layout/h6-r2-speaker-body.json"
B3S_LIBRARY = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty/B3S-1100P.kicad_mod"
B3S_LIBRARY_SHA256 = "95a5411908cb206f5f541cbd40a33a641902bad132892084c85267d6decef989"
B3S_REVIEW = ROOT / "hardware/layout/h6-r2-b3s-actuator-datum-review.json"
B3S_PRIMARY = "https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf"
B3S_BODY_TOLERANCE_MM = 0.3  # Primary p2 unspecified dimensions; conservative per-edge allowance.
MIC_LIBRARY = ROOT / "hardware/ecad/libraries/Leshy2.pretty/CMEJ-0413-42-SMT-TR.kicad_mod"
MIC_LIBRARY_SHA256 = "039257c90aa952b1e74608cb510cf852cb93eeba0b7dea0b98d0864a2b085817"
MIC_PRIMARY = "https://www.sameskydevices.com/product/resource/masterpdf/cmej-0413-42-smt-tr.pdf"
MIC_MAX_BODY_RADIUS_MM = 2.1  # Rev1.04 p2: body diameter4.0 +/-0.2, not Fab pen width.


def geometry_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def obstacle_witness(obstacle):
    return {key: value for key, value in obstacle.items()
            if key not in {"native_text_clearances", "reviewed_body"}}


def clearance_witness(text, obstacle):
    return geometry_digest([text, obstacle_witness(obstacle)])


def checked_native_clearance(text, obstacle, method):
    proof = obstacle.get("native_text_clearances", {}).get(text["id"], {})
    if (proof.get("status") != "measured" or proof.get("method") != method
            or proof.get("inputs_sha256") != clearance_witness(text, obstacle)):
        return None
    lower, upper = proof.get("gap_lower_mm"), proof.get("gap_upper_mm")
    if (isinstance(lower, bool) or isinstance(upper, bool)
            or not isinstance(lower, (int, float)) or not isinstance(upper, (int, float))
            or not math.isfinite(lower) or not math.isfinite(upper)
            or lower < 0 or not 0 <= upper - lower <= 0.000002):
        return None
    return proof


def checked_mask_clearance(text, obstacle):
    return checked_native_clearance(text, obstacle, "native_stroke_shape_to_pad_mask")


def checked_circle_clearance(text, obstacle):
    body = obstacle.get("reviewed_circle_body", {})
    if (body.get("library_sha256") != MIC_LIBRARY_SHA256 or body.get("primary_url") != MIC_PRIMARY
            or body.get("native_geometry_matches_library") is not True
            or body.get("radius_max_mm") != MIC_MAX_BODY_RADIUS_MM):
        return None
    return checked_native_clearance(text, obstacle, "native_stroke_shape_to_maximum_body_circle")


def reviewed_body_clearance(text, obstacle):
    proof = obstacle.get("reviewed_body", {})
    if (proof.get("library_sha256") != B3S_LIBRARY_SHA256
            or proof.get("primary_url") != B3S_PRIMARY
            or proof.get("native_geometry_matches_library") is not True
            or proof.get("inputs_sha256") != geometry_digest(obstacle_witness(obstacle))
            or not obstacle.get("fab_graphics_bbox_mm")):
        return None
    # Fab includes its own line width. Add the entire +/-0.3 dimensional
    # tolerance to every edge rather than assuming symmetric manufacturing error.
    fab = obstacle["fab_graphics_bbox_mm"]
    envelope = {axis: [fab[axis][0] - B3S_BODY_TOLERANCE_MM,
                       fab[axis][1] + B3S_BODY_TOLERANCE_MM] for axis in ("x", "y")}
    gap = bbox_gap(text["bbox_mm"], envelope)
    return gap if gap >= MIN_MASK_GAP_MM else None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def overlaps(first, second):
    return all(first[axis][0] < second[axis][1] and
               second[axis][0] < first[axis][1] for axis in ("x", "y"))


def bbox_gap(first, second):
    return math.hypot(*(max(first[axis][0] - second[axis][1],
                           second[axis][0] - first[axis][1], 0.0) for axis in ("x", "y")))


def within_outline(box, width, height, radius=0.0):
    """Rectangle envelope against the contracted rounded outer board outline."""
    for x in box["x"]:
        for y in box["y"]:
            if not (0 <= x <= width and 0 <= y <= height):
                return False
            cx, cy = min(max(x, radius), width - radius), min(max(y, radius), height - radius)
            if math.hypot(x - cx, y - cy) > radius + 1e-9:
                return False
    return True


def obstacle_on_layer(obstacle, layer):
    """Explicit native side; legacy front fixtures stay front-only."""
    if "silk_layer" in obstacle:
        return obstacle["silk_layer"] == layer
    kind = obstacle["kind"]
    if kind.startswith("front_") or kind in {"display_panel_bbox", "mask_graphic_bbox"}:
        return layer == "F.Silkscreen"
    if kind.startswith("back_"):
        return layer == "B.Silkscreen"
    if kind == "via_drill_bbox" and "front_tented" in obstacle:
        return layer == "F.Silkscreen"
    return True  # Through-drill fixtures apply to both exposed board faces.


def cutout_obstacles(project, contract):
    """Conservative through-cut reservations, including the required ink gap.

    The separate native placement/outline check binds these source cutouts to
    Edge.Cuts. Rounded ends are not reclaimed as printable area here.
    """
    result = []
    for name in ("display_slot", "microsd_recess"):
        spec = contract.get("mechanical", {}).get(name)
        if spec is None or spec.get("board") != project:
            continue
        box = spec["bbox_mm"]
        if any(len(box[axis]) != 2 or
               any(type(v) not in (int, float) or not math.isfinite(v) for v in box[axis]) or
               box[axis][0] >= box[axis][1] for axis in ("x", "y")):
            raise ValueError("Invalid through-cut reservation: " + name)
        result.append({"kind": "through_cutout_bbox", "feature": name,
                       "required_ink_gap_mm": MIN_MASK_GAP_MM,
                       "source_bbox_mm": box,
                       "bbox_mm": {axis: [box[axis][0] - MIN_MASK_GAP_MM,
                                          box[axis][1] + MIN_MASK_GAP_MM]
                                   for axis in ("x", "y")}})
    return result


def required_label_findings(required, actual):
    """A wrong layer/pose/text is an error, not a missing-label suppression."""
    findings, matched = [], []
    used = set()
    for expected in required:
        def distance(row):
            return math.dist(expected["at_mm"], row["at_mm"])
        at_pose = [n for n, row in enumerate(actual) if distance(row) <= POSITION_TOLERANCE_MM]
        exact = [n for n in at_pose if actual[n]["text"] == expected["text"]
                 and actual[n]["layer"] == expected["layer"]]
        if len(exact) > 1:
            findings.append({"kind": "duplicate_required_label", "expected": expected,
                             "actual_ids": [actual[n]["id"] for n in exact]})
        choices = exact or at_pose or [n for n, row in enumerate(actual) if row["text"] == expected["text"]]
        choices = [n for n in choices if n not in used]
        if not choices:
            findings.append({"kind": "missing_required_label", "expected": expected})
            continue
        index = min(choices, key=lambda n: distance(actual[n]))
        used.add(index)
        row = actual[index]
        matched.append({"expected": expected, "actual_id": row["id"]})
        differences = []
        for key in ("text", "layer"):
            if row[key] != expected[key]:
                differences.append(key)
        if distance(row) > POSITION_TOLERANCE_MM:
            differences.append("at_mm")
        if any(abs(size - expected["size_mm"]) > DIMENSION_TOLERANCE_MM or
               size < MIN_FONT_MM - DIMENSION_TOLERANCE_MM for size in row["size_mm"]):
            differences.append("size_mm")
        if (abs(row["thickness_mm"] - expected["thickness_mm"]) > DIMENSION_TOLERANCE_MM or
                row["thickness_mm"] < MIN_STROKE_MM - DIMENSION_TOLERANCE_MM):
            differences.append("thickness_mm")
        angle, expected_angle = row["angle_deg"], expected.get("angle_deg", 0)
        if (any(type(v) not in (int, float) or not math.isfinite(v) for v in (angle, expected_angle))
                or abs((angle - expected_angle + 180) % 360 - 180) > 0.01):
            differences.append("angle_deg")
        if expected["layer"] not in SILK_LAYERS:
            differences.append("unsupported_required_layer")
        if row["mirrored"] != (expected["layer"] == "B.Silkscreen") or not row["visible"]:
            differences.append("mirror_or_visibility")
        if row["horizontal_justify"] != 0 or row["vertical_justify"] != 0:
            differences.append("justification")
        if differences:
            findings.append({"kind": "required_label_mismatch", "fields": differences,
                             "expected": expected, "actual": row})
    return findings, matched


def geometry_candidates(texts, obstacles, width, height, radius=0.0, assembly_texts=None, text_pair_clearances=None):
    candidates, exemptions = [], []
    assembly_texts = assembly_texts or {}
    text_pair_clearances = text_pair_clearances or {}
    visible = [row for row in texts if row["layer"] in SILK_LAYERS and row["visible"]]
    for row in visible:
        if not within_outline(row["bbox_mm"], width, height, radius):
            candidates.append({"kind": "outer_outline_bbox", "text": row})
        if min(row["size_mm"]) < MIN_FONT_MM - DIMENSION_TOLERANCE_MM or row["thickness_mm"] < MIN_STROKE_MM - DIMENSION_TOLERANCE_MM:
            candidates.append({"kind": "small_free_user_text", "text": row})
        for obstacle in obstacles:
            if not obstacle_on_layer(obstacle, row["layer"]):
                continue
            mask = obstacle["kind"] in {"front_pad_mask_bbox", "back_pad_mask_bbox"}
            courtyard = obstacle["kind"] in {"front_courtyard_bbox", "back_courtyard_bbox"}
            circle = courtyard and "reviewed_circle_body" in obstacle
            printed = obstacle["kind"] == "printed_silk_bbox"
            via_mask = obstacle["kind"] in {"front_via_mask_bbox", "back_via_mask_bbox"}
            if not overlaps(row["bbox_mm"], obstacle["bbox_mm"]) and not (
                    (mask or circle or printed or via_mask) and bbox_gap(row["bbox_mm"], obstacle["bbox_mm"]) <= MIN_MASK_GAP_MM):
                continue
            detail = {"kind": obstacle["kind"], "text": row, "obstacle": obstacle}
            if obstacle.get("fab_graphics_bbox_mm"):
                detail["fab_graphics_bbox_overlap"] = overlaps(row["bbox_mm"], obstacle["fab_graphics_bbox_mm"])
                detail["fab_graphics_bbox_gap_mm"] = bbox_gap(row["bbox_mm"], obstacle["fab_graphics_bbox_mm"])
            # Assembly visibility exceptions do not excuse solder-mask/drill or
            # outline crossings. Expose every exemption rather than erasing it.
            assembly_pose = assembly_texts.get(row["text"])
            holder_ntc_assembly = (obstacle["kind"] == "front_fab_body_bbox"
                                   and obstacle.get("reference") == "BT1"
                                   and row["text"] in {"NTC0 PAD", "NTC1 PAD"})
            if (row["layer"] == "F.Silkscreen" and assembly_pose is not None
                    and math.dist(row["at_mm"], assembly_pose) <= POSITION_TOLERANCE_MM
                    and (obstacle["kind"] in {"front_courtyard_bbox", "display_panel_bbox"}
                         or holder_ntc_assembly)):
                detail["exemption_reason"] = "Correctly positioned assembly marking intentionally hidden after final assembly"
                exemptions.append(detail)
            elif obstacle["kind"] == "via_drill_bbox" and obstacle.get("tented", obstacle.get("front_tented", False)):
                detail["exemption_reason"] = "Native tenting on this text side covers this via; it is not a solder-mask opening on this side"
                exemptions.append(detail)
            elif mask:
                proof = checked_mask_clearance(row, obstacle)
                detail["required_mask_gap_mm"] = MIN_MASK_GAP_MM
                if proof is not None:
                    detail["native_mask_gap_mm"] = [proof["gap_lower_mm"], proof["gap_upper_mm"]]
                if proof is not None and proof["gap_lower_mm"] >= MIN_MASK_GAP_MM:
                    detail["resolution_reason"] = "Actual native text strokes, including pen width, clear the actual pad mask by the required gap"
                    exemptions.append(detail)
                else:
                    detail["review_reason"] = "Native stroke-to-mask gap below minimum or unavailable/stale; retain conservative candidate"
                    candidates.append(detail)
            elif circle:
                proof = checked_circle_clearance(row, obstacle)
                detail["required_body_gap_mm"] = MIN_MASK_GAP_MM
                if proof is not None:
                    detail["native_maximum_body_gap_mm"] = [proof["gap_lower_mm"], proof["gap_upper_mm"]]
                if proof is not None and proof["gap_lower_mm"] >= MIN_MASK_GAP_MM:
                    detail["resolution_reason"] = "Actual native text strokes clear the primary maximum circular body; exact native/library geometry agrees. Pads and drills remain independently screened."
                    exemptions.append(detail)
                else:
                    detail["review_reason"] = "Maximum-body circle clearance below minimum or unavailable/stale; retain courtyard candidate"
                    candidates.append(detail)
            elif courtyard and reviewed_body_clearance(row, obstacle) is not None:
                detail["tolerance_expanded_body_gap_mm"] = reviewed_body_clearance(row, obstacle)
                detail["resolution_reason"] = "Exact reviewed B3S native/library geometry agrees; text clears the primary body plus dimensional tolerance, not merely the assembly courtyard. Pads and drills remain independently screened."
                exemptions.append(detail)
            elif printed or via_mask:
                method = "native_stroke_shape_to_printed_silk" if printed else "native_stroke_shape_to_via_mask"
                proof = checked_native_clearance(row, obstacle, method)
                if proof is not None and proof["gap_lower_mm"] >= MIN_MASK_GAP_MM:
                    detail["native_gap_mm"] = [proof["gap_lower_mm"], proof["gap_upper_mm"]]
                    detail["resolution_reason"] = "Actual native shapes on the same side clear by the required gap; empty glyph/outline space is not printed ink"
                    exemptions.append(detail)
                else:
                    candidates.append(detail)
            else:
                candidates.append(detail)
    for index, first in enumerate(visible):
        for second in visible[index + 1:]:
            if first["layer"] != second["layer"]:
                continue
            if bbox_gap(first["bbox_mm"], second["bbox_mm"]) <= MIN_MASK_GAP_MM:
                detail = {"kind": "user_text_bbox_overlap", "text": first, "other_text": second}
                pair = {"other_text": second, "native_text_clearances": {
                    first["id"]: text_pair_clearances.get(first["id"] + "|" + second["id"], {})}}
                proof = checked_native_clearance(first, pair, "native_stroke_shape_to_text_stroke")
                if proof is not None and proof["gap_lower_mm"] >= MIN_MASK_GAP_MM:
                    detail["native_text_gap_mm"] = [proof["gap_lower_mm"], proof["gap_upper_mm"]]
                    detail["resolution_reason"] = "Actual native strokes, including both pen widths, are separated by the required gap"
                    exemptions.append(detail)
                else:
                    candidates.append(detail)
    return candidates, exemptions


def audit_snapshot(snapshot, contract, canonical_to_kicad=None):
    project = snapshot["project"]
    errors = antenna_signal_findings(project, snapshot["placements"], contract,
                                     canonical_to_kicad or {})
    try:
        required = labels(project, snapshot["placements"], contract)
    except (KeyError, ValueError, OSError) as exc:
        errors.append({"kind": "required_label_binding_unavailable", "detail": str(exc)})
        required = []
    label_errors, matched = required_label_findings(required, snapshot["texts"])
    errors.extend(label_errors)
    rows = {row["instance"]: row for row in snapshot["placements"]}
    assembly_texts = {"DISPLAY · FPC ↑": [contract["board"]["width_mm"] / 2, 21.0]} if project == "LESHY2-UI-R2" else {
        f"NTC{index} PAD": [rows[instance]["courtyard_centre_mm"][0], rows[instance]["courtyard_centre_mm"][1] + 4.1]
        for index, instance in enumerate(("pack_ntc0", "pack_ntc1")) if instance in rows
    }
    candidates, exemptions = geometry_candidates(
        snapshot["texts"], snapshot["obstacles"], contract["board"]["width_mm"],
        contract["board"]["height_mm"], contract["board"]["corner_radius_mm"],
        assembly_texts, snapshot.get("native_text_pair_clearances"),
    )
    errors.extend(snapshot.get("extraction_errors", []))
    outline = snapshot.get("native_outline_bbox_mm")
    if outline is not None:
        expected_outline = {"x": [0.0, contract["board"]["width_mm"]], "y": [0.0, contract["board"]["height_mm"]]}
        # Native Edge.Cuts bounding boxes can include a 0.05-mm drawing stroke.
        if any(abs(outline[axis][n] - expected_outline[axis][n]) > 0.06
               for axis in ("x", "y") for n in (0, 1)):
            errors.append({"kind": "native_outline_envelope_mismatch", "actual": outline, "expected": expected_outline})
    return {
        "project": project, "status": "fail" if errors else "review_required" if candidates else "pass_scoped",
        "required_count": len(required), "matched_count": len(matched),
        "free_front_text_count": sum(row["layer"] == "F.Silkscreen" and row["visible"] for row in snapshot["texts"]),
        "free_back_text_count": sum(row["layer"] == "B.Silkscreen" and row["visible"] for row in snapshot["texts"]),
        "errors": errors, "geometry_candidates": candidates,
        "documented_geometry_exemptions": [row for row in exemptions if "exemption_reason" in row],
        "resolved_geometry_findings": [row for row in exemptions if "resolution_reason" in row],
        "required_bindings": matched,
    }


def native_stroke_mask_clearance(text, pad, pcbnew):
    """Exact default KiCad stroke font versus supported native pad shapes.

    Positive mask expansion is a Minkowski offset of these convex pad shapes.
    Unsupported fonts/shapes/negative expansions retain the bbox candidate.
    A 1-nm interval is conservative: only its lower bound may resolve a finding.
    """
    supported = {pcbnew.PAD_SHAPE_RECT, pcbnew.PAD_SHAPE_CIRCLE,
                 pcbnew.PAD_SHAPE_OVAL, pcbnew.PAD_SHAPE_ROUNDRECT}
    try:
        if text.GetLayer() not in {pcbnew.F_SilkS, pcbnew.B_SilkS}:
            return {"status": "unsupported", "reason": "Text is not on a native silk layer"}
        copper_layer, mask_layer = ((pcbnew.F_Cu, pcbnew.F_Mask) if text.GetLayer() == pcbnew.F_SilkS
                                     else (pcbnew.B_Cu, pcbnew.B_Mask))
        expansion = pad.GetSolderMaskExpansion(mask_layer)
        if (text.GetFont() is not None or pad.GetShape() not in supported or expansion < 0
                or not pad.IsOnLayer(copper_layer) or not pad.IsOnLayer(mask_layer)):
            return {"status": "unsupported", "reason": "Only native default stroke font and convex same-side pad shapes with nonnegative mask expansion are refined"}
        ink, copper = text.GetEffectiveTextShape(), pad.GetEffectiveShape(copper_layer)
        if ink is None or copper is None or ink.BBox().GetWidth() <= 0:
            return {"status": "unsupported", "reason": "Native effective shape unavailable or empty"}
        low, high = 0, pcbnew.FromMM(1)
        if ink.Collide(copper, expansion):
            low = high = 0
        else:
            while not ink.Collide(copper, high + expansion):
                high *= 2
                if high > pcbnew.FromMM(100):
                    return {"status": "unsupported", "reason": "No bounded native distance found"}
            while high - low > 1:
                mid = (low + high) // 2
                if ink.Collide(copper, mid + expansion):
                    high = mid
                else:
                    low = mid
        return {"status": "measured", "method": "native_stroke_shape_to_pad_mask",
                "gap_lower_mm": pcbnew.ToMM(low), "gap_upper_mm": pcbnew.ToMM(high)}
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return {"status": "unsupported", "reason": type(exc).__name__ + ": " + str(exc)}


def native_footprint_geometry(fp, pcbnew):
    """Reviewed same-side package geometry, independent of UUID/ref/net labels."""
    def point(value):
        # Imported decimal coordinates may differ by one native nm.
        return [round(pcbnew.ToMM(value.x), 5), round(pcbnew.ToMM(value.y), 5)]
    fab, court, mask = ((pcbnew.F_Fab, pcbnew.F_CrtYd, pcbnew.F_Mask) if fp.GetLayer() == pcbnew.F_Cu
                         else (pcbnew.B_Fab, pcbnew.B_CrtYd, pcbnew.B_Mask))
    graphics = [[int(g.GetShape()), int(g.GetLayer()), point(g.GetStart()), point(g.GetEnd()),
                 round(pcbnew.ToMM(g.GetWidth()), 5)] for g in fp.GraphicalItems()
                if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() in {fab, court}]
    pads = [[p.GetNumber(), point(p.GetPosition()), point(p.GetSize()), point(p.GetOffset()),
             point(p.GetDrillSize()), int(p.GetShape()), int(p.GetAttribute()),
             round(p.GetOrientationDegrees() % 360, 5), list(p.GetLayerSet().Seq()),
             p.GetSolderMaskExpansion(mask)] for p in fp.Pads()]
    return {"graphics": sorted(graphics), "pads": sorted(pads)}


def native_stroke_shape_clearance(text, shape, pcbnew, method, expansion=0):
    """One-nm conservative interval between filled native effective shapes."""
    try:
        if text.GetFont() is not None or expansion < 0:
            return {"status": "unsupported", "reason": "Only native default stroke font and nonnegative expansion are refined"}
        ink = text.GetEffectiveTextShape()
        if ink is None or shape is None or ink.BBox().GetWidth() <= 0:
            return {"status": "unsupported", "reason": "Native effective text shape unavailable or empty"}
        low, high = 0, pcbnew.FromMM(1)
        if ink.Collide(shape, expansion):
            low = high = 0
        else:
            while not ink.Collide(shape, high + expansion):
                high *= 2
                if high > pcbnew.FromMM(100):
                    return {"status": "unsupported", "reason": "No bounded native distance found"}
            while high - low > 1:
                mid = (low + high) // 2
                if ink.Collide(shape, mid + expansion):
                    high = mid
                else:
                    low = mid
        return {"status": "measured", "method": method,
                "gap_lower_mm": pcbnew.ToMM(low), "gap_upper_mm": pcbnew.ToMM(high)}
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return {"status": "unsupported", "reason": type(exc).__name__ + ": " + str(exc)}


def native_stroke_circle_clearance(text, centre_mm, radius_mm, pcbnew):
    """Filled maximum body, not its Fab outline or courtyard approximation."""
    body = pcbnew.SHAPE_CIRCLE(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in centre_mm)),
                              pcbnew.FromMM(radius_mm))
    return native_stroke_shape_clearance(text, body, pcbnew, "native_stroke_shape_to_maximum_body_circle")


def native_stroke_via_mask_clearance(text, via, pcbnew):
    """Actual exposed via annulus on the text side, never the other side's tent."""
    copper, mask = ((pcbnew.F_Cu, pcbnew.F_Mask) if text.GetLayer() == pcbnew.F_SilkS
                    else (pcbnew.B_Cu, pcbnew.B_Mask))
    try:
        if not via.IsOnLayer(copper) or via.IsTented(copper):
            return {"status": "unsupported", "reason": "No exposed via on this text side"}
        return native_stroke_shape_clearance(
            text, via.GetEffectiveShape(copper), pcbnew, "native_stroke_shape_to_via_mask",
            via.GetSolderMaskExpansion())
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return {"status": "unsupported", "reason": type(exc).__name__ + ": " + str(exc)}


def native_snapshot(board, project, ledger_rows, contract, pcbnew, root=ROOT):
    """Extract actual pad, drill, footprint and free-text geometry without mutation."""
    def box_mm(box):
        return {"x": [pcbnew.ToMM(box.GetLeft()), pcbnew.ToMM(box.GetRight())],
                "y": [pcbnew.ToMM(box.GetTop()), pcbnew.ToMM(box.GetBottom())]}
    def point_mm(point):
        return [pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)]
    def expanded(box, amount):
        return {axis: [box[axis][0] - amount, box[axis][1] + amount] for axis in ("x", "y")}
    texts, placements, obstacles, errors = [], [], [], []
    mask_objects, text_objects, printed_objects, via_objects = [], {}, [], []
    sides = ((pcbnew.F_Cu, pcbnew.F_Mask, "F.Silkscreen", "front"),
             (pcbnew.B_Cu, pcbnew.B_Mask, "B.Silkscreen", "back"))

    def add_printed_graphic(graphic, reference=None):
        if graphic.GetLayer() not in {pcbnew.F_SilkS, pcbnew.B_SilkS}:
            return
        if hasattr(graphic, "GetText") and not graphic.IsVisible():
            return  # Hidden native refs/values are not ink.
        obstacle = {"kind": "printed_silk_bbox", "native_id": graphic.m_Uuid.AsString(),
                    "reference": reference, "silk_layer": board.GetLayerName(graphic.GetLayer()),
                    "bbox_mm": box_mm(graphic.GetBoundingBox())}
        if hasattr(graphic, "GetText"):
            obstacle.update(text=graphic.GetText(), at_mm=point_mm(graphic.GetPosition()),
                            size_mm=point_mm(graphic.GetTextSize()),
                            thickness_mm=pcbnew.ToMM(graphic.GetTextThickness()),
                            angle_deg=graphic.GetTextAngleDegrees(), mirrored=graphic.IsMirrored(),
                            default_stroke_font=graphic.GetFont() is None)
        elif isinstance(graphic, pcbnew.PCB_SHAPE):
            obstacle.update(shape=int(graphic.GetShape()), start_mm=point_mm(graphic.GetStart()),
                            end_mm=point_mm(graphic.GetEnd()), width_mm=pcbnew.ToMM(graphic.GetWidth()))
        obstacles.append(obstacle)
        printed_objects.append((obstacle, graphic))

    def align_reference(reference_fp, native_fp):
        # Flip needs board context, but this reference is NOT registered with
        # board.Add(). Creating a second BOARD after LoadBoard invalidates some
        # KiCad 9 Python outline/settings state; borrowing the parent avoids
        # that lifetime trap without adding/removing any inspected object.
        reference_fp.SetParent(board)
        reference_fp.SetPosition(native_fp.GetPosition())
        if native_fp.GetLayer() == pcbnew.B_Cu:
            reference_fp.Flip(native_fp.GetPosition(), False)
        reference_fp.SetOrientationDegrees(native_fp.GetOrientationDegrees())
    library_path = root / B3S_LIBRARY.relative_to(ROOT)
    mic_library_path = root / MIC_LIBRARY.relative_to(ROOT)
    review_path = root / B3S_REVIEW.relative_to(ROOT)
    b3s_reviewed = False
    if library_path.is_file() and review_path.is_file() and sha256(library_path) == B3S_LIBRARY_SHA256:
        review = json.loads(review_path.read_text())
        b3s_reviewed = (review.get("evidence", {}).get("url") == B3S_PRIMARY
                       and review.get("evidence", {}).get("sha256") == "c6391ce552636acbb8a266c68a2f27f17a0f14f73bccbb4fae9aeaf36e0c289b"
                       and review.get("local_datums", {}).get("nominal_body_bounds_mm") == {"x": [-3, 3], "y": [-4.22, 2.38]})
    by_reference = {}
    for fp in board.GetFootprints():
        reference = fp.GetReference()
        if reference in by_reference:
            errors.append({"kind": "duplicate_native_reference", "reference": reference})
        by_reference[reference] = fp
        front = fp.GetLayer() == pcbnew.F_Cu
        layer = pcbnew.F_CrtYd if front else pcbnew.B_CrtYd
        silk_layer, prefix = ("F.Silkscreen", "front") if front else ("B.Silkscreen", "back")
        courtyard = fp.GetCourtyard(layer).BBox()
        fab = [box_mm(g.GetBoundingBox()) for g in fp.GraphicalItems()
               if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() == (pcbnew.F_Fab if front else pcbnew.B_Fab)]
        fab_bbox = ({axis: [min(b[axis][0] for b in fab), max(b[axis][1] for b in fab)] for axis in ("x", "y")}
                    if fab else None)
        if courtyard.GetWidth() > 0 and courtyard.GetHeight() > 0:
            obstacle = {"kind": prefix + "_courtyard_bbox", "silk_layer": silk_layer,
                        "reference": reference, "bbox_mm": box_mm(courtyard)}
            if fab_bbox:
                obstacle["fab_graphics_bbox_mm"] = fab_bbox
            fpid = str(fp.GetFPID().GetLibNickname()) + ":" + str(fp.GetFPID().GetLibItemName())
            if b3s_reviewed and fpid == "Leshy2_R2:B3S-1100P":
                reference_fp = pcbnew.FootprintLoad(str(library_path.parent), library_path.stem)
                align_reference(reference_fp, fp)
                actual_geometry = native_footprint_geometry(fp, pcbnew)
                expected_geometry = native_footprint_geometry(reference_fp, pcbnew)
                obstacle["native_geometry_sha256"] = geometry_digest(actual_geometry)
                if actual_geometry == expected_geometry:
                    obstacle["reviewed_body"] = {
                        "primary_url": B3S_PRIMARY, "section": "Full p2 With Ground Terminal, nominal body6.0x6.6 and +/-0.3-mm unspecified tolerance",
                        "library_sha256": B3S_LIBRARY_SHA256, "native_geometry_matches_library": True,
                        "inputs_sha256": geometry_digest(obstacle_witness(obstacle))}
            if (fpid == "Leshy2:CMEJ-0413-42-SMT-TR"
                    and fp.GetValue() == "Same Sky CMEJ-0413-42-SMT-TR"
                    and mic_library_path.is_file() and sha256(mic_library_path) == MIC_LIBRARY_SHA256):
                reference_fp = pcbnew.FootprintLoad(str(mic_library_path.parent), mic_library_path.stem)
                align_reference(reference_fp, fp)
                actual_geometry = native_footprint_geometry(fp, pcbnew)
                if actual_geometry == native_footprint_geometry(reference_fp, pcbnew):
                    obstacle["native_geometry_sha256"] = geometry_digest(actual_geometry)
                    obstacle["reviewed_circle_body"] = {
                        "primary_url": MIC_PRIMARY, "section": "Rev1.04 p2 mechanical drawing, diameter4.0 +/-0.2 mm",
                        "library_sha256": MIC_LIBRARY_SHA256, "native_geometry_matches_library": True,
                        "centre_mm": point_mm(fp.GetPosition()), "radius_max_mm": MIC_MAX_BODY_RADIUS_MM}
            obstacles.append(obstacle)
        elif fab_bbox:
            # Absence of a courtyard must not erase a present physical body
            # (current BT1 is one such footprint). This is a conservative Fab
            # envelope, not a newly manufacturer-qualified body drawing.
            obstacles.append({"kind": prefix + "_fab_body_bbox", "silk_layer": silk_layer,
                              "reference": reference, "bbox_mm": fab_bbox,
                              "reason": "No native courtyard; conservative same-side Fab graphics envelope"})
        for graphic in fp.GraphicalItems():
            if graphic.GetLayer() in {pcbnew.F_Mask, pcbnew.B_Mask}:
                obstacles.append({"kind": "mask_graphic_bbox", "reference": reference,
                                  "silk_layer": "F.Silkscreen" if graphic.GetLayer() == pcbnew.F_Mask else "B.Silkscreen",
                                  "bbox_mm": box_mm(graphic.GetBoundingBox())})
        printed_ids = set()
        for graphic in [fp.Reference(), fp.Value(), *fp.GraphicalItems()]:
            identity = graphic.m_Uuid.AsString()
            if identity not in printed_ids:
                add_printed_graphic(graphic, reference)
                printed_ids.add(identity)
        for pad in fp.Pads():
            name = reference + "." + pad.GetNumber()
            for copper_layer, mask_layer, silk_layer, prefix in sides:
                if not pad.IsOnLayer(mask_layer):
                    continue
                obstacle = {"kind": prefix + "_pad_mask_bbox", "silk_layer": silk_layer, "pad": name,
                            "native_pad_id": pad.m_Uuid.AsString(),
                            "shape": int(pad.GetShape()), "at_mm": point_mm(pad.GetPosition()),
                            "size_mm": point_mm(pad.GetSize()), "offset_mm": point_mm(pad.GetOffset()),
                            "rotation_deg": pad.GetOrientationDegrees(),
                            "roundrect_radius_mm": pcbnew.ToMM(pad.GetRoundRectCornerRadius()),
                            "mask_expansion_mm": pcbnew.ToMM(pad.GetSolderMaskExpansion(mask_layer)),
                            # Negative expansion is deliberately unsupported by
                            # refinement; its fallback must not shrink the box.
                            "bbox_mm": expanded(box_mm(pad.GetBoundingBox()), max(0.0, pcbnew.ToMM(pad.GetSolderMaskExpansion(mask_layer))))}
                obstacles.append(obstacle)
                mask_objects.append((obstacle, pad))
            drill = pad.GetDrillSize()
            if drill.x > 0 and drill.y > 0:
                # Rotated drill rectangle is conservative for circles/slots.
                x, y = point_mm(pad.GetPosition())
                a = math.radians(pad.GetOrientationDegrees())
                dx, dy = pcbnew.ToMM(drill.x) / 2, pcbnew.ToMM(drill.y) / 2
                rx, ry = abs(dx * math.cos(a)) + abs(dy * math.sin(a)), abs(dx * math.sin(a)) + abs(dy * math.cos(a))
                obstacles.append({"kind": "drill_bbox", "pad": name,
                                  "bbox_mm": {"x": [x-rx, x+rx], "y": [y-ry, y+ry]}})
    for row in ledger_rows:
        if row["project"] != project:
            continue
        fp = by_reference.get(row["reference"])
        if fp is None:
            errors.append({"kind": "missing_native_reference", "reference": row["reference"]})
            continue
        layer = pcbnew.F_CrtYd if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd
        courtyard = fp.GetCourtyard(layer).BBox()
        centre = point_mm(courtyard.GetCenter()) if courtyard.GetWidth() > 0 and courtyard.GetHeight() > 0 else point_mm(fp.GetPosition())
        placement = {"instance": row["instance"], "reference": row["reference"],
                     "courtyard_centre_mm": centre, "footprint_anchor_mm": point_mm(fp.GetPosition()),
                     "footprint": str(fp.GetFPID().GetLibNickname()) + ":" + str(fp.GetFPID().GetLibItemName()),
                     "side": "F.Cu" if fp.GetLayer() == pcbnew.F_Cu else "B.Cu",
                     "rotation_deg": fp.GetOrientationDegrees()}
        if row["instance"] in ANTENNA_INTERFACES:
            placement["signal_pad_nets"] = sorted(
                pad.GetNetname() for pad in fp.Pads() if pad.GetNumber() == "1")
        placements.append(placement)
    for graphic in board.GetDrawings():
        if isinstance(graphic, pcbnew.PCB_TEXT):
            text_objects[graphic.m_Uuid.AsString()] = graphic
            texts.append({"id": graphic.m_Uuid.AsString(), "text": graphic.GetText(),
                          "layer": board.GetLayerName(graphic.GetLayer()), "at_mm": point_mm(graphic.GetPosition()),
                          "size_mm": point_mm(graphic.GetTextSize()), "thickness_mm": pcbnew.ToMM(graphic.GetTextThickness()),
                          "angle_deg": graphic.GetTextAngleDegrees(), "mirrored": graphic.IsMirrored(), "visible": graphic.IsVisible(),
                          "horizontal_justify": int(graphic.GetHorizJustify()), "vertical_justify": int(graphic.GetVertJustify()),
                          "default_stroke_font": graphic.GetFont() is None,
                          "bold": graphic.IsBold(), "italic": graphic.IsItalic(),
                          "bbox_mm": box_mm(graphic.GetBoundingBox())})
        elif graphic.GetLayer() in {pcbnew.F_Mask, pcbnew.B_Mask}:
            obstacles.append({"kind": "mask_graphic_bbox",
                              "silk_layer": "F.Silkscreen" if graphic.GetLayer() == pcbnew.F_Mask else "B.Silkscreen",
                              "bbox_mm": box_mm(graphic.GetBoundingBox())})
        else:
            add_printed_graphic(graphic)
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA):
            continue
        x, y = point_mm(item.GetPosition())
        r = pcbnew.ToMM(item.GetDrillValue()) / 2
        for copper_layer, mask_layer, silk_layer, prefix in sides:
            if not item.IsOnLayer(copper_layer):
                continue
            obstacles.append({"kind": "via_drill_bbox", "via": item.m_Uuid.AsString(),
                              "silk_layer": silk_layer, "tented": item.IsTented(copper_layer),
                              "bbox_mm": {"x": [x-r, x+r], "y": [y-r, y+r]}})
            if not item.IsTented(copper_layer):
                obstacle = {"kind": prefix + "_via_mask_bbox", "via": item.m_Uuid.AsString(),
                            "silk_layer": silk_layer,
                            "mask_expansion_mm": pcbnew.ToMM(item.GetSolderMaskExpansion()),
                            "bbox_mm": expanded(box_mm(item.GetBoundingBox()), max(0.0, pcbnew.ToMM(item.GetSolderMaskExpansion())))}
                obstacles.append(obstacle)
                via_objects.append((obstacle, item))
    if project == "LESHY2-UI-R2":
        obstacles.append({"kind": "display_panel_bbox", "silk_layer": "F.Silkscreen",
                          "bbox_mm": contract["mechanical"]["display_bed"]["panel_bbox_mm"]})
    obstacles.extend(cutout_obstacles(project, contract))
    for row in texts:
        if row["layer"] not in SILK_LAYERS or not row["visible"]:
            continue
        for obstacle, pad in mask_objects:
            if obstacle_on_layer(obstacle, row["layer"]) and bbox_gap(row["bbox_mm"], obstacle["bbox_mm"]) <= MIN_MASK_GAP_MM:
                proof = native_stroke_mask_clearance(text_objects[row["id"]], pad, pcbnew)
                proof["inputs_sha256"] = clearance_witness(row, obstacle)
                obstacle.setdefault("native_text_clearances", {})[row["id"]] = proof
        for obstacle in obstacles:
            body = obstacle.get("reviewed_circle_body")
            if body and obstacle_on_layer(obstacle, row["layer"]) and bbox_gap(row["bbox_mm"], obstacle["bbox_mm"]) <= MIN_MASK_GAP_MM:
                proof = native_stroke_circle_clearance(text_objects[row["id"]], body["centre_mm"], body["radius_max_mm"], pcbnew)
                proof["inputs_sha256"] = clearance_witness(row, obstacle)
                obstacle.setdefault("native_text_clearances", {})[row["id"]] = proof
        for obstacle, graphic in printed_objects:
            if not obstacle_on_layer(obstacle, row["layer"]) or bbox_gap(row["bbox_mm"], obstacle["bbox_mm"]) > MIN_MASK_GAP_MM:
                continue
            try:
                if hasattr(graphic, "GetText"):
                    if graphic.GetFont() is not None:
                        continue
                    shape = graphic.GetEffectiveTextShape()
                else:
                    shape = graphic.GetEffectiveShape()
                proof = native_stroke_shape_clearance(text_objects[row["id"]], shape, pcbnew, "native_stroke_shape_to_printed_silk")
                proof["inputs_sha256"] = clearance_witness(row, obstacle)
                obstacle.setdefault("native_text_clearances", {})[row["id"]] = proof
            except (AttributeError, TypeError, RuntimeError, ValueError):
                pass  # Unsupported shape remains a conservative candidate.
        for obstacle, via in via_objects:
            if obstacle_on_layer(obstacle, row["layer"]) and bbox_gap(row["bbox_mm"], obstacle["bbox_mm"]) <= MIN_MASK_GAP_MM:
                proof = native_stroke_via_mask_clearance(text_objects[row["id"]], via, pcbnew)
                proof["inputs_sha256"] = clearance_witness(row, obstacle)
                obstacle.setdefault("native_text_clearances", {})[row["id"]] = proof
    text_pair_clearances = {}
    visible = [row for row in texts if row["layer"] in SILK_LAYERS and row["visible"]]
    for index, first in enumerate(visible):
        for second in visible[index + 1:]:
            if first["layer"] == second["layer"] and bbox_gap(first["bbox_mm"], second["bbox_mm"]) <= MIN_MASK_GAP_MM:
                other = text_objects[second["id"]]
                if other.GetFont() is not None:
                    continue
                proof = native_stroke_shape_clearance(text_objects[first["id"]], other.GetEffectiveTextShape(), pcbnew,
                                                      "native_stroke_shape_to_text_stroke")
                proof["inputs_sha256"] = clearance_witness(first, {"other_text": second})
                text_pair_clearances[first["id"] + "|" + second["id"]] = proof
    outline_bbox = box_mm(board.GetBoardEdgesBoundingBox())
    # The speaker verifier constructs a temporary BOARD. In KiCad Python this
    # changes global settings context used by a loaded board's outline query.
    # All ordinary native reads above must finish first; the verified speaker
    # reservation needs no further native refinement or reads after this call.
    speaker_spec = contract.get("mechanical", {}).get("speaker_body")
    if speaker_spec is not None:
        from h6_r2_speaker_fit import check_native_speaker_geometry
        try:
            speaker = check_native_speaker_geometry(board, project, pcbnew, speaker_spec)
            if speaker["status"] == "pass_scoped_native_registration":
                obstacles.append({"kind": "speaker_body_bbox", "reference": "speaker_assembly_body",
                                  "silk_layer": "B.Silkscreen", "bbox_mm": speaker["maximum_bbox_mm"]})
        except ValueError as exc:
            errors.append({"kind": "speaker_body_registration_mismatch", "detail": str(exc)})
    return {"project": project, "placements": placements, "texts": texts, "obstacles": obstacles,
            "native_text_pair_clearances": text_pair_clearances,
            "native_outline_bbox_mm": outline_bbox, "extraction_errors": errors}


def checked_net_bindings(root=ROOT):
    """Load current H2-to-KiCad authority; stale/missing source proof is fatal."""
    path = root / NET_BINDINGS.relative_to(ROOT)
    artifact = json.loads(path.read_text())
    if (artifact.get("schema_version") != 1 or artifact.get("status") != "pass"
            or artifact.get("artifact") != "H6-R2 exact KiCad hierarchical net bindings"
            or artifact.get("errors") != []):
        raise ValueError("KiCad net-binding authority is not a passing artifact")
    expected_sources = {str(source.relative_to(root)) for source in net_binding_source_paths(root)}
    sources = artifact.get("source_hashes", {})
    if set(sources) != expected_sources:
        raise ValueError("KiCad net-binding source coverage changed")
    for relative, expected in sources.items():
        if not (root / relative).is_file() or sha256(root / relative) != expected:
            raise ValueError(f"Stale KiCad net-binding source: {relative}")
    if set(artifact.get("projects", {})) != {"LESHY2-UI-R2", "LESHY2-RF-R2"}:
        raise ValueError("KiCad net-binding project coverage changed")
    for project, spec in artifact["projects"].items():
        mapping = spec.get("canonical_to_kicad", {})
        if (not mapping or any(not isinstance(v, str) or not v for v in mapping.values())
                or len(set(mapping.values())) != len(mapping)):
            raise ValueError(f"Invalid or non-unique KiCad net bindings: {project}")
    return artifact


def build(root=ROOT):
    import pcbnew
    from h6_r2_interface_label_coverage import check_coverage, load_contract, CONTRACT_PATH as COVERAGE_PATH
    contract_path = root / CONTRACT.relative_to(ROOT)
    ledger_path = root / LEDGER.relative_to(ROOT)
    contract = json.loads(contract_path.read_text())
    speaker_path = root / SPEAKER_BODY.relative_to(ROOT)
    contract["mechanical"]["speaker_body"] = json.loads(speaker_path.read_text())
    ledger = json.loads(ledger_path.read_text())["rows"]
    devices_path = root / "hardware/architecture/devices.json"
    devices = json.loads(devices_path.read_text())["devices"]
    coverage_contract = load_contract(root)
    binding_path = root / NET_BINDINGS.relative_to(ROOT)
    binding_hash = sha256(binding_path)
    bindings = checked_net_bindings(root)
    inputs = [contract_path, ledger_path, binding_path, Path(__file__), Path(__file__).with_name("h6_r2_user_silkscreen.py")]
    inputs += [root / path.relative_to(ROOT) for path in (B3S_LIBRARY, B3S_REVIEW, MIC_LIBRARY)]
    inputs += [speaker_path, Path(__file__).with_name("h6_r2_speaker_fit.py")]
    inputs += [devices_path, root / COVERAGE_PATH,
               Path(__file__).with_name("h6_r2_interface_label_coverage.py"),
               Path(__file__).with_name("h6-r2-interface-label-placements.json")]
    inputs += [root / relative for relative in bindings["source_hashes"]]
    inputs += [root / spec["output"] for spec in contract["boards"].values()]
    hashes = {str(path): sha256(path) for path in inputs}
    if hashes[str(binding_path)] != binding_hash:
        raise ValueError("KiCad net bindings changed during validation; rerun on a stable checkpoint")
    if any(hashes[str(root / relative)] != digest for relative, digest in bindings["source_hashes"].items()):
        raise ValueError("KiCad net-binding source changed during validation; rerun on a stable checkpoint")
    boards, snapshots, labels_by_project = [], {}, {}
    for project, spec in contract["boards"].items():
        native = pcbnew.LoadBoard(str(root / spec["output"]))
        snapshot = native_snapshot(native, project, ledger, contract, pcbnew, root)
        snapshots[project] = snapshot
        try:
            labels_by_project[project] = labels(project, snapshot["placements"], contract)
        except (KeyError, ValueError, OSError):
            labels_by_project[project] = []  # audit_snapshot records the binding failure.
        boards.append(audit_snapshot(snapshot, contract, bindings["projects"][project]["canonical_to_kicad"]))
    coverage = check_coverage(ledger, devices, labels_by_project,
                              native_snapshots=snapshots, contract=coverage_contract)
    if any(sha256(Path(path)) != digest for path, digest in hashes.items()):
        raise ValueError("Native board or audit input changed during read-only inspection; rerun on a stable checkpoint")
    return {"schema_version": 1, "scope": "native F/B free-board user text; required interface bindings and same-side mask/body/printed-silk screening",
            "status": "fail" if coverage["errors"] or any(b["status"] == "fail" for b in boards) else "review_required" if any(b["status"] == "review_required" for b in boards) else "pass_scoped",
            "production_release_authorized": False,
            "inputs_sha256": {str(Path(path).relative_to(root)): digest for path, digest in hashes.items()},
            "boards": boards,
            "interface_coverage": coverage,
            "limitations": ["Bounding-box candidates require visual inspection and native DRC; they are not proven ink collisions.",
                            "Visible footprint graphics/reference/value text are same-side ink obstacles, not automatically functional interface labels; hidden fields are not printed. This does not separately qualify package graphics against their own pads.",
                            "Supported default native stroke-font/pad-mask, exposed-via-mask, printed-silk and text/text pairs use actual shapes and a0.15-mm gap; unsupported pairs remain conservative candidates. Other geometry uses bounding boxes.",
                            "Only hash-bound primary-reviewed B3S and CMEJ-0413-42-SMT-TR courtyard candidates may resolve against matching native/library geometry with maximum body tolerance; circular bodies use filled circles and actual text strokes. This is not assembly qualification.",
                            "Native Edge.Cuts envelope must match the contracted board. Display-slot and microSD-recess source rectangles plus0.15-mm ink gap exclude text on both faces; native cutout correspondence is independently checked by placement projection. Connector/mechanical readiness remains separate.",
                            "The separately registered UI B-side speaker maximum body is a physical obstacle, not a printed Fab label. F/B text never collides with ink or SMD bodies solely on the opposite face; through drills remain obstacles on both faces.",
                            "1.0 mm font and 0.15 mm stroke are this label contract's minima, not factory qualification."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional temporary JSON path; otherwise print to stdout")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Publish only the generated audit; never change PCB files")
    mode.add_argument("--check", action="store_true", help="Verify the published audit matches current native files")
    args = parser.parse_args()
    if args.output and (args.write or args.check):
        parser.error("--output cannot be combined with --write or --check")
    temporary_roots = {Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve()}
    if args.output and not any(args.output.resolve().is_relative_to(path) for path in temporary_roots):
        parser.error("This unintegrated audit may emit files only under the system temporary directory")
    result = build()
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8")
        print(f"Native user silkscreen: {result['status']}; wrote {OUTPUT.relative_to(ROOT)}")
    elif args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            parser.exit(1, "Stale native user-silkscreen audit; rerun --write\n")
        print(f"Native user silkscreen: {result['status']}; current hashes verified")
    elif args.output:
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"status": result["status"], "output": str(args.output)}))
    else:
        print(text, end="")
    return 0 if result["status"] == "pass_scoped" else 1


if __name__ == "__main__":
    raise SystemExit(main())
