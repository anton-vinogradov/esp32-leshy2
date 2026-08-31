#!/usr/bin/env python3
"""Generate the bilingual public M1 contract from the H0-R2 machine map."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
EN = ROOT / "docs/interconnect.md"
RU = ROOT / "docs/interconnect.ru.md"


GROUPS = (
    ("1–16", "8 × POWER_GROUND + 3V3_MAIN pairs", "8 пар POWER_GROUND + 3V3_MAIN"),
    ("17–20", "2 × AON_SAFE_3V3 with safety returns", "2 × AON_SAFE_3V3 с safety-return"),
    ("21–28", "Hub↔RF RP dedicated SPI + alert and returns", "выделенный SPI Hub↔RF RP + alert и возвраты"),
    ("29–31", "S3 product USB 2.0 D−/D+ + return", "продуктовый USB 2.0 S3 D−/D+ + возврат"),
    ("32–34", "fail-closed Pack/Safety I²C + return", "fail-closed I²C Pack/Safety + возврат"),
    ("35–36", "1 NC reserve + bounded S3 fault-UI reset", "1 NC-резерв + bounded reset S3 fault-UI"),
    ("37–40", "RUN, fault and UI thermal safety crossings + return", "RUN, fault и UI thermal safety + возврат"),
    ("41–50", "9 actual-TX evidence signals + safety return", "9 сигналов actual-TX evidence + safety-return"),
    ("51–54", "rear encoder A/B/push + return", "задний энкодер A/B/push + возврат"),
    ("55–59", "AON service ownership/control and alert", "AON service ownership/control и alert"),
    ("60–64", "5 NC reserve contacts", "5 резервных NC-контактов"),
    ("65–76", "6 × POWER_GROUND + 3V3_MAIN pairs", "6 пар POWER_GROUND + 3V3_MAIN"),
    ("77–80", "4 NC reserve contacts", "4 резервных NC-контакта"),
)


def load() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def render(data: dict, ru: bool) -> str:
    m1 = data["interboard_rebaseline"]
    current = m1["main_current"]
    budget = m1["current_budget"]
    if ru:
        title = "# M1 · межплатное соединение"
        nav = "[Главная](../README.md) · [Железо](hardware.ru.md) · [English](interconnect.md)"
        intro = (
            "UI- и RF/power-платы соединяет одна точная прямая SMT-пара "
            "`Hirose FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` с рабочим зазором 11,00 мм. "
            "Все 80 контактов определены ниже; сквозных электрических выводов на внешних сторонах нет."
        )
        counts = "## Бюджет 80 контактов"
        current_text = (
            f"Основная шина использует **{budget['main_power']}** параллельных контактов и столько же основных возвратов. "
            f"При continuous `{current['continuous_a']:.2f} А` получается `{current['continuous_per_contact_a']:.4f} А/контакт`; "
            f"при step `{current['step_a']:.2f} А` — `{current['step_per_contact_a']:.4f} А/контакт` против рейтинга `{current['contact_rating_a']:.1f} А`."
        )
        mechanics = "## Механическая нагрузка"
        mechanics_text = (
            "M1 выполняет только электрическую функцию и совмещение. Четыре точных 11,00-мм compression-stop, "
            "не менее двух противосдвиговых упоров корпуса и независимые захваты обеих PCB не дают платам "
            "разойтись или сдвинуться даже при одном ослабленном винте. Нагрузки обычного обращения, установки "
            "аккумуляторов и изгиба корпуса несут винты, упоры и захваты, а не SMT-пайка M1."
        )
        group_heading = "## Принципиальная группировка"
        group_col = "Назначение"
        exact_heading = "Полная контактная карта"
        contact_col, net_col, class_col = "Контакт", "Сеть", "Класс"
        note = "Источник истины — `hardware/architecture/h0-r2-rebaseline.json`; таблица генерируется из него."
    else:
        title = "# M1 inter-board connection"
        nav = "[Home](../README.md) · [Hardware](hardware.md) · [Русский](interconnect.ru.md)"
        intro = (
            "The UI and RF/power PCBs use one exact straight-SMT "
            "`Hirose FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` pair at an 11.00-mm working gap. "
            "All 80 contacts are defined below; no electrical tail protrudes through either outer face."
        )
        counts = "## 80-contact budget"
        current_text = (
            f"The main rail uses **{budget['main_power']}** parallel contacts and the same number of primary returns. "
            f"Continuous `{current['continuous_a']:.2f} A` is `{current['continuous_per_contact_a']:.4f} A/contact`; "
            f"the `{current['step_a']:.2f} A` step is `{current['step_per_contact_a']:.4f} A/contact` against a `{current['contact_rating_a']:.1f} A` rating."
        )
        mechanics = "## Mechanical load path"
        mechanics_text = (
            "M1 is electrical/alignment only. Four exact 11.00-mm compression stops, at least two enclosure "
            "anti-shear datums and independent capture of both PCBs prevent separation or relative shear even "
            "with one screw loosened. Ordinary handling, battery installation and enclosure flex are carried by "
            "the fasteners, stops, datums and capture lips rather than the M1 SMT joints."
        )
        group_heading = "## Principle grouping"
        group_col = "Assignment"
        exact_heading = "Complete contact map"
        contact_col, net_col, class_col = "Contact", "Net", "Class"
        note = "The source of truth is `hardware/architecture/h0-r2-rebaseline.json`; this table is generated from it."

    group_rows = "\n".join(
        f"| `{contacts}` | {ru_text if ru else en_text} |" for contacts, en_text, ru_text in GROUPS
    )
    exact_rows = "\n".join(
        f"| `{row['contact']}` | `{row['net']}` | `{row['class']}` |" for row in m1["pin_map"]
    )
    summary = (
        f"`{budget['live_signals']}` live signals · `{budget['main_power']}` main-power · "
        f"`{budget['aon_power']}` AON · `{budget['returns']}` defined returns · "
        f"`{budget['no_connect_reserve']}` NC reserve"
    )
    return "\n".join(
        [
            title, "", nav, "", intro, "", counts, "", summary, "", current_text, "",
            mechanics, "", mechanics_text, "", group_heading, "", f"| Contacts | {group_col} |",
            "|---|---|", group_rows, "", f"<details><summary>{exact_heading}</summary>", "",
            f"| {contact_col} | {net_col} | {class_col} |", "|---:|---|---|", exact_rows, "",
            "</details>", "", f"> {note}", "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load()
    outputs = {EN: render(data, False), RU: render(data, True)}
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                print(f"stale generated artifact: {path.relative_to(ROOT)}")
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
