# DEC-0102 — exact SC1512-A4 order identity

Статус: **принято автоматически; проведено ревью identity propagation**.

## Контекст

Архитектура использует RP2354B0A4/QFN80 как deterministic radio/voice owner.
Прежнее BOM-поле `RP2354B A4 (exact RP2354B0A4 first target)` описывало нужный
кристалл, но не являлось заказываемым MPN. Владелец разрешил автоматически
исправлять компоненты, когда это не меняет функцию и явно не раздувает бюджет.

## Решение

1. First-target purchasing line — `SC1512-A4`.
2. Human-readable product diagrams and runtime contracts show
   `SC1512-A4 (RP2354B0A4)` so order identity does not hide silicon identity.
3. `SC1512(13)-A4` may be considered only as the same-silicon packaging
   alternate during AVL/cost work; it is not silently substituted in the
   first-target BOM.
4. Received lot must still pass marking, A4 identity, land-pattern,
   power/clock and assembly/recovery HIL before production freeze.

## Consequences

- no GPIO, owner, firmware, feature, performance or QFN80-class layout change;
- no added component or material cost from the identity correction itself;
- purchasing and generated artifacts now contain a real order code;
- KiCad remains unauthorized through incomplete I8 and I9.
