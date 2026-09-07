#!/usr/bin/env python3
"""Check exact source-triage evidence without clearing ERC or changing production."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TRIAGE = "hardware/verification/h6-electrical-source-triage.json"
AUDIT = "hardware/verification/generated/H6-R2-electrical-semantics.json"
LEDGER = "hardware/ecad/generated/H2-R2-native-net-ledger.json"
MATERIAL = "hardware/ecad/generated/H2-R2-contact-materialization.json"
MAPS = {f"hardware/verification/h6-electrical-pins-{name}.json" for name in ("power", "digital", "logic")}
REQUIRED_SOURCES = {LEDGER, MATERIAL, *MAPS}
PROJECT_COUNTS = {"LESHY2-UI-R2": 5, "LESHY2-RF-R2": 16}
CLASSIFICATIONS = {
    "external_return_boundary", "interboard_source_boundary",
    "post_inductor_converter_model_gap", "series_resistor_feed_model_gap",
    "bootstrap_supply_model_gap", "diode_or_source_model_gap",
    "passive_return_link_model_gap", "ferrite_feed_model_gap",
}
AUTHORIZATION = {"fabrication": False, "gate_closed": False}
PIN_PATTERN = re.compile(r"Symbol\s+(\S+)\s+(?:Вывод|Pin)\s+(\S+)\s+\[", re.IGNORECASE)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest_relative(relative):
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, f"unsafe source path: {relative}")
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT) and resolved.is_file(), f"missing source: {relative}")
    return hashlib.sha256(resolved.read_bytes()).hexdigest()


def indexes(ledger, material):
    shared = {g["device_id"]: g.get("shared_electrical_pads", {}) for g in material["groups"]}
    contacts = {
        group["device_id"]: {row["contact"]: row["pads"] for row in group["contacts"]}
        for group in material["groups"]
    }
    pins, endpoints = {}, {}
    for row in ledger["rows"]:
        pads = contacts[row["device_id"]][row["contact"]]
        key = (row["project"], row["reference"], row["instance"], row["contact"])
        require(key not in endpoints, f"duplicate ledger endpoint: {key}")
        endpoints[key] = {**row, "pads": pads}
        for pin in pads:
            key = (row["project"], row["reference"], pin)
            previous = pins.setdefault(key, [])
            if previous:
                declared = shared[row["device_id"]].get(pin, [])
                require(all(old["contact"] in declared and row["contact"] in declared and old["net"] == row["net"] and old["instance"] == row["instance"] for old in previous), f"undeclared or inconsistent shared physical pin: {key}")
            previous.append(row)
    return pins, endpoints


def native_findings(audit):
    require(audit.get("status") == "review_required", "native audit must retain review_required")
    require(audit.get("authorization") == AUTHORIZATION, "native audit must not close gate")
    projects = audit.get("projects", [])
    require(Counter(p["project"] for p in projects) == Counter({p: 1 for p in PROJECT_COUNTS}), "native project coverage changed")
    result = []
    for project in projects:
        require(project.get("native_connectivity_unchanged") is True, "native connectivity is not verified unchanged")
        counts = Counter()
        for sheet in project["native_erc"]["sheets"]:
            for violation in sheet.get("violations", []):
                require(not violation.get("excluded", False), "native ERC finding is excluded")
                require(violation.get("severity") == "error", "native severity changed")
                pins = []
                for item in violation["items"]:
                    match = PIN_PATTERN.search(item["description"])
                    require(match is not None and item.get("uuid"), "cannot resolve exact native ERC pin")
                    pins.append((match[1], match[2], item["uuid"]))
                require(pins and len(set(pins)) == len(pins), "empty or duplicate native finding pins")
                result.append((project["project"], violation["type"], tuple(sorted(pins))))
                counts[violation["type"]] += 1
        require(dict(counts) == project["erc_count_by_type"], "native ERC count summary disagrees")
    require(len(result) == len(set(result)), "duplicate native ERC finding")
    return result


def validate_pin(project, net, pin, physical):
    key = (project, pin["reference"], pin["pin"])
    require(key in physical, f"unknown reported pin: {key}")
    candidates = physical[key]
    require(all(row["net"] == net for row in candidates), f"reported pin/net mismatch: {key}")
    for field in ("instance", "contact", "device_id"):
        candidates = [row for row in candidates if pin[field] == row[field]]
        require(candidates, f"reported pin {field} mismatch: {key}")
    require(pin.get("uuid"), f"reported pin lacks UUID: {key}")


def validate_path(row, endpoints):
    path = row.get("source_path", [])
    require(path, "source path is missing")
    seen = set()
    for node in path:
        key = tuple(node[field] for field in ("project", "reference", "instance", "contact"))
        require(key in endpoints, f"unknown source-path endpoint: {key}")
        actual = endpoints[key]
        require(node["net"] == actual["net"] and node["pads"] == actual["pads"], f"source-path pin/net mismatch: {key}")
        require(key not in seen, f"duplicate source-path endpoint: {key}")
        seen.add(key)
    require(any(node["project"] == row["project"] and node["net"] == row["net"] for node in path), "source path never touches reported net")
    require(isinstance(row.get("reason"), str) and row["reason"].strip(), "missing triage reason")
    obligations = row.get("remaining_obligations", [])
    require(obligations and all(isinstance(x, str) and x.strip() for x in obligations), "remaining electrical obligations missing")
    evidence = row.get("evidence", [])
    require(evidence and all((e.get("source") and e.get("selector")) or (e.get("url", "").startswith("https://") and e.get("section") and e.get("checked")) for e in evidence), "incomplete triage evidence")


def validate(triage, audit, ledger, material, current_hashes):
    require(triage.get("schema_version") == 1, "unsupported triage schema")
    require(triage.get("status") == "triaged_not_cleared", "triage cannot claim gate pass")
    require(triage.get("authorization") == AUTHORIZATION, "triage must not authorize production or close gate")
    require(triage.get("observation_source") == AUDIT, "wrong native observation source")
    require(set(triage.get("source_sha256", {})) == REQUIRED_SOURCES, "triage source hash coverage incomplete")
    require({MATERIAL, *MAPS}.issubset(audit.get("source_hashes", {})) and set(current_hashes) == REQUIRED_SOURCES | set(audit.get("source_hashes", {})), "native audit source hash coverage incomplete")
    for owner, hashes in (("triage", triage["source_sha256"]), ("native audit", audit.get("source_hashes", {}))):
        require(hashes, f"{owner} source hashes missing")
        for path, expected in hashes.items():
            require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None and current_hashes.get(path) == expected, f"{owner} stale source hash: {path}")
    physical, endpoints = indexes(ledger, material)
    native = native_findings(audit)
    expected_power = Counter(x for x in native if x[1] == "power_pin_not_driven")
    require(Counter(project for project, kind, _ in native if kind == "power_pin_not_driven") == Counter(PROJECT_COUNTS), "native power-warning coverage is not exact 21 (UI5/RF16)")
    rows = triage.get("findings", [])
    seen, observed = set(), Counter()
    for row in rows:
        key = (row["project"], row["net"])
        require(key not in seen, "duplicate power-net triage")
        seen.add(key)
        require(row.get("classification") in CLASSIFICATIONS, "unknown power-triage classification")
        require(row.get("disposition") == "source_path_observed_not_electrically_cleared", "power finding falsely cleared")
        pins = row.get("pins", [])
        require(pins, "reported pin list missing")
        for pin in pins:
            validate_pin(row["project"], row["net"], pin, physical)
        signature = (row["project"], "power_pin_not_driven", tuple(sorted((p["reference"], p["pin"], p["uuid"]) for p in pins)))
        observed[signature] += 1
        validate_path(row, endpoints)
    require(observed == expected_power, "triage/native power-warning coverage mismatch")
    summary = triage.get("summary", {})
    for key, value in (("native_power_findings", 21), ("ui_findings", 5), ("rf_findings", 16), ("unlocated_reported_pins", 0), ("confirmed_missing_source_from_this_bounded_review", 0)):
        require(type(summary.get(key)) is int and summary[key] == value, f"triage summary mismatch: {key}")
    require(summary.get("whole_electrical_gate_pass") is False, "triage cannot claim whole gate pass")
    require(summary.get("classification_counts") == dict(Counter(r["classification"] for r in rows)), "classification counts mismatch")

    # This is a documented explanation, not an ERC waiver. Any new conflict fails closed.
    conflicts = triage.get("conflicts", [])
    require(len(conflicts) == 1, "exact ACDRV conflict explanation missing")
    conflict = conflicts[0]
    require((conflict.get("project"), conflict.get("net"), conflict.get("type")) == ("LESHY2-RF-R2", "POWER_GROUND", "pin_to_pin"), "ACDRV conflict scope changed")
    require(conflict.get("classification") == "manufacturer_permitted_unused_driver_grounding" and conflict.get("disposition") == "explanation_only_no_erc_suppression", "ACDRV explanation must not suppress ERC")
    require({(p["reference"], p["pin"], p["instance"], p["device_id"]) for p in conflict["pins"]} == {("U1", "10", "nvdc_charger", "ti_bq25798_rqmr"), ("U1", "11", "nvdc_charger", "ti_bq25798_rqmr")}, "ACDRV exact driver pins changed")
    for pin in conflict["pins"]:
        validate_pin(conflict["project"], conflict["net"], pin, physical)
    signature = (conflict["project"], conflict["type"], tuple(sorted((p["reference"], p["pin"], p["uuid"]) for p in conflict["pins"])))
    require(Counter(x for x in native if x[1] != "power_pin_not_driven") == Counter([signature]), "unexplained or changed native non-power conflict")
    validate_path(conflict, endpoints)
    expected_config = {"ACDRV1": "POWER_GROUND", "ACDRV2": "POWER_GROUND", "GND": "POWER_GROUND", "VAC1": "PD_NEGOTIATED_VBUS", "VAC2": "PD_NEGOTIATED_VBUS", "VBUS": "PD_NEGOTIATED_VBUS"}
    actual_config = {n["contact"]: n["net"] for n in conflict["source_path"] if n["project"] == "LESHY2-RF-R2" and n["reference"] == "U1" and n["instance"] == "nvdc_charger"}
    require(actual_config == expected_config and len(conflict["source_path"]) == len(expected_config), "ACDRV VBUS-only configuration evidence incomplete")
    require(any(e.get("url") == "https://www.ti.com/lit/ds/symlink/bq25798.pdf" and "7.3.5.2" in e.get("section", "") for e in conflict["evidence"]), "ACDRV manufacturer configuration evidence missing")
    return {"power_findings": len(rows), "explained_conflicts": 1, "source_path_endpoints": sum(len(r["source_path"]) for r in [*rows, conflict]), "gate_closed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    triage, audit = load(TRIAGE), load(AUDIT)
    # Discover the real native review inputs, not merely whatever a possibly
    # truncated audit claims to hash. Importing this module does not run KiCad.
    spec = importlib.util.spec_from_file_location("h6_native_semantics_sources", ROOT / "hardware/verification/h6_r2_electrical_semantics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    native_sources = {str(path.relative_to(ROOT)) for path in module.source_paths()}
    require(set(audit.get("source_hashes", {})) == native_sources, "native audit source hash coverage incomplete")
    sources = REQUIRED_SOURCES | native_sources
    current_hashes = {path: digest_relative(path) for path in sources}
    result = validate(triage, audit, load(LEDGER), load(MATERIAL), current_hashes)
    print(f"H6 source triage current: {result['power_findings']} power warnings, {result['explained_conflicts']} conflict explanation, {result['source_path_endpoints']} exact path endpoints; ERC and production gate remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
