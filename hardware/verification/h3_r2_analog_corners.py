#!/usr/bin/env python3
"""Consolidate the current R2 display, audio, IR, battery and Airband corners."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "hardware/architecture/candidates/G2F-3I.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
RAILS = ROOT / "hardware/verification/generated/H3-R2-rail-margins.json"
PROVENANCE = ROOT / "hardware/verification/generated/H3-R2-parameter-provenance.json"
AUDIO = ROOT / "hardware/verification/generated/H3-VRF32-audio.json"
IR = ROOT / "hardware/verification/generated/H3-VRF33-ir.json"
BATTERY = ROOT / "hardware/verification/generated/H3-VRF34-battery-analog.json"
AIRBAND = ROOT / "hardware/verification/generated/H3-R2-airband-corners.json"
NATIVE_NETS = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
NATIVE_INSTANCES = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
COST_AUDIT = ROOT / "hardware/product-design/generated/H1-R2-cost-audit.json"
DISPLAY_MOUNT = ROOT / "hardware/product-design/display-mount.json"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-analog-corners.json"
DOC_EN = ROOT / "docs/analog-electrical-verification.md"
DOC_RU = ROOT / "docs/analog-electrical-verification.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_set(candidate: dict) -> set[tuple[str, str, str]]:
    return {(row["from"], row["to"], row["net"]) for row in candidate["fixed_routes"]}


def route_exists(routes: set[tuple[str, str, str]], start: str, end: str, net: str) -> bool:
    return (start, end, net) in routes or (end, start, net) in routes


def all_true(mapping: dict) -> bool:
    return isinstance(mapping, dict) and bool(mapping) and all(value is True for value in mapping.values())


def endpoint_on_net(rows: list[dict], endpoint: str, net: str) -> bool:
    return any(row.get("endpoint") == endpoint and row.get("net") == net for row in rows)


def native_leaf_transfers(candidate: dict, devices: dict, instances: list[dict], rows: list[dict], leaves: dict) -> dict:
    """Bind two reviewed substitutions, not the whole retained G2F circuit.

    Vishay 82907 Rev.1.0 pp.1-3 gives the same electrical device/pinning for
    TT and TR; pp.6-7 distinguish tape presentation, not a new gain/supply spec.
    Same Sky SJ-43504-SMT-TR and SJ-4351X-SMT (2024-09-12), both p.2,
    show normally closed 2--5 tip switches. TS omits the unused ring switch6.
    This permits a bounded electrical-model transfer, NOT transfer of optical
    aiming/range, jack mechanics, acoustic performance, or factory readiness.
    Expectations below are independent of the configurable native pin map.
    """
    specs = {
        "ir": {
            "instance": "ir_carrier", "project": "LESHY2-UI-R2", "reference": "U23",
            "legacy_id": "vishay_tsmp95000tt", "legacy_mpn": "Vishay TSMP95000TT",
            "current_id": "vishay_tsmp95000tr", "current_mpn": "Vishay TSMP95000TR",
            "contacts": {"GND_1": ("1", "power", "POWER_GROUND"), "VS": ("2", "power", "IR_CARRIER_VS"),
                         "CARRIER_OUT": ("3", "signal", "IR_CARRIER_LOCAL_N"), "GND_4": ("4", "power", "POWER_GROUND")},
            "source_urls": ["https://www.vishay.com/docs/82907/tsmp95000.pdf"],
            "transfer_scope": "Same TSMP95000 electrical receiver, supply/current and carrier-output model; TT-to-TR tape presentation only.",
            "not_transferred": ["Optical axis/window/range and emitter-to-witness alignment", "Footprint, assembly process and routed/assembled verification", "Other IR leaf circuitry is retained evidence, not newly verified by this substitution guard"],
        },
        "audio": {
            "instance": "headphone_jack", "project": "LESHY2-RF-R2", "reference": "U83",
            "legacy_id": "same_sky_sj_43504_smt_tr", "legacy_mpn": "Same Sky SJ-43504-SMT-TR",
            "current_id": "same_sky_sj_43515ts_smt_tr", "current_mpn": "Same Sky SJ-43515TS-SMT-TR",
            "contacts": {"SLEEVE": ("1", "analog", "HEADSET_MIC_RAW"), "TIP": ("2", "analog", "HEADPHONE_LEFT_TIP"),
                         "RING1": ("3", "analog", "HEADPHONE_RIGHT_RING1"), "RING2": ("4", "power", "AUDIO_GROUND"),
                         "TIP_SWITCH": ("5", "signal", "HEADSET_SWITCH_STATE")},
            "source_urls": ["https://www.sameskydevices.com/product/resource/sj-43504-smt-tr.pdf",
                            "https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf"],
            "transfer_scope": "Five used CTIA conductors and normally-closed tip2-to-switch5 detector model; unused ring-switch6 is absent, not a new NC pad.",
            "not_transferred": ["Mid-mount cutout, ordinary-SMT footprint, locator holes, plug access and retention", "Contact resistance, lifetime, insertion pop and acoustic/accessory performance", "Other audio leaf circuitry is retained evidence, not newly verified by this substitution guard", "slow_io.P02 must remain a high-impedance input; this is not a firmware configuration execution test"],
        },
    }

    def one_endpoint(endpoint: str, physical: str, net: str, project: str) -> bool:
        found = [row for row in rows if row.get("endpoint") == endpoint]
        return len(found) == 1 and all(found[0].get(key) == value for key, value in {
            "physical": physical, "net": net, "disposition": "connected", "project": project,
            "instance": endpoint.split(".", 1)[0], "contact": endpoint.split(".", 1)[1],
        }.items())

    def support(instance: str, device_id: str, mpn: str, project: str, pins: dict) -> bool:
        found = [row for row in instances if row.get("instance") == instance]
        return (candidate.get("instances", {}).get(instance) == device_id
                and devices.get(device_id, {}).get("mpn") == mpn
                and len(found) == 1 and found[0].get("device_id") == device_id
                and found[0].get("mpn") == mpn and found[0].get("project") == project
                and all(one_endpoint(f"{instance}.{contact}", physical, net, project)
                        and next(row for row in rows if row.get("endpoint") == f"{instance}.{contact}").get("device_id") == device_id
                        and next(row for row in rows if row.get("endpoint") == f"{instance}.{contact}").get("reference") == found[0].get("reference")
                        for contact, (physical, net) in pins.items()))

    def exact_net(net: str, endpoints: set[str], project: str) -> bool:
        found = [row for row in rows if row.get("net") == net]
        return (len(found) == len(endpoints) and {row.get("endpoint") for row in found} == endpoints
                and all(row.get("project") == project and row.get("disposition") == "connected" for row in found))

    result = {}
    for domain, spec in specs.items():
        name, project = spec["instance"], spec["project"]
        old = devices.get(spec["legacy_id"], {})
        new = devices.get(spec["current_id"], {})
        found = [row for row in instances if row.get("instance") == name]
        contacts = {contact: {"physical": physical, "role": role}
                    for contact, (physical, role, _net) in spec["contacts"].items()}
        native_contacts = [row for row in rows if row.get("instance") == name or str(row.get("endpoint", "")).startswith(name + ".")]
        checks = {
            "retained_leaf_exact_identity": candidate.get("instances", {}).get(name) == spec["legacy_id"]
                and leaves.get(domain, {}).get("exact_part_checks", {}).get(name) is True
                and leaves.get(domain, {}).get("checks", {}).get("exact_" + name) is True,
            "manufacturer_identities": old.get("mpn") == spec["legacy_mpn"] and new.get("mpn") == spec["current_mpn"],
            "primary_sources": old.get("source", {}).get("url") == spec["source_urls"][0]
                and new.get("source", {}).get("url") == spec["source_urls"][-1],
            "unique_current_native_instance": len(found) == 1 and all(found[0].get(key) == value for key, value in {
                "device_id": spec["current_id"], "mpn": spec["current_mpn"], "project": project, "reference": spec["reference"],
            }.items()),
            "exact_manufacturer_contacts": new.get("contacts") == contacts
                and all(old.get("contacts", {}).get(contact) == value for contact, value in contacts.items()),
            "complete_current_native_contact_map": len(native_contacts) == len(contacts) and all(
                one_endpoint(f"{name}.{contact}", physical, net, project)
                for contact, (physical, _role, net) in spec["contacts"].items()) and all(
                    row.get("device_id") == spec["current_id"] and row.get("reference") == spec["reference"]
                    and row.get("instance") == name and row.get("contact") in contacts
                    and row.get("endpoint") == f"{name}.{row.get('contact')}"
                    and row.get("role") == contacts[row["contact"]]["role"] for row in native_contacts),
        }
        old_ec, new_ec = old.get("electrical_contract", {}), new.get("electrical_contract", {})
        if domain == "ir":
            expected = {"supply_v": [2.0, 5.5], "carrier_range_khz": [30, 60], "typical_supply_current_ma_at_3v3": 0.35,
                        "output": "active-low carrier cycles; the only onboard source allowed to create measured 30-60-kHz carrier provenance"}
            checks["same_published_electrical_model"] = all(old_ec.get(k) == value and new_ec.get(k) == value for k, value in expected.items())
            checks["tape_presentation_not_electrical_rating"] = (old_ec.get("taping") == "TT top-view tape, 2200 pieces per reel"
                                                               and new_ec.get("taping") == "TR side-view tape, 2300 pieces per reel")
            checks["native_100ohm_supply_and_4k7_pullup"] = (
                support("ir_carrier_supply_res", "yageo_rc0402fr_07100rl", "Yageo RC0402FR-07100RL", project,
                        {"END_1": ("1", "3V3_IR_SWITCHED"), "END_2": ("2", "IR_CARRIER_VS")})
                and support("ir_carrier_pullup", "yageo_rc0402fr_074k7l", "Yageo RC0402FR-074K7L", project,
                            {"END_1": ("1", "IR_CARRIER_LOCAL_N"), "END_2": ("2", "IR_CARRIER_VS")})
                and support("ir_carrier_supply_cap", "murata_grm188z71a475me15d", "Murata GRM188Z71A475ME15D", project,
                            {"END_1": ("1", "IR_CARRIER_VS"), "END_2": ("2", "POWER_GROUND")})
                and support("ir_return_buffer", "nexperia_74lvc2g126dp_125", "Nexperia 74LVC2G126DP,125", project,
                            {"2A": ("5", "IR_CARRIER_LOCAL_N")}))
            checks["no_added_carrier_node_loads"] = (
                exact_net("IR_CARRIER_LOCAL_N", {"ir_carrier.CARRIER_OUT", "ir_carrier_pullup.END_1", "ir_return_buffer.2A"}, project)
                and exact_net("IR_CARRIER_VS", {"ir_carrier.VS", "ir_carrier_pullup.END_2", "ir_carrier_supply_cap.END_1", "ir_carrier_supply_res.END_2"}, project))
        else:
            expected = {"product_wiring_standard": "CTIA/AHJ", "tip": "left headphone", "ring1": "right headphone",
                        "ring2": "audio ground", "sleeve": "headset microphone plus bias"}
            checks["same_five_ctia_conductor_functions"] = all(old_ec.get(k) == value and new_ec.get(k) == value for k, value in expected.items())
            checks["tip2_switch5_closed_absent_open_inserted"] = (
                new_ec.get("tip_switch_closed_without_plug_physical_pads") == ["2", "5"]
                and new_ec.get("tip_switch_open_with_plug_physical_pads") == ["2", "5"])
            old_six = [route for route in candidate.get("fixed_routes", []) if "headphone_jack.RING1_SWITCH" in (route.get("from"), route.get("to"))]
            checks["removed_six_was_only_explicit_nc"] = (len(old_six) == 1 and old_six[0].get("to") == "abstract:no-connect"
                and old_six[0].get("from") == "headphone_jack.RING1_SWITCH" and old.get("contacts", {}).get("RING1_SWITCH") == {"physical": "6", "role": "signal"}
                and set(old.get("contacts", {})) == set(contacts) | {"RING1_SWITCH"})
            checks["native_10k_10k_100k_detector"] = (
                support("headphone_tip_detect_pullup", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL", project,
                        {"END_1": ("1", "3V3_MAIN"), "END_2": ("2", "HEADPHONE_LEFT_TIP")})
                and support("headset_detect_series", "yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL", project,
                            {"END_1": ("1", "HEADSET_SWITCH_STATE"), "END_2": ("2", "HEADSET_ABSENT")})
                and support("headset_absent_pulldown", "yageo_rc0402fr_07100kl", "Yageo RC0402FR-07100KL", project,
                            {"END_1": ("1", "HEADSET_ABSENT"), "END_2": ("2", "AUDIO_GROUND")})
                and support("slow_io", "tca6424argjr", "TCA6424ARGJR", project, {"P02": ("3", "HEADSET_ABSENT")}))
            checks["no_added_detect_node_loads"] = (
                exact_net("HEADSET_SWITCH_STATE", {"headphone_jack.TIP_SWITCH", "headset_detect_series.END_1"}, project)
                and exact_net("HEADSET_ABSENT", {"headset_detect_series.END_2", "headset_absent_pulldown.END_1", "slow_io.P02"}, project)
                and exact_net("HEADPHONE_LEFT_TIP", {"headphone_jack.TIP", "headphone_tip_detect_pullup.END_2", "headphone_l_series.END_2", "headphone_esd.D1_PLUS"}, project))
        result[domain] = {
            "status": "bounded_electrical_equivalence_verified" if all_true(checks) else "review_required",
            "legacy_device_id": spec["legacy_id"], "current_device_id": spec["current_id"],
            "checks": checks, "transfer_scope": spec["transfer_scope"], "not_transferred": spec["not_transferred"],
            "evidence": [{"url": url, "section": "Pinning/ordering/electrical characteristics pp.1-3" if domain == "ir" else "Exact model circuit and terminal table, p.2", "checked": "2026-09-08"} for url in spec["source_urls"]],
            "fabrication_ready": False,
        }
    return result


def panel_endpoint(display_mount: dict, panel_pin: int) -> str:
    """Resolve physical mating only; expected panel functions stay independent."""
    mapping = display_mount["electrical"].get("panel_to_connector_pin_map")
    if mapping != {str(pin): str(51 - pin) for pin in range(1, 51)}:
        raise ValueError("display requires the verified complete panel-to-FH34 51-n bijection")
    if type(panel_pin) is not int or panel_pin not in range(1, 51):
        raise ValueError("invalid physical display panel pin")
    return f"display_connector.PIN_{mapping[str(panel_pin)]}"


def display_topology_checks(native_nets: list[dict], display_mount: dict) -> dict:
    # These are exact panel-datasheet functions, not functions copied from the
    # configurable panel_pin_map or H2 generator. Only mating numbers transform.
    panel = {pin: panel_endpoint(display_mount, pin) for pin in range(1, 51)}
    return {
        "panel_vddi_40_41_on_canonical_main": all(endpoint_on_net(native_nets, panel[pin], "3V3_MAIN") for pin in (40, 41)),
        "panel_vci_42_on_canonical_main": endpoint_on_net(native_nets, panel[42], "3V3_MAIN"),
        "backlight_anode_is_latch_protected": endpoint_on_net(native_nets, "backlight_efuse.OUT", "LCD_LEDA_PROTECTED") and endpoint_on_net(native_nets, panel[1], "LCD_LEDA_PROTECTED"),
        "both_panel_cathodes_enter_one_series_resistor": all(endpoint_on_net(native_nets, panel[pin], "LCD_LEDK") for pin in (2, 3)) and endpoint_on_net(native_nets, "backlight_series_resistor.END_1", "LCD_LEDK"),
        "series_resistor_precedes_pwm_sink": endpoint_on_net(native_nets, "backlight_series_resistor.END_2", "LCD_LEDK_LIMITED") and endpoint_on_net(native_nets, "backlight_mosfet.D", "LCD_LEDK_LIMITED"),
        "pwm_sink_returns_to_ground": endpoint_on_net(native_nets, "backlight_mosfet.S", "POWER_GROUND"),
        "backlight_gate_fails_low": endpoint_on_net(native_nets, "backlight_mosfet.G", "LCD_BACKLIGHT_GATE") and endpoint_on_net(native_nets, "backlight_gate_pulldown.END_1", "LCD_BACKLIGHT_GATE"),
        "production_direct_zif_is_passive_i8080_8": display_mount["electrical"]["selected_mode"] == "ILI9488 8080 8-bit with IM2/IM1/IM0 = 0/1/1" and display_mount["electrical"]["added_active_devices"] == 0,
        "all_eight_i8080_data_lanes_reach_panel": all(
            endpoint_on_net(native_nets, panel[32 - lane], f"LCD_DB{lane}")
            and any(row.get("instance") == "s3" and row.get("net") == f"LCD_DB{lane}" for row in native_nets)
            for lane in range(8)
        ),
        "i8080_write_strobe_reaches_panel": endpoint_on_net(native_nets, panel[36], "LCD_WR_N") and any(row.get("instance") == "s3" and row.get("net") == "LCD_WR_N" for row in native_nets),
    }


def build() -> dict:
    candidate = load(CANDIDATE)
    devices = load(DEVICES)["devices"]
    rails = load(RAILS)
    provenance = load(PROVENANCE)
    audio = load(AUDIO)
    ir = load(IR)
    battery = load(BATTERY)
    airband = load(AIRBAND)
    native_nets = load(NATIVE_NETS)["rows"]
    native_instances = load(NATIVE_INSTANCES)["rows"]
    cost_rows = load(COST_AUDIT)["rows"]
    display_mount = load(DISPLAY_MOUNT)
    native_by_instance = {row["instance"]: row["device_id"] for row in native_instances}
    selected_non_pcba = {row["role"]: row["device_id"] for row in cost_rows}
    errors: list[str] = []

    current_hashes = {
        "hardware/architecture/candidates/G2F-3I.json": sha256(CANDIDATE),
        "hardware/architecture/devices.json": sha256(DEVICES),
    }
    leaf_results = {"audio": audio, "ir": ir, "battery": battery}
    leaf_checks = {}
    for name, result in leaf_results.items():
        hashes = result.get("source_hashes", {})
        leaf_checks[name] = {
            "reviewed": str(result.get("status", "")).startswith("reviewed"),
            "candidate_is_current": hashes.get("hardware/architecture/candidates/G2F-3I.json") == current_hashes["hardware/architecture/candidates/G2F-3I.json"],
            "device_register_is_current": hashes.get("hardware/architecture/devices.json") == current_hashes["hardware/architecture/devices.json"],
            "all_leaf_checks_pass": all_true(result.get("checks", {})),
        }
        if not all_true(leaf_checks[name]):
            errors.append(f"{name} leaf evidence is stale or failing")

    current_native_transfers = native_leaf_transfers(candidate, devices, native_instances, native_nets, leaf_results)
    for name, transfer in current_native_transfers.items():
        leaf_checks[name]["current_native_substitution_is_bound"] = transfer["status"] == "bounded_electrical_equivalence_verified"
        if not leaf_checks[name]["current_native_substitution_is_bound"]:
            errors.append(f"{name} current-native substitution requires review: " + ", ".join(
                key for key, passed in transfer["checks"].items() if not passed))

    exact_board_parts = {
        "backlight_efuse": "ti_tps2553drvr_1",
        "backlight_efuse_ilim": "uniroyal_0402wgf1333tce",
        "backlight_series_resistor": "fh_rs_06l2r70ft",
        "backlight_mosfet": "diodes_dmn2056u_7",
        "air_lo": "skyworks_si5351a_b_gtr",
        "air_lo_crystal": "suzhou_liming_3225_27_00_10_10_10_a",
    }
    exact_parts = {"display": "eastrising_er_tft035ips_6_ctp", **exact_board_parts}
    exact_part_checks = {
        "display": selected_non_pcba.get("display") == exact_parts["display"],
        **{name: native_by_instance.get(name) == device_id for name, device_id in exact_board_parts.items()},
    }
    if not all_true(exact_part_checks):
        errors.append("one or more H3-R2.3 exact part identities drifted")

    topology_checks = display_topology_checks(native_nets, display_mount)
    if not all_true(topology_checks):
        errors.append(
            "display supply/backlight topology drifted: "
            + ", ".join(name for name, passed in topology_checks.items() if not passed)
        )

    display = devices[exact_parts["display"]]["electrical_contract"]
    resistor = devices[exact_parts["backlight_series_resistor"]]["electrical_contract"]
    rail = rails["voltage_corners"]["3V3_MAIN"]
    v_min = float(rail["endpoint_min_v"])
    v_nom = float(rail["nominal_v"])
    v_max = float(rail["endpoint_max_v"])
    r_nom = float(resistor["resistance_ohm"])
    r_tol = float(resistor["tolerance_pct"]) / 100.0
    r_min = r_nom * (1.0 - r_tol)
    r_max = r_nom * (1.0 + r_tol)
    vf_typ = float(display["backlight_forward_voltage_typ_v"])
    normal_max_ma = float(display["backlight_normal_current_max_ma"])
    ilim_min_ma = 174.0
    ilim_max_ma = 234.0
    current_typ_vf = {
        "minimum_rail_ma": max(0.0, (v_min - vf_typ) / r_max * 1000.0),
        "nominal_rail_ma": max(0.0, (v_nom - vf_typ) / r_nom * 1000.0),
        "maximum_rail_ma": max(0.0, (v_max - vf_typ) / r_min * 1000.0),
    }
    fault_power_w = (ilim_max_ma / 1000.0) ** 2 * r_max
    normal_power_w = (normal_max_ma / 1000.0) ** 2 * r_max
    display_checks = {
        "vci_inside_published_range": v_min >= float(display["vci_operating_range_v"][0]) and v_max <= float(display["vci_operating_range_v"][1]),
        "vddi_inside_published_range": v_min >= float(display["vddi_operating_range_v"][0]) and v_max <= float(display["vddi_operating_range_v"][1]),
        "typical_vf_peak_below_panel_normal_max": current_typ_vf["maximum_rail_ma"] <= normal_max_ma,
        "normal_current_resistor_power_below_rating": normal_power_w < float(resistor["rated_power_w_at_70c"]),
        "gross_fault_resistor_power_below_rating_until_latch": fault_power_w < float(resistor["rated_power_w_at_70c"]),
        "efuse_minimum_threshold_above_panel_normal_max": ilim_min_ma > normal_max_ma,
    }
    if not all_true(display_checks):
        errors.append("display analog corner failed")

    crystal = devices[exact_parts["air_lo_crystal"]]["electrical_contract"]
    crystal_checks = {
        "frequency_inside_si5351_range": 25_000_000 <= int(crystal["frequency_hz"]) <= 27_000_000,
        "load_inside_si5351_range": 6 <= float(crystal["load_capacitance_pf"]) <= 12,
        "esr_below_si5351_limit": float(crystal["maximum_esr_ohm"]) <= 150,
        "crystal_drive_rating_covers_si5351_maximum": float(crystal["maximum_drive_level_uw"]) >= 100,
        "airband_filter_corner_passes": airband.get("status") == "pass" and float(airband.get("minimum_margin_db", -1)) > 0,
        "all_parameter_sources_are_closed": provenance.get("summary", {}).get("factory_catalog_only_parameter_sources") == 0,
    }
    if not all_true(crystal_checks):
        errors.append("Airband LO/filter analog corner failed")

    residuals = {
        "display": [
            "H6 preserves the 1206 series-resistor land as a controlled brightness trim point and routes the LED loop compactly",
            "H8 measures panel current, luminance, PWM noise and visible boot at the received panel Vf; the manufacturer publishes no minimum Vf, so paper analysis cannot prove minimum luminance at the simultaneous low-rail/high-Vf endpoint",
        ],
        "audio": audio.get("residual_physical_only", []),
        "ir": ir.get("residual_physical_only", []),
        "battery": battery.get("remaining_hil", []),
        "airband": [
            airband.get("residual"),
            "H8 records Si5351 startup and output-frequency calibration; the exact crystal start limits pass, while long-term aging is calibrated rather than guessed from an unpublished exact-code aging row",
        ],
    }
    return {
        "schema_version": 1,
        "artifact": "H3-R2-analog-corners",
        "marker": "H3-R2.3",
        "status": "pass" if not errors else "fail",
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (CANDIDATE, DEVICES, RAILS, PROVENANCE, AUDIO, IR, BATTERY, AIRBAND, NATIVE_NETS, NATIVE_INSTANCES, COST_AUDIT, DISPLAY_MOUNT)},
        "method": "current R2 display topology/identity binding, retained leaf interval calculations with explicit bounded current-native IR/audio substitution guards, and a production-panel backlight calculation; not whole-board electrical or manufacturing approval",
        "current_native_transfers": current_native_transfers,
        "exact_part_checks": exact_part_checks,
        "topology_checks": topology_checks,
        "display": {
            "rail_v": {"minimum": v_min, "nominal": v_nom, "maximum": v_max},
            "series_resistor": {"mpn": devices[exact_parts["backlight_series_resistor"]]["mpn"], "jlcpcb_part": "C323265", "nominal_ohm": r_nom, "minimum_ohm": r_min, "maximum_ohm": r_max, "rated_power_w": float(resistor["rated_power_w_at_70c"])},
            "current_at_published_typical_vf_ma": current_typ_vf,
            "panel_normal_current_max_ma": normal_max_ma,
            "efuse_latch_threshold_ma": {"minimum": ilim_min_ma, "maximum": ilim_max_ma},
            "resistor_power_w": {"at_panel_normal_max": normal_power_w, "at_efuse_max_until_latch": fault_power_w},
            "checks": display_checks,
            "minimum_luminance_boundary": "physical-only because the panel datasheet does not publish minimum forward voltage or a luminance-versus-current guarantee",
        },
        "leaf_evidence": {
            name: {"checks": checks, "review_summary": leaf_results[name].get("review_summary", {})}
            for name, checks in leaf_checks.items()
        },
        "airband": {"checks": crystal_checks, "filter_minimum_margin_db": airband.get("minimum_margin_db"), "crystal": crystal},
        "residual_physical_only": residuals,
        "errors": errors,
    }


def render(result: dict, language: str) -> str:
    ru = language == "ru"
    title = "Аналоговая проверка Leshy2 R2" if ru else "Leshy2 R2 analog verification"
    intro = (
        "H3‑R2.3 сводит перечисленные расчёты дисплея, аудио, IR, аккумуляторов и Airband. Перенос старых leaf-расчётов на текущие IR/аудиодетали проверяется отдельно и только в явно указанной электрической границе; это не полная проверка платы или разрешение производства."
        if ru else
        "H3-R2.3 consolidates the listed display, audio, IR, battery and Airband calculations. Transfer of retained leaf calculations to current IR/audio parts is checked separately within an explicit electrical scope; this is not whole-board verification or manufacturing approval."
    )
    d = result["display"]
    rows = [
        ("Дисплей / display", "PASS" if all_true(d["checks"]) and all_true(result["topology_checks"]) and all_true(result["exact_part_checks"]) else "REVIEW REQUIRED", f"{d['rail_v']['minimum']:.3f}…{d['rail_v']['maximum']:.3f} V; {d['current_at_published_typical_vf_ma']['nominal_rail_ma']:.1f} mA nominal backlight"),
        ("Аудио / audio", "BOUNDED PASS" if all_true(result["leaf_evidence"]["audio"]["checks"]) else "REVIEW REQUIRED", f"{result['leaf_evidence']['audio']['review_summary'].get('checks', 0)} retained leaf checks + current connector transfer guard"),
        ("IR", "BOUNDED PASS" if all_true(result["leaf_evidence"]["ir"]["checks"]) else "REVIEW REQUIRED", f"{result['leaf_evidence']['ir']['review_summary'].get('checks', 0)} retained leaf checks + current receiver transfer guard"),
        ("Аккумуляторы / battery", "PASS" if all_true(result["leaf_evidence"]["battery"]["checks"]) else "REVIEW REQUIRED", f"{result['leaf_evidence']['battery']['review_summary'].get('checks', 0)} retained leaf checks"),
        ("Airband", "PASS" if all_true(result["airband"]["checks"]) else "REVIEW REQUIRED", f"1,024 filter corners; {result['airband']['filter_minimum_margin_db']:.3f} dB minimum margin"),
    ]
    lines = [f"# {title}", "", intro, "", "| Домен | Статус | Результат |" if ru else "| Domain | Status | Result |", "|---|---:|---|"]
    lines += [f"| {name} | {status} | {detail} |" for name, status, detail in rows]
    lines += ["", "## Граница переноса текущих деталей" if ru else "## Current-part transfer boundary", ""]
    for name, transfer in result["current_native_transfers"].items():
        lines += [f"- `{name}`: `{transfer['legacy_device_id']}` → `{transfer['current_device_id']}`; **{transfer['status']}**. {transfer['transfer_scope']}"]
        lines += ["  " + ("Не переносится: " if ru else "Not transferred: ") + "; ".join(transfer["not_transferred"]) + "."]
    if result["errors"]:
        lines += ["", "Требует проверки: " if ru else "Review required: ", ""]
        lines += [f"- {error}" for error in result["errors"]]
    lines += [
        "",
        "## Подсветка" if ru else "## Backlight",
        "",
        (
            f"Прямой `0 Ω` удалён. Установлен фабрично доступный `RS-06L2R70FT` (`C323265`, 2,7 Ω ±1%, 250 мВт). При типовом Vf панели расчёт даёт {d['current_at_published_typical_vf_ma']['minimum_rail_ma']:.1f}…{d['current_at_published_typical_vf_ma']['maximum_rail_ma']:.1f} мА и не превышает опубликованные 120 мА. Даже при верхнем пороге защёлки защиты резистор рассеивает {d['resistor_power_w']['at_efuse_max_until_latch'] * 1000:.1f} мВт < 250 мВт."
            if ru else
            f"The uncontrolled `0 ohm` path is gone. Factory-stocked `RS-06L2R70FT` (`C323265`, 2.7 ohm +/-1%, 250 mW) is fitted. At the panel's published typical Vf the calculated range is {d['current_at_published_typical_vf_ma']['minimum_rail_ma']:.1f} to {d['current_at_published_typical_vf_ma']['maximum_rail_ma']:.1f} mA and remains below the published 120 mA maximum. Even at the protection latch upper threshold the resistor dissipates {d['resistor_power_w']['at_efuse_max_until_latch'] * 1000:.1f} mW < 250 mW."
        ),
        "",
        "## Что осталось измерить" if ru else "## What remains to measure",
        "",
        (
            "Эта сводка не закрывает остальные проверки H6/H8. В том числе остаются яркость и PWM‑шум реальной панели; шум/поп/температура аудио; дальность и окно IR; калибровка делителей/NTC и безопасное программирование MAX17320; паразитики Airband после разводки и запуск/калибровка кварца. Незакрытая привязка текущей детали выше — отдельная проверка схемы, не физическое измерение."
            if ru else
            "This summary does not close other H6/H8 checks. Remaining measurements include received-panel luminance and PWM noise; audio noise/pop/temperature; IR range and window; divider/NTC calibration and safe MAX17320 programming; routed Airband parasitics plus crystal startup/calibration. A current-part binding marked review-required above is a separate schematic review, not a physical-only measurement."
        ),
        "",
        "Generated by `hardware/verification/h3_r2_analog_corners.py`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    expected = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render(result, "en"),
        DOC_RU: render(result, "ru"),
    }
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale:", ", ".join(stale))
            return 1
    print(json.dumps({"status": result["status"], "errors": result["errors"]}, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
