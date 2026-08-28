# Модель RF coexistence · historical R1

`H3.5.3` проведён ревью: `30` машинных checks, незакрытых аналитических findings нет. Исторический маркер прогресса R1 — `H3.6.1`.

| Активная группа | Активные участники | Quiet contracts чужих RF/IR |
|---|---|---:|
| SG-N24 | nrf0, nrf1, nrf2 | 9 |
| SG-S3-24 | s3 Wi-Fi, s3 BLE, ESP-NOW | 9 |
| SG-C5-NATIVE | c5 Wi-Fi 2.4/5, c5 IEEE 802.15.4 | 9 |
| SG-CC | cc | 9 |
| SG-VOICE | voice UHF, voice_v VHF | 8 |
| SG-BROADCAST | receiver, audio support | 9 |
| SG-U214 | stock U214 receive and GNSS, evidence-aware LoRa Cap RX/TX | 9 |
| SG-IR | c5 IR | 9 |
| SG-EXT-* | one exact accessory profile | 9 |

Runtime допускает максимум одну верхнеуровневую группу сигналов. Display/UI, safety, telemetry и явно объявленные профилем audio/storage/service — supporting planes, а не вторая радиогруппа; их clocks и rails ограничены или затихают. Cross-group injection существует только внутри изолированного тестового слоя «Лаборатория».

`SG-N24` — намеренное внутреннее исключение. Все три радио остаются активны и имеют независимые SPI/PIO/DMA, digital isolation и антенные corridors. Матрица покрывает четыре role mixes, восемь перестановок ролей по радиомодулям и оба support loads. Бумажное ревью **не** заявляет same/near-channel isolation: production acceptance всё ещё требует T1 target плюс независимый observer, правило деградации peer RX не более 3 дБ и отсутствие скрытого standby/RX gap.

Машинное evidence: [`H3-VRF53-rf-coexistence.json`](../hardware/verification/generated/H3-VRF53-rf-coexistence.json).
