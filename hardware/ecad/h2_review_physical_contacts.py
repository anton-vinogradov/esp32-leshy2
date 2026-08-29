#!/usr/bin/env python3
"""Reconcile all H2 ledger rows with populated schematic symbol contacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from h2_review_canonical_inventories import ECAD, REPO, sha256


GENERATED = ECAD / "generated"
LEDGER = GENERATED / "H2-instance-ledger.json"
OUTPUT = GENERATED / "H2-REV72-physical-contacts.json"


def normalized_uid(uid: str) -> str:
    parts = uid.split(":")
    if parts[0] == "LESHY2-LORA-CAP-01":
        return f"{parts[0]}:{parts[-1]}"
    return uid


def schematic_instances() -> tuple[dict[str, dict], dict[str, str]]:
    result = {}
    sources = {}
    for path in sorted(GENERATED.glob("H2-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        project = data.get("project")
        if not project:
            continue
        rows = list(data.get("instances", []))
        if "host_connector" in data:
            host = dict(data["host_connector"])
            host["pin_count"] = data["summary"]["host_physical_contacts"]
            rows.append(host)
        for row in rows:
            uid = f"{project}:{row['instance']}"
            if uid in result:
                raise ValueError(f"duplicate schematic instance identity: {uid}")
            result[uid] = {**row, "artifact": str(path.relative_to(REPO))}
        if rows:
            sources[str(path.relative_to(REPO))] = sha256(path)
    return result, sources


def build() -> tuple[str, dict]:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_uid: dict[str, list[dict]] = defaultdict(list)
    for row in ledger["rows"]:
        by_uid[normalized_uid(row["instance_uid"])].append(row)
    schematic, sources = schematic_instances()
    missing = sorted(set(by_uid) - set(schematic))
    if missing != ["LESHY2-RF:encoder_knob"]:
        raise ValueError(f"unexpected ledger rows absent from ECAD: {missing}")
    extras = sorted(set(schematic) - set(by_uid))
    invalid_extras = [
        uid for uid in extras
        if schematic[uid].get("in_bom") is not False
        and schematic[uid].get("ledger_component") is not False
    ]
    if invalid_extras:
        raise ValueError(f"unregistered purchased schematic components: {invalid_extras}")
    reconciled = []
    for uid in sorted(set(by_uid) & set(schematic)):
        ledger_rows = by_uid[uid]
        symbol = schematic[uid]
        expected_counts = {row["physical_pcb_contact_count"] for row in ledger_rows}
        if symbol.get("pin_count") not in expected_counts:
            raise ValueError(f"{uid} physical contact mismatch: ledger={expected_counts}, symbol={symbol.get('pin_count')}")
        expected_mpns = {row["mpn"] for row in ledger_rows}
        if len(ledger_rows) == 2 and uid == "LESHY2-LORA-CAP-01:variant_module":
            if not all(mpn.rsplit("-", 1)[-1] in symbol.get("mpn", "") for mpn in expected_mpns):
                raise ValueError("LoRa regional alternative MPNs are absent from the union symbol")
            disposition = "two mutually exclusive serial assembly variants represented by one union symbol"
        else:
            if symbol.get("mpn") not in expected_mpns:
                raise ValueError(f"{uid} MPN mismatch: ledger={expected_mpns}, symbol={symbol.get('mpn')}")
            disposition = "one ledger row to one populated symbol"
        reconciled.append({
            "instance": uid,
            "ledger_rows": len(ledger_rows),
            "physical_contacts": symbol["pin_count"],
            "mpn": symbol.get("mpn"),
            "disposition": disposition,
        })
    if len(extras) != 67:
        raise ValueError(f"expected 67 non-BOM/interface-only symbols, got {len(extras)}")
    manifest = {
        "schema_version": 1,
        "stage": "H2.7.2",
        "status": "reviewed_all_physical_contacts",
        "method": "normalized ledger identity and exact MPN/physical-pin-count comparison against every populated leaf/root symbol manifest",
        "source_hashes": {str(LEDGER.relative_to(REPO)): sha256(LEDGER), **sources},
        "summary": {
            "ledger_rows": len(ledger["rows"]),
            "normalized_electrical_identities": len(by_uid),
            "reconciled_electrical_identities": len(reconciled),
            "mechanical_only_h1_items": len(missing),
            "bom_free_or_interface_only_symbols": len(extras),
            "physical_contact_mismatches": 0,
            "mpn_mismatches": 0,
        },
        "mechanical_only": [{"instance": missing[0], "rationale": "the serial encoder knob is an H1 mating body; the electrical encoder switch is separately present in RF35"}],
        "non_ledger_symbols": [{"instance": uid, "disposition": "BOM-free copper test pad" if schematic[uid].get("in_bom") is False else "factory module RF interface boundary"} for uid in extras],
        "reconciled": reconciled,
        "corrected_findings": [{
            "id": "H2.7.2-F01",
            "finding": "the instance ledger called logical-function counts physical contacts for ten expanded-pad/module cases",
            "correction": "every row now carries logical_contact_count and physical_pcb_contact_count separately; contact_count follows the actual carrier/package land count",
            "affected_classes": ["ESP32-S3 carrier", "ESP32-C5 carrier", "E01-ML01SP4 carrier", "TVS2200", "BQ25798", "CSD87313DMS", "TPUL2G223"],
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
        print(f"ok: H2.7.2 physical-contact review is current; {manifest['summary']['reconciled_electrical_identities']} identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
