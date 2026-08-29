#!/usr/bin/env python3
"""Generate and verify the H2 production-schematic input ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from h2_dual_nmos import DEVICE_KEY as DUAL_NMOS_DEVICE_KEY, validate_dual_nmos


REPO = Path(__file__).resolve().parents[2]
DEVICES = REPO / "hardware/architecture/devices.json"
SOURCE_TABLE = REPO / "hardware/product-design/generated/H1-physical-source-table.json"
PLAN = REPO / "hardware/ecad/h2-schematic-plan.json"
SHEET_CONTRACT = REPO / "hardware/ecad/H2-sheet-contract.json"
OUTPUT = REPO / "hardware/ecad/generated/H2-instance-ledger.json"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
LORA_CAP = REPO / "hardware/accessories/leshy2-lora-cap-01.json"
HWFW_INPUT = REPO / "hardware/architecture/target-integration-contract.json"
HWFW_OUTPUT = REPO / "hardware/ecad/generated/H2-hwfw-contract.json"


EXTERNAL_ASSEMBLIES = {
    "display",
    "display_touch_controller",
    "encoder_knob",
    "pack_cell0",
    "pack_cell1",
    "u214",
}
INTERCONNECT_ASSEMBLIES = {
    "c5_rf_jumper",
    "s3_rf_jumper",
    "nrf0_rf_jumper",
    "nrf1_rf_jumper",
    "nrf2_rf_jumper",
    "speaker",
}
FIRMWARE_DOMAINS = {
    "s3": "S3",
    "c5": "C5",
    "rp": "RP",
    "pack_admission": "PACK",
    "safety_controller": "SAFETY",
}

# These outward connectors moved between the two PCB faces in the current R2
# H1 placement.  This generator deliberately preserves the reviewed R1 H2
# ledger as historical evidence; the new R2 H2 starts only after H1 acceptance.
R2_H1_REPARTITIONED_EXTERNALS = {
    "nrf0_external_sma",
    "nrf1_external_sma",
    "nrf2_external_sma",
    "receiver_fmsw_external_sma",
    "receiver_amlw_external_sma",
}
R2_H1_REPLACED_MPNS = {
    "display",
    "display_panel_connector",
    "nrf0",
    "nrf1",
    "nrf2",
}

# These order codes are the same physical Hirose receptacle and land pattern;
# only reel presentation differs.  Keep the historical physical registration
# valid while every current electrical/BOM derivative names the stocked code.
PHYSICALLY_EQUIVALENT_MPN_PAIRS = {
    frozenset({"Hirose U.FL-R-SMT-1(10)", "Hirose U.FL-R-SMT-1(80)"}),
}


def physical_mpn_is_equivalent(left: str, right: str) -> bool:
    return left == right or frozenset({left, right}) in PHYSICALLY_EQUIVALENT_MPN_PAIRS


def contact_counts(device: dict) -> tuple[int, int]:
    """Return logical functions and actual carrier/package lands separately."""
    logical = len(device.get("contacts", []))
    physical = device.get("pcb_pad_contract", {}).get(
        "pad_count", device.get("physical_pcb_contact_count", logical)
    )
    if not isinstance(physical, int) or physical < 0:
        raise ValueError(f"invalid physical PCB contact count for {device.get('mpn')}: {physical}")
    return logical, physical


def sheet_for(instance: str, frame: str) -> str:
    if frame == "display-adapter":
        return "ADP_00_DISPLAY_ADAPTER"
    if instance in {"product_usb_dp_series", "product_usb_dm_series"}:
        return "UI_10_S3_CORE_MEMORY_BOOT"
    if instance in {
        "microphone_bias_filter_res", "microphone_bias_filter_cap",
        "microphone_bias_res", "voice_rx_coupling", "voice_rx_series",
        "voice_rx_bias",
    }:
        return "UI_13_AUDIO_CODEC_HEADSET"
    if instance == "s3_reset_gate_pullup":
        return "UI_50_TX_SAFETY_EVIDENCE"
    if instance.startswith("safe_c5_"):
        return "UI_50_TX_SAFETY_EVIDENCE"
    if instance in {
        "s3_tx_led", "c5_tx_led", "nrf0_tx_led", "nrf1_tx_led", "nrf2_tx_led",
        "cc_tx_led", "voice_tx_led", "ir_tx_led", "ext_tx_led",
        "fault_led",
    } or instance.endswith("_tx_led_series") or instance in {
        "fault_led_series",
    }:
        return "UI_12_CONTROLS_INDICATORS"
    if instance.startswith(("slow_io_", "front_function_")):
        return "UI_12_CONTROLS_INDICATORS"
    if instance.startswith(("touch_", "display_", "backlight_", "sd_", "lcd_")):
        return "UI_11_DISPLAY_TOUCH_STORAGE"
    if instance.startswith(("receiver_", "si_audio_")):
        return "UI_21_FM_AM_RECEIVER"
    if instance.startswith(("codec_", "audio_", "headset_", "headphone_", "mic_tx_")):
        return "UI_13_AUDIO_CODEC_HEADSET"
    if instance.startswith(("speaker_input_", "speaker_output_", "speaker_amp_", "microphone_bias_")):
        return "RF_36_AUDIO_IO_AMP"
    if instance.startswith(("rear_control_", "encoder_ptt_", "ptt_")):
        return "RF_35_REAR_CONTROLS"
    if instance.startswith(("encoder_a_", "encoder_b_")):
        return "UI_12_CONTROLS_INDICATORS"
    if instance.startswith(("s3_evidence_", "c5_evidence_", "ir_evidence_")) or instance in {
        "evidence_cmp_a", "evidence_cmp_a_bypass", "det_s3", "det_c5", "det_ir",
    }:
        return "UI_50_TX_SAFETY_EVIDENCE"
    if instance.startswith(("nrf0_evidence_", "nrf1_evidence_", "nrf2_evidence_", "cc_evidence_", "voice_evidence_", "voice_v_evidence_")) or instance.startswith("evidence_") or instance in {
        "evidence_cmp_b", "evidence_cmp_voice", "det_nrf0", "det_nrf1", "det_nrf2",
        "det_cc", "det_voice", "det_voice_v", "any_tx_aon_pullup", "fault_assert_pullup",
    }:
        return "RF_50_TX_SAFETY_EVIDENCE"
    if instance.startswith(("s3_detector_",)):
        return "UI_10_S3_CORE_MEMORY_BOOT"
    if instance.startswith(("c5_detector_", "ir_detector_")):
        return "UI_20_C5_RADIO_IR_SERVICE"
    if instance.startswith(("nrf0_detector_", "nrf1_detector_", "nrf2_detector_")):
        return "RF_31_NRF24_X3"
    if instance.startswith(("cc_detector_", "voice_detector_")):
        return "RF_32_SUBGHZ_VOICE"
    if instance.startswith(("sys_i2c_", "sys_int_")):
        return "UI_10_S3_CORE_MEMORY_BOOT"
    if instance.startswith(("power_command_", "run_loop_", "power_fault_", "fault_assert_")):
        return "RF_50_TX_SAFETY_EVIDENCE"
    if instance.startswith(("power_zone_temp_", "rf_zone_temp_")):
        return "RF_03_MAIN_RAILS_DOMAIN_GATES"
    if instance in {"display", "display_touch_controller", "display_connector"}:
        return "UI_11_DISPLAY_TOUCH_STORAGE"
    if instance == "sd":
        return "UI_11_DISPLAY_TOUCH_STORAGE"
    if (
        instance.startswith("ui_")
        or instance.endswith("_tx_led")
    ):
        return "UI_12_CONTROLS_INDICATORS"
    if instance == "slow_io":
        return "UI_12_CONTROLS_INDICATORS"
    if instance in {"encoder", "encoder_knob", "ptt_switch"}:
        return "RF_35_REAR_CONTROLS"
    if instance in {
        "audio_speaker_selector", "codec", "codec_i2s_din_boot_gate",
        "headphone_jack", "headset_control_io",
    }:
        return "UI_13_AUDIO_CODEC_HEADSET"
    if instance in {"microphone", "speaker", "speaker_amp"}:
        return "RF_36_AUDIO_IO_AMP"
    if instance.startswith("s3"):
        return "UI_10_S3_CORE_MEMORY_BOOT"
    if instance.startswith("c5") or instance.startswith("ir_"):
        return "UI_20_C5_RADIO_IR_SERVICE"
    if instance.startswith("rp"):
        return "RF_30_RP2354_CORE_SERVICE"
    if instance.startswith("nrf"):
        return "RF_31_NRF24_X3"
    if instance.startswith("cc") or instance.startswith("voice"):
        return "RF_32_SUBGHZ_VOICE"
    if instance == "receiver" or instance.startswith("receiver_"):
        return "UI_21_FM_AM_RECEIVER"
    if instance.startswith("u214") or instance.startswith("unit_"):
        return "RF_34_U214_M5_EXT"
    if instance.startswith("m1_"):
        return "UI_40_INTERBOARD_M1" if frame.startswith("ui-") else "RF_40_INTERBOARD_M1"
    if instance.startswith(("product_usb", "pd_", "charger_", "nvdc_")):
        return "RF_01_USB_PD_CHARGE"
    if instance.startswith(("pack_",)):
        return "RF_02_PACK_SAFETY_AON"
    if instance.startswith(("main_", "ext_", "aon_")) or instance in {
        "power_zone_ntc", "rf_zone_ntc", "ui_zone_ntc",
    }:
        return "RF_03_MAIN_RAILS_DOMAIN_GATES"
    if instance.startswith(("safe_", "safety_", "evidence_")) or instance == "power_command_switch":
        return "UI_50_TX_SAFETY_EVIDENCE" if frame.startswith("ui-") else "RF_50_TX_SAFETY_EVIDENCE"
    raise ValueError(f"no H2 sheet owner for {instance!r} in {frame!r}")


def board_for(instance: str, frame: str) -> str:
    if frame == "display-adapter":
        return "display-adapter"
    if instance in EXTERNAL_ASSEMBLIES:
        return "external-mating-product"
    if frame.startswith("ui-") or frame in {"front-outer", "display-assembly"}:
        return "ui-control-pcb"
    if frame.startswith("rf-") or frame == "rear-outer":
        return "rf-power-pcb"
    raise ValueError(f"no H2 board owner for {instance!r} in {frame!r}")


def disposition_for(instance: str) -> str:
    if instance in EXTERNAL_ASSEMBLIES:
        return "external_mating_product_interface_only"
    if instance in INTERCONNECT_ASSEMBLIES:
        return "fitted_interconnect_assembly"
    return "board_fitted_component"


def project_and_board_for_sheet(sheet: str) -> tuple[str, str]:
    if sheet.startswith("UI_"):
        return "LESHY2-UI", "ui-control-pcb"
    if sheet.startswith("RF_"):
        return "LESHY2-RF", "rf-power-pcb"
    if sheet.startswith("ADP_"):
        return "L2-DISP-ADP-001-A", "display-adapter"
    if sheet.startswith("CAP_"):
        return "LESHY2-LORA-CAP-01", "lora-cap-pcb"
    raise ValueError(f"unknown sheet/project boundary: {sheet}")


def cap_sheet_for(instance: str) -> str:
    if instance == "cap_header":
        return "CAP_00_ROOT"
    if instance == "variant_module" or instance.startswith("rf_"):
        return "CAP_10_RADIO_CONTROL"
    if instance.startswith("evidence_"):
        return "CAP_30_TX_EVIDENCE"
    if instance.startswith(("local_regulator", "identity")) or instance == "radio_bulk":
        return "CAP_20_POWER_BUS"
    raise ValueError(f"no LoRa-Cap sheet owner for {instance}")


def validate_sheet_contract(plan: dict, contract: dict, rows: list[dict]) -> None:
    if contract.get("stage") != "H2.0.2" or contract.get("status") != "reviewed":
        raise ValueError("H2.0.2 sheet contract must be reviewed before later schematic work")
    if contract.get("project_model") != "one_independent_kicad_project_per_pcb":
        raise ValueError("each physical PCB must retain its own KiCad project")
    rules = contract.get("rules", {})
    if not rules.get("one_physical_pcb_per_project") or rules.get("sheet_may_span_multiple_pcbs"):
        raise ValueError("sheet/project physical-boundary rules are not closed")
    if rules.get("hidden_global_labels_across_projects"):
        raise ValueError("cross-project nets may not depend on hidden global labels")

    binding = contract.get("inventory_binding", {})
    if binding.get("status") != "reviewed_against_complete_h2_0_1_inventory":
        raise ValueError("H2.0.2 must be bound to the complete H2.0.1 inventory")
    if binding.get("source_schema_version") != 2:
        raise ValueError("H2.0.2 inventory binding requires ledger schema 2")
    if binding.get("registered_inventory_rows") != len(rows):
        raise ValueError("H2.0.2 inventory row count has drifted")
    project_counts = {
        project: sum(row["project"] == project for row in rows)
        for project in {row["project"] for row in rows}
    }
    if binding.get("project_row_counts") != project_counts:
        raise ValueError("H2.0.2 per-project inventory counts have drifted")
    sheet_counts = {
        sheet: sum(row["sheet"] == sheet for row in rows)
        for sheet in {row["sheet"] for row in rows}
    }
    if binding.get("sheet_row_counts") != sheet_counts:
        raise ValueError("H2.0.2 per-sheet inventory counts have drifted")

    contract_graphs = {
        project["id"]: project["sheets"] for project in contract.get("projects", [])
    }
    if contract_graphs != plan.get("proposed_sheet_graphs"):
        raise ValueError("H2 plan and reviewed sheet graphs have drifted")
    all_sheets = {
        sheet for project_sheets in contract_graphs.values() for sheet in project_sheets
    }
    used_sheets = {row["sheet"] for row in rows}
    if not used_sheets <= all_sheets:
        raise ValueError(f"ledger uses sheets absent from H2.0.2: {sorted(used_sheets - all_sheets)}")
    intentional_empty = set(binding.get("intentionally_component_empty_sheets", {}))
    if all_sheets - used_sheets != intentional_empty:
        raise ValueError("H2.0.2 empty-sheet disposition has drifted")
    if {item.get("id") for item in contract.get("cross_project_contracts", [])} != {
        "M1", "DISPLAY_ADAPTER_40", "CAP_BUS_14"
    }:
        raise ValueError("all three physical cross-project connector contracts are required")


def validate_main_cross_project_routes(candidate: dict, rows: list[dict]) -> None:
    """Reject hidden UI↔RF nets that are absent from the physical M1 map."""
    project_by_instance = {
        row["instance"]: row["project"]
        for row in rows
        if row["project"] in {"LESHY2-UI", "LESHY2-RF"}
    }
    pin_map = candidate["interboard_contract"]["pin_map"]
    m1_nets = {row["net"] for row in pin_map}
    hidden = []
    for route in candidate["fixed_routes"]:
        source = route["from"].split(".", 1)[0]
        target = route["to"].split(".", 1)[0]
        if (
            source in project_by_instance
            and target in project_by_instance
            and project_by_instance[source] != project_by_instance[target]
            and route["net"] not in m1_nets
        ):
            hidden.append(
                f"{route['net']} ({source}:{project_by_instance[source]} -> "
                f"{target}:{project_by_instance[target]})"
            )
    if hidden:
        raise ValueError("cross-project fixed routes missing from M1: " + "; ".join(hidden))

    required_front_evidence = {
        "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2",
        "EV_N5_CC", "EV_N6_VOICE", "EV_N8_LORA_EXT",
    }
    if not required_front_evidence <= m1_nets:
        raise ValueError("all six RF-board front-indicator evidence nets must cross M1")
    if any(row["signal_class"] == "reserved" for row in pin_map):
        raise ValueError("M1 has no silent reserve after front TX-evidence closure")
    main_contacts = sum(row["net"] == "3V3_MAIN" for row in pin_map)
    accounting = candidate["interboard_contract"]["accounting"]
    if main_contacts != 7 or accounting["main_3v3_contacts"] != 7:
        raise ValueError("M1 must retain seven paralleled 3V3_MAIN contacts")
    if accounting["reserved"] != 0 or accounting["maximum_nominal_main_contact_capacity_a"] != 2.8:
        raise ValueError("M1 evidence/power accounting has drifted")


def build() -> dict:
    devices = json.loads(DEVICES.read_text(encoding="utf-8"))["devices"]
    source = json.loads(SOURCE_TABLE.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    sheet_contract = json.loads(SHEET_CONTRACT.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    lora_cap = json.loads(LORA_CAP.read_text(encoding="utf-8"))
    physical_by_instance = {row["instance"]: row for row in source["rows"]}
    dual_nmos = validate_dual_nmos(candidate, devices)
    rows = []

    for instance, device_key in candidate["instances"].items():
        physical = physical_by_instance.get(instance)
        frame = physical["frame"] if physical else ""
        device = devices[device_key]
        sheet = sheet_for(instance, frame)
        project, sheet_board = project_and_board_for_sheet(sheet)
        contacts = device.get("contacts", [])
        logical_contacts, physical_contacts = contact_counts(device)
        disposition = disposition_for(instance)
        board = (
            "external-mating-product"
            if disposition == "external_mating_product_interface_only"
            else sheet_board
        )
        physical_mpn_drift = physical and not physical_mpn_is_equivalent(
            physical["mpn"], device["mpn"]
        )
        if physical_mpn_drift and instance not in R2_H1_REPLACED_MPNS:
            raise ValueError(f"H1/device MPN drift for {instance}")
        physical_board_drift = physical and board_for(instance, frame) != board
        if physical_board_drift and instance not in R2_H1_REPARTITIONED_EXTERNALS:
            raise ValueError(f"H1 physical board drift for {instance}")
        rows.append(
            {
                "instance_uid": f"{project}:{instance}",
                "instance": instance,
                "project": project,
                "device_key": device_key,
                "mpn": device["mpn"],
                "role": physical["role"] if physical else device["kind"],
                "board": board,
                "sheet": sheet,
                "electrical_disposition": disposition,
                "physical_registration": (
                    "h1_r2_supersedes_historical_h2"
                    if physical_board_drift or physical_mpn_drift
                    else "h1_dimensioned_body" if physical else "schematic_only_body"
                ),
                "contact_count": physical_contacts,
                "logical_contact_count": logical_contacts,
                "physical_pcb_contact_count": physical_contacts,
                "contact_evidence_status": (
                    "registered_exact_contact_map" if contacts else "no_device_contact_map"
                ),
                "symbol_source_status": (
                    "interface_symbol_required_during_h2_2_to_h2_4"
                    if disposition == "external_mating_product_interface_only"
                    else "exact_symbol_mapping_required_during_h2_2_to_h2_4"
                ),
                "footprint_source_status": (
                    "no_product_footprint_interface_only"
                    if disposition == "external_mating_product_interface_only"
                    else (
                        "assembly_no_single_footprint"
                        if disposition == "fitted_interconnect_assembly"
                        else "exact_footprint_mapping_required_during_h2_2_to_h2_4"
                    )
                ),
                "manufacturer_evidence": {
                    "document": device["source"]["document"],
                    "version": device["source"].get("version", "current controlled source"),
                    "url": device["source"]["url"],
                    "checked": device["source"]["checked"],
                },
            }
        )
        if device_key == DUAL_NMOS_DEVICE_KEY:
            rows[-1]["physical_pin_to_contact"] = dual_nmos["physical_pin_to_contact"]
            rows[-1]["channel_to_net"] = dual_nmos["instances"][instance]

    for instance, device_key in lora_cap["common_instances"].items():
        device = devices[device_key]
        logical_contacts, physical_contacts = contact_counts(device)
        sheet = cap_sheet_for(instance)
        project, board = project_and_board_for_sheet(sheet)
        rows.append(
            {
                "instance_uid": f"{project}:COMMON:{instance}",
                "instance": instance,
                "project": project,
                "assembly_variant": "COMMON",
                "device_key": device_key,
                "mpn": device["mpn"],
                "role": device["kind"],
                "board": board,
                "sheet": sheet,
                "electrical_disposition": "board_fitted_component",
                "physical_registration": "accessory_schematic_body",
                "contact_count": physical_contacts,
                "logical_contact_count": logical_contacts,
                "physical_pcb_contact_count": physical_contacts,
                "contact_evidence_status": "registered_exact_contact_map",
                "symbol_source_status": "exact_symbol_mapping_required_during_h2_4",
                "footprint_source_status": "exact_footprint_mapping_required_during_h2_4",
                "manufacturer_evidence": {
                    "document": device["source"]["document"],
                    "version": device["source"].get("version", "current controlled source"),
                    "url": device["source"]["url"],
                    "checked": device["source"]["checked"],
                },
            }
        )
    for variant, variant_data in lora_cap["variants"].items():
        device_key = variant_data["module"]
        device = devices[device_key]
        logical_contacts, physical_contacts = contact_counts(device)
        sheet = cap_sheet_for("variant_module")
        project, board = project_and_board_for_sheet(sheet)
        rows.append(
            {
                "instance_uid": f"{project}:{variant}:variant_module",
                "instance": "variant_module",
                "project": project,
                "assembly_variant": variant,
                "device_key": device_key,
                "mpn": device["mpn"],
                "role": device["kind"],
                "board": board,
                "sheet": sheet,
                "electrical_disposition": "board_fitted_component_alternative",
                "physical_registration": "accessory_variant_schematic_body",
                "contact_count": physical_contacts,
                "logical_contact_count": logical_contacts,
                "physical_pcb_contact_count": physical_contacts,
                "contact_evidence_status": "registered_exact_contact_map",
                "symbol_source_status": "exact_symbol_mapping_required_during_h2_4",
                "footprint_source_status": "exact_footprint_mapping_required_during_h2_4",
                "manufacturer_evidence": {
                    "document": device["source"]["document"],
                    "version": device["source"].get("version", "current controlled source"),
                    "url": device["source"]["url"],
                    "checked": device["source"]["checked"],
                },
            }
        )

    validate_sheet_contract(plan, sheet_contract, rows)
    validate_main_cross_project_routes(candidate, rows)
    if len(main_rows := [row for row in rows if row["project"] != "LESHY2-LORA-CAP-01"]) != len(candidate["instances"]):
        raise ValueError("main H2 inventory must cover every candidate instance exactly once")
    instance_uids = [row["instance_uid"] for row in rows]
    if len(instance_uids) != len(set(instance_uids)):
        raise ValueError("H2 inventory instance UIDs must be globally unique")
    sheets = sorted({row["sheet"] for row in rows})
    cap_rows = [row for row in rows if row["project"] == "LESHY2-LORA-CAP-01"]
    return {
        "schema_version": 2,
        "stage": "H2.0.1",
        "status": "reviewed_complete_circuit_inventory",
        "authority": {"baseline": "R1", "lifecycle": "historical_pre_r2_sheet_scaffold", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "generated_from": [
            str(DEVICES.relative_to(REPO)),
            str(SOURCE_TABLE.relative_to(REPO)),
            str(PLAN.relative_to(REPO)),
            str(SHEET_CONTRACT.relative_to(REPO)),
            str(CANDIDATE.relative_to(REPO)),
            str(LORA_CAP.relative_to(REPO)),
        ],
        "authorization": plan["authorization"],
        "summary": {
            "registered_inventory_rows": len(rows),
            "main_candidate_instances": len(main_rows),
            "lora_cap_common_instances": len(lora_cap["common_instances"]),
            "lora_cap_alternative_module_instances": len(lora_cap["variants"]),
            "h1_dimensioned_instances": sum(
                row["physical_registration"] == "h1_dimensioned_body" for row in main_rows
            ),
            "h1_r2_superseded_historical_instances": sum(
                row["physical_registration"] == "h1_r2_supersedes_historical_h2"
                for row in main_rows
            ),
            "schematic_only_main_instances": sum(
                row["physical_registration"] == "schematic_only_body" for row in main_rows
            ),
            "main_board_fitted_components": sum(
                row["electrical_disposition"] == "board_fitted_component" for row in main_rows
            ),
            "main_fitted_interconnect_assemblies": sum(
                row["electrical_disposition"] == "fitted_interconnect_assembly" for row in main_rows
            ),
            "main_external_mating_products": sum(
                row["electrical_disposition"] == "external_mating_product_interface_only" for row in main_rows
            ),
            "lora_cap_rows": len(cap_rows),
            "lora_cap_components_per_assembled_variant": len(lora_cap["common_instances"]) + 1,
            "owning_sheets_used": len(sheets),
            "rows_without_mpn": sum(not row["mpn"] for row in rows),
            "rows_without_manufacturer_evidence": sum(
                not row["manufacturer_evidence"]["url"] for row in rows
            ),
            "rows_without_sheet_owner": 0,
        },
        "sheet_owners_used": sheets,
        "exact_dual_nmos_pinout": dual_nmos,
        "rows": rows,
    }


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_hwfw_export() -> dict:
    devices = json.loads(DEVICES.read_text(encoding="utf-8"))["devices"]
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    integration = json.loads(HWFW_INPUT.read_text(encoding="utf-8"))
    sheet_contract = json.loads(SHEET_CONTRACT.read_text(encoding="utf-8"))

    if integration.get("contract_id") != "LESHY2-HWFW-1":
        raise ValueError("unexpected HW/FW integration contract identity")
    controllers = {row["instance"]: row for row in integration.get("controllers", [])}
    if set(controllers) != set(FIRMWARE_DOMAINS):
        raise ValueError("HW/FW export must contain the five firmware domains exactly once")

    allocations = {instance: [] for instance in FIRMWARE_DOMAINS}
    seen_contacts: set[tuple[str, str]] = set()
    for allocation in candidate["allocations"]:
        instance = allocation["instance"]
        if instance not in allocations:
            continue
        identity = (instance, allocation["contact"])
        if identity in seen_contacts:
            raise ValueError(f"duplicate programmable contact allocation: {identity}")
        seen_contacts.add(identity)
        allocations[instance].append(dict(allocation))

    bsp_domains = []
    for instance, domain in FIRMWARE_DOMAINS.items():
        controller = controllers[instance]
        device = devices[candidate["instances"][instance]]
        if controller["domain"] != domain or controller["mpn"] != device["mpn"]:
            raise ValueError(f"controller identity drift for {domain}")
        bsp_domains.append(
            {
                "domain": domain,
                "instance": instance,
                "mpn": device["mpn"],
                "allocated_contact_count": len(allocations[instance]),
                "pins": allocations[instance],
            }
        )

    service = integration.get("physical_service", {})
    if len(service.get("external_usb", [])) != 3:
        raise ValueError("exactly three external USB ports are required")
    if len(service.get("external_side_controls", [])) != 6:
        raise ValueError("all six externally labelled RST/BOOT controls are required")
    if len(service.get("internal_fallback_headers", [])) != 3:
        raise ValueError("all three internal DBG10 fallback headers are required")
    for row in service["external_side_controls"] + service["internal_fallback_headers"]:
        device = devices[candidate["instances"][row["instance"]]]
        if row["mpn"] != device["mpn"]:
            raise ValueError(f"service MPN drift for {row['instance']}")

    project_graphs = {
        project["id"]: project["sheets"] for project in sheet_contract["projects"]
    }
    return {
        "schema_version": 1,
        "stage": "H2.0.3",
        "status": "reviewed_historical_r1_hwfw_export",
        "export_id": "LESHY2-H2-HWFW-1",
        "authority": {
            "generation": "historical_single_rp_r1",
            "review_evidence_preserved": True,
            "current_r2_authority": False,
            "superseded_by": "hardware/architecture/h0-r2-rebaseline.json",
            "reason": "five domains, one RP and the old M1 cannot represent current six-domain/two-RP H0-R2",
            "r2_kicad_started": False,
        },
        "generated_from": [
            str(path.relative_to(REPO))
            for path in (DEVICES, CANDIDATE, HWFW_INPUT, SHEET_CONTRACT)
        ],
        "source_sha256": {
            str(path.relative_to(REPO)): source_sha256(path)
            for path in (DEVICES, CANDIDATE, HWFW_INPUT, SHEET_CONTRACT)
        },
        "integration_contract": integration,
        "bsp": {
            "pin_source": "hardware/architecture/candidates/G2F-3I.json#/allocations",
            "temporary_pin_assignments_allowed": False,
            "domains": bsp_domains,
            "total_allocated_contacts": sum(
                domain["allocated_contact_count"] for domain in bsp_domains
            ),
        },
        "schematic_projects": project_graphs,
        "drift_policy": {
            "firmware_canonical_copy": "config/hardware_bsp_contract.json",
            "firmware_integration_view": "config/hardware_integration_contract.json",
            "comparison": "byte-stable canonical JSON after generation",
            "failure": "block firmware F2 and hardware H2.7 until regenerated in both repositories",
        },
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(build())
    hwfw_content = render(build_hwfw_export())
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
        HWFW_OUTPUT.write_text(hwfw_content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        print(f"wrote {HWFW_OUTPUT.relative_to(REPO)}")
        return 0
    stale = []
    for path, expected in ((OUTPUT, content), (HWFW_OUTPUT, hwfw_content)):
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            stale.append(path)
    if stale:
        for path in stale:
            print(f"stale: {path.relative_to(REPO)}")
        return 1
    print("ok: H2 schematic input ledger and HW/FW export are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
