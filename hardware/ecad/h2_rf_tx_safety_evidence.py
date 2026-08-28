#!/usr/bin/env python3
"""Generate and verify the exact H2.3.12 RF-side TX safety/evidence sheet."""

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
    FOOTPRINT_DIR, Pin, custom_footprint, effects, escaped, library_symbol,
    schematic_symbol, stable_uuid,
)


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = ECAD / "generated/H2-instance-ledger.json"
ROOT_INTERFACE_PATH = ECAD / "generated/H2-RF-root-interface.json"
SHEET_ID = "RF_50_TX_SAFETY_EVIDENCE"
PROJECT_ID = "LESHY2-RF"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-RF50-tx-safety-evidence.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "RF50"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(instance: str, device: dict) -> list[Pin]:
    overrides = {
        "det_nrf0": {"EPAD": "9"},
        "det_nrf1": {"EPAD": "9"},
        "det_nrf2": {"EPAD": "9"},
        "det_cc": {"EPAD": "9"},
        "det_voice": {"EPAD": "9"},
        "det_voice_v": {"EPAD": "9"},
    }
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = overrides.get(instance, {}).get(contact) or passive.get(contact)
        if number is None:
            match = re.search(r"(?:^|\s)(\d+)(?:\s|$)", physical)
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
        "power_command_switch": "Leshy2:JS102011SCQN",
        "safe_supervisor": "Package_TO_SOT_SMD:SOT-23-6",
        "safety_controller": "Package_SO:Texas_DGS0020A_TSSOP-20_3x5.1mm_P0.5mm",
        "safety_fault_request_iso": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safety_s3_reset_iso": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safety_watchdog": "Package_TO_SOT_SMD:Texas_DDF0008A_SOT-8_1.6x2.9mm_P0.65mm",
        "safe_run_fault_iso": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safe_conditioner": "Package_TO_SOT_SMD:SC-74-6_1.55x2.9mm_P0.95mm",
        "safe_rearm_buffer": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safe_latch": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "safe_reset_buffer": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "safe_fault_reset_buffer": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "safe_reset_sink_b": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "safe_gate_a": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "safe_gate_b": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "safe_ptt_or": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "det_nrf0": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "det_nrf1": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "det_nrf2": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "det_cc": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "det_voice": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "det_voice_v": "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm",
        "evidence_cmp_b": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "evidence_cmp_voice": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "evidence_cmp_voice_v": "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        "evidence_mask": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
        "evidence_main_isolator": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "safety_control_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
    }
    if instance in exact:
        return exact[instance]
    if device_key in {"diodes_bat54_7_f", "onsemi_bat54alt1g"}:
        return "Package_TO_SOT_SMD:SOT-23"
    if device_key.startswith(("tdk_c1608", "murata_grm188")):
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith("murata_grm21"):
        return "Capacitor_SMD:C_0805_2012Metric"
    if device_key.startswith(("tdk_c1005", "yageo_cc0402", "murata_grm155")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc0402", "uniroyal_0402wgf")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "power_command_switch":
        return "SW"
    if device_key.startswith(("tdk_c", "yageo_cc", "murata_grm")):
        return "C"
    if device_key.startswith(("yageo_rc", "uniroyal_0402wgf")):
        return "R"
    if device_key in {"diodes_bat54_7_f", "onsemi_bat54alt1g", "ti_tpd4e05u06_dqar"}:
        return "D"
    if device_key == "diodes_2n7002dw_7_f":
        return "Q"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    switch = custom_footprint(
        "JS102011SCQN",
        [
            ("1", -2.50, 2.35, 0.80, 3.20, copper),
            ("2", 0.00, 2.35, 0.80, 3.20, copper),
            ("3", 2.50, 2.35, 0.80, 3.20, copper),
        ],
        8.50, 3.50, 9.00, 6.70,
        "Littelfuse C&K JS Series VL 01/14/26 page 5: exact JS102011SCQN 8.5x3.5-mm vertical-gullwing SPDT body, 2.5-mm contact pitch and three 0.8x3.2-mm recommended lands; pin 2 is common",
        courtyard_y=1.35,
    )
    return {FOOTPRINT_DIR / "JS102011SCQN.kicad_mod": switch}


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 113:
        raise ValueError(f"{SHEET_ID} must own exactly 113 rows, got {len(rows)}")
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
    column_x = [45.72 + 68.58 * index for index in range(9)]
    cursor_y = [38.10] * len(column_x)
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
        cursor_y[column] = y + height / 2 + 12.70
        placements[spec["instance"]] = (x, y, coords)

    lines = [
        "(kicad_sch", "\t(version 20250114)", '\t(generator "eeschema")',
        '\t(generator_version "10.0")', f'\t(uuid "{stable_uuid(f"sheet:{SHEET_ID}")}")',
        '\t(paper "A0")', "\t(title_block",
        '\t\t(title "Leshy2 — exact RF-side TX interlock and physical evidence")',
        '\t\t(rev "H2.3.12")', "\t)", "\t(lib_symbols", *library_defs, "\t)",
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
        raise ValueError(f"RF50 does not terminate hierarchy interfaces: {sorted(interfaces - hierarchy_used)}")
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
        "stage": "H2.3.12",
        "status": "reviewed_exact_rf_tx_safety_evidence_sheet",
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
            "rf_detector_channels": 6, "comparator_channels": 6,
            "independent_watchdogs": 2, "tx_gate_packages": 3,
            "evidence_mask_inputs": 9, "custom_footprints": len(footprint_outputs()),
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
        "known_deferred_fixture_labels": [
            {"endpoint": instance + "." + contact, "net": net,
             "label_uuid": stable_uuid(f"label:{instance}:{pin}:{net}")}
            for instance, contact, pin, net in (
                ("evidence_mask", "INT_N", "1", "EVIDENCE_MASK_INT_N_TP"),
                ("safety_controller", "PA17", "13", "SAFETY_SERVICE_UART_TX"),
                ("safety_controller", "PA18", "14", "SAFETY_SERVICE_UART_RX"),
                ("safety_controller", "PA19_SWDIO", "15", "SAFETY_SWDIO"),
                ("safety_controller", "PA20_SWCLK", "16", "SAFETY_SWCLK"),
            )
            if net not in interfaces
        ],
        "footprint_evidence": [
            {"mpn": devices[key]["mpn"], "footprint": footprint,
             "source": devices[key]["source"], "status": status}
            for key, footprint, status in (
                ("ck_js102011scqn", "Leshy2:JS102011SCQN", "exact manufacturer body, lead pitch and recommended SMT lands"),
                ("adi_ad8314acpz_rl7", "Package_CSP:LFCSP-8-1EP_3x2mm_P0.5mm_EP1.6x1.65mm", "exact Analog Devices CP-8-23 3x2-mm LFCSP class, including pad 9"),
                ("ti_mspm0c1106_sdgs20r", "Package_SO:Texas_DGS0020A_TSSOP-20_3x5.1mm_P0.5mm", "exact TI DGS20 package"),
                ("ti_tps3435cakagddfr", "Package_TO_SOT_SMD:Texas_DDF0008A_SOT-8_1.6x2.9mm_P0.65mm", "exact TI DDF8 package"),
                ("ti_tca9535_pwr", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "exact TI PW24 package"),
                ("ti_sn74lvc1g74_dcur", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", "exact TI DCU8 package"),
            )
        ],
        "corrections_closed": [
            "AD8314ACPZ-RL7 uses the real 3x2-mm CP-8-23 footprint and explicit exposed pad 9 rather than a fictitious 3x3-mm package",
            "RUN/KILL is one maintained low-current SPDT command switch; it never carries pack, charge or load current",
            "six forward-power samples create independent physical RF evidence for all three nRF24 paths, CC1101, UHF voice and VHF voice TX",
            "TX request gates and physical evidence remain separate so firmware cannot claim transmission solely from a command bit",
            "the always-on MSPM0, TPS3435 watchdog, POR supervisor and asynchronous latch retain kill authority when application processors stall",
            "every safety logic package now has explicit supply/return contacts and local bypass; the latch D input has a physical 10-kOhm fail-low resistor",
        ],
        "review_boundary": {
            "complete": [
                "all 113 RF50 ledger instances have exact MPN, contacts, footprint and circuit nets",
                "all RF50 hierarchy interfaces terminate on physical component contacts",
                "RUN/KILL, POR, watchdog, fault latch, reset sinks and TX request gates are explicit",
                "six RF detector channels, six comparator channels, evidence mask and any-TX diode OR are explicit; UHF/VHF comparators share the reviewed EV_N6 voice identity",
                "native KiCad parses the live hierarchy and controlled switch footprint",
            ],
            "deferred": [
                "forward-sample loss, threshold, hysteresis and hold-time calibration HIL",
                "watchdog timeout, thermal trip, kill/re-arm, brownout and stuck-processor fault-injection HIL",
                "evidence-mask boot defaults, I2C failure behavior and external-module evidence HIL",
                "PCB placement, RF/analog return geometry, thermal coupling and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    expected = {
        "ledger_instances": 113, "schematic_symbols": 113,
        "board_fitted_symbols": 113, "hierarchical_interfaces": 78,
        "physical_contacts": 421, "rf_detector_channels": 6,
        "comparator_channels": 6, "independent_watchdogs": 2,
        "tx_gate_packages": 3, "evidence_mask_inputs": 9,
        "custom_footprints": 1, "intentional_no_connect_pins": 24,
        "pcb_files_created": 0,
    }
    if summary != expected:
        raise ValueError(f"H2.3.12 accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 113:
        raise ValueError("RF50 symbol accounting mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 78:
        raise ValueError("RF50 hierarchy interface accounting mismatch")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted RF50 component lacks footprint: {row['instance']}")
    expected_nc = {
        "cc_evidence_hold_diode.NC", "voice_evidence_hold_diode.NC",
        "voice_v_evidence_hold_diode.NC",
        "det_nrf0.V_DN", "det_nrf1.V_DN", "det_nrf2.V_DN",
        "det_cc.V_DN", "det_voice.V_DN", "det_voice_v.V_DN", "evidence_or_4.K2",
        "safe_rearm_buffer.NC",
        "safe_reset_buffer.NC", "safe_reset_sink_b.D2",
        "safe_run_fault_iso.NC", "safe_supervisor.CT",
        "safety_fault_request_iso.NC", "safety_s3_reset_iso.NC",
        "safety_control_esd.D1_MINUS", "safety_control_esd.D2_PLUS",
        "safety_control_esd.D2_MINUS", "safety_control_esd.NC_6",
        "safety_control_esd.NC_7", "safety_control_esd.NC_9",
        "safety_control_esd.NC_10",
    }
    if set(manifest["intentional_no_connect_endpoints"]) != expected_nc:
        raise ValueError(f"RF50 no-connect accounting drifted: {manifest['intentional_no_connect_endpoints']}")
    forbidden_nc_suffixes = (".VCC", ".VDD", ".GND", ".VSS", ".EPAD", ".PA19_SWDIO", ".PA20_SWCLK")
    if any(row.endswith(forbidden_nc_suffixes) for row in manifest["intentional_no_connect_endpoints"]):
        raise ValueError("RF50 left a power, exposed-pad or safety-debug contact unconnected")
    if manifest["known_deferred_fixture_labels"]:
        raise ValueError("RF50 safety-controller fixture boundary accounting drifted")
    switch = generated[FOOTPRINT_DIR / "JS102011SCQN.kicad_mod"]
    for number, x in (("1", "-2.500"), ("2", "0.000"), ("3", "2.500")):
        token = f'(pad "{number}" smd roundrect (at {x} 2.350) (size 0.800 3.200)'
        if token not in switch:
            raise ValueError("JS102011SCQN exact three-land footprint drifted")
    detector_rows = [row for row in manifest["instances"] if row["instance"].startswith("det_")]
    if len(detector_rows) != 6 or any(row["pin_count"] != 9 for row in detector_rows):
        raise ValueError("AD8314 detector package/pad-9 accounting drifted")


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
    with tempfile.TemporaryDirectory(prefix="leshy2-h2-rf50-") as temp:
        result = subprocess.run(
            [cli, "fp", "upgrade", "--force", "--output", str(Path(temp) / "Leshy2.pretty"), str(FOOTPRINT_DIR)],
            text=True, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(f"KiCad rejected controlled footprints:\n{result.stdout}{result.stderr}")
    result = subprocess.run(
        ["python3", str(ECAD / "h2_rf_root.py"), "--check", "--kicad-check"],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected RF50 hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.3.12 and all controlled footprints")


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
            raise RuntimeError(f"failed to refresh RF hierarchy:\n{root.stdout}{root.stderr}")
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
        print("ok: H2.3.12 RF-side TX safety/evidence sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
