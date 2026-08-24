# Battery sensing and thermal analog verification

H3.3.4 is reviewed with `38` machine checks and four source corrections. No component or BOM-cost change is required. The exact current marker is `H3.4.4`: digital levels/defaults and no-back-power.

## What is now fixed

- The actual MSPM0C1106 DGS20 contacts are used: pack midpoint `PA25/ADC0_2` pin 20, pack stack and POWER `PA26/ADC0_1` pin 1, RF/VOICE `PA27/ADC0_0` pin 2, and UI `PA16/ADC0_14` pin 12.
- Pack dividers use the internal 1.4-V reference. At the 4.3/8.6-V electrical screen their worst nodes are `1.222851` and `1.180070` V, leaving `157.149` and `199.930` mV to the minimum reference. Wait 20 ms, discard two conversions and average at least eight.
- The divider ADC is deliberately gross independent evidence: full-corner reconstruction can move by `-0.190..+0.196` V for the midpoint and `-0.427..+0.443` V for the stack. MAX17320 remains the precision per-cell/imbalance instrument.
- Every 10-kohm/10-kohm board NTC divider uses ADC `VDD` as its reference. Internal 1.4 V would saturate it at room temperature. Warning, kill and rearm are code-bounded at `880`, `740` and `1000`; open is `>=4000`, short is `<=64`.
- The BQ25798 path remains a third independent cell sensor. `TS_IGNORE=0`, `TS_WARM=0`, `JEITA_ISETH=0`; open and short suspend charge. The full-corner warm suspend is `38.00..41.03 C`.
- MAX17320 uses both cell NTCs and exact `nThermCfg=0x71B1`. The operational request becomes zero above 35 C, charge is blocked around 40 C, discharge at 60 C, while board hot spots warn by 65 C and latch `FAULT_KILL` by 75 C.

## Admission boundary

Each MAX17320 cell reading must be 2.70..4.25 V and pair imbalance at most 100 mV. In parallel, midpoint/stack/derived-upper ADC plausibility must be 2.45..4.50, 4.90..9.00 and 1.90..5.10 V. Protected image/checksum, PFAIL and diagnostic-pulse evidence must all agree before the external FET hold releases.

The midpoint divider adds only `0.339` mAh of lower-cell imbalance over 48 hours. This is negligible for the one-to-two-day unattended mission, but long storage and balancing heat remain explicit HIL measurements.

## Corrections

| ID | Corrected result |
|---|---|
| H3.3.4-F01 | Board NTC conversions are VDD-ratiometric; the 1.4-V reference is pack-only. |
| H3.3.4-F02 | BQ25798 and MAX17320 now have explicit machine-readable reset/readback configuration contracts. |
| H3.3.4-F03 | Exact B25/85=3435 K produces MAX17320 `nThermCfg=0x71B1`. |
| H3.3.4-F04 | Exact XTAR electrical limits are now machine-readable; the product retains the 2-A ceiling and a narrower thermal policy. |

## What paper evidence does not close

Sensor bonding and response, ADC calibration, received-cell identity, actual charger thresholds, balance heat and every open/short/reversed/imbalanced fault remain physical HIL gates. The generated evidence is [`H3-VRF34-battery-analog.json`](../hardware/verification/generated/H3-VRF34-battery-analog.json).
