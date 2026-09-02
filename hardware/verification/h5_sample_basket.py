#!/usr/bin/env python3
"""Generate the H5.0.3 sole-prototype article manifest and H7/H8 contracts."""

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
CHECKED_ON = "2026-08-29"


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
    checked_on: str | None = None,
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
            "checked_on": checked_on or CHECKED_ON,
            "availability": availability,
        },
        "coverage": coverage,
        "minimum_quantity_basis": minimum_basis,
        "risk": risk,
        "purchase_authorized": False,
    }


ARTICLES = [
    article("production-display", "display", "EastRising ER-TFT035IPS-6 + ER-TPC035-6 option 5344", 1, "14.91", "published_usd", "BuyDisplay exact product page", "https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen", "listed in stock; one-piece price published; exact panel/touch drawings and interface table available", ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "exactly one production panel is installed and mated in the finished prototype; the exact FH34SRJ-50S-0.5SH(50) board connector is populated during PCBA", order_unit="factory-installed panel", risk="The panel identity and electrical/mechanical endpoint are fixed. Only written acceptance of adhesive/FPC handling and final mating by the selected assembler remains an H5 supplier gate; HMX035CTFT-001 stays legacy evidence only."),
    article("display-psa", "display", "3M (TC) 4910SQ-2(5)", 1, "22.12", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/3m-tc/4910SQ-2-5/3339259", "active; 16 sellable units shown in stock; quantity-one displayed price", ["H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "one ready-cut 50.80 x 50.80 mm square retains the sole production display without an owner cutting operation; no spare or long roll is included", order_unit="ready-cut square", risk="JLCPCB public Standard-parts search exposed no exact result. Treat as a customer-supplied J4-F final-assembly consumable until the assembler accepts the exact pad, backed >=100 kPa pressure process and final FPC mating in writing. Release also requires measured folded-FPC stack <=0.714 mm and actual clearance >=0.20 mm.", checked_on="2026-09-01"),

    article("u214", "expansion", "M5Stack U214 Cap LoRa-1262", 1, "14.50", "published_usd", "M5Stack official store", "https://shop.m5stack.com/products/cap-lora-1262", "listed in stock", ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "the same non-destructive unit closes identity, dimensions, mating and functional checks"),
    article("u214-host-socket", "expansion", "Samtec HLE-107-02-G-DV-PE-LC", 1, "3.338", "published_usd", "Samtec exact product page", "https://www.samtec.com/products/hle-107-02-g-dv-pe-lc", "manufacturer orderable", ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "one production host socket is the actual mixed-pair mate; the former quantity five was spare stock, not evidence"),
    article("m5-host-header-pack", "expansion", "Seeed 114020164 / 1125R-SMT-4P", 1, "2.80", "published_usd", "Seeed official store", "https://www.seeedstudio.com/Grove-Female-Header-SMD-4P-2.0mm-90D-20Pcs-p-4590.html", "listed in stock", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one is needed, but the exact serial connector is sold as a smallest 20-piece pack", order_unit="20-piece pack", contained_pieces=20),
    article("m5-short-cable", "expansion", "M5Stack A034-G", 1, "3.95", "published_usd", "M5Stack official store", "https://shop.m5stack.com/products/4pin-buckled-grove-cable", "orderable", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack supplies the short-profile test article", order_unit="pack"),
    article("m5-boundary-cable", "expansion", "M5Stack A034-B", 1, "2.59", "published_usd", "authorized-distributor exact SKU listing", "https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/A034-B/13974037", "orderable", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack supplies the boundary-length test article", order_unit="pack"),
    article("m5-instrument-cable", "expansion", "M5Stack A096", 1, "4.50", "published_usd", "DigiKey exact-SKU listing", "https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/A096/18084377", "authorized stock", ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "one smallest pack exposes the admitted profiles to instruments", order_unit="pack"),

    article("nrf-modules", "rf", "Ebyte E01-ML01SP4 / JLCPCB C97340", 3, "4.4835", "published_usd", "JLCPCB exact original-manufacturer part page", "https://jlcpcb.com/partdetail/E01-ML01SP4/C97340", "405 in stock, 388 available, MOQ 1; factory SMT placement", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS"], "exactly three factory-fitted PA/LNA modules are required to prove simultaneous full RX, TX and mixed operation; no owner placement or untouched spare"),
    article("rf-jumpers-native", "rf", "TE Connectivity 2118651-2", 2, "2.52", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2118651-2/16538824", "3,082 shown in stock", ["H3-PHY-062", "H5-MECH-NATIVE-RF-JUMPERS"], "two exact 30-mm paths serve S3 and C5; each installed bend/retention path must be represented"),
    article("rf-jumpers-nrf", "rf", "TE Connectivity 1-2118651-0", 3, "1.81", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/1-2118651-0/12380462", "7,283 shown in stock", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS"], "three exact 60-mm paths serve the E01-ML01SP4 radios and retain at least the generated conservative routing slack"),
    article("rf-board-receptacles", "rf", "Hirose U.FL-R-SMT-1(80)", 5, "0.1016", "published_usd", "JLCPCB exact original-manufacturer part C88374", "https://jlcpcb.com/partdetail/U.FL-R-SMT-1%2880%29/C88374", "72,989 in stock; 68,798 orderable; MOQ 1; factory SMT placement", ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"], "one board mate per selected 30-mm jumper path; (80) changes reel presentation only"),
    article("edge-sma", "rf", "GCT RFPC-SMA31-FN-175-A", 4, "3.39", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/gct/RFPC-SMA31-FN-175-A/25576371", "638 shown in stock", ["H3-PHY-053", "H3-PHY-057", "H5-MECH-NRF-GEN1-FEEDS"], "three nRF24 boundaries plus one AM/LW receive boundary; the S3/C5 module cables use their separately selected SMA32 path"),
    article("voice-uhf-module", "rf", "G-NiceRF SA818S-U", 1, "9.7347", "published_usd", "JLCPCB exact G-NiceRF part C3001549", "https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549", "68 in stock; 60 available to order", ["H5-MECH-SA818S-DUAL-LAND-FIT"], "one exact UHF module is required because band-specific RF, conducted power, audio, UART and thermal behavior cannot be inferred from the VHF variant"),
    article("voice-vhf-module", "rf", "G-NiceRF SA818S-V", 1, "10.0710", "published_usd", "JLCPCB exact G-NiceRF part C51897911", "https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911", "stock zero; MOQ one; pre-order; typical 8-15 working days", ["H5-MECH-SA818S-DUAL-LAND-FIT"], "one exact VHF module is required because it is an independent installed product path; common land geometry alone does not prove band-specific RF, audio, UART or thermal behavior", risk="The exact part is priced but stock-zero pre-order. The typical lead range is known; final quote and exact lead remain order-time gates. SA818S-CE cannot replace this VHF path."),

    article("navigation-and-direct-switches", "controls", "Omron B3S-1100P", 16, "0.90", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3S-1100P/368393", "33,862 shown in stock", ["H5-MECH-NAVIGATION-CONTROLS", "H5-MECH-DIRECT-PRESS-CONTROLS"], "five navigation positions plus BACK, OPT, F1-F8 and PTT must all be populated simultaneously to test spacing and enclosure actuation"),
    article("encoder", "controls", "Alps Alpine EC11E18244AU", 1, "4.90", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Alps-Alpine/EC11E18244AU", "966 shown in stock", ["H5-MECH-ENCODER-KNOB"], "one assembled encoder/knob path closes the only encoder gate"),
    article("encoder-knob", "controls", "Davies Molding 1227-J", 1, "1.58", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Davies-Molding/1227-J", "524 shown in stock", ["H5-MECH-ENCODER-KNOB"], "one exact production knob mates to the one encoder specimen"),
    article("run-kill-switch", "controls", "C&K JS102011SCQN", 1, "1.11", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/c-k/JS102011SCQN/7355835", "535 shown in stock", ["H5-MECH-RUN-KILL"], "the installed switch/aperture path closes fit, detent and ordinary-actuation evidence"),

    article("cell-holder", "power", "Keystone 1048P", 1, "11.19", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Keystone-Electronics/1048P", "145 shown in stock", ["H5-MECH-CELL-HOLDER-FIT"], "one holder is the actual two-cell mechanism"),
    article("protected-cells", "power", "XTAR protected 18650 4000 mAh 10 A", 2, "14.50", "published_usd", "XTAR official store", "https://xtardirect.com/products/xtar-high-capacity-36v-18650-4000mah-10a-protected-lithium-ion-battery", "98 shown in stock", ["H5-MECH-CELL-HOLDER-FIT"], "one matched same-lot pair is the only admitted operating pack; mixed MPN, lot, age or state of charge remains forbidden"),
    article("pack-gauges", "power", "Analog Devices MAX17320G20+T", 1, "6.19", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/en/ProductDetail/Analog-Devices-Maxim-Integrated/MAX17320G20%2BT", "7,638 shown in stock", ["H3-PHY-028"], "one device covers blank -> deliberately invalid but electrically safe configuration -> reviewed golden/recovery with complete readback; zero-remaining and failed-copy are emulator/fixture-only, all seven physical updates are never consumed and no sacrificial chip is required"),

    article("speaker", "audio", "PUI Audio AS02404PO", 1, "3.97", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/product-highlight/p/pui-audio/as-series-high-quality-speakers", "421 immediate units shown", ["H5-MECH-ACOUSTIC-PATHS"], "one final-cavity specimen closes the speaker path"),
    article("microphone", "audio", "Same Sky CMEJ-0413-42-SMT-TR", 1, "0.64", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMEJ-0413-42-SMT-TR/10253447", "12,929 shown in stock", ["H5-MECH-ACOUSTIC-PATHS"], "one downward microphone path closes response, sealing and feedback checks"),
    article("headset-jack", "audio", "Same Sky SJ-43504-SMT-TR", 1, "1.29", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Same-Sky/SJ-43504-SMT-TR", "5,344 shown in stock", ["H5-MECH-HEADSET-JACK"], "one repeated CTIA/TRS mating specimen closes the only jack gate"),

    article("ir-demod", "ir", "Vishay TSOP75238TR", 1, "1.3011", "published_usd", "JLCPCB C511498 exact Vishay listing", "https://jlcpcb.com/partdetail/x/C511498", "15 currently placeable; MOQ 1", ["H3-PHY-024"], "one production robust-demodulator channel; TR preserves the TT body, contacts and electrical function but requires explicit CPL rotation/feeder-presentation approval before PCBA"),
    article("ir-carrier", "ir", "Vishay TSMP95000TT", 1, "2.00", "conservative_budget_cap_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Vishay-Semiconductors/TSMP95000TT", "4,182 shown in cut-tape stock", ["H3-PHY-024"], "one independent carrier-learning channel", source_price={"currency": "AUD", "unit": "2.86", "note": "USD 2.00 is a conservative engineering budget cap, not a claimed converted distributor price"}),
    article("ir-emitter", "ir", "Vishay VSMY14940", 1, "2.00", "conservative_budget_cap_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VSMY14940/4071416", "4,872 shown in cut-tape stock", ["H3-PHY-024"], "one actual emitter is sufficient for optical, current and temperature evidence", source_price={"currency": "INR", "unit": "92.62", "note": "USD 2.00 is a conservative engineering budget cap, not a claimed converted distributor price"}),

    article("reference-microsd", "storage", "SanDisk SDSQQNR-032G-GN6IA", 1, "40.05", "published_usd", "TME exact-MPN listing", "https://www.tme.com/in/en/details/sdsqqnr-032g-gn6ia/memory-cards/sandisk/", "200 shown in stock", ["H3-PHY-038"], "one identity-controlled reference medium is sufficient for CMD6, throughput, stalls and buffer traces"),

    article("amlw-core", "amlw-pod", "Fair-Rite 3061990901", 1, "2.70", "published_usd", "Mouser exact-MPN listing", "https://www.mouser.com/ProductDetail/Fair-Rite/3061990901", "1,792 shown in stock", ["H3-PHY-057"], "one controlled first-pod core is measured and wound"),
    article("amlw-plug", "amlw-pod", "Adam Tech RF2-154-T-17-50-G", 1, "3.76", "published_usd", "DigiKey exact-MPN listing", "https://www.digikey.com/en/products/detail/adam-tech/RF2-154-T-17-50-G/9831243", "839 shown in stock", ["H3-PHY-057"], "one male plug mates to the one AM/LW device boundary"),
    article("amlw-wire", "amlw-pod", "Remington 38SNSP.125", 1, "13.33", "published_usd", "Remington Industries official store", "https://www.remingtonindustries.com/magnet-wire/magnet-wire-38-awg-enameled-copper-6-spool-sizes/", "smallest exact-wire spool orderable", ["H3-PHY-057"], "one smallest spool supplies the controlled winding and measurement retries", order_unit="spool"),
]


MEASUREMENTS = [
    {"id": "H5-MSR-DISPLAY", "articles": ["production-display", "display-psa"], "evidence": ["H3-PHY-017", "H5-MECH-DISPLAY-TAIL", "H5-MECH-DISPLAY-PERFORMANCE"], "method": "the factory installs exact ER-TFT035IPS-6 + ER-TPC035-6 option 5344 on one ready-cut 3M (TC) 4910SQ-2(5), folds the FPC through the controlled slot and mates it through exact FH34SRJ-50S-0.5SH(50) in the sole finished prototype; the owner performs first USB-powered bring-up and records known-image, backlight and touch results", "pass_rule": "the released drawing, connector, mating and retention steps are deterministic; measured folded-FPC stack is <=0.714 mm, actual pad-to-stack clearance is >=0.20 mm, and written acceptance of the supplied exact pad, uniformly backed >=100 kPa pressure process, FPC handling and final mating is obtained before order; any paid pre-shipment Function Test remains optional quote-only insurance and never a release gate", "artifacts": "controlled panel, pad and connector identities/drawings, incoming pad dimensions/lot, FPC stack and clearance measurement, deterministic assembly instructions, factory assembly record, owner USB bring-up image/backlight/touch traces and signed result"},
    {"id": "H5-MSR-U214", "articles": ["u214", "u214-host-socket"], "evidence": ["H3-PHY-046", "H5-MECH-U214-MATING-STACK"], "method": "measure the fitted U214 posts and exact HLE; during ordinary assembly/disassembly record all 14 continuities, bottoming clearance, rail preload, screw retention and visual condition without a prescribed force or cycle programme", "pass_rule": "the mixed U214/HLE pair mates without yield or bottoming, retains every contact and preserves the protected hot-plug sequence", "artifacts": "metrology, continuity log and installed photos"},
    {"id": "H5-MSR-M5", "articles": ["m5-host-header-pack", "m5-short-cable", "m5-boundary-cable", "m5-instrument-cable"], "evidence": ["H3-PHY-048", "H5-MECH-M5-UNIT-MATE"], "method": "measure connector/cable geometry, inspect ordinary mating and strain relief, and run I2C, UART, GPIO and 1-Wire profiles through TXS0102 at short and boundary lengths with the breakout attached", "pass_rule": "ordinary mating, retention, strain relief, pull networks and waveforms satisfy each admitted profile; unsupported motor/actuator loads remain excluded", "artifacts": "cable photos/lengths, continuity records and oscilloscope captures"},
    {"id": "H5-MSR-RF5", "articles": ["nrf-modules", "rf-jumpers-native", "rf-jumpers-nrf", "rf-board-receptacles", "edge-sma"], "evidence": ["H3-PHY-053", "H3-PHY-062", "H5-MECH-NRF-GEN1-FEEDS", "H5-MECH-NATIVE-RF-JUMPERS"], "method": "inspect all E01 factory receptacles; assemble the two 30-mm and three 60-mm U.FL cable paths and edge SMA boundaries normally; inspect bend, retention and strain relief, verify continuity and S-parameters, then run all three nRF24 simultaneously in full RX, TX and mixed modes with every inactive interface hardware-quiet", "pass_rule": "all five paths meet inherited loss/match and retention limits, all three nRF24 meet concurrent deadlines without neighbouring-interface stalls or desense", "artifacts": "microscope photos, continuity records, five VNA touchstone sets and 3R/1T2R/2T1R/3T traffic traces"},
    {"id": "H5-MSR-SA818S-DUAL", "articles": ["voice-uhf-module", "voice-vhf-module"], "evidence": ["H5-MECH-SA818S-DUAL-LAND-FIT"], "method": "confirm both factory-installed G-NiceRF identities and the common Rev 1.8 18-land contact map on the sole prototype; inspect each module and castellations, then record VNA, supply/current/temperature, band limits, both power settings, audio, UART/PTT/PD/H-L and FAULT_KILL for each independently selectable installed variant during H7/H8 owner bring-up", "pass_rule": "both exact modules fit the common accepted production land and each independently meets its inherited RF/audio/safety contract; no CE substitution is silent and no test drives reserved contacts 8-18", "artifacts": "factory identity/assembly records, arrival and land-fit photos, VNA/RF/audio/power/thermal/fault traces for U and V"},
    {"id": "H5-MSR-CONTROLS", "articles": ["navigation-and-direct-switches", "encoder", "encoder-knob", "run-kill-switch"], "evidence": ["H5-MECH-NAVIGATION-CONTROLS", "H5-MECH-DIRECT-PRESS-CONTROLS", "H5-MECH-ENCODER-KNOB", "H5-MECH-RUN-KILL"], "method": "use the full 16-switch interface plus encoder/knob and side RUN/KILL aperture on the one assembled prototype; inspect access, ordinary actuation, accidental-press protection, depth and detents without artificial ageing", "pass_rule": "every serial control is independently reachable in the accepted external layout, remains recessed where required and works during ordinary operation", "artifacts": "dimensioned assembled photos, continuity/actuation record and signed ergonomic checklist"},
    {"id": "H5-MSR-PACK", "articles": ["cell-holder", "protected-cells", "pack-gauges"], "evidence": ["H3-PHY-028", "H5-MECH-CELL-HOLDER-FIT"], "method": "verify exact holder/cradle/stop geometry and polarity, install/remove the matched same-lot protected-cell pair only as ordinarily required, then inspect pads/contact retention and continuity; keep the pair inside its exact MPN voltage/current/temperature limits; on one MAX17320 record blank -> deliberately invalid but electrically safe configuration -> reviewed golden/recovery with both address spaces, checksum, NVError and remaining-update bitmap; inject zero-remaining, failed-copy, reversed, swapped, open, short, missing, imbalance and temperature thresholds through the emulator or current-limited cell-simulator/NTC fixture", "pass_rule": "the enclosure rather than SMT pads carries ordinary insertion/removal load, the matched pair remains mechanically/electrically retained, the gauge blocks and recovers deterministically, all seven physical NVM updates are not consumed, and no real cell is abused beyond its MPN limits", "artifacts": "cell identity record, dimensioned installation photos, pad/contact continuity inspection, simulator/NTC-fixture traces, gauge images/readbacks and fault logs"},
    {"id": "H5-MSR-AUDIO", "articles": ["speaker", "microphone", "headset-jack"], "evidence": ["H5-MECH-ACOUSTIC-PATHS", "H5-MECH-HEADSET-JACK"], "method": "mount the exact speaker and downward microphone in the representative cavity; sweep response/noise/feedback and inspect buzz/rattle during ordinary playback; mate CTIA and ordinary TRS as needed while recording detect, source selection, bias, transient and unplug pop", "pass_rule": "the enclosure path meets the inherited gain/noise/thermal limits and the jack preserves CTIA/TRS behavior without blocking the internal microphone", "artifacts": "audio sweeps, noise/feedback captures, ordinary-mating continuity record and transient traces"},
    {"id": "H5-MSR-IR", "articles": ["ir-demod", "ir-carrier", "ir-emitter"], "evidence": ["H3-PHY-024"], "method": "verify markings/orientation; confirm TSOP75238TR CPL rotation and feeder presentation against the JLCPCB placement preview; run simultaneous robust-envelope and 30-to-60-kHz carrier capture; measure startup/QOD/no-back-power; replay the protocol corpus and measure emitter current, range, alignment, temperature and optical safety", "pass_rule": "the assembled TR orientation matches the Vishay contact map, both receive channels and fail-closed transmit satisfy the inherited timing/electrical/optical bounds with no back-power or false provenance", "artifacts": "CPL/placement approval, incoming photos, logic/power traces, protocol corpus results and optical/thermal measurements"},
    {"id": "H5-MSR-STORAGE", "articles": ["reference-microsd"], "evidence": ["H3-PHY-038"], "method": "record CID/CSD/CMD6 identity and run the admitted record/display contention profile through temperature and induced stalls", "pass_rule": "the exact reference card sustains >=1.5 MB/s logging, qualified >=4.0 MB/s transfers and the 512-KiB buffer contract without a radio deadline miss", "artifacts": "identity dump, raw throughput/stall CSV and buffer/radio timing trace"},
    {"id": "H5-MSR-AMLW", "articles": ["edge-sma", "amlw-core", "amlw-plug", "amlw-wire"], "evidence": ["H3-PHY-057"], "method": "verify exact delivered identities and physical envelopes; wind and trim the first owner pod to 300 uH +/-5% after arrival; document mating and constituent geometry", "pass_rule": "the installed SMA and every controlled pod constituent match the selected identities/envelopes and the completed pod meets inductance; routed parasitic budget remains H6 and total populated capacitance remains H8", "artifacts": "arrival photos, dimensions, winding record, L/Q sweep and mating record"},
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
    unpriced = [row for row in ARTICLES if row["pricing"]["subtotal_usd"] is None]
    published_total = sum(Decimal(row["pricing"]["subtotal_usd"]) for row in priced if row["pricing"]["kind"] == "published_usd")
    budget_total = sum(Decimal(row["pricing"]["subtotal_usd"]) for row in priced if row["pricing"]["kind"] == "conservative_budget_cap_usd")
    total = published_total + budget_total
    groups = defaultdict(lambda: Decimal("0"))
    for row in priced:
        groups[row["group"]] += Decimal(row["pricing"]["subtotal_usd"])
    checks = {
        "h5_0_2_is_reviewed_and_current": research["status"] == "reviewed_research_only" and research["inputs"][str(RESIDUAL_MAP.relative_to(REPO))] == sha256(RESIDUAL_MAP),
        "every_required_residual_and_gate_has_an_article": required <= covered,
        "every_required_residual_and_gate_has_a_measurement_contract": required <= measurement_evidence,
        "article_ids_are_unique": len(article_ids) == len(ARTICLES),
        "every_article_is_used_by_a_measurement": article_ids == measurement_articles,
        "every_selected_identity_is_exact": all(
            row["mpn"] and "UNRESOLVED" not in row["mpn"].upper()
            for row in ARTICLES
        ),
        "production_display_is_one_exact_priced_factory_installed_panel": [
            (row["order_quantity"], row["pricing"]["unit_usd"], row["order_unit"])
            for row in ARTICLES
            if row["id"] == "production-display"
        ] == [(1, "14.91", "factory-installed panel")],
        "display_psa_is_one_exact_priced_ready_cut_square": [
            (row["mpn"], row["order_quantity"], row["pricing"]["unit_usd"], row["order_unit"])
            for row in ARTICLES
            if row["id"] == "display-psa"
        ] == [("3M (TC) 4910SQ-2(5)", 1, "22.12", "ready-cut square")],
        "every_quantity_has_an_explicit_minimum_basis": all(row["order_quantity"] > 0 and row["minimum_quantity_basis"] for row in ARTICLES),
        "no_selected_article_has_unpriced_identity": not unpriced,
        "both_selected_voice_variants_are_in_the_integrated_manifest": {"voice-uhf-module", "voice-vhf-module"} <= article_ids,
        "voice_prices_match_reviewed_jlcpcb_routes": {
            row["mpn"]: row["pricing"]["unit_usd"]
            for row in ARTICLES
            if row["id"] in {"voice-uhf-module", "voice-vhf-module"}
        } == {"G-NiceRF SA818S-U": "9.7347", "G-NiceRF SA818S-V": "10.0710"},
        "purchase_layout_fabrication_not_authorized": all(not row["purchase_authorized"] for row in ARTICLES),
        "no_separate_sample_or_coupon_order": True,
        "all_physical_contracts_execute_on_h7_h8_prototype_or_ordinary_accessories": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H5.0.3 basket checks failed: " + ", ".join(failed))
    return {
        "schema_version": 2,
        "stage": "H5.0.3-R1",
        "status": "draft_order_integrated_manifest_exact_display_selected_factory_response_pending",
        "checked_on": CHECKED_ON,
        "purpose": "one order-integrated article manifest for the sole fully assembled Leshy2 prototype plus H7/H8 owner evidence contracts; no device batch, separate sample purchase or purchase authorization",
        "procurement_target": {
            "finished_device_quantity": 1,
            "deliverable": "one fully assembled Leshy2 prototype built without factory engineering choices",
            "display": "one exact EastRising ER-TFT035IPS-6 + ER-TPC035-6 option 5344 panel retained by one ready-cut 3M (TC) 4910SQ-2(5), installed and mated by the factory in that prototype after the explicit stack/clearance and written process gates close",
            "first_power_on": "owner USB-powered bring-up after delivery: known image, backlight and touch",
            "factory_function_test": "optional quote-only insurance; not required and not a release gate",
            "batteries_included": False,
            "factory_attrition_rule": "extra display units, connectors and flex components belong to quoted factory attrition and are not user samples",
            "hmx_donor_route": "rejected procurement route; legacy evidence only",
            "separate_engineering_sample_purchase": False,
            "coupon_board_phase": False,
            "physical_evidence_execution": "owner H7 arrival/bring-up and H8 qualification on the sole prototype and ordinary accessories",
            "article_manifest_scope": "factory-installed production parts, factory-packed accessories where accepted, and ordinary owner-supplied operating items; it is not a second commercial order",
        },
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
            "unpriced_manufacturer_lines": len(unpriced),
            "excluded_from_budget": ["factory display attrition", "SA818S-V pre-order freight/lead-time charge", "J4-F box-build", "J4-P kit/packing", "freight", "tax", "customs", "general laboratory instruments and ordinary passives"],
            "former_parked_plan_usd": "164.54 for only a partial eight-line lot",
            "comparison_note": "The priced subtotal includes the exact one-piece production panel and one exact ready-cut display PSA square; it excludes only factory attrition and services. These lines form the integrated sole-prototype/bring-up manifest, not a separate sample basket or device batch.",
        },
        "group_budget_usd": {key: f"{value:.2f}" for key, value in sorted(groups.items())},
        "articles": ARTICLES,
        "measurements": MEASUREMENTS,
        "supply_constraints": {
            "selected_uhf": {"mpn": "G-NiceRF SA818S-U", "jlcpcb_part": "C3001549", "stock": 68, "available_order_quantity": 60, "quantity_one_usd": "9.7347", "status": "priced_in_stock"},
            "selected_vhf": {"mpn": "G-NiceRF SA818S-V", "jlcpcb_part": "C51897911", "stock": 0, "minimum_quantity": 1, "quantity_one_usd": "10.0710", "status": "priced_preorder_lead_time_open"},
            "qualified_pending_uhf_alternate": {"mpn": "G-NiceRF SA818S-CE", "jlcpcb_part": "C19632390", "stock": 8, "quantity_one_usd": "9.3449", "status": "not_in_order_manifest", "restriction": "may replace only SA818S-U after owner HIL and a 470-MHz firmware clamp; never replaces SA818S-V and never substitutes silently"},
            "orders_or_requests_submitted": 4,
            "supplier_information_inquiries_submitted": 4,
            "sourcing_requests_submitted": 0,
            "orders_submitted": 0,
            "submitted_inquiry": {
                "supplier": "JLCPCB",
                "channel": "Contact Us / PCB Assembly Inquiry",
                "submitted_on": "2026-08-26",
                "result": "successfully_submitted",
                "ticket_number": None,
                "scope": "information only; no order, quote project, sourcing request or reservation",
            },
            "submitted_clarification": {
                "supplier": "JLCPCB",
                "channel": "Gmail",
                "submitted_on": "2026-09-01",
                "from": "vinogradov.anton@gmail.com",
                "to": "support@jlcpcb.com",
                "result": "message_sent",
                "scope": "exactly one prototype; information only; no order, pre-order, quote, reservation, sourcing request or fabrication",
            },
            "submitted_display_psa_clarification": {
                "supplier": "JLCPCB",
                "channel": "Gmail",
                "submitted_on": "2026-09-01",
                "submitted_at_local": "19:25 Europe/Moscow",
                "from": "vinogradov.anton@gmail.com",
                "to": "support@jlcpcb.com",
                "result": "message_sent",
                "source_reference": "hardware/procurement/H5.0.3-R1-jlcpcb-display-psa-clarification.md",
                "scope": "exact 3M (TC) 4910SQ-2(5), deterministic FPC/ZIF/pressure process and exactly one prototype; information only; no commercial action",
            },
            "submitted_fallback_inquiry": {
                "supplier": "PCBWay",
                "channel": "Gmail",
                "submitted_on": "2026-09-02",
                "submitted_at_local": "20:14 Europe/Moscow",
                "from": "vinogradov.anton@gmail.com",
                "to": "service@pcbway.com",
                "result": "message_sent",
                "source_reference": "hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md",
                "scope": "exactly one prototype; information only; no order, quote project, sourcing request, reservation or purchase",
            },
            "jlcpcb_ticket_merge": {
                "received_on": "2026-09-02",
                "from": "mitchell@jlcpcb.com",
                "to": "vinogradov.anton@gmail.com",
                "merged_into_ticket": "TKEM2026082605925",
                "substantive_release_answer": False,
                "source_reference": "hardware/procurement/H5.0.3-R1-jlcpcb-ticket-merge-2026-09-02.md",
            },
            "jlcpcb_substantive_response": {
                "received_on": "2026-09-02",
                "from": "support@jlcpcb.com",
                "to": "av@apache.org",
                "viewed_in_gmail_account": "no.mail.in@gmail.com",
                "result": "pcba_only_accepted_full_device_declined",
                "exact_dual_module_placement": True,
                "exact_mpn_and_no_silent_substitution": True,
                "pcba_minimum_quantity": 2,
                "special_process_preorder_acceptance": False,
                "complete_enclosure_assembly": False,
                "source_reference": "hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md",
            },
            "next_action": "wait for PCBWay's written response to the exact-one full-device questionnaire; JLCPCB remains the PCBA-only reference after explicitly declining complete enclosure assembly and deferring special-process feasibility until after order",
        },
        "sequencing": {
            "now": "wait for PCBWay's substantive full-device response; retain JLCPCB's accepted exact dual-module/no-substitution PCBA route but not as the final-device assembler, while Function Test, batteries and accessory packing remain optional or owner-supplied",
            "after_mapping": "use approved read-only Parts access for repeatable availability checks when permission becomes usable; no additional submission is required for the current gate",
            "after_quote": "publish exact sole-prototype and final-assembly costs, close the H5 supplier/manifest gate, then continue through H6 and the existing single H7 prototype-order approval",
            "after_order": "H7 records arrival identity, assembly and first owner bring-up; H8 executes the retained fit, RF, thermal, audio, control and interoperability contracts on that prototype and ordinary accessories",
            "forbidden": ["separate engineering-sample purchase", "H5 coupon-board fabrication", "PCB placement/routing before H5 closes", "prototype fabrication before H6 and F-PO"],
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
        return f"""# H5.0.3 · единый article manifest прототипа

[English](component-sample-basket.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Предыдущий поиск](component-source-research.ru.md)

Цель `H5.0.3-R1` — один order-integrated manifest для ровно **одного полностью собранного прототипа Leshy2** и его обычных bring-up accessories. Отдельной закупки engineering samples и отдельной H5 coupon-платы нет. Manifest объединяет установленные фабрикой production parts, принятые фабрикой packed accessories и обычные owner-supplied operating items; это не второй коммерческий заказ. Фабрика по закрытому production package устанавливает точный `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 на готовый квадрат `3M (TC) 4910SQ-2(5)` и стыкует его через `FH34SRJ-50S-0.5SH(50)` без инженерных догадок — после закрытия измерительного и письменного supplier gate. Первый полный power-on и USB bring-up изображения, подсветки и touch выполняет владелец в H7; физическая квалификация продолжается на том же прототипе в H8. Платный factory Function Test — только optional quote-insurance, а не gate. Аккумуляторы не устанавливаются и не поставляются. HMX035CTFT-001 и полные donor-board остаются только legacy evidence и не являются маршрутом закупки. [JLCPCB Standard PCBA остаётся неэксклюзивным производственным ориентиром](manufacturing-platform.ru.md). Закупка, sourcing request, quote/reservation, PCB placement/routing и fabrication пока не разрешены.

```mermaid
flowchart TD
  R["✅ H5.0.2-R1<br/>источники и замены"] --> B["▶️ H5.0.3-R1<br/>единый order manifest"]
  B --> P["JLCPCB Standard<br/>210 строк · 1050 установок"]
  P --> Q["пересборка маршрутов<br/>J0–J3 · J4-F/P"]
  Q --> S["SA818S-V<br/>final pre-order quote"]
  Q --> X["J4-F box-build<br/>J4-P kit/shipping"]
  S --> A["цена одного прототипа<br/>+ factory attrition"]
  X --> A
  A --> H6["H6<br/>KiCad release"]
  H6 --> H7["H7<br/>1 прототип + owner bring-up"]
  H7 --> H8["H8<br/>qualification того же прототипа"]
```

## Сводка стоимости

- **${summary['known_engineering_material_budget_usd']}** — известный консервативный material budget для всех priced lines.
- Внутри него **${summary['published_price_subtotal_usd']}** — публичные USD-цены и **${summary['conservative_budget_caps_usd']}** — два консервативных cap для дешёвых IR-деталей, чьи live-страницы показывают цену в AUD/INR.
- В сумму включены exact `SA818S-U` `C3001549` за `$9.7347` и exact `SA818S-V` `C51897911` за `$10.0710`; у VHF-модуля stock `0`, MOQ 1 и типичные 8–15 рабочих дней, а final quote/lead остаются order-time gate.
- Точный production panel за `$14.91` и один готовый квадрат `3M (TC) 4910SQ-2(5)` за `$22.12` включены. Квадрат не требует ручной вырубки; его использование остаётся fail-closed до измерения folded-FPC stack `≤0.714 mm`, фактического зазора `≥0.20 mm` и письменного согласия фабрики на J4-F установку с равномерно поддержанным давлением `≥100 kPa`.
- Не включены только factory attrition, финальная сборка/FCT, доставка, налоги и таможня. Любые дополнительные экземпляры дисплея или коннекторов входят в attrition фабричного quote, а не в пользовательские samples; отдельного H5 coupon-заказа нет.
- Старая сумма `$164.54` была не дешёвой полной корзиной, а неполным набором из восьми строк; она не покрывала большинство H5 gates.

## Что входит в единый manifest

{group_sections(data, True)}

## Контракты owner bring-up H7/H8

Все `{summary['covered_residuals_and_gates']}` residual/gate покрыты `{summary['measurement_contracts']}` контрактами. Они исполняются после получения единственного прототипа в H7/H8, а не отдельной закупкой samples/coupons. Pass/fail без raw evidence не принимается.

{measurement_sections(data, True)}

## Открытые supplier inputs

Цена каждого выбранного модуля известна. [Содержательный ответ JLCPCB от 2 сентября](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md) подтверждает установку exact `SA818S-V C51897911` и `SA818S-U C3001549` на разных designator через BOM Matching, exact-MPN incoming control и запрет замены без подтверждения. Одновременно JLCPCB установил PCBA MOQ 2, отказался от полной сборки корпуса/устройства и оставил клей, FPC и пять microcoax только на post-order review. Поэтому JLCPCB остаётся PCBA-only reference, а [information-only запрос PCBWay](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md), отправленный 2 сентября с `vinogradov.anton@gmail.com`, теперь является активным full-device gate. Function Test, аккумуляторы и упаковка аксессуаров не являются gate. `SA818S-CE C19632390` остаётся только qualified-pending UHF-заменой после HIL и firmware-clamp 470 МГц. Quote, reservation и заказ не создавались.

Машинный результат: [`H5-EVR03`](../hardware/verification/generated/H5-EVR03-irreducible-sample-basket.json).
"""
    return f"""# H5.0.3 · sole-prototype article manifest

[Русский](component-sample-basket.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Previous research](component-source-research.md)

The `H5.0.3-R1` target is one order-integrated manifest for exactly **one fully assembled Leshy2 prototype** and its ordinary bring-up accessories. There is no separate engineering-sample purchase and no separate H5 coupon board. The manifest joins factory-installed production parts, accepted factory-packed accessories and ordinary owner-supplied operating items; it is not a second commercial order. From the released production package, the factory installs exact `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 on one ready-cut `3M (TC) 4910SQ-2(5)` and mates it through `FH34SRJ-50S-0.5SH(50)` without making engineering guesses, after the measurement and written supplier gates close. The owner performs first full USB image/backlight/touch bring-up in H7 and continues physical qualification on that same prototype in H8. Paid factory Function Test is optional quote-only insurance, not a gate. Batteries are neither installed nor supplied. HMX035CTFT-001 and complete donor boards remain legacy evidence only and are rejected as the procurement route. [JLCPCB Standard PCBA remains the non-exclusive manufacturing reference](manufacturing-platform.md). Purchase, sourcing request, quote/reservation, PCB placement/routing and fabrication remain unauthorized.

```mermaid
flowchart TD
  R["✅ H5.0.2-R1<br/>sources + replacements"] --> B["▶️ H5.0.3-R1<br/>one order manifest"]
  B --> P["JLCPCB Standard<br/>210 lines · 1050 placements"]
  P --> Q["route rebuild<br/>J0–J3 · J4-F/P"]
  Q --> S["SA818S-V<br/>final pre-order quote"]
  Q --> X["J4-F box-build<br/>J4-P kit/shipping"]
  S --> A["one-prototype price<br/>+ factory attrition"]
  X --> A
  A --> H6["H6<br/>KiCad release"]
  H6 --> H7["H7<br/>1 prototype + owner bring-up"]
  H7 --> H8["H8<br/>qualify that same prototype"]
```

## Cost summary

- **${summary['known_engineering_material_budget_usd']}** is the known conservative material budget for every priced line.
- It contains **${summary['published_price_subtotal_usd']}** of published USD prices and **${summary['conservative_budget_caps_usd']}** of conservative caps for two cheap IR parts whose live pages expose AUD/INR prices.
- The total includes exact `SA818S-U` `C3001549` at `$9.7347` and exact `SA818S-V` `C51897911` at `$10.0710`; the VHF module has zero stock, MOQ 1 and a typical 8–15-working-day lead, while final quote/lead remain an order-time gate.
- The exact production panel at `$14.91` and one ready-cut `3M (TC) 4910SQ-2(5)` at `$22.12` are included. The square requires no owner cutting; its use remains fail-closed until the folded-FPC stack measures `≤0.714 mm`, actual clearance is `≥0.20 mm`, and the factory accepts J4-F installation with uniformly backed `≥100 kPa` pressure in writing.
- Only factory attrition, final assembly/FCT, freight, taxes and customs are excluded. Any additional display or connector units belong to the factory attrition quote, not to user samples; there is no separate H5 coupon order.
- The former `$164.54` was not a cheaper complete basket: it covered only eight partial lines and omitted most H5 gates.

## Integrated order and bring-up articles

{group_sections(data, False)}

## H7/H8 owner evidence contracts

All `{summary['covered_residuals_and_gates']}` residuals/gates are covered by `{summary['measurement_contracts']}` contracts. They execute after the sole prototype arrives in H7/H8, not through a separate sample/coupon purchase. A pass/fail summary without raw evidence is not accepted.

{measurement_sections(data, False)}

## Open supplier inputs

Both selected module prices are known. JLCPCB's [substantive 2 September response](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md) confirms separate-designator placement of exact `SA818S-V C51897911` and `SA818S-U C3001549` through BOM Matching, exact-MPN incoming control and no replacement without customer confirmation. It also sets PCBA MOQ 2, declines complete enclosure/final-device assembly, and leaves adhesive, FPC and five-microcoax feasibility to post-order review. JLCPCB therefore remains the PCBA-only reference, while the [information-only PCBWay inquiry](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md), sent on 2 September from `vinogradov.anton@gmail.com`, is now the active full-device gate. Function Test, batteries and accessory packing are not gates. `SA818S-CE C19632390` remains only a qualified-pending UHF alternate after HIL and a 470-MHz firmware clamp. No quote, reservation or order was created.

Machine result: [`H5-EVR03`](../hardware/verification/generated/H5-EVR03-irreducible-sample-basket.json).
"""


def render_legacy_pointer() -> str:
    return """# H5 sole-prototype article manifest

This former hand-maintained partial plan has been superseded by the generated,
fully covered H5.0.3 order-integrated manifest:

- [readable sole-prototype manifest](../../docs/component-sample-basket.md);
- [machine manifest and H7/H8 evidence contracts](../verification/generated/H5-EVR03-irreducible-sample-basket.json);
- [Russian page](../../docs/component-sample-basket.ru.md).

The old quantities and `$164.54` partial subtotal are intentionally not an
ordering source. There is no separate engineering-sample or H5 coupon order:
the listed production parts and ordinary bring-up accessories join the sole
prototype order, and H7/H8 execute the evidence contracts after delivery.
PCB placement/routing and fabrication remain unauthorized. The VHF pre-order
route is recorded; the nine exact-one supplier answers remain open while the
integrated manifest is rebuilt.
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
        "ok: H5.0.3-R1 order-integrated manifest covers "
        f"{data['summary']['covered_residuals_and_gates']} residuals/gates with "
        f"{data['summary']['article_lines']} article lines and "
        f"{data['summary']['measurement_contracts']} measurement contracts; "
        f"known material budget ${data['summary']['known_engineering_material_budget_usd']}; "
        "no separate sample/coupon order; exact production panel selected, factory-attrition and remaining factory gates open"
    )


if __name__ == "__main__":
    main()
