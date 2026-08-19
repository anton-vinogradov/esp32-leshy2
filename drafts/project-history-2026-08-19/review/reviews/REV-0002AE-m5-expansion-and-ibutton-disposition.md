# REV-0002AE — M5 ecosystem audit and iButton disposition

- Статус: **Проведено ревью фактов и W-EXTRA-11; platform later closed by `DEC-0034`**
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
| M5-only reaches 90% product-result coverage | no; at this review point `FND-0044` gave 27.8% full/44.4% partial/50% with custom iButton; later `DEC-0036/FND-0045/DEC-0038/DEC-0039` give current 20.0%/40.0%/46.7% over 15 live classes |
| viable improvement found | yes; M5-first plus separate high-speed tier, `IMP-0028` |
| exact ports/pins/power selected before G3/G4 | no |
| accepted existing U214/GPS/U216 profiles lost | no |
| safety/update/recovery boundaries applied to active accessories | yes at requirement level |

## Result

`W-EXTRA-11` and its capability contract receive **«Проведено ревью»** through
`DEC-0033/REQ-IBTN-0001`. This does not close all of G2: `W-EXTRA-12..17`
remain open. `AUD-0005` facts were reviewed here; the subsequent owner decision
is recorded by `DEC-0034/REV-0002AF`.
