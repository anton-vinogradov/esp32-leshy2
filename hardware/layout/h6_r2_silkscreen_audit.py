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


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
LEDGER = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NET_BINDINGS = ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json"
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-user-silkscreen-audit.json"
POSITION_TOLERANCE_MM = 0.01
DIMENSION_TOLERANCE_MM = 0.001
MIN_FONT_MM = 1.0
MIN_STROKE_MM = 0.15


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


def required_label_findings(required, actual):
    """A wrong layer/pose/text is an error, not a missing-label suppression."""
    findings, matched = [], []
    used = set()
    for expected in required:
        def distance(row):
            return math.dist(expected["at_mm"], row["at_mm"])
        at_pose = [n for n, row in enumerate(actual) if distance(row) <= POSITION_TOLERANCE_MM]
        exact = [n for n in at_pose if actual[n]["text"] == expected["text"]]
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
        if abs((row["angle_deg"] + 180) % 360 - 180) > 0.01:
            differences.append("angle_deg")
        if row["mirrored"] or not row["visible"]:
            differences.append("mirror_or_visibility")
        if row["horizontal_justify"] != 0 or row["vertical_justify"] != 0:
            differences.append("justification")
        if differences:
            findings.append({"kind": "required_label_mismatch", "fields": differences,
                             "expected": expected, "actual": row})
    return findings, matched


def geometry_candidates(texts, obstacles, width, height, radius=0.0, assembly_texts=None):
    candidates, exemptions = [], []
    assembly_texts = assembly_texts or {}
    visible = [row for row in texts if row["layer"] == "F.Silkscreen" and row["visible"]]
    for row in visible:
        if not within_outline(row["bbox_mm"], width, height, radius):
            candidates.append({"kind": "outer_outline_bbox", "text": row})
        if min(row["size_mm"]) < MIN_FONT_MM - DIMENSION_TOLERANCE_MM or row["thickness_mm"] < MIN_STROKE_MM - DIMENSION_TOLERANCE_MM:
            candidates.append({"kind": "small_free_user_text", "text": row})
        for obstacle in obstacles:
            if not overlaps(row["bbox_mm"], obstacle["bbox_mm"]):
                continue
            detail = {"kind": obstacle["kind"], "text": row, "obstacle": obstacle}
            if obstacle.get("fab_graphics_bbox_mm"):
                detail["fab_graphics_bbox_overlap"] = overlaps(row["bbox_mm"], obstacle["fab_graphics_bbox_mm"])
                detail["fab_graphics_bbox_gap_mm"] = bbox_gap(row["bbox_mm"], obstacle["fab_graphics_bbox_mm"])
            # Assembly visibility exceptions do not excuse solder-mask/drill or
            # outline crossings. Expose every exemption rather than erasing it.
            assembly_pose = assembly_texts.get(row["text"])
            if (assembly_pose is not None and math.dist(row["at_mm"], assembly_pose) <= POSITION_TOLERANCE_MM
                    and obstacle["kind"] in {"front_courtyard_bbox", "display_panel_bbox"}):
                detail["exemption_reason"] = "Correctly positioned assembly marking intentionally hidden after final assembly"
                exemptions.append(detail)
            elif obstacle["kind"] == "via_drill_bbox" and obstacle.get("front_tented"):
                detail["exemption_reason"] = "Native front tenting covers this via; it is not a front solder-mask opening"
                exemptions.append(detail)
            else:
                candidates.append(detail)
    for index, first in enumerate(visible):
        for second in visible[index + 1:]:
            if overlaps(first["bbox_mm"], second["bbox_mm"]):
                candidates.append({"kind": "user_text_bbox_overlap", "text": first, "other_text": second})
    return candidates, exemptions


def audit_snapshot(snapshot, contract, canonical_to_kicad=None):
    project = snapshot["project"]
    errors = antenna_signal_findings(project, snapshot["placements"], contract,
                                     canonical_to_kicad or {})
    try:
        required = labels(project, snapshot["placements"], contract)
    except (KeyError, ValueError) as exc:
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
        assembly_texts,
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
        "errors": errors, "geometry_candidates": candidates, "documented_geometry_exemptions": exemptions,
        "required_bindings": matched,
    }


def native_snapshot(board, project, ledger_rows, contract, pcbnew):
    """Extract actual pad, drill, footprint and free-text geometry without mutation."""
    def box_mm(box):
        return {"x": [pcbnew.ToMM(box.GetLeft()), pcbnew.ToMM(box.GetRight())],
                "y": [pcbnew.ToMM(box.GetTop()), pcbnew.ToMM(box.GetBottom())]}
    def point_mm(point):
        return [pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)]
    def expanded(box, amount):
        return {axis: [box[axis][0] - amount, box[axis][1] + amount] for axis in ("x", "y")}
    texts, placements, obstacles, errors = [], [], [], []
    by_reference = {}
    for fp in board.GetFootprints():
        reference = fp.GetReference()
        if reference in by_reference:
            errors.append({"kind": "duplicate_native_reference", "reference": reference})
        by_reference[reference] = fp
        layer = pcbnew.F_CrtYd if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd
        courtyard = fp.GetCourtyard(layer).BBox()
        if fp.GetLayer() == pcbnew.F_Cu and courtyard.GetWidth() > 0 and courtyard.GetHeight() > 0:
            obstacle = {"kind": "front_courtyard_bbox", "reference": reference, "bbox_mm": box_mm(courtyard)}
            fab = [box_mm(g.GetBoundingBox()) for g in fp.GraphicalItems()
                   if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() == pcbnew.F_Fab]
            if fab:
                obstacle["fab_graphics_bbox_mm"] = {axis: [min(b[axis][0] for b in fab), max(b[axis][1] for b in fab)] for axis in ("x", "y")}
            obstacles.append(obstacle)
        for graphic in fp.GraphicalItems():
            if graphic.GetLayer() == pcbnew.F_Mask:
                obstacles.append({"kind": "mask_graphic_bbox", "reference": reference, "bbox_mm": box_mm(graphic.GetBoundingBox())})
        for pad in fp.Pads():
            name = reference + "." + pad.GetNumber()
            if pad.IsOnLayer(pcbnew.F_Mask):
                obstacles.append({"kind": "front_pad_mask_bbox", "pad": name,
                                  "bbox_mm": expanded(box_mm(pad.GetBoundingBox()), pcbnew.ToMM(pad.GetSolderMaskExpansion(pcbnew.F_Mask)))})
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
                     "courtyard_centre_mm": centre, "footprint_anchor_mm": point_mm(fp.GetPosition())}
        if row["instance"] in ANTENNA_INTERFACES:
            placement["signal_pad_nets"] = sorted(
                pad.GetNetname() for pad in fp.Pads() if pad.GetNumber() == "1")
        placements.append(placement)
    for graphic in board.GetDrawings():
        if isinstance(graphic, pcbnew.PCB_TEXT):
            texts.append({"id": graphic.m_Uuid.AsString(), "text": graphic.GetText(),
                          "layer": board.GetLayerName(graphic.GetLayer()), "at_mm": point_mm(graphic.GetPosition()),
                          "size_mm": point_mm(graphic.GetTextSize()), "thickness_mm": pcbnew.ToMM(graphic.GetTextThickness()),
                          "angle_deg": graphic.GetTextAngleDegrees(), "mirrored": graphic.IsMirrored(), "visible": graphic.IsVisible(),
                          "horizontal_justify": int(graphic.GetHorizJustify()), "vertical_justify": int(graphic.GetVertJustify()),
                          "bbox_mm": box_mm(graphic.GetBoundingBox())})
        elif graphic.GetLayer() == pcbnew.F_Mask:
            obstacles.append({"kind": "mask_graphic_bbox", "bbox_mm": box_mm(graphic.GetBoundingBox())})
    for item in board.GetTracks():
        if not isinstance(item, pcbnew.PCB_VIA):
            continue
        x, y = point_mm(item.GetPosition())
        r = pcbnew.ToMM(item.GetDrillValue()) / 2
        if item.IsOnLayer(pcbnew.F_Cu):
            obstacles.append({"kind": "via_drill_bbox", "via": item.m_Uuid.AsString(),
                              "front_tented": item.IsTented(pcbnew.F_Cu), "bbox_mm": {"x": [x-r, x+r], "y": [y-r, y+r]}})
        if not item.IsTented(pcbnew.F_Cu) and item.IsOnLayer(pcbnew.F_Cu):
            obstacles.append({"kind": "front_via_mask_bbox", "via": item.m_Uuid.AsString(),
                              "bbox_mm": expanded(box_mm(item.GetBoundingBox()), pcbnew.ToMM(item.GetSolderMaskExpansion(pcbnew.F_Mask)))})
    if project == "LESHY2-UI-R2":
        obstacles.append({"kind": "display_panel_bbox", "bbox_mm": contract["mechanical"]["display_bed"]["panel_bbox_mm"]})
    return {"project": project, "placements": placements, "texts": texts, "obstacles": obstacles,
            "native_outline_bbox_mm": box_mm(board.GetBoardEdgesBoundingBox()), "extraction_errors": errors}


def checked_net_bindings(root=ROOT):
    """Load current H2-to-KiCad authority; stale/missing source proof is fatal."""
    path = root / NET_BINDINGS.relative_to(ROOT)
    artifact = json.loads(path.read_text())
    if (artifact.get("schema_version") != 1 or artifact.get("status") != "pass"
            or artifact.get("artifact") != "H6-R2 exact KiCad hierarchical net bindings"
            or artifact.get("errors") != []):
        raise ValueError("KiCad net-binding authority is not a passing artifact")
    expected_sources = {
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-controlled-symbol-library.json",
        "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_sch",
        "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_sch",
    }
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
    contract_path = root / CONTRACT.relative_to(ROOT)
    ledger_path = root / LEDGER.relative_to(ROOT)
    contract = json.loads(contract_path.read_text())
    ledger = json.loads(ledger_path.read_text())["rows"]
    binding_path = root / NET_BINDINGS.relative_to(ROOT)
    binding_hash = sha256(binding_path)
    bindings = checked_net_bindings(root)
    inputs = [contract_path, ledger_path, binding_path, Path(__file__), Path(__file__).with_name("h6_r2_user_silkscreen.py")]
    inputs += [root / relative for relative in bindings["source_hashes"]]
    inputs += [root / spec["output"] for spec in contract["boards"].values()]
    hashes = {str(path): sha256(path) for path in inputs}
    if hashes[str(binding_path)] != binding_hash:
        raise ValueError("KiCad net bindings changed during validation; rerun on a stable checkpoint")
    if any(hashes[str(root / relative)] != digest for relative, digest in bindings["source_hashes"].items()):
        raise ValueError("KiCad net-binding source changed during validation; rerun on a stable checkpoint")
    boards = []
    for project, spec in contract["boards"].items():
        native = pcbnew.LoadBoard(str(root / spec["output"]))
        snapshot = native_snapshot(native, project, ledger, contract, pcbnew)
        boards.append(audit_snapshot(snapshot, contract, bindings["projects"][project]["canonical_to_kicad"]))
    if any(sha256(Path(path)) != digest for path, digest in hashes.items()):
        raise ValueError("Native board or audit input changed during read-only inspection; rerun on a stable checkpoint")
    return {"schema_version": 1, "scope": "native free-board user text; required interface bindings plus conservative geometry screening",
            "status": "fail" if any(b["status"] == "fail" for b in boards) else "review_required" if any(b["status"] == "review_required" for b in boards) else "pass_scoped",
            "production_release_authorized": False,
            "inputs_sha256": {str(Path(path).relative_to(root)): digest for path, digest in hashes.items()},
            "boards": boards,
            "limitations": ["Bounding-box candidates require visual inspection and native DRC; they are not proven ink collisions.",
                            "Footprint package graphics/reference/value text are outside this free-board user-text audit.",
                            "Native Edge.Cuts envelope must match the contracted board; text is screened against its rounded envelope. Slot geometry, exact ink outlines and mechanical connector readiness are separate.",
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
