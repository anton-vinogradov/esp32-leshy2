# AUD-0010 — high-speed USB host use cases, feasibility and safety boundary

- Статус: **Проведено ревью фактов; product disposition открыт**
- Дата snapshot: 2026-08-17
- Delta: `W-EXTRA-16`
- Предложение: [`IMP-0033`](../improvements/IMP-0033-native-high-speed-usb-host.md)
- Finding: [`FND-0047`](../findings/FND-0047-full-speed-usb-is-not-raw-sdr-tier.md)

## Пользовательские результаты, которые нельзя смешивать

| Attached-device class | Typical result | Speed reality | Additional burden |
|---|---|---|---|
| programmers/debug probes/USB-UART | flash, recover, diagnose another owned target | usually FS/LS is sufficient; throughput is not the main problem | exact CDC/vendor/HID driver, target voltage/power/isolation and authorization |
| HID and simple instruments | keyboard/mouse, low-rate measurement/control | FS/LS sufficient | class/profile allowlist and safe disconnect |
| mass storage | import/export/update/corpus | FS works slowly; HS materially improves large capture transfer | filesystem ownership, malware/untrusted-parser boundary, power/removal |
| cellular/serial modems | command/data link | often CDC/vendor bulk; actual need depends on modem | driver, network/regional qualification and peak current |
| USB SDR/raw-IQ | HackRF-class receive/transmit stream | genuinely HS; FS cannot carry useful full-rate IQ | sustained bulk scheduling, buffers/storage/compute, class driver and drop evidence |
| external Linux/compute | command/result or bulk dataset exchange | command link may be FS; raw data benefits from HS | protocol, trust, update/recovery and whether compute is host or device |

“USB host” therefore is not one finished feature. The product may expose a
general enumerating port, but each useful device class still needs a qualified
driver/profile and truthful performance/safety evidence.

## Current controller facts

- ESP32-S2/S3 USB OTG is Full-Speed: 12 Mbit/s line rate, host or device. It
  does not become High-Speed because the connector is USB-C.
- RP2350/RP2354 has a USB 1.1 controller/PHY with FS/LS host or device support.
- MAX3421E, used by older M5 USB host modules, is Full-/Low-Speed host only and
  cannot implement the accepted raw-data tier.
- Current ESP32-P4 documentation specifies an integrated USB 2.0 High-Speed OTG
  transceiver supporting 480 Mbit/s HS plus FS/LS, host or device. This proves a
  current MCU-class implementation is feasible without an external ULPI PHY;
  it does **not** select P4 or a compute topology for Leshy2.
- Current ESP USB host documentation exposes control, bulk, interrupt and
  isochronous transfers, HS devices and custom clients. Official examples cover
  CDC/USB-UART variants, MSC, HID and UVC. The stack still lists limitations:
  asynchronous transfers only, one active configuration, no transfer timeouts,
  and incomplete hub error/FS-behind-HS-hub behavior. “PHY exists” therefore is
  not blanket accessory compatibility.

## Why Full-Speed is not the raw-SDR tier

HackRF One officially uses High-Speed USB 2.0 and supports up to 20 million
8-bit complex samples per second. A 20 Msps stream with one 8-bit I and one
8-bit Q value is 40 MB/s of payload before USB overhead. USB FS has only a
12 Mbit/s line rate, so no buffering trick can make it an equivalent live path.
Even HS line rate is not guaranteed application throughput; sustained loss/drop
evidence and lower qualified modes remain mandatory.

This does not mean Leshy2 must perform desktop GNU Radio workloads. A native HS
host can provide bounded capture/stream/control profiles, while heavy analytics
may still run on an attached owner-controlled compute device. Raw reachability,
on-device decoding and full Linux compatibility are separate claims.

## Connector and role are downstream, but not free

The product result requires:

- a protected 5 V VBUS source, default off, with current limit, overcurrent
  reporting, discharge and backfeed prevention;
- explicit host/device/power-role state and cable/accessory identity; connector
  shape alone never implies role;
- independent product programming/recovery even if the application host stack,
  HS owner or connector is broken;
- profile-specific current budget and battery/runtime/thermal effects;
- ESD, insertion/removal, short and malformed-descriptor/parser testing;
- local consent before storage write, programmer action or external TX;
- FIDO exclusive mode disables host VBUS and all accessory enumeration;
- a qualified external transmitter starts safe/off, loses every lease on
  disconnect/reset/STOP and never inherits permission merely from USB attach.

A dedicated HS host/data connector and a separate device/recovery connector is
often simpler and safer than one fully dual-role connector. Conversely, a
well-designed USB-C DRP can save an opening. G3/G7 must compare both; accepting
HS host does not silently decide the connector count.

## Sources

- [Espressif ESP32-S3 USB OTG overview](https://docs.espressif.com/projects/esp-iot-solution/en/release-v2.0/usb/usb_overview/usb_otg.html)
- [Raspberry Pi RP2350 product information](https://www.raspberrypi.com/products/rp2350/)
- [Analog Devices MAX3421E product/datasheet](https://www.analog.com/en/products/max3421e.html)
- [Espressif ESP32-P4 current datasheet](https://documentation.espressif.com/esp32-p4_datasheet_en.html)
- [Espressif ESP32-P4 USB host documentation](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html)
- [Great Scott Gadgets HackRF One specifications](https://greatscottgadgets.com/hackrf/one/)
- [USB-IF USB Type-C 2.0 specification](https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf)

## Audit gate

- [x] general host, programmer, storage, modem, SDR and compute results separated;
- [x] FS/HS claims checked against current primary documentation;
- [x] current integrated-HS feasibility identified without selecting silicon;
- [x] line rate separated from sustained application throughput;
- [x] connector data/power role separated from USB speed;
- [x] recovery, FIDO, external-TX and malformed-device boundaries recorded;
- [ ] owner disposition through `IMP-0033`.
