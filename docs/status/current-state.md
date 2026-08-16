# Leshy2 Hardware — current engineering state

> Snapshot: 2026-08-16. This page describes what is proven now. The intended finished product is described in the [hardware target README](../../README.md); the [firmware target README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.md) describes the finished software product.

- Canonical evidence: [review ledger](../review/README.md)
- Russian version: [current-state.ru.md](current-state.ru.md)
- Legacy reference only: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Review progress

| Stage | State |
|---|---|
| 0. Review system and baseline | Reviewed |
| 1. Vision and boundaries | Reviewed, including three-tier clarification |
| 2. Capabilities and exclusions | In progress |
| 3–10 | Not started |

The canonical stage table is [`docs/review/stages.md`](../review/stages.md).

## Accepted target decisions already reflected in the product page

- all-in-one field-tool profile, non-aggression pledge, and three functional levels (`DEC-0002`, `DEC-0010`);
- conservative TX defaults and explicit maximum-power selection (`DEC-0003`);
- zero-loss total-cost optimization (`DEC-0005`);
- external M5 GNSS and external U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- an NMEA baseline and a conditional per-revision advanced CASIC profile without another GNSS (`DEC-0014`);
- an FM/RDS/ordinary-AM baseline and an open owner-imported SSB/CW patch loader without a bundled blob (`DEC-0015`);
- a conditional SA518 dual-band analog-voice target with an honest UHF-only SA868S fallback (`DEC-0016`);
- external M5 Unit NFC U216 as the first HF NFC backend, RFID2 as limited compatibility, and custom PN7160 as a qualification fallback (`DEC-0017`);
- onboard mono ES8311 audio architecture with fail-safe analog bypass (`DEC-0009`);
- C5 target ownership of 3×nRF24 and IR (`DEC-0001`), without claiming a working inter-MCU architecture.
- owner-controlled signed S3/C5 updates with rollback and an open developer lifecycle (`DEC-0013`), without enabling irreversible hardware lockdown.

## Open engineering state

- `FND-0001`: C5's single GP-SPI cannot serve the legacy nRF-master and S3↔C5-slave roles simultaneously.
- `FND-0002`: the BLE owner still differs between legacy repositories.
- `FND-0003`: audio architecture is accepted, but pin/electrical/firmware/HIL proof is pending.
- `FND-0006`: the original key-matrix proposal and audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current STOP button is only an I²C-expander input, not an independent hardware TX kill.
- `FND-0011`: SA868 now has PTT receive-default, PD power-down-default, and a physical low-power H/L ceiling; independent STOP and controllable high power still require stage-3 proof.
- `FND-0013`: VOX has no microphone-capture path and is explicitly deferred to the consolidated audio/pin budget.
- `FND-0015`: both documented M5 NFC Units require a 5 V PORT.A power profile, while current `J40/J41` provide 3.3 V; the electrical correction awaits the consolidated port/power design.
- `FND-0017`: the legacy IR source still has S3 ownership, an unqualified generic emitter/current path, and no proved STOP/TX-state/optical behavior. Its false `FAB-READY` label was removed and Q58 now has a reset-safe pull-down.
- `FND-0018`: the fixed 38 kHz TSOP38238 yields a demodulated envelope and cannot measure the source carrier; receiver architecture awaits `IMP-0015`.
- Existing tsCircuit/KiCad files remain legacy implementation artifacts until their producing stages are reviewed and regenerated.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The GNSS/navigation slice [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) is **Reviewed** under `REV-0002K`. The owner accepted `IMP-0012/A` as [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA is the mandatory baseline of a qualified profile, while assistance and receiver-reported jamming/spoofing remain conditional on exact revision/firmware proof. Unsupported, timeout, and parser error mean `unknown`, not “no threat,” and host heuristics are kept distinct from receiver status.

`FND-0009` is closed at requirement level. UART/power hardware, parser, assistance source, actual Unit/U214 advanced-message support, RF self-desense, and HIL remain unimplemented evidence for later stages.

The Si4732 slice [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) is **Reviewed** under `REV-0002M`. The owner accepted `IMP-0013/A` as [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): an open bounded loader is in the target, the SSB blob is locally imported with distinct integrity/provenance states, and synchronous AM remains deferred pending separate proof. `FND-0010` is closed at requirement level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder, and coexistence HIL remain unimplemented.

The analog-voice slice [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) is **Reviewed** under `REV-0002O`. The owner accepted `IMP-0014/A` as [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 is the preferred 136–174/400–470 MHz half-duplex analog-FM target, while the current SA868S remains an explicitly UHF-only fallback until price, supply, PCB/power, and conducted-RF qualification pass. The peak 2 W-class→1 W trade is accepted and is not recorded as zero-loss saving. `FND-0012` is closed at requirement level; microphone capture/VOX (`FND-0013`), independent STOP, high-power control, exact hardware, protocol, RF, audio, and HIL proof remain for later stages.

The NFC/RFID slice [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) is **Reviewed** under `REV-0002Q`. The owner accepted `IMP-0005/A` as [`DEC-0017`](../review/decisions/DEC-0017-u216-hf-nfc-backend.md): the external $7 M5 Unit NFC U216 is the first HF NFC target, the $4.95 RFID2 is limited compatibility, and custom PN7160 is a fallback only after qualification failure. The $2.05 accessory delta is accepted to retain A/B/F/V, ISO15693/FeliCa, limited emulation, and custom-mode scope; it does not affect the base BOM. `FND-0016` is closed at requirement level by explicit three-tier gates and by rejecting universal clone, one-frontend relay, key-recovery, LF 125 kHz, and payment-compliance overclaims. The exact U216 IC is NRND, and exact-revision/lifecycle, 5 V `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol, and HIL proof remain open implementation work.

The consumer-IR prerequisite audit is **Reviewed** under `REV-0002R`; [`REQ-IR-0001`](../review/requirements/REQ-IR-0001-consumer-infrared.md) is **In review**. The current TSOP38238 is a robust fixed-38 kHz demodulator but cannot preserve or measure carrier, while Vishay's TSMP95000 exposes 30–60 kHz carrier cycles for close-range learning. ESP32-C5 has exactly two RX RMT channels, so a dual path is feasible but consumes both. **⚠️ Proposal [`IMP-0015`](../review/improvements/IMP-0015-dual-path-consumer-ir-learning.md)** recommends keeping robust demodulated RX and adding carrier-learning RX plus a qualified 940 nm emitter/driver; cheaper single-learning and honest fixed-38 variants have explicit capability losses. TV-B-Gone and brute-force/multi-code sweeps are moved to the Controlled Zone with `BOTH`. The artifact safe-state was improved, but `FND-0017`, `FND-0018`, C5 pins/transport, exact BOM, STOP, optics, licences and HIL remain open.

## Deferred architecture gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) remains open, but [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) defers the A/B choice to stage 3. No owner decision is requested until a consolidated pin/GPIO/resource budget covers both MCUs, expanders, fixed-function pins, inter-MCU transport, audio, UI/touch, external modules, and genuinely freed onboard GNSS/LoRa lines.

`FND-0006` and `FND-0007` remain open. The deferral neither selects `U14`/the 3×3 matrix nor proves a hardware STOP.
