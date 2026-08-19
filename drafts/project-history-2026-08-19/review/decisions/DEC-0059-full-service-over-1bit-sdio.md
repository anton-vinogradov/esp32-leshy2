# DEC-0059 — full S3/C5 service over 1-bit SDIO

> Later allocation: `DEC-0086` consumes the GPIO47 reserve for encoder phase B;
> the 1-bit SDIO and restored service paths decided here remain unchanged.

- Статус: **Принято владельцем — вариант A**
- Дата: 2026-08-17
- Ответ владельца: `го` после рекомендации варианта A
- Proposal: [`IMP-0049`](../improvements/IMP-0049-service-access-versus-4bit-sdio.md)
- Finding: [`FND-0070`](../findings/FND-0070-service-access-conflicts-with-4bit-sdio.md)
- Review: [`REV-0005L`](../reviews/REV-0005L-full-service-1bit-sdio-propagation.md)
- Internal block: [`INT-0001/I1`](../architecture/INT-0001-internal-design-closure-sequence.md)

## Решение

1. Working link S3↔C5 возвращается к dedicated **1-bit SDIO**:
   - S3 `GPIO10/11/12/13` = `CLK/CMD/DAT0/DAT1_IRQ`;
   - C5 `GPIO9/10/8/7` = `CLK/CMD/DAT0/DAT1_IRQ`.
2. C5 `GPIO13/14` становятся permanent native USB `D-/D+`; UART0
   `GPIO11/12`, `CHIP_PU`, `GPIO28` и `GPIO27` также остаются выведенными.
3. S3 сохраняет native USB `GPIO19/20`, `EN/GPIO0` и permanent default UART0
   `GPIO43/44` для RF-test, recovery и diagnostics.
4. RP2354B сохраняет independent USB, SWD, RUN и
   `USB_BOOT/QSPI_SS` через предусмотренный service boundary.
5. Чтобы permanent UART0 S3 не делился с accessory-stub, M5 Unit-профиль на
   тех же физических GPIO7/8 использует второй I²C controller, UART1 через
   GPIO matrix либо GPIO. Возможность UART Unit сохраняется без смены порта.
6. 4-bit SDIO удаляется из working map. Это только fallback после
   документированного провала 1-bit HIL и потребует отдельной схемы service
   isolation/multiplexing и повторного решения.

## Performance и HIL boundary

- 1-bit at 20 MHz = `2.5 MB/s` raw;
- acceptance: `≥1.5 MB/s` framed, admitted occupancy `≤70%`, control RTT
  `≤2 ms`;
- обязательны control-priority, reset/recovery и simultaneous C5
  Wi-Fi/802.15.4 load tests.

Это решение принимает topology и pin budget, но не объявляет измерения
пройденными. HIL остаётся честным prototype gate.

## Pin/cost consequence

- budgets остаются `S3 32 used / 3 reserved / 1 free`,
  `C5 14/6/1`, `RP 48/0/0`, slow I/O `24/0/0`;
- свободный S3 contact теперь `GPIO47`, а не GPIO43;
- добавляется C5 USB connector/protection branch, но не требуется
  high-speed SDIO/UART service mux;
- exact connector, ESD, CC, series, header и switch BOM закрываются в
  `INT-0001/I7/I8`, а не скрываются внутри принятия pin map.
