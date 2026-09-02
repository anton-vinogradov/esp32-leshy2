#!/usr/bin/env python3
"""Reconcile every current R2 instance contact to a net or explicit NC."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-net-ledger-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
KICAD = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
NUMERIC_PHYSICAL = re.compile(r"^\d+(?:/\d+)*$")
NC_ROLES = {"nc", "no_connect", "reserved"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legacy_reference_map() -> tuple[dict[tuple[str, str], str], list[str]]:
    result: dict[tuple[str, str], str] = {}
    errors: list[str] = []
    for path in sorted((ROOT / "hardware/ecad/generated").glob("H2-*.json")):
        try:
            artifact = load(path)
        except (json.JSONDecodeError, OSError):
            continue
        authority = artifact.get("authority", {})
        if authority.get("baseline") != "R1" or authority.get("allowed_as_r2_authority") is not False:
            continue
        project = artifact.get("project")
        if not project:
            continue
        for row in artifact.get("instances", []):
            reference = row.get("reference") or row.get("ref")
            instance = row.get("instance")
            if not reference or not instance:
                continue
            key = (project, reference)
            if key in result and result[key] != instance:
                errors.append(f"historical reference collision: {key}")
            result[key] = instance
    return result, errors


def export_legacy_nodes(projects: dict[str, str], references: dict[tuple[str, str], str]) -> tuple[dict, list[str]]:
    nodes: dict[tuple[str, str, str], dict] = {}
    errors: list[str] = []
    if not KICAD.is_file():
        return nodes, [f"KiCad CLI not found: {KICAD}"]
    with tempfile.TemporaryDirectory(prefix="leshy2-r2-net-hints-") as temporary:
        for project, relative in projects.items():
            source = ROOT / relative
            output = Path(temporary) / f"{project}.xml"
            completed = subprocess.run(
                [str(KICAD), "sch", "export", "netlist", "--format", "kicadxml", "-o", str(output), str(source)],
                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            if completed.returncode != 0:
                errors.append(f"historical netlist export failed: {project}: {completed.stdout.strip()}")
                continue
            root = ET.parse(output).getroot()
            for net in root.findall("./nets/net"):
                net_name = net.get("name", "")
                for node in net.findall("node"):
                    reference = node.get("ref", "")
                    instance = references.get((project, reference))
                    if not instance:
                        continue
                    key = (project, instance, node.get("pin", ""))
                    value = {
                        "net": net_name,
                        "pinfunction": node.get("pinfunction", ""),
                        "reference": reference,
                    }
                    if key in nodes and nodes[key]["net"] != net_name:
                        errors.append(f"historical endpoint has two nets: {key}")
                    nodes[key] = value
                    pinfunction = value["pinfunction"]
                    suffix = "_" + node.get("pin", "")
                    function = pinfunction[:-len(suffix)] if suffix and pinfunction.endswith(suffix) else pinfunction
                    function_key = (project, instance, f"FUNCTION::{function}")
                    if function_key in nodes and nodes[function_key]["net"] != net_name:
                        errors.append(f"historical contact function has two nets: {function_key}")
                    nodes[function_key] = value
    return nodes, errors


def physical_pins(physical: str) -> list[str]:
    if NUMERIC_PHYSICAL.fullmatch(physical):
        return physical.split("/")
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:/[A-Za-z0-9_]+)*", physical):
        return physical.split("/")
    return []


def legacy_alias(instance: str) -> tuple[str, str | None]:
    if instance == "hub_rp":
        return "rp", "HUB_RP"
    if instance == "rf_rp":
        return "rp", "RF_RP"
    if instance.startswith("hub_rp_"):
        return "rp_" + instance[len("hub_rp_"):], "HUB_RP"
    if instance.startswith("rf_rp_"):
        return "rp_" + instance[len("rf_rp_"):], "RF_RP"
    return instance, None


def transform_legacy_net(net: str, rp_prefix: str | None, aliases: dict[str, str]) -> str:
    if rp_prefix and net.startswith("RP_"):
        net = rp_prefix + net[len("RP"):]
    return aliases.get(net, net)


def route_indexes(
    h1: dict, explicit_aliases: dict[str, str]
) -> tuple[dict[str, list[dict]], dict[str, str], dict[str, str]]:
    routes: dict[str, list[dict]] = defaultdict(list)
    occurrences: Counter[str] = Counter()
    for row in h1.get("fixed_routes", []):
        occurrences[explicit_aliases.get(row["net"], row["net"])] += 1
        for endpoint in (row.get("from", ""), row.get("to", "")):
            if endpoint and not endpoint.startswith("abstract:"):
                routes[endpoint].append(row)
    parent: dict[str, str] = {}

    def find(item: str) -> str:
        parent.setdefault(item, item)
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for rows in routes.values():
        nets = [explicit_aliases.get(row["net"], row["net"]) for row in rows]
        for net in nets:
            find(net)
        for net in nets[1:]:
            union(nets[0], net)
    groups: dict[str, set[str]] = defaultdict(set)
    for net in parent:
        groups[find(net)].add(net)
    preferred = {explicit_aliases.get(net, net) for net in explicit_aliases.values()}
    inferred_aliases: dict[str, str] = {}
    for group in groups.values():
        preferred_group = group & preferred
        choices = preferred_group or group
        canonical = sorted(choices, key=lambda net: (-occurrences[net], len(net), net))[0]
        for net in group:
            inferred_aliases[net] = canonical
    for source, target in explicit_aliases.items():
        inferred_aliases[source] = inferred_aliases.get(target, target)
    allocations = {
        f"{row['instance']}.{row['contact']}": row["net"]
        for row in h1.get("allocations", [])
    }
    return routes, allocations, inferred_aliases


def routed_current_net(
    endpoint: str,
    routes: dict[str, list[dict]],
    aliases: dict[str, str],
    route_aliases: dict[str, str],
    rp_prefix: str | None = None,
) -> tuple[str | None, str | None]:
    rows = routes.get(endpoint, [])
    if not rows:
        return None, None
    for row in rows:
        peer = row["to"] if row["from"] == endpoint else row["from"]
        if peer.startswith("abstract:no-connect"):
            return None, "reconciled_historical_explicit_nc_hint"
    nets = {
        transform_legacy_net(route_aliases.get(row["net"], aliases.get(row["net"], row["net"])), rp_prefix, aliases)
        for row in rows
    }
    if len(nets) != 1:
        return None, None
    return next(iter(nets)), "reconciled_historical_same_endpoint_route_hint"


def current_override(instance: str, contact: str, sources: dict[str, dict], aliases: dict[str, str]) -> tuple[str | None, str | None]:
    h0 = sources["h0"]
    dual = sources["dual_rp"]
    c5 = sources["c5_mux"]
    boundary = sources["pack_safety_boundary"]
    display = sources["display_mount"]
    h1_routes = sources["h1_routes"]
    routes = sources["_h1_route_index"]
    allocations = sources["_h1_allocation_index"]
    route_aliases = sources["_h1_route_net_aliases"]
    topology = sources["topology"].get("endpoint_overrides", {})
    endpoint = f"{instance}.{contact}"
    if endpoint in topology:
        return topology[endpoint], "current_r2_board_local_topology"
    if instance == "s3" and contact.startswith("GPIO"):
        gpio = int(contact[4:])
        row = next((row for row in h0["s3"]["pin_map"] if row["gpio"] == gpio), None)
        if row:
            if row.get("direction") == "reserve":
                return None, "current_h0_reserved_gpio_explicit_nc"
            return aliases.get(row["net"], row["net"]), "current_h0_s3_pin_map"
    if instance in {"hub_rp", "rf_rp"} and contact.startswith("GPIO"):
        gpio = int(contact[4:])
        row = next((row for row in dual[instance]["pin_map"] if row["gpio"] == gpio), None)
        if row:
            if row.get("direction") == "reserve":
                return None, "current_h1_reserved_gpio_explicit_nc"
            return aliases.get(row["net"], row["net"]), "current_h1_dual_rp_pin_map"
    if instance == "c5" and contact.startswith("GPIO"):
        gpio = contact
        signal_to_net = {
            "SDIO_DAT1": "C5_SDIO_D1_C5",
            "SDIO_DAT0": "C5_SDIO_D0_C5",
            "SDIO_CLK": "C5_SDIO_CLK_C5",
            "SDIO_CMD": "C5_SDIO_CMD_C5",
            "SDIO_DAT3_USB_DM": "C5_GPIO13_COMMON",
            "SDIO_DAT2_USB_DP": "C5_GPIO14_COMMON",
        }
        row = next((row for row in c5["c5_module"]["signals"] if row["gpio"] == gpio), None)
        if row:
            return signal_to_net[row["signal"]], "current_c5_fixed_mux_contract"
        if contact in h1_routes.get("reservations", {}).get("c5", {}) or contact in h1_routes.get("free_gpio", {}).get("c5", []):
            return None, "reconciled_historical_reserved_or_free_nc_hint"
    if instance in {"m1_ui_plug", "m1_rf_receptacle"} and contact.startswith("P"):
        position = int(contact[1:])
        row = next(row for row in h0["interboard_rebaseline"]["pin_map"] if row["contact"] == position)
        net = aliases.get(row["net"], row["net"])
        if row["class"] == "reserve":
            return None, "current_h0_m1_explicit_nc"
        return net, "current_h0_m1_map"
    if instance == "hub_safe_i2c_boundary":
        row = next(row for row in boundary["buffer"]["pin_topology"] if row["name"] == contact)
        return aliases.get(row["net"], row["net"]), "current_pack_safety_boundary"
    if instance == "display_connector" and contact.startswith("PIN_"):
        position = contact[4:]
        text = display["electrical"]["panel_pin_map"][position]
        if text.startswith("OPEN "):
            return None, "current_display_direct_explicit_nc"
        return aliases.get(text, text), "current_display_direct_map"
    if instance in {"hub_rp", "rf_rp"} and contact.startswith("QSPI_") and contact != "QSPI_SS_USB_BOOT":
        return None, "current_exact_stacked_flash_no_connect"
    controller_gpio = instance in {"s3", "c5", "hub_rp", "rf_rp"} and contact.startswith("GPIO")
    if not controller_gpio:
        net, origin = routed_current_net(endpoint, routes, aliases, route_aliases)
        if origin:
            return net, origin
        if endpoint in allocations:
            net = route_aliases.get(allocations[endpoint], aliases.get(allocations[endpoint], allocations[endpoint]))
            return net, "reconciled_historical_controller_allocation_hint"
        old_instance, rp_prefix = legacy_alias(instance)
        if old_instance != instance:
            net, origin = routed_current_net(
                f"{old_instance}.{contact}", routes, aliases, route_aliases, rp_prefix
            )
            if origin:
                return net, origin
    if instance.startswith("hub_safe_i2c_") and contact in {"END_1", "END_2"}:
        if contact == "END_2":
            return "POWER_GROUND", "current_pack_safety_decoupling"
        rail = "AON_SAFE_3V3" if "_aon_" in instance else "3V3_MAIN"
        return rail, "current_pack_safety_decoupling"
    return None, None


def build() -> dict:
    contract = load(CONTRACT)
    errors: list[str] = []
    current_sources: dict[str, dict] = {}
    source_manifest: dict[str, dict] = {}
    for name, relative in contract["authority"].items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing current net authority: {relative}")
            continue
        current_sources[name] = load(path)
        source_manifest[name] = {"path": relative, "sha256": sha256(path), "authority": True}
    historical = contract["reconciled_historical_hints"]
    route_contract_path = ROOT / historical["route_contract"]
    current_sources["h1_routes"] = load(route_contract_path)
    source_manifest["historical_route_contract"] = {
        "path": historical["route_contract"],
        "sha256": sha256(route_contract_path),
        "authority": False,
    }
    route_index, allocation_index, route_net_aliases = route_indexes(
        current_sources["h1_routes"], contract.get("canonical_net_aliases", {})
    )
    current_sources["_h1_route_index"] = route_index
    current_sources["_h1_allocation_index"] = allocation_index
    current_sources["_h1_route_net_aliases"] = route_net_aliases
    old_ledger_path = ROOT / historical["instance_ledger"]
    source_manifest["historical_instance_ledger"] = {
        "path": historical["instance_ledger"], "sha256": sha256(old_ledger_path), "authority": False,
    }
    for project, relative in historical["kicad_projects"].items():
        path = ROOT / relative
        source_manifest[f"historical_project_{project}"] = {
            "path": relative, "sha256": sha256(path), "authority": False,
        }
    reference_map, reference_errors = legacy_reference_map()
    errors.extend(reference_errors)
    legacy_nodes, legacy_errors = export_legacy_nodes(historical["kicad_projects"], reference_map)
    errors.extend(legacy_errors)
    old_rows = load(old_ledger_path).get("rows", [])
    old_device_candidates: dict[str, list[dict]] = defaultdict(list)
    for row in old_rows:
        old_device_candidates[row["instance"]].append(row)

    instances = current_sources.get("instances", {}).get("rows", [])
    definitions = {
        row["device_id"]: row for row in current_sources.get("definitions", {}).get("groups", [])
    }
    aliases = contract.get("canonical_net_aliases", {})
    replacements = contract.get("same_pin_replacements", {})
    rows = []
    unresolved = []
    origins = Counter()
    for instance_row in instances:
        instance = instance_row["instance"]
        device_id = instance_row["device_id"]
        definition = definitions[device_id]
        old_instance, rp_prefix = legacy_alias(instance)
        old_candidates = old_device_candidates.get(old_instance, [])
        allowed_old_device = replacements.get(device_id, device_id)
        old_candidates = [row for row in old_candidates if row["device_key"] == allowed_old_device]
        if len(old_candidates) > 1:
            project_hint = "LESHY2-RF" if rp_prefix else None
            if project_hint:
                old_candidates = [row for row in old_candidates if row["project"] == project_hint]
        for contact, contact_row in definition["contact_map"].items():
            role = contact_row["role"]
            override_net, override_origin = current_override(instance, contact, current_sources, aliases)
            if override_origin:
                disposition = "no_connect" if override_net is None else "connected"
                net = override_net
                origin = override_origin
            elif role in NC_ROLES:
                disposition = "no_connect"
                net = None
                origin = "current_exact_contact_role"
            elif not physical_pins(str(contact_row["physical"])):
                if role == "rf":
                    disposition = "external_interface"
                    net = f"EXTERNAL::{instance}.{contact}"
                    origin = "current_exact_external_interface"
                else:
                    disposition = "unresolved"
                    net = None
                    origin = "unresolved_non_numeric_contact"
            elif len(old_candidates) == 1:
                old = old_candidates[0]
                found = []
                for pin in physical_pins(str(contact_row["physical"])):
                    node = legacy_nodes.get((old["project"], old_instance, pin))
                    if node and not node["net"].startswith("unconnected-("):
                        found.append(transform_legacy_net(node["net"], rp_prefix, aliases))
                function_node = legacy_nodes.get((old["project"], old_instance, f"FUNCTION::{contact}"))
                if function_node and not function_node["net"].startswith("unconnected-("):
                    found.append(transform_legacy_net(function_node["net"], rp_prefix, aliases))
                unique = sorted(set(found))
                if len(unique) == 1:
                    disposition = "connected"
                    net = unique[0]
                    origin = "reconciled_historical_same_pin_hint"
                else:
                    disposition = "unresolved"
                    net = None
                    origin = "unresolved_historical_pin_hint"
            else:
                disposition = "unresolved"
                net = None
                origin = "unresolved_without_reconciled_source"
            row = {
                "endpoint": f"{instance}.{contact}",
                "instance": instance,
                "project": instance_row["project"],
                "sheet": instance_row["sheet"],
                "reference": instance_row["reference"],
                "device_id": device_id,
                "contact": contact,
                "physical": contact_row["physical"],
                "role": role,
                "disposition": disposition,
                "net": net,
                "origin": origin,
                "historical_topology_authority": False,
            }
            rows.append(row)
            origins[origin] += 1
            if disposition == "unresolved":
                unresolved.append(row)

    if len(rows) != 4302:
        errors.append(f"current endpoint count changed: {len(rows)} != 4302")
    current_endpoints = {row["endpoint"] for row in rows}
    stale_topology = sorted(set(current_sources.get("topology", {}).get("endpoint_overrides", {})) - current_endpoints)
    if stale_topology:
        errors.append(f"stale board-local topology endpoints: {stale_topology}")
    if unresolved:
        errors.append(f"unresolved current endpoints: {len(unresolved)}")
    if len({row["endpoint"] for row in rows}) != len(rows):
        errors.append("duplicate current endpoint names")
    authorization = contract["authorization"]
    if authorization != {
        "native_net_ledger": True,
        "kicad_project_creation": False,
        "pcb_placement_or_routing": False,
        "fabrication": False,
        "ordering": False,
    }:
        errors.append("native net authorization boundary changed")
    return {
        "schema_version": 1,
        "artifact": "H2-R2-native-net-ledger",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "sources": source_manifest,
        "summary": {
            "endpoint_count": len(rows),
            "connected_endpoint_count": sum(row["disposition"] == "connected" for row in rows),
            "no_connect_endpoint_count": sum(row["disposition"] == "no_connect" for row in rows),
            "external_interface_endpoint_count": sum(row["disposition"] == "external_interface" for row in rows),
            "unresolved_endpoint_count": len(unresolved),
            "unique_net_count": len({row["net"] for row in rows if row["disposition"] == "connected"}),
            "origin_counts": dict(sorted(origins.items())),
            "errors": len(errors),
        },
        "canonical_net_aliases": dict(sorted(
            (source, target)
            for source, target in current_sources.get("_h1_route_net_aliases", {}).items()
            if source != target
        )),
        "rows": rows,
        "authorization": authorization,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--analyze", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.analyze:
        print(json.dumps(result["summary"], indent=2))
        unresolved = [row for row in result["rows"] if row["disposition"] == "unresolved"]
        for row in unresolved[:200]:
            print(f"UNRESOLVED {row['endpoint']} [{row['device_id']}] {row['origin']}")
        return 1 if result["errors"] else 0
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
    print("ok: 4302 current R2 endpoints reconciled; zero unresolved; native projects not yet created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
