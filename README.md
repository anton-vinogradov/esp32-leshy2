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

- The currently accepted finished architecture assigns all three full-function nRF24 radios and IR TX/RX to ESP32-C5. The final inter-MCU transport must satisfy that ownership without overcommitting C5's single general-purpose SPI controller.
- ESP32-C5 provides ordinary 2.4/5 GHz Wi-Fi in one selected band and built-in IEEE 802.15.4 without another RF module. OpenThread is the open Thread baseline; Zigbee coordinator/router/end-device support is an optional conditional adapter and is not required to build, update, or recover the open core product. Ordinary operation on owner-administered networks is Main, passive raw analysis is Lab, and active security tests are Controlled Zone. The product does not promise simultaneous dual band, DFS SoftAP, full lossless monitor, or public deauth/disassociation support ([`DEC-0020`](docs/review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md)).
- ESP32-S3 is the sole baseline native Bluetooth LE owner for ordinary scan/advertise, GAP/GATT/SMP/HID, product identity and bond storage; C5 BLE is default-off. This does not reduce the nRF24 radios: only their extra experimental legacy-1M BLE-compatible subset is limited, because nRF24 is not a complete BLE controller ([`DEC-0021`](docs/review/decisions/DEC-0021-s3-native-ble-owner.md)).
- Each of the three nRF24 paths retains the native transceiver feature set, independent PTX/PRX sessions and simultaneous reception. They also provide 2.4 GHz energy sampling and a calibrated sector hunt based on binary RPD hit rate. Records expose the sampling window and calibration state; the product does not invent RSSI/dBm, bearing, angle, or VSWR. Passive ESB discovery is Lab, authorized single-target exploitation is Controlled Zone, and interference/carrier tests require both authorization and conducted or RF-shielded containment ([`DEC-0019`](docs/review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md), [`REQ-N24-0001`](docs/review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)).
- GNSS is not populated on the base board. Navigation uses a supported external M5Stack Unit GPS v1.1, or the GNSS included in a supported combined expansion. A qualified profile must provide the NMEA baseline; assistance and receiver-reported interference/spoofing status are enabled only after exact revision/firmware proof, and unsupported/unknown is never presented as no threat ([`DEC-0014`](docs/review/decisions/DEC-0014-casic-gnss-profile.md)).
- LoRa is not populated on the base board. M5Stack U214 is the first `EXT-RF14` LoRa+GNSS backend for common 868/915 profiles within the module and regional limits; other carriers are optional and separately qualified.
- The onboard mono digital-audio prerequisite uses ES8311, the existing RX-source mux, and two hardware-default-to-analog selectors. Ordinary listening and microphone voice remain available across MCU or codec reset and failure.
- The onboard Si4732 provides FM/RDS and ordinary LW/MW/SW reception. SSB USB/LSB and CW via BFO become available after the owner locally imports a compatible volatile patch through an open bounded loader; no third-party blob ships without proven provenance and redistribution rights. Synchronous AM is not promised pending separate proof ([`DEC-0015`](docs/review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md)).
- The preferred voice-radio backend is a half-duplex analog-FM SA518 covering VHF 136–174 and UHF 400–470 MHz at 0.5/1 W under explicit regional/licence profiles. A UHF-only SA868S fallback remains until price, supply, and RF qualification pass, and is never labelled dual-band. The 2 W-class→1 W peak trade is accepted for one VHF+UHF module; an external SMA is not represented as licence-exempt PMR446 equipment ([`DEC-0016`](docs/review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md)).
- HF NFC/RFID is provided by an external M5 Unit NFC U216 through a qualified 5 V `PORT.A-NFC`, keeping the frontend out of the base BOM. The first target covers NFC-A/B/F/V and ordinary tag operations; credential analysis belongs to Lab, while recovery, credential writing/cloning, emulation, and a two-frontend relay belong to the Controlled Zone and require an authorized target. RFID2 is limited compatibility and a custom PN7160 design is only a qualification fallback. Exact U216 revision/lifecycle support remains conditional and no universal-clone, payment-compliance, or LF 125 kHz claim is implied ([`DEC-0017`](docs/review/decisions/DEC-0017-u216-hf-nfc-backend.md)).
- Consumer IR uses two C5 receive paths: TSOP38238 for robust demodulated 38 kHz reception and TSMP95000 for measured-carrier learning from 30 to 60 kHz. TSAL6200 is the first conditional 940 nm emitter candidate. Own-device remote/replay is Main, passive analysis is Lab, unknown/security replay requires an authorized target in the Controlled Zone, and disruptive multi-code sweeps require both isolation and authorization. Automatic 455 kHz/out-of-band learning remains deferred ([`DEC-0018`](docs/review/decisions/DEC-0018-dual-path-consumer-ir.md)).

## Safety and cost boundary

- Every transmitter starts off; Lab tools start disarmed.
- Initial TX uses a conservative per-radio profile. Maximum available power requires an explicit choice and is never a global default.
- Emergency stop and actual-TX indication have priority over UI and application state; their final electrical implementation must pass failure-injection review.
- Normal S3/C5 update paths accept owner-authorized signed images with validation and rollback. Keys, offline build/signing, and developer firmware remain under owner control; irreversible hardware lockdown is a separate opt-in decision ([`DEC-0013`](docs/review/decisions/DEC-0013-owner-controlled-signed-updates.md)).
- Total product cost is optimized only through implementations proven equivalent in capability, performance, safety, reliability, autonomy, serviceability, and testability.

## How this page grows

Only accepted product contracts are summarized here. Open findings and proposals remain in the [current-state page](docs/status/current-state.md) and review ledger until resolved. As stage 2 produces reviewed `REQ-*`, this page will grow into the complete start document for the finished hardware product.
