# REV-0003Z — display/touch/storage real-device evidence review

- Статус: **Проведено ревью фактов; performance принят позднее `DEC-0043`**
- Дата: 2026-08-17
- Artifact: [`DSP-0001`](../architecture/DSP-0001-display-storage-real-device-evidence.md)
- Finding: [`FND-0051`](../findings/FND-0051-legacy-display-interface-and-throughput.md)
- Later decision: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)

## Проверено

| Проверка | Результат |
|---|---|
| exact devices, not generic controller families | Waveshare 29318, Elecrow DLS31040B1, Riverdi RVT35HITNWC00-B and Hirose DM3AT-SF-PEJM5 identified |
| actual exposed contacts | внесены все host/module/socket contacts и alternate connector numbering where applicable |
| old 24-pin connector matches a candidate | нет; это найденное и локализованное несоответствие |
| ST7796S can satisfy old 4.5 MB/s gate | нет; datasheet ceiling 1.89 MB/s before overhead |
| onboard display TF equals independent SDMMC | нет; он делит SPI with display |
| target performance accepted | позднее да, task-based contract в `DEC-0043` |
| target display accepted | нет; exact MPN/optics/mechanics/HIL открыты |
| target storage socket/width accepted | нет; interface HIL and physical design remain downstream |

Фактический scope получает статус **«Проведено ревью»**. Ни один exact display
не получает target/Q status, а обе draft owner/pin maps остаются provisional.
