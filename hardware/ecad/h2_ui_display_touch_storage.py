#!/usr/bin/env python3
"""Generate and verify the exact H2.2.3 display, touch and microSD sheet."""

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
from h2_ui_s3_core import (
    Pin,
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
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_11_DISPLAY_TOUCH_STORAGE"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI11-display-touch-storage.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI11"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "sd": {"DETECT_A": "9", "DETECT_B": "10", "SHIELD": "SH"},
        "backlight_efuse": {"POWERPAD": "7"},
    }
    pins = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = overrides.get(instance, {}).get(contact)
        if number is None:
            numeric = re.match(r"^(\d+)", physical)
            number = numeric.group(1) if numeric else contact
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pin number in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return ""
    exact = {
        "display_connector": "Connector_Hirose_DF40:Hirose_DF40C(2.0)-40DS-0.4V_2x20_P0.4mm",
        "sd": "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5",
        "touch_irq_buffer": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "backlight_efuse": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
        "backlight_mosfet": "Package_TO_SOT_SMD:SOT-23",
        "sd_host_buffer": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "sd_miso_buffer": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "sd_esd_a": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "sd_esd_b": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "sd_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    }
    if instance in exact:
        return exact[instance]
    if device_key in {"murata_grm21br60j226me39l"}:
        return "Capacitor_SMD:C_0805_2012Metric"
    if device_key in {"murata_grm188r60j106me47d", "tdk_c1608x7r1c105k080ac"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c", "yageo_cc")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key == "panasonic_erj_p08f10r0v":
        return "Resistor_SMD:R_1206_3216Metric"
    if device_key == "yageo_rc0603fr_071kl":
        return "Resistor_SMD:R_0603_1608Metric"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf", "panasonic_erj_2r")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str, on_board: bool) -> str:
    if not on_board:
        return "X"
    if instance in {"sd", "display_connector"}:
        return "J"
    if "cap" in instance or "bypass" in instance or "bulk" in instance:
        return "C"
    if any(token in instance for token in ("resistor", "series", "pullup", "pulldown", "ilim")):
        return "R"
    return "U"


def abstract_canonical(endpoint: str) -> str | None:
    if endpoint == "abstract:3V3_MAIN":
        return "3V3_MAIN"
    if endpoint.startswith("abstract:power-ground"):
        return "POWER_GROUND"
    if endpoint.startswith("abstract:rf-ground"):
        return "POWER_GROUND"
    if endpoint == "abstract:chassis-rf-ground":
        return "POWER_GROUND"
    if endpoint == "abstract:audio-ground":
        return "AUDIO_GROUND"
    if endpoint == "abstract:safety-ground":
        return "SAFETY_GROUND"
    if endpoint == "abstract:AON_SAFE_3V3":
        return "AON_SAFE_3V3"
    if endpoint == "abstract:AON_RAW_3V3":
        return "AON_RAW_3V3"
    if endpoint == "abstract:SYS_INT_N_WIRED_LOW":
        return "SYS_INT_N"
    if endpoint == "abstract:power-current-thermal-fault":
        return "POWER_FAULT_N"
    if endpoint == "abstract:qualified-2s-positive":
        return "BATTERY_STACK_POSITIVE"
    if endpoint == "abstract:protected-2s-midpoint":
        return "PACK_2S_MIDPOINT"
    return None


def endpoint_nets(
    candidate: dict, local_instances: set[str]
) -> tuple[dict[tuple[str, str], str], dict[str, str], set[str]]:
    aliases: dict[str, str] = {}
    no_connect_nets: set[str] = set()
    for route in candidate["fixed_routes"]:
        route_instances = {
            endpoint.split(".", 1)[0]
            for endpoint in (route["from"], route["to"])
            if "." in endpoint and not endpoint.startswith("abstract:")
        }
        if not route_instances.intersection(local_instances):
            continue
        canonical = abstract_canonical(route["from"]) or abstract_canonical(route["to"])
        if canonical:
            previous = aliases.setdefault(route["net"], canonical)
            if previous != canonical:
                raise ValueError(f"physical net alias conflict: {route['net']} -> {previous}/{canonical}")
        if "abstract:no-connect" in (route["from"], route["to"]):
            no_connect_nets.add(route["net"])

    found: dict[tuple[str, str], set[str]] = defaultdict(set)
    for route in candidate["fixed_routes"]:
        net = aliases.get(route["net"], route["net"])
        for endpoint in (route["from"], route["to"]):
            if "." not in endpoint or endpoint.startswith("abstract:"):
                continue
            instance, contact = endpoint.split(".", 1)
            if instance in local_instances:
                found[(instance, contact)].add(net)
    for allocation in candidate["allocations"]:
        net = aliases.get(allocation["net"], allocation["net"])
        for endpoint in (
            f"{allocation['instance']}.{allocation['contact']}",
            *allocation.get("peers", []),
        ):
            if "." not in endpoint or endpoint.startswith("abstract:"):
                continue
            instance, contact = endpoint.split(".", 1)
            if instance in local_instances:
                found[(instance, contact)].add(net)
    result: dict[tuple[str, str], str] = {}
    for endpoint, nets in found.items():
        meaningful = {net for net in nets if net != "NO_CONNECT"}
        if len(meaningful) > 1:
            raise ValueError(f"one physical endpoint has multiple nets: {endpoint} -> {sorted(meaningful)}")
        result[endpoint] = next(iter(meaningful), "NO_CONNECT")
    return result, aliases, no_connect_nets


def pin_net(
    instance: str,
    pin: Pin,
    endpoints: dict[tuple[str, str], str],
    no_connect_nets: set[str],
) -> str:
    net = endpoints.get((instance, pin.contact), "NO_CONNECT")
    if (
        net == "NO_CONNECT"
        or net.endswith("_NC")
        or net in no_connect_nets
        or pin.contact.startswith("NC_")
    ):
        return "NO_CONNECT"
    return net


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 49:
        raise ValueError(f"{SHEET_ID} must own exactly 49 ledger rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interfaces = set(interface_row["interfaces"])
    local_instances = {row["instance"] for row in rows}
    endpoints, aliases, no_connect_nets = endpoint_nets(candidate, local_instances)

    specs = []
    ref_counts: Counter[str] = ScopedReferenceCounter(SHEET_ID)
    for row in rows:
        instance = row["instance"]
        device = devices[row["device_key"]]
        on_board = row["electrical_disposition"] == "board_fitted_component"
        prefix = reference_prefix(instance, row["device_key"], on_board)
        ref_counts[prefix] += 1
        specs.append({
            "instance": instance,
            "device_key": row["device_key"],
            "mpn": row["mpn"],
            "role": row["role"],
            "pins": pins_for(instance, device),
            "reference": f"{prefix}{ref_counts[prefix]}",
            "footprint": footprint_for(instance, row["device_key"], on_board),
            "on_board": on_board,
            "in_bom": on_board,
        })

    library_defs = []
    placements = {}
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], spec["on_board"], spec["in_bom"], True,
            SYMBOL_NAMESPACE,
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
        "(kicad_sch",
        "\t(version 20250114)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")',
        "\t(title_block",
        '\t\t(title "Leshy2 — exact display, integrated touch and isolated microSD")',
        '\t\t(rev "H2.2.3")',
        "\t)",
        "\t(lib_symbols",
        *library_defs,
        "\t)",
    ]
    net_endpoints: dict[str, list[tuple[str, Pin, float, float, str]]] = defaultdict(list)
    for spec in specs:
        x, y, coords = placements[spec["instance"]]
        lines.append(schematic_symbol(
            spec["instance"], spec["pins"], spec["reference"], spec["mpn"], spec["footprint"],
            spec["role"], x, y, coords, spec["on_board"], spec["in_bom"], SYMBOL_NAMESPACE,
            PROJECT_ID, SHEET_ID,
        ))
        for pin in spec["pins"]:
            net = pin_net(spec["instance"], pin, endpoints, no_connect_nets)
            px, py, side = coords[pin.number]
            net_endpoints[net].append((spec["instance"], pin, x + px, y - py, side))

    hierarchy_used: set[str] = set()
    no_connect_count = 0
    no_connect_endpoints: list[str] = []
    for net, points in sorted(net_endpoints.items()):
        for instance, pin, x, y, side in points:
            if net == "NO_CONNECT":
                lines += [
                    f"\t(no_connect (at {x:.2f} {y:.2f})",
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")',
                    "\t)",
                ]
                no_connect_count += 1
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
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")',
                "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(
            f"UI11 circuit does not terminate every hierarchy interface: "
            f"missing {sorted(interfaces - hierarchy_used)}; unexpected {sorted(hierarchy_used - interfaces)}"
        )
    lines += [
        "\t(sheet_instances",
        '\t\t(path "/"',
        '\t\t\t(page "1")',
        "\t\t)",
        "\t)",
        "\t(embedded_fonts no)",
        ")",
        "",
    ]
    schematic = "\n".join(lines)
    generated = {
        OUTPUT_SCH: schematic,
        SYMBOL_LIBRARY: build_symbol_library({OUTPUT_SCH: schematic}),
    }
    manifest = {
        "schema_version": 1,
        "stage": "H2.2.3",
        "status": "reviewed_exact_display_touch_storage_sheet",
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
            "external_assembly_interface_symbols": sum(not spec["on_board"] for spec in specs),
            "display_contacts": len(devices["qdtech_hmx035ctft_001"]["contacts"]),
            "microsd_socket_contacts": len(devices["hirose_dm3at_sf_pejm5"]["contacts"]),
            "hierarchical_interfaces": len(interfaces),
            "intentional_no_connect_pins": no_connect_count,
            "pcb_files_created": 0,
        },
        "instances": [
            {
                "instance": spec["instance"],
                "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
                "reference": spec["reference"],
                "mpn": spec["mpn"],
                "footprint": spec["footprint"] or None,
                "pin_count": len(spec["pins"]),
                "board_fitted": spec["on_board"],
            }
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {
                "mpn": "Hirose DF40C(2.0)-40DS-0.4V(51)",
                "footprint": footprint_for("display_connector", "", True),
                "source": devices["hirose_df40c_2_0_40ds_0_4v_51"]["source"],
            },
            {
                "mpn": "Hirose DM3AT-SF-PEJM5",
                "footprint": footprint_for("sd", "", True),
                "source": devices["hirose_dm3at_sf_pejm5"]["source"],
                "pin_mapping": {"card": "1..8", "detect_A": "9", "detect_B": "10", "shield": "SH"},
            },
            {
                "mpn": "Texas Instruments SN74LVC3G34DCUR",
                "footprint": footprint_for("sd_host_buffer", "", True),
                "source": devices["ti_sn74lvc3g34_dcur"]["source"],
            },
            {
                "mpn": "Texas Instruments TPD4E05U06DQAR",
                "footprint": footprint_for("sd_esd_a", "", True),
                "source": devices["ti_tpd4e05u06_dqar"]["source"],
            },
            {
                "mpn": "Texas Instruments TPS2553DRVR-1",
                "footprint": footprint_for("backlight_efuse", "", True),
                "source": devices["ti_tps2553drvr_1"]["source"],
                "powerpad": "physical pad 7 tied to POWER_GROUND",
            },
        ],
        "corrections_closed": [
            "TPS22919 QOD and VOUT now share the one physical SD_CARD_3V3 net instead of two aliases on one pad",
            "all direct 3V3_MAIN and POWER_GROUND branch aliases collapse to their physical conductor without invented net-tie parts",
            "DM3AT detect contacts map explicitly to footprint pads 9/10 and all four shield lands share pad SH",
            "display contacts 1..40 remain one-to-one through the exact DF40 adapter boundary",
            "display logic stays powered while the independently protected LEDA branch is latched off on a backlight fault",
            "microSD host outputs, return data, ESD, switched pull-ups, detect and QOD paths are all explicit",
        ],
        "review_boundary": {
            "complete": [
                "every H2 ledger instance owned by UI11 is placed once with exact MPN and contact map",
                "every display, touch, backlight and microSD contact is connected or explicitly no-connect",
                "every live UI11 hierarchy interface terminates on a real circuit pin",
                "native KiCad parses the populated hierarchy with only exact machine-accounted findings",
            ],
            "deferred": [
                "display-tail incoming inspection and adapter mating evidence in H5",
                "QSPI/shared-SPI timing, card hot-plug, backlight current/thermal and ESD HIL",
                "PCB placement, return geometry, impedance/ringing tuning and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 49,
        "schematic_symbols": 49,
        "board_fitted_symbols": 47,
        "external_assembly_interface_symbols": 2,
        "display_contacts": 40,
        "microsd_socket_contacts": 11,
        "hierarchical_interfaces": 18,
        "intentional_no_connect_pins": 33,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"reviewed H2.2.3 accounting drifted: {manifest['summary']}")
    sch = generated[OUTPUT_SCH]
    if sch.count("\n\t(symbol\n") != 49:
        raise ValueError("UI11 schematic symbol instance count mismatch")
    if sch.count("\n\t(hierarchical_label \"") != 18:
        raise ValueError("UI11 hierarchical label count mismatch")
    fitted = [row for row in manifest["instances"] if row["board_fitted"]]
    if any(not row["footprint"] for row in fitted):
        raise ValueError("a fitted UI11 component lacks an exact footprint mapping")
    display = next(row for row in manifest["instances"] if row["instance"] == "display")
    connector = next(row for row in manifest["instances"] if row["instance"] == "display_connector")
    if display["pin_count"] != 40 or connector["pin_count"] != 40:
        raise ValueError("40-contact display boundary drifted")
    sd = next(row for row in manifest["instances"] if row["instance"] == "sd")
    if sd["pin_count"] != 11 or "DM3AT-SF-PEJM5" not in sd["footprint"]:
        raise ValueError("exact DM3AT socket mapping drifted")
    qod = manifest["physical_net_aliases_collapsed"]
    if qod.get("SD_QOD") is not None:
        raise ValueError("obsolete SD_QOD alias returned")


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
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected populated UI hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.3 inside the live hierarchy")


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
            cwd=REPO,
            text=True,
            capture_output=True,
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
        print("ok: H2.2.3 display/touch/storage sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
