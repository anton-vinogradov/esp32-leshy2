# DEC-0069 — latch-off external accessory eFuse

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Parent topology: [`DEC-0068`](DEC-0068-separate-fixed-downstream-rails.md)
- Analysis: [`PWR-0008`](../architecture/PWR-0008-exact-downstream-rail-tree.md)
- Propagation review: [`REV-0005Z`](../reviews/REV-0005Z-latch-off-efuse-propagation.md)

## Context

Первый active-tree pass указал `TPS259470ARPWR`. Проверка exact suffix по
официальной device-comparison table показала, что `A` — auto-retry: после
thermal fault устройство при оставшемся enable автономно пробует включиться
снова примерно через 110 ms. Для доступного снаружи 5-V разъёма это слабее
принятого fail-closed поведения: зависший control domain или stuck-high request
не должны превращать аппаратную аварию в повторяющийся цикл подачи питания.

## Decision

1. Exact external eFuse is `TPS259470LRPWR`, not `TPS259470ARPWR`.
2. `L` latch-off behavior remains off after a latched/thermal fault until
   `EN/UVLO` is explicitly taken below shutdown or input power is cycled.
3. Firmware also latches every observed `FLT`, isolates accessory signals and
   requires a fresh explicit user action after the physical cause is removed.
   Software retry loops are forbidden.
4. Same RPW-10 package, contacts and surrounding passive topology are retained;
   no GPIO, footprint or cost-class change follows from the suffix correction.
5. The accepted 1.25-A continuous output is not implemented as a nominal
   1.25-A current limit. Exact passive closure uses a nominal 1.50-A set point
   so the component-tolerance floor remains at least 1.25 A; bounded 2-A
   transients still use `ITIMER`.
6. Reverse-current blocking, `FLT`, `ILM`, `dVdt`, `OVLO` and `ITIMER` behavior
   remain mandatory and are not replaced by firmware estimates.

## Availability/cost check

At selection time TI listed `TPS259470LRPWR` active. JLCPCB `C3662793` showed
6,218 units and DigiKey 11,374; DigiKey listed the same unit and reel prices as
the earlier A suffix. The safety improvement therefore has no recurring BOM
premium at the checked quantities.

Primary evidence:

- [TI exact L-suffix product page](https://www.ti.com/product/TPS25947/part-details/TPS259470LRPWR)
- [TI TPS25947 family datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
- [JLCPCB C3662793](https://jlcpcb.com/partdetail/TPS259470LRPWR/C3662793)

This remains a principle/electrical decision, not KiCad authorization.
