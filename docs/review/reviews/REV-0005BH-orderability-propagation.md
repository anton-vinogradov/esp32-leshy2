# REV-0005BH — current orderability and exact-RP propagation

Статус: **проведено ревью; display sourcing/cost/alternates remain open**.

> `FND-0112/BOM-0011/REV-0005BJ` subsequently exclude the assembly-internal
> ST77922 purchasing duplicate. Counts below are the reviewed pre-correction
> snapshot; current purchase coverage is 857 placements / 187 lines / 186
> source records.

| Проверка | Результат |
|---|---|
| audit input | pass: all 33 previously missing used-line sources inspected |
| exact identity | fixed: pseudo-MPN replaced by `SC1512-A4`; silicon identity remains `RP2354B0A4` |
| sourced lines | pass: 32/33 receive dated exact-line evidence with evidence type stated |
| unresolved line | explicit: only `HMX035CTFT-001` lacks standalone orderability/drawing/lifecycle proof |
| machine source | pass: `devices.json` carries 187/188 orderability records |
| generated BOM | pass: review and CSV reproduce 858 placements, 188 lines and 187/188 coverage |
| current diagrams | pass: target landing and generated principle views show `SC1512-A4 (RP2354B0A4)` identity |
| firmware contract | pass: runtime owner name follows exact current hardware identity; no behavior changes |
| physical gaps | pass: SMA, RF-cable, M5-connector and antenna-kit families remain separate downstream gates |
| cost/AVL | open: all quantity-100 costs and alternate dispositions remain I8 work |
| regression | pass: generated-artifact check and 65 hardware architecture tests |

## Verdict

`FND-0111/BOM-0009/DEC-0102` close the batch review without claiming that every
line is currently stocked or quoted. The exact controller correction is
nonfunctional and accepted under delegated component-maintenance authority.
Display sourcing is the sole remaining used-line source gap; the complete I8
stage is not yet reviewed.
