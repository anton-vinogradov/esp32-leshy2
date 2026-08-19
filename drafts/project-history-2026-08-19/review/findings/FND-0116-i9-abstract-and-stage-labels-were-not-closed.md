# FND-0116 — I9 abstract and stage labels were not closed

- Статус: **Исправлено `I9-0001/REV-0005CD`**
- Дата: 2026-08-19
- Scope: `G2F-3I`, `INT-0001/I9`

## Несоответствия

1. Generator проверял contact/pin/resource validity, но не требовал
   исчерпывающей классификации каждого `abstract:*` fixed-route endpoint. Новый
   hidden physical item мог появиться под новым label и не попасть в
   procurement gate.
2. Четыре machine-source строки продолжали направлять XTAR procurement,
   detector quote и NTC physical HIL в уже закрытый I8 вместо downstream G8
   или G11.
3. Название I9 `atomic paper projection` пересекалось с нормативным G7
   `atomic architecture` и могло создать ложное впечатление, что working G2F
   candidate уже выбран до G3…G6.

## Исправление

- все 970 abstract-route occurrences / 59 unique labels внесены ровно в одну
  из пяти machine-validated classes;
- новый endpoint, stale classification, duplicate class, неполная class set
  или unresolved owner decision теперь ломают regression;
- четыре stale I8 references перенесены в G8/G11, а ранний nRF cost estimate
  явно superseded текущими exact-MPN cost records;
- I9 называется joint internally consistent **candidate** paper projection и
  прямо не является G7 atomic architecture.

## Последствие

I9 может получить **«Проведено ревью»** в G2F working-candidate scope. Это
разрешает возобновить G3 product/mockup work по `DEC-0058`, но не выбирает
target architecture, не замораживает pins/components и не разрешает KiCad.
