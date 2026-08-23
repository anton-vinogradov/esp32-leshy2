#!/usr/bin/env python3
"""Reconcile every root-hierarchy net and all 80 physical M1 crossings."""

from __future__ import annotations

import argparse
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from h2_review_canonical_inventories import ECAD, REPO, sha256
from h2_review_power_paths import PROJECTS, export_project


GENERATED = ECAD / "generated"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
OUTPUT = GENERATED / "H2-REV73-named-nets-m1.json"
ROOTS = {
    "LESHY2-UI": GENERATED / "H2-UI-root-interface.json",
    "LESHY2-RF": GENERATED / "H2-RF-root-interface.json",
    "LESHY2-LORA-CAP-01": GENERATED / "H2-CAP00-root-interface.json",
}
UI_M1 = GENERATED / "H2-UI40-interboard-m1.json"
RF_M1 = GENERATED / "H2-RF40-interboard-m1.json"


def xml_pin_nets(path: Path) -> dict[tuple[str, str], str]:
    tree = ET.parse(path)
    result = {}
    for net in tree.findall(".//nets/net"):
        name = (net.get("name") or "").split("/")[-1]
        for node in net.findall("node"):
            key = (node.get("ref", ""), node.get("pin", ""))
            if key in result and result[key] != name:
                raise ValueError(f"one physical pin appears on two nets: {key}")
            result[key] = name
    return result


def build() -> tuple[str, dict]:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    root_data = {project: json.loads(path.read_text(encoding="utf-8")) for project, path in ROOTS.items()}
    ui = json.loads(UI_M1.read_text(encoding="utf-8"))
    rf = json.loads(RF_M1.read_text(encoding="utf-8"))
    expected_m1 = candidate["interboard_contract"]["pin_map"]
    if ui["contacts"] != rf["contacts"]:
        raise ValueError("UI and RF M1 sheet contracts differ")
    reduced = [{key: row[key] for key in ("contact", "net", "direction", "signal_class")} for row in ui["contacts"]]
    if reduced != expected_m1:
        raise ValueError("M1 schematic contract differs from the canonical architecture pin map")
    exports = {}
    actual_pin_maps = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h273-") as temp:
        for project, root in PROJECTS.items():
            destination = Path(temp) / f"{project}.xml"
            nets, stats = export_project(project, root, destination)
            exports[project] = {"nets": nets, "stats": stats}
            actual_pin_maps[project] = xml_pin_nets(destination)
    reviewed_roots = []
    for project, manifest in root_data.items():
        expected = {row["name"] for row in manifest["nets"]}
        actual = set(exports[project]["nets"])
        missing = sorted(expected - actual)
        if missing:
            raise ValueError(f"{project} root nets absent from native netlist: {missing}")
        reviewed_roots.append({
            "project": project,
            "root_named_nets": len(expected),
            "native_netlist_nets": len(actual),
            "missing_root_nets": 0,
        })
    ui_ref = ui["instances"][0]["reference"]
    rf_ref = rf["instances"][0]["reference"]
    m1_rows = []
    for row in ui["contacts"]:
        pin = str(row["symbol_pin"])
        ui_net = actual_pin_maps["LESHY2-UI"].get((ui_ref, pin))
        rf_net = actual_pin_maps["LESHY2-RF"].get((rf_ref, pin))
        if ui_net != row["net"] or rf_net != row["net"]:
            raise ValueError(f"M1.{pin} net mismatch: contract={row['net']}, UI={ui_net}, RF={rf_net}")
        m1_rows.append({"contact": row["contact"], "net": row["net"], "direction": row["direction"], "signal_class": row["signal_class"], "ui": ui_net, "rf": rf_net})
    if len(m1_rows) != 80 or len({row["net"] for row in m1_rows}) != 51:
        raise ValueError("M1 must remain 80 physical contacts carrying 51 unique nets")
    manifest = {
        "schema_version": 1,
        "stage": "H2.7.3",
        "status": "reviewed_named_nets_and_m1",
        "method": "fresh native KiCad XML netlists compared with all root hierarchy names and both physical M1 connector pin maps",
        "source_hashes": {
            str(CANDIDATE.relative_to(REPO)): sha256(CANDIDATE),
            **{str(path.relative_to(REPO)): sha256(path) for path in (*ROOTS.values(), UI_M1, RF_M1, *PROJECTS.values())},
        },
        "summary": {
            "projects_exported": len(PROJECTS),
            "root_named_nets": sum(row["root_named_nets"] for row in reviewed_roots),
            "missing_root_nets": 0,
            "m1_physical_contacts": len(m1_rows),
            "m1_unique_nets": len({row["net"] for row in m1_rows}),
            "m1_contact_mismatches": 0,
            "hidden_ui_rf_crossings": 0,
        },
        "root_projects": reviewed_roots,
        "m1_contacts": m1_rows,
        "corrected_findings": [],
        "open_findings": [],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, manifest = build()
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    else:
        print(f"ok: H2.7.3 named-net/M1 review is current; {manifest['summary']['m1_physical_contacts']} M1 contacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
