# Проверка battery sensing и температурных analog-порогов · historical R1

`H3.3.4` проверено: `38` машинных проверок и четыре исправления по первичным источникам. Компоненты и стоимость BOM не изменились. Исторический маркер прогресса R1 — `H3.6.1`, worst-case thermal model плат, аккумуляторов и корпуса.

## Что теперь зафиксировано

- Используются реальные контакты MSPM0C1106 DGS20: midpoint pack — `PA25/ADC0_2`, pin 20; stack pack и POWER — `PA26/ADC0_1`, pin 1; RF/VOICE — `PA27/ADC0_0`, pin 2; UI — `PA16/ADC0_14`, pin 12.
- Делители pack используют внутренний reference 1,4 В. На электрическом экране 4,3/8,6 В их worst-case nodes равны `1.222851` и `1.180070` В, запас до минимальных 1,38 В — `157.149` и `199.930` мВ. Ожидание 20 мс, две отброшенные конверсии и усреднение не менее восьми обязательны.
- Этот АЦП — независимая грубая проверка, а не точный imbalance meter: full-corner ошибка midpoint равна `-0.190..+0.196` В, stack — `-0.427..+0.443` В. Точные cell/imbalance limits проверяет MAX17320.
- Все три board NTC 10 кОм/10 кОм измеряются относительно `VDD`. С внутренними 1,4 В они насыщали бы АЦП уже при комнатной температуре. Warning, kill и rearm ограничены кодами `880`, `740` и `1000`; open — `>=4000`, short — `<=64`.
- BQ25798 остаётся третьим независимым cell sensor: `TS_IGNORE=0`, `TS_WARM=0`, `JEITA_ISETH=0`; open и short запрещают заряд. Полный corner warm-suspend — `38.00..41.03 °C`.
- MAX17320 использует оба cell NTC и точный `nThermCfg=0x71B1`. Запрос заряда обнуляется выше 35 °C, charge блокируется около 40 °C, discharge — при 60 °C; board hotspots дают warning не позже 65 °C и защёлкивают `FAULT_KILL` не позже 75 °C.

## Граница admission

Каждая cell по MAX17320 должна быть 2,70..4,25 В, разбаланс — не более 100 мВ. Одновременно midpoint/stack/derived-upper по ADC должны лежать в грубых окнах 2,45..4,50, 4,90..9,00 и 1,90..5,10 В. Protected image/checksum, PFAIL и diagnostic pulse должны согласиться до снятия внешнего FET hold.

Midpoint divider добавляет лишь `0.339` мА·ч разбаланса нижней cell за 48 часов. Для оставленного на один-два дня устройства это ничтожно, но длительное хранение и нагрев balancing остаются обязательными HIL-измерениями.

## Исправления

| ID | Исправленный результат |
|---|---|
| H3.3.4-F01 | Board NTC измеряются ratiometric относительно VDD; reference 1,4 В используется только для pack. |
| H3.3.4-F02 | BQ25798 и MAX17320 получили явные machine-readable reset/readback configuration contracts. |
| H3.3.4-F03 | Точный B25/85=3435 K даёт MAX17320 `nThermCfg=0x71B1`. |
| H3.3.4-F04 | Точные XTAR electrical limits теперь machine-readable; сохраняются потолок 2 А и более узкая thermal policy продукта. |

## Что бумажная проверка не закрывает

Прижим и отклик sensors, ADC calibration, подлинность received cells, реальные charger thresholds и нагрев balancing остаются физическими HIL gates. Один полученный MAX17320 проходит последовательность blank → намеренно некорректная, но электрически безопасная конфигурация → проверенный golden/recovery; на каждом переходе читаются оба address space, checksum, `NVError` и bitmap оставшихся обновлений. Zero-remaining и failed-copy вводятся только в emulator/fixture: все семь физических NVM-записей не расходуются, отдельный жертвенный gauge не нужен, необратимые locks/security burns запрещены.

Open/short/swapped/reversed/missing/imbalanced состояния банков задаёт current-limited cell simulator, температурные faults и thresholds — NTC fixture. Реальные банки остаются внутри ограничений точного MPN по напряжению, току и температуре. Механические drop- и cycle-тесты разъёмов/держателя — отдельная потенциально повреждающая DVT-работа только на выделенных прототипах. 24/48-часовой прогон под питанием — обычная неразрушающая qualification. Машинный результат: [`H3-VRF34-battery-analog.json`](../hardware/verification/generated/H3-VRF34-battery-analog.json).
