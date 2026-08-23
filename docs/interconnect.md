# M1 inter-board connection

[Home](../README.md) · [Hardware](hardware.md) · [Русский](interconnect.ru.md)

The two boards use one exact 80-contact pair at the working 11-mm board spacing: `Hirose FX8C-80P-SV1(92)` on the UI board and `Hirose FX8C-80S-SV5(92)` on the RF/power board. Both parts use 0.6-mm pitch, are rated for 8 Gbit/s and up to 0.4 A per contact; the connector is not an enclosure fastener.

## UI/control board

- Compute: `ESP32-S3-WROOM-1U-N16R8` owns UI, display, storage and audio; `ESP32-C5-WROOM-1U-N8R8` owns native 2.4/5-GHz radio and IR.
- Interfaces: `HMX035CTFT-001 (QDtech schematic assembly marking)`, microSD, `Everest Semiconductor ES8311`, `Si4732-A10-GSR`, CTIA headset, D-pad, BACK, OPT and F1…F8.
- Local safety: S3/C5 hardware reset, IR gate and analog S3/C5/IR transmit evidence.
- C5 service: a separate data-only `GCT USB4105-GF-A` USB-C receptacle.

## RF/power board

- Real-time radio domain: `SC1512-A4`, three `Ebyte E01-ML01IPX`, `CC1101RGPR` and `NiceRF SA518`.
- External modules: removable `M5Stack U214 Cap LoRa-1262` on exact vertical `Samtec HLE-107-02-G-DV-PE-LC` of the raised rear rail and an independent M5 Unit port on exact `1125R-SMT-4P`.
- Power and product USB-C: `JAE DX07S016JA1R1500`, `Texas Instruments TPD4S201RUKR` protection, `Texas Instruments TPS25751DREFR` USB-PD, charger, cells and every rail converter.
- Rear-board audio: `Same Sky CMEJ-0413-42-SMT-TR` microphone with local bias, `Diodes Incorporated PAM8302AASCR` differential amplifier and `PUI Audio AS02404PO` speaker.
- Rear controls: encoder and PTT; the single side RUN/KILL switch supplies both the safety state and low-current source command.
- Local safety: `Texas Instruments MSPM0C1106SDGS20R`, `Texas Instruments TPS3435CAKAGDDFR`, FAULT_KILL latch, three thermal zones, hardware gates and physical transmit evidence.

## Why the split is arranged this way

- raw USB VBUS, CC, negotiated high voltage, charger and battery current remain entirely on the RF/power board
- speaker class-D BTL switching remains on the RF/power board; only low-level differential audio crosses M1 with adjacent AUDIO_GROUND
- the internal microphone body remains on the RF/power board; its quiet bias/filter network and the headset bias remain UI-local, so the single biased MIC_RAW conductor crosses M1 once beside AUDIO_GROUND to the internal/headset selector, after which one MIC_SELECTED_RAW source feeds both capture and transmit selectors
- S3/C5/IR detector analog outputs and the IR carrier remain on the UI board; nRF/CC/voice detector analog outputs remain on the RF board
- RUN/KILL conditioning, the independent watchdog, safety controller and FAULT_KILL latch remain on the RF/power board; only digital RUN_PERMIT, split reset gates, UI temperature and read-only status cross M1
- six RF-board TX-evidence lines cross M1 to their individual front indicators; the UI-local S3, C5 and IR paths also drive their own LEDs, while the one system ANY_TX_AON_N aggregate remains on the RF/power safety plane
- only encoder push and phases cross M1; F1 through F8 are UI-local and PTT is local to the RP/voice domain

## Contact budget

- 80 positions total; 0 reserved and no-connect.
- 7 × `3V3_MAIN`, 2 × `AON_SAFE_3V3`.
- 22 power returns, 3 audio returns and 2 safety returns.
- Raw VBUS/PD high voltage, battery current, analog TX-detector outputs, IR carrier and class-D speaker outputs do not cross M1.

## Physical passage through the sandwich

Every inter-board net listed below crosses only inside the single M1 body: the 11-mm air channel contains no separate USB, IPC, I2C, audio, control or power cable. Their shared mechanical conflict with components is therefore checked once against the complete keep-out of the exact `FX8C-80P-SV1(92)` / `FX8C-80S-SV5(92)` pair. That pair is the one intentional mate and clears every unrelated body on both boards. The five RF microcoaxes, display adapter, pass-through U214 socket, nine antenna-connector tails and seven encoder through-board features are checked separately.

This closes physical bodies and the inter-board air channel, not PCB routing. Fan-out from all 80 contacts, via fields, return paths, impedance and electrical clearances become proven only after ERC/DRC of the routed KiCad boards. Until then the map below is the accepted net assignment, not a claim that copper is already routed.

## Exact contact map

| Contact | Net | Direction | Class |
|---:|---|---|---|
| `1` | `POWER_GROUND` | return | `return` |
| `2` | `RP_ALERT_N` | RF→UI | `ipc_high_speed` |
| `3` | `POWER_GROUND` | return | `return` |
| `4` | `S3_RP_IPC_CS_N` | UI→RF | `ipc_high_speed` |
| `5` | `S3_RP_IPC_SCK` | UI→RF | `ipc_high_speed` |
| `6` | `POWER_GROUND` | return | `return` |
| `7` | `S3_RP_IPC_MOSI` | UI→RF | `ipc_high_speed` |
| `8` | `S3_RP_IPC_MISO` | RF→UI | `ipc_high_speed` |
| `9` | `POWER_GROUND` | return | `return` |
| `10` | `S3_USB_DM` | bidirectional | `usb2_high_speed` |
| `11` | `S3_USB_DP` | bidirectional | `usb2_high_speed` |
| `12` | `POWER_GROUND` | return | `return` |
| `13` | `SYS_I2C_SDA` | bidirectional | `control` |
| `14` | `SYS_I2C_SCL` | bidirectional | `control` |
| `15` | `POWER_GROUND` | return | `return` |
| `16` | `SYS_INT_N` | RF→UI | `control` |
| `17` | `CC_BAND_V1_REQ` | UI→RF | `control` |
| `18` | `CC_BAND_V2_REQ` | UI→RF | `control` |
| `19` | `POWER_GROUND` | return | `return` |
| `20` | `U214_I2C_READY` | RF→UI | `control` |
| `21` | `VOICE_DOMAIN_REQ` | UI→RF | `control` |
| `22` | `VOICE_HL_RELEASE_REQ` | UI→RF | `control` |
| `23` | `POWER_GROUND` | return | `return` |
| `24` | `U214_5V_REQ` | UI→RF | `control` |
| `25` | `UNIT_5V_REQ` | UI→RF | `control` |
| `26` | `POWER_FAULT_N` | RF→UI | `control` |
| `27` | `POWER_GROUND` | return | `return` |
| `28` | `UNIT_READY` | RF→UI | `control` |
| `29` | `EV_N2_NRF0` | RF→UI | `tx_evidence` |
| `30` | `EV_N3_NRF1` | RF→UI | `tx_evidence` |
| `31` | `POWER_GROUND` | return | `return` |
| `32` | `RUN_PERMIT` | RF→UI | `safety` |
| `33` | `EV_N4_NRF2` | RF→UI | `tx_evidence` |
| `34` | `RF_RESET_KILL_GATE` | RF→UI | `safety` |
| `35` | `POWER_GROUND` | return | `return` |
| `36` | `EV_N0_S3` | UI→RF | `tx_evidence` |
| `37` | `EV_N1_C5` | UI→RF | `tx_evidence` |
| `38` | `EV_N7_IR` | UI→RF | `tx_evidence` |
| `39` | `POWER_GROUND` | return | `return` |
| `40` | `C5_RF_TX_EVIDENCE_N` | RF→UI | `tx_evidence` |
| `41` | `IR_TX_EVIDENCE_N` | RF→UI | `tx_evidence` |
| `42` | `RX_SA518_AFOUT_ISOLATED` | RF→UI | `audio` |
| `43` | `AUDIO_GROUND` | return | `return` |
| `44` | `VOICE_MIC_SELECTED_MAIN` | UI→RF | `audio` |
| `45` | `AUDIO_GROUND` | return | `return` |
| `46` | `SPEAKER_SELECTED_P` | UI→RF | `audio` |
| `47` | `SPEAKER_SELECTED_N` | UI→RF | `audio` |
| `48` | `MIC_RAW` | RF→UI | `audio` |
| `49` | `AUDIO_GROUND` | return | `return` |
| `50` | `UI_ENCODER_PUSH_N` | RF→UI | `control` |
| `51` | `3V3_MAIN` | rail | `power` |
| `52` | `3V3_MAIN` | rail | `power` |
| `53` | `3V3_MAIN` | rail | `power` |
| `54` | `3V3_MAIN` | rail | `power` |
| `55` | `3V3_MAIN` | rail | `power` |
| `56` | `3V3_MAIN` | rail | `power` |
| `57` | `3V3_MAIN` | rail | `power` |
| `58` | `EV_N5_CC` | RF→UI | `tx_evidence` |
| `59` | `POWER_GROUND` | return | `return` |
| `60` | `POWER_GROUND` | return | `return` |
| `61` | `POWER_GROUND` | return | `return` |
| `62` | `POWER_GROUND` | return | `return` |
| `63` | `POWER_GROUND` | return | `return` |
| `64` | `POWER_GROUND` | return | `return` |
| `65` | `AON_SAFE_3V3` | rail | `power` |
| `66` | `AON_SAFE_3V3` | rail | `power` |
| `67` | `SAFETY_GROUND` | return | `return` |
| `68` | `SAFETY_GROUND` | return | `return` |
| `69` | `UNIT_HOST_SIG0` | bidirectional | `unit_configurable` |
| `70` | `POWER_GROUND` | return | `return` |
| `71` | `UNIT_HOST_SIG1` | bidirectional | `unit_configurable` |
| `72` | `POWER_GROUND` | return | `return` |
| `73` | `ENCODER_A` | RF→UI | `control` |
| `74` | `ENCODER_B` | RF→UI | `control` |
| `75` | `S3_RESET_KILL_GATE` | RF→UI | `safety` |
| `76` | `UI_ZONE_TEMP_ADC` | UI→RF | `analog` |
| `77` | `FAULT_LATCH_SENSE_AON` | RF→UI | `safety` |
| `78` | `SPEAKER_AMP_EN` | UI→RF | `control` |
| `79` | `EV_N6_VOICE` | RF→UI | `tx_evidence` |
| `80` | `EV_N8_LORA_EXT` | RF→UI | `tx_evidence` |

Seven paralleled `3V3_MAIN` contacts provide a 2.8-A nameplate ceiling, but finished-device current is accepted only after connector-temperature measurement under simultaneous load. All 80 contacts are assigned; six digital RF-evidence lines are dedicated to the front transmit indicators.
