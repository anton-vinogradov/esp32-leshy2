# DEC-0073 — exact converter control-passive profile

- Статус: **Принято автоматически в пределах делегированного выбора компонентов; распространено**
- Дата: 2026-08-18
- Analysis: [`PWR-0012`](../architecture/PWR-0012-exact-converter-control-passives.md)
- Parent PG decision: [`DEC-0070`](DEC-0070-enable-qualified-switched-rail-pg.md)
- Propagation review: [`REV-0005AD`](../reviews/REV-0005AD-converter-control-passive-profile.md)

## Context

The converter and PG-qualifier topology was accepted, but its EN, PG, base and
fault pulls were still described by values rather than exact physical
instances. This left reset defaults, static loading, BOM count and visible
principled diagrams incomplete.

## Decision

1. `TPS629203.EN` is strapped directly to admitted `BQ25798.SYS`; there is no
   runtime or passive-divider AON-disable path.
2. AON PG uses one exact `RC0402FR-0747KL` 47-kOhm pull-up to
   `AON_SAFE_3V3`.
3. Main, voice and accessory TPS564252 EN each receive a separate exact
   `RC0402FR-0710KL` 10-kOhm fail-low resistor.
4. Voice and accessory PG each receive a separate exact
   `RC0402FR-0710KL` pull-up to `3V3_MAIN`.
5. `POWER_FAULT_N` receives one exact `RC0402FR-0710KL` pull-up to
   `3V3_MAIN`.
6. The two MMBT3904 bases each receive one exact `RC0402FR-0768KL` 68-kOhm
   series resistor.
7. All nine resistors are independent physical machine/diagram instances.

## Consequence

No GPIO, voltage selector or behavior changes. AON remains autonomous; every
application converter fails low; optional-off PG remains non-fault; enabled
PG loss remains hardware-visible. The profile adds no unique BOM MPN and
approximately `$0.006` of checked material per board. Dynamic and multi-fault
HIL remain prerequisites; no KiCad authorization is implied.

