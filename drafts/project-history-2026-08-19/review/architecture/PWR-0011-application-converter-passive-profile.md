# PWR-0011 — exact application-converter energy and feedback passives

- Статус: **Проведено ревью бумажного электрического профиля**
- Дата: 2026-08-18
- Parent topology: [`PWR-0008`](PWR-0008-exact-downstream-rail-tree.md)
- External-port protection: [`PWR-0010`](PWR-0010-external-efuse-passive-profile.md)
- Decision: [`DEC-0072`](../decisions/DEC-0072-exact-converter-energy-feedback-passives.md)
- Propagation review: [`REV-0005AC`](../reviews/REV-0005AC-application-converter-passive-profile.md)
- Post-buck containment: [`PWR-0020`](PWR-0020-independent-post-buck-containment.md)

## Scope

Этот проход заменяет abstract feedback/input/output networks четырёх уже
принятых преобразователей точными физическими компонентами. Он проверяет
режим `TPS629203`, выходные напряжения трёх `TPS564252`, nominal/effective
capacitance margin, LC pole, lifecycle и доступность exact MPN. Каждая
физическая деталь внесена отдельным экземпляром в machine source и living
diagram.

EN/PG pull networks subsequently close in `PWR-0012/DEC-0073`; this artifact
still does not close copper/thermal geometry, load-step, ripple/EMI or
specimen HIL. Артефакт не разрешает начинать KiCad.

## `TPS629203DRLR` AON profile

| Function | Exact physical part | Accepted connection |
|---|---|---|
| mode/configuration | `Yageo RC0402FR-0742K2L`, 42.2 kOhm, 1%, 0402 | `MODE/S-CONF` to GND: VSET, auto PFM/PWM with AEE, up to 2.5 MHz, output discharge off |
| output selection | no fitted component | `FB/VSET` deliberately open; datasheet decodes open or at least 249 kOhm as fixed 3.3 V |
| input energy | `TDK CGA5L1X7R1E475K160AC`, 4.7 uF, 25 V, X7R, 1206 | one local VIN-to-GND capacitor |
| output energy | `Murata GRM31CR71A226KE15L`, 22 uF, 10 V, X7R, 1206 | one local `AON_RAW_3V3` converter capacitor; `VOS` senses its positive terminal; `PWR-0020` adds a separately protected output bank |

TI requires at least 3 uF effective input and 10 uF effective output
capacitance and recommends nominal 4.7/22 uF with 2.2 uH. The chosen 1206
parts deliberately avoid a smaller high-bias package. Exact TDK/Murata
characteristic curves remain reference rather than a production guarantee;
capacitance, ripple and supervisor hold-up therefore remain specimen gates.

`FB/VSET` is not fitted with an unnecessary 249-kOhm resistor. Open is an
explicit datasheet state, saves one component and cannot create a runtime
voltage selector.

## `TPS564252DRLR` common energy profile

Every converter receives its own physical copies of the following parts:

| Function per converter | Exact physical part | Quantity |
|---|---|---:|
| bulk input | `Murata GRM32ER71E226KE15L`, 22 uF, 25 V, X7R, 1210 | 1 |
| HF input | `TDK C1005X7R1H104K050BB`, 100 nF, 50 V, X7R, 0402 | 1 |
| output bank | `Murata GRM32ER71E226KE15L`, 22 uF, 25 V, X7R, 1210 | 2 |
| feed-forward | `KEMET C0402C330J5GACTU`, 33 pF, 50 V, C0G, 0402 | 1 |

The common profile uses three bulk-input, three HF-input, six output and
three feed-forward physical instances. Reusing MPNs reduces setup/sourcing
cost while the rails remain electrically independent.

The datasheet asks for more than 10 uF nominal input plus close 0.1 uF HF
bypass. Its 3.3-V and 5-V table recommends 44 uF nominal output and a 30-pF
feed-forward capacitor; 33 pF remains inside the stated 10…100-pF high-output
range. The exact 25-V 1210 output part is more conservative under DC bias than
the datasheet example's 10-V 0805 capacitor.

Two selected 22-uF parts therefore provide 44 uF nominal per rail. Published
reference data for `GRM32ER71E226KE15L` show approximately 20% typical loss at
5 V, or about 35.2 uF combined before tolerance/temperature. For the accepted
inductors this gives the following paper screen:

| Rail | L | nominal LC pole at 44 uF | representative pole at 35.2 uF | Result |
|---|---:|---:|---:|---|
| `3V3_MAIN` | 3.3 uH | 13.21 kHz | 14.77 kHz | below the approximately 20-kHz design target |
| `VVOICE_4V` | 3.3 uH | 13.21 kHz | 14.77 kHz | below target; exact transient HIL remains |
| `5V_EXT_PREPROTECT` | 4.7 uH | 11.07 kHz | 12.37 kHz | below target before eFuse/load dynamics |

The DC-bias curves are typical, not guaranteed minima. Production acceptance
must measure effective capacitance and response on the assembled board; this
review does not turn a typical curve into a worst-case guarantee.

## Exact fixed dividers

`TPS564252` uses `VOUT = 0.6 × (1 + RTOP/RBOTTOM)`. All six divider parts are
1% 0402 Yageo resistors and remain separate physical instances.

| Rail | RTOP exact MPN | RBOTTOM exact MPN | Nominal output | Divider-only 1% range | Full paper range including 591…609-mV `VREF` |
|---|---|---|---:|---:|---:|
| `3V3_MAIN` | `RC0402FR-0745K3L`, 45.3 kOhm | `RC0402FR-0710KL`, 10 kOhm | 3.318 V | 3.264…3.373 V | 3.215…3.424 V |
| `VVOICE_4V` | `RC0402FR-0768KL`, 68 kOhm | `RC0402FR-0712KL`, 12 kOhm | 4.000 V | 3.933…4.069 V | 3.874…4.130 V |
| `5V_EXT_PREPROTECT` | `RC0402FR-07220KL`, 220 kOhm | `RC0402FR-0730KL`, 30 kOhm | 5.000 V | 4.913…5.089 V | 4.839…5.165 V |

The TI table's exact 45.0-kOhm Yageo candidate is obsolete. Active 45.3 kOhm
raises the main nominal by only 18 mV and keeps the full paper range inside the
accepted 3.3-V consumers' 3.0…3.6-V supply envelope.

The 5-V full paper maximum of 5.165 V remains below the eFuse OVLO paper floor
of approximately 5.336 V, leaving about 171 mV before the earliest cutoff.
The fixed 4-V divider remains physically incapable of selecting 5 V.

## Feed-forward placement

Each 33-pF C0G part is placed across the corresponding top feedback resistor,
not from FB to ground. Approximate feed-forward zeros are 106.5 kHz main,
70.9 kHz voice and 21.9 kHz external. Layout must keep FB and its Kelvin ground
away from SW copper.

## Availability and recurring cost

Exact-MPN selection was checked on 2026-08-18:

- TDK lists both `CGA5L1X7R1E475K160AC` and `C1005X7R1H104K050BB` as
  Production with multi-distributor stock;
- authorized distributors list `GRM31CR71A226KE15L` and
  `GRM32ER71E226KE15L` active with substantial stock;
- KEMET `C0402C330J5GACTU` is active with six-digit distributor stock;
- all selected Yageo divider/configuration values are active. Obsolete
  `RC0402FR-0745KL` is not admitted.

The 24 fitted physical instances add approximately **$1.8 per board** at the
checked 100-piece distributor snapshot; nine `GRM32ER71E226KE15L` capacitors
dominate. This is closure of passives omitted from the earlier `$3.43` active-
stage estimate, not a new function. A smaller 0805 output bank may be qualified
later only if the same DC-bias/transient/temperature envelope passes HIL.

Primary sources:

- [TI TPS629203 datasheet](https://www.ti.com/lit/ds/symlink/tps629203.pdf)
- [TI TPS564252 datasheet](https://www.ti.com/lit/ds/symlink/tps564252.pdf)
- [TDK CGA5L1X7R1E475K160AC product data](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA5L1X7R1E475K160AC)
- [TDK C1005X7R1H104K050BB product data](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1005X7R1H104K050BB)
- [KEMET C0402C330J5GACTU specification](https://search.kemet.com/download/specsheet/C0402C330J5GACTU)
- [Yageo RC component specifications](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0768KL)

## Review result

Exact AON configuration/energy parts and all three application-converter
input, output, feedback and feed-forward parts receive **«Проведено ревью»**
at the paper electrical-profile level. `PWR-0012/DEC-0073` later close
EN/PG/qualifier pulls; effective-capacitance measurement,
ripple/load-step/EMI and layout remain open. `PWR-0020/DEC-0081` separately
review post-buck protection loss and the raw/protected rail split; hot HIL
remains open.
