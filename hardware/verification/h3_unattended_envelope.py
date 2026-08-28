#!/usr/bin/env python3
"""Build the H3.6.3 unattended-operation and endurance-test envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
THERMAL_PATH = REPO / "hardware/verification/generated/H3-VRF61-thermal-model.json"
FAULT_PATH = REPO / "hardware/verification/generated/H3-VRF62-fault-tree.json"
SOURCE_PATH = REPO / "hardware/verification/generated/H3-VRF13-source-charge-budget.json"
BATTERY_PATH = REPO / "hardware/verification/generated/H3-VRF34-battery-analog.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF63-unattended-envelope.json"
DOC_EN = REPO / "docs/unattended-operation.md"
DOC_RU = REPO / "docs/unattended-operation.ru.md"


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, quantum: str = "0.001") -> str:
    return str(value.quantize(Decimal(quantum), rounding=ROUND_HALF_UP))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    thermal = json.loads(THERMAL_PATH.read_text(encoding="utf-8"))
    fault = json.loads(FAULT_PATH.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    battery = json.loads(BATTERY_PATH.read_text(encoding="utf-8"))

    cell = battery["cell_contract"]
    typical_energy_wh = d(2) * d(cell["nominal_voltage_v"]) * d(cell["typical_capacity_mah"]) / d(1000)
    minimum_energy_wh = d(2) * d(cell["nominal_voltage_v"]) * d(cell["minimum_capacity_mah"]) / d(1000)

    candidates = [
        state for state in source["states"]
        if state["usb"] == "USB_ABSENT"
        and state["pack"] == "PACK_2S_LOW"
        and state["charge_mode"] == "PACK_DISCHARGE"
        and state["system_mode"] == "RUN"
        and state["support_profile"] == "SUPPORT_IDLE"
    ]
    worst_by_group: dict[str, dict] = {}
    for state in candidates:
        previous = worst_by_group.get(state["signal_group"])
        if previous is None or d(state["sys_demand_w"]) > d(previous["sys_demand_w"]):
            worst_by_group[state["signal_group"]] = state

    planning_rows = []
    for group, state in sorted(worst_by_group.items()):
        demand = d(state["sys_demand_w"])
        planning_rows.append({
            "signal_group": group,
            "group_mode": state["group_mode"],
            "conservative_system_demand_w": q(demand),
            "minimum_nominal_energy_ideal_ceiling_h": q(minimum_energy_wh / demand, "0.01"),
            "disposition": "planning ceiling only; not runtime, autonomy or availability promise",
        })

    self_test = {
        "ui_path": "Settings > Safety > Full self-test",
        "owner": "independent safety MSPM0 monotonic active-session timer",
        "default": "EVERY_48_H",
        "values": [
            {"id": "EVERY_24_H", "active_session_seconds": 86400, "bounded_periodic_proof": True},
            {"id": "EVERY_48_H", "active_session_seconds": 172800, "bounded_periodic_proof": True},
            {
                "id": "STARTUP_ONLY",
                "active_session_seconds": None,
                "bounded_periodic_proof": False,
                "warning": "periodic destructive fault-plane proof is disabled; proof still runs at every physical KILL-to-RUN boundary",
            },
        ],
        "change_authority": "local physical UI only; no radio, network or remote-management command",
        "activation": "a changed value is staged and becomes active only after the next physical KILL-to-RUN proof",
        "warnings_before_due_seconds": [1800, 300, 60],
        "check_now": "immediately performs the same orderly stop and requests physical KILL-to-RUN",
        "deadline_sequence": [
            "revoke every TX lease and reject renewal",
            "request every signal group quiet and record acknowledgements when available",
            "flush the bounded operation log when S3 remains healthy",
            "retain first cause FAULT_PLANE_PROOF_DUE in the safety controller",
            "hold SAFETY_FAULT_REQUEST low and require physical KILL-to-RUN",
        ],
        "invariants": [
            "the setting never changes watchdog service, temperature FAULT_KILL, power-fault handling or TX-lease limits",
            "loss of S3, its settings storage or the settings mailbox cannot extend the already active safety-controller deadline",
            "power loss cannot bypass proof because the next RUN admission repeats the destructive startup proof",
        ],
    }

    ambient = {
        "design_target_c": {"minimum": 0, "maximum": 35},
        "status": "accepted engineering target pending H6/H8; not a published operating guarantee",
        "charge_behavior": "normal charge request is zero above 35 C; charge is blocked at the independent hot/cold limits and on any cell-sensor fault",
        "h6_base_to_ambient_rtheta_k_per_w_max_at_35c": {
            "quiet_support_idle": thermal["ambient_parameter_sweep"]["quiet_idle"][1]["rtheta_base_to_ambient_for_65c_warning_k_per_w_max"],
            "voice_support_idle_worst_group": thermal["ambient_parameter_sweep"]["support_idle_worst_group"][1]["rtheta_base_to_ambient_for_65c_warning_k_per_w_max"],
            "qualified_external_support_idle": q(d(30) / d("3.249")),
        },
        "rule": "H6 must meet the applicable resistance and H8 must measure it before any sustained profile is admitted",
    }

    source_policy = {
        "runtime_claim": "none; no battery or USB operating duration is promised",
        "extended_operation_guidance": "connect a qualified USB-PD source for long operation",
        "battery_table_role": "pre-HIL energy planning only; real usable energy, cutoff, ageing and profile duration are measured in H8",
        "usb_rule": "USB removes the finite-pack-energy premise but never relaxes thermal, watchdog, fault, quiet-state or lease rules",
        "endurance_interpretation": "24-hour and 48-hour intervals are H8 validation durations and selectable self-test intervals, not product uptime or autonomy specifications",
    }

    sustained_policy = {
        "candidate_profiles": "SUPPORT_IDLE only, one active top-level signal group; all final permissions remain profile-specific",
        "excluded": [
            "SUPPORT_WORST as a sustained state",
            "continuous or unleased TX",
            "an unknown or unqualified external accessory",
            "operation after any required thermal/evidence/power sensor becomes unreadable",
        ],
        "tx": "TX remains a short bounded lease inside an otherwise admitted profile; H8 sets final duty and session limits",
        "logging": [
            "active profile and source state",
            "all three board-zone temperatures and both cell temperatures",
            "rail/power-fault flags, active lease and actual-TX evidence mask",
            "self-test setting, elapsed active-session time, warnings and retained first cause",
        ],
    }

    hil = [
        "H6: meet the profile-specific 35-C base-to-ambient resistance target with final copper, vias, enclosure and installed accessory geometry",
        "H8: run 24-hour and 48-hour USB-powered endurance cases as validation tests, including the configured proof-due stop and retained display reason",
        "H8: run each battery profile to its real protected cutoff and publish measurements only as test results, not guaranteed autonomy",
        "H8: chamber-test admitted sustained profiles at 0, 25 and 35 C plus boundary/fault behavior outside the design target",
        "H8: verify all three self-test settings, staged activation, local-only authority, warning sequence, S3-loss behavior and physical KILL-to-RUN recovery",
        "H8: correlate final thermal time constants and set per-profile TX duty/session limits before release",
    ]

    settings = {row["id"]: row for row in self_test["values"]}
    group_rows = {row["signal_group"]: row for row in planning_rows}
    checks = {
        "typical_pack_energy_is_28_8wh": typical_energy_wh == d("28.8"),
        "minimum_nominal_pack_energy_is_27_36wh": minimum_energy_wh == d("27.36"),
        "all_ten_signal_groups_have_planning_rows": len(planning_rows) == 10,
        "quiet_ideal_ceiling_is_below_24h": d(group_rows["NONE"]["minimum_nominal_energy_ideal_ceiling_h"]) < d(24),
        "no_runtime_claim_is_made": source_policy["runtime_claim"].startswith("none"),
        "long_operation_uses_usb_guidance": "USB-PD" in source_policy["extended_operation_guidance"],
        "endurance_intervals_are_tests_not_promises": "not product uptime" in source_policy["endurance_interpretation"],
        "self_test_default_is_48h": self_test["default"] == "EVERY_48_H" and settings["EVERY_48_H"]["active_session_seconds"] == 172800,
        "self_test_24h_is_available": settings["EVERY_24_H"]["active_session_seconds"] == 86400,
        "startup_only_is_explicit_unbounded_override": settings["STARTUP_ONLY"]["bounded_periodic_proof"] is False,
        "self_test_changes_require_physical_rearm": "KILL-to-RUN" in self_test["activation"],
        "self_test_setting_is_local_only": "local physical UI only" in self_test["change_authority"],
        "deadline_revokes_tx_before_fault_request": self_test["deadline_sequence"][0].startswith("revoke every TX lease") and self_test["deadline_sequence"][-1].startswith("hold SAFETY_FAULT_REQUEST"),
        "watchdog_and_thermal_limits_are_not_configurable_here": "never changes watchdog" in self_test["invariants"][0],
        "fault_plane_requires_physical_rearm_proof": "KILL-to-RUN" in fault["fault_plane"]["destructive_test_boundary"],
        "ambient_target_is_0_to_35c": ambient["design_target_c"] == {"minimum": 0, "maximum": 35},
        "ambient_target_is_not_a_guarantee": "not a published" in ambient["status"],
        "quiet_35c_rtheta_matches_h3_6_1": ambient["h6_base_to_ambient_rtheta_k_per_w_max_at_35c"]["quiet_support_idle"] == "16.713",
        "voice_35c_rtheta_matches_h3_6_1": ambient["h6_base_to_ambient_rtheta_k_per_w_max_at_35c"]["voice_support_idle_worst_group"] == "5.446",
        "support_worst_is_not_sustained": any("SUPPORT_WORST" in row for row in sustained_policy["excluded"]),
        "tx_remains_bounded": "bounded lease" in sustained_policy["tx"],
        "physical_residuals_are_assigned": len(hil) == 6 and all(row.startswith(("H6:", "H8:")) for row in hil),
        "upstream_thermal_review_is_clean": thermal["review_summary"]["unresolved_analytical_findings"] == 0,
        "upstream_fault_review_is_clean": fault["review_summary"]["unresolved_analytical_findings"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.6.3 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.6.3",
        "status": "reviewed_unattended_safety_and_endurance_test_envelope",
        "method": "conservative source-energy bounds plus accepted ambient target, configurable destructive-proof interval and explicit H6/H8 admission gates",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (THERMAL_PATH, FAULT_PATH, SOURCE_PATH, BATTERY_PATH)
        },
        "accepted_product_policy": source_policy,
        "ambient_design_target": ambient,
        "fault_plane_self_test_setting": self_test,
        "sustained_operation_policy": sustained_policy,
        "pack_energy": {
            "topology": "2S; voltage and energy add, ampere-hours do not",
            "typical_nominal_wh": q(typical_energy_wh, "0.01"),
            "minimum_nominal_wh": q(minimum_energy_wh, "0.01"),
            "planning_rows": planning_rows,
        },
        "h6_h8_required_evidence": hil,
        "checks": checks,
        "open_findings": [],
        "pending_decisions": [],
        "non_claims": [
            "guaranteed battery runtime, USB uptime or availability",
            "a final product operating-temperature range before H8",
            "continuous SUPPORT_WORST, continuous TX or operation with an unqualified accessory",
            "thermal closure before H6 or endurance/fault closure before H8",
        ],
        "review_summary": {
            "checks": len(checks),
            "failed": 0,
            "unresolved_analytical_findings": 0,
            "status": "reviewed",
        },
        "next": {"stage": "H3.6.4", "action": "consolidate thermal, fault and unattended-operation evidence"},
    }
    return {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(manifest, russian=False),
        DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    rows = manifest["pack_energy"]["planning_rows"]
    if russian:
        title = "# Длительная работа и self-test · historical R1"
        intro = (
            "`H3.6.3` проведён ревью. Устройство не обещает автономность или uptime в часах: "
            "для долгой работы подключается USB-PD, а 24/48 часов остаются длительностью испытаний H8."
        )
        target = (
            "Цель проектирования до физических измерений — `0…35 °C`, не паспортная гарантия. "
            "При 35 °C H6 должен получить не хуже `16,713 K/W` для quiet и `5,446 K/W` для тяжёлого voice RX."
        )
        setting = (
            "В `Настройки → Безопасность → Полный self-test` доступны `24 часа`, `48 часов` по умолчанию "
            "и `только при запуске`. Изменение применяется после следующего физического `KILL → RUN`. "
            "Настройка не меняет watchdog, thermal FAULT_KILL или TX-lease."
        )
        headers = "| Группа | Тяжёлый SUPPORT_IDLE | Идеальный предел от минимальной энергии, не обещание |\n|---|---|---:|"
        table = "\n".join(
            f"| `{row['signal_group']}` | `{row['group_mode']}` / {row['conservative_system_demand_w']} W | {row['minimum_nominal_energy_ideal_ceiling_h']} h |"
            for row in rows
        )
        boundary = (
            "Таблица нужна только для планирования H8: она не учитывает старение, cutoff, разброс, температуру и реальные duty. "
            "SUPPORT_WORST, непрерывный TX и неизвестные расширения не допускаются как длительные режимы."
        )
        evidence = "[Машинное evidence](../hardware/verification/generated/H3-VRF63-unattended-envelope.json)."
    else:
        title = "# Extended operation and self-test · historical R1"
        intro = (
            "`H3.6.3` is reviewed. The product promises no battery autonomy or uptime in hours: "
            "long operation uses USB-PD, while 24 and 48 hours remain H8 validation durations."
        )
        target = (
            "The pre-physical engineering target is `0 to 35 °C`, not a datasheet guarantee. "
            "At 35 °C H6 must achieve no worse than `16.713 K/W` for quiet and `5.446 K/W` for heavy voice RX."
        )
        setting = (
            "`Settings > Safety > Full self-test` offers `24 hours`, default `48 hours`, and `startup only`. "
            "A change activates after the next physical `KILL to RUN`. The setting cannot alter watchdog, "
            "thermal FAULT_KILL or TX-lease behavior."
        )
        headers = "| Group | Heavy SUPPORT_IDLE case | Ideal minimum-energy ceiling, not a promise |\n|---|---|---:|"
        table = "\n".join(
            f"| `{row['signal_group']}` | `{row['group_mode']}` / {row['conservative_system_demand_w']} W | {row['minimum_nominal_energy_ideal_ceiling_h']} h |"
            for row in rows
        )
        boundary = (
            "The table is H8 planning only: it excludes ageing, cutoff, lot spread, temperature and real duty. "
            "SUPPORT_WORST, continuous TX and unknown accessories are not admitted as extended modes."
        )
        evidence = "[Machine evidence](../hardware/verification/generated/H3-VRF63-unattended-envelope.json)."
    return "\n\n".join((title, intro, target, setting, headers + "\n" + table, boundary, evidence)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    else:
        stale = [
            str(path.relative_to(REPO))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale H3.6.3 artifacts: " + ", ".join(stale))
    print(f"ok: H3.6.3 reviewed; {manifest['review_summary']['checks']} checks, next H3.6.4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
