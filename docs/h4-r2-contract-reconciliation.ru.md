# Сверка контрактов железа и прошивки H4-R2

[English](h4-r2-contract-reconciliation.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Фиксация входов](h4-r2-input-freeze.ru.md)

`H4-R2.0.2` и объединённый cross-check `H4-R2.1` проведены ревью. Six-domain контракт H2, все 80 контактов M1, текущие импорты H3, владение USB/service, прямой i8080 на 20 МГц и границы утверждений target-build совпадают между репозиториями.

Ревью нашло одну ограниченную implementation-проблему с тремя владельцами доменов: сгенерированный BSP F2 пока представляет лишь `135` из `173` текущих controller-строк H2. Недостающие `38` строк — пропуск генерации прошивки, а не изменение аппаратной распиновки.

| Домен | Строк H2 | Строк BSP | Не хватает | Текущее отображение |
|---|---:|---:|---:|---|
| `s3` | 33 | 33 | 0 | `exact_pins` |
| `c5` | 14 | 6 | 8 | `partial_exact_pins` |
| `rf_rp` | 48 | 48 | 0 | `exact_pins` |
| `hub_rp` | 48 | 48 | 0 | `exact_pins` |
| `pack` | 13 | 0 | 13 | `identity_only` |
| `safety` | 17 | 0 | 17 | `identity_only` |

H4-R2.2 должен сгенерировать полные точные карты C5, Pack и Safety и заставить их target-проекты fail-closed проверять точный mapping/count. Отдельное обязательство F5/F6 по драйверу дисплея остаётся открытым намеренно; никакое физическое evidence H5/H6/H8 не поглощено.

**Текущий маркер: `H4-R2.2`.** Закупка, placement, routing и печать остаются запрещены.

[Машинная сверка](../hardware/verification/generated/H4-R2-contract-reconciliation.json) · [машинный объединённый cross-check](../hardware/verification/generated/H4-R2-joined-crosscheck.json).
