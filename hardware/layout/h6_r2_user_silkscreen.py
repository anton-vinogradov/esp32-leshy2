"""User labels bound to actual H6 interface positions, not H1 drawing pixels.

The inner faces keep assembly/package graphics but do not acquire duplicated
user labels. All coordinates returned here are in each native PCB's XY frame.
Mechanical validity and connector orientation are checked separately.
"""

from __future__ import annotations


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


def antenna_signal_findings(project: str, placed_rows: list[dict], contract: dict) -> list[dict]:
    """Validate actual pad nets; a correct label alone does not prove identity."""
    rows = {row["instance"]: row for row in placed_rows}
    errors = []
    for instance in contract.get("antenna_ports", {}).get(project, {}):
        path, _, expected = ANTENNA_INTERFACES[instance]
        row = rows.get(instance, {})
        actual = row.get("signal_pad_nets", [])
        if actual != [expected]:
            errors.append({"kind": "antenna_signal_identity_mismatch", "instance": instance,
                           "reference": row.get("reference"), "path": path,
                           "signal_pad": "1", "expected": expected, "actual": actual})
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
    for instance in contract.get("antenna_ports", {}).get(project, {}):
        _, text, _ = ANTENNA_INTERFACES[instance]
        # Bind to the physical RF port, not the independently ordered H1 silk
        # list. The native extractor supplies the actual footprint anchor.
        x = rows[instance]["footprint_anchor_mm"][0]
        add(instance, text, x, 15.2, role="antenna")

    for instance, spec in contract["service_buttons"]["by_project"][project].items():
        row = rows[instance]
        owner, action, _ = instance.rsplit("_", 2)
        x = 6.0 if spec["edge"] == "left" else width - 6.0
        y = row["courtyard_centre_mm"][1]
        add(instance, SERVICE_OWNERS[owner], x, y - 1.05)
        add(instance, "RST" if action == "reset" else "BOOT", x, y + 1.05)

    for instance, (owner, role) in USB_OWNERS.items():
        if instance not in rows:
            continue
        x = rows[instance]["courtyard_centre_mm"][0]
        # Shared rows above the bottom port bodies and their through-board tabs.
        add(instance, owner, x, 138.0)
        add(instance, role, x, 140.0)

    if project == "LESHY2-UI-R2":
        for instance, text in INDICATORS.items():
            x, y = rows[instance]["courtyard_centre_mm"]
            add(instance, text, x, y + 2.3)
        for n in range(1, 9):
            instance = f"ui_switch_f{n}"
            x, y = rows[instance]["courtyard_centre_mm"]
            add(instance, f"F{n}", x, y + 6.5)
        for instance, text, dy in (
            ("ui_switch_back", "BACK", -6.15),
            ("ui_switch_opt", "OPT", -6.15),
            ("ui_dpad_left", "LEFT", -6.15),
            ("ui_dpad_right", "RIGHT", -6.15),
            ("ui_dpad_down", "DOWN", 6.0),
        ):
            x, y = rows[instance]["courtyard_centre_mm"]
            add(instance, text, x, y + dy)
        x, y = rows["ui_dpad_up"]["courtyard_centre_mm"]
        add("ui_dpad_up", "UP", x + 7.5, y)
        # The centre gap contains the grounded solder tab of OK. Keep its label
        # in the lower-right opening, outside both OK and DOWN body/mask areas.
        x, y = rows["ui_dpad_ok"]["courtyard_centre_mm"]
        add("ui_dpad_ok", "OK", x + 6.5, y + 5.7)
        add("sd", "microSD", rows["sd"]["courtyard_centre_mm"][0], 140.0)
    else:
        add("unit_connector", "M5 UNIT", rows["unit_connector"]["courtyard_centre_mm"][0], 140.0)
        x, y = rows["ptt_switch"]["courtyard_centre_mm"]
        add("ptt_switch", "PTT", x, y + 6.5)
        x, y = rows["encoder"]["courtyard_centre_mm"]
        add("encoder", "ENC / OK", x, y + 10.0)
    return result


def add_to_board(board, project, placed_rows, contract, add_text, pcbnew):
    for row in labels(project, placed_rows, contract):
        add_text(board, row["text"], tuple(row["at_mm"]), pcbnew.F_SilkS,
                 row["size_mm"], row["thickness_mm"])
