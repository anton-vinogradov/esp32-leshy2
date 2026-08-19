#!/usr/bin/env python3
"""Generate and validate the first current G3 clamshell zoning projection."""

from __future__ import annotations

import argparse
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
OUTPUT = REPO / "docs/review/product-design/img/G3-0001-current-clamshell.svg"

BOARD_W = 75.0
BOARD_H = 150.0
HOLES = ((5.0, 5.0), (70.0, 5.0), (5.0, 145.0), (70.0, 145.0))
HOLE_KEEPOUT_R = 2.6
SMA_R = 3.175
SMA_KEEPOUT_R = 6.0
FRONT_SMA = ((15.0, "S3-2G4"), (30.0, "C5-2G4/5"), (45.0, "RX-FM/SW"), (60.0, "RX-AM/LW"))
REAR_SMA = ((13.0, "N24-0"), (25.5, "CC-SUB"), (38.0, "N24-1"), (50.5, "VOICE-V/U"), (63.0, "N24-2"))
U214 = (-4.5, 15.0, 84.0, 15.281)
BATTERY = (17.6, 40.0, 39.8, 86.0)
DISPLAY = (10.25, 11.0, 54.5, 101.5)
MEZZ = (23.5, 119.0, 28.0, 7.0)


@dataclass(frozen=True)
class Item:
    instance: str
    x: float
    y: float
    w: float
    h: float
    role: str
    kind: str = "device"


FRONT_INNER = (
    Item("s3", 6.0, 16.0, 18.0, 19.2, "UI/display/audio owner"),
    Item("c5", 51.0, 16.0, 18.0, 21.2, "native 2.4/5-GHz + IR owner"),
    Item("display_connector", 25.0, 42.0, 24.1, 6.4, "display FPC mate"),
    Item("sd", 6.0, 54.0, 13.85, 15.95, "removable microSD"),
    Item("slow_io", 25.0, 55.0, 5.0, 5.0, "main slow-control expander"),
    Item("ui_matrix_io", 34.0, 55.0, 5.0, 4.4, "local-control matrix expander"),
    Item("codec", 43.0, 55.0, 3.0, 3.0, "audio codec"),
    Item("receiver", 51.0, 54.0, 9.9, 6.0, "FM/AM/SW/LW receiver"),
    Item("ir_demod", 0.0, 76.0, 6.8, 3.0, "38-kHz IR receiver"),
    Item("ir_carrier", 0.0, 83.0, 6.8, 3.0, "carrier-learning IR receiver"),
    Item("ir_emitter", 0.0, 90.0, 3.1, 3.1, "940-nm IR transmitter"),
    Item("headphone_jack", 60.0, 76.0, 15.0, 9.5, "headphone/line connector"),
    Item("product_usb_protector", 20.0, 76.0, 3.0, 3.0, "CC/USB2 port protector"),
    Item("pd_controller", 27.0, 76.0, 4.0, 6.0, "sink-only USB-PD controller"),
    Item("product_usb_connector", 9.0, 143.0, 8.94, 6.9, "product USB-C data + sink"),
    Item("microphone", 33.5, 146.0, 4.0, 4.0, "bottom microphone port"),
)

REAR_INNER = (
    Item("rp", 32.5, 14.0, 10.0, 10.0, "deterministic radio owner"),
    Item("nrf0", 5.0, 30.0, 12.0, 19.0, "full-function nRF24 #0"),
    Item("nrf1", 31.5, 30.0, 12.0, 19.0, "full-function nRF24 #1"),
    Item("nrf2", 58.0, 30.0, 12.0, 19.0, "full-function nRF24 #2"),
    Item("voice", 5.0, 55.0, 39.5, 24.0, "VHF/UHF voice transceiver"),
    Item("cc", 50.0, 55.0, 4.0, 4.0, "multiband sub-GHz transceiver"),
    Item("c5_service_usb_connector", 13.0, 143.0, 8.94, 7.0, "C5 data-only service USB"),
    Item("rp_service_usb_connector", 34.0, 143.0, 8.94, 7.0, "RP data-only service USB"),
)

NUMBERED_ITEMS = FRONT_INNER + REAR_INNER
ITEM_NUMBER = {item.instance: index for index, item in enumerate(NUMBERED_ITEMS, 1)}

CONTROLS = (
    ("BACK", "ck_y78b23214fp"), ("F1", "ck_y78b23214fp"),
    ("D-pad UP", "ck_y78b23214fp"), ("D-pad DOWN", "ck_y78b23214fp"),
    ("D-pad LEFT", "ck_y78b23214fp"), ("D-pad RIGHT", "ck_y78b23214fp"),
    ("OK", "ck_y78b23214fp"), ("OPT", "ck_y78b23214fp"),
    ("F2", "ck_y78b23214fp"), ("ENC push", "alps_ec11e18244au"),
    ("PTT", "ck_y78b23214fp"), ("STOP", "panasonic_aeq10410"),
    ("RE-ARM", "ck_y78b23214fp"),
)


def load() -> tuple[dict, dict, dict]:
    database = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    return database, candidate, candidate["instances"]


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float], margin: float = 0.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw + margin and bx < ax + aw + margin and ay < by + bh + margin and by < ay + ah + margin


def validate() -> list[str]:
    devices, candidate, instances = load()
    errors: list[str] = []
    required_mpn = {
        "s3": "ESP32-S3-WROOM-1U-N16R2",
        "c5": "ESP32-C5-WROOM-1U-N8R8",
        "rp": "SC1512-A4",
        "display": "HMX035CTFT-001 (QDtech schematic assembly marking)",
        "u214": "M5Stack U214 Cap LoRa-1262",
        "pack_holder": "Keystone Electronics 1048P",
    }
    for instance, mpn in required_mpn.items():
        actual = devices[instances[instance]]["mpn"]
        if actual != mpn:
            errors.append(f"{instance}: expected current MPN {mpn}, got {actual}")
    if devices[instances["display"]].get("dimensions_mm") != [54.5, 101.5, 10.0]:
        errors.append("display G3 envelope must follow the published 54.5x101.5x10-mm reference")

    expected_paths = [path for _, path in FRONT_SMA + REAR_SMA]
    machine_paths = candidate["antenna_policy"]["base_onboard_sma_paths"]
    if len(expected_paths) != len(set(expected_paths)) or set(expected_paths) != set(machine_paths):
        errors.append("G3 antenna centres do not preserve the nine machine-source path identities")
    if len(FRONT_SMA) + len(REAR_SMA) != 9:
        errors.append("G3 projection must retain exactly nine onboard SMA endpoints")

    for face_name, items in (("front-inner", FRONT_INNER), ("rear-inner", REAR_INNER)):
        for item in items:
            if item.instance not in instances:
                errors.append(f"{face_name}: unknown instance {item.instance}")
            if item.x < 0 or item.y < 0 or item.x + item.w > BOARD_W + 0.01 or item.y + item.h > BOARD_H + 0.01:
                errors.append(f"{face_name}: {item.instance} is outside the board")
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if overlaps((left.x, left.y, left.w, left.h), (right.x, right.y, right.w, right.h), 0.7):
                    errors.append(f"{face_name}: {left.instance} overlaps {right.instance}")

    if overlaps(U214, BATTERY):
        errors.append("U214 rear strip overlaps the Keystone holder")
    if abs(U214[0]) != 4.5 or abs(U214[0] + U214[2] - BOARD_W) != 4.5:
        errors.append("U214 must retain symmetric 4.5-mm side overhang")
    if U214[1] + U214[3] >= BATTERY[1]:
        errors.append("U214 must retain a positive service gap above the holder")
    if DISPLAY[0] < 0 or DISPLAY[1] < 0 or DISPLAY[0] + DISPLAY[2] > BOARD_W or DISPLAY[1] + DISPLAY[3] > BOARD_H:
        errors.append("display envelope does not fit the front face")

    for bank_name, bank in (("front", FRONT_SMA), ("rear", REAR_SMA)):
        for index, (centre, _) in enumerate(bank):
            for other, _ in bank[index + 1 :]:
                if abs(centre - other) < SMA_KEEPOUT_R * 2:
                    errors.append(f"{bank_name} SMA keep-outs overlap at {centre}/{other}")
            for hx, hy in HOLES:
                if math.hypot(centre - hx, 3.5 - hy) < SMA_R + HOLE_KEEPOUT_R:
                    errors.append(f"{bank_name} SMA at {centre} hits mounting-hole keep-out")
    for centre, _ in REAR_SMA:
        dy = max(U214[1] - 3.5, 0.0, 3.5 - (U214[1] + U214[3]))
        dx = max(U214[0] - centre, 0.0, centre - (U214[0] + U214[2]))
        if math.hypot(dx, dy) <= SMA_KEEPOUT_R:
            errors.append(f"rear SMA at {centre} collides with U214 keep-out")

    if {name for name, _ in CONTROLS} != {
        "BACK", "F1", "D-pad UP", "D-pad DOWN", "D-pad LEFT", "D-pad RIGHT",
        "OK", "OPT", "F2", "ENC push", "PTT", "STOP", "RE-ARM",
    }:
        errors.append("complete local control inventory is not preserved")
    return errors


def render() -> str:
    devices, _, instances = load()
    scale = 3.0
    width, height = 1180, 1360
    origins = {"fo": (70.0, 105.0), "fi": (365.0, 105.0), "ri": (70.0, 625.0), "ro": (365.0, 625.0)}

    def sx(origin: tuple[float, float], mm: float) -> float:
        return origin[0] + mm * scale

    def sy(origin: tuple[float, float], mm: float) -> float:
        return origin[1] + mm * scale

    def text(x: float, y: float, value: str, size: float = 12, weight: str = "normal", anchor: str = "start", colour: str = "#172033") -> str:
        return f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'

    def rect(origin: tuple[float, float], x: float, y: float, w: float, h: float, fill: str, stroke: str, dash: str = "", rx: float = 3) -> str:
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<rect x="{sx(origin, x):.1f}" y="{sy(origin, y):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"{dashed}/>'

    def board(origin: tuple[float, float], title: str) -> list[str]:
        rows = [text(origin[0], origin[1] - 20, title, 15, "bold"), rect(origin, 0, 0, BOARD_W, BOARD_H, "#f8fafc", "#344054", rx=7)]
        for hx, hy in HOLES:
            rows.append(f'<circle cx="{sx(origin,hx):.1f}" cy="{sy(origin,hy):.1f}" r="{2.2*scale:.1f}" fill="white" stroke="#667085" stroke-width="1.4"/>')
        return rows

    def label_item(origin: tuple[float, float], item: Item) -> list[str]:
        rows = [rect(origin, item.x, item.y, item.w, item.h, "#eef2f6", "#667085")]
        cx, cy = sx(origin, item.x + item.w/2), sy(origin, item.y + item.h/2)
        rows.append(text(cx, cy + 4, str(ITEM_NUMBER[item.instance]), 9, "bold", "middle"))
        return rows

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(32, 34, "G3-0001 — current two-board clamshell working projection", 22, "bold"),
        text(32, 58, "75×150-mm legacy geometry reused; current owners, MPNs, controls, nine SMA paths and U214 restored", 12, colour="#526076"),
    ]
    out += board(origins["fo"], "1 · UI/CONTROL OUTER — front")
    out += board(origins["fi"], "2 · UI/CONTROL INNER — back view")
    out += board(origins["ri"], "3 · RF/POWER INNER — back view")
    out += board(origins["ro"], "4 · RF/POWER OUTER — rear")

    # Front face: current panel and the complete local controls.
    out.append(rect(origins["fo"], *DISPLAY, "#dbeafe", "#2563eb", rx=5))
    out.append(text(sx(origins["fo"], 37.5), sy(origins["fo"], 57), "HMX035CTFT-001", 9, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(origins["fo"], 37.5), sy(origins["fo"], 62), "3.5-inch QSPI IPS + touch", 7, anchor="middle", colour="#1d4ed8"))
    for x, y, label in ((5,120,"BACK"),(5,132,"F1"),(64,120,"OPT"),(64,132,"F2")):
        out.append(rect(origins["fo"], x, y, 6, 6, "#ede9fe", "#7c3aed", rx=4))
        out.append(text(sx(origins["fo"],x+3),sy(origins["fo"],y+4),label,5.5,"bold","middle","#6d28d9"))
    out.append(rect(origins["fo"], 27.5, 120, 20, 20, "#ede9fe", "#7c3aed", rx=8))
    out.append(text(sx(origins["fo"],37.5),sy(origins["fo"],132),"D-pad + OK",7,"bold","middle","#6d28d9"))
    for x, y, label, colour in ((0,70,"STOP","#b42318"),(69,70,"PTT","#7c3aed"),(1,143,"RE-ARM","#b42318"),(58,141,"ENC","#7c3aed")):
        out.append(rect(origins["fo"], x, y, 6 if label != "ENC" else 12, 7, "#fee4e2" if colour == "#b42318" else "#ede9fe", colour, rx=3))
        out.append(text(sx(origins["fo"],x+(3 if label != "ENC" else 6)),sy(origins["fo"],y+4.8),label,5.2,"bold","middle",colour))

    for origin, bank in ((origins["fo"], FRONT_SMA), (origins["ro"], REAR_SMA)):
        for centre, path in bank:
            out.append(f'<circle cx="{sx(origin,centre):.1f}" cy="{sy(origin,3.5):.1f}" r="{SMA_R*scale:.1f}" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>')
            out.append(text(sx(origin,centre),sy(origin,10.5),path,5.7,"bold","middle","#1d4ed8"))

    for item in FRONT_INNER:
        out += label_item(origins["fi"], item)
    for item in REAR_INNER:
        out += label_item(origins["ri"], item)
    for origin in (origins["fi"], origins["ri"]):
        out.append(rect(origin, *MEZZ, "#fce7f3", "#db2777", rx=3))
        out.append(text(sx(origin,37.5),sy(origin,123.5),"M1 · MPN TBD · power/HV/safety/S3↔RP",6.6,"bold","middle","#be185d"))
    out.append(rect(origins["ri"], 48, 64, 21, 58, "#fafaf9", "#a8a29e", "5 3", 4))
    out.append(text(sx(origins["ri"],58.5),sy(origins["ri"],91),"POWER",8,"bold","middle","#78716c"))
    out.append(text(sx(origins["ri"],58.5),sy(origins["ri"],96),"exact devices",6.5,anchor="middle",colour="#78716c"))
    out.append(text(sx(origins["ri"],58.5),sy(origins["ri"],101),"packing at G6/G9",6.5,anchor="middle",colour="#78716c"))

    out.append(rect(origins["ro"], *U214, "#ffedd5", "#ea580c", rx=6))
    out.append(text(sx(origins["ro"],37.5),sy(origins["ro"],23),"M5Stack U214 · LoRa/GNSS Cap · raised rear dock",8,"bold","middle","#9a3412"))
    out.append(rect(origins["ro"], *BATTERY, "#dcfce7", "#16a34a", rx=10))
    out.append(text(sx(origins["ro"],37.5),sy(origins["ro"],83),"Keystone 1048P",9,"bold","middle","#166534"))
    out.append(text(sx(origins["ro"],37.5),sy(origins["ro"],89),"2× XTAR 18650 4000mAh",7.2,anchor="middle",colour="#166534"))
    out.append(rect(origins["ro"], 57, 132, 18, 8, "#fef3c7", "#d97706", rx=3))
    out.append(text(sx(origins["ro"],66),sy(origins["ro"],137),"M5 Unit · MPN TBD",6.2,"bold","middle","#92400e"))
    out.append(rect(origins["ro"], 3, 132, 24, 12, "#dbeafe", "#2563eb", rx=7))
    out.append(text(sx(origins["ro"],15),sy(origins["ro"],139),"PUI AS02404PO · speaker",6.1,"bold","middle","#1d4ed8"))

    note_x = 650
    out += [
        text(note_x, 105, "Current physical split", 16, "bold"),
        text(note_x, 132, "UI/control board", 12, "bold", colour="#1d4ed8"),
        text(note_x, 152, "S3 + C5; display, storage, controls, audio/receiver and IR stay local.", 10.5),
        text(note_x, 178, "RF/power board", 12, "bold", colour="#c2410c"),
        text(note_x, 198, "RP + 3× E01-ML01IPX + CC1101RGPR + SA518; U214 and power stay local.", 10.5),
        text(note_x, 234, "No old ownership is inherited", 12, "bold"),
        text(note_x, 254, "nRF is RP-owned; IR is C5-owned; physical board locality is separate.", 10.5),
        text(note_x, 290, "Verified geometry retained", 12, "bold"),
        text(note_x, 310, "75×150 mm · fold/mirror · four M2.5 zones · 11-mm inner gap", 10.5),
        text(note_x, 330, "9 SMA keep-outs · 4.5-mm U214 overhang · exact 1048P envelope", 10.5),
        text(note_x, 366, "Visible controls retained", 12, "bold"),
        text(note_x, 386, "D-pad/OK · BACK · OPT · F1 · F2 · encoder/push · PTT", 10.5),
        text(note_x, 406, "hard STOP · recessed RE-ARM; phone is only optional text input", 10.5),
        text(note_x, 442, "Not yet frozen", 12, "bold", colour="#b42318"),
        text(note_x, 462, "SMA bodies/pigtails, M5 connectors, mezzanine, display approval", 10.5),
        text(note_x, 482, "drawing, enclosure stack, cable bends and final internal packing.", 10.5),
        text(note_x, 518, "Next G3 checks", 12, "bold"),
        text(note_x, 538, "hand/grip + installed-U214 access · side-control discrimination", 10.5),
        text(note_x, 558, "antenna/cable routing · service hatch · thermal/weight/centre of mass", 10.5),
        text(note_x, 594, "Working projection only — not G7 architecture and not KiCad.", 11, "bold", colour="#b42318"),
        text(650, 655, "Legend", 15, "bold"),
        '<rect x="650" y="674" width="24" height="14" rx="3" fill="#eef2f6" stroke="#667085"/>',
        text(684, 686, "one physical device · exact/current MPN + role", 10.5),
        '<rect x="650" y="702" width="24" height="14" rx="3" fill="#fafaf9" stroke="#a8a29e" stroke-dasharray="5 3"/>',
        text(684, 714, "placement responsibility, not a combined device", 10.5),
        '<rect x="650" y="730" width="24" height="14" rx="3" fill="#ffedd5" stroke="#ea580c"/>',
        text(684, 742, "removable external module/envelope", 10.5),
        text(650, 778, "Numbered physical devices", 14, "bold"),
    ]
    legend_y = 798
    for item in NUMBERED_ITEMS:
        mpn = devices[instances[item.instance]]["mpn"].replace(
            " (QDtech schematic assembly marking)", ""
        )
        number = ITEM_NUMBER[item.instance]
        out.append(text(650, legend_y, f"{number:02d}  {mpn}", 8.2, "bold"))
        out.append(text(676, legend_y + 9, item.role, 7.4, colour="#526076"))
        legend_y += 22
    out.append(text(650, legend_y + 2, "M1  MPN TBD · board-to-board power/HV/safety/S3↔RP mezzanine", 8.2, "bold", colour="#be185d"))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = validate()
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    rendered = render()
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"error: stale {OUTPUT.relative_to(REPO)}")
            return 1
        print("ok: G3 current clamshell projection is valid and current")
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
