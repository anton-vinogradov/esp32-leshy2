# DEC-0076 — exact TPS25751D and CAT24C512 support profile

- Статус: **Принято; проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Analysis: [`PWR-0015`](../architecture/PWR-0015-exact-tps25751-eeprom-support-profile.md)
- Corrected finding: [`FND-0080`](../findings/FND-0080-tps25751-autonomous-start-and-bus-pulls.md)
- Propagation review: [`REV-0005AG`](../reviews/REV-0005AG-tps25751-eeprom-support-profile.md)

## Decision

1. Raw USB VBUS feeds both TPS25751 `VBUS` and `VBUS_IN`; the former provides
   dead-battery startup/attach and the latter is the protected PPHV input.
2. `ADCIN1=7`, `ADCIN2=0` selects hardware SafeMode and target address `0x20`.
   No application MCU is required before the EEPROM image is loaded.
3. `PP5V` is grounded for the accepted sink-only/no-VCONN product.
4. `VIN_3V3` uses `AON_SAFE_3V3`; the AON budget becomes at least 15 mA
   continuous and 20 mA transient without changing TPS629203. `DEC-0091`
   later raises the transient reserve to 30 mA for three active nRF evidence
   detectors, still without a converter change.
5. Accept the exact 17-component profile and all contact terminations in
   `PWR-0015`.
6. Replace the previous charger-only 10-kOhm SCL/SDA pulls with complete-bus
   2.2-kOhm pulls. Add the previously implicit S3 host-bus SCL/SDA and IRQ
   physical pulls.
7. GPIO0 is open-drain and may only sink EEPROM WP in a signed authorized write
   window. GPIO1 remains the separate open-drain charger-enable sink.
8. A blank EEPROM is either programmed before placement or through direct
   SDA/SCL/WP pads only after a current-limited raw-VBUS fixture observes
   `ReadyForPatch` and verifies I2Cc high-Z. The fixture must not inject power
   into `LDO_3V3`; the normal FLxx flow updates only an initialized image.

## Consequence

The unit can attach and load a safe PD configuration from raw USB power without
S3, a battery-derived AON rail or an enabled charger. Missing configuration
fails with the high-voltage path and charging off. The correction consumes no
GPIO and does not add a source/power-bank feature. This is a reviewed working
design, not the final atomic architecture and not KiCad authorization.
