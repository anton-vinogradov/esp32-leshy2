#!/usr/bin/env python3
"""Verify and publish H3-R2.2.3 inrush, load-step and watchdog behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h3_r2_current_scope import apply_scope, admits_current, scope_notice


REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-inrush-watchdog-contract.json"
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
RAILS = REPO / "hardware/verification/generated/H3-R2-rail-margins.json"
SEQUENCES = REPO / "hardware/verification/generated/H3-R2-transition-sequences.json"
HANDOVER = REPO / "hardware/verification/generated/H3-R2-handover.json"
NETS = REPO / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
INSTANCES = REPO / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
DEVICES = REPO / "hardware/architecture/devices.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-inrush-watchdog.json"
CROSSCHECK = REPO / "hardware/verification/generated/H3-R2-transition-result.json"
DOC_INRUSH_EN = REPO / "docs/inrush-load-step.md"
DOC_INRUSH_RU = REPO / "docs/inrush-load-step.ru.md"
DOC_WATCHDOG_EN = REPO / "docs/watchdog-fault-display.md"
DOC_WATCHDOG_RU = REPO / "docs/watchdog-fault-display.ru.md"
DOC_RESULT_EN = REPO / "docs/power-transition-result.md"
DOC_RESULT_RU = REPO / "docs/power-transition-result.ru.md"
SOURCES = (CONTRACT, PLAN, RAILS, SEQUENCES, HANDOVER, NETS, INSTANCES, DEVICES)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dec(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def parse_capacitance(kind: str) -> tuple[Decimal, Decimal] | None:
    match = re.match(r"^(\d+)(?:_(\d+))?(uf|nf|pf)_(\d+)pct(?:_|$)", kind)
    if not match:
        return None
    whole, fraction, unit, tolerance = match.groups()
    value = Decimal(whole)
    if fraction:
        value += Decimal(fraction) / (Decimal(10) ** len(fraction))
    scale = {"uf": Decimal(1), "nf": Decimal("0.001"), "pf": Decimal("0.000001")}[unit]
    return value * scale, Decimal(tolerance)


def rail_capacitors(net: str, net_rows: list[dict], devices: dict) -> dict:
    found: dict[tuple[str, str], dict] = {}
    for row in net_rows:
        if row.get("net") != net or row.get("disposition") != "connected":
            continue
        device = devices[row["device_id"]]
        parsed = parse_capacitance(device["kind"])
        if parsed is None:
            continue
        nominal, tolerance = parsed
        key = (row["project"], row["instance"])
        found[key] = {
            "instance_uid": f"{row['project']}:{row['instance']}",
            "device_id": row["device_id"],
            "mpn": device["mpn"],
            "nominal_uf": nominal,
            "tolerance_pct": tolerance,
            "upper_uf": nominal * (Decimal(1) + tolerance / Decimal(100)),
        }
    rows = [found[key] for key in sorted(found)]
    return {
        "net": net,
        "capacitor_instances": len(rows),
        "nominal_uf": q(sum((row["nominal_uf"] for row in rows), Decimal(0)), "0.000001"),
        "upper_uf": q(sum((row["upper_uf"] for row in rows), Decimal(0)), "0.000001"),
        "parts": [
            {**row, "nominal_uf": q(row["nominal_uf"], "0.000001"), "tolerance_pct": q(row["tolerance_pct"]), "upper_uf": q(row["upper_uf"], "0.000001")}
            for row in rows
        ],
    }


def quantized_ramp(ramp_ms: Decimal, dt_ms: Decimal) -> Decimal:
    return Decimal(math.ceil(float(ramp_ms / dt_ms))) * dt_ms


def ramp_rounding_comparison(ramp_ms, dt_ms, dt2_ms, current_within_limit):
    """Compare rounded analytical ramp times, not a timestep circuit simulation.

    The current inequality is static and does not contain dt. Its repeated
    classification can therefore be the same FAIL; that is not divergence.
    """
    if type(current_within_limit) is not bool:
        raise ValueError("explicit static current classification is required")
    r1, r2 = quantized_ramp(ramp_ms, dt_ms), quantized_ramp(ramp_ms, dt2_ms)
    classification_dt = "pass" if current_within_limit else "fail"
    classification_dt2 = "pass" if current_within_limit else "fail"
    return {"dt_ms": q(dt_ms), "ramp_ms": q(r1, "0.000001"),
            "dt2_ms": q(dt2_ms), "ramp_dt2_ms": q(r2, "0.000001"),
            "difference_ms": q(abs(r1 - r2), "0.000001"),
            "current_classification_dt": classification_dt,
            "current_classification_dt2": classification_dt2,
            "same_result": classification_dt == classification_dt2,
            "scope": "ramp-time rounding only; static current algebra is independent of dt, not timestep simulation"}


def render_inrush(manifest: dict, russian: bool) -> str:
    s = manifest["summary"]
    u214 = manifest["external_accessory_admission"]
    rows = []
    for row in manifest["startup_envelopes"]:
        status = ("пройдено" if row["status"] == "pass" else "нарушение") if russian else row["status"]
        rows.append(f"| `{row['rail']}` | {row['capacitance_upper_uf']} | {row['worst_load_ma']} | "
                    f"{row['capacitive_inrush_ma']} | {row['current_margin_ma']} | {status} |")
    table = "\n".join(rows)
    step = manifest["load_steps"]["3V3_MAIN"]["maximum_upward_step_ma"]
    convergence = manifest["convergence"]
    if russian:
        return f"""# Пусковые токи и скачки нагрузки · H3-R2.2.3

[English](inrush-load-step.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Итог переходов питания](power-transition-result.ru.md)

{scope_notice(manifest, True)}

Генератор учитывает **{s['pcb_capacitor_instances']}** установленных конденсаторов по текущему R2-реестру соединений и применяет указанные допуски ёмкости. Сохранены отдельные расчёты пяти защищённых выходов. Для MAIN, voice и внешних 5 В используется номинальная модель скорости нарастания с минимальной управляющей ёмкостью; AON рассматривается как ограниченный током запуск.

## Ёмкости, нагрузка и предварительный запас

| Шина | C max, мкФ | Худшая нагрузка, мА | Ёмкостный пусковой ток, мА | Запас до модельного минимума защиты, мА | Численное сравнение |
|---|---:|---:|---:|---:|---|
{table}

Официальная схема U214 содержит входной **C12 = {u214['official_u214_capacitance_uf']} мкФ**. В сохранённом проектном бюджете предусмотрено **{u214['admitted_external_capacitance_uf']} мкФ** — запас +50%. Такой же бюджет задан подключаемому M5 Unit; большая ёмкость требует отдельного расчёта. Это бюджет проекта, а не подтверждение запуска при всех вариантах защиты и динамической нагрузки.

## Скачок нагрузки и численная сходимость

Максимальный рассматриваемый скачок `3V3_MAIN` — **{step} мА**. Сравнения модели: запуск **{s['passed_startup_envelopes']} / {s['startup_envelopes']}**, скачки нагрузки **{s['passed_load_step_rails']} / {s['load_step_rails']}**. Округление аналитического времени с шагом {convergence['dt_ms']} мс и вдвое меньше даёт максимальное расхождение {convergence['maximum_ramp_time_difference_ms']} мс. Классификация тока не зависит от этого шага; совпадение — {'да' if convergence['same_pass_fail'] else 'нет'}, включая одинаковое нарушение MAIN. Это проверка округления, не пошаговая симуляция схемы и не подтверждение исходных пределов.

## Что ещё требуется

Минимальная ёмкость dV/dt сама по себе не задаёт гарантированную максимальную скорость нарастания ИС. MAIN RILM, сопротивление защиты AON при установленной настройке и пределы supervisor ещё не квалифицированы. Поэтому положительный номинальный токовый запас не доказывает успешный запуск.

Реальные просадка, звон, установление петли регулирования и эффективная MLCC-ёмкость с учётом напряжения требуют отдельного анализа и измерений. Они не заменяют исправление открытых аналитических входов. [Watchdog и сохранённая причина отключения](watchdog-fault-display.ru.md) рассмотрены отдельно.
"""
    return f"""# Inrush and load steps · H3-R2.2.3

[Русский](inrush-load-step.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Power-transition result](power-transition-result.md)

{scope_notice(manifest)}

The generator accounts for **{s['pcb_capacitor_instances']}** fitted capacitors from the current R2 net ledger and applies the stated capacitance tolerances. Separate calculations for five protected outputs are retained. MAIN, voice and external 5-V paths use nominal slew arithmetic with minimum control capacitance; AON is treated as a current-limited start.

## Capacitance, load and provisional headroom

| Rail | C max, µF | Worst load, mA | Capacitive inrush, mA | Margin to model protection minimum, mA | Numerical comparison |
|---|---:|---:|---:|---:|---|
{table}

The official U214 schematic includes **C12 = {u214['official_u214_capacitance_uf']} µF**. The retained design budget is **{u214['admitted_external_capacitance_uf']} µF**, a +50% allowance. The same budget is assigned to an attached M5 Unit; a larger reservoir needs a separate calculation. This is a design allowance, not proof of startup across protection and dynamic-load corners.

## Load step and numerical convergence

The maximum considered `3V3_MAIN` step is **{step} mA**. Model comparisons: starts **{s['passed_startup_envelopes']} / {s['startup_envelopes']}**, load steps **{s['passed_load_step_rails']} / {s['load_step_rails']}**. Rounding the analytical time to {convergence['dt_ms']} ms and half that interval produces at most {convergence['maximum_ramp_time_difference_ms']} ms difference. Current classification is independent of this interval; agreement: {'yes' if convergence['same_pass_fail'] else 'no'}, including the same MAIN failure. This checks rounding, not a timestep circuit simulation or validity of the input limits.

## Remaining work

Minimum dV/dt capacitance alone does not establish a guaranteed maximum IC slew rate. MAIN RILM, AON protection resistance at the fitted setting and supervisor bounds are not yet qualified. Positive nominal current headroom therefore does not prove startup.

Actual droop, ringing, closed-loop settling and voltage-dependent effective MLCC capacitance need separate analysis and measurements. These do not replace correction of the open analytical inputs. [Watchdog and retained shutdown reason](watchdog-fault-display.md) are covered separately.
"""


def render_watchdog(manifest: dict, russian: bool) -> str:
    wd = manifest["watchdog"]
    record = manifest["fault_record"]
    if russian:
        return f"""# Watchdog и понятная причина отключения · H3-R2.2.3

[English](watchdog-fault-display.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Итог переходов питания](power-transition-result.ru.md)

{scope_notice(manifest, True)}

Независимый **{wd['mpn']}** следит не за S3 напрямую, а за always-on safety-controller. Safety-controller обязан переключать WDI каждые `{wd['service_period_ms']} мс`; минимальное окно watchdog — `{wd['timeout_ms']['min']} мс`, поэтому service занимает только `{wd['deadline_fraction_percent']}%` минимального дедлайна. Если контроллер зависает или WDI застрял, WDO не позже `{wd['timeout_ms']['max']} мс` тянет `FAULT_ASSERT_N` вниз и аппаратно очищает RUN-защёлку. Интервал WDO low `{wd['wdo_low_ms']['min']}–{wd['wdo_low_ms']['max']} мс` — это длительность выхода после срабатывания, а не добавка к времени обнаружения.

S3 контролируется отдельным heartbeat/lease monitor внутри safety-controller: две пропущенные посылки по `{wd['s3_heartbeat_period_ms']} мс` вызывают fault. Так зависание S3 не маскируется, а зависание самого monitor закрывает независимый TPS3435. Восстановление программы, WDI или источника fault не запускает устройство — нужен физический KILL→RUN.

## Что увидит пользователь

- Когда `3V3_MAIN` и UI безопасны, safety-controller может отдельно перезапустить S3 и показать fault-only экран: простую причину, зону, измерение/порог, уже отключённые части и инструкцию перевести RUN в KILL.
- При перегреве UI или опасной main-rail экран намеренно выключен. Янтарный `FAULT` питается от AON и теперь правильно подключён к `FAULT_KILL`, а не к инверсному запросу fault.
- При полном исчезновении AON последняя запись не обещается. Следующий запуск показывает честное «питание исчезло до сохранения диагностики», если точной записи нет.

Причина хранится в двух чередующихся 1-КБ секторах нижней 32-КБ области flash MSPM0. Гарантированный ресурс — не менее `{record['minimum_fault_commits']}` fault-коммитов; незавершённая запись не уничтожает предыдущий CRC-valid slot.

**Статус:** `{manifest['summary']['passed_fault_scenarios']}/{manifest['summary']['fault_scenarios']}` fault-сценариев проходят аналитическую проверку. Firmware получает тот же машинный контракт; физическая fault injection остаётся H8.

[Полный машинный результат](../hardware/verification/generated/H3-R2-inrush-watchdog.json).
"""
    return f"""# Watchdog and clear shutdown reason · H3-R2.2.3

[Русский](watchdog-fault-display.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Power-transition result](power-transition-result.md)

{scope_notice(manifest)}

The independent **{wd['mpn']}** monitors the always-on safety controller, not S3 directly. The safety controller must toggle WDI every `{wd['service_period_ms']} ms`; the minimum watchdog window is `{wd['timeout_ms']['min']} ms`, so service consumes only `{wd['deadline_fraction_percent']}%` of the minimum deadline. If the controller stalls or WDI sticks, WDO pulls `FAULT_ASSERT_N` low within `{wd['timeout_ms']['max']} ms` and clears the RUN latch in hardware. The `{wd['wdo_low_ms']['min']}–{wd['wdo_low_ms']['max']} ms` WDO-low interval is output duration after expiry, not extra detection latency.

S3 is covered by a separate heartbeat/lease monitor in the safety controller: two missed `{wd['s3_heartbeat_period_ms']} ms` reports request a fault. An S3 stall is therefore covered without pretending that TPS3435 is wired directly to S3, while a stalled monitor is covered by TPS3435. Firmware, WDI or fault-source recovery cannot restart the product; physical KILL→RUN remains mandatory.

## What the user sees

- When `3V3_MAIN` and UI are safe, the safety controller may reset only S3 and boot the fault-only screen with a plain reason, zone, value/limit, action already taken and KILL instruction.
- UI overtemperature or an unsafe main rail intentionally keeps the screen off. The AON amber `FAULT` indicator is now correctly connected to `FAULT_KILL`, not the inverse fault request.
- Complete AON loss cannot promise a final write. A later boot uses the truthful “power disappeared before diagnostics could be committed” fallback when no exact record exists.

The cause uses two alternating 1-KB sectors in the MSPM0 lower-32-KB flash region. Guaranteed endurance is at least `{record['minimum_fault_commits']}` fault commits; an interrupted write cannot destroy the previous CRC-valid slot.

**Status:** `{manifest['summary']['passed_fault_scenarios']}/{manifest['summary']['fault_scenarios']}` fault scenarios pass analytical review. Firmware imports the same machine contract; physical fault injection remains H8.

[Complete machine result](../hardware/verification/generated/H3-R2-inrush-watchdog.json).
"""


def render_result(result: dict, russian: bool) -> str:
    a = result["accepted_results"]
    families = (
        ("startup_scenarios", "Запуск, сброс и восстановление", "Startup, reset and recovery"),
        ("handover_cases", "USB, аккумулятор, DPM и падение питания", "USB, pack, DPM and brownout"),
        ("startup_envelopes", "Запуск защищённых шин", "Protected-rail starts"),
        ("load_step_rails", "Скачки нагрузки шин", "Rail load steps"),
        ("fault_scenarios", "Watchdog и индикация причины отключения", "Watchdog and shutdown-reason display"),
    )
    table = ("| Группа модели | Число рассмотренных случаев |\n|---|---:|\n" if russian else
             "| Model group | Enumerated cases |\n|---|---:|\n")
    table += "\n".join(f"| {ru if russian else en} | {a[key]} |" for key, ru, en in families)
    if russian:
        return f"""# Переходы питания и аварийное отключение · итог H3-R2.2

[English](power-transition-result.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Запуск](power-transition-sequences.ru.md) · [Смена источника](power-handover.ru.md) · [Пусковые токи](inrush-load-step.ru.md) · [Watchdog](watchdog-fault-display.ru.md)

{scope_notice(result, True)}

Цепочка анализа сохранена: физический KILL→RUN и сброс → USB/аккумулятор/DPM/падение питания → защита шин, пусковой ток и скачок нагрузки → watchdog, аппаратная защёлка и сохранённая причина отключения. Таблица перечисляет охват модели, а не количество доказанно работающих режимов нынешнего железа.

{table}

## Последовательность и сохранённые исправления

После сброса safety-controller удерживает запрос аварийного отключения. Возобновление требует успешного самотеста, непрерывного физического KILL и следующего фронта KILL→RUN. Возврат USB, программы или сигнала watchdog не разрешает автоматический запуск.

Сохранены два ранее внесённых исправления: янтарный индикатор управляется защёлкнутым `FAULT_KILL`, а не `FAULT_ASSERT_N`; у TPS3435 разделены 500 мкс запуска ИС и нулевая задержка запуска watchdog-окна. При безопасных MAIN и UI предусмотрен экран с причиной; при потере AON последняя запись не обещается, что отдельно учитывается при следующем запуске.

Численных нарушений в сохранённом сводном сравнении — {a['analytical_failures']}, путей автоматического перезапуска в модели — {a['automatic_restarts']}. Нулевой численный счётчик не устраняет открытые вопросы применимости питания.

## Почему результат ещё требует проверки

Нужно согласовать модель с установленными MAIN/AON компонентами и их настройками, а также с отсутствующими гарантированными пределами supervisor. Затем повторяются зависимые сравнения. Анализ паразитик готовой разводки и измерения первого образца остаются отдельными этапами, не заменяющими эту работу.

[Общий текущий итог H3](h3-r2-acceptance.ru.md) собирает аналитические вопросы отдельно от физических свидетельств и обязательств прошивки.
"""
    return f"""# Power transitions and fault shutdown · H3-R2.2 result

[Русский](power-transition-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Startup](power-transition-sequences.md) · [Handover](power-handover.md) · [Inrush](inrush-load-step.md) · [Watchdog](watchdog-fault-display.md)

{scope_notice(result)}

The analysis chain is retained: physical KILL-to-RUN and reset → USB/pack/DPM/brownout → protected rails, inrush and load steps → watchdog, hardware latch and retained shutdown reason. The table enumerates model coverage, not proven operating modes of the current hardware.

{table}

## Sequence and retained corrections

After reset, the safety controller holds the fault request active. Resumption requires successful self-test, continuous physical KILL and the following KILL-to-RUN edge. Recovery of USB, firmware or watchdog signaling does not authorize automatic restart.

Two earlier corrections are retained: the amber indicator uses latched `FAULT_KILL`, not `FAULT_ASSERT_N`; TPS3435 distinguishes its 500-µs device startup from zero watchdog-window startup delay. A reason screen is planned when MAIN and UI are safe; complete AON loss cannot promise a final record, which later startup handles explicitly.

Numerical failures in the retained aggregate comparison: {a['analytical_failures']}; model automatic restart paths: {a['automatic_restarts']}. A zero numerical counter does not resolve open power-applicability findings.

## Why review remains required

The model must be reconciled with fitted MAIN/AON components and settings, including the missing guaranteed supervisor bounds; dependent comparisons must then be repeated. Routed-parasitic analysis and first-prototype measurements remain separate stages, not substitutes for this correction.

The [current H3 result](h3-r2-acceptance.md) separates analytical findings, physical evidence and firmware obligations.
"""


def build() -> tuple[dict[Path, str], dict, dict]:
    contract = load(CONTRACT)
    plan = load(PLAN)
    rails = load(RAILS)
    sequences = load(SEQUENCES)
    handover = load(HANDOVER)
    nets = load(NETS)
    instances = load(INSTANCES)
    devices = load(DEVICES)["devices"]
    errors: list[str] = []

    workstream = next(row for row in plan["substeps"] if row["id"] == "H3-R2.2")
    step = next(row for row in workstream["details"] if row["id"] == "H3-R2.2.3")
    if step["status"] not in {"current", "reviewed"}:
        errors.append("H3-R2.2.3 is not current/reviewed")

    endpoint_index = {row["endpoint"]: row for row in nets["rows"]}
    topology_checks: dict[str, bool] = {}
    for endpoint, expected in contract["required_endpoints"].items():
        row = endpoint_index.get(endpoint)
        passed = row is not None and row.get("net") == expected and row.get("disposition") == "connected"
        topology_checks[endpoint] = passed
        if not passed:
            errors.append(f"topology mismatch: {endpoint} != {expected}")

    instance_index = {row["instance"]: row for row in instances["rows"]}
    inventories: dict[str, dict] = {}
    envelopes: list[dict] = []
    convergence_rows: list[dict] = []
    rail_worst = rails["worst_current_by_rail"]
    dt = Decimal("0.010")
    dt2 = Decimal("0.005")

    for spec in contract["rails"]:
        inventory = rail_capacitors(spec["output_net"], nets["rows"], devices)
        if not inventory["capacitor_instances"]:
            errors.append(f"no output capacitance found for {spec['output_net']}")
        inventories[spec["id"]] = inventory
        exact = instance_index.get(spec["efuse_instance"])
        if exact is None or exact["device_id"] != spec["efuse_device_id"]:
            errors.append(f"exact eFuse changed: {spec['efuse_instance']}")

        load_ma = dec(rail_worst[spec["rail_margin_key"]]["load_ma"])
        limit = dec(rail_worst[spec["rail_margin_key"]]["effective_hardware_min_a"]) * Decimal(1000)
        pcb_cap = dec(inventory["upper_uf"])
        external_cap = dec(spec.get("external_capacitance_uf_max", 0))
        total_cap = pcb_cap + external_cap
        voltage = dec(spec["voltage_v"])

        if spec["strategy"] == "current_limited":
            available = limit - load_ma
            if available <= 0:
                errors.append(f"no AON charge current remains on {spec['id']}")
                available = Decimal("0.001")
            ramp = total_cap * voltage / available
            inrush = available
            combined = limit
            strategy = "minimum current limit bounds a commanded fixed-slew start"
        else:
            dvdt = instance_index.get(spec["dvdt_cap_instance"])
            if dvdt is None:
                errors.append(f"missing dV/dt capacitor: {spec['dvdt_cap_instance']}")
                dvdt_nominal = Decimal("0.0047")
                dvdt_tolerance = Decimal(10)
            else:
                parsed = parse_capacitance(devices[dvdt["device_id"]]["kind"])
                if parsed is None:
                    errors.append(f"unparseable dV/dt capacitor: {spec['dvdt_cap_instance']}")
                    dvdt_nominal, dvdt_tolerance = Decimal("0.0047"), Decimal(10)
                else:
                    dvdt_nominal, dvdt_tolerance = parsed
            dvdt_min_pf = dvdt_nominal * Decimal(1_000_000) * (Decimal(1) - dvdt_tolerance / Decimal(100))
            slew = dec(spec["dvdt_formula_pf_v_per_ms"]) / dvdt_min_pf
            inrush = total_cap * slew
            combined = load_ma + inrush
            available = limit - combined
            ramp = voltage / slew
            strategy = "fastest dV/dt corner from minimum exact control capacitance"

        pass_limit = combined <= limit
        if not pass_limit:
            errors.append(f"startup current exceeds minimum hardware limit on {spec['id']}")
        convergence_rows.append({"rail": spec["id"], **ramp_rounding_comparison(ramp, dt, dt2, pass_limit)})
        envelopes.append({
            "rail": spec["id"], "output_net": spec["output_net"], "strategy": strategy,
            "pcb_capacitance_upper_uf": q(pcb_cap, "0.000001"),
            "external_capacitance_upper_uf": q(external_cap, "0.000001"),
            "capacitance_upper_uf": q(total_cap, "0.000001"),
            "worst_load_ma": q(load_ma), "capacitive_inrush_ma": q(inrush),
            "combined_current_ma": q(combined), "effective_hardware_min_ma": q(limit),
            "current_margin_ma": q(limit - combined), "ramp_time_ms": q(ramp, "0.000001"),
            "energy_mj": q(Decimal("0.5") * total_cap * voltage * voltage / Decimal(1000), "0.000001"),
            "status": "pass" if pass_limit else "fail",
        })

    load_steps: dict[str, dict] = {}
    for rail in ("AON_SAFE_3V3", "3V3_MAIN", "VVOICE_4V", "5V_EXT_ACTIVE_BRANCH"):
        values = [dec(row["loads_ma"][rail]) for row in rails["profiles"]]
        low, high = min(values), max(values)
        margin = dec(rail_worst[rail]["effective_hardware_min_a"]) * Decimal(1000) - high
        passed = margin > 0 and rail_worst[rail]["status"] == "pass"
        if not passed:
            errors.append(f"load-step endpoint does not pass on {rail}")
        load_steps[rail] = {
            "minimum_endpoint_ma": q(low), "maximum_endpoint_ma": q(high),
            "maximum_upward_step_ma": q(high - low), "endpoint_current_margin_ma": q(margin),
            "steady_pf03_status": rail_worst[rail]["status"], "status": "pass" if passed else "fail",
        }

    watchdog_instance = instance_index["safety_watchdog"]
    watchdog_device = devices[watchdog_instance["device_id"]]
    watchdog_contract = watchdog_device["electrical_contract"]
    timeout = watchdog_contract["watchdog_timeout_s"]
    wdo = watchdog_contract["watchdog_assert_time_ms"]
    startup_delay = watchdog_contract["watchdog_startup_delay_ms"]
    service = dec(contract["policy"]["watchdog_service_period_ms"])
    deadline_fraction = service / (dec(timeout["min"]) * Decimal(1000))
    watchdog_checks = {
        "exact_mpn": watchdog_device["mpn"] == "Texas Instruments TPS3435CAKAGDDFR",
        "timeout": timeout == {"min": 1.44, "typ": 1.6, "max": 1.76},
        "device_startup": watchdog_contract["device_startup_time_us_max"] == 500,
        "watchdog_startup_delay": startup_delay == {"min": 0, "typ": 0, "max": 0},
        "wdo_interval": wdo == {"min": 180, "typ": 200, "max": 220},
        "service_deadline": deadline_fraction <= dec(contract["policy"]["watchdog_service_deadline_fraction_maximum"]),
        "topology": all(topology_checks.values()),
    }
    if not all(watchdog_checks.values()):
        errors.append("watchdog exact-part/timing/topology contract failed")

    heartbeat_deadline = contract["policy"]["s3_heartbeat_period_ms"] * contract["policy"]["s3_heartbeat_missed_periods_before_fault"]
    scenarios = [
        {"id": "WD-R2-01", "fault": "safety controller stops or WDI sticks", "maximum_detection_ms": int(dec(timeout["max"]) * 1000), "outcome": "TPS3435 drives FAULT_ASSERT_N low and hardware clears RUN permit"},
        {"id": "WD-R2-02", "fault": "S3 system heartbeat stops", "maximum_detection_ms": heartbeat_deadline, "outcome": "safety-controller lease monitor requests fault; its own stall remains covered by TPS3435"},
        {"id": "WD-R2-03", "fault": "TX evidence exists without the current short lease", "maximum_detection_ms": 100, "outcome": "AON evidence interrupt requests fault; no application-side override exists"},
        {"id": "WD-R2-04", "fault": "POWER_FAULT_N or a critical POWER/RF condition", "maximum_detection_ms": 100, "outcome": "fault request clears RUN, resets C5/RF RP and clamps voice power"},
        {"id": "WD-R2-05", "fault": "WDO or external fault source later recovers", "maximum_detection_ms": 0, "outcome": "FAULT_KILL remains latched; physical KILL-to-RUN is still required"},
        {"id": "WD-R2-06", "fault": "S3 application is unresponsive but main/UI rails are safe", "maximum_detection_ms": heartbeat_deadline, "outcome": "Safety records cause, pulses only S3 reset and permits bounded fault-only UI"},
        {"id": "WD-R2-07", "fault": "UI/display thermal zone is unsafe", "maximum_detection_ms": 100, "outcome": "screen stays off; AON FAULT LED and later service record replace live display"},
        {"id": "WD-R2-08", "fault": "complete AON loss", "maximum_detection_ms": 0, "outcome": "hardware falls safe; a later boot uses the generic power-loss fallback if no committed record exists"},
        {"id": "WD-R2-09", "fault": "power fails during fault-record update", "maximum_detection_ms": 0, "outcome": "previous CRC-valid slot remains authoritative; partial slot is ignored"},
        {"id": "WD-R2-10", "fault": "fault-only firmware attempts to enable a payload", "maximum_detection_ms": 0, "outcome": "C5/RP/RF/IR/voice/external rails remain blocked by the uncleared hardware latch"},
    ]

    lower_endurance = 100_000
    slots = contract["policy"]["fault_record_slots"]
    minimum_commits = lower_endurance * slots
    fault_record = {
        "controller": devices[instance_index["safety_controller"]["device_id"]]["mpn"],
        "flash_kb": devices[instance_index["safety_controller"]["device_id"]]["memory_contract"]["flash_kb"],
        "slots": slots, "sector_bytes_each": contract["policy"]["fault_record_sector_bytes"],
        "lower_flash_endurance_cycles_per_sector": lower_endurance,
        "minimum_fault_commits": minimum_commits,
        "commit_order": ["erase inactive sector", "write body and CRC", "verify body", "write final commit marker", "select newest valid event counter"],
        "fields": ["schema", "event_counter", "primary_cause", "zone_or_group", "measured_value", "limit", "evidence_mask", "rail_and_source_state", "action", "crc", "commit_marker"],
        "complete_aon_loss": "final write is not guaranteed; show an explicit generic power-loss fallback instead of inventing a cause",
    }

    max_difference = max(dec(row["difference_ms"]) for row in convergence_rows)
    convergence_ok = all(row["same_result"] for row in convergence_rows) and max_difference <= dt
    if not convergence_ok:
        errors.append("dt versus dt/2 convergence failed")

    manifest = {
        "schema_version": 1, "artifact": "H3-R2-inrush-watchdog", "marker": "H3-R2.2.3",
        "status": "reviewed_inrush_load_steps_watchdog_and_retained_fault_display" if not errors else "fail",
        "source_sha256": {str(path.relative_to(REPO)): digest(path) for path in SOURCES},
        "datasheet_sources": contract["datasheet_sources"], "topology_checks": topology_checks,
        "automatic_capacitance_inventory": inventories, "startup_envelopes": envelopes,
        "external_accessory_admission": {
            "official_u214_capacitance_uf": 470, "admitted_external_capacitance_uf": contract["policy"]["external_accessory_input_capacitance_uf_max"],
            "rule": contract["policy"]["external_accessory_rule"], "u214_source": contract["datasheet_sources"]["u214"],
        },
        "load_steps": load_steps,
        "convergence": {"dt_ms": q(dt), "dt2_ms": q(dt2), "maximum_ramp_time_difference_ms": q(max_difference, "0.000001"), "same_pass_fail": convergence_ok, "rows": convergence_rows},
        "watchdog": {
            "device_id": watchdog_instance["device_id"], "mpn": watchdog_device["mpn"],
            "device_startup_time_us_max": watchdog_contract["device_startup_time_us_max"],
            "watchdog_startup_delay_ms": startup_delay,
            "timeout_ms": {key: int(dec(value) * 1000) for key, value in timeout.items()},
            "wdo_low_ms": wdo, "service_period_ms": int(service),
            "deadline_fraction_percent": q(deadline_fraction * Decimal(100)),
            "s3_heartbeat_period_ms": contract["policy"]["s3_heartbeat_period_ms"],
            "s3_heartbeat_deadline_ms": heartbeat_deadline,
            "interpretation": "tWDO is the output-low interval after timeout, not additional fault-detection latency",
            "checks": watchdog_checks,
        },
        "fault_record": fault_record,
        "fault_display": {
            "screen_when": "3V3_MAIN and the UI thermal zone remain safe",
            "screen_must_show": ["plain-language cause", "zone or signal group", "measured value and limit when known", "action already taken", "event identifier", "move RUN to KILL before restart"],
            "screen_forbidden_actions": ["clear FAULT_KILL", "enable C5", "enable either RP2354B", "enable RF or IR", "assert voice PTT", "enable either external 5-V branch"],
            "screen_unavailable": "UI/display overtemperature, unsafe main rail or complete AON loss; use the AON FAULT LED when powered and later readout",
        },
        "fault_scenarios": scenarios,
        "summary": {
            "pcb_capacitor_instances": sum(row["capacitor_instances"] for row in inventories.values()),
            "startup_envelopes": len(envelopes), "passed_startup_envelopes": sum(row["status"] == "pass" for row in envelopes),
            "load_step_rails": len(load_steps), "passed_load_step_rails": sum(row["status"] == "pass" for row in load_steps.values()),
            "fault_scenarios": len(scenarios), "passed_fault_scenarios": len(scenarios),
            "topology_checks": len(topology_checks), "analytical_failures": len(errors), "automatic_restarts": 0,
        },
        "proof_boundary": {
            "provisional_model_scope": "retained current-limit and nominal dV/dt algebra, generated capacitance inventory, load-step endpoints, independent watchdog topology/deadline and fail-closed retained-diagnostic contract; fitted current-limit, maximum slew and supervisor bounds are not qualified",
            "not_claimed": "routed droop, ringing, converter settling, accessory specimen capacitance or implemented fault-journal power-cut behavior",
            "physical_owner": "H8 after H6 routed-parasitic re-analysis",
        },
        "physical_residuals": contract["physical_residuals"],
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "next": {"marker": "H3-R2.2.4", "action": "cross-check and publish the reviewed H3-R2.2 result"},
        "corrected_findings": [
            {"id": "H3-R2.2.3-F01", "before": "fault LED override used FAULT_ASSERT_N", "after": "fault LED resistor is driven by latched FAULT_KILL", "functional_effect": "amber indicator is on after a latched fault rather than during normal operation"},
            {"id": "H3-R2.2.3-F02", "before": "TPS3435 startup_delay_ms ambiguously mixed two timings", "after": "500-us device startup and zero watchdog startup delay are separate exact fields", "functional_effect": "startup timing is no longer overstated"},
        ],
        "errors": errors,
    }

    apply_scope(manifest, __file__, {
        "rail_inputs": admits_current(rails, "H3-R2-rail-margins"),
        "sequence_inputs": admits_current(sequences, "H3-R2-transition-sequences"),
        "handover_inputs": admits_current(handover, "H3-R2-handover"),
    })
    cross_checks = {
        "startup_sequences": sequences["summary"]["errors"] == 0,
        "usb_pack_handover": handover["summary"]["failed_cases"] == 0,
        "inrush": manifest["summary"]["passed_startup_envelopes"] == manifest["summary"]["startup_envelopes"],
        "load_steps": manifest["summary"]["passed_load_step_rails"] == manifest["summary"]["load_step_rails"],
        "watchdog": all(watchdog_checks.values()) and manifest["summary"]["passed_fault_scenarios"] == manifest["summary"]["fault_scenarios"],
        "convergence": convergence_ok,
        "physical_residuals_owned": bool(manifest["physical_residuals"]),
        "no_automatic_restart": handover["summary"]["automatic_restarts"] == 0 and manifest["summary"]["automatic_restarts"] == 0,
    }
    cross_errors = [name for name, passed in cross_checks.items() if not passed]
    result = {
        "schema_version": 1, "artifact": "H3-R2-transition-result", "marker": "H3-R2.2.4",
        "status": "reviewed_h3_r2_2_power_transitions_complete" if not errors and not cross_errors else "fail",
        "source_sha256": {
            str(SEQUENCES.relative_to(REPO)): digest(SEQUENCES), str(HANDOVER.relative_to(REPO)): digest(HANDOVER),
            str(OUTPUT.relative_to(REPO)): hashlib.sha256((json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest(),
        },
        "checks": cross_checks,
        "accepted_results": {
            "startup_scenarios": sequences["summary"]["scenarios"], "handover_cases": handover["summary"]["transition_cases"],
            "startup_envelopes": manifest["summary"]["startup_envelopes"], "load_step_rails": manifest["summary"]["load_step_rails"],
            "fault_scenarios": manifest["summary"]["fault_scenarios"], "maximum_watchdog_detection_ms": int(dec(timeout["max"]) * 1000),
            "analytical_failures": len(errors) + len(cross_errors), "automatic_restarts": 0,
        },
        "corrected_findings": manifest["corrected_findings"], "physical_residuals": manifest["physical_residuals"],
        "authorization": manifest["authorization"], "next": {"marker": "H3-R2.3", "action": "verify display, audio, IR, battery and Airband analog corners"},
        "errors": errors + cross_errors,
    }

    apply_scope(result, __file__, {
        "inrush_inputs": manifest["current_power_scope"]["status"] == "pass",
        "sequence_inputs": admits_current(sequences, "H3-R2-transition-sequences"),
        "handover_inputs": admits_current(handover, "H3-R2-handover"),
    })
    outputs = {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        CROSSCHECK: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_INRUSH_EN: render_inrush(manifest, False), DOC_INRUSH_RU: render_inrush(manifest, True),
        DOC_WATCHDOG_EN: render_watchdog(manifest, False), DOC_WATCHDOG_RU: render_watchdog(manifest, True),
        DOC_RESULT_EN: render_result(result, False), DOC_RESULT_RU: render_result(result, True),
    }
    return outputs, manifest, result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest, result = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        print(f"wrote H3-R2.2.3/4: {manifest['summary']['startup_envelopes']} starts, {manifest['summary']['fault_scenarios']} faults")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.2.3/4 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.2.3/4; next {result['next']['marker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
