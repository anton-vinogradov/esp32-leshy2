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
    candidate_oem = receiver.get("candidate_oem_family", {})
    required_official_evidence = {"application_circuit", "pinout", "channel_table"}
    if not required_official_evidence.issubset(official):
        errors.append("official K331 integration evidence is incomplete")
    if any("akktek.com/media/catalog/product/" not in official.get(key, "") for key in required_official_evidence):
        errors.append("official K331 integration evidence is not manufacturer-hosted")
    if official.get("does_not_cover") != "maximum body dimensions, pad pitch and land geometry, packaging or reflow profile":
        errors.append("official K331 media no longer preserves the physical-evidence boundary")
    candidate_geometry = candidate_oem.get("controlled_geometry", {})
    if candidate_oem.get("mpn") != "SP331RX" or candidate_oem.get("manufacturer") != "Shenzhen Sinopine Technology Co., Ltd.":
        errors.append("the controlled 331RX-family candidate identity is missing")
    if candidate_geometry.get("nominal_board_xy_mm") != [28.7, 23.1]:
        errors.append("official SP331RX nominal XY is missing or stale")
    if candidate_geometry.get("contact_pitch_mm") != 2.54 or candidate_geometry.get("contact_edge_offset_mm") != 1.4:
        errors.append("official SP331RX contact-axis geometry is missing or stale")
    if candidate_geometry.get("pin_count") != 14:
        errors.append("official SP331RX pin count is missing or stale")
    if candidate_oem.get("formal_equivalence_to_akk_k331") or candidate_oem.get("accepted_as_k331_physical_body"):
        errors.append("SP331RX evidence is overstated as accepted K331 production equivalence")
    if candidate_oem.get("retrieval_evidence", {}).get("pdf_sha256") != "6ed3b34c23092c62891a6dfcd2608f8beca6dd3b1f401c6dfb540b4c5e51756f":
        errors.append("the inspected official-origin SP331RX PDF is not hash-pinned")
    if "maximum Z" not in candidate_oem.get("does_not_cover", "") or "recommended PCB land/paste" not in candidate_oem.get("does_not_cover", ""):
        errors.append("SP331RX evidence no longer preserves the remaining assembly boundary")
    mechanical = receiver["mechanical"]
    if mechanical.get("nominal_board_xy_mm") != [28.7, 23.1]:
        errors.append("K331 nominal XY corroboration is missing or stale")
    if mechanical.get("working_envelope_mm") != [30.0, 24.0, 8.0]:
        errors.append("K331 conservative collision reserve is missing or stale")
    if "SP331RX" not in mechanical.get("nominal_board_xy_source_class", "") or "not yet formally tied" not in mechanical.get("nominal_board_xy_source_class", ""):
        errors.append("candidate SP331RX geometry is overstated as accepted K331 geometry")
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
    attachment = receiver.get("attachment_strategy", {})
    if not attachment.get("h1_accepted") or attachment.get("architecture") != "dual mutually exclusive post-PCBA land":
        errors.append("the dual post-PCBA receiver attachment is not accepted for H1")
    if attachment.get("population_rule") != "exactly one receiver module":
        errors.append("the receiver bay does not fail closed to one populated module")
    if attachment.get("primary", {}).get("mpn") != "AKK K331" or attachment.get("primary", {}).get("contact_count") != 14:
        errors.append("the tolerant K331 attachment is incomplete")
    if attachment.get("fallback", {}).get("mpn") != "AWM666V RX" or not attachment.get("fallback", {}).get("controlled_land_pattern"):
        errors.append("the exact AWM666V fallback attachment is incomplete")
    if attachment.get("normal_pcba_bom_additions") != 0:
        errors.append("the post-PCBA receiver unexpectedly entered the normal PCBA BOM")
    rf_selection = attachment.get("rf_selection", {})
    if rf_selection.get("internal_ufl") or rf_selection.get("internal_cable") or "no live RF stub" not in rf_selection.get("unused_path", ""):
        errors.append("the dual receiver land regressed to a cable or live RF stub")
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
    if not outreach.get("sent_on") or outreach["sent_on"] > model["checked_on"]:
        errors.append("supplier outreach date is missing or later than the model check")
    if set(outreach) != {"sent_on", "akk", "sinopine", "jlcpcb"}:
        errors.append("supplier outreach does not cover AKK, Sinopine and JLCPCB")
    if "pending" not in outreach["akk"].get("status", ""):
        errors.append("AKK production-package request must remain fail-closed until the reply arrives")
    if "pending" not in outreach["sinopine"].get("status", ""):
        errors.append("Sinopine production-identity request must remain fail-closed until the reply arrives")
    if "response received" not in outreach["jlcpcb"].get("status", ""):
        errors.append("JLCPCB factory-route response is missing")
    route = receiver["jlcpcb_surface"].get("consigned_parts_route", {})
    if route.get("selected") or not route.get("optional_later_simplification") or not route.get("approval_required_before_shipment"):
        errors.append("the optional K331 Consigned Parts route is overstated or incomplete")
    current_blockers = model["current_h1_blockers"]
    downstream = model["downstream_verification"]
    if current_blockers:
        errors.append("the accepted post-PCBA receiver attachment still exposes an H1 blocker")
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
        "attachment_strategy": attachment["architecture"],
        "attachment_h1_accepted": attachment["h1_accepted"],
        "receiver_population_rule": attachment["population_rule"],
        "factory_placement_accepted": receiver["jlcpcb_surface"]["accepted_for_factory_placement"],
        "production_acceptance": model["result"]["production_acceptance"],
        "receiver_alternatives_reviewed": len(alternatives),
        "jlcpcb_catalogue_hits": sum(row["catalogue_hits"] for row in searches.values()),
        "jlcpcb_placeable_hits": sum(row["placeable_hits"] for row in searches.values()),
        "supplier_outreach_sent_on": outreach["sent_on"],
        "official_integration_evidence": sorted(required_official_evidence),
        "candidate_oem_family": candidate_oem.get("mpn"),
        "candidate_oem_geometry": candidate_geometry,
        "candidate_oem_equivalence_accepted": candidate_oem.get("formal_equivalence_to_akk_k331"),
        "supplier_responses_pending": [key for key in ("akk", "sinopine", "jlcpcb") if "pending" in outreach[key]["status"]],
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
        (625, 118, 150, "K331 / AWM666V", "one post-PCBA VRX"),
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
        '<text x="32" y="347" font-family="sans-serif" font-size="11" fill="#166534">H1 accepts one-of-two post-PCBA lands: K331 is primary; exact-drawing AWM666V is the seven-channel fallback; H5/H7 qualifies the received module and solder process.</text>',
        '</svg>\n',
    ])
    return "\n".join(out)


def render_doc(model: dict, result: dict, ru: bool) -> str:
    r, a = model["receiver"], model["antenna"]
    e = r["official_integration_evidence"]
    attachment = r["attachment_strategy"]
    if ru:
        title = f'# {model["marker"]} · тракт аналогового FPV'
        intro = 'H1 принимает сменную post-PCBA-посадку одного аналогового FPV-приёмника: основной K331 или документированный fallback AWM666V.'
        result_text = (
            f'- `AKK {r["mpn"]}` покрывает {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} МГц, до {r["maximum_current_ma"]} мА и выдаёт CVBS 1 Vpp/75 Ω.\n'
            f'- Официальные материалы AKK подтверждают [схему включения 331RX]({e["application_circuit"]}), [функции всех 14 контактов]({e["pinout"]}) и [таблицу 24 каналов]({e["channel_table"]}). Оси толерантной ручной посадки опираются на официальный `SP331R-MANUAL-V1.0`: 28,7×23,1 мм, шаг 2,54 мм, отступ 1,4 мм. Это не выдаётся за production-footprint AKK.\n'
            f'- В той же зоне помещается `AWM666V RX` с точным корпусом 26,16×16,38×3,70 мм и рекомендованной посадкой производителя. Это fallback на семь каналов 5725–5875 МГц, а не функционально равная замена K331.\n'
            '- CH1/CH2/CH3 используют задние RP GPIO32/33/34; GPIO30/31 обслуживают power/video-lock. Официальный pinout помечает K331 pin 6 `RSSI (NC)`, поэтому GPIO15 остаётся свободным.\n'
            f'- Резерв 5 В оставляет {result["power_margin_ma"]} мА запаса. Один выбранный RF-тракт идёт напрямую к MMCX; альтернативная ветвь разомкнута у запуска, поэтому нет U.FL, кабеля или активного stub.\n'
            '- Общий резерв увеличен до `30×24×8 мм`; после переноса C5 DBG10 минимальный встречный зазор составляет 1,05 мм при требовании 0,70 мм.\n'
            f'- Антенна `{a["mpn"]}` линейная, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} МГц, {a["gain_dbi"]} dBi, {a["cable_length_mm"]} мм; точная маркировка комплекта — `{a["printed_identity"]}`.'
            f' Независимый линейный резерв `{a["supply_independent_alternate"]["mpn"]}` покрывает 4,9–6,0 ГГц и сохраняет MMCX, но сейчас доступен только под заказ с lead time 16 недель.'
        )
        factory = (
            'JLCPCB подтвердила отсутствие K331 в Parts Library и Global Sourcing и не нашла прямой замены; AWM666V также не имеет публичного фабричного маршрута. Поэтому обычный PCBA BOM не содержит приёмника: после reflow устанавливается ровно один модуль. Consigned Parts остаётся необязательным будущим упрощением. H5/H7 проверяет фактический корпус, ручную пайку, Z, удержание и процесс; ответ AKK/Sinopine позволит заменить только толерантную посадку обычным footprint без изменения интерфейсов.'
        )
        blockers = '- Нет: выбранная post-PCBA-архитектура снимает production-пакет K331 с критического пути H1.'
        downstream = '\n'.join(
            f'- **{row["stage"]}:** {row["requirement_ru"]}'
            for row in model['downstream_verification']
        )
        headings = ('## Результат', '## Фабричная граница', '## Блокеры FPV для H1', '## Последующая проверка — не блокирует H1')
        alternatives_heading = '## Рассмотренные приёмники'
        footer = f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.'
    else:
        title = f'# {model["marker"]} · analog-FPV receive path'
        intro = 'H1 accepts a replaceable one-of-two post-PCBA analog-FPV receiver land: primary K331 or documented AWM666V fallback.'
        result_text = (
            f'- `AKK {r["mpn"]}` covers {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} MHz, draws at most {r["maximum_current_ma"]} mA and emits 1-Vpp/75-ohm CVBS.\n'
            f'- Official AKK-hosted media confirms the [331RX application circuit]({e["application_circuit"]}), [all 14 pin functions]({e["pinout"]}) and the [24-channel table]({e["channel_table"]}). The tolerant hand-solder axes use the official `SP331R-MANUAL-V1.0`: 28.7 × 23.1 mm, 2.54-mm pitch and 1.4-mm edge offset. It is not represented as an AKK production footprint.\n'
            '- The same bay accepts exact-drawing `AWM666V RX`, 26.16 × 16.38 × 3.70 mm, on its manufacturer land. It is a seven-channel 5725–5875-MHz fallback, not a functionally equal K331 replacement.\n'
            '- CH1/CH2/CH3 use rear-RP GPIO32/33/34; GPIO30/31 serve power/video lock. The official pinout marks K331 pin 6 `RSSI (NC)`, so GPIO15 remains free.\n'
            f'- The 5-V reserve retains {result["power_margin_ma"]} mA. One selected RF branch runs directly to MMCX; the alternate is isolated at the launch, leaving no U.FL, cable or live stub.\n'
            '- The common reserve is enlarged to `30 × 24 × 8 mm`; after relocating C5 DBG10, minimum opposing clearance is 1.05 mm against 0.70 mm required.\n'
            f'- `{a["mpn"]}` is linear, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} MHz, {a["gain_dbi"]} dBi and {a["cable_length_mm"]} mm; its exact kit mark is `{a["printed_identity"]}`.'
            f' Independent linear fallback `{a["supply_independent_alternate"]["mpn"]}` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.'
        )
        factory = (
            'JLCPCB confirmed that K331 is unavailable in both Parts Library and Global Sourcing and found no direct replacement; AWM666V also has no public factory route. The normal PCBA BOM therefore omits the receiver and exactly one module is installed after reflow. Consigned Parts remains an optional later simplification. H5/H7 qualifies received body, hand soldering, Z, retention and process; an AKK/Sinopine response can replace only the tolerant land with a regular footprint without changing any interface.'
        )
        blockers = '- None: the selected post-PCBA architecture removes the K331 production package from the H1 critical path.'
        downstream = '\n'.join(
            f'- **{row["stage"]}:** {row["requirement"]}'
            for row in model['downstream_verification']
        )
        headings = ('## Result', '## Factory boundary', '## FPV blockers for H1', '## Later verification — does not block H1')
        alternatives_heading = '## Receivers reviewed'
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
