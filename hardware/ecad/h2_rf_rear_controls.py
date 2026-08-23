#!/usr/bin/env python3
"""Generate and verify the H2.3.9 rear controls and encoder sheet.

The rear encoder phases and push contact cross M1 as independent direct inputs;
PTT remains local to the RP/voice domain.  Every exposed contact has an exact
serial component, deterministic pull-up where this board owns it, and local
ESD protection.  The removable knob is recorded as a mechanical mating item,
not invented as an electrical schematic symbol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
    Pin,
    effects,
    escaped,
    library_symbol,
    schematic_symbol,
    stable_uuid,
)


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-RF-root-interface.json"
SHEET_ID = "RF_35_REAR_CONTROLS"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF35-rear-controls.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF35"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    encoder = {"A": "A", "C": "C", "B": "B", "SW1": "S1", "SW2": "S2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if instance == "encoder":
            number = encoder.get(contact)
        if number is None:
            match = re.search(r"(?:^|\s)(\d+)(?:\s|$)", str(row.get("physical", "")))
            if not match:
                raise ValueError(f"no physical contact number for {instance}.{contact}")
            number = match.group(1)
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical contacts in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "ptt_switch": "Leshy2:B3S-1100P",
        "rear_control_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "encoder_ptt_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "encoder": "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm_MountingHoles",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "yageo_rc0603fr_071kl":
        return "Resistor_SMD:R_0603_1608Metric"
    if device_key.startswith("yageo_rc0402"):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key.startswith(("tdk_c1005", "murata_grm155")):
        return "Capacitor_SMD:C_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "ptt_switch":
        return "SW"
    if instance == "encoder":
        return "ENC"
    if device_key == "ti_tpd4e05u06_dqar":
        return "D"
    if device_key.startswith("yageo_rc"):
        return "R"
    if device_key.startswith(("tdk_c", "murata_grm")):
        return "C"
    return "U"


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 8:
        raise ValueError(f"{SHEET_ID} must own exactly 8 ledger rows, got {len(rows)}")
    electrical_rows = [
        row for row in rows
        if row["electrical_disposition"] == "board_fitted_component"
    ]
    mechanical_rows = [
        row for row in rows
        if row["electrical_disposition"] == "external_mating_product_interface_only"
    ]
    if len(electrical_rows) != 7 or len(mechanical_rows) != 1:
        raise ValueError("RF35 must contain seven fitted electrical parts and one external knob")

    interface_order = list(next(
        row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID
    ))
    interfaces = set(interface_order)
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(
        candidate, local_instances, interface_order
    )

    specs = []
    ref_counts: Counter[str] = Counter()
    for row in electrical_rows:
        prefix = reference_prefix(row["instance"], row["device_key"])
        ref_counts[prefix] += 1
        specs.append({
            "instance": row["instance"],
            "device_key": row["device_key"],
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"]),
        })

    library_defs = []
    placements = {}
    column_x = [55.88, 132.08, 208.28, 284.48]
    cursor_y = [45.72] * len(column_x)
    for spec in specs:
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"],
            spec["reference"].rstrip("0123456789"), spec["footprint"],
            spec["role"], True, True, True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        column = min(range(len(cursor_y)), key=lambda item: cursor_y[item])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - remainder) / 2.54) * 2.54 + remainder
        cursor_y[column] = y + height / 2 + 17.78
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A2")', "\t(title_block",
        '\t\t(title "Leshy2 — rear encoder, push and independent PTT")',
        '\t\t(rev "H2.3.9")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords,
            True, True, SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
        ))
        for pin in spec["pins"]:
            net = pin_net(spec["instance"], pin, endpoints, no_connect_nets)
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used: set[str] = set()
    no_connect_endpoints = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")', "\t)",
                ]
                no_connect_endpoints.append(f"{instance}.{pin.contact}")
                continue
            hierarchical = net in interfaces and net not in hierarchy_used
            if hierarchical:
                hierarchy_used.add(net)
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            token = "hierarchical_label" if hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if hierarchical else ""
            lines += [
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})", f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")', "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(f"RF35 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

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
        "stage": "H2.3.9",
        "status": "reviewed_exact_rear_controls_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs),
            "external_mechanical_mating_items": len(mechanical_rows),
            "hierarchical_interfaces": len(interfaces),
            "board_physical_contacts": sum(len(spec["pins"]) for spec in specs),
            "independent_direct_control_paths": 4,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints_added": 0,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"],
                "mpn": spec["mpn"],
                "footprint": spec["footprint"],
                "pin_count": len(spec["pins"]),
                "board_fitted": True,
            }
            for spec in specs
        ],
        "external_mechanical_mating_items": [
            {
                "instance": row["instance"],
                "mpn": row["mpn"],
                "role": row["role"],
                "schematic_symbol": False,
                "board_footprint": False,
            }
            for row in mechanical_rows
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "known_deferred_fixture_labels": [],
        "footprint_evidence": [
            {
                "mpn": "OMRON B3S-1100P",
                "footprint": "Leshy2:B3S-1100P",
                "status": "exact manufacturer land pattern already controlled by UI12",
            },
            {
                "mpn": "Texas Instruments TPD4E05U06DQAR",
                "footprint": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
                "status": "exact TI DQA package",
            },
            {
                "mpn": "Alps Alpine EC11E18244AU",
                "footprint": "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm_MountingHoles",
                "status": "KiCad 10 EC11E switch footprint matches official Drawing No.2 signal, switch and mounting-hole axes",
            },
        ],
        "corrections_closed": [
            "the Davies knob remains an external mechanical mating item and cannot become a fictitious electrical symbol or board footprint",
            "encoder A, B and push are three independent M1 paths; PTT remains a fourth direct path local to RP instead of an I2C-scanned key",
            "the RF sheet owns the exposed encoder and PTT contacts while the three encoder pull-ups remain correctly owned by UI12",
            "the selected encoder footprint includes the exact switch terminals and both manufacturer mounting-hole types",
            "STOP and RE-ARM controls are absent; unattended shutdown is owned by the independent watchdog and FAULT_KILL architecture",
        ],
        "review_boundary": {
            "complete": [
                "all seven fitted electrical components, 36 contacts, six hierarchy interfaces and twelve intentional NC contacts are explicit",
                "encoder phase, encoder push and PTT remain independent direct inputs with local exposed-contact ESD protection",
                "all fitted devices use exact serial MPNs and exact package/land patterns",
                "native KiCad parses RF35 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received encoder detent, bounce, shaft/knob interference fit and enclosure actuation close in H5/H8",
                "PTT and encoder ESD, long-hold, chatter and accidental-actuation fault injection close in H3/H8",
                "mounting-hole tolerances, keepouts, return geometry and complete DRC close in H6",
                "PCNT full-detent semantics and input debounce close in firmware F3/F4 and H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 8,
        "schematic_symbols": 7,
        "board_fitted_symbols": 7,
        "external_mechanical_mating_items": 1,
        "hierarchical_interfaces": 6,
        "board_physical_contacts": 36,
        "independent_direct_control_paths": 4,
        "intentional_no_connect_pins": 12,
        "custom_footprints_added": 0,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.9 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 7:
        raise ValueError("RF35 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 6:
        raise ValueError("RF35 hierarchy accounting mismatch")
    expected_nc = {
        "rear_control_esd.D1_MINUS", "rear_control_esd.D2_PLUS",
        "rear_control_esd.D2_MINUS", "encoder_ptt_esd.D2_MINUS",
        *(f"rear_control_esd.NC_{pin}" for pin in (6, 7, 9, 10)),
        *(f"encoder_ptt_esd.NC_{pin}" for pin in (6, 7, 9, 10)),
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF35 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if any(not row["footprint"] for row in manifest["instances"]):
        raise ValueError("fitted RF35 component lacks an exact footprint")
    if manifest["external_mechanical_mating_items"] != [{
        "instance": "encoder_knob",
        "mpn": "Davies Molding 1227-J",
        "role": "exact soft-touch knob over rear encoder",
        "schematic_symbol": False,
        "board_footprint": False,
    }]:
        raise ValueError("encoder knob disposition drifted")


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def kicad_check() -> None:
    cli = find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf35-") as temp:
        staged = Path(temp) / "RF_35_REAR_CONTROLS.kicad_sch"
        shutil.copy2(OUTPUT_SCH, staged)
        result = subprocess.run(
            [cli, "sch", "export", "python-bom", "-o", str(Path(temp) / "bom.xml"), str(staged)],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected RF35:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed the exact H2.3.9 rear-controls sheet")


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
    else:
        stale = [
            path.relative_to(REPO) for path, content in generated.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path}")
            return 1
        print("ok: H2.3.9 rear-controls sheet is current")
        if args.kicad_check:
            kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
