# Leshy2 manufacturing platform

[Русский](manufacturing-platform.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

## Reference line

**The working reference is JLCPCB Standard PCBA.** This is neither exclusive lock-in nor order authorization. Standard was selected for its public stock/JLC-number assembly library, double-sided SMT+THT, fine-pitch/BGA/QFN, special stackups and SPI/AOI/X-ray. See the official [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) and [parts-sourcing paths](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction).

The procurement target is exactly **one fully assembled prototype**, with no batteries. The factory makes no electrical or mechanical design choices: the production package first fixes the exact panel, its mating, every component and the assembly sequence. The owner performs the first full power-on and USB bring-up.

PCBWay is the first full-device fallback: its official pages confirm [turnkey/combo/consigned PCBA and test](https://www.pcbway.com/assembly-capabilities.html) plus [OEM final assembly](https://www.pcbway.com/oem.html). Exact Leshy2 acceptance and prices still need a written answer; the prepared inquiry has not been sent. Seeed Fusion is confirmed only as a PCBA second source: [turnkey, OPL and mixed assembly](https://www.seeedstudio.com/pcb-assembly.html) are public, but the four required final-assembly operations for one prototype are not proven.

```mermaid
flowchart TD
  M["New MPN"] --> PPlaced during PCBA?
  P -->|yes| J0["J0 · exact JLC stock"]
  J0 -->|no| J1["J1 · qualified alternate"]
  J1 -->|no non-degrading alternate| J2["J2 · private pre-order"]
  J2 -->|no| J3["J3 · global/consign"]
  P -->|no; factory installs| J4F["J4-F · factory final assembly"]
  P -->|no; packed separately| J4P["J4-P · factory-packed"]
  P -->|not delivered| J5U["J5-U · user-supplied"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  J5U --> F
  F --> R["stock recheck before every order"]
```

## Meaning of “always available”

No platform guarantees perpetual public stock. Leshy2 therefore selects ordinary parts from JLC stock or with prequalified alternates; unique functional identities are reserved in the [private parts library](https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb) or received through global sourcing/consignment. A shortage never permits a silent factory substitution.

## Controlled BOM Tool run

The controlled BOM Tool capture belongs to the former 209-line BOM: 176 matched, 33 unmatched and 1019 placements. The current BOM replaces `SA518` with two exact voice modules, the legacy display with the exact EastRising endpoint, and the former 0-dBm nRF24 with the stocked full-power `E01-ML01SP4`. This yields a checkable current map of `212` lines and `1052` placements without retransmitting the BOM. Before applying the retained outlier resolutions it has 184 exact catalogue routes and 28 unresolved lines; zero semantic MPN substitutions were observed.

The retained exact search resolves all 28 remaining outliers without component replacement: 11 are added to `J0`, 2 to `J2`, 10 retain the exact MPN through `J3`, 3 require factory final assembly `J4-F`, U214 uses `J4-P`, and accumulators use out-of-delivery `J5-U`. The exact EastRising display already enters through its direct `J4-F` route. The whole-BOM result is `J0=167`, `J1=0`, `J2=29`, `J3=10`, `J4-F=4`, `J4-P=1`, `J5-U=1`; zero lines remain unmapped.

The `$1255.6365` displayed in the historical BOM Tool capture covers only its former 176 matched lines and is **not** a current complete assembly price, quote or order. The sole prototype's order-integrated article manifest is calculated on the [manifest page](component-sample-basket.md); there is no separate sample/coupon purchase.

<details>
<summary>How the 28 remaining outliers were resolved</summary>

| Normalized MPN | Qty | Route | Evidence |
|---|---:|---:|---|
| `1227-J` | 1 | `J4-F` | encoder knob requires deterministic factory installation after enclosure integration; full control bring-up is performed by the owner |
| `RFPC-SMA31-FN-175-A` | 8 | `J3` | exact board SMA is orderable outside the public JLC library |
| `RFPC-SMA32-FN-175-A` | 2 | `J3` | exact board RP-SMA is orderable outside the public JLC library |
| `FX8C-80S-SV5(92)` | 1 | `J3` | exact inter-board receptacle is orderable outside the public JLC library |
| `BGS13SN8E6327XTSA1` | 2 | `J2` | `C55118249` · stock 0 |
| `U214 Cap LoRa-1262` | 1 | `J4-P` | removable rear Cap accessory is packed separately for user installation; factory compatibility FCT is not mandatory |
| `GJM1555C1H101JB01D` | 2 | `J3` | retain exact RF capacitor until an RF-equivalent alternate is separately qualified |
| `PESD24VY1BSF` | 2 | `J3` | retain exact low-capacitance RF ESD identity until an RF-equivalent alternate is separately qualified |
| `AS02404PO` | 1 | `J3` | exact board speaker is orderable outside the public JLC library and needs manual/THT assembly acceptance |
| `1125R-SMT-4P` | 1 | `J3` | exact Seeed SMT Unit connector is orderable outside the public JLC library |
| `1-2118651-0` | 3 | `J4-F` | three removable 60-mm nRF microcoax jumpers require deterministic factory installation and strain routing during final sandwich assembly; full power-on is owner bring-up |
| `2118651-2` | 2 | `J4-F` | two removable 30-mm S3/C5 microcoax jumpers require deterministic factory installation and strain routing during final sandwich assembly; full power-on is owner bring-up |
| `SN74LVC1G07DCKR` | 10 | `J0` | `C7830` · stock 31027 |
| `SN74LVC1G08DCKR` | 4 | `J0` | `C7832` · stock 179787 |
| `SN74LVC1G17DCKR` | 1 | `J0` | `C10425` · stock 59402 |
| `TCA9539PWR` | 1 | `J0` | `C131972` · stock 8380 |
| `TLV1821DCKR` | 2 | `J3` | exact voice-evidence comparator must be sourced; no silent threshold/path alternate |
| `TLV1824PWR` | 2 | `J0` | `C35149428` · stock 9 |
| `TPD2EUSB30ADRTR` | 2 | `J0` | `C94934` · stock 5068 |
| `TPD4E05U06DQAR` | 13 | `J0` | `C138714` · stock 61819 |
| `TPUL2G223BQBR` | 1 | `J3` | exact safety timer must be sourced; no silent timing-function alternate |
| `B0310J50100AHF` | 1 | `J2` | `C5160223` · stock 0 |
| `TSMP95000TT` | 1 | `J3` | only a zero-stock generic JLC Assembly placeholder exists; exact Vishay identity must be sourced |
| `18650 4000mAh` | 2 | `J5-U` | accumulator cells are not part of device delivery; the user separately supplies and installs compatible protected cells |
| `RC0402FR-07100RL` | 7 | `J0` | `C106232` · stock 5003833 |
| `RC0402FR-071KL` | 12 | `J0` | `C106235` · stock 4396756 |
| `RC0402FR-0733RL` | 1 | `J0` | `C138002` · stock 5477653 |
| `RC0402FR-074K7L` | 1 | `J0` | `C105871` · stock 7353078 |

</details>

## Independent critical-part check

`23` critical identities were checked independently before the bulk run. Their stock snapshots neither override the current BOM Tool result nor promise permanent availability.

| MPN | JLC | Current evidence | Route |
|---|---:|---|---|
| [`RS-06L2R70FT`](https://jlcpcb.com/partdetail/304147-RS06L2R70FT/C323265) | `C323265` | stock 3617 | `J0` · exact 2.7-Ohm +/-1% 250-mW 1206 backlight resistor removes the uncontrolled zero-Ohm cathode path while retaining useful first-prototype brightness |
| [`FSUSB42MUX`](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355) | `C11355` | stock 66698 | `J0` · live 2026-08-30 public-stock route for the exact onsemi MSOP-10; selected without package or pin-topology change |
| [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946) | `C3013946` | stock 14529 | `J0` · exact selected module is directly assembleable |
| [`ESP32-C5-WROOM-1U-N8R8`](https://jlcpcb.com/partdetail/C54951858) | `C54951858` | stock 460 | `J0` · official Espressif MPN remains unsuffixed; the supplier code fixes the production route at V1.2 and incoming MD plus eFuse must independently prove revision >=v1.2 |
| [`CC1101RGPR`](https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953) | `C29953` | stock 14194 | `J0` · exact selected transceiver is directly assembleable |
| [`ES8311`](https://jlcpcb.com/partdetail/1044199-ES8311/C962342) | `C962342` | stock 96905 | `J0` · exact selected codec is directly assembleable |
| [`74LVC2G126DP,125`](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392) | `C503392` | stock 155 | `J0` · exact selected TSSOP package variant is in public stock; same official family, pin map, logic, Ioff and timing as the former DC package |
| [`74LVC2G14GV,125`](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708) | `C426708` | stock 153 | `J0` · exact selected TSOP package variant has ten-part trial coverage; same official family, pin map, Schmitt thresholds, Ioff and timing as the former GW package |
| [`MAX17320G20+T`](https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894) | `C7457895` | Extended SMT pre-order | `J2` · the exact selected +T order suffix remains on the pre-order route; the stocked C7457894 card names MAX17320G20+ without proving suffix equivalence, so it is not silently accepted |
| [`SC1512-A4`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | `C39843328` | stock 3442 | `J0` · live original-manufacturer route; canPresale 3442 is the authoritative assembly availability, displayed stock is 3605, and received A4 marking remains an incoming gate |
| [`MSPM0C1106SDGS20R`](https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805) | `C52995805` | Extended SMT | `J2` · listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation |
| [`E01-ML01SP4`](https://jlcpcb.com/partdetail/E01-ML01SP4/C97340) | `C97340` | stock 405 | `J0` · exact Chengdu Ebyte PA/LNA module is directly factory-placeable; 20-dBm and ten-land footprint replace the incorrect 0-dBm E01-ML01IPX baseline |
| [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | `C3001549` | stock 68 | `J0` · exact selected UHF module is priced and in public stock |
| [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | `C51897911` | Standard PCBA pre-order | `J2` · exact selected VHF module is priced but stock-zero pre-order; lead time remains open |
| [`ER-TFT035IPS-6 + ER-TPC035-6 option 5344`](https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen) | `—` | stock manufacturer in stock | `J4-F` · exact configured panel, drawings, 50-contact tail, ILI9488/FT6236 endpoint and price are fixed; written assembler acceptance remains only for adhesive/FPC/final mating |
| [`FH34SRJ-50S-0.5SH(50)`](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104) | `C3169104` | stock 2679 | `J0` · exact selected 50-position panel connector is directly placeable; quantity-one price USD 0.5832 |
| [`0402WGF1603TCE`](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757) | `C25757` | stock 388017 | `J0` · exact stocked 160-kOhm 0402 replacement preserves the complete audio-attenuator electrical contract and uses a thinner body |
| [`RS-06K47R0FT`](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014) | `C140014` | stock 78058 | `J0` · exact stocked 47-Ohm 1206 replacement preserves the IR current-limit power, voltage and temperature contract |
| [`CC0603KRX7R0BB104`](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803) | `C113803` | stock 1027658 | `J0` · exact stocked 100-nF 100-V 0603 body; X7R temperature stability is stricter than the replaced X7S class |
| [`DF40C(2.0)-40DS-0.4V(51)`](https://jlcpcb.com/partdetail/x/C597934) | `C597934` | stock 7218 | `J0` · exact Hirose receptacle body and mate; (51) changes only reel quantity from the former (58) order code |
| [`CSD87313DMS`](https://jlcpcb.com/partdetail/x/C2863848) | `C2863848` | stock 4813 | `J0` · same production die, WSON-CLIP body, contacts and electrical contract as DMST; DMS changes tape-and-reel quantity only |
| [`TSOP75238TR`](https://jlcpcb.com/partdetail/x/C511498) | `C511498` | stock 17 | `J0` · same final body, contacts and electrical contract as TT; TR changes tape presentation, so approve CPL rotation/feeder orientation and recheck complete-job stock before order |
| [`LQW15AN56NG00D`](https://jlcpcb.com/partdetail/x/C167482) | `C167482` | stock 21558 | `J0` · exact 56-nH LQW15AN 0402 body; G tightens inductance tolerance from +/-5% to +/-2% without degrading RF limits |

## Assembly boundary

JLCPCB Standard PCBA assembles both boards and accepted SMT/THT parts; its official Function Test path accepts a procedure for review and quotation. For Leshy2 that service is optional quote-only insurance, not a gate. Exact `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 and `FH34SRJ-50S-0.5SH(50)` are selected; only written factory acceptance of adhesive, FPC insertion/ZIF closure and one-device final assembly remains open.

| Route | Required operation | Status |
|---|---|---|
| `J4-F` | From the release package, the factory installs and mates exact `ER-TFT035IPS-6 + ER-TPC035-6` through `C3169104`, secures two 30-mm and three 60-mm microcoax jumpers, installs the encoder knob and integrates the enclosure/sandwich without engineering guesses | 🔒 Open until written adhesive/FPC/final-assembly capability acceptance and one-prototype assembly price; optional Function Test is not a gate |
| `J4-P` | Factory compatibility-tests and separately packs U214; external antennas are packed as a kit | 🔒 U214 and antenna kit remain open until a kit/packing quote |
| `J5-U` | User separately buys and installs compatible protected 18650 cells | ✅ Accepted product boundary: accumulators are not included in device delivery |

`J4-F` and `J4-P` do not claim that JLCPCB has already accepted these operations. They define the required result for the selected factory or fallback box-build contractor.

## Two exact voice routes

`SA818S-U` is bound to exact `C3001549`: stock 68, available quantity 60 and one-piece price `$9.7347`. `SA818S-V` is bound to exact `C51897911`: stock 0, MOQ 1, one-piece price `$10.0710` and route `J2` pre-order. `SA818S-CE C19632390` remains only a qualified-pending UHF alternate and is not in the production BOM: it requires HIL and a 470-MHz firmware clamp, never replaces VHF and is never substituted silently.

## C5 MPN, supplier and revision

The official MPN remains `ESP32-C5-WROOM-1U-N8R8`. Only the supplier order code carries the suffix: `ESP32-C5-WROOM-1U-N8R8-V1.2`. The active route is Espressif `C54951858`, Standard PCBA, stock 460, available 440 and MOQ 1; former `C51950748` is forbidden as an active route. Production requires both MD/lot identity and eFuse readback `>=v1.2`; `v1.0` is engineering-only, while `v0.1`, unknown identity and any mismatch are quarantined.

## Current result

- JLCPCB Standard PCBA is the working reference without lock-in.
- All `212` lines have a defined `J0`–`J3`, `J4-F`, `J4-P` or `J5-U` route; no functional replacement was introduced.
- JLCPCB's partial [26 August 2026 response](../hardware/procurement/H5.0.3-R1-jlcpcb-response-2026-08-26.md) confirms exact `SA818S-V C51897911` MOQ 1 and a typical 8–15-working-day pre-order, plus the official Function Test path with manual procedure review and a `$15.70 + $7.86/hour` basis. Function Test is optional for this project and closes no gate; written acceptance of display mating and one-prototype final assembly is still absent. Accumulators remain `J5-U` and outside delivery. [`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json) stays fail-closed; purchase and order remain unauthorized.
- The JLCAPI application is approved, the `ESP32-Leshy2 BOM Validator` app exists, and its signing key is stored locally outside Git, but Parts permission remains `Rejected`. [Support replied](../hardware/procurement/H5.0.3-R1-parts-api-support-inquiry.md) that the account is new and has no order history, so an ongoing business need could not yet be verified; reapplication is possible after building history or with a fuller business case/integration plan. The responder explicitly is not on the API review team and supplied no exact order threshold. No reapplication was submitted: API calls remain unusable, and live manual catalogue cards plus BOM validation remain authoritative. PCB/3D are also rejected; SMT Stencil and JLC Balance remain inactive.
- [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json) preserves a fallback without restarting H5: PCBWay is the first full-device candidate and Seeed is the PCBA second source. The [same no-order PCBWay questionnaire](../hardware/procurement/H5.0.3-R1-pcbway-fallback-inquiry.md) is prepared but sending it and all commercial actions remain unauthorized.
- The former 209-line BOM upload was transmitted and processed; the current 212-line file was generated locally but not transmitted: 196 identities are preserved, 15 exact pages, the refreshed C5 route and the new external 60-mm microcoax were checked separately. No quote, sourcing request, reservation, purchase, KiCad layout or fabrication was performed or authorized. Raw API responses are not redistributed publicly.

Machine results: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json), [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json) and [`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json). [JLCPCB BOM requirements](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly).
