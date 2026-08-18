# PWR-0002 — I3 power prerequisite and legacy-candidate audit

- Статус: **Проведено ревью пререквизитов `I3`; supervised 2S confirmed by `DEC-0065`**
- Дата: 2026-08-18
- Dependency step: [`INT-0001/I3`](INT-0001-internal-design-closure-sequence.md)
- Previous envelope: [`PWR-0001`](PWR-0001-zero-based-power-safety-envelope.md)
- Accepted safety load: [`SAFE-0002`](SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)
- Finding: [`FND-0073`](../findings/FND-0073-legacy-power-is-not-a-current-target.md)
- Owner proposal: [`IMP-0052`](../improvements/IMP-0052-safe-field-replaceable-2s-pack.md)

## Boundary

Этот артефакт заново выводит power demand из текущей начинки и сценариев.
Старый `hardware/tscircuit/power.tsx` используется только как проверяемый
candidate/reference. Ни один его MPN, net или physical holder не переносится
автоматически.

Артефакт закрывает входы и отбраковку прежней схемы, но не завершает `I3`.
Формат батареи влияет на protection/gauge/connector/mechanics; владелец
сохранил два отдельно заменяемых слота в `DEC-0062`, `DEC-0064` переоткрыл
их электрическую конфигурацию для сравнения, а `DEC-0065` принял supervised
2S. Exact manager выбирается в `PWR-0005/IMP-0054`.

## Current load classes

Значения ниже — sizing envelopes, не разрешение включить все передатчики
одновременно и не замена measured current exact specimen.

| Load class | Continuous allowance | Transient allowance | Current basis / uncertainty |
|---|---:|---:|---|
| `AON_SAFE_3V3` | `5 mA` minimum | `8 mA` minimum | accepted `SAFE-0002`: latch/gates, 7 RF detectors, optical evidence, comparators, mask and critical LEDs |
| ESP32-S3 branch | `450 mA` | inside common `3 A` step | manufacturer Wi-Fi peak plus PSRAM/I/O margin from `PWR-0001` |
| ESP32-C5 branch | `500 mA` | inside common `3 A` step | manufacturer 5-GHz TX peak plus PSRAM/I/O margin from `PWR-0001` |
| RP2354B branch | `100 mA` | `150 mA` local | architecture allowance until exact clocks/PIO workload are measured |
| display/touch/backlight | `300 mA` provisional | `400 mA` provisional | HMX logic and reference backlight are 3.3-V loads; exact assembly current remains `I4/HIL` |
| microSD | `100 mA` admitted | `300 mA` local | removable-card startup/write spike; exact card matrix remains `I4/HIL` |
| base logic/audio/control | `200 mA` | `300 mA` | slow I/O, codec/receiver/selectors, indicators and margin; exact analog split is `I5` |
| three current nRF candidates | `3 × 13 mA` TX | `3 × 25 mA` local rail envelope | exact `E01-ML01IPX` is a 0-dBm compact module; any higher-power replacement reopens rail/RF review |
| CC1101 branch | `50 mA` | `75 mA` | accepted envelope above maximum listed bare-IC TX current |
| `3V3_MAIN` | **`2.5 A` floor** | **`3.0 A` load step** | preserves previous envelope with margin for current uncertainties and allowed native-radio scenarios |
| `VVOICE=4.0 V` | **`1.25 A`** | **`1.5 A`** | accepted `DEC-0025`; preserves SA518 0.5/1-W class |
| `5V_AUX/EXT` before branch limits | **`1.25 A`** | **`2.0 A`** | one 0.75-A external profile plus audio/IR inrush; exact simultaneous support loads are closed in `I4/I5/I7` |
| protected battery path | `≥3 A` target before margins | `≥4 A` pulse target before exact qualification | at least `12 W` continuous / `15 W` bounded transient; `PWR-0006` derives the 2S minimum currents |

The former `5 V / 3 A` rail was sized around deleted onboard SA868, onboard
LoRa and WS2812 loads. Carrying it forward would spend area/cost without a
current requirement. Conversely, the former `3.3 V / 2 A` rail is below the
accepted current floor and cannot be copied.

## Scenario ledger

| Scenario | Mandatory powered result | Power admission rule |
|---|---|---|
| physical OFF, charger attached | pack protection/gauge and charger only; application rails and AON off | charging may continue; no accessory or TX path can wake |
| USB-only service / absent or admitted pack | AON and bounded core/service rail from valid USB system power | service must not require a battery; a deeply discharged cell is refused by `DEC-0067`, never revived by the product |
| cold boot / update | AON first, then all three compute domains and required service/storage | no TX rail; inrush cannot release STOP or create an evidence pulse |
| `SG-N24` full mix | RP, three nRF, UI/IPC/recording | `3R`, `1T2R`, `2T1R`, `3T`; current candidate is 0-dBm, no hidden high-power allowance |
| native S3 or C5 group | selected compute native RF plus UI/storage | other RF branches power-isolated/quiet; common core load step still includes native peak |
| voice TX | core/audio plus `VVOICE` | battery supplement allowed; unrelated TX and external maximum not assumed |
| U214/Unit profile | core plus current-limited reverse-safe `5V_EXT` | exact profile/inrush admitted before enable; U214 without qualified evidence remains unknown |
| STOP/fault storm | AON and critical indicators survive until input/AON itself is lost | asynchronous gates win; logging and I2C are best effort only |

## What survives from the old design

> `DEC-0064` temporarily reopened 2S; `DEC-0065` confirmed it after the
> `PWR-0006` comparison. The following is again a current base-product input.

- In the accepted `2S / 6.0…8.4 V` topology all three main output rails
  are ordinary bucks and SA518 keeps its accepted 4.0-V profile.
- A common efficient 3.3-V converter plus separately switched radio/storage/
  analog branches is lower-cost than one converter per small load.
- Charge input and pack require cell temperature, per-cell voltage, current
  limit and balance/protection evidence.
- C5 and RP service USB VBUS remain protected data/sense inputs and may not
  backfeed the system. Only the S3 product USB is a normal power input.

These are reusable principles, not approval of `BQ25887`, `S-8252A`,
`MP2315`, `TPS7A2033`, the old switch location or the open holder.

## Verified legacy mismatches

| Old claim/topology | Checked fact | Consequence |
|---|---|---|
| `BQ25887` is charger plus usable system power path | TI lists an active 2S boost **charger** with ADC/balancing but no NVDC power path | no battery/deeply discharged battery cannot power recovery; system load and charge termination remain coupled |
| `BQ25887 ADC = fuel gauge` | ADC reports instantaneous input/cell/charge/temperature values; it is not a discharge coulomb counter or learned SOC gauge | remaining runtime/health cannot be claimed; an actual pack gauge or explicitly weaker voltage-only UI is required |
| two `5.1 kΩ` Rd resistors justify fixed 3-A draw | Rd declares sink role; it does not report source `Default/1.5 A/3 A` capability to the charger | Type-C CC logic or PD controller must bound input current; ICO/VINDPM is extra protection, not protocol proof |
| master switch before old `BAT` node gives true off | the same open contact also separates cells from the charger BAT node | device cannot charge while physically off; abrupt cut also has no hardware orderly-shutdown hold-up |
| `3V3 MP2315 / 2 A` | accepted current floor is `2.5 A`, transient `3 A` | undersized before exact thermal/derating proof |
| old rail set is complete | no accepted `AON_SAFE`, no 4-V voice rail, no reverse-safe external branch, no reviewed per-group switching/fault aggregation | incompatible with current I2/quiet-state contracts |
| open `2×18650` frame is already a pack | two independently replaceable cells add wrong orientation, mixed model/age/SOC and one-cell removal states | battery mechanical/electrical class requires an explicit owner decision before protector/gauge selection |

The old source also uses resistor symbols as TVS/PPTC proxies and a generic
`pinrow3` battery placeholder. Those constructs were useful for connectivity
experiments but are not exact physical devices and cannot enter the living
principled diagram.

## Charger/front-end architectures after the pack decision

The following are current, manufacturer-supported comparison directions. They
are not selected MPNs yet, so distributor availability is deliberately deferred
until the owner resolves pack format.

| Direction | Core devices | Preserved result | Cost/complexity |
|---|---|---|---|
| `C5V` reference-derived 5-V input | TI `BQ25883` NVDC 2S boost charger + `TUSB320LAI` CC logic + real 1–2S gauge/protector such as `BQ28Z610-R1` | plain 5-V USB, BC1.2/Type-C current detection, instant-on/power path, balance/protection/SOC | recommended cost-conscious baseline; TI `PMP40496` proves the same device classes, but exact Leshy2 circuit still requires review |
| `CPD` modern PD input | `TPS25751` + `BQ25798` + real pack gauge/protector | faster charging, wide input, high-headroom NVDC path and battery supplement | best electrical headroom; materially more BOM, configuration, layout and compliance work for an ~18-Wh handheld |
| `CLEG` repaired legacy | `BQ25887` plus separate CC logic, ideal power path, gauge/protector and off/charge redesign | can retain integrated charger balancing | dominated: once missing functions are added it is not simpler or cheaper than `C5V` |

Primary references:

- [TI BQ25887 product page](https://www.ti.com/product/BQ25887)
- [TI BQ25883 product page](https://www.ti.com/product/BQ25883)
- [TI TUSB320LAI product page](https://www.ti.com/product/TUSB320LAI)
- [TI PMP40496 2S reference design](https://www.ti.com/tool/PMP40496)
- [TI BQ28Z610-R1 product page](https://www.ti.com/product/BQ28Z610-R1)
- [TI BQ25798 product page](https://www.ti.com/product/BQ25798)
- [TI TPS25751 product page](https://www.ti.com/product/TPS25751)

## Exit from this prerequisite pass

- Load/scenario envelope: **reviewed**.
- Legacy useful ideas: **separated from obsolete implementation**.
- Legacy power source: **reference only; rejected as current target**.
- Battery-format input: `DEC-0062/0065` retain two individually replaceable
  cells in supervised 2S and the hard pre-connect/reverse/mismatch/removal
  boundary.
- The charge frontend is selected by `DEC-0063`; next select the exact
  admission/protector/gauge in `IMP-0054`, then the compatible rail parts and
  close every fault/loss/thermal row.
