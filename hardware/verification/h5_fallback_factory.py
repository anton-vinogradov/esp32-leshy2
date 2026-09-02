#!/usr/bin/env python3
"""Generate the read-only H5.0.3-R1 fallback-factory readiness record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json"
CHECKED_ON = "2026-08-26"
UPDATED_ON = "2026-09-02"


PCBWAY_CONTACT = {
    "authorized_on": "2026-09-02",
    "sent_on": "2026-09-02",
    "sent_at_local": "20:14 Europe/Moscow",
    "from": "vinogradov.anton@gmail.com",
    "to": "service@pcbway.com",
    "channel": "Gmail",
    "subject": "Leshy2 exact-part PCBA and final assembly capability — information only",
    "result": "message_sent",
    "information_only": True,
    "commercial_action_created": False,
    "source_reference": "hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md",
}


JLCPCB_DISPOSITION = {
    "received_on": "2026-09-02",
    "source_reference": "hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md",
    "exact_dual_module_placement_accepted": True,
    "exact_mpn_and_no_silent_substitution_accepted": True,
    "pcba_minimum_quantity": 2,
    "special_process_preorder_acceptance": False,
    "complete_enclosure_final_device_assembly": False,
    "owner_final_assembly_accepted": True,
    "role": "primary_pcba_candidate_with_owner_final_assembly",
}


FACTORIES = [
    {
        "id": "pcbway",
        "role": "optional_full_device_cost_and_convenience_comparison",
        "official_sources": [
            "https://www.pcbway.com/assembly-capabilities.html",
            "https://www.pcbway.com/oem.html",
        ],
        "publicly_confirmed": {
            "consigned_kitted_parts": True,
            "turnkey_parts": True,
            "partial_turnkey_combo": True,
            "customer_approval_before_component_decisions": True,
            "double_sided_mixed_smt_tht": True,
            "prototype_minimum_quantity_five": True,
            "xray_aoi_ict_and_customer_functional_test": True,
            "repair_and_rework": True,
            "oem_component_procurement_pcba_testing_and_final_assembly": True,
        },
        "still_requires_written_acceptance": [
            "exact SA818S-V sourcing lead time or consignment",
            "the four requested final-assembly operations for exactly one unpowered device",
            "exact-MPN incoming inspection and no-silent-substitution terms",
        ],
        "status": "questionnaire_sent_response_optional_for_release",
    },
    {
        "id": "seeed-fusion",
        "role": "second_source_for_pcba_not_yet_full_box_build",
        "official_sources": ["https://www.seeedstudio.com/pcb-assembly.html"],
        "publicly_confirmed": {
            "turnkey_pcba": True,
            "supplier_linked_component_sourcing": True,
            "local_open_parts_library": True,
            "no_minimum_order": True,
            "double_sided_mixed_smt_tht": True,
            "functional_testing": True,
        },
        "observed_gap": "the inspected productization/mass-production deep link returned HTTP 404; the PCBA page does not itemize the required final-device J4-F/J4-P operations",
        "still_requires_written_acceptance": [
            "full-device final assembly rather than PCBA only",
            "exact SA818S-U/V sourcing or consignment",
            "the four requested final-assembly operations for exactly one unpowered device",
        ],
        "status": "retain_as_pcba_second_source_not_first_box_build_fallback",
    },
]


def build() -> dict:
    rows = {row["id"]: row for row in FACTORIES}
    pcbway = rows["pcbway"]
    seeed = rows["seeed-fusion"]
    checks = {
        "exactly_two_non_jlc_candidates_are_recorded": set(rows) == {"pcbway", "seeed-fusion"},
        "pcbway_public_evidence_covers_sourcing_pcba_test_and_final_assembly_classes": all(pcbway["publicly_confirmed"].values()),
        "pcbway_exact_leshy_acceptance_and_price_remain_open": len(pcbway["still_requires_written_acceptance"]) == 3,
        "seeed_public_evidence_is_not_overstated_as_full_box_build": seeed["role"] == "second_source_for_pcba_not_yet_full_box_build" and "404" in seeed["observed_gap"],
        "pcbway_information_only_questionnaire_sent_without_commercial_action": PCBWAY_CONTACT["result"] == "message_sent"
        and PCBWAY_CONTACT["information_only"]
        and not PCBWAY_CONTACT["commercial_action_created"],
        "owner_final_assembly_removes_jlcpcb_full_device_decline_from_release_gate": not JLCPCB_DISPOSITION["complete_enclosure_final_device_assembly"]
        and not JLCPCB_DISPOSITION["special_process_preorder_acceptance"]
        and JLCPCB_DISPOSITION["owner_final_assembly_accepted"]
        and JLCPCB_DISPOSITION["role"] == "primary_pcba_candidate_with_owner_final_assembly",
        "no_order_or_commercial_action_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError([key for key, value in checks.items() if not value])
    return {
        "schema_version": 1,
        "artifact": "H5-EVR08",
        "gate": "H5.0.3-R1",
        "checked_on": CHECKED_ON,
        "updated_on": UPDATED_ON,
        "status": "optional_full_device_inquiry_response_open_pcba_path_unblocked",
        "contact": PCBWAY_CONTACT,
        "primary_disposition": JLCPCB_DISPOSITION,
        "factories": FACTORIES,
        "selection": {
            "first_fallback": "pcbway",
            "reason": "PCBWay remains useful as an optional cost/convenience comparison, but owner installation of the display, five microcoax jumpers, encoder knob and enclosure removes full-device factory assembly from the release gate",
            "second_source_pcba": "seeed-fusion",
            "jlcpcb_remains_pcba_reference": True,
            "jlcpcb_remains_primary_full_device_factory": False,
        },
        "checks": checks,
        "authorization": {
            "additional_fallback_supplier_contact_send": False,
            "quote_project": False,
            "reservation": False,
            "sourcing_request": False,
            "purchase": False,
            "component_replacement": False,
            "pcb_placement_and_routing": False,
            "fabrication": False,
        },
        "next": "close H5 and continue H6 on the JLCPCB PCBA path; select exact screw length and obtain the real PCBA price only after H6 enclosure and fabrication outputs exist; record PCBWay's reply when it arrives, but do not wait for it",
    }


def render() -> str:
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale generated artifact: {OUTPUT.relative_to(REPO)}")
        print("ok: PCBWay response is optional; JLCPCB PCBA plus owner final assembly is unblocked")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
