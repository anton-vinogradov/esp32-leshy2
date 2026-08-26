# H1-R2.3 · Airband input filter

A compact low-cost replacement for the large `BPF-A127+` has been tested. This is a physical-design result, not authorization to start KiCad.

![Airband filter feasibility](images/h1-airband-filter.svg)

## Result

- The nominal finite-Q model passes: worst 118–137 MHz loss is `3.03 dB` against `4.5 dB`, and every named nominal stop point passes.
- A `16386`-state value stress sweep keeps the passband within limit (`4.27 dB` against `4.5 dB`), but worst 180-MHz rejection is `34.62 dB` against `40 dB`. Values and production MPNs are therefore **not accepted**.
- The serial LC route is retained, but its physical cell grows to `24 × 11 mm` and gains a via fence plus alternate-value/DNP tuning pads.
- A lumped model cannot prove 180–2200 MHz above component SRF; H3 extracted modelling and H7 VNA measurement close that band.

## Factory feasibility witnesses

This is not the filter BOM. These rows prove that the required precision serial RF-inductor classes exist on the factory surface. The complete MPN set is accepted only after H3.

| Exact MPN | JLCPCB | Value | Current route |
|---|---|---|---|
| `LQW2UASR56F00L` | [`C907989`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2UASR56F00L/C907989) | 560 nH +/-1%, 1008 | 502 pieces, MOQ 1, USD 0.2618 at quantity 1 |
| `LQW2BASR22G00L` | [`C527968`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR22G00L/C527968) | 220 nH +/-2%, 0805 | 180 pieces, MOQ 1, USD 0.1325 at quantity 1 |
| `LQW2BASR33G00L` | [`C703717`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR33G00L/C703717) | 330 nH +/-2%, 0805 | 249 pieces, MOQ 1, USD 0.1455 at quantity 1 |
| `LQW15AN10NG80D` | [`C3224837`](https://www.lcsc.com/product-detail/C3224837.html) | 10 nH +/-2%, 0402 | 28,540 pieces, MOQ/multiple 10, USD 0.0575 at quantity 10 |

## Next gate

H3 must find one fixed factory BOM state with extracted PCB parasitics and tolerances. If the complete mask does not close, the design returns to an exact purchased filter or a different receiver boundary; nominal compliance will not be presented as a finished result.

> Exact current marker: **H1-R2.3**. H1 remains in progress.
