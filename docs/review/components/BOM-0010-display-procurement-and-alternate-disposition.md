# BOM-0010 — display procurement and alternate disposition

- Статус: **проведено ревью display line; standalone orderability/RFQ открыт**
- Дата: 2026-08-19
- Architecture: [`DSP-0008`](../architecture/DSP-0008-display-procurement-boundary-and-rfq.md)
- Review: [`REV-0005BI`](../reviews/REV-0005BI-display-procurement-propagation.md)

## Machine disposition

Для `qdtech_hmx035ctft_001` теперь machine-readable зафиксированы:

- два current complete-board specimen sources;
- exact production RFQ evidence checklist;
- `no_drop_in_substitute` alternate policy;
- три requalification-only lead, ни один из которых не выдан за equivalent.

`orderable_source` намеренно не добавлен: доступность платы с установленной
панелью не доказывает возможность заказать отдельную панель для PCBA. Поэтому
current totals становятся:

- orderability `187/188`;
- comparable quantity-100 component cost `0/188`;
- alternate/no-substitution disposition `1/188`.

## Procurement actions

1. Заказать минимум один `DLE06235B`/`ES3C35P-QD` как donor/HIL specimen.
2. Отправить QDtech/QDTFT exact standalone RFQ из `DSP-0008`.
3. Не использовать complete-board retail price как raw-panel COGS.
4. Не подменять HMX на AXS15231B/Leadtek только по диагонали и разрешению.
5. После ответа/образцов обновить exact assembly MPN, drawing revision,
   connector fit, quote, lifecycle и alternate disposition одним review.

Это закрывает метод получения prototype evidence и политику замены, но не
закрывает последнюю sourcing line и не разрешает KiCad.
