# Тихое состояние Leshy2

[English](quiet-state.md) · [На главную](../README.ru.md) · [Изоляция интерфейсов](interface-isolation.ru.md)

По умолчанию активной группы нет. Неиспользуемые радио и интерфейсы переводятся в проверяемое аппаратно безопасное состояние.

| Группа | Неактивное состояние |
|---|---|
| `N24_QUIET` | питание снято; сигналы high-Z |
| `CC_QUIET` | питание снято; сигналы high-Z |
| `U214_CAP_QUIET` | reverse-blocked 5 В off; 11 сигналов изолированы |
| `UNIT_PORT_QUIET` | reverse-blocked 5 В off; 2 сигнала изолированы |
| `VOICE_QUIET` | питание снято; PTT аппаратно off |
| `RECEIVER_QUIET` | питание снято; reset и control isolation |
| `CODEC_AUDIO_QUIET` | питание снято; I²C/I²S/audio изолированы |
| `VOICE_INTERFACE_QUIET` | I/O rail off; digital/analog изоляция |
| `IR_QUIET` | RX rail off; TX gate fault-dominant |
| `S3_RF_QUIET` | native RF off; CPU остаётся включён |
| `C5_RF_QUIET` | native RF off; CPU остаётся включён |
| `STORAGE_QUIET` | flush, затем rail off и static bus |
| `SERVICE_IPC_QUIET` | только bounded transaction; затем clock/DMA stop |

`SG-N24` — единственное исключение: три nRF24 могут одновременно работать в полном RX/TX mix внутри одной активной группы.

## Результат H2.5.4

✅ **Проведено ревью:** все 13 quiet-state контрактов сопоставлены с реальными цепями KiCad и точными серийными компонентами.

[Машинное evidence](../hardware/ecad/generated/H2-REV54-quiet-state.json).
