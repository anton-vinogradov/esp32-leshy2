# REV-0005AI — diagnostic lockout propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0078`](../decisions/DEC-0078-hardware-diagnostic-refractory-lockout.md)
- Analysis: [`PWR-0017`](../architecture/PWR-0017-hardware-diagnostic-refractory-lockout.md)
- Corrected finding: [`FND-0082`](../findings/FND-0082-tpul-pin-map-and-repeat-pulse-gap.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Physical package | `2Q` corrected to WQFN contact 5; `VCC` corrected to contact 16; regression tests added |
| One-pulse bound | channel 1 remains the sole gate source and production still accepts only `25…50 ms` |
| Repetition bound | channel-1 falling edge starts channel 2; complementary channel-2 output clears channel 1 for `>=350 ms` |
| Race/reset behavior | first pulse completes before lockout starts; POR gives inactive Q/active complementary Q; PA22 remains externally low by default |
| Exact passives | `RC0402FR-07620KL` and `C1608X7R1C105K080AC`; measured acceptance `350…860 ms` |
| Load | 2×`CRM2512-FX-20R0ELF` in parallel preserves 10 Ohm, raises nominal continuous rating from 1 W to 4 W and splits heat |
| Hostile repetition | 50-ms/350-ms worst hardware cadence is below hot derated combined load rating without firmware credit |
| Firmware | stable-VDD delay `>=1 ms`, normal retry floor `>=10 s`, missing/misaligned/saturated evidence fails closed |
| Threshold provenance | exact numbers wait for exact cell MPN and SoC/temperature/contact HIL; no universal invented resistance limit |
| Product diagram | timer role, both timer passives and both physical load resistors appear as separate exact-MPN nodes |
| Cost/GPIO | no active part or GPIO added; net BOM increase below roughly `$0.30` at 100-piece visible pricing |

## Remaining gates

Exact cell selection and droop distribution, channel-1/channel-2 lot timing,
repeated-trigger waveform, timer startup, 300-mm²-equivalent heat-spreading
copper, resistor/MOSFET/holder temperature and enclosure HIL remain mandatory.
The corrected paper contract receives **«Проведено ревью»** and does not
authorize KiCad.
