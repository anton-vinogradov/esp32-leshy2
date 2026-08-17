# IMP-0042 — external SMA gender/polarity and feed-class policy

- Статус: **Ожидает решения владельца**
- Дата: 2026-08-17
- Decisions: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md),
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- Evidence: [`RFH-0001`](../architecture/RFH-0001-module-to-external-sma-interface-review.md)
- Finding: [`FND-0057`](../findings/FND-0057-ebyte-ipx-mating-family-unproven.md)

## Контекст решения

Внешний класс `SMA` и число 9 уже приняты, но `SMA` не определяет polarity и
gender. Без этого нельзя задать antenna/accessory manifests, общий внешний
mechanical envelope и qualification references. Mounting/length пока выбирать
рано: они зависят от G3 physical layout.

## Вариант A — standard SMA jack на устройстве для всех 9 (рекомендуется)

Снаружи каждый path имеет standard 50-ohm SMA **jack/female centre contact**;
съёмные antennas/pods — standard SMA plug/male centre contact. Одинаковая
механика снижает число connector families, стоимость, запасные части и
количество переходников.

Ошибка antenna не предотвращается геометрией: девять диапазонов всё равно
невозможно закодировать только SMA/RP-SMA. Поэтому остаются permanent path/band
label, цветные collars/caps, antenna-profile manifest и TX interlock.
`RX-AM/LW` использует ту же механику только как keyed product interface, но не
объявляется generic 50-ohm long-coax port.

Внутри это не один feed SKU:

- S3/C5 — доказанный MHF I/U.FL/AMC-compatible plug class;
- nRF — тот же class только после `FND-0057` specimen gate;
- PCB RF paths — direct/short-coax launch выбирается в co-design;
- exact lengths, lock/IP rating и mount остаются G3 output.

## Вариант B — RP-SMA для 2.4/5 GHz, standard SMA для остальных

RP-SMA частично отделяет пять Wi-Fi/nRF ports от четырёх остальных, но не
различает S3, C5 и три nRF между собой и не кодирует диапазоны CC/voice/RX.
Появляются две polarity families, дополнительные harness/antenna SKUs и риск
переходников, которые уничтожают предполагаемую защиту. Capability не
улучшается; baseline cost/serviceability хуже.

## Вариант C — external SMA plug на устройстве

Технически возможен, но выступающий male centre contact у девяти device ports
хуже защищён при транспортировке и менее согласуется с готовыми
bulkhead-jack harness references. Не рекомендуется.

## Рекомендация

Принять **A** как внешний mating convention, не выбирая сейчас panel mounting
и cable length. Одновременно принять обязательный `FND-0057` sample gate и
запрет считать все девять paths одним электрическим feed/BOM item.

## Вопрос владельцу

Принимаем вариант **A: девять standard SMA jack на устройстве, antennas с SMA
plug, а различие диапазонов обеспечивают маркировка/profile manifest/TX
interlock; mount и длины выбираются позже в physical co-design**?
