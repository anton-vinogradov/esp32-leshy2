# Leshy2 manufacturing platform

[Русский](manufacturing-platform.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

## Reference line

**The working reference is JLCPCB Standard PCBA.** This is neither exclusive lock-in nor order authorization. Standard was selected for its public stock/JLC-number assembly library, double-sided SMT+THT, fine-pitch/BGA/QFN, special stackups and SPI/AOI/X-ray. See the official [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) and [parts-sourcing paths](https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction).

PCBWay remains the manual turnkey/box-build quote fallback; Seeed Fusion remains a second manufacturing quote. Their supplier availability is less suitable as a repeatable machine-checkable MPN-selection source.

```mermaid
flowchart TD
  M["New MPN"] --> PPlaced during PCBA?
  P -->|yes| J0["J0 · exact JLC stock"]
  J0 -->|no| J1["J1 · qualified alternate"]
  J1 -->|no non-degrading alternate| J2["J2 · private pre-order"]
  J2 -->|no| J3["J3 · global/consign"]
  P -->|no; factory installs| J4F["J4-F · factory final assembly"]
  P -->|no; packed separately| J4P["J4-P · factory-packed"]
  J0 --> F["BOM freeze"]
  J1 --> F
  J2 --> F
  J3 --> F
  J4F --> F
  J4P --> F
  F --> R["stock recheck before every order"]
```

## Meaning of “always available”

No platform guarantees perpetual public stock. Leshy2 therefore selects ordinary parts from JLC stock or with prequalified alternates; unique functional identities are reserved in the [private parts library](https://jlcpcb.com/help/article/how-to-build-your-own-parts-library-in-jlcpcb) or received through global sourcing/consignment. A shortage never permits a silent factory substitution.

## Controlled BOM Tool run

The controlled BOM Tool capture belongs to the former 209-line BOM: 176 matched, 33 unmatched and 1019 placements. The current BOM differs only by replacing `SA518` with exact `SA818S-U` + `SA818S-V`: 208 unchanged identities are joined by MPN, and the two new modules by exact `C3001549` and `C51897911` pages. This yields a checkable current map of `210` lines and `1052` placements without retransmitting the BOM. Before applying the retained outlier resolutions it has 178 exact catalogue routes and 32 unresolved lines; zero semantic MPN substitutions were observed.

The retained exact search resolves all 32 unchanged outliers without component replacement: 12 are added to `J0`, 4 to `J2`, 11 retain the exact MPN through `J3`, 3 require factory final assembly `J4-F`, and 2 are packed separately through `J4-P`. With the new voice routes, the whole-BOM result is `J0=148`, `J1=0`, `J2=46`, `J3=11`, `J4-F=3`, `J4-P=2`; zero lines remain unmapped.

The `$1255.6365` displayed in the historical BOM Tool capture covers only its former 176 matched lines and is **not** a current complete assembly price, quote or order. The current minimum evidence basket is calculated separately on the [sample page](component-sample-basket.md).

<details>
<summary>How the 32 unchanged outliers were resolved</summary>

| Normalized MPN | Qty | Route | Evidence |
|---|---:|---:|---|
| `1227-J` | 1 | `J4-F` | encoder knob requires factory installation and control test after enclosure integration |
| `E01-ML01IPX` | 3 | `J3` | three exact full-power nRF24 modules are externally orderable and must be consigned or globally sourced |
| `ESP32-C5-WROOM-1U-N8R8` | 1 | `J2` | `C51950748` · stock 0 |
| `RFPC-SMA31-FN-175-A` | 8 | `J3` | exact board SMA is orderable outside the public JLC library |
| `RFPC-SMA32-FN-175-A` | 2 | `J3` | exact board RP-SMA is orderable outside the public JLC library |
| `FX8C-80S-SV5(92)` | 1 | `J3` | exact inter-board receptacle is orderable outside the public JLC library |
| `BGS13SN8E6327XTSA1` | 2 | `J2` | `C55118249` · stock 0 |
| `U214 Cap LoRa-1262` | 1 | `J4-P` | removable rear Cap accessory is factory-tested, then packed separately for user installation |
| `GJM1555C1H101JB01D` | 2 | `J3` | retain exact RF capacitor until an RF-equivalent alternate is separately qualified |
| `PESD24VY1BSF` | 2 | `J3` | retain exact low-capacitance RF ESD identity until an RF-equivalent alternate is separately qualified |
| `AS02404PO` | 1 | `J3` | exact board speaker is orderable outside the public JLC library and needs manual/THT assembly acceptance |
| `HMX035CTFT-001` | 1 | `J4-F` | display/flex requires factory mating and display/touch functional test during final assembly |
| `SC1512-A4` | 1 | `J2` | `C52763783` · stock 0 |
| `1125R-SMT-4P` | 1 | `J3` | exact Seeed SMT Unit connector is orderable outside the public JLC library |
| `2118651-2` | 5 | `J4-F` | five removable 30-mm microcoax jumpers require factory installation, strain routing and continuity test during final sandwich assembly |
| `MSPM0C1106SDGS20R` | 2 | `J0` | `C52995805` · stock 34 |
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
| `18650 4000mAh` | 2 | `J4-P` | protected cells are packed separately for user installation unless a compliant battery box-build and shipping route is later qualified |
| `RC0402FR-07100RL` | 7 | `J0` | `C106232` · stock 5003833 |
| `RC0402FR-071KL` | 12 | `J0` | `C106235` · stock 4396756 |
| `RC0402FR-0733RL` | 1 | `J0` | `C138002` · stock 5477653 |
| `RC0402FR-074K7L` | 1 | `J0` | `C105871` · stock 7353078 |

</details>

## Independent critical-part check

`11` critical identities were checked independently before the bulk run. Their stock snapshots neither override the current BOM Tool result nor promise permanent availability.

| MPN | JLC | Current evidence | Route |
|---|---:|---|---|
| [`ESP32-S3-WROOM-1U-N16R8`](https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1U-N16R8/C3013946) | `C3013946` | stock 14529 | `J0` · exact selected module is directly assembleable |
| [`ESP32-C5-WROOM-1U-N8R8-V1.2`](https://jlcpcb.com/partdetail/C54951858) | `C54951858` | stock 547 | `J0` · current explicit V1.2 stock matches the architecture revision floor; BOM spelling must be normalized before release |
| [`CC1101RGPR`](https://jlcpcb.com/partdetail/TexasInstruments-CC1101RGPR/C29953) | `C29953` | stock 14194 | `J0` · exact selected transceiver is directly assembleable |
| [`ES8311`](https://jlcpcb.com/partdetail/1044199-ES8311/C962342) | `C962342` | stock 96905 | `J0` · exact selected codec is directly assembleable |
| [`MAX17320G20+ / selected order suffix +T`](https://jlcpcb.com/partdetail/8483980-MAX17320G20/C7457894) | `C7457894` | stock 13 | `J0` · functional identity is present but packaging/order-suffix equivalence and low stock require confirmation or J2 reservation |
| [`SC1512-A4`](https://jlcpcb.com/partdetail/RaspberryPi-SC1512A4/C52763783) | `C52763783` | SMT; fixture; Economic and Standard | `J2` · listed and assembleable, but not public-stock; reserve by pre-order or consign exact parts |
| [`MSPM0C1106SDGS20R`](https://jlcpcb.com/partdetail/55934010-MSPM0C1106SDGS20R/C52995805) | `C52995805` | Extended SMT | `J2` · listed with pre-order MOQ 6; two fitted devices plus attrition are compatible with a small reservation |
| [`E01-ML01IPX`](https://jlcpcb.com/parts/componentSearch?searchTxt=E01-ML01IPX) | `—` | not found in public library | `J3` · retain exact module only through new-part/global-sourcing/consignment until a function-preserving stocked module is qualified |
| [`G-NiceRF SA818S-U`](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549) | `C3001549` | stock 68 | `J0` · exact selected UHF module is priced and in public stock |
| [`G-NiceRF SA818S-V`](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911) | `C51897911` | Standard PCBA pre-order | `J2` · exact selected VHF module is priced but stock-zero pre-order; lead time remains open |
| [`HMX035CTFT-001`](https://jlcpcb.com/parts/componentSearch?searchTxt=HMX035CTFT-001) | `—` | display/flex belongs to factory final assembly | `J4-F` · keep replaceable display-adapter architecture; require factory mating plus display/touch test rather than treating the display as an ordinary line-loaded SMT part |

## Assembly boundary

JLCPCB Standard PCBA assembles both boards and accepted SMT/THT parts. That does not yet prove final device assembly.

| Route | Required operation | Status |
|---|---|---|
| `J4-F` | Factory mates and tests display/flex, installs and strain-routes five microcoax jumpers, installs the encoder knob, integrates the enclosure/sandwich and performs whole-device test | 🔒 Open until written capability acceptance and a separate box-build price; H5 and H7 cannot close without it |
| `J4-P` | Factory compatibility-tests U214 and packs it separately; external antennas are packed as a kit; protected 18650 cells are packed separately for user installation unless compliant battery box-build and shipping are qualified | 🔒 Open until kit/packing/shipping quote |

`J4-F` and `J4-P` do not claim that JLCPCB has already accepted these operations. They define the required result for the selected factory or fallback box-build contractor.

## Two exact voice routes

`SA818S-U` is bound to exact `C3001549`: stock 68, available quantity 60 and one-piece price `$9.7347`. `SA818S-V` is bound to exact `C51897911`: stock 0, MOQ 1, one-piece price `$10.0710` and route `J2` pre-order. `SA818S-CE C19632390` remains only a qualified-pending UHF alternate and is not in the production BOM: it requires HIL and a 470-MHz firmware clamp, never replaces VHF and is never substituted silently.

## Current result

- JLCPCB Standard PCBA is the working reference without lock-in.
- All `210` lines have a defined `J0`–`J3`, `J4-F` or `J4-P` route; no functional replacement was introduced.
- Every component price in the minimum evidence basket is known. A no-order JLCPCB inquiry was successfully submitted on 26 August 2026; H5.0.3-R1 now waits for exact `SA818S-V` pre-order lead time/terms, `J4-F` box-build acceptance/pricing and `J4-P` kit/packing/shipping terms. Sample purchase remains a later separate decision.
- The JLCAPI application is approved, the `ESP32-Leshy2 BOM Validator` app exists, and its signing key is stored locally outside Git. The portal now reports Parts permission as `Rejected`, without a reason in its activity log, so API calls remain unusable. PCB/3D are also rejected; SMT Stencil and JLC Balance remain inactive. Manual catalogue/BOM evidence remains the active path.
- The former 209-line BOM upload was transmitted and processed; the current 210-line file was generated locally but not transmitted because 208 identities are unchanged and both new exact pages were checked separately. No quote, sourcing request, reservation, purchase, replacement, KiCad layout or fabrication was performed or authorized. Raw API responses are not redistributed publicly.

Machine results: [`H5-EVR04`](../hardware/verification/generated/H5-EVR04-pcba-platform-baseline.json), [`H5-EVR05`](../hardware/verification/generated/H5-EVR05-jlcpcb-bom-match.json) and [`H5-EVR06`](../hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json). [JLCPCB BOM requirements](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly).
