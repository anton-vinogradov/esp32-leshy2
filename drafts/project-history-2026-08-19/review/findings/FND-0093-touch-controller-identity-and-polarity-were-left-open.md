# FND-0093 — touch controller identity and interrupt polarity were left open

- Status: **исправлено; Проведено ревью paper electrical boundary**
- Scope: exact `HMX035CTFT-001` display/touch assembly
- Architecture: [`DSP-0007`](../architecture/DSP-0007-exact-integrated-st77922-touch-endpoint.md)

## Finding

The current display documents treated the capacitive-touch controller as a
possibly separate unknown IC and left `TP_INT` polarity to specimen HIL. That
was inconsistent with the primary sources already selected for the exact
assembly:

- the Sitronix primary datasheet identifies `ST77922` as a single-chip TFT
  controller/driver/touch TDDI and publishes its touch I2C, reset and interrupt
  die pads;
- the exact Elecrow/QDtech `ES3C35P` specification publishes touch address
  `0x38` and states that `TP_INT` is low during a touch event;
- the QDtech schematic publishes the exact `HMX035CTFT-001` 40-contact
  assembly boundary.

The machine contract also retained stale text saying that TP_INT reached S3
GPIO39 directly, although `DEC-0086` had already reassigned GPIO39 to encoder
phase A and moved touch to shared GPIO37. Keeping both descriptions would make
the later schematic ambiguous.

## Correction

- Exact integrated controller `Sitronix ST77922` is now a named device inside
  `HMX035CTFT-001`; no fictional FT6x36-class companion IC is introduced.
- Touch uses SYS_I2C at exact 7-bit address `0x38`, with controller limit
  400 kHz.
- Exact die pads are projected through the assembly contacts: SCL 28, SDA 29,
  TP_INT 31 and TP_RESXP 49. Display QSPI/reset/strap/TE pads are recorded in
  the same device registry.
- Active-low TP_INT now has an exact `RC0402FR-0710KL` 10-kOhm raw pull-up and
  fixed non-inverting open-drain `SN74LVC1G07DCKR` before shared S3 GPIO37.
  The pin-compatible inverting `SN74LVC1G06DCKR` population option is removed.
- The stale direct-GPIO39 wording is corrected in the machine display
  contract.

The raw pull-up makes the board input deterministic whether the assembled COG
output stage is push-pull or open-drain. It adds no GPIO and no user-visible
function; the resistor is a negligible BOM correction under the delegated
no-material-cost-inflation rule.

## Remaining evidence, not paper uncertainty

Specimen HIL must still read an expected controller identity/status response,
confirm `0x38`, measure raw idle voltage, prove assertion/persistence/clear
semantics, exercise reset/recovery and identify the source correctly while
`SYS_INT_N` is shared. Real-tail fit, standalone assembly sourcing, QSPI
signal integrity, backlight thermals and enclosure ESD remain separate open
gates. None authorizes KiCad.

## Primary sources

- [Sitronix ST77922 primary datasheet](https://dl.espressif.com/AE/esp-iot-solution/ST77922_SPEC_V0.1.pdf)
- [Elecrow/QDtech ES3C35P exact specification](https://www.elecrow.com/download/product/DLE06235B/3.5inch_IPS_ESP32-S3_Specification.pdf)
- [QDtech ES3C35P schematic with HMX035CTFT-001](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
- [Sitronix current TDDI catalog](https://www.sitronix.com.tw/en/products-service/aiot-device-ddi/)
