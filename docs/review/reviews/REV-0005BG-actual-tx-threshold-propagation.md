# REV-0005BG — actual-TX threshold and AON-boundary propagation

Статус: **проведено ревью; measured calibration/physical HIL не выполнено**.

| Проверка | Результат |
|---|---|
| primary sources | pass: current TI TLV1824/TCA9534A/SN74LVC3G07 and ADI LTC5532/AD8314 sources checked |
| comparator packages | pass: both exact TSSOP-14 packages have V+/V− and separate 100-nF bypass |
| eight thresholds | pass: 32 separate exact resistor placements; seven RF 100k/10k/1M/10k and IR 100k/12k/1M/10k |
| nominal arithmetic | pass: RF 0.327-V assert/0.297-V clear; IR 0.384-V assert/0.350-V clear |
| open-drain pulls | fixed: every EV_N output has its own 10-kOhm AON pull-up |
| source mask | fixed: VCC/GND/bypass, A2/A1/A0=000, RP-local SDA/SCL and test-only INT are explicit |
| aggregate | fixed: independent 10-kOhm `ANY_TX_AON_N` pull-up and exact 2.2-kOhm LED resistor |
| power domains | fixed: exact triple Ioff/open-drain buffer plus three main-domain pull-ups replace direct AON→C5/RP exposure |
| runtime semantics | unchanged: C5 GPIO23/24 and RP GPIO22 remain active-low; no firmware remap |
| GPIO/functions | unchanged: no contact, radio, UI, STOP or service capability change |
| diagram | pass: generated atlas and both root product diagrams are vertical and show every new placement as a separate MPN/role box |
| BOM | pass: 858 placements / 188 used lines / 155 current orderability / four remaining gap families |
| regression | pass: 65 hardware architecture tests plus generated-artifact check |
| HIL | open: threshold distributions, false states, timing, temperature/lots, optical coupling and AON/main transition injection |

## Сводка исправленных несоответствий

| Было | Исправлено | Влияние |
|---|---|---|
| eight abstract threshold endpoints | 32 exact resistor placements | first PCB population becomes buildable; production calibration remains open |
| comparator power/bypass omitted | both supply pairs and two local bypasses exact | required support restored |
| TCA9534A support partly prose-only | supply/bypass/address/bus routes exact | source-mask circuit becomes physical |
| eight pull-ups only claimed in prose | eight exact output pull-ups | deterministic EV_N idle |
| ANY-TX LED path acted as implicit pull-up | independent logic pull-up plus exact LED resistor | aggregate logic no longer depends on LED leakage |
| AON nodes directly exposed C5/RP | triple open-drain isolation and three main pull-ups | power-off back-feed risk removed |

## Verdict

`FND-0110/SAFE-0003/DEC-0101` close the actual-TX paper-instantiation residue
without changing product behavior. I8 qualification continues with 33 source,
188 cost and 188 alternate dispositions plus the four explicit physical gap
families. KiCad and the paused integrated mockup remain unauthorized.

Subsequent `FND-0111/BOM-0009/REV-0005BH` closes 32 of those 33 source gaps;
the numbers above remain the reviewed threshold-repair snapshot rather than
the current I8 sourcing count.
