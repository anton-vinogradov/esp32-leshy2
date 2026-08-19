# REV-0005BI — display procurement boundary propagation

Статус: **проведено ревью sourcing strategy; external RFQ/specimen HIL открыт**.

| Проверка | Результат |
|---|---|
| exact current assembly | unchanged: `HMX035CTFT-001` with integrated `ST77922` |
| prototype availability | pass: two orderable complete-board sources expose the exact installed assembly through official schematic identity |
| production orderability | open: standalone raw-panel order page/quote and approval drawing absent |
| cost honesty | pass: complete-board retail/tier prices are not recorded as raw-panel COGS |
| alternate screen | pass: OPL/Waveshare/Leadtek remain requalification leads, not drop-in substitutes |
| machine policy | pass: explicit `no_drop_in_substitute` and exact RFQ evidence list added |
| functionality/pins | unchanged: QSPI D0…D3, touch I2C/IRQ/reset, backlight, GPIO and product display class remain fixed |
| diagram | unchanged correctly: no physical target component was added or replaced |
| regression | pass: generated-artifact check and 65 hardware architecture tests |

## Verdict

The panel can be obtained for prototype measurement without inventing a raw
MPN. Production sourcing still needs supplier response and samples. This is a
reviewed procurement plan, not final panel acceptance or KiCad authorization.
