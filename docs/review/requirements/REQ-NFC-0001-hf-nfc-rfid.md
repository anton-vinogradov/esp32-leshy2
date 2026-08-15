# REQ-NFC-0001 — HF NFC/RFID read, write, analysis and emulation contract

- Статус набора: **На ревью; ожидается решение `IMP-0005`**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-NFC-01`–`C-NFC-10`, `OUT-06`, пересечения `C-X-01`, `C-X-02`, `C-X-07`, `C-X-11`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0013`; NFC backend decision pending
- Находки: `FND-0015`, `FND-0016`
- Условные входы реализации: accessory/port power, I²C timing, backend driver, storage/privacy, protocol corpus и HIL

## Граница документа

Этот набор отделяет обычную работу с собственными NFC tags от security analysis и действительно опасных credential operations. Наличие radio frontend не создаёт ключ, authorization либо совместимость с произвольной картой. Exact backend/revision и доказанный support matrix всегда видимы.

HF 13.56 MHz и LF 125 kHz — разные hardware paths. Payment APDU transport не означает payment application или EMVCo-certified product. Все third-level functions наследуют banner каждого входа по `DEC-0010` и затем проходят собственный target/action gate.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-NFC-01` | все | `conditional` | Основной | Accessory manager определяет exact SKU/hardware/IC/driver revision, power profile и proven capability bitmap. Неизвестный backend остаётся RF-off; branch скрывается или показывает причину. RFID2, U216 и PN7160 не смешиваются под общим именем. |
| `REQ-NFC-02` | `C-NFC-01` | `conditional` | Основной | Poll/detect/anticollision показывает technology, UID/identifier, ATQA/SAK/ATS либо protocol-native equivalents и confidence/source без выдуманного fingerprint. Privacy-safe display скрывает identifier на lock/screenshot/export по умолчанию. |
| `REQ-NFC-03` | `C-NFC-05`, `C-NFC-06`, `C-NFC-08` | `conditional` | Основной | Обычные owner-present Ultralight/NTAG/NDEF/Amiibo-read сценарии поддерживают bounded read, typed parse и raw view. Malformed/oversized TLV/NDEF не повреждает state. Amiibo identification не включает proprietary keys или false authenticity claim. |
| `REQ-NFC-04` | `C-NFC-05`, `C-NFC-06` | `conditional` | Основной destructive confirmation | NDEF/ordinary user-tag write строит полный preview, перечитывает tag, проверяет capacity/lock/password state и выполняет explicit hold-to-write. Credential sector, irreversible lock/OTP/config bits и unknown tag переводят действие в `REQ-NFC-09`, а не пишутся как ordinary NDEF. |
| `REQ-NFC-05` | `C-NFC-02` | `conditional` | Основной owner data / Лаборатория credential analysis | MIFARE Classic known-key authenticate/read и owner-data dump отделены от credential recovery. Keys никогда не логируются; sensitive dump требует scoped vault/export. Unknown/default key не считается разрешением на чужую карту. |
| `REQ-NFC-06` | `C-NFC-02`, `C-NFC-03`, `OUT-06` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Dictionary, nested и будущие darkside/hardnested recovery — отдельные tools с явной model/applicability, bounded attempts/time/temperature, resumable state и proof на synthetic/owned corpus. `hardnested/darkside` остаются disabled до license/provenance, on-device runtime/RAM/storage и repeatable success/failure benchmark. |
| `REQ-NFC-07` | `C-NFC-04` detect | `conditional` | Лаборатория | Magic-card generation/backdoor detection является read-only analysis с evidence/confidence; отсутствие ответа не доказывает genuine card. Probe не выполняет write/wipe и не сохраняет credential без consent. |
| `REQ-NFC-08` | `C-NFC-04`, `C-NFC-07` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | UID clone, magic-card format/wipe и restore доступны только для явно выбранной owned/authorized destination card. UI показывает source/destination, irreversible regions, before-image и verification; removal/mismatch aborts before next write. |
| `REQ-NFC-09` | `C-NFC-02`, `C-NFC-05`, `C-NFC-06` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Credential-sector restore, password/config/lock/OTP write и иные security-sensitive modifications используют per-operation allowlist, fresh preview/hold, power/removal recovery semantics и mandatory readback. Generic raw command не обходит этот gate. |
| `REQ-NFC-10` | `C-NFC-09` | `conditional` | Лаборатория | ISO14443-4/ISO-DEP, DESFire and generic APDU diagnostic records direction, timing, status and redacted payload. Payment-card inspection is privacy-gated, stores the minimum, never requests PIN/CVC or performs payment, and never claims terminal/card authenticity or EMVCo certification. |
| `REQ-NFC-11` | `OUT-06` A/B/F/V | `conditional` | Основной read/write | Advanced backend provides only corpus-proven NFC-A/B, NFC-F/FeliCa and NFC-V/ISO15693 discovery/read/write. A chip marketing list is not enough; exact tag families, rates, commands and known limitations are versioned. |
| `REQ-NFC-12` | `OUT-06` emulation | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Card/tag emulation is restricted to explicitly modeled NFC-A/NFC-F or other backend-proven test profiles and owner-supplied non-secret data. Each session shows emulated identifiers/data, expires/disarms on exit/STOP/reset/accessory loss, and never claims to reproduce protected credential/backend state. |
| `REQ-NFC-13` | `OUT-06` relay | `conditional`, later substage | Контролируемая зона, `AUTHORIZED_TARGET` | NFC relay requires two independently qualified frontend roles, authorization for both endpoints, visible link/latency/error state, hard session timeout and STOP. One mode-switching frontend is insufficient; implementation remains disabled until dual-unit bus/address, field isolation and real-reader latency HIL pass. |
| `REQ-NFC-14` | `OUT-06` LF | `defer` | Future expansion | LF 125 kHz is not provided by any HF backend. It is not `exclude-proven`, but requires a separate reader/emulator/antenna, protocol list, enclosure/coexistence and cost decision before becoming product scope. |
| `REQ-NFC-15` | `C-NFC-10` | `conditional` | Сквозной storage/privacy | Card/tag library stores typed records with provenance, owner label, consent/scope and secret classification. Sensitive dumps/keys are locked, redacted from crash/export by default, atomically updated and erased by factory reset; duplicate UID is not treated as identity proof. |
| `REQ-NFC-16` | все | `conditional` | Сквозной hardware | NFC accessory uses a qualified 5 V `PORT.A-NFC` with 3.3 V-safe I²C, bounded current, power/removal policy and bus recovery. Current 3.3 V `J40/J41` artifact does not pass (`FND-0015`). Shared-bus timing cannot starve safety/power/audio control. |
| `REQ-NFC-17` | все | `acceptance` | Сквозной | HIL covers card absent/present/collision, weak/canted/cycled field, cable/removal/brownout, malformed frames, write interruption, storage full, reset/update/STOP and exact success/failure classification without silent partial write or false clone/authentication claim. |

## Security split and default state

- Main starts RF polling only after a recognized accessory profile; no background UID logging.
- Lab read-only analysis may inspect owner-present credentials but never modifies or emulates them.
- Controlled Zone is required for recovery, clone, credential/destructive write, emulation and relay. Every entry shows the banner, and every operation separately binds target and action.
- Exiting, STOP, lock, reset, watchdog, power fault, accessory removal or session expiry disables emulation/relay and clears volatile keys/session data.
- CLI, import, saved task or external command cannot bypass level, target, destructive preview or vault policy.

## Acceptance corpus

- positive/negative cards for every claimed A/B/F/V family, including collisions and unsupported variants;
- known-key and deliberately vulnerable synthetic MIFARE fixtures; no success metric relies on third-party credentials;
- NDEF/TLV/APDU malformed, oversized, truncated and fuzz fixtures;
- ordinary write, credential write and irreversible-bit power-cut/removal matrix;
- emulation interoperability against at least two independent authorized readers per claimed profile;
- dual-frontend relay latency/error/STOP test only if `REQ-NFC-13` advances;
- 5 V rail/I²C waveform, shared-bus contention, RF range/orientation and enclosure/coexistence measurements.

## Стоимость без потери продукта

NFC остаётся external accessory, поэтому base BOM не получает frontend/antenna. На дату аудита RFID2 стоит $4.95, а U216 — $7; экономия $2.05 через RFID2 теряет FeliCa/ISO15693/emulation/custom-mode и не является zero-loss. U216 может убрать custom PN7160 PCB, antenna/matching и NCI port, но требует 5 V port correction и lifecycle gate exact NRND `ST25R3916-AQWT`.

## Первичные источники

- [M5Stack Unit NFC U216 documentation](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack M5Unit-NFC MIT library and support matrix](https://github.com/m5stack/M5Unit-NFC)
- [M5Stack RFID2 U031-B documentation](https://docs.m5stack.com/en/unit/rfid2)
- [STMicroelectronics ST25R3916 product page](https://www.st.com/en/nfc/st25r3916.html)
- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
- [NXP PN7160/PN7161 datasheet](https://www.nxp.com/docs/en/data-sheet/PN7160_PN7161.pdf)
