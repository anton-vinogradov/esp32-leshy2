# FND-0103 — cross-group HIL could reopen forbidden concurrency

- Статус: **Исправлено; проведено ревью**
- Scope: consolidated I6 qualification semantics
- Correction: [`COX-0001`](../architecture/COX-0001-consolidated-i6-qualification-matrix.md), [`DEC-0097`](../decisions/DEC-0097-one-group-i6-qualification-and-fixtures.md)

## Несоответствие

`DEC-0045` states that exactly one top-level signal group may be active. The
older neutral `RFQ-0001` matrix and two later carry-over rows still used `Q`
for selected cross-group pairs and described promotion after conducted/OTA HIL.
That wording could let a measurement silently create a runtime state that the
owner had explicitly prohibited.

The contradiction affected S3/C5 versus nRF, voice versus CC/Si4732, C5 5 GHz
versus other receivers and external NFC versus another receive session. It did
not affect required concurrency inside `SG-N24`, visible native-chain TDM or
the LoRa/GNSS support members of one exact U214 manifest.

## Исправление

- every independent cross-group pair is `X-RUNTIME` without a promotion path;
- contained RF/optical injection remains `LAB-CHAR` for blocking, false
  evidence, residual-transition energy and recovery tests only;
- every evidence record states that Laboratory characterization cannot modify
  the runtime group catalog or permission state;
- only explicitly declared members of one group may run concurrently;
- regression tests reject the former cross-group-promotion wording.

No radio capability is removed: the groups switch atomically and each radio
remains full-function when its group owns the signal plane. The correction adds
no component, GPIO, cost or performance ceiling.

