# DEC-0071 — controlled startup and post-start accessory transient

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Analysis: [`PWR-0010`](../architecture/PWR-0010-external-efuse-passive-profile.md)
- Parent eFuse decision: [`DEC-0069`](DEC-0069-latch-off-external-efuse.md)
- Propagation review: [`REV-0005AB`](../reviews/REV-0005AB-external-efuse-passive-profile.md)

## Context

Datasheet verification found that the existing paper architecture had assigned
the wrong role to `ITIMER`. `TPS259470L` applies the `RILM` current limit
immediately during startup; `ITIMER` does not defer it. Retaining the old claim
would make the accepted accessory behavior physically unimplementable.

## Decision

1. The external port remains `1.25 A` continuous.
2. `RC0402FR-072K21L` sets a nominal `1.509 A` limit, active at startup and in
   normal operation; its paper tolerance floor is approximately `1.344 A`.
3. `GRM155R71H472KA01D`, 4.7 nF, controls startup slew. An admitted external
   profile is initially capped at `1 mF` effective input capacitance and must
   pass specimen inrush HIL.
4. The accepted `2.0 A` envelope is a bounded **post-start** transient only.
   `GRM188R71E224KA88D`, 220 nF, sets an approximate `86.6…404 ms` screened
   interval; it is not an ordinary continuous rating.
5. `169 kOhm / 47 kOhm` exact resistors set nominal 5.515-V OVLO. Separate
   2.2-uF local capacitors and a 1-kOhm passive bleeder close the first paper
   bypass/discharge profile.
6. Any eFuse fault latches the session off. Firmware isolates accessory
   signals, clears enable and forbids automatic retry. OVLO recovery is treated
   as a new admission because this IC bypasses `dVdt` on that recovery path.

## Consequence

The external port keeps its intended continuous and transient capability, but
its startup and post-start guarantees are now implementable by the selected
silicon. Eight exact physical passives replace an abstract discharge circuit
in the machine design and both visible target diagrams. Remaining HIL and
layout gates stay explicit; this is not KiCad authorization.
