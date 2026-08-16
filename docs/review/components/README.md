# Этап 4 — компоненты и BOM

- Статус: **В работе**
- Пререквизит: этап 3 **Проведено ревью** (`DEC-0028`, `REV-0003U`)
- Target: `PKG-0001/SYN-3A`

Этап 4 превращает принятые архитектурные функции в проверяемый BOM. Legacy schematic/BOM используется только как источник кандидатов, прежних ошибок и уже существующих footprints; присутствие детали в legacy artifact не даёт ей приоритета.

## Каноническая цепочка

1. [`BOM-0001`](BOM-0001-stage4-component-evidence-register.md) — полный реестр component functions, evidence state, dependencies и порядок qualification;
2. `BOM-0002` — compute modules, clocks, boot/debug/recovery and compatibility identities;
3. `BOM-0003` — AON/STOP, battery input and all power rails/branch protection;
4. `BOM-0004` — UI/display/touch/storage/USB and non-safety slow control;
5. `BOM-0005` — receive/audio/IR signal chain;
6. `BOM-0006` — packet RF, analog voice and antenna/front-end assemblies;
7. `BOM-0007` — external M5 profiles/connectors/power-isolation;
8. `BOM-0008` — consolidated sourcing, alternates, lifecycle, cost and assembly manifest.

Каждый `BOM-*` сначала проверяет primary facts, затем electrical/reset/pin fit, supply/AVL/cost и HIL/substitution evidence. Следующий artifact не использует строку как закрытый пререквизит, пока соответствующее review явно не дало статус **«Проведено ревью»**.

## Правила

- exact architecture-locked part нельзя заменить «аналогом» только по названию или цене;
- conditional candidate не становится target до полного evidence и явного disposition;
- abstract circuit function обязательно получает exact implementation до schematic stage;
- external accessory не попадает в base BOM, но его connector/power/isolation обязан попасть;
- zero-loss saving требует proof capability, performance, safety, reliability, autonomy, serviceability and testability equivalence;
- по `DEC-0029` newest stable manufacturer-supported hardware revision предпочтительна на BOM freeze только после compatibility/errata/toolchain/supply/requalification proof; больший номер не означает automatic substitution;
- новая лишняя функция/деталь сначала помечается и выносится владельцу как **⚠️ Предложение**, если она не является очевидным implementation prerequisite уже принятого target;
- component mismatch создаёт finding; молчаливое изменение owner/pin/power/STOP/RF/update contract запрещено.

## Review

- [`REV-0004A`](../reviews/REV-0004A-stage4-entry-register.md) — completeness и ordering реестра; **Проведено ревью**.
- [`REV-0004B`](../reviews/REV-0004B-compute-clock-recovery-evidence.md) — compute/clock/recovery primary facts; **Проведено ревью фактов**.
- [`REV-0004C`](../reviews/REV-0004C-c5-v1.2-propagation.md) — C5 v1.2 production floor; **Проведено ревью**.
- [`REV-0004D`](../reviews/REV-0004D-compute-cad-library-audit.md) — availability/provenance audit critical CAD libraries; **Проведено ревью фактов**, strategy `IMP-0025` открыта.

Статус `REV-0004A` относится к полноте входного реестра, а не к квалификации перечисленных компонентов.
