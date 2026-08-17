# DEC-0044 — delegated non-interference layout search

- Статус: **Принято владельцем; цифровая компоновка проведена ревью**
- Дата: 2026-08-17
- Основание: владелец передал подбор компоновки исполнителю, потребовал
  перебирать варианты до сходимости и отдельно обсуждать только неизбежное
  влияние соседних радио/интерфейсов
- Принимает: [`IMP-0037/A`](../improvements/IMP-0037-slow-control-and-external-i2c-isolation.md)
- Артефакт: [`NIF-0001`](../architecture/NIF-0001-digital-noninterference-layout.md)

## Решение

До atomic architecture исполнитель самостоятельно выбирает и отбрасывает
варианты owners/controllers/pins по следующим инвариантам:

1. ни один radio FIFO/IRQ/PTT/actual-TX deadline не ждёт владения шиной
   соседнего радио, display, storage или внешнего accessory;
2. каждое междоменное IPC имеет отдельный аппаратный controller и выполняет
   принятый framed-throughput/latency contract;
3. разделяемый ресурс разрешён только для нетайминговых интерфейсов с явным
   arbiter, максимальным непрерываемым quantum, наблюдаемой задержкой и HIL;
4. каждый programmable domain сохраняет независимые programming, recovery и
   diagnostics без исправного peer/application image;
5. GPIO считаются по реально выведенным контактам exact package/module, а не
   по GPIO кристалла;
6. physical RF self-desense/coexistence не маскируется цифровой независимостью
   и выносится отдельным решением, если antenna/filter/zoning proof не даёт
   одновременность без деградации.

`IMP-0037/A` принят как рабочий инвариант: минимум 24 slow endpoints, прямой
U214 IRQ и разделённые internal, Unit и U214 I²C fault domains. Это принимает
ёмкость и границы, но не замораживает production MPN.

## Текущий результат

`G2F-3I` становится **ведущей бумажной цифровой компоновкой**, а не target
architecture. Он использует RP2354B A4/QFN80, отдельные data/IRQ paths для
3×nRF24, CC1101 и U214, dedicated 4-bit SDIO S3↔C5 и dedicated SPI3 S3↔RP.
Единственная high-rate scheduled pair — display+microSD на SPI2; она не
обслуживает radio FIFO/IPC и имеет bounded arbitration contract.

Финальное принятие owners/parts/board/layout остаётся atomic: exact
peripherals, power, physical RF, mechanics, cost and HIL должны сойтись вместе.
