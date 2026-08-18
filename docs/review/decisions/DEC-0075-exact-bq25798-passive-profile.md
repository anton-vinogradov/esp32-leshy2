# DEC-0075 — exact 750-kHz BQ25798 passive and reset profile

- Статус: **Принято автоматически в делегированных пределах**
- Дата: 2026-08-18
- Owner authority: component substitutions/selections may be made without a new question when budget is not increased dramatically and device functionality is preserved
- Analysis: [`PWR-0014`](../architecture/PWR-0014-exact-bq25798-passive-profile.md)
- Propagation review: [`REV-0005AF`](../reviews/REV-0005AF-bq25798-passive-profile.md)

## Decision

1. `BQ25798RQMR` uses its physical 2S/750-kHz profile: exact 8.2-kOhm PROG
   strap, `MWSA0503S-2R2MT` 2.2-uH/7-A inductor and the complete individually
   instantiated VBUS/PMID/SYS/BAT/BTST/REGN/SDRV capacitor network from
   `PWR-0014`.
2. A 44.2-kOhm/100-kOhm ILIM divider provides an independent approximately
   2.71…3.29-A physical envelope. The negotiated BQ IINDPM register is always
   the lower limit; TPS writes and verifies it before charge enable.
3. A third independent `B57332V5103F360` with 5.23-kOhm/30.1-kOhm bias gives
   BQ its own non-ignored temperature gate. Its mechanical coupling remains
   an explicit I3/HIL dependency.
4. TPS `LDO_3V3` supplies the exact 10-kOhm SCL/SDA/INT pull-ups. CE has an
   exact 10-kOhm pull-up to BQ REGN; TPS GPIO1 is open-drain and sinks only
   after valid image, source contract and IINDPM readback.
5. Both VAC inputs tie to VBUS; both unused ACDRV outputs tie to ground. SDRV
   uses the current Rev-C 1-nF/50-V/0402 termination. D+/D-/QON/disabled STAT
   remain no-connects. No backup/OTG/MPPT/BC1.2 behavior is introduced.
6. Exact product USB-C/USB2 protection is corrected back to dependent step I4.
   TPS25751/CAT24C512 support passives become the next true I3 paper item.

## Consequence

The accepted 9-V/3-A and 15-V/2-A source classes remain usable, while reset,
weak-source and thermal behavior fail conservatively. The larger 750-kHz
magnetics and 1206 bulk bank add no user-visible limitation and are expected
to improve efficiency/EMI margin for modest passive cost. This is a reviewed
working-design decision, not authorization to begin KiCad.
