# M1 · межплатное соединение

[Главная](../README.md) · [Железо](hardware.ru.md) · [English](interconnect.md)

UI- и RF/power-платы соединяет одна точная прямая SMT-пара `Hirose FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` с рабочим зазором 11,00 мм. Все 80 контактов определены ниже; сквозных электрических выводов на внешних сторонах нет.

## Бюджет 80 контактов

`25` live signals · `14` main-power · `2` AON · `25` defined returns · `14` NC reserve

Основная шина использует **14** параллельных контактов и столько же основных возвратов. При continuous `3.75 А` получается `0.2679 А/контакт`; при step `4.25 А` — `0.3036 А/контакт` против рейтинга `0.4 А`.

## Механическая нагрузка

M1 выполняет только электрическую функцию и совмещение. Четыре точных 11,00-мм compression-stop, не менее двух противосдвиговых упоров корпуса и независимые захваты обеих PCB не дают платам разойтись или сдвинуться даже при одном ослабленном винте. Падение, установка аккумуляторов и изгиб корпуса не должны нагружать SMT-пайку M1.

## Принципиальная группировка

| Contacts | Назначение |
|---|---|
| `1–16` | 8 пар POWER_GROUND + 3V3_MAIN |
| `17–20` | 2 × AON_SAFE_3V3 с safety-return |
| `21–28` | выделенный SPI Hub↔RF RP + alert и возвраты |
| `29–31` | продуктовый USB 2.0 S3 D−/D+ + возврат |
| `32–34` | fail-closed I²C Pack/Safety + возврат |
| `35–36` | 75-омный FPV_CVBS + отдельный video-return |
| `37–40` | RUN, fault и UI thermal safety + возврат |
| `41–50` | 9 сигналов actual-TX evidence + safety-return |
| `51–54` | задний энкодер A/B/push + возврат |
| `55–64` | 10 резервных NC-контактов |
| `65–76` | 6 пар POWER_GROUND + 3V3_MAIN |
| `77–80` | 4 резервных NC-контакта |

<details><summary>Полная контактная карта</summary>

| Контакт | Сеть | Класс |
|---:|---|---|
| `1` | `POWER_GROUND` | `main_return` |
| `2` | `3V3_MAIN` | `main_power` |
| `3` | `POWER_GROUND` | `main_return` |
| `4` | `3V3_MAIN` | `main_power` |
| `5` | `POWER_GROUND` | `main_return` |
| `6` | `3V3_MAIN` | `main_power` |
| `7` | `POWER_GROUND` | `main_return` |
| `8` | `3V3_MAIN` | `main_power` |
| `9` | `POWER_GROUND` | `main_return` |
| `10` | `3V3_MAIN` | `main_power` |
| `11` | `POWER_GROUND` | `main_return` |
| `12` | `3V3_MAIN` | `main_power` |
| `13` | `POWER_GROUND` | `main_return` |
| `14` | `3V3_MAIN` | `main_power` |
| `15` | `POWER_GROUND` | `main_return` |
| `16` | `3V3_MAIN` | `main_power` |
| `17` | `AON_SAFE_3V3` | `aon_power` |
| `18` | `SAFETY_GROUND` | `safety_return` |
| `19` | `AON_SAFE_3V3` | `aon_power` |
| `20` | `SAFETY_GROUND` | `safety_return` |
| `21` | `POWER_GROUND` | `ipc_return` |
| `22` | `HUB_RF_ALERT_N` | `ipc` |
| `23` | `HUB_RF_CS_N` | `ipc` |
| `24` | `HUB_RF_SCK` | `ipc` |
| `25` | `POWER_GROUND` | `ipc_return` |
| `26` | `HUB_RF_MOSI` | `ipc` |
| `27` | `HUB_RF_MISO` | `ipc` |
| `28` | `POWER_GROUND` | `ipc_return` |
| `29` | `S3_USB_DM` | `usb2` |
| `30` | `S3_USB_DP` | `usb2` |
| `31` | `POWER_GROUND` | `usb_return` |
| `32` | `HUB_SAFE_I2C_SDA` | `control` |
| `33` | `HUB_SAFE_I2C_SCL` | `control` |
| `34` | `POWER_GROUND` | `control_return` |
| `35` | `FPV_CVBS` | `video_75ohm` |
| `36` | `VIDEO_GROUND` | `video_return` |
| `37` | `RUN_PERMIT` | `safety` |
| `38` | `FAULT_ASSERT_N` | `safety` |
| `39` | `UI_ZONE_TEMP_ADC` | `safety_analog` |
| `40` | `SAFETY_GROUND` | `safety_return` |
| `41` | `EV_N0_S3` | `tx_evidence` |
| `42` | `EV_N1_C5` | `tx_evidence` |
| `43` | `EV_N2_NRF0` | `tx_evidence` |
| `44` | `EV_N3_NRF1` | `tx_evidence` |
| `45` | `EV_N4_NRF2` | `tx_evidence` |
| `46` | `EV_N7_IR` | `tx_evidence` |
| `47` | `SAFETY_GROUND` | `safety_return` |
| `48` | `EV_N5_CC` | `tx_evidence` |
| `49` | `EV_N6_VOICE` | `tx_evidence` |
| `50` | `EV_N8_LORA_EXT` | `tx_evidence` |
| `51` | `ENCODER_A` | `ui` |
| `52` | `ENCODER_B` | `ui` |
| `53` | `UI_ENCODER_PUSH_N` | `ui` |
| `54` | `POWER_GROUND` | `ui_return` |
| `55` | `NC_55` | `reserve` |
| `56` | `NC_56` | `reserve` |
| `57` | `NC_57` | `reserve` |
| `58` | `NC_58` | `reserve` |
| `59` | `NC_59` | `reserve` |
| `60` | `NC_60` | `reserve` |
| `61` | `NC_61` | `reserve` |
| `62` | `NC_62` | `reserve` |
| `63` | `NC_63` | `reserve` |
| `64` | `NC_64` | `reserve` |
| `65` | `POWER_GROUND` | `main_return` |
| `66` | `3V3_MAIN` | `main_power` |
| `67` | `POWER_GROUND` | `main_return` |
| `68` | `3V3_MAIN` | `main_power` |
| `69` | `POWER_GROUND` | `main_return` |
| `70` | `3V3_MAIN` | `main_power` |
| `71` | `POWER_GROUND` | `main_return` |
| `72` | `3V3_MAIN` | `main_power` |
| `73` | `POWER_GROUND` | `main_return` |
| `74` | `3V3_MAIN` | `main_power` |
| `75` | `POWER_GROUND` | `main_return` |
| `76` | `3V3_MAIN` | `main_power` |
| `77` | `NC_77` | `reserve` |
| `78` | `NC_78` | `reserve` |
| `79` | `NC_79` | `reserve` |
| `80` | `NC_80` | `reserve` |

</details>

> Источник истины — `hardware/architecture/h0-r2-rebaseline.json`; таблица генерируется из него.
