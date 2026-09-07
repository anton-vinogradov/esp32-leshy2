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

## What we obtained

The [hash-bound electrical audit](../hardware/verification/generated/H6-R2-electrical-semantics.json)
records **683 reviewed pin types across 48 exact-part groups**. The contact
inventory contains 1,575 distinct named pads across its component groups;
that is not a useful completeness denominator: mechanical pads, unreviewed
passives and unresolved electrical pins are mixed into it. Uncertain pin types
remain explicitly unreviewed, not counted as verified passive pins.

Both boards retain identical electrical membership between original and typed
XML exports. The isolated ERC nevertheless reports:

- UI: 5 `power_pin_not_driven` findings.
- RF/power: 16 `power_pin_not_driven` findings and one output-to-output finding
  on charger ACDRV1/ACDRV2, which share the ground net in the unused-driver
  configuration.

The [source-path triage](../hardware/verification/h6-electrical-source-triage.json)
explains observed paths through M1, inductors, resistors, ferrites, diodes and
bootstrap circuits. It has **not cleared the ERC findings**. An observed path
is not proof of start-up, sufficient voltage or valid switching states; the
ACDRV case also needs its exact configuration-specific justification retained.
No blanket suppression or unconditional rail-source flag is accepted.

The corrected physical boundary was synchronized to firmware and its twelve
target/configuration builds were requalified. This checks the build contract,
not powered hardware, PSRAM operation or complete electrical correctness.
[Firmware evidence](https://github.com/anton-vinogradov/esp32-leshy2-firmware/tree/e7e613c830d17617b574411ef10a2b21c7073126)
owns those results; historical H4 evidence was not rewritten as a fresh test.

Historical H2 sheet checks now reproduce their original, hash-locked device
input through an [explicit legacy boundary](../hardware/ecad/h2_legacy_device_basis.py).
Their old outputs remain unchanged and cannot authorize R2; current native R2
checks use the corrected live register.

## What remains

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
