# REV-0005G — U214 physical-envelope fact review

- Статус: **Проведено ревью фактов; placement decision открыт**
- Дата: 2026-08-17
- Finding: [`FND-0068`](../findings/FND-0068-u214-envelope-missing-from-legacy-layout.md)
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)

## Проверенный результат

| Gate | Результат |
|---|---|
| exact product | pass: M5Stack `U214 Cap LoRa-1262` |
| published body | pass: `84.0 × 24.0 × 15.2 mm` |
| official structure | pass: official STL exists; body axes confirm 84 × 24 mm shell components |
| interface | pass: direct 14-pin Cap-Bus carries LoRa SPI/control, GNSS UART, I2C and power |
| accessory RF | pass: own RP-SMA LoRa antenna and internal GNSS ceramic antenna; downstream HY2.0-4P exists |
| legacy render | fail as target: no U214 body/dock/cable/sky-view envelope is drawn |
| placement | open: bottom 75-mm overhang, 84-mm chassis or top/SMA rearrangement require owner choice |

## Boundary

Проведено ревью только фактов и обнаруженного omission. До решения placement
active SVG не должен обещать одновременно conflict-free U214 и прежние
top-edge SMA banks.

