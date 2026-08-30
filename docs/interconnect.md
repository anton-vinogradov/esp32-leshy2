# M1 inter-board connection

[Home](../README.md) · [Hardware](hardware.md) · [Русский](interconnect.ru.md)

The UI and RF/power PCBs use one exact straight-SMT `Hirose FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` pair at an 11.00-mm working gap. All 80 contacts are defined below; no electrical tail protrudes through either outer face.

## 80-contact budget

`29` live signals · `14` main-power · `2` AON · `24` defined returns · `11` NC reserve

The main rail uses **14** parallel contacts and the same number of primary returns. Continuous `3.75 A` is `0.2679 A/contact`; the `4.25 A` step is `0.3036 A/contact` against a `0.4 A` rating.

## Mechanical load path

M1 is electrical/alignment only. Four exact 11.00-mm compression stops, at least two enclosure anti-shear datums and independent capture of both PCBs prevent separation or relative shear even with one screw loosened. Ordinary handling, battery installation and enclosure flex are carried by the fasteners, stops, datums and capture lips rather than the M1 SMT joints.

## Principle grouping

| Contacts | Assignment |
|---|---|
| `1–16` | 8 × POWER_GROUND + 3V3_MAIN pairs |
| `17–20` | 2 × AON_SAFE_3V3 with safety returns |
| `21–28` | Hub↔RF RP dedicated SPI + alert and returns |
| `29–31` | S3 product USB 2.0 D−/D+ + return |
| `32–34` | fail-closed Pack/Safety I²C + return |
| `35–36` | 2 NC reserve contacts |
| `37–40` | RUN, fault and UI thermal safety crossings + return |
| `41–50` | 9 actual-TX evidence signals + safety return |
| `51–54` | rear encoder A/B/push + return |
| `55–59` | AON service ownership/control and alert |
| `60–64` | 5 NC reserve contacts |
| `65–76` | 6 × POWER_GROUND + 3V3_MAIN pairs |
| `77–80` | 4 NC reserve contacts |

<details><summary>Complete contact map</summary>

| Contact | Net | Class |
|---:|---|---|
| `1` | `POWER_GROUND` | `main_return` |
| `2` | `3V3_MAIN` | `main_power` |
| `3` | `POWER_GROUND` | `main_return` |
| `4` | `3V3_MAIN` | `main_power` |
| `5` | `POWER_GROUND` | `main_return` |
| `6` | `3V3_MAIN` | `main_power` |
| `7` | `POWER_GROUND` | `main_return` |
| `8` | `3V3_MAIN` | `main_power` |
| `9` | `POWER_GROUND` | `main_return` |
| `10` | `3V3_MAIN` | `main_power` |
| `11` | `POWER_GROUND` | `main_return` |
| `12` | `3V3_MAIN` | `main_power` |
| `13` | `POWER_GROUND` | `main_return` |
| `14` | `3V3_MAIN` | `main_power` |
| `15` | `POWER_GROUND` | `main_return` |
| `16` | `3V3_MAIN` | `main_power` |
| `17` | `AON_SAFE_3V3` | `aon_power` |
| `18` | `SAFETY_GROUND` | `safety_return` |
| `19` | `AON_SAFE_3V3` | `aon_power` |
| `20` | `SAFETY_GROUND` | `safety_return` |
| `21` | `POWER_GROUND` | `ipc_return` |
| `22` | `HUB_RF_ALERT_N` | `ipc` |
| `23` | `HUB_RF_CS_N` | `ipc` |
| `24` | `HUB_RF_SCK` | `ipc` |
| `25` | `POWER_GROUND` | `ipc_return` |
| `26` | `HUB_RF_MOSI` | `ipc` |
| `27` | `HUB_RF_MISO` | `ipc` |
| `28` | `POWER_GROUND` | `ipc_return` |
| `29` | `S3_USB_DM` | `usb2` |
| `30` | `S3_USB_DP` | `usb2` |
| `31` | `POWER_GROUND` | `usb_return` |
| `32` | `HUB_SAFE_I2C_SDA` | `control` |
| `33` | `HUB_SAFE_I2C_SCL` | `control` |
| `34` | `POWER_GROUND` | `control_return` |
| `35` | `NC_35` | `reserve` |
| `36` | `NC_36` | `reserve` |
| `37` | `RUN_PERMIT` | `safety` |
| `38` | `FAULT_ASSERT_N` | `safety` |
| `39` | `UI_ZONE_TEMP_ADC` | `safety_analog` |
| `40` | `SAFETY_GROUND` | `safety_return` |
| `41` | `EV_N0_S3` | `tx_evidence` |
| `42` | `EV_N1_C5` | `tx_evidence` |
| `43` | `EV_N2_NRF0` | `tx_evidence` |
| `44` | `EV_N3_NRF1` | `tx_evidence` |
| `45` | `EV_N4_NRF2` | `tx_evidence` |
| `46` | `EV_N7_IR` | `tx_evidence` |
| `47` | `SAFETY_GROUND` | `safety_return` |
| `48` | `EV_N5_CC` | `tx_evidence` |
| `49` | `EV_N6_VOICE` | `tx_evidence` |
| `50` | `EV_N8_LORA_EXT` | `tx_evidence` |
| `51` | `ENCODER_A` | `ui` |
| `52` | `ENCODER_B` | `ui` |
| `53` | `UI_ENCODER_PUSH_N` | `ui` |
| `54` | `POWER_GROUND` | `ui_return` |
| `55` | `C5_MUX_SEL_REQUEST` | `aon_service_control` |
| `56` | `C5_SERVICE_PATH_ACK` | `aon_service_control` |
| `57` | `AON_SERVICE_RELEASE_REQ` | `aon_service_control` |
| `58` | `C5_SERVICE_OWNED` | `aon_service_status` |
| `59` | `HUB_AON_ALERT_N` | `aon_status` |
| `60` | `NC_60` | `reserve` |
| `61` | `NC_61` | `reserve` |
| `62` | `NC_62` | `reserve` |
| `63` | `NC_63` | `reserve` |
| `64` | `NC_64` | `reserve` |
| `65` | `POWER_GROUND` | `main_return` |
| `66` | `3V3_MAIN` | `main_power` |
| `67` | `POWER_GROUND` | `main_return` |
| `68` | `3V3_MAIN` | `main_power` |
| `69` | `POWER_GROUND` | `main_return` |
| `70` | `3V3_MAIN` | `main_power` |
| `71` | `POWER_GROUND` | `main_return` |
| `72` | `3V3_MAIN` | `main_power` |
| `73` | `POWER_GROUND` | `main_return` |
| `74` | `3V3_MAIN` | `main_power` |
| `75` | `POWER_GROUND` | `main_return` |
| `76` | `3V3_MAIN` | `main_power` |
| `77` | `NC_77` | `reserve` |
| `78` | `NC_78` | `reserve` |
| `79` | `NC_79` | `reserve` |
| `80` | `NC_80` | `reserve` |

</details>

> The source of truth is `hardware/architecture/h0-r2-rebaseline.json`; this table is generated from it.
