#!/usr/bin/env python3
"""Prove every allocated controller contact reaches the same H2/F2 net."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from h2_review_canonical_inventories import (
    ECAD,
    FW,
    REPO,
    sha256,
    validate_historical_firmware_copy,
)
from h2_review_no_connects import pin_map, top_symbol_blocks
from h2_review_power_paths import PROJECTS, export_project
from h2_symbol_library import embedded_symbols


GENERATED = ECAD / "generated"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
HWFW = GENERATED / "H2-hwfw-contract.json"
FW_BSP = FW / "config/hardware_bsp_contract.json"
FW_INTEGRATION = FW / "config/hardware_integration_contract.json"
FW_IMPORTER = FW / "tools/import_hardware_contract.py"
OUTPUT = GENERATED / "H2-REV74-firmware-contract.json"
FIRMWARE_INSTANCES = {"s3", "c5", "rp", "pack_admission", "safety_controller"}


def instance_locations() -> dict[str, dict]:
    result = {}
    for path in sorted(GENERATED.glob("H2-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("project") or not data.get("sheet"):
            continue
        for row in data.get("instances", []):
            if row["instance"] in result:
                raise ValueError(f"duplicate instance location for {row['instance']}")
            result[row["instance"]] = {**row, "project": data["project"], "sheet": data["sheet"], "artifact": path}
    return result


def xml_pin_nets(path: Path) -> dict[tuple[str, str], str]:
    tree = ET.parse(path)
    result = {}
    for net in tree.findall(".//nets/net"):
        name = (net.get("name") or "").split("/")[-1]
        for node in net.findall("node"):
            result[(node.get("ref", ""), node.get("pin", ""))] = name
    return result


def build() -> tuple[str, dict]:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    hwfw = json.loads(HWFW.read_text(encoding="utf-8"))
    fw_bsp = json.loads(FW_BSP.read_text(encoding="utf-8"))
    fw_integration = json.loads(FW_INTEGRATION.read_text(encoding="utf-8"))
    validate_historical_firmware_copy(hwfw, fw_bsp)
    if fw_bsp["integration_contract"] != fw_integration:
        raise ValueError("firmware integration copy differs from its canonical BSP import")
    result = subprocess.run([sys.executable, str(FW_IMPORTER), "--check"], cwd=FW, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"firmware importer drift check failed:\n{result.stdout}{result.stderr}")
    locations = instance_locations()
    native = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h274-") as temp:
        for project, root in PROJECTS.items():
            destination = Path(temp) / f"{project}.xml"
            export_project(project, root, destination)
            native[project] = xml_pin_nets(destination)
    sheet_cache = {}
    reviewed = []
    for allocation in candidate["allocations"]:
        instance = allocation["instance"]
        location = locations[instance]
        project, sheet = location["project"], location["sheet"]
        key = (project, sheet)
        if key not in sheet_cache:
            schematic = ECAD / f"kicad/{project}/{sheet}.kicad_sch"
            text = schematic.read_text(encoding="utf-8")
            definitions = dict(embedded_symbols(text))
            blocks = {}
            for block in top_symbol_blocks(text):
                uuid = re.search(r'\(uuid "([^"]+)"\)', block)
                lib_id = re.search(r'\(lib_id "Leshy2:([^"]+)"\)', block)
                if uuid and lib_id:
                    blocks[uuid.group(1)] = lib_id.group(1)
            sheet_cache[key] = (definitions, blocks)
        definitions, blocks = sheet_cache[key]
        lib_id = blocks[location["symbol_uuid"]]
        pins = pin_map(definitions[lib_id]).get(allocation["contact"], [])
        if not pins:
            raise ValueError(f"{instance}.{allocation['contact']} is absent from the populated symbol")
        actual = {
            native[project].get((location["reference"], number))
            for number, _, _ in pins
        } - {None}
        if actual != {allocation["net"]}:
            raise ValueError(f"{instance}.{allocation['contact']} net drift: pin={allocation['net']}, KiCad={sorted(actual)}")
        reviewed.append({
            "domain": next((row["domain"] for row in hwfw["bsp"]["domains"] if row["instance"] == instance), "PD_CONFIG"),
            "endpoint": f"{instance}.{allocation['contact']}",
            "net": allocation["net"],
            "direction": allocation["direction"],
            "controller": allocation["controller"],
            "physical_pin": "/".join(number for number, _, _ in pins),
        })
    bsp_rows = [pin for domain in hwfw["bsp"]["domains"] for pin in domain["pins"]]
    expected_firmware = [row for row in candidate["allocations"] if row["instance"] in FIRMWARE_INSTANCES]
    if bsp_rows != expected_firmware or len(bsp_rows) != 125:
        raise ValueError("firmware BSP pin rows differ from the 125 MCU-visible architecture allocations")
    manifest = {
        "schema_version": 1,
        "stage": "H2.7.4",
        "status": "reviewed_zero_hwfw_contract_drift",
        "method": "fresh native KiCad pin-to-net lookup for every allocation plus a semantically identical firmware import carrying explicit fail-closed historical-R1 authority",
        "source_hashes": {
            str(CANDIDATE.relative_to(REPO)): sha256(CANDIDATE),
            str(HWFW.relative_to(REPO)): sha256(HWFW),
            "firmware/config/hardware_bsp_contract.json": sha256(FW_BSP),
            "firmware/config/hardware_integration_contract.json": sha256(FW_INTEGRATION),
            "firmware/tools/import_hardware_contract.py": sha256(FW_IMPORTER),
            **{str(row["artifact"].relative_to(REPO)): sha256(row["artifact"]) for row in locations.values() if row["instance"] in {a["instance"] for a in candidate["allocations"]}},
        },
        "summary": {
            "architecture_allocations": len(reviewed),
            "firmware_bsp_contacts": len(bsp_rows),
            "hardware_configured_pd_contacts": len(reviewed) - len(bsp_rows),
            "physical_pin_or_net_mismatches": 0,
            "firmware_import_drift": 0,
            "temporary_pin_assignments_allowed": False,
        },
        "allocations": reviewed,
        "corrected_findings": [{
            "id": "H2.7.4-F01",
            "finding": "PACK UART allocations used PACK_SERVICE_UART_TX/RX while KiCad, fixture pads and fixed routes used PACK_ADMISSION_UART_TX/RX",
            "correction": "the two allocation/F2 names now use the established PACK_ADMISSION_UART_TX/RX canonical nets",
        }],
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
        print(f"ok: H2.7.4 HW/FW contract is current; {manifest['summary']['architecture_allocations']} allocated contacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
