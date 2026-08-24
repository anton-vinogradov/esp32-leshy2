# Digital levels, defaults and no-back-power

`H3.4.1` is reviewed: `73` machine checks cover all `130` controller allocations, `13` digital interface groups, `13` quiet-state contracts and all six no-back-power invariants. No analytical finding or component change remains open. The exact current marker is `H3.6.1`.

## Guaranteed static margins

| Boundary | Worst reviewed result |
|---|---|
| LVC buffered 3.3-V paths | `VOH-VIH >= 0.200 V`; `VIL-VOL >= 0.250 V` at the much harsher 24-mA data-sheet point; actual 10-kOhm pull load is <=`0.329 mA` |
| Direct common-rail CMOS | same instantaneous rail; conservative high margin `0.155 V`, low margin `0.466 V` at the minimum reviewed rail |
| SYS_I2C open drain | 2.2-kOhm pull-up sinks <=`1.545 mA`; guaranteed low margin `0.400 V`; no push-pull high crosses the AON/main boundary |
| Service USB | exact FSUSB42MUX power-off isolation and sense-only VBUS pass; USB differential SI is bounded in H3.4.3 and physically checked in H8, not disguised as a CMOS margin |

Every switched domain has an off-safe enable, a local line default and either exact `Ioff`, a powered-main open switch, powered-off-high-Z I2C isolation or a same-rail/no-partial-power proof. The three nRF24 paths remain fully independent and all six signals per module are isolated in both directions.

## What paper review does not close

Five measurements remain explicit H8 gates: powered-off leakage, reset/brownout captures, simultaneous service-host injection, wrong-accessory reverse current and far-end M1 logic levels under load. They are not reported as paper passes.

Machine evidence: [`H3-VRF41-digital-levels.json`](../hardware/verification/generated/H3-VRF41-digital-levels.json).
