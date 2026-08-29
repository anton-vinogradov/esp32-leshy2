# Steady DC power budget · current R2 architecture

[Русский](dc-power-budget.ru.md) · [Home](../README.md) · [States](power-state-register.md) · [Methods](verification-methods.md)

The H3.1.2 calculation attaches a numeric current to all 50 load profiles. Both ESP devices, both RP2354B domains and all three full-power nRF24 radios are concurrent in the worst case; typical values never prove a pass.

| Rail | Worst load | Hardware minimum | Hardware reserve | Accepted-envelope margin | Worst profile |
|---|---:|---:|---:|---:|---|
| `AON_SAFE_3V3` | 89.500 mA | 0.165 A | 84.358% | 75.500 mA | `NRF24/3PRX/SUPPORT_IDLE` |
| `3V3_MAIN` | 3063.000 mA | 4.340 A | 41.688% | 687.000 mA | `NRF24/3PRX/SUPPORT_WORST` |
| `VVOICE_4V` | 750.000 mA | 1.550 A | 106.667% | 500.000 mA | `VOICE/RX/SUPPORT_IDLE` |
| `5V_EXT_ACTIVE_BRANCH` | 1250.000 mA | 1.632 A | 30.560% | 0.000 mA | `LORA_CAP/STOCK_U214_RX_GNSS_ONLY/SUPPORT_IDLE` |

## Calculation-driven correction

Both exposed-port eFuses now use the active `Yageo RC0402FR-071K82L` 1.82-kohm resistor instead of 2.21 kohm. The guaranteed-low threshold rises from 1.358 to 1.632 A: steady reserve above the 1.25-A port is 30.6%, while the bounded 2-A pulse remains available. The checked quantity-100 price is unchanged.

## What this proves

All four DC rails pass the 25% rule against the minimum hardware threshold. The worst `3V3_MAIN` profile draws 3.063 A, leaving 687 mA to the accepted 3.75-A continuous envelope and 41.69% to the guaranteed 4.3399-A protection threshold. H3.2 must still prove the load step and H8 must measure the real sum.

**Status:** the H3.1.2 numeric model is refreshed and passes for `H1-R2.35`; the complete H3 phase is not closed.

[Complete machine calculation](../hardware/verification/generated/H3-VRF12-dc-budget.json).
