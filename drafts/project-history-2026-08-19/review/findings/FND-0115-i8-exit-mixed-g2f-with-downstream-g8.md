# FND-0115 — I8 exit mixed G2F feasibility with downstream G8

- Статус: **Исправлено `BOM-0028/REV-0005CC`**
- Дата: 2026-08-19
- Нормативный workflow: [`FLOW-0001`](../architecture/FLOW-0001-product-to-cad-gates.md)
- Internal sequence: [`INT-0001`](../architecture/INT-0001-internal-design-closure-sequence.md)

## Несоответствие

Текущий I8 правильно собрал полный candidate inventory, sourcing, cost,
substitution и physical-gap evidence, но его статус оставался открыт до:

- exact connector/harness/antenna identities, зависящих от G3 geometry;
- received-item coupons и assembled RF/physical HIL;
- specific qualified alternates для production BOM;
- ответов RFQ и полного factory COGS.

Это создавало цикл. `FLOW-0001` требует сначала G3 product design, затем
G4…G7 whole-device/optimality/atomic work и только в G8 — exact qualified BOM,
cost and alternates. G2F при этом прямо не может выдавать final architecture,
normative footprint или production BOM. Значит, downstream G3/G8 outputs не
могут одновременно быть пререквизитом завершения внутреннего G2F/I8.

## Исправленная граница

I8 paper procurement-feasibility считается проверенным, когда:

1. каждый current physical instance и purchase line посчитан;
2. у каждой used line есть dated source evidence либо явный sourcing/RFQ gate;
3. у каждой line есть comparable cost evidence либо явный non-numeric gate;
4. у каждой line есть одна no-silent-substitution class;
5. каждая ещё не instantiated physical family имеет owner, prerequisites и
   acceptance, а не generic placeholder;
6. никакой open gate не выдан за нулевую стоимость, qualified part, HIL pass
   или разрешение начать KiCad.

Exact downstream result остаётся обязательным, но принадлежит своему gate:

- G3 исполняет geometry/received-mate/coupon inputs;
- G4…G7 могут пересинтезировать candidate и переоткрыть I8 evidence;
- G8 повторно проверяет exact target BOM, RFQ, lifecycle, cost, qualified
  alternates and factory COGS после atomic architecture.

## Последствие

`BOM-0028/REV-0005CC` проводят consolidated I8 review в ограниченном paper
feasibility scope. Это не принимает `G2F-3I` как target architecture и не
переносит G8 раньше G3. Следующим внутренним шагом становится I9 joint
self-review; integrated G3 mockup возобновляется только после его pass.
