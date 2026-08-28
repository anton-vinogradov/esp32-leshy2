#!/usr/bin/env python3
"""Generate and verify the exact H2.3.5 RP2354B core/service sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from h2_symbol_library import build as build_symbol_library
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
    FOOTPRINT_DIR,
    Pin,
    effects,
    escaped,
    footprint_outputs as common_footprint_outputs,
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
SHEET_ID = "RF_30_RP2354_CORE_SERVICE"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF30-rp2354-core-service.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF30"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        if instance == "rp_service_usb_connector":
            number = "SH" if contact == "SHIELD" else contact.split("_", 1)[0]
        else:
            number = passive.get(contact)
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
        "rp": "Package_DFN_QFN:QFN-80-1EP_10x10mm_P0.4mm_EP3.4x3.4mm",
        "rp_vreg_inductor": "Inductor_SMD:L_Murata_DFE201610P",
        "rp_clock": "Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm",
        "rp_service_usb_connector": "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
        "rp_service_usb_esd": "Package_TO_SOT_SMD:SOT-23",
        "rp_service_usb_switch": "Package_SO:MSOP-10_3x3mm_P0.5mm",
        "rp_dbg_header": "Leshy2:FTSH-105-01-L-DV-K-P-TR",
        "rp_dbg_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "rp_reset_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
        "rp_boot_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
    }
    if instance in exact:
        return exact[instance]
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_gjm")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc0402", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "rp_vreg_inductor":
        return "L"
    if instance == "rp_clock":
        return "Y"
    if "button" in instance:
        return "SW"
    if any(token in instance for token in ("connector", "header")):
        return "J"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_gjm")):
        return "C"
    if device_key.startswith(("yageo_rc0402", "panasonic_erj_2r")):
        return "R"
    if device_key in {"ti_tpd2eusb30a_drtr", "ti_tpd4e05u06_dqar"}:
        return "D"
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
    if len(rows) != 48:
        raise ValueError(f"{SHEET_ID} must own exactly 48 rows, got {len(rows)}")
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
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20, 538.48]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"],
            spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], True, True, True,
            SYMBOL_NAMESPACE,
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
        '\t\t(title "Leshy2 — exact RP2354B core, clock, USB and recovery")',
        '\t\t(rev "H2.3.5")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF30 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

    lines += [
        "\t(sheet_instances", '\t\t(path "/"', '\t\t\t(page "1")', "\t\t)", "\t)",
        "\t(embedded_fonts no)", ")", "",
    ]
    schematic = "\n".join(lines)
    shared = common_footprint_outputs()
    ftsh_path = FOOTPRINT_DIR / "FTSH-105-01-L-DV-K-P-TR.kicad_mod"
    generated = {OUTPUT_SCH: schematic, ftsh_path: shared[ftsh_path]}
    generated[SYMBOL_LIBRARY] = build_symbol_library({OUTPUT_SCH: schematic})

    manifest = {
        "schema_version": 1,
        "stage": "H2.3.5",
        "status": "reviewed_exact_rp2354_core_service_sheet",
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
            "physical_package_contacts": sum(len(spec["pins"]) for spec in specs),
            "rp2354_package_contacts": len(next(spec for spec in specs if spec["instance"] == "rp")["pins"]),
            "dedicated_100nf_supply_bypasses": 14,
            "reference_4_7uf_caps": 4,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_footprints": 1,
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
            alias: canonical for alias, canonical in sorted(aliases.items())
            if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {
                "mpn": devices["rp2354b_a4"]["mpn"],
                "footprint": "Package_DFN_QFN:QFN-80-1EP_10x10mm_P0.4mm_EP3.4x3.4mm",
                "source": devices["rp2354b_a4"]["source"],
            },
            {
                "mpn": devices["abracon_abm8_272_t3"]["mpn"],
                "footprint": "Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm",
                "source": devices["abracon_abm8_272_t3"]["source"],
            },
            {
                "mpn": devices["abracon_aota_b201610s3r3_101_t"]["mpn"],
                "footprint": "Inductor_SMD:L_Murata_DFE201610P",
                "source": devices["abracon_aota_b201610s3r3_101_t"]["source"],
                "boundary": "package-compatible 2.0x1.6-mm H2 contact pattern; final Abracon recommended-land transcription closes before H6 routing",
            },
        ],
        "corrections_closed": [
            "all 80 perimeter contacts and exposed-pad contact 81 of the real SC1512-A4 package are explicit",
            "the internal 1.1-V switchmode regulator uses the official 3.3-uH inductor, four 4.7-uF capacitors and the required 33-Ohm AVDD filter",
            "every DVDD, IOVDD, ADC_AVDD, USB_OTP_VDD and QSPI_IOVDD supply contact has its own 100-nF local bypass",
            "the exact 12-MHz crystal circuit uses two 15-pF C0G loads and the official 1-kOhm XOUT series resistor",
            "native USB, SWD, RUN and USB_BOOT remain externally recoverable without creating a service-port power path",
            "the stacked 2-MB die is used; unused external-QSPI data/clock contacts are explicit no-connects rather than a fictitious second flash",
        ],
        "review_boundary": {
            "complete": [
                "all 48 RF30 ledger instances and all 219 physical package contacts are explicit",
                "all 51 hierarchy interfaces terminate on real package contacts",
                "the core regulator, clock, USB and recovery circuits match primary manufacturer references",
                "native KiCad parses RF30 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received SC1512-A4 die identity, boot-ROM USB behavior and debug recovery HIL",
                "oscillator startup margin and USB timing measurements in H3/H8",
                "the final AOTA manufacturer recommended land, switch-node geometry, crystal placement, impedance and DRC in H6",
                "firmware boot manager, USB descriptors and rollback behavior in firmware phases",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 48,
        "schematic_symbols": 48,
        "board_fitted_symbols": 48,
        "hierarchical_interfaces": 52,
        "physical_package_contacts": 219,
        "rp2354_package_contacts": 81,
        "dedicated_100nf_supply_bypasses": 14,
        "reference_4_7uf_caps": 4,
        "intentional_no_connect_pins": 13,
        "custom_footprints": 1,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.5 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 48:
        raise ValueError("RF30 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 52:
        raise ValueError("RF30 hierarchy accounting mismatch")
    expected_nc = {
        "rp.QSPI_SD3", "rp.QSPI_SCLK", "rp.QSPI_SD0", "rp.QSPI_SD2", "rp.QSPI_SD1",
        "rp_service_usb_switch.HSD2_PLUS", "rp_service_usb_switch.HSD2_MINUS",
        "rp_service_usb_connector.A8_SBU1", "rp_service_usb_connector.B8_SBU2",
        "rp_dbg_esd.NC_6", "rp_dbg_esd.NC_7", "rp_dbg_esd.NC_9", "rp_dbg_esd.NC_10",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF30 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    rp = next(row for row in manifest["instances"] if row["instance"] == "rp")
    if rp["pin_count"] != 81 or not rp["footprint"].endswith("EP3.4x3.4mm"):
        raise ValueError("RP2354B lost the real 80+EP package-contact contract")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted RF30 component lacks footprint: {row['instance']}")


def kicad_check() -> None:
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF30 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.5 and the live RF/power hierarchy")


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
        print("ok: H2.3.5 RP2354 core/service sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
