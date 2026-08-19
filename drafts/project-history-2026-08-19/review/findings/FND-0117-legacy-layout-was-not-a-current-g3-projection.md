# FND-0117 — legacy layout was not a current G3 projection

- Статус: **Исправлено `G3-0001/REV-0005CE`**
- Дата: 2026-08-19
- Scope: `FLOW-0001/G3`

## Несоответствие

Legacy generator сохранил полезную clamshell-геометрию и семь проверок, но
его функциональная модель больше не совпадала с reviewed candidate:

- C5 ошибочно владел тремя nRF, тогда как current owner — RP;
- onboard LoRa занимал отдельный корпус/антенну вместо removable U214;
- 4-inch display и generic Si4732 скрывали current 3.5-inch HMX assembly и
  раздельные `RX-FM/SW` / `RX-AM/LW` antenna domains;
- не были представлены полный набор controls, три независимых service domains,
  exact battery holder, U214 overhang и current IR devices;
- board names одновременно означали физическую половину и compute ownership,
  что могло снова превратить историческую раскладку в архитектурное решение.

## Исправление

Создан новый active generator `hardware/product-design/g3_clamshell.py`. Он
читает current device/candidate machine source, проверяет exact key MPN,
девять antenna identities, полную control inventory, границы, overlaps,
mounting-hole/SMA keep-outs и U214/battery fit. Его SVG показывает отдельное
тело для каждого размещённого устройства и вынесенный читаемый
`номер → exact/current MPN → роль` register.

Физические половины теперь называются `UI/control` и `RF/power`. Current
working locality кладёт S3+C5/display/storage/audio/receiver/IR на первую, а
RP+3×nRF/CC/voice/U214/power — на вторую. Это сокращает critical local paths,
но остаётся G3 packing hypothesis, а не новая electrical ownership decision.

## Последствие

Legacy generator остаётся evidence source, но не active target. G3 получил
воспроизводимый current starting projection. Exact connector plane, complete
internal packing, cable bends, enclosure/control ergonomics and HIL remain
open; KiCad не разрешён.
