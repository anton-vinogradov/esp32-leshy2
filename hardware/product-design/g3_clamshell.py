#!/usr/bin/env python3
"""Generate and validate dimensioned Leshy2 mechanical projections."""

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
EXTERNAL_OUTPUT = REPO / "docs/images/current-clamshell.svg"
INTERNAL_OUTPUT = REPO / "docs/images/internal-board-layout.svg"

BOARD_W = 75.0
BOARD_H = 150.0
MOUNT_HOLE_D = 2.7
MOUNT_KEEPOUT_R = 4.0
HOLES = ((5.0, 11.0), (70.0, 11.0), (5.0, 145.0), (70.0, 145.0))

U214_X = -4.5
U214_Y = 17.0
U214_W = 84.0
U214_H = 24.0
U214_CLEARANCE = 0.7

# Exact GCT RFPC-SMA31/SMA32 1.6-mm edge-launch family. The 10.2-mm
# plan width includes the nut envelope; the 6-mm board-side depth comes from
# the exact land/body drawing rather than the full external threaded length.
RF_BODY_W = 10.2
RF_BODY_D = 6.0
RF_BARREL_D = 6.35
RF_BARREL_OUT = 11.4
FRONT_RF = (
    (16.0, "S3-2G4", "RP-SMA"),
    (30.0, "C5-2G4/5", "RP-SMA"),
    (45.0, "RX-FM/SW", "SMA"),
    (59.0, "RX-AM/LW", "SMA"),
)
REAR_RF = (
    (13.5, "N24-0", "SMA"),
    (25.5, "CC-SUB", "SMA"),
    (37.5, "N24-1", "SMA"),
    (49.5, "VOICE-V/U", "SMA"),
    (61.5, "N24-2", "SMA"),
)
TX_RF_PATHS = {
    "S3-2G4", "C5-2G4/5", "N24-0", "CC-SUB", "N24-1", "VOICE-V/U", "N24-2"
}
TX_LED_W = 1.6
TX_LED_H = 0.8
TX_LED_BOXES = {
    "S3-2G4": (22.2, 6.5, TX_LED_W, TX_LED_H),
    "C5-2G4/5": (36.7, 6.5, TX_LED_W, TX_LED_H),
    "N24-0": (12.7, 7.0, TX_LED_W, TX_LED_H),
    "CC-SUB": (24.7, 7.0, TX_LED_W, TX_LED_H),
    "N24-1": (36.7, 7.0, TX_LED_W, TX_LED_H),
    "VOICE-V/U": (48.7, 7.0, TX_LED_W, TX_LED_H),
    "N24-2": (60.7, 7.0, TX_LED_W, TX_LED_H),
}
TX_LED_INSTANCES = {
    "S3-2G4": "s3_tx_led",
    "C5-2G4/5": "c5_tx_led",
    "N24-0": "nrf0_tx_led",
    "CC-SUB": "cc_tx_led",
    "N24-1": "nrf1_tx_led",
    "VOICE-V/U": "voice_tx_led",
    "N24-2": "nrf2_tx_led",
}


@dataclass(frozen=True)
class Placement:
    instance: str
    x: float
    y: float
    role: str
    rotation: int = 0


@dataclass(frozen=True)
class Reserve:
    name: str
    x: float
    y: float
    w: float
    h: float
    role: str


UI_INNER = (
    Placement("s3", 6.0, 22.0, "UI, display, storage and audio owner"),
    Placement("c5", 51.0, 22.0, "native 2.4/5-GHz and IR owner"),
    Placement("display_connector", 25.0, 43.0, "40-contact display FPC mate"),
    Placement("slow_io", 24.0, 55.0, "24-line slow-control expander"),
    Placement("ui_matrix_io", 33.0, 55.0, "local-control matrix expander"),
    Placement("codec", 42.0, 55.0, "audio capture and playback codec"),
    Placement("receiver", 51.0, 54.0, "FM/AM/SW/LW receiver"),
    Placement("ir_demod", 0.0, 75.0, "38-kHz IR receiver"),
    Placement("ir_carrier", 0.0, 82.0, "carrier-learning IR receiver"),
    Placement("ir_emitter", 0.0, 89.0, "940-nm IR transmitter"),
    Placement("ir_safe_gate", 8.0, 75.0, "UI-local STOP-qualified IR carrier gate"),
    Placement("evidence_cmp_a", 8.0, 82.0, "UI-local S3/C5/IR TX evidence comparator"),
    Placement("headphone_jack", 60.0, 75.0, "3.5-mm headphone/line connector"),
    Placement("safe_conditioner", 20.0, 75.0, "front-local STOP input conditioner"),
    Placement("safe_latch", 23.0, 75.0, "front-local STOP/RE-ARM safety latch"),
    Placement("safe_reset_buffer", 27.0, 75.0, "front-local reset-kill buffer"),
    Placement("safe_reset_sink_a", 30.0, 75.0, "S3/C5 reset sinks"),
    Placement("m1_ui_plug", 22.2, 119.0, "80-contact M1 plug; 11-mm board stack"),
    Placement("c5_service_usb_connector", 27.0, 142.65, "C5 data-only service USB"),
    Placement("microphone", 42.0, 146.0, "bottom microphone port"),
    Placement("sd", 48.0, 136.15, "bottom-access push-push microSD", 90),
)

RF_INNER = (
    Placement("rp", 32.5, 22.0, "deterministic radio owner"),
    Placement("nrf0", 6.0, 34.5, "full-function nRF24 radio #0"),
    Placement("nrf1", 31.5, 34.5, "full-function nRF24 radio #1"),
    Placement("nrf2", 57.0, 34.5, "full-function nRF24 radio #2"),
    Placement("voice", 5.0, 57.0, "VHF/UHF voice transceiver"),
    Placement("cc", 50.0, 57.0, "multi-band sub-GHz transceiver"),
    Placement("nvdc_charger", 49.0, 67.0, "2S charger and NVDC power path"),
    Placement("pack_gauge", 56.0, 67.0, "2S protection and fuel gauge"),
    Placement("pack_admission", 63.0, 67.0, "fail-closed battery admission MCU"),
    Placement("aon_buck", 49.0, 75.0, "always-on 3.3-V converter"),
    Placement("main_buck", 54.0, 75.0, "main 3.3-V converter"),
    Placement("voice_buck", 59.0, 75.0, "voice 4.0-V converter"),
    Placement("ext_buck", 64.0, 75.0, "accessory 5.0-V converter"),
    Placement("safe_supervisor", 49.0, 82.0, "always-on safety supervisor"),
    Placement("safe_reset_sink_b", 55.0, 82.0, "RP reset sink"),
    Placement("safe_ptt_or", 59.0, 82.0, "STOP-dominant voice PTT gate"),
    Placement("safe_gate_b", 49.0, 88.0, "rear-domain transmit safety gates"),
    Placement("evidence_cmp_b", 58.0, 88.0, "RF-local nRF/CC TX evidence comparator"),
    Placement("evidence_cmp_voice", 66.0, 88.0, "RF-local voice TX evidence comparator"),
    Placement("product_usb_protector", 20.0, 87.0, "product USB CC/USB2 protector"),
    Placement("pd_controller", 25.0, 87.0, "sink-only USB-PD controller"),
    Placement("speaker_amp", 31.0, 87.0, "rear-local differential speaker amplifier"),
    Placement("safe_gate_a", 49.0, 94.0, "nRF-domain transmit safety gates"),
    Placement("m1_rf_receptacle", 22.2, 119.0, "80-contact M1 receptacle; 11-mm board stack"),
    Placement("product_usb_connector", 12.0, 143.1, "product USB-C data and sink"),
    Placement("rp_service_usb_connector", 33.0, 142.65, "RP data-only service USB"),
)

FRONT_CONTROLS = (
    Placement("stop_switch", 9.0, 114.0, "physical hard STOP"),
    Placement("ptt_switch", 14.0, 131.0, "independent PTT"),
    Placement("ui_switch_back", 24.0, 115.0, "BACK"),
    Placement("ui_switch_f1", 24.0, 132.0, "F1"),
    Placement("ui_switch_up", 35.4, 115.0, "D-pad up"),
    Placement("ui_switch_left", 29.5, 124.5, "D-pad left"),
    Placement("ui_switch_ok", 35.4, 124.5, "D-pad OK"),
    Placement("ui_switch_right", 41.3, 124.5, "D-pad right"),
    Placement("ui_switch_down", 35.4, 134.0, "D-pad down"),
    Placement("ui_switch_opt", 51.0, 115.0, "OPT"),
    Placement("ui_switch_f2", 51.0, 132.0, "F2"),
    Placement("encoder", 59.0, 113.0, "rotary encoder with push"),
    Placement("rearm_switch", 63.0, 132.0, "recessed RE-ARM"),
)

CAP_RESERVES = (
    Reserve("PTT cap", 12.1, 128.9, 8.0, 7.0, "ergonomic cap/case feature, MPN TBD"),
    Reserve("BACK cap", 23.1, 112.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("F1 cap", 23.1, 129.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("UP cap", 34.5, 112.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("LEFT cap", 28.6, 122.4, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("OK cap", 34.5, 122.4, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("RIGHT cap", 40.4, 122.4, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("DOWN cap", 34.5, 131.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("OPT cap", 50.1, 112.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("F2 cap", 50.1, 129.9, 6.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("encoder knob", 57.0, 111.0, 15.0, 15.0, "knob/case feature, MPN TBD"),
    Reserve("RE-ARM cap", 61.1, 129.9, 8.0, 7.0, "recessed cap/case feature, MPN TBD"),
)


def load() -> tuple[dict, dict, dict]:
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    return devices, candidate, candidate["instances"]


def placement_size(item: Placement, devices: dict, instances: dict) -> tuple[float, float]:
    dimensions = devices[instances[item.instance]].get("dimensions_mm")
    if not dimensions or len(dimensions) < 2 or dimensions[0] is None or dimensions[1] is None:
        raise ValueError(f"{item.instance}: two-dimensional package envelope is missing")
    w, h = float(dimensions[0]), float(dimensions[1])
    return (h, w) if item.rotation % 180 else (w, h)


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float], margin: float = 0.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw + margin and bx < ax + aw + margin and ay < by + bh + margin and by < ay + ah + margin


def hits_hole(
    rectangle: tuple[float, float, float, float],
    hole: tuple[float, float],
    clearance: float = 0.0,
) -> bool:
    x, y, w, h = rectangle
    hx, hy = hole
    px = min(max(hx, x), x + w)
    py = min(max(hy, y), y + h)
    return math.hypot(hx - px, hy - py) < MOUNT_KEEPOUT_R + clearance


def validate_items(name: str, items: tuple[Placement, ...], devices: dict, instances: dict) -> list[str]:
    errors: list[str] = []
    rectangles = []
    for item in items:
        if item.instance not in instances:
            errors.append(f"{name}: unknown instance {item.instance}")
            continue
        try:
            w, h = placement_size(item, devices, instances)
        except ValueError as error:
            errors.append(str(error))
            continue
        rectangle = (item.x, item.y, w, h)
        rectangles.append((item, rectangle))
        if item.x < 0 or item.y < 0 or item.x + w > BOARD_W + 0.001 or item.y + h > BOARD_H + 0.001:
            errors.append(f"{name}: {item.instance} is outside the 75x150-mm board")
        for hole in HOLES:
            if hits_hole(rectangle, hole):
                errors.append(f"{name}: {item.instance} enters the M2.5 keep-out at {hole}")
    for index, (left, left_box) in enumerate(rectangles):
        for right, right_box in rectangles[index + 1:]:
            if overlaps(left_box, right_box, 0.7):
                errors.append(f"{name}: {left.instance} overlaps {right.instance}")
    return errors


def validate() -> list[str]:
    devices, candidate, instances = load()
    errors: list[str] = []
    required = {
        "s3": "ESP32-S3-WROOM-1U-N16R2",
        "c5": "ESP32-C5-WROOM-1U-N8R8",
        "rp": "SC1512-A4",
        "display": "HMX035CTFT-001 (QDtech schematic assembly marking)",
        "u214": "M5Stack U214 Cap LoRa-1262",
        "pack_holder": "Keystone Electronics 1048P",
    }
    for instance, expected in required.items():
        actual = devices[instances[instance]]["mpn"]
        if actual != expected:
            errors.append(f"{instance}: expected {expected}, got {actual}")

    errors += validate_items("ui-inner", UI_INNER, devices, instances)
    errors += validate_items("rf-inner", RF_INNER, devices, instances)
    errors += validate_items("front-controls", FRONT_CONTROLS, devices, instances)
    display = Placement("display", 10.25, 8.0, "display")
    holder = Placement("pack_holder", 17.6, 42.0, "battery holder", 90)
    speaker = Placement("speaker", 12.0, 133.0, "speaker")
    errors += validate_items("front-display", (display,), devices, instances)
    errors += validate_items("rear-exact", (holder, speaker), devices, instances)

    u214_dims = devices[instances["u214"]]["dimensions_mm"]
    if u214_dims[:2] != [84.0, 24.0]:
        errors.append("U214 must use the official 84x24-mm plan envelope")
    holder_w, holder_h = placement_size(holder, devices, instances)
    u214_box = (U214_X, U214_Y, U214_W, U214_H)
    if overlaps(u214_box, (holder.x, holder.y, holder_w, holder_h), U214_CLEARANCE):
        errors.append("full U214 envelope lacks 0.7-mm clearance to the Keystone holder")
    for hole in HOLES:
        if hits_hole(u214_box, hole, U214_CLEARANCE):
            errors.append(f"full U214 envelope lacks 0.7-mm clearance to the M2.5 keep-out at {hole}")

    machine_paths = set(candidate["antenna_policy"]["base_onboard_sma_paths"])
    drawn_paths = {path for _, path, _ in FRONT_RF + REAR_RF}
    if machine_paths != drawn_paths or len(drawn_paths) != 9:
        errors.append("mechanical projection must retain all nine unique onboard RF paths")
    if len(TX_RF_PATHS) != 7 or not TX_RF_PATHS <= drawn_paths:
        errors.append("seven transmitting RF paths must retain individual TX indicators")
    display_box = (display.x, display.y, *placement_size(display, devices, instances))
    for bank_name, bank in (("front", FRONT_RF), ("rear", REAR_RF)):
        bodies = [(centre - RF_BODY_W / 2, 0.0, RF_BODY_W, RF_BODY_D) for centre, _, _ in bank]
        for index, (centre, _, _) in enumerate(bank):
            body = bodies[index]
            for hole in HOLES:
                if hits_hole(body, hole):
                    errors.append(f"{bank_name}: RF connector at x={centre} enters mounting keep-out")
            for other, _, _ in bank[index + 1:]:
                if abs(centre - other) < RF_BODY_W + 0.7:
                    errors.append(f"{bank_name}: RF connector bodies overlap at {centre}/{other}")
        bank_leds = []
        for _, path, _ in bank:
            if path not in TX_RF_PATHS:
                continue
            led_box = TX_LED_BOXES[path]
            bank_leds.append((path, led_box))
            led_mpn = devices[instances[TX_LED_INSTANCES[path]]]["mpn"]
            led_dims = devices[instances[TX_LED_INSTANCES[path]]]["dimensions_mm"][:2]
            if led_mpn != "LTST-C190KRKT" or led_dims != [TX_LED_W, TX_LED_H]:
                errors.append(f"{path}: TX indicator must retain exact LTST-C190KRKT geometry")
            if any(overlaps(led_box, body, 0.7) for body in bodies):
                errors.append(f"{bank_name}: {path} TX indicator lacks 0.7-mm RF-body clearance")
            if any(hits_hole(led_box, hole, 0.7) for hole in HOLES):
                errors.append(f"{bank_name}: {path} TX indicator enters a mounting keep-out")
            if bank_name == "front" and overlaps(led_box, display_box, 0.7):
                errors.append(f"front: {path} TX indicator lacks 0.7-mm display clearance")
            if bank_name == "rear" and overlaps(led_box, u214_box, 0.7):
                errors.append(f"rear: {path} TX indicator lacks 0.7-mm U214 clearance")
        for index, (path, led_box) in enumerate(bank_leds):
            for other_path, other_box in bank_leds[index + 1:]:
                if overlaps(led_box, other_box, 0.7):
                    errors.append(f"{bank_name}: {path}/{other_path} TX indicators overlap")

    control_roles = {item.role for item in FRONT_CONTROLS}
    for role in ("physical hard STOP", "independent PTT", "F1", "F2", "recessed RE-ARM"):
        if role not in control_roles:
            errors.append(f"front controls omit {role}")
    return errors


def helpers(scale: float):
    def sx(origin, mm):
        return origin[0] + mm * scale

    def sy(origin, mm):
        return origin[1] + mm * scale

    def text(x, y, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{colour}">{html.escape(value)}</text>'
        )

    def rect(origin, x, y, w, h, fill, stroke, dash="", rx=2.0):
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{sx(origin,x):.1f}" y="{sy(origin,y):.1f}" '
            f'width="{w*scale:.1f}" height="{h*scale:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dashed}/>'
        )

    return sx, sy, text, rect


def board(origin, title, scale, sx, sy, text, rect):
    rows = [
        text(origin[0], origin[1] - RF_BARREL_OUT*scale - 22, title, 15, "bold"),
        rect(origin, 0, 0, BOARD_W, BOARD_H, "#f8fafc", "#344054", rx=5),
    ]
    for hx, hy in HOLES:
        rows.append(
            f'<circle cx="{sx(origin,hx):.1f}" cy="{sy(origin,hy):.1f}" '
            f'r="{MOUNT_KEEPOUT_R*scale:.1f}" fill="#fff7ed" stroke="#fb923c" '
            f'stroke-width="1" stroke-dasharray="4 3"/>'
        )
        rows.append(
            f'<circle cx="{sx(origin,hx):.1f}" cy="{sy(origin,hy):.1f}" '
            f'r="{MOUNT_HOLE_D*scale/2:.1f}" fill="white" stroke="#475467" stroke-width="1.4"/>'
        )
    return rows


def rf_bank(origin, bank, scale, sx, sy, text, rect, show_body):
    rows = []
    for centre, path, polarity in bank:
        if show_body:
            rows.append(rect(origin, centre-RF_BODY_W/2, 0, RF_BODY_W, RF_BODY_D, "#eef2f6", "#667085", rx=2))
        x = sx(origin, centre)
        edge_y = sy(origin, 0)
        barrel_top = edge_y - RF_BARREL_OUT * scale
        rows.append(
            f'<rect x="{x-RF_BARREL_D*scale/2:.1f}" y="{barrel_top:.1f}" '
            f'width="{RF_BARREL_D*scale:.1f}" height="{RF_BARREL_OUT*scale:.1f}" '
            f'fill="#d0d5dd" stroke="#344054" stroke-width="1.2"/>'
        )
        nut_r = 4.0 * scale
        points = []
        for number in range(6):
            angle = math.radians(60*number + 30)
            points.append(f"{x+nut_r*math.cos(angle):.1f},{edge_y+nut_r*math.sin(angle):.1f}")
        rows.append(f'<polygon points="{" ".join(points)}" fill="#e4e7ec" stroke="#344054" stroke-width="1.2"/>')
        rows.append(f'<path d="M{x:.1f} {barrel_top+2:.1f} V{barrel_top-12:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        rows.append(text(x, sy(origin, 15.5), path, 6.2, "bold", "middle", "#1d4ed8"))
        rows.append(text(x, sy(origin, 18.2), polarity, 5.2, anchor="middle", colour="#526076"))
        if path in TX_RF_PATHS:
            led_x, led_y, led_w, led_h = TX_LED_BOXES[path]
            rows.append(rect(origin, led_x, led_y, led_w, led_h, "#ef4444", "#991b1b", rx=1))
            rows.append(text(sx(origin,led_x + led_w/2), sy(origin,led_y - 0.35), "TX", 4.7, "bold", "middle", "#991b1b"))
    return rows


def render_external(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)
    front, rear = (80.0, 150.0), (465.0, 150.0)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1370" height="790" viewBox="0 0 1370 790">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30, 32, "Leshy2 — dimensioned external layout", 22, "bold"),
        text(30, 56, "One millimetre scale; orange dashed shapes are reserves, not selected-MPN geometry.", 11, colour="#526076"),
    ]
    out += board(front, "Front / UI face", scale, sx, sy, text, rect)
    out += board(rear, "Rear / battery and expansion face", scale, sx, sy, text, rect)

    # The installed Cap is a full-size external envelope. Draw it beneath the
    # RF-port annotation layer so it cannot hide port identity or TX evidence.
    out.append(rect(rear, U214_X, U214_Y, U214_W, U214_H, "#ffedd5", "#ea580c", rx=6))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 12.5), "M5Stack U214 · exact 84×24-mm plan envelope", 7.3, "bold", "middle", "#9a3412"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 17.0), "rear insertion / removal ⊙", 6.2, anchor="middle", colour="#dc2626"))
    out += rf_bank(front, FRONT_RF, scale, sx, sy, text, rect, False)
    out += rf_bank(rear, REAR_RF, scale, sx, sy, text, rect, False)

    display = Placement("display", 10.25, 8.0, "display")
    dw, dh = placement_size(display, devices, instances)
    out.append(rect(front, display.x, display.y, dw, dh, "#dbeafe", "#2563eb", rx=5))
    out.append(text(sx(front,37.5), sy(front,55), "HMX035CTFT-001", 9, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,60), "54.5×101.5-mm reference envelope", 6.5, anchor="middle", colour="#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,65), "touch / view ⊗", 6.5, anchor="middle", colour="#dc2626"))

    for item in FRONT_CONTROLS:
        w, h = placement_size(item, devices, instances)
        is_stop = item.instance == "stop_switch"
        out.append(rect(front, item.x, item.y, w, h, "#fee4e2" if is_stop else "#ede9fe", "#b42318" if is_stop else "#7c3aed", rx=2))
    for reserve in CAP_RESERVES:
        out.append(rect(front, reserve.x, reserve.y, reserve.w, reserve.h, "none", "#ea580c", "4 3", 3))
    labels = (
        (15.6,120,"STOP"),(16.1,136,"PTT"),(26.1,118,"BACK"),(26.1,135,"F1"),
        (37.5,118,"↑"),(31.6,127.5,"←"),(37.5,127.5,"OK"),(43.4,127.5,"→"),
        (37.5,137,"↓"),(53.1,118,"OPT"),(53.1,135,"F2"),(64.5,121,"ENC"),
        (65.1,135,"RE-ARM"),
    )
    for x, y, label in labels:
        out.append(text(sx(front,x), sy(front,y), label, 5.2, "bold", "middle", "#b42318" if label == "STOP" else "#4c1d95"))

    # Edge interfaces remain visible on the product projection. Their full
    # bodies live on the inner-board drawing; here the arrows show access.
    for y, label in ((76.5, "IR 38k RX"), (83.5, "IR raw RX"), (90.5, "IR TX")):
        out.append(rect(front, 0, y-1.5, 3.2, 3.0, "#fef3c7", "#d97706", rx=2))
        out.append(f'<path d="M{sx(front,0):.1f} {sy(front,y):.1f} L{sx(front,-7):.1f} {sy(front,y):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(text(sx(front,4.0), sy(front,y+0.7), label, 4.8, "bold", colour="#92400e"))
    out.append(f'<circle cx="{sx(front,4.5):.1f}" cy="{sy(front,94):.1f}" r="{1.1*scale:.1f}" fill="#ef4444" stroke="#991b1b"/>')
    out.append(text(sx(front,6.2), sy(front,95), "IR actual TX", 4.8, "bold", colour="#991b1b"))
    out.append(f'<path d="M{sx(front,75):.1f} {sy(front,79.8):.1f} L{sx(front,82):.1f} {sy(front,79.8):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    out.append(text(sx(front,71.5), sy(front,78.2), "3.5 mm", 4.8, "bold", "middle", "#1d4ed8"))
    for x, label in ((31.5, "C5 USB"), (44.0, "MIC"), (56.0, "microSD")):
        out.append(f'<path d="M{sx(front,x):.1f} {sy(front,150):.1f} L{sx(front,x):.1f} {sy(front,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(text(sx(front,x), sy(front,148), label, 4.6, "bold", "middle", "#1d4ed8"))

    holder = Placement("pack_holder", 17.6, 42.0, "holder", 90)
    hw, hh = placement_size(holder, devices, instances)
    out.append(rect(rear, holder.x, holder.y, hw, hh, "#dcfce7", "#16a34a", rx=10))
    out.append(text(sx(rear,37.5), sy(rear,82), "Keystone 1048P", 9, "bold", "middle", "#166534"))
    out.append(text(sx(rear,37.5), sy(rear,87), "86×39.8-mm rotated holder", 6.5, anchor="middle", colour="#166534"))
    for cell_x in (28.0, 47.0):
        out.append(rect(rear, cell_x-9.3, 52.0, 18.6, 65.0, "#ecfdf3", "#22c55e", rx=20))
        out.append(text(sx(rear,cell_x), sy(rear,86), "18650", 7, "bold", "middle", "#166534"))

    speaker = Placement("speaker", 12.0, 133.0, "speaker")
    sw, sh = placement_size(speaker, devices, instances)
    out.append(rect(rear, speaker.x, speaker.y, sw, sh, "#dbeafe", "#2563eb", rx=8))
    out.append(text(sx(rear,24), sy(rear,140), "AS02404PO · sound ⊙", 5.8, "bold", "middle", "#1d4ed8"))
    out.append(rect(rear, 48, 133, 18, 8, "#fff7ed", "#ea580c", "5 3", 3))
    out.append(text(sx(rear,57), sy(rear,138), "M5 Unit · MPN TBD", 5.6, "bold", "middle", "#9a3412"))
    out.append(f'<path d="M{sx(rear,57):.1f} {sy(rear,141):.1f} V{sy(rear,148):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    for x, label in ((16.5, "USB/PWR"), (37.5, "RP USB")):
        out.append(f'<path d="M{sx(rear,x):.1f} {sy(rear,150):.1f} V{sy(rear,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(text(sx(rear,x), sy(rear,148), label, 4.8, "bold", "middle", "#1d4ed8"))

    note_x = 850
    out += [
        text(note_x,105,"What this drawing proves",16,"bold"),
        text(note_x,135,"• both 75×150-mm panels use the same millimetre scale",11),
        text(note_x,158,"• every solid component envelope comes from the MPN register",11),
        text(note_x,181,"• full U214 and Keystone holder envelopes do not overlap",11),
        text(note_x,204,"• exact components clear all M2.5 hole/head keep-outs",11),
        text(note_x,245,"Interface direction",15,"bold"),
        text(note_x,273,"↑ / ↓ / ← / →  interface faces through that enclosure edge",11),
        text(note_x,296,"⊗  touch/press enters face     ⊙  sound/module leaves face",11),
        text(note_x,337,"TX indication",15,"bold"),
        '<circle cx="858" cy="360" r="5" fill="#ef4444" stroke="#991b1b"/>',
        text(875,364,"physical actual-TX evidence for each transmitting path",11),
        text(note_x,386,"S3, C5, 3×nRF24, CC and voice get antenna-local indicators.",11),
        text(note_x,409,"IR gets its own indicator; the two Si4732 ports are RX-only.",11),
        text(note_x,450,"Geometry status",15,"bold"),
        '<rect x="850" y="467" width="28" height="15" rx="3" fill="#eef2f6" stroke="#667085"/>',
        text(890,479,"solid — registered MPN/reference assembly envelope",11),
        '<rect x="850" y="497" width="28" height="15" rx="3" fill="none" stroke="#ea580c" stroke-dasharray="5 3"/>',
        text(890,509,"dashed — reserved space; exact MPN is not selected",11),
        text(note_x,550,"RF connectors are barrels with hex nuts, not circles.",11,"bold"),
        text(note_x,573,"SMA: GCT RFPC-SMA31-FN-175-A · 6 GHz · IP67 · 1.6-mm PCB.",11),
        text(note_x,593,"RP-SMA: GCT RFPC-SMA32-FN-175-A · same panel cut-out.",11),
        text(note_x,614,"Dimensioned projection — not an enclosure release drawing.",11,"bold",colour="#b42318"),
        text(note_x,637,"Caps/knob, enclosure wall stack and internal cable lengths remain open.",11),
        text(note_x,670,"Controls retain D-pad + OK, BACK, OPT, F1/F2, PTT, STOP and RE-ARM.",11,"bold"),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_internal(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)
    ui, rf = (80.0, 150.0), (465.0, 150.0)
    all_items = UI_INNER + RF_INNER
    numbers = {item.instance: index for index, item in enumerate(all_items, 1)}
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="800" viewBox="0 0 1510 800">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30,32,"Leshy2 — dimensioned inner-board placement",22,"bold"),
        text(30,56,"Every grey rectangle is one device at registered MPN size; reserves are orange and dashed.",11,colour="#526076"),
    ]
    out += board(ui, "UI/control PCB — inner side", scale, sx, sy, text, rect)
    out += board(rf, "RF/power PCB — inner side", scale, sx, sy, text, rect)
    out += rf_bank(ui, FRONT_RF, scale, sx, sy, text, rect, True)
    out += rf_bank(rf, REAR_RF, scale, sx, sy, text, rect, True)
    for origin, items in ((ui, UI_INNER), (rf, RF_INNER)):
        for item in items:
            w, h = placement_size(item, devices, instances)
            out.append(rect(origin, item.x, item.y, w, h, "#eef2f6", "#667085", rx=2))
            out.append(text(sx(origin,item.x+w/2), sy(origin,item.y+h/2)+3, str(numbers[item.instance]), 7.5, "bold", "middle"))

    arrows = (
        (ui,0,76.5,-10,76.5),(ui,0,83.5,-10,83.5),(ui,0,90.5,-10,90.5),
        (ui,75,79.8,85,79.8),(ui,31.5,150,31.5,159),
        (ui,44,150,44,159),(ui,56,150,56,159),(rf,16.5,150,16.5,159),
        (rf,37.5,150,37.5,159),
    )
    for origin, x1, y1, x2, y2 in arrows:
        out.append(f'<path d="M{sx(origin,x1):.1f} {sy(origin,y1):.1f} L{sx(origin,x2):.1f} {sy(origin,y2):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')

    left_x, right_x = 830, 1165
    out += [text(left_x,105,"Numbered physical devices",16,"bold"), text(left_x,128,"UI/control PCB",12,"bold",colour="#1d4ed8")]
    y = 148
    for item in UI_INNER:
        mpn = devices[instances[item.instance]]["mpn"].replace(" (QDtech schematic assembly marking)", "")
        out.append(text(left_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(left_x+26,y+9,item.role,7.2,colour="#526076"))
        y += 21
    out.append(text(right_x,128,"RF/power PCB",12,"bold",colour="#c2410c"))
    y = 148
    for item in RF_INNER:
        mpn = devices[instances[item.instance]]["mpn"]
        out.append(text(right_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(right_x+26,y+9,item.role,7.2,colour="#526076"))
        y += 21
    out += [
        text(left_x,560,"Validated clearances",14,"bold"),
        text(left_x,584,"• device-to-device: ≥0.7 mm in this projection",10),
        text(left_x,605,"• M2.5 hole/head keep-out: 4.0-mm radius",10),
        text(left_x,626,"• every edge interface has an outward direction arrow",10),
        text(left_x,647,"• microSD is edge-accessible; C5 USB stays with C5",10),
        text(left_x,668,"SMA · GCT RFPC-SMA31-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,688,"RP-SMA · GCT RFPC-SMA32-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,714,"Only unselected RF cable bodies remain physical reserves.",9.2,"bold",colour="#9a3412"),
        text(left_x,737,"Placement projection; passives, copper and enclosure stack are omitted.",9.2,colour="#526076"),
    ]
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
    devices, _, instances = load()
    outputs = {
        EXTERNAL_OUTPUT: render_external(devices, instances),
        INTERNAL_OUTPUT: render_internal(devices, instances),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    if args.check:
        stale = [path.relative_to(REPO) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"error: stale {path}")
            return 1
        print("ok: external and internal mechanical projections are valid and current")
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
