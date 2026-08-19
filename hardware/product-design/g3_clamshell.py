#!/usr/bin/env python3
"""Generate and validate dimensioned Leshy2 mechanical projections."""

from __future__ import annotations

import argparse
import html
import json
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
EXTERNAL_OUTPUT = REPO / "docs/images/current-clamshell.svg"
INTERNAL_OUTPUT = REPO / "docs/images/internal-board-layout.svg"
SANDWICH_OUTPUT = REPO / "docs/images/sandwich-section.svg"
TOP_EDGE_OUTPUT = REPO / "docs/images/top-edge-view.svg"

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
U214_CONNECTOR_W = 18.29
U214_CONNECTOR_D = 4.95
U214_CONNECTOR_X = (BOARD_W - U214_CONNECTOR_W) / 2
# The U214 male Cap-Bus exits normal to its broad rear face.  The exact host
# socket is therefore vertical on the raised Cardputer-like rear rail and is
# projected beneath the installed Cap envelope, not beside it.
U214_CONNECTOR_Y = U214_Y + (U214_H - U214_CONNECTOR_D) / 2
U214_RETENTION_PITCH = 56.0
U214_RETENTION_X = (
    U214_X + (U214_W - U214_RETENTION_PITCH) / 2,
    U214_X + (U214_W + U214_RETENTION_PITCH) / 2,
)
U214_RETENTION_Y = U214_Y + U214_H / 2

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
RF_INSTANCE_BY_PATH = {
    "S3-2G4": "s3_external_rp_sma",
    "C5-2G4/5": "c5_external_rp_sma",
    "RX-FM/SW": "receiver_fmsw_external_sma",
    "RX-AM/LW": "receiver_amlw_external_sma",
    "N24-0": "nrf0_external_sma",
    "CC-SUB": "cc_external_sma",
    "N24-1": "nrf1_external_sma",
    "VOICE-V/U": "voice_external_sma",
    "N24-2": "nrf2_external_sma",
}
RF_USER_LABEL_LINES = {
    "S3-2G4": ("WI-FI/BLE", "2.4 GHz RP-SMA"),
    "C5-2G4/5": ("WI-FI/15.4", "2.4/5 GHz RP-SMA"),
    "RX-FM/SW": ("FM/SW RX", "SMA"),
    "RX-AM/LW": ("AM/LW LOOP", "SMA"),
    "N24-0": ("nRF24-1", "2.4 GHz SMA"),
    "CC-SUB": ("SUB-GHz", "SMA"),
    "N24-1": ("nRF24-2", "2.4 GHz SMA"),
    "VOICE-V/U": ("VHF/UHF", "SMA"),
    "N24-2": ("nRF24-3", "2.4 GHz SMA"),
}
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
    ("s3_tx_led", "WI-FI/BLE", 4.0, 115.0),
    ("c5_tx_led", "WI-FI/15.4", 12.3, 115.0),
    ("nrf0_tx_led", "nRF24-1", 20.6, 115.0),
    ("nrf1_tx_led", "nRF24-2", 28.9, 115.0),
    ("nrf2_tx_led", "nRF24-3", 37.2, 115.0),
    ("cc_tx_led", "SUB-GHz", 45.5, 115.0),
    ("voice_tx_led", "VHF/UHF", 53.8, 115.0),
    ("ir_tx_led", "IR", 62.1, 115.0),
    ("any_tx_led", "TX ACTIVE", 70.4, 115.0),
)

# Every directional interface that crosses the enclosure is rendered here.
# `coordinate` is Y for left/right exits and X for bottom exits.
EDGE_INTERFACES = (
    ("ir_demod", "front", "left", 76.5, "IR 38 kHz RX"),
    ("ir_carrier", "front", "left", 83.5, "IR raw RX"),
    ("ir_emitter", "front", "left", 90.255, "IR TX"),
    ("headphone_jack", "front", "right", 79.75, "HEADPHONES / LINE"),
    ("c5_service_usb_connector", "front", "bottom", 31.47, "C5 SERVICE USB"),
    ("sd", "front", "bottom", 55.975, "microSD"),
    ("power_command_switch", "rear", "right", 112.75, "POWER ON/OFF"),
    ("product_usb_connector", "rear", "bottom", 16.47, "USB / POWER"),
    ("rp_service_usb_connector", "rear", "bottom", 37.47, "RP SERVICE USB"),
    ("unit_connector", "rear", "bottom", 57.0, "M5 UNIT"),
)

# Acoustic openings have a physical location but no electrical direction.
ACOUSTIC_OPENINGS = (
    ("speaker", "rear", "left", 109.0, "SPEAKER / GRILLE"),
    ("microphone", "rear", "bottom", 47.0, "MICROPHONE"),
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
    reserve_class: str


UI_INNER = (
    Placement("s3", 6.0, 22.0, "UI, display, storage and audio owner"),
    Placement("c5", 51.0, 22.0, "native 2.4/5-GHz and IR owner"),
    Placement("display_connector", 25.0, 43.0, "40-contact display FPC mate"),
    Placement("slow_io", 24.0, 55.0, "24-line slow-control expander"),
    Placement("ui_matrix_io", 33.0, 55.0, "sixteen-line direct-control input expander"),
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
    Placement("microphone", 45.0, 146.0, "rear bottom microphone port"),
    Placement("speaker", 5.0, 103.0, "internal 4-Ohm differential speaker"),
    Placement("rp_dbg_header", 40.0, 104.0, "keyed RP SWD/RUN/USB_BOOT header"),
    Placement("rp_reset_button", 51.0, 104.0, "RP technological RUN/RESET"),
    Placement("rp_boot_button", 59.5, 104.0, "RP technological USB_BOOT"),
    Placement("power_command_switch", 65.8, 111.0, "low-current ON/OFF command; charging remains available"),
)

FRONT_CONTROLS = (
    Placement("ui_switch_back", 16.8, 134.4, "direct-press BACK"),
    Placement("ui_dpad_switch", 32.21, 132.11, "four directions plus center push", 45),
    Placement("ui_switch_opt", 51.6, 134.4, "direct-press OPT"),
)

DIRECT_PRESS_FRONT_CONTROLS = {"ui_switch_back", "ui_switch_opt"}

REAR_CONTROLS = (
    Placement("encoder", 2.5, 45.0, "rear encoder above F1/F2"),
    Placement("ui_switch_f1", 4.2, 63.5, "rear F1"),
    Placement("ui_switch_f2", 4.2, 78.5, "rear F2"),
    Placement("ptt_switch", 64.2, 63.5, "rear independent PTT"),
    Placement("stop_switch", 64.45, 78.5, "rear physical hard STOP"),
    Placement("rearm_switch", 64.2, 96.5, "rear recessed RE-ARM"),
)

DIRECT_PRESS_REAR_CONTROLS = {
    "ui_switch_f1", "ui_switch_f2", "ptt_switch", "stop_switch", "rearm_switch"
}

FRONT_CAP_RESERVES = (
    Reserve(
        "single D-pad cross", 28.8, 127.9, 17.4, 19.0,
        "custom keyed D-pad actuator over one SKRHADE010 stem; supplier MPN does not apply",
        "custom_actuator",
    ),
)

REAR_CAP_RESERVES = (
    Reserve(
        "RE-ARM recess", 63.0, 95.0, 9.0, 9.0,
        "custom enclosure guard around direct button; no cap or supplier MPN",
        "custom_enclosure_geometry",
    ),
)
REAR_CAP_TO_CONTROL = {
    "RE-ARM recess": "rearm_switch",
}

REAR_SELECTED_ACTUATORS = (
    Placement("encoder_knob", 0.5, 43.0, "exact soft-touch knob over rear encoder"),
)

INTERNAL_RESERVES = ()

REAR_OUTER = (
    Placement(
        "u214_connector",
        U214_CONNECTOR_X,
        U214_CONNECTOR_Y,
        "vertical host socket on the raised rear U214 rail",
    ),
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
    angle = math.radians(item.rotation % 180)
    return (
        abs(w * math.cos(angle)) + abs(h * math.sin(angle)),
        abs(w * math.sin(angle)) + abs(h * math.cos(angle)),
    )


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


def text_bounds_px(element: ET.Element) -> tuple[float, float, float, float]:
    """Conservative sans-serif bounds for generated silkscreen text."""
    x = float(element.attrib["x"])
    baseline = float(element.attrib["y"])
    size = float(element.attrib["font-size"])
    value = "".join(element.itertext())
    width = max(size * 0.6, len(value) * size * 0.58)
    anchor = element.attrib.get("text-anchor", "start")
    if anchor == "middle":
        left = x - width / 2
    elif anchor == "end":
        left = x - width
    else:
        left = x
    return left, baseline - size, width, size * 1.25


def validate_external_silkscreen(svg: str, devices: dict, instances: dict) -> list[str]:
    """Prove that every physical silk label is on an outer face and unobscured."""
    errors: list[str] = []
    scale = 3.7
    origins = {"front": (80.0, 150.0), "rear": (465.0, 150.0)}

    def px_box(origin, box):
        x, y, w, h = box
        return origin[0] + x * scale, origin[1] + y * scale, w * scale, h * scale

    display = Placement("display", 10.25, 11.0, "display")
    holder = Placement("pack_holder", 17.6, 42.0, "holder", 90)
    knob = REAR_SELECTED_ACTUATORS[0]
    visible = {
        "front": [
            ("display", (display.x, display.y, *placement_size(display, devices, instances))),
            *(
                (item.instance, (item.x, item.y, *placement_size(item, devices, instances)))
                for item in FRONT_CONTROLS
                if item.instance in DIRECT_PRESS_FRONT_CONTROLS
            ),
            *((reserve.name, (reserve.x, reserve.y, reserve.w, reserve.h)) for reserve in FRONT_CAP_RESERVES),
            *((label + " LED", (x, y, TX_LED_W, TX_LED_H)) for _, label, x, y in FRONT_TX_INDICATORS),
        ],
        "rear": [
            ("U214", (U214_X, U214_Y, U214_W, U214_H)),
            ("battery holder", (holder.x, holder.y, *placement_size(holder, devices, instances))),
            *((item.instance, (item.x, item.y, *placement_size(item, devices, instances))) for item in REAR_CONTROLS),
            ("encoder knob", (knob.x, knob.y, *placement_size(knob, devices, instances))),
            *((reserve.name, (reserve.x, reserve.y, reserve.w, reserve.h)) for reserve in REAR_CAP_RESERVES),
        ],
    }
    for face, bank in (("front", FRONT_RF), ("rear", REAR_RF)):
        visible[face].extend(
            (f"{path} connector", (centre - RF_BODY_W / 2, 0.0, RF_BODY_W, RF_BODY_D))
            for centre, path, _ in bank
        )
    for face in visible:
        visible[face].extend(
            (f"M2.5 keep-out {index}", (hx - MOUNT_KEEPOUT_R, hy - MOUNT_KEEPOUT_R, 2 * MOUNT_KEEPOUT_R, 2 * MOUNT_KEEPOUT_R))
            for index, (hx, hy) in enumerate(HOLES, 1)
        )

    root = ET.fromstring(svg)
    labels: dict[str, list[tuple[str, tuple[float, float, float, float]]]] = {"front": [], "rear": []}
    for element in root.iter("{http://www.w3.org/2000/svg}text"):
        if element.attrib.get("data-layer") != "pcb-silkscreen":
            continue
        value = "".join(element.itertext())
        box = text_bounds_px(element)
        face = next(
            (
                name
                for name, origin in origins.items()
                if origin[0] <= box[0]
                and box[0] + box[2] <= origin[0] + BOARD_W * scale
                and origin[1] <= box[1]
                and box[1] + box[3] <= origin[1] + BOARD_H * scale
            ),
            None,
        )
        if face is None:
            errors.append(f"external silk '{value}' is not wholly inside an outer PCB face")
            continue
        labels[face].append((value, box))
        for component, component_mm in visible[face]:
            if overlaps(box, px_box(origins[face], component_mm)):
                errors.append(f"{face}: silk '{value}' overlaps {component}")

    for face, face_labels in labels.items():
        for index, (value, box) in enumerate(face_labels):
            for other_value, other_box in face_labels[index + 1:]:
                if overlaps(box, other_box):
                    errors.append(f"{face}: silk '{value}' overlaps silk '{other_value}'")
    if not labels["front"] or not labels["rear"]:
        errors.append("both outer PCB faces must carry their generated user silkscreen labels")
    return errors


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
        if reserve.reserve_class not in {
            "custom_actuator", "custom_enclosure_geometry", "unselected_bom_part",
        }:
            errors.append(f"{name}: {reserve.name} has invalid reserve class {reserve.reserve_class}")
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
        "u214_connector": "Samtec SSW-107-02-S-D",
        "pack_holder": "Keystone Electronics 1048P",
        "unit_connector": "1125R-SMT-4P",
        "encoder_knob": "Davies Molding 1227-J",
        "ui_dpad_switch": "Alps Alpine SKRHADE010",
    }
    for instance, expected in required.items():
        actual = devices[instances[instance]]["mpn"]
        if actual != expected:
            errors.append(f"{instance}: expected {expected}, got {actual}")

    errors += validate_items("ui-inner", UI_INNER, devices, instances)
    errors += validate_items("rf-inner", RF_INNER, devices, instances)
    errors += validate_items("front-controls", FRONT_CONTROLS, devices, instances)
    errors += validate_items("rear-controls", REAR_CONTROLS, devices, instances)
    errors += validate_items("rear-outer", REAR_OUTER, devices, instances)
    errors += validate_items("rear-selected-actuators", REAR_SELECTED_ACTUATORS, devices, instances)
    errors += validate_reserves("front-caps", FRONT_CAP_RESERVES)
    errors += validate_reserves("rear-caps", REAR_CAP_RESERVES)
    errors += validate_reserves("internal-reserves", INTERNAL_RESERVES)
    dpad = next(item for item in FRONT_CONTROLS if item.instance == "ui_dpad_switch")
    dpad_w, dpad_h = placement_size(dpad, devices, instances)
    if dpad.rotation != 45:
        errors.append("SKRHADE010 must remain 45 degrees clockwise so A/B/C/D map to up/right/left/down")
    if abs(dpad.x + dpad_w / 2 - 37.5) > 0.02 or abs(dpad.y + dpad_h / 2 - 137.4) > 0.02:
        errors.append("SKRHADE010 rotated envelope must remain centred at D-pad axis 37.5,137.4 mm")
    display = Placement("display", 10.25, 11.0, "display")
    holder = Placement("pack_holder", 17.6, 42.0, "battery holder", 90)
    errors += validate_items("front-display", (display,), devices, instances)
    errors += validate_items("rear-exact", (holder,), devices, instances)
    ui_instances = {item.instance for item in UI_INNER}
    rf_instances = {item.instance for item in RF_INNER}
    if "microphone" in ui_instances or "microphone" not in rf_instances:
        errors.append("microphone must remain on the RF/power PCB inner side")
    if {(instance, face, side) for instance, face, side, _, _ in ACOUSTIC_OPENINGS} != {
        ("speaker", "rear", "left"),
        ("microphone", "rear", "bottom"),
    }:
        errors.append("speaker and microphone must use non-directional rear acoustic openings")

    u214_dims = devices[instances["u214"]]["dimensions_mm"]
    if u214_dims != [84.0, 24.0, 15.287]:
        errors.append("U214 must use the official 84x24x15.287-mm envelope")
    connector = REAR_OUTER[0]
    connector_w, connector_d = placement_size(connector, devices, instances)
    if (connector_w, connector_d) != (U214_CONNECTOR_W, U214_CONNECTOR_D):
        errors.append("U214 host socket must retain the exact 18.29x4.95-mm plan envelope")
    if abs(connector.x + connector_w / 2 - (U214_X + U214_W / 2)) > 0.001:
        errors.append("U214 host socket and Cap must share the same 84-mm centreline")
    if abs(connector.y + connector_d / 2 - (U214_Y + U214_H / 2)) > 0.001:
        errors.append("U214 host socket must be centred beneath the Cap envelope")
    mechanical = devices[instances["u214_connector"]].get("mechanical_contract", {})
    if not mechanical.get("orientation", "").startswith("vertical socket"):
        errors.append("raised rear U214 rail requires a vertical socket normal to its plane")
    holder_w, holder_h = placement_size(holder, devices, instances)
    u214_box = (U214_X, U214_Y, U214_W, U214_H)
    if overlaps(u214_box, (holder.x, holder.y, holder_w, holder_h), U214_CLEARANCE):
        errors.append("full U214 envelope lacks 0.7-mm clearance to the Keystone holder")
    for hole in HOLES:
        if hits_hole(u214_box, hole, U214_CLEARANCE):
            errors.append(f"full U214 envelope lacks 0.7-mm clearance to the M2.5 keep-out at {hole}")
    connector_box = (connector.x, connector.y, connector_w, connector_d)
    if not overlaps(connector_box, u214_box):
        errors.append("vertical U214 host socket must project beneath the installed Cap")
    if any(x < 0.0 or x > BOARD_W for x in U214_RETENTION_X):
        errors.append("U214 56-mm retention pitch must remain inside the 75-mm base")
    rear_control_by_instance = {item.instance: item for item in REAR_CONTROLS}
    holder_box = (holder.x, holder.y, holder_w, holder_h)
    for cap in REAR_CAP_RESERVES:
        control = rear_control_by_instance[REAR_CAP_TO_CONTROL[cap.name]]
        control_w, control_h = placement_size(control, devices, instances)
        control_box = (control.x, control.y, control_w, control_h)
        cap_box = (cap.x, cap.y, cap.w, cap.h)
        if abs((control.x + control_w / 2) - (cap.x + cap.w / 2)) > 0.15:
            errors.append(f"rear: {cap.name} is not centred over {control.instance} in X")
        if abs((control.y + control_h / 2) - (cap.y + cap.h / 2)) > 0.15:
            errors.append(f"rear: {cap.name} is not centred over {control.instance} in Y")
        if overlaps(control_box, holder_box, U214_CLEARANCE):
            errors.append(f"rear: {control.instance} body lacks battery-holder clearance")
        if overlaps(cap_box, holder_box, U214_CLEARANCE):
            errors.append(f"rear: {cap.name} lacks battery-holder clearance")
        if overlaps(cap_box, u214_box, U214_CLEARANCE):
            errors.append(f"rear: {cap.name} lacks installed-U214 clearance")
    encoder = rear_control_by_instance["encoder"]
    encoder_w, encoder_h = placement_size(encoder, devices, instances)
    knob = REAR_SELECTED_ACTUATORS[0]
    knob_w, knob_h = placement_size(knob, devices, instances)
    knob_box = (knob.x, knob.y, knob_w, knob_h)
    if abs((encoder.x + encoder_w / 2) - (knob.x + knob_w / 2)) > 0.15:
        errors.append("rear: exact encoder knob is not centred over the encoder in X")
    if abs((encoder.y + encoder_h / 2) - (knob.y + knob_h / 2)) > 0.15:
        errors.append("rear: exact encoder knob is not centred over the encoder in Y")
    if overlaps(knob_box, holder_box, U214_CLEARANCE):
        errors.append("rear: exact encoder knob lacks battery-holder clearance")
    if overlaps(knob_box, u214_box, U214_CLEARANCE):
        errors.append("rear: exact encoder knob lacks installed-U214 clearance")
    for centre, _, _ in REAR_RF:
        rf_box = (centre - RF_BODY_W / 2, 0.0, RF_BODY_W, RF_BODY_D)
        if overlaps(connector_box, rf_box, U214_CLEARANCE):
            errors.append("U214 host socket lacks 0.7-mm clearance to the rear RF connector bank")

    machine_paths = set(candidate["antenna_policy"]["base_onboard_sma_paths"])
    drawn_paths = {path for _, path, _ in FRONT_RF + REAR_RF}
    if machine_paths != drawn_paths or len(drawn_paths) != 9:
        errors.append("mechanical projection must retain all nine unique onboard RF paths")
    if set(RF_USER_LABEL_LINES) != drawn_paths:
        errors.append("every antenna path must have one user-facing silkscreen label")
    antenna_planes = candidate["interboard_contract"].get("antenna_connector_planes", {})
    connector_family = antenna_planes.get("connector_family", {})
    expected_family = {
        "standard_sma_mpn": "GCT RFPC-SMA31-FN-175-A",
        "reverse_sma_mpn": "GCT RFPC-SMA32-FN-175-A",
        "pcb_thickness_mm": 1.6,
        "body_width_mm": RF_BODY_W,
        "board_side_launch_depth_mm": RF_BODY_D,
        "thread_major_diameter_mm": RF_BARREL_D,
        "maximum_profile_above_pcb_mm": 3.9,
        "external_thread_length_mm": RF_BARREL_OUT,
    }
    for field, expected in expected_family.items():
        if connector_family.get(field) != expected:
            errors.append(f"antenna connector plane contract has invalid {field}")
    for face_key, expected_face, bank in (
        ("ui_outer_face", "outward_front", FRONT_RF),
        ("rf_power_outer_face", "outward_rear", REAR_RF),
    ):
        face = antenna_planes.get(face_key, {})
        if face.get("face") != expected_face:
            errors.append(f"{face_key}: antenna bank must remain on {expected_face}")
        actual_ports = [
            (port.get("instance"), port.get("path"), float(port.get("x_center_mm", -1)))
            for port in face.get("ports", [])
        ]
        expected_ports = [
            (RF_INSTANCE_BY_PATH[path], path, centre)
            for centre, path, _ in bank
        ]
        if actual_ports != expected_ports:
            errors.append(f"{face_key}: machine port order/coordinates differ from the product layout")
        for instance, path, _ in actual_ports:
            if instance not in instances or path not in drawn_paths:
                errors.append(f"{face_key}: unknown antenna instance/path {instance}/{path}")
    separation = antenna_planes.get("separation", {})
    expected_outer_face_separation = float(candidate["interboard_contract"]["working_inner_gap_mm"]) + 2 * 1.6
    expected_centre_plane_separation = expected_outer_face_separation + RF_BARREL_D
    if separation.get("interboard_channel_mm") != 11.0:
        errors.append("antenna contract must preserve the exact 11-mm interboard channel")
    if abs(float(separation.get("outer_pcb_face_separation_mm", -1)) - expected_outer_face_separation) > 0.001:
        errors.append("antenna contract has invalid outward PCB face separation")
    if abs(float(separation.get("antenna_centre_plane_separation_mm", -1)) - expected_centre_plane_separation) > 0.001:
        errors.append("antenna contract has invalid connector centre-plane separation")
    if separation.get("interboard_channel_contains_connector_bodies") is not False:
        errors.append("antenna connector bodies may not occupy the interboard channel")
    ui_outer_z = float(devices[instances["display"]]["dimensions_mm"][2])
    ui_inner_z = ui_outer_z + 1.6
    rf_inner_z = ui_inner_z + 11.0
    rf_outer_z = rf_inner_z + 1.6
    front_rf_centre_z = ui_outer_z - RF_BARREL_D / 2
    rear_rf_centre_z = rf_outer_z + RF_BARREL_D / 2
    if abs(front_rf_centre_z + RF_BARREL_D / 2 - ui_outer_z) > 0.001:
        errors.append("front antenna bodies must terminate at the UI PCB outer face")
    if abs(rear_rf_centre_z - RF_BARREL_D / 2 - rf_outer_z) > 0.001:
        errors.append("rear antenna bodies must begin at the RF/power PCB outer face")
    if abs((rf_inner_z - ui_inner_z) - 11.0) > 0.001:
        errors.append("the 11-mm interboard channel must remain free of antenna bodies")
    if rear_rf_centre_z - front_rf_centre_z < 20.5:
        errors.append("opposed outer-face antenna banks lost their maximum depth separation")
    for _, path, polarity in FRONT_RF + REAR_RF:
        lines = RF_USER_LABEL_LINES.get(path, ())
        if len(lines) != 2 or polarity not in lines[1]:
            errors.append(f"{path}: user label must state function plus {polarity} connector type")
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
    expected_tx_labels = {RF_USER_LABEL_LINES[path][0] for path in TX_RF_PATHS} | {"IR", "TX ACTIVE"}
    if {label for _, label, _, _ in FRONT_TX_INDICATORS} != expected_tx_labels:
        errors.append("front: TX labels must match user-facing antenna names plus IR and TX ACTIVE")
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
    external_svg = render_external(devices, instances)
    for token in (
        'id="front-outer-rf-bank" data-mount-face="ui-pcb-outer"',
        'id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer"',
    ):
        if token not in external_svg:
            errors.append("both antenna banks must render as outward-face assemblies")
    errors += validate_external_silkscreen(external_svg, devices, instances)
    internal_svg = render_internal(devices, instances)
    if 'data-layer="pcb-silkscreen"' in internal_svg:
        errors.append("inner PCB faces must not carry silkscreen text")
    if internal_svg.count('data-connector-bodies="omitted-outer-face"') != 2:
        errors.append("inner projections must omit both reverse-side antenna connector banks")
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


def rf_bank(
    origin,
    bank,
    scale,
    sx,
    sy,
    text,
    rect,
    show_body,
    compact_labels=False,
    mirror=False,
    compact_label_y=None,
    show_annotations=True,
    show_arrows=True,
    show_connector=True,
):
    rows = []
    for source_centre, path, polarity in bank:
        centre = mirrored_x(source_centre) if mirror else source_centre
        if show_body and show_connector:
            rows.append(rect(origin, centre-RF_BODY_W/2, 0, RF_BODY_W, RF_BODY_D, "#eef2f6", "#667085", rx=2))
        x = sx(origin, centre)
        edge_y = sy(origin, 0)
        barrel_top = edge_y - RF_BARREL_OUT * scale
        if show_connector:
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
        if show_arrows:
            arrow_start = barrel_top + 2 if show_connector else edge_y - 2
            rows.append(f'<path d="M{x:.1f} {arrow_start:.1f} V{arrow_start-14:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        if show_annotations:
            label_y = (compact_label_y if compact_label_y is not None else 9.0) if compact_labels else 15.5
            if compact_labels:
                for line_index, visible_label in enumerate(RF_USER_LABEL_LINES[path]):
                    rows.append(text(x, sy(origin, label_y + 2.0 * line_index), visible_label, 3.8, "bold", "middle", "#1d4ed8"))
            else:
                rows.append(text(x, sy(origin, label_y), path, 6.2, "bold", "middle", "#1d4ed8"))
                rows.append(text(x, sy(origin, 18.2), polarity, 5.2, anchor="middle", colour="#526076"))
    return rows


def dpad_cap(origin, scale, sx, sy, text):
    """Draw one custom D-pad actuator over the selected guided navigation switch."""
    cx, cy = sx(origin, 37.5), sy(origin, 137.4)
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
        f'<polygon points="{path}" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.7" data-part="single-D-pad-cross" data-manufacturing-class="custom-actuator"/>',
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{2.0*scale:.1f}" fill="#ffffff" stroke="#7c3aed" stroke-width="1.2"/>',
        text(cx, cy + 2.0, "OK", 5.0, "bold", "middle", "#4c1d95"),
    ]


def render_external(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)
    def silk_text(*args, **kwargs):
        return text(*args, **kwargs).replace(
            "<text ", '<text data-layer="pcb-silkscreen" ', 1
        )

    front, rear = (80.0, 150.0), (465.0, 150.0)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1370" height="790" viewBox="0 0 1370 790">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30, 32, "Leshy2 — dimensioned external layout", 22, "bold"),
        text(30, 56, "Text outside component outlines is intended PCB silkscreen; text inside is drawing annotation.", 11, colour="#526076"),
    ]
    out += board(front, "Front / UI face", scale, sx, sy, text, rect)
    out += board(rear, "Rear / battery and expansion face", scale, sx, sy, text, rect)

    # The raised rail occupies the same plan band as the installed Cap.  The
    # exact vertical socket is hidden beneath the Cap in the assembled view.
    out.append(rect(rear, 0.0, U214_Y, BOARD_W, U214_H, "#f0f9ff", "#0284c7", "5 3", 4))
    dock = REAR_OUTER[0]
    dock_w, dock_d = placement_size(dock, devices, instances)

    # The installed Cap is a full-size external envelope. Draw it beneath the
    # RF-port annotation layer so it cannot hide port identity or TX evidence.
    out.append(rect(rear, U214_X, U214_Y, U214_W, U214_H, "#ffedd5", "#ea580c", rx=6))
    out.append(rect(rear, dock.x, dock.y, dock_w, dock_d, "#e0f2fe", "#0369a1", "4 2", 2))
    for retention_x in U214_RETENTION_X:
        out.append(
            f'<circle cx="{sx(rear,retention_x):.1f}" cy="{sy(rear,U214_RETENTION_Y):.1f}" '
            f'r="{1.6*scale:.1f}" fill="#ffffff" stroke="#0369a1" stroke-width="1.2"/>'
        )
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 8.0), "M5Stack U214 · 84×24 mm", 7.0, "bold", "middle", "#9a3412"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 12.5), "raised rail · SSW-107-02-S-D beneath Cap", 5.0, "bold", "middle", "#075985"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 17.0), "insert ⊗ · remove ⊙", 6.2, anchor="middle", colour="#dc2626"))
    out.append('<g id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer">')
    out += rf_bank(rear, REAR_RF, scale, sx, sy, silk_text, rect, True, True, compact_label_y=7.8)
    out.append('</g>')

    display = Placement("display", 10.25, 11.0, "display")
    dw, dh = placement_size(display, devices, instances)
    out.append(rect(front, display.x, display.y, dw, dh, "#dbeafe", "#2563eb", rx=5))
    out.append(text(sx(front,37.5), sy(front,55), "HMX035CTFT-001", 9, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,60), "54.5×101.5-mm reference envelope", 6.5, anchor="middle", colour="#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,65), "touch / view ⊗", 6.5, anchor="middle", colour="#dc2626"))
    out.append('<g id="front-outer-rf-bank" data-mount-face="ui-pcb-outer">')
    out += rf_bank(front, FRONT_RF, scale, sx, sy, silk_text, rect, True, True, compact_label_y=7.8)
    out.append('</g>')

    for instance, label, x, y in FRONT_TX_INDICATORS:
        out.append(rect(front, x, y, TX_LED_W, TX_LED_H, "#ef4444", "#991b1b", rx=1))
        out.append(silk_text(sx(front,x + TX_LED_W/2), sy(front,y + 2.6), label, 4.2, "bold", "middle", "#991b1b"))

    for control in FRONT_CONTROLS:
        if control.instance not in DIRECT_PRESS_FRONT_CONTROLS:
            continue
        control_w, control_h = placement_size(control, devices, instances)
        out.append(
            rect(
                front, control.x, control.y, control_w, control_h,
                "#e2e8f0", "#64748b", rx=2,
            ).replace(
                "/>", f' data-instance="{control.instance}" data-direct-press="true"/>'
            )
        )
    for reserve in FRONT_CAP_RESERVES:
        out.append(
            rect(front, reserve.x, reserve.y, reserve.w, reserve.h, "none", "#7c3aed", "4 3", 3).replace(
                "/>", f' data-reserve-class="{reserve.reserve_class}"/>',
            )
        )
    out += dpad_cap(front, scale, sx, sy, text)
    out.append(silk_text(sx(front,20.1), sy(front,145.0), "BACK", 5.0, "bold", "middle", "#4c1d95"))
    out.append(silk_text(sx(front,54.9), sy(front,145.0), "OPT", 5.0, "bold", "middle", "#4c1d95"))

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
            out.append(silk_text(sx(front,label_x), sy(front,first_y + 2.6 * line_index), line, 4.2, "bold", "middle", stroke))
    for _, face, side, x, label in EDGE_INTERFACES:
        if face != "front" or side != "bottom":
            continue
        out.append(f'<path d="M{sx(front,x):.1f} {sy(front,150):.1f} L{sx(front,x):.1f} {sy(front,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(silk_text(sx(front,x), sy(front,149), label, 4.2, "bold", "middle", "#1d4ed8"))

    holder = Placement("pack_holder", 17.6, 42.0, "holder", 90)
    hw, hh = placement_size(holder, devices, instances)
    out.append(rect(rear, holder.x, holder.y, hw, hh, "#dcfce7", "#16a34a", rx=10))
    out.append(text(sx(rear,37.5), sy(rear,82), "Keystone 1048P", 9, "bold", "middle", "#166534"))
    out.append(text(sx(rear,37.5), sy(rear,87), "86×39.8-mm rotated holder", 6.5, anchor="middle", colour="#166534"))
    for cell_x in (28.0, 47.0):
        out.append(rect(rear, cell_x-9.3, 52.0, 18.6, 65.0, "#ecfdf3", "#22c55e", rx=20))
        out.append(text(sx(rear,cell_x), sy(rear,86), "18650", 7, "bold", "middle", "#166534"))

    # F1/F2/PTT/STOP/RE-ARM are complete, directly pressed switches on the exposed PCB.
    # They therefore render as selected solid parts, not speculative caps.
    for control in REAR_CONTROLS:
        if control.instance not in DIRECT_PRESS_REAR_CONTROLS:
            continue
        control_w, control_h = placement_size(control, devices, instances)
        fill = "#fee2e2" if control.instance == "stop_switch" else "#e2e8f0"
        stroke = "#b42318" if control.instance == "stop_switch" else "#64748b"
        out.append(
            rect(
                rear, control.x, control.y, control_w, control_h,
                fill, stroke, rx=2,
            ).replace(
                "/>", f' data-instance="{control.instance}" data-direct-press="true"/>'
            )
        )

    knob = REAR_SELECTED_ACTUATORS[0]
    knob_w, knob_h = placement_size(knob, devices, instances)
    knob_cx = sx(rear, knob.x + knob_w / 2)
    knob_cy = sy(rear, knob.y + knob_h / 2)
    out.append(
        f'<circle cx="{knob_cx:.1f}" cy="{knob_cy:.1f}" r="{knob_w*scale/2:.1f}" '
        'fill="#dbe4ee" stroke="#475467" stroke-width="1.5" '
        'data-instance="encoder_knob" data-selected-part="true"/>'
    )
    out.append(
        f'<path d="M{knob_cx:.1f} {knob_cy-knob_h*scale/2+3:.1f} '
        f'V{knob_cy-knob_h*scale/2+12:.1f}" stroke="#475467" stroke-width="2" '
        'data-part="knob-indicator-line"/>'
    )
    for reserve in REAR_CAP_RESERVES:
        out.append(rect(rear, reserve.x, reserve.y, reserve.w, reserve.h, "none", "#ea580c", "4 3", 3))
    for x, y, label in (
        (7.5, 61.5, "ENC"), (7.5, 74.0, "F1"), (7.5, 89.0, "F2"),
        (67.5, 74.0, "PTT"), (67.5, 89.0, "STOP"), (67.5, 107.0, "RE-ARM"),
    ):
        out.append(silk_text(sx(rear,x), sy(rear,y), label, 5.0, "bold", "middle", "#b42318" if label == "STOP" else "#4c1d95"))

    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if face != "rear" or side not in {"left", "right"}:
            continue
        stroke = "#ea580c"
        start_x, end_x = (0.0, -7.0) if side == "left" else (75.0, 82.0)
        out.append(f'<path d="M{sx(rear,start_x):.1f} {sy(rear,coordinate):.1f} L{sx(rear,end_x):.1f} {sy(rear,coordinate):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        label_x = 5.0 if side == "left" else 70.0
        lines = SIDE_INTERFACE_LABEL_LINES[instance]
        first_y = coordinate - 1.3 * (len(lines) - 1)
        for line_index, line in enumerate(lines):
            out.append(silk_text(sx(rear,label_x), sy(rear,first_y + 2.6 * line_index), line, 4.2, "bold", "middle", stroke))
    for _, face, side, x, label in EDGE_INTERFACES:
        if face != "rear" or side != "bottom":
            continue
        out.append(f'<path d="M{sx(rear,x):.1f} {sy(rear,150):.1f} V{sy(rear,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(silk_text(sx(rear,x), sy(rear,149), label, 4.2, "bold", "middle", "#1d4ed8"))

    # Speaker grille and microphone port are labelled openings, not arrows.
    for instance, face, side, coordinate, label in ACOUSTIC_OPENINGS:
        if face != "rear":
            continue
        if side == "left":
            for offset in (-2.0, 0.0, 2.0):
                out.append(
                    f'<line x1="{sx(rear,0):.1f}" y1="{sy(rear,coordinate + offset):.1f}" '
                    f'x2="{sx(rear,3):.1f}" y2="{sy(rear,coordinate + offset):.1f}" '
                    'stroke="#2563eb" stroke-width="1.4"/>'
                )
            out.append(silk_text(sx(rear,7.0), sy(rear,coordinate + 1.2), label, 4.2, "bold", "middle", "#2563eb"))
        elif side == "bottom":
            out.append(
                f'<circle cx="{sx(rear,coordinate):.1f}" cy="{sy(rear,149):.1f}" r="3.2" '
                'fill="none" stroke="#d97706" stroke-width="1.4" data-interface-kind="acoustic-opening"/>'
            )
            out.append(silk_text(sx(rear,coordinate), sy(rear,146.8), label, 4.2, "bold", "middle", "#92400e"))

    note_x = 850
    out += [
        text(note_x,105,"What this drawing proves",16,"bold"),
        text(note_x,135,"• both 75×150-mm panels use the same millimetre scale",11),
        text(note_x,158,"• every solid component envelope comes from the MPN register",11),
        text(note_x,181,"• raised U214 rail, vertical host socket and Keystone holder all fit",11),
        text(note_x,204,"• exact components clear all M2.5 hole/head keep-outs",11),
        text(note_x,225,"• both RF connector banks mount on the outward PCB faces",11),
        text(note_x,245,"Interface direction",15,"bold"),
        text(note_x,273,"↑ / ↓ / ← / →  interface faces through that enclosure edge",11),
        text(note_x,296,"⊗ / ⊙  press toward / remove away from the viewed face",11),
        text(note_x,319,"○ / ≋  microphone port and speaker grille are locations, not signal directions",11),
        text(note_x,347,"TX indication",15,"bold"),
        '<circle cx="858" cy="370" r="5" fill="#ef4444" stroke="#991b1b"/>',
        text(875,374,"physical actual-TX evidence for each transmitting path",11),
        text(note_x,396,"Eight path indicators plus TX ACTIVE form one front line below the display.",11),
        text(note_x,419,"Labels match antenna use: WI-FI/BLE, WI-FI/15.4, nRF24-1..3, SUB-GHz, VHF/UHF and IR.",11),
        text(note_x,450,"Geometry status",15,"bold"),
        '<rect x="850" y="467" width="28" height="15" rx="3" fill="#eef2f6" stroke="#667085"/>',
        text(890,479,"solid — registered MPN/reference assembly envelope",11),
        '<rect x="850" y="497" width="28" height="15" rx="3" fill="none" stroke="#ea580c" stroke-dasharray="5 3"/>',
        text(890,509,"orange dashed — open custom enclosure drawing",11),
        '<rect x="850" y="527" width="28" height="15" rx="3" fill="#ede9fe" stroke="#7c3aed"/>',
        text(890,539,"violet — custom product part; supplier MPN does not apply",11),
        text(note_x,566,"RF connectors are outward-face bodies with barrels and hex nuts.",11,"bold"),
        text(note_x,589,"SMA: GCT RFPC-SMA31-FN-175-A · 6 GHz · IP67 · 1.6-mm PCB.",11),
        text(note_x,609,"RP-SMA: GCT RFPC-SMA32-FN-175-A · same panel cut-out.",11),
        text(note_x,630,"Cap-Bus host: Samtec SSW-107-02-S-D · 2×7 · 2.54 mm · vertical.",11),
        text(note_x,653,"Dimensioned projection — not an enclosure release drawing.",11,"bold",colour="#b42318"),
        text(note_x,676,"D-pad cross is custom over Alps SKRHADE010; its control drawing replaces a cap MPN.",11),
        text(note_x,699,"Davies 1227-J is the exact encoder knob; only its fit HIL remains.",11),
        text(note_x,722,"BACK/OPT/F1/F2/PTT/STOP/RE-ARM are direct buttons; D-pad is one SKRH switch and one cross.",11,"bold"),
        text(note_x,745,"STOP uses a same-size SPDT tactile body and its normally-closed fail-safe contact.",11),
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
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="{svg_height}" viewBox="0 0 1510 {svg_height}" data-view="mirrored-x" data-inner-silkscreen="none">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30,32,"Leshy2 — dimensioned inner-board placement",22,"bold"),
        text(30,56,"Inner PCB faces contain no silkscreen text; numbers inside outlines are drawing annotations.",11,colour="#526076"),
    ]
    out += board(ui, "UI/control PCB — inner side", scale, sx, sy, text, rect)
    out += board(rf, "RF/power PCB — inner side", scale, sx, sy, text, rect)
    # Looking at either PCB's inner side means physically turning that board
    # over.  Therefore all X coordinates are mirrored relative to the matching
    # external face; this is not a transparent-through-board projection.
    out.append('<g id="front-rf-reverse-reference" data-connector-bodies="omitted-outer-face">')
    out += rf_bank(ui, FRONT_RF, scale, sx, sy, text, rect, False, mirror=True, show_annotations=False, show_connector=False)
    out.append('</g>')
    out.append('<g id="rear-rf-reverse-reference" data-connector-bodies="omitted-outer-face">')
    out += rf_bank(rf, REAR_RF, scale, sx, sy, text, rect, False, mirror=True, show_annotations=False, show_connector=False)
    out.append('</g>')
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
            component_number = str(numbers[item.instance])
            if item.instance == "speaker":
                component_number += " · SPK"
            out.append(text(sx(origin,view_x+w/2), sy(origin,item.y+h/2)+3, component_number, 7.5 if item.instance != "microphone" else 5.2, "bold", "middle"))
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
        text(left_x,notes_top+87,"• antenna arrows reference outer-face ports; their bodies are absent here",10),
        text(left_x,notes_top+108,"SMA · GCT RFPC-SMA31-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,notes_top+128,"RP-SMA · GCT RFPC-SMA32-FN-175-A",9.2,"bold",colour="#344054"),
        text(left_x,notes_top+154,"Only unselected RF cable bodies remain physical reserves.",9.2,"bold",colour="#9a3412"),
        text(left_x,notes_top+175,"POWER command: C&K JS102011SCQN; low-current request only, never pack current.",9.2,"bold",colour="#9a3412"),
        text(left_x,notes_top+196,"Placement projection; passives, copper and enclosure stack are omitted.",9.2,colour="#526076"),
        "</g>",
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_rear_face(devices, instances):
    """Render the rear face as seen by a user looking straight at it."""

    scale = 4.0
    ox, oy = 170.0, 105.0

    def x(mm):
        return ox + mm * scale

    def y(mm):
        return oy + mm * scale

    def t(px, py, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{px:.1f}" y="{py:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    def r(mm_x, mm_y, mm_w, mm_h, fill, stroke, dash="", rx=2, extra=""):
        dotted = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{x(mm_x):.1f}" y="{y(mm_y):.1f}" width="{mm_w*scale:.1f}" '
            f'height="{mm_h*scale:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="1.6"{dotted}{extra}/>'
        )

    def h_dim(x1_mm, x2_mm, y_px, label):
        x1, x2 = x(x1_mm), x(x2_mm)
        return [
            f'<line x1="{x1:.1f}" y1="{y_px:.1f}" x2="{x2:.1f}" y2="{y_px:.1f}" stroke="#344054"/>',
            f'<line x1="{x1:.1f}" y1="{y_px-6:.1f}" x2="{x1:.1f}" y2="{y_px+6:.1f}" stroke="#344054"/>',
            f'<line x1="{x2:.1f}" y1="{y_px-6:.1f}" x2="{x2:.1f}" y2="{y_px+6:.1f}" stroke="#344054"/>',
            t((x1+x2)/2, y_px-7, label, 11, "bold", "middle", "#344054"),
        ]

    def v_dim(y1_mm, y2_mm, x_px, label, rotate_label=False):
        y1, y2 = y(y1_mm), y(y2_mm)
        if rotate_label:
            label_x, label_y = x_px + 18, (y1 + y2) / 2
            label_text = t(label_x, label_y, label, 10, "bold", "middle", "#344054").replace(
                "<text ", f'<text transform="rotate(-90 {label_x:.1f} {label_y:.1f})" ', 1
            )
        else:
            label_text = t(x_px-9, (y1+y2)/2+4, label, 10, "bold", "end", "#344054")
        return [
            f'<line x1="{x_px:.1f}" y1="{y1:.1f}" x2="{x_px:.1f}" y2="{y2:.1f}" stroke="#344054"/>',
            f'<line x1="{x_px-6:.1f}" y1="{y1:.1f}" x2="{x_px+6:.1f}" y2="{y1:.1f}" stroke="#344054"/>',
            f'<line x1="{x_px-6:.1f}" y1="{y2:.1f}" x2="{x_px+6:.1f}" y2="{y2:.1f}" stroke="#344054"/>',
            label_text,
        ]

    cap_mpn = devices[instances["u214"]]["mpn"]
    socket_mpn = devices[instances["u214_connector"]]["mpn"]
    holder_mpn = devices[instances["pack_holder"]]["mpn"]
    holder = Placement("pack_holder", 17.6, 42.0, "battery holder", 90)
    holder_w, holder_h = placement_size(holder, devices, instances)

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" data-view="rear-face" data-look-direction="rear-to-front">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 34, "Leshy2 — complete rear view", 22, "bold"),
        t(30, 58, "View normal to the rear face; left and right are shown as seen by the user from behind.", 11, colour="#526076"),
        r(0, 0, BOARD_W, BOARD_H, "#f8fafc", "#344054", rx=8, extra=' data-board-mm="75x150"'),
    ]

    # Exact rear antenna connector bodies and outward barrels.
    out.append('<g id="rear-antenna-bank" data-plan-y-mm="0..6" data-mount-face="rf-pcb-outer">')
    for centre, path, polarity in REAR_RF:
        out.append(r(centre-RF_BODY_W/2, 0, RF_BODY_W, RF_BODY_D, "#eef2f6", "#667085", rx=2))
        out.append(
            f'<rect x="{x(centre)-RF_BARREL_D*scale/2:.1f}" y="{y(0)-RF_BARREL_OUT*scale:.1f}" '
            f'width="{RF_BARREL_D*scale:.1f}" height="{RF_BARREL_OUT*scale:.1f}" '
            'fill="#d0d5dd" stroke="#344054" stroke-width="1.3"/>'
        )
        for line_index, visible_label in enumerate(RF_USER_LABEL_LINES[path]):
            out.append(t(x(centre), y(8.4 + 2.0*line_index), visible_label, 6.0, "bold", "middle", "#1d4ed8"))
    out.append('</g>')

    # Existing base mounting holes and head keep-outs.
    for hole_x, hole_y in HOLES:
        out.append(
            f'<circle cx="{x(hole_x):.1f}" cy="{y(hole_y):.1f}" r="{MOUNT_KEEPOUT_R*scale:.1f}" '
            'fill="none" stroke="#f97316" stroke-dasharray="5 3"/>'
        )
        out.append(
            f'<circle cx="{x(hole_x):.1f}" cy="{y(hole_y):.1f}" r="{MOUNT_HOLE_D*scale/2:.1f}" '
            'fill="#ffffff" stroke="#475467" stroke-width="1.5"/>'
        )

    # The rail is part of the base; the Cap is the larger removable orange
    # envelope. The connector and two retention points are below the Cap.
    out += [
        '<g id="u214-zone" data-plan-y-mm="17..41" data-overhang-mm="4.5" data-retention-pitch-mm="56">',
        r(0, U214_Y, BOARD_W, U214_H, "#e0f2fe", "#0284c7", "5 3", 4, ' data-part="raised-host-rail"'),
        r(U214_X, U214_Y, U214_W, U214_H, "#ffedd5", "#ea580c", "", 6, ' fill-opacity="0.72" data-part="installed-u214"'),
        r(U214_CONNECTOR_X, U214_CONNECTOR_Y, U214_CONNECTOR_W, U214_CONNECTOR_D, "#bae6fd", "#0369a1", "4 2", 2, ' data-part="vertical-host-socket"'),
    ]
    for retention_x in U214_RETENTION_X:
        out.append(
            f'<circle cx="{x(retention_x):.1f}" cy="{y(U214_RETENTION_Y):.1f}" r="{1.6*scale:.1f}" '
            'fill="#ffffff" stroke="#0369a1" stroke-width="1.5" data-part="u214-retention"/>'
        )
    out += [
        t(x(37.5), y(21.5), "removable U214 Cap · 84×24 mm", 11, "bold", "middle", "#9a3412"),
        t(x(37.5), y(26.0), "raised 75-mm rail · vertical socket beneath", 8.5, "bold", "middle", "#075985"),
        t(x(37.5), y(34.5), "insert ⊗ / remove ⊙", 8.5, "bold", "middle", "#075985"),
        '</g>',
    ]

    # Battery holder begins one millimetre after the Cap envelope. It never
    # shares plan area with the Cap or its rail.
    out += [
        '<g id="battery-zone" data-plan-y-mm="42..128" data-gap-from-u214-mm="1">',
        r(holder.x, holder.y, holder_w, holder_h, "#dcfce7", "#16a34a", "", 12, ' data-part="battery-holder"'),
    ]
    for cell_x in (28.0, 47.0):
        out.append(r(cell_x-9.3, 52.0, 18.6, 65.0, "#ecfdf3", "#22c55e", "", 20, ' data-part="18650-cell"'))
        out.append(t(x(cell_x), y(86), "18650", 10, "bold", "middle", "#166534"))
    out += [
        t(x(37.5), y(124.0), "Keystone 1048P · 39.8×86 mm plan", 9, "bold", "middle", "#166534"),
        '</g>',
    ]

    # F1/F2/PTT/STOP/RE-ARM are exact directly pressed switch bodies. RE-ARM
    # keeps only a protective recess.
    out.append('<g id="rear-controls" data-direct-press="F1-F2-PTT-STOP-RE-ARM" data-actuator-reserves="none" data-enclosure-reserves="RE-ARM-recess">')
    for control in REAR_CONTROLS:
        control_w, control_h = placement_size(control, devices, instances)
        fill = "#fee2e2" if control.instance == "stop_switch" else "#e2e8f0"
        stroke = "#b42318" if control.instance == "stop_switch" else "#64748b"
        out.append(r(control.x, control.y, control_w, control_h, fill, stroke, "", 2, f' data-instance="{control.instance}"'))
    knob = REAR_SELECTED_ACTUATORS[0]
    knob_w, knob_h = placement_size(knob, devices, instances)
    knob_cx = x(knob.x + knob_w / 2)
    knob_cy = y(knob.y + knob_h / 2)
    out.append(
        f'<circle cx="{knob_cx:.1f}" cy="{knob_cy:.1f}" r="{knob_w*scale/2:.1f}" '
        'fill="#dbe4ee" stroke="#475467" stroke-width="1.6" '
        'data-instance="encoder_knob" data-selected-part="true"/>'
    )
    for reserve in REAR_CAP_RESERVES:
        out.append(r(reserve.x, reserve.y, reserve.w, reserve.h, "#f5f3ff", "#ea580c", "5 3", 3, f' fill-opacity="0.62" data-part="{reserve.name}"'))
    for label_x, label_y, label, colour in (
        (8.0, 61.5, "ENC", "#4c1d95"),
        (7.5, 74.0, "F1", "#4c1d95"),
        (7.5, 89.0, "F2", "#4c1d95"),
        (67.5, 74.0, "PTT", "#4c1d95"),
        (67.5, 89.0, "STOP", "#b42318"),
        (67.5, 107.0, "RE-ARM", "#4c1d95"),
    ):
        out.append(t(x(label_x), y(label_y), label, 7.0, "bold", "middle", colour))
    out.append('</g>')

    # Dimensions: base, Cap, overhang, retention and the two non-overlapping
    # longitudinal bands. These are documentation annotations, not silk.
    out += h_dim(0, BOARD_W, 744, "base PCB · 75 mm")
    out += h_dim(U214_X, U214_X+U214_W, 773, "U214 · 84 mm")
    out += h_dim(U214_X, 0, y(U214_Y)-10, "4.5")
    out += h_dim(BOARD_W, U214_X+U214_W, y(U214_Y)-10, "4.5")
    out += h_dim(U214_RETENTION_X[0], U214_RETENTION_X[1], 802, "retention · 56 mm")
    out += v_dim(U214_Y, U214_Y+U214_H, x(U214_X)-30, "24 mm")
    out += v_dim(42.0, 128.0, x(BOARD_W)+52, "86 mm holder", rotate_label=True)

    note_x = 560.0
    out += [
        t(note_x, 112, "Fit result", 17, "bold"),
        t(note_x, 143, "✓ antenna bodies end at Y=6 mm; the Cap starts at Y=17 mm", 12, "bold", colour="#166534"),
        t(note_x, 170, "✓ U214 occupies Y=17…41 mm", 12, "bold", colour="#166534"),
        t(note_x, 197, "✓ battery holder occupies Y=42…128 mm", 12, "bold", colour="#166534"),
        t(note_x, 224, "✓ the two envelopes have a 1.0-mm plan gap", 12, "bold", colour="#166534"),
        t(note_x, 251, "✓ 84-mm Cap overhang is symmetric: 4.5 mm per side", 12, "bold", colour="#166534"),
        t(note_x, 278, "✓ 56-mm retention pitch remains inside the 75-mm base", 12, "bold", colour="#166534"),
        t(note_x, 305, "✓ direct buttons, exact knob and recess clear the battery and U214", 12, "bold", colour="#166534"),
        t(note_x, 350, "Selected parts", 15, "bold"),
        t(note_x, 378, cap_mpn, 11, "bold", colour="#9a3412"),
        t(note_x, 403, f"{socket_mpn} · vertical 2×7 host socket", 11, "bold", colour="#075985"),
        t(note_x, 428, f"{holder_mpn} · rotated holder", 11, "bold", colour="#166534"),
        t(note_x, 474, "Rear controls shown to scale", 15, "bold"),
        t(note_x, 502, "OMRON B3S-1100P · direct BACK/OPT/F1/F2/PTT/RE-ARM", 11),
        t(note_x, 527, "C&K TLSMDT3C020GLFS · direct-press normally-closed STOP", 11),
        t(note_x, 552, "Alps EC11E18244AU + Davies 1227-J · exact encoder and knob", 11),
        t(note_x, 598, "Meaning of this view", 15, "bold"),
        t(note_x, 626, "Rear face viewed normal to the PCB — not a side section.", 11),
        t(note_x, 651, "Solid: exact bodies/direct buttons/knob. Dashed: RE-ARM recess.", 11),
        t(note_x, 676, "Orange: removable Cap/controls; blue: raised rail; green: batteries.", 11),
        t(note_x, 716, "Still requires specimen/HIL", 15, "bold", colour="#b42318"),
        t(note_x, 744, "• STOP 0.85-mm height offset, RE-ARM recess and encoder access", 11),
        t(note_x, 769, "• received-U214 pin fit, rail height, screw engagement and removal", 11),
        t(note_x, 794, "• enclosure-side and depth clearance with every installed accessory", 11),
        t(note_x, 840, "Dimensioned architecture projection — not a production enclosure drawing.", 11, "bold", colour="#b42318"),
        t(note_x, 866, "All free text in this mechanical view is documentation annotation, not PCB silkscreen.", 10, colour="#526076"),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _render_sandwich_legacy(devices, instances):
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
    plan_scale = 330.0 / BOARD_H
    x0, top, height = 120.0, 125.0, 330.0
    shell = 1.5 * z_scale
    display_z = depth("display") * z_scale
    pcb_z = 1.6 * z_scale
    gap_z = 11.0 * z_scale
    cell_z = 18.6 * z_scale
    holder_installed_z = float(
        devices[instances["pack_holder"]]["installed_envelope_mm"][2]
    ) * z_scale
    x_shell_front = x0
    x_display = x_shell_front + shell
    x_ui = x_display + display_z
    x_gap = x_ui + pcb_z
    x_rf = x_gap + gap_z
    x_holder = x_rf + pcb_z
    x_cells = x_holder + (holder_installed_z - cell_z) / 2
    x_shell_rear = x_holder + holder_installed_z
    x_rear_outer = x_shell_rear + shell
    u214_z = depth("u214") * z_scale
    u214_connector_z = depth("u214_connector") * z_scale
    total_nominal = (x_shell_rear - x_display) / z_scale
    u214_y = top + U214_Y * plan_scale
    u214_h = U214_H * plan_scale
    connector_y = top + U214_CONNECTOR_Y * plan_scale
    connector_h = U214_CONNECTOR_D * plan_scale
    holder_y = top + 42.0 * plan_scale
    holder_h = 86.0 * plan_scale
    cells_y = top + 52.0 * plan_scale
    cells_h = 65.0 * plan_scale

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1650" height="720" viewBox="0 0 1650 720">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 34, "Leshy2 — dimensioned front-to-rear sandwich", 22, "bold"),
        t(30, 58, "Depth uses exact registered part envelopes; vertical position preserves board Y so the Cap and battery zones cannot be conflated.", 11, colour="#526076"),
        t(x0 - 32, 105, "FRONT", 12, "bold", "middle", "#1d4ed8"),
        t(x_rear_outer + u214_z + 28, 105, "REAR", 12, "bold", "middle", "#166534"),
        r(x_shell_front, top, shell, height, "none", "#ea580c", "6 4", 2),
        r(x_display, top + 24, display_z, height - 48, "#dbeafe", "#2563eb", rx=3),
        r(x_ui, top, pcb_z, height, "#dcfce7", "#16a34a", rx=1),
        r(x_gap, top, gap_z, height, "#f8fafc", "#94a3b8", "5 4", 2),
        r(x_rf, top, pcb_z, height, "#ffedd5", "#ea580c", rx=1),
        '<g id="battery-zone" data-plan-y-mm="42..128">',
        r(x_holder, holder_y, holder_installed_z, holder_h, "#f0fdf4", "#16a34a", rx=18),
        r(x_cells, cells_y, cell_z, cells_h, "#dcfce7", "#22c55e", rx=18),
        '</g>',
        '<g id="rear-open-frame" data-continuous-battery-lid="false">',
        r(x_shell_rear, top, shell, u214_y - top, "none", "#ea580c", "6 4", 2),
        r(
            x_shell_rear,
            u214_y + u214_h,
            shell,
            holder_y - (u214_y + u214_h),
            "none",
            "#ea580c",
            "6 4",
            2,
        ),
        r(
            x_shell_rear,
            holder_y + holder_h,
            shell,
            top + height - (holder_y + holder_h),
            "none",
            "#ea580c",
            "6 4",
            2,
        ),
        '</g>',
        '<g id="u214-zone" data-plan-y-mm="17..41">',
        r(x_rear_outer, u214_y, u214_z, u214_h, "#ffedd5", "#ea580c", rx=5),
        r(x_rear_outer, connector_y, u214_connector_z, connector_h, "#e0f2fe", "#0369a1", rx=2),
        '</g>',
        t(x_display + display_z/2, top + height/2, "HMX035CTFT-001", 10, "bold", "middle", "#1d4ed8"),
        t(x_display + display_z/2, top + height/2 + 17, "10.0 mm", 9, anchor="middle", colour="#1d4ed8"),
        t(x_ui + pcb_z/2, top + height + 24, "UI/control PCB · 1.6 mm", 10, "bold", "middle", "#166534"),
        t(x_rf + pcb_z/2, top + height + 44, "RF/power PCB · 1.6 mm", 10, "bold", "middle", "#c2410c"),
        t(x_holder + holder_installed_z/2, holder_y + holder_h/2 - 8, "1048P + 2× 18650", 10, "bold", "middle", "#166534"),
        t(x_holder + holder_installed_z/2, holder_y + holder_h/2 + 10, "installed depth 20.7 mm", 8.5, anchor="middle", colour="#166534"),
        t(x_shell_rear + shell + 6, holder_y + holder_h - 7, "open rear frame — no battery lid", 8.5, "bold", colour="#166534"),
        t(x_rear_outer + u214_z - 5, u214_y + u214_h/2 + 4, "U214 · 15.287 mm", 8.5, "bold", "end", "#9a3412"),
        t(x_rear_outer + u214_connector_z/2, connector_y + connector_h/2 + 3, "2×7", 7.5, "bold", "middle", "#075985"),
        t(x_rear_outer + u214_z, u214_y + u214_h + 13, "separate upper dock", 8.5, "bold", "end", "#9a3412"),
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
        arrow(x_cells + cell_z - 8, holder_y + holder_h/2, x_shell_rear + 55, holder_y + holder_h/2),
        t(x_shell_rear + 60, holder_y + holder_h/2 + 4, "cell insertion / rear controls", 9, "bold", colour="#dc2626"),
    ]

    note_x = 1040.0
    out += [
        t(note_x, 112, "What is physically represented", 16, "bold"),
        t(note_x, 142, f"• display assembly: {mpn('display')} · {depth('display'):.1f}-mm envelope", 11),
        t(note_x, 168, "• two 1.6-mm PCBs joined by the exact 11-mm FX8C pair", 11),
        t(note_x, 194, f"• largest shown cavity load: {mpn('speaker')} · {depth('speaker'):.1f} mm", 11),
        t(note_x, 220, f"• battery region: {mpn('pack_holder')} plus Ø18.6-mm cells", 11),
        t(note_x, 246, f"• upper rear expansion: {mpn('u214')} · {depth('u214'):.3f}-mm envelope", 11),
        t(note_x, 272, f"• Cap-Bus host: {mpn('u214_connector')} · vertical on raised rail", 11),
        t(note_x, 312, "Interface directions", 15, "bold"),
        t(note_x, 340, "← front: touch/view and front labels", 11),
        t(note_x, 366, "→ rear: open battery holder; controls sit beside it on the same PCB face", 11),
        t(note_x, 392, "⊗/⊙ on rear face: U214 presses onto / lifts from the vertical socket", 11),
        t(note_x, 418, "↑ top: nine separately labelled SMA/RP-SMA antenna ports", 11),
        t(note_x, 444, "bottom/sides: USB, microSD, microphone port, headphones and M5 Unit", 11),
        t(note_x, 486, "Clearance meaning", 15, "bold"),
        t(note_x, 514, "The 11-mm value is the selected connector's board-to-board height.", 11),
        t(note_x, 540, "Component placement uses real package depth; passives and copper are omitted.", 11),
        t(note_x, 566, "The dashed rear reserve is a perimeter frame, not a continuous battery lid.", 11),
        t(note_x, 608, "Dimensioned architecture projection — not a production enclosure drawing.", 11, "bold", colour="#b42318"),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_sandwich(devices, instances):
    """Render two real X/Z sections; never merge different board-Y zones."""

    def mpn(instance):
        return devices[instances[instance]]["mpn"].replace(
            " (QDtech schematic assembly marking)", ""
        )

    def depth(instance):
        return float(devices[instances[instance]]["dimensions_mm"][2])

    def t(x, y, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    def r(x, y, w, h, fill, stroke, dash="", rx=2, extra=""):
        dotted = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dotted}{extra}/>'
        )

    def line(x1, y1, x2, y2, colour="#344054", dash="", width=1.2):
        dotted = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{colour}" stroke-width="{width}"{dotted}/>'
        )

    x_scale = 6.5
    z_scale = 9.0
    drawing_top = 155.0
    pcb_front_z = depth("display")
    ui_rear_z = pcb_front_z + 1.6
    rf_front_z = ui_rear_z + 11.0
    base_rear_z = rf_front_z + 1.6
    holder_depth = float(devices[instances["pack_holder"]]["installed_envelope_mm"][2])
    battery_rear_z = base_rear_z + holder_depth
    cap_rear_z = base_rear_z + depth("u214")

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" data-view="true-sections">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 36, "Leshy2 — two physical cross-sections", 23, "bold"),
        t(30, 62, "Each panel is one physical cut plane; zones are never combined.", 12, "bold", colour="#b42318"),
        t(30, 84, "Horizontal: board X. Vertical: front-to-rear depth Z. Both panels look from the antenna edge along +Y.", 11, colour="#526076"),
    ]

    def panel(panel_x, title, cut_y, kind):
        origin_x = panel_x + 60.0

        def px(mm):
            return origin_x + (mm + 4.5) * x_scale

        def pz(mm):
            return drawing_top + mm * z_scale

        parts = [
            t(panel_x, 118, title, 18, "bold"),
            t(panel_x, 140, f"cut plane Y={cut_y:.0f} mm · view from antenna edge", 10.5, colour="#526076"),
            t(px(-4.5) - 24, pz(0) + 5, "FRONT", 9, "bold", "end", "#1d4ed8"),
            t(px(-4.5) - 24, pz(base_rear_z) + 5, "REAR", 9, "bold", "end", "#166534"),
            r(px(10.25), pz(0), 54.5*x_scale, depth("display")*z_scale, "#dbeafe", "#2563eb", rx=4, extra=' data-instance="display"'),
            t(px(37.5), pz(5.2), "HMX035CTFT-001", 8.8, "bold", "middle", "#1d4ed8"),
            r(px(0), pz(pcb_front_z), BOARD_W*x_scale, 1.6*z_scale, "#dcfce7", "#16a34a", rx=1, extra=' data-instance="ui-pcb"'),
            r(px(0), pz(ui_rear_z), BOARD_W*x_scale, 11.0*z_scale, "#f8fafc", "#94a3b8", "5 4", 1, ' data-board-gap-mm="11"'),
            r(px(0), pz(rf_front_z), BOARD_W*x_scale, 1.6*z_scale, "#ffedd5", "#ea580c", rx=1, extra=' data-instance="rf-pcb"'),
            t(px(37.5), pz(ui_rear_z+5.8), "FX8C M1 · exact 11-mm board-to-board gap", 8.3, "bold", "middle", "#9d174d"),
            line(px(0), pz(0), px(0), pz(max(battery_rear_z, cap_rear_z)), "#cbd5e1", "3 3"),
            line(px(75), pz(0), px(75), pz(max(battery_rear_z, cap_rear_z)), "#cbd5e1", "3 3"),
        ]

        if kind == "u214":
            parts += [
                f'<g id="section-u214" data-cut-y-mm="{cut_y:.0f}" data-contains="u214-no-battery">',
                r(px(U214_X), pz(base_rear_z), U214_W*x_scale, depth("u214")*z_scale, "#ffedd5", "#ea580c", rx=5, extra=' fill-opacity="0.75" data-instance="u214"'),
                r(px(U214_CONNECTOR_X), pz(base_rear_z), U214_CONNECTOR_W*x_scale, depth("u214_connector")*z_scale, "#bae6fd", "#0369a1", "4 2", 2, ' data-instance="u214-connector"'),
                t(px(37.5), pz(base_rear_z+4.7), "Samtec SSW-107-02-S-D · vertical host socket", 7.2, "bold", "middle", "#075985"),
                t(px(37.5), pz(base_rear_z+12.4), "M5Stack U214 · 84 × 24 × 15.287 mm", 9.2, "bold", "middle", "#9a3412"),
                t(px(37.5), pz(cap_rear_z)+24, "No battery appears: its Y=42…128-mm zone does not cross A–A.", 9.3, "bold", "middle", "#166534"),
                '</g>',
            ]
            rear_z = cap_rear_z
            rear_label = f"base + U214 = {rear_z:.3f} mm"
        else:
            holder_x = 17.6
            holder_w = 39.8
            parts += [
                f'<g id="section-battery" data-cut-y-mm="{cut_y:.0f}" data-contains="battery-controls-no-u214">',
                r(px(holder_x), pz(base_rear_z), holder_w*x_scale, holder_depth*z_scale, "#dcfce7", "#16a34a", rx=12, extra=' data-instance="pack-holder"'),
                r(px(18.7), pz(base_rear_z+1.05), 18.6*x_scale, 18.6*z_scale, "#ecfdf3", "#22c55e", rx=16, extra=' data-instance="cell-left"'),
                r(px(37.7), pz(base_rear_z+1.05), 18.6*x_scale, 18.6*z_scale, "#ecfdf3", "#22c55e", rx=16, extra=' data-instance="cell-right"'),
                t(px(37.5), pz(base_rear_z+10.8), "Keystone Electronics 1048P + 2× 18650", 9.2, "bold", "middle", "#166534"),
                r(px(4.2), pz(base_rear_z), 6.6*x_scale, depth("ui_switch_f2")*z_scale, "#e2e8f0", "#64748b", rx=2, extra=' data-instance="F2"'),
                r(px(64.45), pz(base_rear_z), 6.1*x_scale, depth("stop_switch")*z_scale, "#fee2e2", "#b42318", rx=2, extra=' data-instance="STOP"'),
                t(px(7.5), pz(base_rear_z+2.7), "F2", 8, "bold", "middle", "#4c1d95"),
                t(px(67.5), pz(base_rear_z+3.4), "STOP", 8, "bold", "middle", "#b42318"),
                t(px(37.5), pz(battery_rear_z)+24, "No U214 appears: its Y=17…41-mm zone does not cross B–B.", 9.3, "bold", "middle", "#9a3412"),
                '</g>',
            ]
            rear_z = battery_rear_z
            rear_label = f"base + installed holder = {rear_z:.1f} mm"

        dim_x = px(-4.5) - 42
        parts += [
            line(dim_x, pz(0), dim_x, pz(rear_z)),
            line(dim_x-6, pz(0), dim_x+6, pz(0)),
            line(dim_x-6, pz(rear_z), dim_x+6, pz(rear_z)),
            t(dim_x-9, (pz(0)+pz(rear_z))/2, rear_label, 9, "bold", "middle", "#344054").replace(
                '<text ', f'<text transform="rotate(-90 {dim_x-9:.1f} {((pz(0)+pz(rear_z))/2):.1f})" ', 1
            ),
            line(px(0), pz(rear_z)+58, px(75), pz(rear_z)+58),
            line(px(0), pz(rear_z)+52, px(0), pz(rear_z)+64),
            line(px(75), pz(rear_z)+52, px(75), pz(rear_z)+64),
            t(px(37.5), pz(rear_z)+51, "base PCB · 75 mm", 9.5, "bold", "middle", "#344054"),
        ]
        if kind == "u214":
            parts += [
                line(px(U214_X), pz(rear_z)+88, px(U214_X+U214_W), pz(rear_z)+88),
                line(px(U214_X), pz(rear_z)+82, px(U214_X), pz(rear_z)+94),
                line(px(U214_X+U214_W), pz(rear_z)+82, px(U214_X+U214_W), pz(rear_z)+94),
                t(px(37.5), pz(rear_z)+81, "U214 · 84 mm · 4.5-mm overhang per side", 9.5, "bold", "middle", "#9a3412"),
            ]
        return parts

    out += panel(60, "A–A · U214 dock zone", 29.0, "u214")
    out += panel(780, "B–B · battery/control zone", 82.0, "battery")
    out += [
        line(745, 105, 745, 750, "#d0d5dd", "6 5"),
        t(60, 750, f"Display: {mpn('display')} · 10.0-mm envelope", 10.5, "bold"),
        t(60, 774, f"Inner component positions—including {mpn('speaker')}—are documented in the adjacent inner-face view.", 10.5, colour="#526076"),
        t(780, 750, "The sections exclude enclosure walls, solder and manufacturing tolerances.", 10.5, "bold", colour="#b42318"),
        t(780, 774, "Dimensioned architecture projection — not a production enclosure drawing.", 10.5, colour="#526076"),
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_top_edge(devices, instances):
    """Render a true orthographic view from the antenna edge along board Y."""

    def mpn(instance):
        return devices[instances[instance]]["mpn"].replace(
            " (QDtech schematic assembly marking)", ""
        )

    def depth(instance):
        return float(devices[instances[instance]]["dimensions_mm"][2])

    def t(x, y, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    def r(x, y, w, h, fill, stroke, dash="", rx=2, extra=""):
        dotted = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dotted}{extra}/>'
        )

    scale_x = 8.0
    scale_z = 9.0
    ox, oz = 120.0, 145.0

    def x(mm):
        return ox + (mm + 4.5) * scale_x

    def z(mm):
        return oz + mm * scale_z

    ui_outer_z = depth("display")
    ui_inner_z = ui_outer_z + 1.6
    rf_inner_z = ui_inner_z + 11.0
    rf_outer_z = rf_inner_z + 1.6
    base_rear_z = rf_outer_z
    front_rf_centre_z = ui_outer_z - RF_BARREL_D / 2
    rear_rf_centre_z = rf_outer_z + RF_BARREL_D / 2
    rf_centre_spacing = rear_rf_centre_z - front_rf_centre_z
    holder_depth = float(devices[instances["pack_holder"]]["installed_envelope_mm"][2])
    max_rear_z = base_rear_z + holder_depth
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="720" viewBox="0 0 1400 720" data-view="top-edge" data-look-direction="antenna-edge-to-bottom" data-rf-mounting="opposed-outer-faces">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 36, "Leshy2 — true top view from the antenna edge", 23, "bold"),
        t(30, 62, "Looking along board +Y. Horizontal is board X; vertical is front-to-rear depth Z.", 11, "bold", colour="#b42318"),
        t(30, 84, "Board Y is collapsed in this orthographic projection; the rear view separately proves U214/battery longitudinal clearance.", 11, colour="#526076"),
        t(x(-4.5)-24, z(0)+5, "FRONT", 9, "bold", "end", "#1d4ed8"),
        t(x(-4.5)-24, z(base_rear_z)+5, "REAR", 9, "bold", "end", "#166534"),
        r(x(10.25), z(0), 54.5*scale_x, 10.0*scale_z, "#dbeafe", "#2563eb", rx=4, extra=' data-instance="display"'),
        t(x(37.5), z(5.2), "HMX035CTFT-001 · display", 9.5, "bold", "middle", "#1d4ed8"),
        r(x(0), z(ui_outer_z), BOARD_W*scale_x, 1.6*scale_z, "#dcfce7", "#16a34a", rx=1, extra=' data-instance="ui-pcb"'),
        r(x(0), z(ui_inner_z), BOARD_W*scale_x, 11.0*scale_z, "#f8fafc", "#94a3b8", "5 4", 1, ' data-board-gap-mm="11" data-antenna-bodies="none"'),
        r(x(0), z(rf_inner_z), BOARD_W*scale_x, 1.6*scale_z, "#ffedd5", "#ea580c", rx=1, extra=' data-instance="rf-pcb"'),
        t(x(37.5), z(17.7), "FX8C M1 · 11-mm board gap", 8.5, "bold", "middle", "#9d174d"),
        '<g id="top-edge-rear-envelopes" data-y-collapsed="true">',
        r(x(U214_X), z(base_rear_z), U214_W*scale_x, depth("u214")*scale_z, "#ffedd5", "#ea580c", "7 4", 5, ' fill-opacity="0.45" data-instance="u214"'),
        r(x(17.6), z(base_rear_z), 39.8*scale_x, holder_depth*scale_z, "#dcfce7", "#16a34a", "4 3", 12, ' fill-opacity="0.45" data-instance="pack-holder"'),
        '</g>',
        t(x(37.5), z(base_rear_z+6.0), "U214 · 84 mm wide · Y=17…41", 9, "bold", "middle", "#9a3412"),
        t(x(37.5), z(base_rear_z+17.9), "1048P + cells · 39.8 mm wide · Y=42…128", 9, "bold", "middle", "#166534"),
        '<g id="front-antenna-bank" data-count="4" data-mount-face="ui-pcb-outer">',
    ]
    for centre, path, _ in FRONT_RF:
        out.append(f'<ellipse cx="{x(centre):.1f}" cy="{z(front_rf_centre_z):.1f}" rx="{RF_BARREL_D*scale_x/2:.1f}" ry="{RF_BARREL_D*scale_z/2:.1f}" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5" data-path="{path}"/>')
    out += ['</g>', '<g id="rear-antenna-bank" data-count="5" data-mount-face="rf-pcb-outer">']
    for centre, path, _ in REAR_RF:
        out.append(f'<ellipse cx="{x(centre):.1f}" cy="{z(rear_rf_centre_z):.1f}" rx="{RF_BARREL_D*scale_x/2:.1f}" ry="{RF_BARREL_D*scale_z/2:.1f}" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5" data-path="{path}"/>')
    out += [
        '</g>',
        t(885, z(front_rf_centre_z)+4, "4 front ports · UI outer face", 10, "bold", "end", "#1d4ed8"),
        t(885, z(rear_rf_centre_z)+4, "5 rear ports · RF/power outer face", 10, "bold", "end", "#9a3412"),
        f'<line x1="{x(0):.1f}" y1="{z(max_rear_z)+58:.1f}" x2="{x(75):.1f}" y2="{z(max_rear_z)+58:.1f}" stroke="#344054"/>',
        f'<line x1="{x(0):.1f}" y1="{z(max_rear_z)+52:.1f}" x2="{x(0):.1f}" y2="{z(max_rear_z)+64:.1f}" stroke="#344054"/>',
        f'<line x1="{x(75):.1f}" y1="{z(max_rear_z)+52:.1f}" x2="{x(75):.1f}" y2="{z(max_rear_z)+64:.1f}" stroke="#344054"/>',
        t(x(37.5), z(max_rear_z)+50, "base PCB · 75 mm", 10, "bold", "middle", "#344054"),
        f'<line x1="{x(U214_X):.1f}" y1="{z(max_rear_z)+88:.1f}" x2="{x(U214_X+U214_W):.1f}" y2="{z(max_rear_z)+88:.1f}" stroke="#344054"/>',
        f'<line x1="{x(U214_X):.1f}" y1="{z(max_rear_z)+82:.1f}" x2="{x(U214_X):.1f}" y2="{z(max_rear_z)+94:.1f}" stroke="#344054"/>',
        f'<line x1="{x(U214_X+U214_W):.1f}" y1="{z(max_rear_z)+82:.1f}" x2="{x(U214_X+U214_W):.1f}" y2="{z(max_rear_z)+94:.1f}" stroke="#344054"/>',
        t(x(37.5), z(max_rear_z)+80, "U214 · 84 mm · symmetric 4.5-mm side overhang", 10, "bold", "middle", "#9a3412"),
        t(920, 150, "What this view proves", 16, "bold"),
        t(920, 184, "✓ 84-mm Cap overhang is 4.5 mm on each side", 11, "bold", colour="#166534"),
        t(920, 212, "✓ both antenna banks mount on opposed outward PCB faces", 11, "bold", colour="#166534"),
        t(920, 240, "✓ the exact 11-mm interboard channel contains no antenna body", 11, "bold", colour="#166534"),
        t(920, 268, f"✓ antenna centre planes are separated by {rf_centre_spacing:.2f} mm", 11, "bold", colour="#166534"),
        t(920, 316, "Projection limits", 16, "bold"),
        t(920, 350, "Display/front-bank and U214/battery overlaps are Y-collapse artifacts.", 11),
        t(920, 378, "Use the adjacent external views for their real longitudinal positions.", 11),
        t(920, 426, "Selected depth references", 16, "bold"),
        t(920, 460, f"{mpn('u214')} · {depth('u214'):.3f} mm", 10.5),
        t(920, 488, f"{mpn('pack_holder')} · {holder_depth:.1f}-mm installed envelope", 10.5),
        t(920, 516, f"{mpn('display')} · {depth('display'):.1f} mm", 10.5),
        t(920, 564, "Nominal maximum selected-part depth: 44.9 mm", 11, "bold", colour="#b42318"),
        t(920, 590, "Excludes enclosure walls, solder and manufacturing tolerances.", 10.5, colour="#526076"),
        t(30, 690, "Dimensioned architecture projection — not a production enclosure drawing.", 10.5, "bold", colour="#b42318"),
        '</svg>',
    ]
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
        TOP_EDGE_OUTPUT: render_top_edge(devices, instances),
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
        print("ok: external, internal, top-edge and section mechanical projections are valid and current")
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
