# Display electrical verification

[Русский](display-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)

H3.3.1 checks one complete chain: ST77922 supply → backlight power path → direct-QSPI/touch timing. This is a paper review of serial parts and real contacts; raw HMX035CTFT-001 specimen measurements remain HIL.

## Supply

- Serial `Vishay TNPW040243K7BEED` / `Vishay TNPW040210K0BEED` set `3.222000 V` nominal.
- With ±1.5% VREF, ±0.1% resistors and mandatory `0.020 Vpp`, the raw endpoint is `3.158510…3.285658 V`.
- After the separate `0.050 V` path budget the connector retains `3.108510…3.285658 V`: `458.510 mV` above VDD minimum and `14.342 mV` below the common 3.3-V maximum.

## Backlight

The donor schematic had been misread: `R31=0R` is in the common LEDK path while `R33=10R` is in Q4's gate. The power path now uses `Yageo RC0402JR-070RL`. TPS2553 does not regulate brightness: it latches a fault at `174.000…234.000 mA`, retaining at least `45.000%` over the donor's 120-mA mode. Actual current and brightness remain specimen measurements.

## Direct QSPI and touch

The initial cap is `40 MHz`: `25.000 ns` period versus 16 ns minimum; `12.500 ns` high/low versus 7 ns. CS gets at least `25.000 ns` setup/hold. One non-preemptible 1-ms quantum carries up to `20000` bytes / `10000` RGB565 pixels; a full frame is `15.360 ms` payload-only, so menus and waterfall use dirty regions rather than full-frame redraw. Touch remains ≤400 kHz.

## Corrected by review

1. Removed the possible ST77922 excursion above 3.3 V.
2. Removed the mistaken 10-ohm power resistor that would have taken about 1.2 V from the backlight.

## What remains physical

- measure protected-rail ripple and connector voltage at every accepted load and temperature corner
- confirm HMX035CTFT-001 tail, ST77922 identity, VDD/VDDI ramp equality and reset/readback on received specimens
- measure QSPI edges, CS-high high-Z/contention and shared-microSD throughput before raising the 40-MHz initial cap
- measure actual panel backlight current, brightness, PWM EMI, temperature and TPS2553 latch recovery

The three replacements add `0.4452 USD` per unit at quantity 100. **H3.3.1 is reviewed; the exact current marker is `H3.3.4`.**

[Machine H3-VRF31 package](../hardware/verification/generated/H3-VRF31-display.json).
