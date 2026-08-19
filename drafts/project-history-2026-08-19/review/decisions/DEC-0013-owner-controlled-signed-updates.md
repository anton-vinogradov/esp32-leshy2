# DEC-0013 — открытая owner-controlled цепочка подписанных обновлений

- Статус: **Принято владельцем проекта**
- Этап: 2 — System/UI/storage product-security baseline
- Дата принятия: 2026-08-16
- Принимает: `IMP-0011`, вариант `A-open`
- Затрагивает: S3/C5 firmware, OTA/SD/USB update, recovery, build/release и target README

## Контекст

Подпись обновления и закрытое устройство — разные свойства. Подпись доказывает целостность и происхождение образа в обычном update flow. Закрытость появляется, если только производитель владеет допустимым ключом либо hardware lockdown лишает владельца собственного build/flash path.

Leshy2 должен защищать safety-гейты от подменённого Wi-Fi/SD/C5 image, не превращаясь в vendor-controlled appliance.

## Решение

1. Все образы и data packages, устанавливаемые штатными OTA/SD/USB update paths, имеют открытый versioned manifest с target MCU, hardware revision, version/security version, size/hash и cryptographic signature.
2. S3 проверяет общий package до применения или передачи C5 image. C5 независимо проверяет предназначенный ему image перед activation; доверие только к S3 transport недостаточно.
3. Оба MCU используют working-image rollback/recovery и подтверждают новый image только после first-boot self-test. После update/recovery все TX off, Lab/Controlled Zone disarmed, а сохранённое arming не восстанавливается.
4. Корень доверия принадлежит владельцу устройства. Формат manifest, build и offline signing tools открыты; private keys не находятся в репозитории, firmware, устройстве или обязательном облачном сервисе.
5. Владелец может собирать и подписывать firmware собственным ключом. Vendor-only signing key, обязательный vendor cloud и запрет owner firmware не допускаются.
6. Отдельный явно маркированный `DEVELOPMENT / UNTRUSTED` lifecycle сохраняет локальную разработку и физическую перепрошивку. Он не может маскироваться под production-trusted state.
7. Hardware Secure Boot, Flash Encryption, eFuse key enrollment/revocation, debug lockdown и hardware anti-rollback **не включаются этим решением**. Это отдельный opt-in gate этапов 3/7 только после threat model, owner-key enrollment, backup/rotation и доказанного brick-safe recovery.
8. Если появится factory production profile, до необратимой блокировки он обязан позволить owner-controlled enrollment/transition. Включение необратимого режима сопровождается отдельным предупреждением и проверкой recovery/key backup.

## Не выбранные варианты

- Немедленный обязательный production Secure Boot v2 + Flash Encryption отклонён как преждевременный до recovery/lifecycle proof.
- Необязательная подпись штатных updates отклонена: она не защищает safety-контракты от подмены обычного update artifact.

## Критерии последующего proof

- wrong-target, corrupted, unsigned, revoked и недопустимо downgraded images отклоняются до activation;
- power-cut matrix покрывает download/write/switch/first boot обоих MCU;
- owner может полностью offline собрать, подписать, проверить и установить собственный image по опубликованной инструкции;
- потеря vendor infrastructure не лишает владельца update/recovery;
- developer/production state видимы в UI и diagnostic export;
- включение любого hardware lockdown невозможно без отдельного принятого решения и проверенного runbook.

## Первичные источники

- [ESP-IDF OTA: validation, rollback, anti-rollback and signed updates](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html)
- [ESP32-S3 Secure Boot v2 and signed verification without hardware Secure Boot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/secure-boot-v2.html)
- [ESP-IDF security overview](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/security.html)
