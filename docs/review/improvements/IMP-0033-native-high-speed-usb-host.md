# IMP-0033 — native High-Speed USB host for qualified instruments

- Статус: **⚠️ Требуется решение владельца**
- Дата: 2026-08-17
- Delta: `W-EXTRA-16`
- Evidence: [`AUD-0010`](../audits/AUD-0010-high-speed-usb-host-use-cases.md)
- Finding: [`FND-0047`](../findings/FND-0047-full-speed-usb-is-not-raw-sdr-tier.md)

## Контекст

`DEC-0034` already reserves a separate high-throughput expansion class but does
not decide whether the base is a USB host. Programmers, USB-UART, HID and many
service tools fit Full-Speed. HackRF/raw-IQ does not: current HackRF is a
High-Speed USB peripheral and its maximum stream is roughly 40 MB/s payload.

Current hardware proves native HS OTG is feasible—ESP32-P4 has an integrated
480 Mbit/s HS transceiver and current host stack—but accepting it materially
constrains future compute/power/connector architecture and still requires every
device driver/profile to be qualified.

## Options

### A — accept native USB 2.0 High-Speed host as a base product capability

Every complete architecture preserves one native HS-capable host/data path for
qualified SDR, storage, programmer, modem and external-compute profiles.
Connector count and whether HS is dedicated host or safely dual-role remain
G3/G7 decisions; independent device/recovery access remains mandatory.

- Плюсы: turns the accepted high-throughput tier into a real standard interface;
  covers low-rate service devices and makes bounded HackRF-class raw streaming
  technically reachable without a laptop in the data path.
- Минусы: materially influences MCU/topology, 5 V source/battery/thermal design,
  connector area and firmware attack surface; does not guarantee GNU Radio,
  every USB class or maximum-rate lossless streaming.

### B — accept Full-Speed host only; raw SDR remains companion-compute territory

The base hosts programmers, serial/HID and bounded storage. Raw SDR connects to
a laptop/phone/external compute, not directly to Leshy2.

- Плюсы: many current MCU choices already provide FS OTG; simpler power, memory
  and driver load.
- Минусы: the `DEC-0034` high-throughput tier remains non-USB or external and
  Leshy2 cannot honestly act as a direct HackRF-class raw host.

### C — no base USB host

Product USB remains device/service/FIDO only; all USB peripherals attach to an
external owner-controlled host.

- Плюсы: smallest host stack, power-source and parser attack surface.
- Минусы: loses direct programmers/storage/modem/SDR attachment and weakens the
  all-in-one instrument result; another high-throughput interface still has to
  satisfy `DEC-0034` if raw external classes remain reachable.

## ⚠️ Recommendation

**A**, with a strict distinction between capability and compatibility. The
project explicitly wants receivers, transmitters, programmers and expansion,
and already accepted a real high-throughput tier. Native HS host is the most
standard way to serve those classes. It should not force one dual-role connector
or select ESP32-P4 now; G3/G4 must compare dedicated-host and DRP topologies, and
G7 selects silicon only with the rest of the architecture.

## Acceptance boundary for A

- at least one native USB 2.0 HS-capable host/data path in every final candidate;
- dedicated versus dual-role Type-C is open, clearly indicated and fault-safe;
- product programming/recovery remains independent of the application host path;
- host VBUS default off with per-profile power/current/backfeed/fault control;
- no unknown USB device gets transmitter, programmer, write or trust authority;
- external TX profiles obey STOP, explicit arm/lease and safe-off on every fault;
- FIDO exclusive mode powers down/disables the host surface;
- CDC/VCP, HID, MSC, SDR/vendor and modem profiles qualify independently;
- no “lossless/max-rate/Linux-compatible” claim without measured corpus/HIL.
