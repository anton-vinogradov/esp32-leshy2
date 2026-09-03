#!/usr/bin/env python3
"""Generate the two current H2-R2 native KiCad schematic projects.

The generator deliberately stops at logical schematics.  It materializes the
reviewed fitted-instance ledger, exact controlled symbols, canonical networks
and explicit no-connects, but creates no PCB, placement, routing or production
files.  R1 KiCad projects are never read by this generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "hardware/ecad/h2-r2-native-kicad-contract.json"
UUID_NAMESPACE = uuid.UUID("55d78bc6-bb67-4c34-aa29-29952908dcf4")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_uuid(scope: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, scope))


def escaped(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def natural_key(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def effects(justify: str | None = None, size: float = 1.27) -> str:
    suffix = f" (justify {justify})" if justify else ""
    return f"(effects (font (size {size:.2f} {size:.2f})){suffix})"


def property_block(
    key: str,
    value: object,
    x: float,
    y: float,
    *,
    hide: bool = False,
) -> list[str]:
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


def parenthesis_delta(line: str) -> int:
    """Count structural parentheses while ignoring quoted strings."""
    delta = 0
    quoted = False
    escaped_char = False
    for char in line:
        if escaped_char:
            escaped_char = False
            continue
        if char == "\\" and quoted:
            escaped_char = True
            continue
        if char == '"':
            quoted = not quoted
        elif not quoted and char == "(":
            delta += 1
        elif not quoted and char == ")":
            delta -= 1
    return delta


def embedded_symbol_definitions(library_text: str) -> dict[str, str]:
    """Extract top-level controlled symbols and namespace them for schematics."""
    definitions: dict[str, str] = {}
    lines = library_text.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r'^\t\(symbol "([^"]+)"$', lines[index])
        if not match:
            index += 1
            continue
        device_id = match.group(1)
        block = [lines[index]]
        depth = parenthesis_delta(lines[index])
        index += 1
        while depth and index < len(lines):
            block.append(lines[index])
            depth += parenthesis_delta(lines[index])
            index += 1
        if depth:
            raise ValueError(f"unterminated controlled symbol: {device_id}")
        block[0] = block[0].replace(
            f'\t(symbol "{device_id}"',
            f'\t(symbol "Leshy2_R2:{device_id}"',
            1,
        )
        definitions[device_id] = "\n".join("\t" + line for line in block)
    return definitions


def pin_layout(symbol: dict) -> tuple[dict[str, tuple[float, float, str]], float]:
    pins = symbol["pin_map"]
    midpoint = (len(pins) + 1) // 2
    left, right = pins[:midpoint], pins[midpoint:]
    rows = max(len(left), len(right), 2)
    top = (rows - 1) * 1.27
    result: dict[str, tuple[float, float, str]] = {}
    for side, side_pins in (("left", left), ("right", right)):
        for index, pin in enumerate(side_pins):
            x = -20.32 if side == "left" else 20.32
            result[pin["number"]] = (x, top - index * 2.54, side)
    return result, max(10.16, rows * 2.54)


def symbol_instance(
    project: str,
    sheet: str,
    instance: dict,
    symbol: dict,
    x: float,
    y: float,
) -> str:
    coords, body_height = pin_layout(symbol)
    symbol_uuid = stable_uuid(f"symbol:{project}:{sheet}:{instance['instance']}")
    in_bom = "no" if instance.get("bom_excluded") else "yes"
    lines = [
        "\t(symbol",
        f'\t\t(lib_id "{escaped(symbol["symbol_id"])}")',
        f"\t\t(at {x:.2f} {y:.2f} 0)",
        "\t\t(unit 1)",
        "\t\t(exclude_from_sim no)",
        f"\t\t(in_bom {in_bom})",
        "\t\t(on_board yes)",
        "\t\t(dnp no)",
        f'\t\t(uuid "{symbol_uuid}")',
    ]
    lines += property_block("Reference", instance["reference"], x, y - body_height / 2 - 2.54)
    lines += property_block("Value", instance["mpn"], x, y + body_height / 2 + 2.54)
    lines += property_block("Footprint", instance["footprint"], x, y, hide=True)
    lines += property_block("Datasheet", "~", x, y, hide=True)
    lines += property_block("Description", instance["device_id"], x, y, hide=True)
    lines += property_block("Leshy2Instance", instance["instance"], x, y, hide=True)
    for pin in symbol["pin_map"]:
        if pin["number"] not in coords:
            raise ValueError(f"pin layout lost {instance['instance']}.{pin['number']}")
        pin_uuid = stable_uuid(
            f"pin:{project}:{sheet}:{instance['instance']}:{pin['number']}"
        )
        lines += [
            f'\t\t(pin "{escaped(pin["number"])}"',
            f'\t\t\t(uuid "{pin_uuid}")',
            "\t\t)",
        ]
    sheet_uuid = stable_uuid(f"sheet:{project}:{sheet}")
    lines += [
        "\t\t(instances",
        f'\t\t\t(project "{escaped(project)}"',
        f'\t\t\t\t(path "/{sheet_uuid}"',
        f'\t\t\t\t\t(reference "{escaped(instance["reference"])}")',
        "\t\t\t\t\t(unit 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        "\t)",
    ]
    return "\n".join(lines)


def place_instances(instances: list[dict], symbols: dict[str, dict]) -> dict[str, tuple[float, float]]:
    """Deterministically pack symbols into twelve roomy A0 columns."""
    columns = 12
    column_x = [55.88 + index * 91.44 for index in range(columns)]
    cursor_y = [38.10] * columns
    placements: dict[str, tuple[float, float]] = {}
    for instance in sorted(instances, key=lambda row: natural_key(row["reference"])):
        symbol = symbols[instance["device_id"]]
        _, body_height = pin_layout(symbol)
        occupied = body_height + 17.78
        column = min(range(columns), key=lambda item: cursor_y[item])
        y = cursor_y[column] + occupied / 2
        cursor_y[column] += occupied + 7.62
        if cursor_y[column] > 815:
            raise ValueError(f"A0 placement overflow on {instance['sheet']}: {instance['instance']}")
        placements[instance["instance"]] = (column_x[column], y)
    return placements


def endpoint_target(rows: list[dict], instance: str, pin: dict) -> tuple[str, str | None]:
    candidates = [rows_by_contact for contact in pin["contacts"] for rows_by_contact in rows if rows_by_contact["contact"] == contact]
    if not candidates:
        raise ValueError(f"no logical endpoint for physical pin {instance}.{pin['number']}")
    targets = {(row["disposition"], row.get("net")) for row in candidates}
    if len(targets) != 1:
        raise ValueError(
            f"logical contacts disagree on physical pin {instance}.{pin['number']}: {sorted(targets)}"
        )
    disposition, net = next(iter(targets))
    if disposition not in {"connected", "no_connect"}:
        raise ValueError(f"unsupported endpoint disposition on {instance}.{pin['number']}: {disposition}")
    if disposition == "connected" and not net:
        raise ValueError(f"connected pin lost net: {instance}.{pin['number']}")
    return disposition, net


def child_schematic(
    project: str,
    sheet: dict,
    instances: list[dict],
    net_rows: list[dict],
    symbols: dict[str, dict],
    embedded_definitions: dict[str, str],
    cross_sheet_nets: set[str],
) -> tuple[str, dict]:
    sheet_id = sheet["id"]
    placements = place_instances(instances, symbols)
    used_devices = sorted({row["device_id"] for row in instances})
    lines = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "leshy2-h2-r2-native")',
        '\t(generator_version "1.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{project}:{sheet_id}")}")',
        '\t(paper "A0")',
        "\t(title_block",
        f'\t\t(title "Leshy2 R2 — {escaped(sheet["role"])}")',
        '\t\t(rev "H2-R2.1.3")',
        "\t)",
        "\t(lib_symbols",
    ]
    lines += [embedded_definitions[device_id] for device_id in used_devices]
    lines.append("\t)")

    rows_by_instance: dict[str, list[dict]] = defaultdict(list)
    for row in net_rows:
        rows_by_instance[row["instance"]].append(row)
    hierarchical_used: set[str] = set()
    physical_pin_count = 0
    connected_pin_count = 0
    no_connect_pin_count = 0
    external_interfaces = []
    for instance in sorted(instances, key=lambda row: natural_key(row["reference"])):
        symbol = symbols[instance["device_id"]]
        x, y = placements[instance["instance"]]
        lines.append(symbol_instance(project, sheet_id, instance, symbol, x, y))
        coords, _ = pin_layout(symbol)
        instance_rows = rows_by_instance[instance["instance"]]
        for pin in symbol["pin_map"]:
            disposition, net = endpoint_target(instance_rows, instance["instance"], pin)
            px, py, side = coords[pin["number"]]
            pin_x, pin_y = x + px, y - py
            physical_pin_count += 1
            if disposition == "no_connect":
                no_connect_pin_count += 1
                nc_uuid = stable_uuid(
                    f"nc:{project}:{sheet_id}:{instance['instance']}:{pin['number']}"
                )
                lines += [
                    f"\t(no_connect (at {pin_x:.2f} {pin_y:.2f})",
                    f'\t\t(uuid "{nc_uuid}")',
                    "\t)",
                ]
                continue
            connected_pin_count += 1
            assert net is not None
            is_hierarchical = net in cross_sheet_nets and net not in hierarchical_used
            if is_hierarchical:
                hierarchical_used.add(net)
            token = "hierarchical_label" if is_hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if is_hierarchical else ""
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            label_uuid = stable_uuid(
                f"net-label:{project}:{sheet_id}:{instance['instance']}:{pin['number']}:{net}"
            )
            lines += [
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {pin_x:.2f} {pin_y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{label_uuid}")',
                "\t)",
            ]
        for contact in symbol["external_interfaces"]:
            matches = [row for row in instance_rows if row["contact"] == contact]
            if len(matches) != 1 or matches[0]["disposition"] != "connected":
                raise ValueError(f"external interface target changed: {instance['instance']}.{contact}")
            target = matches[0]
            annotation = {
                "endpoint": target["endpoint"],
                "net": target["net"],
                "representation": "on-module receptacle; no Leshy2 PCB pad",
            }
            external_interfaces.append(annotation)
            text_x, text_y = x, y + pin_layout(symbol)[1] / 2 + 7.62
            external_uuid = stable_uuid(
                f"external-interface:{project}:{sheet_id}:{target['endpoint']}"
            )
            lines += [
                f'\t(text "EXT {escaped(contact)} → {escaped(target["net"])} (on-module receptacle)"',
                f"\t\t(exclude_from_sim no)",
                f"\t\t(at {text_x:.2f} {text_y:.2f} 0)",
                f"\t\t{effects(size=1.00)}",
                f'\t\t(uuid "{external_uuid}")',
                "\t)",
            ]

    expected_hierarchical = {
        row["net"]
        for row in net_rows
        if row["disposition"] == "connected" and row["net"] in cross_sheet_nets
    }
    missing_hierarchy = expected_hierarchical - hierarchical_used
    if missing_hierarchy:
        raise ValueError(f"{sheet_id} lost hierarchical nets: {sorted(missing_hierarchy)}")
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
    summary = {
        "id": sheet_id,
        "role": sheet["role"],
        "instance_count": len(instances),
        "physical_symbol_pin_count": physical_pin_count,
        "connected_physical_pin_count": connected_pin_count,
        "explicit_no_connect_physical_pin_count": no_connect_pin_count,
        "hierarchical_interface_count": len(hierarchical_used),
        "external_module_interface_count": len(external_interfaces),
        "external_module_interfaces": external_interfaces,
    }
    return "\n".join(lines), summary


def root_schematic(project: dict, interfaces: dict[str, list[str]]) -> str:
    project_id = project["id"]
    root_id = project["root"]
    root_uuid = stable_uuid(f"sheet:{project_id}:{root_id}")
    lines = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "leshy2-h2-r2-native")',
        '\t(generator_version "1.0")',
        f'\t(uuid "{root_uuid}")',
        '\t(paper "A0")',
        "\t(title_block",
        f'\t\t(title "Leshy2 R2 — {escaped(project["board"])} hierarchy")',
        '\t\t(rev "H2-R2.1.3")',
        "\t)",
        "\t(lib_symbols)",
    ]
    pin_positions: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    y_cursor = 20.32
    child_sheets = [sheet for sheet in project["sheets"] if sheet["id"] != root_id]
    for sheet_index, sheet in enumerate(child_sheets):
        sheet_id = sheet["id"]
        nets = interfaces[sheet_id]
        x, y, width = 20.32, y_cursor, 254.00
        # The root is a machine-audit hierarchy, not a human schematic page.
        # A 1.27-mm pin pitch keeps the full 13-sheet RF project on one A0 root
        # without hiding or dropping any named interface.
        root_pin_pitch = 1.27
        height = max(33.02, 12.70 + len(nets) * root_pin_pitch)
        y_cursor += height + 7.62
        if y_cursor > 825:
            raise ValueError(f"root hierarchy overflows A0 for {project_id}")
        hierarchy_uuid = stable_uuid(f"hierarchy:{project_id}:{sheet_id}")
        lines += [
            "\t(sheet",
            f"\t\t(at {x:.2f} {y:.2f})",
            f"\t\t(size {width:.2f} {height:.2f})",
            "\t\t(fields_autoplaced yes)",
            "\t\t(stroke (width 0) (type default))",
            "\t\t(fill (color 0 0 0 0.0000))",
            f'\t\t(uuid "{hierarchy_uuid}")',
            f'\t\t(property "Sheetname" "{escaped(sheet_id)}"',
            f"\t\t\t(at {x:.2f} {y - 0.71:.4f} 0)",
            f"\t\t\t{effects('left bottom')}",
            "\t\t)",
            f'\t\t(property "Sheetfile" "{escaped(sheet_id)}.kicad_sch"',
            f"\t\t\t(at {x:.2f} {y + height + 0.71:.4f} 0)",
            f"\t\t\t{effects('left top')}",
            "\t\t)",
        ]
        for pin_index, net in enumerate(nets):
            pin_x, pin_y = x + width, y + 6.35 + pin_index * root_pin_pitch
            pin_positions[net].append((pin_x, pin_y, sheet_id))
            lines += [
                f'\t\t(pin "{escaped(net)}" bidirectional',
                f"\t\t\t(at {pin_x:.2f} {pin_y:.2f} 0)",
                f"\t\t\t{effects()}",
                f'\t\t\t(uuid "{stable_uuid(f"root-pin:{project_id}:{sheet_id}:{net}")}")',
                "\t\t)",
            ]
        lines += [
            "\t\t(instances",
            f'\t\t\t(project "{escaped(project_id)}"',
            f'\t\t\t\t(path "/{root_uuid}/{hierarchy_uuid}"',
            f'\t\t\t\t\t(page "{sheet_index + 2}")',
            "\t\t\t\t)",
            "\t\t\t)",
            "\t\t)",
            "\t)",
        ]
    for net_index, (net, positions) in enumerate(sorted(pin_positions.items())):
        rail_x = 320.04 + net_index * 2.54
        if rail_x > 1160:
            raise ValueError(f"root net rails overflow A0 for {project_id}")
        y_values = [position[1] for position in positions]
        for pin_x, pin_y, sheet_id in positions:
            lines += [
                "\t(wire",
                f"\t\t(pts (xy {pin_x:.2f} {pin_y:.2f}) (xy {rail_x:.2f} {pin_y:.2f}))",
                "\t\t(stroke (width 0) (type default))",
                f'\t\t(uuid "{stable_uuid(f"root-branch:{project_id}:{sheet_id}:{net}")}")',
                "\t)",
                f"\t(junction (at {rail_x:.2f} {pin_y:.2f})",
                "\t\t(diameter 0)",
                "\t\t(color 0 0 0 0)",
                f'\t\t(uuid "{stable_uuid(f"root-junction:{project_id}:{sheet_id}:{net}")}")',
                "\t)",
            ]
        lines += [
            "\t(wire",
            f"\t\t(pts (xy {rail_x:.2f} {min(y_values):.2f}) (xy {rail_x:.2f} {max(y_values):.2f}))",
            "\t\t(stroke (width 0) (type default))",
            f'\t\t(uuid "{stable_uuid(f"root-rail:{project_id}:{net}")}")',
            "\t)",
        ]
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
    return "\n".join(lines)


def project_file(project_id: str) -> str:
    return json.dumps(
        {
            "board": {
                "design_settings": {
                    "meta": {
                        "filename": "board_design_settings.json",
                        "version": 2,
                    },
                    "rules": {
                        "allow_blind_buried_vias": False,
                        "allow_microvias": False,
                        "min_clearance": 0.15,
                        "min_copper_edge_clearance": 0.20,
                        "min_hole_clearance": 0.25,
                        "min_hole_to_hole": 0.25,
                        "min_silk_clearance": 0.15,
                        "min_text_height": 1.0,
                        "min_text_thickness": 0.15,
                        "min_through_hole_diameter": 0.20,
                        "min_track_width": 0.10,
                        "min_via_annular_width": 0.10,
                        "min_via_diameter": 0.40,
                    },
                }
            },
            "boards": [],
            "cvpcb": {},
            "erc": {"rule_severities": {"lib_symbol_mismatch": "ignore"}},
            "libraries": {},
            "meta": {"filename": f"{project_id}.kicad_pro", "version": 1},
            "net_settings": {
                "classes": [
                    {
                        "bus_width": 12,
                        "clearance": 0.15,
                        "diff_pair_gap": 0.15,
                        "diff_pair_via_gap": 0.15,
                        "diff_pair_width": 0.15,
                        "line_style": 0,
                        "microvia_diameter": 0.30,
                        "microvia_drill": 0.10,
                        "name": "Default",
                        "pcb_color": "rgba(0, 0, 0, 0.000)",
                        "priority": 2147483647,
                        "schematic_color": "rgba(0, 0, 0, 0.000)",
                        "track_width": 0.15,
                        "via_diameter": 0.40,
                        "via_drill": 0.20,
                        "wire_width": 6,
                    }
                ],
                "meta": {"version": 4},
                "net_colors": None,
                "netclass_assignments": None,
                "netclass_patterns": [],
            },
            "pcbnew": {},
            "schematic": {},
            "sheets": [],
            "text_variables": {
                "LESHY2_PCB_PROJECT": project_id,
                "LESHY2_STAGE": "H2-R2.1.3",
                "LESHY2_PCB_AUTHORIZED": "false",
            },
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def sym_lib_table() -> str:
    return """(sym_lib_table
  (version 7)
  (lib (name "Leshy2_R2") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/leshy2_r2.kicad_sym") (options "") (descr "Repository-controlled Leshy2 R2 exact symbols"))
)
"""


def fp_lib_table() -> str:
    return """(fp_lib_table
  (version 7)
  (lib (name "Leshy2") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/Leshy2.pretty") (options "") (descr "Repository-controlled Leshy2 exact footprints"))
  (lib (name "Leshy2_R2") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/Leshy2_R2.pretty") (options "") (descr "Repository-controlled Leshy2 R2 exact footprints"))
)
"""


def build() -> tuple[dict[Path, str], dict]:
    contract = load(CONTRACT_PATH)
    errors = []
    if (contract.get("marker"), contract.get("status")) != (
        "H2-R2.1.3",
        "current_native_schematic_project_contract",
    ):
        errors.append("native KiCad contract identity changed")
    sources = {}
    upstream = {}
    for key, relative in contract["authority"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing native KiCad authority: {relative}")
            continue
        sources[key] = {"path": relative, "sha256": sha256(path)}
        if path.suffix == ".json":
            upstream[key] = load(path)
    if errors:
        return {}, {"status": "fail", "errors": errors}

    inventory = upstream["inventory"]
    instance_ledger = upstream["instances"]
    net_ledger = upstream["nets"]
    symbol_manifest = upstream["symbols"]
    if any(
        source.get("status") not in {"pass", "reviewed_source_sheet_component_inventory"}
        for source in (instance_ledger, net_ledger, symbol_manifest)
    ):
        errors.append("one or more native KiCad upstream ledgers are not passing")
    projects = inventory["projects"]
    instances = instance_ledger["rows"]
    net_rows = net_ledger["rows"]
    symbols = {row["device_id"]: row for row in symbol_manifest["symbols"]}
    definitions = embedded_symbol_definitions((ROOT / contract["authority"]["symbol_library"]).read_text(encoding="utf-8"))
    if set(symbols) != set(definitions):
        errors.append("controlled symbol manifest/library identities differ")

    instances_by_sheet: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in instances:
        instances_by_sheet[(row["project"], row["sheet"])].append(row)
    nets_by_sheet: dict[tuple[str, str], list[dict]] = defaultdict(list)
    sheets_by_project_net: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in net_rows:
        nets_by_sheet[(row["project"], row["sheet"])].append(row)
        if row["disposition"] == "connected":
            sheets_by_project_net[(row["project"], row["net"])].add(row["sheet"])

    outputs: dict[Path, str] = {}
    project_summaries = []
    all_sheet_summaries = []
    output_root = ROOT / contract["output_root"]
    for project in projects:
        project_id = project["id"]
        project_dir = output_root / project_id
        outputs[project_dir / f"{project_id}.kicad_pro"] = project_file(project_id)
        outputs[project_dir / "sym-lib-table"] = sym_lib_table()
        outputs[project_dir / "fp-lib-table"] = fp_lib_table()
        cross_sheet_nets = {
            net
            for (owner, net), sheet_ids in sheets_by_project_net.items()
            if owner == project_id and len(sheet_ids) > 1
        }
        project_interfaces: dict[str, list[str]] = {}
        project_instance_count = 0
        project_physical_pin_count = 0
        project_external_count = 0
        for sheet in project["sheets"]:
            sheet_id = sheet["id"]
            if sheet_id == project["root"] and len(project["sheets"]) > 1:
                continue
            sheet_instances = instances_by_sheet[(project_id, sheet_id)]
            sheet_rows = nets_by_sheet[(project_id, sheet_id)]
            schematic, summary = child_schematic(
                project_id,
                sheet,
                sheet_instances,
                sheet_rows,
                symbols,
                definitions,
                cross_sheet_nets,
            )
            outputs[project_dir / f"{sheet_id}.kicad_sch"] = schematic
            all_sheet_summaries.append(summary | {"project": project_id})
            project_instance_count += summary["instance_count"]
            project_physical_pin_count += summary["physical_symbol_pin_count"]
            project_external_count += summary["external_module_interface_count"]
        if len(project["sheets"]) > 1:
            for sheet in project["sheets"]:
                if sheet["id"] == project["root"]:
                    continue
                nets = {
                    row["net"]
                    for row in nets_by_sheet[(project_id, sheet["id"])]
                    if row["disposition"] == "connected" and row["net"] in cross_sheet_nets
                }
                project_interfaces[sheet["id"]] = sorted(nets)
            outputs[project_dir / f"{project_id}.kicad_sch"] = root_schematic(project, project_interfaces)
        else:
            only_sheet = project["sheets"][0]["id"]
            source = outputs.pop(project_dir / f"{only_sheet}.kicad_sch")
            outputs[project_dir / f"{project_id}.kicad_sch"] = source
        project_summaries.append(
            {
                "id": project_id,
                "root": project["root"],
                "sheet_count": len(project["sheets"]),
                "populated_sheet_count": sum(
                    bool(instances_by_sheet[(project_id, sheet["id"])]) for sheet in project["sheets"]
                ),
                "instance_count": project_instance_count,
                "physical_symbol_pin_count": project_physical_pin_count,
                "external_module_interface_count": project_external_count,
                "canonical_net_count": len(
                    {
                        row["net"]
                        for row in net_rows
                        if row["project"] == project_id and row["disposition"] == "connected"
                    }
                ),
                "cross_sheet_net_count": len(cross_sheet_nets),
            }
        )

    physical_pin_count = sum(row["physical_symbol_pin_count"] for row in all_sheet_summaries)
    connected_pin_count = sum(row["connected_physical_pin_count"] for row in all_sheet_summaries)
    no_connect_pin_count = sum(row["explicit_no_connect_physical_pin_count"] for row in all_sheet_summaries)
    external_count = sum(row["external_module_interface_count"] for row in all_sheet_summaries)
    expected_instance_count = instance_ledger["summary"]["fitted_board_instance_count"]
    if sum(row["instance_count"] for row in project_summaries) != expected_instance_count:
        errors.append("native KiCad projects lost fitted instances")
    if physical_pin_count != sum(symbols[row["device_id"]]["pin_count"] for row in instances):
        errors.append("native KiCad projects lost controlled physical symbol pins")
    if connected_pin_count + no_connect_pin_count != physical_pin_count:
        errors.append("not every physical symbol pin is connected or explicit no-connect")
    if external_count != 5:
        errors.append(f"expected five fitted on-module RF interface annotations, got {external_count}")
    if any(path.suffix == ".kicad_pcb" for path in outputs):
        errors.append("native logical generation created an unauthorized PCB")
    expected_authorization = {
        "native_kicad_project_creation": True,
        "native_schematic_symbols_and_nets": True,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }
    if contract["authorization"] != expected_authorization:
        errors.append("native KiCad authorization boundary changed")

    generated_files = [
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_bytes(content.encode("utf-8")),
        }
        for path, content in sorted(outputs.items(), key=lambda item: str(item[0]))
    ]
    manifest = {
        "schema_version": 1,
        "artifact": "H2-R2-native-kicad-projects",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "sources": sources,
        "summary": {
            "project_count": len(project_summaries),
            "project_graph_sheet_count": sum(row["sheet_count"] for row in project_summaries),
            "populated_sheet_count": sum(row["populated_sheet_count"] for row in project_summaries),
            "fitted_symbol_instance_count": sum(row["instance_count"] for row in project_summaries),
            "physical_symbol_pin_count": physical_pin_count,
            "connected_physical_pin_count": connected_pin_count,
            "explicit_no_connect_physical_pin_count": no_connect_pin_count,
            "external_module_interface_annotation_count": external_count,
            "canonical_net_count": net_ledger["summary"]["unique_net_count"],
            "generated_file_count": len(generated_files),
            "pcb_file_count": 0,
        },
        "projects": project_summaries,
        "sheets": all_sheet_summaries,
        "generated_files": generated_files,
        "authorization": contract["authorization"],
        "errors": errors,
    }
    return outputs, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if manifest.get("errors"):
        for error in manifest["errors"]:
            print(f"ERROR: {error}")
        return 1
    contract = load(CONTRACT_PATH)
    manifest_path = ROOT / contract["manifest"]
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        manifest_path.write_text(manifest_text, encoding="utf-8")
        print(
            "wrote 2 native projects: "
            f"{manifest['summary']['fitted_symbol_instance_count']} symbols, "
            f"{manifest['summary']['physical_symbol_pin_count']} pins, "
            f"{manifest['summary']['canonical_net_count']} nets"
        )
        return 0
    stale = []
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
    if not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8") != manifest_text:
        stale.append(str(manifest_path.relative_to(ROOT)))
    if stale:
        print("stale: " + ", ".join(stale[:20]))
        return 1
    print(
        "ok: 2 native projects, 22 sheets, "
        f"{manifest['summary']['fitted_symbol_instance_count']} symbols, "
        f"{manifest['summary']['physical_symbol_pin_count']} pins"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
