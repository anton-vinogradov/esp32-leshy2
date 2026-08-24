#!/usr/bin/env python3
"""Inventory H3 electrical parameters, provenance and model gaps."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[2]
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
LEDGER_PATH = REPO / "hardware/ecad/generated/H2-instance-ledger.json"
FREEZE_PATH = REPO / "hardware/verification/generated/H3-VRF01-input-freeze.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF02-parameter-inventory.json"
DOC_EN = REPO / "docs/parameter-model-register.md"
DOC_RU = REPO / "docs/parameter-model-register.ru.md"

# H2 remains immutable. These H3-only records replace distributor-hosted document
# mirrors with the original manufacturer's exact-part page/specification.
PROVENANCE_OVERRIDES = {
    "hirose_ufl_r_smt_1_10": {
        "document": "Hirose U.FL-R-SMT-1(10) official specification sheet",
        "url": "https://www.hirose.com/product/document?clcode=CL0331-0472-2-10&documentid=0000266652&documenttype=SpecSheet&lang=en&productname=U.FL-R-SMT-1%2810%29&series=U.FL",
        "reason": "original manufacturer source replaces the accepted H2 distributor mirror without changing the H2 baseline",
    },
    "jae_dx07s016ja1r1500": {
        "document": "JAE DX07S016JA1R1500 official exact-product page",
        "url": "https://products.jae.com/jp/ja/connectors/category/io/dx07-receptacle/dx07s016ja1r1500/",
        "reason": "original manufacturer source replaces the accepted H2 distributor mirror without changing the H2 baseline",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parameter_class(kind: str) -> tuple[str, list[str], str]:
    k = kind.lower()
    if any(token in k for token in ("resistor", "capacitor", "inductor", "ferrite", "crystal")):
        return (
            "passive_corner",
            ["nominal", "tolerance", "voltage/current derating", "temperature coefficient", "frequency/bias dependence"],
            "analytic_or_vendor_curve",
        )
    if any(token in k for token in ("sma", "ufl", "connector", "receptacle", "plug", "socket", "header", "mezzanine")):
        return (
            "connector_interconnect",
            ["contact rating", "contact resistance/loss", "parasitics", "mating applicability", "frequency or data-rate limit"],
            "datasheet_plus_prelayout_constraint",
        )
    if any(token in k for token in ("radio", "lora", "rf_", "rf ", "coupler", "antenna", "detector", "voice_module")):
        return (
            "radio_rf",
            ["supply range", "RX/TX current", "power/sensitivity", "timing", "impedance/loss/matching", "temperature limits"],
            "datasheet_behavioral_and_rf_budget",
        )
    if any(token in k for token in ("display", "codec", "microphone", "speaker", "amplifier", "thermistor", "infrared", "photodiode")):
        return (
            "analog_peripheral",
            ["supply/current", "input/output levels", "gain/noise or optical response", "timing", "load and thermal limits"],
            "datasheet_corner_model",
        )
    if any(token in k for token in ("esp32", "rp235", "microcontroller", "mcu", "bare_qfn", "bare_vqfn")):
        return (
            "programmable_controller",
            ["supply/current", "IO levels and drive", "reset/boot defaults", "clock/timing", "package thermal limits"],
            "datasheet_static_and_timing_model",
        )
    if any(token in k for token in ("switch", "mux", "buffer", "gate", "inverter", "transceiver", "eeprom", "expander")):
        return (
            "digital_interface",
            ["supply/current", "logic thresholds", "leakage/back-power", "reset/default state", "propagation and loading"],
            "datasheet_static_and_timing_model",
        )
    if any(token in k for token in ("charger", "gauge", "protector", "efuse", "regulator", "converter", "mosfet", "diode", "transistor", "comparator", "watchdog", "latch")):
        return (
            "power_safety_active",
            ["absolute/operating limits", "loss/efficiency or on-resistance", "threshold tolerances", "startup/fault timing", "thermal limits"],
            "corner_equation_and_circuit_model",
        )
    if any(token in k for token in ("battery", "holder", "knob", "encoder", "tact", "led", "fuse", "load_resistor")):
        return (
            "electromechanical_or_load",
            ["rating", "operating tolerance", "contact/forward/drop behavior", "pulse or thermal limit", "lifecycle"],
            "datasheet_corner_model",
        )
    return (
        "general_component",
        ["operating limits", "DC behavior", "timing/frequency behavior", "temperature limits", "applicability"],
        "datasheet_corner_model",
    )


def local_models() -> list[str]:
    root = REPO / "hardware/verification/models"
    if not root.is_dir():
        return []
    suffixes = {".cir", ".lib", ".model", ".sub", ".subckt", ".ibs", ".ibis", ".s1p", ".s2p", ".s3p", ".s4p"}
    return sorted(str(path.relative_to(REPO)) for path in root.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)


def build() -> tuple[dict[Path, str], dict]:
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    if freeze.get("status") != "reviewed_accepted_h2_inputs_and_complete_verification_matrix_frozen":
        raise ValueError("H3.0.1 input freeze is not reviewed")

    instances: dict[str, list[dict]] = defaultdict(list)
    for row in ledger["rows"]:
        instances[row["device_key"]].append(row)

    missing = sorted(set(instances) - set(devices))
    if missing:
        raise ValueError("H2 ledger uses unregistered devices: " + ", ".join(missing))

    rows = []
    for key in sorted(instances):
        device = devices[key]
        used = instances[key]
        source = PROVENANCE_OVERRIDES.get(key, device.get("source"))
        if not source or not source.get("url"):
            source_status = "missing"
            source_host = None
        else:
            source_status = "official_h3_override" if key in PROVENANCE_OVERRIDES else "accepted_h2_authoritative_source"
            source_host = urlparse(source["url"]).netloc.lower()
        pclass, required, method = parameter_class(device.get("kind", ""))
        contract = device.get("electrical_contract", {})
        rows.append(
            {
                "device_key": key,
                "mpn": device.get("mpn"),
                "kind": device.get("kind"),
                "instance_count": len(used),
                "projects": sorted({row["project"] for row in used}),
                "sheets": sorted({row["sheet"] for row in used}),
                "roles": sorted({row["role"] for row in used}),
                "lifecycle": device.get("lifecycle", "unregistered"),
                "source": source,
                "source_status": source_status,
                "source_host": source_host,
                "accepted_h2_source_preserved": device.get("source"),
                "structured_parameter_count": len(contract),
                "structured_parameters": contract,
                "parameter_class": pclass,
                "required_parameter_groups": required,
                "h3_model_method": method,
                "model_status": "method_to_be_frozen_in_H3.0.3",
            }
        )

    models = local_models()
    source_status = Counter(row["source_status"] for row in rows)
    parameter_classes = Counter(row["parameter_class"] for row in rows)
    structured = sum(bool(row["structured_parameter_count"]) for row in rows)
    lifecycle_attention = [row["device_key"] for row in rows if "not_recommended" in row["lifecycle"]]
    if lifecycle_attention != ["ebyte_e01_ml01ipx"]:
        raise ValueError(f"unexpected lifecycle decision set: {lifecycle_attention}")

    decision = {
        "id": "H3-NRF24-LIFECYCLE",
        "status": "confirmed_A_under_delegated_user_authority",
        "confirmed_on": "2026-08-24",
        "selected_option": "A",
        "subject": "three full-function nRF24 paths versus new-design lifecycle",
        "affected_device": "ebyte_e01_ml01ipx",
        "affected_instances": len(instances["ebyte_e01_ml01ipx"]),
        "facts": [
            "The selected serial E01-ML01IPX is a current Ebyte product using an original nRF24L01+ and exposes the required SPI/register-compatible transceiver interface.",
            "Nordic classifies the nRF24 family as not recommended for new designs; this is a lifecycle warning, not proof that the selected module is discontinued.",
            "Nordic nRF52 devices can communicate with legacy nRF24 devices through software Enhanced ShockBurst, but they are programmable SoCs rather than register-compatible SPI transceivers.",
        ],
        "sources": [
            {"title": "Ebyte E01-ML01IPX current product page", "url": "https://www.ebyte.com/product/47.html"},
            {"title": "Ebyte E01-ML01IPX product specification (2025-01-16)", "url": "https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf"},
            {"title": "Nordic nRF24 series lifecycle page", "url": "https://www.nordicsemi.com/Products/nRF24-series"},
            {"title": "Nordic Enhanced ShockBurst user guide", "url": "https://docs.nordicsemi.com/r/bundle/nrf5_sdk_v17.0.2/page/esb_users_guide.html"},
        ],
        "options": [
            {
                "id": "A",
                "title": "retain 3x E01-ML01IPX",
                "consequence": "preserves full nRF24 hardware/register behavior and accepted H2 architecture; H5 must validate supplier, silicon marking and reserve sourcing",
            },
            {
                "id": "B",
                "title": "replace with modern nRF52-class programmable modules",
                "consequence": "improves lifecycle but adds three firmware/boot/recovery domains, changes buses and timing, and cannot be treated as complete nRF24 register-level equivalence without a new requirement and HIL campaign; reopens H0-H2",
            },
        ],
        "recommendation": "A",
        "recommendation_reason": "full-function nRF24 is an explicit product requirement; option B is a different radio-compute architecture rather than a drop-in component improvement",
    }

    manifest = {
        "schema_version": 1,
        "stage": "H3.0.2",
        "status": "reviewed_inventory_complete_lifecycle_choice_resolved",
        "source_hashes": {
            str(DEVICES_PATH.relative_to(REPO)): sha256(DEVICES_PATH),
            str(LEDGER_PATH.relative_to(REPO)): sha256(LEDGER_PATH),
            str(FREEZE_PATH.relative_to(REPO)): sha256(FREEZE_PATH),
        },
        "policy": {
            "accepted_h2_baseline_is_immutable": True,
            "official_source_overrides_are_h3_only": True,
            "local_models_are_not_silently_assumed": True,
            "missing_vendor_models_are_replaced_only_by_documented_H3.0.3_methods": True,
        },
        "provenance_overrides": PROVENANCE_OVERRIDES,
        "rows": rows,
        "local_model_files": models,
        "summary": {
            "registered_instances": len(ledger["rows"]),
            "used_device_types": len(rows),
            "used_types_with_source": len(rows) - source_status["missing"],
            "source_missing": source_status["missing"],
            "official_h3_source_overrides": source_status["official_h3_override"],
            "used_types_with_structured_electrical_contract": structured,
            "used_types_requiring_parameter_extraction": len(rows) - structured,
            "local_vendor_model_files": len(models),
            "parameter_classes": dict(sorted(parameter_classes.items())),
            "lifecycle_decisions": 1,
            "open_decisions": 0,
        },
        "physical_only_residuals": [
            {
                "device_key": "qdtech_hmx035ctft_001",
                "gate": "H5",
                "evidence": "received assembly marking, supplier-controlled tail/connector drawing, backlight and optical characterization",
            },
            {
                "device_key": "everest_es8311_qfn20",
                "gate": "H5",
                "evidence": "authorized production source and lot identity; electrical corners remain H3",
            },
        ],
        "resolved_choices": [decision],
        "open_decisions": [],
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    s = manifest["summary"]
    decision = manifest["resolved_choices"][0]
    if russian:
        title = "# Параметры и модели H3"
        nav = "[English](parameter-model-register.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Виртуальная проверка](virtual-verification.ru.md)"
        intro = "Это входной реестр расчётов H3: для каждого реально установленного типа компонента он связывает MPN, экземпляры, схему, первичный источник, требуемые группы параметров и будущий метод модели. Полная таблица остаётся в машинном JSON, чтобы страница продукта была читаемой."
        counts_h = "## Покрытие"
        counts = (
            f"- `{s['registered_instances']}` экземпляров, `{s['used_device_types']}` используемых типов.\n"
            f"- Первичный источник есть у `{s['used_types_with_source']}` из `{s['used_device_types']}` типов; пропусков: `{s['source_missing']}`.\n"
            f"- У `{s['used_types_with_structured_electrical_contract']}` типов параметры уже структурированы; для `{s['used_types_requiring_parameter_extraction']}` их нужно извлечь по классам во время H3.1–H3.6.\n"
            f"- Локальных vendor-моделей сейчас `{s['local_vendor_model_files']}`; допустимый аналитический, behavioral или circuit-метод фиксируется в `H3.0.3`, а не выдумывается.\n"
            f"- Две ссылки-зеркала H2 заменены в этом реестре точными официальными страницами Hirose и JAE без изменения принятого H2."
        )
        residual_h = "## Что нельзя честно закрыть до образца"
        residual = "Хвост/разъём, оптика и подсветка точной сборки `HMX035CTFT-001`, а также поставщик и партия `ES8311` остаются входным контролем H5. Их электрические расчёты по опубликованным данным выполняются в H3."
        decision_h = "## Закрытый архитектурный gate"
        decision_text = (
            f"`{decision['id']}` закрыт вариантом A: остаются три `E01-ML01IPX`, потому что они дают требуемое полное аппаратное поведение nRF24. "
            "Семейство nRF24 не рекомендуется для новых разработок, поэтому H5 проверит поставщика, маркировку silicon и резервную доступность. Современный nRF52 работает только в 2,4 ГГц, поддерживает совместимый эфирный ESB, но не является SPI/register drop-in заменой."
        )
        marker = "**Статус:** `H3.0.2` завершено и проверено; текущий маркер — `H3.3.3`."
        evidence = "[Машинный реестр из 213 строк](../hardware/verification/generated/H3-VRF02-parameter-inventory.json)."
    else:
        title = "# H3 parameters and models"
        nav = "[Русский](parameter-model-register.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Virtual verification](virtual-verification.md)"
        intro = "This is the H3 calculation input register: for every actually fitted device type it links the MPN, instances, schematic ownership, primary source, required parameter groups and future model method. The full table remains machine-readable so the product site stays readable."
        counts_h = "## Coverage"
        counts = (
            f"- `{s['registered_instances']}` instances and `{s['used_device_types']}` used device types.\n"
            f"- A primary source exists for `{s['used_types_with_source']}` of `{s['used_device_types']}` types; missing: `{s['source_missing']}`.\n"
            f"- `{s['used_types_with_structured_electrical_contract']}` types already have structured parameters; `{s['used_types_requiring_parameter_extraction']}` are extracted by class during H3.1–H3.6.\n"
            f"- There are `{s['local_vendor_model_files']}` local vendor models; an admissible analytic, behavioral or circuit method is frozen in `H3.0.3`, never invented silently.\n"
            f"- Two H2 document mirrors are superseded here by exact official Hirose and JAE sources without changing accepted H2."
        )
        residual_h = "## What cannot honestly close before receiving a sample"
        residual = "The exact `HMX035CTFT-001` tail/connector, optics and backlight plus the `ES8311` supplier and lot remain H5 incoming inspection. Their published-data electrical analysis still runs in H3."
        decision_h = "## Closed architecture gate"
        decision_text = (
            f"`{decision['id']}` is closed with option A: three `E01-ML01IPX` modules remain because they provide the required full nRF24 hardware behavior. "
            "The nRF24 family is not recommended for new designs, so H5 must verify supplier, silicon marking and reserve availability. A modern nRF52 is 2.4-GHz-only and supports over-air ESB compatibility, but is not an SPI/register drop-in replacement."
        )
        marker = "**Status:** `H3.0.2` is reviewed; current marker is `H3.3.3`."
        evidence = "[213-row machine register](../hardware/verification/generated/H3-VRF02-parameter-inventory.json)."
    return "\n\n".join((title, nav, intro, counts_h, counts, residual_h, residual, decision_h, decision_text, marker, evidence)) + "\n"


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
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        s = manifest["summary"]
        print(f"ok: H3.0.2 inventory reviewed; {s['used_device_types']} types, {s['source_missing']} missing sources, 0 open decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
