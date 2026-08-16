# IMP-0015 — dual-path consumer IR learning без ложного universal claim

- Статус: **Принято владельцем: вариант A, `DEC-0018`**
- Связано: `C-IR-01`–`C-IR-05`, `FND-0017`, `FND-0018`, draft `REQ-IR-0001`
- Зона: Main own-device remote; Lab passive analysis; Controlled Zone disruptive sweep/replay
- Дата: 2026-08-16

## Контекст

Текущий `TSOP38238` хорош как noise-resistant demodulated receiver для 38 kHz long-burst consumer protocols, но удаляет carrier и не может автоматически узнать исходную частоту. Специализированный `TSMP95000` сохраняет carrier cycles для 30–60 kHz code learning, однако его типовая дальность в datasheet — 1.8 m с TSAL6200/50 mA, то есть он не является безусловной заменой robust receiver. ESP32-C5 предоставляет ровно два RX RMT channels, поэтому возможно сохранить оба назначения.

TX artifact также требует exact emitter/driver. `TSAL6200` — доказанный 940 nm high-power remote-control candidate с ±17° и 100 mA continuous/200 mA pulse ratings; финальные current/duty/range/eye-safety определяются схемой и HIL, не названием детали.

## Рассмотренные варианты

### A — два RX path + квалифицированный TX (рекомендация)

- robust demodulated path: `TSOP38238` либо corpus-selected exact 36/38/40/56 variant;
- learning path: `TSMP95000` carrier-out 30–60 kHz;
- оба C5 RX RMT channels заняты IR, один TX RMT — emitter waveform;
- `TSAL6200` — first emitter candidate через logic low-side driver с hardware pull-down/current limit;
- 30–60 kHz learned records сохраняют measured carrier; decoder/DB/import carrier имеет отдельный provenance;
- 455 kHz и иной out-of-band learn честно deferred, а known/imported TX включается только после отдельного HIL;
- цена — дополнительный receiver, GPIO, passives, площадь/window и tests; точная BOM-дельта ждёт AVL quote.

Это единственный вариант из трёх, сохраняющий robust ordinary RX и одновременно исполняющий legacy carrier-learning intent. Он не расширяет base product до arbitrary optical transmitter.

### B — один `TSMP95000`

Даёт carrier-aware learning 30–60 kHz на одном RX GPIO/RMT и убирает `TSOP38238`, но меняет long-range/noise behavior на learning-oriented типовую дальность 1.8 m. Это меньший BOM, однако не zero-loss saving без acceptance, которая явно отказывается от robust receive.

### C — оставить один `TSOP38238`

Минимальная переделка и robust 38 kHz receive. Carrier хранится только как protocol/database/import/manual metadata; неизвестный raw capture не называется faithful learned replay. Это честный дешёвый baseline, но снимает automatic carrier learning и сужает universal-remote promise.

## Общий safety/security contract любого варианта

- own-tagged single-device remote/replay — Main с explicit press-to-send;
- passive analysis чужого/неясного сигнала — Lab, без автоматического TX;
- unknown-provenance replay, TV-B-Gone/multi-code power sweep, brute-force/service-code sweep — Controlled Zone;
- массовый/sweep tool использует `BOTH`: изолированная line-of-sight зона и явно авторизованные targets;
- entry banner не вооружает emitter; каждое действие отдельно показывает target set, code count, max duration и STOP;
- reset/link loss/STOP/session exit выключают driver аппаратно; import/playlist/deep link не обходят arming;
- bundled universal/TV-B-Gone/AC databases требуют per-record provenance/licence; owner-import допустим, но не получает trusted status автоматически.

## Стоимость без потери продукта

Вариант A добавляет BOM и потому не называется экономией. Но по сравнению с discrete photodiode analog learner либо bank из нескольких demodulators он использует один специализированный learning IC и уже имеющиеся C5 RMT resources. На stage 3/4 сравниваются exact AVL/quote, две GPIO, PCB/window area и HIL; удаление robust receiver в B считается экономией только если владелец отдельно принимает потерю range/noise criterion.

## Первичные источники

- [ESP32-C5 datasheet: 2 TX + 2 RX RMT](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP-IDF RMT API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/rmt.html)
- [Vishay TSOP382/384 datasheet](https://www.vishay.com/docs/82491/tsop382.pdf)
- [Vishay TSMP95000 datasheet](https://www.vishay.com/docs/82907/tsmp95000.pdf)
- [Vishay TSAL6200 datasheet](https://www.vishay.com/docs/81010/tsal6200.pdf)
- [Arduino-IRremote MIT reference](https://github.com/Arduino-IRremote/Arduino-IRremote)
- [IRremoteESP8266 protocol matrix](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/SupportedProtocols.md)

## Решение владельца

2026-08-16 принят вариант A: два независимых C5 RX path (`TSOP38238` + `TSMP95000`) и квалифицируемый TX с `TSAL6200` как первым emitter candidate. Канонический контракт — `DEC-0018`; варианты B/C не могут быть применены как скрытая BOM-экономия.
