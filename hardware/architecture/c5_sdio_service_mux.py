#!/usr/bin/env python3
"""Validate and render the scoped C5 service-USB / four-bit-SDIO mux contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/architecture/c5-sdio-service-mux-contract.json"
DEVICES = REPO / "hardware/architecture/devices.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
OUTPUT = REPO / "hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json"


EXPECTED_C5_SIGNALS = {
    "SDIO_DAT1": ("GPIO7", 9),
    "SDIO_DAT0": ("GPIO8", 10),
    "SDIO_CLK": ("GPIO9", 11),
    "SDIO_CMD": ("GPIO10", 12),
    "SDIO_DAT3_USB_DM": ("GPIO13", 13),
    "SDIO_DAT2_USB_DP": ("GPIO14", 14),
}
EXPECTED_MUX_PINS = {
    1: ("VCC", "3V3_MAIN"),
    2: ("SEL", "C5_MUX_SEL"),
    3: ("D+", "C5_GPIO14_COMMON"),
    4: ("D-", "C5_GPIO13_COMMON"),
    5: ("GND", "POWER_GROUND"),
    6: ("HSD1-", "C5_SERVICE_USB_DM_BRANCH"),
    7: ("HSD1+", "C5_SERVICE_USB_DP_BRANCH"),
    8: ("HSD2-", "HUB_C5_SDIO_DAT3_BRANCH"),
    9: ("HSD2+", "HUB_C5_SDIO_DAT2_BRANCH"),
    10: ("OE", "C5_MUX_DISABLE"),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def build(contract: dict | None = None, devices: dict | None = None,
          h0: dict | None = None) -> dict:
    contract = contract or load(CONTRACT)
    devices = devices or load(DEVICES)
    h0 = h0 or load(H0)
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
    _error(errors, seen_signals == EXPECTED_C5_SIGNALS,
           "C5 fixed SDIO/USB signal-to-module-pad map is incomplete or wrong")

    seen_mux = {
        row.get("pin"): (row.get("name"), row.get("net"))
        for row in contract.get("mux", {}).get("pin_topology", [])
    }
    _error(errors, seen_mux == EXPECTED_MUX_PINS,
           "FSUSB42 MSOP-10 pin topology or branch polarity is wrong")
    truth = {
        (str(row.get("sel")), row.get("oe")): row.get("state")
        for row in contract.get("mux", {}).get("truth_table", [])
    }
    _error(errors, truth == {("0", 0): "SERVICE_USB", ("1", 0): "RUNTIME_SDIO", ("X", 1): "SAFE_DISCONNECTED"},
           "FSUSB42 SEL/OE truth table is not fail-safe")

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
    _error(errors, all("HSD2" in location and "disconnected" in location for location in muxed_pulls.values()),
           "DAT2/DAT3 pull-ups must be branch-local and disconnected in USB mode")
    usb_series = {row.get("signal"): row for row in conditioning.get("usb_series", [])}
    _error(errors, set(usb_series) == {"USB_DP", "USB_DM"}
           and all(row.get("initial_ohm") in {22, 33} and "HSD1" in row.get("location", "")
                   for row in usb_series.values()),
           "USB D+/D- require branch-local 22/33-ohm HSD1 series footprints")

    straps = {row.get("gpio"): row for row in contract.get("edge_straps", {}).get("contacts", [])}
    _error(errors, straps.get("GPIO25", {}).get("module_pad") == 26
           and straps.get("GPIO25", {}).get("latched_value") == 1,
           "GPIO25 must be module pad 26 and strap high for rising-edge sample")
    _error(errors, straps.get("GPIO3", {}).get("module_pad") == 5
           and straps.get("GPIO3", {}).get("latched_value") == 0,
           "GPIO3/MTDI must be module pad 5 and strap low for falling-edge drive")
    _error(errors, contract.get("edge_straps", {}).get("hold_after_c5_en_release_ms_min", 0) >= 3,
           "C5 strap levels must remain valid for at least 3 ms after EN release")

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
        "nexperia_74hc20pw_118": ("74HC20PW,118", "C546719"),
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
        3: ("Q_N", "C5_SERVICE_FREE_DIAG"),
        4: ("GND", "SAFETY_GROUND"),
        5: ("Q", "C5_SERVICE_OWNED"),
        6: ("CLR_N", "C5_SERVICE_CLEAR_N"),
        7: ("PRE_N", "SERVICE_VBUS_PRESENT_N"),
        8: ("VCC", "AON_SAFE_3V3"),
    }, "service ownership latch pin topology is incomplete or unsafe")
    qualifier_inputs = qualifier.get("used_gate", {}).get("inputs", [])
    _error(errors, qualifier_inputs == [
        "SERVICE_VBUS_PRESENT_N", "C5_EN_LOW_PROOF",
        "HUB_SDIO_HIGH_Z_PROOF", "AON_SERVICE_RELEASE_REQ",
    ] and qualifier.get("used_gate", {}).get("output") == "C5_SERVICE_CLEAR_N",
           "release qualifier must be the exact four-condition NAND")
    _error(errors, "SAFETY_GROUND" in qualifier.get("unused_gate", "")
           and "unconnected" in qualifier.get("unused_gate", ""),
           "unused 74HC20 gate must not float")
    _error(errors, detector.get("input_current_ua_nominal_at_5v", 100) <= 2.5
           and detector.get("gate_voltage_v_min_at_4v75_with_1pct_divider", 0) >= 2.35
           and "No semiconductor junction" in detector.get("proof", ""),
           "service-VBUS detector must remain high-impedance and junction-isolated")
    passive_key = {
        (row.get("mpn"), row.get("jlcpcb_part_number"), row.get("quantity"))
        for row in detector_latch.get("passives", [])
    }
    _error(errors, passive_key == {
        ("RC0402FR-071ML", "C138033", 2),
        ("RC0402FR-0710KL", "C60490", 1),
        ("CC0402KRX7R9BB104", "C131394", 2),
    }, "detector/latch passive population is not the accepted exact set")

    detector_latch_inventory_complete = all(
        component.get("live_inventory", {}).get(key) is not None
        for component in (detector, service_latch, qualifier)
        for key in ("stock", "available_order_quantity", "moq", "price_tiers_usd")
    ) and all(
        row.get(key) is not None
        for row in detector_latch.get("passives", [])
        for key in ("stock", "available_order_quantity", "moq", "unit_price_usd_quantity_1")
    )
    detector_latch_release_allowed = (
        detector_latch.get("selection_status") == "accepted"
        and detector_latch_inventory_complete
        and ownership.get("service_vbus", {}).get("detector_and_latch_mpn_status") == "accepted"
    )
    if detector_latch.get("selection_status") == "accepted":
        _error(errors, detector_latch_inventory_complete,
               "detector/latch cannot be accepted without complete live routes, MOQ and price")

    for name in ("runtime_to_service", "service_to_runtime"):
        sequence = contract.get("transition_sequences", {}).get(name, [])
        joined = " ".join(sequence)
        _error(errors, "mux OE high" in joined and "C5 EN low" in joined
               and "Hub" in joined and "high-impedance" in joined,
               f"{name} must reset C5, isolate the mux and prove Hub high-Z")

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
    _error(errors, candidate.get("manufacturer") == "onsemi"
           and candidate.get("mpn") == "FSUSB42MUX"
           and candidate.get("jlcpcb_part_number") == "C11355"
           and "Standard" in candidate.get("pcba_type", []),
           "factory candidate identity must remain exact onsemi FSUSB42MUX / C11355 / Standard PCBA")
    inventory = route.get("live_inventory", {})
    inventory_complete = all(inventory.get(key) is not None for key in (
        "stock", "available_order_quantity", "moq", "price_tiers_usd"
    ))
    if route.get("selection_status") == "accepted":
        _error(errors, inventory_complete,
               "production mux cannot be accepted without live stock/route, MOQ and price")
    production_release_allowed = route.get("selection_status") == "accepted" and inventory_complete

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
    if not production_release_allowed:
        open_gates.append("live JLC stock-or-explicit-route, MOQ and price for FSUSB42MUX/C11355")
    if not detector_latch_release_allowed:
        open_gates.append("exact factory-placeable service-VBUS detector/latch implementation")
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
        "detector_latch_release_allowed": detector_latch_release_allowed,
        "transition_sequences": contract.get("transition_sequences", {}),
        "performance": performance,
        "production_mux_route": route,
        "production_release_allowed": production_release_allowed,
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
