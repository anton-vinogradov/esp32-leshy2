# Leshy2 Hardware

> **Target product document.** This page describes reviewed product behavior,
> boundaries and the current principled working design. That design is not the
> final electronic architecture or current implementation. See the
> [current engineering state](docs/status/current-state.md).

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

The final form factor, component set, board partition and enclosure remain
open. The current owner/bus/pin hypothesis is accepted below as a reopenable
working design, not a frozen target. Former
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

- Three independent full-function nRF24 paths retain native PTX/PRX features
  and must support every simultaneous `3R/1T2R/2T1R/3T` mix without automatic
  peer standby or hidden RX gaps. Packet/drop/timestamp and exact mixed-RF
  profile evidence remain explicit. `G2F-3I` places them on RP2354B as the
  leading paper candidate; atomic ownership and wiring are not yet final.
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

## Principled solution design

[`DEC-0051`](docs/review/decisions/DEC-0051-principled-pinout-as-working-design.md)
accepts `G2F-3I/PIN-0003` as the current working design for physical layout.
Its principled pin mapping is reviewed, but it is neither the final atomic
architecture nor authorization to begin KiCad.
[`DEC-0052`](docs/review/decisions/DEC-0052-qspi-first-display-path.md) adds
direct-QSPI D2/D3 on S3 GPIO41/42 and measured `<=1 ms` display occupancy;
[`DEC-0053`](docs/review/decisions/DEC-0053-new-35in-qspi-display-class.md)
accepts a 3.5-inch portrait `320×480` IPS direct-QSPI capacitive-touch class.
[`DSP-0004`](docs/review/architecture/DSP-0004-display-part-number-register.md)
lists every known display reference part number. The official QDtech schematic
discloses exact assembly `HMX035CTFT-001`; `DSP-0005/REV-0005A` review its
40-contact electrical fit without consuming a new GPIO. Standalone
orderability/drawing/lifecycle, exact connector, backlight, optics and
protection remain explicitly open.
`AUDIO-0001/REV-0005B` also instantiate exact `ES8311` QFN-20 contacts:
`CE` is address strap `0x19`, P10 is external `CODEC_PWR_EN`, and the S3
digital fit is unchanged. `AUDIO-0002/REV-0005C` correct the missing RX-source
control on slow P27 and compare complete capture/playback/TX/reset paths.
`DEC-0054/REV-0005D` accept option A: exact active capture, differential
speaker and TX selectors, reset-safe gate and direct S3 GPIO6 `AUDIO_ARM` are
now in the machine map. Passive values and electrical/HIL closure remain open.
`DEC-0057/PHY-0001` accept the removable U214 dock across the rear RF half
above the batteries. The 84-mm Cap overhangs the 75-mm base by 4.5 mm per side;
the legacy rear encoder must move. `MEC-0001/FND-0069` keep the separate host
receptacle MPN, insertion/rail stack-up, screws and installed-cap HIL open.

The diagram below is intentionally maintained as a narrow top-to-bottom view.
It is a living projection of the current internals: every accepted change to a
device, owner, bus or inter-device path must update this diagram, its Russian
twin and the generated pinout atlas in the same commit.

```mermaid
flowchart TD
  S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display/storage, audio, BLE/Wi-Fi owner"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, IEEE 802.15.4 and IR owner"]
  RP["RP2354B A4<br/>deterministic radio and voice owner"]
  SLOW["TCA6424ARGJR<br/>24-line slow-control and UI expander"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  SD["DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SI["Si4732-A10-GS<br/>AM/FM/SW/LW broadcast receiver"]
  CODEC["ES8311<br/>mono ADC/DAC audio codec"]
  RXMUX["SN74LVC1G3157DBVR<br/>receive-audio source selector"]
  BUF["TLV9061IDBVR<br/>active high-impedance capture buffer"]
  SPKSEL["TMUX1136DGSR<br/>dual differential speaker-path selector"]
  TXSEL["TS5A63157DCKR<br/>transmit-audio selector"]
  SAFE["SN74LVC2G08DCUR<br/>reset-safe selector-request gate"]
  PAM["PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPK["MPN TBD<br/>internal loudspeaker"]
  MIC["MPN TBD<br/>electret microphone"]
  NRF0["E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  SA["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  CAPDOCK["MPN TBD<br/>2×7 female 2.54-mm host Cap-Bus receptacle"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  IR0["MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver"]
  IR1["MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver"]
  IRTX["MPN TBD (TSAL6200 screened)<br/>IR transmit LED/driver endpoint"]
  %% Layout-only invisible spine: these links are not electrical connections.
  S3 ~~~ SLOW ~~~ SAFE ~~~ SI ~~~ RXMUX ~~~ BUF ~~~ CODEC
  CODEC ~~~ SPKSEL ~~~ PAM ~~~ SPK ~~~ MIC ~~~ TXSEL
  TXSEL ~~~ LCD ~~~ SD ~~~ UNIT ~~~ C5 ~~~ IR0 ~~~ IR1 ~~~ IRTX
  IRTX ~~~ RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ SA
  SA ~~~ ISO ~~~ CAPDOCK ~~~ U214
  S3 <-->|"4-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
  S3 <-->|"I²C0 + interrupt"| SLOW
  S3 -->|"direct QSPI + touch"| LCD
  S3 <-->|"scheduled SPI2"| SD
  S3 <-->|"I²S0 + I²C0"| CODEC
  S3 <-->|"I²C0"| SI
  S3 <-->|"profile port"| UNIT
  SI --> RXMUX --> BUF --> CODEC
  SA -->|"AFOUT"| RXMUX
  CODEC --> SPKSEL --> PAM
  PAM --> SPK
  CODEC --> TXSEL -->|"MIC_IN"| SA
  MIC --> TXSEL
  S3 -->|"GPIO6 AUDIO_ARM"| SAFE
  SLOW -->|"P11/P12 requests"| SAFE
  SAFE --> SPKSEL
  SAFE --> TXSEL
  C5 -->|"RMT RX0"| IR0
  C5 -->|"RMT RX1"| IR1
  C5 -->|"RMT TX0 + evidence"| IRTX
  RP <-->|"PIO0 SM0"| NRF0
  RP <-->|"PIO0 SM1"| NRF1
  RP <-->|"PIO0 SM2"| NRF2
  RP <-->|"PIO0 SM3"| CC
  RP <-->|"UART0/PTT/evidence"| SA
  RP <-->|"PIO1/UART1"| CAPDOCK
  RP <-->|"I²C0"| ISO
  ISO <-->|"isolated I²C"| CAPDOCK
  CAPDOCK <-->|"14-pin Cap-Bus"| U214
```

| Principled group | Exact owner contacts in the current map | Contract |
|---|---|---|
| S3↔C5 | S3 `GPIO10,GPIO11,GPIO12,GPIO13,GPIO44,GPIO47`; C5 `GPIO7,GPIO8,GPIO9,GPIO10,GPIO13,GPIO14` | dedicated 4-bit SDIO |
| S3↔RP | S3 `GPIO3,GPIO9,GPIO14,GPIO21,GPIO48`; RP `GPIO19,GPIO24,GPIO25,GPIO26,GPIO27` | dedicated SPI3/SPI1 + alert |
| display+microSD | S3 `GPIO4,GPIO5,GPIO35,GPIO36,GPIO38,GPIO39,GPIO40,GPIO41,GPIO42` | direct QSPI display + 1-bit SPI microSD; the only high-rate scheduled pair |
| audio+Si4732 | S3 `GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18` | I²S0 and bounded internal I²C0 |
| M5 Unit | S3 `GPIO7,GPIO8` | separate configurable profile port |
| IR | C5 `GPIO0,GPIO1,GPIO4,GPIO6,GPIO24` | dual RX, TX, power gate and evidence |
| nRF24 #0 | RP `GPIO0,GPIO1,GPIO2,GPIO30,GPIO31,GPIO32` | PIO0 SM0, direct CE/CSN/IRQ |
| nRF24 #1 | RP `GPIO3,GPIO4,GPIO5,GPIO33,GPIO34,GPIO35` | PIO0 SM1, direct CE/CSN/IRQ |
| nRF24 #2 | RP `GPIO6,GPIO7,GPIO8,GPIO36,GPIO37,GPIO38` | PIO0 SM2, direct CE/CSN/IRQ |
| CC1101 | RP `GPIO9,GPIO10,GPIO11,GPIO23,GPIO39,GPIO42,GPIO43` | independent PIO0 SM3/GDO/power |
| SA518/PTT | RP `GPIO16,GPIO17,GPIO18,GPIO20,GPIO21,GPIO22` | UART0, PTT, activity/evidence |
| U214 LoRa/GNSS | RP `GPIO12,GPIO13,GPIO14,GPIO28,GPIO29,GPIO40,GPIO41,GPIO44,GPIO45,GPIO46,GPIO47` | independent PIO1/UART1/I²C0 |

The pin budget is S3 `32 used / 3 reserved / 1 free`, C5 `14/6/1`, RP
`48/0/0` and slow I/O `24/0/0`. RP has no free direct GPIO; independent
SWD/USB/RUN/BOOTSEL remain outside this budget.

The complete normative projection of the current map is in
[`PIN-0003`](docs/review/architecture/PIN-0003-g2f-3i-principled-pinout.md) and
the machine-generated
[`exact pad/net atlas`](docs/review/architecture/generated/G2F-3I-principled-pinout.md).
Remaining electrical boundaries are listed in
[`FND-0060`](docs/review/findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)
and may change the working design after repeated review. The current display
path already terminates on `HMX035CTFT-001`: S3 GPIO39 is touch IRQ, slow
P06/P07 are display/touch reset, and S3 GPIO43 remains free.
The audio digital path likewise terminates on exact `ES8311` contacts at S3
GPIO1/2/15/16/17/18; codec power and differential analog conditioning remain
open electrical blocks rather than hidden pins. The former slow reserve P27 now
carries the required `RX_AUDIO_SOURCE_SEL`; accepted `DEC-0054` assigns direct
S3 GPIO6 `AUDIO_ARM` to exact `SN74LVC2G08DCUR` gate inputs.

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
leading reviewed paper map without radio-bus contention. `DEC-0047` selects a
qualified `SG-N24` envelope; the ordered second ESP32-DIV provides early
`L0 DIV↔DIV` pre-HIL, while target pass requires Leshy2 `T1`. `DEC-0048`
accepts three compact IPEX→external-SMA nRF paths and external SMA for every
onboard antenna endpoint. `ANT-0001/REV-0004P` now prove that exact Si4732 has
separate FM/SW and AM/LW antenna inputs; `DEC-0049/REV-0004Q` accept nine
labelled SMA with separate `RX-FM/SW` and `RX-AM/LW`. The latter requires a
short loop/pod or qualified buffered profile and is not a generic coax port.
`RFH-0001/REV-0004R` additionally review module-to-panel feeds: S3/C5 have
explicit first-generation U.FL/MHF I/AMC compatibility, while Ebyte calls its
connector only `IPX`, so `FND-0057` requires a specimen-fit gate.
`RFH-0002/REV-0004S` show that RP-SMA is typical for native Wi-Fi,
Ebyte/nRF uses standard SMA and sub-GHz has both polarities. The owner choice
is accepted by `DEC-0050/REV-0004T` as bounded `2 RP-SMA + 7 standard SMA`;
`ANT-0002/REV-0004U` review procurement candidates; `DEC-0055/REV-0005E`
accept the 12-item profiled kit and exact-MPN availability gate. Mounting,
cable lengths, two-source assemblies and target RF qualification remain open.
`PIN-0003/REV-0004V` add a generated principled owner/net/pad atlas. The
current exact exposed-contact budget is S3 `32/3/1`, C5 `14/6/1`, RP
`48/0/0` and slow I/O `24/0/0`; exact SA518 service and Si4732 control/RF
contacts are instantiated, while remaining electrical abstractions stay open
under `FND-0060`.
Physical RF/full-mix
measurements, unused-interface quiet-state power controls,
peripherals, power and HIL close in parallel with adapting the legacy physical
mockup and may reopen the working pinout. Whole-device optimality, conceptual placement and a new atomic
architecture decision must precede components and KiCad. The normative sequence is
[`FLOW-0001`](docs/review/architecture/FLOW-0001-product-to-cad-gates.md).
