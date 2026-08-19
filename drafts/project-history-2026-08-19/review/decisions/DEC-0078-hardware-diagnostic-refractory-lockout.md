# DEC-0078 — hardware refractory lockout for pack diagnostics

- Статус: **Принято как safety correction; проведено ревью бумажной схемы**
- Дата: 2026-08-18
- Analysis: [`PWR-0017`](../architecture/PWR-0017-hardware-diagnostic-refractory-lockout.md)
- Corrected finding: [`FND-0082`](../findings/FND-0082-tpul-pin-map-and-repeat-pulse-gap.md)
- Propagation review: [`REV-0005AI`](../reviews/REV-0005AI-diagnostic-lockout-propagation.md)

## Decision

1. Retain exact `Texas Instruments TPUL2G223BQBR`, with its corrected WQFN-16
   physical contact map.
2. Channel 1 remains the only diagnostic MOSFET gate authority and retains the
   accepted `25…50 ms` production pulse window.
3. Channel 2 becomes an independent refractory timer. The falling edge of
   channel-1 `Q` starts it; complementary `2Q` holds channel-1 `CLR` low for at
   least `350 ms` under the complete paper corner screen.
4. Use exact `Yageo RC0402FR-07620KL` and
   `TDK C1608X7R1C105K080AC` for the channel-2 timer. Production accepts a
   measured `350…860 ms` hardware lockout; the lower bound protects the load
   and the upper bound keeps the configured circuit inside the TI range.
5. Replace the single 10-Ohm/1-W load with two parallel exact
   `Bourns CRM2512-FX-20R0ELF` parts. Effective resistance is `10 Ohm ±1%`,
   continuous rating is 4 W at 70 °C and each branch receives half the pulse
   and repetition heat.
6. Normal firmware waits at least 10 seconds between attempts. HIL may increase
   this interval for an exact cell profile, but cannot reduce it below 10 s.
7. Droop/contact acceptance remains fail-closed and cannot receive a production
   number until an exact qualified cell MPN and its temperature/SoC HIL matrix
   are available.

## Consequence

One additional 2512 resistor and two small timing passives add well below one
dollar at prototype quantity and roughly `$0.30` at 100-piece visible pricing.
No GPIO or new active device is added. A software fault can slow diagnostics by
requesting rejected retries, but cannot convert the diagnostic branch into a
near-continuous heater.

This closes physical pin provenance and paper hardware cooldown. It does not
authorize KiCad and does not claim final cell-dependent droop thresholds.

