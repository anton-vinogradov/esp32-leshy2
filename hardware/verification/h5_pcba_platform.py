#!/usr/bin/env python3
"""Generate the H5 PCBA-platform baseline and critical-component spot check."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
BOM = REPO / "hardware/architecture/generated/G2F-3I-target-bom.csv"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json"
UPLOAD = REPO / "hardware/verification/generated/H5-EVR04-jlcpcb-bom-upload.csv"
CAPTURE = REPO / "hardware/verification/jlcpcb-bom-tool-capture-2026-08-25-compact.json"
MATCH_OUTPUT = REPO / "hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json"
DOC_EN = REPO / "docs/manufacturing-platform.md"
DOC_RU = REPO / "docs/manufacturing-platform.ru.md"
CHECKED_ON = "2026-08-25"
UPLOAD_AUTHORIZED_ON = "2026-08-25"


# The architecture register intentionally keeps the manufacturer beside the
# orderable identity for human readability.  JLCPCB's BOM matcher, however,
# treats Comment as the lookup token and expects the bare manufacturer part
# number.  Keep the transformation explicit and reviewable instead of growing
# a second hand-maintained BOM.
MPN_VENDOR_PREFIXES = tuple(
    sorted(
        {
            "Abracon",
            "Alps Alpine",
            "Analog Devices",
            "Bourns",
            "C&K",
            "Davies Molding",
            "Diodes Incorporated",
            "Ebyte",
            "Everest Semiconductor",
            "GCT",
            "Hirose",
            "Infineon",
            "JAE",
            "KEMET",
            "KYOCERA AVX",
            "Keystone Electronics",
            "Littelfuse",
            "M5Stack",
            "Murata",
            "Nexperia",
            "NiceRF",
            "OMRON",
            "PUI Audio",
            "Panasonic",
            "Same Sky",
            "Samtec",
            "Seiko Epson",
            "Sunlord",
            "TDK",
            "TE Connectivity",
            "TTM Technologies",
            "Texas Instruments",
            "Vishay",
            "XTAR",
            "Yageo",
            "onsemi",
        },
        key=len,
        reverse=True,
    )
)


def bare_mpn(value: str) -> str:
    """Return the orderable identity without the register's maker annotation."""
    normalized = value.strip()
    if normalized == "HMX035CTFT-001 (QDtech schematic assembly marking)":
        return "HMX035CTFT-001"
    for prefix in MPN_VENDOR_PREFIXES:
        marker = prefix + " "
        if normalized.startswith(marker):
            return normalized[len(marker) :]
    return normalized


SOURCES = {
    "jlc_capabilities": "https://jlcpcb.com/capabilities/pcb-assembly-capabilities",
    "jlc_sourcing": "https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction",
    "jlc_private_library": "https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb",
    "jlc_own_parts": "https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order",
    "jlc_api": "https://jlcpcb.com/help/article/jlcpcb-online-api-available-now",
    "jlc_bom_format": "https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly",
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


def semantic_mpn(value: str) -> str:
    """Normalize punctuation/case only; do not collapse order-code suffixes."""
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def capture_row_index(designator: str) -> int:
    first = designator.split(",", 1)[0]
    if not re.fullmatch(r"X\d{6}", first):
        raise ValueError(f"unexpected synthetic designator: {first}")
    return int(first[1:4])


def build_match_result(rows: list[dict[str, str]]) -> dict:
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    records = capture["matched"] + capture["unmatched"]
    by_index = {capture_row_index(record["designator"]): record for record in records}
    routes = []
    for index, row in enumerate(rows, start=1):
        record = by_index[index]
        quantity = int(row["quantity"])
        expected_designators = [f"X{index:03d}{unit:03d}" for unit in range(1, quantity + 1)]
        actual_designators = record["designator"].split(",")
        common = {
            "bom_index": index,
            "device_id": row["device_id"],
            "source_mpn": row["mpn"],
            "normalized_mpn": bare_mpn(row["mpn"]),
            "quantity": quantity,
            "designators_complete": actual_designators == expected_designators,
        }
        if "matched_mpn" in record:
            common.update(
                {
                    "route": "J0" if record["status"] == "in_stock" else "J2",
                    "tool_status": record["status"],
                    "lcsc": record["lcsc"],
                    "matched_mpn": record["matched_mpn"],
                    "semantic_mpn_equal": semantic_mpn(record["comment"])
                    == semantic_mpn(record["matched_mpn"]),
                    "stock_snapshot": record["stock"],
                    "displayed_line_cost_usd": float(record["cost"].removeprefix("$")),
                }
            )
        else:
            common.update(
                {
                    "route": "unresolved",
                    "tool_status": "not_matched",
                    "lcsc": None,
                    "matched_mpn": None,
                    "semantic_mpn_equal": None,
                    "stock_snapshot": None,
                    "displayed_line_cost_usd": None,
                }
            )
        routes.append(common)

    summary = capture["result"]
    checks = {
        "capture_is_for_current_upload": capture["input"]["sha256"]
        == hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
        "all_209_unique_lines_returned": len(routes) == len(records) == len(rows) == 209,
        "all_bom_indices_returned_once": set(by_index) == set(range(1, len(rows) + 1)),
        "all_normalized_mpns_returned": all(
            route["normalized_mpn"] == by_index[route["bom_index"]]["comment"]
            for route in routes
        ),
        "all_designators_and_1019_placements_parsed": all(
            route["designators_complete"] for route in routes
        )
        and summary["parsed_placements"] == sum(int(row["quantity"]) for row in rows) == 1019,
        "matched_and_outlier_counts_reconcile": summary["matched_lines"] == 176
        and summary["unmatched_lines"] == 33
        and summary["in_stock_lines"] == 135
        and summary["pre_order_lines"] == 41,
        "no_semantic_mpn_substitution_observed": summary["semantic_mpn_mismatches"] == 0
        and all(route["semantic_mpn_equal"] is not False for route in routes),
        "no_quote_reservation_or_order_created": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed_match_checks": [key for key, value in checks.items() if not value]})
    return {
        "schema_version": 1,
        "artifact": "H5-EVR05",
        "stage": "H5.0.3",
        "status": "bom_tool_match_captured_33_outliers_open",
        "checked_on": CHECKED_ON,
        "input": {
            "target_bom": str(BOM.relative_to(REPO)),
            "target_bom_sha256": sha256(BOM),
            "upload": str(UPLOAD.relative_to(REPO)),
            "upload_sha256": capture["input"]["sha256"],
            "capture": str(CAPTURE.relative_to(REPO)),
            "capture_sha256": sha256(CAPTURE),
            "assembly_quantity": capture["input"]["assembly_quantity"],
        },
        "summary": summary,
        "strict_text_variants": [
            {
                "normalized_mpn": route["normalized_mpn"],
                "matched_mpn": route["matched_mpn"],
                "lcsc": route["lcsc"],
                "finding": "punctuation-only catalogue spelling; semantic MPN is unchanged",
            }
            for route in routes
            if route["matched_mpn"] is not None
            and route["normalized_mpn"].upper() != route["matched_mpn"].upper()
        ],
        "routes": routes,
        "next": {
            "local": "qualify the 33 unresolved lines by exact public-library search, then prequalified non-degrading alternate, J2/J3 exact sourcing, or J4 final assembly",
            "external_authority_later": "a sourcing request, private-stock reservation, quote creation or purchase still requires explicit authority",
            "forbidden": ["sourcing request", "private-stock reservation", "quote creation", "purchase", "component replacement", "KiCad placement/routing", "fabrication"],
        },
        "checks": checks,
    }


def build() -> dict:
    with BOM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    match_result = build_match_result(rows)
    match_summary = match_result["summary"]
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
        "first_minimum_bom_upload_was_transmitted_and_parse_failed": True,
        "normalized_compact_bom_was_transmitted_and_processed": True,
        "all_target_placements_were_parsed": match_summary["parsed_placements"] == 1019,
        "no_semantic_mpn_substitution_was_observed": match_summary["semantic_mpn_mismatches"] == 0,
        "all_33_unmatched_lines_remain_explicit": match_summary["unmatched_lines"] == 33,
        "no_order_or_layout_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed": [key for key, value in checks.items() if not value], "missing": missing})
    return {
        "schema_version": 1,
        "artifact": "H5-EVR04",
        "stage": "H5.0.3",
        "status": "reference_selected_33_platform_outliers_open",
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
            "columns": ["Comment", "Designator", "Footprint", "Quantity", "Manufacturer Part Number", "LCSC Part #"],
            "exact_lines": len(rows),
            "project_data_fields": ["Manufacturer Part Number", "Quantity"],
            "synthetic_parser_fields": ["Designator", "Footprint"],
            "contains_only_authorized_project_data": True,
            "authorized_on": UPLOAD_AUTHORIZED_ON,
            "transmitted": True,
            "processed": True,
            "assembly_quantity": 5,
            "result_artifact": str(MATCH_OUTPUT.relative_to(REPO)),
            "first_attempt": {
                "sha256": "6f3d832ff4751d2dad37c1fe5d944f6a4ff50869f819ba49a5fb7f2423c57db4",
                "columns": ["Manufacturer Part Number", "Quantity"],
                "transmitted": True,
                "result": "JLCPCB notice: File parsing failed",
            },
            "second_attempt": {
                "columns": ["Comment", "Designator", "Footprint", "Quantity", "Manufacturer Part Number", "LCSC Part #"],
                "transmitted": True,
                "result": "176 matched, 33 unmatched, but one 192-placement designator list was truncated to 191; superseded",
            },
            "current_attempt": {
                "sha256": hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
                "transmitted": True,
                "processed": True,
                "result": "176 matched, 33 unmatched, all 1019 target placements parsed",
            },
            "blocker": "33 unmatched lines require local qualification; no sourcing request, quote, reservation or order has been created",
        },
        "critical_spot_checks": SPOT_CHECKS,
        "summary": {
            "target_bom_lines": len(rows),
            "critical_lines_spot_checked": len(SPOT_CHECKS),
            "public_stock_exact_or_revision_explicit": sum(row["tier"] == "J0" for row in SPOT_CHECKS),
            "preorder_reservation": sum(row["tier"] == "J2" for row in SPOT_CHECKS),
            "global_sourcing_or_consignment": sum(row["tier"] == "J3" for row in SPOT_CHECKS),
            "post_pcba_final_assembly": sum(row["tier"] == "J4" for row in SPOT_CHECKS),
            "bom_tool_exact_or_punctuation_equivalent_matches": match_summary["matched_lines"],
            "bom_tool_public_stock_lines": match_summary["in_stock_lines"],
            "bom_tool_preorder_lines": match_summary["pre_order_lines"],
            "bom_tool_unmatched_lines": match_summary["unmatched_lines"],
            "target_placements_parsed": match_summary["parsed_placements"],
            "full_bom_lines_pending_mapping": match_summary["unmatched_lines"],
        },
        "policy": {
            "selection_time": "prefer J0; use J1 only after owner-level equivalence checks; use J2/J3 for function-critical identities that cannot be replaced without degradation",
            "freeze_time": "every soldered line must have an exact JLC number or a received private-stock route, assembly type and attrition quantity",
            "order_time": "recheck stock and price; a shortage reopens sourcing, never authorizes a silent substitute",
            "continuity": "permanent availability is approximated by qualified alternates or reserved private inventory, never claimed from one stock snapshot",
        },
        "next": {
            "local": "qualify the 33 BOM Tool outliers by exact search, non-degrading alternate, J2/J3 exact sourcing, or J4 final assembly",
            "external_authority_later": "Parts API application, sourcing request, quote creation, private-stock reservation and purchase still require separate explicit authority",
            "forbidden": ["purchase", "component replacement", "Parts API application", "sourcing request", "quote creation", "private-stock reservation", "KiCad placement/routing", "fabrication"],
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


def outlier_table(match_result: dict, russian: bool) -> str:
    lines = [
        "| Нормализованный MPN | Кол-во | Следующее доказательство |"
        if russian
        else "| Normalized MPN | Qty | Next evidence |",
        "|---|---:|---|",
    ]
    next_text = (
        "exact search → недеградирующая серийная замена → J2/J3/J4"
        if russian
        else "exact search → non-degrading serial alternate → J2/J3/J4"
    )
    for route in match_result["routes"]:
        if route["tool_status"] == "not_matched":
            lines.append(f"| `{route['normalized_mpn']}` | {route['quantity']} | {next_text} |")
    return "\n".join(lines)


def render(data: dict, match_result: dict, russian: bool) -> str:
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

## Контрольный BOM Tool прогон

Нормализованный BOM принят и обработан для расчётного тиража 5 плат. JLCPCB сопоставил `{summary['bom_tool_exact_or_punctuation_equivalent_matches']}` из `{summary['target_bom_lines']}` уникальных строк: `{summary['bom_tool_public_stock_lines']}` public-stock и `{summary['bom_tool_preorder_lines']}` pre-order; `{summary['bom_tool_unmatched_lines']}` строк остались явными outliers. Все `{summary['target_placements_parsed']}` установок распознаны. Два написания Panasonic отличаются только дефисами; семантических подмен MPN — ноль.

Показываемая BOM Tool сумма `$1255.6365` — сумма рекомендованных заказных количеств только для 176 найденных строк, включая справочные pre-order цены. Это **не** полная цена сборки, не quote и не заказ.

<details>
<summary>33 строки, требующие локальной квалификации</summary>

{outlier_table(match_result, True)}

</details>

## Независимая проверка критических деталей

До bulk-прогона отдельно проверены `{summary['critical_lines_spot_checked']}` критических идентичностей. Их stock-снимки не заменяют текущий BOM Tool результат и не обещают постоянную доступность.

{table(data, True)}

## Граница сборки

JLCPCB собирает обе платы и принятые SMT/THT-компоненты. Дисплейный flex, U214/M5, аккумуляторы, внешние антенны и финальная сборка «бутерброда» остаются post-PCBA operations, пока отдельный box-build quote не докажет обратное.

## Текущий результат

- JLCPCB Standard PCBA принят как рабочий reference без lock-in.
- Bulk mapping закрыт для `{summary['bom_tool_exact_or_punctuation_equivalent_matches']}` строк; локальная квалификация открыта для `{summary['full_bom_lines_pending_mapping']}` outliers.
- Прямой RFQ NiceRF отложен: сначала проверяется JLC global sourcing/new-part route.
- Минимальный BOM upload передан и обработан; quote, Parts API application, sourcing request, reservation, покупка, замены, KiCad layout и fabrication не выполнялись и не разрешены.

Машинные результаты: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json) и [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json). [Требования JLCPCB к BOM]({SOURCES['jlc_bom_format']}).
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

## Controlled BOM Tool run

The normalized BOM was accepted and processed for an assessment quantity of five boards. JLCPCB matched `{summary['bom_tool_exact_or_punctuation_equivalent_matches']}` of `{summary['target_bom_lines']}` unique lines: `{summary['bom_tool_public_stock_lines']}` public-stock and `{summary['bom_tool_preorder_lines']}` pre-order; `{summary['bom_tool_unmatched_lines']}` remain explicit outliers. All `{summary['target_placements_parsed']}` placements were parsed. Two Panasonic spellings differ only by punctuation; zero semantic MPN substitutions were observed.

The displayed `$1255.6365` is the sum of recommended order quantities for only the 176 matched lines, including reference pre-order prices. It is **not** a complete assembly price, quote or order.

<details>
<summary>33 lines requiring local qualification</summary>

{outlier_table(match_result, False)}

</details>

## Independent critical-part check

`{summary['critical_lines_spot_checked']}` critical identities were checked independently before the bulk run. Their stock snapshots neither override the current BOM Tool result nor promise permanent availability.

{table(data, False)}

## Assembly boundary

JLCPCB assembles both boards and accepted SMT/THT parts. Display flex mating, U214/M5, cells, external antennas and final sandwich integration remain post-PCBA operations until a separate box-build quote proves otherwise.

## Current result

- JLCPCB Standard PCBA is the working reference without lock-in.
- Bulk mapping is complete for `{summary['bom_tool_exact_or_punctuation_equivalent_matches']}` lines; local qualification remains open for `{summary['full_bom_lines_pending_mapping']}` outliers.
- Direct NiceRF contact is deferred while the JLC global-sourcing/new-part route is checked first.
- The minimum BOM upload was transmitted and processed. No quote, Parts API application, sourcing request, reservation, purchase, replacement, KiCad layout or fabrication was performed or authorized.

Machine results: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json) and [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json). [JLCPCB BOM requirements]({SOURCES['jlc_bom_format']}).
"""


def render_upload() -> str:
    """Return a standard-column BOM containing only authorized project data."""
    with BOM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=[
            "Comment",
            "Designator",
            "Footprint",
            "Quantity",
            "Manufacturer Part Number",
            "LCSC Part #",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for index, row in enumerate(rows, start=1):
        quantity = int(row["quantity"])
        mpn = bare_mpn(row["mpn"])
        writer.writerow(
            {
                "Comment": mpn,
                "Designator": ",".join(
                    # JLCPCB derives part quantity from the designator list and
                    # truncates cells around 2,000 characters.  The 192-piece
                    # resistor line therefore needs compact, fixed-width IDs.
                    f"X{index:03d}{unit:03d}" for unit in range(1, quantity + 1)
                ),
                "Footprint": "TBD",
                "Quantity": quantity,
                "Manufacturer Part Number": mpn,
                "LCSC Part #": "",
            }
        )
    return stream.getvalue()


def outputs() -> dict[Path, str]:
    data = build()
    with BOM.open(newline="", encoding="utf-8") as handle:
        match_result = build_match_result(list(csv.DictReader(handle)))
    return {
        OUTPUT: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        MATCH_OUTPUT: json.dumps(match_result, ensure_ascii=False, indent=2) + "\n",
        UPLOAD: render_upload(),
        DOC_EN: render(data, match_result, False),
        DOC_RU: render(data, match_result, True),
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
    print(
        f"ok: {data['decision']['reference_platform']}; "
        f"{data['summary']['bom_tool_exact_or_punctuation_equivalent_matches']}/"
        f"{data['summary']['target_bom_lines']} BOM Tool lines matched; "
        f"{data['summary']['bom_tool_unmatched_lines']} outliers open; "
        "no order or replacement authorized"
    )


if __name__ == "__main__":
    main()
