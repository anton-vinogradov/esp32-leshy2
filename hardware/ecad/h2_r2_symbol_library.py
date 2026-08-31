#!/usr/bin/env python3
"""Generate the deterministic H2-R2.1.3 controlled KiCad symbol library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-symbol-library-contract.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def escaped(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def natural_key(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def effects(hide: bool = False, size: float = 1.27) -> str:
    hidden = " (hide yes)" if hide else ""
    return f"(effects (font (size {size:.2f} {size:.2f})){hidden})"


def property_block(key: str, value: object, x: float, y: float, hide: bool = False) -> list[str]:
    lines = [
        f'\t\t(property "{escaped(key)}" "{escaped(value)}"',
        f"\t\t\t(at {x:.2f} {y:.2f} 0)",
        "\t\t\t(show_name no)",
        "\t\t\t(do_not_autoplace no)",
    ]
    if hide:
        lines.append("\t\t\t(hide yes)")
    lines += [f"\t\t\t{effects()}", "\t\t)"]
    return lines


def reference_prefix(device_id: str, footprint: str) -> str:
    library = footprint.split(":", 1)[0]
    if library.startswith("Resistor"):
        return "R"
    if library.startswith("Capacitor"):
        return "C"
    if library.startswith("Inductor"):
        return "L"
    if library.startswith("Crystal"):
        return "Y"
    if library.startswith(("Diode", "LED")) or device_id.startswith("vishay_vsm"):
        return "D"
    if library.startswith("Connector") or any(
        token in device_id for token in ("gct_rfpc", "gct_usb", "hirose_", "jae_", "samtec_", "seeed_1125")
    ):
        return "J"
    if library.startswith(("Button_Switch", "Rotary_Encoder")) or device_id.startswith(("alps_", "ck_js", "omron_")):
        return "SW"
    if "fuse" in device_id or device_id.startswith("littelfuse_045"):
        return "F"
    if device_id.startswith(("diodes_2n", "diodes_dmn", "diodes_mmbt")):
        return "Q"
    if device_id == "keystone_1048p":
        return "BT"
    if device_id == "pui_as02404po":
        return "LS"
    if device_id == "same_sky_cmej_0413_42_smt_tr":
        return "MK"
    return "U"


def pin_rows(group: dict) -> list[dict]:
    pad_to_contacts: dict[str, list[dict]] = defaultdict(list)
    for contact in group["contacts"]:
        if contact["disposition"] != "pcb_footprint_pad":
            continue
        for pad in contact["pads"]:
            pad_to_contacts[pad].append(contact)
    result = []
    for pad in sorted(pad_to_contacts, key=natural_key):
        contacts = sorted(pad_to_contacts[pad], key=lambda row: row["contact"])
        names = [row["contact"] for row in contacts]
        roles = sorted({row["role"] for row in contacts})
        pin_type = "no_connect" if set(roles).issubset({"nc", "no_connect", "reserved"}) else "passive"
        result.append(
            {
                "number": pad,
                "name": "/".join(names),
                "contacts": names,
                "roles": roles,
                "type": pin_type,
            }
        )
    return result


def symbol_text(group: dict, ledger: dict) -> tuple[str, dict]:
    pins = pin_rows(group)
    midpoint = (len(pins) + 1) // 2
    left, right = pins[:midpoint], pins[midpoint:]
    rows = max(len(left), len(right), 2)
    top = (rows - 1) * 1.27
    half_height = max(5.08, rows * 1.27)
    half_width = 15.24
    pin_x = half_width + 5.08
    source = ledger.get("manufacturer_evidence") or {}
    external = [
        contact["contact"]
        for contact in group["contacts"]
        if contact["disposition"] == "external_on_module_interface"
    ]
    name = group["device_id"]
    prefix = reference_prefix(name, group["footprint"])
    lines = [
        f'\t(symbol "{escaped(name)}"',
        "\t\t(pin_names (offset 1.016))",
        "\t\t(exclude_from_sim no)",
        "\t\t(in_bom yes)",
        "\t\t(on_board yes)",
        "\t\t(in_pos_files yes)",
        "\t\t(duplicate_pin_numbers_are_jumpers no)",
    ]
    lines += property_block("Reference", prefix, 0, half_height + 2.54)
    lines += property_block("Value", group["mpn"], 0, -half_height - 2.54)
    lines += property_block("Footprint", group["footprint"], 0, 0, True)
    lines += property_block("Datasheet", source.get("url", "~"), 0, 0, True)
    lines += property_block("Description", ledger.get("role", "Leshy2 R2 exact component"), 0, 0, True)
    lines += property_block("Leshy2DeviceID", name, 0, 0, True)
    lines += property_block("ManufacturerEvidenceChecked", source.get("checked", "unknown"), 0, 0, True)
    lines += property_block("ExternalInterfaces", ",".join(external) or "none", 0, 0, True)
    lines += [
        f'\t\t(symbol "{escaped(name)}_0_1"',
        "\t\t\t(rectangle",
        f"\t\t\t\t(start {-half_width:.2f} {half_height:.2f})",
        f"\t\t\t\t(end {half_width:.2f} {-half_height:.2f})",
        "\t\t\t\t(stroke (width 0.254) (type default))",
        "\t\t\t\t(fill (type background))",
        "\t\t\t)",
        "\t\t)",
        f'\t\t(symbol "{escaped(name)}_1_1"',
    ]
    for side, side_pins in (("left", left), ("right", right)):
        for index, pin in enumerate(side_pins):
            x = -pin_x if side == "left" else pin_x
            y = top - index * 2.54
            angle = 0 if side == "left" else 180
            lines += [
                f"\t\t\t(pin {pin['type']} line",
                f"\t\t\t\t(at {x:.2f} {y:.2f} {angle})",
                "\t\t\t\t(length 5.08)",
                f'\t\t\t\t(name "{escaped(pin["name"])}" {effects()})',
                f'\t\t\t\t(number "{escaped(pin["number"])}" {effects()})',
                "\t\t\t)",
            ]
    lines += ["\t\t)", "\t\t(embedded_fonts no)", "\t)"]
    manifest = {
        "device_id": name,
        "symbol_id": f"Leshy2_R2:{name}",
        "reference_prefix": prefix,
        "value": group["mpn"],
        "footprint": group["footprint"],
        "pin_count": len(pins),
        "no_connect_pin_count": sum(pin["type"] == "no_connect" for pin in pins),
        "external_interfaces": external,
        "pin_map": pins,
    }
    return "\n".join(lines), manifest


def build() -> tuple[str, dict]:
    contract = load(CONTRACT)
    errors = []
    if (contract.get("marker"), contract.get("status")) != (
        "H2-R2.1.3",
        "current_controlled_symbol_library",
    ):
        errors.append("symbol-library contract identity changed")
    sources = {}
    loaded = {}
    for key, relative in contract["authority"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing symbol-library authority: {relative}")
            continue
        sources[key] = {"path": relative, "sha256": sha256(path)}
        loaded[key] = load(path)
    material = loaded.get("contact_materialization", {})
    ledger = loaded.get("exact_ledger", {})
    if material.get("status") != "pass" or ledger.get("status") != "pass":
        errors.append("upstream symbol sources are not passing")
    ledger_groups = {row["device_id"]: row for row in ledger.get("groups", [])}
    definitions = []
    symbols = []
    for group in sorted(material.get("groups", []), key=lambda row: row["device_id"]):
        ledger_row = ledger_groups.get(group["device_id"])
        if not ledger_row:
            errors.append(f"materialized group lost exact ledger row: {group['device_id']}")
            continue
        definition, manifest = symbol_text(group, ledger_row)
        definitions.append(definition)
        symbols.append(manifest)
    library = "\n".join(
        [
            "(kicad_symbol_lib",
            "\t(version 20251024)",
            '\t(generator "leshy2-h2-r2-symbol-library")',
            '\t(generator_version "1.0")',
            *definitions,
            ")",
            "",
        ]
    )
    symbol_ids = [row["symbol_id"] for row in symbols]
    if len(symbols) != 233 or len(set(symbol_ids)) != 233:
        errors.append("expected 233 unique controlled symbols")
    pin_count = sum(row["pin_count"] for row in symbols)
    if pin_count != 1610:
        errors.append(f"expected 1610 unique electrical-pad pins, got {pin_count}")
    external_count = sum(len(row["external_interfaces"]) for row in symbols)
    if external_count != 3:
        errors.append(f"expected three on-module external interfaces, got {external_count}")
    authorization = contract.get("authorization", {})
    if authorization != {
        "controlled_symbol_library": True,
        "native_schematic_nets": False,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }:
        errors.append("symbol-library authorization boundary changed")
    manifest = {
        "schema_version": 1,
        "artifact": "H2-R2-controlled-symbol-library",
        "marker": contract.get("marker"),
        "status": "pass" if not errors else "fail",
        "sources": sources,
        "library": {
            "id": contract.get("library_id"),
            "path": contract.get("output"),
            "sha256": sha256_bytes(library.encode("utf-8")),
            "symbol_count": len(symbols),
            "pin_count": pin_count,
            "external_interface_metadata_count": external_count,
        },
        "symbols": symbols,
        "authorization": authorization,
        "errors": errors,
    }
    return library, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = load(CONTRACT)
    output = ROOT / contract["output"]
    manifest_path = ROOT / contract["manifest"]
    library, manifest = build()
    if manifest["errors"]:
        for error in manifest["errors"]:
            print(f"ERROR: {error}")
        return 1
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        output.write_text(library, encoding="utf-8")
        manifest_path.write_text(manifest_text, encoding="utf-8")
        print(f"wrote {output.relative_to(ROOT)} and {manifest_path.relative_to(ROOT)}")
        return 0
    stale = []
    if not output.is_file() or output.read_text(encoding="utf-8") != library:
        stale.append(str(output.relative_to(ROOT)))
    if not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8") != manifest_text:
        stale.append(str(manifest_path.relative_to(ROOT)))
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: 233 controlled R2 symbols, 1610 exact pad pins, 3 external-interface metadata entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
