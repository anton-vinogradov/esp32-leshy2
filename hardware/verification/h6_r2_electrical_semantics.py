#!/usr/bin/env python3
"""Run reviewed pin types in isolated native KiCad copies, never hide open ERC findings."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MATERIAL = ROOT / "hardware/ecad/generated/H2-R2-contact-materialization.json"
INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
MAP_NAMES = ("power", "digital", "logic", "analog", "protection", "interfaces", "passives", "peripherals")
MAPS = [ROOT / f"hardware/verification/h6-electrical-pins-{name}.json" for name in MAP_NAMES]
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")
OUTPUT = ROOT / "hardware/verification/generated/H6-R2-electrical-semantics.json"
TYPES = {"input", "output", "bidirectional", "tri_state", "passive", "power_in", "power_out", "open_collector", "open_emitter", "no_connect"}
# KiCad's documented Symbol Pin styles. A style controls drawing, not whether
# the electrical type gets reviewed: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html
PIN_SHAPES = {"line", "inverted", "clock", "inverted_clock", "input_low", "clock_low", "output_low", "edge_clock_high", "non_logic"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_paths():
    paths = [Path(__file__), MATERIAL, INSTANCES, *MAPS, ROOT / "hardware/ecad/libraries/leshy2_r2.kicad_sym"]
    for project in PROJECTS:
        directory = ROOT / "hardware/ecad/kicad" / project
        paths.extend(sorted(directory.glob("*.kicad_sch")))
        paths.append(directory / f"{project}.kicad_pro")
        paths.extend(directory / name for name in ("sym-lib-table", "fp-lib-table"))
    return paths


def source_hashes():
    return {str(path.relative_to(ROOT)): digest(path) for path in source_paths()}


def reviewed_maps(fragments, groups):
    """Unknown devices, absent pads, duplicate reviews and unsupported types fail closed."""
    known = {group["device_id"]: group for group in groups}
    reviews = {}
    for fragment in fragments:
        if fragment.get("schema_version") != 1:
            raise ValueError("unsupported electrical review schema")
        for row in fragment["devices"]:
            device = row["device_id"]
            if device not in known or device in reviews:
                raise ValueError(f"unknown or duplicate reviewed device: {device}")
            if row["mpn"] != known[device]["mpn"]:
                raise ValueError(f"exact MPN mismatch: {device}")
            evidence = row.get("evidence", [])
            if not evidence or any(not all(item.get(key) for key in ("url", "section", "checked")) for item in evidence):
                raise ValueError(f"incomplete primary evidence: {device}")
            pads = set(known[device]["pad_inventory"])
            for pin, spec in row["pins"].items():
                if pin not in pads or spec.get("type") not in TYPES or not spec.get("reason"):
                    raise ValueError(f"invalid reviewed pad/type/reason: {device}.{pin}")
            reviews[device] = row
    return reviews


def matching_paren(text, start):
    depth, quoted, escaped = 0, False, False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unterminated KiCad expression")


def apply_reviewed_types(text, reviews, *, required_devices=()):
    """Change only cached symbol pin-type tokens; keep pins, wires, UUIDs and names intact."""
    replacements = []
    openings = unquoted_openings(text)
    cached_devices = set()
    for match in re.finditer(r'\(\s*symbol\s+"Leshy2_R2:([^"\\]+)"', text):
        if match.start() not in openings:
            continue
        review = reviews.get(match.group(1))
        if review is None:
            continue
        device = match.group(1)
        if device in cached_devices:
            raise ValueError(f"duplicate reviewed symbol cache: {device}")
        cached_devices.add(device)
        end = matching_paren(text, match.start())
        symbol = text[match.start():end]
        seen_pads = set()
        applied_pads = set()
        for pin_match in re.finditer(r'\(\s*pin\b', symbol):
            if match.start() + pin_match.start() not in openings:
                continue
            pin_end = matching_paren(symbol, pin_match.start())
            pin_text = symbol[pin_match.start():pin_end]
            header = re.match(r'\(\s*pin\s+(\w+)\s+(\w+)\b', pin_text)
            if header is None or header.group(1) not in TYPES | {"free", "unspecified"} or header.group(2) not in PIN_SHAPES:
                raise ValueError(f"unsupported cached pin type/style: {device}")
            numbers = [number for number in re.finditer(r'\(\s*number\s+"([^"\\]+)"', pin_text)
                       if match.start() + pin_match.start() + number.start() in openings]
            if len(numbers) != 1:
                raise ValueError("cached library pin has no unique number")
            number = numbers[0].group(1)
            # Current exact symbols have one physical occurrence per number.
            # Future stacked/multi-unit pins need explicit support, not double counting.
            if number in seen_pads:
                raise ValueError(f"duplicate cached physical pin: {device}.{number}")
            seen_pads.add(number)
            spec = review["pins"].get(number)
            if spec:
                applied_pads.add(number)
                replacements.append((match.start()+pin_match.start()+header.start(1), match.start()+pin_match.start()+header.end(1), spec["type"]))
        if applied_pads != set(review["pins"]):
            raise ValueError(f"reviewed pads absent from cached symbol {device}: {sorted(set(review['pins']) - applied_pads)}")
    if set(required_devices) - cached_devices:
        raise ValueError(f"required reviewed symbol cache is absent: {sorted(set(required_devices) - cached_devices)}")
    for start, end, value in sorted(replacements, reverse=True):
        text = text[:start] + value + text[end:]
    return text, len(replacements)


def typed_source_sheets(project, instances, reviews):
    """Check every reviewed instance has its complete, actually typed local cache."""
    source = ROOT / "hardware/ecad/kicad" / project
    for path in sorted(source.glob("*.kicad_sch")):
        required = {row["device_id"] for row in instances
                    if row["project"] == project and row["sheet"] == path.stem and row["device_id"] in reviews}
        content, count = apply_reviewed_types(path.read_text(encoding="utf-8"), reviews, required_devices=required)
        yield path, content, count


def unquoted_openings(text):
    quoted, escaped = False, False
    openings = set()
    for index, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            openings.add(index)
    return openings


def net_membership(path):
    root = ET.parse(path).getroot()
    nets = root.find("nets")
    if nets is None:
        raise ValueError("native XML contains no nets")
    nodes = {}
    for net in nets:
        for node in net.findall("node"):
            key = (node.attrib["ref"], node.attrib["pin"])
            if key in nodes:
                raise ValueError(f"duplicate native node {key}")
            nodes[key] = net.attrib["name"]
    return nodes


def direct_net_findings(nodes, instances, reviews):
    """Screen direct native nets only; absent direct source is not proof of an unpowered rail."""
    by_ref = {row["reference"]: row for row in instances}
    typed = defaultdict(list)
    for (ref, pin), net in nodes.items():
        instance = by_ref.get(ref)
        if instance is None:
            raise ValueError(f"native reference absent from instance ledger: {ref}")
        spec = reviews.get(instance["device_id"], {}).get("pins", {}).get(pin)
        if spec:
            typed[net].append({"reference": ref, "instance": instance["instance"], "pin": pin, "type": spec["type"], "reason": spec["reason"]})
    results = []
    for net, pins in sorted(typed.items()):
        sources = [p for p in pins if p["type"] == "power_out"]
        inputs = [p for p in pins if p["type"] == "power_in"]
        push_pull = [p for p in pins if p["type"] == "output"]
        if len(push_pull) > 1:
            results.append({"kind": "multiple_push_pull_outputs", "net": net, "pins": push_pull, "status": "requires_review"})
        if inputs and not sources:
            results.append({"kind": "no_direct_reviewed_power_output", "net": net, "pins": inputs, "status": "requires_source_path_review"})
    return results


def command(args):
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    if result.returncode:
        raise ValueError(f"KiCad command failed ({result.returncode}): {result.stdout[-2000:]}")


def review_coverage(groups, reviews):
    missing = []
    for group in groups:
        pads = sorted(set(group["pad_inventory"]) - set(reviews.get(group["device_id"], {}).get("pins", {})))
        if pads:
            missing.append({"device_id": group["device_id"], "pins": pads})
    return {"reviewed_devices": len(reviews), "device_count": len(groups),
            "reviewed_unique_pins": sum(len(row["pins"]) for row in reviews.values()), "unreviewed": missing}


def content_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_audit(audit, groups, reviews, expected_hashes, expected_counts, expected_sheets):
    """Validate saved partial evidence, never reinterpret --check as ERC acceptance.

    This detects stale/incomplete evidence without rerunning KiCad. It is not a
    signature against intentional forgery; fresh --write is the native rerun.
    """
    if audit.get("source_hashes") != expected_hashes:
        raise ValueError("electrical-semantics evidence is stale; rerun the isolated native review")
    if (audit.get("schema_version"), audit.get("marker"), audit.get("gate"), audit.get("status")) != (1, "H6.0.3-R1", "H6-NATIVE-ELECTRICAL-SEMANTICS", "review_required"):
        raise ValueError("electrical-semantics audit must retain its exact partial-review status")
    if audit.get("authorization") != {"fabrication": False, "gate_closed": False}:
        raise ValueError("this partial review must not close the production gate")
    if audit.get("coverage") != review_coverage(groups, reviews):
        raise ValueError("electrical-semantics coverage does not match current reviewed maps")
    unresolved = [{"device_id": device, "finding": finding} for device, review in reviews.items() for finding in review.get("unresolved", [])]
    if audit.get("source_review_findings") != unresolved:
        raise ValueError("electrical-semantics source findings are missing or changed")
    projects = audit.get("projects")
    if not isinstance(projects, list) or len(projects) != len(PROJECTS) or {row.get("project") for row in projects} != set(PROJECTS):
        raise ValueError("electrical-semantics audit must contain both distinct native projects")
    for row in projects:
        project = row["project"]
        if row.get("cached_pin_types_reviewed") != expected_counts[project] or expected_counts[project] <= 0:
            raise ValueError(f"{project}: applied cached-pin coverage is incomplete")
        if row.get("native_connectivity_unchanged") is not True:
            raise ValueError(f"{project}: unchanged native connectivity was not verified")
        if type(row.get("physical_netlist_nodes")) is not int or row["physical_netlist_nodes"] <= 0:
            raise ValueError(f"{project}: missing physical native netlist evidence")
        if any(not isinstance(row.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", row[key])
               for key in ("native_xml_sha256", "typed_xml_sha256", "erc_report_sha256")):
            raise ValueError(f"{project}: missing native evidence digest")
        report = row.get("native_erc")
        if not isinstance(report, dict) or report.get("$schema") != "https://schemas.kicad.org/erc.v1.json" or report.get("source") != f"{project}.kicad_sch":
            raise ValueError(f"{project}: missing or wrong native ERC report")
        if not all(report.get(key) for key in ("date", "kicad_version", "coordinate_units")) or set(report.get("included_severities", [])) != {"error", "warning", "exclusion"}:
            raise ValueError(f"{project}: native ERC metadata or severities are incomplete")
        if row.get("erc_content_sha256") != content_digest(report):
            raise ValueError(f"{project}: saved native ERC content changed")
        sheets = report.get("sheets")
        if not isinstance(sheets, list) or not sheets or len(sheets) != len(expected_sheets[project]) or {sheet.get("path") for sheet in sheets} != set(expected_sheets[project]):
            raise ValueError(f"{project}: native ERC sheet coverage is incomplete")
        violations = []
        for sheet in sheets:
            if not sheet.get("uuid_path") or not isinstance(sheet.get("violations"), list):
                raise ValueError(f"{project}: malformed native ERC sheet")
            for violation in sheet["violations"]:
                if not violation.get("type") or violation.get("severity") not in {"error", "warning", "exclusion"} or not violation.get("description") or not isinstance(violation.get("items"), list):
                    raise ValueError(f"{project}: malformed native ERC violation")
            violations.extend(sheet["violations"])
        if row.get("erc_count_by_type") != dict(Counter(item["type"] for item in violations)):
            raise ValueError(f"{project}: native ERC count does not match retained findings")
        if not isinstance(row.get("direct_net_findings"), list):
            raise ValueError(f"{project}: direct-net findings are absent")


def build():
    before = source_hashes()
    material = load(MATERIAL)
    instances = load(INSTANCES)["rows"]
    reviews = reviewed_maps([load(path) for path in MAPS], material["groups"])
    cli = shutil.which("kicad-cli") or "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    project_results = []
    expected_counts, expected_sheets = {}, {}
    with tempfile.TemporaryDirectory(prefix="leshy2-typed-erc-") as directory:
        temporary = Path(directory)
        for project in PROJECTS:
            source = ROOT / "hardware/ecad/kicad" / project
            shadow = temporary / project
            shadow.mkdir()
            count = 0
            sheet_paths = []
            for path, content, changed in typed_source_sheets(project, instances, reviews):
                (shadow / path.name).write_text(content, encoding="utf-8")
                count += changed
                sheet_paths.append("/" if path.stem == project else f"/{path.stem}/")
            expected_counts[project], expected_sheets[project] = count, sheet_paths
            # Preserve actual library resolution rather than turning missing-library
            # warnings off merely because the review runs in a temporary directory.
            for name in ("sym-lib-table", "fp-lib-table"):
                content = (source / name).read_text(encoding="utf-8").replace("${KIPRJMOD}", str(source))
                (shadow / name).write_text(content, encoding="utf-8")
            settings = load(source / f"{project}.kicad_pro")
            # No historical ignored ERC findings or pin-conflict overrides enter the review.
            # Cached symbols intentionally differ only in their reviewed types.
            settings["erc"] = {"rule_severities": {"lib_symbol_mismatch": "ignore"}}
            (shadow / f"{project}.kicad_pro").write_text(json.dumps(settings), encoding="utf-8")
            native_xml, shadow_xml = shadow / "original.xml", shadow / "typed.xml"
            for sch, output in ((source / f"{project}.kicad_sch", native_xml), (shadow / f"{project}.kicad_sch", shadow_xml)):
                command([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(output), str(sch)])
            native_nodes, typed_nodes = net_membership(native_xml), net_membership(shadow_xml)
            if native_nodes != typed_nodes:
                raise ValueError(f"{project}: typed review altered native connectivity")
            report_path = shadow / "erc.json"
            command([cli, "sch", "erc", "--format", "json", "--severity-all", "-o", str(report_path), str(shadow / f"{project}.kicad_sch")])
            report = load(report_path)
            if not isinstance(report.get("sheets"), list):
                raise ValueError("incomplete native ERC report")
            violations = [violation for sheet in report["sheets"] for violation in sheet.get("violations", [])]
            project_results.append({
                "project": project, "cached_pin_types_reviewed": count,
                "native_connectivity_unchanged": True, "physical_netlist_nodes": len(native_nodes),
                "native_xml_sha256": digest(native_xml), "typed_xml_sha256": digest(shadow_xml),
                "erc_report_sha256": digest(report_path), "erc_content_sha256": content_digest(report), "native_erc": report,
                "erc_count_by_type": dict(sorted(Counter(row["type"] for row in violations).items())),
                "direct_net_findings": direct_net_findings(native_nodes, [row for row in instances if row["project"] == project], reviews),
            })
    if source_hashes() != before:
        raise ValueError("electrical review inputs changed during native verification")
    audit = {
        "schema_version": 1, "marker": "H6.0.3-R1", "gate": "H6-NATIVE-ELECTRICAL-SEMANTICS",
        "status": "review_required", "source_hashes": before,
        "method": "reviewed exact-part pin types applied only to isolated native KiCad copies; original and typed XML memberships must be identical; native ERC findings retained without suppression",
        "coverage": review_coverage(material["groups"], reviews),
        "source_review_findings": [{"device_id": device, "finding": finding} for device, review in reviews.items() for finding in review.get("unresolved", [])],
        "projects": project_results,
        "limits": ["not a completed physical-pin mapping review", "unreviewed pins retain original types and are not counted as verified", "no-direct-source findings require series-component, converter-dependency and M1 path review; they are not proof of missing power", "GPIO directions, tri-state enables and open-drain pullups require configuration-aware review", "native production library remains unchanged until the reviewed mapping and all findings are reconciled"],
        "authorization": {"fabrication": False, "gate_closed": False},
    }
    validate_audit(audit, material["groups"], reviews, before, expected_counts, expected_sheets)
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        audit = build()
        OUTPUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        audit = load(OUTPUT)
        before = source_hashes()
        if audit.get("source_hashes") != before:
            raise ValueError("electrical-semantics evidence is stale; rerun the isolated native review")
        groups, instances = load(MATERIAL)["groups"], load(INSTANCES)["rows"]
        reviews = reviewed_maps([load(path) for path in MAPS], groups)
        counts, sheets = {}, {}
        for project in PROJECTS:
            typed = list(typed_source_sheets(project, instances, reviews))
            counts[project] = sum(count for _, _, count in typed)
            sheets[project] = ["/" if path.stem == project else f"/{path.stem}/" for path, _, _ in typed]
        validate_audit(audit, groups, reviews, before, counts, sheets)
        if source_hashes() != before:
            raise ValueError("electrical review inputs changed during evidence validation")
    print(f"H6 electrical semantics: {audit['status']}; {audit['coverage']['reviewed_devices']} reviewed devices; native evidence bound to current inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
