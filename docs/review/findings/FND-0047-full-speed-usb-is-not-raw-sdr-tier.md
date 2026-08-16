# FND-0047 — Full-Speed USB is not the accepted raw-SDR/high-throughput tier

- Статус: **Исправление определено; product disposition открыт**
- Дата: 2026-08-17
- Обнаружено: [`AUD-0010`](../audits/AUD-0010-high-speed-usb-host-use-cases.md)
- Затрагивает: `W-EXTRA-16`, `DEC-0034/REQ-EXT-0001`, G3/G4/G7/G9

## Несоответствие

The accepted two-tier expansion model preserves a high-throughput class, but a
future architecture could accidentally satisfy it with ESP32-S3/RP2350 or
MAX3421E USB host and a USB-C connector. Those controllers are Full-Speed only.
They can cover programmers, serial devices, HID and bounded storage, but not a
HackRF-class live raw-IQ stream.

At 20 Msps, 8-bit I + 8-bit Q requires 40 MB/s payload before overhead, while
USB FS line rate is only 12 Mbit/s. Connector shape, buffering and a “USB 2.0”
label cannot close that gap.

## Исправление

- reserve the term `high-throughput USB` for a native HS-capable data path;
- report exact sustained payload, drops, latency and supported transfer/class
  profiles rather than only the 480 Mbit/s line rate;
- allow FS host as a useful separate result, never as raw-SDR equivalence;
- keep exact HS silicon/owner/connector open until whole-device comparison;
- require an explicit owner decision before making native HS host a base result.

## Exit criteria

- [x] current FS and HS controller facts documented;
- [x] raw-IQ arithmetic and overclaim boundary documented;
- [ ] owner chooses product disposition through `IMP-0033`;
- if accepted, a dedicated `REQ-USBH-*` contract and propagation review follow.
