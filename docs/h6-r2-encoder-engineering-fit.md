# H6.0.3-R1 — EC11 encoder engineering fit

[Русская версия](h6-r2-encoder-engineering-fit.ru.md) · [Interface review](h6-r2-interface-review.md)

## What we want

Mount the selected Alps Alpine **EC11E18244AU** at the existing native RF-board shaft axis without changing the controls, MPN, board size or completed copper. This is a local prototype-engineering checkpoint, not fabrication approval or H6 completion.

## What we decided

Use the exact nominal body and terminal axes from Alps **Drawing No.2**, with the shaft at native **[71, 50.25] mm, F.Cu, 0°**. The mounting-lug pitch is **12.5 mm**. Five electrical pad positions and nets stay unchanged; the explicit current-R2 aliases are old `S1 → E`, `S2 → D`. The two undocumented locating holes in the generic footprint are removed. No borrowed 3D model is accepted. [Alps primary drawing](https://tech.alpsalpine.com/cms.media/product_catalog_ec_01_ec11e_en_611f078659.pdf)

The **2.0 × 4.0 mm plated mounting slots**, 2.8 × 4.8 mm copper lands and ordinary **1.1 mm signal holes** are our declared engineering profile, not an Alps-approved replacement land pattern. The detailed finished-hole intervals, conditional mounting-aperture containment and annulus calculation are in the [geometry contract](../hardware/layout/h6-r2-encoder-fit-candidate.json). The conditional 128-corner check separately includes hole-position error and mounting-pitch tolerance under a symmetric-pair assumption; unknown common-mode lug registration relative to the shaft is not qualified. They use the published [JLCPCB standard capabilities](https://jlcpcb.com/capabilities/pcb-capabilities); no new precision process is implicitly selected.

## What we found and corrected

The former generic footprint had an 11.2 mm mounting pitch and the wrong mechanical-hole inventory. Its replacement needs a local rearrangement of 17 supporting parts. The detector's supply bypass, enable-hold RC and external filter capacitor now have explicit physical-pad locality checks. The filter capacitor is close to both `FLTR4` and `V_UP6`; the hold net is a **1 µF / 10 kΩ enable-hold circuit**, not the RF detector output. No completed track or via was removed.

Rotating the encoder by 90°/270° at the same shaft axis was also checked. It moved a mounting slot into completed CC1101 RF copper and added opposite-face conflicts, so that alternative was rejected.

## What we obtained

The reviewed RF candidate is identified by SHA-256 `e11215ffe5cc25645aa091872af93540c121e84d83def5dae3f39c03c782fd32`. Its guarded update changes only the encoder and the declared support group, preserving the other footprints, the five world pad/net pairs and all existing copper. Fresh native DRC and schematic parity both report **zero findings** for this candidate. The UI PCB is unchanged by this checkpoint. Current board-wide counters and later routing changes belong to the [live routing report](h6-r2-current-routing.md), not this fixed candidate record.

The library retains an explicit **mechanics-open engineering status**. Native/library agreement and DRC do not establish insertion, solder strength, assembled access or complete electrical qualification.

## What remains

- **Signal-hole proof is limited:** minimum finished 1.02 mm exceeds the recommended 1.0 mm aperture only in a coaxial comparison. The actual lead cross-section is undocumented; adding the published hole-position error does not prove full reference-aperture containment. This is neither a guaranteed insertion proof nor evidence that the real lead cannot fit.
- **Solder both metal mounting lugs**, even though the two MP pads have no electrical net. Seat the body flush and level; do not wash the encoder. Quantitative solder fill, joint strength and knob torque remain unqualified. [Alps assembly cautions](https://tech.alpsalpine.com/e/products/detail/EC11E18244AU/)
- Check actual inward lead/solder protrusion and opposite-board clearance: the nominal lead projection is 3.5 mm minus the actual finished PCB thickness, not a zero-height 2D pad. Knob and closed-case clearance remain open.
- Route and verify the detector/filter/hold network. The RF tap requires its intended controlled-impedance route; pad-to-pad distances alone do not prove RF response, noise immunity, startup or safety behaviour.

The phase marker remains **H6.0.3-R1**. No order, new MPN or whole-device release is authorized by this result.
