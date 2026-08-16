# AUD-0002 — снижение стоимости без потерь

- Статус: **В работе**
- Основание: `DEC-0005`
- Этап начала: 2; основной BOM-аудит — этап 4
- Дата начала: 2026-08-15

## Базовая точка

Legacy оценивает электронику примерно в `$102`, а полную сборку — в `$130–155`, но это не воспроизводимый BOM:

- цены приблизительные и не имеют единой даты/поставщика/количества;
- часть модулей задана placeholder footprint и не попадает в автоматическую котировку;
- `hardware/tscircuit/expansion.tsx` содержит бортовой SAM-M8Q примерно за `$12`, хотя legacy BOM объявляет GPS внешним;
- отсутствует канонический экспорт `refdes → MPN → supplier SKU → quantity → lifecycle → price tiers`.

До формирования такого экспорта legacy-итог используется только как грубая верхнеуровневая оценка.

## Первичный triage

| Область | Кандидат | Возможная экономия | Риск потери | Статус |
|---|---|---:|---|---|
| UI/I²C/STOP | `U14` → 3×3 matrix; STOP → независимый hardware TX-kill; audio-control → `U13` + освобождённые LoRa-линии `U12` | один PCA9555, развязка, часть pull-ups и placements; часть экономии поглотят STOP gates | ghosting/latency/power sequence; полный kill всех TX-path | исходный `IMP-0006` конфликтует с `DEC-0009`; `IMP-0010` сравнивается только после `INV-0002` freeze на полном demand model |
| GNSS | удалить legacy SAM-M8Q и реализовать M5 UART `PORT.C` | около `$12` и обвязка минус connector/power protection в base BOM | внешний Unit обязателен для GNSS | принято в `DEC-0006`; дельту подтвердить котировкой |
| LoRa + GNSS | внешний M5Stack Cap LoRa-1262 `U214` вместо E22 и отдельного GPS Unit в данной конфигурации | предварительно около `$4.45` на полном наборе плюс PCB/RF/assembly, минус Cap-Bus/protection/mechanics | U214 заявлен только на 868–923 MHz; обе функции зависят от одного Cap | основной профиль по `DEC-0008`; экономию подтвердить котировкой |
| Модульный LoRa | совместимый с U214 внешний `EXT-RF14` и опциональные radio backends | base device теряет E22/RF path; дополнительный модуль считается отдельно | connector/power/mechanics и firmware abstraction | транспорт принят в `DEC-0008`; E22 carrier не обязательна |
| Audio | ES8311 mono codec + два default-to-analog selector вместо stereo codec/внешнего модуля | IC subtotal около `$0.70` low-volume / `$0.43` tier 100 до passives/assembly | pin proof, analog levels, IDF regression, EMI/SNR | принято в `DEC-0009`; полная дельта требует proof |
| IR learning | dual `TSOP38238` + `TSMP95000` против single-learning или fixed-38 RX | вариант A добавляет receiver/GPIO/passives; B/C дешевле | B теряет robust range/noise, C теряет measured carrier | вариант A принят в `DEC-0018`; дополнительная стоимость принята, B/C не являются zero-loss |
| 3×nRF24, owner и hunt | exact identical qualified PA/LNA modules; S3 shared-SPI owner против C5+SDIO; calibrated RPD sector comparison; independent CE latch/direct CS/decoder после freeze | S3 сохраняет текущую routing side и preliminarily уменьшает reroute/raw-IPC NRE; hunt по `DEC-0019` не добавляет measurement BOM | общий SPI требует measured latency/loss; C5 требует SDIO и плотный pin budget; 1 radio+RF switch или общий неразделимый CE теряют функцию | **⚠️ `IMP-0021/A`** — только предварительный layout candidate до `INV-0002` freeze; число три и полный native feature set сохраняются; `AUD-0003` |
| ESP32-C5 module | legacy `ESP32-C5-WROOM-1U-N8R4`/`C49308183` → текущий стандартный `ESP32-C5-WROOM-1U-N8R8`/`C51950748` | предварительно не дороже рыночного legacy-кандидата и даёт 8 MB PSRAM вместо 4 MB; точную экономию покажет AVL quote | другая variant/PSRAM qualification, availability у конкретного assembler | source candidate исправлен; считать zero-loss только после pin/footprint/flash/PSRAM, supplier stock и RF HIL (`FND-0022`) |
| 802.15.4 stacks | использовать встроенный C5 radio: raw 802.15.4 и OpenThread; Zigbee только условным firmware backend | новый RF/BOM не нужен | shared 2.4 GHz radio, RAM/flash, coexistence и proprietary Zigbee core | принято в `DEC-0020`: OpenThread baseline, Zigbee optional conditional; dual-SoC radio был бы улучшением производительности, а не zero-loss экономией |
| Native BLE owner | один baseline owner на S3; C5 BLE default-off; только BLE-compatible subset nRF24 ограничен | новый BLE BOM и C5↔S3 BLE IPC не нужны; меньше power/coexistence/HIL cost | exact host stack, S3 Wi-Fi coexistence и cross-MCU RF arbitration требуют proof | принято `DEC-0021`: весь native BLE baseline и весь native nRF24 feature set сохраняются |
| BLE connection sniffer | не включать отдельный nRF52-class sniffer в base device | base BOM, площадь, питание и transport не растут | native S3/C5 не получают passive connection-follow capability | честная декомпозиция, не zero-loss BLE-функция: accessory/onboard вариант рассматривается отдельно в `IMP-0004` |
| USB | один разъём с аппаратным выбором S3/C5 | разъём, ESD/CC и отверстие корпуса минус mux/selector | потеря recovery при отказе MCU | исследовать; не предлагать без fail-safe proof |
| Закупка | verified AVL и эквивалентные second sources | зависит от серии | скрытая деградация/контрафакт | обязательно на этапе 4 |
| Производство | унификация пассивов, сокращение уникальных позиций и по возможности одна сторона SMT | feeder/setup/assembly cost | площадь и RF-разводка | считать по реальной котировке, не форсировать |

## Что сейчас не считается экономией без потерь

- уменьшение числа трёх nRF24 или иных уже принятых радиотрактов;
- объединение антенн без доказательства одновременности, isolation и insertion loss;
- удаление аппаратных TX-live LED, физического STOP или recovery-path;
- дешёвые неизвестные RF-модули без входного контроля и сравнительных измерений;
- перенос встроенной функции во внешний аксессуар без явного решения по продукту.

## Пересечение UI, audio и аппаратного STOP

После принятия `DEC-0009` исходный `IMP-0006` дважды назначает `U13.P10..P17`: восемь линий нужны matrix+STOP+touch, ещё три — codec/selectors. Это зафиксировано как `FND-0006`, поэтому прежняя оценка удаления `U14` больше не считается достижимой.

`IMP-0010` предлагает вынести STOP из I²C в обязательный аппаратный TX-kill и удалить `U14` только после доказательства matrix/recovery/IRQ map. `FND-0032` исправляет старый расчёт: U214 сохраняет reset, поэтому свободна только `U12.P12`; остальные controls размещаются на `U13` после физического C5 BOOT и touch-IRQ aggregation. Чистая экономия определяется только вместе со стоимостью fail-safe gates, IRQ buffer и HIL. Safety-цепь не является необязательной «надбавкой ради экономии»: `FND-0007` показывает, что текущий STOP не гасит TX без исправных S3/I²C/firmware.

## Следующие проверки

1. На этапе 3 проверить pin/power budget для принятого M5 UART-порта из `DEC-0006`.
2. После фиксации `REQ-*` построить воспроизводимый BOM и ценовые снимки `1 / 10 / 100 / 1000`.
3. Для каждого крупного стоимостного блока сравнить минимум два функционально эквивалентных варианта.
4. Отдельно получить PCB/PCBA и mechanical quotes; цена детали не равна полной экономии.
5. Принять только варианты, прошедшие equivalence tests из `DEC-0005`.
6. Для `DEC-0008` построить поканальную regional matrix U214; ярлык 868/915 не заменяет проверку окна 868–923 MHz и местных правил.
7. Сравнить котировки U214 и основной PCB с `EXT-RF14`; опциональные будущие carrier не включать в обязательный BOM.
8. Для C5 сравнивать current standard N8R8 с legacy N8R4 по полной landed/PCBA цене и доступности, не по одной случайной карточке магазина.
9. Для `DEC-0021` считать не только нулевой BLE radio BOM, но и flash/RAM, active current, coexistence и HIL matrix; наличие radio в обоих MCU не делает dual-owner бесплатным.
10. Для **⚠️ `IMP-0021`** сравнить полный landed BOM и NRE S3 shared-SPI+CE-latch против C5+SDIO, затем доказать worst-case three-radio FIFO/IRQ latency/loss; существующая routing side сама по себе не равна zero-loss.

## Принятая GNSS-дельта

На снимке 2026-08-15 бортовой SAM-M8Q стоит около `$11.99` без обвязки, а внешний M5Stack Unit GPS v1.1 — `$9.95`. Это уменьшает base BOM, но не доказывает такую же дельту полной комплектации: UART connector/protection остаются на плате, аксессуар поставляется отдельно, а официальный M5Stack store в момент проверки показывает out of stock.

## Кандидат на объединение LoRa + GNSS

`IMP-0007` предлагает подключаемый M5Stack Cap LoRa-1262 `U214`, который объединяет SX1262, GNSS AT6668 и LoRa-антенну за `$14.50`. Против legacy-оценки `$9` за E22 с антенной и `$9.95` за отдельный GPS Unit грубая экономия полного набора равна `$4.45` до connector/protection/mechanics. `DEC-0008` принимает U214 в его окне `868–923 MHz`; полный legacy-диапазон E22 не является требованием. U214 всё ещё требует измерений и котировки.

`IMP-0008` сохраняет расширяемость: тот же внешний слот сможет принимать отдельно проверенные будущие модули. `DEC-0008` не включает E22 carrier в обязательную разработку, BOM или условие экономии без потерь.

## Кандидат цифрового audio-path

`REV-0002E` сравнил current analog path, внутренние ADC/sigma-delta S3, три класса codec и внешний M5Stack Audio Module. Legacy scope прямо задаёт mono, поэтому ES8311 восстанавливает все перечисленные audio-пререквизиты без оплаты незапрошенного stereo.

Ценовой снимок `IMP-0009`: ES8311 `C962342` — `$0.5547` при 1 шт. и `$0.3059` на tier 100; два TI analog selector — примерно `$0.0748`/шт. low-volume и `$0.0625`/шт. на tier 100. `DEC-0009` принимает эту архитектуру. Это только IC subtotal: zero-loss статус по-прежнему зависит от hardware bypass, pin proof, уровней SA868, измерений audio quality и полной PCBA-котировки.
