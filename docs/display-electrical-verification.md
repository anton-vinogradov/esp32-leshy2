# Display electrical contract · R2 input

[Русский](display-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Roadmap](roadmap.md)

The selected production assembly is EastRising `ER-TFT035IPS-6` configured
with capacitive touch `ER-TPC035-6`: 3.5-inch IPS, 320×480, `ILI9488` display
controller and `FT6236` touch controller. Its configured envelope is
56.54×84.96×3.76 mm and its 50-contact 0.5-mm FPC mates with stocked Hirose
`FH34SRJ-50S-0.5SH(50)` (`C3169104`) on passive adapter
`L2-DISP-ADP-001-B`.

## Interface contract

- Normal mode is direct 8-bit i8080 from S3. Interface straps are
  `IM2/IM1/IM0 = 0/1/1`.
- The conservative initial write clock is 24 MHz. One byte transfers every
  41.667 ns, above the ILI9488 40-ns minimum write cycle; high and low phases
  are 20.833 ns, above the 15-ns minima.
- Peak payload is 24 MB/s. A complete RGB565 frame is 307,200 bytes and takes
  12.8 ms payload-only; partial menu/waterfall updates remain preferred.
- The same panel supports ordinary 4-wire serial as a deliberate recovery
  strap. No QSPI capability is claimed.
- Touch stays on the local S3 I²C path with its own interrupt/reset contract.

## What remains for R2 H2/H3

R2 H2 must instantiate the exact 50-to-40 map, rail/backlight protection,
straps and timing nets in ECAD. R2 H3 then verifies voltage corners, reset and
power sequencing, backlight current/fault behaviour, i8080 timing and signal
integrity. H5 records written final-assembly acceptance for the customer-supplied
panel and FPC mating. H7 performs the first physical image/touch/backlight test.

The old `HMX035CTFT-001`/`ST77922` QSPI analysis is historical R1 evidence only
and is not part of the R2 order BOM or firmware contract.
