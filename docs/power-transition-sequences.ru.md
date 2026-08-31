# Запуск, сброс и восстановление · H3-R2.2.1

[English](power-transition-sequences.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

Проверка `H3-R2.2.1` завершена: все сценарии запуска и аварийного возврата проходят без автоматического повторного старта. Обычный fault аппаратно выключает опасные домены и напрямую сбрасывает C5/RF RP, но оставляет S3 для понятного сообщения, пока доступно питание UI.

## Правило запуска

Safety держит `SAFETY_FAULT_REQUEST` активным после сброса. Сначала self-test, затем физический `KILL` непрерывно 500 мс, и только следующий фронт `KILL→RUN` может тактировать аппаратную защёлку `RUN_PERMIT`. USB, software reset и исчезновение причины fault фронт не создают.

## Точные границы

- TPS3808 с открытым CT: `12..28 мс`; аварийное утверждение reset — не более `20 мкс`.
- TPS3435: запуск ИС — не более `500 мкс`, задержка запуска watchdog-окна — `0 мс`; timeout `1.44..1.76 с`, WDO low `180..220 мс`; heartbeat — `500 мс`.
- 100 кОм / 2,2 мкФ: расчётный rise `96.888..283.86 мс`, гарантированный tolerance-only discharge `484.525 мс`; это debounce, не единственный interlock.

## Проверенные сценарии

| Сценарий | Итог |
|---|---|
| `SEQ-01` · Cold start with switch at KILL | ✅ проходит |
| `SEQ-02` · Cold start with switch already at RUN | ✅ проходит |
| `SEQ-03` · RUN-at-boot followed by explicit KILL and RUN | ✅ проходит |
| `SEQ-04` · Insufficient KILL dwell | ✅ проходит |
| `SEQ-05` · Switch bounce fails closed | ✅ проходит |
| `SEQ-06` · Physical KILL or open loop during RUN | ✅ проходит |
| `SEQ-07` · Watchdog timeout and automatic WDO recovery | ✅ проходит |
| `SEQ-08` · Safety-controller reset during RUN | ✅ проходит |
| `SEQ-09` · Fault recovery while switch remains RUN | ✅ проходит |
| `SEQ-10` · Independent S3 fault-UI reset | ✅ проходит |
| `SEQ-11` · AON undervoltage or POR assertion | ✅ проходит |
| `SEQ-12` · Self-test failure | ✅ проходит |
| `SEQ-13` · USB attach cannot rearm a stopped product | ✅ проходит |
| `SEQ-14` · Complete qualified recovery after fault | ✅ проходит |

## Исправления

- S3 получил отдельный reset через M1-36 и остаётся fault-UI; C5 и RF RP по-прежнему сбрасываются напрямую.
- Вход PA23 получил внешний 10-кОм pulldown переиспользованием прежней лишней позиции: BOM и цена не выросли.
- Антиавтозапуск теперь опирается на квалифицированный физический KILL, а не на предположение о моменте RC-фронта.

## Что остаётся физике

- H8 measures real switch bounce and break-before-make interval.
- H8 measures the populated 100-kohm/2.2-uF RC under DC bias and temperature; startup safety does not depend solely on this number.
- H8 captures POR assertion/release, direct C5/RF-RP reset and S3 fault-display retention at real rail corners.

**Результат:** `14/14` сценариев и `51` endpoint-проверок проходят. H3-R2.3 и [цифровая проверка H3-R2.4](digital-electrical-verification.ru.md) проведены ревью; **текущий маркер — `H3-R2.5`**. Заказ и трассировка всё ещё запрещены.

[Машинный отчёт](../hardware/verification/generated/H3-R2-transition-sequences.json).
