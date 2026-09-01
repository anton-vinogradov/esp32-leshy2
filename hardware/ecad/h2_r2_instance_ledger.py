#!/usr/bin/env python3
"""Allocate the exact H2-R2.1.3 fitted instance ledger without copying R1 nets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-instance-ledger-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
VALID_INSTANCE = re.compile(r"^[a-z][a-z0-9_]*$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_names(role: str, quantity: int) -> list[str]:
    names = [part.strip() for part in role.split(",")]
    if len(names) == quantity and all(VALID_INSTANCE.fullmatch(name) for name in names):
        return names
    return []


def expand_rp_prefix(names: list[str], do_not_expand: set[str]) -> list[str]:
    result = []
    for name in names:
        if name in do_not_expand:
            result.append(name)
            continue
        if name == "rp":
            result += ["hub_rp", "rf_rp"]
        elif name.startswith("rp_"):
            suffix = name[3:]
            result += [f"hub_rp_{suffix}", f"rf_rp_{suffix}"]
        else:
            result.append(name)
    return result


def project_for_sheet(sheet: str) -> str:
    if sheet.startswith("UI_"):
        return "LESHY2-UI-R2"
    if sheet.startswith("RF_"):
        return "LESHY2-RF-R2"
    raise ValueError(f"sheet has no native project: {sheet}")


def inferred_sheet(instance: str, allowed: list[str]) -> str | None:
    rules = [
        (("hub_rp",), "UI_30_HUB_RP_CORE_SERVICE"),
        (("rf_rp",), "RF_10_RP2354_CORE_SERVICE"),
        (("s3_", "display_", "touch_", "backlight_", "lcd_"), "UI_10_S3_DISPLAY_TOUCH"),
        (("c5_", "ir_"), "UI_20_C5_WIFI_IR_SERVICE"),
        (("nrf", "det_nrf"), "UI_31_NRF24_X3_TX_EVIDENCE"),
        (("sd_", "ui_", "encoder", "ptt", "f1", "f2", "back", "opt"), "UI_11_STORAGE_CONTROLS_INDICATORS"),
        (("cc_", "voice_", "voice_v_", "det_cc", "det_voice"), "RF_20_CC1101_VOICE_TX"),
        (("receiver_", "airband_", "air_", "si_"), "RF_21_BROADCAST_AIRBAND_RX"),
        (("audio_", "codec_", "speaker", "microphone", "headset_", "headphone_"), "RF_22_AUDIO_CODEC_IO"),
        (("u214_", "unit_", "ext_", "cap_"), "RF_30_U214_U219_M5_EXT"),
        (("pack_", "safety_", "hub_safe_i2c", "aon_"), "RF_02_PACK_SAFETY_AON"),
        (("pd_", "charger_", "product_usb_"), "RF_01_USB_PD_CHARGE"),
        (("main_", "power_", "voice_efuse", "ext_buck"), "RF_03_MAIN_RAILS_DOMAIN_GATES"),
    ]
    for prefixes, sheet in rules:
        if instance.startswith(prefixes) and sheet in allowed:
            return sheet
    return None


def reference_prefix(device_id: str, footprint: str) -> str:
    library = footprint.split(":", 1)[0]
    if library.startswith("Resistor"):
        return "R"
    if library.startswith("Capacitor"):
        return "C"
    if library.startswith("Inductor"):
        return "L"
    if library.startswith("Crystal"):
        return "Y"
    if library.startswith(("Diode", "LED")) or device_id.startswith("vishay_vsm"):
        return "D"
    if library.startswith("Connector") or any(
        token in device_id
        for token in ("gct_rfpc", "gct_usb", "hirose_", "jae_", "samtec_", "seeed_1125")
    ):
        return "J"
    if library.startswith(("Button_Switch", "Rotary_Encoder")) or device_id.startswith(
        ("alps_", "ck_js", "omron_")
    ):
        return "SW"
    if "fuse" in device_id or device_id.startswith("littelfuse_045"):
        return "F"
    if device_id.startswith(("diodes_2n", "diodes_dmn", "diodes_mmbt")):
        return "Q"
    if device_id == "keystone_1048p":
        return "BT"
    if device_id == "pui_as02404po":
        return "LS"
    if device_id == "same_sky_cmej_0413_42_smt_tr":
        return "MK"
    return "U"


def build() -> dict:
    contract = load(CONTRACT)
    errors = []
    sources = {}
    loaded = {}
    for key, relative in contract["authority"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing current instance authority: {relative}")
            continue
        sources[key] = {"path": relative, "sha256": sha256(path), "authority": True}
        loaded[key] = load(path)
    historical_path = ROOT / contract["historical_hints"]["instance_ledger"]
    if not historical_path.is_file():
        errors.append("missing historical instance-name hint ledger")
        historical = []
    else:
        sources["historical_instance_hints"] = {
            "path": contract["historical_hints"]["instance_ledger"],
            "sha256": sha256(historical_path),
            "authority": False,
        }
        historical = load(historical_path).get("rows", [])

    inventory = loaded.get("native_inventory", {})
    definitions = loaded.get("exact_definition_ledger", {})
    if inventory.get("status") != "pass" or definitions.get("status") != "pass":
        errors.append("one or more current R2 instance prerequisites are not passing")
    definition_rows = {row["device_id"]: row for row in definitions.get("groups", []) if row.get("symbol_id")}
    old_by_device = defaultdict(list)
    old_by_device_instance = {}
    for row in historical:
        if row.get("electrical_disposition") != "board_fitted_component":
            continue
        old_by_device[row["device_key"]].append(row["instance"])
        old_by_device_instance[(row["device_key"], row["instance"])] = row

    exact_names = contract.get("exact_instance_names", {})
    additions = contract.get("additional_instance_names", {})
    replacements = contract.get("replace_instance_names", {})
    removals = contract.get("remove_historical_instances", {})
    expand_groups = set(contract.get("expand_historical_rp_prefix_for", []))
    do_not_expand = set(contract.get("do_not_expand_historical_rp_instances", []))
    sheet_overrides = contract.get("instance_sheet_overrides", {})
    sheet_map = contract["former_sheet_map"]
    rows = []
    reconciliation_counts = Counter()
    for group in inventory.get("component_groups", []):
        if group.get("ecad_disposition") != "schematic_component_group":
            continue
        device_id = group["device_id"]
        quantity = group["quantity_per_product"]
        if device_id not in definition_rows:
            errors.append(f"instance group lacks current symbol definition: {device_id}")
            continue
        if device_id in exact_names:
            names = exact_names[device_id]
            origin = "explicit_current_r2_allocation"
        else:
            names = role_names(group.get("role", ""), quantity)
            origin = "exact_current_role_list"
            if not names:
                names = [
                    name for name in old_by_device.get(device_id, [])
                    if name not in set(removals.get(device_id, []))
                ]
                if device_id in expand_groups:
                    names = expand_rp_prefix(names, do_not_expand)
                origin = "reconciled_historical_instance_name_hint"
        device_replacements = replacements.get(device_id, {})
        stale_replacements = sorted(set(device_replacements) - set(names))
        if stale_replacements:
            errors.append(
                f"stale current-R2 instance replacements: {device_id}: "
                f"{stale_replacements}"
            )
        names = [device_replacements.get(name, name) for name in names]
        names += additions.get(device_id, [])
        if additions.get(device_id):
            origin = "current_r2_allocation_with_explicit_additions"
        elif device_replacements:
            origin = "current_r2_allocation_with_explicit_replacement"
        if len(names) != quantity:
            errors.append(
                f"instance allocation count mismatch: {device_id}: {len(names)} != {quantity}"
            )
        if len(names) != len(set(names)) or not all(VALID_INSTANCE.fullmatch(name) for name in names):
            errors.append(f"invalid or duplicate local instance names: {device_id}")
        allowed_sheets = definition_rows[device_id]["native_sheet_affinity"]
        for instance in names:
            sheet = sheet_overrides.get(instance)
            if sheet is not None and sheet not in allowed_sheets:
                errors.append(
                    f"instance sheet override is outside current affinity: "
                    f"{device_id}/{instance}: {sheet} not in {allowed_sheets}"
                )
                continue
            historical_name = instance
            if instance.startswith("rf_rp_"):
                historical_name = "rp_" + instance[len("rf_rp_") :]
            old = old_by_device_instance.get((device_id, historical_name))
            if old and sheet is None:
                mapped = sheet_map.get(old["sheet"])
                if mapped in allowed_sheets:
                    sheet = mapped
                    reconciliation_counts["former_sheet_hint_reconciled"] += 1
            if sheet is None:
                sheet = inferred_sheet(instance, allowed_sheets)
            if sheet is None and len(allowed_sheets) == 1:
                sheet = allowed_sheets[0]
            if sheet is None:
                errors.append(
                    f"ambiguous native sheet allocation: {device_id}/{instance}: {allowed_sheets}"
                )
                continue
            rows.append(
                {
                    "instance_uid": f"{project_for_sheet(sheet)}:{instance}",
                    "instance": instance,
                    "project": project_for_sheet(sheet),
                    "sheet": sheet,
                    "device_id": device_id,
                    "mpn": group["mpn"],
                    "symbol_id": definition_rows[device_id]["symbol_id"],
                    "footprint": definition_rows[device_id]["footprint"],
                    "reference_prefix": reference_prefix(
                        device_id, definition_rows[device_id]["footprint"]
                    ),
                    "allocation_origin": origin,
                    "historical_topology_authority": False,
                }
            )
            reconciliation_counts[origin] += 1

    duplicate_local = [
        key for key, count in Counter((row["project"], row["instance"]) for row in rows).items()
        if count > 1
    ]
    if duplicate_local:
        errors.append(f"duplicate project-local instance names: {duplicate_local}")
    rows.sort(key=lambda row: (row["project"], row["sheet"], row["instance"]))
    counters = defaultdict(Counter)
    for row in rows:
        counters[row["project"]][row["reference_prefix"]] += 1
        row["reference"] = f"{row['reference_prefix']}{counters[row['project']][row['reference_prefix']]}"
    if len(rows) != 1183:
        errors.append(f"expected 1183 fitted board instances, got {len(rows)}")
    project_counts = Counter(row["project"] for row in rows)
    project_graph_sheet_count = sum(
        len(project.get("sheets", [])) for project in inventory.get("projects", [])
    )
    if project_graph_sheet_count != 22:
        errors.append(f"native project graph sheet count changed: {project_graph_sheet_count}")
    if set(project_counts) != {"LESHY2-UI-R2", "LESHY2-RF-R2"}:
        errors.append(f"native project coverage changed: {dict(project_counts)}")
    authorization = contract.get("authorization", {})
    if authorization != {
        "native_instance_ledger": True,
        "native_schematic_nets": False,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }:
        errors.append("native instance authorization boundary changed")
    return {
        "schema_version": 1,
        "artifact": "H2-R2-native-instance-ledger",
        "marker": contract.get("marker"),
        "status": "pass" if not errors else "fail",
        "sources": sources,
        "summary": {
            "fitted_board_instance_count": len(rows),
            "component_group_count": len(set(row["device_id"] for row in rows)),
            "project_counts": dict(sorted(project_counts.items())),
            "project_graph_sheet_count": project_graph_sheet_count,
            "populated_sheet_count": len(set(row["sheet"] for row in rows)),
            "sheet_counts": dict(sorted(Counter(row["sheet"] for row in rows).items())),
            "allocation_origins": dict(sorted(Counter(row["allocation_origin"] for row in rows).items())),
            "former_sheet_hints_reconciled": reconciliation_counts["former_sheet_hint_reconciled"],
            "native_schematic_nets_created": 0,
            "errors": len(errors),
        },
        "rows": rows,
        "authorization": authorization,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
        print(f"stale: {OUTPUT.relative_to(ROOT)}")
        return 1
    print("ok: 1183 exact fitted R2 instances across 2 native projects and 22 sheets; zero nets created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
