#!/usr/bin/env python3
"""Read-only native SMA lands, exact copper contacts and bounded access screening.

The 1 mm rectangular per-land expansion is an engineering screening allowance,
NOT a factory standard, tool diameter, solder process or 3-D qualification.
Only --write writes this audit JSON and its marked bilingual report sections;
this module never saves a native board.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("hardware/layout/h6-r2-placement-contract.json")
OUTPUT = Path("hardware/layout/generated/H6-R2-sma-solder-access-audit.json")
DOCS = {"en": Path("docs/h6-r2-component-views.md"),
        "ru": Path("docs/h6-r2-component-views.ru.md")}
BEGIN = "<!-- SMA-SOLDER-ACCESS:BEGIN -->"
END = "<!-- SMA-SOLDER-ACCESS:END -->"
SCREENING_MM = 1.0
STANDARD = "RFPC-SMA31-FN-175-A"
REVERSE = "RFPC-SMA32-FN-175-A"
EXPECTED = {
    "LESHY2-UI-R2": {
        "nrf0_external_sma": ("J12", STANDARD),
        "s3_external_rp_sma": ("J3", REVERSE),
        "nrf1_external_sma": ("J14", STANDARD),
        "c5_external_rp_sma": ("J7", REVERSE),
        "nrf2_external_sma": ("J16", STANDARD),
    },
    "LESHY2-RF-R2": {
        "receiver_fmsw_external_sma": ("J9", STANDARD),
        "receiver_amlw_external_sma": ("J8", STANDARD),
        "cc_external_sma": ("J5", STANDARD),
        "voice_external_sma": ("J6", STANDARD),
        "voice_v_external_sma": ("J7", STANDARD),
    },
}
LIMITATIONS = [
    "Fab graphics bounding boxes are not manufacturer-qualified physical bodies or 3-D solids.",
    "Courtyard bounding boxes are placement reservations, not solder-tool volumes.",
    "Foreign copper pad contact is a native shape check, not a complete KiCad DRC run.",
    "The 1.0 mm rectangular screening expansion is engineering review only; it is not a factory rule or tool diameter.",
    "Tracks, zones, thermal mass, solder-mask clearance, paste process, tool approach angle and enclosure/other-board volumes are not qualified here.",
    "The separate SMA slot versus finished PCB thickness release gate remains open.",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_paths(root=ROOT):
    return [Path(__file__), root / CONTRACT,
            *(root / f"hardware/ecad/kicad/{p}/{p}.kicad_pcb" for p in EXPECTED),
            *(root / f"hardware/ecad/libraries/Leshy2.pretty/{name}.kicad_mod"
              for name in (STANDARD, REVERSE))]


def bbox_gap(a, b):
    return math.hypot(*(max(a[k][0] - b[k][1], b[k][0] - a[k][1], 0.0)
                        for k in ("x", "y")))


def overlaps(a, b):
    return all(a[k][0] <= b[k][1] and b[k][0] <= a[k][1] for k in ("x", "y"))


def expanded(box, amount=SCREENING_MM):
    return {k: [round(box[k][0] - amount, 6), round(box[k][1] + amount, 6)]
            for k in ("x", "y")}


def expected_pad(number, anchor):
    x, y = anchor
    dx = {"1": 0, "2": 2.55, "3": -2.55, "4": 2.55, "5": -2.55}[number]
    w = 1.87 if number == "1" else 1.6
    side = "F" if int(number) <= 3 else "B"
    return {"number": number, "shape": "rect", "attribute": "smd",
            "at_mm": [round(x + dx, 6), round(y + 1.65, 6)],
            "size_mm": [w, 3.3], "rotation_deg": 180.0, "offset_mm": [0.0, 0.0],
            "drill_mm": [0.0, 0.0], "side": side,
            "layers": sorted([side + ".Cu", side + ".Mask", side + ".Paste"]),
            "bbox_mm": {"x": [round(x + dx - w/2, 6), round(x + dx + w/2, 6)],
                        "y": [round(y, 6), round(y + 3.3, 6)]}}


def scope_errors(project, connectors, contract):
    errors = []
    expected = EXPECTED.get(project)
    if expected is None:
        return [{"kind": "unknown_project", "project": project}]
    ports = contract.get("antenna_ports", {}).get(project, {})
    if set(ports) != set(expected):
        errors.append({"kind": "contract_scope_mismatch", "project": project})
    observed = Counter(c["instance"] for c in connectors)
    if observed != Counter({instance: 1 for instance in expected}):
        errors.append({"kind": "native_scope_mismatch", "project": project,
                       "observed": dict(observed)})
    for row in connectors:
        instance = row["instance"]
        if instance not in expected or instance not in ports:
            continue
        reference, name = expected[instance]
        for key, value in {"reference": reference, "mpn": "GCT " + name,
                           "footprint": "Leshy2:" + name, "side": "F",
                           "rotation_deg": 180.0, "anchor_mm": ports[instance]}.items():
            if row.get(key) != value:
                errors.append({"kind": "connector_geometry_mismatch", "instance": instance, "field": key})
        counts = Counter(p["number"] for p in row["pads"])
        if counts != Counter({str(i): 1 for i in range(1, 6)}):
            errors.append({"kind": "pad_scope_mismatch", "instance": instance, "observed": dict(counts)})
        for pad in row["pads"]:
            if pad["number"] not in {str(i) for i in range(1, 6)}:
                continue
            for key, value in expected_pad(pad["number"], ports[instance]).items():
                if pad.get(key) != value:
                    errors.append({"kind": "pad_geometry_mismatch", "instance": instance,
                                   "pad": pad["number"], "field": key})
        grounds = [p.get("net") for p in row["pads"] if p["number"] in {"2", "3", "4", "5"}]
        signal = [p.get("net") for p in row["pads"] if p["number"] == "1"]
        if len(grounds) != 4 or not all(grounds) or len(set(grounds)) != 1 or not all(signal) or set(signal) & set(grounds):
            errors.append({"kind": "missing_or_inconsistent_sma_pad_nets", "instance": instance})
    return errors


def checked_gap(value):
    low, high = value.get("lower_mm"), value.get("upper_mm")
    if (value.get("method") != "native_effective_copper_shape"
            or type(value.get("contact_or_overlap")) is not bool
            or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
                   for x in (low, high))
            or low < 0 or not 0 <= high - low <= 0.0000011
            or (value["contact_or_overlap"] and (low != 0 or high != 0))):
        raise ValueError("invalid or unsupported native pad clearance proof")
    return value


def native_shape_gap(a, b, pcbnew):
    if a is None or b is None:
        raise ValueError("unsupported native effective copper shape")
    if a.Collide(b, 0):
        return {"method": "native_effective_copper_shape", "contact_or_overlap": True,
                "lower_mm": 0.0, "upper_mm": 0.0}
    low, high = 0, 1000
    while not a.Collide(b, high):
        low, high = high, high * 2
        if high > 1_000_000_000:
            raise ValueError("native clearance search exceeds one metre")
    while high - low > 1:
        mid = (low + high)//2
        if a.Collide(b, mid): high = mid
        else: low = mid
    return {"method": "native_effective_copper_shape", "contact_or_overlap": False,
            "lower_mm": round(pcbnew.ToMM(low), 6), "upper_mm": round(pcbnew.ToMM(high), 6)}


def classify_land(land, reference, obstacles, exact_gap):
    """BBox candidates stay separate from actual native copper shape contacts."""
    eligible = [o for o in obstacles if o["side"] == land["side"] and o["reference"] != reference]
    screen = expanded(land["bbox_mm"])
    candidates, pad_contacts, fab_hits, courtyard_hits = [], [], [], []
    nearest = {}
    for kind in ("foreign_pad", "fab_bbox", "courtyard_bbox", "drill_bbox"):
        ordered = sorted((o for o in eligible if o["kind"] == kind),
                         key=lambda o: (bbox_gap(land["bbox_mm"], o["bbox_mm"]), o["id"]))
        nearest_gap = math.inf
        for o in ordered:
            bbox_distance = bbox_gap(land["bbox_mm"], o["bbox_mm"])
            in_screen = overlaps(screen, o["bbox_mm"])
            if not in_screen and bbox_distance > nearest_gap:
                continue
            row = dict(o)
            row["bbox_gap_mm"] = round(bbox_distance, 6)
            if kind == "foreign_pad":
                proof = checked_gap(exact_gap(land["native_id"], o["native_id"], land["side"]))
                row["native_clearance"] = proof
                distance = proof["upper_mm"]
                if proof["contact_or_overlap"]:
                    pad_contacts.append(row)
            else:
                distance = bbox_distance
                if overlaps(land["bbox_mm"], o["bbox_mm"]):
                    if kind == "fab_bbox": fab_hits.append(row)
                    if kind == "courtyard_bbox": courtyard_hits.append(row)
            if distance < nearest_gap:
                nearest_gap = distance
                nearest[kind] = row
            if in_screen:
                row["classification"] = "engineering_screening_candidate"
                candidates.append(row)
    return {**land, "screening_bbox_mm": screen, "nearest": nearest,
            "foreign_pad_contact_or_overlap": pad_contacts,
            "foreign_fab_bbox_overlap": fab_hits,
            "foreign_courtyard_bbox_overlap": courtyard_hits,
            "screening_candidates": candidates}


def audit_snapshot(snapshot, contract, exact_gap):
    project = snapshot["project"]
    errors = scope_errors(project, snapshot["connectors"], contract)
    ids = [o["id"] for o in snapshot["obstacles"]]
    if len(ids) != len(set(ids)):
        errors.append({"kind": "duplicate_obstacle_identity", "project": project})
    connectors = []
    if not errors:
        for connector in sorted(snapshot["connectors"], key=lambda c: c["anchor_mm"][0]):
            row = {k: v for k, v in connector.items() if k != "pads"}
            row["pads"] = [classify_land(p, connector["reference"], snapshot["obstacles"], exact_gap)
                           for p in sorted(connector["pads"], key=lambda p: int(p["number"]))]
            connectors.append(row)
    pads = [p for c in connectors for p in c["pads"]]
    contacts = sum(len(p["foreign_pad_contact_or_overlap"]) for p in pads)
    candidates = sum(len(p["screening_candidates"]) for p in pads)
    return {"project": project, "native_board_sha256": snapshot["native_board_sha256"],
            "inventory_counts": snapshot["inventory_counts"], "connectors": connectors,
            "summary": {"connector_count": len(connectors), "pad_count": len(pads),
                        "front_pad_count": sum(p["side"] == "F" for p in pads),
                        "back_pad_count": sum(p["side"] == "B" for p in pads),
                        "native_foreign_pad_contact_count": contacts,
                        "fab_bbox_overlap_count": sum(len(p["foreign_fab_bbox_overlap"]) for p in pads),
                        "courtyard_bbox_overlap_count": sum(len(p["foreign_courtyard_bbox_overlap"]) for p in pads),
                        "screening_candidate_count": candidates,
                        "pads_with_screening_candidates": sum(bool(p["screening_candidates"]) for p in pads)},
            "errors": errors,
            "status": "fail" if errors or contacts else "review_required" if candidates else "no_candidates_in_screened_scope"}


def native_snapshot(path, project, pcbnew):
    board = pcbnew.LoadBoard(str(path))
    shapes = {}
    connectors, obstacles = [], []
    def point(v): return [round(pcbnew.ToMM(v.x), 6), round(pcbnew.ToMM(v.y), 6)]
    def box(b):
        return {"x": [round(pcbnew.ToMM(b.GetX()), 6), round(pcbnew.ToMM(b.GetRight()), 6)],
                "y": [round(pcbnew.ToMM(b.GetY()), 6), round(pcbnew.ToMM(b.GetBottom()), 6)]}
    def join(boxes):
        return {axis: [min(b[axis][0] for b in boxes), max(b[axis][1] for b in boxes)] for axis in ("x", "y")}
    fps = list(board.GetFootprints())
    if len({fp.GetReference() for fp in fps}) != len(fps):
        raise ValueError(f"{project}: duplicate footprint reference")
    for fp in fps:
        ref = fp.GetReference()
        field = fp.GetField("Leshy2Instance")
        instance = field.GetText() if field else ""
        item = str(fp.GetFPID().GetLibItemName())
        fpid = str(fp.GetFPID().GetLibNickname()) + ":" + item
        is_sma = instance in EXPECTED.get(project, {}) or "RFPC-SMA" in item or "RFPC-SMA" in fp.GetValue()
        pads = []
        for pad in fp.Pads():
            native_id = pad.m_Uuid.AsString()
            layers = sorted(board.GetLayerName(layer) for layer in pad.GetLayerSet().Seq())
            sides = [side for side, layer in (("F", pcbnew.F_Cu), ("B", pcbnew.B_Cu)) if pad.IsOnLayer(layer)]
            pad_record = {"native_id": native_id, "number": pad.GetNumber(), "net": pad.GetNetname(),
                          "shape": "rect" if pad.GetShape() == pcbnew.PAD_SHAPE_RECT else str(int(pad.GetShape())),
                          "attribute": "smd" if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD else str(int(pad.GetAttribute())),
                          "at_mm": point(pad.GetPosition()), "size_mm": point(pad.GetSize()),
                          "rotation_deg": round(pad.GetOrientationDegrees() % 360, 6),
                          "offset_mm": point(pad.GetOffset()), "drill_mm": point(pad.GetDrillSize()),
                          "side": sides[0] if len(sides) == 1 else "+".join(sides),
                          "layers": layers, "bbox_mm": box(pad.GetBoundingBox())}
            if is_sma: pads.append(pad_record)
            for side, layer in (("F", pcbnew.F_Cu), ("B", pcbnew.B_Cu)):
                if pad.IsOnLayer(layer) and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                    shapes[native_id, side] = pad.GetEffectiveShape(layer)
                    obstacles.append({"id": "pad:" + side + ":" + native_id,
                        "native_id": native_id, "kind": "foreign_pad", "reference": ref,
                        "pad": pad.GetNumber(), "mpn": fp.GetValue(), "net": pad.GetNetname(),
                        "side": side, "bbox_mm": pad_record["bbox_mm"]})
            drill = pad.GetDrillSize()
            if drill.x > 0 and drill.y > 0:
                angle = math.radians(pad.GetOrientationDegrees())
                dx, dy = pcbnew.ToMM(drill.x)/2, pcbnew.ToMM(drill.y)/2
                rx, ry = abs(dx*math.cos(angle))+abs(dy*math.sin(angle)), abs(dx*math.sin(angle))+abs(dy*math.cos(angle))
                x, y = point(pad.GetPosition())
                for side in ("F", "B"):
                    obstacles.append({"id": "drill:" + side + ":" + native_id,
                        "kind": "drill_bbox", "reference": ref, "pad": pad.GetNumber(), "side": side,
                        "bbox_mm": {"x": [round(x-rx, 6), round(x+rx, 6)], "y": [round(y-ry, 6), round(y+ry, 6)]}})
        for side, fab_layer, court_layer in (("F", pcbnew.F_Fab, pcbnew.F_CrtYd), ("B", pcbnew.B_Fab, pcbnew.B_CrtYd)):
            fab = [box(g.GetBoundingBox()) for g in fp.GraphicalItems()
                   if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() == fab_layer]
            if fab:
                obstacles.append({"id": "fab:" + side + ":" + ref, "kind": "fab_bbox",
                    "reference": ref, "mpn": fp.GetValue(), "side": side, "bbox_mm": join(fab)})
            courtyard = fp.GetCourtyard(court_layer).BBox()
            if courtyard.GetWidth() > 0 and courtyard.GetHeight() > 0:
                obstacles.append({"id": "court:" + side + ":" + ref, "kind": "courtyard_bbox",
                    "reference": ref, "mpn": fp.GetValue(), "side": side, "bbox_mm": box(courtyard)})
        if is_sma:
            connectors.append({"instance": instance, "reference": ref, "mpn": fp.GetValue(),
                "footprint": fpid, "side": "B" if fp.IsFlipped() else "F",
                "anchor_mm": point(fp.GetPosition()), "rotation_deg": round(fp.GetOrientationDegrees() % 360, 6),
                "pads": pads})
    def exact_gap(first, second, side):
        return native_shape_gap(shapes[first, side], shapes[second, side], pcbnew)
    return {"project": project, "native_board_sha256": sha256(path), "connectors": connectors,
            "obstacles": obstacles, "inventory_counts": {"footprints": len(fps),
                **dict(Counter(o["kind"] for o in obstacles))}}, exact_gap


def build(root=ROOT):
    import pcbnew
    paths = source_paths(root)
    before = {str(path.relative_to(root)): sha256(path) for path in paths}
    contract = json.loads((root / CONTRACT).read_text())
    if set(contract.get("antenna_ports", {})) != set(EXPECTED):
        raise ValueError("fixed two-project antenna scope mismatch")
    boards = []
    for project in EXPECTED:
        path = root / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
        snapshot, measure = native_snapshot(path, project, pcbnew)
        boards.append(audit_snapshot(snapshot, contract, measure))
    after = {str(path.relative_to(root)): sha256(path) for path in paths}
    if before != after:
        raise ValueError("source/native input changed while auditing")
    summary = {key: sum(b["summary"][key] for b in boards) for key in boards[0]["summary"]}
    error_count = sum(len(b["errors"]) for b in boards)
    failed = error_count or summary["native_foreign_pad_contact_count"]
    return {"schema_version": 1, "artifact": "H6-R2-native-SMA-solder-access-screening",
            "status": "fail" if failed else "review_required" if summary["screening_candidate_count"] else "no_candidates_in_screened_scope",
            "fixed_scope": {"boards": 2, "connectors": 10, "pads": 50, "F": 30, "B": 20},
            "screening": {"per_land_axis_expansion_mm": SCREENING_MM,
                "classification": "engineering_screening_only_not_factory_or_tool_standard"},
            "source_sha256": before, "summary": summary, "geometry_error_count": error_count,
            "boards": boards, "limitations": LIMITATIONS,
            "authorization": {"native_board_writes": False, "solder_process_qualified": False,
                              "three_dimensional_access_qualified": False, "production_release": False}}


def document_section(result, language):
    ru = language == "ru"
    s = result["summary"]
    prefix = (f"Текущий результат: **{s['pad_count']} площадок**, "
              f"{s['native_foreign_pad_contact_count']} пересечений/касаний чужих медных площадок, "
              f"{s['fab_bbox_overlap_count']} пересечений имеющихся Fab-габаритов и "
              f"{s['courtyard_bbox_overlap_count']} пересечений монтажных зон. "
              f"Предварительный запас выделил **{s['pads_with_screening_candidates']} площадок для ревью**." if ru else
              f"Current result: **{s['pad_count']} lands**, "
              f"{s['native_foreign_pad_contact_count']} contacts/overlaps with foreign copper pads, "
              f"{s['fab_bbox_overlap_count']} overlaps with available Fab bounding boxes and "
              f"{s['courtyard_bbox_overlap_count']} courtyard overlaps. "
              f"The provisional margin flagged **{s['pads_with_screening_candidates']} lands for review**.")
    lines = [BEGIN, "", prefix, "",
             "| Плата | Площадка | Ближайшая монтажная зона | Зазор, мм |" if ru else
             "| Board | Land | Nearest courtyard | Gap, mm |",
             "| --- | --- | --- | ---: |"]
    rows = []
    for board in result["boards"]:
        name = board["project"].removeprefix("LESHY2-").removesuffix("-R2")
        for connector in board["connectors"]:
            for pad in connector["pads"]:
                if not pad["screening_candidates"]:
                    continue
                nearest = pad["nearest"].get("courtyard_bbox")
                gap = nearest["bbox_gap_mm"] if nearest else math.inf
                rows.append((gap, name, f"{connector['reference']}.{pad['number']}",
                             pad["side"], nearest["reference"] if nearest else "—"))
    for gap, name, land, side, neighbour in sorted(rows):
        number = f"{gap:.3f}" if math.isfinite(gap) else "—"
        if ru: number = number.replace(".", ",")
        lines.append(f"| {name} · {side} | {land} | {neighbour} | {number} |")
    lines += ["", ("В таблице расстояние до монтажной зоны, **не до физического корпуса**; "
                    "полные отдельные измерения меди и Fab находятся в отчёте. "
                    "Это список для проверки доступа к пайке, не список коротких замыканий. " if ru else
                    "Table distances are to courtyards, **not physical bodies**; separate copper and Fab measurements "
                    "are in the report. These are solder-access review items, not a list of shorts. ")
              + f"`status: {result['status']}`; `solder_process_qualified: false`.", "", END]
    return "\n".join(lines)


def refreshed_document(text, section):
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
        raise ValueError("SMA report requires one ordered marker pair")
    return text[:text.index(BEGIN)] + section + text[text.index(END)+len(END):]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    audit = build()
    text = json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
    documents = {path: refreshed_document((ROOT / path).read_text(), document_section(audit, language))
                 for language, path in DOCS.items()}
    if args.write:
        (ROOT / OUTPUT).write_text(text, encoding="utf-8")
        for path, contents in documents.items():
            (ROOT / path).write_text(contents, encoding="utf-8")
    if args.check and (not (ROOT / OUTPUT).is_file() or (ROOT / OUTPUT).read_text() != text):
        print(f"STALE: {OUTPUT}")
        return 1
    if args.check:
        for path, contents in documents.items():
            if (ROOT / path).read_text() != contents:
                print(f"STALE: {path}")
                return 1
    print(json.dumps({"status": audit["status"], "summary": audit["summary"],
                      "solder_process_qualified": False, "production_release": False}))
    return 1 if audit["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
