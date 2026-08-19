# FND-0050 — nRF24 is NRND; CC1101 is active

- Статус: **Исходное lifecycle-обобщение исправлено; nRF24 risk остаётся открытым**
- Дата: 2026-08-17
- Обнаружено: exact-device/lifecycle pass для новых G2F-кандидатов
- Затрагивает: `REQ-N24-0001`, `REQ-SUB-0001`, `SRC-0002`

## Наблюдение

Требуемые compatibility paths опираются на зрелые silicon families, но их
актуальные lifecycle-статусы **разные**:

- Nordic относит nRF24 series к *not recommended for new designs*;
- актуальная карточка `CC1101RGPR` у TI показывает `ACTIVE`; TI определяет этот
  статус как recommended for new designs. Следовательно, переносить на CC1101
  статус NRND нельзя.

NRND не делает nRF24-функции невозможными и не отменяет ранее принятый полный
nRF24-compatible scope. Но доступность случайных marketplace boards или
существующий драйвер не доказывают устойчивую закупку, подлинность кристалла,
RF repeatability и долгосрочную заменяемость. Для активного CC1101 всё ещё
нужны exact sourcing и RF implementation proof, но это не lifecycle finding.

## Исправление статуса

- `E01-ML01S` используется только как реальный compact interface/geometry
  reference, а не как production choice трёх radio paths;
- bare `CC1101RGPR` доказывает silicon pin boundary, но не crystal/matching/
  antenna implementation;
- machine-generated ledger автоматически показывает lifecycle gap только для
  трёх nRF instances; CC1101 помечен `active`;
- будущий component pass обязан сравнить authorised sourcing, qualified
  alternates/compatible implementations, RF envelope и protocol HIL без
  удаления функции.

## Первичные источники

- [Nordic nRF24 lifecycle page](https://www.nordicsemi.com/Products/nRF24-series)
- [TI CC1101 product/order page](https://www.ti.com/product/CC1101/part-details/CC1101RGPR)
- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)

Немедленный выбор замены nRF не делается: сначала нужно установить, существует
ли современная совместимая реализация, сохраняющая принятые raw/full-function
сценарии и не увеличивающая стоимость/габарит больше исходного варианта.
