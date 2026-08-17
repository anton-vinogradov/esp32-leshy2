# IMP-0038 — visible qualified RF arbiter

- Статус: **Принято как A-GROUP решением `DEC-0045`; уточнено `DEC-0046`**
- Дата: 2026-08-17
- Finding: [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
- Architecture facts: [`RFQ-0002`](../architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md)

## Контекст решения

Цифровая карта уже не заставляет radio/IPC ждать чужую шину или DMA. Но S3,
C5 и 3×nRF находятся в 2.4 GHz, U214 пересекается с CC в 868/915 MHz, а
SA518 до 1 W пересекается с CC в 400–464 MHz. Произвольный local TX↔RX без
деградации потребовал бы десятки/сотню dB дополнительной развязки; фильтр не
отделяет wanted и local signal на одной частоте.

## Принятый вариант A-GROUP — честный встроенный RF arbiter

- каждый radio остаётся full-function и имеет независимые digital resources;
- `SG-N24` сохраняет все три полнофункциональных nRF одновременно активными и
  не скрывает их PTX/PRX mix через автоматический standby/time-sharing;
- S3/C5 native shared-chain modes и overlapping TX↔RX time-share физический RF;
- перед grant TX arbiter проверяет exact band/channel/power/antenna/profile,
  приостанавливает несовместимые RX и публикует gap/stale/loss/active owner;
- exact separated-band/channel pair может быть повышена из `X/T` в `Q` только
  после conducted/OTA HIL конкретной ревизии;
- base product платит за zoning, band filters, shields/test points и evidence,
  но не за универсальные remote heads.

Между разными signal groups потери функций нет: есть явное переключение группы.
Внутри `SG-N24` это правило не разрешает скрытые gaps; exact физическая граница
full mix вынесена в `IMP-0039`, потому что цифровой arbiter не создаёт RF
изоляцию между тремя близкими 2.4 GHz трактами.

## Вариант B — A плюс remote/conducted RF heads для Лаборатории

Base device использует A, а отдельный laboratory fixture выносит выбранные RF
paths по coax/remote head или в shielded room. Это может квалифицировать больше
точных пар, особенно U214↔CC и 2.4 TX↔RX, но добавляет connectors, cables,
calibration, ESD, fixture identity и стоимость. Даже он не обещает arbitrary
same-channel full duplex без duplexer/circulator и конкретного link budget.

## Вариант C — пытаться получить всё внутри корпуса

Добавить больше shield cavities, SAW banks, RF switches/couplers и antenna
isolation, сохранив обещание широкой внутренней одновременности. Это увеличит
BOM/area/loss и сузит перестраиваемые диапазоны, но всё равно не создаст
универсальной same-frequency развязки. Вариант не рекомендуется как product
contract; отдельные его элементы всё равно нужны в A.

## Рекомендация

Принять **A как обязательную product architecture** и **B как поддерживаемый
Controlled-Zone/Laboratory fixture profile**, не включённый в base BOM. Это
сохраняет все radios и максимально расширяет реально доказуемую concurrency,
не выдавая временные слепые интервалы за непрерывный capture.

## Решение владельца

[`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md) принимает более
строгий вариант `A-GROUP`: одновременно активна ровно одна versioned signal
group. Cross-group pair promotion base product больше не требуется. B остаётся
допустимым будущим Laboratory fixture, но не входит в base BOM и не блокирует
архитектуру. [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md)
добавляет hardware/native power-down и digital quiet-state всем неиспользуемым
интерфейсам. Full mix трёх nRF остаётся отдельным открытым acceptance choice,
а не отменяется этим решением.
