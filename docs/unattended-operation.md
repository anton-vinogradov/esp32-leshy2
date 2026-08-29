# Extended operation and self-test · historical R1

`H3.6.3` is reviewed. The product promises no battery autonomy or uptime in hours: long operation uses USB-PD, while 24 and 48 hours remain H8 validation durations.

The pre-physical engineering target is `0 to 35 °C`, not a datasheet guarantee. At 35 °C H6 must achieve no worse than `16.713 K/W` for quiet and `5.446 K/W` for heavy voice RX.

`Settings > Safety > Full self-test` offers `24 hours`, default `48 hours`, and `startup only`. A change activates after the next physical `KILL to RUN`. This fault-plane proof is service-interrupting but does not damage hardware. The setting cannot alter watchdog, thermal FAULT_KILL or TX-lease behavior.

| Group | Heavy SUPPORT_IDLE case | Ideal minimum-energy ceiling, not a promise |
|---|---|---:|
| `BROADCAST_RX` | `FM_AM_SW_LW_RX` / 1.892 W | 14.46 h |
| `C5_RF` | `2G4_RX` / 1.778 W | 15.39 h |
| `CC1101` | `RX` / 1.933 W | 14.15 h |
| `IR` | `LEARN_OR_RAW_RX` / 2.044 W | 13.39 h |
| `LORA_CAP` | `STOCK_U214_RX_GNSS_ONLY` / 9.207 W | 2.97 h |
| `M5_UNIT` | `QUALIFIED_PROFILE_RX_OR_PASSIVE` / 9.207 W | 2.97 h |
| `NONE` | `QUIET` / 1.778 W | 15.39 h |
| `NRF24` | `3PRX` / 3.323 W | 8.23 h |
| `S3_RF` | `2G4_RX_OR_SCAN` / 1.778 W | 15.39 h |
| `VOICE` | `RX` / 5.406 W | 5.06 h |

The table is H8 planning only: it excludes ageing, cutoff, lot spread, temperature and real duty. SUPPORT_WORST, continuous TX and unknown accessories are not admitted as extended modes.

[Machine evidence](../hardware/verification/generated/H3-VRF63-unattended-envelope.json).
