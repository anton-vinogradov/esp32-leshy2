# DEC-0056 — prefer one-stop PCBA/antenna kitting with fallback

- Статус: **Принято владельцем; проведено ревью propagation**
- Дата: 2026-08-17
- Owner answer: `B`
- Proposal: [`IMP-0047`](../improvements/IMP-0047-one-stop-pcba-antenna-kitting-policy.md)
- Facts: [`MFG-0001`](../architecture/MFG-0001-one-stop-pcba-antenna-kitting.md)
- Propagation review: [`REV-0005F`](../reviews/REV-0005F-kitting-policy-decision-propagation.md)

## Решение

Для prototype и production RFQ действует следующий порядок:

1. Сначала запрашивается единый turnkey offer: PCB fabrication, PCBA,
   procurement и упаковка loose antenna kit.
2. One-stop offer сравнивается с раздельной закупкой по total landed cost,
   сроку, substitutions, traceability, quality/test scope и риску поставки.
3. Если единый offer проигрывает по существенному критерию, PCBA и antennas
   можно заказать раздельно без изменения архитектуры продукта.

One-stop kitting является предпочтением, а не hard supplier constraint. Seeed
и Elecrow — первые RFQ candidates по документированной способности kitting;
это не утверждает заранее выбранную фабрику. JLCPCB, PCBWay и другие suppliers
не исключаются, если раздельная либо письменно подтверждённая custom supply
оказывается лучше.

## Неизменные требования к комплекту

- exact MPN и количество каждой loose antenna;
- `no substitution without written approval`;
- раздельная маркировка port/profile и SMA/RP-SMA;
- lot/quantity traceability и согласованный incoming inspection;
- pigtails/harnesses/крепёж отдельными BOM lines;
- RF qualification не подменяется фактом комплектования фабрикой.

Решение не выбирает exact MPN, supplier или quantity. Эти параметры появляются
на BOM/RFQ gate после architecture/product-design closure.

