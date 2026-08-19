# DEC-0105 — machine-readable quantity-100 cost evidence

- Статус: **принято**
- Дата: 2026-08-19
- BOM review: [`BOM-0013`](../components/BOM-0013-first-quantity-100-cost-evidence.md)
- Propagation review: [`REV-0005BL`](../reviews/REV-0005BL-first-cost-evidence-propagation.md)

## Решение

1. Cost evidence для purchase line принимается только для exact current MPN,
   в USD и для закупки 100 изделий.
2. Каждая цена хранит positive unit price, точный тип опубликованной ценовой
   ступени, HTTPS source и дату проверки.
3. Если distributor публикует одну `1+` цену без промежуточной ступени и
   разрешает заказать 100 штук, это явно называется `1+ price applied to 100`,
   а не маскируется под отдельную ступень `100`.
4. RFQ-only, prototype-board retail price, другая упаковка/MPN, цена «от» без
   применимой ступени и валютный пересчёт не считаются сопоставимой ценой.
5. Непокрытая строка остаётся пустой; ей запрещено присваивать ноль.
6. Generator проверяет контракт, считает только покрытые physical placements,
   разделяет scope и маркирует сумму как partial subtotal, пока не закрыты все
   purchase lines и physical-gap families.
7. Базовый cost scope исключает PCB, PCBA, test, enclosure, tax, tariff,
   freight, yield и tooling до отдельных factory quotes.

## Почему

Иначе смесь розничных модулей, reel MOQ, supplier RFQ и component prices даёт
точное на вид, но несопоставимое число. Этот контракт позволяет постепенно
накапливать доказательства и искать cost-down без скрытой потери функции.

## Последствия

- первая партия может получить «Проведено ревью» независимо от незакрытого
  полного COGS;
- subtotal нельзя использовать как цену готового устройства;
- изменение exact MPN или substitution class требует нового price evidence и
  соответствующей requalification;
- решение не меняет электрическую архитектуру, распиновку или диаграмму.

`DEC-0106/BOM-0014/REV-0005BM` later extend this contract with explicit
machine-readable gates for researched RFQ/retail-only gaps.
`BOM-0016/REV-0005BO` then advance current coverage to 52/187 lines / 614
placements without changing these rules.
