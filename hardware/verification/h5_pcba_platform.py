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
OUTLIER_CAPTURE = REPO / "hardware/verification/jlcpcb-outlier-search-capture-2026-08-25.json"
OUTLIER_OUTPUT = REPO / "hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json"
DOC_EN = REPO / "docs/manufacturing-platform.md"
DOC_RU = REPO / "docs/manufacturing-platform.ru.md"
CHECKED_ON = "2026-08-26"
UPLOAD_AUTHORIZED_ON = "2026-08-25"
SUPPLIER_INQUIRY = {
    "supplier": "JLCPCB",
    "channel": "Contact Us / PCB Assembly Inquiry",
    "submitted_on": "2026-08-26",
    "result": "successfully_submitted",
    "ticket_number": None,
    "scope": "information only; no order, quote project, sourcing request or reservation",
}


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
            "G-NiceRF",
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


# Every BOM Tool outlier is resolved without changing the selected functional
# identity.  J0/J2 entries name an original-maker catalogue row observed in the
# public search capture.  J3 keeps the exact selected MPN for sourcing or
# consignment.  J4-F/J4-P are intentionally outside automated PCBA placement:
# J4-F must be accepted by the final-assembly factory, while J4-P is packed as
# a removable/user-installed item.
OUTLIER_RESOLUTIONS = {
    "SN74LVC1G07DCKR": {"route": "J0", "lcsc": "C7830", "manufacturer": "Texas Instruments"},
    "MSPM0C1106SDGS20R": {"route": "J0", "lcsc": "C52995805", "manufacturer": "Texas Instruments"},
    "SN74LVC1G17DCKR": {"route": "J0", "lcsc": "C10425", "manufacturer": "Texas Instruments"},
    "SN74LVC1G08DCKR": {"route": "J0", "lcsc": "C7832", "manufacturer": "Texas Instruments"},
    "TCA9539PWR": {"route": "J0", "lcsc": "C131972", "manufacturer": "Texas Instruments"},
    "RC0402FR-07100RL": {"route": "J0", "lcsc": "C106232", "manufacturer": "YAGEO"},
    "RC0402FR-074K7L": {"route": "J0", "lcsc": "C105871", "manufacturer": "YAGEO"},
    "RC0402FR-0733RL": {"route": "J0", "lcsc": "C138002", "manufacturer": "YAGEO"},
    "TPD4E05U06DQAR": {"route": "J0", "lcsc": "C138714", "manufacturer": "Texas Instruments"},
    "TLV1824PWR": {"route": "J0", "lcsc": "C35149428", "manufacturer": "Texas Instruments"},
    "RC0402FR-071KL": {"route": "J0", "lcsc": "C106235", "manufacturer": "YAGEO"},
    "TPD2EUSB30ADRTR": {"route": "J0", "lcsc": "C94934", "manufacturer": "Texas Instruments"},
    "SC1512-A4": {"route": "J2", "lcsc": "C52763783", "manufacturer": "Raspberry Pi"},
    "BGS13SN8E6327XTSA1": {"route": "J2", "lcsc": "C55118249", "manufacturer": "Infineon Technologies"},
    "ESP32-C5-WROOM-1U-N8R8": {"route": "J2", "lcsc": "C51950748", "manufacturer": "Espressif Systems"},
    "B0310J50100AHF": {"route": "J2", "lcsc": "C5160223", "manufacturer": "TTM Technologies, Inc."},
    "RFPC-SMA31-FN-175-A": {"route": "J3", "reason": "exact board SMA is orderable outside the public JLC library"},
    "TSMP95000TT": {"route": "J3", "reason": "only a zero-stock generic JLC Assembly placeholder exists; exact Vishay identity must be sourced"},
    "RFPC-SMA32-FN-175-A": {"route": "J3", "reason": "exact board RP-SMA is orderable outside the public JLC library"},
    "1125R-SMT-4P": {"route": "J3", "reason": "exact Seeed SMT Unit connector is orderable outside the public JLC library"},
    "AS02404PO": {"route": "J3", "reason": "exact board speaker is orderable outside the public JLC library and needs manual/THT assembly acceptance"},
    "FX8C-80S-SV5(92)": {"route": "J3", "reason": "exact inter-board receptacle is orderable outside the public JLC library"},
    "TPUL2G223BQBR": {"route": "J3", "reason": "exact safety timer must be sourced; no silent timing-function alternate"},
    "TLV1821DCKR": {"route": "J3", "reason": "exact voice-evidence comparator must be sourced; no silent threshold/path alternate"},
    "GJM1555C1H101JB01D": {"route": "J3", "reason": "retain exact RF capacitor until an RF-equivalent alternate is separately qualified"},
    "PESD24VY1BSF": {"route": "J3", "reason": "retain exact low-capacitance RF ESD identity until an RF-equivalent alternate is separately qualified"},
    "E01-ML01IPX": {"route": "J3", "reason": "three exact full-power nRF24 modules are externally orderable and must be consigned or globally sourced"},
    "2118651-2": {"route": "J4-F", "reason": "five removable 30-mm microcoax jumpers require factory installation, strain routing and continuity test during final sandwich assembly"},
    "U214 Cap LoRa-1262": {"route": "J4-P", "reason": "removable rear Cap accessory is factory-tested, then packed separately for user installation"},
    "HMX035CTFT-001": {"route": "J4-F", "reason": "display/flex requires factory mating and display/touch functional test during final assembly"},
    "1227-J": {"route": "J4-F", "reason": "encoder knob requires factory installation and control test after enclosure integration"},
    "18650 4000mAh": {"route": "J4-P", "reason": "protected cells are packed separately for user installation unless a compliant battery box-build and shipping route is later qualified"},
}

ROUTE_IDS = ("J0", "J1", "J2", "J3", "J4-F", "J4-P")
J4_FACTORY_MPNS = {"2118651-2", "HMX035CTFT-001", "1227-J"}
J4_PACKED_MPNS = {"U214 Cap LoRa-1262", "18650 4000mAh"}


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


JLCAPI_STATE = {
    "application_status": "approved",
    "app_name": "ESP32-Leshy2 BOM Validator",
    "app_status": "enabled",
    "parts_permission_status": "rejected",
    "automatically_listed_permissions": {"PCB": "rejected", "3D": "rejected"},
    "inactive_permissions": ["SMT Stencil", "JLC Balance"],
    "access_key_created": True,
    "tokenization_key_created": False,
    "credential_storage": "local macOS Keychain; no credential is stored in this repository",
    "raw_api_data_publication": False,
    "usable_now": False,
    "checked_on": CHECKED_ON,
}


VOICE_PART_ROUTES = {
    "SA818S-U": {
        "device_id": "nicerf_sa818s_u_v18",
        "mpn": "G-NiceRF SA818S-U",
        "lcsc": "C3001549",
        "route": "J0",
        "stock": 68,
        "available_order_quantity": 60,
        "quantity_one_usd": "9.7347",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549",
    },
    "SA818S-V": {
        "device_id": "nicerf_sa818s_v_v18",
        "mpn": "G-NiceRF SA818S-V",
        "lcsc": "C51897911",
        "route": "J2",
        "stock": 0,
        "minimum_quantity": 1,
        "quantity_one_usd": "10.0710",
        "status": "pre_order",
        "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911",
    },
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
    {"id": "J4-F", "name": "factory final assembly", "rule": "the final-assembly factory must install and test the part after PCBA; H5 and H7 cannot close until this box-build route is accepted and quoted"},
    {"id": "J4-P", "name": "factory-packed removable item", "rule": "the factory tests compatibility where applicable and packs the removable accessory, antenna or cell separately for user installation"},
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
    {"device_id": "nicerf_sa818s_u_v18", "mpn": "G-NiceRF SA818S-U", "jlc": "C3001549", "tier": "J0", "stock": 68, "pcba": "Standard PCBA", "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549", "finding": "exact selected UHF module is priced and in public stock"},
    {"device_id": "nicerf_sa818s_v_v18", "mpn": "G-NiceRF SA818S-V", "jlc": "C51897911", "tier": "J2", "stock": 0, "pcba": "Standard PCBA pre-order", "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911", "finding": "exact selected VHF module is priced but stock-zero pre-order; lead time remains open"},
    {"device_id": "qdtech_hmx035ctft_001", "mpn": "HMX035CTFT-001", "jlc": None, "tier": "J4-F", "stock": 0, "pcba": "display/flex belongs to factory final assembly", "source": "https://jlcpcb.com/parts/componentSearch?searchTxt=HMX035CTFT-001", "finding": "keep replaceable display-adapter architecture; require factory mating plus display/touch test rather than treating the display as an ordinary line-loaded SMT part"},
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
    by_mpn = {record["comment"]: record for record in records}
    routes = []
    for index, row in enumerate(rows, start=1):
        quantity = int(row["quantity"])
        expected_designators = [f"X{index:03d}{unit:03d}" for unit in range(1, quantity + 1)]
        normalized_mpn = bare_mpn(row["mpn"])
        common = {
            "bom_index": index,
            "device_id": row["device_id"],
            "source_mpn": row["mpn"],
            "normalized_mpn": normalized_mpn,
            "quantity": quantity,
        }
        if normalized_mpn in VOICE_PART_ROUTES:
            voice = VOICE_PART_ROUTES[normalized_mpn]
            common.update(
                {
                    "route": voice["route"],
                    "tool_status": voice["status"],
                    "match_provenance": "current_exact_jlcpcb_part_page",
                    "lcsc": voice["lcsc"],
                    "matched_mpn": normalized_mpn,
                    "semantic_mpn_equal": True,
                    "stock_snapshot": voice["stock"],
                    "displayed_line_cost_usd": float(voice["quantity_one_usd"]),
                    "designators_complete": len(expected_designators) == quantity,
                }
            )
            routes.append(common)
            continue

        record = by_mpn[normalized_mpn]
        actual_designators = record["designator"].split(",")
        common["designators_complete"] = len(expected_designators) == quantity
        common["historical_capture_quantity"] = len(actual_designators)
        common["current_quantity_delta"] = quantity - len(actual_designators)
        common["match_provenance"] = "unchanged_mpn_from_2026_08_25_bom_tool_capture"
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

    inherited = capture["result"]
    summary = {
        "target_lines": len(routes),
        "matched_lines": inherited["matched_lines"] + len(VOICE_PART_ROUTES),
        "bom_tool_inherited_matched_lines": inherited["matched_lines"],
        "exact_voice_page_lines": len(VOICE_PART_ROUTES),
        "unmatched_lines": inherited["unmatched_lines"] - 1,
        "in_stock_lines": inherited["in_stock_lines"] + 1,
        "pre_order_lines": inherited["pre_order_lines"] + 1,
        "parsed_placements": sum(int(row["quantity"]) for row in rows),
        "strict_text_variants": inherited["strict_text_variants"],
        "semantic_mpn_mismatches": inherited["semantic_mpn_mismatches"],
    }
    current_mpns = {bare_mpn(row["mpn"]) for row in rows}
    checks = {
        "historical_capture_is_self_consistent": len(records) == len(by_mpn) == 209
        and inherited["matched_lines"] == 176
        and inherited["unmatched_lines"] == 33,
        "historical_capture_diff_is_exactly_sa518_to_dual_sa818s": set(by_mpn) - current_mpns == {"SA518"}
        and current_mpns - set(by_mpn) == set(VOICE_PART_ROUTES),
        "all_210_current_lines_returned_once": len(routes) == len(rows) == 210
        and len({route["bom_index"] for route in routes}) == 210,
        "all_current_designator_quantities_and_1052_placements_reconcile": all(
            route["designators_complete"] for route in routes
        ) and summary["parsed_placements"] == 1052,
        "current_exact_route_counts_reconcile": summary["matched_lines"] == 178
        and summary["unmatched_lines"] == 32
        and summary["in_stock_lines"] == 136
        and summary["pre_order_lines"] == 42,
        "both_voice_routes_use_exact_current_jlcpcb_pages": all(
            any(route["normalized_mpn"] == mpn and route["lcsc"] == voice["lcsc"] for route in routes)
            for mpn, voice in VOICE_PART_ROUTES.items()
        ),
        "no_semantic_mpn_substitution_observed": summary["semantic_mpn_mismatches"] == 0
        and all(route["semantic_mpn_equal"] is not False for route in routes),
        "no_quote_reservation_or_order_created": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed_match_checks": [key for key, value in checks.items() if not value]})
    return {
        "schema_version": 1,
        "artifact": "H5-EVR05",
        "stage": "H5.0.3-R1",
        "status": "current_210_line_route_join_captured_32_outliers_open",
        "checked_on": CHECKED_ON,
        "input": {
            "target_bom": str(BOM.relative_to(REPO)),
            "target_bom_sha256": sha256(BOM),
            "upload": str(UPLOAD.relative_to(REPO)),
            "upload_sha256": hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
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
            "local": "retain the 32 unchanged outlier resolutions, join exact SA818S-U/V routes, then recheck every current route without accepting substitutions",
            "external_authority_later": "a sourcing request, private-stock reservation, quote creation or purchase still requires explicit authority",
            "forbidden": ["sourcing request", "private-stock reservation", "quote creation", "purchase", "component replacement", "KiCad placement/routing", "fabrication"],
        },
        "checks": checks,
    }


def build_outlier_resolution(rows: list[dict[str, str]], match_result: dict) -> dict:
    capture = json.loads(OUTLIER_CAPTURE.read_text(encoding="utf-8"))
    searches = {row["query"]: row for row in capture["searches"]}
    raw_outliers = {
        route["normalized_mpn"]: route
        for route in match_result["routes"]
        if route["tool_status"] == "not_matched"
    }
    source_by_mpn = {bare_mpn(row["mpn"]): row for row in rows}
    resolved = []
    for mpn in sorted(raw_outliers, key=lambda value: raw_outliers[value]["bom_index"]):
        resolution = OUTLIER_RESOLUTIONS[mpn]
        search = searches[mpn]
        selected_catalogue_row = None
        if resolution["route"] in {"J0", "J2"}:
            selected = [
                row
                for row in search["exact"]
                if row["lcsc"] == resolution["lcsc"]
                and row["manufacturer"] == resolution["manufacturer"]
                and semantic_mpn(row["mpn"]) == semantic_mpn(mpn)
            ]
            if len(selected) != 1:
                raise ValueError({"missing_selected_catalogue_row": mpn, "selected": selected})
            selected_catalogue_row = selected[0]
        source = source_by_mpn[mpn]
        resolved.append(
            {
                "bom_index": raw_outliers[mpn]["bom_index"],
                "device_id": raw_outliers[mpn]["device_id"],
                "normalized_mpn": mpn,
                "quantity": raw_outliers[mpn]["quantity"],
                "route": resolution["route"],
                "lcsc": resolution.get("lcsc"),
                "manufacturer": resolution.get("manufacturer"),
                "stock_snapshot": selected_catalogue_row["stock"] if selected_catalogue_row else None,
                "reason": resolution.get(
                    "reason",
                    "exact original-maker public catalogue row is in stock"
                    if resolution["route"] == "J0"
                    else "exact original-maker public catalogue row exists but has no public stock",
                ),
                "target_bom_orderable_evidence": source["orderable_evidence"],
                "target_bom_source": source["cost_source"],
                "component_replacement": False,
            }
        )

    final_routes = [dict(route) for route in match_result["routes"]]
    resolution_by_index = {row["bom_index"]: row for row in resolved}
    for route in final_routes:
        if route["bom_index"] in resolution_by_index:
            replacement = resolution_by_index[route["bom_index"]]
            route.update(
                {
                    "route": replacement["route"],
                    "lcsc": replacement["lcsc"],
                    "stock_snapshot": replacement["stock_snapshot"],
                    "outlier_resolution_reason": replacement["reason"],
                    "component_replacement": False,
                }
            )
    counts = {
        tier: sum(route["route"] == tier for route in final_routes)
        for tier in ROUTE_IDS
    }
    checks = {
        "capture_covers_all_32_unchanged_bom_tool_outliers": set(searches) - {"SA518"} == set(raw_outliers) == set(OUTLIER_RESOLUTIONS),
        "every_outlier_has_one_route": len(resolved) == len({row["bom_index"] for row in resolved}) == 32,
        "j0_rows_have_positive_original_maker_stock": all(
            row["stock_snapshot"] is not None and row["stock_snapshot"] > 0
            for row in resolved
            if row["route"] == "J0"
        ),
        "j2_rows_have_exact_zero_stock_catalogue_identity": all(
            row["stock_snapshot"] == 0 and row["lcsc"]
            for row in resolved
            if row["route"] == "J2"
        ),
        "j3_rows_keep_exact_selected_identity": all(
            row["target_bom_orderable_evidence"] == "present" and not row["component_replacement"]
            for row in resolved
            if row["route"] == "J3"
        ),
        "j4f_rows_are_factory_final_assembly_parts": {
            row["normalized_mpn"] for row in resolved if row["route"] == "J4-F"
        }
        == J4_FACTORY_MPNS,
        "j4p_rows_are_factory_packed_removable_parts": {
            row["normalized_mpn"] for row in resolved if row["route"] == "J4-P"
        }
        == J4_PACKED_MPNS,
        "generic_placeholders_are_not_accepted_as_identity": all(
            row["lcsc"] is None for row in resolved if row["normalized_mpn"] == "TSMP95000TT"
        ),
        "all_210_lines_have_defined_availability_or_final_assembly_route": sum(counts.values()) == 210
        and all(route["route"] in counts for route in final_routes),
        "no_component_replacement_is_introduced": counts["J1"] == 0
        and all(not row["component_replacement"] for row in resolved),
        "no_sourcing_quote_reservation_or_order_created": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed_outlier_checks": [key for key, value in checks.items() if not value]})
    return {
        "schema_version": 2,
        "artifact": "H5-EVR06",
        "stage": "H5.0.3-R1",
        "status": "all_210_routes_mapped_dual_sa818s_and_factory_gates_open",
        "checked_on": CHECKED_ON,
        "input": {
            "bom_tool_result": str(MATCH_OUTPUT.relative_to(REPO)),
            "bom_tool_result_sha256": hashlib.sha256(
                (json.dumps(match_result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            ).hexdigest(),
            "search_capture": str(OUTLIER_CAPTURE.relative_to(REPO)),
            "search_capture_sha256": sha256(OUTLIER_CAPTURE),
        },
        "summary": {
            "target_bom_lines": len(final_routes),
            "bom_tool_matched_lines": match_result["summary"]["matched_lines"],
            "bom_tool_outliers_resolved": len(resolved),
            "availability_routes": counts,
            "component_replacements": 0,
            "unmapped_lines": 0,
            "open_qualified_price_lines": 0,
            "open_qualified_price_mpn": None,
            "preorder_lead_time_open_lines": 1,
            "preorder_lead_time_open_mpn": "SA818S-V",
        },
        "outlier_resolutions": resolved,
        "final_routes": final_routes,
        "boundary": {
            "meaning": "availability and sourcing route only; footprint, placement, assembly-class and current stock are revalidated at BOM freeze",
            "factory_final_assembly": {
                "route": "J4-F",
                "mpns": sorted(J4_FACTORY_MPNS),
                "accepted_and_quoted": False,
                "gate": "H5 and H7 remain open until the selected factory accepts and quotes installation plus functional test",
            },
            "factory_packed_removable": {
                "route": "J4-P",
                "mpns": sorted(J4_PACKED_MPNS),
                "accepted_and_quoted": False,
                "gate": "kit inclusion, compatibility test where applicable, packing and battery shipping boundary must be quoted",
            },
            "not_authorized": ["sourcing request", "quote", "reservation", "purchase", "component replacement", "KiCad placement/routing", "fabrication"],
        },
        "next": {
            "decision_needed": "wait for the itemized response to the no-order inquiry submitted on 2026-08-26: exact SA818S-V pre-order lead time and J4-F/J4-P capability/pricing remain open before H5.0.3-R1 can close",
            "purchase_remains_last": True,
        },
        "checks": checks,
    }


def build() -> dict:
    with BOM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    match_result = build_match_result(rows)
    outlier_result = build_outlier_resolution(rows, match_result)
    match_summary = match_result["summary"]
    by_id = {row["device_id"]: row for row in rows}
    missing = [row["device_id"] for row in SPOT_CHECKS if row["device_id"] not in by_id]
    checks = {
        "reference_is_standard_pcba": PLATFORMS[0]["id"] == "jlcpcb-standard-pcba",
        "target_bom_has_210_exact_lines": len(rows) == 210,
        "every_spot_check_is_in_target_bom": not missing,
        "every_spot_check_has_a_source_and_tier": all(row["source"] and row["tier"] in {tier["id"] for tier in TIERS} for row in SPOT_CHECKS),
        "no_stock_snapshot_claims_permanent_availability": True,
        "no_component_replacement_is_authorized": True,
        "minimum_bom_upload_authorized_by_user": True,
        "first_minimum_bom_upload_was_transmitted_and_parse_failed": True,
        "historical_209_line_compact_bom_was_transmitted_and_processed": True,
        "current_210_line_upload_was_generated_but_not_transmitted": True,
        "all_target_placements_were_parsed": match_summary["parsed_placements"] == 1052,
        "no_semantic_mpn_substitution_was_observed": match_summary["semantic_mpn_mismatches"] == 0,
        "all_32_unchanged_unmatched_lines_remain_explicit": match_summary["unmatched_lines"] == 32,
        "all_210_lines_have_defined_availability_or_final_assembly_route": outlier_result["summary"]["unmapped_lines"] == 0,
        "all_component_sample_prices_are_known": outlier_result["summary"]["open_qualified_price_lines"] == 0,
        "sa818s_v_preorder_lead_time_is_explicitly_open": outlier_result["summary"]["preorder_lead_time_open_mpn"] == "SA818S-V",
        "factory_final_assembly_gate_is_explicitly_open": not PLATFORMS[0]["fit"]["final_box_build_proven"],
        "jlcapi_application_and_app_are_ready": JLCAPI_STATE["application_status"] == "approved"
        and JLCAPI_STATE["app_status"] == "enabled"
        and JLCAPI_STATE["access_key_created"],
        "parts_api_rejection_is_explicit_and_fail_closed": JLCAPI_STATE["parts_permission_status"] == "rejected"
        and not JLCAPI_STATE["usable_now"],
        "both_selected_voice_modules_have_exact_jlcpcb_routes": set(VOICE_PART_ROUTES) == {"SA818S-U", "SA818S-V"}
        and all(row["lcsc"] and row["quantity_one_usd"] for row in VOICE_PART_ROUTES.values()),
        "api_credentials_are_not_repository_data": "no credential" in JLCAPI_STATE["credential_storage"]
        and not JLCAPI_STATE["tokenization_key_created"],
        "no_order_or_layout_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed": [key for key, value in checks.items() if not value], "missing": missing})
    return {
        "schema_version": 2,
        "artifact": "H5-EVR04",
        "stage": "H5.0.3-R1",
        "status": "routes_complete_dual_sa818s_preorder_and_factory_gates_open",
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
            "J4-F_factory_final_assembly": {
                "status": "open_until_factory_acceptance_and_quote",
                "required_operations": ["display/flex mating and display/touch test", "five microcoax installation, strain routing and continuity test", "encoder knob installation and control test", "final sandwich/enclosure integration and whole-device functional test"],
                "close_gate": "H5 and H7 cannot close until the selected factory accepts and prices these operations",
            },
            "J4-P_factory_packed_removable": {
                "status": "open_until_kit_and_shipping_quote",
                "required_operations": ["test U214 compatibility, then pack the removable Cap separately", "pack selected external antennas separately", "pack protected 18650 cells separately for user installation unless compliant integrated battery shipping is qualified"],
            },
        },
        "parts_api": JLCAPI_STATE,
        "supplier_inquiry": SUPPLIER_INQUIRY,
        "voice_part_routes": VOICE_PART_ROUTES,
        "bom_tool_upload": {
            "path": str(UPLOAD.relative_to(REPO)),
            "sha256": hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
            "columns": ["Comment", "Designator", "Footprint", "Quantity", "Manufacturer Part Number", "LCSC Part #"],
            "exact_lines": len(rows),
            "project_data_fields": ["Manufacturer Part Number", "Quantity"],
            "synthetic_parser_fields": ["Designator", "Footprint"],
            "contains_only_authorized_project_data": True,
            "authorized_on": UPLOAD_AUTHORIZED_ON,
            "transmitted": False,
            "processed": False,
            "assembly_quantity": 5,
            "result_artifact": str(MATCH_OUTPUT.relative_to(REPO)),
            "outlier_result_artifact": str(OUTLIER_OUTPUT.relative_to(REPO)),
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
            "historical_209_line_attempt": {
                "capture": str(CAPTURE.relative_to(REPO)),
                "transmitted": True,
                "processed": True,
                "result": "176 matched, 33 unmatched, all 1019 historical target placements parsed",
            },
            "current_210_line_attempt": {
                "sha256": hashlib.sha256(render_upload().encode("utf-8")).hexdigest(),
                "transmitted": False,
                "processed": False,
                "result": "historical 209-line capture retained for 208 unchanged identities; exact current SA818S-U/V pages joined separately into the 210-line map",
            },
            "blocker": "all 210 current lines have defined routes and all sample component prices are known; exact SA818S-V pre-order lead time plus J4-F/J4-P final-assembly acceptance/pricing remain open, and no sourcing request, quote, reservation or order has been created",
        },
        "critical_spot_checks": SPOT_CHECKS,
        "summary": {
            "target_bom_lines": len(rows),
            "critical_lines_spot_checked": len(SPOT_CHECKS),
            "public_stock_exact_or_revision_explicit": sum(row["tier"] == "J0" for row in SPOT_CHECKS),
            "preorder_reservation": sum(row["tier"] == "J2" for row in SPOT_CHECKS),
            "global_sourcing_or_consignment": sum(row["tier"] == "J3" for row in SPOT_CHECKS),
            "factory_final_assembly": sum(row["tier"] == "J4-F" for row in SPOT_CHECKS),
            "factory_packed_removable": sum(row["tier"] == "J4-P" for row in SPOT_CHECKS),
            "historical_bom_tool_matched_lines": match_summary["bom_tool_inherited_matched_lines"],
            "historical_bom_tool_public_stock_lines": match_summary["in_stock_lines"] - 1,
            "historical_bom_tool_preorder_lines": match_summary["pre_order_lines"] - 1,
            "historical_bom_tool_unmatched_lines": match_summary["unmatched_lines"] + 1,
            "current_exact_catalogue_routes_before_outlier_resolution": match_summary["matched_lines"],
            "current_public_stock_lines_before_outlier_resolution": match_summary["in_stock_lines"],
            "current_preorder_lines_before_outlier_resolution": match_summary["pre_order_lines"],
            "current_unmatched_lines_before_outlier_resolution": match_summary["unmatched_lines"],
            "target_placements_parsed": match_summary["parsed_placements"],
            "outliers_resolved_after_exact_search": outlier_result["summary"]["bom_tool_outliers_resolved"],
            "availability_routes": outlier_result["summary"]["availability_routes"],
            "full_bom_lines_pending_mapping": outlier_result["summary"]["unmapped_lines"],
            "open_qualified_price_lines": outlier_result["summary"]["open_qualified_price_lines"],
        },
        "policy": {
            "selection_time": "prefer J0; use J1 only after owner-level equivalence checks; use J2/J3 for function-critical identities that cannot be replaced without degradation",
            "freeze_time": "every soldered line must have an exact JLC number or a received private-stock route, assembly type and attrition quantity",
            "order_time": "recheck stock and price; a shortage reopens sourcing, never authorizes a silent substitute",
            "continuity": "permanent availability is approximated by qualified alternates or reserved private inventory, never claimed from one stock snapshot",
        },
        "next": {
            "local": "all 210 lines have defined routes; preserve the map, keep SA818S-V lead time and J4-F/J4-P as open factory gates, and keep the optional rejected Parts API path fail-closed",
            "external_authority_later": "quote creation, sourcing requests, private-stock reservation, purchase and any materially expanded supplier request still require separate explicit authority",
            "forbidden": ["purchase", "component replacement", "sourcing request", "quote creation", "private-stock reservation", "raw API data redistribution", "KiCad placement/routing", "fabrication"],
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


def outlier_table(outlier_result: dict, russian: bool) -> str:
    lines = [
        "| Нормализованный MPN | Кол-во | Маршрут | Доказательство |"
        if russian
        else "| Normalized MPN | Qty | Route | Evidence |",
        "|---|---:|---:|---|",
    ]
    for row in outlier_result["outlier_resolutions"]:
        evidence = (
            f"`{row['lcsc']}` · stock {row['stock_snapshot']}"
            if row["lcsc"]
            else row["reason"]
        )
        lines.append(
            f"| `{row['normalized_mpn']}` | {row['quantity']} | `{row['route']}` | {evidence} |"
        )
    return "\n".join(lines)


def render(data: dict, match_result: dict, outlier_result: dict, russian: bool) -> str:
    summary = data["summary"]
    if russian:
        return f"""# Производственная платформа Leshy2

[English](manufacturing-platform.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

## Базовая линия

**Рабочий reference — JLCPCB Standard PCBA.** Это не эксклюзивная привязка и не разрешение заказа. Standard выбран из-за публичной assembly-библиотеки со stock/JLC-number, двухстороннего SMT+THT, fine-pitch/BGA/QFN, специального stack-up и SPI/AOI/X-ray. [Официальные capabilities]({SOURCES['jlc_capabilities']}) и [варианты sourcing]({SOURCES['jlc_sourcing']}).

PCBWay остаётся fallback для ручного turnkey/box-build quote, Seeed Fusion — второй производственный quote. Их supplier availability хуже подходит как автоматически проверяемый источник выбора MPN.

```mermaid
flowchart TD
  M["Новый MPN"] --> P{"Устанавливается при PCBA?"}
  P -->|да| J0["J0 · exact JLC stock"]
  J0 -->|нет| J1["J1 · квалифицированная замена"]
  J1 -->|нет без деградации| J2["J2 · private pre-order"]
  J2 -->|нет| J3["J3 · global/consign"]
  P -->|нет; ставит фабрика| J4F["J4-F · factory final assembly"]
  P -->|нет; в комплект отдельно| J4P["J4-P · factory-packed"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  F --> R["повторная stock-проверка перед заказом"]
```

## Что значит «доступно всегда»

Ни одна площадка не гарантирует вечный публичный остаток. Для Leshy2 это означает: обычные детали выбираются из JLC stock или имеют заранее квалифицированные замены; уникальные функциональные MPN резервируются в private library через [pre-order]({SOURCES['jlc_private_library']}) или поступают через global sourcing/consignment. Недостаток stock никогда не разрешает фабрике молчаливую замену.

## Контрольный BOM Tool прогон

Контрольный BOM Tool capture относится к прежним 209 строкам: 176 matched, 33 unmatched и 1019 установок. Текущий BOM отличается от него только заменой `SA518` на exact `SA818S-U` + `SA818S-V`: 208 неизменившихся identity присоединены по MPN, а два новых модуля — по точным страницам `C3001549` и `C51897911`. Так получена проверяемая текущая карта `{summary['target_bom_lines']}` строк и `{summary['target_placements_parsed']}` установок без повторной передачи BOM. До применения сохранённых outlier-решений в ней 178 exact catalogue routes и 32 unresolved lines; семантических подмен MPN — ноль.

Сохранённый exact-поиск закрывает все 32 неизменившихся outlier без замены компонентов: 12 добавлены в `J0`, 4 — в `J2`, 11 сохраняют точный MPN через `J3`, 3 требуют фабричной финальной сборки `J4-F`, 2 комплектуются отдельно по `J4-P`. Вместе с новыми voice routes итог всей BOM: `J0=148`, `J1=0`, `J2=46`, `J3=11`, `J4-F=3`, `J4-P=2`; несопоставленных строк — ноль.

Показываемая в историческом BOM Tool capture сумма `$1255.6365` относится только к прежним 176 найденным строкам и **не** является текущей полной ценой сборки, quote или заказом. Актуальная минимальная корзина evidence отдельно посчитана на [странице образцов](component-sample-basket.ru.md).

<details>
<summary>Как разрешены 32 неизменившихся outlier</summary>

{outlier_table(outlier_result, True)}

</details>

## Независимая проверка критических деталей

До bulk-прогона отдельно проверены `{summary['critical_lines_spot_checked']}` критических идентичностей. Их stock-снимки не заменяют текущий BOM Tool результат и не обещают постоянную доступность.

{table(data, True)}

## Граница сборки

JLCPCB Standard PCBA собирает обе платы и принятые SMT/THT-компоненты. Это ещё не подтверждает финальную сборку устройства.

| Маршрут | Обязательная операция | Статус |
|---|---|---|
| `J4-F` | Фабрика стыкует и проверяет дисплей/flex, устанавливает и фиксирует пять microcoax, ставит ручку энкодера, собирает корпус/«бутерброд» и выполняет whole-device test | 🔒 Открыто до письменного подтверждения capability и отдельной цены box-build; без этого H5 и H7 не закрываются |
| `J4-P` | Фабрика проверяет совместимость U214, затем кладёт его отдельно; внешние антенны кладутся комплектом; защищённые 18650 кладутся отдельно для установки пользователем, если не подтверждён безопасный battery box-build и shipping | 🔒 Открыто до kit/packing/shipping quote |

`J4-F` и `J4-P` не означают, что операции уже приняты JLCPCB. Они фиксируют требуемый результат для выбранной фабрики или fallback box-build подрядчика.

## Два точных voice-маршрута

`SA818S-U` связан с exact `C3001549`: stock 68, available quantity 60, цена одного `$9.7347`. `SA818S-V` связан с exact `C51897911`: stock 0, MOQ 1, цена одного `$10.0710`, маршрут `J2` pre-order. `SA818S-CE C19632390` остаётся только qualified-pending UHF-заменой и не входит в production BOM: она требует HIL и firmware clamp 470 МГц, не заменяет VHF и никогда не подставляется молча.

## Текущий результат

- JLCPCB Standard PCBA принят как рабочий reference без lock-in.
- Все `{summary['target_bom_lines']}` строк имеют определённый маршрут `J0`–`J3`, `J4-F` или `J4-P`; функциональных замен нет.
- Все component prices минимальной evidence-корзины известны. Запрос JLCPCB без заказа успешно отправлен 26 августа 2026 года; H5.0.3-R1 теперь ожидает точный срок/условия pre-order `SA818S-V`, подтверждение/цену `J4-F` box-build и условия `J4-P` kit/packing/shipping. [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) отдельно проверит полноту ответа и прохождение gates, не разрешая заказ. Закупка образцов остаётся отдельным последующим решением.
- Заявка JLCAPI одобрена, приложение `ESP32-Leshy2 BOM Validator` создано, ключ подписи хранится только локально вне Git. Портал теперь показывает право Parts как `Rejected`, но причины в журнале нет, поэтому API-вызовы по-прежнему невозможны. PCB/3D также отклонены, SMT Stencil и JLC Balance выключены. Активным остаётся ручной путь через каталог и BOM.
- Прежний 209-строчный BOM upload был передан и обработан; текущий 210-строчный файл сгенерирован локально, но не передавался, потому что 208 identity неизменны, а обе новые exact-страницы проверены отдельно. Quote, sourcing request, reservation, покупка, замены, KiCad layout и fabrication не выполнялись и не разрешены. Сырые API-ответы публично не распространяются.

Машинные результаты: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json) и [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json). [Требования JLCPCB к BOM]({SOURCES['jlc_bom_format']}).
"""
    return f"""# Leshy2 manufacturing platform

[Русский](manufacturing-platform.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

## Reference line

**The working reference is JLCPCB Standard PCBA.** This is neither exclusive lock-in nor order authorization. Standard was selected for its public stock/JLC-number assembly library, double-sided SMT+THT, fine-pitch/BGA/QFN, special stackups and SPI/AOI/X-ray. See the official [assembly capabilities]({SOURCES['jlc_capabilities']}) and [parts-sourcing paths]({SOURCES['jlc_sourcing']}).

PCBWay remains the manual turnkey/box-build quote fallback; Seeed Fusion remains a second manufacturing quote. Their supplier availability is less suitable as a repeatable machine-checkable MPN-selection source.

```mermaid
flowchart TD
  M["New MPN"] --> P{"Placed during PCBA?"}
  P -->|yes| J0["J0 · exact JLC stock"]
  J0 -->|no| J1["J1 · qualified alternate"]
  J1 -->|no non-degrading alternate| J2["J2 · private pre-order"]
  J2 -->|no| J3["J3 · global/consign"]
  P -->|no; factory installs| J4F["J4-F · factory final assembly"]
  P -->|no; packed separately| J4P["J4-P · factory-packed"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  F --> R["stock recheck before every order"]
```

## Meaning of “always available”

No platform guarantees perpetual public stock. Leshy2 therefore selects ordinary parts from JLC stock or with prequalified alternates; unique functional identities are reserved in the [private parts library]({SOURCES['jlc_private_library']}) or received through global sourcing/consignment. A shortage never permits a silent factory substitution.

## Controlled BOM Tool run

The controlled BOM Tool capture belongs to the former 209-line BOM: 176 matched, 33 unmatched and 1019 placements. The current BOM differs only by replacing `SA518` with exact `SA818S-U` + `SA818S-V`: 208 unchanged identities are joined by MPN, and the two new modules by exact `C3001549` and `C51897911` pages. This yields a checkable current map of `{summary['target_bom_lines']}` lines and `{summary['target_placements_parsed']}` placements without retransmitting the BOM. Before applying the retained outlier resolutions it has 178 exact catalogue routes and 32 unresolved lines; zero semantic MPN substitutions were observed.

The retained exact search resolves all 32 unchanged outliers without component replacement: 12 are added to `J0`, 4 to `J2`, 11 retain the exact MPN through `J3`, 3 require factory final assembly `J4-F`, and 2 are packed separately through `J4-P`. With the new voice routes, the whole-BOM result is `J0=148`, `J1=0`, `J2=46`, `J3=11`, `J4-F=3`, `J4-P=2`; zero lines remain unmapped.

The `$1255.6365` displayed in the historical BOM Tool capture covers only its former 176 matched lines and is **not** a current complete assembly price, quote or order. The current minimum evidence basket is calculated separately on the [sample page](component-sample-basket.md).

<details>
<summary>How the 32 unchanged outliers were resolved</summary>

{outlier_table(outlier_result, False)}

</details>

## Independent critical-part check

`{summary['critical_lines_spot_checked']}` critical identities were checked independently before the bulk run. Their stock snapshots neither override the current BOM Tool result nor promise permanent availability.

{table(data, False)}

## Assembly boundary

JLCPCB Standard PCBA assembles both boards and accepted SMT/THT parts. That does not yet prove final device assembly.

| Route | Required operation | Status |
|---|---|---|
| `J4-F` | Factory mates and tests display/flex, installs and strain-routes five microcoax jumpers, installs the encoder knob, integrates the enclosure/sandwich and performs whole-device test | 🔒 Open until written capability acceptance and a separate box-build price; H5 and H7 cannot close without it |
| `J4-P` | Factory compatibility-tests U214 and packs it separately; external antennas are packed as a kit; protected 18650 cells are packed separately for user installation unless compliant battery box-build and shipping are qualified | 🔒 Open until kit/packing/shipping quote |

`J4-F` and `J4-P` do not claim that JLCPCB has already accepted these operations. They define the required result for the selected factory or fallback box-build contractor.

## Two exact voice routes

`SA818S-U` is bound to exact `C3001549`: stock 68, available quantity 60 and one-piece price `$9.7347`. `SA818S-V` is bound to exact `C51897911`: stock 0, MOQ 1, one-piece price `$10.0710` and route `J2` pre-order. `SA818S-CE C19632390` remains only a qualified-pending UHF alternate and is not in the production BOM: it requires HIL and a 470-MHz firmware clamp, never replaces VHF and is never substituted silently.

## Current result

- JLCPCB Standard PCBA is the working reference without lock-in.
- All `{summary['target_bom_lines']}` lines have a defined `J0`–`J3`, `J4-F` or `J4-P` route; no functional replacement was introduced.
- Every component price in the minimum evidence basket is known. A no-order JLCPCB inquiry was successfully submitted on 26 August 2026; H5.0.3-R1 now waits for exact `SA818S-V` pre-order lead time/terms, `J4-F` box-build acceptance/pricing and `J4-P` kit/packing/shipping terms. [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) will separately check response completeness and gate acceptance without authorizing an order. Sample purchase remains a later separate decision.
- The JLCAPI application is approved, the `ESP32-Leshy2 BOM Validator` app exists, and its signing key is stored locally outside Git. The portal now reports Parts permission as `Rejected`, without a reason in its activity log, so API calls remain unusable. PCB/3D are also rejected; SMT Stencil and JLC Balance remain inactive. Manual catalogue/BOM evidence remains the active path.
- The former 209-line BOM upload was transmitted and processed; the current 210-line file was generated locally but not transmitted because 208 identities are unchanged and both new exact pages were checked separately. No quote, sourcing request, reservation, purchase, replacement, KiCad layout or fabrication was performed or authorized. Raw API responses are not redistributed publicly.

Machine results: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json) and [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json). [JLCPCB BOM requirements]({SOURCES['jlc_bom_format']}).
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
    with BOM.open(newline="", encoding="utf-8") as handle:
        outlier_result = build_outlier_resolution(list(csv.DictReader(handle)), match_result)
    return {
        OUTPUT: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        MATCH_OUTPUT: json.dumps(match_result, ensure_ascii=False, indent=2) + "\n",
        OUTLIER_OUTPUT: json.dumps(outlier_result, ensure_ascii=False, indent=2) + "\n",
        UPLOAD: render_upload(),
        DOC_EN: render(data, match_result, outlier_result, False),
        DOC_RU: render(data, match_result, outlier_result, True),
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
        f"{data['summary']['current_exact_catalogue_routes_before_outlier_resolution']}/"
        f"{data['summary']['target_bom_lines']} exact catalogue routes before retained outlier resolution; "
        f"all {data['summary']['target_bom_lines']} sourcing/final-assembly routes mapped; "
        "SA818S-V lead time and J4-F/J4-P factory gates open; "
        "no order or replacement authorized"
    )


if __name__ == "__main__":
    main()
