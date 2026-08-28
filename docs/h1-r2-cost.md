# H1-R2.21 · component cost ranking

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

This is a ranked snapshot of the current hardware, not a commercial quote. Every line burden includes the quantity fitted to one device; the trial columns use five devices and preserve observed JLCPCB MOQ/pre-order effects.

## Summary

- Volume material basis: **$236.72** per device; `198/210` lines are priced.
- Reachable planning subtotal: **$286.00** per device, with `5` base-product lines still unpriced.
- With the required post-PCBA K331: **$315.99** per device or **$1,579.94** for five devices before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.
- Partial five-device JLCPCB capture: **$1,354.66** for `178` matched lines; four live checks move it to **$1,415.50**, with `32` rows excluded.
- The external antenna kit is separate: **$145.27** is known and `4` lines remain unpriced.

## Highest-cost finished-device lines

| MPN | Role | Per device | Unit on accepted basis | Device line | For 5 devices | Planned line ×5 | JLC live / MOQ |
|---|---|---:|---:|---:|---:|---:|---:|
| `HMX035CTFT-001 (QDtech schematic assembly marking)` | display/touch assembly via donor ceiling / экран и touch через donor-ceiling | 1 | $20.90 | $20.90 | 5 | $104.50 | — |
| `GCT RFPC-SMA31-FN-175-A` | eight standard outward SMA / восемь внешних SMA | 8 | $2.46 | $19.72 | 40 | $98.58 | — |
| `Analog Devices AD8314ACPZ-RL7` | six real-TX RF detectors / шесть RF-детекторов фактической передачи | 6 | $2.86 | $17.14 | 30 | $85.71 | $159.55 |
| `OMRON B3S-1100P` | sixteen ordinary user keys / шестнадцать обычных клавиш | 16 | $0.64 | $10.25 | 80 | $51.24 | $74.58 |
| `G-NiceRF SA818S-V` | VHF voice transceiver / VHF голосовой трансивер | 1 | $10.07 | $10.07 | 5 | $50.35 | $50.35 |
| `G-NiceRF SA818S-U` | UHF voice transceiver / UHF голосовой трансивер | 1 | $9.73 | $9.73 | 5 | $48.67 | $48.67 |
| `TE Connectivity 2118651-2` | five 30-mm RF jumpers / пять 30-мм RF-кабелей | 5 | $1.82 | $9.11 | 25 | $45.53 | — |
| `Keystone Electronics 1048P` | dual protected-18650 holder / держатель двух защищённых 18650 | 1 | $8.57 | $8.57 | 5 | $42.85 | $33.66 |
| `Texas Instruments TMUX1136DGSR` | four complete audio/control selectors / четыре полных audio/control selector | 4 | $2.06 | $8.23 | 20 | $41.16 | $12.79 |
| `LTC5532ES6#TRMPBF` | S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц | 2 | $3.89 | $7.78 | 10 | $38.88 | $117.15 |
| `Ebyte E01-ML01IPX` | three full nRF24 radios / три полнофункциональных nRF24 | 3 | $2.37 | $7.11 | 15 | $35.55 | — |
| `Hirose U.FL-R-SMT-1(10)` | five native/module microcoax mates / пять микрокоаксиальных точек | 5 | $1.07 | $5.33 | 25 | $26.64 | $5.66 |
| `ESP32-S3-WROOM-1U-N16R8` | s3 | 1 | $5.11 | $5.11 | 5 | $25.54 | $25.24 |
| `Samtec FTSH-105-01-L-DV-K-P-TR` | three internal recovery headers / три внутренних recovery-разъёма | 3 | $1.70 | $5.10 | 15 | $25.49 | $16.35 |
| `GCT RFPC-SMA32-FN-175-A` | two native-radio RP-SMA / два RP-SMA native-радио | 2 | $2.46 | $4.93 | 10 | $24.65 | — |
| `TPS3808G33DBVR` | safe_supervisor, u214_supervisor, unit_supervisor, voice_supervisor | 4 | $1.10 | $4.39 | 20 | $21.97 | $8.86 |
| `ESP32-C5-WROOM-1U-N8R8` | c5 | 1 | $4.37 | $4.37 | 5 | $21.85 | — |
| `Murata GRM32ER71E226KE15L` | thirteen 22-uF power capacitors / тринадцать силовых конденсаторов 22 мкФ | 13 | $0.33 | $4.29 | 65 | $21.47 | $31.67 |
| `Texas Instruments TPD4E05U06DQAR` | thirteen four-line ESD arrays / тринадцать четырёхканальных ESD-сборок | 13 | $0.31 | $4.02 | 65 | $20.09 | — |
| `Analog Devices MAX17320G20+T` | pack_gauge | 1 | $4.00 | $4.00 | 5 | $20.01 | $31.06 |

[Complete 210-line ranking — CSV](../hardware/product-design/generated/H1-R2-cost-ranked.csv)

## Where the small batch overpays

- The `42` pre-order rows cost **$842.94** in the capture versus **$362.23** on their volume material basis.
- The observed small-lot premium is **$480.71**. This is the first priority: seek stocked JLCPCB MPNs that remain inside the existing substitution envelopes.
- JLCPCB displayed-line cost uses recommended quantities and pre-order reference pricing; it is an honest small-batch pain indicator, not a final quote or order total.

## External antenna kit

| Code | Profile | MPN | Qty | Known line |
|---|---|---|---:|---:|
| `AIR` | receive-only telescopic whip | `SMA-W100RX2` | 1 | $35.95 |
| `VHF` | VHF 136-174 MHz | `AN0155H13` | 1 | $31.70 |
| `S3` | 2.4/5 GHz native radio | `001-0012` | 1 | $16.91 |
| `C5` | 2.4/5 GHz native radio | `001-0012` | 1 | $16.91 |
| `S433` | 433 MHz | `ANT-433-CW-QW-SMA` | 1 | $11.23 |
| `UHF` | UHF 400-470 MHz | `ANT-433-CW-QW-SMA` | 1 | $11.23 |
| `S315` | 315 MHz | `ANT-315-CW-HW-SMA` | 1 | $9.60 |
| `FPV` | receive-only 5.8-GHz analog FPV, unknown source polarization | `TBS5G8MMCXA` | 1 | $6.95 |
| `S915` | 868/915 MHz | `TI.08.C.0112` | 1 | $4.79 |
| `N1` | 2.4 GHz nRF24 | `TX2400-JW-5` | 1 | — |
| `N2` | 2.4 GHz nRF24 | `TX2400-JW-5` | 1 | — |
| `N3` | 2.4 GHz nRF24 | `TX2400-JW-5` | 1 | — |
| `LOOP` | passive receive-only direct-plug ferrite pod | `L2-ANT-AM-LW-001` | 1 | — |

## Cost-reduction queue

1. ✅ **Replace safe equivalent pre-order passives and ordinary logic with in-stock JLCPCB parts** — The normalized five-device evidence charges USD 842.9365 for 42 pre-order rows versus USD 362.2315 for the same rows on their quantity-100 material basis; the observed small-lot premium is USD 480.705 before full quotation. Review every pre-order row against its substitution class; only exact or no-worse parametric replacements may be accepted.
2. ✅ **Replace the ten GCT bulkhead-style SMA/RP-SMA bodies with factory-placeable edge connectors and a shared protective frame** — The current ten GCT bodies contribute USD 24.6456 per device at the quantity-100 source tier and have no demonstrated current JLCPCB route; their individual nuts do not transfer load without a real enclosure wall. Search an exact standard/reverse pair with mechanical board tabs, 1.6-mm PCB fit and at least 6-GHz rating for native paths.
3. ⚠️ **Re-evaluate eight RF power detectors without weakening real-TX evidence** — Six AD8314 plus two LTC5532 contribute USD 24.9174 per device at quantity 100; the live five-device requirement is USD 276.70 and both families require pre-order for the complete quantity. Compare factory-stocked detectors and calibrated diode cells per band. Keep independent evidence for the three concurrently active nRF24 paths.
4. ✅ **Find one serial in-stock tact-switch family for all sixteen ordinary controls** — B3S-1100P contributes USD 10.248 per device at quantity 100 and USD 74.58 for 80 pieces in the five-device pre-order route. Preserve footprint/enclosure reach, force, height, endurance and recessed actuation.
5. ⚠️ **Reduce five U.FL receptacle plus 30-mm jumper paths by source-to-port placement** — Five board U.FL plus five TE jumpers contribute USD 14.433 per device at quantity 100, before assembly handling. Remove a cable only where a short controlled-impedance direct path preserves module keep-outs, repairability and coexistence.
6. ⚠️ **Compare the 1048P holder with serial cell contacts captured by the enclosure cradle** — 1048P contributes USD 8.57 per device at quantity 100 and is currently stock-zero pre-order at JLCPCB. Any replacement must keep protected-cell length tolerance, polarity, insertion cycles and a non-peeling enclosure load path.
7. ✅ **Replace three premium DBG10 headers with an equally keyed serial factory-stocked family** — Three Samtec FTSH headers contribute USD 5.0973 per device and exist only as opened-sandwich recovery fallbacks. Preserve independent S3/C5/RP recovery, keying, pitch, probe access and the internal height envelope.
8. ✅ **Obtain the standalone panel route instead of consuming a complete donor per device** — The current reachable DLE06235B donor is USD 20.90 per display, while standalone HMX035CTFT-001 price and production identity remain open. Keep the replaceable adapter and treat the donor as an EVT ceiling, not production COGS.

## Display and flex orientation

- The official complete-donor rear view does show a folded FPC and rear ZIF, but it does not disclose the standalone raw `HMX035CTFT-001` outline, length or contact side.
- The correct rule is to physically orient the panel **with its flex toward the antenna edge**, then rotate display memory and touch coordinates in firmware. The tail then stays out of the LED, D-pad and function-key zone.
- The upper adapter PCB position `[24.75, 1.0]` already passes the current exact-body model: `0` same-face collisions and `5.1 mm` minimum opposing clearance versus `0.7 mm` required, with no GPIO or BOM change.
- This is a preferred orientation rather than a frozen production fact until the received flex passes H5 bend/retention. The lower position remains the proven fallback until then.

> Marker: **H1-R2.21**. H1 remains open pending the complete mock-up decision.
