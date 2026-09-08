"""Current H3 power applicability, separate from provisional arithmetic.

Known analytical failures are publishable diagnostics. Malformed inputs and I/O
errors are not caught here. Exact check scopes belong to this current-H3 path;
this does not authorize a phase, hardware operation or manufacturing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = {
    "H3-R2-rail-margins": ("main_raw_model", "main_protection_model", "main_thermal_model", "aon_ron_model", "series_distribution_scope"),
    "H3-R2-source-margins": ("rail_inputs", "source_model_binding"),
    "H3-R2-dc-source-crosscheck": ("rail_inputs", "source_inputs"),
    "H3-R2-transition-sequences": ("dc_inputs", "supervisor_assertion_bound", "supervisor_hysteresis_bound"),
    "H3-R2-handover": ("source_inputs", "sequence_inputs"),
    "H3-R2-inrush-watchdog": ("rail_inputs", "sequence_inputs", "handover_inputs"),
    "H3-R2-transition-result": ("inrush_inputs", "sequence_inputs", "handover_inputs"),
    "H3-R2-analog-corners": ("rail_inputs",),
    "H3-R2-digital-interfaces": ("rail_inputs",),
    "H3-R2-rf-coexistence": ("digital_inputs", "analog_inputs"),
    "H3-R2-thermal-fault": ("rail_inputs", "source_inputs", "transition_inputs", "rf_inputs"),
    "H3-R2-crosscheck": ("current_power_inputs",),
    "H3-R2-physical-residuals": ("crosscheck_inputs",),
    "H3-R2-acceptance-package": ("crosscheck_inputs",),
}


# Exact current producers and direct consumed sources. This list is code-reviewed,
# not inferred from the artifact being admitted; deleting matching outer/proof
# hash entries therefore cannot erase a required dependency.
PRODUCERS = {
    "H3-R2-rail-margins": "hardware/verification/h3_r2_rail_margins.py",
    "H3-R2-source-margins": "hardware/verification/h3_r2_source_margins.py",
    "H3-R2-dc-source-crosscheck": "hardware/verification/h3_r2_dc_source_crosscheck.py",
    "H3-R2-transition-sequences": "hardware/verification/h3_r2_transition_sequences.py",
    "H3-R2-handover": "hardware/verification/h3_r2_handover.py",
    "H3-R2-inrush-watchdog": "hardware/verification/h3_r2_inrush_watchdog.py",
    "H3-R2-transition-result": "hardware/verification/h3_r2_inrush_watchdog.py",
    "H3-R2-analog-corners": "hardware/verification/h3_r2_analog_corners.py",
    "H3-R2-digital-interfaces": "hardware/verification/h3_r2_digital_interfaces.py",
    "H3-R2-rf-coexistence": "hardware/verification/h3_r2_rf_coexistence.py",
    "H3-R2-thermal-fault": "hardware/verification/h3_r2_thermal_fault.py",
    "H3-R2-crosscheck": "hardware/verification/h3_r2_crosscheck.py",
    "H3-R2-physical-residuals": "hardware/verification/h3_r2_crosscheck.py",
    "H3-R2-acceptance-package": "hardware/verification/h3_r2_crosscheck.py"
}
DIRECT_SOURCES = {
    "H3-R2-rail-margins": (
        "hardware/verification/h3-r2-rail-margin-contract.json",
        "hardware/verification/generated/H3-R2-load-binding.json",
        "hardware/verification/generated/H3-R2-power-state-register.json",
        "hardware/verification/generated/H3-R2-method-contract.json",
        "hardware/architecture/h0-r2-rebaseline.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/architecture/devices.json",
    ),
    "H3-R2-source-margins": (
        "hardware/verification/h3-r2-source-margin-contract.json",
        "hardware/verification/generated/H3-R2-power-state-register.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-load-binding.json",
        "hardware/verification/generated/H3-R2-method-contract.json",
    ),
    "H3-R2-dc-source-crosscheck": (
        "hardware/verification/generated/H3-R2-method-contract.json",
        "hardware/verification/generated/H3-R2-power-state-register.json",
        "hardware/verification/generated/H3-R2-load-binding.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-source-margins.json",
        "hardware/verification/h3-r2-verification-plan.json",
    ),
    "H3-R2-transition-sequences": (
        "hardware/verification/h3-r2-transition-sequence-contract.json",
        "hardware/verification/h3-r2-verification-plan.json",
        "hardware/verification/generated/H3-R2-input-freeze.json",
        "hardware/verification/generated/H3-R2-method-contract.json",
        "hardware/verification/generated/H3-R2-dc-source-crosscheck.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/ecad/generated/H2-R2-interboard-m1.json",
        "hardware/architecture/devices.json",
    ),
    "H3-R2-handover": (
        "hardware/verification/h3-r2-handover-contract.json",
        "hardware/verification/h3-r2-verification-plan.json",
        "hardware/verification/generated/H3-R2-source-margins.json",
        "hardware/verification/generated/H3-R2-transition-sequences.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/architecture/devices.json",
    ),
    "H3-R2-inrush-watchdog": (
        "hardware/verification/h3-r2-inrush-watchdog-contract.json",
        "hardware/verification/h3-r2-verification-plan.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-transition-sequences.json",
        "hardware/verification/generated/H3-R2-handover.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/architecture/devices.json",
    ),
    "H3-R2-transition-result": (
        "hardware/verification/generated/H3-R2-transition-sequences.json",
        "hardware/verification/generated/H3-R2-handover.json",
        "hardware/verification/generated/H3-R2-inrush-watchdog.json",
    ),
    "H3-R2-analog-corners": (
        "hardware/architecture/candidates/G2F-3I.json",
        "hardware/architecture/devices.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-parameter-provenance.json",
        "hardware/verification/generated/H3-VRF32-audio.json",
        "hardware/verification/generated/H3-VRF33-ir.json",
        "hardware/verification/generated/H3-VRF34-battery-analog.json",
        "hardware/verification/generated/H3-R2-airband-corners.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/product-design/generated/H1-R2-cost-audit.json",
        "hardware/product-design/display-mount.json",
    ),
    "H3-R2-digital-interfaces": (
        "hardware/architecture/h0-r2-rebaseline.json",
        "hardware/architecture/devices.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/ecad/generated/H2-R2-native-net-ledger.json",
        "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
        "hardware/product-design/display-mount.json",
    ),
    "H3-R2-rf-coexistence": (
        "hardware/architecture/candidates/G2F-3I.json",
        "hardware/architecture/devices.json",
        "hardware/architecture/antenna-kit.json",
        "hardware/product-design/generated/H1-R2-placement-audit.json",
        "hardware/verification/generated/H3-R2-power-state-register.json",
        "hardware/verification/generated/H3-R2-digital-interfaces.json",
        "hardware/verification/generated/H3-R2-analog-corners.json",
        "hardware/verification/generated/H3-R2-parameter-provenance.json",
    ),
    "H3-R2-thermal-fault": (
        "hardware/architecture/candidates/G2F-3I.json",
        "hardware/architecture/devices.json",
        "hardware/verification/generated/H3-R2-method-contract.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-source-margins.json",
        "hardware/verification/generated/H3-R2-transition-result.json",
        "hardware/verification/generated/H3-R2-inrush-watchdog.json",
        "hardware/verification/generated/H3-VRF34-battery-analog.json",
        "hardware/verification/generated/H3-R2-rf-coexistence.json",
        "hardware/ecad/generated/H2-REV55-fault-kill.json",
    ),
    "H3-R2-crosscheck": (
        "hardware/verification/h3-r2-verification-plan.json",
        "hardware/verification/generated/H3-R2-input-freeze.json",
        "hardware/verification/generated/H3-R2-parameter-provenance.json",
        "hardware/verification/generated/H3-R2-method-contract.json",
        "hardware/verification/generated/H3-R2-power-state-register.json",
        "hardware/verification/generated/H3-R2-load-binding.json",
        "hardware/verification/generated/H3-R2-rail-margins.json",
        "hardware/verification/generated/H3-R2-source-margins.json",
        "hardware/verification/generated/H3-R2-dc-source-crosscheck.json",
        "hardware/verification/generated/H3-R2-transition-sequences.json",
        "hardware/verification/generated/H3-R2-handover.json",
        "hardware/verification/generated/H3-R2-inrush-watchdog.json",
        "hardware/verification/generated/H3-R2-transition-result.json",
        "hardware/verification/generated/H3-VRF32-audio.json",
        "hardware/verification/generated/H3-VRF33-ir.json",
        "hardware/verification/generated/H3-VRF34-battery-analog.json",
        "hardware/verification/generated/H3-R2-airband-corners.json",
        "hardware/verification/generated/H3-R2-analog-corners.json",
        "hardware/verification/generated/H3-R2-digital-interfaces.json",
        "hardware/verification/generated/H3-R2-rf-coexistence.json",
        "hardware/verification/generated/H3-R2-thermal-fault.json",
    ),
    "H3-R2-physical-residuals": (
        "hardware/verification/generated/H3-R2-crosscheck.json",
    ),
    "H3-R2-acceptance-package": (
        "hardware/verification/generated/H3-R2-crosscheck.json",
        "hardware/verification/generated/H3-R2-physical-residuals.json",
    ),
}


def required_sources(artifact):
    return set(DIRECT_SOURCES[artifact]) | {PRODUCERS[artifact],
        "hardware/verification/h3_r2_current_scope.py"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _proof(artifact, numerical_ok, applicability):
    expected = REQUIREMENTS[artifact]
    findings = []
    if type(numerical_ok) is not bool:
        findings.append("numerical:missing_explicit_result")
    elif not numerical_ok:
        findings.append("numerical:existing_checks")
    if set(applicability) != set(expected):
        findings.append("applicability:required_check_scope_mismatch")
    for key in expected:
        if applicability.get(key) is not True:
            findings.append("applicability:" + key)
    safe = {key: value if type(value) is bool else None for key, value in applicability.items()}
    return {"schema_version": 1, "artifact": artifact,
            "status": "review_required" if findings else "pass",
            "numerical_status": "provisional_pass" if numerical_ok is True else "provisional_fail",
            "numerical_checks_pass": numerical_ok if type(numerical_ok) is bool else None,
            "applicability_checks": safe, "open_findings": findings,
            "current_analytical_scope_complete": not findings,
            "production_release_authorized": False, "battery_energization_authorized": False}


def apply_scope(result, producer, applicability, *, numerical_ok=None):
    """Mutate the current result before serializing it, preserving algebra rows."""
    previous_errors = list(result.get("errors", []))
    if numerical_ok is None:
        numerical_ok = not previous_errors
    proof = _proof(result["artifact"], numerical_ok, applicability)
    field = next((key for key in ("source_sha256", "source_hashes", "sources") if key in result), "source_sha256")
    sources = dict(result.get(field, {}))
    for path in (Path(producer), Path(__file__)):
        sources[str(path.resolve().relative_to(ROOT))] = digest(path)
    result[field] = sources
    proof["source_sha256"] = dict(sources)
    result["current_power_scope"] = proof
    result["provisional_numerical_errors"] = previous_errors
    result["errors"] = previous_errors + proof["open_findings"]
    result["status"] = proof["status"]
    result["current_analytical_scope_complete"] = proof["current_analytical_scope_complete"]
    result["open_analytical_findings"] = list(proof["open_findings"])
    result["production_release_authorized"] = False
    result["battery_energization_authorized"] = False
    # An analytical review is not permission to advance or energize. Existing
    # numerical rows/counters remain provisional, with an explicit open count.
    result["authorization"] = {key: False for key in result.get("authorization", {})}
    result["authorization"].update(advance_phase=False, fabrication=False, purchasing=False,
                                   battery_energization=False, final_product_claim=False)
    if "summary" in result:
        result["summary"]["open_analytical_findings"] = len(proof["open_findings"])
        if "analytical_findings_open" in result["summary"]:
            result["summary"]["analytical_findings_open"] = len(proof["open_findings"])
    return result


def admits_current(result, artifact):
    """Reject old plausible PASS, stale evidence, omitted checks and false closure."""
    if not isinstance(result, dict) or result.get("artifact") != artifact or result.get("status") != "pass":
        return False
    proof = result.get("current_power_scope")
    if not isinstance(proof, dict) or artifact not in REQUIREMENTS:
        return False
    sources = proof.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        return False
    if not required_sources(artifact).issubset(sources):
        return False
    field = next((key for key in ("source_sha256", "source_hashes", "sources") if key in result), "source_sha256")
    if result.get(field) != sources:
        return False
    for relative, expected in sources.items():
        if not isinstance(relative, str) or not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
            return False
        path = ROOT / relative
        if Path(relative).is_absolute() or ".." in Path(relative).parts or not path.is_file() or digest(path) != expected:
            return False
    applicability = proof.get("applicability_checks")
    if not isinstance(applicability, dict):
        return False
    rebuilt = _proof(artifact, proof.get("numerical_checks_pass"), applicability)
    rebuilt["source_sha256"] = sources
    if rebuilt["status"] != "pass" or json.dumps(proof, sort_keys=True) != json.dumps(rebuilt, sort_keys=True):
        return False
    return (result.get("current_analytical_scope_complete") is True
            and result.get("production_release_authorized") is False
            and result.get("battery_energization_authorized") is False
            and result.get("errors") == [] and result.get("open_analytical_findings") == []
            and bool(result.get("authorization")) and all(value is False for value in result["authorization"].values()))


def scope_notice(result, russian=False):
    link = f"\n\n[{'Машинное evidence' if russian else 'Machine evidence'}](../hardware/verification/generated/{result['artifact']}.json)."
    findings = result.get("errors", [])
    detail = ("\n\n" + ("Открыто: " if russian else "Open: ") + "; ".join(f"`{item}`" for item in findings) + ".") if findings else ""
    if russian:
        return ("**Текущий статус: `" + result["status"] + "`.** Численные и логические проверки ниже сохранены "
                "как предварительные. Применимость к установленной ячейке питания проверяется отдельно; открытые "
                "аналитические вопросы не заменены физическими испытаниями. Переход фазы, закупка, изготовление "
                "и питание от аккумуляторов не разрешены этим результатом." + detail + link)
    return ("**Current status: `" + result["status"] + "`.** Numerical and logical checks below are retained as "
            "provisional. Applicability to the fitted power cell is checked separately; open analytical findings "
            "are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, "
            "fabrication or battery energization." + detail + link)
