#!/usr/bin/env python3
"""Generate and verify the H2.3.8 U214 and native M5 Unit sheet.

The removable U214 Cap-Bus and the independent HY2.0-4P Unit port share only
the upstream 5-V source.  Each exposed branch has its own power qualification,
reverse blocking, discharge, signal isolation and connector-side ESD.  The
stock U214 is an external mating product and therefore never becomes a false
board footprint or board BOM item.
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
SHEET_ID = "RF_34_U214_M5_EXT"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF34-u214-m5-ext.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF34"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    unit = {"GND": "1", "5V": "2", "SIG0": "3", "SIG1": "4"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if instance == "unit_connector":
            number = unit.get(contact)
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


def footprint_for(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return ""
    exact = {
        "u214_connector": "Connector_Samtec_HLE_THT:Samtec_HLE-107-02-xx-DV-PE-LC_2x07_P2.54mm_Horizontal",
        "unit_connector": "Leshy2:1125R-SMT-4P",
        "u214_i2c_iso": "Package_SO:VSSOP-8_3x3mm_P0.65mm",
        "u214_host_buffer_a": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "u214_host_buffer_b": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "u214_return_buffer": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "u214_supervisor": "Package_TO_SOT_SMD:SOT-23-6",
        "unit_supervisor": "Package_TO_SOT_SMD:SOT-23-6",
        "unit_efuse": "Leshy2:TI-RPW0010A-VQFN-HR-10",
        "unit_signal_iso": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "ti_tpd4e05u06_dqar":
        return "Package_SON:USON-10_2.5x1.0mm_P0.5mm"
    if device_key == "murata_grm21br71e225ke11l":
        return "Capacitor_SMD:C_0805_2012Metric"
    if device_key in {"murata_grm188r71e224ka88d"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c1005", "murata_grm155")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key == "yageo_rc0603fr_071kl":
        return "Resistor_SMD:R_0603_1608Metric"
    if device_key.startswith(("yageo_rc0402", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return "X"
    if instance.endswith("connector"):
        return "J"
    if device_key.startswith(("tdk_c", "murata_grm")):
        return "C"
    if device_key.startswith(("yageo_rc", "panasonic_erj")):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    # The manufacturer drawing fixes 2-mm contact pitch, 1.01-mm signal-land
    # width, 1.50-mm anchors and the 12.0x9.1-mm body.  The complete axes and
    # land lengths below independently agree with the published OrCAD-derived
    # and KiCad implementations of this exact MPN.
    pads = [
        ("1", 3.000, -3.815, 1.010, 2.740, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
        ("2", 1.000, -3.815, 1.010, 2.740, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
        ("3", -1.000, -3.815, 1.010, 2.740, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
        ("4", -3.000, -3.815, 1.010, 2.740, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
        ("", -5.405, 3.685, 1.500, 3.000, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
        ("", 5.405, 3.685, 1.500, 3.000, ("F.Cu", "F.Paste", "F.Mask"), "rect"),
    ]
    grove = custom_footprint(
        "1125R-SMT-4P",
        pads,
        12.00,
        9.10,
        12.80,
        11.10,
        "Seeed/NS-Tech NS-1125-W00010 Rev.A exact 1125R-SMT-4P: 12.0x9.1-mm right-angle body, four 2.0-mm-pitch contacts and two anchors; complete land axes cross-checked against two independent published CAD implementations",
    )
    return {FOOTPRINT_DIR / "1125R-SMT-4P.kicad_mod": grove}


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 53:
        raise ValueError(f"{SHEET_ID} must own exactly 53 ledger rows, got {len(rows)}")
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
        on_board = row["electrical_disposition"] == "board_fitted_component"
        prefix = reference_prefix(row["instance"], row["device_key"], on_board)
        ref_counts[prefix] += 1
        specs.append({
            "instance": row["instance"],
            "device_key": row["device_key"],
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"], on_board),
            "on_board": on_board,
            "in_bom": on_board,
        })

    library_defs = []
    placements = {}
    column_x = [40.64, 96.52, 152.40, 208.28, 264.16, 320.04, 375.92, 431.80]
    cursor_y = [35.56] * len(column_x)
    for spec in specs:
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"],
            spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], spec["on_board"], spec["in_bom"],
            True, SYMBOL_NAMESPACE,
        )
        library_defs.append(lib)
        column = min(range(len(cursor_y)), key=lambda item: cursor_y[item])
        x = column_x[column]
        target_y = cursor_y[column] + height / 2
        remainder = next(iter(coords.values()))[1] % 2.54
        y = round((target_y - remainder) / 2.54) * 2.54 + remainder
        cursor_y[column] = y + height / 2 + 12.70
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — isolated U214 Cap-Bus and native M5 Unit expansion")',
        '\t\t(rev "H2.3.8")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"],
            spec["footprint"], spec["role"], x, y, coords,
            spec["on_board"], spec["in_bom"], SYMBOL_NAMESPACE, PROJECT_ID, SHEET_ID,
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
        raise ValueError(f"RF34 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

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
    board_specs = [spec for spec in specs if spec["on_board"]]
    manifest = {
        "schema_version": 1,
        "stage": "H2.3.8",
        "status": "reviewed_exact_u214_m5_expansion_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": len(board_specs),
            "external_mating_product_symbols": len(specs) - len(board_specs),
            "hierarchical_interfaces": len(interfaces),
            "physical_package_or_interface_contacts": sum(len(spec["pins"]) for spec in specs),
            "board_physical_contacts": sum(len(spec["pins"]) for spec in board_specs),
            "u214_cap_bus_contacts": len(next(spec for spec in specs if spec["instance"] == "u214")["pins"]),
            "native_unit_contacts": len(next(spec for spec in specs if spec["instance"] == "unit_connector")["pins"]),
            "independent_protected_power_branches": 2,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints": len(footprint_outputs()),
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
                "board_fitted": spec["on_board"],
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
                "mpn": devices[key]["mpn"],
                "footprint": footprint,
                "source": devices[key]["source"],
                "status": status,
            }
            for key, footprint, status in (
                ("samtec_hle_107_02_g_dv_pe_lc", "Connector_Samtec_HLE_THT:Samtec_HLE-107-02-xx-DV-PE-LC_2x07_P2.54mm_Horizontal", "exact KiCad 10 generator transcription of the Samtec series print"),
                ("seeed_1125r_smt_4p", "Leshy2:1125R-SMT-4P", "exact manufacturer geometry, independently cross-checked against published OrCAD/KiCad CAD"),
                ("tca4307dgkr", "Package_SO:VSSOP-8_3x3mm_P0.65mm", "exact TI DGK package"),
                ("nexperia_74lvc126apw_118", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "exact Nexperia TSSOP14 package"),
                ("ti_tpd4e05u06_dqar", "Package_SON:USON-10_2.5x1.0mm_P0.5mm", "exact TI DQA package"),
                ("ti_tps259470l_rpwr", "Leshy2:TI-RPW0010A-VQFN-HR-10", "exact TI RPW package already controlled by RF03"),
                ("ti_tps3808g33_dbvr", "Package_TO_SOT_SMD:SOT-23-6", "exact TI DBV package"),
                ("ti_txs0102_dcur", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "exact TI DCU package"),
            )
        ],
        "connector_cad_cross_checks": [
            {
                "mpn": "1125R-SMT-4P",
                "source": "Seeed/NS-Tech NS-1125-W00010 Rev.A manufacturer drawing",
                "url": "https://statics3.seeedstudio.com/fusion/opl/datasheet/320110032.pdf",
                "role": "authoritative body, pitch, land-width and anchor geometry",
            },
            {
                "mpn": "1125R-SMT-4P",
                "source": "Blues OrCAD-derived KiCad library",
                "url": "https://github.com/blues/blues-kicad-lib/blob/43a444c407770574958df7fc5fb36ab590af02f3/blues-kicad-lib.pretty/J-4-0200-MOS-GROVE.kicad_mod",
                "role": "independent full-axis and land-length cross-check",
            },
            {
                "mpn": "1125R-SMT-4P",
                "source": "Jeff Makes KiCad library",
                "url": "https://github.com/jeffmakes/jeffmakes-kicad-library/blob/main/jeffmakes-kicad-library.pretty/1125R-SMT-4P.kicad_mod",
                "role": "second independent pitch, land and anchor cross-check",
            },
        ],
        "corrections_closed": [
            "the stock U214 remains an external interface-only symbol and cannot appear in the board BOM or placement set",
            "the exact fourteen-contact U214 map terminates one-to-one at the pass-through HLE host socket",
            "the native M5 Unit port has the user-visible GND, 5V, SIG0, SIG1 order bound to four real footprint lands",
            "U214 SPI, UART, reset and return paths are independently Ioff-buffered, source-terminated and connector-ESD-protected",
            "U214 I2C uses a separate hot-swap/stuck-bus boundary and cannot stall the internal system I2C bus",
            "the two exposed 5-V branches remain reverse-blocked, current-limited, slew-controlled, discharged and independently qualified",
        ],
        "review_boundary": {
            "complete": [
                "all 53 RF34 ledger instances, 228 physical contacts, 27 hierarchy interfaces and intentional NC contacts are explicit",
                "the U214 and native Unit connectors have separate protected power, readiness, signal-isolation and ESD boundaries",
                "the exact HLE footprint and complete documented 1125R land pattern remove any pre-KiCad sample dependency",
                "native KiCad parses RF34 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received U214 insertion force, retention, repeated-cycle continuity and 56-mm screw preload close in H5/H8",
                "received HY2.0 cable polarity, retention and strain relief close in H8 without changing footprint geometry",
                "branch inrush, reverse-source, current limit, brownout, stuck-bus and wrong-accessory fault injection close in H3/H8",
                "placement, exposed-connector return geometry, ESD via fields and complete DRC close in H6",
                "accessory manifests, protocol profiles and fail-closed admission behavior close in firmware F3/F4 and H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 53,
        "schematic_symbols": 53,
        "board_fitted_symbols": 52,
        "external_mating_product_symbols": 1,
        "hierarchical_interfaces": 27,
        "physical_package_or_interface_contacts": 228,
        "board_physical_contacts": 214,
        "u214_cap_bus_contacts": 14,
        "native_unit_contacts": 4,
        "independent_protected_power_branches": 2,
        "intentional_no_connect_pins": 22,
        "custom_footprints": 1,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.8 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 53:
        raise ValueError("RF34 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 27:
        raise ValueError("RF34 hierarchy accounting mismatch")
    expected_nc = {
        *(f"u214_esd_{array}.NC_{pin}" for array in "abc" for pin in (6, 7, 9, 10)),
        *(f"unit_esd.NC_{pin}" for pin in (6, 7, 9, 10)),
        "u214_host_buffer_b.2Y", "u214_host_buffer_b.3Y", "u214_host_buffer_b.4Y",
        "unit_efuse.AUXOFF", "unit_esd.D2_MINUS", "unit_esd.D2_PLUS",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF34 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    u214 = next(row for row in manifest["instances"] if row["instance"] == "u214")
    if u214["board_fitted"] or u214["footprint"]:
        raise ValueError("external U214 became a fictitious board component")
    for row in manifest["instances"]:
        if row["board_fitted"] and not row["footprint"]:
            raise ValueError(f"fitted RF34 component lacks footprint: {row['instance']}")
    grove = generated[FOOTPRINT_DIR / "1125R-SMT-4P.kicad_mod"]
    if any(grove.count(f'\n\t(pad "{number}" ') != 1 for number in range(1, 5)):
        raise ValueError("1125R footprint must contain electrical lands 1..4 exactly once")
    if grove.count('\n\t(pad "" ') != 2:
        raise ValueError("1125R footprint must contain two unnumbered mechanical anchors")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf34-") as temp:
        staged = Path(temp) / "RF_34_U214_M5_EXT.kicad_sch"
        shutil.copy2(OUTPUT_SCH, staged)
        result = subprocess.run(
            [cli, "sch", "export", "python-bom", "-o", str(Path(temp) / "bom.xml"), str(staged)],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected RF34:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed the exact H2.3.8 U214/M5 Unit sheet")


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
        stale = [path.relative_to(REPO) for path, content in generated.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path}")
            return 1
        print("ok: H2.3.8 U214/M5 Unit sheet is current")
        if args.kicad_check:
            kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
