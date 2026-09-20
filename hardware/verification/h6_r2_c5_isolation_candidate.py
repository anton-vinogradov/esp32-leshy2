"""In-memory, nonproduction C5 evidence isolation candidate; no new solver.

Adds four instances of existing exact part types, never edits native sources.
The existing domain-crossing evaluator screens a commanded state; changing
the count or receiver of a path is not circuit qualification or ranking.
"""

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import signal
import tempfile
import time

from hardware.verification import h6_r2_power_domain_crossings as crossings
from hardware.verification import h6_r2_c5_interface_screen as interface

ROOT = crossings.ROOT
PROJECT = "LESHY2-UI-R2"
SHEET = "UI_20_C5_WIFI_IR_SERVICE"
ORIGIN = "experimental_c5_isolation_overlay_not_production"
BUFFER = "exp_c5_evidence_iso"
OUTPUTS = {"c5.GPIO23": ("EV_N1_C5", "EXP_C5_RF_TX_EVIDENCE_N"),
           "c5.GPIO24": ("EV_N7_IR", "EXP_IR_TX_EVIDENCE_N")}
# Reviewed physical fixture, independent of the cloning procedure below.
PARTS = {
    BUFFER: ("EXP_U_C5_ISO", "safe_fault_reset_buffer", "ti_sn74lvc3g07_dcur", "SN74LVC3G07DCUR",
             "Package_SO:VSSOP-8_2.3x2mm_P0.5mm"),
    "exp_c5_rf_pullup": ("EXP_R_C5_RF", "c5_evidence_output_pullup", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL",
                         "Resistor_SMD:R_0402_1005Metric"),
    "exp_c5_ir_pullup": ("EXP_R_C5_IR", "c5_evidence_output_pullup", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL",
                         "Resistor_SMD:R_0402_1005Metric"),
    "exp_c5_iso_bypass": ("EXP_C_C5_ISO", "evidence_cmp_a_bypass", "yageo_cc0402krx7r9bb104", "Yageo CC0402KRX7R9BB104",
                          "Capacitor_SMD:C_0402_1005Metric"),
}
CONNECTIONS = {
    BUFFER: {"1A": ("1", "EV_N1_C5"), "1Y": ("7", "EXP_C5_RF_TX_EVIDENCE_N"),
             "2A": ("3", "EV_N7_IR"), "2Y": ("5", "EXP_IR_TX_EVIDENCE_N"),
             "3A": ("6", "POWER_GROUND"), "3Y": ("2", None),
             "VCC": ("8", "AON_SAFE_3V3"), "GND": ("4", "POWER_GROUND")},
    "exp_c5_rf_pullup": {"END_1": ("1", "3V3_MAIN"), "END_2": ("2", "EXP_C5_RF_TX_EVIDENCE_N")},
    "exp_c5_ir_pullup": {"END_1": ("1", "3V3_MAIN"), "END_2": ("2", "EXP_IR_TX_EVIDENCE_N")},
    "exp_c5_iso_bypass": {"END_1": ("1", "AON_SAFE_3V3"), "END_2": ("2", "POWER_GROUND")},
}
PARTS_MAIN_SCHMITT = {
    "exp_c5_rf_schmitt": ("EXP_U_C5_RF", "safe_rearm_buffer", "ti_sn74lvc1g17_dckr", "SN74LVC1G17DCKR",
                          "Package_TO_SOT_SMD:SOT-353_SC-70-5"),
    "exp_c5_ir_schmitt": ("EXP_U_C5_IR", "safe_rearm_buffer", "ti_sn74lvc1g17_dckr", "SN74LVC1G17DCKR",
                          "Package_TO_SOT_SMD:SOT-353_SC-70-5"),
    "exp_c5_rf_bypass": ("EXP_C_C5_RF", "evidence_cmp_a_bypass", "yageo_cc0402krx7r9bb104", "Yageo CC0402KRX7R9BB104",
                         "Capacitor_SMD:C_0402_1005Metric"),
    "exp_c5_ir_bypass": ("EXP_C_C5_IR", "evidence_cmp_a_bypass", "yageo_cc0402krx7r9bb104", "Yageo CC0402KRX7R9BB104",
                         "Capacitor_SMD:C_0402_1005Metric"),
}
CONNECTIONS_MAIN_SCHMITT = {
    "exp_c5_rf_schmitt": {"NC": ("1", None), "A": ("2", "EV_N1_C5"), "GND": ("3", "POWER_GROUND"),
                          "Y": ("4", "EXP_C5_RF_TX_EVIDENCE_N"), "VCC": ("5", "3V3_MAIN")},
    "exp_c5_ir_schmitt": {"NC": ("1", None), "A": ("2", "EV_N7_IR"), "GND": ("3", "POWER_GROUND"),
                          "Y": ("4", "EXP_IR_TX_EVIDENCE_N"), "VCC": ("5", "3V3_MAIN")},
    "exp_c5_rf_bypass": {"END_1": ("1", "3V3_MAIN"), "END_2": ("2", "POWER_GROUND")},
    "exp_c5_ir_bypass": {"END_1": ("1", "3V3_MAIN"), "END_2": ("2", "POWER_GROUND")},
}
VARIANTS = ("aon_open_drain", "main_schmitt")
UNRESOLVED = [
    "CMOS buffer input slew/transition limits: actual 10-kohm-pulled EV edges, shared capacitance and source-domain applicability are unproven",
    "Buffer output leakage plus MAIN rail discharge/clamping and resulting unpowered C5 pin voltage remain unbounded",
    "Buffer VIH/VIL, comparator VOL, loaded output VOL/VOH, pullup tolerance and LED/shared-load currents require exact source conditions",
    "AON/MAIN ramp, collapse, opposite-power states, startup and propagation/IRQ timing are not modeled",
    "No brightness, physical PCB/routing, assembly, factory availability or production MPN adoption is qualified",
]
UNRESOLVED_MAIN_SCHMITT = [
    "Exact Schmitt input levels/hysteresis, loaded EV voltage and added input leakage require source-condition review",
    "Exact powered-off input tolerance is source evidence only; input/output leakage, MAIN discharge and resulting C5 pin voltage remain unqualified",
    "Loaded output VOH/VOL, C5 input levels and propagation/IRQ timing remain unqualified",
    *UNRESOLVED[3:],
]


def require(condition, message):
    crossings.require(condition, message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def snapshot():
    # The core is an in-memory rewrite, not a compiler/native subprocess. The
    # optional CLI reuses route_board's existing keep_awake/cleanup helper.
    return {**crossings.snapshot(), str(Path(__file__).relative_to(ROOT)):
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "tools/route_board.py": hashlib.sha256((ROOT / "tools/route_board.py").read_bytes()).hexdigest(),
            **{str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in interface.source_paths()}}


def row_index(rows, field):
    result = {}
    for row in rows:
        key = (row["project"], row[field])
        require(key not in result, "duplicate candidate " + field)
        result[key] = row
    return result


def fixtures(variant):
    require(variant in VARIANTS, "unsupported fixed isolation variant")
    if variant == "main_schmitt":
        return PARTS_MAIN_SCHMITT, CONNECTIONS_MAIN_SCHMITT, {"c5.GPIO23": "exp_c5_rf_schmitt.A", "c5.GPIO24": "exp_c5_ir_schmitt.A"}
    return PARTS, CONNECTIONS, {"c5.GPIO23": BUFFER + ".1A", "c5.GPIO24": BUFFER + ".2A"}


def overlay_metadata(ledger, original, variant="aon_open_drain"):
    return {"artifact": "C5-isolation-experimental-" + ledger,
            "status": "experimental_nonproduction_candidate", "qualified": False,
            "scope": "in-memory ledger topology experiment; not regenerated native evidence",
            "baseline_artifact": original["artifact"], "baseline_ledger_semantic_sha256": digest(original),
            "experimental_origin": ORIGIN, "experimental_variant": variant}


def templates(data, reviews, variant="aon_open_drain"):
    parts, connections, _ = fixtures(variant)
    instances = data["instances"]["rows"]
    endpoints = data["nets"]["rows"]
    result = {}
    groups = {g["device_id"]: g for g in data["material"]["groups"]}
    for name, (_, seed, device_id, mpn, footprint) in parts.items():
        selected = [r for r in instances if r["instance"] == seed]
        require(len(selected) == 1 and all(selected[0].get(k) == v for k, v in
                (("device_id", device_id), ("mpn", mpn), ("footprint", footprint))), "candidate exact template identity differs")
        group = groups[device_id]
        require(group["mpn"] == mpn and group["footprint"] == footprint
                and data["devices"]["devices"][device_id]["mpn"] == mpn, "candidate template material/device differs")
        rows = [r for r in endpoints if (r["project"], r["instance"]) == (selected[0]["project"], seed)]
        require(len(rows) == len(connections[name]) and {r["contact"] for r in rows} == set(connections[name]), "candidate template contact coverage differs")
        material = {r["contact"]: r for r in group["contacts"]}
        for row in rows:
            physical = connections[name][row["contact"]][0]
            require(row["physical"] == physical and material[row["contact"]]["pads"] == [physical], "candidate exact pad mapping differs")
        result[name] = selected[0], rows
    if variant == "main_schmitt":
        part = parts["exp_c5_rf_schmitt"]
        expected_types = {"1": "no_connect", "2": "input", "3": "power_in", "4": "output", "5": "power_in"}
        function = "single non-inverting Schmitt-trigger buffer, Y=A"
        label = "Schmitt"
    else:
        part = parts[BUFFER]
        expected_types = {"1": "input", "2": "open_collector", "3": "input", "4": "power_in",
                          "5": "open_collector", "6": "input", "7": "open_collector", "8": "power_in"}
        function = "three non-inverting buffers with open-drain outputs"
        label = "open-drain"
    review = reviews.get(part[2], {})
    require(review.get("mpn") == part[3] and {p: r["type"] for p, r in review.get("pins", {}).items()} == expected_types,
            "candidate requires exact noninverting " + label + " pin review")
    require(data["devices"]["devices"][part[2]]["electrical_contract"]["function"] == function,
            "candidate polarity/function differs")
    return result


def make_candidate(data, reviews, variant="aon_open_drain"):
    parts, connections, _ = fixtures(variant)
    seeds = templates(data, reviews, variant)
    instance_names = {r["instance"] for r in data["instances"]["rows"]}
    references = {r["reference"] for r in data["instances"]["rows"]}
    nets = {r["net"] for r in data["nets"]["rows"]}
    require(not instance_names.intersection(parts) and not references.intersection(p[0] for p in parts.values())
            and not nets.intersection(pair[1] for pair in OUTPUTS.values()), "experimental name/reference/net collision")
    result = copy.deepcopy(data)
    for ledger in ("instances", "nets"):
        # Retain only the copied rows. Original sources/summary/status describe
        # the baseline, not newly generated native CAD or authoritative counts.
        result[ledger] = {**overlay_metadata(ledger, data[ledger], variant), "rows": result[ledger]["rows"]}
    for row in result["nets"]["rows"]:
        if row["project"] == PROJECT and row["endpoint"] in OUTPUTS:
            old, new = OUTPUTS[row["endpoint"]]
            require(row["net"] == old and row["disposition"] == "connected", "C5 baseline observation net differs")
            row["net"] = new
    for name, (reference, _, _, _, _) in parts.items():
        instance, rows = seeds[name]
        identity = {"project": PROJECT, "instance": name, "reference": reference, "sheet": SHEET}
        result["instances"]["rows"].append({**instance, **identity, "instance_uid": PROJECT + ":" + name, "allocation_origin": ORIGIN})
        for row in rows:
            net = connections[name][row["contact"]][1]
            result["nets"]["rows"].append({**row, **identity, "endpoint": name + "." + row["contact"],
                                         "net": net, "disposition": "connected" if net is not None else "no_connect", "origin": ORIGIN})
    return result


def validate_delta(baseline, candidate, reviews, variant="aon_open_drain"):
    parts, connections, inputs = fixtures(variant)
    seeds = templates(baseline, reviews, variant)
    for ledger in ("instances", "nets"):
        require({k: v for k, v in candidate[ledger].items() if k != "rows"} == overlay_metadata(ledger, baseline[ledger], variant),
                "candidate metadata cannot inherit native authority")
    for key in baseline.keys() - {"instances", "nets"}:
        require(candidate[key] == baseline[key], "candidate changed non-ledger input: " + key)
    old_instances = row_index(baseline["instances"]["rows"], "instance")
    new_instances = row_index(candidate["instances"]["rows"], "instance")
    old_pins = row_index(baseline["nets"]["rows"], "endpoint")
    new_pins = row_index(candidate["nets"]["rows"], "endpoint")
    require(set(new_instances) - set(old_instances) == {(PROJECT, name) for name in parts}
            and set(old_instances) <= set(new_instances), "candidate component delta differs")
    expected_pins = {(PROJECT, name + "." + contact) for name, rows in connections.items() for contact in rows}
    require(set(new_pins) - set(old_pins) == expected_pins and set(old_pins) <= set(new_pins), "candidate endpoint delta differs")
    for key, row in old_instances.items():
        require(new_instances[key] == row, "existing component changed: " + str(key))
    changed = []
    for key, row in old_pins.items():
        expected = copy.deepcopy(row)
        if key[0] == PROJECT and key[1] in OUTPUTS:
            require(row["net"] == OUTPUTS[key[1]][0], "C5 baseline observation differs")
            expected["net"] = OUTPUTS[key[1]][1]
            changed.append({"endpoint": key[1], "old_net": row["net"], "new_net": expected["net"]})
        require(new_pins[key] == expected, "existing endpoint changed: " + str(key))
    require(len(changed) == 2, "both original C5 observations required")
    for name, (reference, _, device_id, mpn, _) in parts.items():
        seed, seed_pins = seeds[name]
        identity = {"project": PROJECT, "instance": name, "reference": reference, "sheet": SHEET}
        expected = {**seed, **identity, "instance_uid": PROJECT + ":" + name, "allocation_origin": ORIGIN}
        require(new_instances[PROJECT, name] == expected, "new component exact metadata differs")
        for source in seed_pins:
            contact = source["contact"]
            _, net = connections[name][contact]
            expected = {**source, **identity, "endpoint": name + "." + contact, "net": net,
                        "disposition": "connected" if net is not None else "no_connect", "origin": ORIGIN}
            require(new_pins[PROJECT, name + "." + contact] == expected, "new component pad/net delta differs")
    # Explicit external-membership assertion protects the AON comparator, LED,
    # Safety/TCA and M1 networks, not merely the new buffer's local mapping.
    external = {}
    for endpoint, (old_net, new_net) in OUTPUTS.items():
        before = {key for key, row in old_pins.items() if row["net"] == old_net}
        after = {key for key, row in new_pins.items() if row["net"] == old_net}
        require(after == (before - {(PROJECT, endpoint)}) | {(PROJECT, inputs[endpoint])}, "external AON membership changed")
        external[old_net] = {"retained_original_endpoints": len(before) - 1, "added_buffer_input": inputs[endpoint]}
    crossings.indexes(candidate, reviews)  # Independent identity/contact checks.
    return {"added_components": 4, "added_endpoint_rows": 14, "changed_original_endpoints": changed,
            "unchanged_original_components": len(old_instances), "unchanged_original_endpoint_rows": len(old_pins) - 2,
            "added_bom": dict(sorted(Counter(parts[n][3] for n in parts).items())), "external_aon_membership": external,
            "original_u118_preserved": new_instances["LESHY2-RF-R2", "safe_fault_reset_buffer"] == old_instances["LESHY2-RF-R2", "safe_fault_reset_buffer"]}


def summarize_scan(report):
    return {key: report[key] for key in ("status", "qualified", "physical_rail_state_proven", "scanned_instances", "scanned_nets")} | {
        "potential_crossings": len(report["crossings"]), "unknown_supply_ownership": len(report["unknown_supply_ownership"]),
        "unreviewed_connected_endpoints": len(report["unreviewed_connected_pins"]),
        "crossing_receivers": [row["receiver"] for row in report["crossings"]]}


def validate_scan_delta(baseline, scan, variant="aon_open_drain"):
    parts, connections, inputs = fixtures(variant)
    crossings.validate_result(baseline)
    crossings.validate_result(scan)
    def key(row):
        receiver = row["receiver"]
        return receiver["project"], receiver["instance"], receiver["contact"]
    expected = {key(row): copy.deepcopy(row) for row in baseline["crossings"]}
    for endpoint, (old_net, _) in OUTPUTS.items():
        old_key = (PROJECT, "c5", endpoint.split(".")[1])
        require(old_key in expected, "baseline C5 crossing evidence missing")
        old = expected.pop(old_key)
        require(old["net"] == old_net, "baseline C5 crossing net differs")
        if variant == "main_schmitt":
            instance = inputs[endpoint].split(".")[0]
            reference, _, device_id, mpn, _ = parts[instance]
            old["receiver"] = {"project": PROJECT, "reference": reference, "instance": instance,
                               "contact": "A", "device_id": device_id, "mpn": mpn, "pads": ["2"],
                               "net": old_net, "type": "input"}
            old["receiver_supply"] = {"state": "commanded_off", "net": "3V3_MAIN", "domain": "3V3_MAIN", "contacts": ["VCC"]}
            # No new tolerance evidence is registered by a topology experiment.
            old.update(finding_kind="missing_off_state_tolerance", input_tolerance_evidence=[])
            expected[key(old)] = old
    require({key(row): row for row in scan["crossings"]} == expected, "crossing receiver/source delta differs")
    # Existing pin-review maps intentionally leave capacitors unreviewed; do
    # not fabricate a passive review merely because the recipe adds bypasses.
    expected_unreviewed = copy.deepcopy(baseline["unreviewed_connected_pins"])
    for instance, (reference, _, device_id, mpn, _) in parts.items():
        if device_id == "yageo_cc0402krx7r9bb104":
            for contact, (pad, net) in connections[instance].items():
                expected_unreviewed.append({"project": PROJECT, "reference": reference, "instance": instance,
                                            "contact": contact, "device_id": device_id, "mpn": mpn,
                                            "pads": [pad], "net": net, "type": "unreviewed"})
    require(scan["unreviewed_connected_pins"] == expected_unreviewed, "unreviewed endpoint delta differs")
    excluded = {"crossings", "scanned_instances", "scanned_nets", "unreviewed_connected_pins"}
    require({k: v for k, v in scan.items() if k not in excluded} == {k: v for k, v in baseline.items() if k not in excluded},
            "unrelated crossing result changed")
    require(scan["scanned_instances"] == baseline["scanned_instances"] + 4
            and scan["scanned_nets"] == baseline["scanned_nets"] + 2, "candidate scan coverage differs")


def validate_reviewed_scan(raw, reviewed, variant, proofs):
    parts, _, inputs = fixtures(variant)
    crossings.validate_result(raw)
    crossings.validate_result(reviewed)
    expected = copy.deepcopy(raw)
    if variant == "main_schmitt":
        require(len(proofs) == 1 and proofs[0]["device_id"] == parts["exp_c5_rf_schmitt"][2]
                and proofs[0]["mpn"] == parts["exp_c5_rf_schmitt"][3] and proofs[0]["pads"] == ["2"]
                and proofs[0]["supply_contacts"] == ["VCC"], "unexpected Schmitt off-input evidence")
        targets = {(PROJECT, endpoint.split(".")[0], "A") for endpoint in inputs.values()}
        changed = set()
        for row in expected["crossings"]:
            pin = row["receiver"]
            key = pin["project"], pin["instance"], pin["contact"]
            if key in targets:
                require(row["finding_kind"] == "missing_off_state_tolerance" and row["input_tolerance_evidence"] == [],
                        "raw Schmitt scan must remain source-uncredited")
                row.update(finding_kind="off_state_input_evidence_requires_voltage_review", input_tolerance_evidence=[proofs[0]])
                changed.add(key)
        require(changed == targets, "reviewed Schmitt receivers missing")
    else:
        require(not proofs, "unexpected open-drain off-input evidence")
    require(reviewed == expected, "source-reviewed crossing delta differs")


def build(variant="aon_open_drain"):
    fixtures(variant)
    before = snapshot()
    data = {key: crossings.load(ROOT / path) for key, path in crossings.INPUTS.items()}
    contracts = {key: crossings.load(ROOT / path) for key, path in crossings.LEDGER_CONTRACTS.items()}
    crossings.validate_provenance(data, contracts, before)
    reviews = crossings.semantics.reviewed_maps([crossings.load(p) for p in crossings.semantics.MAPS], data["material"]["groups"])
    state = crossings.state_snapshot()
    baseline = crossings.evaluate(data, reviews, state, crossings.OFF_INPUT_PROOFS, before)
    proofs = interface.off_input_proofs(variant)
    original_hash = digest(data)
    hashes, results = [], []
    for _ in range(2):
        candidate = make_candidate(data, reviews, variant)
        delta = validate_delta(data, candidate, reviews, variant)
        scan = crossings.evaluate(candidate, reviews, state, crossings.OFF_INPUT_PROOFS, before)
        crossings.validate_result(scan)
        source_reviewed = crossings.evaluate(candidate, reviews, state, (*crossings.OFF_INPUT_PROOFS, *proofs), before)
        validate_reviewed_scan(scan, source_reviewed, variant, proofs)
        source_screen = interface.review_candidate(candidate, reviews, variant)
        require(source_screen.get("qualified") is False, "interface source screen cannot qualify the candidate")
        hashes.append(digest(candidate))
        results.append((delta, scan, source_reviewed, source_screen))
    require(hashes[0] == hashes[1] and results[0] == results[1], "candidate deterministic replay differs")
    require(digest(data) == original_hash, "candidate mutated baseline inputs")
    delta, scan, source_reviewed, source_screen = results[0]
    validate_scan_delta(baseline, scan, variant)
    require(snapshot() == before, "candidate source inputs changed during experiment")
    schmitt = variant == "main_schmitt"
    return {"variant": variant, "status": "not_qualified", "mechanics_status": "pass", "qualified": False, "production_promoted": False,
            "fabrication_authorized": False, "native_candidate_generated": False, "source_sha256": before,
            "source_hash_scope": "Input provenance only; not a regenerated candidate native export or physical source proof",
            "baseline": summarize_scan(baseline), "candidate": summarize_scan(scan), "delta": delta,
            "source_screen": source_screen, "source_reviewed_crossing_scan": source_reviewed,
            "crossing_scan_scope": "baseline/candidate use identical raw graph evidence; source_reviewed_crossing_scan separately credits exact input-source evidence, never bounds loaded voltage or grants qualification",
            "deterministic_replay": {"runs": 2, "pass": True, "candidate_semantic_sha256": hashes},
            "scope": "In-memory ledger topology experiment only; no native CAD generation, electrical solver or production writes",
            "crossing_count_interpretation": "Finding count is neither an electrical ranking nor a qualification metric; MAIN Schmitt moves the two receiver findings, it does not clear them",
            "selection_status": "unqualified_pending_levels_leakage_power_sequences" if schmitt else "not_selected_slew_and_output_leakage_unqualified",
            "selection_reason": "Not selected for production: loaded levels, leakage and power sequences unresolved" if schmitt else
                                "Not selected for production: input slew and powered-on output leakage/MAIN-off voltage unresolved",
            "unresolved": list(UNRESOLVED_MAIN_SCHMITT if schmitt else UNRESOLVED)}


def main(argv=None):
    from tools.route_board import keep_awake
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, default="aon_open_drain")
    args = parser.parse_args(argv)
    def interrupted(signum, frame):
        raise KeyboardInterrupt("C5 candidate experiment cancelled")
    previous = signal.signal(signal.SIGTERM, interrupted)
    try:
        work = ROOT / "work"
        require(work.is_dir() and not work.is_symlink(), "existing real work directory required")
        directory = Path(tempfile.mkdtemp(prefix="c5-isolation-candidate-", dir=work))
        started, awake = time.monotonic(), {}
        with keep_awake(awake, directory) as power:
            report = build(args.variant)
            require(power is None or power.poll() is None, "idle-sleep assertion ended during experiment")
        require(snapshot() == report["source_sha256"], "candidate source inputs changed before report publication")
        report.update(caffeinate=awake, elapsed_s=round(time.monotonic() - started, 3))
        path = directory / "result.json"
        with path.open("x") as output:
            json.dump(report, output, indent=2, sort_keys=True)
            output.write("\n")
        print(json.dumps({"variant": args.variant, "status": report["status"], "mechanics_status": report["mechanics_status"],
                          "potential_crossings_before": report["baseline"]["potential_crossings"],
                          "potential_crossings_after": report["candidate"]["potential_crossings"],
                          "qualified": False, "report": str(path)}))
        return 1
    except (Exception, KeyboardInterrupt) as error:
        cancelled = isinstance(error, KeyboardInterrupt)
        print(json.dumps({"status": "cancelled" if cancelled else "execution_error", "qualified": False,
                          "report": None, "error": f"{type(error).__name__}: {error}"}))
        return 130 if cancelled else 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
