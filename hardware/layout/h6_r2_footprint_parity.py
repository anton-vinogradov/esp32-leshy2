#!/usr/bin/env python3
"""Audit native pad geometry against the actual selected footprint libraries.

Read-only for PCB/library files. --write updates only the JSON audit. Library
edits are not automatically applied to routed boards. This checks pads, not
body/cutout correctness, electrical semantics or physical part qualification.
Run with KiCad's bundled Python.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    import pcbnew
except ImportError:
    pcbnew = None

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-footprint-pad-parity.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
STANDARD = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
POLYGON_ERROR_MM = .001


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_pad_rows(actual, expected):
    """Keep multiplicities: four same-number shield tabs are four features."""
    encode = lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))
    got, want = Counter(map(encode, actual)), Counter(map(encode, expected))
    return {"native_only": [json.loads(s) for s in sorted((got-want).elements())],
            "library_only": [json.loads(s) for s in sorted((want-got).elements())]}


def canonical_ring(points):
    """Ignore contour start and winding, retaining every integer vertex."""
    points = tuple(tuple(point) for point in points)
    if len(points) > 1 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 3:
        raise ValueError("pad copper polygon has fewer than three vertices")
    first = min(points)
    candidates = []
    for ring in (points, tuple(reversed(points))):
        candidates.extend(ring[index:] + ring[:index]
                          for index, point in enumerate(ring) if point == first)
    return min(candidates)


def copper_polygon(pad, layer):
    """Canonical pad-relative copper contours in nm, with explicit curve error.

    KiCad's primitive vector is opaque in the Python binding. Use its actual
    copper polygon conversion, not only the custom-shape enum/anchor size.
    Include holes and every disjoint outline; never replace them by a bbox.
    """
    polygon = pcbnew.SHAPE_POLY_SET()
    pad.TransformShapeToPolygon(polygon, layer, 0, pcbnew.FromMM(POLYGON_ERROR_MM),
                                pcbnew.ERROR_INSIDE)
    if polygon.OutlineCount() == 0 or polygon.ArcCount():
        raise ValueError("pad copper polygon is empty or retains unsupported arcs")
    origin = pad.GetPosition()
    def ring(chain):
        return canonical_ring((chain.CPoint(i).x - origin.x, chain.CPoint(i).y - origin.y)
                              for i in range(chain.PointCount()))
    return sorted((ring(polygon.COutline(i)),
                   tuple(sorted(ring(polygon.CHole(i, hole))
                                for hole in range(polygon.HoleCount(i)))))
                  for i in range(polygon.OutlineCount()))


def pad_rows(fp):
    def xy(v):
        # Canonical micrometres avoid sub-nm float conversion artifacts while
        # remaining much tighter than any PCB/assembly tolerance.
        return [round(pcbnew.ToMM(v.x), 3), round(pcbnew.ToMM(v.y), 3)]
    rows = []
    for p in fp.Pads():
        layers = sorted(p.GetLayerSet().Seq())
        copper = [layer for layer in layers if pcbnew.IsCopperLayer(layer)]
        rows.append({"number": p.GetNumber(), "at_mm": xy(p.GetPosition()),
                     "size_mm": xy(p.GetSize()), "drill_mm": xy(p.GetDrillSize()),
                     "rotation_deg": round(p.GetOrientationDegrees() % 360, 3),
                     "shape": int(p.GetShape()), "drill_shape": int(p.GetDrillShape()),
                     "attribute": int(p.GetAttribute()), "layers": layers,
                     "roundrect_ratio": round(p.GetRoundRectRadiusRatio(), 6),
                     "copper_by_layer": [{
                         "layer": layer, "shape": int(p.GetShape(layer)),
                         "offset_mm": xy(p.GetOffset(layer)), "delta_mm": xy(p.GetDelta(layer)),
                         "chamfer_ratio": round(p.GetChamferRectRatio(layer), 6),
                         "chamfer_positions": int(p.GetChamferPositions(layer)),
                         "custom_anchor_shape": int(p.GetAnchorPadShape(layer)) if p.GetShape(layer) == pcbnew.PAD_SHAPE_CUSTOM else None,
                         "custom_zone_mode": int(p.GetCustomShapeInZoneOpt()) if p.GetShape(layer) == pcbnew.PAD_SHAPE_CUSTOM else None,
                         "polygon_nm": copper_polygon(p, layer),
                     } for layer in copper]})
    return rows


def build():
    if pcbnew is None:
        raise RuntimeError("run with KiCad's bundled Python runtime")
    sources, source_paths, boards, errors = {}, {}, [], []
    for project in PROJECTS:
        path = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
        board_sha256 = sha(path)
        board = pcbnew.LoadBoard(str(path))
        checked, deviations = [], []
        for native in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
            identity = native.GetFPID()
            nickname, name = str(identity.GetLibNickname()), str(identity.GetLibItemName())
            # add_mechanical_geometry() deliberately loads these eight holes
            # directly from this standard directory without a library nickname.
            # Resolve that exact controlled case only; do not guess other names.
            if (not nickname and native.GetReference() in {"MH1", "MH2", "MH3", "MH4"}
                    and name == "MountingHole_2.7mm_M2.5"):
                nickname = "MountingHole"
            if nickname in ("Leshy2", "Leshy2_R2"):
                directory = ROOT / f"hardware/ecad/libraries/{nickname}.pretty"
                source_label = str(directory.relative_to(ROOT) / (name + ".kicad_mod"))
            else:
                directory = STANDARD / (nickname + ".pretty")
                source_label = "kicad-standard/" + nickname + ".pretty/" + name + ".kicad_mod"
            library_path = directory / (name + ".kicad_mod")
            ref = native.GetReference()
            if not nickname or not name or not library_path.is_file():
                errors.append(f"{project}:{ref}: missing source {nickname}:{name}")
                continue
            current_digest = sha(library_path)
            if sources.setdefault(source_label, current_digest) != current_digest:
                errors.append(f"{source_label}: footprint library changed between instances")
            source_paths[source_label] = library_path
            expected = pcbnew.FootprintLoad(str(directory), name)
            if expected is None:
                errors.append(f"{project}:{ref}: unreadable source {nickname}:{name}")
                continue
            # A separate scratch board owns the expected footprint. Never
            # mutate native, its nets, stored geometry or routed copper.
            scratch = pcbnew.BOARD()
            scratch.Add(expected)
            if native.IsFlipped():
                expected.Flip(pcbnew.VECTOR2I(0, 0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            expected.SetOrientationDegrees(native.GetOrientationDegrees())
            expected.SetPosition(native.GetPosition())
            delta = compare_pad_rows(pad_rows(native), pad_rows(expected))
            checked.append(ref)
            if delta["native_only"] or delta["library_only"]:
                deviations.append({"reference": ref, "footprint": f"{nickname}:{name}",
                                   "source": source_label, **delta})
        boards.append({"project": project, "board": str(path.relative_to(ROOT)),
                       "board_sha256": board_sha256, "native_footprint_count": len(board.GetFootprints()),
                       "checked_references": checked, "deviations": deviations})
    if any(sha(source_paths[label]) != digest for label, digest in sources.items()):
        errors.append("footprint library changed during native comparison")
    if any(sha(ROOT / row["board"]) != row["board_sha256"] for row in boards):
        errors.append("native PCB changed during footprint comparison")
    count = sum(len(b["deviations"]) for b in boards)
    return {"schema_version": 2, "artifact": "H6-R2 native/library pad geometry parity",
            "status": "pass" if not errors and count == 0 else "open_native_library_drift",
            "fabrication_ready": False,
            "scope": "Pad number/multiplicity, transformed XY, size, angle, drill, layers, attribute, offset, trapezoid delta, chamfer, custom anchor/zone mode and canonical effective copper polygons on every pad copper layer. Polygon curves use an explicit 0.001-mm maximum tessellation error; vertices retain integer nanometres. Does not establish mask/paste aperture parity, body fit, cutouts, sourcing, nets or complete fabrication readiness.",
            "coordinate_precision_mm": .001, "source_library_sha256": dict(sorted(sources.items())),
            "copper_polygon_error_mm": POLYGON_ERROR_MM,
            "summary": {"native_footprints": sum(b["native_footprint_count"] for b in boards),
                        "checked_footprints": sum(len(b["checked_references"]) for b in boards),
                        "footprints_with_pad_geometry_drift": count, "lookup_errors": len(errors)},
            "errors": errors, "boards": boards}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    text = json.dumps(result, indent=2, sort_keys=False) + "\n"
    if args.write:
        OUTPUT.write_text(text)
    elif not OUTPUT.is_file() or OUTPUT.read_text() != text:
        raise SystemExit("stale native/library pad-parity audit; regenerate the read-only audit")
    print(json.dumps({"status": result["status"], **result["summary"]}))
    # --check means the report is reproducible, not that drift is cleared.
    # Always expose status; downstream release gates must require status=pass.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
