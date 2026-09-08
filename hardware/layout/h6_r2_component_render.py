#!/usr/bin/env python3
"""Native, side-separated component plots; never edit production PCB files.

Fab is the current footprint drawing, not independently verified 3D geometry.
Back faces are viewed after turning the board around its vertical axis:
x_view = 80 - x_native, y_view = y_native. Both board identities use this rule;
these are individual face views, not a common assembled-device coordinate map.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOARDS = {name: ROOT / f"hardware/ecad/kicad/LESHY2-{name.upper()}-R2/LESHY2-{name.upper()}-R2.kicad_pcb"
          for name in ("ui", "rf")}
DEST = ROOT / "docs/images"
MANIFEST = ROOT / "hardware/layout/generated/H6-R2-component-views.json"
CLI_CANDIDATES = ("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli", "/usr/bin/kicad-cli", "/usr/local/bin/kicad-cli")
VIEWS = (("ui", "outer"), ("rf", "outer"), ("ui", "inner"), ("rf", "inner"))
WIDTH, HEIGHT = 96, 190
COLORS = {"#AFAFAF": "#334155", "#585D84": "#334155",  # front/back Fab
          "#F2EDA1": "#2563eb", "#E8B2A7": "#2563eb",  # front/back Silk
          "#D0D2CD": "#17263c", "#000000": "#17263c"}  # Edge.Cuts
SMA_REFERENCES = {
    "ui": {"J3": "32", "J7": "32", "J12": "31", "J14": "31", "J16": "31"},
    "rf": {"J5": "31", "J6": "31", "J7": "31", "J8": "31", "J9": "31"},
}


def sma_solder_lands(board, name):
    """Read copper lands on their actual face, independent of footprint side.

    SMA bodies are F footprints, but pads 4/5 are on B. Fab-only plotting and
    clipping opposite-face bodies therefore hid those real soldering sites.
    These are copper outlines, not paste/mask apertures or a solder/tool volume.
    """
    import pcbnew
    result = {"outer": [], "inner": []}
    selected = [fp for fp in board.GetFootprints()
                if "RFPC-SMA" in str(fp.GetFPID().GetLibItemName())]
    if {fp.GetReference() for fp in selected} != set(SMA_REFERENCES[name]) or len(selected) != 5:
        raise RuntimeError(f"{name}: unexpected SMA inventory; review solder-land coverage")
    for fp in sorted(selected, key=lambda item: item.GetReference()):
        ref = fp.GetReference()
        expected = f"RFPC-SMA{SMA_REFERENCES[name][ref]}-FN-175-A"
        if (str(fp.GetFPID().GetLibNickname()) != "Leshy2"
                or str(fp.GetFPID().GetLibItemName()) != expected or fp.IsFlipped()):
            raise RuntimeError(f"{name} {ref}: unreviewed SMA footprint/side")
        pads = list(fp.Pads())
        if len(pads) != 5 or {pad.GetNumber() for pad in pads} != {"1", "2", "3", "4", "5"}:
            raise RuntimeError(f"{name} {ref}: expected five distinct SMA solder lands")
        for pad in sorted(pads, key=lambda item: item.GetNumber()):
            number = pad.GetNumber()
            face = "inner" if number in {"4", "5"} else "outer"
            layer, other = ((pcbnew.B_Cu, pcbnew.F_Cu) if face == "inner"
                            else (pcbnew.F_Cu, pcbnew.B_Cu))
            if (pad.GetShape() != pcbnew.PAD_SHAPE_RECT or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD
                    or not pad.IsOnLayer(layer) or pad.IsOnLayer(other)):
                raise RuntimeError(f"{name} {ref}.{number}: unreviewed SMA pad geometry/layer")
            size, pos = pad.GetSize(), pad.GetPosition()
            result[face].append({"reference": ref, "pad": number,
                                 "side": "B.Cu" if face == "inner" else "F.Cu",
                                 "centre_mm": [pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)],
                                 "size_mm": [pcbnew.ToMM(size.x), pcbnew.ToMM(size.y)],
                                 "angle_deg": pad.GetOrientation().AsDegrees(),
                                 "net": pad.GetNetname()})
    return result


def render_sma_solder_lands(records, face):
    content = ['<g data-role="native-sma-solder-lands">']
    for row in records:
        x, y = row["centre_mm"]
        w, h = row["size_mm"]
        label = f'{row["reference"]}.{row["pad"]}'
        content += [f'<g data-role="sma-solder-land" data-reference="{row["reference"]}" '
                    f'data-pad="{row["pad"]}" data-side="{row["side"]}">',
                    f'<title>{html.escape(label + " · " + row["side"] + " · " + row["net"])} · copper land, not solder volume</title>',
                    f'<rect x="{x-w/2:.6f}" y="{y-h/2:.6f}" width="{w:.6f}" height="{h:.6f}" '
                    f'transform="rotate({-row["angle_deg"]:.6f} {x:.6f} {y:.6f})" fill="#f3bd53"/>']
        counter_mirror = " scale(-1 1)" if face == "inner" else ""
        content += [f'<g data-role="sma-land-label" transform="translate({x:.6f} {y:.6f}){counter_mirror} rotate(-90)">',
                    text(0, .2, label, .6, "#51350b", "middle"), '</g>', '</g>']
    return "\n".join(content + ['</g>'])


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def output(name, face):
    return DEST / f"h6-r2-components-{name}-{face}.svg"


def text(x, y, value, size=1.8, color="#334155", anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,DejaVu Sans,sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}">{html.escape(value)}</text>')


def export_native(cli, board, face, directory, card_reference=None):
    side = "F" if face == "outer" else "B"
    temporary = Path(directory) / f"{board.stem}-{face}.svg"
    layers = f"{side}.Fab,{side}.Silkscreen,Edge.Cuts"
    result = subprocess.run([str(cli), "pcb", "export", "svg", "--output", str(temporary),
                             "--layers", layers, "--mode-single", "--page-size-mode", "2",
                             "--fit-page-to-board", "--exclude-drawing-sheet", str(board)],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    svg = temporary.read_text()
    # KiCad keeps native mm coordinates. Do not use its automatically cropped
    # root viewport (it clips protruding connectors and differs between boards).
    content = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    content = re.sub(r"<title>.*?</title>", "", content, flags=re.S)
    content = re.sub(r"<desc>Image generated by PCBNEW\s*</desc>", "", content)
    for original, chosen in COLORS.items():
        content = content.replace(original, chosen)
    content = "\n".join(line.rstrip() for line in content.splitlines())
    return distinguish_microsd_card_states(content, face, card_reference)


def native_inventory(board_path):
    import pcbnew
    board = pcbnew.LoadBoard(str(board_path))
    footprints = list(board.GetFootprints())
    refs = {face: sorted(fp.GetReference() for fp in footprints
                        if fp.IsFlipped() == (face == "inner")) for face in ("outer", "inner")}
    positions = {}
    for fp in footprints:
        box = fp.GetBoundingBox(False, False)
        centre = box.GetCenter()
        positions[fp.GetReference()] = [pcbnew.ToMM(centre.x), pcbnew.ToMM(centre.y),
                                       pcbnew.ToMM(box.GetWidth()), pcbnew.ToMM(box.GetHeight())]
    holes = []
    for fp in footprints:
        for pad in fp.Pads():
            drill = pad.GetDrillSize()
            if not drill.x or not drill.y:
                continue
            pos = pad.GetPosition()
            x, y = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
            dx, dy = pcbnew.ToMM(drill.x), pcbnew.ToMM(drill.y)
            # KiCad angle is counterclockwise; SVG Y increases downwards.
            angle = -pad.GetOrientation().AsDegrees()
            # Oblong drills are capsules, not ellipses.
            holes.append(f'<rect x="{x-dx/2:.6f}" y="{y-dy/2:.6f}" width="{dx:.6f}" height="{dy:.6f}" '
                         f'rx="{min(dx,dy)/2:.6f}" transform="rotate({angle:.6f} {x:.6f} {y:.6f})" '
                         'fill="white" stroke="#9a6700" stroke-width="0.08"/>')
    # L32 is an unrouted PCB-loop reservation, not an installed component body.
    # Its real Dwgs.User rectangle must not vanish just because copper is hidden.
    reserve = []
    for fp in footprints:
        if fp.GetReference() != "L32" or "NFC_Pickup" not in str(fp.GetFPID().GetLibItemName()):
            continue
        for item in fp.GraphicalItems():
            if item.GetLayer() == pcbnew.Dwgs_User and isinstance(item, pcbnew.PCB_SHAPE):
                if item.GetShape() != pcbnew.SHAPE_T_RECT:
                    raise RuntimeError("unexpected NFC reserve shape")
                start, end = item.GetStart(), item.GetEnd()
                x0, x1 = sorted((pcbnew.ToMM(start.x), pcbnew.ToMM(end.x)))
                y0, y1 = sorted((pcbnew.ToMM(start.y), pcbnew.ToMM(end.y)))
                reserve.append(f'<rect x="{x0:.6f}" y="{y0:.6f}" width="{x1-x0:.6f}" height="{y1-y0:.6f}" '
                               'fill="none" stroke="#a16207" stroke-width="0.18" stroke-dasharray="1.1 .6"/>')
                reserve.append(text((x0+x1)/2, y1-1.2, "L32 · NFC reserve / резерв", 1.4, "#854d0e", "middle"))
    card_reference = microsd_reference_model(board) if board_path.stem == "LESHY2-UI-R2" else None
    name = "ui" if board_path.stem == "LESHY2-UI-R2" else "rf"
    return (refs, "\n".join(holes), "\n".join(reserve), positions,
            native_board_shape(board), card_reference, sma_solder_lands(board, name))


def microsd_reference_model(board):
    """One exact current footprint/pose, not an outside-board shape heuristic."""
    matches = [fp for fp in board.GetFootprints() if fp.GetReference() == "J5"]
    if len(matches) != 1:
        raise RuntimeError("UI J5 microSD reference illustration needs one exact footprint")
    fp = matches[0]
    identity = (str(fp.GetFPID().GetLibNickname()), str(fp.GetFPID().GetLibItemName()))
    if (identity != ("Connector_Card", "microSD_HC_Hirose_DM3AT-SF-PEJM5")
            or not fp.IsFlipped() or fp.GetOrientationDegrees() != 180):
        raise RuntimeError("UI J5 microSD reference illustration requires reviewed DM3AT B180 pose")
    import pcbnew
    pos = fp.GetPosition()
    return {"reference": "J5", "anchor_mm": [pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)]}


def microsd_state_paths(card_reference, state):
    """Transcription of DM3AT native Fab reference strokes, in native B180 XY.

    Local terminal card edges are y=9.725 locked and 13.725 ejected; both
    corner radii are .5 mm. This is the manufacturer's nominal 4-mm travel,
    not a tolerance or installed-card assertion. A changed native Fab must
    match all strokes below exactly at KiCad SVG's .0001-mm plotting precision.
    """
    x, y = card_reference["anchor_mm"]
    end = 9.725 if state == "locked" else 13.725
    paths = [f"M{x+5.425:.4f} {y+end:.4f} L{x-4.575:.4f} {y+end:.4f}",
             f"M{x-5.075:.4f} {y+end-.5:.4f} A0.5000 0.5000 0.0 0 0 {x-4.575:.4f} {y+end:.4f}",
             f"M{x+5.425:.4f} {y+end:.4f} A0.5000 0.5000 0.0 0 0 {x+5.925:.4f} {y+end-.5:.4f}"]
    if state == "ejected":
        paths += [f"M{x-5.075:.4f} {y+13.225:.4f} L{x-5.075:.4f} {y+8.325:.4f}",
                  f"M{x+5.925:.4f} {y+8.325:.4f} L{x+5.925:.4f} {y+13.225:.4f}"]
    return paths


def distinguish_microsd_card_states(native, face, card_reference):
    if card_reference is None or face != "inner":
        return native

    def key(path):
        tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", path)
        return tuple(token if token.isalpha() else float(token) for token in tokens)

    expected = {key(path): state for state in ("locked", "ejected")
                for path in microsd_state_paths(card_reference, state)}
    seen = {path: 0 for path in expected}

    def annotate(match):
        tag = match.group(0)
        path = re.search(r'\bd="([^"]+)"', tag)
        identity = key(path[1]) if path else None
        if identity not in expected:
            return tag
        state = expected[identity]
        seen[identity] += 1
        additions = f' data-role="microsd-card-state-reference" data-reference="J5" data-card-state="{state}"'
        if state == "ejected":
            style = "stroke:#b45309;stroke-dasharray:0.7 0.45;stroke-width:0.1;fill:none"
            if re.search(r'\bstyle="', tag):
                tag = re.sub(r'\bstyle="([^"]*)"', lambda m: f'style="{m[1]};{style}"', tag, count=1)
            else:
                additions += f' style="{style}"'
        return tag.replace("<path", "<path" + additions, 1)

    result = re.sub(r"<path\b[^>]*>", annotate, native)
    if any(count != 1 for count in seen.values()):
        raise RuntimeError("exact UI J5 locked/ejected Fab reference strokes changed or duplicated; review illustration")
    # The native two long vertical strokes are shared by the state outlines.
    # Restate only their locked-state subsegments solid, without hiding geometry.
    x, y = card_reference["anchor_mm"]
    for side in (-5.075, 5.925):
        result += (f'<path data-role="microsd-card-state-reference" data-reference="J5" data-card-state="locked" '
                   f'd="M{x+side:.4f} {y+8.325:.4f} L{x+side:.4f} {y+9.225:.4f}" '
                   'fill="none" stroke="#334155" stroke-width="0.1"/>')
    return result


def microsd_state_annotation(face, card_reference):
    if card_reference is None:
        return ""
    x, y = card_reference["anchor_mm"]
    centre, ejected = x + .425, y + 13.725
    counter = " scale(-1 1)" if face == "inner" else ""
    return (f'<g data-role="microsd-state-annotation" data-not-silkscreen="true">'
            f'<path d="M{centre:.4f} {ejected:.4f} v1.25" fill="none" stroke="#b45309" stroke-width=".1"/>'
            f'<g transform="translate({centre:.4f} {ejected+2.5:.4f}){counter}">'
            + text(0, 0, "card ejected / карта извлечена", .85, "#b45309", "middle") + '</g></g>')


def native_board_shape(board):
    """Fill the actual native board, including notches and routed openings.

    KiCad polygonizes the native Edge.Cuts solely for background/clip masks;
    the exported exact Edge.Cuts drawing remains visible over that fill. Never
    infer an outline from a bounding box or a possibly newer source contract.
    NPTH holes are rendered independently by native_inventory.
    """
    import pcbnew
    polygons = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(polygons, False, None, False, False):
        raise RuntimeError("native Edge.Cuts does not define a valid board; no rectangular render fallback")
    if polygons.OutlineCount() < 1:
        raise RuntimeError("native Edge.Cuts has no board outline")

    def chain_path(chain):
        if chain.PointCount() < 3:
            raise RuntimeError("native board contour has fewer than three points")
        points = [(pcbnew.ToMM(chain.CPoint(i).x), pcbnew.ToMM(chain.CPoint(i).y))
                  for i in range(chain.PointCount())]
        return "M" + " L".join(f"{x:.6f} {y:.6f}" for x, y in points) + " Z"

    outer, holes = [], []
    for index in range(polygons.OutlineCount()):
        outer.append(chain_path(polygons.COutline(index)))
        holes.extend(chain_path(polygons.CHole(index, hole))
                     for hole in range(polygons.HoleCount(index)))
    return {"outer": " ".join(outer), "material": " ".join(outer + holes)}


def with_reference_fallbacks(native, face, refs, positions):
    present = set(re.findall(r"<desc>([^<]+)</desc>", native))
    added = []
    for ref in refs:
        if ref.startswith("MH") or ref in present:
            continue
        x, y, width, height = positions[ref]
        size = 0.55 if min(width, height) < 2 else 0.75
        counter_mirror = " scale(-1 1)" if face == "inner" else ""
        native += (f'<g data-role="reference-label-fallback" data-reference="{ref}" '
                   f'transform="translate({x:.6f} {y:.6f}){counter_mirror}">'
                   + text(0, size*.35, ref, size, "#334155", "middle") + '</g>')
        added.append(ref)
    return native, added


def panel(name, face, native, opposite, refs, holes, reserve, board_shape, card_reference=None, solder_lands=""):
    side = "F" if face == "outer" else "B"
    count = sum(not ref.startswith("MH") for ref in refs)
    face_label = "наружная / outer" if face == "outer" else "внутренняя / inner"
    board_label = "Передняя UI" if name == "ui" else "Задняя RF / power"
    transform = "translate(80 0) scale(-1 1)" if face == "inner" else ""
    result = [text(8, 5, f"{board_label} · {face_label}", 2.6, "#17263c"),
              text(8, 8.3, f"{side} face · {count} позиций / items · 80 × 150 mm", 1.65),
              text(48, 12, "АНТЕННЫ / ANTENNA EDGE ↑", 1.45, "#475569", "middle"),
              '<g transform="translate(8 25)">',
              f'<g transform="{transform}">',
              f'<path data-role="native-board-material" d="{board_shape["material"]}" fill="#f8fafc" fill-rule="evenodd"/>',
              f'<defs><clipPath id="outside-{name}-{face}"><path clip-rule="evenodd" '
              f'd="M-8 -14H88V158H-8Z {board_shape["outer"]}"/></clipPath></defs>',
              f'<g data-role="opposite-face-protrusions" clip-path="url(#outside-{name}-{face})" opacity="0.65">',
              opposite, '</g>', solder_lands, native,
              '<g data-role="through-board-drills">', holes, '</g>',
              microsd_state_annotation(face, card_reference)]
    if face == "outer" and reserve:
        result.extend(['<g data-role="unrouted-nfc-reserve">', reserve, '</g>'])
    result.extend(['</g>', '</g>'])
    result.append(text(8, 179, "Золото / gold: площадки пайки SMA / SMA solder lands", 1.35, "#855b15"))
    if face == "inner":
        result.append(text(8, 186, "После переворота / turned over · x′ = 80 − x", 1.5))
    elif name == "ui":
        result.append(text(8, 186, "PCB без наклеенного экрана / display not installed", 1.5))
    else:
        result.append(text(8, 186, "Держатель без батарей / holder without cells", 1.5))
    result.append('<path d="M79 183 h10 M79 182 v2 M89 182 v2" fill="none" stroke="#334155" stroke-width=".15"/>')
    result.append(text(84, 186, "10 mm", 1.3, anchor="middle"))
    return "\n".join(result)


def wrap(content, width, height, metadata, title):
    attrs = " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in metadata.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width*20}" height="{height*20}" '
            f'viewBox="0 0 {width} {height}" {attrs}>\n<title>{html.escape(title)}</title>\n'
            f'<rect width="{width}" height="{height}" fill="white"/>\n{content}\n</svg>\n')


def write_all():
    cli = next((Path(p) for p in CLI_CANDIDATES if Path(p).is_file()), None)
    if cli is None:
        raise RuntimeError("KiCad CLI not found")
    inputs = {str(path.relative_to(ROOT)): digest(path) for path in (*BOARDS.values(), Path(__file__))}
    manifest = {"status": "current_native_visualization_not_assembly_approval", "inputs_sha256": inputs,
                "view_convention": "outer=native; inner=x_view=80-x_native, y unchanged; no extra RF transform",
                "same_scale": True, "board_size_mm": [80, 150],
                "layers": {"outer": "F.Fab,F.Silkscreen,Edge.Cuts", "inner": "B.Fab,B.Silkscreen,Edge.Cuts"},
                "overlays": {"sma_solder_lands": "Actual selected-face copper pads, including B pads of F footprints; not paste/mask or solder volume."},
                "limitations": ["Current Fab geometry includes known defects; not a 3D qualification.",
                                "No tracks, ratsnest, cells, display, loose cables or external antennas.",
                                "Native Edge.Cuts defines the background and outer-outline clip; KiCad polygonization is only a visual fill, not fabrication geometry.",
                                "Opposite-face drawings are shown only outside the actual outer board contour as context; not a 3D visibility test.",
                                "Reference designators are drawing annotations, not additional silkscreen.",
                                "Gold SMA copper lands are shown even when the footprint body belongs to the opposite face. They do not prove solder-tool or rework access.",
                                "UI J5 DM3AT card reference positions are nominal: locked solid, ejected ochre/dashed. The callout is a drawing annotation, not PCB silkscreen or an installed-card claim.",
                                "L32 is the actual Dwgs.User reservation, not completed loop copper."],
                "views": [], "outputs_sha256": {}}
    panels = []
    with tempfile.TemporaryDirectory(prefix="leshy2-component-plots-") as directory:
        inventories = {name: native_inventory(board) for name, board in BOARDS.items()}
        exports = {(name, face): export_native(cli, BOARDS[name], face, directory, inventories[name][5])
                   for name, face in VIEWS}
        for name, face in VIEWS:
            native = exports[name, face]
            opposite = exports[name, "outer" if face == "inner" else "inner"]
            refs, holes, reserve, positions, board_shape, card_reference, solder_lands = inventories[name]
            native, fallback_refs = with_reference_fallbacks(native, face, refs[face], positions)
            if name == "rf" and not reserve:
                raise RuntimeError("NFC reservation must remain visible on the RF outer plot")
            content = panel(name, face, native, opposite, refs[face], holes, reserve, board_shape,
                            card_reference, render_sma_solder_lands(solder_lands[face], face))
            board_hash = inputs[str(BOARDS[name].relative_to(ROOT))]
            path = output(name, face)
            path.write_text(wrap(content, WIDTH, HEIGHT,
                                 {"data-board": name, "data-face": face, "data-source-sha256": board_hash,
                                  "data-renderer-sha256": inputs[str(Path(__file__).relative_to(ROOT))]},
                                 f"Leshy2 current components · {name.upper()} {face}"))
            manifest["views"].append({"board": name, "face": face, "references": refs[face],
                                      "component_count": sum(not ref.startswith("MH") for ref in refs[face]),
                                      "mount_count": sum(ref.startswith("MH") for ref in refs[face]),
                                      "fallback_reference_labels": fallback_refs,
                                      "sma_solder_lands": solder_lands[face],
                                      "svg": str(path.relative_to(ROOT))})
            panels.append(content)
    overview = [text(8, 6, "Leshy2 · Компоненты обеих плат / Both boards", 3.4, "#17263c"),
                text(8, 10, "Одинаковый масштаб · контуры текущих footprints, не 3D-проверка сборки", 1.7),
                text(8, 13, "Same scale · current footprint drawings, not a 3D assembly validation", 1.7)]
    for index, content in enumerate(panels):
        overview.append(f'<g transform="translate({(index%2)*WIDTH} {18+(index//2)*HEIGHT})">{content}</g>')
    overview.append(text(8, 402, "Серый / grey: Fab + references    Синий / blue: actual silkscreen    Охра / ochre: holes / reserve", 1.65))
    overview.append(text(8, 405, "Золото / gold: 50 площадок пайки SMA / 50 SMA copper lands · не объём припоя / not solder volume", 1.5, "#855b15"))
    overview_path = DEST / "h6-r2-components-overview.svg"
    overview_path.write_text(wrap("\n".join(overview), WIDTH*2, 406,
                                   {"data-renderer-sha256": inputs[str(Path(__file__).relative_to(ROOT))]},
                                   "Leshy2 · four native component faces"))
    for path in [output(*view) for view in VIEWS] + [overview_path]:
        manifest["outputs_sha256"][str(path.relative_to(ROOT))] = digest(path)
    if any(digest(ROOT/path) != expected for path, expected in inputs.items()):
        raise RuntimeError("source changed during render")
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def check():
    manifest = json.loads(MANIFEST.read_text())
    for section in ("inputs_sha256", "outputs_sha256"):
        for name, expected in manifest[section].items():
            if digest(ROOT/name) != expected:
                raise RuntimeError(f"stale component view: {name}")
    if sum(view["component_count"] for view in manifest["views"]) != 1208:
        raise RuntimeError("component inventory coverage changed; review counts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_all()
    check()
    print("Native component views: 4 faces, 1208 inventory items, common scale; source PCBs untouched")


if __name__ == "__main__":
    main()
