# REV-0004K — slow-control and external-I²C fact review

- Статус: **Проведено ревью фактов; последующее `IMP-0037/A` принято `DEC-0044`**
- Дата: 2026-08-17
- Evidence: [`CTL-0001`](../architecture/CTL-0001-slow-control-and-external-i2c-boundary.md)
- Finding: [`FND-0052`](../findings/FND-0052-draft-maps-do-not-close-slow-control.md)
- Proposal: [`IMP-0037`](../improvements/IMP-0037-slow-control-and-external-i2c-isolation.md)

## Проверено

| Проверка | Результат |
|---|---|
| generator proves every slow semantic endpoint is placed | нет; он доказывает MCU contacts/collisions/accounting |
| current TCA9535 allocation is complete | нет; 5/16 и 3/16 ports assigned in the two drafts |
| planning envelope shown without pretending it is final | да; `19…27`, central `22…24`, compression remains provable option |
| timing-critical/safety paths silently moved to expander | нет; PTT, STOP kill, actual-TX evidence and U214 IRQ stay outside |
| polling can satisfy accepted menu contract in principle | да; bounded internal-bus polling is compatible with `≤100 ms`; shortest-button/encoder capture remains an explicit HIL gate |
| U214/Port-A external SDA/SCL can fault internal controls in current draft | да; explicit isolation blocker recorded |
| exact isolation and 24-port references use real package pins | да; `TCA4307DGKR` and `TCA6424ARGJR` contacts checked and versioned |
| TCA4307 falsely proves complete U214 hot-plug | нет; SPI/UART/power/backfeed/RF gates remain open |
| S3 second hardware I²C omitted | было; machine capability corrected |
| active map proves S3 UART0 fallback | нет; GPIO43/44 are occupied, native USB+EN/BOOT is the current baseline |

Факты, mismatch correction и source propagation получают статус
**«Проведено ревью»**. На момент этого review capacity/topology оставалась
открыта; последующее `DEC-0044/NIF-0001/REV-0004L` приняло 24-port envelope и
проверило полную machine allocation без изменения исторического результата.
