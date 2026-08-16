# AUD-0005 — M5 expansion ecosystem coverage and Leshy2 attachment boundary

- Статус: **Проведено ревью; вариант B принят `DEC-0034`**
- Дата snapshot: 2026-08-16
- Scope: актуальные official M5Stack Unit/Cap/Module interfaces и продукты,
  которые пересекаются с reviewed wishlist Leshy2
- Связанные finding/decision: [`FND-0042`](../findings/FND-0042-m5-is-not-one-interface-or-ninety-percent-solution.md),
  [`DEC-0033`](../decisions/DEC-0033-external-m5-ibutton-profile.md)
- Предложение: [`IMP-0028`](../improvements/IMP-0028-m5-first-not-m5-only-expansion.md)
- Решение: [`DEC-0034`](../decisions/DEC-0034-m5-first-two-tier-expansion.md)

## Вопрос аудита

Можно ли использовать M5Stack ecosystem как основной способ вынести редкие
функции из base BOM без потери продукта, и достигает ли он хотя бы 90% задач?

Ответ зависит от того, что называется «покрытием»:

1. **Connector reachability** — сигналы физически можно передать через
   совместимый разъём.
2. **Catalog availability** — существует актуальный официальный M5 accessory,
   который заявляет нужный пользовательский результат.
3. **Product qualification** — exact SKU/revision, питание, уровни, protocol,
   lifecycle, safety, firmware и HIL действительно приняты Leshy2.

Эти уровни нельзя смешивать. Разъём GPIO не превращает отсутствующий LF reader
или iButton contact tool в готовый продукт, а совпадающий I²C адрес не доказывает
протокол или безопасное hot-plug поведение.

## Это не один интерфейс

| Семейство | Физика и базовые сигналы | Что реально даёт | Почему не взаимозаменяемо |
|---|---|---|---|
| M5 Unit `HY2.0-4P` | `GND, 5V, signal 1, signal 2` | Port A = I²C, B = GPIO/special one-wire, C = UART, white = custom | нет ID/detect pin; protocol, direction, levels, pull-ups и power profile зависят от exact Unit |
| Cardputer-Adv Cap | `2.54-14P` | SPI + `CS/BUSY/IRQ/RESET`, I²C, UART, `5VIN/5VOUT/GND` | отдельная механика и 11 signal roles; U214 использует почти весь контракт |
| M5-Bus Module | `2×15`, 2.54 mm | 5 V/3.3 V/BAT и host-dependent GPIO/buses | pin mapping меняется между Core families; Modules используют DIP/jumpers, общий EN и могут конфликтовать |
| Smart/standalone Unit | часто HY2.0 только как собственный expansion или fixed protocol | локальный ESP/STM32/modem и собственная firmware | наличие Grove не означает, что Leshy2 управляет внутренним radio напрямую или контролирует его update chain |

Официальная convention фиксирует 5 V на втором контакте всех Port A/B/C, но не
обещает blanket 5-V tolerance сигнальных GPIO. Поэтому совместимость требует
per-profile qualification, а не одного общего «M5 mode».

## Релевантный актуальный каталог

| Leshy2 result | Official M5 example | Interface / evidence | Audit disposition |
|---|---|---|---|
| внешний GNSS | Unit GPS v1.1 `U032-V11` | Port C UART, 5 V/31.64 mA, NMEA 0183 4.1 | сильное прямое покрытие; уже accepted first profile |
| LoRa + GNSS | Cap LoRa-1262 `U214` | Cap SPI/control + UART + I²C, 868–923 MHz, +22 dBm, LoRa 5 V/163.4 mA | сильное прямое покрытие; уже accepted first profile |
| HF NFC | Unit NFC `U216` | Port A I²C `0x50`, 5 V/67.65 mA continuous read, A/B/F/V + emulation direction | сильное прямое покрытие; exact modes всё ещё corpus/HIL-conditional |
| cellular | Unit CatM `U128` | Port C UART, Cat-M/NB-IoT, network peak 249 mA | частичное: не broadband LTE и не GSM/voice; country/operator/SIM/FOTA qualification отдельно |
| haptic | Unit Vibrator `U059` | Port B PWM/GPIO, 5 V/424.35 mA at stated operating point | прямое external haptic покрытие, но высокий port-current и механическая вибрация |
| orientation/motion | Unit Mini IMU `U095` | Port A I²C `0x68`, MPU6886 | прямое 6-axis покрытие; Mini IMU-Pro has lifecycle/magnetic-placement caveats |
| physical text input | Unit CardKB2 `U215` | custom HY2.0 I²C/UART; ESP32-C61, USB recovery, 19.31 mA standby | прямое optional keyboard покрытие; это active programmable accessory |
| two same-address NFC frontends | 2×U216 + PaHub v2.1 | PCA9548A channels isolate repeated `0x50` address | electrically plausible, but relay timing, two-field coexistence and end-to-end firmware remain unqualified |
| ordinary I²C fan-out | PaHub v2.1 | one Port A to six isolated I²C channels, address `0x70..0x77` | useful qualified topology pattern; does not expand UART/GPIO timing paths |
| basic GPIO fan-out | PbHub | Port A I²C to six simple GPIO channels through MCU | not transparent Port B: vendor explicitly excludes timing-dependent Units |
| consumer IR | Unit IR `U002` | Port B TX/RX, receiver fixed at 38 kHz | useful simple remote accessory, but **does not** replace accepted carrier-learning IR path |
| fixed 433 MHz ASK | RF433T/R | Port B fixed 433.92 MHz ASK pair | useful narrow accessory, but **does not** replace CC1101 tuning/RSSI/raw scope |
| UHF RFID | Unit UHF-RFID `U107` | Port C UART, 840–960 MHz, 18–26 dBm | extra UHF result; neither HF NFC nor LF 125 kHz replacement |
| USB host/peripheral | Module USB `M020` | M5-Bus + MAX3421E SPI | EOL; CoreS3 incompatible warning; only 12/1.5 Mbps full/low-speed, not high-speed USB |

The current catalog audit found **no official M5 iButton/Dallas-key Unit and no
official LF 125 kHz access-key Unit**. RFID2 is 13.56 MHz and Unit UHF-RFID is
840–960 MHz; neither may be renamed to LF. M5's own software documentation does
show that OneWire can run in software on a GPIO with a 4.7 kΩ pull-up. This is
evidence for a small protected M5-style Port-B contact adapter, not evidence for
a ready-made commercial accessory.

## Coverage calculation against Leshy2, not against catalog size

The denominator is the 18 reviewed hardware additions for which external
attachment is a plausible product strategy. Pure software rows
(`W-EXTRA-01/03/12`) and the separate base-radio question `W-EXTRA-17` are not
inflated into this number.

| # | External hardware class | Official M5 full result | Partial/custom result |
|---:|---|---|---|
| 1 | GNSS | yes, GPS v1.1/U214 | — |
| 2 | common-band LoRa | yes, U214 | — |
| 3 | primary HF NFC | yes, U216 | exact modes conditional |
| 4 | BLE connection-follow sniffer | no | custom smart accessory possible |
| 5 | Bluetooth Classic controller | no | custom HCI accessory possible |
| 6 | additional HF/VHF/SDR receiver | no | command-level custom accessory possible; raw IQ is not |
| 7 | digital voice backend | no | custom smart modem possible |
| 8 | full-duplex repeater backend | no | custom dual-RF appliance possible |
| 9 | wideband SDR + Linux analytics | no | requires a separate high-throughput class |
| 10 | cellular | no full result | Cat-M/NB-IoT only |
| 11 | LF 125 kHz RFID | no | custom protected frontend required |
| 12 | second independent NFC frontend | no qualified relay | two U216 through PaHub is electrically plausible |
| 13 | heavy recovery/analytics compute | no | separate high-throughput compute link required |
| 14 | iButton/1-Wire contact tool | no | accepted passive protected Port-B adapter |
| 15 | haptic feedback | yes, U059 | high current |
| 16 | IMU/orientation | yes, U095 | — |
| 17 | physical keyboard | yes, U215 | active accessory firmware |
| 18 | high-speed USB accessory host | no | old M020 is EOL and full/low-speed only |

Results:

- **6/18 = 33.3%** have a current official M5 product that directly matches the
  product result strongly enough to begin qualification.
- **8/18 = 44.4%** if narrow cellular and the unproven dual-U216 topology count
  as partial coverage.
- **9/18 = 50.0%** after adding our own passive M5-style iButton adapter.
- therefore **M5-only does not meet a 90% Leshy2 result target**.

This deliberately avoids a misleading percentage over hundreds of easy
temperature/light/relay Units that are not Leshy2 wishlist rows.

## Where the 90% idea becomes achievable

M5 is strong for low-rate control-plane devices: I²C sensors/frontends, UART
modems/GNSS, GPIO/timing accessories and the U214 SPI Cap. It is weak exactly
where the remaining wishlist becomes data-plane heavy: raw SDR/IQ, Linux-class
compute and high-speed USB host.

If locally intelligent custom accessories are allowed to own radio timing and
send bounded commands/results rather than raw samples, Unit/Cap signal classes
are a plausible transport for **15/18 = 83.3%** of the attachment classes. The
three exceptions are wideband raw SDR/Linux, heavy external compute and the
high-speed host path itself. This is much better than the 50% catalog-result
coverage, but still below 90% and requires custom hardware/firmware.

A two-tier expansion model can cover more than 90% of the *attachment classes*:

1. M5 Unit A/B/C plus Cardputer-compatible Cap for low-rate and U214-class
   accessories.
2. A separate native high-speed USB data/power path for SDR, external compute
   and general host devices.

Together these interfaces are a plausible transport for **18/18 attachment
classes** in the current external-hardware denominator. The practical target
is stated as `>=90%`, because exact USB classes, drivers, throughput, power and
regional radio profiles can still fail qualification.

That statement is connector reachability, not feature completion. Every exact
radio, protocol and driver still needs its own profile and acceptance evidence.
Without the second tier, M5-compatible custom modules can plausibly carry only
command/summary traffic; they cannot preserve arbitrary raw high-rate data.

## Architecture-neutral minimum contract for native M5 support

### Unit-port electrical contract

- at least one native HY2.0-4P surface; G3 compares one-port+dock, two-port and
  fixed A/B/C layouts rather than selecting a count here;
- 5 V rail default-off with per-port load switch/current limit, back-feed
  blocking, discharge behavior and observable fault/current state;
- both signal lines independently usable as protected 3.3 V GPIO, UART,
  I²C/open-drain and timing I/O; 5 V signal tolerance is never assumed;
- switchable pull-ups and profile-specific ADC/PWM/one-wire conditioning;
- wrong profile, short, stuck-low, overcurrent, brownout and detach fail closed;
- no hot-plug promise until the exact Unit passes powered insertion/removal HIL.

The current known sizing points are 31.64 mA GPS, 67.65 mA U216, 249 mA CatM
network peak and 424.35 mA Vibrator. A provisional 0.5 A per active Unit-port
class is therefore a useful G3/G4 candidate, not yet an accepted rail value.
Actuators above the final shared battery/thermal budget require external power.

### Cap electrical contract

- preserve all official U214 roles: SPI `SCK/MOSI/MISO/NSS`, `BUSY/IRQ/RESET`,
  GNSS UART, I²C and `5VIN/5VOUT/GND`;
- control both 5 V directions so an externally powered Cap/Unit cannot backfeed
  a sleeping, stopped or unpowered Leshy2;
- default U214 rail and RF path off; antenna-present confirmation before power,
  because M5 explicitly warns against powering U214 without its antenna;
- hard STOP removes the energy/enable required for external TX and invalidates
  its lease; a later reconnect cannot restore channel, power or target;
- the 84×24×15.2 mm Cap, RP-SMA antenna and cable/bending envelope are G3
  mechanical inputs, not a connector-only detail.

### Concurrency and fan-out contract

- repeated I²C addresses use isolated buses or an explicit PaHub-class mux;
  passive wire splitting is allowed only for distinct addresses and proven bus
  capacitance;
- UART/GPIO timing Units are not routed through PbHub unless that exact Unit is
  proven compatible;
- profile selection reserves buses/pins/power atomically and reports conflicts
  before energizing anything;
- `U214 + its downstream Port A + another Unit port` is an important concrete
  configuration: LoRa/GNSS + U216 + passive iButton can coexist without
  onboard duplication;
- `GPS Unit + U216 + iButton` without U214 requires three simultaneous protocol
  surfaces or a Cap-to-A/B/C dock; G3 must compare that use case explicitly.

### Identity and software contract

Native Grove has no identity pin. Therefore automatic universal enumeration is
not a safe baseline.

- unknown port starts unpowered;
- the user selects a profile or a separately identified carrier provides an ID;
- discovery after power is exact-profile logic: I²C scan alone cannot identify
  UART/GPIO Units and an address alone cannot distinguish revisions safely;
- each profile manifest records SKU/revision/lifecycle, protocol, addresses,
  signal direction/levels/pull-ups, current/peak, power sequence, hot-plug flag,
  firmware version, capability bitmap, safety level, STOP behavior and HIL set;
- driver code is versioned with source/licence/provenance; Arduino availability
  does not prove integration into the eventual Leshy2 runtime;
- UI distinguishes `commanded`, `module-reported`, `observed-current` and
  independently measured actual-TX states.

### Programmable accessory contract

CardKB2, PbHub, C6L, cellular modems and many newer Units contain their own MCU
or modem firmware. They do not become invisible trusted peripherals.

- firmware identity/version and failure behavior are part of the accessory
  profile;
- a flashable selected accessory needs an owner-usable update/recovery path, or
  it is explicitly treated as a factory-firmware dependency with bounded claims;
- a factory-locked modem/secure element cannot be described as satisfying the
  owner-controlled update promise for Leshy2 firmware;
- accessory loss/reset/update disarms every dependent session.

### Mechanical and RF contract

- HY2.0 cable alone is not field retention: G3 supplies strain relief, keyed
  routing and a replaceable mount for common 24/32/48/72/84 mm Unit lengths;
- M5-compatible LEGO/M2 holes may be used by a rail/carrier, but exact spacing
  is verified per SKU;
- magnets are not a universal mount: M5 explicitly warns that magnetic hosts
  disturb the Mini IMU-Pro magnetometer;
- GNSS ceramic antenna sky view, LoRa/UHF antenna clearance, body shadowing,
  self-desense, thermal rise and connector torque enter enclosure/HIL evidence;
- an RF-emitting Unit is never powered merely because it was plugged in.

## Why native M5-Bus is not the default

The 30-pin M5-Bus would add a large 54 mm stack surface, multiple power rails,
BAT/EN semantics and host-specific pin conflicts. Official Modules themselves
use DIP switches to adapt between Core generations; the old USB Module even
documents an EN conflict and incompatibility with CoreS3.

Therefore blanket M5-Bus compatibility is a poor base-product promise. An exact
Module may be supported later by a profile-specific powered carrier connected
to the general Cap/high-speed expansion. The carrier supplies only the rails
and pins that module needs and does not expose an unqualified BAT/HPWR stack.

## Cost conclusion

M5-first can lower **base-device** cost without silently removing accepted
functions:

- GNSS, LoRa, NFC, optional haptic/IMU/keyboard/cellular frontends are not paid
  by every owner;
- one protected port platform and reusable driver/profile framework replaces
  several one-off connectors and onboard RF frontends;
- field failure of an accessory does not force base-board replacement.

It does not necessarily minimize **full-kit** cost, mass or cable burden. A
fully equipped owner buys modules, mounts and protection repeatedly. G4 cost
comparison must therefore show base, likely field kit and maximum lab kit
separately; only the base price is allowed to fall without pretending that the
accessories are free.

## ⚠️ Catalog capabilities that were not silently added

The catalog review exposed plausible user results not present in the current
wishlist: UWB indoor ranging, UHF inventory tags, an external secure element,
thermal/camera accessories, Ethernet/PoE/CAN/RS485, and additional detachable
encoders/buttons/actuators. They are useful evidence that the low-rate platform
has a long tail, but catalog existence is not a product requirement.

These results remain an explicit future owner-review queue. They are excluded
from both numerator and denominator above, carry no base-BOM/resource promise
and cannot be used to inflate the 90% figure. The queue should be dispositioned
one result at a time after the general expansion strategy is decided.

## Reviewed conclusions

- [x] Unit, Cap and M5-Bus are separated rather than called one interface.
- [x] Current relevant official products, lifecycle and power points are
  inventoried from primary vendor documentation.
- [x] iButton and LF 125 kHz are not falsely attributed to existing M5 Units.
- [x] coverage is calculated against Leshy2 external hardware rows, not catalog
  volume.
- [x] M5-only is proven below 90% of product results.
- [x] M5-first plus a separate high-throughput tier is a viable route to at
  least 90% attachment-class reachability, pending owner decision and G3/G4.
- [x] exact connector count, pins, rail values and mechanics remain correctly
  deferred to product design and complete architecture comparison.

## Primary sources

- [M5Stack HY2.0-4P Port A/B/C convention](https://docs.m5stack.com/en/learn/interface/grove)
- [Cardputer-Adv 14-pin EXT pin map](https://docs.m5stack.com/en/core/Cardputer-Adv)
- [Cap LoRa-1262 U214](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [Unit GPS v1.1](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [Unit NFC U216](https://docs.m5stack.com/en/unit/Unit_NFC)
- [Unit CatM](https://docs.m5stack.com/en/unit/cat_m)
- [Unit Vibrator](https://docs.m5stack.com/en/unit/vibrator)
- [Unit Mini IMU](https://docs.m5stack.com/en/unit/imu)
- [Unit CardKB2](https://docs.m5stack.com/en/unit/Unit_CardKB2)
- [Unit PaHub v2.1](https://docs.m5stack.com/en/unit/unit-PaHub%20v2.1)
- [Unit PbHub limitations](https://docs.m5stack.com/en/unit/pbhub)
- [Unit IR](https://docs.m5stack.com/en/unit/ir)
- [Unit RF433T](https://docs.m5stack.com/en/unit/rf433_t)
- [RFID2, 13.56 MHz](https://docs.m5stack.com/en/unit/rfid2)
- [Unit UHF-RFID, 840–960 MHz](https://docs.m5stack.com/en/unit/uhf_rfid)
- [Unit UWB indoor-ranging scope and firmware limit](https://docs.m5stack.com/en/unit/uwb)
- [Unit ID ATECC608B secure element](https://docs.m5stack.com/en/unit/id)
- [M5 software OneWire and 4.7 kΩ pull-up](https://docs.m5stack.com/en/mpy/official/machine)
- [M5 Module USB EOL/compatibility warning](https://docs.m5stack.com/en/module/usb)
- [MAX3421E full/low-speed limits](https://www.analog.com/en/products/max3421e.html)
- [M5 Module DIP/pin adaptation example](https://docs.m5stack.com/en/guide/dip_switch/module_lora868_v1.2/pins_change)
