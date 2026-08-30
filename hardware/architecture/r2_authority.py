#!/usr/bin/env python3
"""Fail-closed authority gate between current H0-R2 and historical R1 H2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
POLICY = REPO / "hardware/architecture/r2-authority.json"
H0 = REPO / "hardware/architecture/h0-r2-rebaseline.json"
PIN_AUTHORITY = REPO / "hardware/architecture/h1-r2-dual-rp-pinout.json"
C5_MUX = REPO / "hardware/architecture/c5-sdio-service-mux-contract.json"
PACK_SAFETY_I2C = REPO / "hardware/architecture/pack-safety-i2c-boundary-contract.json"
G2F = REPO / "hardware/architecture/candidates/G2F-3I.json"
U219_CONTRACT = REPO / "hardware/architecture/h1-r2-u219-cap.json"
PHYSICAL_H1 = REPO / "hardware/product-design/h1-r2-placement.json"
H2 = REPO / "hardware/ecad/generated/H2-R2-hwfw-contract.json"
H2_M1 = REPO / "hardware/ecad/generated/H2-R2-interboard-m1.json"
OUTPUT = REPO / "hardware/architecture/generated/H0-R2-authority-gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_domain_id(row: dict) -> str:
    return str(row.get("id") or row.get("instance") or row.get("domain") or "").lower()


def composed_c5_pin_map(g2f: dict, c5_mux: dict) -> list[dict]:
    """Compose retained IR/service/evidence pins with the current SDIO/USB mux."""
    base = [row for row in g2f.get("allocations", []) if row.get("instance") == "c5"]
    mux_contacts = {
        row["gpio"]: row for row in c5_mux.get("c5_module", {}).get("signals", [])
    }
    net_by_signal = {
        "SDIO_DAT1": "C5_SDIO_D1",
        "SDIO_DAT0": "C5_SDIO_D0",
        "SDIO_CLK": "C5_SDIO_CLK",
        "SDIO_CMD": "C5_SDIO_CMD",
        "SDIO_DAT3_USB_DM": "C5_SDIO_D3_USB_DM",
        "SDIO_DAT2_USB_DP": "C5_SDIO_D2_USB_DP",
    }
    rows = [row for row in base if row.get("contact") not in mux_contacts]
    direction_by_contact = {row.get("contact"): row.get("direction") for row in base}
    for contact, mux in mux_contacts.items():
        rows.append({
            "instance": "c5",
            "contact": contact,
            "net": net_by_signal[mux["signal"]],
            "signal": mux["signal"],
            "direction": direction_by_contact.get(contact, "io"),
            "controller": (
                "SDIO_SLAVE_OR_USB_SERIAL_JTAG"
                if mux["muxed_with_usb"] else "SDIO_SLAVE"
            ),
            "module_pad": mux["module_pad"],
            "muxed_with_usb": mux["muxed_with_usb"],
            "strap_role": mux["strap_role"],
            "endpoint": (
                "Hub RP native 4-bit SDIO through FSUSB42 service mux"
                if mux["muxed_with_usb"] else "Hub RP native 4-bit SDIO"
            ),
        })
    return sorted(rows, key=lambda row: int(str(row["contact"]).removeprefix("GPIO")))


def retained_controller_pin_maps(g2f: dict, c5_mux: dict) -> dict[str, list[dict]]:
    """Return the exact non-RP controller maps retained from reviewed G2F-3I.

    The C5 SDIO/service overlay is checked independently as a complete source
    artifact.  Keeping the whole retained map here prevents future H2 exports
    from silently preserving only the six muxed contacts while dropping IR,
    service or TX-evidence contacts.  Pack and Safety receive the same exact
    treatment rather than being represented by MPN identity alone.
    """
    instance_by_domain = {
        "pack": "pack_admission",
        "safety": "safety_controller",
    }
    allocations = g2f.get("allocations", [])
    result = {}
    for domain, instance in instance_by_domain.items():
        rows = [dict(row) for row in allocations if row.get("instance") == instance]
        for row in rows:
            if row.get("contact") == "PA0":
                row.update(
                    net="HUB_SAFE_I2C_SDA",
                    peers=["hub_rp.GPIO42", "M1.32"],
                    endpoint="Hub RP I2C1 through TCA9803DGKR SDAA/SDAB powered-off boundary and M1.32",
                )
            elif row.get("contact") == "PA11":
                row.update(
                    net="HUB_SAFE_I2C_SCL",
                    peers=["hub_rp.GPIO43", "M1.33"],
                    endpoint="Hub RP I2C1 through TCA9803DGKR SCLA/SCLB powered-off boundary and M1.33",
                )
        result[domain] = rows
    result["c5"] = composed_c5_pin_map(g2f, c5_mux)
    return result


def expected_domain_contracts(current_domains: list[dict], h0: dict,
                              pin_authority: dict, c5_mux: dict,
                              g2f: dict | None = None) -> list[dict]:
    g2f = g2f or load(G2F)
    retained_maps = retained_controller_pin_maps(g2f, c5_mux)
    pin_maps = {
        "s3": h0.get("s3", {}).get("pin_map", []),
        **retained_maps,
        "hub_rp": pin_authority.get("hub_rp", {}).get("pin_map", []),
        "rf_rp": pin_authority.get("rf_rp", {}).get("pin_map", []),
    }
    result = []
    for row in current_domains:
        contract = {"id": row.get("id"), "mpn": row.get("mpn")}
        if row.get("id") in pin_maps:
            contract["pin_map"] = pin_maps[row["id"]]
        result.append(contract)
    return result


def canonical_domain_contracts(rows: object) -> list[dict] | None:
    if not isinstance(rows, list):
        return None
    result = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        domain_id = normalized_domain_id(row)
        contract = {"id": domain_id, "mpn": row.get("mpn")}
        if domain_id in {"s3", "c5", "hub_rp", "rf_rp", "pack", "safety"}:
            contract["pin_map"] = row.get("pin_map")
        result.append(contract)
    return result


def expected_m1(h0: dict) -> dict:
    interboard = h0.get("interboard_rebaseline", {})
    return {
        "connector": interboard.get("connector"),
        "current_budget": interboard.get("current_budget"),
        "pin_map": interboard.get("pin_map"),
    }


def expected_source_hashes() -> dict[str, str]:
    return {
        str(H0.relative_to(REPO)): digest(H0),
        str(PIN_AUTHORITY.relative_to(REPO)): digest(PIN_AUTHORITY),
        str(C5_MUX.relative_to(REPO)): digest(C5_MUX),
        str(PACK_SAFETY_I2C.relative_to(REPO)): digest(PACK_SAFETY_I2C),
        str(G2F.relative_to(REPO)): digest(G2F),
        str(U219_CONTRACT.relative_to(REPO)): digest(U219_CONTRACT),
        str(PHYSICAL_H1.relative_to(REPO)): digest(PHYSICAL_H1),
    }


def build(policy: dict | None = None, h0: dict | None = None,
          h2: dict | None = None, h2_m1: dict | None = None,
          pin_authority: dict | None = None, c5_mux: dict | None = None,
          physical_h1: dict | None = None, g2f: dict | None = None) -> dict:
    policy = policy or load(POLICY)
    h0 = h0 or load(H0)
    h2 = h2 or load(H2)
    h2_m1 = h2_m1 or load(H2_M1)
    pin_authority = pin_authority or load(PIN_AUTHORITY)
    c5_mux = c5_mux or load(C5_MUX)
    g2f = g2f or load(G2F)
    physical_h1 = physical_h1 or load(PHYSICAL_H1)

    current_domains = h0.get("compute_domains", [])
    current_rps = [row for row in current_domains if row.get("mpn") == "SC1512-A4"]
    candidate_domains = h2.get("bsp", {}).get("domains", [])
    reported_rps = [row for row in candidate_domains if row.get("mpn") == "SC1512-A4"]
    candidate_rps = [
        row for row in candidate_domains
        if normalized_domain_id(row) in {"hub_rp", "rf_rp"}
    ]
    m1 = h0.get("interboard_rebaseline", {})
    m1_budget = m1.get("current_budget", {})
    h0_pin_map = m1.get("pin_map", [])
    errors: list[str] = []
    if len(current_domains) != 6:
        errors.append("H0-R2 must define six compute domains")
    if len(current_rps) != 2 or {row.get("id") for row in current_rps} != {"hub_rp", "rf_rp"}:
        errors.append("H0-R2 must define distinct front Hub RP and rear RF RP")
    if len(h0_pin_map) != 80:
        errors.append("H0-R2 M1 must contain all 80 contacts")
    exact_pin_maps = {
        domain: pin_authority.get(domain, {}).get("pin_map", [])
        for domain in ("hub_rp", "rf_rp")
    }
    if pin_authority.get("marker") != "H1-R2.31":
        errors.append("current dual-RP pin authority must carry marker H1-R2.31")
    if any([row.get("gpio") for row in rows] != list(range(48)) for rows in exact_pin_maps.values()):
        errors.append("current dual-RP pin authority must map GPIO0..47 exactly once per RP")
    if len(pin_authority.get("m1_binding", [])) != 5:
        errors.append("current dual-RP pin authority must bind exactly five Hub-RF M1 signals")
    pre_h2_gates = pin_authority.get("authority_chain", {}).get("remaining_h2_gates", [])
    physical_pre_h2_gates = physical_h1.get("pre_r2_h2_gates", [])
    reconciliation = h2.get("r2_reconciliation", {})
    expected_domains = [(row.get("id"), row.get("mpn")) for row in current_domains]
    exact_domain_contracts = expected_domain_contracts(
        current_domains, h0, pin_authority, c5_mux, g2f
    )
    candidate_domain_identities = [
        (normalized_domain_id(row), row.get("mpn")) for row in candidate_domains
    ]
    candidate_rp_maps = {
        normalized_domain_id(row): row.get("pin_map") for row in candidate_rps
    }
    expected_hashes = expected_source_hashes()
    candidate_hashes = h2.get("source_sha256", {})
    h2_m1_contacts = [
        {"contact": row.get("contact"), "net": row.get("net")}
        for row in h2_m1.get("contacts", [])
    ]
    expected_m1_contacts = [
        {"contact": row.get("contact"), "net": row.get("net")}
        for row in h0_pin_map
    ]
    physical_source = str(PHYSICAL_H1.relative_to(REPO))
    expected_physical_reconciliation = {
        "source": physical_source,
        "sha256": expected_hashes[physical_source],
        "marker": physical_h1.get("marker"),
        "pin_authority_marker": physical_h1.get("pin_authority_marker"),
        "status": physical_h1.get("status"),
        "current_h1_blockers": physical_h1.get("current_h1_blockers", []),
        "pre_r2_h2_gates": physical_pre_h2_gates,
    }
    candidate_integration_domains = h2.get("integration_contract", {}).get("controllers", [])
    compatibility = {
        "six_compute_domains": candidate_domain_identities == expected_domains,
        "two_distinct_rp_domains": len(candidate_rps) == 2
        and {normalized_domain_id(row) for row in candidate_rps} == {"hub_rp", "rf_rp"}
        and all(row.get("mpn") == "SC1512-A4" for row in candidate_rps),
        "exact_six_domain_contracts": canonical_domain_contracts(candidate_domains)
        == exact_domain_contracts
        and canonical_domain_contracts(candidate_integration_domains) == exact_domain_contracts
        and reconciliation.get("domain_contracts") == exact_domain_contracts,
        "exact_hub_rp_pin_map": candidate_rp_maps.get("hub_rp") == exact_pin_maps["hub_rp"]
        and reconciliation.get("hub_pin_map") == exact_pin_maps["hub_rp"],
        "exact_rf_rp_pin_map": candidate_rp_maps.get("rf_rp") == exact_pin_maps["rf_rp"]
        and reconciliation.get("rear_pin_map") == exact_pin_maps["rf_rp"],
        "exact_c5_mux": reconciliation.get("c5_sdio_service_mux") == c5_mux,
        "exact_source_hashes": all(candidate_hashes.get(path) == sha256
                                    for path, sha256 in expected_hashes.items())
        and reconciliation.get("hardware_sources") == expected_hashes,
        "exact_m1_reconciliation": reconciliation.get("interboard") == expected_m1(h0),
        "exact_m1_export": h2_m1_contacts == expected_m1_contacts,
        "hardware_marker": reconciliation.get("hardware_marker") == pin_authority.get("marker"),
        "zero_unresolved_pre_h2_gates": pre_h2_gates == []
        and physical_pre_h2_gates == []
        and reconciliation.get("pre_h2_gates") == [],
        "physical_h1_reviewed": physical_h1.get("pin_authority_marker") == pin_authority.get("marker")
        and physical_h1.get("status") == "reviewed"
        and physical_h1.get("current_h1_blockers") == []
        and reconciliation.get("physical_h1") == expected_physical_reconciliation,
    }
    h2_is_current_r2 = all(compatibility.values())
    if pre_h2_gates and "open" not in policy.get("exact_c5_mux_status", ""):
        errors.append("R2 authority status must expose unresolved pre-H2 production gates")
    if policy.get("current_r2_h2_export") and not h2_is_current_r2:
        errors.append("current-R2 H2 claim is forbidden until domains, exact RP maps, C5 mux/source hashes, M1, reviewed physical H1 and every pre-H2 gate reconcile")
    if policy.get("r2_kicad_started") and not (
        policy.get("current_r2_h2_export") and h2_is_current_r2
    ):
        errors.append("R2 KiCad cannot start before the generated H2 export matches H0-R2 and physical H1 is reviewed")

    r2_h2_authoritative = h2_is_current_r2 and policy.get("current_r2_h2_export", False)

    return {
        "schema_version": 1,
        "artifact": "H0-R2-authority-gate",
        "status": (
            "fail" if errors else
            "pass_current_r2_h2_reconciled" if r2_h2_authoritative else
            "pass_historical_r1_h2_quarantined"
        ),
        "current_authority": policy.get("current_authority"),
        "current_h0": {
            "domain_count": len(current_domains),
            "domain_ids": [row.get("id") for row in current_domains],
            "rp_domain_ids": [row.get("id") for row in current_rps],
            "m1_contacts": len(h0_pin_map),
            "m1_live_signals": m1_budget.get("live_signals"),
            "m1_reserve_contacts": sum(row.get("class") == "reserve" for row in h0_pin_map),
        },
        "current_h1_pin_authority": {
            "source": policy.get("current_pin_authority"),
            "marker": pin_authority.get("marker"),
            "hub_gpio_rows": len(exact_pin_maps["hub_rp"]),
            "rf_gpio_rows": len(exact_pin_maps["rf_rp"]),
            "m1_signal_bindings": len(pin_authority.get("m1_binding", [])),
            "c5_mux_status": policy.get("exact_c5_mux_status"),
        },
        "current_h1_physical_authority": {
            "source": policy.get("current_physical_authority"),
            "marker": physical_h1.get("marker"),
            "status": physical_h1.get("status"),
            "open_blockers": len(physical_h1.get("current_h1_blockers", [])),
        },
        "current_exact_domain_contracts": exact_domain_contracts,
        "current_r2_h2": {
            "authority": "current_native_r2" if r2_h2_authoritative else "not_authoritative",
            "domain_count": len(candidate_domains),
            "domain_ids": [normalized_domain_id(row) for row in candidate_domains],
            "rp_instances": [normalized_domain_id(row) for row in reported_rps],
            "m1_unique_nets": h2_m1.get("summary", {}).get("unique_nets"),
            "m1_reserve_contacts": h2_m1.get("summary", {}).get("no_connect_reserve_contacts"),
            "native_kicad_started": h2.get("authority", {}).get("native_kicad_started"),
        },
        "r2_h2_compatibility": compatibility,
        "r2_h2_authoritative": r2_h2_authoritative,
        "r2_kicad_started": policy.get("r2_kicad_started", False),
        "exact_rp_gpio_order_status": policy.get("exact_rp_gpio_order_status"),
        "exact_c5_mux_status": policy.get("exact_c5_mux_status"),
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
