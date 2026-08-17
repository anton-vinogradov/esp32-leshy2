# REV-0005G — U214 physical-envelope fact review

- Статус: **Проведено ревью фактов; placement закрыт `DEC-0057`**
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
| installed geometry | pass for paper model: official aligned STL components show an L-shaped edge wrap, `15.281 mm` rear strip and about `15.11 mm` protrusion beyond the host rear datum |
| rear candidate | pass for scaled paper fit: `4.5 mm` side overhang, `5.5 mm` SMA-plan clearance, `9.719 mm` battery-plan clearance and `3.49 mm` bare-cell depth reserve (`PHY-0001`) |
| placement | pass: rear-above-battery D accepted in `DEC-0057`; exact dock/specimen and installed-cap HIL remain required |

## Boundary

Проведено ревью фактов, STL-derived paper geometry и scaled rear fit. Вариант D
закреплён `DEC-0057`, поэтому active SVG показывает его как принятую компоновку,
но сохраняет явную коллизию legacy encoder и открытые
dock/header/boss/wall/hand/GNSS/RF gates до specimen/HIL-проверки.
