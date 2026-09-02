#!/usr/bin/env python3
"""Validate the fail-closed H5.0.3-R1 supplier-response gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
INPUT = REPO / "hardware/procurement/H5.0.3-R1-supplier-response.json"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR07-supplier-response-gate.json"

J4_F_IDS = {
    "display_flex",
    "microcoax_x5",
    "encoder_knob",
    "sandwich_enclosure",
    "whole_device_test",
}
J4_P_IDS = {"u214_test_and_pack", "antenna_kit"}
OUT_OF_SUPPLIER_SCOPE_IDS = {"protected_cells"}
FORBIDDEN_AUTHORITY = {
    "quote_project",
    "reservation",
    "sourcing_request",
    "purchase",
    "component_replacement",
    "pcb_placement_and_routing",
    "fabrication",
}


def present(value: object) -> bool:
    return value is not None and value != ""


def operation_completeness(row: dict) -> tuple[list[str], bool]:
    missing: list[str] = []
    if row.get("required_for_release") is not True:
        return missing, True
    if not isinstance(row.get("accepted"), bool):
        missing.append(f"{row.get('id', '<unknown>')}.accepted")
        return missing, False
    if row["accepted"] is False:
        return missing, False
    if not isinstance(row.get("required_fixtures_or_files"), list):
        missing.append(f"{row['id']}.required_fixtures_or_files")
    return missing, row["accepted"]


def build(source: dict | None = None) -> dict:
    if source is None:
        source = json.loads(INPUT.read_text(encoding="utf-8"))
    if source.get("schema_version") != 1 or source.get("gate") != "H5.0.3-R1":
        raise ValueError("supplier response schema or gate identity drifted")
    if source.get("status") not in {"waiting_for_supplier_response", "response_recorded"}:
        raise ValueError("supplier response status drifted")

    j4_f = source.get("j4_f_operations", [])
    j4_p_all = source.get("j4_p_operations", [])
    j4_p = [row for row in j4_p_all if row.get("in_supplier_scope", True)]
    out_of_scope = [row for row in j4_p_all if not row.get("in_supplier_scope", True)]
    if {row.get("id") for row in j4_f} != J4_F_IDS or len(j4_f) != len(J4_F_IDS):
        raise ValueError("J4-F operation set drifted")
    if {row.get("id") for row in j4_p} != J4_P_IDS or len(j4_p) != len(J4_P_IDS):
        raise ValueError("J4-P operation set drifted")
    if {row.get("id") for row in out_of_scope} != OUT_OF_SUPPLIER_SCOPE_IDS:
        raise ValueError("out-of-supplier-scope operation set drifted")
    required_j4_f = [row for row in j4_f if row.get("required_for_release") is True]
    optional_operations = [row for row in j4_f + j4_p if row.get("required_for_release") is False]
    if {row.get("id") for row in required_j4_f} != {
        "display_flex", "microcoax_x5", "encoder_knob", "sandwich_enclosure"
    }:
        raise ValueError("release-required final-assembly operation set drifted")
    if {row.get("id") for row in optional_operations} != {
        "whole_device_test", "u214_test_and_pack", "antenna_kit"
    }:
        raise ValueError("optional operation set drifted")
    if set(source.get("authorization", {})) != FORBIDDEN_AUTHORITY:
        raise ValueError("authorization boundary drifted")

    missing: list[str] = []
    supplier = source["supplier"]
    for field in ("received_on", "source_reference"):
        if not present(supplier.get(field)):
            missing.append(f"supplier.{field}")

    clarification = source.get("clarification", {})
    clarification_sent = (
        clarification.get("sent_on") == "2026-09-01"
        and clarification.get("from") == "vinogradov.anton@gmail.com"
        and clarification.get("to") == "support@jlcpcb.com"
        and clarification.get("result") == "message_sent"
        and clarification.get("information_only") is True
        and clarification.get("commercial_action_created") is False
    )
    display_psa = source.get("display_psa_clarification", {})
    display_psa_clarification_sent = (
        display_psa.get("sent_on") == "2026-09-01"
        and display_psa.get("from") == "vinogradov.anton@gmail.com"
        and display_psa.get("to") == "support@jlcpcb.com"
        and display_psa.get("result") == "message_sent"
        and display_psa.get("exact_mpn") == "3M (TC) 4910SQ-2(5)"
        and display_psa.get("source_reference") == "hardware/procurement/H5.0.3-R1-jlcpcb-display-psa-clarification.md"
        and display_psa.get("information_only") is True
        and display_psa.get("commercial_action_created") is False
    )
    merge = source.get("ticket_merge_notice", {})
    administrative_merge_recorded = (
        merge.get("received_on") == "2026-09-02"
        and merge.get("result") == "clarification_request_closed_and_merged"
        and merge.get("merged_into_ticket") == "TKEM2026082605925"
        and merge.get("source_reference") == "hardware/procurement/H5.0.3-R1-jlcpcb-ticket-merge-2026-09-02.md"
        and merge.get("substantive_release_answer") is False
        and merge.get("commercial_action_created") is False
    )
    substantive = source.get("substantive_clarification_response", {})
    substantive_response_recorded = (
        substantive.get("received_on") == "2026-09-02"
        and substantive.get("from") == "support@jlcpcb.com"
        and substantive.get("to") == "av@apache.org"
        and substantive.get("viewed_in_gmail_account") == "no.mail.in@gmail.com"
        and substantive.get("result") == "partial_acceptance_with_required_final_assembly_decline"
        and substantive.get("source_reference") == "hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md"
        and substantive.get("information_only") is True
        and substantive.get("commercial_action_created") is False
    )
    pcba_order = source.get("pcba_order", {})
    pcba_order_boundary_recorded = (
        pcba_order.get("minimum_quantity_pieces") == 2
        and pcba_order.get("online_orders_only") is True
        and pcba_order.get("special_process_feasibility_confirmed_before_order") is False
    )

    voice = source["sa818s_v"]
    exact_voice_identity = voice.get("mpn") == "SA818S-V" and voice.get("jlcpcb_part") == "C51897911"
    for field in ("standard_pcba_installation", "sample_lead_time_days", "moq"):
        if not present(voice.get(field)):
            missing.append(f"sa818s_v.{field}")
    voice_values_valid = (
        isinstance(voice.get("standard_pcba_installation"), bool)
        and isinstance(voice.get("sample_lead_time_days"), int)
        and not isinstance(voice.get("sample_lead_time_days"), bool)
        and voice.get("sample_lead_time_days", 0) > 0
        and isinstance(voice.get("moq"), int)
        and not isinstance(voice.get("moq"), bool)
        and voice.get("moq", 0) >= 1
    )

    dual = source["dual_module_job"]
    exact_dual_identity = dual.get("sa818s_u_mpn") == "SA818S-U" and dual.get("sa818s_u_jlcpcb_part") == "C3001549"
    for field in ("accepted",):
        if not isinstance(dual.get(field), bool):
            missing.append(f"dual_module_job.{field}")

    j4_f_accepted = True
    for row in required_j4_f:
        row_missing, accepted = operation_completeness(row)
        missing.extend(f"j4_f_operations.{item}" for item in row_missing)
        j4_f_accepted = j4_f_accepted and accepted

    battery = source["battery_shipping"]
    battery_out_of_scope = battery.get("supply_scope") is False and battery.get("user_supplied") is True
    if not battery_out_of_scope:
        for field in ("procure_and_ship_same_parcel", "destination_restrictions", "required_compliance_documents", "separate_shipment_required"):
            if not present(battery.get(field)):
                missing.append(f"battery_shipping.{field}")
    battery_complete = battery_out_of_scope or (
        isinstance(battery.get("procure_and_ship_same_parcel"), bool)
        and isinstance(battery.get("destination_restrictions"), list)
        and isinstance(battery.get("required_compliance_documents"), list)
        and isinstance(battery.get("separate_shipment_required"), bool)
    )

    identity = source["identity_control"]
    for field in ("exact_external_mpns_controlled_at_incoming_inspection", "silent_substitution_prohibited", "exceptions"):
        if not present(identity.get(field)):
            missing.append(f"identity_control.{field}")
    identity_complete = (
        isinstance(identity.get("exact_external_mpns_controlled_at_incoming_inspection"), bool)
        and isinstance(identity.get("silent_substitution_prohibited"), bool)
        and isinstance(identity.get("exceptions"), list)
    )

    if source["status"] != "response_recorded":
        missing.append("status=response_recorded")
    response_complete = not missing and voice_values_valid and battery_complete and identity_complete
    explicit_declines = [
        f"J4-F:{row['id']}" for row in required_j4_f if row.get("accepted") is False
    ]
    all_factory_gates_accepted = (
        voice.get("standard_pcba_installation") is True
        and dual.get("accepted") is True
        and j4_f_accepted
        and identity.get("exact_external_mpns_controlled_at_incoming_inspection") is True
        and identity.get("silent_substitution_prohibited") is True
        and not identity.get("exceptions")
    )
    no_new_authority = all(value is False for value in source["authorization"].values())
    gate_passed = response_complete and exact_voice_identity and exact_dual_identity and all_factory_gates_accepted and clarification_sent and display_psa_clarification_sent and substantive_response_recorded and no_new_authority

    blockers: list[str] = []
    if missing:
        blockers.append("supplier response is incomplete")
    if explicit_declines:
        blockers.append("supplier explicitly declines: " + ", ".join(explicit_declines))
    if response_complete and not all_factory_gates_accepted:
        blockers.append("supplier explicitly declines or qualifies at least one required factory gate")
    if not exact_voice_identity or not exact_dual_identity:
        blockers.append("exact selected module identity is not preserved")
    if not no_new_authority:
        blockers.append("the response record cannot authorize commercial, layout or fabrication actions")

    return {
        "schema_version": 1,
        "artifact": "H5-EVR07",
        "gate": "H5.0.3-R1",
        "source": str(INPUT.relative_to(REPO)),
        "source_status": source["status"],
        "status": "passed_supplier_gate" if gate_passed else ("supplier_gate_failed_explicit_required_decline" if explicit_declines else ("complete_response_gate_failed" if response_complete else ("partial_response_gate_open" if source["status"] == "response_recorded" else "waiting_for_complete_supplier_response"))),
        "summary": {
            "response_complete": response_complete,
            "factory_gate_passed": gate_passed,
            "missing_field_count": len(missing),
            "explicit_decline_count": len(explicit_declines),
            "out_of_supplier_scope_operations": len(out_of_scope),
            "j4_f_operations": len(j4_f),
            "j4_p_operations": len(j4_p),
            "release_required_final_assembly_operations": len(required_j4_f),
            "optional_non_gating_operations": len(optional_operations),
            "orders_authorized": 0,
        },
        "checks": {
            "exact_sa818s_v_identity_preserved": exact_voice_identity,
            "exact_sa818s_u_identity_preserved": exact_dual_identity,
            "release_relevant_and_optional_operations_are_machine_separated": len(required_j4_f) == 4 and len(optional_operations) == 3 and len(out_of_scope) == 1,
            "exact_one_clarification_sent_without_commercial_action": clarification_sent,
            "exact_display_psa_clarification_sent_without_commercial_action": display_psa_clarification_sent,
            "administrative_ticket_merge_recorded_without_closing_the_gate": administrative_merge_recorded,
            "substantive_response_address_and_scope_recorded": substantive_response_recorded,
            "pcba_moq_and_post_order_special_process_boundary_recorded": pcba_order_boundary_recorded,
            "commercial_layout_and_fabrication_authority_remains_false": no_new_authority,
            "response_complete": response_complete,
            "all_required_factory_gates_accepted": all_factory_gates_accepted,
        },
        "missing_fields": sorted(set(missing)),
        "explicit_declines": explicit_declines,
        "blockers": blockers,
        "authorization": source["authorization"],
        "next": ("use PCBWay as the active full-device candidate; retain JLCPCB as the PCBA-only reference" if explicit_declines else ("wait for a substantive supplier response in merged ticket TKEM2026082605925" if clarification_sent and display_psa_clarification_sent and administrative_merge_recorded and not response_complete else ("wait for the supplier response to the exact-one and display-PSA clarifications" if clarification_sent and display_psa_clarification_sent and not response_complete else ("send the prepared exact-one and exact display-PSA clarifications without authorizing a commercial action" if not response_complete else ("prepare the separate cost/order decision" if gate_passed else "compare an alternate factory or revise the declined required operation boundary"))))),
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale generated artifact: {OUTPUT.relative_to(REPO)}")
        print("ok: H5 supplier response gate is current and fail-closed")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
