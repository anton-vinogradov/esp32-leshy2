# REV-0005AK — source-sequence propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0080`](../decisions/DEC-0080-exact-aon-pg-por-main-sequence.md)
- Analysis: [`PWR-0019`](../architecture/PWR-0019-exact-source-sequence-and-power-reserve.md)
- Finding: [`FND-0084`](../findings/FND-0084-abstract-main-source-sequencer.md)
- Later containment review: [`REV-0005AL`](REV-0005AL-internal-rail-containment-propagation.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Source validity | only admitted battery or protected USB can create `BQ25798 SYS` |
| AON start | `SYS → TPS629203.EN` remains a direct hardware strap |
| AON qualification | exact pulled-up `AON_PG_N → TPS3808.MR_N`; after `DEC-0081`, pull-up and 3.07-V SENSE are on independently protected AON |
| Delay | exact existing CT network remains between valid AON and POR release |
| Main enable | exact `TPS3808.RESET_N/POR_N → TPS564252 #MAIN.EN` replaces the abstract sequencer |
| Pulls | exact 10-kOhm POR pull-up plus 100-kOhm main fail-low pull; about 3.0-V nominal release |
| Failure | AON PG/SENSE loss asserts POR, disables main and leaves AON safety outputs fail-safe |
| Charge power | 85% input-power reserve and dynamic system-first current cap propagated to hardware/firmware contracts |
| Diagram | each resistor and active device remains a separate exact-MPN box |
| Cost | no new unique MPN; one additional exact 10-kOhm position and an existing 100-kOhm value reused |

## Remaining gates

Measure AON PG/MR/SENSE/RESET, main EN/PG and all application rails during
battery admission, USB 5/9/15-V attach/remove, weak-source DPM, pack removal,
brownout and repeated faults. Source sequencing and calculated logic levels
receive **«Проведено ревью»** at paper level; measured transition behavior
does not.
