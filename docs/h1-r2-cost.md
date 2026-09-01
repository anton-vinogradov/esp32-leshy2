# H1-R2.38 · component cost ranking

[Русский](h1-r2-cost.ru.md) · [English](h1-r2-cost.md) · [Current placement](h1-r2-physical-layout.md)

This is a ranked snapshot of the current hardware, not a commercial quote. Every line burden includes the fitted quantity in the target one fully assembled prototype. Identical MPNs are grouped into one row; the historical five-board BOM Tool capture remains below only as MOQ/pre-order evidence, not the procurement target.

## Summary

- Volume material basis: **$252.10** per device; `201/210` lines are priced.
- Reachable planning subtotal: **$271.90** per device, with `5` base-product lines still unpriced.
- Current planned component minimum with no mandatory post-PCBA active module: **$271.90** per device and **$271.90** for the one target prototype before PCB/PCBA, enclosure, antennas, freight, tax, yield and test.
- The same accepted price basis scales linearly to **$2,719.03** for ten devices. This compares groups; it is not a batch quote.
- The top 10 / 20 / 40 groups contribute **40.38% / 57.78% / 76.49%** of the known base BOM.
- Historical five-board JLCPCB capture: **$1,365.05** for `182` matched lines; `24` live checks move it to **$1,406.44**, with `28` rows excluded. This is evidence, not the target quantity.
- The external antenna kit is separate: **$138.32** is known and `4` positions in `2` MPN groups remain unpriced. The known electronics plus known antennas already reach **$410.22** before PCB/PCBA, enclosure and freight.

## Accepted all-in-one cost boundary

- The current product remains a fully populated all-in-one. Its repeatable complete-device target is **$220.00–$260.00**, excluding batteries and the full specialized external-antenna kit.
- To leave room for PCB, PCBA and enclosure, electronics must land near **$189.00–$216.00**.
- The current base BOM has `208` MPN groups and `1094` fitted components. The accepted no-function-loss AD8314 and Hirose U.FL routes already save **$10.42** and leave the exact current planning floor at **$271.90**. The cheaper SMA/RP-SMA pair was checked and rejected, so its hypothetical saving is not counted.
- A further **$55.90–$82.90** must be removed to reach the electronics band. The formal margin to the complete-device ceiling is only **$-11.90**, so boards, assembly and enclosure do not fit without further resynthesis.

**Accepted:** no separate `Core` is designed now. One fully populated `R2-EVT1` is built and verified first; implementation cost is reduced without removing built-in functions or the safety outcome. The historical `$150` goal is deferred as a possible post-EVT1 community fit option, not a current hardware branch. The sole first order will still cost more because MOQ, setup, manual placement, freight and tax cannot be amortized.

### Why ESP32-DIV is much cheaper

The official [ESP32-DIV v2 architecture](https://github.com/cifertech/ESP32-DIV/tree/9d4d82fe7a12febf554b12e1eca6d434ebe79d39) is much smaller: one S3, three nRF24 modules, one CC1101, IR and a simple connector/passive layer. Its public shield BOM does not contain two voice modules, an Airband conversion chain, two RP domains, three independent service-USB paths, autonomous pack safety, physical actual-TX evidence or ten separately qualified RF ports. Retail volume also amortizes setup and purchasing minima, while this review must survive a sole first order.

That does not mean Leshy2 must cost eight times as much. It means the current architecture pays not only for functions, but also for laboratory observability, independent recovery and fail-safe supervision around nearly every path.

### Feasibility without losing the result

| Boundary | Electronics | Complete base | Honest result |
|---|---:|---:|---|
| Current circuit | $271.90 | above $271.90 | already above the accepted ceiling before boards, assembly and enclosure |
| After the accepted AD8314 and Hirose U.FL changes | $271.90 | above $271.90 | exact current planning floor; still insufficient |
| Same built-in user functions and same safety outcome after full cost resynthesis | $214.00–$235.00 | $241.00–$280.00 | only the upper portion overlaps the `$220–260` target |
| Modular community base; specialist paths are fitted as task-specific Caps/Units | $108.00–$125.00 | $135.00–$165.00 | deferred until a working `R2-EVT1`; there is no separate Core now |

The `$214–235` and `$241–280` bands are not price promises: they assume successful remaining RF-evidence, audio/safety and internal-RF resynthesis without changing the result. Controls, holder and recovery headers have now been checked and retained, so their former assumed saving is removed. The lower part of the `$220–260` target is not yet demonstrated.

The full antenna kit is an accessory, not a hidden device-price line. A broadband receive antenna cannot replace band-matched transmit antennas; the basic kit and additional band-specific antennas must be priced separately.

The primary ranking below shows **one prototype only**. It contains neither the historical five-board capture nor a ×10 multiplication.

## Unified top 20: electronics and external antennas

| № | Source | MPN and role | Qty ×1 | Unit on accepted basis | Group ×1 | Share of known total |
|---:|---|---|---:|---:|---:|---:|
| 1 | Antenna | `SMA-W100RX2`<br><sub>receive-only telescopic whip; AIR</sub> | 1 | $35.95 | $35.95 | 8.76% |
| 2 | Antenna | `001-0012`<br><sub>2.4/5 GHz native radio; S3, C5</sub> | 2 | $16.91 | $33.82 | 8.24% |
| 3 | Antenna | `AN0155H13`<br><sub>VHF 136-174 MHz; VHF</sub> | 1 | $31.70 | $31.70 | 7.73% |
| 4 | Antenna | `ANT-433-CW-QW-SMA`<br><sub>433 MHz / UHF 400-470 MHz; S433, UHF</sub> | 2 | $11.23 | $22.46 | 5.47% |
| 5 | Base BOM | `GCT RFPC-SMA31-FN-175-A`<br><sub>eight standard outward SMA / восемь внешних SMA</sub> | 8 | $2.46 | $19.72 | 4.81% |
| 6 | Base BOM | `EastRising ER-TFT035IPS-6 + ER-TPC035-6`<br><sub>display</sub> | 1 | $14.91 | $14.91 | 3.63% |
| 7 | Base BOM | `Analog Devices AD8314ARMZ-REEL`<br><sub>six real-TX RF detectors / шесть RF-детекторов фактической передачи</sub> | 6 | $1.94 | $11.64 | 2.84% |
| 8 | Base BOM | `OMRON B3S-1100P`<br><sub>sixteen ordinary user keys / шестнадцать обычных клавиш</sub> | 16 | $0.64 | $10.25 | 2.50% |
| 9 | Base BOM | `G-NiceRF SA818S-V`<br><sub>VHF voice transceiver / VHF голосовой трансивер</sub> | 1 | $10.07 | $10.07 | 2.46% |
| 10 | Base BOM | `G-NiceRF SA818S-U`<br><sub>UHF voice transceiver / UHF голосовой трансивер</sub> | 1 | $9.73 | $9.73 | 2.37% |
| 11 | Antenna | `ANT-315-CW-HW-SMA`<br><sub>315 MHz; S315</sub> | 1 | $9.60 | $9.60 | 2.34% |
| 12 | Base BOM | `Ebyte E01-ML01SP4`<br><sub>three 20-dBm PA/LNA full-function nRF24 radios / три полнофункциональных nRF24 с PA/LNA 20 dBm</sub> | 3 | $2.96 | $8.89 | 2.17% |
| 13 | Base BOM | `Keystone Electronics 1048P`<br><sub>dual protected-18650 holder / держатель двух защищённых 18650</sub> | 1 | $8.57 | $8.57 | 2.09% |
| 14 | Base BOM | `Texas Instruments TMUX1136DGSR`<br><sub>four complete audio/control selectors / четыре полных audio/control selector</sub> | 4 | $2.06 | $8.23 | 2.01% |
| 15 | Base BOM | `LTC5532ES6#TRMPBF`<br><sub>S3/C5 2.4/5-GHz TX detectors / детекторы TX S3/C5 2,4/5 ГГц</sub> | 2 | $3.89 | $7.78 | 1.90% |
| 16 | Base BOM | `Samtec FTSH-105-01-L-DV-K-P-TR`<br><sub>four internal recovery headers / четыре внутренних recovery-разъёма</sub> | 4 | $1.70 | $6.80 | 1.66% |
| 17 | Base BOM | `TE Connectivity 1-2118651-0`<br><sub>three 60-mm nRF RF jumpers / три 60-мм RF-кабеля nRF</sub> | 3 | $1.81 | $5.43 | 1.32% |
| 18 | Base BOM | `ESP32-S3-WROOM-1U-N16R8`<br><sub>s3</sub> | 1 | $5.11 | $5.11 | 1.25% |
| 19 | Base BOM | `GCT RFPC-SMA32-FN-175-A`<br><sub>two native-radio RP-SMA / два RP-SMA native-радио</sub> | 2 | $2.46 | $4.93 | 1.20% |
| 20 | Antenna | `TI.08.C.0112`<br><sub>868/915 MHz; S915</sub> | 1 | $4.79 | $4.79 | 1.17% |

[Unified top 20 — CSV](../hardware/product-design/generated/H1-R2-cost-top20.csv) · [Complete 210-line ranking — CSV](../hardware/product-design/generated/H1-R2-cost-ranked.csv)

## Critical mass-market audit of the complete top 20

All 20 current groups were checked and **all 20 are retained**. Six cheaper antenna candidates were rejected by the `2026-08-30` decision: their combined paper saving of **$89.13** remains comparison evidence only and is neither an active qualification route nor a BOM substitution.

| # | Current group | Best mass-market route | Status | Saving up to |
|---:|---|---|---|---:|
| 1 | [`SMA-W100RX2`](https://www.comet-ant.co.jp/product/638/) | [Opek SCANSMA 25-1300](https://www.hamradio.com/detail.cfm?pid=H0-016713) | ✅ retain · candidate rejected | $20.00 |
| 2 | [`001-0012`](https://www.te.com/en/product-001-0012.html) | [split the group: TE 001-0001 for S3 2.4 GHz; Taoglas GW.05.0153 for C5 2.4/5 GHz](https://www.taoglas.com/datasheets/GW.05.0153.pdf) | ✅ retain · candidate rejected | $19.30 |
| 3 | [`AN0155H13`](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h13.html) | [Powerwerx ANT-8](https://powerwerx.com/vhf-uhf-dual-band-standard-sma-antenna) | ✅ retain · candidate rejected | $23.93 |
| 4 | [`ANT-433-CW-QW-SMA`](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html) | [Ebyte TX433-JZR-6 for UHF plus TX433-JK-11 for the narrow 433-MHz port](https://www.ebyte.com/product/824.html) | ✅ retain · candidate rejected | $19.57 |
| 5 | [`GCT RFPC-SMA31-FN-175-A`](https://www.digikey.com/en/products/detail/gct/RFPC-SMA31-FN-175-A/17833784) | [retain current GCT standard-SMA body](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554) | ✅ retain | $0.00 |
| 6 | [`EastRising ER-TFT035IPS-6 + ER-TPC035-6`](https://www.buydisplay.com/3-5-inch-tft-lcd-display-capacitive-touch-screen-ips-320x480) | [retain the documented EastRising panel and touch pair](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf) | ✅ retain | $0.00 |
| 7 | [`Analog Devices AD8314ARMZ-REEL`](https://jlcpcb.com/partdetail/AnalogDevices-AD8314ARMZREEL/C652687) | [retain accepted C652687 MSOP route](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8314.pdf) | ✅ retain | $0.00 |
| 8 | [`OMRON B3S-1100P`](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3S-1100P/60835) | [retain B3S-1100P; source by JLC pre-order/consignment if necessary](https://jlcpcb.com/partdetail/OmronElectronicComponents-B3S1100P/C2733652) | ✅ retain | $0.00 |
| 9 | [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | [retain exact SA818S-V C51897911](https://www.nicerf.com/walkie-talkie-module-sa818s.html) | ✅ retain | $0.00 |
| 10 | [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | [retain SA818S-U C3001549](https://www.nicerf.com/walkie-talkie-module-sa818s.html) | ✅ retain | $0.00 |
| 11 | [`ANT-315-CW-HW-SMA`](https://www.te.com/en/product-ANT-315-CW-HW-SMA.html) | [Joymax UHX-328ASA2B](https://www.digikey.com/en/products/detail/joymax-electronics/UHX-328ASA2B/28334978) | ✅ retain · candidate rejected | $4.03 |
| 12 | [`Ebyte E01-ML01SP4`](https://jlcpcb.com/partdetail/E01-ML01SP4/C97340) | [retain JLCPCB C97340](https://www.ebyte.com/product/1200.html) | ✅ retain | $0.00 |
| 13 | [`Keystone Electronics 1048P`](https://www.digikey.com/en/products/detail/keystone-electronics/1048P/4499417) | [retain 1048P; use reviewed factory sourcing/consignment route](https://jlcpcb.com/partdetail/KeystoneElectronics-1048P/C6038062) | ✅ retain | $0.00 |
| 14 | [`Texas Instruments TMUX1136DGSR`](https://jlcpcb.com/partdetail/TexasInstruments-TMUX1136DGSR/C2673301) | [retain TMUX1136DGSR C2673301](https://www.ti.com/lit/ds/symlink/tmux1136.pdf) | ✅ retain | $0.00 |
| 15 | [`LTC5532ES6#TRMPBF`](https://jlcpcb.com/partdetail/AnalogDevices-LTC5532ES6TRMPBF/C580926) | [retain LTC5532; exact-one needs two and current stock covers it](https://www.analog.com/media/en/technical-documentation/data-sheets/5532f.pdf) | ✅ retain | $0.00 |
| 16 | [`Samtec FTSH-105-01-L-DV-K-P-TR`](https://jlcpcb.com/partdetail/Samtec-FTSH_105_01_L_DV_K_PTR/C2932107) | [retain JLCPCB C2932107](https://www.tag-connect.com/product/tc2050-idc-nl-10-pin-no-legs-cable-with-ribbon-connector) | ✅ retain | $0.00 |
| 17 | [`TE Connectivity 1-2118651-0`](https://www.te.com/en/product-1-2118651-0.html) | [retain exact 60-mm 1.37-mm-max U.FL-to-U.FL jumper](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/1-2118651-0/12380462) | ✅ retain | $0.00 |
| 18 | [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/EspressifSystems-ESP32S3WROOM1UN16R8/C3013946) | [retain exact N16R8 external-antenna module](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | ✅ retain | $0.00 |
| 19 | [`GCT RFPC-SMA32-FN-175-A`](https://www.digikey.com/en/products/detail/gct/RFPC-SMA32-FN-175-A/17833785) | [retain current GCT reverse-polarity body](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE901/C914553) | ✅ retain | $0.00 |
| 20 | [`TI.08.C.0112`](https://www.taoglas.com/datasheets/TI.08.C.0112.pdf) | [Seeed Studio 113070002 868/915-MHz whip](https://www.seeedstudio.com/External-Antenna-868-915MHZ-2dBi-SMA-L195mm-Foldable-p-5863.html) | ✅ retain · candidate rejected | $2.30 |

Why the six alternatives were rejected:

- **`SMA-W100RX2` → Opek SCANSMA 25-1300:** same stated 25-1300-MHz receive range, but it is a remote magnetic-mount antenna with 12-ft RG-174 rather than a direct telescopic whip (in stock at Ham Radio Outlet; USD 15.95)
- **`001-0012` → split the group: TE 001-0001 for S3 2.4 GHz; Taoglas GW.05.0153 for C5 2.4/5 GHz:** S3 does not use 5 GHz, so its dual-band/IP67 capability is unused; C5 candidate begins at 5150 rather than 4910 MHz and both substitutions require assembled-device matching/EIRP closure (001-0001: 2,656 Mouser stock; GW.05.0153: distributor stock and serial order route)
- **`AN0155H13` → Powerwerx ANT-8:** covers 136-174 and 400-470 MHz with standard SMA, but its public page does not close gain, VSWR, power or exact mechanical seating; it may cover both voice ports only after VNA and voice-TX HIL (in stock; USD 7.77)
- **`ANT-433-CW-QW-SMA` → Ebyte TX433-JZR-6 for UHF plus TX433-JK-11 for the narrow 433-MHz port:** UHF candidate preserves 400-480 MHz, 10 W and improves stated VSWR but nominal gain falls 3.3 to 3.0 dBi; the 433 candidate is narrow-band and both need VNA/EIRP HIL (both serial Ebyte parts available from stocked distributors; TX433-JZR-6 observed at USD 1.72)
- **`ANT-315-CW-HW-SMA` → Joymax UHX-328ASA2B:** candidate is 312-317 rather than 304-325 MHz, -0.4 rather than 0 dBi and 1 W; adequate only for the exact 315-MHz profile after VNA/TX HIL (958 DigiKey stock; USD 5.5693 at 100)
- **`TI.08.C.0112` → Seeed Studio 113070002 868/915-MHz whip:** candidate preserves both bands, SMA and 10 W but changes right-angle mechanics and falls from 2.48 to 2.0 dBi at 868 MHz; both regional EIRP limits require HIL (in stock; USD 2.49)

[Complete audit and evidence — CSV](../hardware/product-design/generated/H1-R2-top20-market-audit.csv)

## Most likely unjustified-cost candidates

| Priority | Group | Current ×1 | Finding | Realistic saving |
|---:|---|---:|---|---:|
| 1 | External antennas | $138.32 + 4 unknown | Largest separate group; the functions are required, but the first branded MPNs need not be the best-value equivalents | to be established |
| 2 | 10 outward SMA/RP-SMA | $24.65 | Cheaper standard/reverse pairs were checked and fail orientation, 5+5 geometry or the exact-one factory route. GCT remains justified | $0 proven |
| 3 | 8 RF detectors | $19.41 | Six AD8314 are already moved to C652687 after the complete placement audit; function and all eight evidence paths are retained | $5.50 accepted |
| 4 | 5 U.FL plus 5 cables | $9.48 | The Hirose packaging route is already reduced without loss; only a proven C5 T2 route can remove one path | up to ~$1.90 more |
| 5 | 16 user buttons | $10.25 | Checked cheaper candidates weaken ESD, feel or evidence; the current group is justified | $0 |
| 6 | Dual-18650 holder | $8.57 | Stocked single-cell bodies do not prove the complete protected-cell and polarity contract; 1048P is justified | $0 |
| 7 | 4 internal DBG10 headers | $6.80 | Exact Samtec is stocked; Tag-Connect costs more for the sole EVT1 and weakens long-session ergonomics | $0 for EVT1 |

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

| Scope | Previous position | Verified position | JLCPCB | Orderable | Status |
|---|---|---|---|---:|---|
| ESP32-C5 production supplier route and revision floor | `ESP32-C5-WROOM-1U-N8R8 / historical C51950748` | `ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2` | `C54951858` | 440 | `accepted_stocked_supplier_route_identity_normalization` |
| dual Ioff return buffers | `Nexperia 74LVC2G126DC,125` | `Nexperia 74LVC2G126DP,125` | `C503392` | 155 | `accepted_stocked_exact_family_package_variant` |
| six AD8314 real-TX evidence detectors | `Analog Devices AD8314ACPZ-RL7` | `Analog Devices AD8314ARMZ-REEL` | `C652687` | 2977 | `accepted_same_device_msop_explicit_factory_route_and_physical_fit` |
| five native/module U.FL receptacles | `Hirose U.FL-R-SMT-1(10)` | `Hirose U.FL-R-SMT-1(80)` | `C88374` | 68798 | `accepted_stocked_exact_packaging_variant` |
| all 100-nF 50-V X7R 0402 bypass positions | `TDK C1005X7R1H104K050BB` | `YAGEO CC0402KRX7R9BB104` | `C131394` | 7796754 | `accepted_stocked_exact_parametric_replacement` |
| six ordinary 0402 resistor identities across 28 positions | `YAGEO RC0402FR-072K2L / 07133KL / 07270KL / 075K23L / 078K2L / 071K65L` | `UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE` | `C25879 / C25753 / C25770 / C25907 / C25924 / C25869` | 2027222 / 6692 / 156208 / 40861 / 234262 / 5616 | `accepted_stocked_exact_parametric_replacements` |
| two dual Schmitt inverters | `Nexperia 74LVC2G14GW,125` | `Nexperia 74LVC2G14GV,125` | `C426708` | 35 | `accepted_stocked_exact_family_package_variant` |
| codec transmit attenuator top resistor | `Vishay CRCW0402160KFKED` | `UNI-ROYAL 0402WGF1603TCE` | `C25757` | 388017 | `accepted_stocked_exact_parametric_replacement` |
| IR emitter current-limit resistor | `YAGEO RC1206FR-0747RL` | `FH RS-06K47R0FT` | `C140014` | 78058 | `accepted_stocked_exact_parametric_replacement` |
| 100-nF 100-V USB VBIAS capacitor | `TDK C1608X7S2A104K080AB` | `YAGEO CC0603KRX7R0BB104` | `C113803` | 1027658 | `accepted_stocked_no_worse_parametric_replacement` |
| dual common-drain pack-protection MOSFET | `Texas Instruments CSD87313DMST` | `Texas Instruments CSD87313DMS` | `C2863848` | 4741 | `accepted_stocked_exact_packaging_variant` |
| robust 38-kHz demodulating IR receiver | `Vishay TSOP75238TT` | `Vishay TSOP75238TR` | `C511498` | 15 | `accepted_stocked_exact_tape_presentation_variant_with_placement_gate` |
| Si4732 FMI 56-nH high-Q matching inductor | `Murata LQW15AN56NJ00D` | `Murata LQW15AN56NG00D` | `C167482` | 20744 | `accepted_stocked_no_worse_parametric_replacement` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `OMRON B3S-1000P` | `C180420` | 3254 | `not_accepted_missing_ground_terminal` |
| sixteen ordinary user controls | `OMRON B3S-1100P` | `BZCN TSG002A04526A` | `C2888613` | 440 | `not_accepted_heavier_force_ground_and_exact_life_unresolved` |
| dual protected-button-top 18650 retention | `Keystone Electronics 1048P` | `MYOUNG BH-18650-B1BA002` | `C2988620` | 995 | `not_accepted_single_cell_and_protected_length_unproven` |
| four independent opened-sandwich recovery endpoints | `Samtec FTSH-105-01-L-DV-K-P-TR` | `Tag-Connect TC2050-IDC board footprint` | `not applicable; bare PCB pads and locating holes` | official cable available | `not_accepted_for_exact_one_evt1_cost_and_debug_ergonomics` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5` | `C53278703 / C53278707` | 67 standard / 133 reverse | `rejected_wrong_board_normal_orientation` |
| ten outward antenna connectors | `GCT RFPC-SMA31-FN-175-A / RFPC-SMA32-FN-175-A` | `DreamLNK SMA-KWE902 / SMA-KWE901` | `C914554 / C914553` | 5479 pre-sale + 5588 overseas standard / 7 pre-sale + 42 overseas reverse | `rejected_current_5_plus_5_mechanical_envelope_and_factory_route` |

- **`ESP32-C5-WROOM-1U-N8R8 / supplier code ESP32-C5-WROOM-1U-N8R8-V1.2`:** Accepted at H1-R2.28 without changing the official Espressif MPN, 8-MiB flash, 8-MiB PSRAM, module body, land pattern or antenna connector. The JLC suffix is a supplier order code only. C54951858 is the active stocked Standard-PCBA route; historical zero-stock C51950748 is forbidden as active. Production requires incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed. The quantity-100 material basis falls from USD 4.3700 to USD 4.1338 per device, while the five-device live line is USD 29.2935. [JLCPCB](https://jlcpcb.com/partdetail/C54951858)
- **`Nexperia 74LVC2G126DP,125`:** Accepted at H1-R2.23. DP and DC are package variants of the same current Nexperia 74LVC2G126 family and preserve logic, pin order, Schmitt inputs, Ioff and timing. The larger TSSOP bodies pass the regenerated placement audit. The five-device line falls from the observed USD 40.60 pre-order route to USD 12.1425 in stock; the quantity-100 unit tier rises from the former external USD 0.2086 basis to JLCPCB USD 0.3753. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392)
- **`Analog Devices AD8314ARMZ-REEL`:** Accepted at H1-R2.36. Analog Devices specifies ARMZ-REEL and ACPZ-RL7 as package variants of the same AD8314 function with identical numbered contacts 1-8; RM-8 simply has no exposed paddle. JLCPCB C652687 is Extended SMT for Standard PCBA with an explicit 2,977-piece pre-order/overseas route, 2,978 overseas pieces and MOQ 4; the exact-one device needs six. All six 5.15 x 3.20 x 1.10-mm full lead envelopes, the two retained LTC5532 detectors, all five couplers and eight bounded local evidence islands now pass collision, compression-stop and opposing-board audits. The quantity-100 line falls from USD 17.1420 to USD 11.6388, saving USD 5.5032 per device without deleting evidence. [JLCPCB](https://jlcpcb.com/partdetail/AnalogDevices-AD8314ARMZREEL/C652687)
- **`Hirose U.FL-R-SMT-1(80)`:** Accepted at H1-R2.37. Hirose lists (01), (60) and (80) as order presentations of the same U.FL-R-SMT-1 receptacle with the same contacts, 2.6 x 2.6 x 1.25-mm body, land pattern and 6-GHz/50-Ohm rating; only packaging changes. C88374 is live JLCPCB SMT stock for Economic and Standard PCBA. Five fitted receptacles fall from USD 5.3275 to USD 0.4115 on the common quantity-100 basis, saving USD 4.9160 without a PCB, RF or firmware change. [JLCPCB](https://jlcpcb.com/partdetail/U.FL-R-SMT-1%2880%29/C88374)
- **`YAGEO CC0402KRX7R9BB104`:** Accepted at H1-R2.24. The YAGEO part preserves 100 nF, 50 V, X7R, +/-10%, 0402/1005, -55 to +125 C and the exact 1.0 x 0.5 x 0.5-mm body. The JLCPCB route is MOQ 1 and stocked for Standard PCBA. The five-device line falls from the observed USD 22.5624 TDK pre-order charge to USD 5.9535 in stock, saving USD 16.6089; the quantity-100 material basis falls by USD 2.2197 per device. [JLCPCB](https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394)
- **`UNI-ROYAL 0402WGF2201TCE / 1333TCE / 2703TCE / 5231TCE / 8201TCE / 1651TCE`:** Accepted at H1-R2.26. Every replacement preserves its exact resistance, 0402 body, 1% tolerance, 62.5-mW rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. All six exact UNI-ROYAL MPNs are live JLCPCB Standard-PCBA stock with MOQ 1. Their five-device requirement falls from approximately USD 53.7347 in the captured pre-order route to USD 0.5430 in live stock, saving approximately USD 53.1917; the public material basis falls by USD 0.1542 per device. [JLCPCB](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879)
- **`Nexperia 74LVC2G14GV,125`:** Accepted at H1-R2.26. GV and GW are package variants in the same current Nexperia 74LVC2G14 datasheet: dual Schmitt-inverter behavior, pins 1-6, 1.65-to-5.5-V operation, Ioff partial-power-down protection and timing are common. The 2.9 x 1.5 x 1.1-mm TSOP6 bodies pass the regenerated placement audit. Ten trial parts are covered by the 35-piece available order quantity. The five-device line falls from USD 9.0376 pre-order to USD 2.0100 in stock, saving USD 7.0276; the conservative quantity-100 material basis rises by USD 0.2026 per device. [JLCPCB](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708)
- **`UNI-ROYAL 0402WGF1603TCE`:** Accepted at H1-R2.27. The UNI-ROYAL part preserves 160 kOhm, +/-1%, 0402, the standardized 1/16-W rating, 50-V working voltage, 100-ppm/C temperature coefficient and -55 to +155 C range. Its official body is 1.00 x 0.50 x 0.35 mm versus the selected Vishay's 1.00 x 0.50 x 0.40 mm, so the verified 0402 land pattern and sandwich clearance do not degrade. The five-device line falls from USD 8.9565 pre-order to USD 0.0130 in stock, saving USD 8.9435; the public material basis falls by USD 0.0131 per device. [JLCPCB](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757)
- **`FH RS-06K47R0FT`:** Accepted at H1-R2.27. The FH part preserves 47 Ohm, +/-1%, 1206, 0.25 W, 200 V, 100 ppm/C and -55 to +155 C. Its official 3.20 x 1.60 x 0.55-mm body is thinner than the selected YAGEO 3.20 x 1.60 x 0.65-mm body and uses the standard 1206 land pattern. The five-device line falls from USD 8.9566 pre-order to USD 0.0310 in stock, saving USD 8.9256; the public material basis falls by USD 0.0108 per device. [JLCPCB](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014)
- **`YAGEO CC0603KRX7R0BB104`:** Accepted at H1-R2.27. The YAGEO part preserves 100 nF, +/-10%, 100 V, 0603/1608, -55 to +125 C and the exact 1.60 x 0.80 x 0.80-mm body. X7R holds capacitance within +/-15% over temperature and is stricter than the former X7S +/-22% class, so the USB VBIAS role does not degrade. The five-device line falls from USD 9.0752 pre-order to USD 0.1300 in stock, saving USD 8.9452; the public material basis falls by USD 0.0266 per device. [JLCPCB](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803)
- **`Texas Instruments CSD87313DMS`:** Accepted at H1-R2.29. TI lists DMS and DMST as the same production die, WSON-CLIP DMS 8 package, pin map and electrical limits; DMS is the 2,500-piece large tape-and-reel code and DMST is the 250-piece small tape-and-reel code. C2863848 is live JLCPCB Standard-PCBA stock. The five-device line falls from USD 7.3675 to USD 5.2790, saving USD 2.0885; the quantity-100 material basis falls by USD 0.7084 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C2863848)
- **`Vishay TSOP75238TR`:** Accepted at H1-R2.29. Vishay uses the same final 6.8 x 3.0 x 3.2-mm Heimdall body, contacts and electrical contract for TR and TT; TR changes the tape presentation from top view to side view and the reel quantity from 2,200 to 2,300. C511498 currently covers the five-device trial but not a 100-device run. Before every order, exact stock plus attrition must be covered or pre-ordered, and the CPL rotation/feeder presentation must be approved against the JLCPCB placement preview. The five-device line falls from USD 7.3000 to USD 6.5055, saving USD 0.7945; the quantity-100 material basis falls by USD 0.2369 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C511498)
- **`Murata LQW15AN56NG00D`:** Accepted at H1-R2.29. The Murata G code preserves the LQW15AN 0402 body, 56-nH nominal inductance, Q, 2.8-GHz minimum SRF, 200-mA current and 1.17-Ohm maximum DCR while tightening tolerance from +/-5% to +/-2%. C167482 is live JLCPCB Standard-PCBA stock. The five-device line falls from USD 0.3620 to USD 0.2235, saving USD 0.1385; the quantity-100 material basis falls by USD 0.0277 per device. [JLCPCB](https://jlcpcb.com/partdetail/x/C167482)
- **`OMRON B3S-1000P`:** The stocked member preserves the 6.6 x 6.0 x 4.3-mm body, 1.57-N feel, 500k endurance and IP67 family boundary, but removes the fifth cover-ground terminal. That can weaken the user-exposed ESD path, so the current B3S-1100P remains selected until an equivalent grounded stocked part is proven. [JLCPCB](https://jlcpcb.com/partdetail/OmronElectronics-B3S1000P/C180420)
- **`BZCN TSG002A04526A`:** The stocked 6.15 x 6.15 x 4.5-mm IP67 SMT body would reduce sixteen quantity-one switches from USD 14.50 to USD 0.79, but it raises force from 1.57 N to 2.6 N, removes the fifth grounded-cover terminal from the directly finger-operated user boundary and the exact order code does not disclose a guaranteed 500k-cycle life. Those are functional, ESD and feel regressions rather than a free saving, so it is not selected. [JLCPCB](https://jlcpcb.com/partdetail/BZCN-TSG002A04526A/C2888613)
- **`MYOUNG BH-18650-B1BA002`:** The stocked gold-plated single-cell holder is factory placeable and cheaper, but its 77.05 x 20.65-mm drawing does not prove the selected long protected button-top XTAR envelope, dual-cell mechanical polarization before contact or the current four-independent-contact body. Two pieces therefore do not constitute a no-worse replacement for 1048P. [JLCPCB](https://jlcpcb.com/partdetail/BH-18650-B1BA002/C2988620)
- **`Tag-Connect TC2050-IDC board footprint`:** The keyed spring-probe footprint would save all four board headers in a repeated build, but the exact-one prototype would first require a USD 39 cable, versus USD 5.64 for four currently stocked Samtec headers at JLCPCB. It also replaces a hands-free long-session connection with a dedicated probe workflow. Keep the stocked Samtec parts for EVT1; Tag-Connect remains a post-EVT1 volume option. [JLCPCB](https://www.tag-connect.com/product/tc2050-idc-tag-connect-2050-idc)
- **`HenryTech HL2-SMA-KEP-13.5 / HL2-RP-SMA-KEP-13.5`:** The JLCPCB cards prove a 6-GHz standard/reverse pair and the controlled HenryTech drawings prove individual retention without a nut, but both bodies point normal to the PCB. They do not replace the selected edge-facing GCT bodies without changing antenna direction and product form. [JLCPCB](https://jlcpcb.com/partdetail/HenryTech-HL2_SMA_KEP_135/C53278703)
- **`DreamLNK SMA-KWE902 / SMA-KWE901`:** The exact DreamLNK drawings confirm a robust no-nut, five-pin through-board 6-GHz pair, but also close the fit question negatively for the accepted mock-up. Each 9.7 x 9.7-mm outer body enters an upper 4-mm compression-stop head keep-out at both edge ports on each PCB, while the 5.08 x 5.08-mm pin pattern intersects the display connector, two native-RF couplers, the Airband reserve and CC1101 area on the inner faces. Fixing this would require moving the accepted structural axes or compressing the 5+5 bank and relocating RF bodies. The JLCPCB route is still Plugin/manualWeld with 13/12 procurement minima and no exact-one assembly quote. This is not a drop-in no-loss saving, so the selected GCT pair remains. [JLCPCB](https://jlcpcb.com/partdetail/DreamLNK-SMAKWE902/C914554)
**Accepted rule:** remove avoidable small-lot pre-order first, but replace an MPN only with an exact or no-worse stocked part. RF, power-safety, battery-protection and user-exposed ESD boundaries are not simplified for cost. When no proven equivalent exists, the original MPN and explicit pre-order route remain.

## Cost-reduction queue

1. ▶ **Rebuild the external antenna kit from stocked no-worse equivalents** — Eight of twelve exact first-target antenna profiles already contribute USD 138.3166 per device, while three nRF24 antennas and the controlled AM/LW receive pod remain unpriced. This is the largest separate material group even though it sits outside the base PCBA BOM. Keep every accepted band and all band-specific TX matching. Search the current factory/order surface for exact or no-worse connector, band, power and matching equivalents; optimize receive-only profiles separately and never silently substitute one generic whip for a qualified TX antenna.
2. ✅ **Replace safe equivalent pre-order passives and ordinary logic with in-stock JLCPCB parts** — After seven safe replacement batches, 27 pre-order rows cost USD 660.0144 in the normalized five-device evidence versus USD 331.0265 on their quantity-100 material basis. The stocked Nexperia, YAGEO, UNI-ROYAL, FH, Hirose, TI, Vishay and Murata routes together remove approximately USD 140.8195 from the observed trial route and reduce the public material basis by a net USD 8.0045 per device. Review every pre-order row against its substitution class; only exact or no-worse parametric replacements may be accepted.
3. ✅ **Retain the GCT pair after the cheaper through-hole pair fails the complete 5+5 gate** — Ten GCT RFPC-SMA31/32 connectors contribute USD 24.6456 per device. Exact drawings close the tempting DreamLNK alternative: four outer bodies conflict with the accepted upper compression-stop head keep-outs and five port groups conflict with inner-face bodies/reserves; the factory route also remains manualWeld without an exact-one quote. Keep the accepted dual-face GCT pair. Reopen only for a factory-placeable standard/reverse pair that retains outward orientation and 6-GHz native-port coverage, passes the unchanged 5+5 plus compression-stop geometry and has a complete exact-one order route.
4. ✅ **Use the factory-routable AD8314 MSOP package without weakening real-TX evidence** — Six accepted AD8314ARMZ-REEL plus two retained LTC5532 now contribute USD 19.4142 per device on the common quantity-100 basis. C652687 has an explicit Extended-SMT Standard-PCBA pre-order/overseas route, MOQ 4, and the exact-one device needs six. The full packages, five couplers and eight local evidence allocations pass H1-R2.36 geometry. Keep C652687 and the two LTC5532; carry all eight local evidence allocations into the new R2 H2 schematic/layout and preserve independent evidence for the three concurrently active nRF24 paths.
5. ✅ **Retain the grounded Omron family for all sixteen ordinary controls** — B3S-1100P contributes USD 10.248 per device at quantity 100. Two stocked alternatives were checked: B3S-1000P preserves feel, height, endurance and ingress but removes the grounded cover; TSG002A04526A is dramatically cheaper but also removes that terminal, raises force to 2.6 N and does not prove the exact 500k-cycle life. Because every control is directly finger-operated without a cap or plunger, neither is no-worse. Keep B3S-1100P for the present architecture. Reopen only for an exact factory-placeable part that preserves the grounded user boundary, approximately 1.6-N force, 4.3-mm reach, IP67 and at least 500k cycles, or after a future enclosure revision makes the metal cover physically inaccessible.
6. ✅ **Retain all five U.FL plus 30-mm jumper paths after source-to-port review** — The five paths now contribute USD 9.517 per device at quantity 100 after the exact stocked Hirose packaging-route change, before assembly handling. S3 and all three E01 modules expose only microcoax RF outputs, and each path must still pass through its local coupler and real-TX detector before SMA. The current C5 module also exposes U.FL; an exact stocked Espressif T2/ANT2 factory route is not proved. Therefore 0/5 paths can be removed safely now. A future qualified C5 T2 route could remove one path and save about USD 1.90 per device.
7. ✅ **Retain 1048P until a complete protected-cell holder is proven** — 1048P contributes USD 8.57 per device at quantity 100 and remains a pre-order route, but the checked stocked MYOUNG holders are single-cell bodies or loose contacts that do not prove the selected protected button-top length, dual-cell pre-contact polarity blocking and enclosure-supported four-contact mechanism. Keep 1048P as a justified safety/mechanical part for EVT1. Reopen only for a serial factory-placeable dual holder that proves the complete XTAR envelope and transfers insertion/removal load through the enclosure rather than the solder joints.
8. ✅ **Retain four stocked Samtec DBG10 headers for the exact-one EVT1** — The corrected R2 count is four, not three. Exact C2932107 is currently JLCPCB Extended SMT stock with 890 pieces, 887 orderable, MOQ 1 and USD 1.41 at quantity 1. Four headers therefore cost USD 5.64 on the exact-one factory route. A TC2050-IDC footprint would remove the fitted parts but requires a USD 39 reusable cable and changes long-session debug ergonomics. Keep four FTSH-105-01-L-DV-K-P-TR headers for independent S3/C5/Hub-RP/RF-RP recovery. Reconsider Tag-Connect only after EVT1 when its one-time cable cost can be amortized and the service workflow can be tested.
9. ✅ **Do not optimize away the selected serial production panel** — EastRising ER-TFT035IPS-6 plus ER-TPC035-6 contributes USD 14.91 and already provides a controlled drawing, ILI9488/FT6236, direct i8080-8 and quantity-one serial ordering. The donor route is gone. Treat the display material cost as justified. Only the assembler fee and written acceptance of panel/FPC final mating remain open; do not restart display selection for a small speculative saving.

## Display and flex orientation

- Exact EastRising drawings control the complete panel body, 50-contact FPC, 0.50-mm pitch, 0.30-mm stiffener and contact map; donor-board geometry is no longer used.
- The panel is physically oriented **with its flex toward the antenna edge**, while ILI9488 display memory and FT6236 touch coordinates rotate in firmware. The tail stays out of the LED, D-pad and function-key zone.
- Direct ZIF `Hirose FH34SRJ-50S-0.5SH(50)` at `[24.0, 1.8]` passes the current exact-body model: `0` same-face collisions and `10.0 mm` to the opposing PCB plane versus `0.7 mm` required.
- The adapter PCB and both DF40 parts are removed: stack height falls from `3.8` to `1.0 mm`, and one-prototype component cost falls by `$1.07`. The bezel, PSA and compliant preload carry the panel; ZIF contacts carry no mechanical load.

> Marker: **H1-R2.38**. Included in the current reviewed H1 result.
