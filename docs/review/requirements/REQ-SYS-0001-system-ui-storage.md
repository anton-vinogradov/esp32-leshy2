# REQ-SYS-0001 — System/UI/storage platform contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-SYS-01`–`C-SYS-11`, `C-X-01`, `C-X-02`, `C-X-09`, `C-HWX-01`, `C-HWX-03`, `C-HWX-04`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0006`, `DEC-0008`–`DEC-0013`
- Открытые архитектурные входы: `FND-0001`–`FND-0003`, `FND-0006`–`FND-0008`

## Граница документа

Этот набор определяет пользовательский результат, safety-инварианты и проверяемые критерии. Он не принимает GUI toolkit, RTOS, S3↔C5 transport, USB composite layout, pin-map, количество PCA9555, файловую систему или конкретную реализацию STOP. Такие решения относятся к этапам 3–8.

`conditional` означает принятую целевую возможность, реализация которой зависит от явно названного hardware/accessory/architecture prerequisite. Это не заявление о готовности текущего legacy-артефакта.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-SYS-01` | `C-SYS-01` | `include` | Основной | Launcher/home, единая навигация, status bar и настройки. Экран постоянно различает текущий уровень, armed/disarmed, commanded TX и доступную actual-TX индикацию. |
| `REQ-SYS-02` | `C-SYS-02` | `conditional` | Основной | Touch, физические кнопки/encoder и экранный ввод дают полное управление без телефона. Shortcut не является единственным путём; обычный выбор списка не запускает TX. Физическая схема и pins ждут этап 3/`DEC-0012`. |
| `REQ-LAB-USB-01` | `C-SYS-03` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | USB HID/DuckyScript допускается только для явно разрешённого host. Нет autorun при boot/connect/restore; каждый запуск отдельно вооружается и подтверждается, отображает прогресс и прекращает новые HID reports по STOP/disconnect. Уже отправленные host-команды необратимы, что явно показывается до запуска. |
| `REQ-SYS-03` | `C-SYS-04` | `include` | Основной с наследованием per-command gates | USB service предоставляет serial console и управляемый экспорт storage. CLI/deep link не обходят Main/Lab/Controlled-Zone gates. USB MSC получает эксклюзивное владение носителем либо read-only snapshot; одновременная запись host и firmware запрещена. Одновременность HID/CDC/MSC не обещается до endpoint/PHY audit этапа 3. |
| `REQ-SYS-04` | `C-SYS-05` | `conditional` | Основной maintenance | Обновления S3 поддерживают проверяемые Wi-Fi и removable-media пути; C5 обновляется через выбранный этапом 3 transport, а не legacy-only `SPI3`. Все штатно устанавливаемые S3/C5 images имеют owner-authorized signature/open manifest, проверяются целевым MCU и используют validation/rollback. Update требует power margin, запрещает TX и после reboot запускает все TX off/Lab disarmed. Hardware lockdown остаётся отдельным opt-in по `DEC-0013`. |
| `REQ-SYS-05` | `C-SYS-06` | `include` | Основной | File manager, config import/export и offline databases используют versioned schemas, bounded parsing, atomic replace/recovery и явный результат ошибок. Import не может включить TX, подавить safety gates или незаметно восстановить armed state. |
| `REQ-SYS-06` | `C-SYS-07` | `include` | Основной | Battery/charge state, sleep и управляемые peripheral states видимы и проверяемы. Sleep, brownout, low-battery shutdown, watchdog и wake сначала обеспечивают TX-off/disarm; внезапный master-off учитывается периодическим durable flush, а не обещанием всегда успеть записать данные при brownout. |
| `REQ-SYS-07` | `C-SYS-08`, `C-X-01` | `conditional` | Сквозной safety | Display/WS2812/buzzer сообщают status/warning, но не заменяют фактическую TX-индикацию. Quiet/dim theme может отключить обычные эффекты, но не скрывает active-TX и critical safety state. Аппаратный proof actual-TX/STOP остаётся этапам 3–9 и `FND-0007`. |
| `REQ-SYS-08` | `C-SYS-09` | `conditional` | Основной | Expansion manager показывает только квалифицированные accessory profiles и capability descriptor. `PORT.C` GPS v1.1, U214/`EXT-RF14` и generic Grove I²C не смешиваются в blanket M5 compatibility. Подключение под питанием разрешается только профилю с доказанным hot-swap; иначе UI требует power-off. |
| `REQ-SYS-09` | `C-SYS-10` | `conditional` | Основной | Audio routing реализует `DEC-0009`: source/off, amp/mute, jack behavior и цифровые codec modes при сохранении hardware-default analog listening/voice. Reset/failure MCU или codec не должен оставлять случайный loud output либо ломать базовый analog path. Pins ждут сводного budget этапа 3. |
| `REQ-SYS-10` | `C-SYS-11` | `include` + dev-only split | Основной maintenance | Device info, bounded self-test, fault history, crash/core-dump export и factory reset входят в продукт. Dump/export не выдаёт signing keys или сохранённые credentials без отдельного protected flow. Factory reset требует destructive confirmation, стирает пользовательские secrets/state и возвращает install pledge + все safety defaults. Произвольный kill/start RTOS tasks не является пользовательской функцией; scheduler diagnostics относится к dev/service build этапа 7. |
| `REQ-SYS-11` | `C-X-01`, `C-X-02` | `include` | Сквозной safety | STOP, long-BACK, reset, shutdown, update, lock и session expiry применяют `DEC-0003`/`DEC-0010`. Ни launcher, favorites, recent, CLI, import, USB или companion path не обходят pledge, level-entry и per-tool arming. |
| `REQ-SYS-12` | `C-X-09` | `conditional` | Основной | On-device text input всегда доступен. BLE phone input может быть дополнительным backend после решения `FND-0002`; отсутствие телефона или BLE не блокирует настройку и safe operation. Wi-Fi portal может рассматриваться на этапе 7, но не должен молча занимать radio во время несовместимой задачи. |
| `REQ-SYS-13` | `C-HWX-01` | `conditional` | Основной | Backlight timeout/manual dim входят при наличии управляемого dimming path; ambient auto-brightness требует отдельного sensor/profile. Until then on/off control is not described as brightness control. |
| `REQ-SYS-14` | `C-HWX-03`, `C-HWX-04` | `acceptance`, не feature | Сквозной | UI latency, waterfall continuity и bounded SD/radio contention задаются измеримыми budgets на этапах 7–9. Dirty rectangles, DMA, double buffering и конкретный bus arbiter — допустимые способы, но не продуктовые обещания сами по себе. |

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
- accessory test проверяет wrong profile, address conflict, removal and power behavior до заявления hot-swap;
- storage fuzz/schema tests отклоняют malformed/oversized config, database и script без partial apply;
- diagnostics test подтверждает secret redaction и полный возврат onboarding/safety state после factory reset.

## Решённый gate

`IMP-0011` принят как `A-open` в `DEC-0013`: штатные S3/C5 updates подписаны и откатываемы, ключи контролирует владелец, build/signing остаются offline/open, developer firmware разрешена, а необратимый production Secure Boot/Flash Encryption profile требует отдельного будущего решения.

## Первичные технические источники

- [Espressif ESP32-S3 USB Device Stack: HID, CDC, MSC, endpoint/PHY constraints](https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html)
- [ESP-IDF OTA: image validation, rollback, anti-rollback and signed updates](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html)
- [ESP32-S3 Secure Boot v2 and signed verification without hardware Secure Boot](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/security/secure-boot-v2.html)
