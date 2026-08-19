# DEC-0081 — independent containment for every internal converter rail

- Статус: **Принято; проведено ревью paper electrical behavior**
- Дата: 2026-08-18
- Analysis: [`PWR-0020`](../architecture/PWR-0020-independent-post-buck-containment.md)
- Finding: [`FND-0085`](../findings/FND-0085-uncontained-internal-buck-high-side-short.md)
- Propagation: [`REV-0005AL`](../reviews/REV-0005AL-internal-rail-containment-propagation.md)

## Decision

1. Every internal buck output has a raw converter net and an independent
   protected load net. No load may bypass the protection boundary.
2. `TPS25961DRVR` protects AON with about 0.208-A nominal current limit and a
   3.505…3.809-V full-corner OVLO window. `TPS3808`, its POR pull-up and all
   always-on safety consumers live only on `AON_SAFE_3V3`.
3. Two separate `TPS25974LRPWR` devices protect main and voice. Main uses a
   guaranteed 3.2…3.715-A breaker window and 3.438…3.578-V OVLO window; voice
   uses 1.55…1.905 A and 4.314…4.610 V respectively.
4. Main and voice use controlled rise, bounded overload time, latch-off fault
   behavior and protected-side PG thresholds. Their raw converter PG contacts
   are fixture-only and cannot certify a load rail.
5. TPS25961 handles AON overcurrent/thermal faults with its bounded autonomous
   retry; persistent OVLO stays disconnected while the fault remains, and the
   supervisor cannot release main without sustained protected-AON validity.
   A latched main trip requires complete source removal and fresh admission;
   voice can remove/reapply its raw rail through the existing STOP-dominant
   domain enable. Firmware may shed loads and report evidence, but it cannot
   bypass, widen or directly reset an energized protection boundary.
6. The exact protection profile in `PWR-0020` is accepted under the delegated
   rule for improvements without noticeable budget growth: approximately
   USD 2.4 per board at 100-piece component pricing plus placement, no GPIO
   and no loss of function.

## Consequence

One failed converter switch can no longer directly apply `SYS` to its
low-voltage consumers. AON validity now means protected-AON validity, and
runtime fault qualification for main/voice is based on the load side of the
independent cutoff.

The added on-resistance is small compared with the rail budgets: paper loss is
about 61 mW typical on main at 2.5 A and 15 mW on voice at 1.25 A; AON series
loss is negligible at its expected load. Exact hot-copper temperatures,
transient response and injected high-side-short containment remain HIL. This
decision does not authorize KiCad.
