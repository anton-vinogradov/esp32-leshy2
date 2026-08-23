#!/usr/bin/env python3
"""Generate and verify the reviewed H2.2.1 UI schematic hierarchy.

The root is intentionally component-free.  It instantiates every reviewed UI
functional sheet and exposes every net which crosses between two UI sheets.
The interface set is derived from the architecture route graph and the exact
M1 contact map, so a later circuit edit cannot silently invent or omit a
cross-sheet connection.
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
from collections import defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
ROOT_PATH = ECAD / "kicad/LESHY2-UI/LESHY2-UI.kicad_sch"
PROJECT_DIR = ROOT_PATH.parent
OUTPUT = ECAD / "generated/H2-UI-root-interface.json"
NAMESPACE = uuid.UUID("4ed50bf6-dbd9-44f6-a71f-9f07341b4db6")


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instance_name(endpoint: str) -> str | None:
    if endpoint.startswith("abstract:"):
        return None
    return endpoint.split(".", 1)[0]


def build_interfaces(candidate: dict, ledger: dict, sheet_contract: dict) -> dict[str, list[str]]:
    ui_sheets = next(
        project["sheets"]
        for project in sheet_contract["projects"]
        if project["id"] == "LESHY2-UI"
    )
    child_sheets = set(ui_sheets) - {"UI_00_ROOT"}
    instance_sheets = {
        row["instance"]: row["sheet"]
        for row in ledger["rows"]
        if row["project"] == "LESHY2-UI"
    }
    m1_nets = {row["net"] for row in candidate["interboard_contract"]["pin_map"]}
    net_sheets: dict[str, set[str]] = defaultdict(set)
    for route in candidate["fixed_routes"]:
        net = route["net"]
        if net == "NO_CONNECT" or net.endswith("_NC"):
            continue
        for endpoint in (route["from"], route["to"]):
            instance = instance_name(endpoint)
            if instance in instance_sheets:
                sheet = instance_sheets[instance]
                if sheet in child_sheets:
                    net_sheets[net].add(sheet)
        if net in m1_nets:
            net_sheets[net].add("UI_40_INTERBOARD_M1")
    interfaces: dict[str, list[str]] = defaultdict(list)
    for net, sheets in net_sheets.items():
        if len(sheets) < 2:
            continue
        for sheet in sheets:
            interfaces[sheet].append(net)
    return {
        sheet: sorted(interfaces.get(sheet, []))
        for sheet in ui_sheets
        if sheet != "UI_00_ROOT"
    }


def effects(justify: str | None = None, size: float = 1.27) -> str:
    suffix = f" (justify {justify})" if justify else ""
    return f'(effects (font (size {size:.2f} {size:.2f})){suffix})'


def child_schematic(sheet: str, nets: list[str]) -> str:
    lines = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{sheet}")}")',
        '\t(paper "A4")',
        "\t(lib_symbols)",
    ]
    midpoint = (len(nets) + 1) // 2
    for index, net in enumerate(nets):
        left = index < midpoint
        column_index = index if left else index - midpoint
        x = 20.32 if left else 190.50
        y = 20.32 + column_index * 5.08
        angle = 0 if left else 180
        justify = None if left else "right"
        lines += [
            f'\t(hierarchical_label "{net}"',
            "\t\t(shape bidirectional)",
            f"\t\t(at {x:.2f} {y:.2f} {angle})",
            f"\t\t{effects(justify)}",
            f'\t\t(uuid "{stable_uuid(f"child-label:{sheet}:{net}")}")',
            "\t)",
        ]
        stub_x = x + 5.08 if left else x - 5.08
        lines += [
            "\t(wire",
            f"\t\t(pts (xy {x:.2f} {y:.2f}) (xy {stub_x:.2f} {y:.2f}))",
            "\t\t(stroke (width 0) (type default))",
            f'\t\t(uuid "{stable_uuid(f"child-stub:{sheet}:{net}")}")',
            "\t)",
            f"\t(no_connect (at {stub_x:.2f} {y:.2f})",
            f'\t\t(uuid "{stable_uuid(f"child-stub-nc:{sheet}:{net}")}")',
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


def root_schematic(interfaces: dict[str, list[str]]) -> str:
    sheets = list(interfaces)
    pin_positions: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    lines = [
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid("sheet:UI_00_ROOT")}")',
        '\t(paper "A0")',
        "\t(lib_symbols)",
    ]
    root_uuid = stable_uuid("sheet:UI_00_ROOT")
    y_cursor = 25.40
    for sheet_index, sheet in enumerate(sheets):
        x = 25.40
        y = y_cursor
        width = 304.80
        height = max(45.72, 15.24 + len(interfaces[sheet]) * 2.54)
        y_cursor += height + 12.70
        sheet_uuid = stable_uuid(f"hierarchy:{sheet}")
        lines += [
            "\t(sheet",
            f"\t\t(at {x:.2f} {y:.2f})",
            f"\t\t(size {width:.2f} {height:.2f})",
            "\t\t(fields_autoplaced yes)",
            "\t\t(stroke (width 0) (type default))",
            "\t\t(fill (color 0 0 0 0.0000))",
            f'\t\t(uuid "{sheet_uuid}")',
            f'\t\t(property "Sheetname" "{sheet}"',
            f"\t\t\t(at {x:.2f} {y - 0.71:.4f} 0)",
            f"\t\t\t{effects('left bottom')}",
            "\t\t)",
            f'\t\t(property "Sheetfile" "{sheet}.kicad_sch"',
            f"\t\t\t(at {x:.2f} {y + height + 0.71:.4f} 0)",
            f"\t\t\t{effects('left top')}",
            "\t\t)",
        ]
        for pin_index, net in enumerate(interfaces[sheet]):
            pin_x = x + width
            pin_y = y + 7.62 + pin_index * 2.54
            pin_positions[net].append((pin_x, pin_y, sheet))
            lines += [
                f'\t\t(pin "{net}" bidirectional',
                f"\t\t\t(at {pin_x:.2f} {pin_y:.2f} 0)",
                f"\t\t\t{effects()}",
                f'\t\t\t(uuid "{stable_uuid(f"root-pin:{sheet}:{net}")}")',
                "\t\t)",
            ]
        lines += [
            "\t\t(instances",
            '\t\t\t(project "LESHY2-UI"',
            f'\t\t\t\t(path "/{root_uuid}/{sheet_uuid}"',
            f'\t\t\t\t\t(page "{sheet_index + 2}")',
            "\t\t\t\t)",
            "\t\t\t)",
            "\t\t)",
            "\t)",
        ]
    for net_index, (net, positions) in enumerate(sorted(pin_positions.items())):
        rail_x = 365.76 + net_index * 5.08
        for pin_x, pin_y, sheet in positions:
            lines += [
                "\t(wire",
                f"\t\t(pts (xy {pin_x:.2f} {pin_y:.2f}) (xy {rail_x:.2f} {pin_y:.2f}))",
                "\t\t(stroke (width 0) (type default))",
                f'\t\t(uuid "{stable_uuid(f"root-branch:{sheet}:{net}")}")',
                "\t)",
                f"\t(junction (at {rail_x:.2f} {pin_y:.2f})",
                "\t\t(diameter 0)",
                "\t\t(color 0 0 0 0)",
                f'\t\t(uuid "{stable_uuid(f"root-junction:{sheet}:{net}")}")',
                "\t)",
            ]
        y_values = [position[1] for position in positions]
        lines += [
            "\t(wire",
            f"\t\t(pts (xy {rail_x:.2f} {min(y_values):.2f}) (xy {rail_x:.2f} {max(y_values):.2f}))",
            "\t\t(stroke (width 0) (type default))",
            f'\t\t(uuid "{stable_uuid(f"root-rail:{net}")}")',
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


def outputs() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    sheet_contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    interfaces = build_interfaces(candidate, ledger, sheet_contract)
    expected_sheets = {
        sheet
        for project in sheet_contract["projects"]
        if project["id"] == "LESHY2-UI"
        for sheet in project["sheets"]
        if sheet != "UI_00_ROOT"
    }
    if set(interfaces) != expected_sheets:
        raise ValueError(
            f"UI root sheet set differs: missing {sorted(expected_sheets - set(interfaces))}, "
            f"unexpected {sorted(set(interfaces) - expected_sheets)}"
        )
    generated = {ROOT_PATH: root_schematic(interfaces)}
    generated.update(
        {
            PROJECT_DIR / f"{sheet}.kicad_sch": child_schematic(sheet, nets)
            for sheet, nets in interfaces.items()
        }
    )
    net_sheets: dict[str, list[str]] = defaultdict(list)
    for sheet, nets in interfaces.items():
        for net in nets:
            net_sheets[net].append(sheet)
    manifest = {
        "schema_version": 1,
        "stage": "H2.2.1",
        "status": "reviewed_ui_root_hierarchy",
        "project": "LESHY2-UI",
        "root_sheet": "UI_00_ROOT",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, LEDGER_PATH, SHEET_CONTRACT_PATH)
        },
        "summary": {
            "child_sheet_count": len(interfaces),
            "cross_sheet_net_count": len(net_sheets),
            "root_hierarchical_pin_count": sum(map(len, interfaces.values())),
            "child_hierarchical_label_count": sum(map(len, interfaces.values())),
            "known_child_stub_erc_violations": sum(map(len, interfaces.values())),
            "circuit_symbols_placed": 0,
            "pcb_files_created": 0,
        },
        "sheets": [
            {"id": sheet, "interface_count": len(nets), "interfaces": nets}
            for sheet, nets in interfaces.items()
        ],
        "nets": [
            {"name": net, "sheets": sorted(sheets)}
            for net, sheets in sorted(net_sheets.items())
        ],
        "rules": {
            "derivation": "fixed-route endpoints plus exact M1 contact membership",
            "pin_type": "bidirectional at H2.2.1; exact electrical pin types close with each implemented functional sheet",
            "no_hidden_cross_sheet_globals": True,
            "no_no_connect_aggregation": True,
            "root_is_component_free": True,
        },
        "review_boundary": {
            "complete": [
                "all nine UI child sheets instantiated by the KiCad root",
                "all 73 derived cross-sheet nets represented by explicit named pins and child labels",
                "one direct root rail joins only sheet pins carrying the same reviewed net name",
                "native KiCad parser accepts the complete UI hierarchy and the root has zero ERC violations",
            ],
            "deferred": [
                "functional circuit symbols and exact electrical sheet-pin directions in H2.2.2-H2.2.9",
                "the 180 exact child-stub label_dangling findings disappear as functional circuit pins are placed",
                "manufacturing test-point interfaces in H2.2.10",
                "final full-project ERC closure in H2.6",
                "all PCB placement, routing, fabrication and purchasing",
            ],
        },
    }
    generated[OUTPUT] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-ui-root-") as temp:
        staged = Path(temp) / "LESHY2-UI"
        staged.mkdir()
        for path, content in generated.items():
            if path.suffix == ".kicad_sch":
                (staged / path.name).write_text(content, encoding="utf-8")
        report = staged / "root-erc.json"
        result = subprocess.run(
            [
                cli, "sch", "erc", "--format", "json", "--severity-all",
                "-o", str(report), str(staged / ROOT_PATH.name),
            ],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected the UI hierarchy:\n{result.stdout}{result.stderr}")
        if not report.is_file():
            raise RuntimeError("KiCad did not produce the UI root ERC report")
        erc = json.loads(report.read_text(encoding="utf-8"))
        violations = [
            violation
            for sheet in erc.get("sheets", [])
            for violation in sheet.get("violations", [])
        ]
        expected_label_uuids = {
            stable_uuid(f"child-label:{row['id']}:{net}")
            for row in manifest["sheets"]
            for net in row["interfaces"]
        }
        actual_label_uuids = {
            violation["items"][0]["uuid"]
            for violation in violations
            if violation.get("type") == "label_dangling"
            and len(violation.get("items", [])) == 1
        }
        if (
            len(violations) != len(expected_label_uuids)
            or actual_label_uuids != expected_label_uuids
        ):
            raise RuntimeError(
                "child-stub ERC differs from the exact H2.2.1 interface set: "
                f"violations={len(violations)}, expected={len(expected_label_uuids)}"
            )
    print("ok: KiCad parsed H2.2.1; only the exact declared child-stub findings remain")


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    root = generated[ROOT_PATH]
    summary = manifest["summary"]
    if root.count("\n\t(sheet\n") != summary["child_sheet_count"]:
        raise ValueError("UI root child-sheet count mismatch")
    if root.count("\n\t\t(pin \"") != summary["root_hierarchical_pin_count"]:
        raise ValueError("UI root hierarchical-pin count mismatch")
    if "\n\t(label \"" in root or "\n\t(global_label \"" in root:
        raise ValueError("UI root may not hide interfaces behind labels")
    if root.count("\n\t(wire\n") != (
        summary["root_hierarchical_pin_count"] + summary["cross_sheet_net_count"]
    ):
        raise ValueError("UI root interface-wire count mismatch")
    if root.count("\n\t(junction ") != summary["root_hierarchical_pin_count"]:
        raise ValueError("UI root interface-junction count mismatch")
    child_labels = sum(
        text.count("\n\t(hierarchical_label \"")
        for path, text in generated.items()
        if path.suffix == ".kicad_sch" and path != ROOT_PATH
    )
    if child_labels != summary["child_hierarchical_label_count"]:
        raise ValueError("UI child hierarchical-label count mismatch")
    if summary != {
        "child_sheet_count": 9,
        "cross_sheet_net_count": 73,
        "root_hierarchical_pin_count": 180,
        "child_hierarchical_label_count": 180,
        "known_child_stub_erc_violations": 180,
        "circuit_symbols_placed": 0,
        "pcb_files_created": 0,
    }:
        raise ValueError(f"reviewed H2.2.1 interface accounting drifted: {summary}")
    for required in (
        "3V3_MAIN", "AON_SAFE_3V3", "POWER_GROUND", "SAFETY_GROUND",
        "S3_USB_DP", "S3_USB_DM", "SYS_I2C_SDA", "SYS_I2C_SCL",
        "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2", "EV_N5_CC",
        "EV_N6_VOICE", "EV_N8_LORA_EXT", "FAULT_LATCH_SENSE_AON",
    ):
        if not any(row["name"] == required for row in manifest["nets"]):
            raise ValueError(f"UI root omits required interface {required}")


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
        print("ok: H2.2.1 UI root hierarchy is current")
    if args.kicad_check:
        parse_check(generated, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
