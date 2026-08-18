# DEC-0098 — exact independent M5 expansion boundary

Статус: **принято; проведено ревью в paper scope**.

## Решение

1. Поддержать и rear U214 Cap-Bus, и отдельный native HY2.0-4P Unit port.
2. Сохранить один fixed-5-V buck, но дать каждому внешнему 5-В контакту
   собственный true-reverse-blocking `TPS259470LRPWR` branch.
3. Выделить P17 под `U214_5V_REQ`, P05 под `UNIT_5V_REQ`; STOP аппаратно
   доминирует над общим buck и обеими branch eFuse.
4. Разрешать сигналы только после отдельного `TPS3808G33DBVR` branch READY.
5. Защитить девять U214 SPI/UART/control lines тремя `74LVC126APW,118`, I²C —
   `TCA4307DGKR`, все 11 наружных signals — тремя `TPD4E05U06DQAR`.
6. Защитить native Unit signals `TXS0102DCUR` и отдельным
   `TPD4E05U06DQAR`.
7. Удалить фиктивный `ACCESSORY_PRESENT_N`; P26 становится `UNIT_READY`.
8. Unknown accessory остаётся без питания; после явного manifest выполняется
   power-ready и profile-specific identity/readback.
9. Не резервировать generic USB host. Future high-throughput transport может
   появиться только из конкретного RF/SDR profile.
10. Не замораживать MPN обоих connector bodies без physical specimen/coupon.

## Следствия

- U214 и native Unit можно включать по отдельности или вместе, не включая
  неиспользуемый интерфейс.
- Внешнее питание одного разъёма не подпитывает другой и общий buck.
- GPIO MCU не меняются; main slow I/O закрывается `24/0/0`.
- Оценка добавки защиты/изоляции: USD 4,5–6,5 при qty 100 без connector bodies.
- Physical/HIL остаётся обязательным и может переоткрыть exact passives,
  connector MPN или конкретный accessory profile, но не разрешает ослабить
  default-off/STOP/reverse-blocking contract.

