# FND-0096 — nRF quiet state and TX evidence were not physical

- Status: **исправлено на paper electrical уровне; Проведено ревью subblock**
- Scope: `I6` three-nRF electrical endpoint
- Architecture: [`N24E-0001`](../architecture/N24E-0001-exact-three-nrf-electrical-endpoint.md)

## Finding

The previous architecture had the right functional allocation — three
independent E01-ML01IPX radios, one shared switched rail and dedicated RP2354
PIO/DMA ownership — but two implementation claims were stronger than the
circuit:

1. `N24_QUIET` said that all six digital paths per radio were isolated and
   high-Z after rail-off, while RP CE/CSN/SCK/MOSI/MISO/IRQ still reached the
   module directly. Firmware pin parking cannot prove absence of back-power.
2. The `LTC5532` evidence input was an abstract, non-directional RF tap. Receive
   energy could assert it, tap loss was unknown, and the route did not prove
   reliable detection of the E01 module's minimum output.
3. An initially attractive `HHM2510B1` coupler covers only 2400–2500 MHz and
   would silently omit nRF channels 101–125. It was rejected before entry into
   the source of truth.
4. The Ebyte receptacle is called `IPX`, but no exact mating family is stated.
   Treating it as U.FL would turn a trade label into an unsupported mechanical
   fact.

## Correction

| Gap | Exact correction | Result |
|---|---|---|
| host-to-module isolation | one switched-rail `74LVC126APW,118` per radio | CE/CSN/SCK/MOSI disappear through specified Ioff at VCC=0 |
| module-to-host isolation | one switched-rail `74LVC2G126DC,125` per radio | MISO/IRQ cannot back-power RP or float the host input |
| signal defaults | exact 10-kOhm pulls on both domains plus six 22-Ohm output-source resistors per radio | CE low, CSN/IRQ high and clock/data parked deterministically |
| module energy | 10-uF + 100-nF per module; exact 1-uF switch input and ON pull-down | three-radio transients and reset-off state are represented physically |
| forward sample | one `DC2337J5010AHF` per radio, configuration 2 | 2400–2525 MHz is covered with 10.0–11.2-dB coupling and ≤0.25-dB mainline loss |
| detector | one AON `AD8314ACPZ-RL7`, 52.3-Ohm shunt and 120-pF response capacitor per radio | detector response extends to 2.7 GHz; minimum TX sample is inside its typical range |
| reverse discrimination | exact 49.9-Ohm isolated-port termination | ordinary receive enters the reverse direction; strong-RX false positives fail safe |
| shutdown evidence | common BAT54/10-kOhm/1-uF ENBL hold | evidence remains active through QOD fall, then returns to low-current shutdown |
| module mate | explicit specimen microscope/fit/VNA gate | no U.FL compatibility is claimed without a received part |

## Remaining evidence

This correction is not a PCB or production pass. Received-module authenticity,
exact pigtail mate, insertion/return loss, 10-Mbit/s SPI, POR/QOD/no-backpower,
detector thresholds at channels 0/100/125 across temperature/lots and the full
T1 `3R/1T2R/2T1R/3T` fixture remain blocking HIL.

## Primary sources

- [Nexperia 74LVC126A](https://assets.nexperia.com/documents/data-sheet/74LVC126A.pdf)
- [Nexperia 74LVC2G126](https://assets.nexperia.com/documents/data-sheet/74LVC2G126.pdf)
- [TTM DC2337J5010AHF Rev. H](https://cdn.ttm.com/repository/products/wireless-xinger/10-20-30-dB-directional-couplers/DC2337J5010AHF/DC2337J5010AHF.pdf)
- [Analog Devices AD8314](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8314.pdf)
