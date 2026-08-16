# REV-0003U — принятие и cross-repository propagation этапа 3

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3 — системная архитектура и владение
- Decision: [`DEC-0028`](../decisions/DEC-0028-accept-zero-based-syn-3a.md)
- Target package: [`PKG-0001/SYN-3A`](../architecture/PKG-0001-zero-based-target-architecture-proposal.md)

## Проверка атомарного принятия

| Проверка | Результат |
|---|---|
| owner decision относится ко всему package | да; `DEC-0028` принимает owners/transports/pins/UI/update/power/RF/cost и `KG-01…08` одной записью |
| subordinate fragment не получил отдельного target status | да; `SYN-2A/2B` остаются только comparative/fallback inputs |
| legacy layout не стал скрытым пререквизитом | да; target ссылается на zero-based chain и архивирует legacy только как idea/risk source |
| exact owners и variants | S3 N16R2, C5 N8R8 rev ≥1.0, RP2354A A4 зафиксированы |
| exact transport/pin/recovery | 1-bit SDIO, SPI+alert и `PIN-0002/SYN-3A` нормативны |
| safety/update/cost consequences | приняты без удаления premium, third-target burden, sourcing shortage или kill-gates |

## Проверка hardware propagation

- `README.md` и `README.ru.md` теперь описывают принятый трёхдоменный finished-product target;
- `docs/contracts/ownership.md` больше не содержит «nRF owner не выбран» и фиксирует все runtime/peripheral границы;
- `PKG-0001` и `REV-0003T` отражают принятие, но сохраняют исходный контекст предложения и tradeoffs;
- `docs/status/current-state*.md` отделяют принятую architecture от ещё не реализованных component/schematic/layout/HIL artifacts;
- `docs/review/stages.md` даёт этапу 3 точный статус **«Проведено ревью»** и не объявляет этап 4 завершённым.

## Проверка firmware propagation

- target `README.md`/`README.ru.md` больше не называют устройство dual-MCU и не оставляют nRF ownership открытым;
- [`ARC-0001`](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/architecture/ARC-0001-three-domain-runtime-contract.md) фиксирует три images/domains, typed IPC, local deadlines, safety leases, boot/degraded states, budgets, update/recovery и failure behavior;
- firmware architecture index имеет статус **Reviewed** и ссылается на `DEC-0028/PKG-0001`;
- firmware current-state не выдаёт принятый контракт за реализованный код и указывает stage 4 как следующий cross-repository gate.

## Проверка непротиворечивости

- root target pages содержат только принятый finished-product contract;
- current-state pages сохраняют исторические checkpoint формулировки только с явным указанием, что позднее их разрешил `DEC-0028`;
- STOP охватывает RP `RUN` и S3/C5 reset/enable policy, а не устаревшую формулу «оба MCU»;
- normal signed update/recovery охватывает S3, C5 и RP;
- unqualified RF/TX/component claims остаются gates, а не ложными passes;
- `git diff --check` проходит в обоих репозиториях.

## Выход

Пререквизиты, решение, package, target entrypoints, ownership contract и firmware runtime contract согласованы. Этап 3 получает статус **«Проведено ревью»**. Следующий разрешённый шаг — этап 4: единый component/BOM evidence register, затем поочерёдная qualification exact parts и всё ещё абстрактных circuit functions без изменения принятой архитектуры.
