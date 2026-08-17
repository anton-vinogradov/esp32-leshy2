# IMP-0047 — one-stop PCBA and antenna-kitting policy

- Статус: **Принято как вариант B в DEC-0056**
- Дата: 2026-08-17
- Facts: [`MFG-0001`](../architecture/MFG-0001-one-stop-pcba-antenna-kitting.md)
- Antenna decision: [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md)
- Decision: [`DEC-0056`](../decisions/DEC-0056-prefer-one-stop-kitting-with-fallback.md)

## Контекст

Один заказ уменьшает ручную логистику и риск перепутать 12 antenna items, но
жёсткое требование «только одна фабрика» сужает выбор PCBA supplier и может
увеличить цену и срок. Seeed и Elecrow прямо предлагают kitting; стандартные
JLCPCB/PCBWay flows не дают достаточного основания считать loose antennas
обычными PCBA parts.

## Варианты

- **A — hard requirement:** PCBA supplier обязан сам закупить, промаркировать и
  упаковать antennas. Проще получение, но меньше конкуренция и выше риск
  наценки/срока.
- **B — preference with fallback:** сначала RFQ Seeed/Elecrow на единый kit;
  если цена, качество или срок хуже, платы и antennas заказываются раздельно.
  Сохраняет экономическую конкуренцию и является рекомендуемым вариантом.
- **C — separate by design:** всегда отделять PCBA от antenna procurement.
  Максимальный выбор поставщиков, но ручной комплектовочный труд и риск ошибок.

## Решение владельца

Принят **B**: one-stop kitting является первым RFQ и предпочтением, но не
жёстким ограничением выбора фабрики. Если total cost, срок, quality/test scope
или supply risk хуже, PCBA и antennas заказываются раздельно.
