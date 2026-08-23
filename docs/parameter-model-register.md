# H3 parameters and models

[Русский](parameter-model-register.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Virtual verification](virtual-verification.md)

This is the H3 calculation input register: for every actually fitted device type it links the MPN, instances, schematic ownership, primary source, required parameter groups and future model method. The full table remains machine-readable so the product site stays readable.

## Coverage

- `1028` instances and `213` used device types.
- A primary source exists for `213` of `213` types; missing: `0`.
- `64` types already have structured parameters; `149` are extracted by class during H3.1–H3.6.
- There are `0` local vendor models; an admissible analytic, behavioral or circuit method is frozen in `H3.0.3`, never invented silently.
- Two H2 document mirrors are superseded here by exact official Hirose and JAE sources without changing accepted H2.

## What cannot honestly close before receiving a sample

The exact `HMX035CTFT-001` tail/connector, optics and backlight plus the `ES8311` supplier and lot remain H5 incoming inspection. Their published-data electrical analysis still runs in H3.

## Open architecture question

`H3-NRF24-LIFECYCLE`: the three selected `E01-ML01IPX` modules provide the required full nRF24 hardware behavior, but the nRF24 family is not recommended for new designs. A modern nRF52 supports over-air ESB compatibility but is a programmable SoC, not an SPI/register drop-in replacement. An automatic substitution would therefore reopen requirements, recovery, firmware, pinout and H2.

**Current marker:** `H3.0.2` — inventory complete; gate `H3-NRF24-LIFECYCLE` is pending.

[213-row machine register](../hardware/verification/generated/H3-VRF02-parameter-inventory.json).
