#!/usr/bin/env python3
"""Review H2.5.4 reset-safe quiet-state controls and isolation hardware."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from h2_review_power_paths import (
    CANDIDATE_PATH,
    ECAD,
    PROJECTS,
    REPO,
    export_project,
    instance_reference_maps,
    sha256,
)


GENERATED = ECAD / "generated"
OUTPUT_MANIFEST = GENERATED / "H2-REV54-quiet-state.json"
OUTPUT_DOC_EN = REPO / "docs/quiet-state.md"
OUTPUT_DOC_RU = REPO / "docs/quiet-state.ru.md"

GROUP_EVIDENCE = {
    "N24_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("nrf_power_switch", "nrf_power_on_pulldown", "safe_gate_a",
                      "nrf0_host_buffer", "nrf1_host_buffer", "nrf2_host_buffer",
                      "nrf0_return_buffer", "nrf1_return_buffer", "nrf2_return_buffer"),
        "nets": {
            "NRF_GROUP_PWR_EN": {"rp", "safe_gate_a"},
            "NRF_GROUP_PWR_EN_SAFE": {"safe_gate_a", "nrf_power_switch", "nrf_power_on_pulldown"},
        },
        "class": "rail_off_plus_bidirectional_signal_isolation",
    },
    "CC_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("cc_power_switch", "cc_power_on_pulldown", "safe_gate_b",
                      "cc_host_buffer", "cc_return_buffer"),
        "nets": {
            "CC_PWR_EN": {"rp", "safe_gate_b"},
            "CC_PWR_EN_SAFE": {"safe_gate_b", "cc_power_switch", "cc_power_on_pulldown"},
        },
        "class": "rail_off_plus_bidirectional_signal_isolation",
    },
    "U214_CAP_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("ext_efuse", "u214_req_pulldown", "ext_branch_gate", "u214_supervisor",
                      "u214_host_buffer_a", "u214_host_buffer_b", "u214_return_buffer", "u214_i2c_iso"),
        "nets": {
            "U214_5V_REQ": {"m1_rf_receptacle", "u214_req_pulldown", "ext_branch_gate"},
            "U214_5V_EN_SAFE": {"ext_branch_gate", "ext_efuse", "u214_supervisor"},
            "U214_READY": {"u214_supervisor", "u214_host_buffer_a", "u214_host_buffer_b",
                           "u214_return_buffer", "u214_i2c_iso"},
        },
        "class": "reverse_blocked_rail_off_plus_eleven_signal_isolation",
    },
    "UNIT_PORT_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("unit_efuse", "unit_req_pulldown", "ext_branch_gate", "unit_supervisor",
                      "unit_signal_iso", "unit_signal_iso_oe_pulldown"),
        "nets": {
            "UNIT_5V_REQ": {"m1_rf_receptacle", "unit_req_pulldown", "ext_branch_gate"},
            "UNIT_5V_EN_SAFE": {"ext_branch_gate", "unit_efuse", "unit_supervisor"},
            "UNIT_READY": {"unit_supervisor", "unit_signal_iso", "unit_signal_iso_oe_pulldown"},
        },
        "class": "reverse_blocked_rail_off_plus_two_signal_isolation",
    },
    "VOICE_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("voice_buck", "voice_en_pulldown", "voice_efuse", "safe_gate_b",
                      "safe_ptt_or", "voice_ptt_iso", "voice_ptt_pullup", "voice_supervisor"),
        "nets": {
            "VOICE_DOMAIN_REQ": {"m1_rf_receptacle", "safe_gate_b"},
            "VOICE_DOMAIN_EN_SAFE": {"safe_gate_b", "voice_buck", "voice_en_pulldown", "voice_supervisor"},
            "VOICE_PTT_REQ_N": {"rp", "safe_ptt_or"},
            "VOICE_PTT_SAFE_N": {"safe_ptt_or", "voice_ptt_iso"},
            "VOICE_PTT_MODULE_N": {"voice_ptt_iso", "voice_ptt_pullup", "voice"},
        },
        "class": "rail_off_plus_hardware_ptt_off",
    },
    "RECEIVER_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("receiver_power_switch", "receiver_power_on_pulldown", "receiver_supervisor",
                      "receiver_i2c_iso", "receiver_irq_iso"),
        "nets": {"RX_DOMAIN_EN": {"slow_io", "receiver_power_switch", "receiver_power_on_pulldown"}},
        "class": "rail_off_reset_asserted_and_control_isolated",
    },
    "CODEC_AUDIO_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("codec_power_switch", "codec_power_on_pulldown", "codec_supervisor",
                      "codec_i2c_iso", "codec_i2s_bclk_iso", "codec_i2s_ws_iso",
                      "codec_i2s_din_iso", "codec_i2s_dout_iso", "audio_safe_gate",
                      "audio_arm_pulldown"),
        "nets": {"AUDIO_ARM": {"s3", "audio_arm_pulldown", "audio_safe_gate"}},
        "class": "rail_off_plus_i2c_i2s_and_audio_output_isolation",
    },
    "VOICE_INTERFACE_QUIET": {
        "project": "LESHY2-RF",
        "instances": ("voice_io_power_switch", "voice_uart_tx_iso", "voice_audio_iso",
                      "voice_ptt_iso", "voice_hl_driver"),
        "nets": {
            "VOICE_PTT_SAFE_N": {"safe_ptt_or", "voice_ptt_iso"},
            "VOICE_PTT_MODULE_N": {"voice_ptt_iso", "voice"},
        },
        "class": "switched_io_rail_plus_digital_and_analog_isolation",
    },
    "IR_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("ir_power_switch", "ir_power_on_pulldown", "ir_return_buffer",
                      "ir_safe_gate", "ir_tx_mosfet", "ir_tx_gate_pulldown"),
        "nets": {"IR_FRONTEND_PWR_EN": {"c5", "ir_power_switch", "ir_power_on_pulldown"}},
        "class": "receiver_rail_off_plus_fault_dominant_emitter_gate",
    },
    "S3_RF_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("s3", "s3_evidence_output_pullup"),
        "nets": {},
        "class": "native_rf_block_off_cpu_remains_alive",
    },
    "C5_RF_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("c5", "c5_evidence_output_pullup"),
        "nets": {},
        "class": "native_rf_block_off_cpu_remains_alive",
    },
    "STORAGE_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("sd_power_switch", "sd_on_pulldown", "sd_host_buffer", "sd_miso_buffer"),
        "nets": {"SD_PWR_EN": {"slow_io", "sd_power_switch", "sd_on_pulldown"}},
        "class": "bounded_flush_then_rail_off_and_bus_static",
    },
    "SERVICE_IPC_QUIET": {
        "project": "LESHY2-UI",
        "instances": ("c5_service_usb_switch", "s3", "c5", "display_connector"),
        "nets": {},
        "class": "bounded_transaction_then_controller_clock_and_dma_stop",
    },
}


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    quiet = candidate["quiet_state_policy"]
    if quiet["default_state"] != "QUIET":
        raise ValueError("boot/default state must remain QUIET")
    contracts = {row["id"]: row for row in quiet["contracts"]}
    if len(contracts) != len(quiet["contracts"]):
        raise ValueError("duplicate quiet-state contract id")
    if quiet["required_contracts"] != list(contracts):
        raise ValueError("required quiet-state contracts and definitions differ or changed order")
    if set(contracts) != set(GROUP_EVIDENCE):
        raise ValueError(
            f"quiet-state scope drifted; missing={sorted(set(GROUP_EVIDENCE)-set(contracts))}, "
            f"extra={sorted(set(contracts)-set(GROUP_EVIDENCE))}"
        )

    groups = candidate["signal_group_policy"]
    if groups["default_group"] != "NONE" or groups["exclusive"] is not True:
        raise ValueError("signal-group default must remain NONE and exclusive")
    if groups["required_full_mix_groups"] != ["SG-N24"]:
        raise ValueError("only SG-N24 may require internal full-mix operation")

    reference_maps, details = instance_reference_maps()
    actual_nets = {}
    stats = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h254-") as temp_dir:
        for project in sorted({row["project"] for row in GROUP_EVIDENCE.values()}):
            actual_nets[project], stats[project] = export_project(
                project, PROJECTS[project], Path(temp_dir) / f"{project}.xml"
            )

    reviewed = []
    for group_id, evidence in GROUP_EVIDENCE.items():
        project = evidence["project"]
        missing_instances = [item for item in evidence["instances"] if item not in details]
        if missing_instances:
            raise ValueError(f"{group_id} lacks instantiated evidence: {missing_instances}")
        parts = []
        for instance in evidence["instances"]:
            row = details[instance]
            if not row.get("mpn") or not row.get("footprint"):
                raise ValueError(f"{group_id}/{instance} lacks exact MPN/footprint")
            parts.append({"instance": instance, "reference": row["reference"], "mpn": row["mpn"]})
        checked_nets = []
        for net, required_instances in evidence["nets"].items():
            refs = actual_nets[project].get(net, set())
            actual_instances = {reference_maps[project].get(ref, ref) for ref in refs}
            missing = sorted(required_instances - actual_instances)
            if missing:
                raise ValueError(f"{group_id}/{net} lacks required members: {missing}")
            checked_nets.append({"net": net, "required_members": sorted(required_instances)})
        contract = contracts[group_id]
        if not contract["inactive_state"] or not contract["control"] or not contract["proof_gate"]:
            raise ValueError(f"{group_id} has incomplete state/control/HIL contract")
        reviewed.append({
            "id": group_id, "status": "reviewed", "project": project,
            "isolation_class": evidence["class"], "inactive_state": contract["inactive_state"],
            "control": contract["control"], "checked_nets": checked_nets,
            "critical_parts": parts,
        })

    manifest = {
        "schema_version": 1,
        "stage": "H2.5.4",
        "status": "reviewed_reset_safe_quiet_state_and_isolation",
        "method": "complete KiCad netlist control-membership checks plus exact instantiated isolation evidence for every required quiet contract",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, PROJECTS["LESHY2-UI"], PROJECTS["LESHY2-RF"])
        },
        "hierarchy_exports": stats,
        "corrected_findings": [{
            "id": "H2.5.4-F01",
            "severity": "contract_traceability",
            "finding": "VOICE_QUIET and VOICE_INTERFACE_QUIET retained obsolete abstract VOICE_PTT_N and VOICE_DOMAIN_EN names",
            "correction": "the contracts now name the implemented request, safety-gated and module-side PTT nets plus request and safe domain-enable nets",
            "evidence": "all five voice request/safe/module control nets are present with the required hardware members in the complete RF hierarchy",
        }],
        "default_state": quiet["default_state"],
        "signal_group_policy": {
            "default_group": groups["default_group"], "exclusive": groups["exclusive"],
            "internal_full_mix_exception": groups["required_full_mix_groups"],
        },
        "reviewed_contract_count": len(reviewed),
        "reviewed_contracts": reviewed,
        "invariants": [
            "boot and reset default to no active signal group",
            "only the three nRF24 paths may operate as one internally simultaneous full-mix group",
            "switched peripherals have off-safe pulls and an explicit power or signal-isolation boundary",
            "S3/C5 native radios use vendor RF-block-off states because their CPUs remain alive for UI, IR and recovery",
            "display, USB and processor IPC clocks run only for bounded transactions and remain static otherwise",
            "paper review does not claim radiated quietness; current, discharge, spectrum and desense remain measured HIL gates",
        ],
        "review_boundary": {
            "complete": [
                "all 13 required quiet contracts map to exact fitted MPNs and complete-hierarchy control nets",
                "reset defaults, off-safe pulls, switched rails and isolation devices are explicit",
                "the native-radio and bounded-transaction exceptions are explicit rather than represented as nonexistent load switches",
            ],
            "deferred": [
                "powered-off leakage and rail-discharge timing in H3/H8",
                "no-carrier/no-optical-output and active-receiver desense HIL in H8",
                "DMA/clock spectral measurements and simultaneous SG-N24 full-mix proof in firmware F3/H8",
            ],
        },
    }
    return {
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        OUTPUT_DOC_EN: render_doc(manifest, russian=False),
        OUTPUT_DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    display = {
        "rail_off_plus_bidirectional_signal_isolation": ("питание снято; сигналы high-Z", "rail off; signals high-Z"),
        "reverse_blocked_rail_off_plus_eleven_signal_isolation": ("reverse-blocked 5 В off; 11 сигналов изолированы", "reverse-blocked 5 V off; 11 signals isolated"),
        "reverse_blocked_rail_off_plus_two_signal_isolation": ("reverse-blocked 5 В off; 2 сигнала изолированы", "reverse-blocked 5 V off; 2 signals isolated"),
        "rail_off_plus_hardware_ptt_off": ("питание снято; PTT аппаратно off", "rail off; hardware PTT off"),
        "rail_off_reset_asserted_and_control_isolated": ("питание снято; reset и control isolation", "rail off; reset and control isolation"),
        "rail_off_plus_i2c_i2s_and_audio_output_isolation": ("питание снято; I²C/I²S/audio изолированы", "rail off; I²C/I²S/audio isolated"),
        "switched_io_rail_plus_digital_and_analog_isolation": ("I/O rail off; digital/analog изоляция", "I/O rail off; digital/analog isolation"),
        "receiver_rail_off_plus_fault_dominant_emitter_gate": ("RX rail off; TX gate fault-dominant", "RX rail off; fault-dominant TX gate"),
        "native_rf_block_off_cpu_remains_alive": ("native RF off; CPU остаётся включён", "native RF off; CPU remains alive"),
        "bounded_flush_then_rail_off_and_bus_static": ("flush, затем rail off и static bus", "flush, then rail off and static bus"),
        "bounded_transaction_then_controller_clock_and_dma_stop": ("только bounded transaction; затем clock/DMA stop", "bounded transaction only; then clock/DMA stop"),
    }
    if russian:
        title = "# Тихое состояние Leshy2"
        nav = "[English](quiet-state.md) · [На главную](../README.ru.md) · [Изоляция интерфейсов](interface-isolation.ru.md)"
        intro = "По умолчанию активной группы нет. Неиспользуемые радио и интерфейсы переводятся в проверяемое аппаратно безопасное состояние."
        headers = "| Группа | Неактивное состояние |\n|---|---|"
        result = f"## Результат H2.5.4\n\n✅ **Проведено ревью:** все {manifest['reviewed_contract_count']} quiet-state контрактов сопоставлены с реальными цепями KiCad и точными серийными компонентами."
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV54-quiet-state.json)."
        idx = 0
    else:
        title = "# Leshy2 quiet state"
        nav = "[Русский](quiet-state.ru.md) · [Home](../README.md) · [Interface isolation](interface-isolation.md)"
        intro = "No signal group is active by default. Every unused radio and interface enters a reviewable hardware-safe state."
        headers = "| Group | Inactive state |\n|---|---|"
        result = f"## H2.5.4 result\n\n✅ **Reviewed:** all {manifest['reviewed_contract_count']} quiet-state contracts map to actual KiCad nets and exact serial components."
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV54-quiet-state.json)."
        idx = 1
    rows = [f"| `{row['id']}` | {display[row['isolation_class']][idx]} |" for row in manifest["reviewed_contracts"]]
    note = ("`SG-N24` — единственное исключение: три nRF24 могут одновременно работать в полном RX/TX mix внутри одной активной группы."
            if russian else "`SG-N24` is the sole exception: all three nRF24 paths may run a full RX/TX mix inside one active group.")
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(rows), note, result, evidence)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items()
                 if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.5.4 quiet-state review is current; {manifest['reviewed_contract_count']} contracts reviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
