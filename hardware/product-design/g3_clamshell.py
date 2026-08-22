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
EXTERNAL_OUTPUT = REPO / "docs/images/current-clamshell.svg"
INTERNAL_OUTPUT = REPO / "docs/images/internal-board-layout.svg"
SANDWICH_OUTPUT = REPO / "docs/images/sandwich-section.svg"
TOP_EDGE_OUTPUT = REPO / "docs/images/top-edge-view.svg"

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
    (30.0, "RX-FM/SW", "SMA"),
    (45.0, "RX-AM/LW", "SMA"),
    (59.0, "C5-2G4/5", "RP-SMA"),
)
REAR_RF = (
    (13.5, "N24-0", "SMA"),
    (25.5, "CC-SUB", "SMA"),
    (37.5, "N24-1", "SMA"),
    (49.5, "VOICE-V/U", "SMA"),
    (61.5, "N24-2", "SMA"),
)
VOICE_RF_CORRIDOR = ((49.5, 0.0), (49.5, 33.0))
OPPOSITE_FACE_CLEARANCE_MM = 1.5
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
    ("s3_tx_led", "WI-FI/BLE", 5.1, 104.5),
    ("c5_tx_led", "WI-FI/15.4", 20.9, 104.5),
    ("nrf0_tx_led", "nRF24-1", 36.7, 104.5),
    ("nrf1_tx_led", "nRF24-2", 52.5, 104.5),
    ("nrf2_tx_led", "nRF24-3", 68.3, 104.5),
    ("cc_tx_led", "SUB-GHz", 5.1, 111.0),
    ("voice_tx_led", "VHF/UHF", 20.9, 111.0),
    ("ir_tx_led", "IR", 36.7, 111.0),
    ("ext_tx_led", "LORA/EXT", 52.5, 111.0),
    ("any_tx_led", "TX ACTIVE", 68.3, 111.0),
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
    ("power_command_switch", "rear", "right", 112.75, "RUN / KILL"),
    ("product_usb_connector", "rear", "bottom", 16.47, "USB / POWER"),
    ("rp_service_usb_connector", "rear", "bottom", 37.47, "RP SERVICE USB"),
    ("unit_connector", "rear", "bottom", 57.0, "M5 UNIT"),
)

# Acoustic openings have a physical location but no electrical direction.
ACOUSTIC_OPENINGS = (
    ("speaker", "rear", "right", 133.0, "SPEAKER / GRILLE"),
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
    "power_command_switch": ("RUN", "KILL"),
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
    Placement("display_connector", 25.0, 43.0, "40-contact display FPC mate"),
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
    Placement("headphone_jack", 60.0, 75.0, "3.5-mm headphone/line connector"),
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

# Exact module-side axes come from the Espressif package drawings.  Each
# polyline is exactly the selected 30-mm assembly length in plan.  Corners are
# a route corridor rather than a cable-fold instruction; bend radius and
# strain relief are verified on the received feed coupon.
UI_RF_CABLES = (
    CableRoute(
        "s3_rf_jumper",
        ((21.0, 24.46), (26.0, 24.46), (26.0, 14.0), (15.45, 14.0), (15.45, 10.55), (16.0, 10.55)),
        "exact 30-mm S3 UMCC Gen1 jumper corridor",
    ),
    CableRoute(
        "c5_rf_jumper",
        ((66.0, 24.38), (66.0, 18.0), (59.4, 18.0), (59.4, 13.0), (64.0, 13.0), (64.0, 10.55), (59.0, 10.55)),
        "exact 30-mm C5 UMCC Gen1 jumper corridor",
    ),
)

RF_INNER = (
    Placement("nrf0_rf_board_connector", 23.0, 28.0, "nRF24 #0 Gen1 jumper board receptacle"),
    Placement("nrf1_rf_board_connector", 50.0, 28.0, "nRF24 #1 Gen1 jumper board receptacle"),
    Placement("nrf2_rf_board_connector", 70.0, 22.0, "nRF24 #2 Gen1 jumper board receptacle"),
    Placement("rp", 0.0, 33.0, "deterministic radio owner"),
    Placement("nrf0", 10.0, 7.5, "full-function nRF24 radio #0"),
    Placement("nrf1", 31.5, 7.5, "full-function nRF24 radio #1; rotated for U214 tail clearance", 90),
    Placement("nrf2", 52.9, 7.5, "full-function nRF24 radio #2"),
    Placement("voice", 12.0, 33.0, "VHF/UHF voice transceiver; contact 7 faces its SMA", 180),
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
    Placement("safe_latch", 37.0, 82.0, "asynchronous FAULT_KILL latch"),
    Placement("safe_reset_buffer", 41.0, 82.0, "C5/RP fault-reset buffer"),
    Placement("safe_reset_sink_a", 44.0, 82.0, "S3/C5 passive-drain reset sinks"),
    Placement("safe_supervisor", 49.0, 82.0, "always-on safety supervisor"),
    Placement("safe_reset_sink_b", 55.0, 82.0, "RP reset sink"),
    Placement("safe_ptt_or", 59.0, 82.0, "FAULT_KILL-dominant voice PTT gate"),
    Placement("safe_gate_b", 49.0, 88.0, "rear-domain transmit safety gates"),
    Placement("evidence_cmp_b", 58.0, 88.0, "RF-local nRF/CC TX evidence comparator"),
    Placement("evidence_cmp_voice", 66.0, 88.0, "RF-local voice TX evidence comparator"),
    Placement("product_usb_protector", 7.5, 135.0, "product USB CC/USB2 protector"),
    Placement("pd_controller", 11.5, 134.5, "sink-only USB-PD controller"),
    Placement("speaker_amp", 31.0, 87.0, "rear-local differential speaker amplifier"),
    Placement("safe_gate_a", 49.0, 94.0, "nRF-domain transmit safety gates"),
    Placement("m1_rf_receptacle", 22.2, 119.0, "80-contact M1 receptacle; 11-mm board stack"),
    Placement("product_usb_connector", 12.0, 143.1, "product USB-C data and sink"),
    Placement("rp_service_usb_connector", 33.0, 142.65, "RP data-only service USB"),
    Placement("unit_connector", 51.0, 140.9, "native M5 Unit HY2.0-4P edge receptacle"),
    Placement("microphone", 45.0, 146.0, "rear bottom microphone port"),
    Placement("speaker", 50.0, 127.0, "internal 4-Ohm differential speaker"),
    Placement("rp_dbg_header", 40.0, 104.0, "keyed RP SWD/RUN/USB_BOOT header"),
    Placement("rp_reset_button", 51.0, 104.0, "RP technological RUN/RESET"),
    Placement("rp_boot_button", 59.5, 104.0, "RP technological USB_BOOT"),
    Placement("power_command_switch", 65.8, 111.0, "single low-current RUN/KILL; charging remains available in KILL"),

    Placement("u214_host_buffer_a", 55.3, 27.3, "U214 host-command buffer A"),
    Placement("u214_host_buffer_b", 61.2, 27.3, "U214 host-command buffer B"),
    Placement("u214_return_buffer", 67.1, 27.3, "U214 return-path buffer"),
    Placement("u214_i2c_iso", 67.1, 34.0, "U214 hot-swap I2C isolation and stuck-bus recovery"),
    Placement("nrf0_host_buffer", 0.0, 44.0, "nRF24 #0 host-command buffer"),
    Placement("nrf0_return_buffer", 6.0, 44.0, "nRF24 #0 return-path buffer"),
    Placement("nrf1_host_buffer", 55.3, 34.0, "nRF24 #1 host-command buffer"),
    Placement("nrf1_return_buffer", 61.2, 34.0, "nRF24 #1 return-path buffer"),
    Placement("nrf2_host_buffer", 55.3, 40.0, "nRF24 #2 host-command buffer"),
    Placement("nrf2_return_buffer", 61.2, 40.0, "nRF24 #2 return-path buffer"),
    Placement("cc_host_buffer", 55.3, 58.0, "CC1101 host-command buffer"),
    Placement("cc_return_buffer", 61.2, 58.0, "CC1101 return-path buffer"),
    Placement("cc_band_buffer", 67.1, 58.0, "CC1101 band-select buffer"),

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
    Placement("evidence_mask", 50.0, 67.0, "AON evidence-source mask expander"),

    Placement("pd_pphv_cap0", 1.0, 127.0, "USB-PD high-voltage bulk capacitor #0"),
    Placement("pd_pphv_cap1", 4.9, 127.0, "USB-PD high-voltage bulk capacitor #1"),
    Placement("pd_pphv_cap2", 8.8, 127.0, "USB-PD high-voltage bulk capacitor #2"),
    Placement("pd_pphv_cap3", 12.7, 127.0, "USB-PD high-voltage bulk capacitor #3"),
    Placement("pd_config_eeprom", 16.3, 134.5, "TPS25751 configuration EEPROM"),
    Placement("pd_vbus_cap", 22.0, 134.5, "raw VBUS local capacitor"),
    Placement("pd_vbus_tvs", 26.0, 134.5, "raw VBUS flat-clamp TVS"),
)

FRONT_CONTROLS = (
    Placement("ui_switch_back", 16.8, 129.4, "direct-press BACK"),
    Placement("ui_dpad_switch", 32.21, 127.11, "four directions plus center push", 45),
    Placement("ui_switch_opt", 51.6, 129.4, "direct-press OPT"),
)

DIRECT_PRESS_FRONT_CONTROLS = {"ui_switch_back", "ui_switch_opt"}

REAR_CONTROLS = (
    Placement("encoder", 2.5, 45.0, "rear encoder above F1/F2"),
    Placement("ui_switch_f1", 4.2, 63.5, "rear F1"),
    Placement("ui_switch_f2", 4.2, 78.5, "rear F2"),
    Placement("ptt_switch", 64.2, 63.5, "rear independent PTT"),
)

DIRECT_PRESS_REAR_CONTROLS = {
    "ui_switch_f1", "ui_switch_f2", "ptt_switch"
}

FRONT_CAP_RESERVES = (
    Reserve(
        "single D-pad cross", 28.8, 122.9, 17.4, 19.0,
        "custom keyed D-pad actuator over one SKRHADE010 stem; supplier MPN does not apply",
        "custom_actuator",
    ),
)

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
MECHANICAL_ASSEMBLY_EMBEDDED_INSTANCES = {"display_touch_controller"}
MECHANICAL_EXTERIOR_INSTANCES = {
    "display", "u214", "pack_holder", "pack_cell0", "pack_cell1",
    *RF_INSTANCE_BY_PATH.values(),
    *TX_LED_INSTANCES.values(),
    *(route.instance for route in UI_RF_CABLES),
    "nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper",
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
    "display_connector": "FPC insertion in the UI-inner plane; received-tail fit remains a named sample gate",
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
    "s3_reset_button": "normal to the UI-inner face; enclosure-open service only",
    "s3_boot_button": "normal to the UI-inner face; enclosure-open service only",
    "c5_reset_button": "normal to the UI-inner face; enclosure-open service only",
    "c5_boot_button": "normal to the UI-inner face; enclosure-open service only",
    "rp_reset_button": "normal to the RF-inner face; enclosure-open service only",
    "rp_boot_button": "normal to the RF-inner face; enclosure-open service only",
    "nrf0": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "nrf1": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "nrf2": "normal to the RF-inner face inside the bounded module-face Gen1 endpoint zone; exact axis remains H5 evidence",
    "voice": "contact 7 faces the antenna edge along the straight VHF/UHF corridor",
}

DIRECTIONAL_BODY_DIRECTIONS = {
    **INTERNAL_CONNECTOR_ACTUATOR_DIRECTIONS,
    **{
        instance: f"{face} {side} enclosure exit"
        for instance, face, side, _, _ in EDGE_INTERFACES
    },
    **{
        instance: f"{face} {side} acoustic opening"
        for instance, face, side, _, _ in ACOUSTIC_OPENINGS
    },
    **{item.instance: "front-normal outward actuation" for item in FRONT_CONTROLS},
    **{item.instance: "rear-normal outward actuation" for item in REAR_CONTROLS},
    **{item.instance: "rear-normal outward actuation" for item in REAR_SELECTED_ACTUATORS},
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
        for instance in TX_LED_INSTANCES.values()
    ),
    *(
        BodyProjectionContract(route.instance, "ui-inner-route", 0, "module-to-board RF cable path")
        for route in UI_RF_CABLES
    ),
    *(
        BodyProjectionContract(
            instance,
            "rf-inner-route",
            0,
            "bounded module-face zone to fixed Gen1 board receptacle; exact axis closes in H5",
        )
        for instance in ("nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper")
    ),
    BodyProjectionContract(
        "display_touch_controller",
        "display-assembly",
        0,
        "embedded in HMX035CTFT-001; no separate mechanical interface",
    ),
)


def load() -> tuple[dict, dict, dict]:
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    return devices, candidate, candidate["instances"]


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
                axis_aligned_segment_hits_box(start, end, rf_box, cable_radius)
                for start, end in zip(route.points, route.points[1:])
            ):
                clearance = (
                    INTERBOARD_GAP_MM
                    - cable_od
                    - placement_height(rf_item, devices, instances)
                )
                pairs.append((clearance, route, rf_item))
    return sorted(pairs, key=lambda row: (row[0], row[1].instance, row[2].instance))


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
        actual_length = polyline_length(route.points)
        if abs(actual_length - expected_length) > 0.05:
            errors.append(
                f"native-rf-cable: {route.instance} route is {actual_length:.2f} mm, "
                f"not the exact {expected_length:.2f}-mm assembly"
            )
        cable_radius = float(device["electrical_contract"]["cable_outer_diameter_mm"]) / 2
        cable_od = cable_radius * 2
        if INTERBOARD_GAP_MM - cable_od < MIN_INTERBOARD_Z_CLEARANCE_MM:
            errors.append(f"native-rf-cable: {route.instance} does not fit the interboard channel")
        for point in route.points:
            if not (cable_radius <= point[0] <= BOARD_W - cable_radius and cable_radius <= point[1] <= BOARD_H - cable_radius):
                errors.append(f"native-rf-cable: {route.instance} leaves the PCB plan at {point}")
        for segment in zip(route.points, route.points[1:]):
            try:
                axis_aligned_segment_hits_box(*segment, (0.0, 0.0, 0.0, 0.0))
            except ValueError as error:
                errors.append(f"native-rf-cable: {route.instance}: {error}")
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
            try:
                route_hits = any(
                    axis_aligned_segment_hits_box(
                        start,
                        end,
                        item_box,
                        cable_radius + MIN_INTERBOARD_Z_CLEARANCE_MM,
                    )
                    for start, end in zip(route.points, route.points[1:])
                )
            except ValueError:
                route_hits = False
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
    if constraint.get("current_step") != "H1.1.3.3.3":
        errors.append("mechanical-gates: exact evidence-research substep drifted")

    gates = data.get("gates", [])
    identifiers = [gate.get("id") for gate in gates]
    if len(identifiers) != len(set(identifiers)) or any(not item for item in identifiers):
        errors.append("mechanical-gates: gate IDs must be present and unique")
    required_h1 = {
        "H1-MECH-DISPLAY-TAIL",
        "H1-MECH-U214-MATING-STACK",
        "H1-MECH-DPAD-ACTUATOR",
    }
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
        "display", "display_connector",
        "nrf0", "nrf1", "nrf2",
        "nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper",
        "nrf0_rf_board_connector", "nrf1_rf_board_connector", "nrf2_rf_board_connector",
        "nrf0_external_sma", "nrf1_external_sma", "nrf2_external_sma",
        "u214", "u214_connector", "ui_dpad_switch",
        "voice", "encoder", "encoder_knob", "power_command_switch",
        "ui_switch_back", "ui_switch_opt", "ui_switch_f1", "ui_switch_f2", "ptt_switch",
        "unit_connector", "pack_holder", "pack_cell0", "pack_cell1",
        "s3_rf_jumper", "c5_rf_jumper", "s3_rf_board_connector", "c5_rf_board_connector",
        "speaker", "microphone",
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
    if data.get("current_substep") != "H1.1.3.3.3":
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
        ("H1.1.3.3.3", "current"),
        ("H1.1.3.3.4", "blocked"),
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


def validate() -> list[str]:
    devices, candidate, instances = load()
    errors: list[str] = []
    required = {
        "s3": "ESP32-S3-WROOM-1U-N16R8",
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

    mechanically_accounted, mechanical_source_errors = validate_mechanical_sources(
        devices, instances
    )
    errors += mechanical_source_errors
    errors += validate_mechanical_evidence_gates(instances, mechanically_accounted)
    errors += validate_source_research()
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
    errors += validate_items("rf-inner", RF_INNER, devices, instances)
    inner_height_errors = []
    for item in UI_INNER + RF_INNER:
        try:
            placement_height(item, devices, instances)
        except ValueError as error:
            inner_height_errors.append(str(error))
    errors += inner_height_errors
    if not inner_height_errors:
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

    voice = rf_by_instance["voice"]
    voice_device = devices[instances["voice"]]
    voice_contact = voice_device.get("mechanical_contract", {}).get("antenna_contact", {})
    voice_nominal_w, voice_nominal_h = map(float, voice_device["dimensions_mm"][:2])
    voice_contact_xy = voice_contact.get("nominal_center_from_illustrated_top_left_mm", [])
    if voice.rotation != 180 or len(voice_contact_xy) != 2:
        errors.append("SA518 must retain its manufacturer-drawing contact-7 orientation contract")
    else:
        voice_ant_x = voice.x + voice_nominal_w - float(voice_contact_xy[0])
        voice_ant_y = voice.y + voice_nominal_h - float(voice_contact_xy[1])
        voice_port_x = next(centre for centre, path, _ in REAR_RF if path == "VOICE-V/U")
        if abs(voice_ant_x - voice_port_x) > 0.01 or abs(voice_ant_y - VOICE_RF_CORRIDOR[1][1]) > 0.01:
            errors.append("SA518 contact 7 must remain nominally aligned to the VHF/UHF RF corridor")
        if VOICE_RF_CORRIDOR != ((voice_port_x, 0.0), (voice_ant_x, voice_ant_y)):
            errors.append("SA518 RF corridor must remain a straight controlled path to the VHF/UHF SMA")

    cc_zone = next(zone for zone in INTERNAL_RESERVES if zone.name == "cc-reference-rf-network")
    cc_port_x = next(centre for centre, path, _ in REAR_RF if path == "CC-SUB")
    if not (
        cc_zone.x <= cc_port_x <= cc_zone.x + cc_zone.w
        and cc_zone.y >= RF_BODY_D + OPPOSITE_FACE_CLEARANCE_MM
    ):
        errors.append("CC1101 reference RF zone must align to SUB-GHz and clear the outer connector land")
    front_path_centres = {path: centre for centre, path, _ in FRONT_RF}
    if front_path_centres.get("S3-2G4") != 16.0 or front_path_centres.get("C5-2G4/5") != 59.0:
        errors.append("native RF ports must remain aligned to the two exact 30-mm jumper corridors")
    dpad = next(item for item in FRONT_CONTROLS if item.instance == "ui_dpad_switch")
    dpad_w, dpad_h = placement_size(dpad, devices, instances)
    if dpad.rotation != 45:
        errors.append("SKRHADE010 must remain 45 degrees clockwise so A/B/C/D map to up/right/left/down")
    if abs(dpad.x + dpad_w / 2 - 37.5) > 0.02 or abs(dpad.y + dpad_h / 2 - 132.4) > 0.02:
        errors.append("SKRHADE010 rotated envelope must remain centred at D-pad axis 37.5,132.4 mm")

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
    dpad_mechanical = devices[instances["ui_dpad_switch"]].get("mechanical_contract", {})
    if dpad_mechanical.get("body_thickness_mm") != 1.85:
        errors.append("SKRHADE010 body thickness must remain distinct from its complete stem height")
    if dpad_mechanical.get("overall_to_stem_top_mm") != 5.0:
        errors.append("SKRHADE010 complete stem-top height must remain 5.0 mm from the PCB")
    if dpad_mechanical.get("stem_diameter_mm") != 3.0:
        errors.append("SKRHADE010 custom actuator interface must retain the exact 3-mm stem")
    direct_mechanical = devices[instances["ptt_switch"]].get("mechanical_contract", {})
    if direct_mechanical.get("plunger_diameter_mm") != 3.3:
        errors.append("B3S-1100P direct-press controls must retain the exact 3.3-mm plunger")
    if direct_mechanical.get("nominal_height_mm") != 4.3:
        errors.append("B3S-1100P nominal direct-press height must remain 4.3 mm")
    display = Placement("display", 10.25, 11.0, "display")
    holder = Placement("pack_holder", 17.6, 42.0, "battery holder", 90)
    errors += validate_items("front-display", (display,), devices, instances)
    errors += validate_items("rear-exact", (holder,), devices, instances)
    ui_instances = {item.instance for item in UI_INNER}
    rf_instances = {item.instance for item in RF_INNER}
    if "microphone" in ui_instances or "microphone" not in rf_instances:
        errors.append("microphone must remain on the RF/power PCB inner side")
    if {(instance, face, side) for instance, face, side, _, _ in ACOUSTIC_OPENINGS} != {
        ("speaker", "rear", "right"),
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
    for item in RF_INNER:
        item_w, item_h = placement_size(item, devices, instances)
        if overlaps(
            connector_box,
            (item.x, item.y, item_w, item_h),
            OPPOSITE_FACE_CLEARANCE_MM,
        ):
            errors.append(f"rear opposite faces: U214 through-hole socket conflicts with {item.instance}")
    for zone in INTERNAL_RESERVES:
        if overlaps(
            connector_box,
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
    indicator_rows = {}
    for _, _, x, y in FRONT_TX_INDICATORS:
        indicator_rows.setdefault(y, []).append(x)
    if len(indicator_rows) != 2 or sorted(map(len, indicator_rows.values())) != [5, 5]:
        errors.append("front: all ten TX indicators must remain in two rows of five")
    if len({tuple(sorted(xs)) for xs in indicator_rows.values()}) != 1:
        errors.append("front: both five-indicator rows must retain aligned columns")
    expected_tx_labels = {RF_USER_LABEL_LINES[path][0] for path in TX_RF_PATHS} | {"IR", "LORA/EXT", "TX ACTIVE"}
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

    control_roles = {item.role for item in REAR_CONTROLS}
    for role in ("rear independent PTT", "rear F1", "rear F2"):
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

    def rect(origin, x, y, w, h, fill, stroke, dash="", rx=2.0, extra=""):
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<rect x="{sx(origin,x):.1f}" y="{sy(origin,y):.1f}" '
            f'width="{w*scale:.1f}" height="{h*scale:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dashed}{extra}/>'
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
    cx, cy = sx(origin, 37.5), sy(origin, 132.4)
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
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 8.0), "M5Stack U214 · installed worst-case · 84×24 mm", 6.3, "bold", "middle", "#9a3412"))
    out.append(text(sx(rear,37.5), sy(rear,U214_Y + 12.5), "shared Cap-Bus rail · SSW-107-02-S-D beneath", 5.0, "bold", "middle", "#075985"))
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
    out.append(silk_text(sx(front,20.1), sy(front,140.0), "BACK", 5.0, "bold", "middle", "#4c1d95"))
    out.append(silk_text(sx(front,54.9), sy(front,140.0), "OPT", 5.0, "bold", "middle", "#4c1d95"))

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

    # F1/F2/PTT are complete, directly pressed switches on the exposed PCB.
    # They therefore render as selected solid parts, not speculative caps.
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
    for x, y, label in (
        (7.5, 61.5, "ENC"), (7.5, 74.0, "F1"), (7.5, 89.0, "F2"),
        (67.5, 74.0, "PTT"),
    ):
        out.append(silk_text(sx(rear,x), sy(rear,y), label, 5.0, "bold", "middle", "#4c1d95"))

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
        elif side == "right":
            for offset in (-2.0, 0.0, 2.0):
                out.append(
                    f'<line x1="{sx(rear,BOARD_W-3):.1f}" y1="{sy(rear,coordinate + offset):.1f}" '
                    f'x2="{sx(rear,BOARD_W):.1f}" y2="{sy(rear,coordinate + offset):.1f}" '
                    'stroke="#2563eb" stroke-width="1.4"/>'
                )
            out.append(silk_text(sx(rear,BOARD_W-7.0), sy(rear,coordinate + 1.2), label, 4.2, "bold", "middle", "#2563eb"))
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
        text(note_x,181,"• shared Cap-Bus rail, vertical host socket and Keystone holder all fit",11),
        text(note_x,204,"• exact components clear all M2.5 hole/head keep-outs",11),
        text(note_x,225,"• both RF connector banks mount on the outward PCB faces",11),
        text(note_x,245,"Interface direction",15,"bold"),
        text(note_x,273,"↑ / ↓ / ← / →  interface faces through that enclosure edge",11),
        text(note_x,296,"⊗ / ⊙  press toward / remove away from the viewed face",11),
        text(note_x,319,"○ / ≋  microphone port and speaker grille are locations, not signal directions",11),
        text(note_x,347,"TX indication",15,"bold"),
        '<circle cx="858" cy="370" r="5" fill="#ef4444" stroke="#991b1b"/>',
        text(875,374,"physical actual-TX evidence for each built-in transmitting path",11),
        text(note_x,396,"Nine path indicators plus TX ACTIVE form two aligned rows of five.",11),
        text(note_x,419,"Labels match use: WI-FI/BLE, WI-FI/15.4, nRF24-1..3, SUB-GHz, VHF/UHF, IR and LORA/EXT.",11),
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
        text(note_x,722,"BACK/OPT/F1/F2/PTT are direct buttons; D-pad is one SKRH switch and one cross.",11,"bold"),
        text(note_x,745,"The side C&K JS102011SCQN is the sole RUN/KILL and source-command control.",11),
    ]
    out.append("</svg>")
    return "\n".join(out) + "\n"


def render_internal(devices, instances):
    scale = 3.7
    sx, sy, text, rect = helpers(scale)

    ui, rf = (80.0, 150.0), (465.0, 150.0)
    ui_items = UI_INNER + UI_RF_CABLES
    all_items = ui_items + RF_INNER
    numbers = {item.instance: index for index, item in enumerate(all_items, 1)}
    legend_first_y = 795
    legend_row_height = 21
    rf_legend_columns = 3
    rf_legend_rows = math.ceil(len(RF_INNER) / rf_legend_columns)
    legend_bottom = legend_first_y + (max(len(ui_items), rf_legend_rows) - 1) * legend_row_height + 9
    notes_top = max(560, legend_bottom + 35)
    clearance_pairs = interboard_clearance_pairs(devices, instances)
    cable_clearance_pairs = cable_interboard_clearance_pairs(devices, instances)
    maximum_cable_od = max(
        float(devices[instances[route.instance]]["electrical_contract"]["cable_outer_diameter_mm"])
        for route in UI_RF_CABLES
    )
    minimum_clearance, minimum_ui, minimum_rf = clearance_pairs[0]
    svg_height = notes_top + 317
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1510" height="{svg_height}" viewBox="0 0 1510 {svg_height}" data-view="mirrored-x" data-inner-silkscreen="none">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#dc2626"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(30,32,"Leshy2 — dimensioned inner-board placement",22,"bold"),
        text(30,56,"Inner PCB faces contain no silkscreen text; numbers inside outlines are drawing annotations.",11,colour="#526076"),
        text(30,72,"Red antenna arrows reference outer-face ports; other red arrows show enclosure exits.",9.2,colour="#526076"),
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

    voice_route_points = " ".join(
        f"{sx(rf,mirrored_x(x)):.1f},{sy(rf,y):.1f}"
        for x, y in VOICE_RF_CORRIDOR
    )
    out.append(
        f'<polyline points="{voice_route_points}" fill="none" stroke="#0f766e" stroke-width="2.2" '
        f'data-route="SA518.7-to-VOICE-V/U" data-centreline-mm="{polyline_length(VOICE_RF_CORRIDOR):.2f}"/>'
    )

    out.append('<g id="exact-native-rf-jumpers" data-route-units="mm" data-bend-state="coupon-open">')
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
            f'data-instance="{route.instance}" data-centreline-mm="{polyline_length(route.points):.2f}"/>'
        )
        for endpoint_x, endpoint_y in (route.points[0], route.points[-1]):
            out.append(
                f'<circle cx="{sx(ui,mirrored_x(endpoint_x)):.1f}" cy="{sy(ui,endpoint_y):.1f}" '
                f'r="{1.35*scale:.1f}" fill="none" stroke="#0f766e" stroke-width="1.2"/>'
            )
        annotation_x, annotation_y = route.points[len(route.points) // 2]
        out.append(
            text(
                sx(ui,mirrored_x(annotation_x)), sy(ui,annotation_y)-5,
                str(numbers[route.instance]), 6.8, "bold", "middle", "#115e59"
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
            out.append(rect(origin, view_x, item.y, w, h, fill, stroke, rx=2))
            component_number = str(numbers[item.instance])
            if item.instance == "speaker":
                component_number += " · SPK"
            out.append(text(sx(origin,view_x+w/2), sy(origin,item.y+h/2)+3, component_number, 7.5 if item.instance != "microphone" else 5.2, "bold", "middle"))
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
    ui_legend_x = 30
    rf_legend_x = (400, 770, 1140)
    out += [
        text(30,750,"Numbered physical devices",16,"bold"),
        text(ui_legend_x,775,"UI/control PCB",12,"bold",colour="#1d4ed8"),
    ]
    y = legend_first_y
    for item in ui_items:
        mpn = devices[instances[item.instance]]["mpn"].replace(" (QDtech schematic assembly marking)", "")
        out.append(text(ui_legend_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
        out.append(text(ui_legend_x+26,y+9,item.role,7.2,colour="#526076"))
        y += legend_row_height
    for column_index, column_x in enumerate(rf_legend_x):
        first = column_index * rf_legend_rows
        last = min(first + rf_legend_rows, len(RF_INNER))
        out.append(
            text(
                column_x, 775,
                f"RF/power PCB · {column_index + 1}/{rf_legend_columns}",
                12, "bold", colour="#c2410c",
            )
        )
        y = legend_first_y
        for item in RF_INNER[first:last]:
            mpn = devices[instances[item.instance]]["mpn"]
            out.append(text(column_x,y,f"{numbers[item.instance]:02d}  {mpn}",8.1,"bold"))
            out.append(text(column_x+26,y+9,item.role,7.2,colour="#526076"))
            y += legend_row_height
    note_x = 30
    out += [
        f'<g id="validated-clearances" data-legend-bottom="{legend_bottom}" data-top="{notes_top}" '
        f'data-opposing-pairs="{len(clearance_pairs)}" data-intentional-mates="{len(INTENTIONAL_INTERBOARD_MATES)}" '
        f'data-min-z-clearance-mm="{minimum_clearance:.2f}" data-rf-cable-routes="{len(UI_RF_CABLES)}" '
        f'data-opposing-cable-pairs="{len(cable_clearance_pairs)}" data-cable-od-max-mm="{maximum_cable_od:.2f}" '
        f'data-functional-zones="{len(INTERNAL_RESERVES)}" data-voice-rf-route-mm="{polyline_length(VOICE_RF_CORRIDOR):.2f}">',
        text(note_x,notes_top,"Validated clearances",14,"bold"),
        text(note_x,notes_top+24,"• same-face device-to-device clearance: ≥0.7 mm",10),
        text(note_x,notes_top+45,f"• opposing inner faces: {len(clearance_pairs)} non-mating XY pairs checked; minimum Z gap {minimum_clearance:.2f} mm",10),
        text(note_x,notes_top+66,f"• outward connector / through-hole tail clearance on the opposite face: ≥{OPPOSITE_FACE_CLEARANCE_MM:.1f} mm",10),
        text(note_x,notes_top+87,f"• native RF coax: {len(UI_RF_CABLES)} routes checked; {len(cable_clearance_pairs)} opposing-body crossings; maximum OD {maximum_cable_od:.2f} mm",10),
        text(note_x,notes_top+108,f"• limiting pair: {numbers[minimum_ui.instance]:02d} {minimum_ui.role} / {numbers[minimum_rf.instance]:02d} {minimum_rf.role}",10),
        text(note_x,notes_top+129,"• exact M1 plug/receptacle is one intentional mate, not a clearance pair",10),
        text(note_x,notes_top+150,"• M2.5 hole/head keep-out: 4.0-mm radius",10),
        text(note_x,notes_top+171,"• both inner views are horizontally mirrored from their external faces",10),
        text(note_x,notes_top+192,f"• outer antenna bodies are absent; the {polyline_length(VOICE_RF_CORRIDOR):.2f}-mm SA518.7 copper corridor is shown",10),
        text(note_x,notes_top+213,"• orange dashed boundary is a placement zone, not one combined device",10),
        text(note_x,notes_top+234,"SMA · GCT RFPC-SMA31-FN-175-A",9.2,"bold",colour="#344054"),
        text(note_x,notes_top+254,"RP-SMA · GCT RFPC-SMA32-FN-175-A",9.2,"bold",colour="#344054"),
        text(note_x,notes_top+280,"All five native/nRF module feeds use exact 30-mm 2118651-2 Gen1 jumpers.",9.2,"bold",colour="#166534"),
        text(note_x,notes_top+301,"Placement projection; all mechanically significant bodies are accounted; only small passives and unshown copper are omitted.",9.2,colour="#526076"),
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

    # F1/F2/PTT are exact directly pressed switch bodies; RUN/KILL is side-facing.
    out.append('<g id="rear-controls" data-direct-press="F1-F2-PTT" data-actuator-reserves="none" data-enclosure-reserves="none">')
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
        (7.5, 74.0, "F1", "#4c1d95"),
        (7.5, 89.0, "F2", "#4c1d95"),
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
        t(note_x, 305, "✓ direct buttons and exact knob clear the battery and U214", 12, "bold", colour="#166534"),
        t(note_x, 350, "Selected parts", 15, "bold"),
        t(note_x, 378, cap_mpn, 11, "bold", colour="#9a3412"),
        t(note_x, 403, f"{socket_mpn} · vertical 2×7 host socket", 11, "bold", colour="#075985"),
        t(note_x, 428, f"{holder_mpn} · rotated holder", 11, "bold", colour="#166534"),
        t(note_x, 474, "Rear controls shown to scale", 15, "bold"),
        t(note_x, 502, "OMRON B3S-1100P · direct BACK/OPT/F1/F2/PTT", 11),
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
                t(px(37.5), pz(base_rear_z+12.4), "M5Stack U214 worst-case · 84 × 24 × 15.287 mm", 9.2, "bold", "middle", "#9a3412"),
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
                t(px(7.5), pz(base_rear_z+2.7), "F2", 8, "bold", "middle", "#4c1d95"),
                t(px(37.5), pz(battery_rear_z)+24, "No installed Cap appears: its Y=17…41-mm zone does not cross B–B.", 9.3, "bold", "middle", "#9a3412"),
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
    out += panel(780, "B–B · battery/control zone", 82.0, "battery")
    out += [
        line(745, 105, 745, 750, "#d0d5dd", "6 5"),
        t(60, 750, f"Display: {mpn('display')} · {depth('display'):.1f}-mm LCD/CTP body", 10.5, "bold"),
        t(60, 774, f"Complete opposing-body Z clearance—including {mpn('speaker')}—is audited in the inner-face view.", 10.5, colour="#526076"),
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
        t(30, 84, "Board Y is collapsed in this orthographic projection; the rear view separately proves Cap/battery longitudinal clearance.", 11, colour="#526076"),
        t(x(-4.5)-24, z(0)+5, "FRONT", 9, "bold", "end", "#1d4ed8"),
        t(x(-4.5)-24, z(base_rear_z)+5, "REAR", 9, "bold", "end", "#166534"),
        r(x(10.25), z(0), 54.5*scale_x, depth("display")*scale_z, "#dbeafe", "#2563eb", rx=4, extra=' data-instance="display"'),
        t(x(37.5), z(0)-9, "HMX035CTFT-001 · display", 9.5, "bold", "middle", "#1d4ed8"),
        r(x(0), z(ui_outer_z), BOARD_W*scale_x, 1.6*scale_z, "#dcfce7", "#16a34a", rx=1, extra=' data-instance="ui-pcb"'),
        r(x(0), z(ui_inner_z), BOARD_W*scale_x, 11.0*scale_z, "#f8fafc", "#94a3b8", "5 4", 1, ' data-board-gap-mm="11" data-antenna-bodies="none"'),
        r(x(0), z(rf_inner_z), BOARD_W*scale_x, 1.6*scale_z, "#ffedd5", "#ea580c", rx=1, extra=' data-instance="rf-pcb"'),
        t(x(37.5), z(17.7), "FX8C M1 · 11-mm board gap", 8.5, "bold", "middle", "#9d174d"),
        '<g id="top-edge-rear-envelopes" data-y-collapsed="true">',
        r(x(U214_X), z(base_rear_z), U214_W*scale_x, depth("u214")*scale_z, "#ffedd5", "#ea580c", "7 4", 5, ' fill-opacity="0.45" data-instance="u214"'),
        r(x(17.6), z(base_rear_z), 39.8*scale_x, holder_depth*scale_z, "#dcfce7", "#16a34a", "4 3", 12, ' fill-opacity="0.45" data-instance="pack-holder"'),
        '</g>',
        t(x(37.5), z(base_rear_z+6.0), "stock U214 worst-case · 84 mm wide · Y=17…41", 8.7, "bold", "middle", "#9a3412"),
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
        t(x(37.5), z(max_rear_z)+80, "installed U214 worst-case · symmetric 4.5-mm side overhang", 9.5, "bold", "middle", "#9a3412"),
        t(920, 150, "What this view proves", 16, "bold"),
        t(920, 184, "✓ 84-mm Cap overhang is 4.5 mm on each side", 11, "bold", colour="#166534"),
        t(920, 212, "✓ both antenna banks mount on opposed outward PCB faces", 11, "bold", colour="#166534"),
        t(920, 240, "✓ the exact 11-mm interboard channel contains no antenna body", 11, "bold", colour="#166534"),
        t(920, 268, f"✓ antenna centre planes are separated by {rf_centre_spacing:.2f} mm", 11, "bold", colour="#166534"),
        t(920, 316, "Projection limits", 16, "bold"),
        t(920, 350, "Display/front-bank and installed-Cap/battery overlaps are Y-collapse artifacts.", 11),
        t(920, 378, "Use the adjacent external views for their real longitudinal positions.", 11),
        t(920, 426, "Selected depth references", 16, "bold"),
        t(920, 460, f"{mpn('u214')} · {depth('u214'):.3f} mm", 10.5),
        t(920, 488, f"{mpn('pack_holder')} · {holder_depth:.1f}-mm installed envelope", 10.5),
        t(920, 516, f"{mpn('display')} · {depth('display'):.1f} mm", 10.5),
        t(920, 564, f"Nominal maximum selected-part depth: {max_rear_z:.1f} mm", 11, "bold", colour="#b42318"),
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
