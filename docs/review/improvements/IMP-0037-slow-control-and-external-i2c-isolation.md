# ⚠️ IMP-0037 — complete slow-control plane and isolate external I²C

- Статус: **Открыто; требуется решение владельца**
- Дата: 2026-08-17
- Finding: [`FND-0052`](../findings/FND-0052-draft-maps-do-not-close-slow-control.md)
- Evidence: [`CTL-0001`](../architecture/CTL-0001-slow-control-and-external-i2c-boundary.md)

## Контекст решения

Нулевой свободный S3 GPIO сам по себе не является hard fail: меню и waterfall
не требуют отдельного interrupt на каждую кнопку, а внутренний I²C polling
может пройти accepted `≤100 ms` visible-response contract. Актуальный blocker:
16 slow ports не доказаны достаточными для planning envelope `19…27`, а внешний
U214/Port-A I²C fault сейчас способен повредить internal control bus.

Это решение задаёт только **рабочий G2F-инвариант** для следующей полной
компоновки. Оно не выбирает target MCU owner, expander MPN или финальную
архитектуру отдельно от atomic package.

## A — ≥24 slow endpoints и разделённые I²C domains, рекомендуется

- планировать common slow plane минимум на 24 endpoints;
- сохранить U214 IRQ прямым timing endpoint;
- ordinary controls/touch в active mode обслуживать bounded polling с HIL
  shortest-pulse/encoder-capture; touch IRQ и deep-sleep wake добавлять только
  после отдельного latency/power proof;
- internal UI/audio/receiver I²C отделить от U214/Port-A stuck-bus branch;
- GPIO7/8 использовать как независимый S3 `I2C1`, UART или custom Unit profile;
- `TCA6424ARGJR` и `TCA4307DGKR` использовать как первые exact references, но
  exact parts выбрать после закрытия touch/codec/receiver/voice/power pins.

Последствия: MCU GPIO не растёт; внешний кабель не валит меню/audio control;
один 24-port chip минимизирует адреса и BOM count. Цена — UQFN32 сложнее
ручного прототипирования, isolator добавляет BOM/area, а exact endpoint map и
HIL всё ещё обязательны.

## B — два 16-port expander, 32 endpoints

Даёт больше резерва, допускает prototype-friendly TSSOP и может разделить
input/output fault domains. Цена — второй IC, address/INT/reset wiring,
площадь, idle current, firmware/test surface и более высокая recurring BOM.

## C — оставить один TCA9535/16

Допустимо только после точного proof: UI compression, все reset/status/audio
lines, wake/interrupt policy и accessory isolation должны поместиться без
удаления функций. Это может оказаться самым дешёвым production-вариантом, но
сейчас такого доказательства нет; silent acceptance нарушила бы правило
zero-loss cost.

## Рекомендация

Принять `A` как working invariant. На следующем проходе generator получит
полный semantic endpoint ledger; затем сравнение точного 24-port решения с
двумя 16-port и доказанным compressed-16 будет частью единого архитектурного
пакета, а не преждевременным выбором корпуса.

## Вопрос владельцу

Принимаем вариант `A` как рабочий G2F-инвариант: минимум 24 slow endpoints,
прямой U214 IRQ и разделение internal/U214/Unit I²C domains, без выбора exact
expander до закрытия остальных периферийных контактов?
