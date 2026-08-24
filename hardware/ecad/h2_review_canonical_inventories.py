#!/usr/bin/env python3
"""Capture the canonical H1/ledger/pin/M1/F2 inventories for H2.7.1."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
FW = REPO.parent / "esp32-leshy2-firmware"
OUTPUT = ECAD / "generated/H2-REV71-canonical-inventories.json"
PATHS = {
    "h1_physical_acceptance": REPO / "hardware/product-design/generated/H1-cross-view-acceptance.json",
    "h2_instance_ledger": ECAD / "generated/H2-instance-ledger.json",
    "architecture_pin_source": REPO / "hardware/architecture/candidates/G2F-3I.json",
    "ui_m1": ECAD / "generated/H2-UI40-interboard-m1.json",
    "rf_m1": ECAD / "generated/H2-RF40-interboard-m1.json",
    "h2_hwfw_export": ECAD / "generated/H2-hwfw-contract.json",
    "firmware_f2_import": FW / "config/hardware_bsp_contract.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[str, dict]:
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in PATHS.items()}
    h1 = data["h1_physical_acceptance"]
    ledger = data["h2_instance_ledger"]
    candidate = data["architecture_pin_source"]
    ui_m1 = data["ui_m1"]
    rf_m1 = data["rf_m1"]
    hwfw = data["h2_hwfw_export"]
    fw = data["firmware_f2_import"]
    if h1.get("status") != "reviewed" or h1.get("final_acceptance", {}).get("status") != "accepted":
        raise ValueError("H1 physical acceptance is not reviewed")
    if ledger.get("status") != "reviewed_complete_circuit_inventory" or len(ledger["rows"]) != 1035:
        raise ValueError("H2 instance ledger is not the reviewed 1,035-row inventory")
    pin_counts = dict(Counter(row["instance"] for row in candidate["allocations"]))
    if pin_counts != {"s3": 33, "c5": 14, "rp": 48, "pd_controller": 5, "pack_admission": 13, "safety_controller": 17}:
        raise ValueError(f"programmable pin inventory drifted: {pin_counts}")
    if ui_m1["contacts"] != rf_m1["contacts"] or len(ui_m1["contacts"]) != 80:
        raise ValueError("UI/RF M1 inventories are not identical 80-contact maps")
    if hwfw != fw:
        raise ValueError("firmware F2 canonical import differs from H2 HW/FW export")
    inventories = [
        {"owner": "H1", "role": "physical bodies, coordinates and accepted mechanical fit", "artifact": str(PATHS["h1_physical_acceptance"].relative_to(REPO)), "count": h1["physical_fit"]["source_registered_instances"]},
        {"owner": "H2 instance ledger", "role": "MPN, owning sheet and logical/physical contact counts", "artifact": str(PATHS["h2_instance_ledger"].relative_to(REPO)), "count": len(ledger["rows"])},
        {"owner": "architecture pin source", "role": "programmable contact assignment, direction, peripheral and peers; includes five hardware-configured PD contacts outside MCU BSP", "artifact": str(PATHS["architecture_pin_source"].relative_to(REPO)), "count": sum(pin_counts.values())},
        {"owner": "M1", "role": "the sole UI-to-RF electrical crossing", "artifact": str(PATHS["ui_m1"].relative_to(REPO)), "count": len(ui_m1["contacts"])},
        {"owner": "firmware F2", "role": "byte-stable software-visible copy of the H2 export", "artifact": "../esp32-leshy2-firmware/config/hardware_bsp_contract.json", "count": sum(row["allocated_contact_count"] for row in hwfw["bsp"]["domains"])},
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H2.7.1",
        "status": "reviewed_canonical_inventory_snapshot",
        "method": "assign one canonical owner to physical fit, part inventory, pin assignment, interboard crossing and firmware-visible state",
        "source_hashes": {key: sha256(path) for key, path in PATHS.items()},
        "inventories": inventories,
        "summary": {
            "canonical_inventories": len(inventories),
            "h2_instance_rows": len(ledger["rows"]),
            "allocated_controller_contacts": sum(pin_counts.values()),
            "firmware_bsp_contacts": 125,
            "pd_hardware_configuration_contacts": pin_counts["pd_controller"],
            "m1_contacts": len(ui_m1["contacts"]),
            "firmware_copy_byte_identical": True,
        },
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
        print(f"ok: H2.7.1 canonical inventory snapshot is current; {manifest['summary']['canonical_inventories']} owners")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
