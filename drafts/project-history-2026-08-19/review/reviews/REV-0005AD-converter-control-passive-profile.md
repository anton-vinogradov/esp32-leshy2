# REV-0005AD — converter control-passive propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0073`](../decisions/DEC-0073-exact-converter-control-passives.md)
- Analysis: [`PWR-0012`](../architecture/PWR-0012-exact-converter-control-passives.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Datasheet prerequisites | TPS629203 EN/PG, TPS564252 EN/PG and TPS259470L EN ceilings/thresholds checked against official sources |
| Reset safety | direct AON strap is always-on; DEC-0080 later changes main to a 10-kOhm POR pull-up/100-kOhm fail-low pair while voice/accessory retain 10-kOhm pulls |
| PG loading | AON approximately 70 uA below 1 mA; optional PG approximately 0.320 mA including base current below 4 mA |
| Fault aggregate | one 10-kOhm pull-up requires at most 0.33-mA sink and preserves the reviewed NPN forced-beta margin |
| Machine source | DEC-0080-amended current map has ten separate physical resistors and exact two-terminal routes; the original nine-part review remains historical |
| Generated/target diagrams | vertical atlas and both product landing diagrams show every new physical instance separately |
| BOM/cost | four already-used MPNs after DEC-0080; no new feeder line and still below one cent of checked resistor material per board |
| Firmware | fixed hardware truth table plus AON-PG/POR source sequence is the runtime input |

## Corrections made

- the AON enable is now an explicit direct hardware strap, not an unnamed
  resistor whose interaction with the dynamic internal pull-down was unproved;
- the low-IQ AON PG pull is 47 kOhm rather than the application-domain 10 kOhm;
- base resistors, optional PG pulls, all converter EN defaults and the shared
  fault pull are actual one-component instances rather than prose-only values.

## Remaining gates

Startup/shutdown deadlines, temperature, another-source-low behavior,
reverse-BE cycling, brownout and multi-fault injection remain prototype HIL.
The paper schematic result receives **«Проведено ревью»** and does not
authorize KiCad.
