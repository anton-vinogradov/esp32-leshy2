# FND-0080 — TPS autonomous startup and complete-bus pulls were incomplete

- Статус: **Исправлено**
- Дата: 2026-08-18
- Correction: [`PWR-0015`](../architecture/PWR-0015-exact-tps25751-eeprom-support-profile.md)
- Decision: [`DEC-0076`](../decisions/DEC-0076-exact-tps25751-eeprom-support-profile.md)
- Review: [`REV-0005AG`](../reviews/REV-0005AG-tps25751-eeprom-support-profile.md)

## Finding

The previous block map connected raw connector power only to `VBUS_IN`.
TPS25751 uses separate `VBUS` pins to power dead-battery attach detection, safe
discharge and its startup LDO. With only `VBUS_IN` represented, autonomous
USB-only boot was asserted but not electrically established.

The previous BQ pass also instantiated 10-kOhm SCL/SDA pull-ups as if they were
charger-only pins. The real local bus contains TPS25751, CAT24C512 and BQ25798;
the host bus contains multiple targets and a shared wired-low IRQ. The complete
bus pull networks had not been calculated or physically instantiated.

The former EEPROM service description also offered an external 3.3-V fixture
source on a net now proven to be TPS `LDO_3V3`. That could back-drive an LDO
output. TI's FLxx update flow also assumes initialized region headers and is not
a blank-device programming method.

## Correction

- raw VBUS now reaches both `VBUS` and `VBUS_IN`;
- SafeMode straps, LDO/VBUS/PPHV/CC capacitors and every unused TPS termination
  are explicit;
- local SCL/SDA pulls are replaced by exact 2.2-kOhm parts;
- host SCL/SDA 2.2-kOhm and IRQ 10-kOhm pulls are physical instances;
- EEPROM VCC/VSS/bypass/WP and open-drain protection are explicit;
- blank first image uses pre-placement programming or raw-VBUS-powered direct
  ISP only after `ReadyForPatch`/I2Cc-high-Z proof; external LDO_3V3 injection
  is forbidden;
- all affected architecture, landing-page diagrams and firmware contracts are
  regenerated or reviewed by `REV-0005AG`.

No pin budget, source-role or accepted PD power profile changes. Measured bus
capacitance/rise time and raw-VBUS boot/fault behavior remain HIL gates.
