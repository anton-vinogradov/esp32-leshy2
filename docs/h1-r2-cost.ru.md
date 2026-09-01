# H1-R2.38 · стоимость компонентов

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

Это ранжированный снимок текущего железа, а не коммерческое предложение. Цена строки учитывает установленное количество в целевом одном полностью собранном прототипе. Одинаковые MPN объединены в одну группу; исторический BOM Tool capture пяти плат сохранён ниже только как MOQ/pre-order evidence, а не план заказа.

## Сводка

- Серийная материальная база: **$252.10** на устройство; цены известны для `201/210` строк.
- Достижимый плановый минимум: **$271.90** на устройство; ещё `5` базовых строк не оценены.
- Текущий плановый компонентный минимум без обязательных post-PCBA активных модулей: **$271.90** на устройство и **$271.90** на один целевой прототип до стоимости плат, сборки, корпуса, антенн, доставки, налогов, брака и теста.
- Та же принятая ценовая база для десяти устройств: **$2,719.03**. Это линейное сравнение групп, а не обещание цены партии.
- Верхние 10 / 20 / 40 групп дают **40.38% / 57.78% / 76.49%** текущей известной базовой BOM.
- Исторический JLCPCB capture на пять плат: **$1,365.05** по `182` строкам; `24` live-проверок дают **$1,406.44**, ещё `28` строк не входят; это evidence, а не целевой quantity.
- Внешний антенный комплект вынесен отдельно: уже известно **$138.32**, ещё `4` позиции в `2` MPN-группах не оценены. Вместе с известной электронной BOM это уже **$410.22** до PCB/PCBA, корпуса и доставки.

## Принятая ценовая граница all-in-one

- Текущий продукт остаётся полностью начинённым all-in-one. Цель повторяемого готового устройства: **$220.00–$260.00** без аккумуляторов и полного набора специализированных внешних антенн.
- Чтобы внутри этой цены остались PCB, PCBA и корпус, электроника должна попасть примерно в **$189.00–$216.00**.
- Сейчас базовая BOM содержит `208` MPN-групп и `1094` установленных компонентов. Принятые без потери функции маршруты AD8314 и Hirose U.FL уже экономят **$10.42** и оставляют текущий точный planning floor **$271.90**. Дешёвая пара SMA/RP-SMA проверена и отклонена, поэтому её предполагаемая экономия сюда не входит.
- После них до целевой электронной BOM нужно убрать ещё **$55.90–$82.90**. Формальный запас до потолка готового устройства — только **$-11.90**, поэтому без дальнейшего пересинтеза в него не помещаются платы, сборка и корпус.

**Принято:** отдельный `Core` сейчас не проектируется. Сначала строится и проверяется один полностью оснащённый `R2-EVT1`; стоимость снижается пересинтезом реализации без удаления встроенных функций и safety-результата. Историческая цель `$150` отложена как возможная community-комплектация после работающего EVT1, а не является текущей аппаратной веткой. Первый единственный заказ всё равно будет дороже из-за MOQ, setup, ручной установки, доставки и налогов.

### Почему ESP32-DIV заметно дешевле

Официальная [архитектура ESP32-DIV v2](https://github.com/cifertech/ESP32-DIV/tree/9d4d82fe7a12febf554b12e1eca6d434ebe79d39) существенно меньше: один S3, три nRF24, один CC1101, IR и простой слой разъёмов/пассивов. В его публичной shield BOM нет двух voice-модулей, Airband-конвертера, двух RP-доменов, трёх независимых service USB, автономной pack-safety, физического контроля фактического TX и десяти отдельно квалифицированных RF-портов. Розничная серия также амортизирует setup и закупочные минимумы, тогда как наш текущий расчёт должен выдержать единственный первый заказ.

Это не означает, что Леший обязан стоить в восемь раз дороже. Это означает, что мы дорого реализовали не только функции, но и лабораторную наблюдаемость, независимое восстановление и отказоустойчивость каждого тракта.

### Насколько реалистична цель без потери результата

| Граница | Электроника | Готовая база | Честный вывод |
|---|---:|---:|---|
| Текущая схема | $271.90 | больше $271.90 | уже выше принятого потолка без плат, сборки и корпуса |
| После уже принятых AD8314 и Hirose U.FL изменений | $271.90 | больше $271.90 | точный текущий planning floor; всё ещё недостаточно |
| Те же встроенные пользовательские функции и тот же safety-результат после полного cost-resynthesis | $214.00–$235.00 | $241.00–$280.00 | с целью `$220–260` пересекается только верхняя часть |
| Модульная community-база; специализированные тракты ставятся Cap/Unit по задаче | $108.00–$125.00 | $135.00–$165.00 | отложена до работающего `R2-EVT1`; отдельного Core сейчас нет |

Диапазоны `$214–235` и `$241–280` — не обещание цены: они предполагают успешный пересинтез оставшихся RF-evidence, audio/safety и внутренних RF-трактов без изменения результата. Кнопки, держатель и recovery-разъёмы уже проверены и сохранены, поэтому прежняя ожидаемая экономия на них удалена. Нижняя часть цели `$220–260` пока не доказана.

Полный антенный комплект — аксессуар, а не скрытая часть цены устройства. Универсальная RX-антенна не заменяет согласованные TX-антенны; базовый комплект и дополнительные диапазонные антенны должны оцениваться отдельно.

Главный рейтинг ниже показывает **только один прототип**. В нём нет исторической цены пяти плат и нет умножения ×10.

## Единый топ-20: электроника и внешние антенны

| № | Источник | MPN и роль | Шт. ×1 | Цена 1 шт. по принятой базе | Группа ×1 | Доля известной суммы |
|---:|---|---|---:|---:|---:|---:|
| 1 | Антенна | `SMA-W100RX2`<br><sub>receive-only telescopic whip; AIR</sub> | 1 | $35.95 | $35.95 | 8.76% |
| 2 | Антенна | `001-0012`<br><sub>2.4/5 GHz native radio; S3, C5</sub> | 2 | $16.91 | $33.82 | 8.24% |
| 3 | Антенна | `AN0155H13`<br><sub>VHF 136-174 MHz; VHF</sub> | 1 | $31.70 | $31.70 | 7.73% |
| 4 | Антенна | `ANT-433-CW-QW-SMA`<br><sub>433 MHz / UHF 400-470 MHz; S433, UHF</sub> | 2 | $11.23 | $22.46 | 5.47% |
| 5 | Основная BOM | `GCT RFPC-SMA31-FN-175-A`<br><sub>eight standard outward SMA / восемь внешних SMA</sub> | 8 | $2.46 | $19.72 | 4.81% |
| 6 | Основная BOM | `EastRising ER-TFT035IPS-6 + ER-TPC035-6`<br><sub>display</sub> | 1 | $14.91 | $14.91 | 3.63% |
| 7 | Основная BOM | `Analog Devices AD8314ARMZ-REEL`<br><sub>six real-TX RF detectors / шесть RF-детекторов фактической передачи</sub> | 6 | $1.94 | $11.64 | 2.84% |
| 8 | Основная BOM | `OMRON B3S-1100P`<br><sub>sixteen ordinary user keys / шестнадцать обычных клавиш</sub> | 16 | $0.64 | $10.25 | 2.50% |
| 9 | Основная BOM | `G-NiceRF SA818S-V`<br><sub>VHF voice transceiver / VHF голосовой трансивер</sub> | 1 | $10.07 | $10.07 | 2.46% |
| 10 | Основная BOM | `G-NiceRF SA818S-U`<br><sub>UHF voice transceiver / UHF голосовой трансивер</sub> | 1 | $9.73 | $9.73 | 2.37% |
| 11 | Антенна | `ANT-315-CW-HW-SMA`<br><sub>315 MHz; S315</sub> | 1 | $9.60 | $9.60 | 2.34% |
| 12 | Основная BOM | `Ebyte E01-ML01SP4`<br><sub>three 20-dBm PA/LNA full-function nRF24 radios / три полнофункциональных nRF24 с PA/LNA 20 dBm</sub> | 3 | $2.96 | $8.89 | 2.17% |
| 13 | Основная BOM | `Keystone Electronics 1048P`<br><sub>dual protected-18650 holder / держатель двух защищённых 18650</sub> | 1 | $8.57 | $8.57 | 2.09% |
| 14 | Основная BOM | `Texas Instruments TMUX1136DGSR`<br><sub>four complete audio/control selectors / четыре полных audio/control selector</sub> | 4 | $2.06 | $8.23 | 2.01% |
| 15 | Основная BOM | `LTC5532ES6#TRMPBF`<br><sub>S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц</sub> | 2 | $3.89 | $7.78 | 1.90% |
| 16 | Основная BOM | `Samtec FTSH-105-01-L-DV-K-P-TR`<br><sub>four internal recovery headers / четыре внутренних recovery-разъёма</sub> | 4 | $1.70 | $6.80 | 1.66% |
| 17 | Основная BOM | `TE Connectivity 1-2118651-0`<br><sub>three 60-mm nRF RF jumpers / три 60-мм RF-кабеля nRF</sub> | 3 | $1.81 | $5.43 | 1.32% |
| 18 | Основная BOM | `ESP32-S3-WROOM-1U-N16R8`<br><sub>s3</sub> | 1 | $5.11 | $5.11 | 1.25% |
| 19 | Основная BOM | `GCT RFPC-SMA32-FN-175-A`<br><sub>two native-radio RP-SMA / два RP-SMA native-радио</sub> | 2 | $2.46 | $4.93 | 1.20% |
| 20 | Антенна | `TI.08.C.0112`<br><sub>868/915 MHz; S915</sub> | 1 | $4.79 | $4.79 | 1.17% |

[Единый топ-20 — CSV](../hardware/product-design/generated/H1-R2-cost-top20.csv) · [Полный рейтинг 210 строк — CSV](../hardware/product-design/generated/H1-R2-cost-ranked.csv)

## Критический аудит массового рынка для всего топ-20

Проверены все 20 текущих групп, и **все 20 сохранены**. Шесть более дешёвых антенных кандидатов отклонены решением от `2026-08-30`: их суммарная бумажная экономия **$89.13** остаётся только сравнительным evidence и не является активным маршрутом квалификации или заменой BOM.

| № | Текущая группа | Лучший массовый маршрут | Статус | До экономии |
|---:|---|---|---|---:|
| 1 | [`SMA-W100RX2`](https://www.comet-ant.co.jp/product/638/) | [Opek SCANSMA 25-1300](https://www.hamradio.com/detail.cfm?pid=H0-016713) | ✅ оставить · кандидат отклонён | $20.00 |
| 2 | [`001-0012`](https://www.te.com/en/product-001-0012.html) | [split the group: TE 001-0001 for S3 2.4 GHz; Taoglas GW.05.0153 for C5 2.4/5 GHz](https://www.taoglas.com/datasheets/GW.05.0153.pdf) | ✅ оставить · кандидат отклонён | $19.30 |
| 3 | [`AN0155H13`](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h13.html) | [Powerwerx ANT-8](https://powerwerx.com/vhf-uhf-dual-band-standard-sma-antenna) | ✅ оставить · кандидат отклонён | $23.93 |
| 4 | [`ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | [Ebyte TX433-JZR-6 for UHF plus TX433-JK-11 for the narrow 433-MHz port](https://www.ebyte.com/product/824.html) | ✅ оставить · кандидат отклонён | $19.57 |
| 5 | [`GCT RFPC-SMA31-FN-175-A`](https://www.digikey.com/en/products/detail/gct/RFPC-SMA31-FN-175-A/17833784) | [retain current GCT standard-SMA body](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554) | ✅ оставить | $0.00 |
| 6 | [`EastRising ER-TFT035IPS-6 + ER-TPC035-6`](https://www.buydisplay.com/3-5-inch-tft-lcd-display-capacitive-touch-screen-ips-320x480) | [retain the documented EastRising panel and touch pair](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf) | ✅ оставить | $0.00 |
| 7 | [`Analog Devices AD8314ARMZ-REEL`](https://jlcpcb.com/partdetail/AnalogDevices-AD8314ARMZREEL/C652687) | [retain accepted C652687 MSOP route](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8314.pdf) | ✅ оставить | $0.00 |
| 8 | [`OMRON B3S-1100P`](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3S-1100P/60835) | [retain B3S-1100P; source by JLC pre-order/consignment if necessary](https://jlcpcb.com/partdetail/OmronElectronicComponents-B3S1100P/C2733652) | ✅ оставить | $0.00 |
| 9 | [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | [retain exact SA818S-V C51897911](https://www.nicerf.com/walkie-talkie-module-sa818s.html) | ✅ оставить | $0.00 |
| 10 | [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | [retain SA818S-U C3001549](https://www.nicerf.com/walkie-talkie-module-sa818s.html) | ✅ оставить | $0.00 |
| 11 | [`ANT-315-CW-HW-SMA`](https://www.te.com/en/product-ANT-315-CW-HW-SMA.html) | [Joymax UHX-328ASA2B](https://www.digikey.com/en/products/detail/joymax-electronics/UHX-328ASA2B/28334978) | ✅ оставить · кандидат отклонён | $4.03 |
| 12 | [`Ebyte E01-ML01SP4`](https://jlcpcb.com/partdetail/E01-ML01SP4/C97340) | [retain JLCPCB C97340](https://www.ebyte.com/product/1200.html) | ✅ оставить | $0.00 |
| 13 | [`Keystone Electronics 1048P`](https://www.digikey.com/en/products/detail/keystone-electronics/1048P/4499417) | [retain 1048P; use reviewed factory sourcing/consignment route](https://jlcpcb.com/partdetail/KeystoneElectronics-1048P/C6038062) | ✅ оставить | $0.00 |
| 14 | [`Texas Instruments TMUX1136DGSR`](https://jlcpcb.com/partdetail/TexasInstruments-TMUX1136DGSR/C2673301) | [retain TMUX1136DGSR C2673301](https://www.ti.com/lit/ds/symlink/tmux1136.pdf) | ✅ оставить | $0.00 |
| 15 | [`LTC5532ES6#TRMPBF`](https://jlcpcb.com/partdetail/AnalogDevices-LTC5532ES6TRMPBF/C580926) | [retain LTC5532; exact-one needs two and current stock covers it](https://www.analog.com/media/en/technical-documentation/data-sheets/5532f.pdf) | ✅ оставить | $0.00 |
| 16 | [`Samtec FTSH-105-01-L-DV-K-P-TR`](https://jlcpcb.com/partdetail/Samtec-FTSH_105_01_L_DV_K_PTR/C2932107) | [retain JLCPCB C2932107](https://www.tag-connect.com/product/tc2050-idc-nl-10-pin-no-legs-cable-with-ribbon-connector) | ✅ оставить | $0.00 |
| 17 | [`TE Connectivity 1-2118651-0`](https://www.te.com/en/product-1-2118651-0.html) | [retain exact 60-mm 1.37-mm-max U.FL-to-U.FL jumper](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/1-2118651-0/12380462) | ✅ оставить | $0.00 |
| 18 | [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/EspressifSystems-ESP32S3WROOM1UN16R8/C3013946) | [retain exact N16R8 external-antenna module](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | ✅ оставить | $0.00 |
| 19 | [`GCT RFPC-SMA32-FN-175-A`](https://www.digikey.com/en/products/detail/gct/RFPC-SMA32-FN-175-A/17833785) | [retain current GCT reverse-polarity body](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE901/C914553) | ✅ оставить | $0.00 |
| 20 | [`TI.08.C.0112`](https://www.taoglas.com/datasheets/TI.08.C.0112.pdf) | [Seeed Studio 113070002 868/915-MHz whip](https://www.seeedstudio.com/External-Antenna-868-915MHZ-2dBi-SMA-L195mm-Foldable-p-5863.html) | ✅ оставить · кандидат отклонён | $2.30 |

Почему шесть альтернатив отклонены:

- **`SMA-W100RX2` → Opek SCANSMA 25-1300:** same stated 25-1300-MHz receive range, but it is a remote magnetic-mount antenna with 12-ft RG-174 rather than a direct telescopic whip (in stock at Ham Radio Outlet; USD 15.95)
- **`001-0012` → split the group: TE 001-0001 for S3 2.4 GHz; Taoglas GW.05.0153 for C5 2.4/5 GHz:** S3 does not use 5 GHz, so its dual-band/IP67 capability is unused; C5 candidate begins at 5150 rather than 4910 MHz and both substitutions require assembled-device matching/EIRP closure (001-0001: 2,656 Mouser stock; GW.05.0153: distributor stock and serial order route)
- **`AN0155H13` → Powerwerx ANT-8:** covers 136-174 and 400-470 MHz with standard SMA, but its public page does not close gain, VSWR, power or exact mechanical seating; it may cover both voice ports only after VNA and voice-TX HIL (in stock; USD 7.77)
- **`ANT-433-CW-QW-SMA` → Ebyte TX433-JZR-6 for UHF plus TX433-JK-11 for the narrow 433-MHz port:** UHF candidate preserves 400-480 MHz, 10 W and improves stated VSWR but nominal gain falls 3.3 to 3.0 dBi; the 433 candidate is narrow-band and both need VNA/EIRP HIL (both serial Ebyte parts available from stocked distributors; TX433-JZR-6 observed at USD 1.72)
- **`ANT-315-CW-HW-SMA` → Joymax UHX-328ASA2B:** candidate is 312-317 rather than 304-325 MHz, -0.4 rather than 0 dBi and 1 W; adequate only for the exact 315-MHz profile after VNA/TX HIL (958 DigiKey stock; USD 5.5693 at 100)
- **`TI.08.C.0112` → Seeed Studio 113070002 868/915-MHz whip:** candidate preserves both bands, SMA and 10 W but changes right-angle mechanics and falls from 2.48 to 2.0 dBi at 868 MHz; both regional EIRP limits require HIL (in stock; USD 2.49)

[Полный аудит и evidence — CSV](../hardware/product-design/generated/H1-R2-top20-market-audit.csv)

## Где вероятнее всего есть неоправданные траты

| Приоритет | Группа | Сейчас ×1 | Вывод | Реалистичная экономия |
|---:|---|---:|---|---:|
| 1 | Внешние антенны | $138.32 + 4 неизвестных | Крупнейшая отдельная группа; функциональность нужна, но брендовые первые MPN не обязаны быть самыми выгодными | уточняется |
| 2 | 10 внешних SMA/RP-SMA | $24.65 | Проверены дешёвые standard/reverse-пары; они провалили направление, геометрию 5+5 либо exact-one factory route. GCT остаётся оправданным | $0 доказанно |
| 3 | 8 RF-detector’ов | $19.41 | Шесть AD8314 уже переведены на C652687 после полного placement-аудита; функциональность и все восемь evidence-трактов сохранены | $5.50 уже принято |
| 4 | 5 U.FL + 5 кабелей | $9.48 | Упаковочная версия Hirose уже удешевлена без потерь; убрать можно только один тракт после доказанного C5 T2-маршрута | до ~$1.90 дополнительно |
| 5 | 16 пользовательских кнопок | $10.25 | Проверенные дешёвые кандидаты ухудшают ESD, feel или evidence; текущая группа оправдана | $0 |
| 6 | Держатель 2×18650 | $8.57 | Складские одиночные держатели не доказывают полный protected-cell и polarity contract; 1048P оправдан | $0 |
| 7 | 4 внутренних DBG10 | $6.80 | Exact Samtec уже складской; Tag-Connect удорожает единственный EVT1 и ухудшает long-session workflow | $0 для EVT1 |

**Не считаю неоправданными:** серийный дисплей за $14,91, два voice-модуля за $19,81, три полнофункциональных nRF24 за $8,89, оба RP/S3/C5, M1 и элементы автономной защиты. Их удаление или упрощение напрямую режет принятую функцию, пропускную способность, восстановление либо безопасность.

## Что ещё нельзя считать бесплатным

Эти позиции имеют **не нулевую**, а пока неизвестную цену. До exact-one quote итоговая стоимость остаётся нижней границей.

| Источник | MPN и роль | Шт. ×1 |
|---|---|---:|
| Основная BOM | `Murata GJM1555C1H101JB01D`<br><sub>cc_rf_n_dc_block, cc_rf_p_dc_block</sub> | 2 |
| Основная BOM | `Nexperia PESD24VY1BSF`<br><sub>voice_rf_esd, voice_v_rf_esd</sub> | 2 |
| Основная BOM | `Panasonic ERJ-P08F49R9V`<br><sub>pack_batts_rbal, pack_cell1_rbal</sub> | 2 |
| Основная BOM | `Sunlord MWSA0503S-3R3MT`<br><sub>main_inductor, voice_inductor</sub> | 2 |
| Основная BOM | `Texas Instruments TPUL2G223BQBR`<br><sub>pack_diag_timer</sub> | 1 |
| Антенный комплект | `TX2400-JW-5`<br><sub>2.4 GHz nRF24; N1, N2, N3</sub> | 3 |
| Антенный комплект | `L2-ANT-AM-LW-001`<br><sub>passive receive-only direct-plug ferrite pod; LOOP</sub> | 1 |

## Где малая партия переплачивает

- `27` pre-order-строк стоят в снимке **$660.01** против **$331.03** на массовой материальной базе.
- Наблюдаемый штраф малой партии — **$328.98**. Это верхний приоритет: искать не «дешевле любой ценой», а эквивалентные stocked JLCPCB MPN внутри уже заданных substitution-классов.
- `displayed_line_cost` JLCPCB использует рекомендуемое количество и pre-order reference pricing; это честный индикатор боли малой партии, но не финальный quote и не сумма готового заказа.

## Внешний антенный комплект

| Code | Profile | MPN | Qty | Known line |
|---|---|---|---:|---:|
| `AIR` | receive-only telescopic whip | `SMA-W100RX2` | 1 | $35.95 |
| `S3, C5` | 2.4/5 GHz native radio | `001-0012` | 2 | $33.82 |
| `VHF` | VHF 136-174 MHz | `AN0155H13` | 1 | $31.70 |
| `S433, UHF` | 433 MHz / UHF 400-470 MHz | `ANT-433-CW-QW-SMA` | 2 | $22.46 |
| `S315` | 315 MHz | `ANT-315-CW-HW-SMA` | 1 | $9.60 |
| `S915` | 868/915 MHz | `TI.08.C.0112` | 1 | $4.79 |
| `N1, N2, N3` | 2.4 GHz nRF24 | `TX2400-JW-5` | 3 | — |
| `LOOP` | passive receive-only direct-plug ferrite pod | `L2-ANT-AM-LW-001` | 1 | — |

## Проверенные складские кандидаты

| Область | Исходная позиция | Проверенная позиция | JLCPCB | Доступно для заказа | Статус |
|---|---|---|---|---:|---|
| ESP32-C5 production supplier route and revision floor | `ESP32-C5-WROOM-1U-N8R8 / historical C51950748` | `ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2` | `C54951858` | 440 | `accepted_stocked_supplier_route_identity_normalization` |
| dual Ioff return buffers | `Nexperia 74LVC2G126DC,125` | `Nexperia 74LVC2G126DP,125` | `C503392` | 155 | `accepted_stocked_exact_family_package_variant` |
| six AD8314 real-TX evidence detectors | `Analog Devices AD8314ACPZ-RL7` | `Analog Devices AD8314ARMZ-REEL` | `C652687` | 2977 | `accepted_same_device_msop_explicit_factory_route_and_physical_fit` |
| five native/module U.FL receptacles | `Hirose U.FL-R-SMT-1(10)` | `Hirose U.FL-R-SMT-1(80)` | `C88374` | 68798 | `accepted_stocked_exact_packaging_variant` |
| all 100-nF 50-V X7R 0402 bypass positions | `TDK C1005X7R1H104K050BB` | `YAGEO CC0402KRX7R9BB104` | `C131394` | 7796754 | `accepted_stocked_exact_parametric_replacement` |
| six ordinary 0402 resistor identities across 28 positions | `YAGEO RC0402FR-072K2L / 07133KL / 07270KL / 075K23L / 078K2L / 071K65L` | `UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE` | `C25879 / C25753 / C25770 / C25907 / C25924 / C25869` | 2027222 / 6692 / 156208 / 40861 / 234262 / 5616 | `accepted_stocked_exact_parametric_replacements` |
| two dual Schmitt inverters | `Nexperia 74LVC2G14GW,125` | `Nexperia 74LVC2G14GV,125` | `C426708` | 35 | `accepted_stocked_exact_family_package_variant` |
| codec transmit attenuator top resistor | `Vishay CRCW0402160KFKED` | `UNI-ROYAL 0402WGF1603TCE` | `C25757` | 388017 | `accepted_stocked_exact_parametric_replacement` |
| IR emitter current-limit resistor | `YAGEO RC1206FR-0747RL` | `FH RS-06K47R0FT` | `C140014` | 78058 | `accepted_stocked_exact_parametric_replacement` |
| 100-nF 100-V USB VBIAS capacitor | `TDK C1608X7S2A104K080AB` | `YAGEO CC0603KRX7R0BB104` | `C113803` | 1027658 | `accepted_stocked_no_worse_parametric_replacement` |
| dual common-drain pack-protection MOSFET | `Texas Instruments CSD87313DMST` | `Texas Instruments CSD87313DMS` | `C2863848` | 4741 | `accepted_stocked_exact_packaging_variant` |
| robust 38-kHz demodulating IR receiver | `Vishay TSOP75238TT` | `Vishay TSOP75238TR` | `C511498` | 15 | `accepted_stocked_exact_tape_presentation_variant_with_placement_gate` |
| Si4732 FMI 56-nH high-Q matching inductor | `Murata LQW15AN56NJ00D` | `Murata LQW15AN56NG00D` | `C167482` | 20744 | `accepted_stocked_no_worse_parametric_replacement` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `OMRON B3S-1000P` | `C180420` | 3254 | `not_accepted_missing_ground_terminal` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `BZCN TSG002A04526A` | `C2888613` | 440 | `not_accepted_heavier_force_ground_and_exact_life_unresolved` |
| dual protected-button-top 18650 retention | `Keystone Electronics 1048P` | `MYOUNG BH-18650-B1BA002` | `C2988620` | 995 | `not_accepted_single_cell_and_protected_length_unproven` |
| four independent opened-sandwich recovery endpoints | `Samtec FTSH-105-01-L-DV-K-P-TR` | `Tag-Connect TC2050-IDC board footprint` | `not applicable; bare PCB pads and locating holes` | official cable available | `not_accepted_for_exact_one_evt1_cost_and_debug_ergonomics` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5` | `C53278703 / C53278707` | 67 standard / 133 reverse | `rejected_wrong_board_normal_orientation` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `DreamLNK SMA-KWE902 / SMA-KWE901` | `C914554 / C914553` | 5479 pre-sale + 5588 overseas standard / 7 pre-sale + 42 overseas reverse | `rejected_current_5_plus_5_mechanical_envelope_and_factory_route` |

- **`ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2`:** Принято в H1-R2.28 без изменения официального MPN Espressif, 8 МиБ flash, 8 МиБ PSRAM, корпуса, land pattern или антенного разъёма. Суффикс JLC является только supplier order code. Активный складской маршрут Standard PCBA — C54951858; исторический zero-stock C51950748 запрещён как active. Production требует одновременно MD/lot identity и eFuse revision >=v1.2; v1.0 только engineering, v0.1/unknown запрещены. Серийная материальная база снижается с $4,3700 до $4,1338 на устройство, live-строка пяти устройств равна $29,2935. [JLCPCB](https://jlcpcb.com/partdetail/C54951858)
- **`Nexperia 74LVC2G126DP,125`:** Принято в H1-R2.23. DP и DC — корпусные варианты одного семейства Nexperia 74LVC2G126: логика, порядок выводов, Schmitt-входы, Ioff и тайминги сохранены. Увеличенные TSSOP-корпуса прошли повторный аудит компоновки. Строка партии из пяти устройств снижается с наблюдавшихся $40,60 pre-order до $12,1425 со склада; цена одной микросхемы на ступени 100 шт. растёт с прежней внешней базы $0,2086 до JLCPCB $0,3753. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392)
- **`Analog Devices AD8314ARMZ-REEL`:** Принято в H1-R2.36. Analog Devices задаёт ARMZ-REEL и ACPZ-RL7 как корпусные варианты одной функции AD8314 с одинаковыми пронумерованными выводами 1-8; у RM-8 лишь нет exposed paddle. JLCPCB C652687 доступен как Extended SMT для Standard PCBA через явный pre-order/overseas-маршрут на 2 977 деталей, при 2 978 overseas и MOQ 4; на единственное устройство нужно шесть. Все шесть полных lead-envelope 5,15 x 3,20 x 1,10 мм, два сохранённых LTC5532, все пять coupler и восемь локальных evidence-островов проходят аудит коллизий, compression-stop и встречной платы. Строка quantity-100 снижается с $17,1420 до $11,6388, экономия $5,5032 на устройство без удаления evidence. [JLCPCB](https://jlcpcb.com/partdetail/AnalogDevices-AD8314ARMZREEL/C652687)
- **`Hirose U.FL-R-SMT-1(80)`:** Принято в H1-R2.37. Hirose перечисляет (01), (60) и (80) как варианты поставки одной розетки U.FL-R-SMT-1 с теми же контактами, корпусом 2,6 x 2,6 x 1,25 мм, посадкой и параметрами 6 ГГц / 50 Ом; меняется только упаковка. C88374 есть на складе JLCPCB как SMT для Economic и Standard PCBA. Пять установленных розеток снижаются с $5,3275 до $0,4115 на общей базе quantity-100, экономя $4,9160 без изменения платы, RF или прошивки. [JLCPCB](https://jlcpcb.com/partdetail/U.FL-R-SMT-1%2880%29/C88374)
- **`YAGEO CC0402KRX7R9BB104`:** Принято в H1-R2.24. YAGEO сохраняет 100 нФ, 50 В, X7R, +/-10%, 0402/1005, диапазон -55…+125 °C и тот же корпус 1,0 x 0,5 x 0,5 мм. На JLCPCB это складская позиция для Standard PCBA с MOQ 1. Строка партии из пяти устройств снижается с наблюдавшихся $22,5624 pre-order TDK до $5,9535 со склада, экономия $16,6089; серийная материальная база уменьшается на $2,2197 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394)
- **`UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE`:** Принято в H1-R2.26. Каждая замена сохраняет точный номинал, корпус 0402, допуск 1 %, мощность 62,5 мВт, рабочее напряжение 50 В, ТКС 100 ppm/°C и диапазон -55…+155 °C. Все шесть точных MPN UNI-ROYAL есть на складе JLCPCB для Standard PCBA с MOQ 1. Потребность партии из пяти устройств снижается примерно с $53,7347 по зафиксированному pre-order-маршруту до $0,5430 со склада, экономия около $53,1917; публичная материальная база снижается на $0,1542 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879)
- **`Nexperia 74LVC2G14GV,125`:** Принято в H1-R2.26. GV и GW — корпусные варианты из одного актуального datasheet Nexperia 74LVC2G14: общими остаются два Schmitt-инвертора, выводы 1–6, питание 1,65–5,5 В, Ioff при снятом питании и тайминги. Корпуса TSOP6 2,9 × 1,5 × 1,1 мм проходят повторный аудит компоновки. Для десяти деталей пробной партии доступны 35 штук. Строка партии из пяти устройств снижается с $9,0376 pre-order до $2,0100 со склада, экономия $7,0276; консервативная серийная материальная база растёт на $0,2026 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708)
- **`UNI-ROYAL 0402WGF1603TCE`:** Принято в H1-R2.27. UNI-ROYAL сохраняет 160 кОм, допуск +/-1 %, корпус 0402, стандартную мощность 1/16 Вт, рабочее напряжение 50 В, ТКС 100 ppm/°C и диапазон -55…+155 °C. Официальный корпус 1,00 x 0,50 x 0,35 мм тоньше выбранного Vishay 1,00 x 0,50 x 0,40 мм, поэтому проверенная посадка 0402 и просвет бутерброда не ухудшаются. Строка партии из пяти устройств снижается с $8,9565 pre-order до $0,0130 со склада, экономия $8,9435; публичная материальная база снижается на $0,0131 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757)
- **`FH RS-06K47R0FT`:** Принято в H1-R2.27. FH сохраняет 47 Ом, допуск +/-1 %, корпус 1206, мощность 0,25 Вт, 200 В, ТКС 100 ppm/°C и диапазон -55…+155 °C. Его официальный корпус 3,20 x 1,60 x 0,55 мм тоньше выбранного YAGEO 3,20 x 1,60 x 0,65 мм и использует стандартную посадку 1206. Строка партии из пяти устройств снижается с $8,9566 pre-order до $0,0310 со склада, экономия $8,9256; публичная материальная база снижается на $0,0108 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014)
- **`YAGEO CC0603KRX7R0BB104`:** Принято в H1-R2.27. YAGEO сохраняет 100 нФ, допуск +/-10 %, 100 В, корпус 0603/1608, диапазон -55…+125 °C и точные габариты 1,60 x 0,80 x 0,80 мм. X7R удерживает ёмкость в пределах +/-15 % по температуре и строже прежнего X7S +/-22 %, поэтому тракт USB VBIAS не ухудшается. Строка партии из пяти устройств снижается с $9,0752 pre-order до $0,1300 со склада, экономия $8,9452; публичная материальная база снижается на $0,0266 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803)
- **`Texas Instruments CSD87313DMS`:** Принято в H1-R2.29. TI задаёт DMS и DMST как один production die, один корпус WSON-CLIP DMS 8, одну распиновку и одни электрические пределы; DMS — большая катушка 2500 шт., DMST — малая катушка 250 шт. C2863848 есть на складе JLCPCB для Standard PCBA. Строка пяти устройств снижается с $7,3675 до $5,2790, экономия $2,0885; серийная материальная база уменьшается на $0,7084 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/x/C2863848)
- **`Vishay TSOP75238TR`:** Принято в H1-R2.29. Vishay использует для TR и TT один и тот же конечный корпус Heimdall 6,8 x 3,0 x 3,2 мм, контакты и электрический контракт; TR меняет подачу в ленте с top view на side view и катушку с 2200 на 2300 шт. Текущий остаток C511498 покрывает партию из пяти устройств, но не серию из 100. Перед каждым заказом точный остаток должен покрывать всю работу с attrition либо деталь заранее заказывается, а CPL rotation/подача feeder сверяются с placement preview JLCPCB. Строка пяти устройств снижается с $7,3000 до $6,5055, экономия $0,7945; серийная материальная база уменьшается на $0,2369 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/x/C511498)
- **`Murata LQW15AN56NG00D`:** Принято в H1-R2.29. Код G Murata сохраняет корпус LQW15AN 0402, номинал 56 нГн, Q, минимальный SRF 2,8 ГГц, ток 200 мА и максимальный DCR 1,17 Ом, одновременно ужесточая допуск с +/-5 % до +/-2 %. C167482 есть на складе JLCPCB для Standard PCBA. Строка пяти устройств снижается с $0,3620 до $0,2235, экономия $0,1385; серийная материальная база уменьшается на $0,0277 на устройство. [JLCPCB](https://jlcpcb.com/partdetail/x/C167482)
- **`OMRON B3S-1000P`:** Складской вариант сохраняет корпус 6,6 × 6,0 × 4,3 мм, усилие 1,57 Н, ресурс 500 тысяч нажатий и IP67, но лишён пятого вывода заземления крышки. Это может ухудшить ESD-защиту доступной пользователю клавиши, поэтому B3S-1100P остаётся выбранной до доказательства равноценной складской замены. [JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-B3S1000P/C180420)
- **`BZCN TSG002A04526A`:** Складской SMT-корпус 6,15 x 6,15 x 4,5 мм с IP67 снизил бы цену шестнадцати кнопок при количестве 1 с $14,50 до $0,79, но усилие возрастает с 1,57 до 2,6 Н, исчезает пятый заземлённый вывод крышки на доступной пальцу границе, а для точного кода не заявлен гарантированный ресурс 500 тысяч нажатий. Это ухудшение функции, ESD и ощущений, а не бесплатная экономия, поэтому деталь не выбрана. [JLCPCB](https://jlcpcb.com/partdetail/BZCN-TSG002A04526A/C2888613)
- **`MYOUNG BH-18650-B1BA002`:** Складской позолоченный держатель одного элемента устанавливается фабрикой и дешевле, но его чертёж 77,05 x 20,65 мм не доказывает посадку выбранного длинного защищённого button-top XTAR, механическую защиту двух элементов от переполюсовки до касания контактов и текущий единый корпус с четырьмя независимыми контактами. Поэтому две такие детали не являются равноценной заменой 1048P. [JLCPCB](https://jlcpcb.com/partdetail/BH-18650-B1BA002/C2988620)
- **`Tag-Connect TC2050-IDC board footprint`:** Ключевая пружинная площадка убрала бы все четыре разъёма из повторяемой BOM, но для единственного прототипа сначала потребуется кабель за $39 вместо $5,64 за четыре текущих складских Samtec в JLCPCB. Кроме того, свободное длительное подключение сменится отдельным probe-процессом. Для EVT1 сохраняются складские Samtec; Tag-Connect остаётся вариантом после EVT1 при серийном удешевлении. [JLCPCB](https://www.tag-connect.com/product/tc2050-idc-tag-connect-2050-idc)
- **`HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5`:** Карточки JLCPCB подтверждают standard/reverse-пару до 6 ГГц, а контролируемые чертежи HenryTech — индивидуальное удержание без гайки, но оба корпуса направлены перпендикулярно плате. Они не заменяют выбранные торцевые GCT без смены направления антенн и формы продукта. [JLCPCB](https://jlcpcb.com/partdetail/HenryTech-HL2_SMA_KEP_135/C53278703)
- **`DreamLNK SMA-KWE902 / SMA-KWE901`:** Точные чертежи DreamLNK подтверждают прочную standard/reverse-пару до 6 ГГц без гаек с пятью сквозными выводами, но одновременно отрицательно закрывают вопрос посадки в принятом мокапе. Каждый внешний корпус 9,7 x 9,7 мм входит в 4-мм keep-out головки верхней compression-stop у крайних портов обеих плат, а рисунок выводов 5,08 x 5,08 мм пересекает разъём дисплея, два coupler native-RF, резерв Airband и область CC1101 на внутренних сторонах. Исправление потребует переноса принятых силовых осей либо сжатия ряда 5+5 и перемещения RF-компонентов. Маршрут JLCPCB всё ещё Plugin/manualWeld с минимумами закупки 13/12 и без цены сборки ровно одного устройства. Это не drop-in экономия без потерь, поэтому выбранная пара GCT остаётся. [JLCPCB](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554)
**Принятое правило:** сначала устранять pre-order на малой партии, но менять MPN только на точный или не худший складской вариант. RF, power-safety, battery-protection и пользовательские ESD-границы не упрощаются ради цены. Если доказанного аналога нет, остаётся исходный MPN и явный pre-order.

## Очередь удешевления

1. ▶ **Пересобрать внешний антенный комплект из складских эквивалентов** — Уже оценённые восемь из двенадцати профилей стоят $138,32 на одно устройство; три nRF24-антенны и AM/LW pod ещё не оценены. Это крупнейшая отдельная материальная группа проекта, хотя она не входит в базовую PCBA BOM. Не удалять диапазоны и не подменять TX-антенны широкополосным компромиссом: для каждого порта найти серийный складской MPN с тем же разъёмом, диапазоном, мощностью и не худшим согласованием, а receive-only профили оптимизировать отдельно.
2. ✅ **Заменить безопасно эквивалентные pre-order пассивы и обычную логику на складские JLCPCB** — После семи безопасных пакетов 27 pre-order-строк стоят $660,0144 в нормализованном снимке партии из пяти устройств против $331,0265 по серийной материальной базе. Складские маршруты Nexperia, YAGEO, UNI-ROYAL, FH, Hirose, TI, Vishay и Murata вместе убирают около $140,8195 из наблюдаемого пробного маршрута и снижают публичную материальную базу на $8,0045 на устройство. Проверять каждую строку по её substitution-классу; принимать только точную либо не худшую параметрическую замену.
3. ✅ **Сохранить GCT-пару после провала полной проверки дешёвой сквозной пары в геометрии 5+5** — Десять GCT RFPC-SMA31/32 стоят $24,65 на устройство. Точные чертежи закрыли привлекательную альтернативу DreamLNK: четыре внешних корпуса конфликтуют с keep-out головок принятых верхних compression-stop, пять групп портов — с телами или резервами на внутренних сторонах, а фабричный маршрут остаётся manualWeld без цены для ровно одного устройства. Оставить принятую двусторонне припаянную пару GCT. Возвращаться к замене только для фабрично устанавливаемой standard/reverse-пары с внешним направлением, покрытием 6 ГГц для native-портов, посадкой в неизменённую геометрию 5+5 и compression-stop и полным маршрутом заказа ровно одного устройства.
4. ✅ **Сохранить принятую MSOP-версию AD8314 и все восемь трактов реальной передачи** — Шесть AD8314ARMZ-REEL и два LTC5532 теперь дают $19,41 на устройство. C652687 имеет явный JLCPCB Extended-SMT Standard-PCBA pre-order/overseas-маршрут: MOQ 4, доступно 2 977, а единственному устройству нужно шесть. Все корпуса и восемь локальных островов проходят H1-R2.36. Перенести точные корпуса, локальные RF/passive allocations и отсутствие EPAD у RM-8 в новый R2 H2. Два LTC5532 и независимое evidence трёх одновременно работающих nRF24 сохранить.
5. ✅ **Сохранить заземлённую серию Omron для всех шестнадцати обычных клавиш** — B3S-1100P дают $10,25 на устройство. Проверены два складских аналога: B3S-1000P сохраняет усилие, высоту, ресурс и IP67, но теряет заземление крышки; TSG002A04526A намного дешевле, но также теряет этот вывод, повышает усилие до 2,6 Н и не доказывает ресурс точного кода в 500 тысяч нажатий. Поскольку все кнопки нажимаются пальцем напрямую без колпачка или толкателя, оба варианта хуже. Оставить B3S-1100P в текущей архитектуре. Возвращаться к замене только при наличии фабрично устанавливаемой детали с заземлённой пользовательской границей, усилием около 1,6 Н, высотой 4,3 мм, IP67 и ресурсом не менее 500 тысяч нажатий либо после будущей механической изоляции металлической крышки корпусом.
6. ✅ **Сохранить все пять трактов U.FL + 30-мм кабель после проверки размещения источников** — Пять трактов теперь дают $9,52 на устройство после перехода на точную складскую упаковочную версию Hirose; ручная укладка не учтена. S3 и все три E01 выводят RF только через микрокоаксиальный разъём, а каждый тракт обязан пройти через локальный coupler и детектор реальной передачи до SMA. Текущий C5 также выводит U.FL; точный складской Espressif T2/ANT2 factory-route не доказан. Поэтому сейчас безопасно удалить можно 0/5 трактов. Будущий квалифицированный C5 T2 может убрать один тракт и сэкономить около $1,90 на устройство.
7. ✅ **Сохранить 1048P до доказательства полноценного держателя защищённых элементов** — 1048P даёт $8,57 на устройство и остаётся pre-order, но проверенные складские MYOUNG — одиночные держатели или отдельные контакты: они не доказывают длину выбранных защищённых button-top XTAR, механическую блокировку переполюсовки двух элементов до касания контактов и единый четырёхконтактный механизм с опорой на корпус. Для EVT1 оставить 1048P как оправданный safety/mechanical-компонент. Возвращаться к замене только при наличии серийного фабрично устанавливаемого двойного держателя, который доказывает полный XTAR-envelope и передаёт усилия вставки/извлечения на корпус, а не на пайку.
8. ✅ **Сохранить четыре складских Samtec DBG10 для единственного EVT1** — Исправленное количество R2 — четыре, а не три. Точный C2932107 сейчас есть на складе JLCPCB Extended SMT: 890 шт., доступны 887, MOQ 1 и $1,41 при количестве 1. Четыре разъёма стоят $5,64 на exact-one factory route. Площадки TC2050-IDC убрали бы детали с плат, но потребовали бы отдельный кабель за $39 и изменили бы удобство длительной отладки. Оставить четыре FTSH-105-01-L-DV-K-P-TR для независимого восстановления S3/C5/Hub-RP/RF-RP. Вернуться к Tag-Connect после EVT1, когда одноразовую цену кабеля можно амортизировать и проверить service-workflow.
9. ✅ **Не удешевлять уже выбранную серийную панель** — EastRising ER-TFT035IPS-6 + ER-TPC035-6 стоит $14,91, имеет полный чертёж, ILI9488/FT6236, i8080-8 и серийный заказ от одной штуки. Донорская схема удалена. Считать стоимость дисплея оправданной; открытым остаётся только тариф и письменное принятие фабрикой установки панели и FPC, а не поиск другого экрана.

## Ориентация экрана и шлейфа

- Точные чертежи EastRising контролируют полный корпус панели, 50-контактный FPC, шаг 0,50 мм, stiffener 0,30 мм и карту контактов; геометрия donor-board больше не используется.
- Экран физически ориентирован **шлейфом к антенному торцу**, а изображение ILI9488 и координаты FT6236 разворачиваются программно. Шлейф не входит в зону LED, D-pad и функциональных клавиш.
- Прямой ZIF `Hirose FH34SRJ-50S-0.5SH(50)` в позиции `[24.0, 1.8]` прогнан по текущим точным корпусам: `0` same-face collisions и `10.0 мм` до противоположной плоскости при требуемых `0.7 мм`.
- Отдельная плата-адаптер и оба DF40 удалены: высота стека снижается с `3.8` до `1.0 мм`, а цена компонентов одного прототипа — на `$1.07`. Панель держит один готовый 3M (TC) `4910SQ-2(5)` 50,8×50,8-мм PSA-квадрат; контакты ZIF нагрузки не несут. Его условные `$22.12` не добавлены в замороженный BOM до проверки стека ≤0,714 мм и принятия фабрикой.

> Маркер: **H1-R2.38**. Включено в текущий проведённый ревью результат H1.
