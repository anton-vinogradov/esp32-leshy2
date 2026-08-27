#!/usr/bin/env python3
"""Validate and render the H1-R2 analog-FPV module boundary."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-fpv.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-fpv-audit.json"
SVG_PATH = REPO / "docs/images/h1-r2-fpv-path.svg"
EN_DOC_PATH = REPO / "docs/h1-r2-fpv.md"
RU_DOC_PATH = REPO / "docs/h1-r2-fpv.ru.md"


def load() -> dict:
    return json.loads(MODEL_PATH.read_text())


def audit(model: dict) -> dict:
    receiver = model["receiver"]
    antenna = model["antenna"]
    alternate = antenna["supply_independent_alternate"]
    outreach = model["supplier_outreach"]
    pins = {row["pin"]: row for row in receiver["pinout"]}
    errors: list[str] = []
    if set(pins) != set(range(1, 15)):
        errors.append("K331 pinout is not the complete 1..14 set")
    expected_controls = {1: "GPIO32", 2: "GPIO33", 3: "GPIO34", 5: "GPIO30"}
    for pin, token in expected_controls.items():
        if token not in pins[pin]["owner"]:
            errors.append(f"K331 pin {pin} does not use reserved {token}")
    if pins[6]["name"] != "RSSI (NC)" or "No connect" not in pins[6]["owner"]:
        errors.append("K331 pin 6 is overstated as an available RSSI output")
    if receiver["maximum_current_ma"] > model["power_fit"]["reserved_active_5v_ma"]:
        errors.append("K331 exceeds the reserved active 5-V budget")
    antenna_covers_receiver_band = (
        antenna["frequency_mhz"][0] <= receiver["frequency_mhz"][0]
        and antenna["frequency_mhz"][1] >= receiver["frequency_mhz"][1]
    )
    if not antenna_covers_receiver_band:
        errors.append("selected antenna does not cover the complete K331 band")
    if antenna["termination"] != "MMCX plug":
        errors.append("selected antenna does not mate the external MMCX")
    if not (
        alternate["frequency_mhz"][0] <= receiver["frequency_mhz"][0]
        and alternate["frequency_mhz"][1] >= receiver["frequency_mhz"][1]
    ):
        errors.append("supply-independent antenna alternate does not cover K331")
    if not alternate["termination"].startswith("MMCX male"):
        errors.append("supply-independent antenna alternate does not mate MMCX")
    if not any("without U.FL or cable" in step for step in model["signal_path"]):
        errors.append("the selected same-board RF path regressed to U.FL")
    if receiver["jlcpcb_surface"]["accepted_for_factory_placement"]:
        errors.append("K331 factory placement is claimed without a JLCPCB route")
    official = receiver.get("official_integration_evidence", {})
    required_official_evidence = {"application_circuit", "pinout", "channel_table"}
    if not required_official_evidence.issubset(official):
        errors.append("official K331 integration evidence is incomplete")
    if any("akktek.com/media/catalog/product/" not in official.get(key, "") for key in required_official_evidence):
        errors.append("official K331 integration evidence is not manufacturer-hosted")
    if official.get("does_not_cover") != "maximum body dimensions, pad pitch and land geometry, packaging or reflow profile":
        errors.append("official K331 media no longer preserves the physical-evidence boundary")
    mechanical = receiver["mechanical"]
    if mechanical.get("nominal_board_xy_mm") != [28.7, 23.1]:
        errors.append("K331 nominal XY corroboration is missing or stale")
    if mechanical.get("working_envelope_mm") != [30.0, 24.0, 4.0]:
        errors.append("K331 conservative collision reserve is missing or stale")
    if "reseller" not in mechanical.get("nominal_board_xy_source_class", ""):
        errors.append("K331 nominal XY evidence is overstated as controlled")
    alternatives = {row["mpn"]: row for row in model["receiver_alternatives_reviewed"]}
    if set(alternatives) != {"AKK K331", "AWM666V RX", "AWM682 RX", "TUE-RFVRX-58-D", "SP166RX", "MM238R-MCU", "RichWave RTC6715 IC", "generic RX5808"}:
        errors.append("receiver alternative review is incomplete")
    controlled_fallback = alternatives.get("AWM666V RX", {})
    if controlled_fallback.get("controlled_envelope_mm") != [26.16, 16.38, 3.7]:
        errors.append("AWM666V controlled fallback envelope is missing or stale")
    if not controlled_fallback.get("fits_k331_working_envelope"):
        errors.append("AWM666V no longer fits the K331 reserve")
    if controlled_fallback.get("jlcpcb_surface", {}).get("placeable_hits") != 0:
        errors.append("AWM666V factory route is overstated")
    if controlled_fallback.get("channel_count") >= receiver["channel_count"]:
        errors.append("AWM666V channel degradation is no longer explicit")
    if alternatives.get("AWM682 RX", {}).get("controlled_envelope_mm", [0, 0])[1] <= model["receiver"]["mechanical"]["working_envelope_mm"][1]:
        errors.append("AWM682 rejection no longer proves a larger controlled body")
    if alternatives.get("TUE-RFVRX-58-D", {}).get("maximum_current_ma", 0) <= model["power_fit"]["reserved_active_5v_ma"]:
        errors.append("Top-Unum rejection no longer proves a power overrun")
    sp166rx = alternatives.get("SP166RX", {})
    if sp166rx.get("controlled_board_xy_mm", [0, 0])[0] <= mechanical["working_envelope_mm"][0] or sp166rx.get("controlled_board_xy_mm", [0, 0])[1] <= mechanical["working_envelope_mm"][1]:
        errors.append("SP166RX rejection no longer proves an oversized controlled board")
    if sp166rx.get("jlcpcb_surface", {}).get("placeable_hits") != 0 or "contradict" not in sp166rx.get("result", ""):
        errors.append("SP166RX factory or specification rejection is no longer explicit")
    mm238r = alternatives.get("MM238R-MCU", {})
    if mm238r.get("working_envelope_mm") != [28.0, 23.0, 3.0] or mm238r.get("jlcpcb_surface", {}).get("placeable_hits") != 0:
        errors.append("MM238R-MCU fit or factory-route evidence is stale")
    if "discontinued" not in mm238r.get("availability", "") or mm238r.get("controlled_mechanical_drawing"):
        errors.append("MM238R-MCU supply and documentary rejection is no longer fail-closed")
    searches = {row["query"]: row for row in receiver["jlcpcb_surface"]["searches"]}
    if set(searches) != {"AKK K331", "RX5808", "RTC6715", "SP166RX", "MM238R-MCU"}:
        errors.append("JLCPCB receiver search surface is incomplete")
    if any(row["placeable_hits"] != 0 for row in searches.values()):
        errors.append("a JLCPCB receiver route is marked placeable without live stock")
    rtc = alternatives.get("RichWave RTC6715 IC", {})
    if rtc.get("jlcpcb_part") != "C7464354" or rtc.get("jlcpcb_surface", {}).get("stock") != 0:
        errors.append("exact RichWave RTC6715 factory evidence is stale")
    if "without a public reference application" not in rtc.get("datasheet_status", ""):
        errors.append("RTC6715 custom-RF rejection lost its documentation gate")
    rx5808 = alternatives.get("generic RX5808", {})
    if rx5808.get("jlcpcb_part") != "C9900139392" or rx5808.get("jlcpcb_surface", {}).get("stock") != 0:
        errors.append("generic RX5808 factory evidence is stale")
    if outreach.get("sent_on") != model["checked_on"]:
        errors.append("supplier outreach date is missing or stale")
    if set(outreach) != {"sent_on", "akk", "jlcpcb"}:
        errors.append("supplier outreach does not cover both AKK and JLCPCB")
    if "pending" not in outreach["akk"].get("status", ""):
        errors.append("AKK production-package request must remain fail-closed until the reply arrives")
    if "response received" not in outreach["jlcpcb"].get("status", ""):
        errors.append("JLCPCB factory-route response is missing")
    route = receiver["jlcpcb_surface"].get("consigned_parts_route", {})
    if not route.get("selected") or not route.get("approval_required_before_shipment"):
        errors.append("the conditional K331 Consigned Parts route is not explicit")
    current_blockers = model["current_h1_blockers"]
    downstream = model["downstream_verification"]
    if len(current_blockers) != 1:
        errors.append("FPV must expose exactly the one present H1 blocker")
    if any(not row.get("stage") or not row.get("requirement") for row in downstream):
        errors.append("downstream FPV verification must retain an owning stage and requirement")
    if any(row["stage"] == "H1" for row in downstream):
        errors.append("a downstream FPV verification item is still owned by H1")
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "pass" if not errors else "fail",
        "functional_and_pin_fit": not errors,
        "receiver": receiver["mpn"],
        "antenna": antenna["mpn"],
        "antenna_alternate": alternate["mpn"],
        "pin_count": len(pins),
        "power_margin_ma": model["power_fit"]["margin_ma"],
        "antenna_covers_receiver_band": antenna_covers_receiver_band,
        "receiver_physical_body_accepted": receiver["mechanical"]["accepted"],
        "receiver_nominal_board_xy_mm": receiver["mechanical"]["nominal_board_xy_mm"],
        "receiver_collision_reserve_mm": receiver["mechanical"]["working_envelope_mm"],
        "factory_placement_accepted": receiver["jlcpcb_surface"]["accepted_for_factory_placement"],
        "production_acceptance": model["result"]["production_acceptance"],
        "receiver_alternatives_reviewed": len(alternatives),
        "jlcpcb_catalogue_hits": sum(row["catalogue_hits"] for row in searches.values()),
        "jlcpcb_placeable_hits": sum(row["placeable_hits"] for row in searches.values()),
        "supplier_outreach_sent_on": outreach["sent_on"],
        "official_integration_evidence": sorted(required_official_evidence),
        "supplier_responses_pending": [key for key in ("akk", "jlcpcb") if "pending" in outreach[key]["status"]],
        "current_h1_blockers": current_blockers,
        "downstream_verification": downstream,
        "errors": errors,
    }


def render_svg(model: dict) -> str:
    esc = html.escape
    nodes = [
        (35, 118, 170, "TBS5G8MMCXA", "linear 5.5–6.0 GHz"),
        (245, 118, 150, "73415-2063", "C588480 · vertical MMCX"),
        (435, 118, 150, "50 Ω PCB", "no U.FL / cable"),
        (625, 118, 150, "AKK K331", "24-channel VRX"),
        (815, 118, 170, "TVP5150AM1PBS", "UI-local CVBS → BT.656"),
        (1025, 118, 170, "ESP32-S3", "direct LCD_CAM"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1230" height="365" viewBox="0 0 1230 365">',
        '<rect width="1230" height="365" fill="#ffffff"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"/></marker><marker id="arrowBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/></marker></defs>',
        f'<text x="32" y="42" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} analog-FPV receive path</text>',
        '<text x="32" y="70" font-family="sans-serif" font-size="13" fill="#526076">Receive-only · direct rear RF trace · one 75-ohm CVBS signal crosses M1 · the decoder and LCD_CAM remain front-local.</text>',
    ]
    for x, y, w, title, subtitle in nodes:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="9" fill="#ecfccb" stroke="#4d7c0f" stroke-width="2"/>')
        out.append(f'<text x="{x+w/2}" y="{y+29}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#365314">{esc(title)}</text>')
        out.append(f'<text x="{x+w/2}" y="{y+51}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#4d7c0f">{esc(subtitle)}</text>')
    for x in (205, 395, 585, 775, 985):
        out.append(f'<path d="M{x} 154 H{x+40}" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>')
    out.extend([
        '<rect x="498" y="240" width="270" height="82" rx="9" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>',
        '<text x="633" y="266" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="700" fill="#1d4ed8">SC1512-A4 rear RP · local controls</text>',
        '<text x="633" y="290" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#1d4ed8">GP15 free · GP30 power · GP31 video lock</text>',
        '<text x="633" y="309" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#1d4ed8">GP32/33/34 → K331 CH1/CH2/CH3</text>',
        '<path d="M633 240 V194" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrowBlue)"/>',
        '<text x="32" y="347" font-family="sans-serif" font-size="11" fill="#9a3412">K331 functional/pin fit and conditional Consigned Parts route pass; the AKK production package remains the H1 gate.</text>',
        '</svg>\n',
    ])
    return "\n".join(out)


def render_doc(model: dict, result: dict, ru: bool) -> str:
    r, a = model["receiver"], model["antenna"]
    e = r["official_integration_evidence"]
    if ru:
        title = f'# {model["marker"]} · тракт аналогового FPV'
        intro = 'Принят серийный функциональный кандидат приёмника и точная антенна; физическая приёмка K331 ещё не заявлена.'
        result_text = (
            f'- `AKK {r["mpn"]}` покрывает {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} МГц, до {r["maximum_current_ma"]} мА и выдаёт CVBS 1 Vpp/75 Ω.\n'
            f'- Официальные материалы AKK подтверждают [схему включения 331RX]({e["application_circuit"]}), [функции всех 14 контактов]({e["pinout"]}) и [таблицу выбора 24 каналов]({e["channel_table"]}). AKK-брендированный кадр у продавца даёт номинальный контур платы 28,7×23,1 мм; аудит коллизий использует увеличенный резерв 30×24×4 мм.\n'
            '- CH1/CH2/CH3 используют задние RP GPIO32/33/34; GPIO30/31 обслуживают power/video-lock. Официальный pinout помечает K331 pin 6 `RSSI (NC)`, поэтому GPIO15 остаётся свободным.\n'
            f'- Резерв 5 В оставляет {result["power_margin_ma"]} мА запаса. RF идёт напрямую по 50-омной PCB-дорожке к MMCX без U.FL.\n'
            f'- Антенна `{a["mpn"]}` линейная, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} МГц, {a["gain_dbi"]} dBi, {a["cable_length_mm"]} мм; точная маркировка комплекта — `{a["printed_identity"]}`.'
            f' Независимый линейный резерв `{a["supply_independent_alternate"]["mpn"]}` покрывает 4,9–6,0 ГГц и сохраняет MMCX, но сейчас доступен только под заказ с lead time 16 недель.'
        )
        factory = (
            'Производитель показывает K331 в наличии по $29.99. JLCPCB подтвердила его отсутствие и в Parts Library, и в Global Sourcing, не нашла прямой замены и принимает оригинальные модули AKK через Consigned Parts application до отправки деталей. '
            '`RichWave RTC6715` `C7464354` и безродный `RX5808` `C9900139392` остаются недоступными карточками: склад 0, MOQ 442 и нет покупаемого module route. '
            'Точные запросы `SP166RX` и `MM238R-MCU` дали ноль результатов; первый не входит в текущую ячейку, второй не имеет контролируемой текущей production-identity и найден только как отсутствующий/снятый товар. '
            'RTC6715 — голая QFN48, а её публичный preliminary-документ 2007 года не содержит reference application или PCB layout; собственный RF/IF-тракт повысил бы риск, не решив supply. '
            'Поэтому выбран условный фабричный маршрут: оригинальная поставка AKK плюс JLCPCB Consigned Parts. '
            'Антенна за $6.95 остаётся аксессуаром комплекта после PCBA. '
            'Официальный production-пакет AKK всё ещё нужен для точной установки и consignment application; финальный DFM по Gerber/BOM/CPL и дополнительное рассмотрение function test 5 В/channel-select/CVBS следуют в H5/H6/H7.'
        )
        blockers = '\n'.join(f'- {gate}' for gate in model['current_h1_blockers'])
        downstream = '\n'.join(
            f'- **{row["stage"]}:** {row["requirement_ru"]}'
            for row in model['downstream_verification']
        )
        headings = ('## Результат', '## Фабричная граница', '## Что блокирует H1 сейчас', '## Последующая проверка — не блокирует H1')
        alternatives_heading = '## Почему K331 остаётся ведущим кандидатом'
        footer = f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.'
    else:
        title = f'# {model["marker"]} · analog-FPV receive path'
        intro = 'The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.'
        result_text = (
            f'- `AKK {r["mpn"]}` covers {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} MHz, draws at most {r["maximum_current_ma"]} mA and emits 1-Vpp/75-ohm CVBS.\n'
            f'- Official AKK-hosted media confirms the [331RX application circuit]({e["application_circuit"]}), [all 14 pin functions]({e["pinout"]}) and the [24-channel selection table]({e["channel_table"]}). An AKK-branded reseller image gives a 28.7 × 23.1 mm nominal board outline; collision audit uses an enlarged 30 × 24 × 4 mm reserve.\n'
            '- CH1/CH2/CH3 use rear-RP GPIO32/33/34; GPIO30/31 serve power/video lock. The official pinout marks K331 pin 6 `RSSI (NC)`, so GPIO15 remains free.\n'
            f'- The 5-V reserve retains {result["power_margin_ma"]} mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.\n'
            f'- `{a["mpn"]}` is linear, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} MHz, {a["gain_dbi"]} dBi and {a["cable_length_mm"]} mm; its exact kit mark is `{a["printed_identity"]}`.'
            f' Independent linear fallback `{a["supply_independent_alternate"]["mpn"]}` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.'
        )
        factory = (
            'The manufacturer lists K331 in stock at $29.99. JLCPCB confirmed that it is unavailable in both Parts Library and Global Sourcing, found no direct replacement and accepts genuine AKK modules through a Consigned Parts application before shipment. '
            'Its `RichWave RTC6715` `C7464354` and generic `RX5808` `C9900139392` cards remain unavailable: zero stock, MOQ 442 and no purchasable module route. '
            'Exact `SP166RX` and `MM238R-MCU` searches return zero results; the former does not fit the present bay, while the latter has no controlled current production identity and was found only out of stock or discontinued. '
            'RTC6715 is a bare QFN48 whose public 2007 preliminary sheet has no reference application or PCB layout; a custom RF/IF path would add risk without fixing supply. '
            'Genuine AKK supply plus JLCPCB Consigned Parts is therefore the selected conditional factory route. '
            'The $6.95 antenna remains a post-PCBA kit accessory. '
            'The official AKK production package is still required for exact placement and the consignment application; final Gerber/BOM/CPL DFM and optional 5-V/channel-select/CVBS function-test review follow in H5/H6/H7.'
        )
        blockers = '\n'.join(f'- {gate}' for gate in model['current_h1_blockers'])
        downstream = '\n'.join(
            f'- **{row["stage"]}:** {row["requirement"]}'
            for row in model['downstream_verification']
        )
        headings = ('## Result', '## Factory boundary', '## What blocks H1 now', '## Later verification — does not block H1')
        alternatives_heading = '## Why K331 remains the leading candidate'
        footer = f'> Exact current marker: **{model["marker"]}**. H1 remains in progress.'
    alternatives = '\n'.join(
        f'- `{row["mpn"]}` — {row["result_ru"] if ru else row["result"]}.'
        for row in model["receiver_alternatives_reviewed"]
    )
    return f'''{title}

[{'Главная' if ru else 'Home'}](../{'README.ru.md' if ru else 'README.md'}) · [{'English' if ru else 'Русский'}](h1-r2-fpv{'' if ru else '.ru'}.md)

{intro}

![{'Тракт аналогового FPV' if ru else 'Analog-FPV receive path'}](images/h1-r2-fpv-path.svg)

{headings[0]}

{result_text}

{alternatives_heading}

{alternatives}

{headings[1]}

{factory}

{headings[2]}

{blockers}

{headings[3]}

{downstream}

{footer}
'''


def outputs(model: dict) -> dict[Path, str]:
    result = audit(model)
    return {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        SVG_PATH: render_svg(model),
        EN_DOC_PATH: render_doc(model, result, False),
        RU_DOC_PATH: render_doc(model, result, True),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model = load()
    rendered = outputs(model)
    result = audit(model)
    if result["errors"]:
        print("\n".join(result["errors"]))
        return 1
    if args.write:
        for path, content in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, content in rendered.items() if not path.exists() or path.read_text() != content]
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
    if not args.write and not args.check:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
