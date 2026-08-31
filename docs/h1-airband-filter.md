# H3-R2.3 · Airband input filter

The large purchased `BPF-A127+` has been replaced by an exact factory-placeable LC network without weakening the accepted mask.

![Airband filter verification](images/h1-airband-filter.svg)

## Result

- All `1024` effective tolerance endpoints pass; the minimum calculated margin is `0.187 dB`.
- The filter has `18` fitted parts and `10` exact MPNs; all were live JLCPCB SMT routes for Standard PCBA with MOQ 1 on 2026-08-31.
- One device uses `$1.6736` of filter material instead of the costly purchased filter.
- This is not yet a production freeze: the small margin requires the same H6 mask with routed parasitics, followed by the H8 assembled-board VNA check.

## Exact fitted group

| Exact MPN | JLCPCB | Quantity | Role |
|---|---|---:|---|
| `LQW2BASR22G00L` | `C527968` | 2 | S1/S3 220-nH series arms |
| `LQW2BAS47NG00L` | `C162657` | 2 | S1/S3 47-nH series arms |
| `LQW2BAS22NG00L` | `C2042201` | 4 | P1/P2 equal 22-nH parallel pairs |
| `LQW2UASR56F00L` | `C907989` | 1 | S2 560-nH arm |
| `GJM1555C1H5R7WB01D` | `C2220921` | 1 | S1 5.7-pF arm |
| `GCM1555C1H121FA16D` | `C126496` | 2 | P1/P2 120-pF branches |
| `GCM1555C1H200FA16D` | `C437436` | 2 | P1/P2 20-pF branches |
| `GJM1555C1H1R4WB01D` | `C2181496` | 2 | P1/P2 1.4-pF fine branches |
| `CC0402BRNPO9BN2R8` | `C1853353` | 1 | S2 2.8-pF arm |
| `GJM1555C1H5R8WB01D` | `C2177031` | 1 | S3 5.8-pF arm |

## Next gate

H6 uses the reserved compact tuning island and fitted/DNP trim footprints, extracts routed pads, traces, vias, coupling, shield and enclosure parasitics, and reruns the same mask before the exact-one order. H8 VNA measurement confirms or retunes the fitted/DNP state on the assembled prototype.
