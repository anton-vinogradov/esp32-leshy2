# ⚠️ IMP-0035 — one source for device pins and physical layout

- Статус: **Требуется решение владельца**
- Дата: 2026-08-17
- Основание: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md),
  [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)

## Текущее состояние

Legacy Python generator хорошо проверяет physical geometry, но component data,
pin maps и review Markdown живут отдельно. Новый `SRC-0002` добавляет ещё один
обязательный слой: exact MPN/revision, package/module pad, реально выведенный
контакт и source version. Ручное дублирование создаёт риск, что diagram,
pin-budget и device qualification снова разойдутся.

## Варианты

### A — один versioned data model, рекомендуется

Создать активный data-driven generator. Versioned device inventory хранит exact
MPN, dimensions/heights/keepouts, exposed contacts, power/level, sources и
qualification status; candidate netlist связывает semantic endpoint с owner,
controller и exact pin. Один запуск:

- проверяет uniqueness, strap/reset/recovery, controller-instance и unknown
  device rows;
- генерирует Markdown/CSV pin ledgers и block diagrams;
- подаёт те же dimensions/interfaces в унаследованные physical checks и SVG;
- падает, если drawing использует незакрытый или несуществующий контакт.

Цена: сначала нужно аккуратно отделить данные от рисования и написать schemas/
validators. Выигрыш: меньше повторной ручной работы, меньше drift, проще
сравнивать candidate maps и автоматически перепроверять изменения MPN.

### B — оставить таблицы и drawing script раздельными

Быстрее получить первый рисунок: pin maps остаются Markdown, а script получает
размеры вручную. Цена — постоянная ручная cross-check matrix и высокий риск
тихого расхождения при каждой смене owner, module или footprint.

## Рекомендация

Принять `A`. Первый incremental milestone не требует большой системы: schema
для compute/U214/nRF candidates, validation exact exposed pins и генерация
used/free ledger. Старые geometric checks подключаются после review двух
электрических maps.

