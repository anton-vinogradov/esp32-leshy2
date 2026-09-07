#!/usr/bin/env python3
"""Review the native MAIN/AON startup prerequisites, never certify startup.

The H3 source-state matrix is an admission model.  This deliberately small
independent audit binds its power-cell assumptions to physical native pins.
It reports unresolved findings instead of converting connectivity into a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "nets": "hardware/ecad/generated/H2-R2-native-net-ledger.json",
    "instances": "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
    "devices": "hardware/architecture/devices.json",
    "h0": "hardware/architecture/h0-r2-rebaseline.json",
    "h1": "hardware/product-design/h1-r2-power-thermal.json",
    "h3": "hardware/verification/h3-r2-rail-margin-contract.json",
    "margins": "hardware/verification/generated/H3-R2-rail-margins.json",
    "inrush": "hardware/verification/generated/H3-R2-inrush-watchdog.json",
}
EVIDENCE = {
    "aon_buck": {"url": "https://www.ti.com/lit/ds/symlink/tps629203.pdf", "section": "Tables 8-1/8-2; sections 8.3.3/8.3.5", "checked": "2026-09-07"},
    "main_buck": {"url": "https://www.ti.com/lit/ds/symlink/tps566231.pdf", "section": "Sections 4/5.5/6.3, TPS566231P (PG variant)", "checked": "2026-09-07"},
    "aon_efuse": {"url": "https://www.ti.com/lit/ds/symlink/tps25961.pdf", "section": "Sections 6.3/6.5/7.3, especially RON test conditions", "checked": "2026-09-07"},
    "main_efuse": {"url": "https://www.ti.com/lit/ds/symlink/tps2597.pdf", "section": "Sections 6.5/6.7/7.3.4/7.3.8; equations 4/5/16", "checked": "2026-09-07"},
    "supervisor": {"url": "https://www.ti.com/lit/ds/symlink/tps3808.pdf", "section": "Tables 4-1/5-1; sections 6.5/6.6/7.3.2", "checked": "2026-09-07"},
    "rilm_resistor": {"url": "https://www.uni-royal.cn/en/images/userfile/file/1753752986c56505e6d9ab55c7.pdf", "section": "Sections 2/7: F = 1%, 0402 above 10 ohms = 100 ppm/C", "checked": "2026-09-07"},
}

# Physical numbers and native net names are independently transcribed from the
# exact manufacturer pin tables, not inferred from generic passive symbols.
PINS = {
    "aon_buck": ("ti_tps629203_drlr", {
        "VIN": ("6", "NVDC_SYS"), "EN": ("7", "NVDC_SYS"),
        "SW": ("4", "AON_BUCK_SW"), "VOS": ("3", "AON_RAW_3V3"),
        "GND": ("5", "POWER_GROUND"), "MODE_SCONF": ("8", "AON_MODE_SET"),
        "PG": ("2", "AON_PG_N"), "FB_VSET": ("1", None),
    }),
    "aon_efuse": ("ti_tps25961_drvr", {
        "IN": ("6", "AON_RAW_3V3"), "EN_UVLO": ("5", "AON_RAW_3V3"),
        "OUT": ("1", "AON_SAFE_3V3"), "GND": ("4", "POWER_GROUND"),
        "EP_GND": ("7", "POWER_GROUND"), "OVLO": ("2", "AON_EFUSE_OVLO"),
        "ILIM": ("3", "AON_EFUSE_ILIM"),
    }),
    "safe_supervisor": ("ti_tps3808g33_dbvr", {
        "VDD": ("6", "AON_SAFE_3V3"), "SENSE": ("5", "AON_SAFE_3V3"),
        "GND": ("2", "POWER_GROUND"), "MR_N": ("3", "AON_PG_N"),
        "RESET_N": ("1", "POR_N"), "CT": ("4", None),
    }),
    "main_buck": ("ti_tps566231p_rqfr", {
        "VIN_1": ("5", "NVDC_SYS"), "VIN_2": ("6", "NVDC_SYS"),
        "EN": ("3", "POR_N"), "FB": ("2", "MAIN_3V3_FB"),
        "PGND": ("4", "POWER_GROUND"), "SW": ("8", "MAIN_BUCK_SW"),
        "VCC": ("1", "MAIN_BUCK_VCC"), "BST": ("7", "MAIN_BUCK_BST"),
        "PG": ("9", "MAIN_RAW_3V3_PG_N"),
    }),
    "main_efuse": ("ti_tps25974l_rpwr", {
        "IN": ("5", "MAIN_RAW_3V3"), "EN_UVLO": ("1", "MAIN_RAW_3V3"),
        "OUT": ("6", "3V3_MAIN"), "GND": ("8", "POWER_GROUND"),
        "PG": ("3", "POWER_FAULT_N"), "PGTH": ("4", "MAIN_EFUSE_PGTH"),
        "OVLO": ("2", "MAIN_EFUSE_OVLO"), "ILM": ("9", "MAIN_EFUSE_ILM"),
        "DVDT": ("7", "MAIN_EFUSE_DVDT"), "ITIMER": ("10", "MAIN_EFUSE_ITIMER"),
    }),
}
PASSIVES = {
    "aon_inductor": ("AON_BUCK_SW", "AON_RAW_3V3"),
    "aon_mode_res": ("AON_MODE_SET", "POWER_GROUND"),
    "aon_pg_pullup": ("AON_SAFE_3V3", "AON_PG_N"),
    "aon_input_cap": ("NVDC_SYS", "POWER_GROUND"),
    "aon_output_cap": ("AON_RAW_3V3", "POWER_GROUND"),
    "aon_efuse_rilim": ("AON_EFUSE_ILIM", "POWER_GROUND"),
    "aon_efuse_ovlo_top": ("AON_RAW_3V3", "AON_EFUSE_OVLO"),
    "aon_efuse_ovlo_bottom": ("AON_EFUSE_OVLO", "POWER_GROUND"),
    "safe_por_pullup": ("AON_SAFE_3V3", "POR_N"),
    "main_en_pulldown": ("POR_N", "POWER_GROUND"),
    "main_inductor": ("MAIN_BUCK_SW", "MAIN_RAW_3V3"),
    "main_buck_bootstrap_cap": ("MAIN_BUCK_BST", "MAIN_BUCK_BST_LINK"),
    "main_buck_bootstrap_link": ("MAIN_BUCK_BST_LINK", "MAIN_BUCK_SW"),
    "main_buck_vcc_cap": ("MAIN_BUCK_VCC", "POWER_GROUND"),
    "main_fb_top": ("MAIN_RAW_3V3", "MAIN_3V3_FB"),
    "main_fb_bottom": ("MAIN_3V3_FB", "POWER_GROUND"),
    "main_ff_cap": ("MAIN_RAW_3V3", "MAIN_3V3_FB"),
    "main_efuse_rilm": ("MAIN_EFUSE_ILM", "POWER_GROUND"),
    "main_efuse_pg_top": ("3V3_MAIN", "MAIN_EFUSE_PGTH"),
    "main_efuse_pg_bottom": ("MAIN_EFUSE_PGTH", "POWER_GROUND"),
    "main_efuse_ovlo_top": ("MAIN_RAW_3V3", "MAIN_EFUSE_OVLO"),
    "main_efuse_ovlo_bottom": ("MAIN_EFUSE_OVLO", "POWER_GROUND"),
    "main_efuse_dvdt_cap": ("MAIN_EFUSE_DVDT", "POWER_GROUND"),
    "main_efuse_itimer_cap": ("MAIN_EFUSE_ITIMER", "POWER_GROUND"),
}


def resistance(device):
    """Read a declared value; do not guess from an MPN substring."""
    match = re.match(r"^(\d+(?:_\d+)?)(k?)ohm_", device["kind"])
    if match is None:
        raise ValueError(f"resistance is not declared for {device['mpn']}")
    value = float(match[1].replace("_", ".")) * (1000 if match[2] else 1)
    tolerance = re.search(r"_(\d+(?:_\d+)?)pct_", device["kind"])
    if tolerance is None:
        raise ValueError(f"resistor tolerance is not declared for {device['mpn']}")
    return value, float(tolerance[1].replace("_", ".")) / 100


def evaluate(data):
    rows = data["nets"]["rows"]
    endpoints = {row["endpoint"]: row for row in rows}
    if len(endpoints) != len(rows):
        raise ValueError("duplicate native endpoint")
    instances = {row["instance"]: row for row in data["instances"]["rows"]}
    devices = data["devices"]["devices"]
    checks = []

    def check(ident, passed, detail, observed=None):
        checks.append({"id": ident, "pass": bool(passed), "detail": detail, "observed": observed})

    for instance, (device, pins) in PINS.items():
        check(f"identity:{instance}", instances.get(instance, {}).get("device_id") == device,
              "Exact installed package must match the independently reviewed pin table.")
        for contact, (physical, net) in pins.items():
            row = endpoints.get(f"{instance}.{contact}", {})
            number = str(row.get("physical", "")).split()[0:1]
            declared = devices.get(device, {}).get("contacts", {}).get(contact, {})
            declared_number = str(declared.get("physical", "")).split()[0:1]
            check(f"pin:{instance}.{contact}",
                  row.get("device_id") == device and number == [physical]
                  and declared_number == [physical] and row.get("net") == net
                  and row.get("disposition") == ("no_connect" if net is None else "connected"),
                  "Native physical pin, device-register pin and net must agree with the reviewed prerequisite.",
                  {key: row.get(key) for key in ("reference", "physical", "net", "disposition")})
    for instance, nets in PASSIVES.items():
        actual = [endpoints.get(f"{instance}.END_{pin}", {}) for pin in (1, 2)]
        check(f"path:{instance}", all(row.get("net") == net and row.get("disposition") == "connected"
              for row, net in zip(actual, nets)), "Both terminals of the support path must reach the native nets.")

    def resistor(instance):
        return resistance(devices[instances[instance]["device_id"]])

    mode, _ = resistor("aon_mode_res")
    check("aon_vset_configuration", mode == 42200,
          "TPS629203 Table 8-1 option 11 selects VSET; Table 8-2 open VSET selects 3.3 V, not a missing feedback divider.", mode)
    rt, _ = resistor("main_fb_top")
    rb, _ = resistor("main_fb_bottom")
    vnom = .6 * (1 + rt / rb)
    check("main_feedback_target", abs(vnom - data["h3"]["rails"]["3V3_MAIN"]["nominal_v"]) < 1e-9,
          "TPS566231P uses a 0.600 V nominal reference, not a nominal 3.3 V assumption.", vnom)

    rilm, tolerance = resistor("main_efuse_rilm")
    h1 = data["h1"]["main_power_cell"]
    h3_main = data["h3"]["rails"]["3V3_MAIN"]
    main = data["margins"]["worst_current_by_rail"]["3V3_MAIN"]
    current = float(main["load_ma"]) / 1000
    # H1's existing conservative gain envelope, kept distinct from a guaranteed
    # table row.  Arbitrary-R interpolation is NOT a new manufacturer guarantee.
    model_lower = 5747 / rilm * .90 / (1 + tolerance)
    model_upper = 5747 / rilm * 1.10 / (1 - tolerance)
    check("rilm_matches_accepted_h1", rilm == h1["efuse_threshold_resistor"]["resistance_ohm"],
          "The native fitted resistance must implement the accepted H1 power cell.", rilm)
    check("h3_current_limit_bound_to_fitted_rilm", abs(h3_main["protection_min_a"] - model_lower) < .001,
          "The H3 current threshold cannot survive a different fitted RILM.",
          {"h3_a": h3_main["protection_min_a"], "native_h1_model_lower_a": model_lower})
    check("main_pf03_current_reserve", model_lower >= current * 1.25,
          "PF-R2-03 requires 25% reserve, not merely a positive current remainder.",
          {"load_a": current, "model_lower_a": model_lower, "required_a": current * 1.25})
    floor = data["h0"]["power_rebaseline"]["h1_required_envelope"]
    check("main_h0_step_floor", model_lower >= floor["step_a_min"],
          "A lower RILM threshold cannot silently replace the accepted H0 step envelope.",
          {"model_lower_a": model_lower, "h0_step_a": floor["step_a_min"]})
    check("main_efuse_high_below_buck_limit", model_upper < 6.1,
          "The H1 model's upper eFuse threshold must stay below the exact buck's 6.1 A minimum valley limit.", model_upper)
    main_inrush = next(row for row in data["inrush"]["startup_envelopes"] if row["rail"] == "3V3_MAIN")
    combined = float(main_inrush["combined_current_ma"]) / 1000
    check("main_existing_inrush_model_headroom", combined <= model_lower,
          "Even the existing H3 capacitor-only slew model must fit the native RILM envelope; this is not a startup guarantee.",
          {"combined_current_a": combined, "native_h1_model_lower_a": model_lower, "margin_a": model_lower - combined})
    actual_mpn = instances["main_buck"]["mpn"]
    check("h3_converter_source_is_installed_part", "tps566231" in h3_main["source"].lower(),
          "A conservative current admission does not make the TPS564252 datasheet valid for the fitted TPS566231P.", actual_mpn)

    top, top_tol = resistor("main_efuse_pg_top")
    bottom, bottom_tol = resistor("main_efuse_pg_bottom")
    pg_assert_max = 1.23 * (1 + top * (1 + top_tol) / (bottom * (1 - bottom_tol))) + 1e-6 * top * (1 + top_tol)
    rail_min = float(data["margins"]["voltage_corners"]["3V3_MAIN"]["endpoint_min_v"])
    check("main_pg_assertion_headroom", rail_min >= pg_assert_max,
          "PGTH max 1.23 V, maximum divider ratio and +1 uA input leakage must permit PG on the admitted low rail.",
          {"admitted_output_min_v": rail_min, "required_output_v": pg_assert_max, "margin_v": rail_min - pg_assert_max})

    aon_rilim, _ = resistor("aon_efuse_rilim")
    aon_ron = data["h3"]["rails"]["AON_SAFE_3V3"]["efuse_ron_max_ohm"]
    # Only this exact nominal resistor test condition has a reviewed maximum.
    # The 100k/250k rows publish typical values, not alternative maximum bounds;
    # increasing an unsupported claim above 240 mOhm cannot make it verified.
    # The low-VIN maximum is conservative for the other published VIN range.
    documented_ron_max = .240 if aon_rilim == 34480 else None
    check("aon_ron_test_condition_binding",
          documented_ron_max is not None and math.isfinite(aon_ron) and aon_ron >= documented_ron_max,
          "TPS25961's reviewed 240 mOhm maximum uses nominal RILIM=34.48k and 2.7<=VIN<4.5 V. Other resistor conditions remain unreviewed; 250k/455 mOhm is typical only. This binds a nominal table condition, not resistor-tolerance or startup behavior.",
          {"rilim_ohm": aon_rilim, "claimed_ron_max_ohm": aon_ron,
           "reviewed_table_max_ohm": documented_ron_max,
           "rilim_condition_status": "reviewed_nominal_table_condition" if documented_ron_max is not None else "unreviewed_rilim_condition"})

    failures = [row["id"] for row in checks if not row["pass"]]
    return {
        "schema_version": 1, "artifact": "H6-R2-native-power-startup-review",
        "status": "review_required" if failures else "prerequisites_consistent_not_startup_proven",
        "startup_proven": False, "authorization": {"fabrication": False, "gate_closed": False},
        "evidence": EVIDENCE, "checks": checks, "findings": failures,
        "current_limit": {
            "fitted_rilm_ohm": rilm, "fitted_tolerance_fraction": tolerance,
            "h1_model_lower_a": model_lower, "h1_model_upper_a": model_upper,
            "direct_datasheet_row_1650ohm_min_a": 3.2 if rilm == 1650 else None,
            "direct_row_resistor_tolerance_scaled_min_a": 3.2 / (1 + tolerance) if rilm == 1650 else None,
            "boundary": "H1 gain model and inverse-R extension of a table row are separate evidence; resistor TCR and arbitrary-R guarantees are not silently supplied.",
        },
        "dependency_order": ["NVDC_SYS", "AON_RAW_3V3", "AON_SAFE_3V3", "POR_N", "MAIN_RAW_3V3", "3V3_MAIN"],
        "unproven": [
            "Availability and cold-start of NVDC_SYS itself; usb_present is not a voltage or startup waveform.",
            "Combined source impedance, soft-start, live low-voltage loads and eFuse thermal behavior.",
            "3300/CdVdt with minimum C covers capacitor tolerance, not a guaranteed maximum slew across IC process, voltage and temperature.",
            "AON eFuse RON and resulting supervisor release headroom need bounds for the fitted RILIM, not a different test condition.",
            "H1 efficiency 89.86% is a required floor for its assumed 44 K/W layout, not a simulated or measured efficiency.",
            "PG high qualifies its threshold only; it cannot by itself prove every consumer's voltage or transient margin.",
        ],
    }


def build():
    data = {name: json.loads((ROOT / path).read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    result = evaluate(data)
    result["source_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in INPUTS.values()}
    return result


def validate_result(result):
    """Integrity of a review is independent of whether its findings are closed."""
    checks = result["checks"]
    if not checks or len({row["id"] for row in checks}) != len(checks):
        raise ValueError("empty or duplicate prerequisite checks")
    if any(type(row["pass"]) is not bool for row in checks):
        raise ValueError("a prerequisite check is not an explicit boolean")
    findings = [row["id"] for row in checks if not row["pass"]]
    if result["findings"] != findings:
        raise ValueError("review findings are incomplete")
    expected = "review_required" if findings else "prerequisites_consistent_not_startup_proven"
    if result["status"] != expected or result["startup_proven"] is not False:
        raise ValueError("prerequisite review cannot prove startup")
    if result["authorization"] != {"fabrication": False, "gate_closed": False}:
        raise ValueError("prerequisite review cannot authorize release")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check review integrity; unresolved findings remain review_required, not release PASS")
    parser.add_argument("--require-no-findings", action="store_true", help="also return nonzero when prerequisite findings remain")
    args = parser.parse_args()
    result = build()
    validate_result(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.require_no_findings and result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
