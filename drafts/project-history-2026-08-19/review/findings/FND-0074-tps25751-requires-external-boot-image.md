# FND-0074 — TPS25751 requires an external boot image

- Статус: **Исправлено в DEC-0063/PWR-0004; recovery HIL открыт**
- Дата: 2026-08-18
- Source: [TPS25751 datasheet](https://www.ti.com/lit/ds/symlink/tps25751.pdf)

## Finding

`TPS25751DREFR` is not a self-contained retained-configuration replacement for
a passive Type-C sink. On every boot it attempts to load its patch and
application configuration from one dedicated I2C EEPROM at address `0x50`;
the datasheet requires at least 36 kB. Without that image it waits for an
external host and cannot be treated as the accepted autonomous PD/charger
policy.

The earlier option-level comparison named the controller and charger but did
not account for the mandatory EEPROM, first-image provisioning, corruption
recovery or update/rollback path. That omission also understated BOM and
service scope.

## Correction

- instantiate exact 64-kB `CAT24C512WI-GT3`, matching TI's current integrated
  PD/charger reference;
- expose local SDA/SCL/WP plus power/ground for blank-device factory programming
  and independent recovery;
- use reset-high WP and a dual-region update policy;
- require S3 to verify an owner-signed bundle before an update write window;
- keep charge disabled and prohibit negotiation above safe fallback when the
  image is invalid or absent;
- version and reproduce the generated binary/config source as a product build
  artifact rather than an opaque factory-only blob.

This does not close the device: owner firmware and owner-controlled signing
remain allowed. It makes a security-relevant configuration artifact explicit,
recoverable and reviewable.
