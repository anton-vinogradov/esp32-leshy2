#!/usr/bin/env python3
"""Review H2.5.3 powered-boundary and no-back-power invariants."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
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
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
OUTPUT_MANIFEST = GENERATED / "H2-REV53-no-back-power.json"
OUTPUT_DOC_EN = REPO / "docs/interface-isolation.md"
OUTPUT_DOC_RU = REPO / "docs/interface-isolation.ru.md"
M1_UI = GENERATED / "H2-UI40-interboard-m1.json"
M1_RF = GENERATED / "H2-RF40-interboard-m1.json"

EXACT_NETS = {
    "LESHY2-UI": {
        "C5_SERVICE_VBUS_SENSE_ONLY": {
            "c5_service_usb_connector", "c5_service_usb_vbus_bleeder",
            "TP_C5_SERVICE_VBUS_SENSE",
        },
    },
    "LESHY2-RF": {
        "RP_SERVICE_VBUS_SENSE_ONLY": {
            "rp_service_usb_connector", "rp_service_usb_vbus_bleeder",
            "TP_RP_SERVICE_VBUS_SENSE",
        },
        "USB_C_VBUS_RAW": {
            "product_usb_connector", "pd_vbus_tvs", "pd_vbus_cap", "pd_controller",
        },
        "5V_EXT_PREPROTECT": {
            "ext_input_cap", "ext_inductor", "ext_buck_output_cap0",
            "ext_buck_output_cap1", "ext_buck_fb_top", "ext_buck_ff_cap",
            "ext_efuse", "ext_ovlo_top", "unit_input_cap", "unit_efuse",
            "unit_ovlo_top",
        },
        "5V_U214_PROTECTED": {
            "ext_efuse", "ext_output_cap", "ext_bleeder", "u214",
            "u214_connector", "u214_supervisor_sense_top",
        },
        "5V_UNIT_PROTECTED": {
            "unit_efuse", "unit_output_cap", "unit_bleeder", "unit_connector",
            "unit_supervisor_sense_top",
        },
    },
}

CRITICAL_PARTS = {
    "c5_service_usb_switch": "onsemi FSUSB42MUX",
    "rp_service_usb_switch": "onsemi FSUSB42MUX",
    "ext_efuse": "Texas Instruments TPS259470LRPWR",
    "unit_efuse": "Texas Instruments TPS259470LRPWR",
    "u214_i2c_iso": "TCA4307DGKR",
    "u214_host_buffer_a": "Nexperia 74LVC126APW,118",
    "u214_host_buffer_b": "Nexperia 74LVC126APW,118",
    "u214_return_buffer": "Nexperia 74LVC126APW,118",
    "unit_signal_iso": "Texas Instruments TXS0102DCUR",
}

FORBIDDEN_M1_POWER = {
    "USB_C_VBUS_RAW", "PD_NEGOTIATED_VBUS", "PACK_SLOT0_POSITIVE_RAW",
    "PACK_SLOT1_POSITIVE_RAW", "PACK_2S_MIDPOINT", "BATTERY_STACK_POSITIVE",
    "PROTECTED_PACK_POSITIVE", "NVDC_SYS", "AON_RAW_3V3", "MAIN_RAW_3V3",
    "VVOICE_RAW_4V", "VVOICE_4V", "5V_EXT_PREPROTECT",
    "5V_U214_PROTECTED", "5V_UNIT_PROTECTED",
    "C5_SERVICE_VBUS_SENSE_ONLY", "RP_SERVICE_VBUS_SENSE_ONLY",
}


def review_m1() -> dict:
    ui = json.loads(M1_UI.read_text(encoding="utf-8"))
    rf = json.loads(M1_RF.read_text(encoding="utf-8"))
    if ui["contacts"] != rf["contacts"]:
        raise ValueError("UI and RF M1 contact maps differ")
    contacts = ui["contacts"]
    if len(contacts) != 80 or [row["contact"] for row in contacts] != list(range(1, 81)):
        raise ValueError("M1 must retain one exact ordered 80-contact map")
    counts = Counter(row["net"] for row in contacts)
    expected = {
        "3V3_MAIN": 7,
        "AON_SAFE_3V3": 2,
        "POWER_GROUND": 20,
        "AUDIO_GROUND": 3,
        "SAFETY_GROUND": 2,
    }
    for net, count in expected.items():
        if counts[net] != count:
            raise ValueError(f"M1 {net} contact count drifted: {counts[net]} != {count}")
    forbidden = sorted({row["net"] for row in contacts} & FORBIDDEN_M1_POWER)
    if forbidden:
        raise ValueError(f"raw/high-energy rails crossed M1: {forbidden}")
    return {
        "contacts": len(contacts),
        "power_and_return_contacts": expected,
        "forbidden_raw_or_exposed_rails": forbidden,
        "ui_rf_maps_identical": True,
    }


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    reference_maps, details = instance_reference_maps()

    exported = {}
    stats = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h253-") as temp_dir:
        for project in EXACT_NETS:
            exported[project], stats[project] = export_project(
                project, PROJECTS[project], Path(temp_dir) / f"{project}.xml"
            )

    reviewed_nets = []
    for project, expectations in EXACT_NETS.items():
        ref_map = reference_maps[project]
        for net, expected in expectations.items():
            refs = exported[project].get(net, set())
            unknown = sorted(refs - ref_map.keys())
            if unknown:
                raise ValueError(f"{project}/{net} has unmapped references: {unknown}")
            actual = {ref_map[ref] for ref in refs}
            if actual != expected:
                raise ValueError(
                    f"{project}/{net} membership drifted; "
                    f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
                )
            reviewed_nets.append({
                "project": project, "net": net, "status": "reviewed",
                "instances": sorted(actual),
            })

    critical_parts = []
    for instance, expected_mpn in CRITICAL_PARTS.items():
        row = details.get(instance)
        if not row or row.get("mpn") != expected_mpn or not row.get("footprint"):
            raise ValueError(f"{instance} exact MPN/footprint drifted")
        critical_parts.append({
            "instance": instance, "reference": row["reference"],
            "mpn": row["mpn"], "footprint": row["footprint"],
        })

    if devices["onsemi_fsusb42_mux"]["kind"] != "msop10_usb2_dpdt_power_off_protected_switch":
        raise ValueError("service USB switch no longer guarantees power-off protection")
    if devices["ti_tps259470l_rpwr"]["kind"] != "5_5a_true_reverse_blocking_latchoff_adjustable_efuse":
        raise ValueError("expansion eFuse no longer guarantees true reverse blocking")

    service = candidate["service_recovery_contract"]
    expansion = candidate["external_expansion_contract"]
    if "VBUS reaches only an exact 1-MOhm bleeder and a high-impedance test pad" not in service["usb"]:
        raise ValueError("service USB data-only VBUS contract drifted")
    if "Neither connector may source the common buck or the other connector" not in expansion["branch_power"]:
        raise ValueError("expansion reverse-source contract drifted")

    manifest = {
        "schema_version": 1,
        "stage": "H2.5.3",
        "status": "reviewed_no_back_power_boundaries",
        "method": "fresh complete KiCad netlists plus exact USB, M1 and expansion-boundary membership checks",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, M1_UI, M1_RF,
                         PROJECTS["LESHY2-UI"], PROJECTS["LESHY2-RF"])
        },
        "hierarchy_exports": stats,
        "corrected_findings": [{
            "id": "H2.5.3-F01",
            "severity": "recovery_observability",
            "finding": "C5 service VBUS had a physical sense pad while the equivalent RP VBUS observation existed only in the abstract service contract",
            "correction": "one BOM-free TP_RP_SERVICE_VBUS_SENSE copper pad now completes the symmetric data-only USB boundary",
            "evidence": "each service VBUS net now contains exactly its connector, 1-MOhm bleeder and one read-only test pad",
        }],
        "reviewed_nets": reviewed_nets,
        "m1": review_m1(),
        "critical_components": critical_parts,
        "invariants": [
            "C5 and RP service USB-C VBUS cannot power any product rail; each ends at a bleeder and test pad",
            "both FSUSB42MUX paths are board-powered power-off-protected data boundaries",
            "the sole product USB-C is sink-only and USB_C_VBUS_RAW reaches the PD front end, not M1 or a service connector",
            "M1 carries only seven 3V3_MAIN and two AON_SAFE_3V3 source contacts; no raw USB, battery, NVDC or exposed 5-V rail crosses it",
            "U214 and native M5 Unit use independent true-reverse-blocking eFuses and cannot feed their common buck or one another",
            "U214 I2C/SPI/UART/control and native Unit signals stay behind separately enabled isolation devices",
        ],
        "review_boundary": {
            "complete": [
                "paper topology and actual KiCad membership of all three USB VBUS boundaries",
                "identical 80-contact M1 maps and absence of every forbidden raw/high-energy rail",
                "separate expansion branch power nets, exact reverse-blocking eFuses and signal isolators",
            ],
            "deferred": [
                "powered-off leakage/current measurement with one and three USB hosts in H8",
                "external-source and wrong-accessory fault injection in H8",
                "USB edge/eye, hot-plug transients and expansion brownout simulation in H3/H8",
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
        title = "# Изоляция внешних интерфейсов Leshy2"
        nav = "[English](interface-isolation.md) · [На главную](../README.ru.md) · [Питание](power-architecture.ru.md)"
        intro = "Кабель или внешний модуль не может незаметно запитать выключенное устройство либо соседний порт."
        headers = "| Граница | Что проходит | Что аппаратно запрещено |\n|---|---|---|"
        rows = [
            "| USB-C S3 | USB 2.0 + sink-only PD до 30 Вт | source/OTG и обход PD |",
            "| USB-C C5 | только D+/D− через FSUSB42MUX | питание платы через VBUS или data-пины |",
            "| USB-C RP2354B | только D+/D− через FSUSB42MUX | питание платы через VBUS или data-пины |",
            "| M1 между платами | 3V3_MAIN, AON_SAFE_3V3 и сигналы | raw USB, аккумуляторы, NVDC и внешние 5 В |",
            "| U214 Cap / M5 Unit | две независимо разрешаемые защищённые ветви | обратное питание общего buck или соседнего порта |",
        ]
        result = (
            f"## Результат H2.5.3\n\n✅ **Проведено ревью:** {len(manifest['reviewed_nets'])} "
            "ключевых силовых границ проверены по полной KiCad-netlist; обе карты 80-контактного "
            "M1 совпадают. Добавлена отсутствовавшая контрольная площадка RP VBUS без BOM."
        )
        evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV53-no-back-power.json)."
    else:
        title = "# Leshy2 external-interface isolation"
        nav = "[Русский](interface-isolation.ru.md) · [Home](../README.md) · [Power](power-architecture.md)"
        intro = "A cable or accessory cannot silently power an off product or an adjacent port."
        headers = "| Boundary | Allowed path | Hardware prohibition |\n|---|---|---|"
        rows = [
            "| S3 USB-C | USB 2.0 plus sink-only PD up to 30 W | source/OTG and PD bypass |",
            "| C5 USB-C | D+/D− only through FSUSB42MUX | board power through VBUS or data pins |",
            "| RP2354B USB-C | D+/D− only through FSUSB42MUX | board power through VBUS or data pins |",
            "| Interboard M1 | 3V3_MAIN, AON_SAFE_3V3 and signals | raw USB, cells, NVDC and exposed 5 V |",
            "| U214 Cap / M5 Unit | two independently admitted protected branches | feeding the common buck or adjacent port |",
        ]
        result = (
            f"## H2.5.3 result\n\n✅ **Reviewed:** {len(manifest['reviewed_nets'])} critical "
            "power boundaries are checked in complete KiCad netlists and both 80-contact M1 maps "
            "match. The missing RP VBUS observation pad was added with no BOM impact."
        )
        evidence = "[Machine evidence](../hardware/ecad/generated/H2-REV53-no-back-power.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(rows), result, evidence)) + "\n"


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
        print(f"ok: H2.5.3 no-back-power review is current; {len(manifest['reviewed_nets'])} nets reviewed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
