#!/usr/bin/env python3
"""Generate and verify the exact H2.3.4 main rails and domain-gates sheet."""

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
SHEET_ID = "RF_03_MAIN_RAILS_DOMAIN_GATES"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF03-main-rails-domain-gates.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
FOOTPRINT_DIR = ECAD / "libraries/Leshy2.pretty"
SYMBOL_NAMESPACE = "RF03"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    pins = []
    for contact, row in device["contacts"].items():
        number = passive.get(contact)
        if number is None:
            match = re.match(r"^(?:termination\s+)?(\d+)", str(row.get("physical", "")))
            if not match:
                raise ValueError(f"no physical contact number for {instance}.{contact}")
            number = match.group(1)
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical contact numbers in {instance}: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "ext_request_or": "Package_TO_SOT_SMD:SC-74A-5_1.55x2.9mm_P0.95mm",
        "ext_branch_gate": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "aon_buck": "Leshy2:TI-DRL0008A-SOT-5X3-8",
        "aon_inductor": "Inductor_SMD:L_Murata_LQH2MCNxxxx02_2.0x1.6mm",
        "aon_efuse": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
        "main_buck": "Package_TO_SOT_SMD:Texas_R-PDSO-N6_DRL-6",
        "main_inductor": "Inductor_SMD:L_Sunlord_MWSA0503S",
        "main_efuse": "Leshy2:TI-RPW0010A-VQFN-HR-10",
        "ext_buck": "Package_TO_SOT_SMD:Texas_R-PDSO-N6_DRL-6",
        "ext_inductor": "Inductor_SMD:L_Sunlord_MWSA0503S",
        "ext_pg_qualifier": "Package_TO_SOT_SMD:SOT-23",
        "ext_efuse": "Leshy2:TI-RPW0010A-VQFN-HR-10",
        "ext_evidence_buffer": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "tdk_b57332v5103f360":
        return "Resistor_SMD:R_0603_1608Metric"
    if device_key in {"murata_grm32er71e226ke15l"}:
        return "Capacitor_SMD:C_1210_3225Metric"
    if device_key in {"tdk_cga5l1x7r1e475k160ac", "murata_grm31cr71a226ke15l"}:
        return "Capacitor_SMD:C_1206_3216Metric"
    if device_key in {"murata_grm21br71e225ke11l"}:
        return "Capacitor_SMD:C_0805_2012Metric"
    if device_key.startswith(("tdk_c1005", "murata_grm155", "kemet_c0402")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith("murata_grm188"):
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("yageo_rc0402", "yageo_rt0402")):
        return "Resistor_SMD:R_0402_1005Metric"
    if device_key.startswith("yageo_rc0603"):
        return "Resistor_SMD:R_0603_1608Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if "inductor" in instance:
        return "L"
    if device_key == "tdk_b57332v5103f360":
        return "RT"
    if device_key.startswith(("tdk_c", "murata_grm", "kemet_c")):
        return "C"
    if device_key.startswith(("yageo_rc", "yageo_rt")):
        return "R"
    if device_key == "diodes_mmbt3904_7_f":
        return "Q"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")

    # TI MPCS002G DRL0008A package outline: 8 contacts, 0.5-mm pitch,
    # 1.1-1.3 x 1.5-1.7-mm body and 0.6-mm maximum height.  The H6 land-pattern
    # pass still owns paste segmentation and density-class selection.
    drl_pads = []
    for index in range(4):
        y = -0.75 + index * 0.50
        drl_pads.append((str(index + 1), -0.85, y, 0.60, 0.25, copper, "rect"))
        drl_pads.append((str(8 - index), 0.85, y, 0.60, 0.25, copper, "rect"))
    drl = custom_footprint(
        "TI-DRL0008A-SOT-5X3-8", drl_pads, 1.30, 1.70, 2.00, 2.10,
        "TI MPCS002G DRL0008A package-contact pattern: eight 0.5-mm-pitch contacts and 1.3x1.7-mm maximum body; final IPC density and paste rules close in H6",
    )

    # RPW0010A is a ten-contact 2x2-mm HotRod VQFN-HR with 0.45-mm pitch.
    # Every numbered copper contact is distinct here; H6 replaces this package
    # contact pattern with the final TI recommended-board-layout paste/copper
    # geometry before fabrication release.
    rpw_pads = []
    for number, x, y in (
        (1, -0.78, 0.68), (2, -0.78, 0.23), (3, -0.78, -0.23),
        (4, -0.78, -0.68), (5, -0.23, -0.78), (6, 0.23, -0.78),
        (7, 0.78, -0.68), (8, 0.78, -0.23), (9, 0.78, 0.23),
        (10, 0.78, 0.68),
    ):
        vertical = number not in {5, 6}
        rpw_pads.append((
            str(number), x, y,
            0.32 if vertical else 0.40,
            0.40 if vertical else 0.32,
            copper, "rect",
        ))
    rpw = custom_footprint(
        "TI-RPW0010A-VQFN-HR-10", rpw_pads, 2.10, 2.10, 2.50, 2.50,
        "TI 4225183/A RPW0010A package-contact pattern: ten distinct 0.45-mm-pitch HotRod contacts and 2.1x2.1-mm maximum body; final shaped power lands and paste close in H6",
    )
    return {
        FOOTPRINT_DIR / "TI-DRL0008A-SOT-5X3-8.kicad_mod": drl,
        FOOTPRINT_DIR / "TI-RPW0010A-VQFN-HR-10.kicad_mod": rpw,
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
    if len(rows) != 69:
        raise ValueError(f"{SHEET_ID} must own exactly 69 rows, got {len(rows)}")
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
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], spec["reference"].rstrip("0123456789") or "X",
            spec["footprint"], spec["role"], True, True, True, SYMBOL_NAMESPACE,
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
        '\t\t(title "Leshy2 — exact independent rails, eFuses and accessory gates")',
        '\t\t(rev "H2.3.4")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF03 does not terminate interfaces: {sorted(interfaces - hierarchy_used)}")

    deferred_fixture_endpoints = ["main_buck.PG"]
    deferred_fixture_labels = []
    for endpoint in deferred_fixture_endpoints:
        instance, contact = endpoint.split(".", 1)
        spec = next(row for row in specs if row["instance"] == instance)
        pin = next(row for row in spec["pins"] if row.contact == contact)
        net = endpoints[(instance, contact)]
        if net not in interfaces:
            deferred_fixture_labels.append({
                "endpoint": endpoint, "net": net,
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
        "schema_version": 1, "stage": "H2.3.4",
        "status": "reviewed_exact_main_rails_domain_gates_sheet",
        "project": PROJECT_ID, "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows), "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs),
            "hierarchical_interfaces": len(interfaces),
            "physical_package_contacts": sum(len(spec["pins"]) for spec in specs),
            "aon_buck_package_pins": len(next(spec for spec in specs if spec["instance"] == "aon_buck")["pins"]),
            "aon_efuse_package_pads": len(next(spec for spec in specs if spec["instance"] == "aon_efuse")["pins"]),
            "main_efuse_package_pads": len(next(spec for spec in specs if spec["instance"] == "main_efuse")["pins"]),
            "external_efuse_package_pads": len(next(spec for spec in specs if spec["instance"] == "ext_efuse")["pins"]),
            "independent_switchmode_domains": 3,
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "custom_package_contact_footprints": 2,
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
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "known_deferred_fixture_labels": deferred_fixture_labels,
        "review_boundary": {
            "complete": [
                "all 69 RF03 ledger instances and all 186 physical package contacts are explicit",
                "AON, main and accessory converters have independent inductors, feedback, bypass and post-protection",
                "AON eFuse exposed pad is explicit and both HotRod eFuses expose all ten real package contacts",
                "TPS259470 AUXOFF is correctly treated as an unused open-drain output rather than a fast-off input",
                "main PG and all qualified accessory current, thermal and voltage faults share one POWER_FAULT_N aggregate",
                "all twenty-one hierarchy interfaces and three intentional no-connect contacts are explicit",
            ],
            "deferred": [
                "the single raw main-converter PG diagnostic pad is instantiated by RF60",
                "final DRL/RPW copper density, shaped HotRod lands, paste segmentation and DRC close in H6",
                "rail efficiency, transient response, current-limit tolerance, thermal trip and source handover close in H3/H8",
                "exact converter startup order and fault messages close in firmware/virtual/HIL phases",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    expected = {
        "ledger_instances": 69, "schematic_symbols": 69,
        "board_fitted_symbols": 69, "hierarchical_interfaces": 21,
        "physical_package_contacts": 186, "aon_buck_package_pins": 8,
        "aon_efuse_package_pads": 7, "main_efuse_package_pads": 10,
        "external_efuse_package_pads": 10, "independent_switchmode_domains": 3,
        "intentional_no_connect_pins": 3, "custom_package_contact_footprints": 2,
        "pcb_files_created": 0,
    }
    if manifest["summary"] != expected:
        raise ValueError(f"H2.3.4 accounting drifted: {manifest['summary']}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 69:
        raise ValueError("RF03 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 21:
        raise ValueError("RF03 hierarchy accounting mismatch")
    expected_nc = {"aon_buck.FB_VSET", "ext_efuse.AUXOFF", "ext_evidence_buffer.NC"}
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF03 no-connect set drifted: {manifest['intentional_no_connect_endpoints']}")
    if manifest["known_deferred_fixture_labels"]:
        raise ValueError("RF03 deferred fixture-boundary set drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted RF03 component lacks footprint: {row['instance']}")


def kicad_check() -> None:
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF03 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.4 and the live RF/power hierarchy")


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
        print("ok: H2.3.4 main rails and domain gates sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
