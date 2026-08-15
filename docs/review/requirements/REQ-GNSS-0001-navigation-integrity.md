# REQ-GNSS-0001 — navigation, logging, time and integrity contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-GPS-01`–`C-GPS-04`, `C-X-06`, `C-X-07`, `C-X-11`, GNSS-часть `C-UX-01`
- Обязательные решения: `DEC-0002`, `DEC-0005`, `DEC-0006`, `DEC-0008`, `DEC-0010`, `DEC-0013`, `DEC-0014`
- Условные входы реализации: pin/power/profile/parser/RF/HIL proof следующих этапов

## Граница документа

Этот набор определяет результат для пользователя, privacy/safety-инварианты и критерии приёмки. Он не выбирает окончательные UART GPIO, power switch, корпус/кабель, parser library, формат внутренней БД или конкретный online assistance provider.

Все GNSS-возможности условны подключённым квалифицированным аксессуаром. Поддерживаются M5Stack Unit GPS v1.1 `U032-V11` и AT6668 в U214; одновременно активен только один GNSS backend, sensor fusion не обещается. Совпадение AT6668 либо разъёма само по себе не делает другую ревизию совместимой.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-GNSS-01` | `C-GPS-01` | `conditional` | Основной | Expansion manager определяет только квалифицированный GNSS profile, показывает model/revision/firmware и активирует ровно один backend. Отсутствующий/неизвестный аксессуар не получает blanket compatibility; функции скрыты либо явно недоступны. |
| `REQ-GNSS-02` | `C-GPS-01` | `conditional` | Основной | Экран позиции показывает latitude/longitude, altitude, speed/course, UTC, fix type/validity, age, satellites и доступные accuracy/DOP indicators с единицами. Stale/invalid/unknown никогда не маскируется последним известным fix без явной маркировки. |
| `REQ-GNSS-03` | `C-GPS-01`, `C-GPS-02` | `conditional` | Основной | Навигация к waypoint показывает bearing/distance и погрешность, не называется safety-of-life navigation и не обещает карту/маршрутизацию до отдельного offline-map requirement. Waypoint import проходит bounded schema validation. |
| `REQ-GNSS-04` | `C-GPS-02` | `conditional` | Основной | Track log пишет timestamp, fix validity/quality и координаты в versioned internal format; GPX/KML export не теряет invalid gaps и не подставляет last-known location как live. Запись атомарна/восстанавливаема после power loss или снятия аксессуара. |
| `REQ-GNSS-05` | `C-GPS-02` | `conditional` | Основной | Локальные geofence alerts имеют видимую accuracy boundary, hysteresis/debounce и состояние unknown при недостаточном fix. Они не являются охранной/safety-of-life гарантией и не запускают TX без отдельного разрешённого сценария. |
| `REQ-GNSS-06` | `C-GPS-01`, `C-X-07` | `conditional` | Основной/System | RTC принимает GNSS time только при доказанной validity и разумном age; источник, uncertainty и last-sync видимы. Большой или обратный скачок не применяется молча, monotonic timers не зависят от wall-clock correction, а GNSS/NTP disagreement создаёт fault. |
| `REQ-GNSS-07` | `C-X-06`, `C-UX-01` | `conditional` | Основной с privacy gate | Geotag для capture/wardrive включается явно на сессию; перед стартом видны типы собираемых RF/location data и storage target. Export/delete доступны локально. Нет fix — записывается `unknown` с uncertainty, а не сохранённая позиция. Security-классификация самой RF-сессии наследуется независимо от GNSS. |
| `REQ-GNSS-08` | `C-GPS-01` | `conditional` | Основной maintenance | Конфигурирование ограничено allowlist конкретного profile: rate/message/constellation/start modes применяются транзакционно, читаются обратно и имеют recovery defaults. UBX/u-blox commands никогда не отправляются AT6668; online firmware update GNSS-модуля не входит автоматически. |
| `REQ-GNSS-09` | `C-GPS-03` | `conditional` | Основной/System | По `DEC-0014` быстрый старт формулируется backend-neutral. Проверенные assistance records имеют source, acquisition time, constellation, validity/expiry, size bound и integrity check; Wi-Fi не обязателен, допускается SD. Просроченные/неподходящие данные отклоняются, координаты наружу без согласия не отправляются. |
| `REQ-GNSS-10` | `C-GPS-04` | `conditional` | Основной, defensive readout | По `DEC-0014` receiver-reported jamming/spoofing отображается только после per-profile proof как `unknown / normal / suspected / strong` с источником и временем. Unsupported/timeout = unknown, не «угроз нет». Host heuristics отделены визуально и терминологически; ни один индикатор не объявляется гарантированным обнаружением или безопасностью координат. |
| `REQ-GNSS-11` | `C-X-11` | `conditional` | Основной | LED/buzzer/display alert сообщает loss/stale/integrity state, но quiet mode не может скрыть critical untrusted-fix state во время зависимой навигации/записи. Alert не включает RF transmission. |
| `REQ-GNSS-12` | все | `conditional` | Сквозной | Отключение, power fault, parser failure или смена backend закрывают/flush активного track log, переводят position/time/integrity в unavailable/unknown и безопасно останавливают зависимые операции. Снятие U214 дополнительно разоружает его LoRa TX по `IMP-0007`. |

## Обязательные acceptance-наборы

### Parser и состояние

- recorded NMEA 0183 4.1 traces обоих M5-профилей, incomplete/malformed/checksum-failed/oversized frames и fuzz corpus;
- no-fix → fix → stale → loss → reconnect без сохранения ложного trusted state;
- hot unplug допускается только после электрической квалификации; до неё проверяется controlled power-off removal;
- одновременное обнаружение Unit и U214 требует явного выбора одного backend и не смешивает epochs.

### Навигация, время и storage

- waypoint bearing/distance на эталонных координатах, antimeridian/poles и неверном input;
- GPX/KML round-trip, storage-full, power cut и removable-media ownership;
- geofence boundary jitter/hysteresis и unknown accuracy;
- GNSS week/date edge cases, leap/update input, backward/large jump и disagreement с NTP;
- privacy regression: last-known location не попадает в новую сессию без явного указания.

### Advanced profile по `DEC-0014`

- proof поддерживаемых CASTXT/CASBIN IDs на каждой product/revision/firmware;
- corrupt/stale/wrong-constellation assistance rejection и измеренный cold/warm/hot-start delta;
- receiver-reported normal/interference/spoof status mapping; RF-инъекция только в изолированной среде;
- unsupported, timeout и parser error дают `unknown`, не false-safe;
- LoRa TX/GNSS self-desense U214 измеряется на целевом enclosure/power profile.

## Стоимость без потери продукта

Base hardware не дорожает: GNSS остаётся внешним по `DEC-0006`/`DEC-0008`. Принятый `DEC-0014` добавляет firmware/HIL NRE, но не BOM; эта работа необходима, чтобы сохранить legacy-пользовательский результат честно. Удаление advanced-функций будет сокращением scope, а не экономией без потерь. Третий backend добавляется только при отдельном принятом требовании.

## Первичные источники

- [M5Stack Unit GPS v1.1](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [M5Stack U214](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [CASIC Multi-mode Satellite Navigation Receiver Protocol Specification v6.3.2](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1173/CASIC_Multi-mode_Satellite_Navigation_Receiver_Protocol_Specification.pdf)
