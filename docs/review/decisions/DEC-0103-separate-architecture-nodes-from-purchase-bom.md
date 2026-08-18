# DEC-0103 — separate architecture evidence nodes from purchase BOM

Статус: **принято автоматически; проведено ревью accounting boundary**.

## Контекст

Принципиальная диаграмма обязана показывать отдельные физические устройства и
их роли. Иногда доказательный узел физически находится внутри уже закупаемой
assembly. Если одинаково трактовать diagram nodes и purchasing placements,
factory BOM получает двойной счёт.

## Решение

1. Architecture `instances` остаются полным графом физических/evidence nodes.
2. Purchased assembly остаётся одной supplied/costed placement.
3. Внутренний controller может оставаться отдельным diagram/contact node, но
   обязан входить в explicit `non_purchase_instances` со своим parent и reason.
4. Generator и tests должны показывать разницу между architecture count и
   purchase count; молчаливое исключение запрещено.
5. Current first application: `display_touch_controller` / `ST77922` is
   contained by `display` / `HMX035CTFT-001`.

## Consequences

- machine diagram remains detailed and unchanged;
- factory BOM no longer buys/costs the COG twice;
- current purchasing denominator becomes 187 lines / 857 placements;
- any future module-internal node must declare the same boundary explicitly.
