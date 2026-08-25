#!/usr/bin/env python3
"""Generate the deduplicated H5.0.3 engineering-sample basket and contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
RESIDUAL_MAP = REPO / "hardware/verification/generated/H5-EVR01-residual-map.json"
SOURCE_RESEARCH = REPO / "hardware/verification/generated/H5-EVR02-source-research.json"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR03-irreducible-sample-basket.json"
DOC_EN = REPO / "docs/component-sample-basket.md"
DOC_RU = REPO / "docs/component-sample-basket.ru.md"
LEGACY_PLAN = REPO / "hardware/procurement/pre-kicad-sample-plan.md"
CHECKED_ON = "2026-08-25"


def article(
    identity: str,
    group: str,
    mpn: str,
    quantity: int,
    unit_price: str | None,
    price_kind: str,
    source_label: str,
    source_url: str,
    availability: str,
    coverage: list[str],
    minimum_basis: str,
    *,
    order_unit: str = "piece",
    contained_pieces: int = 1,
    source_price: dict | None = None,
    risk: str | None = None,
) -> dict:
    subtotal = None if unit_price is None else Decimal(unit_price) * quantity
    return {
        "id": identity,
        "group": group,
        "mpn": mpn,
        "order_quantity": quantity,
        "order_unit": order_unit,
        "contained_pieces_per_order_unit": contained_pieces,
        "pricing": {
            "kind": price_kind,
            "unit_usd": unit_price,
            "subtotal_usd": None if subtotal is None else f"{subtotal:.3f}",
            "source_price": source_price,
        },
        "source": {
            "label": source_label,
            "url": source_url,
            "checked_on": CHECKED_ON,
            "availability": availability,
        },
        "coverage": coverage,
        "minimum_quantity_basis": minimum_basis,
        "risk": risk,
        "purchase_authorized": False,
    }


ARTICLES = [
    article("display-donor", "display", "Elecrow DLE06235B / QDtech ES3C35P donor containing HMX035CTFT-001", 2, "20.90", "published_usd", "Elecrow current complete-board page", "https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html", "listed in stock", ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "one retained intact electrical/visual reference and one sacrificial tail/adapter specimen; the former five-donor plan added three unneeded spares"),
    article("display-zif", "display", "Hirose FH34SRJ-40S-0.5SH(99)", 1, "3.40", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Hirose-Connector/FH34SRJ-40S-0.5SH99", "orderable exact MPN", ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "one repeated-mating adapter coupon uses one panel ZIF; failure means the test fails rather than consuming a hidden spare"),
    article("display-df40-receptacle", "display", "Hirose DF40C(2.0)-40DS-0.4V(58)", 1, "1.36", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Hirose-Connector/DF40C2.0-40DS-0.4V58", "orderable exact MPN", ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL"], "one fixed receptacle is sufficient for the single display-adapter coupon"),
    article("display-df40-plug", "display", "Hirose DF40C-40DP-0.4V(51)", 1, "1.01", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Hirose-Connector/DF40C-40DP-0.4V51", "orderable exact MPN", ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL"], "one plug is sufficient for the single display-adapter coupon"),

    article("u214", "expansion", "M5Stack U214 Cap LoRa-1262", 1, "14.50", "published_usd", "M5Stack official store", "https://shop.m5stack.com/products/cap-lora-1262", "listed in stock", ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "the same non-destructive unit closes identity, dimensions, mating and functional checks"),
    article("u214-host-socket", "expansion", "Samtec HLE-107-02-G-DV-PE-LC", 1, "3.338", "published_usd", "Samtec exact product page", "https://www.samtec.com/products/hle-107-02-g-dv-pe-lc", "manufacturer orderable", ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "one production host socket is the actual mixed-pair mate; the former quantity five was spare stock, not evidence"),
    article("m5-host-header-pack", "expansion", "Seeed 114020164 / 1125R-SMT-4P", 1, "2.80", "published_usd", "Seeed official store", "https://www.seeedstudio.com/Grove-Female-Header-SMD-4P-2.0mm-90D-20Pcs-p-4590.html", "listed in stock", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one is needed, but the exact serial connector is sold as a smallest 20-piece pack", order_unit="20-piece pack", contained_pieces=20),
    article("m5-short-cable", "expansion", "M5Stack A034-G", 1, "3.95", "published_usd", "M5Stack official store", "https://shop.m5stack.com/products/4pin-buckled-grove-cable", "orderable", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack supplies the short-profile test article", order_unit="pack"),
    article("m5-boundary-cable", "expansion", "M5Stack A034-B", 1, "2.59", "published_usd", "authorized-distributor exact SKU listing", "https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/A034-B/13974037", "orderable", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack supplies the boundary-length test article", order_unit="pack"),
    article("m5-instrument-cable", "expansion", "M5Stack A096", 1, "4.50", "published_usd", "DigiKey exact-SKU listing", "https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/A096/18084377", "authorized stock", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack exposes the admitted profiles to instruments", order_unit="pack"),

    article("nrf-modules", "rf", "Ebyte E01-ML01IPX", 3, "2.37", "published_usd", "RobotShop, sold and fulfilled by Ebyte", "https://www.robotshop.com/products/ebyte-e01-ml01ipx-frequency-hopping-nrf24l01p-high-speed-24g-rf-wireless-100mw-24ghz-nrf24l01-tx-rx-module", "98 shown in stock", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS"], "exactly three modules are required to prove simultaneous full RX, TX and mixed operation; no untouched spare"),
    article("rf-jumpers", "rf", "TE Connectivity 2118651-2", 5, "2.52", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2118651-2/16538824", "3,082 shown in stock", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"], "five real paths exist: S3, C5 and three nRF24; every installed bend/retention path must be represented"),
    article("rf-board-receptacles", "rf", "Hirose U.FL-R-SMT-1(10)", 5, "1.67", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/U-FL-R-SMT-1-10/2391570", "319,443 shown in stock", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"], "one board mate per selected 30-mm jumper path"),
    article("edge-sma", "rf", "GCT RFPC-SMA31-FN-175-A", 4, "3.39", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/gct/RFPC-SMA31-FN-175-A/25576371", "638 shown in stock", ["H3-PHY-053", "H3-PHY-057", "H5-MECH-NRF-GEN1-FEEDS"], "three nRF24 boundaries plus one AM/LW receive boundary; the S3/C5 module cables use their separately selected SMA32 path"),
    article("voice-module", "rf", "NiceRF SA518", 1, None, "manufacturer_rfq", "NiceRF manufacturer product/RFQ page", "https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html", "current product; public manufacturer price absent", ["H5-MECH-SA518-LAND-FIT"], "one module is enough for land-fit, thermal, conducted RF, audio and fault testing; a spare does not add a distinct claim", risk="Manufacturer quote and exact production-variant confirmation remain open. Third-party marketplace stock is not accepted as identity-controlled supply."),

    article("navigation-and-direct-switches", "controls", "Omron B3S-1100P", 16, "0.90", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3S-1100P/368393", "33,862 shown in stock", ["H5-MECH-NAVIGATION-CONTROLS", "H5-MECH-DIRECT-PRESS-CONTROLS"], "five navigation positions plus BACK, OPT, F1-F8 and PTT must all be populated simultaneously to test spacing and enclosure actuation"),
    article("encoder", "controls", "Alps Alpine EC11E18244AU", 1, "4.90", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Alps-Alpine/EC11E18244AU", "966 shown in stock", ["H5-MECH-ENCODER-KNOB"], "one assembled encoder/knob path closes the only encoder gate"),
    article("encoder-knob", "controls", "Davies Molding 1227-J", 1, "1.58", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Davies-Molding/1227-J", "524 shown in stock", ["H5-MECH-ENCODER-KNOB"], "one exact production knob mates to the one encoder specimen"),
    article("run-kill-switch", "controls", "C&K JS102011SCQN", 1, "1.11", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/c-k/JS102011SCQN/7355835", "535 shown in stock", ["H5-MECH-RUN-KILL"], "one switch/aperture path closes force, detent and endurance evidence"),

    article("cell-holder", "power", "Keystone 1048P", 1, "11.19", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Keystone-Electronics/1048P", "145 shown in stock", ["H5-MECH-CELL-HOLDER-FIT"], "one holder is the actual two-cell mechanism"),
    article("protected-cells", "power", "XTAR protected 18650 4000 mAh 10 A", 2, "14.50", "published_usd", "XTAR official store", "https://xtardirect.com/products/xtar-high-capacity-36v-18650-4000mah-10a-protected-lithium-ion-battery", "98 shown in stock", ["H5-MECH-CELL-HOLDER-FIT"], "one matched same-lot pair is the only admitted operating pack; mixed MPN, lot, age or state of charge remains forbidden"),
    article("pack-gauges", "power", "Analog Devices MAX17320G20+T", 2, "6.19", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Analog-Devices-Maxim-Integrated/MAX17320G20%2BT", "7,638 shown in stock", ["H3-PHY-028"], "one retained golden device and one sacrificial device sequenced through blank, corrupt and exhausted-write states; four dedicated chips are unnecessary"),

    article("speaker", "audio", "PUI Audio AS02404PO", 1, "3.97", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/product-highlight/p/pui-audio/as-series-high-quality-speakers", "421 immediate units shown", ["H5-MECH-ACOUSTIC-PATHS"], "one final-cavity specimen closes the speaker path"),
    article("microphone", "audio", "Same Sky CMEJ-0413-42-SMT-TR", 1, "0.64", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMEJ-0413-42-SMT-TR/10253447", "12,929 shown in stock", ["H5-MECH-ACOUSTIC-PATHS"], "one downward microphone path closes response, sealing and feedback checks"),
    article("headset-jack", "audio", "Same Sky SJ-43504-SMT-TR", 1, "1.29", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Same-Sky/SJ-43504-SMT-TR", "5,344 shown in stock", ["H5-MECH-HEADSET-JACK"], "one repeated CTIA/TRS mating specimen closes the only jack gate"),

    article("ir-demod", "ir", "Vishay TSOP75238TT", 1, "1.46", "published_usd", "DigiKey exact-MPN cut-tape listing", "https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/TSOP75238TT/4075864", "13 shown in cut-tape stock", ["H3-PHY-024"], "one received robust-demodulator channel; the full-reel-only TSOP95238TT is no longer selected"),
    article("ir-carrier", "ir", "Vishay TSMP95000TT", 1, "2.00", "conservative_budget_cap_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Vishay-Semiconductors/TSMP95000TT", "4,182 shown in cut-tape stock", ["H3-PHY-024"], "one independent carrier-learning channel", source_price={"currency": "AUD", "unit": "2.86", "note": "USD 2.00 is a conservative engineering budget cap, not a claimed converted distributor price"}),
    article("ir-emitter", "ir", "Vishay VSMY14940", 1, "2.00", "conservative_budget_cap_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VSMY14940/4071416", "4,872 shown in cut-tape stock", ["H3-PHY-024"], "one actual emitter is sufficient for optical, current and temperature evidence", source_price={"currency": "INR", "unit": "92.62", "note": "USD 2.00 is a conservative engineering budget cap, not a claimed converted distributor price"}),

    article("reference-microsd", "storage", "SanDisk SDSQQNR-032G-GN6IA", 1, "40.05", "published_usd", "TME exact-MPN listing", "https://www.tme.com/in/en/details/sdsqqnr-032g-gn6ia/memory-cards/sandisk/", "200 shown in stock", ["H3-PHY-038"], "one identity-controlled reference medium is sufficient for CMD6, throughput, stalls and buffer traces"),

    article("amlw-core", "amlw-pod", "Fair-Rite 3061990901", 1, "2.70", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Fair-Rite/3061990901", "1,792 shown in stock", ["H3-PHY-057"], "one controlled first-pod core is measured and wound"),
    article("amlw-plug", "amlw-pod", "Adam Tech RF2-154-T-17-50-G", 1, "3.76", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/adam-tech/RF2-154-T-17-50-G/9831243", "839 shown in stock", ["H3-PHY-057"], "one male plug mates to the one AM/LW device boundary"),
    article("amlw-wire", "amlw-pod", "Remington 38SNSP.125", 1, "13.33", "published_usd", "Remington Industries official store", "https://www.remingtonindustries.com/magnet-wire/magnet-wire-38-awg-enameled-copper-6-spool-sizes/", "smallest exact-wire spool orderable", ["H3-PHY-057"], "one smallest spool supplies the controlled winding and measurement retries", order_unit="spool"),
]


MEASUREMENTS = [
    {"id": "H5-MSR-DISPLAY", "articles": ["display-donor", "display-zif", "display-df40-receptacle", "display-df40-plug"], "evidence": ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "method": "retain one donor intact; photograph both lots; disassemble the second; measure flex outline, pitch, thickness, contact side, stiffener and bend keepout; cycle the exact adapter; then record QSPI/touch identity, VDD/VDDI ramps, reset/IRQ, backlight current, temperature and optical response", "pass_rule": "the current HMX035CTFT-001 tail fits and retains in a replaceable adapter without changing the UI PCB/enclosure datum, and the complete measured display path meets every inherited H3 timing/power rule", "artifacts": "dimensioned photos, raw measurements, continuity matrix, logic/power traces and signed record"},
    {"id": "H5-MSR-U214", "articles": ["u214", "u214-host-socket"], "evidence": ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "method": "measure the fitted U214 posts and exact HLE; record all 14 continuities, bottoming, insertion/withdrawal force, repeated cycles, rail preload and screw retention", "pass_rule": "the mixed U214/HLE pair mates without yield or bottoming, retains every contact and preserves the protected hot-plug sequence", "artifacts": "metrology, force/cycle CSV, continuity log and installed photos"},
    {"id": "H5-MSR-M5", "articles": ["m5-host-header-pack", "m5-short-cable", "m5-boundary-cable", "m5-instrument-cable"], "evidence": ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "method": "measure connector/cable geometry and run I2C, UART, GPIO and 1-Wire profiles through TXS0102 at short and boundary lengths with the breakout attached", "pass_rule": "insertion, retention, strain relief, pull networks and waveforms satisfy each admitted profile; unsupported motor/actuator loads remain excluded", "artifacts": "cable photos/lengths, force/cycle records and oscilloscope captures"},
    {"id": "H5-MSR-RF5", "articles": ["nrf-modules", "rf-jumpers", "rf-board-receptacles", "edge-sma"], "evidence": ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"], "method": "inspect all E01 factory receptacles; assemble five straight U.FL-to-U.FL cable paths and four edge SMA boundaries; measure bend, retention and S-parameters; run all three nRF24 simultaneously in full RX, TX and mixed modes with every inactive interface hardware-quiet", "pass_rule": "all five paths meet inherited loss/match and retention limits, all three nRF24 meet concurrent deadlines without neighbouring-interface stalls or desense", "artifacts": "microscope photos, force/cycle CSV, five VNA touchstone sets and 3R/1T2R/2T1R/3T traffic traces"},
    {"id": "H5-MSR-SA518", "articles": ["voice-module"], "evidence": ["H5-MECH-SA518-LAND-FIT"], "method": "confirm received revision/variant and contact map; measure castellations; populate one shortest contact-7 coupon; record solder heat, VNA, supply/current/temperature, both bands, both power settings, audio, UART/PTT/PD/H-L and FAULT_KILL", "pass_rule": "the exact manufacturer-controlled sample fits the accepted reserve and meets the complete inherited RF/audio/safety contract without undocumented drive of UPDATE or VOXEN", "artifacts": "supplier response, incoming record, land-fit X-ray/photos, VNA/RF/audio/power/thermal/fault traces"},
    {"id": "H5-MSR-CONTROLS", "articles": ["navigation-and-direct-switches", "encoder", "encoder-knob", "run-kill-switch"], "evidence": ["H5-MECH-NAVIGATION-CONTROLS", "H5-MECH-DIRECT-PRESS-CONTROLS", "H5-MECH-ENCODER-KNOB", "H5-MECH-RUN-KILL"], "method": "populate the full 16-switch interface plus encoder/knob and side RUN/KILL aperture; measure access, actuation, accidental-press protection, depth, detents and repeated cycles", "pass_rule": "every serial control is independently reachable in the accepted external layout, remains recessed where required and passes the declared force/endurance limits", "artifacts": "dimensioned assembled photos, force curves, cycle log and signed ergonomic checklist"},
    {"id": "H5-MSR-PACK", "articles": ["cell-holder", "protected-cells", "pack-gauges"], "evidence": ["H3-PHY-028", "H5-MECH-CELL-HOLDER-FIT"], "method": "test one matched same-lot protected-cell pair in the exact holder across insertion, compression, polarity, vibration and thermal cycles; retain one MAX17320 golden device and sequence the second through blank, corrupt and exhausted-write conditions", "pass_rule": "the matched pair remains mechanically/electrically retained at all admitted corners and every gauge fault state deterministically blocks or recovers exactly as specified", "artifacts": "cell lot record, dimensional/force/thermal/vibration traces, gauge images/readbacks and fault logs"},
    {"id": "H5-MSR-AUDIO", "articles": ["speaker", "microphone", "headset-jack"], "evidence": ["H5-MECH-ACOUSTIC-PATHS", "H5-MECH-HEADSET-JACK"], "method": "mount the exact speaker and downward microphone in the representative cavity; sweep response/noise/feedback/vibration; cycle the jack with CTIA and ordinary TRS while recording detect, source selection, bias, transient and unplug pop", "pass_rule": "the enclosure path meets the inherited gain/noise/thermal limits and the jack preserves CTIA/TRS behavior without blocking the internal microphone", "artifacts": "audio sweeps, noise/feedback captures, insertion-force/cycle data and transient traces"},
    {"id": "H5-MSR-IR", "articles": ["ir-demod", "ir-carrier", "ir-emitter"], "evidence": ["H3-PHY-024"], "method": "verify markings/orientation; run simultaneous robust-envelope and 30-to-60-kHz carrier capture; measure startup/QOD/no-back-power; replay the protocol corpus and measure emitter current, range, alignment, temperature and optical safety", "pass_rule": "both receive channels and fail-closed transmit satisfy the inherited timing/electrical/optical bounds with no back-power or false provenance", "artifacts": "incoming photos, logic/power traces, protocol corpus results and optical/thermal measurements"},
    {"id": "H5-MSR-STORAGE", "articles": ["reference-microsd"], "evidence": ["H3-PHY-038"], "method": "record CID/CSD/CMD6 identity and run the admitted record/display contention profile through temperature and induced stalls", "pass_rule": "the exact reference card sustains >=1.5 MB/s logging, qualified >=4.0 MB/s transfers and the 512-KiB buffer contract without a radio deadline miss", "artifacts": "identity dump, raw throughput/stall CSV and buffer/radio timing trace"},
    {"id": "H5-MSR-AMLW", "articles": ["edge-sma", "amlw-core", "amlw-plug", "amlw-wire"], "evidence": ["H3-PHY-057"], "method": "verify exact identities and physical envelopes; wind and trim the first pod to 300 uH +/-5%; document mating and constituent geometry", "pass_rule": "the received SMA and every controlled pod constituent match the selected identities/envelopes and the completed pod meets inductance; routed parasitic budget remains H6 and total populated capacitance remains H8", "artifacts": "incoming photos, dimensions, winding record, L/Q sweep and mating record"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    residuals = load(RESIDUAL_MAP)
    research = load(SOURCE_RESEARCH)
    required = {row["id"] for row in residuals["residuals"]} | {row["id"] for row in residuals["mechanical_gates"]}
    covered = {item for row in ARTICLES for item in row["coverage"]}
    measurement_evidence = {item for row in MEASUREMENTS for item in row["evidence"]}
    article_ids = {row["id"] for row in ARTICLES}
    measurement_articles = {item for row in MEASUREMENTS for item in row["articles"]}
    priced = [row for row in ARTICLES if row["pricing"]["subtotal_usd"] is not None]
    rfq = [row for row in ARTICLES if row["pricing"]["kind"] == "manufacturer_rfq"]
    published_total = sum(Decimal(row["pricing"]["subtotal_usd"]) for row in priced if row["pricing"]["kind"] == "published_usd")
    budget_total = sum(Decimal(row["pricing"]["subtotal_usd"]) for row in priced if row["pricing"]["kind"] == "conservative_budget_cap_usd")
    total = published_total + budget_total
    groups = defaultdict(lambda: Decimal("0"))
    for row in priced:
        groups[row["group"]] += Decimal(row["pricing"]["subtotal_usd"])
    checks = {
        "h5_0_2_is_reviewed_and_current": research["status"] == "reviewed_research_only" and research["input"]["sha256"] == sha256(RESIDUAL_MAP),
        "every_required_residual_and_gate_has_an_article": required <= covered,
        "every_required_residual_and_gate_has_a_measurement_contract": required <= measurement_evidence,
        "article_ids_are_unique": len(article_ids) == len(ARTICLES),
        "every_article_is_used_by_a_measurement": article_ids == measurement_articles,
        "every_identity_is_exact_and_non_tbd": all(row["mpn"] and "TBD" not in row["mpn"].upper() for row in ARTICLES),
        "every_quantity_has_an_explicit_minimum_basis": all(row["order_quantity"] > 0 and row["minimum_quantity_basis"] for row in ARTICLES),
        "all_non_rfq_lines_have_a_current_cost": all(row["pricing"]["subtotal_usd"] is not None for row in ARTICLES if row["pricing"]["kind"] != "manufacturer_rfq"),
        "exactly_one_supplier_price_and_variant_remain_open": len(rfq) == 1 and rfq[0]["id"] == "voice-module",
        "purchase_layout_fabrication_not_authorized": all(not row["purchase_authorized"] for row in ARTICLES),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H5.0.3 basket checks failed: " + ", ".join(failed))
    return {
        "schema_version": 1,
        "stage": "H5.0.3",
        "status": "draft_supplier_quote_open",
        "checked_on": CHECKED_ON,
        "purpose": "one deduplicated engineering-sample basket after documentary and serial-replacement research; no purchase authorization",
        "inputs": {
            "residual_map": {"path": str(RESIDUAL_MAP.relative_to(REPO)), "sha256": sha256(RESIDUAL_MAP)},
            "source_research": {"path": str(SOURCE_RESEARCH.relative_to(REPO)), "sha256": sha256(SOURCE_RESEARCH)},
        },
        "summary": {
            "article_lines": len(ARTICLES),
            "measurement_contracts": len(MEASUREMENTS),
            "covered_residuals_and_gates": len(required),
            "published_price_subtotal_usd": f"{published_total:.2f}",
            "conservative_budget_caps_usd": f"{budget_total:.2f}",
            "known_engineering_material_budget_usd": f"{total:.2f}",
            "unpriced_manufacturer_lines": len(rfq),
            "excluded_from_budget": ["SA518 manufacturer sample quote", "freight", "tax", "customs", "H5.2 coupon PCB fabrication/assembly", "general laboratory instruments and ordinary passives"],
            "former_parked_plan_usd": "164.54 for only a partial eight-line lot",
            "comparison_note": "The new total is larger because it covers all 9 H5 residuals and 14 mechanical gates, but quantities within each line are reduced to evidence minima.",
        },
        "group_budget_usd": {key: f"{value:.2f}" for key, value in sorted(groups.items())},
        "articles": ARTICLES,
        "measurements": MEASUREMENTS,
        "supplier_blocker": {
            "article": "voice-module",
            "reason": "NiceRF publishes current SA518 technical evidence but no controlled sample price, production-variant confirmation or authorized-stock channel. Marketplace listings provide a cost ceiling only and do not prove identity-controlled supply.",
            "marketplace_reference": {
                "currency": "GBP",
                "item": "20.72",
                "delivery": "3.52",
                "total": "24.24",
                "source": "https://www.onbuy.com/gb/p/1pc-sa518-1w-uv-dual-frequency-walkie-talkie-module-support-wireless-data-and-voice~p259569520/",
                "accepted_as_qualified_source": False,
            },
            "replacements_rejected": [
                "SA818Pro is ordered as separate UHF or VHF variants; preserving both bands requires two modules and a full redesign",
                "SA528 is simultaneous U/V but 54.03 x 38.30 x 7.70 mm with a different 23-contact/audio interface",
            ],
            "prepared_request": "hardware/procurement/SA518-sample-rfq.md",
            "direct_request_status": "deferred while a qualified exact-SA518 price is pursued through the selected JLCPCB route",
            "next_action": "obtain one qualified exact-SA518 price; all 209 BOM lines already have J0-J4 routes without replacement, and the JLCAPI Parts permission is reviewing",
        },
        "sequencing": {
            "now": "keep all 209 exact J0-J4 routes stable and obtain one qualified exact-SA518 price; the JLCAPI app exists and Parts permission is reviewing",
            "after_mapping": "use approved read-only Parts access for repeatable availability checks; route SA518 through JLCPCB global sourcing/new-part request only after separate authorization, with the prepared NiceRF request as fallback",
            "after_quote": "publish exact whole-basket cost and request a separate sample-order decision",
            "after_order": "H5.1 incoming identity/metrology; then design and price only the H5.2 coupons whose geometry depends on received parts",
            "forbidden": ["component purchase without a separate decision", "PCB placement/routing", "prototype fabrication"],
        },
        "checks": checks,
    }


def money(value: str | None) -> str:
    return "RFQ" if value is None else f"${Decimal(value):.2f}"


def group_sections(data: dict, russian: bool) -> str:
    labels = {
        "display": "Дисплей" if russian else "Display",
        "expansion": "Расширения" if russian else "Expansion",
        "rf": "Радиотракты" if russian else "RF paths",
        "controls": "Органы управления" if russian else "Controls",
        "power": "Питание" if russian else "Power",
        "audio": "Аудио" if russian else "Audio",
        "ir": "IR" if russian else "IR",
        "storage": "Хранилище" if russian else "Storage",
        "amlw-pod": "AM/LW pod" if russian else "AM/LW pod",
    }
    sections = []
    for group, title in labels.items():
        rows = [row for row in data["articles"] if row["group"] == group]
        lines = []
        for row in rows:
            subtotal = money(row["pricing"]["subtotal_usd"])
            availability = row["source"]["availability"]
            detail = "Почему минимум" if russian else "Minimum basis"
            lines.append(
                f"- **{row['order_quantity']} × `{row['mpn']}` — {subtotal}.** "
                f"[{row['source']['label']}]({row['source']['url']}); {availability}.\n"
                f"  {detail}: {row['minimum_quantity_basis']}"
            )
        sections.append(f"### {title}\n\n" + "\n".join(lines))
    return "\n\n".join(sections)


def measurement_sections(data: dict, russian: bool) -> str:
    sections = []
    for row in data["measurements"]:
        if russian:
            body = (
                f"- Покрывает: `{', '.join(row['evidence'])}`.\n"
                f"- Метод: {row['method']}.\n"
                f"- Критерий: {row['pass_rule']}.\n"
                f"- Артефакты: {row['artifacts']}."
            )
        else:
            body = (
                f"- Covers: `{', '.join(row['evidence'])}`.\n"
                f"- Method: {row['method']}.\n"
                f"- Pass rule: {row['pass_rule']}.\n"
                f"- Artifacts: {row['artifacts']}."
            )
        sections.append(f"<details><summary><code>{row['id']}</code></summary>\n\n{body}\n\n</details>")
    return "\n\n".join(sections)


def render_doc(data: dict, russian: bool) -> str:
    summary = data["summary"]
    if russian:
        return f"""# H5.0.3 · единая корзина неустранимых образцов

[English](component-sample-basket.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Предыдущий поиск](component-source-research.ru.md)

Корзина опубликована, но **H5.0.3 ещё не закрыт**: [JLCPCB Standard PCBA выбран рабочей производственной линией](manufacturing-platform.ru.md); контрольный BOM Tool прогон сопоставил 176/209 строк и распознал все 1019 установок, а exact-поиск дал всем 209 строкам маршруты `J0`–`J4` без замен. `NiceRF SA518` остаётся единственной неизвестной ценой корзины. Приложение JLCAPI создано, право Parts находится на ревью; закупка, sourcing request, quote/reservation, PCB placement/routing и fabrication не разрешены.

```mermaid
flowchart TD
  R["✅ H5.0.2<br/>источники и замены"] --> B["▶️ H5.0.3<br/>$266.63 + SA518 RFQ"]
  B --> P["JLCPCB Standard<br/>176/209 · 1019/1019"]
  P --> Q["✅ 209/209 маршрутов<br/>J0–J4 без замен"]
  Q --> S["квалифицированная цена<br/>exact SA518"]
  S --> A["отдельное решение<br/>о закупке образцов"]
  A --> H51["H5.1<br/>incoming inspection"]
  H51 --> H52["H5.2<br/>coupons по реальным размерам"]
```

## Сводка стоимости

- **${summary['known_engineering_material_budget_usd']}** — известный консервативный material budget для всех priced lines.
- Внутри него **${summary['published_price_subtotal_usd']}** — публичные USD-цены и **${summary['conservative_budget_caps_usd']}** — два консервативных cap для дешёвых IR-деталей, чьи live-страницы показывают цену в AUD/INR.
- Отдельно: **один `SA518` — RFQ**. Непроверенный marketplace даёт только ceiling `£24.24` с доставкой, но не квалифицированный источник.
- Не включены доставка, налоги, таможня и H5.2 coupon PCB: геометрия части coupons зависит от H5.1 incoming measurements, поэтому преждевременная печать создала бы тот же цикл, который мы устраняем.
- Старая сумма `$164.54` была не дешёвой полной корзиной, а неполным набором из восьми строк; она не покрывала большинство H5 gates.

## Что именно требуется получить

{group_sections(data, True)}

## Измерительные контракты

Все `{summary['covered_residuals_and_gates']}` residual/gate покрыты `{summary['measurement_contracts']}` контрактами. Pass/fail без raw evidence не принимается.

{measurement_sections(data, True)}

## Единственный открытый supplier input

`SA518` остаётся функционально лучшим вариантом: `SA818Pro` требует два отдельных U/V-модуля и переделку RF/power/audio, а dual-band `SA528` имеет корпус `54.03 × 38.30 × 7.70 мм` и другой 23-контактный interface. У NiceRF есть текущие datasheet и product page, но нет публичной квалифицированной цены образца и подтверждения production variant.

Подготовленный [manufacturer RFQ](../hardware/procurement/SA518-sample-rfq.md) сохранён как fallback. Сначала `SA518` проходит через JLCPCB global sourcing/new-part route вместе с полным [производственным аудитом](manufacturing-platform.ru.md). После квалифицированного ответа появится точная полная стоимость и отдельный вопрос о заказе.

Машинный результат: [`H5-EVR03`](../hardware/verification/generated/H5-EVR03-irreducible-sample-basket.json).
"""
    return f"""# H5.0.3 · one irreducible engineering-sample basket

[Русский](component-sample-basket.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Previous research](component-source-research.md)

The basket is published, but **H5.0.3 is not yet reviewed**: [JLCPCB Standard PCBA is now the manufacturing reference](manufacturing-platform.md); its controlled BOM Tool run matched 176/209 lines and parsed all 1019 placements, while exact search gave all 209 lines `J0`–`J4` routes without replacement. `NiceRF SA518` remains the basket's only unpriced line. The JLCAPI app exists and Parts permission is under review; purchase, sourcing request, quote/reservation, PCB placement/routing and fabrication are not authorized.

```mermaid
flowchart TD
  R["✅ H5.0.2<br/>sources + replacements"] --> B["▶️ H5.0.3<br/>$266.63 + SA518 RFQ"]
  B --> P["JLCPCB Standard<br/>176/209 · 1019/1019"]
  P --> Q["✅ 209/209 routes<br/>J0–J4 · no replacement"]
  Q --> S["qualified exact-SA518<br/>price"]
  S --> A["separate sample-order<br/>decision"]
  A --> H51["H5.1<br/>incoming inspection"]
  H51 --> H52["H5.2<br/>coupons from real dimensions"]
```

## Cost summary

- **${summary['known_engineering_material_budget_usd']}** is the known conservative material budget for every priced line.
- It contains **${summary['published_price_subtotal_usd']}** of published USD prices and **${summary['conservative_budget_caps_usd']}** of conservative caps for two cheap IR parts whose live pages expose AUD/INR prices.
- Separately, **one `SA518` is RFQ**. An unqualified marketplace listing gives only a `£24.24` delivered ceiling, not an identity-controlled source.
- Freight, taxes, customs and H5.2 coupon PCBs are excluded. Some coupon geometry depends on H5.1 incoming measurements; fabricating it now would recreate the cycle this phase removes.
- The former `$164.54` was not a cheaper complete basket: it covered only eight partial lines and omitted most H5 gates.

## Exact received articles

{group_sections(data, False)}

## Measurement contracts

All `{summary['covered_residuals_and_gates']}` residuals/gates are covered by `{summary['measurement_contracts']}` contracts. A pass/fail summary without raw evidence is not accepted.

{measurement_sections(data, False)}

## Sole open supplier input

`SA518` remains the best functional fit: `SA818Pro` needs two separate U/V modules and an RF/power/audio redesign, while dual-band `SA528` is `54.03 × 38.30 × 7.70 mm` with a different 23-contact interface. NiceRF publishes current technical sources but no qualified sample price or production-variant confirmation.

The prepared [manufacturer RFQ](../hardware/procurement/SA518-sample-rfq.md) remains a fallback. `SA518` first goes through JLCPCB global sourcing/new-part routing as part of the complete [manufacturing audit](manufacturing-platform.md). A qualified response enables the exact whole-basket cost and a separate order decision.

Machine result: [`H5-EVR03`](../hardware/verification/generated/H5-EVR03-irreducible-sample-basket.json).
"""


def render_legacy_pointer() -> str:
    return """# H5 engineering-sample basket

This former hand-maintained partial plan has been superseded by the generated,
fully covered H5.0.3 artifact:

- [readable engineering-sample basket](../../docs/component-sample-basket.md);
- [machine basket and measurement contracts](../verification/generated/H5-EVR03-irreducible-sample-basket.json);
- [Russian page](../../docs/component-sample-basket.ru.md).

The old quantities and `$164.54` partial subtotal are intentionally not an
ordering source. Purchasing is the last resort after documentary and
function-preserving replacement research. Sample ordering, PCB
placement/routing and fabrication remain unauthorized. The current basket has
one supplier-price input open (`SA518`); all 209 availability routes are mapped,
the JLCAPI Parts permission is under review, and the prepared direct manufacturer
request remains a fallback.
"""


def outputs() -> dict[Path, str]:
    data = build()
    return {
        OUTPUT: json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(data, False),
        DOC_RU: render_doc(data, True),
        LEGACY_PLAN: render_legacy_pointer(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, content in expected.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H5.0.3 artifacts: " + ", ".join(stale))
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    data = build()
    print(
        "ok: H5.0.3 draft covers "
        f"{data['summary']['covered_residuals_and_gates']} residuals/gates with "
        f"{data['summary']['article_lines']} article lines and "
        f"{data['summary']['measurement_contracts']} measurement contracts; "
        f"known material budget ${data['summary']['known_engineering_material_budget_usd']}; "
        "one SA518 manufacturer quote remains open"
    )


if __name__ == "__main__":
    main()
