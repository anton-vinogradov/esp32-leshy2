# FND-0070 — full service access conflicts with the current 4-bit C5 SDIO map

- Статус: **Открыто; варианты вынесены в `IMP-0049`**
- Серьёзность: recovery / RF-test / pin-map blocker
- Обнаружено: 2026-08-17
- Active block: [`INT-0001/I1`](../architecture/INT-0001-internal-design-closure-sequence.md)
- Proposal: [`IMP-0049`](../improvements/IMP-0049-service-access-versus-4bit-sdio.md)

## Проверенные факты

1. ESP32-S3 supports USB and UART download. Espressif recommends retaining the
   UART download interface because its current RF-test firmware supports UART;
   default UART0 is `GPIO43=U0TXD`, `GPIO44=U0RXD`.
2. ESP32-C5 likewise supports USB and UART download; UART0 defaults to
   `GPIO11/12`, while Joint Download Boot 0 requires `GPIO28=0`, `GPIO27=1`
   and reset through `CHIP_PU`.
3. C5 native USB D−/D+ are `GPIO13/14`. The same two contacts are
   `SDIO_DATA3/2` in 4-bit mode; they cannot be independent direct interfaces
   at the same time.
4. Current `G2F-3I` additionally routes S3 `GPIO44/47` to those C5 SDIO data
   contacts. Therefore S3 default UART0 RX on GPIO44 is also consumed.
5. RP2354B retains independent USB, `USB_BOOT/QSPI_SS`, `RUN`, `SWD` and
   `SWCLK`; this portion has no pin collision in the current map.

## Несоответствие

The current service ledger is sufficient for basic independent recovery:
S3 native USB + EN/GPIO0, C5 UART0 + CHIP_PU/GPIO28/GPIO27, RP USB + SWD/RUN.
It is not equivalent to the former three-domain full USB/UART prototype-access
study, and it lacks the manufacturer-recommended default S3 UART0 RF-test path.

Simply reconnecting the old three USB-C/DBG topology would create unterminated
branches or external-driver contention on high-speed SDIO and service pins.
That is not a mechanical detail and must be decided before final pinout.

## Correct boundary

No active allocation changes until `IMP-0049` is decided. Whichever option is
selected must preserve erased-image recovery without peer firmware, physical
boot/reset control, RF-test diagnostics, TX-off defaults, no host backfeed and
the measured S3↔C5 payload/latency gate.

## Primary sources

- [Espressif ESP32-S3 download guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/download-guidelines.html)
- [Espressif ESP32-S3 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html)
- [Espressif ESP32-C5 download guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/download-guidelines.html)
- [Espressif ESP32-C5 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html)
- [Raspberry Pi hardware design with RP2350](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf)
