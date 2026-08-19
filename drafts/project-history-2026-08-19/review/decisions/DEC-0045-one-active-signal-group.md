# DEC-0045 — one active signal group

- Статус: **Принято**
- Дата: 2026-08-17
- Основание: явные решения владельца «одновременно работаем только с одной
  группой сигналов» и «nRF должен работать одновременно и на полный приём, и
  на передачу, и микс»
- Finding: [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
- Реализация: [`IMP-0038`](../improvements/IMP-0038-visible-qualified-rf-arbiter.md), вариант A-GROUP
- Architecture: [`RFQ-0002`](../architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md)

## Решение

1. В runtime существует ровно один `active_signal_group`; после boot, reset,
   update, fault или STOP активна группа `NONE`, все TX disarmed/off.
2. Две независимые signal groups физически одновременно не работают. Это
   относится и к скрытым background Wi-Fi/BLE scans/advertising: они либо
   входят в manifest текущей группы, либо остановлены.
3. UI, local controls, hard STOP/dead-man, bounded event transport, storage,
   power/fault monitoring и service diagnostics являются системными planes,
   а не signal groups. Они продолжают работать, но проходят digital-aggression
   EMI HIL и не получают права RF TX.
4. Внутригрупповая параллельность объявляется явно и не переносится на другую
   группу по аналогии. `SG-N24` — одно атомарное исключение из простого правила
   «один radio»: все три nRF одновременно включены, каждый независимо выбирает
   `PRX` или `PTX`, и runtime обязан поддержать любое сочетание ролей, включая
   `3×PRX`, `1×PTX+2×PRX`, `2×PTX+1×PRX` и `3×PTX`. Передача одного nRF сама по
   себе не переводит два соседних nRF в standby и не создаёт скрытых RX gaps.
5. Это решение фиксирует функциональную и цифровую concurrency, но не объявляет
   доказанной сохранность изолированной weak-signal sensitivity при локальной
   передаче на той же/соседней частоте. Физический критерий и exact RF profile
   остаются открыты в [`FND-0054`](../findings/FND-0054-three-nrf-mix-needs-rf-acceptance.md)
   и [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md).
6. GNSS, audio capture или другой support member может работать внутри группы
   только если указан в её versioned manifest и прошёл совместный HIL. Так
   wardrive/geotagging не теряются, но GNSS не становится неучтённой второй
   foreground group.
7. Переключение группы атомарно: revoke leases → запретить новый TX → дождаться
   actual-TX-off/timeout → остановить RX и закрыть records как complete/incomplete
   → перевести старую группу в standby/power-off → настроить/self-test новую →
   показать identity/band/antenna/gaps → отдельно arm TX при необходимости.
8. Failure, timeout, unknown actual-TX evidence, wrong/missing accessory или
   неподтверждённый antenna profile оставляет `NONE`; rollback к предыдущей
   armed/TX группе запрещён.
9. Неактивные signal interfaces обязаны перейти в проверяемое тихое состояние
   по [`DEC-0046`](DEC-0046-unused-interface-quiet-by-default.md): TX hardware-off,
   frontend power-down/load-switch там, где тракт допускает, остановленные
   clocks/DMA и статически припаркованные выводы.

## Начальный каталог групп

| Group | Активные signal members | Внутренняя concurrency |
|---|---|---|
| `SG-N24` | nRF0+nRF1+nRF2 | all three active; independent `PRX`/`PTX`; every simultaneous mix is required, with common time and independent state/loss/age |
| `SG-S3-24` | S3 Wi-Fi/BLE/ESP-NOW | одна native chain, vendor TDM visible |
| `SG-C5-NATIVE` | C5 Wi-Fi 2.4/5 + 802.15.4 | одна 1T1R chain, vendor TDM visible |
| `SG-CC` | CC1101 | RX либо controlled TX по exact profile |
| `SG-VOICE` | SA518/qualified fallback | half-duplex RX либо TX; RX↔TX mutually exclusive |
| `SG-BROADCAST` | Si473x + audio/decode support | receive-only |
| `SG-U214` | exact U214 LoRa plus declared GNSS support | LoRa/GNSS pair qualified inside one accessory manifest |
| `SG-IR` | dual RX learner либо TX phase | optical learn and replay are separate phases |
| `SG-EXT-*` | one exact M5/other signal accessory profile | only manifest-declared members; no blanket connector capability |

NFC/iButton получают собственные `SG-EXT-*` profiles. Новый signal backend не
расширяет существующую группу молча: он добавляет manifest, pair/HIL matrix и
safe transition tests.

## Последствия

- `G2F-3I` сохраняет независимые buses/IRQ/DMA, поэтому выбранная группа не
  тормозит из-за digital neighbour и быстро переключается;
- `SG-N24` нельзя реализовать как один передатчик с двумя автоматически
  заглушёнными соседями или как незаметное пакетное time-sharing;
- base BOM не обязан обеспечивать невозможную arbitrary same-band isolation
  между разными signal groups; точная цена full-mix isolation внутри `SG-N24`
  остаётся открыта до решения `IMP-0039`;
- filters, zoning, shields, clean power и measurement points всё равно нужны
  для isolated sensitivity, harmonics, EMI и compliance;
- UI/log всегда показывает selected group, active members, transition state,
  stale/gap/loss и отдельный TX armed/actual state.
