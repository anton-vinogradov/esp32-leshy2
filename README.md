# Leshy2 Hardware

> **Target product document.** This page is assembled from accepted, reviewed decisions and describes the intended finished device—not the current implementation. See the [current engineering state](docs/status/current-state.md) for maturity, blockers, and pending proposals.

- [Русская версия](README.ru.md)
- [Firmware target product](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
- [Canonical review ledger](docs/review/README.md)

## Finished product target

Leshy2 is an open, autonomous, portable all-in-one field instrument for observation, diagnostics, communications, and authorized experiments across several radio ecosystems. It is designed as a buildable and verifiable product with explicit safety boundaries, not as an unchecked collection of maximum-capability demos.

## Three functional levels

1. **Main** — everyday tools, reception, diagnostics, navigation, maintenance, and legitimate communications outside a security-research scenario.
2. **Lab** — passive, defensive, and bounded security-research tools.
3. **Lab → Controlled Zone** — genuinely dangerous active or disruptive tools. Every entry requires a fresh non-suppressible warning and hold-to-confirm, plus an isolated environment, an explicitly authorized target, or both as required by the tool.

Initial setup separately requires acceptance of the non-aggression pledge. Neither the pledge nor the Controlled-Zone banner arms a tool or overrides spectrum, licensing, privacy, or third-party constraints. The canonical contracts are [`DEC-0002`](docs/review/decisions/DEC-0002-project-vision.md) and [`DEC-0010`](docs/review/decisions/DEC-0010-three-functional-levels.md).

## Accepted hardware direction

- The finished architecture assigns all three nRF24 radios and IR TX/RX to ESP32-C5. The final inter-MCU transport must satisfy that ownership without overcommitting C5's single general-purpose SPI controller.
- GNSS is not populated on the base board. Navigation uses a supported external M5Stack Unit GPS v1.1, or the GNSS included in a supported combined expansion.
- LoRa is not populated on the base board. M5Stack U214 is the first `EXT-RF14` LoRa+GNSS backend for common 868/915 profiles within the module and regional limits; other carriers are optional and separately qualified.
- The onboard mono digital-audio prerequisite uses ES8311, the existing RX-source mux, and two hardware-default-to-analog selectors. Ordinary listening and microphone voice remain available across MCU or codec reset and failure.

## Safety and cost boundary

- Every transmitter starts off; Lab tools start disarmed.
- Initial TX uses a conservative per-radio profile. Maximum available power requires an explicit choice and is never a global default.
- Emergency stop and actual-TX indication have priority over UI and application state; their final electrical implementation must pass failure-injection review.
- Normal S3/C5 update paths accept owner-authorized signed images with validation and rollback. Keys, offline build/signing, and developer firmware remain under owner control; irreversible hardware lockdown is a separate opt-in decision ([`DEC-0013`](docs/review/decisions/DEC-0013-owner-controlled-signed-updates.md)).
- Total product cost is optimized only through implementations proven equivalent in capability, performance, safety, reliability, autonomy, serviceability, and testability.

## How this page grows

Only accepted product contracts are summarized here. Open findings and proposals remain in the [current-state page](docs/status/current-state.md) and review ledger until resolved. As stage 2 produces reviewed `REQ-*`, this page will grow into the complete start document for the finished hardware product.
