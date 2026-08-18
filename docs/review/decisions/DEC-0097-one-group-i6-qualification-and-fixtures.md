# DEC-0097 — one-group I6 qualification and fixtures

- Статус: **Принято автоматически; paper I6 проведён ревью, physical HIL open**
- Дата: 2026-08-18
- Architecture: [`COX-0001`](../architecture/COX-0001-consolidated-i6-qualification-matrix.md)
- Findings: [`FND-0103`](../findings/FND-0103-cross-group-hil-could-reopen-forbidden-concurrency.md), [`FND-0104`](../findings/FND-0104-monolithic-receiver-audio-quiet-contract.md)

## Решение

1. Preserve `DEC-0045` literally: at most one top-level signal group is active;
   no cross-group HIL result may add a runtime pair.
2. Treat contained cross-group injection as Laboratory robustness/fault
   characterization only.
3. Split the contradictory `RECEIVER_AUDIO_QUIET` into independent
   `RECEIVER_QUIET`, `CODEC_AUDIO_QUIET` and `VOICE_INTERFACE_QUIET` contracts.
4. Require every group, every allowed intragroup mode, every installed ordered
   group transition and all eight evidence channels in one versioned matrix.
5. Freeze eight functional fixture classes for configuration, conducted, OTA,
   nRF observer, optical, digital timing, fault and thermal proof.
6. Accept a profile only from raw calibrated traces against its exact manifest;
   unknown identity, false-negative evidence, missed deadline or failed safety,
   legal, thermal or performance limit leaves `NONE` and reopens the owner.
7. Mark consolidated I6 paper scope reviewed without claiming unexecuted HIL.
   Advance paper work to I7; neither KiCad nor integrated mockup is authorized.

## Consequences

- no components, pins, rails, capabilities or cost are added;
- the exact meaning of every quiet state is now group-aware and testable;
- SG-N24 remains the mandatory three-radio full-mix exception;
- system planes remain responsive but receive no RF permission;
- physical I6 evidence is a named reopen gate rather than hidden prose.

