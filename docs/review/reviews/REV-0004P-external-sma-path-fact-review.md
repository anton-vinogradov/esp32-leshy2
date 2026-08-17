# REV-0004P — external-SMA path fact review

- Статус: **Проведено ревью фактов; решение IMP-0041 открыто**
- Дата: 2026-08-17
- Evidence: [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
- Finding: [`FND-0055`](../findings/FND-0055-si4732-two-antenna-input-domains.md)
- Proposal: [`IMP-0041`](../improvements/IMP-0041-exact-external-sma-count.md)

## Проверенная матрица

| Проверка | Результат |
|---|---|
| Owner clarification | все base-device antenna endpoints external SMA; external M5 owns its antennas |
| Legacy geometry | 9 slots реально нарисованы; onboard LoRa removal освобождает один |
| S3/C5 | по одному module antenna path; C5 standard `-1U` использует `ANT1`, не `ANT2` |
| nRF | три separate IPEX→SMA закреплены `DEC-0048` |
| SA518 | exact rev 1.1 выводит один physical `ANT` pin 7 для 50-ohm antenna |
| SA518 non-RF pins | exact check also found no dedicated `SQ` and an ambiguous `UPDATE` direction; `FND-0056` corrects the paper maps without pretending `Audio_ON` is proven squelch |
| Si4732 | exact SOIC16 выводит `FMI` pin 1 и `AMI` pin 3 для разных band/antenna domains |
| AMI cable caveat | manufacturer guidance требует учитывать total input capacitance; generic long coax не принят |
| CC1101 | разные band-specific TI matching networks подтверждены; legacy generic balun/SP4T proxy не production proof |
| Endpoint count | 9 при separate Si inputs; 8 только с дополнительно квалифицируемым shared port |
| Accessories | U214/GNSS/NFC antennas не входят в base bank; IR/iButton не RF SMA |

## Результат

Fact-review scope получает **«Проведено ревью»**. Старый один `Si4732` SMA
зафиксирован как `FND-0055`, active RF model исправлена без изменения legacy
draft. Exact count не получает review/decision status до ответа владельца на
`IMP-0041`.
