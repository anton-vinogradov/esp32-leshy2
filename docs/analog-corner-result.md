# Consolidated analog-corner result

H3.3 is reviewed: all four leaf packages and `153` leaf checks pass, followed by `22` consolidation checks. Fourteen source corrections are closed, no analytical finding remains open and the total quantity-100 BOM delta is only `0.4908 USD`. The exact current marker is `H3.5.1`.

## Closed analytical envelope

| Path | Reviewed result |
|---|---|
| Display | 3.108510..3.285658 V connector supply; 40-MHz initial QSPI; dirty/tile work sliced to <=1 ms |
| Audio | 4-ohm speaker corner, complete capture/playback/TX paths and 625-mA branch; playback mutes above 50 C |
| IR | >=20-mA characterized optical point, <=50.513-mA conservative instantaneous current, 20-ms mark/trip and 75-C local limit |
| Battery/thermal | exact DGS20 ADC contacts, independent MAX/BQ/ADC evidence, 35-C charge-request cutoff, 40-C charge block, 60-C cell-discharge block and 65/75-C board warning/kill |

The temperature rules are deliberately ordered: charge request zero at 35 C, BQ backup no later than 41.03 C, speaker mute at 50 C, cell discharge block at 60 C, board warning by 65 C and `FAULT_KILL`/IR local ceiling at 75 C. The display quantum is shorter than every safety deadline and no radio FIFO shares its bus.

## Shared-rail caveat

The enumerated 3V3_MAIN profile is `2493 mA` against a `2500 mA` analytical allocation. Its hardware protection reserve is still `28.359%`, but the 7-mA paper gap is not manufacturing margin. H3.6 and H8 must measure <=2.5 A; an excess reopens allowances or functionality before layout or ordering.

## Physical boundary retained

All 17 physical-only items remain explicit HIL gates: display signal integrity/current/optics, audio gain/noise/acoustics/RF immunity, IR coupling/range/IEC 62471/temperature, and battery identity/calibration/sensor response/charge thresholds/balance heat. H3.3 does not turn those into paper passes.

Machine evidence: [`H3-VRF35-analog-consolidation.json`](../hardware/verification/generated/H3-VRF35-analog-consolidation.json).
