#!/usr/bin/env python3
"""Generate and verify the exact H2.2.5 codec and CTIA-headset sheet."""

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
from h2_ui_display_touch_storage import abstract_canonical, pin_net
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
ROOT_INTERFACE_PATH = ECAD / "generated/H2-UI-root-interface.json"
SHEET_ID = "UI_13_AUDIO_CODEC_HEADSET"
PROJECT_ID = "LESHY2-UI"
PROJECT_DIR = ECAD / f"kicad/{PROJECT_ID}"
OUTPUT_SCH = PROJECT_DIR / f"{SHEET_ID}.kicad_sch"
OUTPUT_MANIFEST = ECAD / "generated/H2-UI13-audio-codec-headset.json"
SYMBOL_LIBRARY = ECAD / "libraries/leshy2.kicad_sym"
SYMBOL_NAMESPACE = "UI13"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins_for(device: dict) -> list[Pin]:
    passive = {"END_1": "1", "END_2": "2"}
    pins: list[Pin] = []
    for contact, row in device["contacts"].items():
        physical = str(row.get("physical", ""))
        number = passive.get(contact)
        if number is None:
            numeric = re.match(r"^(\d+)", physical)
            number = numeric.group(1) if numeric else contact
        pins.append(Pin(number, contact, contact))
    numbers = [pin.number for pin in pins]
    if len(numbers) != len(set(numbers)):
        raise ValueError(f"duplicate physical pin numbers: {numbers}")
    return pins


def footprint_for(instance: str, device_key: str) -> str:
    exact = {
        "codec": "Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm",
        "audio_rx_mux": "Package_TO_SOT_SMD:SOT-23-6",
        "audio_capture_selector": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "audio_capture_buffer": "Package_TO_SOT_SMD:SOT-23-5",
        "audio_speaker_selector": "Package_SO:TSSOP-10_3x3mm_P0.5mm",
        "audio_tx_selector": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "audio_safe_gate": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "headphone_jack": "Leshy2:SJ-43504-SMT-TR",
        "headset_mic_selector": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
        "headset_control_io": "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
        "headphone_esd": "Package_SON:USON-10_2.5x1.0mm_P0.5mm",
        "codec_supervisor": "Package_TO_SOT_SMD:SOT-23",
        "codec_i2c_iso": "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
        "codec_i2s_bclk_iso": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "codec_i2s_ws_iso": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "codec_i2s_dout_iso": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "codec_i2s_din_iso": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "codec_i2s_din_boot_gate": "Package_TO_SOT_SMD:Texas_R-PDSO-G5_DCK-5",
        "codec_power_switch": "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    }
    if instance in exact:
        return exact[instance]
    if device_key == "murata_blm18pg181sn1d":
        return "Inductor_SMD:L_0603_1608Metric"
    if device_key == "murata_grm21br60j226me39l":
        return "Capacitor_SMD:C_0805_2012Metric"
    if device_key in {"murata_grm188r60j106me47d", "tdk_c1608x7r1c105k080ac"}:
        return "Capacitor_SMD:C_0603_1608Metric"
    if device_key.startswith(("tdk_c", "murata_grm")):
        return "Capacitor_SMD:C_0402_1005Metric"
    if device_key.startswith(("yageo_rc", "panasonic_erj_2r", "vishay_crcw")):
        return "Resistor_SMD:R_0402_1005Metric"
    raise ValueError(f"no exact footprint mapping for {instance}/{device_key}")


def reference_prefix(instance: str, device_key: str) -> str:
    if instance == "headphone_jack":
        return "J"
    if device_key == "ti_tpd4e05u06_dqar":
        return "D"
    if device_key == "murata_blm18pg181sn1d":
        return "FB"
    if device_key.startswith(("tdk_c", "murata_grm")):
        return "C"
    if device_key.startswith(("yageo_rc", "panasonic_erj_2r", "vishay_crcw")):
        return "R"
    return "U"


def footprint_outputs() -> dict[Path, str]:
    copper = ("F.Cu", "F.Paste", "F.Mask")
    # Same Sky drawing page 2, top view: every terminal uses one 1.7 x
    # 1.5-mm land.  The body reference and pad centres are transcribed in the
    # same top-view orientation, with the receptacle opening towards -Y.
    jack = custom_footprint(
        "SJ-43504-SMT-TR",
        [
            ("1", 4.25, -3.00, 1.70, 1.50, copper, "rect"),
            ("2", -4.25, 3.55, 1.70, 1.50, copper, "rect"),
            ("3", 4.25, -0.25, 1.70, 1.50, copper, "rect"),
            ("4", -4.25, -3.00, 1.70, 1.50, copper, "rect"),
            ("5", -4.25, 4.80, 1.70, 1.50, copper, "rect"),
            ("6", 4.25, 4.80, 1.70, 1.50, copper, "rect"),
        ],
        6.80,
        11.50,
        10.60,
        12.00,
        "Same Sky SJ-43504-SMT-TR Rev.1.06 page 2: exact six 1.7x1.5-mm lands, 6.80x11.50-mm top-view body reference and numbered CTIA/switch contact orientation",
    )
    return {FOOTPRINT_DIR / "SJ-43504-SMT-TR.kicad_mod": jack}


def endpoint_nets(
    candidate: dict, local_instances: set[str], interface_order: list[str]
) -> tuple[dict[tuple[str, str], str], dict[str, str], set[str]]:
    """Collapse physical aliases while preserving the first reviewed net name.

    The paper route graph may give one physical contact several descriptive
    segment names. KiCad requires one electrical name, so contacts form a
    union graph. A cross-sheet interface wins; otherwise route order wins.
    """

    aliases: dict[str, str] = {}
    no_connect_nets: set[str] = set()
    endpoint_labels: dict[tuple[str, str], list[str]] = defaultdict(list)
    order: dict[str, int] = {}

    def add(endpoint: str, net: str) -> None:
        if endpoint.startswith("abstract:") or "." not in endpoint:
            return
        instance, contact = endpoint.split(".", 1)
        if instance not in local_instances:
            return
        key = (instance, contact)
        if net not in endpoint_labels[key]:
            endpoint_labels[key].append(net)
        order.setdefault(net, len(order))

    for route in candidate["fixed_routes"]:
        route_instances = {
            endpoint.split(".", 1)[0]
            for endpoint in (route["from"], route["to"])
            if "." in endpoint and not endpoint.startswith("abstract:")
        }
        if not route_instances.intersection(local_instances):
            continue
        canonical = abstract_canonical(route["from"]) or abstract_canonical(route["to"])
        net = canonical or route["net"]
        if canonical:
            aliases[route["net"]] = canonical
        if any(endpoint.startswith("abstract:no-connect") for endpoint in (route["from"], route["to"])):
            no_connect_nets.add(net)
        add(route["from"], net)
        add(route["to"], net)
    for allocation in candidate["allocations"]:
        endpoints = [
            f"{allocation['instance']}.{allocation['contact']}",
            *allocation.get("peers", []),
        ]
        if not any(
            "." in endpoint and endpoint.split(".", 1)[0] in local_instances
            for endpoint in endpoints
        ):
            continue
        net = aliases.get(allocation["net"], allocation["net"])
        for endpoint in endpoints:
            add(endpoint, net)

    parent: dict[str, str] = {}

    def find(item: str) -> str:
        parent.setdefault(item, item)
        if parent[item] != item:
            parent[item] = find(parent[item])
        return parent[item]

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for labels in endpoint_labels.values():
        for label in labels:
            find(label)
        for label in labels[1:]:
            union(labels[0], label)
    groups: dict[str, set[str]] = defaultdict(set)
    for label in parent:
        groups[find(label)].add(label)
    interface_rank = {net: index for index, net in enumerate(interface_order)}
    canonical_by_label: dict[str, str] = {}
    for labels in groups.values():
        public = [label for label in labels if label in interface_rank]
        canonical = (
            min(public, key=interface_rank.get)
            if public
            else min(labels, key=order.get)
        )
        for label in labels:
            canonical_by_label[label] = canonical
            if label != canonical:
                aliases[label] = canonical
    result = {
        endpoint: canonical_by_label[labels[0]]
        for endpoint, labels in endpoint_labels.items()
    }
    return result, aliases, no_connect_nets


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    root_manifest = json.loads(ROOT_INTERFACE_PATH.read_text(encoding="utf-8"))
    rows = [
        row for row in ledger["rows"]
        if row["project"] == PROJECT_ID and row["sheet"] == SHEET_ID
    ]
    if len(rows) != 104:
        raise ValueError(f"{SHEET_ID} must own exactly 104 ledger rows, got {len(rows)}")
    interface_row = next(row for row in root_manifest["sheets"] if row["id"] == SHEET_ID)
    interface_order = list(interface_row["interfaces"])
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
            "pins": pins_for(devices[row["device_key"]]),
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
        '\t\t(title "Leshy2 — exact codec, capture, playback and CTIA headset")',
        '\t\t(rev "H2.2.5")',
        "\t)",
        "\t(lib_symbols",
        *library_defs,
        "\t)",
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
                    f'\t\t(uuid "{stable_uuid(f"nc:{instance}:{pin.number}")}")',
                    "\t)",
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
                f'\t({token} "{escaped(net)}"{shape}',
                f"\t\t(at {x:.2f} {y:.2f} {angle})",
                f"\t\t{effects(justify)}",
                f'\t\t(uuid "{stable_uuid(f"label:{instance}:{pin.number}:{net}")}")',
                "\t)",
            ]
    if hierarchy_used != interfaces:
        raise ValueError(
            f"UI13 circuit does not terminate every hierarchy interface: "
            f"missing {sorted(interfaces - hierarchy_used)}"
        )
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
        "stage": "H2.2.5",
        "status": "reviewed_exact_audio_codec_headset_sheet",
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
            "codec_contacts": len(devices["everest_es8311_qfn20"]["contacts"]),
            "headset_contacts": len(devices["same_sky_sj_43504_smt_tr"]["contacts"]),
            "analog_selectors": sum(
                spec["device_key"] in {
                    "ti_sn74lvc1g3157_dbvr", "ti_ts5a63157_dckr", "ti_tmux1136_dgsr"
                }
                for spec in specs
            ),
            "io_isolators_and_boot_gate": sum(
                spec["device_key"] in {
                    "ti_sn74lvc2g66_dcur", "ti_sn74lvc1g126_dckr", "ti_sn74lvc1g08_dckr"
                }
                for spec in specs
            ),
            "custom_footprints": len(footprint_outputs()),
            "intentional_no_connect_pins": len(no_connect_endpoints),
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
            alias: canonical for alias, canonical in sorted(aliases.items()) if alias != canonical
        },
        "intentional_no_connect_endpoints": sorted(no_connect_endpoints),
        "footprint_evidence": [
            {
                "mpn": devices[key]["mpn"],
                "footprint": footprint,
                "source": devices[key]["source"],
            }
            for key, footprint in (
                ("everest_es8311_qfn20", "Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm"),
                ("same_sky_sj_43504_smt_tr", "Leshy2:SJ-43504-SMT-TR"),
                ("ti_tmux1136_dgsr", "Package_SO:TSSOP-10_3x3mm_P0.5mm"),
                ("ti_tpd4e05u06_dqar", "Package_SON:USON-10_2.5x1.0mm_P0.5mm"),
            )
        ],
        "corrections_closed": [
            "all descriptive segment names sharing one physical audio contact collapse to one deterministic KiCad net and remain auditable as aliases",
            "codec QFN contact 21, analog/digital grounds and the single local AUDIO_GROUND star link are explicit",
            "the CTIA jack has six separately numbered contacts; insertion detect never doubles as microphone selection",
            "CODEC_READY and reset-low AUDIO_ARM jointly isolate the GPIO0 capture-data path during boot",
            "speaker and voice-TX selectors default to receive bypass and direct electret audio until explicitly armed",
        ],
        "review_boundary": {
            "complete": [
                "every UI13 ledger instance is placed once with exact MPN, contact map and footprint",
                "all 24 hierarchy interfaces terminate on real circuit pins",
                "capture, playback, headset, power, reset and no-backfeed paths are electrically explicit",
                "native KiCad parses the populated UI hierarchy with only machine-accounted findings",
            ],
            "deferred": [
                "received-jack footprint/cutout measurement and CTIA/TRS insertion HIL",
                "codec address, clock mode, gain, noise, distortion, headphone load and pop/click HIL",
                "selector reset/watchdog/brownout, ESD and RF-immunity fault injection",
                "PCB placement, split-return geometry and DRC in H6",
            ],
        },
    }
    generated[OUTPUT_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return generated, manifest


def structural_check(generated: dict[Path, str], manifest: dict) -> None:
    summary = manifest["summary"]
    if summary["ledger_instances"] != 104 or summary["schematic_symbols"] != 104:
        raise ValueError(f"reviewed H2.2.5 instance accounting drifted: {summary}")
    if summary["hierarchical_interfaces"] != 24 or summary["codec_contacts"] != 21:
        raise ValueError(f"reviewed H2.2.5 interface/contact accounting drifted: {summary}")
    if summary["headset_contacts"] != 6 or summary["analog_selectors"] != 5:
        raise ValueError(f"reviewed H2.2.5 audio endpoint accounting drifted: {summary}")
    if summary["io_isolators_and_boot_gate"] != 6 or summary["custom_footprints"] != 1:
        raise ValueError(f"reviewed H2.2.5 isolation/footprint accounting drifted: {summary}")
    schematic = generated[OUTPUT_SCH]
    if schematic.count("\n\t(symbol\n") != 104:
        raise ValueError("UI13 schematic symbol instance count mismatch")
    if schematic.count("\n\t(hierarchical_label \"") != 24:
        raise ValueError("UI13 hierarchy-interface count mismatch")
    for row in manifest["instances"]:
        if not row["footprint"]:
            raise ValueError(f"fitted UI13 component lacks footprint: {row['instance']}")
    jack = generated[FOOTPRINT_DIR / "SJ-43504-SMT-TR.kicad_mod"]
    if jack.count('\n\t(pad "') != 6 or any(
        f'(pad "{number}"' not in jack for number in range(1, 7)
    ):
        raise ValueError("SJ-43504-SMT-TR six-contact footprint drifted")
    required_aliases = {
        "CODEC_CAPTURE_VMID": "CODEC_CAPTURE_BUFFER_IN",
        "CODEC_CAPTURE_BUFFER_OUT": "CODEC_CAPTURE_BUFFER_FB",
        "CODEC_HP_R_RAW": "CODEC_DAC_OUT_N",
        "CODEC_HP_L_RAW": "CODEC_DAC_OUT_P",
        "CODEC_TX_DAC_TAP": "CODEC_DAC_OUT_P",
        "CODEC_PVDD": "3V3_CODEC_SWITCHED",
        "CODEC_QOD": "3V3_CODEC_SWITCHED",
        "HEADSET_TIP_DETECT_SOURCE": "HEADPHONE_LEFT_TIP",
    }
    actual_aliases = manifest["physical_net_aliases_collapsed"]
    for alias, canonical in required_aliases.items():
        if actual_aliases.get(alias) != canonical:
            raise ValueError(f"physical audio alias drifted: {alias} -> {actual_aliases.get(alias)}")


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
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad rejected populated UI hierarchy:\n{result.stdout}{result.stderr}")
    print("ok: KiCad parsed H2.2.5 inside the live hierarchy")


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
        print("ok: H2.2.5 audio codec/headset sheet is current")
    if args.kicad_check:
        kicad_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
