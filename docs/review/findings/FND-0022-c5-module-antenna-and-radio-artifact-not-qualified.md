# FND-0022 — C5 module/antenna artifact был неверно описан и ещё не квалифицирован

- Статус: **Частично исправлено консервативно; implementation finding открыт**
- Серьёзность: hardware/RF/availability/traceability blocker
- Затрагивает: `C-W5-01`–`C-W5-09`, `hardware/tscircuit/c5-buses.tsx`, antenna/power/enclosure/BOM/HIL
- Обнаружено и частично исправлено: 2026-08-16

## Несоответствие

Legacy-source задавал `U20` как снятый из текущего стандартного ряда `ESP32-C5-WROOM-1U-N8R4` с JLC/LCSC `C49308183` и называл нижний pad `ANT2` «u.FL feed». Это две разные ошибки:

1. штатный внешний IPEX-разъём модуля `-1U` — `ANT1`; он является частью самого модуля и соединяется с внешней антенной off-board coax, поэтому PCB netlist его не доказывает;
2. `ANT2` в стандартном `-1U` отключён. Его использование требует заказного варианта `T2` и согласования с Espressif, а не обычной трассы на RF-sheet;
3. прежний `N8R4` supplier SKU имеет нулевой остаток в текущем снимке и больше не указан как стандартный массовый вариант, тогда как текущий `N8R8` сохраняет тот же module class и увеличивает PSRAM с 4 до 8 MB;
4. exact antenna MPN/type/gain, cable loss, connector retention, placement, enclosure clearance и certification envelope в артефакте отсутствуют;
5. source/netlist не доказывает load-step питания при Wi-Fi TX, single-radio coexistence, RF STOP/dead-man, реальный `TXDET_C5`, emissions или self-desense с соседними 2.4 GHz трактами.

## Выполненное безопасное исправление

- source candidate заменён на текущий стандартный `ESP32-C5-WROOM-1U-N8R8`, `jlcpcb:C51950748`;
- комментарии исправлены: `ANT1` — встроенный IPEX connector вне netlist, `ANT2` — disabled alternate RF pad и остаётся неподключённым;
- parts-engine обнаружил отличающееся имя тепловых pads; legacy `GND5..GND13` заменены на реальные `EPAD1..EPAD9` и подключены к GND;
- смена candidate не объявлена производственным BOM и не закрывает RF/power qualification.

## Что остаётся открытым

- reproducible AVL/quote минимум для двух поставщиков и проверка lifecycle exact module revision;
- parts-engine/netlist, land, flash/PSRAM configuration и firmware memory-map proof именно N8R8;
- exact dual-band antenna/cable/connector assembly в пределах допустимого gain/type certification profile;
- 3.3 V peak/load-step, thermal, RF coexistence и enclosure HIL;
- hardware-observed `TX-live`, independent STOP и safe state при reset/crash/update/link loss.

## Критерий закрытия

Находка закрывается только после stage-3/4/6 artifacts и HIL exact `U20`+antenna assembly: BOM/AVL воспроизводим, ANT1 path однозначен, ANT2 не используется, supply/RF/coexistence проходят min/nom/max tests, а TX safety наблюдает фактическое состояние радио.

## Первичные источники

- [ESP32-C5-WROOM-1 / WROOM-1U datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)
- [ESP32-C5 RF coexistence guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
