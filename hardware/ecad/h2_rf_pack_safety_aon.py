#!/usr/bin/env python3
"""Generate and verify the exact H2.3.3 pack admission and safety sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_dual_nmos import PIN_MAP as DUAL_NMOS_PIN_MAP, validate_dual_nmos
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
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
SHEET_ID = "RF_02_PACK_SAFETY_AON"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF02-pack-safety-aon.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
FOOTPRINT_DIR = ECAD / "libraries/Leshy2.pretty"
SYMBOL_NAMESPACE = "RF02"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    if instance == "pack_power_fet":
        return [
            Pin("1", "G1", "G1"), Pin("2", "D_COMMON_2", "D_COMMON"),
            Pin("3", "D_COMMON_3", "D_COMMON"), Pin("4", "G2", "G2"),
            Pin("5", "S2_5", "S2"), Pin("6", "S2_6", "S2"),
            Pin("7", "S1_7", "S1"), Pin("8", "S1_8", "S1"),
            Pin("9", "D_COMMON_EP", "D_COMMON"),
        ]
    if instance == "pack_diag_timer":
        pins = []
        for contact, row in device["contacts"].items():
            number = re.match(r"^(\d+)", str(row["physical"])).group(1)
            pins.append(Pin(number, contact, contact))
            if contact == "GND":
                pins.append(Pin("17", "GND_EP", contact))
        return pins
    passive = {"END_1": "1", "END_2": "2"}
    overrides = {
        "pack_holder": {
            "SLOT0_POS": "1", "SLOT0_NEG": "2",
            "SLOT1_POS": "3", "SLOT1_NEG": "4",
        },
        "pack_cell0": {"POS": "1", "NEG": "2"},
        "pack_cell1": {"POS": "1", "NEG": "2"},
    }
    pins = []
    for contact, row in device["contacts"].items():
        number = overrides.get(instance, {}).get(contact) or passive.get(contact)
        if number is None:
            match = re.match(r"^(\d+)", str(row.get("physical", "")))
            if not match:
                raise ValueError(f"no physical pad number for {instance}.{contact}")
            number = match.group(1)
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pad numbers in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return ""
    exact = {
        "pack_gauge": "Package_DFN_QFN:TQFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
        "pack_admission": "Package_SO:Texas_DGS0020A_TSSOP-20_3x5.1mm_P0.5mm",
        "pack_power_fet": "Leshy2:CSD87313DMS",
        "pack_fuse0": "Leshy2:0451005.MRL",
        "pack_fuse1": "Leshy2:0451005.MRL",
        "pack_holder": "Leshy2:Keystone-1048P",
        "pack_diag_timer": "Leshy2:TPUL2G223BQBR",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "vishay_wsl25125l000fea":
        return "Resistor_SMD:R_2512_6332Metric"
    if device_key == "diodes_2n7002dw_7_f":
        return "Package_TO_SOT_SMD:SOT-363_SC-70-6"
    if device_key in {"onsemi_bav70lt1g", "diodes_bat54_7_f", "diodes_dmn2056u_7"}:
        return "Package_TO_SOT_SMD:SOT-23"
    if device_key in {"panasonic_erj_p08f10r0v", "panasonic_erj_p08f49r9v"}:
        return "Resistor_SMD:R_1206_3216Metric"
    if device_key == "bourns_crm2512_fx_20r0elf":
        return "Resistor_SMD:R_2512_6332Metric"
    if device_key in {"tdk_b57332v5103f360", "murata_grm188r71e474ka12d", "murata_grm188r60j106me47d", "tdk_c1608x7r1c105k080ac"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key == "murata_grm31c5c1h224je02l":
        return "Capacitor_SMD:C_1206_3216Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402", "murata_grm155")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc0402", "uniroyal_0402wgf")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return "BT"
    if "fuse" in instance:
        return "F"
    if device_key == "tdk_b57332v5103f360":
        return "RT"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj", "vishay_wsl", "bourns_crm")):
        return "R"
    if device_key in {"onsemi_bav70lt1g", "diodes_bat54_7_f"}:
        return "D"
    if instance == "pack_holder":
        return "BT"
    return "Q" if device_key in {"diodes_2n7002dw_7_f", "diodes_dmn2056u_7"} else "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    copper_no_paste = ("F.Cu", "F.Mask")
    paste = ("F.Paste",)

    csd_pads = []
    for index in range(4):
        y = -0.975 + index * 0.65
        csd_pads.append((str(1 + index), -1.655, y, 1.14, 0.32, copper, "rect"))
        csd_pads.append((str(8 - index), 1.655, y, 0.40, 0.32, copper, "rect"))
    csd_pads += [
        ("9", 0.0, 0.0, 1.28, 1.66, copper_no_paste, "rect"),
        ("9", 0.0, 0.0, 1.05, 1.37, paste, "rect"),
    ]
    csd = custom_footprint(
        "CSD87313DMS", csd_pads, 3.30, 3.30, 4.70, 3.70,
        "TI SLPS642 DMS recommended PCB pattern: 0.65-mm pitch, four 1.14x0.32-mm and four 0.40x0.32-mm perimeter lands plus the 1.28x1.66-mm common-drain exposed clip",
    )

    bqb_pads = [
        ("1", -0.25, 1.55, 0.24, 0.60, copper, "rect"),
        ("2", 0.25, 1.55, 0.24, 0.60, copper, "rect"),
        ("9", -0.25, -1.55, 0.24, 0.60, copper, "rect"),
        ("10", 0.25, -1.55, 0.24, 0.60, copper, "rect"),
    ]
    for index in range(6):
        y = 1.25 - index * 0.50
        bqb_pads.append((str(3 + index), -1.20, y, 0.60, 0.24, copper, "rect"))
        bqb_pads.append((str(16 - index), 1.20, -y, 0.60, 0.24, copper, "rect"))
    bqb_pads += [
        ("17", 0.0, 0.0, 1.00, 2.30, copper_no_paste, "rect"),
        ("17", 0.0, 0.0, 0.95, 1.79, paste, "rect"),
    ]
    bqb = custom_footprint(
        "TPUL2G223BQBR", bqb_pads, 2.50, 3.50, 3.00, 4.00,
        "TI BQB0016A 4224640/B January 2026: 16x 0.24x0.60-mm lands, 0.50-mm pitch, 2.5x3.3-mm outer land span and 1.0x2.3-mm exposed pad",
    )

    fuse = custom_footprint(
        "0451005.MRL",
        [("1", -1.955, 0.0, 2.95, 3.15, copper, "rect"),
         ("2", 1.955, 0.0, 2.95, 3.15, copper, "rect")],
        6.10, 2.69, 7.20, 3.60,
        "Littelfuse 451/453 Nano2 drawing: 6.10x2.69-mm body and 6.86x3.15-mm recommended two-land envelope",
    )

    # The official drawing controls the complete body and four independent SMT
    # terminations.  Pad-to-slot polarity still has a received-continuity H5
    # gate, so the four logical pad identities may not be used for fabrication
    # release until that gate closes.
    holder = custom_footprint(
        "Keystone-1048P",
        [("1", -41.0, -9.55, 4.0, 6.0, copper, "rect"),
         ("2", 41.0, -9.55, 4.0, 6.0, copper, "rect"),
         ("3", -41.0, 9.55, 4.0, 6.0, copper, "rect"),
         ("4", 41.0, 9.55, 4.0, 6.0, copper, "rect")],
        86.0, 39.8, 87.0, 40.8,
        "Keystone 1048P manufacturer drawing: 86.0x39.8-mm dual polarized holder and four independent SMT termination reserves; exact slot-polarity continuity remains the declared H5 received-part gate",
    )
    return {
        FOOTPRINT_DIR / "CSD87313DMS.kicad_mod": csd,
        FOOTPRINT_DIR / "TPUL2G223BQBR.kicad_mod": bqb,
        FOOTPRINT_DIR / "0451005.MRL.kicad_mod": fuse,
        FOOTPRINT_DIR / "Keystone-1048P.kicad_mod": holder,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    dual_nmos = validate_dual_nmos(
        candidate, devices, {"pack_hold", "pack_status_buffer"}
    )
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 61:
        raise ValueError(f"{SHEET_ID} must own exactly 61 rows, got {len(rows)}")
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
            "instance": row["instance"], "device_key": row["device_key"],
            "mpn": row["mpn"], "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"], on_board),
            "on_board": on_board, "in_bom": on_board,
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20, 538.48]
    cursor_y = [40.64] * len(column_x)
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
        cursor_y[column] = y + height / 2 + 15.24
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — exact fail-closed 2S pack admission and diagnostics")',
        '\t\t(rev "H2.3.3")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF02 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")
    deferred_fixture_endpoints = [
        "pack_supply_or.A2",
        "pack_admission.PA17",
        "pack_admission.PA18",
        "pack_admission.PA19_SWDIO",
        "pack_admission.PA20_SWCLK",
    ]
    deferred_fixture_labels = []
    for endpoint in deferred_fixture_endpoints:
        instance, contact = endpoint.split(".", 1)
        spec = next(row for row in specs if row["instance"] == instance)
        pin = next(row for row in spec["pins"] if row.contact == contact)
        net = endpoints[(instance, contact)]
        if net not in interfaces:
            deferred_fixture_labels.append({
                "endpoint": endpoint,
                "net": net,
                "label_uuid": stable_uuid(f"label:{instance}:{pin.number}:{net}"),
            })
    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    schematic = "\n".join(lines)
    generated = {OUTPUT_SCH: schematic, **footprint_outputs()}
    generated[SYMBOL_LIBRARY] = build_symbol_library({OUTPUT_SCH: schematic})
    manifest = {
        "schema_version": 1, "stage": "H2.3.3",
        "status": "reviewed_exact_pack_safety_aon_sheet",
        "project": PROJECT_ID, "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows), "schematic_symbols": len(specs),
            "board_fitted_symbols": sum(spec["on_board"] for spec in specs),
            "external_cell_interface_symbols": sum(not spec["on_board"] for spec in specs),
            "hierarchical_interfaces": len(interfaces),
            "physical_package_or_interface_contacts": sum(len(spec["pins"]) for spec in specs),
            "board_physical_pads": sum(len(spec["pins"]) for spec in specs if spec["on_board"]),
            "pack_gauge_package_pads": len(next(spec for spec in specs if spec["instance"] == "pack_gauge")["pins"]),
            "admission_mcu_package_pins": len(next(spec for spec in specs if spec["instance"] == "pack_admission")["pins"]),
            "pack_fet_package_pads": len(next(spec for spec in specs if spec["instance"] == "pack_power_fet")["pins"]),
            "diagnostic_timer_package_pads": len(next(spec for spec in specs if spec["instance"] == "pack_diag_timer")["pins"]),
            "permanent_admission_service_signals": 5,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints": 4, "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": spec["on_board"],
            }
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "known_deferred_fixture_labels": deferred_fixture_labels,
        "exact_dual_nmos_pinout": dual_nmos,
        "review_boundary": {
            "complete": [
                "all 61 RF02 ledger instances and all 198 physical package/interface contacts are explicit",
                "the real DGS20 pin map replaces the incorrect legacy physical numbering",
                "MAX17320, the common-drain FET, two slot fuses, four holder contacts, two protected cells and both NTCs are fully connected",
                "blank-device NRST, UART1 and SWD access are permanent and cannot bypass the external fail-closed hold",
                "the diagnostic load pulse is hardware-limited and non-retriggerable with a hardware refractory interval",
                "all fourteen hierarchy interfaces and six intentional no-connect contacts are explicit",
            ],
            "deferred": [
                "MAX17320 NVM image, checksum/readback, MSPM0 boot manager and admission thresholds in firmware/virtual/HIL phases",
                "received 1048P slot-polarity continuity, cell fit, NTC coupling and protected-cell lot qualification in H5",
                "exact pulse/cooldown, shunt Kelvin accuracy, common-drain thermal performance and hostile repetition in H3/H8",
                "PCB copper, placement, creepage, fuse hot-copper, return paths and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 61, "schematic_symbols": 61,
        "board_fitted_symbols": 59, "external_cell_interface_symbols": 2,
        "hierarchical_interfaces": 14,
        "physical_package_or_interface_contacts": 198, "board_physical_pads": 194,
        "pack_gauge_package_pads": 25, "admission_mcu_package_pins": 20,
        "pack_fet_package_pads": 9, "diagnostic_timer_package_pads": 17,
        "permanent_admission_service_signals": 5,
        "intentional_no_connect_pins": 6, "custom_footprints": 4,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.3 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 61:
        raise ValueError("RF02 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 14:
        raise ValueError("RF02 hierarchy accounting mismatch")
    expected_nc = {
        "pack_admission.PA27", "pack_admission.PA30",
        "pack_diag_timer.CH1_Q_N", "pack_diag_timer.CH2_Q",
        "pack_system_diode.NC", "pack_gauge.ZVC",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF02 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if (
        manifest["exact_dual_nmos_pinout"]["physical_pin_to_contact"]
        != DUAL_NMOS_PIN_MAP
        or set(manifest["exact_dual_nmos_pinout"]["instances"])
        != {"pack_hold", "pack_status_buffer"}
    ):
        raise ValueError("RF02 exact 2N7002DW physical/channel evidence drifted")
    expected_fixture_endpoints = set()
    if {
        row["endpoint"] for row in manifest["known_deferred_fixture_labels"]
    } != expected_fixture_endpoints:
        raise ValueError("RF02 deferred fixture-boundary set drifted")
    for row in manifest["instances"]:
        if row["board_fitted"] and not row["footprint"]:
            raise ValueError(f"fitted RF02 component lacks footprint: {row['instance']}")
        if not row["board_fitted"] and row["footprint"]:
            raise ValueError(f"external RF02 cell invented a PCB footprint: {row['instance']}")
    dgs = next(row for row in manifest["instances"] if row["instance"] == "pack_admission")
    if dgs["footprint"] != "Package_SO:Texas_DGS0020A_TSSOP-20_3x5.1mm_P0.5mm":
        raise ValueError("MSPM0C1106 lost the real DGS20 footprint")


def kicad_check() -> None:
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF02 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.3 and the live RF/power hierarchy")


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
        print("ok: H2.3.3 pack admission and safety sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
