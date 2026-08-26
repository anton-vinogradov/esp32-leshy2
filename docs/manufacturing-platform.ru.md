# Производственная платформа Leshy2

[English](manufacturing-platform.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

## Базовая линия

**Рабочий reference — JLCPCB Standard PCBA.** Это не эксклюзивная привязка и не разрешение заказа. Standard выбран из-за публичной assembly-библиотеки со stock/JLC-number, двухстороннего SMT+THT, fine-pitch/BGA/QFN, специального stack-up и SPI/AOI/X-ray. [Официальные capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) и [варианты sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction).

PCBWay остаётся fallback для ручного turnkey/box-build quote, Seeed Fusion — второй производственный quote. Их supplier availability хуже подходит как автоматически проверяемый источник выбора MPN.

```mermaid
flowchart TD
  M["Новый MPN"] --> PУстанавливается при PCBA?
  P -->|да| J0["J0 · exact JLC stock"]
  J0 -->|нет| J1["J1 · квалифицированная замена"]
  J1 -->|нет без деградации| J2["J2 · private pre-order"]
  J2 -->|нет| J3["J3 · global/consign"]
  P -->|нет; ставит фабрика| J4F["J4-F · factory final assembly"]
  P -->|нет; в комплект отдельно| J4P["J4-P · factory-packed"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  F --> R["повторная stock-проверка перед заказом"]
```

## Что значит «доступно всегда»

Ни одна площадка не гарантирует вечный публичный остаток. Для Leshy2 это означает: обычные детали выбираются из JLC stock или имеют заранее квалифицированные замены; уникальные функциональные MPN резервируются в private library через [pre-order](https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb) или поступают через global sourcing/consignment. Недостаток stock никогда не разрешает фабрике молчаливую замену.

## Контрольный BOM Tool прогон

Контрольный BOM Tool capture относится к прежним 209 строкам: 176 matched, 33 unmatched и 1019 установок. Текущий BOM отличается от него только заменой `SA518` на exact `SA818S-U` + `SA818S-V`: 208 неизменившихся identity присоединены по MPN, а два новых модуля — по точным страницам `C3001549` и `C51897911`. Так получена проверяемая текущая карта `210` строк и `1052` установок без повторной передачи BOM. До применения сохранённых outlier-решений в ней 178 exact catalogue routes и 32 unresolved lines; семантических подмен MPN — ноль.

Сохранённый exact-поиск закрывает все 32 неизменившихся outlier без замены компонентов: 12 добавлены в `J0`, 4 — в `J2`, 11 сохраняют точный MPN через `J3`, 3 требуют фабричной финальной сборки `J4-F`, 2 комплектуются отдельно по `J4-P`. Вместе с новыми voice routes итог всей BOM: `J0=148`, `J1=0`, `J2=46`, `J3=11`, `J4-F=3`, `J4-P=2`; несопоставленных строк — ноль.

Показываемая в историческом BOM Tool capture сумма `$1255.6365` относится только к прежним 176 найденным строкам и **не** является текущей полной ценой сборки, quote или заказом. Актуальная минимальная корзина evidence отдельно посчитана на [странице образцов](component-sample-basket.ru.md).

<details>
<summary>Как разрешены 32 неизменившихся outlier</summary>

| Нормализованный MPN | Кол-во | Маршрут | Доказательство |
|---|---:|---:|---|
| `1227-J` | 1 | `J4-F` | encoder knob requires factory installation and control test after enclosure integration |
| `E01-ML01IPX` | 3 | `J3` | three exact full-power nRF24 modules are externally orderable and must be consigned or globally sourced |
| `ESP32-C5-WROOM-1U-N8R8` | 1 | `J2` | `C51950748` · stock 0 |
| `RFPC-SMA31-FN-175-A` | 8 | `J3` | exact board SMA is orderable outside the public JLC library |
| `RFPC-SMA32-FN-175-A` | 2 | `J3` | exact board RP-SMA is orderable outside the public JLC library |
| `FX8C-80S-SV5(92)` | 1 | `J3` | exact inter-board receptacle is orderable outside the public JLC library |
| `BGS13SN8E6327XTSA1` | 2 | `J2` | `C55118249` · stock 0 |
| `U214 Cap LoRa-1262` | 1 | `J4-P` | removable rear Cap accessory is factory-tested, then packed separately for user installation |
| `GJM1555C1H101JB01D` | 2 | `J3` | retain exact RF capacitor until an RF-equivalent alternate is separately qualified |
| `PESD24VY1BSF` | 2 | `J3` | retain exact low-capacitance RF ESD identity until an RF-equivalent alternate is separately qualified |
| `AS02404PO` | 1 | `J3` | exact board speaker is orderable outside the public JLC library and needs manual/THT assembly acceptance |
| `HMX035CTFT-001` | 1 | `J4-F` | display/flex requires factory mating and display/touch functional test during final assembly |
| `SC1512-A4` | 1 | `J2` | `C52763783` · stock 0 |
| `1125R-SMT-4P` | 1 | `J3` | exact Seeed SMT Unit connector is orderable outside the public JLC library |
| `2118651-2` | 5 | `J4-F` | five removable 30-mm microcoax jumpers require factory installation, strain routing and continuity test during final sandwich assembly |
| `MSPM0C1106SDGS20R` | 2 | `J0` | `C52995805` · stock 34 |
| `SN74LVC1G07DCKR` | 10 | `J0` | `C7830` · stock 31027 |
| `SN74LVC1G08DCKR` | 4 | `J0` | `C7832` · stock 179787 |
| `SN74LVC1G17DCKR` | 1 | `J0` | `C10425` · stock 59402 |
| `TCA9539PWR` | 1 | `J0` | `C131972` · stock 8380 |
| `TLV1821DCKR` | 2 | `J3` | exact voice-evidence comparator must be sourced; no silent threshold/path alternate |
| `TLV1824PWR` | 2 | `J0` | `C35149428` · stock 9 |
| `TPD2EUSB30ADRTR` | 2 | `J0` | `C94934` · stock 5068 |
| `TPD4E05U06DQAR` | 13 | `J0` | `C138714` · stock 61819 |
| `TPUL2G223BQBR` | 1 | `J3` | exact safety timer must be sourced; no silent timing-function alternate |
| `B0310J50100AHF` | 1 | `J2` | `C5160223` · stock 0 |
| `TSMP95000TT` | 1 | `J3` | only a zero-stock generic JLC Assembly placeholder exists; exact Vishay identity must be sourced |
| `18650 4000mAh` | 2 | `J4-P` | protected cells are packed separately for user installation unless a compliant battery box-build and shipping route is later qualified |
| `RC0402FR-07100RL` | 7 | `J0` | `C106232` · stock 5003833 |
| `RC0402FR-071KL` | 12 | `J0` | `C106235` · stock 4396756 |
| `RC0402FR-0733RL` | 1 | `J0` | `C138002` · stock 5477653 |
| `RC0402FR-074K7L` | 1 | `J0` | `C105871` · stock 7353078 |

</details>

## Независимая проверка критических деталей

До bulk-прогона отдельно проверены `11` критических идентичностей. Их stock-снимки не заменяют текущий BOM Tool результат и не обещают постоянную доступность.

| MPN | JLC | Сейчас | Маршрут |
|---|---:|---|---|
| [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946) | `C3013946` | stock 14529 | `J0` · exact selected module is directly assembleable |
| [`ESP32-C5-WROOM-1U-N8R8-V1.2`](https://jlcpcb.com/partdetail/C54951858) | `C54951858` | stock 547 | `J0` · current explicit V1.2 stock matches the architecture revision floor; BOM spelling must be normalized before release |
| [`CC1101RGPR`](https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953) | `C29953` | stock 14194 | `J0` · exact selected transceiver is directly assembleable |
| [`ES8311`](https://jlcpcb.com/partdetail/1044199-ES8311/C962342) | `C962342` | stock 96905 | `J0` · exact selected codec is directly assembleable |
| [`MAX17320G20+ / selected order suffix +T`](https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894) | `C7457894` | stock 13 | `J0` · functional identity is present but packaging/order-suffix equivalence and low stock require confirmation or J2 reservation |
| [`SC1512-A4`](https://jlcpcb.com/partdetail/RaspberryPi-SC1512A4/C52763783) | `C52763783` | SMT; fixture; Economic and Standard | `J2` · listed and assembleable, but not public-stock; reserve by pre-order or consign exact parts |
| [`MSPM0C1106SDGS20R`](https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805) | `C52995805` | Extended SMT | `J2` · listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation |
| [`E01-ML01IPX`](https://jlcpcb.com/parts/componentSearch?searchTxt=E01-ML01IPX) | `—` | not found in public library | `J3` · retain exact module only through new-part/global-sourcing/consignment until a function-preserving stocked module is qualified |
| [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | `C3001549` | stock 68 | `J0` · exact selected UHF module is priced and in public stock |
| [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | `C51897911` | Standard PCBA pre-order | `J2` · exact selected VHF module is priced but stock-zero pre-order; lead time remains open |
| [`HMX035CTFT-001`](https://jlcpcb.com/parts/componentSearch?searchTxt=HMX035CTFT-001) | `—` | display/flex belongs to factory final assembly | `J4-F` · keep replaceable display-adapter architecture; require factory mating plus display/touch test rather than treating the display as an ordinary line-loaded SMT part |

## Граница сборки

JLCPCB Standard PCBA собирает обе платы и принятые SMT/THT-компоненты. Это ещё не подтверждает финальную сборку устройства.

| Маршрут | Обязательная операция | Статус |
|---|---|---|
| `J4-F` | Фабрика стыкует и проверяет дисплей/flex, устанавливает и фиксирует пять microcoax, ставит ручку энкодера, собирает корпус/«бутерброд» и выполняет whole-device test | 🔒 Открыто до письменного подтверждения capability и отдельной цены box-build; без этого H5 и H7 не закрываются |
| `J4-P` | Фабрика проверяет совместимость U214, затем кладёт его отдельно; внешние антенны кладутся комплектом; защищённые 18650 кладутся отдельно для установки пользователем, если не подтверждён безопасный battery box-build и shipping | 🔒 Открыто до kit/packing/shipping quote |

`J4-F` и `J4-P` не означают, что операции уже приняты JLCPCB. Они фиксируют требуемый результат для выбранной фабрики или fallback box-build подрядчика.

## Два точных voice-маршрута

`SA818S-U` связан с exact `C3001549`: stock 68, available quantity 60, цена одного `$9.7347`. `SA818S-V` связан с exact `C51897911`: stock 0, MOQ 1, цена одного `$10.0710`, маршрут `J2` pre-order. `SA818S-CE C19632390` остаётся только qualified-pending UHF-заменой и не входит в production BOM: она требует HIL и firmware clamp 470 МГц, не заменяет VHF и никогда не подставляется молча.

## Текущий результат

- JLCPCB Standard PCBA принят как рабочий reference без lock-in.
- Все `210` строк имеют определённый маршрут `J0`–`J3`, `J4-F` или `J4-P`; функциональных замен нет.
- Все component prices минимальной evidence-корзины известны. Запрос JLCPCB без заказа успешно отправлен 26 августа 2026 года; H5.0.3-R1 теперь ожидает точный срок/условия pre-order `SA818S-V`, подтверждение/цену `J4-F` box-build и условия `J4-P` kit/packing/shipping. Закупка образцов остаётся отдельным последующим решением.
- Заявка JLCAPI одобрена, приложение `ESP32-Leshy2 BOM Validator` создано, ключ подписи хранится только локально вне Git. Портал теперь показывает право Parts как `Rejected`, но причины в журнале нет, поэтому API-вызовы по-прежнему невозможны. PCB/3D также отклонены, SMT Stencil и JLC Balance выключены. Активным остаётся ручной путь через каталог и BOM.
- Прежний 209-строчный BOM upload был передан и обработан; текущий 210-строчный файл сгенерирован локально, но не передавался, потому что 208 identity неизменны, а обе новые exact-страницы проверены отдельно. Quote, sourcing request, reservation, покупка, замены, KiCad layout и fabrication не выполнялись и не разрешены. Сырые API-ответы публично не распространяются.

Машинные результаты: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json) и [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json). [Требования JLCPCB к BOM](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly).
