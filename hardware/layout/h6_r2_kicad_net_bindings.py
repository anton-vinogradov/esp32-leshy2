#!/usr/bin/env python3
"""Bind canonical H2 nets to KiCad's exact hierarchical PCB net names."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTANCE_PATH = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NET_PATH = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
SYMBOL_PATH = ROOT / "hardware/ecad/generated/H2-R2-controlled-symbol-library.json"
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json"
PROJECTS = {
    "LESHY2-UI-R2": ROOT / "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_sch",
    "LESHY2-RF-R2": ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_sch",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logical_pin_map(project: str) -> tuple[dict[tuple[str, str], str], set[str]]:
    instances = load(INSTANCE_PATH)["rows"]
    rows = load(NET_PATH)["rows"]
    symbols = {row["device_id"]: row for row in load(SYMBOL_PATH)["symbols"]}
    by_instance = {row["instance"]: row for row in instances if row["project"] == project}
    contact_to_pin = {
        device_id: {
            contact: pin["number"]
            for pin in symbol["pin_map"]
            for contact in pin["contacts"]
        }
        for device_id, symbol in symbols.items()
    }
    result: dict[tuple[str, str], str] = {}
    physical_nets: set[str] = set()
    for row in rows:
        if row["project"] != project or row["disposition"] != "connected":
            continue
        instance = by_instance[row["instance"]]
        pin = contact_to_pin[instance["device_id"]].get(row["contact"])
        if pin is None:
            if row["contact"] in {"ANT", "ANT1"}:
                continue
            raise ValueError(f"{project}: no physical pin for {row['endpoint']}")
        key = (instance["reference"], pin)
        previous = result.get(key)
        if previous and previous != row["net"]:
            raise ValueError(f"{project}: {key} maps to both {previous} and {row['net']}")
        result[key] = row["net"]
        physical_nets.add(row["net"])
    return result, physical_nets


def bind_project(project: str, xml_path: Path) -> dict:
    pin_map, expected_nets = logical_pin_map(project)
    mappings: dict[str, set[str]] = defaultdict(set)
    physical_nodes = 0
    explicit_no_connect_nodes = 0
    unknown = []
    mixed = []
    root = ET.parse(xml_path).getroot()
    nets = root.find("nets")
    if nets is None:
        raise ValueError(f"{project}: KiCad XML export contains no nets")
    for net in nets:
        actual_name = net.attrib["name"]
        canonical = {
            pin_map[(node.attrib["ref"], node.attrib["pin"])]
            for node in net
            if (node.attrib["ref"], node.attrib["pin"]) in pin_map
        }
        if not canonical:
            if actual_name.split("/")[-1].startswith("unconnected-"):
                explicit_no_connect_nodes += len(net)
            else:
                unknown.append(actual_name)
            continue
        physical_nodes += len(net)
        if len(canonical) != 1:
            mixed.append({"kicad_net": actual_name, "canonical_nets": sorted(canonical)})
            continue
        mappings[next(iter(canonical))].add(actual_name)
    split = {name: sorted(values) for name, values in mappings.items() if len(values) != 1}
    missing = sorted(expected_nets - set(mappings))
    errors = []
    if unknown:
        errors.append(f"{len(unknown)} KiCad nets contain no reviewed physical endpoint")
    if mixed:
        errors.append(f"{len(mixed)} KiCad nets merge distinct canonical nets")
    if split:
        errors.append(f"{len(split)} canonical nets split into multiple KiCad nets")
    if missing:
        errors.append(f"{len(missing)} canonical physical nets are absent from KiCad")
    if errors:
        raise ValueError(f"{project}: " + "; ".join(errors))
    return {
        "schematic": str(PROJECTS[project].relative_to(ROOT)),
        "schematic_sha256": sha256(PROJECTS[project]),
        "exported_net_count": len(nets),
        "canonical_physical_net_count": len(expected_nets),
        "connected_physical_node_count": physical_nodes,
        "explicit_no_connect_node_count": explicit_no_connect_nodes,
        "canonical_to_kicad": {
            name: next(iter(mappings[name])) for name in sorted(mappings)
        },
    }


def build(ui_netlist: Path, rf_netlist: Path) -> dict:
    return {
        "schema_version": 1,
        "artifact": "H6-R2 exact KiCad hierarchical net bindings",
        "marker": "H6.0.2-R1",
        "status": "pass",
        "method": "KiCad 10 kicadxml export joined by exact reference/pin to the reviewed H2 native net ledger",
        "source_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (INSTANCE_PATH, NET_PATH, SYMBOL_PATH, *PROJECTS.values())
        },
        "projects": {
            "LESHY2-UI-R2": bind_project("LESHY2-UI-R2", ui_netlist),
            "LESHY2-RF-R2": bind_project("LESHY2-RF-R2", rf_netlist),
        },
        "authorization": {"pcb_net_binding": True, "routing": True, "fabrication": False},
        "errors": [],
    }


def check() -> list[str]:
    if not OUTPUT.is_file():
        return ["binding artifact is missing"]
    artifact = load(OUTPUT)
    errors = []
    if artifact.get("status") != "pass" or artifact.get("marker") != "H6.0.2-R1":
        errors.append("binding identity/status changed")
    for relative, expected in artifact.get("source_hashes", {}).items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            errors.append(f"source drift: {relative}")
    for project in PROJECTS:
        _, expected = logical_pin_map(project)
        mapping = artifact.get("projects", {}).get(project, {}).get("canonical_to_kicad", {})
        if set(mapping) != expected:
            errors.append(f"{project}: canonical binding coverage changed")
        if len(set(mapping.values())) != len(mapping):
            errors.append(f"{project}: distinct canonical nets share one KiCad name")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--ui-netlist", type=Path)
    parser.add_argument("--rf-netlist", type=Path)
    args = parser.parse_args()
    if args.write:
        if not args.ui_netlist or not args.rf_netlist:
            parser.error("--write requires --ui-netlist and --rf-netlist")
        artifact = build(args.ui_netlist, args.rf_netlist)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        counts = artifact["projects"]
        print(
            "H6-R2 KiCad net bindings pass: "
            f"{counts['LESHY2-UI-R2']['canonical_physical_net_count']} UI + "
            f"{counts['LESHY2-RF-R2']['canonical_physical_net_count']} RF canonical nets"
        )
        return 0
    errors = check()
    if errors:
        print("H6-R2 KiCad net bindings fail: " + "; ".join(errors))
        return 1
    artifact = load(OUTPUT)
    print(
        "H6-R2 KiCad net bindings pass: "
        f"{artifact['projects']['LESHY2-UI-R2']['canonical_physical_net_count']} UI + "
        f"{artifact['projects']['LESHY2-RF-R2']['canonical_physical_net_count']} RF canonical nets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
