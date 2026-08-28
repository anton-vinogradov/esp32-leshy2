# H1-R2.30 · component cost ranking

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

This is a ranked snapshot of the current hardware, not a commercial quote. Every line burden includes the quantity fitted to one device; the trial columns use five devices and preserve observed JLCPCB MOQ/pre-order effects.

## Summary

- Volume material basis: **$235.35** per device; `199/210` lines are priced.
- Reachable planning subtotal: **$284.66** per device, with `5` base-product lines still unpriced.
- With the required post-PCBA K331: **$314.65** per device or **$1,573.25** for five devices before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.
- Partial five-device JLCPCB capture: **$1,234.40** for `180` matched lines; `22` live checks move it to **$1,300.42**, with `30` rows excluded.
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
| `Murata GRM32ER71E226KE15L` | thirteen 22-uF power capacitors / тринадцать силовых конденсаторов 22 мкФ | 13 | $0.33 | $4.29 | 65 | $21.47 | $31.67 |
| `ESP32-C5-WROOM-1U-N8R8` | c5 | 1 | $4.13 | $4.13 | 5 | $20.67 | $29.29 |
| `Texas Instruments TPD4E05U06DQAR` | thirteen four-line ESD arrays / тринадцать четырёхканальных ESD-сборок | 13 | $0.31 | $4.02 | 65 | $20.09 | — |
| `Analog Devices MAX17320G20+T` | pack_gauge | 1 | $4.00 | $4.00 | 5 | $20.01 | $31.06 |

[Complete 210-line ranking — CSV](../hardware/product-design/generated/H1-R2-cost-ranked.csv)

## Where the small batch overpays

- The `26` pre-order rows cost **$648.04** in the capture versus **$322.65** on their volume material basis.
- The observed small-lot premium is **$325.40**. This is the first priority: seek stocked JLCPCB MPNs that remain inside the existing substitution envelopes.
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
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `DreamLNK SMA-KWE902 / SMA-KWE901` | `C914554 / C914553` | 5594 standard / 64 reverse | `rejected_high_profile_tht_form_change` |

- **`ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2`:** Accepted at H1-R2.28 without changing the official Espressif MPN, 8-MiB flash, 8-MiB PSRAM, module body, land pattern or antenna connector. The JLC suffix is a supplier order code only. C54951858 is the active stocked Standard-PCBA route; historical zero-stock C51950748 is forbidden as active. Production requires incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed. The quantity-100 material basis falls from USD 4.3700 to USD 4.1338 per device, while the five-device live line is USD 29.2935. [JLCPCB](https://jlcpcb.com/partdetail/C54951858)
- **`Nexperia 74LVC2G126DP,125`:** Accepted at H1-R2.23. DP and DC are package variants of the same current Nexperia 74LVC2G126 family and preserve logic, pin order, Schmitt inputs, Ioff and timing. The larger TSSOP bodies pass the regenerated placement audit. The five-device line falls from the observed USD 40.60 pre-order route to USD 12.1425 in stock; the quantity-100 unit tier rises from the former external USD 0.2086 basis to JLCPCB USD 0.3753. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392)
- **`Analog Devices AD8314ARMZ-REEL`:** Analog Devices lists ACPZ-RL7 and ARMZ-REEL as production package variants of the same AD8314 specification with the same pins 1-8 and electrical behavior. C652687 is live JLCPCB stock. Thirty trial parts cost USD 70.56 instead of the current C578691 live requirement of USD 159.55, saving USD 88.99; 600 parts cost USD 1,097.40, reducing the six-device line from USD 17.142 to USD 10.974 per finished device. This is not accepted into the production BOM yet: MSOP grows from the 2 x 3-mm LFCSP body to a roughly 3 x 3-mm body with up to 5.15-mm lead span and 1.10-mm height, and removes the exposed pad. All six exact courtyards, adjacent RF match/bypass bodies and RF-ground fanout must pass the H1 placement and route audit first. [JLCPCB](https://jlcpcb.com/partdetail/AD8314ARMZ-REEL/C652687)
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
- **`DreamLNK SMA-KWE902 / SMA-KWE901`:** This is a fully documented, stocked, no-nut 6-GHz right-angle standard/reverse pair, but its approximately 10.2-mm board profile and through-hole tails replace the 3.9-mm GCT edge-launch envelope. On the front board the connector axis would sit roughly 7 mm above the display glass and the tails would enter the sandwich. The saving is real but not functionally or mechanically neutral. [JLCPCB](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554)
**Accepted rule:** remove avoidable small-lot pre-order first, but replace an MPN only with an exact or no-worse stocked part. RF, power-safety, battery-protection and user-exposed ESD boundaries are not simplified for cost. When no proven equivalent exists, the original MPN and explicit pre-order route remain.

## Cost-reduction queue

1. ✅ **Replace safe equivalent pre-order passives and ordinary logic with in-stock JLCPCB parts** — After six safe replacement batches, 26 pre-order rows cost USD 648.0444 in the normalized five-device evidence versus USD 322.6465 on their quantity-100 material basis. The stocked Nexperia, YAGEO, UNI-ROYAL, FH, Hirose, TI, Vishay and Murata routes together remove approximately USD 137.7020 from the observed trial route and reduce the public material basis by a net USD 3.0885 per device. Review every pre-order row against its substitution class; only exact or no-worse parametric replacements may be accepted.
2. ✅ **Retain the low-profile GCT edge-launch pair unless a truly equivalent stocked pair appears** — The selected GCT RFPC-SMA31/32 pair preserves the 3.9-mm edge-launch envelope, but the official GCT set includes an individual panel nut and washer; no nutless GCT sibling was found. HenryTech points normal to the PCB, while the stocked nutless DreamLNK pair would save about USD 19.01 per device but raises the connector axis roughly 6.3 mm and adds through-hole tails inside the sandwich. Keep the GCT pair with no shared frame; safe connector saving is currently USD 0. Reopen only for a stocked standard/reverse edge-launch pair rated to at least 6 GHz with equal or lower profile and a controlled 1.6-mm PCB drawing.
3. ▶ **Re-evaluate eight RF power detectors without weakening real-TX evidence** — Six AD8314 plus two LTC5532 contribute USD 24.9174 per device at quantity 100; the live five-device requirement is USD 276.70. Stocked same-device AD8314ARMZ-REEL C652687 would save USD 88.99 on EVT5 and USD 6.168 per finished device at a 100-device run. No strict no-worse LTC5532 replacement is proved. Register and collision-check all six larger MSOP courtyards, adjacent match/bypass bodies and RF-ground fanout before accepting C652687. Keep the two LTC5532 and independent evidence for the three concurrently active nRF24 paths.
4. ⏳ **Find one serial in-stock tact-switch family for all sixteen ordinary controls** — B3S-1100P contributes USD 10.248 per device at quantity 100 and USD 74.58 for 80 pieces in the five-device pre-order route. The first stocked candidate was rejected because it removes the grounded cover terminal. Preserve footprint/enclosure reach, force, height, endurance, the ESD boundary and recessed actuation.
5. ✅ **Retain all five U.FL plus 30-mm jumper paths after source-to-port review** — The five paths contribute USD 14.433 per device at quantity 100, before assembly handling. S3 and all three E01 modules expose only microcoax RF outputs, and each path must still pass through its local coupler and real-TX detector before SMA. The current C5 module also exposes U.FL; an exact stocked Espressif T2/ANT2 factory route is not proved. Therefore 0/5 paths can be removed safely now. A future qualified C5 T2 route could remove one path and save about USD 2.89 per device.
6. ⏳ **Compare the 1048P holder with serial cell contacts captured by the enclosure cradle** — 1048P contributes USD 8.57 per device at quantity 100 and is currently stock-zero pre-order at JLCPCB. Any replacement must keep protected-cell length tolerance, polarity, insertion cycles and a non-peeling enclosure load path.
7. ⏳ **Replace three premium DBG10 headers with an equally keyed serial factory-stocked family** — Three Samtec FTSH headers contribute USD 5.0973 per device and exist only as opened-sandwich recovery fallbacks. Preserve independent S3/C5/RP recovery, keying, pitch, probe access and the internal height envelope.
8. ⏳ **Obtain the standalone panel route instead of consuming a complete donor per device** — The current reachable DLE06235B donor is USD 20.90 per display, while standalone HMX035CTFT-001 price and production identity remain open. Keep the replaceable adapter and treat the donor as an EVT ceiling, not production COGS.

## Display and flex orientation

- The official complete-donor rear view does show a folded FPC and rear ZIF, but it does not disclose the standalone raw `HMX035CTFT-001` outline, length or contact side.
- The correct rule is to physically orient the panel **with its flex toward the antenna edge**, then rotate display memory and touch coordinates in firmware. The tail then stays out of the LED, D-pad and function-key zone.
- The accepted upper adapter PCB position `[24.75, 1.0]` passes the current exact-body model: `0` same-face collisions and `5.1 mm` minimum opposing clearance versus `0.7 mm` required, with no GPIO or BOM change.
- H1 now fixes this orientation; H5 qualifies the received flex, bend and retention on the replaceable adapter. A mismatch cannot silently return the tail to the control zone.

> Marker: **H1-R2.30**. H1 remains open pending the complete mock-up decision.
