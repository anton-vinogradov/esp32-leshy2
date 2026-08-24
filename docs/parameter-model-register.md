# H3 parameters and models

[Русский](parameter-model-register.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Virtual verification](virtual-verification.md)

This is the H3 calculation input register: for every actually fitted device type it links the MPN, instances, schematic ownership, primary source, required parameter groups and future model method. The full table remains machine-readable so the product site stays readable.

## Coverage

- `1035` instances and `217` used device types.
- A primary source exists for `217` of `217` types; missing: `0`.
- `71` types already have structured parameters; `146` are extracted by class during H3.1–H3.6.
- There are `0` local vendor models; an admissible analytic, behavioral or circuit method is frozen in `H3.0.3`, never invented silently.
- Two H2 document mirrors are superseded here by exact official Hirose and JAE sources without changing accepted H2.

## What cannot honestly close before receiving a sample

The exact `HMX035CTFT-001` tail/connector, optics and backlight plus the `ES8311` supplier and lot remain H5 incoming inspection. Their published-data electrical analysis still runs in H3.

## Closed architecture gate

`H3-NRF24-LIFECYCLE` is closed with option A: three `E01-ML01IPX` modules remain because they provide the required full nRF24 hardware behavior. The nRF24 family is not recommended for new designs, so H5 must verify supplier, silicon marking and reserve availability. A modern nRF52 is 2.4-GHz-only and supports over-air ESB compatibility, but is not an SPI/register drop-in replacement.

**Status:** `H3.0.2` is reviewed; current marker is `H3.4.1`.

[213-row machine register](../hardware/verification/generated/H3-VRF02-parameter-inventory.json).
