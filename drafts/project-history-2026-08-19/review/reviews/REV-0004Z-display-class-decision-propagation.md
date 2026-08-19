# REV-0004Z — display-class decision and part-number propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md) /
  [`DSP-0004`](../architecture/DSP-0004-display-part-number-register.md)

## Проверка

- Owner acceptance `IMP-0045/A` записано как `DEC-0053`.
- Hardware target/readme/status/stage и firmware upstream/runtime docs называют
  один класс: 3.5-inch portrait `320×480` IPS, direct QSPI, capacitive touch.
- Primary/secondary HIL references не названы production parts.
- Все известные order identifiers/controller markings/fallback MPN собраны в
  mobile-readable vertical register.
- Отсутствующие raw-panel, connector, touch, backlight, protection и optics
  MPN явно имеют status `TBD`; controller name не подменяет panel MPN.
- Старый 4-inch `ST7796S` закрыт как A0/control fixture, а не QSPI target.
- Current S3 pin/resource map не изменён: решение выбирает класс на уже принятой
  direct-QSPI шине.

## Итог

`DEC-0053` получает статус **«Проведено ревью распространения»**. Exact
production assembly и его init/HIL остаются downstream gate, поэтому KiCad и
production firmware driver ещё не разрешены.

## Последующее исправление

`FND-0063/REV-0005A` установили, что official QDtech schematic всё-таки
раскрывает assembly marking `HMX035CTFT-001`. Это исправляет прежнее
утверждение про отсутствующий raw MPN, но не меняет production boundary:
standalone orderability/drawing/lifecycle и qualification остаются открыты.
