# H6.0.3-R1 · Electrical pin review

[Home](../README.md) · [Roadmap](roadmap.md) · [Current routing](h6-r2-current-routing.md) · [Русский](h6-r2-electrical-semantics.ru.md)

**Checkpoint: 2026-09-07. Status: partial review; release blocked.**
`H6-NATIVE-ELECTRICAL-SEMANTICS` remains open. This report records corrected
physical pin mappings and an ERC experiment, not completed electrical sign-off.

## What we want

Check that the intended signals reach the correct physical pins, every supply
has a valid source in the relevant operating state, and connected outputs are
compatible. Passing connectivity checks alone cannot establish these facts.

## What we decided

Keep the production symbol library passive until reviewed pin types and the
resulting findings are reconciled. Apply manufacturer-backed electrical types
to isolated copies of both native KiCad projects first. This **typed shadow**
changes pin types only: original and typed XML netlists must have identical
reference/pin-to-net membership on each board. It does not silently repair
topology or add power flags to obtain a clean ERC result.

Confirmed mapping defects are instead corrected at their source, propagated
through the native projects and hardware/firmware contracts, and regression
tested. Component choices and intended product functions remain unchanged.

## What we found and corrected

| Exact part and instance | Correction and significance | Primary evidence |
|---|---|---|
| `SN74LVC1G17DCKR`, RF U122 (`safe_rearm_buffer`) | DCK pin 1 is NC; input A is pin 2. The previous A1/NC2 mapping connected the delay signal to an unused pin and left the real input unconnected. | [TI, Pin Functions, DCK column](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf) |
| `TXS0102DCUR`, RF U102 (`unit_signal_iso`) | DCU map corrected to B2=1, GND=2, VCCA=3, A2=4, A1=5, OE=6, VCCB=7, B1=8. This fixes physical supply/signal assignments, not merely labels. | [TI, Table 4-1, DCT/DCU/DTT column](https://www.ti.com/lit/ds/symlink/txs0102.pdf) |
| `SC1512-A4` (RP2354B), UI U28 / RF U23 (`hub_rp` / `rf_rp`) | Pad 69, QSPI_IOVDD, is restored to `3V3_MAIN`. The internal-flash NC rule had incorrectly included its power supply. Existing 100-nF bypasses C53/UI and C100/RF are retained; no extra parts are needed. | [Raspberry Pi, §14.3 and QFN-80 pin table](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) |
| `74LVC1G32GV,125`, RF U19 / U121 | GV input labels corrected to A=2, B=1. OR is commutative, so this particular swap does not change the logic function. | [Nexperia, Tables 3–4, TSSOP5 column](https://assets.nexperia.com/documents/data-sheet/74LVC1G32.pdf) |

The RP bypass placement rule now measures each capacitor's supply pad against
its owner's **actual pad 69**, with a maximum pad-centre distance of 3 mm.
[Exact-placement evidence](h6-r2-exact-placement.md) owns the measured result;
this geometric limit is not a claim that the final supply loop is routed.

The expanded review adds four source-level corrections, propagated together
through the native projects. This is not electrical sign-off, a new component
selection or a reduction in functionality:

| Exact part and instance | Correction and significance | Primary evidence |
|---|---|---|
| `TPS3839K33DBZR`, RF U66 / U81 | DBZ GND=1 and RESET=2 replace the reversed mapping; VDD remains pin 3. RESET is push-pull, not open-drain. | [TI, §6, SOT-23-3 top view and Pin Functions](https://www.ti.com/lit/ds/symlink/tps3839.pdf) |
| `TPD2EUSB30ADRTR`, UI U21 / U30 and RF U25 | Replace the incorrectly substituted SOT-23 footprint with the exact DRT-3 package, whose body is 1.00 × 0.80 mm. Signal numbering is unchanged; placement and copper must be checked against the real smaller lands. | [TI, DRT package and land-pattern drawings](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf) |
| `B3S-1100P`, UI navigation/function buttons and RF PTT | Manufacturer top view has 4/3 above, 2/1 below and shield 5; permanent common pairs are 1–2 and 3–4. Correct footprint numbering and logical mapping together, preserving each existing physical land's intended net. | [OMRON, Terminal Arrangement/Internal Connections, p2](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf) |
| `FH34SRJ-50S-0.5SH(50)`, UI J1 | Manufacturer contact 1 is on the right when the solder row is above the body. Correct the footprint and explicitly map panel contact `n` to connector contact `51−n`. The installed pose, upward panel-tail exit and untwisted fold stay unchanged; matching numbers on two different parts is not an electrical requirement. | [Hirose, FH34SRJ mounting and FPC patterns, p8](https://www.hirose.com/en/product/document?clcode=CL0580-1232-0-50&documentid=en_FH34_CAT&documenttype=Catalog&lang=en&productname=FH34SRJ-30S-0.5SH%2850%29&series=FH34SRJ) |

For `HMC544AETR`, the source link is corrected from the older non-A datasheet
to the [exact HMC544A/544AE document](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc544ae.pdf).
Its physical mapping and selected part are unchanged. The display mating rule
is owned by the [assembly contract](../hardware/product-design/display-mount.json);
it does not remove the received-panel dry-fit, contact-face or slack checks.

All existing component poses are preserved. The B3S and display corrections
also preserve each physical land's intended net. Fresh PCB DRC has no
violations on either board, but neither that result nor the completed source
regeneration closes the electrical review below. Current routing and placement
reports own the geometry and copper counts.

## What we obtained

The final hardware regression run passed all **616 tests**. Visual inspection
of the manufacturer PDF drawings resolved the package/view ambiguities;
independent pad-map and native-connectivity tests now guard these corrections.

The [hash-bound electrical audit](../hardware/verification/generated/H6-R2-electrical-semantics.json)
now draws on **seven source maps with 1,289 reviewed pin types across 158
exact-part groups**: digital, logic, power, analog/RF, protection, interfaces
and selected passives. This is not a percentage of completed electrical
verification. Mechanical pads, unreviewed parts and unresolved electrical pins
remain in the inventory; uncertain types are not counted as verified passive
pins. A passive RF terminal or connector contact proves neither matching/bias
nor correct external mating, and an ordinary passive component type does not
prove its value or operating margins.

Both expanded native projects retain identical electrical membership between
original and typed XML exports. Their fresh isolated ERC reports:

- UI: 5 `power_pin_not_driven` findings.
- RF/power: 17 `power_pin_not_driven` findings and one output-to-output finding
  on charger ACDRV1/ACDRV2, which share the ground net in the unused-driver
  configuration.

The additional RF supply finding comes from reviewing the PGA-103+ shared
RF-output/DC-input pad: its external DC bias is a supply obligation, not a
power source. In total, 22 power findings and one output conflict remain.
The linked audit owns the per-board results and membership-parity evidence;
the electrical release gate remains open.

The [source-path triage](../hardware/verification/h6-electrical-source-triage.json)
explains observed paths through M1, inductors, resistors, ferrites, diodes and
bootstrap circuits. It has **not cleared the ERC findings**. An observed path
is not proof of start-up, sufficient voltage or valid switching states; the
ACDRV case also needs its exact configuration-specific justification retained.
No blanket suppression or unconditional rail-source flag is accepted.

The corrected H2/H3 boundary was synchronized to firmware without changing
generated BSP code, controller GPIO assignments, display scheduling or
transport APIs. One new clean twelve-job qualification compiled and linked
all six targets in debug/release and verified their declared artifacts.
[Firmware evidence](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/f2_r2_build_qualification.json)
owns that build result, not powered hardware, PSRAM operation or complete
electrical correctness. Historical H4 evidence was not rewritten as a fresh test.

Historical H2 sheet checks now reproduce their original, hash-locked device
input through an [explicit legacy boundary](../hardware/ecad/h2_legacy_device_basis.py).
Their old outputs remain unchanged and cannot authorize R2; current native R2
checks use the corrected live register.

## What remains

One exact-package question needs manufacturer clarification: `PAM8302AAYCR`
(U-DFN3030-8 Type E) has a centre exposed pad drawn in
[DS41333 Rev. 6-2](https://www.diodes.com/datasheet/download/PAM8302A.pdf), but
the document does not assign it an electrical net. The official
[evaluation-board guide](https://www.diodes.com/assets/Evaluation-Boards/PAM8302A-User-Guide.pdf)
uses a leaded package and does not establish the DFN pad connection. Neither
ground nor a thermal-only, isolated pad is assumed. Diodes needs to confirm
whether it is internally connected or isolated, which net is permitted or
required, and whether solder attachment or thermal vias are mandatory. The
[inquiry was submitted on 2026-09-07](../hardware/procurement/PAM8302AAYCR-exposed-pad-clarification.md)
and the official support form confirmed receipt. A technical answer is pending;
the exposed-pad connection remains unresolved.

1. Complete the missing exact-pin review and model configuration-dependent GPIO,
   open-drain pull-ups, tri-state enables and unused outputs.
2. Verify supply reachability across both boards and series components, including
   converter prerequisites, external-source presence and power transitions.
3. Resolve every native ERC finding with a correction or a narrowly justified,
   machine-checked configuration rule; explanations alone do not close it.
4. Reconcile reviewed types into the controlled production library, repeat
   connectivity parity and native ERC, and close the electrical-semantics gate
   before claiming H6.0.3 complete. Routing, routed electrical checks and the
   remaining [release work](roadmap.md) are still required.

## Reproduce this checkpoint

```bash
python3 hardware/verification/h6_r2_electrical_semantics.py --check
python3 hardware/verification/h6_r2_electrical_source_triage.py --check
python3 -m unittest hardware.architecture.tests.test_h6_r2_pinmap_corrections hardware.architecture.tests.test_h6_r2_electrical_semantics hardware.architecture.tests.test_h6_r2_electrical_source_triage
```

These checks validate the partial evidence and its limitations, not a clean
electrical release. After schematic, type-map or verifier changes, rerun
`h6_r2_electrical_semantics.py --write` to obtain fresh isolated native ERC,
then review any changed findings before updating the source-path triage.
