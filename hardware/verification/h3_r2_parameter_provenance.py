#!/usr/bin/env python3
"""Build the exact R2 parameter/model-provenance register."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-parameter-provenance-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
FREEZE = REPO / "hardware/verification/generated/H3-R2-input-freeze.json"
INVENTORY = REPO / "hardware/ecad/generated/H2-R2-native-inventory.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
SYMBOLS = REPO / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json"
DEVICES = REPO / "hardware/architecture/devices.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-parameter-provenance.json"
DOC_EN = REPO / "docs/parameter-model-register.md"
DOC_RU = REPO / "docs/parameter-model-register.ru.md"

SOURCES = (CONTRACT, FREEZE, INVENTORY, INSTANCES, SYMBOLS, DEVICES)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parameter_class(kind: str) -> tuple[str, list[str], str]:
    value = kind.lower()
    if any(token in value for token in ("resistor", "capacitor", "inductor", "ferrite", "crystal")):
        return "passive_corner", ["nominal", "tolerance", "derating", "temperature", "frequency_or_bias"], "analytic_or_vendor_curve"
    if any(token in value for token in ("sma", "ufl", "connector", "receptacle", "plug", "socket", "header", "mezzanine")):
        return "connector_interconnect", ["rating", "contact_loss", "parasitics", "mating", "frequency_or_data_rate"], "datasheet_plus_prelayout_constraint"
    if any(token in value for token in ("radio", "lora", "rf_", "rf ", "coupler", "antenna", "detector", "voice_module")):
        return "radio_rf", ["supply", "rx_tx_current", "power_or_sensitivity", "timing", "impedance_loss_matching", "temperature"], "datasheet_behavioral_and_rf_budget"
    if any(token in value for token in ("display", "codec", "microphone", "speaker", "amplifier", "thermistor", "infrared", "photodiode")):
        return "analog_peripheral", ["supply_current", "io_levels", "gain_noise_or_response", "timing", "load_thermal"], "datasheet_corner_model"
    if any(token in value for token in ("esp32", "rp235", "microcontroller", "mcu", "bare_qfn", "bare_vqfn")):
        return "programmable_controller", ["supply_current", "io_levels_drive", "reset_boot", "clock_timing", "package_thermal"], "datasheet_static_and_timing_model"
    if any(token in value for token in ("switch", "mux", "buffer", "gate", "inverter", "transceiver", "eeprom", "expander")):
        return "digital_interface", ["supply_current", "logic_thresholds", "leakage_backpower", "reset_default", "propagation_loading"], "datasheet_static_and_timing_model"
    if any(token in value for token in ("charger", "gauge", "protector", "efuse", "regulator", "converter", "mosfet", "diode", "transistor", "comparator", "watchdog", "latch")):
        return "power_safety_active", ["limits", "loss_or_efficiency", "threshold_tolerance", "startup_fault_timing", "thermal"], "corner_equation_and_circuit_model"
    if any(token in value for token in ("battery", "holder", "knob", "encoder", "tact", "led", "fuse", "load_resistor")):
        return "electromechanical_or_load", ["rating", "operating_tolerance", "contact_or_drop", "pulse_or_thermal", "lifecycle"], "datasheet_corner_model"
    return "general_component", ["operating_limits", "dc_behavior", "timing_or_frequency", "temperature", "applicability"], "datasheet_corner_model"


def build() -> dict:
    contract = load(CONTRACT)
    plan = load(PLAN)
    freeze = load(FREEZE)
    inventory = load(INVENTORY)
    instance_ledger = load(INSTANCES)
    symbol_ledger = load(SYMBOLS)
    devices = load(DEVICES)["devices"]
    errors: list[str] = []

    statuses = {row.get("id"): row.get("status") for row in plan.get("substeps", [])}
    progress_valid = (
        plan.get("current_substep") == "H3-R2.0.2" and statuses.get("H3-R2.0.2") == "current"
    ) or (
        plan.get("current_substep") == "H3-R2.0.3" and statuses.get("H3-R2.0.2") == "reviewed"
    )
    if not progress_valid:
        errors.append("H3 plan does not expose current or reviewed H3-R2.0.2")
    if freeze.get("status") != "pass" or freeze.get("marker") != "H3-R2.0.1":
        errors.append("reviewed H3-R2.0.1 input freeze is not passing")

    groups = inventory.get("component_groups", [])
    symbol_groups = {row["device_id"]: row for row in symbol_ledger.get("groups", [])}
    instance_groups: dict[str, list[dict]] = defaultdict(list)
    for row in instance_ledger.get("rows", []):
        instance_groups[row["device_id"]].append(row)
    sheet_owner = {
        sheet: workstream["id"]
        for workstream in freeze.get("workstreams", [])
        for sheet in workstream.get("sheets", [])
    }
    overrides = contract.get("manufacturer_source_overrides", {})
    factory_only = contract.get("factory_catalog_only_parameter_sources", {})
    non_pcba_owners = contract.get("non_pcba_workstream_owners", {})

    rows: list[dict] = []
    for group in sorted(groups, key=lambda row: row["device_id"]):
        device_id = group["device_id"]
        device = devices.get(device_id)
        if device is None:
            errors.append(f"unregistered device: {device_id}")
            continue
        instances = instance_groups.get(device_id, [])
        is_board = group.get("ecad_disposition") == "schematic_component_group"
        source = overrides.get(device_id, device.get("source"))
        source_url = (source or {}).get("url")
        source_checked = (source or {}).get("checked")
        if not source_url:
            errors.append(f"missing source URL: {device_id}")
        if not source_checked:
            errors.append(f"missing source check date: {device_id}")
        if device_id in factory_only:
            source_tier = "exact_factory_catalog_identity_parameter_gap"
        elif device_id in overrides:
            source_tier = "manufacturer_primary_h3_override"
        else:
            source_tier = "manufacturer_primary_accepted_h2"
        if source_url and "jlcpcb.com" in urlparse(source_url).netloc.lower() and device_id not in factory_only:
            errors.append(f"factory catalog source is not classified or overridden: {device_id}")

        sheets = sorted({row["sheet"] for row in instances})
        owners = sorted({sheet_owner[sheet] for sheet in sheets if sheet in sheet_owner})
        if not owners:
            owners = sorted(non_pcba_owners.get(device_id, []))
        if not owners:
            errors.append(f"no H3 workstream owner: {device_id}")
        if is_board and len(instances) != group.get("quantity_per_product"):
            errors.append(f"instance quantity mismatch: {device_id}")
        if is_board and device_id not in symbol_groups:
            errors.append(f"missing symbol/footprint provenance: {device_id}")

        pclass, required, candidate = parameter_class(device.get("kind", ""))
        electrical = device.get("electrical_contract", {})
        gap = factory_only.get(device_id)
        rows.append({
            "device_id": device_id,
            "mpn": group.get("mpn"),
            "manufacturer": device.get("manufacturer"),
            "kind": device.get("kind"),
            "role": group.get("role"),
            "scope": group.get("scope"),
            "ecad_disposition": group.get("ecad_disposition"),
            "quantity_per_product": group.get("quantity_per_product"),
            "fitted_board_instance_count": len(instances),
            "projects": sorted({row["project"] for row in instances}),
            "sheets": sheets,
            "references": sorted(row["reference"] for row in instances),
            "lifecycle": group.get("lifecycle"),
            "jlcpcb_part_number": group.get("jlcpcb_part_number"),
            "source": source,
            "source_tier": source_tier,
            "accepted_h2_source_preserved": device.get("source"),
            "source_host": urlparse(source_url).netloc.lower() if source_url else None,
            "parameter_class": pclass,
            "required_parameter_groups": required,
            "structured_parameters": electrical,
            "structured_parameter_count": len(electrical),
            "parameter_state": "structured_seed_present" if electrical else "explicit_extraction_queue",
            "model_method_candidate": candidate,
            "model_method_state": "candidate_pending_H3-R2.0.3",
            "owner_workstreams": owners,
            "factory_catalog_parameter_gap": gap,
            "symbol_contact_map_sha256": symbol_groups.get(device_id, {}).get("contact_map_sha256"),
            "symbol_electrical_contract_sha256": symbol_groups.get(device_id, {}).get("electrical_contract_sha256"),
        })

    expected = contract.get("expected", {})
    board_groups = sum(row["ecad_disposition"] == "schematic_component_group" for row in rows)
    fitted = sum(row["fitted_board_instance_count"] for row in rows)
    actual = {
        "component_groups": len(rows),
        "board_component_groups": board_groups,
        "explicit_non_pcba_groups": len(rows) - board_groups,
        "fitted_board_instances": fitted,
        "source_missing": sum(not row["source"].get("url") for row in rows if row.get("source")),
        "factory_catalog_only_parameter_sources": sum(row["source_tier"] == "exact_factory_catalog_identity_parameter_gap" for row in rows),
    }
    if actual != expected:
        errors.append(f"R2 parameter-register counts differ: {actual} != {expected}")
    if len({row["device_id"] for row in rows}) != len(rows):
        errors.append("duplicate component-group identity")
    if set(factory_only) != {row["device_id"] for row in rows if row["factory_catalog_parameter_gap"]}:
        errors.append("factory-catalog gap set differs from contract")

    class_counts = Counter(row["parameter_class"] for row in rows)
    class_structured = Counter(row["parameter_class"] for row in rows if row["structured_parameter_count"])
    sources = {str(path.relative_to(REPO)): digest(path) for path in SOURCES}
    payload = json.dumps({"sources": sources, "rows": rows}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "artifact": "H3-R2-parameter-provenance",
        "marker": "H3-R2.0.2",
        "status": "pass" if not errors else "fail",
        "accepted_input": "H3-R2.0.1",
        "input_freeze_sha256": freeze.get("freeze_sha256"),
        "register_sha256": hashlib.sha256(payload).hexdigest(),
        "source_sha256": sources,
        "policy": contract.get("policy", {}),
        "summary": {
            **actual,
            "groups_with_structured_parameter_seeds": sum(bool(row["structured_parameter_count"]) for row in rows),
            "groups_in_explicit_parameter_extraction_queue": sum(not row["structured_parameter_count"] for row in rows),
            "manufacturer_primary_sources": sum(row["source_tier"].startswith("manufacturer_primary") for row in rows),
            "model_method_candidates": len(rows),
            "owned_component_groups": sum(bool(row["owner_workstreams"]) for row in rows),
            "parameter_classes": dict(sorted(class_counts.items())),
            "structured_by_parameter_class": dict(sorted(class_structured.items())),
            "bounded_source_findings": len(factory_only),
            "open_decisions": 0,
            "errors": len(errors),
        },
        "manufacturer_source_overrides": overrides,
        "bounded_source_findings": [
            {"device_id": device_id, **finding}
            for device_id, finding in sorted(factory_only.items())
        ],
        "rows": rows,
        "authorization": {
            "advance_to_method_freeze": not errors,
            "placement_or_routing": False,
            "purchasing": False,
            "fabrication": False,
        },
        "errors": errors,
    }


def render_json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def render_doc(result: dict, ru: bool) -> str:
    summary = result["summary"]
    classes = summary["parameter_classes"]
    structured = summary["structured_by_parameter_class"]
    if ru:
        title = "# Параметры и модели R2"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](parameter-model-register.md)"
        intro = "Статус `H3-R2.0.2`: ✅ reviewed. Это точный реестр входов будущих расчётов для принятой R2-схемы, а не старой R1: каждый тип компонента связан с MPN, экземплярами, листами, источником параметров, классом модели и владельцем проверки."
        coverage = "## Покрытие"
        bullets = (
            f"- `{summary['component_groups']}` групп компонентов: `{summary['board_component_groups']}` на платах и `{summary['explicit_non_pcba_groups']}` явно внешних/финально устанавливаемых.\n"
            f"- `{summary['fitted_board_instances']}` устанавливаемых позиций; у всех `{summary['owned_component_groups']}` групп есть владелец H3.\n"
            f"- У `{summary['groups_with_structured_parameter_seeds']}` групп уже есть структурированные параметры; `{summary['groups_in_explicit_parameter_extraction_queue']}` стоят в явной очереди извлечения, а не получают выдуманные значения.\n"
            f"- Назначены `{summary['model_method_candidates']}` кандидата метода; точный метод, tolerance и applicability фиксирует следующий шаг `H3-R2.0.3`."
        )
        table_title = "## Классы моделей"
        headers = ("Класс", "Группы", "Со structured seed", "Требуют извлечения")
        findings_title = "## Ограниченные находки источников"
        findings = "Для `CS0805-R27J-S` (`C108271`) и `3225-27.00-10-10-10/A` (`C518151`) точная идентичность и фабричный маршрут подтверждены JLCPCB, но полной manufacturer-controlled модели corners пока нет. Они остаются входами `H3-R2.3`; недостающие параметры нельзя молча предполагать. Это не запрос на замену компонента."
        boundary = "Placement, routing, закупка и печать не разрешены. Следующий шаг — воспроизводимо зафиксировать методы, допуски и pass/fail rules."
        machine = "[Машинный реестр из 242 строк](../hardware/verification/generated/H3-R2-parameter-provenance.json). Исторический R1-реестр сохранён отдельно как `H3-VRF02`, но не является authority R2."
    else:
        title = "# R2 parameters and models"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](parameter-model-register.ru.md)"
        intro = "`H3-R2.0.2` is reviewed. This is the exact future-calculation input register for the accepted R2 circuit, not the old R1 topology: every component type is bound to its MPN, instances, sheets, parameter source, model class and verification owner."
        coverage = "## Coverage"
        bullets = (
            f"- `{summary['component_groups']}` component groups: `{summary['board_component_groups']}` on-board and `{summary['explicit_non_pcba_groups']}` explicitly external/final-installed.\n"
            f"- `{summary['fitted_board_instances']}` fitted positions; all `{summary['owned_component_groups']}` groups have an H3 owner.\n"
            f"- `{summary['groups_with_structured_parameter_seeds']}` groups already contain structured parameters; `{summary['groups_in_explicit_parameter_extraction_queue']}` are in an explicit extraction queue rather than receiving invented values.\n"
            f"- `{summary['model_method_candidates']}` method candidates are assigned; exact methods, tolerances and applicability are frozen next in `H3-R2.0.3`."
        )
        table_title = "## Model classes"
        headers = ("Class", "Groups", "With structured seed", "Need extraction")
        findings_title = "## Bounded source findings"
        findings = "For `CS0805-R27J-S` (`C108271`) and `3225-27.00-10-10-10/A` (`C518151`), JLCPCB proves exact identity and the factory route, but a complete manufacturer-controlled corner model is not yet bound. They remain `H3-R2.3` inputs; missing parameters may not be silently assumed. This is not a component-replacement request."
        boundary = "Placement, routing, purchasing and fabrication remain forbidden. The next step reproducibly freezes methods, tolerances and pass/fail rules."
        machine = "[242-row machine register](../hardware/verification/generated/H3-R2-parameter-provenance.json). The historical R1 `H3-VRF02` register remains archived evidence and is not R2 authority."
    table = "\n".join(
        f"| `{name}` | {count} | {structured.get(name, 0)} | {count - structured.get(name, 0)} |"
        for name, count in sorted(classes.items())
    )
    return "\n\n".join((
        title, nav, intro, coverage, bullets, table_title,
        "| " + " | ".join(headers) + " |\n|---|---:|---:|---:|\n" + table,
        findings_title, findings, "> " + boundary, machine,
    )) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    outputs = {OUTPUT: render_json(result), DOC_EN: render_doc(result, False), DOC_RU: render_doc(result, True)}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(
            f"wrote H3-R2.0.2 register {result['register_sha256'][:12]}: "
            f"{result['summary']['component_groups']} groups, "
            f"{result['summary']['fitted_board_instances']} fitted positions"
        )
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: exact R2 parameter/model provenance is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
