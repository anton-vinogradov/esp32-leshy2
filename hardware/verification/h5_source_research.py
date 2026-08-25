#!/usr/bin/env python3
"""Publish the H5.0.2 primary-source and serial-alternative review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
INPUT = REPO / "hardware/verification/generated/H5-EVR01-residual-map.json"
OUTPUT = REPO / "hardware/verification/generated/H5-EVR02-source-research.json"
DOC_EN = REPO / "docs/component-source-research.md"
DOC_RU = REPO / "docs/component-source-research.ru.md"
CHECKED_ON = "2026-08-25"


SOURCES = {
    "ebyte_e01": {
        "owner": "Chengdu Ebyte",
        "title": "E01-ML01IPX product page",
        "url": "https://www.ebyte.com/product/47.html",
        "supports": "exact module identity, nRF24L01P, external IPEX interface, 12 x 19 mm body and SPI role",
    },
    "ebyte_e01_datasheet": {
        "owner": "Chengdu Ebyte",
        "title": "E01 series user manual",
        "url": "https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf",
        "supports": "current manufacturer electrical and module-outline evidence",
    },
    "ebyte_cable": {
        "owner": "Chengdu Ebyte",
        "title": "XC-IPX-SMA-15 product page",
        "url": "https://www.ebyte.com/product/2040.html",
        "supports": "serial IPEX-1 to SMA-K, 150 mm RF1.13 cable identity",
    },
    "te_2118651": {
        "owner": "TE Connectivity",
        "title": "2118651-2 product page",
        "url": "https://www.te.com/en/product-2118651-2.html",
        "supports": "active 30 mm UMCC Gen 1 plug-to-plug, 1.13 mm, 50 ohm, 9 GHz cable identity and drawings",
    },
    "digikey_2118651": {
        "owner": "DigiKey",
        "title": "2118651-2 authorized-distributor listing",
        "url": "https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2118651-2/16538824",
        "supports": "current authorized-distributor lifecycle, stock and price evidence at review time",
    },
    "m5_u214": {
        "owner": "M5Stack",
        "title": "Cap LoRa-1262 (U214) documentation",
        "url": "https://docs.m5stack.com/en/cap/Cap_LoRa-1262",
        "supports": "exact U214 SKU, 84 x 24 x 15.2 mm envelope, pin map and official schematic/model links",
    },
    "m5_u214_schematic": {
        "owner": "M5Stack",
        "title": "U214 schematic V1.1",
        "url": "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1208/U214-sche-Cap-LoRa1262_SCH_V1.1_20251029_2025_11_07_22_53_19.pdf",
        "supports": "P1 is specified only as generic HDR-SMD_14P-P2.54; no fitted-header manufacturer MPN or metallurgy is disclosed",
    },
    "m5_u214_structure": {
        "owner": "M5Stack",
        "title": "U214 structure files",
        "url": "https://github.com/m5stack/M5_Hardware/tree/master/Products/U214_Cap_LoRa-1262/Structures",
        "supports": "official STL structure evidence without a fitted-header BOM identity",
    },
    "lcdwiki_es3c35p": {
        "owner": "LCDWiki",
        "title": "3.5-inch ESP32-S3 display ES3C35P",
        "url": "https://www.lcdwiki.com/3.5inch_ESP32-S3_Display",
        "supports": "orderable complete donor SKU ES3C35P/ES3C35P-NS and 3.5-inch 320 x 480 ST77922 QSPI capacitive-touch class",
    },
    "lcdwiki_es3c35p_spec": {
        "owner": "LCDWiki",
        "title": "ES3C35P specification V1.0",
        "url": "https://www.lcdwiki.com/res/ES3C35P/3.5inch_IPS_ESP32-S3_Specification_V1.0.pdf",
        "supports": "official complete-board dimensions, display timing/interface and connector evidence",
    },
    "sandisk_endurance": {
        "owner": "SanDisk",
        "title": "High Endurance microSD product page",
        "url": "https://shop.sandisk.com/it-it/products/memory-cards/microsd-cards/sandisk-high-endurance-uhs-i-microsd?sku=SDSQQNR-032G-GN6IA",
        "supports": "exact 32 GB SDSQQNR-032G-GN6IA serial reference, temperature range and rated sequential performance",
    },
    "tme_sandisk": {
        "owner": "TME",
        "title": "SDSQQNR-032G-GN6IA distributor page",
        "url": "https://www.tme.com/in/en/details/sdsqqnr-032g-gn6ia/memory-cards/sandisk/",
        "supports": "independent distributor identity for the exact selected reference medium",
    },
    "m5_grove": {
        "owner": "M5Stack",
        "title": "M5Stack Grove interface definition",
        "url": "https://docs.m5stack.com/en/learn/interface/grove",
        "supports": "HY2.0-4P mechanical family and official I2C, UART and GPIO signal profiles",
    },
    "m5_cables": {
        "owner": "M5Stack",
        "title": "4-pin buckled Grove cable",
        "url": "https://shop.m5stack.com/products/4pin-buckled-grove-cable",
        "supports": "serial A034-G 5 cm and A034-B 20 cm cable SKUs",
    },
    "m5_a096": {
        "owner": "M5Stack",
        "title": "Grove to Dupont conversion cable",
        "url": "https://docs.m5stack.com/en/accessory/cable/grove2dupont",
        "supports": "exact A096 20 cm instrument-breakout cable identity",
    },
}


RESIDUAL_FINDINGS = {
    "H3-PHY-017": {
        "disposition": "irreducible_received_sample",
        "sources": ["lcdwiki_es3c35p", "lcdwiki_es3c35p_spec"],
        "finding": "ES3C35P is an exact serial donor route for the HMX035CTFT-001-marked display assembly; no standalone raw-panel order identity, current-lot FPC drawing or fully documented drop-in raw replacement was found.",
        "finding_ru": "ES3C35P — точный серийный донор для сборки с маркировкой HMX035CTFT-001; самостоятельный order identity панели, чертёж FPC текущей партии и полностью документированная drop-in замена не найдены.",
        "remaining": "receive one donor/assembly and measure controller identity, rails, tail and optical/electrical behaviour",
        "remaining_ru": "получить одну donor-сборку и измерить identity контроллера, питания, шлейф, оптику и электрическое поведение",
    },
    "H3-PHY-024": {
        "disposition": "irreducible_received_sample",
        "sources": [],
        "finding": "The exact selected IR parts already have primary datasheets; orientation of the received lot and dynamic startup/capture/no-back-power behaviour are assembled-sample properties, not documentary omissions.",
        "finding_ru": "Для выбранных IR-деталей уже есть первичные datasheet; ориентация полученной партии и динамические startup/capture/no-back-power — свойства собранного образца, а не пробел документации.",
        "remaining": "run the inherited two-channel dynamic fixture on received parts",
        "remaining_ru": "прогнать принятую двухканальную динамическую fixture на полученных деталях",
    },
    "H3-PHY-028": {
        "disposition": "irreducible_received_sample",
        "sources": [],
        "finding": "MAX17320 documentation defines the interfaces and limits, but golden-image programming and blank/corrupt/exhausted-write reactions are deliberately injected state tests on received silicon.",
        "finding_ru": "Документация MAX17320 задаёт интерфейсы и пределы, но programming golden image и реакции на blank/corrupt/exhausted-write — намеренно вводимые состояния реального экземпляра.",
        "remaining": "program and fault-inject the received gauge specimen set",
        "remaining_ru": "запрограммировать полученные gauge-образцы и провести fault injection",
    },
    "H3-PHY-038": {
        "disposition": "serial_reference_selected_physical_test_open",
        "sources": ["sandisk_endurance", "tme_sandisk"],
        "finding": "SDSQQNR-032G-GN6IA is selected as the exact reference microSD; its rated performance clears the required rates on paper, while CMD6 identity, stalls and the 512 KiB buffer trace remain HIL evidence.",
        "finding_ru": "Точная эталонная microSD выбрана: SDSQQNR-032G-GN6IA. Паспортные скорости выше требований, но CMD6 identity, задержки и трасса 512-КиБ буфера остаются HIL evidence.",
        "remaining": "receive the exact card and run the existing throughput/stall/buffer contract",
        "remaining_ru": "получить точную карту и прогнать принятый throughput/stall/buffer contract",
    },
    "H3-PHY-046": {
        "disposition": "irreducible_received_sample",
        "sources": ["m5_u214", "m5_u214_schematic", "m5_u214_structure"],
        "finding": "The official schematic names P1 only as HDR-SMD_14P-P2.54 and the official structure repository adds no BOM. Manufacturer MPN, section tolerance, material and plating of the fitted post remain undisclosed.",
        "finding_ru": "Официальная схема называет P1 только HDR-SMD_14P-P2.54, а structure repository не содержит BOM. MPN, допуск сечения, материал и покрытие установленного штыря не опубликованы.",
        "remaining": "identify and measure a received U214, then cycle the mixed U214/HLE stack",
        "remaining_ru": "идентифицировать и измерить полученный U214, затем циклировать смешанный stack U214/HLE",
    },
    "H3-PHY-048": {
        "disposition": "serial_reference_selected_physical_test_open",
        "sources": ["m5_grove", "m5_cables", "m5_a096"],
        "finding": "A034-G, A034-B and A096 form the exact short, boundary-length and instrument-breakout test set for the admitted M5 profiles; pull networks and waveforms through TXS0102 remain physical.",
        "finding_ru": "A034-G, A034-B и A096 образуют точный короткий, граничный и измерительный набор для разрешённых M5-профилей; pull-сети и формы сигналов через TXS0102 остаются физической проверкой.",
        "remaining": "receive the three exact cable SKUs and run I2C, UART, GPIO and 1-Wire profiles",
        "remaining_ru": "получить три точных cable SKU и прогнать профили I2C, UART, GPIO и 1-Wire",
    },
    "H3-PHY-053": {
        "disposition": "irreducible_received_sample",
        "sources": ["ebyte_e01", "ebyte_e01_datasheet", "ebyte_cable"],
        "finding": "Ebyte confirms an external IPEX interface but does not disclose the fitted receptacle MPN or lot axis. XC-IPX-SMA-15 was rejected because its 150 mm cable and direct SMA end are not a drop-in replacement for the selected 30 mm jumper, board receptacle and sealed edge SMA path.",
        "finding_ru": "Ebyte подтверждает внешний IPEX, но не публикует MPN и ось установленного receptacle. XC-IPX-SMA-15 отклонён: кабель 150 мм и прямой SMA не являются drop-in заменой выбранным 30-мм jumper, board receptacle и герметичному краевому SMA-тракту.",
        "remaining": "inspect the fitted receptacles and measure all three assembled RF feeds",
        "remaining_ru": "осмотреть установленные receptacle и измерить все три собранных RF-тракта",
    },
    "H3-PHY-057": {
        "disposition": "irreducible_received_sample",
        "sources": [],
        "finding": "Total AMI capacitance includes the received edge SMA, routed PCB and completed controlled pod; no component substitution can prove the capacitance of that assembled path.",
        "finding_ru": "Полная AMI-ёмкость включает полученный краевой SMA, разведённую PCB и собранный controlled pod; замена отдельной детали не доказывает ёмкость всего тракта.",
        "remaining": "measure the completed exact path and reconcile it to the tuning contract",
        "remaining_ru": "измерить завершённый точный тракт и сверить его с tuning contract",
    },
    "H3-PHY-062": {
        "disposition": "selected_part_confirmed_physical_test_open",
        "sources": ["te_2118651", "digikey_2118651", "ebyte_e01", "ebyte_e01_datasheet"],
        "finding": "TE 2118651-2 remains active, fully documented and stocked by an authorized distributor. No evaluated 30 mm alternative improved its 9 GHz performance and price without changing the selected path; installed bend, strain and retention remain physical.",
        "finding_ru": "TE 2118651-2 остаётся active, полностью документирован и доступен у авторизованного дистрибьютора. Рассмотренные 30-мм альтернативы не улучшили 9-ГГц характеристики и цену без изменения тракта; изгиб, strain и retention после установки остаются физическими.",
        "remaining": "install five exact jumpers and measure bend, strain, retention and RF loss",
        "remaining_ru": "установить пять точных jumper и измерить изгиб, strain, retention и RF-потери",
    },
}


GATE_DISPOSITIONS = {
    "H5-MECH-DISPLAY-TAIL": ("donor_route_found_sample_open", ["lcdwiki_es3c35p", "lcdwiki_es3c35p_spec"]),
    "H5-MECH-NRF-GEN1-FEEDS": ("primary_sources_exhausted_sample_open", ["ebyte_e01", "ebyte_e01_datasheet", "te_2118651"]),
    "H5-MECH-U214-MATING-STACK": ("manufacturer_subpart_hidden_sample_open", ["m5_u214", "m5_u214_schematic", "m5_u214_structure"]),
    "H5-MECH-NAVIGATION-CONTROLS": ("assembled_ergonomics_sample_open", []),
    "H5-MECH-SA518-LAND-FIT": ("received_module_and_coupon_open", []),
    "H5-MECH-ENCODER-KNOB": ("assembled_ergonomics_sample_open", []),
    "H5-MECH-DIRECT-PRESS-CONTROLS": ("assembled_ergonomics_sample_open", []),
    "H5-MECH-RUN-KILL": ("assembled_ergonomics_sample_open", []),
    "H5-MECH-M5-UNIT-MATE": ("serial_test_set_selected_sample_open", ["m5_grove", "m5_cables", "m5_a096"]),
    "H5-MECH-CELL-HOLDER-FIT": ("assembled_retention_sample_open", []),
    "H5-MECH-NATIVE-RF-JUMPERS": ("selected_part_confirmed_sample_open", ["te_2118651", "digikey_2118651"]),
    "H5-MECH-DISPLAY-PERFORMANCE": ("donor_route_found_sample_open", ["lcdwiki_es3c35p", "lcdwiki_es3c35p_spec"]),
    "H5-MECH-ACOUSTIC-PATHS": ("enclosure_dependent_sample_open", []),
    "H5-MECH-HEADSET-JACK": ("assembled_mating_sample_open", []),
}


TEST_ARTICLES = [
    {
        "category": "reference_microSD",
        "identities": ["SDSQQNR-032G-GN6IA"],
        "sources": ["sandisk_endurance", "tme_sandisk"],
        "selection_status": "selected_not_ordered",
    },
    {
        "category": "M5_profile_interconnect_set",
        "identities": ["A034-G", "A034-B", "A096"],
        "sources": ["m5_cables", "m5_a096"],
        "selection_status": "selected_not_ordered",
    },
]


ALTERNATIVES = [
    {
        "target": "E01-ML01IPX RF feed",
        "candidate": "XC-IPX-SMA-15",
        "sources": ["ebyte_cable"],
        "decision": "rejected",
        "reason": "150 mm direct IPEX-to-SMA cable is not a drop-in replacement for the selected 30 mm internal jumper, PCB feed and sealed edge SMA architecture",
    },
    {
        "target": "HMX035CTFT-001 standalone panel",
        "candidate": "other 3.5-inch QSPI panels",
        "sources": ["lcdwiki_es3c35p", "lcdwiki_es3c35p_spec"],
        "decision": "rejected_as_drop_in",
        "reason": "no alternative found with a fully documented identical controller, flex contacts, outline, touch stack and connector; substitution would reopen architecture and placement",
    },
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    evidence = load(INPUT)
    residual_ids = {row["id"] for row in evidence["residuals"]}
    gate_ids = {row["id"] for row in evidence["mechanical_gates"]}
    residuals = []
    for row in evidence["residuals"]:
        finding = RESIDUAL_FINDINGS[row["id"]]
        residuals.append({
            "id": row["id"],
            "source_group": row["source_group"],
            **finding,
            "physical_claim_closed": False,
            "purchase_authorized": False,
        })
    gates = [
        {
            "id": row["id"],
            "disposition": GATE_DISPOSITIONS[row["id"]][0],
            "sources": GATE_DISPOSITIONS[row["id"]][1],
            "physical_claim_closed": False,
        }
        for row in evidence["mechanical_gates"]
    ]
    referenced_sources = {
        key
        for row in residuals + gates + TEST_ARTICLES + ALTERNATIVES
        for key in row.get("sources", [])
    }
    checks = {
        "all_nine_h5_residuals_researched": residual_ids == set(RESIDUAL_FINDINGS) and len(residuals) == 9,
        "all_fourteen_mechanical_gates_dispositioned": gate_ids == set(GATE_DISPOSITIONS) and len(gates) == 14,
        "exactly_two_previously_open_test_article_categories_selected": len(TEST_ARTICLES) == 2,
        "every_selected_test_article_has_exact_non_tbd_serial_identity": all(row["identities"] and all(identity and "TBD" not in identity.upper() for identity in row["identities"]) for row in TEST_ARTICLES),
        "every_selected_test_article_has_a_primary_or_distributor_source": all(row["sources"] for row in TEST_ARTICLES),
        "every_referenced_external_source_is_registered": referenced_sources <= set(SOURCES),
        "all_evaluated_replacements_have_an_explicit_decision_and_reason": all(row["decision"] and row["reason"] for row in ALTERNATIVES),
        "no_received_sample_claim_is_closed_by_document_search": all(not row["physical_claim_closed"] for row in residuals + gates),
        "purchase_layout_and_fabrication_are_not_authorized": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H5.0.2 source-research checks failed: " + ", ".join(failed))
    return {
        "schema_version": 1,
        "stage": "H5.0.2",
        "status": "reviewed_research_only",
        "checked_on": CHECKED_ON,
        "purpose": "exhaust primary documentary evidence and fully documented serial alternatives before proposing any received sample",
        "input": {"path": str(INPUT.relative_to(REPO)), "sha256": sha256(INPUT)},
        "summary": {
            "h5_residuals_researched": len(residuals),
            "mechanical_gates_dispositioned": len(gates),
            "test_article_categories_selected": len(TEST_ARTICLES),
            "exact_test_article_skus_selected": sum(len(row["identities"]) for row in TEST_ARTICLES),
            "alternatives_explicitly_evaluated": len(ALTERNATIVES),
            "physical_claims_closed": 0,
            "orders_authorized": 0,
        },
        "sources": {key: SOURCES[key] for key in sorted(referenced_sources)},
        "residuals": residuals,
        "mechanical_gates": gates,
        "selected_test_articles": TEST_ARTICLES,
        "evaluated_alternatives": ALTERNATIVES,
        "checks": checks,
        "decision_boundary": {
            "accepted_now": "the documentary search result, exact microSD and M5 interconnect test identities, and rejected non-drop-in alternatives",
            "not_accepted": "any received-lot identity, fit, retention, RF, timing, acoustic, thermal, endurance or fault-injection claim",
            "next": "H5.0.3 deduplicates the irreducible received-sample basket, measurements and current cost for explicit approval",
            "purchase_authorized": False,
            "pcb_placement_and_routing_authorized": False,
            "fabrication_authorized": False,
        },
    }


def source_links(keys: list[str], russian: bool = False) -> str:
    if not keys:
        return "первичные datasheet уже выбранных деталей из H5-EVR01" if russian else "existing selected-part primary datasheets in H5-EVR01"
    return ", ".join(f"[{SOURCES[key]['owner']}]({SOURCES[key]['url']})" for key in keys)


def residual_sections(data: dict, russian: bool) -> str:
    sections = []
    for row in data["residuals"]:
        finding = row["finding_ru"] if russian else row["finding"]
        remaining_value = row["remaining_ru"] if russian else row["remaining"]
        label = "Источники" if russian else "Sources"
        outcome = "Итог" if russian else "Outcome"
        remaining = "Осталось физически" if russian else "Still physical"
        sections.append(
            f"### `{row['id']}` · `{row['source_group']}`\n\n"
            f"- {outcome}: {finding}\n"
            f"- {label}: {source_links(row['sources'], russian)}.\n"
            f"- {remaining}: {remaining_value}."
        )
    return "\n\n".join(sections)


def render_doc(data: dict, russian: bool) -> str:
    if russian:
        return f"""# H5.0.2 · поиск источников и серийных замен

[English](component-source-research.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

Ревью проведено {CHECKED_ON}: первичные документы и серийные альтернативы проверены до закупки. Выбраны точные тестовые identities для двух прежних пробелов; ни один физический claim не закрыт и заказ не разрешён.

```mermaid
flowchart LR
  M["✅ H5.0.1<br/>9 residuals + 14 gates"] --> R["✅ H5.0.2<br/>поиск исчерпан"]
  R --> I["2 закрытых selection gaps<br/>4 точных SKU"]
  R --> S["▶️ H5.0.3<br/>неустранимые образцы + стоимость"]
  S -. "только после явного согласия" .-> B["закупка"]
```

## Что улучшилось без закупки

- Эталонная microSD: `SDSQQNR-032G-GN6IA`.
- Набор M5-проводов: `A034-G`, `A034-B`, `A096`.
- Для дисплея найден серийный донор `ES3C35P`; raw-панель всё ещё нельзя честно квалифицировать без образца.
- `TE 2118651-2` подтверждён как active и документированный; менять его нет оснований.
- Для stock `U214` и `E01-ML01IPX` производители действительно не раскрывают MPN установленных connector subparts.

## Результат по девяти residuals

{residual_sections(data, True)}

## Проверенные, но отклонённые замены

- `XC-IPX-SMA-15`: серийный, но его 150-мм прямой тракт не заменяет выбранный 30-мм внутренний jumper + PCB + герметичный краевой SMA.
- Другие 3.5-дюймовые QSPI-панели: не найдена drop-in модель с одновременно теми же controller, flex contacts, outline, touch stack и connector.

## Честная граница

- Все 9 residuals и 14 mechanical gates получили явный research disposition.
- Документами не закрыт ни один fit/RF/timing/acoustic/thermal/retention claim.
- Точные тестовые SKU **выбраны, но не заказаны**.
- PCB placement/routing и fabrication остаются запрещены.
- Точный следующий маркер: `H5.0.3` — единый недублирующийся набор только неустранимых образцов, измерения и текущая стоимость для отдельного согласования.

Машинный результат: [`H5-EVR02`](../hardware/verification/generated/H5-EVR02-source-research.json).
"""
    return f"""# H5.0.2 · primary-source and serial-alternative research

[Русский](component-source-research.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

Review completed on {CHECKED_ON}: primary documents and serial alternatives were exhausted before purchase. Exact test identities close two former selection gaps; no physical claim is closed and no order is authorized.

```mermaid
flowchart LR
  M["✅ H5.0.1<br/>9 residuals + 14 gates"] --> R["✅ H5.0.2<br/>research exhausted"]
  R --> I["2 selection gaps closed<br/>4 exact SKUs"]
  R --> S["▶️ H5.0.3<br/>irreducible samples + cost"]
  S -. "explicit approval only" .-> B["purchase"]
```

## What improved without a purchase

- Reference microSD: `SDSQQNR-032G-GN6IA`.
- M5 interconnect set: `A034-G`, `A034-B`, `A096`.
- A serial `ES3C35P` display donor route is identified; the raw panel still cannot be honestly qualified without a received sample.
- `TE 2118651-2` is confirmed active and documented; replacement has no demonstrated benefit.
- The makers of stock `U214` and `E01-ML01IPX` genuinely do not disclose the fitted connector-subpart MPNs.

## Result for the nine residuals

{residual_sections(data, False)}

## Evaluated and rejected alternatives

- `XC-IPX-SMA-15`: serial, but its 150 mm direct path does not replace the selected 30 mm internal jumper + PCB + sealed edge SMA.
- Other 3.5-inch QSPI panels: no drop-in model was found with the same controller, flex contacts, outline, touch stack and connector together.

## Honest boundary

- All 9 residuals and 14 mechanical gates now have an explicit research disposition.
- Documents close no fit/RF/timing/acoustic/thermal/retention claim.
- Exact test SKUs are **selected, not ordered**.
- PCB placement/routing and fabrication remain prohibited.
- Exact next marker: `H5.0.3` — one deduplicated basket of irreducible samples, measurements and current cost for separate approval.

Machine result: [`H5-EVR02`](../hardware/verification/generated/H5-EVR02-source-research.json).
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
            raise SystemExit("stale H5.0.2 artifacts: " + ", ".join(stale))
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    data = build()
    print(
        "ok: H5.0.2 researched "
        f"{data['summary']['h5_residuals_researched']} residuals and "
        f"{data['summary']['mechanical_gates_dispositioned']} mechanical gates; "
        f"selected {data['summary']['exact_test_article_skus_selected']} exact test SKUs; "
        "physical closures 0"
    )


if __name__ == "__main__":
    main()
