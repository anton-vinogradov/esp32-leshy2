#!/usr/bin/env python3
"""Generate and verify the exact H2.4.1 display-adapter schematic.

The adapter is intentionally passive.  Every contact on the 0.4-mm DF40
board-to-board plug is carried to the same numbered contact on the 0.5-mm
FH34 panel FPC connector.  Reserved panel contacts remain routed across the
replaceable adapter; the two FH34 solder hold-downs are mechanical only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_display_touch_storage import endpoint_nets
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
ADAPTER_PATH = REPO / "hardware/product-design/display-adapter.json"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
SHEET_ID = "ADP_00_DISPLAY_ADAPTER"
PROJECT_ID = "L2-DISP-ADP-001-A"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{PROJECT_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-ADP00-display-adapter.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "ADP00"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        if contact == "FITTING_1":
            number = "MP1"
        elif contact == "FITTING_2":
            number = "MP2"
        else:
            number = str(row["physical"])
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical contacts in {instance}: {numbers}")
    return pins


def footprint_for(instance: str) -> str:
    if instance == "display_adapter_plug":
        return "Connector_Hirose_DF40:Hirose_DF40C-40DP-0.4V_2x20-1MP_P0.4mm"
    if instance == "display_panel_connector":
        return "Leshy2:FH34SRJ-40S-0.5SH-99"
    raise ValueError(f"no exact adapter footprint for {instance}")


def footprint_outputs() -> dict[Path, str]:
    # Hirose drawing EDC3-159714-05, page 1/9.  For the 40-position member:
    # B=19.5 mm between contact 1/40 centres; the two 0.8-mm solder fittings
    # have 21.1-mm centre spacing (E=21.1, F=21.9) and the row spacing is
    # 3.3 mm.  The fitting pads are mechanical and deliberately use MP names.
    copper = ("F.Cu", "F.Paste", "F.Mask")
    pads = [
        (str(number), -9.75 + (number - 1) * 0.5, -1.65, 0.30, 0.80, copper)
        for number in range(1, 41)
    ]
    pads += [
        ("MP1", -10.55, 1.65, 0.80, 0.80, copper),
        ("MP2", 10.55, 1.65, 0.80, 0.80, copper),
    ]
    footprint = custom_footprint(
        "FH34SRJ-40S-0.5SH-99", pads,
        22.00, 3.80, 22.40, 4.20,
        "Hirose EDC3-159714-05 Rev.3: FH34SRJ-40S-0.5SH(99), 40 contacts on 0.50-mm pitch, B=19.5-mm contact span, 22.0x3.8-mm body and two mechanical solder fittings",
    )
    return {FOOTPRINT_DIR / "FH34SRJ-40S-0.5SH-99.kicad_mod": footprint}


def contact_map(candidate: dict) -> dict[int, str]:
    endpoints, _, _ = endpoint_nets(candidate, {"display_connector"})
    result = {
        number: endpoints.get(("display_connector", f"PIN_{number}"), "")
        for number in range(1, 41)
    }
    missing = [number for number, net in result.items() if not net]
    if missing:
        raise ValueError(f"UI display boundary is missing contacts: {missing}")
    return result


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    adapter = json.loads(ADAPTER_PATH.read_text(encoding="utf-8"))
    sheet_contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 2:
        raise ValueError(f"{SHEET_ID} must own exactly two ledger rows, got {len(rows)}")
    cross_contract = next(
        row for row in sheet_contract["cross_project_contracts"]
        if row["id"] == "DISPLAY_ADAPTER_40"
    )
    if SHEET_ID not in cross_contract["endpoints"]:
        raise ValueError("display-adapter cross-project contract lost ADP_00")
    if adapter["electrical"]["position_count"] != 40:
        raise ValueError("display-adapter source is no longer a 40-position contract")

    nets = contact_map(candidate)
    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
        instance = row["instance"]
        device = devices[row["device_key"]]
        ref_counts["J"] += 1
        specs.append({
            "instance": instance,
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins_for(instance, device),
            "reference": f"J{ref_counts['J']}",
            "footprint": footprint_for(instance),
        })

    placements = {
        "display_adapter_plug": (76.20, 76.20),
        "display_panel_connector": (177.80, 76.20),
    }
    library_defs = []
    symbol_coords = {}
    for spec in specs:
        lib, coords, _ = library_symbol(
            spec["instance"], spec["pins"], "J", spec["footprint"], spec["role"],
            True, True, True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        symbol_coords[spec["instance"]] = coords

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A3")', "\t(title_block",
        '\t\t(title "Leshy2 — passive 40-contact display adapter")',
        '\t\t(rev "H2.4.1")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    mechanical_endpoints: list[tuple[str, Pin, float, float]] = []
    for spec in specs:
        x, y = placements[spec["instance"]]
        coords = symbol_coords[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords, True, True,
            SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
        ))
        for pin in spec["pins"]:
            px, py, side = coords[pin.number]
            point = (x + px, y - py)
            if pin.contact.startswith("FITTING_"):
                mechanical_endpoints.append((spec["instance"], pin, *point))
            else:
                number = int(pin.contact.removeprefix("PIN_"))
                net_endpoints[nets[number]].append((spec["instance"], pin, *point, side))

    if sum(len(points) for points in net_endpoints.values()) != 80:
        raise ValueError("the 40 adapter contact pairs must create exactly 80 endpoints")
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            lines += [
                f'\t(label "{escaped(net)}"', f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")', "\t)",
            ]
    for instance, pin, x, y in mechanical_endpoints:
        lines += [
            f"\t(no_connect (at {x:.2f} {y:.2f})",
            f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")', "\t)",
        ]
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
        "stage": "H2.4.1",
        "status": "reviewed_exact_passive_display_adapter_sheet",
        "authority": {"baseline": "R1", "lifecycle": "historical_pre_r2_sheet_scaffold", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ADAPTER_PATH, SHEET_CONTRACT_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs),
            "one_to_one_conductors": len(nets),
            "electrical_contact_endpoints": sum(len(points) for points in net_endpoints.values()),
            "mechanical_only_fittings": len(mechanical_endpoints),
            "custom_footprints": len(footprint_outputs()),
            "active_devices": 0,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": True,
            }
            for spec in specs
        ],
        "contact_map": [
            {
                "contact": number,
                "net": nets[number],
                "adapter_plug": f"J1.{number}",
                "panel_connector": f"J2.{number}",
            }
            for number in range(1, 41)
        ],
        "intentional_no_connect_endpoints": [
            "display_panel_connector.FITTING_1",
            "display_panel_connector.FITTING_2",
        ],
        "footprint_evidence": [
            {
                "mpn": "Hirose DF40C-40DP-0.4V(51)",
                "footprint": footprint_for("display_adapter_plug"),
                "source": devices["hirose_df40c_40dp_0_4v_51"]["source"],
                "manufacturer_dimensions_mm": {"body": [9.52, 2.97, 1.14], "pitch": 0.4},
            },
            {
                "mpn": "Hirose FH34SRJ-40S-0.5SH(99)",
                "footprint": footprint_for("display_panel_connector"),
                "source": devices["hirose_fh34srj_40s_0_5sh_99"]["source"],
                "manufacturer_dimensions_mm": {
                    "body": [22.0, 3.8, 1.0], "pitch": 0.5,
                    "contact_span_B": 19.5, "fitting_centres_E": 21.1,
                },
            },
        ],
        "review_boundary": {
            "complete": [
                "both serial orderable connectors are exact MPNs with exact physical contact counts",
                "all 40 numbered contacts are preserved one-to-one with no active device or signal reinterpretation",
                "the stock DF40 footprint and manufacturer-derived FH34 footprint preserve pin-1 orientation and mechanical lands",
                "native KiCad parses the standalone adapter project and its custom footprint",
            ],
            "deferred": [
                "received HMX035CTFT-001 tail thickness, stiffener and insertion fit in H5",
                "adapter placement, routing, bend radius, DRC and panel keep-out in H6",
                "continuity, insertion retention and display HIL in H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 2,
        "schematic_symbols": 2,
        "board_fitted_symbols": 2,
        "one_to_one_conductors": 40,
        "electrical_contact_endpoints": 80,
        "mechanical_only_fittings": 2,
        "custom_footprints": 1,
        "active_devices": 0,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.4.1 accounting drifted: {manifest['summary']}")
    if len(manifest["contact_map"]) != 40:
        raise ValueError("display adapter lost its 40-position map")
    for index, row in enumerate(manifest["contact_map"], 1):
        if row["contact"] != index or row["adapter_plug"] != f"J1.{index}" or row["panel_connector"] != f"J2.{index}":
            raise ValueError(f"display adapter contact {index} is not one-to-one: {row}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 2 or schematic.count("\n\t(label \"") != 80:
        raise ValueError("display-adapter schematic symbol/label accounting mismatch")
    if schematic.count("\n\t(no_connect ") != 2:
        raise ValueError("FH34 mechanical-fitting accounting mismatch")
    footprint = generated[FOOTPRINT_DIR / "FH34SRJ-40S-0.5SH-99.kicad_mod"]
    if footprint.count('\n\t(pad "') != 42:
        raise ValueError("FH34 footprint must have 40 electrical lands and two mechanical fittings")


def find_kicad_cli() -> str:
    found = shutil.which("kicad-cli")
    if found:
        return found
    mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac.is_file():
        return str(mac)
    raise FileNotFoundError("kicad-cli not found")


def kicad_check(generated: dict[Path, str], manifest: dict) -> None:
    cli = find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-adp00-") as temp:
        staged_ecad = Path(temp) / "hardware/ecad"
        staged = staged_ecad / f"kicad/{PROJECT_ID}"
        staged.mkdir(parents=True)
        for support in (
            PROJECT_DIR / f"{PROJECT_ID}.kicad_pro",
            PROJECT_DIR / "sym-lib-table",
            PROJECT_DIR / "fp-lib-table",
        ):
            shutil.copy2(support, staged / support.name)
        libraries = staged_ecad / "libraries"
        shutil.copytree(ECAD / "libraries", libraries)
        for path, content in generated.items():
            if path == OUTPUT_SCH:
                (staged / path.name).write_text(content, encoding="utf-8")
            elif path == SYMBOL_LIBRARY:
                (libraries / path.name).write_text(content, encoding="utf-8")
            elif path.suffix == ".kicad_mod":
                (libraries / "Leshy2.pretty" / path.name).write_text(content, encoding="utf-8")
        upgraded = Path(temp) / "upgraded.pretty"
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(libraries / "Leshy2.pretty")],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected adapter footprints:\n{result.stdout}{result.stderr}")
        report = staged / "adapter-erc.json"
        result = subprocess.run(
            [cli, "sch", "erc", "--format", "json", "--severity-all", "-o", str(report), str(staged / OUTPUT_SCH.name)],
            text=True, capture_output=True,
        )
        if result.returncode or not report.is_file():
            raise RuntimeError(f"KiCad rejected display adapter:\n{result.stdout}{result.stderr}")
        erc = json.loads(report.read_text(encoding="utf-8"))
        violations = [
            violation for sheet in erc.get("sheets", [])
            for violation in sheet.get("violations", [])
        ]
        if violations:
            raise RuntimeError(f"display-adapter ERC is not empty: {violations}")
    print("ok: KiCad parsed H2.4.1 display adapter with an empty native ERC report")


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
            path for path, content in generated.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print("ok: H2.4.1 display-adapter sheet is current")
    if args.kicad_check:
        kicad_check(generated, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
