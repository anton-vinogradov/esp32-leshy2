# Steady DC power budget

[Русский](dc-power-budget.ru.md) · [Home](../README.md) · [States](power-state-register.md) · [Methods](verification-methods.md)

H3.1.2 attaches a numeric current to all 50 load profiles. Both ESP devices reserve their published RF peak in the worst case, all three nRF24 radios are genuinely concurrent, and typical values never prove a pass.

| Rail | Worst load | Hardware minimum | Hardware reserve | Accepted-envelope margin | Worst profile |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 89.500 mA | 0.165 A | 84.358% | 75.500 mA | `NRF24/3PRX/SUPPORT_IDLE` |
| `3V3_MAIN` | 2462.000 mA | 3.200 A | 29.976% | 38.000 mA | `IR/LEARN_OR_RAW_RX/SUPPORT_WORST` |
| `VVOICE_4V` | 900.000 mA | 1.550 A | 72.222% | 350.000 mA | `VOICE/RX/SUPPORT_IDLE` |
| `5V_EXT_ACTIVE_BRANCH` | 1250.000 mA | 1.632 A | 30.560% | 0.000 mA | `LORA_CAP/STOCK_U214_RX_GNSS_ONLY/SUPPORT_IDLE` |

## Calculation-driven correction

Both exposed-port eFuses now use the active `Yageo RC0402FR-071K82L` 1.82-kohm resistor instead of 2.21 kohm. The guaranteed-low threshold rises from 1.358 to 1.632 A: steady reserve above the 1.25-A port is 30.6%, while the bounded 2-A pulse remains available. The checked quantity-100 price is unchanged.

## What this proves

All four DC rails pass the 25% rule against the minimum hardware threshold. `3V3_MAIN` has the tightest accepted operating envelope: the conservative 2.462-A load leaves 38 mA to the accepted 2.5-A requirement but 30.0% to the guaranteed 3.2-A protection threshold. H3.2 must therefore prove the load step and H8 must measure the real sum.

**Status:** `H3.1.2` is complete and reviewed; the exact current marker is `H3.3.1`.

[Complete machine calculation](../hardware/verification/generated/H3-VRF12-dc-budget.json).
