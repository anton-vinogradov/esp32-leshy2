#!/usr/bin/env python3
"""Materialize and audit every H2-R2.1.3 logical contact against real pads."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-contact-materialization-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-contact-materialization.json"
PAD_RE = re.compile(r'^\s*\(pad\s+(?:"([^"]*)"|([^\s()]+))\s+([^\s()]+)')
LEADING_PIN_RE = re.compile(r"^\s*(\d+(?:\s*/\s*\d+)*)")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def standard_footprint_roots() -> list[Path]:
    candidates = []
    if os.environ.get("KICAD10_FOOTPRINT_DIR"):
        candidates.append(Path(os.environ["KICAD10_FOOTPRINT_DIR"]))
    candidates.extend(
        [
            Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"),
            Path("/usr/share/kicad/footprints"),
            Path("/usr/local/share/kicad/footprints"),
        ]
    )
    return candidates


def resolve_footprint(footprint: str) -> tuple[Path | None, str]:
    library, name = footprint.split(":", 1)
    if library in {"Leshy2", "Leshy2_R2"}:
        relative = Path("hardware/ecad/libraries") / f"{library}.pretty" / f"{name}.kicad_mod"
        path = ROOT / relative
        return (path if path.is_file() else None), str(relative)
    for base in standard_footprint_roots():
        path = base / f"{library}.pretty" / f"{name}.kicad_mod"
        if path.is_file():
            return path, f"${{KICAD10_FOOTPRINT_DIR}}/{library}.pretty/{name}.kicad_mod"
    return None, f"${{KICAD10_FOOTPRINT_DIR}}/{library}.pretty/{name}.kicad_mod"


def parse_pads(path: Path) -> tuple[dict[str, dict], int]:
    pads: dict[str, dict] = {}
    ignored_unnumbered = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PAD_RE.match(line)
        if not match:
            continue
        name = match.group(1) if match.group(1) is not None else match.group(2)
        pad_type = match.group(3)
        if not name:
            ignored_unnumbered += 1
            continue
        row = pads.setdefault(name, {"occurrences": 0, "types": set()})
        row["occurrences"] += 1
        row["types"].add(pad_type)
    return {
        name: {"occurrences": row["occurrences"], "types": sorted(row["types"])}
        for name, row in sorted(pads.items())
    }, ignored_unnumbered


def automatic_pads(contact_name: str, physical: object, available: set[str]) -> tuple[list[str], str]:
    if isinstance(physical, str) and physical.strip() in available:
        return [physical.strip()], "exact_physical_pad_name"
    if isinstance(physical, str):
        match = LEADING_PIN_RE.match(physical)
        if match:
            names = [part.strip() for part in match.group(1).split("/")]
            return names, "leading_manufacturer_pin_numbers"
    if contact_name in available:
        return [contact_name], "exact_logical_pad_name"
    for prefix in ("PIN_", "END_"):
        if contact_name.startswith(prefix) and contact_name[len(prefix) :] in available:
            return [contact_name[len(prefix) :]], "normalized_logical_pin_number"
    return [], "unresolved"


def build() -> dict:
    contract = load(CONTRACT)
    errors: list[str] = []
    if (
        contract.get("schema_version"),
        contract.get("marker"),
        contract.get("status"),
    ) != (1, "H2-R2.1.3", "current_exact_contact_to_pad_materialization"):
        errors.append("contact materialization contract identity or status changed")

    source_records: dict[str, dict] = {}
    loaded: dict[str, dict] = {}
    for key, relative in contract.get("authority", {}).items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing authority source: {relative}")
            continue
        source_records[key] = {"path": relative, "sha256": sha256(path)}
        loaded[key] = load(path)

    ledger = loaded.get("exact_ledger", {})
    devices = loaded.get("device_register", {}).get("devices", {})
    if ledger.get("marker") != "H2-R2.1.2" or ledger.get("status") != "pass":
        errors.append("H2-R2.1.2 exact ledger is not a passing input")

    overrides = contract.get("contact_to_pad_overrides", {})
    external = contract.get("external_interfaces", {})
    mechanical = contract.get("mechanical_only_pads", {})
    allowed_shared = contract.get("allowed_shared_electrical_pads", {})
    rows: list[dict] = []
    external_contact_count = 0
    mapped_contact_count = 0
    footprint_pad_occurrence_count = 0
    named_footprint_pad_count = 0
    mechanical_pad_occurrence_count = 0
    ignored_unnumbered_pad_occurrence_count = 0

    board_rows = [row for row in ledger.get("groups", []) if row.get("symbol_id")]
    for ledger_row in board_rows:
        device_id = ledger_row["device_id"]
        device = devices.get(device_id, {})
        contacts = device.get("contacts", {})
        if contacts != ledger_row.get("contact_map"):
            errors.append(f"contact evidence drifted after H2-R2.1.2: {device_id}")

        footprint_path, footprint_source = resolve_footprint(ledger_row["footprint"])
        if footprint_path is None:
            errors.append(f"missing selected footprint file: {device_id}: {ledger_row['footprint']}")
            pads = {}
            ignored_unnumbered = 0
            footprint_hash = None
        else:
            pads, ignored_unnumbered = parse_pads(footprint_path)
            footprint_hash = sha256(footprint_path)
        available = set(pads)
        footprint_pad_occurrence_count += sum(row["occurrences"] for row in pads.values())
        named_footprint_pad_count += len(pads)
        ignored_unnumbered_pad_occurrence_count += ignored_unnumbered

        contact_rows = []
        claimed_by: dict[str, list[str]] = defaultdict(list)
        for contact_name, contact in contacts.items():
            external_description = external.get(device_id, {}).get(contact_name)
            if external_description:
                contact_rows.append(
                    {
                        "contact": contact_name,
                        "role": contact.get("role"),
                        "physical": contact.get("physical"),
                        "disposition": "external_on_module_interface",
                        "pads": [],
                        "resolution": "explicit_external_interface",
                        "interface": external_description,
                    }
                )
                external_contact_count += 1
                continue

            if contact_name in overrides.get(device_id, {}):
                selected = overrides[device_id][contact_name]
                resolution = "explicit_contact_to_pad_override"
            else:
                selected, resolution = automatic_pads(
                    contact_name, contact.get("physical"), available
                )
            missing = sorted(set(selected) - available)
            if not selected:
                errors.append(f"unresolved logical contact: {device_id}/{contact_name}")
            if missing:
                errors.append(
                    f"logical contact maps to absent pad(s): {device_id}/{contact_name}: {missing}"
                )
            for pad in selected:
                if pad in available:
                    claimed_by[pad].append(contact_name)
            contact_rows.append(
                {
                    "contact": contact_name,
                    "role": contact.get("role"),
                    "physical": contact.get("physical"),
                    "disposition": "pcb_footprint_pad",
                    "pads": selected,
                    "resolution": resolution,
                }
            )
            mapped_contact_count += 1

        mechanical_names = mechanical.get(device_id, [])
        missing_mechanical = sorted(set(mechanical_names) - available)
        if missing_mechanical:
            errors.append(f"declared mechanical pad absent: {device_id}: {missing_mechanical}")
        for pad in mechanical_names:
            if pad in pads:
                mechanical_pad_occurrence_count += pads[pad]["occurrences"]
        unclaimed = sorted(available - set(claimed_by) - set(mechanical_names))
        if unclaimed:
            errors.append(f"named footprint pads are unclaimed: {device_id}: {unclaimed}")

        shared_actual = {
            pad: sorted(names) for pad, names in claimed_by.items() if len(names) > 1
        }
        shared_expected = {
            pad: sorted(names) for pad, names in allowed_shared.get(device_id, {}).items()
        }
        if shared_actual != shared_expected:
            errors.append(
                f"shared electrical pad allowance mismatch: {device_id}: "
                f"actual={shared_actual}, allowed={shared_expected}"
            )

        rows.append(
            {
                "device_id": device_id,
                "mpn": ledger_row["mpn"],
                "symbol_id": ledger_row["symbol_id"],
                "footprint": ledger_row["footprint"],
                "footprint_source": footprint_source,
                "footprint_sha256": footprint_hash,
                "logical_contact_count": len(contacts),
                "footprint_named_pad_count": len(pads),
                "footprint_pad_occurrence_count": sum(
                    row["occurrences"] for row in pads.values()
                ),
                "ignored_unnumbered_pad_occurrence_count": ignored_unnumbered,
                "pad_inventory": pads,
                "contacts": contact_rows,
                "mechanical_only_pads": mechanical_names,
                "shared_electrical_pads": shared_actual,
            }
        )

    used_overrides = set(overrides) | set(external) | set(mechanical) | set(allowed_shared)
    board_ids = {row["device_id"] for row in board_rows}
    stale_contract_ids = sorted(used_overrides - board_ids)
    if stale_contract_ids:
        errors.append(f"contract references non-board device groups: {stale_contract_ids}")
    if len(board_rows) != 232:
        errors.append("expected exactly 232 board component groups")
    logical_contact_count = sum(row["logical_contact_count"] for row in rows)
    source_ledger_contact_count = ledger.get("summary", {}).get("logical_contact_count")
    if logical_contact_count != 1519 or source_ledger_contact_count != 1578:
        errors.append(
            "expected 1519 board contacts inside the reviewed 1578-contact total ledger"
        )
    if mapped_contact_count + external_contact_count != logical_contact_count:
        errors.append("contact disposition accounting does not balance")

    authorization = contract.get("authorization", {})
    expected_authorization = {
        "exact_contact_materialization": True,
        "footprint_files": True,
        "symbol_library": False,
        "schematic_nets": False,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }
    if authorization != expected_authorization:
        errors.append("H2-R2.1.3 contact-materialization authorization boundary changed")

    rows.sort(key=lambda row: row["device_id"])
    return {
        "schema_version": 1,
        "artifact": "H2-R2-contact-materialization",
        "marker": contract.get("marker"),
        "status": "pass" if not errors else "fail",
        "sources": source_records,
        "kicad_reference_version": contract.get("kicad_reference_version"),
        "summary": {
            "board_component_group_count": len(rows),
            "source_ledger_logical_contact_count": source_ledger_contact_count,
            "board_logical_contact_count": logical_contact_count,
            "pcb_footprint_contact_count": mapped_contact_count,
            "external_on_module_interface_count": external_contact_count,
            "named_footprint_pad_count": named_footprint_pad_count,
            "footprint_pad_occurrence_count": footprint_pad_occurrence_count,
            "mechanical_only_pad_occurrence_count": mechanical_pad_occurrence_count,
            "ignored_unnumbered_pad_occurrence_count": ignored_unnumbered_pad_occurrence_count,
            "new_exact_footprint_files_materialized": len(
                contract.get("new_local_footprint_geometry", {})
            ),
            "native_schematic_nets_created": 0,
            "unresolved_error_count": len(errors),
        },
        "new_local_footprint_geometry": contract.get("new_local_footprint_geometry", {}),
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
        "ok: H2-R2.1.3 materializes "
        f"{summary['board_logical_contact_count']} board contacts across "
        f"{summary['board_component_group_count']} groups; "
        f"{summary['external_on_module_interface_count']} external interfaces; zero errors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
