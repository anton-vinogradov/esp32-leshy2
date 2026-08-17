#!/usr/bin/env python3
"""Generate the paper-fit view for the U214 rear dock above the batteries."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/review/product-design/img/PHY-0001-u214-rear-fit.svg"

BOARD_W = 75.0
BOARD_H = 150.0
U214_W = 84.0
U214_REAR_STRIP = 15.281
U214_DEPTH_BEYOND_HOST_REAR = 15.11
U214_X = (BOARD_W - U214_W) / 2.0
U214_Y = 15.0
BATTERY_X, BATTERY_Y = 17.5, 40.0
BATTERY_W, BATTERY_H = 40.0, 78.0
BATTERY_DEPTH = 18.6
SMA_Y = 3.5
SMA_KEEP_OUT_R = 6.0
SMA_CENTRES = [13.0, 25.5, 38.0, 50.5, 63.0]
SMA_PATHS = ["N24-0", "CC-SUB", "N24-1", "VOICE-V/U", "N24-2"]


def overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def validate() -> list[str]:
    errors: list[str] = []
    u214 = (U214_X, U214_Y, U214_W, U214_REAR_STRIP)
    battery = (BATTERY_X, BATTERY_Y, BATTERY_W, BATTERY_H)
    old_encoder = (30.0, 20.0, 15.0, 13.0)

    if abs(-U214_X - 4.5) > 0.001 or abs(U214_X + U214_W - BOARD_W - 4.5) > 0.001:
        errors.append("U214 must overhang the 75-mm chassis symmetrically by 4.5 mm")
    if overlap(u214, battery):
        errors.append("U214 rear projection overlaps the battery-holder projection")
    if not overlap(u214, old_encoder):
        errors.append("legacy encoder collision must remain visible until the encoder is relocated")
    if U214_DEPTH_BEYOND_HOST_REAR >= BATTERY_DEPTH:
        errors.append("U214 must remain inside the bare-cell rear-depth silhouette")
    if U214_Y + U214_REAR_STRIP >= BATTERY_Y:
        errors.append("U214 needs a positive planar service gap above the battery holder")
    for centre in SMA_CENTRES:
        dx = max(U214_X - centre, 0.0, centre - (U214_X + U214_W))
        dy = max(U214_Y - SMA_Y, 0.0, SMA_Y - (U214_Y + U214_REAR_STRIP))
        if (dx * dx + dy * dy) ** 0.5 <= SMA_KEEP_OUT_R:
            errors.append(f"SMA at x={centre} collides with U214 projected keep-out")
    return errors


def render() -> str:
    scale = 4.0
    bx, by = 80.0, 90.0
    width, height = 760, 980

    def x(mm: float) -> float:
        return bx + mm * scale

    def y(mm: float) -> float:
        return by + mm * scale

    def rect(mm_x: float, mm_y: float, mm_w: float, mm_h: float, fill: str, stroke: str,
             dash: str = "", rx: float = 4.0) -> str:
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{x(mm_x):.1f}" y="{y(mm_y):.1f}" width="{mm_w * scale:.1f}" '
            f'height="{mm_h * scale:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="2"{dashed}/>'
        )

    def text(px: float, py: float, value: str, size: float = 14.0, weight: str = "normal",
             anchor: str = "start", colour: str = "#172033") -> str:
        return (
            f'<text x="{px:.1f}" y="{py:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        text(32, 34, "PHY-0001 — U214 rear dock above batteries", 21, "bold"),
        text(32, 58, "Paper fit from official M5Stack U214/Cardputer-Adv STL alignment; not enclosure sign-off", 12, colour="#526076"),
        text(bx, 80, "RF-board rear face — scaled plan view", 16, "bold"),
        rect(0, 0, BOARD_W, BOARD_H, "#edf2f7", "#344054", rx=10),
        rect(30.0, 20.0, 15.0, 13.0, "none", "#dc2626", "5 3", 3),
    ]

    for index, (centre, path) in enumerate(zip(SMA_CENTRES, SMA_PATHS, strict=True), start=1):
        out.append(
            f'<circle cx="{x(centre):.1f}" cy="{y(SMA_Y):.1f}" r="{3.175 * scale:.1f}" '
            f'fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>'
        )
        out.append(
            f'<circle cx="{x(centre):.1f}" cy="{y(SMA_Y):.1f}" r="{SMA_KEEP_OUT_R * scale:.1f}" '
            f'fill="none" stroke="#93c5fd" stroke-width="1" stroke-dasharray="4 3"/>'
        )
        out.append(text(x(centre), y(10.8), str(index), 10, "bold", "middle", "#1d4ed8"))

    out += [
        rect(U214_X, U214_Y, U214_W, U214_REAR_STRIP, "#ffedd5", "#ea580c", rx=7),
        text(x(BOARD_W / 2), y(U214_Y + 6.0), "M5Stack U214 Cap LoRa-1262", 12, "bold", "middle", "#9a3412"),
        text(x(BOARD_W / 2), y(U214_Y + 11.1), "LoRa/GNSS Cap · official 84-mm body", 10, anchor="middle", colour="#9a3412"),
        text(x(37.5), y(37.0), "legacy ENC → relocate", 10, "bold", "middle", "#b91c1c"),
        rect(BATTERY_X, BATTERY_Y, BATTERY_W, BATTERY_H, "#dcfce7", "#16a34a", rx=9),
        text(x(BATTERY_X + 2.0), y(BATTERY_Y + 5.0), "6", 10, "bold", colour="#166534"),
    ]

    for cell_x, label, number in ((20.0, "CELL 1", "7"), (38.7, "CELL 2", "8")):
        out.append(rect(cell_x, 46.0, 18.6, 65.0, "#bbf7d0", "#15803d", rx=28))
        out.append(text(x(cell_x + 3.0), y(50.0), number, 9, "bold", "middle", "#166534"))
        out.append(text(x(cell_x + 9.3), y(79), label, 9, "bold", "middle", "#166534"))
        out.append(text(x(cell_x + 9.3), y(84), "MPN TBD", 8, anchor="middle", colour="#166534"))

    note_x = 430.0
    out += [
        text(note_x, 100, "Separate physical devices", 15, "bold"),
        text(note_x, 128, "1  SMA connector · MPN TBD · N24-0 antenna port", 11),
        text(note_x, 150, "2  SMA connector · MPN TBD · CC-SUB antenna port", 11),
        text(note_x, 172, "3  SMA connector · MPN TBD · N24-1 antenna port", 11),
        text(note_x, 194, "4  SMA connector · MPN TBD · VOICE-V/U antenna port", 11),
        text(note_x, 216, "5  SMA connector · MPN TBD · N24-2 antenna port", 11),
        text(note_x, 238, "6  Battery holder · MPN TBD · 2×18650 retention", 11),
        text(note_x, 260, "7  Battery cell 1 · MPN TBD · device power", 11),
        text(note_x, 282, "8  Battery cell 2 · MPN TBD · device power", 11),
        text(note_x, 316, "U214 end openings must remain accessible:", 11, "bold"),
        text(note_x, 338, "own RP-SMA, downstream HY2.0-4P and screw access", 11),
        text(note_x, 372, "Plan clearances", 15, "bold"),
        text(note_x, 400, f"side overhang: {abs(U214_X):.1f} mm per side", 11),
        text(note_x, 422, f"SMA keep-out → U214: {U214_Y - SMA_Y - SMA_KEEP_OUT_R:.1f} mm", 11),
        text(note_x, 444, f"U214 → battery holder: {BATTERY_Y - U214_Y - U214_REAR_STRIP:.1f} mm", 11),
        text(note_x, 476, "Required mount", 15, "bold"),
        text(note_x, 504, "Cardputer-like raised rail / recessed female header", 11),
        text(note_x, 526, "+ two screw bosses; not a flat PCB header", 11),
        text(note_x, 558, "Four UI-board SMA are separate and unaffected.", 11, colour="#526076"),
    ]

    sy = 740.0
    sx = 80.0
    depth_scale = 8.0
    out += [
        text(sx, sy - 28, "Side section — rear protrusion", 16, "bold"),
        f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx + 600:.1f}" y2="{sy:.1f}" stroke="#344054" stroke-width="4"/>',
        text(sx + 610, sy + 5, "rear shell datum", 11, colour="#526076"),
        f'<rect x="{sx + 40:.1f}" y="{sy:.1f}" width="{190:.1f}" height="{U214_DEPTH_BEYOND_HOST_REAR * depth_scale:.1f}" '
        f'rx="8" fill="#ffedd5" stroke="#ea580c" stroke-width="2"/>',
        text(sx + 135, sy + 36, "U214", 13, "bold", "middle", "#9a3412"),
        text(sx + 135, sy + 56, f"+{U214_DEPTH_BEYOND_HOST_REAR:.2f} mm", 11, anchor="middle", colour="#9a3412"),
        f'<rect x="{sx + 330:.1f}" y="{sy:.1f}" width="{190:.1f}" height="{BATTERY_DEPTH * depth_scale:.1f}" '
        f'rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>',
        text(sx + 425, sy + 36, "18650 silhouette", 13, "bold", "middle", "#166534"),
        text(sx + 425, sy + 56, f"+{BATTERY_DEPTH:.1f} mm", 11, anchor="middle", colour="#166534"),
        text(sx + 290, sy + 176, f"depth reserve: {BATTERY_DEPTH - U214_DEPTH_BEYOND_HOST_REAR:.2f} mm", 12, "bold", "middle", "#166534"),
        text(sx, 942, "Open: exact dock/header MPN, boss geometry, enclosure wall, installed-cap hand/GNSS/RF HIL", 11, colour="#b45309"),
        "</svg>",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")

    errors = validate()
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    rendered = render()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        return 0
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        print(f"error: stale or missing {OUTPUT.relative_to(REPO)}")
        return 1
    print("ok: U214 rear-fit SVG is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
