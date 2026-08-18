# REV-0005AF — BQ25798 passive and reset-profile propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0075`](../decisions/DEC-0075-exact-bq25798-passive-profile.md)
- Analysis: [`PWR-0014`](../architecture/PWR-0014-exact-bq25798-passive-profile.md)
- Corrected finding: [`FND-0079`](../findings/FND-0079-product-usb-is-an-i4-consumer.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Current TI revision | Rev-C VAC1/VAC2, ACDRV1/2, SDRV, QON and 1-A reset defaults represented exactly |
| 2S/frequency | 8.2-kOhm PROG strap and 2.2-uH inductor force 2S/750 kHz at POR |
| Peak-current paper fit | <2.85-A p-p worst buck ripple; <6.43-A device-limited peak against 7-A exact inductor rating |
| Energy banks | 12 separate 10-uF, three separate 100-nF, two bootstrap, REGN and SDRV capacitor instances |
| Source ceiling | 44.2k/100k physical ILIM gives about 2.71-3.29 A; negotiated register always lower |
| Charge reset | exact REGN pull-up keeps CE high at reset; GPIO1 is open-drain only and enables after IINDPM readback |
| Temperature | third independent B57332V5103F360 plus 5.23k/30.1k; TS remains non-ignored |
| USB isolation | BQ D+/D- remain NC; product connector/USB2 protection correctly deferred to I4 |
| Special pins | VAC1/2 to VBUS, ACDRV1/2 to GND, SDRV 1 nF to GND, QON/STAT NC |
| Machine/diagrams | 31 physical charger-support instances and exact routes added; no different components share one box |
| Firmware | 750-kHz physical profile, 1-A reset charge, <=2-A runtime charge, contract-derived IINDPM and fail-off gates propagated |

## Corrections made

- `FND-0079` removes product USB from the I3 remainder and exposes the real
  TPS25751/CAT24C512 support-passive dependency;
- the former block-level charger omitted physical energy storage, special-pin
  terminations, BATP/TS/ILIM and reset pulls;
- CE is no longer described as a generic external pull: it is exact,
  REGN-referenced and driven only by a TPS open-drain sink;
- the accepted 9-V/3-A input is preserved without treating a static resistor
  as USB negotiation.

## Remaining gates

TPS25751/CAT24C512 passives/straps, cell/NTC mechanics, hot loss and EMI,
source attach/remove, negotiated-current matrix, watchdog/reset, capacitor
effective value and inductor thermal/saturation HIL remain open. The BQ paper
circuit receives **«Проведено ревью»** and does not authorize KiCad.
