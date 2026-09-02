#!/usr/bin/env python3
"""Validate and publish the H2-R2.1.1 native source/sheet/component inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-native-inventory-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-inventory.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_authority(path: Path) -> dict | list[dict]:
    if path.suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    return load(path)


def r2_cost_base_rows(historical_rows: list[dict], model: dict) -> list[dict]:
    """Build the pre-H2 R2 component ledger without reading generated H2 output.

    The cost report consumes the native inventory, so the native inventory must
    not consume the generated cost report in return.  This projection keeps the
    historical G2F BOM plus the accepted H1 R2 replacements, additions and
    quantity overrides as the stable, acyclic 221-group base.
    """
    replacements = model.get("r2_device_replacements", {})
    overrides = model.get("r2_quantity_overrides", {})
    rows: list[dict] = []
    for historical in historical_rows:
        row = dict(historical)
        replacement = replacements.get(row["device_id"])
        if replacement:
            row["historical_capture_route"] = row["device_id"]
            row["device_id"] = replacement["device_id"]
            row["mpn"] = replacement["mpn"]
        quantity = int(row["quantity"])
        if row["device_id"] in overrides:
            quantity = int(overrides[row["device_id"]]["quantity_per_device"])
        rows.append({
            "scope": row["scope"],
            "device_id": row["device_id"],
            "mpn": row["mpn"],
            "quantity_per_device": quantity,
            "role": row.get("placements", row["device_id"]),
            "historical_capture_route": row.get("historical_capture_route"),
        })
    for addition in model.get("r2_additional_groups", []):
        rows.append({
            "scope": addition["scope"],
            "device_id": addition["device_id"],
            "mpn": addition["mpn"],
            "quantity_per_device": int(addition["quantity"]),
            "role": addition.get("placements", addition["device_id"]),
            "historical_capture_route": None,
        })
    return rows


def antenna_rows(antenna_model: dict) -> list[dict]:
    grouped: dict[str, dict] = {}
    for item in antenna_model.get("items", []):
        prices = [
            value for key, value in item.get("availability", {}).items()
            if key.startswith("unit_price_usd") and value is not None
        ]
        price = float(prices[0]) if prices else None
        row = grouped.setdefault(item["mpn"], {
            "codes": [],
            "mpn": item["mpn"],
            "quantity": 0,
            "known_line_usd": 0.0 if price is not None else None,
            "profiles": [],
        })
        row["codes"].append(item["kit_code"])
        row["profiles"].append(item["profile"])
        row["quantity"] += int(item["quantity"])
        if price is None:
            row["known_line_usd"] = None
        elif row["known_line_usd"] is not None:
            row["known_line_usd"] += price * int(item["quantity"])
    return [
        {
            "code": ", ".join(row["codes"]),
            "mpn": row["mpn"],
            "quantity": row["quantity"],
            "known_line_usd": row["known_line_usd"],
            "profile": " / ".join(dict.fromkeys(row["profiles"])),
        }
        for row in grouped.values()
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jlc_number(row: dict, device: dict) -> str | None:
    if row.get("jlcpcb_part"):
        return row["jlcpcb_part"]
    text = json.dumps(device.get("orderable_source", {}), ensure_ascii=False)
    match = re.search(r"\bC\d{3,}\b", text)
    return match.group(0) if match else None


def build() -> dict:
    contract = load(CONTRACT)
    errors: list[str] = []
    if (contract.get("schema_version"), contract.get("marker"), contract.get("status")) != (
        1,
        "H2-R2.1.1",
        "reviewed_source_sheet_component_inventory",
    ):
        errors.append("native inventory identity/status changed")

    sources: dict[str, dict] = {}
    loaded: dict[str, dict] = {}
    for key, relative in contract.get("authority", {}).items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing authority source: {relative}")
            continue
        sources[key] = {"path": relative, "sha256": sha256(path)}
        loaded[key] = load_authority(path)

    h0 = loaded.get("functional", {})
    pins = loaded.get("pin_map", {})
    physical = loaded.get("physical", {})
    devices = loaded.get("device_register", {}).get("devices", {})
    cost_model = loaded.get("r2_cost_model", {})
    c5 = loaded.get("c5_mux_and_service_vbus", {})
    pack = loaded.get("pack_safety_boundary", {})
    power = loaded.get("power_cell", {})
    u219 = loaded.get("u214_u219", {})
    freeze = loaded.get("freeze_new_parts", {})

    domain_ids = [row.get("id") for row in h0.get("compute_domains", [])]
    if domain_ids != ["s3", "c5", "rf_rp", "hub_rp", "pack", "safety"]:
        errors.append("functional authority is not the exact six-domain R2 model")
    if pins.get("marker") != "H1-R2.31" or pins.get("authority_chain", {}).get("remaining_h2_gates") != []:
        errors.append("pin authority is not the closed H1-R2.31 map")
    if physical.get("marker") != "H1-R2.38" or physical.get("status") != "reviewed":
        errors.append("physical authority is not reviewed H1-R2.38")
    if c5.get("production_mux_route", {}).get("selection_status") != "accepted":
        errors.append("H2-R2.0.1 live C5 mux route is not accepted")
    if c5.get("ownership", {}).get("detector_latch_implementation", {}).get("selection_status") != "accepted":
        errors.append("H2-R2.0.2 service-VBUS implementation is not accepted")
    if (
        pack.get("status") != "reviewed_exact_factory_placeable_boundary"
        or pack.get("buffer", {}).get("mpn") != "TCA9803DGKR"
        or pack.get("buffer", {}).get("jlcpcb_part_number") != "C2687966"
    ):
        errors.append("H2-R2.0.3 exact Pack/Safety boundary is not reviewed")
    if (
        power.get("main_power_cell", {}).get("converter", {}).get("mpn") != "TPS566231PRQFR"
        or power.get("main_power_cell", {}).get("inductor", {}).get("mpn") != "PSPMAA0605H-2R2M-ANP"
    ):
        errors.append("accepted H1-R2 main power cell is not present")
    if u219.get("status") != "paper_architecture_accepted__pcb_vna_hil_open":
        errors.append("accepted H1-R2 U219 support circuit is not present")
    frozen_mpns = {row.get("mpn") for row in freeze.get("parts", [])}
    required_frozen_mpns = {
        "TPS566231PRQFR", "PSPMAA0605H-2R2M-ANP", "CL10B105KO8NNNC",
        "CL05B104KB5NNNC", "SN74CBTLV1G125DCKR", "SN74LVC1G06DCKR",
        "BAT54S,215", "LMV331IDBVR", "0402WGF1001TCE", "0402WGF1002TCE",
        "0402WGF1003TCE", "0402WGF1004TCE", "GRM155R71H103KA88D",
        "CC0402KRX7R9BB104", "RC0402JR-070RL",
    }
    if frozen_mpns != required_frozen_mpns or not all(freeze.get("checks", {}).values()):
        errors.append("new power/U219 groups lack an exact passing JLCPCB architecture-freeze recheck")

    projects = contract.get("projects", [])
    project_ids = [row.get("id") for row in projects]
    if project_ids != ["LESHY2-UI-R2", "LESHY2-RF-R2"]:
        errors.append("native R2 must contain exactly the two product PCBs")
    sheets = [sheet for project in projects for sheet in project.get("sheets", [])]
    sheet_ids = [row.get("id") for row in sheets]
    if len(sheet_ids) != 22 or len(sheet_ids) != len(set(sheet_ids)):
        errors.append("native R2 sheet inventory must contain 22 unique sheets")
    source_keys = set(contract.get("authority", {}))
    for sheet in sheets:
        if not set(sheet.get("sources", [])).issubset(source_keys):
            errors.append(f"{sheet.get('id')} references an unknown authority source")
    domain_owners: list[str] = []
    for sheet in sheets:
        if sheet.get("domain_owner"):
            domain_owners.append(sheet["domain_owner"])
        domain_owners.extend(sheet.get("domain_owners", []))
    if domain_owners != ["s3", "c5", "hub_rp", "pack", "safety", "rf_rp"]:
        errors.append("each of the six compute domains must have exactly one owning native sheet")
    if any("LORA-CAP" in project_id for project_id in project_ids):
        errors.append("native R2 may not manufacture the historical custom LoRa-Cap PCB")

    base_rows = r2_cost_base_rows(loaded.get("component_groups", []), cost_model)
    component_contract = contract.get("component_inventory", {})
    if len(base_rows) != component_contract.get("base_group_count"):
        errors.append("base exact component-group count drifted")
    if sum(row.get("quantity_per_device", 0) for row in base_rows) != component_contract.get("base_quantity_per_product"):
        errors.append("base per-product component quantity drifted")

    rows: dict[str, dict] = {}
    non_pcba = component_contract.get("non_pcba_dispositions", {})
    for row in base_rows:
        device_id = row.get("device_id")
        device = devices.get(device_id)
        if not device:
            errors.append(f"component group missing from device register: {device_id}")
            continue
        if device.get("mpn") != row.get("mpn"):
            errors.append(f"exact MPN drift for {device_id}")
        rows[device_id] = {
            "device_id": device_id,
            "mpn": row.get("mpn"),
            "quantity_per_product": row.get("quantity_per_device"),
            "scope": row.get("scope"),
            "role": row.get("role"),
            "ecad_disposition": non_pcba.get(device_id, "schematic_component_group"),
            "qualification": device.get("qualification"),
            "lifecycle": device.get("lifecycle"),
            "contact_evidence": bool(device.get("contacts")),
            "jlcpcb_part_number": jlc_number(row, device),
            "accepted_identity_source": "hardware/architecture/devices.json",
            "historical_cost_route_only": row.get("historical_capture_route"),
            "bom_excluded": bool(device.get("bom_excluded", False)),
        }

    adjustment_sheets: dict[str, list[str]] = {}
    for adjustment in component_contract.get("adjustments", []):
        device_id = adjustment["device_id"]
        if device_id not in rows:
            errors.append(f"adjustment targets missing group: {device_id}")
            continue
        rows[device_id]["quantity_per_product"] += adjustment["quantity_delta"]
        owners = adjustment.get("sheets", [adjustment.get("sheet")])
        adjustment_sheets.setdefault(device_id, []).extend(owner for owner in owners if owner)
        rows[device_id]["r2_adjustment"] = adjustment["reason"]

    new_group_sheets: dict[str, list[str]] = {}
    for addition in component_contract.get("new_groups", []):
        device_id = addition["device_id"]
        if device_id in rows:
            errors.append(f"new component group duplicates base group: {device_id}")
            continue
        device = devices.get(device_id)
        if not device:
            errors.append(f"new component group missing from device register: {device_id}")
            continue
        rows[device_id] = {
            "device_id": device_id,
            "mpn": device.get("mpn"),
            "quantity_per_product": addition["quantity"],
            "scope": "base_product",
            "role": addition.get("role", "H2-R2.0.3 exact Pack/Safety powered-off boundary"),
            "ecad_disposition": "schematic_component_group",
            "qualification": device.get("qualification"),
            "lifecycle": device.get("lifecycle"),
            "contact_evidence": bool(device.get("contacts")),
            "jlcpcb_part_number": jlc_number({}, device),
            "accepted_identity_source": addition.get("identity_source", "hardware/architecture/pack-safety-i2c-boundary-contract.json"),
            "historical_cost_route_only": None,
            "bom_excluded": bool(device.get("bom_excluded", False)),
        }
        new_group_sheets.setdefault(device_id, []).append(addition["sheet"])

    valid_sheets = set(sheet_ids)
    for device_id, owners in {**adjustment_sheets, **new_group_sheets}.items():
        if not set(owners).issubset(valid_sheets):
            errors.append(f"{device_id} has an invalid R2 sheet assignment")
        rows[device_id]["r2_sheet_assignment"] = owners

    component_rows = sorted(rows.values(), key=lambda row: row["device_id"])
    if len(component_rows) != component_contract.get("expected_group_count"):
        errors.append("final exact component-group count drifted")
    if sum(row["quantity_per_product"] for row in component_rows) != component_contract.get("expected_quantity_per_product"):
        errors.append("final per-product component quantity drifted")
    if any(
        not row["contact_evidence"]
        for row in component_rows
        if row["ecad_disposition"] == "schematic_component_group"
    ):
        errors.append("one or more exact component groups lost contact evidence")

    exact_pack_groups = {
        row["device_id"]: row for row in component_rows
        if row["device_id"] in {
            "ti_tca9803_dgkr",
            "uniroyal_0402wgf2201tce",
            "samsung_cl05a105ka5nqnc",
            "samsung_cl05b104ko5nnnc",
        }
    }
    expected_pack_quantities = {
        "ti_tca9803_dgkr": 1,
        "uniroyal_0402wgf2201tce": 25,
        "samsung_cl05a105ka5nqnc": 7,
        "samsung_cl05b104ko5nnnc": 2,
    }
    if {key: row["quantity_per_product"] for key, row in exact_pack_groups.items()} != expected_pack_quantities:
        errors.append("Pack/Safety component delta is incomplete")

    authorization = contract.get("authorization", {})
    if authorization != {
        "native_source_and_sheet_inventory": True,
        "schematic_symbols_or_nets": False,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }:
        errors.append("H2-R2.1.1 authorization boundary changed")

    antennas = antenna_rows(loaded.get("antennas", {}))
    return {
        "schema_version": 1,
        "artifact": "H2-R2-native-inventory",
        "marker": contract.get("marker"),
        "status": "pass" if not errors else "fail",
        "sources": sources,
        "projects": projects,
        "summary": {
            "project_count": len(projects),
            "sheet_count": len(sheet_ids),
            "domain_count": len(domain_ids),
            "component_group_count": len(component_rows),
            "component_quantity_per_product": sum(row["quantity_per_product"] for row in component_rows),
            "external_antenna_group_count": len(antennas),
            "external_antenna_count": sum(row.get("quantity", 0) for row in antennas),
            "unresolved_pre_ecad_prerequisites": len(pins.get("authority_chain", {}).get("remaining_h2_gates", [])),
            "native_schematic_symbols_created": 0,
            "native_schematic_nets_created": 0,
        },
        "component_groups": component_rows,
        "external_antenna_kit": antennas,
        "historical_quarantine": contract.get("historical_quarantine"),
        "route_freshness": contract.get("route_freshness"),
        "authorization": authorization,
        "errors": errors,
    }


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


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
    print(
        "ok: H2-R2.1.1 freezes 2 native projects, 22 sheets, 6 domains, "
        f"{result['summary']['component_group_count']} exact component groups and {result['summary']['component_quantity_per_product']} per-product positions; no symbols or nets created"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
