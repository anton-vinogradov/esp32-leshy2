# H6.0.3-R1 · Component unification

[Русский](h6-r2-component-unification.ru.md)

2026-09-09. **GCT USB4105-GF-A ×4 is implemented in current H2 and the native boards following explicit approval.** Fresh native DRC/parity and preservation checks pass. No other component family below was replaced. H6.0.3-R1 remains open and is not fabrication-ready.

<!-- usb-unification-status:start -->
The accepted placement is four identical GCT receptacles, all B.Cu / 180°, anchor Y146.325 mm and nominal mouth Y150 mm: flush with, not projecting past, the PCB edge. This follows the GCT drawing and retains the three service-port poses. Native X positions are explicitly UI J11 = 14.87 mm, UI J9 = 26.1 mm; RF J1 = 16.47 mm, RF J4 = 37.47 mm (nominal). The RF change replaced J1 and moved U5 0.15 mm inward to B0 [16.5,139.35]; C31/C32 and the other three ports stay in place. The screened 0.2-mm GCT recess was not selected because it required unnecessary additional companion moves. H2 current-only generation/checks and native integration checks pass. The [integration receipt](../hardware/layout/h6-r2-usb-unification-integration.json) records the exact two-reference change and unchanged UI; live routing and view artifacts have their existing owners.
<!-- usb-unification-status:end -->

## Native verification and limits

Final regression run on 2026-09-09: the general suite ran **1,417 tests with no failures and 99 environment-dependent skips**; separately, KiCad Python ran **821 H6 tests with no failures or skips**. These suites overlap and their counts are not added. Commands: `python3 -m unittest discover -s hardware/architecture/tests -q` and KiCad Python with `-m unittest discover -s hardware/architecture/tests -p 'test_h6*.py' -q`.

Both boards pass fresh native DRC: **0 rule violations / 0 schematic-parity findings**. All **1208 electrical positions** are placed without hard conflicts; **1216 footprints** including mounts have zero source/library pad drift, and the native silkscreen audit passes. All **857 copper objects (UI92 + RF765)** remain unchanged; **197 connections are resolved / 3071 remain unrouted**. Ten SMA connectors / 50 lands have no foreign-pad contacts in the scoped screen, and five microcoax paths retain at least **5.22 mm nominal slack**.

The RF J1 exact GCT pattern needs a narrowly scoped **0.19-mm NPTH-locator-to-GND rule** for its native nominal **0.1944-mm** internal gap, instead of the global 0.25-mm minimum. Only the exact footprint's Ø0.65-mm NPTH locators and named GND lands are covered; other parts, tracks and global rules are unchanged. The three existing GCT ports already have their separate 0.09-mm internal rule. These are explicit nominal-pattern accommodations, **not toleranced manufacturing/DFM qualification**. Plug/case access, soldering, electrical behaviour and incomplete routing remain open. [Integration record](../hardware/layout/h6-r2-usb-unification-integration.json), [RF rules](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_dru).

## What changes, and why

The protected product port was selected as JAE DX07S016JA1R1500 on 2026-08-18; GCT service receptacles were added on 2026-08-19, retaining that earlier choice. The scoped history provides no comparative requirement that JAE alone can carry product power. The service ports are data-only because of their wiring, not because GCT is a data-only connector. See [USB-0001](../drafts/project-history-2026-08-19/review/architecture/USB-0001-exact-product-usb-c-and-protection.md) and [SVC-0002](../drafts/project-history-2026-08-19/review/architecture/SVC-0002-exact-three-domain-service-recovery-boundary.md).

The approved GCT variant has 16 mating contacts, 12 shared solder positions and four shell stakes. Its collective VBUS rating is 5 A; this does **not** raise any negotiated product current or protection limit. All four ports keep their existing electrical roles. The [dated factory record](../hardware/verification/jlcpcb-usb-unification-2026-09-09.json) records JLC C3020560, Standard PCBA / SMT eligibility, assembly difficulty High, displayed stock 1044 and a stock-backed private-library pre-order route: minimum 9 pieces, estimated $1.0656 each at that quantity. It is not MOQ 1, a reservation or an all-in assembly quote. [GCT primary product/drawing](https://gct.co/connector/usb4105).

Current H2 has **244 board device groups / 250 product groups**, with all **1208 electrical instances** retained. Removing the redundant JAE type reduces definition-level contacts, not the real port count: native symbols still represent 4305 physical pins. The H5 purchasing view has 248 purchasable groups. No other replacement is approved by this audit. [Current routing](h6-r2-current-routing.md) owns live PCB hashes and verification results.

## Audit boundary

The two reproducible inventories are snapshots of commit `33908f003f2e622119de197056ed8ef70ddeeb2d`, **before** USB unification: 1208 instances / 245 fitted device IDs, not the old 210-part concept summary.

- [Nonpassive/family audit](../hardware/verification/h6-r2-component-diversity-nonpassive-2026-09-09.json): 14 bounded comparisons; full source hashes, IDs, roles, counts and relevant physical endpoints. Its 287-row non-R/C/L/FB screen also contains RF passives, crystals and fuses; it is not a count of semiconductors.
- [Passive audit](../hardware/verification/h6-r2-component-diversity-passive-2026-09-09.json): 926 passive/diode/printed-loop instances, including one non-orderable NFC loop. These scopes overlap and must not be added together.

Both records preserve the old source hashes as historical evidence. Neither is a replacement qualification or a current factory-stock check.

## Concrete remaining candidates — not adopted

| Pair in the audited population | Count | Remaining application check |
|---|---:|---|
| UNI 0402WGF1002TCE ↔ Yageo RC0402FR-0710KL, 10k | 4 ↔ 216 | NFC output/threshold/control bias: preserve thresholds and currents. |
| UNI 0402WGF1003TCE ↔ Yageo RC0402FR-07100KL, 100k | 2 ↔ 43 | NFC discharge and threshold: preserve RC corners. |
| UNI 0402WGF1004TCE ↔ Yageo RC0402FR-071ML, 1M | 1 ↔ 15 | NFC hysteresis and leakage. |
| UNI 0402WGF1001TCE ↔ Yageo RC0402FR-071KL, 1k | 2 ↔ 16 | R228/R229 are 13.56 MHz pickup inputs: DC matching alone is insufficient. |
| Samsung CL05B104KB5NNNC ↔ Yageo CC0402KRX7R9BB104 | 1 ↔ 173 | C70 is MAIN bootstrap: primary exact specs and effective capacitance, not arbitrary bypass substitution. |
| Samsung CL10B105KO8NNNC ↔ TDK C1608X7R1C105K080AC | 1 ↔ 37 | C71 is MAIN buck VCC: verify effective capacitance and regulator requirements. |
| SN74LVC1G3157DBVR ↔ TS5A63157DCKR | 1 ↔ 3 | RF U69 versus U68/U72/U85; detailed boundary below. |

The four resistor pairs share the verified 0402, 1%, ±100 ppm/°C class, but the nine UNI positions versus 290 Yageo positions do not choose the sourcing direction. UNI's old Basic record and Yageo's old distributor record require a fresh exact JLC comparison. Changing the majority would affect 290 positions. The two capacitor pairs presently match registered nominal classes only; they are weaker candidates. Primary links and per-position identities are in the passive audit.

### U69: a real candidate, not a drop-in

U69 (`ti_sn74lvc1g3157_dbvr`, RX selector) and the three `ti_ts5a63157_dckr` selectors use 3V3_MAIN/AUDIO_GROUND. U69's two inputs are biased toward AUDIO_VMID_MAIN through R165/R210; their complete signal/fault envelope is not yet qualified. U106.P27 drives selection with R173's 10k pulldown: low selects Si4732 on pin 3, high selects voice on pin 1. This truth mapping is shared by both parts; an unpowered rail is a separate state.

| Primary comparison | LVC part at U69 | Existing TS5A family |
|---|---|---|
| Normal analog range; logic thresholds | 0…VCC; 0.7/0.3 × VCC | Same |
| Full-range resistance at 3 V, −24 mA | 25 Ω maximum | 18 Ω maximum |
| Switch-OFF leakage, specified powered conditions | ±1 µA maximum | 0.05 µA maximum |
| VCC = 0 isolation | Not established by that leakage row | Explicit; NC/NO 2 µA, COM 5 µA maxima |
| Selected package / ambient range | DBV SOT-23-6 / −40…125°C | DCK SC70-6 / −40…85°C |

Sources: [LVC recommended conditions](https://www.ti.com/document-viewer/SN74LVC1G3157/datasheet/GUID-XXXXXXXX-SF0T-XXXX-XXXX-000000355792), [LVC electrical table](https://www.ti.com/document-viewer/SN74LVC1G3157/datasheet/GUID-XXXXXXXX-SF0T-XXXX-XXXX-000000358095), [TS5A 3.3-V table](https://www.ti.com/document-viewer/TS5A63157/datasheet/electrical-characteristics-for-3-3-v-supply-scds203493). Full-temperature maxima have different temperature envelopes; they do not prove audio equivalence. Before any change: verify local maximum temperature, output-level margins, startup/fault states, pop/click/noise, package/lands and live sourcing. Do not weaken the three existing TS5A power-off-protected uses.

## Differences retained for a reason

| Family / exact populated examples | Reason to retain; not proof that every existing circuit is qualified |
|---|---|
| Bucks: TPS629203DRLR ×1, TPS566231PRQFR ×1, TPS564252DRLR ×2 | AON low-current/Iq versus MAIN and switched power rails; different feedback, enable and load envelopes. Existing power findings remain open. |
| eFuses: TPS25961DRVR ×1, TPS25974LRPWR ×2, TPS259470LRPWR ×2; TPS2553DRVR-1 ×1 | Different current protection, PG/PGTH, reverse blocking, fault/latch behavior and backlight role. TPS22919DCKR ×8 is already unified and is not an equivalent eFuse. |
| TCA9534APWR ×2, TCA9535PWR ×1, TCA9539PWR ×1, TCA6424ARGJR ×1 | 8/16/24 lines, addresses, reset and power domains differ. Even the two 24-pin packages disagree at pin 3: A2 versus RESET_N. |
| TPS3839K33DBZR ×2 / TPS3808G33DBVR ×4 | Fixed push-pull reset versus open-drain, sense/manual-reset/CT functions. |
| ESD, bus buffers and logic | Channel count, capacitance, voltage, power-off behavior, OE polarity and domain isolation matter. Supplier name alone does not establish duplication; exact groups are in the audit. |
| LMV331IDBVR ×1 / TLV1821DCKR ×3 / TLV1824PWR ×2 | Secondary review lead only: NFC versus evidence thresholds, input range, POR and different pinout. Not an approved consolidation. |
| B3S-1100P ×16; SKRTLAE010 ×8; red LTST-C190KRKT ×9 / orange LTST-C190KFKT ×1 | Matching button roles already share parts; top/side actuation and fault color are intentional. |
| TLV9061IDBVR ×2; FSUSB42MUX ×3; U.FL ×5; debug FTSH ×6 | Already unified where function matches. MCU/RF bands, complementary M1 halves and SMA polarity remain distinct. |

No protection, safety boundary, analog function, existing unresolved electrical finding or assembly gate is removed to reduce part numbers.
