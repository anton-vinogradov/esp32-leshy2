#!/usr/bin/env python3
"""Independent product-intent checks, not a comparison to the placement freeze.

These requirements come from the exterior arrangement requested by the owner.
Changing a frozen coordinate or drawing cannot make a misplaced part pass.
This finite audit does not qualify component Z envelopes or factory assembly.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "hardware/layout/generated/H6-R2-placement-intent.json"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")


def native_bottom_edges(board, pcbnew):
    """Observe the finite UI bottom contour directly, without placement inputs.

    The corner arcs extend beyond X2..78 and are outside this notch feature.
    Start/mid/end points retain the actual native arc instead of its bbox.
    """
    result = []
    point = lambda p: [round(pcbnew.ToMM(p.x), 6), round(pcbnew.ToMM(p.y), 6)]
    for item in board.GetDrawings():
        if not isinstance(item, pcbnew.PCB_SHAPE) or item.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if item.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            kind, points = "line", [point(item.GetStart()), point(item.GetEnd())]
        elif item.GetShape() == pcbnew.SHAPE_T_ARC:
            kind, points = "arc", [point(item.GetStart()), point(item.GetArcMid()), point(item.GetEnd())]
        else:
            continue
        if all(1.999 <= x <= 78.001 and 147.999 <= y <= 150.001 for x, y in points):
            result.append([kind, *points])
    return sorted(result)


def checked_native_notch(edges):
    """Independent nominal 10x1.2/R0.6 opening; not a tolerance/fit proof."""
    expected = [
        ["line", [78, 150], [66.43, 150]],
        ["line", [66.43, 150], [66.43, 149.4]],
        ["arc", [66.43, 149.4], [66.254264, 148.975736], [65.83, 148.8]],
        ["line", [65.83, 148.8], [57.03, 148.8]],
        ["arc", [57.03, 148.8], [56.605736, 148.975736], [56.43, 149.4]],
        ["line", [56.43, 149.4], [56.43, 150]],
        ["line", [56.43, 150], [2, 150]],
    ]
    def matches(a, b):
        if len(a) != len(b) or a[0] != b[0]:
            return False
        return any(all(abs(x-y) <= .002 for p, q in zip(a[1:], points)
                       for x, y in zip(p, q))
                   for points in (b[1:], b[1:][::-1]))
    # Cardinality plus a bijection rejects duplicate, missing and closing edges.
    remaining = list(edges)
    for wanted in expected:
        hits = [i for i, observed in enumerate(remaining) if matches(observed, wanted)]
        if len(hits) != 1:
            return {"pass": False, "observed_edges": edges}
        remaining.pop(hits[0])
    if remaining:
        return {"pass": False, "observed_edges": edges}
    floor = next(row for row in edges if row[0] == "line"
                 and all(abs(p[1]-148.8) <= .002 for p in row[1:]))
    return {"pass": True, "axis_x_mm": sum(p[0] for p in floor[1:])/2,
            "floor_y_mm": sum(p[1] for p in floor[1:])/2,
            "observed_edges": edges}


def native_snapshot(root=ROOT):
    import pcbnew
    result = {"boards": {}, "sources": {}, "assembly_registration": {}, "bottom_edges": {}}
    script = Path(__file__).resolve()
    result["sources"][str(script.relative_to(root))] = hashlib.sha256(script.read_bytes()).hexdigest()
    helper = root / "hardware/layout/h6_r2_speaker_fit.py"
    speaker_json = root / "hardware/layout/h6-r2-speaker-body.json"
    for path in (helper, speaker_json):
        result["sources"][str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("intent_speaker", helper)
    speaker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(speaker)
    speaker_body = json.loads(speaker_json.read_text())
    for project in PROJECTS:
        path = root / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
        result["sources"][str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        board = pcbnew.LoadBoard(str(path))
        if project == PROJECTS[0]:
            result["bottom_edges"][project] = native_bottom_edges(board, pcbnew)
        result["assembly_registration"][project] = speaker.check_native_speaker_geometry(
            board, project, pcbnew, speaker_body)
        rows = {}
        for fp in board.GetFootprints():
            reference = fp.GetReference()
            if reference in rows:
                raise ValueError(f"duplicate {project} {reference}")
            pads = list(fp.Pads())
            point = lambda p: [round(pcbnew.ToMM(p.x), 6), round(pcbnew.ToMM(p.y), 6)]
            xy = []
            for graphic in fp.GraphicalItems():
                if isinstance(graphic, pcbnew.PCB_SHAPE) and graphic.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab):
                    bounds = graphic.GetBoundingBox()
                    xy += [point(bounds.GetOrigin()), point(bounds.GetEnd())]
            body = ([min(p[0] for p in xy), min(p[1] for p in xy),
                     max(p[0] for p in xy), max(p[1] for p in xy)] if xy else None)
            contacts = [p for p in pads if p.GetNumber() in ("1", "2", "3", "4")]
            actuator = ([sum(pcbnew.ToMM(p.GetPosition().x) for p in contacts)/4,
                         sum(pcbnew.ToMM(p.GetPosition().y) for p in contacts)/4]
                        if len(contacts) == 4 and "B3S-1100P" in str(fp.GetFPID().GetLibItemName()) else None)
            rows[reference] = {"footprint": str(fp.GetFPID().GetLibNickname()) + ":" + str(fp.GetFPID().GetLibItemName()),
                               "side": "B.Cu" if fp.IsFlipped() else "F.Cu",
                               "anchor_mm": point(fp.GetPosition()),
                               "rotation_deg": fp.GetOrientationDegrees(),
                               "fab_stroke_bounds_mm": body, "actuator_mm": actuator,
                               "pad1_nets": sorted({p.GetNetname() for p in pads if p.GetNumber() == "1"})}
        result["boards"][project] = rows
    return result


def evaluate(snapshot):
    checks = []

    def check(name, condition, observed):
        checks.append({"requirement": name, "pass": bool(condition), "observed": observed})

    ui = snapshot["boards"][PROJECTS[0]]
    rf = snapshot["boards"][PROJECTS[1]]
    assembly = snapshot.get("assembly_registration", {}).get(PROJECTS[0], {})
    check("speaker body registered on UI inner face, not confused with RF wire termination",
          assembly.get("status") == "pass_scoped_native_registration"
          and assembly.get("observed_count") == assembly.get("required_count") == 5,
          assembly)
    width, height, tol = 80.0, 150.0, 0.002
    near = lambda a, b: abs(a-b) <= tol
    holder, encoder, ptt, jack = (rf[r] for r in ("BT1", "SW3", "SW4", "U83"))
    check("holder centered on rear PCB, not shifted to clear another part",
          holder["side"] == "F.Cu" and near(holder["anchor_mm"][0], width/2)
          and near(holder["anchor_mm"][1], 85)
          and near(holder["rotation_deg"] % 180, 90), holder)
    body = holder["fab_stroke_bounds_mm"]
    check("holder drawing is the centered real body, not its 86mm land reserve",
          body is not None and near((body[0]+body[2])/2, width/2)
          and near((body[1]+body[3])/2, 85)
          and abs((body[2]-body[0])-39.78) < .16
          and abs((body[3]-body[1])-77.06) < .16, body)
    ntcs = [rf[r]["anchor_mm"] for r in ("R33", "R34")]
    check("two outward NTCs follow the centered cell axes",
          all(rf[r]["side"] == "F.Cu" for r in ("R33", "R34"))
          and near((ntcs[0][0]+ntcs[1][0])/2, width/2)
          and all(near(p[1], holder["anchor_mm"][1]) for p in ntcs)
          and near(ntcs[1][0]-ntcs[0][0], 19.1), ntcs)
    check("encoder on LEFT when looking at the exterior rear, antennas up",
          encoder["side"] == "F.Cu" and 0 < encoder["anchor_mm"][0] < width/4, encoder)
    check("PTT on RIGHT when looking at the exterior rear, antennas up",
          ptt["side"] == "F.Cu" and ptt["actuator_mm"] is not None
          and ptt["actuator_mm"][0] > width*3/4, ptt)
    check("headset jack body BETWEEN PCBs, with mouth toward left rear edge",
          jack["side"] == "B.Cu" and near(jack["rotation_deg"] % 360, 0)
          and 0 < jack["anchor_mm"][0] < 2, jack)
    mic = rf.get("MK1")
    # Exact CMEJ top acoustic openings are opposite its SMT pads (primary p2).
    # F mounting points them away from the RF exterior, not into the sandwich.
    # XY rotation does not change this normal; enclosure acoustics stay open.
    check("exact top-port microphone present on outward RF face",
          mic is not None and mic.get("footprint") == "Leshy2:CMEJ-0413-42-SMT-TR"
          and mic.get("side") == "F.Cu"
          and 0 < mic["anchor_mm"][0] < width and 0 < mic["anchor_mm"][1] < height,
          {"pose": mic, "port_normal_if_exact_F": "outward from RF F; not enclosure acoustic qualification"})
    exterior_functions = {"BT1", "R33", "R34", "SW3", "SW4", "J5", "J6", "J7", "J8", "J9", "J10", "L32", "MK1"}
    unexplained = sorted(ref for ref, row in rf.items()
                         if row["side"] == "F.Cu" and ref not in exterior_functions
                         and not ref.startswith("MH"))
    check("no ordinary RF support components moved outside merely to solve packing",
          not unexplained, unexplained)
    usb = rf["J1"]
    # This independently transcribes the exact JAE shell-mouth datum. The
    # manufacturer's reference PCB-edge position is NOT our physical edge.
    usb_mouth = usb["anchor_mm"][1] + 3.6
    check("product USB is inward-facing PCB mount, outward mouth without overhang",
          usb["side"] == "B.Cu" and near(usb["rotation_deg"] % 360, 180)
          and 0 <= height-usb_mouth <= 0.5, {"pose": usb, "mouth_y_mm": usb_mouth})
    sd = ui["J5"]
    notch = checked_native_notch(snapshot.get("bottom_edges", {}).get(PROJECTS[0], []))
    check("actual native microSD notch is open at the reviewed bottom-edge datum",
          notch["pass"], notch)
    locked, pushed, ejected = [sd["anchor_mm"][1]+v for v in (9.725, 8.925, 13.725)]
    card_axis = sd["anchor_mm"][0] + .425
    check("microSD locked card recessed; pressed card remains accessible at notch",
          sd["side"] == "B.Cu" and near(sd["rotation_deg"] % 360, 180)
          and notch["pass"] and near(card_axis, notch["axis_x_mm"])
          and notch["floor_y_mm"] < pushed < locked < height < ejected,
          {"card_axis_x_mm": card_axis, "notch_axis_x_mm": notch.get("axis_x_mm"),
           "locked_y_mm": locked, "pushed_y_mm": pushed, "ejected_y_mm": ejected})
    for left, right in zip(range(9, 13), range(13, 17)):
        a, b = ui[f"SW{left}"], ui[f"SW{right}"]
        ax, bx = a["actuator_mm"], b["actuator_mm"]
        check(f"F{left-8}/F{right-8} equal physical actuator edge insets",
              ax is not None and bx is not None and a["side"] == b["side"] == "F.Cu"
              and near(ax[0], width-bx[0]) and near(ax[1], bx[1]), [ax, bx])
    for project, refs in ((PROJECTS[0], ("J12", "J3", "J14", "J7", "J16")),
                          (PROJECTS[1], ("J9", "J8", "J5", "J6", "J7"))):
        bank = [snapshot["boards"][project][r] for r in refs]
        xs = [r["anchor_mm"][0] for r in bank]
        pitches = [b-a for a, b in zip(xs, xs[1:])]
        check(f"{project} five symmetric outward SMA ports at >=14.7mm pitch",
              all(r["side"] == "F.Cu" and near(r["anchor_mm"][1], 0)
                  and near(r["rotation_deg"] % 360, 180) for r in bank)
              and all(p >= 14.7-tol for p in pitches)
              and max(pitches)-min(pitches) < tol and near(xs[0]+xs[-1], width), xs)
    check("RF antenna labels match the actual UHF/VHF signal identities",
          rf["J6"]["pad1_nets"] == ["/RF_20_CC1101_VOICE_TX/VOICE_U_EXTERNAL_RF_50R"]
          and rf["J7"]["pad1_nets"] == ["/RF_20_CC1101_VOICE_TX/VOICE_V_EXTERNAL_RF_50R"],
          {r: rf[r]["pad1_nets"] for r in ("J6", "J7")})
    return {"schema_version": 1, "status": "pass" if all(c["pass"] for c in checks) else "fail",
            "scope": "Independent planar product intent from native PCB; not general DRC or assembled-Z qualification",
            "sources": snapshot.get("sources", {}), "checks": checks,
            "failed_requirements": [c["requirement"] for c in checks if not c["pass"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = evaluate(native_snapshot())
    content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        DEST.write_text(content)
    if args.check and (not DEST.exists() or DEST.read_text() != content):
        raise SystemExit("placement-intent report is stale")
    print(json.dumps({"status": result["status"], "failed": result["failed_requirements"]}, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
