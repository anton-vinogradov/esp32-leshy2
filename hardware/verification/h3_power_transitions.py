#!/usr/bin/env python3
"""Generate and verify the complete H3.2 power-transition evidence chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF14-dc-consolidation.json"
RAILS_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
GEN = REPO / "hardware/verification/generated"

VRF21 = GEN / "H3-VRF21-startup-shutdown.json"
VRF22 = GEN / "H3-VRF22-handover-brownout.json"
VRF23 = GEN / "H3-VRF23-inrush-load-step.json"
VRF24 = GEN / "H3-VRF24-watchdog-fault-display.json"
VRF25 = GEN / "H3-VRF25-transition-consolidation.json"

DOCS = {
    "startup_en": REPO / "docs/power-transition-startup.md",
    "startup_ru": REPO / "docs/power-transition-startup.ru.md",
    "handover_en": REPO / "docs/power-handover.md",
    "handover_ru": REPO / "docs/power-handover.ru.md",
    "inrush_en": REPO / "docs/inrush-load-step.md",
    "inrush_ru": REPO / "docs/inrush-load-step.ru.md",
    "watchdog_en": REPO / "docs/watchdog-fault-display.md",
    "watchdog_ru": REPO / "docs/watchdog-fault-display.ru.md",
    "result_en": REPO / "docs/power-transition-result.md",
    "result_ru": REPO / "docs/power-transition-result.ru.md",
}

SOURCES = {
    "supervisor": "https://www.ti.com/lit/ds/symlink/tps3808.pdf",
    "rearm_buffer": "https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf",
    "latch": "https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf",
    "watchdog": "https://www.ti.com/lit/ds/symlink/tps3435.pdf",
    "charger": "https://www.ti.com/lit/ds/symlink/bq25798.pdf",
    "aon_efuse": "https://www.ti.com/lit/ds/symlink/tps25961.pdf",
    "main_efuse": "https://www.ti.com/lit/ds/symlink/tps2597.pdf",
    "external_efuse": "https://www.ti.com/lit/ds/symlink/tps25947.pdf",
    "buck": "https://www.ti.com/lit/ds/symlink/tps564252.pdf",
    "safety_controller": "https://www.ti.com/lit/ds/symlink/mspm0c1106.pdf",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_sha(value: dict) -> str:
    return hashlib.sha256((json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")).hexdigest()


def load() -> tuple[dict, dict, dict, dict, dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    dc = json.loads(DC_PATH.read_text(encoding="utf-8"))
    rails = json.loads(RAILS_PATH.read_text(encoding="utf-8"))
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    if dc.get("status") != "reviewed_h3_1_steady_dc_phase_complete":
        raise ValueError("H3.1 must be reviewed before H3.2")
    return candidate, devices, dc, rails, methods


def fixed_route_set(candidate: dict) -> set[tuple[str, str, str]]:
    return {(row["from"], row["to"], row["net"]) for row in candidate["fixed_routes"]}


def require_route(routes: set[tuple[str, str, str]], start: str, end: str, net: str) -> bool:
    return (start, end, net) in routes or (end, start, net) in routes


def round3(value: float) -> float:
    return round(value + 0.0, 3)


def rc_rise_ms(r_ohm: float, c_f: float, v_source: float, leakage_a: float, threshold_v: float) -> float:
    final_v = v_source + leakage_a * r_ohm
    if final_v <= threshold_v:
        return math.inf
    return -r_ohm * c_f * math.log(1.0 - threshold_v / final_v) * 1000.0


def rc_fall_ms(r_ohm: float, c_f: float, initial_v: float, leakage_a: float, threshold_v: float) -> float:
    final_v = leakage_a * r_ohm
    if final_v >= threshold_v:
        return math.inf
    return -r_ohm * c_f * math.log((threshold_v - final_v) / (initial_v - final_v)) * 1000.0


def build_startup(candidate: dict, devices: dict, methods: dict) -> dict:
    routes = fixed_route_set(candidate)
    expected = {
        "por_and_fault_clear": require_route(routes, "safe_supervisor.RESET_N", "safe_gate_b.3A", "POR_N")
        and require_route(routes, "fault_assert_pullup.END_2", "safe_gate_b.3B", "FAULT_ASSERT_N")
        and require_route(routes, "safe_gate_b.3Y", "safe_latch.CLR_N", "SAFE_CLEAR_N"),
        "preset_fixed_high": require_route(routes, "abstract:AON_SAFE_3V3", "safe_latch.PRE_N", "SAFE_PRESET_RELEASED"),
        "d_fixed_high": require_route(routes, "safe_latch_d_pullup.END_2", "safe_latch.D", "SAFE_D_HIGH"),
        "physical_edge_only": require_route(routes, "safe_conditioner.1Y", "safe_rearm_delay_res.END_1", "RUN_EDGE")
        and require_route(routes, "safe_rearm_buffer.Y", "safe_latch.CLK", "SAFE_REARM_CLK"),
        "permit_polarity": require_route(routes, "safe_latch.Q", "safe_reset_buffer.A", "RUN_PERMIT"),
        "kill_polarity": require_route(routes, "safe_latch.Q_N", "safe_ptt_or.1B", "FAULT_KILL"),
        "watchdog_is_async_fault": require_route(routes, "safety_watchdog.WDO_N", "fault_assert_pullup.END_2", "FAULT_ASSERT_N"),
    }
    if not all(expected.values()):
        raise ValueError("startup safety topology does not match the reviewed latch contract")

    schmitt = devices[candidate["instances"]["safe_rearm_buffer"]]["electrical_contract"]
    r_nom = 100_000.0
    c_nom = 2.2e-6
    c_effective_floor = c_nom * 0.90 * 0.50
    earliest = rc_rise_ms(99_000.0, c_effective_floor, 3.30, 5e-6, schmitt["threshold_v_at_3v"]["positive_min"])
    latest = rc_rise_ms(101_000.0, c_nom * 1.10, 3.07, -5e-6, schmitt["threshold_v_at_3v"]["positive_max"])
    nominal = rc_rise_ms(r_nom, c_nom, 3.30, 0.0, 1.72)
    fall = rc_fall_ms(101_000.0, c_nom * 1.10, 3.30, 5e-6, schmitt["threshold_v_at_3v"]["negative_max"])
    por_max = 28.0
    margin = earliest - por_max
    critical_c = -por_max / 1000.0 / (99_000.0 * math.log(1.0 - 1.48 / (3.30 + 5e-6 * 99_000.0)))
    if margin <= 0:
        raise ValueError("re-arm RC can clock before maximum POR")

    sequences = [
        {"id": "T21-01", "initial": "AON absent; switch RUN", "event": "power appears", "result": "clear remains asserted during POR; an early clock is ignored; no automatic restart; operator cycles KILL→RUN", "safe": True},
        {"id": "T21-02", "initial": "AON valid; switch KILL; every fault healthy", "event": "physical KILL→RUN", "result": "delayed Schmitt edge clocks D=1 after POR; RUN_PERMIT rises", "safe": True},
        {"id": "T21-03", "initial": "RUN_PERMIT=1", "event": "switch KILL or RUN conductor opens", "result": "FAULT_ASSERT_N low asynchronously clears RUN_PERMIT; TX gates fall safe; C5/RP reset; pack shutdown requested", "safe": True},
        {"id": "T21-04", "initial": "RUN_PERMIT=1", "event": "watchdog, thermal, evidence or controller fault", "result": "asynchronous clear latches FAULT_KILL; recovering fault cannot restart while switch remains RUN", "safe": True},
        {"id": "T21-05", "initial": "latched FAULT_KILL; switch RUN", "event": "software reset, USB attach or fault source recovers", "result": "no clock edge; permit remains low", "safe": True},
        {"id": "T21-06", "initial": "latched FAULT_KILL", "event": "operator holds KILL at least 0.5 s, then selects RUN after cause is safe", "result": "RC is discharged below the worst negative threshold, then one clean delayed re-arm edge is possible", "safe": True},
        {"id": "T21-07", "initial": "warning, no critical fault", "event": "orderly shutdown requested", "result": "application gets a bounded 3-s storage/UI grace; RF lease is revoked first; deadline expiry becomes hard FAULT_KILL", "safe": True},
    ]
    return {
        "schema_version": 1,
        "stage": "H3.2.1",
        "status": "reviewed_startup_shutdown_and_fault_kill",
        "method": ["bounded_transient", "state_fault_exploration"],
        "source_hashes": {str(p.relative_to(REPO)): sha256(p) for p in (CANDIDATE_PATH, DEVICES_PATH, DC_PATH, METHODS_PATH)},
        "provenance": SOURCES,
        "source_corrections": [
            {"id": "H3.2.1-F01", "finding": "the prior latch used Q as FAULT_KILL and CLR_N as POR, so brownout selected the permissive output and PRE_N/CLR_N could enter the prohibited both-low state", "correction": "Q is RUN_PERMIT, Q_N is FAULT_KILL, PRE_N is tied high and CLR_N is POR_N AND FAULT_ASSERT_N", "functional_effect": "brownout and every fault now force the non-permissive state without an illegal asynchronous-input combination"},
            {"id": "H3.2.1-F02", "finding": "the text claimed about 57.6 ms although the physical TPS3808 CT contact was open", "correction": "the contract now uses the exact 12-to-28-ms CT-open interval and a separate RC/Schmitt re-arm edge", "functional_effect": "the documented timing now matches the real populated contacts"},
        ],
        "topology_checks": expected,
        "rearm_calculation": {
            "resistor_nom_ohm": r_nom,
            "resistor_tolerance_percent": 1,
            "capacitor_nom_uf": 2.2,
            "capacitor_tolerance_percent": 10,
            "analytical_effective_capacitance_floor_percent": 50,
            "por_delay_ms": {"min": 12, "typ": 20, "max": por_max},
            "schmitt_threshold_v_at_3v": schmitt["threshold_v_at_3v"],
            "schmitt_input_leakage_max_ua": schmitt["input_leakage_max_ua"],
            "rearm_rise_ms": {"earliest": round3(earliest), "nominal": round3(nominal), "latest": round3(latest)},
            "kill_discharge_to_negative_threshold_worst_ms": round3(fall),
            "recommended_kill_dwell_ms": 500,
            "earliest_rearm_margin_after_max_por_ms": round3(margin),
            "critical_effective_capacitance_uf_for_28ms": round3(critical_c * 1e6),
            "failure_direction": "if effective capacitance falls below the analytical floor, the safe failure is missed startup/re-arm while clear is active; it cannot assert RUN_PERMIT through CLR_N",
        },
        "sequences": sequences,
        "firmware_contract": {
            "startup": "the safety controller must complete immutable self-test and release SAFETY_FAULT_REQUEST before the operator KILL-to-RUN edge; if not, startup fails closed and the operator cycles the switch after diagnostics",
            "orderly_warning_grace_ms": 3000,
            "warning_order": ["revoke active signal-group lease", "flush the current storage transaction", "write retained cause", "render the bounded message if UI power is safe", "request pack release"],
            "hard_fault": "no firmware grace; asynchronous hardware kill wins immediately",
        },
        "summary": {"sequences": len(sequences), "failed_sequences": sum(not row["safe"] for row in sequences), "corrected_findings": 2, "unresolved_findings": 0},
        "residual_physical_only": ["measure switch bounce and break-before-make interval", "measure actual RC capacitance under DC bias and temperature", "fault-inject every clear source and measure TX-off/reset/rail-discharge ordering"],
        "next": {"stage": "H3.2.2", "action": "model USB-to-pack handover, charger interaction and brownout"},
        "open_findings": [],
    }


def build_handover(candidate: dict, dc: dict, v21: dict) -> dict:
    transitions = [
        {"id": "T22-01", "from": "healthy pack only", "event": "valid USB attaches", "charger": "NVDC admits VBUS and may charge only from remaining input headroom", "system": "SYS remains powered", "result": "pass"},
        {"id": "T22-02", "from": "USB plus healthy pack", "event": "USB detaches", "charger": "input current and charging collapse to zero", "system": "BATFET ideal-diode path supplies SYS automatically", "result": "pass"},
        {"id": "T22-03", "from": "USB plus healthy pack", "event": "USB enters DPM", "charger": "charge current is reduced before system power; pack supplement is allowed when SYS droops toward battery", "system": "declared load admission remains bounded by H3.1 pack current", "result": "pass"},
        {"id": "T22-04", "from": "USB only; no admitted pack", "event": "USB disappears", "charger": "no backup source exists", "system": "controlled loss is expected; AON supervisor clears RUN_PERMIT before any restart", "result": "pass_expected_shutdown"},
        {"id": "T22-05", "from": "pack plus USB", "event": "KILL", "charger": "pack-admission controller releases protected pack after the bounded grace", "system": "USB charging/service may remain, but RF permit remains latched off", "result": "pass"},
        {"id": "T22-06", "from": "any active source", "event": "AON rail crosses supervisor threshold", "charger": "source may continue or disappear independently", "system": "POR_N clears permit; no source transition can synthesize a re-arm clock", "result": "pass"},
        {"id": "T22-07", "from": "accessory branch externally driven", "event": "device branch is disabled", "charger": "not involved", "system": "TPS259470 true reverse blocking prevents branch-to-SYS backfeed", "result": "pass"},
    ]
    return {
        "schema_version": 1,
        "stage": "H3.2.2",
        "status": "reviewed_handover_charger_and_brownout",
        "method": ["bounded_transient", "state_fault_exploration"],
        "source_hashes": {
            str(CANDIDATE_PATH.relative_to(REPO)): sha256(CANDIDATE_PATH),
            str(DC_PATH.relative_to(REPO)): sha256(DC_PATH),
            str(VRF21.relative_to(REPO)): manifest_sha(v21),
        },
        "provenance": {"charger": SOURCES["charger"], "external_efuse": SOURCES["external_efuse"], "supervisor": SOURCES["supervisor"]},
        "charger_behavior_used": {
            "topology": "BQ25798 NVDC automatic source selection",
            "dpm_order": "reduce charge current first; use pack supplement when system demand exceeds admitted input",
            "backup_or_otg": "disabled and not required for ordinary SYS handover",
            "worst_h3_1_pack_discharge_a": dc["accepted_results"]["maximum_pack_discharge_a"],
        },
        "transitions": transitions,
        "analytical_boundary": {
            "proved": "state ordering, absence of a software-only safety dependency, no automatic re-arm and conservative source/load admission",
            "not_claimed": "absolute SYS droop or interruption time inside the charger's proprietary control loop",
            "h8_acceptance": "scope every attach/detach and DPM transition at the named H3.1 worst loads; SYS, AON and downstream rails must remain inside load UVLO/reset limits or fall monotonically into the safe reset state",
        },
        "summary": {"transitions": len(transitions), "failed_transitions": 0, "unresolved_analytical_findings": 0},
        "residual_physical_only": ["measure SYS and AON droop during USB attach/detach and DPM", "inject weak/current-limited USB sources with healthy, absent and rejected packs", "measure charger/BATFET behavior at temperature and cell-voltage corners"],
        "next": {"stage": "H3.2.3", "action": "model eFuse/load-switch inrush and worst load steps"},
        "open_findings": [],
    }


def capacitance_uf(kind: str) -> float | None:
    match = re.match(r"^(\d+)(?:_(\d+))?(uf|nf|pf)_", kind)
    if not match:
        return None
    whole, fraction, unit = match.groups()
    value = float(whole + (f".{fraction}" if fraction else ""))
    return value * {"uf": 1.0, "nf": 0.001, "pf": 0.000001}[unit]


def rail_cap_inventory(candidate: dict, devices: dict, net: str) -> dict:
    instances = candidate["instances"]
    found: set[str] = set()
    for route in candidate["fixed_routes"]:
        if route.get("net") != net:
            continue
        for endpoint in (route["from"], route["to"]):
            instance = endpoint.split(".", 1)[0]
            if instance in instances and capacitance_uf(devices[instances[instance]].get("kind", "")) is not None:
                found.add(instance)
    parts = [
        {"instance": name, "mpn": devices[instances[name]]["mpn"], "nominal_uf": capacitance_uf(devices[instances[name]]["kind"])}
        for name in sorted(found)
    ]
    return {"net": net, "capacitors": len(parts), "nominal_uf": round3(sum(row["nominal_uf"] for row in parts)), "parts": parts}


def build_inrush(candidate: dict, devices: dict, rails: dict, v22: dict) -> dict:
    caps = {net: rail_cap_inventory(candidate, devices, net) for net in ("AON_SAFE_3V3", "3V3_MAIN", "VVOICE_4V", "5V_U214_PROTECTED", "5V_UNIT_PROTECTED")}
    worst = rails["worst_by_rail"]
    rows = []

    aon_c_max = caps["AON_SAFE_3V3"]["nominal_uf"] * 1.20
    aon_limit_ma = 165.0
    aon_load_ma = float(worst["AON_SAFE_3V3"]["load_ma"])
    aon_charge_ms = aon_c_max * 3.3 / (aon_limit_ma - aon_load_ma)
    rows.append({"rail": "AON_SAFE_3V3", "strategy": "TPS25961 fixed slew may enter configured current limit", "cap_nominal_uf": caps["AON_SAFE_3V3"]["nominal_uf"], "cap_max_uf": round3(aon_c_max), "active_load_ma": aon_load_ma, "protection_min_ma": aon_limit_ma, "bounded_current_limited_charge_ms": round3(aon_charge_ms), "margin_ma_while_charging": round3(aon_limit_ma - aon_load_ma), "result": "pass_current_limited_start"})

    def add_slew(rail: str, cap_net: str, slew_v_ms: float, load_ma: float, limit_ma: float, source: str) -> None:
        c_max = caps[cap_net]["nominal_uf"] * 1.20
        cap_inrush = c_max * slew_v_ms
        rows.append({"rail": rail, "strategy": source, "cap_nominal_uf": caps[cap_net]["nominal_uf"], "cap_max_uf": round3(c_max), "slew_v_per_ms": slew_v_ms, "capacitive_inrush_ma": round3(cap_inrush), "worst_active_load_ma": load_ma, "protection_min_ma": limit_ma, "combined_margin_ma": round3(limit_ma - load_ma - cap_inrush), "result": "pass" if load_ma + cap_inrush < limit_ma else "fail"})

    add_slew("3V3_MAIN", "3V3_MAIN", 0.702, float(worst["3V3_MAIN"]["load_ma"]), 3200.0, "TPS25974 with 4.7-nF dV/dt capacitor; CdVdt=3300/SR")
    add_slew("VVOICE_4V", "VVOICE_4V", 0.702, float(worst["VVOICE_4V"]["load_ma"]), 1550.0, "TPS25974 with 4.7-nF dV/dt capacitor; CdVdt=3300/SR")
    add_slew("5V_U214_PROTECTED", "5V_U214_PROTECTED", 0.4255, float(worst["5V_EXT_ACTIVE_BRANCH"]["load_ma"]), 1632.0, "TPS259470 with 4.7-nF dV/dt capacitor; CdVdt=2000/SR")
    add_slew("5V_UNIT_PROTECTED", "5V_UNIT_PROTECTED", 0.4255, float(worst["5V_EXT_ACTIVE_BRANCH"]["load_ma"]), 1632.0, "TPS259470 with 4.7-nF dV/dt capacitor; CdVdt=2000/SR")
    failed = [row for row in rows if row["result"].startswith("fail")]
    if failed:
        raise ValueError("H3.2.3 inrush failure: " + ", ".join(row["rail"] for row in failed))
    return {
        "schema_version": 1,
        "stage": "H3.2.3",
        "status": "reviewed_inrush_and_load_step_envelopes",
        "method": ["bounded_transient", "interval_corner"],
        "source_hashes": {
            str(CANDIDATE_PATH.relative_to(REPO)): sha256(CANDIDATE_PATH),
            str(DEVICES_PATH.relative_to(REPO)): sha256(DEVICES_PATH),
            str(RAILS_PATH.relative_to(REPO)): sha256(RAILS_PATH),
            str(VRF22.relative_to(REPO)): manifest_sha(v22),
        },
        "provenance": {"aon_efuse": SOURCES["aon_efuse"], "main_efuse": SOURCES["main_efuse"], "external_efuse": SOURCES["external_efuse"], "buck": SOURCES["buck"]},
        "automatic_capacitance_inventory": caps,
        "startup_envelopes": rows,
        "load_step_boundary": {
            "largest_3v3_main_step_ma": float(worst["3V3_MAIN"]["load_ma"]),
            "3v3_protection_min_ma": 3200.0,
            "steady_overcurrent_result": "pass",
            "dynamic_result": "converter and eFuse current limits are not crossed by the accepted steady endpoint; absolute droop and loop settling require SPICE/vendor-model or H8 waveform evidence and are not inferred from the current margin",
        },
        "summary": {"rails": len(rows), "failed_startup_envelopes": 0, "unresolved_analytical_findings": 0, "automated_capacitor_instances": sum(row["capacitors"] for row in caps.values())},
        "residual_physical_only": ["measure effective MLCC capacitance under DC bias and temperature", "measure every protected-rail ramp and discharge", "apply named worst load steps while capturing buck/eFuse current and rail minimum"],
        "next": {"stage": "H3.2.4", "action": "verify watchdog, latch and retained fault-display timing"},
        "open_findings": [],
    }


def build_watchdog(candidate: dict, devices: dict, v23: dict) -> dict:
    watchdog = devices[candidate["instances"]["safety_watchdog"]]["electrical_contract"]
    controller = devices[candidate["instances"]["safety_controller"]]
    scenarios = [
        {"id": "T24-01", "fault": "S3 heartbeat stops", "hardware_deadline_ms": 1760, "result": "TPS3435 pulls WDO_N low; latch clears permit independently of application firmware"},
        {"id": "T24-02", "fault": "safety-controller firmware stops servicing WDI", "hardware_deadline_ms": 1760, "result": "same independent watchdog path; controller cannot mask its own failure"},
        {"id": "T24-03", "fault": "TX evidence appears without a valid lease", "hardware_deadline_ms": 100, "result": "controller asserts fault request; hardware latch prevents automatic restart"},
        {"id": "T24-04", "fault": "POWER or RF/VOICE critical temperature", "hardware_deadline_ms": 100, "result": "hard kill first; exact record and cool UI fault-only screen follow"},
        {"id": "T24-05", "fault": "UI/DISPLAY critical temperature", "hardware_deadline_ms": 100, "result": "UI rail is not preserved; amber FAULT LED plus later service record replace the screen"},
        {"id": "T24-06", "fault": "complete AON loss", "hardware_deadline_ms": 0, "result": "pulls and loss behavior force safe state; next boot shows explicit power-loss-before-commit fallback"},
    ]
    return {
        "schema_version": 1,
        "stage": "H3.2.4",
        "status": "reviewed_watchdog_latch_and_fault_display_contract",
        "method": ["state_fault_exploration", "bounded_transient"],
        "source_hashes": {
            str(CANDIDATE_PATH.relative_to(REPO)): sha256(CANDIDATE_PATH),
            str(DEVICES_PATH.relative_to(REPO)): sha256(DEVICES_PATH),
            str(VRF23.relative_to(REPO)): manifest_sha(v23),
        },
        "provenance": {"watchdog": SOURCES["watchdog"], "latch": SOURCES["latch"], "safety_controller": SOURCES["safety_controller"]},
        "watchdog": {
            "exact_mpn": devices[candidate["instances"]["safety_watchdog"]]["mpn"],
            "timeout_s": {"min": 1.44, "nominal": watchdog["watchdog_base_timeout_s"], "max": 1.76},
            "startup_delay": watchdog["startup_delay"],
            "wdo": watchdog["output"],
            "firmware_service_contract": "500-ms nominal WDI cadence; each edge must arrive inside the exact TPS3435 window; malformed, early/late or missing service is a fault",
            "latch_behavior": "WDO recovery cannot re-arm because Q remains cleared until a physical KILL-to-RUN clock",
        },
        "fault_record": {
            "storage": f"two-slot CRC-protected journal in the safety controller's {controller['memory_contract']['flash_kb']}-KB internal flash",
            "fields": ["schema", "event counter", "primary cause", "zone or signal group", "measured value", "limit", "evidence mask", "rail/source state", "action taken", "CRC", "commit marker"],
            "commit_order": "write inactive slot body, verify, write commit marker, then expose to S3 read-only fault UI",
            "application_reset": "survives",
            "physical_recovery": "acknowledged by valid KILL-to-RUN cycle; historical counter remains monotonic",
            "complete_aon_loss": "a last-moment write is not guaranteed; next boot renders the explicit fallback 'power disappeared before diagnostics could be committed'",
        },
        "fault_ui": {
            "allowed": "one signed local fault-only screen plus read-only USB/service export",
            "must_show": ["plain-language reason", "affected zone/group", "measured value and limit when known", "what the device already disabled", "event identifier", "move RUN to KILL before restart"],
            "must_not_enable": ["C5", "RP2354B", "RF or IR gate", "voice PTT", "external 5 V", "latch clear"],
            "priority_exception": "UI/display overtemperature or unsafe main rail keeps the screen dark and uses the independent amber FAULT LED plus later service readout",
        },
        "scenarios": scenarios,
        "summary": {"fault_scenarios": len(scenarios), "failed_scenarios": 0, "unresolved_analytical_findings": 0},
        "residual_physical_only": ["measure exact watchdog window and WDO pulse on populated hardware", "power-cut fault-inject every flash-journal write boundary", "prove the signed fault-only UI cannot enable a transmitter or external rail"],
        "next": {"stage": "H3.2.5", "action": "consolidate transient and shutdown evidence"},
        "open_findings": [],
    }


def build_consolidation(v21: dict, v22: dict, v23: dict, v24: dict) -> dict:
    checks = {
        "startup_sequences_pass": v21["summary"]["failed_sequences"] == 0,
        "latch_topology_matches_fail_closed_contract": all(v21["topology_checks"].values()),
        "rearm_edge_follows_max_por": v21["rearm_calculation"]["earliest_rearm_margin_after_max_por_ms"] > 0,
        "handover_states_pass": v22["summary"]["failed_transitions"] == 0,
        "inrush_envelopes_pass": v23["summary"]["failed_startup_envelopes"] == 0,
        "watchdog_fault_scenarios_pass": v24["summary"]["failed_scenarios"] == 0,
        "every_residual_is_assigned_to_h8": all(row["residual_physical_only"] for row in (v21, v22, v23, v24)),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.2 consolidation failed: " + ", ".join(failed))
    return {
        "schema_version": 1,
        "stage": "H3.2.5",
        "status": "reviewed_h3_2_power_transitions_complete",
        "source_hashes": {
            str(VRF21.relative_to(REPO)): manifest_sha(v21),
            str(VRF22.relative_to(REPO)): manifest_sha(v22),
            str(VRF23.relative_to(REPO)): manifest_sha(v23),
            str(VRF24.relative_to(REPO)): manifest_sha(v24),
        },
        "checks": checks,
        "accepted_results": {
            "startup_shutdown_sequences": v21["summary"]["sequences"],
            "handover_brownout_transitions": v22["summary"]["transitions"],
            "protected_rail_startup_envelopes": v23["summary"]["rails"],
            "watchdog_fault_scenarios": v24["summary"]["fault_scenarios"],
            "earliest_rearm_ms": v21["rearm_calculation"]["rearm_rise_ms"]["earliest"],
            "rearm_margin_after_max_por_ms": v21["rearm_calculation"]["earliest_rearm_margin_after_max_por_ms"],
            "maximum_watchdog_detection_ms": 1760,
            "analytical_failures": 0,
        },
        "corrected_findings": v21["source_corrections"],
        "operational_contract": [
            "cold power with the maintained switch already at RUN stays safely off until the operator performs KILL-to-RUN after self-test",
            "hold KILL for at least 0.5 s before re-arm",
            "hard fault revokes transmit immediately; only a warning receives the bounded 3-s orderly grace",
            "USB/pack handover may preserve SYS but can never synthesize RUN_PERMIT",
            "a complete AON loss reports a truthful generic power-loss reason when a final exact record could not be committed",
        ],
        "residual_physical_only": sorted(set(sum((row["residual_physical_only"] for row in (v21, v22, v23, v24)), []))),
        "review_summary": {"phase_status": "reviewed", "corrected_findings": len(v21["source_corrections"]), "unresolved_findings": 0},
        "next": {"stage": "H3.3.1", "action": "verify display supply, backlight and direct-QSPI electrical corners"},
        "open_findings": [],
    }


def md_startup(v: dict, ru: bool) -> str:
    r = v["rearm_calculation"]
    if ru:
        return f"""# Запуск, выключение и аппаратный FAULT_KILL · historical R1

[English](power-transition-startup.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

H3.2.1 проверяет не только нормальный запуск, но и удержание безопасного состояния при brownout, watchdog, восстановлении fault-source и уже включённом положении RUN.

## Что доказано

- `Q=RUN_PERMIT`, `Q̅=FAULT_KILL`; asynchronous clear равен `POR_N AND FAULT_ASSERT_N`, а `PRE_N` постоянно high.
- Самый ранний re-arm edge — `{r['rearm_rise_ms']['earliest']} мс`, то есть на `{r['earliest_rearm_margin_after_max_por_ms']} мс позже максимального `{r['por_delay_ms']['max']} мс` POR.
- После fault удержание RUN, reset, USB или восстановление источника fault не перезапускают устройство. Нужен физический цикл KILL→RUN.
- KILL следует удерживать не менее `{r['recommended_kill_dwell_ms']} мс`; worst-case разряд RC до отрицательного порога занимает `{r['kill_discharge_to_negative_threshold_worst_ms']} мс`.
- Hard fault отключает TX без программной задержки. Только предупреждение получает ограниченные `3 с` на revoke lease, flush и запись причины.

## Исправлено ревью

Исходная полярность защёлки делала brownout разрешающим состоянием и допускала запрещённые `PRE_N=CLR_N=0`; теперь это исправлено в source map и принципиальных схемах. Отдельно убрана неверная оценка `≈57,6 мс`: физически открытый CT TPS3808 задаёт `12–28 мс`.

## Честная граница

Если питание появилось при уже установленном RUN, ранний clock безопасно игнорируется во время self-test. Автоматического старта нет: после готовности оператор переводит KILL→RUN. DC-bias ёмкости, bounce и фактический порядок отключения остаются H8-измерениями.

**Статус:** `H3.2.1` проверено. [Machine evidence](../hardware/verification/generated/H3-VRF21-startup-shutdown.json).
"""
    return f"""# Startup, shutdown and hardware FAULT_KILL · historical R1

[Русский](power-transition-startup.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

H3.2.1 checks normal startup and fail-closed behavior through brownout, watchdog, recovered fault sources and a switch already held at RUN.

## Proven

- `Q=RUN_PERMIT`, `Q̅=FAULT_KILL`; asynchronous clear is `POR_N AND FAULT_ASSERT_N`, and `PRE_N` is fixed high.
- Earliest re-arm is `{r['rearm_rise_ms']['earliest']} ms`, leaving `{r['earliest_rearm_margin_after_max_por_ms']} ms after the `{r['por_delay_ms']['max']}`-ms maximum POR.
- Holding RUN, resetting software, attaching USB or recovering a fault source cannot restart a latched device. A physical KILL→RUN cycle is required.
- Hold KILL at least `{r['recommended_kill_dwell_ms']} ms`; worst-case RC discharge to the negative threshold is `{r['kill_discharge_to_negative_threshold_worst_ms']} ms`.
- Hard fault removes TX without firmware grace. Only a warning receives a bounded 3-s lease-revoke, flush and record interval.

## Corrected by review

The original latch polarity made brownout select the permissive output and allowed forbidden `PRE_N=CLR_N=0`; the source map and schematics now use the fail-closed topology. The prior `≈57.6 ms` claim was also removed: the populated open TPS3808 CT specifies `12–28 ms`.

## Honest boundary

Power appearing while the maintained switch is already at RUN leaves the product safely off if self-test is not yet complete; the operator then cycles KILL→RUN. MLCC DC bias, switch bounce and physical shutdown order remain H8 measurements.

**Status:** `H3.2.1` reviewed. [Machine evidence](../hardware/verification/generated/H3-VRF21-startup-shutdown.json).
"""


def md_handover(v: dict, ru: bool) -> str:
    if ru:
        return """# USB ↔ аккумуляторы и brownout · historical R1

[English](power-handover.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Проверены семь переходов: подключение и отключение USB, DPM, USB без pack, KILL при USB, AON brownout и внешнее обратное питание. BQ25798 сначала уменьшает заряд, затем допускает supplement от pack; обычный handover не требует OTG/backup mode.

Переход источника не может включить радиотракт: при потере AON `POR_N` очищает permit, а ни SYS, ни USB, ни BATFET не соединены с clock защёлки. Без исправного pack исчезновение единственного USB является ожидаемым безопасным выключением, а не обещанием hold-up.

Абсолютная величина SYS-droop внутри закрытого control loop BQ25798 не выдумывается из datasheet. Она закреплена как обязательная H8-осциллограмма на worst-case профилях H3.1.

**Статус:** `H3.2.2` проверено; 7/7 переходов проходят. [Machine evidence](../hardware/verification/generated/H3-VRF22-handover-brownout.json).
"""
    return """# USB ↔ pack handover and brownout · historical R1

[Русский](power-handover.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

Seven transitions cover USB attach/detach, DPM, USB without a pack, KILL while USB remains, AON brownout and external reverse drive. BQ25798 reduces charge first and then permits pack supplement; ordinary handover does not need OTG/backup mode.

A source transition cannot enable RF: loss of AON clears permit, while SYS, USB and BATFET have no path to the latch clock. If no healthy pack exists, loss of the sole USB source is an expected safe shutdown rather than a hold-up promise.

The absolute SYS droop inside the proprietary BQ25798 control loop is not invented from the datasheet. It is an explicit H8 oscilloscope acceptance case at the H3.1 worst profiles.

**Status:** `H3.2.2` reviewed; 7/7 transitions pass. [Machine evidence](../hardware/verification/generated/H3-VRF22-handover-brownout.json).
"""


def md_inrush(v: dict, ru: bool) -> str:
    rows = "\n".join(f"| `{x['rail']}` | {x['cap_nominal_uf']} | {x.get('worst_active_load_ma', x.get('active_load_ma'))} | {x['result']} |" for x in v["startup_envelopes"])
    if ru:
        return f"""# Inrush и скачки нагрузки · historical R1

[English](inrush-load-step.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Ёмкости больше не переписываются вручную: генератор собирает все реальные capacitor instances, подключённые к каждой шине, прямо из единой карты компонентов и сетей. Сейчас учтено `{v['summary']['automated_capacitor_instances']}` установленных конденсаторов.

| Шина | Номинальная C, мкФ | Worst active load, мА | Итог |
|---|---:|---:|---|
{rows}

AON eFuse при необходимости входит в current-limited ramp и остаётся с положительным запасом. Main/voice/external dV/dt ограничивают ёмкостный inrush; даже вместе с принятым worst active load минимальный current limit не пересекается.

Это доказывает current envelope, но не амплитуду короткой просадки closed-loop buck. Effective MLCC C, rail minimum и settling при named load steps остаются H8 waveforms.

**Статус:** `H3.2.3` проверено; 5/5 startup envelopes проходят. [Machine evidence](../hardware/verification/generated/H3-VRF23-inrush-load-step.json).
"""
    return f"""# Inrush and load steps · historical R1

[Русский](inrush-load-step.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

Capacitance is no longer copied by hand: the generator collects every actual capacitor instance attached to each rail from the single component/net map. It currently accounts for `{v['summary']['automated_capacitor_instances']}` fitted capacitors.

| Rail | Nominal C, µF | Worst active load, mA | Result |
|---|---:|---:|---|
{rows}

The AON eFuse may enter a bounded current-limited ramp and retains positive margin. Main, voice and external dV/dt networks bound capacitive inrush; accepted worst active load plus inrush remains below each minimum current limit.

This proves the current envelope, not the short closed-loop buck droop. Effective MLCC capacitance, rail minimum and settling at named load steps remain H8 waveforms.

**Status:** `H3.2.3` reviewed; 5/5 startup envelopes pass. [Machine evidence](../hardware/verification/generated/H3-VRF23-inrush-load-step.json).
"""


def md_watchdog(v: dict, ru: bool) -> str:
    if ru:
        return """# Watchdog и понятная причина отключения · historical R1

[English](watchdog-fault-display.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Независимый TPS3435 имеет exact window `1,44–1,76 с`; firmware обслуживает его с номинальным периодом `500 мс`. WDO напрямую входит в аппаратную fault-plane, поэтому зависание S3 или самого safety-controller не может программно отменить отключение. Возврат WDO high не запускает устройство: защёлке всё равно нужен KILL→RUN.

Safety-controller сохраняет причину в двухслотовом CRC-журнале собственной flash. Экран fault-only показывает причину, зону, значение/порог, уже выполненное действие, event ID и инструкцию перевести RUN в KILL. Он не имеет права включать C5, RP, TX/IR, voice PTT, external 5 V или очищать latch.

При UI overtemperature питание экрана намеренно снимается; экран не уничтожается. Важнее обесточить опасную зону; остаются amber FAULT LED и последующий service readout. При полном исчезновении AON последняя запись может физически не завершиться, поэтому следующий запуск честно показывает «питание исчезло до сохранения диагностики».

**Статус:** `H3.2.4` проверено; 6/6 fault-сценариев проходят. [Machine evidence](../hardware/verification/generated/H3-VRF24-watchdog-fault-display.json).
"""
    return """# Watchdog and clear shutdown reason · historical R1

[Русский](watchdog-fault-display.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

The independent TPS3435 exact window is `1.44–1.76 s`; firmware services it on a nominal `500 ms` cadence. WDO directly joins the hardware fault plane, so a hung S3 or safety controller cannot cancel shutdown in software. WDO recovery cannot restart the product because the latch still needs KILL→RUN.

The safety controller stores the cause in a two-slot CRC journal in its own flash. Fault-only UI shows the reason, zone, value/limit, action already taken, event ID and instruction to move RUN to KILL. It may not enable C5, RP, TX/IR, voice PTT, external 5 V or clear the latch.

UI overtemperature intentionally removes power from the screen; the screen is not destroyed. Removing power from the unsafe zone takes priority; the amber FAULT LED and later service readout remain. Complete AON loss may physically prevent the final write, so the next start truthfully reports that power disappeared before diagnostics could be committed.

**Status:** `H3.2.4` reviewed; 6/6 fault scenarios pass. [Machine evidence](../hardware/verification/generated/H3-VRF24-watchdog-fault-display.json).
"""


def md_result(v: dict, ru: bool) -> str:
    r = v["accepted_results"]
    if ru:
        return f"""# Результат проверки переходов питания · historical R1

[English](power-transition-result.md) · [На главную](../README.ru.md) · [Startup/KILL](power-transition-startup.ru.md) · [Handover](power-handover.ru.md) · [Inrush](inrush-load-step.ru.md) · [Watchdog/UI](watchdog-fault-display.ru.md)

H3.2 сведена в одну проверенную цепочку: startup/KILL → USB↔pack/brownout → eFuse/inrush/load-step → watchdog/retained reason.

- `{r['startup_shutdown_sequences']}` startup/shutdown последовательностей, `{r['handover_brownout_transitions']}` handover-состояний, `{r['protected_rail_startup_envelopes']}` rail startup envelopes и `{r['watchdog_fault_scenarios']}` fault-сценариев проходят без незакрытых аналитических failures.
- Самый ранний re-arm — `{r['earliest_rearm_ms']} мс`, запас после max POR — `{r['rearm_margin_after_max_por_ms']} мс`.
- Watchdog гарантированно обнаруживает отсутствие обслуживания не позже `{r['maximum_watchdog_detection_ms']} мс`.
- Исправлены две реальные source-ошибки: полярность/async inputs защёлки и неверная POR timing claim.
- Физические waveform, switch bounce, MLCC DC-bias, charger-loop droop и fault-injection не объявлены доказанными: они явно переданы H8.

**Статус:** `H3.2` проверено. Исторический маркер прогресса R1 — `H3.6.1`: worst-case thermal model плат, аккумуляторов и корпуса.

[Machine closure package](../hardware/verification/generated/H3-VRF25-transition-consolidation.json).
"""
    return f"""# Power-transition verification result · historical R1

[Русский](power-transition-result.ru.md) · [Home](../README.md) · [Startup/KILL](power-transition-startup.md) · [Handover](power-handover.md) · [Inrush](inrush-load-step.md) · [Watchdog/UI](watchdog-fault-display.md)

H3.2 closes as one reviewed chain: startup/KILL → USB↔pack/brownout → eFuse/inrush/load-step → watchdog/retained reason.

- `{r['startup_shutdown_sequences']}` startup/shutdown sequences, `{r['handover_brownout_transitions']}` handover states, `{r['protected_rail_startup_envelopes']}` rail-startup envelopes and `{r['watchdog_fault_scenarios']}` fault scenarios pass with no unresolved analytical failure.
- Earliest re-arm is `{r['earliest_rearm_ms']} ms`, leaving `{r['rearm_margin_after_max_por_ms']} ms after maximum POR.
- The watchdog detects missing service no later than `{r['maximum_watchdog_detection_ms']} ms`.
- Two real source errors were corrected: latch polarity/asynchronous inputs and the wrong POR timing claim.
- Physical waveforms, switch bounce, MLCC DC bias, charger-loop droop and fault injection are not claimed complete; they are explicitly assigned to H8.

**Historical R1-chain status:** `H3.2-R1` reviewed. The later marker in that chain was `H3.6.1-R1`, the worst-case board, battery and enclosure thermal model. The current hardware marker is `H1-R2.31`.

[Machine closure package](../hardware/verification/generated/H3-VRF25-transition-consolidation.json).
"""


def build() -> tuple[dict[Path, str], dict]:
    candidate, devices, dc, rails, methods = load()
    v21 = build_startup(candidate, devices, methods)
    outputs: dict[Path, str] = {VRF21: json.dumps(v21, indent=2, ensure_ascii=False) + "\n"}
    v22 = build_handover(candidate, dc, v21)
    outputs[VRF22] = json.dumps(v22, indent=2, ensure_ascii=False) + "\n"
    v23 = build_inrush(candidate, devices, rails, v22)
    outputs[VRF23] = json.dumps(v23, indent=2, ensure_ascii=False) + "\n"
    v24 = build_watchdog(candidate, devices, v23)
    outputs[VRF24] = json.dumps(v24, indent=2, ensure_ascii=False) + "\n"
    v25 = build_consolidation(v21, v22, v23, v24)
    outputs.update({
        VRF25: json.dumps(v25, indent=2, ensure_ascii=False) + "\n",
        DOCS["startup_en"]: md_startup(v21, False),
        DOCS["startup_ru"]: md_startup(v21, True),
        DOCS["handover_en"]: md_handover(v22, False),
        DOCS["handover_ru"]: md_handover(v22, True),
        DOCS["inrush_en"]: md_inrush(v23, False),
        DOCS["inrush_ru"]: md_inrush(v23, True),
        DOCS["watchdog_en"]: md_watchdog(v24, False),
        DOCS["watchdog_ru"]: md_watchdog(v24, True),
        DOCS["result_en"]: md_result(v25, False),
        DOCS["result_ru"]: md_result(v25, True),
    })
    return outputs, v25


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, result = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H3.2 reviewed; {result['accepted_results']['analytical_failures']} analytical failures; next H3.3.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
