# REV-0005AG — TPS25751D/EEPROM support-profile propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0076`](../decisions/DEC-0076-exact-tps25751-eeprom-support-profile.md)
- Analysis: [`PWR-0015`](../architecture/PWR-0015-exact-tps25751-eeprom-support-profile.md)
- Corrected finding: [`FND-0080`](../findings/FND-0080-tps25751-autonomous-start-and-bus-pulls.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| Exact contacts | separate VBUS/VBUS_IN, PPHV, PP5V, DRAIN/GND pads and every unused GPIO represented |
| Autonomous boot | ADCIN1=7/ADCIN2=0 SafeMode, address 0x20, raw-VBUS LDO and EEPROM address 0x50 represented |
| Failure default | missing/corrupt image leaves PD, PPHV and charge disabled |
| Energy | VIN/LDO, 88-uF nominal PPHV, VBUS, per-CC and EEPROM capacitors are separate physical instances |
| EEPROM | LDO power, bypass, low address straps, factory pads and reset-high/open-drain WP represented |
| Blank first image | pre-placement programming or current-limited raw-VBUS ISP after ReadyForPatch/I2Cc-high-Z proof; no LDO-output injection |
| Local bus | old charger-only 10-kOhm SCL/SDA pair replaced by complete-bus 2.2-kOhm pair; INT remains 10 kOhm |
| Host bus | exact 2.2-kOhm SCL/SDA and 10-kOhm wired-low IRQ pulls added to 3V3_MAIN |
| AON | TPS maximum active current was included in the 15-mA continuous / 20-mA transient contract; later `DEC-0091` raises transient reserve to 30 mA for nRF evidence without a converter change |
| Cost | three new active/orderable MPN lines; approximately $1.15…1.45 total support material, mostly reused bulk |
| Product diagrams | 17 support parts appear as 17 distinct MPN-and-role boxes in both target landing pages |
| Firmware | SafeMode, autonomous boot, WP open-drain and PPHV/IINDPM/CE ordering are contractual inputs |

## Remaining gates

Exact connector and connector-side protection, total CC capacitance, effective
PPHV capacitance at 15 V, layout/thermal copper, bus rise time, blank/corrupt
image, raw-VBUS-only boot, attach/remove, signed rollback and fault injection
remain I4/HIL. The paper circuit receives **«Проведено ревью»** and does not
authorize KiCad.
