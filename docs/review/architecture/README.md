# Zero-based architecture workspace

- Статус: **Активно по `DEC-0027`**
- Дата перезапуска: 2026-08-16

## Канонический порядок

1. [`CAP-0001`](CAP-0001-zero-based-capability-input.md) — что должен уметь продукт, без аппаратной раскладки;
2. [`CON-0001`](CON-0001-hardware-neutral-concurrency-model.md) — одновременные, degraded и failure scenarios;
3. [`RES-0001`](RES-0001-hardware-neutral-resource-demand.md) — resource demand без MCU/GPIO placement;
4. `SYN-*` — несколько полных аппаратных синтезов;
5. `PIN-*` — exact pin/controller maps только после полного synthesis;
6. `PKG-*` — атомарное сравнение и выбор.

Каждый шаг получает статус **«Проведено ревью»** до того, как станет пререквизитом следующего.

## Запрещённые входы

Legacy schematic/source, прежние owner assignments, buses, GPIO, pin maps, S3-heavy/C5-heavy/balanced варианты и связанные бюджеты не являются constraints. Их полный текст сохранён в [`drafts/stage3-legacy-derived-2026-08-16/`](../../../drafts/stage3-legacy-derived-2026-08-16/README.md).

## Активные находки и решения

- [`DEC-0027`](../decisions/DEC-0027-zero-based-capability-driven-architecture.md) — zero-based метод;
- [`FND-0033`](../findings/FND-0033-legacy-layout-assumptions-leaked-into-synthesis.md) — ошибка прежнего synthesis;
- [`REV-0003J`](../reviews/REV-0003J-zero-based-stage3-restart.md) — ревью перезапуска.
- [`REV-0003K`](../reviews/REV-0003K-zero-based-concurrency-model.md) — ревью hardware-neutral concurrency model.
- [`REV-0003L`](../reviews/REV-0003L-zero-based-resource-model.md) — ревью hardware-neutral resource model.
