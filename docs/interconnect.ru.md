# Межплатное соединение M1

[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](interconnect.md)

Две платы соединяет одна точная 80-контактная пара с рабочим межплатным расстоянием 11 мм: `Hirose FX8C-80P-SV1(92)` на UI-плате и `Hirose FX8C-80S-SV5(92)` на RF/power-плате. Шаг — 0,6 мм, паспортная скорость — 8 Гбит/с, ток одного контакта — до 0.4 А; разъём не является механическим крепежом корпуса.

## UI/control-плата

- Вычислители: `ESP32-S3-WROOM-1U-N16R2` управляет UI, экраном, картой памяти и аудио; `ESP32-C5-WROOM-1U-N8R8` — собственными диапазонами 2,4/5 ГГц и IR.
- Интерфейсы: `HMX035CTFT-001 (QDtech schematic assembly marking)`, microSD, `Everest Semiconductor ES8311`, `Si4732-A10-GSR`, микрофон, наушники и все органы управления.
- Локальная безопасность: формирователь и защёлка STOP/RE-ARM, аппаратный сброс S3/C5, IR-гейт и аналоговое подтверждение передачи S3/C5/IR.
- Обслуживание C5: отдельный data-only USB-C `GCT USB4105-GF-A`.

## RF/power-плата

- Радиодомен реального времени: `SC1512-A4`, три `Ebyte E01-ML01IPX`, `CC1101RGPR` и `NiceRF SA518`.
- Внешние модули: съёмный `M5Stack U214 Cap LoRa-1262` и независимый порт M5 Unit.
- Питание и основной USB-C: `JAE DX07S016JA1R1500`, защита `Texas Instruments TPD4S201RUKR`, USB-PD `Texas Instruments TPS25751DREFR`, заряд, аккумуляторы и все преобразователи питания.
- Выход звука: дифференциальный усилитель `Diodes Incorporated PAM8302AASCR` и динамик `PUI Audio AS02404PO`.
- Локальная безопасность: аппаратные гейты nRF/CC/voice/расширений, сброс RP и аналоговое подтверждение передачи nRF/CC/voice.

## Почему такое разделение

- Сырой VBUS, согласованное повышенное напряжение USB-PD, зарядное устройство и аккумуляторы остаются на RF/power-плате.
- Класс-D усилитель остаётся рядом с динамиком; через M1 проходит только низкоуровневый дифференциальный аудиосигнал.
- Аналоговые выходы детекторов передачи и IR-несущая обрабатываются на своей плате; через M1 проходят только цифровые признаки передачи.
- Защёлка STOP/RE-ARM расположена рядом с органами управления; на вторую плату передаётся цифровое аппаратное разрешение.

## Бюджет контактов

- Всего 80 контактов; 9 зарезервированы и физически не подключены.
- 8 × `3V3_MAIN`, 2 × `AON_SAFE_3V3`.
- 23 силовых возвратов, 2 аудиовозврата и 2 возврата безопасности.
- Сырой VBUS/PD, ток аккумуляторов, аналоговые выходы TX-детекторов, IR-несущая и выходы класса D через M1 не проходят.

## Точная карта контактов

| Контакт | Цепь | Направление | Класс |
|---:|---|---|---|
| `1` | `POWER_GROUND` | return | `return` |
| `2` | `RP_ALERT_N` | RF→UI | `ipc_high_speed` |
| `3` | `POWER_GROUND` | return | `return` |
| `4` | `S3_RP_IPC_CS_N` | UI→RF | `ipc_high_speed` |
| `5` | `S3_RP_IPC_SCK` | UI→RF | `ipc_high_speed` |
| `6` | `POWER_GROUND` | return | `return` |
| `7` | `S3_RP_IPC_MOSI` | UI→RF | `ipc_high_speed` |
| `8` | `S3_RP_IPC_MISO` | RF→UI | `ipc_high_speed` |
| `9` | `POWER_GROUND` | return | `return` |
| `10` | `S3_USB_DM` | bidirectional | `usb2_high_speed` |
| `11` | `S3_USB_DP` | bidirectional | `usb2_high_speed` |
| `12` | `POWER_GROUND` | return | `return` |
| `13` | `SYS_I2C_SDA` | bidirectional | `control` |
| `14` | `SYS_I2C_SCL` | bidirectional | `control` |
| `15` | `POWER_GROUND` | return | `return` |
| `16` | `SYS_INT_N` | RF→UI | `control` |
| `17` | `CC_BAND_V1_REQ` | UI→RF | `control` |
| `18` | `CC_BAND_V2_REQ` | UI→RF | `control` |
| `19` | `POWER_GROUND` | return | `return` |
| `20` | `U214_I2C_READY` | RF→UI | `control` |
| `21` | `VOICE_DOMAIN_REQ` | UI→RF | `control` |
| `22` | `VOICE_HL_RELEASE_REQ` | UI→RF | `control` |
| `23` | `POWER_GROUND` | return | `return` |
| `24` | `U214_5V_REQ` | UI→RF | `control` |
| `25` | `UNIT_5V_REQ` | UI→RF | `control` |
| `26` | `POWER_FAULT_N` | RF→UI | `control` |
| `27` | `POWER_GROUND` | return | `return` |
| `28` | `UNIT_READY` | RF→UI | `control` |
| `29` | `PTT_BUTTON_N` | UI→RF | `control` |
| `30` | `POR_N` | RF→UI | `safety` |
| `31` | `POWER_GROUND` | return | `return` |
| `32` | `RUN_PERMIT` | UI→RF | `safety` |
| `33` | `TX_KILL` | UI→RF | `safety` |
| `34` | `RESET_KILL_GATE` | UI→RF | `safety` |
| `35` | `POWER_GROUND` | return | `return` |
| `36` | `EV_N0_S3` | UI→RF | `tx_evidence` |
| `37` | `EV_N1_C5` | UI→RF | `tx_evidence` |
| `38` | `EV_N7_IR` | UI→RF | `tx_evidence` |
| `39` | `POWER_GROUND` | return | `return` |
| `40` | `C5_RF_TX_EVIDENCE_N` | RF→UI | `tx_evidence` |
| `41` | `IR_TX_EVIDENCE_N` | RF→UI | `tx_evidence` |
| `42` | `RX_SA518_AFOUT_ISOLATED` | RF→UI | `audio` |
| `43` | `AUDIO_GROUND` | return | `return` |
| `44` | `VOICE_MIC_SELECTED_MAIN` | UI→RF | `audio` |
| `45` | `AUDIO_GROUND` | return | `return` |
| `46` | `SPEAKER_SELECTED_P` | UI→RF | `audio` |
| `47` | `SPEAKER_SELECTED_N` | UI→RF | `audio` |
| `48` | `SPEAKER_AMP_EN` | UI→RF | `control` |
| `49` | `POWER_GROUND` | return | `return` |
| `50` | `RESERVED_50` | reserved | `reserved` |
| `51` | `3V3_MAIN` | rail | `power` |
| `52` | `3V3_MAIN` | rail | `power` |
| `53` | `3V3_MAIN` | rail | `power` |
| `54` | `3V3_MAIN` | rail | `power` |
| `55` | `3V3_MAIN` | rail | `power` |
| `56` | `3V3_MAIN` | rail | `power` |
| `57` | `3V3_MAIN` | rail | `power` |
| `58` | `3V3_MAIN` | rail | `power` |
| `59` | `POWER_GROUND` | return | `return` |
| `60` | `POWER_GROUND` | return | `return` |
| `61` | `POWER_GROUND` | return | `return` |
| `62` | `POWER_GROUND` | return | `return` |
| `63` | `POWER_GROUND` | return | `return` |
| `64` | `POWER_GROUND` | return | `return` |
| `65` | `AON_SAFE_3V3` | rail | `power` |
| `66` | `AON_SAFE_3V3` | rail | `power` |
| `67` | `SAFETY_GROUND` | return | `return` |
| `68` | `SAFETY_GROUND` | return | `return` |
| `69` | `POWER_GROUND` | return | `return` |
| `70` | `POWER_GROUND` | return | `return` |
| `71` | `POWER_GROUND` | return | `return` |
| `72` | `POWER_GROUND` | return | `return` |
| `73` | `RESERVED_73` | reserved | `reserved` |
| `74` | `RESERVED_74` | reserved | `reserved` |
| `75` | `RESERVED_75` | reserved | `reserved` |
| `76` | `RESERVED_76` | reserved | `reserved` |
| `77` | `RESERVED_77` | reserved | `reserved` |
| `78` | `RESERVED_78` | reserved | `reserved` |
| `79` | `RESERVED_79` | reserved | `reserved` |
| `80` | `RESERVED_80` | reserved | `reserved` |

Восемь параллельных контактов `3V3_MAIN` дают паспортный потолок 3,2 А, но допустимый ток готового устройства определяется только измерением нагрева разъёма при одновременной нагрузке. Девять резервных контактов остаются физически не подключёнными.
