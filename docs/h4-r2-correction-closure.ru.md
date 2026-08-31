# Закрытие исправлений BSP H4-R2.2

[English](h4-r2-correction-closure.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Диагностика](h4-r2-contract-reconciliation.ru.md)

Три назначенных исправления firmware-generation закрыты без изменения аппаратной распиновки. Сгенерированный BSP теперь представляет все **173/173** проведённых H2 controller-строк; каждый target отказывается от нормального старта при неполном mapping/count.

| Домен | Строк H2 | Строк BSP | Mapping | Итог |
|---|---:|---:|---|---|
| `s3` | 33 | 33 | `exact_pins` | ✅ |
| `c5` | 14 | 14 | `exact_pins` | ✅ |
| `rf_rp` | 48 | 48 | `exact_pins` | ✅ |
| `hub_rp` | 48 | 48 | `exact_pins` | ✅ |
| `pack` | 13 | 13 | `exact_pins` | ✅ |
| `safety` | 17 | 17 | `exact_pins` | ✅ |

Исправленный BSP скомпилирован и слинкован во всех **12** закреплённых конфигурациях debug/release. Квалификация проверила **60 artifacts, 16 map-файлов и 16 size gates** без build warnings. Это доказывает интеграцию и линковку target-кода, но не runtime boot и не физическое железо.

Отдельное обязательство F5/F6 по direct i8080 и все 51 physical-остаток H5/H6/H8 остаются открытыми. Закупка, placement, routing и печать не разрешены.

[Глобальный объединённый gate H4-R2](h4-r2-acceptance.ru.md) проведён ревью. **Текущий маркер: `H5.0.3-R1`.**

[Машинное закрытие](../hardware/verification/generated/H4-R2-correction-closure.json).
