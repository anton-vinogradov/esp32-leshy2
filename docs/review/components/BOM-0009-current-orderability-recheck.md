# BOM-0009 — current exact-line orderability recheck

- Статус: **проведено ревью текущей заказываемости; один display residue открыт**
- Дата: 2026-08-19
- Finding: [`FND-0111`](../findings/FND-0111-orderability-audit-exposed-pseudo-mpn-and-display-gap.md)
- Decision: [`DEC-0102`](../decisions/DEC-0102-exact-sc1512-a4-order-identity.md)
- Machine view: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)

## Проверенный scope

Проверены все 33 used BOM lines, у которых после `BOM-0008` отсутствовал
датированный `orderable_source`. Проверка выполнялась по exact order code, а не
по имени семейства или похожей поисковой выдаче. Для источника зафиксированы
дата, тип доказательства, документ и URL.

## Результат

| Класс результата | Lines | Что доказано | Что не доказано |
|---|---:|---|---|
| current exact source recorded | 32 | exact identity присутствует у производителя, production supplier или distributor/authorized aggregation | будущий stock, landed factory price и alternate equivalence |
| standalone source unresolved | 1 | official reference schematic раскрывает `HMX035CTFT-001` и его contacts; `BOM-0010` later proves complete-board specimen access | отдельный raw-panel order page/quote, approval drawing/lifecycle и стабильный production channel |

После recheck текущая machine-readable coverage равна `187/188`. Эта метрика
не называется «все детали лежат на складе»: manufacturer RFQ/current-product
страница и live distributor stock — разные уровни evidence. Особенно
ограниченные строки остаются видимыми в собственном `orderable_source`.

## Exact identity correction

`SC1512-A4` заменяет прежнюю prose-псевдостроку RP. Это действительный код
заказа RP2354B0A4 в 7-inch reel. В документах, предназначенных человеку,
используется форма `SC1512-A4 (RP2354B0A4)`; в BOM поле MPN содержит только
`SC1512-A4`.

## Не смешивать с physical gaps

Следующие items пока не являются пропущенными строками среди 188 used MPN:

- 9 внешних SMA connector bodies — зависят от connector plane и mechanics;
- 5 RF cable assemblies — зависят от полученных RF-модулей и placement;
- 2 M5 connector bodies — зависят от полученного U214/cable и fit coupon;
- 12 external antenna-kit items — зависят от RF qualification и regional
  variant.

Их нельзя выбрать по фотографии до завершения внутренней архитектуры и
возобновления physical mockup. Они остаются отдельными обязательными gates, а
не исчезают из BOM.

## Следующий порядок I8

1. разрешить exact display sourcing без скрытого изменения endpoint;
2. назначить оставшимся 187 used lines qualified alternate, parametric policy
   либо explicit no-drop-in-substitute; display disposition already exists;
3. собрать сопоставимые quantity-100 cost snapshots;
4. материализовать четыре physical families после соответствующих
   mechanics/RF specimen gates;
5. выполнить consolidated I8 self-review.
