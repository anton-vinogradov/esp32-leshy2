# IMP-0028 — M5-first, not M5-only external expansion platform

- Статус: **Принят вариант B; `DEC-0034`**
- Дата: 2026-08-16
- Evidence: [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md)
- Finding: [`FND-0042`](../findings/FND-0042-m5-is-not-one-interface-or-ninety-percent-solution.md)

## Контекст

Already accepted external profiles use M5 Unit GPS v1.1, Unit NFC U216 and
Cardputer Cap U214. The current competitor delta also makes external haptic,
IMU, keyboard and iButton attractive ways to reduce base BOM. A common
expansion platform is therefore materially better than one connector per
feature.

The audit also disproves an M5-only 90% claim. Official M5 products fully cover
5 of 18 relevant external hardware classes, 8 with partial matches and 9 after
our custom iButton adapter. Remaining high-rate SDR/compute/USB needs cannot be
preserved over low-rate Grove/Cap command links alone.

## Options

### A — M5-only

Native Unit/Cap/M5-Bus surfaces; every future accessory is forced through them.

- Плюс: one ecosystem label.
- Минусы: false 90% promise, large M5-Bus mechanics, no honest raw SDR or
  high-speed host route, host-specific pin conflicts and legacy/EOL baggage.

### B — M5-first, plus separate high-speed tier

Native M5 Unit and U214-compatible Cap remain the primary low-rate expansion
surface. High-speed USB host/data is evaluated as a separate G3/G4 surface.
M5-Bus Modules are supported only through exact profile-specific carriers.

- Плюсы: preserves accepted M5 modules and low base BOM; can reach more than
  90% of external attachment classes without pretending Grove is high-speed;
  does not permanently expose a 30-pin battery/power stack.
- Минусы: two software/connector classes; high-speed USB adds power, ESD,
  connector-role and driver work if later accepted.

### C — generic proprietary expansion only

Expose one Leshy2 high-density connector and use adapters for all M5 families.

- Плюс: maximum pin/power flexibility and fewer native connector constraints.
- Минусы: every M5 accessory needs an adapter; weaker field usability and more
  custom NRE before the first product works.

## Recommendation

**Принят B** в [`DEC-0034`](../decisions/DEC-0034-m5-first-two-tier-expansion.md).
It treats M5 as the default low-rate accessory ecosystem, not as a
religion or a throughput claim. Exact number and placement of HY2.0 ports,
whether a passive Cap-to-A/B/C dock is included, and the high-speed connector
remain G3/G4 comparisons. The base does not promise native M5-Bus.

## Acceptance boundary

- native Unit profiles distinguish A/B/C/custom and use protected default-off
  5 V power;
- native Cap profile preserves the full documented U214 pin/power contract;
- exact-profile manifests and HIL replace blanket enumeration/hot-plug claims;
- hard STOP and update/reset faults fail every external transmitter off;
- active accessory firmware identity/recovery limitations remain visible;
- M5-Bus support is per exact carrier, never universal;
- high-speed tier is accepted as a distinct architectural class and cannot be
  silently removed once a reviewed external result depends on it; its exact
  USB/user-facing scope remains open in `W-EXTRA-16`;
- base, likely-field-kit and maximum-lab-kit cost are reported separately.
