# Производственная платформа Leshy2

[English](manufacturing-platform.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

## Базовая линия

**Рабочий reference — JLCPCB Standard PCBA.** Это не эксклюзивная привязка и не разрешение заказа. Standard выбран из-за публичной assembly-библиотеки со stock/JLC-number, двухстороннего SMT+THT, fine-pitch/BGA/QFN, специального stack-up и SPI/AOI/X-ray. [Официальные capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) и [варианты sourcing](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction).

Целевой заказ — ровно **один полностью собранный прототип**, без аккумуляторов. Фабрика не выбирает схемные или механические решения: production package заранее фиксирует exact panel, его mating, все компоненты и последовательность сборки. Первый полноценный power-on и USB bring-up выполняет владелец.

JLCPCB остаётся PCBA-only reference: он подтвердил exact dual-designator placement и no-silent-substitution, но прямо отказался от полной сборки корпуса/устройства и рассматривает специальные клей/FPC/microcoax-процессы только после заказа. PCBWay поэтому стал активным кандидатом полного устройства: его официальные страницы подтверждают [turnkey/combo/consigned PCBA и тестирование](https://www.pcbway.com/assembly-capabilities.html), а также [OEM final assembly](https://www.pcbway.com/oem.html). [Информационный exact-one запрос](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) отправлен 2 сентября с `vinogradov.anton@gmail.com` на `service@pcbway.com`; письменное принятие Leshy2 и цены ещё ожидаются. Отправка не создала quote, sourcing request, reservation, purchase или order. Seeed Fusion подтверждён только как второй источник PCBA.

```mermaid
flowchart TD
  M["Новый MPN"] --> PУстанавливается при PCBA?
  P -->|да| J0["J0 · exact JLC stock"]
  J0 -->|нет| J1["J1 · квалифицированная замена"]
  J1 -->|нет без деградации| J2["J2 · private pre-order"]
  J2 -->|нет| J3["J3 · global/consign"]
  P -->|нет; ставит фабрика| J4F["J4-F · factory final assembly"]
  P -->|нет; в комплект отдельно| J4P["J4-P · factory-packed"]
  P -->|не входит в поставку| J5U["J5-U · user-supplied"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  J5U --> F
  F --> R["повторная stock-проверка перед заказом"]
```

## Что значит «доступно всегда»

Ни одна площадка не гарантирует вечный публичный остаток. Для Leshy2 это означает: обычные детали выбираются из JLC stock или имеют заранее квалифицированные замены; уникальные функциональные MPN резервируются в private library через [pre-order](https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb) или поступают через global sourcing/consignment. Недостаток stock никогда не разрешает фабрике молчаливую замену.

## Контрольный BOM Tool прогон

Контрольный BOM Tool capture относится к прежним 209 строкам: 176 matched, 33 unmatched и 1019 установок. Текущий BOM заменяет `SA518` двумя exact voice-модулями, legacy-дисплей — точным EastRising endpoint, а прежний 0-dBm nRF24 — складским full-power `E01-ML01SP4`. Так получена проверяемая текущая карта `210` строк и `1050` установок без повторной передачи BOM. До применения сохранённых outlier-решений в ней 182 exact catalogue route и 28 unresolved lines; семантических подмен MPN — ноль.

Сохранённый exact-поиск закрывает все 28 оставшихся outlier без замены компонентов: 11 добавлены в `J0`, 2 — в `J2`, 10 сохраняют точный MPN через `J3`, 3 требуют фабричной финальной сборки `J4-F`, U214 идёт через `J4-P`, а аккумуляторы — через `J5-U` вне поставки. Точный EastRising-дисплей уже входит отдельным прямым маршрутом `J4-F`. Итог всей BOM: `J0=165`, `J1=0`, `J2=29`, `J3=10`, `J4-F=4`, `J4-P=1`, `J5-U=1`; несопоставленных строк — ноль.

Показываемая в историческом BOM Tool capture сумма `$1255.6365` относится только к прежним 176 найденным строкам и **не** является текущей полной ценой сборки, quote или заказом. Актуальный order-integrated article manifest единственного прототипа посчитан на [странице manifest](component-sample-basket.ru.md); отдельной закупки образцов/coupons нет.

<details>
<summary>Как разрешены 28 оставшихся outlier</summary>

| Нормализованный MPN | Кол-во | Маршрут | Доказательство |
|---|---:|---:|---|
| `1227-J` | 1 | `J4-F` | encoder knob requires deterministic factory installation after enclosure integration; full control bring-up is performed by the owner |
| `RFPC-SMA31-FN-175-A` | 8 | `J3` | exact board SMA is orderable outside the public JLC library |
| `RFPC-SMA32-FN-175-A` | 2 | `J3` | exact board RP-SMA is orderable outside the public JLC library |
| `FX8C-80S-SV5(92)` | 1 | `J3` | exact inter-board receptacle is orderable outside the public JLC library |
| `BGS13SN8E6327XTSA1` | 2 | `J2` | `C55118249` · stock 0 |
| `U214 Cap LoRa-1262` | 1 | `J4-P` | removable rear Cap accessory is packed separately for user installation; factory compatibility FCT is not mandatory |
| `GJM1555C1H101JB01D` | 2 | `J3` | retain exact RF capacitor until an RF-equivalent alternate is separately qualified |
| `PESD24VY1BSF` | 2 | `J3` | retain exact low-capacitance RF ESD identity until an RF-equivalent alternate is separately qualified |
| `AS02404PO` | 1 | `J3` | exact board speaker is orderable outside the public JLC library and needs manual/THT assembly acceptance |
| `1125R-SMT-4P` | 1 | `J3` | exact Seeed SMT Unit connector is orderable outside the public JLC library |
| `1-2118651-0` | 3 | `J4-F` | three removable 60-mm nRF microcoax jumpers require deterministic factory installation and strain routing during final sandwich assembly; full power-on is owner bring-up |
| `2118651-2` | 2 | `J4-F` | two removable 30-mm S3/C5 microcoax jumpers require deterministic factory installation and strain routing during final sandwich assembly; full power-on is owner bring-up |
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
| `18650 4000mAh` | 2 | `J5-U` | accumulator cells are not part of device delivery; the user separately supplies and installs compatible protected cells |
| `RC0402FR-07100RL` | 7 | `J0` | `C106232` · stock 5003833 |
| `RC0402FR-071KL` | 12 | `J0` | `C106235` · stock 4396756 |
| `RC0402FR-0733RL` | 1 | `J0` | `C138002` · stock 5477653 |
| `RC0402FR-074K7L` | 1 | `J0` | `C105871` · stock 7353078 |

</details>

## Независимая проверка критических деталей

До bulk-прогона отдельно проверены `22` критических идентичностей. Их stock-снимки не заменяют текущий BOM Tool результат и не обещают постоянную доступность.

| MPN | JLC | Сейчас | Маршрут |
|---|---:|---|---|
| [`RS-06L2R70FT`](https://jlcpcb.com/partdetail/304147-RS06L2R70FT/C323265) | `C323265` | stock 3617 | `J0` · exact 2.7-Ohm +/-1% 250-mW 1206 backlight resistor removes the uncontrolled zero-Ohm cathode path while retaining useful first-prototype brightness |
| [`FSUSB42MUX`](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355) | `C11355` | stock 66698 | `J0` · live 2026-08-30 public-stock route for the exact onsemi MSOP-10; selected without package or pin-topology change |
| [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946) | `C3013946` | stock 14529 | `J0` · exact selected module is directly assembleable |
| [`ESP32-C5-WROOM-1U-N8R8`](https://jlcpcb.com/partdetail/C54951858) | `C54951858` | stock 460 | `J0` · official Espressif MPN remains unsuffixed; the supplier code fixes the production route at V1.2 and incoming MD plus eFuse must independently prove revision >=v1.2 |
| [`CC1101RGPR`](https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953) | `C29953` | stock 14194 | `J0` · exact selected transceiver is directly assembleable |
| [`ES8311`](https://jlcpcb.com/partdetail/1044199-ES8311/C962342) | `C962342` | stock 96905 | `J0` · exact selected codec is directly assembleable |
| [`74LVC2G126DP,125`](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392) | `C503392` | stock 155 | `J0` · exact selected TSSOP package variant is in public stock; same official family, pin map, logic, Ioff and timing as the former DC package |
| [`74LVC2G14GV,125`](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708) | `C426708` | stock 153 | `J0` · exact selected TSOP package variant has ten-part trial coverage; same official family, pin map, Schmitt thresholds, Ioff and timing as the former GW package |
| [`MAX17320G20+T`](https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894) | `C7457895` | Extended SMT pre-order | `J2` · the exact selected +T order suffix remains on the pre-order route; the stocked C7457894 card names MAX17320G20+ without proving suffix equivalence, so it is not silently accepted |
| [`SC1512-A4`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | `C39843328` | stock 3442 | `J0` · live original-manufacturer route; canPresale 3442 is the authoritative assembly availability, displayed stock is 3605, and received A4 marking remains an incoming gate |
| [`MSPM0C1106SDGS20R`](https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805) | `C52995805` | Extended SMT | `J2` · listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation |
| [`E01-ML01SP4`](https://jlcpcb.com/partdetail/E01-ML01SP4/C97340) | `C97340` | stock 405 | `J0` · exact Chengdu Ebyte PA/LNA module is directly factory-placeable; 20-dBm and ten-land footprint replace the incorrect 0-dBm E01-ML01IPX baseline |
| [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | `C3001549` | stock 68 | `J0` · exact selected UHF module is priced and in public stock |
| [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | `C51897911` | Standard PCBA pre-order | `J2` · exact selected VHF module is priced but stock-zero pre-order; lead time remains open |
| [`ER-TFT035IPS-6 + ER-TPC035-6 option 5344`](https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen) | `—` | stock manufacturer in stock | `J4-F` · exact configured panel, drawings, 50-contact tail, ILI9488/FT6236 endpoint and price are fixed; written assembler acceptance remains only for adhesive/FPC/final mating |
| [`FH34SRJ-50S-0.5SH(50)`](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104) | `C3169104` | stock 2679 | `J0` · exact selected 50-position panel connector is directly placeable; quantity-one price USD 0.5832 |
| [`0402WGF1603TCE`](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757) | `C25757` | stock 388017 | `J0` · exact stocked 160-kOhm 0402 replacement preserves the complete audio-attenuator electrical contract and uses a thinner body |
| [`RS-06K47R0FT`](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014) | `C140014` | stock 78058 | `J0` · exact stocked 47-Ohm 1206 replacement preserves the IR current-limit power, voltage and temperature contract |
| [`CC0603KRX7R0BB104`](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803) | `C113803` | stock 1027658 | `J0` · exact stocked 100-nF 100-V 0603 body; X7R temperature stability is stricter than the replaced X7S class |
| [`CSD87313DMS`](https://jlcpcb.com/partdetail/x/C2863848) | `C2863848` | stock 4813 | `J0` · same production die, WSON-CLIP body, contacts and electrical contract as DMST; DMS changes tape-and-reel quantity only |
| [`TSOP75238TR`](https://jlcpcb.com/partdetail/x/C511498) | `C511498` | stock 17 | `J0` · same final body, contacts and electrical contract as TT; TR changes tape presentation, so approve CPL rotation/feeder orientation and recheck complete-job stock before order |
| [`LQW15AN56NG00D`](https://jlcpcb.com/partdetail/x/C167482) | `C167482` | stock 21558 | `J0` · exact 56-nH LQW15AN 0402 body; G tightens inductance tolerance from +/-5% to +/-2% without degrading RF limits |

## Граница сборки

JLCPCB Standard PCBA собирает обе платы и принятые SMT/THT-компоненты; exact dual-SA818S placement и запрет молчаливой замены подтверждены. Однако PCBA MOQ равен 2, клей/FPC/microcoax оцениваются только после заказа, а complete enclosure/final-device assembly не поддерживается. Поэтому точный `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 и его `FH34SRJ-50S-0.5SH(50)` сохраняются, но полное J4-F принятие до заказа теперь требуется от PCBWay. Function Test остаётся optional quote-insurance, а не gate.

| Маршрут | Обязательная операция | Статус |
|---|---|---|
| `J4-F` | Фабрика по release package устанавливает и стыкует exact `ER-TFT035IPS-6 + ER-TPC035-6` через `C3169104`, фиксирует две 30-мм и три 60-мм microcoax, ставит ручку энкодера и собирает корпус/«бутерброд» без инженерных догадок | ❌ JLCPCB отказался от complete enclosure assembly и не подтверждает special process до заказа; 🔒 ожидается письменный exact-one ответ PCBWay |
| `J4-P` | U214 и внешние антенны остаются съёмными аксессуарами, которые владелец приобретает и устанавливает после доставки | ✅ Необязательная упаковка фабрикой не является release gate |
| `J5-U` | Пользователь отдельно приобретает и устанавливает совместимые защищённые 18650 | ✅ Принятая граница продукта: аккумуляторы не входят в поставку устройства |

`J4-F` фиксирует обязательный результат для выбранной фабрики или fallback box-build подрядчика. `J4-P` сохраняется только как классификация съёмных аксессуаров и не требует принятия фабрикой для release.

## Два точных voice-маршрута

`SA818S-U` связан с exact `C3001549`: stock 68, available quantity 60, цена одного `$9.7347`. `SA818S-V` связан с exact `C51897911`: stock 0, MOQ 1, цена одного `$10.0710`, маршрут `J2` pre-order. `SA818S-CE C19632390` остаётся только qualified-pending UHF-заменой и не входит в production BOM: она требует HIL и firmware clamp 470 МГц, не заменяет VHF и никогда не подставляется молча.

## C5: MPN, поставщик и ревизия

Официальный MPN остаётся `ESP32-C5-WROOM-1U-N8R8`. Суффикс есть только в supplier order code `ESP32-C5-WROOM-1U-N8R8-V1.2`: активный маршрут — Espressif `C54951858`, Standard PCBA, stock 460, available 440, MOQ 1. Прежний `C51950748` запрещён как active route. Для production одновременно обязательны MD/lot identity и eFuse readback `>=v1.2`; `v1.0` допускается только как явно помеченный engineering specimen, `v0.1`, unknown и любое расхождение изолируются.

## Текущий результат

- JLCPCB Standard PCBA сохранён как PCBA-only reference без lock-in; full-device роль отклонена самим JLCPCB.
- Все `210` строк имеют определённый маршрут `J0`–`J3`, `J4-F`, `J4-P` или `J5-U`; функциональных замен нет.
- [Ответ JLCPCB от 2 сентября](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-09-02.md) подтверждает exact `SA818S-V C51897911` и `SA818S-U C3001549` на разных designator через BOM Matching, exact-MPN incoming control и запрет замены без подтверждения. Он одновременно задаёт PCBA MOQ 2, откладывает решение по клею/FPC/microcoax до post-order engineering review и прямо отказывает в complete enclosure/final-device assembly. Письмо пришло в исходный тикет на `av@apache.org` и отображается в Gmail-аккаунте `no.mail.in@gmail.com`; это объясняет видимую адресную путаницу. [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) фиксирует explicit required decline; JLCPCB full-device gate не пройден.
- Заявка JLCAPI одобрена, приложение `ESP32-Leshy2 BOM Validator` создано, ключ подписи хранится только локально вне Git, но право Parts остаётся `Rejected`. [Поддержка ответила](../hardware/procurement/H5.0.3-R1-parts-api-support-inquiry.md), что аккаунт новый и не имеет истории заказов, поэтому устойчивую business need пока не удалось подтвердить; повторная заявка возможна после появления истории либо с расширенным business case/integration plan. Автор ответа отдельно указал, что не входит в API review team, и точный порог заказов не назван. Повторная заявка не отправлена: до фактического одобрения API-вызовы невозможны, а активным авторитетным путём остаются ручные карточки каталога и BOM. PCB/3D также отклонены, SMT Stencil и JLC Balance выключены.
- [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json) переводит PCBWay из резерва в активного кандидата полной сборки; Seeed остаётся вторым источником PCBA. [No-order запрос PCBWay](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) отправлен 2 сентября; ожидается письменный line-by-line ответ. Никаких коммерческих действий запрос не создал.
- Прежний 209-строчный BOM upload был передан и обработан; текущий 210-строчный direct-ZIF файл сгенерирован локально, но не передавался. Оба устаревших DF40 удалены; актуальный C5 route и новый внешний 60-мм microcoax проверены отдельно. Quote, sourcing request, reservation, покупка, замены, KiCad layout и fabrication не выполнялись и не разрешены. Сырые API-ответы публично не распространяются.

Машинные результаты: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json), [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json) и [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json). [Требования JLCPCB к BOM](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly).
