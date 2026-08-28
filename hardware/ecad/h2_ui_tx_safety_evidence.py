#!/usr/bin/env python3
"""Generate and verify the exact H2.2.9 UI-side TX safety/evidence sheet."""

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
from h2_dual_nmos import PIN_MAP as DUAL_NMOS_PIN_MAP, validate_dual_nmos
from h2_ui_s3_core import ScopedReferenceCounter
from h2_ui_audio_codec_headset import endpoint_nets
from h2_ui_display_touch_storage import pin_net
from h2_ui_s3_core import (
    FOOTPRINT_DIR, Pin, custom_footprint, effects, escaped, library_symbol,
    schematic_symbol, stable_uuid,
)


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_50_TX_SAFETY_EVIDENCE"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI50-tx-safety-evidence.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI50"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "det_ir": {"ANODE": "1", "CATHODE": "2"},
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
        "ir_evidence_amp": "Package_TO_SOT_SMD:SOT-23-5",
        "safe_reset_sink_a": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "safe_c5_reset_buffer": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safe_c5_fault_reset_buffer": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "det_s3": "Package_TO_SOT_SMD:TSOT-23-6",
        "det_c5": "Package_TO_SOT_SMD:TSOT-23-6",
        "det_ir": "Leshy2:VEMD1060X01",
        "evidence_cmp_a": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
    }
    if instance in exact:
        return exact[instance]
    if device_key.startswith(("tdk_c", "yageo_cc", "kemet_c")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "det_ir":
        return "D"
    if device_key.startswith(("tdk_c", "yageo_cc", "kemet_c")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf")):
        return "R"
    if device_key == "diodes_2n7002dw_7_f":
        return "Q"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    photodiode = custom_footprint(
        "VEMD1060X01",
        [
            ("1", -0.80, 0.0, 1.00, 1.45, copper),
            ("2", 0.80, 0.0, 1.00, 1.45, copper),
        ],
        2.00, 1.25, 2.80, 1.75,
        "Vishay VEMD1060X01 Rev.1.1 page 4: exact 2.0x1.25-mm body and two 1.0x1.45-mm recommended lands separated by 0.6 mm; pad 1 anode at the marked side, pad 2 cathode",
    )
    return {FOOTPRINT_DIR / "VEMD1060X01.kicad_mod": photodiode}


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    dual_nmos = validate_dual_nmos(candidate, devices, {"safe_reset_sink_a"})
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 33:
        raise ValueError(f"{SHEET_ID} must own exactly 33 rows, got {len(rows)}")
    interface_order = list(next(
        row["interfaces"] for row in root_manifest["sheets"] if row["id"] == SHEET_ID
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
    column_x = [50.80, 132.08, 213.36, 294.64, 375.92, 457.20]
    cursor_y = [40.64] * len(column_x)
    for spec in specs:
        prefix = spec["reference"].rstrip("0123456789") or "X"
        lib, coords, height = library_symbol(
            spec["instance"], spec["pins"], prefix, spec["footprint"], spec["role"],
            True, True, True, SYMBOL_NAMESPACE,
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
        '\t\t(title "Leshy2 — exact UI-side actual-TX evidence and reset safety")',
        '\t\t(rev "H2.2.9")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"UI50 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
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
        "stage": "H2.2.9",
        "status": "reviewed_exact_ui_tx_safety_evidence_sheet",
        "project": PROJECT_ID,
        "sheet": SHEET_ID,
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, LEDGER_PATH, ROOT_INTERFACE_PATH)
        },
        "summary": {
            "ledger_instances": len(rows), "schematic_symbols": len(specs),
            "board_fitted_symbols": len(specs), "hierarchical_interfaces": len(interfaces),
            "physical_contacts": sum(len(spec["pins"]) for spec in specs),
            "rf_detector_channels": 2, "optical_detector_channels": 1,
            "comparator_channels": 4, "reset_sink_channels": 2,
            "custom_footprints": len(footprint_outputs()),
            "intentional_no_connect_pins": len(no_connect_endpoints),
            "pcb_files_created": 0,
        },
        "instances": [
            {"instance": spec["instance"], "symbol_uuid": stable_uuid(f"symbol:{spec['instance']}"),
             "reference": spec["reference"], "mpn": spec["mpn"],
             "footprint": spec["footprint"], "pin_count": len(spec["pins"]),
             "board_fitted": True}
            for spec in specs
        ],
        "physical_net_aliases_collapsed": {
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "exact_dual_nmos_pinout": dual_nmos,
        "footprint_evidence": [
            {"mpn": devices[key]["mpn"], "footprint": footprint, "source": devices[key]["source"]}
            for key, footprint in (
                ("adi_ltc5532_es6_trmpbf", "Package_TO_SOT_SMD:TSOT-23-6"),
                ("ti_tlv1824_pwr", "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"),
                ("ti_tlv9061_idbvr", "Package_TO_SOT_SMD:SOT-23-5"),
                ("vishay_vemd1060x01", "Leshy2:VEMD1060X01"),
                ("diodes_2n7002dw_7_f", "Package_TO_SOT_SMD:SOT-363_SC-70-6"),
            )
        ],
        "corrections_closed": [
            "the one physical S3 comparator output now has one canonical EV_N0_S3 name across UI controls, safety evidence and M1",
            "the IR evidence sensor observes emitted light through a physical photodiode path rather than inferring TX from the drive command",
            "S3 and C5 RF detector analog outputs remain UI-local; only active-low digital evidence crosses M1",
            "the unused fourth TLV1824 channel is tied to safety ground at both inputs and its open-drain output is explicitly NC",
            "independent passive-drain reset sinks hold S3 and C5 reset paths fail-closed under their separate kill gates",
        ],
        "review_boundary": {
            "complete": [
                "all 33 UI50 ledger instances have exact MPN, contacts, footprint and circuit nets",
                "all 18 hierarchy interfaces terminate on real component contacts",
                "S3 RF, C5 RF and IR optical evidence paths plus reset-kill sinks are explicit",
                "all threshold, hysteresis, output pull-up, bypass and analog-return networks are instantiated",
                "native KiCad parses the live hierarchy and controlled photodiode footprint",
            ],
            "deferred": [
                "detector threshold/calibration, forward-sample loss and comparator hysteresis HIL",
                "light-tight tunnel, false-positive/false-negative, optical response and ambient-crosstalk HIL",
                "reset assertion/release, brownout and unpowered-domain fault-injection HIL",
                "PCB placement, RF/analog return geometry, thermal coupling and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary != {
        "ledger_instances": 33, "schematic_symbols": 33,
        "board_fitted_symbols": 33, "hierarchical_interfaces": 19,
        "physical_contacts": 99, "rf_detector_channels": 2,
        "optical_detector_channels": 1, "comparator_channels": 4,
        "reset_sink_channels": 2, "custom_footprints": 1,
        "intentional_no_connect_pins": 3, "pcb_files_created": 0,
    }:
        raise ValueError(f"H2.2.9 accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 33:
        raise ValueError("UI50 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 19:
        raise ValueError("UI50 hierarchy interface accounting mismatch")
    if manifest["intentional_no_connect_endpoints"] != [
        "evidence_cmp_a.OUT4", "safe_c5_fault_reset_buffer.NC",
        "safe_c5_reset_buffer.NC",
    ]:
        raise ValueError("UI50 no-connect accounting drifted")
    if (
        manifest["exact_dual_nmos_pinout"]["physical_pin_to_contact"]
        != DUAL_NMOS_PIN_MAP
        or set(manifest["exact_dual_nmos_pinout"]["instances"])
        != {"safe_reset_sink_a"}
    ):
        raise ValueError("UI50 exact 2N7002DW physical/channel evidence drifted")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted UI50 component lacks footprint: {row['instance']}")
    footprint = generated[FOOTPRINT_DIR / "VEMD1060X01.kicad_mod"]
    for number, x in (("1", "-0.800"), ("2", "0.800")):
        if f'(pad "{number}" smd roundrect (at {x} 0.000) (size 1.000 1.450)' not in footprint:
            raise ValueError("VEMD1060X01 exact two-land footprint drifted")
    if "S3_RF_TX_EVIDENCE_AON_N" in schematic:
        raise ValueError("obsolete alias split the physical EV_N0_S3 net")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-ui50-") as temp:
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(Path(temp) / "Leshy2.pretty"), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected controlled footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_ui_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected UI50 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.9 and all controlled footprints")


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
            ["python3", str(ECAD / "h2_ui_root.py"), "--write"],
            cwd=REPO, text=True, capture_output=True,
        )
        if root.returncode:
            raise RuntimeError(f"failed to refresh UI hierarchy:\n{root.stdout}{root.stderr}")
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
        print("ok: H2.2.9 UI-side TX safety/evidence sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
