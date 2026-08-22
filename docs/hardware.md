# Leshy2 hardware architecture

[Home](../README.md) · [Русский](hardware.ru.md) · [Safety](safety.md)

## Principle component interconnections

[Open the complete principle-diagram set](schematics.md). It is split into
readable maps for compute owners, UI and storage, C5 and IR, the RP radio
domain, controls, audio, service and recovery, all nine antenna paths, power
and hardware safety. Every node represents one physical device and includes
its MPN and product role; arrows show link purpose and direction.

The [pin table](pinout.md) gives the exact contacts behind these links, while
the [M1 map](interconnect.md) shows how they cross the two boards.
The machine-readable
[HW/FW integration contract](../hardware/architecture/target-integration-contract.json)
freezes the same controller MPNs, transports, pins, signal-group mapping,
safety timings and regional LoRa profiles for both repositories.

## Compute ownership

```mermaid
flowchart TB
  S3["ESP32-S3-WROOM-1U-N16R8<br/>UI, display, storage, audio, BLE/Wi-Fi"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, 802.15.4, IR"]
  RP["SC1512-A4 · RP2354B<br/>nRF24 ×3, Sub-GHz, voice, Cap Bus"]
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
```

Each owner has independent buses to latency-sensitive devices. The display,
storage and radio paths do not wait on one overloaded shared bus. Within its
group, all three nRF24 radios retain concurrent receive and transmit. Across
top-level signal groups, one group is active while the others are physically
powered down and discharged. The C5 lot must identify chip revision v1.0 or
later because Espressif does not support SDIO on revision v0.1.

## Radio paths

| Path | Primary MPN | Owner | Capability |
|---|---|---|---|
| Native S3 | `ESP32-S3-WROOM-1U-N16R8` | S3 | 2.4-GHz Wi-Fi, BLE, ESP-NOW |
| Native C5 | `ESP32-C5-WROOM-1U-N8R8` | C5 | 2.4/5-GHz Wi-Fi, IEEE 802.15.4 |
| nRF24 ×3 | `Ebyte E01-ML01IPX` | RP2354B | Concurrent `3R`, `1T2R`, `2T1R`, `3T` |
| Sub-GHz | `CC1101RGPR` | RP2354B | 315, 433, 868 and 915 MHz |
| Broadcast RX | `Si4732-A10-GSR` | S3 | FM/SW plus a separate AM/LW input |
| Voice | `NiceRF SA518` | RP2354B | Analog VHF/UHF communications |
| IR RX | `TSOP95238TT` + `TSMP95000TT` | C5 | 38-kHz demodulation and 30–60-kHz learning |
| IR TX | `VSMY14940` | C5 | Controlled 940-nm transmit with optical evidence |
| LoRa/GNSS Cap | `M5Stack U214 Cap LoRa-1262` or `LESHY2-LORA-CAP-01-EU868/US915` | RP2354B | Stock Cap: RX/GNSS; exact Leshy Cap: qualified regional RX/TX |
| External antenna jacks | `7× GCT RFPC-SMA31-FN-175-A` + `2× GCT RFPC-SMA32-FN-175-A` | Dedicated per path | 6-GHz, 50-ohm board-edge SMA/RP-SMA on the two outward PCB faces; no RF sharing or connector bodies in the interboard channel |

Every built-in transmit path has independent actual-TX evidence. Native S3/C5 each use
an exact 30-mm `TE Connectivity 2118651-2` UMCC Gen1 jumper, their own
`U.FL-R-SMT-1(10)` and a `CP0603Q5425ENTR` directional coupler beside the
external RP-SMA. The module and board connector axes and both 30-mm cable
corridors are fixed in the dimensioned inner-board drawing. Each nRF24 has its
own external SMA and `DC2337J5010AHF`; its pigtail remains specimen-gated
because Ebyte documents only `IPEX`, not a mating generation. Nine labelled
per-path indicators plus a `TX ACTIVE` summary sit in one line on the front below
the display. Evidence reports actual transmit activity and a relative level; it
never grants transmit permission.

The stock U214 provides receive and GNSS but no independent actual-RF evidence,
so its TX remains blocked. Cap-Bus contact 5 is monitored through the exact
5-V-tolerant `SN74LVC1G07DCKR`: stock `5V_OUT` reads inactive. The
[exact Leshy LoRa Cap](lora-cap.md) uses `NiceRF LoRa1262-868` or
`LoRa1262-915` and may assert open-drain `EXT_TX_EVIDENCE_N` only from a
`DC0710J5020AHF`/`AD8314ACPZ-RL7` detector on its final external 50-ohm RF
feed. `BUSY`, `IRQ`, branch power and firmware state are diagnostic context,
never substitutes for measured RF.

## User interface, storage and audio

| Device | MPN | Implementation |
|---|---|---|
| Display | `HMX035CTFT-001` | 3.5-inch `320×480` IPS, direct QSPI, capacitive touch; proven 54.5×83.0×3.2-mm LCD/CTP body and 48.96×73.44-mm 2:3 active area |
| FPC mate | `Hirose FH12-40S-0.5SH(55)` | 40 contacts, 0.5-mm pitch |
| microSD | `Hirose DM3AT-SF-PEJM5` | Push-push; independently powered and isolated |
| Audio codec | `Everest ES8311` | I²S capture and playback |
| Microphone | `Same Sky CMEJ-0413-42-SMT-TR` | Rear RF/power board; bottom acoustic port |
| Speaker | `PUI Audio AS02404PO` | Rear RF/power board; 4-ohm differential output through side grille |
| Headphones | `Same Sky SJ1-3515-SMT-TR` | 3.5-mm connector with detect |
| Main I/O expander | `TCA6424ARGJR` | Power, modes and slow signals |
| Control panel | `TCA9539PWR` | Ten independent active-low inputs for D-pad, BACK, OPT, F1, F2 and encoder push |
| D-pad switch | `Alps Alpine SKRHADE010` | Four directions plus centre push beneath one cross; mounted 45° clockwise |
| Direct buttons | `OMRON B3S-1100P` | BACK, OPT, F1, F2 and PTT |
| RUN/KILL | `C&K JS102011SCQN` | Sole side control for physical safety state and low-current source command |
| Safety controller | `Texas Instruments MSPM0C1106SDGS20R` | Independent heartbeat, TX-lease, evidence and three-zone thermal supervisor |
| Independent watchdog | `Texas Instruments TPS3435CAKAGDDFR` | 1.6-second AON timeout; directly latches FAULT_KILL |
| Encoder | `Alps Alpine EC11E18244AU` | Phases wired directly to S3 PCNT |
| Encoder knob | `Davies Molding 1227-J` | 15-mm soft-touch interference fit for the 6×4.5-mm D shaft |

The front panel contains one D-pad cross with centre `OK`. The cross is keyed
to the 3-mm stem of one guided `SKRHADE010`, rather than floating above five
separate plungers. All ten ordinary controls use independent expander inputs,
so simultaneous keys need no matrix scan or ghost-key reconstruction. `BACK`,
`OPT`, `F1`, `F2` and `PTT` are identical directly pressed
`OMRON B3S-1100P` buttons—there is no separate cap or plunger. F1/F2 and the
encoder sit to the rear battery's left; PTT sits to its right. The encoder
carries an exact `Davies Molding 1227-J` knob. The side-facing
`C&K JS102011SCQN` is the sole `RUN/KILL` control; separate STOP and RE-ARM
buttons are not fitted. A phone may provide occasional long-form text input but
cannot confirm dangerous actions.

The battery holder and rear controls mount directly on the external face of the
RF/power PCB. There is no continuous rear lid over the holder: cells insert
directly into the open `Keystone 1048P`. `F1/F2` sit to the holder's left and
`PTT` to its right, so their actuation axes do not cross the battery envelope.
RUN/KILL faces the enclosure side and is labelled on that external edge.

## Expansion

- The raised rear 14-contact rail uses exact vertical `Samtec SSW-107-02-S-D`
  and accepts either `M5Stack U214 Cap LoRa-1262` or
  `LESHY2-LORA-CAP-01-EU868/US915` normal to the rear face. Both share the
  84×24-mm envelope and 56-mm retention pitch; the stock U214 remains the
  worst-case depth. The Cap sits between the antenna bank and battery holder
  and overhangs the 75-mm base by 4.5 mm per side.
- A separate exact `1125R-SMT-4P` right-angle M5 Unit receptacle provides a
  protected, switchable 5-V branch and two isolated signal lines for qualified
  GNSS, LoRa, NFC, iButton/1-Wire and other modules. Its keyed mating-view order
  is GND, 5 V, SIG0, SIG1.
- High-throughput raw SDR needs a dedicated interface; the low-rate Unit port
  is not presented as a raw RF data path.

## Dimensioned layout

Solid component outlines use dimensions from the part-number register. The
display uses the published `54.5×83.0×3.2 mm` LCD/CTP screen-body envelope,
not the complete ES3C35P donor-board envelope of `54.5×101.5×≈10 mm`. The
published 3.2-mm depth excludes the flex and adhesive. The integral
40-contact tail geometry and its exact fit in
`FH12-40S-0.5SH(55)` remain gated on a supplier approval drawing and a real
specimen; the mockup does not present them as already proven. The violet
D-pad cross is a custom product part over the exact rotated
`Alps Alpine SKRHADE010`, so the cross requires a controlled manufacturing
drawing rather than a supplier MPN. The exact `Davies Molding 1227-J` encoder
knob is rendered as a solid 15-mm part.
The generator rejects component-to-
component overlap and entry into the 4-mm screw-head keep-outs around the M2.5
mounting holes.

Every placed body on both inner faces must also have a manufacturer-backed body
height. Maximum tolerance envelopes are used where the manufacturer publishes
them. The generator mirrors the RF/power board into the UI-board physical datum
and checks all 41 non-mating pairs whose XY projections overlap across the exact
11-mm channel. The current limiting pair—the headphone jack opposite a protected
pack fuse—retains a 3.31-mm Z gap, above the enforced 0.7-mm minimum. The aligned
FX8C plug and receptacle are validated separately as the single intentional mate.
The opposite-face bodies and through-hole tails of the external RF jacks and U214
socket retain at least 1.5 mm of plan clearance from inner components. The
central nRF24 module is rotated 90 degrees to clear the U214 tails; the SA518
contact 7 is aligned to a straight 33-mm VHF/UHF corridor; and the CC1101 plus
its reference matching network occupy a dedicated dashed RF zone at the
`SUB-GHz` jack. Both exact 30-mm native RF coax routes are checked against
same-face bodies, screw keep-outs and all opposing bodies. Their three opposing
XY crossings retain 7.77 mm of Z clearance. All mechanically significant
bodies—including power inductors, bulk capacitors, pack protection, interface
buffers and audio selectors—must appear in a physical projection. Only small
passives, unshown copper and manufacturing tolerances remain for ECAD closure.

In two aligned rows of five below the display, user-facing actual-transmit labels cover
`WI-FI/BLE`, `WI-FI/15.4`, `nRF24-1`, `nRF24-2`, `nRF24-3`, `SUB-GHz`,
`VHF/UHF`, `IR`, `LORA/EXT` and the aggregate `TX ACTIVE`. Antenna silkscreen uses the
same names and also states the required frequency and `SMA`/`RP-SMA` type.
The two Si4732 antenna inputs are receive-only. Both exact GCT end-launch
connector banks are mirrored onto the outward PCB faces: the faces are
14.2 mm apart, their antenna centre planes are 20.55 mm apart, and no
connector body enters the exact 11-mm interboard channel.

![Dimensioned external layout](images/current-clamshell.svg?layout=15)

![Dimensioned internal-board layout](images/internal-board-layout.svg?layout=11)

![Dimensioned top view from the antenna edge](images/top-edge-view.svg?layout=4)

![Dimensioned sections through the LoRa Cap and battery zones](images/sandwich-section.svg?layout=10)

![Dimensioned custom LoRa Cap component zones](images/lora-cap-layout.svg?layout=1)

## External antennas

The [complete 12-item antenna kit](antennas.md) maps every user-facing port
label to an exact first-target MPN, band and SMA/RP-SMA type. Three antennas
are interchangeable profiles for the single `SUB-GHz` port and two are
interchangeable VHF/UHF profiles; the other seven have fixed ports.

## Power and service

- The main `JAE DX07S016JA1R1500` carries S3 USB 2.0 Full-Speed and sink-only
  USB-PD: 5 V, 9 V × 3 A or 15 V × 2 A, up to 30 W. There is no power-bank mode.
- `TPS25751DREFR`, `TVS2200DRVR` and `BQ25798RQMR` form the protected PD/NVDC
  frontend and 2S charger, starting conservatively at 1 A and capped at 2 A.
- Two replaceable protected button-top `XTAR 18650 4000mAh` cells sit in a
  polarized `Keystone 1048P`; both are required, providing 28.8 Wh total.
- `MAX17320G20+T` protects and gauges the 2S pack while one
  `MSPM0C1106SDGS20R` performs local fail-closed admission. A second MSPM0,
  powered by AON, owns heartbeat, transmit leases, evidence and three board NTCs.
- The maintained `C&K JS102011SCQN` is the sole low-current RUN/KILL control.
  KILL asks pack admission to shut down and removes RUN_PERMIT; it never carries
  cell or load current, so USB charging and service recovery remain available.
- `TPS3435CAKAGDDFR` independently watches the safety MSPM0 and directly
  latches FAULT_KILL. Restart always requires a physical KILL-to-RUN cycle.
- Independent fixed rails: 3.3-V always-on from `TPS629203DRLR`, plus separate
  3.3-V main, 4.0-V voice and 5.0-V accessory rails from `TPS564252DRLR`.
- S3 exposes product USB and keyed UART0/RESET/BOOT; C5 exposes data-only USB
  and UART0/RESET/BOOT; RP2354B exposes data-only USB and SWD/RUN/USB_BOOT.
  Service USB ports never power the device.

## Implementation data

The detailed tables serve schematic, verification and manufacturing work:

- [Exact assignment of every programmable controller](pinout.md)
- [Device principle diagrams](schematics.md)
- [Exact M1 inter-board connection](interconnect.md)
- [Antenna profiles and exact field kit](antennas.md)
- [Machine-readable BOM CSV](../hardware/architecture/generated/G2F-3I-target-bom.csv)
- [Machine-readable antenna-kit manifest](../hardware/architecture/antenna-kit.json)
- [Exact removable LoRa Cap](lora-cap.md)
- [Machine-readable LoRa Cap source](../hardware/accessories/leshy2-lora-cap-01.json)
