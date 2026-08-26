#!/usr/bin/env python3
"""Join every H5 physical residual to parts, missing data and pass rules."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
H3_RESIDUALS = REPO / "hardware/verification/generated/H3-VRF72-physical-residuals.json"
PHYSICAL_SOURCES = REPO / "hardware/product-design/generated/H1-physical-source-table.json"
MECHANICAL_GATES = REPO / "hardware/product-design/mechanical-evidence-gates.json"
DEVICES = REPO / "hardware/architecture/devices.json"
AM_LW_POD = REPO / "hardware/architecture/am-lw-pod.json"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR01-residual-map.json"
DOC_EN = REPO / "docs/component-evidence-map.md"
DOC_RU = REPO / "docs/component-evidence-map.ru.md"


RESIDUAL_MAP = {
    "H3-PHY-017": {
        "instances": ["display", "display_touch_controller", "display_connector", "display_adapter_plug", "display_panel_connector"],
        "mechanical_gates": ["H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"],
        "missing_data": [
            "standalone order identity and current-lot full FPC outline for the HMX035CTFT-001-marked assembly",
            "received-controller identity/readback and measured VDD/VDDI ramp equality",
        ],
        "sample_specific": True,
    },
    "H3-PHY-024": {
        "instances": ["ir_demod", "ir_carrier", "ir_emitter"],
        "mechanical_gates": [],
        "missing_data": ["received-lot orientation and measured startup, quiet-guard, capture and no-back-power behaviour"],
        "sample_specific": True,
    },
    "H3-PHY-028": {
        "instances": ["pack_gauge"],
        "mechanical_gates": ["H5-MECH-CELL-HOLDER-FIT"],
        "missing_data": ["programmed golden-image readback plus blank, corrupt and exhausted-write fault-injection records"],
        "sample_specific": True,
    },
    "H3-PHY-038": {
        "instances": ["sd"],
        "mechanical_gates": [],
        "missing_data": [
            "exact serial microSD reference-medium MPN is not selected",
            "received-card CMD6 identity, throughput, stall distribution and 512-KiB-buffer trace",
        ],
        "sample_specific": True,
    },
    "H3-PHY-046": {
        "instances": ["u214", "u214_connector"],
        "mechanical_gates": ["H5-MECH-U214-MATING-STACK"],
        "missing_data": [
            "the stock U214 fitted male-post manufacturer/MPN, section, material and plating are not published",
            "measured continuity, insertion/withdrawal force and repeated-cycle retention for the mixed stock-U214/HLE pair",
        ],
        "sample_specific": True,
    },
    "H3-PHY-048": {
        "instances": ["unit_connector"],
        "extra_devices": ["ti_txs0102_dcur"],
        "mechanical_gates": ["H5-MECH-M5-UNIT-MATE"],
        "missing_data": [
            "exact serial cable/accessory set for the admitted I2C, UART, GPIO and 1-Wire profiles is not selected",
            "received cable lengths, pull networks and profile waveforms through TXS0102",
        ],
        "sample_specific": True,
    },
    "H3-PHY-053": {
        "instances": [
            "nrf0", "nrf1", "nrf2",
            "nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper",
            "nrf0_rf_board_connector", "nrf1_rf_board_connector", "nrf2_rf_board_connector",
            "nrf0_external_sma", "nrf1_external_sma", "nrf2_external_sma",
        ],
        "mechanical_gates": ["H5-MECH-NRF-GEN1-FEEDS"],
        "missing_data": [
            "the fitted microcoax receptacle MPN and connector axis on each received E01-ML01IPX lot are not published",
            "three independent assembled-feed loss/match and mating/retention records",
        ],
        "sample_specific": True,
    },
    "H3-PHY-057": {
        "instances": ["receiver", "receiver_amlw_external_sma"],
        "custom_assemblies": ["L2-ANT-AM-LW-001"],
        "mechanical_gates": [],
        "missing_data": ["received edge-SMA and controlled pod constituent identities, physical envelopes and mating records before the H6 routed-capacitance budget and H8 total measurement"],
        "sample_specific": True,
    },
    "H3-PHY-062": {
        "instances": [
            "s3", "c5", "nrf0", "nrf1", "nrf2",
            "s3_rf_jumper", "c5_rf_jumper", "nrf0_rf_jumper", "nrf1_rf_jumper", "nrf2_rf_jumper",
            "s3_rf_board_connector", "c5_rf_board_connector", "nrf0_rf_board_connector", "nrf1_rf_board_connector", "nrf2_rf_board_connector",
        ],
        "mechanical_gates": ["H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"],
        "missing_data": [
            "received 2118651-2 bend, retention and strain behaviour in all five installed paths",
            "received E01 fitted-connector axes before freezing placement",
        ],
        "sample_specific": True,
    },
}


RESIDUAL_MISSING_RU = {
    "H3-PHY-017": "самостоятельный order identity и полный контур FPC текущей партии HMX035CTFT-001; identity/readback контроллера и равенство разгона VDD/VDDI на образце",
    "H3-PHY-024": "ориентацию полученной партии, startup, quiet guard, два канала захвата и отсутствие обратного питания",
    "H3-PHY-028": "readback эталонного образа и fault injection для пустого, повреждённого и исчерпавшего записи экземпляров",
    "H3-PHY-038": "выбрать точный серийный MPN эталонной microSD; измерить CMD6 identity, скорость, задержки и работу 512-КиБ буфера",
    "H3-PHY-046": "непубликуемые MPN/материал/покрытие штырей stock U214; непрерывность, усилия и удержание смешанной пары U214/HLE",
    "H3-PHY-048": "выбрать серийный набор кабелей/аксессуаров для I2C, UART, GPIO и 1-Wire; измерить длины, pull-сети и формы сигналов через TXS0102",
    "H3-PHY-053": "непубликуемый MPN и ось встроенного разъёма партии E01-ML01IPX; отдельно измерить три собранных RF-тракта и удержание",
    "H3-PHY-057": "identity, физические envelopes и mating полученного краевого SMA и составляющих pod до H6 routed-budget и итогового измерения H8",
    "H3-PHY-062": "изгиб, удержание и разгрузку пяти полученных 2118651-2; оси встроенных разъёмов партии E01 до фиксации placement",
}


MECHANICAL_MISSING_RU = {
    "H5-MECH-DISPLAY-TAIL": "контур, толщина, stiffener, клей, изгиб и удержание FPC текущей партии дисплея",
    "H5-MECH-NRF-GEN1-FEEDS": "ось и MPN встроенного разъёма партии E01, fit/retention, изгиб и сквозные RF-потери",
    "H5-MECH-U214-MATING-STACK": "сечение штырей U214, усилия, циклы, винтовое удержание и preload планки",
    "H5-MECH-NAVIGATION-CONTROLS": "доступ через корпус, защита от случайного нажатия, ощущения, герметизация и ресурс",
    "H5-MECH-SA818S-DUAL-LAND-FIT": "identity двух партий, общий 18-land fit, пайку и тепловое поведение SA818S-U/V; conducted RF остаётся H8",
    "H5-MECH-ENCODER-KNOB": "глубина посадки, удержание, ход нажатия, ощущения и итоговая глубина",
    "H5-MECH-DIRECT-PRESS-CONTROLS": "ощущения через корпус, защита от случайного нажатия и ресурс",
    "H5-MECH-RUN-KILL": "доступ сбоку, усилие фиксации, случайное перемещение и ресурс",
    "H5-MECH-M5-UNIT-MATE": "вставка, удержание, разгрузка и циклы полученного Grove-кабеля",
    "H5-MECH-CELL-HOLDER-FIT": "усилие вставки, прижим контактов, полярность, вибрация и термоциклы",
    "H5-MECH-NATIVE-RF-JUMPERS": "реальный радиус изгиба, разгрузка, усилие, удержание и RF-потери после сборки",
    "H5-MECH-DISPLAY-PERFORMANCE": "QSPI/touch, оптика, ток и нагрев подсветки, ресурс flex и повторяемость партий",
    "H5-MECH-ACOUSTIC-PATHS": "акустика корпуса, резонанс, герметизация, feedback, response микрофона и вибрация",
    "H5-MECH-HEADSET-JACK": "допуски выреза, shield/solder-tab fit, усилия, CTIA/TRS, удержание и transient отключения",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def part_from_row(row: dict) -> dict:
    source = row["source"]
    return {
        "identity": row["instance"],
        "kind": "selected_physical_instance",
        "mpn": row["mpn"],
        "role": row["role"],
        "source": source,
    }


def custom_pod_part(pod: dict) -> dict:
    electrical = pod["electrical_design"]
    interface = pod["interface"]
    return {
        "identity": pod["assembly_id"],
        "kind": "controlled_custom_assembly",
        "mpn": pod["assembly_id"],
        "role": pod["role"],
        "constituent_mpns": [
            electrical["core"]["mpn"],
            electrical["winding"]["wire_mpn"],
            interface["connector_mpn"],
            electrical["device_side_components"]["esd_mpn"],
            electrical["device_side_components"]["coupling_capacitor_mpn"],
        ],
        "source": {"document": "controlled AM/LW pod definition", "url": "hardware/architecture/am-lw-pod.json"},
    }


def build() -> dict:
    residual_source = load(H3_RESIDUALS)
    physical_source = load(PHYSICAL_SOURCES)
    mechanical_source = load(MECHANICAL_GATES)
    devices = load(DEVICES)["devices"]
    pod = load(AM_LW_POD)
    rows = {row["instance"]: row for row in physical_source["rows"]}
    gates = {row["id"]: row for row in mechanical_source["gates"]}
    h5_residuals = [row for row in residual_source["registry"] if "H5" in row["closure_stages"]]

    mapped_residuals = []
    for residual in h5_residuals:
        mapping = RESIDUAL_MAP[residual["id"]]
        parts = [part_from_row(rows[name]) for name in mapping["instances"]]
        for key in mapping.get("extra_devices", []):
            device = devices[key]
            parts.append({
                "identity": key,
                "kind": "selected_architecture_device",
                "mpn": device["mpn"],
                "role": device["kind"],
                "source": device["source"],
            })
        for assembly in mapping.get("custom_assemblies", []):
            if assembly != pod["assembly_id"]:
                raise ValueError(f"unknown custom assembly: {assembly}")
            parts.append(custom_pod_part(pod))
        mapped_residuals.append({
            "id": residual["id"],
            "source_phase": residual["source_phase"],
            "source_group": residual["source_group"],
            "requirement": residual["residual"],
            "parts": parts,
            "mechanical_gates": mapping["mechanical_gates"],
            "missing_data": mapping["missing_data"],
            "sample_specific": mapping["sample_specific"],
            "required_artifact": residual["evidence_contracts"]["H5"]["required_artifact"],
            "accepted_pass_rule": residual["evidence_contracts"]["H5"]["pass_rule"],
            "status": "mapped_evidence_open",
        })

    mechanical_gates = []
    for gate in mechanical_source["gates"]:
        affected = [part_from_row(rows[name]) for name in gate["affected_instances"]]
        mechanical_gates.append({
            "id": gate["id"],
            "parts": affected,
            "known_boundary": gate["evidence_boundary"],
            "missing_data": gate["unknown"],
            "accepted_pass_rule": gate["closure"],
            "blocks": gate["blocks"],
            "status": "mapped_evidence_open",
        })

    checks = {
        "exactly_nine_h3_residuals_are_owned_by_h5": len(h5_residuals) == 9,
        "every_h5_residual_has_one_explicit_mapping": {row["id"] for row in h5_residuals} == set(RESIDUAL_MAP),
        "every_mapped_instance_exists_in_the_h1_physical_register": all(name in rows for value in RESIDUAL_MAP.values() for name in value["instances"]),
        "every_referenced_mechanical_gate_exists": all(gate in gates for value in RESIDUAL_MAP.values() for gate in value["mechanical_gates"]),
        "all_fourteen_mechanical_gates_are_joined": len(mechanical_gates) == 14,
        "all_board_fitted_mechanical_gate_parts_have_exact_non_tbd_mpns": all(part["mpn"] and "TBD" not in part["mpn"].upper() for gate in mechanical_gates for part in gate["parts"]),
        "every_residual_has_parts_missing_data_source_and_pass_rule": all(row["parts"] and row["missing_data"] and all(part["source"] for part in row["parts"]) and row["accepted_pass_rule"] for row in mapped_residuals),
        "sample_specific_claims_remain_open": all(row["sample_specific"] and row["status"] == "mapped_evidence_open" for row in mapped_residuals),
        "purchase_layout_and_fabrication_are_not_authorized": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H5.0.1 residual-map checks failed: " + ", ".join(failed))

    return {
        "schema_version": 1,
        "stage": "H5.0.1-R1",
        "status": "reviewed_mapping_only",
        "purpose": "map every H5 residual to selected identities, sources, still-missing data and an inherited pass rule without claiming physical closure",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (H3_RESIDUALS, PHYSICAL_SOURCES, MECHANICAL_GATES, DEVICES, AM_LW_POD)
        },
        "summary": {
            "h3_residuals": len(mapped_residuals),
            "mechanical_gates": len(mechanical_gates),
            "mapped_selected_part_references": sum(len(row["parts"]) for row in mapped_residuals),
            "board_fitted_mechanical_part_references": sum(len(row["parts"]) for row in mechanical_gates),
            "physical_claims_closed": 0,
            "sample_orders_authorized": 0,
            "explicit_research_targets": sum(len(row["missing_data"]) for row in mapped_residuals),
        },
        "checks": checks,
        "residuals": mapped_residuals,
        "mechanical_gates": mechanical_gates,
        "decision_boundary": {
            "accepted_now": "the evidence map, exact selected identities and existing source join",
            "not_accepted": "received-part fit, lot identity, electrical performance or any production qualification",
            "next": "H5.0.2-R1 searches primary manufacturer/distributor evidence and fully documented serial alternatives before any sample proposal",
            "purchase_authorized": False,
            "pcb_placement_and_routing_authorized": False,
            "fabrication_authorized": False,
        },
    }


def short_mpns(row: dict) -> str:
    values = []
    for part in row["parts"]:
        value = part["mpn"]
        if value not in values:
            values.append(value)
    return "; ".join(f"`{value}`" for value in values)


def residual_sections(data: dict, russian: bool) -> str:
    sections = []
    for row in data["residuals"]:
        if russian:
            sections.append(
                f"### `{row['id']}` · `{row['source_group']}`\n\n"
                f"- Выбрано: {short_mpns(row)}.\n"
                f"- Осталось доказать: {RESIDUAL_MISSING_RU[row['id']]}.\n"
                "- Критерий: полученный и однозначно идентифицированный образец напрямую подтверждает пункт; несовпадение повторно открывает связанный результат H1/H2/H3."
            )
        else:
            sections.append(
                f"### `{row['id']}` · `{row['source_group']}`\n\n"
                f"- Selected: {short_mpns(row)}.\n"
                f"- Still to prove: {'; '.join(row['missing_data'])}.\n"
                f"- Pass rule: {row['accepted_pass_rule']}"
            )
    return "\n\n".join(sections)


def render_doc(data: dict, russian: bool) -> str:
    if russian:
        title = "# H5.0.1-R1 · карта evidence компонентов"
        intro = (
            "[English](component-evidence-map.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)\n\n"
            "Карта проведена: все девять H5-residuals и все 14 механических gate’ов связаны с выбранными "
            "серийными деталями, существующими источниками, недостающими данными и заранее принятыми pass rules. "
            "Это **не** закрывает физические проверки и **не** разрешает закупку."
        )
        mech = [f"- `{row['id']}` — {short_mpns(row)}; открыто: {MECHANICAL_MISSING_RU[row['id']]}" for row in data["mechanical_gates"]]
        return f"""{title}

{intro}

```mermaid
flowchart LR
  R["9 H5 residuals"] --> M["✅ точные identities<br/>и источники связаны"]
  G["14 mechanical gates"] --> M
  M --> S["▶️ H5.0.2-R1<br/>документы и серийные замены"]
  S --> P["H5.0.3-R1<br/>только неустранимые образцы"]
```

## Девять физических residuals

{residual_sections(data, True)}

## Четырнадцать механических gate’ов

{chr(10).join(mech)}

## Честная граница результата

- У всех устанавливаемых деталей в механических gate’ах есть точный, не-TBD MPN.
- Не выбранные пока **тестовые** изделия отмечены явно: эталонная microSD и набор M5 Unit/cable для профилей.
- Встроенный разъём полученного `E01-ML01IPX` и штырь установленного на stock `U214` не превращены в выдуманные MPN: производитель их не публикует.
- Реальный fit, retention, RF, timing и lot identity остаются открыты до полученного образца.
- Следующий точный маркер — `H5.0.2-R1`; заказ, PCB placement/routing и fabrication запрещены.

Машинный результат: [`H5-EVR01`](../hardware/verification/generated/H5-EVR01-residual-map.json).
"""
    title = "# H5.0.1-R1 · component-evidence map"
    intro = (
        "[Русский](component-evidence-map.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)\n\n"
        "The mapping review is complete: all nine H5 residuals and all 14 mechanical gates are joined to selected "
        "serial parts, existing sources, missing data and pre-accepted pass rules. This does **not** close a physical "
        "check and does **not** authorize a purchase."
    )
    mech = [f"- `{row['id']}` — {short_mpns(row)}; open: {row['missing_data']}" for row in data["mechanical_gates"]]
    return f"""{title}

{intro}

```mermaid
flowchart LR
  R["9 H5 residuals"] --> M["✅ exact identities<br/>and sources joined"]
  G["14 mechanical gates"] --> M
  M --> S["▶️ H5.0.2-R1<br/>documents and serial alternatives"]
  S --> P["H5.0.3-R1<br/>irreducible samples only"]
```

## Nine physical residuals

{residual_sections(data, False)}

## Fourteen mechanical gates

{chr(10).join(mech)}

## Honest result boundary

- Every board-fitted part in a mechanical gate has an exact non-TBD MPN.
- Test articles not selected yet are explicit: a reference microSD and the M5 Unit/cable profile set.
- The fitted connector in a received `E01-ML01IPX` and the fitted post on a stock `U214` were not assigned invented MPNs; their makers do not publish them.
- Actual fit, retention, RF, timing and lot identity remain open until received-sample evidence exists.
- The next exact marker is `H5.0.2-R1`; purchase, PCB placement/routing and fabrication remain prohibited.

Machine result: [`H5-EVR01`](../hardware/verification/generated/H5-EVR01-residual-map.json).
"""


def outputs() -> dict[Path, str]:
    data = build()
    return {
        OUTPUT: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(data, False),
        DOC_RU: render_doc(data, True),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H5.0.1 artifacts: " + ", ".join(stale))
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    data = build()
    print(f"ok: H5.0.1-R1 mapped {data['summary']['h3_residuals']} residuals and {data['summary']['mechanical_gates']} mechanical gates; physical closures 0")


if __name__ == "__main__":
    main()
