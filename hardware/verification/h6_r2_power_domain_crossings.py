"""Potential live-to-unpowered input paths in the commanded AON-only snapshot.

Reuses current native contacts, reviewed KiCad pin types and the H3 load policy.
This is a connectivity screen, not an analog solver or a physical rail-state
measurement. A pull-up path does not establish its loaded pin voltage. Nothing
here establishes damage, numerical incompatibility, or complete qualification.
"""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import re

from hardware.verification import h6_r2_electrical_semantics as semantics
from hardware.verification import h6_r2_electrical_source_triage as triage
from hardware.verification import h3_r2_power_states as states
from hardware.verification import h3_r2_source_margins as source_margins
from hardware.verification import h3_r2_input_freeze as freeze
from hardware.verification import h3_r2_method_contract as methods

ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "nets": triage.LEDGER, "instances": str(semantics.INSTANCES.relative_to(ROOT)),
    "material": triage.MATERIAL, "devices": "hardware/architecture/devices.json",
    "rail_contract": "hardware/verification/h3-r2-load-binding-contract.json",
    "h0": "hardware/architecture/h0-r2-rebaseline.json",
}
LEDGER_CONTRACTS = {name: f"hardware/ecad/h2-r2-{stem}-contract.json" for name, stem in
                    (("nets", "net-ledger"), ("instances", "instance-ledger"), ("material", "contact-materialization"))}
AUTHORITY_KEYS = {
    "nets": {"instances", "definitions", "h0", "dual_rp", "c5_mux", "pack_safety_boundary", "display_mount",
             "main_power_cell", "u219", "freeze_new_parts", "topology"},
    "instances": {"native_inventory", "exact_definition_ledger", "physical_source_table"},
    "material": {"exact_ledger", "device_register"},
}
GROUND = {"POWER_GROUND", "SAFETY_GROUND", "AUDIO_GROUND"}
RECEIVERS = {"input", "bidirectional", "tri_state"}
# No current exact powered-off *input* tolerance review is registered. Generic
# Ioff prose (especially output Ioff) is never a substitute for such evidence.
OFF_INPUT_PROOFS = ()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def relative(path):
    return str(Path(path).relative_to(ROOT))


def source_paths():
    paths = {Path(__file__), *semantics.source_paths(), *(ROOT / p for p in INPUTS.values()),
             *(ROOT / p for p in LEDGER_CONTRACTS.values()), *states.SOURCES, *freeze.SOURCES, *methods.SOURCES}
    paths.update(Path(module.__file__) for module in (triage, states, source_margins, freeze, methods))
    paths.add(ROOT / "hardware/verification/h3_r2_current_scope.py")
    for path in LEDGER_CONTRACTS.values():
        paths.update(ROOT / p for p in load(ROOT / path)["authority"].values())
    paths.update(ROOT / row["source"]["path"] for row in OFF_INPUT_PROOFS)
    return sorted(paths)


def snapshot():
    return {relative(path): triage.digest_relative(relative(path)) for path in source_paths()}


def validate_provenance(data, contracts, hashes):
    for name, keys in AUTHORITY_KEYS.items():
        authority = contracts[name]["authority"]
        declared = {key: row for key, row in data[name]["sources"].items() if row.get("authority", True)}
        require(set(authority) == set(declared) == keys, "required ledger provenance membership differs: " + name)
        for key, path in authority.items():
            require(declared[key]["path"] == path and declared[key]["sha256"] == hashes.get(path),
                    "stale or conflicting ledger provenance: " + name + "." + key)


def state_snapshot():
    # Fresh enumeration is cheap. Validate the direct saved prerequisite hash
    # memberships before reuse; neither a cached status nor zero current proves
    # an actual rail is absent on the PCB.
    for module in (freeze, methods):
        saved = load(module.OUTPUT)
        expected = {relative(p): triage.digest_relative(relative(p)) for p in module.SOURCES}
        require(saved.get("source_sha256") == expected, "stale H3 state prerequisite: " + module.__name__)
    current = states.build()
    require(current.get("status") == "pass" and not current.get("errors"), "H3 state enumeration failed")
    aon = [row for row in current["states"] if row["system_mode"] == "AON_SAFE_ONLY"]
    require(aon, "AON_SAFE_ONLY state is absent")
    policy = source_margins.rail_loads(aon[0], {}, {"loads_ma": {"AON_SAFE_3V3": "1", "3V3_MAIN": "1"}})
    require(policy == {"AON_SAFE_3V3": 1, "3V3_MAIN": 0}, "H3 AON-only load admission changed")
    return {"id": "AON_SAFE_ONLY", "rails": {"AON_SAFE_3V3": "assumed_live", "3V3_MAIN": "commanded_off"},
            "basis": "H3 rail_loads admission policy; commanded snapshot, not measured rail voltages",
            "state_ids": [row["id"] for row in aon], "physical_rail_state_proven": False}


def indexes(data, reviews):
    groups = data["material"]["groups"]
    require(len({g["device_id"] for g in groups}) == len(groups), "duplicate material device")
    contacts = {}
    for group in groups:
        rows = group["contacts"]
        require(len({r["contact"] for r in rows}) == len(rows), "duplicate material contact")
        contacts[group["device_id"]] = {row["contact"]: row for row in rows}
    _, endpoints = triage.indexes(data["nets"], data["material"])
    native, by_instance = {}, defaultdict(list)
    for row in data["instances"]["rows"]:
        key = (row["project"], row["instance"])
        require(key not in native, "duplicate native instance")
        require(not any(r["project"] == row["project"] and r["reference"] == row["reference"] for r in native.values()),
                "duplicate native reference")
        native[key] = row
    for key, endpoint in endpoints.items():
        instance = native.get((endpoint["project"], endpoint["instance"]))
        device = data["devices"]["devices"].get(endpoint["device_id"], {})
        require(instance is not None and all(instance[k] == endpoint[k] for k in ("reference", "device_id", "mpn"))
                and device.get("mpn") == endpoint["mpn"], "native device/MPN identity differs")
        require(endpoint["endpoint"] == endpoint["instance"] + "." + endpoint["contact"], "endpoint identity differs")
        material = contacts[endpoint["device_id"]][endpoint["contact"]]
        require(str(endpoint["physical"]) == str(material["physical"]), "native/material physical contact differs")
        require(endpoint["disposition"] in {"connected", "no_connect"}, "unsupported native contact disposition")
        require(bool(endpoint.get("net")) == (endpoint["disposition"] == "connected"), "native net/disposition differs")
        pin_reviews = reviews.get(endpoint["device_id"], {}).get("pins", {})
        types = {pin_reviews[p]["type"] for p in endpoint["pads"] if p in pin_reviews}
        complete = bool(endpoint["pads"]) and all(p in pin_reviews for p in endpoint["pads"])
        endpoint["type"] = next(iter(types)) if complete and len(types) == 1 else "unreviewed"
        by_instance[(endpoint["project"], endpoint["instance"])].append(endpoint)
    require(set(by_instance) == set(native), "native instance/contact coverage differs")
    for key, instance in native.items():
        require({r["contact"] for r in by_instance[key]} == set(contacts[instance["device_id"]]),
                "native contact coverage differs: " + instance["instance"])
    return native, by_instance


def pin_summary(row):
    return {key: row[key] for key in ("project", "reference", "instance", "contact", "device_id", "mpn", "pads", "net", "type")}


def supply(rows, rails, state):
    pins = [row for row in rows if row["type"] == "power_in" and row.get("net") not in GROUND]
    nets = sorted({row["net"] for row in pins if row.get("net")})
    # Two genuinely different supply nets do not establish which domain owns a
    # given signal pad, even when H3 accounts both against one upstream rail.
    if len(nets) != 1 or any(r["disposition"] != "connected" for r in pins):
        return {"state": "unknown", "reason": "missing_or_multisupply_pin_ownership", "nets": nets}
    net = nets[0]
    domain = rails.get(net, {}).get("rail")
    return {"state": state["rails"].get(domain, "unknown"), "net": net, "domain": domain,
            "contacts": sorted(r["contact"] for r in pins)}


def reviewed_proofs(proofs, devices, groups, hashes):
    result = {}
    materials = {g["device_id"]: g for g in groups}
    for row in proofs:
        require(set(row) == {"device_id", "mpn", "pads", "supply_contacts", "parameter", "supply_v", "input_v", "source"},
                "unsupported off-state proof schema")
        ident = row["device_id"]
        require(row["mpn"] == devices.get(ident, {}).get("mpn") == materials.get(ident, {}).get("mpn"), "off-state proof exact MPN differs")
        require(row["parameter"] == "powered_off_input_voltage_tolerance" and row["supply_v"] == ["0", "0"],
                "proof is not a powered-off input tolerance")
        require(isinstance(row["input_v"], list) and len(row["input_v"]) == 2 and all(type(v) is str for v in row["input_v"]),
                "invalid proof input interval")
        require(Fraction(row["input_v"][0]) <= Fraction(row["input_v"][1]), "invalid proof input interval")
        for name in ("pads", "supply_contacts"):
            require(isinstance(row[name], list) and row[name] and len(set(row[name])) == len(row[name])
                    and all(type(v) is str and v for v in row[name]), "empty/duplicate proof " + name)
        require(set(row["pads"]) <= set(materials[ident]["pad_inventory"]), "unknown proof pads")
        source = row["source"]
        require(set(source) == {"path", "sha256", "url", "revision", "selector", "reviewed_on"}
                and all(type(v) is str and v.strip() for v in source.values())
                and source["url"].startswith("https://"), "incomplete proof source")
        require(re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) is not None
                and hashes.get(source["path"]) == source["sha256"], "stale off-state proof source")
        for pad in row["pads"]:
            require((ident, pad) not in result, "duplicate off-state proof pad")
            result[ident, pad] = row
    return result


def evaluate(data, reviews, state, proofs=(), proof_hashes=None):
    require(state.get("id") == "AON_SAFE_ONLY" and state.get("physical_rail_state_proven") is False
            and state.get("rails") == {"AON_SAFE_3V3": "assumed_live", "3V3_MAIN": "commanded_off"}, "unsupported rail-state assumption")
    native, instances = indexes(data, reviews)
    proof_index = reviewed_proofs(proofs, data["devices"]["devices"], data["material"]["groups"], proof_hashes or {})
    rails = data["rail_contract"]["rail_nets"]
    supplies = {key: supply(rows, rails, state) for key, rows in instances.items()}
    # Join boards only through the reviewed, same-number M1 contacts; unrelated
    # equal local labels on different boards are not silently shorted together.
    shared = set()
    for pin in data["h0"]["interboard_rebaseline"]["pin_map"]:
        number, pair = str(pin["contact"]), []
        for project, instance in (("LESHY2-RF-R2", "m1_rf_receptacle"), ("LESHY2-UI-R2", "m1_ui_plug")):
            rows = [r for r in instances.get((project, instance), []) if r["contact"] == "P" + number]
            require(len(rows) == 1 and rows[0]["pads"] == [number], "M1 physical crossing differs")
            pair.append(rows[0])
        require(pair[0]["net"] == pair[1]["net"] and pair[0]["disposition"] == pair[1]["disposition"], "M1 canonical crossing differs")
        if pair[0]["net"] is not None:
            shared.add(pair[0]["net"])
    def net_key(row):
        return ("M1" if row["net"] in shared else row["project"], row["net"])
    by_net, sources = defaultdict(list), defaultdict(list)
    unknown_supply, unreviewed = [], []
    for key, rows in instances.items():
        for row in rows:
            if row["disposition"] != "connected":
                continue
            by_net[net_key(row)].append(row)
            if row["type"] == "unreviewed":
                unreviewed.append(pin_summary(row))
            if row["net"] not in GROUND and row["type"] in {"output", "bidirectional", "tri_state", "open_emitter"} and supplies[key]["state"] == "assumed_live":
                sources[net_key(row)].append({"kind": "potential_direct_high_drive", "pin": pin_summary(row), "supply": supplies[key]})
        device = data["devices"]["devices"][native[key]["device_id"]]
        if re.match(r"^\d+(?:_\d+)?(?:k|m)?ohm_", device.get("kind", "")) and len(rows) == 2:
            for live, signal in (rows, rows[::-1]):
                domain = rails.get(live.get("net"), {}).get("rail")
                if (live["disposition"] == signal["disposition"] == "connected" and signal["net"] not in GROUND
                        and state["rails"].get(domain) == "assumed_live"):
                    sources[net_key(signal)].append({"kind": "resistor_to_live_rail", "pin": pin_summary(signal),
                                                    "rail_contact": pin_summary(live), "domain": domain})
    for key in by_net:
        domain = rails.get(key[1], {}).get("rail")
        if state["rails"].get(domain) == "assumed_live":
            sources[key].append({"kind": "assumed_live_rail", "net": key[1], "domain": domain,
                                 "physical_voltage_proven": False})
    crossings = []
    for key, drivers in sorted(sources.items()):
        for receiver in by_net[key]:
            if receiver["type"] not in RECEIVERS:
                continue
            domain = supplies[receiver["project"], receiver["instance"]]
            if domain["state"] == "unknown":
                unknown_supply.append({"receiver": pin_summary(receiver), "supply": domain, "sources": drivers})
                continue
            if domain["state"] != "commanded_off":
                continue
            evidence = [proof_index.get((receiver["device_id"], pad)) for pad in receiver["pads"]]
            for proof in (row for row in evidence if row is not None):
                require(proof["supply_contacts"] == domain["contacts"], "off-state proof supply ownership differs")
            complete = all(evidence)
            crossings.append({"net": key[1], "net_scope": key[0], "receiver": pin_summary(receiver), "receiver_supply": domain,
                              "sources": drivers, "status": "unqualified", "qualified": False,
                              "finding_kind": "off_state_input_evidence_requires_voltage_review" if complete else "missing_off_state_tolerance",
                              "input_tolerance_evidence": evidence if complete else [],
                              "pin_voltage_bounded": False, "numerical_incompatibility_proven": False})
    return {"status": "review_required", "qualified": False, "gate_closed": False, "physical_rail_state_proven": False,
            "state": state, "crossings": crossings, "unknown_supply_ownership": unknown_supply,
            "unreviewed_connected_pins": unreviewed, "scanned_instances": len(native), "scanned_nets": len(by_net),
            "limits": ["Only the assumed AON-live/commanded-MAIN-off snapshot; not measured rail voltages or all power sequences",
                       "Direct driver and one-resistor paths only; diode/LED/transistor chains, analog loading, clamps and leakage are unmodeled",
                       "Pullups and configurable outputs establish potential exposure, not an independently bounded receiver voltage",
                       "Exact input-tolerance evidence is not application qualification without a loaded pin-voltage and conditions review"]}


def validate_result(result):
    require(result.get("status") == "review_required" and all(result.get(k) is False for k in
            ("qualified", "gate_closed", "physical_rail_state_proven")), "crossing screen cannot grant physical qualification")
    require(result.get("limits") and result.get("scanned_instances", 0) > 0 and result.get("scanned_nets", 0) > 0,
            "crossing scan coverage missing")
    seen = set()
    for row in result["crossings"]:
        receiver = row["receiver"]
        key = (receiver["project"], receiver["instance"], receiver["contact"])
        require(key not in seen, "duplicate reported receiver")
        seen.add(key)
        require(row["status"] == "unqualified" and all(row.get(k) is False for k in
                ("qualified", "pin_voltage_bounded", "numerical_incompatibility_proven")), "crossing cannot assert a voltage violation")
        require(row["finding_kind"] in {"missing_off_state_tolerance", "off_state_input_evidence_requires_voltage_review"}
                and row["sources"] and row["receiver_supply"]["state"] == "commanded_off", "invalid crossing finding")


def build():
    before = snapshot()
    data = {key: load(ROOT / path) for key, path in INPUTS.items()}
    contracts = {key: load(ROOT / path) for key, path in LEDGER_CONTRACTS.items()}
    validate_provenance(data, contracts, before)
    reviews = semantics.reviewed_maps([load(p) for p in semantics.MAPS], data["material"]["groups"])
    result = evaluate(data, reviews, state_snapshot(), OFF_INPUT_PROOFS, before)
    require(snapshot() == before, "power-domain inputs changed during review")
    validate_result(result)
    return {**result, "source_sha256": before}
