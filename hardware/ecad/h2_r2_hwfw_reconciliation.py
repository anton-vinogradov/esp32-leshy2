#!/usr/bin/env python3
"""Reconcile current H2-R2 native KiCad nets with six-domain HW/FW authority."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/ecad/h2-r2-hwfw-reconciliation-contract.json"
OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
M1_OUTPUT = ROOT / "hardware/ecad/generated/H2-R2-interboard-m1.json"
AUTHORITY_MODULE = ROOT / "hardware/architecture/r2_authority.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authority_module():
    spec = importlib.util.spec_from_file_location("leshy2_r2_authority", AUTHORITY_MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def contact_name(pin: dict) -> str:
    if pin.get("contact") is not None:
        return str(pin["contact"])
    if pin.get("gpio") is not None:
        return f"GPIO{pin['gpio']}"
    raise ValueError(f"pin row has neither contact nor gpio: {pin}")


def build() -> tuple[dict, dict]:
    contract = load(CONTRACT)
    sources = {name: ROOT / path for name, path in contract["sources"].items()}
    documents = {name: load(path) for name, path in sources.items()}
    authority = authority_module()
    h0 = documents["h0"]
    pin_authority = documents["pin_authority"]
    c5_mux = documents["c5_mux"]
    retained = documents["retained_allocations"]
    physical = documents["physical_h1"]
    native = documents["native_kicad"]
    net_ledger = documents["net_ledger"]
    errors: list[str] = []

    expected_domains = authority.expected_domain_contracts(
        h0["compute_domains"], h0, pin_authority, c5_mux, retained
    )
    endpoint_index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    connected_by_net: dict[str, list[dict]] = defaultdict(list)
    for row in net_ledger["rows"]:
        endpoint_index[(row["instance"], row["contact"])].append(row)
        if row["disposition"] == "connected":
            connected_by_net[row["net"]].append(row)

    aliases = {
        (row["domain"], row["contact"], row["authority_net"], row["schematic_net"]): row
        for row in contract["conditioned_net_aliases"]
    }
    used_aliases: set[tuple[str, str, str, str]] = set()
    pin_results: list[dict] = []
    for domain in expected_domains:
        domain_id = domain["id"]
        instance = contract["domain_instances"][domain_id]
        for pin in domain.get("pin_map", []):
            contact = contact_name(pin)
            candidates = endpoint_index.get((instance, contact), [])
            if len(candidates) != 1:
                errors.append(
                    f"{domain_id}.{contact}: expected one native endpoint, found {len(candidates)}"
                )
                continue
            actual = candidates[0]
            expected_net = pin.get("net")
            if pin.get("direction") == "reserve":
                resolution = "explicit_no_connect"
                if actual["disposition"] != "no_connect" or actual.get("net") is not None:
                    errors.append(f"{domain_id}.{contact}: reserve is connected to {actual.get('net')}")
            elif actual["disposition"] != "connected":
                resolution = "mismatch"
                errors.append(f"{domain_id}.{contact}: {expected_net} became no-connect")
            elif actual.get("net") == expected_net:
                resolution = "exact"
            else:
                alias_key = (domain_id, contact, expected_net, actual.get("net"))
                alias = aliases.get(alias_key)
                if alias is None:
                    resolution = "mismatch"
                    errors.append(
                        f"{domain_id}.{contact}: expected {expected_net}, got {actual.get('net')}"
                    )
                else:
                    resolution = "conditioned_boundary"
                    used_aliases.add(alias_key)
            pin_results.append({
                "domain": domain_id,
                "instance": instance,
                "contact": contact,
                "authority_net": expected_net,
                "schematic_net": actual.get("net"),
                "resolution": resolution,
            })
    unused_aliases = sorted(set(aliases) - used_aliases)
    if unused_aliases:
        errors.append(f"unused conditioned aliases: {unused_aliases}")

    boundaries = {
        frozenset(row["projects"]): row for row in contract["cross_project_boundaries"]
    }
    cross_project_results: list[dict] = []
    for net, rows in sorted(connected_by_net.items()):
        projects = sorted({row["project"] for row in rows})
        if len(projects) < 2:
            continue
        required_boundaries = []
        for project_pair, boundary in boundaries.items():
            if project_pair.issubset(projects):
                required_boundaries.append(boundary)
        if not required_boundaries:
            errors.append(f"{net}: undeclared cross-project route {projects}")
            continue
        evidence = []
        for boundary in required_boundaries:
            present = sorted({
                row["instance"] for row in rows
                if row["instance"] in boundary["endpoint_instances"]
            })
            expected = sorted(boundary["endpoint_instances"])
            if present != expected:
                errors.append(f"{net}: boundary {boundary['role']} has {present}, expected {expected}")
            evidence.append({"role": boundary["role"], "endpoint_instances": present})
        cross_project_results.append({
            "net": net,
            "projects": projects,
            "boundary_evidence": evidence,
        })

    computed_cross_sheet = {}
    for project in native["projects"]:
        project_id = project["id"]
        count = 0
        for rows in connected_by_net.values():
            sheets = {row["sheet"] for row in rows if row["project"] == project_id}
            if len(sheets) > 1:
                count += 1
        computed_cross_sheet[project_id] = count
        if count != project["cross_sheet_net_count"]:
            errors.append(
                f"{project_id}: {count} cross-sheet nets, manifest reports {project['cross_sheet_net_count']}"
            )

    expected_native_summary = {
        "project_count": 3,
        "project_graph_sheet_count": 23,
        "fitted_symbol_instance_count": 1187,
        "physical_symbol_pin_count": 4327,
        "connected_physical_pin_count": 4067,
        "explicit_no_connect_physical_pin_count": 260,
        "canonical_net_count": 827,
    }
    for key, value in expected_native_summary.items():
        if native["summary"].get(key) != value:
            errors.append(f"native summary {key}: {native['summary'].get(key)} != {value}")
    if native.get("status") != "pass" or native.get("errors") != []:
        errors.append("native KiCad manifest is not clean")
    if native["authorization"].get("pcb_placement_or_routing") is not False:
        errors.append("native result crossed the H2 schematic-only authorization boundary")

    authority_hashes = authority.expected_source_hashes()
    physical_path = str(authority.PHYSICAL_H1.relative_to(ROOT))
    physical_reconciliation = {
        "source": physical_path,
        "sha256": authority_hashes[physical_path],
        "marker": physical.get("marker"),
        "pin_authority_marker": physical.get("pin_authority_marker"),
        "status": physical.get("status"),
        "current_h1_blockers": physical.get("current_h1_blockers", []),
        "pre_r2_h2_gates": physical.get("pre_r2_h2_gates", []),
    }
    source_sha256 = dict(authority_hashes)
    source_sha256.update({str(path.relative_to(ROOT)): digest(path) for path in sources.values()})
    source_sha256[str(CONTRACT.relative_to(ROOT))] = digest(CONTRACT)

    export = {
        "schema_version": 2,
        "stage": contract["marker"],
        "status": "pass" if not errors else "fail",
        "export_id": "LESHY2-H2-R2-HWFW-1",
        "authority": {
            "generation": "current_six_domain_r2",
            "current_r2_authority": not errors,
            "native_kicad_started": True,
            "pcb_placement_or_routing": False,
        },
        "source_sha256": source_sha256,
        "bsp": {"domains": expected_domains},
        "integration_contract": {"controllers": expected_domains},
        "r2_reconciliation": {
            "hardware_marker": pin_authority.get("marker"),
            "domain_contracts": expected_domains,
            "hub_pin_map": pin_authority["hub_rp"]["pin_map"],
            "rear_pin_map": pin_authority["rf_rp"]["pin_map"],
            "c5_sdio_service_mux": c5_mux,
            "hardware_sources": authority_hashes,
            "interboard": authority.expected_m1(h0),
            "pre_h2_gates": [],
            "physical_h1": physical_reconciliation,
            "native_kicad": {
                "marker": native["marker"],
                "summary": native["summary"],
                "cross_sheet_net_counts": computed_cross_sheet,
            },
            "pin_reconciliation": pin_results,
            "cross_project_nets": cross_project_results,
        },
        "summary": {
            "domain_count": len(expected_domains),
            "controller_pin_rows": len(pin_results),
            "exact_pin_rows": sum(row["resolution"] == "exact" for row in pin_results),
            "conditioned_boundary_rows": sum(row["resolution"] == "conditioned_boundary" for row in pin_results),
            "explicit_reserve_no_connect_rows": sum(row["resolution"] == "explicit_no_connect" for row in pin_results),
            "cross_project_net_count": len(cross_project_results),
            "cross_sheet_net_count": sum(computed_cross_sheet.values()),
            "errors": len(errors),
        },
        "authorization": contract["authorization"],
        "errors": errors,
    }
    m1_rows = h0["interboard_rebaseline"]["pin_map"]
    m1_export = {
        "schema_version": 2,
        "stage": contract["marker"],
        "status": "pass" if not errors else "fail",
        "artifact": "H2-R2-interboard-M1",
        "contacts": [
            {
                "contact": row["contact"],
                "net": row["net"],
                "class": row.get("class"),
                "direction": row.get("direction"),
            }
            for row in m1_rows
        ],
        "summary": {
            "physical_contacts": len(m1_rows),
            "unique_nets": len({row["net"] for row in m1_rows}),
            "no_connect_reserve_contacts": h0["interboard_rebaseline"]["current_budget"]["no_connect_reserve"],
            "explicit_reserve_class_contacts": sum(row.get("class") == "reserve" for row in m1_rows),
            "errors": len(errors),
        },
        "errors": errors,
    }
    return export, m1_export


def render(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    export, m1 = build()
    if export["errors"]:
        for error in export["errors"]:
            print(f"error: {error}")
        return 1
    expected = {OUTPUT: render(export), M1_OUTPUT: render(m1)}
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    else:
        stale = [path for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(ROOT)}")
            return 1
    summary = export["summary"]
    print(
        "ok: "
        f"{summary['domain_count']} domains, {summary['controller_pin_rows']} controller pins, "
        f"{summary['cross_project_net_count']} cross-project nets, "
        f"{summary['cross_sheet_net_count']} cross-sheet nets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
