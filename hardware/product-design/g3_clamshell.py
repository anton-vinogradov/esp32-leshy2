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
SANDWICH_OUTPUT = REPO / "docs/images/sandwich-section.svg"

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
TX_LED_INSTANCES = {
    "S3-2G4": "s3_tx_led",
    "C5-2G4/5": "c5_tx_led",
    "N24-0": "nrf0_tx_led",
    "CC-SUB": "cc_tx_led",
    "N24-1": "nrf1_tx_led",
    "VOICE-V/U": "voice_tx_led",
    "N24-2": "nrf2_tx_led",
}
FRONT_TX_INDICATORS = (
    ("s3_tx_led", "S3", 4.0, 115.0),
    ("c5_tx_led", "C5", 12.3, 115.0),
    ("nrf0_tx_led", "N24-0", 20.6, 115.0),
    ("nrf1_tx_led", "N24-1", 28.9, 115.0),
    ("nrf2_tx_led", "N24-2", 37.2, 115.0),
    ("cc_tx_led", "CC", 45.5, 115.0),
    ("voice_tx_led", "VOICE", 53.8, 115.0),
    ("ir_tx_led", "IR", 62.1, 115.0),
    ("any_tx_led", "ANY TX", 70.4, 115.0),
)

# Every interface that crosses the enclosure is rendered from this inventory.
# `coordinate` is Y for left/right exits and X for bottom exits.
EDGE_INTERFACES = (
    ("ir_demod", "front", "left", 76.5, "IR 38 kHz RX"),
    ("ir_carrier", "front", "left", 83.5, "IR raw RX"),
    ("ir_emitter", "front", "left", 90.255, "IR TX"),
    ("headphone_jack", "front", "right", 79.75, "HEADPHONES / LINE"),
    ("c5_service_usb_connector", "front", "bottom", 31.47, "C5 SERVICE USB"),
    ("microphone", "front", "bottom", 44.0, "MICROPHONE"),
    ("sd", "front", "bottom", 55.975, "microSD"),
    ("speaker", "rear", "left", 109.0, "SPEAKER GRILLE"),
    ("power_command_switch", "rear", "right", 112.75, "POWER ON/OFF"),
    ("product_usb_connector", "rear", "bottom", 16.47, "USB / POWER"),
    ("rp_service_usb_connector", "rear", "bottom", 37.47, "RP SERVICE USB"),
    ("unit_connector", "rear", "bottom", 57.0, "M5 UNIT"),
)

# External side projections show only real silkscreen labels and an enclosure
# direction arrow.  They must not invent a visible button/socket body on the
# face, and the front labels must fit wholly in the two gutters beside the
# display envelope.
SIDE_INTERFACE_LABEL_LINES = {
    "ir_demod": ("IR 38 kHz RX",),
    "ir_carrier": ("IR RAW RX",),
    "ir_emitter": ("IR TX",),
    "headphone_jack": ("HEADPHONES", "LINE OUT"),
    "speaker": ("SPEAKER", "GRILLE"),
    "power_command_switch": ("POWER", "ON / OFF"),
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
    Placement("s3_dbg_header", 5.0, 104.0, "keyed S3 UART0/RESET/BOOT header"),
    Placement("s3_reset_button", 16.0, 104.0, "S3 technological RESET"),
    Placement("s3_boot_button", 24.0, 104.0, "S3 technological BOOT"),
    Placement("c5_dbg_header", 47.0, 104.0, "keyed C5 UART0/RESET/BOOT header"),
    Placement("c5_reset_button", 58.0, 104.0, "C5 technological RESET"),
    Placement("c5_boot_button", 66.0, 104.0, "C5 technological BOOT"),
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
    Placement("unit_connector", 51.0, 140.9, "native M5 Unit HY2.0-4P edge receptacle"),
    Placement("speaker", 5.0, 103.0, "internal 4-Ohm differential speaker"),
    Placement("rp_dbg_header", 40.0, 104.0, "keyed RP SWD/RUN/USB_BOOT header"),
    Placement("rp_reset_button", 51.0, 104.0, "RP technological RUN/RESET"),
    Placement("rp_boot_button", 59.5, 104.0, "RP technological USB_BOOT"),
    Placement("power_command_switch", 65.8, 111.0, "low-current ON/OFF command; charging remains available"),
)

FRONT_CONTROLS = (
    Placement("ui_switch_back", 18.0, 136.0, "BACK"),
    Placement("ui_switch_up", 35.4, 130.0, "D-pad up"),
    Placement("ui_switch_left", 29.5, 136.0, "D-pad left"),
    Placement("ui_switch_ok", 35.4, 136.0, "D-pad OK"),
    Placement("ui_switch_right", 41.3, 136.0, "D-pad right"),
    Placement("ui_switch_down", 35.4, 142.0, "D-pad down"),
    Placement("ui_switch_opt", 52.8, 136.0, "OPT"),
)

REAR_CONTROLS = (
    Placement("encoder", 2.5, 45.0, "rear encoder above F1/F2"),
    Placement("ui_switch_f1", 5.5, 65.0, "rear F1"),
    Placement("ui_switch_f2", 5.5, 80.0, "rear F2"),
    Placement("ptt_switch", 65.3, 65.0, "rear independent PTT"),
    Placement("stop_switch", 59.5, 77.0, "rear physical hard STOP"),
    Placement("rearm_switch", 65.3, 97.0, "rear recessed RE-ARM"),
)

FRONT_CAP_RESERVES = (
    Reserve("BACK cap", 16.6, 133.9, 7.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("single D-pad cross", 28.8, 127.5, 17.4, 19.0, "one moulded D-pad cap over five switches, MPN TBD"),
    Reserve("OPT cap", 51.4, 133.9, 7.0, 7.0, "cap/case feature, MPN TBD"),
)

REAR_CAP_RESERVES = (
    Reserve("encoder knob", 0.5, 43.0, 15.0, 15.0, "knob/case feature, MPN TBD"),
    Reserve("F1 cap", 4.0, 63.0, 7.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("F2 cap", 4.0, 78.0, 7.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("PTT cap", 64.0, 63.0, 7.0, 7.0, "cap/case feature, MPN TBD"),
    Reserve("STOP cap", 64.0, 78.0, 7.0, 7.0, "same visible size as PTT/F1/F2; NC body below"),
    Reserve("RE-ARM cap", 64.0, 96.0, 7.0, 7.0, "recessed cap/case feature, MPN TBD"),
)

INTERNAL_RESERVES = ()


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


def mirrored_x(x: float, width: float = 0.0) -> float:
    """Mirror a point or left edge across the 75-mm board centreline."""
    return BOARD_W - x - width


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


def validate_reserves(name: str, reserves: tuple[Reserve, ...]) -> list[str]:
    errors: list[str] = []
    for reserve in reserves:
        rectangle = (reserve.x, reserve.y, reserve.w, reserve.h)
        if reserve.x < 0 or reserve.y < 0 or reserve.x + reserve.w > BOARD_W or reserve.y + reserve.h > BOARD_H:
            errors.append(f"{name}: {reserve.name} is outside the 75x150-mm board")
        for hole in HOLES:
            if hits_hole(rectangle, hole):
                errors.append(f"{name}: {reserve.name} enters the M2.5 keep-out at {hole}")
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
        "unit_connector": "1125R-SMT-4P",
    }
    for instance, expected in required.items():
        actual = devices[instances[instance]]["mpn"]
        if actual != expected:
            errors.append(f"{instance}: expected {expected}, got {actual}")

    errors += validate_items("ui-inner", UI_INNER, devices, instances)
    errors += validate_items("rf-inner", RF_INNER, devices, instances)
    errors += validate_items("front-controls", FRONT_CONTROLS, devices, instances)
    errors += validate_items("rear-controls", REAR_CONTROLS, devices, instances)
    errors += validate_reserves("front-caps", FRONT_CAP_RESERVES)
    errors += validate_reserves("rear-caps", REAR_CAP_RESERVES)
    errors += validate_reserves("internal-reserves", INTERNAL_RESERVES)
    display = Placement("display", 10.25, 11.0, "display")
    holder = Placement("pack_holder", 17.6, 42.0, "battery holder", 90)
    errors += validate_items("front-display", (display,), devices, instances)
    errors += validate_items("rear-exact", (holder,), devices, instances)

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
    indicator_boxes = []
    for instance, label, x, y in FRONT_TX_INDICATORS:
        led_box = (x, y, TX_LED_W, TX_LED_H)
        indicator_boxes.append((label, led_box))
        led_mpn = devices[instances[instance]]["mpn"]
        led_dims = devices[instances[instance]]["dimensions_mm"][:2]
        if led_mpn != "LTST-C190KRKT" or led_dims != [TX_LED_W, TX_LED_H]:
            errors.append(f"{label}: TX indicator must retain exact LTST-C190KRKT geometry")
        if overlaps(led_box, display_box, 0.7):
            errors.append(f"front: {label} TX indicator lacks 0.7-mm display clearance")
        if any(hits_hole(led_box, hole, 0.7) for hole in HOLES):
            errors.append(f"front: {label} TX indicator enters a mounting keep-out")
    for index, (label, led_box) in enumerate(indicator_boxes):
        for other_label, other_box in indicator_boxes[index + 1:]:
            if overlaps(led_box, other_box, 0.7):
                errors.append(f"front: {label}/{other_label} TX indicators overlap")
    if len({y for _, _, _, y in FRONT_TX_INDICATORS}) != 1:
        errors.append("front: all nine TX indicators must remain in one horizontal line")
    edge_instances = {item.instance for item in UI_INNER + RF_INNER}
    edge_placements = {item.instance: item for item in UI_INNER + RF_INNER}
    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if instance not in edge_instances:
            errors.append(f"external interface {label}: source instance {instance} is not placed")
        if face not in {"front", "rear"} or side not in {"left", "right", "bottom"}:
            errors.append(f"external interface {label}: invalid face/side")
        if not label.strip() or not 0 <= coordinate <= BOARD_H:
            errors.append(f"external interface {instance}: label/coordinate is invalid")
        if instance in edge_placements:
            item = edge_placements[instance]
            w, h = placement_size(item, devices, instances)
            component_centre = item.x + w / 2 if side == "bottom" else item.y + h / 2
            if abs(coordinate - component_centre) > 0.051:
                errors.append(
                    f"external interface {label}: label centre {coordinate:.3f} does not "
                    f"match {instance} centre {component_centre:.3f}"
                )
    if len({label for _, _, _, _, label in EDGE_INTERFACES}) != len(EDGE_INTERFACES):
        errors.append("external interface labels must be unique")

    control_roles = {item.role for item in REAR_CONTROLS}
    for role in ("rear physical hard STOP", "rear independent PTT", "rear F1", "rear F2", "rear recessed RE-ARM"):
        if role not in control_roles:
            errors.append(f"rear controls omit {role}")
    rear_exact_boxes = []
    for item in REAR_CONTROLS:
        rear_exact_boxes.append((item.instance, (item.x, item.y, *placement_size(item, devices, instances))))
    holder_box = (holder.x, holder.y, holder_w, holder_h)
    for instance, rectangle in rear_exact_boxes:
        if overlaps(rectangle, holder_box, 0.7):
            errors.append(f"rear: {instance} lacks 0.7-mm clearance to the battery holder")
        if overlaps(rectangle, u214_box, 0.7):
            errors.append(f"rear: {instance} lacks 0.7-mm clearance to U214")
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


def rf_bank(origin, bank, scale, sx, sy, text, rect, show_body, compact_labels=False, mirror=False):
    rows = []
    for source_centre, path, polarity in bank:
        centre = mirrored_x(source_centre) if mirror else source_centre
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
        label_y = 9.0 if compact_labels else 15.5
        visible_label = f"{path} · {polarity}" if compact_labels else path
        rows.append(text(x, sy(origin, label_y), visible_label, 4.2 if compact_labels else 6.2, "bold", "middle", "#1d4ed8"))
        if not compact_labels:
            rows.append(text(x, sy(origin, 18.2), polarity, 5.2, anchor="middle", colour="#526076"))
    return rows


def dpad_cap(origin, scale, sx, sy, text):
    """Draw one moulded D-pad cap; the five switches below remain separate parts."""
    cx, cy = sx(origin, 37.5), sy(origin, 137.0)
    arm, half = 6.6 * scale, 2.4 * scale
    points = (
        (cx - half, cy - arm), (cx + half, cy - arm),
        (cx + half, cy - half), (cx + arm, cy - half),
        (cx + arm, cy + half), (cx + half, cy + half),
        (cx + half, cy + arm), (cx - half, cy + arm),
        (cx - half, cy + half), (cx - arm, cy + half),
        (cx - arm, cy - half), (cx - half, cy - half),
    )
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return [
        f'<polygon points="{path}" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.7"/>',
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{2.0*scale:.1f}" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>',
        text(cx, cy + 2.0, "OK", 5.0, "bold", "middle", "#4c1d95"),
    ]


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
    out += rf_bank(rear, REAR_RF, scale, sx, sy, text, rect, False, True)

    display = Placement("display", 10.25, 11.0, "display")
    dw, dh = placement_size(display, devices, instances)
    out.append(rect(front, display.x, display.y, dw, dh, "#dbeafe", "#2563eb", rx=5))
    out.append(text(sx(front,37.5), sy(front,55), "HMX035CTFT-001", 9, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,60), "54.5×101.5-mm reference envelope", 6.5, anchor="middle", colour="#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,65), "touch / view ⊗", 6.5, anchor="middle", colour="#dc2626"))
    out += rf_bank(front, FRONT_RF, scale, sx, sy, text, rect, False, True)

    for instance, label, x, y in FRONT_TX_INDICATORS:
        out.append(rect(front, x, y, TX_LED_W, TX_LED_H, "#ef4444", "#991b1b", rx=1))
        out.append(text(sx(front,x + TX_LED_W/2), sy(front,y + 2.6), label, 4.2, "bold", "middle", "#991b1b"))

    for reserve in FRONT_CAP_RESERVES:
        out.append(rect(front, reserve.x, reserve.y, reserve.w, reserve.h, "#f5f3ff", "#ea580c", "4 3", 3))
    out += dpad_cap(front, scale, sx, sy, text)
    out.append(text(sx(front,20.1), sy(front,145.0), "BACK", 5.0, "bold", "middle", "#4c1d95"))
    out.append(text(sx(front,54.9), sy(front,145.0), "OPT", 5.0, "bold", "middle", "#4c1d95"))

    # Every side/bottom interface is projected onto the external face even
    # when its physical body is mounted on the inward PCB side.
    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if face != "front" or side not in {"left", "right"}:
            continue
        stroke = "#d97706" if instance.startswith("ir_") else "#2563eb"
        start_x, end_x = (0.0, -7.0) if side == "left" else (75.0, 82.0)
        out.append(f'<path d="M{sx(front,start_x):.1f} {sy(front,coordinate):.1f} L{sx(front,end_x):.1f} {sy(front,coordinate):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        # Display spans x=10.25..64.75 mm; these are the exact centres of
        # the remaining equal 10.25-mm silkscreen gutters.
        label_x = 5.125 if side == "left" else 69.875
        lines = SIDE_INTERFACE_LABEL_LINES[instance]
        first_y = coordinate - 1.3 * (len(lines) - 1)
        for line_index, line in enumerate(lines):
            out.append(text(sx(front,label_x), sy(front,first_y + 2.6 * line_index), line, 4.2, "bold", "middle", stroke))
    for _, face, side, x, label in EDGE_INTERFACES:
        if face != "front" or side != "bottom":
            continue
        out.append(f'<path d="M{sx(front,x):.1f} {sy(front,150):.1f} L{sx(front,x):.1f} {sy(front,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(text(sx(front,x), sy(front,148), label, 4.2, "bold", "middle", "#1d4ed8"))

    holder = Placement("pack_holder", 17.6, 42.0, "holder", 90)
    hw, hh = placement_size(holder, devices, instances)
    out.append(rect(rear, holder.x, holder.y, hw, hh, "#dcfce7", "#16a34a", rx=10))
    out.append(text(sx(rear,37.5), sy(rear,82), "Keystone 1048P", 9, "bold", "middle", "#166534"))
    out.append(text(sx(rear,37.5), sy(rear,87), "86×39.8-mm rotated holder", 6.5, anchor="middle", colour="#166534"))
    for cell_x in (28.0, 47.0):
        out.append(rect(rear, cell_x-9.3, 52.0, 18.6, 65.0, "#ecfdf3", "#22c55e", rx=20))
        out.append(text(sx(rear,cell_x), sy(rear,86), "18650", 7, "bold", "middle", "#166534"))

    for reserve in REAR_CAP_RESERVES:
        out.append(rect(rear, reserve.x, reserve.y, reserve.w, reserve.h, "#fee4e2" if reserve.name == "STOP cap" else "#f5f3ff", "#ea580c", "4 3", 3))
    for x, y, label in (
        (7.5, 61.5, "ENC"), (7.5, 74.0, "F1"), (7.5, 89.0, "F2"),
        (67.5, 74.0, "PTT"), (67.5, 89.0, "STOP"), (67.5, 107.0, "RE-ARM"),
    ):
        out.append(text(sx(rear,x), sy(rear,y), label, 5.0, "bold", "middle", "#b42318" if label == "STOP" else "#4c1d95"))

    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if face != "rear" or side not in {"left", "right"}:
            continue
        stroke = "#2563eb" if instance == "speaker" else "#ea580c"
        start_x, end_x = (0.0, -7.0) if side == "left" else (75.0, 82.0)
        out.append(f'<path d="M{sx(rear,start_x):.1f} {sy(rear,coordinate):.1f} L{sx(rear,end_x):.1f} {sy(rear,coordinate):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        label_x = 5.0 if side == "left" else 70.0
        lines = SIDE_INTERFACE_LABEL_LINES[instance]
        first_y = coordinate - 1.3 * (len(lines) - 1)
        for line_index, line in enumerate(lines):
            out.append(text(sx(rear,label_x), sy(rear,first_y + 2.6 * line_index), line, 4.2, "bold", "middle", stroke))
    for _, face, side, x, label in EDGE_INTERFACES:
        if face != "rear" or side != "bottom":
            continue
        out.append(f'<path d="M{sx(rear,x):.1f} {sy(rear,150):.1f} V{sy(rear,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(text(sx(rear,x), sy(rear,148), label, 4.2, "bold", "middle", "#1d4ed8"))

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
        text(note_x,316,"The front uses one moulded single D-pad cap over five exact switches.",11),
        text(note_x,347,"TX indication",15,"bold"),
        '<circle cx="858" cy="370" r="5" fill="#ef4444" stroke="#991b1b"/>',
        text(875,374,"physical actual-TX evidence for each transmitting path",11),
        text(note_x,396,"Eight path indicators plus ANY TX form one front line below the display.",11),
        text(note_x,419,"Each is labelled S3/C5/N24-0..2/CC/VOICE/IR; Si4732 ports are RX-only.",11),
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
        text(note_x,670,"Front: one D-pad + BACK/OPT. Rear: ENC, F1/F2, PTT, STOP, RE-ARM.",11,"bold"),
        text(note_x,693,"STOP uses the same visible 7×7-mm cap as F1/F2/PTT over its NC safety body.",11),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_internal(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)
    ui, rf = (80.0, 150.0), (465.0, 150.0)
    all_items = UI_INNER + RF_INNER
    numbers = {item.instance: index for index, item in enumerate(all_items, 1)}
    legend_first_y = 148
    legend_row_height = 21
    legend_bottom = legend_first_y + (max(len(UI_INNER), len(RF_INNER)) - 1) * legend_row_height + 9
    notes_top = max(560, legend_bottom + 35)
    svg_height = notes_top + 230
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="{svg_height}" viewBox="0 0 1510 {svg_height}" data-view="mirrored-x">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30,32,"Leshy2 — dimensioned inner-board placement",22,"bold"),
        text(30,56,"Every solid rectangle is one device at registered MPN size; reserves are orange and dashed.",11,colour="#526076"),
    ]
    out += board(ui, "UI/control PCB — inner side", scale, sx, sy, text, rect)
    out += board(rf, "RF/power PCB — inner side", scale, sx, sy, text, rect)
    # Looking at either PCB's inner side means physically turning that board
    # over.  Therefore all X coordinates are mirrored relative to the matching
    # external face; this is not a transparent-through-board projection.
    out += rf_bank(ui, FRONT_RF, scale, sx, sy, text, rect, True, mirror=True)
    out += rf_bank(rf, REAR_RF, scale, sx, sy, text, rect, True, mirror=True)
    for origin, items in ((ui, UI_INNER), (rf, RF_INNER)):
        for item in items:
            w, h = placement_size(item, devices, instances)
            view_x = mirrored_x(item.x, w)
            if item.instance == "speaker":
                fill, stroke = "#dbeafe", "#2563eb"
            elif item.instance == "microphone":
                fill, stroke = "#fef3c7", "#d97706"
            elif item.instance.endswith(("_reset_button", "_boot_button")):
                fill, stroke = "#ede9fe", "#7c3aed"
            elif item.instance.endswith("_dbg_header"):
                fill, stroke = "#ccfbf1", "#0f766e"
            else:
                fill, stroke = "#eef2f6", "#667085"
            out.append(rect(origin, view_x, item.y, w, h, fill, stroke, rx=2))
            out.append(text(sx(origin,view_x+w/2), sy(origin,item.y+h/2)+3, str(numbers[item.instance]), 7.5, "bold", "middle"))
    for reserve in INTERNAL_RESERVES:
        view_x = mirrored_x(reserve.x, reserve.w)
        out.append(rect(rf, view_x, reserve.y, reserve.w, reserve.h, "none", "#ea580c", "5 3", 3))
        out.append(text(sx(rf,view_x+reserve.w/2), sy(rf,reserve.y+reserve.h/2)+2, "PWR", 5.0, "bold", "middle", "#9a3412"))

    arrows = []
    for _, face, side, coordinate, _ in EDGE_INTERFACES:
        origin = ui if face == "front" else rf
        if side == "left":
            arrows.append((origin, 0.0, coordinate, -10.0, coordinate))
        elif side == "right":
            arrows.append((origin, BOARD_W, coordinate, BOARD_W + 10.0, coordinate))
        else:
            arrows.append((origin, coordinate, BOARD_H, coordinate, BOARD_H + 9.0))
    for origin, x1, y1, x2, y2 in arrows:
        out.append(f'<path d="M{sx(origin,mirrored_x(x1)):.1f} {sy(origin,y1):.1f} L{sx(origin,mirrored_x(x2)):.1f} {sy(origin,y2):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    out.append(text(sx(ui,mirrored_x(44)), sy(ui,144.5), "MIC", 5.2, "bold", "middle", "#92400e"))
    out.append(text(sx(rf,mirrored_x(17)), sy(rf,101.5), "AS02404PO · side grille →", 4.8, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(rf,mirrored_x(73.5)), sy(rf,109.5), "ON/OFF request", 4.6, "bold", "start", "#9a3412"))
    out.append(text(sx(ui,mirrored_x(37.5)), sy(ui,101.5), "S3/C5 recovery controls and DBG10", 5.0, "bold", "middle", "#4c1d95"))
    out.append(text(sx(rf,mirrored_x(54.5)), sy(rf,101.5), "RP recovery controls and DBG10", 5.0, "bold", "middle", "#4c1d95"))

    left_x, right_x = 830, 1165
    out += [text(left_x,105,"Numbered physical devices",16,"bold"), text(left_x,128,"UI/control PCB",12,"bold",colour="#1d4ed8")]
    y = legend_first_y
    for item in UI_INNER:
        mpn = devices[instances[item.instance]]["mpn"].replace(" (QDtech schematic assembly marking)", "")
        out.append(text(left_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(left_x+26,y+9,item.role,7.2,colour="#526076"))
        y += legend_row_height
    out.append(text(right_x,128,"RF/power PCB",12,"bold",colour="#c2410c"))
    y = legend_first_y
    for item in RF_INNER:
        mpn = devices[instances[item.instance]]["mpn"]
        out.append(text(right_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(right_x+26,y+9,item.role,7.2,colour="#526076"))
        y += legend_row_height
    out += [
        f'<g id="validated-clearances" data-legend-bottom="{legend_bottom}" data-top="{notes_top}">',
        text(left_x,notes_top,"Validated clearances",14,"bold"),
        text(left_x,notes_top+24,"• device-to-device: ≥0.7 mm in this projection",10),
        text(left_x,notes_top+45,"• M2.5 hole/head keep-out: 4.0-mm radius",10),
        text(left_x,notes_top+66,"• both inner views are horizontally mirrored from their external faces",10),
        text(left_x,notes_top+87,"• every edge arrow is centred on its component (or an explicit reserve)",10),
        text(left_x,notes_top+108,"SMA · GCT RFPC-SMA31-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,notes_top+128,"RP-SMA · GCT RFPC-SMA32-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,notes_top+154,"Only unselected RF cable bodies remain physical reserves.",9.2,"bold",colour="#9a3412"),
        text(left_x,notes_top+175,"POWER command: C&K JS102011SCQN; low-current request only, never pack current.",9.2,"bold",colour="#9a3412"),
        text(left_x,notes_top+196,"Placement projection; passives, copper and enclosure stack are omitted.",9.2,colour="#526076"),
        "</g>",
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_sandwich(devices, instances):
    """Render the physical front-to-rear stack with exact selected-part depths."""

    def mpn(instance):
        return devices[instances[instance]]["mpn"].replace(" (QDtech schematic assembly marking)", "")

    def depth(instance):
        return float(devices[instances[instance]]["dimensions_mm"][2])

    def t(x, y, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    def r(x, y, w, h, fill, stroke, dash="", rx=2):
        dotted = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dotted}/>'
        )

    def arrow(x1, y1, x2, y2):
        return f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="#dc2626" stroke-width="1.7" marker-end="url(#arrow)"/>'

    z_scale = 12.0
    x0, top, height = 120.0, 125.0, 330.0
    shell = 1.5 * z_scale
    display_z = depth("display") * z_scale
    pcb_z = 1.6 * z_scale
    gap_z = 11.0 * z_scale
    cell_z = 18.6 * z_scale
    x_shell_front = x0
    x_display = x_shell_front + shell
    x_ui = x_display + display_z
    x_gap = x_ui + pcb_z
    x_rf = x_gap + gap_z
    x_cells = x_rf + pcb_z
    x_shell_rear = x_cells + cell_z
    total_nominal = depth("display") + 11.0 + 1.6 + 18.6

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="720" viewBox="0 0 1450 720">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 34, "Leshy2 — dimensioned front-to-rear sandwich", 22, "bold"),
        t(30, 58, "Depth uses exact registered part envelopes; enclosure walls and assembly tolerances remain reserves.", 11, colour="#526076"),
        t(x0 - 32, 105, "FRONT", 12, "bold", "middle", "#1d4ed8"),
        t(x_shell_rear + shell + 34, 105, "REAR", 12, "bold", "middle", "#166534"),
        r(x_shell_front, top, shell, height, "none", "#ea580c", "6 4", 2),
        r(x_display, top + 24, display_z, height - 48, "#dbeafe", "#2563eb", rx=3),
        r(x_ui, top, pcb_z, height, "#dcfce7", "#16a34a", rx=1),
        r(x_gap, top, gap_z, height, "#f8fafc", "#94a3b8", "5 4", 2),
        r(x_rf, top, pcb_z, height, "#ffedd5", "#ea580c", rx=1),
        r(x_cells, top + 38, cell_z, height - 76, "#ecfdf3", "#22c55e", rx=18),
        r(x_shell_rear, top, shell, height, "none", "#ea580c", "6 4", 2),
        t(x_display + display_z/2, top + height/2, "HMX035CTFT-001", 10, "bold", "middle", "#1d4ed8"),
        t(x_display + display_z/2, top + height/2 + 17, "10.0 mm", 9, anchor="middle", colour="#1d4ed8"),
        t(x_ui + pcb_z/2, top + height + 24, "UI/control PCB · 1.6 mm", 10, "bold", "middle", "#166534"),
        t(x_rf + pcb_z/2, top + height + 44, "RF/power PCB · 1.6 mm", 10, "bold", "middle", "#c2410c"),
        t(x_cells + cell_z/2, top + height/2, "2× 18650", 11, "bold", "middle", "#166534"),
        t(x_cells + cell_z/2, top + height/2 + 18, "Ø18.6 mm", 9, anchor="middle", colour="#166534"),
    ]

    # Representative opposing components prove the useful 11-mm inter-board cavity.
    ui_comp = depth("c5") * z_scale
    rf_speaker = depth("speaker") * z_scale
    rf_nrf = depth("nrf0") * z_scale
    out += [
        r(x_gap, top + 42, ui_comp, 52, "#fee2e2", "#dc2626", rx=2),
        t(x_gap + ui_comp/2, top + 70, "C5 3.3", 8, "bold", "middle", "#991b1b"),
        r(x_rf - rf_nrf, top + 116, rf_nrf, 52, "#ffedd5", "#ea580c", rx=2),
        t(x_rf - rf_nrf/2, top + 144, "nRF 2.0", 8, "bold", "middle", "#9a3412"),
        r(x_rf - rf_speaker, top + 208, rf_speaker, 62, "#dbeafe", "#2563eb", rx=2),
        t(x_rf - rf_speaker/2, top + 240, "SPK 4.5", 8, "bold", "middle", "#1d4ed8"),
        r(x_gap + 10, top + 290, gap_z - 20, 24, "#fce7f3", "#db2777", rx=3),
        t(x_gap + gap_z/2, top + 307, "FX8C M1 · 11-mm board-to-board", 8, "bold", "middle", "#9d174d"),
    ]

    # Dimension lines and interface direction.
    dim_y = top + height + 82
    out += [
        f'<line x1="{x_display:.1f}" y1="{dim_y:.1f}" x2="{x_shell_rear:.1f}" y2="{dim_y:.1f}" stroke="#172033" stroke-width="1"/>',
        f'<line x1="{x_display:.1f}" y1="{dim_y-7:.1f}" x2="{x_display:.1f}" y2="{dim_y+7:.1f}" stroke="#172033"/>',
        f'<line x1="{x_shell_rear:.1f}" y1="{dim_y-7:.1f}" x2="{x_shell_rear:.1f}" y2="{dim_y+7:.1f}" stroke="#172033"/>',
        t((x_display + x_shell_rear)/2, dim_y - 8, f"nominal selected-part stack ≈ {total_nominal:.1f} mm", 11, "bold", "middle"),
        t((x_display + x_shell_rear)/2, dim_y + 22, "before enclosure walls, adhesive, solder and tolerance allowance", 9, anchor="middle", colour="#526076"),
        arrow(x_display + 8, top + 20, x_display - 45, top + 20),
        t(x_display - 50, top + 24, "touch/view", 9, "bold", "end", "#dc2626"),
        arrow(x_cells + cell_z - 8, top + 20, x_shell_rear + 55, top + 20),
        t(x_shell_rear + 60, top + 24, "cell insertion / rear controls", 9, "bold", colour="#dc2626"),
    ]

    note_x = 855.0
    out += [
        t(note_x, 112, "What is physically represented", 16, "bold"),
        t(note_x, 142, f"• display assembly: {mpn('display')} · {depth('display'):.1f}-mm envelope", 11),
        t(note_x, 168, "• two 1.6-mm PCBs joined by the exact 11-mm FX8C pair", 11),
        t(note_x, 194, f"• largest shown cavity load: {mpn('speaker')} · {depth('speaker'):.1f} mm", 11),
        t(note_x, 220, f"• battery region: {mpn('pack_holder')} plus Ø18.6-mm cells", 11),
        t(note_x, 246, f"• upper rear expansion: {mpn('u214')} · {depth('u214'):.1f}-mm envelope", 11),
        t(note_x, 292, "Interface directions", 15, "bold"),
        t(note_x, 320, "← front: touch/view and front labels", 11),
        t(note_x, 346, "→ rear: batteries, U214, encoder, F1/F2, PTT, STOP, RE-ARM", 11),
        t(note_x, 372, "↑ top: nine separately labelled SMA/RP-SMA antenna ports", 11),
        t(note_x, 398, "↓ bottom/sides: USB, microSD, microphone, audio and M5 Unit", 11),
        t(note_x, 444, "Clearance meaning", 15, "bold"),
        t(note_x, 472, "The 11-mm value is the selected connector's board-to-board height.", 11),
        t(note_x, 498, "Component placement uses real package depth; passives and copper are omitted.", 11),
        t(note_x, 524, "The enclosure reserve is intentionally not converted into a fake final thickness.", 11),
        t(note_x, 566, "Dimensioned architecture projection — not a production enclosure drawing.", 11, "bold", colour="#b42318"),
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
        SANDWICH_OUTPUT: render_sandwich(devices, instances),
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
        print("ok: external, internal and sandwich mechanical projections are valid and current")
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
