#!/usr/bin/env python3
"""Generate and verify the reviewed H2.2.1 UI schematic hierarchy.

The root is intentionally component-free.  It instantiates every reviewed UI
functional sheet and exposes every net which crosses between two UI sheets.
The interface set is derived from both the architecture route graph and the
reviewed controller allocation graph, plus the exact M1 contact map.  The
allocation graph is required because a controller-to-peer assignment is an
electrical connection even when the verbose fixed-route table has no duplicate
entry for that direct digital link.
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
IMPLEMENTED_CHILD_MANIFESTS = {
    "UI_10_S3_CORE_MEMORY_BOOT": ECAD / "generated/H2-UI10-S3-core.json",
    "UI_11_DISPLAY_TOUCH_STORAGE": ECAD / "generated/H2-UI11-display-touch-storage.json",
    "UI_12_CONTROLS_INDICATORS": ECAD / "generated/H2-UI12-controls-indicators.json",
    "UI_13_AUDIO_CODEC_HEADSET": ECAD / "generated/H2-UI13-audio-codec-headset.json",
    "UI_20_C5_RADIO_IR_SERVICE": ECAD / "generated/H2-UI20-c5-radio-ir-service.json",
    "UI_21_FM_AM_RECEIVER": ECAD / "generated/H2-UI21-fm-am-receiver.json",
    "UI_40_INTERBOARD_M1": ECAD / "generated/H2-UI40-interboard-m1.json",
    "UI_50_TX_SAFETY_EVIDENCE": ECAD / "generated/H2-UI50-tx-safety-evidence.json",
    "UI_60_TESTPOINTS_MANUFACTURING": ECAD / "generated/H2-UI60-testpoints-manufacturing.json",
}
IMPLEMENTED_CHILD_STATUSES = {
    "UI_10_S3_CORE_MEMORY_BOOT": "reviewed_exact_s3_core_sheet",
    "UI_11_DISPLAY_TOUCH_STORAGE": "reviewed_exact_display_touch_storage_sheet",
    "UI_12_CONTROLS_INDICATORS": "reviewed_exact_controls_indicators_sheet",
    "UI_13_AUDIO_CODEC_HEADSET": "reviewed_exact_audio_codec_headset_sheet",
    "UI_20_C5_RADIO_IR_SERVICE": "reviewed_exact_c5_radio_ir_service_sheet",
    "UI_21_FM_AM_RECEIVER": "reviewed_exact_fm_am_receiver_sheet",
    "UI_40_INTERBOARD_M1": "reviewed_exact_ui_interboard_m1_sheet",
    "UI_50_TX_SAFETY_EVIDENCE": "reviewed_exact_ui_tx_safety_evidence_sheet",
    "UI_60_TESTPOINTS_MANUFACTURING": "reviewed_exact_ui_testpoints_manufacturing_sheet",
}
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
    for test_point in sheet_contract.get("test_point_contracts", []):
        if test_point.get("project") != "LESHY2-UI":
            continue
        net_sheets[test_point["net"]].update(
            {test_point["owner_sheet"], test_point["test_sheet"]}
        )
    for allocation in candidate["allocations"]:
        net = allocation["net"]
        if net == "NO_CONNECT" or net.endswith("_NC"):
            continue
        endpoints = [
            f"{allocation['instance']}.{allocation['contact']}",
            *allocation.get("peers", []),
        ]
        for endpoint in endpoints:
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
    implemented_children = {}
    for sheet, manifest_path in IMPLEMENTED_CHILD_MANIFESTS.items():
        sheet_path = PROJECT_DIR / f"{sheet}.kicad_sch"
        if not manifest_path.is_file() or not sheet_path.is_file():
            continue
        child_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if child_manifest.get("status") != IMPLEMENTED_CHILD_STATUSES[sheet]:
            continue
        implemented_children[sheet] = child_manifest
    generated = {ROOT_PATH: root_schematic(interfaces)}
    for sheet, nets in interfaces.items():
        sheet_path = PROJECT_DIR / f"{sheet}.kicad_sch"
        generated[sheet_path] = (
            sheet_path.read_text(encoding="utf-8")
            if sheet in implemented_children
            else child_schematic(sheet, nets)
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
            "known_child_stub_erc_violations": sum(
                1
                for sheet, nets in interfaces.items()
                if sheet not in implemented_children
                for net in nets
                if not any(net in interfaces[implemented] for implemented in implemented_children)
            ),
            "implemented_child_sheet_count": len(implemented_children),
            "circuit_symbols_placed": sum(
                child["summary"]["schematic_symbols"]
                for child in implemented_children.values()
            ),
            "known_generated_library_copy_warnings": sum(
                child["summary"]["schematic_symbols"]
                for child in implemented_children.values()
            ),
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
            "derivation": "fixed-route endpoints, allocated contacts and exact M1 contact membership",
            "pin_type": "bidirectional at H2.2.1; exact electrical pin types close with each implemented functional sheet",
            "no_hidden_cross_sheet_globals": True,
            "no_no_connect_aggregation": True,
            "root_is_component_free": True,
            "implemented_children_are_preserved": sorted(implemented_children),
            "generated_library_copy_warning_proof": "the controlled and embedded symbol definitions are generated from one object; validation requires one lib_symbol_mismatch per generated symbol and rejects every other mismatch/finding",
        },
        "review_boundary": {
            "complete": [
                "all nine UI child sheets instantiated by the KiCad root",
                "all 95 derived cross-sheet nets represented by 232 explicit named pins and child labels",
                "one direct root rail joins only sheet pins carrying the same reviewed net name",
                "native KiCad parser accepts the complete UI hierarchy; exact remaining child stubs and generated-library copy warnings are machine-accounted",
            ],
            "deferred": [
                "RF/power-board functional circuit symbols and exact electrical sheet-pin directions in H2.3",
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
        staged_ecad = Path(temp) / "hardware/ecad"
        staged = staged_ecad / "kicad/LESHY2-UI"
        staged.mkdir(parents=True)
        for support in (
            PROJECT_DIR / "LESHY2-UI.kicad_pro",
            PROJECT_DIR / "sym-lib-table",
            PROJECT_DIR / "fp-lib-table",
        ):
            shutil.copy2(support, staged / support.name)
        shutil.copytree(ECAD / "libraries", staged_ecad / "libraries")
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
        implemented_children = set(manifest["rules"]["implemented_children_are_preserved"])
        implemented_nets = {
            net
            for row in manifest["sheets"]
            if row["id"] in implemented_children
            for net in row["interfaces"]
        }
        expected_label_uuids = {
            stable_uuid(f"child-label:{row['id']}:{net}")
            for row in manifest["sheets"]
            if row["id"] not in implemented_children
            for net in row["interfaces"]
            if net not in implemented_nets
        }
        expected_mismatch_uuids = {
            instance["symbol_uuid"]
            for path in IMPLEMENTED_CHILD_MANIFESTS.values()
            if path.is_file()
            for child in [json.loads(path.read_text(encoding="utf-8"))]
            if child.get("status") == IMPLEMENTED_CHILD_STATUSES.get(child.get("sheet"))
            for instance in child["instances"]
        }
        actual_label_uuids = {
            violation["items"][0]["uuid"]
            for violation in violations
            if violation.get("type") == "label_dangling"
            and len(violation.get("items", [])) == 1
        }
        actual_mismatch_uuids = {
            violation["items"][0]["uuid"]
            for violation in violations
            if violation.get("type") == "lib_symbol_mismatch"
            and len(violation.get("items", [])) == 1
        }
        if (
            len(violations) != len(expected_label_uuids) + len(expected_mismatch_uuids)
            or actual_label_uuids != expected_label_uuids
            or actual_mismatch_uuids != expected_mismatch_uuids
        ):
            raise RuntimeError(
                "UI ERC differs from the exact reviewed finding sets: "
                f"violations={len(violations)}, expected-stubs={len(expected_label_uuids)}, "
                f"expected-generated-symbol-warnings={len(expected_mismatch_uuids)}"
            )
    if manifest["summary"]["known_child_stub_erc_violations"]:
        print(
            "ok: KiCad parsed the live UI hierarchy; only exact unimplemented child "
            "stubs and generated-library copy warnings remain"
        )
    else:
        print(
            "ok: KiCad parsed the complete UI hierarchy with no unimplemented child "
            "stubs; only exact generated-library copy warnings remain"
        )


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
        "cross_sheet_net_count": 95,
        "root_hierarchical_pin_count": 232,
        "child_hierarchical_label_count": 232,
        "known_child_stub_erc_violations": 0,
        "implemented_child_sheet_count": 9,
        "circuit_symbols_placed": 387,
        "known_generated_library_copy_warnings": 387,
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
    mode.add_argument("--write-interface-contract", action="store_true")
    parser.add_argument("--kicad-check", action="store_true")
    args = parser.parse_args()
    generated, manifest = outputs()
    if args.write_interface_contract:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(generated[OUTPUT], encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        return 0
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
