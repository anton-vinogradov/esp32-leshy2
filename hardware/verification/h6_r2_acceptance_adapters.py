#!/usr/bin/env python3
"""Read-only acceptance adapters; valid review evidence is not design approval.

These adapters reuse the existing electrical auditors without running KiCad or
rewriting their evidence. A failed bounded prerequisite is distinct from a
missing qualification. None of the current partial reviews proves the
complete electrical design, even when its evidence is internally consistent.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path

from hardware.verification import h6_r2_electrical_semantics as semantics
from hardware.verification import h6_r2_electrical_source_triage as triage
from hardware.verification import h6_r2_power_startup as power
from hardware.verification import h6_r2_power_domain_crossings as crossings


ROOT = Path(__file__).resolve().parents[2]
CHECKS = {
    "electrical.power_domain_crossings": {
        "title": "AON-only potential live-to-unpowered input paths",
        "runtime": "python",
        "scope": "Native direct-drive/pullup exposure in the commanded AON-live/MAIN-off snapshot; no measured rail state, loaded pin voltage or damage claim.",
        "sources": ["hardware/verification/h6_r2_power_domain_crossings.py"],
    },
    "electrical.power_startup": {
        "title": "Native AON/MAIN power prerequisites",
        "runtime": "python",
        "scope": "Exact AON/MAIN source topology and conditioned prerequisite screens; not startup, rail or PCB qualification.",
        "sources": ["hardware/verification/h6_r2_power_startup.py"],
    },
    "electrical.source_triage": {
        "title": "Electrical source-path triage",
        "runtime": "python",
        "scope": "Fresh bounded explanations of retained typed ERC findings; not rail reachability or electrical clearance.",
        "sources": ["hardware/verification/h6_r2_electrical_source_triage.py"],
    },
    "electrical.typed_erc": {
        "title": "Typed native ERC evidence",
        "runtime": "python",
        "scope": "Current hashes, exact reviewed pin types and saved isolated native ERC; no fresh native execution or complete pin/configuration proof.",
        "sources": ["hardware/verification/h6_r2_electrical_semantics.py"],
    },
}


def source_paths(check_id: str) -> list[Path]:
    """Discover actual source inventory, never trust a saved audit's file list."""
    metadata = CHECKS[check_id]
    paths = {Path(__file__), *(ROOT / path for path in metadata["sources"])}
    if check_id == "electrical.power_startup":
        paths.update(ROOT / path for path in power.INPUTS.values())
        paths.update(ROOT / "hardware/verification" / filename for filename in
                     ("h6_power_corner_math.py", "h3_r2_current_scope.py"))
    elif check_id == "electrical.power_domain_crossings":
        paths.update(crossings.source_paths())
    else:
        paths.update(semantics.source_paths())
        paths.add(semantics.OUTPUT)
        # Both adapters reuse this module's full native-audit validator.
        paths.add(ROOT / "hardware/verification/h6_r2_electrical_source_triage.py")
        if check_id == "electrical.source_triage":
            paths.update(ROOT / path for path in triage.REQUIRED_SOURCES)
            paths.add(ROOT / triage.TRIAGE)
    return sorted(paths)


def _snapshot(check_id: str) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_paths(check_id)}


def _native_audit() -> dict:
    """Run the complete saved-evidence check using freshly discovered hashes."""
    before = semantics.source_hashes()
    audit = semantics.load(semantics.OUTPUT)
    material = semantics.load(semantics.MATERIAL)
    triage.validate_native_audit(semantics, audit, before, material)
    if semantics.source_hashes() != before:
        raise ValueError("electrical inputs changed during native evidence validation")
    return audit


def _typed_erc() -> tuple[str, list[str], dict]:
    audit = _native_audit()
    coverage = audit["coverage"]
    counts = Counter()
    for project in audit["projects"]:
        counts.update(project["erc_count_by_type"])
    missing_pins = sum(len(row["pins"]) for row in coverage["unreviewed"])
    findings = [f"{sum(counts.values())} native ERC findings remain unsuppressed."]
    if missing_pins:
        findings.append(f"{missing_pins} physical pin types across {len(coverage['unreviewed'])} device types remain unreviewed.")
    findings.append("Configuration-dependent pin behavior and supply-source paths remain unqualified.")
    return "unqualified", findings, {
        "evidence_status": "current_and_validated",
        "upstream_status": audit["status"],
        "reviewed_devices": coverage["reviewed_devices"],
        "device_count": coverage["device_count"],
        "reviewed_unique_pins": coverage["reviewed_unique_pins"],
        "unreviewed_pin_count": missing_pins,
        "erc_counts": dict(sorted(counts.items())),
        "source_review_finding_count": len(audit["source_review_findings"]),
        "native_execution": False,
        "gate_closed": False,
    }


def _source_triage() -> tuple[str, list[str], dict]:
    audit = _native_audit()
    native_sources = {str(path.relative_to(ROOT)) for path in semantics.source_paths()}
    sources = triage.REQUIRED_SOURCES | native_sources
    hashes = {path: triage.digest_relative(path) for path in sources}
    review = triage.load(triage.TRIAGE)
    result = triage.validate(review, audit, triage.load(triage.LEDGER),
                             triage.load(triage.MATERIAL), hashes)
    return "unqualified", [
        "Source paths and exact identities are validated; all retained native findings remain open.",
        "Source presence, converter startup, switched states, drops and bootstrap behavior are not qualified.",
    ], {"evidence_status": "current_and_validated", "upstream_status": review["status"], **result}


_BOUNDED_POWER_CHECKS = {
    "aon_vset_configuration", "main_feedback_target", "rilm_matches_accepted_h1",
    "h3_current_limit_bound_to_fitted_rilm", "main_pf03_current_reserve",
    "main_h0_step_floor", "main_efuse_high_below_buck_limit",
    "main_existing_inrush_model_headroom", "main_pg_resistor_only_window_feasible",
}


def _power_failure_kind(row: dict) -> str:
    """Classify only known screens; a new/unknown obligation is unqualified."""
    ident, observed = row["id"], row.get("observed") or {}
    if ident.startswith(("identity:", "pin:", "path:")) or ident in _BOUNDED_POWER_CHECKS:
        return "fail"
    if ident == "h3_converter_source_is_installed_part":
        if any(observed.get(key) is False for key in
               ("native_identity_matches", "declared_operating_domain_is_supported")):
            return "fail"
    elif ident == "main_pg_assertion_headroom":
        if observed.get("sense_node_matches") is False:
            return "fail"
        if (observed.get("provisional_protected_local_min_v") is not None
                and observed.get("numerical_headroom_only") is False):
            return "fail"
    elif ident == "aon_ron_test_condition_binding":
        if observed.get("reviewed_table_max_ohm") is not None:
            return "fail"
    return "unqualified"


def _power_startup() -> tuple[str, list[str], dict]:
    result = power.build()
    power.validate_result(result)
    failed = [row for row in result["checks"] if not row["pass"]]
    hard = [row["id"] for row in failed if _power_failure_kind(row) == "fail"]
    unknown = [row["id"] for row in failed if _power_failure_kind(row) == "unqualified"]
    findings = [f"{_power_failure_kind(row)}: {row['id']}: {row['detail']}" for row in failed]
    findings.append("Startup remains unproven even if all bounded prerequisites become consistent.")
    return "fail" if hard else "unqualified", findings, {
        "evidence_status": "recomputed_and_validated",
        "upstream_status": result["status"],
        "check_count": len(result["checks"]),
        "passed_check_count": len(result["checks"]) - len(failed),
        "failed_prerequisites": hard,
        "unqualified_prerequisites": unknown,
        "unproven_obligation_count": len(result["unproven"]),
        "startup_proven": False,
        "gate_closed": False,
    }


def _power_domain_crossings() -> tuple[str, list[str], dict]:
    result = crossings.build()
    crossings.validate_result(result)
    findings = [f"{row['finding_kind']}: {row['receiver']['project']}:{row['receiver']['reference']} "
                f"{row['receiver']['contact']} on {row['net']}" for row in result["crossings"]]
    if result["unknown_supply_ownership"]:
        findings.append(f"{len(result['unknown_supply_ownership'])} exposed input supply-domain assignments remain unknown.")
    findings.append("This commanded-state connectivity screen does not qualify rail states, input voltages, leakage or the complete circuit.")
    return "unqualified", findings, {"evidence_status": "recomputed_and_validated", **result}


_RUNNERS = {
    "electrical.power_domain_crossings": _power_domain_crossings,
    "electrical.power_startup": _power_startup,
    "electrical.source_triage": _source_triage,
    "electrical.typed_erc": _typed_erc,
}


def run_check(check_id: str) -> dict:
    """Return bounded verdicts; evidence corruption is never an electrical PASS."""
    metadata = CHECKS[check_id]
    try:
        before = _snapshot(check_id)
        verdict, findings, details = _RUNNERS[check_id]()
        if _snapshot(check_id) != before:
            raise ValueError("acceptance inputs changed during validation")
    except (FileNotFoundError, KeyError) as error:
        verdict, findings = "unqualified", [f"Required electrical evidence is missing: {error}"]
        details = {"evidence_status": "missing_required_data", "gate_closed": False}
    except (ValueError, TypeError) as error:
        verdict, findings = "fail", [f"Electrical evidence or prerequisite validation failed: {error}"]
        details = {"evidence_status": "invalid_or_stale", "gate_closed": False}
    return {"verdict": verdict, "scope": metadata["scope"], "findings": findings, "details": details}
