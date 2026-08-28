# H1-R2.27 · component cost ranking

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

This is a ranked snapshot of the current hardware, not a commercial quote. Every line burden includes the quantity fitted to one device; the trial columns use five devices and preserve observed JLCPCB MOQ/pre-order effects.

## Summary

- Volume material basis: **$235.33** per device; `198/210` lines are priced.
- Reachable planning subtotal: **$284.61** per device, with `5` base-product lines still unpriced.
- With the required post-PCBA K331: **$314.60** per device or **$1,573.00** for five devices before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.
- Partial five-device JLCPCB capture: **$1,224.48** for `178` matched lines; `16` live checks move it to **$1,283.40**, with `32` rows excluded.
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

- The `30` pre-order rows cost **$690.02** in the capture versus **$335.73** on their volume material basis.
- The observed small-lot premium is **$354.29**. This is the first priority: seek stocked JLCPCB MPNs that remain inside the existing substitution envelopes.
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

## Verified stocked candidates

| Scope | Current | Candidate | JLCPCB | Stock | Status |
|---|---|---|---|---:|---|
| dual Ioff return buffers | `Nexperia 74LVC2G126DC,125` | `Nexperia 74LVC2G126DP,125` | `C503392` | 155 | `accepted_stocked_exact_family_package_variant` |
| all 100-nF 50-V X7R 0402 bypass positions | `TDK C1005X7R1H104K050BB` | `YAGEO CC0402KRX7R9BB104` | `C131394` | 9027089 | `accepted_stocked_exact_parametric_replacement` |
| six ordinary 0402 resistor identities across 28 positions | `YAGEO RC0402FR-072K2L / 07133KL / 07270KL / 075K23L / 078K2L / 071K65L` | `UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE` | `C25879 / C25753 / C25770 / C25907 / C25924 / C25869` | 2027222 / 6692 / 156208 / 40861 / 234262 / 5616 | `accepted_stocked_exact_parametric_replacements` |
| two dual Schmitt inverters | `Nexperia 74LVC2G14GW,125` | `Nexperia 74LVC2G14GV,125` | `C426708` | 153 | `accepted_stocked_exact_family_package_variant` |
| codec transmit attenuator top resistor | `Vishay CRCW0402160KFKED` | `UNI-ROYAL 0402WGF1603TCE` | `C25757` | 388017 | `accepted_stocked_exact_parametric_replacement` |
| IR emitter current-limit resistor | `YAGEO RC1206FR-0747RL` | `FH RS-06K47R0FT` | `C140014` | 78058 | `accepted_stocked_exact_parametric_replacement` |
| 100-nF 100-V USB VBIAS capacitor | `TDK C1608X7S2A104K080AB` | `YAGEO CC0603KRX7R0BB104` | `C113803` | 1027658 | `accepted_stocked_no_worse_parametric_replacement` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `OMRON B3S-1000P` | `C180420` | 3254 | `not_accepted_missing_ground_terminal` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5` | `C53278703 / C53278707` | 67 standard / 133 reverse | `rejected_wrong_board_normal_orientation` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `DreamLNK SMA-KWE902 / SMA-KWE901` | `C914554 / C914553` | 5594 standard / 64 reverse | `rejected_high_profile_tht_form_change` |

- **`Nexperia 74LVC2G126DP,125`:** Accepted at H1-R2.23. DP and DC are package variants of the same current Nexperia 74LVC2G126 family and preserve logic, pin order, Schmitt inputs, Ioff and timing. The larger TSSOP bodies pass the regenerated placement audit. The five-device line falls from the observed USD 40.60 pre-order route to USD 12.1425 in stock; the quantity-100 unit tier rises from the former external USD 0.2086 basis to JLCPCB USD 0.3753. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392)
- **`YAGEO CC0402KRX7R9BB104`:** Accepted at H1-R2.24. The YAGEO part preserves 100 nF, 50 V, X7R, +/-10%, 0402/1005, -55 to +125 C and the exact 1.0 x 0.5 x 0.5-mm body. The JLCPCB route is MOQ 1 and stocked for Standard PCBA. The five-device line falls from the observed USD 22.5624 TDK pre-order charge to USD 5.9535 in stock, saving USD 16.6089; the quantity-100 material basis falls by USD 2.2197 per device. [JLCPCB](https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394)
- **`UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE`:** Accepted at H1-R2.26. Every replacement preserves its exact resistance, 0402 body, 1% tolerance, 62.5-mW rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. All six exact UNI-ROYAL MPNs are live JLCPCB Standard-PCBA stock with MOQ 1. Their five-device requirement falls from approximately USD 53.7347 in the captured pre-order route to USD 0.5430 in live stock, saving approximately USD 53.1917; the public material basis falls by USD 0.1542 per device. [JLCPCB](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879)
- **`Nexperia 74LVC2G14GV,125`:** Accepted at H1-R2.26. GV and GW are package variants in the same current Nexperia 74LVC2G14 datasheet: dual Schmitt-inverter behavior, pins 1-6, 1.65-to-5.5-V operation, Ioff partial-power-down protection and timing are common. The 2.9 x 1.5 x 1.1-mm TSOP6 bodies pass the regenerated placement audit. Ten trial parts are covered by the 35-piece available order quantity. The five-device line falls from USD 9.0376 pre-order to USD 2.0100 in stock, saving USD 7.0276; the conservative quantity-100 material basis rises by USD 0.2026 per device. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708)
- **`UNI-ROYAL 0402WGF1603TCE`:** Accepted at H1-R2.27. The UNI-ROYAL part preserves 160 kOhm, +/-1%, 0402, the standardized 1/16-W rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. Its official body is 1.00 x 0.50 x 0.35 mm versus the selected Vishay's 1.00 x 0.50 x 0.40 mm, so the verified 0402 land pattern and sandwich clearance do not degrade. The five-device line falls from USD 8.9565 pre-order to USD 0.0130 in stock, saving USD 8.9435; the public material basis falls by USD 0.0131 per device. [JLCPCB](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757)
- **`FH RS-06K47R0FT`:** Accepted at H1-R2.27. The FH part preserves 47 Ohm, +/-1%, 1206, 0.25 W, 200 V, 100 ppm/C and -55 to +155 C. Its official 3.20 x 1.60 x 0.55-mm body is thinner than the selected YAGEO 3.20 x 1.60 x 0.65-mm body and uses the standard 1206 land pattern. The five-device line falls from USD 8.9566 pre-order to USD 0.0310 in stock, saving USD 8.9256; the public material basis falls by USD 0.0108 per device. [JLCPCB](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014)
- **`YAGEO CC0603KRX7R0BB104`:** Accepted at H1-R2.27. The YAGEO part preserves 100 nF, +/-10%, 100 V, 0603/1608, -55 to +125 C and the exact 1.60 x 0.80 x 0.80-mm body. X7R holds capacitance within +/-15% over temperature and is stricter than the former X7S +/-22% class, so the USB VBIAS role does not degrade. The five-device line falls from USD 9.0752 pre-order to USD 0.1300 in stock, saving USD 8.9452; the public material basis falls by USD 0.0266 per device. [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803)
- **`OMRON B3S-1000P`:** The stocked member preserves the 6.6 x 6.0 x 4.3-mm body, 1.57-N feel, 500k endurance and IP67 family boundary, but removes the fifth cover-ground terminal. That can weaken the user-exposed ESD path, so the current B3S-1100P remains selected until an equivalent grounded stocked part is proven. [JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-B3S1000P/C180420)
- **`HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5`:** The JLCPCB cards prove a 6-GHz standard/reverse pair and the controlled HenryTech drawings prove individual retention without a nut, but both bodies point normal to the PCB. They do not replace the selected edge-facing GCT bodies without changing antenna direction and product form. [JLCPCB](https://jlcpcb.com/partdetail/HenryTech-HL2_SMA_KEP_135/C53278703)
- **`DreamLNK SMA-KWE902 / SMA-KWE901`:** This is a fully documented, stocked, no-nut 6-GHz right-angle standard/reverse pair, but its approximately 10.2-mm board profile and through-hole tails replace the 3.9-mm GCT edge-launch envelope. On the front board the connector axis would sit roughly 7 mm above the display glass and the tails would enter the sandwich. The saving is real but not functionally or mechanically neutral. [JLCPCB](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554)
**Accepted rule:** remove avoidable small-lot pre-order first, but replace an MPN only with an exact or no-worse stocked part. RF, power-safety, battery-protection and user-exposed ESD boundaries are not simplified for cost. When no proven equivalent exists, the original MPN and explicit pre-order route remain.

## Cost-reduction queue

1. ✅ **Replace safe equivalent pre-order passives and ordinary logic with in-stock JLCPCB parts** — After five safe replacement batches, 30 pre-order rows cost USD 690.0191 in the normalized five-device evidence versus USD 335.7260 on their quantity-100 material basis. The stocked Nexperia package variants, YAGEO bypass capacitors, UNI-ROYAL resistors and FH IR resistor together remove approximately USD 132.1000 from the observed trial route and reduce the public material basis by a net USD 1.3883 per device. Review every pre-order row against its substitution class; only exact or no-worse parametric replacements may be accepted.
2. ✅ **Retain the low-profile GCT edge-launch pair unless a truly equivalent stocked pair appears** — HenryTech provides a cheaper straight pair and DreamLNK provides a cheaper right-angle pair without nuts, but neither preserves the selected 3.9-mm edge-launch envelope. The DreamLNK pair would save about USD 19.01 per device at the quantity-100 tiers while raising the connector axis roughly 6.3 mm and adding through-hole tails inside the sandwich. Keep GCT RFPC-SMA31/32 with independent board retention and no shared frame. Reopen replacement only for a stocked standard/reverse edge-launch pair rated to at least 6 GHz with equal or lower profile and a controlled 1.6-mm PCB drawing.
3. ⚠️ **Re-evaluate eight RF power detectors without weakening real-TX evidence** — Six AD8314 plus two LTC5532 contribute USD 24.9174 per device at quantity 100; the live five-device requirement is USD 276.70 and both families require pre-order for the complete quantity. Compare factory-stocked detectors and calibrated diode cells per band. Keep independent evidence for the three concurrently active nRF24 paths.
4. ✅ **Find one serial in-stock tact-switch family for all sixteen ordinary controls** — B3S-1100P contributes USD 10.248 per device at quantity 100 and USD 74.58 for 80 pieces in the five-device pre-order route. Preserve footprint/enclosure reach, force, height, endurance and recessed actuation.
5. ⚠️ **Reduce five U.FL receptacle plus 30-mm jumper paths by source-to-port placement** — Five board U.FL plus five TE jumpers contribute USD 14.433 per device at quantity 100, before assembly handling. Remove a cable only where a short controlled-impedance direct path preserves module keep-outs, repairability and coexistence.
6. ⚠️ **Compare the 1048P holder with serial cell contacts captured by the enclosure cradle** — 1048P contributes USD 8.57 per device at quantity 100 and is currently stock-zero pre-order at JLCPCB. Any replacement must keep protected-cell length tolerance, polarity, insertion cycles and a non-peeling enclosure load path.
7. ✅ **Replace three premium DBG10 headers with an equally keyed serial factory-stocked family** — Three Samtec FTSH headers contribute USD 5.0973 per device and exist only as opened-sandwich recovery fallbacks. Preserve independent S3/C5/RP recovery, keying, pitch, probe access and the internal height envelope.
8. ✅ **Obtain the standalone panel route instead of consuming a complete donor per device** — The current reachable DLE06235B donor is USD 20.90 per display, while standalone HMX035CTFT-001 price and production identity remain open. Keep the replaceable adapter and treat the donor as an EVT ceiling, not production COGS.

## Display and flex orientation

- The official complete-donor rear view does show a folded FPC and rear ZIF, but it does not disclose the standalone raw `HMX035CTFT-001` outline, length or contact side.
- The correct rule is to physically orient the panel **with its flex toward the antenna edge**, then rotate display memory and touch coordinates in firmware. The tail then stays out of the LED, D-pad and function-key zone.
- The accepted upper adapter PCB position `[24.75, 1.0]` passes the current exact-body model: `0` same-face collisions and `5.1 mm` minimum opposing clearance versus `0.7 mm` required, with no GPIO or BOM change.
- H1 now fixes this orientation; H5 qualifies the received flex, bend and retention on the replaceable adapter. A mismatch cannot silently return the tail to the control zone.

> Marker: **H1-R2.27**. H1 remains open pending the complete mock-up decision.
