# H3 parameters and models · historical R1

[Русский](parameter-model-register.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Virtual verification](virtual-verification.md)

This is the H3 calculation input register: for every actually fitted device type it links the MPN, instances, schematic ownership, primary source, required parameter groups and future model method. The full table remains machine-readable so the product site stays readable.

## Coverage

- `1081` instances and `218` used device types.
- A primary source exists for `218` of `218` types; missing: `0`.
- `74` types already have structured parameters; `144` are extracted by class during H3.1–H3.6.
- There are `0` local vendor models; an admissible analytic, behavioral or circuit method is frozen in `H3.0.3`, never invented silently.
- Two H2 document mirrors are superseded here by exact official Hirose and JAE sources without changing accepted H2.

## What cannot honestly close before receiving a sample

The exact `HMX035CTFT-001` tail/connector, optics and backlight plus the `ES8311` supplier and lot remain H5 incoming inspection. Their published-data electrical analysis still runs in H3.

## Closed architecture gate

`H3-NRF24-LIFECYCLE` is closed with option A: three `E01-ML01IPX` modules remain because they provide the required full nRF24 hardware behavior. The nRF24 family is not recommended for new designs, so H5 must verify supplier, silicon marking and reserve availability. A modern nRF52 is 2.4-GHz-only and supports over-air ESB compatibility, but is not an SPI/register drop-in replacement.

**Historical R1-chain status:** `H3.0.2-R1` is reviewed; the later marker in that chain is `H3.6.1-R1`. The current hardware marker is `H1-R2.32`.

[213-row machine register](../hardware/verification/generated/H3-VRF02-parameter-inventory.json).
