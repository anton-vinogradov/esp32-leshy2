#!/usr/bin/env python3
"""Generate and verify H2.4.4 LoRa Cap power and identity sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_s3_core import Pin, effects, escaped, library_symbol, schematic_symbol, stable_uuid


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
ACCESSORY_PATH = REPO / "hardware/accessories/leshy2-lora-cap-01.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-CAP00-root-interface.json"
SHEET_ID = "CAP_20_POWER_BUS"
PROJECT_ID = "LESHY2-LORA-CAP-01"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-CAP20-power-bus.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "CAP20"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    pins = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if number is None:
            match = re.match(r"^(\d+)", str(row.get("physical", "")))
            if not match:
                raise ValueError(f"no physical pin number for {instance}.{contact}")
            number = match.group(1)
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate CAP20 physical contacts in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    if instance in {"local_regulator", "identity"}:
        return "Package_TO_SOT_SMD:SOT-23-5"
    if device_key.startswith(("tdk_c1608", "murata_grm188")):
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("yageo_rc0402"):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact CAP20 footprint for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        return "C"
    if device_key.startswith("yageo_rc"):
        return "R"
    return "U"


def endpoint_nets(accessory: dict, local_instances: set[str]) -> dict[tuple[str, str], str]:
    found: dict[tuple[str, str], set[str]] = defaultdict(set)
    for route in accessory["fixed_routes"]:
        for endpoint in (route["from"], route["to"]):
            if endpoint.startswith("abstract:") or "." not in endpoint:
                continue
            instance, contact = endpoint.split(".", 1)
            if instance in local_instances:
                found[(instance, contact)].add(route["net"])
    explicit = {
        ("local_regulator", "GND"): "GND",
        ("local_regulator", "NC"): "NO_CONNECT",
        ("local_regulator", "OUT"): "CAP_3V3",
        ("local_regulator_input", "END_1"): "5V_IN",
        ("local_regulator_input", "END_2"): "GND",
        ("local_regulator_output", "END_1"): "CAP_3V3",
        ("local_regulator_output", "END_2"): "GND",
        ("radio_bulk", "END_1"): "CAP_3V3",
        ("radio_bulk", "END_2"): "GND",
        ("identity", "VSS"): "GND",
        ("identity", "VCC"): "CAP_3V3",
        ("identity", "NC"): "NO_CONNECT",
        ("identity_bypass", "END_1"): "CAP_3V3",
        ("identity_bypass", "END_2"): "GND",
    }
    for endpoint, net in explicit.items():
        found[endpoint].add(net)
    result = {}
    for endpoint, nets in found.items():
        meaningful = {net for net in nets if net != "NO_CONNECT"}
        if len(meaningful) > 1:
            raise ValueError(f"one CAP20 endpoint has multiple nets: {endpoint} -> {sorted(meaningful)}")
        result[endpoint] = next(iter(meaningful), "NO_CONNECT")
    return result


def build() -> tuple[dict[Path, str], dict]:
    accessory = json.loads(ACCESSORY_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 8:
        raise ValueError(f"{SHEET_ID} must own eight ledger rows, got {len(rows)}")
    interface_order = list(next(row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID))
    interfaces = set(interface_order)
    if interfaces != {"5V_IN", "GND", "CAP_3V3", "IDENTITY_SCL", "IDENTITY_SDA"}:
        raise ValueError(f"CAP20 interface drifted: {sorted(interfaces)}")
    endpoints = endpoint_nets(accessory, {row["instance"] for row in rows})

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
        prefix = reference_prefix(row["instance"], row["device_key"])
        ref_counts[prefix] += 1
        specs.append({
            "instance": row["instance"], "device_key": row["device_key"],
            "mpn": row["mpn"], "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"]),
        })

    library_defs = []
    placements = {}
    column_x = [45.72, 111.76, 177.80, 243.84]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789")
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            True, True, True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        column = min(range(len(cursor_y)), key=lambda item: cursor_y[item])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - remainder) / 2.54) * 2.54 + remainder
        cursor_y[column] = y + height / 2 + 15.24
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A2")', "\t(title_block",
        '\t\t(title "Leshy2 LoRa Cap — 5-V to low-noise 3.3-V power and identity")',
        '\t\t(rev "H2.4.4")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords, True, True,
            SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
        ))
        for pin in spec["pins"]:
            net = endpoints.get((spec["instance"], pin.contact), "NO_CONNECT")
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used = set()
    no_connects = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")', "\t)",
                ]
                no_connects.append(f"{instance}.{pin.contact}")
                continue
            hierarchical = net in interfaces and net not in hierarchy_used
            if hierarchical:
                hierarchy_used.add(net)
            token = "hierarchical_label" if hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if hierarchical else ""
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            lines += [
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})", f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")', "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(f"CAP20 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")
    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    schematic = "\n".join(lines)
    generated = {
        OUTPUT_SCH: schematic,
        SYMBOL_LIBRARY: build_symbol_library({OUTPUT_SCH: schematic}),
    }
    manifest = {
        "schema_version": 1,
        "stage": "H2.4.4",
        "status": "reviewed_exact_lora_power_identity_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (ACCESSORY_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs),
            "physical_package_contacts": sum(len(spec["pins"]) for spec in specs),
            "hierarchical_interfaces": len(interfaces),
            "intentional_no_connect_pins": len(no_connects),
            "custom_footprints": 0,
            "local_regulator_output_v": 3.3,
            "local_regulator_max_output_ma": 300,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"], "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": True,
            }
            for spec in specs
        ],
        "intentional_no_connect_endpoints": sorted(no_connects),
        "electrical_contract": {
            "input": "host-protected 5V_IN",
            "regulator": "TPS7A2033PDBVR fixed 3.3 V, EN tied to input, smart pulldown and 300-mA rating",
            "input_decoupling": "1 uF X7R at IN",
            "output_decoupling": "1 uF X7R at OUT plus 10 uF local radio bulk",
            "identity": "24AA02UIDT-I/OT factory 32-bit serial number over 3.3-V 400-kHz I2C",
            "identity_security": "convenience identity only; never authorization",
            "i2c_pullups": "independent 2.2-kOhm pull-ups to CAP_3V3",
        },
        "review_boundary": {
            "complete": [
                "all 5-V input, enable, ground, fixed 3.3-V output and regulator NC contacts are explicit",
                "minimum input/output capacitance, local radio bulk and identity bypass are explicit",
                "EEPROM power, ground, SCL, SDA, local pull-ups and NC are explicit",
                "every fitted part uses an exact serial MPN and matching stock package footprint",
                "native KiCad parses CAP20 and the complete live LoRa Cap hierarchy with exact findings only",
            ],
            "deferred": [
                "power-plane placement, regulator thermal copper, decoupling loop and I2C routing in H6",
                "inrush, 5-V droop, 3.3-V ripple, peak TX current and identity HIL in H8",
                "factory identity provisioning policy remains firmware/product work and never grants TX authority",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 8,
        "schematic_symbols": 8,
        "board_fitted_symbols": 8,
        "physical_package_contacts": 22,
        "hierarchical_interfaces": 5,
        "intentional_no_connect_pins": 2,
        "custom_footprints": 0,
        "local_regulator_output_v": 3.3,
        "local_regulator_max_output_ma": 300,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.4.4 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 8 or schematic.count("\n\t(hierarchical_label \"") != 5:
        raise ValueError("CAP20 symbol/interface accounting mismatch")
    if set(manifest["intentional_no_connect_endpoints"]) != {"identity.NC", "local_regulator.NC"}:
        raise ValueError(f"CAP20 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if any(not row["footprint"] for row in manifest["instances"]):
        raise ValueError("CAP20 fitted component lacks footprint")


def kicad_check() -> None:
    result = subprocess.run(
        ["python3", str(ECAD / "h2_lora_cap_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected CAP20 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.4.4 and the live LoRa Cap hierarchy")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--kicad-check", action="store_true")
    args = parser.parse_args()
    generated, manifest = build()
    structural_check(generated, manifest)
    if args.write:
        for path, content in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
        root = subprocess.run(
            ["python3", str(ECAD / "h2_lora_cap_root.py"), "--write"],
            cwd=REPO, text=True, capture_output=True,
        )
        if root.returncode:
            raise RuntimeError(f"failed to refresh LoRa Cap hierarchy:\n{root.stdout}{root.stderr}")
        print(root.stdout, end="")
    else:
        stale = [
            path for path, content in generated.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print("ok: H2.4.4 LoRa Cap power/identity sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
