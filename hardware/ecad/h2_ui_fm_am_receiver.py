#!/usr/bin/env python3
"""Generate and verify the exact H2.2.7 FM/AM/SW/LW receiver sheet."""

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
    FOOTPRINT_DIR, Pin, custom_footprint, effects, escaped, library_symbol,
    schematic_symbol, stable_uuid,
)


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_21_FM_AM_RECEIVER"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI21-fm-am-receiver.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI21"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "receiver_fmsw_external_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
        "receiver_amlw_external_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = overrides.get(instance, {}).get(contact) or passive.get(contact)
        if number is None:
            numeric = re.match(r"^(\d+)", physical)
            number = numeric.group(1) if numeric else contact
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pin numbers in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "receiver_fmsw_external_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "receiver_amlw_external_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "receiver": "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
        "receiver_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "receiver_supervisor": "Package_TO_SOT_SMD:SOT-23",
        "receiver_i2c_iso": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "receiver_irq_iso": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "receiver_clock": "Leshy2:FC-135-Q13FC13500005",
    }
    if instance in exact:
        return exact[instance]
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        if device_key == "tdk_c1608x7r1c105k080ac" or device_key == "murata_grm188r60j106me47d":
            return "Capacitor_SMD:C_0603_1608Metric"
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("yageo_rc"):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key == "murata_lqw15an56nj00d":
        return "Inductor_SMD:L_0402_1005Metric"
    if device_key == "littelfuse_sesd0402x1un_0020_090":
        return "Diode_SMD:D_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if "external_sma" in instance:
        return "J"
    if device_key == "littelfuse_sesd0402x1un_0020_090":
        return "D"
    if device_key == "murata_lqw15an56nj00d":
        return "L"
    if device_key == "epson_q13fc13500005":
        return "Y"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        return "C"
    if device_key.startswith("yageo_rc"):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    sma = custom_footprint(
        "RFPC-SMA31-FN-175-A",
        [("1", 0.0, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("2", -1.75, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("3", 1.75, -1.65, 1.60, 3.30, ("F.Cu", "F.Paste", "F.Mask")),
         ("4", -1.75, -1.65, 1.60, 3.30, ("B.Cu", "B.Paste", "B.Mask")),
         ("5", 1.75, -1.65, 1.60, 3.30, ("B.Cu", "B.Paste", "B.Mask"))],
        10.20, 6.60, 10.40, 6.80,
        "GCT RFPC-SMA31-FN drawing Rev.1.5: option 175 for 1.60-mm PCB; exact standard-polarity SMA body with three top and two bottom 1.60x3.30-mm lands",
    )
    crystal = custom_footprint(
        "FC-135-Q13FC13500005",
        [("1", -1.25, 0.0, 1.00, 1.80, copper),
         ("2", 1.25, 0.0, 1.00, 1.80, copper)],
        3.20, 1.50, 3.50, 2.10,
        "Seiko Epson FC-135 Q13FC13500005 official specification page 1: exact two 1.0x1.8-mm recommended lands with 2.5-mm centre spacing and no-copper centre region",
    )
    return {
        FOOTPRINT_DIR / "RFPC-SMA31-FN-175-A.kicad_mod": sma,
        FOOTPRINT_DIR / "FC-135-Q13FC13500005.kicad_mod": crystal,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 32:
        raise ValueError(f"{SHEET_ID} must own exactly 32 rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interface_order = list(interface_row["interfaces"])
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
            "instance": row["instance"], "device_key": row["device_key"],
            "mpn": row["mpn"], "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"]),
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789") or "X"
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            True, True, True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        column = min(range(len(cursor_y)), key=lambda col: cursor_y[col])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        pin_remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - pin_remainder) / 2.54) * 2.54 + pin_remainder
        cursor_y[column] = y + height / 2 + 15.24
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — exact FM/AM/SW/LW receive-only frontend")',
        '\t\t(rev "H2.2.7")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords, True, True,
            SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
        ))
        for pin in spec["pins"]:
            net = pin_net(spec["instance"], pin, endpoints, no_connect_nets)
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used: set[str] = set()
    no_connect_endpoints: list[str] = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")', "\t)",
                ]
                no_connect_endpoints.append(f"{instance}.{pin.contact}")
                continue
            is_hierarchical = net in interfaces and net not in hierarchy_used
            if is_hierarchical:
                hierarchy_used.add(net)
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            token = "hierarchical_label" if is_hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if is_hierarchical else ""
            lines += [
                f'\t({token} "{escaped(net)}"{shape}', f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")', "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(f"UI21 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
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
        "stage": "H2.2.7",
        "status": "reviewed_exact_fm_am_receiver_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows), "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs), "hierarchical_interfaces": len(interfaces),
            "receiver_contacts": len(devices["skyworks_si4732_a10_gsr"]["contacts"]),
            "external_receive_ports": 2, "custom_footprints": len(footprint_outputs()),
            "intentional_no_connect_pins": len(no_connect_endpoints), "pcb_files_created": 0,
        },
        "instances": [
            {"instance": spec["instance"], "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
             "reference": spec["reference"], "mpn": spec["mpn"],
             "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
             "board_fitted": True}
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {"mpn": devices[key]["mpn"], "footprint": footprint, "source": devices[key]["source"]}
            for key, footprint in (
                ("skyworks_si4732_a10_gsr", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"),
                ("epson_q13fc13500005", "Leshy2:FC-135-Q13FC13500005"),
                ("gct_rfpc_sma31_fn_175_a", "Leshy2:RFPC-SMA31-FN-175-A"),
            )
        ],
        "corrections_closed": [
            "all SMA shell lands and both RF-ESD shunts collapse to the physical POWER_GROUND plane",
            "Si4732 manufacturer NC is physical SOIC pin 5 and remains explicitly open",
            "FM/SW 50-ohm boundary and non-50-ohm AM/LW loop/pod boundary are separate labelled ports",
            "power-off isolates I2C and IRQ while the receiver rail is actively discharged",
            "stereo outputs are AC-coupled and passively summed around AUDIO_VMID_MAIN without consuming a new GPIO",
        ],
        "review_boundary": {
            "complete": [
                "all 32 UI21 ledger instances have exact MPN, contacts, footprint and circuit nets",
                "all eight hierarchy interfaces terminate on real pins",
                "receive-only RF, power/reset, I2C/IRQ, clock and mono-audio paths are explicit",
                "native KiCad parses the live hierarchy and the controlled SMA footprint library",
            ],
            "deferred": [
                "received Si4732 identity, I2C address/boot-state and radio-firmware command HIL",
                "FM/SW match sweep and qualified AM/LW ferrite-loop or transformer-pod HIL",
                "clock load/frequency, sensitivity, selectivity, audio level/noise and EMI HIL",
                "PCB placement, RF return/impedance geometry and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary != {
        "ledger_instances": 32, "schematic_symbols": 32,
        "board_fitted_symbols": 32, "hierarchical_interfaces": 8,
        "receiver_contacts": 16, "external_receive_ports": 2,
        "custom_footprints": 2, "intentional_no_connect_pins": 4,
        "pcb_files_created": 0,
    }:
        raise ValueError(f"H2.2.7 accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 32 or schematic.count("\n\t(hierarchical_label \"") != 8:
        raise ValueError("UI21 symbol/interface accounting mismatch")
    required_nc = {"receiver.GPO1", "receiver.NC", "receiver_irq_iso.NC", "receiver_power_switch.NC"}
    if set(manifest["intentional_no_connect_endpoints"]) != required_nc:
        raise ValueError("UI21 no-connect accounting drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted UI21 component lacks footprint: {row['instance']}")
    sma = generated[FOOTPRINT_DIR / "RFPC-SMA31-FN-175-A.kicad_mod"]
    if sma.count('(layers "F.Cu" "F.Paste" "F.Mask")') != 3 or sma.count('(layers "B.Cu" "B.Paste" "B.Mask")') != 2:
        raise ValueError("RFPC-SMA31 five-land footprint drifted")
    crystal = generated[FOOTPRINT_DIR / "FC-135-Q13FC13500005.kicad_mod"]
    if '(pad "1" smd roundrect (at -1.250 0.000) (size 1.000 1.800)' not in crystal or '(pad "2" smd roundrect (at 1.250 0.000) (size 1.000 1.800)' not in crystal:
        raise ValueError("FC-135 exact two-land footprint drifted")
    aliases = manifest["physical_net_aliases_collapsed"]
    for net in ("RX_FMSW_SMA_RF_GROUND", "RX_AMLW_SMA_RF_GROUND", "RX_FMSW_ESD_GROUND", "RX_AMLW_ESD_GROUND"):
        if aliases.get(net) != "POWER_GROUND":
            raise ValueError(f"RF ground did not collapse to POWER_GROUND: {net}")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-ui21-") as temp:
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(Path(temp) / "Leshy2.pretty"), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected controlled footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected UI21 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.7 and all custom footprints")


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
            ["python3", str(ECAD / "h2_ui_root.py"), "--write"],
            cwd=REPO, text=True, capture_output=True,
        )
        if root.returncode:
            raise RuntimeError(f"failed to refresh UI hierarchy:\n{root.stdout}{root.stderr}")
        print(root.stdout, end="")
    else:
        stale = [path for path, content in generated.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print("ok: H2.2.7 FM/AM/SW/LW receiver sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
