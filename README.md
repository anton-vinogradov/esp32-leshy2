# Leshy2 hardware

[Русский](README.ru.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware)

Leshy2 is an open, autonomous instrument for radio observation,
communications, diagnostics and authorized research of wireless and contact
systems. This documentation describes what the target device does and how it
is built.

## What the device can do

- Operate three full-function nRF24 radios concurrently in `3R`, `1T2R`,
  `2T1R` and `3T` combinations.
- Work with 2.4/5-GHz Wi-Fi, Bluetooth LE, ESP-NOW, IEEE 802.15.4,
  315/433/868/915-MHz Sub-GHz, FM/AM/SW/LW, VHF/UHF voice and IR.
- Route all nine onboard RF paths to external antennas: two RP-SMA and seven
  SMA ports.
- Show menus, a spectrum waterfall and path state on a 3.5-inch portrait
  `320×480` touch IPS display driven by direct QSPI.
- Record data and audio to removable microSD, play through a speaker or
  headphones and capture from the built-in microphone.
- Accept a rear M5Stack U214 LoRa/GNSS Cap and a separately protected M5 Unit
  port for external GNSS, LoRa, NFC, iButton/1-Wire and other modules.
- Give the owner independent programming, recovery and diagnostic paths for
  every programmable controller.

## How it is built

The device contains four isolatable compute domains. The
`ESP32-S3-WROOM-1U-N16R2` owns UI, display, storage and audio;
`ESP32-C5-WROOM-1U-N8R8` owns native 2.4/5-GHz radio, IEEE 802.15.4 and IR;
`SC1512-A4` (RP2354B) owns the three nRF24 radios, Sub-GHz, voice and U214;
`MSPM0C1104SDGS20R` independently admits the battery pack. Unused interfaces
are powered down and placed into a verifiable quiet state.

![Current Leshy2 layout](docs/images/current-clamshell.svg)

## Safety levels

1. **Normal mode** — receive, diagnostics, maintenance and ordinary
   communications.
2. **Laboratory** — passive, defensive and constrained research tools.
3. **Laboratory → Controlled Zone** — potentially dangerous active functions
   for an isolated environment or an explicitly authorized target. Every entry
   displays a fresh mandatory warning.

Physical `STOP` dominates transmit hardware and `RE-ARM` requires a separate
action. Initial setup requires acceptance of a non-aggression agreement; it
does not replace law, spectrum licensing or the target owner's permission.

## Documentation

- [Hardware architecture and components](docs/hardware.md)
- [Exact controller pin assignment](docs/pinout.md)
- [Safety, power, update and recovery](docs/safety.md)
- [Firmware capabilities and architecture](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
