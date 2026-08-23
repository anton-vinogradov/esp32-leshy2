#!/usr/bin/env python3
"""Validate architecture source data and generate its review ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ARCH_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARCH_DIR.parents[1]
DEVICE_FILE = ARCH_DIR / "devices.json"
CANDIDATE_DIR = ARCH_DIR / "candidates"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=reject_duplicate_keys)


def load_sources() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    database = load_json(DEVICE_FILE)
    candidates = [load_json(path) for path in sorted(CANDIDATE_DIR.glob("*.json"))]
    return database, candidates


def natural_contact_key(contact: str) -> tuple[str, int, str]:
    match = re.fullmatch(r"([A-Za-z_]+)(\d+)", contact)
    if match:
        return match.group(1), int(match.group(2)), contact
    return contact, -1, contact


def _check_endpoint(
    endpoint: str,
    candidate_id: str,
    instances: dict[str, str],
    devices: dict[str, Any],
    errors: list[str],
    context: str,
) -> None:
    if endpoint.startswith("abstract:"):
        return
    if "." not in endpoint:
        errors.append(f"{candidate_id}: {context}: malformed endpoint {endpoint!r}")
        return
    instance, contact = endpoint.split(".", 1)
    if instance not in instances:
        errors.append(f"{candidate_id}: {context}: unknown instance {instance!r}")
        return
    device = devices[instances[instance]]
    if contact not in device.get("contacts", {}):
        errors.append(
            f"{candidate_id}: {context}: {endpoint} is not exposed by {device['mpn']}"
        )


def validate_sources(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    devices = database.get("devices", {})
    if database.get("schema_version") != 1:
        errors.append("devices.json: unsupported schema_version")
    if not devices:
        errors.append("devices.json: no devices")

    for device_id, device in devices.items():
        for required in ("mpn", "kind", "qualification", "lifecycle", "source", "contacts"):
            if required not in device:
                errors.append(f"device {device_id}: missing {required}")
        contacts = device.get("contacts", {})
        if len(contacts) != len(set(contacts)):
            errors.append(f"device {device_id}: duplicate contact")
        for contact, attributes in contacts.items():
            if not attributes.get("physical") or not attributes.get("role"):
                errors.append(f"device {device_id}.{contact}: incomplete physical contact")
        allocatable_contacts = device.get("allocatable_contacts", [])
        if len(allocatable_contacts) != len(set(allocatable_contacts)):
            errors.append(f"device {device_id}: duplicate allocatable contact")
        for contact in allocatable_contacts:
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown allocatable contact {contact}")
        for contact in device.get("strapping_contacts", []):
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown strap contact {contact}")
        for contact in device.get("service_required", []):
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown service contact {contact}")
        for contact in device.get("service_required_all", []):
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown mandatory service contact {contact}")
        for alternative_number, alternative in enumerate(device.get("service_required_any", []), 1):
            if not alternative:
                errors.append(f"device {device_id}: empty service alternative {alternative_number}")
            for contact in alternative:
                if contact not in contacts:
                    errors.append(
                        f"device {device_id}: unknown service-alternative contact {contact}"
                    )
        if device.get("programmable") and not device.get("controller_capabilities"):
            errors.append(f"device {device_id}: programmable device lacks controller_capabilities")
        capabilities = set(device.get("controller_capabilities", []))
        window_group_controllers: set[str] = set()
        for group_number, group in enumerate(device.get("controller_gpio_window_groups", []), 1):
            context = f"device {device_id}: GPIO-window group {group_number}"
            group_controllers = group.get("controllers", [])
            if not group.get("id") or not group_controllers or not group.get("allowed_windows"):
                errors.append(f"{context}: missing id, controllers or allowed_windows")
            unknown = set(group_controllers) - capabilities
            if unknown:
                errors.append(f"{context}: unknown controllers {sorted(unknown)}")
            duplicates = set(group_controllers) & window_group_controllers
            if duplicates:
                errors.append(f"{context}: controllers repeated across groups {sorted(duplicates)}")
            window_group_controllers.update(group_controllers)
            for window in group.get("allowed_windows", []):
                if (
                    not isinstance(window, list)
                    or len(window) != 2
                    or not all(isinstance(bound, int) for bound in window)
                    or window[0] > window[1]
                ):
                    errors.append(f"{context}: invalid allowed window {window!r}")
        if "not_recommended" in device.get("lifecycle", "") and not device.get("lifecycle_source"):
            errors.append(f"device {device_id}: constrained lifecycle lacks lifecycle_source")
        cost = device.get("cost")
        cost_gate = device.get("cost_gate")
        if cost is not None and cost_gate is not None:
            errors.append(f"device {device_id}: cost and cost_gate are mutually exclusive")
        if cost is not None:
            for required in (
                "currency",
                "target_quantity",
                "unit_price_usd",
                "price_break",
                "source",
            ):
                if required not in cost:
                    errors.append(f"device {device_id}: cost missing {required}")
            if cost.get("currency") != "USD":
                errors.append(f"device {device_id}: cost currency must be USD")
            if cost.get("target_quantity") != 100:
                errors.append(f"device {device_id}: cost target quantity must be 100")
            unit_price = cost.get("unit_price_usd")
            if (
                isinstance(unit_price, bool)
                or not isinstance(unit_price, (int, float))
                or unit_price <= 0
            ):
                errors.append(f"device {device_id}: cost unit price must be positive")
            source = cost.get("source")
            if not isinstance(source, dict):
                errors.append(f"device {device_id}: cost source must be an object")
            else:
                for required in ("document", "url", "checked"):
                    if not source.get(required):
                        errors.append(
                            f"device {device_id}: cost source missing {required}"
                        )
                if source.get("url") and not source["url"].startswith("https://"):
                    errors.append(f"device {device_id}: cost source must use HTTPS")
                if source.get("checked") and not re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}", source["checked"]
                ):
                    errors.append(
                        f"device {device_id}: cost source checked date must be YYYY-MM-DD"
                    )
        if cost_gate is not None:
            if not isinstance(cost_gate, dict):
                errors.append(f"device {device_id}: cost_gate must be an object")
            else:
                for required in ("status", "reason", "source"):
                    if not cost_gate.get(required):
                        errors.append(f"device {device_id}: cost_gate missing {required}")
                allowed_cost_gate_statuses = {
                    "quantity_100_rfq_required",
                    "retail_only_no_quantity_100_tier",
                    "regional_retail_only_no_quantity_100_tier",
                    "standalone_raw_assembly_rfq_required",
                }
                if (
                    cost_gate.get("status")
                    and cost_gate["status"] not in allowed_cost_gate_statuses
                ):
                    errors.append(f"device {device_id}: unknown cost_gate status")
                gate_source = cost_gate.get("source")
                if not isinstance(gate_source, dict):
                    errors.append(f"device {device_id}: cost_gate source must be an object")
                else:
                    for required in ("document", "url", "checked"):
                        if not gate_source.get(required):
                            errors.append(
                                f"device {device_id}: cost_gate source missing {required}"
                            )
                    if gate_source.get("url") and not gate_source["url"].startswith(
                        "https://"
                    ):
                        errors.append(
                            f"device {device_id}: cost_gate source must use HTTPS"
                        )
                    if gate_source.get("checked") and not re.fullmatch(
                        r"\d{4}-\d{2}-\d{2}", gate_source["checked"]
                    ):
                        errors.append(
                            f"device {device_id}: cost_gate source checked date must be YYYY-MM-DD"
                        )

    candidate_ids: set[str] = set()
    for candidate in candidates:
        candidate_id = candidate.get("id", "<missing-id>")
        if candidate_id in candidate_ids:
            errors.append(f"duplicate candidate id {candidate_id}")
        candidate_ids.add(candidate_id)
        if candidate.get("schema_version") != 1:
            errors.append(f"{candidate_id}: unsupported schema_version")
        if not candidate.get("decisive_open_risk"):
            errors.append(f"{candidate_id}: missing decisive_open_risk")

        if candidate.get("status") == "target_architecture_pre_schematic_reviewed":
            review = candidate.get("pre_schematic_review", {})
            if review.get("status") != "reviewed":
                errors.append(f"{candidate_id}: pre-schematic review status is not reviewed")
            if review.get("result") != "coherent_target_architecture":
                errors.append(f"{candidate_id}: pre-schematic review result is not coherent")
            if review.get("kicad_authorization") != "not_granted_by_this_review":
                errors.append(f"{candidate_id}: review must not imply KiCad authorization")
            for field in ("scope", "open_evidence_is_not_an_architecture_decision"):
                values = review.get(field, [])
                if not isinstance(values, list) or not values or any(
                    not isinstance(value, str) or not value.strip() for value in values
                ):
                    errors.append(f"{candidate_id}: invalid pre-schematic review {field}")

        interboard = candidate.get("interboard_contract")
        if interboard is not None:
            connector = interboard.get("connector_pair", {})
            pin_map = interboard.get("pin_map", [])
            accounting = interboard.get("accounting", {})
            positions = connector.get("positions")
            contacts = [row.get("contact") for row in pin_map]
            if positions != 80 or accounting.get("positions") != 80:
                errors.append(f"{candidate_id}: M1 must retain the reviewed 80-position budget")
            if contacts != list(range(1, 81)):
                errors.append(f"{candidate_id}: M1 contacts must cover ordered physical positions 1..80 exactly once")
            reserved = sum(row.get("signal_class") == "reserved" for row in pin_map)
            if reserved != accounting.get("reserved"):
                errors.append(f"{candidate_id}: M1 reserved-contact accounting is inconsistent")
            instances = candidate.get("instances", {})
            expected_connectors = {
                connector.get("ui_instance"): "hirose_fx8c_80p_sv1_92",
                connector.get("rf_power_instance"): "hirose_fx8c_80s_sv5_92",
            }
            for instance, device_id in expected_connectors.items():
                if not instance or instances.get(instance) != device_id:
                    errors.append(f"{candidate_id}: M1 connector instance {instance!r} must be {device_id}")
                elif devices[device_id]["electrical_contract"]["positions"] != positions:
                    errors.append(f"{candidate_id}: M1 device/contact budget mismatch at {instance}")
            required_nets = {
                "S3_RP_IPC_CS_N", "S3_RP_IPC_SCK", "S3_RP_IPC_MOSI",
                "S3_RP_IPC_MISO", "RP_ALERT_N", "S3_USB_DM", "S3_USB_DP",
                "SYS_I2C_SDA", "SYS_I2C_SCL", "SYS_INT_N", "RUN_PERMIT",
                "RF_RESET_KILL_GATE", "S3_RESET_KILL_GATE",
                "UI_ENCODER_PUSH_N", "ENCODER_A", "ENCODER_B",
                "FAULT_LATCH_SENSE_AON", "UI_ZONE_TEMP_ADC", "EV_N0_S3", "EV_N1_C5",
                "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2", "EV_N5_CC",
                "EV_N6_VOICE", "EV_N8_LORA_EXT",
                "EV_N7_IR", "C5_RF_TX_EVIDENCE_N", "IR_TX_EVIDENCE_N",
                "RX_SA518_AFOUT_ISOLATED", "VOICE_MIC_SELECTED_MAIN", "MIC_RAW",
                "SPEAKER_SELECTED_P", "SPEAKER_SELECTED_N", "SPEAKER_AMP_EN", "3V3_MAIN",
                "AON_SAFE_3V3", "POWER_GROUND", "SAFETY_GROUND", "AUDIO_GROUND",
            }
            mapped_nets = {row.get("net") for row in pin_map}
            missing = required_nets - mapped_nets
            if missing:
                errors.append(f"{candidate_id}: M1 misses required cross-board nets {sorted(missing)}")
            forbidden = {
                "USB_C_VBUS_RAW", "PD_PPHV", "PROTECTED_PACK_POSITIVE",
                "IR_TX_CARRIER", "S3_DETECT_V", "C5_DETECT_V", "IR_DETECT_V",
                "NRF0_DETECT_V", "NRF1_DETECT_V", "NRF2_DETECT_V",
                "CC_DETECT_V", "VOICE_DETECT_V", "SPEAKER_BTL_P", "SPEAKER_BTL_N",
            }
            leaked = forbidden & mapped_nets
            if leaked:
                errors.append(f"{candidate_id}: M1 carries forbidden power/analog/high-slew nets {sorted(leaked)}")
            if sum(row.get("net") == "3V3_MAIN" for row in pin_map) != 7:
                errors.append(f"{candidate_id}: M1 must retain seven paralleled 3V3_MAIN contacts")

        antenna_policy = candidate.get("antenna_policy", {})
        expected_antenna_policy = {
            "decision": "DEC-0048",
            "exact_count_decision": "DEC-0049",
            "external_connector_decision": "DEC-0050",
            "kit_profile_decision": "DEC-0055",
            "availability_check_gate": "exact_mpn_selection",
            "full_field_kit_physical_items": 12,
            "max_simultaneously_connected": 9,
            "kit_profiles": {
                "native_wifi": {
                    "paths": ["S3-2G4", "C5-2G4/5"],
                    "shared_exact_mpn": True,
                    "physical_items": 2,
                },
                "nrf24": {
                    "paths": ["N24-0", "N24-1", "N24-2"],
                    "shared_exact_mpn": True,
                    "physical_items": 3,
                },
                "cc_sub": {
                    "path": "CC-SUB",
                    "profiles": ["315", "433", "868_915_combined"],
                    "physical_items": 3,
                },
                "voice": {
                    "path": "VOICE-V/U",
                    "profiles": ["VHF_136_174", "UHF_400_470"],
                    "physical_items": 2,
                },
                "receiver": {
                    "paths": ["RX-FM/SW", "RX-AM/LW"],
                    "profiles": ["FM_SW_whip", "AM_LW_loop_or_buffered_pod"],
                    "physical_items": 2,
                },
            },
            "base_extended_packaging_decision": "deferred_to_costed_product_variants",
            "base_onboard_endpoint": "external_sma",
            "base_onboard_sma_count": 9,
            "base_onboard_sma_paths": [
                "S3-2G4",
                "C5-2G4/5",
                "N24-0",
                "N24-1",
                "N24-2",
                "CC-SUB",
                "VOICE-V/U",
                "RX-FM/SW",
                "RX-AM/LW",
            ],
            "device_connector_by_path": {
                "S3-2G4": "rp_sma_jack_pin_center",
                "C5-2G4/5": "rp_sma_jack_pin_center",
                "N24-0": "sma_jack_socket_center",
                "N24-1": "sma_jack_socket_center",
                "N24-2": "sma_jack_socket_center",
                "CC-SUB": "sma_jack_socket_center",
                "VOICE-V/U": "sma_jack_socket_center",
                "RX-FM/SW": "sma_jack_socket_center",
                "RX-AM/LW": "sma_jack_socket_center",
            },
            "antenna_mate_by_path": {
                "S3-2G4": "rp_sma_plug_socket_center",
                "C5-2G4/5": "rp_sma_plug_socket_center",
                "N24-0": "sma_plug_pin_center",
                "N24-1": "sma_plug_pin_center",
                "N24-2": "sma_plug_pin_center",
                "CC-SUB": "sma_plug_pin_center",
                "VOICE-V/U": "sma_plug_pin_center",
                "RX-FM/SW": "sma_plug_pin_center",
                "RX-AM/LW": "sma_plug_pin_center",
            },
            "antenna_qualification_gate": {
                "minimum_orderable_qualified_mpns_per_group": 2,
                "native_wifi_fallback": "standard_sma_if_no_gain_cost_availability_advantage",
            },
            "identification_controls": [
                "permanent_path_band_label",
                "color_collar_or_cap",
                "antenna_profile_manifest",
                "tx_interlock",
            ],
            "nrf_module_interface": "ipex_to_short_pigtail",
            "nrf_dedicated_sma_count": 3,
            "integrated_pcb_antenna_baseline": False,
            "si4732_port_topology": "dedicated_fmi_and_ami",
            "si4732_shared_switch": False,
            "si4732_ami_external_profile": "direct_plug_in_loop_or_qualified_buffered_pod",
            "external_accessory_antennas": "owned_by_accessory",
        }
        for field, expected in expected_antenna_policy.items():
            if antenna_policy.get(field) != expected:
                errors.append(
                    f"{candidate_id}: antenna policy {field} must be {expected!r}"
                )
        exact_external_connectors = {
            "s3_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
            "c5_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
            "receiver_fmsw_external_sma": "gct_rfpc_sma31_fn_175_a",
            "receiver_amlw_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf0_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf1_external_sma": "gct_rfpc_sma31_fn_175_a",
            "nrf2_external_sma": "gct_rfpc_sma31_fn_175_a",
            "cc_external_sma": "gct_rfpc_sma31_fn_175_a",
            "voice_external_sma": "gct_rfpc_sma31_fn_175_a",
        }
        if candidate_id == "G2F-3I":
            instances = candidate.get("instances", {})
            for instance, device_id in exact_external_connectors.items():
                if instances.get(instance) != device_id:
                    errors.append(
                        f"{candidate_id}: external RF connector {instance} must be {device_id}"
                    )
            if len(exact_external_connectors) != antenna_policy.get("base_onboard_sma_count"):
                errors.append(
                    f"{candidate_id}: exact external RF connector count must match antenna policy"
                )
        for nrf_instance in ("nrf0", "nrf1", "nrf2"):
            if candidate.get("instances", {}).get(nrf_instance) != "ebyte_e01_ml01ipx":
                errors.append(
                    f"{candidate_id}: {nrf_instance} must use compact IPEX reference under DEC-0048"
                )

        signal_policy = candidate.get("signal_group_policy")
        if signal_policy is not None:
            if not signal_policy.get("decision") or not signal_policy.get("default_group"):
                errors.append(f"{candidate_id}: incomplete signal-group policy header")
            if not isinstance(signal_policy.get("exclusive"), bool):
                errors.append(f"{candidate_id}: signal-group exclusive must be boolean")
            group_ids: set[str] = set()
            groups_by_id: dict[str, dict[str, Any]] = {}
            for group_number, group in enumerate(signal_policy.get("groups", []), 1):
                context = f"signal group {group_number}"
                group_id = group.get("id", "")
                if not group_id:
                    errors.append(f"{candidate_id}: {context}: missing id")
                elif group_id in group_ids:
                    errors.append(f"{candidate_id}: duplicate signal group {group_id}")
                group_ids.add(group_id)
                groups_by_id[group_id] = group
                if not group.get("members") or not group.get("mode"):
                    errors.append(f"{candidate_id}: {context}: missing members or mode")
                if group.get("full_mix"):
                    if len(group.get("members", [])) < 2:
                        errors.append(f"{candidate_id}: {context}: full mix needs multiple members")
                    if not group.get("required_role_mixes"):
                        errors.append(f"{candidate_id}: {context}: full mix lacks required role mixes")
                    if group.get("peer_standby_forbidden") is not True:
                        errors.append(f"{candidate_id}: {context}: full mix must forbid peer standby")
                    rf_acceptance = group.get("rf_acceptance", {})
                    for required_field in (
                        "decision",
                        "mode",
                        "external_observer_fixture",
                    ):
                        if not rf_acceptance.get(required_field):
                            errors.append(
                                f"{candidate_id}: {context}: full mix RF acceptance missing {required_field}"
                            )
                    if rf_acceptance.get("hil_required") is not True:
                        errors.append(
                            f"{candidate_id}: {context}: full mix RF acceptance must require HIL"
                        )
                    fixture_levels = rf_acceptance.get("fixture_levels", [])
                    if fixture_levels != ["L0_DIV_DIV_PRE_HIL", "T1_TARGET"]:
                        errors.append(
                            f"{candidate_id}: {context}: full mix RF acceptance must separate L0 DIV pre-HIL from T1 target HIL"
                        )
                    if rf_acceptance.get("production_acceptance_level") != "T1_TARGET":
                        errors.append(
                            f"{candidate_id}: {context}: production RF acceptance must require T1_TARGET"
                        )
                    if not isinstance(
                        rf_acceptance.get("same_near_channel_isolated_sensitivity_guaranteed"),
                        bool,
                    ):
                        errors.append(
                            f"{candidate_id}: {context}: same/near-channel sensitivity flag must be boolean"
                        )
            if not signal_policy.get("groups"):
                errors.append(f"{candidate_id}: signal-group policy has no groups")
            for required_group in signal_policy.get("required_full_mix_groups", []):
                group = groups_by_id.get(required_group)
                if group is None:
                    errors.append(
                        f"{candidate_id}: missing required full-mix group {required_group}"
                    )
                elif group.get("full_mix") is not True:
                    errors.append(
                        f"{candidate_id}: required group {required_group} is not full mix"
                    )

        quiet_policy = candidate.get("quiet_state_policy")
        if quiet_policy is not None:
            if not quiet_policy.get("decision") or not quiet_policy.get("default_state"):
                errors.append(f"{candidate_id}: incomplete quiet-state policy header")
            quiet_ids: set[str] = set()
            for quiet_number, quiet in enumerate(quiet_policy.get("contracts", []), 1):
                context = f"quiet-state contract {quiet_number}"
                quiet_id = quiet.get("id", "")
                if not quiet_id:
                    errors.append(f"{candidate_id}: {context}: missing id")
                elif quiet_id in quiet_ids:
                    errors.append(f"{candidate_id}: duplicate quiet-state contract {quiet_id}")
                quiet_ids.add(quiet_id)
                for required_field in ("interfaces", "inactive_state", "control", "proof_gate"):
                    if not quiet.get(required_field):
                        errors.append(f"{candidate_id}: {context}: missing {required_field}")
            required_quiet = set(quiet_policy.get("required_contracts", []))
            missing_quiet = required_quiet - quiet_ids
            unexpected_quiet = quiet_ids - required_quiet
            if missing_quiet:
                errors.append(
                    f"{candidate_id}: missing required quiet-state contracts {sorted(missing_quiet)}"
                )
            if unexpected_quiet:
                errors.append(
                    f"{candidate_id}: unrequired quiet-state contracts {sorted(unexpected_quiet)}"
                )

        instances = candidate.get("instances", {})
        for instance, device_id in instances.items():
            if device_id not in devices:
                errors.append(f"{candidate_id}: {instance} uses unknown device {device_id}")
        if any(device_id not in devices for device_id in instances.values()):
            continue

        bom_audit = candidate.get("bom_audit")
        if bom_audit is not None:
            for required in (
                "status",
                "default_scope",
                "cost_basis",
                "non_purchase_instances",
                "substitution_policy",
                "required_uninstantiated_parts",
                "pcb_features_not_mpn_lines",
                "exit",
            ):
                if not bom_audit.get(required):
                    errors.append(f"{candidate_id}: BOM audit missing {required}")
            for instance in bom_audit.get("scope_overrides", {}):
                if instance not in instances:
                    errors.append(
                        f"{candidate_id}: BOM scope override references unknown {instance}"
                    )
            non_purchase_names: set[str] = set()
            for row_number, row in enumerate(
                bom_audit.get("non_purchase_instances", []), 1
            ):
                context = f"BOM non-purchase instance {row_number}"
                for required in ("instance", "parent_instance", "reason"):
                    if not row.get(required):
                        errors.append(f"{candidate_id}: {context}: missing {required}")
                instance = row.get("instance")
                parent = row.get("parent_instance")
                if instance not in instances:
                    errors.append(
                        f"{candidate_id}: {context}: unknown instance {instance!r}"
                    )
                if parent not in instances:
                    errors.append(
                        f"{candidate_id}: {context}: unknown parent {parent!r}"
                    )
                if instance == parent:
                    errors.append(
                        f"{candidate_id}: {context}: instance cannot parent itself"
                    )
                if instance in non_purchase_names:
                    errors.append(
                        f"{candidate_id}: duplicate BOM non-purchase instance {instance}"
                    )
                non_purchase_names.add(instance)
            substitution_policy = bom_audit.get("substitution_policy", {})
            if not substitution_policy.get("status"):
                errors.append(f"{candidate_id}: BOM substitution policy missing status")
            substitution_class_ids: set[str] = set()
            substitution_members: set[str] = set()
            for row_number, row in enumerate(
                substitution_policy.get("classes", []), 1
            ):
                context = f"BOM substitution class {row_number}"
                for required in (
                    "id",
                    "title",
                    "disposition",
                    "equivalence_envelope",
                    "requalification",
                    "device_ids",
                ):
                    if not row.get(required):
                        errors.append(f"{candidate_id}: {context}: missing {required}")
                class_id = row.get("id", "")
                if class_id in substitution_class_ids:
                    errors.append(
                        f"{candidate_id}: duplicate BOM substitution class {class_id}"
                    )
                substitution_class_ids.add(class_id)
                for device_id in row.get("device_ids", []):
                    if device_id not in devices:
                        errors.append(
                            f"{candidate_id}: {context}: unknown device {device_id}"
                        )
                    if device_id in substitution_members:
                        errors.append(
                            f"{candidate_id}: duplicate BOM substitution member {device_id}"
                        )
                    substitution_members.add(device_id)
            expected_purchase_devices = {
                device_id
                for instance, device_id in instances.items()
                if instance not in non_purchase_names
            }
            missing_substitution = expected_purchase_devices - substitution_members
            unexpected_substitution = substitution_members - expected_purchase_devices
            if missing_substitution:
                errors.append(
                    f"{candidate_id}: BOM substitution policy omits current purchase lines "
                    f"{sorted(missing_substitution)}"
                )
            if unexpected_substitution:
                errors.append(
                    f"{candidate_id}: BOM substitution policy contains non-purchase lines "
                    f"{sorted(unexpected_substitution)}"
                )
            missing_part_ids: set[str] = set()
            allowed_physical_gate_statuses = {
                "g3_connector_plane_and_mount_coupon_required",
                "received_mate_and_routed_length_coupon_required",
                "received_mate_identification_and_retention_coupon_required",
                "profile_variant_bom_and_hil_required",
            }
            for row_number, row in enumerate(
                bom_audit.get("required_uninstantiated_parts", []), 1
            ):
                context = f"BOM uninstantiated part {row_number}"
                for required in ("id", "quantity", "scope", "role", "blocker"):
                    if not row.get(required):
                        errors.append(f"{candidate_id}: {context}: missing {required}")
                if row.get("id") in missing_part_ids:
                    errors.append(
                        f"{candidate_id}: duplicate BOM uninstantiated id {row.get('id')}"
                    )
                missing_part_ids.add(row.get("id", ""))
                gate = row.get("resolution_gate", {})
                for required in (
                    "status",
                    "owner_stage",
                    "prerequisites",
                    "acceptance",
                    "evidence_refs",
                ):
                    if not gate.get(required):
                        errors.append(
                            f"{candidate_id}: {context}: resolution gate missing {required}"
                        )
                if gate.get("status") not in allowed_physical_gate_statuses:
                    errors.append(
                        f"{candidate_id}: {context}: unsupported resolution gate status "
                        f"{gate.get('status')!r}"
                    )
                for field in ("prerequisites", "acceptance", "evidence_refs"):
                    values = gate.get(field, [])
                    if not isinstance(values, list) or any(
                        not isinstance(value, str) or not value.strip()
                        for value in values
                    ):
                        errors.append(
                            f"{candidate_id}: {context}: resolution gate {field} "
                            "must be a non-empty string list"
                        )
                    elif len(values) != len(set(values)):
                        errors.append(
                            f"{candidate_id}: {context}: duplicate resolution gate {field}"
                        )
            required_gap_ids = {
                "external_antenna_kit",
            }
            if required_gap_ids - missing_part_ids:
                errors.append(
                    f"{candidate_id}: BOM audit omits physical gap families "
                    f"{sorted(required_gap_ids - missing_part_ids)}"
                )
            gap_by_id = {
                row.get("id"): row
                for row in bom_audit.get("required_uninstantiated_parts", [])
            }
            if gap_by_id.get("external_antenna_kit", {}).get("quantity") != antenna_policy.get(
                "full_field_kit_physical_items"
            ):
                errors.append(
                    f"{candidate_id}: BOM antenna-kit gap must match antenna policy"
                )

        if candidate_id == "G2F-3I":
            projection_audit = candidate.get("i9_projection_audit", {})
            if projection_audit.get("status") != "paper_reviewed_joint_target_projection":
                errors.append(f"{candidate_id}: I9 projection audit status is not reviewed")
            for required in (
                "fixed_route_abstract_policy",
                "consistency_checks",
                "unresolved_owner_decisions",
                "downstream_reopen",
            ):
                if required not in projection_audit:
                    errors.append(f"{candidate_id}: I9 projection audit missing {required}")
            for field in ("consistency_checks", "downstream_reopen"):
                values = projection_audit.get(field, [])
                if not isinstance(values, list) or not values or any(
                    not isinstance(value, str) or not value.strip()
                    for value in values
                ):
                    errors.append(
                        f"{candidate_id}: I9 projection audit {field} must be a non-empty string list"
                    )
            unresolved_owner_decisions = projection_audit.get(
                "unresolved_owner_decisions", None
            )
            if not isinstance(unresolved_owner_decisions, list):
                errors.append(
                    f"{candidate_id}: I9 unresolved_owner_decisions must be a list"
                )
            elif unresolved_owner_decisions:
                errors.append(
                    f"{candidate_id}: I9 has unresolved owner decisions "
                    f"{unresolved_owner_decisions}"
                )

            abstract_policy = projection_audit.get(
                "fixed_route_abstract_policy", {}
            )
            required_abstract_classes = {
                "electrical_plane_rail_or_wired_logic",
                "intentional_no_connect_or_open_strap",
                "pcb_geometry_test_or_reserved_feature",
                "external_fixture_source_boundary",
            }
            class_ids: set[str] = set()
            classified_abstracts: set[str] = set()
            for row_number, row in enumerate(abstract_policy.get("classes", []), 1):
                context = f"I9 abstract class {row_number}"
                for required in ("id", "rule", "endpoints"):
                    if not row.get(required):
                        errors.append(f"{candidate_id}: {context}: missing {required}")
                class_id = row.get("id", "")
                if class_id in class_ids:
                    errors.append(f"{candidate_id}: duplicate I9 abstract class {class_id}")
                class_ids.add(class_id)
                endpoints = row.get("endpoints", [])
                if not isinstance(endpoints, list) or any(
                    not isinstance(endpoint, str)
                    or not endpoint.startswith("abstract:")
                    for endpoint in endpoints
                ):
                    errors.append(
                        f"{candidate_id}: {context}: endpoints must be abstract endpoint strings"
                    )
                    continue
                for endpoint in endpoints:
                    if endpoint in classified_abstracts:
                        errors.append(
                            f"{candidate_id}: duplicate I9 abstract endpoint classification {endpoint}"
                        )
                    classified_abstracts.add(endpoint)
            if class_ids != required_abstract_classes:
                errors.append(
                    f"{candidate_id}: I9 abstract classes differ from required set; "
                    f"missing {sorted(required_abstract_classes - class_ids)}, "
                    f"unexpected {sorted(class_ids - required_abstract_classes)}"
                )

            abstract_occurrences = [
                endpoint
                for route in candidate.get("fixed_routes", [])
                for endpoint in (route.get("from"), route.get("to"))
                if isinstance(endpoint, str) and endpoint.startswith("abstract:")
            ]
            actual_abstracts = set(abstract_occurrences)
            missing_classification = actual_abstracts - classified_abstracts
            stale_classification = classified_abstracts - actual_abstracts
            if missing_classification:
                errors.append(
                    f"{candidate_id}: I9 unclassified abstract endpoints "
                    f"{sorted(missing_classification)}"
                )
            if stale_classification:
                errors.append(
                    f"{candidate_id}: I9 stale abstract endpoint classifications "
                    f"{sorted(stale_classification)}"
                )
            if abstract_policy.get("expected_unique_endpoint_count") != len(
                actual_abstracts
            ):
                errors.append(
                    f"{candidate_id}: I9 abstract unique count must be "
                    f"{len(actual_abstracts)}"
                )
            if abstract_policy.get("expected_occurrence_count") != len(
                abstract_occurrences
            ):
                errors.append(
                    f"{candidate_id}: I9 abstract occurrence count must be "
                    f"{len(abstract_occurrences)}"
                )

        controller_sets: dict[str, set[str]] = {}
        for instance, controller_list in candidate.get("controllers", {}).items():
            if instance not in instances:
                errors.append(f"{candidate_id}: controllers declared for unknown {instance}")
                continue
            if len(controller_list) != len(set(controller_list)):
                errors.append(f"{candidate_id}: duplicate controller on {instance}")
            device = devices[instances[instance]]
            unknown_controllers = set(controller_list) - set(device.get("controller_capabilities", []))
            if unknown_controllers:
                errors.append(
                    f"{candidate_id}: {instance} declares unavailable controllers {sorted(unknown_controllers)}"
                )
            controller_sets[instance] = set(controller_list)

        used: dict[str, set[str]] = {instance: set() for instance in instances}
        allocation_lookup: dict[tuple[str, str], str] = {}
        for row_number, allocation in enumerate(candidate.get("allocations", []), 1):
            context = f"allocation {row_number}"
            instance = allocation.get("instance", "")
            contact = allocation.get("contact", "")
            if instance not in instances:
                errors.append(f"{candidate_id}: {context}: unknown instance {instance!r}")
                continue
            device = devices[instances[instance]]
            contact_data = device.get("contacts", {}).get(contact)
            if not contact_data:
                errors.append(
                    f"{candidate_id}: {context}: {instance}.{contact} is not exposed by {device['mpn']}"
                )
                continue
            if not device.get("programmable") or contact_data.get("role") != "gpio":
                errors.append(f"{candidate_id}: {context}: {instance}.{contact} is not a programmable GPIO")
            if contact in used[instance]:
                errors.append(f"{candidate_id}: duplicate allocation {instance}.{contact}")
            used[instance].add(contact)
            allocation_lookup[(instance, contact)] = allocation.get("net", "")
            if not allocation.get("net") or not allocation.get("direction") or not allocation.get("controller"):
                errors.append(f"{candidate_id}: {context}: incomplete net/direction/controller")
            if allocation.get("controller") not in controller_sets.get(instance, set()):
                errors.append(
                    f"{candidate_id}: {context}: undeclared controller {instance}.{allocation.get('controller')}"
                )
            if contact in device.get("strapping_contacts", []) and not allocation.get("strap_proof"):
                errors.append(f"{candidate_id}: {instance}.{contact} is a strap without strap_proof")
            for peer in allocation.get("peers", []):
                _check_endpoint(peer, candidate_id, instances, devices, errors, context)

        for allocation in candidate.get("allocations", []):
            for peer in allocation.get("peers", []):
                if peer.startswith("abstract:") or "." not in peer:
                    continue
                peer_instance, peer_contact = peer.split(".", 1)
                peer_device = devices[instances[peer_instance]]
                if peer_device.get("programmable"):
                    peer_net = allocation_lookup.get((peer_instance, peer_contact))
                    if peer_net != allocation.get("net"):
                        errors.append(
                            f"{candidate_id}: {allocation['instance']}.{allocation['contact']} peer "
                            f"{peer} does not reciprocate net {allocation.get('net')}"
                        )

        selected_windows: dict[tuple[str, str], tuple[int, int]] = {}
        for window_number, window in enumerate(candidate.get("controller_gpio_windows", []), 1):
            context = f"controller GPIO window {window_number}"
            instance = window.get("instance", "")
            controllers = window.get("controllers", [])
            gpio_min = window.get("gpio_min")
            gpio_max = window.get("gpio_max")
            if instance not in instances:
                errors.append(f"{candidate_id}: {context}: unknown instance {instance!r}")
                continue
            if not controllers or not window.get("reason"):
                errors.append(f"{candidate_id}: {context}: missing controllers or reason")
            if (
                not isinstance(gpio_min, int)
                or not isinstance(gpio_max, int)
                or gpio_min > gpio_max
            ):
                errors.append(f"{candidate_id}: {context}: invalid GPIO bounds")
                continue
            for controller in controllers:
                key = (instance, controller)
                if key in selected_windows:
                    errors.append(
                        f"{candidate_id}: {context}: duplicate GPIO-window selection for "
                        f"{instance}.{controller}"
                    )
                selected_windows[key] = (gpio_min, gpio_max)
                if controller not in controller_sets.get(instance, set()):
                    errors.append(
                        f"{candidate_id}: {context}: undeclared controller {instance}.{controller}"
                    )
                matched_rows = [
                    row
                    for row in candidate.get("allocations", [])
                    if row.get("instance") == instance and row.get("controller") == controller
                ]
                if not matched_rows:
                    errors.append(
                        f"{candidate_id}: {context}: controller {instance}.{controller} has no allocation"
                    )
                for row in matched_rows:
                    match = re.fullmatch(r"GPIO(\d+)", row.get("contact", ""))
                    if not match or not gpio_min <= int(match.group(1)) <= gpio_max:
                        errors.append(
                            f"{candidate_id}: {instance}.{controller} allocation "
                            f"{row.get('contact')} is outside GPIO{gpio_min}..GPIO{gpio_max}"
                        )

        for instance, device_id in instances.items():
            device = devices[device_id]
            declared = controller_sets.get(instance, set())
            for group in device.get("controller_gpio_window_groups", []):
                active = declared & set(group["controllers"])
                if not active:
                    continue
                selections = {
                    selected_windows[(instance, controller)]
                    for controller in active
                    if (instance, controller) in selected_windows
                }
                missing = {
                    controller
                    for controller in active
                    if (instance, controller) not in selected_windows
                }
                if missing:
                    errors.append(
                        f"{candidate_id}: {instance} {group['id']} missing GPIO-window "
                        f"selection for {sorted(missing)}"
                    )
                if len(selections) > 1:
                    errors.append(
                        f"{candidate_id}: {instance} {group['id']} controllers select "
                        f"different shared GPIO windows {sorted(selections)}"
                    )
                allowed = {tuple(bounds) for bounds in group["allowed_windows"]}
                for selection in selections:
                    if selection not in allowed:
                        errors.append(
                            f"{candidate_id}: {instance} {group['id']} selects unsupported "
                            f"GPIO window {selection}; allowed {sorted(allowed)}"
                        )

        capacity_ids: set[str] = set()
        for capacity_number, capacity in enumerate(candidate.get("capacity_contracts", []), 1):
            context = f"capacity contract {capacity_number}"
            capacity_id = capacity.get("id", "")
            available = capacity.get("available")
            reserve = capacity.get("reserve")
            claims = capacity.get("claims", [])
            if not capacity_id:
                errors.append(f"{candidate_id}: {context}: missing id")
            elif capacity_id in capacity_ids:
                errors.append(f"{candidate_id}: duplicate capacity contract {capacity_id}")
            capacity_ids.add(capacity_id)
            if capacity.get("instance") not in instances:
                errors.append(
                    f"{candidate_id}: {context}: unknown instance {capacity.get('instance')}"
                )
            if not isinstance(available, int) or available <= 0:
                errors.append(f"{candidate_id}: {context}: invalid available capacity")
                continue
            if not isinstance(reserve, int) or reserve < 0:
                errors.append(f"{candidate_id}: {context}: invalid reserve")
                continue
            if not claims or not capacity.get("proof"):
                errors.append(f"{candidate_id}: {context}: missing claims or proof")
            claimed = 0
            consumers: set[str] = set()
            for claim in claims:
                consumer = claim.get("consumer", "")
                units = claim.get("units")
                if not consumer or not isinstance(units, int) or units <= 0:
                    errors.append(f"{candidate_id}: {context}: invalid claim {claim!r}")
                    continue
                if consumer in consumers:
                    errors.append(
                        f"{candidate_id}: {context}: duplicate consumer {consumer!r}"
                    )
                consumers.add(consumer)
                claimed += units
            if claimed + reserve != available:
                errors.append(
                    f"{candidate_id}: {context}: {claimed} claimed + {reserve} reserve "
                    f"!= {available} available"
                )

        mux_ids: set[str] = set()
        for mux_number, mux in enumerate(candidate.get("mux_contracts", []), 1):
            context = f"mux contract {mux_number}"
            mux_id = mux.get("id", "")
            instance = mux.get("instance", "")
            controller = mux.get("controller", "")
            contacts = mux.get("contacts", [])
            if not mux_id:
                errors.append(f"{candidate_id}: {context}: missing id")
            elif mux_id in mux_ids:
                errors.append(f"{candidate_id}: duplicate mux contract {mux_id}")
            mux_ids.add(mux_id)
            if instance not in instances:
                errors.append(f"{candidate_id}: {context}: unknown instance {instance!r}")
                continue
            if controller not in controller_sets.get(instance, set()):
                errors.append(
                    f"{candidate_id}: {context}: undeclared controller {instance}.{controller}"
                )
            if not contacts or len(contacts) != len(set(contacts)) or not mux.get("proof"):
                errors.append(f"{candidate_id}: {context}: incomplete contacts or proof")
            unknown = set(contacts) - set(devices[instances[instance]].get("contacts", {}))
            if unknown:
                errors.append(
                    f"{candidate_id}: {context}: contacts not exposed by exact device {sorted(unknown)}"
                )
            actual = {
                row.get("contact")
                for row in candidate.get("allocations", [])
                if row.get("instance") == instance and row.get("controller") == controller
            }
            if actual != set(contacts):
                errors.append(
                    f"{candidate_id}: {context}: declared contacts {sorted(contacts, key=natural_contact_key)} "
                    f"!= allocated {sorted(actual, key=natural_contact_key)}"
                )

        missing_muxes = set(candidate.get("required_mux_contracts", [])) - mux_ids
        if missing_muxes:
            errors.append(f"{candidate_id}: missing required mux contracts {sorted(missing_muxes)}")

        reservations = candidate.get("reservations", {})
        free_gpio = candidate.get("free_gpio", {})
        for instance, device_id in instances.items():
            device = devices[device_id]
            if not device.get("programmable"):
                continue
            all_gpio = {
                contact
                for contact, attributes in device["contacts"].items()
                if attributes.get("role") == "gpio"
            }
            reserved = set(reservations.get(instance, {}))
            free = set(free_gpio.get(instance, []))
            for label, contacts in (("used", used[instance]), ("reserved", reserved), ("free", free)):
                unknown = contacts - all_gpio
                if unknown:
                    errors.append(f"{candidate_id}: {instance} {label} unknown GPIO {sorted(unknown)}")
            overlaps = (used[instance] & reserved) | (used[instance] & free) | (reserved & free)
            if overlaps:
                errors.append(f"{candidate_id}: {instance} GPIO classification overlap {sorted(overlaps)}")
            missing = all_gpio - used[instance] - reserved - free
            if missing:
                errors.append(f"{candidate_id}: {instance} unaccounted GPIO {sorted(missing, key=natural_contact_key)}")
            extra = (used[instance] | reserved | free) - all_gpio
            if extra:
                errors.append(f"{candidate_id}: {instance} non-GPIO classification {sorted(extra)}")

        services_by_instance = {
            service.get("instance"): set(service.get("contacts", []))
            for service in candidate.get("services", [])
        }
        for service in candidate.get("services", []):
            instance = service.get("instance", "")
            if instance not in instances:
                errors.append(f"{candidate_id}: service for unknown instance {instance}")
                continue
            for contact in service.get("contacts", []):
                if contact not in devices[instances[instance]]["contacts"]:
                    errors.append(f"{candidate_id}: service contact {instance}.{contact} is not exposed")
            if not service.get("method"):
                errors.append(f"{candidate_id}: service method missing for {instance}")
        for instance, device_id in instances.items():
            device = devices[device_id]
            required = set(device.get("service_required", [])) | set(
                device.get("service_required_all", [])
            )
            missing_service = required - services_by_instance.get(instance, set())
            if missing_service:
                errors.append(f"{candidate_id}: {instance} missing service contacts {sorted(missing_service)}")
            alternatives = [set(group) for group in device.get("service_required_any", [])]
            if alternatives and not any(
                group <= services_by_instance.get(instance, set()) for group in alternatives
            ):
                errors.append(
                    f"{candidate_id}: {instance} missing one complete service alternative "
                    f"{[sorted(group) for group in alternatives]}"
                )

        for route_number, route in enumerate(candidate.get("fixed_routes", []), 1):
            context = f"fixed route {route_number}"
            for endpoint_name in ("from", "to"):
                endpoint = route.get(endpoint_name, "")
                _check_endpoint(endpoint, candidate_id, instances, devices, errors, context)
            if not route.get("net") or not route.get("safety"):
                errors.append(f"{candidate_id}: {context}: missing net or safety note")

        route_endpoints = {
            route[endpoint_name]
            for route in candidate.get("fixed_routes", [])
            for endpoint_name in ("from", "to")
            if route.get(endpoint_name)
        }
        for instance, accounting in candidate.get("contact_accounting", {}).items():
            if instance not in instances:
                errors.append(f"{candidate_id}: contact accounting for unknown instance {instance}")
                continue
            allocatable = set(devices[instances[instance]].get("allocatable_contacts", []))
            used_contacts = set(accounting.get("used", []))
            reserved_contacts = set(accounting.get("reserved", {}))
            free_contacts = set(accounting.get("free", []))
            for label, contacts in (
                ("used", used_contacts),
                ("reserved", reserved_contacts),
                ("free", free_contacts),
            ):
                unknown = contacts - allocatable
                if unknown:
                    errors.append(
                        f"{candidate_id}: {instance} {label} unknown allocatable contacts {sorted(unknown, key=natural_contact_key)}"
                    )
            overlaps = (
                (used_contacts & reserved_contacts)
                | (used_contacts & free_contacts)
                | (reserved_contacts & free_contacts)
            )
            if overlaps:
                errors.append(
                    f"{candidate_id}: {instance} contact classification overlap {sorted(overlaps, key=natural_contact_key)}"
                )
            missing = allocatable - used_contacts - reserved_contacts - free_contacts
            if missing:
                errors.append(
                    f"{candidate_id}: {instance} unaccounted allocatable contacts {sorted(missing, key=natural_contact_key)}"
                )
            for contact in used_contacts:
                if f"{instance}.{contact}" not in route_endpoints:
                    errors.append(
                        f"{candidate_id}: {instance}.{contact} is marked used but has no fixed route"
                    )

        resource_ids: set[str] = set()
        resources_by_id: dict[str, dict[str, Any]] = {}
        for resource_number, resource in enumerate(candidate.get("resource_contracts", []), 1):
            context = f"resource contract {resource_number}"
            resource_id = resource.get("id", "")
            if not resource_id:
                errors.append(f"{candidate_id}: {context}: missing id")
            elif resource_id in resource_ids:
                errors.append(f"{candidate_id}: duplicate resource contract {resource_id}")
            resource_ids.add(resource_id)
            resources_by_id[resource_id] = resource
            for required_field in ("owner", "clients", "sharing", "deadline", "proof_gate"):
                if not resource.get(required_field):
                    errors.append(f"{candidate_id}: {context}: missing {required_field}")
            if resource.get("owner") not in instances:
                errors.append(f"{candidate_id}: {context}: unknown owner {resource.get('owner')}")
            if resource.get("sharing") not in {"dedicated", "scheduled"}:
                errors.append(f"{candidate_id}: {context}: invalid sharing {resource.get('sharing')}")
            if resource.get("sharing") == "scheduled" and not resource.get("arbitration"):
                errors.append(f"{candidate_id}: {context}: scheduled resource lacks arbitration")

        required_resources = set(candidate.get("required_resource_contracts", []))
        missing_resources = required_resources - resource_ids
        if missing_resources:
            errors.append(
                f"{candidate_id}: missing required resource contracts {sorted(missing_resources)}"
            )
        for resource_id in candidate.get("exclusive_resource_contracts", []):
            resource = resources_by_id.get(resource_id)
            if resource is None:
                errors.append(
                    f"{candidate_id}: exclusive resource {resource_id} has no contract"
                )
            elif resource.get("sharing") != "dedicated":
                errors.append(
                    f"{candidate_id}: exclusive resource {resource_id} is not dedicated"
                )

    return errors


def render_ledger(database: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    devices = database["devices"]
    referenced_ids = sorted({device_id for c in candidates for device_id in c["instances"].values()})
    reviewed_targets = [
        candidate["id"]
        for candidate in candidates
        if candidate.get("status") == "target_architecture_pre_schematic_reviewed"
    ]
    review_status = (
        "- Статус: **"
        + ", ".join(reviewed_targets)
        + " — проведено сводное предсхемное ревью; H1 принят; разрешена только H2 production-схема, а PCB placement/routing остаётся отдельным gate**"
        if reviewed_targets
        else "- Статус: **машинные проверки проведены; target architecture ещё не принята**"
    )
    lines = [
        "# G2F — generated exact-device pin ledger",
        "",
        review_status,
        "- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/*.json`",
        "- Regenerate: `python3 hardware/architecture/generate.py --write`",
        "- Verify: `python3 hardware/architecture/generate.py --check`",
        "",
        "> Файл сгенерирован. Ручные изменения будут отвергнуты `--check`.",
        "",
        "## Candidate snapshot",
        "",
        "| Candidate | Programmable domains | Exact exposed-GPIO budget | Decisive open risk |",
        "|---|---:|---|---|",
    ]
    for candidate in candidates:
        budgets: list[str] = []
        programmable_domains = 0
        for instance, device_id in candidate["instances"].items():
            device = devices[device_id]
            if not device.get("programmable"):
                continue
            programmable_domains += 1
            used_count = sum(1 for row in candidate["allocations"] if row["instance"] == instance)
            reserved_count = len(candidate["reservations"].get(instance, {}))
            free_count = len(candidate["free_gpio"].get(instance, []))
            budgets.append(f"`{instance} {used_count}U/{reserved_count}R/{free_count}F`")
        lines.append(
            f"| `{candidate['id']}` | {programmable_domains} | {', '.join(budgets)} | "
            f"{candidate['decisive_open_risk']} |"
        )
    lines += [
        "",
        "## Exact-device provenance used by these drafts",
        "",
        "| Device id | Exact MPN / boundary | Qualification | Lifecycle | Primary source | Lifecycle evidence |",
        "|---|---|---|---|---|---|",
    ]
    for device_id in referenced_ids:
        device = devices[device_id]
        source = device["source"]
        lifecycle_source = device.get("lifecycle_source")
        lifecycle_evidence = (
            f"[{lifecycle_source['document']}]({lifecycle_source['url']})"
            if lifecycle_source
            else "same primary source"
        )
        lines.append(
            f"| `{device_id}` | `{device['mpn']}` | `{device['qualification']}` | "
            f"`{device['lifecycle']}` | [{source['document']} {source['version']}]({source['url']}) | "
            f"{lifecycle_evidence} |"
        )

    for candidate in candidates:
        candidate_id = candidate["id"]
        lines += [
            "",
            f"## {candidate_id} — {candidate['title']}",
            "",
            f"- Candidate status: `{candidate['status']}`",
            "- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.",
        ]
        antenna_policy = candidate["antenna_policy"]
        rp_sma_paths = [
            path
            for path, connector in antenna_policy["device_connector_by_path"].items()
            if connector == "rp_sma_jack_pin_center"
        ]
        standard_sma_paths = [
            path
            for path, connector in antenna_policy["device_connector_by_path"].items()
            if connector == "sma_jack_socket_center"
        ]
        lines += [
            "",
            "### Antenna policy",
            "",
            f"Decisions `{antenna_policy['decision']}`/`{antenna_policy['exact_count_decision']}`: "
            f"onboard endpoint `{antenna_policy['base_onboard_endpoint']}`; "
            f"`{antenna_policy['base_onboard_sma_count']}` total SMA paths "
            f"({', '.join(f'`{path}`' for path in antenna_policy['base_onboard_sma_paths'])}); "
            f"three nRF paths use `{antenna_policy['nrf_module_interface']}` to "
            f"`{antenna_policy['nrf_dedicated_sma_count']}` dedicated SMA; integrated-PCB baseline "
            f"`{str(antenna_policy['integrated_pcb_antenna_baseline']).lower()}`. Si4732 topology "
            f"`{antenna_policy['si4732_port_topology']}` with shared switch "
            f"`{str(antenna_policy['si4732_shared_switch']).lower()}` and AMI profile "
            f"`{antenna_policy['si4732_ami_external_profile']}`. Connector decision "
            f"`{antenna_policy['external_connector_decision']}` assigns device-side RP-SMA jack/pin to "
            f"{', '.join(f'`{path}`' for path in rp_sma_paths)} and standard SMA jack/socket to "
            f"{', '.join(f'`{path}`' for path in standard_sma_paths)}. Each antenna group requires at least "
            f"`{antenna_policy['antenna_qualification_gate']['minimum_orderable_qualified_mpns_per_group']}` "
            f"orderable qualified MPNs; native Wi-Fi fallback is "
            f"`{antenna_policy['antenna_qualification_gate']['native_wifi_fallback']}`. External accessories own their antennas.",
            f"Kit decision `{antenna_policy['kit_profile_decision']}` defines "
            f"`{antenna_policy['full_field_kit_physical_items']}` loose antenna items with at most "
            f"`{antenna_policy['max_simultaneously_connected']}` connected at once. Native Wi-Fi uses "
            f"one shared exact MPN in quantity 2, nRF24 one shared exact MPN in quantity 3, CC-SUB "
            f"uses 315/433/combined-868+915 profiles, VOICE uses separate VHF/UHF profiles, and the "
            f"receiver uses FM/SW whip plus AM/LW loop or buffered pod. Availability is checked at "
            f"`{antenna_policy['availability_check_gate']}`; base/extended packaging remains "
            f"`{antenna_policy['base_extended_packaging_decision']}`.",
        ]
        signal_policy = candidate.get("signal_group_policy")
        if signal_policy:
            lines += [
                "",
                "### Signal-group policy",
                "",
                f"Decision `{signal_policy['decision']}`; default `{signal_policy['default_group']}`; "
                f"exclusive groups: `{str(signal_policy['exclusive']).lower()}`.",
                "",
                "| Group | Members | Runtime mode | Required role mixes | RF acceptance |",
                "|---|---|---|---|---|",
            ]
            for group in signal_policy["groups"]:
                members = ", ".join(f"`{member}`" for member in group["members"])
                mixes = ", ".join(f"`{mix}`" for mix in group.get("required_role_mixes", [])) or "—"
                rf_acceptance = group.get("rf_acceptance")
                rf_text = "—"
                if rf_acceptance:
                    rf_text = (
                        f"`{rf_acceptance['decision']}` / `{rf_acceptance['mode']}`; "
                        f"observer `{rf_acceptance['external_observer_fixture']}`; "
                        f"`L0 DIV↔DIV` pre-HIL → `{rf_acceptance['production_acceptance_level']}`; HIL required"
                    )
                lines.append(
                    f"| `{group['id']}` | {members} | {group['mode']} | {mixes} | {rf_text} |"
                )

        quiet_policy = candidate.get("quiet_state_policy")
        if quiet_policy:
            lines += [
                "",
                "### Unused-interface quiet-state policy",
                "",
                f"Decision `{quiet_policy['decision']}`; default `{quiet_policy['default_state']}`.",
                "",
                "| Contract | Interfaces | Inactive state | Control | Proof gate |",
                "|---|---|---|---|---|",
            ]
            for quiet in quiet_policy["contracts"]:
                interfaces = ", ".join(f"`{interface}`" for interface in quiet["interfaces"])
                lines.append(
                    f"| `{quiet['id']}` | {interfaces} | {quiet['inactive_state']} | "
                    f"{quiet['control']} | {quiet['proof_gate']} |"
                )
        allocations_by_instance: dict[str, list[dict[str, Any]]] = {}
        for allocation in candidate["allocations"]:
            allocations_by_instance.setdefault(allocation["instance"], []).append(allocation)

        for instance, device_id in candidate["instances"].items():
            device = devices[device_id]
            if not device.get("programmable"):
                continue
            allocations = sorted(
                allocations_by_instance.get(instance, []), key=lambda row: natural_contact_key(row["contact"])
            )
            reserved = candidate["reservations"].get(instance, {})
            free = candidate["free_gpio"].get(instance, [])
            lines += [
                "",
                f"### `{instance}` — `{device['mpn']}`",
                "",
                "| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |",
                "|---|---:|---|---|---|---|---|",
            ]
            for row in allocations:
                pad = device["contacts"][row["contact"]]["physical"]
                peers = ", ".join(f"`{peer}`" for peer in row.get("peers", []))
                proof = row.get("strap_proof", "—")
                lines.append(
                    f"| `{row['contact']}` | {pad} | `{row['net']}` | `{row['direction']}` | "
                    f"`{row['controller']}` | {peers} | {proof} |"
                )
            reserved_text = ", ".join(f"`{pin}`" for pin in sorted(reserved, key=natural_contact_key)) or "none"
            free_text = ", ".join(f"`{pin}`" for pin in sorted(free, key=natural_contact_key)) or "none"
            gpio_total = sum(1 for attributes in device["contacts"].values() if attributes["role"] == "gpio")
            lines += [
                "",
                f"Budget: **{len(allocations)} used + {len(reserved)} reserved + {len(free)} free = {gpio_total} exposed GPIO**.",
                f"Reserved: {reserved_text}. Free: {free_text}.",
            ]

        lines += ["", "### Fixed-function/control routes", "", "| Net | From | To | Reset/safety rule |", "|---|---|---|---|"]
        for route in candidate.get("fixed_routes", []):
            lines.append(f"| `{route['net']}` | `{route['from']}` | `{route['to']}` | {route['safety']} |")
        if not candidate.get("fixed_routes"):
            lines.append("| — | — | — | no fixed routes declared |")

        lines += ["", "### Programming, recovery and diagnostics", ""]
        for service in candidate["services"]:
            contacts = ", ".join(f"`{contact}`" for contact in service["contacts"])
            lines.append(f"- `{service['instance']}`: {contacts} — {service['method']}.")

        if candidate.get("contact_accounting"):
            lines += [
                "",
                "### Non-MCU contact accounting",
                "",
                "| Instance | Used | Reserved | Free |",
                "|---|---:|---:|---:|",
            ]
            for instance, accounting in candidate["contact_accounting"].items():
                lines.append(
                    f"| `{instance}` | {len(accounting.get('used', []))} | "
                    f"{len(accounting.get('reserved', {}))} | {len(accounting.get('free', []))} |"
                )

        if candidate.get("resource_contracts"):
            lines += [
                "",
                "### Interface non-interference contracts",
                "",
                "| Resource | Owner | Clients | Sharing | Deadline / bound | Proof gate |",
                "|---|---|---|---|---|---|",
            ]
            for resource in candidate["resource_contracts"]:
                clients = ", ".join(f"`{client}`" for client in resource["clients"])
                sharing = resource["sharing"]
                if resource.get("arbitration"):
                    sharing += f"; {resource['arbitration']}"
                lines.append(
                    f"| `{resource['id']}` | `{resource['owner']}` | {clients} | {sharing} | "
                    f"{resource['deadline']} | {resource['proof_gate']} |"
                )

        if candidate.get("controller_gpio_windows"):
            lines += [
                "",
                "### Controller GPIO-window selections",
                "",
                "| Instance | Controllers | Selected window | Device constraint / reason |",
                "|---|---|---|---|",
            ]
            for window in candidate["controller_gpio_windows"]:
                controllers = ", ".join(f"`{controller}`" for controller in window["controllers"])
                lines.append(
                    f"| `{window['instance']}` | {controllers} | "
                    f"`GPIO{window['gpio_min']}..GPIO{window['gpio_max']}` | {window['reason']} |"
                )

        if candidate.get("capacity_contracts"):
            lines += [
                "",
                "### Controller/DMA capacity accounting",
                "",
                "| Capacity | Instance | Claims | Reserve / available | Basis |",
                "|---|---|---|---:|---|",
            ]
            for capacity in candidate["capacity_contracts"]:
                claims = ", ".join(
                    f"{claim['consumer']}={claim['units']}" for claim in capacity["claims"]
                )
                lines.append(
                    f"| `{capacity['id']}` | `{capacity['instance']}` | {claims} | "
                    f"{capacity['reserve']} / {capacity['available']} | {capacity['proof']} |"
                )

        if candidate.get("mux_contracts"):
            lines += [
                "",
                "### Exact fixed-mux contracts",
                "",
                "| Contract | Instance/controller | Exact contacts | Datasheet/device proof |",
                "|---|---|---|---|",
            ]
            for mux in candidate["mux_contracts"]:
                contacts = ", ".join(f"`{contact}`" for contact in mux["contacts"])
                lines.append(
                    f"| `{mux['id']}` | `{mux['instance']}.{mux['controller']}` | "
                    f"{contacts} | {mux['proof']} |"
                )

        lines += ["", "### Open qualification gaps", ""]
        automatic_gaps: list[str] = []
        for instance, device_id in candidate["instances"].items():
            device = devices[device_id]
            if device["qualification"] != "verified_candidate":
                automatic_gaps.append(
                    f"`{instance}` uses `{device['mpn']}` as `{device['qualification']}`, not an accepted production choice."
                )
            if device["lifecycle"] not in {"active", "active_candidate_revision_floor_v1_2"}:
                automatic_gaps.append(f"`{instance}` lifecycle: `{device['lifecycle']}`.")
        for gap in automatic_gaps + candidate.get("qualification_gaps", []):
            lines.append(f"- {gap}")

    lines += [
        "",
        "## Machine-check result and review boundary",
        "",
        "All source candidates pass structural validation: exact exposed contacts and programmable GPIO are accounted without collisions. For G2F-3I, non-MCU contacts, interface resources, controller windows, fixed-mux contacts, capacity arithmetic, signal groups, quiet states, power/safety paths, product geometry and the HW/FW boundary have also passed the joint pre-schematic review. G2F-3I therefore has status «Проведено ревью» as the target architecture. H1 final acceptance now authorizes H2 production-schematic work only; this status does not replace received-part, electrical, RF, thermal, acoustic or coexistence qualification and does not authorize PCB placement/routing.",
        "",
    ]
    return "\n".join(lines)


def _substitution_class_lookup(audit: dict[str, Any]) -> dict[str, str]:
    return {
        device_id: row["id"]
        for row in audit.get("substitution_policy", {}).get("classes", [])
        for device_id in row.get("device_ids", [])
    }


def _target_bom_lines(
    database: dict[str, Any], candidate: dict[str, Any]
) -> list[dict[str, Any]]:
    """Collapse physical instance names into exact-MPN quantity lines."""

    devices = database["devices"]
    audit = candidate["bom_audit"]
    non_purchase_instances = {
        row["instance"] for row in audit.get("non_purchase_instances", [])
    }
    substitution_class_by_device = _substitution_class_lookup(audit)
    grouped: dict[str, list[str]] = {}
    for instance, device_id in candidate["instances"].items():
        if instance in non_purchase_instances:
            continue
        grouped.setdefault(device_id, []).append(instance)

    result: list[dict[str, Any]] = []
    for device_id, placements in sorted(grouped.items()):
        device = devices[device_id]
        cost = device.get("cost")
        cost_gate = device.get("cost_gate")
        scopes = {
            audit.get("scope_overrides", {}).get(instance, audit["default_scope"])
            for instance in placements
        }
        scope = next(iter(scopes)) if len(scopes) == 1 else "+".join(sorted(scopes))
        result.append(
            {
                "scope": scope,
                "device_id": device_id,
                "mpn": device["mpn"],
                "quantity": len(placements),
                "lifecycle": device["lifecycle"],
                "qualification": device["qualification"],
                "orderable_evidence": "present" if device.get("orderable_source") else "missing",
                "cost_evidence": "present" if cost else "missing",
                "cost_currency": cost["currency"] if cost else "",
                "cost_target_quantity": cost["target_quantity"] if cost else "",
                "unit_price_usd": cost["unit_price_usd"] if cost else "",
                "line_material_usd": round(cost["unit_price_usd"] * len(placements), 4)
                if cost
                else "",
                "cost_price_break": cost["price_break"] if cost else "",
                "cost_source": cost["source"]["url"] if cost else "",
                "cost_checked": cost["source"]["checked"] if cost else "",
                "cost_gate_status": cost_gate["status"] if cost_gate else "",
                "cost_gate_reason": cost_gate["reason"] if cost_gate else "",
                "cost_gate_source": cost_gate["source"]["url"] if cost_gate else "",
                "cost_gate_checked": cost_gate["source"]["checked"] if cost_gate else "",
                "alternate_evidence": "present" if device_id in substitution_class_by_device else "missing",
                "alternate_policy_class": substitution_class_by_device.get(device_id, "missing"),
                "placements": sorted(placements),
            }
        )
    return result


def render_target_bom_review(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> str:
    """Render a narrow-screen I8 coverage review without pretending to be a quote."""

    candidate = next(candidate for candidate in candidates if candidate["id"] == "G2F-3I")
    audit = candidate["bom_audit"]
    devices = database["devices"]
    bom = _target_bom_lines(database, candidate)
    purchase_instance_count = sum(row["quantity"] for row in bom)
    architecture_instance_count = len(candidate["instances"])
    non_purchase_instances = audit.get("non_purchase_instances", [])
    non_purchase_node_word = "node" if len(non_purchase_instances) == 1 else "nodes"
    orderable = sum(row["orderable_evidence"] == "present" for row in bom)
    costed = sum(row["cost_evidence"] == "present" for row in bom)
    explicit_cost_gates = sum(bool(row["cost_gate_status"]) for row in bom)
    alternates = sum(row["alternate_evidence"] == "present" for row in bom)
    substitution_classes = {
        row["id"]: row
        for row in audit.get("substitution_policy", {}).get("classes", [])
    }
    scope_counts: dict[str, int] = {}
    covered_cost_scope_subtotals: dict[str, float] = {}
    costed_placements = 0
    for row in bom:
        scope_counts[row["scope"]] = scope_counts.get(row["scope"], 0) + row["quantity"]
        if row["cost_evidence"] == "present":
            costed_placements += row["quantity"]
            covered_cost_scope_subtotals[row["scope"]] = round(
                covered_cost_scope_subtotals.get(row["scope"], 0.0)
                + row["line_material_usd"],
                4,
            )

    lines = [
        "# G2F-3I — generated target BOM coverage review",
        "",
        "- Статус: **I8 paper procurement-feasibility scope reviewed; downstream G3/G8 qualification gated**",
        "- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`",
        "- Regenerate: `python3 hardware/architecture/generate.py --write`",
        "",
        "> Файл сгенерирован. Он показывает полноту входа в I8, а не выдаёт незакрытые строки за factory quote.",
        "",
        "## Что уже посчитано",
        "",
        f"- **{architecture_instance_count}** architecture instances include **{len(non_purchase_instances)}** explicit assembly-internal evidence {non_purchase_node_word}.",
        f"- After excluding those non-purchase nodes, **{purchase_instance_count}** supplied/costed placements collapse to **{len(bom)}** used exact-device/MPN lines.",
        f"- Current orderability evidence exists for **{orderable}/{len(bom)}** used lines; **{len(bom) - orderable}** need a current source check.",
        f"- Machine-readable quantity-100 cost evidence exists for **{costed}/{len(bom)}** lines.",
        f"- Of the remaining **{len(bom) - costed}** unpriced lines, **{explicit_cost_gates}** have an explicit RFQ/retail comparability gate instead of a fabricated numeric value.",
        f"- Those priced lines cover **{costed_placements}/{purchase_instance_count}** supplied placements; their partial subtotals are "
        + "; ".join(
            f"`{scope}` — USD {subtotal:.4f}"
            for scope, subtotal in sorted(covered_cost_scope_subtotals.items())
        )
        + ". These are coverage diagnostics, not product COGS.",
        f"- Machine-readable alternate/no-substitution evidence exists for **{alternates}/{len(bom)}** lines.",
        f"- Cost basis: {audit['cost_basis']}.",
        "",
        "Scopes: " + "; ".join(
            f"`{scope}` — {quantity} placements"
            for scope, quantity in sorted(scope_counts.items())
        )
        + ".",
        "",
        "The complete per-line manifest is the adjacent `G2F-3I-target-bom.csv`; unused comparison-device definitions are deliberately excluded.",
        "",
        "## Substitution/no-silent-replacement policy",
        "",
        "Every purchase line below belongs to exactly one validated class. A class is a disposition and requalification envelope, not a claim that a second MPN is already qualified.",
        "",
    ]
    for class_id, policy in substitution_classes.items():
        class_lines = [
            row for row in bom if row["alternate_policy_class"] == class_id
        ]
        lines += [
            f"<details><summary><code>{class_id}</code> — {policy['title']} — {len(class_lines)} line(s)</summary>",
            "",
            f"- Disposition: {policy['disposition']}.",
            "- Equivalence envelope:",
        ]
        lines.extend(f"  - {item}." for item in policy["equivalence_envelope"])
        lines += ["- Required requalification:"]
        lines.extend(f"  - {item}." for item in policy["requalification"])
        lines += ["- Current lines:"]
        lines.extend(
            f"  - `{row['device_id']}` — `{row['mpn']}`."
            for row in class_lines
        )
        lines += ["", "</details>", ""]
    lines += [
        "## Quantity-100 cost evidence",
        "",
        "Only exact-MPN published USD prices that apply to a 100-piece purchase are listed. Taxes, tariffs, freight, PCB, assembly, test, enclosure, yield and tooling are excluded. The sum below is intentionally partial while any purchase line remains unpriced.",
        "",
    ]
    for row in (row for row in bom if row["cost_evidence"] == "present"):
        lines += [
            f"<details><summary><code>{row['mpn']}</code> — {row['quantity']} × USD {row['unit_price_usd']:.4f} = USD {row['line_material_usd']:.4f}</summary>",
            "",
            f"- Device id: `{row['device_id']}`.",
            f"- Scope: `{row['scope']}`.",
            f"- Comparable basis: {row['cost_price_break']}; target quantity `{row['cost_target_quantity']}`.",
            f"- Checked: `{row['cost_checked']}`; [published source]({row['cost_source']}).",
            "",
            "</details>",
            "",
        ]
    lines += [
        "## Unpriced lines with explicit cost gates",
        "",
        "These entries are intentionally excluded from the partial subtotal until a comparable quantity-100 USD quote exists.",
        "",
    ]
    for row in (row for row in bom if row["cost_gate_status"]):
        lines += [
            f"<details><summary><code>{row['mpn']}</code> — <code>{row['cost_gate_status']}</code></summary>",
            "",
            f"- Device id: `{row['device_id']}`.",
            f"- Scope: `{row['scope']}`; quantity `{row['quantity']}`.",
            f"- Reason: {row['cost_gate_reason']}.",
            f"- Checked: `{row['cost_gate_checked']}`; [gate source]({row['cost_gate_source']}).",
            "",
            "</details>",
            "",
        ]
    lines += [
        "## Assembly-internal evidence nodes excluded from purchase BOM",
        "",
    ]
    for row in non_purchase_instances:
        instance = row["instance"]
        parent = row["parent_instance"]
        device = devices[candidate["instances"][instance]]
        lines += [
            f"- `{instance}` / `{device['mpn']}` is contained by `{parent}`: {row['reason']}.",
        ]
    lines += [
        "",
        "## Physical purchase families with explicit resolution gates",
        "",
    ]
    for gap in audit["required_uninstantiated_parts"]:
        gate = gap["resolution_gate"]
        lines += [
            f"### `{gap['id']}` — {gap['quantity']} item(s)",
            "",
            f"- Scope: `{gap['scope']}`.",
            f"- Role: {gap['role']}.",
            f"- Blocking evidence: {gap['blocker']}.",
            f"- Gate: `{gate['status']}`.",
            f"- Owner stage: {gate['owner_stage']}.",
            f"- Evidence chain: {', '.join(f'`{ref}`' for ref in gate['evidence_refs'])}.",
            "- Prerequisites:",
            *[f"  - {item}." for item in gate["prerequisites"]],
            "- Acceptance:",
            *[f"  - {item}." for item in gate["acceptance"]],
            "",
        ]

    missing_orderability = [
        row for row in bom if row["orderable_evidence"] == "missing"
    ]
    lines += [
        "## Used lines without current orderability evidence",
        "",
        "This is deliberately rendered as vertical cards so the document remains usable on a narrow screen.",
        "",
    ]
    for row in missing_orderability:
        lines += [
            f"<details><summary><code>{row['mpn']}</code> — qty {row['quantity']}</summary>",
            "",
            f"- Device id: `{row['device_id']}`",
            f"- Scope: `{row['scope']}`",
            f"- Lifecycle claim awaiting I8 recheck: `{row['lifecycle']}`",
            f"- Qualification: `{row['qualification']}`",
            f"- Placements: {', '.join(f'`{placement}`' for placement in row['placements'])}",
            "",
            "</details>",
            "",
        ]

    lines += [
        "## Non-MPN physical features",
        "",
    ]
    lines.extend(f"- {feature}." for feature in audit["pcb_features_not_mpn_lines"])
    lines += [
        "",
        "These need exact library/geometry and manufacturing rules, but must not be padded into component cost as fictitious purchased parts.",
        "",
        "## I8 exit",
        "",
        audit["exit"] + ".",
        "",
        "Until those conditions pass, the BOM has **not** received «Проведено ревью», no total COGS is claimed and PCB placement/routing, fabrication and purchasing remain unauthorized.",
        "",
    ]
    return "\n".join(lines)


def _csv_cell(value: Any) -> str:
    value_text = str(value)
    return '"' + value_text.replace('"', '""') + '"'


def render_target_bom_csv(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> str:
    candidate = next(candidate for candidate in candidates if candidate["id"] == "G2F-3I")
    columns = (
        "scope",
        "device_id",
        "mpn",
        "quantity",
        "lifecycle",
        "qualification",
        "orderable_evidence",
        "cost_evidence",
        "cost_currency",
        "cost_target_quantity",
        "unit_price_usd",
        "line_material_usd",
        "cost_price_break",
        "cost_source",
        "cost_checked",
        "cost_gate_status",
        "cost_gate_reason",
        "cost_gate_source",
        "cost_gate_checked",
        "alternate_evidence",
        "alternate_policy_class",
        "placements",
    )
    rows = [",".join(_csv_cell(column) for column in columns)]
    for line in _target_bom_lines(database, candidate):
        values = dict(line)
        values["placements"] = ";".join(line["placements"])
        rows.append(",".join(_csv_cell(values[column]) for column in columns))
    return "\n".join(rows) + "\n"


MERMAID_RENDER_LIMIT = 12_000
MERMAID_NODE_CHUNK_LIMIT = 4_200


def _mermaid_node_id(line: str) -> str | None:
    """Return a declared Mermaid node ID, excluding subgraphs and edges."""

    match = re.match(r"^\s{2}([A-Z][A-Z0-9_]*)\s*(?:\[|\()", line)
    return match.group(1) if match else None


def _render_split_principled_atlas(raw_lines: list[str]) -> list[str]:
    """Split the exhaustive projection into bounded, renderable domain diagrams."""

    groups: list[dict[str, Any]] = []
    all_node_lines: dict[str, str] = {}
    current: dict[str, Any] | None = None
    final_group_end = -1
    for index, line in enumerate(raw_lines):
        subgraph_match = re.match(r'^\s{2}subgraph\s+([A-Z0-9_]+)\["(.*)"\]$', line)
        if subgraph_match:
            current = {
                "id": subgraph_match.group(1),
                "title": subgraph_match.group(2),
                "nodes": [],
            }
            groups.append(current)
            continue
        if current is not None and line == "  end":
            final_group_end = index
            current = None
            continue
        if current is not None:
            node_id = _mermaid_node_id(line)
            if node_id:
                current["nodes"].append(node_id)
                all_node_lines[node_id] = line

    edge_lines = [
        line
        for line in raw_lines[final_group_end + 1 :]
        if any(token in line for token in ("-->", "<-->", "-.->"))
    ]
    all_node_ids = set(all_node_lines)
    edge_refs: list[tuple[str, set[str]]] = []
    for line in edge_lines:
        unlabeled = re.sub(r'\|".*?"\|', "", line)
        refs = set(re.findall(r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]*)(?![A-Z0-9_])", unlabeled))
        if refs and refs <= all_node_ids:
            edge_refs.append((line, refs))

    titles = {
        "COMPUTE": "Вычислительные владельцы и межпроцессорные связи",
        "UI_STORAGE": "Экран, storage и органы управления",
        "AUDIO_PATH": "Приём, запись, воспроизведение и voice audio",
        "RADIO_ACCESSORY": "Радиотракты и внешние расширения",
        "IR_PATH": "Инфракрасный приём, передача и оптическое evidence",
        "SERVICE_RECOVERY": "Независимая прошивка, recovery и диагностика",
        "SAFETY_STOP": "Always-on RUN/KILL, watchdog и аппаратный запрет передачи",
        "TX_EVIDENCE": "Физическое evidence фактической передачи",
        "POWER_RAILS": "Независимые rails и тихое отключение неиспользуемых интерфейсов",
        "POWER_INPUT": "USB-PD, зарядка, сменные элементы и допуск батареи",
    }
    order = tuple(titles)
    group_by_id = {group["id"]: group for group in groups}
    ordered_groups = [group_by_id[group_id] for group_id in order if group_id in group_by_id]
    ordered_groups.extend(group for group in groups if group["id"] not in order)

    context_by_group = {
        "SERVICE_RECOVERY": ("S3", "C5", "RP"),
        "UI_STORAGE": ("S3", "MAIN_EFUSE"),
        "AUDIO_PATH": ("S3", "RP", "SLOW_IO", "MAIN_EFUSE", "VOICE_EFUSE"),
        "RADIO_ACCESSORY": (
            "S3", "C5", "RP", "SLOW_IO", "MAIN_EFUSE", "SAFE_GATE_A", "SAFE_GATE_B",
            "DET_S3", "DET_C5", "DET_NRF0", "DET_NRF1", "DET_NRF2", "DET_CC",
            "DET_VOICE", "EVIDENCE_CMP_A", "EVIDENCE_CMP_B",
        ),
        "IR_PATH": ("C5", "SAFE_GATE_B", "DET_IR"),
        "SAFETY_STOP": ("S3", "C5", "RP", "SLOW_IO", "AON_EFUSE"),
        "TX_EVIDENCE": ("S3", "C5", "RP", "SLOW_IO", "SAFE_GATE_A", "SAFE_GATE_B"),
        "POWER_RAILS": (
            "NVDC_CHARGER", "S3", "C5", "RP", "SLOW_IO", "VOICE", "U214"
        ),
        "POWER_INPUT": ("AON_BUCK", "MAIN_BUCK", "VOICE_BUCK", "EXT_BUCK"),
    }

    rendered: list[str] = []
    diagram_number = 0
    rendered_node_ids: set[str] = set()
    for group in ordered_groups:
        node_chunks: list[list[str]] = []
        chunk: list[str] = []
        chunk_size = 0
        for node_id in group["nodes"]:
            node_size = len(all_node_lines[node_id]) + 1
            if chunk and chunk_size + node_size > MERMAID_NODE_CHUNK_LIMIT:
                node_chunks.append(chunk)
                chunk = []
                chunk_size = 0
            chunk.append(node_id)
            chunk_size += node_size
        if chunk:
            node_chunks.append(chunk)

        for chunk_number, node_ids in enumerate(node_chunks, 1):
            context_ids = [
                node_id
                for node_id in context_by_group.get(group["id"], ())
                if node_id in all_node_lines and node_id not in node_ids
            ]
            available_ids = set(node_ids) | set(context_ids)
            internal_edges = [
                line
                for line, refs in edge_refs
                if refs <= available_ids and refs & set(node_ids)
            ]
            base_lines = [
                "flowchart TD",
                f'  subgraph {group["id"]}_{chunk_number}["{group["title"]}"]',
                *[all_node_lines[node_id] for node_id in context_ids],
                *[all_node_lines[node_id] for node_id in node_ids],
                "  end",
            ]
            spine_ids = context_ids + node_ids
            for offset in range(0, len(spine_ids), 12):
                spine = spine_ids[offset : offset + 12]
                if len(spine) > 1:
                    base_lines.append("  " + " ~~~ ".join(spine))

            edge_batches: list[list[str]] = [[]]
            current_size = len("\n".join(base_lines)) + 1
            for edge in internal_edges:
                edge_size = len(edge) + 1
                if edge_batches[-1] and current_size + edge_size >= MERMAID_RENDER_LIMIT:
                    edge_batches.append([])
                    current_size = len("\n".join(base_lines)) + 1
                edge_batches[-1].append(edge)
                current_size += edge_size

            for edge_batch_number, edge_batch in enumerate(edge_batches, 1):
                diagram_number += 1
                title = titles.get(group["id"], group["title"])
                part_count = len(node_chunks)
                if part_count > 1:
                    title += f" — узлы {chunk_number}/{part_count}"
                if len(edge_batches) > 1:
                    title += f", связи {edge_batch_number}/{len(edge_batches)}"
                diagram_lines = base_lines + edge_batch
                diagram = "\n".join(diagram_lines)
                if len(diagram) >= MERMAID_RENDER_LIMIT:
                    raise ValueError(
                        f"split Mermaid block {group['id']} remains too large: {len(diagram)}"
                    )
                rendered += [
                    f"### {diagram_number}. {title}",
                    "",
                    "```mermaid",
                    diagram,
                    "```",
                    "",
                ]
            rendered_node_ids.update(node_ids)

    if rendered_node_ids != all_node_ids:
        missing = sorted(all_node_ids - rendered_node_ids)
        extra = sorted(rendered_node_ids - all_node_ids)
        raise ValueError(f"split Mermaid atlas coverage mismatch: missing={missing}, extra={extra}")
    return rendered


def _target_node(
    devices: dict[str, Any], candidate: dict[str, Any], instance: str, role: str
) -> str:
    mpn = devices[candidate["instances"][instance]]["mpn"]
    return f'{instance.upper()}["{mpn}<br/>{role}"]'


def render_target_principled_section(
    database: dict[str, Any], candidates: list[dict[str, Any]], *, russian: bool
) -> str:
    """Render the bounded landing-page maps from the current machine sources."""

    candidate = next(candidate for candidate in candidates if candidate["id"] == "G2F-3I")
    devices = database["devices"]
    if russian:
        heading = "## Принципиальный дизайн решения"
        intro = [
            "Архитектура читается от трёх вычислительных владельцев, а не от USB-порта.",
            "Первая схема показывает только межпроцессорные связи; следующие схемы",
            "разворачивают устройства каждого владельца и отдельный тракт питания.",
            "Каждый прямоугольник — одно физическое устройство с выбранным партномером",
            "или явной пометкой «партномер не выбран», а также его ролью в продукте.",
        ]
        labels = {
            "owners": "Карта вычислительных владельцев",
            "s3": "S3: интерфейс пользователя, storage, audio и native expansion",
            "c5": "C5: native 2,4/5 ГГц, 802.15.4 и IR",
            "rp": "RP: детерминированные радио, voice и Cap Bus",
            "controls": "Органы управления: от физической кнопки до владельца",
            "audio": "Аудиотракт: приём, запись, воспроизведение и передача",
            "service": "Прошивка, восстановление и диагностика трёх вычислителей",
            "rf_ports": "Девять независимых антенных портов",
            "power": "Питание как отдельный тракт",
            "safety": "RUN/KILL, watchdog, thermal и подтверждение фактической передачи",
        }
        roles = {
            "s3": "приложение, UI, экран, storage, audio, BLE/Wi-Fi",
            "c5": "native 2,4/5 ГГц, IEEE 802.15.4 и IR",
            "rp": "детерминированные радио и voice",
            "display": "3,5-дюймовый QSPI экран и touch assembly",
            "sd": "push-push разъём microSD",
            "slow_io": "24-линейный slow-control expander",
            "ui_matrix_io": "16 прямых входов D-pad и функциональных кнопок",
            "ui_dpad_up": "отдельная кнопка навигации ВВЕРХ",
            "ui_dpad_down": "отдельная кнопка навигации ВНИЗ",
            "ui_dpad_left": "отдельная кнопка навигации ВЛЕВО",
            "ui_dpad_right": "отдельная кнопка навигации ВПРАВО",
            "ui_dpad_ok": "отдельная кнопка подтверждения OK",
            "ui_switch_back": "кнопка BACK",
            "ui_switch_opt": "кнопка OPT",
            "ui_switch_f1": "левая кнопка у экрана F1",
            "ui_switch_f2": "левая кнопка у экрана F2",
            "ui_switch_f3": "левая кнопка у экрана F3",
            "ui_switch_f4": "левая кнопка у экрана F4",
            "ui_switch_f5": "правая кнопка у экрана F5",
            "ui_switch_f6": "правая кнопка у экрана F6",
            "ui_switch_f7": "правая кнопка у экрана F7",
            "ui_switch_f8": "правая кнопка у экрана F8",
            "encoder": "задний энкодер с нажатием",
            "ptt_switch": "независимая задняя кнопка PTT",
            "codec": "кодек записи и воспроизведения",
            "receiver": "приёмник FM/AM/SW/LW",
            "audio_rx_mux": "выбор источника принимаемого звука",
            "audio_capture_selector": "выбор microphone/RX для записи",
            "audio_capture_buffer": "буфер АЦП кодека",
            "codec_supervisor": "контроль готовности питания кодека",
            "codec_i2s_din_boot_gate": "аппаратный gate CODEC_READY AND AUDIO_ARM",
            "codec_i2s_din_iso": "трёхстабильный буфер capture data на boot GPIO0",
            "audio_speaker_selector": "выбор RX-bypass/codec для динамика",
            "audio_tx_selector": "выбор microphone/codec для voice TX",
            "speaker_amp": "дифференциальный усилитель динамика",
            "speaker": "внутренний 4-Ом динамик",
            "microphone": "внутренний электретный микрофон",
            "headphone_jack": "гарнитурный разъём 3,5 мм CTIA с detect",
            "headset_mic_selector": "выбор встроенного/гарнитурного микрофона",
            "headset_control_io": "выделенное управление гарнитурой и 7 резервных I/O",
            "ir_demod": "демодулирующий IR-приёмник 38 кГц",
            "ir_carrier": "IR-приёмник обучения несущей",
            "ir_emitter": "IR-передатчик 940 нм",
            "nrf0": "полнофункциональное nRF24-радио №0",
            "nrf1": "полнофункциональное nRF24-радио №1",
            "nrf2": "полнофункциональное nRF24-радио №2",
            "cc": "многодиапазонный sub-GHz transceiver",
            "voice": "аналоговый VHF/UHF voice transceiver",
            "u214": "съёмный LoRa/GNSS Cap-модуль",
            "u214_connector": "вертикальный 14-контактный host Cap-Bus на поднятой планке",
            "unit_connector": "защищённый разъём M5 Unit HY2.0-4P",
            "s3_external_rp_sma": "внешний RP-SMA порт S3 2,4 ГГц",
            "c5_external_rp_sma": "внешний RP-SMA порт C5 2,4/5 ГГц",
            "receiver_fmsw_external_sma": "приёмный SMA порт FM/SW",
            "receiver_amlw_external_sma": "не-50-омный SMA порт AM/LW loop/pod",
            "nrf0_external_sma": "независимый SMA порт nRF24 №0",
            "nrf1_external_sma": "независимый SMA порт nRF24 №1",
            "nrf2_external_sma": "независимый SMA порт nRF24 №2",
            "cc_external_sma": "многодиапазонный SMA порт sub-GHz",
            "voice_external_sma": "SMA порт VHF/UHF voice",
            "product_usb_connector": "основной USB-C разъём",
            "product_usb_protector": "защита CC и USB2 порта",
            "c5_service_usb_connector": "data-only USB-C восстановления C5",
            "c5_service_usb_switch": "power-off-защищённый USB2 ключ C5",
            "rp_service_usb_connector": "data-only USB-C восстановления RP",
            "rp_service_usb_switch": "power-off-защищённый USB2 ключ RP",
            "s3_dbg_header": "внутренний резервный DBG10: UART0/RESET/BOOT",
            "c5_dbg_header": "внутренний резервный DBG10: UART0/RESET/BOOT",
            "rp_dbg_header": "внутренний резервный DBG10: SWD/RUN/USB_BOOT",
            "s3_reset_button": "внешняя боковая кнопка RESET S3",
            "s3_boot_button": "внешняя боковая кнопка BOOT S3",
            "c5_reset_button": "внешняя боковая кнопка RESET C5",
            "c5_boot_button": "внешняя боковая кнопка BOOT C5",
            "rp_reset_button": "внешняя боковая кнопка RUN/RESET RP",
            "rp_boot_button": "внешняя боковая кнопка USB_BOOT RP",
            "pd_vbus_tvs": "шунтирующая защита VBUS 22 В",
            "pd_controller": "sink-only USB-PD контроллер",
            "nvdc_charger": "2S зарядка и NVDC power path",
            "pack_holder": "поляризованный держатель двух 18650",
            "pack_gauge": "защита и fuel gauge батареи 2S",
            "pack_admission": "локальный fail-closed контроллер допуска 2S pack",
            "power_command_switch": "единственный малотоковый переключатель RUN/KILL",
            "aon_buck": "always-on преобразователь безопасности 3,3 В",
            "main_buck": "основной преобразователь 3,3 В",
            "voice_buck": "преобразователь voice 4,0 В",
            "ext_buck": "преобразователь расширений 5,0 В",
            "safe_supervisor": "контроль always-on питания безопасности",
            "safety_controller": "независимый AON-контроллер watchdog, thermal и TX lease",
            "safety_watchdog": "независимый timeout-watchdog 1,6 с",
            "safe_conditioner": "формирователь физического RUN и S3 fault reset",
            "safe_latch": "асинхронная защёлка FAULT_KILL",
            "safe_gate_a": "аппаратные разрешения трёх nRF24 и их питания",
            "safe_gate_b": "аппаратные разрешения CC, voice и расширений",
            "ir_safe_gate": "локальное аппаратное разрешение IR carrier",
            "evidence_cmp_a": "UI-компаратор фактического TX S3, C5 и IR",
            "evidence_cmp_b": "RF-компаратор фактического TX 3×nRF24 и CC",
            "evidence_cmp_voice": "отдельный RF-компаратор фактического voice TX",
            "evidence_mask": "16-битный AON-регистр маски девяти источников TX",
            "ext_evidence_buffer": "5-В-стойкая развязка evidence от LoRa Cap",
            "evidence_or_0": "диодное объединение evidence S3 и C5",
            "evidence_or_1": "диодное объединение evidence nRF24 №1 и №2",
            "evidence_or_2": "диодное объединение evidence nRF24 №3 и Sub-GHz",
            "evidence_or_3": "диодное объединение evidence voice и IR",
            "evidence_or_4": "диодное объединение evidence LoRa/EXT",
            "evidence_main_isolator": "развязка цифровых TX-свидетельств в main domain",
        }
        atlas_text = (
            "[Полный отрисовываемый атлас всех физических устройств]"
            "(hardware/architecture/generated/G2F-3I-principled-pinout.md) разбит"
            " на ограниченные Mermaid-диаграммы. Исходная монолитная проекция для"
            " машинного ревью сохраняется отдельно в"
            " [`G2F-3I-principled-projection.mmd`]"
            "(hardware/architecture/generated/G2F-3I-principled-projection.mmd)."
        )
    else:
        heading = "## Principled solution design"
        intro = [
            "Read the architecture from its three compute owners, not from the USB port.",
            "The first map shows only inter-processor links; the following maps expand",
            "each owner's devices and the independent power path. Every box is one",
            "physical device with its selected part number or an explicit ‘not selected’",
            "mark and product role; no box combines different devices.",
        ]
        labels = {
            "owners": "Compute ownership map",
            "s3": "S3: user interface, storage, audio and native expansion",
            "c5": "C5: native 2.4/5 GHz, 802.15.4 and IR",
            "rp": "RP: deterministic radios, voice and Cap Bus",
            "controls": "Controls: from each physical switch to its owner",
            "audio": "Audio path: receive, capture, playback and transmit",
            "service": "Programming, recovery and diagnostics for all three compute owners",
            "rf_ports": "Nine independent antenna ports",
            "power": "Power as an independent path",
            "safety": "RUN/KILL, watchdog, thermal supervision and physical TX evidence",
        }
        roles = {
            "s3": "application, UI, display, storage, audio, BLE/Wi-Fi owner",
            "c5": "native 2.4/5-GHz, IEEE 802.15.4 and IR owner",
            "rp": "deterministic radio and voice owner",
            "display": "3.5-inch QSPI display and touch assembly",
            "sd": "push-push microSD connector",
            "slow_io": "24-line slow-control expander",
            "ui_matrix_io": "16 direct D-pad and function-key inputs",
            "ui_dpad_up": "independent UP navigation button",
            "ui_dpad_down": "independent DOWN navigation button",
            "ui_dpad_left": "independent LEFT navigation button",
            "ui_dpad_right": "independent RIGHT navigation button",
            "ui_dpad_ok": "independent OK confirmation button",
            "ui_switch_back": "BACK button",
            "ui_switch_opt": "OPT button",
            "ui_switch_f1": "left display-side F1 button",
            "ui_switch_f2": "left display-side F2 button",
            "ui_switch_f3": "left display-side F3 button",
            "ui_switch_f4": "left display-side F4 button",
            "ui_switch_f5": "right display-side F5 button",
            "ui_switch_f6": "right display-side F6 button",
            "ui_switch_f7": "right display-side F7 button",
            "ui_switch_f8": "right display-side F8 button",
            "encoder": "rear rotary encoder with push",
            "ptt_switch": "independent rear PTT button",
            "codec": "audio capture and playback codec",
            "receiver": "FM/AM/SW/LW broadcast receiver",
            "audio_rx_mux": "received-audio source selector",
            "audio_capture_selector": "microphone/RX capture selector",
            "audio_capture_buffer": "codec ADC buffer",
            "codec_supervisor": "codec-power readiness supervisor",
            "codec_i2s_din_boot_gate": "hardware CODEC_READY AND AUDIO_ARM gate",
            "codec_i2s_din_iso": "capture-data tri-state buffer onto boot GPIO0",
            "audio_speaker_selector": "RX-bypass/codec speaker selector",
            "audio_tx_selector": "microphone/codec voice-TX selector",
            "speaker_amp": "differential speaker amplifier",
            "speaker": "internal 4-Ohm speaker",
            "microphone": "internal electret microphone",
            "headphone_jack": "3.5-mm CTIA headset jack with detect",
            "headset_mic_selector": "internal/headset microphone selector",
            "headset_control_io": "dedicated headset control and 7 reserve I/O lines",
            "ir_demod": "38-kHz demodulating IR receiver",
            "ir_carrier": "carrier-learning IR receiver",
            "ir_emitter": "940-nm IR transmitter",
            "nrf0": "full-function nRF24 radio #0",
            "nrf1": "full-function nRF24 radio #1",
            "nrf2": "full-function nRF24 radio #2",
            "cc": "multi-band sub-GHz transceiver",
            "voice": "analog VHF/UHF voice transceiver",
            "u214": "removable LoRa/GNSS Cap module",
            "u214_connector": "vertical 14-contact Cap-Bus host on raised rear rail",
            "unit_connector": "protected M5 Unit HY2.0-4P connector",
            "s3_external_rp_sma": "external S3 2.4-GHz RP-SMA port",
            "c5_external_rp_sma": "external C5 2.4/5-GHz RP-SMA port",
            "receiver_fmsw_external_sma": "receive-only FM/SW SMA port",
            "receiver_amlw_external_sma": "non-50-Ohm AM/LW loop/pod SMA port",
            "nrf0_external_sma": "independent nRF24 #0 SMA port",
            "nrf1_external_sma": "independent nRF24 #1 SMA port",
            "nrf2_external_sma": "independent nRF24 #2 SMA port",
            "cc_external_sma": "multi-band sub-GHz SMA port",
            "voice_external_sma": "VHF/UHF voice SMA port",
            "product_usb_connector": "product USB-C receptacle",
            "product_usb_protector": "CC and USB2 port protector",
            "c5_service_usb_connector": "data-only C5 recovery USB-C",
            "c5_service_usb_switch": "power-off-protected C5 USB2 switch",
            "rp_service_usb_connector": "data-only RP recovery USB-C",
            "rp_service_usb_switch": "power-off-protected RP USB2 switch",
            "s3_dbg_header": "internal fallback DBG10: UART0/RESET/BOOT",
            "c5_dbg_header": "internal fallback DBG10: UART0/RESET/BOOT",
            "rp_dbg_header": "internal fallback DBG10: SWD/RUN/USB_BOOT",
            "s3_reset_button": "external side S3 RESET button",
            "s3_boot_button": "external side S3 BOOT button",
            "c5_reset_button": "external side C5 RESET button",
            "c5_boot_button": "external side C5 BOOT button",
            "rp_reset_button": "external side RP RUN/RESET button",
            "rp_boot_button": "external side RP USB_BOOT button",
            "pd_vbus_tvs": "22-V VBUS shunt protector",
            "pd_controller": "sink-only USB-PD controller",
            "nvdc_charger": "2S charger and NVDC power path",
            "pack_holder": "polarized dual-18650 holder",
            "pack_gauge": "2S protection and fuel gauge",
            "pack_admission": "local fail-closed 2S pack admission controller",
            "power_command_switch": "single maintained low-current RUN/KILL switch",
            "aon_buck": "always-on 3.3-V safety converter",
            "main_buck": "main 3.3-V converter",
            "voice_buck": "voice 4.0-V converter",
            "ext_buck": "accessory 5.0-V converter",
            "safe_supervisor": "always-on safety-rail supervisor",
            "safety_controller": "independent AON watchdog, thermal and TX-lease controller",
            "safety_watchdog": "independent 1.6-s timeout watchdog",
            "safe_conditioner": "physical RUN and S3 fault-reset conditioner",
            "safe_latch": "asynchronous FAULT_KILL latch",
            "safe_gate_a": "hardware permits for three nRF24 radios and their rail",
            "safe_gate_b": "hardware permits for CC, voice and expansion",
            "ir_safe_gate": "local hardware permit for the IR carrier",
            "evidence_cmp_a": "UI-local physical-TX comparator for S3, C5 and IR",
            "evidence_cmp_b": "RF-local physical-TX comparator for 3×nRF24 and CC",
            "evidence_cmp_voice": "dedicated RF-local physical voice-TX comparator",
            "evidence_mask": "16-bit AON mask register for nine TX evidence sources",
            "ext_evidence_buffer": "5-V-tolerant LoRa Cap evidence boundary",
            "evidence_or_0": "S3 and C5 evidence diode combiner",
            "evidence_or_1": "nRF24 #1 and #2 evidence diode combiner",
            "evidence_or_2": "nRF24 #3 and sub-GHz evidence diode combiner",
            "evidence_or_3": "voice and IR evidence diode combiner",
            "evidence_or_4": "LoRa/EXT evidence diode combiner",
            "evidence_main_isolator": "digital TX-evidence isolation into the main domain",
        }
        atlas_text = (
            "The [complete rendered physical-device atlas]"
            "(hardware/architecture/generated/G2F-3I-principled-pinout.md) is split"
            " into bounded Mermaid diagrams. The original monolithic projection remains"
            " available for machine review as"
            " [`G2F-3I-principled-projection.mmd`]"
            "(hardware/architecture/generated/G2F-3I-principled-projection.mmd)."
        )

    node = lambda instance: _target_node(devices, candidate, instance, roles[instance])
    diagrams = [
        (
            labels["owners"],
            [node("s3"), node("c5"), node("rp")],
            ['  S3 <-->|"1-bit SDIO"| C5', '  S3 <-->|"dedicated SPI3 + alert"| RP'],
        ),
        (
            labels["s3"],
            [
                node("s3"), node("display"), node("sd"), node("slow_io"),
                node("ui_matrix_io"), node("codec"), node("receiver"),
                node("unit_connector"),
            ],
            [
                '  S3 -->|"direct QSPI + touch"| DISPLAY',
                '  S3 -->|"scheduled SPI + isolated rail"| SD',
                '  S3 <-->|"I²C0 + wired-low IRQ"| SLOW_IO',
                '  S3 <-->|"I²C0 + wired-low IRQ"| UI_MATRIX_IO',
                '  S3 <-->|"isolated I²S0 + I²C0"| CODEC',
                '  S3 <-->|"isolated I²C0"| RECEIVER',
                '  S3 <-->|"isolated profile pair"| UNIT_CONNECTOR',
            ],
        ),
        (
            labels["c5"],
            [node("c5"), node("ir_demod"), node("ir_carrier"), node("ir_emitter")],
            [
                '  C5 <-->|"RMT RX0"| IR_DEMOD',
                '  C5 <-->|"RMT RX1"| IR_CARRIER',
                '  C5 -->|"RMT TX + FAULT_KILL-qualified power"| IR_EMITTER',
            ],
        ),
        (
            labels["rp"],
            [
                node("rp"), node("nrf0"), node("nrf1"), node("nrf2"),
                node("cc"), node("voice"), node("u214_connector"), node("u214"),
            ],
            [
                '  RP <-->|"independent PIO0 SM0"| NRF0',
                '  RP <-->|"independent PIO0 SM1"| NRF1',
                '  RP <-->|"independent PIO0 SM2"| NRF2',
                '  RP <-->|"independent PIO0 SM3"| CC',
                '  RP <-->|"UART0 + direct PTT"| VOICE',
                '  RP <-->|"PIO1 + UART1 + I²C0"| U214_CONNECTOR',
                '  U214_CONNECTOR <-->|"2×7 · 2.54 mm · contacts 1…14"| U214',
            ],
        ),
        (
            labels["controls"],
            [
                node("s3"), node("rp"), node("ui_matrix_io"),
                node("ui_dpad_up"), node("ui_dpad_down"),
                node("ui_dpad_left"), node("ui_dpad_right"), node("ui_dpad_ok"),
                node("ui_switch_back"),
                node("ui_switch_opt"), node("ui_switch_f1"),
                node("ui_switch_f2"), node("ui_switch_f3"), node("ui_switch_f4"),
                node("ui_switch_f5"), node("ui_switch_f6"), node("ui_switch_f7"),
                node("ui_switch_f8"), node("encoder"), node("ptt_switch"),
                node("power_command_switch"), node("safety_controller"),
                node("safety_watchdog"), node("safe_conditioner"), node("safe_latch"),
            ],
            [
                '  UI_DPAD_UP -->|"direct P00"| UI_MATRIX_IO',
                '  UI_DPAD_DOWN -->|"direct P01"| UI_MATRIX_IO',
                '  UI_DPAD_LEFT -->|"direct P02"| UI_MATRIX_IO',
                '  UI_DPAD_RIGHT -->|"direct P03"| UI_MATRIX_IO',
                '  UI_DPAD_OK -->|"direct P04"| UI_MATRIX_IO',
                '  UI_SWITCH_BACK -->|"direct P05"| UI_MATRIX_IO',
                '  UI_SWITCH_OPT -->|"direct P06"| UI_MATRIX_IO',
                '  UI_SWITCH_F3 -->|"direct P07"| UI_MATRIX_IO',
                '  UI_SWITCH_F1 -->|"direct P10"| UI_MATRIX_IO',
                '  UI_SWITCH_F2 -->|"direct P11"| UI_MATRIX_IO',
                '  ENCODER -->|"push P12 across M1"| UI_MATRIX_IO',
                '  UI_SWITCH_F4 -->|"direct P13"| UI_MATRIX_IO',
                '  UI_SWITCH_F5 -->|"direct P14"| UI_MATRIX_IO',
                '  UI_SWITCH_F6 -->|"direct P15"| UI_MATRIX_IO',
                '  UI_SWITCH_F7 -->|"direct P16"| UI_MATRIX_IO',
                '  UI_SWITCH_F8 -->|"direct P17"| UI_MATRIX_IO',
                '  UI_MATRIX_IO -->|"I²C0 + IRQ"| S3',
                '  ENCODER -->|"A/B direct PCNT"| S3',
                '  PTT_SWITCH -->|"direct active-low PTT"| RP',
                '  POWER_COMMAND_SWITCH -->|"physical KILL / RUN edge"| SAFE_CONDITIONER',
                '  SAFETY_CONTROLLER -->|"deadline service"| SAFETY_WATCHDOG',
                '  SAFETY_WATCHDOG -->|"WDO_N"| SAFE_LATCH',
                '  SAFE_CONDITIONER -->|"KILL / physical re-arm clock"| SAFE_LATCH',
            ],
        ),
        (
            labels["audio"],
            [
                node("s3"), node("slow_io"), node("receiver"), node("voice"),
                node("microphone"), node("headset_control_io"),
                node("headset_mic_selector"), node("audio_rx_mux"),
                node("audio_capture_selector"), node("audio_capture_buffer"),
                node("codec"), node("codec_supervisor"),
                node("codec_i2s_din_boot_gate"), node("codec_i2s_din_iso"),
                node("audio_speaker_selector"),
                node("audio_tx_selector"), node("speaker_amp"),
                node("speaker"), node("headphone_jack"),
            ],
            [
                '  RECEIVER -->|"FM/AM/SW/LW audio"| AUDIO_RX_MUX',
                '  VOICE -->|"received AF"| AUDIO_RX_MUX',
                '  AUDIO_RX_MUX -->|"selected RX"| AUDIO_CAPTURE_SELECTOR',
                '  MICROPHONE -->|"guarded internal MIC_RAW across M1"| HEADSET_MIC_SELECTOR',
                '  HEADPHONE_JACK -->|"CTIA sleeve microphone"| HEADSET_MIC_SELECTOR',
                '  HEADPHONE_JACK -->|"detect-only tip switch"| SLOW_IO',
                '  S3 -->|"I²C0 · address 0x39"| HEADSET_CONTROL_IO',
                '  HEADSET_CONTROL_IO -->|"dedicated P0 source select"| HEADSET_MIC_SELECTOR',
                '  HEADSET_MIC_SELECTOR -->|"selected microphone"| AUDIO_CAPTURE_SELECTOR',
                '  AUDIO_CAPTURE_SELECTOR --> AUDIO_CAPTURE_BUFFER --> CODEC',
                '  S3 -->|"I²S0 outputs + I²C0 control"| CODEC',
                '  CODEC -->|"ASDOUT capture"| CODEC_I2S_DIN_ISO -->|"I²S DIN on GPIO0"| S3',
                '  CODEC_SUPERVISOR -->|"CODEC_READY"| CODEC_I2S_DIN_BOOT_GATE',
                '  S3 -->|"GPIO6 AUDIO_ARM; reset-low"| CODEC_I2S_DIN_BOOT_GATE',
                '  CODEC_I2S_DIN_BOOT_GATE -->|"output enable"| CODEC_I2S_DIN_ISO',
                '  AUDIO_RX_MUX -->|"reset-default receive bypass"| AUDIO_SPEAKER_SELECTOR',
                '  CODEC -->|"differential playback"| AUDIO_SPEAKER_SELECTOR',
                '  AUDIO_SPEAKER_SELECTOR -->|"differential low-level across M1"| SPEAKER_AMP',
                '  SPEAKER_AMP -->|"filtered BTL"| SPEAKER',
                '  CODEC -->|"stereo CTIA tip/ring1"| HEADPHONE_JACK',
                '  HEADSET_MIC_SELECTOR -->|"internal/headset voice source"| AUDIO_TX_SELECTOR',
                '  CODEC -->|"generated/processed voice source"| AUDIO_TX_SELECTOR',
                '  AUDIO_TX_SELECTOR -->|"isolated microphone input"| VOICE',
            ],
        ),
        (
            labels["service"],
            [
                node("s3"), node("product_usb_connector"),
                node("product_usb_protector"), node("s3_dbg_header"),
                node("s3_reset_button"), node("s3_boot_button"),
                node("c5"), node("c5_service_usb_connector"),
                node("c5_service_usb_switch"), node("c5_dbg_header"),
                node("c5_reset_button"), node("c5_boot_button"),
                node("rp"), node("rp_service_usb_connector"),
                node("rp_service_usb_switch"), node("rp_dbg_header"),
                node("rp_reset_button"), node("rp_boot_button"),
            ],
            [
                '  PRODUCT_USB_CONNECTOR <-->|"USB2 data"| PRODUCT_USB_PROTECTOR <-->|"native USB"| S3',
                '  S3_DBG_HEADER <-->|"UART0 + RESET + BOOT"| S3',
                '  S3_RESET_BUTTON -->|"RESET"| S3',
                '  S3_BOOT_BUTTON -->|"GPIO0; gated I²S_DIN only after boot"| S3',
                '  C5_SERVICE_USB_CONNECTOR <-->|"data only; VBUS sense only"| C5_SERVICE_USB_SWITCH <-->|"native USB"| C5',
                '  C5_DBG_HEADER <-->|"UART0 + RESET + BOOT"| C5',
                '  C5_RESET_BUTTON -->|"RESET"| C5',
                '  C5_BOOT_BUTTON -->|"GPIO28"| C5',
                '  RP_SERVICE_USB_CONNECTOR <-->|"data only; VBUS sense only"| RP_SERVICE_USB_SWITCH <-->|"native USB"| RP',
                '  RP_DBG_HEADER <-->|"SWD + RUN + USB_BOOT"| RP',
                '  RP_RESET_BUTTON -->|"RUN"| RP',
                '  RP_BOOT_BUTTON -->|"QSPI_SS / USB_BOOT"| RP',
            ],
        ),
        (
            labels["rf_ports"],
            [
                node("s3"), node("s3_external_rp_sma"),
                node("c5"), node("c5_external_rp_sma"),
                node("receiver"), node("receiver_fmsw_external_sma"),
                node("receiver_amlw_external_sma"),
                node("nrf0"), node("nrf0_external_sma"),
                node("nrf1"), node("nrf1_external_sma"),
                node("nrf2"), node("nrf2_external_sma"),
                node("cc"), node("cc_external_sma"),
                node("voice"), node("voice_external_sma"),
            ],
            [
                '  S3 -->|"50 Ω"| S3_EXTERNAL_RP_SMA',
                '  C5 -->|"50 Ω"| C5_EXTERNAL_RP_SMA',
                '  RECEIVER -->|"FM/SW receive"| RECEIVER_FMSW_EXTERNAL_SMA',
                '  RECEIVER -->|"AM/LW loop/pod"| RECEIVER_AMLW_EXTERNAL_SMA',
                '  NRF0 -->|"50 Ω"| NRF0_EXTERNAL_SMA',
                '  NRF1 -->|"50 Ω"| NRF1_EXTERNAL_SMA',
                '  NRF2 -->|"50 Ω"| NRF2_EXTERNAL_SMA',
                '  CC -->|"50 Ω"| CC_EXTERNAL_SMA',
                '  VOICE -->|"50 Ω"| VOICE_EXTERNAL_SMA',
            ],
        ),
        (
            labels["power"],
            [
                node("product_usb_connector"), node("product_usb_protector"), node("s3"),
                node("pd_vbus_tvs"), node("pd_controller"), node("nvdc_charger"),
                node("pack_holder"), node("pack_gauge"), node("pack_admission"),
                node("power_command_switch"), node("aon_buck"),
                node("main_buck"), node("voice_buck"), node("ext_buck"),
            ],
            [
                '  PRODUCT_USB_CONNECTOR <-->|"D+/D-"| PRODUCT_USB_PROTECTOR <-->|"protected USB2 GPIO19/20"| S3',
                '  PRODUCT_USB_CONNECTOR <-->|"CC1/CC2"| PRODUCT_USB_PROTECTOR <-->|"protected CC1/CC2"| PD_CONTROLLER',
                '  PRODUCT_USB_CONNECTOR -->|"VBUS sink only; never source"| PD_CONTROLLER',
                '  PRODUCT_USB_CONNECTOR -->|"VBUS shunt only"| PD_VBUS_TVS',
                '  PD_CONTROLLER -->|"negotiated protected HV input"| NVDC_CHARGER',
                '  PACK_HOLDER -->|"two removable cells"| PACK_GAUGE -->|"supervised 2S pack"| NVDC_CHARGER',
                '  POWER_COMMAND_SWITCH -->|"KILL: low-current pack shutdown; never load current"| PACK_ADMISSION',
                '  PACK_ADMISSION <-->|"local gauge admission and fault evidence"| PACK_GAUGE',
                '  NVDC_CHARGER -->|"VSYS"| AON_BUCK',
                '  NVDC_CHARGER -->|"VSYS"| MAIN_BUCK',
                '  NVDC_CHARGER -->|"VSYS"| VOICE_BUCK',
                '  NVDC_CHARGER -->|"VSYS"| EXT_BUCK',
            ],
        ),
        (
            labels["safety"],
            [
                node("power_command_switch"), node("safe_supervisor"),
                node("safety_controller"), node("safety_watchdog"),
                node("safe_conditioner"), node("safe_latch"),
                node("safe_gate_a"), node("safe_gate_b"), node("ir_safe_gate"),
                node("evidence_cmp_a"), node("evidence_cmp_b"),
                node("evidence_cmp_voice"), node("u214_connector"),
                node("ext_evidence_buffer"), node("evidence_mask"),
                node("evidence_or_0"), node("evidence_or_1"),
                node("evidence_or_2"), node("evidence_or_3"),
                node("evidence_or_4"),
                node("evidence_main_isolator"),
            ],
            [
                '  SAFE_SUPERVISOR -->|"power-on reset"| SAFE_LATCH',
                '  POWER_COMMAND_SWITCH -->|"KILL / physical RUN edge"| SAFE_CONDITIONER',
                '  SAFETY_CONTROLLER -->|"deadline service"| SAFETY_WATCHDOG',
                '  SAFETY_WATCHDOG -->|"WDO_N"| SAFE_LATCH',
                '  SAFE_CONDITIONER -->|"KILL / physical re-arm clock"| SAFE_LATCH',
                '  SAFE_LATCH -->|"RUN_PERMIT"| SAFE_GATE_A',
                '  SAFE_LATCH -->|"RUN_PERMIT"| SAFE_GATE_B',
                '  SAFE_LATCH -->|"one digital permit across M1"| IR_SAFE_GATE',
                '  EVIDENCE_CMP_A -->|"three UI-local digital evidence lines"| EVIDENCE_MASK',
                '  EVIDENCE_CMP_B -->|"four RF-local digital evidence lines"| EVIDENCE_MASK',
                '  EVIDENCE_CMP_VOICE -->|"one RF-local digital evidence line"| EVIDENCE_MASK',
                '  U214_CONNECTOR -->|"stock 5V_OUT high or qualified EXT_TX_EVIDENCE_N low"| EXT_EVIDENCE_BUFFER',
                '  EXT_EVIDENCE_BUFFER -->|"ninth active-low evidence line"| EVIDENCE_MASK',
                '  EVIDENCE_CMP_A -->|"C5 / IR evidence"| EVIDENCE_MAIN_ISOLATOR',
                '  EVIDENCE_CMP_A -->|"sources 0 / 1"| EVIDENCE_OR_0',
                '  EVIDENCE_CMP_B -->|"sources 2 / 3"| EVIDENCE_OR_1',
                '  EVIDENCE_CMP_B -->|"sources 4 / 5"| EVIDENCE_OR_2',
                '  EVIDENCE_CMP_VOICE -->|"source 6"| EVIDENCE_OR_3',
                '  EVIDENCE_CMP_A -->|"source 7"| EVIDENCE_OR_3',
                '  EXT_EVIDENCE_BUFFER -->|"source 8"| EVIDENCE_OR_4',
                '  EVIDENCE_OR_0 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR',
                '  EVIDENCE_OR_1 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR',
                '  EVIDENCE_OR_2 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR',
                '  EVIDENCE_OR_3 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR',
                '  EVIDENCE_OR_4 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR',
            ],
        ),
    ]

    lines = [heading, "", *intro, ""]
    for diagram_heading, nodes, edges in diagrams:
        lines += [f"### {diagram_heading}", "", "```mermaid", "flowchart TD", *nodes, *edges, "```", ""]
    lines += [atlas_text, ""]
    return "\n".join(lines)


def render_target_readme(
    current: str,
    database: dict[str, Any],
    candidates: list[dict[str, Any]],
    *,
    russian: bool,
) -> str:
    """Replace only the generated principled-design landing-page section."""

    heading = "## Принципиальный дизайн решения" if russian else "## Principled solution design"
    next_summary = (
        "<summary><strong>Принципиальная распиновка</strong></summary>"
        if russian
        else "<summary><strong>Principled pin assignment</strong></summary>"
    )
    start = current.index(heading)
    summary_start = current.index(next_summary, start)
    details_start = current.rfind("<details>", start, summary_start)
    generated = render_target_principled_section(database, candidates, russian=russian)
    return current[:start] + generated + "\n" + current[details_start:]


def render_public_schematics(
    database: dict[str, Any], candidates: list[dict[str, Any]], *, russian: bool
) -> str:
    """Render the product-facing principle diagrams without the review ledger."""

    section = render_target_principled_section(database, candidates, russian=russian)
    section = section.rsplit("\n\n", 1)[0]
    old_heading = "## Принципиальный дизайн решения" if russian else "## Principled solution design"
    new_heading = "# Принципиальные схемы Leshy2" if russian else "# Leshy2 principle diagrams"
    section = section.replace(old_heading, new_heading, 1)
    if russian:
        navigation = "[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](schematics.md)"
        detail = (
            "Схемы ниже показывают конечное устройство по функциональным доменам. "
            "Точные контакты, направления сигналов и электрические связи находятся в "
            "[публичной таблице распиновки](pinout.ru.md). Полный состав устройства — в "
            "[машинном BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv). "
            "Отдельные принципиальные схемы съёмного передающего аксессуара находятся "
            "на странице [Leshy LoRa Cap](lora-cap.ru.md)."
        )
        ecad = """## Актуальная production ECAD-схема

Функциональные диаграммы ниже остаются обзорной картой готового продукта.
Реализованные листы KiCad — точная электрическая схема: каждый компонент
имеет MPN, физические контакты, footprint, цепи и явные no-connect.

| Лист | Состояние | Замкнутая электрическая часть |
|---|---|---|
| [`UI_00_ROOT`](../hardware/ecad/kicad/LESHY2-UI/LESHY2-UI.kicad_sch) | точный ECAD | 9 дочерних листов, 91 межлистовая цепь, 218 явных pins/labels |
| [`UI_10_S3_CORE_MEMORY_BOOT`](../hardware/ecad/kicad/LESHY2-UI/UI_10_S3_CORE_MEMORY_BOOT.kicad_sch) | точный ECAD | 32 компонента, 41 carrier-pad S3, boot/recovery/USB/RF и 39 интерфейсов |
| [`UI_11_DISPLAY_TOUCH_STORAGE`](../hardware/ecad/kicad/LESHY2-UI/UI_11_DISPLAY_TOUCH_STORAGE.kicad_sch) | точный ECAD | 49 экземпляров, все 40 контактов display, все 11 контактов microSD, backlight/touch/isolation и 17 интерфейсов |
| [`UI_12_CONTROLS_INDICATORS`](../hardware/ecad/kicad/LESHY2-UI/UI_12_CONTROLS_INDICATORS.kicad_sch) | точный ECAD | 71 компонент, 15 серийных кнопок, 9 фактических TX LED, аппаратный FAULT LED, thermal/ESD и 45 интерфейсов |

Машинные результаты: [UI root](../hardware/ecad/generated/H2-UI-root-interface.json),
[S3 core](../hardware/ecad/generated/H2-UI10-S3-core.json) и
[display/touch/storage](../hardware/ecad/generated/H2-UI11-display-touch-storage.json) и
[controls/indicators](../hardware/ecad/generated/H2-UI12-controls-indicators.json).
PCB placement, routing и производство этими листами ещё не разрешены."""
    else:
        navigation = "[Home](../README.md) · [Hardware](hardware.md) · [Русский](schematics.ru.md)"
        detail = (
            "The diagrams below describe the finished device by functional domain. "
            "Exact contacts, signal directions and electrical connections are in the "
            "[public pin table](pinout.md). The complete device content is in the "
            "[machine-readable BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv). "
            "The removable transmitting accessory has its own split principle diagrams "
            "on the [Leshy LoRa Cap](lora-cap.md) page."
        )
        ecad = """## Current production ECAD schematic

The functional diagrams below remain the overview of the finished product.
The implemented KiCad sheets are the exact electrical schematic: every device
has an MPN, physical contacts, footprint, nets and explicit no-connects.

| Sheet | State | Closed electrical content |
|---|---|---|
| [`UI_00_ROOT`](../hardware/ecad/kicad/LESHY2-UI/LESHY2-UI.kicad_sch) | exact ECAD | 9 child sheets, 91 cross-sheet nets and 218 explicit pins/labels |
| [`UI_10_S3_CORE_MEMORY_BOOT`](../hardware/ecad/kicad/LESHY2-UI/UI_10_S3_CORE_MEMORY_BOOT.kicad_sch) | exact ECAD | 32 components, 41 S3 carrier pads, boot/recovery/USB/RF and 39 interfaces |
| [`UI_11_DISPLAY_TOUCH_STORAGE`](../hardware/ecad/kicad/LESHY2-UI/UI_11_DISPLAY_TOUCH_STORAGE.kicad_sch) | exact ECAD | 49 instances, all 40 display contacts, all 11 microSD contacts, backlight/touch/isolation and 17 interfaces |
| [`UI_12_CONTROLS_INDICATORS`](../hardware/ecad/kicad/LESHY2-UI/UI_12_CONTROLS_INDICATORS.kicad_sch) | exact ECAD | 71 components, 15 serial switches, 9 actual-TX LEDs, hardware FAULT LED, thermal/ESD and 45 interfaces |

Machine outputs: [UI root](../hardware/ecad/generated/H2-UI-root-interface.json),
[S3 core](../hardware/ecad/generated/H2-UI10-S3-core.json) and
[display/touch/storage](../hardware/ecad/generated/H2-UI11-display-touch-storage.json) and
[controls/indicators](../hardware/ecad/generated/H2-UI12-controls-indicators.json).
These sheets do not yet authorize PCB placement, routing or fabrication."""
    heading, remainder = section.split("\n", 1)
    return f"{heading}\n\n{navigation}\n\n{detail}\n\n{ecad}\n{remainder}"


def render_readme_schematics(
    current: str, database: dict[str, Any], candidates: list[dict[str, Any]], *, russian: bool
) -> str:
    """Keep the complete split principle-diagram set visible on the landing page."""

    begin = "<!-- BEGIN GENERATED PRINCIPLE DIAGRAMS -->"
    end = "<!-- END GENERATED PRINCIPLE DIAGRAMS -->"
    if begin not in current or end not in current:
        raise ValueError("README is missing generated principle-diagram markers")
    section = render_target_principled_section(database, candidates, russian=russian)
    section = section.rsplit("\n\n", 1)[0]
    old_heading = "## Принципиальный дизайн решения" if russian else "## Principled solution design"
    new_heading = "## Принципиальные связи компонентов" if russian else "## Principle component interconnections"
    section = section.replace(old_heading, new_heading, 1)
    if russian:
        footer = (
            "Точные контакты показаны в [распиновке](docs/pinout.ru.md), а прохождение "
            "сигналов между платами — в [карте M1](docs/interconnect.ru.md)."
        )
    else:
        footer = (
            "Exact contacts are in the [pin assignment](docs/pinout.md), while signals "
            "crossing the two boards are in the [M1 map](docs/interconnect.md)."
        )
    generated = f"{begin}\n\n{section}\n\n{footer}\n\n{end}"
    start = current.index(begin)
    finish = current.index(end, start) + len(end)
    return current[:start] + generated + current[finish:]


def render_public_interconnect(
    database: dict[str, Any], candidates: list[dict[str, Any]], *, russian: bool
) -> str:
    """Render the final board-locality and exact M1 contact budget."""

    candidate = next(candidate for candidate in candidates if candidate["id"] == "G2F-3I")
    devices = database["devices"]
    contract = candidate["interboard_contract"]
    connector = contract["connector_pair"]
    plug = devices[candidate["instances"][connector["ui_instance"]]]
    receptacle = devices[candidate["instances"][connector["rf_power_instance"]]]
    accounting = contract["accounting"]
    locality = contract["physical_locality"]

    def mpn(instance: str) -> str:
        return devices[candidate["instances"][instance]]["mpn"]

    if russian:
        title = "# Межплатное соединение M1"
        navigation = "[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](interconnect.md)"
        intro = (
            "Две платы соединяет одна точная 80-контактная пара с рабочим "
            f"межплатным расстоянием {contract['working_inner_gap_mm']:g} мм: "
            f"`{plug['mpn']}` на UI-плате и `{receptacle['mpn']}` на RF/power-плате. "
            f"Шаг — 0,6 мм, паспортная скорость — {connector['transmission_rate_gbps']} Гбит/с, "
            f"ток одного контакта — до {connector['rated_current_per_contact_a']:g} А; "
            "разъём не является механическим крепежом корпуса."
        )
        ui_label = "UI/control-плата"
        rf_label = "RF/power-плата"
        principles = "Почему такое разделение"
        budget = "Бюджет контактов"
        passage_heading = "Физический проход через бутерброд"
        passage_paragraphs = (
            "Все перечисленные ниже межплатные цепи проходят только внутри единого "
            "корпуса M1: в воздушном 11-мм канале нет отдельных шлейфов или проводов "
            "для USB, IPC, I2C, аудио, управления либо питания. Поэтому их общий "
            "механический конфликт с компонентами проверяется один раз полным keep-out "
            "точной пары `FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)`. Пара совмещена "
            "намеренно и не пересекается с посторонними корпусами на обеих платах. "
            "Отдельно проверены пять RF-коаксиалов, переходник дисплея, проходная "
            "розетка U214, девять выводов антенных разъёмов и семь сквозных выводов "
            "энкодера.",
            "Эта проверка закрывает объёмы деталей и межплатный воздушный канал, но не "
            "подменяет трассировку: fan-out всех 80 контактов, via fields, возвратные "
            "пути, импеданс и электрические зазоры будут доказаны только ERC/DRC "
            "готовых плат в KiCad. До этого карта ниже является утверждённой картой "
            "цепей, а не заявлением, что медь уже разведена.",
        )
        table_heading = "Точная карта контактов"
        columns = ("Контакт", "Цепь", "Направление", "Класс")
        footer = (
            "Семь параллельных контактов `3V3_MAIN` дают паспортный потолок 2,8 А, "
            "но допустимый ток готового устройства определяется только измерением нагрева "
            "разъёма при одновременной нагрузке. Все 80 контактов назначены; шесть "
            "цифровых линий RF evidence выделены для лицевых индикаторов передачи."
        )
        ui_groups = (
            f"Вычислители: `{mpn('s3')}` управляет UI, экраном, картой памяти и аудио; `{mpn('c5')}` — собственными диапазонами 2,4/5 ГГц и IR.",
            f"Интерфейсы: `{mpn('display')}`, microSD, `{mpn('codec')}`, `{mpn('receiver')}`, CTIA-гарнитура, D-pad, BACK, OPT и F1…F8.",
            "Локальная безопасность: аппаратный сброс S3/C5, IR-гейт и аналоговое подтверждение передачи S3/C5/IR.",
            f"Обслуживание C5: отдельный data-only USB-C `{mpn('c5_service_usb_connector')}`.",
        )
        rf_groups = (
            f"Радиодомен реального времени: `{mpn('rp')}`, три `{mpn('nrf0')}`, `{mpn('cc')}` и `{mpn('voice')}`.",
            f"Внешние модули: съёмный `{mpn('u214')}` на точном вертикальном `{mpn('u214_connector')}` поднятой задней планки и независимый порт M5 Unit на точном `{mpn('unit_connector')}`.",
            f"Питание и основной USB-C: `{mpn('product_usb_connector')}`, защита `{mpn('product_usb_protector')}`, USB-PD `{mpn('pd_controller')}`, заряд, аккумуляторы и все преобразователи питания.",
            f"Аудио на задней плате: микрофон `{mpn('microphone')}` с локальным смещением, дифференциальный усилитель `{mpn('speaker_amp')}` и динамик `{mpn('speaker')}`.",
            "Задние органы управления: энкодер и PTT; единственный боковой RUN/KILL одновременно задаёт safety-состояние и малотоковую команду источнику.",
            f"Локальная безопасность: `{mpn('safety_controller')}`, `{mpn('safety_watchdog')}`, защёлка FAULT_KILL, три температурные зоны, аппаратные гейты и физическое подтверждение передачи.",
        )
    else:
        title = "# M1 inter-board connection"
        navigation = "[Home](../README.md) · [Hardware](hardware.md) · [Русский](interconnect.ru.md)"
        intro = (
            "The two boards use one exact 80-contact pair at the working "
            f"{contract['working_inner_gap_mm']:g}-mm board spacing: `{plug['mpn']}` on "
            f"the UI board and `{receptacle['mpn']}` on the RF/power board. Both parts "
            f"use 0.6-mm pitch, are rated for {connector['transmission_rate_gbps']} Gbit/s and "
            f"up to {connector['rated_current_per_contact_a']:g} A per contact; the connector is not "
            "an enclosure fastener."
        )
        ui_label = "UI/control board"
        rf_label = "RF/power board"
        principles = "Why the split is arranged this way"
        budget = "Contact budget"
        passage_heading = "Physical passage through the sandwich"
        passage_paragraphs = (
            "Every inter-board net listed below crosses only inside the single M1 body: "
            "the 11-mm air channel contains no separate USB, IPC, I2C, audio, control "
            "or power cable. Their shared mechanical conflict with components is "
            "therefore checked once against the complete keep-out of the exact "
            "`FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` pair. That pair is the one "
            "intentional mate and clears every unrelated body on both boards. The five "
            "RF microcoaxes, display adapter, pass-through U214 socket, nine "
            "antenna-connector tails and seven encoder through-board features are "
            "checked separately.",
            "This closes physical bodies and the inter-board air channel, not PCB "
            "routing. Fan-out from all 80 contacts, via fields, return paths, impedance "
            "and electrical clearances become proven only after ERC/DRC of the routed "
            "KiCad boards. Until then the map below is the accepted net assignment, "
            "not a claim that copper is already routed.",
        )
        table_heading = "Exact contact map"
        columns = ("Contact", "Net", "Direction", "Class")
        footer = (
            "Seven paralleled `3V3_MAIN` contacts provide a 2.8-A nameplate ceiling, "
            "but finished-device current is accepted only after connector-temperature "
            "measurement under simultaneous load. All 80 contacts are assigned; six "
            "digital RF-evidence lines are dedicated to the front transmit indicators."
        )
        ui_groups = (
            f"Compute: `{mpn('s3')}` owns UI, display, storage and audio; `{mpn('c5')}` owns native 2.4/5-GHz radio and IR.",
            f"Interfaces: `{mpn('display')}`, microSD, `{mpn('codec')}`, `{mpn('receiver')}`, CTIA headset, D-pad, BACK, OPT and F1…F8.",
            "Local safety: S3/C5 hardware reset, IR gate and analog S3/C5/IR transmit evidence.",
            f"C5 service: a separate data-only `{mpn('c5_service_usb_connector')}` USB-C receptacle.",
        )
        rf_groups = (
            f"Real-time radio domain: `{mpn('rp')}`, three `{mpn('nrf0')}`, `{mpn('cc')}` and `{mpn('voice')}`.",
            f"External modules: removable `{mpn('u214')}` on exact vertical `{mpn('u214_connector')}` of the raised rear rail and an independent M5 Unit port on exact `{mpn('unit_connector')}`.",
            f"Power and product USB-C: `{mpn('product_usb_connector')}`, `{mpn('product_usb_protector')}` protection, `{mpn('pd_controller')}` USB-PD, charger, cells and every rail converter.",
            f"Rear-board audio: `{mpn('microphone')}` microphone with local bias, `{mpn('speaker_amp')}` differential amplifier and `{mpn('speaker')}` speaker.",
            "Rear controls: encoder and PTT; the single side RUN/KILL switch supplies both the safety state and low-current source command.",
            f"Local safety: `{mpn('safety_controller')}`, `{mpn('safety_watchdog')}`, FAULT_KILL latch, three thermal zones, hardware gates and physical transmit evidence.",
        )

    lines = [title, "", navigation, "", intro, "", f"## {ui_label}", ""]
    lines.extend(f"- {item}" for item in ui_groups)
    lines += ["", f"## {rf_label}", ""]
    lines.extend(f"- {item}" for item in rf_groups)
    lines += ["", f"## {principles}", ""]
    if russian:
        rationale = (
            "Сырой VBUS, согласованное повышенное напряжение USB-PD, зарядное устройство и аккумуляторы остаются на RF/power-плате.",
            "Класс-D усилитель остаётся рядом с динамиком; через M1 проходит только низкоуровневый дифференциальный аудиосигнал.",
            "Микрофон и его цепь смещения находятся на RF/power-плате; MIC_RAW проходит через M1 рядом с AUDIO_GROUND к расположенным на UI-плате селекторам записи и передачи.",
            "Аналоговые выходы детекторов передачи и IR-несущая обрабатываются на своей плате; через M1 проходят только цифровые признаки передачи.",
            "RUN/KILL, независимый watchdog, safety-контроллер и защёлка FAULT_KILL расположены на RF/power-плате; на UI-плату передаются RUN_PERMIT, раздельный reset S3, температура UI и read-only status.",
            "Через M1 проходят только нажатие и фазы энкодера; F1…F8 локальны для UI-платы, PTT локальна для RP/voice, а четыре контакта M1 зарезервированы и оставлены NC.",
        )
    else:
        rationale = locality["rationale"]
    lines.extend(f"- {reason}" for reason in rationale)
    if russian:
        budget_lines = (
            f"- Всего {accounting['positions']} контактов; {accounting['reserved']} зарезервированы и физически не подключены.",
            f"- {accounting['main_3v3_contacts']} × `3V3_MAIN`, {accounting['aon_contacts']} × `AON_SAFE_3V3`.",
            f"- {accounting['power_ground_contacts']} силовых возвратов, {accounting['audio_ground_contacts']} аудиовозврата и {accounting['safety_ground_contacts']} возврата безопасности.",
            "- Сырой VBUS/PD, ток аккумуляторов, аналоговые выходы TX-детекторов, IR-несущая и выходы класса D через M1 не проходят.",
        )
    else:
        budget_lines = (
            f"- {accounting['positions']} positions total; {accounting['reserved']} reserved and no-connect.",
            f"- {accounting['main_3v3_contacts']} × `3V3_MAIN`, {accounting['aon_contacts']} × `AON_SAFE_3V3`.",
            f"- {accounting['power_ground_contacts']} power returns, {accounting['audio_ground_contacts']} audio returns and {accounting['safety_ground_contacts']} safety returns.",
            "- Raw VBUS/PD high voltage, battery current, analog TX-detector outputs, IR carrier and class-D speaker outputs do not cross M1.",
        )
    lines += [
        "",
        f"## {budget}",
        "",
        *budget_lines,
        "",
        f"## {passage_heading}",
        "",
        passage_paragraphs[0],
        "",
        passage_paragraphs[1],
        "",
        f"## {table_heading}",
        "",
        f"| {columns[0]} | {columns[1]} | {columns[2]} | {columns[3]} |",
        "|---:|---|---|---|",
    ]
    for row in contract["pin_map"]:
        lines.append(
            f"| `{row['contact']}` | `{row['net']}` | {row['direction']} | `{row['signal_class']}` |"
        )
    lines += ["", footer, ""]
    return "\n".join(lines)


def _render_principled_pinout_bundle(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> tuple[str, str]:
    """Render a readable, machine-derived atlas for the leading paper map."""

    candidate = next(candidate for candidate in candidates if candidate["id"] == "G2F-3I")
    devices = database["devices"]
    allocations = candidate["allocations"]

    def contacts(instance: str, prefixes: tuple[str, ...]) -> str:
        selected = sorted(
            {
                row["contact"]
                for row in allocations
                if row["instance"] == instance
                and any(row["net"].startswith(prefix) for prefix in prefixes)
            },
            key=natural_contact_key,
        )
        return ",".join(selected) or "—"

    def budget(instance: str) -> tuple[int, int, int, int]:
        device = devices[candidate["instances"][instance]]
        used = sum(1 for row in allocations if row["instance"] == instance)
        reserved = len(candidate["reservations"].get(instance, {}))
        free = len(candidate["free_gpio"].get(instance, []))
        total = sum(1 for attributes in device["contacts"].values() if attributes["role"] == "gpio")
        return used, reserved, free, total

    c5_sdio_controllers = {
        row["controller"]
        for row in allocations
        if row["instance"] == "c5" and row["net"].startswith("S3_C5_SDIO_")
    }
    sdio_label = (
        "1-bit SDIO"
        if c5_sdio_controllers == {"SDIO_SLAVE"}
        else "4-bit SDIO"
        if c5_sdio_controllers == {"SDIO_SLAVE_4BIT"}
        else "SDIO"
    )

    def node(instance: str, role: str, suffix: str = "") -> str:
        """Name one physical device with its source-of-truth MPN and role."""

        mpn = devices[candidate["instances"][instance]]["mpn"]
        label = f"{mpn}<br/>{role}".replace('"', "&quot;")
        return f'  {instance.upper()}{suffix}["{label}"]'

    abstract_endpoints = sorted(
        {
            endpoint.removeprefix("abstract:")
            for row in allocations
            for endpoint in row.get("peers", [])
            if endpoint.startswith("abstract:")
        }
        | {
            endpoint.removeprefix("abstract:")
            for route in candidate.get("fixed_routes", [])
            for endpoint in (route["from"], route["to"])
            if endpoint.startswith("abstract:")
        }
    )

    audio_excluded = {
        "codec_power_switch", "receiver_power_switch", "voice_buck", "voice_inductor",
        "voice_input_cap", "voice_hf_input_cap", "voice_fb_top", "voice_fb_bottom",
        "voice_ff_cap", "voice_output_cap0", "voice_output_cap1", "voice_efuse",
        "voice_efuse_rilm", "voice_efuse_dvdt_cap", "voice_efuse_itimer_cap",
        "voice_efuse_ovlo_top", "voice_efuse_ovlo_bottom", "voice_efuse_pg_top",
        "voice_efuse_pg_bottom", "voice_efuse_output_cap", "voice_en_pulldown",
        "voice_pg_pullup", "voice_pg_base_res", "voice_pg_qualifier",
    }
    audio_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if (
            instance in {"codec", "receiver", "voice", "microphone", "speaker", "headphone_jack", "headphone_esd"}
            or instance.startswith(("audio_", "si_audio_", "speaker_", "headphone_", "headset_", "codec_", "receiver_", "voice_", "mic_tx_", "microphone_"))
        )
        and instance not in audio_excluded
    )
    audio_roles = {
        "receiver": "AM/FM/SW/LW broadcast receiver",
        "codec": "mono ADC/DAC audio codec",
        "voice": "VHF/UHF analog voice transceiver",
        "microphone": "top-port analog electret microphone",
        "speaker": "24-by-12-mm 4-Ohm internal loudspeaker",
        "headphone_jack": "shielded 3.5-mm CTIA TRRS headset jack with insertion switches",
        "headphone_esd": "independent left/right/headset-microphone IEC-ESD array",
        "headset_mic_selector": "controlled internal/CTIA-headset microphone selector",
        "headset_mic_selector_bypass": "headset-microphone selector bypass capacitor",
        "headset_mic_bias_res": "separate 2.2-kOhm CTIA microphone-bias resistor",
        "headset_control_io": "0x39 microphone-source controller with seven pulled reserve I/O lines",
        "headset_control_io_bypass": "headset-controller bypass capacitor",
        "headset_mic_select_pullup": "internal-microphone reset-default pull-up",
        "headset_detect_series": "10-kOhm plug-detect input protection",
        "audio_rx_mux": "Si4732/SA518 receive-audio source selector",
        "audio_capture_selector": "RX/microphone recording-source selector",
        "audio_capture_buffer": "active high-impedance capture buffer",
        "audio_speaker_selector": "dual differential RX-bypass/codec speaker selector",
        "audio_tx_selector": "electret/codec transmit-audio selector",
        "audio_safe_gate": "direct-AUDIO_ARM dual selector-request gate",
        "speaker_amp": "reset-off mono Class-D speaker amplifier",
        "codec_supervisor": "3.08-V 200-ms codec interface supervisor",
        "codec_i2c_iso": "dual bilateral codec-I2C power isolation",
        "codec_i2s_bclk_iso": "physical BCLK tri-state isolation buffer",
        "codec_i2s_ws_iso": "physical word-select tri-state isolation buffer",
        "codec_i2s_dout_iso": "physical playback-data tri-state isolation buffer",
        "codec_i2s_din_iso": "physical capture-data tri-state isolation buffer",
        "receiver_supervisor": "3.08-V 200-ms receiver reset/interface supervisor",
        "receiver_i2c_iso": "dual bilateral receiver-I2C power isolation",
        "receiver_irq_iso": "Ioff open-drain receiver-interrupt isolator",
        "receiver_clock": "32.768-kHz receiver reference crystal",
        "receiver_fmi_esd": "FM/SW-boundary 0.2-pF RF ESD shunt",
        "receiver_fmi_match_inductor": "56-nH high-Q FM first target on FM/SW port",
        "receiver_fmi_coupling_cap": "1-nF C0G FMI AC-coupling capacitor",
        "receiver_ami_esd": "AM/LW-boundary 0.2-pF RF ESD shunt",
        "receiver_ami_coupling_cap": "0.47-uF AMI AC-coupling capacitor",
        "voice_supervisor": "FAULT_KILL-qualified protected-4-V voice supervisor",
        "voice_io_power_switch": "discharged local voice-interface supply switch",
        "voice_ptt_iso": "physical module-PTT tri-state isolation buffer",
        "voice_uart_tx_iso": "physical host-to-module UART isolation buffer",
        "voice_hl_driver": "low-or-open SA518 H/L driver",
        "voice_audio_iso": "dual AFOUT/MIC_IN power-domain isolation switch",
    }
    nrf_support_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if (
            instance in {"nrf0", "nrf1", "nrf2"}
            or instance.startswith(("nrf0_", "nrf1_", "nrf2_", "nrf_evidence_", "nrf_power_input_", "nrf_power_on_"))
        )
        and not any(
            token in instance
            for token in ("_evidence_threshold_", "_evidence_hysteresis", "_evidence_output_pullup", "_evidence_main_pullup")
        )
    )
    nrf_roles = {
        "nrf0": "nRF24-compatible full-function radio 0",
        "nrf1": "nRF24-compatible full-function radio 1",
        "nrf2": "nRF24-compatible full-function radio 2",
        "nrf_power_input_cap": "common nRF switch-input bypass capacitor",
        "nrf_power_on_pulldown": "common nRF rail fail-low resistor",
        "nrf_evidence_hold_diode": "actual-TX evidence hold isolation diode",
        "nrf_evidence_hold_cap": "actual-TX evidence enable hold capacitor",
        "nrf_evidence_hold_pulldown": "actual-TX evidence hold discharge resistor",
    }

    def nrf_role(instance: str) -> str:
        if instance in nrf_roles:
            return nrf_roles[instance]
        if instance.endswith("_tx_led_series"):
            return "antenna-local actual-TX indicator 2.2-kOhm current limit"
        if instance.endswith("_tx_led"):
            return "antenna-local actual-TX indicator"
        suffix_roles = {
            "host_buffer": "CE/CSN/SCK/MOSI switched-rail Ioff buffer",
            "return_buffer": "MISO/IRQ switched-rail Ioff buffer",
            "host_buffer_bypass": "host-buffer local bypass capacitor",
            "return_buffer_bypass": "return-buffer local bypass capacitor",
            "module_bulk_cap": "radio-module local bulk capacitor",
            "module_hf_cap": "radio-module high-frequency bypass capacitor",
            "coupler": "full-band forward-power directional coupler",
            "coupler_termination": "coupler isolated-port 49.9-Ohm termination",
            "detector_match": "AD8314 52.3-Ohm broadband input match",
            "detector_filter": "AD8314 response filter capacitor",
            "detector_bypass": "AD8314 local bypass capacitor",
        }
        for suffix, role in suffix_roles.items():
            if instance.endswith(suffix):
                return role
        if instance.endswith("_series"):
            return "22-Ohm isolated-interface source resistor"
        if instance.endswith(("_pullup", "_pulldown")):
            return "10-kOhm deterministic interface-state resistor"
        return instance.replace("_", " ") + " physical component"

    cc_support_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if instance.startswith("cc_")
        and instance != "cc_power_switch"
        and not any(
            token in instance
            for token in ("_evidence_threshold_", "_evidence_hysteresis", "_evidence_output_pullup", "_evidence_main_pullup")
        )
    )
    cc_roles = {
        "cc_host_buffer": "SCLK/SI/CSN switched-rail Ioff buffer",
        "cc_return_buffer": "SO/GDO0/GDO2 switched-rail Ioff buffer",
        "cc_band_buffer": "rail-off V1/V2 band-control Ioff buffer",
        "cc_power_input_cap": "CC load-switch input bypass capacitor",
        "cc_local_bulk_cap": "CC switched-rail local bulk capacitor",
        "cc_power_on_pulldown": "CC load-switch reset-off resistor",
        "cc_dcoupl_cap": "CC1101 DCOUPL capacitor",
        "cc_rbias_res": "CC1101 56-kOhm RBIAS resistor",
        "cc_crystal": "CC1101 exact 26-MHz reference crystal",
        "cc_crystal_load_q1": "CC crystal Q1 load capacitor",
        "cc_crystal_load_q2": "CC crystal Q2 load capacitor",
        "cc_rf_p_dc_block": "RF_P high-Q series DC-block capacitor",
        "cc_rf_n_dc_block": "RF_N high-Q series DC-block capacitor",
        "cc_rf_diff_cap": "differential RF trim capacitor",
        "cc_balun": "300-MHz-to-1-GHz 50-to-100-Ohm RF balun",
        "cc_match_l3n3": "balun-output 3.3-nH series match",
        "cc_match_c1p2": "balun-output 1.2-pF shunt match",
        "cc_match_l6n8": "balun-output 6.8-nH series match",
        "cc_switch_a": "transceiver-side three-band SP3T isolator",
        "cc_switch_b": "antenna-side three-band SP3T isolator",
        "cc_315_l10_in": "315-MHz input series inductor",
        "cc_315_shunt_l3n6": "315-MHz shunt-trap inductor",
        "cc_315_shunt_c8p": "315-MHz shunt-trap capacitor",
        "cc_315_l10_out": "315-MHz output series inductor",
        "cc_433_shunt_c10p": "433-MHz input shunt capacitor",
        "cc_433_l15": "433-MHz series inductor",
        "cc_433_shunt_c6p2": "433-MHz output shunt capacitor",
        "cc_868_915_l10": "combined 868/915-MHz series inductor",
        "cc_output_l2n2": "selected-path output matching inductor",
        "cc_rf_esd": "external CC RF line ultra-low-capacitance ESD diode",
        "cc_detector_tap_cap": "actual-TX high-impedance RF sample capacitor",
        "cc_detector_filter": "AD8314 response filter capacitor",
        "cc_detector_bypass": "AD8314 local bypass capacitor",
        "cc_evidence_hold_diode": "actual-TX evidence hold isolation diode",
        "cc_evidence_hold_cap": "actual-TX evidence enable hold capacitor",
        "cc_evidence_hold_pulldown": "actual-TX evidence hold discharge resistor",
        "cc_tx_led_series": "CC actual-TX indicator 2.2-kOhm current limit",
        "cc_tx_led": "CC antenna-local actual-TX indicator",
    }

    def cc_role(instance: str) -> str:
        if instance in cc_roles:
            return cc_roles[instance]
        if instance.endswith("_bypass"):
            return "local switched-domain bypass capacitor"
        if instance.endswith("_series"):
            return "22-Ohm switched-interface source resistor"
        if instance.endswith(("_pullup", "_pulldown")):
            return "10-kOhm deterministic interface-state resistor"
        return instance.removeprefix("cc_").replace("_", " ") + " CC physical component"

    voice_rf_support_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if instance.startswith("voice_")
        and instance in {
            "voice_rf_esd",
            "voice_detector_series_attenuator",
            "voice_detector_match",
            "voice_detector_filter",
            "voice_detector_bypass",
            "voice_evidence_hold_diode",
            "voice_evidence_hold_cap",
            "voice_evidence_hold_pulldown",
            "voice_tx_led_series",
            "voice_tx_led",
        }
    )
    voice_rf_roles = {
        "voice_rf_esd": "24-V ultra-low-capacitance external voice RF ESD diode",
        "voice_detector_series_attenuator": "actual-TX 5.1-kOhm RF series sampler",
        "voice_detector_match": "AD8314 52.3-Ohm detector input shunt",
        "voice_detector_filter": "AD8314 response filter capacitor",
        "voice_detector_bypass": "AD8314 local bypass capacitor",
        "voice_evidence_hold_diode": "actual-TX evidence hold isolation diode",
        "voice_evidence_hold_cap": "actual-TX evidence enable hold capacitor",
        "voice_evidence_hold_pulldown": "actual-TX evidence hold discharge resistor",
        "voice_tx_led_series": "voice actual-TX indicator 2.2-kOhm current limit",
        "voice_tx_led": "voice antenna-local actual-TX indicator",
    }

    ir_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if instance.startswith("ir_")
        and not any(
            token in instance
            for token in ("_evidence_threshold_", "_evidence_hysteresis", "_evidence_output_pullup", "_evidence_main_pullup")
        )
    )
    ir_roles = {
        "ir_power_switch": "independent reset-off IR-receiver load switch",
        "ir_power_input_cap": "IR-receiver switch input capacitor",
        "ir_power_output_cap": "IR switched-rail bulk capacitor",
        "ir_power_output_bypass": "IR switched-rail high-frequency bypass capacitor",
        "ir_power_on_pulldown": "IR receive-rail reset-off resistor",
        "ir_demod": "38-kHz AGC2 demodulating IR receiver",
        "ir_demod_supply_res": "demodulator 100-Ohm supply-filter resistor",
        "ir_demod_supply_cap": "demodulator 4.7-uF supply-filter capacitor",
        "ir_carrier": "30-to-60-kHz carrier-learning IR receiver",
        "ir_carrier_supply_res": "carrier receiver 100-Ohm supply-filter resistor",
        "ir_carrier_supply_cap": "carrier receiver 4.7-uF supply-filter capacitor",
        "ir_carrier_pullup": "carrier-output 4.7-kOhm pull-up resistor",
        "ir_return_buffer": "dual switched-rail Ioff IR-return buffer",
        "ir_return_buffer_bypass": "IR-return-buffer bypass capacitor",
        "ir_demod_series": "demodulated-envelope 100-Ohm source resistor",
        "ir_carrier_series": "carrier-cycle 100-Ohm source resistor",
        "ir_demod_host_pullup": "host-side demodulated-input idle pull-up",
        "ir_carrier_host_pullup": "host-side carrier-input idle pull-up",
        "ir_emitter": "side-view 940-nm consumer IR transmit emitter",
        "ir_emitter_limit": "33-Ohm 1206 emitter current-limit resistor",
        "ir_tx_mosfet": "FAULT_KILL-qualified low-side IR emitter switch",
        "ir_tx_gate_series": "100-Ohm IR-switch gate resistor",
        "ir_tx_gate_pulldown": "10-kOhm IR-switch fail-low resistor",
        "ir_safe_gate": "UI-local FAULT_KILL-qualified IR carrier gate",
        "ir_safe_gate_bypass": "IR safety-gate local bypass capacitor",
        "ir_evidence_amp": "AON physical-optical transimpedance amplifier",
        "ir_evidence_amp_bypass": "optical-evidence amplifier bypass capacitor",
        "ir_evidence_vref_top": "optical-evidence 100-kOhm reference upper leg",
        "ir_evidence_vref_bottom": "optical-evidence 10-kOhm reference lower leg",
        "ir_evidence_vref_cap": "optical-evidence reference filter capacitor",
        "ir_evidence_feedback": "47-kOhm optical transimpedance feedback resistor",
        "ir_evidence_feedback_cap": "1-nF optical-evidence response capacitor",
        "ir_tx_led_series": "IR actual-TX indicator 2.2-kOhm current limit",
        "ir_tx_led": "IR-local physical-optical actual-TX indicator",
    }

    native_rf_support_instance_names = tuple(
        instance
        for instance in candidate["instances"]
        if instance.startswith(("s3_rf_", "s3_detector_", "c5_rf_", "c5_detector_"))
        or instance in {"s3_tx_led", "s3_tx_led_series", "c5_tx_led", "c5_tx_led_series"}
    )
    native_rf_roles = {
        "s3_rf_jumper": "S3 exact 30-mm UMCC Gen1 module jumper",
        "s3_rf_board_connector": "S3 module-jumper board receptacle",
        "s3_rf_coupler": "S3 2.4-GHz forward-power directional coupler",
        "s3_rf_coupler_termination": "S3 coupler 49.9-Ohm termination",
        "s3_detector_input_cap": "S3 detector RF-input DC block",
        "s3_detector_feedback_res": "S3 detector gain feedback resistor",
        "s3_detector_ground_res": "S3 detector gain ground resistor",
        "s3_detector_output_cap": "S3 detector output-load capacitor",
        "s3_detector_bypass": "S3 detector local bypass capacitor",
        "c5_rf_jumper": "C5 exact 30-mm UMCC Gen1 module jumper",
        "c5_rf_board_connector": "C5 module-jumper board receptacle",
        "c5_rf_coupler": "C5 2.4/5-GHz forward-power directional coupler",
        "c5_rf_coupler_termination": "C5 coupler 49.9-Ohm termination",
        "c5_detector_input_cap": "C5 detector RF-input DC block",
        "c5_detector_feedback_res": "C5 detector gain feedback resistor",
        "c5_detector_ground_res": "C5 detector gain ground resistor",
        "c5_detector_output_cap": "C5 detector output-load capacitor",
        "c5_detector_bypass": "C5 detector local bypass capacitor",
        "s3_tx_led_series": "S3 actual-TX indicator 2.2-kOhm current limit",
        "s3_tx_led": "S3 antenna-local actual-TX indicator",
        "c5_tx_led_series": "C5 actual-TX indicator 2.2-kOhm current limit",
        "c5_tx_led": "C5 antenna-local actual-TX indicator",
    }

    evidence_support_instance_names = (
        "evidence_cmp_a", "evidence_cmp_a_bypass",
        "evidence_cmp_b", "evidence_cmp_b_bypass",
        "evidence_cmp_voice", "evidence_cmp_voice_bypass",
        "s3_evidence_threshold_top", "s3_evidence_threshold_bottom",
        "s3_evidence_hysteresis", "s3_evidence_output_pullup",
        "c5_evidence_threshold_top", "c5_evidence_threshold_bottom",
        "c5_evidence_hysteresis", "c5_evidence_output_pullup",
        "nrf0_evidence_threshold_top", "nrf0_evidence_threshold_bottom",
        "nrf0_evidence_hysteresis", "nrf0_evidence_output_pullup",
        "nrf1_evidence_threshold_top", "nrf1_evidence_threshold_bottom",
        "nrf1_evidence_hysteresis", "nrf1_evidence_output_pullup",
        "nrf2_evidence_threshold_top", "nrf2_evidence_threshold_bottom",
        "nrf2_evidence_hysteresis", "nrf2_evidence_output_pullup",
        "cc_evidence_threshold_top", "cc_evidence_threshold_bottom",
        "cc_evidence_hysteresis", "cc_evidence_output_pullup",
        "voice_evidence_threshold_top", "voice_evidence_threshold_bottom",
        "voice_evidence_hysteresis", "voice_evidence_output_pullup",
        "ir_evidence_threshold_top", "ir_evidence_threshold_bottom",
        "ir_evidence_hysteresis", "ir_evidence_output_pullup",
        "ext_evidence_input_series", "ext_evidence_input_pullup",
        "ext_evidence_buffer", "ext_evidence_buffer_bypass", "ext_evidence_output_pullup",
        "evidence_mask", "evidence_mask_bypass",
        "evidence_mask_scl_pullup", "evidence_mask_sda_pullup",
        "evidence_mask_p11_pulldown", "evidence_mask_p12_pulldown",
        "evidence_mask_p13_pulldown", "evidence_mask_p14_pulldown",
        "evidence_mask_p15_pulldown", "evidence_mask_p16_pulldown",
        "evidence_mask_p17_pulldown",
        "evidence_or_0", "evidence_or_1", "evidence_or_2", "evidence_or_3", "evidence_or_4",
        "any_tx_aon_pullup",
        "ext_tx_led_series", "ext_tx_led",
        "evidence_main_isolator", "evidence_main_isolator_bypass",
        "c5_evidence_main_pullup", "ir_evidence_main_pullup",
        "rp_any_tx_main_pullup",
    )

    def evidence_role(instance: str) -> str:
        fixed = {
            "evidence_cmp_a": "UI-local S3/C5/IR AON evidence comparator; fourth channel inert",
            "evidence_cmp_a_bypass": "UI evidence-comparator local bypass capacitor",
            "evidence_cmp_b": "RF-local nRF0/nRF1/nRF2/CC AON evidence comparator",
            "evidence_cmp_b_bypass": "RF evidence-comparator local bypass capacitor",
            "evidence_cmp_voice": "RF-local dedicated voice AON evidence comparator",
            "evidence_cmp_voice_bypass": "voice evidence-comparator local bypass capacitor",
            "ext_evidence_input_series": "1-kOhm protected Cap-contact evidence input resistor",
            "ext_evidence_input_pullup": "10-kOhm AON no-Cap/no-evidence input pull-up resistor",
            "ext_evidence_buffer": "5-V-tolerant non-inverting open-drain LoRa Cap evidence boundary",
            "ext_evidence_buffer_bypass": "LoRa Cap evidence-boundary local bypass capacitor",
            "ext_evidence_output_pullup": "10-kOhm ninth-evidence-bit AON pull-up resistor",
            "evidence_mask": "AON 16-bit evidence source mask on the private safety I2C bus",
            "evidence_mask_bypass": "evidence-mask local bypass capacitor",
            "evidence_mask_scl_pullup": "10-kOhm private evidence-clock pull-up resistor",
            "evidence_mask_sda_pullup": "10-kOhm private evidence-data pull-up resistor",
            "evidence_mask_p11_pulldown": "10-kOhm unused P11 input pull-down resistor",
            "evidence_mask_p12_pulldown": "10-kOhm unused P12 input pull-down resistor",
            "evidence_mask_p13_pulldown": "10-kOhm unused P13 input pull-down resistor",
            "evidence_mask_p14_pulldown": "10-kOhm unused P14 input pull-down resistor",
            "evidence_mask_p15_pulldown": "10-kOhm unused P15 input pull-down resistor",
            "evidence_mask_p16_pulldown": "10-kOhm unused P16 input pull-down resistor",
            "evidence_mask_p17_pulldown": "10-kOhm unused P17 input pull-down resistor",
            "evidence_or_0": "evidence diode-OR pair 0/1",
            "evidence_or_1": "evidence diode-OR pair 2/3",
            "evidence_or_2": "evidence diode-OR pair 4/5",
            "evidence_or_3": "evidence diode-OR pair 6/7",
            "evidence_or_4": "evidence diode-OR source 8 with one unused diode",
            "any_tx_aon_pullup": "10-kOhm AON ANY-TX logic pull-up resistor",
            "ext_tx_led_series": "2.2-kOhm LoRa/EXT physical-TX indicator current limit",
            "ext_tx_led": "red physical LoRa/EXT actual-TX indicator",
            "evidence_main_isolator": "triple AON-to-main open-drain evidence isolator",
            "evidence_main_isolator_bypass": "evidence-domain-isolator local bypass capacitor",
            "c5_evidence_main_pullup": "10-kOhm main-domain C5-evidence pull-up resistor",
            "ir_evidence_main_pullup": "10-kOhm main-domain IR-evidence pull-up resistor",
            "rp_any_tx_main_pullup": "10-kOhm main-domain RP ANY-TX pull-up resistor",
        }
        if instance in fixed:
            return fixed[instance]
        channel = instance.split("_evidence_", 1)[0].replace("nrf", "nRF")
        if instance.endswith("threshold_top"):
            return f"{channel} first-population 100-kOhm threshold upper resistor"
        if instance.endswith("threshold_bottom"):
            value = "12-kOhm" if channel == "ir" else "10-kOhm"
            return f"{channel} first-population {value} threshold lower resistor"
        if instance.endswith("hysteresis"):
            return f"{channel} 1-MOhm evidence-hysteresis feedback resistor"
        if instance.endswith("output_pullup"):
            return f"{channel} 10-kOhm AON comparator-output pull-up resistor"
        return instance.replace("_", " ") + " evidence component"

    expansion_instance_names = (
        "u214_connector", "u214_i2c_iso", "u214_i2c_iso_bypass", "u214_i2c_host_sda_pullup",
        "u214_i2c_host_scl_pullup", "u214_host_buffer_a", "u214_host_buffer_b",
        "u214_return_buffer", "u214_host_buffer_a_bypass",
        "u214_host_buffer_b_bypass", "u214_return_buffer_bypass",
        "u214_series_rst", "u214_series_gps_rx", "u214_series_sck",
        "u214_series_mosi", "u214_series_nss", "u214_series_busy",
        "u214_series_irq", "u214_series_gps_tx", "u214_series_miso",
        "u214_esd_a", "u214_esd_b", "u214_esd_c", "ext_request_or",
        "ext_request_or_bypass", "ext_any_req_pulldown", "ext_branch_gate",
        "ext_branch_gate_bypass", "u214_req_pulldown", "unit_req_pulldown",
        "u214_supervisor", "u214_supervisor_bypass",
        "u214_supervisor_sense_top", "u214_supervisor_sense_bottom",
        "u214_supervisor_ct", "u214_supervisor_pullup", "unit_efuse",
        "unit_rilm", "unit_dvdt_cap", "unit_itimer_cap", "unit_ovlo_top",
        "unit_ovlo_bottom", "unit_input_cap", "unit_output_cap", "unit_bleeder",
        "unit_supervisor", "unit_supervisor_bypass", "unit_supervisor_sense_top",
        "unit_supervisor_sense_bottom", "unit_supervisor_ct",
        "unit_supervisor_pullup", "unit_signal_iso",
        "unit_signal_iso_vcca_bypass", "unit_signal_iso_vccb_bypass",
        "unit_signal_iso_oe_pulldown", "unit_esd",
    )

    service_instance_names = (
        "m1_ui_plug", "m1_rf_receptacle",
        "c5_service_usb_connector", "c5_service_usb_esd",
        "c5_service_usb_switch", "c5_service_usb_switch_bypass",
        "c5_service_usb_cc1_rd", "c5_service_usb_cc2_rd",
        "c5_service_usb_vbus_bleeder", "c5_service_usb_dm_series",
        "c5_service_usb_dp_series", "rp_service_usb_connector",
        "rp_service_usb_esd", "rp_service_usb_switch",
        "rp_service_usb_switch_bypass", "rp_service_usb_cc1_rd",
        "rp_service_usb_cc2_rd", "rp_service_usb_vbus_bleeder",
        "rp_service_usb_dm_series", "rp_service_usb_dp_series",
        "s3_dbg_header", "c5_dbg_header", "rp_dbg_header",
        "s3_dbg_esd", "c5_dbg_esd", "rp_dbg_esd",
        "s3_reset_button", "s3_boot_button", "c5_reset_button",
        "c5_boot_button", "rp_reset_button", "rp_boot_button",
        "s3_dbg_vtref_series", "s3_dbg_reset_series", "s3_dbg_boot_series",
        "s3_dbg0_series", "s3_dbg1_series", "s3_dbg_id0_strap",
        "s3_dbg_id1_strap", "c5_dbg_vtref_series", "c5_dbg_reset_series",
        "c5_dbg_boot_series", "c5_dbg0_series", "c5_dbg1_series",
        "c5_dbg_id0_strap", "c5_dbg_id1_strap", "rp_dbg_vtref_series",
        "rp_dbg_reset_series", "rp_dbg_boot_series", "rp_dbg0_series",
        "rp_dbg1_series", "rp_dbg_id0_strap", "rp_dbg_id1_strap",
        "s3_boot_pullup", "c5_boot_pullup", "rp_boot_pullup",
        "c5_gpio27_pullup",
    )

    def service_role(instance: str) -> str:
        if instance == "m1_ui_plug":
            return "UI-board half of the exact 80-contact 11-mm inter-board link"
        if instance == "m1_rf_receptacle":
            return "RF/power-board half of the exact 80-contact 11-mm inter-board link"
        domain = "C5" if instance.startswith("c5_") else "RP" if instance.startswith("rp_") else "S3"
        if instance.endswith("service_usb_connector"):
            return f"{domain} independent data-only USB-C service receptacle"
        if instance.endswith("service_usb_esd"):
            return f"{domain} service USB D+/D- low-capacitance ESD shunt"
        if instance.endswith("service_usb_switch"):
            return f"{domain} board-off D+/D- backfeed-isolation switch"
        if instance.endswith("service_usb_switch_bypass"):
            return f"{domain} USB isolation-switch local bypass capacitor"
        if "service_usb_cc" in instance:
            return f"{domain} service-port passive Type-C Rd resistor"
        if instance.endswith("service_usb_vbus_bleeder"):
            return f"{domain} no-power service-VBUS bleeder resistor"
        if instance.endswith("service_usb_dm_series"):
            return f"{domain} USB Full-Speed D- MCU-side series resistor"
        if instance.endswith("service_usb_dp_series"):
            return f"{domain} USB Full-Speed D+ MCU-side series resistor"
        if instance.endswith("dbg_header"):
            return f"{domain} keyed ten-contact independent debug header"
        if instance.endswith("dbg_esd"):
            return f"{domain} RESET/BOOT/debug four-line ESD array"
        if instance.endswith("reset_button"):
            return f"{domain} separate physical RESET service control"
        if instance.endswith("boot_button"):
            return f"{domain} separate physical BOOT service control"
        if instance.endswith("dbg_vtref_series"):
            return f"{domain} fixture VTREF sense-current resistor"
        if instance.endswith("dbg_reset_series"):
            return f"{domain} active-low RESET fixture-current resistor"
        if instance.endswith("dbg_boot_series"):
            return f"{domain} active-low BOOT fixture-current resistor"
        if instance.endswith(("dbg0_series", "dbg1_series")):
            return f"{domain} UART/SWD fixture-current and edge resistor"
        if instance.endswith(("dbg_id0_strap", "dbg_id1_strap")):
            return f"{domain} passive DBG10 identity strap resistor"
        if instance.endswith("boot_pullup"):
            return f"{domain} deterministic normal-boot pull-up resistor"
        if instance == "c5_gpio27_pullup":
            return "C5 fixed-high normal-boot and ROM-log strap resistor"
        return instance.replace("_", " ") + " service component"

    full_ledger = render_ledger(database, candidates)
    detail_start = full_ledger.index("\n### `s3` —", full_ledger.index("\n## G2F-3I —")) + 1
    detail_end = full_ledger.index("\n## Machine-check result and review boundary", detail_start)
    exact_details = full_ledger[detail_start:detail_end].rstrip()

    lines = [
        "# G2F-3I — generated principled pinout atlas",
        "",
        "- Статус: **целевая принципиальная распиновка G2F-3I — проведено сводное предсхемное ревью; H1 принят; разрешена только H2 production-схема, не PCB placement/routing**",
        "- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`",
        "- Regenerate: `python3 hardware/architecture/generate.py --write`",
        "- Verify: `python3 hardware/architecture/generate.py --check`",
        "",
        "> Файл сгенерирован. Ручные изменения будут отвергнуты `--check`.",
        "",
        "## Как читать артефакт",
        "",
        "Диаграмма — навигатор по owners и физически независимым interface groups.",
        "Она намеренно строится сверху вниз и остаётся живой проекцией текущей",
        "начинки: изменение machine source обязано регенерировать этот atlas и",
        "синхронно обновить diagram-срезы обеих стартовых страниц.",
        "Каждый прямоугольник физического устройства содержит его exact/current",
        "paper MPN и роль. Разные устройства не объединяются в один прямоугольник.",
        "Если production part ещё не выбран, узел явно помечается `MPN TBD`;",
        "пассивная цепь отдельно помечается как circuit, а не как заказной компонент.",
        "Нормативные pin/net значения находятся в следующих за ней таблицах и",
        "получены из того же JSON. `abstract:*` означает зарезервированную функцию,",
        "для которой exact peripheral MPN/electrical circuit ещё не принят; это не",
        "разрешение рисовать вымышленный pin в KiCad.",
        "",
        "## Полная машинная проекция owners и pin groups",
        "",
        "GitHub не рендерит эту исчерпывающую one-device-per-node проекцию из-за",
        "лимита текста Mermaid. Она сохранена как проверяемый исходник; рабочая",
        "обзорная диаграмма находится на стартовой странице проекта, а точные",
        "pin/net-данные — в таблицах ниже.",
        "",
        "<details>",
        "<summary><strong>Исходник полной проекции</strong></summary>",
        "",
        "```text",
        "flowchart TD",
        "  subgraph POWER_INPUT[\"Sink-only USB-PD and replaceable-cell power path\"]",
        node("product_usb_connector", "product USB-C receptacle: protected S3 USB2 data and sink-only power"),
        node("product_usb_protector", "CC1/CC2 and USB2 D+/D- short-to-VBUS/ESD protector"),
        node("product_usb_dp_series", "22-Ohm S3 USB Full-Speed D+ series resistor"),
        node("product_usb_dm_series", "22-Ohm S3 USB Full-Speed D- series resistor"),
        node("product_usb_vbias_cap", "100-nF 100-V port-protector VBIAS capacitor"),
        node("product_usb_vpwr_cap", "1-uF 16-V port-protector VPWR capacitor"),
        node("product_usb_fault_pullup", "10-kOhm port-protector fault pull-up"),
        node("pd_cc1_cap", "220-pF C0G protected USB-C CC1 capacitor"),
        node("pd_cc2_cap", "220-pF C0G protected USB-C CC2 capacitor"),
        node("pd_vbus_tvs", "22-V flat-clamp VBUS surge protection"),
        node("pd_controller", "sink-only USB-PD policy and protected high-voltage path"),
        node("pd_config_eeprom", "dedicated PD patch/configuration EEPROM"),
        node("pd_vin_cap", "10-uF PD-controller VIN_3V3 capacitor"),
        node("pd_ldo3v3_cap", "10-uF PD-controller 3.3-V LDO capacitor"),
        node("pd_ldo1v5_cap", "10-uF PD-controller 1.5-V LDO capacitor"),
        node("pd_pphv_cap0", "22-uF 25-V protected-VBUS capacitor #0"),
        node("pd_pphv_cap1", "22-uF 25-V protected-VBUS capacitor #1"),
        node("pd_pphv_cap2", "22-uF 25-V protected-VBUS capacitor #2"),
        node("pd_pphv_cap3", "22-uF 25-V protected-VBUS capacitor #3"),
        node("pd_vbus_cap", "4.7-uF 25-V raw-VBUS startup capacitor"),
        node("pd_eeprom_bypass", "100-nF PD EEPROM bypass capacitor"),
        node("pd_eeprom_wp_pullup", "10-kOhm reset-high EEPROM write-protect pull-up"),
        node("pd_local_scl_pullup", "2.2-kOhm local PD-bus SCL pull-up"),
        node("pd_local_sda_pullup", "2.2-kOhm local PD-bus SDA pull-up"),
        node("sys_i2c_scl_pullup", "2.2-kOhm system host-bus SCL pull-up"),
        node("sys_i2c_sda_pullup", "2.2-kOhm system host-bus SDA pull-up"),
        node("sys_int_pullup", "10-kOhm shared wired-low system IRQ pull-up"),
        node("nvdc_charger", "2S-configured buck-boost charger and NVDC system power path"),
        node("charger_inductor", "2.2-uH 7-A 750-kHz charger inductor"),
        node("charger_vbus_cap0", "10-uF 25-V X7R charger VBUS capacitor #0"),
        node("charger_vbus_cap1", "10-uF 25-V X7R charger VBUS capacitor #1"),
        node("charger_vbus_hf_cap", "100-nF 50-V charger VBUS HF capacitor"),
        node("charger_pmid_cap0", "10-uF 25-V X7R charger PMID capacitor #0"),
        node("charger_pmid_cap1", "10-uF 25-V X7R charger PMID capacitor #1"),
        node("charger_pmid_cap2", "10-uF 25-V X7R charger PMID capacitor #2"),
        node("charger_pmid_hf_cap", "100-nF 50-V charger PMID HF capacitor"),
        node("charger_sys_cap0", "10-uF 25-V X7R charger SYS capacitor #0"),
        node("charger_sys_cap1", "10-uF 25-V X7R charger SYS capacitor #1"),
        node("charger_sys_cap2", "10-uF 25-V X7R charger SYS capacitor #2"),
        node("charger_sys_cap3", "10-uF 25-V X7R charger SYS capacitor #3"),
        node("charger_sys_cap4", "10-uF 25-V X7R charger SYS capacitor #4"),
        node("charger_sys_hf_cap", "100-nF 50-V charger SYS HF capacitor"),
        node("charger_bat_cap0", "10-uF 25-V X7R charger BAT capacitor #0"),
        node("charger_bat_cap1", "10-uF 25-V X7R charger BAT capacitor #1"),
        node("charger_btst1_cap", "47-nF 25-V charger bootstrap capacitor #1"),
        node("charger_btst2_cap", "47-nF 25-V charger bootstrap capacitor #2"),
        node("charger_regn_cap", "4.7-uF 25-V charger REGN capacitor"),
        node("charger_sdrv_cap", "1-nF 50-V no-ship-FET SDRV capacitor"),
        node("charger_prog_res", "8.2-kOhm 1% 2S/750-kHz PROG resistor"),
        node("charger_batp_res", "100-Ohm 1% BATP sense resistor"),
        node("charger_ts_top", "5.23-kOhm 1% charger TS upper resistor"),
        node("charger_ts_bottom", "30.1-kOhm 1% charger TS lower resistor"),
        node("charger_ts_ntc", "independent 10-kOhm charger battery NTC"),
        node("charger_ilim_top", "44.2-kOhm 1% hardware ILIM upper resistor"),
        node("charger_ilim_bottom", "100-kOhm 1% hardware ILIM lower resistor"),
        node("charger_int_pullup", "10-kOhm charger INT pull-up resistor"),
        node("charger_ce_pullup", "10-kOhm reset-high charger CE pull-up resistor"),
        node("pack_holder", "polarized dual protected-button-top 18650 retention and four independent contacts"),
        node("pack_cell0", "individually replaceable protected button-top 4-Ah cell #0"),
        node("pack_fuse0", "slot-0 independent 5-A fast fuse"),
        node("pack_ntc0", "cell-0 temperature sensor"),
        node("pack_cell1", "individually replaceable protected button-top 4-Ah cell #1"),
        node("pack_fuse1", "slot-1 independent 5-A fast fuse"),
        node("pack_ntc1", "cell-1 temperature sensor"),
        node("pack_gauge", "2S high-side protection, gauging, temperature and balancing"),
        node("pack_in_res", "10-Ohm MAX17320 IN series resistor"),
        node("pack_in_bypass", "100-nF 50-V MAX17320 IN bypass capacitor"),
        node("pack_cp_cap", "0.47-uF 25-V MAX17320 CP-to-IN capacitor"),
        node("pack_aoldo_cap", "0.47-uF 25-V MAX17320 AOLDO bypass capacitor"),
        node("pack_reg3_cap", "0.47-uF 25-V MAX17320 REG3 bypass capacitor"),
        node("pack_reg2_cap", "0.47-uF 25-V MAX17320 REG2 bypass capacitor"),
        node("pack_cell1_rbal", "49.9-Ohm 0.66-W bottom-cell balancing resistor"),
        node("pack_batts_rbal", "49.9-Ohm 0.66-W top-cell balancing resistor"),
        node("pack_cell1_filter_cap", "100-nF 50-V bottom-cell sense filter capacitor"),
        node("pack_batts_filter_cap", "100-nF 50-V top-cell sense filter capacitor"),
        node("pack_pckp_res", "1-kOhm protected-pack PCKP series resistor"),
        node("pack_shunt", "5-mOhm Kelvin current shunt"),
        node("pack_power_fet", "fully-switching common-drain CHG/DIS power pair"),
        node("pack_chg_gate_cap", "100-nF charge-FET gate-to-source capacitor"),
        node("pack_dis_gate_cap", "100-nF discharge-FET gate-to-source capacitor"),
        node("pack_hold", "reset-default ALRT hold and explicit release"),
        node("pack_hold_pullup", "10-kOhm reset-default ALRT-hold pull-up resistor"),
        node("pack_hold_release_pulldown", "10-kOhm hold-release fail-low resistor"),
        node("pack_alrt_pullup", "10-kOhm REG3-referenced ALRT release pull-up resistor"),
        node("pack_status_buffer", "dual PFAIL level translator and passive-drain system IRQ"),
        node("pack_pfail_pullup", "10-kOhm admission-referenced PFAIL_N pull-up resistor"),
        node("pack_irq_gate_pulldown", "10-kOhm shared-IRQ gate fail-low resistor"),
        node("pack_gauge_scl_pullup", "10-kOhm private gauge-clock pull-up resistor"),
        node("pack_gauge_sda_pullup", "10-kOhm private gauge-data pull-up resistor"),
        node("pack_supply_or", "AOLDO/fixture source isolation"),
        node("pack_system_diode", "admitted-system source isolation and priority"),
        node("pack_admission", "fail-closed pair admission, watchdog and service bridge"),
        node("pack_admission_bulk_cap", "10-uF admission-controller bulk decoupling capacitor"),
        node("pack_admission_bypass", "100-nF admission-controller bypass capacitor"),
        node("pack_admission_reset_pullup", "47-kOhm admission-controller NRST pull-up resistor"),
        node("pack_admission_reset_cap", "10-nF admission-controller NRST capacitor"),
        node("power_command_switch", "single maintained low-current RUN/KILL command switch"),
        node("power_command_pullup", "47-kOhm admission-domain ON-command pull-up resistor"),
        node("power_command_filter", "100-nF power-command contact filter capacitor"),
        node("pack_diag_timer", "non-retriggerable pulse limiter and refractory lockout"),
        node("pack_diag_timer_res", "169-kOhm 1% diagnostic-pulse timing resistor"),
        node("pack_diag_timer_cap", "220-nF 50-V C0G diagnostic-pulse timing capacitor"),
        node("pack_diag_lockout_res", "620-kOhm 1% refractory-lockout timing resistor"),
        node("pack_diag_lockout_cap", "1-uF 16-V X7R refractory-lockout timing capacitor"),
        node("pack_diag_timer_bypass", "100-nF 50-V X7R one-shot bypass capacitor"),
        node("pack_diag_trigger_pulldown", "10-kOhm 1% diagnostic-trigger fail-low resistor"),
        node("pack_diag_gate_pulldown", "10-kOhm 1% diagnostic-gate fail-low resistor"),
        node("pack_diag_switch", "20-V low-gate-drive diagnostic-load MOSFET"),
        node("pack_diag_res0", "20-Ohm 2-W pulse-rated diagnostic-load branch #0"),
        node("pack_diag_res1", "20-Ohm 2-W pulse-rated diagnostic-load branch #1"),
        node("pack_mid_adc_top0", "220-kOhm 1% midpoint-divider top resistor #0"),
        node("pack_mid_adc_top1", "220-kOhm 1% midpoint-divider top resistor #1"),
        node("pack_mid_adc_bottom", "169-kOhm 1% midpoint-divider bottom resistor"),
        node("pack_mid_adc_filter", "10-nF 50-V X7R midpoint ADC filter capacitor"),
        node("pack_stack_adc_top0", "220-kOhm 1% stack-divider top resistor #0"),
        node("pack_stack_adc_top1", "220-kOhm 1% stack-divider top resistor #1"),
        node("pack_stack_adc_top2", "220-kOhm 1% stack-divider top resistor #2"),
        node("pack_stack_adc_top3", "220-kOhm 1% stack-divider top resistor #3"),
        node("pack_stack_adc_top4", "220-kOhm 1% stack-divider top resistor #4"),
        node("pack_stack_adc_bottom", "169-kOhm 1% stack-divider bottom resistor"),
        node("pack_stack_adc_filter", "10-nF 50-V X7R stack ADC filter capacitor"),
        "  end",
        "  subgraph POWER_RAILS[\"Independent fixed rails and quiet-state switches\"]",
        node("aon_buck", "low-IQ always-on 3.3-V safety converter"),
        node("aon_inductor", "2.2-uH shielded AON converter inductor"),
        node("aon_mode_res", "42.2-kOhm 1% AON mode/configuration resistor"),
        node("aon_input_cap", "4.7-uF 25-V X7R AON input capacitor"),
        node("aon_output_cap", "22-uF 10-V X7R AON raw-output capacitor"),
        node("aon_efuse", "independent AON overvoltage/current/short cutoff"),
        node("aon_efuse_rilim", "240-kOhm 1% AON eFuse current-limit resistor"),
        node("aon_efuse_ovlo_top", "196-kOhm 1% AON eFuse OVLO top resistor"),
        node("aon_efuse_ovlo_bottom", "100-kOhm 1% AON eFuse OVLO bottom resistor"),
        node("aon_efuse_input_cap", "100-nF 50-V X7R AON eFuse input capacitor"),
        node("aon_efuse_output_cap", "10-uF 6.3-V X5R protected-AON output capacitor"),
        node("aon_pg_pullup", "47-kOhm 1% AON power-good pull-up resistor"),
        node("main_buck", "fixed 3.3-V 4-A main converter"),
        node("main_inductor", "3.3-uH main-rail power inductor"),
        node("main_input_cap", "22-uF 25-V X7R main-converter bulk input capacitor"),
        node("main_hf_input_cap", "100-nF 50-V X7R main-converter HF input capacitor"),
        node("main_fb_top", "45.3-kOhm 1% main feedback top resistor"),
        node("main_fb_bottom", "10-kOhm 1% main feedback bottom resistor"),
        node("main_ff_cap", "33-pF 50-V C0G main feed-forward capacitor"),
        node("main_output_cap0", "22-uF 25-V X7R main raw-output capacitor #0"),
        node("main_output_cap1", "22-uF 25-V X7R main raw-output capacitor #1"),
        node("main_efuse", "main latch-off overvoltage circuit-breaker eFuse with protected PG"),
        node("main_efuse_rilm", "1.65-kOhm 1% main eFuse threshold resistor"),
        node("main_efuse_dvdt_cap", "4.7-nF 50-V X7R main eFuse slew capacitor"),
        node("main_efuse_itimer_cap", "120-pF 50-V C0G main eFuse transient timer"),
        node("main_efuse_ovlo_top", "191-kOhm 0.1% main eFuse OVLO top resistor"),
        node("main_efuse_ovlo_bottom", "100-kOhm 0.1% main eFuse OVLO bottom resistor"),
        node("main_efuse_pg_top", "45.3-kOhm 1% main protected-PG top resistor"),
        node("main_efuse_pg_bottom", "30-kOhm 1% main protected-PG bottom resistor"),
        node("main_efuse_output_cap", "10-uF 6.3-V X5R protected-main output capacitor"),
        node("main_en_pulldown", "100-kOhm 1% main-enable fail-low resistor"),
        node("power_fault_pullup", "10-kOhm 1% wired-low power-fault pull-up resistor"),
        node("voice_buck", "fixed 4.0-V 4-A voice converter"),
        node("voice_inductor", "3.3-uH voice-rail power inductor"),
        node("voice_input_cap", "22-uF 25-V X7R voice-converter bulk input capacitor"),
        node("voice_hf_input_cap", "100-nF 50-V X7R voice-converter HF input capacitor"),
        node("voice_fb_top", "68-kOhm 1% voice feedback top resistor"),
        node("voice_fb_bottom", "12-kOhm 1% voice feedback bottom resistor"),
        node("voice_ff_cap", "33-pF 50-V C0G voice feed-forward capacitor"),
        node("voice_output_cap0", "22-uF 25-V X7R voice raw-output capacitor #0"),
        node("voice_output_cap1", "22-uF 25-V X7R voice raw-output capacitor #1"),
        node("voice_efuse", "voice latch-off overvoltage circuit-breaker eFuse with protected PG"),
        node("voice_efuse_rilm", "3.32-kOhm 1% voice eFuse threshold resistor"),
        node("voice_efuse_dvdt_cap", "4.7-nF 50-V X7R voice eFuse slew capacitor"),
        node("voice_efuse_itimer_cap", "120-pF 50-V C0G voice eFuse transient timer"),
        node("voice_efuse_ovlo_top", "270-kOhm 1% voice eFuse OVLO top resistor"),
        node("voice_efuse_ovlo_bottom", "100-kOhm 1% voice eFuse OVLO bottom resistor"),
        node("voice_efuse_pg_top", "68-kOhm 1% voice protected-PG top resistor"),
        node("voice_efuse_pg_bottom", "33-kOhm 1% voice protected-PG bottom resistor"),
        node("voice_efuse_output_cap", "10-uF 6.3-V X5R protected-voice output capacitor"),
        node("voice_en_pulldown", "10-kOhm 1% voice-enable fail-low resistor"),
        node("voice_pg_pullup", "10-kOhm 1% voice power-good pull-up resistor"),
        node("voice_pg_base_res", "68-kOhm 1% voice PG-qualifier base resistor"),
        node("voice_pg_qualifier", "voice-rail enable-qualified PG fault transistor"),
        node("ext_buck", "fixed 5.0-V 4-A accessory converter"),
        node("ext_inductor", "4.7-uH accessory-rail power inductor"),
        node("ext_buck_input_cap", "22-uF 25-V X7R accessory-converter bulk input capacitor"),
        node("ext_buck_hf_input_cap", "100-nF 50-V X7R accessory-converter HF input capacitor"),
        node("ext_buck_fb_top", "220-kOhm 1% accessory feedback top resistor"),
        node("ext_buck_fb_bottom", "30-kOhm 1% accessory feedback bottom resistor"),
        node("ext_buck_ff_cap", "33-pF 50-V C0G accessory feed-forward capacitor"),
        node("ext_buck_output_cap0", "22-uF 25-V X7R accessory output capacitor #0"),
        node("ext_buck_output_cap1", "22-uF 25-V X7R accessory output capacitor #1"),
        node("ext_en_pulldown", "10-kOhm 1% accessory-enable fail-low resistor"),
        node("ext_pg_pullup", "10-kOhm 1% accessory power-good pull-up resistor"),
        node("ext_pg_base_res", "68-kOhm 1% accessory PG-qualifier base resistor"),
        node("ext_pg_qualifier", "accessory-rail enable-qualified PG fault transistor"),
        node("ext_efuse", "true-reverse-blocking latch-off accessory eFuse and current monitor"),
        node("ext_rilm", "2.21-kOhm 1% eFuse current-limit resistor"),
        node("ext_dvdt_cap", "4.7-nF 50-V X7R eFuse startup-slew capacitor"),
        node("ext_itimer_cap", "220-nF 25-V X7R post-start transient-timer capacitor"),
        node("ext_ovlo_top", "169-kOhm 1% eFuse OVLO top resistor"),
        node("ext_ovlo_bottom", "47-kOhm 1% eFuse OVLO bottom resistor"),
        node("ext_input_cap", "2.2-uF 25-V X7R local eFuse input capacitor"),
        node("ext_output_cap", "2.2-uF 25-V X7R local eFuse output capacitor"),
        node("ext_bleeder", "1-kOhm 1% protected-output discharge resistor"),
        node("nrf_power_switch", "three-radio nRF quiet-state load switch"),
        node("cc_power_switch", "CC1101 quiet-state load switch"),
        node("sd_power_switch", "microSD quiet-state load switch"),
        node("codec_power_switch", "ES8311 quiet-state load switch"),
        node("receiver_power_switch", "Si4732 quiet-state load switch"),
        "  end",
        "  subgraph COMPUTE[\"Compute owners\"]",
        node("s3", "application, UI, display/storage, audio, BLE/Wi-Fi owner"),
        node("s3_supply_bulk", "22-uF local S3 module bulk capacitor"),
        node("s3_supply_bypass", "100-nF local S3 module high-frequency bypass capacitor"),
        node("s3_reset_delay_cap", "1-uF S3 EN power-up delay capacitor"),
        node("c5", "2.4/5 GHz, IEEE 802.15.4 and IR owner"),
        node("rp", "deterministic radio and voice owner"),
        "  end",
        "  subgraph SERVICE_RECOVERY[\"Independent three-domain service and recovery devices\"]",
        *[node(instance, service_role(instance)) for instance in service_instance_names],
        "  %% Service layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in service_instance_names),
        "  end",
        "  subgraph UI_STORAGE[\"UI and storage devices\"]",
        node("display_connector", "40-position 0.4-mm UI-board receptacle for the replaceable display adapter"),
        node("display_adapter_plug", "40-position 0.4-mm adapter-board plug; exact 2-mm DF40 mate"),
        node("display_panel_connector", "40-position 0.5-mm dual-contact ZIF on the replaceable adapter"),
        node("display", "3.5-inch QSPI IPS display and capacitive-touch assembly"),
        node("display_touch_controller", "integrated display plus capacitive-touch TDDI COG"),
        node("display_logic_bulk_cap", "10-uF protected-main display-logic bulk capacitor"),
        node("display_logic_hf_cap", "100-nF display-logic high-frequency bypass capacitor"),
        node("display_reset_pulldown", "10-kOhm display RESX reset-default pull-down"),
        node("touch_reset_pulldown", "10-kOhm touch TP_RESXP reset-default pull-down"),
        node("backlight_efuse", "latch-off and reverse-blocking LEDA power switch"),
        node("backlight_efuse_ilim", "133-kOhm 1% approximately 200-mA backlight-limit resistor"),
        node("backlight_efuse_input_cap", "100-nF backlight-switch input bypass capacitor"),
        node("backlight_efuse_output_bulk", "10-uF protected-LEDA output bulk capacitor"),
        node("backlight_efuse_output_hf", "100-nF protected-LEDA output bypass capacitor"),
        node("backlight_fault_pullup", "10-kOhm open-drain backlight-fault pull-up"),
        node("backlight_series_resistor", "10-Ohm 0.66-W anti-surge LED cathode resistor"),
        node("backlight_mosfet", "low-gate-drive LED cathode PWM MOSFET"),
        node("backlight_gate_series", "100-Ohm PWM gate series resistor"),
        node("backlight_gate_pulldown", "10-kOhm PWM gate reset-off pull-down"),
        node("sd", "push-push microSD card connector"),
        node("sd_host_buffer", "three-channel Ioff SCK/CMD/CS card-side buffer"),
        node("sd_miso_buffer", "CS-gated Ioff DAT0/MISO return buffer"),
        node("sd_esd_a", "four-channel low-capacitance microSD signal ESD array A"),
        node("sd_esd_b", "four-channel low-capacitance microSD supply/signal/detect ESD array B"),
        node("sd_power_input_cap", "1-uF storage-switch input bypass capacitor"),
        node("sd_power_bulk_cap", "22-uF switched-card bulk capacitor"),
        node("sd_power_hf_cap", "100-nF switched-card high-frequency bypass capacitor"),
        node("sd_host_buffer_bypass", "100-nF triple-buffer bypass capacitor"),
        node("sd_miso_buffer_bypass", "100-nF return-buffer bypass capacitor"),
        node("sd_on_pulldown", "10-kOhm storage-power reset-off pull-down"),
        node("sd_host_sck_pulldown", "10-kOhm shared-clock reset-low pull-down"),
        node("sd_host_d0_pulldown", "10-kOhm GPIO46/QSPI-D0 reset-low pull-down"),
        node("sd_host_d1_pullup", "10-kOhm shared-D1 reset-high pull-up"),
        node("sd_host_cs_pullup", "10-kOhm card-CS reset-high pull-up"),
        node("lcd_host_cs_pullup", "10-kOhm display-CS reset-high pull-up"),
        node("sd_card_cmd_pullup", "10-kOhm switched-card CMD pull-up"),
        node("sd_card_dat0_pullup", "10-kOhm switched-card DAT0 pull-up"),
        node("sd_card_dat1_pullup", "10-kOhm switched-card DAT1 pull-up"),
        node("sd_card_dat2_pullup", "10-kOhm switched-card DAT2 pull-up"),
        node("sd_card_dat3_pullup", "10-kOhm switched-card DAT3/CS pull-up"),
        node("sd_sck_series", "22-Ohm buffered-card clock source-series resistor"),
        node("sd_cmd_series", "22-Ohm buffered-card CMD source-series resistor"),
        node("sd_cs_series", "22-Ohm buffered-card CS source-series resistor"),
        node("sd_miso_series", "22-Ohm card-MISO buffer source-series resistor"),
        node("sd_detect_series", "1-kOhm card-detect input series resistor"),
        node("sd_detect_pullup", "10-kOhm always-readable card-detect pull-up"),
        node("sd_detect_cap", "100-nF card-detect hardware filter capacitor"),
        node("slow_io", "24-line main slow-control expander; all P00-P27 contacts allocated"),
        node("slow_io_vcci_bypass", "100-nF main slow-I/O VCCI bypass capacitor"),
        node("slow_io_vccp_bypass", "100-nF main slow-I/O VCCP bypass capacitor"),
        node("slow_io_bulk_cap", "1-uF main slow-I/O local bulk capacitor"),
        node("slow_io_reset_pullup", "10-kOhm main slow-I/O RESET_N pull-up"),
        "  SLOW_IO_RESET((\"SLOW_IO_RESET_N<br/>protected fixture-reset node\"))",
        node("slow_io_fault_sense_iso", "AON-powered open-drain FAULT-sense domain isolator"),
        node("slow_io_fault_sense_iso_bypass", "100-nF FAULT-sense-isolator bypass capacitor"),
        node("slow_io_fault_sense_pullup", "10-kOhm main-domain FAULT-sense pull-up"),
        node("slow_io_s3_evidence_iso", "AON-powered open-drain S3-evidence domain isolator"),
        node("slow_io_s3_evidence_iso_bypass", "100-nF S3-evidence-isolator bypass capacitor"),
        node("slow_io_s3_evidence_pullup", "10-kOhm main-domain S3-evidence pull-up"),
        node("ui_matrix_io", "interrupt-capable 16-bit direct-control input expander"),
        node("ui_matrix_io_bypass", "100-nF UI-expander bypass capacitor"),
        node("ui_input_up_pullup", "10-kOhm D-pad UP pull-up"),
        node("ui_input_down_pullup", "10-kOhm D-pad DOWN pull-up"),
        node("ui_input_left_pullup", "10-kOhm D-pad LEFT pull-up"),
        node("ui_input_right_pullup", "10-kOhm D-pad RIGHT pull-up"),
        node("ui_input_ok_pullup", "10-kOhm D-pad center-push pull-up"),
        node("ui_input_back_pullup", "3.32-kOhm BACK contact-current pull-up"),
        node("ui_input_opt_pullup", "3.32-kOhm OPT contact-current pull-up"),
        node("ui_input_f1_pullup", "3.32-kOhm F1 contact-current pull-up"),
        node("ui_input_f2_pullup", "3.32-kOhm F2 contact-current pull-up"),
        node("ui_input_f3_pullup", "3.32-kOhm F3 contact-current pull-up"),
        node("ui_input_f4_pullup", "3.32-kOhm F4 contact-current pull-up"),
        node("ui_input_f5_pullup", "3.32-kOhm F5 contact-current pull-up"),
        node("ui_input_f6_pullup", "3.32-kOhm F6 contact-current pull-up"),
        node("ui_input_f7_pullup", "3.32-kOhm F7 contact-current pull-up"),
        node("ui_input_f8_pullup", "3.32-kOhm F8 contact-current pull-up"),
        node("ui_input_encoder_pullup", "3.32-kOhm encoder-push contact-current pull-up"),
        node("ui_matrix_esd", "eight-channel front-control ESD array"),
        node("front_function_esd", "eight-channel display-side function-key ESD array"),
        node("rear_control_esd", "four-channel rear encoder-push ESD array"),
        node("ui_dpad_up", "independent UP navigation button"),
        node("ui_dpad_down", "independent DOWN navigation button"),
        node("ui_dpad_left", "independent LEFT navigation button"),
        node("ui_dpad_right", "independent RIGHT navigation button"),
        node("ui_dpad_ok", "independent OK confirmation button"),
        node("ui_switch_back", "BACK ultra-low-current ordinary control"),
        node("ui_switch_opt", "OPT ultra-low-current ordinary control"),
        node("ui_switch_f1", "F1 ultra-low-current ordinary control"),
        node("ui_switch_f2", "F2 ultra-low-current ordinary control"),
        node("ui_switch_f3", "F3 ultra-low-current ordinary control"),
        node("ui_switch_f4", "F4 ultra-low-current ordinary control"),
        node("ui_switch_f5", "F5 ultra-low-current ordinary control"),
        node("ui_switch_f6", "F6 ultra-low-current ordinary control"),
        node("ui_switch_f7", "F7 ultra-low-current ordinary control"),
        node("ui_switch_f8", "F8 ultra-low-current ordinary control"),
        node("encoder", "36-detent/18-pulse rotary encoder with push"),
        node("encoder_knob", "15-mm soft-touch 6x4.5-mm D-shaft encoder knob"),
        node("encoder_a_pullup", "3.32-kOhm encoder-phase-A contact-current pull-up"),
        node("encoder_b_pullup", "3.32-kOhm encoder-phase-B contact-current pull-up"),
        node("encoder_ptt_esd", "four-channel encoder/PTT low-capacitance ESD array"),
        node("ptt_pullup", "10-kOhm direct-PTT contact-current pull-up"),
        node("ptt_series", "1-kOhm direct-PTT input series resistor"),
        node("ptt_filter_cap", "100-nF direct-PTT hardware filter capacitor"),
        "  PTT_RAW((\"PTT_BUTTON_RAW_N<br/>active-low direct-PTT node\"))",
        node("touch_irq_buffer", "fixed non-inverting open-drain touch-interrupt normalizer"),
        node("touch_irq_pullup", "10-kOhm active-low TP_INT raw pull-up"),
        node("touch_irq_buffer_bypass", "100-nF touch-interrupt-buffer bypass capacitor"),
        "  TOUCH_IRQ_RAW((\"LCD_TOUCH_INT_RAW_N<br/>active-low ST77922 touch node\"))",
        "  end",
        "  subgraph AUDIO_PATH[\"Broadcast, voice and fail-safe audio devices\"]",
        *[
            node(
                instance,
                audio_roles.get(instance, instance.replace("_", " ") + " physical component"),
            )
            for instance in audio_instance_names
        ],
        "  %% Audio layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in audio_instance_names),
        "  end",
        "  subgraph RADIO_ACCESSORY[\"Radio and external-accessory devices\"]",
        *[node(instance, native_rf_roles[instance]) for instance in native_rf_support_instance_names],
        node("s3_external_rp_sma", "S3 dedicated 6-GHz IP67 RP-SMA edge-launch jack"),
        node("c5_external_rp_sma", "C5 dedicated 6-GHz IP67 RP-SMA edge-launch jack"),
        *[node(instance, nrf_role(instance)) for instance in nrf_support_instance_names],
        node("nrf0_external_sma", "nRF0 dedicated 6-GHz IP67 standard-SMA edge-launch jack"),
        node("nrf1_external_sma", "nRF1 dedicated 6-GHz IP67 standard-SMA edge-launch jack"),
        node("nrf2_external_sma", "nRF2 dedicated 6-GHz IP67 standard-SMA edge-launch jack"),
        node("cc", "sub-GHz transceiver"),
        *[node(instance, cc_role(instance)) for instance in cc_support_instance_names],
        node("cc_external_sma", "CC dedicated 6-GHz IP67 standard-SMA edge-launch jack"),
        "  %% CC layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in cc_support_instance_names),
        node("voice", "136-174/400-470-MHz analog voice transceiver"),
        *[node(instance, voice_rf_roles[instance]) for instance in voice_rf_support_instance_names],
        node("voice_external_sma", "voice dedicated 6-GHz IP67 standard-SMA edge-launch jack"),
        node("receiver_fmsw_external_sma", "dedicated FM/SW standard-SMA receive jack"),
        node("receiver_amlw_external_sma", "dedicated non-50-Ohm AM/LW loop-pod standard-SMA jack"),
        "  %% Voice-RF layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in voice_rf_support_instance_names),
        node("u214", "external LoRa/GNSS Cap module"),
        node("u214_connector", "vertical 14-contact Cap-Bus host socket on raised rear rail"),
        node("u214_i2c_iso", "external I2C stuck-bus isolator"),
        node("u214_i2c_iso_bypass", "100-nF external-I2C-isolator bypass capacitor"),
        node("u214_i2c_host_sda_pullup", "2.2-kOhm U214 controller-side SDA pull-up"),
        node("u214_i2c_host_scl_pullup", "2.2-kOhm U214 controller-side SCL pull-up"),
        node("u214_host_buffer_a", "U214 RST/GPS-RX/SCK/MOSI Ioff buffer"),
        node("u214_host_buffer_b", "U214 NSS plus disabled-spare Ioff buffer"),
        node("u214_return_buffer", "U214 BUSY/IRQ/GPS-TX/MISO Ioff return buffer"),
        node("u214_host_buffer_a_bypass", "100-nF first U214 host-buffer bypass capacitor"),
        node("u214_host_buffer_b_bypass", "100-nF second U214 host-buffer bypass capacitor"),
        node("u214_return_buffer_bypass", "100-nF U214 return-buffer bypass capacitor"),
        node("u214_series_rst", "22-Ohm U214 reset source-series resistor"),
        node("u214_series_gps_rx", "22-Ohm U214 GPS-RX source-series resistor"),
        node("u214_series_sck", "22-Ohm U214 SPI-clock source-series resistor"),
        node("u214_series_mosi", "22-Ohm U214 MOSI source-series resistor"),
        node("u214_series_nss", "22-Ohm U214 NSS source-series resistor"),
        node("u214_series_busy", "22-Ohm U214 BUSY return-series resistor"),
        node("u214_series_irq", "22-Ohm U214 IRQ return-series resistor"),
        node("u214_series_gps_tx", "22-Ohm U214 GPS-TX return-series resistor"),
        node("u214_series_miso", "22-Ohm U214 MISO return-series resistor"),
        node("u214_esd_a", "four-channel U214 I2C/RST/GPS-RX ESD array"),
        node("u214_esd_b", "four-channel U214 SCK/MOSI/NSS/BUSY ESD array"),
        node("u214_esd_c", "four-channel U214 IRQ/GPS-TX/MISO/contact-5 evidence ESD array"),
        node("ext_request_or", "U214/native-Unit branch-request OR gate"),
        node("ext_request_or_bypass", "100-nF external-request-OR bypass capacitor"),
        node("ext_any_req_pulldown", "10-kOhm shared-5-V request fail-low resistor"),
        node("ext_branch_gate", "dual FAULT_KILL-qualified U214/native-Unit branch gate"),
        node("ext_branch_gate_bypass", "100-nF external-branch-gate bypass capacitor"),
        node("u214_req_pulldown", "10-kOhm U214 request fail-low resistor"),
        node("unit_req_pulldown", "10-kOhm native-Unit request fail-low resistor"),
        node("u214_supervisor", "protected-U214-5-V readiness supervisor"),
        node("u214_supervisor_bypass", "100-nF U214-supervisor bypass capacitor"),
        node("u214_supervisor_sense_top", "110-kOhm U214-ready threshold top resistor"),
        node("u214_supervisor_sense_bottom", "220-kOhm U214-ready threshold bottom resistor"),
        node("u214_supervisor_ct", "10-nF U214-ready delay capacitor"),
        node("u214_supervisor_pullup", "10-kOhm U214-ready main-domain pull-up"),
        node("unit_efuse", "native-Unit true-reverse-blocking latch-off eFuse"),
        node("unit_rilm", "2.21-kOhm native-Unit eFuse current-limit resistor"),
        node("unit_dvdt_cap", "4.7-nF native-Unit eFuse slew capacitor"),
        node("unit_itimer_cap", "220-nF native-Unit post-start transient timer"),
        node("unit_ovlo_top", "169-kOhm native-Unit OVLO top resistor"),
        node("unit_ovlo_bottom", "47-kOhm native-Unit OVLO bottom resistor"),
        node("unit_input_cap", "2.2-uF native-Unit eFuse input capacitor"),
        node("unit_output_cap", "2.2-uF native-Unit eFuse output capacitor"),
        node("unit_bleeder", "1-kOhm native-Unit protected-output discharge resistor"),
        node("unit_supervisor", "protected-native-Unit-5-V readiness supervisor"),
        node("unit_supervisor_bypass", "100-nF native-Unit-supervisor bypass capacitor"),
        node("unit_supervisor_sense_top", "110-kOhm native-Unit-ready threshold top resistor"),
        node("unit_supervisor_sense_bottom", "220-kOhm native-Unit-ready threshold bottom resistor"),
        node("unit_supervisor_ct", "10-nF native-Unit-ready delay capacitor"),
        node("unit_supervisor_pullup", "10-kOhm native-Unit-ready main-domain pull-up"),
        node("unit_signal_iso", "dual bidirectional I2C/UART/GPIO Unit signal isolator"),
        node("unit_signal_iso_vcca_bypass", "100-nF Unit-isolator VCCA bypass capacitor"),
        node("unit_signal_iso_vccb_bypass", "100-nF Unit-isolator VCCB bypass capacitor"),
        node("unit_signal_iso_oe_pulldown", "10-kOhm Unit-isolator OE fail-low resistor"),
        node("unit_esd", "four-channel native-Unit connector ESD array"),
        node("unit_connector", "exact protected HY2.0-4P M5 Unit connector"),
        "  end",
        "  subgraph IR_PATH[\"IR frontend devices\"]",
        *[node(instance, ir_roles[instance]) for instance in ir_instance_names],
        "  %% IR layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in ir_instance_names),
        "  end",
        "  subgraph SAFETY_STOP[\"AON RUN/KILL, watchdog and thermal-safety devices\"]",
        node("ptt_switch", "separate normally-open hold-to-talk PTT control"),
        node("power_command_switch", "single maintained low-current RUN/KILL switch"),
        node("run_loop_pullup", "10-kOhm AON RUN-loop pull-up"),
        node("run_loop_filter", "100-nF RUN-loop contact filter"),
        node("safety_control_esd", "dedicated four-channel RUN/KILL ESD array"),
        "  RUN_LOOP((\"RUN_LOOP_RAW<br/>physical RUN/KILL node\"))",
        node("safe_supervisor", "AON rail supervisor and power-on reset"),
        node("safe_por_pullup", "10-kOhm 1% AON POR pull-up resistor"),
        node("safety_controller", "independent MSPM0 watchdog, thermal and TX-lease controller"),
        node("safety_controller_bulk", "10-uF safety-controller bulk capacitor"),
        node("safety_controller_bypass", "100-nF safety-controller bypass capacitor"),
        node("safety_controller_reset_pullup", "47-kOhm safety-controller reset pull-up"),
        node("safety_controller_reset_cap", "10-nF safety-controller reset filter"),
        node("safety_watchdog", "independent 1.6-s timeout watchdog"),
        node("safety_watchdog_bypass", "100-nF watchdog bypass capacitor"),
        node("safety_watchdog_wdo_pullup", "10-kOhm open-drain WDO pull-up"),
        node("safety_watchdog_wdi_pulldown", "10-kOhm watchdog-input reset default"),
        node("safety_watchdog_mr_pullup", "10-kOhm watchdog manual-reset pull-up"),
        node("safety_fault_request_pulldown", "10-kOhm fail-low controller fault default"),
        node("safety_fault_request_iso", "open-drain safety-controller fault request"),
        node("safety_fault_request_iso_bypass", "100-nF fault-request buffer bypass"),
        node("safe_run_fault_iso", "open-drain physical-KILL fault request"),
        node("safe_run_fault_iso_bypass", "100-nF RUN fault-buffer bypass"),
        node("fault_assert_pullup", "10-kOhm wired FAULT_ASSERT_N pull-up"),
        node("safety_s3_reset_iso", "open-drain bounded S3 fault-reset request"),
        node("safety_s3_reset_iso_bypass", "100-nF S3-reset buffer bypass"),
        node("power_zone_ntc", "POWER-zone 10-kOhm NTC"),
        node("power_zone_temp_pullup", "10-kOhm POWER-zone ADC pull-up"),
        node("power_zone_temp_filter", "100-nF POWER-zone ADC filter"),
        node("rf_zone_ntc", "RF/VOICE-zone 10-kOhm NTC"),
        node("rf_zone_temp_pullup", "10-kOhm RF/VOICE-zone ADC pull-up"),
        node("rf_zone_temp_filter", "100-nF RF/VOICE-zone ADC filter"),
        node("ui_zone_ntc", "UI/DISPLAY-zone 10-kOhm NTC"),
        node("ui_zone_temp_pullup", "10-kOhm UI/DISPLAY-zone ADC pull-up"),
        node("ui_zone_temp_filter", "100-nF UI/DISPLAY-zone ADC filter"),
        node("safe_conditioner", "physical RUN and S3 fault-reset Schmitt conditioner"),
        node("safe_latch", "asynchronous latched FAULT_KILL"),
        node("safe_reset_buffer", "AON open-drain RUN-permit inverter"),
        node("safe_reset_buffer_bypass", "100-nF AON reset-driver bypass capacitor"),
        node("safe_reset_gate_pullup", "10-kOhm C5/RP fail-reset gate pull-up"),
        node("s3_reset_gate_pullup", "10-kOhm S3 fault-reset gate pull-up"),
        node("safe_reset_sink_a", "independent passive-drain S3/C5 reset sinks"),
        node("safe_reset_sink_b", "independent passive-drain RP reset sink plus inert spare"),
        node("s3_reset_pullup", "10-kOhm passive S3 EN pull-up resistor"),
        node("c5_reset_pullup", "10-kOhm passive C5 CHIP_PU pull-up resistor"),
        node("rp_reset_pullup", "10-kOhm passive RP RUN pull-up resistor"),
        node("safe_gate_a", "four FAULT_KILL-dominant nRF request gates"),
        node("safe_gate_b", "four FAULT_KILL-dominant rail/IR/accessory gates"),
        node("safe_ptt_or", "active-low voice PTT force-RX gate"),
        node("fault_led", "orange physical latched-FAULT indicator"),
        node("fault_led_series", "2.2-kOhm physical FAULT-indicator current limit"),
        "  end",
        "  subgraph TX_EVIDENCE[\"Per-path physical TX-evidence devices\"]",
        node("det_s3", "S3 2.4-GHz RF power detector"),
        node("det_c5", "C5 2.4/5-GHz RF power detector"),
        node("det_nrf0", "nRF0 2.4-GHz RF power detector"),
        node("det_nrf1", "nRF1 2.4-GHz RF power detector"),
        node("det_nrf2", "nRF2 2.4-GHz RF power detector"),
        node("det_cc", "CC1101 sub-GHz RF power detector"),
        node("det_voice", "SA518 VHF/UHF RF power detector"),
        node("det_ir", "IR optical-evidence photodiode"),
        *[node(instance, evidence_role(instance)) for instance in evidence_support_instance_names],
        "  %% TX-evidence layout-only invisible spine: every box above is one physical device.",
        "  " + " ~~~ ".join(instance.upper() for instance in evidence_support_instance_names),
        "  end",
        "  %% Layout-only invisible spine: these links are not electrical connections.",
        "  PRODUCT_USB_CONNECTOR ~~~ PRODUCT_USB_PROTECTOR ~~~ PRODUCT_USB_DP_SERIES ~~~ PRODUCT_USB_DM_SERIES ~~~ PRODUCT_USB_VBIAS_CAP ~~~ PRODUCT_USB_VPWR_CAP ~~~ PRODUCT_USB_FAULT_PULLUP ~~~ PD_CC1_CAP ~~~ PD_CC2_CAP ~~~ PD_VBUS_TVS ~~~ PD_CONTROLLER ~~~ PD_CONFIG_EEPROM ~~~ NVDC_CHARGER",
        "  NVDC_CHARGER ~~~ PACK_HOLDER ~~~ PACK_CELL0 ~~~ PACK_FUSE0 ~~~ PACK_NTC0 ~~~ PACK_CELL1 ~~~ PACK_FUSE1 ~~~ PACK_NTC1",
        "  PACK_NTC1 ~~~ PACK_GAUGE ~~~ PACK_IN_RES ~~~ PACK_IN_BYPASS ~~~ PACK_CP_CAP ~~~ PACK_AOLDO_CAP ~~~ PACK_REG3_CAP ~~~ PACK_REG2_CAP",
        "  PACK_REG2_CAP ~~~ PACK_CELL1_RBAL ~~~ PACK_BATTS_RBAL ~~~ PACK_CELL1_FILTER_CAP ~~~ PACK_BATTS_FILTER_CAP ~~~ PACK_PCKP_RES ~~~ PACK_SHUNT ~~~ PACK_POWER_FET ~~~ PACK_CHG_GATE_CAP ~~~ PACK_DIS_GATE_CAP",
        "  PACK_DIS_GATE_CAP ~~~ PACK_HOLD ~~~ PACK_HOLD_PULLUP ~~~ PACK_HOLD_RELEASE_PULLDOWN ~~~ PACK_ALRT_PULLUP ~~~ PACK_STATUS_BUFFER ~~~ PACK_PFAIL_PULLUP ~~~ PACK_IRQ_GATE_PULLDOWN ~~~ PACK_GAUGE_SCL_PULLUP ~~~ PACK_GAUGE_SDA_PULLUP",
        "  PACK_GAUGE_SDA_PULLUP ~~~ PACK_SUPPLY_OR ~~~ PACK_SYSTEM_DIODE ~~~ PACK_ADMISSION ~~~ PACK_ADMISSION_BULK_CAP ~~~ PACK_ADMISSION_BYPASS ~~~ PACK_ADMISSION_RESET_PULLUP ~~~ PACK_ADMISSION_RESET_CAP",
        "  PACK_ADMISSION_RESET_CAP ~~~ POWER_COMMAND_SWITCH ~~~ POWER_COMMAND_PULLUP ~~~ POWER_COMMAND_FILTER ~~~ PACK_DIAG_TIMER ~~~ PACK_DIAG_TIMER_RES ~~~ PACK_DIAG_TIMER_CAP ~~~ PACK_DIAG_LOCKOUT_RES ~~~ PACK_DIAG_LOCKOUT_CAP ~~~ PACK_DIAG_TIMER_BYPASS ~~~ PACK_DIAG_TRIGGER_PULLDOWN ~~~ PACK_DIAG_GATE_PULLDOWN",
        "  PACK_DIAG_GATE_PULLDOWN ~~~ PACK_DIAG_SWITCH ~~~ PACK_DIAG_RES0 ~~~ PACK_DIAG_RES1 ~~~ PACK_MID_ADC_TOP0 ~~~ PACK_MID_ADC_TOP1 ~~~ PACK_MID_ADC_BOTTOM ~~~ PACK_MID_ADC_FILTER",
        "  PACK_MID_ADC_FILTER ~~~ PACK_STACK_ADC_TOP0 ~~~ PACK_STACK_ADC_TOP1 ~~~ PACK_STACK_ADC_TOP2 ~~~ PACK_STACK_ADC_TOP3 ~~~ PACK_STACK_ADC_TOP4 ~~~ PACK_STACK_ADC_BOTTOM ~~~ PACK_STACK_ADC_FILTER",
        "  PACK_STACK_ADC_FILTER ~~~ AON_BUCK ~~~ AON_INDUCTOR ~~~ AON_MODE_RES ~~~ AON_INPUT_CAP ~~~ AON_OUTPUT_CAP ~~~ AON_EFUSE ~~~ AON_EFUSE_RILIM ~~~ AON_EFUSE_OVLO_TOP ~~~ AON_EFUSE_OVLO_BOTTOM ~~~ AON_EFUSE_INPUT_CAP ~~~ AON_EFUSE_OUTPUT_CAP ~~~ AON_PG_PULLUP",
        "  AON_PG_PULLUP ~~~ MAIN_BUCK ~~~ MAIN_INDUCTOR ~~~ MAIN_INPUT_CAP ~~~ MAIN_HF_INPUT_CAP ~~~ MAIN_FB_TOP ~~~ MAIN_FB_BOTTOM ~~~ MAIN_FF_CAP ~~~ MAIN_OUTPUT_CAP0 ~~~ MAIN_OUTPUT_CAP1 ~~~ MAIN_EFUSE ~~~ MAIN_EFUSE_RILM ~~~ MAIN_EFUSE_DVDT_CAP ~~~ MAIN_EFUSE_ITIMER_CAP ~~~ MAIN_EFUSE_OVLO_TOP ~~~ MAIN_EFUSE_OVLO_BOTTOM ~~~ MAIN_EFUSE_PG_TOP ~~~ MAIN_EFUSE_PG_BOTTOM ~~~ MAIN_EFUSE_OUTPUT_CAP ~~~ MAIN_EN_PULLDOWN ~~~ POWER_FAULT_PULLUP",
        "  POWER_FAULT_PULLUP ~~~ VOICE_BUCK ~~~ VOICE_INDUCTOR ~~~ VOICE_INPUT_CAP ~~~ VOICE_HF_INPUT_CAP ~~~ VOICE_FB_TOP ~~~ VOICE_FB_BOTTOM ~~~ VOICE_FF_CAP ~~~ VOICE_OUTPUT_CAP0 ~~~ VOICE_OUTPUT_CAP1 ~~~ VOICE_EFUSE ~~~ VOICE_EFUSE_RILM ~~~ VOICE_EFUSE_DVDT_CAP ~~~ VOICE_EFUSE_ITIMER_CAP ~~~ VOICE_EFUSE_OVLO_TOP ~~~ VOICE_EFUSE_OVLO_BOTTOM ~~~ VOICE_EFUSE_PG_TOP ~~~ VOICE_EFUSE_PG_BOTTOM ~~~ VOICE_EFUSE_OUTPUT_CAP ~~~ VOICE_EN_PULLDOWN ~~~ VOICE_PG_PULLUP ~~~ VOICE_PG_BASE_RES ~~~ VOICE_PG_QUALIFIER",
        "  VOICE_PG_QUALIFIER ~~~ EXT_BUCK ~~~ EXT_INDUCTOR ~~~ EXT_BUCK_INPUT_CAP ~~~ EXT_BUCK_HF_INPUT_CAP ~~~ EXT_BUCK_FB_TOP ~~~ EXT_BUCK_FB_BOTTOM ~~~ EXT_BUCK_FF_CAP ~~~ EXT_BUCK_OUTPUT_CAP0 ~~~ EXT_BUCK_OUTPUT_CAP1 ~~~ EXT_EN_PULLDOWN ~~~ EXT_PG_PULLUP ~~~ EXT_PG_BASE_RES ~~~ EXT_PG_QUALIFIER ~~~ EXT_EFUSE",
        "  EXT_EFUSE ~~~ EXT_RILM ~~~ EXT_DVDT_CAP ~~~ EXT_ITIMER_CAP ~~~ EXT_OVLO_TOP ~~~ EXT_OVLO_BOTTOM",
        "  EXT_OVLO_BOTTOM ~~~ EXT_INPUT_CAP ~~~ EXT_OUTPUT_CAP ~~~ EXT_BLEEDER ~~~ NRF_POWER_SWITCH ~~~ CC_POWER_SWITCH ~~~ SD_POWER_SWITCH ~~~ CODEC_POWER_SWITCH ~~~ RECEIVER_POWER_SWITCH ~~~ S3 ~~~ S3_SUPPLY_BULK ~~~ S3_SUPPLY_BYPASS ~~~ S3_RESET_DELAY_CAP ~~~ SLOW_IO",
        "  SLOW_IO ~~~ SLOW_IO_VCCI_BYPASS ~~~ SLOW_IO_VCCP_BYPASS ~~~ SLOW_IO_BULK_CAP ~~~ SLOW_IO_RESET_PULLUP ~~~ SLOW_IO_RESET ~~~ SLOW_IO_FAULT_SENSE_ISO ~~~ SLOW_IO_FAULT_SENSE_ISO_BYPASS ~~~ SLOW_IO_FAULT_SENSE_PULLUP",
        "  SLOW_IO_FAULT_SENSE_PULLUP ~~~ SLOW_IO_S3_EVIDENCE_ISO ~~~ SLOW_IO_S3_EVIDENCE_ISO_BYPASS ~~~ SLOW_IO_S3_EVIDENCE_PULLUP ~~~ UI_MATRIX_IO ~~~ UI_MATRIX_IO_BYPASS ~~~ UI_INPUT_UP_PULLUP ~~~ UI_INPUT_DOWN_PULLUP ~~~ UI_INPUT_LEFT_PULLUP ~~~ UI_INPUT_RIGHT_PULLUP ~~~ UI_INPUT_OK_PULLUP",
        "  UI_INPUT_OK_PULLUP ~~~ UI_INPUT_BACK_PULLUP ~~~ UI_INPUT_OPT_PULLUP ~~~ UI_INPUT_F1_PULLUP ~~~ UI_INPUT_F2_PULLUP ~~~ UI_INPUT_F3_PULLUP ~~~ UI_INPUT_F4_PULLUP",
        "  UI_INPUT_F4_PULLUP ~~~ UI_INPUT_F5_PULLUP ~~~ UI_INPUT_F6_PULLUP ~~~ UI_INPUT_F7_PULLUP ~~~ UI_INPUT_F8_PULLUP ~~~ UI_INPUT_ENCODER_PULLUP ~~~ UI_MATRIX_ESD ~~~ FRONT_FUNCTION_ESD ~~~ REAR_CONTROL_ESD",
        "  REAR_CONTROL_ESD ~~~ UI_DPAD_UP ~~~ UI_DPAD_DOWN ~~~ UI_DPAD_LEFT ~~~ UI_DPAD_RIGHT ~~~ UI_DPAD_OK ~~~ UI_SWITCH_BACK ~~~ UI_SWITCH_OPT ~~~ UI_SWITCH_F1 ~~~ UI_SWITCH_F2",
        "  UI_SWITCH_F2 ~~~ UI_SWITCH_F3 ~~~ UI_SWITCH_F4 ~~~ UI_SWITCH_F5 ~~~ UI_SWITCH_F6 ~~~ UI_SWITCH_F7 ~~~ UI_SWITCH_F8 ~~~ ENCODER ~~~ ENCODER_A_PULLUP ~~~ ENCODER_B_PULLUP",
        "  ENCODER_B_PULLUP ~~~ ENCODER_PTT_ESD ~~~ PTT_PULLUP ~~~ PTT_SERIES ~~~ PTT_FILTER_CAP ~~~ PTT_RAW ~~~ TOUCH_IRQ_PULLUP ~~~ TOUCH_IRQ_RAW ~~~ TOUCH_IRQ_BUFFER ~~~ TOUCH_IRQ_BUFFER_BYPASS",
        "  TOUCH_IRQ_BUFFER_BYPASS ~~~ AUDIO_SAFE_GATE ~~~ RECEIVER ~~~ AUDIO_RX_MUX ~~~ AUDIO_CAPTURE_BUFFER ~~~ CODEC",
        "  CODEC ~~~ AUDIO_SPEAKER_SELECTOR ~~~ SPEAKER_AMP ~~~ SPEAKER ~~~ MICROPHONE ~~~ HEADSET_MIC_SELECTOR ~~~ HEADSET_MIC_SELECTOR_BYPASS ~~~ HEADSET_MIC_BIAS_RES ~~~ AUDIO_TX_SELECTOR ~~~ DISPLAY_CONNECTOR ~~~ DISPLAY_ADAPTER_PLUG ~~~ DISPLAY_PANEL_CONNECTOR ~~~ DISPLAY ~~~ DISPLAY_TOUCH_CONTROLLER ~~~ DISPLAY_LOGIC_BULK_CAP ~~~ DISPLAY_LOGIC_HF_CAP",
        "  DISPLAY_LOGIC_HF_CAP ~~~ DISPLAY_RESET_PULLDOWN ~~~ TOUCH_RESET_PULLDOWN ~~~ BACKLIGHT_EFUSE ~~~ BACKLIGHT_EFUSE_ILIM ~~~ BACKLIGHT_EFUSE_INPUT_CAP ~~~ BACKLIGHT_EFUSE_OUTPUT_BULK ~~~ BACKLIGHT_EFUSE_OUTPUT_HF",
        "  BACKLIGHT_EFUSE_OUTPUT_HF ~~~ BACKLIGHT_FAULT_PULLUP ~~~ BACKLIGHT_SERIES_RESISTOR ~~~ BACKLIGHT_MOSFET ~~~ BACKLIGHT_GATE_SERIES ~~~ BACKLIGHT_GATE_PULLDOWN ~~~ SD ~~~ SD_HOST_BUFFER ~~~ SD_MISO_BUFFER ~~~ SD_ESD_A ~~~ SD_ESD_B",
        "  SD_ESD_B ~~~ SD_POWER_INPUT_CAP ~~~ SD_POWER_BULK_CAP ~~~ SD_POWER_HF_CAP ~~~ SD_HOST_BUFFER_BYPASS ~~~ SD_MISO_BUFFER_BYPASS ~~~ SD_ON_PULLDOWN ~~~ SD_HOST_SCK_PULLDOWN ~~~ SD_HOST_D0_PULLDOWN ~~~ SD_HOST_D1_PULLUP",
        "  SD_HOST_D1_PULLUP ~~~ SD_HOST_CS_PULLUP ~~~ LCD_HOST_CS_PULLUP ~~~ SD_CARD_CMD_PULLUP ~~~ SD_CARD_DAT0_PULLUP ~~~ SD_CARD_DAT1_PULLUP ~~~ SD_CARD_DAT2_PULLUP ~~~ SD_CARD_DAT3_PULLUP",
        "  SD_CARD_DAT3_PULLUP ~~~ SD_SCK_SERIES ~~~ SD_CMD_SERIES ~~~ SD_CS_SERIES ~~~ SD_MISO_SERIES ~~~ SD_DETECT_SERIES ~~~ SD_DETECT_PULLUP ~~~ SD_DETECT_CAP ~~~ UNIT_CONNECTOR",
        "  UNIT_CONNECTOR ~~~ C5 ~~~ " + " ~~~ ".join(instance.upper() for instance in ir_instance_names) + " ~~~ RP ~~~ " + " ~~~ ".join(instance.upper() for instance in service_instance_names),
        "  C5 ~~~ " + " ~~~ ".join(instance.upper() for instance in native_rf_support_instance_names),
        "  " + " ~~~ ".join(instance.upper() for instance in native_rf_support_instance_names) + " ~~~ RP",
        "  RP ~~~ " + " ~~~ ".join(instance.upper() for instance in nrf_support_instance_names) + " ~~~ CC ~~~ VOICE",
        "  VOICE ~~~ " + " ~~~ ".join(instance.upper() for instance in voice_rf_support_instance_names) + " ~~~ VOICE_EXTERNAL_SMA ~~~ " + " ~~~ ".join(instance.upper() for instance in expansion_instance_names) + " ~~~ UNIT_CONNECTOR ~~~ U214_CONNECTOR ~~~ U214 ~~~ PTT_SWITCH ~~~ POWER_COMMAND_SWITCH ~~~ RUN_LOOP_PULLUP ~~~ RUN_LOOP_FILTER ~~~ SAFETY_CONTROL_ESD",
        "  SAFETY_CONTROL_ESD ~~~ RUN_LOOP ~~~ SAFE_SUPERVISOR ~~~ SAFE_POR_PULLUP ~~~ SAFETY_CONTROLLER ~~~ SAFETY_WATCHDOG ~~~ SAFE_CONDITIONER ~~~ SAFE_LATCH",
        "  SAFE_LATCH ~~~ SAFE_RESET_BUFFER ~~~ SAFE_RESET_BUFFER_BYPASS ~~~ SAFE_RESET_GATE_PULLUP ~~~ S3_RESET_GATE_PULLUP ~~~ SAFE_RESET_SINK_A ~~~ SAFE_RESET_SINK_B ~~~ S3_RESET_PULLUP ~~~ C5_RESET_PULLUP ~~~ RP_RESET_PULLUP ~~~ SAFE_GATE_A ~~~ SAFE_GATE_B ~~~ SAFE_PTT_OR ~~~ FAULT_LED_SERIES ~~~ FAULT_LED",
        "  FAULT_LED ~~~ DET_S3 ~~~ DET_C5 ~~~ DET_NRF0 ~~~ DET_NRF1 ~~~ DET_NRF2",
        "  DET_NRF2 ~~~ DET_CC ~~~ DET_VOICE ~~~ DET_IR ~~~ " + " ~~~ ".join(instance.upper() for instance in evidence_support_instance_names),
        "  PRODUCT_USB_CONNECTOR -->|\"VBUS sink only\"| PD_CONTROLLER",
        "  PRODUCT_USB_CONNECTOR -->|\"VBUS shunt\"| PD_VBUS_TVS",
        "  PRODUCT_USB_CONNECTOR <-->|\"CC1/CC2 + D+/D-\"| PRODUCT_USB_PROTECTOR",
        "  PRODUCT_USB_PROTECTOR <-->|\"protected D+\"| PRODUCT_USB_DP_SERIES <-->|\"Full-Speed GPIO20\"| S3",
        "  PRODUCT_USB_PROTECTOR <-->|\"protected D-\"| PRODUCT_USB_DM_SERIES <-->|\"Full-Speed GPIO19\"| S3",
        "  PRODUCT_USB_PROTECTOR <-->|\"protected CC1/CC2\"| PD_CONTROLLER",
        "  C5_SERVICE_USB_CONNECTOR <-->|\"D+/D-; VBUS sense-only\"| C5_SERVICE_USB_ESD",
        "  C5_SERVICE_USB_CONNECTOR <-->|\"board-off isolated data\"| C5_SERVICE_USB_SWITCH <-->|\"22 Ω D+/D-\"| C5",
        "  RP_SERVICE_USB_CONNECTOR <-->|\"D+/D-; VBUS sense-only\"| RP_SERVICE_USB_ESD",
        "  RP_SERVICE_USB_CONNECTOR <-->|\"board-off isolated data\"| RP_SERVICE_USB_SWITCH <-->|\"27 Ω D+/D-\"| RP",
        "  S3_DBG_HEADER <-->|\"protected UART0 + RESET/BOOT\"| S3_DBG_ESD <-->|\"current-limited\"| S3",
        "  C5_DBG_HEADER <-->|\"protected UART0 + RESET/BOOT\"| C5_DBG_ESD <-->|\"current-limited\"| C5",
        "  RP_DBG_HEADER <-->|\"protected SWD + RESET/BOOT\"| RP_DBG_ESD <-->|\"current-limited\"| RP",
        "  SAFETY_CONTROLLER -->|\"deadline service\"| SAFETY_WATCHDOG -->|\"FAULT_ASSERT_N\"| SAFE_LATCH",
        "  SAFE_LATCH -->|\"RUN_PERMIT\"| SAFE_RESET_BUFFER -->|\"RF_RESET_KILL_GATE\"| SAFE_RESET_SINK_A",
        "  SAFE_RESET_BUFFER -->|\"RF_RESET_KILL_GATE\"| SAFE_RESET_SINK_B",
        "  SAFETY_CONTROLLER -->|\"bounded S3 reset\"| SAFE_CONDITIONER -->|\"S3_RESET_KILL_GATE\"| SAFE_RESET_SINK_A",
        "  SAFE_RESET_SINK_A -->|\"passive-drain EN\"| S3",
        "  SAFE_RESET_SINK_A -->|\"passive-drain CHIP_PU\"| C5",
        "  SAFE_RESET_SINK_B -->|\"passive-drain RUN\"| RP",
        "  PRODUCT_USB_PROTECTOR --> PRODUCT_USB_VBIAS_CAP",
        "  PD_CONTROLLER -->|\"LDO_3V3\"| PRODUCT_USB_VPWR_CAP --> PRODUCT_USB_PROTECTOR",
        "  PD_CONTROLLER --> PRODUCT_USB_FAULT_PULLUP --> PRODUCT_USB_PROTECTOR",
        "  PD_CONTROLLER -->|\"protected CC shunts\"| PD_CC1_CAP",
        "  PD_CONTROLLER --> PD_CC2_CAP",
        "  PD_CONTROLLER <-->|\"local I²C boot image\"| PD_CONFIG_EEPROM",
        "  PD_CONTROLLER <-->|\"protected VBUS + local I²C/IRQ\"| NVDC_CHARGER",
        "  S3 <-->|\"SYS I²C0 + shared wired-low IRQ\"| PD_CONTROLLER",
        "  PACK_CELL0 -->|\"protected button-top contacts\"| PACK_HOLDER",
        "  PACK_CELL1 -->|\"protected button-top contacts\"| PACK_HOLDER",
        "  PACK_HOLDER -->|\"independent slot-0 contacts\"| PACK_FUSE0 --> PACK_GAUGE",
        "  PACK_NTC0 -->|\"TH1\"| PACK_GAUGE",
        "  PACK_HOLDER -->|\"independent slot-1 contacts\"| PACK_FUSE1 --> PACK_GAUGE",
        "  PACK_NTC1 -->|\"TH2\"| PACK_GAUGE",
        "  PACK_NTC0 -.->|\"insulated compliant mid-can contact\"| PACK_CELL0",
        "  PACK_NTC1 -.->|\"insulated compliant mid-can contact\"| PACK_CELL1",
        "  CHARGER_TS_NTC -.->|\"indexed thermally worst-slot contact\"| PACK_HOLDER",
        "  PACK_FUSE1 -->|\"fused stack positive\"| PACK_IN_RES --> PACK_GAUGE",
        "  PACK_GAUGE --> PACK_IN_BYPASS",
        "  PACK_GAUGE -->|\"CP to IN\"| PACK_CP_CAP",
        "  PACK_GAUGE -->|\"AOLDO/REG3/REG2 local bypass\"| PACK_AOLDO_CAP",
        "  PACK_GAUGE --> PACK_REG3_CAP",
        "  PACK_GAUGE --> PACK_REG2_CAP",
        "  PACK_FUSE0 -->|\"2S midpoint\"| PACK_CELL1_RBAL --> PACK_GAUGE",
        "  PACK_FUSE1 -->|\"top of 2S stack\"| PACK_BATTS_RBAL --> PACK_GAUGE",
        "  PACK_GAUGE -->|\"CELL1 to GND\"| PACK_CELL1_FILTER_CAP",
        "  PACK_GAUGE -->|\"BATTS to shorted CELL3\"| PACK_BATTS_FILTER_CAP",
        "  PACK_SHUNT -->|\"CSP/CSN Kelvin plus force path\"| PACK_GAUGE",
        "  PACK_GAUGE -->|\"PCKP through 1 kΩ\"| PACK_PCKP_RES --> PACK_POWER_FET",
        "  PACK_GAUGE -->|\"CHG/DIS gates; no prequal\"| PACK_POWER_FET",
        "  PACK_POWER_FET --> PACK_CHG_GATE_CAP",
        "  PACK_POWER_FET --> PACK_DIS_GATE_CAP",
        "  PACK_POWER_FET <-->|\"protected 2S power boundary\"| NVDC_CHARGER",
        "  PACK_HOLD_PULLUP --> PACK_HOLD",
        "  PACK_HOLD_RELEASE_PULLDOWN --> PACK_HOLD",
        "  PACK_ALRT_PULLUP --> PACK_GAUGE",
        "  PACK_HOLD -->|\"ALRT low by default\"| PACK_GAUGE",
        "  PACK_ADMISSION -->|\"explicit release\"| PACK_HOLD",
        "  PACK_GAUGE -->|\"push-pull PFAIL\"| PACK_STATUS_BUFFER -->|\"safe active-low status\"| PACK_ADMISSION",
        "  PACK_PFAIL_PULLUP --> PACK_STATUS_BUFFER",
        "  PACK_ADMISSION -->|\"high means assert\"| PACK_STATUS_BUFFER -->|\"passive-drain SYS_INT_N\"| S3",
        "  PACK_IRQ_GATE_PULLDOWN --> PACK_STATUS_BUFFER",
        "  PACK_GAUGE_SCL_PULLUP --> PACK_GAUGE",
        "  PACK_GAUGE_SDA_PULLUP --> PACK_GAUGE",
        "  PACK_GAUGE -->|\"AOLDO\"| PACK_SUPPLY_OR --> PACK_ADMISSION",
        "  PACK_SYSTEM_DIODE -->|\"admitted 3V3\"| PACK_ADMISSION",
        "  PACK_ADMISSION --> PACK_ADMISSION_BULK_CAP",
        "  PACK_ADMISSION --> PACK_ADMISSION_BYPASS",
        "  PACK_ADMISSION -->|\"NRST\"| PACK_ADMISSION_RESET_PULLUP",
        "  PACK_ADMISSION --> PACK_ADMISSION_RESET_CAP",
        "  POWER_COMMAND_SWITCH -->|\"OFF grounds low-current request\"| PACK_ADMISSION",
        "  POWER_COMMAND_PULLUP -->|\"ON default\"| PACK_ADMISSION",
        "  POWER_COMMAND_FILTER -->|\"contact transient filter\"| PACK_ADMISSION",
        "  PACK_GAUGE <-->|\"local I²C + fault\"| PACK_ADMISSION",
        "  PACK_ADMISSION <-->|\"SYS I²C0 + shared IRQ\"| S3",
        "  PACK_ADMISSION -->|\"PA22 edge\"| PACK_DIAG_TIMER",
        "  PACK_ADMISSION --> PACK_DIAG_TRIGGER_PULLDOWN",
        "  PACK_SUPPLY_OR -->|\"admission VDD\"| PACK_DIAG_TIMER",
        "  PACK_DIAG_TIMER -->|\"169 kΩ / 220 nF; ≤50 ms\"| PACK_DIAG_TIMER_RES --> PACK_DIAG_TIMER_CAP",
        "  PACK_DIAG_TIMER -->|\"falling Q edge; ≥350-ms lockout\"| PACK_DIAG_LOCKOUT_RES --> PACK_DIAG_LOCKOUT_CAP",
        "  PACK_DIAG_TIMER --> PACK_DIAG_TIMER_BYPASS",
        "  PACK_DIAG_TIMER -->|\"bounded gate pulse\"| PACK_DIAG_SWITCH",
        "  PACK_DIAG_TIMER --> PACK_DIAG_GATE_PULLDOWN",
        "  PACK_DIAG_RES0 -->|\"fused full-stack load; 10 Ω total\"| PACK_DIAG_SWITCH",
        "  PACK_DIAG_RES1 --> PACK_DIAG_SWITCH",
        "  PACK_FUSE0 --> PACK_MID_ADC_TOP0 --> PACK_MID_ADC_TOP1 -->|\"PA25/A2\"| PACK_ADMISSION",
        "  PACK_ADMISSION --> PACK_MID_ADC_BOTTOM",
        "  PACK_ADMISSION --> PACK_MID_ADC_FILTER",
        "  PACK_FUSE1 --> PACK_STACK_ADC_TOP0 --> PACK_STACK_ADC_TOP1 --> PACK_STACK_ADC_TOP2 --> PACK_STACK_ADC_TOP3 --> PACK_STACK_ADC_TOP4 -->|\"PA26/A1\"| PACK_ADMISSION",
        "  PACK_ADMISSION --> PACK_STACK_ADC_BOTTOM",
        "  PACK_ADMISSION --> PACK_STACK_ADC_FILTER",
        "  NVDC_CHARGER -->|\"SYS\"| AON_BUCK --> AON_INDUCTOR -->|\"AON_RAW_3V3\"| AON_EFUSE -->|\"AON_SAFE_3V3\"| SAFE_SUPERVISOR",
        "  AON_BUCK -->|\"MODE/S-CONF\"| AON_MODE_RES",
        "  NVDC_CHARGER -->|\"SYS local bypass\"| AON_INPUT_CAP",
        "  AON_INDUCTOR -->|\"raw local bypass\"| AON_OUTPUT_CAP",
        "  AON_INDUCTOR --> AON_EFUSE_INPUT_CAP",
        "  AON_EFUSE -->|\"ILIM\"| AON_EFUSE_RILIM",
        "  AON_INDUCTOR -->|\"OVLO divider\"| AON_EFUSE_OVLO_TOP --> AON_EFUSE_OVLO_BOTTOM",
        "  AON_EFUSE --> AON_EFUSE_OUTPUT_CAP",
        "  AON_EFUSE -->|\"PG pull-up source\"| AON_PG_PULLUP --> AON_BUCK",
        "  AON_PG_PULLUP -->|\"AON_PG_N to MR_N\"| SAFE_SUPERVISOR",
        "  AON_EFUSE -->|\"POR pull-up\"| SAFE_POR_PULLUP --> SAFE_SUPERVISOR",
        "  SAFE_SUPERVISOR -->|\"delayed POR_N enables main\"| MAIN_BUCK",
        "  NVDC_CHARGER -->|\"SYS\"| MAIN_BUCK --> MAIN_INDUCTOR -->|\"MAIN_RAW_3V3\"| MAIN_EFUSE -->|\"3V3_MAIN\"| S3",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| MAIN_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| MAIN_HF_INPUT_CAP",
        "  MAIN_INDUCTOR -->|\"feedback\"| MAIN_FB_TOP --> MAIN_FB_BOTTOM",
        "  MAIN_INDUCTOR -->|\"feed-forward\"| MAIN_FF_CAP",
        "  MAIN_INDUCTOR -->|\"local output bank\"| MAIN_OUTPUT_CAP0",
        "  MAIN_INDUCTOR -->|\"local output bank\"| MAIN_OUTPUT_CAP1",
        "  MAIN_EFUSE -->|\"ILM\"| MAIN_EFUSE_RILM",
        "  MAIN_EFUSE -->|\"dVdt\"| MAIN_EFUSE_DVDT_CAP",
        "  MAIN_EFUSE -->|\"ITIMER\"| MAIN_EFUSE_ITIMER_CAP",
        "  MAIN_INDUCTOR -->|\"OVLO divider\"| MAIN_EFUSE_OVLO_TOP --> MAIN_EFUSE_OVLO_BOTTOM",
        "  MAIN_EFUSE -->|\"PGTH divider\"| MAIN_EFUSE_PG_TOP --> MAIN_EFUSE_PG_BOTTOM",
        "  MAIN_EFUSE --> MAIN_EFUSE_OUTPUT_CAP",
        "  MAIN_BUCK -->|\"100-kOhm EN fail-low\"| MAIN_EN_PULLDOWN",
        "  MAIN_EFUSE -->|\"protected PG to fault aggregate\"| SLOW_IO",
        "  MAIN_EFUSE -->|\"POWER_FAULT_N pull-up source\"| POWER_FAULT_PULLUP --> SLOW_IO",
        "  MAIN_EFUSE -->|\"3V3_MAIN: VCCI/VCCP\"| SLOW_IO",
        "  MAIN_EFUSE --> SLOW_IO_VCCI_BYPASS --> SLOW_IO",
        "  MAIN_EFUSE --> SLOW_IO_VCCP_BYPASS --> SLOW_IO",
        "  MAIN_EFUSE --> SLOW_IO_BULK_CAP --> SLOW_IO",
        "  MAIN_EFUSE --> SLOW_IO_RESET_PULLUP --> SLOW_IO_RESET --> SLOW_IO",
        "  MAIN_EFUSE -->|\"3V3_MAIN\"| C5",
        "  MAIN_EFUSE -->|\"3V3_MAIN\"| RP",
        "  MAIN_EFUSE --> NRF_POWER_SWITCH",
        "  MAIN_EFUSE --> CC_POWER_SWITCH",
        "  MAIN_EFUSE --> SD_POWER_SWITCH",
        "  MAIN_EFUSE --> CODEC_POWER_SWITCH",
        "  MAIN_EFUSE --> RECEIVER_POWER_SWITCH",
        "  NVDC_CHARGER -->|\"SYS\"| VOICE_BUCK --> VOICE_INDUCTOR -->|\"VVOICE_RAW_4V\"| VOICE_EFUSE -->|\"protected 4.0 V\"| VOICE",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| VOICE_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| VOICE_HF_INPUT_CAP",
        "  VOICE_INDUCTOR -->|\"feedback\"| VOICE_FB_TOP --> VOICE_FB_BOTTOM",
        "  VOICE_INDUCTOR -->|\"feed-forward\"| VOICE_FF_CAP",
        "  VOICE_INDUCTOR -->|\"local output bank\"| VOICE_OUTPUT_CAP0",
        "  VOICE_INDUCTOR -->|\"local output bank\"| VOICE_OUTPUT_CAP1",
        "  VOICE_EFUSE -->|\"ILM\"| VOICE_EFUSE_RILM",
        "  VOICE_EFUSE -->|\"dVdt\"| VOICE_EFUSE_DVDT_CAP",
        "  VOICE_EFUSE -->|\"ITIMER\"| VOICE_EFUSE_ITIMER_CAP",
        "  VOICE_INDUCTOR -->|\"OVLO divider\"| VOICE_EFUSE_OVLO_TOP --> VOICE_EFUSE_OVLO_BOTTOM",
        "  VOICE_EFUSE -->|\"PGTH divider\"| VOICE_EFUSE_PG_TOP --> VOICE_EFUSE_PG_BOTTOM",
        "  VOICE_EFUSE --> VOICE_EFUSE_OUTPUT_CAP",
        "  VOICE_BUCK -->|\"EN fail-low\"| VOICE_EN_PULLDOWN",
        "  MAIN_EFUSE -->|\"PG pull-up\"| VOICE_PG_PULLUP --> VOICE_EFUSE",
        "  SAFE_GATE_B -->|\"EN\"| VOICE_PG_BASE_RES --> VOICE_PG_QUALIFIER",
        "  VOICE_EFUSE -->|\"protected PG\"| VOICE_PG_QUALIFIER -->|\"qualified open collector\"| SLOW_IO",
        "  NVDC_CHARGER -->|\"SYS\"| EXT_BUCK --> EXT_INDUCTOR",
        "  EXT_INDUCTOR --> EXT_EFUSE -->|\"protected U214 5.0 V\"| U214_CONNECTOR --> U214",
        "  EXT_INDUCTOR --> UNIT_EFUSE -->|\"protected native-Unit 5.0 V\"| UNIT_CONNECTOR",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| EXT_BUCK_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| EXT_BUCK_HF_INPUT_CAP",
        "  EXT_INDUCTOR -->|\"feedback\"| EXT_BUCK_FB_TOP --> EXT_BUCK_FB_BOTTOM",
        "  EXT_INDUCTOR -->|\"feed-forward\"| EXT_BUCK_FF_CAP",
        "  EXT_INDUCTOR -->|\"local output bank\"| EXT_BUCK_OUTPUT_CAP0",
        "  EXT_INDUCTOR -->|\"local output bank\"| EXT_BUCK_OUTPUT_CAP1",
        "  EXT_BUCK -->|\"EN fail-low\"| EXT_EN_PULLDOWN",
        "  MAIN_EFUSE -->|\"PG pull-up\"| EXT_PG_PULLUP --> EXT_BUCK",
        "  SAFE_GATE_B -->|\"EN\"| EXT_PG_BASE_RES --> EXT_PG_QUALIFIER",
        "  EXT_BUCK -->|\"PG\"| EXT_PG_QUALIFIER -->|\"qualified open collector\"| SLOW_IO",
        "  EXT_EFUSE -->|\"ILM\"| EXT_RILM",
        "  EXT_EFUSE -->|\"dVdt\"| EXT_DVDT_CAP",
        "  EXT_EFUSE -->|\"ITIMER\"| EXT_ITIMER_CAP",
        "  EXT_INDUCTOR -->|\"OVLO divider\"| EXT_OVLO_TOP --> EXT_OVLO_BOTTOM",
        "  EXT_INDUCTOR --> EXT_INPUT_CAP",
        "  EXT_EFUSE --> EXT_OUTPUT_CAP",
        "  EXT_EFUSE --> EXT_BLEEDER",
        "  NRF_POWER_SWITCH -->|\"switched 3.3 V\"| NRF0",
        "  NRF_POWER_SWITCH --> NRF0_HOST_BUFFER",
        "  NRF_POWER_SWITCH --> NRF0_RETURN_BUFFER",
        "  NRF_POWER_SWITCH -->|\"switched 3.3 V\"| NRF1",
        "  NRF_POWER_SWITCH --> NRF1_HOST_BUFFER",
        "  NRF_POWER_SWITCH --> NRF1_RETURN_BUFFER",
        "  NRF_POWER_SWITCH -->|\"switched 3.3 V\"| NRF2",
        "  NRF_POWER_SWITCH --> NRF2_HOST_BUFFER",
        "  NRF_POWER_SWITCH --> NRF2_RETURN_BUFFER",
        "  CC_POWER_SWITCH -->|\"switched 3.3 V\"| CC",
        "  CC_POWER_SWITCH --> CC_HOST_BUFFER",
        "  CC_POWER_SWITCH --> CC_RETURN_BUFFER",
        "  CC_POWER_SWITCH --> CC_BAND_BUFFER",
        "  CC_POWER_SWITCH --> CC_SWITCH_A",
        "  CC_POWER_SWITCH --> CC_SWITCH_B",
        "  RP -->|\"SCLK / SI / CSN\"| CC_HOST_BUFFER --> CC",
        "  CC -->|\"SO / GDO0 / GDO2\"| CC_RETURN_BUFFER --> RP",
        "  SLOW_IO -->|\"P03/P04; rail-off only\"| CC_BAND_BUFFER",
        "  CC_BAND_BUFFER -->|\"same V1/V2 to both ends\"| CC_SWITCH_A",
        "  CC_BAND_BUFFER -->|\"same V1/V2 to both ends\"| CC_SWITCH_B",
        "  CC --> CC_RF_P_DC_BLOCK --> CC_BALUN",
        "  CC --> CC_RF_N_DC_BLOCK --> CC_BALUN",
        "  CC_RF_P_DC_BLOCK --> CC_RF_DIFF_CAP",
        "  CC_RF_N_DC_BLOCK --> CC_RF_DIFF_CAP",
        "  CC_BALUN --> CC_MATCH_L3N3 --> CC_MATCH_L6N8 --> CC_SWITCH_A",
        "  CC_MATCH_L3N3 -->|\"shunt\"| CC_MATCH_C1P2",
        "  CC_SWITCH_A -->|\"RF1 = 315 MHz\"| CC_315_L10_IN --> CC_315_L10_OUT --> CC_SWITCH_B",
        "  CC_315_L10_IN -->|\"shunt trap\"| CC_315_SHUNT_L3N6 --> CC_315_SHUNT_C8P",
        "  CC_SWITCH_A -->|\"RF2 = 433 MHz\"| CC_433_L15 --> CC_SWITCH_B",
        "  CC_SWITCH_A -->|\"433 input shunt\"| CC_433_SHUNT_C10P",
        "  CC_433_L15 -->|\"433 output shunt\"| CC_433_SHUNT_C6P2",
        "  CC_SWITCH_A -->|\"RF3 = 868/915 MHz\"| CC_868_915_L10 --> CC_SWITCH_B",
        "  CC_SWITCH_B --> CC_OUTPUT_L2N2 --> CC_RF_ESD --> CC_EXTERNAL_SMA",
        "  CC_OUTPUT_L2N2 -->|\"0.47-pF actual-TX sample\"| CC_DETECTOR_TAP_CAP --> DET_CC",
        "  VOICE -->|\"short controlled 50-Ohm line\"| VOICE_EXTERNAL_SMA",
        "  VOICE -->|\"24-V shunt at external boundary\"| VOICE_RF_ESD",
        "  VOICE -->|\"5.1-kOhm actual-TX sample\"| VOICE_DETECTOR_SERIES_ATTENUATOR --> DET_VOICE",
        "  DET_VOICE -->|\"52.3-Ohm RFIN shunt\"| VOICE_DETECTOR_MATCH",
        "  VOICE_DETECTOR_FILTER --> DET_VOICE",
        "  VOICE_DETECTOR_BYPASS --> DET_VOICE",
        "  SAFE_GATE_B --> VOICE_EVIDENCE_HOLD_DIODE --> VOICE_EVIDENCE_HOLD_CAP",
        "  VOICE_EVIDENCE_HOLD_DIODE --> VOICE_EVIDENCE_HOLD_PULLDOWN",
        "  VOICE_EVIDENCE_HOLD_DIODE --> DET_VOICE",
        "  MAIN_EFUSE --> SD_POWER_SWITCH -->|\"switched 3.3 V\"| SD",
        "  MAIN_EFUSE -->|\"local input bypass\"| SD_POWER_INPUT_CAP",
        "  SLOW_IO -->|\"P20 session enable\"| SD_POWER_SWITCH",
        "  SD_ON_PULLDOWN -->|\"reset off\"| SD_POWER_SWITCH",
        "  SD_POWER_SWITCH --> SD_POWER_BULK_CAP",
        "  SD_POWER_SWITCH --> SD_POWER_HF_CAP",
        "  SD_POWER_SWITCH --> SD_HOST_BUFFER_BYPASS",
        "  SD_POWER_SWITCH --> SD_MISO_BUFFER_BYPASS",
        "  SD_POWER_SWITCH -->|\"VCC with Ioff\"| SD_HOST_BUFFER",
        "  SD_POWER_SWITCH -->|\"VCC with Ioff\"| SD_MISO_BUFFER",
        "  SD_HOST_SCK_PULLDOWN -->|\"reset low\"| S3",
        "  SD_HOST_D0_PULLDOWN -->|\"reset low\"| S3",
        "  MAIN_EFUSE --> SD_HOST_D1_PULLUP --> S3",
        "  MAIN_EFUSE --> SD_HOST_CS_PULLUP --> S3",
        "  MAIN_EFUSE --> LCD_HOST_CS_PULLUP --> S3",
        "  S3 -->|\"shared SCK/CMD + card CS\"| SD_HOST_BUFFER",
        "  SD_HOST_BUFFER -->|\"SCK\"| SD_SCK_SERIES --> SD",
        "  SD_HOST_BUFFER -->|\"CMD\"| SD_CMD_SERIES --> SD",
        "  SD_HOST_BUFFER -->|\"CS\"| SD_CS_SERIES --> SD",
        "  SD -->|\"DAT0 only while CS low\"| SD_MISO_BUFFER --> SD_MISO_SERIES --> S3",
        "  S3 -->|\"SD_CS_N output enable\"| SD_MISO_BUFFER",
        "  SD_POWER_SWITCH --> SD_CARD_CMD_PULLUP --> SD",
        "  SD_POWER_SWITCH --> SD_CARD_DAT0_PULLUP --> SD",
        "  SD_POWER_SWITCH --> SD_CARD_DAT1_PULLUP --> SD",
        "  SD_POWER_SWITCH --> SD_CARD_DAT2_PULLUP --> SD",
        "  SD_POWER_SWITCH --> SD_CARD_DAT3_PULLUP --> SD",
        "  SD_ESD_A -.->|\"CLK/CMD/DAT0/DAT3 shunt clamps\"| SD",
        "  SD_ESD_B -.->|\"DAT1/DAT2/VDD/detect shunt clamps\"| SD",
        "  SD -->|\"normally-open detect\"| SD_DETECT_SERIES --> SLOW_IO",
        "  MAIN_EFUSE --> SD_DETECT_PULLUP --> SLOW_IO",
        "  SLOW_IO --> SD_DETECT_CAP",
        "  CODEC_POWER_SWITCH --> CODEC",
        "  RECEIVER_POWER_SWITCH --> RECEIVER",
        f"  S3 <-->|\"{sdio_label}: S3 {contacts('s3', ('S3_C5_',))} ↔ C5 {contacts('c5', ('S3_C5_',))}\"| C5",
        f"  S3 <-->|\"SPI3+alert: S3 {contacts('s3', ('S3_RP_', 'RP_ALERT_'))} ↔ RP {contacts('rp', ('S3_RP_', 'RP_ALERT_'))}\"| RP",
        f"  S3 <-->|\"I²C0+INT: {contacts('s3', ('SYS_I2C_', 'SLOW_IO_'))}\"| SLOW_IO",
        "  SAFE_LATCH -->|\"Q polarity preserved\"| SLOW_IO_FAULT_SENSE_ISO --> SLOW_IO",
        "  AON_EFUSE --> SLOW_IO_FAULT_SENSE_ISO_BYPASS --> SLOW_IO_FAULT_SENSE_ISO",
        "  MAIN_EFUSE --> SLOW_IO_FAULT_SENSE_PULLUP --> SLOW_IO",
        "  EVIDENCE_CMP_A -->|\"active-low polarity preserved\"| SLOW_IO_S3_EVIDENCE_ISO --> SLOW_IO",
        "  AON_EFUSE --> SLOW_IO_S3_EVIDENCE_ISO_BYPASS --> SLOW_IO_S3_EVIDENCE_ISO",
        "  MAIN_EFUSE --> SLOW_IO_S3_EVIDENCE_PULLUP --> SLOW_IO",
        f"  S3 -->|\"QSPI/touch/PWM: {contacts('s3', ('DISPLAY_SD_', 'LCD_'))}\"| DISPLAY_CONNECTOR",
        "  DISPLAY_CONNECTOR <-->|\"exact 2-mm 40-contact DF40 mate\"| DISPLAY_ADAPTER_PLUG",
        "  DISPLAY_ADAPTER_PLUG <-->|\"one-to-one adapter copper\"| DISPLAY_PANEL_CONNECTOR",
        "  DISPLAY_PANEL_CONNECTOR <-->|\"dual-contact 40-position ZIF; received-tail fit H5\"| DISPLAY",
        "  DISPLAY -->|\"integrated exact COG\"| DISPLAY_TOUCH_CONTROLLER",
        "  DISPLAY_TOUCH_CONTROLLER -->|\"TP_INT low on touch\"| TOUCH_IRQ_RAW",
        "  TOUCH_IRQ_PULLUP -->|\"10 kOhm to 3V3_MAIN\"| TOUCH_IRQ_RAW",
        "  TOUCH_IRQ_RAW --> TOUCH_IRQ_BUFFER -->|\"open-drain SYS_INT_N\"| S3",
        "  SLOW_IO -->|\"P06/P07 reset release\"| DISPLAY_CONNECTOR",
        "  S3 <-->|\"SYS I²C0 + shared wired-low IRQ\"| UI_MATRIX_IO",
        "  UI_MATRIX_IO_BYPASS --> UI_MATRIX_IO",
        "  UI_MATRIX_IO -.->|\"P00..P07 front shunt protection\"| UI_MATRIX_ESD",
        "  UI_DPAD_UP -->|\"direct P00\"| UI_MATRIX_IO",
        "  UI_DPAD_DOWN -->|\"direct P01\"| UI_MATRIX_IO",
        "  UI_DPAD_LEFT -->|\"direct P02\"| UI_MATRIX_IO",
        "  UI_DPAD_RIGHT -->|\"direct P03\"| UI_MATRIX_IO",
        "  UI_DPAD_OK -->|\"direct P04\"| UI_MATRIX_IO",
        "  UI_SWITCH_BACK -->|\"direct P05\"| UI_MATRIX_IO",
        "  UI_SWITCH_OPT -->|\"direct P06\"| UI_MATRIX_IO",
        "  UI_SWITCH_F3 -->|\"direct P07\"| UI_MATRIX_IO",
        "  UI_SWITCH_F1 -->|\"direct P10\"| UI_MATRIX_IO",
        "  UI_SWITCH_F2 -->|\"direct P11\"| UI_MATRIX_IO",
        "  ENCODER -->|\"push P12 across M1\"| UI_MATRIX_IO",
        "  UI_SWITCH_F4 -->|\"direct P13\"| UI_MATRIX_IO",
        "  UI_SWITCH_F5 -->|\"direct P14\"| UI_MATRIX_IO",
        "  UI_SWITCH_F6 -->|\"direct P15\"| UI_MATRIX_IO",
        "  UI_SWITCH_F7 -->|\"direct P16\"| UI_MATRIX_IO",
        "  UI_SWITCH_F8 -->|\"direct P17\"| UI_MATRIX_IO",
        "  FRONT_FUNCTION_ESD -.->|\"F1/F2/F4..F8 shunt protection\"| UI_MATRIX_IO",
        "  REAR_CONTROL_ESD -.->|\"encoder-push shunt protection\"| UI_MATRIX_IO",
        "  UI_INPUT_UP_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_DOWN_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_LEFT_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_RIGHT_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_OK_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_BACK_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_OPT_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F1_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F2_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F3_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F4_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F5_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F6_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F7_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_F8_PULLUP --> UI_MATRIX_IO",
        "  UI_INPUT_ENCODER_PULLUP --> UI_MATRIX_IO",
        "  ENCODER_A_PULLUP --> ENCODER",
        "  ENCODER_B_PULLUP --> ENCODER",
        "  ENCODER_KNOB -->|\"6x4.5-mm D-shaft interference fit\"| ENCODER",
        "  ENCODER -->|\"GPIO39/GPIO47 PCNT0 quadrature\"| S3",
        "  DISPLAY_RESET_PULLDOWN -->|\"RESX default low\"| DISPLAY_CONNECTOR",
        "  TOUCH_RESET_PULLDOWN -->|\"TP_RESXP default low\"| DISPLAY_CONNECTOR",
        "  MAIN_EFUSE -->|\"protected 3.3 V logic\"| DISPLAY_LOGIC_BULK_CAP --> DISPLAY_CONNECTOR",
        "  MAIN_EFUSE --> DISPLAY_LOGIC_HF_CAP --> DISPLAY_CONNECTOR",
        "  MAIN_EFUSE -->|\"LEDA branch\"| BACKLIGHT_EFUSE --> DISPLAY_CONNECTOR",
        "  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_ILIM",
        "  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_INPUT_CAP",
        "  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_OUTPUT_BULK",
        "  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_OUTPUT_HF",
        "  BACKLIGHT_FAULT_PULLUP --> BACKLIGHT_EFUSE",
        "  DISPLAY_CONNECTOR -->|\"3 x LEDK\"| BACKLIGHT_SERIES_RESISTOR --> BACKLIGHT_MOSFET",
        "  S3 -->|\"GPIO40 PWM\"| BACKLIGHT_GATE_SERIES --> BACKLIGHT_MOSFET",
        "  BACKLIGHT_GATE_PULLDOWN -->|\"reset off\"| BACKLIGHT_MOSFET",
        f"  S3 -.->|\"logical scheduler contract; no electrical bypass: {contacts('s3', ('DISPLAY_SD_', 'SD_SPI_'))}\"| SD",
        f"  S3 <-->|\"I²C0 host side: {contacts('s3', ('SYS_I2C_',))}\"| CODEC_I2C_ISO",
        "  CODEC_I2C_ISO <-->|\"switched local I²C; 0x19\"| CODEC",
        "  S3 -->|\"I²S0 outputs: GPIO15,GPIO16,GPIO17\"| CODEC_I2S_BCLK_ISO",
        "  S3 --> CODEC_I2S_WS_ISO --> CODEC",
        "  S3 --> CODEC_I2S_DOUT_ISO --> CODEC",
        "  CODEC --> CODEC_I2S_DIN_ISO -->|\"GPIO0 after boot\"| S3",
        "  CODEC_SUPERVISOR -->|\"CODEC_READY\"| CODEC_I2S_DIN_BOOT_GATE",
        "  S3 -->|\"GPIO6 AUDIO_ARM; reset-low\"| CODEC_I2S_DIN_BOOT_GATE",
        "  CODEC_I2S_DIN_BOOT_GATE -->|\"output enable\"| CODEC_I2S_DIN_ISO",
        "  S3 <-->|\"I²C0 host side\"| RECEIVER_I2C_ISO",
        "  RECEIVER_I2C_ISO <-->|\"switched local I²C\"| RECEIVER",
        "  RECEIVER_SUPERVISOR -->|\"reset + 200-ms isolation release\"| RECEIVER_I2C_ISO",
        "  RECEIVER --> RECEIVER_IRQ_ISO --> SLOW_IO",
        f"  S3 <-->|\"profile port: {contacts('s3', ('UNIT_',))}\"| UNIT_CONNECTOR",
        f"  C5 <-->|\"RMT RX0/power: {contacts('c5', ('IR_',))}\"| IR_DEMOD",
        "  C5 <-->|\"RMT RX1/power\"| IR_CARRIER",
        f"  RP -->|\"PIO0 SM0 outputs: {contacts('rp', ('NRF0_',))}\"| NRF0_HOST_BUFFER --> NRF0",
        "  NRF0 -->|\"MISO + IRQ\"| NRF0_RETURN_BUFFER --> RP",
        f"  RP -->|\"PIO0 SM1 outputs: {contacts('rp', ('NRF1_',))}\"| NRF1_HOST_BUFFER --> NRF1",
        "  NRF1 -->|\"MISO + IRQ\"| NRF1_RETURN_BUFFER --> RP",
        f"  RP -->|\"PIO0 SM2 outputs: {contacts('rp', ('NRF2_',))}\"| NRF2_HOST_BUFFER --> NRF2",
        "  NRF2 -->|\"MISO + IRQ\"| NRF2_RETURN_BUFFER --> RP",
        f"  RP <-->|\"PIO0 SM3 + GDO/power: {contacts('rp', ('CC_',))}\"| CC",
        f"  RP <-->|\"UART0/PTT request: {contacts('rp', ('VOICE_', 'PTT_'))}\"| VOICE",
        "  PTT_PULLUP -->|\"10 kOhm to 3V3_MAIN\"| PTT_RAW",
        "  PTT_FILTER_CAP -->|\"100 nF to power ground\"| PTT_RAW",
        "  PTT_SWITCH -->|\"NO contact to power ground\"| PTT_RAW",
        "  PTT_RAW --> ENCODER_PTT_ESD",
        "  PTT_RAW -->|\"direct GPIO21 through 1 kOhm; never in UI expander\"| PTT_SERIES --> RP",
        "  ENCODER --> ENCODER_PTT_ESD",
        f"  RP -->|\"PIO1/UART1 outputs: {contacts('rp', ('U214_HOST_',))}\"| U214_HOST_BUFFER_A --> U214_CONNECTOR --> U214",
        "  RP --> U214_HOST_BUFFER_B --> U214_CONNECTOR",
        "  U214 --> U214_CONNECTOR -->|\"BUSY/IRQ/GPS-TX/MISO\"| U214_RETURN_BUFFER --> RP",
        "  RP <-->|\"I²C0\"| U214_I2C_ISO",
        "  U214_I2C_ISO <-->|\"isolated external I²C\"| U214_CONNECTOR",
        "  U214_CONNECTOR <-->|\"contacts 1..14\"| U214",
        "  U214_ESD_A -.->|\"I²C/RST/GPS-RX shunt protection\"| U214_CONNECTOR",
        "  U214_ESD_B -.->|\"SCK/MOSI/NSS/BUSY shunt protection\"| U214_CONNECTOR",
        "  U214_ESD_C -.->|\"IRQ/GPS-TX/MISO shunt protection\"| U214_CONNECTOR",
        "  S3 <-->|\"GPIO7/GPIO8 profile signals\"| UNIT_SIGNAL_ISO <-->|\"isolated I²C/UART/GPIO\"| UNIT_CONNECTOR",
        "  UNIT_ESD -.->|\"two signal shunt clamps\"| UNIT_CONNECTOR",
        "  SLOW_IO -->|\"P17/P05 independent requests\"| EXT_REQUEST_OR --> SAFE_GATE_B",
        "  SAFE_GATE_B --> EXT_BRANCH_GATE",
        "  EXT_BRANCH_GATE --> EXT_EFUSE",
        "  EXT_BRANCH_GATE --> UNIT_EFUSE",
        "  EXT_EFUSE --> U214_SUPERVISOR --> U214_HOST_BUFFER_A",
        "  U214_SUPERVISOR --> U214_I2C_ISO",
        "  UNIT_EFUSE --> UNIT_SUPERVISOR --> UNIT_SIGNAL_ISO",
        "  RECEIVER --> SI_AUDIO_L_COUPLING --> SI_AUDIO_L_SUM --> AUDIO_RX_MUX",
        "  RECEIVER --> SI_AUDIO_R_COUPLING --> SI_AUDIO_R_SUM --> AUDIO_RX_MUX",
        "  RECEIVER_CLOCK --> RECEIVER",
        "  VOICE -->|\"AFOUT\"| VOICE_AUDIO_ISO --> VOICE_RX_COUPLING --> AUDIO_RX_MUX",
        "  SLOW_IO -->|\"P27 source request\"| AUDIO_RX_MUX",
        "  AUDIO_RX_MUX -->|\"analog bypass\"| AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_RX_MUX --> AUDIO_CAPTURE_RX_COUPLING --> AUDIO_CAPTURE_SELECTOR",
        "  MICROPHONE --> HEADSET_MIC_SELECTOR",
        "  HEADPHONE_JACK -->|\"CTIA sleeve microphone\"| HEADSET_MIC_SELECTOR",
        "  HEADSET_MIC_BIAS_RES --> HEADPHONE_JACK",
        "  SLOW_IO -->|\"P02 plug state / inserted-only override\"| HEADSET_MIC_SELECTOR",
        "  HEADSET_MIC_SELECTOR --> AUDIO_CAPTURE_MIC_COUPLING --> AUDIO_CAPTURE_SELECTOR",
        "  SLOW_IO -->|\"P00 RX/microphone capture select\"| AUDIO_CAPTURE_SELECTOR",
        "  AUDIO_CAPTURE_SELECTOR --> AUDIO_CAPTURE_INPUT_COUPLING --> AUDIO_CAPTURE_BUFFER --> CODEC_ADC_P_COUPLING --> CODEC",
        "  CODEC -->|\"OUTP/OUTN\"| AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_SPEAKER_SELECTOR --> SPEAKER_INPUT_P_COUPLING --> SPEAKER_AMP",
        "  AUDIO_SPEAKER_SELECTOR --> SPEAKER_INPUT_N_COUPLING --> SPEAKER_AMP",
        "  SPEAKER_AMP --> SPEAKER_OUTPUT_BEAD_P --> SPEAKER",
        "  SPEAKER_AMP --> SPEAKER_OUTPUT_BEAD_N --> SPEAKER",
        "  SLOW_IO -->|\"P01 reset-off speaker enable\"| SPEAKER_AMP",
        "  CODEC --> HEADPHONE_L_COUPLING0 --> HEADPHONE_JACK",
        "  CODEC --> HEADPHONE_R_COUPLING0 --> HEADPHONE_JACK",
        "  HEADPHONE_JACK --> HEADPHONE_ESD",
        "  HEADPHONE_JACK -->|\"P02 insertion state\"| SLOW_IO",
        "  CODEC --> CODEC_TX_COUPLING --> CODEC_TX_ATTEN_TOP --> AUDIO_TX_SELECTOR",
        "  HEADSET_MIC_SELECTOR --> MIC_TX_COUPLING --> AUDIO_TX_SELECTOR",
        "  AUDIO_TX_SELECTOR --> VOICE_AUDIO_ISO -->|\"MIC_IN\"| VOICE",
        "  SLOW_IO -->|\"P11/P12 requests\"| AUDIO_SAFE_GATE",
        "  S3 -->|\"GPIO6 AUDIO_ARM\"| AUDIO_SAFE_GATE",
        "  AUDIO_SAFE_GATE --> AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_SAFE_GATE --> AUDIO_TX_SELECTOR",
        "  CODEC_POWER_SWITCH --> CODEC_SUPERVISOR --> CODEC_I2C_ISO",
        "  CODEC_SUPERVISOR --> CODEC_I2S_BCLK_ISO",
        "  VOICE_SUPERVISOR --> VOICE_IO_POWER_SWITCH --> VOICE_PTT_ISO",
        "  VOICE_IO_POWER_SWITCH --> VOICE_UART_TX_ISO",
        "  VOICE_IO_POWER_SWITCH --> VOICE_AUDIO_ISO",
        "  SLOW_IO -->|\"P14 low-or-open power select\"| VOICE_HL_DRIVER --> VOICE",
        "  RECEIVER_FMSW_EXTERNAL_SMA --> RECEIVER_FMI_ESD",
        "  RECEIVER_FMSW_EXTERNAL_SMA --> RECEIVER_FMI_MATCH_INDUCTOR --> RECEIVER_FMI_COUPLING_CAP -->|\"FMI contact 6\"| RECEIVER",
        "  RECEIVER_AMLW_EXTERNAL_SMA --> RECEIVER_AMI_ESD",
        "  RECEIVER_AMLW_EXTERNAL_SMA --> RECEIVER_AMI_COUPLING_CAP -->|\"AMI contact 8\"| RECEIVER",
        "  RUN_LOOP_PULLUP -->|\"10 kOhm to AON_SAFE_3V3\"| RUN_LOOP",
        "  RUN_LOOP_FILTER -->|\"100 nF to safety ground\"| RUN_LOOP",
        "  POWER_COMMAND_SWITCH -->|\"RUN throw\"| RUN_LOOP",
        "  RUN_LOOP --> SAFETY_CONTROL_ESD",
        "  RUN_LOOP --> SAFE_CONDITIONER --> SAFE_LATCH",
        "  SAFE_SUPERVISOR --> SAFE_LATCH",
        "  SAFETY_CONTROLLER --> SAFETY_WATCHDOG --> SAFE_LATCH",
        "  SAFETY_CONTROLLER --> SAFETY_FAULT_REQUEST_ISO --> SAFE_LATCH",
        "  SAFETY_CONTROLLER --> POWER_ZONE_NTC",
        "  SAFETY_CONTROLLER --> RF_ZONE_NTC",
        "  SAFETY_CONTROLLER --> UI_ZONE_NTC",
        "  SAFE_LATCH -->|\"RUN_PERMIT\"| SAFE_RESET_BUFFER",
        "  SAFE_RESET_BUFFER -->|\"CHIP_PU\"| C5",
        "  SAFE_RESET_BUFFER -->|\"RUN\"| RP",
        "  SAFETY_CONTROLLER -->|\"bounded fault reset\"| SAFE_CONDITIONER -->|\"CHIP_PU\"| S3",
        "  SAFE_LATCH --> SAFE_GATE_A",
        "  SAFE_LATCH --> SAFE_GATE_B",
        "  SAFE_LATCH --> SAFE_PTT_OR",
        "  SAFE_LATCH --> FAULT_LED_SERIES --> FAULT_LED",
        "  RP -->|\"3×CE + nRF rail requests\"| SAFE_GATE_A",
        "  RP -->|\"CC rail request\"| SAFE_GATE_B",
        "  C5 -->|\"IR carrier request\"| SAFE_GATE_B",
        "  SLOW_IO -->|\"voice/accessory rail requests\"| SAFE_GATE_B",
        "  RP -->|\"PTT request\"| SAFE_PTT_OR --> VOICE_PTT_ISO --> VOICE",
        "  SAFE_GATE_A -->|\"CE0\"| NRF0_HOST_BUFFER",
        "  SAFE_GATE_A -->|\"CE1\"| NRF1_HOST_BUFFER",
        "  SAFE_GATE_A -->|\"CE2\"| NRF2_HOST_BUFFER",
        "  SAFE_GATE_A --> NRF_POWER_SWITCH",
        "  SAFE_GATE_A --> NRF_EVIDENCE_HOLD_DIODE --> NRF_EVIDENCE_HOLD_CAP",
        "  NRF_EVIDENCE_HOLD_DIODE --> NRF_EVIDENCE_HOLD_PULLDOWN",
        "  NRF_EVIDENCE_HOLD_DIODE --> DET_NRF0",
        "  NRF_EVIDENCE_HOLD_DIODE --> DET_NRF1",
        "  NRF_EVIDENCE_HOLD_DIODE --> DET_NRF2",
        "  SAFE_GATE_B --> CC_POWER_SWITCH",
        "  SAFE_GATE_B --> VOICE_BUCK",
        "  SAFE_GATE_B --> IR_EMITTER",
        "  SAFE_GATE_B --> EXT_BUCK",
        "  S3 -->|\"ANT receptacle\"| S3_RF_JUMPER -->|\"30-mm UMCC Gen1\"| S3_RF_BOARD_CONNECTOR --> S3_RF_COUPLER -->|\"dedicated RP-SMA boundary\"| S3_EXTERNAL_RP_SMA",
        "  S3_RF_COUPLER -->|\"-20-dB forward sample\"| S3_DETECTOR_INPUT_CAP --> DET_S3 --> EVIDENCE_CMP_A",
        "  S3_RF_COUPLER --> S3_RF_COUPLER_TERMINATION",
        "  S3_DETECTOR_FEEDBACK_RES --> DET_S3",
        "  S3_DETECTOR_GROUND_RES --> DET_S3",
        "  S3_DETECTOR_OUTPUT_CAP --> DET_S3",
        "  S3_DETECTOR_BYPASS --> DET_S3",
        "  C5 -->|\"ANT1 receptacle\"| C5_RF_JUMPER -->|\"30-mm UMCC Gen1\"| C5_RF_BOARD_CONNECTOR --> C5_RF_COUPLER -->|\"dedicated RP-SMA boundary\"| C5_EXTERNAL_RP_SMA",
        "  C5_RF_COUPLER -->|\"-20/-13-dB forward sample\"| C5_DETECTOR_INPUT_CAP --> DET_C5 --> EVIDENCE_CMP_A",
        "  C5_RF_COUPLER --> C5_RF_COUPLER_TERMINATION",
        "  C5_DETECTOR_FEEDBACK_RES --> DET_C5",
        "  C5_DETECTOR_GROUND_RES --> DET_C5",
        "  C5_DETECTOR_OUTPUT_CAP --> DET_C5",
        "  C5_DETECTOR_BYPASS --> DET_C5",
        "  NRF0 -->|\"qualified pigtail\"| NRF0_COUPLER -->|\"dedicated SMA\"| NRF0_EXTERNAL_SMA",
        "  NRF0_COUPLER -->|\"10-dB forward sample\"| DET_NRF0 --> EVIDENCE_CMP_B",
        "  NRF1 -->|\"qualified pigtail\"| NRF1_COUPLER -->|\"dedicated SMA\"| NRF1_EXTERNAL_SMA",
        "  NRF1_COUPLER -->|\"10-dB forward sample\"| DET_NRF1 --> EVIDENCE_CMP_B",
        "  NRF2 -->|\"qualified pigtail\"| NRF2_COUPLER -->|\"dedicated SMA\"| NRF2_EXTERNAL_SMA",
        "  NRF2_COUPLER -->|\"10-dB forward sample\"| DET_NRF2 --> EVIDENCE_CMP_B",
        "  DET_CC --> EVIDENCE_CMP_B",
        "  DET_VOICE --> EVIDENCE_CMP_VOICE",
        "  IR_EMITTER --> DET_IR --> EVIDENCE_CMP_A",
        "  EVIDENCE_CMP_A_BYPASS --> EVIDENCE_CMP_A",
        "  EVIDENCE_CMP_B_BYPASS --> EVIDENCE_CMP_B",
        "  EVIDENCE_CMP_VOICE_BYPASS --> EVIDENCE_CMP_VOICE",
        "  S3_EVIDENCE_THRESHOLD_TOP --> S3_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_A",
        "  S3_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_A",
        "  S3_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_A",
        "  C5_EVIDENCE_THRESHOLD_TOP --> C5_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_A",
        "  C5_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_A",
        "  C5_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_A",
        "  NRF0_EVIDENCE_THRESHOLD_TOP --> NRF0_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_B",
        "  NRF0_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_B",
        "  NRF0_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_B",
        "  NRF1_EVIDENCE_THRESHOLD_TOP --> NRF1_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_B",
        "  NRF1_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_B",
        "  NRF1_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_B",
        "  NRF2_EVIDENCE_THRESHOLD_TOP --> NRF2_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_B",
        "  NRF2_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_B",
        "  NRF2_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_B",
        "  CC_EVIDENCE_THRESHOLD_TOP --> CC_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_B",
        "  CC_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_B",
        "  CC_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_B",
        "  VOICE_EVIDENCE_THRESHOLD_TOP --> VOICE_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_VOICE",
        "  VOICE_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_VOICE",
        "  VOICE_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_VOICE",
        "  IR_EVIDENCE_THRESHOLD_TOP --> IR_EVIDENCE_THRESHOLD_BOTTOM --> EVIDENCE_CMP_A",
        "  IR_EVIDENCE_HYSTERESIS --> EVIDENCE_CMP_A",
        "  IR_EVIDENCE_OUTPUT_PULLUP --> EVIDENCE_CMP_A",
        "  EVIDENCE_CMP_A --> EVIDENCE_MASK",
        "  EVIDENCE_CMP_B --> EVIDENCE_MASK",
        "  EVIDENCE_CMP_VOICE --> EVIDENCE_MASK",
        "  U214_CONNECTOR --> U214_ESD_C --> EXT_EVIDENCE_INPUT_SERIES --> EXT_EVIDENCE_BUFFER",
        "  EXT_EVIDENCE_INPUT_PULLUP --> EXT_EVIDENCE_BUFFER",
        "  EXT_EVIDENCE_BUFFER_BYPASS --> EXT_EVIDENCE_BUFFER",
        "  EXT_EVIDENCE_OUTPUT_PULLUP --> EXT_EVIDENCE_BUFFER",
        "  EXT_EVIDENCE_BUFFER --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_BYPASS --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P11_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P12_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P13_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P14_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P15_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P16_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_MASK_P17_PULLDOWN --> EVIDENCE_MASK",
        "  EVIDENCE_CMP_A --> EVIDENCE_OR_0",
        "  EVIDENCE_CMP_A --> EVIDENCE_OR_3",
        "  EVIDENCE_CMP_B --> EVIDENCE_OR_1",
        "  EVIDENCE_CMP_B --> EVIDENCE_OR_2",
        "  EVIDENCE_CMP_VOICE --> EVIDENCE_OR_3",
        "  EXT_EVIDENCE_BUFFER --> EVIDENCE_OR_4",
        "  EVIDENCE_OR_0 --> ANY_TX_AON_PULLUP",
        "  EVIDENCE_OR_1 --> ANY_TX_AON_PULLUP",
        "  EVIDENCE_OR_2 --> ANY_TX_AON_PULLUP",
        "  EVIDENCE_OR_3 --> ANY_TX_AON_PULLUP",
        "  EVIDENCE_OR_4 --> ANY_TX_AON_PULLUP",
        "  EXT_TX_LED_SERIES --> EXT_TX_LED --> EXT_EVIDENCE_BUFFER",
        "  EVIDENCE_MASK <-->|\"private bit-banged I²C source mask\"| SAFETY_CONTROLLER",
        "  EVIDENCE_CMP_A -->|\"C5 RF evidence\"| EVIDENCE_MAIN_ISOLATOR",
        "  EVIDENCE_CMP_A -->|\"IR evidence\"| EVIDENCE_MAIN_ISOLATOR",
        "  ANY_TX_AON_PULLUP -->|\"AON aggregate\"| EVIDENCE_MAIN_ISOLATOR",
        "  EVIDENCE_MAIN_ISOLATOR_BYPASS --> EVIDENCE_MAIN_ISOLATOR",
        "  EVIDENCE_MAIN_ISOLATOR --> C5_EVIDENCE_MAIN_PULLUP -->|\"GPIO23 active-low\"| C5",
        "  EVIDENCE_MAIN_ISOLATOR --> IR_EVIDENCE_MAIN_PULLUP -->|\"GPIO24 active-low\"| C5",
        "  EVIDENCE_MAIN_ISOLATOR --> RP_ANY_TX_MAIN_PULLUP -->|\"GPIO22 active-low\"| RP",
        "```",
        "",
        "</details>",
        "",
        "## Сводный pin budget",
        "",
        "| Domain | Exact exposed boundary | Used | Reserved | Free | Total |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for instance in ("s3", "c5", "rp"):
        used, reserved, free, total = budget(instance)
        lines.append(
            f"| `{instance}` | `{devices[candidate['instances'][instance]]['mpn']}` | "
            f"{used} | {reserved} | {free} | {total} |"
        )
    slow = candidate["contact_accounting"]["slow_io"]
    lines += [
        f"| `slow_io` | `{devices[candidate['instances']['slow_io']]['mpn']}` | "
        f"{len(slow['used'])} | {len(slow['reserved'])} | {len(slow['free'])} | "
        f"{len(devices[candidate['instances']['slow_io']]['allocatable_contacts'])} |",
        "",
        "`RP=0 free` является текущим честным результатом после direct quiet-state",
        "controls `NRF_GROUP_PWR_EN` и `CC_PWR_EN`, а не ошибкой округления. Новый",
        "direct RP endpoint требует явного remap/review; service pins SWD/USB/RUN/",
        "BOOTSEL не входят в GPIO budget и остаются выведенными независимо.",
        "",
        "## Ещё абстрактные electrical endpoints",
        "",
        "Следующие функции имеют pin reservation, но не exact production MPN/circuit:",
        "",
    ]
    lines.extend(f"- `{endpoint}`" for endpoint in abstract_endpoints)
    lines += [
        "",
        "Эти строки блокируют final schematic/BOM, но не нарушают проверенную",
        "арифметику MCU pins. Их нельзя молча удалить либо объявить реализованными.",
        "",
        "## Exact pin/net tables",
        "",
        exact_details,
        "",
        "## Граница проведённого ревью",
        "",
        "Validator доказывает существование реально выведенных compute contacts,",
        "полный used/reserved/free accounting, straps, fixed mux, service paths,",
        "PIO/DMA capacity, independent radio/IPC resources и exact paper-level",
        "AON RUN/KILL, watchdog, thermal and physical-TX evidence circuit. Remaining peripheral MPN, branch power,",
        "signal/power integrity, RF taps/layout and HIL are later gates; этот atlas",
        "не разрешает PCB placement/routing, печать или закупку и не является frozen BOM.",
        "",
    ]
    projection_heading = lines.index("## Полная машинная проекция owners и pin groups")
    raw_open = lines.index("```text", projection_heading)
    raw_close = lines.index("```", raw_open + 1)
    raw_lines = lines[raw_open + 1 : raw_close]
    declared_node_ids = {
        node_id
        for line in raw_lines
        if (node_id := _mermaid_node_id(line)) is not None
    }
    required_node_ids = {instance.upper() for instance in candidate["instances"]}
    if missing := sorted(required_node_ids - declared_node_ids):
        raise ValueError(f"principled projection omits physical instances: {missing}")
    implicit_nodes: set[str] = set()
    for line in raw_lines:
        if not any(token in line for token in ("-->", "<-->", "-.->", "~~~")):
            continue
        unlabeled = re.sub(r'\|".*?"\|', "", line)
        referenced = set(
            re.findall(r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]*)(?![A-Z0-9_])", unlabeled)
        )
        implicit_nodes.update(referenced - declared_node_ids)
    if implicit_nodes:
        raise ValueError(
            f"principled projection contains implicit Mermaid nodes: {sorted(implicit_nodes)}"
        )
    details_open = lines.index("<details>", projection_heading)
    details_close = lines.index("</details>", details_open)
    lines[projection_heading:details_close + 1] = [
        "## Отрисовываемый атлас физических устройств",
        "",
        "Исчерпывающая one-device-per-node проекция разбита по функциональным",
        "доменам и автоматически режется дальше до безопасного размера Mermaid.",
        "Диаграммы показывают внутренние связи своего среза; междоменные pin/net",
        "связи без потерь перечислены в machine-derived таблицах ниже. Полный",
        "монолитный исходник сохраняется рядом как",
        "`G2F-3I-principled-projection.mmd` для машинного diff/review.",
        "",
        *_render_split_principled_atlas(raw_lines),
    ]
    return "\n".join(lines), "\n".join(raw_lines) + "\n"


def render_principled_pinout(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> str:
    """Render the human atlas while retaining the raw bundle internally."""

    return _render_principled_pinout_bundle(database, candidates)[0]


def render_public_pinout(
    database: dict[str, Any], candidates: list[dict[str, Any]], *, russian: bool
) -> str:
    """Render the exact current controller assignment without project history."""

    candidate = next(item for item in candidates if item["id"] == "G2F-3I")
    devices = database["devices"]
    owners = (
        ("s3", "S3 — application, UI, display, storage and audio"),
        ("c5", "C5 — native 2.4/5-GHz radio, IEEE 802.15.4 and IR"),
        ("rp", "RP2354B — nRF24 ×3, Sub-GHz, voice and Cap Bus"),
        ("pd_controller", "USB-PD controller"),
        ("pack_admission", "Battery-pack admission controller"),
    )
    if russian:
        title = "# Распиновка Leshy2"
        navigation = "[На главную](../README.ru.md) · [English](pinout.md) · [Аппаратная архитектура](hardware.ru.md)"
        intro = (
            "Страница автоматически строится из той же карты устройств и сетей, что используется "
            "для электрических проверок. Здесь показано текущее целевое назначение контактов."
        )
        headings = {
            "s3": "S3 — приложение, UI, display, storage и audio",
            "c5": "C5 — native 2,4/5 ГГц, IEEE 802.15.4 и IR",
            "rp": "RP2354B — nRF24 ×3, Sub-GHz, voice и Cap Bus",
            "pd_controller": "USB-PD controller",
            "pack_admission": "Контроллер допуска батарейного pack",
        }
        columns = "| Контакт | Сеть | Направление | Периферия | Подключение |"
        footer = (
            "`i` — вход, `o` — выход, `io` — двунаправленный контакт. "
            "Сервисные, питание и fixed-function контакты учитываются в полной machine-карте, "
            "даже если не являются GPIO."
        )
    else:
        title = "# Leshy2 pin assignment"
        navigation = "[Home](../README.md) · [Русский](pinout.ru.md) · [Hardware architecture](hardware.md)"
        intro = (
            "This page is generated from the same device and net map used by the electrical "
            "checks. It shows the current target contact assignment."
        )
        headings = {owner: heading for owner, heading in owners}
        columns = "| Contact | Net | Direction | Peripheral | Connected endpoint |"
        footer = (
            "`i` means input, `o` output and `io` bidirectional. Service, power and fixed-function "
            "contacts remain accounted in the complete machine map even when they are not GPIO."
        )

    def clean(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        title,
        "",
        navigation,
        "",
        intro,
        "",
        "> Файл сгенерирован из `hardware/architecture/devices.json` и `hardware/architecture/candidates/G2F-3I.json`."
        if russian
        else "> Generated from `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`.",
        "",
    ]
    for owner, _ in owners:
        device_id = candidate["instances"][owner]
        mpn = devices[device_id]["mpn"]
        lines.extend((f"## {headings[owner]}", "", f"**MPN:** `{mpn}`", "", columns, "|---|---|---|---|---|"))
        rows = sorted(
            (row for row in candidate["allocations"] if row["instance"] == owner),
            key=lambda row: natural_contact_key(row["contact"]),
        )
        for row in rows:
            peers = "<br>".join(clean(peer) for peer in row.get("peers", ())) or "—"
            lines.append(
                f"| `{clean(row['contact'])}` | `{clean(row['net'])}` | `{clean(row['direction'])}` | "
                f"`{clean(row['controller'])}` | {peers} |"
            )
        lines.append("")
    lines.extend((footer, ""))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate and require generated output to match")
    mode.add_argument("--write", action="store_true", help="validate and rewrite generated output")
    args = parser.parse_args(argv)

    database, candidates = load_sources()
    errors = validate_sources(database, candidates)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    principled_pinout, raw_projection = _render_principled_pinout_bundle(
        database, candidates
    )
    outputs = {
        REPO_ROOT / "README.md": render_readme_schematics(
            (REPO_ROOT / "README.md").read_text(encoding="utf-8"),
            database,
            candidates,
            russian=False,
        ),
        REPO_ROOT / "README.ru.md": render_readme_schematics(
            (REPO_ROOT / "README.ru.md").read_text(encoding="utf-8"),
            database,
            candidates,
            russian=True,
        ),
        REPO_ROOT / database["generated_ledger"]: render_ledger(database, candidates),
        REPO_ROOT / database["generated_principled_pinout"]: principled_pinout,
        REPO_ROOT / "hardware/architecture/generated/G2F-3I-principled-projection.mmd": raw_projection,
        REPO_ROOT / database["generated_target_bom_review"]: render_target_bom_review(
            database, candidates
        ),
        REPO_ROOT / database["generated_target_bom_csv"]: render_target_bom_csv(
            database, candidates
        ),
        REPO_ROOT / "docs/pinout.md": render_public_pinout(
            database, candidates, russian=False
        ),
        REPO_ROOT / "docs/pinout.ru.md": render_public_pinout(
            database, candidates, russian=True
        ),
        REPO_ROOT / "docs/schematics.md": render_public_schematics(
            database, candidates, russian=False
        ),
        REPO_ROOT / "docs/schematics.ru.md": render_public_schematics(
            database, candidates, russian=True
        ),
        REPO_ROOT / "docs/interconnect.md": render_public_interconnect(
            database, candidates, russian=False
        ),
        REPO_ROOT / "docs/interconnect.ru.md": render_public_interconnect(
            database, candidates, russian=True
        ),
    }
    if args.write:
        for output_path, rendered in outputs.items():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
            print(f"wrote {output_path.relative_to(REPO_ROOT)}")
        return 0

    for output_path, rendered in outputs.items():
        if not output_path.exists():
            print(f"ERROR: missing generated artifact {output_path.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        if output_path.read_text(encoding="utf-8") != rendered:
            print(
                f"ERROR: stale generated artifact {output_path.relative_to(REPO_ROOT)}; run --write",
                file=sys.stderr,
            )
            return 1
    print(f"ok: {len(candidates)} candidates, {len(outputs)} generated artifacts are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
