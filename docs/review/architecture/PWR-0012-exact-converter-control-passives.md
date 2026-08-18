# PWR-0012 — exact converter enable, power-good and fault pull profile

- Статус: **Проведено ревью бумажной принципиальной схемы**
- Дата: 2026-08-18
- Parent topology: [`PWR-0008`](PWR-0008-exact-downstream-rail-tree.md)
- PG qualifier: [`PWR-0009`](PWR-0009-enable-qualified-switched-rail-pg.md)
- Energy/feedback passives: [`PWR-0011`](PWR-0011-application-converter-passive-profile.md)
- Decision: [`DEC-0073`](../decisions/DEC-0073-exact-converter-control-passives.md)
- Propagation review: [`REV-0005AD`](../reviews/REV-0005AD-converter-control-passive-profile.md)
- Post-buck containment: [`PWR-0020`](PWR-0020-independent-post-buck-containment.md)

## Scope

Этот проход закрывает оставшиеся abstract EN/PG/power-fault resistor networks
четырёх принятых преобразователей. Он не меняет rail topology, напряжения,
runtime sequencing или accepted truth table `EN AND NOT(PG)`. The original
nine resistors are amended by `PWR-0019/DEC-0080` to ten separate
machine/diagram instances; AON EN receives an exact direct strap and the exact
AON-POR/main-EN pair replaces the hidden sequencer.
`PWR-0020/DEC-0081` later source AON PG/POR and main/voice runtime PG evidence
from the protected side of independent post-buck cutoffs; raw converter PG is
fixture-only.

Startup/shutdown timing, brownout, simultaneous faults and specimen HIL remain
open. Артефакт не разрешает начинать KiCad.

## Exact physical profile

| Physical function | Exact MPN | Qty | Connection |
|---|---|---:|---|
| AON PG pull-up | `Yageo RC0402FR-0747KL`, 47 kOhm, 1%, 0402 | 1 | `AON_SAFE_3V3 → TPS629203.PG` |
| AON POR pull-up | `Yageo RC0402FR-0710KL`, 10 kOhm, 1%, 0402 | 1 | `AON_SAFE_3V3 → TPS3808.RESET_N/POR_N` |
| main converter EN fail-low | `Yageo RC0402FR-07100KL`, 100 kOhm, 1%, 0402 | 1 | `POR_N / MAIN.EN → GND` |
| wired-low fault pull-up | `Yageo RC0402FR-0710KL` | 1 | `3V3_MAIN → POWER_FAULT_N` |
| voice converter EN fail-low | `Yageo RC0402FR-0710KL` | 1 | `VOICE_DOMAIN_EN_SAFE → GND` |
| voice PG pull-up | `Yageo RC0402FR-0710KL` | 1 | `3V3_MAIN → VOICE_4V_PG_N` |
| voice qualifier base | `Yageo RC0402FR-0768KL`, 68 kOhm, 1%, 0402 | 1 | safe EN → `MMBT3904.B` |
| accessory converter/eFuse EN fail-low | `Yageo RC0402FR-0710KL` | 1 | `EXT_5V_EN_SAFE → GND` |
| accessory PG pull-up | `Yageo RC0402FR-0710KL` | 1 | `3V3_MAIN → EXT_5V_PG_N` |
| accessory qualifier base | `Yageo RC0402FR-0768KL` | 1 | safe EN → `MMBT3904.B` |

Итого: six 10-kOhm, one 47-kOhm, two 68-kOhm and one 100-kOhm physical
resistors. All four MPNs already occur in the accepted BOM: 10/68 kOhm in
feedback/control networks, 47 kOhm in eFuse OVLO and 100 kOhm in the BQ25798
ILIM divider. Нового unique line item нет.

## AON enable and power-good

`TPS629203.EN` is tied directly to admitted `BQ25798.SYS`. TI permits EN up to
the converter input range, requires that it not float and shows direct VIN
enable in its reference circuits. The direct strap avoids a divider against
the unspecified dynamic internal fail-low resistor and saves one component.
There is no application-firmware shutdown path for the safety rail.

The AON PG pull-up is 47 kOhm rather than the common 10 kOhm. At 3.3 V it
draws approximately 70.2 uA when asserted, versus 330 uA for 10 kOhm. This is
below the TPS629203 1-mA recommended PG sink and preserves the low-IQ purpose
without adding a new MPN. The maximum specified 1-uA high-state leakage would
drop only 47 mV. The same exact node now drives `TPS3808.MR_N`; edge timing
remains a HIL gate.

## TPS564252 enable defaults

TI specifies a 2-MOhm internal EN pull-down, 1.25-V maximum rising threshold
and 1.10-V maximum falling threshold. Voice and accessory retain exact 10-kOhm
pull-downs on push-pull safe-gate outputs. Main is different: its open-drain
POR uses a 10-kOhm AON pull-up and a 100-kOhm fail-low pull-down, yielding
3.00 V nominal and about 2.79 V at the supervisor's minimum valid rail with
1% corners. Equal 10-kOhm values would have yielded only 1.65 V and are no
longer accepted. A 3.3-V asserted optional safe-gate output still sources about
0.33 mA per 10-kOhm pull-down; with one qualifier base branch and eFuse EN
leakage it remains below approximately 0.4 mA static load.

Accessory `EXT_5V_EN_SAFE` drives the fixed 5-V converter and
`TPS259470LRPWR.EN/UVLO` together. The 3.3-V high is above both devices'
maximum enable thresholds and below their recommended pin-voltage ceilings;
the 10-kOhm low reaches true eFuse shutdown rather than merely UVLO.

## PG qualifier and aggregate arithmetic

Each TPS564252 PG gets an independent 10-kOhm pull-up to `3V3_MAIN`.
Using the datasheet worst-case `VPG(OL)=0.4 V`, its pull-up contributes about
290 uA. In the only fault state, `EN=3.3 V`, `PG=0.4 V` and conservative
`VBE=0.85 V` leave about 30.1 uA through 68 kOhm. Total PG sink is therefore
about 0.320 mA, less than one tenth of the specified 4-mA test current.

The shared `POWER_FAULT_N` 10-kOhm pull-up asks an asserting source to sink at
most 0.33 mA. The NPN forced beta is approximately 11, retaining the margin
already reviewed in `PWR-0009`. Main PG, either qualifier collector and eFuse
FLT therefore share one, not several competing, pull-ups.

The existing `EN=0, PG=1` transient can reverse-bias the MMBT3904 base-emitter
junction up to 3.3 V, below its 6-V absolute limit. Repeated shutdown,
brownout and another-source-low combinations remain explicit HIL because an
absolute limit is not a lifetime qualification.

## Availability and cost

The selected exact Yageo parts are active/current and stocked. The checked
LCSC 100+ material class remains below one cent per board for all ten
resistors. Because all four MPNs already occur elsewhere on the board, this
closure adds placements but no feeder/unique-part line.

Primary sources:

- [TI TPS629203 datasheet](https://www.ti.com/lit/ds/symlink/tps629203.pdf)
- [TI TPS564252 datasheet](https://www.ti.com/lit/ds/symlink/tps564252.pdf)
- [TI TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
- [Diodes MMBT3904 product page](https://www.diodes.com/part/view/MMBT3904)
- [Yageo RC0402FR-0768KL specification](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0768KL)
- [LCSC RC0402FR-0710KL](https://www.lcsc.com/product-detail/C60490.html)
- [LCSC RC0402FR-0747KL](https://www.lcsc.com/product-detail/C93943.html)
- [LCSC RC0402FR-0768KL](https://www.lcsc.com/product-detail/C137947.html)

## Review result

Exact AON EN/PG/POR, three application-converter EN defaults, both qualifier base
branches, both optional PG pull-ups and the common fault pull-up receive
**«Проведено ревью»** at paper schematic level. Dynamic timing, temperature,
brownout, reverse-BE cycling, multi-fault and HIL remain open. The later
protected-side evidence amendment is reviewed in `PWR-0020/REV-0005AL`.
