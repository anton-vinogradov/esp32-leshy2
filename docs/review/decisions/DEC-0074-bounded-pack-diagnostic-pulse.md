# DEC-0074 — bounded pre-admission pack diagnostic pulse

- Статус: **Принято владельцем; exact components propagated automatically**
- Дата: 2026-08-18
- Owner choice: `10 Ohm`, hardware/software pulse limit `<=50 ms`
- Analysis: [`PWR-0013`](../architecture/PWR-0013-exact-pack-diagnostic-frontends.md)
- Corrected finding: [`FND-0078`](../findings/FND-0078-mspm0-pa24-forbids-injection-current.md)
- Propagation review: [`REV-0005AE`](../reviews/REV-0005AE-pack-diagnostic-profile.md)

## Decision

1. The pre-admission screen places one exact `CRCW251210R0JNEGIF` 10-Ohm
   pulse-proof resistor and one `DMN2056U-7` low-side MOSFET across the fused
   full 2S stack ahead of the normally-open MAX17320 CHG/DIS pair.
2. `PA22/A4` supplies only a rising trigger edge. One active-production
   `TPUL2G223BQBR` channel independently terminates the gate pulse; it is
   non-retriggerable and cannot be held active by a stuck GPIO.
3. Exact `169 kOhm / GRM31C5C1H224JE02L 220 nF C0G` timing components produce
   about 34.4 ms typical and a conservative `28.7…40.7 ms` paper window after
   IC, initial-component and temperature tolerances. Production accepts only a
   measured `25…50 ms` pulse; this protects both the loaded-sample window and
   the owner-accepted upper ceiling.
4. Firmware must still request only one bounded admission pulse, enforce a
   HIL-derived cooldown and never present this screen as full-load proof.
5. Midpoint evidence moves to `PA25/A2`; stack evidence moves to `PA26/A1`.
   `PA24/A3` is released because the exact MSPM0C1104 datasheet forbids
   injection current there.
6. Midpoint uses `2×220 kOhm / 169 kOhm / 10 nF`; full stack uses
   `5×220 kOhm / 169 kOhm / 10 nF`. Both use the internal 1.4-V reference and
   remain below it at the defined 4.3/8.6-V screen corners.
7. Every timer, load, pull, divider and filter component is a separate machine
   and vertical-diagram instance.

## Consequence

The diagnostic can expose a weak cell/contact/fuse path without energizing the
product rails, while a frozen or hostile firmware level cannot stretch one
pulse beyond the hardware interval. The current is intentionally only about
`0.57…0.88 A`; the existing `2.78 A` product transient still requires separate
HIL. GPIO budget remains `12/3/3`. Exact acceptance thresholds, cooldown and
thermal repetition limits are deliberately not frozen before prototype data.

This is a reviewed working-design decision, not authorization to begin KiCad.
