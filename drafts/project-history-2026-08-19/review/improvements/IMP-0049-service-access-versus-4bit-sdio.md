# ⚠️ Предложение IMP-0049 — complete service access versus 4-bit C5 SDIO

- Статус: **Принято владельцем — A / `DEC-0059`**
- Дата: 2026-08-17
- Finding: [`FND-0070`](../findings/FND-0070-service-access-conflicts-with-4bit-sdio.md)
- Internal step: [`INT-0001/I1`](../architecture/INT-0001-internal-design-closure-sequence.md)
- Decision: [`DEC-0059`](../decisions/DEC-0059-full-service-over-1bit-sdio.md)

## Текущее состояние

Current `G2F-3I` gives C5 a dedicated 4-bit SDIO link and basic independent
UART recovery, but consumes C5 native USB `GPIO13/14` and S3 default UART0 RX
`GPIO44`. The owner requirement remains stronger: every programmable device is
permanently accessible for prototype flashing, recovery and diagnostics.
Espressif separately recommends retaining UART for current RF-test firmware.

## A — return S3↔C5 to 1-bit SDIO and restore complete native service

- S3↔C5 keeps `CLK/CMD/DAT0/DAT1` on S3 `GPIO10…13` and C5 `GPIO7…10`.
- C5 `GPIO13/14` return to native USB; UART0 `GPIO11/12` and
  `CHIP_PU/GPIO28/GPIO27` remain available.
- S3 `GPIO43/44` return to default UART0 while native product USB and
  EN/GPIO0 remain available; S3 GPIO47 also returns to the free pool.
- RP keeps native USB, SWD, RUN and USB_BOOT.
- The former three-domain prototype intent can be implemented without a
  high-speed service mux: three USB data paths plus permanent per-domain
  fixture/control access. Exact connector/header/button MPNs wait for their
  selection gate.

Tradeoff: 1-bit SDIO has less bandwidth margin. Existing reviewed arithmetic
gives `2.5 MB/s` raw at 20 MHz against the required `≥1.5 MB/s` framed payload,
but that margin must pass throughput, priority, reset and RF-load HIL before the
map becomes atomic. Compared with B, A carries one additional C5 USB connector
and its ESD/CC/series network, but removes the SDIO/UART service switch and its
control/SI qualification. Exact total cost and board-edge burden are deferred
to the component/mechanical comparison rather than guessed from part count.

## B — retain 4-bit SDIO and add explicit service isolation/multiplexing

C5 remains UART-only for independent ROM recovery; S3 keeps native USB and
gets default UART0 through a hardware service switch/isolation path on GPIO44.
Four-bit IPC margin stays high and one C5 USB connector can be omitted, but a
new high-speed component/control/default-state path enters SDIO, adds SI and
failure modes, and still provides less convenient C5 USB diagnostics.

## C — retain the current map and omit S3 default UART0

Cheapest paper topology: S3 USB, C5 UART, RP USB/SWD. Erased-image recovery is
present, but current Espressif UART-only RF-test workflow for S3 is not
preserved. This is a service/test capability reduction and is not treated as
zero-loss cost reduction.

## Рекомендация

Принять **A** as the new working transport/service baseline, conditional on the
already-required 1-bit SDIO HIL. It removes service muxes, restores the richest
manufacturer-native access for S3/C5/RP, adds useful pin reserve and matches the
owner's stated expectation that prototype access will be used heavily. If HIL
misses the framed-link gate, B remains the fallback; no product capability is
silently removed.

## Решение владельца

Владелец ответил `го`: вариант **A** принят. Machine map переведён на 1-bit
SDIO; native USB C5 и default UART0 S3 восстановлены; 4-bit остаётся только
fallback при провале HIL и не является параллельной рабочей разводкой.
