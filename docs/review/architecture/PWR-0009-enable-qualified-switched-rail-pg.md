# PWR-0009 — enable-qualified switched-rail power-good evidence

- Статус: **Проведено ревью принципиальной схемы**
- Дата: 2026-08-18
- Parent rail tree: [`PWR-0008`](PWR-0008-exact-downstream-rail-tree.md)
- Decision: [`DEC-0070`](../decisions/DEC-0070-enable-qualified-switched-rail-pg.md)
- Propagation review: [`REV-0005AA`](../reviews/REV-0005AA-switched-rail-pg-qualification.md)

## Найденное несоответствие

`TPS564252DRLR.PG` — open-drain power-good, который закономерно остаётся low,
когда преобразователь выключен. Прямое wired-low объединение `VOICE_4V_PG_N`
и `EXT_5V_PG_N` с `POWER_FAULT_N` поэтому превращало штатный quiet state в
постоянную аварию. Номиналом pull-up это исправить невозможно.

Основная 3,3-В шина не имеет такого противоречия: при её отсутствии нет
работающего `TCA6424/P25` diagnostic domain. Для двух опциональных шин требуется
квалификация факта `PG` соответствующим STOP-dominant `EN`.

## Принятая схема

Каждая шина получает собственный физический `MMBT3904-7-F`:

- pin 1 `B` получает соответствующий safe `EN` через отдельный 68-kOhm 1%
  series resistor;
- pin 2 `E` получает open-drain `PG` преобразователя с pull-up внутри
  `3V3_MAIN` diagnostic domain;
- pin 3 `C` — open-collector выход в общий `POWER_FAULT_N`;
- прямые маршруты switched-rail `PG → POWER_FAULT_N` запрещены.

Два транзистора остаются двумя отдельными компонентами в machine source и
living diagram. Никакой GPIO не добавляется.

## Таблица истинности

| Safe `EN` | Converter `PG` | Qualified collector | Meaning |
|---:|---:|---|---|
| 0 | 0 | released | штатно выключенная шина |
| 0 | 1 | released | остаточный high во время выключения |
| 1 | 0 | low | запуск ещё не завершён либо rail fault |
| 1 | 1 | released | включённая исправная шина |

Таким образом fault-функция равна `EN AND NOT(PG)`. При включении low сначала
является ожидаемым `pending`, а не немедленно защёлкнутой аварией. Он обязан
освободиться в измеренном startup deadline; иначе session fails closed. При
выключении падение `EN` сразу исключает ложную аварию независимо от разряда
шины.

## Paper electrical screen

- `TPS564252 PG` гарантирует `VPG(OL) <= 0.4 V` при 4 mA.
- Target `POWER_FAULT_N` pull-up 10 kOhm на 3,3 В требует около 0,33 mA sink.
- При `RB=68 kOhm ±1%`, `VPG=0.4 V` и консервативном `VBE=0.85 V` остаётся
  около 29.8 uA base current; forced beta для 0,33 mA не превышает 11.1.
- `MMBT3904-7-F` имеет datasheet minimum `hFE=40` при 100 uA и 70 при 1 mA;
  `VCE(sat)` указан не более 0,2 В при существенно большем 10-mA test current
  и forced beta 10.
- Консервативная low-оценка на P25 — `0.4 + 0.2 = 0.6 V`, ниже
  `TCA6424A VIL(max)=0.3*VCCP=0.99 V` при 3,3 В с запасом 0,39 В.
- Краткое состояние `EN=0, PG=1` даёт reverse `VBE` до 3,3 В, ниже
  абсолютного `BVEBO=6 V`; повторные shutdown cycles остаются HIL gate.

Это расчёт принципиальной пригодности, а не температурная гарантия платы.
Prototype HIL измеряет low/high levels, startup/shutdown pulse widths,
brownout, repeated cycling и одновременное действие другого wired-low fault.

## Exact part and cost

`MMBT3904-7-F` — SOT-23 NPN 40 V / 200 mA, contacts `1 B`, `2 E`, `3 C`.
Diodes Incorporated сохраняет exact base order code; опубликованный EOL notice
для suffixed `-79` заменяет его именно на `MMBT3904-7-F`, а не снимает этот
target. LCSC `C94514` показывал не менее 18,060 штук и `$0.0159` при 50 шт.,
то есть два qualifiers добавляют около `$0.032` на устройство до assembly.

Primary evidence:

- [Diodes MMBT3904 product page](https://www.diodes.com/part/view/MMBT3904)
- [Diodes MMBT3904 datasheet](https://www.diodes.com/datasheet/download/MMBT3904.pdf)
- [LCSC C94514](https://www.lcsc.com/product-detail/C94514.html)
- [TI TPS564252 datasheet](https://www.ti.com/lit/ds/symlink/tps564252.pdf)
- [TI TCA6424A datasheet](https://www.ti.com/lit/ds/symlink/tca6424a.pdf)

## Review boundary

Принципиальная fault-функция, exact transistor/contact fit, machine routes,
стоимость и отсутствие нового GPIO получают **«Проведено ревью»**. Exact MPN
резисторов/pull-ups, температурные уровни, startup timeout и fault-injection
HIL закрываются вместе с остальными rail passives. KiCad не разрешён.
