#!/usr/bin/env python3
"""Generate the H5 PCBA-platform baseline and critical-component spot check."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
BOM = REPO / "hardware/architecture/generated/G2F-3I-target-bom.csv"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json"
UPLOAD = REPO / "hardware/verification/generated/H5-EVR04-jlcpcb-bom-upload.csv"
DOC_EN = REPO / "docs/manufacturing-platform.md"
DOC_RU = REPO / "docs/manufacturing-platform.ru.md"
CHECKED_ON = "2026-08-25"
UPLOAD_AUTHORIZED_ON = "2026-08-25"


SOURCES = {
    "jlc_capabilities": "https://jlcpcb.com/capabilities/pcb-assembly-capabilities",
    "jlc_sourcing": "https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction",
    "jlc_private_library": "https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb",
    "jlc_own_parts": "https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order",
    "jlc_api": "https://jlcpcb.com/help/article/jlcpcb-online-api-available-now",
    "pcbway_capabilities": "https://www.pcbway.com/assembly-capabilities.html",
    "seeed_pcba": "https://www.seeedstudio.com/pcb-assembly.html",
}


PLATFORMS = [
    {
        "id": "jlcpcb-standard-pcba",
        "role": "reference",
        "reason": "public assembly-parts library with visible MPN, JLC number, stock, assembly class and price; private pre-order, global-sourcing and consignment paths; Standard PCBA covers the accepted board class",
        "fit": {
            "double_sided_smt_tht": True,
            "mixed_technology": True,
            "fine_pitch_bga_qfn": True,
            "special_stackup": True,
            "spi_aoi_xray": True,
            "public_machine_readable_parts_path": True,
            "final_box_build_proven": False,
        },
    },
    {
        "id": "pcbway-turnkey",
        "role": "fallback-quote",
        "reason": "turnkey, combo and consigned sourcing plus functional test and box-build options, but component availability is approval/quote driven rather than a public stock contract",
        "fit": {"double_sided_smt_tht": True, "box_build_claimed": True, "public_machine_readable_parts_path": False},
    },
    {
        "id": "seeed-fusion",
        "role": "second-source-quote",
        "reason": "turnkey PCBA, public OPL and distributor-linked sourcing, but a smaller public local library and no selected advantage over JLCPCB for this BOM",
        "fit": {"double_sided_smt_tht": True, "public_local_parts_library": True, "public_machine_readable_parts_path": False},
    },
]


TIERS = [
    {"id": "J0", "name": "public-stock exact", "rule": "exact accepted MPN and JLC number are publicly in stock for Standard PCBA; stock is rechecked at every freeze and order"},
    {"id": "J1", "name": "approved in-stock alternate", "rule": "only a prequalified same-function alternate inside the owning substitution class; never a factory-selected silent substitute"},
    {"id": "J2", "name": "private pre-order stock", "rule": "exact MPN is bought into My Parts Lib before PCBA; public stock may supplement only where JLC rules permit"},
    {"id": "J3", "name": "global sourcing or consignment", "rule": "exact identity is sourced or supplied into the private library and must be received before assembly"},
    {"id": "J4", "name": "final/manual assembly", "rule": "removable accessories, cells, antennas and parts outside the PCBA boundary are installed and tested after board assembly"},
]


SPOT_CHECKS = [
    {"device_id": "esp32_s3_wroom_1u_n16r8", "mpn": "ESP32-S3-WROOM-1U-N16R8", "jlc": "C3013946", "tier": "J0", "stock": 14529, "pcba": "Standard only; X-ray required", "source": "https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946", "finding": "exact selected module is directly assembleable"},
    {"device_id": "esp32_c5_wroom_1u_n8r8", "mpn": "ESP32-C5-WROOM-1U-N8R8-V1.2", "jlc": "C54951858", "tier": "J0", "stock": 547, "pcba": "Extended SMT", "source": "https://jlcpcb.com/partdetail/C54951858", "finding": "current explicit V1.2 stock matches the architecture revision floor; BOM spelling must be normalized before release"},
    {"device_id": "cc1101rgpr", "mpn": "CC1101RGPR", "jlc": "C29953", "tier": "J0", "stock": 14194, "pcba": "Economic and Standard", "source": "https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953", "finding": "exact selected transceiver is directly assembleable"},
    {"device_id": "everest_es8311_qfn20", "mpn": "ES8311", "jlc": "C962342", "tier": "J0", "stock": 96905, "pcba": "Economic and Standard; fixture; MSL3", "source": "https://jlcpcb.com/partdetail/1044199-ES8311/C962342", "finding": "exact selected codec is directly assembleable"},
    {"device_id": "adi_max17320_g20_t", "mpn": "MAX17320G20+ / selected order suffix +T", "jlc": "C7457894", "tier": "J0", "stock": 13, "pcba": "Extended SMT", "source": "https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894", "finding": "functional identity is present but packaging/order-suffix equivalence and low stock require confirmation or J2 reservation"},
    {"device_id": "rp2354b_a4", "mpn": "SC1512-A4", "jlc": "C52763783", "tier": "J2", "stock": 0, "pcba": "SMT; fixture; Economic and Standard", "source": "https://jlcpcb.com/partdetail/RaspberryPi-SC1512A4/C52763783", "finding": "listed and assembleable, but not public-stock; reserve by pre-order or consign exact parts"},
    {"device_id": "ti_mspm0c1106_sdgs20r", "mpn": "MSPM0C1106SDGS20R", "jlc": "C52995805", "tier": "J2", "stock": 0, "pcba": "Extended SMT", "source": "https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805", "finding": "listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation"},
    {"device_id": "ebyte_e01_ml01ipx", "mpn": "E01-ML01IPX", "jlc": None, "tier": "J3", "stock": 0, "pcba": "not found in public library", "source": "https://jlcpcb.com/parts/componentSearch?searchTxt=E01-ML01IPX", "finding": "retain exact module only through new-part/global-sourcing/consignment until a function-preserving stocked module is qualified"},
    {"device_id": "nicerf_sa518_v11", "mpn": "NiceRF SA518", "jlc": None, "tier": "J3", "stock": 0, "pcba": "not found in public library", "source": "https://jlcpcb.com/parts/componentSearch?searchTxt=SA518", "finding": "route the exact module and its supplier questions through JLC sourcing first; direct manufacturer contact is no longer the first action"},
    {"device_id": "qdtech_hmx035ctft_001", "mpn": "HMX035CTFT-001", "jlc": None, "tier": "J4", "stock": 0, "pcba": "display/flex belongs to final assembly", "source": "https://jlcpcb.com/parts/componentSearch?searchTxt=HMX035CTFT-001", "finding": "keep replaceable display-adapter architecture; the display is not treated as an ordinary line-loaded SMT part"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    with BOM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["device_id"]: row for row in rows}
    missing = [row["device_id"] for row in SPOT_CHECKS if row["device_id"] not in by_id]
    checks = {
        "reference_is_standard_pcba": PLATFORMS[0]["id"] == "jlcpcb-standard-pcba",
        "target_bom_has_209_exact_lines": len(rows) == 209,
        "every_spot_check_is_in_target_bom": not missing,
        "every_spot_check_has_a_source_and_tier": all(row["source"] and row["tier"] in {tier["id"] for tier in TIERS} for row in SPOT_CHECKS),
        "no_stock_snapshot_claims_permanent_availability": True,
        "no_component_replacement_is_authorized": True,
        "minimum_bom_upload_authorized_by_user": True,
        "minimum_bom_not_yet_transmitted": True,
        "no_order_or_layout_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed": [key for key, value in checks.items() if not value], "missing": missing})
    return {
        "schema_version": 1,
        "artifact": "H5-EVR04",
        "stage": "H5.0.3",
        "status": "reference_selected_full_bom_audit_open",
        "checked_on": CHECKED_ON,
        "input": {"path": str(BOM.relative_to(REPO)), "sha256": sha256(BOM), "exact_lines": len(rows)},
        "decision": {
            "reference_platform": "JLCPCB Standard PCBA",
            "fallback_platform": "PCBWay turnkey/box-build quote",
            "second_source_quote": "Seeed Fusion",
            "exclusive_lock_in": False,
            "reason": "JLCPCB gives the strongest public, repeatable component-selection surface while retaining exact-part pre-order, global sourcing and consignment paths.",
        },
        "platforms": PLATFORMS,
        "availability_tiers": TIERS,
        "assembly_boundary": {
            "inside_pcba": ["both Leshy2 rigid boards", "all ordinary SMT/THT parts accepted by Standard PCBA", "board connectors and soldered RF boundaries when their exact assembly rule is accepted"],
            "after_pcba": ["display/flex final mating", "removable U214 Cap and M5 Units", "cells", "external antennas", "knob and any enclosure-only hardware not accepted in the assembly quote", "final sandwich/box integration"],
        },
        "bom_tool_upload": {
            "path": str(UPLOAD.relative_to(REPO)),
            "sha256": hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
            "columns": ["Manufacturer Part Number", "Quantity"],
            "exact_lines": len(rows),
            "contains_only_authorized_fields": True,
            "authorized_on": UPLOAD_AUTHORIZED_ON,
            "transmitted": False,
            "blocker": "user sign-in to the JLCPCB account; credentials and CAPTCHA remain user-only",
        },
        "critical_spot_checks": SPOT_CHECKS,
        "summary": {
            "target_bom_lines": len(rows),
            "critical_lines_spot_checked": len(SPOT_CHECKS),
            "public_stock_exact_or_revision_explicit": sum(row["tier"] == "J0" for row in SPOT_CHECKS),
            "preorder_reservation": sum(row["tier"] == "J2" for row in SPOT_CHECKS),
            "global_sourcing_or_consignment": sum(row["tier"] == "J3" for row in SPOT_CHECKS),
            "post_pcba_final_assembly": sum(row["tier"] == "J4" for row in SPOT_CHECKS),
            "full_bom_lines_pending_mapping": len(rows) - len(SPOT_CHECKS),
        },
        "policy": {
            "selection_time": "prefer J0; use J1 only after owner-level equivalence checks; use J2/J3 for function-critical identities that cannot be replaced without degradation",
            "freeze_time": "every soldered line must have an exact JLC number or a received private-stock route, assembly type and attrition quantity",
            "order_time": "recheck stock and price; a shortage reopens sourcing, never authorizes a silent substitute",
            "continuity": "permanent availability is approximated by qualified alternates or reserved private inventory, never claimed from one stock snapshot",
        },
        "next": {
            "local": "map all 209 BOM lines to J0-J4 and identify function-neutral JLC-stock substitutions",
            "external_authority_later": "the minimum MPN-and-quantity upload is authorized; Parts API application, sourcing request and purchase still require separate explicit authority",
            "forbidden": ["purchase", "component replacement", "Parts API application", "sourcing request", "KiCad placement/routing", "fabrication"],
        },
        "sources": SOURCES,
        "checks": checks,
    }


def table(data: dict, russian: bool) -> str:
    lines = ["| MPN | JLC | Сейчас | Маршрут |" if russian else "| MPN | JLC | Current evidence | Route |", "|---|---:|---|---|"]
    for row in data["critical_spot_checks"]:
        stock = f"stock {row['stock']}" if row["stock"] else row["pcba"]
        lines.append(f"| [`{row['mpn']}`]({row['source']}) | `{row['jlc'] or '—'}` | {stock} | `{row['tier']}` · {row['finding']} |")
    return "\n".join(lines)


def render(data: dict, russian: bool) -> str:
    summary = data["summary"]
    if russian:
        return f"""# Производственная платформа Leshy2

[English](manufacturing-platform.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

## Базовая линия

**Рабочий reference — JLCPCB Standard PCBA.** Это не эксклюзивная привязка и не разрешение заказа. Standard выбран из-за публичной assembly-библиотеки со stock/JLC-number, двухстороннего SMT+THT, fine-pitch/BGA/QFN, специального stack-up и SPI/AOI/X-ray. [Официальные capabilities]({SOURCES['jlc_capabilities']}) и [варианты sourcing]({SOURCES['jlc_sourcing']}).

PCBWay остаётся fallback для ручного turnkey/box-build quote, Seeed Fusion — второй производственный quote. Их supplier availability хуже подходит как автоматически проверяемый источник выбора MPN.

```mermaid
flowchart TD
  M["Новый MPN"] --> J0["J0 · exact JLC stock"]
  J0 -->|нет| J1["J1 · квалифицированная замена"]
  J1 -->|нет без деградации| J2["J2 · private pre-order"]
  J2 -->|нет| J3["J3 · global/consign"]
  J3 --> J4["J4 · final/manual assembly"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4 --> F
  F --> R["повторная stock-проверка перед заказом"]
```

## Что значит «доступно всегда»

Ни одна площадка не гарантирует вечный публичный остаток. Для Leshy2 это означает: обычные детали выбираются из JLC stock или имеют заранее квалифицированные замены; уникальные функциональные MPN резервируются в private library через [pre-order]({SOURCES['jlc_private_library']}) или поступают через global sourcing/consignment. Недостаток stock никогда не разрешает фабрике молчаливую замену.

## Первая проверка критических деталей

Проверено `{summary['critical_lines_spot_checked']}` из `{summary['target_bom_lines']}` exact BOM lines; это старт полного аудита, а не полный assembly quote.

{table(data, True)}

## Граница сборки

JLCPCB собирает обе платы и принятые SMT/THT-компоненты. Дисплейный flex, U214/M5, аккумуляторы, внешние антенны и финальная сборка «бутерброда» остаются post-PCBA operations, пока отдельный box-build quote не докажет обратное.

## Текущий результат

- JLCPCB Standard PCBA принят как рабочий reference без lock-in.
- Полный mapping ещё открыт: `{summary['full_bom_lines_pending_mapping']}` строк.
- Прямой RFQ NiceRF отложен: сначала проверяется JLC global sourcing/new-part route.
- Минимальный BOM upload (только MPN и количество) разрешён, файл подготовлен, но ещё не передан: требуется пользовательский вход в JLCPCB. API application, sourcing request, покупка, замены, KiCad layout и fabrication не разрешены.

Машинный результат: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json).
"""
    return f"""# Leshy2 manufacturing platform

[Русский](manufacturing-platform.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

## Reference line

**The working reference is JLCPCB Standard PCBA.** This is neither exclusive lock-in nor order authorization. Standard was selected for its public stock/JLC-number assembly library, double-sided SMT+THT, fine-pitch/BGA/QFN, special stackups and SPI/AOI/X-ray. See the official [assembly capabilities]({SOURCES['jlc_capabilities']}) and [parts-sourcing paths]({SOURCES['jlc_sourcing']}).

PCBWay remains the manual turnkey/box-build quote fallback; Seeed Fusion remains a second manufacturing quote. Their supplier availability is less suitable as a repeatable machine-checkable MPN-selection source.

```mermaid
flowchart TD
  M["New MPN"] --> J0["J0 · exact JLC stock"]
  J0 -->|no| J1["J1 · qualified alternate"]
  J1 -->|no non-degrading alternate| J2["J2 · private pre-order"]
  J2 -->|no| J3["J3 · global/consign"]
  J3 --> J4["J4 · final/manual assembly"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4 --> F
  F --> R["stock recheck before every order"]
```

## Meaning of “always available”

No platform guarantees perpetual public stock. Leshy2 therefore selects ordinary parts from JLC stock or with prequalified alternates; unique functional identities are reserved in the [private parts library]({SOURCES['jlc_private_library']}) or received through global sourcing/consignment. A shortage never permits a silent factory substitution.

## First critical-part check

`{summary['critical_lines_spot_checked']}` of `{summary['target_bom_lines']}` exact BOM lines are spot-checked. This starts the full audit; it is not a complete assembly quote.

{table(data, False)}

## Assembly boundary

JLCPCB assembles both boards and accepted SMT/THT parts. Display flex mating, U214/M5, cells, external antennas and final sandwich integration remain post-PCBA operations until a separate box-build quote proves otherwise.

## Current result

- JLCPCB Standard PCBA is the working reference without lock-in.
- Full mapping remains open for `{summary['full_bom_lines_pending_mapping']}` lines.
- Direct NiceRF contact is deferred while the JLC global-sourcing/new-part route is checked first.
- The minimum BOM upload (MPN and quantity only) is authorized and prepared but not yet transmitted because user sign-in is required. API application, sourcing request, purchase, replacements, KiCad layout and fabrication are not authorized.

Machine result: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json).
"""


def render_upload() -> str:
    """Return the minimum disclosure accepted for the JLCPCB BOM Tool."""
    with BOM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=["Manufacturer Part Number", "Quantity"],
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "Manufacturer Part Number": row["mpn"],
                "Quantity": row["quantity"],
            }
        )
    return stream.getvalue()


def outputs() -> dict[Path, str]:
    data = build()
    return {
        OUTPUT: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        UPLOAD: render_upload(),
        DOC_EN: render(data, False),
        DOC_RU: render(data, True),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, value in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != value]
        if stale:
            raise SystemExit("stale H5 PCBA-platform artifacts: " + ", ".join(stale))
    else:
        for path, value in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    data = build()
    print(f"ok: {data['decision']['reference_platform']}; {data['summary']['critical_lines_spot_checked']}/{data['summary']['target_bom_lines']} critical/BOM lines mapped; no order or replacement authorized")


if __name__ == "__main__":
    main()
