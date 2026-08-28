#!/usr/bin/env python3
"""Generate the H1-R2 cost-ranked product and trial-batch review."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-cost-review.json"
BOM_PATH = REPO / "hardware/architecture/generated/G2F-3I-target-bom.csv"
TRIAL_PATH = REPO / "hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json"
ANTENNA_PATH = REPO / "hardware/architecture/antenna-kit.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-cost-audit.json"
CSV_PATH = REPO / "hardware/product-design/generated/H1-R2-cost-ranked.csv"
EN_PATH = REPO / "docs/h1-r2-cost.md"
RU_PATH = REPO / "docs/h1-r2-cost.ru.md"


ROLE_OVERRIDES = {
    "adi_ad8314acpz_rl7": "six real-TX RF detectors / шесть RF-детекторов фактической передачи",
    "adi_ltc5532_es6_trmpbf": "S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц",
    "ebyte_e01_ml01ipx": "three full nRF24 radios / три полнофункциональных nRF24",
    "gct_rfpc_sma31_fn_175_a": "eight standard outward SMA / восемь внешних SMA",
    "gct_rfpc_sma32_fn_175_a": "two native-radio RP-SMA / два RP-SMA native-радио",
    "hirose_fx8c_80p_sv1_92": "80-contact UI-side interboard plug / 80-контактная межплатная вилка UI",
    "hirose_fx8c_80s_sv5_92": "80-contact RF-side interboard receptacle / 80-контактная межплатная розетка RF",
    "hirose_ufl_r_smt_1_10": "five native/module microcoax mates / пять микрокоаксиальных точек",
    "keystone_1048p": "dual protected-18650 holder / держатель двух защищённых 18650",
    "nicerf_sa818s_u_v18": "UHF voice transceiver / UHF голосовой трансивер",
    "nicerf_sa818s_v_v18": "VHF voice transceiver / VHF голосовой трансивер",
    "omron_b3s_1100p": "sixteen ordinary user keys / шестнадцать обычных клавиш",
    "qdtech_hmx035ctft_001": "display/touch assembly via donor ceiling / экран и touch через donor-ceiling",
    "samtec_ftsh_105_01_l_dv_k_p_tr": "three internal recovery headers / три внутренних recovery-разъёма",
    "te_2118651_2": "five 30-mm RF jumpers / пять 30-мм RF-кабелей",
    "ti_tmux1136_dgsr": "four complete audio/control selectors / четыре полных audio/control selector",
    "murata_grm32er71e226ke15l": "thirteen 22-uF power capacitors / тринадцать силовых конденсаторов 22 мкФ",
    "ti_tpd4e05u06_dqar": "thirteen four-line ESD arrays / тринадцать четырёхканальных ESD-сборок",
    "yageo_cc0402krx7r9bb104": "147 stocked 100-nF bypass capacitors / 147 складских развязывающих конденсаторов 100 нФ",
    "nexperia_74lvc2g14gv_125": "two stocked dual Schmitt inverters / два складских двойных Schmitt-инвертора",
}

LANES_RU = {
    "factory-preorder-penalty": (
        "Заменить безопасно эквивалентные pre-order пассивы и обычную логику на складские JLCPCB",
        "После четырёх безопасных пакетов 33 оставшиеся pre-order-строки стоят $717,0074 в нормализованном снимке партии из пяти устройств против $336,1525 по серийной материальной базе. Два складских корпусных варианта Nexperia, байпасный конденсатор YAGEO и шесть номиналов UNI-ROYAL вместе убирают около $105,2857 из наблюдаемого маршрута и в сумме снижают публичную материальную базу на $1,3378 на устройство.",
        "Проверять каждую строку по её substitution-классу; принимать только точную либо не худшую параметрическую замену.",
    ),
    "main-rf-mechanics": (
        "Сохранить низкопрофильную торцевую пару GCT до появления действительно равноценной складской замены",
        "HenryTech даёт дешёвую прямую пару, DreamLNK — дешёвую угловую пару без гаек, но обе меняют выбранный профиль 3,9 мм. DreamLNK сэкономил бы около $19,01 на устройство, одновременно подняв ось разъёма примерно на 6,3 мм и добавив сквозные хвосты внутрь бутерброда.",
        "Оставить GCT RFPC-SMA31/32 с индивидуальным удержанием и без общей рамки. Возвращаться к замене только для складской standard/reverse edge-launch пары до 6 ГГц с не большим профилем и контролируемым чертежом под плату 1,6 мм.",
    ),
    "rf-evidence-detectors": (
        "Пересмотреть восемь RF-детекторов, не ослабляя доказательство реальной передачи",
        "Шесть AD8314 и два LTC5532 дают $24,92 на устройство; live-цена партии — $276,70, и полного количества сейчас нет на складе.",
        "Сравнить складские детекторы и калиброванные диодные ячейки по диапазонам; сохранить независимый контроль трёх одновременно работающих nRF24.",
    ),
    "ordinary-controls": (
        "Подобрать одну серийную складскую серию tact-кнопок для всех шестнадцати обычных клавиш",
        "B3S-1100P дают $10,25 на устройство и $74,58 за 80 штук для партии из пяти устройств.",
        "Сохранить посадку, достижимость из корпуса, усилие, высоту, ресурс и утопленное нажатие.",
    ),
    "native-rf-jumpers": (
        "Сократить пять трактов U.FL + 30-мм кабель за счёт размещения источника около антенного порта",
        "Пять U.FL и пять RF-кабелей дают $14,43 на устройство без учёта ручной укладки.",
        "Удалять кабель только там, где короткая контролируемая RF-дорожка сохраняет keep-out, ремонтопригодность и сосуществование радио.",
    ),
    "battery-holder": (
        "Сравнить 1048P с серийными контактами аккумуляторов, удерживаемыми ложементом корпуса",
        "1048P даёт $8,57 на устройство и сейчас доступен JLCPCB только через pre-order.",
        "Замена обязана поддерживать длину защищённых элементов, полярность, ресурс циклов и передачу нагрузки на корпус, а не на пайку.",
    ),
    "service-headers": (
        "Заменить три дорогих DBG10-разъёма на равноценно ключеванную складскую серию",
        "Три Samtec FTSH дают $5,10 на устройство и используются только как резерв восстановления раскрытого бутерброда.",
        "Сохранить независимое восстановление S3/C5/RP, ключ, шаг, доступ щупов и внутреннюю высоту.",
    ),
    "display-production-route": (
        "Получить поставку отдельной панели вместо разбора полного донора",
        "Доступный донор стоит $20,90; цена и серийная идентичность отдельной HMX035CTFT-001 остаются открытыми.",
        "Сохранить сменный адаптер; донор считать верхней границей EVT-цены, а не серийной себестоимостью.",
    ),
}


def money(value: float | None) -> str:
    return "—" if value is None else f"${value:,.2f}"


def load() -> tuple[dict, list[dict], dict, dict]:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    with BOM_PATH.open(encoding="utf-8", newline="") as handle:
        bom = list(csv.DictReader(handle))
    trial = json.loads(TRIAL_PATH.read_text(encoding="utf-8"))
    antennas = json.loads(ANTENNA_PATH.read_text(encoding="utf-8"))
    return model, bom, trial, antennas


def trial_line_cost(row: dict, device_quantity: int) -> float | None:
    """Normalize mixed evidence to the complete trial-batch line cost.

    BOM Tool captures already include its assembly quantity. The two exact SA818
    part-page additions are unit prices and therefore need explicit scaling.
    """
    cost = row.get("displayed_line_cost_usd")
    if cost is None:
        return None
    if row.get("match_provenance") == "current_exact_jlcpcb_part_page":
        return cost * row["quantity"] * device_quantity
    return cost


def build(model: dict, bom: list[dict], trial: dict, antennas: dict) -> dict:
    trial_by_id = {row["device_id"]: row for row in trial["routes"]}
    provisional = model["provisional_unit_routes"]
    live = model["live_jlcpcb_spot_checks"]
    rows = []
    for source in bom:
        quantity = int(source["quantity"])
        production_line = (
            float(source["line_material_usd"])
            if source["line_material_usd"]
            else None
        )
        burden_kind = "quantity-100"
        if production_line is None and source["device_id"] in provisional:
            production_line = quantity * float(
                provisional[source["device_id"]]["unit_price_usd"]
            )
            burden_kind = "provisional reachable route"
        trial_row = trial_by_id.get(source["device_id"], {})
        trial_cost = trial_line_cost(trial_row, model["trial_device_quantity"])
        if source["device_id"] in live:
            trial_cost = live[source["device_id"]]["trial_displayed_cost_usd"]
        rows.append(
            {
                "device_id": source["device_id"],
                "mpn": source["mpn"],
                "role": ROLE_OVERRIDES.get(
                    source["device_id"], source["placements"].replace(";", ", ")
                ),
                "scope": source["scope"],
                "quantity_per_device": quantity,
                "quantity_trial": quantity * model["trial_device_quantity"],
                "planning_trial_line_usd": (
                    production_line * model["trial_device_quantity"]
                    if production_line is not None else None
                ),
                "unit_price_quantity_100_usd": (
                    float(source["unit_price_usd"])
                    if source["unit_price_usd"]
                    else None
                ),
                "effective_unit_price_usd": (
                    production_line / quantity if production_line is not None else None
                ),
                "line_burden_per_device_usd": production_line,
                "line_burden_basis": burden_kind,
                "quantity_100_batch_line_usd": (
                    production_line * 100 if production_line is not None else None
                ),
                "trial_displayed_line_usd": trial_cost,
                "trial_route": trial_row.get("tool_status", "not matched"),
                "jlcpcb_part": trial_row.get("lcsc"),
                "cost_gate": source["cost_gate_status"] or None,
            }
        )
    rows.sort(
        key=lambda row: (
            row["line_burden_per_device_usd"] is not None,
            row["line_burden_per_device_usd"] or 0,
        ),
        reverse=True,
    )
    known_quantity_100 = sum(
        float(row["line_material_usd"])
        for row in bom
        if row["line_material_usd"] and row["scope"] == "base_product"
    )
    planning_base = sum(
        row["line_burden_per_device_usd"] or 0
        for row in rows
        if row["scope"] == "base_product"
    )
    remaining_base = [
        row for row in rows
        if row["scope"] == "base_product" and row["line_burden_per_device_usd"] is None
    ]
    post_pcba = sum(
        row["quantity_per_device"] * row["unit_price_usd"]
        for row in model["post_pcba_required"]
    )
    capture_total = sum(
        trial_line_cost(row, model["trial_device_quantity"]) or 0
        for row in trial["routes"]
    )
    adjusted_total = capture_total
    for device_id, current in live.items():
        old = trial_line_cost(
            trial_by_id.get(device_id, {}), model["trial_device_quantity"]
        ) or 0
        adjusted_total += current["trial_displayed_cost_usd"] - old
    preorder_rows = [
        row for row in trial["routes"]
        if trial_line_cost(row, model["trial_device_quantity"]) is not None
        and row.get("tool_status") == "pre_order"
    ]
    preorder_capture = sum(
        trial_line_cost(row, model["trial_device_quantity"]) or 0
        for row in preorder_rows
    )
    bom_by_id = {row["device_id"]: row for row in bom}
    preorder_scale = sum(
        model["trial_device_quantity"]
        * float(bom_by_id[row["device_id"]]["line_material_usd"] or 0)
        for row in preorder_rows
    )
    antenna_rows = []
    for item in antennas["items"]:
        prices = [
            value for key, value in item["availability"].items()
            if key.startswith("unit_price_usd") and value is not None
        ]
        price = float(prices[0]) if prices else None
        antenna_rows.append(
            {
                "code": item["kit_code"],
                "mpn": item["mpn"],
                "quantity": item["quantity"],
                "known_line_usd": price * item["quantity"] if price is not None else None,
                "profile": item["profile"],
            }
        )
    antenna_rows.sort(
        key=lambda row: (row["known_line_usd"] is not None, row["known_line_usd"] or 0),
        reverse=True,
    )
    antenna_known = sum(row["known_line_usd"] or 0 for row in antenna_rows)
    errors = []
    if len(bom) != 210:
        errors.append("target BOM is no longer 210 lines")
    if any(
        rows[index]["line_burden_per_device_usd"] is not None
        and rows[index + 1]["line_burden_per_device_usd"] is not None
        and rows[index]["line_burden_per_device_usd"]
        < rows[index + 1]["line_burden_per_device_usd"]
        for index in range(len(rows) - 1)
    ):
        errors.append("cost rows are not descending")
    display = model["display_orientation_review"]
    if display["paper_fit"]["same_face_collisions"] != 0:
        errors.append("upper display-adapter candidate collides on the UI inner face")
    if (
        display["paper_fit"]["minimum_opposing_clearance_mm"]
        < display["paper_fit"]["required_minimum_mm"]
    ):
        errors.append("upper display-adapter candidate violates opposing clearance")
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "checked_on": model["checked_on"],
        "status": "pass_review_with_open_cost_actions" if not errors else "fail",
        "summary": {
            "bom_lines": len(bom),
            "quantity_100_priced_lines": sum(bool(row["line_material_usd"]) for row in bom),
            "known_quantity_100_base_usd_per_device": round(known_quantity_100, 4),
            "planning_base_usd_per_device": round(planning_base, 4),
            "remaining_unpriced_base_lines": len(remaining_base),
            "planning_base_plus_post_pcba_usd_per_device": round(planning_base + post_pcba, 4),
            "planning_base_plus_post_pcba_usd_for_trial": round(
                (planning_base + post_pcba) * model["trial_device_quantity"], 4
            ),
            "trial_capture_matched_lines": sum(
                row.get("displayed_line_cost_usd") is not None for row in trial["routes"]
            ),
            "live_spot_checks": len(live),
            "trial_capture_displayed_usd": round(capture_total, 4),
            "trial_spot_adjusted_displayed_usd": round(adjusted_total, 4),
            "trial_unmatched_lines": sum(
                row.get("displayed_line_cost_usd") is None for row in trial["routes"]
            ),
            "preorder_rows": len(preorder_rows),
            "preorder_capture_usd": round(preorder_capture, 4),
            "preorder_quantity_100_basis_for_five_usd": round(preorder_scale, 4),
            "preorder_observed_small_lot_premium_usd": round(preorder_capture - preorder_scale, 4),
            "antenna_known_first_target_usd": round(antenna_known, 4),
            "antenna_unpriced_lines": sum(row["known_line_usd"] is None for row in antenna_rows),
        },
        "rows": rows,
        "post_pcba_required": model["post_pcba_required"],
        "antenna_rows": antenna_rows,
        "display_orientation_review": display,
        "accepted_cost_reduction_policy": model["accepted_cost_reduction_policy"],
        "current_stocked_candidate_checks": model["current_stocked_candidate_checks"],
        "optimization_lanes": model["optimization_lanes"],
        "errors": errors,
    }


def render_csv(result: dict) -> str:
    fields = [
        "device_id", "mpn", "role", "scope", "quantity_per_device",
        "unit_price_quantity_100_usd", "effective_unit_price_usd", "line_burden_per_device_usd",
        "line_burden_basis", "quantity_trial", "planning_trial_line_usd",
        "trial_displayed_line_usd",
        "trial_route", "jlcpcb_part", "quantity_100_batch_line_usd", "cost_gate",
    ]
    import io
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(result["rows"])
    return output.getvalue()


def render_doc(result: dict, ru: bool) -> str:
    summary = result["summary"]
    rows = result["rows"]
    display = result["display_orientation_review"]
    if ru:
        title = f'# {result["marker"]} · стоимость компонентов'
        intro = (
            'Это ранжированный снимок текущего железа, а не коммерческое предложение. '
            'Цена строки всегда учитывает количество на одном устройстве; колонка пробной '
            'партии показывает пять устройств и сохраняет реальные MOQ/pre-order эффекты JLCPCB.'
        )
        top_h = '## Сводка'
        basis = 'База'
        table_h = '## Самые дорогие строки готового устройства'
        trial_h = '## Где малая партия переплачивает'
        antenna_h = '## Внешний антенный комплект'
        candidates_h = '## Проверенные складские кандидаты'
        improve_h = '## Очередь удешевления'
        display_h = '## Ориентация экрана и шлейфа'
        role_h = 'Роль'
        qty_h = 'На устройство'
        unit_h = 'Цена 1 шт. по принятой базе'
        one_h = 'Строка на устройство'
        trial_qty_h = 'На 5 устройств'
        trial_plan_h = 'Плановая строка ×5'
        trial_cost_h = 'JLC live / MOQ'
    else:
        title = f'# {result["marker"]} · component cost ranking'
        intro = (
            'This is a ranked snapshot of the current hardware, not a commercial quote. '
            'Every line burden includes the quantity fitted to one device; the trial columns '
            'use five devices and preserve observed JLCPCB MOQ/pre-order effects.'
        )
        top_h = '## Summary'
        basis = 'Basis'
        table_h = '## Highest-cost finished-device lines'
        trial_h = '## Where the small batch overpays'
        antenna_h = '## External antenna kit'
        candidates_h = '## Verified stocked candidates'
        improve_h = '## Cost-reduction queue'
        display_h = '## Display and flex orientation'
        role_h = 'Role'
        qty_h = 'Per device'
        unit_h = 'Unit on accepted basis'
        one_h = 'Device line'
        trial_qty_h = 'For 5 devices'
        trial_plan_h = 'Planned line ×5'
        trial_cost_h = 'JLC live / MOQ'
    lines = [
        title, '',
        '[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)',
        '', intro, '', top_h, '',
    ]
    if ru:
        lines += [
            f'- Серийная материальная база: **{money(summary["known_quantity_100_base_usd_per_device"])}** на устройство; '
            f'цены известны для `{summary["quantity_100_priced_lines"]}/210` строк.',
            f'- Достижимый плановый минимум: **{money(summary["planning_base_usd_per_device"])}** на устройство; '
            f'ещё `{summary["remaining_unpriced_base_lines"]}` базовых строк не оценены.',
            f'- С обязательным модулем K331, устанавливаемым после PCBA: **{money(summary["planning_base_plus_post_pcba_usd_per_device"])}** '
            f'на устройство или **{money(summary["planning_base_plus_post_pcba_usd_for_trial"])}** на пять устройств '
            'до стоимости плат, сборки, корпуса, антенн, доставки, налогов, брака и теста.',
            f'- Частичный JLCPCB-снимок партии из пяти устройств: **{money(summary["trial_capture_displayed_usd"])}** по '
            f'`{summary["trial_capture_matched_lines"]}` найденным строкам; `{summary["live_spot_checks"]}` live-проверок дают '
            f'**{money(summary["trial_spot_adjusted_displayed_usd"])}**, ещё `{summary["trial_unmatched_lines"]}` строки не входят.',
            f'- Внешний антенный комплект вынесен отдельно: уже известно **{money(summary["antenna_known_first_target_usd"])}**, '
            f'ещё `{summary["antenna_unpriced_lines"]}` позиции не оценены.',
        ]
    else:
        lines += [
            f'- Volume material basis: **{money(summary["known_quantity_100_base_usd_per_device"])}** per device; '
            f'`{summary["quantity_100_priced_lines"]}/210` lines are priced.',
            f'- Reachable planning subtotal: **{money(summary["planning_base_usd_per_device"])}** per device, with '
            f'`{summary["remaining_unpriced_base_lines"]}` base-product lines still unpriced.',
            f'- With the required post-PCBA K331: **{money(summary["planning_base_plus_post_pcba_usd_per_device"])}** '
            f'per device or **{money(summary["planning_base_plus_post_pcba_usd_for_trial"])}** for five devices '
            'before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.',
            f'- Partial five-device JLCPCB capture: **{money(summary["trial_capture_displayed_usd"])}** for '
            f'`{summary["trial_capture_matched_lines"]}` matched lines; `{summary["live_spot_checks"]}` live checks move it to '
            f'**{money(summary["trial_spot_adjusted_displayed_usd"])}**, with `{summary["trial_unmatched_lines"]}` rows excluded.',
            f'- The external antenna kit is separate: **{money(summary["antenna_known_first_target_usd"])}** is known and '
            f'`{summary["antenna_unpriced_lines"]}` lines remain unpriced.',
        ]
    lines += ['', table_h, '',
        f'| MPN | {role_h} | {qty_h} | {unit_h} | {one_h} | {trial_qty_h} | {trial_plan_h} | {trial_cost_h} |',
        '|---|---|---:|---:|---:|---:|---:|---:|',
    ]
    for row in rows[:20]:
        lines.append(
            f'| `{row["mpn"]}` | {row["role"]} | {row["quantity_per_device"]} | '
            f'{money(row["effective_unit_price_usd"])} | {money(row["line_burden_per_device_usd"])} | '
            f'{row["quantity_trial"]} | {money(row["planning_trial_line_usd"])} | '
            f'{money(row["trial_displayed_line_usd"])} |'
        )
    full_csv = '../hardware/product-design/generated/H1-R2-cost-ranked.csv'
    full_text = 'Полный рейтинг 210 строк — CSV' if ru else 'Complete 210-line ranking — CSV'
    lines += ['', f'[{full_text}]({full_csv})', '', trial_h, '']
    if ru:
        lines += [
            f'- `{summary["preorder_rows"]}` pre-order-строк стоят в снимке **{money(summary["preorder_capture_usd"])}** против '
            f'**{money(summary["preorder_quantity_100_basis_for_five_usd"])}** на массовой материальной базе.',
            f'- Наблюдаемый штраф малой партии — **{money(summary["preorder_observed_small_lot_premium_usd"])}**. '
            'Это верхний приоритет: искать не «дешевле любой ценой», а эквивалентные stocked JLCPCB MPN внутри уже заданных substitution-классов.',
            '- `displayed_line_cost` JLCPCB использует рекомендуемое количество и pre-order reference pricing; это честный индикатор боли малой партии, но не финальный quote и не сумма готового заказа.',
        ]
    else:
        lines += [
            f'- The `{summary["preorder_rows"]}` pre-order rows cost **{money(summary["preorder_capture_usd"])}** in the capture versus '
            f'**{money(summary["preorder_quantity_100_basis_for_five_usd"])}** on their volume material basis.',
            f'- The observed small-lot premium is **{money(summary["preorder_observed_small_lot_premium_usd"])}**. '
            'This is the first priority: seek stocked JLCPCB MPNs that remain inside the existing substitution envelopes.',
            '- JLCPCB displayed-line cost uses recommended quantities and pre-order reference pricing; it is an honest small-batch pain indicator, not a final quote or order total.',
        ]
    lines += ['', antenna_h, '', '| Code | Profile | MPN | Qty | Known line |', '|---|---|---|---:|---:|']
    for row in result["antenna_rows"]:
        lines.append(f'| `{row["code"]}` | {row["profile"]} | `{row["mpn"]}` | {row["quantity"]} | {money(row["known_line_usd"])} |')
    lines += ['', candidates_h, '']
    lines += [
        '| Scope | Current | Candidate | JLCPCB | Stock | Status |',
        '|---|---|---|---|---:|---|',
    ]
    for candidate in result["current_stocked_candidate_checks"]:
        lines.append(
            f'| {candidate["scope"]} | `{candidate["current_mpn"]}` | '
            f'`{candidate["candidate_mpn"]}` | `{candidate["jlcpcb_part"]}` | '
            f'{candidate["stock"]} | `{candidate["status"]}` |'
        )
    lines.append('')
    for candidate in result["current_stocked_candidate_checks"]:
        explanation = candidate.get("why_ru", candidate["why"]) if ru else candidate["why"]
        lines.append(
            f'- **`{candidate["candidate_mpn"]}`:** {explanation} '
            f'[JLCPCB]({candidate["source"]})'
        )
    if ru:
        lines += [
            '**Принятое правило:** сначала устранять pre-order на малой партии, но менять MPN только на точный или не худший складской вариант. RF, power-safety, battery-protection и пользовательские ESD-границы не упрощаются ради цены. Если доказанного аналога нет, остаётся исходный MPN и явный pre-order.',
        ]
    else:
        lines += [
            '**Accepted rule:** remove avoidable small-lot pre-order first, but replace an MPN only with an exact or no-worse stocked part. RF, power-safety, battery-protection and user-exposed ESD boundaries are not simplified for cost. When no proven equivalent exists, the original MPN and explicit pre-order route remain.',
        ]
    lines += ['', improve_h, '']
    for lane in result["optimization_lanes"]:
        marker = '⚠️' if lane["production_function_change"] else '✅'
        title, evidence, action = (
            LANES_RU[lane["id"]]
            if ru
            else (lane["title"], lane["evidence"], lane["action"])
        )
        lines.append(f'{lane["priority"]}. {marker} **{title}** — {evidence} {action}')
    lines += ['', display_h, '']
    if ru:
        lines += [
            '- Официальный rear-view полного донора действительно показывает сложенный FPC и задний ZIF, но не раскрывает отдельный контур, длину и сторону контактов raw `HMX035CTFT-001`.',
            '- Правильное правило — физически ориентировать экран **шлейфом к антенному торцу**, а изображение и touch развернуть программно. Тогда шлейф не входит в зону LED, D-pad и функциональных клавиш.',
            f'- Принятая верхняя позиция adapter PCB `{display["current_upper_adapter_board_xy_mm"]}` прогнана по текущим точным корпусам: `0` same-face collisions, минимальный встречный зазор `{display["paper_fit"]["minimum_opposing_clearance_mm"]:.1f} мм` при требуемых `{display["paper_fit"]["required_minimum_mm"]:.1f} мм`, GPIO и BOM не меняются.',
            '- Ориентация зафиксирована в H1; H5 проверяет реальный шлейф, bend и retention сменного адаптера. Несовпадение не возвращает шлейф в зону органов управления молча.',
        ]
    else:
        lines += [
            '- The official complete-donor rear view does show a folded FPC and rear ZIF, but it does not disclose the standalone raw `HMX035CTFT-001` outline, length or contact side.',
            '- The correct rule is to physically orient the panel **with its flex toward the antenna edge**, then rotate display memory and touch coordinates in firmware. The tail then stays out of the LED, D-pad and function-key zone.',
            f'- The accepted upper adapter PCB position `{display["current_upper_adapter_board_xy_mm"]}` passes the current exact-body model: `0` same-face collisions and `{display["paper_fit"]["minimum_opposing_clearance_mm"]:.1f} mm` minimum opposing clearance versus `{display["paper_fit"]["required_minimum_mm"]:.1f} mm` required, with no GPIO or BOM change.',
            '- H1 now fixes this orientation; H5 qualifies the received flex, bend and retention on the replaceable adapter. A mismatch cannot silently return the tail to the control zone.',
        ]
    lines += ['', f'> Marker: **{result["marker"]}**. H1 remains open pending the complete mock-up decision.']
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(*load())
    if result["errors"]:
        for error in result["errors"]:
            print(f"error: {error}")
        return 1
    outputs = {
        AUDIT_PATH: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        CSV_PATH: render_csv(result),
        EN_PATH: render_doc(result, False),
        RU_PATH: render_doc(result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    if args.check:
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                print(f"error: stale generated artifact {path.relative_to(REPO)}")
                return 1
    print(f"ok: {len(result['rows'])} BOM rows; planning ${result['summary']['planning_base_plus_post_pcba_usd_per_device']:.2f}; trial ${result['summary']['trial_spot_adjusted_displayed_usd']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
