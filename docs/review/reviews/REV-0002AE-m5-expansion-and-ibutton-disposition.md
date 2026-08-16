# REV-0002AE — M5 ecosystem audit and iButton disposition

- Статус: **Проведено ревью фактов и W-EXTRA-11; platform proposal открыт**
- Дата: 2026-08-16
- Inputs: `AUD-0004/W-EXTRA-11`, `AUD-0005`, `IMP-0027`, owner response
- Outputs: `DEC-0033`, `REQ-IBTN-0001`, `FND-0042`, `IMP-0028`

## Checks

| Check | Result |
|---|---|
| iButton silently added to base mechanics | no; passive external adapter only |
| nonexistent official M5 iButton/LF Unit claimed | no |
| RFID2/UHF confused with LF 125 kHz | no |
| Unit, Cap and M5-Bus treated as one connector | no |
| 90% calculated by padding with irrelevant sensors | no; 18 Leshy2 external hardware classes are the denominator |
| M5-only reaches 90% product-result coverage | no; 33.3% full, 44.4% with partial, 50% with custom iButton |
| viable improvement found | yes; M5-first plus separate high-speed tier, `IMP-0028` |
| exact ports/pins/power selected before G3/G4 | no |
| accepted existing U214/GPS/U216 profiles lost | no |
| safety/update/recovery boundaries applied to active accessories | yes at requirement level |

## Result

`W-EXTRA-11` and its capability contract receive **«Проведено ревью»** through
`DEC-0033/REQ-IBTN-0001`. This does not close all of G2: `W-EXTRA-12..17`
remain open. `AUD-0005` facts are reviewed, while `IMP-0028` requires one owner
decision before M5 becomes the primary general expansion strategy.
