# FND-0039 — architecture was frozen before product design and whole-device optimality

- Статус: **Закрыто переоткрытием архитектуры; проведено ревью исправления**
- Дата: 2026-08-16
- Обнаружено владельцем до начала схемы/PCB
- Решение: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)

## Несоответствие

После requirement-level wishlist работа сразу перешла к compute domains,
controllers, pins, buses, exact variants and component CAD. `SYN-0001`
сравнивал три размещения уже предполагаемого набора электронных блоков, но до
этого не был принят целевой физический дизайн устройства:

- form factor, габаритный/массовый envelope и способ ношения/удержания;
- display/control surface, доступность STOP/PTT/service controls и эргономика;
- battery concept, зарядка, разъёмы, крышки, кабели и external-module strategy;
- antenna volumes, ориентация устройства, человеческое тело и RF separation;
- board partition, enclosure openings, assembly/repair and environmental goals;
- целевая стоимость и ранжированные критерии оптимальности.

Следовательно, `SYN-2A/2B/3A` были полезными electronic-placement studies, но
не несколькими независимыми whole-product architectures. Их сравнение не могло
доказать глобальную оптимальность, а `DEC-0028` не имел достаточных
пререквизитов для финального выбора `SYN-3A`.

Stage 4 затем начал exact component qualification и KiCad before enclosure,
concept placement and accepted architecture. Reproducibility конкретной CAD
геометрии не исправляет ошибочный порядок входов.

## Исправление

1. `DEC-0028` и `PKG-0001/SYN-3A` понижены до superseded candidate/reference.
2. Exact C5/RP/S3 variants, owners, buses, pins and connector topology больше
   не являются product contract.
3. Постоянный независимый programming/recovery/diagnostic access каждого
   реально выбранного programmable chip сохранён как requirement, без
   преждевременного назначения USB/header/pins.
4. Active KiCad libraries/CI removed. The exact tracked compute snapshot is
   preserved under a non-canonical draft; the never-committed service-CAD
   experiment is recorded as discarded rather than presented as reproducible.
5. Corrected product→architecture→CAD gates are normative in [`FLOW-0001`](../architecture/FLOW-0001-product-to-cad-gates.md).

## Проверка потерь

Принятые capabilities, safety/legal levels, non-aggression onboarding,
conservative TX defaults, full-function three-nRF requirement, external GNSS/
LoRa/NFC desires and open owner-controlled firmware remain inputs. Only their
premature physical implementation is reopened.

No schematic or PCB had been started, so the correction avoids fabrication
rework. Historical studies stay available as evidence and negative results but
may not be consumed as final prerequisites.
