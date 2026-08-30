#!/usr/bin/env python3
"""Validate and publish the exact H2-R2.0.3 Pack/Safety I2C boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/architecture/pack-safety-i2c-boundary-contract.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
PINOUT = ROOT / "hardware/architecture/h1-r2-dual-rp-pinout.json"
OUTPUT = ROOT / "hardware/architecture/generated/H2-R2-pack-safety-i2c-boundary.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(contract: dict[str, Any], devices: dict[str, Any], pinout: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("marker") != "H2-R2.0.3":
        errors.append("boundary marker must be H2-R2.0.3")
    if contract.get("status") != "reviewed_exact_factory_placeable_boundary":
        errors.append("boundary must be explicitly reviewed and factory-placeable")
    if contract.get("authority", {}).get("does_not_authorize") != [
        "R2 KiCad", "fabrication", "ordering"
    ]:
        errors.append("prerequisite closure must not authorize KiCad, fabrication or ordering")

    bus = contract.get("bus", {})
    if bus.get("maximum_clock_hz") != 400_000 or bus.get("hard_safety_dependency") is not False:
        errors.append("mailbox bus must remain 400 kHz and outside the hard-safety dependency")
    hub = {row["gpio"]: row for row in pinout.get("hub_rp", {}).get("pin_map", [])}
    for gpio, signal in ((42, "SDA"), (43, "SCL")):
        row = hub.get(gpio, {})
        if signal not in row.get("net", "") or "TCA9803DGKR" not in row.get("endpoint", ""):
            errors.append(f"Hub GPIO{gpio} must terminate at the exact TCA9803 {signal} path")

    buffer = contract.get("buffer", {})
    if (buffer.get("manufacturer"), buffer.get("mpn"), buffer.get("jlcpcb_part_number")) != (
        "Texas Instruments", "TCA9803DGKR", "C2687966"
    ):
        errors.append("exact TCA9803 manufacturer/MPN/JLC identity changed")
    expected_pins = {
        1: ("VCCA", "3V3_MAIN"), 2: ("SCLA", "HUB_SAFE_I2C_SCL_MAIN"),
        3: ("SDAA", "HUB_SAFE_I2C_SDA_MAIN"), 4: ("GND", "GND"),
        5: ("EN", "TCA9803_EN_INTERNAL_VCCA_PULLUP"),
        6: ("SDAB", "HUB_SAFE_I2C_SDA_AON"),
        7: ("SCLB", "HUB_SAFE_I2C_SCL_AON"), 8: ("VCCB", "AON_SAFE_3V3"),
    }
    actual_pins = {row["pin"]: (row["name"], row["net"]) for row in buffer.get("pin_topology", [])}
    if actual_pins != expected_pins:
        errors.append("TCA9803 VSSOP-8 pin topology changed")
    electrical = buffer.get("electrical_contract", {})
    for key, expected in (
        ("a_side_powered_off_state", "high impedance"),
        ("all_bus_pins_back_power_protection", True),
        ("b_side_external_pullups", "forbidden"),
        ("b_side_capacitance_pf_max", 400),
    ):
        if electrical.get(key) != expected:
            errors.append(f"TCA9803 electrical rule changed: {key}")
    if electrical.get("b_side_current_source_ma_typical", 99) > 6:
        errors.append("B-side current source exceeds the registered MSPM0 SDIO sink rating")

    factory = buffer.get("factory_surface", {})
    for key in ("stock", "available_order_quantity", "moq", "unit_price_usd_quantity_1"):
        if not isinstance(factory.get(key), (int, float)) or factory[key] <= 0:
            errors.append(f"TCA9803 factory route lacks positive {key}")
    if factory.get("assembly_type") != "SMT Assembly" or "Standard" not in factory.get("pcba_type", ""):
        errors.append("TCA9803 must remain on the JLCPCB Standard-PCBA SMT surface")

    required_devices = {
        "ti_tca9803_dgkr": ("TCA9803DGKR", "C2687966"),
        "uniroyal_0402wgf2201tce": ("UNI-ROYAL 0402WGF2201TCE", "C25879"),
        "samsung_cl05a105ka5nqnc": ("Samsung CL05A105KA5NQNC", "C52923"),
        "samsung_cl05b104ko5nnnc": ("Samsung CL05B104KO5NNNC", "C1525"),
    }
    registry = devices.get("devices", {})
    for key, (mpn, jlc) in required_devices.items():
        row = registry.get(key, {})
        joined = json.dumps(row, sort_keys=True)
        if row.get("mpn") != mpn or jlc not in joined:
            errors.append(f"device register lost exact {key}/{mpn}/{jlc}")

    term = contract.get("rail_local_termination", {})
    if term.get("main_a_side", {}).get("quantity") != 2:
        errors.append("A-side must retain exactly two MAIN-local pull-ups")
    if term.get("aon_b_side", {}).get("external_pullup_quantity") != 0:
        errors.append("B-side must not contain external pull-ups")
    decoupling = contract.get("decoupling", [])
    if sorted((row.get("rail"), row.get("value"), row.get("quantity")) for row in decoupling) != [
        ("3V3_MAIN", "1 uF", 1), ("3V3_MAIN", "100 nF", 1),
        ("AON_SAFE_3V3", "1 uF", 1), ("AON_SAFE_3V3", "100 nF", 1),
    ]:
        errors.append("both supplies require local 1-uF plus 100-nF decoupling")
    calculated = (
        factory.get("unit_price_usd_quantity_1", 0)
        + 2 * term.get("main_a_side", {}).get("unit_price_usd_quantity_1", 0)
        + sum(row.get("quantity", 0) * row.get("unit_price_usd_quantity_1", 0)
              for row in decoupling)
    )
    if abs(calculated - contract.get("exact_one_component_cost_usd", -1)) > 0.00001:
        errors.append("exact-one component cost does not equal the selected BOM")

    truth = {(row.get("main"), row.get("aon")): row.get("result", "")
             for row in contract.get("power_truth_table", [])}
    if set(truth) != {(0, 0), (0, 1), (1, 0), (1, 1)}:
        errors.append("power truth table must cover all four rail states")
    if "no Hub/main back-power" not in truth.get((0, 1), "") \
            or "no reverse power" not in truth.get((1, 0), ""):
        errors.append("truth table must prove isolation in both asymmetric power states")
    return errors


def build(contract: dict[str, Any] | None = None, devices: dict[str, Any] | None = None,
          pinout: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or load(CONTRACT)
    devices = devices or load(DEVICES)
    pinout = pinout or load(PINOUT)
    errors = validate(contract, devices, pinout)
    return {
        "schema_version": 1,
        "artifact": "H2-R2-pack-safety-i2c-boundary",
        "marker": contract.get("marker"),
        "status": "pass_reviewed_exact_boundary" if not errors else "fail",
        "source_sha256": {
            str(CONTRACT.relative_to(ROOT)): digest(CONTRACT),
            str(DEVICES.relative_to(ROOT)): digest(DEVICES),
            str(PINOUT.relative_to(ROOT)): digest(PINOUT),
        },
        "contract": contract,
        "errors": errors,
    }


def render(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(render(result), encoding="utf-8")
    print(render(result), end="")
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
