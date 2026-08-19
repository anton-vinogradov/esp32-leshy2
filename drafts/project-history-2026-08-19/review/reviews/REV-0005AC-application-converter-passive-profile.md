# REV-0005AC — application-converter passive-profile propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0072`](../decisions/DEC-0072-exact-converter-energy-feedback-passives.md)
- Analysis: [`PWR-0011`](../architecture/PWR-0011-application-converter-passive-profile.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Datasheet prerequisites | TPS629203 VSET/MODE and TPS564252 divider/CIN/COUT/Cff rules checked against official sources |
| Lifecycle | obsolete 45.0-kOhm Yageo candidate rejected; every fitted exact MPN is active/current |
| Electrical arithmetic | fixed nominal and tolerance voltages, LC poles and eFuse OVLO separation pass the paper screen |
| Machine source | 24 physical passive instances and their exact two-terminal routes replace abstract converter networks |
| Generated artifacts | ledger and vertical principled atlas regenerate from the same source |
| Target product pages | English/Russian diagrams show every physical instance separately with MPN and role |
| Cost | approximately `$1.8` per board at the checked 100-piece snapshot; nine robust 1210 capacitors dominate |

## Corrections made

- `RC0402FR-0745KL` is no longer treated as orderable;
- AON 3.3 V is explicitly selected by open `FB/VSET`, not an unnamed network;
- every TPS564252 now has a separate local input loop and two-capacitor output
  bank rather than one shared or abstract capacitance;
- the external full tolerance voltage is cross-checked below the eFuse OVLO
  floor.

## Remaining gates

Exact EN/PG/pull/qualifier resistor values subsequently close in
`PWR-0012/DEC-0073/REV-0005AD`. Effective-capacitance measurement,
load-step/ripple/EMI, hot loss, copper/Kelvin layout and fault HIL remain open.
The result is **«Проведено ревью»** at the paper electrical-profile level and
does not authorize KiCad.
