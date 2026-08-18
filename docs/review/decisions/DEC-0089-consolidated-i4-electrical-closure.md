# DEC-0089 — consolidated I4 electrical closure

- Status: **accepted under delegated no-material-function/cost rule; Проведено ревью paper electrical block**
- Finding: [`FND-0094`](../findings/FND-0094-consolidated-i4-audit-found-hidden-interface-gaps.md)
- Architecture: [`IOX-0001`](../architecture/IOX-0001-consolidated-i4-electrical-closure.md)
- Propagation review: [`REV-0005AT`](../reviews/REV-0005AT-consolidated-i4-propagation.md)

## Decision

1. Freeze `TCA6424ARGJR` as the exact main slow-I/O core at address `0x22`,
   with VCCI/VCCP on protected `3V3_MAIN`, complete exact decoupling, grounded
   exposed pad, pulled-up fixture RESET_N and shared open-drain INT.
2. Insert two separate AON-powered `SN74LVC1G07DCKR` open-drain buffers and
   main-domain 10-kOhm pull-ups between the AON STOP/S3-evidence sources and
   TCA6424A P22/P23. Preserve existing signal polarity and diagnostic-only
   semantics.
3. Fix the pack-admission SYS_I2C target at firmware address `0x2A`.
4. Correct microSD DAT0 return to real S3 GPIO4 and replace the abstract STOP
   LED resistor with exact `RC0402FR-072K2L`.
5. Bond product USB shell directly to local power/ESD ground at the entry zone.
   Treat the display FPC as internal, service-only and not live-insertable;
   reopen ESD protection if later mechanics invalidate that boundary.
6. Record main slow-I/O as `18 used / 6 free` and retain UI P7 only as a
   protected local fixture/growth test pad.
7. Mark I4 **«Проведено ревью»** for paper electrical scope and advance the
   dependency sequence to I5, while keeping all named physical/HIL gates open.

## Consequences

- Full D-pad, PTT, STOP, F1, F2, encoder, touch, display, microSD and product
  USB remain present with unchanged user-visible behavior.
- No MCU GPIO is added or removed. The correction adds two already-qualified
  buffer-family instances and commodity passives; it does not materially
  expand cost or unique BOM burden.
- Product TCA6424A recovery uses bus recovery, then a full main-rail power
  cycle below 0.2 V; fixture reset remains direct.
- Audio/receiver/RF/accessory circuits are not accepted by implication.
- The decision does not authorize KiCad, final atomic architecture or the
  paused integrated mockup.
