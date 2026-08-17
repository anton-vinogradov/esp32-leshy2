# REV-0004W — fast-display path fact and option review

- Статус: **Проведено ревью фактов; IMP-0044 и exact panel открыты**
- Дата: 2026-08-17
- Evidence: [`DSP-0002`](../architecture/DSP-0002-fast-display-path-options.md)
- Finding: [`FND-0061`](../findings/FND-0061-stale-display-quantum-after-u214-move.md)
- Proposal: [`IMP-0044`](../improvements/IMP-0044-qspi-first-fast-display-path.md)

## Проверено

| Проверка | Результат |
|---|---|
| only remaining deliberately shared high-rate pair | pass: display+microSD on S3 SPI2; radio and IPC paths are dedicated |
| fixed `256 B` quantum still follows current U214 topology | fail/finding: U214 moved to dedicated RP PIO SPI, so old rationale is stale |
| existing RP/C5 can own display without remap | no: RP has 0 and C5 has 1 free direct GPIO |
| exact S3 module exposes enough free pins for QSPI | pass: GPIO6/41/42/43 are free; D2/D3 need two |
| direct QSPI is an official S3 LCD mode | pass: SPI/Quad/Octal LCD plus DMA are documented by Espressif |
| current exact panel already proves QSPI | no: ST7796S SPI references do not; exact QSPI module remains a gate |
| real 320×480 QSPI ecosystem exists | pass as prototype evidence: Waveshare AXS15231B reference exposes four data lines |
| I80/RGB fit current map | no: minimum data-line counts exceed four free S3 GPIO |
| display coprocessor alternative is real | pass: BT817/BT818 QSPI host/RGB engine and exact Riverdi module reviewed |
| fourth MCU is required by current UI workload | no evidence: menu/waterfall dirty regions should test direct path first |
| cost-without-loss rule applied | pass: A0/A1 test before extra controller/MCU BOM |

## Результат

Фактическая часть получает **«Проведено ревью»**. Решение не принято: current
machine map и `256 B` contract не меняются до ответа владельца по `IMP-0044`.
Exact panel, shared-line electrical behavior, optics/mechanics and scenario HIL
остаются qualification gates независимо от выбранного пути.
