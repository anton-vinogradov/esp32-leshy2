# Leshy2 quiet state

[Русский](quiet-state.ru.md) · [Home](../README.md) · [Interface isolation](interface-isolation.md)

No signal group is active by default. Every unused radio and interface enters a reviewable hardware-safe state.

| Group | Inactive state |
|---|---|
| `N24_QUIET` | rail off; signals high-Z |
| `CC_QUIET` | rail off; signals high-Z |
| `U214_CAP_QUIET` | reverse-blocked 5 V off; 11 signals isolated |
| `UNIT_PORT_QUIET` | reverse-blocked 5 V off; 2 signals isolated |
| `VOICE_QUIET` | rail off; hardware PTT off |
| `RECEIVER_QUIET` | rail off; reset and control isolation |
| `CODEC_AUDIO_QUIET` | rail off; I²C/I²S/audio isolated |
| `VOICE_INTERFACE_QUIET` | I/O rail off; digital/analog isolation |
| `IR_QUIET` | RX rail off; fault-dominant TX gate |
| `S3_RF_QUIET` | native RF off; CPU remains alive |
| `C5_RF_QUIET` | native RF off; CPU remains alive |
| `STORAGE_QUIET` | flush, then rail off and static bus |
| `SERVICE_IPC_QUIET` | bounded transaction only; then clock/DMA stop |

`SG-N24` is the sole exception: all three nRF24 paths may run a full RX/TX mix inside one active group.

## H2.5.4 result

✅ **Reviewed:** all 13 quiet-state contracts map to actual KiCad nets and exact serial components.

[Machine evidence](../hardware/ecad/generated/H2-REV54-quiet-state.json).
