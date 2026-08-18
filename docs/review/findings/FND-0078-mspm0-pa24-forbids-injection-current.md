# FND-0078 — MSPM0 PA24 cannot accept the unpowered-divider current

- Статус: **Закрыто исправлением machine map и regression-проверкой**
- Дата: 2026-08-18
- Severity: real-device electrical provenance / cell-admission safety
- Closure: [`PWR-0013`](../architecture/PWR-0013-exact-pack-diagnostic-frontends.md),
  [`DEC-0074`](../decisions/DEC-0074-bounded-pack-diagnostic-pulse.md),
  [`REV-0005AE`](../reviews/REV-0005AE-pack-diagnostic-profile.md)

## Finding

The working admission map assigned the protected 2S midpoint divider to
`MSPM0C1104SDGS20R PA24/A3`. The exact current TI datasheet exposes that
physical DGS-20 contact, but singles PA24 out from the otherwise supported
injection-current rule: no injection current is allowed on PA24.

Both battery dividers remain energized when the passive-OR admission supply is
absent or moving between sources. A high-value divider would limit the current
to microamps, but nonzero current is still incompatible with a pin whose
specified supported injection current is zero. The previous map therefore did
not satisfy its own every-insertion/removal reset proof.

## Correction

- midpoint evidence moves from `PA24/A3` to physically exposed `PA25/A2`;
- full-stack evidence moves from `PA25/A2` to physically exposed `PA26/A1`;
- `PA24/A3` becomes free and is forbidden for battery-derived analog evidence;
- the admission-controller budget remains `12 used / 3 service-reserved / 3
  free`;
- machine validation now asserts the corrected contacts and the free set
  `{PA24/A3, PA27/A0, PA28/A5}`.

The selected dividers limit any unpowered-pin current on PA25/PA26 to about
7 uA, far below the ordinary ±2-mA supported injection-current bound. This is
still a paper screen; insertion, removal and supply-handover waveforms remain
prototype HIL.

