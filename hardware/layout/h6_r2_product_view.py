#!/usr/bin/env python3
"""Current product-facing preview composed from the actual exterior PCB plots.

H1 remains a historical concept; this preview never imports its old placements.
Only the separately supplied display-panel envelope is added, explicitly labelled.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/images/h6-r2-product-exterior.svg"
MANIFEST = ROOT / "hardware/layout/generated/H6-R2-product-view.json"
NS = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", NS[1:-1])
BOARD_PATHS = {name: f"hardware/ecad/kicad/LESHY2-{name.upper()}-R2/LESHY2-{name.upper()}-R2.kicad_pcb"
               for name in ("ui", "rf")}
COMPONENT_SCRIPT = "hardware/layout/h6_r2_component_render.py"
EXPECTED_VIEW_INPUTS = set(BOARD_PATHS.values()) | {COMPONENT_SCRIPT}
EXPECTED_VIEW_OUTPUTS = {f"docs/images/h6-r2-components-{name}-{face}.svg"
                         for name in ("ui", "rf") for face in ("outer", "inner")} | {
                             "docs/images/h6-r2-components-overview.svg"}
EXPECTED_INTENT_SOURCES = set(BOARD_PATHS.values()) | {
    "hardware/layout/h6_r2_placement_intent.py",
    "hardware/layout/h6_r2_speaker_fit.py",
    "hardware/layout/h6-r2-speaker-body.json"}
MINIMUM_INTENT_CHECKS = 20


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate manifest key: {name}")
        result[name] = value
    return result


def validate_evidence(views, intent):
    if not isinstance(intent, dict) or intent.get("status") != "pass":
        raise ValueError("Do not publish a corrected product preview while placement intent fails")
    checks = intent.get("checks")
    if (type(intent.get("schema_version")) is not int or intent["schema_version"] != 1
            or not isinstance(checks, list) or len(checks) < MINIMUM_INTENT_CHECKS
            or intent.get("failed_requirements") != []):
        raise ValueError("incomplete or inconsistent placement-intent checks")
    names = []
    for check in checks:
        if (not isinstance(check, dict) or check.get("pass") is not True
                or not isinstance(check.get("requirement"), str)
                or not check["requirement"].strip()):
            raise ValueError("placement-intent checks must be named and strictly true")
        names.append(check["requirement"].strip())
    if len(names) != len(set(names)):
        raise ValueError("duplicate placement-intent requirement")
    if not isinstance(views, dict) or views.get("status") != "current_native_visualization_not_assembly_approval":
        raise ValueError("unexpected component-view evidence")
    for label, entries, required in (
            ("view inputs", views.get("inputs_sha256"), EXPECTED_VIEW_INPUTS),
            ("view outputs", views.get("outputs_sha256"), EXPECTED_VIEW_OUTPUTS),
            ("intent sources", intent.get("sources"), EXPECTED_INTENT_SOURCES)):
        if not isinstance(entries, dict) or set(entries) != required:
            raise ValueError(f"incomplete or unexpected {label} inventory")
        for name, expected in entries.items():
            if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
                raise ValueError(f"invalid source digest: {name}")
    # Validate the finite inventory before reading any path from the records.
    for entries in (views["inputs_sha256"], views["outputs_sha256"], intent["sources"]):
        for name, expected in entries.items():
            if sha(ROOT/name) != expected:
                raise ValueError(f"stale native view/intent input: {name}")


def validate_outer_view(original, name, views):
    if (original.tag != NS+"svg" or original.get("viewBox") != "0 0 96 190"
            or original.get("data-board") != name or original.get("data-face") != "outer"
            or original.get("data-source-sha256") != views["inputs_sha256"][BOARD_PATHS[name]]
            or original.get("data-renderer-sha256") != views["inputs_sha256"][COMPONENT_SCRIPT]):
        raise ValueError(f"wrong native outer-view identity, scale or source: {name}")


def build():
    views_path = ROOT / "hardware/layout/generated/H6-R2-component-views.json"
    intent_path = ROOT / "hardware/layout/generated/H6-R2-placement-intent.json"
    contract_path = ROOT / "hardware/layout/h6-r2-placement-contract.json"
    views, intent = [json.loads(path.read_text(), object_pairs_hook=unique_object)
                     for path in (views_path, intent_path)]
    validate_evidence(views, intent)
    paths = [Path(__file__), views_path, intent_path, contract_path]
    content = []
    for index, name in enumerate(("ui", "rf")):
        path = ROOT / f"docs/images/h6-r2-components-{name}-outer.svg"
        paths.append(path)
        original = ET.fromstring(path.read_text())
        validate_outer_view(original, name, views)
        parts = [ET.tostring(child, encoding="unicode") for child in original
                 if child.tag != NS+"title"]
        content.append(f'<g data-board="{name}" transform="translate({index*96} 15)">' + "".join(parts))
        if name == "ui":
            bed = json.loads(contract_path.read_text())["mechanical"]["display_bed"]["panel_bbox_mm"]
            x, y = bed["x"][0]+8, bed["y"][0]+25
            w, h = bed["x"][1]-bed["x"][0], bed["y"][1]-bed["y"][0]
            content += [f'<g data-role="nominal-display-panel-envelope" data-source="H6-display-bed">',
                        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx=".6" fill="#dbeafe" stroke="#2563eb" stroke-width=".3"/>',
                        f'<text x="{x+w/2}" y="{y+5}" text-anchor="middle" font-size="2" fill="#1d4ed8">FPC ↑</text>',
                        f'<text x="{x+w/2}" y="{y+h/2}" text-anchor="middle" font-size="3" fill="#1d4ed8">DISPLAY</text>',
                        f'<text x="{x+w/2}" y="{y+h/2+4}" text-anchor="middle" font-size="1.7" fill="#334155">56.54 × 84.96 mm · panel envelope</text>',
                        '</g>', '<rect x="7" y="182" width="65" height="7" fill="white"/>',
                        '<text x="8" y="186" font-size="1.4" fill="#334155">Синий: габарит панели / blue: panel envelope</text>']
        content.append('</g>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="4100" viewBox="0 0 192 205" '
           'font-family="Arial,DejaVu Sans,sans-serif" data-role="current-native-product-preview">'
           '<title>Leshy2 · Current exterior arrangement from native PCB</title>'
           '<rect width="192" height="205" fill="white"/>'
           '<text x="8" y="5" font-size="3.4" fill="#17263c">Леший2 · Текущая компоновка / Current arrangement</text>'
           '<text x="8" y="9" font-size="1.65" fill="#475569">Положения из PCB; не 3D-проверка сборки / Native positions; not assembled 3D validation</text>'
           + "".join(content) + '</svg>\n')
    manifest = {"status": "native_planar_preview_not_assembly_qualification",
                "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in paths},
                "output": str(OUTPUT.relative_to(ROOT)),
                "output_sha256": hashlib.sha256(svg.encode()).hexdigest(),
                "assembly_overlay": "Only labelled nominal display panel envelope. No invented cells, knob, free-cable or enclosure geometry."}
    return svg, json.dumps(manifest, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    svg, manifest = build()
    if args.write:
        OUTPUT.write_text(svg)
        MANIFEST.write_text(manifest)
    if not OUTPUT.exists() or OUTPUT.read_text() != svg or not MANIFEST.exists() or MANIFEST.read_text() != manifest:
        raise SystemExit("current product preview is stale")
    print("Current product preview matches native PCB views and independent placement intent")


if __name__ == "__main__":
    main()
