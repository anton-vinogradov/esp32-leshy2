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
    same_face = []
    for entry in fixed:
        item, b = entry["item"], entry["bbox"]
        for row in base["rows"]:
            if row["source_frame"] != item["frame"]:
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
            gap = z_clearance(b, row["world_bbox_mm"])
            cross.append({"new": item["id"], "base": row["instance"], "clearance_mm": round(gap, 3)})
            if gap < minimum:
                errors.append(f"opposing clearance {item['id']} / {row['instance']} is {gap:.3f} mm")
    min_cross = min((x["clearance_mm"] for x in cross), default=None)
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "pass" if not errors else "fail",
        "base_model": model["base_model"],
        "new_fixed_body_count": len(fixed),
        "new_reserve_count": sum(x["item"]["kind"] == "reserve" for x in new),
        "same_face_collisions": same_face,
        "opposing_overlap_count": len(cross),
        "minimum_opposing_clearance_mm": min_cross,
        "required_opposing_clearance_mm": minimum,
        "opposing_overlaps": cross,
        "errors": errors,
        "open_gates": model["open_gates"],
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="850" viewBox="0 0 1380 850">',
        '<rect width="1380" height="850" fill="#ffffff"/>',
        '<text x="40" y="42" font-family="sans-serif" font-size="26" font-weight="700" fill="#172033">Leshy2 · H1-R2.1 inner placement</text>',
        '<text x="40" y="70" font-family="sans-serif" font-size="13" fill="#526076">World-scale engineering view · RF board is mirrored · numbered marks are documentation, never inner-face silkscreen.</text>',
    ]
    for frame, title in (("ui-inner", "UI PCB · inner"), ("rf-inner", "RF / power PCB · inner · mirrored")):
        x0 = ox[frame]
        out.append(f'<text x="{x0 + board_w * scale / 2:.2f}" y="96" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="#172033">{esc(title)}</text>')
        out.append(rect(x0, oy, board_w * scale, board_h * scale, fill="#f8fafc", stroke="#334155", stroke_width="2"))
        for row in base["rows"]:
            if row["source_frame"] != frame:
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
    mmcx_y = oy + 99.5 * scale
    fpv = next(item for item in model["placements"] if item["id"] == "fpv_receiver_bay")
    dec = next(item for item in model["placements"] if item["id"] == "fpv_decoder")
    fpv_x = rf_x + (board_w - fpv["world_xy_mm"][0] - fpv["size_mm"][0]) * scale
    fpv_cy = oy + (fpv["world_xy_mm"][1] + fpv["size_mm"][1] / 2) * scale
    dec_x = rf_x + (board_w - dec["world_xy_mm"][0] - dec["size_mm"][0]) * scale
    dec_cy = oy + (dec["world_xy_mm"][1] + dec["size_mm"][1] / 2) * scale
    out.extend([
        rect(rf_x - 19, mmcx_y, 19, 13, rx="3", fill="#dbeafe", stroke="#1d4ed8", stroke_width="2"),
        f'<text x="{rf_x - 9.5}" y="{mmcx_y + 6.5:.2f}" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="#1d4ed8">7</text>',
        f'<path d="M {rf_x - 19} {mmcx_y + 6.5:.2f} L {rf_x - 37} {mmcx_y + 6.5:.2f}" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>',
        f'<text x="{rf_x - 41}" y="{mmcx_y + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="9" font-weight="700" fill="#dc2626">finished-device RIGHT side</text>',
        f'<path d="M {rf_x:.2f} {mmcx_y + 6.5:.2f} L {fpv_x:.2f} {fpv_cy:.2f}" stroke="#0f766e" stroke-width="3" fill="none"/>',
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
        f'<text x="{audit_x}" y="344" font-family="sans-serif" font-size="15" font-weight="700" fill="#9a3412">Still open</text>',
    ])
    y = 370
    for line in (
        "exact in-production 5.8-GHz RX module",
        "Airband LC synthesis and image mask",
        "MMCX drawing / enclosure side opening",
        "1.8-V LDO live JLC stock recheck",
        "complete R2 rail and thermal matrix",
    ):
        out.append(f'<text x="{audit_x}" y="{y}" font-family="sans-serif" font-size="11" fill="#9a3412">• {esc(line)}</text>')
        y += 22
    out.append('</svg>')
    return "\n".join(out) + "\n"


def render_doc(model: dict, result: dict, ru: bool) -> str:
    if ru:
        title = "# H1-R2.1 · физическая перекомпоновка"
        intro = "Это текущий проверяемый результат H1, а не журнал решений и не разрешение начинать KiCad."
        state = "В принятую 75×150-мм систему координат добавлены второй Hub RP, активные корпуса Airband, видеодекодер FPV и сменная зона его ещё не выбранного 5,8-ГГц приёмника."
        audit_heading = "## Что уже проверено"
        open_heading = "## Что ещё блокирует H1"
        factory_heading = "## Точные фабричные позиции"
        bullets = [
            f'- Коллизии корпусов на одной стороне: `{len(result["same_face_collisions"])}`.',
            f'- Намеренных встречных XY-проекций: `{result["opposing_overlap_count"]}`; минимальный Z-зазор `{result["minimum_opposing_clearance_mm"]:.2f} мм` при требовании `{result["required_opposing_clearance_mm"]:.2f} мм`.',
            '- Большой резерв приёмника FPV помещается без изменения контура платы и внешних зон аккумуляторов/U214.',
            '- Hub остаётся на UI-плате рядом со storage/audio/broadcast; RF-модуль FPV и видеодекодер расположены вместе на RF-плате.',
        ]
        table_header = "| Роль | Точный MPN | JLCPCB | Статус выбора | Текущий маршрут |\n|---|---|---|---|---|"
        gates = model["open_gates_ru"]
    else:
        title = "# H1-R2.1 · physical re-layout"
        intro = "This is the current verified H1 result, not a decision diary and not authorization to start KiCad."
        state = "The second Hub RP, Airband active bodies, FPV video decoder and a replaceable bay for its still-unselected 5.8-GHz receiver are placed in the accepted 75 × 150 mm coordinate system."
        audit_heading = "## Already verified"
        open_heading = "## What still blocks H1"
        factory_heading = "## Exact factory parts"
        bullets = [
            f'- Same-face body collisions: `{len(result["same_face_collisions"])}`.',
            f'- Intentional opposing XY projections: `{result["opposing_overlap_count"]}`; minimum Z clearance is `{result["minimum_opposing_clearance_mm"]:.2f} mm` against `{result["required_opposing_clearance_mm"]:.2f} mm` required.',
            '- The large FPV receiver bay fits without changing the PCB outline or battery/U214 exterior zones.',
            '- Hub remains on the UI board beside storage/audio/broadcast; the FPV RF module and decoder remain together on the RF board.',
        ]
        table_header = "| Role | Exact MPN | JLCPCB | Selection status | Current route |\n|---|---|---|---|---|"
        gates = model["open_gates"]
    lines = [title, "", intro, "", state, "", "![H1-R2 inner placement](images/h1-r2-inner-placement.svg)", "", audit_heading, ""]
    lines.extend(bullets)
    lines.extend(["", factory_heading, "", table_header])
    for row in model["factory_evidence"]:
        role = row.get("role_ru", row["role"]) if ru else row["role"]
        route = row.get("availability_ru", row["availability"]) if ru else row["availability"]
        status = row.get("selection_status_ru", row["selection_status"]) if ru else row["selection_status"]
        lines.append(f'| {role} | `{row["mpn"]}` | [`{row["jlcpcb_part"]}`]({row["url"]}) | {status} | {route} |')
    lines.extend(["", open_heading, ""])
    lines.extend(f"- {gate}" for gate in gates)
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
