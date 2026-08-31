# H4-R2 global result · joined pre-layout gate

[Русский](h4-r2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Stage results](stage-results.md#h4)

**H4-R2 is reviewed.** The current mechanics, native ECAD, virtual electrical evidence and hardware-visible firmware boundary now form one consistent pre-layout package. No cross-domain contradiction remains.

```text
H1 mechanics ─┐
H2 ECAD ──────┼─> H4 joined gate ──> H5 identity/factory evidence
H3 analysis ──┤                    ├─> H6 routed proof
FW BSP/build ─┘                    └─> H8 physical measurements
```

## Result at a glance

| Joined evidence | Reviewed result |
|---|---:|
| Hash-bound inputs | 24 |
| Compute domains | 6 |
| H2 controller rows represented in BSP | 173 / 173 |
| M1 contacts reconciled | 80 / 80 |
| Qualified target configurations | 12 / 12 |
| Remaining cross-domain contradictions | 0 |
| Open analytical findings | 0 |

The audit first found a real 38-row BSP-generation omission in C5, Pack and Safety. The original `135/173` diagnostic remains preserved; H4-R2.2 then restored all rows, added fail-closed mapping/count guards and requalified 60 artifacts, 16 maps and 16 size gates without warnings.

## What deliberately remains open

H4 transfers, rather than hides, all **51 physical residuals**: 1 to H5, 5 to H6 and 46 to H8. F5/F6 still owns one direct-i8080 implementation obligation. Runtime boot, routed geometry and measurements on the sole assembled prototype are therefore not claimed here.

H4 does **not** authorize component purchase, PCB placement/routing or fabrication. The current hardware work is **`H5.0.3-R1`**, completing the exact-one-prototype component/factory route without silent substitution.

[Machine acceptance package](../hardware/verification/generated/H4-R2-acceptance-package.json) · [BSP correction](h4-r2-correction-closure.md) · [input freeze](h4-r2-input-freeze.md).
