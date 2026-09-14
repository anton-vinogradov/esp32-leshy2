#!/usr/bin/env python3
"""Validate and render the scoped C5 service-USB / four-bit-SDIO mux contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/architecture/c5-sdio-service-mux-contract.json"
DEVICES = REPO / "hardware/architecture/devices.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
OUTPUT = REPO / "hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json"
CONTROL_MODEL = REPO / "hardware/verification/c5_mux_control_candidate.py"


EXPECTED_C5_SIGNALS = {
    "SDIO_DAT1": ("GPIO7", 9),
    "SDIO_DAT0": ("GPIO8", 10),
    "SDIO_CLK": ("GPIO9", 11),
    "SDIO_CMD": ("GPIO10", 12),
    "SDIO_DAT3_USB_DM": ("GPIO13", 13),
    "SDIO_DAT2_USB_DP": ("GPIO14", 14),
}
EXPECTED_MUX_PINS = {
    1: ("1D+", "C5_SERVICE_USB_DP_BRANCH"),
    2: ("1D-", "C5_SERVICE_USB_DM_BRANCH"),
    3: ("2D+", "HUB_C5_SDIO_DAT2_BRANCH"),
    4: ("2D-", "HUB_C5_SDIO_DAT3_BRANCH"),
    5: ("GND", "POWER_GROUND"),
    6: ("OE", "C5_MUX_DISABLE"),
    7: ("D-", "C5_GPIO13_COMMON"),
    8: ("D+", "C5_GPIO14_COMMON"),
    9: ("S", "C5_MUX_SEL_REQUEST"),
    10: ("VCC", "3V3_MAIN"),
}
EXPECTED_INPUTS = {
    "O": ("C5_SERVICE_OWNED", "c5_service_owner_latch.Q"),
    "R": ("C5_MUX_SEL_REQUEST", "evidence_mask.P12"),
    "A": ("C5_SERVICE_PATH_ACK", "evidence_mask.P13"),
    "L": ("AON_SERVICE_RELEASE_REQ", "evidence_mask.P14"),
    "P": ("RUN_PERMIT", None), "F": ("FAULT_ASSERT_N", None),
}
EXPECTED_EQUATIONS = {"SEL": "R", "VALID": "!(O&R)", "OE": "!(A&!(O&R)&P&F)", "HUB_HOLD": "O|L|!R"}
EXPECTED_INVERTERS = [
    {"instance": "c5_service_mux_logic_inverters", "gate": 1, "input": "C5_SERVICE_OWNED", "output": "C5_SERVICE_OWNER_NOT"},
    {"instance": "c5_service_mux_logic_inverters", "gate": 2, "input": "AON_SERVICE_RELEASE_REQ", "output": "C5_SERVICE_RELEASE_NOT"},
]
CLEAR_INPUTS = ["SERVICE_VBUS_PRESENT_N", "C5_EN_LOW_PROOF", "HUB_SDIO_HIGH_Z_PROOF", "AON_SERVICE_RELEASE_REQ"]
EXPECTED_NANDS = [
    {"instance": "c5_service_release_logic", "gate": 1, "inputs": CLEAR_INPUTS, "output": "C5_SERVICE_CLEAR_N"},
    {"instance": "c5_service_release_logic", "gate": 2, "inputs": ["C5_SERVICE_OWNED", "C5_MUX_SEL_REQUEST", "AON_SAFE_3V3", "AON_SAFE_3V3"], "output": "C5_SERVICE_PATH_VALID"},
    {"instance": "c5_service_path_logic", "gate": 1, "inputs": ["C5_SERVICE_PATH_ACK", "C5_SERVICE_PATH_VALID", "RUN_PERMIT", "FAULT_ASSERT_N"], "output": "C5_MUX_DISABLE"},
    {"instance": "c5_service_path_logic", "gate": 2, "inputs": ["C5_SERVICE_OWNER_NOT", "C5_SERVICE_RELEASE_NOT", "C5_MUX_SEL_REQUEST", "AON_SAFE_3V3"], "output": "C5_SERVICE_HUB_HOLD"},
]
QUALIFICATION_FIELDS = {
    "native_topology_verified", "full_temperature_levels_qualified", "voltage_ramps_qualified",
    "vbus_detector_latch_qualified", "switching_timing_qualified", "recovery_qualified", "production_release_allowed",
}


def positive_number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def route_complete(inventory: dict, checked_at: str | None = None) -> bool:
    """A documented acquisition route, NOT electrical or production acceptance."""
    if (not (inventory.get("checked_at") or checked_at)
            or inventory.get("currency") != "USD"
            or type(inventory.get("stock")) is not int or inventory["stock"] < 0
            or type(inventory.get("moq")) is not int or inventory["moq"] <= 0):
        return False
    if inventory.get("route") == "public JLCPCB stock":
        quantity = inventory.get("available_order_quantity")
        prices = inventory.get("price_tiers_usd")
        return (type(quantity) is int and inventory["stock"] >= quantity >= inventory["moq"]
                and isinstance(prices, list) and bool(prices)
                and all(type(row.get("minimum_quantity")) is int and row["minimum_quantity"] > 0
                        and positive_number(row.get("unit_price")) for row in prices))
    estimate = inventory.get("preorder_estimate", {})
    return (inventory.get("route") == "explicit JLCPCB Pre-order"
            and inventory["stock"] == 0 and inventory.get("available_order_quantity") is None
            and inventory.get("explicit_preorder_offered") is True
            and inventory.get("price_is_estimate") is True
            and "lead_time_days" in inventory and inventory["lead_time_days"] is None
            and inventory.get("price_tiers_usd") == []
            and positive_number(estimate.get("unit_price"))
            and type(estimate.get("minimum_quantity")) is int
            and estimate["minimum_quantity"] == inventory["moq"]
            and estimate.get("not_a_stocked_price_tier") is True)


def ordered_trace_errors(control: dict) -> list[str]:
    """Cross-check explicit event order; the model's waits remain unmeasured."""
    errors = []
    traces = control.get("ordered_traces", {})
    if set(traces) != {"runtime_to_service", "service_to_runtime"}:
        return ["both explicit ordered control traces are required"]
    spec = importlib.util.spec_from_file_location("c5_mux_order_witness", CONTROL_MODEL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    for name, destination in (("runtime_to_service", "usb"), ("service_to_runtime", "sdio")):
        try:
            events = []
            for row in traces[name]:
                if set(row) == {"controls"}:
                    values = row["controls"]
                    if len(values) != 6 or any(type(value) is not int or value not in (0, 1) for value in values):
                        raise ValueError("six literal binary O/R/A/L/P/F controls required")
                    events.append(module.Controls(*values))
                elif set(row) in ({"assumed_wait"}, {"assumed_wait", "duration_ms"}):
                    events.append(module.AssumedWait(row["assumed_wait"], row.get("duration_ms")))
                else:
                    raise ValueError("unknown event or measurement claim")
            result = module.check_sequence(events)
            required_waits = {"reset_and_pad_high_z", "mux_settle"}
            if destination == "sdio":
                required_waits.add("c5_strap_and_ready")
            if (result["errors"] or result["final_outputs"]["path"] != destination
                    or not required_waits.issubset({row["kind"] for row in result["conditional_waits"]})
                    or result["boundary"]["timing_qualified"] is not False
                    or result["boundary"]["production_topology_verified"] is not False):
                errors.append(f"{name}: ordered control trace lacks safe conditional sequencing")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{name}: malformed ordered control trace")
    return errors


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def build(contract: dict | None = None, devices: dict | None = None,
          h0: dict | None = None) -> dict:
    contract = load(CONTRACT) if contract is None else contract
    devices = load(DEVICES) if devices is None else devices
    h0 = load(H0) if h0 is None else h0
    errors: list[str] = []

    _error(errors, contract.get("contract_id") == "C5-SDIO-SERVICE-MUX-1",
           "unexpected C5 mux contract identity")
    device_id = contract.get("c5_module", {}).get("device_id")
    c5 = devices.get("devices", {}).get(device_id, {})
    _error(errors, c5.get("mpn") == contract.get("c5_module", {}).get("mpn"),
           "C5 exact module identity differs from devices.json")
    _error(errors, "SDIO_SLAVE_4BIT" in c5.get("controller_capabilities", []),
           "C5 device record does not expose the fixed four-bit SDIO slave")

    seen_signals: dict[str, tuple[str, int]] = {}
    for row in contract.get("c5_module", {}).get("signals", []):
        seen_signals[row.get("signal")] = (row.get("gpio"), row.get("module_pad"))
        contact = c5.get("contacts", {}).get(row.get("gpio"), {})
        _error(errors, contact.get("physical") == str(row.get("module_pad")),
               f"{row.get('gpio')} module pad differs from devices.json")
    _error(errors, len(contract.get("c5_module", {}).get("signals", [])) == 6
           and seen_signals == EXPECTED_C5_SIGNALS,
           "C5 fixed SDIO/USB signal-to-module-pad map is incomplete or wrong")

    seen_mux = {
        row.get("pin"): (row.get("name"), row.get("net"))
        for row in contract.get("mux", {}).get("pin_topology", [])
    }
    _error(errors, len(contract.get("mux", {}).get("pin_topology", [])) == 10
           and all(type(row.get("pin")) is int for row in contract.get("mux", {}).get("pin_topology", []))
           and seen_mux == EXPECTED_MUX_PINS,
           "TS3USB221E RSE ten-contact topology or branch polarity is wrong")
    mux = devices.get("devices", {}).get("ti_ts3usb221erser", {})
    registered_mux_pins = {key: row.get("physical") for key, row in mux.get("contacts", {}).items()}
    _error(errors, mux.get("mpn") == "TS3USB221ERSER" and registered_mux_pins == {
        "HSD1_PLUS": "1", "HSD1_MINUS": "2", "HSD2_PLUS": "3", "HSD2_MINUS": "4",
        "GND": "5", "OE": "6", "D_MINUS": "7", "D_PLUS": "8", "SEL": "9", "VCC": "10",
    }, "TS3USB221ERSER registered physical contacts differ")
    reference = contract.get("mux", {}).get("electrical_reference", {})
    _error(errors, reference.get("device_id") == "ti_ts3usb221erser"
           and reference.get("mpn") == "TS3USB221ERSER"
           and reference.get("recommended_supply_v") == mux.get("electrical_contract", {}).get("recommended_supply_v") == [2.3, 3.6]
           and reference.get("voltage_ramps_qualified") is False,
           "mux supply/reference must retain the unqualified ramp boundary")
    truth = {
        (str(row.get("sel")), row.get("oe")): row.get("state")
        for row in contract.get("mux", {}).get("truth_table", [])
    }
    _error(errors, len(contract.get("mux", {}).get("truth_table", [])) == 3
           and truth == {("0", 0): "SERVICE_USB", ("1", 0): "RUNTIME_SDIO", ("X", 1): "SAFE_DISCONNECTED"},
           "TS3USB221E SEL/OE truth table is wrong")

    conditioning = contract.get("branch_conditioning", {})
    series_signals = {row.get("signal") for row in conditioning.get("sdio_series", [])}
    pullup_signals = {row.get("signal") for row in conditioning.get("sdio_pullups", [])}
    _error(errors, series_signals == {"CLK", "CMD", "DAT0", "DAT1", "DAT2", "DAT3"},
           "every four-bit SDIO line must have its own series tuning footprint")
    _error(errors, pullup_signals == {"CMD", "DAT0", "DAT1", "DAT2", "DAT3"},
           "SDIO pull-ups must be fitted on CMD and DAT0..DAT3 only")
    clock_bias = conditioning.get("sdio_clock_bias", {})
    _error(errors, clock_bias.get("signal") == "CLK"
           and clock_bias.get("gpio") == "GPIO9"
           and clock_bias.get("fitted_pull") is None
           and "not populated" in clock_bias.get("dnp_footprint", ""),
           "SDIO CLK must have no fitted pull and retain only a DNP bias footprint")
    muxed_pulls = {
        row.get("signal"): row.get("location", "")
        for row in conditioning.get("sdio_pullups", []) if row.get("signal") in {"DAT2", "DAT3"}
    }
    _error(errors, all("2D" in location and "disconnected" in location for location in muxed_pulls.values()),
           "DAT2/DAT3 pull-ups must be branch-local and disconnected in USB mode")
    usb_series = {row.get("signal"): row for row in conditioning.get("usb_series", [])}
    _error(errors, set(usb_series) == {"USB_DP", "USB_DM"}
           and all(row.get("initial_ohm") in {22, 33} and "1D" in row.get("location", "")
                   for row in usb_series.values()),
           "USB D+/D- require branch-local 22/33-ohm port1 series footprints")

    straps = {row.get("gpio"): row for row in contract.get("edge_straps", {}).get("contacts", [])}
    _error(errors, straps.get("GPIO25", {}).get("module_pad") == 26
           and straps.get("GPIO25", {}).get("latched_value") == 1,
           "GPIO25 must be module pad 26 and strap high for rising-edge sample")
    _error(errors, straps.get("GPIO3", {}).get("module_pad") == 5
           and straps.get("GPIO3", {}).get("latched_value") == 0,
           "GPIO3/MTDI must be module pad 5 and strap low for falling-edge drive")
    _error(errors, contract.get("edge_straps", {}).get("hold_after_c5_en_release_ms_min", 0) >= 3,
           "C5 strap levels must remain valid for at least 3 ms after EN release")
    boot = contract.get("boot_straps", {})
    _error(errors, boot.get("contacts") == [
        {"gpio": "GPIO27", "module_pad": 18, "net": "C5_GPIO27_FIXED_HIGH", "pullup_ohm": 10000},
        {"gpio": "GPIO28", "module_pad": 15, "net": "C5_BOOT_N", "pullup_ohm": 10000, "button_series_ohm": 1000},
    ] and boot.get("joint_download_boot_0") == {"GPIO27": 1, "GPIO28": 0}
           and boot.get("application_boot") == {"GPIO27": 1, "GPIO28": 1}
           and type(boot.get("hold_after_en_release_ms_min")) is int
           and boot["hold_after_en_release_ms_min"] == 3
           and boot.get("sampled_levels_and_timing_qualified") is False
           and c5.get("contacts", {}).get("GPIO27", {}).get("physical") == "18"
           and c5.get("contacts", {}).get("GPIO28", {}).get("physical") == "15",
           "C5 BOOT GPIO27/28 topology, 3-ms hold or unqualified boundary changed")

    ownership = contract.get("ownership", {})
    latch = ownership.get("latch", {})
    _error(errors, latch.get("firmware_cannot_override") is True,
           "service ownership must be enforced by hardware, not firmware")
    _error(errors, "service VBUS present" in latch.get("asynchronous_set", ""),
           "service VBUS must asynchronously seize mux ownership")
    _error(errors, {row.get("state") for row in ownership.get("states", [])}
           == {"SAFE_DISCONNECTED", "SERVICE_USB", "RUNTIME_SDIO"},
           "ownership state machine must contain exactly the three safe states")
    _error(errors, "board power input" in ownership.get("service_vbus", {}).get("forbidden", []),
           "service VBUS must remain sense-only")
    control = ownership.get("control_mapping", {})
    _error(errors, {key: (row.get("net"), row.get("source"))
                    for key, row in control.get("inputs", {}).items()} == EXPECTED_INPUTS
           and control.get("equations") == EXPECTED_EQUATIONS,
           "O/R/A/L/P/F mapping or control equations differ")
    _error(errors, control.get("inverters") == EXPECTED_INVERTERS
           and control.get("nand_gates") == EXPECTED_NANDS
           and control.get("nand_device_id") == "ti_sn74lv20apwr"
           and type(control.get("nand_package_count")) is int and control["nand_package_count"] == 2
           and control.get("nand_supply") == "AON_SAFE_3V3"
           and control.get("nand_unconnected_pins") == [3, 11]
           and control.get("owner_q_n_used") is False,
           "control requires two exact LV NAND packages and U17 NOT(O)/NOT(L), never raw Q_N")
    _error(errors, control.get("reset_sinks") == {
        "c5_service_reset_sink.G": "C5_MUX_DISABLE",
        "c5_service_hub_reset_sink.G2": "C5_SERVICE_HUB_HOLD",
        "c5_service_hub_reset_sink.G1": "C5_RESET_KILL_GATE",
    } and control.get("independent_kill_fault_sinks_preserved") is True
           and control.get("kill_policy_changed") is False
           and control.get("firmware_service_manager_implemented") is False,
           "reset-sink identity, unchanged KILL or unimplemented service-manager boundary changed")
    _error(errors, "force mux SEL low" not in latch.get("service_override", [])
           and "keep SEL equal to R without an asynchronous branch change" in latch.get("service_override", []),
           "service ownership must veto the connection, not asynchronously change SEL")
    _error(errors, control.get("boolean_model") == "hardware/verification/c5_mux_control_candidate.py",
           "control-order witness source is not the reviewed finite model")
    errors.extend(ordered_trace_errors(control))
    qualification = contract.get("qualification", {})
    _error(errors, set(qualification) == QUALIFICATION_FIELDS
           and all(value is False for value in qualification.values()),
           "schematic contract must not claim native, electrical, timing, recovery or production qualification")

    detector_latch = ownership.get("detector_latch_implementation", {})
    detector = detector_latch.get("detector", {})
    service_latch = detector_latch.get("latch", {})
    qualifier = detector_latch.get("release_qualifier", {})
    exact_logic = {
        detector.get("device_id"): (detector.get("mpn"), detector.get("jlcpcb_part_number")),
        service_latch.get("device_id"): (service_latch.get("mpn"), service_latch.get("jlcpcb_part_number")),
        qualifier.get("device_id"): (qualifier.get("mpn"), qualifier.get("jlcpcb_part_number")),
    }
    _error(errors, exact_logic == {
        "diodes_dmn2056u_7": ("DMN2056U-7", "C332302"),
        "ti_sn74lvc1g74_dcur": ("SN74LVC1G74DCUR", "C70285"),
        "ti_sn74lv20apwr": ("SN74LV20APWR", "C2862070"),
    }, "service-VBUS detector, latch or release-qualifier identity is not exact")
    for device_id, (mpn, _) in exact_logic.items():
        registered = devices.get("devices", {}).get(device_id, {})
        registered_mpn = registered.get("mpn", "")
        _error(errors, registered_mpn == mpn or registered_mpn.endswith(f" {mpn}"),
               f"{device_id} exact MPN differs from devices.json")

    latch_pins = {
        row.get("pin"): (row.get("name"), row.get("net"))
        for row in service_latch.get("pin_topology", [])
    }
    _error(errors, latch_pins == {
        1: ("CLK", "SAFETY_GROUND"),
        2: ("D", "SAFETY_GROUND"),
        3: ("Q_N", None),
        4: ("GND", "SAFETY_GROUND"),
        5: ("Q", "C5_SERVICE_OWNED"),
        6: ("CLR_N", "C5_SERVICE_CLEAR_N"),
        7: ("PRE_N", "SERVICE_VBUS_PRESENT_N"),
        8: ("VCC", "AON_SAFE_3V3"),
    }, "service ownership latch pin topology is incomplete or unsafe")
    qualifier_inputs = qualifier.get("used_gate", {}).get("inputs", [])
    _error(errors, qualifier_inputs == CLEAR_INPUTS
           and qualifier.get("used_gate", {}).get("output") == "C5_SERVICE_CLEAR_N",
           "release qualifier must be the exact four-condition NAND")
    _error(errors, qualifier.get("quantity") == 2 and qualifier.get("instances") == [
        "c5_service_release_logic", "c5_service_path_logic"],
        "two LV NAND packages must cover all four assigned gates")
    lv = devices.get("devices", {}).get("ti_sn74lv20apwr", {})
    _error(errors, {name: row.get("physical") for name, row in lv.get("contacts", {}).items()} == {
        "1A": "1", "1B": "2", "NC_3": "3", "1C": "4", "1D": "5", "1Y": "6", "GND": "7",
        "2Y": "8", "2A": "9", "2B": "10", "NC_11": "11", "2C": "12", "2D": "13", "VCC": "14",
    }, "SN74LV20APWR physical package map differs")
    _error(errors, detector.get("input_current_ua_nominal_at_5v") == 2.5
           and detector.get("gate_voltage_v_resistor_only_min_at_4v75_with_1pct_divider") == 2.35125
           and detector.get("resistor_only_bound_excludes") == ["gate leakage", "temperature", "VBUS ramp", "detector and latch propagation"]
           and detector.get("full_electrical_detection_qualified") is False
           and "gate_voltage_v_min_at_4v75_with_1pct_divider" not in detector,
           "service-VBUS divider is a resistor-only calculation, not detector qualification")
    passive_key = {
        (row.get("mpn"), row.get("jlcpcb_part_number"), row.get("quantity"))
        for row in detector_latch.get("passives", [])
    }
    _error(errors, passive_key == {
        ("RC0402FR-071ML", "C138033", 2),
        ("RC0402FR-0710KL", "C60490", 1),
        ("CC0402KRX7R9BB104", "C131394", 3),
    }, "detector/latch passive population is not the accepted exact set")

    detector_latch_inventory_complete = all(
        route_complete(component.get("live_inventory", {}),
                       None if component is qualifier else "2026-08-30T13:36:59+03:00")
        and component.get("assembly_type") == "SMT Assembly"
        and component.get("part_class") == "Extended"
        and "Standard" in component.get("pcba_type", [])
        for component in (detector, service_latch, qualifier)
    ) and all(
        row.get(key) is not None
        for row in detector_latch.get("passives", [])
        for key in ("stock", "available_order_quantity", "moq", "unit_price_usd_quantity_1")
    )
    detector_latch_schematic_allowed = (
        detector_latch.get("selection_status") == "accepted"
        and detector_latch.get("selection_scope") == "engineering_schematic_only"
        and detector_latch.get("production_release_allowed") is False
        and detector_latch_inventory_complete
        and ownership.get("service_vbus", {}).get("detector_and_latch_mpn_status") == "accepted"
    )
    if detector_latch.get("selection_status") == "accepted":
        _error(errors, detector_latch_inventory_complete,
               "detector/latch schematic selection requires complete stock or explicit Pre-order routes, MOQ and price")
    _error(errors, detector_latch.get("selection_scope") == "engineering_schematic_only"
           and detector_latch.get("production_release_allowed") is False,
           "detector/latch procurement must not authorize production")

    for name in ("runtime_to_service", "service_to_runtime"):
        sequence = contract.get("transition_sequences", {}).get(name, [])
        joined = " ".join(sequence)
        _error(errors, "mux OE high" in joined and "C5 EN low" in joined
               and "Hub" in joined and "high-impedance" in joined,
               f"{name} must reset C5, isolate the mux and prove Hub high-Z")
        _error(errors, "AssumedWait reset_and_pad_high_z" in joined
               and "AssumedWait mux_settle" in joined
               and "wait at least 1 microsecond" not in joined,
               f"{name} requires explicit unmeasured reset/high-Z and settle premises")
    runtime_sequence = " ".join(contract.get("transition_sequences", {}).get("service_to_runtime", []))
    _error(errors, "AssumedWait c5_strap_and_ready" in runtime_sequence
           and "Only then write and confirm L=0" in runtime_sequence
           and "while releasing Hub RUN" not in runtime_sequence,
           "Hub must remain held until the C5 strap-and-ready premise")

    performance = contract.get("performance", {})
    _error(errors, performance.get("bus_width_bits") == 4,
           "performance contract must remain four-bit")
    _error(errors, performance.get("bringup_clock_hz") == 20_000_000
           and performance.get("bringup_raw_mb_s") == 10.0,
           "20 MHz bring-up raw rate must be 10.0 MB/s")
    _error(errors, performance.get("target_clock_hz") == 40_000_000
           and performance.get("target_raw_mb_s") == 20.0,
           "40 MHz target raw rate must be 20.0 MB/s")
    _error(errors, performance.get("qualified_payload_floor_mb_s") == 7.5
           and performance.get("qualification_frequency_hz") == 40_000_000,
           "7.5 MB/s acceptance must be qualified at 40 MHz, not at bring-up speed")

    route = contract.get("production_mux_route", {})
    candidate = route.get("candidate", {})
    _error(errors, candidate.get("manufacturer") == "Texas Instruments"
           and candidate.get("mpn") == "TS3USB221ERSER"
           and candidate.get("jlcpcb_part_number") == "C129313"
           and candidate.get("assembly_type") == "SMT Assembly"
           and candidate.get("part_class") == "Extended"
           and "Standard" in candidate.get("pcba_type", []),
           "factory candidate must be exact TI TS3USB221ERSER / C129313 / SMT Standard PCBA")
    inventory = route.get("live_inventory", {})
    inventory_complete = route_complete(inventory)
    if route.get("selection_status") == "accepted":
        _error(errors, inventory_complete,
               "mux schematic selection requires a complete live stock/route, MOQ and price")
    _error(errors, route.get("selection_scope") == "engineering_schematic_only"
           and route.get("production_release_allowed") is False,
           "mux procurement must not authorize production")
    mux_schematic_allowed = route.get("selection_status") == "accepted" and inventory_complete

    h0_link = next((row for row in h0.get("transport_contracts", []) if row.get("id") == "HUB_C5"), {})
    h0_integration = {
        "native_four_bit_declared": h0_link.get("transport") == "native C5 4-bit SDIO",
        "current_clock_hz": h0_link.get("clock_hz"),
        "current_raw_mb_s": h0_link.get("raw_payload_mb_s"),
        "current_qualified_floor_mb_s": h0_link.get("qualified_payload_floor_mb_s"),
        "bringup_matches": h0_link.get("bringup_clock_hz") == performance.get("bringup_clock_hz"),
        "target_clock_explicit": h0_link.get("clock_hz") == performance.get("target_clock_hz"),
        "hil_frequency_semantics_explicit": "40 MHz" in h0_link.get("service_mux", ""),
    }
    _error(errors, h0_integration["native_four_bit_declared"],
           "H0-R2 no longer declares native four-bit C5 SDIO")

    open_gates: list[str] = []
    if not mux_schematic_allowed:
        open_gates.append("live JLC stock-or-explicit-route, MOQ and price for TS3USB221ERSER/C129313")
    if not detector_latch_schematic_allowed:
        open_gates.append("exact factory-placeable service-VBUS detector/latch implementation")
    open_gates.extend([
        "SN74LV20APWR Pre-order lead time and final quote; recheck all exact routes at freeze and before order",
        "native endpoint binding, full-temperature output loading and reset-low proof",
        "MAIN/AON ramps and VBUS detector/latch asynchronous hazards",
        "ordered Safety service manager, measured waits, unchanged KILL/update conflict and physical recovery",
        "USB/SDIO signal integrity and 7.5 MB/s at 40 MHz HIL",
    ])
    if not h0_integration["target_clock_explicit"] or not h0_integration["hil_frequency_semantics_explicit"]:
        open_gates.append("top-level H0 promotion of 40 MHz target and 7.5 MB/s-at-40-MHz semantics")

    return {
        "schema_version": 1,
        "artifact": "H0-R2-c5-sdio-service-mux",
        "status": (
            "fail" if errors else
            "pass_scoped_contract_open_gates" if open_gates else
            "pass_scoped_contract"
        ),
        "contract_id": contract.get("contract_id"),
        "c5_signal_map": contract.get("c5_module", {}).get("signals", []),
        "mux_pin_topology": contract.get("mux", {}).get("pin_topology", []),
        "branch_conditioning": conditioning,
        "edge_straps": contract.get("edge_straps", {}),
        "ownership": ownership,
        "detector_latch_schematic_selection_allowed": detector_latch_schematic_allowed and not errors,
        "detector_latch_release_allowed": False,
        "transition_sequences": contract.get("transition_sequences", {}),
        "performance": performance,
        "production_mux_route": route,
        "mux_schematic_selection_allowed": mux_schematic_allowed and not errors,
        "production_release_allowed": False,
        "boot_straps": boot,
        "qualification": qualification,
        "h0_integration": h0_integration,
        "open_gates": open_gates,
        "errors": errors,
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    content = render(result)
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    print("ok: C5 service-USB / four-bit-SDIO scoped contract is deterministic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
