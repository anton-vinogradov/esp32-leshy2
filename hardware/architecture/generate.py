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
    lines = [
        "# G2F — generated exact-device pin ledger",
        "",
        "- Статус: **машинные проверки проведены; кандидаты не приняты и не являются target architecture**",
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
        "All source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. Where declared, non-MCU contacts, interface resource contracts, controller GPIO-window selections, fixed-mux contact contracts, capacity arithmetic, signal-group declarations and quiet-state contract coverage are also complete. It does **not** close electrical feasibility: abstract peers, reference-only modules, RF networks, quiet-state circuitry, timing/EMI HIL, power and physical integration remain open. Therefore no candidate receives «Проведено ревью» as a complete target architecture in this generated artifact.",
        "",
    ]
    return "\n".join(lines)


def render_principled_pinout(
    database: dict[str, Any], candidates: list[dict[str, Any]]
) -> str:
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

    full_ledger = render_ledger(database, candidates)
    detail_start = full_ledger.index("\n### `s3` —", full_ledger.index("\n## G2F-3I —")) + 1
    detail_end = full_ledger.index("\n## Machine-check result and review boundary", detail_start)
    exact_details = full_ledger[detail_start:detail_end].rstrip()

    lines = [
        "# G2F-3I — generated principled pinout atlas",
        "",
        "- Статус: **машинная принципиальная распиновка ведущего paper candidate; не target architecture**",
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
        "синхронно обновить обе стартовые диаграммы.",
        "Каждый прямоугольник физического устройства содержит его exact/current",
        "paper MPN и роль. Разные устройства не объединяются в один прямоугольник.",
        "Если production part ещё не выбран, узел явно помечается `MPN TBD`;",
        "пассивная цепь отдельно помечается как circuit, а не как заказной компонент.",
        "Нормативные pin/net значения находятся в следующих за ней таблицах и",
        "получены из того же JSON. `abstract:*` означает зарезервированную функцию,",
        "для которой exact peripheral MPN/electrical circuit ещё не принят; это не",
        "разрешение рисовать вымышленный pin в KiCad.",
        "",
        "## Принципиальная структура owners и pin groups",
        "",
        "```mermaid",
        "flowchart TD",
        "  subgraph POWER_INPUT[\"Sink-only USB-PD and replaceable-cell power path\"]",
        "  USBC[\"MPN TBD<br/>product USB-C receptacle: S3 USB2 data and sink-only power\"]",
        node("pd_vbus_tvs", "22-V flat-clamp VBUS surge protection"),
        node("pd_controller", "sink-only USB-PD policy and protected high-voltage path"),
        node("pd_config_eeprom", "dedicated PD patch/configuration EEPROM"),
        node("nvdc_charger", "2S-configured buck-boost charger and NVDC system power path"),
        "  CELL0[\"MPN TBD<br/>individually replaceable qualified 18650 cell #0\"]",
        node("pack_fuse0", "slot-0 independent 5-A fast fuse"),
        node("pack_ntc0", "cell-0 temperature sensor"),
        "  CELL1[\"MPN TBD<br/>individually replaceable qualified 18650 cell #1\"]",
        node("pack_fuse1", "slot-1 independent 5-A fast fuse"),
        node("pack_ntc1", "cell-1 temperature sensor"),
        node("pack_gauge", "2S high-side protection, gauging, temperature and balancing"),
        node("pack_shunt", "5-mOhm Kelvin current shunt"),
        node("pack_power_fet", "fully-switching common-drain CHG/DIS power pair"),
        node("pack_hold", "reset-default ALRT hold and explicit release"),
        node("pack_supply_or", "AOLDO/fixture source isolation"),
        node("pack_system_diode", "admitted-system source isolation and priority"),
        node("pack_admission", "fail-closed pair admission, watchdog and service bridge"),
        node("pack_diag_timer", "non-retriggerable hardware diagnostic-pulse limiter"),
        node("pack_diag_timer_res", "169-kOhm 1% diagnostic-pulse timing resistor"),
        node("pack_diag_timer_cap", "220-nF 50-V C0G diagnostic-pulse timing capacitor"),
        node("pack_diag_timer_bypass", "100-nF 50-V X7R one-shot bypass capacitor"),
        node("pack_diag_trigger_pulldown", "10-kOhm 1% diagnostic-trigger fail-low resistor"),
        node("pack_diag_gate_pulldown", "10-kOhm 1% diagnostic-gate fail-low resistor"),
        node("pack_diag_switch", "20-V low-gate-drive diagnostic-load MOSFET"),
        node("pack_diag_res", "10-Ohm 1-W pulse-proof diagnostic-load resistor"),
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
        node("aon_output_cap", "22-uF 10-V X7R AON output capacitor"),
        node("aon_pg_pullup", "47-kOhm 1% AON power-good pull-up resistor"),
        node("main_buck", "fixed 3.3-V 4-A main converter"),
        node("main_inductor", "3.3-uH main-rail power inductor"),
        node("main_input_cap", "22-uF 25-V X7R main-converter bulk input capacitor"),
        node("main_hf_input_cap", "100-nF 50-V X7R main-converter HF input capacitor"),
        node("main_fb_top", "45.3-kOhm 1% main feedback top resistor"),
        node("main_fb_bottom", "10-kOhm 1% main feedback bottom resistor"),
        node("main_ff_cap", "33-pF 50-V C0G main feed-forward capacitor"),
        node("main_output_cap0", "22-uF 25-V X7R main output capacitor #0"),
        node("main_output_cap1", "22-uF 25-V X7R main output capacitor #1"),
        node("main_en_pulldown", "10-kOhm 1% main-enable fail-low resistor"),
        node("power_fault_pullup", "10-kOhm 1% wired-low power-fault pull-up resistor"),
        node("voice_buck", "fixed 4.0-V 4-A voice converter"),
        node("voice_inductor", "3.3-uH voice-rail power inductor"),
        node("voice_input_cap", "22-uF 25-V X7R voice-converter bulk input capacitor"),
        node("voice_hf_input_cap", "100-nF 50-V X7R voice-converter HF input capacitor"),
        node("voice_fb_top", "68-kOhm 1% voice feedback top resistor"),
        node("voice_fb_bottom", "12-kOhm 1% voice feedback bottom resistor"),
        node("voice_ff_cap", "33-pF 50-V C0G voice feed-forward capacitor"),
        node("voice_output_cap0", "22-uF 25-V X7R voice output capacitor #0"),
        node("voice_output_cap1", "22-uF 25-V X7R voice output capacitor #1"),
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
        node("c5", "2.4/5 GHz, IEEE 802.15.4 and IR owner"),
        node("rp", "deterministic radio and voice owner"),
        "  end",
        "  subgraph UI_STORAGE[\"UI and storage devices\"]",
        node("display", "3.5-inch QSPI IPS display and capacitive-touch assembly"),
        node("sd", "push-push microSD card connector"),
        node("slow_io", "24-line slow-control and UI expander"),
        "  end",
        "  subgraph AUDIO_PATH[\"Broadcast, voice and fail-safe audio devices\"]",
        node("receiver", "AM/FM/SW/LW broadcast receiver"),
        "  MONOSUM[\"MPN-independent passive circuit<br/>Si4732 stereo-to-mono summing network\"]",
        node("audio_rx_mux", "Si4732/SA518 receive-audio source selector"),
        "  CAPNET[\"MPN-independent passive circuit<br/>high-impedance AC/bias capture network\"]",
        node("audio_capture_buffer", "active high-impedance capture buffer"),
        "  ADCNET[\"MPN-independent passive circuit<br/>ES8311 mic-range differential input network\"]",
        node("codec", "mono ADC/DAC audio codec"),
        node("audio_speaker_selector", "dual differential speaker-path selector"),
        node("speaker_amp", "mono Class-D speaker amplifier"),
        "  SPEAKER[\"MPN TBD<br/>internal loudspeaker\"]",
        "  TXATT[\"MPN-independent passive circuit<br/>35–45 dB codec-to-voice attenuator/filter\"]",
        node("audio_tx_selector", "electret/codec transmit-audio selector"),
        "  MIC[\"MPN TBD<br/>electret microphone\"]",
        node("audio_safe_gate", "reset-safe dual selector-request gate"),
        node("voice", "VHF/UHF analog voice transceiver"),
        "  end",
        "  subgraph RADIO_ACCESSORY[\"Radio and external-accessory devices\"]",
        node("nrf0", "nRF24-compatible radio #0 compact IPEX reference"),
        node("nrf1", "nRF24-compatible radio #1 compact IPEX reference"),
        node("nrf2", "nRF24-compatible radio #2 compact IPEX reference"),
        node("cc", "sub-GHz transceiver"),
        node("u214", "external LoRa/GNSS Cap module"),
        node("u214_i2c_iso", "external I2C stuck-bus isolator"),
        "  UNIT[\"MPN TBD<br/>protected HY2.0-4P M5 Unit connector\"]",
        "  end",
        "  subgraph IR_PATH[\"IR frontend devices\"]",
        "  IRDEMOD[\"MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver\"]",
        "  IRCARRIER[\"MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver\"]",
        "  IRTX[\"MPN TBD (TSAL6200 screened)<br/>IR transmit LED and fail-safe driver endpoint\"]",
        "  end",
        "  subgraph SAFETY_STOP[\"AON hard-STOP devices\"]",
        "  STOPSW[\"MPN TBD<br/>normally-closed physical STOP control\"]",
        "  REARMSW[\"MPN TBD<br/>normally-open recessed RE-ARM control\"]",
        node("safe_supervisor", "AON rail supervisor and power-on reset"),
        node("safe_conditioner", "STOP and RE-ARM Schmitt conditioner"),
        node("safe_por_or", "STOP-dominant POR/clear combiner"),
        node("safe_latch", "asynchronous latched hard STOP"),
        node("safe_reset_buffer", "Ioff three-domain reset fan-out"),
        node("safe_gate_a", "four STOP-dominant nRF request gates"),
        node("safe_gate_b", "four STOP-dominant rail/IR/accessory gates"),
        node("safe_ptt_or", "active-low voice PTT force-RX gate"),
        node("stop_led", "orange physical latched-STOP indicator"),
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
        node("evidence_cmp_a", "S3/C5/nRF0/nRF1 evidence thresholds"),
        node("evidence_cmp_b", "nRF2/CC/voice/IR evidence thresholds"),
        node("evidence_mask", "eight-bit evidence source mask on local RP I2C0"),
        node("evidence_or_0", "evidence diode-OR pair 0/1"),
        node("evidence_or_1", "evidence diode-OR pair 2/3"),
        node("evidence_or_2", "evidence diode-OR pair 4/5"),
        node("evidence_or_3", "evidence diode-OR pair 6/7"),
        node("any_tx_led", "red physical ANY-TX indicator"),
        "  end",
        "  %% Layout-only invisible spine: these links are not electrical connections.",
        "  USBC ~~~ PD_VBUS_TVS ~~~ PD_CONTROLLER ~~~ PD_CONFIG_EEPROM ~~~ NVDC_CHARGER",
        "  NVDC_CHARGER ~~~ CELL0 ~~~ PACK_FUSE0 ~~~ PACK_NTC0 ~~~ CELL1 ~~~ PACK_FUSE1 ~~~ PACK_NTC1",
        "  PACK_NTC1 ~~~ PACK_GAUGE ~~~ PACK_SHUNT ~~~ PACK_POWER_FET ~~~ PACK_HOLD ~~~ PACK_SUPPLY_OR ~~~ PACK_SYSTEM_DIODE ~~~ PACK_ADMISSION",
        "  PACK_ADMISSION ~~~ PACK_DIAG_TIMER ~~~ PACK_DIAG_TIMER_RES ~~~ PACK_DIAG_TIMER_CAP ~~~ PACK_DIAG_TIMER_BYPASS ~~~ PACK_DIAG_TRIGGER_PULLDOWN ~~~ PACK_DIAG_GATE_PULLDOWN",
        "  PACK_DIAG_GATE_PULLDOWN ~~~ PACK_DIAG_SWITCH ~~~ PACK_DIAG_RES ~~~ PACK_MID_ADC_TOP0 ~~~ PACK_MID_ADC_TOP1 ~~~ PACK_MID_ADC_BOTTOM ~~~ PACK_MID_ADC_FILTER",
        "  PACK_MID_ADC_FILTER ~~~ PACK_STACK_ADC_TOP0 ~~~ PACK_STACK_ADC_TOP1 ~~~ PACK_STACK_ADC_TOP2 ~~~ PACK_STACK_ADC_TOP3 ~~~ PACK_STACK_ADC_TOP4 ~~~ PACK_STACK_ADC_BOTTOM ~~~ PACK_STACK_ADC_FILTER",
        "  PACK_STACK_ADC_FILTER ~~~ AON_BUCK ~~~ AON_INDUCTOR ~~~ AON_MODE_RES ~~~ AON_INPUT_CAP ~~~ AON_OUTPUT_CAP ~~~ AON_PG_PULLUP",
        "  AON_PG_PULLUP ~~~ MAIN_BUCK ~~~ MAIN_INDUCTOR ~~~ MAIN_INPUT_CAP ~~~ MAIN_HF_INPUT_CAP ~~~ MAIN_FB_TOP ~~~ MAIN_FB_BOTTOM ~~~ MAIN_FF_CAP ~~~ MAIN_OUTPUT_CAP0 ~~~ MAIN_OUTPUT_CAP1 ~~~ MAIN_EN_PULLDOWN ~~~ POWER_FAULT_PULLUP",
        "  POWER_FAULT_PULLUP ~~~ VOICE_BUCK ~~~ VOICE_INDUCTOR ~~~ VOICE_INPUT_CAP ~~~ VOICE_HF_INPUT_CAP ~~~ VOICE_FB_TOP ~~~ VOICE_FB_BOTTOM ~~~ VOICE_FF_CAP ~~~ VOICE_OUTPUT_CAP0 ~~~ VOICE_OUTPUT_CAP1 ~~~ VOICE_EN_PULLDOWN ~~~ VOICE_PG_PULLUP ~~~ VOICE_PG_BASE_RES ~~~ VOICE_PG_QUALIFIER",
        "  VOICE_PG_QUALIFIER ~~~ EXT_BUCK ~~~ EXT_INDUCTOR ~~~ EXT_BUCK_INPUT_CAP ~~~ EXT_BUCK_HF_INPUT_CAP ~~~ EXT_BUCK_FB_TOP ~~~ EXT_BUCK_FB_BOTTOM ~~~ EXT_BUCK_FF_CAP ~~~ EXT_BUCK_OUTPUT_CAP0 ~~~ EXT_BUCK_OUTPUT_CAP1 ~~~ EXT_EN_PULLDOWN ~~~ EXT_PG_PULLUP ~~~ EXT_PG_BASE_RES ~~~ EXT_PG_QUALIFIER ~~~ EXT_EFUSE",
        "  EXT_EFUSE ~~~ EXT_RILM ~~~ EXT_DVDT_CAP ~~~ EXT_ITIMER_CAP ~~~ EXT_OVLO_TOP ~~~ EXT_OVLO_BOTTOM",
        "  EXT_OVLO_BOTTOM ~~~ EXT_INPUT_CAP ~~~ EXT_OUTPUT_CAP ~~~ EXT_BLEEDER ~~~ NRF_POWER_SWITCH ~~~ CC_POWER_SWITCH ~~~ SD_POWER_SWITCH ~~~ CODEC_POWER_SWITCH ~~~ RECEIVER_POWER_SWITCH ~~~ S3 ~~~ SLOW_IO",
        "  SLOW_IO ~~~ AUDIO_SAFE_GATE ~~~ RECEIVER ~~~ MONOSUM",
        "  MONOSUM ~~~ AUDIO_RX_MUX ~~~ CAPNET ~~~ AUDIO_CAPTURE_BUFFER ~~~ ADCNET",
        "  ADCNET ~~~ CODEC ~~~ AUDIO_SPEAKER_SELECTOR ~~~ SPEAKER_AMP ~~~ SPEAKER",
        "  SPEAKER ~~~ MIC ~~~ TXATT ~~~ AUDIO_TX_SELECTOR ~~~ DISPLAY ~~~ SD ~~~ UNIT",
        "  UNIT ~~~ C5 ~~~ IRDEMOD ~~~ IRCARRIER ~~~ IRTX ~~~ RP",
        "  RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ VOICE",
        "  VOICE ~~~ U214_I2C_ISO ~~~ U214 ~~~ STOPSW ~~~ REARMSW",
        "  REARMSW ~~~ SAFE_SUPERVISOR ~~~ SAFE_CONDITIONER ~~~ SAFE_POR_OR ~~~ SAFE_LATCH",
        "  SAFE_LATCH ~~~ SAFE_RESET_BUFFER ~~~ SAFE_GATE_A ~~~ SAFE_GATE_B ~~~ SAFE_PTT_OR ~~~ STOP_LED",
        "  STOP_LED ~~~ DET_S3 ~~~ DET_C5 ~~~ DET_NRF0 ~~~ DET_NRF1 ~~~ DET_NRF2",
        "  DET_NRF2 ~~~ DET_CC ~~~ DET_VOICE ~~~ DET_IR ~~~ EVIDENCE_CMP_A ~~~ EVIDENCE_CMP_B",
        "  EVIDENCE_CMP_B ~~~ EVIDENCE_MASK ~~~ EVIDENCE_OR_0 ~~~ EVIDENCE_OR_1 ~~~ EVIDENCE_OR_2 ~~~ EVIDENCE_OR_3 ~~~ ANY_TX_LED",
        "  USBC -->|\"VBUS sink only\"| PD_CONTROLLER",
        "  USBC -->|\"VBUS shunt\"| PD_VBUS_TVS",
        "  USBC <-->|\"D-/D+ direct; no PD/charger tap\"| S3",
        "  PD_CONTROLLER <-->|\"local I²C boot image\"| PD_CONFIG_EEPROM",
        "  PD_CONTROLLER <-->|\"protected VBUS + local I²C/IRQ\"| NVDC_CHARGER",
        "  S3 <-->|\"SYS I²C0 + shared wired-low IRQ\"| PD_CONTROLLER",
        "  CELL0 --> PACK_FUSE0 --> PACK_GAUGE",
        "  PACK_NTC0 -->|\"TH1\"| PACK_GAUGE",
        "  CELL1 --> PACK_FUSE1 --> PACK_GAUGE",
        "  PACK_NTC1 -->|\"TH2\"| PACK_GAUGE",
        "  PACK_SHUNT -->|\"CSP/CSN Kelvin evidence\"| PACK_GAUGE",
        "  PACK_GAUGE -->|\"CHG/DIS gates; no prequal\"| PACK_POWER_FET",
        "  PACK_POWER_FET <-->|\"protected 2S power boundary\"| NVDC_CHARGER",
        "  PACK_HOLD -->|\"ALRT low by default\"| PACK_GAUGE",
        "  PACK_ADMISSION -->|\"explicit release\"| PACK_HOLD",
        "  PACK_GAUGE -->|\"AOLDO\"| PACK_SUPPLY_OR --> PACK_ADMISSION",
        "  PACK_SYSTEM_DIODE -->|\"admitted 3V3\"| PACK_ADMISSION",
        "  PACK_GAUGE <-->|\"local I²C + fault\"| PACK_ADMISSION",
        "  PACK_ADMISSION <-->|\"SYS I²C0 + shared IRQ\"| S3",
        "  PACK_ADMISSION -->|\"PA22 edge\"| PACK_DIAG_TIMER",
        "  PACK_ADMISSION --> PACK_DIAG_TRIGGER_PULLDOWN",
        "  PACK_SUPPLY_OR -->|\"admission VDD\"| PACK_DIAG_TIMER",
        "  PACK_DIAG_TIMER -->|\"169 kΩ / 220 nF; ≤50 ms\"| PACK_DIAG_TIMER_RES --> PACK_DIAG_TIMER_CAP",
        "  PACK_DIAG_TIMER --> PACK_DIAG_TIMER_BYPASS",
        "  PACK_DIAG_TIMER -->|\"bounded gate pulse\"| PACK_DIAG_SWITCH",
        "  PACK_DIAG_TIMER --> PACK_DIAG_GATE_PULLDOWN",
        "  PACK_DIAG_RES -->|\"fused full-stack load\"| PACK_DIAG_SWITCH",
        "  PACK_FUSE0 --> PACK_MID_ADC_TOP0 --> PACK_MID_ADC_TOP1 -->|\"PA25/A2\"| PACK_ADMISSION",
        "  PACK_ADMISSION --> PACK_MID_ADC_BOTTOM",
        "  PACK_ADMISSION --> PACK_MID_ADC_FILTER",
        "  PACK_FUSE1 --> PACK_STACK_ADC_TOP0 --> PACK_STACK_ADC_TOP1 --> PACK_STACK_ADC_TOP2 --> PACK_STACK_ADC_TOP3 --> PACK_STACK_ADC_TOP4 -->|\"PA26/A1\"| PACK_ADMISSION",
        "  PACK_ADMISSION --> PACK_STACK_ADC_BOTTOM",
        "  PACK_ADMISSION --> PACK_STACK_ADC_FILTER",
        "  NVDC_CHARGER -->|\"SYS\"| AON_BUCK --> AON_INDUCTOR -->|\"AON_SAFE_3V3\"| SAFE_SUPERVISOR",
        "  AON_BUCK -->|\"MODE/S-CONF\"| AON_MODE_RES",
        "  NVDC_CHARGER -->|\"SYS local bypass\"| AON_INPUT_CAP",
        "  AON_INDUCTOR -->|\"AON_SAFE_3V3 local bypass\"| AON_OUTPUT_CAP",
        "  AON_INDUCTOR -->|\"PG pull-up\"| AON_PG_PULLUP --> AON_BUCK",
        "  NVDC_CHARGER -->|\"SYS\"| MAIN_BUCK --> MAIN_INDUCTOR -->|\"3V3_MAIN\"| S3",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| MAIN_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| MAIN_HF_INPUT_CAP",
        "  MAIN_INDUCTOR -->|\"feedback\"| MAIN_FB_TOP --> MAIN_FB_BOTTOM",
        "  MAIN_INDUCTOR -->|\"feed-forward\"| MAIN_FF_CAP",
        "  MAIN_INDUCTOR -->|\"local output bank\"| MAIN_OUTPUT_CAP0",
        "  MAIN_INDUCTOR -->|\"local output bank\"| MAIN_OUTPUT_CAP1",
        "  MAIN_BUCK -->|\"EN fail-low\"| MAIN_EN_PULLDOWN",
        "  MAIN_INDUCTOR -->|\"POWER_FAULT_N pull-up\"| POWER_FAULT_PULLUP --> SLOW_IO",
        "  MAIN_INDUCTOR -->|\"3V3_MAIN\"| C5",
        "  MAIN_INDUCTOR -->|\"3V3_MAIN\"| RP",
        "  MAIN_INDUCTOR --> NRF_POWER_SWITCH",
        "  MAIN_INDUCTOR --> CC_POWER_SWITCH",
        "  MAIN_INDUCTOR --> SD_POWER_SWITCH",
        "  MAIN_INDUCTOR --> CODEC_POWER_SWITCH",
        "  MAIN_INDUCTOR --> RECEIVER_POWER_SWITCH",
        "  NVDC_CHARGER -->|\"SYS\"| VOICE_BUCK --> VOICE_INDUCTOR -->|\"fixed 4.0 V\"| VOICE",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| VOICE_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| VOICE_HF_INPUT_CAP",
        "  VOICE_INDUCTOR -->|\"feedback\"| VOICE_FB_TOP --> VOICE_FB_BOTTOM",
        "  VOICE_INDUCTOR -->|\"feed-forward\"| VOICE_FF_CAP",
        "  VOICE_INDUCTOR -->|\"local output bank\"| VOICE_OUTPUT_CAP0",
        "  VOICE_INDUCTOR -->|\"local output bank\"| VOICE_OUTPUT_CAP1",
        "  VOICE_BUCK -->|\"EN fail-low\"| VOICE_EN_PULLDOWN",
        "  MAIN_INDUCTOR -->|\"PG pull-up\"| VOICE_PG_PULLUP --> VOICE_BUCK",
        "  SAFE_GATE_B -->|\"EN\"| VOICE_PG_BASE_RES --> VOICE_PG_QUALIFIER",
        "  VOICE_BUCK -->|\"PG\"| VOICE_PG_QUALIFIER -->|\"qualified open collector\"| SLOW_IO",
        "  NVDC_CHARGER -->|\"SYS\"| EXT_BUCK --> EXT_INDUCTOR --> EXT_EFUSE -->|\"protected fixed 5.0 V\"| U214",
        "  NVDC_CHARGER -->|\"SYS local bulk\"| EXT_BUCK_INPUT_CAP",
        "  NVDC_CHARGER -->|\"SYS local HF\"| EXT_BUCK_HF_INPUT_CAP",
        "  EXT_INDUCTOR -->|\"feedback\"| EXT_BUCK_FB_TOP --> EXT_BUCK_FB_BOTTOM",
        "  EXT_INDUCTOR -->|\"feed-forward\"| EXT_BUCK_FF_CAP",
        "  EXT_INDUCTOR -->|\"local output bank\"| EXT_BUCK_OUTPUT_CAP0",
        "  EXT_INDUCTOR -->|\"local output bank\"| EXT_BUCK_OUTPUT_CAP1",
        "  EXT_BUCK -->|\"EN fail-low\"| EXT_EN_PULLDOWN",
        "  MAIN_INDUCTOR -->|\"PG pull-up\"| EXT_PG_PULLUP --> EXT_BUCK",
        "  SAFE_GATE_B -->|\"EN\"| EXT_PG_BASE_RES --> EXT_PG_QUALIFIER",
        "  EXT_BUCK -->|\"PG\"| EXT_PG_QUALIFIER -->|\"qualified open collector\"| SLOW_IO",
        "  EXT_EFUSE -->|\"ILM\"| EXT_RILM",
        "  EXT_EFUSE -->|\"dVdt\"| EXT_DVDT_CAP",
        "  EXT_EFUSE -->|\"ITIMER\"| EXT_ITIMER_CAP",
        "  EXT_INDUCTOR -->|\"OVLO divider\"| EXT_OVLO_TOP --> EXT_OVLO_BOTTOM",
        "  EXT_INDUCTOR --> EXT_INPUT_CAP",
        "  EXT_EFUSE --> EXT_OUTPUT_CAP",
        "  EXT_EFUSE --> EXT_BLEEDER",
        "  NRF_POWER_SWITCH --> NRF0",
        "  NRF_POWER_SWITCH --> NRF1",
        "  NRF_POWER_SWITCH --> NRF2",
        "  CC_POWER_SWITCH --> CC",
        "  SD_POWER_SWITCH --> SD",
        "  CODEC_POWER_SWITCH --> CODEC",
        "  RECEIVER_POWER_SWITCH --> RECEIVER",
        f"  S3 <-->|\"{sdio_label}: S3 {contacts('s3', ('S3_C5_',))} ↔ C5 {contacts('c5', ('S3_C5_',))}\"| C5",
        f"  S3 <-->|\"SPI3+alert: S3 {contacts('s3', ('S3_RP_', 'RP_ALERT_'))} ↔ RP {contacts('rp', ('S3_RP_', 'RP_ALERT_'))}\"| RP",
        f"  S3 <-->|\"I²C0+INT: {contacts('s3', ('SYS_I2C_', 'SLOW_IO_'))}\"| SLOW_IO",
        f"  S3 -->|\"QSPI/touch: {contacts('s3', ('DISPLAY_SD_', 'LCD_'))}\"| DISPLAY",
        f"  S3 <-->|\"SPI2: {contacts('s3', ('DISPLAY_SD_', 'SD_SPI_'))}\"| SD",
        f"  S3 <-->|\"I²S0/I²C: {contacts('s3', ('I2S_', 'SYS_I2C_'))}\"| CODEC",
        "  S3 <-->|\"I²C0\"| RECEIVER",
        f"  S3 <-->|\"profile port: {contacts('s3', ('UNIT_',))}\"| UNIT",
        f"  C5 <-->|\"RMT RX0/power: {contacts('c5', ('IR_',))}\"| IRDEMOD",
        "  C5 <-->|\"RMT RX1/power\"| IRCARRIER",
        f"  RP <-->|\"PIO0 SM0 + direct control: {contacts('rp', ('NRF0_',))}\"| NRF0",
        f"  RP <-->|\"PIO0 SM1 + direct control: {contacts('rp', ('NRF1_',))}\"| NRF1",
        f"  RP <-->|\"PIO0 SM2 + direct control: {contacts('rp', ('NRF2_',))}\"| NRF2",
        f"  RP <-->|\"PIO0 SM3 + GDO/power: {contacts('rp', ('CC_',))}\"| CC",
        f"  RP <-->|\"UART0/PTT request: {contacts('rp', ('VOICE_', 'PTT_'))}\"| VOICE",
        f"  RP <-->|\"PIO1/UART1: {contacts('rp', ('U214_',))}\"| U214",
        "  RP <-->|\"I²C0\"| U214_I2C_ISO",
        "  U214_I2C_ISO <-->|\"isolated external I²C\"| U214",
        "  RECEIVER --> MONOSUM --> AUDIO_RX_MUX",
        "  VOICE -->|\"AFOUT\"| AUDIO_RX_MUX",
        "  SLOW_IO -->|\"P27 source request\"| AUDIO_RX_MUX",
        "  AUDIO_RX_MUX -->|\"analog bypass\"| AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_RX_MUX --> CAPNET --> AUDIO_CAPTURE_BUFFER --> ADCNET --> CODEC",
        "  CODEC -->|\"OUTP/OUTN\"| AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_SPEAKER_SELECTOR --> SPEAKER_AMP --> SPEAKER",
        "  CODEC --> TXATT --> AUDIO_TX_SELECTOR",
        "  MIC --> AUDIO_TX_SELECTOR -->|\"MIC_IN\"| VOICE",
        "  SLOW_IO -->|\"P11/P12 requests\"| AUDIO_SAFE_GATE",
        "  S3 -->|\"GPIO6 AUDIO_ARM\"| AUDIO_SAFE_GATE",
        "  AUDIO_SAFE_GATE --> AUDIO_SPEAKER_SELECTOR",
        "  AUDIO_SAFE_GATE --> AUDIO_TX_SELECTOR",
        "  STOPSW --> SAFE_CONDITIONER --> SAFE_LATCH",
        "  REARMSW --> SAFE_CONDITIONER",
        "  SAFE_SUPERVISOR --> SAFE_POR_OR --> SAFE_LATCH",
        "  STOPSW --> SAFE_POR_OR",
        "  SAFE_LATCH -->|\"RUN_PERMIT\"| SAFE_RESET_BUFFER",
        "  SAFE_RESET_BUFFER -->|\"CHIP_PU\"| S3",
        "  SAFE_RESET_BUFFER -->|\"CHIP_PU\"| C5",
        "  SAFE_RESET_BUFFER -->|\"RUN\"| RP",
        "  SAFE_LATCH --> SAFE_GATE_A",
        "  SAFE_LATCH --> SAFE_GATE_B",
        "  SAFE_LATCH --> SAFE_PTT_OR",
        "  SAFE_LATCH --> STOP_LED",
        "  RP -->|\"3×CE + nRF rail requests\"| SAFE_GATE_A",
        "  RP -->|\"CC rail request\"| SAFE_GATE_B",
        "  C5 -->|\"IR carrier request\"| SAFE_GATE_B",
        "  SLOW_IO -->|\"voice/accessory rail requests\"| SAFE_GATE_B",
        "  RP -->|\"PTT request\"| SAFE_PTT_OR --> VOICE",
        "  SAFE_GATE_A --> NRF0",
        "  SAFE_GATE_A --> NRF1",
        "  SAFE_GATE_A --> NRF2",
        "  SAFE_GATE_A --> NRF_POWER_SWITCH",
        "  SAFE_GATE_B --> CC_POWER_SWITCH",
        "  SAFE_GATE_B --> VOICE_BUCK",
        "  SAFE_GATE_B --> IRTX",
        "  SAFE_GATE_B --> EXT_BUCK",
        "  SAFE_GATE_B --> EXT_EFUSE",
        "  S3 --> DET_S3 --> EVIDENCE_CMP_A",
        "  C5 --> DET_C5 --> EVIDENCE_CMP_A",
        "  NRF0 --> DET_NRF0 --> EVIDENCE_CMP_A",
        "  NRF1 --> DET_NRF1 --> EVIDENCE_CMP_A",
        "  NRF2 --> DET_NRF2 --> EVIDENCE_CMP_B",
        "  CC --> DET_CC --> EVIDENCE_CMP_B",
        "  VOICE --> DET_VOICE --> EVIDENCE_CMP_B",
        "  IRTX --> DET_IR --> EVIDENCE_CMP_B",
        "  EVIDENCE_CMP_A --> EVIDENCE_MASK",
        "  EVIDENCE_CMP_B --> EVIDENCE_MASK",
        "  EVIDENCE_CMP_A --> EVIDENCE_OR_0",
        "  EVIDENCE_CMP_A --> EVIDENCE_OR_1",
        "  EVIDENCE_CMP_B --> EVIDENCE_OR_2",
        "  EVIDENCE_CMP_B --> EVIDENCE_OR_3",
        "  EVIDENCE_OR_0 --> ANY_TX_LED",
        "  EVIDENCE_OR_1 --> ANY_TX_LED",
        "  EVIDENCE_OR_2 --> ANY_TX_LED",
        "  EVIDENCE_OR_3 --> ANY_TX_LED",
        "  EVIDENCE_MASK <-->|\"local I²C0 source mask\"| RP",
        "  ANY_TX_LED -->|\"RP.GPIO22 RP_ANY_TX_N\"| RP",
        "```",
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
        "AON hard-STOP/evidence circuit. Remaining peripheral MPN, branch power,",
        "signal/power integrity, RF taps/layout and HIL are later gates; этот atlas",
        "не разрешает KiCad и не является frozen BOM.",
        "",
    ]
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

    outputs = {
        REPO_ROOT / database["generated_ledger"]: render_ledger(database, candidates),
        REPO_ROOT / database["generated_principled_pinout"]: render_principled_pinout(
            database, candidates
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
