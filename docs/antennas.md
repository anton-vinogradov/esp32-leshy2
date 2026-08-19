# Leshy2 antennas

[Home](../README.md) · [Русский](antennas.ru.md) · [Hardware architecture](hardware.md)

The device has nine permanently labelled antenna ports. The full field kit
contains 12 physical antennas: nine can remain connected at once, while the
correct `SUB-GHz` and `VHF/UHF` antenna is selected for the active profile.

## What connects where

| Device label | Profile | First-target antenna | Kit quantity | Antenna plug |
|---|---|---|---:|---|
| `WI-FI/BLE` | 2.4/5 GHz | [TE `001-0012`](https://www.te.com/en/product-001-0012.html) | 1 | RP-SMA male |
| `WI-FI/15.4` | 2.4/5 GHz | [TE `001-0012`](https://www.te.com/en/product-001-0012.html) | 1 | RP-SMA male |
| `nRF24-1` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `nRF24-2` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `nRF24-3` | 2.4 GHz | [Ebyte `TX2400-JW-5`](https://www.ebyte.com/product/495.html) | 1 | SMA male |
| `SUB-GHz` | 315 MHz | [TE `ANT-315-CW-HW-SMA`](https://www.te.com/en/product-ANT-315-CW-HW-SMA.html) | 1 interchangeable | SMA male |
| `SUB-GHz` | 433 MHz | [TE `ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | 1 interchangeable | SMA male |
| `SUB-GHz` | 868/915 MHz | [Taoglas `TI.08.C.0112`](https://www.taoglas.com/datasheets/TI.08.C.0112.pdf) | 1 interchangeable | right-angle SMA male |
| `VHF/UHF` | VHF 136–174 MHz | [Hytera `AN0155H13`](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h13.html) | 1 interchangeable | SMA male |
| `VHF/UHF` | UHF 400–470 MHz | [TE `ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | 1 interchangeable | SMA male |
| `FM/SW RX` | receive 25–1300 MHz | [Comet `SMA-W100RX2`](https://www.comet-ant.co.jp/product/638/) | 1 | SMA male |
| `AM/LW LOOP` | LW 153–279 kHz; AM 520–1710 kHz | Leshy2 [`L2-ANT-AM-LW-001`](../hardware/architecture/am-lw-pod.json) | 1 | SMA male |

The kit contains two separate `ANT-433-CW-QW-SMA` units. Its specification
covers 400–470 MHz and up to 10 W, so one unit serves the 433-MHz profile and
the other serves UHF voice. This reduces unique SKUs without moving one antenna
between two connected paths.

## Connectors and safe transmit

- The two native ports are RP-SMA. The antenna requires an RP-SMA male plug
  with a socket centre contact.
- The other seven ports are standard SMA. The antenna requires an SMA male
  plug with a centre pin; a visually similar RP-SMA plug is not compatible.
- Transmit always starts disabled. A selected profile, band or power limit is
  never restored after reset or a fault.
- A colour collar and package label must repeat the port name and band. The
  software profile alone is not evidence that the correct antenna is fitted.

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

## Selection and remaining qualification

An exact first target is selected for all 12 physical items. Availability
was checked at selection time: the volume TE/Taoglas parts have authorized
distributor stock, Ebyte accepts direct sample/quantity RFQs, and the Hytera
and Comet items are sold as finished accessories; the AM/LW pod has a controlled
assembly specification made from currently orderable parts. The dated price and stock
snapshot is retained in the [machine manifest](../hardware/architecture/antenna-kit.json).

The kit is not yet production-qualified. It still needs independent alternates
and assembled-device measurements for match, receive
sensitivity, EIRP, harmonics, coexistence, connector load and operation with
all nine ports populated. `SMA-W100RX2` is documented only from 25 MHz, so no
below-25-MHz performance is claimed before hardware testing.
