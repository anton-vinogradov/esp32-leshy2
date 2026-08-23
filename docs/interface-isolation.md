# Leshy2 external-interface isolation

[Русский](interface-isolation.ru.md) · [Home](../README.md) · [Power](power-architecture.md)

A cable or accessory cannot silently power an off product or an adjacent port.

| Boundary | Allowed path | Hardware prohibition |
|---|---|---|
| S3 USB-C | USB 2.0 plus sink-only PD up to 30 W | source/OTG and PD bypass |
| C5 USB-C | D+/D− only through FSUSB42MUX | board power through VBUS or data pins |
| RP2354B USB-C | D+/D− only through FSUSB42MUX | board power through VBUS or data pins |
| Interboard M1 | 3V3_MAIN, AON_SAFE_3V3 and signals | raw USB, cells, NVDC and exposed 5 V |
| U214 Cap / M5 Unit | two independently admitted protected branches | feeding the common buck or adjacent port |

## H2.5.3 result

✅ **Reviewed:** 6 critical power boundaries are checked in complete KiCad netlists and both 80-contact M1 maps match. The missing RP VBUS observation pad was added with no BOM impact.

[Machine evidence](../hardware/ecad/generated/H2-REV53-no-back-power.json).
