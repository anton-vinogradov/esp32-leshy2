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
- dual-path consumer IR on C5 with TSOP38238 robust RX and TSMP95000 measured-carrier learning from 30 to 60 kHz (`DEC-0018`);
- calibrated three-antenna nRF24 RPD hit-rate sector comparison without invented RSSI/dBm, bearing, or VSWR (`DEC-0019`);
- OpenThread as the open Thread baseline and an optional conditional Zigbee adapter without closing the core product (`DEC-0020`);
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
- `FND-0019`: the three generic nRF24 PA/LNA placeholders still use the S3 bus, exact modules/STOP/TX detectors are absent, and the post-dual-IR C5 resource budget is unproved. False `FAB-READY` labels were removed and shared CE now has a reset-safe pull-down.
- `FND-0021`: ESB/MouseJack/KeySniffer/BLE-compatible/interference claims require separate capability, security, licence, and HIL gates.
- `FND-0022`: the C5 source candidate and antenna comment were wrong. They now use current-standard N8R8/`C51950748` and the stock `ANT1` path; final antenna/cable/power/STOP/TX-live/EMC/AVL qualification remains open.
- `FND-0023`: public C5 Wi-Fi raw TX does not provide arbitrary management/deauth, `AUTO` is not simultaneous dual band, and any patched vendor binary needs a separate provenance/licence/update/HIL boundary.
- `FND-0024`: 5 GHz modes do not yet implement country/DFS/PMF/privacy gates; DFS SoftAP is excluded by the current radio contract.
- Existing tsCircuit/KiCad files remain legacy implementation artifacts until their producing stages are reviewed and regenerated.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The GNSS/navigation slice [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) is **Reviewed** under `REV-0002K`. The owner accepted `IMP-0012/A` as [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA is the mandatory baseline of a qualified profile, while assistance and receiver-reported jamming/spoofing remain conditional on exact revision/firmware proof. Unsupported, timeout, and parser error mean `unknown`, not “no threat,” and host heuristics are kept distinct from receiver status.

`FND-0009` is closed at requirement level. UART/power hardware, parser, assistance source, actual Unit/U214 advanced-message support, RF self-desense, and HIL remain unimplemented evidence for later stages.

The Si4732 slice [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) is **Reviewed** under `REV-0002M`. The owner accepted `IMP-0013/A` as [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): an open bounded loader is in the target, the SSB blob is locally imported with distinct integrity/provenance states, and synchronous AM remains deferred pending separate proof. `FND-0010` is closed at requirement level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder, and coexistence HIL remain unimplemented.

The analog-voice slice [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) is **Reviewed** under `REV-0002O`. The owner accepted `IMP-0014/A` as [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 is the preferred 136–174/400–470 MHz half-duplex analog-FM target, while the current SA868S remains an explicitly UHF-only fallback until price, supply, PCB/power, and conducted-RF qualification pass. The peak 2 W-class→1 W trade is accepted and is not recorded as zero-loss saving. `FND-0012` is closed at requirement level; microphone capture/VOX (`FND-0013`), independent STOP, high-power control, exact hardware, protocol, RF, audio, and HIL proof remain for later stages.

The NFC/RFID slice [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) is **Reviewed** under `REV-0002Q`. The owner accepted `IMP-0005/A` as [`DEC-0017`](../review/decisions/DEC-0017-u216-hf-nfc-backend.md): the external $7 M5 Unit NFC U216 is the first HF NFC target, the $4.95 RFID2 is limited compatibility, and custom PN7160 is a fallback only after qualification failure. The $2.05 accessory delta is accepted to retain A/B/F/V, ISO15693/FeliCa, limited emulation, and custom-mode scope; it does not affect the base BOM. `FND-0016` is closed at requirement level by explicit three-tier gates and by rejecting universal clone, one-frontend relay, key-recovery, LF 125 kHz, and payment-compliance overclaims. The exact U216 IC is NRND, and exact-revision/lifecycle, 5 V `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol, and HIL proof remain open implementation work.

The consumer-IR slice [`REQ-IR-0001`](../review/requirements/REQ-IR-0001-consumer-infrared.md) is **Reviewed** under `REV-0002S`. The owner accepted `IMP-0015/A` as [`DEC-0018`](../review/decisions/DEC-0018-dual-path-consumer-ir.md): C5 uses TSOP38238 for robust demodulated 38 kHz receive and TSMP95000 for measured-carrier learning from 30 to 60 kHz, consuming both C5 RX RMT channels; TSAL6200 is the first conditional 940 nm emitter candidate. Cheaper single-learning/fixed-38 variants lose an accepted capability and cannot be substituted silently. `FND-0018` is closed at requirement level; automatic 455 kHz/out-of-band learning remains deferred. Own remote/replay is Main, passive analysis is Lab, unknown replay is Controlled Zone `AUTHORIZED_TARGET`, and TV-B-Gone/brute-force/multi-code sweep is Controlled Zone `BOTH`. `FND-0017`, C5 pins/transport, exact BOM, STOP, optics, licences and HIL remain open implementation work.

The 3×nRF24 prerequisite audit is **Reviewed** under `REV-0002T`, and final propagation under `REV-0002U` makes [`REQ-N24-0001`](../review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md) **Reviewed**. The owner accepted `IMP-0016/A` as [`DEC-0019`](../review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md): three simultaneous paths provide calibrated binary RPD hit-rate sector comparison with sampling/calibration metadata, never RSSI/dBm/bearing/VSWR; real-power hardware remains a separate future decision. `FND-0020` is closed at requirement level. Current hardware still routes three generic module placeholders through S3, has no real `TXDET_NRF1..3` detector circuits, and has no proved post-dual-IR C5 pin budget, so `FND-0019` remains open. Passive ESB/MouseJack discovery, sensitive KeySniffer capture, active injection, address brute-force, and interference tests have distinct gates; interference/carrier sweeps are conducted or RF-shielded `BOTH` only, and GPL references are not treated as MIT code, leaving `FND-0021` open for implementation proof. **⚠️ Proposal [`IMP-0017`](../review/improvements/IMP-0017-native-ble-plus-nrf24-compatibility.md)** is deferred to BLE-owner review.

The C5 Wi-Fi/IEEE 802.15.4 prerequisite audit passed `REV-0002V`, and final propagation under [`REV-0002W`](../review/reviews/REV-0002W-c5-wifi-802154-decision-propagation.md) makes [`REQ-W5-0001`](../review/requirements/REQ-W5-0001-c5-wifi-ieee802154.md) **Reviewed**. The owner accepted `IMP-0018/A` as [`DEC-0020`](../review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md): OpenThread is the open baseline and Zigbee is an optional conditional adapter not required by core/raw/Thread builds. Main/Lab/Controlled Zone are separated, and the shared C5 2.4 GHz path is not represented as simultaneous radios. `FND-0025` is closed at requirement level. N8R4→N8R8, ANT1/ANT2, and EPAD source corrections are complete while final RF qualification remains open (`FND-0022`); the public/raw/patched boundary (`FND-0023`) and DFS/country/PMF/privacy (`FND-0024`) still require implementation/HIL. `IMP-0003` and a private patched Wi-Fi backend were not accepted automatically.

## Deferred architecture gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) remains open, but [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) defers the A/B choice to stage 3. No owner decision is requested until a consolidated pin/GPIO/resource budget covers both MCUs, expanders, fixed-function pins, inter-MCU transport, audio, UI/touch, external modules, and genuinely freed onboard GNSS/LoRa lines.

`FND-0006` and `FND-0007` remain open. The deferral neither selects `U14`/the 3×3 matrix nor proves a hardware STOP.
