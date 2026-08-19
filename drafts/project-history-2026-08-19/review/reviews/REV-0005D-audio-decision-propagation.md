# REV-0005D — DEC-0054 audio-decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Decision: [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md)
- Proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)
- Machine candidate: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверенный результат

| Gate | Результат |
|---|---|
| owner choice | pass: вариант A принят целиком, а не отдельными удобными фрагментами |
| exact devices | pass: ES8311, SN74LVC1G3157, TLV9061, TMUX1136, TS5A63157, SN74LVC2G08 и PAM8302A имеют exact package contacts в `devices.json` |
| control ownership | pass: direct S3 GPIO6 = `AUDIO_ARM`; P11/P12 = requests; P27 = RX-source select |
| reset default | pass at architecture level: pull-down arm and dual AND force analog speaker/electret defaults independently of stale expander output |
| pin accounting | pass: S3 `32/3/1`, C5 `14/6/1`, RP `48/0/0`, slow plane `24/0/0` |
| PTT independence | pass: audio selector has no route to PTT assertion |
| diagram identity | pass: every shown physical device is a separate node with part number and role; open parts say `MPN TBD`; mixed `display + microSD` / `codec + receiver` nodes are regression-forbidden |
| generated artifacts | pass: regenerated from the validated JSON source |
| schematic/electrical proof | open by design: passive values, rails, loading, common mode, pop/click, RF and HIL are explicit gates |

## Self-review corrections

1. The old navigation diagrams combined two physical devices in one square and
   used generic labels. They now separate `HMX035CTFT-001` from
   `DM3AT-SF-PEJM5`, and `ES8311` from `Si4732-A10-GSR`, while stating each role.
2. The former `31/3/2` S3 snapshot was superseded at this review by the
   accepted GPIO6 allocation and point-in-time `32/3/1`. Historical review
   snapshots remain historical; current product pages and generated artifacts
   publish `33/3/0` after the direct encoder allocation.
3. The earlier abstract codec output, RX selector and amplifier endpoints are
   replaced by exact instantiated IC contacts. Passive networks remain openly
   abstract because their values have not yet passed schematic/HIL review.

## Boundary

This review closes decision propagation and the paper pin/resource model. It
does not close the analog schematic or authorize PCB layout. The next audio
gate is calculated schematic plus specimen/HIL evidence listed in `DEC-0054`.
