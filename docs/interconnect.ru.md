# Межплатное соединение M1

[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](interconnect.md)

Две платы соединяет одна точная 80-контактная пара с рабочим межплатным расстоянием 11 мм: `Hirose FX8C-80P-SV1(92)` на UI-плате и `Hirose FX8C-80S-SV5(92)` на RF/power-плате. Шаг — 0,6 мм, паспортная скорость — 8 Гбит/с, ток одного контакта — до 0.4 А; разъём не является механическим крепежом корпуса.

## UI/control-плата

- Вычислители: `ESP32-S3-WROOM-1U-N16R8` управляет UI, экраном, картой памяти и аудио; `ESP32-C5-WROOM-1U-N8R8` — собственными диапазонами 2,4/5 ГГц и IR.
- Интерфейсы: `HMX035CTFT-001 (QDtech schematic assembly marking)`, microSD, `Everest Semiconductor ES8311`, `Si4732-A10-GSR`, наушники, D-pad, BACK и OPT.
- Локальная безопасность: аппаратный сброс S3/C5, IR-гейт и аналоговое подтверждение передачи S3/C5/IR.
- Обслуживание C5: отдельный data-only USB-C `GCT USB4105-GF-A`.

## RF/power-плата

- Радиодомен реального времени: `SC1512-A4`, три `Ebyte E01-ML01IPX`, `CC1101RGPR` и `NiceRF SA518`.
- Внешние модули: съёмный `M5Stack U214 Cap LoRa-1262` на точном вертикальном `Samtec SSW-107-02-S-D` поднятой задней планки и независимый порт M5 Unit на точном `1125R-SMT-4P`.
- Питание и основной USB-C: `JAE DX07S016JA1R1500`, защита `Texas Instruments TPD4S201RUKR`, USB-PD `Texas Instruments TPS25751DREFR`, заряд, аккумуляторы и все преобразователи питания.
- Аудио на задней плате: микрофон `Same Sky CMEJ-0413-42-SMT-TR` с локальным смещением, дифференциальный усилитель `Diodes Incorporated PAM8302AASCR` и динамик `PUI Audio AS02404PO`.
- Задние органы управления: F1/F2, энкодер и PTT; единственный боковой RUN/KILL одновременно задаёт safety-состояние и малотоковую команду источнику.
- Локальная безопасность: `Texas Instruments MSPM0C1106SDGS20R`, `Texas Instruments TPS3435CAKAGDDFR`, защёлка FAULT_KILL, три температурные зоны, аппаратные гейты и физическое подтверждение передачи.

## Почему такое разделение

- Сырой VBUS, согласованное повышенное напряжение USB-PD, зарядное устройство и аккумуляторы остаются на RF/power-плате.
- Класс-D усилитель остаётся рядом с динамиком; через M1 проходит только низкоуровневый дифференциальный аудиосигнал.
- Микрофон и его цепь смещения находятся на RF/power-плате; MIC_RAW проходит через M1 рядом с AUDIO_GROUND к расположенным на UI-плате селекторам записи и передачи.
- Аналоговые выходы детекторов передачи и IR-несущая обрабатываются на своей плате; через M1 проходят только цифровые признаки передачи.
- RUN/KILL, независимый watchdog, safety-контроллер и защёлка FAULT_KILL расположены на RF/power-плате; на UI-плату передаются RUN_PERMIT, раздельный reset S3, температура UI и read-only status.
- F1/F2 и энкодер используют пять прямых входных/фазных контактов M1; PTT остаётся локальным для RP/voice; два контакта M1 зарезервированы и оставлены NC.

## Бюджет контактов

- Всего 80 контактов; 2 зарезервированы и физически не подключены.
- 8 × `3V3_MAIN`, 2 × `AON_SAFE_3V3`.
- 22 силовых возвратов, 3 аудиовозврата и 2 возврата безопасности.
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
| `29` | `UI_F1_N` | RF→UI | `control` |
| `30` | `POR_N` | RF→UI | `safety` |
| `31` | `POWER_GROUND` | return | `return` |
| `32` | `RUN_PERMIT` | RF→UI | `safety` |
| `33` | `UI_F2_N` | RF→UI | `control` |
| `34` | `RF_RESET_KILL_GATE` | RF→UI | `safety` |
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
| `48` | `MIC_RAW` | RF→UI | `audio` |
| `49` | `AUDIO_GROUND` | return | `return` |
| `50` | `UI_ENCODER_PUSH_N` | RF→UI | `control` |
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
| `73` | `ENCODER_A` | RF→UI | `control` |
| `74` | `ENCODER_B` | RF→UI | `control` |
| `75` | `S3_RESET_KILL_GATE` | RF→UI | `safety` |
| `76` | `UI_ZONE_TEMP_ADC` | UI→RF | `analog` |
| `77` | `FAULT_LATCH_SENSE` | RF→UI | `safety` |
| `78` | `SPEAKER_AMP_EN` | UI→RF | `control` |
| `79` | `RESERVED_79` | reserved | `reserved` |
| `80` | `RESERVED_80` | reserved | `reserved` |

Восемь параллельных контактов `3V3_MAIN` дают паспортный потолок 3,2 А, но допустимый ток готового устройства определяется только измерением нагрева разъёма при одновременной нагрузке. Два резервных контакта остаются физически не подключёнными.
