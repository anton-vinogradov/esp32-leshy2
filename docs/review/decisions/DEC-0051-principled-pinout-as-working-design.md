# DEC-0051 — principled pinout as the visible working design

> Последующее изменение: `DEC-0052/REV-0004X` добавляют direct-QSPI D2/D3 на
> S3 GPIO41/42 и меняют S3 budget с `29/3/4` на `31/3/2`; `DEC-0054/REV-0005D`
> затем назначают GPIO6 `AUDIO_ARM` и дают current `32/3/1`, сохраняя правило
> machine-source/regeneration настоящего решения.

- Статус: **Принято по прямому указанию владельца**
- Дата: 2026-08-17
- Основание: принципиальная распиновка должна быть видимой частью design-дока,
  а не только внутренним generated/review artifact
- Artifact: [`PIN-0003`](../architecture/PIN-0003-g2f-3i-principled-pinout.md)
- Generated source view: [`G2F-3I principled pinout`](../architecture/generated/G2F-3I-principled-pinout.md)
- Reviews: [`REV-0004V`](../reviews/REV-0004V-principled-pinout-self-review.md),
  [`REV-0005K`](../reviews/REV-0005K-vertical-living-principled-diagram.md)

## Решение

1. `G2F-3I/PIN-0003` принимается как **текущий принципиальный working design**
   для G3 physical/product layout: owners, основные interface groups, exact
   compute contacts, resource separation, service/recovery и pin budgets.
2. Корневой hardware target-док показывает этот дизайн отдельным разделом:
   owner diagram, принципиальные pin groups, budget и прямую ссылку на полный
   exact pad/net atlas.
3. Единственным источником exact контактов остаются
   `hardware/architecture/devices.json` и `G2F-3I.json`. Корневой документ —
   обозримая design-проекция; generated atlas — полная проверяемая таблица.
4. Working design не является final `G7` atomic architecture или разрешением
   на KiCad. `FND-0060`, exact production parts, physical packing, RF/power/SI,
   whole-device optimality и HIL могут переоткрыть карту.
5. Изменение working pinout выполняется через machine source, regeneration,
   повторное review и синхронное обновление design-проекции. Молчаливое
   расхождение README и generated atlas запрещено.
6. Диаграмма `Principled solution design` поддерживается в узком вертикальном
   формате `top-to-bottom`. Любое принятое изменение начинки — устройства,
   owner, шины или межкомпонентного тракта — обновляет обе стартовые диаграммы
   и generated atlas в том же коммите; regression test проверяет orientation и
   присутствие каждого current candidate MPN.

## Последствия

- распиновка становится видимым design contract, а не скрытым приложением;
- G3 использует конкретную карту и возвращает найденные packing/RF/power
  конфликты в G2F;
- статус остаётся честным: principle mapping reviewed, final electrical and
  whole-device architecture open.
