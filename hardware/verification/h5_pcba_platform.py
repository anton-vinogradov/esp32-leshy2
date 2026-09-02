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
FALLBACK_OUTPUT = REPO / "hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json"
C5_INVARIANT_PATH = REPO / "hardware/architecture/c5-procurement-invariant.json"
DOC_EN = REPO / "docs/manufacturing-platform.md"
DOC_RU = REPO / "docs/manufacturing-platform.ru.md"
CHECKED_ON = "2026-08-31"
C5_INVARIANT = json.loads(C5_INVARIANT_PATH.read_text(encoding="utf-8"))
UPLOAD_AUTHORIZED_ON = "2026-08-25"
SUPPLIER_INQUIRY = {
    "supplier": "JLCPCB",
    "channel": "Contact Us / PCB Assembly Inquiry",
    "submitted_on": "2026-08-26",
    "result": "successfully_submitted",
    "ticket_number": None,
    "scope": "information only; no order, quote project, sourcing request or reservation",
}
SUPPLIER_CLARIFICATION = {
    "supplier": "JLCPCB",
    "channel": "Gmail",
    "submitted_on": "2026-09-01",
    "from": "vinogradov.anton@gmail.com",
    "to": "support@jlcpcb.com",
    "subject": "Re: Leshy2 PCBA and final assembly inquiry — clarification",
    "result": "message_sent",
    "scope": "exactly one prototype; information only; no order, pre-order, quote, reservation, sourcing request or fabrication",
}
SUPPLIER_DISPLAY_PSA_CLARIFICATION = {
    "supplier": "JLCPCB",
    "channel": "Gmail",
    "submitted_on": "2026-09-01",
    "submitted_at_local": "19:25 Europe/Moscow",
    "from": "vinogradov.anton@gmail.com",
    "to": "support@jlcpcb.com",
    "subject": "Re: Leshy2 PCBA and final assembly inquiry — clarification",
    "result": "message_sent",
    "source_reference": "hardware/procurement/H5.0.3-R1-jlcpcb-display-psa-clarification.md",
    "scope": "exact 3M (TC) 4910SQ-2(5), deterministic FPC/ZIF/pressure process and exactly one prototype; information only; no commercial action",
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
            "FH",
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
            "UNI-ROYAL",
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
# consignment. J4-F/J4-P are intentionally outside automated PCBA placement:
# J4-F is installed by the owner from the released procedure, while J4-P is a
# removable/user-installed item. A supplier may optionally quote either task.
OUTLIER_RESOLUTIONS = {
    "SN74LVC1G07DCKR": {"route": "J0", "lcsc": "C7830", "manufacturer": "Texas Instruments"},
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
    "BGS13SN8E6327XTSA1": {"route": "J2", "lcsc": "C55118249", "manufacturer": "Infineon Technologies"},
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
    "2118651-2": {"route": "J4-F", "reason": "two removable 30-mm S3/C5 microcoax jumpers are owner-installed and strain-routed during final sandwich assembly; the released routing and continuity check remain mandatory"},
    "1-2118651-0": {"route": "J4-F", "reason": "three removable 60-mm nRF microcoax jumpers are owner-installed and strain-routed during final sandwich assembly; the released routing and continuity check remain mandatory"},
    "U214 Cap LoRa-1262": {"route": "J4-P", "reason": "removable rear Cap accessory is packed separately for user installation; factory compatibility FCT is not mandatory"},
    "1227-J": {"route": "J4-F", "reason": "encoder knob is owner-installed after enclosure integration; full control bring-up is performed by the owner"},
    "18650 4000mAh": {"route": "J5-U", "reason": "accumulator cells are not part of device delivery; the user separately supplies and installs compatible protected cells"},
}

ROUTE_IDS = ("J0", "J1", "J2", "J3", "J4-F", "J4-P", "J5-U")
J4_FINAL_ASSEMBLY_MPNS = {"2118651-2", "1-2118651-0", "ER-TFT035IPS-6 + ER-TPC035-6", "1227-J"}
J4_PACKED_MPNS = {"U214 Cap LoRa-1262"}
J5_USER_MPNS = {"18650 4000mAh"}
CURRENT_CAPTURE_FREE_OUTLIERS = {"1-2118651-0"}


def bare_mpn(value: str) -> str:
    """Return the orderable identity without the register's maker annotation."""
    normalized = value.strip()
    if normalized == "EastRising ER-TFT035IPS-6 + ER-TPC035-6":
        return "ER-TFT035IPS-6 + ER-TPC035-6"
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
    "pcbway_oem": "https://www.pcbway.com/oem.html",
    "seeed_pcba": "https://www.seeedstudio.com/pcb-assembly.html",
}


JLCAPI_STATE = {
    "application_status": "approved",
    "app_name": "ESP32-Leshy2 BOM Validator",
    "app_status": "enabled",
    "parts_permission_status": "rejected",
    "official_review_basis": [
        "previous JLCPCB orders",
        "company situation",
        "business situation",
    ],
    "exact_rejection_reason_confirmed": False,
    "automatically_listed_permissions": {"PCB": "rejected", "3D": "rejected"},
    "inactive_permissions": ["SMT Stencil", "JLC Balance"],
    "access_key_created": True,
    "tokenization_key_created": False,
    "credential_storage": "local macOS Keychain; no credential is stored in this repository",
    "raw_api_data_publication": False,
    "usable_now": False,
    "support_inquiry": {
        "submitted_on": "2026-08-26",
        "channel": "JLCPCB Contact Us / Others",
        "subject": "Parts API permission rejected — App ID 615135176579813377",
        "result": "successfully_submitted",
        "ticket_number": None,
        "contains_api_secret": False,
        "commercial_authority_granted": False,
        "response_received_on": "2026-08-27",
        "response_author": "JLCPCB customer support; explicitly not a member of the API review team",
        "response": "account is relatively new and has no order history, so JLCPCB cannot verify a clear ongoing business need; build order history and reapply, or submit a more detailed business case/integration plan for possible exception review",
        "exact_order_history_threshold_provided": False,
        "api_review_team_confirmation": False,
        "follow_up_status": "no reapplication submitted; manual catalogue and BOM validation remain authoritative",
    },
    "checked_on": "2026-08-27",
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


CURRENT_EXACT_PART_ROUTES = {
    "RS-06L2R70FT": {
        "device_id": "fh_rs_06l2r70ft",
        "mpn": "FH RS-06L2R70FT",
        "lcsc": "C323265",
        "route": "J0",
        "stock": 3617,
        "available_order_quantity": 3522,
        "minimum_quantity": 1,
        "quantity_one_usd": "0.0084",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/304147-RS06L2R70FT/C323265",
    },
    "U.FL-R-SMT-1(80)": {
        "device_id": "hirose_ufl_r_smt_1_10",
        "mpn": "Hirose U.FL-R-SMT-1(80)",
        "lcsc": "C88374",
        "route": "J0",
        "stock": 72989,
        "available_order_quantity": 68798,
        "minimum_quantity": 1,
        "quantity_one_usd": "0.1016",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/U.FL-R-SMT-1%2880%29/C88374",
    },
    "E01-ML01SP4": {
        "device_id": "ebyte_e01_ml01sp4",
        "mpn": "Ebyte E01-ML01SP4",
        "lcsc": "C97340",
        "route": "J0",
        "stock": 405,
        "available_order_quantity": 388,
        "minimum_quantity": 1,
        "quantity_one_usd": "4.4835",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/E01-ML01SP4/C97340",
    },
    "ER-TFT035IPS-6 + ER-TPC035-6": {
        "device_id": "eastrising_er_tft035ips_6_ctp",
        "mpn": "EastRising ER-TFT035IPS-6 + ER-TPC035-6",
        "lcsc": None,
        "route": "J4-F",
        "stock": "manufacturer_in_stock",
        "available_order_quantity": None,
        "minimum_quantity": 1,
        "quantity_one_usd": "14.91",
        "status": "owner_post_pcba_final_assembly",
        "source": "https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen",
    },
    "FH34SRJ-50S-0.5SH(50)": {
        "device_id": "hirose_fh34srj_50s_0_5sh_50",
        "mpn": "Hirose FH34SRJ-50S-0.5SH(50)",
        "lcsc": "C3169104",
        "route": "J0",
        "stock": 2679,
        "available_order_quantity": 2614,
        "minimum_quantity": 1,
        "quantity_one_usd": "0.5832",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104",
    },
    "SC1512-A4": {
        "device_id": "rp2354b_a4",
        "mpn": "SC1512-A4",
        "factory_alias": "RP2354B",
        "lcsc": "C39843328",
        "route": "J0",
        "stock": 3442,
        "displayed_stock": 3605,
        "available_order_quantity": 3442,
        "minimum_quantity": 1,
        "quantity_one_usd": "1.5658",
        "quantity_ten_usd": "1.4927",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328",
    },
    "MSPM0C1106SDGS20R": {
        "device_id": "ti_mspm0c1106_sdgs20r",
        "mpn": "Texas Instruments MSPM0C1106SDGS20R",
        "lcsc": "C52995805",
        "route": "J2",
        "stock": 0,
        "available_order_quantity": 0,
        "minimum_quantity": 6,
        "quantity_one_usd": "1.1969",
        "status": "pre_order",
        "price_note": "last public quantity-one price snapshot; pre-order final quote remains open",
        "source": "https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805",
    },
    C5_INVARIANT["official_identity"]["mpn"]: {
        "device_id": C5_INVARIANT["official_identity"]["device_id"],
        "mpn": C5_INVARIANT["official_identity"]["mpn"],
        "supplier_order_code": C5_INVARIANT["active_supplier_route"]["supplier_order_code"],
        "lcsc": C5_INVARIANT["active_supplier_route"]["jlcpcb_part_number"],
        "route": C5_INVARIANT["active_supplier_route"]["route"],
        "stock": C5_INVARIANT["active_supplier_route"]["stock"],
        "available_order_quantity": C5_INVARIANT["active_supplier_route"]["available_order_quantity"],
        "minimum_quantity": C5_INVARIANT["active_supplier_route"]["moq"],
        "quantity_one_usd": str(C5_INVARIANT["active_supplier_route"]["price_tiers_usd"][0]["unit_price_usd"]),
        "status": C5_INVARIANT["active_supplier_route"]["status"],
        "source": C5_INVARIANT["active_supplier_route"]["source"],
    },
    **VOICE_PART_ROUTES,
    "74LVC2G126DP,125": {
        "device_id": "nexperia_74lvc2g126dp_125",
        "mpn": "Nexperia 74LVC2G126DP,125",
        "lcsc": "C503392",
        "route": "J0",
        "stock": 155,
        "available_order_quantity": 155,
        "quantity_one_usd": "0.4857",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392",
    },
    "74LVC2G14GV,125": {
        "device_id": "nexperia_74lvc2g14gv_125",
        "mpn": "Nexperia 74LVC2G14GV,125",
        "lcsc": "C426708",
        "route": "J0",
        "stock": 153,
        "available_order_quantity": 35,
        "quantity_one_usd": "0.2010",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708",
    },
    "CC0402KRX7R9BB104": {
        "device_id": "yageo_cc0402krx7r9bb104",
        "mpn": "Yageo CC0402KRX7R9BB104",
        "lcsc": "C131394",
        "route": "J0",
        "stock": 9027089,
        "available_order_quantity": 7796754,
        "quantity_one_usd": "0.0107",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394",
    },
    "0402WGF2201TCE": {
        "device_id": "uniroyal_0402wgf2201tce",
        "mpn": "UNI-ROYAL 0402WGF2201TCE",
        "lcsc": "C25879",
        "route": "J0",
        "stock": 2027222,
        "available_order_quantity": 2027222,
        "quantity_one_usd": "0.0039",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879",
    },
    "0402WGF1333TCE": {
        "device_id": "uniroyal_0402wgf1333tce",
        "mpn": "UNI-ROYAL 0402WGF1333TCE",
        "lcsc": "C25753",
        "route": "J0",
        "stock": 6692,
        "available_order_quantity": 6692,
        "quantity_one_usd": "0.0015",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26496-0402WGF1333TCE/C25753",
    },
    "0402WGF2703TCE": {
        "device_id": "uniroyal_0402wgf2703tce",
        "mpn": "UNI-ROYAL 0402WGF2703TCE",
        "lcsc": "C25770",
        "route": "J0",
        "stock": 156208,
        "available_order_quantity": 156208,
        "quantity_one_usd": "0.0057",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26513-0402WGF2703TCE/C25770",
    },
    "0402WGF5231TCE": {
        "device_id": "uniroyal_0402wgf5231tce",
        "mpn": "UNI-ROYAL 0402WGF5231TCE",
        "lcsc": "C25907",
        "route": "J0",
        "stock": 40861,
        "available_order_quantity": 40861,
        "quantity_one_usd": "0.0061",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26650-0402WGF5231TCE/C25907",
    },
    "0402WGF8201TCE": {
        "device_id": "uniroyal_0402wgf8201tce",
        "mpn": "UNI-ROYAL 0402WGF8201TCE",
        "lcsc": "C25924",
        "route": "J0",
        "stock": 234262,
        "available_order_quantity": 234262,
        "quantity_one_usd": "0.0048",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26667-0402WGF8201TCE/C25924",
    },
    "0402WGF1651TCE": {
        "device_id": "uniroyal_0402wgf1651tce",
        "mpn": "UNI-ROYAL 0402WGF1651TCE",
        "lcsc": "C25869",
        "route": "J0",
        "stock": 5616,
        "available_order_quantity": 5616,
        "quantity_one_usd": "0.0008",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26612-0402WGF1651TCE/C25869",
    },
    "0402WGF1603TCE": {
        "device_id": "uniroyal_0402wgf1603tce",
        "mpn": "UNI-ROYAL 0402WGF1603TCE",
        "lcsc": "C25757",
        "route": "J0",
        "stock": 388017,
        "available_order_quantity": 388017,
        "quantity_one_usd": "0.0026",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757",
    },
    "RS-06K47R0FT": {
        "device_id": "fh_rs_06k47r0ft",
        "mpn": "FH RS-06K47R0FT",
        "lcsc": "C140014",
        "route": "J0",
        "stock": 78058,
        "available_order_quantity": 78058,
        "quantity_one_usd": "0.0062",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014",
    },
    "CC0603KRX7R0BB104": {
        "device_id": "yageo_cc0603krx7r0bb104",
        "mpn": "Yageo CC0603KRX7R0BB104",
        "lcsc": "C113803",
        "route": "J0",
        "stock": 1027658,
        "available_order_quantity": 1027658,
        "quantity_one_usd": "0.0260",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803",
    },
    "CSD87313DMS": {
        "device_id": "ti_csd87313dms",
        "mpn": "Texas Instruments CSD87313DMS",
        "lcsc": "C2863848",
        "route": "J0",
        "stock": 4813,
        "available_order_quantity": 4741,
        "minimum_quantity": 1,
        "quantity_one_usd": "1.0558",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/x/C2863848",
    },
    "TSOP75238TR": {
        "device_id": "vishay_tsop75238tr",
        "mpn": "Vishay TSOP75238TR",
        "lcsc": "C511498",
        "route": "J0",
        "stock": 17,
        "available_order_quantity": 15,
        "minimum_quantity": 1,
        "quantity_one_usd": "1.3011",
        "status": "in_stock",
        "risk": "thin public stock covers the five-device trial only; recheck complete-job stock or pre-order the exact part",
        "source": "https://jlcpcb.com/partdetail/x/C511498",
    },
    "LQW15AN56NG00D": {
        "device_id": "murata_lqw15an56ng00d",
        "mpn": "Murata LQW15AN56NG00D",
        "lcsc": "C167482",
        "route": "J0",
        "stock": 21558,
        "available_order_quantity": 20744,
        "minimum_quantity": 1,
        "quantity_one_usd": "0.0447",
        "status": "in_stock",
        "source": "https://jlcpcb.com/partdetail/x/C167482",
    },
}

# C5's manufacturer identity is unchanged from the historical capture; only
# its current supplier route is normalized to the explicit V1.2 order code.
CURRENT_EXACT_OVERRIDE_MPNS = {
    C5_INVARIANT["official_identity"]["mpn"],
    "SC1512-A4",
    "MSPM0C1106SDGS20R",
}


HISTORICAL_REPLACED_MPNS = {
    "U.FL-R-SMT-1(10)",
    "SA518",
    "HMX035CTFT-001",
    "FH34SRJ-40S-0.5SH(99)",
    "74LVC2G126DC,125",
    "74LVC2G14GW,125",
    "C1005X7R1H104K050BB",
    "RC0402FR-072K2L",
    "RC0402FR-07133KL",
    "RC0402FR-07270KL",
    "RC0402FR-075K23L",
    "RC0402FR-078K2L",
    "RC0402FR-071K65L",
    "CRCW0402160KFKED",
    "RC1206FR-0747RL",
    "C1608X7S2A104K080AB",
    "DF40C(2.0)-40DS-0.4V(58)",
    "DF40C-40DP-0.4V(51)",
    "CSD87313DMST",
    "TSOP75238TT",
    "LQW15AN56NJ00D",
    "E01-ML01IPX",
}
HISTORICAL_MATCHED_REPLACED_MPNS = HISTORICAL_REPLACED_MPNS - {"SA518", "HMX035CTFT-001", "E01-ML01IPX"}
HISTORICAL_PREORDER_REPLACED_MPNS = HISTORICAL_MATCHED_REPLACED_MPNS - {
    "FH34SRJ-40S-0.5SH(99)",
    "U.FL-R-SMT-1(10)",
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
        "role": "optional-full-device-cost-and-convenience-comparison",
        "reason": "official sources confirm turnkey/combo/consigned sourcing, customer approval before component decisions, double-sided mixed PCBA, inspection/customer functional test and OEM final assembly; the sent Leshy2 inquiry is now optional because owner final assembly is accepted",
        "fit": {"double_sided_smt_tht": True, "functional_test": True, "final_device_assembly_class": True, "public_machine_readable_parts_path": False},
    },
    {
        "id": "seeed-fusion",
        "role": "second-source-for-pcba-only",
        "reason": "official PCBA source confirms turnkey sourcing, OPL, double-sided mixed assembly and functional test; the inspected productization deep link returned 404, but final-device assembly is no longer a release gate",
        "fit": {"double_sided_smt_tht": True, "functional_test": True, "public_local_parts_library": True, "final_device_assembly_class": False, "public_machine_readable_parts_path": False},
    },
]


TIERS = [
    {"id": "J0", "name": "public-stock exact", "rule": "exact accepted MPN and JLC number are publicly in stock for Standard PCBA; stock is rechecked at every freeze and order"},
    {"id": "J1", "name": "approved in-stock alternate", "rule": "only a prequalified same-function alternate inside the owning substitution class; never a factory-selected silent substitute"},
    {"id": "J2", "name": "private pre-order stock", "rule": "exact MPN is bought into My Parts Lib before PCBA; public stock may supplement only where JLC rules permit"},
    {"id": "J3", "name": "global sourcing or consignment", "rule": "exact identity is sourced or supplied into the private library and must be received before assembly"},
    {"id": "J4-F", "name": "post-PCBA final assembly", "rule": "the owner installs and connects the part from the deterministic release package; an optional supplier quote may replace this manual step but is not a release gate"},
    {"id": "J4-P", "name": "removable owner-installed item", "rule": "the owner separately sources and installs the removable accessory or antenna; optional factory packing is convenience only"},
    {"id": "J5-U", "name": "user-supplied consumable", "rule": "the item is required for operation but is not part of device delivery, factory assembly, packing or shipping"},
]


SPOT_CHECKS = [
    {"device_id": "fh_rs_06l2r70ft", "mpn": "RS-06L2R70FT", "jlc": "C323265", "tier": "J0", "stock": 3617, "available_order_quantity": 3522, "moq": 1, "quantity_one_usd": 0.0084, "pcba": "SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/304147-RS06L2R70FT/C323265", "finding": "exact 2.7-Ohm +/-1% 250-mW 1206 backlight resistor removes the uncontrolled zero-Ohm cathode path while retaining useful first-prototype brightness"},
    {"device_id": "onsemi_fsusb42_mux", "mpn": "FSUSB42MUX", "jlc": "C11355", "tier": "J0", "stock": 66698, "available_order_quantity": 66045, "moq": 1, "quantity_one_usd": 0.3179, "pcba": "Extended SMT; Economic and Standard; MSL 1", "source": "https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355", "finding": "live 2026-08-30 public-stock route for the exact onsemi MSOP-10; selected without package or pin-topology change"},
    {"device_id": "esp32_s3_wroom_1u_n16r8", "mpn": "ESP32-S3-WROOM-1U-N16R8", "jlc": "C3013946", "tier": "J0", "stock": 14529, "pcba": "Standard only; X-ray required", "source": "https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946", "finding": "exact selected module is directly assembleable"},
    {"device_id": "esp32_c5_wroom_1u_n8r8", "mpn": "ESP32-C5-WROOM-1U-N8R8", "supplier_order_code": "ESP32-C5-WROOM-1U-N8R8-V1.2", "jlc": "C54951858", "tier": "J0", "stock": 460, "available_order_quantity": 440, "moq": 1, "pcba": "SMT; Standard PCBA", "source": "https://jlcpcb.com/partdetail/C54951858", "finding": "official Espressif MPN remains unsuffixed; the supplier code fixes the production route at V1.2 and incoming MD plus eFuse must independently prove revision >=v1.2"},
    {"device_id": "cc1101rgpr", "mpn": "CC1101RGPR", "jlc": "C29953", "tier": "J0", "stock": 14194, "pcba": "Economic and Standard", "source": "https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953", "finding": "exact selected transceiver is directly assembleable"},
    {"device_id": "everest_es8311_qfn20", "mpn": "ES8311", "jlc": "C962342", "tier": "J0", "stock": 96905, "pcba": "Economic and Standard; fixture; MSL3", "source": "https://jlcpcb.com/partdetail/1044199-ES8311/C962342", "finding": "exact selected codec is directly assembleable"},
    {"device_id": "nexperia_74lvc2g126dp_125", "mpn": "74LVC2G126DP,125", "jlc": "C503392", "tier": "J0", "stock": 155, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392", "finding": "exact selected TSSOP package variant is in public stock; same official family, pin map, logic, Ioff and timing as the former DC package"},
    {"device_id": "nexperia_74lvc2g14gv_125", "mpn": "74LVC2G14GV,125", "jlc": "C426708", "tier": "J0", "stock": 153, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708", "finding": "exact selected TSOP package variant has ten-part trial coverage; same official family, pin map, Schmitt thresholds, Ioff and timing as the former GW package"},
    {"device_id": "adi_max17320_g20_t", "mpn": "MAX17320G20+T", "jlc": "C7457895", "tier": "J2", "stock": 0, "pcba": "Extended SMT pre-order", "source": "https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894", "finding": "the exact selected +T order suffix remains on the pre-order route; the stocked C7457894 card names MAX17320G20+ without proving suffix equivalence, so it is not silently accepted"},
    {"device_id": "rp2354b_a4", "mpn": "SC1512-A4", "factory_alias": "RP2354B / SC1512(13)-A4", "jlc": "C39843328", "tier": "J0", "stock": 3442, "displayed_stock": 3605, "moq": 1, "pcba": "SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328", "finding": "live original-manufacturer route; canPresale 3442 is the authoritative assembly availability, displayed stock is 3605, and received A4 marking remains an incoming gate"},
    {"device_id": "ti_mspm0c1106_sdgs20r", "mpn": "MSPM0C1106SDGS20R", "jlc": "C52995805", "tier": "J2", "stock": 0, "pcba": "Extended SMT", "source": "https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805", "finding": "listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation"},
    {"device_id": "ebyte_e01_ml01sp4", "mpn": "E01-ML01SP4", "jlc": "C97340", "tier": "J0", "stock": 405, "available_order_quantity": 388, "moq": 1, "pcba": "Extended SMT; Standard PCBA", "source": "https://jlcpcb.com/partdetail/E01-ML01SP4/C97340", "finding": "exact Chengdu Ebyte PA/LNA module is directly factory-placeable; 20-dBm and ten-land footprint replace the incorrect 0-dBm E01-ML01IPX baseline"},
    {"device_id": "nicerf_sa818s_u_v18", "mpn": "G-NiceRF SA818S-U", "jlc": "C3001549", "tier": "J0", "stock": 68, "pcba": "Standard PCBA", "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549", "finding": "exact selected UHF module is priced and in public stock"},
    {"device_id": "nicerf_sa818s_v_v18", "mpn": "G-NiceRF SA818S-V", "jlc": "C51897911", "tier": "J2", "stock": 0, "pcba": "Standard PCBA pre-order", "source": "https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911", "finding": "exact selected VHF module is priced but stock-zero pre-order; lead time remains open"},
    {"device_id": "eastrising_er_tft035ips_6_ctp", "mpn": "ER-TFT035IPS-6 + ER-TPC035-6 option 5344", "jlc": None, "tier": "J4-F", "stock": "manufacturer in stock", "moq": 1, "quantity_one_usd": "14.91", "pcba": "owner-installed after PCBA with exact ready-cut PSA", "source": "https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen", "finding": "exact configured panel, drawings, 50-contact tail, ILI9488/FT6236 endpoint and price are fixed; received-part FPC dry fit remains before bonding"},
    {"device_id": "hirose_fh34srj_50s_0_5sh_50", "mpn": "FH34SRJ-50S-0.5SH(50)", "jlc": "C3169104", "tier": "J0", "stock": 2679, "available_order_quantity": 2614, "moq": 1, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104", "finding": "exact selected 50-position panel connector is directly placeable; quantity-one price USD 0.5832"},
    {"device_id": "uniroyal_0402wgf1603tce", "mpn": "0402WGF1603TCE", "jlc": "C25757", "tier": "J0", "stock": 388017, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757", "finding": "exact stocked 160-kOhm 0402 replacement preserves the complete audio-attenuator electrical contract and uses a thinner body"},
    {"device_id": "fh_rs_06k47r0ft", "mpn": "RS-06K47R0FT", "jlc": "C140014", "tier": "J0", "stock": 78058, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014", "finding": "exact stocked 47-Ohm 1206 replacement preserves the IR current-limit power, voltage and temperature contract"},
    {"device_id": "yageo_cc0603krx7r0bb104", "mpn": "CC0603KRX7R0BB104", "jlc": "C113803", "tier": "J0", "stock": 1027658, "pcba": "Extended SMT; Economic and Standard; MSL 1", "source": "https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803", "finding": "exact stocked 100-nF 100-V 0603 body; X7R temperature stability is stricter than the replaced X7S class"},
    {"device_id": "ti_csd87313dms", "mpn": "CSD87313DMS", "jlc": "C2863848", "tier": "J0", "stock": 4813, "available_order_quantity": 4741, "moq": 1, "pcba": "Extended SMT; Economic and Standard", "source": "https://jlcpcb.com/partdetail/x/C2863848", "finding": "same production die, WSON-CLIP body, contacts and electrical contract as DMST; DMS changes tape-and-reel quantity only"},
    {"device_id": "vishay_tsop75238tr", "mpn": "TSOP75238TR", "jlc": "C511498", "tier": "J0", "stock": 17, "available_order_quantity": 15, "moq": 1, "pcba": "Extended SMT; Economic and Standard; MSL 4", "source": "https://jlcpcb.com/partdetail/x/C511498", "finding": "same final body, contacts and electrical contract as TT; TR changes tape presentation, so approve CPL rotation/feeder orientation and recheck complete-job stock before order"},
    {"device_id": "murata_lqw15an56ng00d", "mpn": "LQW15AN56NG00D", "jlc": "C167482", "tier": "J0", "stock": 21558, "available_order_quantity": 20744, "moq": 1, "pcba": "Extended SMT; Economic and Standard; MSL 1", "source": "https://jlcpcb.com/partdetail/x/C167482", "finding": "exact 56-nH LQW15AN 0402 body; G tightens inductance tolerance from +/-5% to +/-2% without degrading RF limits"},
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
        if normalized_mpn in CURRENT_EXACT_PART_ROUTES:
            exact_part = CURRENT_EXACT_PART_ROUTES[normalized_mpn]
            common.update(
                {
                    "route": exact_part["route"],
                    "tool_status": exact_part["status"],
                    "match_provenance": "current_exact_jlcpcb_part_page",
                    "lcsc": exact_part["lcsc"],
                    "matched_mpn": normalized_mpn,
                    "supplier_order_code": exact_part.get("supplier_order_code", normalized_mpn),
                    "semantic_mpn_equal": True,
                    "stock_snapshot": exact_part["stock"],
                    "displayed_line_cost_usd": float(exact_part["quantity_one_usd"]),
                    "designators_complete": len(expected_designators) == quantity,
                }
            )
            routes.append(common)
            continue

        record = by_mpn.get(normalized_mpn)
        if record is None:
            if normalized_mpn not in CURRENT_CAPTURE_FREE_OUTLIERS:
                raise KeyError(normalized_mpn)
            common.update(
                {
                    "route": "unresolved",
                    "tool_status": "not_matched",
                    "match_provenance": "new_exact_external_identity_not_present_in_historical_bom_capture",
                    "lcsc": None,
                    "matched_mpn": None,
                    "semantic_mpn_equal": None,
                    "stock_snapshot": None,
                    "displayed_line_cost_usd": None,
                    "designators_complete": len(expected_designators) == quantity,
                }
            )
            routes.append(common)
            continue
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
    current_stocked = sum(part["status"] == "in_stock" for part in CURRENT_EXACT_PART_ROUTES.values())
    summary = {
        "target_lines": len(routes),
        "matched_lines": sum(route["tool_status"] != "not_matched" for route in routes),
        "bom_tool_inherited_matched_lines": inherited["matched_lines"],
        "bom_tool_inherited_in_stock_lines": inherited["in_stock_lines"],
        "bom_tool_inherited_pre_order_lines": inherited["pre_order_lines"],
        "bom_tool_inherited_unmatched_lines": inherited["unmatched_lines"],
        "exact_voice_page_lines": len(VOICE_PART_ROUTES),
        "exact_stocked_replacement_page_lines": current_stocked - 1,
        "unmatched_lines": sum(route["tool_status"] == "not_matched" for route in routes),
        "in_stock_lines": sum(route["tool_status"] == "in_stock" for route in routes),
        "pre_order_lines": sum(route["tool_status"] == "pre_order" for route in routes),
        "parsed_placements": sum(int(row["quantity"]) for row in rows),
        "strict_text_variants": inherited["strict_text_variants"],
        "semantic_mpn_mismatches": inherited["semantic_mpn_mismatches"],
    }
    current_mpns = {bare_mpn(row["mpn"]) for row in rows}
    checks = {
        "historical_capture_is_self_consistent": len(records) == len(by_mpn) == 209
        and inherited["matched_lines"] == 176
        and inherited["unmatched_lines"] == 33,
        "historical_capture_diff_is_exactly_known_replacements_to_current_exact_pages": set(by_mpn) - current_mpns == HISTORICAL_REPLACED_MPNS
        and current_mpns - set(by_mpn) == (set(CURRENT_EXACT_PART_ROUTES) - CURRENT_EXACT_OVERRIDE_MPNS) | CURRENT_CAPTURE_FREE_OUTLIERS
        and CURRENT_EXACT_OVERRIDE_MPNS <= current_mpns & set(by_mpn),
        "all_210_current_lines_returned_once": len(routes) == len(rows) == 210
        and len({route["bom_index"] for route in routes}) == 210,
        "all_current_designator_quantities_and_1050_placements_reconcile": all(
            route["designators_complete"] for route in routes
        ) and summary["parsed_placements"] == 1050,
        "current_exact_route_counts_reconcile": summary["matched_lines"] == 182
        and summary["unmatched_lines"] == 28
        and summary["in_stock_lines"] == 154
        and summary["pre_order_lines"] == 27,
        "both_voice_routes_use_exact_current_jlcpcb_pages": all(
            any(route["normalized_mpn"] == mpn and route["lcsc"] == voice["lcsc"] for route in routes)
            for mpn, voice in VOICE_PART_ROUTES.items()
        ),
        "c5_route_uses_official_identity_and_explicit_v1_2_supplier_code": any(
            route["normalized_mpn"] == C5_INVARIANT["official_identity"]["mpn"]
            and route["lcsc"] == "C54951858"
            and route["supplier_order_code"] == "ESP32-C5-WROOM-1U-N8R8-V1.2"
            and route["tool_status"] == "in_stock"
            for route in routes
        ),
        "stocked_logic_routes_use_exact_current_jlcpcb_pages": all(
            any(
                route["normalized_mpn"] == mpn
                and route["lcsc"] == CURRENT_EXACT_PART_ROUTES[mpn]["lcsc"]
                and route["tool_status"] == "in_stock"
                for route in routes
            )
            for mpn in {"74LVC2G126DP,125", "74LVC2G14GV,125"}
        ),
        "stocked_bypass_route_uses_exact_current_jlcpcb_page": any(
            route["normalized_mpn"] == "CC0402KRX7R9BB104"
            and route["lcsc"] == "C131394"
            and route["tool_status"] == "in_stock"
            for route in routes
        ),
        "six_stocked_resistor_routes_use_exact_current_jlcpcb_pages": all(
            any(
                route["normalized_mpn"] == mpn
                and route["lcsc"] == CURRENT_EXACT_PART_ROUTES[mpn]["lcsc"]
                and route["tool_status"] == "in_stock"
                for route in routes
            )
            for mpn in {
                "0402WGF2201TCE",
                "0402WGF1333TCE",
                "0402WGF2703TCE",
                "0402WGF5231TCE",
                "0402WGF8201TCE",
                "0402WGF1651TCE",
            }
        ),
        "three_new_stocked_passive_routes_use_exact_current_jlcpcb_pages": all(
            any(
                route["normalized_mpn"] == mpn
                and route["lcsc"] == CURRENT_EXACT_PART_ROUTES[mpn]["lcsc"]
                and route["tool_status"] == "in_stock"
                for route in routes
            )
            for mpn in {"0402WGF1603TCE", "RS-06K47R0FT", "CC0603KRX7R0BB104"}
        ),
        "three_cost_normalization_routes_use_exact_current_jlcpcb_pages": all(
            any(
                route["normalized_mpn"] == mpn
                and route["lcsc"] == CURRENT_EXACT_PART_ROUTES[mpn]["lcsc"]
                and route["tool_status"] == "in_stock"
                for route in routes
            )
            for mpn in {
                "CSD87313DMS",
                "TSOP75238TR",
                "LQW15AN56NG00D",
            }
        ),
        "no_semantic_mpn_substitution_observed": summary["semantic_mpn_mismatches"] == 0
        and all(route["semantic_mpn_equal"] is not False for route in routes),
        "no_quote_reservation_or_order_created": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed_match_checks": [key for key, value in checks.items() if not value], "summary": summary})
    return {
        "schema_version": 1,
        "artifact": "H5-EVR05",
        "stage": "H5.0.3-R1",
        "status": "current_210_line_route_join_captured_28_outliers_open",
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
            "local": "retain the 28 current outlier resolutions, including both exact microcoax lengths, and join exact display, connector, RP2354B, MSPM0 pre-order, SA818S-U/V, full-power nRF24 and C5 V1.2 supplier routes before rechecking every current route without substitutions",
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
        selected_catalogue_row = None
        if resolution["route"] in {"J0", "J2"}:
            search = searches[mpn]
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
        "capture_plus_explicit_new_external_identity_covers_all_current_bom_tool_outliers": (set(searches) - HISTORICAL_REPLACED_MPNS - CURRENT_EXACT_OVERRIDE_MPNS) | CURRENT_CAPTURE_FREE_OUTLIERS == set(raw_outliers) == set(OUTLIER_RESOLUTIONS),
        "every_outlier_has_one_route": len(resolved) == len({row["bom_index"] for row in resolved}) == len(OUTLIER_RESOLUTIONS),
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
        "j4f_rows_are_post_pcba_final_assembly_parts": {
            row["normalized_mpn"] for row in final_routes if row["route"] == "J4-F"
        }
        == J4_FINAL_ASSEMBLY_MPNS,
        "j4p_rows_are_factory_packed_removable_parts": {
            row["normalized_mpn"] for row in resolved if row["route"] == "J4-P"
        }
        == J4_PACKED_MPNS,
        "j5u_rows_are_user_supplied_not_delivered_parts": {
            row["normalized_mpn"] for row in resolved if row["route"] == "J5-U"
        }
        == J5_USER_MPNS,
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
        "status": "all_210_routes_mapped_owner_final_assembly_accepted",
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
            "post_pcba_final_assembly": {
                "route": "J4-F",
                "mpns": sorted(J4_FINAL_ASSEMBLY_MPNS),
                "owner_installation_accepted": True,
                "supplier_quote_required": False,
                "gate": "the exact display/PSA/FPC, microcoax, knob and fastener kit must be complete before H7 owner assembly; supplier box-build is optional",
            },
            "factory_packed_removable": {
                "route": "J4-P",
                "mpns": sorted(J4_PACKED_MPNS),
                "accepted_and_quoted": False,
                "gate": "none for H5 release; removable accessories are owner-supplied after delivery unless packing is separately requested later",
            },
            "user_supplied_not_delivered": {
                "route": "J5-U",
                "mpns": sorted(J5_USER_MPNS),
                "accepted_and_quoted": True,
                "gate": "none; accumulator cells are explicitly outside device delivery and supplier scope",
            },
            "not_authorized": ["sourcing request", "quote", "reservation", "purchase", "component replacement", "KiCad placement/routing", "fabrication"],
        },
        "next": {
            "decision_needed": "none: the JLCPCB PCBA supplier gate is answered for exact dual-SA818S/no-silent-substitution and the exact 11.00-mm stop is selected; close H5, then let H6 select the wall-dependent screw length and emit the files needed for the real PCBA quote; final pre-order terms and stock recheck remain order-time gates",
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
    fallback = json.loads(FALLBACK_OUTPUT.read_text(encoding="utf-8"))
    c5_route = C5_INVARIANT["active_supplier_route"]
    c5_policy = C5_INVARIANT["silicon_revision_policy"]
    c5_incoming = C5_INVARIANT["incoming_inspection"]
    forbidden_c5_numbers = {
        row["jlcpcb_part_number"] for row in C5_INVARIANT["forbidden_active_routes"]
    }
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
        "all_target_placements_were_parsed": match_summary["parsed_placements"] == 1050,
        "no_semantic_mpn_substitution_was_observed": match_summary["semantic_mpn_mismatches"] == 0,
        "all_28_current_unmatched_lines_remain_explicit": match_summary["unmatched_lines"] == 28,
        "all_210_lines_have_defined_availability_or_final_assembly_route": outlier_result["summary"]["unmapped_lines"] == 0,
        "all_component_sample_prices_are_known": outlier_result["summary"]["open_qualified_price_lines"] == 0,
        "sa818s_v_preorder_lead_time_is_explicitly_open": outlier_result["summary"]["preorder_lead_time_open_mpn"] == "SA818S-V",
        "owner_final_assembly_removes_factory_box_build_gate": not PLATFORMS[0]["fit"]["final_box_build_proven"],
        "one_prototype_without_batteries_is_the_only_procurement_target": True,
        "factory_function_test_is_optional_not_a_release_gate": True,
        "fallback_factory_readiness_is_current_and_fail_closed": fallback["artifact"] == "H5-EVR08"
        and fallback["gate"] == "H5.0.3-R1"
        and fallback["selection"]["first_fallback"] == "pcbway"
        and fallback["selection"]["second_source_pcba"] == "seeed-fusion"
        and fallback["selection"]["jlcpcb_remains_pcba_reference"]
        and not fallback["selection"]["jlcpcb_remains_primary_full_device_factory"]
        and all(fallback["checks"].values())
        and not any(fallback["authorization"].values()),
        "jlcapi_application_and_app_are_ready": JLCAPI_STATE["application_status"] == "approved"
        and JLCAPI_STATE["app_status"] == "enabled"
        and JLCAPI_STATE["access_key_created"],
        "parts_api_rejection_is_explicit_and_fail_closed": JLCAPI_STATE["parts_permission_status"] == "rejected"
        and not JLCAPI_STATE["usable_now"],
        "parts_api_official_review_basis_is_recorded_without_guessing_the_exact_reason": len(JLCAPI_STATE["official_review_basis"]) == 3
        and not JLCAPI_STATE["exact_rejection_reason_confirmed"],
        "parts_api_support_request_is_recorded_without_secret_or_commercial_authority": JLCAPI_STATE["support_inquiry"]["result"] == "successfully_submitted"
        and not JLCAPI_STATE["support_inquiry"]["contains_api_secret"]
        and not JLCAPI_STATE["support_inquiry"]["commercial_authority_granted"],
        "parts_api_support_response_preserves_manual_fail_closed_route": JLCAPI_STATE["support_inquiry"]["response_received_on"] == "2026-08-27"
        and not JLCAPI_STATE["support_inquiry"]["exact_order_history_threshold_provided"]
        and not JLCAPI_STATE["support_inquiry"]["api_review_team_confirmation"]
        and "manual catalogue" in JLCAPI_STATE["support_inquiry"]["follow_up_status"],
        "both_selected_voice_modules_have_exact_jlcpcb_routes": set(VOICE_PART_ROUTES) == {"SA818S-U", "SA818S-V"}
        and all(row["lcsc"] and row["quantity_one_usd"] for row in VOICE_PART_ROUTES.values()),
        "c5_machine_invariant_binds_official_mpn_to_explicit_v1_2_supplier_route": C5_INVARIANT["invariant_id"] == "C5-PROCUREMENT-IDENTITY-1"
        and C5_INVARIANT["official_identity"]["mpn"] == "ESP32-C5-WROOM-1U-N8R8"
        and c5_route["manufacturer"] == "Espressif Systems"
        and c5_route["jlcpcb_part_number"] == "C54951858"
        and c5_route["supplier_order_code"] == "ESP32-C5-WROOM-1U-N8R8-V1.2"
        and c5_route["pcba_surface"] == "Standard PCBA"
        and c5_route["stock"] == 460
        and c5_route["available_order_quantity"] == 440
        and c5_route["moq"] == 1,
        "c5_revision_and_incoming_policy_is_fail_closed": c5_policy["production_floor"] == "v1.2"
        and c5_policy["engineering_only"] == ["v1.0"]
        and set(c5_policy["rejected"]) == {"v0.1", "unknown"}
        and {row["id"] for row in c5_incoming["checks"]} == {"MD_IDENTITY", "EFUSE_SILICON_REVISION"}
        and "both independent checks" in c5_incoming["acceptance"],
        "historical_c5_catalogue_row_is_forbidden_as_active_route": "C51950748" in forbidden_c5_numbers
        and all(row["lcsc"] not in forbidden_c5_numbers for row in CURRENT_EXACT_PART_ROUTES.values())
        and "ESP32-C5-WROOM-1U-N8R8" not in OUTLIER_RESOLUTIONS,
        "api_credentials_are_not_repository_data": "no credential" in JLCAPI_STATE["credential_storage"]
        and not JLCAPI_STATE["tokenization_key_created"],
        "no_order_or_layout_is_authorized": True,
    }
    if not all(checks.values()):
        raise ValueError({"failed": [key for key, value in checks.items() if not value], "missing": missing})
    return {
        "schema_version": 3,
        "artifact": "H5-EVR04",
        "stage": "H5.0.3-R1",
        "status": "routes_complete_pcba_supplier_gate_passed_h6_and_order_gates_assigned",
        "checked_on": CHECKED_ON,
        "input": {"path": str(BOM.relative_to(REPO)), "sha256": sha256(BOM), "exact_lines": len(rows)},
        "r2_quantity_overlay": {
            "status": "current_h0_r2_authority_over_historical_g2f_bom",
            "device_id": "rp2354b_a4",
            "mpn": "SC1512-A4",
            "factory_alias": "RP2354B",
            "jlcpcb_part": "C39843328",
            "route": "J0",
            "quantity_per_device": 2,
            "evt5_quantity": 10,
            "can_presale": 3442,
            "displayed_stock": 3605,
            "quantity_one_unit_price_usd": 1.5658,
            "quantity_ten_unit_price_usd": 1.4927,
            "evt5_line_cost_usd": 14.927,
            "incoming_gate": "received device must prove A4 marking/stepping; accepted identity RP2354B / SC1512(13)-A4, with SC1512-A4 retained as the controlled project MPN",
            "historical_input_note": "the G2F BOM and its uploaded placement count remain preserved R1 evidence with one RP; a future R2 H2 BOM must materialize both distinct designators before any order",
        },
        "decision": {
            "reference_platform": "JLCPCB Standard PCBA",
            "optional_full_device_comparison": "PCBWay turnkey/box-build response",
            "second_source_quote": "Seeed Fusion",
            "exclusive_lock_in": False,
            "reason": "JLCPCB gives the strongest public, repeatable component-selection surface while retaining exact-part pre-order, global sourcing and consignment paths.",
        },
        "procurement_target": {
            "finished_device_quantity": 1,
            "deliverable": "one owner-assembled Leshy2 prototype built from two factory-populated PCBAs and the released exact owner kit",
            "device_batch": False,
            "batteries_included": False,
            "production_display": "exact EastRising ER-TFT035IPS-6 + ER-TPC035-6 option 5344 selected; owner installs it with exact ready-cut PSA and mates it through factory-populated C3169104 after received-part dry fit",
            "first_power_on": "owner USB-powered bring-up after PCBA receipt and final assembly",
            "factory_function_test": {
                "standard_pcba_service_surface": "supported subject to procedure review and quote",
                "project_use": "optional quote-only insurance",
                "release_gate": False,
            },
            "factory_attrition_rule": "PCBA attrition is quoted by the board assembler; the owner kit intentionally contains one display and one PSA without a sacrificial spare",
        },
        "platforms": PLATFORMS,
        "fallback_factory_evidence": {
            "path": str(FALLBACK_OUTPUT.relative_to(REPO)),
            "sha256": sha256(FALLBACK_OUTPUT),
            "status": fallback["status"],
            "first_fallback": fallback["selection"]["first_fallback"],
            "second_source_pcba": fallback["selection"]["second_source_pcba"],
            "jlcpcb_remains_pcba_reference": fallback["selection"]["jlcpcb_remains_pcba_reference"],
            "jlcpcb_remains_primary_full_device_factory": fallback["selection"]["jlcpcb_remains_primary_full_device_factory"],
            "contact_result": fallback["contact"]["result"],
            "contact_sent_on": fallback["contact"]["sent_on"],
            "contact_from": fallback["contact"]["from"],
            "contact_to": fallback["contact"]["to"],
            "information_only": fallback["contact"]["information_only"],
            "commercial_action_created": fallback["contact"]["commercial_action_created"],
        },
        "availability_tiers": TIERS,
        "assembly_boundary": {
            "inside_pcba": ["both Leshy2 rigid boards", "all ordinary SMT/THT parts accepted by Standard PCBA", "board connectors and soldered RF boundaries when their exact assembly rule is accepted"],
            "J4-F_post_pcba_final_assembly": {
                "status": "owner_assembly_accepted_exact_stop_selected_screw_length_owned_by_h6",
                "required_operations": ["install and mate the documented exact production panel from released drawings", "install, strain-route and continuity-check two exact 30-mm plus three exact 60-mm microcoax jumpers", "encoder knob installation", "final sandwich/enclosure integration from deterministic assembly instructions"],
                "responsible_party": "owner",
                "display_mating_feasibility": "exact endpoint and ready-cut PSA selected; received-part dry fit must confirm FPC length, relaxed bend, contact orientation and stack clearance before bonding",
                "factory_function_test": "optional quote-only insurance; not required for H5/H7 closure",
                "close_gate": "H5 closes the exact display/PSA/microcoax/knob/11-mm-stop identities; H6 selects the enclosure-dependent screw length and creates the quoteable release outputs; H7 executes owner assembly and first power-on; PCBWay box-build is optional",
            },
            "J4-P_factory_packed_removable": {
                "status": "owner_sourced_optional_factory_packing",
                "required_operations": ["owner installs and tests the removable U214 Cap", "owner installs the labelled external antennas"],
            },
            "J5-U_user_supplied_not_delivered": {
                "status": "accepted_project_boundary",
                "items": ["compatible protected 18650 cells"],
                "rule": "not included, assembled, packed, shipped or priced with the device",
            },
        },
        "parts_api": JLCAPI_STATE,
        "supplier_inquiry": SUPPLIER_INQUIRY,
        "supplier_clarification": SUPPLIER_CLARIFICATION,
        "supplier_display_psa_clarification": SUPPLIER_DISPLAY_PSA_CLARIFICATION,
        "voice_part_routes": VOICE_PART_ROUTES,
        "c5_procurement_invariant": {
            "path": str(C5_INVARIANT_PATH.relative_to(REPO)),
            "sha256": sha256(C5_INVARIANT_PATH),
            "official_identity": C5_INVARIANT["official_identity"],
            "silicon_revision_policy": c5_policy,
            "active_supplier_route": c5_route,
            "forbidden_active_routes": C5_INVARIANT["forbidden_active_routes"],
            "incoming_inspection": c5_incoming,
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
            "transmitted": False,
            "processed": False,
            "assembly_quantity": 1,
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
                "result": "historical 209-line capture retained as evidence; the current direct-ZIF BOM is joined without either superseded DF40 part, C5 is rebound to current exact C54951858, and the new exact 60-mm external jumper remains fail-closed in the 210-line map",
            },
            "blocker": "none inside H5: all 210 current lines have defined routes, the JLCPCB exact dual-SA818S/no-silent-substitution PCBA gate is answered, owner final assembly is accepted and exact Ettinger 007.02.611 stops preserve the four-screw stack. H6 owns exact screw length and quoteable Gerber/BOM/CPL; final SA818S-V terms and stock recheck are order-time gates. PCBWay box-build, Function Test and accessory packing are optional; no sourcing request, quote, reservation or order has been created",
        },
        "critical_spot_checks": SPOT_CHECKS,
        "summary": {
            "target_bom_lines": len(rows),
            "critical_lines_spot_checked": len(SPOT_CHECKS),
            "public_stock_exact_or_revision_explicit": sum(row["tier"] == "J0" for row in SPOT_CHECKS),
            "preorder_reservation": sum(row["tier"] == "J2" for row in SPOT_CHECKS),
            "global_sourcing_or_consignment": sum(row["tier"] == "J3" for row in SPOT_CHECKS),
            "post_pcba_final_assembly": sum(row["tier"] == "J4-F" for row in SPOT_CHECKS),
            "factory_packed_removable": sum(row["tier"] == "J4-P" for row in SPOT_CHECKS),
            "user_supplied_not_delivered": sum(row["tier"] == "J5-U" for row in SPOT_CHECKS),
            "historical_bom_tool_matched_lines": match_summary["bom_tool_inherited_matched_lines"],
            "historical_bom_tool_public_stock_lines": match_summary["bom_tool_inherited_in_stock_lines"],
            "historical_bom_tool_preorder_lines": match_summary["bom_tool_inherited_pre_order_lines"],
            "historical_bom_tool_unmatched_lines": match_summary["bom_tool_inherited_unmatched_lines"],
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
            "local": "close H5 and start H6 placement/routing plus enclosure-stack closure; select exact nylon screw length and obtain the real two-PCBA price from H6 outputs, then execute final SA818S-V terms and complete stock recheck immediately before the single order; record any PCBWay response only as an optional comparison",
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
    outlier_count = outlier_result["summary"]["bom_tool_outliers_resolved"]
    outlier_route_counts = {
        route: sum(row["route"] == route for row in outlier_result["outlier_resolutions"])
        for route in ROUTE_IDS
    }
    final_route_counts = outlier_result["summary"]["availability_routes"]
    if russian:
        return f"""# Производственная платформа Leshy2

[English](manufacturing-platform.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

## Базовая линия

**Рабочий reference — JLCPCB Standard PCBA.** Это не эксклюзивная привязка и не разрешение заказа. Standard выбран из-за публичной assembly-библиотеки со stock/JLC-number, двухстороннего SMT+THT, fine-pitch/BGA/QFN, специального stack-up и SPI/AOI/X-ray. [Официальные capabilities]({SOURCES['jlc_capabilities']}) и [варианты sourcing]({SOURCES['jlc_sourcing']}).

Целевой заказ — две фабрично установленные PCBA по MOQ JLCPCB, из которых владелец собирает ровно **один рабочий прототип**, без аккумуляторов в поставке. Фабрика не выбирает схемные или механические решения: production package заранее фиксирует exact panel, его mating, все компоненты и последовательность сборки. Владелец ставит дисплей с готовым PSA, пять microcoax, ручку и крепёж, затем выполняет первый полноценный power-on и USB bring-up.

JLCPCB подтвердил exact dual-designator placement и no-silent-substitution и остаётся основной PCBA-кандидатурой. Его отказ от полной сборки корпуса/устройства больше не блокирует проект, потому что владелец принял контролируемую post-PCBA сборку. [Информационный exact-one запрос PCBWay](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) уже отправлен; ответ даст полезное сравнение цены и удобства, но ждать его для release не нужно. Seeed Fusion остаётся вторым источником PCBA. Ни один запрос не создал quote, sourcing request, reservation, purchase или order.

```mermaid
flowchart TD
  M["Новый MPN"] --> P{"Устанавливается при PCBA?"}
  P -->|да| J0["J0 · exact JLC stock"]
  J0 -->|нет| J1["J1 · квалифицированная замена"]
  J1 -->|нет без деградации| J2["J2 · private pre-order"]
  J2 -->|нет| J3["J3 · global/consign"]
  P -->|нет; ставит владелец| J4F["J4-F · post-PCBA final assembly"]
  P -->|нет; съёмный аксессуар| J4P["J4-P · owner-installed"]
  P -->|не входит в поставку| J5U["J5-U · user-supplied"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  J5U --> F
  F --> R["повторная stock-проверка перед заказом"]
```

## Что значит «доступно всегда»

Ни одна площадка не гарантирует вечный публичный остаток. Для Leshy2 это означает: обычные детали выбираются из JLC stock или имеют заранее квалифицированные замены; уникальные функциональные MPN резервируются в private library через [pre-order]({SOURCES['jlc_private_library']}) или поступают через global sourcing/consignment. Недостаток stock никогда не разрешает фабрике молчаливую замену.

## Контрольный BOM Tool прогон

Контрольный BOM Tool capture относится к прежним 209 строкам: 176 matched, 33 unmatched и 1019 установок. Текущий BOM заменяет `SA518` двумя exact voice-модулями, legacy-дисплей — точным EastRising endpoint, а прежний 0-dBm nRF24 — складским full-power `E01-ML01SP4`. Так получена проверяемая текущая карта `{summary['target_bom_lines']}` строк и `{summary['target_placements_parsed']}` установок без повторной передачи BOM. До применения сохранённых outlier-решений в ней {summary['current_exact_catalogue_routes_before_outlier_resolution']} exact catalogue route и {summary['current_unmatched_lines_before_outlier_resolution']} unresolved lines; семантических подмен MPN — ноль.

Сохранённый exact-поиск закрывает все {outlier_count} оставшихся outlier без замены компонентов: {outlier_route_counts['J0']} добавлены в `J0`, {outlier_route_counts['J2']} — в `J2`, {outlier_route_counts['J3']} сохраняют точный MPN через `J3`, {outlier_route_counts['J4-F']} входят в контролируемую post-PCBA сборку владельца `J4-F`, U214 идёт через owner-installed `J4-P`, а аккумуляторы — через `J5-U` вне поставки. Точный EastRising-дисплей уже входит отдельным прямым маршрутом `J4-F`. Итог всей BOM: `J0={final_route_counts['J0']}`, `J1={final_route_counts['J1']}`, `J2={final_route_counts['J2']}`, `J3={final_route_counts['J3']}`, `J4-F={final_route_counts['J4-F']}`, `J4-P={final_route_counts['J4-P']}`, `J5-U={final_route_counts['J5-U']}`; несопоставленных строк — ноль.

Показываемая в историческом BOM Tool capture сумма `$1255.6365` относится только к прежним 176 найденным строкам и **не** является текущей полной ценой сборки, quote или заказом. Актуальный order-integrated article manifest единственного прототипа посчитан на [странице manifest](component-sample-basket.ru.md); отдельной закупки образцов/coupons нет.

<details>
<summary>Как разрешены {outlier_count} оставшихся outlier</summary>

{outlier_table(outlier_result, True)}

</details>

## Независимая проверка критических деталей

До bulk-прогона отдельно проверены `{summary['critical_lines_spot_checked']}` критических идентичностей. Их stock-снимки не заменяют текущий BOM Tool результат и не обещают постоянную доступность.

{table(data, True)}

## Граница сборки

JLCPCB Standard PCBA собирает обе платы и принятые SMT/THT-компоненты; exact dual-SA818S placement и запрет молчаливой замены подтверждены. PCBA MOQ равен 2. Точный `ER-TFT035IPS-6 + ER-TPC035-6` option 5344, готовый PSA и пять microcoax устанавливает владелец по release-инструкции; точные 11-мм упоры `Ettinger 007.02.611` сохраняют четыре проходных пластиковых M2.5-винта, длину которых фиксирует H6 после размеров корпуса. Отказ JLCPCB от box-build и post-order review special process больше не являются gate. Function Test и ответ PCBWay остаются optional.

| Маршрут | Обязательная операция | Статус |
|---|---|---|
| `J4-F` | Владелец устанавливает и стыкует exact `ER-TFT035IPS-6 + ER-TPC035-6` через `C3169104`, фиксирует две 30-мм и три 60-мм microcoax, ставит ручку энкодера и собирает корпус/«бутерброд» по release-инструкции | ✅ Роль принята; точные 11-мм упоры `Ettinger 007.02.611` выбраны; H6 фиксирует зависящую от стенок длину M2.5 nylon-винтов; received-part dry fit дисплея выполняется до наклейки |
| `J4-P` | U214 и внешние антенны остаются съёмными аксессуарами, которые владелец приобретает и устанавливает после доставки | ✅ Необязательная упаковка фабрикой не является release gate |
| `J5-U` | Пользователь отдельно приобретает и устанавливает совместимые защищённые 18650 | ✅ Принятая граница продукта: аккумуляторы не входят в поставку устройства |

`J4-F` фиксирует обязательный результат post-PCBA сборки владельца; box-build подрядчик может выполнить его только как необязательную услугу. `J4-P` сохраняется как классификация съёмных аксессуаров.

## Два точных voice-маршрута

`SA818S-U` связан с exact `C3001549`: stock 68, available quantity 60, цена одного `$9.7347`. `SA818S-V` связан с exact `C51897911`: stock 0, MOQ 1, цена одного `$10.0710`, маршрут `J2` pre-order. `SA818S-CE C19632390` остаётся только qualified-pending UHF-заменой и не входит в production BOM: она требует HIL и firmware clamp 470 МГц, не заменяет VHF и никогда не подставляется молча.

## C5: MPN, поставщик и ревизия

Официальный MPN остаётся `ESP32-C5-WROOM-1U-N8R8`. Суффикс есть только в supplier order code `ESP32-C5-WROOM-1U-N8R8-V1.2`: активный маршрут — Espressif `C54951858`, Standard PCBA, stock 460, available 440, MOQ 1. Прежний `C51950748` запрещён как active route. Для production одновременно обязательны MD/lot identity и eFuse readback `>=v1.2`; `v1.0` допускается только как явно помеченный engineering specimen, `v0.1`, unknown и любое расхождение изолируются.

## Текущий результат

- JLCPCB Standard PCBA сохранён как основная PCBA-кандидатура без lock-in; full-device роль не требуется.
- Все `{summary['target_bom_lines']}` строк имеют определённый маршрут `J0`–`J3`, `J4-F`, `J4-P` или `J5-U`; функциональных замен нет.
- [Ответ JLCPCB от 2 сентября](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md) подтверждает exact `SA818S-V C51897911` и `SA818S-U C3001549` на разных designator через BOM Matching, exact-MPN incoming control и запрет замены без подтверждения. Он задаёт PCBA MOQ 2 и не поддерживает complete enclosure assembly, но [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) теперь закрывает PCBA supplier gate: дисплей/PSA, microcoax, ручка и корпус приняты как owner assembly. Письмо пришло в исходный тикет на `av@apache.org` и отображается в Gmail-аккаунте `no.mail.in@gmail.com`.
- Заявка JLCAPI одобрена, приложение `ESP32-Leshy2 BOM Validator` создано, ключ подписи хранится только локально вне Git, но право Parts остаётся `Rejected`. [Поддержка ответила](../hardware/procurement/H5.0.3-R1-parts-api-support-inquiry.md), что аккаунт новый и не имеет истории заказов, поэтому устойчивую business need пока не удалось подтвердить; повторная заявка возможна после появления истории либо с расширенным business case/integration plan. Автор ответа отдельно указал, что не входит в API review team, и точный порог заказов не назван. Повторная заявка не отправлена: до фактического одобрения API-вызовы невозможны, а активным авторитетным путём остаются ручные карточки каталога и BOM. PCB/3D также отклонены, SMT Stencil и JLC Balance выключены.
- [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json) сохраняет PCBWay как необязательное сравнение box-build цены/удобства, а Seeed — вторым источником PCBA. [No-order запрос PCBWay](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) уже отправлен; его ответ будет записан, но не блокирует H6.
- Прежний 209-строчный BOM upload был передан и обработан; текущий 210-строчный direct-ZIF файл сгенерирован локально, но не передавался. Оба устаревших DF40 удалены; актуальный C5 route и новый внешний 60-мм microcoax проверены отдельно. H5 не выполнял quote, sourcing request, reservation, покупку, замены, KiCad layout или fabrication; H6 теперь владеет layout, а все коммерческие действия и печать остаются заблокированы. Сырые API-ответы публично не распространяются.

Машинные результаты: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json), [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json) и [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json). [Требования JLCPCB к BOM]({SOURCES['jlc_bom_format']}).
"""
    return f"""# Leshy2 manufacturing platform

[Русский](manufacturing-platform.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

## Reference line

**The working reference is JLCPCB Standard PCBA.** This is neither exclusive lock-in nor order authorization. Standard was selected for its public stock/JLC-number assembly library, double-sided SMT+THT, fine-pitch/BGA/QFN, special stackups and SPI/AOI/X-ray. See the official [assembly capabilities]({SOURCES['jlc_capabilities']}) and [parts-sourcing paths]({SOURCES['jlc_sourcing']}).

The procurement target is two factory-populated PCBAs under JLCPCB's MOQ, from which the owner assembles exactly **one working prototype**, with no batteries in delivery. The factory makes no electrical or mechanical design choices: the production package first fixes the exact panel, mating, components and assembly sequence. The owner installs the display with ready-cut PSA, five microcoax jumpers, knob and fasteners, then performs first full power-on and USB bring-up.

JLCPCB confirmed exact dual-designator placement and no silent substitution and remains the primary PCBA candidate. Its refusal of complete enclosure/final-device assembly no longer blocks the project because controlled owner post-PCBA assembly is accepted. The [information-only exact-one PCBWay inquiry](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) has already been sent; its reply will provide a useful cost/convenience comparison but is not awaited for release. Seeed Fusion remains a PCBA second source. No inquiry created a quote, sourcing request, reservation, purchase or order.

```mermaid
flowchart TD
  M["New MPN"] --> P{"Placed during PCBA?"}
  P -->|yes| J0["J0 · exact JLC stock"]
  J0 -->|no| J1["J1 · qualified alternate"]
  J1 -->|no non-degrading alternate| J2["J2 · private pre-order"]
  J2 -->|no| J3["J3 · global/consign"]
  P -->|no; owner installs| J4F["J4-F · post-PCBA final assembly"]
  P -->|no; removable accessory| J4P["J4-P · owner-installed"]
  P -->|not delivered| J5U["J5-U · user-supplied"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  J5U --> F
  F --> R["stock recheck before every order"]
```

## Meaning of “always available”

No platform guarantees perpetual public stock. Leshy2 therefore selects ordinary parts from JLC stock or with prequalified alternates; unique functional identities are reserved in the [private parts library]({SOURCES['jlc_private_library']}) or received through global sourcing/consignment. A shortage never permits a silent factory substitution.

## Controlled BOM Tool run

The controlled BOM Tool capture belongs to the former 209-line BOM: 176 matched, 33 unmatched and 1019 placements. The current BOM replaces `SA518` with two exact voice modules, the legacy display with the exact EastRising endpoint, and the former 0-dBm nRF24 with the stocked full-power `E01-ML01SP4`. This yields a checkable current map of `{summary['target_bom_lines']}` lines and `{summary['target_placements_parsed']}` placements without retransmitting the BOM. Before applying the retained outlier resolutions it has {summary['current_exact_catalogue_routes_before_outlier_resolution']} exact catalogue routes and {summary['current_unmatched_lines_before_outlier_resolution']} unresolved lines; zero semantic MPN substitutions were observed.

The retained exact search resolves all {outlier_count} remaining outliers without component replacement: {outlier_route_counts['J0']} are added to `J0`, {outlier_route_counts['J2']} to `J2`, {outlier_route_counts['J3']} retain the exact MPN through `J3`, {outlier_route_counts['J4-F']} use controlled owner post-PCBA assembly `J4-F`, U214 uses owner-installed `J4-P`, and accumulators use out-of-delivery `J5-U`. The exact EastRising display already enters through its direct `J4-F` route. The whole-BOM result is `J0={final_route_counts['J0']}`, `J1={final_route_counts['J1']}`, `J2={final_route_counts['J2']}`, `J3={final_route_counts['J3']}`, `J4-F={final_route_counts['J4-F']}`, `J4-P={final_route_counts['J4-P']}`, `J5-U={final_route_counts['J5-U']}`; zero lines remain unmapped.

The `$1255.6365` displayed in the historical BOM Tool capture covers only its former 176 matched lines and is **not** a current complete assembly price, quote or order. The sole prototype's order-integrated article manifest is calculated on the [manifest page](component-sample-basket.md); there is no separate sample/coupon purchase.

<details>
<summary>How the {outlier_count} remaining outliers were resolved</summary>

{outlier_table(outlier_result, False)}

</details>

## Independent critical-part check

`{summary['critical_lines_spot_checked']}` critical identities were checked independently before the bulk run. Their stock snapshots neither override the current BOM Tool result nor promise permanent availability.

{table(data, False)}

## Assembly boundary

JLCPCB Standard PCBA assembles both boards and accepted SMT/THT parts; exact dual-SA818S placement and no silent substitution are confirmed. PCBA MOQ is 2. The owner installs exact `ER-TFT035IPS-6 + ER-TPC035-6` option 5344, ready-cut PSA and five microcoax jumpers from the released procedure; exact 11-mm `Ettinger 007.02.611` stops preserve four pass-through plastic M2.5 screws, whose length H6 locks after enclosure dimensions. JLCPCB's box-build refusal and post-order-only special-process review are no longer gates. Function Test and the PCBWay response remain optional.

| Route | Required operation | Status |
|---|---|---|
| `J4-F` | The owner installs and mates exact `ER-TFT035IPS-6 + ER-TPC035-6` through `C3169104`, secures two 30-mm and three 60-mm microcoax jumpers, fits the encoder knob and integrates the enclosure/sandwich from the released procedure | ✅ Role accepted; exact `Ettinger 007.02.611` 11-mm stops selected; H6 owns wall-dependent M2.5 nylon screw length; received-part display dry fit precedes bonding |
| `J4-P` | U214 and the external antennas remain removable accessories sourced and installed by the owner after delivery | ✅ Optional factory packing is not a release gate |
| `J5-U` | User separately buys and installs compatible protected 18650 cells | ✅ Accepted product boundary: accumulators are not included in device delivery |

`J4-F` defines the required owner post-PCBA assembly result; a box-build contractor may perform it only as an optional service. `J4-P` remains the removable-accessory classification.

## Two exact voice routes

`SA818S-U` is bound to exact `C3001549`: stock 68, available quantity 60 and one-piece price `$9.7347`. `SA818S-V` is bound to exact `C51897911`: stock 0, MOQ 1, one-piece price `$10.0710` and route `J2` pre-order. `SA818S-CE C19632390` remains only a qualified-pending UHF alternate and is not in the production BOM: it requires HIL and a 470-MHz firmware clamp, never replaces VHF and is never substituted silently.

## C5 MPN, supplier and revision

The official MPN remains `ESP32-C5-WROOM-1U-N8R8`. Only the supplier order code carries the suffix: `ESP32-C5-WROOM-1U-N8R8-V1.2`. The active route is Espressif `C54951858`, Standard PCBA, stock 460, available 440 and MOQ 1; former `C51950748` is forbidden as an active route. Production requires both MD/lot identity and eFuse readback `>=v1.2`; `v1.0` is engineering-only, while `v0.1`, unknown identity and any mismatch are quarantined.

## Current result

- JLCPCB Standard PCBA remains the primary PCBA candidate without lock-in; no full-device factory role is required.
- All `{summary['target_bom_lines']}` lines have a defined `J0`–`J3`, `J4-F`, `J4-P` or `J5-U` route; no functional replacement was introduced.
- JLCPCB's [2 September response](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md) confirms exact `SA818S-V C51897911` and `SA818S-U C3001549` at separate designators through BOM Matching, exact-MPN incoming control and no replacement without confirmation. It sets PCBA MOQ 2 and does not support complete enclosure assembly, but [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) now closes the PCBA supplier gate because display/PSA, microcoax, knob and enclosure are accepted owner assembly. The reply went to `av@apache.org` and is visible in Gmail account `no.mail.in@gmail.com`.
- The JLCAPI application is approved, the `ESP32-Leshy2 BOM Validator` app exists, and its signing key is stored locally outside Git, but Parts permission remains `Rejected`. [Support replied](../hardware/procurement/H5.0.3-R1-parts-api-support-inquiry.md) that the account is new and has no order history, so an ongoing business need could not yet be verified; reapplication is possible after building history or with a fuller business case/integration plan. The responder explicitly is not on the API review team and supplied no exact order threshold. No reapplication was submitted: API calls remain unusable, and live manual catalogue cards plus BOM validation remain authoritative. PCB/3D are also rejected; SMT Stencil and JLC Balance remain inactive.
- [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json) retains PCBWay as an optional box-build cost/convenience comparison and Seeed as the PCBA second source. The [no-order PCBWay questionnaire](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) has been sent; its reply will be recorded but does not block H6.
- The former 209-line BOM upload was transmitted and processed; the current 210-line direct-ZIF file was generated locally but not transmitted. Both superseded DF40 parts are removed; the refreshed C5 route and the new external 60-mm microcoax were checked separately. H5 performed no quote, sourcing request, reservation, purchase, KiCad layout or fabrication; H6 now owns layout, while every commercial action and fabrication remain locked. Raw API responses are not redistributed publicly.

Machine results: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json), [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json) and [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json). [JLCPCB BOM requirements]({SOURCES['jlc_bom_format']}).
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
        "JLCPCB PCBA supplier gate accepted; owner final assembly adopted; PCBWay response optional; "
        "no order or replacement authorized"
    )


if __name__ == "__main__":
    main()
