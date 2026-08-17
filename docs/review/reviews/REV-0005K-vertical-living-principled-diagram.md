# REV-0005K — vertical living principled diagram

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Owner instruction: диаграмма в `Principled solution design` должна быть
  вертикальной и обновляться при изменениях начинки
- Governing decision: [`DEC-0051`](../decisions/DEC-0051-principled-pinout-as-working-design.md)
- Machine projection: [`G2F-3I principled pinout`](../architecture/generated/G2F-3I-principled-pinout.md)

## Проверено

1. Обе стартовые диаграммы используют `flowchart TD` и невидимую
   layout-only vertical spine; она не является электрической связью.
2. Каждый физический компонент остаётся отдельным узлом с MPN и ролью.
3. Generated atlas использует ту же ориентацию и строится из current
   `devices.json/G2F-3I.json`.
4. Regression test проверяет направление, наличие vertical-spine marker и
   присутствие MPN-token каждого устройства current candidate в обеих
   стартовых диаграммах.
5. `DEC-0051` теперь требует обновлять обе стартовые диаграммы и generated
   atlas в том же коммите, что и принятое изменение начинки.

## Результат

- `python3 hardware/architecture/generate.py --check` — пройдено;
- `python3 -m unittest discover -s hardware/architecture/tests -v` —
  **39/39 пройдено**;
- электрическая карта и pin budget не изменены;
- открытый выбор `IMP-0049` не принят этой правкой.
