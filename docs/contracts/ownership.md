# Контракт владения аппаратными блоками

Статус документа: **Проведено ревью** (`DEC-0028`, `REV-0003U`).

Вычислительные домены target: `ESP32-S3-WROOM-1U-N16R2`, `ESP32-C5-WROOM-1U-N8R8` revision ≥1.0 и `RP2354A A4` QFN60 со stacked flash 2 MiB.

| Блок | Владелец | Состояние решения |
|---|---|---|
| Product application, UI, display/touch/slow controls | ESP32-S3 | принят `PKG-0001`; STOP/PTT/RE-ARM не делегируются I²C UI controller |
| microSD/files, product USB/Web | ESP32-S3 | единственный normal filesystem writer; snapshot/exclusive MSC |
| ES8311/Si4732 audio samples и routing | ESP32-S3 | mono full-duplex digital path + hardware-default analog bypass |
| 3× nRF24L01+ | RP2354A | три полнофункциональных тракта, прямые CSN/CE/IRQ и общий SPI0; принято `DEC-0028` |
| CC1101 | RP2354A | прямые CS/GDO0/GDO2, общий SPI0 packet-radio domain |
| Analog voice control/PTT/dead-man/evidence | RP2354A | UART/control и local deadline/safe-off; audio samples остаются у S3 |
| IR TX | ESP32-C5 | dual-path IR service и local lease; принято `DEC-0028` |
| IR RX | ESP32-C5 | TSOP38238 + TSMP95000, оба C5 RX RMT channels |
| Native BLE | ESP32-S3 | принято `DEC-0021`; C5 BLE default-off |
| C5 Wi-Fi/IEEE 802.15.4 | ESP32-C5 | принято на уровне controller ownership `REQ-W5-0001` |
| S3 Wi-Fi 2.4/ESP-NOW | ESP32-S3 | принято на уровне controller ownership `REQ-W24-0001` |
| U214, selected Unit GPS/GNSS и U216 profile manager | ESP32-S3 | одновременно активен один GNSS и один LoRa backend; external profile проходит isolation/power gate |
| Physical PTT | RP2354A direct GPIO | действует только в armed foreground voice session |
| Latched STOP/TX_KILL/critical indication | `AON_SAFE` hardware | firmware не является единственным барьером; RP наблюдает STOP напрямую, S3/C5 входят в reset/enable safe policy |

## Междоменные границы

- S3↔C5: 1-bit SDIO, typed control/event/bulk/liveness/recovery channels.
- S3↔RP: initial 20 MHz SPI + `RP_ALERT_N`, те же semantic channel classes.
- C5 и RP локально выдерживают peripheral deadlines и снимают TX lease при stale/malformed/lost IPC.
- IPC передаёт намерение и bounded параметры, но не используется как remote raw GPIO.
- Точный controller/pin/strap/recovery map задаёт `PIN-0002/SYN-3A`; memory/traffic/power/RF/update contracts задаёт `PKG-0001` целиком.

Назначения выведены zero-based цепочкой `CAP→CON→RES→SRC→SYN→PIN→BUD→PWR→RFQ→CST→PKG` и не наследуют legacy layout. Изменение одной строки, затрагивающее другие package contracts, требует повторного атомарного ревью по `DEC-0026/0028`.
