# REQ-SYS-0001 — System/UI/storage platform contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-SYS-01`–`C-SYS-11`, `C-X-01`, `C-X-02`, `C-X-09`, `C-HWX-01`, `C-HWX-03`, `C-HWX-04`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0006`, `DEC-0008`–`DEC-0013`, `DEC-0038`, `DEC-0039`, `DEC-0043`
- Открытые архитектурные входы: `FND-0001`–`FND-0003`, `FND-0006`–`FND-0008`

## Граница документа

Этот набор определяет пользовательский результат, safety-инварианты и проверяемые критерии. Он не принимает GUI toolkit, RTOS, inter-target transport, USB composite layout, pin-map, expander count, файловую систему или конкретную реализацию STOP. Такие решения относятся к corrected `FLOW-0001` gates.

`conditional` означает принятую целевую возможность, реализация которой зависит от явно названного hardware/accessory/architecture prerequisite. Это не заявление о готовности текущего legacy-артефакта.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-SYS-01` | `C-SYS-01` | `include` | Основной | Launcher/home, единая навигация, status bar и настройки. Экран постоянно различает текущий уровень, armed/disarmed, commanded TX и доступную actual-TX индикацию. |
| `REQ-SYS-02` | `C-SYS-02` | `conditional` | Основной | Selected local control surfaces provide complete core field, safety, pairing/revoke, service and recovery operation without a phone. Dedicated physical safety/voice controls remain where separately required; touch, D-pad, encoder and action-key mix are G3 archetype variables. Permanent text keyboard is excluded by `DEC-0038`; ordinary list selection never starts TX. Exact mechanics and pins wait for G3–G7. |
| `REQ-LAB-USB-01` | `C-SYS-03` | `defer-release`, software-only exception | Контролируемая зона, `AUTHORIZED_TARGET` | `DEC-0039`: USB HID/DuckyScript may ship only after the radio/key core, over the already-required USB device/service path, in a mutually exclusive mode with no incremental base hardware or architecture score. Нет autorun при boot/connect/restore; каждый запуск для явно разрешённого host отдельно вооружается и подтверждается, отображает прогресс и прекращает новые HID reports по STOP/disconnect. Уже отправленные host-команды необратимы, что явно показывается до запуска. |
| `REQ-SYS-03` | `C-SYS-04` | `include` | Основной с наследованием per-command gates | USB service предоставляет serial console и управляемый экспорт storage. CLI/deep link не обходят Main/Lab/Controlled-Zone gates. USB MSC получает эксклюзивное владение носителем либо read-only snapshot; одновременная запись host и firmware запрещена. Одновременность HID/CDC/MSC не обещается до endpoint/PHY audit этапа 3. |
| `REQ-SYS-04` | `C-SYS-05` | `conditional` | Основной maintenance | Primary product firmware supports qualified Wi-Fi and removable-media update paths; every other selected programmable target uses its reviewed update transport rather than a legacy-only bus assumption. Every normally installable image has owner-authorized signature/open manifest, target-side verification and validation/rollback. Update requires power margin, prohibits TX and boots with all TX off/Lab disarmed. Hardware lockdown remains a separate opt-in under `DEC-0013`. |
| `REQ-SYS-05` | `C-SYS-06` | `include` | Основной | File manager, config import/export и offline databases используют versioned schemas, bounded parsing, atomic replace/recovery и явный результат ошибок. Import не может включить TX, подавить safety gates или незаметно восстановить armed state. |
| `REQ-SYS-06` | `C-SYS-07` | `include` | Основной | Battery/charge state, sleep и управляемые peripheral states видимы и проверяемы. Sleep, brownout, low-battery shutdown, watchdog и wake сначала обеспечивают TX-off/disarm; внезапный master-off учитывается периодическим durable flush, а не обещанием всегда успеть записать данные при brownout. |
| `REQ-SYS-07` | `C-SYS-08`, `C-X-01` | `conditional` | Сквозной safety | Display/WS2812/buzzer сообщают status/warning, но не заменяют фактическую TX-индикацию. Quiet/dim theme может отключить обычные эффекты, но не скрывает active-TX и critical safety state. Аппаратный proof actual-TX/STOP остаётся этапам 3–9 и `FND-0007`. |
| `REQ-SYS-08` | `C-SYS-09` | `conditional` | Основной | Expansion manager показывает только квалифицированные accessory profiles и capability descriptor. Unit Port A/B/C/custom, U214/Cardputer Cap и M5-Bus Module не смешиваются в blanket M5 compatibility. Native Grove не имеет identity pin: unknown profile remains unpowered; address scan alone is insufficient. Подключение под питанием разрешается только exact profile с доказанным hot-swap; иначе UI требует power-off. |
| `REQ-SYS-09` | `C-SYS-10` | `conditional` | Основной | Audio routing реализует `DEC-0009`: source/off, amp/mute, jack behavior и цифровые codec modes при сохранении hardware-default analog listening/voice. Reset/failure MCU или codec не должен оставлять случайный loud output либо ломать базовый analog path. Pins ждут сводного budget этапа 3. |
| `REQ-SYS-10` | `C-SYS-11` | `include` + dev-only split | Основной maintenance | Device info, bounded self-test, fault history, crash/core-dump export и factory reset входят в продукт. Dump/export не выдаёт signing keys или сохранённые credentials без отдельного protected flow. Factory reset требует destructive confirmation, стирает пользовательские secrets/state и возвращает install pledge + все safety defaults. Произвольный kill/start RTOS tasks не является пользовательской функцией; scheduler diagnostics относится к dev/service build этапа 7. |
| `REQ-SYS-11` | `C-X-01`, `C-X-02` | `include` | Сквозной safety | STOP, long-BACK, reset, shutdown, update, lock и session expiry применяют `DEC-0003`/`DEC-0010`. Ни launcher, favorites, recent, CLI, import, USB или companion path не обходят pledge, level-entry и per-tool arming. |
| `REQ-SYS-12` | `C-X-09` | `conditional` | Основной | Rare/long arbitrary text may require a locally paired owner phone under `DEC-0038`; the device exposes that dependency and never claims the workflow ready without it. Phone supplies characters only: full text/consequence is shown locally and local confirmation remains mandatory. Absence of phone never blocks core field/safety, pairing/revoke, service or recovery operation. Exact BLE versus other companion transport is selected at G7 without silently occupying a radio needed by an incompatible task. |
| `REQ-SYS-13` | `C-HWX-01` | `conditional` | Основной | Backlight timeout/manual dim входят при наличии управляемого dimming path; ambient auto-brightness требует отдельного sensor/profile. Until then on/off control is not described as brightness control. |
| `REQ-SYS-14` | `C-HWX-03`, `C-HWX-04` | `acceptance`, не feature | Сквозной | По `DEC-0043` critical state и первый menu feedback видимы за `≤100 ms`; waterfall использует bounded dirty/tiled updates, явно считает visual coalescing/drop и не отнимает raw radio/audio capture. Полный redraw публикуется как HIL result, но full-frame FPS не является product demand. Exact bus/renderer проверяются на этапах 7–9. |

## Обязательные UX/safety инварианты

1. Main, Lab и Controlled Zone различимы по навигации и постоянному состоянию; каждый вход в Controlled Zone заново выполняет `DEC-0010`.
2. `armed` и `transmitting` — разные состояния. Выбор цели/файла/скрипта никогда сам по себе не передаёт.
3. PTT активен только в foreground voice mode после допустимого arming; вне него нажатие инертно.
4. BACK в активном TX сначала прекращает текущую передачу; отдельный long-BACK вызывает software panic-stop из любого UI context. Это не заменяет будущий hardware STOP.
5. Любое combo дублируется видимым menu action. Destructive modal по умолчанию фокусирует cancel и сообщает необратимый эффект.
6. Commanded-TX banner остаётся видимым при уходе с экрана инструмента. Actual-TX indication не выводится только из application state.
7. После reset/update/factory reset/failed restore нельзя восстановить armed state, максимальную мощность или подтверждение Controlled Zone.
8. External command surfaces наследуют те же gates, что локальный UI; «это CLI/USB/import» не является отдельным разрешением.

## Проверки приёмки будущих этапов

- route test покрывает menu/search/favorites/recent/deep link/CLI/USB/restore для каждого уровня;
- reset matrix покрывает power-on, brownout, watchdog, crash, update success/failure и reset обоих MCU;
- USB MSC fault test доказывает отсутствие dual-writer corruption и восстановление после cable/power loss;
- update fault test прерывает download/write/first boot и проверяет working-image recovery и TX-off state;
- input test доказывает локальный путь для каждой essential action без phone/backend;
- accessory test проверяет wrong profile, no-ID/default-off, address conflict,
  UART/GPIO non-enumerability, power direction/backfeed, short/overcurrent,
  removal and power behavior до заявления hot-swap;
- storage fuzz/schema tests отклоняют malformed/oversized config, database и script без partial apply;
- diagnostics test подтверждает secret redaction и полный возврат onboarding/safety state после factory reset.

## Решённый gate

`IMP-0011` принят как `A-open` в `DEC-0013`: штатные updates каждого selected
programmable target подписаны и откатываемы, ключи контролирует владелец,
build/signing остаются offline/open, developer firmware разрешена, а
необратимый production lockdown profile требует отдельного будущего решения.

## Первичные технические источники

- [Espressif ESP32-S3 USB Device Stack: HID, CDC, MSC, endpoint/PHY constraints](https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html)
- [ESP-IDF OTA: image validation, rollback, anti-rollback and signed updates](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html)
- [ESP32-S3 Secure Boot v2 and signed verification without hardware Secure Boot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/secure-boot-v2.html)
