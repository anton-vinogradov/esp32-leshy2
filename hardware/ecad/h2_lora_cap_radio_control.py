#!/usr/bin/env python3
"""Generate and verify H2.4.3 LoRa radio, control and final RF path."""

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
ACCESSORY_PATH = REPO / "hardware/accessories/leshy2-lora-cap-01.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-CAP00-root-interface.json"
SHEET_ID = "CAP_10_RADIO_CONTROL"
PROJECT_ID = "LESHY2-LORA-CAP-01"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-CAP10-radio-control.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "CAP10"
VARIANT_KEYS = ("nicerf_lora1262_868", "nicerf_lora1262_915")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "rf_sma": {
            "RF": "1", "GROUND_TOP_LEFT": "2", "GROUND_TOP_RIGHT": "3",
            "GROUND_BOTTOM_LEFT": "4", "GROUND_BOTTOM_RIGHT": "5",
        },
        "rf_detector": {"EPAD": "9"},
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins = []
    for contact, row in device["contacts"].items():
        number = overrides.get(instance, {}).get(contact, passive.get(contact))
        if number is None:
            match = re.match(r"^(\d+)", str(row.get("physical", "")))
            if not match:
                raise ValueError(f"no physical pin number for {instance}.{contact}")
            number = match.group(1)
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical contacts in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "variant_module": "Leshy2:NiceRF-LoRa126X",
        "rf_sma": "Leshy2:RFPC-SMA31-FN-175-A",
        "rf_coupler": "Leshy2:DC0710J5020AHF",
        "rf_detector": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
    }
    if instance in exact:
        return exact[instance]
    if device_key.startswith("yageo_rc0402"):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402")):
        return "Capacitor_SMD:C_0402_1005Metric"
    raise ValueError(f"no exact CAP10 footprint for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "rf_sma":
        return "J"
    if device_key.startswith("yageo_rc"):
        return "R"
    if device_key.startswith(("tdk_c", "yageo_cc")):
        return "C"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    # NiceRF LoRa126X Rev.2.3 pages 7/9: 16x16-mm module, eight pads per
    # opposing edge, 2.00-mm pitch, 1.00-mm pad width and 1.70-mm land depth.
    module_pads = []
    for index, number in enumerate(range(1, 9)):
        module_pads.append((str(number), -7.0 + index * 2.0, 7.65, 1.00, 1.70, copper))
    for index, number in enumerate(range(16, 8, -1)):
        module_pads.append((str(number), -7.0 + index * 2.0, -7.65, 1.00, 1.70, copper))
    module = custom_footprint(
        "NiceRF-LoRa126X", module_pads, 16.00, 16.00, 16.50, 16.50,
        "NiceRF LoRa126X Product Specification Rev.2.3 pages 7 and 9: 16x16-mm body, pins 1..8 and 16..9 on opposing edges, 2.00-mm pitch, 1.00-mm pad width and 1.70-mm module land depth",
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
        "DC0710J5020AHF", coupler_pads, 2.04, 1.29, 2.34, 1.59,
        "TTM DC0710J5020AHF Rev.J configuration 2: 2.04x1.29-mm body and six oriented terminals; pin 1 RF input, pin 2 forward sample, pin 5 isolated and pin 6 direct output",
    )
    return {
        FOOTPRINT_DIR / "NiceRF-LoRa126X.kicad_mod": module,
        FOOTPRINT_DIR / "DC0710J5020AHF.kicad_mod": coupler,
    }


def endpoint_nets(accessory: dict, local_instances: set[str]) -> dict[tuple[str, str], str]:
    found: dict[tuple[str, str], set[str]] = defaultdict(set)
    for route in accessory["fixed_routes"]:
        net = "GND" if route["net"] == "GND" else route["net"]
        for endpoint in (route["from"], route["to"]):
            if endpoint.startswith("abstract:") or "." not in endpoint:
                continue
            instance, contact = endpoint.split(".", 1)
            if instance in local_instances:
                found[(instance, contact)].add(net)
    explicit = {
        ("variant_module", "GND_1"): "GND",
        ("variant_module", "GND_8"): "GND",
        ("variant_module", "GND_10"): "GND",
        ("variant_module", "VCC"): "CAP_3V3",
        ("variant_module", "NC_7"): "NO_CONNECT",
        ("variant_module", "DIO3_TCXO"): "NO_CONNECT",
        ("variant_module", "NC_12"): "NO_CONNECT",
        ("variant_module", "NC_14"): "NO_CONNECT",
        ("rf_coupler", "GND_3"): "GND",
        ("rf_coupler", "GND_4"): "GND",
        ("rf_sma", "GROUND_TOP_LEFT"): "GND",
        ("rf_sma", "GROUND_TOP_RIGHT"): "GND",
        ("rf_sma", "GROUND_BOTTOM_LEFT"): "GND",
        ("rf_sma", "GROUND_BOTTOM_RIGHT"): "GND",
        ("rf_detector", "ENBL"): "CAP_3V3",
        ("rf_detector", "FLTR"): "NO_CONNECT",
        ("rf_detector", "COMM"): "GND",
        ("rf_detector", "V_DN"): "NO_CONNECT",
        ("rf_detector", "VPOS"): "CAP_3V3",
        ("rf_detector", "EPAD"): "GND",
        ("rf_detector_bypass", "END_1"): "CAP_3V3",
        ("rf_detector_bypass", "END_2"): "GND",
    }
    for endpoint, net in explicit.items():
        found[endpoint].add(net)
    result = {}
    for endpoint, nets in found.items():
        meaningful = {net for net in nets if net != "NO_CONNECT"}
        if len(meaningful) > 1:
            raise ValueError(f"one CAP10 endpoint has multiple physical nets: {endpoint} -> {sorted(meaningful)}")
        result[endpoint] = next(iter(meaningful), "NO_CONNECT")
    return result


def build() -> tuple[dict[Path, str], dict]:
    accessory = json.loads(ACCESSORY_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 8:
        raise ValueError(f"{SHEET_ID} must own eight ledger rows, got {len(rows)}")
    variant_rows = [row for row in rows if row["instance"] == "variant_module"]
    if {row["device_key"] for row in variant_rows} != set(VARIANT_KEYS):
        raise ValueError("CAP10 must expose exact EU868 and US915 assembly variants")
    interface_order = list(next(row["interfaces"] for row in root["sheets"] if row["id"] == SHEET_ID))
    interfaces = set(interface_order)
    expected_interfaces = {
        "CAP_3V3", "GND", "LORA_NRESET", "LORA_DIO1", "LORA_BUSY",
        "LORA_SCK", "LORA_MOSI", "LORA_MISO", "LORA_NSS", "RF_FORWARD_LEVEL",
    }
    if interfaces != expected_interfaces:
        raise ValueError(f"CAP10 interface drifted: {sorted(interfaces)}")

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in [item for item in rows if item["instance"] != "variant_module"]:
        prefix = reference_prefix(row["instance"], row["device_key"])
        ref_counts[prefix] += 1
        specs.append({
            "instance": row["instance"], "device_key": row["device_key"],
            "mpn": row["mpn"], "role": row["role"],
            "pins": pins_for(row["instance"], devices[row["device_key"]]),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(row["instance"], row["device_key"]),
            "ledger_rows": 1,
        })
    ref_counts["U"] += 1
    specs.append({
        "instance": "variant_module", "device_key": "nicerf_lora1262_assembly_variant",
        "mpn": "NiceRF LoRa1262-868 / LoRa1262-915 (one assembly variant)",
        "role": "one fitted region-specific SX1262 TCXO module",
        "pins": pins_for("variant_module", devices[VARIANT_KEYS[0]]),
        "reference": f"U{ref_counts['U']}",
        "footprint": footprint_for("variant_module", VARIANT_KEYS[0]),
        "ledger_rows": 2,
    })
    endpoints = endpoint_nets(accessory, {spec["instance"] for spec in specs})

    library_defs = []
    placements = {}
    column_x = [45.72, 111.76, 177.80, 243.84]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789")
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
        '\t(paper "A2")', "\t(title_block",
        '\t\t(title "Leshy2 LoRa Cap — regional SX1262, final RF feed and forward-power detector")',
        '\t\t(rev "H2.4.3")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
            net = endpoints.get((spec["instance"], pin.contact), "NO_CONNECT")
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used = set()
    no_connects = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")', "\t)",
                ]
                no_connects.append(f"{instance}.{pin.contact}")
                continue
            hierarchical = net in interfaces and net not in hierarchy_used
            if hierarchical:
                hierarchy_used.add(net)
            token = "hierarchical_label" if hierarchical else "label"
            shape = "\n\t\t(shape bidirectional)" if hierarchical else ""
            angle = 0 if side == "left" else 180
            justify = None if side == "left" else "right bottom"
            lines += [
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})", f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")', "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(f"CAP10 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")
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
        "stage": "H2.4.3",
        "status": "reviewed_exact_lora_radio_control_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (ACCESSORY_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_rows": len(rows),
            "schematic_symbols": len(specs),
            "board_fitted_symbols_per_variant": len(specs),
            "alternative_module_mpn_count": len(variant_rows),
            "fitted_variant_modules_per_assembly": 1,
            "physical_package_contacts": sum(len(spec["pins"]) for spec in specs),
            "hierarchical_interfaces": len(interfaces),
            "intentional_no_connect_pins": len(no_connects),
            "custom_footprints": len(footprint_outputs()),
            "independent_final_rf_paths": 1,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"], "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"], "mpn": spec["mpn"],
                "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
                "board_fitted": True, "ledger_rows_represented": spec["ledger_rows"],
            }
            for spec in specs
        ],
        "assembly_variants": [
            {
                "assembly": assembly,
                "device_key": row["module"],
                "mpn": devices[row["module"]]["mpn"],
                "band_label": row["band_label"],
                "shared_reference": next(spec["reference"] for spec in specs if spec["instance"] == "variant_module"),
                "fitted_quantity": 1,
            }
            for assembly, row in accessory["variants"].items()
        ],
        "intentional_no_connect_endpoints": sorted(no_connects),
        "footprint_evidence": [
            {"mpn": "NiceRF LoRa1262-868 / LoRa1262-915", "footprint": "Leshy2:NiceRF-LoRa126X", "source": devices[VARIANT_KEYS[0]]["source"]},
            {"mpn": devices["ttm_dc0710j5020ahf"]["mpn"], "footprint": "Leshy2:DC0710J5020AHF", "source": devices["ttm_dc0710j5020ahf"]["source"]},
            {"mpn": devices["adi_ad8314acpz_rl7"]["mpn"], "footprint": footprint_for("rf_detector", ""), "source": devices["adi_ad8314acpz_rl7"]["source"]},
            {"mpn": devices["gct_rfpc_sma31_fn_175_a"]["mpn"], "footprint": footprint_for("rf_sma", ""), "source": devices["gct_rfpc_sma31_fn_175_a"]["source"]},
        ],
        "corrections_closed": [
            "AD8314 V_UP, VSET and comparator input now share the one physical RF_FORWARD_LEVEL conductor instead of two aliases on V_UP",
            "the two regional modules are one assembly-option reference and can never be interpreted as two simultaneously fitted radios",
            "DIO3 on the selected TCXO module and all three manufacturer NC pads remain explicit no-connects",
            "the final SMA feed, forward sample, isolated termination, detector measurement mode, supplies and grounds are all explicit",
        ],
        "review_boundary": {
            "complete": [
                "EU868 and US915 are exact one-of-two assembly variants using the same reviewed 16-contact footprint",
                "all host SPI/control contacts terminate on the module and every module contact is connected or explicit no-connect",
                "the independent 50-Ohm final feed passes module, directional coupler and standard-polarity SMA without a switch",
                "AD8314 supply, enable, ground, exposed pad, measurement-mode tie and forward-level output are explicit",
                "native KiCad parses CAP10 and the complete live LoRa Cap hierarchy with exact findings only",
            ],
            "deferred": [
                "regional finished-product radio authorization and user-selected band enforcement",
                "50-Ohm placement/routing, coupler orientation and detector-input geometry in H6",
                "conducted RF, harmonic, output-power and detector-threshold HIL in H8",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_rows": 8,
        "schematic_symbols": 7,
        "board_fitted_symbols_per_variant": 7,
        "alternative_module_mpn_count": 2,
        "fitted_variant_modules_per_assembly": 1,
        "physical_package_contacts": 42,
        "hierarchical_interfaces": 10,
        "intentional_no_connect_pins": 6,
        "custom_footprints": 2,
        "independent_final_rf_paths": 1,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.4.3 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 7 or schematic.count("\n\t(hierarchical_label \"") != 10:
        raise ValueError("CAP10 symbol/interface accounting mismatch")
    expected_nc = {
        "rf_detector.FLTR", "rf_detector.V_DN", "variant_module.DIO3_TCXO",
        "variant_module.NC_7", "variant_module.NC_12", "variant_module.NC_14",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"CAP10 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if len(manifest["assembly_variants"]) != 2 or {row["fitted_quantity"] for row in manifest["assembly_variants"]} != {1}:
        raise ValueError("CAP10 assembly-variant accounting drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"CAP10 fitted component lacks footprint: {row['instance']}")
    module = generated[FOOTPRINT_DIR / "NiceRF-LoRa126X.kicad_mod"]
    coupler = generated[FOOTPRINT_DIR / "DC0710J5020AHF.kicad_mod"]
    if module.count('\n\t(pad "') != 16 or coupler.count('\n\t(pad "') != 6:
        raise ValueError("CAP10 custom footprint contact count drifted")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-cap10-") as temp:
        upgraded = Path(temp) / "Leshy2.pretty"
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(upgraded), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected CAP10 footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_lora_cap_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected CAP10 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.4.3 and the live LoRa Cap hierarchy")


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
            ["python3", str(ECAD / "h2_lora_cap_root.py"), "--write"],
            cwd=REPO, text=True, capture_output=True,
        )
        if root.returncode:
            raise RuntimeError(f"failed to refresh LoRa Cap hierarchy:\n{root.stdout}{root.stderr}")
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
        print("ok: H2.4.3 LoRa radio/control sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
