# H5.0.1-R1 · component-evidence map

[Русский](component-evidence-map.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

The mapping review is complete: all nine H5 residuals and all 14 mechanical gates are joined to selected serial parts, existing sources, missing data and pre-accepted pass rules. This does **not** close a physical check and does **not** authorize a purchase.

```mermaid
flowchart LR
  R["9 H5 residuals"] --> M["✅ exact identities<br/>and sources joined"]
  G["14 mechanical gates"] --> M
  M --> S["▶️ H5.0.2-R1<br/>documents and serial alternatives"]
  S --> P["H5.0.3-R1<br/>one order manifest"]
```

## Nine physical residuals

### `H3-PHY-017` · `display`

- Selected: `EastRising ER-TFT035IPS-6 + ER-TPC035-6`; `Hirose FH34SRJ-50S-0.5SH(50)`.
- Still to prove: current-lot complete FPC construction and fit in the direct FH34SRJ-50S-0.5SH(50), including the source-backed free-loop radius and enclosure keep-out; received ER-TFT035IPS-6 plus ER-TPC035-6 identity/readback, measured VDD/VDDI ramp equality and one-prototype adhesive/FPC assembly record.
- Pass rule: the factory assembly record confirms the exact ER-TFT035IPS-6 + ER-TPC035-6, correct PSA cut, free loop and direct-FH34SRJ insertion; owner bring-up of the sole prototype confirms ILI9488/FT6236, VDD/VDDI, reset, image and touch; a mismatch reopens H1/H2/H3

### `H3-PHY-024` · `ir`

- Selected: `Vishay TSOP75238TR`; `Vishay TSMP95000TT`; `Vishay VSMY14940`.
- Still to prove: received-lot orientation and measured startup, quiet-guard, capture and no-back-power behaviour.
- Pass rule: the received specimen directly demonstrates this item: verify received TSOP75238TR/TSMP95000TT identity, orientation, two-channel capture, 20-ms startup guard, 5-ms QOD quiet guard and no-back-power; confirm TSOP75238TR CPL rotation and feeder presentation against the JLCPCB placement preview; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-028` · `battery`

- Selected: `Analog Devices MAX17320G20+T`.
- Still to prove: one-device blank -> deliberately invalid but electrically safe configuration -> golden/recovery record with both address spaces, checksum, NVError and remaining-update bitmap; zero-remaining and failed-copy emulator/fixture injection records without consuming all seven physical updates.
- Pass rule: the received specimen directly demonstrates this item: on one received MAX17320, record blank fail-closed behavior, program a deliberately invalid but electrically safe configuration, then program the reviewed golden image and prove recovery; read both address spaces, checksum, NVError and remaining-update bitmap at each transition; inject zero-remaining and failed-copy only in the emulator or isolated fixture, never consume all seven physical updates and use no sacrificial chip; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-038` · `timing`

- Selected: `Hirose DM3AT-SF-PEJM5`.
- Still to prove: exact serial microSD reference-medium MPN is not selected; received-card CMD6 identity, throughput, stall distribution and 512-KiB-buffer trace.
- Pass rule: the received specimen directly demonstrates this item: qualify SD card identity/CMD6 high-speed mode, >=4.0-MB/s storage, 1.5-MB/s record, 250-ms stalls and 512-KiB buffering; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-046` · `boundaries`

- Selected: `M5Stack U214 Cap LoRa-1262`; `Samtec HLE-107-02-G-DV-PE-LC`.
- Still to prove: the stock U214 fitted male-post manufacturer/MPN, section, material and plating are not published; ordinary assembly/disassembly, continuity, bottoming-clearance and retention inspection for the mixed stock-U214/HLE pair; any unsourced force remains a design-analysis input rather than a qualification load.
- Pass rule: the received specimen directly demonstrates this item: verify received stock U214 male-post material/plating, ordinary assembly/disassembly, current continuity, bottoming clearance and retention inspection; any unsourced insertion force remains a design-analysis input, and the 4.1-A figure proves only the controlled HLE/TSM pair; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-048` · `boundaries`

- Selected: `1125R-SMT-4P`; `Texas Instruments TXS0102DCUR`.
- Still to prove: exact serial cable/accessory set for the admitted I2C, UART, GPIO and 1-Wire profiles is not selected; received cable lengths, pull networks and profile waveforms through TXS0102.
- Pass rule: the received specimen directly demonstrates this item: qualify each native Unit profile, cable length and pull network through TXS0102; 1-Wire remains specimen-only; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-053` · `phase`

- Selected: `Ebyte E01-ML01SP4`; `TE Connectivity 1-2118651-0`; `Hirose U.FL-R-SMT-1(80)`; `GCT RFPC-SMA31-FN-175-A`.
- Still to prove: the fitted microcoax receptacle subpart MPN on E01-ML01SP4 is not published; the module drawing does publish its location; three independent assembled-feed loss/match and mating/retention records.
- Pass rule: the received specimen directly demonstrates this item: measure all three E01 module-to-SMA feeds and received-lot Gen1 mating/retention independently; a mismatch reopens the owning H1/H2/H3 result

### `H3-PHY-057` · `phase`

- Selected: `Si4732-A10-GSR`; `GCT RFPC-SMA31-FN-175-A`; `L2-ANT-AM-LW-001`.
- Still to prove: received edge-SMA and controlled pod constituent identities, physical envelopes and mating records before the H6 routed-capacitance budget and H8 total measurement.
- Pass rule: the received SMA and every controlled pod constituent match their selected identities and physical envelopes; H5 does not claim total assembled-path capacitance

### `H3-PHY-062` · `phase`

- Selected: `ESP32-S3-WROOM-1U-N16R8`; `ESP32-C5-WROOM-1U-N8R8`; `Ebyte E01-ML01SP4`; `TE Connectivity 2118651-2`; `TE Connectivity 1-2118651-0`; `Hirose U.FL-R-SMT-1(80)`.
- Still to prove: received 2118651-2 bend, retention and strain behaviour in the two 30-mm S3/C5 paths and 1-2118651-0 behaviour in the three 60-mm nRF paths; received E01 fitted-receptacle mate fit against the published connector locations before freezing placement.
- Pass rule: the received specimen directly demonstrates this item: measure received 2118651-2 bend/retention/strain behavior and E01 connector axes before freezing the five microcoax paths; a mismatch reopens the owning H1/H2/H3 result

## Fourteen mechanical gates

- `H5-MECH-DISPLAY-TAIL` — `EastRising ER-TFT035IPS-6 + ER-TPC035-6`; `Hirose FH34SRJ-50S-0.5SH(50)`; open: Current-lot FPC thickness/stiffener conformity, actual insertion, exact free-loop bend radius and enclosure keep-out, the exact safe rear adhesive perimeter and the assembler's accepted die-cut PSA material/process remain properties of the one-prototype route. 3M 9495LE is only a 0.17-mm technical candidate until that route is confirmed.
- `H5-MECH-NRF-GEN1-FEEDS` — `Ebyte E01-ML01SP4`; `TE Connectivity 1-2118651-0`; `Hirose U.FL-R-SMT-1(80)`; `GCT RFPC-SMA31-FN-175-A`; open: The fitted receptacle manufacturer's exact subpart MPN, actual mate retention, bend/strain behaviour and end-to-end RF loss remain received-part properties. H1 uses the published connector location and full maximum body envelope; H5/H8 verify the real fit and RF path.
- `H5-MECH-U214-MATING-STACK` — `M5Stack U214 Cap LoRa-1262`; `Samtec HLE-107-02-G-DV-PE-LC`; open: Current U214 post section, insertion force, contact retention, retention-screw engagement and final compliant rail preload remain received-part properties; absent manufacturer limits remain design-analysis inputs and do not create an artificial cycle test.
- `H5-MECH-NAVIGATION-CONTROLS` — `OMRON B3S-1100P`; open: Assembled enclosure opening access, accidental-press margin, multi-button feel and sealing boundary.
- `H5-MECH-SA818S-DUAL-LAND-FIT` — `G-NiceRF SA818S-U`; `G-NiceRF SA818S-V`; open: Received SA818S-U/V lot identity, common-land tolerance, solder fillet and thermal assembly behaviour.
- `H5-MECH-ENCODER-KNOB` — `Alps Alpine EC11E18244AU`; `Davies Molding 1227-J`; open: Insertion depth, retention, push travel, feel and final rear depth on received parts.
- `H5-MECH-DIRECT-PRESS-CONTROLS` — `OMRON B3S-1100P`; open: PCB/enclosure press feel and accidental-press margin.
- `H5-MECH-RUN-KILL` — `C&K JS102011SCQN`; open: Received side access, detent force and accidental motion.
- `H5-MECH-M5-UNIT-MATE` — `1125R-SMT-4P`; open: Received Grove cable insertion, retention and strain relief.
- `H5-MECH-CELL-HOLDER-FIT` — `Keystone Electronics 1048P`; `XTAR 18650 4000mAh`; open: Received insertion force, contact compression, polarity protection and enclosure support; values absent from manufacturer sources remain design-analysis inputs.
- `H5-MECH-NATIVE-RF-JUMPERS` — `TE Connectivity 2118651-2`; `Hirose U.FL-R-SMT-1(80)`; open: Actual bend radius, strain relief, insertion force, retention and RF loss after assembly.
- `H5-MECH-DISPLAY-PERFORMANCE` — `EastRising ER-TFT035IPS-6 + ER-TPC035-6`; `Hirose FH34SRJ-50S-0.5SH(50)`; open: i8080/touch operation, optical quality, backlight current/thermal and received flex conformity.
- `H5-MECH-ACOUSTIC-PATHS` — `PUI Audio AS02404PO`; `Same Sky CMEJ-0413-42-SMT-TR`; open: Enclosure acoustic treatment, cavity resonance, sealing, feedback and microphone response.
- `H5-MECH-HEADSET-JACK` — `Same Sky SJ-43504-SMT-TR`; open: Received cutout tolerance, shield and solder-tab fit, enclosure opening, plug insertion/withdrawal force, CTIA and three-pole TRS behavior, retention and unplug transient remain assembled-product properties.

## Honest result boundary

- Every board-fitted part in a mechanical gate has an exact non-TBD MPN.
- Test articles not selected yet are explicit: a reference microSD and the M5 Unit/cable profile set.
- The fitted connector in a received `E01-ML01SP4` and the fitted post on a stock `U214` were not assigned invented MPNs; their makers do not publish them.
- Actual fit, retention, RF, timing and lot identity remain open until H7/H8 owner bring-up of the sole prototype; no separate sample/coupon purchase exists.
- The next exact marker is `H5.0.2-R1`; purchase, PCB placement/routing and fabrication remain prohibited.

Machine result: [`H5-EVR01`](../hardware/verification/generated/H5-EVR01-residual-map.json).
