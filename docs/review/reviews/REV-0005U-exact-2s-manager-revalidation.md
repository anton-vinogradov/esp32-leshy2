# REV-0005U — exact 2S manager revalidation

- Статус: **Проведено ревью фактов; owner gate IMP-0054 открыт**
- Дата: 2026-08-18
- Topology: [`DEC-0065`](../decisions/DEC-0065-supervised-2s-battery-topology.md)
- Device review: [`PWR-0005`](../architecture/PWR-0005-replaceable-2s-manager-options.md)
- Proposal: [`IMP-0054`](../improvements/IMP-0054-fail-closed-2s-admission-manager.md)

## Revalidation matrix

| Check | Result |
|---|---|
| exact gauge order code | pass: ADI Rev.12 lists `MAX17320G20+T` as 24-TQFN, I2C, SHA column blank; `G22` is the SHA-included I2C code |
| exact gauge contacts | pass: all 24 physical contacts enumerated; internal NC pads are not promoted to pins; 2S cell-tap passive connection remains an explicit next circuit gate |
| protection/default state | pass at architecture level: high-side CHG/DIS, four thermistor inputs and `ALRT` FET override are exposed; override requires factory-programmed/read-back `OvrdEn=1` before energized assembly |
| exact controller order code | pass: TI lists active `MSPM0C1104SDGS20R`, DGS20 VSSOP, 16-kB flash/1-kB SRAM |
| controller physical fit | pass: reset, SWD, UART, system I2C without losing reset, local bit-banged gauge bus and remaining control GPIO are physically exposed |
| controller power | conditional pass: low-clock/duty operation fits the `<2 mA` concept; 24-MHz and flash programming do not, so fixture/system-rail supply isolation is mandatory and remains exact-circuit work |
| service/recovery | pass at boundary: NRST, SWDIO, SWCLK, UART, VDD/VSS and gauge I2C/NVM pads remain accessible; blank-device programming uses fixture power |
| sourcing/cost | pass as current evidence: exact A pair is active and stocked at checked distributors, about `$4.47/100` before common power parts; B gauge remains zero-stock in the checked snapshot |
| openness | pass: candidate exact G20 has no SHA feature; owner firmware/recovery remains available and no irreversible production lock is required |
| selection | open: factual review does not accept A/B/C for the owner |

## Conclusion

The exact-device and real-contact comparison receives **«Проведено ревью»**.
Option A remains recommended, but no manager is projected into the target
diagram or machine map until `IMP-0054` is answered.

