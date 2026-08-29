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
TOP20_CSV_PATH = REPO / "hardware/product-design/generated/H1-R2-cost-top20.csv"
EN_PATH = REPO / "docs/h1-r2-cost.md"
RU_PATH = REPO / "docs/h1-r2-cost.ru.md"


ROLE_OVERRIDES = {
    "adi_ad8314acpz_rl7": "six real-TX RF detectors / шесть RF-детекторов фактической передачи",
    "adi_ltc5532_es6_trmpbf": "S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц",
    "ebyte_e01_ml01sp4": "three 20-dBm PA/LNA full-function nRF24 radios / три полнофункциональных nRF24 с PA/LNA 20 dBm",
    "gct_rfpc_sma31_fn_175_a": "eight standard outward SMA / восемь внешних SMA",
    "gct_rfpc_sma32_fn_175_a": "two native-radio RP-SMA / два RP-SMA native-радио",
    "hirose_fx8c_80p_sv1_92": "80-contact UI-side interboard plug / 80-контактная межплатная вилка UI",
    "hirose_fx8c_80s_sv5_92": "80-contact RF-side interboard receptacle / 80-контактная межплатная розетка RF",
    "hirose_ufl_r_smt_1_10": "five native/module microcoax mates / пять микрокоаксиальных точек",
    "keystone_1048p": "dual protected-18650 holder / держатель двух защищённых 18650",
    "nicerf_sa818s_u_v18": "UHF voice transceiver / UHF голосовой трансивер",
    "nicerf_sa818s_v_v18": "VHF voice transceiver / VHF голосовой трансивер",
    "omron_b3s_1100p": "sixteen ordinary user keys / шестнадцать обычных клавиш",
    "qdtech_hmx035ctft_001": "unresolved production display gate / незакрытый production-display gate",
    "samtec_ftsh_105_01_l_dv_k_p_tr": "four internal recovery headers / четыре внутренних recovery-разъёма",
    "te_2118651_2": "five 30-mm RF jumpers / пять 30-мм RF-кабелей",
    "ti_tmux1136_dgsr": "four complete audio/control selectors / четыре полных audio/control selector",
    "murata_grm32er71e226ke15l": "thirteen 22-uF power capacitors / тринадцать силовых конденсаторов 22 мкФ",
    "ti_tpd4e05u06_dqar": "thirteen four-line ESD arrays / тринадцать четырёхканальных ESD-сборок",
    "yageo_cc0402krx7r9bb104": "147 stocked 100-nF bypass capacitors / 147 складских развязывающих конденсаторов 100 нФ",
    "nexperia_74lvc2g14gv_125": "two stocked dual Schmitt inverters / два складских двойных Schmitt-инвертора",
    "uniroyal_0402wgf1603tce": "stocked codec TX attenuator resistor / складской резистор аттенюатора TX кодека",
    "fh_rs_06k47r0ft": "stocked IR emitter current-limit resistor / складской токоограничивающий резистор IR",
    "yageo_cc0603krx7r0bb104": "stocked 100-nF 100-V USB VBIAS capacitor / складской конденсатор USB VBIAS 100 нФ 100 В",
}

LANES_RU = {
    "external-antenna-kit": (
        "Пересобрать внешний антенный комплект из складских эквивалентов",
        "Уже оценённые восемь из двенадцати профилей стоят $138,32 на одно устройство; три nRF24-антенны и AM/LW pod ещё не оценены. Это крупнейшая отдельная материальная группа проекта, хотя она не входит в базовую PCBA BOM.",
        "Не удалять диапазоны и не подменять TX-антенны широкополосным компромиссом: для каждого порта найти серийный складской MPN с тем же разъёмом, диапазоном, мощностью и не худшим согласованием, а receive-only профили оптимизировать отдельно.",
    ),
    "factory-preorder-penalty": (
        "Заменить безопасно эквивалентные pre-order пассивы и обычную логику на складские JLCPCB",
        "После шести безопасных пакетов 26 pre-order-строк стоят $648,0444 в нормализованном снимке партии из пяти устройств против $322,6465 по серийной материальной базе. Складские маршруты Nexperia, YAGEO, UNI-ROYAL, FH, Hirose, TI, Vishay и Murata вместе убирают около $137,7020 из наблюдаемого пробного маршрута и снижают публичную материальную базу на $3,0885 на устройство.",
        "Проверять каждую строку по её substitution-классу; принимать только точную либо не худшую параметрическую замену.",
    ),
    "main-rf-mechanics": (
        "Заменить дорогую GCT-пару на прочную складскую standard/reverse пару, если она помещается",
        "Десять GCT RFPC-SMA31/32 стоят $24,65 на устройство. Низкий профиль больше не является требованием; nutless-пара DreamLNK уменьшила бы строку примерно на $19,01 на общей quantity-100 базе, но её сквозные хвосты, MOQ и ручная фабричная пайка требуют нового внутреннего keep-out и подтверждения маршрута сборки.",
        "Искать не низкопрофильность, а правильное направление антенны, standard/RP-SMA, минимум 6 ГГц для native-портов и силовую пайку с двух сторон либо сквозное удержание. Принять замену только после полного 5+5 placement/clearance-аудита.",
    ),
    "rf-evidence-detectors": (
        "Пересмотреть восемь RF-детекторов, не ослабляя доказательство реальной передачи",
        "Шесть AD8314 и два LTC5532 дают $24,92 на устройство; live-цена партии — $276,70. Складской вариант того же устройства AD8314ARMZ-REEL C652687 сэкономит $88,99 на прежнем EVT5-снимке и $5,4864 на устройство на общей quantity-100 базе. Строго не худшая замена LTC5532 не доказана.",
        "До принятия C652687 зарегистрировать и проверить столкновения всех шести увеличенных MSOP-courtyard, соседних match/bypass-компонентов и fanout RF-земли. Два LTC5532 оставить; независимое evidence трёх одновременно работающих nRF24 сохранить.",
    ),
    "ordinary-controls": (
        "Сохранить заземлённую серию Omron для всех шестнадцати обычных клавиш",
        "B3S-1100P дают $10,25 на устройство. Проверены два складских аналога: B3S-1000P сохраняет усилие, высоту, ресурс и IP67, но теряет заземление крышки; TSG002A04526A намного дешевле, но также теряет этот вывод, повышает усилие до 2,6 Н и не доказывает ресурс точного кода в 500 тысяч нажатий. Поскольку все кнопки нажимаются пальцем напрямую без колпачка или толкателя, оба варианта хуже.",
        "Оставить B3S-1100P в текущей архитектуре. Возвращаться к замене только при наличии фабрично устанавливаемой детали с заземлённой пользовательской границей, усилием около 1,6 Н, высотой 4,3 мм, IP67 и ресурсом не менее 500 тысяч нажатий либо после будущей механической изоляции металлической крышки корпусом.",
    ),
    "native-rf-jumpers": (
        "Сохранить все пять трактов U.FL + 30-мм кабель после проверки размещения источников",
        "Пять трактов дают $14,43 на устройство без учёта ручной укладки. S3 и все три E01 выводят RF только через микрокоаксиальный разъём, а каждый тракт обязан пройти через локальный coupler и детектор реальной передачи до SMA. Текущий C5 также выводит U.FL; точный складской Espressif T2/ANT2 factory-route не доказан.",
        "Поэтому сейчас безопасно удалить можно 0/5 трактов. Будущий квалифицированный C5 T2 может убрать один тракт и сэкономить около $2,89 на устройство.",
    ),
    "battery-holder": (
        "Сохранить 1048P до доказательства полноценного держателя защищённых элементов",
        "1048P даёт $8,57 на устройство и остаётся pre-order, но проверенные складские MYOUNG — одиночные держатели или отдельные контакты: они не доказывают длину выбранных защищённых button-top XTAR, механическую блокировку переполюсовки двух элементов до касания контактов и единый четырёхконтактный механизм с опорой на корпус.",
        "Для EVT1 оставить 1048P как оправданный safety/mechanical-компонент. Возвращаться к замене только при наличии серийного фабрично устанавливаемого двойного держателя, который доказывает полный XTAR-envelope и передаёт усилия вставки/извлечения на корпус, а не на пайку.",
    ),
    "service-headers": (
        "Сохранить четыре складских Samtec DBG10 для единственного EVT1",
        "Исправленное количество R2 — четыре, а не три. Точный C2932107 сейчас есть на складе JLCPCB Extended SMT: 890 шт., доступны 887, MOQ 1 и $1,41 при количестве 1. Четыре разъёма стоят $5,64 на exact-one factory route. Площадки TC2050-IDC убрали бы детали с плат, но потребовали бы отдельный кабель за $39 и изменили бы удобство длительной отладки.",
        "Оставить четыре FTSH-105-01-L-DV-K-P-TR для независимого восстановления S3/C5/Hub-RP/RF-RP. Вернуться к Tag-Connect после EVT1, когда одноразовую цену кабеля можно амортизировать и проверить service-workflow.",
    ),
    "display-production-route": (
        "Не удешевлять уже выбранную серийную панель",
        "EastRising ER-TFT035IPS-6 + ER-TPC035-6 стоит $14,91, имеет полный чертёж, ILI9488/FT6236, i8080-8 и серийный заказ от одной штуки. Донорская схема удалена.",
        "Считать стоимость дисплея оправданной; открытым остаётся только тариф и письменное принятие фабрикой установки панели и FPC, а не поиск другого экрана.",
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
    procurement_quantity = model["procurement_target_device_quantity"]
    historical_quantity = model["historical_cost_capture_device_quantity"]
    trial_by_id = {row["device_id"]: row for row in trial["routes"]}
    provisional = model["provisional_unit_routes"]
    live = model["live_jlcpcb_spot_checks"]
    rows = []
    for source in bom:
        quantity = int(source["quantity"])
        override = model.get("r2_quantity_overrides", {}).get(source["device_id"])
        if override:
            quantity = int(override["quantity_per_device"])
        production_line = (
            float(source["unit_price_usd"]) * quantity
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
        trial_cost = trial_line_cost(trial_row, historical_quantity)
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
                "quantity_procurement_target": quantity * procurement_quantity,
                "planning_procurement_line_usd": (
                    production_line * procurement_quantity
                    if production_line is not None else None
                ),
                "quantity_historical_capture": quantity * historical_quantity,
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
                "quantity_ten_devices": quantity * 10,
                "planning_ten_devices_line_usd": (
                    production_line * 10 if production_line is not None else None
                ),
                "historical_capture_displayed_line_usd": trial_cost,
                "historical_capture_route": trial_row.get("tool_status", "not matched"),
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
        row["line_burden_per_device_usd"] or 0
        for row in rows
        if row["scope"] == "base_product"
        and row["line_burden_basis"] == "quantity-100"
    )
    planning_base = sum(
        row["line_burden_per_device_usd"] or 0
        for row in rows
        if row["scope"] == "base_product"
    )
    cumulative_base = 0.0
    for row in rows:
        burden = row["line_burden_per_device_usd"]
        if row["scope"] == "base_product" and burden is not None:
            cumulative_base += burden
            row["share_of_planning_base_pct"] = round(
                100.0 * burden / planning_base, 3
            )
            row["cumulative_planning_base_pct"] = round(
                100.0 * cumulative_base / planning_base, 3
            )
        else:
            row["share_of_planning_base_pct"] = None
            row["cumulative_planning_base_pct"] = None
    remaining_base = [
        row for row in rows
        if row["scope"] == "base_product" and row["line_burden_per_device_usd"] is None
    ]
    post_pcba = sum(
        row["quantity_per_device"] * row["unit_price_usd"]
        for row in model["post_pcba_required"]
    )
    capture_total = sum(
        trial_line_cost(row, historical_quantity) or 0
        for row in trial["routes"]
    )
    adjusted_total = capture_total
    for device_id, current in live.items():
        old = trial_line_cost(
            trial_by_id.get(device_id, {}), historical_quantity
        ) or 0
        adjusted_total += current["trial_displayed_cost_usd"] - old
    preorder_rows = [
        row for row in trial["routes"]
        if trial_line_cost(row, historical_quantity) is not None
        and row.get("tool_status") == "pre_order"
    ]
    preorder_capture = sum(
        trial_line_cost(row, historical_quantity) or 0
        for row in preorder_rows
    )
    bom_by_id = {row["device_id"]: row for row in bom}
    preorder_scale = sum(
        historical_quantity
        * float(bom_by_id[row["device_id"]]["line_material_usd"] or 0)
        for row in preorder_rows
    )
    antenna_by_mpn = {}
    for item in antennas["items"]:
        prices = [
            value for key, value in item["availability"].items()
            if key.startswith("unit_price_usd") and value is not None
        ]
        price = float(prices[0]) if prices else None
        grouped = antenna_by_mpn.setdefault(
            item["mpn"],
            {
                "codes": [],
                "mpn": item["mpn"],
                "quantity": 0,
                "known_line_usd": 0.0 if price is not None else None,
                "profiles": [],
            },
        )
        grouped["codes"].append(item["kit_code"])
        grouped["profiles"].append(item["profile"])
        grouped["quantity"] += item["quantity"]
        if price is None:
            grouped["known_line_usd"] = None
        elif grouped["known_line_usd"] is not None:
            grouped["known_line_usd"] += price * item["quantity"]
    antenna_rows = [
        {
            "code": ", ".join(row["codes"]),
            "mpn": row["mpn"],
            "quantity": row["quantity"],
            "known_line_usd": row["known_line_usd"],
            "profile": " / ".join(dict.fromkeys(row["profiles"])),
        }
        for row in antenna_by_mpn.values()
    ]
    antenna_rows.sort(
        key=lambda row: (row["known_line_usd"] is not None, row["known_line_usd"] or 0),
        reverse=True,
    )
    antenna_known = sum(row["known_line_usd"] or 0 for row in antenna_rows)
    combined_ranked_rows = [
        {
            "source": "base_bom",
            "mpn": row["mpn"],
            "role": row["role"],
            "quantity_per_prototype": row["quantity_per_device"],
            "effective_unit_price_usd": row["effective_unit_price_usd"],
            "group_cost_per_prototype_usd": row["line_burden_per_device_usd"],
        }
        for row in rows
        if row["scope"] == "base_product"
        and row["line_burden_per_device_usd"] is not None
    ] + [
        {
            "source": "external_antenna",
            "mpn": row["mpn"],
            "role": f'{row["profile"]}; {row["code"]}',
            "quantity_per_prototype": row["quantity"],
            "effective_unit_price_usd": row["known_line_usd"] / row["quantity"],
            "group_cost_per_prototype_usd": row["known_line_usd"],
        }
        for row in antenna_rows
        if row["known_line_usd"] is not None
    ]
    combined_ranked_rows.sort(
        key=lambda row: row["group_cost_per_prototype_usd"], reverse=True
    )
    known_combined_total = planning_base + post_pcba + antenna_known
    target = model["community_cost_target"]
    paper_qualified_no_loss_savings = round(
        (connector_cost := (
            next(row for row in rows if row["device_id"] == "gct_rfpc_sma31_fn_175_a")["line_burden_per_device_usd"]
            + next(row for row in rows if row["device_id"] == "gct_rfpc_sma32_fn_175_a")["line_burden_per_device_usd"]
        ))
        - (8 * 0.5515 + 2 * 0.6066)
        + (
            next(row for row in rows if row["device_id"] == "adi_ad8314acpz_rl7")["line_burden_per_device_usd"]
            - 6 * 1.9426
        ),
        4,
    )
    after_paper_qualified = round(
        planning_base + post_pcba - paper_qualified_no_loss_savings, 4
    )
    for rank, row in enumerate(combined_ranked_rows, 1):
        row["rank"] = rank
        row["share_of_known_combined_total_pct"] = round(
            100.0 * row["group_cost_per_prototype_usd"] / known_combined_total, 3
        )
    ranked_base = [
        row for row in rows
        if row["scope"] == "base_product"
        and row["line_burden_per_device_usd"] is not None
    ]

    def top_share(count: int) -> float:
        return round(
            100.0 * sum(
                row["line_burden_per_device_usd"] for row in ranked_base[:count]
            ) / planning_base,
            2,
        )
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
            "procurement_target_device_quantity": procurement_quantity,
            "historical_cost_capture_device_quantity": historical_quantity,
            "planning_base_plus_post_pcba_usd_for_procurement_target": round(
                (planning_base + post_pcba) * procurement_quantity, 4
            ),
            "planning_base_plus_post_pcba_usd_for_ten_devices": round(
                (planning_base + post_pcba) * 10, 4
            ),
            "planning_plus_known_antenna_usd_per_device": round(
                known_combined_total, 4
            ),
            "base_bom_lines": sum(row["scope"] == "base_product" for row in bom),
            "base_fitted_placements": sum(
                int(row["quantity_per_device"])
                for row in rows if row["scope"] == "base_product"
            ),
            "community_complete_device_target_usd": target["complete_device_usd"],
            "community_electronics_target_usd": target["electronics_target_usd"],
            "paper_qualified_no_loss_savings_usd": paper_qualified_no_loss_savings,
            "base_after_paper_qualified_savings_usd": after_paper_qualified,
            "pre_pcba_margin_to_complete_ceiling_usd": round(
                target["complete_device_usd"] - after_paper_qualified, 4
            ),
            "additional_savings_to_electronics_target_usd": [
                round(after_paper_qualified - target["electronics_target_usd"][1], 4),
                round(after_paper_qualified - target["electronics_target_usd"][0], 4),
            ],
            "combined_top_20_share_pct": round(
                100.0 * sum(
                    row["group_cost_per_prototype_usd"]
                    for row in combined_ranked_rows[:20]
                ) / known_combined_total,
                2,
            ),
            "top_10_share_pct": top_share(10),
            "top_20_share_pct": top_share(20),
            "top_40_share_pct": top_share(40),
            "historical_capture_matched_lines": sum(
                row.get("displayed_line_cost_usd") is not None for row in trial["routes"]
            ),
            "live_spot_checks": len(live),
            "historical_capture_displayed_usd": round(capture_total, 4),
            "historical_spot_adjusted_displayed_usd": round(adjusted_total, 4),
            "historical_capture_unmatched_lines": sum(
                row.get("displayed_line_cost_usd") is None for row in trial["routes"]
            ),
            "preorder_rows": len(preorder_rows),
            "preorder_capture_usd": round(preorder_capture, 4),
            "preorder_volume_basis_for_historical_capture_usd": round(preorder_scale, 4),
            "preorder_observed_small_lot_premium_usd": round(preorder_capture - preorder_scale, 4),
            "antenna_known_first_target_usd": round(antenna_known, 4),
            "antenna_unpriced_lines": sum(row["known_line_usd"] is None for row in antenna_rows),
            "antenna_unpriced_positions": sum(
                row["quantity"]
                for row in antenna_rows
                if row["known_line_usd"] is None
            ),
        },
        "rows": rows,
        "procurement_target": model["procurement_target"],
        "legacy_display_evidence": model["legacy_display_evidence"],
        "post_pcba_required": model["post_pcba_required"],
        "antenna_rows": antenna_rows,
        "combined_top_20_rows": combined_ranked_rows[:20],
        "display_orientation_review": display,
        "accepted_cost_reduction_policy": model["accepted_cost_reduction_policy"],
        "community_cost_target": target,
        "cost_feasibility": model["cost_feasibility"],
        "current_stocked_candidate_checks": model["current_stocked_candidate_checks"],
        "optimization_lanes": model["optimization_lanes"],
        "errors": errors,
    }


def render_csv(result: dict) -> str:
    fields = [
        "device_id", "mpn", "role", "scope", "quantity_per_device",
        "unit_price_quantity_100_usd", "effective_unit_price_usd", "line_burden_per_device_usd",
        "share_of_planning_base_pct", "cumulative_planning_base_pct",
        "line_burden_basis", "quantity_procurement_target", "planning_procurement_line_usd",
        "quantity_ten_devices", "planning_ten_devices_line_usd",
        "quantity_historical_capture", "historical_capture_displayed_line_usd",
        "historical_capture_route", "jlcpcb_part", "quantity_100_batch_line_usd", "cost_gate",
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


def render_top20_csv(result: dict) -> str:
    fields = [
        "rank", "source", "mpn", "role", "quantity_per_prototype",
        "effective_unit_price_usd", "group_cost_per_prototype_usd",
        "share_of_known_combined_total_pct",
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
    writer.writerows(result["combined_top_20_rows"])
    return output.getvalue()


def render_doc(result: dict, ru: bool) -> str:
    summary = result["summary"]
    rows = result["rows"]
    display = result["display_orientation_review"]
    feasibility = result["cost_feasibility"]
    if ru:
        title = f'# {result["marker"]} · стоимость компонентов'
        intro = (
            'Это ранжированный снимок текущего железа, а не коммерческое предложение. '
            'Цена строки учитывает установленное количество в целевом одном полностью собранном прототипе. '
            'Одинаковые MPN объединены в одну группу; исторический BOM Tool capture пяти плат сохранён ниже только как MOQ/pre-order evidence, а не план заказа.'
        )
        top_h = '## Сводка'
        basis = 'База'
        table_h = '## Единый топ-20: электроника и внешние антенны'
        trial_h = '## Где малая партия переплачивает'
        antenna_h = '## Внешний антенный комплект'
        candidates_h = '## Проверенные складские кандидаты'
        improve_h = '## Очередь удешевления'
        display_h = '## Ориентация экрана и шлейфа'
        role_h = 'MPN и роль'
        qty_h = 'Шт. ×1'
        unit_h = 'Цена 1 шт. по принятой базе'
        one_h = 'Группа ×1'
        source_h = 'Источник'
        share_h = 'Доля известной суммы'
    else:
        title = f'# {result["marker"]} · component cost ranking'
        intro = (
            'This is a ranked snapshot of the current hardware, not a commercial quote. '
            'Every line burden includes the fitted quantity in the target one fully assembled prototype. '
            'Identical MPNs are grouped into one row; the historical five-board BOM Tool capture remains below only as MOQ/pre-order evidence, not the procurement target.'
        )
        top_h = '## Summary'
        basis = 'Basis'
        table_h = '## Unified top 20: electronics and external antennas'
        trial_h = '## Where the small batch overpays'
        antenna_h = '## External antenna kit'
        candidates_h = '## Verified stocked candidates'
        improve_h = '## Cost-reduction queue'
        display_h = '## Display and flex orientation'
        role_h = 'MPN and role'
        qty_h = 'Qty ×1'
        unit_h = 'Unit on accepted basis'
        one_h = 'Group ×1'
        source_h = 'Source'
        share_h = 'Share of known total'
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
            f'- Текущий плановый компонентный минимум без обязательных post-PCBA активных модулей: **{money(summary["planning_base_plus_post_pcba_usd_per_device"])}** '
            f'на устройство и **{money(summary["planning_base_plus_post_pcba_usd_for_procurement_target"])}** на один целевой прототип '
            'до стоимости плат, сборки, корпуса, антенн, доставки, налогов, брака и теста.',
            f'- Та же принятая ценовая база для десяти устройств: **{money(summary["planning_base_plus_post_pcba_usd_for_ten_devices"])}**. '
            'Это линейное сравнение групп, а не обещание цены партии.',
            f'- Верхние 10 / 20 / 40 групп дают **{summary["top_10_share_pct"]:.2f}% / {summary["top_20_share_pct"]:.2f}% / {summary["top_40_share_pct"]:.2f}%** текущей известной базовой BOM.',
            f'- Исторический JLCPCB capture на пять плат: **{money(summary["historical_capture_displayed_usd"])}** по '
            f'`{summary["historical_capture_matched_lines"]}` строкам; `{summary["live_spot_checks"]}` live-проверок дают '
            f'**{money(summary["historical_spot_adjusted_displayed_usd"])}**, ещё `{summary["historical_capture_unmatched_lines"]}` строк не входят; это evidence, а не целевой quantity.',
            f'- Внешний антенный комплект вынесен отдельно: уже известно **{money(summary["antenna_known_first_target_usd"])}**, '
                f'ещё `{summary["antenna_unpriced_positions"]}` позиции в `{summary["antenna_unpriced_lines"]}` MPN-группах не оценены. Вместе с известной электронной BOM это уже '
            f'**{money(summary["planning_plus_known_antenna_usd_per_device"])}** до PCB/PCBA, корпуса и доставки.',
        ]
    else:
        lines += [
            f'- Volume material basis: **{money(summary["known_quantity_100_base_usd_per_device"])}** per device; '
            f'`{summary["quantity_100_priced_lines"]}/210` lines are priced.',
            f'- Reachable planning subtotal: **{money(summary["planning_base_usd_per_device"])}** per device, with '
            f'`{summary["remaining_unpriced_base_lines"]}` base-product lines still unpriced.',
            f'- Current planned component minimum with no mandatory post-PCBA active module: **{money(summary["planning_base_plus_post_pcba_usd_per_device"])}** '
            f'per device and **{money(summary["planning_base_plus_post_pcba_usd_for_procurement_target"])}** for the one target prototype '
            'before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.',
            f'- The same accepted price basis scales linearly to **{money(summary["planning_base_plus_post_pcba_usd_for_ten_devices"])}** for ten devices. '
            'This compares groups; it is not a batch quote.',
            f'- The top 10 / 20 / 40 groups contribute **{summary["top_10_share_pct"]:.2f}% / {summary["top_20_share_pct"]:.2f}% / {summary["top_40_share_pct"]:.2f}%** of the known base BOM.',
            f'- Historical five-board JLCPCB capture: **{money(summary["historical_capture_displayed_usd"])}** for '
            f'`{summary["historical_capture_matched_lines"]}` matched lines; `{summary["live_spot_checks"]}` live checks move it to '
            f'**{money(summary["historical_spot_adjusted_displayed_usd"])}**, with `{summary["historical_capture_unmatched_lines"]}` rows excluded. This is evidence, not the target quantity.',
            f'- The external antenna kit is separate: **{money(summary["antenna_known_first_target_usd"])}** is known and '
                f'`{summary["antenna_unpriced_positions"]}` positions in `{summary["antenna_unpriced_lines"]}` MPN groups remain unpriced. The known electronics plus known antennas already reach '
            f'**{money(summary["planning_plus_known_antenna_usd_per_device"])}** before PCB/PCBA, enclosure and freight.',
        ]
    if ru:
        lines += [
            '', '## Принятая ценовая граница all-in-one', '',
            f'- Текущий продукт остаётся полностью начинённым all-in-one. Цель повторяемого готового устройства: **{money(result["community_cost_target"]["preferred_complete_device_range_usd"][0])}–{money(result["community_cost_target"]["preferred_complete_device_range_usd"][1])}** без аккумуляторов и полного набора специализированных внешних антенн.',
            f'- Чтобы внутри этой цены остались PCB, PCBA и корпус, электроника должна попасть примерно в **{money(summary["community_electronics_target_usd"][0])}–{money(summary["community_electronics_target_usd"][1])}**.',
            f'- Сейчас базовая BOM содержит `{summary["base_bom_lines"]}` MPN-групп и `{summary["base_fitted_placements"]}` установленных компонентов. Даже две уже найденные paper-qualified замены без потери функции — SMA/RP-SMA и корпус AD8314 — экономят только **{money(summary["paper_qualified_no_loss_savings_usd"])}** и оставляют **{money(summary["base_after_paper_qualified_savings_usd"])}**.',
            f'- После них до целевой электронной BOM нужно убрать ещё **{money(summary["additional_savings_to_electronics_target_usd"][0])}–{money(summary["additional_savings_to_electronics_target_usd"][1])}**. Формальный запас до потолка готового устройства — только **{money(summary["pre_pcba_margin_to_complete_ceiling_usd"])}**, поэтому без дальнейшего пересинтеза в него не помещаются платы, сборка и корпус.',
            '',
            '**Принято:** отдельный `Core` сейчас не проектируется. Сначала строится и проверяется один полностью оснащённый `R2-EVT1`; стоимость снижается пересинтезом реализации без удаления встроенных функций и safety-результата. Историческая цель `$150` отложена как возможная community-комплектация после работающего EVT1, а не является текущей аппаратной веткой. Первый единственный заказ всё равно будет дороже из-за MOQ, setup, ручной установки, доставки и налогов.',
            '',
            '### Почему ESP32-DIV заметно дешевле',
            '',
            f'Официальная [архитектура {feasibility["comparison_reference"]["product"]}]({feasibility["comparison_reference"]["source"]}) существенно меньше: один S3, три nRF24, один CC1101, IR и простой слой разъёмов/пассивов. В его публичной shield BOM нет двух voice-модулей, Airband-конвертера, двух RP-доменов, трёх независимых service USB, автономной pack-safety, физического контроля фактического TX и десяти отдельно квалифицированных RF-портов. Розничная серия также амортизирует setup и закупочные минимумы, тогда как наш текущий расчёт должен выдержать единственный первый заказ.',
            '',
            'Это не означает, что Леший обязан стоить в восемь раз дороже. Это означает, что мы дорого реализовали не только функции, но и лабораторную наблюдаемость, независимое восстановление и отказоустойчивость каждого тракта.',
            '',
            '### Насколько реалистична цель без потери результата',
            '',
            '| Граница | Электроника | Готовая база | Честный вывод |',
            '|---|---:|---:|---|',
            f'| Текущая схема | {money(summary["planning_base_plus_post_pcba_usd_per_device"])} | больше {money(summary["planning_base_plus_post_pcba_usd_per_device"])} | уже выше принятого потолка без плат, сборки и корпуса |',
            f'| Только уже paper-qualified замены | {money(summary["base_after_paper_qualified_savings_usd"])} | больше {money(summary["base_after_paper_qualified_savings_usd"])} | всё ещё недостаточно |',
            f'| Те же встроенные пользовательские функции и тот же safety-результат после полного cost-resynthesis | {money(feasibility["same_all_in_one_result"]["electronics_working_range_usd"][0])}–{money(feasibility["same_all_in_one_result"]["electronics_working_range_usd"][1])} | {money(feasibility["same_all_in_one_result"]["repeatable_complete_base_working_range_usd"][0])}–{money(feasibility["same_all_in_one_result"]["repeatable_complete_base_working_range_usd"][1])} | с целью `$220–260` пересекается только верхняя часть |',
            f'| Модульная community-база; специализированные тракты ставятся Cap/Unit по задаче | {money(feasibility["modular_entry_result"]["electronics_target_usd"][0])}–{money(feasibility["modular_entry_result"]["electronics_target_usd"][1])} | {money(feasibility["modular_entry_result"]["repeatable_complete_target_usd"][0])}–{money(feasibility["modular_entry_result"]["repeatable_complete_target_usd"][1])} | отложена до работающего `R2-EVT1`; отдельного Core сейчас нет |',
            '',
            'Диапазоны `$214–235` и `$241–280` — не обещание цены: они предполагают успешный пересинтез оставшихся RF-evidence, audio/safety и внутренних RF-трактов без изменения результата. Кнопки, держатель и recovery-разъёмы уже проверены и сохранены, поэтому прежняя ожидаемая экономия на них удалена. Нижняя часть цели `$220–260` пока не доказана.',
            '',
            'Полный антенный комплект — аксессуар, а не скрытая часть цены устройства. Универсальная RX-антенна не заменяет согласованные TX-антенны; базовый комплект и дополнительные диапазонные антенны должны оцениваться отдельно.',
            '', 'Главный рейтинг ниже показывает **только один прототип**. В нём нет исторической цены пяти плат и нет умножения ×10.',
        ]
    else:
        lines += [
            '', '## Accepted all-in-one cost boundary', '',
            f'- The current product remains a fully populated all-in-one. Its repeatable complete-device target is **{money(result["community_cost_target"]["preferred_complete_device_range_usd"][0])}–{money(result["community_cost_target"]["preferred_complete_device_range_usd"][1])}**, excluding batteries and the full specialized external-antenna kit.',
            f'- To leave room for PCB, PCBA and enclosure, electronics must land near **{money(summary["community_electronics_target_usd"][0])}–{money(summary["community_electronics_target_usd"][1])}**.',
            f'- The current base BOM has `{summary["base_bom_lines"]}` MPN groups and `{summary["base_fitted_placements"]}` fitted components. Even the two paper-qualified no-function-loss replacements already identified — SMA/RP-SMA and the AD8314 package — save only **{money(summary["paper_qualified_no_loss_savings_usd"])}** and leave **{money(summary["base_after_paper_qualified_savings_usd"])}**.',
            f'- A further **{money(summary["additional_savings_to_electronics_target_usd"][0])}–{money(summary["additional_savings_to_electronics_target_usd"][1])}** must be removed to reach the electronics band. The formal margin to the complete-device ceiling is only **{money(summary["pre_pcba_margin_to_complete_ceiling_usd"])}**, so boards, assembly and enclosure do not fit without further resynthesis.',
            '',
            '**Accepted:** no separate `Core` is designed now. One fully populated `R2-EVT1` is built and verified first; implementation cost is reduced without removing built-in functions or the safety outcome. The historical `$150` goal is deferred as a possible post-EVT1 community fit option, not a current hardware branch. The sole first order will still cost more because MOQ, setup, manual placement, freight and tax cannot be amortized.',
            '',
            '### Why ESP32-DIV is much cheaper',
            '',
            f'The official [{feasibility["comparison_reference"]["product"]} architecture]({feasibility["comparison_reference"]["source"]}) is much smaller: one S3, three nRF24 modules, one CC1101, IR and a simple connector/passive layer. Its public shield BOM does not contain two voice modules, an Airband conversion chain, two RP domains, three independent service-USB paths, autonomous pack safety, physical actual-TX evidence or ten separately qualified RF ports. Retail volume also amortizes setup and purchasing minima, while this review must survive a sole first order.',
            '',
            'That does not mean Leshy2 must cost eight times as much. It means the current architecture pays not only for functions, but also for laboratory observability, independent recovery and fail-safe supervision around nearly every path.',
            '',
            '### Feasibility without losing the result',
            '',
            '| Boundary | Electronics | Complete base | Honest result |',
            '|---|---:|---:|---|',
            f'| Current circuit | {money(summary["planning_base_plus_post_pcba_usd_per_device"])} | above {money(summary["planning_base_plus_post_pcba_usd_per_device"])} | already above the accepted ceiling before boards, assembly and enclosure |',
            f'| Paper-qualified replacements only | {money(summary["base_after_paper_qualified_savings_usd"])} | above {money(summary["base_after_paper_qualified_savings_usd"])} | still insufficient |',
            f'| Same built-in user functions and same safety outcome after full cost resynthesis | {money(feasibility["same_all_in_one_result"]["electronics_working_range_usd"][0])}–{money(feasibility["same_all_in_one_result"]["electronics_working_range_usd"][1])} | {money(feasibility["same_all_in_one_result"]["repeatable_complete_base_working_range_usd"][0])}–{money(feasibility["same_all_in_one_result"]["repeatable_complete_base_working_range_usd"][1])} | only the upper portion overlaps the `$220–260` target |',
            f'| Modular community base; specialist paths are fitted as task-specific Caps/Units | {money(feasibility["modular_entry_result"]["electronics_target_usd"][0])}–{money(feasibility["modular_entry_result"]["electronics_target_usd"][1])} | {money(feasibility["modular_entry_result"]["repeatable_complete_target_usd"][0])}–{money(feasibility["modular_entry_result"]["repeatable_complete_target_usd"][1])} | deferred until a working `R2-EVT1`; there is no separate Core now |',
            '',
            'The `$214–235` and `$241–280` bands are not price promises: they assume successful remaining RF-evidence, audio/safety and internal-RF resynthesis without changing the result. Controls, holder and recovery headers have now been checked and retained, so their former assumed saving is removed. The lower part of the `$220–260` target is not yet demonstrated.',
            '',
            'The full antenna kit is an accessory, not a hidden device-price line. A broadband receive antenna cannot replace band-matched transmit antennas; the basic kit and additional band-specific antennas must be priced separately.',
            '', 'The primary ranking below shows **one prototype only**. It contains neither the historical five-board capture nor a ×10 multiplication.',
        ]
    lines += ['', table_h, '',
        f'| № | {source_h} | {role_h} | {qty_h} | {unit_h} | {one_h} | {share_h} |',
        '|---:|---|---|---:|---:|---:|---:|',
    ]
    for row in result["combined_top_20_rows"]:
        role = row["role"]
        if len(role) > 180:
            role = (
                f'{row["quantity_per_prototype"]} сгруппированных установок; полный список в CSV'
                if ru else f'{row["quantity_per_prototype"]} grouped placements; complete list in CSV'
            )
        source = (
            ('Антенна' if ru else 'Antenna')
            if row["source"] == "external_antenna"
            else ('Основная BOM' if ru else 'Base BOM')
        )
        lines.append(
            f'| {row["rank"]} | {source} | `{row["mpn"]}`<br><sub>{role}</sub> | '
            f'{row["quantity_per_prototype"]} | {money(row["effective_unit_price_usd"])} | '
            f'{money(row["group_cost_per_prototype_usd"])} | '
            f'{row["share_of_known_combined_total_pct"]:.2f}% |'
        )
    full_csv = '../hardware/product-design/generated/H1-R2-cost-ranked.csv'
    top20_csv = '../hardware/product-design/generated/H1-R2-cost-top20.csv'
    full_text = 'Полный рейтинг 210 строк — CSV' if ru else 'Complete 210-line ranking — CSV'
    top20_text = 'Единый топ-20 — CSV' if ru else 'Unified top 20 — CSV'
    by_id = {row["device_id"]: row for row in rows}
    connector_cost = (
        by_id["gct_rfpc_sma31_fn_175_a"]["line_burden_per_device_usd"]
        + by_id["gct_rfpc_sma32_fn_175_a"]["line_burden_per_device_usd"]
    )
    detector_cost = (
        by_id["adi_ad8314acpz_rl7"]["line_burden_per_device_usd"]
        + by_id["adi_ltc5532_es6_trmpbf"]["line_burden_per_device_usd"]
    )
    jumper_cost = (
        by_id["te_2118651_2"]["line_burden_per_device_usd"]
        + by_id["hirose_ufl_r_smt_1_10"]["line_burden_per_device_usd"]
    )
    lines += ['', f'[{top20_text}]({top20_csv}) · [{full_text}]({full_csv})', '']
    if ru:
        lines += [
            '## Где вероятнее всего есть неоправданные траты', '',
            '| Приоритет | Группа | Сейчас ×1 | Вывод | Реалистичная экономия |',
            '|---:|---|---:|---|---:|',
            f'| 1 | Внешние антенны | {money(summary["antenna_known_first_target_usd"])} + 4 неизвестных | Крупнейшая отдельная группа; функциональность нужна, но брендовые первые MPN не обязаны быть самыми выгодными | уточняется |',
            f'| 2 | 10 внешних SMA/RP-SMA | {money(connector_cost)} | Цена GCT больше не оправдывается требованием низкого профиля; нужна повторная компоновка прочной пары с фабричным manual-solder route | до ~$19.02 |',
            f'| 3 | 8 RF-detector’ов | {money(detector_cost)} | Evidence реальной передачи нужен; шесть AD8314 можно перевести на складской корпус того же IC после placement-аудита | ~$5.49 |',
            f'| 4 | 5 U.FL + 5 кабелей | {money(jumper_cost)} | Сейчас функционально оправдано; убрать можно только один тракт после доказанного C5 T2-маршрута | до ~$2.89 |',
            f'| 5 | 16 пользовательских кнопок | {money(by_id["omron_b3s_1100p"]["line_burden_per_device_usd"])} | Проверенные дешёвые кандидаты ухудшают ESD, feel или evidence; текущая группа оправдана | $0 |',
            f'| 6 | Держатель 2×18650 | {money(by_id["keystone_1048p"]["line_burden_per_device_usd"])} | Складские одиночные держатели не доказывают полный protected-cell и polarity contract; 1048P оправдан | $0 |',
            f'| 7 | 4 внутренних DBG10 | {money(by_id["samtec_ftsh_105_01_l_dv_k_p_tr"]["line_burden_per_device_usd"])} | Exact Samtec уже складской; Tag-Connect удорожает единственный EVT1 и ухудшает long-session workflow | $0 для EVT1 |',
            '',
            '**Не считаю неоправданными:** серийный дисплей за $14,91, два voice-модуля за $19,81, три полнофункциональных nRF24 за $8,89, оба RP/S3/C5, M1 и элементы автономной защиты. Их удаление или упрощение напрямую режет принятую функцию, пропускную способность, восстановление либо безопасность.',
            '',
        ]
    else:
        lines += [
            '## Most likely unjustified-cost candidates', '',
            '| Priority | Group | Current ×1 | Finding | Realistic saving |',
            '|---:|---|---:|---|---:|',
            f'| 1 | External antennas | {money(summary["antenna_known_first_target_usd"])} + 4 unknown | Largest separate group; the functions are required, but the first branded MPNs need not be the best-value equivalents | to be established |',
            f'| 2 | 10 outward SMA/RP-SMA | {money(connector_cost)} | GCT cost is no longer justified by a low-profile requirement; a robust pair needs a fresh placement and factory manual-solder check | up to ~$19.02 |',
            f'| 3 | 8 RF detectors | {money(detector_cost)} | Real-TX evidence remains required; six AD8314 can move to the stocked package of the same IC after placement review | ~$5.49 |',
            f'| 4 | 5 U.FL plus 5 cables | {money(jumper_cost)} | Functionally justified now; only a proven C5 T2 route can remove one path | up to ~$2.89 |',
            f'| 5 | 16 user buttons | {money(by_id["omron_b3s_1100p"]["line_burden_per_device_usd"])} | Checked cheaper candidates weaken ESD, feel or evidence; the current group is justified | $0 |',
            f'| 6 | Dual-18650 holder | {money(by_id["keystone_1048p"]["line_burden_per_device_usd"])} | Stocked single-cell bodies do not prove the complete protected-cell and polarity contract; 1048P is justified | $0 |',
            f'| 7 | 4 internal DBG10 headers | {money(by_id["samtec_ftsh_105_01_l_dv_k_p_tr"]["line_burden_per_device_usd"])} | Exact Samtec is stocked; Tag-Connect costs more for the sole EVT1 and weakens long-session ergonomics | $0 for EVT1 |',
            '',
            '**Not classified as unjustified:** the $14.91 serial display, $19.81 dual voice modules, $8.89 three full-function nRF24 modules, both RP/S3/C5, M1 and autonomous safety components. Removing or simplifying them directly cuts an accepted function, throughput, recovery or safety boundary.',
            '',
        ]
    unpriced_base = [
        row for row in rows
        if row["scope"] == "base_product"
        and row["line_burden_per_device_usd"] is None
    ]
    if ru:
        lines += [
            '## Что ещё нельзя считать бесплатным', '',
            'Эти позиции имеют **не нулевую**, а пока неизвестную цену. До exact-one quote итоговая стоимость остаётся нижней границей.', '',
            '| Источник | MPN и роль | Шт. ×1 |',
            '|---|---|---:|',
        ]
    else:
        lines += [
            '## Costs that must not be mistaken for zero', '',
            'These positions have an **unknown**, not zero, price. The total remains a lower bound until the exact-one quote.', '',
            '| Source | MPN and role | Qty ×1 |',
            '|---|---|---:|',
        ]
    for row in unpriced_base:
        lines.append(
            f'| {"Основная BOM" if ru else "Base BOM"} | `{row["mpn"]}`<br><sub>{row["role"]}</sub> | {row["quantity_per_device"]} |'
        )
    for row in result["antenna_rows"]:
        if row["known_line_usd"] is None:
            lines.append(
                f'| {"Антенный комплект" if ru else "Antenna kit"} | `{row["mpn"]}`<br><sub>{row["profile"]}; {row["code"]}</sub> | {row["quantity"]} |'
            )
    lines += ['', trial_h, '']
    if ru:
        lines += [
            f'- `{summary["preorder_rows"]}` pre-order-строк стоят в снимке **{money(summary["preorder_capture_usd"])}** против '
            f'**{money(summary["preorder_volume_basis_for_historical_capture_usd"])}** на массовой материальной базе.',
            f'- Наблюдаемый штраф малой партии — **{money(summary["preorder_observed_small_lot_premium_usd"])}**. '
            'Это верхний приоритет: искать не «дешевле любой ценой», а эквивалентные stocked JLCPCB MPN внутри уже заданных substitution-классов.',
            '- `displayed_line_cost` JLCPCB использует рекомендуемое количество и pre-order reference pricing; это честный индикатор боли малой партии, но не финальный quote и не сумма готового заказа.',
        ]
    else:
        lines += [
            f'- The `{summary["preorder_rows"]}` pre-order rows cost **{money(summary["preorder_capture_usd"])}** in the capture versus '
            f'**{money(summary["preorder_volume_basis_for_historical_capture_usd"])}** on their volume material basis.',
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
        marker = {
            "accepted": "✅",
            "active": "▶",
            "waiting": "⏳",
        }[lane["queue_status"]]
        title, evidence, action = (
            LANES_RU[lane["id"]]
            if ru
            else (lane["title"], lane["evidence"], lane["action"])
        )
        lines.append(f'{lane["priority"]}. {marker} **{title}** — {evidence} {action}')
    lines += ['', display_h, '']
    if ru:
        lines += [
            '- Точные чертежи EastRising контролируют полный корпус панели, 50-контактный FPC, шаг 0,50 мм, stiffener 0,30 мм и карту контактов; геометрия donor-board больше не используется.',
            '- Экран физически ориентирован **шлейфом к антенному торцу**, а изображение ILI9488 и координаты FT6236 разворачиваются программно. Шлейф не входит в зону LED, D-pad и функциональных клавиш.',
            f'- Принятая верхняя позиция adapter PCB `{display["current_upper_adapter_board_xy_mm"]}` прогнана по текущим точным корпусам: `0` same-face collisions, минимальный встречный зазор `{display["paper_fit"]["minimum_opposing_clearance_mm"]:.1f} мм` при требуемых `{display["paper_fit"]["required_minimum_mm"]:.1f} мм`, GPIO и BOM не меняются.',
            '- Ориентация и сменный адаптер зафиксированы в H1; открыты только письменное принятие фабрикой установки/FPC и входная проверка соответствия полученной партии.',
        ]
    else:
        lines += [
            '- Exact EastRising drawings control the complete panel body, 50-contact FPC, 0.50-mm pitch, 0.30-mm stiffener and contact map; donor-board geometry is no longer used.',
            '- The panel is physically oriented **with its flex toward the antenna edge**, while ILI9488 display memory and FT6236 touch coordinates rotate in firmware. The tail stays out of the LED, D-pad and function-key zone.',
            f'- The accepted upper adapter PCB position `{display["current_upper_adapter_board_xy_mm"]}` passes the current exact-body model: `0` same-face collisions and `{display["paper_fit"]["minimum_opposing_clearance_mm"]:.1f} mm` minimum opposing clearance versus `{display["paper_fit"]["required_minimum_mm"]:.1f} mm` required, with no GPIO or BOM change.',
            '- H1 fixes the orientation and replaceable adapter; only written factory acceptance of panel/FPC work and incoming-lot conformity remain open.',
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
        TOP20_CSV_PATH: render_top20_csv(result),
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
    print(f"ok: {len(result['rows'])} BOM rows; one-prototype planning ${result['summary']['planning_base_plus_post_pcba_usd_for_procurement_target']:.2f}; historical capture ${result['summary']['historical_spot_adjusted_displayed_usd']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
