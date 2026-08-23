#!/usr/bin/env python3
"""Generate and verify the exact H2.3.1 RF/power schematic hierarchy."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

from h2_ui_root import child_schematic, effects, stable_uuid


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
PROJECT_ID = "LESHY2-RF"
ROOT_SHEET = "RF_00_ROOT"
M1_SHEET = "RF_40_INTERBOARD_M1"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
ROOT_PATH = PROJECT_DIR / f"{PROJECT_ID}.kicad_sch"
OUTPUT = ECAD / "generated/H2-RF-root-interface.json"
IMPLEMENTED_CHILD_MANIFESTS = {
    "RF_01_USB_PD_CHARGE": ECAD / "generated/H2-RF01-usb-pd-charge.json",
    "RF_02_PACK_SAFETY_AON": ECAD / "generated/H2-RF02-pack-safety-aon.json",
    "RF_03_MAIN_RAILS_DOMAIN_GATES": ECAD / "generated/H2-RF03-main-rails-domain-gates.json",
    "RF_30_RP2354_CORE_SERVICE": ECAD / "generated/H2-RF30-rp2354-core-service.json",
    "RF_31_NRF24_X3": ECAD / "generated/H2-RF31-nrf24-x3.json",
    "RF_32_SUBGHZ_VOICE": ECAD / "generated/H2-RF32-subghz-voice.json",
    "RF_34_U214_M5_EXT": ECAD / "generated/H2-RF34-u214-m5-ext.json",
}
IMPLEMENTED_CHILD_STATUSES = {
    "RF_01_USB_PD_CHARGE": "reviewed_exact_usb_pd_charge_sheet",
    "RF_02_PACK_SAFETY_AON": "reviewed_exact_pack_safety_aon_sheet",
    "RF_03_MAIN_RAILS_DOMAIN_GATES": "reviewed_exact_main_rails_domain_gates_sheet",
    "RF_30_RP2354_CORE_SERVICE": "reviewed_exact_rp2354_core_service_sheet",
    "RF_31_NRF24_X3": "reviewed_exact_three_nrf24_sheet",
    "RF_32_SUBGHZ_VOICE": "reviewed_exact_electrical_subghz_voice_sheet",
    "RF_34_U214_M5_EXT": "reviewed_exact_u214_m5_expansion_sheet",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instance_name(endpoint: str) -> str | None:
    if endpoint.startswith("abstract:"):
        return None
    return endpoint.split(".", 1)[0]


def build_interfaces(candidate: dict, ledger: dict, contract: dict) -> dict[str, list[str]]:
    sheets = next(
        project["sheets"] for project in contract["projects"]
        if project["id"] == PROJECT_ID
    )
    children = set(sheets) - {ROOT_SHEET}
    instance_sheets = {
        row["instance"]: row["sheet"] for row in ledger["rows"]
        if row["project"] == PROJECT_ID
    }
    m1_nets = {row["net"] for row in candidate["interboard_contract"]["pin_map"]}
    net_sheets: dict[str, set[str]] = defaultdict(set)
    for route in candidate["fixed_routes"]:
        net = route["net"]
        if net == "NO_CONNECT" or net.endswith("_NC"):
            continue
        for endpoint in (route["from"], route["to"]):
            instance = instance_name(endpoint)
            if instance in instance_sheets and instance_sheets[instance] in children:
                net_sheets[net].add(instance_sheets[instance])
        if net in m1_nets:
            net_sheets[net].add(M1_SHEET)
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
            if instance in instance_sheets and instance_sheets[instance] in children:
                net_sheets[net].add(instance_sheets[instance])
        if net in m1_nets:
            net_sheets[net].add(M1_SHEET)
    for test_point in contract.get("test_point_contracts", []):
        if test_point.get("project") != PROJECT_ID:
            continue
        net_sheets[test_point["net"]].update(
            {test_point["owner_sheet"], test_point["test_sheet"]}
        )
    interfaces: dict[str, list[str]] = defaultdict(list)
    for net, owners in net_sheets.items():
        if len(owners) < 2:
            continue
        for sheet in owners:
            interfaces[sheet].append(net)
    return {
        sheet: sorted(interfaces.get(sheet, []))
        for sheet in sheets if sheet != ROOT_SHEET
    }


def root_schematic(interfaces: dict[str, list[str]]) -> str:
    pin_positions: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{ROOT_SHEET}")}")',
        '\t(paper "A0" portrait)', "\t(lib_symbols)",
    ]
    root_uuid = stable_uuid(f"sheet:{ROOT_SHEET}")
    y_cursor = 20.32
    for sheet_index, (sheet, nets) in enumerate(interfaces.items()):
        x, y, width = 20.32, y_cursor, 254.00
        height = max(45.72, 15.24 + len(nets) * 2.54)
        y_cursor += height + 5.08
        sheet_uuid = stable_uuid(f"hierarchy:{sheet}")
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
            pin_x, pin_y = x + width, y + 7.62 + pin_index * 2.54
            pin_positions[net].append((pin_x, pin_y, sheet))
            lines += [
                f'\t\t(pin "{net}" bidirectional',
                f"\t\t\t(at {pin_x:.2f} {pin_y:.2f} 0)",
                f"\t\t\t{effects()}",
                f'\t\t\t(uuid "{stable_uuid(f"root-pin:{sheet}:{net}")}")',
                "\t\t)",
            ]
        lines += [
            "\t\t(instances", f'\t\t\t(project "{PROJECT_ID}"',
            f'\t\t\t\t(path "/{root_uuid}/{sheet_uuid}"',
            f'\t\t\t\t\t(page "{sheet_index + 2}")',
            "\t\t\t\t)", "\t\t\t)", "\t\t)", "\t)",
        ]
    for net_index, (net, positions) in enumerate(sorted(pin_positions.items())):
        rail_x = 299.72 + net_index * 2.54
        for pin_x, pin_y, sheet in positions:
            lines += [
                "\t(wire",
                f"\t\t(pts (xy {pin_x:.2f} {pin_y:.2f}) (xy {rail_x:.2f} {pin_y:.2f}))",
                "\t\t(stroke (width 0) (type default))",
                f'\t\t(uuid "{stable_uuid(f"root-branch:{sheet}:{net}")}")', "\t)",
                f"\t(junction (at {rail_x:.2f} {pin_y:.2f})",
                "\t\t(diameter 0)", "\t\t(color 0 0 0 0)",
                f'\t\t(uuid "{stable_uuid(f"root-junction:{sheet}:{net}")}")', "\t)",
            ]
        y_values = [position[1] for position in positions]
        lines += [
            "\t(wire",
            f"\t\t(pts (xy {rail_x:.2f} {min(y_values):.2f}) (xy {rail_x:.2f} {max(y_values):.2f}))",
            "\t\t(stroke (width 0) (type default))",
            f'\t\t(uuid "{stable_uuid(f"root-rail:{net}")}")', "\t)",
        ]
    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")',
        "\t\t)", "\t)", "\t(embedded_fonts no)", ")", "",
    ]
    return "\n".join(lines)


def outputs() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    interfaces = build_interfaces(candidate, ledger, contract)
    expected_sheets = {
        sheet for project in contract["projects"] if project["id"] == PROJECT_ID
        for sheet in project["sheets"] if sheet != ROOT_SHEET
    }
    if set(interfaces) != expected_sheets:
        raise ValueError("RF/power root sheet set differs from the reviewed sheet contract")
    implemented_children = {}
    for sheet, manifest_path in IMPLEMENTED_CHILD_MANIFESTS.items():
        sheet_path = PROJECT_DIR / f"{sheet}.kicad_sch"
        if not manifest_path.is_file() or not sheet_path.is_file():
            continue
        child = json.loads(manifest_path.read_text(encoding="utf-8"))
        if child.get("status") == IMPLEMENTED_CHILD_STATUSES[sheet]:
            implemented_children[sheet] = child
    generated = {ROOT_PATH: root_schematic(interfaces)}
    for sheet, nets in interfaces.items():
        sheet_path = PROJECT_DIR / f"{sheet}.kicad_sch"
        generated[sheet_path] = (
            sheet_path.read_text(encoding="utf-8")
            if sheet in implemented_children else child_schematic(sheet, nets)
        )
    net_sheets: dict[str, list[str]] = defaultdict(list)
    for sheet, nets in interfaces.items():
        for net in nets:
            net_sheets[net].append(sheet)
    manifest = {
        "schema_version": 1,
        "stage": "H2.3.1",
        "status": "reviewed_rf_power_root_hierarchy",
        "project": PROJECT_ID,
        "root_sheet": ROOT_SHEET,
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
                1 for sheet, nets in interfaces.items()
                if sheet not in implemented_children for net in nets
                if not any(net in interfaces[item] for item in implemented_children)
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
            "known_deferred_fixture_erc_violations": sum(
                len(child.get("known_deferred_fixture_labels", []))
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
            "derivation": "RF/power fixed-route endpoints, allocated contacts and exact M1 contact membership",
            "pin_type": "bidirectional at H2.3.1; exact electrical pin types close with each functional sheet",
            "no_hidden_cross_sheet_globals": True,
            "no_no_connect_aggregation": True,
            "root_is_component_free": True,
            "root_page": "A0 portrait; all sheet bodies and 133 net rails remain inside the page",
            "implemented_children_are_preserved": sorted(implemented_children),
        },
        "review_boundary": {
            "complete": [
                "all twelve RF/power child sheets are instantiated by the KiCad root",
                "all 133 derived cross-sheet nets are represented by 305 explicit named pins and child labels",
                "one direct root rail joins only sheet pins carrying the same reviewed net name",
                "the 51-net RF/power side of M1 is represented without reserves or implicit globals",
                "native KiCad accepts the hierarchy with the exact remaining component-empty child-stub set",
            ],
            "deferred": [
                "functional circuit symbols and exact electrical sheet-pin directions in H2.3.2-H2.3.13",
                "each exact child-stub finding disappears as its functional circuit sheet is placed",
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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf-root-") as temp:
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
        report = staged / "root-erc.json"
        result = subprocess.run(
            [
                cli, "sch", "erc", "--format", "json", "--severity-all",
                "-o", str(report), str(staged / ROOT_PATH.name),
            ],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected the RF/power hierarchy:\n{result.stdout}{result.stderr}")
        erc = json.loads(report.read_text(encoding="utf-8"))
        violations = [
            violation for sheet in erc.get("sheets", [])
            for violation in sheet.get("violations", [])
        ]
        implemented_children = set(manifest["rules"]["implemented_children_are_preserved"])
        implemented_nets = {
            net for row in manifest["sheets"] if row["id"] in implemented_children
            for net in row["interfaces"]
        }
        expected_labels = {
            stable_uuid(f"child-label:{row['id']}:{net}")
            for row in manifest["sheets"] if row["id"] not in implemented_children
            for net in row["interfaces"] if net not in implemented_nets
        }
        expected_mismatches = {
            instance["symbol_uuid"]
            for path in IMPLEMENTED_CHILD_MANIFESTS.values() if path.is_file()
            for child in [json.loads(path.read_text(encoding="utf-8"))]
            if child.get("status") == IMPLEMENTED_CHILD_STATUSES.get(child.get("sheet"))
            for instance in child["instances"]
        }
        expected_isolated = {
            row["label_uuid"]
            for path in IMPLEMENTED_CHILD_MANIFESTS.values() if path.is_file()
            for child in [json.loads(path.read_text(encoding="utf-8"))]
            if child.get("status") == IMPLEMENTED_CHILD_STATUSES.get(child.get("sheet"))
            for row in child.get("known_deferred_fixture_labels", [])
        }
        actual_labels = {
            violation["items"][0]["uuid"] for violation in violations
            if violation.get("type") == "label_dangling"
            and len(violation.get("items", [])) == 1
        }
        actual_mismatches = {
            violation["items"][0]["uuid"] for violation in violations
            if violation.get("type") == "lib_symbol_mismatch"
            and len(violation.get("items", [])) == 1
        }
        actual_isolated = {
            violation["items"][0]["uuid"] for violation in violations
            if violation.get("type") == "isolated_pin_label"
            and len(violation.get("items", [])) == 1
        }
        if (
            len(violations) != len(expected_labels) + len(expected_mismatches) + len(expected_isolated)
            or actual_labels != expected_labels
            or actual_mismatches != expected_mismatches
            or actual_isolated != expected_isolated
        ):
            raise RuntimeError(
                "RF/power ERC differs from the exact reviewed finding sets: "
                f"violations={len(violations)}, expected-stubs={len(expected_labels)}, "
                f"expected-generated-symbol-warnings={len(expected_mismatches)}, "
                f"expected-deferred-fixture-boundaries={len(expected_isolated)}"
            )
    print("ok: KiCad parsed the exact RF/power hierarchy and accounted every reviewed finding")


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    expected = {
        "child_sheet_count": 12, "cross_sheet_net_count": 133,
        "root_hierarchical_pin_count": 305,
        "child_hierarchical_label_count": 305,
        "known_child_stub_erc_violations": 46,
        "implemented_child_sheet_count": 7, "circuit_symbols_placed": 507,
        "known_generated_library_copy_warnings": 507,
        "known_deferred_fixture_erc_violations": 8, "pcb_files_created": 0,
    }
    if summary != expected:
        raise ValueError(f"reviewed H2.3.1 interface accounting drifted: {summary}")
    root = generated[ROOT_PATH]
    if root.count("\n\t(sheet\n") != 12:
        raise ValueError("RF/power root child-sheet count mismatch")
    if root.count("\n\t\t(pin \"") != 305:
        raise ValueError("RF/power root hierarchical-pin count mismatch")
    if root.count("\n\t(wire\n") != 438 or root.count("\n\t(junction ") != 305:
        raise ValueError("RF/power root rail accounting mismatch")
    labels = sum(
        content.count("\n\t(hierarchical_label \"")
        for path, content in generated.items()
        if path.suffix == ".kicad_sch" and path != ROOT_PATH
    )
    if labels != 305:
        raise ValueError("RF/power child-label count mismatch")
    if "\n\t(label \"" in root or "\n\t(global_label \"" in root:
        raise ValueError("RF/power root may not hide interfaces behind labels")
    required = {
        "POWER_GROUND", "SAFETY_GROUND", "PROTECTED_PACK_POSITIVE",
        "AON_SAFE_3V3", "3V3_MAIN", "RUN_PERMIT", "POWER_FAULT_N",
        "RF_RESET_KILL_GATE", "S3_USB_DP", "S3_USB_DM", "S3_RP_IPC_SCK",
        "SYS_I2C_SDA", "SYS_I2C_SCL",
        "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2", "EV_N5_CC",
        "EV_N6_VOICE", "EV_N8_LORA_EXT", "FAULT_LATCH_SENSE_AON",
    }
    actual = {row["name"] for row in manifest["nets"]}
    if not required <= actual:
        raise ValueError(f"RF/power root omits required interfaces: {sorted(required - actual)}")
    m1 = next(row for row in manifest["sheets"] if row["id"] == M1_SHEET)
    if m1["interface_count"] != 51:
        raise ValueError("RF/power M1 hierarchy must expose exactly 51 unique nets")


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
        print("ok: H2.3.1 RF/power root hierarchy is current")
    if args.kicad_check:
        parse_check(generated, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
