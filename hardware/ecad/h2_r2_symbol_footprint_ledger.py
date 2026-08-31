#!/usr/bin/env python3
"""Build the H2-R2.1.2 exact symbol/contact/value/footprint ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-symbol-footprint-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def walk_records(value: object):
    if isinstance(value, dict):
        if value.get("mpn") and "footprint" in value:
            yield value
        for child in value.values():
            yield from walk_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_records(child)


def native_affinity_for_file(name: str, mapping: dict[str, list[str]]) -> list[str]:
    matched = [sheets for prefix, sheets in mapping.items() if name.startswith(prefix)]
    if len(matched) > 1:
        raise ValueError(f"historical hint file maps more than once: {name}")
    return matched[0] if matched else []


def collect_historical_hints(contract: dict, current_mpns: set[str]) -> tuple[dict, list]:
    candidates: dict[str, dict] = defaultdict(
        lambda: {"footprints": set(), "pin_counts": set(), "native_affinity": set(), "files": set()}
    )
    source_files: dict[Path, dict] = {}
    sheet_map = contract["legacy_sheet_to_native_affinity"]
    for pattern in contract["historical_hint_globs"]:
        for path in sorted(ROOT.glob(pattern)):
            source_files[path] = {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
                "authority": False,
                "use": "exact-MPN package-name hint only; no designator, net or sheet authority",
            }
            affinity = native_affinity_for_file(path.name, sheet_map)
            for row in walk_records(load(path)):
                mpn = row.get("mpn")
                footprint = row.get("footprint")
                if mpn not in current_mpns or not footprint:
                    continue
                candidate = candidates[mpn]
                candidate["footprints"].add(footprint)
                if isinstance(row.get("pin_count"), int):
                    candidate["pin_counts"].add(row["pin_count"])
                candidate["native_affinity"].update(affinity)
                candidate["files"].add(str(path.relative_to(ROOT)))
    normalized = {
        mpn: {
            "footprints": sorted(row["footprints"]),
            "pin_counts": sorted(row["pin_counts"]),
            "native_affinity": sorted(row["native_affinity"]),
            "files": sorted(row["files"]),
        }
        for mpn, row in candidates.items()
    }
    return normalized, [source_files[path] for path in sorted(source_files)]


def local_footprint_record(footprint: str) -> dict:
    if footprint.startswith("Leshy2:"):
        name = footprint.split(":", 1)[1]
        path = ROOT / "hardware/ecad/libraries/Leshy2.pretty" / f"{name}.kicad_mod"
        if not path.is_file():
            raise ValueError(f"controlled historical footprint is missing: {footprint}")
        return {
            "status": "existing_manufacturer_derived_definition_reconciled",
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
    if footprint.startswith("Leshy2_R2:"):
        return {
            "status": "exact_manufacturer_geometry_registered_pending_h2_r2_1_3_materialization",
            "path": None,
            "sha256": None,
        }
    return {
        "status": "exact_package_identity_mapped_to_standard_kicad_library",
        "path": None,
        "sha256": None,
    }


def build() -> dict:
    contract = load(CONTRACT)
    errors: list[str] = []
    if (
        contract.get("schema_version"),
        contract.get("marker"),
        contract.get("status"),
    ) != (
        1,
        "H2-R2.1.2",
        "reviewed_exact_symbol_contact_value_footprint_ledger",
    ):
        errors.append("symbol/footprint contract identity or status changed")

    source_records: dict[str, dict] = {}
    loaded: dict[str, dict] = {}
    for key, relative in contract.get("authority", {}).items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing current authority source: {relative}")
            continue
        source_records[key] = {"path": relative, "sha256": sha256(path)}
        loaded[key] = load(path)

    inventory = loaded.get("native_inventory", {})
    devices = loaded.get("device_register", {}).get("devices", {})
    if inventory.get("marker") != "H2-R2.1.1" or inventory.get("status") != "pass":
        errors.append("H2-R2.1.1 native inventory is not a passing input")
    groups = inventory.get("component_groups", [])
    if len(groups) != 238:
        errors.append("native component group count drifted")
    current_mpns = {row.get("mpn") for row in groups}

    try:
        hints, hint_sources = collect_historical_hints(contract, current_mpns)
    except ValueError as exc:
        errors.append(str(exc))
        hints, hint_sources = {}, []

    valid_sheets = {
        sheet["id"]
        for project in inventory.get("projects", [])
        for sheet in project.get("sheets", [])
    }
    footprint_overrides = contract.get("footprint_overrides", {})
    sheet_overrides = contract.get("sheet_affinity_overrides", {})
    rows: list[dict] = []
    historical_reconciled = 0
    historical_conflicts_resolved = 0
    new_exact_geometry = 0

    for group in groups:
        device_id = group["device_id"]
        device = devices.get(device_id)
        if not device:
            errors.append(f"device group lost current device evidence: {device_id}")
            continue
        if device.get("mpn") != group.get("mpn"):
            errors.append(f"exact MPN mismatch for {device_id}")
        contacts = device.get("contacts", {})
        is_board_component = group.get("ecad_disposition") == "schematic_component_group"
        hint = hints.get(group["mpn"], {})
        candidates = hint.get("footprints", [])

        footprint = footprint_overrides.get(group["mpn"])
        footprint_resolution = "explicit_current_override"
        if footprint is not None and len(candidates) > 1:
            historical_conflicts_resolved += 1
        if not is_board_component:
            footprint = None
            footprint_resolution = "not_applicable_off_board_or_final_assembly"
        elif footprint is None and len(candidates) == 1:
            footprint = candidates[0]
            footprint_resolution = "reconciled_exact_mpn_historical_package_hint"
            historical_reconciled += 1
        elif footprint is None and not candidates:
            errors.append(f"board component has no exact footprint identity: {device_id}")
        elif footprint is None:
            errors.append(
                f"board component has ambiguous footprint hints without override: {device_id}: {candidates}"
            )

        footprint_record = None
        if footprint:
            try:
                footprint_record = local_footprint_record(footprint)
            except ValueError as exc:
                errors.append(str(exc))
            if footprint.startswith("Leshy2_R2:"):
                new_exact_geometry += 1

        affinity = sheet_overrides.get(
            device_id,
            hint.get("native_affinity", []) + group.get("r2_sheet_assignment", []),
        )
        affinity = sorted(set(affinity))
        if not affinity:
            errors.append(f"component group has no native R2 sheet affinity: {device_id}")
        elif not set(affinity).issubset(valid_sheets):
            errors.append(f"component group has invalid native R2 sheet affinity: {device_id}")
        if is_board_component and not contacts:
            errors.append(f"board component has no exact contact map: {device_id}")

        role_counts = Counter(
            str(contact.get("role", "unspecified")) for contact in contacts.values()
        )
        row = {
            "device_id": device_id,
            "mpn": group["mpn"],
            "quantity_per_product": group["quantity_per_product"],
            "role": group["role"],
            "ecad_disposition": group["ecad_disposition"],
            "native_sheet_affinity": affinity,
            "schematic_value": device.get("kind", group["mpn"]),
            "symbol_id": f"Leshy2_R2:{device_id}" if is_board_component else None,
            "symbol_status": (
                "exact_identity_and_contact_map_registered_pending_h2_r2_1_3_materialization"
                if is_board_component
                else "not_applicable_external_or_final_assembly"
            ),
            "logical_contact_count": len(contacts),
            "contact_role_counts": dict(sorted(role_counts.items())),
            "contact_map": contacts,
            "contact_map_sha256": canonical_sha256(contacts),
            "electrical_contract_sha256": canonical_sha256(device.get("electrical_contract", {})),
            "manufacturer_evidence": device.get("source"),
            "footprint": footprint,
            "footprint_resolution": footprint_resolution,
            "footprint_definition": footprint_record,
            "historical_hint_files": hint.get("files", []),
            "historical_hint_pin_counts": hint.get("pin_counts", []),
            "jlcpcb_part_number": group.get("jlcpcb_part_number"),
        }
        rows.append(row)

    rows.sort(key=lambda row: row["device_id"])
    board_rows = [row for row in rows if row["symbol_id"]]
    external_rows = [row for row in rows if not row["symbol_id"]]
    if len(rows) != 238 or len(board_rows) != 233 or len(external_rows) != 5:
        errors.append("expected 233 board groups plus five explicit non-PCBA groups")
    if len({row["symbol_id"] for row in board_rows}) != len(board_rows):
        errors.append("symbol identities are not one-to-one with board component groups")
    if any(not row["footprint"] for row in board_rows):
        errors.append("one or more board component groups lack a footprint identity")
    if any(row["footprint"] for row in external_rows):
        errors.append("an off-board/final-assembly group incorrectly owns a PCB footprint")

    authorization = contract.get("authorization", {})
    if authorization != {
        "exact_group_ledger": True,
        "symbol_or_footprint_files": False,
        "schematic_nets": False,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }:
        errors.append("H2-R2.1.2 authorization boundary changed")

    return {
        "schema_version": 1,
        "artifact": "H2-R2-symbol-footprint-ledger",
        "marker": contract.get("marker"),
        "status": "pass" if not errors else "fail",
        "sources": source_records,
        "historical_hint_sources": hint_sources,
        "summary": {
            "component_group_count": len(rows),
            "board_component_group_count": len(board_rows),
            "explicit_non_pcba_group_count": len(external_rows),
            "symbol_identity_count": len([row for row in board_rows if row["symbol_id"]]),
            "footprint_identity_count": len([row for row in board_rows if row["footprint"]]),
            "logical_contact_count": sum(row["logical_contact_count"] for row in rows),
            "historical_package_hints_reconciled": historical_reconciled,
            "historical_package_conflicts_resolved": historical_conflicts_resolved,
            "explicit_current_footprint_overrides": sum(
                1 for row in board_rows if row["footprint_resolution"] == "explicit_current_override"
            ),
            "standard_kicad_footprint_identities": sum(
                1
                for row in board_rows
                if row["footprint_definition"]["status"]
                == "exact_package_identity_mapped_to_standard_kicad_library"
            ),
            "reconciled_local_footprint_definitions": sum(
                1
                for row in board_rows
                if row["footprint_definition"]["status"]
                == "existing_manufacturer_derived_definition_reconciled"
            ),
            "new_exact_footprint_geometries_pending_materialization": new_exact_geometry,
            "schematic_symbols_or_footprint_files_created": 0,
            "native_schematic_nets_created": 0,
            "unresolved_groups": len(errors),
        },
        "groups": rows,
        "authorization": authorization,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        return 1
    expected = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    summary = result["summary"]
    print(
        "ok: H2-R2.1.2 maps "
        f"{summary['board_component_group_count']} board groups and "
        f"{summary['explicit_non_pcba_group_count']} non-PCBA groups; "
        f"{summary['logical_contact_count']} logical contacts; zero nets/files created"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
