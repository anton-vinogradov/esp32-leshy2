# FND-0049 — exact pin map did not prove every real device boundary

- Статус: **Исправлено на уровне процесса и статуса; component rows открыты**
- Дата: 2026-08-17
- Обнаружено: при возврате от старого макета к логической pin feasibility
- Решение: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Новый ledger: [`SRC-0002`](../architecture/SRC-0002-real-device-pin-provenance.md)

## Несоответствие

Исторический [`PIN-0002`](../architecture/PIN-0002-zero-based-exact-pin-maps.md)
правильно использовал module-exposed GPIO для конкретных ESP WROOM variants,
но слово `exact` распространялось шире доказательств:

- три nRF24 были интерфейсной абстракцией, а не выбранным и проверенным exact
  module MPN/revision;
- CC1101, display/touch, voice backend и часть control/safety logic не имели
  единой принятой package/module/carrier provenance;
- generic M5 Unit connector не доказывал pinout каждого фактически выбранного
  Unit SKU;
- отдельный high-throughput external profile не имел connector/transport/pin
  определения;
- legacy physical drawing использовал условные размеры nRF-модулей.

Следовательно, документ доказывал внутреннюю непротиворечивость нескольких
кандидатных MCU maps, но не точную реализуемость всей реальной сборки.

## Подтверждённый пример риска

`ESP32-C5` silicon документирует `GPIO15`, однако в
`ESP32-C5-WROOM-1U-N8R8` этот вывод используется как `SPICS1` встроенной PSRAM
и недоступен приложению. Старый `SRC-0001/PIN-0002` этот конкретный случай уже
учёл; теперь тот же уровень проверки становится обязательным для **каждого**
чипа, модуля и готового аксессуара.

Для nRF физический риск тоже не теоретический: текущий compact reference
`E01-ML01S` имеет тело `12×19 mm`, а high-power `E01-2G4M27D` —
`18×33.4 mm` и существенно другой power/antenna burden. Ни один generic
прямоугольник не может представлять оба.

## Исправление

1. `PIN-0002` явно понижен до historical candidate/reference.
2. `SRC-0002` ведёт per-device provenance и запрещает считать незакрытую строку.
3. `G2F` требует exact device/carrier proof до принятия рабочей карты.
4. Новый physical generator будет получать размеры и интерфейсы из того же
   проверяемого device inventory, что и pin ledger.
5. Прототип закрывает последний слой marking/continuity/boot/self-test; бумажный
   review не подменяется несуществующим измерением.

## Открытый остаток

Точные nRF/CC/voice/display/control parts и high-throughput external profile
ещё не выбраны. Это открытые qualification rows, а не обнаруженные GPIO
резервы. Они должны закрыться в новых complete candidates без потери wishlist.

