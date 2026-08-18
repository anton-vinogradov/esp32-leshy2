# REV-0005BB — Si4732 SOIC-16 pin-map correction

- Статус: **Проведено ревью**
- Finding: [`FND-0102`](../findings/FND-0102-si4732-soic16-contact-map-was-shifted.md)
- Corrected endpoint: [`RXF-0001`](../architecture/RXF-0001-exact-si4732-dual-input-receive-frontend.md)

## Проверка

| Check | Result |
|---|---|
| primary visual source | pass: official Si4732-A10 SOIC-16 top-view package drawing inspected directly, not inferred from PDF extraction order |
| full package map | pass: all 16 contact identities match the manufacturer drawing and are regression-locked |
| RF ownership | pass: physical `FMI=6`, `RFGND=7`, `AMI=8`; exact block diagram independently retains `FM/SW → FMI`, `AM/LW → AMI` |
| control and clock | pass: `RST=9`, `SENB=10`, `SCLK=11`, `SDIO=12`, `RCLK=13` |
| power and audio | pass: `VDD=14`, `GND=15`, `ROUT/DOUT=16`, `LOUT/DFS=1` |
| route propagation | pass: symbolic machine routes remain valid and now resolve to correct physical contacts; generated diagram/ledger and paired firmware prose are corrected |
| pre-existing implementation cross-check | pass: legacy `hardware/tscircuit/audio.tsx` independently documents the same physical map |
| physical fallout | pass: no KiCad authorization, PCB or released BOM existed; correction occurs before atomic-architecture acceptance |

## Result

The exact Si4732-A10 SOIC-16 contact map receives **«Проведено ревью»**. The
earlier shifted map is not valid evidence and is superseded everywhere by the
manufacturer-drawing map. RF performance, exact received-lot identity and HIL
remain open exactly as stated by `DEC-0096`; the correction does not consume a
GPIO, add cost or change product functionality.

