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
    expected_controls = {1: "GPIO36", 2: "GPIO37", 3: "GPIO38", 5: "GPIO34", 6: "GPIO33"}
    for pin, token in expected_controls.items():
        if token not in pins[pin]["owner"]:
            errors.append(f"K331 pin {pin} does not use reserved {token}")
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
    alternatives = {row["mpn"]: row for row in model["receiver_alternatives_reviewed"]}
    if set(alternatives) != {"AKK K331", "AWM682 RX", "TUE-RFVRX-58-D", "generic RX5808"}:
        errors.append("receiver alternative review is incomplete")
    if alternatives.get("AWM682 RX", {}).get("controlled_envelope_mm", [0, 0])[1] <= model["receiver"]["mechanical"]["working_envelope_mm"][1]:
        errors.append("AWM682 rejection no longer proves a larger controlled body")
    if alternatives.get("TUE-RFVRX-58-D", {}).get("maximum_current_ma", 0) <= model["power_fit"]["reserved_active_5v_ma"]:
        errors.append("Top-Unum rejection no longer proves a power overrun")
    if outreach.get("sent_on") != model["checked_on"]:
        errors.append("supplier outreach date is missing or stale")
    if set(outreach) != {"sent_on", "akk", "jlcpcb"}:
        errors.append("supplier outreach does not cover both AKK and JLCPCB")
    if any("pending" not in outreach[key].get("status", "") for key in ("akk", "jlcpcb")):
        errors.append("supplier outreach status must remain fail-closed until replies arrive")
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
        "factory_placement_accepted": receiver["jlcpcb_surface"]["accepted_for_factory_placement"],
        "production_acceptance": model["result"]["production_acceptance"],
        "receiver_alternatives_reviewed": len(alternatives),
        "supplier_outreach_sent_on": outreach["sent_on"],
        "supplier_responses_pending": [key for key in ("akk", "jlcpcb") if "pending" in outreach[key]["status"]],
        "open_gates": model["open_gates"],
        "errors": errors,
    }


def render_svg(model: dict) -> str:
    esc = html.escape
    nodes = [
        (35, 118, 170, "TBS5G8MMCXA", "linear 5.5–6.0 GHz"),
        (245, 118, 150, "DL-MMCX-KWE-90", "external MMCX"),
        (435, 118, 150, "50 Ω PCB", "no U.FL / cable"),
        (625, 118, 150, "AKK K331", "24-channel VRX"),
        (815, 118, 170, "TVP5150AM1PBS", "CVBS → BT.656"),
        (1025, 118, 170, "ESP32-S3", "direct LCD_CAM"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1230" height="365" viewBox="0 0 1230 365">',
        '<rect width="1230" height="365" fill="#ffffff"/>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"/></marker><marker id="arrowBlue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/></marker></defs>',
        f'<text x="32" y="42" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} analog-FPV receive path</text>',
        '<text x="32" y="70" font-family="sans-serif" font-size="13" fill="#526076">Receive-only · one direct RF trace · channel control is offloaded to the Hub RP.</text>',
    ]
    for x, y, w, title, subtitle in nodes:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="9" fill="#ecfccb" stroke="#4d7c0f" stroke-width="2"/>')
        out.append(f'<text x="{x+w/2}" y="{y+29}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#365314">{esc(title)}</text>')
        out.append(f'<text x="{x+w/2}" y="{y+51}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#4d7c0f">{esc(subtitle)}</text>')
    for x in (205, 395, 585, 775, 985):
        out.append(f'<path d="M{x} 154 H{x+40}" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>')
    out.extend([
        '<rect x="498" y="240" width="270" height="82" rx="9" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>',
        '<text x="633" y="266" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="700" fill="#1d4ed8">RP2354B Hub · exact reserved controls</text>',
        '<text x="633" y="290" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#1d4ed8">GP33 RSSI · GP34 power · GP35 lock</text>',
        '<text x="633" y="309" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#1d4ed8">GP36/37/38 → K331 CH1/CH2/CH3</text>',
        '<path d="M633 240 V194" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrowBlue)"/>',
        '<text x="32" y="347" font-family="sans-serif" font-size="11" fill="#9a3412">K331 functional/pin fit passes; its manufacturer drawing and JLCPCB placement route remain explicit H1 gates.</text>',
        '</svg>\n',
    ])
    return "\n".join(out)


def render_doc(model: dict, result: dict, ru: bool) -> str:
    r, a = model["receiver"], model["antenna"]
    if ru:
        title = f'# {model["marker"]} · тракт аналогового FPV'
        intro = 'Принят серийный функциональный кандидат приёмника и точная антенна; физическая приёмка K331 ещё не заявлена.'
        result_text = (
            f'- `AKK {r["mpn"]}` покрывает {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} МГц, до {r["maximum_current_ma"]} мА и выдаёт CVBS 1 Vpp/75 Ω.\n'
            '- CH1/CH2/CH3 используют уже зарезервированные Hub GPIO36/37/38; новых GPIO или расширителя нет.\n'
            f'- Резерв 5 В оставляет {result["power_margin_ma"]} мА запаса. RF идёт напрямую по 50-омной PCB-дорожке к MMCX без U.FL.\n'
            f'- Антенна `{a["mpn"]}` линейная, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} МГц, {a["gain_dbi"]} dBi, {a["cable_length_mm"]} мм; точная маркировка комплекта — `{a["printed_identity"]}`.'
            f' Независимый линейный резерв `{a["supply_independent_alternate"]["mpn"]}` покрывает 4,9–6,0 ГГц и сохраняет MMCX, но сейчас доступен только под заказ с lead time 16 недель.'
        )
        factory = (
            'Производитель показывает K331 в наличии по $29.99; точные поиски JLCPCB по `AKK K331`, `RX5808` и `RTC6715` дали 0 результатов. '
            'Поэтому до ответа private/global sourcing это отдельный модуль, а не заявленная фабричная PCBA-позиция. '
            f'Антенна продаётся производителем за $6.95 и ставится в комплект после PCBA; JLCPCB для неё также не является сборочным маршрутом. '
            f'{model["supplier_outreach"]["sent_on"]} запросы с точным перечнем механических, assembly и sourcing-свидетельств отправлены AKK и JLCPCB; оба ответа ожидаются.'
        )
        gates = '\n'.join(f'- {gate}' for gate in model['open_gates'])
        headings = ('## Результат', '## Фабричная граница', '## Открытые gates')
        alternatives_heading = '## Почему K331 остаётся ведущим кандидатом'
        footer = f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.'
    else:
        title = f'# {model["marker"]} · analog-FPV receive path'
        intro = 'The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.'
        result_text = (
            f'- `AKK {r["mpn"]}` covers {r["frequency_mhz"][0]}–{r["frequency_mhz"][1]} MHz, draws at most {r["maximum_current_ma"]} mA and emits 1-Vpp/75-ohm CVBS.\n'
            '- CH1/CH2/CH3 use already-reserved Hub GPIO36/37/38; no new GPIO or expander is needed.\n'
            f'- The 5-V reserve retains {result["power_margin_ma"]} mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.\n'
            f'- `{a["mpn"]}` is linear, {a["frequency_mhz"][0]}–{a["frequency_mhz"][1]} MHz, {a["gain_dbi"]} dBi and {a["cable_length_mm"]} mm; its exact kit mark is `{a["printed_identity"]}`.'
            f' Independent linear fallback `{a["supply_independent_alternate"]["mpn"]}` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.'
        )
        factory = (
            'The manufacturer lists K331 in stock at $29.99; exact JLCPCB searches for `AKK K331`, `RX5808` and `RTC6715` returned zero results. '
            'It therefore remains a separate module until a private/global-sourcing response exists, not a claimed factory PCBA line item. '
            'The $6.95 antenna is a post-PCBA kit accessory and likewise not an assembly line item. '
            f'On {model["supplier_outreach"]["sent_on"]}, exact mechanical, assembly and sourcing evidence requests were sent to AKK and JLCPCB; both replies are pending.'
        )
        gates = '\n'.join(f'- {gate}' for gate in model['open_gates'])
        headings = ('## Result', '## Factory boundary', '## Open gates')
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

{gates}

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
