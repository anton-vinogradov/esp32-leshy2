# FND-0052 — draft maps do not close slow control or S3 UART fallback

- Статус: **Исправлено в `G2F-3I`; production parts/HIL открыты**
- Дата: 2026-08-17
- Обнаружено: G2F slow-control/peripheral pass
- Evidence: [`CTL-0001`](../architecture/CTL-0001-slow-control-and-external-i2c-boundary.md)
- Proposal: [`IMP-0037`](../improvements/IMP-0037-slow-control-and-external-i2c-isolation.md)
- Correction: [`DEC-0044/NIF-0001`](../architecture/NIF-0001-digital-noninterference-layout.md)

## Несоответствие 1 — validator scope был шире описан, чем доказан

Обе draft-карты содержат один `TCA9535PWR`, но назначают лишь 5 из 16 портов
в `G2F-2R` и 3 из 16 в `G2F-3D`. Ordinary UI, audio selectors, status inputs и
accessory fault boundary перечислялись только текстовым gap. Generator при
этом валидировал полный учёт programmable MCU contacts, а не всех expander
ports и semantic slow endpoints.

Поэтому формулировка «карта сошлась» могла ошибочно читаться как whole-device
closure. Исправленная формулировка: **MCU contact/collision/accounting checks
pass; slow-control completeness does not**.

## Несоответствие 2 — external U214 I²C смешана с internal bus

В обоих черновиках `SYS_I2C` напрямую объединял U214, slow expander,
touch/codec/receiver. Реальный U214 выводит те же SDA/SCL и на onboard antenna
switch, и на downstream Port A. Внешний stuck-low fault поэтому мог погасить
всю внутреннюю control plane. Exact isolator ещё не выбран, но отсутствие
fault boundary теперь является явным blocker.

## Несоответствие 3 — S3 UART0 recovery был обещан без active route

Active G2F allocations занимают GPIO43/44 функциями U214. Native USB +
physical EN/BOOT присутствуют и достаточны как ROM recovery baseline, но
UART0 fixture route/isolation в active source отсутствует. Service строки и
reservation text исправлены: UART0 остаётся optional later proof, не
подтверждённым свойством текущих карт.

## Выполненное исправление

- machine capability GPIO7/8 расширена до mutually exclusive
  `I2C1_OR_UART0_OR_GPIO` на основании второго hardware I²C controller S3;
- в `devices.json` добавлены complete package-contact references
  `TCA6424ARGJR` и `TCA4307DGKR`;
- обе candidate gap-list явно отделяют MCU accounting от slow-plane closure и
  снимают недоказанное обещание UART0 fallback;
- `SRC-0002`, recovery prerequisite/review и current-state получают ту же
  границу;
- proposal topology не превращалась в решение до ответа владельца.

## Закрытие в G2F-3I

`DEC-0044` принял `IMP-0037/A`. Validator теперь проверяет все allocatable
contacts non-MCU expander, а `G2F-3I` маршрутизирует 23/24 порта и резервирует
`P27`. U214 I²C отделён TCA4307, U214 IRQ/RST/BUSY и все radio IRQ остаются
прямыми. C5 recovery выбирает доказанную альтернативу UART0+EN/BOOT/strap,
поскольку GPIO13/14 заняты 4-bit SDIO.
