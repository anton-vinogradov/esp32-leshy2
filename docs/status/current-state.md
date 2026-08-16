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
| 2. Capabilities and exclusions | Reviewed (`REV-0002AD`) |
| 3. Architecture and ownership | Reviewed (`DEC-0028`, `REV-0003U`) |
| 4. Components and BOM | Ready to start |
| 5–10 | Not started |

The canonical stage table is [`docs/review/stages.md`](../review/stages.md).

## Accepted target decisions already reflected in the product page

- all-in-one field-tool profile, non-aggression pledge, and three functional levels (`DEC-0002`, `DEC-0010`);
- conservative TX defaults and explicit maximum-power selection (`DEC-0003`);
- zero-loss total-cost optimization (`DEC-0005`);
- external M5 GNSS and external U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- an NMEA baseline and a conditional per-revision advanced CASIC profile without another GNSS (`DEC-0014`);
- an FM/RDS/ordinary-AM baseline and an open owner-imported SSB/CW patch loader without a bundled blob (`DEC-0015`);
- a conditional SA518 dual-band analog-voice target with an honest UHF-only SA868S fallback (`DEC-0016`);
- a dedicated STOP-dominant 4.0 V `VVOICE` rail for SA518 and separate stuffing/supply qualification for SA868S (`DEC-0025`);
- external M5 Unit NFC U216 as the first HF NFC backend, RFID2 as limited compatibility, and custom PN7160 as a qualification fallback (`DEC-0017`);
- dual-path consumer IR on C5 with TSOP38238 robust RX and TSMP95000 measured-carrier learning from 30 to 60 kHz (`DEC-0018`);
- calibrated three-antenna nRF24 RPD hit-rate sector comparison without invented RSSI/dBm, bearing, or VSWR (`DEC-0019`);
- OpenThread as the open Thread baseline and an optional conditional Zigbee adapter without closing the core product (`DEC-0020`);
- S3 as the sole baseline native-BLE owner, with C5 BLE default-off and no reduction of the full native nRF24 scope (`DEC-0021`);
- a complete owner-confirmed wishlist before multiple layouts and a consolidated resource budget (`DEC-0022`);
- a frozen 125-leaf wishlist after delegated self-review, with base/optional/deferred boundaries (`DEC-0023`);
- a latched physical hard STOP that drives RP `RUN` and the S3/C5 reset/enable policy, independently inhibits/power-cuts external TX domains, and requires physical re-arm (`DEC-0024`, `DEC-0028`);
- onboard mono ES8311 audio architecture with fail-safe analog bypass (`DEC-0009`);
- the accepted `PKG-0001/SYN-3A` three-domain target: S3 N16R2 application/UI/audio/storage/native Wi-Fi/BLE, C5 N8R8 dual-band Wi-Fi/802.15.4/IR, and RP2354A A4 direct 3×nRF24/CC1101/voice (`DEC-0028`);
- owner-controlled signed S3/C5/RP updates with A/B rollback, physical recovery and an open developer lifecycle (`DEC-0013`, `DEC-0028`), without enabling irreversible hardware lockdown.

## Open engineering state

- `FND-0001`: C5's single GP-SPI cannot serve the legacy nRF-master and S3↔C5-slave roles simultaneously.
- `FND-0003`: audio architecture is accepted, but pin/electrical/firmware/HIL proof is pending.
- `FND-0006`: the original key-matrix proposal and audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current artifact still has only an I²C-expander STOP input. `DEC-0024` fixes the target architecture, but the latch/gates/rails and fault-injection HIL are not implemented.
- `FND-0011`: SA868 now has PTT receive-default, PD power-down-default, and a physical low-power H/L ceiling. `DEC-0024/0025` fix the target STOP/power architecture; exact gates and HIL remain unimplemented.
- `FND-0013`: VOX has no microphone-capture path and is explicitly deferred to the consolidated audio/pin budget.
- `FND-0015`: both documented M5 NFC Units require a 5 V PORT.A power profile, while current `J40/J41` provide 3.3 V; the electrical correction awaits the consolidated port/power design.
- `FND-0017`: the legacy IR source still has S3 ownership, an unqualified generic emitter/current path, and no proved STOP/TX-state/optical behavior. Its false `FAB-READY` label was removed and Q58 now has a reset-safe pull-down.
- `FND-0019`: the three generic nRF24 PA/LNA placeholders still use the S3 bus, exact modules/STOP/TX detectors are absent, and the post-dual-IR C5 resource budget is unproved. False `FAB-READY` labels were removed and shared CE now has a reset-safe pull-down.
- `FND-0021`: ESB/MouseJack/KeySniffer/BLE-compatible/interference claims require separate capability, security, licence, and HIL gates.
- `FND-0022`: the C5 source candidate and antenna comment were wrong. They now use current-standard N8R8/`C51950748` and the stock `ANT1` path; final antenna/cable/power/STOP/TX-live/EMC/AVL qualification remains open.
- `FND-0023`: public C5 Wi-Fi raw TX does not provide arbitrary management/deauth, `AUTO` is not simultaneous dual band, and any patched vendor binary needs a separate provenance/licence/update/HIL boundary.
- `FND-0024`: 5 GHz modes do not yet implement country/DFS/PMF/privacy gates; DFS SoftAP is excluded by the current radio contract.
- `FND-0026`: native BLE advertising scan is not a promiscuous connection-follow sniffer, a rotating address is not stable identity, and RSSI does not prove metres or direction.
- `FND-0027`: Continuity/iBeacon/Find My and attack labels require versioned corpus/spec/licence/peer proof; ordinary, passive, and disruptive BLE cases have distinct security gates.
- `FND-0028`: prior static nRF ownership maps were compared, but `DEC-0027` moved them to a reference-only archive; they are not input constraints for the new synthesis.
- `FND-0029`: the S3 memory variant, S3↔C5 transport, and recovery interfaces consume overlapping scarce pins. N8R8 is not a drop-in replacement for N8R2 because Octal PSRAM consumes GPIO35–37, while C5 4-bit SDIO conflicts with native USB on GPIO13/14.
- `FND-0030`: legacy 5 V voice power would exceed the accepted SA518 1 W profile. `DEC-0025` fixes the target with a dedicated 4.0 V rail; the legacy schematic and conducted HIL remain open.
- `FND-0032`: old matrix accounting incorrectly freed U214 RESET. The corrected candidate retains `EXT_RF_RST`, moves C5 BOOT to physical recovery, and aggregates touch IRQ; matrix/U14 still needs a decision and HIL.
- Existing tsCircuit/KiCad files remain legacy implementation artifacts until their producing stages are reviewed and regenerated.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The GNSS/navigation slice [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) is **Reviewed** under `REV-0002K`. The owner accepted `IMP-0012/A` as [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA is the mandatory baseline of a qualified profile, while assistance and receiver-reported jamming/spoofing remain conditional on exact revision/firmware proof. Unsupported, timeout, and parser error mean `unknown`, not “no threat,” and host heuristics are kept distinct from receiver status.

`FND-0009` is closed at requirement level. UART/power hardware, parser, assistance source, actual Unit/U214 advanced-message support, RF self-desense, and HIL remain unimplemented evidence for later stages.

The Si4732 slice [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) is **Reviewed** under `REV-0002M`. The owner accepted `IMP-0013/A` as [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): an open bounded loader is in the target, the SSB blob is locally imported with distinct integrity/provenance states, and synchronous AM remains deferred pending separate proof. `FND-0010` is closed at requirement level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder, and coexistence HIL remain unimplemented.

The analog-voice slice [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) is **Reviewed** under `REV-0002O`. The owner accepted `IMP-0014/A` as [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 is the preferred 136–174/400–470 MHz half-duplex analog-FM target, while SA868S remains an explicitly UHF-only fallback until qualification. [`DEC-0025`](../review/decisions/DEC-0025-dedicated-4v-sa518-voice-rail.md) now fixes a separate BAT-fed 4.0 V `VVOICE` for SA518 and separate stuffing/supply qualification for fallback. The peak 2 W-class→1 W trade is accepted and is not recorded as zero-loss saving. `FND-0012` is closed at requirement level; microphone capture/VOX (`FND-0013`), exact STOP/power hardware, protocol, RF, audio, and HIL proof remain for later stages.

The NFC/RFID slice [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) is **Reviewed** under `REV-0002Q`. The owner accepted `IMP-0005/A` as [`DEC-0017`](../review/decisions/DEC-0017-u216-hf-nfc-backend.md): the external $7 M5 Unit NFC U216 is the first HF NFC target, the $4.95 RFID2 is limited compatibility, and custom PN7160 is a fallback only after qualification failure. The $2.05 accessory delta is accepted to retain A/B/F/V, ISO15693/FeliCa, limited emulation, and custom-mode scope; it does not affect the base BOM. `FND-0016` is closed at requirement level by explicit three-tier gates and by rejecting universal clone, one-frontend relay, key-recovery, LF 125 kHz, and payment-compliance overclaims. The exact U216 IC is NRND, and exact-revision/lifecycle, 5 V `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol, and HIL proof remain open implementation work.

The consumer-IR slice [`REQ-IR-0001`](../review/requirements/REQ-IR-0001-consumer-infrared.md) is **Reviewed** under `REV-0002S`. The owner accepted `IMP-0015/A` as [`DEC-0018`](../review/decisions/DEC-0018-dual-path-consumer-ir.md): C5 uses TSOP38238 for robust demodulated 38 kHz receive and TSMP95000 for measured-carrier learning from 30 to 60 kHz, consuming both C5 RX RMT channels; TSAL6200 is the first conditional 940 nm emitter candidate. Cheaper single-learning/fixed-38 variants lose an accepted capability and cannot be substituted silently. `FND-0018` is closed at requirement level; automatic 455 kHz/out-of-band learning remains deferred. Own remote/replay is Main, passive analysis is Lab, unknown replay is Controlled Zone `AUTHORIZED_TARGET`, and TV-B-Gone/brute-force/multi-code sweep is Controlled Zone `BOTH`. `FND-0017`, C5 pins/transport, exact BOM, STOP, optics, licences and HIL remain open implementation work.

The 3×nRF24 capability audit passed `REV-0002T`/`REV-0002U`: [`REQ-N24-0001`](../review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md) preserves three simultaneous full-function radios and accepted [`DEC-0019`](../review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md), a calibrated binary RPD hit-rate sector comparison that is never RSSI/dBm/bearing/VSWR. Ownership remained open at this stage-2 checkpoint and was later resolved to direct RP2354A control by `DEC-0028`. `REV-0002Z`/`AUD-0003`/`IMP-0021` remain historical idea/risk sources only; `FND-0019` and `FND-0021` remain implementation gates.

The C5 Wi-Fi/IEEE 802.15.4 prerequisite audit passed `REV-0002V`, and final propagation under [`REV-0002W`](../review/reviews/REV-0002W-c5-wifi-802154-decision-propagation.md) makes [`REQ-W5-0001`](../review/requirements/REQ-W5-0001-c5-wifi-ieee802154.md) **Reviewed**. The owner accepted `IMP-0018/A` as [`DEC-0020`](../review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md): OpenThread is the open baseline and Zigbee is an optional conditional adapter not required by core/raw/Thread builds. Main/Lab/Controlled Zone are separated, and the shared C5 2.4 GHz path is not represented as simultaneous radios. `FND-0025` is closed at requirement level. N8R4→N8R8, ANT1/ANT2, and EPAD source corrections are complete while final RF qualification remains open (`FND-0022`); the public/raw/patched boundary (`FND-0023`) and DFS/country/PMF/privacy (`FND-0024`) still require implementation/HIL. `IMP-0003` and a private patched Wi-Fi backend were not accepted automatically.

The native BLE prerequisite audit [`REV-0002X`](../review/reviews/REV-0002X-ble-prerequisites.md) is completed by [`DEC-0021`](../review/decisions/DEC-0021-s3-native-ble-owner.md) and propagation review [`REV-0002Y`](../review/reviews/REV-0002Y-s3-native-ble-decision-propagation.md): S3 is the sole baseline native-BLE owner, C5 BLE is default-off, [`REQ-BLE-0001`](../review/requirements/REQ-BLE-0001-native-ble-and-security.md) is **Reviewed**, and `FND-0002` is closed. Only the extra experimental legacy-1M BLE-compatible nRF24 subset is limited; native PTX/PRX/Enhanced-ShockBurst/rate/channel/ACK/pipe/FIFO/IRQ/RPD functions remain intact. Native scan is not represented as a connection sniffer, identifier, or ranging system (`FND-0026`), and vendor/emulation/attack claims retain corpus, rights, and three-level gates (`FND-0027`). Dedicated nRF52 connection sniffing and Bluetooth Mesh are retained as optional deferred-release profiles, not base-board blockers.

The remaining stage-2 slices are now **Reviewed**: [`REQ-W24-0001`](../review/requirements/REQ-W24-0001-s3-wifi-espnow.md), [`REQ-SUB-0001`](../review/requirements/REQ-SUB-0001-cc1101-subghz.md), [`REQ-LORA-0001`](../review/requirements/REQ-LORA-0001-external-sx1262.md), and [`REQ-X-0001`](../review/requirements/REQ-X-0001-cross-session-performance.md). [`INV-0004`](../review/inventories/INV-0004-wishlist-self-review.md) accounts for 125/125 candidates and twelve leaf dispositions from ten source extras. `REV-0002AD` closes stage 2 at requirement level; exact hardware and HIL remain later-stage evidence.


## Reviewed architecture and next gate

Stage 3 was restarted under [`DEC-0027`](../review/decisions/DEC-0027-zero-based-capability-driven-architecture.md). [`FND-0033`](../review/findings/FND-0033-legacy-layout-assumptions-leaked-into-synthesis.md) records the method error: prior work optimized legacy owners, buses and pins instead of deriving hardware independently from the accepted capabilities.

The complete prior `DM/BUD/PIN/SC/LAY/CMP/ADR`, nRF-owner audit and `IMP-0021` texts are preserved under [`drafts/stage3-legacy-derived-2026-08-16/`](../../drafts/stage3-legacy-derived-2026-08-16/README.md) as idea/risk references only. No previous owner, transport, GPIO or layout is an input constraint.

The new active chain starts with [`CAP-0001`](../review/architecture/CAP-0001-zero-based-capability-input.md). It covers 15/15 owner invariants, 9/9 wishlist groups and 13/13 requirement documents without pin/bus allocation and is **Reviewed** under [`REV-0003J`](../review/reviews/REV-0003J-zero-based-stage3-restart.md). The next hardware-neutral artifact, [`CON-0001`](../review/architecture/CON-0001-hardware-neutral-concurrency-model.md), separates mandatory parallelism, time-sharing, qualification-only pairs and exclusions, covers all 21 capability atoms plus failure scenarios, and is **Reviewed** under [`REV-0003K`](../review/reviews/REV-0003K-zero-based-concurrency-model.md). [`RES-0001`](../review/architecture/RES-0001-hardware-neutral-resource-demand.md) then derives compute/interface/timing/memory/power/safety/recovery demand and sizing equations without MCU/GPIO placement; `REV-0003L` reviews it. [`SRC-0001`](../review/architecture/SRC-0001-primary-hardware-resource-facts.md) separates primary package/controller/peripheral facts from layout assumptions and passes `REV-0003M`.

The zero-based method initially fixed only product-level boundaries. `DEC-0028` now resolves the complete target: RP2354A directly owns all three nRF24 radios, CC1101 and voice real-time control; 1-bit SDIO and SPI+alert are the accepted inter-domain transports.

[`SYN-0001`](../review/architecture/SYN-0001-zero-based-whole-device-candidates.md) independently compared three whole-device ways to close the same resource graph: `SYN-2A` places packet-radio service on S3 and U214/GNSS on free C5 interfaces, `SYN-2B` places packet-radio service on C5, and `SYN-3A` adds a deterministic RP2354A A4 domain. `REV-0003N/3O` reviewed the candidate set without choosing a winner; the later atomic package selected `SYN-3A` in `DEC-0028`.

Exact [`PIN-0002`](../review/architecture/PIN-0002-zero-based-exact-pin-maps.md) passes `REV-0003O`: all 36 S3 and 21 C5 pins have an assigned/free/reserved state, controller collisions are absent, and straps, recovery and correct latch/IRQ logic are explicit. `FND-0034` corrects the first `SYN-2A` overflow without losing scope by moving U214 and two GNSS UARTs to free C5 interfaces. `SYN-2A` and `SYN-2B` close with no safe generic GPIO reserve; `SYN-3A` retains seven ordinary C5 GPIO while using 30/30 RP2354 GPIO plus dedicated recovery.

[`BUD-0002`](../review/architecture/BUD-0002-zero-based-memory-traffic-budget.md), reviewed by [`REV-0003P`](../review/reviews/REV-0003P-zero-based-memory-traffic-budget.md), now gives all three maps the same memory, traffic, admission and HIL thresholds. S3 N16R2 passes with a measured 1792 KiB usable-PSRAM floor (`896 KiB` resident + `512 KiB` worst overlay + `384 KiB` reserve). The guaranteed three-nRF profile is simultaneous independent PRX at 200 kB/s payload per radio; a single 10 Mbit/s bus uses 57.6%. The theoretical 3×nRF plus CC maximum would use 79.5% before software margin and is explicitly not advertised as lossless. Failure of the admitted 600 kB/s/latency HIL automatically reopens split ownership.

All candidates pass paper memory and admitted-throughput arithmetic; `SYN-2A` retains the largest S3 contention risk, `SYN-2B` the largest single-core C5 latency risk, and `SYN-3A` the additional signed firmware target.

[`PWR-0001`](../review/architecture/PWR-0001-zero-based-power-safety-envelope.md) passes [`REV-0003Q`](../review/reviews/REV-0003Q-zero-based-power-envelope.md). It sizes one common 3.3 V converter at 2.5 A continuous/3.0 A transient with isolated/current-observed core, packet-RF and audio branches; keeps accepted `VVOICE=4.0 V` at 1.25/1.5 A; gives qualified 5 V accessories 0.75 A/1.0 A; and requires a ≥12 W/15 W 2S power path. These are allowed-scenario floors, not simultaneous permission for every TX. `SYN-3A`'s 100 mA controller allowance fits the same converter, so it adds energy but no candidate-specific DC/DC.

[`RFQ-0001`](../review/architecture/RFQ-0001-zero-based-rf-zoning-coexistence.md) passes [`REV-0003R`](../review/reviews/REV-0003R-zero-based-rf-zoning.md). All candidates are compared with the same independent S3/C5/3×nRF/CC/Si4732/voice/U214/NFC paths, sector antenna geometry and enclosure fixture. Three-nRF PRX remains mandatory and must keep every radio within 3 dB of its isolated sensitivity reference; all other cross-domain RX pairs start qualification-only and every TX pair starts prohibited. `SYN-2B` has the highest native/packet RF concentration; `SYN-3A` has the cleanest controllable partition but must qualify its additional oscillator/IPC emissions.

[`CST-0001`](../review/architecture/CST-0001-dated-candidate-cost-burden.md) passes [`REV-0003S`](../review/reviews/REV-0003S-zero-based-cost-burden.md). At the 2026-08-16 qty-500 snapshot, candidate-specific recurring ranges are `2B $0.5017…0.6517`, `2A $0.6313…0.7813`, and `3A $1.7359…1.8859`. The approximately $1.10 midpoint premium of `3A` over `2A` buys direct radio controls, deterministic isolation and seven free C5 GPIO, not a parts-count saving. It also adds the most firmware/update/HIL work and its observed RP2354A immediate stock is below 500 despite an official RP2350 production horizon through 2045.

Hardware [`PKG-0001`](../review/architecture/PKG-0001-zero-based-target-architecture-proposal.md) was accepted atomically in [`DEC-0028`](../review/decisions/DEC-0028-accept-zero-based-syn-3a.md). [`REV-0003U`](../review/reviews/REV-0003U-stage3-acceptance-propagation.md) verifies the exact owners, transports, pins, controls, budgets, power, RF, update/recovery, cost, kill-gates and cross-repository target propagation; stage 3 is **Reviewed**.

The next gate is stage 4: convert every accepted exact part, conditional candidate and still-abstract circuit function into one evidence register, then qualify components in dependency order. Existing schematic/source artifacts remain legacy implementation evidence until they conform to the accepted target.
