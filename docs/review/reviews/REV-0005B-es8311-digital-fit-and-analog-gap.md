# REV-0005B — ES8311 exact digital fit and analog-gap review

- Статус: **Проведено ревью digital/contact scope; topology decision открыто**
- Дата: 2026-08-17
- Artifact: [`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md)
- Finding: [`FND-0065`](../findings/FND-0065-es8311-ce-and-differential-path.md)
- Proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)

## Проверка

- Current manufacturer brief confirms `ES8311`, QFN-20, current revision and
  mono ADC+DAC boundary; the user guide supplies exact 1…20 plus EPAD contacts.
- S3 `GPIO1/2/15/16/17/18` terminate on exact `CDATA/CCLK/SCLK/LRCK/DSDIN/ASDOUT`.
- `MCLK` is explicit NC under the documented BCLK-derived-clock contract; no
  uncounted GPIO is consumed.
- `CE` is an address strap, not enable/reset. The machine map now uses
  `CODEC_PWR_EN` for an external power switch and straps `CE` to address `0x19`.
- Supply, ground, exposed-pad and reference contacts are represented; exact
  load switch, sequencing, decoupling and isolation remain blockers.
- The digital map does not change current S3 `31/3/2` budget or controller/DMA
  accounting.
- Exact `OUTP/OUTN` and `MIC1P/MIC1N` expose an analog-topology gap in old
  one-wire wording. No unreviewed selector/conditioner was silently selected.
- Regression coverage fixes contacts, directions, exact peers, CE/address,
  MCLK NC, differential endpoints and unchanged free pins.

## Итог

Exact ES8311 **digital/contact fit receives «Проведено ревью»**. It reduces
`FND-0060`, but analog/power implementation and production qualification remain
open. `IMP-0046` is the only owner decision created by this pass; after it,
the exact analog circuit and parts can be reviewed.

