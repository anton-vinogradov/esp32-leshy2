#!/usr/bin/env python3
"""Generate and verify the reopened H2.3.7 Sub-GHz and dual-SA818S sheet.

The CC1101 data path and both serial G-NiceRF voice modules remain electrically
and RF independent.  SA818S-U and SA818S-V share only the protected 4-V supply,
one hardware-selected RP interface and one evidence identity.  Their common
18-land footprint is reproduced from the official G-NiceRF PADS/DXF package.
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
SHEET_ID = "RF_32_SUBGHZ_VOICE"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF32-subghz-voice.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF32"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    sma = {
        "RF": "1",
        "GROUND_TOP_LEFT": "2",
        "GROUND_TOP_RIGHT": "3",
        "GROUND_BOTTOM_LEFT": "4",
        "GROUND_BOTTOM_RIGHT": "5",
    }
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if instance.endswith("_external_sma"):
            number = sma.get(contact)
        if instance == "cc" and contact == "EPAD":
            number = "21"
        if number is None:
            match = re.match(
                r"^(?:termination\s+)?(\d+)", str(row.get("physical", ""))
            )
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
        "cc_external_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "voice_external_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "voice_v_external_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "cc": "Package_DFN_QFN:Texas_RGP0020D_VQFN-20-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
        "cc_host_buffer": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "cc_return_buffer": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "cc_band_buffer": "Package_SO:TSSOP-8_3x3mm_P0.65mm",
        "cc_crystal": "Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm",
        "cc_balun": "Leshy2:B0310J50100AHF",
        "cc_switch_a": "Leshy2:Infineon-PG-TSNP-8-1",
        "cc_switch_b": "Leshy2:Infineon-PG-TSNP-8-1",
        "cc_rf_esd": "Diode_SMD:D_0402_1005Metric",
        "voice": "Leshy2:G-NiceRF-SA818S-Official-Package",
        "voice_v": "Leshy2:G-NiceRF-SA818S-Official-Package",
        "voice_rf_esd": "Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm",
        "voice_v_rf_esd": "Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm",
        "voice_supervisor": "Package_TO_SOT_SMD:SOT-23-6",
        "voice_io_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "voice_band_io": "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
        "voice_band_inverter": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "voice_pd_gate": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "voice_control_mux_a": "Package_SO:TSSOP-10_3x3mm_P0.5mm",
        "voice_control_mux_b": "Package_SO:TSSOP-10_3x3mm_P0.5mm",
        "voice_audio_mux": "Package_SO:TSSOP-10_3x3mm_P0.5mm",
        "voice_hl_driver": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "voice_buck": "Package_TO_SOT_SMD:Texas_R-PDSO-N6_DRL-6",
        "voice_inductor": "Inductor_SMD:L_Sunlord_MWSA0503S",
        "voice_efuse": "Leshy2:TI-RPW0010A-VQFN-HR-10",
        "voice_pg_qualifier": "Package_TO_SOT_SMD:SOT-23",
        "cc_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "cc_backup_gate": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
    }
    if instance in exact:
        return exact[instance]
    if device_key.startswith("murata_lqg15"):
        return "Inductor_SMD:L_0402_1005Metric"
    if device_key == "murata_grm32er71e226ke15l":
        return "Capacitor_SMD:C_1210_3225Metric"
    if device_key in {"tdk_c1608x7r1c105k080ac", "murata_grm188r60j106me47d"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402", "murata_grm155", "murata_gjm155", "kemet_c0402")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc0402", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance.endswith("_external_sma"):
        return "J"
    if instance == "cc_crystal":
        return "Y"
    if "inductor" in instance or device_key.startswith("murata_lqg15"):
        return "L"
    if instance in {"cc_rf_esd", "voice_rf_esd", "voice_v_rf_esd"}:
        return "D"
    if instance == "voice_pg_qualifier":
        return "Q"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm", "murata_gjm", "kemet_c")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    balun = custom_footprint(
        "B0310J50100AHF",
        [
            ("1", -0.65, -0.49, 0.37, 0.30, copper),
            ("2", 0.00, -0.49, 0.37, 0.30, copper),
            ("3", 0.65, -0.49, 0.37, 0.30, copper),
            ("6", -0.65, 0.49, 0.37, 0.30, copper),
            ("5", 0.00, 0.49, 0.37, 0.30, copper),
            ("4", 0.65, 0.49, 0.37, 0.30, copper),
        ],
        2.04,
        1.29,
        2.34,
        1.59,
        "TTM B0310J50100AHF Rev.F outline: 2.04x1.29-mm body and six numbered 0.37x0.30-mm contacts on 0.65-mm columns and 0.98-mm rows; H6 owns transmission-line width and ground-via field",
    )
    bgs_grid = [
        ("1", -0.40, 0.40),
        ("2", 0.00, 0.40),
        ("3", 0.40, 0.40),
        ("4", 0.40, 0.00),
        ("5", 0.40, -0.40),
        ("6", 0.00, -0.40),
        ("7", -0.40, -0.40),
        ("8", -0.40, 0.00),
    ]
    # Infineon specifies square 0.25-mm NSMD copper lands and separate round
    # 0.25-mm stencil apertures.  Keep paste as unnumbered technical pads so
    # the electrical pad numbers remain exactly 1..8.
    bgs_pads = [
        (number, x, y, 0.25, 0.25, ("F.Cu", "F.Mask"), "rect")
        for number, x, y in bgs_grid
    ] + [
        ("", x, y, 0.25, 0.25, ("F.Paste",), "circle")
        for _number, x, y in bgs_grid
    ]
    bgs = custom_footprint(
        "Infineon-PG-TSNP-8-1",
        bgs_pads,
        1.10,
        1.10,
        1.40,
        1.40,
        "Infineon PG-TSNP-8-1 official footprint drawing and BGS13SN8 Rev.2.4: eight 0.25-mm NSMD lands around a 3x3 grid at 0.4-mm pitch, 1.1x1.1-mm body and pin-1 orientation",
    )
    # Exact common SA818S host pattern reproduced from G-NiceRF's official
    # sa818s.asc/sa818s.pcb package: 18 rectangular 2.0x3.6-mm lands, 4.45-mm
    # top/bottom pitch and four 4.6-mm-pitch lands on the right edge.
    sa818s_pads = []
    for number, x in zip(range(1, 8), (-13.35, -8.90, -4.45, 0.00, 4.45, 8.90, 13.35)):
        sa818s_pads.append((str(number), x, -9.50, 2.00, 3.60, copper, "rect"))
    for number, y in zip((8, 9, 10, 11), (-6.90, -2.30, 2.30, 6.90)):
        sa818s_pads.append((str(number), 17.80, y, 3.60, 2.00, copper, "rect"))
    for number, x in zip(range(12, 19), (13.35, 8.90, 4.45, 0.00, -4.45, -8.90, -13.35)):
        sa818s_pads.append((str(number), x, 9.50, 2.00, 3.60, copper, "rect"))
    sa818s = custom_footprint(
        "G-NiceRF-SA818S-Official-Package",
        sa818s_pads,
        35.60,
        19.00,
        39.20,
        22.60,
        "G-NiceRF official SA818S package.zip PADS/DXF host pattern: 35.60x19.00-mm body and eighteen numbered rectangular lands; received solder-fit remains H5 verification rather than an unknown land definition",
    )
    return {
        FOOTPRINT_DIR / "B0310J50100AHF.kicad_mod": balun,
        FOOTPRINT_DIR / "Infineon-PG-TSNP-8-1.kicad_mod": bgs,
        FOOTPRINT_DIR / "G-NiceRF-SA818S-Official-Package.kicad_mod": sa818s,
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
    if not rows:
        raise ValueError(f"{SHEET_ID} owns no ledger rows")
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
            "footprint_status": (
                "manufacturer_exact_land_pattern_received_fit_required"
                if row["instance"] in {"voice", "voice_v"}
                else "manufacturer_or_kicad_exact_package"
            ),
        })

    library_defs = []
    placements = {}
    column_x = [40.64, 96.52, 152.40, 208.28, 264.16, 320.04, 375.92, 431.80, 487.68, 543.56, 599.44]
    cursor_y = [35.56] * len(column_x)
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
        cursor_y[column] = y + height / 2 + 12.70
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — independent CC1101 data plus one-hot SA818S VHF/UHF voice")',
        '\t\t(rev "H2.3.7-R1")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF32 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

    deferred_fixture_endpoints = ["voice_buck.PG"]
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
    generated = {
        OUTPUT_SCH: schematic,
        SYMBOL_LIBRARY: build_symbol_library({OUTPUT_SCH: schematic}),
        **footprint_outputs(),
    }
    manifest = {
        "schema_version": 1,
        "stage": "H2.3.7-R1",
        "status": "reviewed_exact_electrical_subghz_dual_sa818s_sheet",
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
            "cc1101_package_contacts": len(next(spec for spec in specs if spec["instance"] == "cc")["pins"]),
            "sa818s_u_module_contacts": len(next(spec for spec in specs if spec["instance"] == "voice")["pins"]),
            "sa818s_v_module_contacts": len(next(spec for spec in specs if spec["instance"] == "voice_v")["pins"]),
            "independent_rf_paths": 3,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "known_deferred_fixture_boundaries": len(deferred_fixture_labels),
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
                "footprint_status": spec["footprint_status"],
                "pin_count": len(spec["pins"]),
                "board_fitted": True,
            }
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "known_deferred_fixture_labels": deferred_fixture_labels,
        "footprint_evidence": [
            {
                "mpn": devices[key]["mpn"],
                "footprint": footprint,
                "source": devices[key]["source"],
                "status": status,
            }
            for key, footprint, status in (
                ("cc1101rgpr", "Package_DFN_QFN:Texas_RGP0020D_VQFN-20-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", "exact TI RGP0020D package"),
                ("ttm_b0310j50100ahf", "Leshy2:B0310J50100AHF", "exact manufacturer contact pattern"),
                ("infineon_bgs13sn8e6327xtsa1", "Leshy2:Infineon-PG-TSNP-8-1", "exact manufacturer NSMD land and stencil pattern"),
                ("nicerf_sa818s_u_v18", "Leshy2:G-NiceRF-SA818S-Official-Package", "official G-NiceRF 18-land PADS/DXF pattern; received fit remains H5"),
                ("nicerf_sa818s_v_v18", "Leshy2:G-NiceRF-SA818S-Official-Package", "same official G-NiceRF 18-land PADS/DXF pattern; received fit remains H5"),
                ("gct_rfpc_sma31_fn_175_a", "Leshy2:RFPC-SMA31-FN-175-A", "exact manufacturer land pattern"),
            )
        ],
        "corrections_closed": [
            "the previously omitted cc_power_switch.GND contact now closes to POWER_GROUND; without it the CC1101 domain could not operate",
            "CC1101 RGP exposes twenty perimeter contacts plus its mandatory exposed ground pad",
            "the CC path has one independent SPI, switched supply, wideband balun, dual-ended three-band selector, ESD and detector route",
            "SA818S-U and SA818S-V share only the protected fixed 4.0-V rail and one hardware-selected RP interface; each retains a direct independent external RF route",
            "one select bit drives Schmitt-complemented one-hot PD and all UART, PTT/AUDIO_ON and AFOUT/MIC_IN selectors, so a band mismatch cannot enable a second module",
            "both PTT contacts default high/RX, both UART inputs default low, H/L can only be low or open and neither PD can release before the protected rail is qualified",
        ],
        "review_boundary": {
            "complete": [
                "every current RF32 ledger instance, physical contact, hierarchy interface and intentional NC contact is explicit",
                "CC1101, SA818S-U and SA818S-V have independent RF, ESD and actual-transmit sample paths",
                "primary TI, NiceRF, TTM, Infineon, Nexperia and GCT sources determine the selected bodies and physical contacts",
                "native KiCad parses RF32 in the live RF/power hierarchy with every remaining finding machine-accounted",
            ],
            "deferred": [
                "received SA818S-U/V solder-fit evidence must confirm the official host pattern in H5 before H6",
                "CC three-band conducted VNA tuning, matching values, sensitivity, output and spurious proof close in H3/H8",
                "RF placement, return geometry, ESD via fields, isolation, thermal relief and DRC close in H6",
                "both SA818S full-power thermal/current, one-hot UART/audio/PTT behavior and legal-profile HIL close in H8",
                "final CC/UHF/VHF detector thresholds and false-positive/false-negative margins close in H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 143,
        "schematic_symbols": 143,
        "board_fitted_symbols": 143,
        "hierarchical_interfaces": 40,
        "physical_package_contacts": 473,
        "cc1101_package_contacts": 21,
        "sa818s_u_module_contacts": 18,
        "sa818s_v_module_contacts": 18,
        "independent_rf_paths": 3,
        "intentional_no_connect_pins": 20,
        "known_deferred_fixture_boundaries": 0,
        "custom_footprints": 3,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.7 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 143:
        raise ValueError("RF32 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 40:
        raise ValueError("RF32 hierarchy accounting mismatch")
    expected_nc = {
        "cc_balun.DNC_5", "cc_balun.DNC_6", "cc_host_buffer.4Y",
        "cc_power_switch.NC", "cc_return_buffer.4Y", "voice.NC_2",
        "voice.NC_4", "voice.NC_11", "voice.NC_13", "voice.NC_14",
        "voice.NC_15", "voice_v.NC_2", "voice_v.NC_4", "voice_v.NC_11",
        "voice_v.NC_13", "voice_v.NC_14", "voice_v.NC_15",
        "voice_band_inverter.2Y", "voice_hl_driver.NC", "voice_io_power_switch.NC",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF32 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if manifest["known_deferred_fixture_labels"]:
        raise ValueError("RF32 deferred fixture-boundary set drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted RF32 component lacks footprint: {row['instance']}")
    if generated[FOOTPRINT_DIR / "B0310J50100AHF.kicad_mod"].count('\n\t(pad "') != 6:
        raise ValueError("B0310 footprint must contain exactly six contacts")
    bgs_footprint = generated[FOOTPRINT_DIR / "Infineon-PG-TSNP-8-1.kicad_mod"]
    if any(bgs_footprint.count(f'\n\t(pad "{number}" ') != 1 for number in range(1, 9)):
        raise ValueError("BGS13 footprint must contain electrical contacts 1..8 exactly once")
    if bgs_footprint.count('\n\t(pad "" smd circle') != 8:
        raise ValueError("BGS13 footprint must contain eight separate round stencil apertures")
    if generated[FOOTPRINT_DIR / "G-NiceRF-SA818S-Official-Package.kicad_mod"].count('\n\t(pad "') != 18:
        raise ValueError("official SA818S common host pattern must contain exactly eighteen contacts")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf32-") as temp:
        upgraded = Path(temp) / "Leshy2.pretty"
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(FOOTPRINT_DIR)],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected RF32 footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF32 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.7 and the live RF/power hierarchy")


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
            cwd=REPO,
            text=True,
            capture_output=True,
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
        print("ok: H2.3.7 Sub-GHz data and VHF/UHF voice sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
