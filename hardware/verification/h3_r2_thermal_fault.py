#!/usr/bin/env python3
"""Close the current-R2 thermal, single-fault and unattended envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "hardware/architecture/candidates/G2F-3I.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
METHODS = ROOT / "hardware/verification/generated/H3-R2-method-contract.json"
RAILS = ROOT / "hardware/verification/generated/H3-R2-rail-margins.json"
SOURCES = ROOT / "hardware/verification/generated/H3-R2-source-margins.json"
TRANSITIONS = ROOT / "hardware/verification/generated/H3-R2-transition-result.json"
WATCHDOG = ROOT / "hardware/verification/generated/H3-R2-inrush-watchdog.json"
BATTERY = ROOT / "hardware/verification/generated/H3-VRF34-battery-analog.json"
RF = ROOT / "hardware/verification/generated/H3-R2-rf-coexistence.json"
H2_FAULT = ROOT / "hardware/ecad/generated/H2-REV55-fault-kill.json"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-thermal-fault.json"
DOC_EN = ROOT / "docs/thermal-fault-electrical-verification.md"
DOC_RU = ROOT / "docs/thermal-fault-electrical-verification.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> float:
    return float(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def thermal_row(profile: dict, nominal_v: dict[str, Decimal]) -> dict:
    """Conservative enclosure heat: source input minus power delivered outside it."""
    currents = {name: d(value) for name, value in profile["loads_ma"].items()}
    if profile["support_profile"] == "SUPPORT_IDLE":
        currents["5V_EXT_ACTIVE_BRANCH"] = min(currents["5V_EXT_ACTIVE_BRANCH"], d(1000))
    outputs = {name: currents[name] * nominal_v[name] / d(1000) for name in currents}
    rail_output = sum(outputs.values(), d(0))
    system_input = rail_output / d("0.85") + d("0.250")
    source_input = system_input / d("0.85")
    delivered_external = outputs["5V_EXT_ACTIVE_BRANCH"]
    heat = source_input - delivered_external
    return {
        "id": f"{profile['signal_group']}/{profile['group_mode']}/{profile['support_profile']}",
        "signal_group": profile["signal_group"],
        "group_mode": profile["group_mode"],
        "support_profile": profile["support_profile"],
        "external_5v_current_a": q(currents["5V_EXT_ACTIVE_BRANCH"] / d(1000)),
        "rail_output_w": q(rail_output),
        "system_input_w": q(system_input),
        "source_input_upper_w": q(source_input),
        "external_delivered_w": q(delivered_external),
        "conservative_enclosure_heat_upper_w": q(heat),
        "rtheta_to_65c_at_35c_k_per_w_max": q(d(30) / heat),
        "rtheta_to_75c_at_35c_k_per_w_max": q(d(40) / heat),
    }


def fault(identifier: str, domain: str, mode: str, detection: str, primary: str,
          independent: str, result: str, recovery: str, deadline_ms: int | None = 100,
          classification: str = "contained") -> dict:
    return {
        "id": identifier,
        "domain": domain,
        "single_fault": mode,
        "detection": detection,
        "primary_path": primary,
        "independent_or_fail_safe_path": independent,
        "safe_result": result,
        "recovery": recovery,
        "maximum_analytical_detection_ms": deadline_ms,
        "classification": classification,
    }


def fault_rows() -> list[dict]:
    f = fault
    return [
        f("SF-R2-01", "physical command", "RUN is moved to KILL or the RUN conductor opens", "RUN_EDGE falls", "safe_run_fault_iso asserts FAULT_ASSERT_N", "the second switch throw also requests protected-pack shutdown", "every TX gate is safe and C5/RP are reset", "condition safe, then physical KILL-to-RUN"),
        f("SF-R2-02", "physical command", "RUN_LOOP_RAW is shorted permissive", "POWER_COMMAND_OFF_N falls in KILL", "the spare fault-buffer channel asserts FAULT_ASSERT_N", "pack admission receives the independent KILL throw", "one masking short cannot defeat KILL", "service switch/harness, then physical re-arm"),
        f("SF-R2-03", "fault plane", "FAULT_ASSERT_N pull-up opens", "the 1-Mohm backup pull-down wins", "SAFE_CLEAR_N clears RUN_PERMIT", "endpoint pull-downs and direct reset sinks remain", "latched shutdown", "service, then physical re-arm", 0),
        f("SF-R2-04", "fault plane", "FAULT_ASSERT_N is stuck low", "FAULT_ASSERT_SENSE stays low", "RUN_PERMIT cannot set", "direct reset and endpoint gates stay asserted", "safe no-start", "service required", 0),
        f("SF-R2-05", "fault plane", "FAULT_ASSERT_N is stuck permissive before RUN", "P11 remains high during the mandatory low proof", "the safety controller refuses re-arm and every lease", "100-kohm isolation prevents the expander from driving the plane", "safe no-admission", "KILL plus service", 0, "detected_no_admission"),
        f("SF-R2-06", "application", "S3 heartbeat stops", "the 1000-ms heartbeat deadline expires", "the safety controller requests fault", "its own hang is covered by TPS3435", "bounded hard shutdown with retained cause", "physical KILL-to-RUN", 1000),
        f("SF-R2-07", "safety controller", "safety firmware hangs or WDI sticks", "TPS3435 expires", "WDO_N clears the hardware latch", "all endpoint defaults are off-safe without firmware", "bounded hard shutdown", "physical KILL-to-RUN", 1760),
        f("SF-R2-08", "AON supply", "AON browns out or disappears", "TPS3808 POR_N asserts", "the latch clears asynchronously", "reset pull-ups, endpoint pull-downs and eFuse loss behavior are safe", "immediate safe state; final journal write may be absent", "next boot shows generic AON-loss fallback", 0),
        f("SF-R2-09", "primary latch", "RUN_PERMIT is stuck permissive", "readback mismatch or surviving TX evidence", "persistent SAFETY_FAULT_REQUEST asserts the second plane", "direct resets, backup rail gates, voice clamp and branch gates bypass RUN_PERMIT", "hazardous endpoints lose command or power", "KILL plus service"),
        f("SF-R2-10", "processor reset", "one primary C5/RP reset driver is stuck released", "reset/rail evidence disagrees", "RUN_PERMIT requests reset", "the separate FAULT_ASSERT_N sink reaches the same target", "processor remains reset", "KILL plus service"),
        f("SF-R2-11", "processor reset", "one direct fault-reset sink is stuck released", "reset/rail evidence disagrees", "the separate RUN_PERMIT inverter/NMOS path asserts reset", "endpoint rail and command gates also fall safe", "processor and transmitters remain contained", "KILL plus service"),
        f("SF-R2-12", "nRF24 power", "primary nRF rail gate is stuck high", "enable/evidence disagrees with RUN_PERMIT", "FAULT_ASSERT_N drives the backup gate low", "three CE gates and Ioff buffers remain off-safe", "all three nRF paths are contained", "KILL plus service"),
        f("SF-R2-13", "nRF24 power", "nRF backup gate is stuck high", "startup/fault proof finds the mismatch", "the independent RUN_PERMIT primary gate falls", "CE gates and endpoint pulls remain", "nRF group remains off", "KILL plus service"),
        f("SF-R2-14", "nRF24 power", "nRF load switch is shorted on", "rail or unexpected-RF evidence disagrees", "all three independent CE gates fall", "lease enforcement and Ioff isolation remain", "a switch short alone cannot command TX", "KILL, service and no further lease"),
        f("SF-R2-15", "CC1101 power", "primary CC rail gate is stuck high", "enable/evidence mismatch", "FAULT_ASSERT_N lowers the backup gate", "SPI/GDO isolation and endpoint pulls remain", "CC rail and command become safe", "KILL plus service"),
        f("SF-R2-16", "CC1101 power", "CC backup gate or load switch is stuck permissive", "startup proof or unexpected RF evidence", "RUN_PERMIT lowers the primary gate", "physical TX evidence catches any surviving carrier", "the fault cannot create an authorized command", "KILL plus service"),
        f("SF-R2-17", "voice power", "voice buck enable is stuck permissive", "voice PG or RF evidence survives shutdown", "FAULT_ASSERT_N clamps eFuse EN/UVLO", "PTT independently defaults high/RX", "voice rail and PTT become safe", "KILL plus service"),
        f("SF-R2-18", "voice power", "voice eFuse clamp is stuck released", "protected-rail proof mismatches", "RUN_PERMIT disables the upstream buck", "PTT-off remains independent", "voice loses rail or PTT", "KILL plus service"),
        f("SF-R2-19", "voice PTT", "module PTT is stuck active", "voice RF evidence asserts", "persistent fault removes the voice eFuse rail", "the primary buck gate also falls", "uncommanded TX energy is bounded", "KILL plus service"),
        f("SF-R2-20", "external power", "common external 5-V gate is stuck on", "branch readiness/current/evidence mismatches", "each branch gate receives direct FAULT_ASSERT_N", "each connector has true reverse-blocking protection", "both branches turn off independently", "KILL plus service"),
        f("SF-R2-21", "external branch", "one branch gate/eFuse is stuck permissive", "branch readiness/current/evidence mismatches", "the common RUN_PERMIT converter gate falls", "unknown accessories receive no lease", "base-supplied power is removed", "KILL plus service"),
        f("SF-R2-22", "IR transmitter", "IR carrier safety gate is stuck permissive", "optical evidence or carrier mismatch", "direct FAULT_ASSERT_N resets C5", "C5 reset removes the shared switched rail", "IR loses command and supply", "KILL plus service"),
        f("SF-R2-23", "IR transmitter", "IR load switch is shorted on", "rail/current or optical evidence mismatches", "RUN_PERMIT carrier gate falls", "MOSFET pull-down and C5 reset remain", "a rail short alone cannot create optical TX", "KILL plus service"),
        f("SF-R2-24", "TX supervision", "RF/IR TX occurs without a valid lease", "the source EV_N and ANY_TX_AON_N assert", "the controller holds SAFETY_FAULT_REQUEST", "the persistent request survives a primary-path mismatch", "all transmit gates close and source identity is recorded", "physical KILL-to-RUN"),
        f("SF-R2-25", "TX evidence", "one evidence output is stuck active", "one source bit stays low without admitted TX", "conservative fault request", "aggregate and front indicator need no application", "safe nuisance shutdown", "service, then physical re-arm"),
        f("SF-R2-26", "TX evidence", "one evidence output is stuck inactive/unreadable", "mandatory pre-TX proof or private bus fails", "the affected mode receives no lease", "endpoint gates remain off-safe", "safe no-admission", "service before use", 100, "detected_no_admission"),
        f("SF-R2-27", "thermal sensing", "one NTC is open or shorted", "ADC code leaves the valid window", "safety controller requests hard fault", "watchdog covers a controller hang", "hazardous power and TX stop", "service, then physical re-arm"),
        f("SF-R2-28", "thermal sensing", "one NTC is plausibly stuck in range", "startup trend/cross-zone plausibility fails", "high-power and unattended admission for that zone is blocked", "converter/eFuse/chip protections remain", "the sensor fault cannot itself create heat", "service before high-power use", None, "detected_no_admission"),
        f("SF-R2-29", "power protection", "one eFuse/load path fails open", "PG/current/rail mismatch", "the affected domain loses power", "other rails remain independently protected", "safe loss of function", "service required", 0),
        f("SF-R2-30", "fault record", "power disappears during journal commit", "new slot lacks a valid CRC/commit marker", "hardware loss behavior is already safe", "previous valid slot or generic loss fallback is selected", "no fabricated cause is displayed", "read-only service export, then physical recovery", 0),
    ]


def render_doc(result: dict, russian: bool) -> str:
    s = result["summary"]
    sustained = result["thermal"]["worst_sustained_profile"]
    absolute = result["thermal"]["electrical_absolute_profile"]
    if russian:
        title = "# Thermal, единичные отказы и длительная работа · H3-R2.6"
        nav = "[English](thermal-fault-electrical-verification.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)"
        intro = f"`H3-R2.6` проведён ревью: **{s['checks']} checks**, `{s['thermal_profiles']}` thermal-профилей и `{s['single_fault_cases']}` single-fault сценариев проходят без открытых аналитических findings. Текущий маркер — `H3-R2.7`."
        thermal = ("## Тепло\n\n"
                   f"Для длительной thermal-квалификации допускается только support-нагрузка `SUPPORT_IDLE`; внешний 5-В порт ограничен 1,00 А. Худший непрерывный расчётный профиль — `{sustained['id']}`: консервативно `{sustained['conservative_enclosure_heat_upper_w']:.3f} Вт` внутри корпуса. При 35 °C H6 должен обеспечить не хуже `{sustained['rtheta_to_65c_at_35c_k_per_w_max']:.3f} K/W` до предупреждения 65 °C. Сам этот TX-профиль остаётся ограниченной сессией до H8, а не разрешением на unattended TX. "
                   f"Абсолютный electrical corner `{absolute['id']}` даёт `{absolute['conservative_enclosure_heat_upper_w']:.3f} Вт`, но не разрешён как длительный режим. Три NTC, пороги warning/kill/rearm и charger `TREG=60 °C`, `TSHUT=85 °C` остаются независимыми защитами. Это параметрическая верхняя граница, не обещание температуры готового корпуса.")
        faults = ("## Единичные отказы\n\n"
                  "Все 30 сценариев имеют обнаружение, основной и независимый/fail-safe путь, безопасный исход и физическое восстановление. Максимальный бумажный detection deadline — 1760 мс у независимого watchdog. Автоматического или программного re-arm нет; fault-plane проверяется при каждом физическом `KILL → RUN`.")
        unattended = ("## Длительная работа\n\n"
                      "Долгая работа питается от квалифицированного USB-PD. `24/48 часов` — длительность неразрушающего H8 soak и интервал полной проверки, а не обещание автономности. Настройка доступна только локально; по умолчанию 48 часов. Просрочка сначала снимает TX leases, затем останавливает сессию и требует физический re-arm. Watchdog и температурные пределы этой настройкой не меняются.")
        boundary = "## Что осталось физическим\n\n" + "\n".join(f"- {row}" for row in result["physical_residuals"])
        end = "Placement/routing, закупку, печать и итоговые thermal/safety заявления этот результат не разрешает.\n\n[Машинное evidence](../hardware/verification/generated/H3-R2-thermal-fault.json)."
    else:
        title = "# Thermal, single-fault and extended-operation result · H3-R2.6"
        nav = "[Русский](thermal-fault-electrical-verification.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)"
        intro = f"`H3-R2.6` is reviewed: **{s['checks']} checks**, `{s['thermal_profiles']}` thermal profiles and `{s['single_fault_cases']}` single-fault cases pass with no open analytical finding. The current marker is `H3-R2.7`."
        thermal = ("## Thermal envelope\n\n"
                   f"Only the `SUPPORT_IDLE` support load is eligible for sustained thermal qualification and external 5 V is capped at 1.00 A. The worst continuous calculation profile is `{sustained['id']}`: a conservative `{sustained['conservative_enclosure_heat_upper_w']:.3f} W` inside the enclosure. At 35 °C H6 must achieve no worse than `{sustained['rtheta_to_65c_at_35c_k_per_w_max']:.3f} K/W` before the 65 °C warning. That TX case remains a bounded session pending H8, not permission for unattended TX. "
                   f"The absolute electrical corner `{absolute['id']}` reaches `{absolute['conservative_enclosure_heat_upper_w']:.3f} W` but is not a sustained permission. Three NTCs, warning/kill/rearm thresholds and charger `TREG=60 °C`, `TSHUT=85 °C` remain independent protections. This is a parameterized upper bound, not a finished-enclosure temperature claim.")
        faults = ("## Single faults\n\n"
                  "All 30 cases have detection, primary and independent/fail-safe containment, a safe result and physical recovery. The maximum paper detection deadline is 1760 ms for the independent watchdog. Automatic or software re-arm is forbidden; the fault plane is proved at every physical `KILL to RUN`.")
        unattended = ("## Extended operation\n\n"
                      "Long operation uses a qualified USB-PD source. `24/48 hours` are non-destructive H8 soak durations and full-proof intervals, not an autonomy promise. The setting is local-only and defaults to 48 hours. Expiry first revokes TX leases, then stops the session and requires physical re-arm. It cannot change watchdog or temperature limits.")
        boundary = "## Physical-only residuals\n\n" + "\n".join(f"- {row}" for row in result["physical_residuals"])
        end = "This result does not authorize placement/routing, purchasing, fabrication or final thermal/safety claims.\n\n[Machine evidence](../hardware/verification/generated/H3-R2-thermal-fault.json)."
    return "\n\n".join((title, nav, intro, thermal, faults, unattended, boundary, end)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    candidate = load(CANDIDATE)
    devices = load(DEVICES)["devices"]
    methods = load(METHODS)
    rails = load(RAILS)
    sources = load(SOURCES)
    transitions = load(TRANSITIONS)
    watchdog = load(WATCHDOG)
    battery = load(BATTERY)
    rf = load(RF)
    h2_fault = load(H2_FAULT)
    safety = candidate["safety_contract"]

    nominal_v = {name: d(row["nominal_v"]) for name, row in rails["voltage_corners"].items()}
    profiles = [thermal_row(row, nominal_v) for row in rails["profiles"]]
    sustained_profiles = [row for row in profiles if row["support_profile"] == "SUPPORT_IDLE"]
    worst_sustained = max(sustained_profiles, key=lambda row: row["conservative_enclosure_heat_upper_w"])
    absolute = max(profiles, key=lambda row: row["conservative_enclosure_heat_upper_w"])
    quiet = next(row for row in profiles if row["id"] == "NONE/QUIET/SUPPORT_IDLE")
    faults = fault_rows()
    thresholds = battery["board_zone_thermistors"]["thresholds"]
    charger = devices["ti_bq25798_rqmr"]["configuration_contract"]
    method_ids = {row["id"] for row in methods["methods"]}
    fault_classes = {row["classification"] for row in faults}

    proof_values = [
        {"id": "EVERY_24_H", "active_session_seconds": 86400},
        {"id": "EVERY_48_H", "active_session_seconds": 172800},
        {"id": "STARTUP_ONLY", "active_session_seconds": None},
    ]
    unattended = {
        "sustained_admission": "SUPPORT_IDLE plus one top-level signal group; external 5 V <=1.00 A; SUPPORT_WORST, continuous unleased TX, unreadable safety sensing and unknown accessories are excluded",
        "long_operation_source": "qualified USB-PD; USB never relaxes watchdog, thermal, lease or physical-rearm policy",
        "runtime_claim": "none; no battery autonomy or USB uptime is promised",
        "full_fault_plane_proof": {
            "ui_path": "Settings > Safety > Full self-test",
            "default": "EVERY_48_H",
            "values": proof_values,
            "change_authority": "local physical UI only; staged until the next physical KILL-to-RUN",
            "expiry_sequence": ["revoke every TX lease", "stop and flush the active session", "record FAULT_PLANE_PROOF_DUE", "hold SAFETY_FAULT_REQUEST until physical KILL-to-RUN"],
            "invariants": "the setting cannot change TPS3435, heartbeat, thermal, power-fault or evidence deadlines",
        },
        "test_interpretation": "24/48-hour powered runs are ordinary non-destructive H8 soak tests and proof intervals, not product runtime specifications",
    }
    physical = [
        "H6: solve the routed copper, vias, component spreading and enclosure thermal network; meet every admitted profile's 35-C resistance ceiling",
        "H6: keep RUN_PERMIT and FAULT_ASSERT_N routes, pads, returns and endpoint buffers physically independent",
        "H8: map POWER, RF/VOICE, UI/display, both cells, charger and external surfaces at each admitted sustained profile",
        "H8: inject SF-R2-01 through SF-R2-30 with current-limited fixtures/emulators and verify safe output, retained cause and physical-only re-arm",
        "H8: calibrate all thermal/evidence thresholds and measure watchdog, eFuse, reset, QOD and residual-energy timing",
        "H8: run ordinary non-destructive 24/48-hour qualified-USB soak plus battery-to-protected-cutoff measurement without converting it into an uptime promise",
        "H8: interrupt each journal boundary and verify last-valid-slot or explicit AON-loss fallback",
    ]
    checks = {
        "required_r2_methods_exist": {"M-INT", "M-TRANS", "M-STATE", "M-THERMAL"} <= method_ids,
        "upstream_rail_source_transition_rf_reviews_pass": rails["summary"]["steady_thermal_failures"] == 0 and sources["summary"]["failed_states"] == 0 and transitions["status"].startswith("reviewed_") and rf["status"] == "pass",
        "all_56_r2_profiles_are_thermalized": len(profiles) == rails["summary"]["operating_profiles"] == 56,
        "all_28_sustained_profiles_are_thermalized": len(sustained_profiles) == 28,
        "external_sustained_current_is_capped_at_1a": max(row["external_5v_current_a"] for row in sustained_profiles) <= 1.0,
        "support_worst_remains_non_sustained": absolute["support_profile"] == "SUPPORT_WORST" and rails["policy"]["electrical_worst_is_not_a_sustained_profile"],
        "all_thermal_resistance_ceilings_are_positive": all(row["rtheta_to_65c_at_35c_k_per_w_max"] > 0 and row["rtheta_to_75c_at_35c_k_per_w_max"] > row["rtheta_to_65c_at_35c_k_per_w_max"] for row in profiles),
        "rail_junction_margin_exceeds_20c": d(rails["summary"]["minimum_junction_margin_c"]) >= d(20),
        "maximum_sustained_cell_heat_is_bounded": d(sources["summary"]["maximum_sustained_cell_pair_i2r_w"]) <= d("0.200"),
        "three_independent_board_zones_exist": set(battery["board_zone_thermistors"]["channels"]) == {"POWER", "RF_VOICE", "UI"},
        "thermal_threshold_order_is_fail_safe": thresholds["sensor_short_code_at_or_below"] < thresholds["fault_kill_code_at_or_below"] < thresholds["warning_code_at_or_below"] < thresholds["fault_rearm_code_at_or_above"] < thresholds["sensor_open_code_at_or_above"],
        "charger_thermal_registers_are_protected": charger["thermal_regulation_c"] == 60 and charger["thermal_shutdown_c"] == 85,
        "h2_fault_plane_is_reviewed": h2_fault["status"] == "reviewed_watchdog_thermal_fault_and_hardware_shutdown",
        "exactly_30_single_fault_cases": len(faults) == 30 and {row["id"] for row in faults} == {f"SF-R2-{index:02d}" for index in range(1, 31)},
        "faults_have_detection_two_paths_result_and_recovery": all(row["detection"] and row["primary_path"] and row["independent_or_fail_safe_path"] and row["safe_result"] and row["recovery"] for row in faults),
        "all_faults_are_contained_or_refused": fault_classes == {"contained", "detected_no_admission"},
        "watchdog_deadline_is_1760ms": watchdog["watchdog"]["timeout_ms"]["max"] == 1760 and max(row["maximum_analytical_detection_ms"] or 0 for row in faults) == 1760,
        "physical_rearm_is_the_only_rearm": "only re-arm action is a physical KILL-to-RUN edge" in safety["latch_logic"]["rearm"],
        "fault_plane_proof_is_mandatory": "must also read low" in safety["watchdog"]["fault_plane_proof"],
        "nine_physical_tx_evidence_channels": len(safety["evidence"]["channels"]) == 9,
        "fault_journal_has_two_crc_slots": watchdog["fault_record"]["slots"] == 2 and "verify body" in watchdog["fault_record"]["commit_order"],
        "self_test_policy_has_24_48_and_startup": {row["id"] for row in proof_values} == {"EVERY_24_H", "EVERY_48_H", "STARTUP_ONLY"},
        "self_test_defaults_to_48h": unattended["full_fault_plane_proof"]["default"] == "EVERY_48_H",
        "unattended_makes_no_runtime_claim": unattended["runtime_claim"].startswith("none"),
        "all_physical_residuals_are_owned": all(row.startswith(("H6:", "H8:")) for row in physical),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("H3-R2.6 checks failed: " + ", ".join(failures))

    result = {
        "schema_version": 1,
        "artifact": "H3-R2-thermal-fault",
        "marker": "H3-R2.6",
        "status": "pass",
        "reviewed_on": "2026-09-01",
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in (CANDIDATE, DEVICES, METHODS, RAILS, SOURCES, TRANSITIONS, WATCHDOG, BATTERY, RF, H2_FAULT)},
        "methods": ["M-INT", "M-TRANS", "M-STATE", "M-THERMAL"],
        "summary": {
            "checks": len(checks),
            "thermal_profiles": len(profiles),
            "sustained_profiles": len(sustained_profiles),
            "single_fault_cases": len(faults),
            "maximum_watchdog_detection_ms": 1760,
            "physical_residuals": len(physical),
            "analytical_findings_open": 0,
        },
        "thermal": {
            "model": "85%-efficient rail conversion plus 0.25-W named overhead, followed by a second conservative 85% source envelope; externally delivered 5-V power is subtracted, while its conversion loss remains inside",
            "ambient_design_target_c": {"minimum": 0, "maximum": 35, "status": "engineering target pending H6/H8; not a published guarantee"},
            "warning_c": 65,
            "fault_kill_c": 75,
            "rearm_below_c": 60,
            "cell_pair_sustained_i2r_w_max": float(sources["summary"]["maximum_sustained_cell_pair_i2r_w"]),
            "electrical_absolute_profile": absolute,
            "worst_sustained_profile": worst_sustained,
            "quiet_profile": quiet,
            "profiles": profiles,
            "board_zone_thermistors": battery["board_zone_thermistors"],
            "steady_component_thermal": rails["steady_thermal_by_rail"],
        },
        "single_fault": {
            "claim": "one fault at a time; every case reaches bounded-energy containment or deterministic no-admission without the failed compute/path",
            "non_claims": ["two independent simultaneous faults", "common physical damage bypassing both shutdown planes", "final diagnostic commit after complete AON loss", "measured RF silence, timing or enclosure temperature before H6/H8"],
            "faults": faults,
        },
        "unattended": unattended,
        "checks": checks,
        "errors": [],
        "physical_residuals": physical,
        "authorization": {"paper_electrical_contract_reviewed": True, "pcb_placement_or_routing": False, "purchasing": False, "fabrication": False, "final_product_claim": False},
        "next": {"marker": "H3-R2.7", "action": "cross-check every R2 result and publish the bilingual H3 phase report"},
    }
    return {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(result, False),
        DOC_RU: render_doc(result, True),
    }, result


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
        print(f"wrote H3-R2.6: {result['summary']['checks']} checks, {result['summary']['single_fault_cases']} faults")
        return 0
    stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.6 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.6; {result['summary']['checks']} checks, {result['summary']['single_fault_cases']} faults")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
