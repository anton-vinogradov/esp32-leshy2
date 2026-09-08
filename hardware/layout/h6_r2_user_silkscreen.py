"""User labels bound to actual H6 interface positions, not H1 drawing pixels.

The inner faces keep assembly/package graphics but do not acquire duplicated
user labels. All coordinates returned here are in each native PCB's XY frame.
Mechanical validity and connector orientation are checked separately.
"""

from __future__ import annotations

import math


def b3s_actuator_axis(row: dict) -> tuple[float, float]:
    """Omron nominal plunger axis in native PCB XY, never courtyard centre.

    The controlled footprint keeps the original electrical datum. The plunger
    lies at local (0, -0.92), midway between contact rows -3.17 and +1.33.
    KiCad flips local Y for a back-side footprint before its XY rotation.
    """
    if row["footprint"] != "Leshy2_R2:B3S-1100P":
        raise ValueError("B3S actuator datum requires the exact controlled footprint")
    if row["side"] not in {"F.Cu", "B.Cu"}:
        raise ValueError("B3S actuator datum requires an explicit native copper side")
    x, y = row["footprint_anchor_mm"]
    a = math.radians(row["rotation_deg"])
    local_y = -0.92 if row["side"] == "F.Cu" else 0.92
    return round(x + math.sin(a) * local_y, 6), round(y + math.cos(a) * local_y, 6)


SERVICE_OWNERS = {
    "s3": "S3", "c5": "C5", "hub_rp": "HUB", "rf_rp": "RF RP",
}
USB_OWNERS = {
    "hub_rp_service_usb_connector": ("HUB RP", "DATA USB"),
    "c5_service_usb_connector": ("C5", "DATA USB"),
    "rf_rp_service_usb_connector": ("RF RP", "DATA USB"),
    "product_usb_connector": ("S3", "POWER + USB"),
}
INDICATORS = {
    "s3_tx_led": "Wi-Fi/BLE", "c5_tx_led": "Wi-Fi/15.4",
    "nrf0_tx_led": "nRF24-1", "nrf1_tx_led": "nRF24-2", "nrf2_tx_led": "nRF24-3",
    "cc_tx_led": "SUB-GHz", "voice_tx_led": "V/U TX", "ir_tx_led": "IR",
    "ext_tx_led": "LORA/EXT", "fault_led": "FAULT",
}

# Electrical identity is independent of dictionary/list order or XY position.
# Each tuple is (H1 path identity, user label, signal-pad canonical net).
ANTENNA_INTERFACES = {
    "nrf0_external_sma": ("N24-0", "nRF1 · 2G4", "NRF0_EXTERNAL_RF_50R"),
    "s3_external_rp_sma": ("S3-2G4", "S3 · 2G4", "S3_EXTERNAL_RF_50R"),
    "nrf1_external_sma": ("N24-1", "nRF2 · 2G4", "NRF1_EXTERNAL_RF_50R"),
    "c5_external_rp_sma": ("C5-2G4/5", "C5 · 2G4/5G", "C5_EXTERNAL_RF_50R"),
    "nrf2_external_sma": ("N24-2", "nRF3 · 2G4", "NRF2_EXTERNAL_RF_50R"),
    "receiver_fmsw_external_sma": ("RX-FM/SW", "AIR/FM RX", "RX_FMSW_BOUNDARY_RF"),
    "receiver_amlw_external_sma": ("RX-AM/LW", "AM/LW RX", "RX_AMLW_BOUNDARY_RF"),
    "cc_external_sma": ("CC-SUB", "SUB-G TX", "CC_EXTERNAL_RF_50R"),
    "voice_external_sma": ("VOICE-UHF", "UHF TX", "VOICE_U_EXTERNAL_RF_50R"),
    "voice_v_external_sma": ("VOICE-VHF", "VHF TX", "VOICE_V_EXTERNAL_RF_50R"),
}

# This reviewed 5+5 interface scope must not shrink when a placement entry is
# accidentally removed. It is deliberately independent of antenna_ports.
ANTENNA_INSTANCES_BY_PROJECT = {
    "LESHY2-UI-R2": (
        "nrf0_external_sma", "s3_external_rp_sma", "nrf1_external_sma",
        "c5_external_rp_sma", "nrf2_external_sma",
    ),
    "LESHY2-RF-R2": (
        "receiver_fmsw_external_sma", "receiver_amlw_external_sma", "cc_external_sma",
        "voice_external_sma", "voice_v_external_sma",
    ),
}

# User-approved single-sentence notice, on the outward face of each PCB.
# This is a use instruction, not a certification or a liability waiver.
LEGAL_NOTICE_BY_PROJECT = {
    "LESHY2-UI-R2": "USE ONLY IN ACCORDANCE WITH APPLICABLE LAW",
    "LESHY2-RF-R2": "ИСПОЛЬЗОВАТЬ ТОЛЬКО В СООТВЕТСТВИИ С ЗАКОНОМ",
}


def antenna_instances(project: str, contract: dict) -> tuple[str, ...]:
    """Require the complete reviewed bank, independent of placement ordering."""
    if project not in ANTENNA_INSTANCES_BY_PROJECT:
        raise ValueError(f"unknown antenna project: {project}")
    expected = ANTENNA_INSTANCES_BY_PROJECT[project]
    actual = contract.get("antenna_ports", {}).get(project)
    if not isinstance(actual, dict) or set(actual) != set(expected):
        raise ValueError(f"antenna scope mismatch for {project}: expected {list(expected)}, actual {actual}")
    return expected


def antenna_signal_findings(project: str, placed_rows: list[dict], contract: dict,
                            canonical_to_kicad: dict) -> list[dict]:
    """Compare unmodified native pad nets with authoritative full-name bindings."""
    rows = {row["instance"]: row for row in placed_rows}
    errors = []
    try:
        instances = antenna_instances(project, contract)
    except ValueError as exc:
        errors.append({"kind": "antenna_scope_mismatch", "project": project, "detail": str(exc)})
        instances = ANTENNA_INSTANCES_BY_PROJECT.get(project, ())
    for instance in instances:
        path, _, canonical = ANTENNA_INTERFACES[instance]
        expected = canonical_to_kicad.get(canonical)
        if not isinstance(expected, str) or not expected:
            errors.append({"kind": "missing_antenna_net_binding", "instance": instance,
                           "canonical_net": canonical})
            continue
        row = rows.get(instance, {})
        actual = row.get("signal_pad_nets", [])
        if actual != [expected]:
            errors.append({"kind": "antenna_signal_identity_mismatch", "instance": instance,
                           "reference": row.get("reference"), "path": path,
                           "signal_pad": "1", "canonical_net": canonical,
                           "expected": expected, "actual": actual})
    return errors


def labels(project: str, placed_rows: list[dict], contract: dict) -> list[dict]:
    rows = {row["instance"]: row for row in placed_rows}
    result = []

    def add(instance, text, x, y, role="user"):
        row = rows[instance]
        result.append({
            "instance": instance, "reference": row["reference"],
            "text": text, "at_mm": [round(x, 4), round(y, 4)],
            "size_mm": 1.0, "thickness_mm": 0.15, "layer": "F.Silkscreen",
            "role": role,
        })

    width = contract["board"]["width_mm"]
    for instance in antenna_instances(project, contract):
        _, text, _ = ANTENNA_INTERFACES[instance]
        # Bind to the physical RF port, not the independently ordered H1 silk
        # list. The native extractor supplies the actual footprint anchor.
        x = rows[instance]["footprint_anchor_mm"][0]
        add(instance, text, x, 5.4, role="antenna")

    result.append({
        "instance": "board_legal_notice", "reference": None,
        "text": LEGAL_NOTICE_BY_PROJECT[project],
        "at_mm": [width / 2, 11.5],
        "size_mm": 1.0, "thickness_mm": 0.15, "layer": "F.Silkscreen",
        "role": "legal",
    })

    for instance, spec in contract["service_buttons"]["by_project"][project].items():
        row = rows[instance]
        owner, action, _ = instance.rsplit("_", 2)
        x = 6.0 if spec["edge"] == "left" else width - 6.0
        y = row["courtyard_centre_mm"][1]
        # The outward microphone body is next to RF BOOT. Keep this owner
        # caption on the BOOT axis but below the capsule; native stroke tests
        # cover both its primary maximum body and the through-board locator.
        owner_dy = -0.30 if project == "LESHY2-RF-R2" and instance == "rf_rp_boot_button" else -1.05
        add(instance, SERVICE_OWNERS[owner], x, y + owner_dy)
        add(instance, "RST" if action == "reset" else "BOOT", x, y + 1.05)

    for instance, (owner, role) in USB_OWNERS.items():
        if instance not in rows:
            continue
        x = rows[instance]["courtyard_centre_mm"][0]
        # Shared rows above the bottom port bodies and their through-board tabs.
        # The shared owner row clears B3S ground-pad mask at the HUB port by
        # >=0.15 mm with native glyph strokes; preserve the common role row.
        add(instance, owner, x, 138.2)
        add(instance, role, x, 140.0)

    if project == "LESHY2-UI-R2":
        for instance, text in INDICATORS.items():
            x, y = rows[instance]["courtyard_centre_mm"]
            add(instance, text, x, y + 2.3)
        for n in range(1, 9):
            instance = f"ui_switch_f{n}"
            x, y = b3s_actuator_axis(rows[instance])
            add(instance, f"F{n}", x, y + 6.5)
        for instance, text, dy in (
            ("ui_switch_back", "BACK", -6.15),
            ("ui_switch_opt", "OPT", -6.15),
            ("ui_dpad_left", "LEFT", -6.15),
            ("ui_dpad_right", "RIGHT", -6.15),
            ("ui_dpad_down", "DOWN", 6.0),
        ):
            x, y = b3s_actuator_axis(rows[instance])
            add(instance, text, x, y + dy)
        x, y = b3s_actuator_axis(rows["ui_dpad_up"])
        add("ui_dpad_up", "UP", x + 7.5, y)
        # The centre gap contains the grounded solder tab of OK. Keep its label
        # in the lower-right opening, outside both OK and DOWN body/mask areas.
        x, y = b3s_actuator_axis(rows["ui_dpad_ok"])
        add("ui_dpad_ok", "OK", x + 6.5, y + 5.7)
        add("sd", "microSD", rows["sd"]["courtyard_centre_mm"][0], 140.0)
    else:
        add("unit_connector", "M5 UNIT", rows["unit_connector"]["courtyard_centre_mm"][0], 140.0)
        x, y = b3s_actuator_axis(rows["ptt_switch"])
        add("ptt_switch", "PTT", x, y + 6.5)
        x, y = rows["encoder"]["courtyard_centre_mm"]
        add("encoder", "ENC / OK", x, y + 10.0)
    return result


def add_to_board(board, project, placed_rows, contract, add_text, pcbnew):
    for row in labels(project, placed_rows, contract):
        add_text(board, row["text"], tuple(row["at_mm"]), pcbnew.F_SilkS,
                 row["size_mm"], row["thickness_mm"])
