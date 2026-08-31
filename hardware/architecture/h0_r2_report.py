#!/usr/bin/env python3
"""Generate the public H0-R2 architecture report and compact visual evidence."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
REPORT_EN = ROOT / "docs/h0-r2-functional-architecture.md"
REPORT_RU = ROOT / "docs/h0-r2-functional-architecture.ru.md"
SVG = ROOT / "docs/images/h0-r2-functional-architecture.svg"
BOM = ROOT / "hardware/architecture/generated/H0-R2-airband-bom-delta.csv"


def load() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def render_svg_legacy(data: dict) -> str:
    air = data["airband_contract"]
    hub = data["hub_rp"]["gpio_budget"]
    blocks = [
        ("FM / SW / AIR RX", "existing standard-SMA port", "#eff6ff", "#2563eb"),
        ("118–137 MHz BPF", "serial LC · BPF-A127+ mask", "#ecfdf5", "#059669"),
        ("PGA-103+", "C3008207 · low-noise gain", "#ecfdf5", "#059669"),
        ("LT5560EDD#TRPBF", "C462645 · RF − 112 MHz", "#fff7ed", "#ea580c"),
        ("HMC544AETR", "C579555 · direct / converted", "#f5f3ff", "#7c3aed"),
        ("SI4732-A10-GSR", "C2155558 · 6–25 MHz FMI", "#eff6ff", "#2563eb"),
        ("SC1512-A4 · Hub RP", "I²C control · audio · recording", "#f8fafc", "#334155"),
        ("ESP32-S3-WROOM-1U-N16R8", "UI and direct display stay local", "#eff6ff", "#2563eb"),
    ]
    width = 760
    box_x, box_w, box_h, gap = 145, 470, 58, 25
    height = 130 + len(blocks) * (box_h + gap) + 115
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#475569"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="380" y="36" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="700" fill="#172033">Leshy2 · H0-R2 functional architecture</text>',
        '<text x="380" y="62" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#526076">Mandatory receive-only Airband reuses the broadcast path; no UI or display traffic crosses this chain.</text>',
    ]
    y = 92
    for index, (title, role, fill, stroke) in enumerate(blocks):
        out.append(
            f'<rect x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        out.append(
            f'<text x="380" y="{y + 24}" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="#172033">{html.escape(title)}</text>'
        )
        out.append(
            f'<text x="380" y="{y + 44}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#526076">{html.escape(role)}</text>'
        )
        if index < len(blocks) - 1:
            out.append(
                f'<line x1="380" y1="{y + box_h}" x2="380" y2="{y + box_h + gap - 4}" stroke="#475569" stroke-width="2" marker-end="url(#a)"/>'
            )
        y += box_h + gap

    lo_y = 92 + 3 * (box_h + gap)
    out.extend(
        [
            f'<rect x="18" y="{lo_y}" width="105" height="58" rx="9" fill="#fff7ed" stroke="#ea580c" stroke-width="2"/>',
            f'<text x="70" y="{lo_y + 23}" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700" fill="#172033">SI5351A</text>',
            f'<text x="70" y="{lo_y + 42}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#526076">112 MHz LO</text>',
            f'<line x1="123" y1="{lo_y + 29}" x2="143" y2="{lo_y + 29}" stroke="#ea580c" stroke-width="2" marker-end="url(#a)"/>',
            f'<text x="380" y="{height - 48}" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="700" fill="#166534">Hub GPIO: {hub["used"]} used · {hub["free"]} free</text>',
            f'<text x="380" y="{height - 25}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b42318">AIR_RX_EN is fail-low · default path remains direct FM/SW · Airband TX does not exist</text>',
            '</svg>',
        ]
    )
    return "\n".join(out) + "\n"


def render_svg(data: dict) -> str:
    """Render the whole two-PCB architecture and the Airband branch in context."""
    front = data["hub_rp"]["gpio_budget"]
    rear = data["rf_rp"]["gpio_budget"]

    def box(x: int, y: int, w: int, h: int, title: str, detail: str, colour: str) -> list[str]:
        return [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#ffffff" stroke="{colour}" stroke-width="2"/>',
            f'<text x="{x+w/2:.1f}" y="{y+23}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#172033">{html.escape(title)}</text>',
            f'<text x="{x+w/2:.1f}" y="{y+43}" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#526076">{html.escape(detail)}</text>',
        ]

    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="960" viewBox="0 0 1260 960">',
        '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L7 3 L0 6z" fill="#475569"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="630" y="38" text-anchor="middle" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · H0-R2 functional architecture</text>',
        '<text x="630" y="66" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#526076">H2-R2.1.5 is reviewed: 1,185 fitted symbols, 823 nets, zero ERC findings and six-domain reconciliation.</text>',
        '<rect x="40" y="105" width="540" height="610" rx="18" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>',
        '<rect x="680" y="105" width="540" height="610" rx="18" fill="#fff7ed" stroke="#ea580c" stroke-width="3"/>',
        '<text x="310" y="137" text-anchor="middle" font-family="sans-serif" font-size="19" font-weight="700" fill="#1d4ed8">FRONT · UI / RADIO PCB · five SMA</text>',
        '<text x="950" y="137" text-anchor="middle" font-family="sans-serif" font-size="19" font-weight="700" fill="#9a3412">REAR · RF / POWER PCB · five SMA</text>',
    ]
    out += box(70, 165, 225, 74, "ESP32-S3-WROOM-1U-N16R8", "direct i8080-8 · touch · all UI keys · 6 GPIO reserve", "#2563eb")
    out += box(325, 165, 225, 74, "ESP32-C5-WROOM-1U-N8R8", "2.4/5 GHz · 802.15.4 · IR", "#2563eb")
    out += box(70, 270, 480, 78, "SC1512-A4 · FRONT RP", f"UI/radio fan-out · microSD · {front['used']}/48 GPIO", "#7c3aed")
    out += box(70, 380, 480, 82, "3 × E01-ML01SP4 nRF24 ISLANDS", "20-dBm PA/LNA · concurrent full RX/TX/mix · C97340", "#0f766e")
    out += box(70, 500, 225, 74, "S3 ELECTRICAL RESERVE", "6 uncommitted GPIO after reset/service closure", "#7c3aed")
    out += box(325, 500, 225, 74, "microSD + local service", "direct front RP storage and recovery", "#64748b")
    out += box(710, 165, 480, 78, "SC1512-A4 · REAR RP", f"RF / audio / expansion owner · {rear['used']}/48 GPIO", "#7c3aed")
    out += box(710, 270, 225, 74, "CC1101 + VHF/UHF voice", "SUB-G RX/TX · two full-duplex voice paths", "#ea580c")
    out += box(965, 270, 225, 74, "NO ONBOARD VIDEO RX", "no receiver · decoder · connector · reserved bay", "#ea580c")
    out += box(710, 380, 225, 74, "Audio", "ES8311 · speaker · mic · CTIA headset", "#ea580c")
    out += box(965, 380, 225, 74, "M5 + U214 / U219", "one protected Cap profile · local buses", "#ea580c")
    out += box(710, 500, 225, 74, "Power + safety", "watchdog · evidence · thermal hard-off", "#b42318")
    out += box(965, 500, 225, 74, "FM/SW/AM/LW/AIR RX", "Si4732 with direct and converted Airband paths", "#0f766e")
    out.extend([
        '<rect x="585" y="205" width="90" height="420" rx="12" fill="#f8fafc" stroke="#334155" stroke-width="2"/>',
        '<text x="630" y="235" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="#172033">M1</text>',
        '<text x="630" y="258" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#526076">80-contact</text>',
        '<text x="630" y="292" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="#7c3aed">RP link</text>',
        '<text x="630" y="310" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#526076">1.5 MB/s</text>',
        '<text x="630" y="355" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="#7c3aed">M1.35 FAULT · 36 S3 reset</text>',
        '<text x="630" y="373" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#526076">1 NC + S3 reset</text>',
        '<text x="630" y="420" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="#b42318">RUN / FAULT</text>',
        '<text x="630" y="438" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#526076">3× nRF evidence</text>',
        '<text x="630" y="485" text-anchor="middle" font-family="sans-serif" font-size="9" font-weight="700" fill="#166534">14 × 3V3</text>',
        '<text x="630" y="503" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">24 returns</text>',
        '<text x="630" y="520" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">31 signals</text>',
        '<text x="630" y="538" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#166534">10 NC reserve</text>',
        '<line x1="550" y1="309" x2="585" y2="309" stroke="#7c3aed" stroke-width="2" marker-end="url(#a)"/>',
        '<line x1="675" y1="309" x2="710" y2="309" stroke="#7c3aed" stroke-width="2" marker-end="url(#a)"/>',
        '<path d="M965 307 H945 V475 H690 V355 H675" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#a)"/>',
        '<path d="M585 355 V480 H310 V537 H295" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#a)"/>',
        '<text x="630" y="675" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="#166534">No main RF trace crosses M1 · nRF payload is front-local · audio remains below 0.4 MB/s</text>',
        '<text x="40" y="765" font-family="sans-serif" font-size="18" font-weight="700" fill="#172033">Airband receive branch inside the rear broadcast island</text>',
    ])
    out += box(45, 800, 180, 62, "FM/SW input", "direct path", "#2563eb")
    out += box(265, 800, 180, 62, "AIR 118–137 MHz", "BPF → PGA-103+", "#0f766e")
    out += box(485, 800, 180, 62, "LT5560 mixer", "− 112 MHz from SI5351A", "#ea580c")
    out += box(705, 800, 180, 62, "HMC544A selector", "direct or converted 6–25 MHz", "#7c3aed")
    out += box(925, 800, 180, 62, "SI4732-A10-GSR", "audio → rear RP", "#2563eb")
    out.extend([
        '<path d="M225 831 H705" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#a)"/>',
        '<path d="M445 831 H485 M665 831 H705 M885 831 H925" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#a)"/>',
        '<text x="575" y="900" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b42318">AIR_RX_EN is fail-low · default is direct FM/SW · Airband TX does not exist</text>',
        '<text x="575" y="925" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#526076">The mandatory 118–137 MHz BPF rejects the 87–106 MHz image before conversion.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def bom_rows(data: dict) -> list[dict]:
    return data["airband_factory_bom_delta"]["lines"]


def render_report(data: dict, ru: bool) -> str:
    air = data["airband_contract"]
    bom = data["airband_factory_bom_delta"]
    power = data["power_rebaseline"]
    hub = data["hub_rp"]["gpio_budget"]
    rear = data["rf_rp"]["gpio_budget"]
    if ru:
        title = "H0-R2 · Функциональная архитектура"
        intro = (
            "H0-R2 проведён как новый функциональный baseline: UI и дисплей остаются "
            "на S3, высокоскоростные периферийные тракты разгружены через Hub RP, "
            "бортовой видеотракт удалён, а Airband AM 118–137 МГц теперь обязателен."
        )
        current = "Текущий точный маркер — **H5.0.3-R1**. Физическая проекция H1-R2.37 с двумя независимыми RP2354B, точными GPIO0..47, M1 и 226 корпусами принята и прошла ревью 2026-08-30. Native R2 H2 материализует 1 185 экземпляров и 823 nets в трёх проектах KiCad без замечаний ERC. H3-R2 полностью проведён ревью: 20 текущих evidence-artifacts и записанные source hashes сведены без mismatch или открытого аналитического finding; 51 физический остаток назначен H5/H6/H8. Глобальный H4-R2 проведён ревью: BSP покрывает 173/173 controller-строк, все 12 target-сборок квалифицированы, междоменных противоречий нет."
        sections = {
            "result": "Что зафиксировано",
            "air": "Airband RX",
            "pins": "Ноги и владелец",
            "pinmap": "Рабочая принципиальная распиновка",
            "power": "Питание",
            "bom": "Фабричный BOM-delta",
            "limits": "Честная граница возможностей",
            "next": "Что закрывает H1-R2",
        }
        role = "Роль"
        route = "Маршрут"
        price = "Цена, $"
        stock = "Остаток"
        frequency_paragraph = (
            "Фиксированный low-side LO 112 МГц переносит 118–137 МГц в 6–25 МГц. "
            "Зеркальный диапазон находится на 87–106 МГц, поэтому входной band-pass "
            "обязателен для работоспособности, а не является необязательным cleanup-фильтром."
        )
        gpio_headers = ("GPIO", "Функция", "Поведение после reset")
        included_label = "Включено:"
        excluded_label = "Исключено:"
        cost_note = "Incremental-стоимость активных компонентов"
        existing_note = "Существующая строка Si4732 переиспользуется и не входит в эту дельту."
        s3_headers = ("GPIO S3", "Сеть", "Периферия", "Направление")
        hub_headers = ("GPIO переднего RP", "Назначение")
        rear_headers = ("GPIO заднего RP", "Назначение")
        pinmap_note = (
            "Это полный рабочий принципиальный бюджет H0-R2, а не разрешение начинать KiCad. "
            "H1 может изменить конкретный контакт только вместе с этим источником, проверками и публичной таблицей."
        )
    else:
        title = "H0-R2 · Functional architecture"
        intro = (
            "H0-R2 is the new functional baseline: UI and display remain local to S3, "
            "high-throughput peripheral work is offloaded through the Hub RP, the onboard "
            "video path is removed, and 118–137 MHz Airband AM is now mandatory."
        )
        current = "The exact current marker is **H5.0.3-R1**. The H1-R2.37 physical projection with two independent RP2354B domains, exact GPIO0..47 maps, M1 and 226 bodies was accepted and reviewed on 2026-08-30. Native R2 H2 materializes 1,185 instances and 823 nets in three KiCad projects with zero ERC findings. H3-R2 is fully reviewed: 20 current evidence artifacts and their recorded source hashes reconcile without mismatch or open analytical finding, while 51 physical residuals remain owned by H5/H6/H8. Global H4-R2 is reviewed: the BSP covers 173/173 controller rows, all 12 target builds are qualified and no cross-domain contradiction remains."
        sections = {
            "result": "Accepted result",
            "air": "Airband RX",
            "pins": "GPIO and ownership",
            "pinmap": "Working principle pin design",
            "power": "Power",
            "bom": "Factory BOM delta",
            "limits": "Honest capability boundary",
            "next": "What H1-R2 must close",
        }
        role = "Role"
        route = "Route"
        price = "Price, $"
        stock = "Stock"
        frequency_paragraph = (
            "The fixed 112 MHz low-side LO maps 118–137 MHz to 6–25 MHz. "
            "The image band is 87–106 MHz, so the input band-pass network is a mandatory "
            "functional safety/performance element rather than an optional cleanup filter."
        )
        gpio_headers = ("GPIO", "Function", "Reset behavior")
        included_label = "Included:"
        excluded_label = "Excluded:"
        cost_note = "Incremental active-component cost"
        existing_note = "The existing Si4732 line is reused and is not counted in that delta."
        s3_headers = ("S3 GPIO", "Net", "Peripheral", "Direction")
        hub_headers = ("Front RP GPIO", "Assignment")
        rear_headers = ("Rear RP GPIO", "Assignment")
        pinmap_note = (
            "This is the complete H0-R2 working principle budget, not authorization to begin KiCad. "
            "H1 may change a contact only together with this source, its checks and this public table."
        )

    rows = "\n".join(
        f'| `{row["mpn"]}` | `{row["jlcpcb"]}` | {row["role"]} | {row["route"]} | {row["live_stock"]} | {row["unit_price"]:.4f} |'
        for row in bom_rows(data)
    )
    chain = " → ".join(f'`{item}`' for item in air["rf_chain"])
    included = "\n".join(f"- {item}" for item in air["performance_boundary"]["included"])
    excluded = "\n".join(f"- {item}" for item in air["performance_boundary"]["excluded"])
    gates = "\n".join(f"- {item}" for item in data["exit_review"]["open_h1_gates"])
    s3_rows = "\n".join(
        f'| `{row["gpio"]}` | `{row["net"]}` | `{row["peripheral"]}` | `{row["direction"]}` |'
        for row in data["s3"]["pin_map"]
    )
    hub_rows = "\n".join(
        f'| `{", ".join(str(gpio) for gpio in row["gpios"])}` | {row["role"]} |'
        for row in data["hub_rp"]["pin_groups"]
    )
    def current_rear_role(role: str) -> str:
        if role.startswith("U214 busy/IRQ/reset"):
            return (
                "exact-one U214/U219 Cap profile: shared SPI/I2C plus "
                "profile-specific BUSY/NFC_CS, IRQ, reset/power and GNSS/RF-switch lines"
            )
        return role

    rear_rows = "\n".join(
        f'| `{", ".join(str(gpio) for gpio in row["gpios"])}` | {current_rear_role(row["role"])} |'
        for row in data["rf_rp"]["pin_groups"]
    )
    result_lines = (
        "- Один пользовательский порт `FM / SW / AIR RX`; новый внешний разъём не добавлен.\n"
        "- Airband — подрежим `BROADCAST_RX`, поэтому его RF-домен не включается одновременно с TX-группой.\n"
        "- Кнопки остаются на локальном для S3 TCA9539PWR, энкодер и USB подключены к S3 напрямую; direct i8080-8 даёт 20 МБ/с на точных 20 МГц от штатного делителя ESP-IDF.\n"
        "- Передний RP владеет тремя nRF24 и microSD; задний RP владеет Si4732/Airband, CC1101, voice, аудио, M5 и одним из U214/U219.\n"
        "- M1 переносит control/status, safety, USB и питание; контакт 35 — latched FAULT_KILL лицевого индикатора, контакт 36 — отдельный reset S3 fault-UI."
        if ru
        else
        "- One user port is labelled `FM / SW / AIR RX`; no new external connector is added.\n"
        "- Airband is a `BROADCAST_RX` submode, so its RF domain cannot run together with a TX group.\n"
        "- Buttons stay on the S3-local TCA9539PWR path while encoder and USB remain direct; direct i8080-8 provides 20 MB/s at an exact 20 MHz from the standard ESP-IDF divider.\n"
        "- The front RP owns three nRF24 paths and microSD; the rear RP owns Si4732/Airband, CC1101, voice, audio, M5 and exactly one U214/U219 profile.\n"
        "- M1 carries control/status, safety, USB and power; contact 35 carries latched FAULT_KILL to the front indicator and contact 36 is the independent S3 fault-UI reset."
    )
    filter_note = (
        "`BPF-A127+` не найден в каталоге JLCPCB (0 exact matches). Он используется как опубликованный эталон маски; production-вариант — серийная LC-лестница из фабричных passives, а не кастомная деталь. Все её MPN закрываются после H1 RF-синтеза и layout extraction."
        if ru
        else
        "`BPF-A127+` has no exact JLCPCB catalogue match. It is the published response-mask reference; production uses a serial LC ladder made from factory passives, not a custom part. Its exact MPNs close after H1 RF synthesis and layout extraction."
    )
    power_note = (
        f"Старый R1-лимит 2,5 А больше не действителен. Airband резервирует {power['airband_increment']['reserved_current_ma']} мА / {power['airband_increment']['reserved_power_w']:.1f} Вт; новый H1 gate — не менее {power['h1_required_envelope']['continuous_3v3_main_a_min']:.1f} А непрерывно и {power['h1_required_envelope']['step_a_min']:.1f} А step с повторной проверкой buck/eFuse/индуктора/меди/тепла."
        if ru
        else
        f"The old R1 2.5 A limit is no longer current. Airband reserves {power['airband_increment']['reserved_current_ma']} mA / {power['airband_increment']['reserved_power_w']:.1f} W; the new H1 gate is at least {power['h1_required_envelope']['continuous_3v3_main_a_min']:.1f} A continuous and {power['h1_required_envelope']['step_a_min']:.1f} A step, with buck/eFuse/inductor/copper/thermal requalification."
    )
    return f"""# {title}

{intro}

> {current}

![H0-R2 functional architecture](images/h0-r2-functional-architecture.svg)

## {sections['result']}

{result_lines}

## {sections['air']}

{chain}

{frequency_paragraph}

## {sections['pins']}

| {gpio_headers[0]} | {gpio_headers[1]} | {gpio_headers[2]} |
|---|---|---|
| Rear RP GP35 | `AIR_RX_EN` | pulled low; LNA/mixer/LO domain off |
| Rear RP GP36 | `AIR_RX_MODE` | direct FM/SW path selected |

Front RP budget: **{hub['used']} used / {hub['free']} free**. Rear RP budget: **{rear['used']} used / {rear['free']} free**. SI5351 control stays on the rear-local I²C bus at `0x60`; no Airband control traffic uses the S3 UI bus.

## {sections['pinmap']}

{pinmap_note}

| {s3_headers[0]} | {s3_headers[1]} | {s3_headers[2]} | {s3_headers[3]} |
|---:|---|---|---|
{s3_rows}

| {hub_headers[0]} | {hub_headers[1]} |
|---|---|
{hub_rows}

| {rear_headers[0]} | {rear_headers[1]} |
|---|---|
{rear_rows}

## {sections['power']}

{power_note}

## {sections['bom']}

| MPN | JLCPCB | {role} | {route} | {stock} | {price} |
|---|---|---|---|---:|---:|
{rows}

{cost_note}: **`${bom['active_incremental_unit_cost']:.4f}`** before passives, PCB and assembly. {existing_note}

{filter_note}

## {sections['limits']}

{included_label}

{included}

{excluded_label}

{excluded}

## {sections['next']}

{gates}
"""


def write_all() -> None:
    data = load()
    SVG.write_text(render_svg(data), encoding="utf-8")
    REPORT_EN.write_text(render_report(data, False), encoding="utf-8")
    REPORT_RU.write_text(render_report(data, True), encoding="utf-8")
    BOM.parent.mkdir(parents=True, exist_ok=True)
    with BOM.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["mpn", "jlcpcb", "qty", "role", "live_stock", "unit_price", "route"],
        )
        writer.writeheader()
        writer.writerows(bom_rows(data))


if __name__ == "__main__":
    write_all()
