# FND-0017 — текущий IR TX artifact не был fail-safe или квалифицирован

- Статус: **Частично исправлено консервативно; implementation finding открыт**
- Серьёзность: safety/electrical/traceability blocker
- Затрагивает: `DEC-0001`, `DEC-0003`, `C-IR-02`–`C-IR-05`, `hardware/tscircuit/indicators.tsx`
- Обнаружено и частично исправлено: 2026-08-16

## Несоответствие

`hardware/tscircuit/indicators.tsx` называл себя `FAB-READY`, хотя:

1. `IR_TX` и `IR_RX` всё ещё описаны как S3 GPIO2/GPIO42 вопреки принятому C5 ownership `DEC-0001`;
2. `D57` — геометрический `0603` placeholder без MPN, wavelength, viewing angle, pulse-current, thermal, optical-range и enclosure proof;
3. база low-side NPN `Q58` была подключена через 1 kΩ только к GPIO и не имела base-emitter pull-down, поэтому reset/high-Z не задавал независимый hardware-off;
4. 47 Ω от 5 V лишь подразумевает ток: без exact LED `VF`, ключа, rail tolerance и waveform duty он не является доказанным current limit;
5. отдельный IR electrical/optical TX-live proof в artifact отсутствует: `D50` индицирует C5 radio, а не IR emitter.

Это противоречит `DEC-0003`: reset/brownout/update не должны оставлять передающий тракт в неопределённом состоянии, а активный TX нельзя показывать как факт без соответствующего сигнала состояния.

## Выполненное безопасное исправление

- заголовок source изменён на `LEGACY IMPLEMENTATION DRAFT; NOT FAB-READY`;
- добавлен `Rpd58=100 kΩ` base-emitter, задающий IR-off при reset/high-Z;
- комментарий D57 явно фиксирует unqualified placeholder и необходимость переноса на C5.

Изменение не выбирает финальный emitter/driver, не подтверждает перенос на C5 и не требует регенерировать legacy board как production artifact.

## Что остаётся открытым

- exact C5 GPIO/RMT allocation и inter-MCU/STOP contract после stage-3 resource budget;
- qualified 940 nm emitter, logic driver, current/duty/thermal/rail calculations и PCB/enclosure optics;
- independent STOP/dead-man behavior, electrical TX indication и optically observed HIL;
- IEC 62471 risk assessment для exact emitter/current/duty/enclosure;
- reset, rail-disable и back-power tests при всех fault paths.

## Acceptance следующих стадий

1. Scope trace показывает `IR_TX=off` с power-on до explicit action при reset, brownout, watchdog, C5 crash/update и S3↔C5 link loss.
2. GPIO stuck-active и RMT loop physically terminate по STOP/dead-man и не переживают session exit.
3. Exact emitter current не превышает datasheet envelope при min/nom/max rail, temperature и waveform duty.
4. Optical range/angle, enclosure window, self-interference и electrical/optical TX-state classification измерены, а не выведены из UI state.

## Первичные источники

- [Vishay TSAL6200 datasheet](https://www.vishay.com/docs/81010/tsal6200.pdf)
- [Vishay IEC 62471 eye-safety note](https://www.vishay.com/docs/81935/eyesafe.pdf)
- [Espressif ESP32-C5 RMT API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/rmt.html)
