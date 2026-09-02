# Power-rail margins · H3-R2.1.3

[Русский](power-rail-margins.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Load binding](power-load-binding.md)

`H3-R2.1.3` is reviewed. All 629 physical and external load lines have exactly one current owner or an explicit source/pack deferral to H3-R2.1.4. There is no hidden miscellaneous line.

## Current and protection

| Rail | Electrical worst load | Hardware minimum | Reserve | Profile |
|---|---:|---:|---:|---|
| `AON_SAFE_3V3` | 72.100 mA | 0.165 A | 128.849% | `NRF24/3PRX/SUPPORT_IDLE` |
| `3V3_MAIN` | 3046.000 mA | 4.000 A | 31.320% | `NRF24/3PTX/SUPPORT_WORST` |
| `VVOICE_4V` | 750.000 mA | 1.550 A | 106.667% | `VOICE/PTT_TX_MAX/SUPPORT_IDLE` |
| `5V_EXT_ACTIVE_BRANCH` | 1250.000 mA | 1.632 A | 30.560% | `LORA_CAP/U214_STOCK_RX_GNSS/SUPPORT_IDLE` |

The limiting 3V3_MAIN element is the current 4-A `TPS564252DRLR`, not the historical 6-A converter. The worst corner retains 154 mA before the 25% rule boundary.

## Voltage

| Rail | Raw corner | Load endpoint | Allowed load range | Result |
|---|---:|---:|---:|---|
| `AON_SAFE_3V3` | 3.224000…3.376000 V | 3.199000…3.376000 V | 2.700000…3.600000 V | pass |
| `3V3_MAIN` | 3.158510…3.285658 V | 3.108510…3.285658 V | 3.000000…3.300000 V | pass |
| `VVOICE_4V` | 3.853683…4.149717 V | 3.793683…4.149717 V | 3.300000…5.500000 V | pass |
| `5V_EXT_ACTIVE_BRANCH` | 4.814178…5.190222 V | 4.694178…5.190222 V | 4.500000…5.500000 V | pass |

## Steady thermal envelope

| Rail | Sustained current | Converter Tj | Margin to Tj max | eFuse Tj | Result |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 72.100 mA | 37.519 °C | 87.481 °C | 35.092 °C | pass |
| `3V3_MAIN` | 988.000 mA | 76.571 °C | 48.429 °C | 38.504 °C | pass |
| `VVOICE_4V` | 750.000 mA | 74.176 °C | 50.824 °C | 37.019 °C | pass |
| `5V_EXT_ACTIVE_BRANCH` | 1000.000 mA | 100.294 °C | 24.706 °C | 39.470 °C | pass |

`SUPPORT_WORST` remains an electrical simultaneous corner, not a 24-to-48-hour permission. The exposed 5-V port keeps its 1.25-A electrical ceiling, while unattended control admits 1.00 A until H6/H8; the selected U214/U219/M5 functions are unaffected.

**Downstream result:** [`H3-R2.1`](power-dc-source-result.md) is fully reviewed; the [roadmap](roadmap.md) carries the live marker.

[Complete machine result](../hardware/verification/generated/H3-R2-rail-margins.json).
