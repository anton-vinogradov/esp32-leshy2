#!/usr/bin/env python3
"""Generate and verify the exact H2.3.10 acoustic I/O and speaker-amplifier sheet.

The internal electret crosses M1 as MIC_RAW.  The selected differential audio
pair is AC-coupled into a reset-disabled PAM8302AAYCR and remains a floating BTL
path through the EMI network and the wired internal speaker assembly.
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
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
    FOOTPRINT_DIR,
    Pin,
    custom_footprint,
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
SHEET_ID = "RF_36_AUDIO_IO_AMP"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF36-audio-io-amp.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF36"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "speaker": {"PLUS": "+", "MINUS": "-"},
        "microphone": {"OUT_PLUS": "1", "GND_MINUS": "2"},
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        number = overrides.get(instance, {}).get(contact, passive.get(contact))
        if number is None:
            match = re.match(r"^(\d+)", str(row.get("physical", "")))
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
        "speaker_amp": "Leshy2:PAM8302AAYCR-UDFN3030-8E",
        "microphone": "Leshy2:CMEJ-0413-42-SMT-TR",
        "speaker": "Leshy2:Speaker-Wire-Termination-2P",
    }
    if instance in exact:
        return exact[instance]
    if device_key in {"tdk_c1608x7r1c105k080ac", "murata_grm188r60j106me47d"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key == "murata_grm1555c1h221ja01d":
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("yageo_rc0402"):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key == "murata_blm18pg181sn1d":
        return "Inductor_SMD:L_0603_1608Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "speaker":
        return "LS"
    if instance == "microphone":
        return "MIC"
    if instance == "speaker_amp":
        return "U"
    if device_key.startswith(("tdk_c", "murata_grm")):
        return "C"
    if device_key.startswith("yageo_rc"):
        return "R"
    if device_key.startswith("murata_blm"):
        return "FB"
    return "U"


def microphone_footprint() -> str:
    """Transcribe the manufacturer's single-sided concentric land geometry."""
    return "\n".join([
        '(footprint "CMEJ-0413-42-SMT-TR"',
        '\t(version 20260206)',
        '\t(generator "leshy2-h2-rf36")',
        '\t(generator_version "1.0")',
        '\t(layer "F.Cu")',
        '\t(descr "Same Sky Rev.1.04 single-sided recommended PCB layout: 4.0-mm top-port body, 0.86-mm positive centre land and 1.9/2.7-mm negative annulus with 0.6-mm access gap")',
        '\t(property "Reference" "REF**" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        '\t(property "Value" "CMEJ-0413-42-SMT-TR" (at 0 3 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
        '\t(attr smd)',
        '\t(fp_circle (center 0 0) (end 2 0) (stroke (width 0.10) (type default)) (fill none) (layer "F.Fab"))',
        '\t(fp_circle (center 0 0) (end 2.25 0) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
        '\t(pad "1" smd circle (at 0 0) (size 0.86 0.86) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "1" smd rect (at 0 0.89) (size 0.20 1.35) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "2" smd custom',
        '\t\t(at 0 0)',
        '\t\t(size 0.40 0.40)',
        '\t\t(layers "F.Cu" "F.Paste" "F.Mask")',
        '\t\t(options (clearance outline) (anchor circle))',
        '\t\t(primitives',
        '\t\t\t(gr_arc (start -0.35 1.095) (mid 0 -1.15) (end 0.35 1.095) (width 0.40))',
        '\t\t)',
        '\t)',
        ')',
        '',
    ])


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    amplifier_pads = []
    for index in range(4):
        y = -0.975 + index * 0.65
        amplifier_pads.append((str(index + 1), -1.325, y, 0.65, 0.35, copper))
        amplifier_pads.append((str(8 - index), 1.325, y, 0.65, 0.35, copper))
    amplifier_pads.append(("", 0.0, 0.0, 1.60, 2.35, copper, "rect"))
    amplifier = custom_footprint(
        "PAM8302AAYCR-UDFN3030-8E", amplifier_pads,
        3.00, 3.00, 3.70, 3.70,
        "Diodes PAM8302A DS41333 Rev.6-2 U-DFN3030-8 Type E suggested pad layout rotated to the datasheet top-view pin assignment: 0.65x0.35-mm lands, 0.65-mm pitch, 3.30-mm column extent and unnumbered 1.60x2.35-mm central pad",
    )
    amplifier = amplifier.replace(
        "\t(attr smd)",
        "\t(fp_circle (center -1.10 -1.10) (end -0.95 -1.10) "
        "(stroke (width 0.10) (type default)) (fill none) (layer \"F.SilkS\"))\n"
        "\t(attr smd)",
    )
    speaker = custom_footprint(
        "Speaker-Wire-Termination-2P",
        [("+", -1.75, 0.0, 2.50, 1.50, copper),
         ("-", 1.75, 0.0, 2.50, 1.50, copper)],
        6.00, 3.00, 6.50, 3.50,
        "Leshy2 fabricated two-pad solder termination for the AS02404PO wired assembly; polarity is explicit and the 24x12x4.5-mm speaker body remains mechanically registered outside this PCB termination",
    )
    return {
        FOOTPRINT_DIR / "PAM8302AAYCR-UDFN3030-8E.kicad_mod": amplifier,
        FOOTPRINT_DIR / "CMEJ-0413-42-SMT-TR.kicad_mod": microphone_footprint(),
        FOOTPRINT_DIR / "Speaker-Wire-Termination-2P.kicad_mod": speaker,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 14:
        raise ValueError(f"{SHEET_ID} must own exactly 14 ledger rows, got {len(rows)}")
    assembly_rows = [
        row for row in rows
        if row["electrical_disposition"] == "fitted_interconnect_assembly"
    ]
    if [row["instance"] for row in assembly_rows] != ["speaker"]:
        raise ValueError("RF36 must contain exactly the wired speaker assembly")

    interface_order = list(next(
        row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID
    ))
    interfaces = set(interface_order)
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(
        candidate, local_instances, interface_order
    )

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
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
            "disposition": row["electrical_disposition"],
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 121.92, 193.04, 264.16, 335.28]
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
        '\t\t(title "Leshy2 — microphone, reset-safe differential amplifier and wired speaker")',
        '\t\t(rev "H2.3.10")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF36 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    schematic = "\n".join(lines)
    generated = {
        OUTPUT_SCH: schematic,
        SYMBOL_LIBRARY: build_symbol_library({OUTPUT_SCH: schematic}),
        **footprint_outputs(),
    }
    manifest = {
        "schema_version": 1,
        "stage": "H2.3.10",
        "status": "reviewed_exact_audio_io_amplifier_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": len(rows) - len(assembly_rows),
            "fitted_interconnect_assemblies": len(assembly_rows),
            "hierarchical_interfaces": len(interfaces),
            "physical_package_or_interface_contacts": sum(len(spec["pins"]) for spec in specs),
            "board_component_contacts": sum(
                len(spec["pins"]) for spec in specs if spec["instance"] != "speaker"
            ),
            "floating_btl_output_branches": 2,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints": 3,
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
                "electrical_disposition": spec["disposition"],
            }
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "known_deferred_fixture_labels": [],
        "footprint_evidence": [
            {
                "mpn": "Diodes Incorporated PAM8302AAYCR",
                "footprint": "Leshy2:PAM8302AAYCR-UDFN3030-8E",
                "status": "official U-DFN3030-8 Type E suggested land pattern; central pad remains unnumbered and electrically unassigned",
            },
            {
                "mpn": "Same Sky CMEJ-0413-42-SMT-TR",
                "footprint": "Leshy2:CMEJ-0413-42-SMT-TR",
                "status": "official Rev.1.04 single-sided concentric recommended copper geometry",
            },
            {
                "mpn": "PUI Audio AS02404PO",
                "footprint": "Leshy2:Speaker-Wire-Termination-2P",
                "status": "fabricated polarity-keyed PCB wire termination only; speaker body remains the exact registered 24x12x4.5-mm assembly",
            },
        ],
        "corrections_closed": [
            "PAM8302AASCR was rejected because ASCR is MSOP-8; the accepted AYCR order code is the intended compact U-DFN3030-8 Type E and costs slightly less at the recorded quantity tier",
            "the amplifier central package pad is physically present but remains unnumbered instead of being assigned to ground without manufacturer authorization",
            "the speaker is a wired fitted assembly with an explicit two-pad PCB termination instead of a fictitious direct-body land pattern",
            "microphone orientation remains a placement constraint: the exact top-port serial capsule is fitted on the RF-board face that points toward the bottom enclosure exit",
            "both class-D outputs remain floating BTL conductors through independent beads and shunt capacitors; neither speaker terminal is grounded",
        ],
        "review_boundary": {
            "complete": [
                "all fourteen ledger instances, 34 electrical contacts, seven hierarchy interfaces and one intentional NC pin are explicit",
                "the differential selected-audio input, reset-low shutdown, local bypass and both independent BTL output branches are complete",
                "exact serial microphone, amplifier and speaker MPNs are tied to manufacturer drawings without inventing unavailable component contacts",
                "native KiCad parses RF36 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received microphone acoustic orientation, speaker carrier/wire strain relief, excursion clearance and enclosure response close in H5/H8",
                "audio gain, clipping, noise, class-D EMI and thermal behavior close by H3 calculation and H8 HIL",
                "pad-mask tuning, return geometry, placement and complete DRC close in H6",
                "codec/source selection, quiet-state sequencing and UI policy close in firmware F3/F4 and H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 14,
        "schematic_symbols": 14,
        "board_fitted_symbols": 13,
        "fitted_interconnect_assemblies": 1,
        "hierarchical_interfaces": 7,
        "physical_package_or_interface_contacts": 34,
        "board_component_contacts": 32,
        "floating_btl_output_branches": 2,
        "intentional_no_connect_pins": 1,
        "custom_footprints": 3,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.10 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 14:
        raise ValueError("RF36 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 7:
        raise ValueError("RF36 hierarchy accounting mismatch")
    if manifest["intentional_no_connect_endpoints"] != ["speaker_amp.NC"]:
        raise ValueError("RF36 no-connect set drifted")
    amplifier = generated[FOOTPRINT_DIR / "PAM8302AAYCR-UDFN3030-8E.kicad_mod"]
    required_pad_axes = {
        '(pad "1" smd roundrect (at -1.325 -0.975) (size 0.650 0.350)',
        '(pad "4" smd roundrect (at -1.325 0.975) (size 0.650 0.350)',
        '(pad "5" smd roundrect (at 1.325 0.975) (size 0.650 0.350)',
        '(pad "8" smd roundrect (at 1.325 -0.975) (size 0.650 0.350)',
        '(pad "" smd rect (at 0.000 0.000) (size 1.600 2.350)',
    }
    if any(token not in amplifier for token in required_pad_axes):
        raise ValueError("PAM8302AAYCR pin axes no longer match the datasheet top view")
    speaker = next(row for row in manifest["instances"] if row["instance"] == "speaker")
    if speaker["electrical_disposition"] != "fitted_interconnect_assembly":
        raise ValueError("speaker must remain a fitted wired assembly")
    if not all(generated[path].startswith("(footprint") for path in footprint_outputs()):
        raise ValueError("RF36 custom footprint output is malformed")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf36-") as temp:
        staged = Path(temp) / "RF_36_AUDIO_IO_AMP.kicad_sch"
        shutil.copy2(OUTPUT_SCH, staged)
        result = subprocess.run(
            [cli, "sch", "export", "python-bom", "-o", str(Path(temp) / "bom.xml"), str(staged)],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected RF36:\n{result.stdout}{result.stderr}")
        for footprint in footprint_outputs():
            result = subprocess.run(
                [
                    cli, "fp", "export", "svg", "-o", temp,
                    "--fp", footprint.stem, str(FOOTPRINT_DIR),
                ],
                text=True,
                capture_output=True,
            )
            if result.returncode:
                raise RuntimeError(
                    f"KiCad rejected {footprint.name}:\n{result.stdout}{result.stderr}"
                )
    print("ok: KiCad parsed the exact H2.3.10 acoustic sheet and all custom footprints")


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
        print("ok: H2.3.10 audio I/O and amplifier sheet is current")
        if args.kicad_check:
            kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
