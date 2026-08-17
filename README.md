# Leshy2 Hardware

> **Target product document.** This page describes reviewed product behavior
> and boundaries, not a selected electronic architecture or current
> implementation. See the [current engineering state](docs/status/current-state.md).

- [Русская версия](README.ru.md)
- [Firmware target product](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
- [Canonical review ledger](docs/review/README.md)

## Finished-product intent

Leshy2 is an open, autonomous, portable all-in-one field instrument for radio/
wireless observation, diagnostics, communication and authorized research,
including wireless and contact credential tools. Navigation, maintenance and
compute exist to support those results rather than turn the product into a
general-purpose peripheral computer. It must become a buildable, repairable and
measurable product rather than an unchecked maximum-capability demo.

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
  low-rate expansion tier. Accepted raw SDR and external RF/credential-analysis
  profiles may derive a separate high-throughput class; the base does not claim
  generic host or native 30-pin M5-Bus compatibility. Exact port count,
  placement and high-speed connector remain product/architecture decisions.
- An optional qualified external IMU may add timestamped motion, pitch/roll and
  short-term relative-rotation metadata to RF records. Device-pose claims require
  a rigid indexed mount and sensor-to-antenna transform. Six-axis data is not
  absolute heading or RF bearing; no base IMU is required.
- Core field operation, display/storage controls, PTT, hard STOP, explicit
  re-arm, pairing/revoke, service and recovery remain autonomous. The base has
  no permanent text keyboard; a declared rare/long text workflow may use a
  locally paired owner phone. The phone supplies visible text, never authority
  for safety, Controlled-Zone, TX, destructive, trust or recovery actions.
- Display performance follows product tasks, not video-like full-frame FPS:
  dirty/tiled updates give critical and first menu feedback within 100 ms,
  waterfall rendering remains preemptible under admitted radio/audio/storage
  load, and any visual coalescing/drop is explicit. Exact panel and optics
  remain architecture/product-design choices.
- Every programmable chip ultimately selected must expose permanent,
  independent programming, recovery and diagnostic access suitable for
  prototype bring-up and owner repair. Exact connectors and pins remain open.
- Owner-controlled signed updates retain target validation, rollback, offline
  keys/tools and intentional physical recovery. Irreversible lockdown is a
  separate optional decision, never the default.
- Generic USB host, personal FIDO/U2F authenticator and 6 GHz/Wi-Fi 6E are
  outside the product mission. A concrete accepted RF/SDR profile may later
  derive an exact high-throughput transport without making generic host support
  a capability.
- BadUSB/DuckyScript is one explicit non-core exception: a release-optional
  Controlled-Zone software profile over the existing USB device/service path.
  It adds no base hardware, cannot shape architecture or delay the radio/key
  core, and still requires authorization, parser/security review and HIL.

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

The 125 capability leaves and the competitor delta have received repeated G2
review. G3 physical/product inputs remain reviewed, but G2F logical/electrical
feasibility now comes first. One machine-readable source contains three
structurally checked maps; `DEC-0044/NIF-0001/REV-0004L` select `G2F-3I` as the
leading reviewed paper map without radio-bus contention. Physical RF, exact
peripherals, power and HIL must close before adapting the legacy physical
mockup. Whole-device optimality,
conceptual placement and a new atomic
architecture decision must precede components and KiCad. The normative sequence is
[`FLOW-0001`](docs/review/architecture/FLOW-0001-product-to-cad-gates.md).
