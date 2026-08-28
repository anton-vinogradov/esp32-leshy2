#!/usr/bin/env python3
"""Fail-closed authority gate between current H0-R2 and historical R1 H2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
POLICY = REPO / "hardware/architecture/r2-authority.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
H2 = REPO / "hardware/ecad/generated/H2-hwfw-contract.json"
H2_M1 = REPO / "hardware/ecad/generated/H2-RF40-interboard-m1.json"
OUTPUT = REPO / "hardware/architecture/generated/H0-R2-authority-gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(policy: dict | None = None, h0: dict | None = None,
          h2: dict | None = None, h2_m1: dict | None = None) -> dict:
    policy = policy or load(POLICY)
    h0 = h0 or load(H0)
    h2 = h2 or load(H2)
    h2_m1 = h2_m1 or load(H2_M1)

    current_domains = h0.get("compute_domains", [])
    current_rps = [row for row in current_domains if row.get("mpn") == "SC1512-A4"]
    historical_domains = h2.get("bsp", {}).get("domains", [])
    historical_rps = [row for row in historical_domains if row.get("mpn") == "SC1512-A4"]
    m1 = h0.get("interboard_rebaseline", {})
    m1_budget = m1.get("current_budget", {})
    h0_pin_map = m1.get("pin_map", [])
    historical_summary = h2_m1.get("summary", {})

    compatibility = {
        "six_compute_domains": len(historical_domains) == 6,
        "two_distinct_rp_domains": len(historical_rps) == 2
        and {row.get("instance") for row in historical_rps} == {"hub_rp", "rf_rp"},
        "h0_m1_live_signal_count": historical_summary.get("unique_nets")
        == m1_budget.get("live_signals"),
        "h0_m1_reserve_count": historical_summary.get("reserved_contacts")
        == sum(row.get("class") == "reserve" for row in h0_pin_map),
        "h0_m1_has_all_80_contacts": len(h0_pin_map) == 80,
    }
    h2_is_current_r2 = all(compatibility.values())
    errors: list[str] = []
    if len(current_domains) != 6:
        errors.append("H0-R2 must define six compute domains")
    if len(current_rps) != 2 or {row.get("id") for row in current_rps} != {"hub_rp", "rf_rp"}:
        errors.append("H0-R2 must define distinct front Hub RP and rear RF RP")
    if len(h0_pin_map) != 80:
        errors.append("H0-R2 M1 must contain all 80 contacts")
    if policy.get("current_r2_h2_export") and not h2_is_current_r2:
        errors.append("current-R2 H2 claim is forbidden while the generated export is single-RP/old-M1")
    if policy.get("r2_kicad_started") and not h2_is_current_r2:
        errors.append("R2 KiCad cannot start before the generated H2 export matches H0-R2")

    return {
        "schema_version": 1,
        "artifact": "H0-R2-authority-gate",
        "status": "pass_historical_r1_h2_quarantined" if not errors else "fail",
        "current_authority": policy.get("current_authority"),
        "current_h0": {
            "domain_count": len(current_domains),
            "domain_ids": [row.get("id") for row in current_domains],
            "rp_domain_ids": [row.get("id") for row in current_rps],
            "m1_contacts": len(h0_pin_map),
            "m1_live_signals": m1_budget.get("live_signals"),
            "m1_reserve_contacts": sum(row.get("class") == "reserve" for row in h0_pin_map),
        },
        "historical_r1_h2": {
            "authority": "historical_only_not_r2",
            "domain_count": len(historical_domains),
            "domain_ids": [row.get("domain") for row in historical_domains],
            "rp_instances": [row.get("instance") for row in historical_rps],
            "m1_unique_nets": historical_summary.get("unique_nets"),
            "m1_reserve_contacts": historical_summary.get("reserved_contacts"),
            "review_evidence_preserved": True,
        },
        "r2_h2_compatibility": compatibility,
        "r2_h2_authoritative": h2_is_current_r2 and policy.get("current_r2_h2_export", False),
        "r2_kicad_started": policy.get("r2_kicad_started", False),
        "exact_rp_gpio_order_status": policy.get("exact_rp_gpio_order_status"),
        "errors": errors,
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    content = render(result)
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    print("ok: current H0-R2 is authoritative; historical single-RP H2 is quarantined")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
