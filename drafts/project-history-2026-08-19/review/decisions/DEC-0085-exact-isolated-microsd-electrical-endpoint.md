# DEC-0085 — exact isolated microSD electrical endpoint

- Status: **accepted; Проведено ревью for paper electrical scope**
- Finding: [`FND-0089`](../findings/FND-0089-microsd-endpoint-was-backpowered-and-unprotected.md)
- Architecture: [`STO-0001`](../architecture/STO-0001-exact-isolated-microsd-endpoint.md)
- Propagation review: [`REV-0005AP`](../reviews/REV-0005AP-microsd-endpoint-propagation.md)

## Decision

1. Keep active exact socket `Hirose DM3AT-SF-PEJM5` and its eight card
   contacts, shield and normally-open insertion switch as the paper boundary.
2. Keep `TPS22919DCKR`, add exact input/output energy, a physical fail-low ON
   resistor and direct QOD discharge. Card and card-side logic are powered only
   for an active storage session.
3. Isolate SCK, CMD and CS with card-powered `SN74LVC3G34DCUR`. Return DAT0/MISO
   through card-powered `SN74LVC1G125DCKR`, with `OE_N = SD_CS_N`. Both devices
   must retain Ioff partial-power behavior; substitutes need equivalent proof.
4. Populate separate 10-kOhm switched-rail pulls on CMD and DAT0…DAT3. Hold
   host SCK low and D0/D1/card-CS/display-CS high with independent main-side
   reset defaults.
5. Populate four exact 22-Ohm active-output series resistors. Shunt tuning stays
   DNP until shared-bus HIL proves a need.
6. Use two exact `TPD4E05U06DQAR` arrays at the socket for CLK, CMD, DAT0…DAT3,
   VDD and detect, with short ground returns and an independent shield return.
7. Ground `DETECT_B`; route `DETECT_A` through ESD and an exact 1-kOhm resistor
   to P21, with a 10-kOhm `3V3_MAIN` pull-up and 100-nF filter. Detection remains
   available while card power is off.
8. After every card-power cycle, firmware must initialize the card into SPI
   mode while every other CS is high before display transactions resume. Clean
   removal drains writes; unexpected removal reports a possible corrupt tail
   and enters checked recovery.

## Consequences

- S3 and slow-I/O pin budgets do not change.
- The inactive card cannot back-power the host and cannot drive display QSPI D1.
- The added paper BOM is approximately USD 0.75…1.00 at quantity 100 excluding
  the already-selected socket; this is accepted under the delegated minor-cost
  improvement rule.
- Socket placement/access, real media, throughput, final damping, hot-plug,
  ESD/short/brownout and filesystem-recovery HIL remain blockers.
- This decision does not authorize KiCad, a socket footprint freeze or a final
  mechanical layout.
