# REV-0005BF — MAX17320 support repair propagation

Статус: **проведено ревью; physical/HIL не выполнено**.

| Проверка | Результат |
|---|---|
| exact source/contact provenance | pass: MAX17320 Rev.12 и MSPM0C1104 SLASF90D |
| IN/CP/AOLDO/REG3/REG2 | pass: independent exact series/bypass positions instantiated |
| exact 2S mapping | pass: CELL1/CELL2/CELL3 short, only CELL1/BATTS balancing branches and both filters |
| balance power | fixed: low-power abstract resistor replaced by exact 49,9-Ω 0,66-Вт 1206; 0,267-Вт paper worst screen recorded |
| CHG/DIS and PCKP | pass: both gate capacitors and exact 1-kΩ PCKP series instantiated |
| shunt | fixed: CSP/CSN Kelvin routes now accompany explicit END1/END2 force current path |
| unused inputs | pass: ZVC NC; TH3/TH4 fixed low |
| private I²C and ALRT | pass: separate exact pull-ups instantiated |
| PFAIL | fixed: push-pull MAX output no longer directly drives a potentially lower-voltage MSPM0 input |
| shared IRQ | fixed: standard PA23 drives an external NMOS; drain is passive on `SYS_INT_N` |
| MSPM0 support | pass: exact 10-µF/100-nF VDD and 47-kΩ/10-nF NRST plus test point |
| GPIO/function | unchanged: no contact-budget, radio, UI, STOP or service capability change |
| diagram propagation | pass: generated atlas and both target diagrams contain 25 separate MPN/role boxes |
| BOM propagation | pass: 816 placements / 187 used lines / five remaining explicit physical-gap families |
| physical qualification | open: layout, lot, thermal, source handover, balance/current accuracy and fault HIL |

## Verdict

`FND-0109/PWR-0022/DEC-0100` close the narrowly reopened I3 paper-support
subblock. The repair is a prerequisite correction found during I8, not a new
product feature. I8 sourcing/lifecycle/cost/alternate qualification remains
active; KiCad and the integrated physical mockup remain unauthorized.

