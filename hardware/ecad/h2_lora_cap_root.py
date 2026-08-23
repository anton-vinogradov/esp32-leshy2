#!/usr/bin/env python3
"""Generate and verify the H2.4.2 LoRa Cap hierarchy and host boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_root import child_schematic, effects, stable_uuid as hierarchy_uuid
from h2_ui_s3_core import (
    Pin,
    library_symbol,
    schematic_symbol,
    stable_uuid as symbol_uuid,
)


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
ACCESSORY_PATH = REPO / "hardware/accessories/leshy2-lora-cap-01.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
PROJECT_ID = "LESHY2-LORA-CAP-01"
ROOT_SHEET = "CAP_00_ROOT"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
ROOT_PATH = PROJECT_DIR / f"{PROJECT_ID}.kicad_sch"
OUTPUT = ECAD / "generated/H2-CAP00-root-interface.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "CAP00"

INTERFACES = {
    "CAP_10_RADIO_CONTROL": [
        "CAP_3V3", "GND", "LORA_NRESET", "LORA_DIO1", "LORA_BUSY",
        "LORA_SCK", "LORA_MOSI", "LORA_MISO", "LORA_NSS",
        "RF_FORWARD_LEVEL",
    ],
    "CAP_20_POWER_BUS": [
        "5V_IN", "GND", "CAP_3V3", "IDENTITY_SCL", "IDENTITY_SDA",
    ],
    "CAP_30_TX_EVIDENCE": [
        "CAP_3V3", "GND", "RF_FORWARD_LEVEL", "EXT_TX_EVIDENCE_N",
    ],
}
IMPLEMENTED_CHILD_MANIFESTS = {
    "CAP_10_RADIO_CONTROL": ECAD / "generated/H2-CAP10-radio-control.json",
    "CAP_20_POWER_BUS": ECAD / "generated/H2-CAP20-power-bus.json",
    "CAP_30_TX_EVIDENCE": ECAD / "generated/H2-CAP30-tx-evidence.json",
}
IMPLEMENTED_CHILD_STATUSES = {
    "CAP_10_RADIO_CONTROL": "reviewed_exact_lora_radio_control_sheet",
    "CAP_20_POWER_BUS": "reviewed_exact_lora_power_identity_sheet",
    "CAP_30_TX_EVIDENCE": "reviewed_exact_lora_tx_evidence_sheet",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_pin_map(accessory: dict) -> dict[int, str]:
    result = {
        int(row["pin"]): str(row["custom_cap"])
        for row in accessory["pin_contract"]
    }
    if set(result) != set(range(1, 15)):
        raise ValueError("LoRa Cap host contract must contain pins 1..14 exactly once")
    expected = {
        1: "NC", 2: "NC", 3: "IDENTITY_SCL", 4: "IDENTITY_SDA",
        5: "EXT_TX_EVIDENCE_N", 6: "GND", 7: "5V_IN",
        8: "LORA_NRESET", 9: "LORA_DIO1", 10: "LORA_BUSY",
        11: "LORA_SCK", 12: "LORA_MOSI", 13: "LORA_MISO", 14: "LORA_NSS",
    }
    if result != expected:
        raise ValueError(f"LoRa Cap 14-contact contract drifted: {result}")
    return result


def header_pins(device: dict) -> list[Pin]:
    pins = [
        Pin(str(number), f"PIN_{number}", f"PIN_{number}")
        for number in range(1, 15)
    ]
    if set(device["contacts"]) != {pin.name for pin in pins}:
        raise ValueError("TSW-107-07-G-D device map is not exactly 14 contacts")
    return pins


def root_schematic(
    interfaces: dict[str, list[str]], host_map: dict[int, str], header_device: dict
) -> tuple[str, dict]:
    pins = header_pins(header_device)
    footprint = "Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical"
    lib, coords, _ = library_symbol(
        "cap_header", pins, "J", footprint,
        "exact 14-contact male Cap-Bus plug", True, True, True,
        SYMBOL_NAMESPACE,
    )
    header_x, header_y = 304.80, 101.60
    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{hierarchy_uuid(f"sheet:{ROOT_SHEET}")}")',
        '\t(paper "A2")', "\t(title_block",
        '\t\t(title "Leshy2 — optional LoRa Cap and exact 14-contact host boundary")',
        '\t\t(rev "H2.4.2")', "\t)", "\t(lib_symbols", lib, "\t)",
    ]
    lines.append(schematic_symbol(
        "cap_header", pins, "J1", header_device["mpn"], footprint,
        "exact 14-contact male Cap-Bus plug", header_x, header_y, coords,
        True, True, SYMBOL_NAMESPACE, PROJECT_ID, ROOT_SHEET,
    ))

    root_uuid = hierarchy_uuid(f"sheet:{ROOT_SHEET}")
    net_points: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    y_cursor = 20.32
    for sheet_index, (sheet, nets) in enumerate(interfaces.items()):
        x, y, width = 20.32, y_cursor, 152.40
        height = max(38.10, 15.24 + len(nets) * 2.54)
        y_cursor += height + 7.62
        sheet_uuid = hierarchy_uuid(f"hierarchy:{sheet}")
        lines += [
            "\t(sheet", f"\t\t(at {x:.2f} {y:.2f})",
            f"\t\t(size {width:.2f} {height:.2f})",
            "\t\t(fields_autoplaced yes)",
            "\t\t(stroke (width 0) (type default))",
            "\t\t(fill (color 0 0 0 0.0000))",
            f'\t\t(uuid "{sheet_uuid}")',
            f'\t\t(property "Sheetname" "{sheet}"',
            f"\t\t\t(at {x:.2f} {y - 0.71:.4f} 0)",
            f"\t\t\t{effects('left bottom')}", "\t\t)",
            f'\t\t(property "Sheetfile" "{sheet}.kicad_sch"',
            f"\t\t\t(at {x:.2f} {y + height + 0.71:.4f} 0)",
            f"\t\t\t{effects('left top')}", "\t\t)",
        ]
        for pin_index, net in enumerate(nets):
            px, py = x + width, y + 7.62 + pin_index * 2.54
            net_points[net].append((px, py, f"sheet:{sheet}"))
            lines += [
                f'\t\t(pin "{net}" bidirectional',
                f"\t\t\t(at {px:.2f} {py:.2f} 0)", f"\t\t\t{effects()}",
                f'\t\t\t(uuid "{hierarchy_uuid(f"root-pin:{sheet}:{net}")}")',
                "\t\t)",
            ]
        lines += [
            "\t\t(instances", f'\t\t\t(project "{PROJECT_ID}"',
            f'\t\t\t\t(path "/{root_uuid}/{sheet_uuid}"',
            f'\t\t\t\t\t(page "{sheet_index + 2}")',
            "\t\t\t\t)", "\t\t\t)", "\t\t)", "\t)",
        ]

    no_connects = []
    header_point_by_net = {}
    for pin in pins:
        px, py, side = coords[pin.number]
        x, y = header_x + px, header_y - py
        net = host_map[int(pin.number)]
        if net == "NC":
            lines += [
                f"\t(no_connect (at {x:.2f} {y:.2f})",
                f'\t\t(uuid "{symbol_uuid(f"nc:cap_header:{pin.number}")}")', "\t)",
            ]
            no_connects.append(f"cap_header.PIN_{pin.number}")
            continue
        net_points[net].append((x, y, f"header:{pin.number}"))
        header_point_by_net[net] = {"pin": int(pin.number), "side": side, "x": x, "y": y}

    net_rails = {}
    left_index = right_index = 0
    for net in sorted(net_points):
        header = header_point_by_net.get(net)
        if header and header["side"] == "right":
            rail_x = 340.36 + right_index * 2.54
            right_index += 1
        else:
            rail_x = 200.66 + left_index * 2.54
            left_index += 1
        net_rails[net] = rail_x
        for x, y, owner in net_points[net]:
            lines += [
                "\t(wire", f"\t\t(pts (xy {x:.2f} {y:.2f}) (xy {rail_x:.2f} {y:.2f}))",
                "\t\t(stroke (width 0) (type default))",
                f'\t\t(uuid "{hierarchy_uuid(f"root-branch:{owner}:{net}")}")', "\t)",
                f"\t(junction (at {rail_x:.2f} {y:.2f})", "\t\t(diameter 0)",
                "\t\t(color 0 0 0 0)",
                f'\t\t(uuid "{hierarchy_uuid(f"root-junction:{owner}:{net}")}")', "\t)",
            ]
        ys = [point[1] for point in net_points[net]]
        lines += [
            "\t(wire",
            f"\t\t(pts (xy {rail_x:.2f} {min(ys):.2f}) (xy {rail_x:.2f} {max(ys):.2f}))",
            "\t\t(stroke (width 0) (type default))",
            f'\t\t(uuid "{hierarchy_uuid(f"root-rail:{net}")}")', "\t)",
        ]
    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    metadata = {
        "header_footprint": footprint,
        "header_symbol_uuid": symbol_uuid("symbol:cap_header"),
        "no_connects": no_connects,
        "net_rails": net_rails,
        "root_wire_count": sum(len(points) + 1 for points in net_points.values()),
        "root_junction_count": sum(len(points) for points in net_points.values()),
    }
    return "\n".join(lines), metadata


def outputs() -> tuple[dict[Path, str], dict]:
    accessory = json.loads(ACCESSORY_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    sheets = next(
        project["sheets"] for project in contract["projects"]
        if project["id"] == PROJECT_ID
    )
    if sheets != [ROOT_SHEET, *INTERFACES]:
        raise ValueError("LoRa Cap sheet graph differs from the reviewed contract")
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == ROOT_SHEET
    ]
    if len(rows) != 1 or rows[0]["instance"] != "cap_header":
        raise ValueError("CAP_00_ROOT must own only the exact Cap-Bus header")
    header_device = devices[rows[0]["device_key"]]
    host_map = host_pin_map(accessory)
    root, root_metadata = root_schematic(INTERFACES, host_map, header_device)

    implemented_children = {}
    for sheet, manifest_path in IMPLEMENTED_CHILD_MANIFESTS.items():
        path = PROJECT_DIR / f"{sheet}.kicad_sch"
        if not manifest_path.is_file() or not path.is_file():
            continue
        child = json.loads(manifest_path.read_text(encoding="utf-8"))
        if child.get("status") == IMPLEMENTED_CHILD_STATUSES[sheet]:
            implemented_children[sheet] = child
    generated = {ROOT_PATH: root}
    for sheet, nets in INTERFACES.items():
        path = PROJECT_DIR / f"{sheet}.kicad_sch"
        generated[path] = (
            path.read_text(encoding="utf-8")
            if sheet in implemented_children else child_schematic(sheet, nets)
        )
    generated[SYMBOL_LIBRARY] = build_symbol_library(generated)

    net_sheets: dict[str, list[str]] = defaultdict(list)
    for sheet, nets in INTERFACES.items():
        for net in nets:
            net_sheets[net].append(sheet)
    manifest = {
        "schema_version": 1,
        "stage": "H2.4.2",
        "status": "reviewed_exact_lora_cap_root",
        "project": PROJECT_ID,
        "root_sheet": ROOT_SHEET,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (ACCESSORY_PATH, DEVICES_PATH, LEDGER_PATH, SHEET_CONTRACT_PATH)
        },
        "summary": {
            "root_ledger_instances": len(rows),
            "root_schematic_symbols": 1,
            "child_sheet_count": len(INTERFACES),
            "unique_root_nets": len(net_sheets),
            "root_hierarchical_pin_count": sum(map(len, INTERFACES.values())),
            "child_hierarchical_label_count": sum(map(len, INTERFACES.values())),
            "host_physical_contacts": len(host_map),
            "host_connected_contacts": sum(net != "NC" for net in host_map.values()),
            "host_reserved_no_connects": sum(net == "NC" for net in host_map.values()),
            "implemented_child_sheet_count": len(implemented_children),
            "known_child_stub_erc_violations": sum(
                1 for sheet, nets in INTERFACES.items()
                if sheet not in implemented_children for net in nets
                if net not in set(host_map.values())
                if not any(net in INTERFACES[item] for item in implemented_children)
            ),
            "known_generated_library_copy_warnings": 1 + sum(
                child["summary"]["schematic_symbols"] for child in implemented_children.values()
            ),
            "pcb_files_created": 0,
        },
        "host_connector": {
            "instance": "cap_header", "reference": "J1", "mpn": header_device["mpn"],
            "symbol_uuid": root_metadata["header_symbol_uuid"],
            "footprint": root_metadata["header_footprint"],
            "pin_map": [
                {
                    **row,
                    "root_net": host_map[int(row["pin"])],
                    "disposition": "intentional_no_connect" if host_map[int(row["pin"])] == "NC" else "connected",
                }
                for row in accessory["pin_contract"]
            ],
        },
        "intentional_no_connect_endpoints": root_metadata["no_connects"],
        "sheets": [
            {"id": sheet, "interface_count": len(nets), "interfaces": nets}
            for sheet, nets in INTERFACES.items()
        ],
        "nets": [
            {"name": net, "sheets": sorted(owners), "host_pin": next((pin for pin, value in host_map.items() if value == net), None)}
            for net, owners in sorted(net_sheets.items())
        ],
        "rules": {
            "host_contract_source": "hardware/accessories/leshy2-lora-cap-01.json#/pin_contract",
            "no_hidden_cross_sheet_globals": True,
            "root_owns_only_physical_host_connector": True,
            "implemented_children_are_preserved": sorted(implemented_children),
            "selected_header_footprint_matches": "2x7 rows, 2.54-mm pitch and 0.635-mm square through-hole posts",
        },
        "root_geometry_accounting": root_metadata,
        "review_boundary": {
            "complete": [
                "all three LoRa Cap child sheets are instantiated with nineteen explicit named hierarchy contacts",
                "the exact 14-contact custom-Cap map is fixed to J1 pins 1..14 and matches the host-side contract",
                "reserved stock-GPS contacts J1.1/J1.2 are explicit no-connects rather than invented functions",
                "all twelve used host contacts and both Cap-local cross-sheet nets join children through visible root wires",
                "native KiCad parses the complete root hierarchy with only exact generated-symbol copy findings",
            ],
            "deferred": [
                "connector placement, drill tolerances, routing, retention-hole clearance and DRC in H6",
                "installed-Cap mating, power, identity, RF and evidence HIL in H8",
            ],
        },
    }
    generated[OUTPUT] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    fixed = {
        "root_ledger_instances": 1,
        "root_schematic_symbols": 1,
        "child_sheet_count": 3,
        "unique_root_nets": 14,
        "root_hierarchical_pin_count": 19,
        "child_hierarchical_label_count": 19,
        "host_physical_contacts": 14,
        "host_connected_contacts": 12,
        "host_reserved_no_connects": 2,
        "pcb_files_created": 0,
    }
    if any(manifest["summary"].get(key) != value for key, value in fixed.items()):
        raise ValueError(f"H2.4.2 fixed accounting drifted: {manifest['summary']}")
    implemented = set(manifest["rules"]["implemented_children_are_preserved"])
    if manifest["summary"]["implemented_child_sheet_count"] != len(implemented):
        raise ValueError("LoRa Cap implemented-child accounting drifted")
    expected_warnings = 1 + sum(
        json.loads(IMPLEMENTED_CHILD_MANIFESTS[sheet].read_text(encoding="utf-8"))["summary"]["schematic_symbols"]
        for sheet in implemented
    )
    if manifest["summary"]["known_generated_library_copy_warnings"] != expected_warnings:
        raise ValueError("LoRa Cap generated-symbol warning accounting drifted")
    host_nets = {
        row["root_net"] for row in manifest["host_connector"]["pin_map"]
        if row["root_net"] != "NC"
    }
    implemented_nets = {net for sheet in implemented for net in INTERFACES[sheet]}
    expected_stubs = sum(
        1 for sheet, nets in INTERFACES.items() if sheet not in implemented
        for net in nets if net not in host_nets and net not in implemented_nets
    )
    if manifest["summary"]["known_child_stub_erc_violations"] != expected_stubs:
        raise ValueError("LoRa Cap child-stub warning accounting drifted")
    root = generated[ROOT_PATH]
    if root.count("\n\t(sheet\n") != 3 or root.count("\n\t(symbol\n") != 1:
        raise ValueError("LoRa Cap root sheet/symbol accounting mismatch")
    # 19 sheet pins plus the 14 instantiated J1 symbol pins use this syntax.
    if root.count("\n\t\t(pin \"") != 33 or root.count("\n\t(no_connect ") != 2:
        raise ValueError("LoRa Cap root pin/no-connect accounting mismatch")
    if root.count("\n\t(wire\n") != manifest["root_geometry_accounting"]["root_wire_count"]:
        raise ValueError("LoRa Cap root wire accounting mismatch")
    if root.count("\n\t(junction ") != manifest["root_geometry_accounting"]["root_junction_count"]:
        raise ValueError("LoRa Cap root junction accounting mismatch")
    labels = sum(
        content.count("\n\t(hierarchical_label \"")
        for path, content in generated.items()
        if path.suffix == ".kicad_sch" and path != ROOT_PATH
    )
    if labels != 19:
        raise ValueError("LoRa Cap child interface labels drifted")
    if len(manifest["host_connector"]["pin_map"]) != 14:
        raise ValueError("LoRa Cap host contact manifest drifted")


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def parse_check(generated: dict[Path, str], manifest: dict) -> None:
    cli = find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-cap-root-") as temp:
        staged_ecad = Path(temp) / "hardware/ecad"
        staged = staged_ecad / f"kicad/{PROJECT_ID}"
        staged.mkdir(parents=True)
        for support in (
            PROJECT_DIR / f"{PROJECT_ID}.kicad_pro",
            PROJECT_DIR / "sym-lib-table",
            PROJECT_DIR / "fp-lib-table",
        ):
            shutil.copy2(support, staged / support.name)
        shutil.copytree(ECAD / "libraries", staged_ecad / "libraries")
        for path, content in generated.items():
            if path.suffix == ".kicad_sch":
                (staged / path.name).write_text(content, encoding="utf-8")
            elif path == SYMBOL_LIBRARY:
                (staged_ecad / "libraries" / path.name).write_text(content, encoding="utf-8")
        report = staged / "root-erc.json"
        result = subprocess.run(
            [cli, "sch", "erc", "--format", "json", "--severity-all", "-o", str(report), str(staged / ROOT_PATH.name)],
            text=True, capture_output=True,
        )
        if result.returncode or not report.is_file():
            raise RuntimeError(f"KiCad rejected LoRa Cap hierarchy:\n{result.stdout}{result.stderr}")
        erc = json.loads(report.read_text(encoding="utf-8"))
        violations = [
            violation for sheet in erc.get("sheets", [])
            for violation in sheet.get("violations", [])
        ]
        implemented = set(manifest["rules"]["implemented_children_are_preserved"])
        implemented_nets = {
            net for sheet in implemented for net in INTERFACES[sheet]
        }
        host_nets = {
            row["root_net"] for row in manifest["host_connector"]["pin_map"]
            if row["root_net"] != "NC"
        }
        expected_labels = {
            hierarchy_uuid(f"child-label:{sheet}:{net}")
            for sheet, nets in INTERFACES.items() if sheet not in implemented
            for net in nets if net not in implemented_nets and net not in host_nets
        }
        expected_mismatches = {manifest["host_connector"]["symbol_uuid"]} | {
            instance["symbol_uuid"]
            for sheet, path in IMPLEMENTED_CHILD_MANIFESTS.items() if sheet in implemented
            for child in [json.loads(path.read_text(encoding="utf-8"))]
            for instance in child["instances"]
        }
        actual_labels = {
            violation["items"][0]["uuid"] for violation in violations
            if violation.get("type") == "label_dangling" and len(violation.get("items", [])) == 1
        }
        actual_mismatches = {
            violation["items"][0]["uuid"] for violation in violations
            if violation.get("type") == "lib_symbol_mismatch" and len(violation.get("items", [])) == 1
        }
        if (
            len(violations) != len(expected_labels) + len(expected_mismatches)
            or actual_labels != expected_labels or actual_mismatches != expected_mismatches
        ):
            raise RuntimeError(
                "LoRa Cap ERC differs from exact root findings: "
                f"violations={len(violations)}, stubs={len(expected_labels)}, symbols={len(expected_mismatches)}, "
                f"types={[row.get('type') for row in violations]}"
            )
    print("ok: KiCad parsed H2.4.2 LoRa Cap hierarchy and exact host boundary")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--kicad-check", action="store_true")
    args = parser.parse_args()
    generated, manifest = outputs()
    structural_check(generated, manifest)
    if args.write:
        for path, content in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [
            path for path, content in generated.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print("ok: H2.4.2 LoRa Cap root hierarchy is current")
    if args.kicad_check:
        parse_check(generated, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
