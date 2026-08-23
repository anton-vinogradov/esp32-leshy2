#!/usr/bin/env python3
"""Generate and verify the exact H2.2.4 controls and indicators sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_display_touch_storage import endpoint_nets, pin_net
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
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_12_CONTROLS_INDICATORS"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI12-controls-indicators.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI12"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "slow_io": {"EPAD": "33"},
        "ui_matrix_esd": {"GND": "9"},
        "front_function_esd": {"GND": "9"},
    }
    passive = {"END_1": "1", "END_2": "2"}
    led = {"K": "1", "A": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = overrides.get(instance, {}).get(contact)
        if number is None:
            number = passive.get(contact) or led.get(contact)
        if number is None:
            numeric = re.match(r"^(\d+)", physical)
            number = numeric.group(1) if numeric else contact
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pin number in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    if instance == "slow_io":
        return "Leshy2:TCA6424ARGJR"
    if device_key == "ti_tca9539_pwr":
        return "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm"
    if device_key == "omron_b3s_1100p":
        return "Leshy2:B3S-1100P"
    if device_key == "ti_tpd8e003_dqdr":
        return "Leshy2:TPD8E003DQDR"
    if device_key == "ti_sn74lvc1g07_dckr":
        return "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5"
    if device_key in {"tdk_c1608x7r1c105k080ac", "tdk_b57332v5103f360"}:
        return (
            "Capacitor_SMD:C_0603_1608Metric"
            if device_key.startswith("tdk_c")
            else "Resistor_SMD:R_0603_1608Metric"
        )
    if device_key.startswith("tdk_c"):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("yageo_rc"):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key.startswith("liteon_ltst_c190"):
        return "LED_SMD:LED_0603_1608Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if device_key == "omron_b3s_1100p":
        return "SW"
    if device_key == "tdk_b57332v5103f360":
        return "RT"
    if device_key.startswith("liteon_") or device_key == "ti_tpd8e003_dqdr":
        return "D"
    if device_key.startswith("tdk_c"):
        return "C"
    if device_key.startswith("yageo_rc"):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    copper_no_paste = ("F.Cu", "F.Mask")
    paste = ("F.Paste",)

    rgj_pads: list[tuple] = []
    for index in range(8):
        position = -1.75 + index * 0.50
        rgj_pads.append((str(1 + index), -2.40, position, 0.60, 0.25, copper))
        rgj_pads.append((str(9 + index), position, 2.40, 0.25, 0.60, copper))
        rgj_pads.append((str(17 + index), 2.40, -position, 0.60, 0.25, copper))
        rgj_pads.append((str(25 + index), -position, -2.40, 0.25, 0.60, copper))
    rgj_pads.append(("33", 0.0, 0.0, 3.15, 3.15, copper_no_paste, "rect"))
    for x in (-0.785, 0.785):
        for y in (-0.785, 0.785):
            rgj_pads.append(("33", x, y, 1.37, 1.37, paste, "circle"))
    rgj = custom_footprint(
        "TCA6424ARGJR", rgj_pads, 5.0, 5.0, 5.4, 5.4,
        "TI RGJ0032A 4222103 Rev.D: 32x 0.25x0.60-mm lands on 0.50-mm pitch, 4.80-mm outer span, 3.15-mm exposed pad and four 1.37-mm stencil apertures",
    )

    dqd_pads: list[tuple] = []
    for index in range(4):
        x = -0.60 + index * 0.40
        dqd_pads.append((str(1 + index), x, -0.875, 0.20, 0.50, copper, "rect"))
        dqd_pads.append((str(8 - index), x, 0.875, 0.20, 0.50, copper, "rect"))
    dqd_pads += [
        ("9", 0.0, 0.0, 1.20, 0.40, copper_no_paste, "rect"),
        ("9", -0.30, 0.0, 0.50, 0.30, paste, "rect"),
        ("9", 0.30, 0.0, 0.50, 0.30, paste, "rect"),
    ]
    dqd = custom_footprint(
        "TPD8E003DQDR", dqd_pads, 1.70, 1.35, 2.00, 2.05,
        "TI DQD R-PWSON-N8 4209732/4211174: 8x 0.20x0.50-mm lands, 0.40-mm pitch, 1.75-mm row span, 1.20x0.40-mm exposed pad and split stencil",
    )

    b3s = custom_footprint(
        "B3S-1100P",
        [
            ("1", -3.98, -3.17, 1.55, 1.30, copper, "rect"),
            ("3", 3.98, -3.17, 1.55, 1.30, copper, "rect"),
            ("2", -3.98, 1.33, 1.55, 1.30, copper, "rect"),
            ("4", 3.98, 1.33, 1.55, 1.30, copper, "rect"),
            ("5", 0.00, 3.17, 1.30, 1.70, copper, "rect"),
        ],
        6.60, 6.90, 10.00, 8.90,
        "OMRON A204-E1 B3S-1100P: exact five-terminal 9.0x4.5-mm top-view land pattern; terminals 1/3 and 2/4 remain separately numbered and ground terminal is pad 5",
        body_y=-0.925, courtyard_y=-0.170,
    )
    return {
        FOOTPRINT_DIR / "TCA6424ARGJR.kicad_mod": rgj,
        FOOTPRINT_DIR / "TPD8E003DQDR.kicad_mod": dqd,
        FOOTPRINT_DIR / "B3S-1100P.kicad_mod": b3s,
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
    if len(rows) != 71:
        raise ValueError(f"{SHEET_ID} must own exactly 71 ledger rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interfaces = set(interface_row["interfaces"])
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(candidate, local_instances)

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
        instance = row["instance"]
        device = devices[row["device_key"]]
        prefix = reference_prefix(instance, row["device_key"])
        ref_counts[prefix] += 1
        specs.append({
            "instance": instance,
            "device_key": row["device_key"],
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins_for(instance, device),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(instance, row["device_key"]),
            "on_board": True,
            "in_bom": True,
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
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")',
        "\t(title_block",
        '\t\t(title "Leshy2 — exact controls, safety sensing and front indicators")',
        '\t\t(rev "H2.2.4")',
        "\t)",
        "\t(lib_symbols",
        *library_defs,
        "\t)",
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
    no_connect_count = 0
    no_connect_endpoints: list[str] = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")',
                    "\t)",
                ]
                no_connect_count += 1
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
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")',
                "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(
            f"UI12 circuit does not terminate every hierarchy interface: "
            f"missing {sorted(interfaces - hierarchy_used)}; "
            f"unexpected {sorted(hierarchy_used - interfaces)}"
        )
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
        "stage": "H2.2.4",
        "status": "reviewed_exact_controls_indicators_sheet",
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
            "hierarchical_interfaces": len(interfaces),
            "slow_io_contacts": len(devices["tca6424argjr"]["contacts"]),
            "matrix_io_contacts": len(devices["ti_tca9539_pwr"]["contacts"]),
            "serial_tactile_switches": sum(s["device_key"] == "omron_b3s_1100p" for s in specs),
            "actual_tx_indicators": sum(s["device_key"] == "liteon_ltst_c190krkt" for s in specs),
            "fault_indicators": sum(s["device_key"] == "liteon_ltst_c190kfkt" for s in specs),
            "custom_footprints": len(footprint_outputs()),
            "intentional_no_connect_pins": no_connect_count,
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
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {
                "mpn": devices[key]["mpn"],
                "footprint": footprint,
                "source": devices[key]["source"],
            }
            for key, footprint in (
                ("tca6424argjr", "Leshy2:TCA6424ARGJR"),
                ("ti_tpd8e003_dqdr", "Leshy2:TPD8E003DQDR"),
                ("omron_b3s_1100p", "Leshy2:B3S-1100P"),
            )
        ],
        "corrections_closed": [
            "all ten front indicators are exact circuit bodies: nine red physical-TX paths and one amber hardware FAULT latch",
            "the redundant front-only ANY_TX diode aggregate and TX ACTIVE LED are absent while the RF/power ANY_TX_AON_N safety aggregate remains",
            "encoder phase pull-ups terminate on END_2; END_1 remains exclusively 3V3_MAIN",
            "all fifteen direct-press controls use one serial OMRON B3S-1100P footprint with five separately mapped lands",
            "TCA6424 RGJ and TPD8E003 DQD exposed pads are explicit physical contacts tied to their reviewed ground domains",
        ],
        "review_boundary": {
            "complete": [
                "every UI12 ledger instance is placed once with exact MPN, contact map and footprint",
                "every hierarchy interface terminates on a real circuit pin",
                "all user switches, encoder phases, temperature sensing, slow controls, ESD and indicator paths are explicit",
                "native KiCad parses the populated UI hierarchy with only exact machine-accounted findings",
            ],
            "deferred": [
                "switch/encoder debounce and human-interface HIL",
                "LED current/brightness and FAULT visibility HIL",
                "thermal trip calibration and fault-injection HIL",
                "PCB placement, return geometry and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 71,
        "schematic_symbols": 71,
        "board_fitted_symbols": 71,
        "hierarchical_interfaces": 45,
        "slow_io_contacts": 33,
        "matrix_io_contacts": 24,
        "serial_tactile_switches": 15,
        "actual_tx_indicators": 9,
        "fault_indicators": 1,
        "custom_footprints": 3,
        "intentional_no_connect_pins": 3,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"reviewed H2.2.4 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 71:
        raise ValueError("UI12 schematic symbol instance count mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 45:
        raise ValueError("UI12 hierarchy-interface count mismatch")
    if manifest["intentional_no_connect_endpoints"] != [
        "front_function_esd.IO8", "slow_io_fault_sense_iso.NC", "slow_io_s3_evidence_iso.NC"
    ]:
        raise ValueError("UI12 intentional no-connect set drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted UI12 component lacks footprint: {row['instance']}")
    footprints = footprint_outputs()
    rgj = footprints[FOOTPRINT_DIR / "TCA6424ARGJR.kicad_mod"]
    if rgj.count('\n\t(pad "') != 37 or rgj.count('(pad "33"') != 5:
        raise ValueError("TCA6424 RGJ 32+EP/stencil footprint drifted")
    dqd = footprints[FOOTPRINT_DIR / "TPD8E003DQDR.kicad_mod"]
    if dqd.count('\n\t(pad "') != 11 or dqd.count('(pad "9"') != 3:
        raise ValueError("TPD8E003 DQD 8+EP/stencil footprint drifted")
    b3s = footprints[FOOTPRINT_DIR / "B3S-1100P.kicad_mod"]
    if any(f'(pad "{number}"' not in b3s for number in range(1, 6)):
        raise ValueError("B3S-1100P five-land mapping drifted")


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
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected populated UI hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.4 inside the live hierarchy")


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
            cwd=REPO, text=True, capture_output=True,
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
        print("ok: H2.2.4 controls/indicators sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
