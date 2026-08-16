# FND-0018 — fixed 38 kHz demodulator не доказывает universal IR learning

- Статус: **Закрыто на уровне требований: `DEC-0018`, `REQ-IR-0001`, `REV-0002S`**
- Серьёзность: capability overclaim
- Затрагивает: `C-IR-01`–`C-IR-05`, raw capture/replay, universal remote, code DB и HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy одновременно обещает raw capture, carrier-frequency select и universal remote, но текущий RX — `TSOP38238`:

- принимает около фиксированного центра 38 kHz;
- содержит band-pass, AGC и demodulator;
- выдаёт MCU огибающую, а не исходные carrier cycles.

Поэтому captured mark/space timings не содержат измеренную несущую. Firmware может угадать 38 kHz, получить carrier из известного protocol/DB/import либо попросить пользователя выбрать её, но не вправе называть это automatic carrier learning. Другие варианты семейства 30/33/36/40/56 kHz требуют другой MPN, а один `TSOP38238` не становится wideband sensor от настройки RMT.

## Реалистичный обход

Vishay `TSMP95000` выдаёт modulated carrier-out для code learning по 30–60 kHz. ESP32-C5 имеет два TX и два RX RMT channels, поэтому один robust demodulated receiver и один carrier-learning receiver технически могут работать как два независимых RX path. Это требует второго GPIO/RMT RX, нового MPN/passives, layout/window и common-capture HIL; архитектура принята в `DEC-0018`, но её реализация ещё не доказана.

`TSMP95000` не закрывает out-of-band carrier вроде 455 kHz. Такой learn path остаётся отдельным future analog/wideband proposal; известный/imported out-of-band transmit также conditional до emitter/driver/timing HIL.

## Критерий закрытия

Находка закрывается requirement-level решением, которое явно выбирает receiver architecture и честно задаёт:

- какие carrier измеряются автоматически;
- какие берутся из decoder/database/import/manual input;
- где используется demodulated envelope, а где raw carrier;
- range/noise/resource/cost trade;
- unsupported/out-of-band semantics без ложного `universal`.

## Первичные источники

- [Vishay TSOP382/384 datasheet](https://www.vishay.com/docs/82491/tsop382.pdf)
- [Vishay TSMP95000 product page](https://www.vishay.com/en/product/82907/)
- [Vishay TSMP95000 datasheet](https://www.vishay.com/docs/82907/tsmp95000.pdf)
- [Espressif ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)

## Закрытие

Владелец принял dual-path вариант A в `DEC-0018`: `TSOP38238` сохраняет robust demodulated receive, а `TSMP95000` отдельно измеряет carrier 30–60 kHz. `REQ-IR-0001` запрещает называть metadata либо fixed-demodulator envelope измеренной несущей, а out-of-band learning остаётся deferred. Распространение проверено `REV-0002S`; exact pins, BOM, layout и HIL остаются implementation gates в `FND-0017`, но исходная requirement-level неоднозначность закрыта.
