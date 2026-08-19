# DEC-0079 — XTAR 18650 4000mAh exact cell qualification target

- Статус: **Принято как exact first target; проведено ревью paper fit**
- Дата: 2026-08-18
- Analysis: [`PWR-0018`](../architecture/PWR-0018-xtar-18650-4000mah-cell-profile.md)
- Finding: [`FND-0083`](../findings/FND-0083-generic-cell-placeholder-blocked-real-limits.md)
- Propagation review: [`REV-0005AJ`](../reviews/REV-0005AJ-exact-cell-propagation.md)

## Decision

1. The base regional battery kit targets two identical exact
   `XTAR 18650 4000mAh` protected button-top cells without an integrated USB
   charging port.
2. Each installed cell is `3.6 V`, `4000 mAh` typical / `3800 mAh` minimum;
   the supervised 2S pair is `28.8 Wh` nominal and remains inside the accepted
   `6.0…8.4 V` product window.
3. The product charge-current ceiling is `2 A`, equal to the exact cell's
   standard charge current. Source power, system load, temperature or HIL may
   reduce it; firmware cannot use the manufacturer's `4 A` maximum as a normal
   charging target.
4. The `10 A` maximum continuous-discharge rating and `11…14 A` assembly
   overcurrent trip provide margin above the calculated `2.22 A` continuous /
   `2.78 A` transient current per series cell. Existing 5-A slot fuses and
   pack protection remain required and are not replaced by cell protection;
   exact time-current/trip coordination remains a specimen HIL gate.
5. Only an exact manufacturer/approved regional-kit supply path is supported.
   A different protected wrapper around the same raw core, a raw flat-top cell,
   a USB-equipped variant or mixed MPN/lot/age pair is a different product and
   receives no automatic admission.
6. Charging is conservatively blocked outside `0…45 °C` until the exact
   assembly certification package gives a narrower or broader qualified
   range. Discharge/operation remains bounded by the published `-20…60 °C`
   range and may be narrowed by enclosure HIL.
7. The exact model is a qualification target, not yet a production-qualified
   lot. Production kitting requires an assembly-matching UN38.3 test summary,
   authenticity/lot evidence, received-part dimensional and electrical tests,
   `Keystone 1048P` insertion/retention proof, and complete thermal/droop HIL.
8. XTAR publishes `18650 4000mAh` as the model but no separate order code on
   the exact product page. The controlled procurement identity therefore also
   binds manufacturer, exact source URL, protected/no-USB construction and
   received package/lot evidence.

## Consequence

No hardware function or GPIO is lost. The target pair adds no PCB part beyond
the already selected holder and provides about `14%` more nominal energy than
a 3500-mAh pair. Official-store single-unit pricing was `$14.50` per cell,
well below the reviewed Fenix 4000-mAh alternative while meeting the same
product current and charge class.

Exact droop/contact thresholds still depend on measured distributions rather
than one invented universal resistance number. This decision does not
authorize KiCad or claim a shippable lithium kit before the document/specimen
gates pass.
