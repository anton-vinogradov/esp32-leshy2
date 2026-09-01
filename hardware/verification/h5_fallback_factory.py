#!/usr/bin/env python3
"""Generate the read-only H5.0.3-R1 fallback-factory readiness record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json"
CHECKED_ON = "2026-08-26"


FACTORIES = [
    {
        "id": "pcbway",
        "role": "first_fallback_for_full_device",
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
            "the four release-required final-assembly operations for exactly one unpowered device",
            "exact-MPN incoming inspection and no-silent-substitution terms",
        ],
        "status": "ready_for_same_no_order_questionnaire_if_authorized",
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
            "the four release-required final-assembly operations for exactly one unpowered device",
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
        "no_supplier_contact_or_commercial_action_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError([key for key, value in checks.items() if not value])
    return {
        "schema_version": 1,
        "artifact": "H5-EVR08",
        "gate": "H5.0.3-R1",
        "checked_on": CHECKED_ON,
        "status": "fallback_ranked_no_contact_authorized",
        "factories": FACTORIES,
        "selection": {
            "first_fallback": "pcbway",
            "reason": "strongest public evidence for exact-part approval, consignment, mixed PCBA, customer functional test and final product assembly in one supplier class",
            "second_source_pcba": "seeed-fusion",
            "jlcpcb_remains_primary": True,
        },
        "checks": checks,
        "authorization": {
            "fallback_supplier_contact_send": False,
            "quote_project": False,
            "reservation": False,
            "sourcing_request": False,
            "purchase": False,
            "component_replacement": False,
            "pcb_placement_and_routing": False,
            "fabrication": False,
        },
        "next": "keep waiting for JLCPCB; if it declines a release-required operation, request separate authority to send the exact-one no-order gate questionnaire to PCBWay",
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
        print("ok: H5 fallback factory readiness is current; no contact authorized")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
