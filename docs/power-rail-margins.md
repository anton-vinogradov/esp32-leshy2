# Power-rail margins · H3-R2.1.3

[Русский](power-rail-margins.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Load binding](power-load-binding.md)

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `current:3V3_MAIN`; `voltage:3V3_MAIN`; `thermal:3V3_MAIN`; `voltage-target:3V3_MAIN:H0_continuous`; `voltage-target:3V3_MAIN:H0_step_resistive_snapshot_not_transient_proof`; `numerical:existing_checks`; `applicability:main_raw_model`; `applicability:main_protection_model`; `applicability:main_thermal_model`; `applicability:aon_ron_model`; `applicability:series_distribution_scope`.

[Machine evidence](../hardware/verification/generated/H3-R2-rail-margins.json).

## Current and protection

| Rail | Electrical worst load | Provisional model minimum | Reserve | Profile |
|---|---:|---:|---:|---|
| `AON_SAFE_3V3` | 72.100 mA | 0.165 A | 128.849% | `NRF24/3PRX/SUPPORT_IDLE` |
| `3V3_MAIN` | 3046.000 mA | 3.072960761 A | 0.885% | `NRF24/3PTX/SUPPORT_WORST` |
| `VVOICE_4V` | 750.000 mA | 1.550 A | 106.667% | `VOICE/PTT_TX_MAX/SUPPORT_IDLE` |
| `5V_EXT_ACTIVE_BRANCH` | 1250.000 mA | 1.632 A | 30.560% | `LORA_CAP/U214_STOCK_RX_GNSS/SUPPORT_IDLE` |

Fitted MAIN converter: TPS566231PRQFR. Its 6 A rated output is separate from the 6.1/7.4/8.9 A valley threshold. Protection uses actual R67 1650 ohm, with separate initial-only and initial+TCR intervals; old 4.3399 A is not used. This is conditioned arithmetic, not load, startup or PCB admission.

## Voltage

| Rail | Raw corner | Protected local before distribution | Load endpoint | Allowed load range | Result |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 3.224000…3.376000 V | 3.206696…3.376000 V | 3.181696…3.376000 V | 2.700000…3.600000 V | numerical pass; review_required |
| `3V3_MAIN` | 3.145013…3.299695 V | 2.992713…3.299695 V | 2.942713…3.299695 V | 3.000000…3.300000 V | numerical fail; review_required |
| `VVOICE_4V` | 3.853683…4.149717 V | 3.816183…4.149717 V | 3.756183…4.149717 V | 3.300000…5.500000 V | numerical pass; review_required |
| `5V_EXT_ACTIVE_BRANCH` | 4.814178…5.190222 V | 4.739178…5.190222 V | 4.619178…5.190222 V | 4.500000…5.500000 V | numerical pass; review_required |

MAIN VFB 0.591..0.609 V belongs to the VIN12 V, TJ −40..125 °C table; actual NVDC6.0..8.4 V applicability remains unqualified. The divider uses exact 43.7k/10k, 0.1%, 25 ppm/K relative to **20 °C**. Ripple20 mVpp, RON50 mΩ and distribution50 mV are separate engineering allowances, not manufacturer guarantees. Solder/endurance, PG, transients and hot RON remain open.

## Steady thermal envelope

| Rail | Sustained current | Converter Tj | Margin to Tj max | eFuse Tj | Result |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 72.100 mA | 37.519 °C | 87.481 °C | 35.092 °C | pass |
| `3V3_MAIN` | 988.000 mA | not established | not established | not established | review_required |
| `VVOICE_4V` | 750.000 mA | 74.176 °C | 50.824 °C | 37.019 °C | pass |
| `5V_EXT_ACTIVE_BRANCH` | 1000.000 mA | 100.294 °C | 24.706 °C | 39.470 °C | pass |

### MAIN allowable loss, not predicted junction temperature

| Ambient | Reference board | θJA | Chip loss for Tj≤105 °C |
|---|---|---:|---:|
| 35 °C | JEDEC_reference_board | 89.6 K/W | 0.781250 W |
| 35 °C | TI_EVM | 44 K/W | 1.590909 W |
| 45 °C | JEDEC_reference_board | 89.6 K/W | 0.669643 W |
| 45 °C | TI_EVM | 44 K/W | 1.363636 W |

These four independent conditions do not describe our PCB thermal resistance. Neither 85% efficiency nor old 74 K/W is used for MAIN; overall junction margin is not established.

`SUPPORT_WORST` remains an electrical simultaneous corner, not a 24-to-48-hour permission. The exposed 5-V port keeps its 1.25-A electrical ceiling, while unattended control admits 1.00 A until H6/H8; the selected U214/U219/M5 functions are unaffected.

Current numerical results are provisional; analytical applicability findings remain open.
