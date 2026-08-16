# DEC-0034 — M5-first two-tier expansion without native M5-Bus

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-16
- Ответ владельца: **B**
- Предложение: [`IMP-0028`](../improvements/IMP-0028-m5-first-not-m5-only-expansion.md)
- Evidence: [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md)
- Нормативный контракт: [`REQ-EXT-0001`](../requirements/REQ-EXT-0001-m5-first-expansion-platform.md)

## Решение

1. M5 становится основным низкоскоростным accessory ecosystem Leshy2, но не
   универсальным интерфейсом и не единственным expansion path.
2. Native product profiles поддерживают M5 Unit A/B/C/custom через HY2.0-4P и
   полный Cardputer-compatible 14-pin Cap contract, необходимый U214.
3. Базовое устройство не получает нативный 30-pin M5-Bus. Конкретный M5-Bus
   Module может поддерживаться только через отдельно квалифицированный carrier
   с exact pin/power/enable/firmware profile.
4. Для raw SDR/IQ, внешнего compute и general host/data сохраняется отдельный
   high-throughput expansion class. Низкоскоростной Unit/Cap transport не
   выдаётся за эквивалент high-speed data path.
5. Архитектура должна стремиться покрыть не менее 90% релевантных external
   attachment classes сочетанием двух tiers. Reachability не означает готовую
   функцию: каждый exact accessory всё равно проходит qualification.

## Что решение пока не выбирает

- число и расположение Unit-портов;
- пассивный dock либо несколько fixed A/B/C surfaces;
- разъём, USB generation, role, port count и power budget high-speed tier;
- MCU owner, bus routing, GPIO, enclosure и exact load-switch BOM;
- какие дополнительные catalog-возможности становятся product scope.

Эти пункты сравниваются в G3/G4 и затем принимаются атомарной архитектурой.
`W-EXTRA-16` остаётся отдельным вопросом о пользовательском результате
high-speed USB host, а не скрыто закрывается этим infrastructure-решением.

## Цена и граница продукта

M5-first снижает обязательный base BOM за счёт выноса редких frontends и
controls, но требует защищённого default-off питания, exact manifests,
механического удержания и HIL. High-speed tier добавляется в конкретный product
candidate только вместе с доказанными use cases, power/ESD/role UX и стоимостью.
Стоимость сравнивается отдельно для base device, вероятного field kit и
максимального Lab kit.

## Последствия

- `IMP-0028` закрыт вариантом B;
- `FND-0042` закрыт на уровне product model, но electrical/mechanical/HIL proof
  остаётся downstream;
- G2 продолжает current competitor delta с `W-EXTRA-12`;
- target README обоих репозиториев получают двухуровневый expansion contract.

