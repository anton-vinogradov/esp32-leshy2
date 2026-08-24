# Steady-power verification result

[Русский](dc-verification-result.ru.md) · [Home](../README.md) · [DC rails](dc-power-budget.md) · [Sources](source-charge-budget.md)

H3.1 closes as one chain: state register → rail loads → source/charge/discharge → consolidated review. No result substitutes a typical current for a maximum or accepted admission limit.

## Accepted result

- `43` source/charge states, `2032` complete states and `200` rail profiles pass with no unresolved violation.
- Minimum rail protection reserve: `28.359%`.
- Worst SYS case: `16.894 W`; pack: `2.816 A`, with `255.114%` reserve to the 10-A contract.
- 5 V × 3 A without a pack explicitly refuses `14` heavy profiles; this is admission control, not a hidden brownout.

## Corrected during review

- 2.21-kohm external-branch RILM produced only 1.358 A at the guaranteed low corner, below the 1.5625-A PF-02 requirement for a 1.25-A port. Correction: both U214 and native-Unit eFuses now use active/orderable Yageo RC0402FR-071K82L; guaranteed low corner is 1.632 A and high corner is 2.035 A. Functional effect: restores >=30.6% steady reserve and preserves the bounded 2-A post-start transient without changing the connector contract.
- the audio allowance cited an 8-ohm PAM8302A curve although the exact AS02404PO is 4 ohm +/-15%; the display allowance simultaneously treated the TPS2553 fault threshold as a continuous normal load. Correction: reserve 625 mA for amplifier, codec and selectors using the actual 3.4-ohm low corner, and 200 mA for 80-mA display/touch plus the 120-mA normal donor backlight reference. Functional effect: the recalculated 3V3_MAIN worst case is 2493 mA with 28.36% guaranteed hardware reserve; the 174-to-234-mA backlight threshold remains an independent latched fault bound.

## What remains unproven

Steady limits do not replace dynamics or temperature. H3.2 checks startup/shutdown, USB↔pack handover, brownout, DPM, inrush and FAULT_KILL; H3.6 consumes the 2.550-W converter loss and 0.386-W eFuse loss in its thermal model; H8 retains physical measurements.

**Status:** `H3.1` is reviewed. The exact current marker is `H3.3.3`, IR drive/receive/thermal corners.

[Machine H3.1 closure package](../hardware/verification/generated/H3-VRF14-dc-consolidation.json).
