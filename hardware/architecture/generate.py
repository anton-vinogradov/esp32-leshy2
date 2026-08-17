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
        "All source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. Where declared, non-MCU contacts, interface resource contracts, controller GPIO-window selections, fixed-mux contact contracts and capacity arithmetic are also complete. It does **not** close electrical feasibility: abstract peers, reference-only modules, RF networks, timing HIL, power and physical integration remain open. Therefore no candidate receives «Проведено ревью» as a complete target architecture in this generated artifact.",
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

    output_path = REPO_ROOT / database["generated_ledger"]
    rendered = render_ledger(database, candidates)
    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"wrote {output_path.relative_to(REPO_ROOT)}")
        return 0

    if not output_path.exists():
        print(f"ERROR: missing generated ledger {output_path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1
    if output_path.read_text(encoding="utf-8") != rendered:
        print(
            f"ERROR: stale generated ledger {output_path.relative_to(REPO_ROOT)}; run --write",
            file=sys.stderr,
        )
        return 1
    print(f"ok: {len(candidates)} candidates, generated ledger is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
