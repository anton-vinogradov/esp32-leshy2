# Leshy2 hardware

[Home](../README.md) · [Русский](hardware.ru.md) · [Pin assignment](pinout.md) · [Schematics](schematics.md) · [Safety](safety.md)

> Current marker: **`H2-R2.1.3`**. The `H1-R2.37` physical design was accepted
> and reviewed on 2026-08-30. Nothing on this page authorizes KiCad routing
> or an order.

> Current R2 authority is H0/H1: six compute domains with a front Hub RP and a
> rear RF RP. The [exact dual-RP GPIO/M1 map](pinout.md) is current working H1
> authority and the exact C5 module-pad/IO-mux electrical contract is joined.
> G2F/H2/KiCad is historical single-RP R1 evidence only. The live
> FSUSB42MUX/C11355 route is reviewed as `H2-R2.0.1`; the exact service-VBUS
> detector/latch/release implementation is reviewed as `H2-R2.0.2`; the exact
> `TCA9803DGKR/C2687966` Pack/Safety boundary is reviewed as `H2-R2.0.3`.
> The native R2 inventory and exact symbol/contact/footprint ledger passed
> review; controlled definitions and joined native nets are current.

## Capabilities

| Path | Production device or boundary | Owner | Finished-device capability |
|---|---|---|---|
| Native S3 | `ESP32-S3-WROOM-1U-N16R8` | S3 | 2.4-GHz Wi-Fi, BLE, ESP-NOW, UI and direct display |
| Native C5 | `ESP32-C5-WROOM-1U-N8R8` | C5 | 2.4/5-GHz Wi-Fi, IEEE 802.15.4 and IR |
| nRF24 ×3 | `E01-ML01SP4` · JLCPCB `C97340` | Front RP | Three concurrent PA/LNA paths: full RX/TX/mix, up to 20 dBm |
| Sub-GHz | `CC1101RGPR` | Rear RP | 315/433/868/915-MHz RX/TX profiles |
| VHF voice | `SA818S-V` | Rear RP | Independent analog VHF RX/TX |
| UHF voice | `SA818S-U` | Rear RP | Independent analog UHF RX/TX |
| Broadcast/Airband | `Si4732-A10-GSR`, `PGA-103+`, `LT5560EDD#TRPBF`, `SI5351A-B-GTR`, `HMC544AETR` | Rear RP | FM/AM/SW/LW and receive-only 118–137-MHz Airband AM |
| Audio | `ES8311`, `PAM8302AAYCR`, speaker, microphone and CTIA headset | Rear RP | Record, monitor and play audio |
| Expansion | M5 Unit + protected U214/U219 Cap slot | Rear RP | External GPS/radio modules, regional LoRa Cap, or mutually exclusive RX-only CC1101 + read-only NFC profile |

FM/AM/SW/LW/Airband are receive-only. No custom broadcast or
Airband transmitter is part of Leshy2. VHF/UHF, Sub-GHz, nRF, native Wi-Fi/IR
and an explicitly qualified LoRa expansion retain their documented TX paths and
safety gates.

## Functional ownership

![Current two-PCB architecture](images/h0-r2-functional-architecture.svg)

### Front UI/radio PCB

- `ESP32-S3-WROOM-1U-N16R8`: menus, touch, the S3-local `TCA9539PWR` key path,
  direct 24-MHz i8080-8 display TX and BLE/Wi-Fi.
- `ESP32-C5-WROOM-1U-N8R8`: 2.4/5-GHz Wi-Fi, 802.15.4 and IR.
- `SC1512-A4` front RP: C5/S3/rear-RP links, three local nRF24 paths and microSD.
- Three complete nRF islands: radio, command/return buffers, safety gate and
  dedicated physical-TX evidence.
- Eleven S3 GPIOs released by the removed onboard-video experiment remain true
  reserves instead of being consumed by another peripheral.

Front RP GPIO budget: **46 used / 2 free**. TE capture and backlight PWM moved
here so S3 can retain the local UI path and the complete direct i8080-8 bus.

### Rear RF/power PCB

- `SC1512-A4` rear RP: CC1101, voice, broadcast/Airband, audio, M5 and exactly one signed U214/U219 profile.
- Power conversion, pack admission, independent watchdog, thermal sensing and
  hard-off safety.
- Audio codec, speaker amplifier, microphone and CTIA headset path.

Rear RP GPIO budget: **40 used / 8 free** (GP15/28/29/32/33/34/37/38).

## Interboard connector

M1 is the exact straight-SMT Hirose pair `FX8C-80P-SV1(92)` /
`FX8C-80S-SV5(92)`. It has no user-facing through-hole tails.

| Crossing | Current contract |
|---|---|
| Controller transport | Dedicated front-RP ↔ rear-RP SPI plus alert, qualified at 1.5 MB/s |
| Safety | RUN/FAULT and three active-low nRF TX-evidence lines |
| Power | Fourteen parallel 3V3_MAIN contacts; 0.3036 A/contact at the 4.25-A step |
| Returns | Twenty-four defined main/safety/IPC/USB/UI returns |
| Reserve | Sixteen true NC contacts |

No main RF trace and no nRF payload crosses M1. Rear 48-kHz full-duplex audio stays
below 0.4 MB/s, so it does not saturate the RP transport.

## Physical layout

![Four matched PCB faces](images/h1-r2-four-faces.svg?rev=h1-r2.37-reviewed-1)

[Open the detailed exterior at full scale](images/h1-r2-external-layout.svg?rev=h1-r2.37-reviewed-1).

The ten main antenna ports are split symmetrically:

| Front PCB | Rear PCB |
|---|---|
| `nRF1 · 2.4G` | `FM/SW/AIR RX` |
| `S3 · 2.4G` | `AM/LW RX` |
| `nRF2 · 2.4G` | `SUB-G RX/TX` |
| `C5 · 2.4/5G` | `VHF RX/TX` |
| `nRF3 · 2.4G` | `UHF RX/TX` |

### Component legend

![Number, MPN and role of every component](images/h1-r2-component-legend.svg?rev=h1-r2.37-reviewed-1)

[Front inner face at full scale](images/h1-r2-inner-ui.svg) ·
[rear inner face at full scale](images/h1-r2-inner-rf.svg)

The front PCB shows two different physical media: five removable
IPEX/U.FL-to-U.FL microcoax jumpers and the board-local RF paths that continue
from the board U.FL sockets to SMA. The rear PCB has no U.FL or removable RF
cable. Its voice/FM/SW paths are board-local, AM/LW is a separate
high-impedance AMI path, and Airband uses a powered conversion branch and
selector.

The inner faces are shown exactly as viewed after physically turning each PCB
over, so left and right swap relative to the outer face. Numbers are drawing
references, not silkscreen. The complete legend lists all 226 drawing references without
repeating the PCB drawings.

Placement currently has **zero same-face collisions** and **2.59 mm** minimum
opposing clearance against **0.70 mm** required.

M1 is not structural: four 11.00-mm compression stops, at least two enclosure
anti-shear datums and independent capture of both PCBs carry screw, ordinary
handling and enclosure-flex loads. The `Keystone 1048P` is also SMT; its 77.06-mm plastic body is
captured by an enclosure cradle/end-stop pair while the 86.00-mm value shown in
the drawing is its pad span.

## User interface and service

- 3.5-inch portrait 320×480 IPS `ER-TFT035IPS-6` + `ER-TPC035-6`, `ILI9488` + `FT6236`, direct 24-MHz i8080-8 through passive adapter `L2-DISP-ADP-001-B`.
- Five serial navigation switches forming the D-pad, eight side function keys,
  PTT and encoder.
- Two aligned rows of five user-facing status LEDs below the display.
- Four independent USB paths; only `USB / POWER` powers and charges Leshy2.
- Per-controller recessed RESET/BOOT or RUN/USB_BOOT controls and keyed DBG10
  recovery headers.
- User silkscreen is printed only on visible outer faces and is not hidden by
  the display, batteries or U214.

![External service access](images/h1-r2-service-access.svg?rev=h1-r2.37-reviewed-1)

## Power and unattended safety

Two user-supplied protected 18650 cells operate in parallel. One cell can run
the device; the pair increases available energy and current rather than voltage.
USB is the only alternate power source.

Separate `MSPM0C1106SDGS20R` controllers own pack admission and independent
safety/watchdog supervision.

The placed main rail uses `TPS566231PRQFR` with
`PSPMAA0605H-2R2M-ANP`. The current contract is 3.75 A continuous and 4.25 A
step. Independent hardware can revoke transmit permission and hard-disable the
device on watchdog, thermal, rail or evidence faults while preserving a concise
fault reason for the next boot/display opportunity.

See [power and thermal architecture](h1-r2-power-thermal.md) and the
[three-level safety model](safety.md).

## Reviewed physical design and current ECAD entry

Everything above is generated and structurally checked for every currently
registered body. The onboard video experiment, its connector and its
post-PCBA receiver bay are removed; there is no hidden active module for the
owner to solder after factory assembly. The structural audit of every body, all 18 U219 support parts,
the NFC pickup loop and the supplied 108-mm antenna swept volume passes with no
open geometry gate. The exact EastRising panel and passive adapter are fixed as
well. H1 was explicitly accepted and reviewed on 2026-08-30. The C5 electrical
pin/mux contract, live FSUSB42MUX/C11355 route and exact service-VBUS
detector/latch/release implementation and exact TCA9803 Pack/Safety boundary
are closed. `H2-R2.1.1` reviewed 3 native projects, 23 sheets and 213 exact MPN
groups; `H2-R2.1.2` reviewed exact identities for 208 board groups, five
explicit non-PCBA groups and 1,561 logical contacts. `H2-R2.1.3` now
materializes controlled definitions and joined native nets before a new export.
The legacy HMX display is reference evidence only and cannot enter
an R2 order BOM. Routing and all purchasing remain blocked.
