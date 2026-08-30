# H1-R2.3 · Airband input filter

A compact low-cost replacement for the large `BPF-A127+` has been tested. H2 now carries its exact nominal BOM into the native schematic, but the production fitted state is not frozen.

![Airband filter feasibility](images/h1-airband-filter.svg)

## Result

- The nominal finite-Q model passes: worst 118–137 MHz loss is `3.10 dB` against `4.5 dB`, and every named nominal stop point passes.
- A `16386`-state value stress sweep keeps the passband within limit (`4.67 dB` against `4.5 dB`), but worst 155-MHz rejection is `17.85 dB` against `20 dB`. The exact stocked H2 MPNs are therefore accepted only as the nominal ECAD state; the production fitted state is **not accepted**.
- The serial LC route is retained, but its physical cell grows to `24 × 11 mm` and gains a via fence plus alternate-value/DNP tuning pads.
- A lumped model cannot prove 180–2200 MHz above component SRF: H3 uses a bounded pre-layout model, H6 reruns with routed/extracted parasitics before the H7 order, and H8 closes the production state by VNA.

## Factory feasibility witnesses

These are checked stocked MPNs for the nominal H2 ECAD state, not yet the production filter BOM. H3 retunes against manufacturer models, H6 fixes the pre-order fitted/DNP state after extraction, and H8 checks the production state by VNA.

| Exact MPN | JLCPCB | Value | Current route |
|---|---|---|---|
| `LQW2UASR56F00L` | [`C907989`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2UASR56F00L/C907989) | 560 nH +/-1%, 1008 | 155 stock / 152 available, MOQ 1, USD 0.272 at quantity 1 |
| `LQW2BASR22G00L` | [`C527968`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR22G00L/C527968) | 220 nH +/-2%, 0805 | 28 stock / 25 available, MOQ 1, USD 0.1324 at quantity 1 |
| `LQW2BASR33G00L` | [`C703717`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR33G00L/C703717) | 330 nH +/-2%, 0805 | 4573 stock / 4548 available, MOQ 1, USD 0.1158 at quantity 1 |
| `LQW15AN8N2G80D` | [`C307610`](https://jlcpcb.com/partdetail/MurataElectronics-LQW15AN8N2G80D/C307610) | 8.2 nH +/-2%, 0402 | 8484 stock / 8343 available, MOQ 1, USD 0.0975 at quantity 1 |
| `CS0805-R27J-S` | [`C108271`](https://jlcpcb.com/partdetail/ChilisinElec-CS0805R27JS/C108271) | 270 nH +/-5%, Q 48 witness, 0805 | 1972 stock, MOQ 1, USD 0.0549 at quantity 1 |

## Next gate

H2 carries the complete tuning network into ECAD. H3 checks it with bounded pre-layout parasitics; H6 repeats the proof with routed/extracted parasitics before the H7 order; H8 selects the production fitted/DNP state by VNA. A failed mask returns the design to an exact purchased filter or different receiver boundary.

> Result marker: **H1-R2.3**. The current H1 marker is published on the roadmap.
