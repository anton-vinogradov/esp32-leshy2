# REV-0005BJ — assembly-internal BOM propagation

Статус: **проведено ревью; full I8 qualification remains active**.

| Проверка | Результат |
|---|---|
| mismatch | fixed: internal `ST77922` no longer appears as separately purchased/costed line |
| architecture | pass: `display` and `display_touch_controller` stay distinct physical/role nodes |
| explicit boundary | pass: child, purchased parent and reason are machine-readable |
| validation | pass: unknown child/parent, self-parent and duplicate exclusion are rejected |
| generated review | pass: publishes 858 architecture / 1 internal / 857 purchase placements / 187 lines |
| generated CSV | pass: `sitronix_st77922` absent; `qdtech_hmx035ctft_001` remains |
| quantities | pass: every other line unchanged |
| hardware/firmware | unchanged: no contact, GPIO, behavior, update or diagram change |
| regression | pass: generated-artifact check and 66 hardware architecture tests, including malformed-boundary rejection |

## Verdict

The purchasing boundary is now reproducible and reviewed. Historical
858/188 snapshots are retained only where they describe the earlier flawed
generator pass and point to this correction. Current I8 numbers are 857/187.
