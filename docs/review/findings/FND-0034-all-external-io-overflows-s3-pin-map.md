# FND-0034 — all external I/O on S3 overflows the zero-based pin map

- Статус: **Исправлено в `SYN-0001`/`PIN-0002`; учитывать в package comparison**
- Дата: 2026-08-16
- Найдено при: exact pin synthesis `SYN-2A`

## Несоответствие

Первая полная формулировка `SYN-2A` назначала S3 одновременно:

- два SDMMC endpoints, native USB и full-duplex I²S;
- display/touch/local UI;
- 3×nRF24 + CC1101 с безопасной control/event logic;
- U214 SPI/GNSS/Cap I²C;
- voice UART/PTT.

После исключения module-memory pins и сохранения strap/recovery semantics этот набор требует больше 36 выведенных GPIO `ESP32-S3-WROOM-1U-N16R2`. Простое использование общего latch clock не является исправлением: общий с radio SCK latch создаёт лишний байт при снятии выбранного `CSN`, а all-zero clear неверно задаёт active-low selects.

## Исправление без потери функций

- S3 сохраняет 3×nRF24, CC1101, display, audio, voice, UI, storage и application work;
- C5 использует свой свободный GP-SPI/I²C и два UART для U214, его GNSS и отдельного Unit GPS;
- U216 NFC остаётся на изолированном S3 I²C accessory path;
- C5→S3 передаёт уже framed LoRa/GNSS data через тот же 1-bit SDIO с приоритетами/loss semantics;
- U214 и Unit GPS имеют отдельные UART pairs, но policy всё равно допускает ровно один active GNSS backend.

`PIN-0002` даёт collision-free map: S3 использует 35/36 module GPIO, C5 — 21/21. Scope, STOP, independent recovery и full-function nRF не сокращены.

## Следствие

`SYN-2A` остаётся реализуемым candidate, но имеет почти нулевой pin reserve на обоих Espressif modules и более тяжёлый C5 IPC. Это отрицательный factor в atomic comparison, а не причина скрыто удалить U214, Unit GPS, voice или radio controls.
