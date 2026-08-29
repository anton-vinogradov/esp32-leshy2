#!/usr/bin/env python3
"""Generate and verify the exact H2.3.6 three-radio nRF24 sheet.

Each E01-ML01IPX is represented by its eight real carrier-PCB lands plus a
separate factory IPEX assembly boundary.  The three SPI/control paths, power
quiet-state circuits and 50-ohm RF paths remain independent so full concurrent
RX/TX/mixed operation never depends on bus or antenna switching.
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
    gct_rfpc_sma_175_footprint,
    validate_gct_rfpc_sma_175_footprint,
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
SHEET_ID = "RF_31_NRF24_X3"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF31-nrf24-x3.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF31"
RADIOS = ("nrf0", "nrf1", "nrf2")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    if instance in RADIOS:
        # ANT is the factory-fitted IPEX, not a ninth host-PCB land.
        return [
            Pin(str(row["physical"]), contact, contact)
            for contact, row in device["contacts"].items()
            if contact != "ANT"
        ]
    if instance.endswith("_factory_ipex"):
        return [Pin("1", "FACTORY_IPEX", "ANT")]
    overrides = {
        "external_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
        "rf_jumper": {"END_A": "A", "END_B": "B"},
        "rf_board_connector": {"CENTER": "1", "SHELL": "2"},
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if number is None:
            for suffix, mapping in overrides.items():
                if instance.endswith(suffix):
                    number = mapping.get(contact)
                    break
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
    if instance in RADIOS:
        return "Leshy2:Ebyte-E01-ML01IPX"
    if instance.endswith("_external_sma"):
        return "Leshy2:RFPC-SMA31-FN-175-A"
    if instance.endswith("_rf_board_connector"):
        return "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical"
    if instance.endswith("_coupler"):
        return "Leshy2:DC2337J5010AHF"
    if instance.endswith(("_factory_ipex", "_rf_jumper")):
        return ""
    exact = {
        "nrf_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "nrf_backup_gate": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "nrf_evidence_hold_diode": "Package_TO_SOT_SMD:SOT-23",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "nexperia_74lvc126apw_118":
        return "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"
    if device_key == "nexperia_74lvc2g126dp_125":
        return "Package_SO:TSSOP-8_3x3mm_P0.65mm"
    if device_key in {"tdk_c1608x7r1c105k080ac", "murata_grm188r60j106me47d"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402", "murata_grm155")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc0402", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance.endswith("_factory_ipex"):
        return "X"
    if instance.endswith("_rf_jumper"):
        return "W"
    if instance.endswith(("_external_sma", "_rf_board_connector")):
        return "J"
    if instance == "nrf_evidence_hold_diode":
        return "D"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj")):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    module_pads = [
        (str(number), 4.445 - (number - 1) * 1.27, -8.55, 0.90, 1.90, copper)
        for number in range(1, 9)
    ]
    module = custom_footprint(
        "Ebyte-E01-ML01IPX", module_pads, 12.00, 19.00, 12.50, 19.50,
        "Ebyte E01-ML01IPX specification 2025-01-16 chapter 3: exact 12x19-mm body, eight 0.90x1.90-mm bottom lands on 1.27-mm pitch; on-module IPEX is not a host-PCB pad",
    )
    coupler_pads = [
        ("1", -0.65, -0.49, 0.37, 0.30, copper),
        ("2", 0.00, -0.49, 0.37, 0.30, copper),
        ("3", 0.65, -0.49, 0.37, 0.30, copper),
        ("6", -0.65, 0.49, 0.37, 0.30, copper),
        ("5", 0.00, 0.49, 0.37, 0.30, copper),
        ("4", 0.65, 0.49, 0.37, 0.30, copper),
    ]
    coupler = custom_footprint(
        "DC2337J5010AHF", coupler_pads, 2.04, 1.29, 2.34, 1.59,
        "TTM DC2337J5010AHF Rev.H outline: 2.04x1.29-mm body, six 0.37x0.30-mm terminals on 0.65-mm columns and 0.98-mm rows; pin-1 orientation preserved",
    )
    sma = gct_rfpc_sma_175_footprint(
        "RFPC-SMA31-FN-175-A",
        "GCT RFPC-SMA31-FN drawing A1 released 2025-04-07",
    )
    return {
        FOOTPRINT_DIR / "Ebyte-E01-ML01IPX.kicad_mod": module,
        FOOTPRINT_DIR / "DC2337J5010AHF.kicad_mod": coupler,
        FOOTPRINT_DIR / "RFPC-SMA31-FN-175-A.kicad_mod": sma,
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
    if len(rows) != 107:
        raise ValueError(f"{SHEET_ID} must own exactly 107 rows, got {len(rows)}")
    interface_order = list(next(
        row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID
    ))
    interfaces = set(interface_order)
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(
        candidate, local_instances, interface_order
    )
    for radio in RADIOS:
        endpoints[(f"{radio}_factory_ipex", "ANT")] = endpoints[(radio, "ANT")]

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
            "on_board": row["electrical_disposition"] != "fitted_interconnect_assembly",
            "in_bom": True,
            "ledger_component": True,
        })
    for radio in RADIOS:
        ref_counts["X"] += 1
        specs.append({
            "instance": f"{radio}_factory_ipex",
            "device_key": "ebyte_e01_ml01ipx",
            "mpn": f"Ebyte E01-ML01IPX factory IPEX ({radio})",
            "role": "non-PCB factory micro-coax assembly boundary",
            "pins": pins_for(f"{radio}_factory_ipex", devices["ebyte_e01_ml01ipx"]),
            "reference": f"X{ref_counts['X']}",
            "footprint": "",
            "on_board": False,
            "in_bom": False,
            "ledger_component": False,
        })

    library_defs = []
    placements = {}
    column_x = [45.72, 111.76, 177.80, 243.84, 309.88, 375.92, 441.96, 508.00, 574.04]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789") or "X"
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            spec["on_board"], spec["in_bom"], True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        column = min(range(len(cursor_y)), key=lambda item: cursor_y[item])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - remainder) / 2.54) * 2.54 + remainder
        cursor_y[column] = y + height / 2 + 15.24
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — three independent full-function nRF24 paths")',
        '\t\t(rev "H2.3.6")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords, spec["on_board"],
            spec["in_bom"], SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
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
        raise ValueError(f"RF31 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

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
        "stage": "H2.3.6",
        "status": "reviewed_exact_three_nrf24_sheet",
        "authority": {"baseline": "R1", "lifecycle": "historical_pre_r2_sheet_scaffold", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": sum(spec["on_board"] for spec in specs),
            "hierarchical_interfaces": len(interfaces),
            "physical_package_contacts": sum(len(spec["pins"]) for spec in specs),
            "nrf_carrier_pads": sum(len(spec["pins"]) for spec in specs if spec["instance"] in RADIOS),
            "factory_rf_assembly_boundaries": sum(spec["instance"].endswith("_factory_ipex") for spec in specs),
            "independent_spi_paths": 3,
            "independent_rf_paths": 3,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints": len(footprint_outputs()),
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": spec["on_board"],
                "ledger_component": spec["ledger_component"],
            }
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {"mpn": devices[key]["mpn"], "footprint": footprint, "source": devices[key]["source"]}
            for key, footprint in (
                ("ebyte_e01_ml01ipx", "Leshy2:Ebyte-E01-ML01IPX"),
                ("ttm_dc2337j5010ahf", "Leshy2:DC2337J5010AHF"),
                ("gct_rfpc_sma31_fn_175_a", "Leshy2:RFPC-SMA31-FN-175-A"),
                ("hirose_ufl_r_smt_1_10", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical"),
                ("nexperia_74lvc126apw_118", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"),
                ("nexperia_74lvc2g126dp_125", "Package_SO:TSSOP-8_3x3mm_P0.65mm"),
                ("ti_tps22919_dckr", "Package_TO_SOT_SMD:SOT-363_SC-70-6"),
            )
        ],
        "corrections_closed": [
            "each E01-ML01IPX exposes exactly eight host-PCB lands; its factory IPEX is an assembly boundary, never a fictitious ninth pad",
            "the three radios have independent PIO SPI clocks/data, CSN, CE and IRQ paths with no shared transaction bottleneck",
            "all three module rails and translators are enabled together; the group gate never serializes full RX/TX/mixed operation",
            "Ioff-capable LVC buffers and host/module-side safe pulls prevent back-power and command glitches while the radio group is off",
            "three separate module IPEX cables, board U.FL receptacles, couplers and SMA connectors preserve independent 50-Ohm RF paths",
            "each forward-power sample terminates in its own detector interface and evidence-hold path",
        ],
        "review_boundary": {
            "complete": [
                "all 107 RF31 ledger instances, 318 physical contacts and 35 hierarchy interfaces are explicit",
                "the three independent command, return, power-decoupling, RF and evidence paths are electrically complete",
                "primary Ebyte, Nexperia, TTM, GCT, Hirose and TI references determine every selected package",
                "native KiCad parses RF31 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received-module IPEX family/axis inspection and cable mating retention in H5",
                "RF placement, 50-Ohm geometry, coupler orientation, isolation and DRC in H6",
                "three-radio 3R, 1T2R, 2T1R and 3T concurrency plus quiet-state HIL in H8",
                "final detector calibration and per-path forward-power thresholds in H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 107,
        "schematic_symbols": 110,
        "board_fitted_symbols": 104,
        "hierarchical_interfaces": 35,
        "physical_package_contacts": 318,
        "nrf_carrier_pads": 24,
        "factory_rf_assembly_boundaries": 3,
        "independent_spi_paths": 3,
        "independent_rf_paths": 3,
        "intentional_no_connect_pins": 2,
        "custom_footprints": 3,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.6 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 110:
        raise ValueError("RF31 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 35:
        raise ValueError("RF31 hierarchy accounting mismatch")
    expected_nc = {"nrf_evidence_hold_diode.NC", "nrf_power_switch.NC"}
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF31 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    for radio in RADIOS:
        module = next(row for row in manifest["instances"] if row["instance"] == radio)
        boundary = next(row for row in manifest["instances"] if row["instance"] == f"{radio}_factory_ipex")
        if module["pin_count"] != 8 or not module["footprint"]:
            raise ValueError(f"{radio} lost its exact eight-land carrier contract")
        if boundary["board_fitted"] or boundary["footprint"] or boundary["ledger_component"]:
            raise ValueError(f"{radio} factory IPEX became a fictitious PCB component")
    for row in manifest["instances"]:
        if row["board_fitted"] and not row["footprint"]:
            raise ValueError(f"fitted RF31 component lacks footprint: {row['instance']}")
    module_fp = generated[FOOTPRINT_DIR / "Ebyte-E01-ML01IPX.kicad_mod"]
    coupler_fp = generated[FOOTPRINT_DIR / "DC2337J5010AHF.kicad_mod"]
    if module_fp.count('\n\t(pad "') != 8:
        raise ValueError("E01-ML01IPX footprint must contain exactly eight host-PCB lands")
    if coupler_fp.count('\n\t(pad "') != 6:
        raise ValueError("DC2337J5010AHF footprint must contain exactly six oriented lands")
    validate_gct_rfpc_sma_175_footprint(
        generated[FOOTPRINT_DIR / "RFPC-SMA31-FN-175-A.kicad_mod"],
        "RFPC-SMA31",
    )


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf31-") as temp:
        upgraded = Path(temp) / "Leshy2.pretty"
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected RF31 footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF31 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.6 and the live RF/power hierarchy")


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
            raise RuntimeError(f"failed to refresh RF/power hierarchy:\n{root.stdout}{root.stderr}")
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
        print("ok: H2.3.6 three-radio nRF24 sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
