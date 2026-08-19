# REV-0002AK — IMU instrument-value prerequisite review

- Статус: **Проведено ревью фактов; product disposition later closed `DEC-0037`**
- Дата: 2026-08-16
- Input: `W-EXTRA-14`, `AUD-0004/0005`, M5/Bosch/NXP primary sources
- Outputs: `AUD-0008`, `FND-0045`, `IMP-0031`

## Проверка

| Проверка | Результат |
|---|---|
| Concrete receiver/analyzer result exists | yes; pose/motion provenance for measurement windows |
| Consumer-only gesture/fall/tamper scope added | no |
| Current M5 exact SKU/lifecycle checked | U095 current/in-stock; U171 EOL |
| External sensor frame treated as device frame | no; indexed mount/transform required |
| 6-axis represented as absolute heading | no |
| IMU represented as RF bearing/RSSI/distance | no |
| Integrated/external/no-IMU compared | yes |
| Base BOM increased before decision | no |
| M5 coverage correction propagated | yes |
| Target README changed before decision | no |

## Result

Fact/prerequisite slice receives **«Проведено ревью»**. `W-EXTRA-14` remained
`needs-owner` through `IMP-0031` at this review point. The later owner decision
`DEC-0037`, propagated by `REV-0002AL`, accepts recommendation A: truthful
measurement-pose metadata through a qualified external, rigidly indexed Unit,
without increasing base sensor BOM.
