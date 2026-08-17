# FND-0061 — display quantum retained after U214 left the shared SPI

- Статус: **Открыто; несоответствие найдено, изменение контракта требует решения**
- Серьёзность: performance/architecture consistency
- Обнаружено: 2026-08-17
- Historical decision: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)
- Current map: [`NIF-0001`](../architecture/NIF-0001-digital-noninterference-layout.md)
- Evidence: [`DSP-0002`](../architecture/DSP-0002-fast-display-path-options.md)

## Находка

`DEC-0043` ограничил непрерываемую display transaction значением `256 B`,
потому что в рассматривавшейся тогда карте экран и U214 делили SPI, а U214
требовал начать transfer после IRQ не позднее `250 us`. При гарантированном
пределе ST7796S около `1.89 MB/s` более длинный экранный transfer действительно
нарушал бы этот deadline.

В текущей ведущей карте `G2F-3I` U214 уже принадлежит RP2354B и обслуживается
отдельным `PIO1 SM0`, собственными data/control pins, DMA и IRQ. На S3 SPI2
остались только display и microSD. Поэтому прежний U214 deadline больше не
обосновывает фиксированный лимит `256 B`, но этот лимит всё ещё записан в:

- `NIF-0001` и resource contract `DISPLAY_SD_SPI` в `G2F-3I.json`;
- hardware/firmware current-state documents;
- firmware runtime input `ARC-0002`.

Результат безопасен для radio deadlines, но искусственно увеличивает число
display transactions, CS/command/DMA setup overhead и мешает целиком передать
даже одну строку waterfall `320×RGB565 = 640 B`.

## Требуемое исправление

Фиксированное число байтов должно быть заменено измеримым **временным** пределом
непрерываемого владения SPI2. Предлагаемый baseline — `<=1 ms` на одну display
transaction, а фактический byte quantum вычисляется из измеренной валидной
скорости выбранной панели и ограничений её протокола. Приоритет critical UI,
bounded SD operations, card-stall injection и запрет влияния на radio/IPC
сохраняются.

Это не изменяется автоматически: новый предел меняет принятый arbitration
contract и должен быть утверждён вместе с выбором fast-display направления из
`IMP-0044`.

## Критерий закрытия

После решения владельца согласованно обновлены `DEC-0043`-successor,
machine-readable resource contract, generated ledgers, hardware/firmware
runtime documents и HIL plan. Проверка подтверждает целевую UI latency,
storage throughput/stalls и отсутствие влияния на radio/IPC.
