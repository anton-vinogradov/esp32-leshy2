# IMP-0011 — подписанная цепочка обновлений S3 и C5

- Статус: **Принято владельцем как `A-open`; см. `DEC-0013`**
- Этап решения: 2 — product security baseline; concrete lifecycle — этапы 3 и 7–10
- Связано: `C-SYS-05`, `REQ-SYS-04`, `DEC-0003`, `DEC-0010`, `FND-0001`, `FND-0008`
- Обнаружено: 2026-08-16

## Контекст

Legacy обещает OTA S3 по Wi-Fi/SD и OTA C5 по старому `SPI3`, но не определяет доверие к образу, rollback, key ownership и поведение после неудачного обновления. Для устройства с несколькими TX-path и Controlled Zone подмена firmware способна удалить все принятые UI/safety gates. Transport checksum доказывает только целостность передачи, но не происхождение образа.

ESP-IDF поддерживает проверку подписанного OTA без hardware Secure Boot, rollback после первого boot и anti-rollback. Полный Secure Boot v2 проверяет bootloader/application при каждом boot, но production eFuse/Flash Encryption profile ограничивает debug и recovery и требует отдельного lifecycle design.

## Принятый вариант `A-open`

Принят обязательный **signed-update baseline**, а необратимый production-lockdown решается позже:

1. Любой устанавливаемый S3 и C5 application/data image имеет manifest с target, hardware revision, version/security version, size/hash и cryptographic signature.
2. S3 проверяет package/manifest до доставки C5 image, но это не заменяет проверку подписи самим C5 перед activation.
3. Каждый MCU имеет working slot/recovery path и подтверждает новый image только после boot self-test; failure/power loss возвращает последний допустимый image.
4. После любого update/recovery все TX off, Lab/Controlled Zone disarmed, сохранённое arming не восстанавливается.
5. Private signing keys не находятся в репозитории или на устройстве; проект документирует owner-controlled key generation, backup, rotation and revocation.
6. Hardware Secure Boot v2, Flash Encryption, debug policy, eFuse programming и anti-rollback activation выбираются на этапах 3/7 после threat model и доказанного brick-safe recovery.
7. Developer builds остаются возможны через отдельный lifecycle/profile и явно показывают `DEVELOPMENT / UNTRUSTED`; они не маскируются под production image.
8. Build/signing tools и manifest открыты, owner может использовать собственные offline keys; vendor-only key/cloud запрещены.

Плюс: блокирует случайную или сетевую установку неподписанного образа уже без немедленного необратимого eFuse-решения и без закрытия owner firmware. Минус: появляется key-management process; от физического перепрограммирования flash этот baseline без hardware Secure Boot не защищает.

## Вариант B — сразу обязать production Secure Boot v2 + Flash Encryption

Сильнее против физической подмены и извлечения secrets, но преждевременно фиксирует provisioning/debug/recovery policy. Release configuration может отключить привычные ROM download/JTAG paths; ошибка в eFuse/key lifecycle способна сделать устройство невосстановимым обычным способом.

## Вариант C — подпись необязательна

Проще для разработки, но network/SD update не отличает авторизованный firmware от подменённого. Для продукта с активными TX/security функциями это неэквивалентная экономия и не рекомендуется.

## Критерии последующего proof

- negative tests отклоняют wrong target, corrupted, unsigned, revoked и downgraded images до activation;
- power-cut tests проходят на каждой фазе download/write/switch/first boot обоих MCU;
- C5 не доверяет только решению S3 и независимо отклоняет неподходящий image;
- recovery не загружает image ниже принятой security floor после её активации;
- build/release pipeline публикует reproducible metadata, signatures и SBOM без private keys;
- key-loss/rotation/revocation и developer-to-production transition имеют проверенный runbook;
- USB/UART/JTAG recovery фактически проверен для каждого выбранного lifecycle profile.

## Первичные источники

- [ESP-IDF OTA: rollback, anti-rollback and signed update verification](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html)
- [ESP32-S3 Secure Boot v2, key revocation and signed verification without hardware Secure Boot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/secure-boot-v2.html)
- [ESP-IDF security overview: Secure Boot, Flash Encryption and debug/download implications](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/security.html)
