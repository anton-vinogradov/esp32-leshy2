#!/usr/bin/env python3
"""Review H2.5.2 reset, boot, service and recovery paths from KiCad netlists."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path

from h2_review_power_paths import (
    CANDIDATE_PATH,
    ECAD,
    LEDGER_PATH,
    PROJECTS,
    REPO,
    export_project,
    instance_reference_maps,
    sha256,
)
from h2_ui_audio_codec_headset import endpoint_nets


GENERATED = ECAD / "generated"
OUTPUT_MANIFEST = GENERATED / "H2-REV52-recovery-paths.json"
OUTPUT_DOC_EN = REPO / "docs/service-recovery.md"
OUTPUT_DOC_RU = REPO / "docs/service-recovery.ru.md"

REVIEWED_NETS = {
    "LESHY2-UI": (
        "S3_RESET_N", "I2S_DIN", "S3_UART_SERVICE_TX", "S3_UART_SERVICE_RX",
        "S3_USB_DP_LOCAL", "S3_USB_DM_LOCAL",
        "S3_DBG_RESET_CONNECTOR_N", "S3_DBG_BOOT_CONNECTOR_N",
        "S3_DBG0_CONNECTOR", "S3_DBG1_CONNECTOR",
        "C5_RESET_N", "C5_BOOT_N", "C5_UART_SERVICE_TX", "C5_UART_SERVICE_RX",
        "C5_USB_DP", "C5_USB_DM", "C5_GPIO27_FIXED_HIGH",
        "C5_DBG_RESET_CONNECTOR_N", "C5_DBG_BOOT_CONNECTOR_N",
        "C5_DBG0_CONNECTOR", "C5_DBG1_CONNECTOR",
    ),
    "LESHY2-RF": (
        "USB2_DP_CONNECTOR", "USB2_DM_CONNECTOR", "S3_USB_DP", "S3_USB_DM",
        "RP_RESET_N", "RP_USB_BOOT_N", "RP_SWDIO", "RP_SWCLK", "RP_USB_DP", "RP_USB_DM",
        "RP_DBG_RESET_CONNECTOR_N", "RP_DBG_BOOT_CONNECTOR_N", "RP_DBG0_CONNECTOR", "RP_DBG1_CONNECTOR",
        "PACK_FIXTURE_3V3", "PACK_ADMISSION_NRST_N", "PACK_ADMISSION_UART_TX",
        "PACK_ADMISSION_UART_RX", "PACK_ADMISSION_SWDIO", "PACK_ADMISSION_SWCLK",
        "PACK_GAUGE_I2C_SDA", "PACK_GAUGE_I2C_SCL", "PACK_FET_OVERRIDE_N", "PACK_PFAIL_RAW",
        "SAFETY_CONTROLLER_NRST_N", "SAFETY_SERVICE_UART_TX", "SAFETY_SERVICE_UART_RX",
        "SAFETY_SWDIO", "SAFETY_SWCLK",
        "SYS_I2C_SDA", "SYS_I2C_SCL", "SYS_INT_N",
        "PD_LOCAL_I2C_SDA", "PD_LOCAL_I2C_SCL", "PD_EEPROM_WP",
        "VOICE_UPDATE_FIXTURE", "VOICE_UART_TX", "VOICE_UART_RX", "VOICE_READY",
        "RP_SERVICE_VBUS_SENSE_ONLY",
    ),
}

EXPECTED_ADDITIONS = {
    "LESHY2-UI": {
        "S3_RESET_N": {"TP_S3_RUN"},
        "C5_RESET_N": {"TP_C5_RUN"},
        "C5_GPIO27_FIXED_HIGH": {"TP_C5_GPIO27_FIXED_HIGH"},
    },
    "LESHY2-RF": {
        "S3_USB_DP": {"m1_rf_receptacle"},
        "S3_USB_DM": {"m1_rf_receptacle"},
        "PACK_FIXTURE_3V3": {"TP_PACK_FIXTURE_3V3"},
        "RP_RESET_N": {"TP_RP_RESET_N"},
        "PACK_ADMISSION_NRST_N": {"TP_PACK_NRST"},
        "PACK_ADMISSION_UART_TX": {"TP_PACK_UART_TX"},
        "PACK_ADMISSION_UART_RX": {"TP_PACK_UART_RX"},
        "PACK_ADMISSION_SWDIO": {"TP_PACK_SWDIO"},
        "PACK_ADMISSION_SWCLK": {"TP_PACK_SWCLK"},
        "SAFETY_CONTROLLER_NRST_N": {"TP_SAFETY_NRST"},
        "SAFETY_SERVICE_UART_TX": {"TP_SAFETY_UART_TX"},
        "SAFETY_SERVICE_UART_RX": {"TP_SAFETY_UART_RX"},
        "SAFETY_SWDIO": {"TP_SAFETY_SWDIO"},
        "SAFETY_SWCLK": {"TP_SAFETY_SWCLK"},
        "SYS_I2C_SDA": {"m1_rf_receptacle", "TP_SYS_I2C_SDA"},
        "SYS_I2C_SCL": {"m1_rf_receptacle", "TP_SYS_I2C_SCL"},
        "SYS_INT_N": {"m1_rf_receptacle", "TP_SYS_INT_N"},
        "PD_LOCAL_I2C_SDA": {"TP_PD_LOCAL_I2C_SDA"},
        "PD_LOCAL_I2C_SCL": {"TP_PD_LOCAL_I2C_SCL"},
        "PD_EEPROM_WP": {"TP_PD_EEPROM_WP"},
        "VOICE_UPDATE_FIXTURE": {"TP_VOICE_UPDATE"},
        "RP_SERVICE_VBUS_SENSE_ONLY": {"TP_RP_SERVICE_VBUS_SENSE"},
    },
}

TARGETS = [
    {
        "target": "ESP32-S3",
        "primary": "protected product USB-C (native USB Serial/JTAG)",
        "fallback": "internal keyed DBG10 UART0 + RESET/BOOT; two recessed side switches",
        "project": "LESHY2-UI + LESHY2-RF",
    },
    {
        "target": "ESP32-C5",
        "primary": "dedicated data-only USB-C through FSUSB42MUX",
        "fallback": "internal keyed DBG10 UART0 + RESET/BOOT; two recessed side switches",
        "project": "LESHY2-UI",
    },
    {
        "target": "RP2354B",
        "primary": "dedicated data-only USB-C through FSUSB42MUX",
        "fallback": "internal keyed DBG10 SWD + RUN/USB_BOOT; two recessed side switches",
        "project": "LESHY2-RF",
    },
    {
        "target": "pack-admission MSPM0",
        "primary": "internal current-limited fixture VDD/GND + UART + SWD + NRST pads",
        "fallback": "none required; permanent SWD and UART are both present",
        "project": "LESHY2-RF",
    },
    {
        "target": "AON safety MSPM0",
        "primary": "internal AON-powered UART + SWD + NRST pads",
        "fallback": "recovery cannot release RUN_PERMIT or clear hardware FAULT_KILL",
        "project": "LESHY2-RF",
    },
    {
        "target": "TPS25751D + configuration EEPROM",
        "primary": "SYS_I2C target pads plus direct local SDA/SCL/WP pads",
        "fallback": "pre-programmed loose EEPROM or current-limited raw-VBUS fixture",
        "project": "LESHY2-RF",
    },
    {
        "target": "MAX17320 pack gauge",
        "primary": "internal protected local I2C and fault/hold observation",
        "fallback": "image checksum and override readback before energized cell installation",
        "project": "LESHY2-RF",
    },
    {
        "target": "SA518 voice module",
        "primary": "internal UPDATE pad plus permanent UART and hardware PD",
        "fallback": "UPDATE stays inhibited until module-revision timing is qualified",
        "project": "LESHY2-RF",
    },
]

CRITICAL_INSTANCES = (
    "product_usb_connector", "s3_dbg_header", "s3_reset_button", "s3_boot_button",
    "c5_service_usb_connector", "c5_service_usb_switch", "c5_dbg_header",
    "c5_reset_button", "c5_boot_button", "rp_service_usb_connector",
    "rp_service_usb_switch", "rp_dbg_header", "rp_reset_button", "rp_boot_button",
    "pack_admission", "safety_controller", "pd_controller", "pd_config_eeprom",
    "pack_gauge", "voice",
)


def expected_members(candidate: dict, ledger: dict, project: str) -> dict[str, set[str]]:
    local = {row["instance"] for row in ledger["rows"] if row["project"] == project}
    root_name = "UI" if project == "LESHY2-UI" else "RF"
    root = json.loads((GENERATED / f"H2-{root_name}-root-interface.json").read_text(encoding="utf-8"))
    interface_order = [net for sheet in root["sheets"] for net in sheet["interfaces"]]
    endpoints, _, _ = endpoint_nets(candidate, local, interface_order)
    by_net: dict[str, set[str]] = defaultdict(set)
    for (instance, _), net in endpoints.items():
        by_net[net].add(instance)
    for net, additions in EXPECTED_ADDITIONS[project].items():
        by_net[net].update(additions)
    return by_net


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    reference_maps, details = instance_reference_maps()
    exports = {}
    actual_nets = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h252-") as temp_dir:
        for project in REVIEWED_NETS:
            nets, stats = export_project(
                project, PROJECTS[project], Path(temp_dir) / f"{project}.xml"
            )
            actual_nets[project] = nets
            exports[project] = stats

    reviewed = []
    for project, nets in REVIEWED_NETS.items():
        ref_to_instance = reference_maps[project]
        expected = expected_members(candidate, ledger, project)
        for net in nets:
            actual_refs = actual_nets[project].get(net, set())
            if not actual_refs:
                raise ValueError(f"{project} recovery net is absent: {net}")
            unknown = sorted(actual_refs - ref_to_instance.keys())
            if unknown:
                raise ValueError(f"{project}/{net} has unmapped references: {unknown}")
            actual = {ref_to_instance[ref] for ref in actual_refs}
            if actual != expected.get(net, set()):
                raise ValueError(
                    f"{project}/{net} membership drifted; "
                    f"missing={sorted(expected.get(net, set()) - actual)}, "
                    f"extra={sorted(actual - expected.get(net, set()))}"
                )
            reviewed.append({
                "project": project,
                "net": net,
                "status": "reviewed",
                "instances": sorted(actual),
            })

    critical_parts = []
    for instance in CRITICAL_INSTANCES:
        row = details.get(instance)
        if not row:
            raise ValueError(f"recovery component has no generated instance evidence: {instance}")
        if not row.get("mpn") or not row.get("footprint"):
            raise ValueError(f"recovery component lacks exact MPN/footprint: {instance}")
        critical_parts.append({
            "instance": instance,
            "reference": row["reference"],
            "mpn": row["mpn"],
            "footprint": row["footprint"],
        })

    service = candidate["service_recovery_contract"]
    if len(candidate["services"]) != 9:
        raise ValueError("service target register must retain nine entries")
    manifest = {
        "schema_version": 1,
        "stage": "H2.5.2",
        "status": "reviewed_reset_boot_service_and_recovery_paths",
        "method": "fresh complete KiCad netlists compared with collapsed architecture endpoints and explicit fixture pads",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (
                CANDIDATE_PATH, LEDGER_PATH,
                GENERATED / "H2-UI-root-interface.json",
                GENERATED / "H2-RF-root-interface.json",
                PROJECTS["LESHY2-UI"], PROJECTS["LESHY2-RF"],
            )
        },
        "hierarchy_exports": exports,
        "corrected_findings": [{
            "id": "H2.5.2-F01",
            "severity": "recovery_blocking",
            "finding": "the reviewed service contract promised PD target-bus and direct EEPROM recovery pads, but RF60 did not instantiate them",
            "correction": "six BOM-free 1.0-mm internal copper pads now expose SYS_I2C_SDA/SCL/SYS_INT_N and PD_LOCAL_I2C_SDA/SCL/PD_EEPROM_WP",
            "evidence": "the complete RF hierarchy contains 36 physical test pads, including 13 programming/recovery pads",
        }],
        "service_scope": service["scope"],
        "targets": TARGETS,
        "reviewed_net_count": len(reviewed),
        "reviewed_nets": reviewed,
        "critical_components": critical_parts,
        "invariants": [
            "S3, C5 and RP2354B each retain independent USB plus an independent keyed DBG10 fallback",
            "all six RESET/BOOT controls are distinct recessed side switches and can only assert low",
            "both MSPM0 domains retain UART, SWD and reset even with S3/C5/RP firmware absent",
            "PD/EEPROM first programming no longer depends on an undocumented fixture contact",
            "service paths do not authorize RF re-arm, RUN_PERMIT release or FAULT_KILL clearing",
        ],
        "review_boundary": {
            "complete": [
                "every selected reset, boot, USB, UART, SWD, PD and vendor-update net is present with exact reviewed membership in exported KiCad netlists",
                "all purchased connectors, switches and active recovery devices have exact MPNs and footprints",
                "every promised fixture-only contact is represented by real PCB copper",
            ],
            "deferred": [
                "powered-off USB and fixture backfeed proof in H2.5.3",
                "reset-safe inactive-interface proof in H2.5.4",
                "USB signal-integrity and corrupted-image recovery execution in H3/H7/H8",
                "test-pad placement and fixture pitch in H6",
            ],
        },
    }
    return {
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        OUTPUT_DOC_EN: render_doc(manifest, russian=False),
        OUTPUT_DOC_RU: render_doc(manifest, russian=True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Прошивка и восстановление Leshy2"
        nav = "[English](service-recovery.md) · [На главную](../README.ru.md) · [Схемы](schematics.ru.md)"
        intro = (
            "Устройство не превращается в «кирпич» из-за повреждённой прошивки одного "
            "контроллера. Ни один recovery-путь не даёт обходить аппаратные запреты передачи."
        )
        headers = "| Цель | Основной путь | Независимый fallback | Где |\n|---|---|---|---|"
        rendered_targets = [
            ("ESP32-S3", "защищённый основной USB-C, native USB Serial/JTAG", "внутренний keyed DBG10 UART0 + RESET/BOOT; две утопленные боковые кнопки", "UI + RF"),
            ("ESP32-C5", "собственный data-only USB-C через FSUSB42MUX", "внутренний keyed DBG10 UART0 + RESET/BOOT; две утопленные боковые кнопки", "UI"),
            ("RP2354B", "собственный data-only USB-C через FSUSB42MUX", "внутренний keyed DBG10 SWD + RUN/USB_BOOT; две утопленные боковые кнопки", "RF"),
            ("MSPM0 допуска аккумуляторов", "внутренние current-limited VDD/GND + UART + SWD + NRST", "постоянно доступны и SWD, и UART", "RF"),
            ("AON safety MSPM0", "внутренние AON-powered UART + SWD + NRST", "recovery не отпускает RUN_PERMIT и не очищает аппаратный FAULT_KILL", "RF"),
            ("TPS25751D + EEPROM конфигурации", "площадки SYS_I2C и прямые SDA/SCL/WP локальной шины", "заранее прошитая EEPROM либо current-limited raw-VBUS fixture", "RF"),
            ("MAX17320 аккумуляторов", "защищённая локальная I2C и наблюдение fault/hold", "checksum образа и readback override до установки запитанных ячеек", "RF"),
            ("голосовой модуль SA518", "площадка UPDATE, постоянный UART и аппаратный PD", "UPDATE запрещён до квалификации timing конкретной ревизии модуля", "RF"),
        ]
        rendered_invariants = [
            "S3, C5 и RP2354B имеют каждый свой USB и независимый keyed DBG10 fallback",
            "все шесть RESET/BOOT — отдельные утопленные боковые кнопки, способные только притянуть сигнал к нулю",
            "оба MSPM0 сохраняют UART, SWD и reset даже без рабочей прошивки S3/C5/RP",
            "первичное программирование PD/EEPROM больше не зависит от недокументированного контакта fixture",
            "service-пути не разрешают RF re-arm, не отпускают RUN_PERMIT и не очищают FAULT_KILL",
        ]
        status = (
            f"## Результат H2.5.2\n\n✅ **Проведено ревью:** "
            f"{manifest['reviewed_net_count']} reset/boot/service/recovery цепей проверены "
            "по полным KiCad-netlist. Обнаруженный пробел PD/EEPROM исправлен шестью "
            "внутренними медными площадками без BOM и без изменения корпуса."
        )
    else:
        title = "# Leshy2 programming and recovery"
        nav = "[Русский](service-recovery.ru.md) · [Home](../README.md) · [Schematics](schematics.md)"
        intro = (
            "A damaged image in one controller cannot permanently brick the product. "
            "No recovery path can bypass hardware transmit inhibits."
        )
        headers = "| Target | Primary path | Independent fallback | Location |\n|---|---|---|---|"
        rendered_targets = [
            (row["target"], row["primary"], row["fallback"], row["project"])
            for row in manifest["targets"]
        ]
        rendered_invariants = manifest["invariants"]
        status = (
            f"## H2.5.2 result\n\n✅ **Reviewed:** {manifest['reviewed_net_count']} "
            "reset/boot/service/recovery nets are verified in complete KiCad netlists. "
            "The PD/EEPROM access gap was corrected with six internal BOM-free copper pads "
            "and no enclosure change."
        )
    rows = "\n".join(f"| {target} | {primary} | {fallback} | {place} |" for target, primary, fallback, place in rendered_targets)
    invariant_title = "## Аппаратные границы" if russian else "## Hardware boundaries"
    invariants = "\n".join(f"- {item}" for item in rendered_invariants)
    evidence = (
        "[Машинное evidence](../hardware/ecad/generated/H2-REV52-recovery-paths.json)."
        if russian else
        "[Machine evidence](../hardware/ecad/generated/H2-REV52-recovery-paths.json)."
    )
    return "\n\n".join((title, nav, intro, headers + "\n" + rows, invariant_title, invariants, status, evidence)) + "\n"


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
        stale = [
            path for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.5.2 recovery review is current; {manifest['reviewed_net_count']} nets reviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
