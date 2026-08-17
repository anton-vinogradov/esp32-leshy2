# ⚠️ Предложение IMP-0044 — QSPI-first fast display path without a fourth MCU

- Статус: **Открыто — требуется решение владельца**
- Дата: 2026-08-17
- Evidence: [`DSP-0002`](../architecture/DSP-0002-fast-display-path-options.md)
- Finding: [`FND-0061`](../findings/FND-0061-stale-display-quantum-after-u214-move.md)
- Current decision: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)

## Текущее состояние и причина решения

Display+microSD — единственная high-rate пара, которая ещё намеренно делит
controller. Radio и IPC уже изолированы. Current 1-bit ST7796S-like path
арифметически достаточен для dirty menu/waterfall, но имеет низкий full-redraw
ceiling и дополнительно режется устаревшим `256 B` quantum, созданным ради
U214, который теперь находится на dedicated RP bus.

У S3 есть четыре реальные свободные линии. Это позволяет получить быстрый
4-bit QSPI display без нового вычислителя, сохранив microSD на том же SPI2 с
отдельным CS. Нужно решить направление сейчас, потому что два QSPI data pins и
возможный TE входят в принципиальную распиновку и physical display shortlist.

## Вариант A — QSPI-first, без нового compute

1. Сразу заменить fixed `256 B` на измеримый `<=1 ms` non-preemptible display
   time budget; byte quantum выводить из подтверждённой скорости exact panel.
2. В working pin candidate зарезервировать `GPIO41/42` под LCD D2/D3; D0/D1
   переиспользуют `GPIO36/4`, SCK/CS — `GPIO35/38`.
3. `GPIO43` использовать как optional TE только если exact module выводит TE и
   HIL показывает измеримую пользу; `GPIO6` оставить direct reserve.
4. Искать exact QSPI panel/module в принятом display/optical/mechanical
   envelope; не объявлять Waveshare dev board production target.
5. BT817/BT818 EVE сделать формальным fallback после провала direct-QSPI HIL,
   а четвёртый MCU — только после провала обоих путей или изменения UI scope.

Последствия: S3 budget становится `31 used / 3 reserved / 2 free` после D2/D3
либо `32/3/1` с TE. Новый firmware image, update key, recovery owner и
дополнительный RF/EMI emitter не появляются. Обязательны shared-D1 tri-state,
mode switching, SD-stall, DMA/SI/EMI/power and task-latency HIL.

## Вариант B — display coprocessor BT817/BT818 EVE

S3 отправляет по QSPI display lists, widgets и изменённые bitmap data, а EVE
сам хранит graphics resources и сканирует RGB panel. Это реальный аналог
вычислительной разгрузки без четвёртого application firmware.

Последствия: больше UI headroom, но добавляются controller, flash/panel
interface, питание, площадь, стоимость и EVE-specific firmware. Dynamic
waterfall data всё равно нужно передавать. Вариант разумен как fallback либо
при принятии существенно более богатого UI, но не как первая плата.

## Вариант C — четвёртый MCU/display owner

Получает semantic UI commands по IPC и полностью владеет panel/touch.
Максимально разгружает S3, но добавляет MCU, память, питание, boot/update/
signature/recovery/diagnostics, IPC и failure coordination. Ещё один wireless
ESP также создаёт новый quiet-state/EMI объект. Для текущего menu/waterfall
workload это избыточно и дороже без доказанной потери продукта.

## Вариант D — оставить 1-bit SPI, исправить только quantum

Нулевая цена и нулевой pin cost; может уже пройти все принятые product tasks.
Но производственный display остаётся привязан к низкому full-redraw ceiling,
а два доступных GPIO не используются для дешёвого запаса скорости. Полезен как
обязательный первый HIL и cost-control reference, но не рекомендуется как
единственный target direction до сравнения с QSPI.

## Рекомендация

Принять **A** как working architecture direction: сначала измерить бесплатное
устранение stale quantum, затем квалифицировать direct QSPI на тех же S3/SPI2,
не добавляя compute. Считать EVE заранее определённым fallback, а четвёртый MCU
не вводить без измеренного провала или расширения UI scope.

## Вопрос владельцу

Принимаем вариант **A: QSPI-first на S3 с `GPIO41/42` под D2/D3, временным
display quantum `<=1 ms`, optional TE только по HIL, EVE fallback и без
четвёртого MCU в baseline**?
