#!/usr/bin/env python3
"""Generate and verify the exact H2.3.11 RF-side 80-contact M1 sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import Pin, effects, escaped, library_symbol, schematic_symbol, scoped_reference, stable_uuid


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-RF-root-interface.json"
UI_MANIFEST_PATH = ECAD / "generated/H2-UI40-interboard-m1.json"
SHEET_ID = "RF_40_INTERBOARD_M1"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF40-interboard-m1.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF40"
FOOTPRINT = "Connector_Hirose_FX8:Hirose_FX8-80S-SV_2x40_P0.6mm"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    ui_manifest = json.loads(UI_MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 1 or rows[0]["instance"] != "m1_rf_receptacle":
        raise ValueError(f"{SHEET_ID} must own only m1_rf_receptacle, got {rows}")
    device = devices[rows[0]["device_key"]]
    pin_map = candidate["interboard_contract"]["pin_map"]
    connector = candidate["interboard_contract"]["connector_pair"]
    accounting = candidate["interboard_contract"]["accounting"]
    interfaces = set(next(
        row["interfaces"] for row in root_manifest["sheets"] if row["id"] == SHEET_ID
    ))
    if [row["contact"] for row in pin_map] != list(range(1, 81)):
        raise ValueError("M1 contact map must enumerate physical contacts 1..80")
    if len(device["contacts"]) != 80 or connector["positions"] != 80:
        raise ValueError("M1 device, pair and pin-map contact counts differ")
    if connector["rf_power_instance"] != "m1_rf_receptacle":
        raise ValueError("M1 connector-pair RF instance drifted")
    pins = [Pin(str(row["contact"]), row["net"], f"P{row['contact']}") for row in pin_map]
    library, coords, _ = library_symbol(
        "m1_rf_receptacle", pins, "J", FOOTPRINT, rows[0]["role"],
        True, True, True, SYMBOL_NAMESPACE,
    )
    x, y = 165.10, 132.08
    reference = scoped_reference(SHEET_ID, "J1")
    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A1")', "\t(title_block",
        '\t\t(title "Leshy2 — exact RF-side 80-contact M1 receptacle")',
        '\t\t(rev "H2.3.11")', "\t)", "\t(lib_symbols", library, "\t)",
        schematic_symbol(
            "m1_rf_receptacle", pins, reference, device["mpn"], FOOTPRINT, rows[0]["role"],
            x, y, coords, True, True, SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
        ),
    ]
    hierarchy_used: set[str] = set()
    contact_rows = []
    for source, pin in zip(pin_map, pins):
        px, py, side = coords[pin.number]
        point_x, point_y = x + px, y - py
        net = source["net"]
        hierarchical = net in interfaces and net not in hierarchy_used
        if hierarchical:
            hierarchy_used.add(net)
        token = "hierarchical_label" if hierarchical else "label"
        shape = "\n\t\t(shape bidirectional)" if hierarchical else ""
        angle = 0 if side == "left" else 180
        justify = None if side == "left" else "right bottom"
        lines += [
            f'\t({token} "{escaped(net)}"{shape}',
            f"\t\t(at {point_x:.2f} {point_y:.2f} {angle})",
            f"\t\t{effects(justify)}",
            f'\t\t(uuid "{stable_uuid(f"label:m1_rf_receptacle:{pin.number}:{net}")}")',
            "\t)",
        ]
        contact_rows.append({
            "contact": source["contact"], "symbol_pin": pin.number,
            "net": net, "direction": source["direction"],
            "signal_class": source["signal_class"],
        })
    if hierarchy_used != interfaces:
        raise ValueError(f"RF40 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
    if set(row["net"] for row in pin_map) != interfaces:
        raise ValueError("RF40 hierarchy differs from the exact M1 net set")
    if contact_rows != ui_manifest["contacts"]:
        raise ValueError("RF and UI M1 contact/net/direction/class maps differ")
    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    schematic = "\n".join(lines)
    manifest = {
        "schema_version": 1,
        "stage": "H2.3.11",
        "status": "reviewed_exact_rf_interboard_m1_sheet",
        "authority": {"baseline": "R1", "lifecycle": "historical_pre_r2_sheet_scaffold", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (
                CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH,
                ROOT_INTERFACE_PATH, UI_MANIFEST_PATH,
            )
        },
        "summary": {
            "ledger_instances": 1, "schematic_symbols": 1,
            "board_fitted_symbols": 1, "physical_contacts": len(pin_map),
            "unique_nets": len(set(row["net"] for row in pin_map)),
            "hierarchical_interfaces": len(interfaces),
            "power_ground_contacts": sum(row["net"] == "POWER_GROUND" for row in pin_map),
            "main_3v3_contacts": sum(row["net"] == "3V3_MAIN" for row in pin_map),
            "reserved_contacts": sum(row["signal_class"] == "reserved" for row in pin_map),
            "cross_project_contact_mismatches": 0,
            "intentional_no_connect_pins": 0, "pcb_files_created": 0,
        },
        "instances": [{
            "instance": "m1_rf_receptacle",
            "symbol_uuid": stable_uuid("symbol:m1_rf_receptacle"),
            "reference": reference, "mpn": device["mpn"], "footprint": FOOTPRINT,
            "pin_count": len(pins), "board_fitted": True,
        }],
        "contacts": contact_rows,
        "accounting_source": accounting,
        "cross_project_equality": {
            "ui_manifest": str(UI_MANIFEST_PATH.relative_to(REPO)),
            "status": "all_80_contact_net_direction_and_signal_class_rows_equal",
        },
        "footprint_evidence": [{
            "mpn": device["mpn"], "footprint": FOOTPRINT, "source": device["source"],
            "fit": "official FX8/FX8C common receptacle land pattern: 2x40 at 0.6-mm pitch, 0.35x1.50-mm lands and asymmetric locating holes; SV5 with the selected SV1 plug gives the reviewed 11-mm stack",
        }],
        "corrections_closed": [
            "the RF receptacle is a separate exact serial MPN and footprint; it is not mixed with the UI plug in one schematic node",
            "all 80 physical contacts are checked row-for-row against the reviewed UI-side manifest, including net, direction and signal class",
            "all 20 POWER_GROUND and seven 3V3_MAIN contacts stay physically separate instead of collapsing into aggregate connector pins",
            "the complete 80-contact budget contains no reserve or silent no-connect",
        ],
        "known_deferred_fixture_labels": [],
        "review_boundary": {
            "complete": [
                "all 80 RF-receptacle contacts are explicit numbered symbol pins",
                "all 51 unique M1 nets terminate the exact RF hierarchy interfaces",
                "RF and UI project manifests are bit-for-bit equal across all contact semantics",
                "the selected active SV5 receptacle and SV1 plug form the exact reviewed 11-mm mating pair",
                "native KiCad parses the live RF hierarchy with the exact M1 sheet",
            ],
            "deferred": [
                "connector temperature, contact-drop, simultaneous-load, skew/crosstalk and hot/unpowered boundary HIL",
                "received mating-height, coplanarity, cycle-life and separation-force proof in H5/H8",
                "PCB placement, paired-net fan-out, return geometry and DRC in H6",
            ],
        },
    }
    generated = {
        OUTPUT_SCH: schematic,
        SYMBOL_LIBRARY: build_symbol_library({OUTPUT_SCH: schematic}),
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    }
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary != {
        "ledger_instances": 1, "schematic_symbols": 1, "board_fitted_symbols": 1,
        "physical_contacts": 80, "unique_nets": 51, "hierarchical_interfaces": 51,
        "power_ground_contacts": 20, "main_3v3_contacts": 7,
        "reserved_contacts": 0, "cross_project_contact_mismatches": 0,
        "intentional_no_connect_pins": 0, "pcb_files_created": 0,
    }:
        raise ValueError(f"H2.3.11 accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 1:
        raise ValueError("RF40 must contain exactly one physical connector symbol")
    if schematic.count("\n\t(hierarchical_label \"") != 51:
        raise ValueError("RF40 hierarchy interface count drifted")
    contacts = manifest["contacts"]
    if [row["contact"] for row in contacts] != list(range(1, 81)):
        raise ValueError("RF40 physical contact ordering drifted")
    if len({row["symbol_pin"] for row in contacts}) != 80:
        raise ValueError("RF40 collapsed physical contacts")
    accounting = manifest["accounting_source"]
    for key, net in (
        ("power_ground_contacts", "POWER_GROUND"),
        ("audio_ground_contacts", "AUDIO_GROUND"),
        ("safety_ground_contacts", "SAFETY_GROUND"),
        ("main_3v3_contacts", "3V3_MAIN"),
        ("aon_contacts", "AON_SAFE_3V3"),
    ):
        if accounting[key] != sum(row["net"] == net for row in contacts):
            raise ValueError(f"M1 accounting differs for {key}")


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def kicad_check() -> None:
    find_kicad_cli()
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF40 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.11 RF-side M1 hierarchy")


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
            ["python3", str(ECAD / "h2_rf_root.py"), "--write"],
            cwd=REPO, text=True, capture_output=True,
        )
        if root.returncode:
            raise RuntimeError(f"failed to refresh RF hierarchy:\n{root.stdout}{root.stderr}")
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
        print("ok: H2.3.11 RF-side M1 sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
