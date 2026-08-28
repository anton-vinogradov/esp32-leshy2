# Leshy2 hardware

[Home](../README.md) · [Русский](hardware.ru.md) · [Schematics](schematics.md) · [Safety](safety.md)

> Current marker: **`H1-R2.29`**. The functional architecture is reviewed; the
> physical design is in progress. Nothing on this page authorizes KiCad routing
> or an order.

## Capabilities

| Path | Production device or boundary | Owner | Finished-device capability |
|---|---|---|---|
| Native S3 | `ESP32-S3-WROOM-1U-N16R8` | S3 | 2.4-GHz Wi-Fi, BLE, ESP-NOW, UI and direct display |
| Native C5 | `ESP32-C5-WROOM-1U-N8R8` | C5 | 2.4/5-GHz Wi-Fi, IEEE 802.15.4 and IR |
| nRF24 ×3 | `E01-ML01IPX` | Front RP | Three full concurrent RX/TX/mixed paths |
| Sub-GHz | `CC1101RGPR` | Rear RP | 315/433/868/915-MHz RX/TX profiles |
| VHF voice | `SA818S-V` | Rear RP | Independent analog VHF RX/TX |
| UHF voice | `SA818S-U` | Rear RP | Independent analog UHF RX/TX |
| Broadcast/Airband | `Si4732-A10-GSR`, `PGA-103+`, `LT5560EDD#TRPBF`, `SI5351A-B-GTR`, `HMC544AETR` | Rear RP | FM/AM/SW/LW and receive-only 118–137-MHz Airband AM |
| Analog FPV | post-PCBA `K331` / `AWM666V RX` bay + `TVP5150AM1PBS` | Rear RP + S3 | Receive-only 5.8-GHz PAL/NTSC capture |
| Audio | `ES8311`, `PAM8302AAYCR`, speaker, microphone and CTIA headset | Rear RP | Record, monitor and play audio |
| Expansion | M5 Unit + rear U214 Cap rail | Rear RP | External GPS/radio modules and regional LoRa Cap |

FM/AM/SW/LW/Airband and analog FPV are receive-only. No custom broadcast or
Airband transmitter is part of Leshy2. VHF/UHF, Sub-GHz, nRF, native Wi-Fi/IR
and an explicitly qualified LoRa expansion retain their documented TX paths and
safety gates.

## Functional ownership

![Current two-PCB architecture](images/h0-r2-functional-architecture.svg)

### Front UI/radio PCB

- `ESP32-S3-WROOM-1U-N16R8`: menus, touch, all user keys, direct 32-MHz
  i8080-8 display TX, BLE/Wi-Fi and the independent local BT.656 camera RX bus.
- `ESP32-C5-WROOM-1U-N8R8`: 2.4/5-GHz Wi-Fi, 802.15.4 and IR.
- `SC1512-A4` front RP: C5/S3/rear-RP links, three local nRF24 paths and microSD.
- Three complete nRF islands: radio, command/return buffers, safety gate and
  dedicated physical-TX evidence.
- `TVP5150AM1PBS`: CVBS decoding beside S3.

Front RP GPIO budget: **46 used / 2 free**. TE capture and backlight PWM moved
here so S3 can retain every direct UI path and the complete i8080-8 bus.

### Rear RF/power PCB

- `SC1512-A4` rear RP: CC1101, voice, broadcast/Airband, audio, FPV, M5 and U214.
- Power conversion, pack admission, independent watchdog, thermal sensing and
  hard-off safety.
- One mutually exclusive post-PCBA K331/AWM666V receiver and a direct selected 50-ohm path to the rear FPV MMCX.
- Audio codec, speaker amplifier, microphone and CTIA headset path.

Rear RP GPIO budget: **45 used / 3 free**. The K331 `RSSI (NC)` contact is not allocated.

## Interboard connector

M1 is the exact straight-SMT Hirose pair `FX8C-80P-SV1(92)` /
`FX8C-80S-SV5(92)`. It has no user-facing through-hole tails.

| Crossing | Current contract |
|---|---|
| Controller transport | Dedicated front-RP ↔ rear-RP SPI plus alert, qualified at 1.5 MB/s |
| Analog video | One 75-ohm `FPV_CVBS` beside ground |
| Safety | RUN/FAULT and three active-low nRF TX-evidence lines |
| Power | Fourteen parallel 3V3_MAIN contacts; 0.3036 A/contact at the 4.25-A step |
| Returns | Twenty-five defined main/safety/IPC/USB/video/UI returns |
| Reserve | Fourteen true NC contacts |

The decoder's eight data lines plus PCLK/VSYNC/HREF stay on the front PCB. No
main RF trace and no nRF payload crosses M1. Rear 48-kHz full-duplex audio stays
below 0.4 MB/s, so it does not saturate the RP transport.

## Physical layout

![Four matched PCB faces](images/h1-r2-four-faces.svg?rev=h1-r2.21-dual-fpv-7)

[Open the detailed exterior at full scale](images/h1-r2-external-layout.svg?rev=h1-r2.21-dual-fpv-7).

The ten main antenna ports are split symmetrically:

| Front PCB | Rear PCB |
|---|---|
| `nRF1 · 2.4G` | `FM/SW/AIR RX` |
| `S3 · 2.4G` | `AM/LW RX` |
| `nRF2 · 2.4G` | `SUB-G RX/TX` |
| `C5 · 2.4/5G` | `VHF RX/TX` |
| `nRF3 · 2.4G` | `UHF RX/TX` |

The separate Molex `73415-2063` (`C588480`) vertical SMT MMCX is labelled
`FPV RX · 5.8G` below the evenly pitched five-SMA rear row and above U214. It
has no interboard tail. Its body leaves 2.07 mm to SMA. The controlled
right-angle plug reference leaves 2.40 mm to SMA, 4.80 mm to U214 and clears
both mounting holes; Ø12 is only a temporary H5 finger-access check.

### Component legend

![Number, MPN and role of every component](images/h1-r2-component-legend.svg?rev=h1-r2.21-dual-fpv-7)

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
references, not silkscreen. The complete legend lists all 163 bodies without
repeating the PCB drawings.

Placement currently has **zero same-face collisions** and **1.05 mm** minimum
opposing clearance against **0.70 mm** required.

The receiver reserve is **30 × 24 × 8 mm**. Primary K331 uses a tolerant
14-pad hand-solder land; the exact AWM666V manufacturer land nests inside it as
a seven-channel fallback. Exactly one module is installed after PCBA and C5
DBG10 is relocated beside S3 DBG10 to preserve the measured clearance.

M1 is not structural: four 11.00-mm compression stops, at least two enclosure
anti-shear datums and independent capture of both PCBs carry screw, drop and
bending loads. The `Keystone 1048P` is also SMT; its 77.06-mm plastic body is
captured by an enclosure cradle/end-stop pair while the 86.00-mm value shown in
the drawing is its pad span.

## User interface and service

- 3.5-inch portrait 320×480 IPS display `HMX035CTFT-001`.
- Five serial navigation switches forming the D-pad, eight side function keys,
  PTT and encoder.
- Two aligned rows of five user-facing status LEDs below the display.
- Four independent USB paths; only `USB / POWER` powers and charges Leshy2.
- Per-controller recessed RESET/BOOT or RUN/USB_BOOT controls and keyed DBG10
  recovery headers.
- User silkscreen is printed only on visible outer faces and is not hidden by
  the display, batteries or U214.

![External service access](images/h1-r2-service-access.svg?rev=h1-r2.21-dual-fpv-7)

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

## Current physical-design gate

Everything above is generated and audit-checked. The post-PCBA one-of-two
receiver architecture removes the unavailable K331 production package from the
H1 critical path. Actual body, hand soldering, Z and durability are explicit
H5/H7 qualification items; a later AKK/Sinopine package may simplify only the
K331 footprint. No engineering blocker remains, but H1 stays open until the
complete mock-up is explicitly accepted. KiCad and all purchasing remain blocked.
