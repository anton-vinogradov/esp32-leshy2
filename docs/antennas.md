# Leshy2 antennas

[Home](../README.md) · [Русский](antennas.ru.md) · [Hardware architecture](hardware.md)

The established kit covers ten permanently labelled SMA/RP-SMA ports, one
separately keyed MMCX port and 13 physical antennas. Eleven can remain connected at once, while the correct
`SUB-GHz` antenna is selected for the active profile. VHF and UHF have separate
fixed ports. The exact linear FPV antenna is a post-PCBA kit item; it does not
consume a JLCPCB assembly position.

## What connects where

| Kit mark | Device label | Profile | First-target antenna | Kit quantity | Antenna plug |
|---|---|---|---|---:|---|
| `S3` · blue | `WI-FI/BLE` | 2.4/5 GHz | [TE `001-0012`](https://www.te.com/en/product-001-0012.html) | 1 | RP-SMA male |
| `C5` · cyan | `WI-FI/15.4` | 2.4/5 GHz | [TE `001-0012`](https://www.te.com/en/product-001-0012.html) | 1 | RP-SMA male |
| `N1` · violet | `nRF24-1` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `N2` · violet | `nRF24-2` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `N3` · violet | `nRF24-3` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `S315` · orange | `SUB-GHz` | 315 MHz | [TE `ANT-315-CW-HW-SMA`](https://www.te.com/en/product-ANT-315-CW-HW-SMA.html) | 1 interchangeable | SMA male |
| `S433` · amber | `SUB-GHz` | 433 MHz | [TE `ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | 1 interchangeable | SMA male |
| `S915` · yellow | `SUB-GHz` | 868/915 MHz | [Taoglas `TI.08.C.0112`](https://www.taoglas.com/datasheets/TI.08.C.0112.pdf) | 1 interchangeable | right-angle SMA male |
| `VHF` · red | `VHF VOICE` | VHF 136–174 MHz | [Hytera `AN0155H13`](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h13.html) | 1 | SMA male |
| `UHF` · magenta | `UHF VOICE` | UHF 400–470 MHz | [TE `ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | 1 | SMA male |
| `AIR` · green | `FM/SW/AIR RX` | receive FM/SW and 118–137 MHz Airband AM | [Comet `SMA-W100RX2`](https://www.comet-ant.co.jp/product/638/) | 1 | SMA male |
| `LOOP` · slate | `AM/LW LOOP` | LW 153–279 kHz; AM 520–1710 kHz | Leshy2 [`L2-ANT-AM-LW-001`](../hardware/architecture/am-lw-pod.json) | 1 | SMA male |
| `FPV` · lime | `FPV RX 5.8G` | receive-only analog FPV, 5.5–6.0 GHz, linear | [Team BlackSheep `TBS5G8MMCXA`](https://www.team-blacksheep.com/products/product%3A1914) | 1 | MMCX plug |

The kit contains two separate `ANT-433-CW-QW-SMA` units. Its specification
covers 400–470 MHz and up to 10 W, so one unit serves the 433-MHz profile and
the other serves UHF voice. This reduces unique SKUs without moving one antenna
between two connected paths.

## Connectors and safe transmit

- The two native ports are RP-SMA. The antenna requires an RP-SMA male plug
  with a socket centre contact.
- The other eight established ports are standard SMA. The antenna requires an SMA male
  plug with a centre pin; a visually similar RP-SMA plug is not compatible.
- The `FPV RX 5.8G` port is MMCX, mechanically distinct from both SMA families;
  the exact TBS antenna has the matching MMCX plug.
- Transmit always starts disabled. A selected profile, band or power limit is
  never restored after reset or a fault.
- Every outward port has an unobscured short code plus role/band in silkscreen.
  A post-PCBA colour collar around its base repeats the code colour.
- Every antenna has a durable printed heat-shrink flag at the connector end
  with the same code, role and band; its package slot repeats them. Text/code is
  authoritative and colour is only redundant guidance.
- `N1`/`N2`/`N3` are electrically interchangeable, but separate codes keep the
  installed-kit inventory obvious. A substitute inherits the qualified
  profile code only after its RF and mechanical checks pass.
- The software profile alone is not evidence that the correct antenna is fitted.

## Passive AM/LW pod

`L2-ANT-AM-LW-001` plugs directly into the labelled `AM/LW LOOP` port and needs
no power, cable or GPIO setup. It contains one 6×40-mm Fair-Rite `3061990901`
core, a single-layer `38SNSP.125` winding and an
`RF2-154-T-17-50-G` SMA-male plug. The calculated setup winding is 124 turns;
production acceptance is based on the measured 300 µH ±5 %, not the turn count.
The pod is permanently marked `AM/LW LOOP`, `RX ONLY`, `NON-50 OHM` and with a
prompt to rotate it for the best signal.

This is not a 50-Ohm antenna even though it uses the standard SMA mechanics.
Long coax is forbidden because its capacitance consumes the AMI tuning budget.
The core maker suggests material 61 from 0.2 MHz, so LW reception from
153–200 kHz remains an explicit prototype test and is not yet a qualified
sensitivity claim.

## Backup choices

An orderable backup candidate is named for the original 12 items. A
supply-independent linear MMCX fallback for the thirteenth `FPV` item remains
an explicit kit-freeze gate:

- `WI-FI/BLE` and `WI-FI/15.4` — Taoglas [`GW.05.0153`](https://www.taoglas.com/datasheets/GW.05.0153.pdf);
- all three `nRF24` items — Pulse [`W1010`](https://www.digikey.com/en/products/detail/pulse-electronics/W1010/1616689);
- 315-MHz `SUB-GHz` — Joymax [`UHX-328ASA2B`](https://www.digikey.com/en/products/detail/joymax-electronics/UHX-328ASA2B/28334978), for the exact 315-MHz profile only;
- 433-MHz `SUB-GHz` — Joymax [`UHX-325ASAXB`](https://www.digikey.com/en/products/detail/joymax-electronics/UHX-325ASAXB/26742115), for the narrow 433-MHz profile only;
- 868/915-MHz `SUB-GHz` — Joymax [`GHX-221ASA3B`](https://www.digikey.com/en/products/detail/joymax-electronics/GHX-221ASA3B/27545760);
- VHF — Pulse [`SPWB24150`](https://www.pulseelectronics.com/wp-content/uploads/2021/01/PulseLarsen_Portables_Flyer_2017.pdf), whose current stocked quantity is too low for a production commitment;
- UHF — Hytera [`AN0435H25`](https://www.hytera.com/br/product-new/accessories/radio-antennas/an0435h25.html);
- `FM/SW/AIR RX` — remote receive-only Opek [`SCANSMA 25-1300`](https://www.hamradio.com/detail.cfm?pid=H0-016713); the shared port is receive-only and FM/SW/AIR modes are mutually exclusive;
- `AM/LW LOOP` — controlled assembly [`L2-ANT-AM-LW-ALT01`](../hardware/architecture/am-lw-pod.json) using core `3061990891` and connector `CONSMA013.062-G`.

These are purchasing and test backups, not permission for silent substitution.
Narrower antennas enable only the stated firmware profile. Every substitution
must repeat assembled-device match, sensitivity, EIRP, harmonic, coexistence
and mechanical tests. The AM/LW candidate supplies a second geometry but not
yet an independent source: its core material and winding wire retain the same
manufacturers.

## Kit readiness and cost

First choices are named for all 13 physical items. Backup choices are named for
12; 11 are independent of their first target's manufacturer. No backup has completed
hardware qualification yet. Availability, price and limits dated 20 August
2026, plus the FPV selection checked 27 August 2026, are retained in the
[machine manifest](../hardware/architecture/antenna-kit.json).

Using comparable public prices, the backup saves $18.88 for the two native
antennas, $6.39 for the 433-MHz antenna and $20 for the remote FM/SW antenna.
The 315-MHz estimate is about $3.71, but it compares different quantity tiers.
The 868/915-MHz backup adds $0.49. No total is shown because Ebyte is RFQ-only,
VHF/UHF lack comparable volume tiers, and AM/LW pricing excludes assembly.
The exact FPV first target is $6.95 at quantity one; no comparable alternate is
claimed yet.

Both `SMA-W100RX2` and `SCANSMA 25-1300` are documented only from 25 MHz, so no
below-25-MHz performance is claimed before hardware testing.
