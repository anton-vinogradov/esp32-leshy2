#!/usr/bin/env python3
"""Verify and publish H3-R2.2.1 startup, reset and recovery sequences."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-transition-sequence-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
FREEZE = REPO / "hardware/verification/generated/H3-R2-input-freeze.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
DC = REPO / "hardware/verification/generated/H3-R2-dc-source-crosscheck.json"
NETS = REPO / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
M1 = REPO / "hardware/ecad/generated/H2-R2-interboard-m1.json"
DEVICES = REPO / "hardware/architecture/devices.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-transition-sequences.json"
DOC_EN = REPO / "docs/power-transition-sequences.md"
DOC_RU = REPO / "docs/power-transition-sequences.ru.md"
SOURCES = (CONTRACT, PLAN, FREEZE, METHODS, DC, NETS, INSTANCES, M1, DEVICES)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def round3(value: float) -> float:
    return round(value + 0.0, 3)


def rc_rise_ms(r_ohm: float, c_f: float, source_v: float, leakage_a: float, threshold_v: float) -> float:
    final_v = source_v + leakage_a * r_ohm
    if final_v <= threshold_v:
        return math.inf
    return -r_ohm * c_f * math.log(1.0 - threshold_v / final_v) * 1000.0


def rc_fall_ms(r_ohm: float, c_f: float, initial_v: float, leakage_a: float, threshold_v: float) -> float:
    final_v = leakage_a * r_ohm
    if final_v >= threshold_v:
        return math.inf
    return -r_ohm * c_f * math.log((threshold_v - final_v) / (initial_v - final_v)) * 1000.0


class TransitionModel:
    """Small deterministic model of the hardware latch plus Safety boot policy."""

    def __init__(self) -> None:
        self.aon = False
        self.por = False
        self.switch_run = False
        self.self_test = False
        self.fault_request_released = False
        self.external_fault_healthy = True
        self.watchdog_healthy = True
        self.qualified_kill = False
        self.edge_pending = False
        self.permit = False
        self.s3_reset_asserted = False
        self.s3_available = False
        self.firmware_state = "POWERED_OFF"
        self.trace: list[dict] = []
        self.invariant_errors: list[str] = []

    def fault_plane_high(self) -> bool:
        return (
            self.aon
            and self.por
            and self.switch_run
            and self.fault_request_released
            and self.external_fault_healthy
            and self.watchdog_healthy
        )

    def normalize(self) -> None:
        if not self.fault_plane_high():
            self.permit = False

    def snapshot(self, event: str) -> None:
        self.normalize()
        fault_high = self.fault_plane_high()
        hazardous = self.permit and fault_high
        c5_reset = not self.permit or not fault_high
        rf_reset = not self.permit or not fault_high
        if self.permit and not all((self.aon, self.por, self.switch_run, self.fault_request_released, self.external_fault_healthy, self.watchdog_healthy)):
            self.invariant_errors.append(f"{event}: RUN_PERMIT without every prerequisite")
        if hazardous != self.permit:
            self.invariant_errors.append(f"{event}: hazardous enable differs from RUN_PERMIT")
        if not self.permit and not (c5_reset and rf_reset):
            self.invariant_errors.append(f"{event}: stopped state fails to reset C5/RF RP")
        self.trace.append({
            "event": event,
            "firmware_state": self.firmware_state,
            "switch": "RUN" if self.switch_run else "KILL",
            "por_valid": self.por,
            "fault_request_released": self.fault_request_released,
            "fault_plane_high": fault_high,
            "run_permit": self.permit,
            "hazardous_enabled": hazardous,
            "c5_reset_asserted": c5_reset,
            "rf_rp_reset_asserted": rf_reset,
            "s3_reset_asserted": self.s3_reset_asserted,
            "s3_available": self.s3_available and not self.s3_reset_asserted,
        })

    def power_on(self, run: bool) -> None:
        self.__init__()
        self.aon = True
        self.switch_run = run
        self.s3_available = True
        self.firmware_state = "BOOT_HOLD_FAULT"

    def apply(self, event: str) -> None:
        if event == "power_on_kill":
            self.power_on(False)
        elif event == "power_on_run":
            self.power_on(True)
        elif event == "por_valid":
            self.por = True
        elif event == "self_test_pass":
            self.self_test = True
            self.firmware_state = "WAIT_KILL" if self.switch_run else "KILL_QUALIFY"
        elif event == "self_test_fail":
            self.self_test = False
            self.fault_request_released = False
            self.firmware_state = "FAULT_LATCHED"
        elif event == "hold_kill_500":
            if self.self_test and not self.switch_run and self.firmware_state != "FAULT_LATCHED":
                self.qualified_kill = True
                self.fault_request_released = True
                self.firmware_state = "ARMED_WAIT_RUN"
        elif event == "hold_kill_short":
            self.qualified_kill = False
            self.fault_request_released = False
            self.firmware_state = "WAIT_KILL"
        elif event == "switch_run":
            was_kill = not self.switch_run
            self.switch_run = True
            self.edge_pending = bool(was_kill and self.qualified_kill and self.fault_request_released)
            self.qualified_kill = False
            if self.firmware_state != "FAULT_LATCHED":
                self.firmware_state = "ARMED_WAIT_RUN" if self.edge_pending else "WAIT_KILL"
        elif event == "switch_kill":
            self.switch_run = False
            self.edge_pending = False
            self.qualified_kill = False
            self.fault_request_released = False
            self.permit = False
            self.firmware_state = "WAIT_KILL"
        elif event == "rc_clock":
            if self.edge_pending and self.fault_plane_high():
                self.permit = True
                self.edge_pending = False
                self.firmware_state = "RUNNING"
        elif event == "watchdog_fault":
            self.watchdog_healthy = False
            self.fault_request_released = False
            self.firmware_state = "FAULT_LATCHED"
        elif event == "hard_fault":
            self.external_fault_healthy = False
            self.fault_request_released = False
            self.firmware_state = "FAULT_LATCHED"
        elif event == "fault_recovers":
            self.external_fault_healthy = True
            self.watchdog_healthy = True
        elif event == "safety_controller_reset":
            self.self_test = False
            self.fault_request_released = False
            self.qualified_kill = False
            self.edge_pending = False
            self.s3_reset_asserted = False
            self.firmware_state = "BOOT_HOLD_FAULT"
        elif event == "pulse_s3_reset":
            self.s3_reset_asserted = True
        elif event == "release_s3_reset":
            self.s3_reset_asserted = False
        elif event == "aon_undervoltage":
            self.por = False
            self.fault_request_released = False
            self.qualified_kill = False
            self.edge_pending = False
            self.firmware_state = "BOOT_HOLD_FAULT"
        elif event == "aon_recovers":
            self.por = True
        elif event == "usb_attach":
            pass
        elif event == "normal_start":
            for nested in ("power_on_kill", "por_valid", "self_test_pass", "hold_kill_500", "switch_run", "rc_clock"):
                self.apply(nested)
            return
        else:
            raise ValueError(f"unknown transition event: {event}")
        self.snapshot(event)

    def final(self) -> dict:
        self.normalize()
        fault_high = self.fault_plane_high()
        return {
            "permit": self.permit,
            "firmware_state": self.firmware_state,
            "hazardous_enabled": self.permit and fault_high,
            "s3_available": self.s3_available and not self.s3_reset_asserted,
            "s3_reset_asserted": self.s3_reset_asserted,
        }


def build() -> tuple[dict[Path, str], dict]:
    contract = load(CONTRACT)
    plan = load(PLAN)
    freeze = load(FREEZE)
    methods = load(METHODS)
    dc = load(DC)
    nets = load(NETS)
    instances = load(INSTANCES)
    m1 = load(M1)
    devices = load(DEVICES)["devices"]
    errors: list[str] = []

    if freeze.get("status") != "pass" or methods.get("status") != "pass":
        errors.append("reviewed R2 input/method chain is not passing")
    if not str(dc.get("status", "")).startswith("reviewed_h3_r2_1"):
        errors.append("H3-R2.1 cross-check is not reviewed")
    current = next(row for row in plan["substeps"] if row["id"] == "H3-R2.2")
    detail = next(row for row in current["details"] if row["id"] == "H3-R2.2.1")
    if detail["status"] not in {"current", "reviewed"}:
        errors.append("H3-R2.2.1 is not the current/reviewed plan step")

    endpoint_index = {row["endpoint"]: row for row in nets["rows"]}
    topology_checks: dict[str, bool] = {}
    for endpoint, expected_net in contract["required_endpoints"].items():
        row = endpoint_index.get(endpoint)
        passed = row is not None and row.get("net") == expected_net
        if expected_net is None:
            passed = passed and row.get("disposition") == "no_connect"
        else:
            passed = passed and row.get("disposition") == "connected"
        topology_checks[endpoint] = passed
        if not passed:
            errors.append(f"topology mismatch: {endpoint} != {expected_net}")

    members_by_net: dict[str, set[str]] = {}
    for row in nets["rows"]:
        if row.get("net"):
            members_by_net.setdefault(row["net"], set()).add(row["endpoint"])
    net_checks: dict[str, bool] = {}
    for net, required in contract["required_net_members"].items():
        net_checks[net] = set(required) <= members_by_net.get(net, set())
        if not net_checks[net]:
            errors.append(f"required members missing from {net}")
    s3_gate_exact = members_by_net.get("S3_RESET_KILL_GATE", set()) == set(contract["required_net_members"]["S3_RESET_KILL_GATE"])
    net_checks["S3_RESET_KILL_GATE_exact"] = s3_gate_exact
    if not s3_gate_exact:
        errors.append("S3 reset gate has an unreviewed extra or missing endpoint")

    if m1["summary"]["physical_contacts"] != 80 or m1["summary"]["no_connect_reserve_contacts"] != 9:
        errors.append("M1 contact/reserve count differs from the current R2 map")
    p35 = next(row for row in m1["contacts"] if row["contact"] == 35)
    if p35["net"] != "FAULT_KILL" or p35["class"] != "safety":
        errors.append("M1 contact 35 is not the latched front-indicator crossing")
    p36 = next(row for row in m1["contacts"] if row["contact"] == 36)
    if p36["net"] != "S3_RESET_KILL_GATE" or p36["class"] != "safety":
        errors.append("M1 contact 36 is not the bounded S3 reset crossing")

    by_instance = {row["instance"]: row for row in instances["rows"]}
    exact_devices = {
        "supervisor": by_instance["safe_supervisor"]["device_id"],
        "watchdog": by_instance["safety_watchdog"]["device_id"],
        "schmitt": by_instance["safe_rearm_buffer"]["device_id"],
        "latch": by_instance["safe_latch"]["device_id"],
        "rearm_resistor": by_instance["safe_rearm_delay_res"]["device_id"],
        "rearm_capacitor": by_instance["safe_rearm_delay_cap"]["device_id"],
    }
    expected_devices = {
        "supervisor": "ti_tps3808g33_dbvr",
        "watchdog": "ti_tps3435cakagddfr",
        "schmitt": "ti_sn74lvc1g17_dckr",
        "latch": "ti_sn74lvc1g74_dcur",
        "rearm_resistor": "yageo_rc0402fr_07100kl",
        "rearm_capacitor": "murata_grm21br71e225ke11l",
    }
    if exact_devices != expected_devices:
        errors.append("transition chain exact device identities changed")

    supervisor = devices[exact_devices["supervisor"]]["electrical_contract"]
    watchdog = devices[exact_devices["watchdog"]]["electrical_contract"]
    schmitt = devices[exact_devices["schmitt"]]["electrical_contract"]
    latch = devices[exact_devices["latch"]]["electrical_contract"]
    if supervisor["ct_configuration"] != "open" or supervisor["reset_delay_ms"] != {"min": 12, "typ": 20, "max": 28}:
        errors.append("TPS3808 CT-open delay contract changed")
    if watchdog["watchdog_timeout_s"] != {"min": 1.44, "typ": 1.6, "max": 1.76}:
        errors.append("TPS3435 K timeout contract changed")
    if watchdog["watchdog_assert_time_ms"] != {"min": 180, "typ": 200, "max": 220}:
        errors.append("TPS3435 G assert-time contract changed")
    if watchdog["device_startup_time_us_max"] != 500:
        errors.append("TPS3435 device-startup bound changed")
    if watchdog["watchdog_startup_delay_ms"] != {"min": 0, "typ": 0, "max": 0}:
        errors.append("TPS3435 watchdog-window startup delay changed")
    if "CLR_N low forces Q low" not in latch["clear_behavior"]:
        errors.append("latch asynchronous-clear behavior is not bound")

    threshold = schmitt["threshold_v_at_3v"]
    leakage = schmitt["input_leakage_max_ua"] * 1e-6
    rise_earliest = rc_rise_ms(99_000, 1.98e-6, 3.3, leakage, threshold["positive_min"])
    rise_latest = rc_rise_ms(101_000, 2.42e-6, 3.3, -leakage, threshold["positive_max"])
    fall_guaranteed = rc_fall_ms(101_000, 2.42e-6, 3.3, leakage, threshold["negative_min"])
    kill_margin = contract["policy"]["qualified_kill_ms"] - fall_guaranteed
    if kill_margin <= 0:
        errors.append("qualified KILL dwell is shorter than the tolerance/leakage RC discharge bound")

    scenario_rows = []
    for scenario in contract["scenarios"]:
        model = TransitionModel()
        for event in scenario["events"]:
            model.apply(event)
        final = model.final()
        expected = scenario["expected_final"]
        mismatches = {key: {"expected": value, "actual": final.get(key)} for key, value in expected.items() if final.get(key) != value}
        scenario_errors = model.invariant_errors + [f"final {key}: {value}" for key, value in mismatches.items()]
        if scenario_errors:
            errors.append(f"{scenario['id']} failed")
        scenario_rows.append({
            "id": scenario["id"],
            "title": scenario["title"],
            "events": scenario["events"],
            "expected_final": expected,
            "actual_final": final,
            "trace": model.trace,
            "status": "pass" if not scenario_errors else "fail",
            "errors": scenario_errors,
        })

    manifest = {
        "schema_version": 1,
        "artifact": "H3-R2-transition-sequences",
        "marker": "H3-R2.2.1",
        "status": "reviewed_startup_shutdown_reset_and_recovery" if not errors else "fail",
        "source_sha256": {str(path.relative_to(REPO)): digest(path) for path in SOURCES},
        "exact_devices": {key: {"device_id": value, "mpn": devices[value]["mpn"], "source": devices[value]["source"]} for key, value in exact_devices.items()},
        "topology_checks": topology_checks,
        "net_checks": net_checks,
        "timing": {
            "supervisor_ct_open_reset_delay_ms": supervisor["reset_delay_ms"],
            "supervisor_assertion_max_us": supervisor["sense_to_reset_assertion_max_us"],
            "watchdog_timeout_s": watchdog["watchdog_timeout_s"],
            "watchdog_assert_time_ms": watchdog["watchdog_assert_time_ms"],
            "watchdog_device_startup_time_us_max": watchdog["device_startup_time_us_max"],
            "watchdog_startup_delay_ms": watchdog["watchdog_startup_delay_ms"],
            "watchdog_service_period_ms": contract["policy"]["watchdog_service_period_ms"],
            "rearm_rc": {
                "resistor_ohm": {"min": 99000, "nom": 100000, "max": 101000},
                "capacitor_uf_tolerance_only": {"min": 1.98, "nom": 2.2, "max": 2.42},
                "rise_ms": {"earliest": round3(rise_earliest), "latest": round3(rise_latest)},
                "guaranteed_fall_below_vt_minus_min_ms": round3(fall_guaranteed),
                "qualified_kill_ms": contract["policy"]["qualified_kill_ms"],
                "analytical_kill_margin_ms": round3(kill_margin),
                "credit": "debounce and one-edge formation only; never the sole anti-auto-start barrier"
            }
        },
        "firmware_contract": {
            "states": ["BOOT_HOLD_FAULT", "WAIT_KILL", "KILL_QUALIFY", "ARMED_WAIT_RUN", "RUNNING", "FAULT_LATCHED"],
            "reset_outputs": "PA25 and PA23 default low through external 10-kohm pulldowns: hazardous permit is held off while S3 reset remains released",
            "boot_rule": "never release PA25 after self-test while RUN_EDGE is high; require 500 ms continuously low first",
            "fault_rule": "assert PA25 low immediately, store the cause, and require a new qualified KILL-to-RUN cycle",
            "s3_recovery": "PA23 may pulse high to reset only S3; release it low after reset so the fault-only UI can reboot"
        },
        "scenarios": scenario_rows,
        "summary": {
            "scenarios": len(scenario_rows),
            "passed_scenarios": sum(row["status"] == "pass" for row in scenario_rows),
            "topology_endpoints": len(topology_checks),
            "topology_failures": sum(not value for value in topology_checks.values()),
            "net_checks": len(net_checks),
            "errors": len(errors)
        },
        "corrections": [
            {
                "finding": "The prior current-R2 map tied the S3 reset sink to the generic C5 kill gate, so a hard fault could remove the display that must explain the cause.",
                "correction": "M1 contact 36 now carries a separate S3_RESET_KILL_GATE from Safety PA23; C5 and RF RP retain direct fault reset.",
                "cost_effect": "no added fitted body or cost; one former M1 reserve is used"
            },
            {
                "finding": "Safety PA23 had no external reset-state bias and could float during controller reset.",
                "correction": "The unused evidence-mask P17 pulldown is reassigned as a 10-kohm PA23 pulldown; P17 is tied directly to ground.",
                "cost_effect": "BOM-neutral instance reuse"
            },
            {
                "finding": "Earlier wording credited RC delay alone with blocking auto-start, which is not a sufficient invariant for arbitrary firmware release timing.",
                "correction": "The verified rule holds PA25 low until a continuous physical KILL qualification; RC provides a clean subsequent edge only.",
                "cost_effect": "firmware policy only"
            }
        ],
        "physical_residuals": contract["physical_residuals"],
        "authorization": contract["authorization"],
        "next": {"marker": "H3-R2.2.3", "action": "H3-R2.2.2 handover is reviewed; verify inrush, load steps, watchdog kill and retained fault display"},
        "errors": errors,
    }
    outputs = {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }
    return outputs, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    t = manifest["timing"]
    s = manifest["summary"]
    rows = manifest["scenarios"]
    if russian:
        title = "# Запуск, сброс и восстановление · H3-R2.2.1"
        nav = "[English](power-transition-sequences.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)"
        intro = ("Проверка `H3-R2.2.1` завершена: все сценарии запуска и аварийного возврата проходят без автоматического повторного старта. "
                 "Обычный fault аппаратно выключает опасные домены и напрямую сбрасывает C5/RF RP, но оставляет S3 для понятного сообщения, пока доступно питание UI.")
        states_h = "## Правило запуска"
        states = ("Safety держит `SAFETY_FAULT_REQUEST` активным после сброса. Сначала self-test, затем физический `KILL` непрерывно 500 мс, "
                  "и только следующий фронт `KILL→RUN` может тактировать аппаратную защёлку `RUN_PERMIT`. USB, software reset и исчезновение причины fault фронт не создают.")
        timing_h = "## Точные границы"
        timing = (f"- TPS3808 с открытым CT: `{t['supervisor_ct_open_reset_delay_ms']['min']}..{t['supervisor_ct_open_reset_delay_ms']['max']} мс`; аварийное утверждение reset — не более `{t['supervisor_assertion_max_us']} мкс`.\n"
                  f"- TPS3435: запуск ИС — не более `{t['watchdog_device_startup_time_us_max']} мкс`, задержка запуска watchdog-окна — `{t['watchdog_startup_delay_ms']['max']} мс`; timeout `{t['watchdog_timeout_s']['min']}..{t['watchdog_timeout_s']['max']} с`, WDO low `{t['watchdog_assert_time_ms']['min']}..{t['watchdog_assert_time_ms']['max']} мс`; heartbeat — `{t['watchdog_service_period_ms']} мс`.\n"
                  f"- 100 кОм / 2,2 мкФ: расчётный rise `{t['rearm_rc']['rise_ms']['earliest']}..{t['rearm_rc']['rise_ms']['latest']} мс`, гарантированный tolerance-only discharge `{t['rearm_rc']['guaranteed_fall_below_vt_minus_min_ms']} мс`; это debounce, не единственный interlock.")
        seq_h = "## Проверенные сценарии"
        header = "| Сценарий | Итог |\n|---|---|"
        body = "\n".join(f"| `{row['id']}` · {row['title']} | {'✅ проходит' if row['status'] == 'pass' else '❌ ошибка'} |" for row in rows)
        fixes_h = "## Исправления"
        fixes = ("- S3 получил отдельный reset через M1-36 и остаётся fault-UI; C5 и RF RP по-прежнему сбрасываются напрямую.\n"
                 "- Вход PA23 получил внешний 10-кОм pulldown переиспользованием прежней лишней позиции: BOM и цена не выросли.\n"
                 "- Антиавтозапуск теперь опирается на квалифицированный физический KILL, а не на предположение о моменте RC-фронта.")
        residual_h = "## Что остаётся физике"
        residual = "\n".join(f"- {row}" for row in manifest["physical_residuals"])
        end = f"**Результат:** `{s['passed_scenarios']}/{s['scenarios']}` сценариев и `{s['topology_endpoints']}` endpoint-проверок проходят. H3-R2.3, [цифровая проверка H3-R2.4](digital-electrical-verification.ru.md), [RF-проверка H3-R2.5](rf-electrical-verification.ru.md), [thermal/fault H3-R2.6](thermal-fault-electrical-verification.ru.md) и итог H3-R2.7 проведены ревью; **текущий маркер — `H4-R2.0.1`**. Заказ и трассировка всё ещё запрещены.\n\n[Машинный отчёт](../hardware/verification/generated/H3-R2-transition-sequences.json)."
    else:
        title = "# Startup, reset and recovery · H3-R2.2.1"
        nav = "[Русский](power-transition-sequences.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)"
        intro = ("`H3-R2.2.1` verification is complete: every startup and fault-recovery scenario passes without automatic restart. "
                 "An ordinary fault removes hazardous domains and directly resets C5/RF RP, while S3 can keep a readable cause on screen whenever UI power remains available.")
        states_h = "## Startup rule"
        states = ("Safety holds `SAFETY_FAULT_REQUEST` active after reset. Self-test must pass, physical `KILL` must remain continuous for 500 ms, "
                  "and only the following `KILL→RUN` edge may clock the hardware `RUN_PERMIT` latch. USB, software reset and fault recovery create no such edge.")
        timing_h = "## Exact bounds"
        timing = (f"- TPS3808 with CT open: `{t['supervisor_ct_open_reset_delay_ms']['min']}..{t['supervisor_ct_open_reset_delay_ms']['max']} ms`; reset assertion within `{t['supervisor_assertion_max_us']} us`.\n"
                  f"- TPS3435: device startup within `{t['watchdog_device_startup_time_us_max']} us`, watchdog-window startup delay `{t['watchdog_startup_delay_ms']['max']} ms`; `{t['watchdog_timeout_s']['min']}..{t['watchdog_timeout_s']['max']} s` timeout, `{t['watchdog_assert_time_ms']['min']}..{t['watchdog_assert_time_ms']['max']} ms` WDO-low interval; heartbeat target `{t['watchdog_service_period_ms']} ms`.\n"
                  f"- 100 kohm / 2.2 uF: analytical rise `{t['rearm_rc']['rise_ms']['earliest']}..{t['rearm_rc']['rise_ms']['latest']} ms`, tolerance-only guaranteed discharge `{t['rearm_rc']['guaranteed_fall_below_vt_minus_min_ms']} ms`; this is debounce, not the sole interlock.")
        seq_h = "## Verified scenarios"
        header = "| Scenario | Result |\n|---|---|"
        body = "\n".join(f"| `{row['id']}` · {row['title']} | {'✅ pass' if row['status'] == 'pass' else '❌ fail'} |" for row in rows)
        fixes_h = "## Corrections"
        fixes = ("- S3 has an independent M1-36 reset and remains the fault UI; C5 and RF RP retain direct resets.\n"
                 "- PA23 gains an external 10-kohm pulldown by reusing the former unused position, so BOM and cost do not grow.\n"
                 "- Anti-auto-start now depends on qualified physical KILL rather than assumed RC-edge timing.")
        residual_h = "## Physical residuals"
        residual = "\n".join(f"- {row}" for row in manifest["physical_residuals"])
        end = f"**Result:** `{s['passed_scenarios']}/{s['scenarios']}` scenarios and `{s['topology_endpoints']}` endpoint checks pass. H3-R2.3, [H3-R2.4 digital verification](digital-electrical-verification.md), [H3-R2.5 RF verification](rf-electrical-verification.md), [H3-R2.6 thermal/fault verification](thermal-fault-electrical-verification.md) and H3-R2.7 are reviewed; the **current marker is `H4-R2.0.1`**. Ordering and routing remain forbidden.\n\n[Machine report](../hardware/verification/generated/H3-R2-transition-sequences.json)."
    return "\n\n".join((title, nav, intro, states_h, states, timing_h, timing, seq_h, header + "\n" + body, fixes_h, fixes, residual_h, residual, end)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if manifest["errors"]:
        raise SystemExit("H3-R2.2.1 failed: " + "; ".join(manifest["errors"]))
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"wrote H3-R2.2.1: {manifest['summary']['passed_scenarios']}/{manifest['summary']['scenarios']} scenarios")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.2.1 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.2.1 reviewed; {manifest['summary']['passed_scenarios']} scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
