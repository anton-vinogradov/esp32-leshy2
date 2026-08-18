# FND-0091 — TCA9534A address range was wrong in the artifacts

- Status: **исправлено; Проведено ревью по primary datasheet**
- Scope: RP TX-evidence mask and S3 ordinary-control expander
- Primary source: [TI TCA9534A Rev. C datasheet](https://www.ti.com/lit/ds/symlink/tca9534a.pdf)

## Finding

The registered MPN is `TCA9534APWR`, but earlier safety and runtime artifacts
assigned its all-low address straps to seven-bit address `0x20`. The exact TI
address byte is `0 1 1 1 A2 A1 A0 R/W`, so the valid seven-bit range is
`0x38…0x3F`. The old value belonged to a different address family and could not
select this physical MPN.

The same error was briefly copied into the new UI-expander candidate as
`0x27`. Exact address correction is therefore:

- RP-local evidence mask, A2/A1/A0 low: `0x38`;
- S3-internal UI matrix, A2/A1/A0 high: candidate `0x3F`.

The TPS25751D address `0x20` is unrelated and remains unchanged.

## Correction and boundary

The machine registry now carries the complete strap-to-address table and the
regression test checks both endpoints. Machine routes, safety architecture and
firmware inputs use `0x38`/`0x3F`. No pin, strap, control identity or safety
function changes. The assembled S3 SYS-I2C collision scan is still required
because the exact display touch controller is not yet frozen.
