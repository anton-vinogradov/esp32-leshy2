#!/usr/bin/env python3
"""Validate and render the exact Leshy2 removable-accessory source."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any


ACCESSORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = ACCESSORY_DIR.parents[1]
SOURCE_FILE = ACCESSORY_DIR / "leshy2-lora-cap-01.json"
DEVICE_FILE = REPO_ROOT / "hardware/architecture/devices.json"
PINOUT_OUTPUT = ACCESSORY_DIR / "generated/LESHY2-LORA-CAP-01-pinout.md"
BOM_OUTPUT = ACCESSORY_DIR / "generated/LESHY2-LORA-CAP-01-bom.csv"
LAYOUT_OUTPUT = REPO_ROOT / "docs/images/lora-cap-layout.svg"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=reject_duplicate_keys)


def load_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    return load_json(SOURCE_FILE), load_json(DEVICE_FILE)


def variant_instances(
    accessory: dict[str, Any], variant: dict[str, Any]
) -> dict[str, str]:
    return {**accessory["common_instances"], "variant_module": variant["module"]}


def validate_sources(accessory: dict[str, Any], database: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    devices = database.get("devices", {})
    if accessory.get("schema_version") != 1:
        errors.append("unsupported accessory schema_version")
    if accessory.get("id") != "LESHY2-LORA-CAP-01":
        errors.append("unexpected accessory id")

    variants = accessory.get("variants", {})
    expected_variants = {
        "LESHY2-LORA-CAP-01-EU868": "nicerf_lora1262_868",
        "LESHY2-LORA-CAP-01-US915": "nicerf_lora1262_915",
    }
    if {name: row.get("module") for name, row in variants.items()} != expected_variants:
        errors.append("the two exact regional module variants are required")

    for variant_name, variant in variants.items():
        instances = variant_instances(accessory, variant)
        for instance, device_id in instances.items():
            if device_id not in devices:
                errors.append(f"{variant_name}: {instance} references unknown {device_id}")
        if any(device_id not in devices for device_id in instances.values()):
            continue
        module = devices[variant["module"]]
        if "integrated and controlled by SX1262" not in module.get(
            "electrical_contract", {}
        ).get("rf_switch", ""):
            errors.append(f"{variant_name}: module requires an unexposed RF-switch GPIO")

        for route_number, route in enumerate(accessory.get("fixed_routes", []), 1):
            for side in ("from", "to"):
                endpoint = route.get(side, "")
                if endpoint.startswith("abstract:"):
                    continue
                if "." not in endpoint:
                    errors.append(f"route {route_number}: malformed {side} endpoint")
                    continue
                instance, contact = endpoint.split(".", 1)
                if instance not in instances:
                    errors.append(f"route {route_number}: unknown instance {instance}")
                    continue
                device = devices[instances[instance]]
                if contact not in device.get("contacts", {}):
                    errors.append(
                        f"route {route_number}: {endpoint} absent on {device['mpn']}"
                    )

    pins = accessory.get("pin_contract", [])
    if [row.get("pin") for row in pins] != list(range(1, 15)):
        errors.append("Cap-Bus pin contract must cover ordered pins 1..14 exactly")
    if pins:
        if pins[4].get("custom_cap") != "EXT_TX_EVIDENCE_N":
            errors.append("Cap-Bus pin 5 must be EXT_TX_EVIDENCE_N")
        if pins[4].get("stock_u214") != "5V_OUT":
            errors.append("stock U214 pin-5 behavior must remain explicit")

    evidence = accessory.get("evidence_contract", {})
    if evidence.get("output") != (
        "open-drain active-low on Cap-Bus pin 5; no Cap rail means released high"
    ):
        errors.append("evidence output must fail open when the Cap is unpowered")
    pulse = evidence.get("pulse_acceptance_ms", [])
    if pulse != [10.0, 18.0] or evidence.get("host_poll_period_max_ms", 999) > pulse[0]:
        errors.append("the evidence pulse must outlive the maximum host poll period")
    if evidence.get("host_post_revoke_grace_max_ms", 0) < pulse[1]:
        errors.append("the evidence pulse must fit inside post-revoke grace")

    required_routes = {
        ("variant_module.ANT", "rf_coupler.RF_IN"),
        ("rf_coupler.RF_OUT", "rf_sma.RF"),
        ("rf_coupler.COUPLED_FWD", "rf_detector.RFIN"),
        ("rf_detector.V_UP", "evidence_comparator.IN_P"),
        ("evidence_comparator.OUT", "evidence_monostable.B"),
        ("evidence_monostable.Q", "evidence_driver.A"),
        ("evidence_driver.Y", "cap_header.PIN_5"),
    }
    actual_routes = {(route["from"], route["to"]) for route in accessory["fixed_routes"]}
    missing = required_routes - actual_routes
    if missing:
        errors.append(f"incomplete final-feed evidence chain: {sorted(missing)}")
    if accessory.get("common_instances", {}).get("evidence_driver") != (
        "ti_sn74lvc1g06_dckr"
    ):
        errors.append("the active-high monostable pulse requires an inverting open-drain driver")

    assembly = accessory.get("assembly", {})
    if assembly.get("pcb_mm") != [84.0, 24.0, 1.6]:
        errors.append("shared Cap envelope must remain 84 x 24 x 1.6 mm")
    if assembly.get("retention_pitch_mm") != 56.0:
        errors.append("shared Cap retention pitch must remain 56 mm")

    components = accessory.get("layout_projection", {}).get("components", [])
    reference_instances = variant_instances(
        accessory, accessory["variants"]["LESHY2-LORA-CAP-01-EU868"]
    )
    if [item.get("number") for item in components] != list(
        range(1, len(components) + 1)
    ):
        errors.append("layout component numbers must be contiguous from 1")
    layout_instances = [item.get("instance") for item in components]
    if len(layout_instances) != len(set(layout_instances)):
        errors.append("every layout component must appear once")
    if set(layout_instances) != set(reference_instances):
        errors.append(
            "layout must contain every and only the exact accessory device instances"
        )

    def component_box(item: dict[str, Any]) -> tuple[float, float, float, float]:
        device = devices[reference_instances[item["instance"]]]
        width = float(item.get("w", device["dimensions_mm"][0]))
        height = float(item.get("h", device["dimensions_mm"][1]))
        return float(item["x"]), float(item["y"]), width, height

    holes = assembly.get("retention_hole_centres_mm", [])
    for item in components:
        if item.get("face") not in {"outer", "inner", "edge"}:
            errors.append(f"layout component {item.get('instance')}: unknown face")
            continue
        x0, y0, item_width, item_height = component_box(item)
        x1, y1 = x0 + item_width, y0 + item_height
        if item["face"] in {"outer", "inner"} and not (
            0 <= x0 <= x1 <= assembly["pcb_mm"][0]
            and 0 <= y0 <= y1 <= assembly["pcb_mm"][1]
        ):
            errors.append(f"layout component {item['instance']} leaves the PCB")
        if item.get("face") in {"outer", "inner"}:
            for hx, hy in holes:
                nearest_x = min(max(hx, x0), x1)
                nearest_y = min(max(hy, y0), y1)
                if (nearest_x - hx) ** 2 + (nearest_y - hy) ** 2 < 4.0**2:
                    errors.append(
                        f"layout component {item['instance']} enters a 4-mm retention keep-out"
                    )
    for face in ("outer", "inner"):
        same_face = [item for item in components if item.get("face") == face]
        for index, left in enumerate(same_face):
            left_x, left_y, left_w, left_h = component_box(left)
            for right in same_face[index + 1 :]:
                right_x, right_y, right_w, right_h = component_box(right)
                separated = (
                    left_x + left_w <= right_x
                    or right_x + right_w <= left_x
                    or left_y + left_h <= right_y
                    or right_y + right_h <= left_y
                )
                if not separated:
                    errors.append(
                        f"{face} components {left['instance']} and {right['instance']} overlap"
                    )
    return errors


def render_pinout(accessory: dict[str, Any]) -> str:
    lines = [
        "# LESHY2-LORA-CAP-01 exact Cap-Bus contract",
        "",
        "Generated from `hardware/accessories/leshy2-lora-cap-01.json`.",
        "Pins are numbered in the host-mating orientation of the exact 2×7 connector.",
        "",
        "| Pin | Stock M5Stack U214 | LESHY2-LORA-CAP-01 | Direction at host |",
        "|---:|---|---|---|",
    ]
    for pin in accessory["pin_contract"]:
        lines.append(
            f"| {pin['pin']} | `{pin['stock_u214']}` | `{pin['custom_cap']}` | {pin['direction_at_host']} |"
        )
    lines.extend(
        [
            "",
            "Pin 5 is deliberately dual-profile. The stock U214 drives its documented "
            "`5V_OUT` high and therefore provides no TX evidence. The custom Cap only "
            "releases or sinks the line through an open-drain final-feed detector; it never "
            "sources the host boundary.",
            "",
        ]
    )
    return "\n".join(lines)


def render_bom(accessory: dict[str, Any], database: dict[str, Any]) -> str:
    devices = database["devices"]
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "variant",
            "quantity",
            "device_id",
            "mpn",
            "role_instances",
            "unit_price_usd_q100",
            "cost_status",
            "source_url",
        ]
    )
    for variant_name, variant in accessory["variants"].items():
        instances = variant_instances(accessory, variant)
        by_device: dict[str, list[str]] = {}
        for instance, device_id in instances.items():
            by_device.setdefault(device_id, []).append(instance)
        for device_id in sorted(by_device, key=lambda item: devices[item]["mpn"]):
            device = devices[device_id]
            cost = device.get("cost")
            gate = device.get("cost_gate")
            writer.writerow(
                [
                    variant_name,
                    len(by_device[device_id]),
                    device_id,
                    device["mpn"],
                    ";".join(sorted(by_device[device_id])),
                    "" if cost is None else f"{cost['unit_price_usd']:.5f}",
                    "priced" if cost else gate["status"] if gate else "missing",
                    device.get("orderable_source", device["source"])["url"],
                ]
            )
    return output.getvalue()


def known_variant_cost(
    accessory: dict[str, Any], database: dict[str, Any], variant: dict[str, Any]
) -> tuple[float, list[str]]:
    devices = database["devices"]
    counts = Counter(variant_instances(accessory, variant).values())
    known = 0.0
    gates: list[str] = []
    for device_id, quantity in counts.items():
        device = devices[device_id]
        if "cost" in device:
            known += quantity * float(device["cost"]["unit_price_usd"])
        else:
            gates.append(device["mpn"])
    return known, gates


def render_layout(accessory: dict[str, Any], database: dict[str, Any]) -> str:
    width, height, _ = accessory["assembly"]["pcb_mm"]
    scale = 10.0
    ox, oy = 40.0, 260.0
    svg_w, svg_h = 1500, 730
    devices = database["devices"]
    reference_variant = accessory["variants"]["LESHY2-LORA-CAP-01-EU868"]
    instances = variant_instances(accessory, reference_variant)
    components = accessory["layout_projection"]["components"]

    def size(item: dict[str, Any]) -> tuple[float, float]:
        device = devices[instances[item["instance"]]]
        return (
            float(item.get("w", device["dimensions_mm"][0])),
            float(item.get("h", device["dimensions_mm"][1])),
        )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Inter,Arial,sans-serif}.title{font-size:22px;font-weight:700;fill:#172033}.sub{font-size:12px;fill:#526076}.label{font-size:11px;font-weight:700;fill:#172033}.small{font-size:9px;fill:#344054}.tiny{font-size:6px;font-weight:700;fill:#172033}.silk{font-size:9px;font-weight:700;fill:#166534}</style>',
        '<text class="title" x="40" y="42">LESHY2-LORA-CAP-01 · exact-device envelope projection</text>',
        '<text class="sub" x="40" y="68">True millimetre scale. Outer and directly viewed mirrored inner faces are separated; every numbered outline is one physical device.</text>',
        f'<rect x="{ox}" y="{oy}" width="{width*scale}" height="{height*scale}" rx="10" fill="#f8fafc" stroke="#344054" stroke-width="2"/>',
        f'<text class="label" x="{ox}" y="{oy-18}">OUTER FACE · accessible silkscreen is green</text>',
    ]
    for hx, hy in accessory["assembly"]["retention_hole_centres_mm"]:
        cx, cy = ox + hx * scale, oy + hy * scale
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="#f97316" stroke-width="1.5" stroke-dasharray="6 4"/>'
        )
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="#526076" stroke-width="2"/>'
        )
    colors = {"outer": ("#dbeafe", "#2563eb"), "edge": ("#ffedd5", "#ea580c")}
    for item in components:
        if item["face"] == "inner":
            continue
        item_w, item_h = size(item)
        fill, stroke = colors[item["face"]]
        x, y = ox + item["x"] * scale, oy + item["y"] * scale
        w, h = item_w * scale, item_h * scale
        lines.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(4.0, max(0.5, min(w,h)/5))}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" data-instance="{escape(item["instance"])}"/>'
        )
        lines.append(
            f'<text class="tiny" x="{x+w/2}" y="{y+h/2+2}" text-anchor="middle">{item["number"]}</text>'
        )
    lines.extend(
        [
            f'<text class="silk" x="{ox+420}" y="{oy+20}" text-anchor="middle">LORA SMA</text>',
            f'<text class="silk" x="{ox+510}" y="{oy+174}" text-anchor="middle">LESHY2 LORA CAP 01</text>',
            f'<text class="silk" x="{ox+510}" y="{oy+194}" text-anchor="middle">EU868 or US915 · exactly one assembly marking</text>',
            f'<line x1="{ox+420}" y1="{oy-154}" x2="{ox+420}" y2="{oy-190}" stroke="#dc2626" stroke-width="2"/>',
            f'<polygon points="{ox+420},{oy-200} {ox+414},{oy-188} {ox+426},{oy-188}" fill="#dc2626"/>',
            f'<text class="small" x="{ox+438}" y="{oy-164}" fill="#dc2626">RF / antenna outward</text>',
            f'<line x1="{ox}" y1="{oy+height*scale+38}" x2="{ox+width*scale}" y2="{oy+height*scale+38}" stroke="#344054"/>',
            f'<text class="label" x="{ox+width*scale/2}" y="{oy+height*scale+62}" text-anchor="middle">84.0 mm board; 56.0-mm retention pitch</text>',
            '<rect x="910" y="92" width="560" height="470" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>',
            '<text class="label" x="930" y="118">DOCUMENTATION LEGEND · not PCB silkscreen</text>',
        ]
    )
    legend_y = 142
    for item in components:
        device = devices[instances[item["instance"]]]
        mpn = device["mpn"]
        if item["instance"] == "variant_module":
            mpn = "NiceRF LoRa1262-868 / LoRa1262-915"
        lines.append(
            f'<text class="small" x="930" y="{legend_y}"><tspan font-weight="700">{item["number"]:02d} · {escape(mpn)}</tspan><tspan> — {escape(item["label"])}</tspan></text>'
        )
        legend_y += 15

    inner_scale = 5.0
    inner_x, inner_y = 40.0, 590.0
    lines.extend(
        [
            f'<text class="label" x="{inner_x}" y="{inner_y-14}">INNER FACE · direct view, mirrored from outer face · no silkscreen</text>',
            f'<rect x="{inner_x}" y="{inner_y}" width="{width*inner_scale}" height="{height*inner_scale}" rx="7" fill="#f8fafc" stroke="#344054" stroke-width="2"/>',
        ]
    )
    for item in components:
        if item["face"] != "inner":
            continue
        item_w, item_h = size(item)
        mirrored_x = width - item["x"] - item_w
        x = inner_x + mirrored_x * inner_scale
        y = inner_y + item["y"] * inner_scale
        w, h = item_w * inner_scale, item_h * inner_scale
        lines.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.5" data-instance="{escape(item["instance"])}"/>'
        )
        lines.append(
            f'<text class="small" x="{x+w/2}" y="{y+h/2+3}" text-anchor="middle">{item["number"]} · mating ⊗</text>'
        )
    known, _ = known_variant_cost(accessory, database, reference_variant)
    lines.extend(
        [
            '<text class="label" x="930" y="590">Exact regional assemblies</text>',
            f'<text class="small" x="930" y="611">LESHY2-LORA-CAP-01-EU868 · NiceRF LoRa1262-868 · 848–888 MHz</text>',
            f'<text class="small" x="930" y="628">LESHY2-LORA-CAP-01-US915 · NiceRF LoRa1262-915 · 900–940 MHz</text>',
            f'<text class="small" x="930" y="650">Known quantity-100 electronics: ${known:.2f}; radio module, PCB and assembly remain RFQ gates.</text>',
            f'<text class="small" x="930" y="680">Pre-KiCad envelope proof; exact pads and copper follow only after architecture release.</text>',
            '</svg>',
            '',
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        accessory, database = load_sources()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    errors = validate_sources(accessory, database)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    outputs = {
        PINOUT_OUTPUT: render_pinout(accessory),
        BOM_OUTPUT: render_bom(accessory, database),
        LAYOUT_OUTPUT: render_layout(accessory, database),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO_ROOT)}")
        return 0
    stale = [
        path for path, content in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    if stale:
        for path in stale:
            print(f"ERROR: stale {path.relative_to(REPO_ROOT)}; run --write", file=sys.stderr)
        return 1
    print(f"ok: {len(outputs)} accessory artifacts are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
