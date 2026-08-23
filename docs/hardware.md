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

FM/AM/SW/LW broadcast transmission is not a device capability: both Si4732
ports remain receive-only. No custom transmitter or RF Cap is developed for
them. The function may appear only through an exact orderable off-the-shelf
self-contained module with manufacturer documentation, integrated RF-output
protection and a qualified product interface. No suitable module is currently
selected.

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

The two board-mounted U.FL receptacles are not substitutes for available RF
module lands. The selected S3 module exposes no RF/ANT land: its supported RF
output is the connector built into `ESP32-S3-WROOM-1U-N16R8`. The C5 module
does expose `ANT2` on contact 31, but the exact standard module enables its
built-in `ANT1` connector and leaves `ANT2` disabled; Espressif requires prior
contact before `ANT2` is used. Therefore each cable returns to the PCB through
the numbered board U.FL, where the real forward-power TX detector branches off
before the outward RP-SMA. A direct cable-to-SMA path would remove that
measurement rather than merely remove a redundant connector.

The internal drawing renders those media separately. A concentric ring inside
the S3 or C5 module is the module-integrated U.FL at its datasheet axis. A
numbered ring is the distinct board-mounted U.FL where the solid cable stops
and the dashed PCB guide begins. Each nRF24 module also carries a visible IPEX
ring connected directly to its board U.FL. Its position is schematic inside
the whole-face reserve until H5 establishes the current-lot generation and
axis.

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
| Main-board display mate | `Hirose DF40C(2.0)-40DS-0.4V(58)` | Fixed 40-contact receptacle; exact 2.0-mm stack |
| Adapter-board mate | `Hirose DF40C-40DP-0.4V(51)` | Exact 40-contact plug; all contacts map one-to-one |
| Panel ZIF | `Hirose FH34SRJ-40S-0.5SH(99)` | 40 contacts, 0.5-mm pitch, top-and-bottom contact |
| microSD | `Hirose DM3AT-SF-PEJM5` | Push-push; independently powered and isolated |
| Audio codec | `Everest ES8311` | I²S capture and playback |
| Microphone | `Same Sky CMEJ-0413-42-SMT-TR` | Rear RF/power board; faces the bottom edge |
| Speaker | `PUI Audio AS02404PO` | Rear RF/power board; 4-ohm differential output; enclosure acoustic treatment is verified later |
| Headphones | `Same Sky SJ1-3515-SMT-TR` | 3.5-mm connector with detect |
| Main I/O expander | `TCA6424ARGJR` | Power, modes and slow signals |
| Control panel | `TCA9539PWR` | Sixteen independent active-low inputs for D-pad, BACK, OPT, F1…F8 and encoder push |
| Navigation buttons | `5× OMRON B3S-1100P` | Independent direct-press UP, DOWN, LEFT, RIGHT and OK |
| Other direct buttons | `11× OMRON B3S-1100P` | BACK, OPT, F1…F8 and PTT |
| RUN/KILL | `C&K JS102011SCQN` | Sole side control for physical safety state and low-current source command |
| Safety controller | `Texas Instruments MSPM0C1106SDGS20R` | Independent heartbeat, TX-lease, evidence and three-zone thermal supervisor |
| Independent watchdog | `Texas Instruments TPS3435CAKAGDDFR` | 1.6-second AON timeout; directly latches FAULT_KILL |
| Encoder | `Alps Alpine EC11E18244AU` | Phases wired directly to S3 PCNT |
| Encoder knob | `Davies Molding 1227-J` | 15-mm soft-touch interference fit for the 6×4.5-mm D shaft |

The front navigation cluster uses five independent, directly pressed
`OMRON B3S-1100P` buttons for UP, DOWN, LEFT, RIGHT and `OK`. The fifteen
front buttons plus encoder push use all sixteen independent expander inputs;
PTT has its own direct RP line. Simultaneous keys therefore need no matrix
scan or ghost-key reconstruction. `BACK`, `OPT`, `F1` through `F8` and `PTT`
use the same series button; no control needs a custom cap or plunger. Four
function keys sit in each display-side gutter: F1–F4 on the left and F5–F8 on
the right. The rear face retains only the encoder on the left and PTT on the
right. The encoder
carries an exact `Davies Molding 1227-J` knob. The side-facing
`C&K JS102011SCQN` is the sole `RUN/KILL` control; separate STOP and RE-ARM
buttons are not fitted. A phone may provide occasional long-form text input but
cannot confirm dangerous actions.

All sixteen `TCA9539PWR` inputs are assigned. The two display-side key columns
have local ESD protection, and F1/F2 no longer consume inter-board contacts.
Adding another ordinary key now requires a second input expander or an explicit
function trade.

The battery holder and rear controls mount directly on the external face of the
RF/power PCB. There is no continuous rear lid over the holder: cells insert
directly into the open `Keystone 1048P`. The encoder sits to the holder's left
and `PTT` to its right, so their actuation axes do not cross the battery envelope.
RUN/KILL faces the enclosure side and is labelled on that external edge.

## Expansion

- The raised rear 14-contact rail uses exact pass-through
  `Samtec HLE-107-02-G-DV-PE-LC`
  and accepts either `M5Stack U214 Cap LoRa-1262` or
  `LESHY2-LORA-CAP-01-EU868/US915` normal to the rear face. Both share the
  84×24-mm envelope and 56-mm retention pitch; the stock U214 remains the
  worst-case depth. The Cap sits between the antenna bank and battery holder
  and overhangs the 75-mm base by 4.5 mm per side.
  Pass-through entry prevents an undocumented long Cap post from bottoming;
  current-lot fit, force and cycle life are verified at incoming inspection.
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
published 3.2-mm depth excludes the flex and adhesive. Replaceable adapter
`L2-DISP-ADP-001-A` decouples that unknown tail from the main UI PCB: exact
`DF40C(2.0)-40DS-0.4V(58)` and `DF40C-40DP-0.4V(51)` form the fixed 40-contact
2-mm mate, while dual-contact `FH34SRJ-40S-0.5SH(99)` accepts either exposed-
contact orientation. All 40 contacts map one-to-one. Received-tail thickness,
outline, stiffener and bend clearance remain H5 checks and may revise only
the small adapter, not the main PCB or enclosure datum. Navigation is a
24.6×24.0-mm cluster of five exact `OMRON B3S-1100P` series switches on 9-mm
centre pitch. Each switch is pressed directly; there is no custom cap,
plunger, guide or actuator. Button accessibility, feel and endurance in the
assembled enclosure remain H5 tests. The exact `Davies Molding 1227-J` encoder
knob is rendered as a solid 15-mm part.
The generator rejects component-to-
component overlap and entry into the 4-mm screw-head keep-outs around the M2.5
mounting holes.

Every placed body on both inner faces must also have a manufacturer-backed body
height. Maximum tolerance envelopes are used where the manufacturer publishes
them. The generator mirrors the RF/power board into the UI-board physical datum
datum. All 129 bodies on the two main inner faces are first checked individually
against the opposite PCB plane: the tallest body is 8.95 mm and leaves 2.05 mm
in the 11-mm channel. The two additional display-adapter connectors are checked
as one complete 3.8-mm assembly; its five rear-board crossings retain at least
6.00 mm, bringing the covered internal component count to 131. The audit then
checks all 43 non-mating main-board pairs whose XY projections overlap. The
current limiting pair—the headphone jack opposite a protected
pack fuse—retains a 3.31-mm Z gap, above the enforced 0.7-mm minimum. The aligned
FX8C plug and receptacle are validated separately as the single intentional mate.
The opposite-face bodies and tails of the nine external RF jacks and the exact
pass-through U214 socket retain at least 1.5 mm of plan clearance from inner
components. All five 30-mm `TE Connectivity 2118651-2` RF feeds are now in the
mechanical audit. S3 and C5 use direct projections between exact connector
axes: their chords are 14.78 and 15.50 mm, leaving 15.22 and 14.50 mm of the
selected assemblies as three-dimensional slack. Their two direct-chord
opposing XY crossings retain 7.77 mm of Z clearance; final slack bend and
retention remain H5 work. The three Ebyte feeds use the complete module face as
a conservative cable-head reserve plus a direct projection to the exact board
receptacle. Their five opposing crossings retain at
least 5.20 mm; the current-lot module connector axes and cable bends remain an
explicit H5 received-part gate rather than invented geometry.

The solid green lines on the UI board have one bounded meaning. Each starts at
the built-in U.FL of the S3 or C5 radio module and represents one removable
30-mm `TE Connectivity 2118651-2` cable. Its other end snaps onto a
UI-board-mounted `Hirose U.FL-R-SMT-1(10)` receptacle, where the green line
ends. The solid line is the direct 2D connector chord, not the shape imposed on
the flexible 30-mm cable. There is no further loose cable: the signal continues on a future 50-ohm
PCB mainline through its own `KYOCERA AVX CP0603Q5425ENTR`, which takes a small
forward sample for the TX detector, and then reaches the outward
`GCT RFPC-SMA32-FN-175-A` RP-SMA. Dashed blue lines show only that topology;
their final geometry is created and verified in KiCad.

Both inner projections now carry nine dashed-blue source-to-port guides:
`S3→S3 RP-SMA`, `Si4732 FMI→FM/SW SMA`, `Si4732 AMI→AM/LW SMA`,
`C5→C5 RP-SMA`, three independent `E01-ML01IPX→nRF24 SMA` paths,
`CC1101→SUB-GHz SMA` and `SA518 ANT7→VHF/UHF SMA`. On each nRF24 path the
cyan portion is the physical microcoax to the board U.FL; the blue PCB guide
begins there. Every blue endpoint coincides with the red datum of its matching
outward antenna connector. This is a complete connectivity map, not accepted
trace geometry.

The externally mounted `Alps Alpine EC11E18244AU` is treated as a through-board
part, not just an outer 11-mm class body. Its two mounting tabs and five signal
terminals project 3.5 mm into the channel. Their exact seven keep-outs forced a
small paper-layout correction: the RP2354 and nRF0 buffers moved upward, while
the SA518 and the right-hand buffer columns moved right. No component, net or
function changed. The seven features clear every RF-side body by at least the
enforced 0.7 mm; their two opposing UI-body crossings retain 4.20 mm of Z
clearance. Only the real SA518 contact-7 and unchanged VHF/UHF-connector
endpoints are now shown, 32.92 mm apart: an invented pre-KiCad copper line no
longer crosses component bodies in the drawing or masquerades as a routed trace.

The exact 80-contact M1 body and the complete 3.8-mm display-adapter stack also
pass the physical keep-out audit. This result deliberately does not claim that
PCB copper is routed: escape routing, return paths, via fields, controlled
impedance and footprint-level clearance close only after both boards pass KiCad
ERC/DRC and an independent layout review. The received display FPC outline and
bend path remain H5 evidence. All mechanically significant bodies—including
power inductors, bulk capacitors, pack protection, interface buffers and audio
selectors—must appear in a physical projection.

In two aligned rows of five below the display, user-facing actual-transmit labels cover
`WI-FI/BLE`, `WI-FI/15.4`, `nRF24-1`, `nRF24-2`, `nRF24-3`, `SUB-GHz`,
`VHF/UHF`, `IR`, `LORA/EXT` and the aggregate `TX ACTIVE`. Antenna silkscreen
uses the same functional names and adds a frequency only where it helps identify
the radio; connector-family text is omitted from the board face.
The two Si4732 antenna inputs are receive-only. Both exact GCT end-launch
connector banks are mirrored onto the outward PCB faces: the faces are
14.2 mm apart, their antenna centre planes are 20.55 mm apart, and no
connector body enters the exact 11-mm interboard channel.

![Dimensioned external layout](images/current-clamshell.svg?layout=15)

![Dimensioned series navigation cluster](images/navigation-cluster.svg?layout=1)

![Dimensioned replaceable display adapter](images/display-adapter.svg?layout=1)

![Dimensioned internal-board layout](images/internal-board-layout.svg?layout=17)

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
