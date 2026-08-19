# REV-0004S — antenna connector ecosystem fact review

- Статус: **Проведено ревью фактов; вариант B принят `DEC-0050`**
- Дата: 2026-08-17
- Evidence: [`RFH-0002`](../architecture/RFH-0002-antenna-connector-ecosystem-review.md)
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md)
- Decision: [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)

## Проверено

| Проверка | Результат |
|---|---|
| Native Wi-Fi ecosystem | RP-SMA типичен для routers/access points, но current manufacturer catalog имеет и standard SMA variants |
| nRF/Ebyte ecosystem | official E01 family/antenna guide использует standard `SMA-K`/`SMA-J`; перенос всех 2.4 GHz ports на RP-SMA не обоснован |
| Sub-GHz ecosystem | 433/868/915 MHz antenna families доступны в обеих polarities; уникального market default нет |
| Voice/receiver paths | connector popularity не заменяет exact antenna/pod qualification |
| Mechanical coding | standard/RP меняют centre contact, но не дают безопасного band keying; labels/profile/TX interlock обязательны |
| Certification bound | popular router antenna может превышать recommended Espressif gain и потребовать additional testing |

## Результат

Fact scope получает **«Проведено ревью»**. Ограниченный mixed candidate
`2 RP-SMA + 7 standard SMA` принят в `DEC-0050`; exact two-source antenna
shortlist остаётся открытым.
