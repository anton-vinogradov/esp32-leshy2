# AUD-0012 — 6 GHz/Wi-Fi 6E product scope and feasibility

- Статус: **Проведено ревью; owner selected reject/C in `DEC-0040`**
- Дата snapshot: 2026-08-17
- Delta: `W-EXTRA-17`
- Finding: [`FND-0048`](../findings/FND-0048-5ghz-does-not-imply-6ghz.md)
- Предложение: [`IMP-0034`](../improvements/IMP-0034-6ghz-wifi6e-placement.md)
- Решение: [`DEC-0040`](../decisions/DEC-0040-reject-6ghz-wifi6e.md)

## Product result

6 GHz is mission-aligned: authorized Wi-Fi 6E discovery, channel/environment
observation, association and bounded diagnostics are radio results. It is not,
however, an automatic extension of the accepted 2.4/5 GHz result.

The owner decision is whether every base Leshy2 must autonomously cover 6 GHz,
whether a qualified optional radio/compute profile should preserve it without
base burden, or whether it is outside the target entirely.

## Current silicon and integration facts

- Current ESP32-C5 documentation specifies 1T1R Wi-Fi 6 at 2412–2484 MHz and
  5180–5885 MHz. It has no 6 GHz RF path. Selecting C5 for accepted 5 GHz would
  therefore not satisfy `W-EXTRA-17`.
- Current NXP IW693 proves embedded Wi-Fi 6E silicon exists. The family provides
  2×2 2.4/5/6 GHz operation and connects to a host over PCIe or 4-bit SDIO;
  partner modules expose two antenna pins and recommend an i.MX-class host.
- Intel AX210 similarly proves mature 2.4/5/6 GHz modules, but its Wi-Fi link is
  PCIe, Bluetooth is USB and common modules are M.2. It is evidence for an
  external-compute/module class, not a drop-in MCU radio.
- None of those examples selects a Leshy2 part. A real candidate still has to
  prove host driver/licensing, scan/monitor/injection limits, firmware control,
  throughput, sleep/recovery, RF coexistence and lifecycle.

## Why 6 GHz is not a free antenna checkbox

A 6E implementation adds or changes all of the following relative to the
accepted C5-class 2.4/5 GHz result:

- radio plus host interface and driver ownership;
- one or more 5–7 GHz RF paths, matching/filtering and antenna placement;
- current peaks, sleep/resume and thermal/runtime accounting;
- regional channel/power/indoor/very-low-power policy and certified RF profile;
- test fixtures and conducted/radiated evidence across the actual enclosure;
- security/update/recovery for radio firmware and any companion host.

The regulatory profile is not globally uniform. The current EU harmonized
WAS/RLAN allocation covers 5945–6425 MHz under technical conditions, while US
rules distinguish standard-power/AFC, low-power-indoor and very-low-power
classes across different portions and conditions. Product firmware must derive
allowed channels/power/mode from region and device class, default TX off when
uncertain, and never advertise blanket worldwide 6 GHz transmit support.

## Capability boundary if retained

The minimum honest profile is not “has Wi-Fi 6E” but a matrix of independently
qualified results:

1. passive discovery/environment observation;
2. ordinary STA association and bounded network diagnostics;
3. AP/active test modes, only where radio/driver/regulatory class supports them;
4. Lab/Controlled-Zone Wi-Fi security workflows under existing authorization,
   isolation, arm/lease/STOP and capture provenance gates;
5. explicit unavailable states rather than emulating 6 GHz with 5 GHz data.

Raw full-band SDR is not implied. Conversely, rejecting or deferring 6 GHz does
not weaken the already-accepted autonomous 2.4/5 GHz requirement.

## Sources

- [Espressif ESP32-C5 current datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [NXP IW693 product family and host interfaces](https://www.nxp.com/products/IW693)
- [Intel AX210 official specifications](https://www.intel.com/content/www/us/en/products/sku/204836/intel-wifi-6e-ax210-gig/specifications.html)
- [EU 2025/913 update for 5945–6425 MHz WAS/RLAN](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32025D0913)
- [FCC 6 GHz device-class summary](https://docs.fcc.gov/public/attachments/DA-24-1215A1_Rcd.pdf)

## Audit gate

- [x] 5 GHz and 6 GHz physical capability separated;
- [x] current MCU and host-attached 6E examples checked without silicon selection;
- [x] radio, host, antenna, power, driver and recovery burdens exposed;
- [x] region/device-class TX boundary recorded;
- [x] passive, ordinary active and dangerous workflows kept distinct;
- [x] base, optional profile and rejection dispositions prepared for owner;
- [x] owner selected `IMP-0034/C`; no base or optional 6E product profile.
