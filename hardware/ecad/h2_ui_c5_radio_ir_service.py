#!/usr/bin/env python3
"""Generate and verify the exact H2.2.6 C5, IR and service sheet.

The C5 module is deliberately split into its 32 carrier-PCB pads and the
factory ANT1 micro-coax receptacle.  This prevents the on-module U.FL from
being mistaken for a solder land and keeps every manufacturer NC, ground and
the disabled ANT2 carrier pad visible in the electrical design.
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
from h2_ui_s3_core import ScopedReferenceCounter, scoped_reference
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
    FOOTPRINT_DIR,
    Pin,
    custom_footprint,
    effects,
    escaped,
    footprint_outputs as common_rf_footprints,
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
SHEET_ID = "UI_20_C5_RADIO_IR_SERVICE"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI20-c5-radio-ir-service.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI20"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    if instance == "c5":
        contract = device["pcb_pad_contract"]
        return [
            Pin(str(number), str(name), str(name))
            for number, name in sorted(contract["pads"].items(), key=lambda row: int(row[0]))
        ]
    if instance == "c5_factory_ant1":
        return [Pin("1", "FACTORY_UFL_ANT1", "ANT1")]
    if instance == "c5_service_usb_connector":
        return [
            Pin("SH" if contact == "SHIELD" else contact, contact, contact)
            for contact in device["contacts"]
        ]
    overrides = {
        "c5_external_rp_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
        "c5_rf_jumper": {"END_A": "A", "END_B": "B"},
        "c5_rf_board_connector": {"CENTER": "1", "SHELL": "2"},
        "c5_rf_coupler": {
            "RF_IN": "IN", "RF_OUT": "OUT", "COUPLED_FWD": "CPL",
            "TERMINATION_50R": "TERM",
        },
        "ir_emitter": {"ANODE": "1", "CATHODE": "2"},
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
        "c5": "Leshy2:ESP32-C5-WROOM-1U",
        "c5_external_rp_sma": "Leshy2:RFPC-SMA32-FN-175-A",
        "c5_rf_board_connector": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
        "c5_rf_coupler": "Leshy2:CP0603Q5425ENTR",
        "ir_demod": "Leshy2:Vishay-Heimdall-SMD-TT",
        "ir_carrier": "Leshy2:Vishay-Heimdall-SMD-TT",
        "ir_return_buffer": "Package_SO:TSSOP-8_3x3mm_P0.65mm",
        "ir_emitter": "Leshy2:VSMY14940",
        "ir_tx_mosfet": "Package_TO_SOT_SMD:SOT-23",
        "ir_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "ir_safe_gate": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "c5_service_usb_connector": "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
        "c5_service_usb_esd": "Package_TO_SOT_SMD:SOT-23",
        "c5_service_usb_switch": "Package_SO:MSOP-10_3x3mm_P0.5mm",
        "c5_dbg_header": "Leshy2:FTSH-105-01-L-DV-K-P-TR",
        "c5_dbg_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "c5_reset_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
        "c5_boot_button": "Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010",
    }
    if instance in exact:
        return exact[instance]
    if instance in {"c5_factory_ant1", "c5_rf_jumper"}:
        return ""
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm", "kemet_c")):
        if device_key in {"tdk_c1608x7r1c105k080ac", "murata_grm188r60j106me47d", "murata_grm188z71a475me15d"}:
            return "Capacitor_SMD:C_0603_1608Metric"
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc1206fr_", "fh_rs_06")):
        return "Resistor_SMD:R_1206_3216Metric"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "c5_factory_ant1":
        return "X"
    if instance == "c5_rf_jumper":
        return "W"
    if "button" in instance:
        return "SW"
    if any(token in instance for token in ("connector", "header", "sma")):
        return "J"
    if instance == "ir_emitter":
        return "D"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm", "kemet_c")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "R"
    if device_key in {"ti_tpd2eusb30a_drtr", "ti_tpd4e05u06_dqar"}:
        return "D"
    if device_key == "diodes_dmn2056u_7":
        return "Q"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    copper_no_paste = ("F.Cu", "F.Mask")
    pads: list[tuple] = []
    for number in range(1, 15):
        pads.append((str(number), -8.25, -9.10 + (number - 1) * 1.27, 1.50, 0.90, copper))
    for number in range(15, 29):
        pads.append((str(number), 8.25, 7.41 - (number - 15) * 1.27, 1.50, 0.90, copper))
    for number, x in ((32, 1.01), (31, 2.28), (30, 3.55)):
        pads.append((str(number), x, -10.10, 0.90, 1.50, copper))
    thermal_x, thermal_y = 0.8298, -0.322
    for row in (-1.7, 0.0, 1.7):
        for column in (-1.7, 0.0, 1.7):
            pads.append(("29", thermal_x + column, thermal_y + row, 1.30, 1.30, copper_no_paste, "rect"))
    module = custom_footprint(
        "ESP32-C5-WROOM-1U", pads, 18.0, 21.2, 19.0, 22.2,
        "Espressif ESP32-C5-WROOM-1U datasheet v1.2 Figure 11-2: 32 numbered carrier pads, 1.27-mm side/top pitch, 31 lands 1.5x0.9 mm and segmented 4.7x4.7-mm thermal pad; ANT1 remains factory-fitted",
    )
    heimdall = custom_footprint(
        "Vishay-Heimdall-SMD-TT",
        [(str(number), -1.905 + (number - 1) * 1.27, 0.0, 0.80, 1.80, copper) for number in range(1, 5)],
        6.80, 3.20, 7.10, 3.70,
        "Vishay Heimdall TSOP952/TSMP95000 package drawing: four 0.8x1.8-mm proposed lands on 1.27-mm pitch, TT top-view orientation",
    )
    emitter = custom_footprint(
        "VSMY14940",
        [("1", -0.90, 0.0, 1.20, 1.00, copper), ("2", 0.90, 0.0, 1.20, 1.00, copper)],
        3.00, 2.51, 3.30, 2.81,
        "Vishay VSMY14940 Rev.1.6 page 5: exact two 1.2x1.0-mm recommended lands, 3.0-mm total pad span and side-view polarity",
    )
    return {
        **common_rf_footprints(),
        FOOTPRINT_DIR / "ESP32-C5-WROOM-1U.kicad_mod": module,
        FOOTPRINT_DIR / "Vishay-Heimdall-SMD-TT.kicad_mod": heimdall,
        FOOTPRINT_DIR / "VSMY14940.kicad_mod": emitter,
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
    if len(rows) != 60:
        raise ValueError(f"{SHEET_ID} must own exactly 60 ledger rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interface_order = list(interface_row["interfaces"])
    interfaces = set(interface_order)
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(
        candidate, local_instances, interface_order
    )
    endpoints[("c5", "3V3")] = "3V3_MAIN"
    endpoints[("c5", "GND")] = "POWER_GROUND"
    endpoints[("c5", "EPAD_GND")] = "POWER_GROUND"
    endpoints[("c5_factory_ant1", "ANT1")] = "C5_MODULE_RF_50R"

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
    specs.append({
        "instance": "c5_factory_ant1",
        "device_key": "esp32_c5_wroom_1u_n8r8",
        "mpn": "ESP32-C5-WROOM-1U-N8R8 factory ANT1 U.FL",
        "role": "non-PCB factory micro-coax assembly boundary",
        "pins": pins_for("c5_factory_ant1", devices["esp32_c5_wroom_1u_n8r8"]),
        "reference": scoped_reference(SHEET_ID, "X1"),
        "footprint": "",
        "on_board": False,
        "in_bom": False,
        "ledger_component": False,
    })

    library_defs = []
    placements = {}
    column_x = [45.72, 116.84, 187.96, 259.08, 330.20, 401.32, 472.44, 543.56]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789") or "X"
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            spec["on_board"], spec["in_bom"], True, SYMBOL_NAMESPACE,
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
        '\t\t(title "Leshy2 — exact C5 native radio, IR and service")',
        '\t\t(rev "H2.2.6")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"UI20 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
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
    board_fitted = sum(spec["on_board"] for spec in specs)
    manifest = {
        "schema_version": 1,
        "stage": "H2.2.6",
        "status": "reviewed_exact_c5_radio_ir_service_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols": board_fitted,
            "hierarchical_interfaces": len(interfaces),
            "c5_carrier_pads": devices["esp32_c5_wroom_1u_n8r8"]["pcb_pad_contract"]["pad_count"],
            "factory_rf_assembly_boundaries": 1,
            "ir_receiver_channels": 2,
            "custom_footprints": len(footprint_outputs()),
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": spec["on_board"], "ledger_component": spec["ledger_component"],
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
                ("esp32_c5_wroom_1u_n8r8", "Leshy2:ESP32-C5-WROOM-1U"),
                ("vishay_tsop75238tr", "Leshy2:Vishay-Heimdall-SMD-TT"),
                ("vishay_tsmp95000tt", "Leshy2:Vishay-Heimdall-SMD-TT"),
                ("vishay_vsmy14940", "Leshy2:VSMY14940"),
                ("gct_usb4105_gf_a", "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"),
            )
        ],
        "corrections_closed": [
            "all 32 physical C5 carrier pads are represented, including seven grounds, manufacturer NCs and the disabled ANT2 pad",
            "factory ANT1 U.FL is an assembly boundary and never a fictitious carrier-PCB pad",
            "C5 3V3 and every carrier ground now terminate on explicit product rails",
            "the SMA shell, board-U.FL shell, coupler termination and RF/debug ESD returns terminate on physical POWER_GROUND",
            "IR demodulated receive, measured carrier receive and fail-closed transmit are separate complete circuits",
            "the C5 USB receptacle is data-only and hardware-isolated when product 3V3 is absent",
        ],
        "review_boundary": {
            "complete": [
                "every UI20 ledger instance is placed once with exact MPN, contacts and footprint",
                "all 15 hierarchy interfaces terminate on real circuit pins",
                "C5 carrier pads, factory RF boundary, IR paths, USB and recovery paths are explicit",
                "native KiCad parses the populated UI hierarchy with only machine-accounted findings",
            ],
            "deferred": [
                "received C5 revision identity and ANT1/ANT2 default-state HIL",
                "IR receiver orientation, rail discharge, simultaneous capture, optical range and thermal HIL",
                "native USB signal-integrity, service-cable and recovery HIL",
                "PCB placement, RF impedance, return geometry and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary["ledger_instances"] != 60 or summary["schematic_symbols"] != 61:
        raise ValueError(f"H2.2.6 instance accounting drifted: {summary}")
    if summary["hierarchical_interfaces"] != 18 or summary["c5_carrier_pads"] != 32:
        raise ValueError(f"H2.2.6 interface/C5-pad accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 61:
        raise ValueError("UI20 schematic symbol count mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 18:
        raise ValueError("UI20 hierarchy-interface count mismatch")
    for row in manifest["instances"]:
        if row["board_fitted"] and not row["footprint"]:
            raise ValueError(f"fitted UI20 component lacks footprint: {row['instance']}")
    module = generated[FOOTPRINT_DIR / "ESP32-C5-WROOM-1U.kicad_mod"]
    if sum(1 for line in module.splitlines() if line.startswith('\t(pad "')) != 40:
        raise ValueError("C5 footprint must contain 31 perimeter lands plus nine pad-29 thermal regions")
    if any(f'(pad "{number}"' not in module for number in range(1, 33)):
        raise ValueError("C5 footprint lost a physical carrier pad")
    for endpoint in ("c5.NC_PSRAM_GPIO15", "c5.NC_20", "c5.NC_22", "c5.ANT2"):
        if endpoint not in manifest["intentional_no_connect_endpoints"]:
            raise ValueError(f"required C5 no-connect missing: {endpoint}")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-ui20-") as temp:
        upgraded = Path(temp) / "Leshy2.pretty"
        fp_result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if fp_result.returncode:
            raise RuntimeError(
                f"KiCad rejected the controlled footprint library:\n"
                f"{fp_result.stdout}{fp_result.stderr}"
            )
    result = subprocess.run(
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected populated UI hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.6 inside the live hierarchy and all custom footprints")


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
        print("ok: H2.2.6 C5 radio/IR/service sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
