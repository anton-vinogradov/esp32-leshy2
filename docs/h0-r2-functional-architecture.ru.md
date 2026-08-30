# H0-R2 · Функциональная архитектура

H0-R2 проведён как новый функциональный baseline: UI и дисплей остаются на S3, высокоскоростные периферийные тракты разгружены через Hub RP, бортовой видеотракт удалён, а Airband AM 118–137 МГц теперь обязателен.

> Текущий точный маркер — **H2-R2.0**. Физическая проекция H1-R2.37 с двумя независимыми RP2354B, точными GPIO0..47, четырьмя M1 endpoint-группами и 226 корпусами принята и прошла ревью 2026-08-30. В неё входят все восемь TX-детекторов, пять coupler и восемь локальных evidence-островов; шесть AD8314 используют принятый `AD8314ARMZ-REEL` / `C652687`. Серийный дисплей EastRising, U219, NFC-loop и swept volume антенны закрыты. Старая single-RP G2F/H2-проекция остаётся только историческим R1 evidence. H2-R2.0 закрывает live route C11355, точный MPN detector/latch service-VBUS и powered-off-Ioff границу Pack/Safety I2C до native R2 ECAD/KiCad.

![H0-R2 functional architecture](images/h0-r2-functional-architecture.svg)

## Что зафиксировано

- Один пользовательский порт `FM / SW / AIR RX`; новый внешний разъём не добавлен.
- Airband — подрежим `BROADCAST_RX`, поэтому его RF-домен не включается одновременно с TX-группой.
- Кнопки остаются на локальном для S3 TCA9539PWR, энкодер и USB подключены к S3 напрямую; direct i8080-8 даёт 24 МБ/с при безопасных для ILI9488 24 МГц.
- Передний RP владеет тремя nRF24 и microSD; задний RP владеет Si4732/Airband, CC1101, voice, аудио, M5 и одним из U214/U219.
- M1 переносит control/status, safety, USB и питание; контакты 35–36 теперь NC-резерв.

## Airband RX

`shared FM/SW/AIR SMA protection and mode split` → `118-137-MHz image-rejection band-pass network` → `PGA-103+ low-noise gain stage` → `LT5560EDD#TRPBF down-converting mixer` → `112-MHz LO from SI5351A-B-GTR` → `6-25-MHz IF cleanup network` → `HMC544AETR RF/IF selector` → `existing Si4732-A10-GSR FMI and audio path`

Фиксированный low-side LO 112 МГц переносит 118–137 МГц в 6–25 МГц. Зеркальный диапазон находится на 87–106 МГц, поэтому входной band-pass обязателен для работоспособности, а не является необязательным cleanup-фильтром.

## Ноги и владелец

| GPIO | Функция | Поведение после reset |
|---|---|---|
| Rear RP GP35 | `AIR_RX_EN` | pulled low; LNA/mixer/LO domain off |
| Rear RP GP36 | `AIR_RX_MODE` | direct FM/SW path selected |

Front RP budget: **46 used / 2 free**. Rear RP budget: **40 used / 8 free**. SI5351 control stays on the rear-local I²C bus at `0x60`; no Airband control traffic uses the S3 UI bus.

## Рабочая принципиальная распиновка

Это полный рабочий принципиальный бюджет H0-R2, а не разрешение начинать KiCad. H1 может изменить конкретный контакт только вместе с этим источником, проверками и публичной таблицей.

| GPIO S3 | Сеть | Периферия | Направление |
|---:|---|---|---|
| `0` | `S3_RESERVE_0` | `GPIO` | `reserve` |
| `1` | `SYS_UI_I2C_SDA` | `I2C0` | `io` |
| `2` | `SYS_UI_I2C_SCL` | `I2C0` | `out` |
| `3` | `UI_HUB_ALERT_N` | `GPIO_IRQ` | `in` |
| `4` | `LCD_DB0` | `LCD_CAM_TX` | `out` |
| `5` | `S3_RESERVE_5` | `GPIO` | `reserve` |
| `6` | `S3_RESERVE_6` | `GPIO` | `reserve` |
| `7` | `S3_RESERVE_7` | `GPIO` | `reserve` |
| `8` | `S3_RESERVE_8` | `GPIO` | `reserve` |
| `9` | `LCD_DB1` | `LCD_CAM_TX` | `out` |
| `10` | `S3_RESERVE_10` | `GPIO` | `reserve` |
| `11` | `S3_RESERVE_11` | `GPIO` | `reserve` |
| `12` | `S3_RESERVE_12` | `GPIO` | `reserve` |
| `13` | `S3_RESERVE_13` | `GPIO` | `reserve` |
| `14` | `S3_HUB_D1` | `SPI3` | `io` |
| `15` | `S3_RESERVE_15` | `GPIO` | `reserve` |
| `16` | `S3_RESERVE_16` | `GPIO` | `reserve` |
| `17` | `LCD_WR_N` | `LCD_CAM_TX` | `out` |
| `18` | `LCD_DB2` | `LCD_CAM_TX` | `out` |
| `19` | `S3_USB_DM` | `USB_SERIAL_JTAG` | `io` |
| `20` | `S3_USB_DP` | `USB_SERIAL_JTAG` | `io` |
| `21` | `S3_HUB_D0` | `SPI3` | `io` |
| `38` | `LCD_DB3` | `LCD_CAM_TX` | `out` |
| `39` | `ENCODER_A` | `PCNT0` | `in` |
| `40` | `LCD_DB4` | `LCD_CAM_TX` | `out` |
| `41` | `LCD_DB5` | `LCD_CAM_TX` | `out` |
| `42` | `LCD_DB6` | `LCD_CAM_TX` | `out` |
| `43` | `S3_HUB_D2` | `SPI3` | `io` |
| `44` | `S3_HUB_D3` | `SPI3` | `io` |
| `45` | `LCD_DC` | `LCD_CAM_TX` | `out` |
| `46` | `LCD_DB7` | `LCD_CAM_TX` | `out` |
| `47` | `ENCODER_B` | `PCNT0` | `in` |
| `48` | `S3_HUB_SCK` | `SPI3` | `out` |

| GPIO переднего RP | Назначение |
|---|---|
| `0, 1, 2, 3, 4, 5` | exclusive point-to-point S3 quad-SPI D0..D3/SCK plus wired-OR UI_HUB_ALERT_N; no redundant chip-select wire |
| `7, 8, 9, 10, 11, 12` | C5 native 4-bit SDIO CLK/CMD/D0..D3 |
| `13, 14, 15, 16, 17` | dedicated SPI plus ALERT to RF RP |
| `18, 19, 20, 21, 22, 23` | nRF24 #0 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `24, 25, 26, 27, 28, 29` | nRF24 #1 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `30, 31, 32, 33, 34, 35` | nRF24 #2 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `36` | FAULT_KILL-qualified common nRF24 switched-rail request |
| `37, 38, 39, 40, 41, 44` | dedicated microSD SPI SCK/MOSI/MISO/CS plus power and detect |
| `42, 43` | dedicated fail-closed I2C1 controller bus to Pack and Safety MSPM0 mailboxes |
| `45` | LCD_TE direct front-local edge capture; Hub timestamps/alerts S3 without consuming another S3 GPIO |
| `46` | LCD_BL_PWM front-local backlight gate drive with the existing hardware reset-off pull-down |
| `6, 47` | uncommitted electrical reserve |

| GPIO заднего RP | Назначение |
|---|---|
| `0, 1, 2, 3, 6` | full-duplex codec/audio BCLK/WS/DOUT/DIN/ARM |
| `4, 5` | rear-local hardware I2C0 for codec, Si4732, Airband LO, headset and slow controls |
| `7, 8` | rear-local isolated M5 Unit PIO-I2C/PIO-UART/GPIO profile |
| `9, 10, 11, 23, 39, 42, 43` | CC1101 CS/GDO0/GDO2/power plus dedicated PIO SPI |
| `12, 13, 14, 30, 31, 40, 41, 44, 45, 46, 47` | exactly one U214/U219 profile: busy/IRQ/reset-or-power, hardware I2C1, GNSS-or-RF controls and dedicated SPI |
| `16, 17, 18, 20, 21, 22` | voice UART/PTT/audio-on, direct PTT input and ANY_TX diagnostic |
| `19, 24, 25, 26, 27` | dedicated SPI plus ALERT to front RP |
| `35` | AIR_RX_EN fail-low switched-domain and LT5560 enable control |
| `36` | AIR_RX_MODE direct-FM/SW versus converted-Airband selector; reset default direct |
| `15, 28, 29, 32, 33, 34, 37, 38` | uncommitted electrical reserve |

## Питание

Старый R1-лимит 2,5 А больше не действителен. Airband резервирует 150 мА / 0.5 Вт; новый H1 gate — не менее 3.8 А непрерывно и 4.2 А step с повторной проверкой buck/eFuse/индуктора/меди/тепла.

## Фабричный BOM-delta

| MPN | JLCPCB | Роль | Маршрут | Остаток | Цена, $ |
|---|---|---|---|---:|---:|
| `LT5560EDD#TRPBF` | `C462645` | active down-converting mixer | JLCPCB SMT | 165 | 14.5623 |
| `PGA-103+` | `C3008207` | 118-137-MHz low-noise gain | JLCPCB SMT | 1445 | 2.6104 |
| `SI5351A-B-GTR` | `C504891` | 112-MHz local oscillator | JLCPCB SMT | 37669 | 1.2199 |
| `HMC544AETR` | `C579555` | low-loss direct/converted receiver selector | JLCPCB SMT | 304 | 1.8112 |
| `SI4732-A10-GSR` | `C2155558` | existing FM/AM/SW/LW receiver reused for 6-25-MHz IF | existing R1 line; no incremental quantity | 547 | 2.8621 |

Incremental-стоимость активных компонентов: **`$20.2038`** before passives, PCB and assembly. Существующая строка Si4732 переиспользуется и не входит в эту дельту.

`BPF-A127+` не найден в каталоге JLCPCB (0 exact matches). Он используется как опубликованный эталон маски; production-вариант — серийная LC-лестница из фабричных passives, а не кастомная деталь. Все её MPN закрываются после H1 RF-синтеза и layout extraction.

## Честная граница возможностей

Включено:

- AM voice reception
- 25-kHz and 8.33-kHz channel plans
- scan and banks
- recording
- channel-activity history
- ACARS 2400-bps demodulation after the receiver

Исключено:

- Airband transmit
- simultaneous 19-MHz-wide spectrum capture
- VDL Mode 2
- certified VOR/ILS navigation

## Что закрывает H1-R2

- complete the canonical coordinate register for the existing Cap-Bus ESD, series, supervisor, bypass and evidence-aggregate bodies
- complete exact U219 support-passive values/MPNs and prove their courtyards inside the bounded placement islands
- obtain controlled U219 field-structure geometry or measure a received unit before locating the printed NFC pickup loop and DNP C0G bank
- measure the installed U219 RP-SMA antenna swept volume against the rear connector bank, enclosure and user hand access
