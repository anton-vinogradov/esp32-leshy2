# Zero-based architecture workspace

- Статус: **Активно по `DEC-0027`**
- Дата перезапуска: 2026-08-16

## Канонический порядок

1. [`CAP-0001`](CAP-0001-zero-based-capability-input.md) — что должен уметь продукт, без аппаратной раскладки;
2. [`CON-0001`](CON-0001-hardware-neutral-concurrency-model.md) — одновременные, degraded и failure scenarios;
3. [`RES-0001`](RES-0001-hardware-neutral-resource-demand.md) — resource demand без MCU/GPIO placement;
4. [`SRC-0001`](SRC-0001-primary-hardware-resource-facts.md) — package/controller/peripheral facts из первичных источников без выбора layout;
5. [`SYN-0001`](SYN-0001-zero-based-whole-device-candidates.md) — несколько полных аппаратных синтезов, выведенных из resource-consolidation strategies;
6. [`PIN-0002`](PIN-0002-zero-based-exact-pin-maps.md) — exact pin/controller/strap/recovery maps трёх zero-based candidates;
7. [`BUD-0002`](BUD-0002-zero-based-memory-traffic-budget.md) — общий memory/traffic envelope, admission boundaries и HIL gates;
8. [`PWR-0001`](PWR-0001-zero-based-power-safety-envelope.md) — scenario-derived rails, sequencing, STOP/fault и HIL envelope;
9. [`RFQ-0001`](RFQ-0001-zero-based-rf-zoning-coexistence.md) — equal-fixture RF paths/zones/coexistence and HIL gates;
10. `CST-*` — dated recurring-cost and implementation-burden comparison;
11. `PKG-*` — атомарное сравнение и выбор.

Каждый шаг получает статус **«Проведено ревью»** до того, как станет пререквизитом следующего.

## Запрещённые входы

Legacy schematic/source, прежние owner assignments, buses, GPIO, pin maps, S3-heavy/C5-heavy/balanced варианты и связанные бюджеты не являются constraints. Их полный текст сохранён в [`drafts/stage3-legacy-derived-2026-08-16/`](../../../drafts/stage3-legacy-derived-2026-08-16/README.md).

## Активные находки и решения

- [`DEC-0027`](../decisions/DEC-0027-zero-based-capability-driven-architecture.md) — zero-based метод;
- [`FND-0033`](../findings/FND-0033-legacy-layout-assumptions-leaked-into-synthesis.md) — ошибка прежнего synthesis;
- [`REV-0003J`](../reviews/REV-0003J-zero-based-stage3-restart.md) — ревью перезапуска.
- [`REV-0003K`](../reviews/REV-0003K-zero-based-concurrency-model.md) — ревью hardware-neutral concurrency model.
- [`REV-0003L`](../reviews/REV-0003L-zero-based-resource-model.md) — ревью hardware-neutral resource model.
- [`REV-0003M`](../reviews/REV-0003M-primary-hardware-fact-baseline.md) — ревью package-level facts перед synthesis.
- [`REV-0003N`](../reviews/REV-0003N-zero-based-candidate-set.md) — ревью полного zero-based candidate set без выбора winner.
- [`REV-0003O`](../reviews/REV-0003O-zero-based-exact-pin-maps.md) — ревью exact module/controller maps и no-loss исправления `FND-0034`.
- [`REV-0003P`](../reviews/REV-0003P-zero-based-memory-traffic-budget.md) — ревью zero-based memory/traffic arithmetic и admitted guarantees.
- [`REV-0003Q`](../reviews/REV-0003Q-zero-based-power-envelope.md) — ревью scenario-derived power topology и rail floors.
- [`REV-0003R`](../reviews/REV-0003R-zero-based-rf-zoning.md) — ревью equal-fixture RF zoning/coexistence и qualification gates.
