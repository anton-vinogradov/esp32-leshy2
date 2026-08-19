# DEC-0046 — unused interfaces are quiet by default

- Статус: **Принято; exact controls/HIL открыты**
- Дата: 2026-08-17
- Основание: явное решение владельца «для отсутствия помех все остальные
  интерфейсы должны отключаться при неиспользовании»
- Architecture: [`QST-0001`](../architecture/QST-0001-unused-interface-quiet-states.md)
- Group policy: [`DEC-0045`](DEC-0045-one-active-signal-group.md)

## Решение

1. Reset/boot/fault/STOP и состояние `active_signal_group=NONE` запускаются с
   запрещёнными аппаратными TX paths и выключенными external/peripheral rails.
2. Не входящий в активную группу signal interface переводится в максимально
   сильное доступное тихое состояние, а не оставляется background-idle:
   hardware TX inhibit; native sleep/power-down; load-switch off для отдельного
   тракта; controller clock/DMA/periodic polling off; output parking; interrupt
   masking/clearing; отсутствие фоновых scans, advertising, beacons и logs.
3. Для `SG-N24` все три nRF считаются используемыми. Поэтому общий nRF rail
   включён и ни один из трёх не power-down только потому, что сосед перешёл в
   `PTX`; роли меняются независимо.
4. Всегда живые system planes не объявляются «выключенными»: S3 CPU/UI, RP
   arbiter, power/fault supervisor и нужный IPC продолжают работу. Их clocks
   включаются только на ограниченную транзакцию, а остаточная EMI проверяется
   измерением против изолированной sensitivity активного тракта.
5. Программная команда off не является доказательством. Где возможно, state
   machine сверяет rail-good/current, actual-TX detectors, accessory-present и
   endpoint status; неизвестное состояние блокирует переход к активной группе.
6. Firmware не вправе тайно оживлять интерфейс для telemetry, discovery,
   update-check или удобства. Такая операция сначала становится видимым member
   manifest текущей группы либо выполняется после явного group switch.

## Обязательная последовательность отключения

`revoke → TX inhibit → actual-TX-off → controller stop → endpoint sleep/reset →
safe pre-off levels → I/O isolate/high-Z → rail off → discharge → status verify`.

При включении I/O сначала остаются изолированными: rail on → exact settling →
safe pin levels (`CE=low`, chip-select deasserted) → I/O connect → self-test.
TX arm отдельно и автоматически не восстанавливается.

## Граница обещания

«Quiet/off» означает проверенное отсутствие преднамеренной активности и
ограниченную измеренную деградацию active receiver. Это не обещание нулевого
электромагнитного излучения: работающие MCU, DC/DC, display и memory физически
излучают. Поэтому exact layout получает pass только по conducted/OTA EMI HIL,
а не по наличию слова `sleep` в driver.
