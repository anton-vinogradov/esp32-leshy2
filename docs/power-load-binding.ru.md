# Привязка нагрузок питания R2

[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Состояния](power-state-register.ru.md) · [English](power-load-binding.md)

`H3-R2.1.2` прошёл структурное ревью: все `613` устанавливаемых экземпляра, касающихся одной из учитываемых шин, получили ровно по одной явной строке. Добавлены `6` внешних load contracts. Непривязанных строк — `0`, скрытых miscellaneous allowances — `0`.

## Что именно привязано

| Disposition | Строк |
|---|---:|
| `active_consumer` | 121 |
| `connector_or_external_boundary` | 11 |
| `conversion_or_protection_path` | 22 |
| `effective_capacitance_and_dc_leakage` | 241 |
| `indirect_powered_consumer` | 16 |
| `resistive_dc_branch` | 191 |
| `series_dcr_and_saturation` | 9 |
| `series_protection` | 2 |

## Что ещё не является pass

Это ревью полноты учёта, не численный DC-pass. Для каждой строки без применимого exact maximum `H3-R2.1.3` обязан извлечь параметр из закреплённого manufacturer source либо вернуть `unresolved_fail`. Child rails RP/codec/pack отмечены отдельно и не могут считаться второй раз поверх полного device total.

**Downstream-результат:** [`H3-R2.1`](power-dc-source-result.ru.md) полностью проведён ревью; актуальная точка всегда указана в [роадмапе](roadmap.ru.md).

[Полный машинный реестр строк](../hardware/verification/generated/H3-R2-load-binding.json).
