# DEC-0101 — exact actual-TX threshold and domain isolation

Статус: **принято автоматически в предоставленных пределах; проведено ревью paper electrical scope**.

> Subsequent `FND-0112/BOM-0011` corrects one unrelated assembly-internal
> display-controller purchasing duplicate. The 858/188 count below remains
> the threshold-repair snapshot, not the current 857/187 purchase view.

## Контекст

I2 already accepted eight physical TX-evidence channels. I8 exposed that their
threshold networks and several mandatory support placements remained abstract,
while three AON signals reached main-domain MCU inputs without a proved
power-off boundary. The owner has authorized automatic component/support
repairs that preserve function and do not materially inflate budget.

## Решение

1. Instantiate a separate R1/R2/R3/RPU network for every comparator channel.
2. Use 100 kΩ / 10 kΩ / 1 MΩ / 10 kΩ as the first population for all seven RF
   channels; use 12 kΩ for the IR lower leg to clear its 0.30-V nominal idle.
3. Keep these values explicitly provisional until per-path HIL calibrates
   detector/optical distributions and threshold tolerance.
4. Instantiate separate 100-nF bypass placements for both TLV1824 packages,
   the TCA9534A source mask and the new isolator; instantiate source-mask
   power, address and local-I2C contacts.
5. Use one exact `SN74LVC3G07DCUR` on AON to transfer C5 RF evidence, IR
   evidence and ANY-TX as non-inverting passive-drain signals into three
   separately pulled-up `3V3_MAIN` inputs.
6. Give `ANY_TX_AON_N` its own 10-kΩ logic pull-up and the LED its own exact
   2.2-kΩ current resistor.
7. Preserve all GPIO assignments, active-low firmware semantics, hard-STOP
   behavior, radio functions and the ban on claiming unmeasured TX evidence.

## Следствия

- The abstract threshold gap family is closed; four physical gap families
  remain.
- BOM becomes 858 placements / 188 used MPN lines. The only new MPN line is
  the active/orderable triple buffer; all passives reuse existing exact lines.
- Current orderability coverage becomes 155/188; the exact TLV1824 and new
  buffer checks reduce missing current-source evidence to 33 lines.
- No GPIO, firmware polarity or product capability changes.
- KiCad and physical freeze remain unauthorized pending the rest of I8, I9 and
  the stated HIL gates.
