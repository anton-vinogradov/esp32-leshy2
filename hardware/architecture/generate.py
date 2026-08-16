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


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


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
        for contact in device.get("strapping_contacts", []):
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown strap contact {contact}")
        for contact in device.get("service_required", []):
            if contact not in contacts:
                errors.append(f"device {device_id}: unknown service contact {contact}")
        if device.get("programmable") and not device.get("controller_capabilities"):
            errors.append(f"device {device_id}: programmable device lacks controller_capabilities")
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
            required = set(devices[device_id].get("service_required", []))
            missing_service = required - services_by_instance.get(instance, set())
            if missing_service:
                errors.append(f"{candidate_id}: {instance} missing service contacts {sorted(missing_service)}")

        for route_number, route in enumerate(candidate.get("fixed_routes", []), 1):
            context = f"fixed route {route_number}"
            for endpoint_name in ("from", "to"):
                endpoint = route.get(endpoint_name, "")
                _check_endpoint(endpoint, candidate_id, instances, devices, errors, context)
            if not route.get("net") or not route.get("safety"):
                errors.append(f"{candidate_id}: {context}: missing net or safety note")

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
        "Both source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. It does **not** close electrical feasibility: abstract peers, reference-only nRF modules, RF networks, timing HIL, power and physical integration remain open. Therefore neither candidate receives «Проведено ревью» as a complete owner/pin architecture in this artifact.",
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
