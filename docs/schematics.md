# Leshy2 principle schematics

[Home](../README.md) · [Hardware](hardware.md) · [Русский](schematics.ru.md)

These are the current `H0-R2`/`H1-R2.22` principle diagrams of the finished
device. They explain ownership, buses, RF locality, power and service access.
The R2 production ECAD schematic does **not** exist yet: H2 starts only after
the complete H1 mock-up is accepted.

## Component and bus architecture

![Current H0-R2 component and bus architecture](images/h0-r2-functional-architecture.svg)

The front UI/radio PCB owns S3, C5, all three complete nRF24 islands, the front
RP, microSD and TVP5150. The rear RF/power PCB owns CC1101, both voice radios,
broadcast/Airband, audio, the one-of-two post-PCBA K331/AWM666V FPV bay, M5/U214, the rear RP, power and safety.

Exact working GPIO groups and their budgets are published with the
[H0-R2 architecture](h0-r2-functional-architecture.md#working-principle-pin-design).

## Interboard principle

```mermaid
flowchart TD
  S3["ESP32-S3-WROOM-1U-N16R8<br/>UI, i8080-8 TX, camera RX, direct keys"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, 802.15.4, IR"]
  FRP["SC1512-A4 · front RP<br/>3× nRF24, microSD"]
  RRP["SC1512-A4 · rear RP<br/>RF, audio, FPV, expansion"]
  TVP["TVP5150AM1PBS<br/>front-local CVBS decoder"]
  K331["AKK K331 / AWM666V<br/>one post-PCBA analog FPV RX"]
  LCD["HMX035CTFT-001<br/>direct 8-bit i8080 · 32 MHz"]
  M1["Hirose FX8C-80<br/>25 signals · 14 main-power · 2 AON<br/>25 returns · 14 NC reserve"]

  S3 -->|"LCD_CAM TX + GDMA"| LCD
  S3 <-->|"quad data + clock"| FRP
  FRP <-->|"4-bit SDIO"| C5
  FRP <-->|"1.5 MB/s qualified RP link"| RRP
  K331 -->|"75-ohm CVBS"| M1
  M1 --> TVP
  TVP -->|"local camera RX + GDMA"| S3
```

No nRF payload and no main RF antenna trace crosses M1. Only the one analog
video signal crosses before decoding; the 11-line decoded video bus stays on
the front PCB. M1 is electrical/alignment only; four 11-mm compression stops,
anti-shear enclosure datums and independent PCB capture carry mechanical load.

## Physical implementation of the principle

![Outer faces and direct views after turning the PCBs over](images/h1-r2-four-faces.svg?rev=h1-r2.21-dual-fpv-7)

[Front PCB inner face](images/h1-r2-inner-ui.svg) ·
[Rear PCB inner face](images/h1-r2-inner-rf.svg)

Internal numbers are drawing references, not silkscreen. The current placement
audit reports zero same-face body collisions and 1.05 mm minimum opposing
clearance against the 0.70 mm requirement.

## Dedicated signal and power paths

- [Analog-FPV receive path and rear MMCX](h1-r2-fpv.md)
- [Airband receive filter](h1-airband-filter.md)
- [Power, pack and thermal supervision](h1-r2-power-thermal.md)
- [External programming, recovery and physical sections](h1-r2-physical-layout.md)
- [Safety, watchdog and hard-off architecture](safety.md)

## ECAD status

The repository retains the former R1 KiCad sheets and machine reports as
historical engineering evidence. They are **not** the production schematic for
R2 and must not be used for fabrication. H2 will replace them with exact R2
symbols, contacts, nets, values, protection and footprints; only an ERC-clean
reviewed H2 result may be presented here as current production ECAD.
