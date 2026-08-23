#!/usr/bin/env python3
"""Generate and verify the exact H2.3.13 RF/power manufacturing-test sheet.

The symbols are exposed copper pads made with the PCB.  They are real board
features with exact nets and footprints, but deliberately have neither an
orderable MPN nor a BOM line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import Pin, effects, escaped, library_symbol, schematic_symbol, stable_uuid


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
SHEET_CONTRACT_PATH = ECAD / "H2-sheet-contract.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-RF-root-interface.json"
SHEET_ID = "RF_60_TESTPOINTS_MANUFACTURING"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF60-testpoints-manufacturing.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
FOOTPRINT = "TestPoint:TestPoint_Pad_D1.0mm"
SYMBOL_NAMESPACE = "RF60"
EXPECTED_POINT_COUNT = 30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    contract = json.loads(SHEET_CONTRACT_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if rows:
        raise ValueError(f"{SHEET_ID} owns BOM/ledger rows even though it must contain PCB copper only")
    points = [
        row for row in contract["test_point_contracts"]
        if row["project"] == PROJECT_ID and row["test_sheet"] == SHEET_ID
    ]
    interfaces = list(next(
        row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID
    ))
    if {point["net"] for point in points} != set(interfaces):
        raise ValueError("RF60 test-point contract and live root interface differ")
    if len(points) != len({point["id"] for point in points}):
        raise ValueError("RF60 test-point identifiers are not unique")
    if len(points) != len({point["net"] for point in points}):
        raise ValueError("RF60 must expose each selected net exactly once")

    pins = [Pin("1", "TEST", "TEST")]
    definitions = []
    placements = []
    for index, point in enumerate(points, start=1):
        definition, coords, _ = library_symbol(
            point["id"], pins, "TP", FOOTPRINT, point["purpose"],
            on_board=True, in_bom=False, embedded=True, namespace=SYMBOL_NAMESPACE,
        )
        definitions.append(definition)
        column = (index - 1) % 5
        row = (index - 1) // 5
        placements.append((
            point, f"TP{index}", 45.72 + column * 76.20,
            40.64 + row * 40.64, coords,
        ))

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A2")', "\t(title_block",
        '\t\t(title "Leshy2 — exact RF/power manufacturing and diagnostic test pads")',
        '\t\t(rev "H2.3.13")', "\t)", "\t(lib_symbols", *definitions, "\t)",
    ]
    for point, reference, x, y, coords in placements:
        lines.append(schematic_symbol(
            point["id"], pins, reference, point["id"], FOOTPRINT,
            point["purpose"], x, y, coords, on_board=True, in_bom=False,
            namespace=SYMBOL_NAMESPACE, project_id=PROJECT_ID, sheet_id=SHEET_ID,
        ))
        px, py, side = coords["1"]
        pin_x, pin_y = x + px, y - py
        angle = 0 if side == "left" else 180
        justify = None if side == "left" else "right bottom"
        label_uuid = stable_uuid(f"label:{point['id']}:{point['net']}")
        lines += [
            f'\t(hierarchical_label "{escaped(point["net"])}"',
            "\t\t(shape bidirectional)",
            f"\t\t(at {pin_x:.2f} {pin_y:.2f} {angle})",
            f"\t\t{effects(justify)}",
            f'\t\t(uuid "{label_uuid}")',
            "\t)",
        ]
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
        "stage": "H2.3.13",
        "status": "reviewed_exact_rf_testpoints_manufacturing_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (LEDGER_PATH, SHEET_CONTRACT_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": 0,
            "schematic_symbols": len(points),
            "board_fitted_symbols": len(points),
            "bom_symbols": 0,
            "physical_test_pads": len(points),
            "hierarchical_interfaces": len(interfaces),
            "programming_recovery_pads": sum(
                point["net"].endswith(("SWDIO", "SWCLK", "NRST_N", "RESET_N"))
                for point in points
            ),
            "rf_evidence_pads": sum(point["net"].startswith("EV_N") for point in points),
            "intentional_no_connect_pins": 0,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": point["id"],
                "symbol_uuid": stable_uuid(f"symbol:{point['id']}"),
                "reference": reference,
                "mpn": None,
                "manufacturing_identity": "etched PCB copper feature — no purchased part",
                "footprint": FOOTPRINT,
                "net": point["net"],
                "owner_sheet": point["owner_sheet"],
                "purpose": point["purpose"],
                "board_fitted": True,
                "in_bom": False,
            }
            for point, reference, *_ in placements
        ],
        "rules": {
            "fixture_side": "RF/power-board accessible inner side; final position is closed by H6 placement review",
            "pad_geometry": "stock KiCad 1.0-mm circular exposed SMD copper pad",
            "no_bom_or_mpn": "test points are fabricated copper, not components or purchasing lines",
            "no_direct_unpermitted_tx": "RF evidence pads expose detector/comparator outputs only; RUN_PERMIT is observation-only in the fixture procedure",
            "fixture_power": "PACK_FIXTURE_3V3 is current-limited by its owning circuit; all other power pads are measurement references only",
        },
        "review_boundary": {
            "complete": [
                "all thirty selected RF/power manufacturing nets terminate on one physical 1.0-mm pad each",
                "both MSPM0 domains expose independent UART, SWD and reset recovery paths",
                "all six RF evidence nets plus the always-on aggregate and both thermal channels are fixture-observable",
                "every pad has a stable reference, purpose, owning functional sheet and exact hierarchy net",
                "all pads are excluded from BOM and purchasing while remaining real board features",
                "native KiCad parses the complete RF/power hierarchy with no child stubs or deferred fixture labels",
            ],
            "deferred": [
                "fixture pitch, side accessibility, keepouts and final pad coordinates in H6 placement review",
                "probe current limits and automated fixture procedures in manufacturing/HIL phases",
                "analog/RF injection amplitudes and protection limits in H3/H8 qualification",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 0, "schematic_symbols": EXPECTED_POINT_COUNT,
        "board_fitted_symbols": EXPECTED_POINT_COUNT, "bom_symbols": 0,
        "physical_test_pads": EXPECTED_POINT_COUNT,
        "hierarchical_interfaces": EXPECTED_POINT_COUNT,
        "programming_recovery_pads": 7, "rf_evidence_pads": 6,
        "intentional_no_connect_pins": 0, "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.13 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != EXPECTED_POINT_COUNT:
        raise ValueError("RF60 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != EXPECTED_POINT_COUNT:
        raise ValueError("RF60 hierarchy interface accounting mismatch")
    if schematic.count("\n\t\t(in_bom no)") != EXPECTED_POINT_COUNT:
        raise ValueError("RF60 test pads must be excluded from the BOM")
    if any(row["mpn"] is not None or row["in_bom"] for row in manifest["instances"]):
        raise ValueError("RF60 fabricated copper acquired a false purchasing identity")


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
        raise RuntimeError(f"KiCad rejected RF60 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.13 and the complete exact RF/power hierarchy")


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
        print("ok: H2.3.13 RF/power manufacturing-test sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
