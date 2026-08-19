# FND-0057 — Ebyte `IPX` mating family is not proven

- Статус: **Несоответствие подтверждено; machine source исправлен, specimen gate открыт**
- Серьёзность: connector damage / intermittent RF / three-nRF symmetry blocker
- Обнаружено: 2026-08-17
- Evidence: [`RFH-0001`](../architecture/RFH-0001-module-to-external-sma-interface-review.md)

## Несоответствие

Active architecture source называл E01-ML01IPX antenna contact просто
`on-module IPEX connector`, а документы и обсуждение уже предполагали короткий
IPEX→SMA pigtail. Это недостаточная provenance:

- `I-PEX` — производитель и семейство торговых марок, а не один размер;
- Ebyte PDF/страница используют только generic `IPX/IPEX`;
- PDF не сообщает generation, receptacle MPN, mating dimensions или
  совместимость с U.FL/MHF I/AMC;
- официальный PDF дополнительно имеет stale embedded title
  `E01-2G4M27D_产品规格书_v1.0`, хотя видимые header/content описывают
  `E01-ML01IPX`; content evidence пригодно, но document-control quality не
  позволяет заполнять отсутствующие connector facts догадкой;
- рисунок похож на first-generation micro-coax, но изображение не является
  mechanical compatibility specification.

S3/C5 при этом не имеют той же неопределённости: Espressif прямо называет
first generation и три совместимых mating families.

## Исправление

- machine source теперь говорит `manufacturer-labelled IPX; exact mating
  family unproven`, а не обещает совместимый pigtail;
- до sample gate E01-ML01IPX остаётся layout/reference direction, не frozen
  production RF assembly;
- общий harness SKU для S3/C5/nRF запрещён без отдельного доказательства всех
  трёх Ebyte specimens/lots.

## Критерий закрытия

1. Получить production-representative E01-ML01IPX specimens и lot markings.
2. Снять microscope/measurement evidence receptacle geometry.
3. Проверить fit только документированным MHF I/U.FL/AMC plug MPN без
   деформации и с требуемым engagement/retention.
4. Выполнить VNA through/reference и flex/vibration continuity test.
5. Зафиксировать approved module revision/lot и mating harness MPN либо
   заменить module candidate на вариант с опубликованным exact connector.

## Первичный источник

- [Ebyte E01-ML01IPX 2025 specification](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf)
