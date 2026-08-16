# Leshy2 Hardware

> **Target product document.** This page describes reviewed product behavior
> and boundaries, not a selected electronic architecture or current
> implementation. See the [current engineering state](docs/status/current-state.md).

- [Русская версия](README.ru.md)
- [Firmware target product](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
- [Canonical review ledger](docs/review/README.md)

## Finished-product intent

Leshy2 is an open, autonomous, portable all-in-one field instrument for
observation, diagnostics, communications, navigation, maintenance and
authorized experiments across several radio ecosystems. It must become a
buildable, repairable and measurable product rather than an unchecked
maximum-capability demo.

The physical form factor, compute topology, owners, buses, pin map, component
set, board partition and enclosure are intentionally open. Former
`PKG-0001/SYN-3A` is retained only as one candidate study after
[`DEC-0032`](docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md).

## Three functional levels

1. **Main** — everyday tools, reception, diagnostics, navigation, maintenance
   and legitimate communications.
2. **Lab** — passive, defensive and bounded security-research tools.
3. **Lab → Controlled Zone** — dangerous active or disruptive tools. Every
   entry displays a fresh non-suppressible warning; every action separately
   requires an authorized target, isolated/conducted environment, or both.

Initial setup separately requires acceptance of the non-aggression pledge.
Neither acknowledgement arms a tool or overrides spectrum, licensing, privacy
or third-party constraints ([`DEC-0002`](docs/review/decisions/DEC-0002-project-vision.md),
[`DEC-0010`](docs/review/decisions/DEC-0010-three-functional-levels.md)).

## Reviewed capability target

- Three independent full-function nRF24 paths retain native PTX/PRX features,
  simultaneous reception and honest packet/drop/timestamp evidence. Their
  future owner and wiring remain open.
- The product provides ordinary 2.4/5 GHz Wi-Fi, IEEE 802.15.4, native
  Bluetooth LE and ordinary 2.4 GHz Wi-Fi/ESP-NOW profiles. Exact radios and
  ownership are selected only by the future whole-device architecture.
- Packet Sub-GHz, broadcast reception, analog voice, calibrated 2.4 GHz
  sector/RPD comparison, consumer IR learning/transmit and digital/analog audio
  paths remain in scope with their reviewed safety and evidence limits.
- Base-board GNSS, LoRa and HF NFC frontends are not required. The product
  design must support qualified external M5-style GNSS, common-band LoRa via
  both cap and expansion-module strategies where feasible, and external NFC.
  iButton/1-Wire uses a replaceable passive M5-style Port-B adapter rather than
  mandatory contact pads on the base enclosure.
- M5 Unit A/B/C/custom and the full U214-compatible 14-pin Cap form the primary
  low-rate expansion tier. Raw SDR/external-compute/general-host needs retain a
  separate high-throughput class; the base does not claim native 30-pin
  M5-Bus compatibility. Exact port count, placement and high-speed connector
  remain product/architecture decisions.
- An optional qualified external IMU may add timestamped motion, pitch/roll and
  short-term relative-rotation metadata to RF records. Device-pose claims require
  a rigid indexed mount and sensor-to-antenna transform. Six-axis data is not
  absolute heading or RF bearing; no base IMU is required.
- Local display, storage, controls, PTT, hard STOP and explicit re-arm remain
  autonomous; ordinary product use cannot require a phone.
- Every programmable chip ultimately selected must expose permanent,
  independent programming, recovery and diagnostic access suitable for
  prototype bring-up and owner repair. Exact connectors and pins remain open.
- Owner-controlled signed updates retain target validation, rollback, offline
  keys/tools and intentional physical recovery. Irreversible lockdown is a
  separate optional decision, never the default.
- Main includes an open personal FIDO2/CTAP USB authenticator with U2F
  compatibility. It runs in an exclusive minimal mode, requires fresh local
  consent, and keeps device-bound credentials out of ordinary backup. It does
  not claim FIDO certification, hardware backing or tamper resistance without
  separate proof; owner-controlled open firmware remains available.

Named modules and ICs in requirement and candidate studies are first targets or
evidence—not silently fixed BOM components.

## Safety and cost boundary

- Every transmitter and Lab action starts disarmed after power, reset, update,
  watchdog or brownout.
- Initial TX uses a conservative per-path profile; maximum available power
  requires an explicit current-scenario choice.
- Physical STOP must dominate firmware and communication failures. Releasing it
  never restores a prior TX target, power or lease.
- Actual-TX evidence remains distinct from a command or UI indication.
- Cost reductions are accepted only with proof of equivalent capability,
  performance, safety, reliability, autonomy, serviceability and testability.

## Development state

The prior 125 capability leaves are reviewed; G2 is narrowly reopened for the
current competitor delta while target physical/product design proceeds as
research. Whole-device alternatives, optimality, conceptual placement and a
new atomic architecture decision must precede components and KiCad. The
normative sequence is [`FLOW-0001`](docs/review/architecture/FLOW-0001-product-to-cad-gates.md).
