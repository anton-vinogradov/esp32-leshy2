# DEC-0106 — explicit gates for unpriced purchase lines

- Статус: **принято**
- Дата: 2026-08-19
- Основание: [`DEC-0105`](DEC-0105-machine-readable-quantity-100-cost-evidence.md)
- BOM review: [`BOM-0014`](../components/BOM-0014-high-placement-cost-and-explicit-gates.md)
- Propagation review: [`REV-0005BM`](../reviews/REV-0005BM-second-cost-evidence-propagation.md)

## Решение

1. Отсутствие сопоставимой USD price на 100 изделий теперь может иметь
   отдельный machine-readable `cost_gate` с обязательными `status`, `reason`,
   HTTPS source и датой проверки.
2. Числовой `cost` и `cost_gate` взаимоисключающи. Gate объясняет, почему
   строка не вошла в subtotal; он не является ценой и не закрывает cost.
3. Допустимые первые состояния:
   - `quantity_100_rfq_required`;
   - `retail_only_no_quantity_100_tier`;
   - `regional_retail_only_no_quantity_100_tier`;
   - `standalone_raw_assembly_rfq_required`.
4. Розничную цену нельзя умножать на 100, а скрытую RFQ-цену нельзя заменять
   нулём, marketplace estimate или ценой похожего MPN.
5. Generated Markdown и CSV обязаны выводить gate отдельно от priced lines и
   не включать его в partial subtotal.

## Почему

Просто пустая цена не различает непроведённый поиск, обязательный RFQ,
несопоставимую розницу и отсутствие standalone товара. Явный gate делает
следующее действие проверяемым и исключает ложную точность в COGS.

## Последствия

- текущие пять проверенных исключений получают явный маршрут закрытия;
- остальные unpriced lines остаются обычными gaps до их собственного pass;
- это procurement metadata: функции, состав, контакты, питание и diagram не
  меняются;
- I8 остаётся открыт до полного component/factory cost и физических gaps.

`BOM-0018/REV-0005BR` later preserve the existing gates and add two honest
currency-comparability gates. `BOM-0022/REV-0005BV` advance numeric coverage
to 133/187 lines / 787 placements; ten explicit gates remain and the gate
contract is unchanged.
