# REV-0005AB — external-eFuse passive-profile propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0071`](../decisions/DEC-0071-post-start-accessory-transient-profile.md)
- Analysis: [`PWR-0010`](../architecture/PWR-0010-external-efuse-passive-profile.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Datasheet semantics | immediate startup `ILIM` and post-start-only `ITIMER` are separated |
| Exact components | eight physical passive instances have exact MPNs and real two-terminal contacts |
| Machine source | contract, instances and all `ILM/dVdt/ITIMER/OVLO/IN/OUT` routes are explicit |
| Generated artifacts | ledger and vertical pinout atlas regenerate from the accepted source |
| Target product pages | English/Russian behavior and one-part-per-box diagrams are current |
| Firmware contract | startup admission, bounded post-start transient, latch-off and OVLO recovery are consumable requirements |
| Cost | checked passives remain approximately `$0.10` per board at 100-piece pricing |

## Findings closed

- `ITIMER` is no longer described as a startup-current bypass.
- `2.0 A` is no longer presented as an unbounded or startup rating.
- the abstract external-output discharge circuit has been replaced by exact
  input/output capacitors and an exact bleeder resistor;
- OVLO recovery cannot silently reuse the normal-ramp assumption.

## Remaining gates

Specimen inrush, DC-bias capacitance, OVLO tolerance/transients, hot loss,
fault timing, discharge threshold, optional connector clamp and PCB return/
copper geometry remain open. The result is **«Проведено ревью»** at the
principle/electrical-profile level only and does not authorize KiCad.
