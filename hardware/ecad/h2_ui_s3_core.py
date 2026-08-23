#!/usr/bin/env python3
"""Generate and verify the exact H2.2.2 S3 core schematic sheet.

The generator consumes the reviewed architecture, the exact device register,
the H2 instance ledger and the live UI hierarchy contract.  It deliberately
models all 41 carrier-PCB pads of ESP32-S3-WROOM-1U-N16R8; the factory U.FL is
recorded as an assembly interface and is never invented as a 42nd PCB pad.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_10_S3_CORE_MEMORY_BOOT"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI10-S3-core.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
FOOTPRINT_DIR = ECAD / "libraries/Leshy2.pretty"
NAMESPACE = uuid.UUID("a33c87a8-78d9-43bc-9d39-e6af5d07f54d")


@dataclass(frozen=True)
class Pin:
    number: str
    name: str
    contact: str


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheet_reference_base(sheet_id: str) -> int:
    """Reserve a collision-free 1000-reference block per project sheet."""
    match = re.search(r"(?:UI|RF|CAP)_(\d+)", sheet_id)
    return int(match.group(1)) * 1000 if match else 0


def scoped_reference(sheet_id: str, reference: str) -> str:
    match = re.fullmatch(r"([A-Z]+)(\d+)", reference)
    if not match:
        raise ValueError(f"cannot scope malformed schematic reference: {reference}")
    return f"{match.group(1)}{sheet_reference_base(sheet_id) + int(match.group(2))}"


class ScopedReferenceCounter(Counter[str]):
    """Counter whose first generated number begins in the sheet's block."""

    def __init__(self, sheet_id: str):
        super().__init__()
        self.base = sheet_reference_base(sheet_id)

    def __missing__(self, key: str) -> int:
        return self.base


def escaped(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def effects(justify: str | None = None, hide: bool = False, size: float = 1.27) -> str:
    parts = [f"(font (size {size:.2f} {size:.2f}))"]
    if hide:
        parts.append("(hide yes)")
    if justify:
        parts.append(f"(justify {justify})")
    return "(effects " + " ".join(parts) + ")"


def symbol_name(instance: str, namespace: str = "UI10") -> str:
    return namespace + "_" + re.sub(r"[^A-Za-z0-9_]", "_", instance).upper()


def pin_layout(pins: list[Pin]) -> tuple[dict[str, tuple[float, float, str]], float]:
    midpoint = (len(pins) + 1) // 2
    left = pins[:midpoint]
    right = pins[midpoint:]
    rows = max(len(left), len(right), 2)
    top = (rows - 1) * 1.27
    result: dict[str, tuple[float, float, str]] = {}
    for index, pin in enumerate(left):
        result[pin.number] = (-17.78, top - index * 2.54, "left")
    for index, pin in enumerate(right):
        result[pin.number] = (17.78, top - index * 2.54, "right")
    return result, max(10.16, rows * 2.54 + 5.08)


def property_block(key: str, value: str, x: float, y: float, hide: bool = False) -> str:
    hidden = "\n\t\t\t(hide yes)" if hide else ""
    return (
        f'\t\t(property "{escaped(key)}" "{escaped(value)}"\n'
        f"\t\t\t(at {x:.2f} {y:.2f} 0)\n"
        "\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)"
        f"{hidden}\n"
        f"\t\t\t{effects()}\n"
        "\t\t)"
    )


def library_symbol(
    instance: str,
    pins: list[Pin],
    reference_prefix: str,
    footprint: str,
    description: str,
    on_board: bool = True,
    in_bom: bool = True,
    embedded: bool = True,
    namespace: str = "UI10",
) -> tuple[str, dict[str, tuple[float, float, str]], float]:
    name = symbol_name(instance, namespace)
    lib_id = f"Leshy2:{name}" if embedded else name
    coords, height = pin_layout(pins)
    half_height = height / 2 - 2.54
    lines = [
        f'\t\t(symbol "{lib_id}"',
        "\t\t\t(pin_names (offset 1.016))",
        "\t\t\t(exclude_from_sim no)",
        f"\t\t\t(in_bom {'yes' if in_bom else 'no'})",
        f"\t\t\t(on_board {'yes' if on_board else 'no'})",
        f"\t\t\t(in_pos_files {'yes' if on_board else 'no'})",
        "\t\t\t(duplicate_pin_numbers_are_jumpers no)",
        property_block("Reference", reference_prefix, 0, half_height + 2.54).replace("\t\t", "\t\t\t", 1),
        property_block("Value", name, 0, -half_height - 2.54).replace("\t\t", "\t\t\t", 1),
        property_block("Footprint", footprint, 0, 0, True).replace("\t\t", "\t\t\t", 1),
        property_block("Datasheet", "~", 0, 0, True).replace("\t\t", "\t\t\t", 1),
        property_block("Description", description, 0, 0, True).replace("\t\t", "\t\t\t", 1),
        f'\t\t\t(symbol "{name}_0_1"',
        "\t\t\t\t(rectangle",
        f"\t\t\t\t\t(start -12.70 {half_height:.2f})",
        f"\t\t\t\t\t(end 12.70 {-half_height:.2f})",
        "\t\t\t\t\t(stroke (width 0.254) (type default))",
        "\t\t\t\t\t(fill (type background))",
        "\t\t\t\t)",
        "\t\t\t)",
        f'\t\t\t(symbol "{name}_1_1"',
    ]
    for pin in pins:
        x, y, side = coords[pin.number]
        angle = 0 if side == "left" else 180
        lines += [
            "\t\t\t\t(pin passive line",
            f"\t\t\t\t\t(at {x:.2f} {y:.2f} {angle})",
            "\t\t\t\t\t(length 5.08)",
            f'\t\t\t\t\t(name "{escaped(pin.name)}" {effects()})',
            f'\t\t\t\t\t(number "{escaped(pin.number)}" {effects()})',
            "\t\t\t\t)",
        ]
    lines += ["\t\t\t)", "\t\t\t(embedded_fonts no)", "\t\t)"]
    return "\n".join(lines), coords, height


def schematic_symbol(
    instance: str,
    pins: list[Pin],
    reference: str,
    value: str,
    footprint: str,
    description: str,
    x: float,
    y: float,
    coords: dict[str, tuple[float, float, str]],
    on_board: bool = True,
    in_bom: bool = True,
    namespace: str = "UI10",
    project_id: str = PROJECT_ID,
    sheet_id: str = SHEET_ID,
) -> str:
    symbol_uuid = stable_uuid(f"symbol:{instance}")
    lines = [
        "\t(symbol",
        f'\t\t(lib_id "Leshy2:{symbol_name(instance, namespace)}")',
        f"\t\t(at {x:.2f} {y:.2f} 0)",
        "\t\t(unit 1)",
        "\t\t(exclude_from_sim no)",
        f"\t\t(in_bom {'yes' if in_bom else 'no'})",
        f"\t\t(on_board {'yes' if on_board else 'no'})",
        "\t\t(dnp no)",
        f'\t\t(uuid "{symbol_uuid}")',
        property_block("Reference", reference, x, y - max(5.08, len(pins) * 0.7)),
        property_block("Value", value, x, y + max(5.08, len(pins) * 0.7)),
        property_block("Footprint", footprint, x, y, True),
        property_block("Datasheet", "~", x, y, True),
        property_block("Description", description, x, y, True),
    ]
    for pin in pins:
        lines += [
            f'\t\t(pin "{escaped(pin.number)}"',
            f'\t\t\t(uuid "{stable_uuid(f"pin:{instance}:{pin.number}")}")',
            "\t\t)",
        ]
    lines += [
        "\t\t(instances",
        f'\t\t\t(project "{project_id}"',
        f'\t\t\t\t(path "/{stable_uuid(f"sheet:{sheet_id}")}"',
        f'\t\t\t\t\t(reference "{reference}")',
        "\t\t\t\t\t(unit 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        "\t)",
    ]
    return "\n".join(lines)


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "s3": "RF_Module:ESP32-S3-WROOM-1U",
        "s3_external_rp_sma": "Leshy2:RFPC-SMA32-FN-175-A",
        "s3_rf_board_connector": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
        "s3_rf_coupler": "Leshy2:CP0603Q5425ENTR",
        "s3_dbg_header": "Leshy2:FTSH-105-01-L-DV-K-P-TR",
        "s3_dbg_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "s3_reset_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
        "s3_boot_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
    }
    if instance in exact:
        return exact[instance]
    if instance == "s3_rf_jumper" or instance == "s3_factory_ant":
        return ""
    if "cap" in instance or "bypass" in instance:
        if device_key == "murata_grm21br60j226me39l":
            return "Capacitor_SMD:C_0805_2012Metric"
        if device_key == "tdk_c1608x7r1c105k080ac":
            return "Capacitor_SMD:C_0603_1608Metric"
        return "Capacitor_SMD:C_0402_1005Metric"
    return "Resistor_SMD:R_0402_1005Metric"


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "s3_factory_ant":
        return "X"
    if instance == "s3_rf_jumper":
        return "W"
    if "button" in instance:
        return "SW"
    if any(token in instance for token in ("connector", "header", "sma")):
        return "J"
    if "cap" in instance or "bypass" in instance:
        return "C"
    if any(token in instance for token in ("res", "pullup", "strap", "series", "termination")):
        return "R"
    return "U"


def pins_for(instance: str, device: dict) -> list[Pin]:
    if instance == "s3":
        contract = device["pcb_pad_contract"]
        return [
            Pin(str(number), str(name), str(name))
            for number, name in sorted(contract["pads"].items(), key=lambda row: int(row[0]))
        ]
    if instance == "s3_factory_ant":
        return [Pin("1", "FACTORY_UFL", "ANT")]
    number_overrides = {
        "s3_external_rp_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
        "s3_rf_jumper": {"END_A": "A", "END_B": "B"},
        "s3_rf_board_connector": {"CENTER": "1", "SHELL": "2"},
        "s3_rf_coupler": {
            "RF_IN": "IN", "RF_OUT": "OUT", "COUPLED_FWD": "CPL", "TERMINATION_50R": "TERM",
        },
    }
    pins = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = number_overrides.get(instance, {}).get(contact)
        if number is None:
            number = physical if re.fullmatch(r"[A-Za-z0-9_]+", physical) else contact
        pins.append(Pin(number, contact, contact))
    return pins


def endpoint_nets(candidate: dict, local_instances: set[str]) -> dict[tuple[str, str], str]:
    found: dict[tuple[str, str], set[str]] = defaultdict(set)
    aliases: dict[str, str] = {}
    for route in candidate["fixed_routes"]:
        abstract_endpoints = {route["from"], route["to"]}
        if any(endpoint.startswith("abstract:power-ground") or endpoint.startswith("abstract:rf-ground") for endpoint in abstract_endpoints):
            aliases[route["net"]] = "POWER_GROUND"
        elif "abstract:3V3_MAIN" in abstract_endpoints:
            aliases[route["net"]] = "3V3_MAIN"
        net = aliases.get(route["net"], route["net"])
        for endpoint in (route["from"], route["to"]):
            if "." not in endpoint:
                continue
            instance, contact = endpoint.split(".", 1)
            if instance in local_instances:
                found[(instance, contact)].add(net)
    for allocation in candidate["allocations"]:
        instance = allocation["instance"]
        if instance in local_instances:
            found[(instance, allocation["contact"])].add(
                aliases.get(allocation["net"], allocation["net"])
            )
    result: dict[tuple[str, str], str] = {}
    for endpoint, nets in found.items():
        meaningful = {net for net in nets if net != "NO_CONNECT"}
        if len(meaningful) > 1:
            raise ValueError(f"one physical endpoint has multiple nets: {endpoint} -> {sorted(meaningful)}")
        result[endpoint] = next(iter(meaningful), "NO_CONNECT")
    result[("s3", "3V3")] = "3V3_MAIN"
    result[("s3", "GND")] = "POWER_GROUND"
    result[("s3", "EPAD_GND")] = "POWER_GROUND"
    result[("s3_factory_ant", "ANT")] = "S3_MODULE_RF_50R"
    return result


def pin_net(instance: str, pin: Pin, endpoints: dict[tuple[str, str], str]) -> str:
    if pin.contact.startswith("NC_PSRAM_") or pin.contact.startswith("NC_"):
        return "NO_CONNECT"
    if instance == "s3" and pin.contact in ("GND", "EPAD_GND"):
        return "POWER_GROUND"
    return endpoints.get((instance, pin.contact), "NO_CONNECT")


def custom_footprint(
    name: str,
    pads: list[tuple],
    body_width: float,
    body_height: float,
    courtyard_width: float,
    courtyard_height: float,
    source: str,
    body_x: float = 0.0,
    body_y: float = 0.0,
    courtyard_x: float = 0.0,
    courtyard_y: float = 0.0,
) -> str:
    lines = [
        f'(footprint "{name}"',
        "\t(version 20260206)",
        '\t(generator "leshy2-h2-ui10")',
        '\t(generator_version "1.0")',
        '\t(layer "F.Cu")',
        f'\t(descr "{escaped(source)}")',
        '\t(property "Reference" "REF**" (at 0 -4 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'\t(property "Value" "{name}" (at 0 4 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        "\t(attr smd)",
        f'\t(fp_rect (start {body_x-body_width/2:.3f} {body_y-body_height/2:.3f}) (end {body_x+body_width/2:.3f} {body_y+body_height/2:.3f}) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))',
        f'\t(fp_rect (start {courtyard_x-courtyard_width/2:.3f} {courtyard_y-courtyard_height/2:.3f}) (end {courtyard_x+courtyard_width/2:.3f} {courtyard_y+courtyard_height/2:.3f}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
    ]
    for pad in pads:
        number, x, y, sx, sy, layers, *shape_row = pad
        shape = shape_row[0] if shape_row else "roundrect"
        layer_text = " ".join(f'"{layer}"' for layer in layers)
        suffix = " (roundrect_rratio 0.20)" if shape == "roundrect" else ""
        lines.append(
            f'\t(pad "{number}" smd {shape} (at {x:.3f} {y:.3f}) (size {sx:.3f} {sy:.3f}) '
            f'(layers {layer_text}){suffix})'
        )
    lines += [")", ""]
    return "\n".join(lines)


def footprint_outputs() -> dict[Path, str]:
    # These are manufacturer-drawing transcriptions.  Pad identities encode
    # the orientation-sensitive RF functions rather than pretending that the
    # drawings provide numeric pin designators.
    coupler = custom_footprint(
        "CP0603Q5425ENTR",
        [("OUT", -0.625, -0.350, 0.50, 0.40, ("F.Cu", "F.Paste", "F.Mask")),
         ("TERM", 0.625, -0.350, 0.50, 0.40, ("F.Cu", "F.Paste", "F.Mask")),
         ("IN", -0.625, 0.350, 0.50, 0.40, ("F.Cu", "F.Paste", "F.Mask")),
         ("CPL", 0.625, 0.350, 0.50, 0.40, ("F.Cu", "F.Paste", "F.Mask"))],
        1.60, 0.84, 1.95, 1.30,
        "KYOCERA AVX TDS-RFM-0055 Rev.2 CP0603Q5425ENTR: A=1.75, B=0.75, C=1.10, D=0.30, E=0.50, F=0.40-mm recommended land pattern; top-view terminals 1=IN, 2=OUT, 3=COUPLING, 4=50 OHM",
    )
    ftsh_pads = []
    for index in range(5):
        x = (index - 2) * 1.27
        ftsh_pads.append((str(index * 2 + 1), x, 2.035, 0.74, 2.79, ("F.Cu", "F.Paste", "F.Mask")))
        ftsh_pads.append((str(index * 2 + 2), x, -2.035, 0.74, 2.79, ("F.Cu", "F.Paste", "F.Mask")))
    ftsh = custom_footprint(
        "FTSH-105-01-L-DV-K-P-TR", ftsh_pads, 6.35, 3.43, 6.55, 7.06,
        "Samtec FTSH-1XX-XX-XXX-DV-XXX footprint Rev.H Figure 1: five positions per row, 1.27-mm pitch, 0.74x2.79-mm lands, 6.86-mm total land span; odd row below and even row above in the published view",
    )
    sma = custom_footprint(
        "RFPC-SMA32-FN-175-A",
        [("1", 0.0, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("2", -1.75, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("3", 1.75, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("4", -1.75, -1.65, 1.60, 3.30, ("B.Cu", "B.Paste", "B.Mask")),
         ("5", 1.75, -1.65, 1.60, 3.30, ("B.Cu", "B.Paste", "B.Mask"))],
        10.20, 6.60, 10.40, 6.80,
        "GCT RFPC-SMA32-FN drawing A1 dated 2025-02-25: option 175 for 1.60-mm PCB; top has three 1.60x3.30-mm lands across 5.10 mm and bottom has two matching outer ground lands",
    )
    return {
        FOOTPRINT_DIR / "CP0603Q5425ENTR.kicad_mod": coupler,
        FOOTPRINT_DIR / "FTSH-105-01-L-DV-K-P-TR.kicad_mod": ftsh,
        FOOTPRINT_DIR / "RFPC-SMA32-FN-175-A.kicad_mod": sma,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [row for row in ledger["rows"] if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID]
    if len(rows) != 32:
        raise ValueError(f"{SHEET_ID} must own exactly 32 ledger rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interfaces = set(interface_row["interfaces"])
    local_instances = {row["instance"] for row in rows}
    endpoints = endpoint_nets(candidate, local_instances)

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
        instance = row["instance"]
        device = devices[row["device_key"]]
        pins = pins_for(instance, device)
        prefix = reference_prefix(instance, row["device_key"])
        ref_counts[prefix] += 1
        specs.append({
            "instance": instance,
            "device_key": row["device_key"],
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins,
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(instance, row["device_key"]),
            "on_board": row["electrical_disposition"] != "fitted_interconnect_assembly",
            "in_bom": True,
        })
    specs.append({
        "instance": "s3_factory_ant",
        "device_key": "esp32_s3_wroom_1u_n16r8",
        "mpn": "ESP32-S3-WROOM-1U-N16R8 factory U.FL",
        "role": "non-PCB assembly boundary; the receptacle is fitted to the module by Espressif",
        "pins": pins_for("s3_factory_ant", devices["esp32_s3_wroom_1u_n16r8"]),
        "reference": scoped_reference(SHEET_ID, "X1"),
        "footprint": "",
        "on_board": False,
        "in_bom": False,
    })

    library_defs = []
    library_file_defs = []
    placements = {}
    column_x = [60.96, 152.40, 243.84, 335.28, 426.72]
    cursor_y = [45.72] * len(column_x)
    for index, spec in enumerate(specs):
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], spec["on_board"], spec["in_bom"], True,
        )
        library_defs.append(lib)
        file_lib, _, _ = library_symbol(
            spec["instance"], spec["pins"], spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], spec["on_board"], spec["in_bom"], False,
        )
        library_file_defs.append(file_lib.replace("\t\t", "\t", 1))
        column = min(range(len(cursor_y)), key=lambda col: cursor_y[col])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        pin_remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - pin_remainder) / 2.54) * 2.54 + pin_remainder
        cursor_y[column] = y + height / 2 + 17.78
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")',
        "\t(title_block",
        '\t\t(title "Leshy2 — exact S3 core, boot, USB, service and RF feed")',
        '\t\t(rev "H2.2.2")',
        "\t)",
        "\t(lib_symbols",
        *library_defs,
        "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"], spec["footprint"],
            spec["role"], x, y, coords, spec["on_board"], spec["in_bom"],
        ))
        for pin in spec["pins"]:
            net = pin_net(spec["instance"], pin, endpoints)
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used: set[str] = set()
    no_connect_count = 0
    no_connect_endpoints: list[str] = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT" or net.endswith("_NC"):
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")',
                    "\t)",
                ]
                no_connect_count += 1
                no_connect_endpoints.append(f"{instance}.{pin.contact}")
                continue
            is_hierarchical = net in interfaces and net not in hierarchy_used
            hierarchy_used.add(net) if is_hierarchical else None
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            token = "hierarchical_label" if is_hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if is_hierarchical else ""
            lines += [
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")',
                "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(
            f"UI10 circuit does not terminate every hierarchy interface: missing {sorted(interfaces - hierarchy_used)}; "
            f"unexpected {sorted(hierarchy_used - interfaces)}"
        )
    lines += [
        "\t(sheet_instances",
        '\t\t(path "/"',
        '\t\t\t(page "1")',
        "\t\t)",
        "\t)",
        "\t(embedded_fonts no)",
        ")",
        "",
    ]
    generated = {
        OUTPUT_SCH: "\n".join(lines),
        **footprint_outputs(),
    }
    from h2_symbol_library import build as build_symbol_library
    generated[SYMBOL_LIBRARY] = build_symbol_library({OUTPUT_SCH: generated[OUTPUT_SCH]})
    s3_device = devices["esp32_s3_wroom_1u_n16r8"]
    manifest = {
        "schema_version": 1,
        "stage": "H2.2.2",
        "status": "reviewed_exact_s3_core_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "assembly_interface_symbols": 1,
            "s3_carrier_pads": s3_device["pcb_pad_contract"]["pad_count"],
            "hierarchical_interfaces": len(interfaces),
            "intentional_no_connect_pins": no_connect_count,
            "custom_footprints": len(footprint_outputs()),
            "pcb_files_created": 0,
        },
        "s3_pad_contract": s3_device["pcb_pad_contract"],
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "non_pcb_interfaces": s3_device["non_pcb_interfaces"],
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"],
                "mpn": spec["mpn"],
                "footprint": spec["footprint"] or None,
                "pin_count": len(spec["pins"]),
                "ledger_component": spec["instance"] != "s3_factory_ant",
            }
            for spec in specs
        ],
        "footprint_evidence": [
            {
                "mpn": "KYOCERA AVX CP0603Q5425ENTR",
                "source": "TDS-RFM-0055 Rev.2, CP0603 page",
                "url": "https://datasheets.kyocera-avx.com/cp0302.pdf",
                "checked": "2026-08-23",
                "locked_geometry_mm": {
                    "overall_land_span": [1.75, 1.10],
                    "inter_land_gap": [0.75, 0.30],
                    "land_size": [0.50, 0.40],
                },
            },
            {
                "mpn": "Samtec FTSH-105-01-L-DV-K-P-TR",
                "source": "FTSH-1XX-XX-XXX-DV-XXX footprint Rev.H Figure 1",
                "url": "https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf",
                "checked": "2026-08-23",
                "locked_geometry_mm": {
                    "positions_per_row": 5,
                    "pitch": 1.27,
                    "land_size": [0.74, 2.79],
                    "overall_row_land_span": 6.86,
                },
            },
            {
                "mpn": "GCT RFPC-SMA32-FN-175-A",
                "source": "RFPC-SMA32-FN drawing A1 dated 2025-02-25",
                "url": "https://gct.co/connector/rfpc-sma32-fn",
                "checked": "2026-08-23",
                "locked_geometry_mm": {
                    "pcb_thickness": 1.60,
                    "top_land_count": 3,
                    "bottom_land_count": 2,
                    "land_size": [1.60, 3.30],
                    "outer_land_span": 5.10,
                },
            },
        ],
        "corrections_closed": [
            "N16R8 carrier pads 28/29/30 are physical no-connects because octal PSRAM consumes GPIO35/36/37 internally",
            "all three physical module ground lands 1/40/41 are distinct schematic pins on POWER_GROUND",
            "22-uF and 100-nF local module supply capacitors plus the recommended 10-kOhm/1-uF EN network are fitted",
            "USB D+/D- 22-Ohm source terminations are on the UI board beside S3, after M1",
            "the factory module U.FL is an assembly interface, not a fictitious carrier-PCB pad",
            "the board U.FL centre, PCB trace and coupler input use one continuous S3_MODULE_RF_50R net",
            "the SMA shell, board-U.FL shell, coupler termination, RF ESD and debug ESD returns all terminate on physical POWER_GROUND",
            "UNIT_HOST_SIG0/1 now cross M1 contacts 69/71, each beside a retained POWER_GROUND return",
        ],
        "review_boundary": {
            "complete": [
                "every H2 ledger instance owned by UI10 is placed once with exact MPN and contact map",
                "every S3 carrier pad is connected or explicitly no-connect",
                "every one of the live UI10 hierarchy interfaces terminates on a real circuit pin",
                "exact boot, reset, native USB, UART0 fallback, RF feed and local supply networks are represented",
                "native KiCad parses the populated hierarchy; no unexplained UI10 ERC finding remains",
            ],
            "deferred": [
                "PCB placement, controlled-impedance routing, via/return geometry and DRC in H6",
                "USB eye/edge, RF loss/match/directivity, reset timing and service-control HIL",
                "received-part dimensional and mating evidence in H5",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary != {
        "ledger_instances": 32,
        "schematic_symbols": 33,
        "assembly_interface_symbols": 1,
        "s3_carrier_pads": 41,
        "hierarchical_interfaces": 39,
        "intentional_no_connect_pins": 7,
        "custom_footprints": 3,
        "pcb_files_created": 0,
    }:
        raise ValueError(f"reviewed H2.2.2 accounting drifted: {summary}")
    sch = generated[OUTPUT_SCH]
    if sch.count("\n\t(symbol\n") != 33:
        raise ValueError("schematic symbol instance count mismatch")
    if sch.count("\n\t(hierarchical_label \"") != 39:
        raise ValueError("UI10 hierarchical label count mismatch")
    pad_contract = manifest["s3_pad_contract"]["pads"]
    if set(pad_contract) != {str(index) for index in range(1, 42)}:
        raise ValueError("S3 physical pad set is not exactly 1..41")
    if [pad_contract[str(index)] for index in (28, 29, 30)] != [
        "NC_PSRAM_GPIO35", "NC_PSRAM_GPIO36", "NC_PSRAM_GPIO37",
    ]:
        raise ValueError("N16R8 octal-PSRAM no-connect contract drifted")
    coupler = generated[FOOTPRINT_DIR / "CP0603Q5425ENTR.kicad_mod"]
    for exact_land in (
        '(pad "OUT" smd roundrect (at -0.625 -0.350) (size 0.500 0.400)',
        '(pad "TERM" smd roundrect (at 0.625 -0.350) (size 0.500 0.400)',
        '(pad "IN" smd roundrect (at -0.625 0.350) (size 0.500 0.400)',
        '(pad "CPL" smd roundrect (at 0.625 0.350) (size 0.500 0.400)',
    ):
        if exact_land not in coupler:
            raise ValueError(f"CP0603Q5425ENTR land-pattern drift: {exact_land}")
    ftsh = generated[FOOTPRINT_DIR / "FTSH-105-01-L-DV-K-P-TR.kicad_mod"]
    if ftsh.count("(size 0.740 2.790)") != 10:
        raise ValueError("FTSH-105 exact 0.74x2.79-mm ten-land contract drifted")
    if ftsh.count("(at ") < 11 or "(at -2.540 2.035)" not in ftsh or "(at -2.540 -2.035)" not in ftsh:
        raise ValueError("FTSH-105 1.27-mm pitch / 6.86-mm row span drifted")
    sma = generated[FOOTPRINT_DIR / "RFPC-SMA32-FN-175-A.kicad_mod"]
    if sma.count('(layers "F.Cu" "F.Paste" "F.Mask")') != 3:
        raise ValueError("RFPC-SMA32 top-side three-land contract drifted")
    if sma.count('(layers "B.Cu" "B.Paste" "B.Mask")') != 2:
        raise ValueError("RFPC-SMA32 bottom-side two-ground-land contract drifted")
    for exact_land in (
        '(pad "1" smd roundrect (at 0.000 -1.650) (size 1.600 3.300)',
        '(pad "2" smd roundrect (at -1.750 -1.650) (size 1.600 3.300)',
        '(pad "3" smd roundrect (at 1.750 -1.650) (size 1.600 3.300)',
        '(pad "4" smd roundrect (at -1.750 -1.650) (size 1.600 3.300)',
        '(pad "5" smd roundrect (at 1.750 -1.650) (size 1.600 3.300)',
    ):
        if exact_land not in sma:
            raise ValueError(f"RFPC-SMA32 land-pattern drift: {exact_land}")


def kicad_check() -> None:
    cli = find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-ui10-") as temp:
        temp_path = Path(temp)
        upgraded = temp_path / "Leshy2.pretty"
        fp_result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(FOOTPRINT_DIR)],
            text=True,
            capture_output=True,
        )
        if fp_result.returncode:
            raise RuntimeError(f"KiCad rejected the controlled footprint library:\n{fp_result.stdout}{fp_result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected populated UI hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.2 inside the live hierarchy and all custom footprints")


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
        result = subprocess.run(
            ["python3", str(ECAD / "h2_ui_root.py"), "--write"],
            cwd=REPO,
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"failed to refresh live UI hierarchy:\n{result.stdout}{result.stderr}")
        print(result.stdout, end="")
    else:
        stale = [
            path for path, content in generated.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print("ok: H2.2.2 S3 core sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
