#!/usr/bin/env python3
"""Read-only adapters for bounded native layout and assembly acceptance.

Importing this registry never imports pcbnew. Native checks run only through
run_check(), under KiCad Python, and never call an existing writer/main().
Scoped geometry evidence is not complete physical or manufacturing acceptance.
"""
from __future__ import annotations

import hashlib
import importlib
from contextlib import redirect_stdout
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PROJECTS = {"LESHY2-UI-R2", "LESHY2-RF-R2"}
CHECKS = {
    "footprint-parity": {
        "runtime": "kicad",
        "scope": "Current native pad metadata and effective copper polygons on every copper layer versus selected libraries, with 0.001-mm curve tessellation; excludes mask/paste aperture parity, manufacturer qualification and electrical pin semantics.",
    },
    "mechanical-stack": {
        "runtime": "kicad",
        "scope": "Current mounting axes, fastener tolerances and NTC placement, with separate unresolved mechanical release coverage.",
    },
    "microcoax": {
        "runtime": "kicad",
        "scope": "Current nominal cable corridors, slack and planar radius, with separate unresolved source-window and assembled 3D coverage.",
    },
    "silkscreen": {
        "runtime": "kicad",
        "scope": "Native functional labels and supported same-side ink/mask/body screening; excludes complete plotted manufacturing output.",
    },
    "sma-access": {
        "runtime": "kicad",
        "scope": "Native SMA lands, foreign-pad contact and bounded planar access screening; excludes solder process and 3D tool access.",
    },
}


def _module(name):
    directory = str(Path(__file__).resolve().parent)
    sys.path.insert(0, directory)
    try:
        return importlib.import_module(name)
    finally:
        sys.path.remove(directory)


def _result(check_id, verdict, findings=(), **details):
    return {"verdict": verdict, "scope": CHECKS[check_id]["scope"],
            "findings": [str(value) for value in findings], "details": details}


def _project_rows(report):
    rows = report["boards"]
    if len(rows) != 2 or {row["project"] for row in rows} != PROJECTS:
        raise ValueError("exactly one current UI board and one RF board are required")
    return rows


def _verify_source_hashes(report, required, root=ROOT):
    """A cached dependency is usable only with its full expected source set."""
    sources = report.get("source_hashes", {})
    if not sources or set(sources) != set(required):
        raise ValueError("cached dependency source-hash inventory is incomplete or changed")
    for relative, expected in sources.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("cached dependency source escapes the repository")
        if (not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected):
            raise ValueError(f"stale cached dependency source: {relative}")


def _fresh_placement():
    """Recompute placement authority and bind it to BOTH actual routed PCBs.

    The existing builder creates temporary scratch boards, never saves outputs
    into the repository. Its entire placement report must match the stored
    dependency; native signatures retain pads/keepouts/setup and omit routing.
    """
    bindings = _module("h6_r2_kicad_net_bindings")
    errors = bindings.check()
    if errors:
        raise ValueError("stale native net bindings: " + "; ".join(errors[:8]))
    placement = _module("h6_r2_placement")
    outputs, audit = placement.build()
    if audit["status"] != "pass" or audit["errors"]:
        raise ValueError("current placement authority fails: " + "; ".join(audit["errors"][:8]))
    if placement.AUDIT_PATH.read_bytes() != outputs[placement.AUDIT_PATH]:
        raise ValueError("cached placement report differs from fresh current-source evaluation")
    for row in _project_rows(audit):
        path = ROOT / f"hardware/ecad/kicad/{row['project']}/{row['project']}.kicad_pcb"
        if row["output"] != str(path.relative_to(ROOT)):
            raise ValueError("placement output does not identify the current native PCB")
        native = placement.pcbnew.LoadBoard(str(path))
        signature = hashlib.sha256(placement.placement_signature_bytes(row["project"], native)).hexdigest()
        if signature != row["placement_signature_sha256"]:
            raise ValueError(f"current native placement signature differs: {row['project']}")
    errors = _module("h6_r2_placement_freeze").verify()
    if errors:
        raise ValueError("native placement freeze differs: " + "; ".join(errors[:8]))
    return audit


def _footprint_result(report):
    summary = report["summary"]
    findings = list(report["errors"])
    for board in _project_rows(report):
        if (not board["native_footprint_count"]
                or board["native_footprint_count"] != len(set(board["checked_references"]))):
            findings.append(f"{board['project']}: incomplete native footprint coverage")
        findings.extend(f"{board['project']}:{row['reference']}: native/library pad geometry drift"
                        for row in board["deviations"])
    valid = (report["status"] == "pass" and not findings
             and summary["native_footprints"] == summary["checked_footprints"]
             and summary["footprints_with_pad_geometry_drift"] == 0
             and summary["lookup_errors"] == 0)
    if not valid and not findings:
        findings.append("native/library parity status or coverage does not pass")
    return _result("footprint-parity", "pass" if valid else "fail", findings,
                   **summary, manufacturer_geometry_qualified=False,
                   source_library_sha256=report["source_library_sha256"],
                   native_board_sha256={row["board"]: row["board_sha256"] for row in report["boards"]},
                   copper_polygon_error_mm=report["copper_polygon_error_mm"])


def _mechanical_result(report):
    findings = list(report["errors"])
    if (findings or report["status"] not in {"pass", "review_required"}
            or report["fastener_and_planar_checks_status"] != "pass"):
        return _result("mechanical-stack", "fail", findings or ["fastener/planar checks do not pass"],
                       scoped_verdict="fail")
    # This adapter has no complete assembled-solid/FPC qualification method.
    # A future production_ready flag alone cannot close that coverage gap.
    findings.append("Complete opposing-body, enclosure and display/FPC assembly qualification is absent")
    if report["battery_thermal_contacts"].get("physical_contact_proved") is not True:
        findings.append("Cell-to-NTC height/contact/compression qualification remains open")
    if report["connector_fit"]["status"] != "pass":
        findings.append("SMA slot versus finished-PCB thickness fit remains open")
    return _result("mechanical-stack", "unqualified", findings,
                   scoped_verdict="pass", mounting_axis_count=report["geometry"]["mounting_axis_count"],
                   connector_fit=report["connector_fit"]["status"],
                   physical_contact_proved=report["battery_thermal_contacts"].get("physical_contact_proved") is True,
                   complete_assembly_qualified=False)


def _microcoax_result(report):
    summary = report["summary"]
    if report["status"] != "pass" or report["errors"] or summary["path_count"] != 5:
        return _result("microcoax", "fail", report["errors"] or ["nominal five-path cable scope does not pass"],
                       scoped_verdict="fail")
    findings = ["Combined 3D bends, opposing bodies and physical service access are not qualified"]
    if summary.get("all_source_positions_planar_radius_verified") is not True:
        findings.append("Planar radius/clearance is not verified across every admitted source-window position")
    return _result("microcoax", "unqualified", findings, scoped_verdict="pass",
                   path_count=summary["path_count"],
                   minimum_relaxed_reserve_mm=summary["minimum_relaxed_reserve_mm"],
                   all_source_positions_planar_radius_verified=summary.get("all_source_positions_planar_radius_verified") is True,
                   complete_assembly_qualified=False)


def _silkscreen_result(report):
    boards = _project_rows(report)
    errors = list(report["interface_coverage"]["errors"])
    for board in boards:
        errors.extend(f"{board['project']}: {error}" for error in board["errors"])
        if board["required_count"] <= 0 or board["matched_count"] != board["required_count"]:
            errors.append(f"{board['project']}: required label coverage incomplete")
    candidates = sum(len(board["geometry_candidates"]) for board in boards)
    if errors or report["status"] not in {"pass_scoped", "review_required"}:
        verdict = "fail"
        errors = errors or ["native silkscreen status does not pass"]
    elif candidates or report["status"] == "review_required":
        verdict = "unqualified"
        errors.append(f"{candidates} conservative geometry candidates require resolution")
    else:
        verdict = "pass"
    return _result("silkscreen", verdict, errors, geometry_candidate_count=candidates,
                   required_labels=sum(board["required_count"] for board in boards),
                   plotted_manufacturing_output_qualified=False)


def _sma_result(report):
    summary = report["summary"]
    errors = [f"{board['project']}: {error}" for board in _project_rows(report) for error in board["errors"]]
    if summary["connector_count"] != 10 or summary["pad_count"] != 50:
        errors.append("native SMA coverage must include ten connectors and fifty lands")
    if report["geometry_error_count"] or summary["native_foreign_pad_contact_count"]:
        errors.append("SMA geometry errors or native foreign-pad contacts remain")
    if errors or report["status"] not in {"no_candidates_in_screened_scope", "review_required"}:
        verdict = "fail"
        errors = errors or ["native SMA screening status does not pass"]
    elif summary["screening_candidate_count"] or report["status"] == "review_required":
        verdict = "unqualified"
        errors.append(f"{summary['screening_candidate_count']} planar access candidates require resolution")
    else:
        verdict = "pass"
    return _result("sma-access", verdict, errors, **summary,
                   solder_process_qualified=False, three_dimensional_access_qualified=False)


def _run_check(check_id):
    if check_id not in CHECKS:
        raise ValueError(f"unknown layout acceptance check: {check_id}")
    try:
        if check_id == "footprint-parity":
            return _footprint_result(_module("h6_r2_footprint_parity").build())
        if check_id == "silkscreen":
            return _silkscreen_result(_module("h6_r2_silkscreen_audit").build())
        if check_id == "sma-access":
            return _sma_result(_module("h6_r2_sma_solder_access").build())
        placement = _fresh_placement()
        if check_id == "mechanical-stack":
            module = _module("h6_r2_mechanical_stack")
            return _mechanical_result(module.evaluate(module.load(module.CONTRACT), placement))
        module = _module("h6_r2_microcoax_service")
        h3 = module.load(module.H3)
        required = {
            "hardware/architecture/candidates/G2F-3I.json", "hardware/architecture/devices.json",
            "hardware/architecture/antenna-kit.json", "hardware/product-design/generated/H1-R2-placement-audit.json",
            *(f"hardware/verification/generated/H3-R2-{name}.json" for name in
              ("power-state-register", "digital-interfaces", "analog-corners", "parameter-provenance")),
            "hardware/verification/h3_r2_rf_coexistence.py", "hardware/verification/h3_r2_current_scope.py",
        }
        _verify_source_hashes(h3, required)
        return _microcoax_result(module.evaluate(module.load(module.CONTRACT), placement,
                                module.load(module.PLACEMENT_CONTRACT), module.load(module.H1), h3))
    except (Exception, SystemExit) as exc:
        return _result(check_id, "fail", [f"{type(exc).__name__}: {exc}"],
                       prerequisite_error=True)


def run_check(check_id):
    """Return fresh evidence without writes or incidental output on stdout.

    Keep sibling modules available during evaluation as well as import: some
    established auditors intentionally defer their helper imports until build.
    """
    directory = str(Path(__file__).resolve().parent)
    sys.path.insert(0, directory)
    try:
        with redirect_stdout(sys.stderr):
            return _run_check(check_id)
    finally:
        sys.path.remove(directory)
