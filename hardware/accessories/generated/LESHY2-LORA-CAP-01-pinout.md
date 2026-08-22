# LESHY2-LORA-CAP-01 exact Cap-Bus contract

Generated from `hardware/accessories/leshy2-lora-cap-01.json`.
Pins are numbered in the host-mating orientation of the exact 2×7 connector.

| Pin | Stock M5Stack U214 | LESHY2-LORA-CAP-01 | Direction at host |
|---:|---|---|---|
| 1 | `GPS_TX` | `NC` | input/reserved |
| 2 | `GPS_RX` | `NC` | output/reserved |
| 3 | `SCL` | `IDENTITY_SCL` | output |
| 4 | `SDA` | `IDENTITY_SDA` | bidirectional |
| 5 | `5V_OUT` | `EXT_TX_EVIDENCE_N` | input |
| 6 | `GND` | `GND` | power return |
| 7 | `5V_IN` | `5V_IN` | power output |
| 8 | `LORA_RST` | `LORA_NRESET` | output |
| 9 | `LORA_IRQ` | `LORA_DIO1` | input |
| 10 | `LORA_BUSY` | `LORA_BUSY` | input |
| 11 | `SCK` | `LORA_SCK` | output |
| 12 | `MOSI` | `LORA_MOSI` | output |
| 13 | `MISO` | `LORA_MISO` | input |
| 14 | `NSS` | `LORA_NSS` | output |

Pin 5 is deliberately dual-profile. The stock U214 drives its documented `5V_OUT` high and therefore provides no TX evidence. The custom Cap only releases or sinks the line through an open-drain final-feed detector; it never sources the host boundary.
