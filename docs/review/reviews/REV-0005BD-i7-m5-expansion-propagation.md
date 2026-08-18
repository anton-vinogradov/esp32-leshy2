# REV-0005BD — I7 M5 expansion propagation

Статус: **проведено ревью; physical/HIL не выполнено**.

| Проверка | Результат |
|---|---|
| exact U214 contacts and real exposed signals | pass: official 14-contact product/schematic map; no invented pin |
| native Unit contact truth | pass: 5 V, GND and two signals only; connector MPN remains explicit TBD |
| false presence signal | fixed: `ACCESSORY_PRESENT_N` removed; P26 is physical `UNIT_READY` |
| independent unused-interface off | pass: P17/P05 plus separate branch eFuses; one branch need not energize the other |
| reverse source/backfeed containment | pass in paper topology: one `TPS259470LRPWR` per exposed 5-V output; HIL open |
| U214 non-I2C isolation | pass: five outbound and four return paths through three exact Ioff buffers |
| U214 I2C isolation | pass: complete `TCA4307DGKR` power/pulls/EN/READY path; stuck-low HIL open |
| connector ESD | pass: 3× U214 + 1× native Unit exact low-capacitance arrays |
| signal enable before rail valid | rejected by two exact supervisors and main-domain READY pull-ups |
| MCU GPIO budget | pass: unchanged |
| slow-I/O budget | pass: P05 consumed, exact `24/0/0` |
| exact-part availability at selection | pass: TXS0102DCUR and 110-kOhm exact resistor have current authorized/manufacturer paths; reused exact parts retain their registers |
| diagram propagation | pass: generated atlas and EN/RU product diagrams contain separate physical boxes, MPN and roles |
| generic high-throughput port | correctly absent; concrete future profile must derive transport |
| physical qualification | open: connectors, specimen, power/fault/timing/no-back-power/coexistence HIL |

## Verdict

`DEC-0098/EXP-0001` close the M5 external-expansion paper electrical subblock.
They do not authorize KiCad or claim hot-plug/connector/profile qualification.
At this review checkpoint I7 continued with independent USB/debug/recovery
service endpoints. `FND-0106…0108/SVC-0002/DEC-0099/REV-0005BE` subsequently
close that remaining paper subblock and advance the dependency chain to I8.
