# Фиксация объединённых входов H4-R2

[English](h4-r2-input-freeze.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Итог H3](h3-r2-acceptance.ru.md)

`H4-R2.0.1` проведён ревью. Объединённый pre-layout gate теперь имеет один hash-bound набор: `10` hardware-artifacts и `14` firmware-artifacts (всего `24`). Все `3` cross-repository hashes импорта H3 совпадают.

Фиксация переносит проведённые mechanics H1-R2.37, native ECAD H2-R2.1.5, аналитический итог H3-R2.7, текущие six-domain firmware-контракты и проведённое F2-R2 target/BSP/build evidence. Историческое R1 execution-evidence F3/F4 остаётся только regression и не доказывает текущую dual-RP топологию.

Также перенесены все `51` ещё открытых physical-строк и явное обязательство F5/F6 по реализации i8080. Ничто молча не названо завершённым. Закупка, placement, routing и печать остаются запрещены.

Затем H4-R2.0.2/H4-R2.1 нашли один назначенный пробел генерации BSP C5/Pack/Safety. **Текущий маркер: `H4-R2.2`.**

[Машинная фиксация](../hardware/verification/generated/H4-R2-input-freeze.json).
