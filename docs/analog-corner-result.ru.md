# Сводный результат analog corners

`H3.3` проверено: проходят все четыре leaf-пакета, `153` их checks и `22` сводных checks. Закрыты четырнадцать source-исправлений, незакрытых аналитических findings нет, суммарная дельта BOM на количестве 100 — лишь `0.4908 USD`. Точный текущий маркер — `H3.4.3`.

## Закрытый аналитический envelope

| Тракт | Проверенный результат |
|---|---|
| Display | 3,108510..3,285658 В на connector; начальные 40 МГц QSPI; dirty/tile работа нарезана на <=1 мс |
| Audio | corner 4-омного speaker, полные capture/playback/TX paths и ветка 625 мА; playback выключается выше 50 °C |
| IR | >=20 мА гарантированного characterization point, <=50,513 мА conservative instantaneous current, mark/trip 20 мс и local limit 75 °C |
| Battery/thermal | точные DGS20 ADC contacts, независимые MAX/BQ/ADC evidence, отключение запроса заряда при 35 °C, charge block 40 °C, cell-discharge block 60 °C и board warning/kill 65/75 °C |

Температурные правила намеренно упорядочены: нулевой запрос заряда при 35 °C, BQ backup не позже 41,03 °C, mute динамика при 50 °C, блок discharge cell при 60 °C, warning платы не позже 65 °C и `FAULT_KILL`/IR ceiling при 75 °C. Display quantum короче каждого safety deadline, и ни один radio FIFO не делит с ним bus.

## Оговорка общей шины

Перечисленный профиль 3V3_MAIN равен `2493 мА` при аналитическом allowance `2500 мА`. Аппаратный reserve защиты остаётся `28.359%`, но бумажные 7 мА — не производственный допуск. H3.6 и H8 должны измерить <=2,5 А; превышение до layout или заказа повторно открывает allowances либо функции.

## Сохранённая физическая граница

Все 17 physical-only пунктов остаются HIL gates: signal integrity/current/optics дисплея; gain/noise/acoustics/RF immunity audio; coupling/range/IEC 62471/temperature IR; identity/calibration/sensor response/charge thresholds/balance heat аккумуляторов. H3.3 не превращает их в бумажные passes.

Машинное evidence: [`H3-VRF35-analog-consolidation.json`](../hardware/verification/generated/H3-VRF35-analog-consolidation.json).
