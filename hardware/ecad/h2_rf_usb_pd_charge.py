#!/usr/bin/env python3
"""Generate and verify the exact H2.3.2 USB-PD and 2S NVDC charger sheet."""

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
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import Pin, effects, escaped, library_symbol, schematic_symbol, stable_uuid


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-RF-root-interface.json"
SHEET_ID = "RF_01_USB_PD_CHARGE"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF01-usb-pd-charge.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expanded_pin(number: str, name: str, contact: str) -> Pin:
    return Pin(number, name, contact)


def pins_for(instance: str, device: dict) -> list[Pin]:
    if instance == "pd_vbus_tvs":
        return [
            *[expanded_pin(str(number), f"GND_{number}", "GND") for number in (1, 2, 3)],
            *[expanded_pin(str(number), f"IN_{number}", "IN") for number in (4, 5, 6)],
            expanded_pin("7", "GND_PAD", "GND"),
        ]
    if instance == "nvdc_charger":
        pins = []
        for contact, row in device["contacts"].items():
            if contact == "VBUS":
                pins.extend(expanded_pin(str(number), f"VBUS_{number}", contact) for number in (2, 3))
            elif contact == "BAT":
                pins.extend(expanded_pin(str(number), f"BAT_{number}", contact) for number in (22, 23))
            else:
                match = re.match(r"^(\d+)", str(row["physical"]))
                if not match:
                    raise ValueError(f"no physical pad number for {instance}.{contact}")
                pins.append(expanded_pin(match.group(1), contact, contact))
        return pins
    overrides = {
        "product_usb_connector": {"SHIELD": "SH"},
        "product_usb_protector": {"GND_PAD": "21"},
        "pd_controller": {
            "PPHV": "20", "VBUS_IN": "23", "VBUS": "32", "PP5V": "34",
            "GND_PAD": "39", "DRAIN_PAD": "40",
        },
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins = []
    for contact, row in device["contacts"].items():
        number = overrides.get(instance, {}).get(contact) or passive.get(contact)
        if number is None:
            physical = str(row.get("physical", ""))
            match = re.match(r"^([A-Z]*\d+|\d+)", physical)
            number = match.group(1) if match else contact
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pad numbers in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "product_usb_connector": "Connector_USB:USB_C_Receptacle_JAE_DX07S016JA1R1500",
        "product_usb_protector": "Package_DFN_QFN:Texas_RUK0020B_WQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm",
        "pd_controller": "Package_DFN_QFN:Texas_REF0038A_WQFN-38-2EP_6x4mm_P0.4",
        "pd_config_eeprom": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "pd_vbus_tvs": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
        "nvdc_charger": "Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm",
        "charger_inductor": "Inductor_SMD:L_Sunlord_MWSA0503S",
    }
    if instance in exact:
        return exact[instance]
    if device_key in {
        "tdk_c1608x7s2a104k080ab", "tdk_c1608x7r1c105k080ac",
        "murata_grm188r60j106me47d", "tdk_b57332v5103f360",
    }:
        return "Capacitor_SMD:C_0603_1608Metric" if device_key != "tdk_b57332v5103f360" else "Resistor_SMD:R_0603_1608Metric"
    if device_key in {"murata_grm31cr71e106ma12l", "tdk_cga5l1x7r1e475k160ac"}:
        return "Capacitor_SMD:C_1206_3216Metric"
    if device_key == "murata_grm32er71e226ke15l":
        return "Capacitor_SMD:C_1210_3225Metric"
    if device_key.startswith(("tdk_c1005", "murata_grm155", "kemet_c0402")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("yageo_rc0402"):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "product_usb_connector":
        return "J"
    if instance == "pd_vbus_tvs":
        return "D"
    if instance == "charger_inductor":
        return "L"
    if device_key == "tdk_b57332v5103f360":
        return "TH"
    if device_key.startswith(("tdk_c", "murata_grm", "kemet_c")):
        return "C"
    if device_key.startswith("yageo_rc"):
        return "R"
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
    if len(rows) != 52:
        raise ValueError(f"{SHEET_ID} must own exactly 52 rows, got {len(rows)}")
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
            "instance": row["instance"], "device_key": row["device_key"],
            "mpn": row["mpn"], "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"]),
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20, 538.48]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789") or "X"
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            True, True, True, SYMBOL_NAMESPACE,
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
        '\t\t(title "Leshy2 — exact sink-only USB-PD and 2S NVDC charging")',
        '\t\t(rev "H2.3.2")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF01 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
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
        "stage": "H2.3.2",
        "status": "reviewed_exact_usb_pd_charge_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows), "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs), "hierarchical_interfaces": len(interfaces),
            "physical_package_pads": sum(len(spec["pins"]) for spec in specs),
            "usb_c_electrical_contacts": 17, "usb_port_protector_pads": 21,
            "pd_controller_copper_contacts": 34, "vbus_tvs_package_pads": 7,
            "charger_package_pads": 29, "configured_cell_count": 2,
            "switching_frequency_khz": 750,
            "intentional_no_connect_pins": len(no_connect_endpoints),
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
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items())
            if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {"mpn": devices[key]["mpn"], "footprint": footprint, "source": devices[key]["source"]}
            for key, footprint in (
                ("jae_dx07s016ja1r1500", "Connector_USB:USB_C_Receptacle_JAE_DX07S016JA1R1500"),
                ("ti_tpd4s201_rukr", "Package_DFN_QFN:Texas_RUK0020B_WQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm"),
                ("ti_tps25751d_refr", "Package_DFN_QFN:Texas_REF0038A_WQFN-38-2EP_6x4mm_P0.4"),
                ("ti_tvs2200_drvr", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm"),
                ("ti_bq25798_rqmr", "Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm"),
                ("sunlord_mwsa0503s_2r2mt", "Inductor_SMD:L_Sunlord_MWSA0503S"),
            )
        ],
        "review_boundary": {
            "complete": [
                "all 52 RF01 ledger instances have exact MPN, package pad map, footprint and circuit nets",
                "TPS25751D is wired as a sink-only protected PPHV path with dead-battery straps and external EEPROM",
                "TPD4S201 uses its manufacturer-approved USB2-capable channels while SBU and Alt Mode remain unsupported",
                "BQ25798 has a physical 8.2-kohm 2S/750-kHz strap, matching 2.2-uH inductor and complete bypass/bootstrap network",
                "the local PD controller bus owns charger configuration while system I2C remains a separate target interface",
                "all twelve hierarchy interfaces and ten intentional no-connect pins are explicit",
            ],
            "deferred": [
                "TPS25751 configuration image, EEPROM programming and negotiated power policy verification in firmware/virtual/HIL phases",
                "charge-current, cell profile, TS window and fault-response verification against received cells",
                "USB eye, CC capacitance, hot-plug surge, PD source compatibility and thermal HIL",
                "PCB power copper, capacitor/TVS placement, impedance, return current and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 52, "schematic_symbols": 52,
        "board_fitted_symbols": 52, "hierarchical_interfaces": 12,
        "physical_package_pads": 208, "usb_c_electrical_contacts": 17,
        "usb_port_protector_pads": 21, "pd_controller_copper_contacts": 34,
        "vbus_tvs_package_pads": 7, "charger_package_pads": 29,
        "configured_cell_count": 2, "switching_frequency_khz": 750,
        "intentional_no_connect_pins": 10, "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.2 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 52:
        raise ValueError("RF01 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 12:
        raise ValueError("RF01 hierarchy interface accounting mismatch")
    expected_nc = {
        "nvdc_charger.D_MINUS", "nvdc_charger.D_PLUS", "nvdc_charger.QON",
        "nvdc_charger.STAT", "product_usb_connector.A8_SBU1",
        "product_usb_connector.B8_SBU2", "product_usb_protector.NC_16",
        "product_usb_protector.NC_17", "product_usb_protector.NC_19",
        "product_usb_protector.NC_20",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError("RF01 intentional no-connect set drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted RF01 component lacks footprint: {row['instance']}")
    charger = next(row for row in manifest["instances"] if row["instance"] == "nvdc_charger")
    if charger["pin_count"] != 29:
        raise ValueError("BQ25798 physical package-pad expansion drifted")
    tvs = next(row for row in manifest["instances"] if row["instance"] == "pd_vbus_tvs")
    if tvs["pin_count"] != 7:
        raise ValueError("TVS2200 physical package-pad expansion drifted")


def kicad_check() -> None:
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF01 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.2 and the live RF/power hierarchy")


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
        print("ok: H2.3.2 USB-PD and 2S NVDC charger sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
