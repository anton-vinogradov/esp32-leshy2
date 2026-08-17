# REV-0005L — full-service 1-bit SDIO propagation

- Статус: **Проведено ревью; `INT-0001/I1` закрыт на paper level**
- Дата: 2026-08-17
- Decision: [`DEC-0059`](../decisions/DEC-0059-full-service-over-1bit-sdio.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверено

| Проверка | Результат |
|---|---|
| S3↔C5 pin reciprocity | pass: четыре 1-bit SDIO contacts с парными peers |
| C5 USB/UART coexistence | pass: USB GPIO13/14 и UART0 GPIO11/12 независимы |
| S3 USB/UART coexistence | pass: USB GPIO19/20 и UART0 GPIO43/44 независимы |
| RP service | pass: USB/SWD/RUN/USB_BOOT не затронуты |
| M5 Unit после UART0 reservation | исправлено: UART accessory profile использует UART1 на прежних GPIO7/8 |
| pin accounting | pass: S3 `32/3/1`, C5 `14/6/1`, RP `48/0/0`, slow `24/0/0` |
| no-neighbour-stall | pass on paper: C5 retains dedicated SD/MMC/SDIO controller |
| performance boundary | arithmetic closes; framed throughput/reset/RF-load remain named HIL |
| diagrams/docs/FW input | updated in the same decision propagation |

## Tests

- generator structural validation — pass;
- `python3 -m unittest discover -s hardware/architecture/tests -v` —
  **40/40 pass** before documentation-only propagation;
- regression now checks exact 1-bit contacts, both USB/UART service sets,
  Unit UART1 remap, fallback wording and generated diagram label.

## Review boundary

`I1` closes the compute/link/service topology and pin budget. Exact USB/debug
connector circuits, BOM availability and mechanical access remain explicit
`I7/I8` work; executable link qualification remains HIL. `I2` is next.
