#!/usr/bin/env python3
"""Check exact source-triage evidence without clearing ERC or changing production."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
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
MAPS = {f"hardware/verification/h6-electrical-pins-{name}.json" for name in ("power", "digital", "logic", "analog", "protection", "interfaces", "passives")}
REQUIRED_SOURCES = {LEDGER, MATERIAL, *MAPS}
PROJECT_COUNTS = {"LESHY2-UI-R2": 5, "LESHY2-RF-R2": 17}
CLASSIFICATIONS = {
    "external_return_boundary", "interboard_source_boundary",
    "post_inductor_converter_model_gap", "series_resistor_feed_model_gap",
    "bootstrap_supply_model_gap", "diode_or_source_model_gap",
    "passive_return_link_model_gap", "ferrite_feed_model_gap",
    "rf_bias_choke_feed_model_gap",
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
    mpns = {group["device_id"]: group["mpn"] for group in material["groups"]}
    require(len(mpns) == len(material["groups"]), "duplicate material device identity")
    require(all(isinstance(mpn, str) and mpn.strip() for mpn in mpns.values()), "missing material exact MPN")
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
        endpoints[key] = {**row, "pads": pads, "mpn": mpns[row["device_id"]]}
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
        content = json.dumps(project["native_erc"], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        require(project.get("erc_content_sha256") == hashlib.sha256(content.encode("utf-8")).hexdigest(), "native ERC observation content changed")
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
        require(node.get("device_id") == actual["device_id"] and node.get("mpn") == actual["mpn"], f"source-path exact device/MPN identity mismatch: {key}; explicit source review required")
        require(key not in seen, f"duplicate source-path endpoint: {key}")
        seen.add(key)
    require(any(node["project"] == row["project"] and node["net"] == row["net"] for node in path), "source path never touches reported net")
    require(isinstance(row.get("reason"), str) and row["reason"].strip(), "missing triage reason")
    obligations = row.get("remaining_obligations", [])
    require(obligations and all(isinstance(x, str) and x.strip() for x in obligations), "remaining electrical obligations missing")
    evidence = row.get("evidence", [])
    require(evidence and all((e.get("source") and e.get("selector")) or (e.get("url", "").startswith("https://") and e.get("section") and e.get("checked")) for e in evidence), "incomplete triage evidence")


def validate_native_hashes(audit, current_hashes):
    hashes = audit.get("source_hashes", {})
    require({MATERIAL, *MAPS}.issubset(hashes) and set(current_hashes) == REQUIRED_SOURCES | set(hashes), "native audit source hash coverage incomplete")
    for path, expected in hashes.items():
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None and current_hashes.get(path) == expected, f"native audit stale source hash: {path}")


def native_net_observations(audit, physical):
    """Resolve observed pins to exact ledger nets; never invent a source path."""
    observations = {}
    for project, kind, pins in native_findings(audit):
        resolved, nets = [], set()
        for reference, pin, uuid in pins:
            candidates = physical.get((project, reference, pin), [])
            require(candidates, f"unknown native reported pin: {(project, reference, pin)}")
            require(len({(r["net"], r["instance"], r["device_id"]) for r in candidates}) == 1, "ambiguous native reported pin")
            # Declared same-pad aliases share a net and device; choose a stable
            # contact label without changing the physical observation.
            row = min(candidates, key=lambda r: r["contact"])
            require(row["net"], "native reported pin has no ledger net")
            nets.add(row["net"])
            resolved.append({"reference": reference, "pin": pin, "instance": row["instance"], "contact": row["contact"], "device_id": row["device_id"], "uuid": uuid})
        require(len(nets) == 1, "native finding spans different ledger nets")
        key = (project, kind, next(iter(nets)))
        require(key not in observations, "duplicate native project/type/net observation")
        observations[key] = resolved
    return observations


def refresh_observations(triage, audit, ledger, material, current_hashes):
    """Refresh only digests/representative pins after an unchanged-path check.

    A new or removed project/net, changed source-path endpoint or exact part, new conflict,
    stale native run or incomplete maps needs an explicit human/agent review.
    This operation cannot create explanations, paths, part identities or clearance decisions.
    """
    require(set(triage.get("source_sha256", {})) == REQUIRED_SOURCES, "triage source hash coverage incomplete; explicit review required")
    validate_native_hashes(audit, current_hashes)
    physical, endpoints = indexes(ledger, material)
    observations = native_net_observations(audit, physical)
    existing = {}
    for rows, kind in ((triage.get("findings", []), "power_pin_not_driven"), (triage.get("conflicts", []), "pin_to_pin")):
        for row in rows:
            key = (row["project"], kind, row["net"])
            require(key not in existing, "duplicate reviewed project/type/net")
            validate_path(row, endpoints)
            existing[key] = row
    require(set(observations) == set(existing), "native project/type/net set changed; explicit source triage required")
    refreshed = copy.deepcopy(triage)
    refreshed["source_sha256"] = {path: current_hashes[path] for path in triage["source_sha256"]}
    for rows, kind in ((refreshed["findings"], "power_pin_not_driven"), (refreshed["conflicts"], "pin_to_pin")):
        for row in rows:
            row["pins"] = observations[(row["project"], kind, row["net"])]
    # The full validator additionally fixes the 22+1 scope and exact ACDRV
    # configuration; changing only the two permitted fields cannot waive it.
    validate(refreshed, audit, ledger, material, current_hashes)
    return refreshed


def validate(triage, audit, ledger, material, current_hashes):
    require(triage.get("schema_version") == 1, "unsupported triage schema")
    require(triage.get("status") == "triaged_not_cleared", "triage cannot claim gate pass")
    require(triage.get("authorization") == AUTHORIZATION, "triage must not authorize production or close gate")
    require(triage.get("observation_source") == AUDIT, "wrong native observation source")
    require(set(triage.get("source_sha256", {})) == REQUIRED_SOURCES, "triage source hash coverage incomplete")
    validate_native_hashes(audit, current_hashes)
    for owner, hashes in (("triage", triage["source_sha256"]), ("native audit", audit.get("source_hashes", {}))):
        require(hashes, f"{owner} source hashes missing")
        for path, expected in hashes.items():
            require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None and current_hashes.get(path) == expected, f"{owner} stale source hash: {path}")
    physical, endpoints = indexes(ledger, material)
    native = native_findings(audit)
    expected_power = Counter(x for x in native if x[1] == "power_pin_not_driven")
    require(Counter(project for project, kind, _ in native if kind == "power_pin_not_driven") == Counter(PROJECT_COUNTS), "native power-warning coverage is not exact 22 (UI5/RF17)")
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
    for key, value in (("native_power_findings", 22), ("ui_findings", 5), ("rf_findings", 17), ("unlocated_reported_pins", 0), ("confirmed_missing_source_from_this_bounded_review", 0)):
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


def validate_native_audit(module, audit, native_hashes, material):
    """Use the native review's full read-only checker before any refresh write."""
    instances = module.load(module.INSTANCES)["rows"]
    reviews = module.reviewed_maps([module.load(path) for path in module.MAPS], material["groups"])
    counts, sheets = {}, {}
    for project in module.PROJECTS:
        typed = list(module.typed_source_sheets(project, instances, reviews))
        counts[project] = sum(count for _, _, count in typed)
        sheets[project] = ["/" if path.stem == project else f"/{path.stem}/" for path, _, _ in typed]
    module.validate_audit(audit, material["groups"], reviews, native_hashes, counts, sheets)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh-observations", action="store_true", help="refresh only hashes and native representative pins for unchanged reviewed source paths")
    args = parser.parse_args()
    original_digests = {path: digest_relative(path) for path in (TRIAGE, AUDIT)}
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
    material, ledger = load(MATERIAL), load(LEDGER)
    validate_native_hashes(audit, current_hashes)
    validate_native_audit(module, audit, {path: current_hashes[path] for path in native_sources}, material)
    if args.refresh_observations:
        triage = refresh_observations(triage, audit, ledger, material, current_hashes)
    result = validate(triage, audit, ledger, material, current_hashes)
    require(all(digest_relative(path) == value for path, value in {**current_hashes, **original_digests}.items()), "inputs changed during triage validation; no observations written")
    if args.refresh_observations:
        (ROOT / TRIAGE).write_text(json.dumps(triage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"H6 source triage current: {result['power_findings']} power warnings, {result['explained_conflicts']} conflict explanation, {result['source_path_endpoints']} exact path endpoints; ERC and production gate remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
