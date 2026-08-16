# REV-0002AG — U2F/FIDO prerequisite review

- Статус: **Проведено ревью фактов; product disposition открыт**
- Дата: 2026-08-16
- Input: `W-EXTRA-12`, `AUD-0004`, FIDO/W3C/manufacturer/project sources
- Outputs: `AUD-0006`, `FND-0043`, `IMP-0029`

## Проверка

| Проверка | Результат |
|---|---|
| Current published implementation baseline found | CTAP 2.3 Proposed Standard; 2.3.1 remains Working Draft |
| U2F presented as modern full target | no; compatibility only |
| WebAuthn and CTAP roles separated | yes |
| USB HID feasibility confused with security proof | no |
| Main/Lab/Controlled-Zone coexistence risk handled | exclusive Main Authenticator Mode proposed |
| User presence distinct from PIN | yes |
| Backup/restore truth defined | single-device secrets excluded from general backup |
| Openness mistaken for certification/tamper resistance | no |
| Hardware-backed/certified path silently forced | no; explicit option B |
| Target README changed before decision | no |

## Result

Prerequisite/fact slice receives **«Проведено ревью»**. `W-EXTRA-12` remains
`needs-owner` through `IMP-0029`; no FIDO capability is yet accepted into the
target product. After owner disposition, the chosen scope is propagated into a
normative requirement or explicit deferral.
