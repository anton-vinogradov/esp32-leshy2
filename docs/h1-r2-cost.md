# H1-R2.35 · component cost ranking

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

This is a ranked snapshot of the current hardware, not a commercial quote. Every line burden includes the fitted quantity in the target one fully assembled prototype. Identical MPNs are grouped into one row; the historical five-board BOM Tool capture remains below only as MOQ/pre-order evidence, not the procurement target.

## Summary

- Volume material basis: **$257.25** per device; `201/210` lines are priced.
- Reachable planning subtotal: **$278.55** per device, with `5` base-product lines still unpriced.
- Current planned component minimum with no mandatory post-PCBA active module: **$278.55** per device and **$278.55** for the one target prototype before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.
- The same accepted price basis scales linearly to **$2,785.53** for ten devices. This compares groups; it is not a batch quote.
- The top 10 / 20 / 40 groups contribute **41.87% / 59.49% / 77.72%** of the known base BOM.
- Historical five-board JLCPCB capture: **$1,373.20** for `183` matched lines; `23` live checks move it to **$1,429.94**, with `27` rows excluded. This is evidence, not the target quantity.
- The external antenna kit is separate: **$138.32** is known and `4` positions in `2` MPN groups remain unpriced. The known electronics plus known antennas already reach **$416.87** before PCB/PCBA, enclosure and freight.

## The $150 target gate

- The complete base-device target is **at most $150.00**, excluding batteries and the full specialized external-antenna kit.
- To leave room for PCB, PCBA and enclosure, electronics must land near **$108.00–$125.00**.
- The current base BOM has `208` MPN groups and `1049` fitted components. Even the two paper-qualified no-function-loss replacements already identified — SMA/RP-SMA and the AD8314 package — save only **$24.51** and leave **$254.05**.
- That remains **$104.05** above the entire $150 boundary before paying for boards, assembly or enclosure. The remaining gap to the electronics target is **$129.05–$146.05**.

**Conclusion:** the present circuit cannot reach `$150` through brand substitutions alone. The target remains plausible only for a repeatable base device after a dedicated cost-constrained architecture resynthesis: preserve user-visible capabilities and the safety outcome while reducing measurement-class RF parts, service support circuitry and unique factory line items. The first sole prototype will still cost more because MOQ, setup, manual placement, freight and tax cannot be amortized.

The full antenna kit is an accessory, not a hidden device-price line. A broadband receive antenna cannot replace band-matched transmit antennas; the basic kit and additional band-specific antennas must be priced separately.

The primary ranking below shows **one prototype only**. It contains neither the historical five-board capture nor a ×10 multiplication.

## Unified top 20: electronics and external antennas

| № | Source | MPN and role | Qty ×1 | Unit on accepted basis | Group ×1 | Share of known total |
|---:|---|---|---:|---:|---:|---:|
| 1 | Antenna | `SMA-W100RX2`<br><sub>receive-only telescopic whip; AIR</sub> | 1 | $35.95 | $35.95 | 8.62% |
| 2 | Antenna | `001-0012`<br><sub>2.4/5 GHz native radio; S3, C5</sub> | 2 | $16.91 | $33.82 | 8.11% |
| 3 | Antenna | `AN0155H13`<br><sub>VHF 136-174 MHz; VHF</sub> | 1 | $31.70 | $31.70 | 7.60% |
| 4 | Antenna | `ANT-433-CW-QW-SMA`<br><sub>433 MHz / UHF 400-470 MHz; S433, UHF</sub> | 2 | $11.23 | $22.46 | 5.39% |
| 5 | Base BOM | `GCT RFPC-SMA31-FN-175-A`<br><sub>eight standard outward SMA / восемь внешних SMA</sub> | 8 | $2.46 | $19.72 | 4.73% |
| 6 | Base BOM | `Analog Devices AD8314ACPZ-RL7`<br><sub>six real-TX RF detectors / шесть RF-детекторов фактической передачи</sub> | 6 | $2.86 | $17.14 | 4.11% |
| 7 | Base BOM | `EastRising ER-TFT035IPS-6 + ER-TPC035-6`<br><sub>display</sub> | 1 | $14.91 | $14.91 | 3.58% |
| 8 | Base BOM | `OMRON B3S-1100P`<br><sub>sixteen ordinary user keys / шестнадцать обычных клавиш</sub> | 16 | $0.64 | $10.25 | 2.46% |
| 9 | Base BOM | `G-NiceRF SA818S-V`<br><sub>VHF voice transceiver / VHF голосовой трансивер</sub> | 1 | $10.07 | $10.07 | 2.42% |
| 10 | Base BOM | `G-NiceRF SA818S-U`<br><sub>UHF voice transceiver / UHF голосовой трансивер</sub> | 1 | $9.73 | $9.73 | 2.33% |
| 11 | Antenna | `ANT-315-CW-HW-SMA`<br><sub>315 MHz; S315</sub> | 1 | $9.60 | $9.60 | 2.30% |
| 12 | Base BOM | `TE Connectivity 2118651-2`<br><sub>five 30-mm RF jumpers / пять 30-мм RF-кабелей</sub> | 5 | $1.82 | $9.11 | 2.18% |
| 13 | Base BOM | `Ebyte E01-ML01SP4`<br><sub>three 20-dBm PA/LNA full-function nRF24 radios / три полнофункциональных nRF24 с PA/LNA 20 dBm</sub> | 3 | $2.96 | $8.89 | 2.13% |
| 14 | Base BOM | `Keystone Electronics 1048P`<br><sub>dual protected-18650 holder / держатель двух защищённых 18650</sub> | 1 | $8.57 | $8.57 | 2.06% |
| 15 | Base BOM | `Texas Instruments TMUX1136DGSR`<br><sub>four complete audio/control selectors / четыре полных audio/control selector</sub> | 4 | $2.06 | $8.23 | 1.98% |
| 16 | Base BOM | `LTC5532ES6#TRMPBF`<br><sub>S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц</sub> | 2 | $3.89 | $7.78 | 1.86% |
| 17 | Base BOM | `Hirose U.FL-R-SMT-1(10)`<br><sub>five native/module microcoax mates / пять микрокоаксиальных точек</sub> | 5 | $1.07 | $5.33 | 1.28% |
| 18 | Base BOM | `ESP32-S3-WROOM-1U-N16R8`<br><sub>s3</sub> | 1 | $5.11 | $5.11 | 1.23% |
| 19 | Base BOM | `Samtec FTSH-105-01-L-DV-K-P-TR`<br><sub>three internal recovery headers / три внутренних recovery-разъёма</sub> | 3 | $1.70 | $5.10 | 1.22% |
| 20 | Base BOM | `GCT RFPC-SMA32-FN-175-A`<br><sub>two native-radio RP-SMA / два RP-SMA native-радио</sub> | 2 | $2.46 | $4.93 | 1.18% |

[Unified top 20 — CSV](../hardware/product-design/generated/H1-R2-cost-top20.csv) · [Complete 210-line ranking — CSV](../hardware/product-design/generated/H1-R2-cost-ranked.csv)

## Most likely unjustified-cost candidates

| Priority | Group | Current ×1 | Finding | Realistic saving |
|---:|---|---:|---|---:|
| 1 | External antennas | $138.32 + 4 unknown | Largest separate group; the functions are required, but the first branded MPNs need not be the best-value equivalents | to be established |
| 2 | 10 outward SMA/RP-SMA | $24.65 | GCT cost is no longer justified by a low-profile requirement; a robust pair needs a fresh placement and factory manual-solder check | up to ~$19.02 |
| 3 | 8 RF detectors | $24.92 | Real-TX evidence remains required; six AD8314 can move to the stocked package of the same IC after placement review | ~$5.49 |
| 4 | 5 U.FL plus 5 cables | $14.43 | Functionally justified now; only a proven C5 T2 route can remove one path | up to ~$2.89 |
| 5 | 16 user buttons | $10.25 | Expensive group, but the first cheaper candidate lost the grounded cover and was rejected | to be established |
| 6 | Dual-18650 holder | $8.57 | Serial contacts are viable only if the enclosure carries all mechanical load | to be established |
| 7 | 3 internal DBG10 headers | $5.10 | Premium series serves only as an opened-sandwich recovery fallback; a cheaper keyed equivalent is plausible | to be established |

**Not classified as unjustified:** the $14.91 serial display, $19.81 dual voice modules, $8.89 three full-function nRF24 modules, both RP/S3/C5, M1 and autonomous safety components. Removing or simplifying them directly cuts an accepted function, throughput, recovery or safety boundary.

## Costs that must not be mistaken for zero

These positions have an **unknown**, not zero, price. The total remains a lower bound until the exact-one quote.

| Source | MPN and role | Qty ×1 |
|---|---|---:|
| Base BOM | `Murata GJM1555C1H101JB01D`<br><sub>cc_rf_n_dc_block, cc_rf_p_dc_block</sub> | 2 |
| Base BOM | `Nexperia PESD24VY1BSF`<br><sub>voice_rf_esd, voice_v_rf_esd</sub> | 2 |
| Base BOM | `Panasonic ERJ-P08F49R9V`<br><sub>pack_batts_rbal, pack_cell1_rbal</sub> | 2 |
| Base BOM | `Sunlord MWSA0503S-3R3MT`<br><sub>main_inductor, voice_inductor</sub> | 2 |
| Base BOM | `Texas Instruments TPUL2G223BQBR`<br><sub>pack_diag_timer</sub> | 1 |
| Antenna kit | `TX2400-JW-5`<br><sub>2.4 GHz nRF24; N1, N2, N3</sub> | 3 |
| Antenna kit | `L2-ANT-AM-LW-001`<br><sub>passive receive-only direct-plug ferrite pod; LOOP</sub> | 1 |

## Where the small batch overpays

- The `27` pre-order rows cost **$660.01** in the capture versus **$331.03** on their volume material basis.
- The observed small-lot premium is **$328.98**. This is the first priority: seek stocked JLCPCB MPNs that remain inside the existing substitution envelopes.
- JLCPCB displayed-line cost uses recommended quantities and pre-order reference pricing; it is an honest small-batch pain indicator, not a final quote or order total.

## External antenna kit

| Code | Profile | MPN | Qty | Known line |
|---|---|---|---:|---:|
| `AIR` | receive-only telescopic whip | `SMA-W100RX2` | 1 | $35.95 |
| `S3, C5` | 2.4/5 GHz native radio | `001-0012` | 2 | $33.82 |
| `VHF` | VHF 136-174 MHz | `AN0155H13` | 1 | $31.70 |
| `S433, UHF` | 433 MHz / UHF 400-470 MHz | `ANT-433-CW-QW-SMA` | 2 | $22.46 |
| `S315` | 315 MHz | `ANT-315-CW-HW-SMA` | 1 | $9.60 |
| `S915` | 868/915 MHz | `TI.08.C.0112` | 1 | $4.79 |
| `N1, N2, N3` | 2.4 GHz nRF24 | `TX2400-JW-5` | 3 | — |
| `LOOP` | passive receive-only direct-plug ferrite pod | `L2-ANT-AM-LW-001` | 1 | — |

## Verified stocked candidates

| Scope | Current | Candidate | JLCPCB | Stock | Status |
|---|---|---|---|---:|---|
| ESP32-C5 production supplier route and revision floor | `ESP32-C5-WROOM-1U-N8R8 / historical C51950748` | `ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2` | `C54951858` | 460 | `accepted_stocked_supplier_route_identity_normalization` |
| dual Ioff return buffers | `Nexperia 74LVC2G126DC,125` | `Nexperia 74LVC2G126DP,125` | `C503392` | 155 | `accepted_stocked_exact_family_package_variant` |
| six AD8314 real-TX evidence detectors | `Analog Devices AD8314ACPZ-RL7` | `Analog Devices AD8314ARMZ-REEL` | `C652687` | 2977 | `qualified_same_device_pending_six_body_placement_gate` |
| all 100-nF 50-V X7R 0402 bypass positions | `TDK C1005X7R1H104K050BB` | `YAGEO CC0402KRX7R9BB104` | `C131394` | 9027089 | `accepted_stocked_exact_parametric_replacement` |
| six ordinary 0402 resistor identities across 28 positions | `YAGEO RC0402FR-072K2L / 07133KL / 07270KL / 075K23L / 078K2L / 071K65L` | `UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE` | `C25879 / C25753 / C25770 / C25907 / C25924 / C25869` | 2027222 / 6692 / 156208 / 40861 / 234262 / 5616 | `accepted_stocked_exact_parametric_replacements` |
| two dual Schmitt inverters | `Nexperia 74LVC2G14GW,125` | `Nexperia 74LVC2G14GV,125` | `C426708` | 153 | `accepted_stocked_exact_family_package_variant` |
| codec transmit attenuator top resistor | `Vishay CRCW0402160KFKED` | `UNI-ROYAL 0402WGF1603TCE` | `C25757` | 388017 | `accepted_stocked_exact_parametric_replacement` |
| IR emitter current-limit resistor | `YAGEO RC1206FR-0747RL` | `FH RS-06K47R0FT` | `C140014` | 78058 | `accepted_stocked_exact_parametric_replacement` |
| 100-nF 100-V USB VBIAS capacitor | `TDK C1608X7S2A104K080AB` | `YAGEO CC0603KRX7R0BB104` | `C113803` | 1027658 | `accepted_stocked_no_worse_parametric_replacement` |
| display-adapter main-board receptacle | `Hirose DF40C(2.0)-40DS-0.4V(58)` | `Hirose DF40C(2.0)-40DS-0.4V(51)` | `C597934` | 7218 | `accepted_stocked_exact_packaging_variant` |
| dual common-drain pack-protection MOSFET | `Texas Instruments CSD87313DMST` | `Texas Instruments CSD87313DMS` | `C2863848` | 4813 | `accepted_stocked_exact_packaging_variant` |
| robust 38-kHz demodulating IR receiver | `Vishay TSOP75238TT` | `Vishay TSOP75238TR` | `C511498` | 17 | `accepted_stocked_exact_tape_presentation_variant_with_placement_gate` |
| Si4732 FMI 56-nH high-Q matching inductor | `Murata LQW15AN56NJ00D` | `Murata LQW15AN56NG00D` | `C167482` | 21558 | `accepted_stocked_no_worse_parametric_replacement` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `OMRON B3S-1000P` | `C180420` | 3254 | `not_accepted_missing_ground_terminal` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5` | `C53278703 / C53278707` | 67 standard / 133 reverse | `rejected_wrong_board_normal_orientation` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `DreamLNK SMA-KWE902 / SMA-KWE901` | `C914554 / C914553` | 5479 pre-sale + 5588 overseas standard / 7 pre-sale + 42 overseas reverse | `qualified_pending_full_5_plus_5_placement_and_assembly_gate` |

- **`ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2`:** Accepted at H1-R2.28 without changing the official Espressif MPN, 8-MiB flash, 8-MiB PSRAM, module body, land pattern or antenna connector. The JLC suffix is a supplier order code only. C54951858 is the active stocked Standard-PCBA route; historical zero-stock C51950748 is forbidden as active. Production requires incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed. The quantity-100 material basis falls from USD 4.3700 to USD 4.1338 per device, while the five-device live line is USD 29.2935. [JLCPCB](https://jlcpcb.com/partdetail/C54951858)
- **`Nexperia 74LVC2G126DP,125`:** Accepted at H1-R2.23. DP and DC are package variants of the same current Nexperia 74LVC2G126 family and preserve logic, pin order, Schmitt inputs, Ioff and timing. The larger TSSOP bodies pass the regenerated placement audit. The five-device line falls from the observed USD 40.60 pre-order route to USD 12.1425 in stock; the quantity-100 unit tier rises from the former external USD 0.2086 basis to JLCPCB USD 0.3753. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392)
- **`Analog Devices AD8314ARMZ-REEL`:** Analog Devices lists ACPZ-RL7 and ARMZ-REEL as production package variants of the same AD8314 specification with the same pins 1-8 and electrical behavior. C652687 is live JLCPCB stock. Thirty trial parts cost USD 70.56 instead of the current C578691 live requirement of USD 159.55, saving USD 88.99. On the report's common per-MPN quantity-100 price basis, the candidate reduces the six-device line from USD 17.142 to USD 11.6556 per finished device, saving USD 5.4864. This is not accepted into the production BOM yet: MSOP grows from the 2 x 3-mm LFCSP body to a roughly 3 x 3-mm body with up to 5.15-mm lead span and 1.10-mm height, and removes the exposed pad. All six exact courtyards, adjacent RF match/bypass bodies and RF-ground fanout must pass the H1 placement and route audit first. [JLCPCB](https://jlcpcb.com/partdetail/AD8314ARMZ-REEL/C652687)
- **`YAGEO CC0402KRX7R9BB104`:** Accepted at H1-R2.24. The YAGEO part preserves 100 nF, 50 V, X7R, +/-10%, 0402/1005, -55 to +125 C and the exact 1.0 x 0.5 x 0.5-mm body. The JLCPCB route is MOQ 1 and stocked for Standard PCBA. The five-device line falls from the observed USD 22.5624 TDK pre-order charge to USD 5.9535 in stock, saving USD 16.6089; the quantity-100 material basis falls by USD 2.2197 per device. [JLCPCB](https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394)
- **`UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE`:** Accepted at H1-R2.26. Every replacement preserves its exact resistance, 0402 body, 1% tolerance, 62.5-mW rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. All six exact UNI-ROYAL MPNs are live JLCPCB Standard-PCBA stock with MOQ 1. Their five-device requirement falls from approximately USD 53.7347 in the captured pre-order route to USD 0.5430 in live stock, saving approximately USD 53.1917; the public material basis falls by USD 0.1542 per device. [JLCPCB](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879)
- **`Nexperia 74LVC2G14GV,125`:** Accepted at H1-R2.26. GV and GW are package variants in the same current Nexperia 74LVC2G14 datasheet: dual Schmitt-inverter behavior, pins 1-6, 1.65-to-5.5-V operation, Ioff partial-power-down protection and timing are common. The 2.9 x 1.5 x 1.1-mm TSOP6 bodies pass the regenerated placement audit. Ten trial parts are covered by the 35-piece available order quantity. The five-device line falls from USD 9.0376 pre-order to USD 2.0100 in stock, saving USD 7.0276; the conservative quantity-100 material basis rises by USD 0.2026 per device. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708)
- **`UNI-ROYAL 0402WGF1603TCE`:** Accepted at H1-R2.27. The UNI-ROYAL part preserves 160 kOhm, +/-1%, 0402, the standardized 1/16-W rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. Its official body is 1.00 x 0.50 x 0.35 mm versus the selected Vishay's 1.00 x 0.50 x 0.40 mm, so the verified 0402 land pattern and sandwich clearance do not degrade. The five-device line falls from USD 8.9565 pre-order to USD 0.0130 in stock, saving USD 8.9435; the public material basis falls by USD 0.0131 per device. [JLCPCB](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757)
- **`FH RS-06K47R0FT`:** Accepted at H1-R2.27. The FH part preserves 47 Ohm, +/-1%, 1206, 0.25 W, 200 V, 100 ppm/C and -55 to +155 C. Its official 3.20 x 1.60 x 0.55-mm body is thinner than the selected YAGEO 3.20 x 1.60 x 0.65-mm body and uses the standard 1206 land pattern. The five-device line falls from USD 8.9566 pre-order to USD 0.0310 in stock, saving USD 8.9256; the public material basis falls by USD 0.0108 per device. [JLCPCB](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014)
- **`YAGEO CC0603KRX7R0BB104`:** Accepted at H1-R2.27. The YAGEO part preserves 100 nF, +/-10%, 100 V, 0603/1608, -55 to +125 C and the exact 1.60 x 0.80 x 0.80-mm body. X7R holds capacitance within +/-15% over temperature and is stricter than the former X7S +/-22% class, so the USB VBIAS role does not degrade. The five-device line falls from USD 9.0752 pre-order to USD 0.1300 in stock, saving USD 8.9452; the public material basis falls by USD 0.0266 per device. [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803)
- **`Hirose DF40C(2.0)-40DS-0.4V(51)`:** Accepted at H1-R2.29. Hirose defines (51) and (58) as the same 40-position 0.4-mm receptacle, 10.6 x 3.38 x 1.95-mm body, 2.0-mm mated stack, contacts and ratings; only the factory reel quantity changes from 1,000 to 4,000. C597934 is live JLCPCB Standard-PCBA stock. The five-device line falls from USD 5.3500 to USD 2.7695, saving USD 2.5805; the quantity-100 material basis falls by USD 0.7272 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C597934)
- **`Texas Instruments CSD87313DMS`:** Accepted at H1-R2.29. TI lists DMS and DMST as the same production die, WSON-CLIP DMS 8 package, pin map and electrical limits; DMS is the 2,500-piece large tape-and-reel code and DMST is the 250-piece small tape-and-reel code. C2863848 is live JLCPCB Standard-PCBA stock. The five-device line falls from USD 7.3675 to USD 5.2790, saving USD 2.0885; the quantity-100 material basis falls by USD 0.7084 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C2863848)
- **`Vishay TSOP75238TR`:** Accepted at H1-R2.29. Vishay uses the same final 6.8 x 3.0 x 3.2-mm Heimdall body, contacts and electrical contract for TR and TT; TR changes the tape presentation from top view to side view and the reel quantity from 2,200 to 2,300. C511498 currently covers the five-device trial but not a 100-device run. Before every order, exact stock plus attrition must be covered or pre-ordered, and the CPL rotation/feeder presentation must be approved against the JLCPCB placement preview. The five-device line falls from USD 7.3000 to USD 6.5055, saving USD 0.7945; the quantity-100 material basis falls by USD 0.2369 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C511498)
- **`Murata LQW15AN56NG00D`:** Accepted at H1-R2.29. The Murata G code preserves the LQW15AN 0402 body, 56-nH nominal inductance, Q, 2.8-GHz minimum SRF, 200-mA current and 1.17-Ohm maximum DCR while tightening tolerance from +/-5% to +/-2%. C167482 is live JLCPCB Standard-PCBA stock. The five-device line falls from USD 0.3620 to USD 0.2235, saving USD 0.1385; the quantity-100 material basis falls by USD 0.0277 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C167482)
- **`OMRON B3S-1000P`:** The stocked member preserves the 6.6 x 6.0 x 4.3-mm body, 1.57-N feel, 500k endurance and IP67 family boundary, but removes the fifth cover-ground terminal. That can weaken the user-exposed ESD path, so the current B3S-1100P remains selected until an equivalent grounded stocked part is proven. [JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-B3S1000P/C180420)
- **`HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5`:** The JLCPCB cards prove a 6-GHz standard/reverse pair and the controlled HenryTech drawings prove individual retention without a nut, but both bodies point normal to the PCB. They do not replace the selected edge-facing GCT bodies without changing antenna direction and product form. [JLCPCB](https://jlcpcb.com/partdetail/HenryTech-HL2_SMA_KEP_135/C53278703)
- **`DreamLNK SMA-KWE902 / SMA-KWE901`:** This is a fully documented, no-nut 6-GHz right-angle standard/reverse pair with a stronger through-board soldered load path. Its 9.7-mm body, five drilled pins and approximately 2.1-mm inner-side pin projection on a 1.6-mm PCB change the selected GCT keep-out, but low profile is no longer a product requirement. The live JLCPCB cards on 2026-08-29 show a Plugin/manualWeld route, procurement minima of 13/12 and only overseas/pre-sale availability rather than ordinary SMT stock. It remains the leading mechanical candidate, not an accepted production MPN: all ten placements, opposing clearances and written factory assembly acceptance must pass together. [JLCPCB](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554)
**Accepted rule:** remove avoidable small-lot pre-order first, but replace an MPN only with an exact or no-worse stocked part. RF, power-safety, battery-protection and user-exposed ESD boundaries are not simplified for cost. When no proven equivalent exists, the original MPN and explicit pre-order route remain.

## Cost-reduction queue

1. ▶ **Rebuild the external antenna kit from stocked no-worse equivalents** — Eight of twelve exact first-target antenna profiles already contribute USD 138.3166 per device, while three nRF24 antennas and the controlled AM/LW receive pod remain unpriced. This is the largest separate material group even though it sits outside the base PCBA BOM. Keep every accepted band and all band-specific TX matching. Search the current factory/order surface for exact or no-worse connector, band, power and matching equivalents; optimize receive-only profiles separately and never silently substitute one generic whip for a qualified TX antenna.
2. ✅ **Replace safe equivalent pre-order passives and ordinary logic with in-stock JLCPCB parts** — After six safe replacement batches, 26 pre-order rows cost USD 648.0444 in the normalized five-device evidence versus USD 322.6465 on their quantity-100 material basis. The stocked Nexperia, YAGEO, UNI-ROYAL, FH, Hirose, TI, Vishay and Murata routes together remove approximately USD 137.7020 from the observed trial route and reduce the public material basis by a net USD 3.0885 per device. Review every pre-order row against its substitution class; only exact or no-worse parametric replacements may be accepted.
3. ▶ **Replace the expensive GCT pair with a robust stocked standard/reverse pair if it fits** — Ten GCT RFPC-SMA31/32 connectors contribute USD 24.6456 per device. Low profile is no longer a product requirement; the DreamLNK nutless pair would reduce the line by about USD 19.02 on the common quantity-100 basis, but its through-hole tails, procurement minima and manual factory-soldering route require a new internal keep-out and written assembly acceptance. Optimize for the correct outward antenna direction, standard/RP-SMA identity, at least 6-GHz coverage on native ports and a dual-face or through-board mechanical load path. Accept a replacement only after complete 5+5 placement, opposing-clearance and assembly review.
4. ▶ **Re-evaluate eight RF power detectors without weakening real-TX evidence** — Six AD8314 plus two LTC5532 contribute USD 24.9174 per device on the common quantity-100 basis; the historical live five-device requirement is USD 276.70. Stocked same-device AD8314ARMZ-REEL C652687 would save USD 88.99 on that historical EVT5 snapshot and USD 5.4864 per finished device on the same quantity-100 basis. No strict no-worse LTC5532 replacement is proved. Register and collision-check all six larger MSOP courtyards, adjacent match/bypass bodies and RF-ground fanout before accepting C652687. Keep the two LTC5532 and independent evidence for the three concurrently active nRF24 paths.
5. ⏳ **Find one serial in-stock tact-switch family for all sixteen ordinary controls** — B3S-1100P contributes USD 10.248 per device at quantity 100 and USD 74.58 for 80 pieces in the five-device pre-order route. The first stocked candidate was rejected because it removes the grounded cover terminal. Preserve footprint/enclosure reach, force, height, endurance, the ESD boundary and recessed actuation.
6. ✅ **Retain all five U.FL plus 30-mm jumper paths after source-to-port review** — The five paths contribute USD 14.433 per device at quantity 100, before assembly handling. S3 and all three E01 modules expose only microcoax RF outputs, and each path must still pass through its local coupler and real-TX detector before SMA. The current C5 module also exposes U.FL; an exact stocked Espressif T2/ANT2 factory route is not proved. Therefore 0/5 paths can be removed safely now. A future qualified C5 T2 route could remove one path and save about USD 2.89 per device.
7. ⏳ **Compare the 1048P holder with serial cell contacts captured by the enclosure cradle** — 1048P contributes USD 8.57 per device at quantity 100 and is currently stock-zero pre-order at JLCPCB. Any replacement must keep protected-cell length tolerance, polarity, insertion cycles and a non-peeling enclosure load path.
8. ⏳ **Replace three premium DBG10 headers with an equally keyed serial factory-stocked family** — Three Samtec FTSH headers contribute USD 5.0973 per device and exist only as opened-sandwich recovery fallbacks. Preserve independent S3/C5/RP recovery, keying, pitch, probe access and the internal height envelope.
9. ✅ **Do not optimize away the selected serial production panel** — EastRising ER-TFT035IPS-6 plus ER-TPC035-6 contributes USD 14.91 and already provides a controlled drawing, ILI9488/FT6236, direct i8080-8 and quantity-one serial ordering. The donor route is gone. Treat the display material cost as justified. Only the assembler fee and written acceptance of panel/FPC final mating remain open; do not restart display selection for a small speculative saving.

## Display and flex orientation

- Exact EastRising drawings control the complete panel body, 50-contact FPC, 0.50-mm pitch, 0.30-mm stiffener and contact map; donor-board geometry is no longer used.
- The panel is physically oriented **with its flex toward the antenna edge**, while ILI9488 display memory and FT6236 touch coordinates rotate in firmware. The tail stays out of the LED, D-pad and function-key zone.
- The accepted upper adapter PCB position `[22.25, 1.0]` passes the current exact-body model: `0` same-face collisions and `2.6 mm` minimum opposing clearance versus `0.7 mm` required, with no GPIO or BOM change.
- H1 fixes the orientation and replaceable adapter; only written factory acceptance of panel/FPC work and incoming-lot conformity remain open.

> Marker: **H1-R2.35**. H1 remains open pending the complete mock-up decision.
