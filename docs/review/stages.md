# Этапы и статусы

Нормативные gate definitions и правила итерации находятся в
[`FLOW-0001`](architecture/FLOW-0001-product-to-cad-gates.md). Нумерация ниже
исправлена решением [`DEC-0032`](decisions/DEC-0032-reopen-product-design-before-cad.md);
прежняя последовательность ошибочно ставила architecture/BOM раньше product
and physical design (`FND-0039`).

| № | Gate | Основной выход | Статус |
|---:|---|---|---|
| 0 | Review baseline | правила, evidence/decision/finding ledgers | **Проведено ревью** |
| 1 | Product intent | назначение, ranked goals, safety/legal and no-loss boundaries | **Проведено ревью**; может быть переоткрыто явным finding |
| 2 | Capabilities | полный wishlist, competitors, requirements, exclusions, concurrency/failure needs | **Проведено повторное ревью `REV-0002AS`**: `W-EXTRA-11..17` полностью disposed; 6 GHz/Wi-Fi 6E rejected `DEC-0040` |
| 2F | Logical/electrical feasibility | neutral signal demand, real-device pin provenance, ≥2 complete owner/bus/GPIO maps and working baseline | **В работе**: `PIN-0003/REV-0004V` проводят ревью current G2F-3I owner/net/pad projection (`S3 29/3/4`, `C5 14/6/1`, `RP 48/0/0`, slow `23/1/0`) и exact SA518/Si4732 routes; `FND-0060` exact electrical endpoints, `IMP-0043/FND-0058` antenna decision/qualification, lots/feeds/protection, physical RF, peripherals/power/HIL остаются открыты |
| 3 | Target product design | adapted legacy physical mockup, form factor, interaction, controls, interfaces, battery, antenna/service/environment/cost envelopes | **В работе от reviewed `PIN-0003` working baseline**: адаптируется legacy generator; `PD-0001` — input, premature `LAY-0001` P1/P2/P3 — reference only; packing/RF/power conflicts переоткрывают G2F |
| 4 | Whole-device candidates | ≥2 complete architectures covering the same reviewed product | Не начато в исправленном процессе; старые `SYN-2A/2B/3A` — reference studies only |
| 5 | Optimality decision | reviewed weights, score/Pareto/sensitivity and owner selection | Не начато |
| 6 | Conceptual co-design | block/board/antenna/power/thermal/service placement and preliminary resource feasibility | Не начато |
| 7 | Atomic architecture | owners, transports, exact resources/pins, reset/update/safety and reopen gates | **Переоткрыто**; former `DEC-0028/PKG-0001` superseded as target by `DEC-0032` |
| 8 | Components and BOM | exact qualified parts, lifecycle/supply/cost/alternates | Заблокировано этапом 7; former stage-4 evidence is candidate/reference only |
| 9 | Electrical/CAD and firmware architecture | electrical specification, canonical libraries, schematic/ERC, runtime/HAL/toolchain/test contracts | Заблокировано; active KiCad contains no canonical implementation |
| 10 | PCB and pre-fab | placement/routing/DRC/SI/PI/RF/mechanical/manufacturing evidence | Не начато |
| 11 | Prototype and bring-up | assembly, recovery, safety/RF/HIL measurements | Не начато |

Этапы могут содержать параллельные feasibility probes, но их результаты
остаются черновиками. Ни одна ветвь не использует непроверенный или
candidate-only artifact как окончательный вход.
