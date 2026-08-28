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
MECHANICAL_GATES_PATH = REPO / "hardware/product-design/mechanical-evidence-gates.json"
SOURCE_RESEARCH_PATH = REPO / "hardware/product-design/h1-source-research.json"
NAVIGATION_CLUSTER_PATH = REPO / "hardware/product-design/navigation-cluster.json"
DISPLAY_ADAPTER_DESIGN_PATH = REPO / "hardware/product-design/display-adapter.json"
ASSEMBLY_COORDINATE_MODEL_PATH = REPO / "hardware/product-design/assembly-coordinate-model.json"
EXTERNAL_OUTPUT = REPO / "docs/images/current-clamshell.svg"
SERVICE_OUTPUT = REPO / "docs/images/service-access.svg"
INTERNAL_OUTPUT = REPO / "docs/images/internal-board-layout.svg"
SANDWICH_OUTPUT = REPO / "docs/images/sandwich-section.svg"
TOP_EDGE_OUTPUT = REPO / "docs/images/top-edge-view.svg"
NAVIGATION_OUTPUT = REPO / "docs/images/navigation-cluster.svg"
DISPLAY_ADAPTER_OUTPUT = REPO / "docs/images/display-adapter.svg"
SOURCE_TABLE_OUTPUT = REPO / "hardware/product-design/generated/H1-physical-source-table.json"
SOURCE_REGISTER_OUTPUT = REPO / "docs/physical-source-register.md"
UNIFIED_COORDINATE_TABLE_OUTPUT = REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json"
EXTERNAL_ACCEPTANCE_OUTPUT = REPO / "hardware/product-design/generated/H1-external-face-acceptance.json"
CROSS_VIEW_ACCEPTANCE_OUTPUT = REPO / "hardware/product-design/generated/H1-cross-view-acceptance.json"

BOARD_W = 75.0
BOARD_H = 150.0
MOUNT_HOLE_D = 2.7
MOUNT_KEEPOUT_R = 4.0
HOLES = ((5.0, 11.0), (70.0, 11.0), (5.0, 145.0), (70.0, 145.0))

INTERBOARD_GAP_MM = 11.0
MIN_INTERBOARD_Z_CLEARANCE_MM = 0.7
INTENTIONAL_INTERBOARD_MATES = {
    ("m1_ui_plug", "m1_rf_receptacle"),
}

U214_X = -4.5
U214_Y = 17.0
U214_W = 84.0
U214_H = 24.0
U214_CLEARANCE = 0.7
U214_CONNECTOR_W = 17.78
U214_CONNECTOR_D = 5.08
U214_CONNECTOR_PTH_KEEPOUT_W = 17.78
U214_CONNECTOR_PTH_KEEPOUT_D = 3.81
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
PACK_HOLDER_Y = 42.0
PACK_HOLDER_H = 86.0
PACK_CELL_Y = PACK_HOLDER_Y + 10.0
PACK_HOLDER_BODY_W = 39.78
PACK_HOLDER_BODY_H = 77.06
PACK_HOLDER_BODY_X = (BOARD_W - PACK_HOLDER_BODY_W) / 2
PACK_HOLDER_BODY_Y = PACK_HOLDER_Y + (PACK_HOLDER_H - PACK_HOLDER_BODY_H) / 2

# Exact GCT RFPC-SMA31/SMA32 1.6-mm edge-launch family. The 10.2-mm
# plan width includes the nut envelope; the 6-mm board-side depth comes from
# the exact land/body drawing rather than the full external threaded length.
RF_BODY_W = 10.2
RF_BODY_D = 6.0
RF_BARREL_D = 6.35
RF_BARREL_OUT = 11.4
FRONT_RF = (
    (15.7, "S3-2G4", "RP-SMA"),
    (30.0, "RX-FM/SW", "SMA"),
    (45.0, "RX-AM/LW", "SMA"),
    (59.3, "C5-2G4/5", "RP-SMA"),
)
REAR_RF = (
    # Six 10.2-mm SMA bodies plus the 3.6-mm FPV MMCX fit the 75-mm edge
    # with 0.7-mm body gaps and 3.0-mm board margins.  The H1-R2 overlay
    # inserts the MMCX at X=37.5 between N24-1 and VHF.
    (8.1, "N24-0", "SMA"),
    (19.0, "CC-SUB", "SMA"),
    (29.9, "N24-1", "SMA"),
    (45.1, "VOICE-VHF", "SMA"),
    (56.0, "VOICE-UHF", "SMA"),
    (66.9, "N24-2", "SMA"),
)
VOICE_V_RF_CORRIDOR = ((45.1, 0.0), (20.25, 32.5))
VOICE_U_RF_CORRIDOR = ((56.0, 0.0), (71.2, 36.95))
OPPOSITE_FACE_CLEARANCE_MM = 1.5
RF_INSTANCE_BY_PATH = {
    "S3-2G4": "s3_external_rp_sma",
    "C5-2G4/5": "c5_external_rp_sma",
    "RX-FM/SW": "receiver_fmsw_external_sma",
    "RX-AM/LW": "receiver_amlw_external_sma",
    "N24-0": "nrf0_external_sma",
    "CC-SUB": "cc_external_sma",
    "N24-1": "nrf1_external_sma",
    "VOICE-VHF": "voice_v_external_sma",
    "VOICE-UHF": "voice_external_sma",
    "N24-2": "nrf2_external_sma",
}
RF_SOURCE_INSTANCE_BY_PATH = {
    "S3-2G4": "s3",
    "C5-2G4/5": "c5",
    "RX-FM/SW": "receiver",
    "RX-AM/LW": "receiver",
    "N24-0": "nrf0",
    "CC-SUB": "cc",
    "N24-1": "nrf1",
    "VOICE-VHF": "voice_v",
    "VOICE-UHF": "voice",
    "N24-2": "nrf2",
}
BOARD_RF_CABLE_TO_TRACE_HANDOFFS = frozenset(
    {
        "s3_rf_board_connector",
        "c5_rf_board_connector",
        "nrf0_rf_board_connector",
        "nrf1_rf_board_connector",
        "nrf2_rf_board_connector",
    }
)
RF_USER_LABEL_LINES = {
    "S3-2G4": ("WI-FI/BLE", "2.4 GHz"),
    "C5-2G4/5": ("WI-FI/15.4", "2.4/5 GHz"),
    "RX-FM/SW": ("FM/SW/AIR RX",),
    "RX-AM/LW": ("AM/LW LOOP",),
    "N24-0": ("nRF24-1", "2.4 GHz"),
    "CC-SUB": ("SUB-GHz",),
    "N24-1": ("nRF24-2", "2.4 GHz"),
    "VOICE-VHF": ("VHF VOICE", "134-174 MHz"),
    "VOICE-UHF": ("UHF VOICE", "400-480 MHz"),
    "N24-2": ("nRF24-3", "2.4 GHz"),
}
# Optional per-path label coordinates for derivative layouts.  Coordinates
# are PCB millimetres in the matching outer-face frame.  Keeping them in the
# drawing input lets the geometry audit reject silk hidden by a connector,
# cable, display, Cap or mounting keep-out instead of relying on hand tuning.
RF_COMPACT_LABEL_POSITIONS = {
    "N24-0": (12.3, 7.8),
    "N24-2": (62.7, 7.8),
}
TX_RF_PATHS = {
    "S3-2G4", "C5-2G4/5", "N24-0", "CC-SUB", "N24-1", "VOICE-VHF", "VOICE-UHF", "N24-2"
}
TX_LED_W = 1.6
TX_LED_H = 0.8
TX_LED_INSTANCES = {
    "S3-2G4": "s3_tx_led",
    "C5-2G4/5": "c5_tx_led",
    "N24-0": "nrf0_tx_led",
    "CC-SUB": "cc_tx_led",
    "N24-1": "nrf1_tx_led",
    "VOICE-VHF": "voice_tx_led",
    "VOICE-UHF": "voice_tx_led",
    "N24-2": "nrf2_tx_led",
}
FRONT_FACE_INDICATORS = (
    ("s3_tx_led", "WI-FI/BLE", 5.1, 104.5),
    ("c5_tx_led", "WI-FI/15.4", 20.9, 104.5),
    ("nrf0_tx_led", "nRF24-1", 36.7, 104.5),
    ("nrf1_tx_led", "nRF24-2", 52.5, 104.5),
    ("nrf2_tx_led", "nRF24-3", 68.3, 104.5),
    ("cc_tx_led", "SUB-GHz", 5.1, 111.0),
    ("voice_tx_led", "V/U TX", 20.9, 111.0),
    ("ir_tx_led", "IR", 36.7, 111.0),
    ("ext_tx_led", "LORA/EXT", 52.5, 111.0),
    ("fault_led", "FAULT", 68.3, 111.0),
)
PROJECT_REPOSITORY_URL = "github.com/anton-vinogradov/esp32-leshy2"
OUTER_FACE_PRODUCT_MARKS = (
    ("front", "Леший", 37.5, 99.5, 10.5),
    ("rear", "ESP32-LESHY2", 37.5, 136.0, 7.5),
    ("rear", PROJECT_REPOSITORY_URL, 37.5, 142.0, 5.0),
)

# Every directional interface that crosses the enclosure is rendered here.
# `coordinate` is Y for left/right exits and X for bottom exits.
EDGE_INTERFACES = (
    ("ir_demod", "front", "left", 76.5, "IR 38 kHz RX"),
    ("ir_carrier", "front", "left", 83.5, "IR raw RX"),
    ("ir_emitter", "front", "left", 90.255, "IR TX"),
    ("headphone_jack", "front", "right", 79.75, "HEADSET / CTIA"),
    ("c5_service_usb_connector", "front", "bottom", 31.47, "C5 SERVICE USB"),
    ("sd", "front", "bottom", 55.975, "microSD"),
    ("power_command_switch", "rear", "right", 112.75, "RUN / KILL"),
    ("product_usb_connector", "rear", "bottom", 16.47, "USB / POWER"),
    ("rp_service_usb_connector", "rear", "bottom", 37.47, "RP SERVICE USB"),
    ("microphone", "front", "bottom", 47.0, "MICROPHONE"),
    ("unit_connector", "rear", "bottom", 57.0, "M5 UNIT"),
    ("s3_reset_button", "front", "left", 117.25, "S3 RST"),
    ("s3_boot_button", "front", "left", 124.25, "S3 BOOT"),
    ("c5_reset_button", "front", "right", 117.25, "C5 RST"),
    ("c5_boot_button", "front", "right", 124.25, "C5 BOOT"),
    ("rp_reset_button", "rear", "left", 108.25, "RP RST"),
    ("rp_boot_button", "rear", "left", 115.25, "RP BOOT"),
)

EXTERNAL_SERVICE_BUTTONS = frozenset(
    {
        "s3_reset_button", "s3_boot_button",
        "c5_reset_button", "c5_boot_button",
        "rp_reset_button", "rp_boot_button",
    }
)
SERVICE_BUTTON_RECESS_MM = 1.2

# Internal acoustic components can require an exterior label without inventing
# enclosure-slot geometry on the PCB-face projection.
EXTERNAL_COMPONENT_LABELS = (
    ("speaker", "rear", "right", 133.0, "SPEAKER"),
)

# External side projections show only real silkscreen labels and an enclosure
# direction arrow.  They must not invent a visible button/socket body on the
# face, and the front labels must fit wholly in the two gutters beside the
# display envelope.
SIDE_INTERFACE_LABEL_LINES = {
    "ir_demod": ("IR 38 kHz RX",),
    "ir_carrier": ("IR RAW RX",),
    "ir_emitter": ("IR TX",),
    "headphone_jack": ("HEADSET", "CTIA"),
    "power_command_switch": ("RUN", "KILL"),
    "s3_reset_button": ("S3 RST",),
    "s3_boot_button": ("S3 BOOT",),
    "c5_reset_button": ("C5 RST",),
    "c5_boot_button": ("C5 BOOT",),
    "rp_reset_button": ("RP RST",),
    "rp_boot_button": ("RP BOOT",),
}


@dataclass(frozen=True)
class Placement:
    instance: str
    x: float
    y: float
    role: str
    rotation: int = 0


@dataclass(frozen=True)
class CableRoute:
    instance: str
    points: tuple[tuple[float, float], ...]
    role: str


@dataclass(frozen=True)
class CableReserve:
    """Conservative cable space when the exact module connector axis is H5 evidence."""

    instance: str
    module_instance: str
    board_connector_instance: str
    escape_points: tuple[tuple[float, float], ...]
    role: str


@dataclass(frozen=True)
class ThroughBoardFeature:
    """One pin/tab envelope that protrudes from an outer-face part into the gap."""

    assembly_instance: str
    feature: str
    x: float
    y: float
    w: float
    h: float
    inner_height: float
    role: str


@dataclass(frozen=True)
class AntennaTopologyGuide:
    """One visible source-to-antenna relation; never a claim of routed copper."""

    instance: str
    path: str
    frame: str
    source_instance: str
    external_instance: str
    points: tuple[tuple[float, float], ...]
    role: str


@dataclass(frozen=True)
class BodyProjectionContract:
    """Mechanical meaning of one rendered body outside the placement maps."""

    instance: str
    frame: str
    rotation: int
    direction: str


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
    Placement("s3_rf_coupler", 15.2, 6.2, "S3 forward-power coupler beside the outward RP-SMA"),
    Placement("c5_rf_coupler", 58.2, 6.2, "C5 dual-band forward-power coupler beside the outward RP-SMA"),
    Placement("s3_rf_board_connector", 14.5, 9.0, "S3 30-mm jumper board receptacle"),
    Placement("c5_rf_board_connector", 57.5, 9.0, "C5 30-mm jumper board receptacle"),
    Placement("s3", 6.0, 22.0, "UI, display, storage and audio owner"),
    Placement("c5", 51.0, 22.0, "native 2.4/5-GHz and IR owner"),
    Placement("display_connector", 32.2, 6.5, "40-contact fixed receptacle for the antenna-edge replaceable display adapter"),
    Placement("slow_io", 24.0, 55.0, "24-line slow-control expander"),
    Placement("ui_matrix_io", 33.0, 55.0, "sixteen-line direct-control input expander"),
    Placement("codec", 42.0, 55.0, "audio capture and playback codec"),
    Placement("audio_speaker_selector", 42.0, 62.0, "active differential speaker-path selector"),
    Placement("receiver", 51.0, 54.0, "FM/AM/SW/LW receiver"),
    Placement("ir_demod", 0.0, 75.0, "38-kHz IR receiver"),
    Placement("ir_carrier", 0.0, 82.0, "carrier-learning IR receiver"),
    Placement("ir_emitter", 0.0, 89.0, "940-nm IR transmitter"),
    Placement("ir_safe_gate", 8.0, 75.0, "UI-local FAULT_KILL-qualified IR carrier gate"),
    Placement("evidence_cmp_a", 8.0, 82.0, "UI-local S3/C5/IR TX evidence comparator"),
    Placement("ui_zone_ntc", 12.0, 75.0, "UI/display hotspot safety sensor"),
    Placement("codec_i2s_din_boot_gate", 18.0, 75.0, "CODEC_READY and AUDIO_ARM gate protecting S3 boot GPIO0"),
    Placement("safe_reset_sink_a", 18.0, 82.0, "UI-local S3/C5 passive-drain reset sinks"),
    Placement("safe_c5_reset_buffer", 22.0, 82.0, "UI-local RUN_PERMIT C5 reset inverter"),
    Placement("safe_c5_fault_reset_buffer", 25.0, 82.0, "UI-local direct FAULT_ASSERT_N C5 reset sink"),
    Placement("headphone_jack", 60.4, 76.0, "3.5-mm CTIA headset TRRS mid-mount connector"),
    Placement("headset_control_io", 54.2, 77.0, "dedicated 0x39 headset source controller and seven reserve I/O lines"),
    Placement("m1_ui_plug", 22.2, 119.0, "80-contact M1 plug; 11-mm board stack"),
    Placement("c5_service_usb_connector", 27.0, 142.65, "C5 data-only service USB"),
    Placement("sd", 48.0, 136.15, "bottom-access push-push microSD", 90),
    Placement("s3_dbg_header", 5.0, 104.0, "keyed S3 UART0/RESET/BOOT header"),
    Placement("s3_reset_button", 0.0, 115.0, "external left-side S3 RESET service control", 90),
    Placement("s3_boot_button", 0.0, 122.0, "external left-side S3 BOOT service control", 90),
    Placement("c5_dbg_header", 47.0, 104.0, "keyed C5 UART0/RESET/BOOT header"),
    Placement("c5_reset_button", 71.6, 115.0, "external right-side C5 RESET service control", 270),
    Placement("c5_boot_button", 71.6, 122.0, "external right-side C5 BOOT service control", 270),
)

# Exact module-side axes come from the Espressif package drawings. The visible
# line is only the direct 2D projection between connector axes: a flexible
# cable has no PCB-like orthogonal route. The selected assembly is 30 mm long;
# its remaining 3D slack, bend radius and retention close on the H5 coupon.
UI_RF_CABLES = (
    CableRoute(
        "s3_rf_jumper",
        ((21.0, 24.46), (16.0, 10.55)),
        "direct S3 U.FL-to-U.FL plan projection; 30-mm assembly slack closes at H5",
    ),
    CableRoute(
        "c5_rf_jumper",
        ((66.0, 24.38), (59.0, 10.55)),
        "direct C5 U.FL-to-U.FL plan projection; 30-mm assembly slack closes at H5",
    ),
)

# These are topology guides, not routed copper. They connect all ten radio
# sources to the matching outward antenna datum. S3/C5 and nRF guides continue
# after the visible microcoax at the board-mounted U.FL; the four direct paths
# begin at the receiver, CC1101 or SA818S source. KiCad owns final geometry.
ANTENNA_TOPOLOGY_GUIDES = (
    AntennaTopologyGuide(
        "s3_native_rf_pcb_guide",
        "S3-2G4",
        "ui-inner",
        "s3_rf_board_connector",
        "s3_external_rp_sma",
        ((15.7, 10.55), (15.7, 6.62), (15.7, 0.0)),
        "S3 board U.FL through forward coupler to outward S3 RP-SMA",
    ),
    AntennaTopologyGuide(
        "c5_native_rf_pcb_guide",
        "C5-2G4/5",
        "ui-inner",
        "c5_rf_board_connector",
        "c5_external_rp_sma",
        ((59.3, 10.55), (59.3, 6.62), (59.3, 0.0)),
        "C5 board U.FL through forward coupler to outward C5 RP-SMA",
    ),
    AntennaTopologyGuide(
        "receiver_fmsw_pcb_guide",
        "RX-FM/SW",
        "ui-inner",
        "receiver",
        "receiver_fmsw_external_sma",
        ((51.0, 54.8), (30.0, 49.0), (30.0, 0.0)),
        "Si4732 FMI matching and protection to outward FM/SW SMA",
    ),
    AntennaTopologyGuide(
        "receiver_amlw_pcb_guide",
        "RX-AM/LW",
        "ui-inner",
        "receiver",
        "receiver_amlw_external_sma",
        ((51.0, 56.2), (45.0, 52.0), (45.0, 0.0)),
        "Si4732 AMI coupling and protection to outward AM/LW SMA",
    ),
    AntennaTopologyGuide(
        "nrf0_pcb_guide",
        "N24-0",
        "rf-inner",
        "nrf0_rf_board_connector",
        "nrf0_external_sma",
        ((24.5, 29.55), (9.5, 29.55), (9.5, 5.0), (8.1, 5.0), (8.1, 0.0)),
        "nRF24 #0 board U.FL through forward coupler to outward SMA",
    ),
    AntennaTopologyGuide(
        "nrf1_pcb_guide",
        "N24-1",
        "rf-inner",
        "nrf1_rf_board_connector",
        "nrf1_external_sma",
        ((51.5, 29.55), (51.75, 27.0), (51.75, 5.0), (29.9, 5.0), (29.9, 0.0)),
        "nRF24 #1 board U.FL through forward coupler to outward SMA",
    ),
    AntennaTopologyGuide(
        "nrf2_pcb_guide",
        "N24-2",
        "rf-inner",
        "nrf2_rf_board_connector",
        "nrf2_external_sma",
        ((71.5, 23.55), (65.2, 27.5), (65.2, 5.0), (66.9, 5.0), (66.9, 0.0)),
        "nRF24 #2 board U.FL through forward coupler to outward SMA",
    ),
    AntennaTopologyGuide(
        "cc_sub_pcb_guide",
        "CC-SUB",
        "rf-inner",
        "cc",
        "cc_external_sma",
        ((19.0, 10.3), (19.0, 0.0)),
        "CC1101 selected matching branch to outward Sub-GHz SMA",
    ),
    AntennaTopologyGuide(
        "voice_v_pcb_guide",
        "VOICE-VHF",
        "rf-inner",
        "voice_v",
        "voice_v_external_sma",
        tuple(reversed(VOICE_V_RF_CORRIDOR)),
        "SA818S-V contact 12 to outward VHF 134-174-MHz SMA",
    ),
    AntennaTopologyGuide(
        "voice_u_pcb_guide",
        "VOICE-UHF",
        "rf-inner",
        "voice",
        "voice_external_sma",
        tuple(reversed(VOICE_U_RF_CORRIDOR)),
        "SA818S-U contact 12 to outward UHF 400-480-MHz SMA",
    ),
)

RF_INNER = (
    Placement("nrf0_rf_board_connector", 23.0, 28.0, "nRF24 #0 Gen1 jumper board receptacle"),
    Placement("nrf1_rf_board_connector", 50.0, 28.0, "nRF24 #1 Gen1 jumper board receptacle"),
    Placement("nrf2_rf_board_connector", 70.0, 22.0, "nRF24 #2 Gen1 jumper board receptacle"),
    Placement("rp", 0.0, 32.2, "deterministic radio owner"),
    Placement("nrf0", 10.0, 7.5, "full-function nRF24 radio #0"),
    Placement("nrf1", 31.5, 7.5, "full-function nRF24 radio #1; rotated for U214 tail clearance", 90),
    Placement("nrf2", 52.9, 7.5, "full-function nRF24 radio #2"),
    Placement("voice_v", 15.8, 32.5, "VHF 134-174-MHz SA818S-V; dedicated contact-12 RF path", 180),
    Placement("voice", 52.2, 32.5, "UHF 400-480-MHz SA818S-U; dedicated contact-12 RF path", 270),
    Placement("cc", 24.0, 8.3, "multi-band sub-GHz transceiver inside its local reference RF zone"),
    Placement("nvdc_charger", 1.0, 63.0, "2S charger and NVDC power path"),
    Placement("pack_gauge", 1.0, 84.0, "2S protection and fuel gauge"),
    Placement("pack_admission", 5.7, 84.0, "fail-closed battery admission MCU"),
    Placement("aon_buck", 43.0, 61.0, "always-on 3.3-V converter"),
    Placement("main_buck", 20.0, 61.0, "main 3.3-V converter"),
    Placement("voice_buck", 28.0, 61.0, "voice 4.0-V converter"),
    Placement("ext_buck", 36.0, 61.0, "accessory 5.0-V converter"),
    Placement("power_zone_ntc", 25.5, 84.0, "power-conversion hotspot safety sensor"),
    Placement("rf_zone_ntc", 72.0, 56.0, "RF/voice hotspot safety sensor"),
    Placement("safety_controller", 36.0, 87.0, "independent watchdog, thermal and TX-lease controller"),
    Placement("safety_watchdog", 37.0, 94.0, "independent 1.6-s timeout watchdog"),
    Placement("safe_conditioner", 42.0, 94.0, "RUN and S3 fault-reset conditioner"),
    Placement("safe_latch", 37.0, 82.0, "asynchronous RUN_PERMIT / FAULT_KILL latch"),
    Placement("safe_reset_buffer", 41.0, 82.0, "C5/RP fault-reset buffer"),
    Placement("safe_fault_reset_buffer", 44.5, 85.0, "direct FAULT_ASSERT_N C5/RP reset and voice eFuse clamp"),
    Placement("safe_rearm_buffer", 44.0, 82.0, "delayed physical re-arm Schmitt buffer"),
    Placement("safe_supervisor", 49.0, 82.0, "always-on safety supervisor"),
    Placement("safe_reset_sink_b", 55.0, 82.0, "RP reset sink"),
    Placement("safe_ptt_or", 59.0, 82.0, "FAULT_KILL-dominant voice PTT gate"),
    Placement("safe_gate_b", 49.0, 88.0, "rear-domain transmit safety gates"),
    Placement("cc_backup_gate", 57.0, 100.0, "independent FAULT_ASSERT_N CC1101 rail qualifier"),
    Placement("evidence_cmp_b", 58.0, 88.0, "RF-local nRF/CC TX evidence comparator"),
    Placement("evidence_cmp_voice", 66.0, 88.0, "RF-local voice TX evidence comparator"),
    Placement("product_usb_protector", 7.5, 135.0, "product USB CC/USB2 protector"),
    Placement("pd_controller", 11.5, 134.5, "sink-only USB-PD controller"),
    Placement("speaker_amp", 31.0, 87.0, "rear-local differential speaker amplifier"),
    Placement("safe_gate_a", 49.0, 94.0, "nRF-domain transmit safety gates"),
    Placement("nrf_backup_gate", 54.0, 100.0, "independent FAULT_ASSERT_N nRF rail qualifier"),
    Placement("m1_rf_receptacle", 22.2, 119.0, "80-contact M1 receptacle; 11-mm board stack"),
    Placement("product_usb_connector", 12.0, 143.1, "product USB-C data and sink"),
    Placement("rp_service_usb_connector", 33.0, 142.65, "RP data-only service USB"),
    Placement("unit_connector", 51.0, 140.9, "native M5 Unit HY2.0-4P edge receptacle"),
    Placement("microphone", 45.0, 146.0, "rear bottom-facing microphone"),
    Placement("speaker", 50.0, 127.0, "internal 4-Ohm differential speaker"),
    Placement("rp_dbg_header", 40.0, 104.0, "keyed RP SWD/RUN/USB_BOOT header"),
    Placement("rp_reset_button", 0.0, 106.0, "external left-side RP RUN/RESET service control", 90),
    Placement("rp_boot_button", 0.0, 113.0, "external left-side RP USB_BOOT service control", 90),
    Placement("power_command_switch", 65.8, 111.0, "single low-current RUN/KILL; charging remains available in KILL"),

    Placement("voice_band_io", 44.0, 68.8, "TCA9534A UHF/VHF selector and deterministic reset straps"),
    Placement("voice_control_mux_a", 49.7, 68.8, "selected-module UART multiplexer"),
    Placement("voice_control_mux_b", 53.55, 68.8, "selected-module PTT and AUDIO_ON multiplexer"),
    Placement("voice_audio_mux", 44.0, 74.55, "selected-module AFOUT and microphone multiplexer", 90),
    Placement("voice_band_inverter", 49.75, 74.55, "AON complement for one-hot voice selection"),
    Placement("voice_pd_gate", 52.45, 74.55, "AON mutually-exclusive voice PD gate"),
    Placement("u214_host_buffer_a", 16.0, 52.55, "U214 host-command buffer A"),
    Placement("u214_host_buffer_b", 21.8, 52.55, "U214 host-command buffer B"),
    Placement("u214_return_buffer", 27.6, 52.55, "U214 return-path buffer"),
    Placement("u214_i2c_iso", 33.45, 52.55, "U214 hot-swap I2C isolation and stuck-bus recovery"),
    Placement("nrf0_host_buffer", 0.0, 26.8, "nRF24 #0 host-command buffer"),
    Placement("nrf0_return_buffer", 6.0, 26.8, "nRF24 #0 return-path buffer"),
    Placement("nrf1_host_buffer", 37.3, 52.55, "nRF24 #1 host-command buffer"),
    Placement("nrf1_return_buffer", 43.1, 52.55, "nRF24 #1 return-path buffer"),
    Placement("nrf2_host_buffer", 46.15, 52.55, "nRF24 #2 host-command buffer"),
    Placement("nrf2_return_buffer", 55.6, 74.55, "nRF24 #2 return-path buffer"),
    Placement("cc_host_buffer", 57.4, 68.8, "CC1101 host-command buffer"),
    Placement("cc_return_buffer", 63.2, 68.8, "CC1101 return-path buffer"),
    Placement("cc_band_buffer", 58.65, 74.55, "CC1101 band-select buffer"),

    # High-profile and high-current support parts are explicit physical bodies,
    # not hidden inside a generic power-zone rectangle.
    Placement("charger_inductor", 6.0, 62.4, "BQ25798 2.2-uH switching inductor"),
    Placement("charger_vbus_cap0", 1.0, 69.0, "BQ25798 VBUS bulk capacitor #0"),
    Placement("charger_vbus_cap1", 4.9, 69.0, "BQ25798 VBUS bulk capacitor #1"),
    Placement("charger_pmid_cap0", 8.8, 69.0, "BQ25798 PMID bulk capacitor #0"),
    Placement("charger_pmid_cap1", 12.7, 69.0, "BQ25798 PMID bulk capacitor #1"),
    Placement("charger_pmid_cap2", 1.0, 71.3, "BQ25798 PMID bulk capacitor #2"),
    Placement("charger_sys_cap0", 4.9, 71.3, "BQ25798 SYS bulk capacitor #0"),
    Placement("charger_sys_cap1", 8.8, 71.3, "BQ25798 SYS bulk capacitor #1"),
    Placement("charger_sys_cap2", 12.7, 71.3, "BQ25798 SYS bulk capacitor #2"),
    Placement("charger_sys_cap3", 1.0, 73.6, "BQ25798 SYS bulk capacitor #3"),
    Placement("charger_sys_cap4", 4.9, 73.6, "BQ25798 SYS bulk capacitor #4"),
    Placement("charger_bat_cap0", 8.8, 73.6, "BQ25798 BAT bulk capacitor #0"),
    Placement("charger_bat_cap1", 12.7, 73.6, "BQ25798 BAT bulk capacitor #1"),
    Placement("charger_regn_cap", 1.0, 75.9, "BQ25798 REGN local capacitor"),

    Placement("main_inductor", 19.0, 64.0, "main 3.3-V 3.3-uH switching inductor"),
    Placement("main_input_cap", 19.0, 70.0, "main 3.3-V input bulk capacitor"),
    Placement("main_output_cap0", 22.9, 70.0, "main 3.3-V output bulk capacitor #0"),
    Placement("main_output_cap1", 19.0, 73.2, "main 3.3-V output bulk capacitor #1"),
    Placement("voice_inductor", 27.0, 64.0, "voice 4.0-V 3.3-uH switching inductor"),
    Placement("voice_input_cap", 27.0, 70.0, "voice 4.0-V input bulk capacitor"),
    Placement("voice_output_cap0", 30.9, 70.0, "voice 4.0-V output bulk capacitor #0"),
    Placement("voice_output_cap1", 27.0, 73.2, "voice 4.0-V output bulk capacitor #1"),
    Placement("ext_inductor", 35.0, 64.0, "accessory 5.0-V 4.7-uH switching inductor"),
    Placement("ext_buck_input_cap", 35.0, 70.0, "accessory 5.0-V input bulk capacitor"),
    Placement("ext_buck_output_cap0", 39.0, 70.0, "accessory 5.0-V output bulk capacitor #0"),
    Placement("ext_buck_output_cap1", 35.0, 73.2, "accessory 5.0-V output bulk capacitor #1"),
    Placement("aon_inductor", 46.0, 64.0, "always-on 3.3-V 2.2-uH switching inductor"),
    Placement("aon_input_cap", 42.0, 64.0, "always-on 3.3-V input capacitor"),
    Placement("aon_output_cap", 42.0, 66.3, "always-on 3.3-V output capacitor"),

    Placement("pack_fuse0", 1.0, 80.0, "protected-pack branch fuse #0"),
    Placement("pack_fuse1", 7.8, 80.0, "protected-pack branch fuse #1"),
    Placement("pack_shunt", 14.6, 80.0, "Kelvin pack-current shunt"),
    Placement("pack_power_fet", 21.7, 80.0, "back-to-back pack admission FET"),
    Placement("pack_diag_res0", 11.5, 84.0, "pack diagnostic pulse resistor #0"),
    Placement("pack_diag_res1", 18.5, 84.0, "pack diagnostic pulse resistor #1"),
    Placement("evidence_mask", 61.7, 74.55, "AON evidence-source mask expander"),

    Placement("pd_pphv_cap0", 1.0, 127.0, "USB-PD high-voltage bulk capacitor #0"),
    Placement("pd_pphv_cap1", 4.9, 127.0, "USB-PD high-voltage bulk capacitor #1"),
    Placement("pd_pphv_cap2", 8.8, 127.0, "USB-PD high-voltage bulk capacitor #2"),
    Placement("pd_pphv_cap3", 12.7, 127.0, "USB-PD high-voltage bulk capacitor #3"),
    Placement("pd_config_eeprom", 16.3, 134.5, "TPS25751 configuration EEPROM"),
    Placement("pd_vbus_cap", 22.0, 134.5, "raw VBUS local capacitor"),
    Placement("pd_vbus_tvs", 26.0, 134.5, "raw VBUS flat-clamp TVS"),
)

# Ebyte publishes the module and land-pattern envelope but not the current-lot
# Gen1 receptacle axis.  The complete module face therefore remains a legal
# cable-head zone; only the short escape to the exact board receptacle is fixed.
# Cable slack stays above that face, while bend/retention closes on the H5 coupon.
RF_NRF_CABLE_RESERVES = (
    CableReserve(
        "nrf0_rf_jumper",
        "nrf0",
        "nrf0_rf_board_connector",
        ((22.1, 25.0), (24.5, 29.55)),
        "direct nRF24 #0 IPEX-zone-to-board-U.FL projection; module axis closes at H5",
    ),
    CableReserve(
        "nrf1_rf_jumper",
        "nrf1",
        "nrf1_rf_board_connector",
        ((49.0, 19.6), (51.5, 29.55)),
        "direct nRF24 #1 IPEX-zone-to-board-U.FL projection; module axis closes at H5",
    ),
    CableReserve(
        "nrf2_rf_jumper",
        "nrf2",
        "nrf2_rf_board_connector",
        ((65.0, 23.55), (71.5, 23.55)),
        "direct nRF24 #2 IPEX-zone-to-board-U.FL projection; module axis closes at H5",
    ),
)

SIDE_FUNCTION_CONTROLS = (
    Placement("ui_switch_f1", 1.8, 19.5, "front-left function F1"),
    Placement("ui_switch_f2", 1.8, 33.0, "front-left function F2"),
    Placement("ui_switch_f3", 1.8, 46.5, "front-left function F3"),
    Placement("ui_switch_f4", 1.8, 60.0, "front-left function F4"),
    Placement("ui_switch_f5", 66.6, 19.5, "front-right function F5"),
    Placement("ui_switch_f6", 66.6, 33.0, "front-right function F6"),
    Placement("ui_switch_f7", 66.6, 46.5, "front-right function F7"),
    Placement("ui_switch_f8", 66.6, 60.0, "front-right function F8"),
)

BOTTOM_NAV_CONTROLS = (
    Placement("ui_switch_back", 11.0, 129.4, "direct-press BACK"),
    Placement("ui_dpad_up", 34.2, 120.4, "direct-press navigation UP"),
    Placement("ui_dpad_down", 34.2, 138.4, "direct-press navigation DOWN"),
    Placement("ui_dpad_left", 25.2, 129.4, "direct-press navigation LEFT"),
    Placement("ui_dpad_right", 43.2, 129.4, "direct-press navigation RIGHT"),
    Placement("ui_dpad_ok", 34.2, 129.4, "direct-press navigation OK"),
    Placement("ui_switch_opt", 57.4, 129.4, "direct-press OPT"),
)

FRONT_CONTROLS = SIDE_FUNCTION_CONTROLS + BOTTOM_NAV_CONTROLS

DIRECT_PRESS_FRONT_CONTROLS = {item.instance for item in FRONT_CONTROLS}

REAR_CONTROLS = (
    Placement("encoder", 2.15, 44.5, "rear through-hole encoder"),
    Placement("ptt_switch", 64.2, 63.5, "rear independent PTT"),
)

DIRECT_PRESS_REAR_CONTROLS = {"ptt_switch"}

FRONT_CAP_RESERVES = ()

REAR_CAP_RESERVES = ()
REAR_CAP_TO_CONTROL = {}

REAR_SELECTED_ACTUATORS = (
    Placement("encoder_knob", 0.5, 43.0, "exact soft-touch knob over rear encoder"),
)

INTERNAL_RESERVES = (
    Reserve(
        "cc-reference-rf-network",
        22.9,
        7.5,
        7.9,
        17.5,
        "CC1101 broadband balun, switched band matching, detector tap and ESD zone",
        "selected_support_placement_zone",
    ),
)
INTERNAL_ZONE_ALLOWED_INSTANCES = {
    "cc-reference-rf-network": {"cc"},
}

# Bodies that are mechanically accounted for by a dedicated assembly or
# exterior projection rather than by one of the two inner-face placement maps.
MECHANICAL_ASSEMBLY_EMBEDDED_INSTANCES = {
    "display_touch_controller", "display_adapter_plug", "display_panel_connector",
}
MECHANICAL_EXTERIOR_INSTANCES = {
    "display", "u214", "pack_holder", "pack_cell0", "pack_cell1",
    *RF_INSTANCE_BY_PATH.values(),
    *(instance for instance, _, _, _ in FRONT_FACE_INDICATORS),
    *(route.instance for route in UI_RF_CABLES),
    *(reserve.instance for reserve in RF_NRF_CABLE_RESERVES),
}

REAR_OUTER = (
    Placement(
        "u214_connector",
        U214_CONNECTOR_X,
        U214_CONNECTOR_Y,
        "vertical host socket on the raised rear Cap-Bus rail",
    ),
)

# H1.1.2 source-normalisation contract. Placement coordinates always use the
# top-left of the rotated, axis-aligned manufacturer envelope. Rotations are
# clockwise in the named view. Each PCB face is authored as seen from its own
# exterior, so the rear board is mirrored only when it is transformed into the
# front-board datum for interboard collision checks.
MECHANICAL_PROJECTION_FRAMES = {
    "ui-inner": "UI PCB top-left, viewed from the front/exterior",
    "rf-inner": "RF/power PCB top-left, viewed from the rear/exterior",
    "front-outer": "UI PCB top-left, viewed from the front/exterior",
    "rear-outer": "RF/power PCB top-left, viewed from the rear/exterior",
    "ui-inner-route": "UI PCB top-left, viewed from the front/exterior",
    "rf-inner-route": "RF/power PCB top-left, viewed from the rear/exterior",
    "display-assembly": "HMX035CTFT-001 screen-body top-left, front view",
    "display-adapter": "L2-DISP-ADP-001-A top-left, viewed from its panel-facing side",
}

PLACEMENT_PROJECTION_GROUPS = (
    ("ui-inner", UI_INNER),
    ("rf-inner", RF_INNER),
    ("front-outer", FRONT_CONTROLS),
    ("rear-outer", REAR_CONTROLS),
    ("rear-outer", REAR_OUTER),
    ("rear-outer", REAR_SELECTED_ACTUATORS),
)

INTERNAL_CONNECTOR_ACTUATOR_DIRECTIONS = {
    "display_connector": "normal to the UI-inner face toward the replaceable adapter plug",
    "display_adapter_plug": "normal to the adapter underside toward the UI-board receptacle",
    "display_panel_connector": "horizontal FPC insertion in the adapter plane; dual-contact orientation; received-tail thickness remains H5 evidence",
    "s3_rf_board_connector": "normal to the UI-inner face toward the cable plug",
    "c5_rf_board_connector": "normal to the UI-inner face toward the cable plug",
    "nrf0_rf_board_connector": "normal to the RF-inner face toward the Gen1 cable plug",
    "nrf1_rf_board_connector": "normal to the RF-inner face toward the Gen1 cable plug",
    "nrf2_rf_board_connector": "normal to the RF-inner face toward the Gen1 cable plug",
    "m1_ui_plug": "normal to the UI-inner face toward the RF/power board",
    "m1_rf_receptacle": "normal to the RF-inner face toward the UI board",
    "s3_dbg_header": "normal to the UI-inner face; enclosure-open service only",
    "c5_dbg_header": "normal to the UI-inner face; enclosure-open service only",
    "rp_dbg_header": "normal to the RF-inner face; enclosure-open service only",
    "s3_reset_button": "parallel to the UI PCB toward the left enclosure side; externally operable",
    "s3_boot_button": "parallel to the UI PCB toward the left enclosure side; externally operable",
    "c5_reset_button": "parallel to the UI PCB toward the right enclosure side; externally operable",
    "c5_boot_button": "parallel to the UI PCB toward the right enclosure side; externally operable",
    "rp_reset_button": "parallel to the RF PCB toward the left enclosure side; externally operable",
    "rp_boot_button": "parallel to the RF PCB toward the left enclosure side; externally operable",
    "nrf0": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "nrf1": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "nrf2": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "voice": "contact 12 faces the antenna edge along the dedicated UHF corridor",
    "voice_v": "contact 12 faces the antenna edge along the dedicated VHF corridor",
}

DIRECTIONAL_BODY_DIRECTIONS = {
    **INTERNAL_CONNECTOR_ACTUATOR_DIRECTIONS,
    **{
        instance: f"{face} {side} enclosure exit"
        for instance, face, side, _, _ in EDGE_INTERFACES
    },
    **{
        instance: f"{face} {side} labelled internal acoustic component"
        for instance, face, side, _, _ in EXTERNAL_COMPONENT_LABELS
    },
    **{item.instance: "front-normal outward actuation" for item in FRONT_CONTROLS},
    **{item.instance: "rear-normal outward actuation" for item in REAR_CONTROLS},
    **{item.instance: "rear-normal outward actuation" for item in REAR_SELECTED_ACTUATORS},
    "microphone": "bottom enclosure exit; physical body on RF-inner; user silkscreen on front-outer",
    "u214_connector": "rear-normal outward mating into the removable Cap",
}

EXTERIOR_BODY_CONTRACTS = (
    BodyProjectionContract("display", "front-outer", 0, "front-normal outward view/touch"),
    BodyProjectionContract("u214", "rear-outer", 0, "rear-normal dock mating/removal"),
    BodyProjectionContract("pack_holder", "rear-outer", 90, "rear-normal open-cell access"),
    BodyProjectionContract("pack_cell0", "rear-outer", 90, "rear-normal cell insertion/removal"),
    BodyProjectionContract("pack_cell1", "rear-outer", 90, "rear-normal cell insertion/removal"),
    *(
        BodyProjectionContract(
            RF_INSTANCE_BY_PATH[path],
            "front-outer",
            0,
            "toward the antenna edge along board -Y",
        )
        for _, path, _ in FRONT_RF
    ),
    *(
        BodyProjectionContract(
            RF_INSTANCE_BY_PATH[path],
            "rear-outer",
            0,
            "toward the antenna edge along board -Y",
        )
        for _, path, _ in REAR_RF
    ),
    *(
        BodyProjectionContract(instance, "front-outer", 0, "front-normal optical emission")
        for instance, _, _, _ in FRONT_FACE_INDICATORS
    ),
    *(
        BodyProjectionContract(route.instance, "ui-inner-route", 0, "module-to-board RF cable path")
        for route in UI_RF_CABLES
    ),
    *(
        BodyProjectionContract(
            reserve.instance,
            "rf-inner-route",
            0,
            "bounded module-face zone to fixed Gen1 board receptacle; exact axis closes in H5",
        )
        for reserve in RF_NRF_CABLE_RESERVES
    ),
    BodyProjectionContract(
        "display_touch_controller",
        "display-assembly",
        0,
        "embedded in HMX035CTFT-001; no separate mechanical interface",
    ),
    BodyProjectionContract(
        "display_adapter_plug",
        "display-adapter",
        0,
        "normal to the adapter underside toward the UI-board receptacle",
    ),
    BodyProjectionContract(
        "display_panel_connector",
        "display-adapter",
        0,
        "horizontal FPC insertion in the adapter plane; dual-contact orientation; received-tail thickness remains H5 evidence",
    ),
)


def load() -> tuple[dict, dict, dict, dict, dict, dict]:
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    navigation_cluster = json.loads(NAVIGATION_CLUSTER_PATH.read_text(encoding="utf-8"))
    display_adapter_design = json.loads(DISPLAY_ADAPTER_DESIGN_PATH.read_text(encoding="utf-8"))
    assembly_coordinate_model = json.loads(ASSEMBLY_COORDINATE_MODEL_PATH.read_text(encoding="utf-8"))
    return (
        devices, candidate, candidate["instances"], navigation_cluster,
        display_adapter_design, assembly_coordinate_model,
    )


def placement_size(item: Placement, devices: dict, instances: dict) -> tuple[float, float]:
    device = devices[instances[item.instance]]
    dimensions = device.get("maximum_dimensions_mm", device.get("dimensions_mm"))
    if not dimensions or len(dimensions) < 2 or dimensions[0] is None or dimensions[1] is None:
        raise ValueError(f"{item.instance}: two-dimensional package envelope is missing")
    w, h = float(dimensions[0]), float(dimensions[1])
    angle = math.radians(item.rotation % 180)
    return (
        abs(w * math.cos(angle)) + abs(h * math.sin(angle)),
        abs(w * math.sin(angle)) + abs(h * math.cos(angle)),
    )


def placed_contact_xy(
    item: Placement, device: dict, contact_xy: tuple[float, float]
) -> tuple[float, float]:
    """Transform a manufacturer top-left contact coordinate into board space."""
    width, height = map(float, device["dimensions_mm"][:2])
    contact_x, contact_y = contact_xy
    rotation = item.rotation % 360
    if rotation == 0:
        local_x, local_y = contact_x, contact_y
    elif rotation == 90:
        local_x, local_y = height - contact_y, contact_x
    elif rotation == 180:
        local_x, local_y = width - contact_x, height - contact_y
    elif rotation == 270:
        local_x, local_y = contact_y, width - contact_x
    else:
        raise ValueError(f"{item.instance}: unsupported contact rotation {rotation}")
    return item.x + local_x, item.y + local_y


def placement_height(item: Placement, devices: dict, instances: dict) -> float:
    """Return the manufacturer-backed body height recorded for a placed part."""
    device = devices[instances[item.instance]]
    dimensions = device.get("maximum_dimensions_mm", device.get("dimensions_mm"))
    if not dimensions or len(dimensions) < 3 or dimensions[2] is None:
        raise ValueError(f"{item.instance}: package height is missing")
    height = float(dimensions[2])
    if height <= 0:
        raise ValueError(f"{item.instance}: package height must be positive")
    return height


def encoder_through_board_features(
    devices: dict,
    instances: dict,
) -> tuple[ThroughBoardFeature, ...]:
    """Project the exact EC11E mounting tabs and five terminals into the gap."""
    encoder = next(item for item in REAR_CONTROLS if item.instance == "encoder")
    if encoder.rotation != 0:
        raise ValueError("encoder through-board feature map currently requires drawing orientation 0")
    width, height = placement_size(encoder, devices, instances)
    center_x = encoder.x + width / 2
    center_y = encoder.y + height / 2
    contract = devices[instances["encoder"]]["mechanical_contract"]
    inner_height = float(contract["inner_terminal_projection_mm"])
    dummy_w, dummy_h = map(float, contract["maximum_dummy_terminal_hole_mm"])
    pin_d = float(contract["maximum_signal_terminal_hole_diameter_mm"])
    rows: list[ThroughBoardFeature] = []
    for index, (dx, dy) in enumerate(contract["dummy_terminal_centres_mm"], 1):
        rows.append(
            ThroughBoardFeature(
                "encoder", f"dummy_terminal_{index}",
                center_x + float(dx) - dummy_w / 2,
                center_y + float(dy) - dummy_h / 2,
                dummy_w, dummy_h, inner_height,
                "EC11E mechanical terminal and maximum mounting-hole envelope",
            )
        )
    for names, key in (
        (("D", "E"), "switch_terminal_centres_mm"),
        (("A", "C", "B"), "encoder_terminal_centres_mm"),
    ):
        for name, (dx, dy) in zip(names, contract[key]):
            rows.append(
                ThroughBoardFeature(
                    "encoder", f"contact_{name}",
                    center_x + float(dx) - pin_d / 2,
                    center_y + float(dy) - pin_d / 2,
                    pin_d, pin_d, inner_height,
                    "EC11E electrical terminal and maximum plated-hole envelope",
                )
            )
    return tuple(rows)


def nrf_cable_reserve_module_box(
    reserve: CableReserve,
    devices: dict,
    instances: dict,
) -> tuple[float, float, float, float]:
    module = next(item for item in RF_INNER if item.instance == reserve.module_instance)
    width, height = placement_size(module, devices, instances)
    return module.x, module.y, width, height


def interboard_individual_clearances(
    devices: dict,
    instances: dict,
) -> list[tuple[float, Placement]]:
    """Return each inner body's remaining distance to the opposite PCB plane."""
    rows = [
        (INTERBOARD_GAP_MM - placement_height(item, devices, instances), item)
        for item in UI_INNER + RF_INNER
    ]
    return sorted(rows, key=lambda row: (row[0], row[1].instance))


def mirrored_x(x: float, width: float = 0.0) -> float:
    """Mirror a point or left edge across the 75-mm board centreline."""
    return BOARD_W - x - width


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float], margin: float = 0.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw + margin and bx < ax + aw + margin and ay < by + bh + margin and by < ay + ah + margin


def interboard_clearance_pairs(
    devices: dict,
    instances: dict,
) -> list[tuple[float, Placement, Placement]]:
    """Calculate every non-mating pair projected into the same physical datum.

    Placement X is authored as seen from each board's external face.  The rear
    RF/power board therefore has to be mirrored into the front-board datum
    before the two inner faces can be compared.
    """
    pairs: list[tuple[float, Placement, Placement]] = []
    for ui_item in UI_INNER:
        ui_w, ui_h = placement_size(ui_item, devices, instances)
        ui_box = (ui_item.x, ui_item.y, ui_w, ui_h)
        for rf_item in RF_INNER:
            rf_w, rf_h = placement_size(rf_item, devices, instances)
            rf_box = (mirrored_x(rf_item.x, rf_w), rf_item.y, rf_w, rf_h)
            if not overlaps(ui_box, rf_box):
                continue
            if (ui_item.instance, rf_item.instance) in INTENTIONAL_INTERBOARD_MATES:
                continue
            clearance = (
                INTERBOARD_GAP_MM
                - placement_height(ui_item, devices, instances)
                - placement_height(rf_item, devices, instances)
            )
            pairs.append((clearance, ui_item, rf_item))
    return sorted(pairs, key=lambda row: (row[0], row[1].instance, row[2].instance))


def display_adapter_opposing_clearance_pairs(
    design: dict,
    devices: dict,
    instances: dict,
) -> list[tuple[float, Placement]]:
    """Check the complete elevated display-adapter envelope against RF-inner."""
    board = design["board"]
    adapter_x, adapter_y = map(float, board["ui_inner_position_mm"])
    adapter_box = (
        adapter_x,
        adapter_y,
        float(board["width_mm"]),
        float(board["height_mm"]),
    )
    adapter_height = float(design["stack"]["ui_board_to_panel_connector_top_mm"])
    rows: list[tuple[float, Placement]] = []
    for rf_item in RF_INNER:
        rf_w, rf_h = placement_size(rf_item, devices, instances)
        rf_box = (mirrored_x(rf_item.x, rf_w), rf_item.y, rf_w, rf_h)
        if overlaps(adapter_box, rf_box):
            rows.append(
                (
                    INTERBOARD_GAP_MM
                    - adapter_height
                    - placement_height(rf_item, devices, instances),
                    rf_item,
                )
            )
    return sorted(rows, key=lambda row: (row[0], row[1].instance))


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


def polyline_length(points: tuple[tuple[float, float], ...]) -> float:
    return sum(
        math.hypot(x2 - x1, y2 - y1)
        for (x1, y1), (x2, y2) in zip(points, points[1:])
    )


def point_segment_distance(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    px, py = point
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    denominator = dx * dx + dy * dy
    if denominator == 0:
        return math.hypot(px - x1, py - y1)
    amount = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / denominator))
    return math.hypot(px - (x1 + amount * dx), py - (y1 + amount * dy))


def axis_aligned_segment_hits_box(
    start: tuple[float, float],
    end: tuple[float, float],
    rectangle: tuple[float, float, float, float],
    margin: float = 0.0,
) -> bool:
    """Return whether a horizontal/vertical route corridor meets a box."""
    x1, y1 = start
    x2, y2 = end
    x, y, w, h = rectangle
    left, right = x - margin, x + w + margin
    top, bottom = y - margin, y + h + margin
    if abs(y1 - y2) < 0.001:
        return top <= y1 <= bottom and max(min(x1, x2), left) <= min(max(x1, x2), right)
    if abs(x1 - x2) < 0.001:
        return left <= x1 <= right and max(min(y1, y2), top) <= min(max(y1, y2), bottom)
    raise ValueError(f"non-orthogonal cable segment {start}/{end}")


def segment_hits_box(
    start: tuple[float, float],
    end: tuple[float, float],
    rectangle: tuple[float, float, float, float],
    margin: float = 0.0,
) -> bool:
    """Return whether any straight segment meets an expanded axis-aligned box."""
    x, y, w, h = rectangle
    left, right = x - margin, x + w + margin
    top, bottom = y - margin, y + h + margin
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    lower, upper = 0.0, 1.0
    for direction, near_delta, far_delta in (
        (dx, x1 - left, right - x1),
        (dy, y1 - top, bottom - y1),
    ):
        if abs(direction) < 1e-12:
            if near_delta < 0 or far_delta < 0:
                return False
            continue
        first = -near_delta / direction
        second = far_delta / direction
        if first > second:
            first, second = second, first
        lower = max(lower, first)
        upper = min(upper, second)
        if lower > upper:
            return False
    return True


def cable_interboard_clearance_pairs(
    devices: dict,
    instances: dict,
) -> list[tuple[float, CableRoute, Placement]]:
    """Calculate cable/body pairs that overlap across the inner channel."""
    pairs: list[tuple[float, CableRoute, Placement]] = []
    for route in UI_RF_CABLES:
        device = devices[instances[route.instance]]
        cable_od = float(device["electrical_contract"]["cable_outer_diameter_mm"])
        cable_radius = cable_od / 2
        for rf_item in RF_INNER:
            rf_w, rf_h = placement_size(rf_item, devices, instances)
            rf_box = (mirrored_x(rf_item.x, rf_w), rf_item.y, rf_w, rf_h)
            if any(
                segment_hits_box(start, end, rf_box, cable_radius)
                for start, end in zip(route.points, route.points[1:])
            ):
                clearance = (
                    INTERBOARD_GAP_MM
                    - cable_od
                    - placement_height(rf_item, devices, instances)
                )
                pairs.append((clearance, route, rf_item))
    return sorted(pairs, key=lambda row: (row[0], row[1].instance, row[2].instance))


def nrf_cable_reserve_opposing_pairs(
    devices: dict,
    instances: dict,
) -> list[tuple[float, CableReserve, Placement]]:
    """Check the same-board RF-inner cable reserves against UI bodies."""
    pairs: list[tuple[float, CableReserve, Placement]] = []
    for reserve in RF_NRF_CABLE_RESERVES:
        cable = devices[instances[reserve.instance]]
        radius = float(cable["electrical_contract"]["cable_outer_diameter_mm"]) / 2
        occupied_height = max(
            float(cable["mechanical_contract"]["maximum_mated_height_mm"]),
            placement_height(
                next(item for item in RF_INNER if item.instance == reserve.module_instance),
                devices,
                instances,
            ),
        )
        module_box = nrf_cable_reserve_module_box(reserve, devices, instances)
        for ui_item in UI_INNER:
            ui_w, ui_h = placement_size(ui_item, devices, instances)
            ui_box = (mirrored_x(ui_item.x, ui_w), ui_item.y, ui_w, ui_h)
            if overlaps(module_box, ui_box) or any(
                segment_hits_box(start, end, ui_box, radius)
                for start, end in zip(reserve.escape_points, reserve.escape_points[1:])
            ):
                clearance = (
                    INTERBOARD_GAP_MM
                    - occupied_height
                    - placement_height(ui_item, devices, instances)
                )
                pairs.append((clearance, reserve, ui_item))
    return sorted(pairs, key=lambda row: (row[0], row[1].instance, row[2].instance))


def through_board_opposing_pairs(
    devices: dict,
    instances: dict,
) -> list[tuple[float, ThroughBoardFeature, Placement]]:
    """Check exterior THT terminals protruding into the gap against UI bodies."""
    pairs: list[tuple[float, ThroughBoardFeature, Placement]] = []
    for feature in encoder_through_board_features(devices, instances):
        feature_box = (feature.x, feature.y, feature.w, feature.h)
        for ui_item in UI_INNER:
            ui_w, ui_h = placement_size(ui_item, devices, instances)
            ui_box = (mirrored_x(ui_item.x, ui_w), ui_item.y, ui_w, ui_h)
            if overlaps(feature_box, ui_box):
                clearance = (
                    INTERBOARD_GAP_MM
                    - feature.inner_height
                    - placement_height(ui_item, devices, instances)
                )
                pairs.append((clearance, feature, ui_item))
    return sorted(pairs, key=lambda row: (row[0], row[1].feature, row[2].instance))


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
    holder = Placement("pack_holder", 17.6, PACK_HOLDER_Y, "holder", 90)
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
            *((label + " LED", (x, y, TX_LED_W, TX_LED_H)) for _, label, x, y in FRONT_FACE_INDICATORS),
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


def validate_cable_routes(devices: dict, instances: dict) -> list[str]:
    errors: list[str] = []
    ui_by_instance = {item.instance: item for item in UI_INNER}
    module_by_route = {
        "s3_rf_jumper": ("s3", "s3_rf_board_connector"),
        "c5_rf_jumper": ("c5", "c5_rf_board_connector"),
    }
    for route in UI_RF_CABLES:
        if route.instance not in instances:
            errors.append(f"native-rf-cable: unknown instance {route.instance}")
            continue
        device = devices[instances[route.instance]]
        expected_length = float(device["electrical_contract"]["cable_length_mm"])
        projected_length = polyline_length(route.points)
        if len(route.points) != 2:
            errors.append(
                f"native-rf-cable: {route.instance} must render as one direct connector-to-connector projection"
            )
        if projected_length >= expected_length:
            errors.append(
                f"native-rf-cable: {route.instance} {projected_length:.2f}-mm connector chord "
                f"cannot fit the selected {expected_length:.2f}-mm assembly"
            )
        cable_radius = float(device["electrical_contract"]["cable_outer_diameter_mm"]) / 2
        cable_od = cable_radius * 2
        if INTERBOARD_GAP_MM - cable_od < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(f"native-rf-cable: {route.instance} does not fit the interboard channel")
        for point in route.points:
            if not (cable_radius <= point[0] <= BOARD_W - cable_radius and cable_radius <= point[1] <= BOARD_H - cable_radius):
                errors.append(f"native-rf-cable: {route.instance} leaves the PCB plan at {point}")
        for segment in zip(route.points, route.points[1:]):
            for hole in HOLES:
                if point_segment_distance(hole, *segment) < MOUNT_KEEPOUT_R + cable_radius:
                    errors.append(f"native-rf-cable: {route.instance} enters the M2.5 keep-out at {hole}")

        module_instance, board_connector_instance = module_by_route[route.instance]
        module = ui_by_instance[module_instance]
        module_rf = devices[instances[module_instance]]["rf_connector"]["center_from_module_top_left_mm"]
        expected_start = (module.x + float(module_rf[0]), module.y + float(module_rf[1]))
        connector = ui_by_instance[board_connector_instance]
        connector_w, connector_h = placement_size(connector, devices, instances)
        expected_end = (connector.x + connector_w / 2, connector.y + connector_h / 2)
        if any(abs(a - b) > 0.01 for a, b in zip(route.points[0], expected_start)):
            errors.append(f"native-rf-cable: {route.instance} does not start at the official module RF axis")
        if any(abs(a - b) > 0.01 for a, b in zip(route.points[-1], expected_end)):
            errors.append(f"native-rf-cable: {route.instance} does not end at its board receptacle axis")

        allowed_contacts = {module_instance, board_connector_instance}
        for item in UI_INNER:
            if item.instance in allowed_contacts:
                continue
            item_w, item_h = placement_size(item, devices, instances)
            item_box = (item.x, item.y, item_w, item_h)
            route_hits = any(
                segment_hits_box(
                    start,
                    end,
                    item_box,
                    cable_radius + MIN_INTERBOARD_Z_CLEARANCE_MM,
                )
                for start, end in zip(route.points, route.points[1:])
            )
            if route_hits:
                errors.append(
                    f"native-rf-cable: {route.instance} lacks {MIN_INTERBOARD_Z_CLEARANCE_MM:.1f}-mm "
                    f"same-face clearance to {item.instance}"
                )

    if {route.instance for route in UI_RF_CABLES} != {"s3_rf_jumper", "c5_rf_jumper"}:
        errors.append("native-rf-cable: exact S3 and C5 jumper routes must both be present")
    for clearance, route, rf_item in cable_interboard_clearance_pairs(devices, instances):
        if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(
                f"native-rf-cable: {route.instance}/{rf_item.instance} leaves only "
                f"{clearance:.2f} mm across the interboard channel"
            )
    return errors


def validate_nrf_cable_reserves(devices: dict, instances: dict) -> list[str]:
    """Validate conservative RF-inner module-face reserves for all three nRF jumpers."""
    errors: list[str] = []
    rf_by_instance = {item.instance: item for item in RF_INNER}
    expected = {f"nrf{index}_rf_jumper" for index in range(3)}
    if {reserve.instance for reserve in RF_NRF_CABLE_RESERVES} != expected:
        errors.append("nrf-rf-cable: all three conservative jumper reserves must be present")
    for reserve in RF_NRF_CABLE_RESERVES:
        cable = devices[instances[reserve.instance]]
        contract = cable["electrical_contract"]
        mechanical = cable["mechanical_contract"]
        exact_length = float(contract["cable_length_mm"])
        cable_radius = float(contract["cable_outer_diameter_mm"]) / 2
        plug_plan = list(map(float, mechanical.get("maximum_plug_plan_envelope_mm", [])))
        if len(plug_plan) != 2 or plug_plan != [3.0, 3.1]:
            errors.append(f"nrf-rf-cable: {reserve.instance} lacks the exact Gen1 plug plan envelope")
        escape_length = polyline_length(reserve.escape_points)
        if not 0 < escape_length < exact_length:
            errors.append(f"nrf-rf-cable: {reserve.instance} escape cannot retain 30-mm cable slack")
        if len(reserve.escape_points) != 2:
            errors.append(
                f"nrf-rf-cable: {reserve.instance} must render as one direct IPEX-zone-to-U.FL projection"
            )
        module = rf_by_instance[reserve.module_instance]
        connector = rf_by_instance[reserve.board_connector_instance]
        module_box = nrf_cable_reserve_module_box(reserve, devices, instances)
        module_x, module_y, module_w, module_h = module_box
        first_x, first_y = reserve.escape_points[0]
        on_module_edge = (
            module_x - 0.01 <= first_x <= module_x + module_w + 0.01
            and module_y - 0.01 <= first_y <= module_y + module_h + 0.01
            and (
                abs(first_x - module_x) <= 0.01
                or abs(first_x - (module_x + module_w)) <= 0.01
                or abs(first_y - module_y) <= 0.01
                or abs(first_y - (module_y + module_h)) <= 0.01
            )
        )
        if not on_module_edge:
            errors.append(f"nrf-rf-cable: {reserve.instance} escape does not start on its module face")
        connector_w, connector_h = placement_size(connector, devices, instances)
        expected_end = (connector.x + connector_w / 2, connector.y + connector_h / 2)
        if any(abs(a - b) > 0.01 for a, b in zip(reserve.escape_points[-1], expected_end)):
            errors.append(f"nrf-rf-cable: {reserve.instance} escape misses its exact board receptacle")
        allowed = {reserve.module_instance, reserve.board_connector_instance}
        for segment in zip(reserve.escape_points, reserve.escape_points[1:]):
            for hole in HOLES:
                if point_segment_distance(hole, *segment) < MOUNT_KEEPOUT_R + cable_radius:
                    errors.append(f"nrf-rf-cable: {reserve.instance} enters the M2.5 keep-out at {hole}")
            for item in RF_INNER:
                if item.instance in allowed:
                    continue
                item_w, item_h = placement_size(item, devices, instances)
                if segment_hits_box(
                    *segment,
                    (item.x, item.y, item_w, item_h),
                    cable_radius + MIN_INTERBOARD_Z_CLEARANCE_MM,
                ):
                    errors.append(
                        f"nrf-rf-cable: {reserve.instance} escape lacks "
                        f"{MIN_INTERBOARD_Z_CLEARANCE_MM:.1f}-mm clearance to {item.instance}"
                    )
        for point in reserve.escape_points:
            if not (
                cable_radius <= point[0] <= BOARD_W - cable_radius
                and cable_radius <= point[1] <= BOARD_H - cable_radius
            ):
                errors.append(f"nrf-rf-cable: {reserve.instance} escape leaves the PCB plan at {point}")
        # The unknown current-lot axis may be anywhere in the module face.  The
        # controlled plug footprint is reserved inside that complete face; its
        # actual axis, bend and retention remain the already-declared H5 gate.
        if module_w < max(plug_plan or [999]) or module_h < max(plug_plan or [999]):
            errors.append(f"nrf-rf-cable: {reserve.instance} module face cannot contain its plug")
    for clearance, reserve, ui_item in nrf_cable_reserve_opposing_pairs(devices, instances):
        if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(
                f"nrf-rf-cable: {reserve.instance}/{ui_item.instance} leaves only "
                f"{clearance:.2f} mm across the interboard channel"
            )
    return errors


def validate_through_board_features(devices: dict, instances: dict) -> list[str]:
    """Validate THT tails that enter the gap from an externally mounted part."""
    errors: list[str] = []
    features = encoder_through_board_features(devices, instances)
    if len(features) != 7:
        errors.append("through-board: EC11E must expose two tabs and five terminal tails")
    for feature in features:
        feature_box = (feature.x, feature.y, feature.w, feature.h)
        if (
            feature.x < 0
            or feature.y < 0
            or feature.x + feature.w > BOARD_W
            or feature.y + feature.h > BOARD_H
        ):
            errors.append(f"through-board: encoder {feature.feature} leaves the PCB plan")
        if feature.inner_height + MIN_INTERBOARD_Z_CLEARANCE_MM > INTERBOARD_GAP_MM:
            errors.append(f"through-board: encoder {feature.feature} exceeds the 11-mm channel")
        for item in RF_INNER:
            item_w, item_h = placement_size(item, devices, instances)
            if overlaps(
                feature_box,
                (item.x, item.y, item_w, item_h),
                MIN_INTERBOARD_Z_CLEARANCE_MM,
            ):
                errors.append(
                    f"through-board: encoder {feature.feature} conflicts with {item.instance}"
                )
        for zone in INTERNAL_RESERVES:
            if overlaps(
                feature_box,
                (zone.x, zone.y, zone.w, zone.h),
                MIN_INTERBOARD_Z_CLEARANCE_MM,
            ):
                errors.append(f"through-board: encoder {feature.feature} conflicts with {zone.name}")
    for clearance, feature, ui_item in through_board_opposing_pairs(devices, instances):
        if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(
                f"through-board: encoder {feature.feature}/{ui_item.instance} leaves only "
                f"{clearance:.2f} mm across the interboard channel"
            )
    return errors


def validate_reserves(name: str, reserves: tuple[Reserve, ...]) -> list[str]:
    errors: list[str] = []
    for reserve in reserves:
        if reserve.reserve_class not in {
            "custom_actuator", "custom_enclosure_geometry", "unselected_bom_part",
            "selected_support_placement_zone",
        }:
            errors.append(f"{name}: {reserve.name} has invalid reserve class {reserve.reserve_class}")
        rectangle = (reserve.x, reserve.y, reserve.w, reserve.h)
        if reserve.x < 0 or reserve.y < 0 or reserve.x + reserve.w > BOARD_W or reserve.y + reserve.h > BOARD_H:
            errors.append(f"{name}: {reserve.name} is outside the 75x150-mm board")
        for hole in HOLES:
            if hits_hole(rectangle, hole):
                errors.append(f"{name}: {reserve.name} enters the M2.5 keep-out at {hole}")
    return errors


def mechanical_body_contracts() -> tuple[dict[str, BodyProjectionContract], list[str]]:
    """Build one traceable datum/orientation/direction contract per body."""
    contracts: dict[str, BodyProjectionContract] = {}
    errors: list[str] = []

    def register(contract: BodyProjectionContract) -> None:
        if contract.instance in contracts:
            errors.append(f"mechanical-source: duplicate body contract for {contract.instance}")
            return
        contracts[contract.instance] = contract

    for frame, items in PLACEMENT_PROJECTION_GROUPS:
        if frame not in MECHANICAL_PROJECTION_FRAMES:
            errors.append(f"mechanical-source: unknown projection frame {frame}")
        for item in items:
            register(
                BodyProjectionContract(
                    item.instance,
                    frame,
                    item.rotation,
                    DIRECTIONAL_BODY_DIRECTIONS.get(item.instance, "not applicable"),
                )
            )
    for contract in EXTERIOR_BODY_CONTRACTS:
        register(contract)
    return contracts, errors


def validate_mechanical_sources(devices: dict, instances: dict) -> tuple[set[str], list[str]]:
    """Enforce the H1.1.2 manufacturer-envelope and projection contract."""
    contracts, errors = mechanical_body_contracts()
    expected = (
        {
            item.instance
            for _, items in PLACEMENT_PROJECTION_GROUPS
            for item in items
        }
        | MECHANICAL_ASSEMBLY_EMBEDDED_INSTANCES
        | MECHANICAL_EXTERIOR_INSTANCES
    )
    actual = set(contracts)
    if actual != expected:
        missing = ", ".join(sorted(expected - actual)) or "none"
        extra = ", ".join(sorted(actual - expected)) or "none"
        errors.append(f"mechanical-source: contract coverage differs; missing={missing}; extra={extra}")

    for instance, contract in contracts.items():
        if instance not in instances:
            errors.append(f"mechanical-source: unknown instance {instance}")
            continue
        device = devices[instances[instance]]
        mpn = device.get("mpn", "")
        if not isinstance(mpn, str) or not mpn.strip():
            errors.append(f"mechanical-source: {instance} has no exact MPN or explicit MPN TBD")
        if not device.get("qualification"):
            errors.append(f"mechanical-source: {instance} has no evidence qualification")

        dimensions = device.get("maximum_dimensions_mm", device.get("dimensions_mm"))
        if not isinstance(dimensions, list) or len(dimensions) < 3:
            errors.append(f"mechanical-source: {instance} lacks sourced LxWxH")
        elif any(value is None or float(value) <= 0 for value in dimensions[:3]):
            errors.append(f"mechanical-source: {instance} has a non-positive LxWxH envelope")

        source = device.get("mechanical_source", device.get("source", {}))
        for field in ("document", "url", "checked"):
            if not source.get(field):
                errors.append(f"mechanical-source: {instance} dimension source lacks {field}")
        if source.get("url") and not str(source["url"]).startswith("https://"):
            errors.append(f"mechanical-source: {instance} dimension source is not HTTPS")

        if contract.frame not in MECHANICAL_PROJECTION_FRAMES:
            errors.append(f"mechanical-source: {instance} has unknown datum frame {contract.frame}")
        if contract.rotation not in {0, 45, 90, 180, 270}:
            errors.append(f"mechanical-source: {instance} has unsupported orientation {contract.rotation}")
        if not contract.direction.strip():
            errors.append(f"mechanical-source: {instance} has no interface-direction classification")

    for instance, direction in DIRECTIONAL_BODY_DIRECTIONS.items():
        contract = contracts.get(instance)
        if contract is None:
            errors.append(f"mechanical-source: directional body {instance} is not rendered")
        elif contract.direction != direction:
            errors.append(f"mechanical-source: {instance} lost its explicit interface direction")
    return actual, errors


def validate_mechanical_evidence_gates(instances: dict, rendered: set[str]) -> list[str]:
    """Require one explicit H1/H5 disposition for every open physical fit."""
    data = json.loads(MECHANICAL_GATES_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("schema_version") != 1 or data.get("stage") != "H1.1.3":
        errors.append("mechanical-gates: schema/stage mismatch")
    constraint = data.get("execution_constraint", {})
    if constraint.get("status") != "research_first_active":
        errors.append("mechanical-gates: research-first evidence policy must remain explicit")
    if constraint.get("order_authorized") is not False:
        errors.append("mechanical-gates: H1 evidence ordering must remain unauthorized")
    if constraint.get("current_step") != "H2.3.4":
        errors.append("mechanical-gates: exact evidence-research substep drifted")

    gates = data.get("gates", [])
    identifiers = [gate.get("id") for gate in gates]
    if len(identifiers) != len(set(identifiers)) or any(not item for item in identifiers):
        errors.append("mechanical-gates: gate IDs must be present and unique")
    required_h1: set[str] = set()
    actual_h1 = {
        gate["id"] for gate in gates if gate.get("disposition") == "h1_blocker"
    }
    if actual_h1 != required_h1:
        errors.append("mechanical-gates: exact H1 blocker set is not classified")

    covered: set[str] = set()
    for gate in gates:
        if gate.get("disposition") not in {"h1_blocker", "h5_received_sample_gate"}:
            errors.append(f"mechanical-gates: {gate.get('id')} has invalid disposition")
        for field in ("evidence_boundary", "unknown", "closure", "blocks"):
            if not gate.get(field):
                errors.append(f"mechanical-gates: {gate.get('id')} lacks {field}")
        affected = gate.get("affected_instances", [])
        if not affected:
            errors.append(f"mechanical-gates: {gate.get('id')} has no affected instances")
        for instance in affected:
            covered.add(instance)
            if instance not in instances:
                errors.append(f"mechanical-gates: {gate.get('id')} names unknown {instance}")
            elif instance not in rendered:
                errors.append(f"mechanical-gates: {gate.get('id')} names unrendered {instance}")
        if gate.get("disposition") == "h5_received_sample_gate" and "H8" not in gate.get("blocks", []):
            errors.append(f"mechanical-gates: {gate.get('id')} must block H8")

    required_open_instances = {
        "display", "display_connector", "display_adapter_plug", "display_panel_connector",
        "nrf0", "nrf1", "nrf2",
        "nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper",
        "nrf0_rf_board_connector", "nrf1_rf_board_connector", "nrf2_rf_board_connector",
        "nrf0_external_sma", "nrf1_external_sma", "nrf2_external_sma",
        "u214", "u214_connector",
        "ui_dpad_up", "ui_dpad_down", "ui_dpad_left", "ui_dpad_right", "ui_dpad_ok",
        "voice", "encoder", "encoder_knob", "power_command_switch",
        "ui_switch_back", "ui_switch_opt", "ui_switch_f1", "ui_switch_f2",
        "ui_switch_f3", "ui_switch_f4", "ui_switch_f5", "ui_switch_f6",
        "ui_switch_f7", "ui_switch_f8", "ptt_switch",
        "unit_connector", "pack_holder", "pack_cell0", "pack_cell1",
        "s3_rf_jumper", "c5_rf_jumper", "s3_rf_board_connector", "c5_rf_board_connector",
        "speaker", "microphone", "headphone_jack",
    }
    if not required_open_instances <= covered:
        errors.append(
            "mechanical-gates: open physical fits lack dispositions: "
            + ", ".join(sorted(required_open_instances - covered))
        )
    return errors


def validate_source_research() -> list[str]:
    """Keep the accepted research-first / purchase-last sequence machine-checkable."""
    data = json.loads(SOURCE_RESEARCH_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("schema_version") != 1 or data.get("stage") != "H1.1.3.3":
        errors.append("source-research: schema/stage mismatch")
    if data.get("status") != "reviewed" or data.get("current_substep") != "H2.3.4":
        errors.append("source-research: exact current substep drifted")
    policy = data.get("policy", {})
    if policy.get("order_authorized") is not False:
        errors.append("source-research: sample order must remain unauthorized")
    if policy.get("purchase_is_last_resort") is not True:
        errors.append("source-research: purchase-last policy was lost")
    sequence = policy.get("sequence", [])
    expected = [
        ("H1.1.3.3.1", "reviewed"),
        ("H1.1.3.3.2", "reviewed"),
        ("H1.1.3.3.3", "reviewed"),
        ("H1.1.3.3.4", "not_required"),
    ]
    actual = [(row.get("id"), row.get("status")) for row in sequence]
    if actual != expected:
        errors.append("source-research: research/replacement/request/sample order drifted")
    subjects = {row.get("id"): row for row in data.get("subjects", [])}
    if set(subjects) != {"display", "nrf24", "u214"}:
        errors.append("source-research: exact H1 source subjects drifted")
    for subject_id, subject in subjects.items():
        if not subject.get("official_findings"):
            errors.append(f"source-research: {subject_id} lacks official findings")
        if not subject.get("replacement_review"):
            errors.append(f"source-research: {subject_id} lacks replacement review")
        if not subject.get("remaining_gap") or not subject.get("current_disposition"):
            errors.append(f"source-research: {subject_id} lacks disposition")
    return errors


def validate_navigation_cluster(design: dict, devices: dict, instances: dict) -> list[str]:
    """Prove that the navigation cluster contains only exact serial buttons."""
    errors: list[str] = []
    if (
        design.get("schema_version") != 1
        or design.get("stage") != "H1.3.0"
        or design.get("design_id") != "L2-NAV-5B-001-A"
        or design.get("status") != "selected"
    ):
        errors.append("navigation-cluster: schema, stage, identity or status drifted")
    if design.get("manufacturing_class") != "serial_components_only":
        errors.append("navigation-cluster: only serial components are allowed")
    component = design.get("component", {})
    if component.get("device_key") != "omron_b3s_1100p" or component.get("mpn") != "OMRON B3S-1100P":
        errors.append("navigation-cluster: exact serial button MPN drifted")
    switch = devices.get(component.get("device_key"), {})
    if component.get("body_mm") != switch.get("dimensions_mm") or component.get("quantity") != 5:
        errors.append("navigation-cluster: serial button quantity or envelope drifted")
    if "no separate cap" not in str(component.get("actuation", "")):
        errors.append("navigation-cluster: a hidden cap or custom actuator was introduced")
    if not str(component.get("manufacturer_url", "")).startswith("https://components.omron.com/"):
        errors.append("navigation-cluster: manufacturer source must remain OMRON-controlled")
    expected_instances = {
        "ui_dpad_up", "ui_dpad_down", "ui_dpad_left", "ui_dpad_right", "ui_dpad_ok"
    }
    buttons = design.get("layout", {}).get("buttons", [])
    button_by_instance = {row.get("instance"): row for row in buttons}
    if set(button_by_instance) != expected_instances or len(buttons) != 5:
        errors.append("navigation-cluster: exact five-button instance set drifted")
    selected = {item.instance: item for item in FRONT_CONTROLS if item.instance in expected_instances}
    if set(selected) != expected_instances:
        errors.append("navigation-cluster: a direction or OK is absent from the front placement")
    for instance in expected_instances:
        if instances.get(instance) != "omron_b3s_1100p":
            errors.append(f"navigation-cluster: {instance} is not the selected serial B3S-1100P")
            continue
        expected_position = [selected[instance].x, selected[instance].y]
        if button_by_instance.get(instance, {}).get("position_mm") != expected_position:
            errors.append(f"navigation-cluster: {instance} position disagrees with the renderer")
    if design.get("electrical_contract", {}).get("expander_contacts_consumed") != 5:
        errors.append("navigation-cluster: exact five-input pin budget drifted")
    cost = design.get("cost_at_quantity_100_usd", {})
    selected_unit = float(switch.get("cost", {}).get("unit_price_usd", 0))
    if not math.isclose(float(cost.get("five_b3s_1100p", -1)), 5 * selected_unit, abs_tol=1e-9):
        errors.append("navigation-cluster: five-button cost is stale")
    checks = design.get("paper_checks", {})
    control_by_instance = {item.instance: item for item in FRONT_CONTROLS}
    switch_w = float(component.get("body_mm", [0, 0, 0])[0])
    cluster_x, _, cluster_w, _ = map(float, design.get("layout", {}).get("bounding_box_mm", [0, 0, 0, 0]))
    expected_back_clearance = cluster_x - (
        control_by_instance["ui_switch_back"].x + switch_w
    )
    expected_opt_clearance = control_by_instance["ui_switch_opt"].x - (
        cluster_x + cluster_w
    )
    if not math.isclose(float(checks.get("back_clearance_mm", -1)), expected_back_clearance, abs_tol=1e-9):
        errors.append("navigation-cluster: BACK clearance disagrees with the renderer")
    if not math.isclose(float(checks.get("opt_clearance_mm", -1)), expected_opt_clearance, abs_tol=1e-9):
        errors.append("navigation-cluster: OPT clearance disagrees with the renderer")
    if checks.get("custom_mechanical_parts") != 0:
        errors.append("navigation-cluster: custom mechanical parts are forbidden")
    if not all(checks.get(field) is True for field in ("all_five_bodies_inside_board", "mounting_keepouts_clear")):
        errors.append("navigation-cluster: paper containment checks are incomplete")
    if len(design.get("h5_acceptance", [])) < 4 or "H5" not in design.get("release_boundary", ""):
        errors.append("navigation-cluster: assembled control H5 gate is incomplete")
    return errors


def validate_display_adapter_design(
    design: dict, devices: dict, candidate: dict, instances: dict
) -> list[str]:
    """Keep the replaceable 40-to-40 display interface dimensionally honest."""
    errors: list[str] = []
    if design.get("schema_version") != 1 or design.get("design_id") != "L2-DISP-ADP-001-A":
        errors.append("display-adapter: schema/design identity mismatch")
    if design.get("stage") != "H1.1.3.3.3":
        errors.append("display-adapter: exact source-research stage drifted")
    board = design.get("board", {})
    board_w = float(board.get("width_mm", 0))
    board_h = float(board.get("height_mm", 0))
    board_t = float(board.get("thickness_mm", 0))
    board_x, board_y = map(float, board.get("ui_inner_position_mm", [0, 0]))
    if (board_w, board_h, board_t) != (25.5, 12.0, 0.8):
        errors.append("display-adapter: controlled 25.5x12.0x0.8-mm PCB envelope drifted")
    if board_x < 0 or board_y < 0 or board_x + board_w > BOARD_W or board_y + board_h > BOARD_H:
        errors.append("display-adapter: adapter PCB leaves the UI-board projection")
    if any(hits_hole((board_x, board_y, board_w, board_h), hole) for hole in HOLES):
        errors.append("display-adapter: adapter PCB enters a mounting-hole keep-out")

    expected_mpns = {
        "display_connector": "Hirose DF40C(2.0)-40DS-0.4V(58)",
        "display_adapter_plug": "Hirose DF40C-40DP-0.4V(51)",
        "display_panel_connector": "Hirose FH34SRJ-40S-0.5SH(99)",
    }
    rows = {row.get("instance"): row for row in design.get("components", [])}
    if set(rows) != set(expected_mpns):
        errors.append("display-adapter: exact three-connector mechanical set drifted")
    for instance, expected_mpn in expected_mpns.items():
        if instance not in instances or instance not in rows:
            continue
        device = devices[instances[instance]]
        if device.get("mpn") != expected_mpn or rows[instance].get("mpn") != expected_mpn:
            errors.append(f"display-adapter: {instance} exact MPN drifted")
        if [float(value) for value in rows[instance].get("envelope_mm", [])] != [
            float(value) for value in device.get("dimensions_mm", [])
        ]:
            errors.append(f"display-adapter: {instance} envelope disagrees with device register")

    main = rows.get("display_connector", {})
    main_x, main_y = map(float, main.get("ui_inner_position_mm", [0, 0]))
    main_w, main_h, _ = map(float, main.get("envelope_mm", [0, 0, 0]))
    if not (
        board_x <= main_x
        and board_y <= main_y
        and main_x + main_w <= board_x + board_w
        and main_y + main_h <= board_y + board_h
    ):
        errors.append("display-adapter: main receptacle leaves the adapter projection")
    ui_connector = next((item for item in UI_INNER if item.instance == "display_connector"), None)
    if ui_connector is None or (ui_connector.x, ui_connector.y) != (main_x, main_y):
        errors.append("display-adapter: main-receptacle coordinate disagrees with UI-inner placement")

    adapter_plug = rows.get("display_adapter_plug", {})
    plug_x, plug_y = map(float, adapter_plug.get("adapter_position_mm", [0, 0]))
    plug_w, plug_h, _ = map(float, adapter_plug.get("envelope_mm", [0, 0, 0]))
    panel_mate = rows.get("display_panel_connector", {})
    panel_x, panel_y = map(float, panel_mate.get("adapter_position_mm", [0, 0]))
    panel_w, panel_h, _ = map(float, panel_mate.get("envelope_mm", [0, 0, 0]))
    for name, x, y, w, h in (
        ("adapter plug", plug_x, plug_y, plug_w, plug_h),
        ("panel connector", panel_x, panel_y, panel_w, panel_h),
    ):
        if x < 0 or y < 0 or x + w > board_w or y + h > board_h:
            errors.append(f"display-adapter: {name} leaves the adapter PCB")
    if not math.isclose(main_x + main_w / 2, board_x + plug_x + plug_w / 2, abs_tol=0.01):
        errors.append("display-adapter: DF40 plug/receptacle X axes do not coincide")
    if not math.isclose(main_y + main_h / 2, board_y + plug_y + plug_h / 2, abs_tol=0.01):
        errors.append("display-adapter: DF40 plug/receptacle Y axes do not coincide")

    stack = design.get("stack", {})
    derived_height = (
        float(stack.get("df40_mated_height_mm", 0))
        + board_t
        + float(stack.get("panel_connector_height_mm", 0))
    )
    if not math.isclose(derived_height, float(stack.get("ui_board_to_panel_connector_top_mm", -1)), abs_tol=1e-9):
        errors.append("display-adapter: stored Z stack is stale")
    if derived_height + float(stack.get("minimum_reserved_clearance_mm", 0)) > INTERBOARD_GAP_MM:
        errors.append("display-adapter: connector stack exceeds the interboard gap")
    adapter_box = (board_x, board_y, board_w, board_h)
    for item in UI_INNER:
        if item.instance == "display_connector":
            continue
        if overlaps(adapter_box, (item.x, item.y, *placement_size(item, devices, instances))):
            errors.append(f"display-adapter: board projection conflicts with {item.instance}")
    for hole in HOLES:
        if hits_hole(adapter_box, hole, MIN_INTERBOARD_Z_CLEARANCE_MM):
            errors.append(f"display-adapter: board projection enters mounting keep-out at {hole}")
    for clearance, rf_item in display_adapter_opposing_clearance_pairs(
        design, devices, instances
    ):
        if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(
                f"display-adapter: complete stack opposite {rf_item.instance} leaves only "
                f"{clearance:.2f} mm, below the {MIN_INTERBOARD_Z_CLEARANCE_MM:.1f}-mm minimum"
            )

    routes = candidate.get("fixed_routes", [])
    route_pairs = {(row.get("from"), row.get("to"), row.get("net")) for row in routes}
    panel_nets: dict[int, str] = {}
    for row in routes:
        endpoint = row.get("from", "")
        if endpoint.startswith("display_panel_connector.PIN_") and str(row.get("to", "")).startswith("display."):
            panel_nets[int(endpoint.rsplit("_", 1)[1])] = row.get("net")
    if set(panel_nets) != set(range(1, 41)):
        errors.append("display-adapter: panel-side exact 40-contact map is incomplete")
    for pin, net in panel_nets.items():
        if (
            f"display_connector.PIN_{pin}",
            f"display_adapter_plug.PIN_{pin}",
            net,
        ) not in route_pairs or (
            f"display_adapter_plug.PIN_{pin}",
            f"display_panel_connector.PIN_{pin}",
            net,
        ) not in route_pairs:
            errors.append(f"display-adapter: PIN_{pin} is not one-to-one through both mates")
    if "H5" not in design.get("release_boundary", ""):
        errors.append("display-adapter: received-tail fit must remain an H5 gate")
    return errors


def validate_assembly_coordinate_model(
    model: dict, devices: dict, instances: dict, display_adapter_design: dict
) -> list[str]:
    """Prove that every view shares one X/Y/Z datum and board transformation."""
    errors: list[str] = []
    if (
        model.get("schema_version") != 1
        or model.get("model_id") != "L2-ASM-COORD-001-A"
        or model.get("stage") != "H1-R2.22"
        or model.get("status") != "in_progress"
    ):
        errors.append("coordinate-model: schema, identity, stage or review status drifted")
    if [float(value) for value in model.get("board_outline_mm", [])] != [BOARD_W, BOARD_H]:
        errors.append("coordinate-model: board outline disagrees with the renderers")
    holes = model.get("mounting_holes", {})
    if float(holes.get("diameter_mm", 0)) != MOUNT_HOLE_D:
        errors.append("coordinate-model: mounting-hole diameter drifted")
    if float(holes.get("head_keepout_radius_mm", 0)) != MOUNT_KEEPOUT_R:
        errors.append("coordinate-model: mounting keep-out drifted")
    if [tuple(map(float, row)) for row in holes.get("world_xy", [])] != list(HOLES):
        errors.append("coordinate-model: mounting axes disagree with every board view")

    stack = model.get("stack", {})
    display_depth = float(devices[instances["display"]]["dimensions_mm"][2])
    expected_stack = {
        "display_front_z": 0.0,
        "display_depth_mm": display_depth,
        "ui_outer_face_z": display_depth,
        "ui_pcb_thickness_mm": 1.6,
        "ui_inner_face_z": display_depth + 1.6,
        "interboard_gap_mm": INTERBOARD_GAP_MM,
        "rf_inner_face_z": display_depth + 1.6 + INTERBOARD_GAP_MM,
        "rf_pcb_thickness_mm": 1.6,
        "rf_outer_face_z": display_depth + 1.6 + INTERBOARD_GAP_MM + 1.6,
        "selected_base_stack_depth_mm": display_depth + 1.6 + INTERBOARD_GAP_MM + 1.6,
    }
    for field, expected in expected_stack.items():
        if not math.isclose(float(stack.get(field, -999)), expected, abs_tol=1e-9):
            errors.append(f"coordinate-model: {field} is stale (expected {expected:.3f})")

    planes = model.get("antenna_planes", {})
    front_centre = float(stack.get("ui_outer_face_z", 0)) - RF_BARREL_D / 2
    rear_centre = float(stack.get("rf_outer_face_z", 0)) + RF_BARREL_D / 2
    if not math.isclose(float(planes.get("front_bank_centre_z", -1)), front_centre, abs_tol=0.001):
        errors.append("coordinate-model: front antenna centre plane drifted")
    if not math.isclose(float(planes.get("rear_bank_centre_z", -1)), rear_centre, abs_tol=0.001):
        errors.append("coordinate-model: rear antenna centre plane drifted")
    if not math.isclose(
        float(planes.get("centre_plane_separation_mm", -1)),
        rear_centre - front_centre,
        abs_tol=0.001,
    ):
        errors.append("coordinate-model: antenna centre-plane separation drifted")

    zones = model.get("longitudinal_zones", {})
    u214_y = list(map(float, zones.get("u214_cap_y_mm", [])))
    battery_y = list(map(float, zones.get("battery_holder_y_mm", [])))
    if u214_y != [U214_Y, U214_Y + U214_H] or battery_y != [PACK_HOLDER_Y, PACK_HOLDER_Y + PACK_HOLDER_H]:
        errors.append("coordinate-model: U214 or battery Y zone drifted")
    elif u214_y[1] + U214_CLEARANCE > battery_y[0]:
        errors.append("coordinate-model: U214 and battery longitudinal zones overlap")

    envelopes = model.get("accessory_envelopes", {})
    adapter = envelopes.get("display_adapter_bay", {})
    board = display_adapter_design["board"]
    adapter_x, adapter_y = map(float, board["ui_inner_position_mm"])
    expected_adapter = {
        "x_mm": [adapter_x, adapter_x + float(board["width_mm"])],
        "y_mm": [adapter_y, adapter_y + float(board["height_mm"])],
        "z_mm": [
            float(stack.get("ui_inner_face_z", 0)),
            float(stack.get("ui_inner_face_z", 0))
            + float(display_adapter_design["stack"]["ui_board_to_panel_connector_top_mm"]),
        ],
    }
    for axis, expected in expected_adapter.items():
        if [float(value) for value in adapter.get(axis, [])] != expected:
            errors.append(f"coordinate-model: display-adapter {axis} envelope drifted")
    if expected_adapter["z_mm"][1] + MIN_INTERBOARD_Z_CLEARANCE_MM > float(stack.get("rf_inner_face_z", 0)):
        errors.append("coordinate-model: display adapter violates the unified Z channel")

    u214 = envelopes.get("u214", {})
    if [float(value) for value in u214.get("x_mm", [])] != [U214_X, U214_X + U214_W]:
        errors.append("coordinate-model: U214 X envelope drifted")
    if [float(value) for value in u214.get("y_mm", [])] != [U214_Y, U214_Y + U214_H]:
        errors.append("coordinate-model: U214 Y envelope drifted")
    if not model.get("enclosure_reference", {}).get("not_yet_locked"):
        errors.append("coordinate-model: enclosure-open boundary must remain explicit")
    return errors


def validate() -> list[str]:
    (
        devices, candidate, instances, navigation_cluster,
        display_adapter_design, assembly_coordinate_model,
    ) = load()
    errors: list[str] = []
    required = {
        "s3": "ESP32-S3-WROOM-1U-N16R8",
        "c5": "ESP32-C5-WROOM-1U-N8R8",
        "rp": "SC1512-A4",
        "display": "HMX035CTFT-001 (QDtech schematic assembly marking)",
        "u214": "M5Stack U214 Cap LoRa-1262",
        "u214_connector": "Samtec HLE-107-02-G-DV-PE-LC",
        "pack_holder": "Keystone Electronics 1048P",
        "unit_connector": "1125R-SMT-4P",
        "encoder_knob": "Davies Molding 1227-J",
        "ui_dpad_up": "OMRON B3S-1100P",
        "ui_dpad_down": "OMRON B3S-1100P",
        "ui_dpad_left": "OMRON B3S-1100P",
        "ui_dpad_right": "OMRON B3S-1100P",
        "ui_dpad_ok": "OMRON B3S-1100P",
        "display_connector": "Hirose DF40C(2.0)-40DS-0.4V(58)",
        "display_adapter_plug": "Hirose DF40C-40DP-0.4V(51)",
        "display_panel_connector": "Hirose FH34SRJ-40S-0.5SH(99)",
    }
    for instance, expected in required.items():
        actual = devices[instances[instance]]["mpn"]
        if actual != expected:
            errors.append(f"{instance}: expected {expected}, got {actual}")

    mechanically_accounted, mechanical_source_errors = validate_mechanical_sources(
        devices, instances
    )
    errors += mechanical_source_errors
    errors += validate_mechanical_evidence_gates(instances, mechanically_accounted)
    errors += validate_source_research()
    errors += validate_navigation_cluster(navigation_cluster, devices, instances)
    errors += validate_display_adapter_design(
        display_adapter_design, devices, candidate, instances
    )
    errors += validate_assembly_coordinate_model(
        assembly_coordinate_model, devices, instances, display_adapter_design
    )
    for instance, device_key in instances.items():
        device = devices[device_key]
        dimensions = device.get("maximum_dimensions_mm", device.get("dimensions_mm"))
        if not dimensions or len(dimensions) < 2 or dimensions[0] is None or dimensions[1] is None:
            continue
        plan_area = float(dimensions[0]) * float(dimensions[1])
        height = (
            float(dimensions[2])
            if len(dimensions) > 2 and dimensions[2] is not None
            else 0.0
        )
        if (plan_area >= 12.0 or height >= 2.0) and instance not in mechanically_accounted:
            errors.append(
                f"mechanical-accounting: significant body {instance} ({device['mpn']}) "
                "is absent from every physical projection"
            )
    touch = devices[instances["display_touch_controller"]]
    if touch.get("assembly_contract", {}).get("assembly") != "HMX035CTFT-001":
        errors.append("mechanical-accounting: display touch die must remain embedded in HMX035CTFT-001")

    errors += validate_items("ui-inner", UI_INNER, devices, instances)
    errors += validate_cable_routes(devices, instances)
    errors += validate_nrf_cable_reserves(devices, instances)
    errors += validate_items("rf-inner", RF_INNER, devices, instances)
    errors += validate_through_board_features(devices, instances)
    inner_height_errors = []
    for item in UI_INNER + RF_INNER:
        try:
            placement_height(item, devices, instances)
        except ValueError as error:
            inner_height_errors.append(str(error))
    errors += inner_height_errors
    if not inner_height_errors:
        individual_clearances = interboard_individual_clearances(devices, instances)
        for clearance, item in individual_clearances:
            if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
                errors.append(
                    f"interboard: {item.instance} alone leaves only {clearance:.2f} mm "
                    f"to the opposite PCB plane, below the {MIN_INTERBOARD_Z_CLEARANCE_MM:.1f}-mm minimum"
                )
        clearance_pairs = interboard_clearance_pairs(devices, instances)
        for clearance, ui_item, rf_item in clearance_pairs:
            if clearance < MIN_INTERBOARD_Z_CLEARANCE_MM:
                errors.append(
                    f"interboard: {ui_item.instance}/{rf_item.instance} leaves only "
                    f"{clearance:.2f} mm, below the {MIN_INTERBOARD_Z_CLEARANCE_MM:.1f}-mm minimum"
                )
        ui_by_instance = {item.instance: item for item in UI_INNER}
        rf_by_instance = {item.instance: item for item in RF_INNER}
        for ui_instance, rf_instance in INTENTIONAL_INTERBOARD_MATES:
            ui_item = ui_by_instance.get(ui_instance)
            rf_item = rf_by_instance.get(rf_instance)
            if ui_item is None or rf_item is None:
                errors.append(f"interboard: intentional mate {ui_instance}/{rf_instance} is absent")
                continue
            ui_w, ui_h = placement_size(ui_item, devices, instances)
            rf_w, rf_h = placement_size(rf_item, devices, instances)
            if not overlaps(
                (ui_item.x, ui_item.y, ui_w, ui_h),
                (mirrored_x(rf_item.x, rf_w), rf_item.y, rf_w, rf_h),
            ):
                errors.append(f"interboard: intentional mate {ui_instance}/{rf_instance} is not aligned")
        m1_contract = candidate["interboard_contract"]["connector_pair"]
        m1_gap = float(m1_contract.get("mated_height_mm", -1))
        if m1_gap != INTERBOARD_GAP_MM:
            errors.append("interboard: exact M1 mated height must equal the 11-mm inner gap")
        m1_ui_device = devices[instances[m1_contract["ui_instance"]]]
        m1_rf_device = devices[instances[m1_contract["rf_power_instance"]]]
        if float(m1_ui_device["electrical_contract"].get("mated_height_with_fx8c_80s_sv5_mm", -1)) != INTERBOARD_GAP_MM:
            errors.append("interboard: M1 UI plug does not declare the exact 11-mm mate")
        if float(m1_rf_device["electrical_contract"].get("mated_height_with_fx8c_80p_sv1_mm", -1)) != INTERBOARD_GAP_MM:
            errors.append("interboard: M1 RF receptacle does not declare the exact 11-mm mate")
    errors += validate_items("front-controls", FRONT_CONTROLS, devices, instances)
    errors += validate_items("rear-controls", REAR_CONTROLS, devices, instances)
    errors += validate_items("rear-outer", REAR_OUTER, devices, instances)
    errors += validate_items("rear-selected-actuators", REAR_SELECTED_ACTUATORS, devices, instances)
    errors += validate_reserves("front-caps", FRONT_CAP_RESERVES)
    errors += validate_reserves("rear-caps", REAR_CAP_RESERVES)
    errors += validate_reserves("internal-reserves", INTERNAL_RESERVES)
    rf_by_instance = {item.instance: item for item in RF_INNER}
    for zone in INTERNAL_RESERVES:
        zone_box = (zone.x, zone.y, zone.w, zone.h)
        allowed = INTERNAL_ZONE_ALLOWED_INSTANCES.get(zone.name, set())
        for item in RF_INNER:
            item_w, item_h = placement_size(item, devices, instances)
            item_box = (item.x, item.y, item_w, item_h)
            if item.instance in allowed:
                if not (
                    zone.x <= item.x
                    and zone.y <= item.y
                    and item.x + item_w <= zone.x + zone.w
                    and item.y + item_h <= zone.y + zone.h
                ):
                    errors.append(f"internal-zone: {zone.name} does not contain {item.instance}")
            elif overlaps(zone_box, item_box, MIN_INTERBOARD_Z_CLEARANCE_MM):
                errors.append(f"internal-zone: {zone.name} lacks clearance to {item.instance}")

    for instance, path, corridor in (
        ("voice_v", "VOICE-VHF", VOICE_V_RF_CORRIDOR),
        ("voice", "VOICE-UHF", VOICE_U_RF_CORRIDOR),
    ):
        module = rf_by_instance[instance]
        module_device = devices[instances[instance]]
        contact = module_device.get("mechanical_contract", {}).get("antenna_contact", {})
        contact_xy = contact.get("nominal_center_from_illustrated_top_left_mm", [])
        if contact.get("physical") != "12" or len(contact_xy) != 2:
            errors.append(f"{instance}: SA818S official contact-12 orientation contract is missing")
            continue
        antenna_xy = placed_contact_xy(module, module_device, tuple(map(float, contact_xy)))
        port_x = next(centre for centre, candidate_path, _ in REAR_RF if candidate_path == path)
        if corridor[0] != (port_x, 0.0) or any(
            abs(a - b) > 0.01 for a, b in zip(corridor[-1], antenna_xy)
        ):
            errors.append(f"{instance}: contact 12 and dedicated {path} corridor endpoints disagree")
        if polyline_length(corridor) > 41.0:
            errors.append(f"{instance}: dedicated RF corridor exceeds the 41-mm worst-case planar allowance")

    cc_zone = next(zone for zone in INTERNAL_RESERVES if zone.name == "cc-reference-rf-network")
    cc_port_x = next(centre for centre, path, _ in REAR_RF if path == "CC-SUB")
    if not (
        cc_zone.x - RF_BODY_W / 2 <= cc_port_x <= cc_zone.x + cc_zone.w + RF_BODY_W / 2
        and cc_zone.y >= RF_BODY_D + OPPOSITE_FACE_CLEARANCE_MM
    ):
        errors.append("CC1101 reference RF zone must align to SUB-GHz and clear the outer connector land")
    front_path_centres = {path: centre for centre, path, _ in FRONT_RF}
    if front_path_centres.get("S3-2G4") != 15.7 or front_path_centres.get("C5-2G4/5") != 59.3:
        errors.append("native RF ports must remain aligned to the two exact 30-mm jumper corridors")
    navigation_items = {
        item.instance: item
        for item in FRONT_CONTROLS
        if item.instance.startswith("ui_dpad_")
    }
    if set(navigation_items) != {
        "ui_dpad_up", "ui_dpad_down", "ui_dpad_left", "ui_dpad_right", "ui_dpad_ok"
    }:
        errors.append("front navigation must retain five independent serial buttons")
    for item in navigation_items.values():
        if item.rotation != 0:
            errors.append(f"{item.instance}: direct B3S button must retain drawing orientation")

    display_device = devices[instances["display"]]
    if display_device.get("pixel_resolution") != [320, 480]:
        errors.append("display: exact HMX035CTFT-001 resolution must remain 320x480")
    if display_device.get("active_area_mm") != [48.96, 73.44]:
        errors.append("display: exact active area must remain 48.96x73.44 mm")
    if display_device.get("active_area_offset_from_body_top_left_mm") != [2.77, 2.15]:
        errors.append("display: active area must retain the exact 2.77x2.15-mm body offset")
    if display_device.get("viewing_area_mm") != [49.96, 74.44]:
        errors.append("display: exact viewing window must remain 49.96x74.44 mm")
    if display_device.get("viewing_area_offset_from_body_top_left_mm") != [2.27, 1.65]:
        errors.append("display: viewing window must retain the exact 2.27x1.65-mm body offset")
    if display_device.get("effective_touch_area_mm") != [54.5, 83.0]:
        errors.append("display: exact effective touch area must remain 54.5x83.0 mm")
    active_w, active_h = map(float, display_device.get("active_area_mm", [0, 1]))
    if not math.isclose(active_w / active_h, 2 / 3, rel_tol=0, abs_tol=1e-9):
        errors.append("display: active area must retain the exact 2:3 portrait ratio")
    direct_mechanical = devices[instances["ptt_switch"]].get("mechanical_contract", {})
    if direct_mechanical.get("plunger_diameter_mm") != 3.3:
        errors.append("B3S-1100P direct-press controls must retain the exact 3.3-mm plunger")
    if direct_mechanical.get("nominal_height_mm") != 4.3:
        errors.append("B3S-1100P nominal direct-press height must remain 4.3 mm")
    display = Placement("display", 10.25, 11.0, "display")
    holder = Placement("pack_holder", 17.6, PACK_HOLDER_Y, "battery holder", 90)
    errors += validate_items("front-display", (display,), devices, instances)
    errors += validate_items("rear-exact", (holder,), devices, instances)
    ui_instances = {item.instance for item in UI_INNER}
    rf_instances = {item.instance for item in RF_INNER}
    if "microphone" in ui_instances or "microphone" not in rf_instances:
        errors.append("microphone must remain on the RF/power PCB inner side")
    if ("microphone", "front", "bottom") not in {
        (instance, face, side) for instance, face, side, _, _ in EDGE_INTERFACES
    }:
        errors.append("microphone must retain its front-face silkscreen and downward external direction")
    if {(instance, face, side) for instance, face, side, _, _ in EXTERNAL_COMPONENT_LABELS} != {
        ("speaker", "rear", "right"),
    }:
        errors.append("speaker must retain its external label without invented grille geometry")

    u214_dims = devices[instances["u214"]]["dimensions_mm"]
    if u214_dims != [84.0, 24.0, 15.287]:
        errors.append("U214 must use the official 84x24x15.287-mm envelope")
    connector = REAR_OUTER[0]
    connector_w, connector_d = placement_size(connector, devices, instances)
    if (connector_w, connector_d) != (U214_CONNECTOR_W, U214_CONNECTOR_D):
        errors.append("U214 host socket must retain the exact 17.78x5.08-mm plan envelope")
    if abs(connector.x + connector_w / 2 - (U214_X + U214_W / 2)) > 0.001:
        errors.append("U214 host socket and Cap must share the same 84-mm centreline")
    if abs(connector.y + connector_d / 2 - (U214_Y + U214_H / 2)) > 0.001:
        errors.append("Cap-Bus host socket must be centred beneath the Cap envelope")
    mechanical = devices[instances["u214_connector"]].get("mechanical_contract", {})
    if not mechanical.get("orientation", "").startswith("vertical socket"):
        errors.append("raised rear Cap-Bus rail requires a vertical socket normal to its plane")
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
    # Only the exact through-hole pad/locking-clip keep-out reaches the inner
    # PCB face.  Projecting the complete 5.08-mm external moulding through the
    # board would create a false collision with the SA818S and CC reference
    # zone.  The 3.81-mm opposite-face depth is the two 2.54-mm rows plus the
    # controlled pad radius from the Samtec through-hole footprint.
    opposite_connector_box = (
        connector.x,
        connector.y + (connector_d - U214_CONNECTOR_PTH_KEEPOUT_D) / 2,
        U214_CONNECTOR_PTH_KEEPOUT_W,
        U214_CONNECTOR_PTH_KEEPOUT_D,
    )
    for item in RF_INNER:
        item_w, item_h = placement_size(item, devices, instances)
        if overlaps(
            opposite_connector_box,
            (item.x, item.y, item_w, item_h),
            OPPOSITE_FACE_CLEARANCE_MM,
        ):
            errors.append(f"rear opposite faces: U214 through-hole socket conflicts with {item.instance}")
    for zone in INTERNAL_RESERVES:
        if overlaps(
            opposite_connector_box,
            (zone.x, zone.y, zone.w, zone.h),
            OPPOSITE_FACE_CLEARANCE_MM,
        ):
            errors.append(f"rear opposite faces: U214 through-hole socket conflicts with {zone.name}")
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
    cell_boxes = []
    for instance, centre_x in (("pack_cell0", 28.0), ("pack_cell1", 47.0)):
        cell = Placement(instance, 0.0, 0.0, "protected 18650 cell", 90)
        cell_w, cell_h = placement_size(cell, devices, instances)
        cell_box = (
            centre_x - cell_w / 2,
            holder.y + (holder_h - cell_h) / 2,
            cell_w,
            cell_h,
        )
        cell_boxes.append((instance, cell_box))
        if not (
            holder.x <= cell_box[0]
            and holder.y <= cell_box[1]
            and cell_box[0] + cell_box[2] <= holder.x + holder_w
            and cell_box[1] + cell_box[3] <= holder.y + holder_h
        ):
            errors.append(f"rear: {instance} exact envelope leaves the Keystone holder")
    if overlaps(cell_boxes[0][1], cell_boxes[1][1]):
        errors.append("rear: exact protected-cell envelopes overlap")
    for centre, _, _ in REAR_RF:
        rf_box = (centre - RF_BODY_W / 2, 0.0, RF_BODY_W, RF_BODY_D)
        if overlaps(connector_box, rf_box, U214_CLEARANCE):
            errors.append("U214 host socket lacks 0.7-mm clearance to the rear RF connector bank")
        for item in RF_INNER:
            item_w, item_h = placement_size(item, devices, instances)
            if overlaps(
                rf_box,
                (item.x, item.y, item_w, item_h),
                OPPOSITE_FACE_CLEARANCE_MM,
            ):
                errors.append(
                    f"rear opposite faces: outward RF connector at x={centre} conflicts with {item.instance}"
                )
        for zone in INTERNAL_RESERVES:
            if overlaps(
                rf_box,
                (zone.x, zone.y, zone.w, zone.h),
                OPPOSITE_FACE_CLEARANCE_MM,
            ):
                errors.append(
                    f"rear opposite faces: outward RF connector at x={centre} conflicts with {zone.name}"
                )

    machine_paths = set(candidate["antenna_policy"]["base_onboard_sma_paths"])
    drawn_paths = {path for _, path, _ in FRONT_RF + REAR_RF}
    if machine_paths != drawn_paths or len(drawn_paths) != 10:
        errors.append("mechanical projection must retain all ten unique onboard RF paths")
    topology_paths = {guide.path for guide in ANTENNA_TOPOLOGY_GUIDES}
    if topology_paths != drawn_paths or len(ANTENNA_TOPOLOGY_GUIDES) != 10:
        errors.append("every onboard antenna path must have exactly one topology guide")
    if set(RF_SOURCE_INSTANCE_BY_PATH) != drawn_paths:
        errors.append("every onboard antenna path must name one radio source instance")
    if len({guide.instance for guide in ANTENNA_TOPOLOGY_GUIDES}) != 10:
        errors.append("antenna topology guide instance names must be unique")
    ui_inner_instances = {item.instance for item in UI_INNER}
    rf_inner_instances = {item.instance for item in RF_INNER}
    port_centres = {path: centre for centre, path, _ in FRONT_RF + REAR_RF}
    for guide in ANTENNA_TOPOLOGY_GUIDES:
        expected_sources = (
            ui_inner_instances if guide.frame == "ui-inner" else rf_inner_instances
        )
        if guide.source_instance not in expected_sources:
            errors.append(
                f"antenna topology {guide.path}: source {guide.source_instance} is absent from {guide.frame}"
            )
        if RF_INSTANCE_BY_PATH.get(guide.path) != guide.external_instance:
            errors.append(f"antenna topology {guide.path}: wrong external connector instance")
        if guide.points[-1] != (port_centres[guide.path], 0.0):
            errors.append(f"antenna topology {guide.path}: guide misses antenna datum")
        for point in guide.points:
            if not (0.0 <= point[0] <= BOARD_W and 0.0 <= point[1] <= BOARD_H):
                errors.append(f"antenna topology {guide.path}: point {point} leaves PCB plan")
        for segment in zip(guide.points, guide.points[1:]):
            for hole in HOLES:
                if point_segment_distance(hole, *segment) < MOUNT_KEEPOUT_R:
                    errors.append(
                        f"antenna topology {guide.path}: guide enters the M2.5 keep-out at {hole}"
                    )
    cable_fed_paths = {"S3-2G4", "C5-2G4/5", "N24-0", "N24-1", "N24-2"}
    if {
        guide.source_instance
        for guide in ANTENNA_TOPOLOGY_GUIDES
        if guide.path in cable_fed_paths
    } != BOARD_RF_CABLE_TO_TRACE_HANDOFFS:
        errors.append("every physical RF cable must end at one explicit cable-to-PCB handoff")
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
    if float(candidate["interboard_contract"].get("working_inner_gap_mm", -1)) != INTERBOARD_GAP_MM:
        errors.append("mechanical clearance audit requires the exact 11-mm working inner gap")
    expected_outer_face_separation = float(candidate["interboard_contract"]["working_inner_gap_mm"]) + 2 * 1.6
    expected_centre_plane_separation = expected_outer_face_separation + RF_BARREL_D
    if separation.get("interboard_channel_mm") != INTERBOARD_GAP_MM:
        errors.append("antenna contract must preserve the exact 11-mm interboard channel")
    if abs(float(separation.get("outer_pcb_face_separation_mm", -1)) - expected_outer_face_separation) > 0.001:
        errors.append("antenna contract has invalid outward PCB face separation")
    if abs(float(separation.get("antenna_centre_plane_separation_mm", -1)) - expected_centre_plane_separation) > 0.001:
        errors.append("antenna contract has invalid connector centre-plane separation")
    if separation.get("interboard_channel_contains_connector_bodies") is not False:
        errors.append("antenna connector bodies may not occupy the interboard channel")
    ui_outer_z = float(devices[instances["display"]]["dimensions_mm"][2])
    ui_inner_z = ui_outer_z + 1.6
    rf_inner_z = ui_inner_z + INTERBOARD_GAP_MM
    rf_outer_z = rf_inner_z + 1.6
    front_rf_centre_z = ui_outer_z - RF_BARREL_D / 2
    rear_rf_centre_z = rf_outer_z + RF_BARREL_D / 2
    if abs(front_rf_centre_z + RF_BARREL_D / 2 - ui_outer_z) > 0.001:
        errors.append("front antenna bodies must terminate at the UI PCB outer face")
    if abs(rear_rf_centre_z - RF_BARREL_D / 2 - rf_outer_z) > 0.001:
        errors.append("rear antenna bodies must begin at the RF/power PCB outer face")
    if abs((rf_inner_z - ui_inner_z) - INTERBOARD_GAP_MM) > 0.001:
        errors.append("the 11-mm interboard channel must remain free of antenna bodies")
    if rear_rf_centre_z - front_rf_centre_z < 20.5:
        errors.append("opposed outer-face antenna banks lost their maximum depth separation")
    for _, path, _ in FRONT_RF + REAR_RF:
        lines = RF_USER_LABEL_LINES.get(path, ())
        if not lines or any("SMA" in line for line in lines):
            errors.append(f"{path}: antenna silkscreen must identify the function without connector-family text")
    if len(TX_RF_PATHS) != 8 or not TX_RF_PATHS <= drawn_paths:
        errors.append("eight transmitting RF paths must remain represented; VHF/UHF share one wired-OR V/U TX indicator")
    display_box = (display.x, display.y, *placement_size(display, devices, instances))
    for control in SIDE_FUNCTION_CONTROLS:
        control_box = (control.x, control.y, *placement_size(control, devices, instances))
        if overlaps(control_box, display_box, 0.7):
            errors.append(f"front: {control.instance} lacks 0.7-mm display clearance")
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
    for instance, label, x, y in FRONT_FACE_INDICATORS:
        led_box = (x, y, TX_LED_W, TX_LED_H)
        indicator_boxes.append((label, led_box))
        led_mpn = devices[instances[instance]]["mpn"]
        led_dims = devices[instances[instance]]["dimensions_mm"][:2]
        expected_mpn = "LTST-C190KFKT" if instance == "fault_led" else "LTST-C190KRKT"
        if led_mpn != expected_mpn or led_dims != [TX_LED_W, TX_LED_H]:
            errors.append(f"{label}: indicator must retain exact {expected_mpn} geometry")
        if overlaps(led_box, display_box, 0.7):
            errors.append(f"front: {label} TX indicator lacks 0.7-mm display clearance")
        if any(hits_hole(led_box, hole, 0.7) for hole in HOLES):
            errors.append(f"front: {label} TX indicator enters a mounting keep-out")
    for index, (label, led_box) in enumerate(indicator_boxes):
        for other_label, other_box in indicator_boxes[index + 1:]:
            if overlaps(led_box, other_box, 0.7):
                errors.append(f"front: {label}/{other_label} TX indicators overlap")
    indicator_rows = {}
    for _, _, x, y in FRONT_FACE_INDICATORS:
        indicator_rows.setdefault(y, []).append(x)
    if len(indicator_rows) != 2 or sorted(map(len, indicator_rows.values())) != [5, 5]:
        errors.append("front: all ten front indicators must remain in two rows of five")
    if len({tuple(sorted(xs)) for xs in indicator_rows.values()}) != 1:
        errors.append("front: both five-indicator rows must retain aligned columns")
    expected_labels = {
        "WI-FI/BLE", "WI-FI/15.4", "nRF24-1", "nRF24-2", "nRF24-3",
        "SUB-GHz", "V/U TX", "IR", "LORA/EXT", "FAULT",
    }
    if {label for _, label, _, _ in FRONT_FACE_INDICATORS} != expected_labels:
        errors.append("front: indicator labels must match nine TX/evidence identities plus FAULT")
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
            edge_gap = {
                "left": item.x,
                "right": BOARD_W - item.x - w,
                "bottom": BOARD_H - item.y - h,
            }[side]
            if edge_gap < -0.001 or edge_gap > 1.001:
                errors.append(
                    f"external interface {label}: {instance} is {edge_gap:.3f} mm "
                    f"from its declared {side} exit"
                )
    if len({label for _, _, _, _, label in EDGE_INTERFACES}) != len(EDGE_INTERFACES):
        errors.append("external interface labels must be unique")
    required_usb_edges = {
        ("product_usb_connector", "rear", "bottom", "USB / POWER"),
        ("c5_service_usb_connector", "front", "bottom", "C5 SERVICE USB"),
        ("rp_service_usb_connector", "rear", "bottom", "RP SERVICE USB"),
    }
    actual_usb_edges = {
        (instance, face, side, label)
        for instance, face, side, _, label in EDGE_INTERFACES
        if "usb" in instance
    }
    if actual_usb_edges != required_usb_edges:
        errors.append("external layout must expose and label exactly the three selected USB ports")
    if any("dbg_header" in instance for instance, _, _, _, _ in EDGE_INTERFACES):
        errors.append("DBG10 headers are internal fallback diagnostics, not exterior user interfaces")
    required_service_edges = {
        ("s3_reset_button", "front", "left", "S3 RST"),
        ("s3_boot_button", "front", "left", "S3 BOOT"),
        ("c5_reset_button", "front", "right", "C5 RST"),
        ("c5_boot_button", "front", "right", "C5 BOOT"),
        ("rp_reset_button", "rear", "left", "RP RST"),
        ("rp_boot_button", "rear", "left", "RP BOOT"),
    }
    actual_service_edges = {
        (instance, face, side, label)
        for instance, face, side, _, label in EDGE_INTERFACES
        if instance in EXTERNAL_SERVICE_BUTTONS
    }
    if actual_service_edges != required_service_edges:
        errors.append("all six compute-domain RST/BOOT controls must remain externally labelled")
    for instance in EXTERNAL_SERVICE_BUTTONS:
        if devices[instances[instance]]["mpn"] != "Alps Alpine SKRTLAE010":
            errors.append(f"{instance}: external service control must use the exact side switch")

    control_roles = {item.role for item in REAR_CONTROLS}
    for role in ("rear independent PTT",):
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
    external_root = ET.fromstring(external_svg)
    if external_root.attrib.get("data-coordinate-model") != "L2-ASM-COORD-001-A":
        errors.append("external layout must identify the unified coordinate model")
    if (
        external_root.attrib.get("data-review-gate") != "H1.3.1"
        or external_root.attrib.get("data-review-status") != "reviewed"
    ):
        errors.append("external layout must retain the reviewed H1.3.1 gate")
    face_nodes = {
        element.attrib.get("data-face"): element
        for element in external_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-face")
    }
    if set(face_nodes) != {"front-outer", "rear-outer"} or any(
        node.attrib.get("data-board-mm") != "75x150" for node in face_nodes.values()
    ):
        errors.append("external layout must retain both exact 75x150-mm outward PCB faces")
    tx_nodes = [
        element
        for element in external_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-role") == "actual-tx-indicator"
    ]
    if len(tx_nodes) != 9 or {element.attrib.get("data-instance") for element in tx_nodes} != {
        instance for instance, _, _, _ in FRONT_FACE_INDICATORS
        if instance != "fault_led"
    }:
        errors.append("external layout must render all nine exact actual-TX/evidence indicators")
    fault_nodes = [
        element
        for element in external_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-role") == "fault-indicator"
    ]
    if len(fault_nodes) != 1 or fault_nodes[0].attrib.get("data-instance") != "fault_led":
        errors.append("external layout must render the independent FAULT indicator")
    indicator_nodes = tx_nodes + fault_nodes
    if sorted((element.attrib.get("data-row"), element.attrib.get("data-column")) for element in indicator_nodes) != [
        (str(row), str(column)) for row in (1, 2) for column in range(1, 6)
    ]:
        errors.append("external layout must identify the two aligned five-indicator rows")
    service_root = ET.fromstring(render_service_access(devices, instances))
    if (
        service_root.attrib.get("data-coordinate-model") != "L2-ASM-COORD-001-A"
        or service_root.attrib.get("data-view") != "external-service-access"
    ):
        errors.append("service-access view must retain the unified external coordinate model")
    service_instances = {
        element.attrib.get("data-instance")
        for element in service_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-instance")
    }
    required_service_instances = set(EXTERNAL_SERVICE_BUTTONS) | {
        "product_usb_connector",
        "c5_service_usb_connector",
        "rp_service_usb_connector",
    }
    if service_instances != required_service_instances:
        errors.append("service-access view must show exactly three USB ports and six recovery buttons")
    if any("dbg_header" in instance for instance in service_instances):
        errors.append("internal DBG10 headers may not appear as external service bodies")
    recessed_buttons = [
        element
        for element in service_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-instance") in EXTERNAL_SERVICE_BUTTONS
    ]
    protective_recesses = [
        element
        for element in service_root.iter("{http://www.w3.org/2000/svg}rect")
        if element.attrib.get("data-part") == "protective-recess"
    ]
    if len(recessed_buttons) != 6 or any(
        element.attrib.get("data-recessed") != "true" for element in recessed_buttons
    ) or len(protective_recesses) != 6:
        errors.append("all six external recovery buttons require a protective recessed pocket")
    service_labels = {
        element.attrib.get("data-instance"): element
        for element in service_root.iter("{http://www.w3.org/2000/svg}text")
        if element.attrib.get("data-role") == "service-control-label"
    }
    service_buttons = {
        element.attrib.get("data-instance"): element for element in recessed_buttons
    }
    if set(service_labels) != set(EXTERNAL_SERVICE_BUTTONS):
        errors.append("all six external recovery buttons require one machine-bound silk label")
    else:
        for instance, label_node in service_labels.items():
            button_node = service_buttons[instance]
            button_box = tuple(
                float(button_node.attrib[key]) for key in ("x", "y", "width", "height")
            )
            label_box = text_bounds_px(label_node)
            # Four drawing pixels are intentionally more conservative than
            # the visible gap needed at the final silkscreen scale.
            expanded_button = (
                button_box[0] - 4.0, button_box[1] - 4.0,
                button_box[2] + 8.0, button_box[3] + 8.0,
            )
            if overlaps(label_box, expanded_button):
                errors.append(f"{instance}: service silk lacks clearance to the recessed switch")
            label_visual_centre = float(label_node.attrib["y"]) - float(label_node.attrib["font-size"]) / 3
            button_centre = button_box[1] + button_box[3] / 2
            if abs(label_visual_centre - button_centre) > 0.11:
                errors.append(f"{instance}: service silk is not vertically centred on its switch")
    for token in (
        'id="front-outer-rf-bank" data-mount-face="ui-pcb-outer"',
        'id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer"',
    ):
        if token not in external_svg:
            errors.append("both antenna banks must render as outward-face assemblies")
    errors += validate_external_silkscreen(external_svg, devices, instances)
    internal_svg = render_internal(devices, instances, display_adapter_design)
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

    def rect(origin, x, y, w, h, fill, stroke, dash="", rx=2.0, extra=""):
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{sx(origin,x):.1f}" y="{sy(origin,y):.1f}" '
            f'width="{w*scale:.1f}" height="{h*scale:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dashed}{extra}/>'
        )

    return sx, sy, text, rect


def board(origin, title, scale, sx, sy, text, rect, extra=""):
    rows = [
        text(origin[0], origin[1] - RF_BARREL_OUT*scale - 22, title, 15, "bold"),
        rect(origin, 0, 0, BOARD_W, BOARD_H, "#f8fafc", "#344054", rx=5, extra=extra),
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
            label_x = centre
            if compact_labels:
                visible_lines = RF_USER_LABEL_LINES[path]
                position = RF_COMPACT_LABEL_POSITIONS.get(path)
                if position is not None:
                    label_x = float(position[0])
                    label_y = float(position[1])
                for line_index, visible_label in enumerate(visible_lines):
                    rows.append(text(sx(origin, label_x), sy(origin, label_y + 2.0 * line_index), visible_label, 4.2, "bold", "middle", "#1d4ed8"))
            else:
                rows.append(text(x, sy(origin, label_y), path, 6.2, "bold", "middle", "#1d4ed8"))
                rows.append(text(x, sy(origin, 18.2), polarity, 5.2, anchor="middle", colour="#526076"))
    return rows


def render_external(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)
    def silk_text(*args, **kwargs):
        return text(*args, **kwargs).replace(
            "<text ", '<text data-layer="pcb-silkscreen" ', 1
        )

    edge_placements = {item.instance: item for item in UI_INNER + RF_INNER}

    def service_button_projection(origin, instance, side):
        """Show the exact footprint and a DIV-like recessed side actuator."""
        item = edge_placements[instance]
        width, height = placement_size(item, devices, instances)
        body = rect(
            origin,
            item.x,
            item.y,
            width,
            height,
            "none",
            "#7c3aed",
            "2 2",
            1,
            f' data-instance="{instance}" data-projection="inner-mounted-side-switch"',
        )
        centre_y = item.y + height / 2
        recess_x = -0.8 if side == "left" else BOARD_W - 1.7
        recess = rect(
            origin,
            recess_x,
            centre_y - 2.5,
            2.5,
            5.0,
            "none",
            "#ea580c",
            "3 2",
            2,
            f' data-instance="{instance}" data-part="protective-recess" data-recess-mm="{SERVICE_BUTTON_RECESS_MM}"',
        )
        actuator_x = SERVICE_BUTTON_RECESS_MM if side == "left" else BOARD_W - SERVICE_BUTTON_RECESS_MM
        actuator = (
            f'<path d="M{sx(origin,actuator_x):.1f} {sy(origin,centre_y-1.4):.1f} '
            f'V{sy(origin,centre_y+1.4):.1f}" '
            'stroke="#7c3aed" stroke-width="4" stroke-linecap="square" '
            f'data-instance="{instance}" data-part="side-actuator" data-recessed="true"/>'
        )
        return [body, recess, actuator]

    front, rear = (80.0, 150.0), (465.0, 150.0)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1370" height="790" viewBox="0 0 1370 790" data-coordinate-model="L2-ASM-COORD-001-A" data-review-gate="H1.3.1" data-review-status="reviewed">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30, 32, "Leshy2 — dimensioned external layout", 22, "bold"),
        text(30, 56, "Text on a PCB face but outside component outlines is intended silkscreen; text outside PCB faces or inside outlines is drawing annotation.", 11, colour="#526076"),
    ]
    out += board(
        front, "Front / UI face", scale, sx, sy, text, rect,
        ' data-face="front-outer" data-board-mm="75x150"',
    )
    out += board(
        rear, "Rear / battery and expansion face", scale, sx, sy, text, rect,
        ' data-face="rear-outer" data-board-mm="75x150"',
    )

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
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 8.0), "M5Stack U214 · installed worst-case · 84×24 mm", 6.3, "bold", "middle", "#9a3412"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 12.5), "shared Cap-Bus rail · HLE-107-02-G-DV-PE-LC beneath", 5.0, "bold", "middle", "#075985"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 17.0), "insert ⊗ · remove ⊙", 6.2, anchor="middle", colour="#dc2626"))
    out.append('<g id="rear-outer-rf-bank" data-mount-face="rf-pcb-outer">')
    out += rf_bank(rear, REAR_RF, scale, sx, sy, silk_text, rect, True, True, compact_label_y=7.8)
    out.append('</g>')

    display = Placement("display", 10.25, 11.0, "display")
    dw, dh = placement_size(display, devices, instances)
    display_device = devices[instances["display"]]
    active_w, active_h = map(float, display_device["active_area_mm"])
    active_dx, active_dy = map(
        float, display_device["active_area_offset_from_body_top_left_mm"]
    )
    view_w, view_h = map(float, display_device["viewing_area_mm"])
    view_dx, view_dy = map(
        float, display_device["viewing_area_offset_from_body_top_left_mm"]
    )
    active_x = display.x + active_dx
    active_y = display.y + active_dy
    view_x = display.x + view_dx
    view_y = display.y + view_dy
    out.append(rect(front, display.x, display.y, dw, dh, "#eff6ff", "#2563eb", rx=5))
    out.append(rect(front, active_x, active_y, active_w, active_h, "#bfdbfe", "#1d4ed8", rx=3))
    out.append(rect(front, view_x, view_y, view_w, view_h, "none", "#60a5fa", "3 2", 3))
    out.append(text(sx(front,37.5), sy(front,50.5), "HMX035CTFT-001", 9, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,55.5), "ACTIVE 48.96×73.44 mm · 320×480 · 2:3", 6.5, "bold", "middle", "#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,60.5), "54.5×83.0×3.2 mm LCD/CTP body", 6.5, anchor="middle", colour="#1d4ed8"))
    out.append(text(sx(front,37.5), sy(front,65.5), "touch / view ⊗", 6.5, anchor="middle", colour="#dc2626"))
    out.append('<g id="front-outer-rf-bank" data-mount-face="ui-pcb-outer">')
    out += rf_bank(front, FRONT_RF, scale, sx, sy, silk_text, rect, True, True, compact_label_y=7.8)
    out.append('</g>')

    for index, (instance, label, x, y) in enumerate(FRONT_FACE_INDICATORS):
        role = "fault-indicator" if instance == "fault_led" else "actual-tx-indicator"
        out.append(
            rect(
                front, x, y, TX_LED_W, TX_LED_H,
                "#f59e0b" if instance == "fault_led" else "#ef4444",
                "#b45309" if instance == "fault_led" else "#991b1b", rx=1,
            ).replace(
                "/>",
                f' data-instance="{instance}" data-role="{role}" '
                f'data-row="{index // 5 + 1}" data-column="{index % 5 + 1}"/>',
            )
        )
        out.append(
            silk_text(
                sx(front,x + TX_LED_W/2), sy(front,y + 2.6), label, 4.2, "bold", "middle",
                "#b45309" if instance == "fault_led" else "#991b1b",
            )
        )

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
    for label_x, label_y, label in (
        (37.5, 119.1, "▲"),
        (37.5, 147.8, "▼"),
        (23.9, 133.2, "◀"),
        (51.1, 133.2, "▶"),
        (33.2, 127.9, "OK"),
    ):
        out.append(silk_text(sx(front,label_x), sy(front,label_y), label, 4.2, "bold", "middle", "#4c1d95"))
    front_control_by_instance = {item.instance: item for item in FRONT_CONTROLS}
    for instance, label in (("ui_switch_back", "BACK"), ("ui_switch_opt", "OPT")):
        control = front_control_by_instance[instance]
        width, _ = placement_size(control, devices, instances)
        out.append(
            silk_text(
                sx(front, control.x + width / 2), sy(front, 140.0),
                label, 5.0, "bold", "middle", "#4c1d95",
            )
        )
    for index, control in enumerate(SIDE_FUNCTION_CONTROLS, 1):
        width, height = placement_size(control, devices, instances)
        out.append(
            silk_text(
                sx(front, control.x + width / 2), sy(front, control.y + height + 2.8),
                f"F{index}", 4.2, "bold", "middle", "#4c1d95",
            )
        )

    # Every side/bottom interface is projected onto the external face even
    # when its physical body is mounted on the inward PCB side.
    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if face != "front" or side not in {"left", "right"}:
            continue
        if instance in EXTERNAL_SERVICE_BUTTONS:
            out += service_button_projection(front, instance, side)
        stroke = "#d97706" if instance.startswith("ir_") else "#2563eb"
        if instance in EXTERNAL_SERVICE_BUTTONS:
            stroke = "#7c3aed"
        if instance in EXTERNAL_SERVICE_BUTTONS:
            start_x, end_x = (-7.0, SERVICE_BUTTON_RECESS_MM) if side == "left" else (82.0, BOARD_W - SERVICE_BUTTON_RECESS_MM)
        else:
            start_x, end_x = (0.0, -7.0) if side == "left" else (75.0, 82.0)
        out.append(f'<path d="M{sx(front,start_x):.1f} {sy(front,coordinate):.1f} L{sx(front,end_x):.1f} {sy(front,coordinate):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        # Display spans x=10.25..64.75 mm; these are the exact centres of
        # the remaining equal 10.25-mm silkscreen gutters.
        if instance in EXTERNAL_SERVICE_BUTTONS:
            label_x = 7.0 if side == "left" else 68.0
        else:
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

    holder = Placement("pack_holder", 17.6, PACK_HOLDER_Y, "holder", 90)
    hw, hh = placement_size(holder, devices, instances)
    # The manufacturer's plastic body is 77.06 mm long.  The 86.00-mm value
    # is the PCB pad span, not a second body envelope.  Draw both so the SMT
    # mounting and the enclosure load path cannot be confused.
    out.append(rect(rear, holder.x, holder.y, hw, hh, "none", "#16a34a", "4 3", 3).replace(
        "/>", ' data-part="1048P-pcb-pad-span" data-dimension-mm="86.00"/>',
    ))
    out.append(rect(
        rear, PACK_HOLDER_BODY_X, PACK_HOLDER_BODY_Y,
        PACK_HOLDER_BODY_W, PACK_HOLDER_BODY_H,
        "#dcfce7", "#16a34a", rx=10,
        extra=' data-instance="pack_holder" data-mpn="Keystone 1048P" data-mounting="SMT"',
    ))
    cradle_x = PACK_HOLDER_BODY_X - 1.2
    cradle_w = PACK_HOLDER_BODY_W + 2.4
    for stop_y in (PACK_HOLDER_BODY_Y - 1.0, PACK_HOLDER_BODY_Y + PACK_HOLDER_BODY_H + 1.0):
        out.append(
            f'<path d="M{sx(rear,cradle_x):.1f} {sy(rear,stop_y):.1f} '
            f'H{sx(rear,cradle_x+cradle_w):.1f}" stroke="#ea580c" stroke-width="2" '
            'data-layer="mechanical-reference" data-part="enclosure-holder-end-stop"/>'
        )
    out.append(text(sx(rear,37.5), sy(rear,126), "1048P body 77.1 · SMT pad span 86.0", 6.1, "bold", "middle", "#166534"))
    for cell_instance, cell_x in (("pack_cell0", 28.0), ("pack_cell1", 47.0)):
        cell = Placement(cell_instance, 0.0, 0.0, "protected 18650 cell", 90)
        cell_w, cell_h = placement_size(cell, devices, instances)
        cell_y = holder.y + (hh - cell_h) / 2
        out.append(
            rect(
                rear,
                cell_x - cell_w / 2,
                cell_y,
                cell_w,
                cell_h,
                "#ecfdf3",
                "#22c55e",
                rx=20,
                extra=f' data-instance="{cell_instance}" data-source-envelope="true"',
            )
        )
        out.append(text(sx(rear,cell_x), sy(rear,86), "18650", 7, "bold", "middle", "#166534"))

    # PTT is a complete, directly pressed switch on the exposed rear PCB.
    for control in REAR_CONTROLS:
        if control.instance not in DIRECT_PRESS_REAR_CONTROLS:
            continue
        control_w, control_h = placement_size(control, devices, instances)
        fill = "#e2e8f0"
        stroke = "#64748b"
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
    for x, y, label in ((7.5, 61.5, "ENC"), (67.5, 74.0, "PTT")):
        out.append(silk_text(sx(rear,x), sy(rear,y), label, 5.0, "bold", "middle", "#4c1d95"))

    for instance, face, side, coordinate, label in EDGE_INTERFACES:
        if face != "rear" or side not in {"left", "right"}:
            continue
        if instance in EXTERNAL_SERVICE_BUTTONS:
            out += service_button_projection(rear, instance, side)
        stroke = "#7c3aed" if instance in EXTERNAL_SERVICE_BUTTONS else "#ea580c"
        if instance in EXTERNAL_SERVICE_BUTTONS:
            start_x, end_x = (-7.0, SERVICE_BUTTON_RECESS_MM) if side == "left" else (82.0, BOARD_W - SERVICE_BUTTON_RECESS_MM)
        else:
            start_x, end_x = (0.0, -7.0) if side == "left" else (75.0, 82.0)
        out.append(f'<path d="M{sx(rear,start_x):.1f} {sy(rear,coordinate):.1f} L{sx(rear,end_x):.1f} {sy(rear,coordinate):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        label_x = (7.0 if side == "left" else 68.0) if instance in EXTERNAL_SERVICE_BUTTONS else (5.0 if side == "left" else 70.0)
        lines = SIDE_INTERFACE_LABEL_LINES[instance]
        first_y = coordinate - 1.3 * (len(lines) - 1)
        for line_index, line in enumerate(lines):
            out.append(silk_text(sx(rear,label_x), sy(rear,first_y + 2.6 * line_index), line, 4.2, "bold", "middle", stroke))
    for _, face, side, x, label in EDGE_INTERFACES:
        if face != "rear" or side != "bottom":
            continue
        out.append(f'<path d="M{sx(rear,x):.1f} {sy(rear,150):.1f} V{sy(rear,157):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
        out.append(silk_text(sx(rear,x), sy(rear,149), label, 4.2, "bold", "middle", "#1d4ed8"))

    # The speaker is labelled externally, but enclosure-slot geometry is not
    # invented on this PCB-face projection.
    for instance, face, side, coordinate, label in EXTERNAL_COMPONENT_LABELS:
        if face != "rear":
            continue
        if side == "right":
            out.append(silk_text(sx(rear,BOARD_W-7.0), sy(rear,coordinate + 1.2), label, 4.2, "bold", "middle", "#2563eb"))

    for face, value, x, y, size in OUTER_FACE_PRODUCT_MARKS:
        origin = front if face == "front" else rear
        out.append(
            silk_text(
                sx(origin, x), sy(origin, y), value, size, "bold", "middle", "#172033"
            ).replace(
                "<text ", f'<text data-role="product-mark" data-face="{face}" ', 1
            )
        )

    note_x = 850
    out += [
        text(note_x,105,"What this drawing proves",16,"bold"),
        text(note_x,135,"• both 75×150-mm panels use the same millimetre scale",11),
        text(note_x,158,"• every solid component envelope comes from the MPN register",11),
        text(note_x,181,"• shared Cap-Bus rail, vertical host socket and Keystone holder all fit",11),
        text(note_x,204,"• exact components clear all M2.5 hole/head keep-outs",11),
        text(note_x,225,"• both RF connector banks mount on the outward PCB faces",11),
        text(note_x,245,"Interface direction",15,"bold"),
        text(note_x,273,"↑ / ↓ / ← / →  interface faces through that enclosure edge",11),
        text(note_x,296,"⊗ / ⊙  press toward / remove away from the viewed face",11),
        text(note_x,319,"MICROPHONE is front-face silkscreen with a downward arrow; its body remains on the rear PCB.",11),
        text(note_x,347,"TX indication",15,"bold"),
        '<circle cx="858" cy="370" r="5" fill="#ef4444" stroke="#991b1b"/>',
        text(875,374,"physical actual-TX evidence for each built-in transmitting path",11),
        text(note_x,396,"Nine physical-TX indicators plus FAULT form two aligned rows of five.",11),
        text(note_x,419,"Labels match use: WI-FI/BLE, WI-FI/15.4, nRF24-1..3, SUB-GHz, VHF/UHF, IR and LORA/EXT.",11),
        text(note_x,450,"Geometry status",15,"bold"),
        '<rect x="850" y="467" width="28" height="15" rx="3" fill="#eef2f6" stroke="#667085"/>',
        text(890,479,"solid — registered MPN/reference assembly envelope",11),
        '<rect x="850" y="497" width="28" height="15" rx="3" fill="none" stroke="#ea580c" stroke-dasharray="5 3"/>',
        text(890,509,"orange dashed — open custom enclosure drawing",11),
        '<rect x="850" y="527" width="28" height="15" rx="3" fill="#ede9fe" stroke="#7c3aed"/>',
        text(890,539,"violet — selected navigation controls",11),
        text(note_x,566,"RF connectors are outward-face bodies with barrels and hex nuts.",11,"bold"),
        text(note_x,589,"SMA: GCT RFPC-SMA31-FN-175-A · 6 GHz · IP67 · 1.6-mm PCB.",11),
        text(note_x,609,"RP-SMA: GCT RFPC-SMA32-FN-175-A · same panel cut-out.",11),
        text(note_x,630,"Cap-Bus host: Samtec HLE-107-02-G-DV-PE-LC · 2×7 · 2.54 mm · pass-through.",11),
        text(note_x,653,"Dimensioned projection — not an enclosure release drawing.",11,"bold",colour="#b42318"),
        text(note_x,676,"Navigation is five exact OMRON B3S-1100P direct buttons; no custom cap or actuator.",11),
        text(note_x,699,"Davies 1227-J is the exact encoder knob; only its fit HIL remains.",11),
        text(note_x,722,"UP/DOWN/LEFT/RIGHT/OK/BACK/OPT/F1…F8/PTT are serial direct buttons.",11,"bold"),
        text(note_x,745,"The side C&K JS102011SCQN is the sole RUN/KILL and source-command control.",11),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_service_access(devices, instances):
    """Render an uncluttered user view of the external recovery interfaces."""
    scale = 2.8
    sx, sy, text, rect = helpers(scale)

    front = (190.0, 150.0)
    rear = (700.0, 150.0)
    canvas_width = 1300.0
    note_left = 950.0
    note_width = 300.0
    note_centre = note_left + note_width / 2
    rear_right = rear[0] + BOARD_W * scale
    if note_left - rear_right < 40.0:
        raise ValueError("service-access notes require at least 40 px clearance from the rear board")
    if note_left + note_width > canvas_width:
        raise ValueError("service-access notes exceed the SVG canvas")
    edge_placements = {item.instance: item for item in UI_INNER + RF_INNER}

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width:.0f}" height="690" '
        f'viewBox="0 0 {canvas_width:.0f} 690" data-coordinate-model="L2-ASM-COORD-001-A" '
        'data-view="external-service-access">',
        '<defs><marker id="service-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30, 34, "Leshy2 — external service access", 23, "bold"),
        text(30, 59, "Three independent USB paths and six serial side controls; DBG10 headers remain inside the opened sandwich.", 12, colour="#526076"),
    ]
    out += board(
        front, "Front / UI face", scale, sx, sy, text, rect,
        ' data-face="front-outer" data-board-mm="75x150"',
    )
    out += board(
        rear, "Rear / battery face", scale, sx, sy, text, rect,
        ' data-face="rear-outer" data-board-mm="75x150"',
    )

    # Orientation cues only: the service drawing intentionally suppresses all
    # unrelated controls and RF parts so each recovery interface is legible.
    out.append(rect(front, 10.25, 11.0, 54.5, 83.0, "#eff6ff", "#93c5fd", rx=5))
    out.append(text(sx(front, 37.5), sy(front, 53.0), "DISPLAY", 11, "bold", "middle", "#60a5fa"))
    out.append(rect(rear, 17.6, PACK_HOLDER_Y, 39.8, PACK_HOLDER_H, "#ecfdf3", "#86efac", rx=10))
    out.append(text(sx(rear, 37.5), sy(rear, 85.0), "2× 18650", 11, "bold", "middle", "#4ade80"))

    def side_control(origin, instance, side, silk):
        item = edge_placements[instance]
        width, height = placement_size(item, devices, instances)
        centre_y = item.y + height / 2
        edge_x = 0.0 if side == "left" else BOARD_W
        edge_px = sx(origin, edge_x)
        actuator_x = edge_px + (SERVICE_BUTTON_RECESS_MM * scale if side == "left" else -SERVICE_BUTTON_RECESS_MM * scale)
        label_x = sx(origin, 7.0 if side == "left" else 68.0)
        anchor = "start" if side == "left" else "end"
        out.append(
            f'<rect x="{edge_px - (3 if side == "left" else 11):.1f}" y="{sy(origin, centre_y) - 9:.1f}" '
            'width="14" height="18" rx="3" fill="none" stroke="#ea580c" stroke-dasharray="4 2" '
            f'data-part="protective-recess" data-recess-mm="{SERVICE_BUTTON_RECESS_MM}"/>'
        )
        out.append(
            f'<rect x="{actuator_x - 3:.1f}" y="{sy(origin, centre_y) - 6:.1f}" '
            'width="6" height="12" rx="2" fill="#ede9fe" stroke="#7c3aed" '
            f'data-instance="{instance}" data-mpn="Alps Alpine SKRTLAE010" data-recessed="true"/>'
        )
        out.append(
            f'<path d="M{edge_px + (-28 if side == "left" else 28):.1f} {sy(origin, centre_y):.1f} '
            f'L{actuator_x:.1f} {sy(origin, centre_y):.1f}" '
            'stroke="#dc2626" stroke-width="1.5" marker-end="url(#service-arrow)"/>'
        )
        # SVG text uses a baseline, not a visual centre.  Keep the baseline a
        # fixed font-derived offset below the switch centre so left- and
        # right-edge labels remain optically centred beside their actuators.
        label_baseline = sy(origin, centre_y) + 7.2 / 3
        out.append(
            text(label_x, label_baseline, silk, 7.2, "bold", anchor, "#5b21b6").replace(
                "<text ",
                f'<text data-layer="pcb-silkscreen" data-role="service-control-label" data-instance="{instance}" ',
                1,
            )
        )

    for instance, side, silk in (
        ("s3_reset_button", "left", "S3 RST"),
        ("s3_boot_button", "left", "S3 BOOT"),
        ("c5_reset_button", "right", "C5 RST"),
        ("c5_boot_button", "right", "C5 BOOT"),
    ):
        side_control(front, instance, side, silk)
    for instance, side, silk in (
        ("rp_reset_button", "left", "RP RST"),
        ("rp_boot_button", "left", "RP BOOT"),
    ):
        side_control(rear, instance, side, silk)

    def usb_port(origin, instance, centre_x, silk, role, role_y_offset=47):
        device = devices[instances[instance]]
        port_w = float(device["dimensions_mm"][0])
        cx = sx(origin, centre_x)
        edge_y = sy(origin, BOARD_H)
        out.append(
            f'<rect x="{cx - port_w * scale / 2:.1f}" y="{edge_y - 4:.1f}" '
            f'width="{port_w * scale:.1f}" height="12" rx="5" fill="#dbeafe" '
            f'stroke="#2563eb" stroke-width="1.5" data-instance="{instance}" '
            f'data-mpn="{html.escape(device["mpn"])}"/>'
        )
        out.append(
            f'<path d="M{cx:.1f} {edge_y + 9:.1f} V{edge_y + 28:.1f}" '
            'stroke="#dc2626" stroke-width="1.5" marker-end="url(#service-arrow)"/>'
        )
        out.append(
            text(cx, edge_y - 8, silk, 7.0, "bold", "middle", "#1d4ed8").replace(
                "<text ", '<text data-layer="pcb-silkscreen" ', 1
            )
        )
        out.append(text(cx, edge_y + role_y_offset, role, 6.4, "normal", "middle", "#526076"))

    usb_port(front, "c5_service_usb_connector", 31.47, "C5 SERVICE USB", "data only · no device power")
    usb_port(rear, "product_usb_connector", 16.47, "USB / POWER", "S3 native USB + power/charge", 47)
    usb_port(rear, "rp_service_usb_connector", 37.47, "RP SERVICE USB", "data only · no device power", 65)

    out += [
        text(note_centre, 120, "External recovery map", 16, "bold", "middle"),
        text(note_left, 160, "S3", 13, "bold", colour="#5b21b6"),
        text(note_left + 40, 160, "USB / POWER + RST + BOOT", 11),
        text(note_left, 195, "C5", 13, "bold", colour="#5b21b6"),
        text(note_left + 40, 195, "SERVICE USB + RST + BOOT", 11),
        text(note_left, 230, "RP", 13, "bold", colour="#5b21b6"),
        text(note_left + 40, 230, "SERVICE USB + RST + BOOT", 11),
        text(note_left, 280, "Port roles", 15, "bold"),
        text(note_left, 310, "• USB / POWER is the sole powered USB port", 10),
        text(note_left, 336, "• C5/RP service VBUS is sense-only", 10),
        text(note_left, 362, "• every RST/BOOT switch is recessed yet independently reachable", 10),
        text(note_left, 412, "Inside after opening", 15, "bold"),
        text(note_left, 442, "3× keyed DBG10 fallback headers", 10),
        text(note_left, 466, "S3/C5: UART0 · RESET · BOOT", 10),
        text(note_left, 490, "RP: SWD · RUN · USB_BOOT", 10),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_internal(devices, instances, display_adapter_design):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)

    ui, rf = (80.0, 165.0), (465.0, 165.0)
    ui_items = UI_INNER + UI_RF_CABLES
    rf_items = RF_INNER + RF_NRF_CABLE_RESERVES
    all_items = ui_items + rf_items
    numbers = {item.instance: index for index, item in enumerate(all_items, 1)}
    legend_first_y = 795
    legend_row_height = 21
    rf_legend_columns = 3
    rf_legend_rows = math.ceil(len(rf_items) / rf_legend_columns)
    legend_bottom = legend_first_y + (max(len(ui_items), rf_legend_rows) - 1) * legend_row_height + 9
    notes_top = max(560, legend_bottom + 35)
    clearance_pairs = interboard_clearance_pairs(devices, instances)
    individual_clearances = interboard_individual_clearances(devices, instances)
    adapter_clearance_pairs = display_adapter_opposing_clearance_pairs(
        display_adapter_design, devices, instances
    )
    cable_clearance_pairs = cable_interboard_clearance_pairs(devices, instances)
    nrf_reserve_clearance_pairs = nrf_cable_reserve_opposing_pairs(devices, instances)
    through_board_clearance_pairs = through_board_opposing_pairs(devices, instances)
    maximum_cable_od = max(
        float(devices[instances[route.instance]]["electrical_contract"]["cable_outer_diameter_mm"])
        for route in UI_RF_CABLES + tuple(
            CableRoute(reserve.instance, reserve.escape_points, reserve.role)
            for reserve in RF_NRF_CABLE_RESERVES
        )
    )
    minimum_clearance, minimum_ui, minimum_rf = clearance_pairs[0]
    minimum_individual_clearance, tallest_item = individual_clearances[0]
    minimum_adapter_clearance, minimum_adapter_body = adapter_clearance_pairs[0]
    minimum_nrf_reserve_clearance, _, _ = nrf_reserve_clearance_pairs[0]
    minimum_through_board_clearance, _, _ = through_board_clearance_pairs[0]
    tallest_height = placement_height(tallest_item, devices, instances)
    svg_height = notes_top + 430
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="{svg_height}" viewBox="0 0 1510 {svg_height}" data-view="mirrored-x" data-inner-silkscreen="none">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30,32,"Leshy2 — dimensioned inner-board placement",22,"bold"),
        text(30,56,"Inner PCB faces contain no silkscreen text; numbers inside outlines are drawing annotations.",11,colour="#526076"),
        text(30,72,"Red antenna arrows reference outer-face ports; other red arrows show enclosure exits.",9.2,colour="#526076"),
    ]
    out += board(ui, "Front/display PCB — inner side (not user-facing)", scale, sx, sy, text, rect)
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

    out.append(
        '<g id="all-antenna-pcb-topology-guides" '
        'data-route-state="pre-ecad-topology-only" data-medium="controlled-50-ohm-pcb">'
    )
    for guide in ANTENNA_TOPOLOGY_GUIDES:
        origin = ui if guide.frame == "ui-inner" else rf
        points = " ".join(
            f"{sx(origin,mirrored_x(x)):.1f},{sy(origin,y):.1f}"
            for x, y in guide.points
        )
        out.append(
            f'<polyline points="{points}" fill="none" stroke="#2563eb" '
            f'stroke-width="1.6" stroke-dasharray="4 3" '
            f'data-instance="{guide.instance}" data-path="{guide.path}" '
            f'data-source="{guide.source_instance}" data-external="{guide.external_instance}" '
            f'data-role="{html.escape(guide.role)}"/>'
        )
        for endpoint_x, endpoint_y in (guide.points[0], guide.points[-1]):
            out.append(
                f'<circle cx="{sx(origin,mirrored_x(endpoint_x)):.1f}" '
                f'cy="{sy(origin,endpoint_y):.1f}" r="3.2" fill="#ffffff" '
                f'stroke="#2563eb" stroke-width="1.2"/>'
            )
    out.append('</g>')

    path_annotation = {
        "S3-2G4": "S3",
        "RX-FM/SW": "FM/SW/AIR",
        "RX-AM/LW": "AM/LW",
        "C5-2G4/5": "C5",
        "N24-0": "N24-1",
        "CC-SUB": "SUB",
        "N24-1": "N24-2",
        "VOICE-VHF": "VHF",
        "VOICE-UHF": "UHF",
        "N24-2": "N24-3",
    }
    out.append('<g id="outer-antenna-datum-annotations" data-layer="drawing-annotation">')
    for origin, bank in ((ui, FRONT_RF), (rf, REAR_RF)):
        for centre, path, _kind in bank:
            out.append(
                text(
                    sx(origin, mirrored_x(centre)),
                    124,
                    path_annotation[path],
                    7.2,
                    "bold",
                    "middle",
                    "#1d4ed8",
                )
            )
    out.append('</g>')

    def rf_feed_path_callout(
        x: float,
        heading: str,
        module_mpn: str,
        path_id: str,
    ) -> list[str]:
        module_rf_role = (
            "module · no RF land; output is built-in U.FL"
            if path_id == "s3"
            else "module · ANT1 U.FL active; ANT2 land disabled"
        )
        rows = [
            (module_mpn, module_rf_role, "#eef2ff", "#4f46e5"),
            ("TE Connectivity 2118651-2", "removable 30-mm microcoax cable", "#ecfdf5", "#0f766e"),
            ("Hirose U.FL-R-SMT-1(10)", "PCB re-entry · feeds TX coupler and outer RP-SMA", "#ecfdf5", "#0f766e"),
            ("KYOCERA AVX CP0603Q5425ENTR", "PCB 50 Ω mainline · forward TX sample", "#eff6ff", "#2563eb"),
            ("GCT RFPC-SMA32-FN-175-A", "outward RP-SMA · antenna screws on here", "#fff7ed", "#ea580c"),
        ]
        top = 166.0
        width = 300.0
        height = 46.0
        gap = 18.0
        cx = x + width / 2
        rendered = [
            f'<g data-rf-feed-path="{path_id}" data-duplicate-hardware="false">',
            text(x, 142, heading, 13, "bold", colour="#172033"),
        ]
        for index, (mpn, role, fill, stroke) in enumerate(rows):
            y = top + index * (height + gap)
            rendered.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
                f'rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'
            )
            rendered.append(text(cx, y + 18, mpn, 9.0, "bold", "middle"))
            rendered.append(text(cx, y + 34, role, 8.1, anchor="middle", colour="#526076"))
            if index < len(rows) - 1:
                line_y1 = y + height
                line_y2 = y + height + gap
                cable_segment = index < 2
                colour = "#0f766e" if cable_segment else "#2563eb"
                dash = "" if cable_segment else ' stroke-dasharray="4 3"'
                rendered.append(
                    f'<path d="M{cx:.1f} {line_y1:.1f} V{line_y2:.1f}" '
                    f'stroke="{colour}" stroke-width="3"{dash}/>'
                )
        rendered.append('</g>')
        return rendered

    out += [
        text(820, 102, "Antenna-to-radio map · all ten paths", 17, "bold"),
        text(820, 122, "Drawing explanation — not PCB silkscreen.", 9.5, colour="#526076"),
        text(820, 529, "ring on S3/C5 = module U.FL · ring on nRF = module IPEX · numbered ring = board U.FL", 9.5, "bold", colour="#0f766e"),
        text(820, 547, "nRF ring position is schematic; its connector exists, while generation and exact axis close at H5", 9.2, colour="#0e7490"),
        text(820, 570, "solid green/cyan = direct cable projection · dashed blue = future 50 Ω PCB mainline", 10, "bold", colour="#344054"),
        text(820, 589, "The 30-mm cable has 3D slack; the forward TX sample branches only after the board U.FL.", 9.2, colour="#526076"),
        text(820, 616, "UI antenna bank: S3 · FM/SW/AIR · AM/LW · C5", 10, "bold", colour="#1d4ed8"),
        text(820, 636, "RF antenna bank: nRF24-1/2/3 · SUB-GHz · FPV · VHF/UHF", 10, "bold", colour="#1d4ed8"),
        text(820, 656, "Every blue guide ends at its matching red outer-face antenna datum; none represents finished KiCad copper.", 9.2, colour="#526076"),
    ]
    out += rf_feed_path_callout(
        820.0,
        "S3 native antenna path",
        devices[instances["s3"]]["mpn"],
        "s3",
    )
    out += rf_feed_path_callout(
        1160.0,
        "C5 native antenna path",
        devices[instances["c5"]]["mpn"],
        "c5",
    )

    for zone in INTERNAL_RESERVES:
        view_x = mirrored_x(zone.x, zone.w)
        out.append(
            rect(
                rf,
                view_x,
                zone.y,
                zone.w,
                zone.h,
                "#fff7ed",
                "#ea580c",
                "5 3",
                3,
                f' data-zone-kind="{zone.reserve_class}" data-zone="{zone.name}"',
            )
        )
        out.append(text(sx(rf,view_x+zone.w/2), sy(rf,zone.y+zone.h/2)+2, "CC RF REF", 5.2, "bold", "middle", "#9a3412"))

    out.append('<g id="exact-native-rf-jumpers" data-medium="removable-microcoax" data-route-units="mm" data-rendering="direct-axis-projection" data-slack-state="H5-open">')
    for route in UI_RF_CABLES:
        route_device = devices[instances[route.instance]]
        cable_od = float(route_device["electrical_contract"]["cable_outer_diameter_mm"])
        points = " ".join(
            f"{sx(ui,mirrored_x(x)):.1f},{sy(ui,y):.1f}"
            for x, y in route.points
        )
        out.append(
            f'<polyline points="{points}" fill="none" stroke="#0f766e" '
            f'stroke-width="{cable_od*scale:.2f}" stroke-linecap="round" stroke-linejoin="round" '
            f'data-instance="{route.instance}" '
            f'data-projected-chord-mm="{polyline_length(route.points):.2f}" '
            f'data-assembly-length-mm="{float(route_device["electrical_contract"]["cable_length_mm"]):.2f}" '
            f'data-unprojected-slack-mm="{float(route_device["electrical_contract"]["cable_length_mm"])-polyline_length(route.points):.2f}"/>'
        )
        for endpoint_x, endpoint_y in (route.points[0], route.points[-1]):
            out.append(
                f'<circle cx="{sx(ui,mirrored_x(endpoint_x)):.1f}" cy="{sy(ui,endpoint_y):.1f}" '
                f'r="{1.35*scale:.1f}" fill="none" stroke="#0f766e" stroke-width="1.2"/>'
            )
        annotation_x = (route.points[0][0] + route.points[-1][0]) / 2
        annotation_y = (route.points[0][1] + route.points[-1][1]) / 2
        out.append(
            text(
                sx(ui,mirrored_x(annotation_x)), sy(ui,annotation_y)-5,
                str(numbers[route.instance]), 6.8, "bold", "middle", "#115e59"
            )
        )
    out.append('</g>')

    out.append('<g id="nrf-module-face-cable-reserves" data-medium="removable-microcoax" data-rendering="direct-connector-projection" data-axis-state="schematic-position-H5-open" data-route-units="mm">')
    for reserve in RF_NRF_CABLE_RESERVES:
        module_x, module_y, module_w, module_h = nrf_cable_reserve_module_box(
            reserve, devices, instances
        )
        out.append(
            rect(
                rf,
                mirrored_x(module_x, module_w),
                module_y,
                module_w,
                module_h,
                "none",
                "#0891b2",
                "4 3",
                2,
                f' data-instance="{reserve.instance}" data-reserve="module-face"',
            )
        )
        points = " ".join(
            f"{sx(rf,mirrored_x(x)):.1f},{sy(rf,y):.1f}"
            for x, y in reserve.escape_points
        )
        cable_od = float(
            devices[instances[reserve.instance]]["electrical_contract"][
                "cable_outer_diameter_mm"
            ]
        )
        assembly_length = float(
            devices[instances[reserve.instance]]["electrical_contract"][
                "cable_length_mm"
            ]
        )
        out.append(
            f'<polyline points="{points}" fill="none" stroke="#0891b2" '
            f'stroke-width="{cable_od*scale:.2f}" stroke-linecap="round" stroke-linejoin="round" '
            f'data-instance="{reserve.instance}" data-reserve="whole-module-face-plus-direct-projection" '
            f'data-projected-chord-mm="{polyline_length(reserve.escape_points):.2f}" '
            f'data-assembly-length-mm="{assembly_length:.2f}" '
            f'data-unprojected-slack-mm="{assembly_length-polyline_length(reserve.escape_points):.2f}"/>'
        )
        annotation_x = (reserve.escape_points[0][0] + reserve.escape_points[-1][0]) / 2
        annotation_y = (reserve.escape_points[0][1] + reserve.escape_points[-1][1]) / 2
        out.append(
            text(
                sx(rf,mirrored_x(annotation_x)), sy(rf,annotation_y)-4,
                str(numbers[reserve.instance]), 6.8, "bold", "middle", "#0e7490"
            )
        )
    out.append('</g>')

    out.append('<g id="encoder-through-board-features" data-source-face="rear-outer" data-inner-projection-mm="3.5">')
    for feature in encoder_through_board_features(devices, instances):
        out.append(
            rect(
                rf,
                mirrored_x(feature.x, feature.w),
                feature.y,
                feature.w,
                feature.h,
                "#fdf2f8",
                "#be185d",
                "2 2",
                1,
                f' data-feature="{feature.feature}"',
            )
        )
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
            mounting = (
                ' data-mounting="mid-mount-board-cutout" data-cutout-evidence="H5-open"'
                if item.instance == "headphone_jack"
                else ""
            )
            out.append(
                rect(
                    origin,
                    view_x,
                    item.y,
                    w,
                    h,
                    fill,
                    stroke,
                    rx=2,
                    extra=f' data-instance="{item.instance}"{mounting}',
                )
            )
            # RF cable-to-trace handoffs get one numbered U.FL badge below;
            # repeating the number inside the tiny connector body makes both
            # annotations unreadable.
            if item.instance not in BOARD_RF_CABLE_TO_TRACE_HANDOFFS:
                component_number = str(numbers[item.instance])
                if item.instance == "speaker":
                    component_number += " · SPK"
                out.append(text(sx(origin,view_x+w/2), sy(origin,item.y+h/2)+3, component_number, 7.5 if item.instance != "microphone" else 5.2, "bold", "middle"))

    def ufl_symbol(
        origin: tuple[float, float],
        centre: tuple[float, float],
        instance: str,
        relation: str,
        number: int | None = None,
        connector_kind: str = "U.FL-compatible Gen1",
        position_state: str = "exact",
        stroke: str = "#0f766e",
    ) -> list[str]:
        centre_x = sx(origin, mirrored_x(centre[0]))
        centre_y = sy(origin, centre[1])
        outer_r = 1.40 * scale
        inner_r = 0.38 * scale
        rendered = [
            f'<g data-instance="{instance}" data-rf-connector="{connector_kind}" '
            f'data-relation="{relation}" data-position-state="{position_state}">',
            f'<circle cx="{centre_x:.1f}" cy="{centre_y:.1f}" r="{outer_r:.1f}" '
            f'fill="#ffffff" stroke="{stroke}" stroke-width="1.6"/>',
            f'<circle cx="{centre_x:.1f}" cy="{centre_y:.1f}" r="{inner_r:.1f}" '
            f'fill="#f59e0b" stroke="#92400e" stroke-width="0.8"/>',
        ]
        if number is not None:
            badge_x = centre_x + outer_r * 0.78
            badge_y = centre_y - outer_r * 0.78
            rendered.extend(
                [
                    f'<circle cx="{badge_x:.1f}" cy="{badge_y:.1f}" r="3.8" '
                    f'fill="#ffffff" stroke="#667085" stroke-width="1.0"/>',
                    text(badge_x, badge_y + 2.2, str(number), 5.6, "bold", "middle"),
                ]
            )
        rendered.append('</g>')
        return rendered

    out.append('<g id="module-integrated-rf-connectors" data-count="5" data-exact-position-count="2" data-schematic-position-count="3">')
    for route in UI_RF_CABLES:
        module_instance = route.instance.removesuffix("_rf_jumper")
        out += ufl_symbol(
            ui,
            route.points[0],
            f"{module_instance}_integrated_ufl",
            "module-output-and-cable-start",
        )
    for reserve in RF_NRF_CABLE_RESERVES:
        out += ufl_symbol(
            rf,
            reserve.escape_points[0],
            f"{reserve.module_instance}_integrated_ipex",
            "module-IPEX-output-and-cable-start",
            connector_kind="Ebyte-published IPEX; generation H5-open",
            position_state="schematic-within-published-module-face",
            stroke="#0891b2",
        )
    out.append('</g>')

    out.append('<g id="board-rf-cable-to-trace-handoffs" data-count="5">')
    for origin, placements in ((ui, UI_INNER), (rf, RF_INNER)):
        for item in placements:
            if item.instance not in BOARD_RF_CABLE_TO_TRACE_HANDOFFS:
                continue
            item_w, item_h = placement_size(item, devices, instances)
            out += ufl_symbol(
                origin,
                (item.x + item_w / 2, item.y + item_h / 2),
                item.instance,
                "physical-cable-end-and-pcb-trace-start",
                numbers[item.instance],
            )
    out.append('</g>')
    arrows = []
    ui_inner_instances = {item.instance for item in UI_INNER}
    for instance, _face, side, coordinate, _ in EDGE_INTERFACES:
        # The exterior label face and the physical source PCB are independent:
        # MICROPHONE is printed on the front, while its body remains on RF-inner.
        origin = ui if instance in ui_inner_instances else rf
        if side == "left":
            arrows.append((origin, 0.0, coordinate, -10.0, coordinate))
        elif side == "right":
            arrows.append((origin, BOARD_W, coordinate, BOARD_W + 10.0, coordinate))
        else:
            arrows.append((origin, coordinate, BOARD_H, coordinate, BOARD_H + 9.0))
    for origin, x1, y1, x2, y2 in arrows:
        out.append(f'<path d="M{sx(origin,mirrored_x(x1)):.1f} {sy(origin,y1):.1f} L{sx(origin,mirrored_x(x2)):.1f} {sy(origin,y2):.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>')
    ui_legend_x = 30
    rf_legend_x = (400, 770, 1140)
    out += [
        text(30,750,"Numbered physical devices",16,"bold"),
        text(ui_legend_x,775,"Front/display PCB — internal components",12,"bold",colour="#1d4ed8"),
    ]
    y = legend_first_y
    for item in ui_items:
        mpn = devices[instances[item.instance]]["mpn"].replace(" (QDtech schematic assembly marking)", "")
        out.append(text(ui_legend_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(ui_legend_x+26,y+9,item.role,7.2,colour="#526076"))
        y += legend_row_height
    for column_index, column_x in enumerate(rf_legend_x):
        first = column_index * rf_legend_rows
        last = min(first + rf_legend_rows, len(rf_items))
        out.append(
            text(
                column_x, 775,
                f"RF/power PCB · {column_index + 1}/{rf_legend_columns}",
                12, "bold", colour="#c2410c",
            )
        )
        y = legend_first_y
        for item in rf_items[first:last]:
            mpn = devices[instances[item.instance]]["mpn"]
            out.append(text(column_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
            out.append(text(column_x+26,y+9,item.role,7.2,colour="#526076"))
            y += legend_row_height
    note_x = 30
    out += [
        f'<g id="validated-clearances" data-legend-bottom="{legend_bottom}" data-top="{notes_top}" '
        f'data-inner-body-count="{len(individual_clearances)}" data-max-inner-height-mm="{tallest_height:.2f}" '
        f'data-min-single-body-clearance-mm="{minimum_individual_clearance:.2f}" '
        f'data-display-adapter-opposing-pairs="{len(adapter_clearance_pairs)}" '
        f'data-min-display-adapter-clearance-mm="{minimum_adapter_clearance:.2f}" '
        f'data-opposing-pairs="{len(clearance_pairs)}" data-intentional-mates="{len(INTENTIONAL_INTERBOARD_MATES)}" '
        f'data-min-z-clearance-mm="{minimum_clearance:.2f}" data-rf-cable-routes="{len(UI_RF_CABLES)}" '
        f'data-rf-pcb-topology-guides="{len(ANTENNA_TOPOLOGY_GUIDES)}" '
        f'data-nrf-cable-reserves="{len(RF_NRF_CABLE_RESERVES)}" '
        f'data-opposing-cable-pairs="{len(cable_clearance_pairs)}" data-cable-od-max-mm="{maximum_cable_od:.2f}" '
        f'data-nrf-reserve-opposing-pairs="{len(nrf_reserve_clearance_pairs)}" '
        f'data-encoder-through-features="{len(encoder_through_board_features(devices, instances))}" '
        f'data-functional-zones="{len(INTERNAL_RESERVES)}" data-voice-v-rf-endpoint-distance-mm="{polyline_length(VOICE_V_RF_CORRIDOR):.2f}" data-voice-u-rf-endpoint-distance-mm="{polyline_length(VOICE_U_RF_CORRIDOR):.2f}">',
        text(note_x,notes_top,"Validated clearances",14,"bold"),
        text(note_x,notes_top+24,"• same-face device-to-device clearance: ≥0.7 mm",10),
        text(note_x,notes_top+45,f"• all {len(individual_clearances)} inner bodies checked individually; tallest {tallest_height:.2f} mm; opposite-plane remainder {minimum_individual_clearance:.2f} mm",10),
        text(note_x,notes_top+66,f"• complete 3.80-mm display adapter: {len(adapter_clearance_pairs)} opposing crossings; minimum Z gap {minimum_adapter_clearance:.2f} mm to {minimum_adapter_body.instance}",10),
        text(note_x,notes_top+87,f"• opposing inner faces: {len(clearance_pairs)} non-mating XY pairs checked; minimum Z gap {minimum_clearance:.2f} mm",10),
        text(note_x,notes_top+108,f"• outward connector / through-hole tail clearance on the opposite face: ≥{OPPOSITE_FACE_CLEARANCE_MM:.1f} mm",10),
        text(note_x,notes_top+129,f"• RF coax: {len(UI_RF_CABLES)} direct exact-endpoint projections + {len(RF_NRF_CABLE_RESERVES)} nRF module-face reserves; all five 30-mm assemblies accounted",10),
        text(note_x,notes_top+150,f"• limiting pair: {numbers[minimum_ui.instance]:02d} {minimum_ui.role} / {numbers[minimum_rf.instance]:02d} {minimum_rf.role}",10),
        text(note_x,notes_top+171,"• exact M1 plug/receptacle is one intentional 11-mm mate, not a clearance pair",10),
        text(note_x,notes_top+192,"• M2.5 hole/head keep-out: 4.0-mm radius",10),
        text(note_x,notes_top+213,"• both inner views are horizontally mirrored from their external faces",10),
        text(note_x,notes_top+234,f"• nRF reserve crossings: {len(nrf_reserve_clearance_pairs)}; minimum Z gap {minimum_nrf_reserve_clearance:.2f} mm; drawn IPEX positions are schematic and close in H5",10),
        text(note_x,notes_top+255,f"• EC11E through-board features: 7 checked; {len(through_board_clearance_pairs)} opposing crossings; minimum Z gap {minimum_through_board_clearance:.2f} mm",10),
        text(note_x,notes_top+276,f"• all {len(ANTENNA_TOPOLOGY_GUIDES)} onboard antenna paths have a source-to-port topology guide; final copper remains KiCad work",10),
        text(note_x,notes_top+297,"• orange dashed boundary is a placement zone, not one combined device",10),
        text(note_x,notes_top+318,"SMA · GCT RFPC-SMA31-FN-175-A",9.2,"bold",colour="#344054"),
        text(note_x,notes_top+338,"RP-SMA · GCT RFPC-SMA32-FN-175-A",9.2,"bold",colour="#344054"),
        text(note_x,notes_top+364,"All five native/nRF module feeds use exact 30-mm 2118651-2 Gen1 jumpers.",9.2,"bold",colour="#166534"),
        text(note_x,notes_top+385,"Physical keep-outs pass; display-tail evidence and final PCB copper/via DRC remain open.",9.2,"bold",colour="#b42318"),
        text(note_x,notes_top+406,"Placement projection; all mechanically significant bodies are accounted; small passives and production copper remain ECAD work.",9.2,colour="#526076"),
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
    holder = Placement("pack_holder", 17.6, PACK_HOLDER_Y, "battery holder", 90)
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
        f'<g id="u214-zone" data-plan-y-mm="{U214_Y:.1f}..{U214_Y + U214_H:.1f}" data-overhang-mm="4.5" data-retention-pitch-mm="56">',
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
        t(x(37.5), y(U214_Y + 4.5), "removable U214 Cap · 84×24 mm", 11, "bold", "middle", "#9a3412"),
        t(x(37.5), y(U214_Y + 9.0), "raised 75-mm rail · vertical socket beneath", 8.5, "bold", "middle", "#075985"),
        t(x(37.5), y(U214_Y + 17.5), "insert ⊗ / remove ⊙", 8.5, "bold", "middle", "#075985"),
        '</g>',
    ]

    # Battery holder begins 0.9 mm after the Cap envelope. It never
    # shares plan area with the Cap or its rail.
    out += [
        f'<g id="battery-zone" data-plan-y-mm="{PACK_HOLDER_Y:.1f}..{PACK_HOLDER_Y + PACK_HOLDER_H:.1f}" data-gap-from-u214-mm="{PACK_HOLDER_Y - U214_Y - U214_H:.1f}">',
        r(holder.x, holder.y, holder_w, holder_h, "#dcfce7", "#16a34a", "", 12, ' data-part="battery-holder"'),
    ]
    for cell_x in (28.0, 47.0):
        out.append(r(cell_x-9.3, PACK_CELL_Y, 18.6, 65.0, "#ecfdf3", "#22c55e", "", 20, ' data-part="18650-cell"'))
        out.append(t(x(cell_x), y(PACK_CELL_Y + 34.0), "18650", 10, "bold", "middle", "#166534"))
    out += [
        t(x(37.5), y(PACK_HOLDER_Y + 82.0), "Keystone 1048P · 39.8×86 mm plan", 9, "bold", "middle", "#166534"),
        '</g>',
    ]

    # PTT is an exact directly pressed switch body; RUN/KILL is side-facing.
    out.append('<g id="rear-controls" data-direct-press="PTT" data-actuator-reserves="none" data-enclosure-reserves="none">')
    for control in REAR_CONTROLS:
        control_w, control_h = placement_size(control, devices, instances)
        fill = "#e2e8f0"
        stroke = "#64748b"
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
        (67.5, 74.0, "PTT", "#4c1d95"),
    ):
        out.append(t(x(label_x), y(label_y), label, 7.0, "bold", "middle", colour))
    out.append('</g>')

    # Dimensions: base, Cap, overhang, retention and the two non-overlapping
    # longitudinal bands. These are documentation annotations, not silk.
    out += h_dim(0, BOARD_W, 744, "base PCB · 75 mm")
    out += h_dim(U214_X, U214_X+U214_W, 773, "installed U214 worst-case · 84 mm")
    out += h_dim(U214_X, 0, y(U214_Y)-10, "4.5")
    out += h_dim(BOARD_W, U214_X+U214_W, y(U214_Y)-10, "4.5")
    out += h_dim(U214_RETENTION_X[0], U214_RETENTION_X[1], 802, "retention · 56 mm")
    out += v_dim(U214_Y, U214_Y+U214_H, x(U214_X)-30, "24 mm")
    out += v_dim(PACK_HOLDER_Y, PACK_HOLDER_Y + PACK_HOLDER_H, x(BOARD_W)+52, "86 mm holder", rotate_label=True)

    note_x = 560.0
    out += [
        t(note_x, 112, "Fit result", 17, "bold"),
        t(note_x, 143, f"✓ ten antenna bodies end at Y=6 mm; the Cap starts at Y={U214_Y:.1f} mm", 12, "bold", colour="#166534"),
        t(note_x, 170, f"✓ U214 occupies Y={U214_Y:.1f}…{U214_Y + U214_H:.1f} mm", 12, "bold", colour="#166534"),
        t(note_x, 197, f"✓ battery holder occupies Y={PACK_HOLDER_Y:.1f}…{PACK_HOLDER_Y + PACK_HOLDER_H:.1f} mm", 12, "bold", colour="#166534"),
        t(note_x, 224, f"✓ the two envelopes have a {PACK_HOLDER_Y - U214_Y - U214_H:.1f}-mm plan gap", 12, "bold", colour="#166534"),
        t(note_x, 251, "✓ 84-mm Cap overhang is symmetric: 4.5 mm per side", 12, "bold", colour="#166534"),
        t(note_x, 278, "✓ 56-mm retention pitch remains inside the 75-mm base", 12, "bold", colour="#166534"),
        t(note_x, 305, "✓ direct buttons and exact knob clear the battery and U214", 12, "bold", colour="#166534"),
        t(note_x, 350, "Selected parts", 15, "bold"),
        t(note_x, 378, cap_mpn, 11, "bold", colour="#9a3412"),
        t(note_x, 403, f"{socket_mpn} · vertical 2×7 host socket", 11, "bold", colour="#075985"),
        t(note_x, 428, f"{holder_mpn} · rotated holder", 11, "bold", colour="#166534"),
        t(note_x, 474, "Rear controls shown to scale", 15, "bold"),
        t(note_x, 502, "OMRON B3S-1100P · direct BACK/OPT/F1…F8/PTT", 11),
        t(note_x, 527, "C&K JS102011SCQN · side-facing RUN/KILL", 11),
        t(note_x, 552, "Alps EC11E18244AU + Davies 1227-J · exact encoder and knob", 11),
        t(note_x, 598, "Meaning of this view", 15, "bold"),
        t(note_x, 626, "Rear face viewed normal to the PCB — not a side section.", 11),
        t(note_x, 651, "Solid: exact bodies/direct buttons/knob; RUN/KILL is visible in the side view.", 11),
        t(note_x, 676, "Orange: removable Cap/controls; blue: raised rail; green: batteries.", 11),
        t(note_x, 716, "Still requires specimen/HIL", 15, "bold", colour="#b42318"),
        t(note_x, 744, "• RUN/KILL side access, legends, sealing and encoder access", 11),
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
    holder_y = top + PACK_HOLDER_Y * plan_scale
    holder_h = PACK_HOLDER_H * plan_scale
    cells_y = top + PACK_CELL_Y * plan_scale
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
        f'<g id="battery-zone" data-plan-y-mm="{PACK_HOLDER_Y:.1f}..{PACK_HOLDER_Y + PACK_HOLDER_H:.1f}">',
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
        f'<g id="u214-zone" data-plan-y-mm="{U214_Y:.1f}..{U214_Y + U214_H:.1f}">',
        r(x_rear_outer, u214_y, u214_z, u214_h, "#ffedd5", "#ea580c", rx=5),
        r(x_rear_outer, connector_y, u214_connector_z, connector_h, "#e0f2fe", "#0369a1", rx=2),
        '</g>',
        t(x_display + display_z/2, top + height/2, "HMX035CTFT-001", 10, "bold", "middle", "#1d4ed8"),
        t(x_display + display_z/2, top + height/2 + 17, f"{depth('display'):.1f} mm", 9, anchor="middle", colour="#1d4ed8"),
        t(x_ui + pcb_z/2, top + height + 24, "UI/control PCB · 1.6 mm", 10, "bold", "middle", "#166534"),
        t(x_rf + pcb_z/2, top + height + 44, "RF/power PCB · 1.6 mm", 10, "bold", "middle", "#c2410c"),
        t(x_holder + holder_installed_z/2, holder_y + holder_h/2 - 8, "1048P + 2× 18650", 10, "bold", "middle", "#166534"),
        t(x_holder + holder_installed_z/2, holder_y + holder_h/2 + 10, "installed depth 20.7 mm", 8.5, anchor="middle", colour="#166534"),
        t(x_shell_rear + shell + 6, holder_y + holder_h - 7, "open rear frame — no battery lid", 8.5, "bold", colour="#166534"),
        t(x_rear_outer + u214_z - 5, u214_y + u214_h/2 + 4, "stock U214 worst-case · 15.287 mm", 8.5, "bold", "end", "#9a3412"),
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
        t(note_x, 418, "↑ top: ten separately labelled antenna ports", 11),
        t(note_x, 444, "bottom/sides: USB, microSD, downward microphone, headphones and M5 Unit", 11),
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

    def service_motion(x, front_y, rear_y, label):
        """Draw explicit rear-service insertion and removal trajectories."""
        return [
            f'<line x1="{x-5:.1f}" y1="{rear_y:.1f}" x2="{x-5:.1f}" y2="{front_y:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>',
            f'<line x1="{x+5:.1f}" y1="{front_y:.1f}" x2="{x+5:.1f}" y2="{rear_y:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>',
            t(x-12, (front_y+rear_y)/2, f"{label} · INSERT ↑ / REMOVE ↓", 7.8, "bold", "middle", "#b42318").replace(
                '<text ', f'<text transform="rotate(-90 {x-12:.1f} {((front_y+rear_y)/2):.1f})" ', 1
            ),
        ]

    # Both axes use the same millimetre scale: these are physical sections,
    # not an illustrative stack diagram.  Keeping X and Z equal also makes a
    # cylindrical 18650 appear circular in the antenna-edge view.
    x_scale = 7.5
    z_scale = 7.5
    drawing_top = 155.0
    pcb_front_z = depth("display")
    ui_rear_z = pcb_front_z + 1.6
    rf_front_z = ui_rear_z + 11.0
    base_rear_z = rf_front_z + 1.6
    holder_depth = float(devices[instances["pack_holder"]]["installed_envelope_mm"][2])
    battery_rear_z = base_rear_z + holder_depth
    cap_rear_z = base_rear_z + depth("u214")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="820" viewBox="0 0 1500 820" data-view="true-sections" data-x-scale-px-per-mm="{x_scale:.1f}" data-z-scale-px-per-mm="{z_scale:.1f}">',
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
            t(px(37.5), pz(2.15), "HMX035CTFT-001", 8.0, "bold", "middle", "#1d4ed8"),
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
                t(px(37.5), pz(base_rear_z+4.7), "Samtec HLE-107-02-G-DV-PE-LC · pass-through host socket", 7.2, "bold", "middle", "#075985"),
                t(px(37.5), pz(base_rear_z+12.4), "M5Stack U214 worst-case · 84 × 24 × 15.287 mm", 9.2, "bold", "middle", "#9a3412"),
                t(px(37.5), pz(cap_rear_z)+24, f"No battery appears: its Y={PACK_HOLDER_Y:.1f}…{PACK_HOLDER_Y + PACK_HOLDER_H:.1f}-mm zone does not cross A–A.", 9.3, "bold", "middle", "#166534"),
                *service_motion(px(72.0), pz(base_rear_z)+8, pz(cap_rear_z)-8, "CAP"),
                '</g>',
            ]
            rear_z = cap_rear_z
            rear_label = f"base + U214 = {rear_z:.3f} mm"
        else:
            holder_x = 17.6
            holder_w = 39.8
            parts += [
                f'<g id="section-battery" data-cut-y-mm="{cut_y:.0f}" data-contains="battery-no-u214">',
                r(px(holder_x), pz(base_rear_z), holder_w*x_scale, holder_depth*z_scale, "#dcfce7", "#16a34a", rx=12, extra=' data-instance="pack-holder"'),
                r(px(18.7), pz(base_rear_z+1.05), 18.6*x_scale, 18.6*z_scale, "#ecfdf3", "#22c55e", rx=16, extra=' data-instance="cell-left"'),
                r(px(37.7), pz(base_rear_z+1.05), 18.6*x_scale, 18.6*z_scale, "#ecfdf3", "#22c55e", rx=16, extra=' data-instance="cell-right"'),
                t(px(37.5), pz(base_rear_z+10.8), "Keystone Electronics 1048P + 2× 18650", 9.2, "bold", "middle", "#166534"),
                t(px(37.5), pz(battery_rear_z)+24, f"No installed Cap appears: its Y={U214_Y:.1f}…{U214_Y + U214_H:.1f}-mm zone does not cross B–B.", 9.3, "bold", "middle", "#9a3412"),
                *service_motion(px(10.0), pz(base_rear_z)+8, pz(battery_rear_z)-8, "CELLS"),
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
                t(px(37.5), pz(rear_z)+81, "installed U214 worst-case · 84 mm · 4.5-mm overhang per side", 9.2, "bold", "middle", "#9a3412"),
            ]
        return parts

    out += panel(60, "A–A · Cap-Bus dock · stock U214 worst-case", 29.0, "u214")
    out += panel(800, "B–B · battery/control zone", 82.0, "battery")
    out += [
        line(780, 105, 780, 750, "#d0d5dd", "6 5"),
        t(60, 750, f"Display: {mpn('display')} · {depth('display'):.1f}-mm LCD/CTP body", 10.5, "bold"),
        t(60, 774, f"Complete opposing-body Z clearance—including {mpn('speaker')}—is audited in the inner-face view.", 10.5, colour="#526076"),
        t(800, 750, "The sections exclude enclosure walls, solder and manufacturing tolerances.", 10.5, "bold", colour="#b42318"),
        t(800, 774, "Dimensioned architecture projection — not a production enclosure drawing.", 10.5, colour="#526076"),
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

    # A true orthographic view must preserve physical proportions.
    scale_x = 8.0
    scale_z = 8.0
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
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="720" viewBox="0 0 1400 720" data-view="top-edge" data-look-direction="antenna-edge-to-bottom" data-rf-mounting="opposed-outer-faces" data-x-scale-px-per-mm="{scale_x:.1f}" data-z-scale-px-per-mm="{scale_z:.1f}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 36, "Leshy2 — true top view from the antenna edge", 23, "bold"),
        t(30, 62, "Looking along board +Y. Horizontal is board X; vertical is front-to-rear depth Z.", 11, "bold", colour="#b42318"),
        t(30, 84, "Board Y is collapsed in this orthographic projection; the rear view separately proves Cap/battery longitudinal clearance.", 11, colour="#526076"),
        t(x(-4.5)-24, z(0)+5, "FRONT", 9, "bold", "end", "#1d4ed8"),
        t(x(-4.5)-24, z(base_rear_z)+5, "REAR", 9, "bold", "end", "#166534"),
        r(x(10.25), z(0), 54.5*scale_x, depth("display")*scale_z, "#dbeafe", "#2563eb", rx=4, extra=' data-instance="display"'),
        r(x(0), z(ui_outer_z), BOARD_W*scale_x, 1.6*scale_z, "#dcfce7", "#16a34a", rx=1, extra=' data-instance="ui-pcb"'),
        r(x(0), z(ui_inner_z), BOARD_W*scale_x, 11.0*scale_z, "#f8fafc", "#94a3b8", "5 4", 1, ' data-board-gap-mm="11" data-antenna-bodies="none"'),
        r(x(0), z(rf_inner_z), BOARD_W*scale_x, 1.6*scale_z, "#ffedd5", "#ea580c", rx=1, extra=' data-instance="rf-pcb"'),
        t(x(37.5), z(ui_inner_z + 5.5), "FX8C M1 · 11-mm board gap", 8.5, "bold", "middle", "#9d174d"),
        '<g id="top-edge-rear-envelopes" data-y-collapsed="true">',
        r(x(U214_X), z(base_rear_z), U214_W*scale_x, depth("u214")*scale_z, "#ffedd5", "#ea580c", "7 4", 5, ' fill-opacity="0.45" data-instance="u214"'),
        r(x(17.6), z(base_rear_z), 39.8*scale_x, holder_depth*scale_z, "#dcfce7", "#16a34a", "4 3", 12, ' fill-opacity="0.45" data-instance="pack-holder"'),
        '</g>',
        f'<g id="front-antenna-bank" data-count="{len(FRONT_RF)}" data-mount-face="ui-pcb-outer">',
    ]
    for centre, path, _ in FRONT_RF:
        out.append(f'<ellipse cx="{x(centre):.1f}" cy="{z(front_rf_centre_z):.1f}" rx="{RF_BARREL_D*scale_x/2:.1f}" ry="{RF_BARREL_D*scale_z/2:.1f}" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5" data-path="{path}"/>')
    out += ['</g>', f'<g id="rear-antenna-bank" data-count="{len(REAR_RF)}" data-mount-face="rf-pcb-outer">']
    for centre, path, _ in REAR_RF:
        out.append(f'<ellipse cx="{x(centre):.1f}" cy="{z(rear_rf_centre_z):.1f}" rx="{RF_BARREL_D*scale_x/2:.1f}" ry="{RF_BARREL_D*scale_z/2:.1f}" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5" data-path="{path}"/>')
    out += [
        '</g>',
        t(790, z(front_rf_centre_z)-2, f"{len(FRONT_RF)} front ports", 9, "bold", "start", "#1d4ed8"),
        t(790, z(front_rf_centre_z)+11, "UI outer face", 8.5, "normal", "start", "#1d4ed8"),
        t(790, z(rear_rf_centre_z)-5, f"{len(REAR_RF)} rear SMA", 8.5, "bold", "start", "#9a3412"),
        t(790, z(rear_rf_centre_z)+7, "+ 1 FPV MMCX", 8.5, "bold", "start", "#9a3412"),
        t(790, z(rear_rf_centre_z)+19, "RF/power outer face", 8.0, "normal", "start", "#9a3412"),
        f'<line x1="{x(0):.1f}" y1="{z(max_rear_z)+58:.1f}" x2="{x(75):.1f}" y2="{z(max_rear_z)+58:.1f}" stroke="#344054"/>',
        f'<line x1="{x(0):.1f}" y1="{z(max_rear_z)+52:.1f}" x2="{x(0):.1f}" y2="{z(max_rear_z)+64:.1f}" stroke="#344054"/>',
        f'<line x1="{x(75):.1f}" y1="{z(max_rear_z)+52:.1f}" x2="{x(75):.1f}" y2="{z(max_rear_z)+64:.1f}" stroke="#344054"/>',
        t(x(37.5), z(max_rear_z)+50, "base PCB · 75 mm", 10, "bold", "middle", "#344054"),
        f'<line x1="{x(U214_X):.1f}" y1="{z(max_rear_z)+88:.1f}" x2="{x(U214_X+U214_W):.1f}" y2="{z(max_rear_z)+88:.1f}" stroke="#344054"/>',
        f'<line x1="{x(U214_X):.1f}" y1="{z(max_rear_z)+82:.1f}" x2="{x(U214_X):.1f}" y2="{z(max_rear_z)+94:.1f}" stroke="#344054"/>',
        f'<line x1="{x(U214_X+U214_W):.1f}" y1="{z(max_rear_z)+82:.1f}" x2="{x(U214_X+U214_W):.1f}" y2="{z(max_rear_z)+94:.1f}" stroke="#344054"/>',
        t(x(37.5), z(max_rear_z)+80, "installed U214 worst-case · symmetric 4.5-mm side overhang", 9.5, "bold", "middle", "#9a3412"),
        t(920, 150, "What this view proves", 16, "bold"),
        t(920, 184, "✓ 84-mm Cap overhang is 4.5 mm on each side", 11, "bold", colour="#166534"),
        t(920, 212, "✓ both antenna banks mount on opposed outward PCB faces", 11, "bold", colour="#166534"),
        t(920, 240, "✓ the exact 11-mm interboard channel contains no antenna body", 11, "bold", colour="#166534"),
        t(920, 268, f"✓ antenna centre planes are separated by {rf_centre_spacing:.2f} mm", 11, "bold", colour="#166534"),
        t(920, 316, "Projection limits", 16, "bold"),
        t(920, 350, "Display/front-bank and installed-Cap/battery overlaps are Y-collapse artifacts.", 11),
        t(920, 378, "Use the adjacent external views for their real longitudinal positions.", 11),
        t(920, 420, "Y-collapsed rear envelopes", 15, "bold"),
        t(920, 450, f"orange dashed — U214 · 84 mm · Y={U214_Y:.1f}…{U214_Y + U214_H:.1f}", 10, colour="#9a3412"),
        t(920, 476, f"green dashed — 1048P + cells · 39.8 mm · Y={PACK_HOLDER_Y:.1f}…{PACK_HOLDER_Y + PACK_HOLDER_H:.1f}", 10, colour="#166534"),
        t(920, 516, "Selected Z envelopes", 15, "bold"),
        t(920, 546, f"{mpn('u214')} · {depth('u214'):.3f} mm", 10),
        t(920, 570, f"{mpn('pack_holder')} · {holder_depth:.1f} mm installed", 10),
        t(920, 594, f"{mpn('display')} · {depth('display'):.1f} mm", 10),
        t(920, 630, f"Nominal maximum selected-part depth: {max_rear_z:.1f} mm", 10.5, "bold", colour="#b42318"),
        t(920, 654, "Excludes enclosure walls, solder and manufacturing tolerances.", 10, colour="#526076"),
        t(30, 690, "Dimensioned architecture projection — not a production enclosure drawing.", 10.5, "bold", colour="#b42318"),
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_navigation_cluster(design, devices, instances):
    """Render the exact five-series-button navigation cluster and neighbours."""
    scale = 8.0
    ox, oy = 50.0, 105.0
    band_y = 112.0

    def x(value):
        return ox + float(value) * scale

    def y(value):
        return oy + (float(value) - band_y) * scale

    def t(px, py, value, size=12, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{px:.1f}" y="{py:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(value)}</text>'
        )

    labels = {
        "ui_dpad_up": "▲",
        "ui_dpad_down": "▼",
        "ui_dpad_left": "◀",
        "ui_dpad_right": "▶",
        "ui_dpad_ok": "OK",
        "ui_switch_back": "BACK",
        "ui_switch_opt": "OPT",
    }
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1250" height="560" viewBox="0 0 1250 560" data-view="series-navigation-cluster" data-design-id="L2-NAV-5B-001-A" data-manufacturing-class="serial-components-only">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        t(30, 34, "Leshy2 — five-series-button navigation cluster", 22, "bold"),
        t(30, 60, "Every control is an orderable OMRON B3S-1100P; there is no custom cross, cap, plunger or guide.", 11, colour="#526076"),
        f'<rect x="{x(0):.1f}" y="{y(112):.1f}" width="{75*scale:.1f}" height="{38*scale:.1f}" rx="6" fill="#f8fafc" stroke="#344054" stroke-width="1.5" data-board-band-mm="75x38"/>',
        t(x(37.5), y(115.5), "front UI PCB · y=112…150 mm", 10, "bold", "middle", "#526076"),
    ]
    for hx, hy in HOLES:
        if hy < band_y:
            continue
        out.append(
            f'<circle cx="{x(hx):.1f}" cy="{y(hy):.1f}" r="{MOUNT_KEEPOUT_R*scale:.1f}" '
            'fill="#fff7ed" stroke="#fb923c" stroke-dasharray="5 3"/>'
        )
        out.append(
            f'<circle cx="{x(hx):.1f}" cy="{y(hy):.1f}" r="{MOUNT_HOLE_D*scale/2:.1f}" '
            'fill="#ffffff" stroke="#475467"/>'
        )
    for item in BOTTOM_NAV_CONTROLS:
        width, height = placement_size(item, devices, instances)
        is_navigation = item.instance.startswith("ui_dpad_")
        out.append(
            f'<rect x="{x(item.x):.1f}" y="{y(item.y):.1f}" width="{width*scale:.1f}" '
            f'height="{height*scale:.1f}" rx="3" fill="{"#ede9fe" if is_navigation else "#e2e8f0"}" '
            f'stroke="{"#7c3aed" if is_navigation else "#64748b"}" stroke-width="1.5" '
            f'data-instance="{item.instance}" data-mpn="OMRON B3S-1100P" data-direct-press="true"/>'
        )
        out.append(
            t(
                x(item.x + width / 2), y(item.y + height / 2) + 4,
                labels[item.instance], 9, "bold", "middle", "#4c1d95",
            )
        )
    cluster = design["layout"]
    bbox_x, bbox_y, bbox_w, bbox_h = map(float, cluster["bounding_box_mm"])
    out.append(
        f'<rect x="{x(bbox_x):.1f}" y="{y(bbox_y):.1f}" width="{bbox_w*scale:.1f}" '
        f'height="{bbox_h*scale:.1f}" fill="none" stroke="#7c3aed" stroke-width="1.4" '
        'stroke-dasharray="6 4" data-cluster-envelope="true"/>'
    )
    note_x = 700
    cost = design["cost_at_quantity_100_usd"]
    out += [
        t(note_x, 112, "Five exact series buttons", 16, "bold"),
        t(note_x, 143, "5× OMRON B3S-1100P · direct finger press", 12, "bold"),
        t(note_x, 169, "UP · DOWN · LEFT · RIGHT · OK", 11),
        t(note_x, 195, "Each body: 6.6×6.0×4.3 mm · SPST-NO · IEC IP67-equivalent", 11),
        t(note_x, 221, "Five independent active-low TCA9539 inputs; pin budget unchanged.", 11),
        t(note_x, 263, "Mechanical result", 16, "bold"),
        t(note_x, 294, f"Cluster envelope: {bbox_w:.1f}×{bbox_h:.1f} mm", 11),
        t(note_x, 320, f"Button-centre pitch: {cluster['centre_pitch_mm']:.1f} mm", 11),
        t(note_x, 346, f"BACK/OPT clearance: {design['paper_checks']['back_clearance_mm']:.1f} mm each", 11),
        t(note_x, 372, f"Bottom PCB margin: {design['paper_checks']['bottom_board_margin_mm']:.1f} mm", 11),
        t(note_x, 414, "Quantity-100 component cost", 16, "bold"),
        t(note_x, 445, f"Five selected buttons: ${cost['five_b3s_1100p']:.4f} per device", 11),
        t(note_x, 471, "PCB, assembly, enclosure, freight and tax excluded", 11, colour="#526076"),
        t(30, 530, "Dimensioned component placement; enclosure opening feel and endurance remain H5 checks.", 10.5, "bold", colour="#b42318"),
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def render_display_adapter(design):
    """Render the fixed main-board mate and replaceable display-tail adapter."""
    board = design["board"]
    components = {row["instance"]: row for row in design["components"]}
    scale = 14.0
    ox, oy = 130.0, 135.0
    bw = float(board["width_mm"]) * scale
    bh = float(board["height_mm"]) * scale

    def tx(value: float) -> float:
        return ox + value * scale

    def ty(value: float) -> float:
        return oy + value * scale

    def label(x, y, value, size=11, weight="normal", anchor="start", colour="#172033"):
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{colour}">{html.escape(str(value))}</text>'
        )

    def component_box(row, fill, stroke):
        x, y = map(float, row["adapter_position_mm"])
        w, h, _ = map(float, row["envelope_mm"])
        return (
            f'<rect x="{tx(x):.1f}" y="{ty(y):.1f}" width="{w*scale:.1f}" height="{h*scale:.1f}" '
            f'rx="3" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )

    plug = components["display_adapter_plug"]
    panel = components["display_panel_connector"]
    stack = design["stack"]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        label(40, 42, "Leshy2 — replaceable 40-to-40 display adapter", 22, "bold"),
        label(40, 68, "L2-DISP-ADP-001-A · exact connector bodies and one-to-one electrical map", 11, colour="#526076"),
        label(ox, 112, "Panel-facing adapter side · millimetre scale", 14, "bold", colour="#1d4ed8"),
        f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="#f8fafc" stroke="#344054" stroke-width="2"/>',
        component_box(panel, "#dbeafe", "#2563eb"),
        component_box(plug, "#ede9fe", "#7c3aed"),
        label(tx(12.75), ty(2.9), "FH34SRJ-40S-0.5SH(99)", 9.5, "bold", "middle", "#1d4ed8"),
        label(tx(12.75), ty(7.65), "DF40C-40DP-0.4V(51) · underside", 8.5, "bold", "middle", "#6d28d9"),
        f'<path d="M{tx(1.75):.1f} {ty(2.7):.1f} L{tx(-2.5):.1f} {ty(2.7):.1f}" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>',
        label(tx(-2.9), ty(2.25), "DISPLAY FPC", 8.8, "bold", "end", "#b42318"),
        label(ox + bw/2, oy + bh + 26, "25.5 × 12.0 × 0.8 mm adapter PCB", 11, "bold", "middle"),
        label(545, 112, "Front-to-rear stack", 14, "bold", colour="#166534"),
    ]

    sx0 = 555.0
    base_y = 325.0
    z_scale = 38.0
    main_h = 1.95 * z_scale
    mate_h = float(stack["df40_mated_height_mm"]) * z_scale
    pcb_h = float(board["thickness_mm"]) * z_scale
    panel_h = float(stack["panel_connector_height_mm"]) * z_scale
    out += [
        f'<rect x="{sx0:.1f}" y="{base_y:.1f}" width="235" height="18" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>',
        label(sx0 + 245, base_y + 13, "UI/control PCB", 10, "bold"),
        f'<rect x="{sx0+55:.1f}" y="{base_y-main_h:.1f}" width="125" height="{main_h:.1f}" fill="#e0e7ff" stroke="#4338ca" stroke-width="2"/>',
        label(sx0 + 117.5, base_y-main_h/2+4, "DF40C(2.0)-40DS-0.4V(58)", 8.5, "bold", "middle"),
        f'<rect x="{sx0+62:.1f}" y="{base_y-mate_h:.1f}" width="111" height="{1.14*z_scale:.1f}" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>',
        f'<rect x="{sx0+15:.1f}" y="{base_y-mate_h-pcb_h:.1f}" width="205" height="{pcb_h:.1f}" fill="#fff7ed" stroke="#ea580c" stroke-width="2"/>',
        label(sx0 + 230, base_y-mate_h-pcb_h/2+4, "0.8-mm adapter", 10, "bold"),
        f'<rect x="{sx0+25:.1f}" y="{base_y-mate_h-pcb_h-panel_h:.1f}" width="185" height="{panel_h:.1f}" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>',
        label(sx0 + 117.5, base_y-mate_h-pcb_h-panel_h/2+4, "FH34SRJ-40S-0.5SH(99)", 8.8, "bold", "middle"),
        label(555, 390, f"Selected height to panel-connector top: {stack['ui_board_to_panel_connector_top_mm']:.1f} mm", 11, "bold"),
        label(555, 413, f"Available inner gap: {stack['available_interboard_gap_mm']:.1f} mm", 11),
        label(555, 455, "Electrical contract", 14, "bold"),
        label(555, 480, "UI PIN_n ↔ adapter PIN_n ↔ panel PIN_n, n = 1…40", 11, "bold", colour="#166534"),
        label(555, 503, "No active device and no pin remapping on the adapter.", 10.5),
        label(555, 526, "Dual-contact ZIF removes exposed-contact-side dependence.", 10.5),
        label(555, 549, "Tail thickness/outline remains a received-display H5 fit check.", 10.5, "bold", colour="#b42318"),
        label(40, 590, "H1 result", 14, "bold", colour="#166534"),
        label(140, 590, "main UI PCB bay, exact DF40 mate and 40-contact mapping are fixed without buying a display", 11, "bold", colour="#166534"),
        label(40, 620, "H5 boundary", 14, "bold", colour="#b42318"),
        label(140, 620, "a received tail may revise only this small adapter and its panel-side connector", 11, colour="#b42318"),
        '</svg>',
    ]
    return "\n".join(out) + "\n"


def build_physical_source_table(devices: dict, instances: dict) -> dict:
    """Freeze the exact H1.1.4 source row used by every mechanical projection."""
    contracts, errors = mechanical_body_contracts()
    if errors:
        raise ValueError("; ".join(errors))
    placements = {
        item.instance: item
        for _, items in PLACEMENT_PROJECTION_GROUPS
        for item in items
    }
    cable_routes = {route.instance: route for route in UI_RF_CABLES}
    cable_reserves = {reserve.instance: reserve for reserve in RF_NRF_CABLE_RESERVES}
    gates = json.loads(MECHANICAL_GATES_PATH.read_text(encoding="utf-8"))["gates"]
    gate_by_instance: dict[str, list[dict]] = {}
    for gate in gates:
        for instance in gate["affected_instances"]:
            gate_by_instance.setdefault(instance, []).append(
                {"id": gate["id"], "disposition": gate["disposition"]}
            )
    rows = []
    for instance, contract in sorted(contracts.items()):
        device_key = instances[instance]
        device = devices[device_key]
        source = device.get("mechanical_source", device.get("source", {}))
        dimensions = device.get("maximum_dimensions_mm", device.get("dimensions_mm"))
        row = {
            "instance": instance,
            "device_key": device_key,
            "mpn": device["mpn"],
            "role": (
                placements[instance].role
                if instance in placements
                else cable_routes[instance].role
                if instance in cable_routes
                else cable_reserves[instance].role
                if instance in cable_reserves
                else device.get("kind", "physical body")
            ),
            "frame": contract.frame,
            "frame_datum": MECHANICAL_PROJECTION_FRAMES[contract.frame],
            "rotation_deg": contract.rotation,
            "direction": contract.direction,
            "envelope_mm": dimensions[:3],
            "qualification": device["qualification"],
            "source": {
                field: source[field]
                for field in ("document", "version", "url", "checked")
                if field in source
            },
            "evidence_gates": gate_by_instance.get(instance, []),
        }
        if instance in placements:
            row["position_mm"] = [placements[instance].x, placements[instance].y]
        if instance in cable_routes:
            row["route_points_mm"] = [list(point) for point in cable_routes[instance].points]
        if instance in cable_reserves:
            reserve = cable_reserves[instance]
            module_box = nrf_cable_reserve_module_box(reserve, devices, instances)
            row["module_face_reserve_mm"] = {
                "x": [module_box[0], module_box[0] + module_box[2]],
                "y": [module_box[1], module_box[1] + module_box[3]],
            }
            row["escape_points_mm"] = [list(point) for point in reserve.escape_points]
            row["exact_axis_status"] = "H5 received-module evidence"
        if instance == "encoder":
            row["through_board_features"] = [
                {
                    "feature": feature.feature,
                    "plan_bbox_mm": [feature.x, feature.y, feature.w, feature.h],
                    "inner_projection_mm": feature.inner_height,
                }
                for feature in encoder_through_board_features(devices, instances)
            ]
        rows.append(row)
    return {
        "schema_version": 1,
        "stage": "H1.1.4",
        "status": "reviewed",
        "generated_from": [
            str(DEVICES_PATH.relative_to(REPO)),
            str(CANDIDATE_PATH.relative_to(REPO)),
            str(MECHANICAL_GATES_PATH.relative_to(REPO)),
            str(ASSEMBLY_COORDINATE_MODEL_PATH.relative_to(REPO)),
            str(Path(__file__).resolve().relative_to(REPO)),
        ],
        "policy": "Every mechanically rendered body has one exact instance, MPN or explicit TBD, sourced envelope, datum, orientation and interface direction.",
        "summary": {
            "rendered_physical_instances": len(rows),
            "exact_mpn_instances": sum("TBD" not in row["mpn"] for row in rows),
            "explicit_mpn_tbd_instances": sum("TBD" in row["mpn"] for row in rows),
            "h1_blockers": sum(gate["disposition"] == "h1_blocker" for gate in gates),
            "h5_received_sample_gates": sum(gate["disposition"] == "h5_received_sample_gate" for gate in gates),
        },
        "rows": rows,
    }


def build_unified_coordinate_table(
    source_table: dict,
    model: dict,
    devices: dict,
    instances: dict,
    display_adapter_design: dict,
) -> dict:
    """Resolve local view coordinates into the shared front-facing world datum."""
    stack = model["stack"]
    rows = []
    for source in source_table["rows"]:
        if "position_mm" not in source:
            continue
        x, y = map(float, source["position_mm"])
        width, height, body_z = map(float, source["envelope_mm"])
        angle = math.radians(int(source["rotation_deg"]) % 180)
        rotated_w = abs(width * math.cos(angle)) + abs(height * math.sin(angle))
        rotated_h = abs(width * math.sin(angle)) + abs(height * math.cos(angle))
        frame = source["frame"]
        if frame in {"front-outer", "ui-inner"}:
            world_x = x
        elif frame in {"rear-outer", "rf-inner"}:
            world_x = BOARD_W - x - rotated_w
        else:
            continue
        if frame == "front-outer":
            z_range = [float(stack["ui_outer_face_z"]) - body_z, float(stack["ui_outer_face_z"])]
        elif frame == "ui-inner":
            z_range = [float(stack["ui_inner_face_z"]), float(stack["ui_inner_face_z"]) + body_z]
        elif frame == "rf-inner":
            z_range = [float(stack["rf_inner_face_z"]) - body_z, float(stack["rf_inner_face_z"])]
        else:
            z_range = [float(stack["rf_outer_face_z"]), float(stack["rf_outer_face_z"]) + body_z]
        rows.append(
            {
                "instance": source["instance"],
                "source_frame": frame,
                "world_bbox_mm": {
                    "x": [round(world_x, 6), round(world_x + rotated_w, 6)],
                    "y": [round(y, 6), round(y + rotated_h, 6)],
                    "z": [round(z_range[0], 6), round(z_range[1], 6)],
                },
                "direction": source["direction"],
            }
        )
    individual_clearances = interboard_individual_clearances(devices, instances)
    opposing_pairs = interboard_clearance_pairs(devices, instances)
    cable_pairs = cable_interboard_clearance_pairs(devices, instances)
    nrf_reserve_pairs = nrf_cable_reserve_opposing_pairs(devices, instances)
    through_board_pairs = through_board_opposing_pairs(devices, instances)
    adapter_pairs = display_adapter_opposing_clearance_pairs(
        display_adapter_design, devices, instances
    )
    minimum_individual_clearance, tallest_item = individual_clearances[0]
    minimum_pair_clearance, minimum_ui, minimum_rf = opposing_pairs[0]
    minimum_cable_clearance, minimum_cable, minimum_cable_body = cable_pairs[0]
    minimum_nrf_reserve_clearance, minimum_nrf_reserve, minimum_nrf_reserve_body = (
        nrf_reserve_pairs[0]
    )
    minimum_through_clearance, minimum_through_feature, minimum_through_body = (
        through_board_pairs[0]
    )
    minimum_adapter_clearance, minimum_adapter_body = adapter_pairs[0]
    mate_instances = {
        instance
        for pair in INTENTIONAL_INTERBOARD_MATES
        for instance in pair
    }
    free_bodies = [
        (placement_height(item, devices, instances), item)
        for item in UI_INNER + RF_INNER
        if item.instance not in mate_instances
    ]
    tallest_free_height, tallest_free_item = max(
        free_bodies, key=lambda row: (row[0], row[1].instance)
    )
    ui_instances = {item.instance for item in UI_INNER}
    return {
        "schema_version": 1,
        "stage": "H1.2",
        "status": "reviewed",
        "model_id": model["model_id"],
        "world": model["world"],
        "stack": model["stack"],
        "mounting_holes": model["mounting_holes"],
        "antenna_planes": model["antenna_planes"],
        "longitudinal_zones": model["longitudinal_zones"],
        "accessory_envelopes": model["accessory_envelopes"],
        "enclosure_reference": model["enclosure_reference"],
        "interboard_fit_audit": {
            "result": "paper_geometry_passed",
            "interboard_gap_mm": INTERBOARD_GAP_MM,
            "minimum_required_clearance_mm": MIN_INTERBOARD_Z_CLEARANCE_MM,
            "inner_body_count": len(individual_clearances),
            "total_inner_component_count_including_adapter": len(individual_clearances) + 2,
            "all_inner_bodies_have_sourced_positive_height": True,
            "no_inner_body_exceeds_gap": minimum_individual_clearance >= 0,
            "no_inner_body_violates_minimum_clearance": (
                minimum_individual_clearance >= MIN_INTERBOARD_Z_CLEARANCE_MM
            ),
            "tallest_inner_body": {
                "instance": tallest_item.instance,
                "mpn": devices[instances[tallest_item.instance]]["mpn"],
                "height_mm": round(placement_height(tallest_item, devices, instances), 6),
                "remaining_to_opposite_pcb_plane_mm": round(minimum_individual_clearance, 6),
            },
            "tallest_non_mating_body": {
                "instance": tallest_free_item.instance,
                "mpn": devices[instances[tallest_free_item.instance]]["mpn"],
                "height_mm": round(tallest_free_height, 6),
                "remaining_to_opposite_pcb_plane_mm": round(
                    INTERBOARD_GAP_MM - tallest_free_height, 6
                ),
            },
            "individual_body_clearances": [
                {
                    "instance": item.instance,
                    "frame": "ui-inner" if item.instance in ui_instances else "rf-inner",
                    "mpn": devices[instances[item.instance]]["mpn"],
                    "height_mm": round(placement_height(item, devices, instances), 6),
                    "remaining_to_opposite_pcb_plane_mm": round(clearance, 6),
                }
                for clearance, item in individual_clearances
            ],
            "opposing_non_mating_pair_count": len(opposing_pairs),
            "minimum_opposing_pair": {
                "ui_instance": minimum_ui.instance,
                "rf_instance": minimum_rf.instance,
                "remaining_z_clearance_mm": round(minimum_pair_clearance, 6),
            },
            "opposing_non_mating_pairs": [
                {
                    "ui_instance": ui_item.instance,
                    "rf_instance": rf_item.instance,
                    "ui_height_mm": round(placement_height(ui_item, devices, instances), 6),
                    "rf_height_mm": round(placement_height(rf_item, devices, instances), 6),
                    "remaining_z_clearance_mm": round(clearance, 6),
                }
                for clearance, ui_item, rf_item in opposing_pairs
            ],
            "display_adapter_assembly": {
                "component_instances": [
                    "display_adapter_plug",
                    "display_panel_connector",
                ],
                "board_envelope_mm": [
                    float(display_adapter_design["board"]["width_mm"]),
                    float(display_adapter_design["board"]["height_mm"]),
                    float(display_adapter_design["board"]["thickness_mm"]),
                ],
                "complete_height_from_ui_inner_mm": float(
                    display_adapter_design["stack"]["ui_board_to_panel_connector_top_mm"]
                ),
                "remaining_to_opposite_pcb_plane_mm": round(
                    INTERBOARD_GAP_MM
                    - float(display_adapter_design["stack"]["ui_board_to_panel_connector_top_mm"]),
                    6,
                ),
                "opposing_pair_count": len(adapter_pairs),
                "minimum_opposing_body": minimum_adapter_body.instance,
                "minimum_opposing_z_clearance_mm": round(minimum_adapter_clearance, 6),
                "opposing_pairs": [
                    {
                        "rf_instance": rf_item.instance,
                        "rf_height_mm": round(placement_height(rf_item, devices, instances), 6),
                        "remaining_z_clearance_mm": round(clearance, 6),
                    }
                    for clearance, rf_item in adapter_pairs
                ],
            },
            "intentional_mate": {
                "ui_instance": "m1_ui_plug",
                "rf_instance": "m1_rf_receptacle",
                "mpns": [
                    devices[instances["m1_ui_plug"]]["mpn"],
                    devices[instances["m1_rf_receptacle"]]["mpn"],
                ],
                "mated_height_mm": INTERBOARD_GAP_MM,
            },
            "native_rf_cable_direct_projection_opposing_body_crossings": len(cable_pairs),
            "minimum_native_rf_cable_direct_projection_crossing": {
                "cable_instance": minimum_cable.instance,
                "rf_instance": minimum_cable_body.instance,
                "remaining_z_clearance_mm": round(minimum_cable_clearance, 6),
            },
            "native_rf_cable_direct_projection_crossings": [
                {
                    "cable_instance": cable.instance,
                    "rf_instance": rf_item.instance,
                    "remaining_z_clearance_mm": round(clearance, 6),
                }
                for clearance, cable, rf_item in cable_pairs
            ],
            "remaining_gate": "Final PCB, assembly and enclosure tolerance stack plus assembled HIL remain required before production release.",
        },
        "physical_interconnect_clearance_audit": {
            "result": "paper_keepouts_passed_final_ecad_and_h5_open",
            "scope": "Every physical item entering or occupying the 11-mm interboard channel; PCB copper is intentionally a later ECAD/DRC proof.",
            "m1_interboard_connector": {
                "contact_count": 80,
                "intentional_mated_height_mm": INTERBOARD_GAP_MM,
                "same_face_body_keepouts_passed": True,
                "opposing_body_treatment": "one intentional exact mate",
            },
            "rf_microcoax": {
                "direct_endpoint_projection_count": len(UI_RF_CABLES),
                "conservative_nrf_module_face_reserve_count": len(RF_NRF_CABLE_RESERVES),
                "all_five_feed_assemblies_accounted": (
                    len(UI_RF_CABLES) + len(RF_NRF_CABLE_RESERVES) == 5
                ),
                "exact_jumper_mpn": devices[instances["s3_rf_jumper"]]["mpn"],
                "same_face_keepouts_passed": True,
                "direct_projection_opposing_crossing_count": len(cable_pairs),
                "minimum_direct_projection_opposing_z_clearance_mm": round(
                    minimum_cable_clearance, 6
                ),
                "native_direct_projections": [
                    {
                        "cable_instance": route.instance,
                        "points_mm": [list(point) for point in route.points],
                        "projected_chord_mm": round(polyline_length(route.points), 6),
                        "assembly_length_mm": float(
                            devices[instances[route.instance]]["electrical_contract"][
                                "cable_length_mm"
                            ]
                        ),
                        "unprojected_3d_slack_mm": round(
                            float(
                                devices[instances[route.instance]]["electrical_contract"][
                                    "cable_length_mm"
                                ]
                            )
                            - polyline_length(route.points),
                            6,
                        ),
                    }
                    for route in UI_RF_CABLES
                ],
                "native_slack_bend_and_retention_status": "H5_open",
                "nrf_reserve_opposing_crossing_count": len(nrf_reserve_pairs),
                "minimum_nrf_reserve_opposing_crossing": {
                    "cable_instance": minimum_nrf_reserve.instance,
                    "ui_instance": minimum_nrf_reserve_body.instance,
                    "remaining_z_clearance_mm": round(minimum_nrf_reserve_clearance, 6),
                },
                "nrf_reserves": [
                    {
                        "cable_instance": reserve.instance,
                        "module_instance": reserve.module_instance,
                        "board_connector_instance": reserve.board_connector_instance,
                        "module_face_reserve_mm": [
                            round(value, 6)
                            for value in nrf_cable_reserve_module_box(
                                reserve, devices, instances
                            )
                        ],
                        "direct_projection_points_mm": [list(point) for point in reserve.escape_points],
                        "projected_chord_mm": round(polyline_length(reserve.escape_points), 6),
                        "unprojected_3d_slack_mm": round(
                            float(
                                devices[instances[reserve.instance]]["electrical_contract"][
                                    "cable_length_mm"
                                ]
                            )
                            - polyline_length(reserve.escape_points),
                            6,
                        ),
                        "axis_status": "H5 received-module evidence",
                    }
                    for reserve in RF_NRF_CABLE_RESERVES
                ],
                "native_feed_chain_after_green_cable": [
                    {
                        "owner": owner,
                        "module_mpn": devices[instances[owner]]["mpn"],
                        "green_cable_mpn": devices[instances[f"{owner}_rf_jumper"]]["mpn"],
                        "green_cable_ends_at": devices[
                            instances[f"{owner}_rf_board_connector"]
                        ]["mpn"],
                        "then_medium": "controlled_50_ohm_pcb_mainline_final_route_open_in_kicad",
                        "forward_coupler_mpn": devices[
                            instances[f"{owner}_rf_coupler"]
                        ]["mpn"],
                        "user_antenna_connector_mpn": devices[
                            instances[f"{owner}_external_rp_sma"]
                        ]["mpn"],
                    }
                    for owner in ("s3", "c5")
                ],
            },
            "antenna_source_to_port_topology": {
                "result": "all_ten_onboard_paths_accounted_topology_only",
                "guide_count": len(ANTENNA_TOPOLOGY_GUIDES),
                "final_copper_status": "open_until_kicad_drc",
                "rendered_medium_boundaries": {
                    "module_integrated_connector_instances": [
                        "s3_integrated_ufl",
                        "c5_integrated_ufl",
                        "nrf0_integrated_ipex",
                        "nrf1_integrated_ipex",
                        "nrf2_integrated_ipex",
                    ],
                    "module_integrated_connector_count": 5,
                    "exact_module_integrated_connector_count": 2,
                    "schematic_position_module_integrated_connector_count": 3,
                    "physical_cable_medium": "solid_removable_microcoax",
                    "cable_to_pcb_handoff_instances": sorted(
                        BOARD_RF_CABLE_TO_TRACE_HANDOFFS
                    ),
                    "cable_to_pcb_handoff_count": len(
                        BOARD_RF_CABLE_TO_TRACE_HANDOFFS
                    ),
                    "pcb_guide_medium": "dashed_controlled_50_ohm_topology_only",
                    "nrf_module_connector_axis": "rendered_schematically_exact_axis_H5_open",
                },
                "guides": [
                    {
                        "path": guide.path,
                        "frame": guide.frame,
                        "radio_source_instance": RF_SOURCE_INSTANCE_BY_PATH[guide.path],
                        "radio_source_mpn": devices[
                            instances[RF_SOURCE_INSTANCE_BY_PATH[guide.path]]
                        ]["mpn"],
                        "guide_start_instance": guide.source_instance,
                        "external_connector_instance": guide.external_instance,
                        "external_connector_mpn": devices[
                            instances[guide.external_instance]
                        ]["mpn"],
                        "points_mm": [list(point) for point in guide.points],
                        "meaning": guide.role,
                    }
                    for guide in ANTENNA_TOPOLOGY_GUIDES
                ],
            },
            "display_bus": {
                "main_board_and_adapter_stack_result": "paper_geometry_passed",
                "complete_adapter_height_mm": float(
                    display_adapter_design["stack"]["ui_board_to_panel_connector_top_mm"]
                ),
                "minimum_opposing_z_clearance_mm": round(minimum_adapter_clearance, 6),
                "received_panel_tail_result": "H5_open",
                "open_evidence": "current-lot FPC outline, stiffener, thickness and bend path",
            },
            "outer_face_through_board_features": {
                "encoder_feature_count": len(
                    encoder_through_board_features(devices, instances)
                ),
                "encoder_inner_projection_mm": float(
                    devices[instances["encoder"]]["mechanical_contract"][
                        "inner_terminal_projection_mm"
                    ]
                ),
                "encoder_same_face_keepouts_passed": True,
                "encoder_opposing_crossing_count": len(through_board_pairs),
                "minimum_encoder_opposing_crossing": {
                    "feature": minimum_through_feature.feature,
                    "ui_instance": minimum_through_body.instance,
                    "remaining_z_clearance_mm": round(minimum_through_clearance, 6),
                },
                "u214_socket": {
                    "mpn": devices[instances["u214_connector"]]["mpn"],
                    "tail_plan_keepout_mm": [
                        U214_CONNECTOR_PTH_KEEPOUT_W,
                        U214_CONNECTOR_PTH_KEEPOUT_D,
                    ],
                    "minimum_inner_plan_clearance_mm": OPPOSITE_FACE_CLEARANCE_MM,
                    "result": "paper_geometry_passed_H5_mating_fit_open",
                },
                "outward_rf_connector_count": len(FRONT_RF + REAR_RF),
                "outward_rf_tail_minimum_inner_plan_clearance_mm": OPPOSITE_FACE_CLEARANCE_MM,
            },
            "pcb_copper_and_vias": {
                "result": "not_yet_proven_pre_kicad",
                "reason": "logical pin and net maps do not prove escape routing, return paths, via fields or DRC clearance through real footprints",
                "voice_v_rf_endpoint_distance_mm": round(polyline_length(VOICE_V_RF_CORRIDOR), 6),
                "voice_u_rf_endpoint_distance_mm": round(polyline_length(VOICE_U_RF_CORRIDOR), 6),
                "voice_rf_route_rendering": "two_source_to_two_port_topology_guides_no_claimed_copper_path",
                "closure": "route both boards in KiCad, then pass schematic/ERC, layout DRC, differential/controlled-impedance review and independent manufacturing-rule review",
            },
            "remaining_gates": [
                "H5 received E01-ML01IPX connector axes and cable bend/retention coupons",
                "H5 received HMX035CTFT-001 FPC tail and bend path",
                "KiCad footprint-level copper/via routing and DRC",
                "assembled tolerance stack and HIL",
            ],
        },
        "resolved_body_count": len(rows),
        "rows": rows,
    }


def build_external_face_acceptance(devices: dict, instances: dict, model: dict) -> dict:
    """Emit the exact H1.3 exterior package presented at the H1.3.1 user gate."""
    display = devices[instances["display"]]
    function_button_w, function_button_h = placement_size(
        SIDE_FUNCTION_CONTROLS[0], devices, instances
    )
    display_x = 10.25
    display_right = display_x + float(display["dimensions_mm"][0])
    left_display_clearance = display_x - (
        SIDE_FUNCTION_CONTROLS[0].x + function_button_w
    )
    right_display_clearance = SIDE_FUNCTION_CONTROLS[4].x - display_right
    top_mounting_keepout_clearance = min(
        item.y - (hole_y + MOUNT_KEEPOUT_R)
        for item in SIDE_FUNCTION_CONTROLS
        for hole_x, hole_y in HOLES
        if item.x <= hole_x <= item.x + function_button_w and hole_y < item.y
    )

    def antenna_ports(bank):
        return [
            {
                "path": path,
                "user_label": list(RF_USER_LABEL_LINES[path]),
                "connector_type": polarity,
                "connector_mpn": devices[instances[RF_INSTANCE_BY_PATH[path]]]["mpn"],
                "x_center_mm": centre,
            }
            for centre, path, polarity in bank
        ]

    def controls(items):
        rows = []
        for item in items:
            width, height = placement_size(item, devices, instances)
            rows.append(
                {
                    "instance": item.instance,
                    "mpn": devices[instances[item.instance]]["mpn"],
                    "role": item.role,
                    "position_mm": [item.x, item.y],
                    "envelope_mm": [round(width, 6), round(height, 6)],
                }
            )
        return rows

    front_edges = [
        {"instance": instance, "edge": side, "coordinate_mm": coordinate, "silkscreen": label}
        for instance, face, side, coordinate, label in EDGE_INTERFACES
        if face == "front"
    ]
    rear_edges = [
        {"instance": instance, "edge": side, "coordinate_mm": coordinate, "silkscreen": label}
        for instance, face, side, coordinate, label in EDGE_INTERFACES
        if face == "rear"
    ]
    rear_component_labels = [
        {"instance": instance, "edge": side, "coordinate_mm": coordinate, "silkscreen": label}
        for instance, face, side, coordinate, label in EXTERNAL_COMPONENT_LABELS
        if face == "rear"
    ]
    return {
        "schema_version": 1,
        "stage": "H1.3.0",
        "status": "reviewed",
        "review_gate": "H1.3.1",
        "artifact": str(EXTERNAL_OUTPUT.relative_to(REPO)),
        "coordinate_model": model["model_id"],
        "review_scope": "Complete outward front and rear PCB faces: physical envelopes, controls, user silkscreen and interface directions.",
        "explicitly_out_of_scope": [
            "inner-board placement and sandwich relationship (H1.4.1)",
            "antenna-edge and sectional service geometry (H1.5.1)",
            "production ECAD placement, routing and enclosure release",
        ],
        "machine_checks": {
            "same_board_outline_and_scale": True,
            "unified_coordinate_source": True,
            "registered_physical_envelopes": True,
            "mounting_keepouts_clear": True,
            "silkscreen_inside_outer_faces": True,
            "silkscreen_unobscured": True,
            "silkscreen_labels_nonoverlapping": True,
            "external_interface_directions_present": True,
            "exactly_three_external_usb_ports": True,
            "six_external_compute_rst_boot_controls": True,
            "all_six_service_buttons_recessed": True,
            "dbg10_headers_internal_only": True,
            "both_antenna_banks_on_outward_faces": True,
            "function_key_columns_clear_display_and_mounting_keepouts": True,
        },
        "front": {
            "board_outline_mm": [BOARD_W, BOARD_H],
            "product_silkscreen": next(
                {
                    "text": value,
                    "position_mm": [x, y],
                    "font_size_px_at_drawing_scale": size,
                }
                for face, value, x, y, size in OUTER_FACE_PRODUCT_MARKS
                if face == "front"
            ),
            "display": {
                "mpn": display["mpn"],
                "body_mm": display["dimensions_mm"],
                "active_area_mm": display["active_area_mm"],
                "pixels": display["pixel_resolution"],
            },
            "function_key_columns": {
                "mpn": devices[instances["ui_switch_f1"]]["mpn"],
                "button_envelope_mm": [function_button_w, function_button_h],
                "left": ["F1", "F2", "F3", "F4"],
                "right": ["F5", "F6", "F7", "F8"],
                "vertical_pitch_mm": 13.5,
                "board_edge_clearance_mm": 1.8,
                "display_clearance_mm": round(
                    min(left_display_clearance, right_display_clearance), 6
                ),
                "top_mounting_keepout_clearance_mm": round(
                    top_mounting_keepout_clearance, 6
                ),
                "free_expander_inputs_after_placement": 0,
            },
            "antenna_ports": antenna_ports(FRONT_RF),
            "tx_indicators": [
                {
                    "instance": instance,
                    "mpn": devices[instances[instance]]["mpn"],
                    "silkscreen": label,
                    "position_mm": [x, y],
                    "row": index // 5 + 1,
                    "column": index % 5 + 1,
                }
                for index, (instance, label, x, y) in enumerate(FRONT_FACE_INDICATORS)
                if instance != "fault_led"
            ],
            "status_indicators": [
                {
                    "instance": instance,
                    "mpn": devices[instances[instance]]["mpn"],
                    "silkscreen": label,
                    "position_mm": [x, y],
                    "row": index // 5 + 1,
                    "column": index % 5 + 1,
                    "source": "FAULT_KILL hardware latch",
                }
                for index, (instance, label, x, y) in enumerate(FRONT_FACE_INDICATORS)
                if instance == "fault_led"
            ],
            "controls": controls(FRONT_CONTROLS),
            "service_side_controls": controls(
                tuple(item for item in UI_INNER if item.instance in EXTERNAL_SERVICE_BUTTONS)
            ),
            "service_button_recess_mm": SERVICE_BUTTON_RECESS_MM,
            "navigation_cluster": {
                "design_id": "L2-NAV-5B-001-A",
                "manufacturing_class": "serial_components_only",
                "custom_mechanical_parts": 0,
            },
            "edge_interfaces": front_edges,
        },
        "rear": {
            "board_outline_mm": [BOARD_W, BOARD_H],
            "product_silkscreen": next(
                {
                    "text": value,
                    "position_mm": [x, y],
                    "font_size_px_at_drawing_scale": size,
                }
                for face, value, x, y, size in OUTER_FACE_PRODUCT_MARKS
                if face == "rear"
            ),
            "project_url_silkscreen": next(
                {
                    "text": value,
                    "position_mm": [x, y],
                    "font_size_px_at_drawing_scale": size,
                }
                for face, value, x, y, size in OUTER_FACE_PRODUCT_MARKS
                if face == "rear" and value == PROJECT_REPOSITORY_URL
            ),
            "antenna_ports": antenna_ports(REAR_RF),
            "u214": {
                "mpn": devices[instances["u214"]]["mpn"],
                "installed_envelope_mm": [U214_W, U214_H],
                "position_mm": [U214_X, U214_Y],
            },
            "battery_holder": {
                "mpn": devices[instances["pack_holder"]]["mpn"],
                "position_mm": [17.6, PACK_HOLDER_Y],
                "orientation_deg": 90,
                "cells": ["pack_cell0", "pack_cell1"],
            },
            "controls": controls(REAR_CONTROLS),
            "service_side_controls": controls(
                tuple(item for item in RF_INNER if item.instance in EXTERNAL_SERVICE_BUTTONS)
            ),
            "service_button_recess_mm": SERVICE_BUTTON_RECESS_MM,
            "encoder_actuator_mpn": devices[instances["encoder_knob"]]["mpn"],
            "edge_interfaces": rear_edges,
            "external_component_labels": rear_component_labels,
        },
        "internal_fallback_diagnostics": {
            "classification": "not_user_facing; accessible only after opening the board sandwich",
            "headers": controls(
                tuple(
                    item
                    for item in UI_INNER + RF_INNER
                    if item.instance in {"s3_dbg_header", "c5_dbg_header", "rp_dbg_header"}
                )
            ),
        },
    }


def build_cross_view_acceptance(
    candidate: dict,
    devices: dict,
    source_table: dict,
    coordinate_table: dict,
    external_acceptance: dict,
) -> dict:
    """Build one H1.7 package that reconciles every physical view and pin budget."""
    allocation_counts: dict[str, int] = {}
    for allocation in candidate["allocations"]:
        owner = allocation["instance"]
        allocation_counts[owner] = allocation_counts.get(owner, 0) + 1

    contact_accounting = candidate["contact_accounting"]
    slow = contact_accounting["slow_io"]
    ui = contact_accounting["ui_matrix_io"]
    m1 = candidate["interboard_contract"]["accounting"]
    fit = coordinate_table["interboard_fit_audit"]
    passage = coordinate_table["physical_interconnect_clearance_audit"]
    headset_ports = devices[candidate["instances"]["headset_control_io"]][
        "allocatable_contacts"
    ]

    return {
        "schema_version": 1,
        "stage": "H1.7.0",
        "status": "reviewed",
        "review_gate": "H1.7.1",
        "final_acceptance": {
            "gate": "H1.8",
            "status": "accepted",
            "date": "2026-08-23",
            "basis": "explicit user acceptance after the complete H1 self-review report",
        },
        "coordinate_model": coordinate_table["model_id"],
        "artifacts": {
            "external_faces": {
                "path": "docs/images/current-clamshell.svg",
                "review_gate": external_acceptance["review_gate"],
                "status": external_acceptance["status"],
            },
            "external_service_access": {
                "path": "docs/images/service-access.svg",
                "status": "reviewed",
                "external_usb_ports": 3,
                "external_recovery_buttons": 6,
                "internal_dbg10_headers": 3,
            },
            "inner_faces": {
                "path": "docs/images/internal-board-layout.svg",
                "status": "reviewed",
                "mirrored_x": True,
                "inner_silkscreen": "none",
            },
            "antenna_edge": {
                "path": "docs/images/top-edge-view.svg",
                "status": "reviewed",
                "equal_x_z_scale": True,
            },
            "physical_sections": {
                "path": "docs/images/sandwich-section.svg",
                "status": "reviewed",
                "equal_x_z_scale": True,
                "separate_cut_planes": ["U214", "battery/control"],
                "service_trajectories": ["CAP insert/remove", "cells insert/remove"],
            },
            "principle_schematics": "docs/schematics.md",
            "pinout": "docs/pinout.md",
            "interconnect": "docs/interconnect.md",
        },
        "physical_fit": {
            "result": fit["result"],
            "source_registered_instances": source_table["summary"][
                "rendered_physical_instances"
            ],
            "inner_body_count": fit["inner_body_count"],
            "total_inner_component_count_including_adapter": fit[
                "total_inner_component_count_including_adapter"
            ],
            "minimum_required_clearance_mm": fit["minimum_required_clearance_mm"],
            "minimum_opposing_pair": fit["minimum_opposing_pair"],
            "display_adapter_minimum_clearance_mm": fit["display_adapter_assembly"][
                "minimum_opposing_z_clearance_mm"
            ],
            "all_external_machine_checks": all(
                external_acceptance["machine_checks"].values()
            ),
            "physical_interconnect_result": passage["result"],
            "five_rf_microcoaxes_accounted": passage["rf_microcoax"][
                "all_five_feed_assemblies_accounted"
            ],
            "ten_outward_rf_ports": passage["outer_face_through_board_features"][
                "outward_rf_connector_count"
            ],
        },
        "pin_resource_fit": {
            "result": "paper_pin_and_contact_fit_passed",
            "direct_allocation_counts": allocation_counts,
            "free_gpio": candidate["free_gpio"],
            "main_slow_io": {
                "used": len(slow["used"]),
                "reserved": len(slow["reserved"]),
                "free": len(slow["free"]),
            },
            "ui_input_expander": {
                "used": len(ui["used"]),
                "reserved": len(ui["reserved"]),
                "free": len(ui["free"]),
            },
            "headset_control_expander": {
                "used": [headset_ports[0]],
                "pulled_local_reserves": headset_ports[1:],
                "i2c_address_7bit": "0x39",
            },
            "m1": {
                "positions": m1["positions"],
                "assigned": m1["positions"] - m1["reserved"],
                "reserved_no_connect": m1["reserved"],
            },
            "summary": candidate["ui_control_contract"]["pin_budget_result"],
        },
        "not_claimed": {
            "production_schematic_complete": False,
            "production_schematic_authorized": True,
            "pcb_copper_and_vias": passage["pcb_copper_and_vias"]["result"],
            "pcb_placement_and_routing_authorized": False,
            "purchase_authorized": False,
        },
        "remaining_gates": passage["remaining_gates"],
    }


def render_physical_source_register(source_table: dict) -> str:
    """Expose the final physical-source result without project-history clutter."""
    summary = source_table["summary"]
    frame_counts: dict[str, int] = {}
    for row in source_table["rows"]:
        frame_counts[row["frame"]] = frame_counts.get(row["frame"], 0) + 1
    lines = [
        "# Physical source register",
        "",
        "[Hardware](hardware.md) · [Roadmap](roadmap.md) · [Русский](physical-source-register.ru.md)",
        "",
        "Every body drawn in the product views is generated from one machine row with",
        "an exact selected MPN (or an explicit TBD), manufacturer-backed envelope, named",
        "coordinate frame, orientation and interface direction. No H1 geometry blocker",
        "remains; received fit, RF, acoustic, thermal and endurance checks stay in H5.",
        "",
        "| Coverage | Result |",
        "|---|---:|",
        f"| Rendered physical instances | {summary['rendered_physical_instances']} |",
        f"| Exact-MPN instances | {summary['exact_mpn_instances']} |",
        f"| Explicit MPN TBD instances | {summary['explicit_mpn_tbd_instances']} |",
        f"| H1 geometry blockers | {summary['h1_blockers']} |",
        f"| H5 received-sample gates | {summary['h5_received_sample_gates']} |",
        "",
        "## Coordinate frames",
        "",
        "| Frame | Datum | Bodies |",
        "|---|---|---:|",
    ]
    for frame, count in sorted(frame_counts.items()):
        lines.append(f"| `{frame}` | {MECHANICAL_PROJECTION_FRAMES[frame]} | {count} |")
    lines += [
        "",
        "The complete per-instance table is retained as",
        "[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)",
        "for deterministic rendering, review and later ECAD transfer. The resolved",
        "front-facing X/Y/Z projection is",
        "[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).",
        "",
    ]
    return "\n".join(lines)


def render_physical_source_register_ru(source_table: dict) -> str:
    summary = source_table["summary"]
    frame_counts: dict[str, int] = {}
    for row in source_table["rows"]:
        frame_counts[row["frame"]] = frame_counts.get(row["frame"], 0) + 1
    lines = [
        "# Реестр физических первоисточников",
        "",
        "[Железо](hardware.ru.md) · [Роадмап](roadmap.ru.md) · [English](physical-source-register.md)",
        "",
        "Каждый корпус на продуктовых видах генерируется из одной machine-строки:",
        "точный выбранный MPN (или явный TBD), подтверждённый производителем габарит,",
        "именованная система координат, ориентация и направление интерфейса. Blocker",
        "геометрии H1 не осталось; проверка посадки, RF, акустики, тепла и ресурса",
        "реальных деталей остаётся на H5.",
        "",
        "| Покрытие | Результат |",
        "|---|---:|",
        f"| Отрисованных физических экземпляров | {summary['rendered_physical_instances']} |",
        f"| Экземпляров с точным MPN | {summary['exact_mpn_instances']} |",
        f"| Экземпляров с явным MPN TBD | {summary['explicit_mpn_tbd_instances']} |",
        f"| Blocker геометрии H1 | {summary['h1_blockers']} |",
        f"| Received-sample gate H5 | {summary['h5_received_sample_gates']} |",
        "",
        "## Системы координат",
        "",
        "| Система | Datum | Корпусов |",
        "|---|---|---:|",
    ]
    for frame, count in sorted(frame_counts.items()):
        lines.append(f"| `{frame}` | {MECHANICAL_PROJECTION_FRAMES[frame]} | {count} |")
    lines += [
        "",
        "Полная таблица по каждому экземпляру хранится в",
        "[`H1-physical-source-table.json`](../hardware/product-design/generated/H1-physical-source-table.json)",
        "и является детерминированным входом для отрисовки, ревью и переноса в ECAD.",
        "Единая front-facing проекция X/Y/Z записана в",
        "[`H1-unified-coordinate-table.json`](../hardware/product-design/generated/H1-unified-coordinate-table.json).",
        "",
    ]
    return "\n".join(lines)


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
    (
        devices, candidate, instances, navigation_cluster,
        display_adapter_design, assembly_coordinate_model,
    ) = load()
    source_table = build_physical_source_table(devices, instances)
    unified_coordinate_table = build_unified_coordinate_table(
        source_table, assembly_coordinate_model, devices, instances,
        display_adapter_design,
    )
    external_face_acceptance = build_external_face_acceptance(
        devices, instances, assembly_coordinate_model
    )
    cross_view_acceptance = build_cross_view_acceptance(
        candidate, devices, source_table, unified_coordinate_table,
        external_face_acceptance,
    )
    outputs = {
        EXTERNAL_OUTPUT: render_external(devices, instances),
        SERVICE_OUTPUT: render_service_access(devices, instances),
        INTERNAL_OUTPUT: render_internal(devices, instances, display_adapter_design),
        SANDWICH_OUTPUT: render_sandwich(devices, instances),
        TOP_EDGE_OUTPUT: render_top_edge(devices, instances),
        NAVIGATION_OUTPUT: render_navigation_cluster(navigation_cluster, devices, instances),
        DISPLAY_ADAPTER_OUTPUT: render_display_adapter(display_adapter_design),
        SOURCE_TABLE_OUTPUT: json.dumps(source_table, ensure_ascii=False, indent=2) + "\n",
        UNIFIED_COORDINATE_TABLE_OUTPUT: json.dumps(
            unified_coordinate_table, ensure_ascii=False, indent=2
        ) + "\n",
        EXTERNAL_ACCEPTANCE_OUTPUT: json.dumps(
            external_face_acceptance, ensure_ascii=False, indent=2
        ) + "\n",
        CROSS_VIEW_ACCEPTANCE_OUTPUT: json.dumps(
            cross_view_acceptance, ensure_ascii=False, indent=2
        ) + "\n",
        SOURCE_REGISTER_OUTPUT: render_physical_source_register(source_table),
        REPO / "docs/physical-source-register.ru.md": render_physical_source_register_ru(source_table),
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
        print("ok: external, internal, top-edge, section, navigation and display-adapter mechanical projections are valid and current")
    if not args.write and not args.check:
        parser.error("choose --write or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
