# DEC-0082 — I3 paper electrical closure

- Статус: **Принято; I3 paper scope проведено ревью**
- Дата: 2026-08-18
- Audit: [`PWR-0021`](../architecture/PWR-0021-i3-consolidated-paper-closure.md)
- Finding: [`FND-0086`](../findings/FND-0086-i3-paper-and-hil-closure-were-conflated.md)
- Propagation: [`REV-0005AM`](../reviews/REV-0005AM-i3-paper-closure-propagation.md)

## Decision

1. I3 has a complete reviewed paper electrical architecture: supervised 2S
   admission, sink-only USB-PD/NVDC, exact charger/manager support circuits,
   independent fixed rails, source sequence, quiet-state switching, external
   reverse protection and independent post-buck fault containment.
2. Every remaining I3 item is assigned to an explicit prototype/lot HIL or I8
   procurement gate. No generic paper prerequisite remains open.
3. Dependent I4 display/touch/UI-storage/product-USB paper work may begin.
   Any measured failure that exceeds the accepted rail/current/thermal/fault
   envelope reopens I3 before it changes the target.
4. “Paper reviewed” does not mean production-qualified: no source transition,
   thermal, destructive-fault, exact-cell lot, certification or EMC result is
   claimed by this decision.
5. Integrated mockup remains paused through I9, atomic architecture remains
   open, the BOM is not frozen and KiCad is not authorized.

## Consequence

The dependency chain can progress without hiding prototype work. The target
function, component set, pin budget and recurring-cost estimate do not change;
this decision only makes maturity and reopen conditions precise.

