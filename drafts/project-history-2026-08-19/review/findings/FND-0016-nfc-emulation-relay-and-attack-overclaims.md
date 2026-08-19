# FND-0016 — NFC frontend не доказывает universal emulation, relay или key recovery

- Статус: **Закрыто на уровне требований: `DEC-0017`, `REQ-NFC-0001`, `REV-0002Q`**
- Серьёзность: capability/security overclaim
- Затрагивает: `C-NFC-02`–`C-NFC-09`, `OUT-06`, `IMP-0005`
- Обнаружено: 2026-08-16

## Несоответствия

| Legacy/раннее утверждение | Проверенная граница |
|---|---|
| RFID2 — только ISO14443A | WS1850S и актуальная страница M5 заявляют ISO14443 A/B, но текущий M5 software profile для RFID2 ограничен A/B detection и MFRC522-class workflow; конкретные B/APDU операции требуют on-target proof. |
| PN7160 снимает весь NFC ceiling | PN7160 добавляет A/B/F/V, P2P и Type 3/4 card emulation, но direct host design требует как минимум NCI transport, IRQ и VEN; обычный четырёхпроводный Grove I²C не является доказанным drop-in. |
| Card emulation означает клонирование любой карты | PN7160 emulates Type 3/4/ISO-DEP profiles; U216 официально заявляет NFC-A/NFC-F и демонстрирует Ultralight/NTAG-like profiles. Защищённый credential, secret keys и backend authorization этим не воспроизводятся автоматически. |
| Один frontend даёт NFC relay | Relay имеет одновременно две RF-роли и два физических endpoint. Нужны два независимых frontend, routing/latency/field-isolation proof и разрешение владельца обеих сторон. Один переключаемый reader/emulator этого не доказывает. |
| Наличие raw/custom mode доказывает nested/darkside/hardnested | Frontend может дать нужные low-level primitives, но алгоритм, nonce/card applicability, runtime/RAM/storage, provenance/license и corpus/HIL остаются отдельными доказательствами. |
| EMV-capable IC делает устройство платёжным терминалом | ST25R3916 silicon поддерживает EMVCo reader primitives; готовый Leshy2+Unit, application, antenna/system и payment stack не становятся EMVCo-certified и не получают право проводить payment transaction. |
| HF 13.56 MHz frontend покрывает LF | 125 kHz требует другой analog frontend и антенну; ни U216, ни RFID2, ни PN7160 его не добавляют. |

## Обязательное исправление

- Manifest/UI объявляет только exact accessory/revision и проверенные protocol/mode операции.
- Detection, read/write, emulation, credential recovery и relay получают раздельные requirement IDs и acceptance fixtures.
- Emulation, credential recovery, clone/destructive credential write и relay находятся в Контролируемой зоне с `AUTHORIZED_TARGET`; вход в зону не заменяет per-tool arming.
- 125 kHz LF и тяжёлые key-recovery варианты остаются `defer/conditional`, а не `exclude-proven` и не обещание.
- Payment-card APDU analysis отделяется от payment acceptance/compliance и минимизирует сохранение чувствительных данных.

## Первичные источники

- [M5Stack RFID2 U031-B](https://docs.m5stack.com/en/unit/rfid2)
- [M5Stack Unit NFC U216](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack M5Unit-NFC support matrix and MIT library](https://github.com/m5stack/M5Unit-NFC)
- [STMicroelectronics ST25R3916 product page](https://www.st.com/en/nfc/st25r3916.html)
- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
- [NXP PN7160 card-emulation note](https://www.nxp.com/docs/en/application-note/AN13861.pdf)

## Закрытие

`DEC-0017` выбрал U216 как первый target, не превратив frontend primitives в universal capability claims. `REQ-NFC-0001` разнёс read/write, recovery, emulation, relay, LF и payment semantics по отдельным гейтам; распространение проверено `REV-0002Q`. Hardware/driver/HIL остаются implementation proof, но requirement-level неоднозначность закрыта.
