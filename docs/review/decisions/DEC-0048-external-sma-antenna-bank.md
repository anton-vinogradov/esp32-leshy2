# DEC-0048 — external SMA antenna bank and compact nRF IPEX paths

- Статус: **Принято**
- Дата: 2026-08-17
- Основание: владелец уточнил, что все антенны базового устройства в макете
  предполагались внешними и SMA
- Proposal: [`IMP-0040`](../improvements/IMP-0040-three-nrf-module-and-antenna-baseline.md), вариант A
- Evidence: [`N24M-0001`](../architecture/N24M-0001-exact-module-antenna-comparison.md)
- Geometry source: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)

## Решение

1. Все antenna endpoints бортовых RF-трактов Leshy2 выводятся на доступные
   снаружи SMA. Встроенные PCB/chip antennas не являются baseline готового
   устройства.
2. Три nRF paths используют три одинаковых compact 0 dBm modules с IPEX и три
   независимых коротких pigtails к трём отдельным внешним SMA. Один общий
   radiator, RF switch или shared feed не эквивалентны simultaneous
   `3R/1T2R/2T1R/3T` и запрещены.
3. `E01-ML01IPX` становится verified layout/reference direction для всех
   сравниваемых electrical candidates. Exact production MPN/revision, genuine
   lot, approved source и HIL ещё не являются BOM freeze.
4. `E01-ML01S` со встроенной PCB antenna остаётся bench/reference alternate и
   не может автоматически заменить target module. 20/27 dBm PA/LNA variants
   не входят в base BOM; возможен отдельный Laboratory remote-head profile.
5. Полезный принцип legacy mockup сохраняется: внешние antenna positions,
   максимальный практический разнос и короткие внутренние feeds. Старые owner,
   число всех разъёмов и generic footprints не наследуются.
6. Антенны съёмные, поэтому каждый порт получает постоянную band/path marking,
   а TX profile требует подтверждённую совместимую antenna configuration.
   SMA сам по себе не доказывает правильную антенну, EIRP или legal profile.
7. Exact SMA gender/polarity, straight/right-angle implementation, bulkhead
   против edge-launch и cable SKU/loss/bend/retention выбираются позже по
   цельной RF/mechanical компоновке. Итоговые девять antenna endpoints и их
   identities позже закреплены `DEC-0049`.
8. Внешние M5 Unit/Cap accessories не считаются бортовыми antenna paths: они
   сохраняют собственный разъём/антенну и квалифицируются своим manifest.

## Последствия

- `IMP-0040/A` принят; integrated-PCB option B удалён из target direction;
- все три `G2F` paper candidates используют один и тот же
  `E01-ML01IPX` real-device reference, поэтому owner comparison не смешивается
  с antenna/module различиями;
- machine validation отклоняет возврат nRF candidates к встроенной PCB antenna
  или попытку считать меньше трёх dedicated SMA;
- adapted legacy generator обязан рисовать external SMA identities и cable
  envelopes из единого architecture source, а не из старого fixed count.
