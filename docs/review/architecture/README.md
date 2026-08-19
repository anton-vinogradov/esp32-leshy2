# Product and architecture workspace

- Статус: **G2F logical/electrical feasibility active; architecture reopened**
- Correction: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Sequencing refinement: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Integrated-mockup pause: [`DEC-0058`](../decisions/DEC-0058-internals-before-integrated-mockup.md)
- Method: [`FLOW-0001`](FLOW-0001-product-to-cad-gates.md)

## Canonical active chain

1. Reviewed intent/capability inputs from stages 1–2.
2. Logical/electrical feasibility: neutral semantic demand, real-device pin
   provenance and at least two complete owner/bus/GPIO candidates.
3. Owner-selected working electrical baseline, explicitly provisional.
4. Dependency-ordered internal closure through [`INT-0001`](INT-0001-internal-design-closure-sequence.md):
   compute/service, safety, power, UI/storage, audio, RF and expansion evidence.
5. Resume target physical/product mockup only after the joint internal paper
   review; any packing/RF/power conflict loops back visibly.
6. Whole-device optimality, conceptual co-design and owner decision.
7. Atomic architecture only after all prior gates pass.
8. Final components, electrical CAD, schematic and PCB afterwards.

The current active artifacts are `DEM-0001`, `SRC-0002`, `DSP-0001/0002`,
`CTL-0001`, [`NIF-0001`](NIF-0001-digital-noninterference-layout.md),
[`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md) and the generated
`G2F-pin-ledger` plus focused
[`G2F-3I principled pinout`](generated/G2F-3I-principled-pinout.md).
`PIN-0003/REV-0004V` review the exact owner/contact projection;
`DEC-0052/REV-0004X` then allocate S3 GPIO41/42 to direct-QSPI D2/D3 and record
the then-current `S3=2, C5=1, RP=0, slow=P27` free-contact state. Subsequent
`AUDIO-0002/FND-0067` uses P27 for the omitted RX-audio source selector;
`DEC-0054/REV-0005D` then assigns S3 GPIO6 to reset-safe `AUDIO_ARM`. After
`DEC-0059`, GPIO47 was the only free S3 contact. `DEC-0086/UI-0001` now use
GPIO39/GPIO47 for direct encoder PCNT0 capture and move touch IRQ into shared
GPIO37. `DEC-0088/DSP-0007` fix exact active-low ST77922, 10-kOhm raw pull-up
and non-inverting 1G07. A dedicated TCA9534A restores
interrupt-driven 4×3 controls and releases TCA6424 P00…P05. I5 now assigns
P00/P01/P02 to capture selection, speaker enable and headphone sensing; I6
assigns P03/P04 to powered-off CC1101 band selection. `DEC-0098/EXP-0001` then
uses P05 for independent native-M5-Unit power. Current free state is
`S3=0, C5=1, RP=0, main slow=0`; UI-matrix P7 remains reserved.
`DEC-0051` publishes that reviewed projection as the visible principle-level
working design in the root target document; it remains reopenable and is not
the G7 atomic architecture.
`DEC-0044/REV-0004L` make `G2F-3I` the leading reviewed paper
map under a digital no-neighbour-stall invariant. `FND-0053/REV-0004M` prove
that arbitrary cross-group co-located same-band TX↔RX cannot be promised;
`DEC-0045` selects one active group, while `SG-N24` explicitly requires every
simultaneous three-radio PTX/PRX mix. `DEC-0047` selects a qualified RF envelope.
`N24H-0001` separates ordered `L0 DIV↔DIV` pre-HIL from target `T1`, while
`N24M-0001/IMP-0040/DEC-0048` select three compact IPEX→external-SMA nRF paths
and external SMA for every onboard antenna endpoint; exact production lots,
feeds and measurements remain open.
`DEC-0046/QST-0001` require unused interfaces to
enter verified quiet states. It is not yet target: exact RF paths, power gates,
peripherals and HIL remain open; CAD stays blocked.
`AUDIO-0001/REV-0005B` close the exact ES8311 QFN-20 digital/contact fit:
S3 GPIO1/2/15/16/17/18 land on real I2C/I2S contacts, `CE` is address strap
`0x19`, and P10 is external `CODEC_PWR_EN`. `AUDIO-0002/REV-0005C` compare the
complete capture/playback/TX/reset path, add exact TAC5111IRGER reference
contacts and expose `FND-0067`; `DEC-0054` accepts the active-buffer ES8311
prototype plus direct arm and exact selector/gate/amp ICs. `FND-0095/
AUDIO-0003/DEC-0090/REV-0005AU` now close the dependent I5 paper block with
exact power/interface isolation, analog passives, address/clock handling and
physical microphone/speaker/headphone endpoints. I5 has **«Проведено ревью»**;
acoustic/RF/specimen HIL stays explicit. I6 later receives paper review by
`DEC-0097/COX-0001/REV-0005BC`; I7 is reviewed by `DEC-0098/0099`, and I8 is
now active.
`DEC-0058` now pauses the integrated mockup until the internal chain is jointly
reviewed. `INT-0001/I1` has **Проведено ревью** through
`DEC-0059/REV-0005L`: 1-bit C5 SDIO restores S3 UART0 and C5 native USB,
while M5 Unit UART moves to UART1 on the same pins. `DEC-0061/SAFE-0002/
REV-0005O` now give `I2` **Проведено ревью**: exact AON latch/reset/gate
devices cover S3+C5+RP and every external TX request, while seven RF detectors,
optical IR evidence, local-I²C source mask and direct physical aggregate are
machine-projected. `DEC-0082/PWR-0021/REV-0005AM` now give I3 paper electrical
scope **«Проведено ревью»** and make I4 the active paper block; named
procurement and prototype HIL evidence remains open.
`DEC-0083/USB-0001/REV-0005AN` then close the first I4 endpoint: exact JAE
USB-C and TI four-line protection replace the abstract port, corrected 220-pF
CC shunts preserve capacitance margin, and that endpoint leaves GPIO47 free. Physical
port/SI/ESD HIL stays open while I4 proceeds.
`FND-0088/DSP-0006/DEC-0084/REV-0005AO` then close the display paper
electrical endpoint: exact first ZIF candidate, protected-main logic supply,
reset-low defaults and a separately latch-protected PWM backlight replace the
three former abstractions. Real-tail mate/orientation, panel procurement and
electrical/thermal HIL remain open; no KiCad or physical freeze is implied.
`FND-0089/STO-0001/DEC-0085/REV-0005AP` then close the microSD paper
electrical endpoint. Exact card-side Ioff buffers, CS-gated DAT0 return,
mandatory switched pulls, all exposed-contact/detect ESD, reset defaults and
SPI-mode-first sequencing preserve the shared S3 allocation without a new
GPIO. Socket placement/access, real media, throughput and fault HIL stay open.
`FND-0090/UI-0001/DEC-0086/REV-0005AQ` then restore the complete local-control
inventory and close its principled pin fit: 4x3 ordinary matrix, direct PCNT0
encoder, direct RP PTT and independent AON STOP/RE-ARM.
`FND-0092/UI-0002/DEC-0087/REV-0005AR` close the next electrical boundary with
exact low-current switches, a gold-clad COM+NC STOP target, exact pull/filter
networks and separate matrix/fast/safety ESD returns. Cap/guard/harness and
enclosure mechanics and control HIL remain open.
`FND-0093/DSP-0007/DEC-0088/REV-0005AS` then close the exact integrated touch
identity/address/polarity endpoint: ST77922 is the assembly TDDI at `0x38`,
active-low TP_INT has its own 10-kOhm raw pull-up and fixed 1G07 path to shared
GPIO37, and the former inverter option is removed. Specimen IRQ/reset,
shared-source and physical HIL remain open.
`FND-0094/IOX-0001/DEC-0089/REV-0005AT` then complete the consolidated I4
audit. Exact TCA6424A power/address/reset/interrupt, AON-to-main observation
isolation, pack target `0x2A`, real GPIO4 microSD return, direct USB-shell
ground bond and exact STOP LED resistor are machine-projected. I4 paper
electrical scope has **«Проведено ревью»**; I5 follows as reviewed above, while prototype,
physical and procurement evidence stays open and KiCad remains unauthorized.
`PWR-0002/REV-0005P` review its current load/scenario prerequisites and reject
the legacy sheet as a target: its charger lacks a system power path, its ADC
is not a fuel gauge, fixed 3-A Type-C draw is unproven and its rails do not fit
the accepted AON/voice/current envelope. The owner accepted `IMP-0052/B` as
`DEC-0062`: the two 18650 slots remain individually replaceable, and admission
is fail-closed rather than accepting arbitrary loose cells. `DEC-0064` then
reopened the electrical series/controlled-1S arrangement for comparison, and
`DEC-0065/REV-0005T` confirm supervised 2S for the base product.
`PWR-0003/IMP-0053` are closed by `DEC-0063`: the owner selected sink-only
USB-PD up to 30 W. `PWR-0004/REV-0005R` review exact TPS25751DREFR,
BQ25798RQMR, CAT24C512WI-GT3 and TVS2200DRVR fit while leaving the cell manager,
rail tree, passives and HIL active in I3. `PWR-0005/FND-0075` separate ordinary
pack gauging from fail-closed loose-cell admission; `DEC-0066/REV-0005V`
accept exact MAX17320G20+T plus MSPM0C1104SDGS20R and project both physical
devices separately. `PWR-0006/FND-0076` retain the
controlled two-slot 1S and one-slot 1S alternatives as future-SKU comparison
evidence. `PWR-0007/FND-0077/REV-0005W` review the exact 2S tap rules, reset
hold, admission-supply isolation, two-ADC evidence and common-path losses.
`DEC-0067/REV-0005X` close the exposed recovery gate with no in-device
deep-cell recovery and accept the exact active switching FET, fuses, shunt,
NTCs, hold and supply-isolation packages. `PWR-0008/DEC-0068/REV-0005Y`
then review the independent fixed AON/3.3/4.0/5.0-V rail tree, exact
TPS629203/TPS564252 inductors, five TPS22919 branches and reverse-blocking
TPS259470L latch-off external boundary after `DEC-0069/REV-0005Z`.
`PWR-0009/DEC-0070/REV-0005AA` add two exact `MMBT3904-7-F` qualifiers so
disabled optional rails release `POWER_FAULT_N`, while EN-high PG loss remains
hardware-visible. `PWR-0010/DEC-0071/REV-0005AB` correct the earlier startup
claim: the 1.509-A eFuse limit is immediately active, 4.7 nF controls startup
slew and 220 nF admits only a bounded post-start 2-A transient. Exact OVLO,
local bypass and output bleed are now eight physical MPN-bearing instances in
the machine source and living diagrams. `PWR-0011/DEC-0072/REV-0005AC` then
replace the four converters' abstract networks with 24 exact physical
configuration, input, output, fixed-feedback and feed-forward passives. Their
fixed tolerance ranges remain compatible with the loads and eFuse OVLO, and
the obsolete 45.0-kOhm candidate is rejected for the active 45.3-kOhm MPN.
`PWR-0012/DEC-0073/REV-0005AD` first close direct AON enable plus nine exact
EN/PG/fault resistors using only existing BOM MPNs. `FND-0084/PWR-0019/
DEC-0080/REV-0005AK` later expose and remove the hidden source-sequencer
endpoint: AON PG directly holds TPS3808 MR, delayed POR directly enables main,
and an exact 10-kOhm/100-kOhm pair gives 3.0-V nominal release. The amended
control profile has ten physical resistor positions and no new unique MPN.
`FND-0085/PWR-0020/DEC-0081/REV-0005AL` then correct the remaining internal
single-fault gap with exact independent AON/main/voice post-buck cutoffs,
protected-side PG, threshold/loss calculations and a reviewed fault matrix;
no GPIO or function is lost.
`FND-0086/PWR-0021/DEC-0082/REV-0005AM` consolidate every I3 paper obligation,
heat source, fault and physical residue. I3 is paper-reviewed with all
prototype/lot/I8 evidence still explicit; this activates the dependent I4
paper block at that point in the chain.
`FND-0087/USB-0001/DEC-0083/REV-0005AN` now give exact protected product USB
the first I4 paper-endpoint review without promoting placement or HIL.
`FND-0088/DSP-0006/DEC-0084/REV-0005AO` give the second I4 endpoint a paper
review while explicitly rejecting a back-power-prone whole-panel switch and
keeping the connector footprint blocked on a real FPC-tail proof.
`FND-0089/STO-0001/DEC-0085/REV-0005AP` give the third I4 endpoint a paper
review, eliminate storage back-power and display-D1 contention, and keep the
socket footprint, media/endurance, throughput and destructive HIL blocked.
`FND-0090…0093/UI-0001/UI-0002/DSP-0007/DEC-0086…0088` retain every physical
control, close exact switch/protection and touch identity/address/polarity,
and leave only named mechanics/specimen HIL before the consolidated I4 audit.
`FND-0094/IOX-0001/DEC-0089/REV-0005AT` close that consolidated audit, correct
the shared-interface residues and advance the dependency chain to I5 without
claiming layout or HIL evidence.
`FND-0095/AUDIO-0003/DEC-0090/REV-0005AU` close that I5 paper block and
advance the dependency chain to active I6 without claiming acoustic, RF,
layout or HIL evidence.
`FND-0096/N24E-0001/DEC-0091/REV-0005AV` close the first I6 paper subblock:
three full-function nRF paths gain exact powered-off digital isolation,
local energy and directional 2400–2525-MHz actual-TX evidence. The unproven
Ebyte RF mate, thresholds, T1 fixture and every other I6 RF endpoint remain
open, so I6 and the no-KiCad boundary are unchanged.
`FND-0097/NAT-0001/DEC-0092/REV-0005AW` then close the native-radio paper
subblock: exact S3 2.4-GHz and C5 2.4/5-GHz external contacts now lead through
separate real U.FL mates and dual-band directional couplers into complete
LTC5532 evidence circuits. C5 ANT2 is explicitly default-disabled/no-connect;
jumper length, chassis RP-SMA, thresholds and whole-feed HIL remain physical
gates. `FND-0098/CCRF-0001/DEC-0093/REV-0005AX` next close the CC1101 paper
subblock: two equal-control SP3T bodies isolate all three branches at both ends,
P03/P04 select 315/433/868–915 only while power is off, exact crystal/balun/
passives/ESD are physical and a final-line AD8314 sample replaces the abstract
evidence tap. Conducted tuning, sensitivity/output/spurious/legal-profile,
SMA mechanics and coexistence HIL remain open; I6 and no-KiCad boundary stay
active for the remaining RF endpoints. `FND-0099/VRF-0001/DEC-0094/
REV-0005AY` then close the SA518 RF paper subblock: physical ANT contact 7
feeds a direct protected 50-Ohm SMA boundary, exact 24-V low-C ESD and an
AD8314 5.1-kOhm/52.3-Ohm actual-TX sample. The lower-voltage CC TVS is not
reused, no unproven filter bank spends P05, and a measured conducted failure
explicitly reopens that choice. Voice RF HIL remains open; I6 continues with
IR and consolidated coexistence under the same no-KiCad boundary.
`FND-0100/IRF-0001/DEC-0095/REV-0005AZ` then close the IR paper endpoint.
Exact top-view SMD `TSOP95238TT` and `TSMP95000TT` retain robust
demodulation plus measured 30-60-kHz carrier learning behind one discharged
receive rail and Ioff return buffer. Exact `VSMY14940`, 33-Ohm limit,
`DMN2056U-7` and the existing STOP gate close TX; shielded `VEMD1060X01` plus
AON `TLV9061IDBVR` verify physical light rather than current. Pin budgets do
not change. `FND-0101/RXF-0001/DEC-0096/REV-0005BA` subsequently catch the
still-abstract Si4732 FMI/AMI endpoints and add separate protected FM/SW and
non-50-Ohm AM/LW first-target circuits. `FND-0102/REV-0005BB` then correct the
entire shifted SOIC-16 machine contact map from the visually inspected
manufacturer package drawing and lock all 16 contacts. Optical/thermal/IEC and consolidated
coexistence HIL remain open. `FND-0103/FND-0104/COX-0001/DEC-0097/
REV-0005BC` then remove the stale cross-group-promotion path, split receiver,
codec/audio and voice quiet contracts and freeze one consolidated matrix for
all groups, legal intragroup modes, ordered transitions, eight fixture classes,
actual-TX evidence and no-stall thresholds. I6 has **«Проведено ревью»** for
paper electrical and qualification scope; physical HIL remains explicitly
not executed and can reopen its owner. I7 subsequently closes below and the
no-KiCad boundary continues through active I8.
`FND-0105/EXP-0001/DEC-0098/REV-0005BD` close the I7 M5 expansion paper
subblock. U214 and the native HY2.0-4P Unit port now have independent
true-reverse-blocking 5-V branches, branch-valid supervisors, exact signal
isolation and connector ESD. The fictitious accessory-presence input is removed;
P26 reports real Unit-rail readiness. Connector MPNs and all physical/hot-plug/
reverse-source/profile/coexistence evidence remain open.
`FND-0106…0108/SVC-0002/DEC-0099/REV-0005BE` then close the remaining I7
service/recovery paper circuit: separate data-only C5/RP USB ports now block
VBUS and D-line backfeed, three keyed DBG10 and six controls are exact, and
passive-drain reset sinks remove push-pull contention. I7 has **«Проведено
ревью»**; I8 is active and the no-KiCad boundary continues.
`FND-0109/BOM-0008` then generate the first complete I8 coverage view.
`PWR-0022/DEC-0100/REV-0005BF` repair and re-review the exposed MAX17320/MSPM0
support residue without changing the accepted 2S product topology. The current
map has 858 architecture instances; `FND-0112/BOM-0011/DEC-0103/REV-0005BJ`
exclude the one assembly-internal ST77922 evidence node, leaving 857
supplied/costed placements / 187 purchase MPN lines plus four explicit SMA, cable, M5
and antenna-kit gap families. `FND-0110/SAFE-0003/DEC-0101/REV-0005BG`
subsequently instantiate every actual-TX threshold network and repair the
AON-to-main evidence boundary. I8 inventory coverage is reviewed;
orderability, cost and alternate qualification remain active.
`FND-0113/REV-0005BP` then repair the product-site projection itself: a bounded
vertical overview renders on GitHub, while the exhaustive one-device-per-node
source and pin/net tables stay machine-derived. No architecture content changes;
I8 remains active and KiCad remains unauthorized.
`FND-0111/BOM-0009/DEC-0102/REV-0005BH` subsequently recheck all 33 missing
source lines, replace the RP prose pseudo-MPN with exact `SC1512-A4`
(`RP2354B0A4`) and, after the internal-node correction, leave current
orderability coverage at 186/187. Exact
standalone `HMX035CTFT-001` sourcing is the sole used-line residue; cost and
the four physical-gap families remain open. `DSP-0008/BOM-0010/REV-0005BI` then prove current complete-board
specimen access, define the exact standalone-panel RFQ and record the first
no-drop-in disposition without changing the display endpoint.
`BOM-0012/DEC-0104/REV-0005BK` subsequently classify all 187 purchase lines:
policy coverage is complete without pretending that specific second-source
MPNs are already qualified.
`BOM-0013…0021/DEC-0105…0106/REV-0005BL…BU` then validate the cost-evidence
contract, explicit RFQ/retail gaps and first 118/187 prices covering 771
placements. Their USD 142.1808 base-product subtotal is deliberately partial;
69 prices and full factory COGS remain open.
`PWR-0013/DEC-0074/REV-0005AE` then close the exact 10-Ohm pre-admission
load, independent non-retriggerable timer, 28.7-40.7-ms C0G paper window,
25-50-ms production acceptance and both divider/filter frontends. `FND-0078`
corrects the old PA24 battery-divider assignment to real
PA25/PA26 contacts without changing the `12/3/3` budget.
`PWR-0014/DEC-0075/REV-0005AF` then close the exact BQ25798 2S/750-kHz
strap, 2.2-uH/7-A inductor, all physical energy banks, BATP/TS/ILIM, local-bus
pulls, reset-high CE and special-pin terminations. `FND-0079` corrects product
USB-C/USB2 protection back to I4 and exposes TPS25751/CAT24C512 support
passives as the next true I3 paper dependency.
`FND-0080/PWR-0015/DEC-0076/REV-0005AG` then correct separate TPS
VBUS/VBUS_IN startup, hardware SafeMode,
17 exact support components and both complete I2C pull networks.
`FND-0082/PWR-0017/DEC-0078/REV-0005AI` then correct the physical TPUL WQFN
map, reuse its second channel for a `>=350 ms` hardware refractory lockout and
replace the single load with two parallel 20-Ohm/2-W branches. Exact-cell
selection is then closed at paper level by `FND-0083/PWR-0018/DEC-0079/
REV-0005AJ`: two exact `XTAR 18650 4000mAh` protected button-top instances
provide `28.8 Wh`, a 10-A discharge class and a 2-A standard-charge ceiling.
Assembly-matching certification evidence, droop distributions, mechanical
continuity/thermal coupling, calculated hot loss and HIL remain active.

## Active G2F artifacts

- [`INT-0001`](INT-0001-internal-design-closure-sequence.md) defines the
  dependency-ordered `I0…I9` paper/electrical closure required before the
  integrated physical mockup resumes;
- [`SAFE-0001`](SAFE-0001-aon-stop-and-tx-evidence-options.md) reviews the `I2`
  options; [`SAFE-0002`](SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)
  records the accepted exact fan-out, pulls, fault matrix, eight evidence
  channels and test points. `FND-0071` paper mismatch is closed; I3/I6/HIL
  measured proof remains explicit;
- [`SAFE-0003`](SAFE-0003-exact-actual-tx-threshold-and-isolation.md)
  instantiates all eight comparator threshold/hysteresis networks, completes
  comparator/source-mask support and isolates three AON evidence signals from
  main-domain inputs; paper electrical scope reviewed, calibration/HIL open;
- [`PWR-0002`](PWR-0002-i3-power-prerequisite-audit.md) re-derives the `I3`
  loads/scenarios and rejects the old source as a target;
- [`PWR-0003`](PWR-0003-charge-power-path-options.md) compares the complete
  5-V Type-C/NVDC and USB-PD/buck-boost paths; B is accepted by `DEC-0063`;
- [`PWR-0004`](PWR-0004-accepted-usb-pd-front-end.md) verifies the exact
  sink-only 30-W PD/charger/configuration/protection path and sourcing snapshot;
- [`PWR-0005`](PWR-0005-replaceable-2s-manager-options.md) reviews exact
  gauge/admission candidates and reset-default behavior; option A is accepted
  by `DEC-0066`;
- [`PWR-0006`](PWR-0006-one-or-two-cell-topology-comparison.md) reviews the
  reopened topology, rails, losses, one-cell behavior and cost; supervised 2S
  is accepted by `DEC-0065`;
- [`PWR-0007`](PWR-0007-max17320-2s-surrounding-circuit.md) verifies the 2S
  sensing/shorting rules, current/loss screen, per-slot fuse/NTC candidates,
  shunt, reset hold, supply handover and real ADC budget; `DEC-0067` accepts
  no in-device recovery and the exact active common-drain power FET;
- [`PWR-0008`](PWR-0008-exact-downstream-rail-tree.md) verifies independent
  fixed rails, exact converter/inductor/load-switch/eFuse contacts, current
  headroom, availability, sequencing and the updated cost screen;
- [`PWR-0010`](PWR-0010-external-efuse-passive-profile.md) closes the first
  exact eFuse `RILM/dVdt/ITIMER/OVLO`, local-capacitor and discharge profile,
  and separates controlled startup from the bounded 2-A post-start interval;
- [`PWR-0011`](PWR-0011-application-converter-passive-profile.md) closes the
  exact AON and three TPS564252 energy/configuration/feedback profiles as 24
  separate physical parts, including lifecycle, tolerance and DC-bias screens;
- [`PWR-0012`](PWR-0012-exact-converter-control-passives.md) closes direct
  AON enable and, after the DEC-0080 amendment, ten exact converter/POR
  EN/PG/fault resistors without adding a GPIO or unique BOM MPN;
- [`PWR-0013`](PWR-0013-exact-pack-diagnostic-frontends.md) is retained as the
  historical first diagnostic pass and is explicitly superseded by PWR-0017;
- [`PWR-0014`](PWR-0014-exact-bq25798-passive-profile.md) closes the exact
  BQ25798 2S/750-kHz energy, current/temperature sensing, reset and special-pin
  profile while leaving placement/thermal/source-transition HIL explicit;
- [`PWR-0015`](PWR-0015-exact-tps25751-eeprom-support-profile.md) closes the
  exact TPS25751D/CAT24 autonomous SafeMode startup, 17 support components,
  unused contacts and complete local/host pull networks;
- [`PWR-0016`](PWR-0016-keystone-1048p-holder-and-ntc-coupling.md) closes the
  exact polarized holder and three physical cell-temperature contact roles;
- [`PWR-0017`](PWR-0017-hardware-diagnostic-refractory-lockout.md) closes the
  corrected TPUL contacts, cascaded hardware cooldown, hot repetition bound
  and two-branch pulse-rated load while leaving exact-cell droop numbers HIL;
- [`PWR-0018`](PWR-0018-xtar-18650-4000mah-cell-profile.md) selects two exact
  XTAR protected 4-Ah cells as the first qualification target and records the
  certification/specimen gates;
- [`PWR-0019`](PWR-0019-exact-source-sequence-and-power-reserve.md) replaces
  the abstract source sequencer with the exact AON-PG/POR/main path and freezes
  a conservative system-first USB/charge power rule;
- [`PWR-0020`](PWR-0020-independent-post-buck-containment.md) separates all
  internal raw buck outputs from their loads with exact independent cutoffs,
  protected PG and reviewed threshold/loss/single-fault behavior;
- [`PWR-0021`](PWR-0021-i3-consolidated-paper-closure.md) audits the complete
  I3 dependency, heat/fault ledger and remaining evidence, allowing I4 paper
  work without claiming prototype qualification;
- [`PWR-0022`](PWR-0022-exact-max17320-2s-support-profile.md) repairs the exact
  MAX17320 2S support, status translation, shunt force path and MSPM0 support;
  **Проведено ревью paper electrical scope**, physical/HIL open;
- [`USB-0001`](USB-0001-exact-product-usb-c-and-protection.md) closes the first
  I4 endpoint with exact JAE USB-C, four-line TI CC/USB2 protection, corrected
  220-pF CC shunts and complete real-contact routing while retaining HIL;
- [`STO-0001`](STO-0001-exact-isolated-microsd-endpoint.md) closes the third
  I4 endpoint with exact switched power, partial-power isolation, pull/damping,
  complete socket ESD and always-readable detect while retaining physical and
  media HIL;
- [`UI-0002`](UI-0002-exact-switch-and-control-protection.md) closes exact
  contact-current, default-state and ESD routes for every retained physical
  control while keeping actuator/enclosure HIL open;
- [`DSP-0007`](DSP-0007-exact-integrated-st77922-touch-endpoint.md) names the
  integrated ST77922, exact `0x38`/active-low contract and fixed board IRQ
  normalizer while retaining specimen/shared-line HIL;
- [`IOX-0001`](IOX-0001-consolidated-i4-electrical-closure.md) audits all I4
  endpoints together, closes the exact main slow-I/O core and cross-domain
  routes, and classifies every remaining item as HIL, physical, I5…I8 or CAD;
- [`AUDIO-0003`](AUDIO-0003-exact-audio-and-receiver-endpoint.md) closes I5
  with exact codec/receiver/voice power and isolation, complete analog paths,
  exact acoustic endpoints and separately named HIL residue;
- [`DEM-0001`](DEM-0001-current-semantic-signal-demand.md) reconstructs current
  signal demand without inheriting an owner;
- [`SRC-0002`](SRC-0002-real-device-pin-provenance.md) requires the full
  SoC/package/module/carrier chain and records the first verified candidates;
- [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md) records which
  geometry/checks from the old drawing generator will be reused after pin review;
- [`REV-0003X`](../reviews/REV-0003X-electrical-feasibility-entry.md) reviews the
  sequencing correction and these inputs.
- [`DEC-0042`](../decisions/DEC-0042-single-source-architecture-data.md) accepts
  one machine-readable device/net source; [`G2F-pin-ledger`](generated/G2F-pin-ledger.md)
  renders three structurally checked maps including leading `G2F-3I`;
- [`PIN-0003`](PIN-0003-g2f-3i-principled-pinout.md) and the generated
  [`pinout atlas`](generated/G2F-3I-principled-pinout.md) provide the requested
  principled owner/net/pad diagram and exact tables. `FND-0059` fixes stale
  pre-quiet-state budgets; `FND-0060` exposes every still-abstract electrical
  endpoint instead of presenting it as a finished schematic;
- [`REV-0005K`](../reviews/REV-0005K-vertical-living-principled-diagram.md)
  makes that diagram a narrow top-to-bottom living projection. Every accepted
  internals change must update both target README diagrams and the generated
  atlas in the same commit; regression checks current candidate MPN coverage;
- [`REV-0003Y`](../reviews/REV-0003Y-single-source-and-draft-pin-maps.md) reviews
  the generator foundation and explicitly leaves complete-candidate review open.
- [`DSP-0001`](DSP-0001-display-storage-real-device-evidence.md) replaces the
  inherited full-frame target with the accepted task/dirty-region contract;
- [`DSP-0002`](DSP-0002-fast-display-path-options.md) finds that display+SD is
  the only deliberately shared high-rate pair, exposes the stale U214-derived
  `256 B` quantum as `FND-0061`, and reviews direct S3 QSPI, EVE and fourth-MCU
  paths. `IMP-0044/A` is accepted by `DEC-0052`; the machine map now assigns
  S3 GPIO41/42 to QSPI D2/D3 and uses measured `<=1 ms` display occupancy;
- [`DSP-0003`](DSP-0003-exact-fast-display-shortlist.md) shows that the old
  4-inch ST7796S remains a valid A0 workload fixture but not a QSPI target.
  `DEC-0053` accepts the new 3.5-inch portrait `320×480` QSPI IPS+touch class;
  [`DSP-0004`](DSP-0004-display-part-number-register.md) lists every known
  display identifier and every production `TBD` without freezing a dev board;
- [`CTL-0001`](CTL-0001-slow-control-and-external-i2c-boundary.md) proves that
  current validation closes MCU accounting only, derives the open slow-control
  envelope and records the required external-I²C fault boundary;
- [`DEC-0044`](../decisions/DEC-0044-delegated-noninterference-layout.md) accepts
  the 24-endpoint/separated-I²C invariant and delegates layout search;
  [`NIF-0001`](NIF-0001-digital-noninterference-layout.md) records the selected
  paper arrangement and rejected bandwidth/controller variants.
- [`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md) applies real
  shared-chain/range/power facts to `G2F-3I`; [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
  separates impossible arbitrary cross-group TX↔RX concurrency from mandatory
  three-nRF full-function concurrency,
  and [`IMP-0038`](../improvements/IMP-0038-visible-qualified-rf-arbiter.md)
  records the accepted group arbiter. [`FND-0054`](../findings/FND-0054-three-nrf-mix-needs-rf-acceptance.md)
  and [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md)
  derive the physical acceptance envelope for all nRF PTX/PRX mixes;
- [`DEC-0047`](../decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md)
  accepts the qualified-envelope option; [`N24H-0001`](N24H-0001-two-device-full-mix-fixture.md)
  uses the two ESP32-DIV units as `L0` pre-HIL and requires separate target
  `T1` DUT/observer evidence for production acceptance;
- [`QST-0001`](QST-0001-unused-interface-quiet-states.md) propagates
  [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md) into
  per-interface power-down, clock-parking and EMI proof contracts.
- [`ANT-0001`](ANT-0001-external-sma-path-inventory.md) reviews every onboard
  antenna endpoint against exact device pins. It finds two Si4732 input
  domains and rejects the legacy one-generic-port assumption;
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
  accepts nine labelled SMA with separate `RX-FM/SW` and `RX-AM/LW` paths.
- [`RFH-0001`](RFH-0001-module-to-external-sma-interface-review.md) separates
  five module-origin feeds from four PCB/frontend-origin feeds. It verifies
  first-generation U.FL/MHF I/AMC compatibility for S3/C5, records Ebyte
  `IPX` as unproven `FND-0057`, and opens external gender choice `IMP-0042`.
- [`RFH-0002`](RFH-0002-antenna-connector-ecosystem-review.md) checks actual
  antenna ecosystems instead of grouping only by frequency. It finds RP-SMA
  typical for native Wi-Fi, standard SMA in Ebyte's nRF ecosystem and both
  polarities in sub-GHz; `DEC-0050/REV-0004T` accept bounded
  `2 RP-SMA + 7 standard SMA` and made exact antenna sourcing the next gate.
- [`ANT-0002`](ANT-0002-current-orderable-antenna-shortlist.md) reviews exact
  current commercial candidates. It finds safe SKU sharing for S3/C5 and the
  three nRF paths, a combined 868/915 candidate, but no honest universal
  315–915 or full VHF/UHF radiator. `DEC-0055/REV-0005E` accept the profiled
  external kit and exact-MPN availability gate. `FND-0058` keeps production
  two-source and assembled-HIL qualification open; `MFG-0001/IMP-0047` cover
  one-stop PCBA plus loose-antenna kitting without yet constraining supplier.
- [`DSP-0002/REV-0004W`](DSP-0002-fast-display-path-options.md) review the
  display acceleration gate against the exact current pin budget. Direct QSPI
  fits with `GPIO41/42`; current RP/C5 display ownership and direct I80/RGB do
  not. `DEC-0052/REV-0004X` accept and propagate this path;
  `DEC-0053/REV-0004Z` accept the 3.5-inch display class while exact production
  assembly, optics and HIL remain open in `DSP-0004`.
- [`AUDIO-0001`](AUDIO-0001-es8311-exact-electrical-fit.md) records every
  ES8311 QFN-20 contact, proves the unchanged digital pin budget and corrects
  `CE` versus external power enable. [`AUDIO-0002`](AUDIO-0002-complete-audio-path-comparison.md)
  compares the whole fail-safe path; [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)
  is accepted as [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md)
  with propagation reviewed by `REV-0005D`.

## Deferred/reference G3 artifacts

- [`PD-0001`](../product-design/PD-0001-g3-physical-design-inputs.md) translates
  reviewed capabilities into physical field/control/safety/RF/expansion/service
  inputs and has received input review;
- [`LAY-0001`](../product-design/LAY-0001-form-factor-candidates.md) visualizes
  compact, balanced and field-service same-scope experiments. Its drawing
  content was reviewed, but its direction is superseded by `DEC-0041`; no owner
  choice among P1/P2/P3 is requested.
- [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md) retains the
  accepted bounded U214 rear-envelope decision; `DEC-0058` pauses further
  integrated mockup/control/enclosure work until `INT-0001/I9`.

No electronic zone in `LAY-0001` assigns a chip, bus or pin. Former
`SYN/PIN/PKG` arithmetic may be reused only after exact-device revalidation.

## Active reviewed prerequisites

- reviewed stage-1 intent and safety/legal decisions;
- reviewed `REQ-*` behavior, evidence, concurrency and failure obligations with
  owner/backend clauses reopened by `DEC-0032`;
- `INV-0002/0004` for the prior 125 leaves, the current-competitor delta in
  [`AUD-0004`](../audits/AUD-0004-current-competitor-capability-gap.md), and the
  M5 expansion audit [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md),
  plus the former FIDO audit retained only as superseded evidence
  [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md),
  haptic prerequisite audit
  [`AUD-0007`](../audits/AUD-0007-haptic-product-mechanical-cost.md) and IMU
  instrument-value audit
  [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md), plus
  physical-keyboard archetype audit
  [`AUD-0009`](../audits/AUD-0009-physical-keyboard-product-archetype.md), and
  High-Speed USB host audit
  [`AUD-0010`](../audits/AUD-0010-high-speed-usb-host-use-cases.md), and
  mission-scope audit
  [`AUD-0011`](../audits/AUD-0011-radio-key-product-scope.md), and 6 GHz/Wi-Fi
  6E fact review
  [`AUD-0012`](../audits/AUD-0012-6ghz-wifi6e-product-scope.md).

`W-EXTRA-11` is reviewed by `DEC-0033/REQ-IBTN-0001`; M5-first Unit/Cap plus a
separate high-throughput class without native M5-Bus is reviewed by
`DEC-0034/REQ-EXT-0001`. `W-EXTRA-12` is reviewed by
former `DEC-0035/REQ-FIDO-0001` is removed from target by `DEC-0039`; product
haptic is rejected by `DEC-0036`; optional
external IMU measurement pose is reviewed by `DEC-0037/REQ-IMU-0001`. G2
also closes `W-EXTRA-15` through `DEC-0038`: no integrated keyboard, bounded
phone-assisted text. `DEC-0039/REQ-SCOPE-0001` reject generic `W-EXTRA-16`,
retain only RF-derived high-throughput transport and classify BadUSB as a
software-only exception. `DEC-0040` rejects `W-EXTRA-17` 6 GHz/Wi-Fi 6E from
base and optional product scope. `REV-0002AS` closes repeated G2 review; G3
target product design is now the active gate.

## Candidate/reference studies

- Former [`CAP-0001`](CAP-0001-zero-based-capability-input.md),
  [`CON-0001`](CON-0001-hardware-neutral-concurrency-model.md),
  [`RES-0001`](RES-0001-hardware-neutral-resource-demand.md),
  [`SRC-0001`](SRC-0001-primary-hardware-resource-facts.md),
  [`SYN-0001`](SYN-0001-zero-based-whole-device-candidates.md),
  [`PIN-0002`](PIN-0002-zero-based-exact-pin-maps.md),
  [`BUD-0002`](BUD-0002-zero-based-memory-traffic-budget.md),
  [`PWR-0001`](PWR-0001-zero-based-power-safety-envelope.md),
  [`RFQ-0001`](RFQ-0001-zero-based-rf-zoning-coexistence.md),
  [`CST-0001`](CST-0001-dated-candidate-cost-burden.md) and
  [`PKG-0001`](PKG-0001-zero-based-target-architecture-proposal.md) preserve
  useful electronic-placement arithmetic and risks.

They were reviewed for internal consistency, but not against a prior physical
product design or whole-product optimality model. None is a final prerequisite.
`SYN-3A` is one candidate among future alternatives, not the target.

## Archives

- [premature compute CAD](../../../drafts/premature-compute-cad-2026-08-16/README.md);
- [premature service CAD](../../../drafts/premature-service-cad-2026-08-16/README.md);
- [earlier legacy-derived stage 3](../../../drafts/stage3-legacy-derived-2026-08-16/README.md).

Every later artifact receives **«Проведено ревью»** only for its own reviewed
scope; no status propagates automatically to the next gate.
