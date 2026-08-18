# Leshy2 Hardware

> **Target product site.** This page describes the finished Leshy2: its purpose,
> capabilities, interfaces, principled design and mandatory guarantees.
> Engineering progress and open validation work live in separate documents.

- [Русская версия](README.ru.md)
- [Firmware target product](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
- [Current engineering state](docs/status/current-state.md)
- [Engineering decisions and evidence](docs/review/README.md)

## Finished-product intent

Leshy2 is an open, autonomous and portable instrument for spectrum observation,
diagnostics, communication and authorized research into wireless and contact
systems. It combines independent radio paths, a display, local controls, data
recording, audio, service access and expansion in one repairable device.

It is a field instrument rather than a general-purpose pocket computer: every
hardware capability must produce a measurable result, have a defined safe
state and remain diagnosable and recoverable by its owner.

## Three functional levels

1. **Main** — everyday tools, reception, diagnostics, navigation, maintenance
   and legitimate communications.
2. **Lab** — passive, defensive and bounded security-research tools.
3. **Lab → Controlled Zone** — dangerous active or disruptive tools. Every
   entry displays a fresh non-suppressible warning; every action separately
   requires an authorized target, isolated/conducted environment, or both.

Initial setup separately requires acceptance of the non-aggression pledge.
Neither acknowledgement arms a tool or overrides law, spectrum licensing,
privacy or the target owner's authorization.

## Finished-device capabilities

### Radio and communication

- Three independent full-function nRF24 paths operate concurrently in every
  `3R`, `1T2R`, `2T1R` and `3T` mix without silently disabling peer receivers.
- Exactly one top-level signal group owns the signal plane at a time. The three
  nRF paths form one such group and retain every required concurrent mix;
  contained cross-group Laboratory injection can characterize robustness but
  never grants a runtime permission. Every foreign interface is then driven to
  its measured quiet/off state.
- Each nRF path has switched-rail Ioff isolation in both digital directions,
  a dedicated full-band directional forward-power detector and its own
  external SMA feed. The module-side `IPX` mate is qualified from a received
  sample rather than assumed to be U.FL.
- Three separated nRF antennas provide calibrated relative sector/RPD
  comparison. The result is never presented as absolute dBm, angle or VSWR.
- 2.4/5 GHz Wi-Fi, Bluetooth LE, ESP-NOW and IEEE 802.15.4 provide ordinary
  communication, observation and authorized diagnostic workflows.
- The S3 2.4-GHz and C5 2.4/5-GHz radios keep independent external RP-SMA
  feeds. Each feed passes through its own `Hirose U.FL-R-SMT-1(10)` PCB mate
  and `KYOCERA AVX CP0603Q5425ENTR` directional coupler, so actual outgoing RF
  is measured without sharing an antenna or detector path.
- The dedicated `CC1101RGPR` Sub-GHz path selects 315, 433 or a combined
  868/915-MHz branch with two `BGS13SN8E6327XTSA1` switches, disconnecting every
  unused filter at both ends. Band controls change only while its rail is off;
  default `00` isolates all branches. A final-line 0.47-pF sample feeds an
  AON-held `AD8314ACPZ-RL7`; incoming RF can never authorize transmission.
- The Sub-GHz path handles packet systems; a broadcast receiver covers
  AM/FM/SW/LW; a VHF/UHF voice path provides analog communication and audio.
- The `Si4732-A10-GSR` keeps separate protected receive-only ports: FM/SW uses
  `FMI`, with `LQW15AN56NJ00D` 56-nH matching plus
  `GRM1555C1H102JA01D` 1-nF coupling as the FM starting network;
  AM/LW uses `GRM155R71A474KE01D` 0.47-uF coupling into a short labelled loop
  pod. Each boundary has its own `SESD0402X1UN-0020-090`; the AM/LW port is
  explicitly non-50-Ohm and arbitrary long coax is not supported. SW remains
  on the exact chip's published FMI input, but sensitivity is qualified from
  the complete path rather than inferred from the FM reference circuit.
- The exact audio endpoint can route either selected receive audio or the local
  electret microphone into the codec, play through a reset-off 4-Ohm speaker,
  or use insertion-detected 3.5-mm headphones. Codec, receiver and SA518 buses
  are physically isolated while their domains are off; PTT remains a separate
  STOP-dominated authorization and is never inferred from audio.
- Exact `TSOP95238TT` and `TSMP95000TT` receivers provide simultaneous robust
  38-kHz demodulation and measured 30–60-kHz carrier learning. Their filtered
  rail is discharged and Ioff-isolated while inactive. A side-view
  `VSMY14940` replays admitted profiles through a STOP-qualified, current-limited
  driver; a shielded `VEMD1060X01` optical pickup verifies emitted light rather
  than inferring it from drive current.
- All nine onboard antenna paths terminate at dedicated external ports: two
  RP-SMA for native Wi-Fi and seven standard SMA for the remaining paths.

### Interfaces and expansion

- A portrait 3.5-inch `320×480` touch IPS display uses direct QSPI; critical
  state and first menu feedback appear within `100 ms`.
- A removable microSD stores spectrum records, audio, profiles, logs and
  exported data. It is powered only for an active storage session, electrically
  isolated while off, protected on every exposed electrical contact, and
  detected independently of card power. Clean removal drains pending writes;
  unexpected removal is reported and recovered without pretending the last
  unwritten tail is intact.
- A rear 14-pin Cap-Bus accepts the removable M5Stack U214 LoRa/GNSS and
  compatible modules; a separate protected M5 Unit port supports GNSS,
  qualified LoRa modules, NFC, iButton/1-Wire and other extensions.
- A qualified raw-SDR or external RF-analysis module may define a separate
  high-throughput interface; a low-rate M5 command port is never presented as
  a raw-data path.
- Rare long-form text entry may use a locally paired phone, but the phone cannot
  authorize dangerous actions or replace controls on Leshy2.
- An external IMU may annotate measurements with pose and relative motion;
  without a qualified mount it is never presented as a compass or RF bearing.

### Serviceability

- Every programmable compute domain has its own programming, recovery and
  diagnostic path and does not depend on a healthy peer domain.
- S3 uses the protected product USB plus keyed UART0/RESET/BOOT access. C5 has
  its own data-only USB and keyed UART0/RESET/BOOT access; RP2354B has its own
  data-only USB and keyed SWD/RUN/USB_BOOT access. All three domains retain
  separate physical RESET and BOOT controls.
- The C5 and RP USB-C receptacles never power the product. Their VBUS reaches
  only a 1-MOhm bleeder/test point, and a board-powered USB switch disconnects
  D+/D- while the product is off, preventing cable backfeed.
- Hard STOP still dominates every recovery mode. Its reset output uses three
  passive-drain sinks, so a RESET button or fixture can pull a target low
  without fighting a driven-high logic output; recovery always starts TX-off.
- The product USB-C port keeps protected S3 USB2 Full-Speed data (12 Mbit/s)
  and accepts power only:
  5-V fallback, 9 V at 3 A and 15 V at 2 A, up to 30 W. It never acts as a
  power bank or USB-PD source.
- The PD controller enters hardware SafeMode directly from raw USB VBUS,
  autonomously loads a dedicated recoverable EEPROM and keeps the protected
  power path and charging off until a valid image is present. Factory pads can
  program a blank device; field updates verify an owner-signed image and retain
  a rollback region.
- The 2S charger is physically strapped to an efficient `750 kHz` profile
  with a `2.2 uH / 7 A` inductor. Reset restores a conservative `1 A` charge;
  normal operation never exceeds `2 A`, first limits input current to the
  actual 5/9/15-V USB contract and stops on direct battery-temperature faults.
- The supervised 2S battery uses two individually replaceable exact
  `XTAR 18650 4000mAh` protected button-top cells (`28.8 Wh` nominal per pair)
  in an exact polarized `Keystone 1048P` holder; both are required for battery
  operation. Raw flat-top cells are not supported, and the qualified cells
  ship as a separate regional kit by default. Reverse insertion is
  mechanically blocked; hardware observes and admits the pair before it may
  reach the system, and refuses an unsafe combination instead of forcing it
  to operate or equalize. The handheld also refuses deeply discharged cells:
  zero-volt/prequalification recovery is disabled, and any recovery research
  requires a separate isolated Controlled-Zone fixture. Before admission, a
  common-path 10-Ohm diagnostic applies approximately `0.57…0.88 A` for no
  more than `50 ms`. One non-retriggerable hardware channel prevents pulse
  stretching; a second channel then blocks every retry for at least `350 ms`,
  even if firmware is faulty. Two parallel 20-Ohm/2-W pulse-rated branches
  preserve the 10-Ohm load and safely share worst-case repetition heat. Normal
  software waits at least 10 seconds. This is a contact/cell screen, not a
  full-load qualification claim.
- Four independent fixed rails separate always-on safety, 3.3-V compute,
  4.0-V voice and protected 5.0-V accessory power. Unused radio, storage and
  audio branches are disconnected and discharged into a verified quiet state.
  Each converter output crosses its own hardware overvoltage/current/short
  cutoff before it can reach a load. The protected AON rail and its physical
  power-good evidence hold the 3.07-V supervisor in reset; only its delayed
  hardware POR enables the main rail. Firmware cannot bypass source admission,
  AON brownout, any internal protection boundary or that startup order.
  Runtime trusts only protected-side power-good evidence. A latched main fault
  requires complete source removal and fresh admission. The AON cutoff may
  perform its own bounded hardware recovery attempts, but software cannot
  accelerate them and main remains off until protected AON is stably valid.
- The protected accessory port admits startup through a controlled voltage
  slew under an immediately active current limit. It supports `1.25 A`
  continuously and a bounded `2.0 A` transient only after startup; an expired
  overload or other eFuse fault latches the port off instead of auto-retrying.
- Signed updates validate their target and support rollback. Build keys and the
  ability to install owner firmware remain owner-controlled; irreversible
  lockdown is not enabled by default.

## Principled solution design

Three compute domains separate the UI, broadband wireless functions and
deterministic radio service. Independent buses keep an active radio path from
waiting for the display, storage or another radio. Unused interfaces enter a
verified electrically quiet state.

The diagram is maintained as a narrow top-to-bottom projection of the target
internals. Every box represents one physical component and includes its MPN or
an explicit `MPN TBD`, together with its role in the finished device.

```mermaid
flowchart TD
  USBC["DX07S016JA1R1500<br/>product USB-C receptacle: protected S3 USB2 data and sink-only power"]
  PORTPROT["TPD4S201RUKR<br/>CC1/CC2 and USB2 D+/D- short-to-VBUS/ESD protector"]
  PORTDPR["ERJ-2RKF22R0X #USB-DP<br/>22-Ohm S3 USB Full-Speed D+ series resistor"]
  PORTDMR["ERJ-2RKF22R0X #USB-DM<br/>22-Ohm S3 USB Full-Speed D- series resistor"]
  PORTVBIAS["C1608X7S2A104K080AB<br/>100-nF 100-V port-protector VBIAS capacitor"]
  PORTVPWR["C1608X7R1C105K080AC #USB-PROT<br/>1-uF 16-V port-protector VPWR capacitor"]
  PORTFLTPU["RC0402FR-0710KL #USB-PROT-FLT<br/>10-kOhm port-protector fault pull-up"]
  VBUSPROT["TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection"]
  PDCTRL["TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path"]
  PDCFG["CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM"]
  PVINCAP["GRM188R60J106ME47D #VIN<br/>10-uF PD-controller VIN_3V3 capacitor"]
  PL3CAP["GRM188R60J106ME47D #LDO3V3<br/>10-uF PD-controller 3.3-V LDO capacitor"]
  PL1CAP["GRM188R60J106ME47D #LDO1V5<br/>10-uF PD-controller 1.5-V LDO capacitor"]
  PPHVC0["GRM32ER71E226KE15L #PPHV0<br/>22-uF 25-V protected-VBUS capacitor #0"]
  PPHVC1["GRM32ER71E226KE15L #PPHV1<br/>22-uF 25-V protected-VBUS capacitor #1"]
  PPHVC2["GRM32ER71E226KE15L #PPHV2<br/>22-uF 25-V protected-VBUS capacitor #2"]
  PPHVC3["GRM32ER71E226KE15L #PPHV3<br/>22-uF 25-V protected-VBUS capacitor #3"]
  PVBUSCAP["CGA5L1X7R1E475K160AC #PD-VBUS<br/>4.7-uF 25-V raw-VBUS startup capacitor"]
  PCC1CAP["GRM1555C1H221JA01D #CC1<br/>220-pF C0G protected USB-C CC1 capacitor"]
  PCC2CAP["GRM1555C1H221JA01D #CC2<br/>220-pF C0G protected USB-C CC2 capacitor"]
  PEECAP["C1005X7R1H104K050BB #PD-EEPROM<br/>100-nF PD EEPROM bypass capacitor"]
  PEEWPPU["RC0402FR-0710KL #PD-WP<br/>10-kOhm reset-high EEPROM write-protect pull-up"]
  PLSCLPU["RC0402FR-072K2L #PD-SCL<br/>2.2-kOhm local PD-bus SCL pull-up"]
  PLSDAPU["RC0402FR-072K2L #PD-SDA<br/>2.2-kOhm local PD-bus SDA pull-up"]
  PHSCLPU["RC0402FR-072K2L #SYS-SCL<br/>2.2-kOhm host-bus SCL pull-up"]
  PHSDAPU["RC0402FR-072K2L #SYS-SDA<br/>2.2-kOhm host-bus SDA pull-up"]
  PIRQPU["RC0402FR-0710KL #SYS-IRQ<br/>10-kOhm shared wired-low IRQ pull-up"]
  CHARGER["BQ25798RQMR<br/>2S-configured buck-boost charger and NVDC system power path"]
  CHL["MWSA0503S-2R2MT<br/>2.2-uH 7-A 750-kHz charger inductor"]
  CVB0["GRM31CR71E106MA12L #VBUS0<br/>10-uF 25-V X7R charger VBUS capacitor #0"]
  CVB1["GRM31CR71E106MA12L #VBUS1<br/>10-uF 25-V X7R charger VBUS capacitor #1"]
  CVBHF["C1005X7R1H104K050BB #VBUS<br/>100-nF 50-V charger VBUS HF capacitor"]
  CPM0["GRM31CR71E106MA12L #PMID0<br/>10-uF 25-V X7R charger PMID capacitor #0"]
  CPM1["GRM31CR71E106MA12L #PMID1<br/>10-uF 25-V X7R charger PMID capacitor #1"]
  CPM2["GRM31CR71E106MA12L #PMID2<br/>10-uF 25-V X7R charger PMID capacitor #2"]
  CPMHF["C1005X7R1H104K050BB #PMID<br/>100-nF 50-V charger PMID HF capacitor"]
  CSYS0["GRM31CR71E106MA12L #SYS0<br/>10-uF 25-V X7R charger SYS capacitor #0"]
  CSYS1["GRM31CR71E106MA12L #SYS1<br/>10-uF 25-V X7R charger SYS capacitor #1"]
  CSYS2["GRM31CR71E106MA12L #SYS2<br/>10-uF 25-V X7R charger SYS capacitor #2"]
  CSYS3["GRM31CR71E106MA12L #SYS3<br/>10-uF 25-V X7R charger SYS capacitor #3"]
  CSYS4["GRM31CR71E106MA12L #SYS4<br/>10-uF 25-V X7R charger SYS capacitor #4"]
  CSYSHF["C1005X7R1H104K050BB #SYS<br/>100-nF 50-V charger SYS HF capacitor"]
  CBAT0["GRM31CR71E106MA12L #BAT0<br/>10-uF 25-V X7R charger BAT capacitor #0"]
  CBAT1["GRM31CR71E106MA12L #BAT1<br/>10-uF 25-V X7R charger BAT capacitor #1"]
  CBT1["GRM155R71E473KA88D #BTST1<br/>47-nF 25-V charger bootstrap capacitor #1"]
  CBT2["GRM155R71E473KA88D #BTST2<br/>47-nF 25-V charger bootstrap capacitor #2"]
  CREGN["CGA5L1X7R1E475K160AC #REGN<br/>4.7-uF 25-V charger REGN capacitor"]
  CSDRV["C0402C102K5RACTU<br/>1-nF 50-V no-ship-FET SDRV capacitor"]
  CPROG["RC0402FR-078K2L<br/>8.2-kOhm 1% 2S/750-kHz PROG resistor"]
  CBATP["RC0402FR-07100RL<br/>100-Ohm 1% BATP sense resistor"]
  CTSU["RC0402FR-075K23L<br/>5.23-kOhm 1% charger TS upper resistor"]
  CTSL["RC0402FR-0730K1L<br/>30.1-kOhm 1% charger TS lower resistor"]
  CTSN["B57332V5103F360 #CHARGER<br/>independent 10-kOhm charger battery NTC"]
  CILU["RC0402FR-0744K2L<br/>44.2-kOhm 1% hardware ILIM upper resistor"]
  CILL["RC0402FR-07100KL<br/>100-kOhm 1% hardware ILIM lower resistor"]
  CINTPU["RC0402FR-0710KL #CHG-INT<br/>10-kOhm charger INT pull-up resistor"]
  CCEPU["RC0402FR-0710KL #CHG-CE<br/>10-kOhm reset-high charger CE pull-up resistor"]
  HOLDER["Keystone Electronics 1048P<br/>polarized dual protected-button-top 18650 holder"]
  CELL0["XTAR 18650 4000mAh #0<br/>qualified protected button-top 4-Ah cell"]
  FUSE0["0451005.MRL<br/>slot-0 independent 5-A fast fuse"]
  NTC0["B57332V5103F360<br/>cell-0 temperature sensor"]
  CELL1["XTAR 18650 4000mAh #1<br/>qualified protected button-top 4-Ah cell"]
  FUSE1["0451005.MRL<br/>slot-1 independent 5-A fast fuse"]
  NTC1["B57332V5103F360<br/>cell-1 temperature sensor"]
  PACKGAUGE["MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing"]
  PACKINR["ERJ-P08F10R0V<br/>10-Ohm MAX17320 IN series resistor"]
  PACKINC["C1005X7R1H104K050BB<br/>100-nF 50-V MAX17320 IN bypass capacitor"]
  PACKCPC["GRM188R71E474KA12D<br/>0.47-uF 25-V MAX17320 CP-to-IN capacitor"]
  PACKAOC["GRM188R71E474KA12D<br/>0.47-uF 25-V MAX17320 AOLDO bypass capacitor"]
  PACKR3C["GRM188R71E474KA12D<br/>0.47-uF 25-V MAX17320 REG3 bypass capacitor"]
  PACKR2C["GRM188R71E474KA12D<br/>0.47-uF 25-V MAX17320 REG2 bypass capacitor"]
  PACKRB1["ERJ-P08F49R9V<br/>49.9-Ohm 0.66-W bottom-cell balancing resistor"]
  PACKRB4["ERJ-P08F49R9V<br/>49.9-Ohm 0.66-W top-cell balancing resistor"]
  PACKCF1["C1005X7R1H104K050BB<br/>100-nF 50-V bottom-cell sense filter capacitor"]
  PACKCF4["C1005X7R1H104K050BB<br/>100-nF 50-V top-cell sense filter capacitor"]
  PACKPCKR["RC0402FR-071KL<br/>1-kOhm protected-pack PCKP series resistor"]
  SHUNT["WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACKFET["CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair"]
  PACKCGC["C1005X7R1H104K050BB<br/>100-nF charge-FET gate-to-source capacitor"]
  PACKDGC["C1005X7R1H104K050BB<br/>100-nF discharge-FET gate-to-source capacitor"]
  PACKHOLD["2N7002DW-7-F<br/>reset-default ALRT hold and explicit release"]
  PACKHOLDPU["RC0402FR-0710KL<br/>10-kOhm reset-default ALRT-hold pull-up resistor"]
  PACKRELDPD["RC0402FR-0710KL<br/>10-kOhm hold-release fail-low resistor"]
  PACKALRTPU["RC0402FR-0710KL<br/>10-kOhm REG3-referenced ALRT release pull-up resistor"]
  PACKSTAT["2N7002DW-7-F<br/>dual PFAIL level translator and passive-drain system IRQ"]
  PACKPFAILPU["RC0402FR-0710KL<br/>10-kOhm admission-referenced PFAIL_N pull-up resistor"]
  PACKIRQPD["RC0402FR-0710KL<br/>10-kOhm shared-IRQ gate fail-low resistor"]
  PACKSCLPU["RC0402FR-0710KL<br/>10-kOhm private gauge-clock pull-up resistor"]
  PACKSDAPU["RC0402FR-0710KL<br/>10-kOhm private gauge-data pull-up resistor"]
  SUPPLYOR["BAV70LT1G<br/>AOLDO/fixture source isolation"]
  SYSDIODE["BAT54-7-F<br/>admitted-system source isolation and priority"]
  PACKADM["MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge"]
  PACKMCUBULK["GRM188R60J106ME47D<br/>10-uF admission-controller bulk decoupling capacitor"]
  PACKMCUHF["C1005X7R1H104K050BB<br/>100-nF admission-controller bypass capacitor"]
  PACKRSTPU["RC0402FR-0747KL<br/>47-kOhm admission-controller NRST pull-up resistor"]
  PACKRSTC["GRM155R71H103KA88D<br/>10-nF admission-controller NRST capacitor"]
  DIAGTMR["TPUL2G223BQBR<br/>non-retriggerable pulse limiter and refractory lockout"]
  DIAGTR["RC0402FR-07169KL #DIAG-TIME<br/>169-kOhm 1% diagnostic-pulse timing resistor"]
  DIAGTC["GRM31C5C1H224JE02L #DIAG-TIME<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor"]
  DIAGLR["RC0402FR-07620KL<br/>620-kOhm 1% refractory-lockout timing resistor"]
  DIAGLC["C1608X7R1C105K080AC<br/>1-uF 16-V X7R refractory-lockout timing capacitor"]
  DIAGBP["C1005X7R1H104K050BB #DIAG<br/>100-nF 50-V X7R one-shot bypass capacitor"]
  DIAGTRPD["RC0402FR-0710KL #DIAG-TRIG<br/>10-kOhm 1% diagnostic-trigger fail-low resistor"]
  DIAGGPD["RC0402FR-0710KL #DIAG-GATE<br/>10-kOhm 1% diagnostic-gate fail-low resistor"]
  DIAGQ["DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET"]
  DIAGR0["CRM2512-FX-20R0ELF #0<br/>20-Ohm 2-W pulse-rated diagnostic-load branch"]
  DIAGR1["CRM2512-FX-20R0ELF #1<br/>20-Ohm 2-W pulse-rated diagnostic-load branch"]
  MIDADC0["RC0402FR-07220KL #MID-TOP0<br/>220-kOhm 1% midpoint-divider top resistor #0"]
  MIDADC1["RC0402FR-07220KL #MID-TOP1<br/>220-kOhm 1% midpoint-divider top resistor #1"]
  MIDADCB["RC0402FR-07169KL #MID-BOTTOM<br/>169-kOhm 1% midpoint-divider bottom resistor"]
  MIDADCC["GRM155R71H103KA88D #MID<br/>10-nF 50-V X7R midpoint ADC filter capacitor"]
  STACKADC0["RC0402FR-07220KL #STACK-TOP0<br/>220-kOhm 1% stack-divider top resistor #0"]
  STACKADC1["RC0402FR-07220KL #STACK-TOP1<br/>220-kOhm 1% stack-divider top resistor #1"]
  STACKADC2["RC0402FR-07220KL #STACK-TOP2<br/>220-kOhm 1% stack-divider top resistor #2"]
  STACKADC3["RC0402FR-07220KL #STACK-TOP3<br/>220-kOhm 1% stack-divider top resistor #3"]
  STACKADC4["RC0402FR-07220KL #STACK-TOP4<br/>220-kOhm 1% stack-divider top resistor #4"]
  STACKADCB["RC0402FR-07169KL #STACK-BOTTOM<br/>169-kOhm 1% stack-divider bottom resistor"]
  STACKADCC["GRM155R71H103KA88D #STACK<br/>10-nF 50-V X7R stack ADC filter capacitor"]
  AONBUCK["TPS629203DRLR<br/>low-IQ always-on 3.3-V safety converter"]
  AONL["WPN201612H2R2MT<br/>2.2-uH shielded AON converter inductor"]
  AONMODE["RC0402FR-0742K2L<br/>42.2-kOhm 1% AON mode/configuration resistor"]
  AONIN["CGA5L1X7R1E475K160AC<br/>4.7-uF 25-V X7R AON input capacitor"]
  AONOUT["GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON raw-output capacitor"]
  AONFUSE["TPS25961DRVR<br/>independent AON overvoltage/current/short cutoff"]
  AONRILIM["RC0402FR-07240KL<br/>240-kOhm 1% AON eFuse current-limit resistor"]
  AONOVT["RC0402FR-07196KL<br/>196-kOhm 1% AON eFuse OVLO top resistor"]
  AONOVB["RC0402FR-07100KL #AON-OVLO<br/>100-kOhm 1% AON eFuse OVLO bottom resistor"]
  AONFIN["C1005X7R1H104K050BB #AON-EFUSE-IN<br/>100-nF 50-V X7R AON eFuse input capacitor"]
  AONFOUT["GRM188R60J106ME47D #AON-SAFE<br/>10-uF 6.3-V X5R protected-AON output capacitor"]
  AONPGPU["RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor"]
  PORPU["RC0402FR-0710KL #AON-POR<br/>10-kOhm 1% AON POR pull-up resistor"]
  MAINBUCK["TPS564252DRLR<br/>fixed 3.3-V 4-A main converter"]
  MAINL["MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor"]
  MAININ["GRM32ER71E226KE15L #MAIN-IN<br/>22-uF 25-V X7R main bulk input capacitor"]
  MAINHF["C1005X7R1H104K050BB #MAIN<br/>100-nF 50-V X7R main HF input capacitor"]
  MAINFBT["RC0402FR-0745K3L<br/>45.3-kOhm 1% main feedback top resistor"]
  MAINFBB["RC0402FR-0710KL<br/>10-kOhm 1% main feedback bottom resistor"]
  MAINFF["C0402C330J5GACTU #MAIN<br/>33-pF 50-V C0G main feed-forward capacitor"]
  MAINOUT0["GRM32ER71E226KE15L #MAIN-OUT0<br/>22-uF 25-V X7R main raw-output capacitor #0"]
  MAINOUT1["GRM32ER71E226KE15L #MAIN-OUT1<br/>22-uF 25-V X7R main raw-output capacitor #1"]
  MAINFUSE["TPS25974LRPWR #MAIN<br/>main latch-off overvoltage circuit-breaker eFuse with protected PG"]
  MAINRILM["RC0402FR-071K65L<br/>1.65-kOhm 1% main eFuse threshold resistor"]
  MAINDVDT["GRM155R71H472KA01D #MAIN<br/>4.7-nF 50-V X7R main eFuse slew capacitor"]
  MAINIT["GRM1555C1H121JA01D #MAIN<br/>120-pF 50-V C0G main eFuse transient timer"]
  MAINOVT["RT0402BRD07191KL<br/>191-kOhm 0.1% main eFuse OVLO top resistor"]
  MAINOVB["RT0402BRD07100KL<br/>100-kOhm 0.1% main eFuse OVLO bottom resistor"]
  MAINPGT["RC0402FR-0745K3L #MAIN-PGTH<br/>45.3-kOhm 1% main protected-PG top resistor"]
  MAINPGB["RC0402FR-0730KL #MAIN-PGTH<br/>30-kOhm 1% main protected-PG bottom resistor"]
  MAINFOUT["GRM188R60J106ME47D #MAIN-SAFE<br/>10-uF 6.3-V X5R protected-main output capacitor"]
  MAINENPD["RC0402FR-07100KL #MAIN-EN<br/>100-kOhm 1% main-enable fail-low resistor"]
  FAULTPU["RC0402FR-0710KL #POWER-FAULT<br/>10-kOhm 1% wired-low power-fault pull-up resistor"]
  VOICEBUCK["TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter"]
  VOICEL["MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor"]
  VOICEIN["GRM32ER71E226KE15L #VOICE-IN<br/>22-uF 25-V X7R voice bulk input capacitor"]
  VOICEHF["C1005X7R1H104K050BB #VOICE<br/>100-nF 50-V X7R voice HF input capacitor"]
  VOICEFBT["RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor"]
  VOICEFBB["RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor"]
  VOICEFF["C0402C330J5GACTU #VOICE<br/>33-pF 50-V C0G voice feed-forward capacitor"]
  VOICEOUT0["GRM32ER71E226KE15L #VOICE-OUT0<br/>22-uF 25-V X7R voice raw-output capacitor #0"]
  VOICEOUT1["GRM32ER71E226KE15L #VOICE-OUT1<br/>22-uF 25-V X7R voice raw-output capacitor #1"]
  VOICEFUSE["TPS25974LRPWR #VOICE<br/>voice latch-off overvoltage circuit-breaker eFuse with protected PG"]
  VOICERILIM["RC0402FR-073K32L<br/>3.32-kOhm 1% voice eFuse threshold resistor"]
  VOICEDVDT["GRM155R71H472KA01D #VOICE<br/>4.7-nF 50-V X7R voice eFuse slew capacitor"]
  VOICEIT["GRM1555C1H121JA01D #VOICE<br/>120-pF 50-V C0G voice eFuse transient timer"]
  VOICEOVT["RC0402FR-07270KL<br/>270-kOhm 1% voice eFuse OVLO top resistor"]
  VOICEOVB["RC0402FR-07100KL #VOICE-OVLO<br/>100-kOhm 1% voice eFuse OVLO bottom resistor"]
  VOICEPGT["RC0402FR-0768KL #VOICE-PGTH<br/>68-kOhm 1% voice protected-PG top resistor"]
  VOICEPGB["RC0402FR-0733KL #VOICE-PGTH<br/>33-kOhm 1% voice protected-PG bottom resistor"]
  VOICEFOUT["GRM188R60J106ME47D #VOICE-SAFE<br/>10-uF 6.3-V X5R protected-voice output capacitor"]
  VOICEENPD["RC0402FR-0710KL #VOICE-EN<br/>10-kOhm 1% voice-enable fail-low resistor"]
  VOICEPGPU["RC0402FR-0710KL #VOICE-PG<br/>10-kOhm 1% voice power-good pull-up resistor"]
  VOICEPGBR["RC0402FR-0768KL #VOICE-PG-BASE<br/>68-kOhm 1% voice PG-qualifier base resistor"]
  VOICEPGQ["MMBT3904-7-F<br/>voice-rail enable-qualified PG fault transistor"]
  EXTBUCK["TPS564252DRLR<br/>fixed 5.0-V 4-A accessory converter"]
  EXTL["MWSA0503S-4R7MT<br/>4.7-uH accessory-rail power inductor"]
  EXTBUCKIN["GRM32ER71E226KE15L #EXT-BUCK-IN<br/>22-uF 25-V X7R accessory-buck bulk input capacitor"]
  EXTBUCKHF["C1005X7R1H104K050BB #EXT-BUCK<br/>100-nF 50-V X7R accessory-buck HF input capacitor"]
  EXTBUCKFBT["RC0402FR-07220KL<br/>220-kOhm 1% accessory feedback top resistor"]
  EXTBUCKFBB["RC0402FR-0730KL<br/>30-kOhm 1% accessory feedback bottom resistor"]
  EXTBUCKFF["C0402C330J5GACTU #EXT-BUCK<br/>33-pF 50-V C0G accessory feed-forward capacitor"]
  EXTBUCKOUT0["GRM32ER71E226KE15L #EXT-BUCK-OUT0<br/>22-uF 25-V X7R accessory output capacitor #0"]
  EXTBUCKOUT1["GRM32ER71E226KE15L #EXT-BUCK-OUT1<br/>22-uF 25-V X7R accessory output capacitor #1"]
  EXTENPD["RC0402FR-0710KL #EXT-EN<br/>10-kOhm 1% accessory-enable fail-low resistor"]
  EXTPGPU["RC0402FR-0710KL #EXT-PG<br/>10-kOhm 1% accessory power-good pull-up resistor"]
  EXTPGBR["RC0402FR-0768KL #EXT-PG-BASE<br/>68-kOhm 1% accessory PG-qualifier base resistor"]
  EXTPGQ["MMBT3904-7-F<br/>accessory-rail enable-qualified PG fault transistor"]
  EXTFUSE["TPS259470LRPWR<br/>true-reverse-blocking latch-off accessory eFuse/current monitor"]
  EXTRILM["RC0402FR-072K21L<br/>2.21-kOhm 1% eFuse current-limit resistor"]
  EXTDVDT["GRM155R71H472KA01D<br/>4.7-nF 50-V X7R startup-slew capacitor"]
  EXTITIMER["GRM188R71E224KA88D<br/>220-nF 25-V X7R post-start transient timer"]
  EXTOVLOT["RC0402FR-07169KL<br/>169-kOhm 1% eFuse OVLO top resistor"]
  EXTOVLOB["RC0402FR-0747KL<br/>47-kOhm 1% eFuse OVLO bottom resistor"]
  EXTINCAP["GRM21BR71E225KE11L #IN<br/>2.2-uF 25-V X7R local eFuse input capacitor"]
  EXTOUTCAP["GRM21BR71E225KE11L #OUT<br/>2.2-uF 25-V X7R local eFuse output capacitor"]
  EXTBLEED["RC0603FR-071KL<br/>1-kOhm 1% protected-output discharge resistor"]
  SWNRF["TPS22919DCKR<br/>three-radio nRF quiet-state load switch"]
  SWCC["TPS22919DCKR<br/>CC1101 quiet-state load switch"]
  SWSD["TPS22919DCKR<br/>microSD quiet-state load switch"]
  SWCODEC["TPS22919DCKR<br/>ES8311 quiet-state load switch"]
  SWRX["TPS22919DCKR<br/>Si4732 quiet-state load switch"]
  S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display/storage, audio, BLE/Wi-Fi owner"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, IEEE 802.15.4 and IR owner"]
  RP["SC1512-A4 (RP2354B0A4)<br/>deterministic radio and voice owner"]
  C5USBC["GCT USB4105-GF-A #C5<br/>independent data-only USB-C service receptacle"]
  C5UESD["Texas Instruments TPD2EUSB30ADRTR #C5<br/>service USB D+/D- ESD shunt"]
  C5UMUX["onsemi FSUSB42MUX #C5<br/>board-off D+/D- backfeed-isolation switch"]
  C5UMUXBP["C1005X7R1H104K050BB #C5-USB-SW<br/>USB-switch local bypass capacitor"]
  C5CC1["RC0402FR-075K1L #C5-CC1<br/>passive Type-C Rd resistor"]
  C5CC2["RC0402FR-075K1L #C5-CC2<br/>passive Type-C Rd resistor"]
  C5VB["RC0402FR-071ML #C5-VBUS<br/>sense-only VBUS bleeder resistor"]
  C5DMR["ERJ-2RKF22R0X #C5-DM<br/>MCU-side USB D- series resistor"]
  C5DPR["ERJ-2RKF22R0X #C5-DP<br/>MCU-side USB D+ series resistor"]
  RPUSBC["GCT USB4105-GF-A #RP<br/>independent data-only USB-C service receptacle"]
  RPUESD["Texas Instruments TPD2EUSB30ADRTR #RP<br/>service USB D+/D- ESD shunt"]
  RPUMUX["onsemi FSUSB42MUX #RP<br/>board-off D+/D- backfeed-isolation switch"]
  RPUMUXBP["C1005X7R1H104K050BB #RP-USB-SW<br/>USB-switch local bypass capacitor"]
  RPCC1["RC0402FR-075K1L #RP-CC1<br/>passive Type-C Rd resistor"]
  RPCC2["RC0402FR-075K1L #RP-CC2<br/>passive Type-C Rd resistor"]
  RPVB["RC0402FR-071ML #RP-VBUS<br/>sense-only VBUS bleeder resistor"]
  RPDMR["ERJ-2RKF27R0X #RP-DM<br/>MCU-side USB D- series resistor"]
  RPDPR["ERJ-2RKF27R0X #RP-DP<br/>MCU-side USB D+ series resistor"]
  S3DBG["Samtec FTSH-105-01-L-DV-K-P-TR #S3<br/>keyed independent DBG10 header"]
  C5DBG["Samtec FTSH-105-01-L-DV-K-P-TR #C5<br/>keyed independent DBG10 header"]
  RPDBG["Samtec FTSH-105-01-L-DV-K-P-TR #RP<br/>keyed independent DBG10 header"]
  S3DBGE["TPD4E05U06DQAR #S3-DBG<br/>RESET/BOOT/UART ESD array"]
  C5DBGE["TPD4E05U06DQAR #C5-DBG<br/>RESET/BOOT/UART ESD array"]
  RPDBGE["TPD4E05U06DQAR #RP-DBG<br/>RUN/BOOT/SWD ESD array"]
  S3RSTSW["Alps Alpine SKQGADE010 #S3-RESET<br/>separate physical RESET service control"]
  S3BOOTSW["Alps Alpine SKQGADE010 #S3-BOOT<br/>separate physical BOOT service control"]
  C5RSTSW["Alps Alpine SKQGADE010 #C5-RESET<br/>separate physical RESET service control"]
  C5BOOTSW["Alps Alpine SKQGADE010 #C5-BOOT<br/>separate physical BOOT service control"]
  RPRSTSW["Alps Alpine SKQGADE010 #RP-RESET<br/>separate physical RESET service control"]
  RPBOOTSW["Alps Alpine SKQGADE010 #RP-BOOT<br/>separate physical BOOT service control"]
  S3VTR["RC0402FR-071KL #S3-VTREF<br/>fixture voltage-sense resistor"]
  S3RSTR["RC0402FR-071KL #S3-RESET<br/>fixture reset-current resistor"]
  S3BOOTR["RC0402FR-071KL #S3-BOOT<br/>fixture boot-current resistor"]
  S3D0R["RC0402FR-07470RL #S3-DBG0<br/>UART0-TX fixture-current resistor"]
  S3D1R["RC0402FR-07470RL #S3-DBG1<br/>UART0-RX fixture-current resistor"]
  S3ID0["RC0402FR-0710KL #S3-ID0<br/>passive DBG10 identity strap"]
  S3ID1["RC0402FR-0710KL #S3-ID1<br/>passive DBG10 identity strap"]
  C5VTR["RC0402FR-071KL #C5-VTREF<br/>fixture voltage-sense resistor"]
  C5RSTR["RC0402FR-071KL #C5-RESET<br/>fixture reset-current resistor"]
  C5BOOTR["RC0402FR-071KL #C5-BOOT<br/>fixture boot-current resistor"]
  C5D0R["RC0402FR-07470RL #C5-DBG0<br/>UART0-TX fixture-current resistor"]
  C5D1R["RC0402FR-07470RL #C5-DBG1<br/>UART0-RX fixture-current resistor"]
  C5ID0["RC0402FR-0710KL #C5-ID0<br/>passive DBG10 identity strap"]
  C5ID1["RC0402FR-0710KL #C5-ID1<br/>passive DBG10 identity strap"]
  RPVTR["RC0402FR-071KL #RP-VTREF<br/>fixture voltage-sense resistor"]
  RPRSTR["RC0402FR-071KL #RP-RUN<br/>fixture reset-current resistor"]
  RPBOOTR["RC0402FR-071KL #RP-BOOT<br/>fixture boot-current resistor"]
  RPD0R["RC0402FR-07470RL #RP-DBG0<br/>SWDIO fixture-current resistor"]
  RPD1R["RC0402FR-07470RL #RP-DBG1<br/>SWCLK fixture-current resistor"]
  RPID0["RC0402FR-0710KL #RP-ID0<br/>passive DBG10 identity strap"]
  RPID1["RC0402FR-0710KL #RP-ID1<br/>passive DBG10 identity strap"]
  S3BPU["RC0402FR-0710KL #S3-BOOT<br/>deterministic normal-boot pull-up"]
  C5BPU["RC0402FR-0710KL #C5-BOOT<br/>deterministic normal-boot pull-up"]
  RPBPU["RC0402FR-0710KL #RP-BOOT<br/>deterministic normal-boot pull-up"]
  C5G27PU["RC0402FR-0710KL #C5-GPIO27<br/>fixed-high normal-boot and ROM-log strap"]
  SLOW["TCA6424ARGJR<br/>24-line main slow-control expander; all contacts allocated"]
  SLOWVCI["C1005X7R1H104K050BB #SLOW-VCCI<br/>100-nF main slow-I/O VCCI bypass capacitor"]
  SLOWVCP["C1005X7R1H104K050BB #SLOW-VCCP<br/>100-nF main slow-I/O VCCP bypass capacitor"]
  SLOWBULK["C1608X7R1C105K080AC #SLOW<br/>1-uF main slow-I/O local bulk capacitor"]
  SLOWRSTPU["RC0402FR-0710KL #SLOW-RESET<br/>10-kOhm main slow-I/O RESET_N pull-up"]
  SLOWRST(("SLOW_IO_RESET_N<br/>protected fixture-reset node"))
  SLOWSTOPISO["SN74LVC1G07DCKR #STOP-SENSE<br/>AON-powered open-drain STOP-sense domain isolator"]
  SLOWSTOPBP["C1005X7R1H104K050BB #STOP-SENSE<br/>100-nF STOP-sense-isolator bypass capacitor"]
  SLOWSTOPPU["RC0402FR-0710KL #STOP-SENSE<br/>10-kOhm main-domain STOP-sense pull-up"]
  SLOWEVISO["SN74LVC1G07DCKR #S3-EVIDENCE<br/>AON-powered open-drain S3-evidence domain isolator"]
  SLOWEVBP["C1005X7R1H104K050BB #S3-EVIDENCE<br/>100-nF S3-evidence-isolator bypass capacitor"]
  SLOWEVPU["RC0402FR-0710KL #S3-EVIDENCE<br/>10-kOhm main-domain S3-evidence pull-up"]
  UIMATRIX["TCA9534APWR #UI<br/>dedicated interrupt-capable 4x3 control expander"]
  UIMBP["C1005X7R1H104K050BB #UI<br/>100-nF UI-expander bypass capacitor"]
  UIR0PD["RC0603FR-071KL #UI-R0<br/>1-kOhm reset/idle row pull-down"]
  UIR1PD["RC0603FR-071KL #UI-R1<br/>1-kOhm reset/idle row pull-down"]
  UIR2PD["RC0603FR-071KL #UI-R2<br/>1-kOhm reset/idle row pull-down"]
  UIR3PD["RC0603FR-071KL #UI-R3<br/>1-kOhm reset/idle row pull-down"]
  UIC0PU["RC0402FR-0710KL #UI-C0<br/>10-kOhm matrix-column pull-up"]
  UIC1PU["RC0402FR-0710KL #UI-C1<br/>10-kOhm matrix-column pull-up"]
  UIC2PU["RC0402FR-0710KL #UI-C2<br/>10-kOhm matrix-column pull-up"]
  UIMESD["TPD8E003DQDR<br/>eight-channel keypad/GPIO ESD array for P0-P7"]
  UIDUP["onsemi 1N4148WT #UP<br/>D-pad UP matrix-isolation diode"]
  UIDDN["onsemi 1N4148WT #DOWN<br/>D-pad DOWN matrix-isolation diode"]
  UIDLEFT["onsemi 1N4148WT #LEFT<br/>D-pad LEFT matrix-isolation diode"]
  UIDRIGHT["onsemi 1N4148WT #RIGHT<br/>D-pad RIGHT matrix-isolation diode"]
  UIDOK["onsemi 1N4148WT #OK<br/>D-pad OK matrix-isolation diode"]
  UIDBACK["onsemi 1N4148WT #BACK<br/>BACK matrix-isolation diode"]
  UIDOPT["onsemi 1N4148WT #OPT<br/>OPT matrix-isolation diode"]
  UIDF1["onsemi 1N4148WT #F1<br/>F1 matrix-isolation diode"]
  UIDF2["onsemi 1N4148WT #F2<br/>F2 matrix-isolation diode"]
  UIDENC["onsemi 1N4148WT #ENC<br/>encoder-push matrix-isolation diode"]
  UIUP["Y78B23214FP<br/>D-pad UP ultra-low-current ordinary control"]
  UIDOWN["Y78B23214FP<br/>D-pad DOWN ultra-low-current ordinary control"]
  UILEFT["Y78B23214FP<br/>D-pad LEFT ultra-low-current ordinary control"]
  UIRIGHT["Y78B23214FP<br/>D-pad RIGHT ultra-low-current ordinary control"]
  UIOK["Y78B23214FP<br/>D-pad OK ultra-low-current ordinary control"]
  UIBACK["Y78B23214FP<br/>BACK ultra-low-current ordinary control"]
  UIOPT["Y78B23214FP<br/>OPT ultra-low-current ordinary control"]
  UIF1["Y78B23214FP<br/>F1 ultra-low-current ordinary control"]
  UIF2["Y78B23214FP<br/>F2 ultra-low-current ordinary control"]
  ENC["Alps Alpine EC11E18244AU<br/>36-detent/18-pulse encoder with push"]
  ENCAPU["RC0402FR-073K32L #ENC-A<br/>3.32-kOhm encoder-phase-A contact-current pull-up"]
  ENCBPU["RC0402FR-073K32L #ENC-B<br/>3.32-kOhm encoder-phase-B contact-current pull-up"]
  ENCPTTESD["TPD4E05U06DQAR<br/>four-channel encoder/PTT ESD array"]
  PTTPU["RC0402FR-0710KL<br/>10-kOhm direct-PTT pull-up"]
  PTTR["RC0603FR-071KL<br/>1-kOhm direct-PTT input series resistor"]
  PTTC["C1005X7R1H104K050BB<br/>100-nF direct-PTT hardware filter"]
  PTTRAW(("PTT_BUTTON_RAW_N<br/>active-low direct-PTT node"))
  TPIRQ["SN74LVC1G07DCKR<br/>open-drain touch-interrupt adapter"]
  TPIRQPU["RC0402FR-0710KL<br/>10-kOhm active-low TP_INT raw pull-up"]
  TPIRQRAW(("LCD_TOUCH_INT_RAW_N<br/>active-low ST77922 touch node"))
  TPIRQBP["C1005X7R1H104K050BB #TP-IRQ<br/>100-nF touch-IRQ adapter bypass capacitor"]
  LCDCON["FH12-40S-0.5SH(55)<br/>first 40-position 0.5-mm bottom-contact ZIF panel-mate candidate"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  LCDTDDI["Sitronix ST77922<br/>integrated display and capacitive-touch TDDI COG"]
  LCDLBULK["GRM188R60J106ME47D #LCD-LOGIC<br/>10-uF protected-main display-logic bulk capacitor"]
  LCDLHF["C1005X7R1H104K050BB #LCD-LOGIC<br/>100-nF display-logic high-frequency bypass capacitor"]
  LCDRPD["RC0402FR-0710KL #LCD-RESX<br/>10-kOhm display reset-default pull-down"]
  TPRPD["RC0402FR-0710KL #TP-RESXP<br/>10-kOhm touch reset-default pull-down"]
  BLEFUSE["TPS2553DRVR-1<br/>latch-off and reverse-blocking LEDA power switch"]
  BLILIM["RC0402FR-07133KL<br/>133-kOhm 1% approximately 200-mA backlight-limit resistor"]
  BLIN["C1005X7R1H104K050BB #BL-IN<br/>100-nF backlight-switch input bypass capacitor"]
  BLOUT["GRM188R60J106ME47D #BL-OUT<br/>10-uF protected-LEDA output bulk capacitor"]
  BLOUTHF["C1005X7R1H104K050BB #BL-OUT<br/>100-nF protected-LEDA output bypass capacitor"]
  BLFPU["RC0402FR-0710KL #BL-FAULT<br/>10-kOhm open-drain backlight-fault pull-up"]
  BLR["ERJ-P08F10R0V<br/>10-Ohm 0.66-W anti-surge LED cathode resistor"]
  BLQ["DMN2056U-7 #BACKLIGHT<br/>low-gate-drive LED cathode PWM MOSFET"]
  BLGR["RC0402FR-07100RL #BL-GATE<br/>100-Ohm PWM gate series resistor"]
  BLGPD["RC0402FR-0710KL #BL-GATE<br/>10-kOhm PWM gate reset-off pull-down"]
  SD["DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SDHBUF["SN74LVC3G34DCUR<br/>three-channel Ioff SCK/CMD/CS card-side buffer"]
  SDMBUF["SN74LVC1G125DCKR<br/>CS-gated Ioff DAT0/MISO return buffer"]
  SDESDA["TPD4E05U06DQAR #SD-A<br/>four-channel microSD signal ESD array"]
  SDESDB["TPD4E05U06DQAR #SD-B<br/>four-channel microSD supply/signal/detect ESD array"]
  SDINCAP["C1608X7R1C105K080AC #SD-IN<br/>1-uF storage-switch input bypass capacitor"]
  SDBULK["GRM21BR60J226ME39L<br/>22-uF switched-card bulk capacitor"]
  SDHFCAP["C1005X7R1H104K050BB #SD-RAIL<br/>100-nF switched-card bypass capacitor"]
  SDHBUFCAP["C1005X7R1H104K050BB #SD-HOST-BUF<br/>100-nF triple-buffer bypass capacitor"]
  SDMBUFCAP["C1005X7R1H104K050BB #SD-MISO-BUF<br/>100-nF return-buffer bypass capacitor"]
  SDONPD["RC0402FR-0710KL #SD-ON<br/>10-kOhm storage-power reset-off pull-down"]
  SDSCKPD["RC0402FR-0710KL #SD-SCK<br/>10-kOhm shared-clock reset-low pull-down"]
  SDD0PU["RC0402FR-0710KL #SD-D0<br/>10-kOhm shared-D0 reset-high pull-up"]
  SDD1PU["RC0402FR-0710KL #SD-D1<br/>10-kOhm shared-D1 reset-high pull-up"]
  SDHCS["RC0402FR-0710KL #SD-CS<br/>10-kOhm card-CS reset-high pull-up"]
  LCDHCS["RC0402FR-0710KL #LCD-CS<br/>10-kOhm display-CS reset-high pull-up"]
  SDCPUCMD["RC0402FR-0710KL #SD-CMD<br/>10-kOhm switched-card CMD pull-up"]
  SDCPUD0["RC0402FR-0710KL #SD-DAT0<br/>10-kOhm switched-card DAT0 pull-up"]
  SDCPUD1["RC0402FR-0710KL #SD-DAT1<br/>10-kOhm switched-card DAT1 pull-up"]
  SDCPUD2["RC0402FR-0710KL #SD-DAT2<br/>10-kOhm switched-card DAT2 pull-up"]
  SDCPUD3["RC0402FR-0710KL #SD-DAT3<br/>10-kOhm switched-card DAT3/CS pull-up"]
  SDSCKR["ERJ-2RKF22R0X #SD-SCK<br/>22-Ohm buffered-card clock series resistor"]
  SDCMDR["ERJ-2RKF22R0X #SD-CMD<br/>22-Ohm buffered-card CMD series resistor"]
  SDCSR["ERJ-2RKF22R0X #SD-CS<br/>22-Ohm buffered-card CS series resistor"]
  SDMISOR["ERJ-2RKF22R0X #SD-MISO<br/>22-Ohm return-buffer series resistor"]
  SDDETR["RC0603FR-071KL #SD-DETECT<br/>1-kOhm card-detect input series resistor"]
  SDDETPU["RC0402FR-0710KL #SD-DETECT<br/>10-kOhm always-readable card-detect pull-up"]
  SDDETC["C1005X7R1H104K050BB #SD-DETECT<br/>100-nF card-detect hardware filter capacitor"]
  SI["Si4732-A10-GSR<br/>AM/FM/SW/LW broadcast receiver"]
  RXCLK["Q13FC13500005<br/>32.768-kHz receiver crystal"]
  RXCLKC0["GRM1555C1H220JA01D #RX-RCLK<br/>22-pF receiver crystal capacitor"]
  RXCLKC1["GRM1555C1H220JA01D #RX-GPO3<br/>22-pF receiver crystal capacitor"]
  RXSUP["TPS3839K33DBZR #RX<br/>3.08-V 200-ms receiver supervisor"]
  RXI2C["SN74LVC2G66DCUR #RX-I2C<br/>receiver I²C power isolation"]
  RXFMESD["SESD0402X1UN-0020-090 #RX-FM/SW<br/>0.2-pF RF ESD shunt"]
  RXFML["LQW15AN56NJ00D<br/>56-nH high-Q FM first target on FM/SW port"]
  RXFMC["GRM1555C1H102JA01D<br/>1-nF C0G FMI coupling capacitor"]
  RXFMSMA["MPN TBD after mechanics<br/>dedicated FM/SW standard-SMA receive endpoint"]
  RXAMESD["SESD0402X1UN-0020-090 #RX-AM/LW<br/>0.2-pF RF ESD shunt"]
  RXAMC["GRM155R71A474KE01D<br/>0.47-uF AMI coupling capacitor"]
  RXAMSMA["MPN TBD after mechanics<br/>dedicated non-50-Ohm AM/LW loop-pod standard-SMA endpoint"]
  CODEC["Everest Semiconductor ES8311<br/>mono ADC/DAC audio codec"]
  CODECSUP["TPS3839K33DBZR #CODEC<br/>3.08-V 200-ms codec-interface supervisor"]
  CODECI2C["SN74LVC2G66DCUR #ES8311-I2C<br/>codec I²C power isolation"]
  CODECBCLK["SN74LVC1G126DCKR #BCLK<br/>physical codec BCLK isolation buffer"]
  CODECWS["SN74LVC1G126DCKR #WS<br/>physical codec word-select isolation buffer"]
  CODECDOUT["SN74LVC1G126DCKR #DOUT<br/>physical codec playback-data isolation buffer"]
  CODECDIN["SN74LVC1G126DCKR #DIN<br/>physical codec capture-data isolation buffer"]
  RXMUX["SN74LVC1G3157DBVR<br/>receive-audio source selector"]
  CAPSEL["TS5A63157DCKR #CAPTURE<br/>RX/microphone recording-source selector"]
  BUF["TLV9061IDBVR<br/>active high-impedance capture buffer"]
  SPKSEL["TMUX1136DGSR<br/>dual differential speaker-path selector"]
  TXSEL["TS5A63157DCKR #TX<br/>electret/codec transmit-audio selector"]
  SAFE["SN74LVC2G08DCUR<br/>reset-safe selector-request gate"]
  PAM["PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPKBEADP["BLM18PG181SN1D #SPK-P<br/>positive class-D output EMI bead"]
  SPKBEADN["BLM18PG181SN1D #SPK-N<br/>negative class-D output EMI bead"]
  SPK["AS02404PO<br/>24 × 12 mm, 4-Ohm, 2-W internal loudspeaker"]
  MIC["CMEJ-0413-42-SMT-TR<br/>top-port analog electret microphone"]
  MICFILT["RC0402FR-07220RL<br/>220-Ohm microphone-bias filter resistor"]
  AGNDLINK["RC0402JR-070RL<br/>single audio-to-power-ground star link"]
  HPJACK["SJ1-3515-SMT-TR<br/>3.5-mm stereo headphone jack with insertion switches"]
  HPESD["TPD4E05U06DQAR #HEADPHONE<br/>headphone tip/ring IEC-ESD array"]
  S3RFJ["Hirose U.FL-R-SMT-1(10)<br/>S3 module-jumper board receptacle"]
  S3CPL["KYOCERA AVX CP0603Q5425ENTR #S3<br/>S3 2.4-GHz forward-power directional coupler"]
  S3TERM["Yageo RC0402FR-0749R9L #S3<br/>S3 coupler 49.9-Ohm termination"]
  S3CIN["Murata GRM1555C1H390JA01D #S3<br/>S3 detector 39-pF RF-input DC block"]
  S3RFB["Yageo RC0402FR-0710KL #S3-FB<br/>S3 detector gain feedback resistor"]
  S3RGB["Yageo RC0402FR-0710KL #S3-GND<br/>S3 detector gain ground resistor"]
  S3COUT["KEMET C0402C330J5GACTU #S3<br/>S3 detector 33-pF output-load capacitor"]
  S3BP["TDK C1005X7R1H104K050BB #S3-DET<br/>S3 detector 100-nF local bypass capacitor"]
  C5RFJ["Hirose U.FL-R-SMT-1(10)<br/>C5 module-jumper board receptacle"]
  C5CPL["KYOCERA AVX CP0603Q5425ENTR #C5<br/>C5 2.4/5-GHz forward-power directional coupler"]
  C5TERM["Yageo RC0402FR-0749R9L #C5<br/>C5 coupler 49.9-Ohm termination"]
  C5CIN["Murata GRM1555C1H390JA01D #C5<br/>C5 detector 39-pF RF-input DC block"]
  C5RFB["Yageo RC0402FR-0710KL #C5-FB<br/>C5 detector gain feedback resistor"]
  C5RGB["Yageo RC0402FR-0710KL #C5-GND<br/>C5 detector gain ground resistor"]
  C5COUT["KEMET C0402C330J5GACTU #C5<br/>C5 detector 33-pF output-load capacitor"]
  C5BP["TDK C1005X7R1H104K050BB #C5-DET<br/>C5 detector 100-nF local bypass capacitor"]
  NRF0["E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  N0HB["74LVC126APW,118 #nRF0<br/>CE/CSN/SCK/MOSI switched-rail Ioff buffer"]
  N1HB["74LVC126APW,118 #nRF1<br/>CE/CSN/SCK/MOSI switched-rail Ioff buffer"]
  N2HB["74LVC126APW,118 #nRF2<br/>CE/CSN/SCK/MOSI switched-rail Ioff buffer"]
  N0RB["74LVC2G126DC,125 #nRF0<br/>MISO/IRQ switched-rail Ioff buffer"]
  N1RB["74LVC2G126DC,125 #nRF1<br/>MISO/IRQ switched-rail Ioff buffer"]
  N2RB["74LVC2G126DC,125 #nRF2<br/>MISO/IRQ switched-rail Ioff buffer"]
  N0CPL["DC2337J5010AHF #nRF0<br/>2.0-4.0-GHz 10-dB forward-power coupler"]
  N1CPL["DC2337J5010AHF #nRF1<br/>2.0-4.0-GHz 10-dB forward-power coupler"]
  N2CPL["DC2337J5010AHF #nRF2<br/>2.0-4.0-GHz 10-dB forward-power coupler"]
  N0TERM["RC0402FR-0749R9L #nRF0<br/>coupler isolated-port 49.9-Ohm termination"]
  N1TERM["RC0402FR-0749R9L #nRF1<br/>coupler isolated-port 49.9-Ohm termination"]
  N2TERM["RC0402FR-0749R9L #nRF2<br/>coupler isolated-port 49.9-Ohm termination"]
  N0MATCH["RC0402FR-0752R3L #nRF0<br/>AD8314 broadband 52.3-Ohm input match"]
  N1MATCH["RC0402FR-0752R3L #nRF1<br/>AD8314 broadband 52.3-Ohm input match"]
  N2MATCH["RC0402FR-0752R3L #nRF2<br/>AD8314 broadband 52.3-Ohm input match"]
  NEVD["BAT54-7-F #nRF-EVIDENCE<br/>actual-TX evidence hold isolation diode"]
  NEVC["C1608X7R1C105K080AC #nRF-EVIDENCE<br/>1-uF actual-TX evidence hold capacitor"]
  NEVR["RC0402FR-0710KL #nRF-EVIDENCE<br/>10-kOhm evidence hold discharge resistor"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  CCHB["74LVC126APW,118 #CC-HOST<br/>SCLK/SI/CSN switched-rail Ioff buffer"]
  CCRB["74LVC126APW,118 #CC-RETURN<br/>SO/GDO0/GDO2 switched-rail Ioff buffer"]
  CCBAND["74LVC2G126DC,125 #CC-BAND<br/>rail-off V1/V2 band-control Ioff buffer"]
  CCHBBP["C1005X7R1H104K050BB #CC-HOST<br/>host-buffer local bypass capacitor"]
  CCRBBP["C1005X7R1H104K050BB #CC-RETURN<br/>return-buffer local bypass capacitor"]
  CCBANDBP["C1005X7R1H104K050BB #CC-BAND<br/>band-buffer local bypass capacitor"]
  CCPIN["C1608X7R1C105K080AC #CC-IN<br/>CC load-switch input bypass capacitor"]
  CCBULK["C1608X7R1C105K080AC #CC-LOCAL<br/>CC switched-rail local bulk capacitor"]
  CCONPD["RC0402FR-0710KL #CC-ON<br/>CC load-switch reset-off resistor"]
  CCDVBP["C1005X7R1H104K050BB #CC-DVDD<br/>CC1101 DVDD bypass capacitor"]
  CC9BP["C1005X7R1H104K050BB #CC-AVDD9<br/>CC1101 AVDD9 bypass capacitor"]
  CC11BP["C1005X7R1H104K050BB #CC-AVDD11<br/>CC1101 AVDD11 bypass capacitor"]
  CC14BP["C1005X7R1H104K050BB #CC-AVDD14<br/>CC1101 AVDD14 bypass capacitor"]
  CC15BP["C1005X7R1H104K050BB #CC-AVDD15<br/>CC1101 AVDD15 bypass capacitor"]
  CCDCOUPL["C1005X7R1H104K050BB #CC-DCOUPL<br/>CC1101 DCOUPL capacitor"]
  CCRBIAS["RC0402FR-0756KL<br/>CC1101 56-kOhm RBIAS resistor"]
  CCXTAL["ABM8-26.000MHZ-10-D-1-G-T<br/>CC1101 exact 26-MHz reference crystal"]
  CCX1C["GJM1555C1H150JB01D #CC-X1<br/>CC crystal Q1 15-pF load capacitor"]
  CCX2C["GJM1555C1H150JB01D #CC-X2<br/>CC crystal Q2 15-pF load capacitor"]
  CCRSCLK["ERJ-2RKF22R0X #CC-SCLK<br/>SCLK source-series resistor"]
  CCRSI["ERJ-2RKF22R0X #CC-SI<br/>SI source-series resistor"]
  CCRCSN["ERJ-2RKF22R0X #CC-CSN<br/>CSN source-series resistor"]
  CCRSO["ERJ-2RKF22R0X #CC-SO<br/>SO return-source resistor"]
  CCRG0["ERJ-2RKF22R0X #CC-GDO0<br/>GDO0 return-source resistor"]
  CCRG2["ERJ-2RKF22R0X #CC-GDO2<br/>GDO2 return-source resistor"]
  CCRV1["ERJ-2RKF22R0X #CC-V1<br/>band-V1 source-series resistor"]
  CCRV2["ERJ-2RKF22R0X #CC-V2<br/>band-V2 source-series resistor"]
  CCPDSCLK["RC0402FR-0710KL #CC-SCLK<br/>host SCLK fail-low resistor"]
  CCPDSI["RC0402FR-0710KL #CC-SI<br/>host SI fail-low resistor"]
  CCPCS["RC0402FR-0710KL #CC-CSN<br/>host CSN fail-high resistor"]
  CCPDSO["RC0402FR-0710KL #CC-SO<br/>host SO fail-low resistor"]
  CCPDG0["RC0402FR-0710KL #CC-GDO0<br/>host GDO0 fail-low resistor"]
  CCPDG2["RC0402FR-0710KL #CC-GDO2<br/>host GDO2 fail-low resistor"]
  CCPDV1H["RC0402FR-0710KL #CC-V1-HOST<br/>band-V1 host fail-low resistor"]
  CCPDV2H["RC0402FR-0710KL #CC-V2-HOST<br/>band-V2 host fail-low resistor"]
  CCPDV1A["RC0402FR-0710KL #CC-V1-A<br/>switch-A V1 isolation-default resistor"]
  CCPDV2A["RC0402FR-0710KL #CC-V2-A<br/>switch-A V2 isolation-default resistor"]
  CCPDV1B["RC0402FR-0710KL #CC-V1-B<br/>switch-B V1 isolation-default resistor"]
  CCPDV2B["RC0402FR-0710KL #CC-V2-B<br/>switch-B V2 isolation-default resistor"]
  CCCP["GJM1555C1H101JB01D #CC-RF-P<br/>RF_P high-Q 100-pF DC block"]
  CCCN["GJM1555C1H101JB01D #CC-RF-N<br/>RF_N high-Q 100-pF DC block"]
  CCDIFF["GJM1555C1HR60BB01D<br/>0.6-pF differential RF trim capacitor"]
  CCBAL["B0310J50100AHF<br/>300-MHz-to-1-GHz 50-to-100-Ohm balun"]
  CCL33["LQG15HS3N3S02D<br/>balun-output 3.3-nH series match"]
  CCC12["GJM1555C1H1R2BB01D<br/>balun-output 1.2-pF shunt match"]
  CCL68["LQG15HS6N8J02D<br/>balun-output 6.8-nH series match"]
  CCSWA["BGS13SN8E6327XTSA1 #A<br/>transceiver-side three-band SP3T isolator"]
  CCSWB["BGS13SN8E6327XTSA1 #B<br/>antenna-side three-band SP3T isolator"]
  CC315L1["LQG15HS10NJ02D #315-IN<br/>315-MHz input series inductor"]
  CC315L36["LQG15HS3N6S02D<br/>315-MHz shunt-trap inductor"]
  CC315C8["GJM1555C1H8R0DB01D<br/>315-MHz shunt-trap capacitor"]
  CC315L2["LQG15HS10NJ02D #315-OUT<br/>315-MHz output series inductor"]
  CC433C10["GJM1555C1H100JB01D<br/>433-MHz input shunt capacitor"]
  CC433L15["LQG15HS15NJ02D<br/>433-MHz series inductor"]
  CC433C62["GJM1555C1H6R2DB01D<br/>433-MHz output shunt capacitor"]
  CC868L10["LQG15HS10NJ02D #868-915<br/>combined 868/915-MHz series inductor"]
  CCLOUT["LQG15HS2N2S02D<br/>selected-path output matching inductor"]
  CCESD["SESD0402X1UN-0020-090<br/>external CC RF ultra-low-capacitance ESD diode"]
  CCTAP["GJM1555C1HR47BB01D<br/>actual-TX high-impedance RF sample capacitor"]
  CCDF["GRM1555C1H121JA01D #CC-DETECT<br/>AD8314 response filter capacitor"]
  CCDBP["C1005X7R1H104K050BB #CC-DETECT<br/>AD8314 local bypass capacitor"]
  CCEVD["BAT54-7-F #CC-EVIDENCE<br/>actual-TX evidence hold isolation diode"]
  CCEVC["C1608X7R1C105K080AC #CC-EVIDENCE<br/>actual-TX evidence hold capacitor"]
  CCEVR["RC0402FR-0710KL #CC-EVIDENCE<br/>actual-TX evidence hold discharge resistor"]
  CCSMA["MPN TBD after mechanics<br/>CC dedicated external standard-SMA endpoint"]
  SA["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  VOICESUP["TPS3808G33DBVR #VOICE<br/>STOP-qualified protected-4-V voice supervisor"]
  VOICEIOSW["TPS22919DCKR #VOICE-IO<br/>discharged local voice-interface supply switch"]
  VOICEPTT["SN74LVC1G126DCKR #VOICE-PTT<br/>physical module-PTT isolation buffer"]
  VOICEUART["SN74LVC1G126DCKR #VOICE-UART<br/>physical host-to-module UART isolation buffer"]
  VOICEHL["SN74LVC1G07DCKR #VOICE-HL<br/>low-or-open SA518 H/L driver"]
  VOICEAUDIO["SN74LVC2G66DCUR #VOICE-AUDIO<br/>dual AFOUT/MIC_IN domain-isolation switch"]
  VOICEESD["PESD24VY1BSF<br/>24-V 0.17-pF external voice RF ESD diode"]
  VOICETAP["RC0402FR-075K1L<br/>actual-TX 5.1-kOhm RF series sampler"]
  VOICEMATCH["RC0402FR-0752R3L<br/>AD8314 52.3-Ohm detector input shunt"]
  VOICEDF["GRM1555C1H121JA01D #VOICE-DETECT<br/>AD8314 response filter capacitor"]
  VOICEDBP["C1005X7R1H104K050BB #VOICE-DETECT<br/>AD8314 local bypass capacitor"]
  VOICEEVD["BAT54-7-F #VOICE-EVIDENCE<br/>actual-TX evidence hold isolation diode"]
  VOICEEVC["C1608X7R1C105K080AC #VOICE-EVIDENCE<br/>actual-TX evidence hold capacitor"]
  VOICEEVR["RC0402FR-0710KL #VOICE-EVIDENCE<br/>actual-TX evidence hold discharge resistor"]
  VOICESMA["MPN TBD after mechanics<br/>voice dedicated external standard-SMA endpoint"]
  CAPDOCK["MPN TBD<br/>2×7 female 2.54-mm host Cap-Bus receptacle"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  UISOBP["C1005X7R1H104K050BB #U214-I2C<br/>TCA4307 bypass capacitor"]
  UISDAPU["RC0402FR-072K2L #U214-SDA<br/>controller-side I2C pull-up resistor"]
  UISCLPU["RC0402FR-072K2L #U214-SCL<br/>controller-side I2C pull-up resistor"]
  UHBA["74LVC126APW,118 #U214-HOST-A<br/>RST/GPS-RX/SCK/MOSI Ioff buffer"]
  UHBB["74LVC126APW,118 #U214-HOST-B<br/>NSS and disabled-spare Ioff buffer"]
  URB["74LVC126APW,118 #U214-RETURN<br/>BUSY/IRQ/GPS-TX/MISO Ioff buffer"]
  UHBABP["C1005X7R1H104K050BB #U214-HOST-A<br/>host-buffer bypass capacitor"]
  UHBBBP["C1005X7R1H104K050BB #U214-HOST-B<br/>host-buffer bypass capacitor"]
  URBBP["C1005X7R1H104K050BB #U214-RETURN<br/>return-buffer bypass capacitor"]
  URSTR["ERJ-2RKF22R0X #U214-RST<br/>reset source-series resistor"]
  UGPSRR["ERJ-2RKF22R0X #U214-GPS-RX<br/>GNSS receive source-series resistor"]
  USCKR["ERJ-2RKF22R0X #U214-SCK<br/>SPI-clock source-series resistor"]
  UMOSIR["ERJ-2RKF22R0X #U214-MOSI<br/>MOSI source-series resistor"]
  UNSSR["ERJ-2RKF22R0X #U214-NSS<br/>NSS source-series resistor"]
  UBUSYR["ERJ-2RKF22R0X #U214-BUSY<br/>BUSY return-series resistor"]
  UIRQR["ERJ-2RKF22R0X #U214-IRQ<br/>IRQ return-series resistor"]
  UGPSTR["ERJ-2RKF22R0X #U214-GPS-TX<br/>GNSS transmit return-series resistor"]
  UMISOR["ERJ-2RKF22R0X #U214-MISO<br/>MISO return-series resistor"]
  UESDA["TPD4E05U06DQAR #U214-A<br/>I2C/RST/GPS-RX connector ESD array"]
  UESDB["TPD4E05U06DQAR #U214-B<br/>SCK/MOSI/NSS/BUSY connector ESD array"]
  UESDC["TPD4E05U06DQAR #U214-C<br/>IRQ/GPS-TX/MISO connector ESD array"]
  EXTOR["74LVC1G32GV,125 #EXT-REQ<br/>U214/native-Unit request OR gate"]
  EXTORBP["C1005X7R1H104K050BB #EXT-REQ<br/>request-OR bypass capacitor"]
  EXTREQPD["RC0402FR-0710KL #EXT-REQ<br/>shared-5-V request fail-low resistor"]
  EXTBG["SN74LVC2G08DCUR #EXT-BRANCH<br/>dual STOP-qualified connector-branch gate"]
  EXTBGBP["C1005X7R1H104K050BB #EXT-BRANCH<br/>branch-gate bypass capacitor"]
  UREQPD["RC0402FR-0710KL #U214-REQ<br/>U214 request fail-low resistor"]
  UNITREQPD["RC0402FR-0710KL #UNIT-REQ<br/>native-Unit request fail-low resistor"]
  USUP["TPS3808G33DBVR #U214<br/>protected-5-V readiness supervisor"]
  USUPBP["C1005X7R1H104K050BB #U214-SUP<br/>supervisor bypass capacitor"]
  USUPT["RC0402FR-07110KL #U214-SENSE<br/>ready-threshold top resistor"]
  USUPB["RC0402FR-07220KL #U214-SENSE<br/>ready-threshold bottom resistor"]
  USUPC["GRM155R71H103KA88D #U214-READY<br/>readiness delay capacitor"]
  USUPPU["RC0402FR-0710KL #U214-READY<br/>main-domain READY pull-up resistor"]
  UNITEF["TPS259470LRPWR #UNIT<br/>native-Unit true-reverse-blocking latch-off eFuse"]
  UNITRILM["RC0402FR-072K21L #UNIT<br/>native-Unit current-limit resistor"]
  UNITDVDT["GRM155R71H472KA01D #UNIT<br/>native-Unit startup-slew capacitor"]
  UNITIT["GRM188R71E224KA88D #UNIT<br/>native-Unit post-start transient timer"]
  UNITOVT["RC0402FR-07169KL #UNIT<br/>native-Unit OVLO top resistor"]
  UNITOVB["RC0402FR-0747KL #UNIT<br/>native-Unit OVLO bottom resistor"]
  UNITIN["GRM21BR71E225KE11L #UNIT-IN<br/>native-Unit eFuse input capacitor"]
  UNITOUT["GRM21BR71E225KE11L #UNIT-OUT<br/>native-Unit eFuse output capacitor"]
  UNITBLEED["RC0603FR-071KL #UNIT<br/>native-Unit protected-output discharge resistor"]
  UNITSUP["TPS3808G33DBVR #UNIT<br/>protected-native-Unit-5-V readiness supervisor"]
  UNITSUPBP["C1005X7R1H104K050BB #UNIT-SUP<br/>supervisor bypass capacitor"]
  UNITSUPT["RC0402FR-07110KL #UNIT-SENSE<br/>ready-threshold top resistor"]
  UNITSUPB["RC0402FR-07220KL #UNIT-SENSE<br/>ready-threshold bottom resistor"]
  UNITSUPC["GRM155R71H103KA88D #UNIT-READY<br/>readiness delay capacitor"]
  UNITSUPPU["RC0402FR-0710KL #UNIT-READY<br/>main-domain READY pull-up resistor"]
  UNISO["TXS0102DCUR #UNIT-SIGNALS<br/>bidirectional I2C/UART/GPIO isolator"]
  UNISOA["C1005X7R1H104K050BB #UNIT-VCCA<br/>signal-isolator A-side bypass capacitor"]
  UNISOB["C1005X7R1H104K050BB #UNIT-VCCB<br/>signal-isolator B-side bypass capacitor"]
  UNISOEPD["RC0402FR-0710KL #UNIT-OE<br/>signal-isolator fail-low OE resistor"]
  UNITESD["TPD4E05U06DQAR #UNIT<br/>native-Unit connector ESD array"]
  IRSW["TPS22919DCKR #IR-RX<br/>independent reset-off receiver load switch"]
  IRINCAP["C1608X7R1C105K080AC #IR-RX-IN<br/>receiver-switch input capacitor"]
  IROUTCAP["GRM188R60J106ME47D #IR-RX-OUT<br/>switched receiver-rail bulk capacitor"]
  IROUTBP["C1005X7R1H104K050BB #IR-RX-OUT<br/>switched receiver-rail HF bypass capacitor"]
  IRONPD["RC0402FR-0710KL #IR-RX-ON<br/>receiver-rail reset-off pull-down resistor"]
  IR0["TSOP95238TT<br/>38-kHz AGC2 demodulating IR receiver"]
  IR0R["RC0402FR-07100RL #IR-DEMOD<br/>demodulator supply-filter resistor"]
  IR0C["GRM188Z71A475ME15D #IR-DEMOD<br/>demodulator supply-filter capacitor"]
  IR1["TSMP95000TT<br/>30-to-60-kHz carrier-learning IR receiver"]
  IR1R["RC0402FR-07100RL #IR-CARRIER<br/>carrier receiver supply-filter resistor"]
  IR1C["GRM188Z71A475ME15D #IR-CARRIER<br/>carrier receiver supply-filter capacitor"]
  IR1PU["RC0402FR-074K7L #IR-CARRIER<br/>carrier-output pull-up resistor"]
  IRBUF["74LVC2G126DC,125 #IR-RETURN<br/>dual switched-rail Ioff return buffer"]
  IRBUFC["C1005X7R1H104K050BB #IR-RETURN<br/>return-buffer bypass capacitor"]
  IR0SER["RC0402FR-07100RL #IR-DEMOD-OUT<br/>demodulated-envelope source resistor"]
  IR1SER["RC0402FR-07100RL #IR-CARRIER-OUT<br/>carrier-cycle source resistor"]
  IR0HPU["RC0402FR-0710KL #IR-DEMOD-HOST<br/>host-side idle-high pull-up resistor"]
  IR1HPU["RC0402FR-0710KL #IR-CARRIER-HOST<br/>host-side idle-high pull-up resistor"]
  IRTX["VSMY14940<br/>side-view 940-nm consumer IR transmit emitter"]
  IRTXRLIM["RC1206FR-0733RL #IR-TX<br/>33-Ohm emitter current-limit resistor"]
  IRTXFET["DMN2056U-7 #IR-TX<br/>STOP-qualified low-side emitter switch"]
  IRTXGS["RC0402FR-07100RL #IR-TX-GATE<br/>100-Ohm MOSFET gate resistor"]
  IRTXGPD["RC0402FR-0710KL #IR-TX-GATE<br/>10-kOhm MOSFET fail-low resistor"]
  IREVAMP["TLV9061IDBVR #IR-EVIDENCE<br/>AON physical-optical transimpedance amplifier"]
  IREVBP["C1005X7R1H104K050BB #IR-EVIDENCE<br/>amplifier bypass capacitor"]
  IREVT["RC0402FR-07100KL #IR-EVIDENCE<br/>100-kOhm reference upper resistor"]
  IREVB["RC0402FR-0710KL #IR-EVIDENCE<br/>10-kOhm reference lower resistor"]
  IREVC["C1005X7R1H104K050BB #IR-EVIDENCE<br/>reference filter capacitor"]
  IREFBR["RC0402FR-0747KL #IR-EVIDENCE<br/>47-kOhm transimpedance feedback resistor"]
  IREFBC["C0402C102K5RACTU #IR-EVIDENCE<br/>1-nF optical-response capacitor"]
  PTTSW["Y78B23214FP<br/>separate normally-open hold-to-talk PTT control"]
  STOPSW["AEQ10410<br/>gold-clad low-level normally-closed hard-STOP control"]
  REARMSW["Y78B23214FP<br/>normally-open recessed RE-ARM control"]
  STOPPU["RC0402FR-0710KL<br/>10-kOhm AON STOP contact-current pull-up"]
  STOPC["GRM155R71H103KA88D<br/>10-nF X7R asynchronous STOP filter"]
  REARMPU["RC0402FR-0747KL<br/>47-kOhm AON RE-ARM contact-current pull-up"]
  REARMC["C1005X7R1H104K050BB<br/>100-nF X7R RE-ARM filter"]
  SAFEESD["TPD4E05U06DQAR<br/>dedicated STOP/RE-ARM ESD array"]
  STOPLOOP(("STOP_LOOP_SENSE<br/>fail-open AON STOP node"))
  REARMRAW(("REARM_RAW<br/>fresh-press AON node"))
  SUP["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
  COND["74LVC2G14GW,125<br/>STOP and RE-ARM Schmitt conditioner"]
  POROR["74LVC1G32GV,125<br/>STOP-dominant POR/clear combiner"]
  LATCH["SN74LVC1G74DCUR<br/>asynchronous latched hard STOP"]
  RSTBUF["Texas Instruments SN74LVC1G06DCKR<br/>AON open-drain RUN-permit inverter"]
  RSTBUFBP["C1005X7R1H104K050BB #RESET-DRIVER<br/>AON reset-driver bypass capacitor"]
  RSTGPU["RC0402FR-0710KL #RESET-KILL<br/>main-domain fail-reset gate pull-up"]
  RSTQA["Diodes Incorporated 2N7002DW-7-F #RESET-A<br/>independent passive-drain S3/C5 reset sinks"]
  RSTQB["Diodes Incorporated 2N7002DW-7-F #RESET-B<br/>independent passive-drain RP reset sink plus inert spare"]
  S3RPU["RC0402FR-0710KL #S3-EN<br/>passive S3 EN pull-up"]
  C5RPU["RC0402FR-0710KL #C5-EN<br/>passive C5 CHIP_PU pull-up"]
  RPRPU["RC0402FR-0710KL #RP-RUN<br/>passive RP RUN pull-up"]
  GATEA["SN74LVC08APWR #1<br/>four STOP-dominant nRF request gates"]
  GATEB["SN74LVC08APWR #2<br/>four STOP-dominant rail/IR/accessory gates"]
  PTTOR["74LVC1G32GV,125 #2<br/>active-low voice PTT force-RX gate"]
  STOPLEDR["RC0402FR-072K2L #STOP<br/>2.2-kOhm physical STOP-indicator current limit"]
  STOPLED["LTST-C190KFKT<br/>orange physical latched-STOP indicator"]
  DS3["LTC5532ES6#TRMPBF #S3<br/>S3 2.4-GHz RF power detector"]
  DC5["LTC5532ES6#TRMPBF #C5<br/>C5 2.4/5-GHz RF power detector"]
  DN0["AD8314ACPZ-RL7 #nRF0<br/>100-MHz-to-2.7-GHz forward-power detector"]
  DN1["AD8314ACPZ-RL7 #nRF1<br/>100-MHz-to-2.7-GHz forward-power detector"]
  DN2["AD8314ACPZ-RL7 #nRF2<br/>100-MHz-to-2.7-GHz forward-power detector"]
  DCC["AD8314ACPZ-RL7 #CC<br/>CC1101 actual-TX RF power detector"]
  DVOICE["AD8314ACPZ-RL7 #voice<br/>SA518 VHF/UHF actual-TX RF power detector"]
  DIR["VEMD1060X01<br/>IR optical-evidence photodiode"]
  CMPA["TLV1824PWR #1<br/>S3/C5/nRF0/nRF1 AON evidence comparator"]
  CMPABP["C1005X7R1H104K050BB #CMP-A<br/>first evidence-comparator local bypass capacitor"]
  CMPB["TLV1824PWR #2<br/>nRF2/CC/voice/IR AON evidence comparator"]
  CMPBBP["C1005X7R1H104K050BB #CMP-B<br/>second evidence-comparator local bypass capacitor"]
  S3EVT["RC0402FR-07100KL #S3-EV<br/>100-kOhm first-population threshold upper resistor"]
  S3EVB["RC0402FR-0710KL #S3-EV<br/>10-kOhm first-population threshold lower resistor"]
  S3EVH["RC0402FR-071ML #S3-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  S3EVPU["RC0402FR-0710KL #S3-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  C5EVT["RC0402FR-07100KL #C5-EV<br/>100-kOhm first-population threshold upper resistor"]
  C5EVB["RC0402FR-0710KL #C5-EV<br/>10-kOhm first-population threshold lower resistor"]
  C5EVH["RC0402FR-071ML #C5-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  C5EVPU["RC0402FR-0710KL #C5-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  N0EVT["RC0402FR-07100KL #nRF0-EV<br/>100-kOhm first-population threshold upper resistor"]
  N0EVB["RC0402FR-0710KL #nRF0-EV<br/>10-kOhm first-population threshold lower resistor"]
  N0EVH["RC0402FR-071ML #nRF0-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  N0EVPU["RC0402FR-0710KL #nRF0-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  N1EVT["RC0402FR-07100KL #nRF1-EV<br/>100-kOhm first-population threshold upper resistor"]
  N1EVB["RC0402FR-0710KL #nRF1-EV<br/>10-kOhm first-population threshold lower resistor"]
  N1EVH["RC0402FR-071ML #nRF1-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  N1EVPU["RC0402FR-0710KL #nRF1-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  N2EVT["RC0402FR-07100KL #nRF2-EV<br/>100-kOhm first-population threshold upper resistor"]
  N2EVB["RC0402FR-0710KL #nRF2-EV<br/>10-kOhm first-population threshold lower resistor"]
  N2EVH["RC0402FR-071ML #nRF2-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  N2EVPU["RC0402FR-0710KL #nRF2-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  CCEVT["RC0402FR-07100KL #CC-EV<br/>100-kOhm first-population threshold upper resistor"]
  CCEVB["RC0402FR-0710KL #CC-EV<br/>10-kOhm first-population threshold lower resistor"]
  CCEVH["RC0402FR-071ML #CC-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  CCEVPU["RC0402FR-0710KL #CC-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  VOEVT["RC0402FR-07100KL #VOICE-EV<br/>100-kOhm first-population threshold upper resistor"]
  VOEVB["RC0402FR-0710KL #VOICE-EV<br/>10-kOhm first-population threshold lower resistor"]
  VOEVH["RC0402FR-071ML #VOICE-EV<br/>1-MOhm evidence-hysteresis feedback resistor"]
  VOEVPU["RC0402FR-0710KL #VOICE-EV<br/>10-kOhm AON comparator-output pull-up resistor"]
  IREVT2["RC0402FR-07100KL #IR-EV-TH<br/>100-kOhm first-population threshold upper resistor"]
  IREVB2["RC0402FR-0712KL #IR-EV-TH<br/>12-kOhm first-population threshold lower resistor"]
  IREVH["RC0402FR-071ML #IR-EV-TH<br/>1-MOhm evidence-hysteresis feedback resistor"]
  IREVPU["RC0402FR-0710KL #IR-EV-TH<br/>10-kOhm AON comparator-output pull-up resistor"]
  EVMASK["TCA9534APWR<br/>eight-bit evidence source mask on local RP I²C0"]
  EVMASKBP["C1005X7R1H104K050BB #EV-MASK<br/>evidence-mask local bypass capacitor"]
  OR0["BAT54ALT1G #0<br/>evidence diode-OR pair 0/1"]
  OR1["BAT54ALT1G #1<br/>evidence diode-OR pair 2/3"]
  OR2["BAT54ALT1G #2<br/>evidence diode-OR pair 4/5"]
  OR3["BAT54ALT1G #3<br/>evidence diode-OR pair 6/7"]
  ANYPU["RC0402FR-0710KL #ANY-TX-AON<br/>10-kOhm AON ANY-TX logic pull-up resistor"]
  ANYLEDR["RC0402FR-072K2L #ANY-TX<br/>2.2-kOhm physical indicator current limit"]
  ANYLED["LTST-C190KRKT<br/>red physical ANY-TX indicator"]
  EVISO["SN74LVC3G07DCUR<br/>triple AON-to-main open-drain evidence isolator"]
  EVISOBP["C1005X7R1H104K050BB #EV-ISO<br/>evidence-domain-isolator local bypass capacitor"]
  C5EVMPU["RC0402FR-0710KL #C5-EV-MAIN<br/>10-kOhm main-domain C5-evidence pull-up resistor"]
  IREVMPU["RC0402FR-0710KL #IR-EV-MAIN<br/>10-kOhm main-domain IR-evidence pull-up resistor"]
  RPEVMPU["RC0402FR-0710KL #RP-EV-MAIN<br/>10-kOhm main-domain RP ANY-TX pull-up resistor"]
  %% Layout-only invisible spine: these links are not electrical connections.
  USBC ~~~ PORTPROT ~~~ PORTDPR ~~~ PORTDMR ~~~ PORTVBIAS ~~~ PORTVPWR ~~~ PORTFLTPU ~~~ VBUSPROT ~~~ PDCTRL ~~~ PDCFG ~~~ PVINCAP ~~~ PL3CAP ~~~ PL1CAP ~~~ PPHVC0 ~~~ PPHVC1
  PPHVC1 ~~~ PPHVC2 ~~~ PPHVC3 ~~~ PVBUSCAP ~~~ PCC1CAP ~~~ PCC2CAP ~~~ PEECAP ~~~ PEEWPPU
  PEEWPPU ~~~ PLSCLPU ~~~ PLSDAPU ~~~ PHSCLPU ~~~ PHSDAPU ~~~ PIRQPU ~~~ CHARGER
  CHARGER ~~~ CHL ~~~ CVB0 ~~~ CVB1 ~~~ CVBHF ~~~ CPM0 ~~~ CPM1 ~~~ CPM2 ~~~ CPMHF
  CPMHF ~~~ CSYS0 ~~~ CSYS1 ~~~ CSYS2 ~~~ CSYS3 ~~~ CSYS4 ~~~ CSYSHF ~~~ CBAT0 ~~~ CBAT1
  CBAT1 ~~~ CBT1 ~~~ CBT2 ~~~ CREGN ~~~ CSDRV ~~~ CPROG ~~~ CBATP ~~~ CTSU ~~~ CTSL ~~~ CTSN
  CTSN ~~~ CILU ~~~ CILL ~~~ CINTPU ~~~ CCEPU ~~~ HOLDER ~~~ CELL0 ~~~ FUSE0 ~~~ NTC0 ~~~ CELL1 ~~~ FUSE1 ~~~ NTC1
  NTC1 ~~~ PACKGAUGE ~~~ PACKINR ~~~ PACKINC ~~~ PACKCPC ~~~ PACKAOC ~~~ PACKR3C ~~~ PACKR2C
  PACKR2C ~~~ PACKRB1 ~~~ PACKRB4 ~~~ PACKCF1 ~~~ PACKCF4 ~~~ PACKPCKR ~~~ SHUNT ~~~ PACKFET ~~~ PACKCGC ~~~ PACKDGC
  PACKDGC ~~~ PACKHOLD ~~~ PACKHOLDPU ~~~ PACKRELDPD ~~~ PACKALRTPU ~~~ PACKSTAT ~~~ PACKPFAILPU ~~~ PACKIRQPD ~~~ PACKSCLPU ~~~ PACKSDAPU
  PACKSDAPU ~~~ SUPPLYOR ~~~ SYSDIODE ~~~ PACKADM ~~~ PACKMCUBULK ~~~ PACKMCUHF ~~~ PACKRSTPU ~~~ PACKRSTC
  PACKRSTC ~~~ DIAGTMR ~~~ DIAGTR ~~~ DIAGTC ~~~ DIAGLR ~~~ DIAGLC ~~~ DIAGBP ~~~ DIAGTRPD ~~~ DIAGGPD ~~~ DIAGQ ~~~ DIAGR0 ~~~ DIAGR1
  DIAGR1 ~~~ MIDADC0 ~~~ MIDADC1 ~~~ MIDADCB ~~~ MIDADCC ~~~ STACKADC0 ~~~ STACKADC1 ~~~ STACKADC2 ~~~ STACKADC3 ~~~ STACKADC4 ~~~ STACKADCB ~~~ STACKADCC
  STACKADCC ~~~ AONBUCK ~~~ AONL ~~~ AONMODE ~~~ AONIN ~~~ AONOUT ~~~ AONFUSE ~~~ AONRILIM ~~~ AONOVT ~~~ AONOVB ~~~ AONFIN ~~~ AONFOUT ~~~ AONPGPU ~~~ PORPU
  PORPU ~~~ MAINBUCK ~~~ MAINL ~~~ MAININ ~~~ MAINHF ~~~ MAINFBT ~~~ MAINFBB ~~~ MAINFF ~~~ MAINOUT0 ~~~ MAINOUT1 ~~~ MAINFUSE ~~~ MAINRILM ~~~ MAINDVDT ~~~ MAINIT ~~~ MAINOVT ~~~ MAINOVB ~~~ MAINPGT ~~~ MAINPGB ~~~ MAINFOUT ~~~ MAINENPD ~~~ FAULTPU
  FAULTPU ~~~ VOICEBUCK ~~~ VOICEL ~~~ VOICEIN ~~~ VOICEHF ~~~ VOICEFBT ~~~ VOICEFBB ~~~ VOICEFF ~~~ VOICEOUT0 ~~~ VOICEOUT1 ~~~ VOICEFUSE ~~~ VOICERILIM ~~~ VOICEDVDT ~~~ VOICEIT ~~~ VOICEOVT ~~~ VOICEOVB ~~~ VOICEPGT ~~~ VOICEPGB ~~~ VOICEFOUT ~~~ VOICEENPD ~~~ VOICEPGPU ~~~ VOICEPGBR ~~~ VOICEPGQ
  VOICEPGQ ~~~ EXTBUCK ~~~ EXTL ~~~ EXTBUCKIN ~~~ EXTBUCKHF ~~~ EXTBUCKFBT ~~~ EXTBUCKFBB ~~~ EXTBUCKFF ~~~ EXTBUCKOUT0 ~~~ EXTBUCKOUT1 ~~~ EXTENPD ~~~ EXTPGPU ~~~ EXTPGBR ~~~ EXTPGQ ~~~ EXTFUSE ~~~ EXTRILM ~~~ EXTDVDT ~~~ EXTITIMER
  EXTITIMER ~~~ EXTOVLOT ~~~ EXTOVLOB ~~~ EXTINCAP ~~~ EXTOUTCAP ~~~ EXTBLEED ~~~ SWNRF ~~~ SWCC ~~~ SWSD ~~~ SWCODEC ~~~ SWRX ~~~ S3 ~~~ SLOW
  RP ~~~ C5USBC ~~~ C5UESD ~~~ C5UMUX ~~~ C5UMUXBP ~~~ C5CC1 ~~~ C5CC2 ~~~ C5VB ~~~ C5DMR ~~~ C5DPR ~~~ RPUSBC ~~~ RPUESD ~~~ RPUMUX ~~~ RPUMUXBP ~~~ RPCC1 ~~~ RPCC2 ~~~ RPVB ~~~ RPDMR ~~~ RPDPR
  RPDPR ~~~ S3DBG ~~~ C5DBG ~~~ RPDBG ~~~ S3DBGE ~~~ C5DBGE ~~~ RPDBGE ~~~ S3RSTSW ~~~ S3BOOTSW ~~~ C5RSTSW ~~~ C5BOOTSW ~~~ RPRSTSW ~~~ RPBOOTSW
  RPBOOTSW ~~~ S3VTR ~~~ S3RSTR ~~~ S3BOOTR ~~~ S3D0R ~~~ S3D1R ~~~ S3ID0 ~~~ S3ID1 ~~~ C5VTR ~~~ C5RSTR ~~~ C5BOOTR ~~~ C5D0R ~~~ C5D1R ~~~ C5ID0 ~~~ C5ID1
  C5ID1 ~~~ RPVTR ~~~ RPRSTR ~~~ RPBOOTR ~~~ RPD0R ~~~ RPD1R ~~~ RPID0 ~~~ RPID1 ~~~ S3BPU ~~~ C5BPU ~~~ RPBPU ~~~ C5G27PU
  SLOW ~~~ SLOWVCI ~~~ SLOWVCP ~~~ SLOWBULK ~~~ SLOWRSTPU ~~~ SLOWRST ~~~ SLOWSTOPISO ~~~ SLOWSTOPBP ~~~ SLOWSTOPPU
  SLOWSTOPPU ~~~ SLOWEVISO ~~~ SLOWEVBP ~~~ SLOWEVPU ~~~ UIMATRIX ~~~ UIMBP ~~~ UIR0PD ~~~ UIR1PD ~~~ UIR2PD ~~~ UIR3PD ~~~ UIC0PU ~~~ UIC1PU ~~~ UIC2PU ~~~ UIMESD
  UIMESD ~~~ UIDUP ~~~ UIUP ~~~ UIDDN ~~~ UIDOWN ~~~ UIDLEFT ~~~ UILEFT
  UILEFT ~~~ UIDRIGHT ~~~ UIRIGHT ~~~ UIDOK ~~~ UIOK ~~~ UIDBACK ~~~ UIBACK
  UIBACK ~~~ UIDOPT ~~~ UIOPT ~~~ UIDF1 ~~~ UIF1 ~~~ UIDF2 ~~~ UIF2
  UIF2 ~~~ UIDENC ~~~ ENC ~~~ ENCAPU ~~~ ENCBPU ~~~ ENCPTTESD ~~~ PTTPU ~~~ PTTR ~~~ PTTC ~~~ PTTRAW ~~~ TPIRQPU ~~~ TPIRQRAW ~~~ TPIRQ ~~~ TPIRQBP
  TPIRQBP ~~~ SI ~~~ RXCLK ~~~ RXCLKC0 ~~~ RXCLKC1 ~~~ RXSUP ~~~ RXI2C ~~~ RXFMESD ~~~ RXFML ~~~ RXFMC ~~~ RXFMSMA ~~~ RXAMESD ~~~ RXAMC ~~~ RXAMSMA ~~~ RXMUX ~~~ CAPSEL ~~~ BUF
  BUF ~~~ CODEC ~~~ CODECSUP ~~~ CODECI2C ~~~ CODECBCLK ~~~ CODECWS ~~~ CODECDOUT ~~~ CODECDIN ~~~ SAFE ~~~ SPKSEL ~~~ PAM
  PAM ~~~ SPKBEADP ~~~ SPKBEADN ~~~ SPK ~~~ MIC ~~~ MICFILT ~~~ AGNDLINK ~~~ HPJACK ~~~ HPESD ~~~ TXSEL
  TXSEL ~~~ SA ~~~ VOICESUP ~~~ VOICEIOSW ~~~ VOICEPTT ~~~ VOICEUART ~~~ VOICEHL ~~~ VOICEAUDIO ~~~ LCDCON ~~~ LCD ~~~ LCDTDDI ~~~ LCDLBULK ~~~ LCDLHF ~~~ LCDRPD ~~~ TPRPD ~~~ BLEFUSE ~~~ BLILIM ~~~ BLIN ~~~ BLOUT ~~~ BLOUTHF
  BLOUTHF ~~~ BLFPU ~~~ BLR ~~~ BLQ ~~~ BLGR ~~~ BLGPD ~~~ SD ~~~ SDHBUF ~~~ SDMBUF ~~~ SDESDA ~~~ SDESDB
  SDESDB ~~~ SDINCAP ~~~ SDBULK ~~~ SDHFCAP ~~~ SDHBUFCAP ~~~ SDMBUFCAP ~~~ SDONPD ~~~ SDSCKPD ~~~ SDD0PU ~~~ SDD1PU
  SDD1PU ~~~ SDHCS ~~~ LCDHCS ~~~ SDCPUCMD ~~~ SDCPUD0 ~~~ SDCPUD1 ~~~ SDCPUD2 ~~~ SDCPUD3
  SDCPUD3 ~~~ SDSCKR ~~~ SDCMDR ~~~ SDCSR ~~~ SDMISOR ~~~ SDDETR ~~~ SDDETPU ~~~ SDDETC ~~~ UNIT ~~~ C5 ~~~ IRSW ~~~ IRINCAP ~~~ IROUTCAP ~~~ IROUTBP ~~~ IRONPD
  IRONPD ~~~ IR0 ~~~ IR0R ~~~ IR0C ~~~ IR1 ~~~ IR1R ~~~ IR1C ~~~ IR1PU ~~~ IRBUF ~~~ IRBUFC ~~~ IR0SER ~~~ IR1SER ~~~ IR0HPU ~~~ IR1HPU
  IR1HPU ~~~ IRTX ~~~ IRTXRLIM ~~~ IRTXFET ~~~ IRTXGS ~~~ IRTXGPD ~~~ IREVAMP ~~~ IREVBP ~~~ IREVT ~~~ IREVB ~~~ IREVC ~~~ IREFBR ~~~ IREFBC
  IREFBC ~~~ S3RFJ ~~~ S3CPL ~~~ S3TERM ~~~ S3CIN ~~~ S3RFB ~~~ S3RGB ~~~ S3COUT ~~~ S3BP ~~~ C5RFJ ~~~ C5CPL ~~~ C5TERM ~~~ C5CIN ~~~ C5RFB ~~~ C5RGB ~~~ C5COUT ~~~ C5BP
  C5BP ~~~ RP ~~~ N0HB ~~~ NRF0 ~~~ N0RB ~~~ N0CPL ~~~ N0TERM ~~~ N0MATCH ~~~ N1HB ~~~ NRF1 ~~~ N1RB ~~~ N1CPL ~~~ N1TERM ~~~ N1MATCH ~~~ N2HB ~~~ NRF2 ~~~ N2RB ~~~ N2CPL ~~~ N2TERM ~~~ N2MATCH ~~~ NEVD ~~~ NEVC ~~~ NEVR ~~~ CC
  CC ~~~ CCHB ~~~ CCRB ~~~ CCBAND ~~~ CCHBBP ~~~ CCRBBP ~~~ CCBANDBP ~~~ CCPIN ~~~ CCBULK ~~~ CCONPD ~~~ CCDVBP ~~~ CC9BP ~~~ CC11BP ~~~ CC14BP ~~~ CC15BP ~~~ CCDCOUPL ~~~ CCRBIAS ~~~ CCXTAL ~~~ CCX1C ~~~ CCX2C
  CCX2C ~~~ CCRSCLK ~~~ CCRSI ~~~ CCRCSN ~~~ CCRSO ~~~ CCRG0 ~~~ CCRG2 ~~~ CCRV1 ~~~ CCRV2 ~~~ CCPDSCLK ~~~ CCPDSI ~~~ CCPCS ~~~ CCPDSO ~~~ CCPDG0 ~~~ CCPDG2 ~~~ CCPDV1H ~~~ CCPDV2H ~~~ CCPDV1A ~~~ CCPDV2A ~~~ CCPDV1B ~~~ CCPDV2B
  CCPDV2B ~~~ CCCP ~~~ CCCN ~~~ CCDIFF ~~~ CCBAL ~~~ CCL33 ~~~ CCC12 ~~~ CCL68 ~~~ CCSWA ~~~ CC315L1 ~~~ CC315L36 ~~~ CC315C8 ~~~ CC315L2 ~~~ CC433C10 ~~~ CC433L15 ~~~ CC433C62 ~~~ CC868L10 ~~~ CCSWB ~~~ CCLOUT ~~~ CCESD ~~~ CCTAP ~~~ CCDF ~~~ CCDBP ~~~ CCEVD ~~~ CCEVC ~~~ CCEVR ~~~ CCSMA ~~~ SA
  SA ~~~ ISO ~~~ UISOBP ~~~ UISDAPU ~~~ UISCLPU ~~~ EXTOR ~~~ EXTORBP ~~~ EXTREQPD ~~~ EXTBG ~~~ EXTBGBP ~~~ UREQPD ~~~ UNITREQPD
  UNITREQPD ~~~ USUP ~~~ USUPBP ~~~ USUPT ~~~ USUPB ~~~ USUPC ~~~ USUPPU ~~~ UHBA ~~~ UHBABP ~~~ UHBB ~~~ UHBBBP ~~~ URB ~~~ URBBP
  URBBP ~~~ URSTR ~~~ UGPSRR ~~~ USCKR ~~~ UMOSIR ~~~ UNSSR ~~~ UBUSYR ~~~ UIRQR ~~~ UGPSTR ~~~ UMISOR ~~~ UESDA ~~~ UESDB ~~~ UESDC
  UESDC ~~~ CAPDOCK ~~~ U214 ~~~ UNITEF ~~~ UNITRILM ~~~ UNITDVDT ~~~ UNITIT ~~~ UNITOVT ~~~ UNITOVB ~~~ UNITIN ~~~ UNITOUT ~~~ UNITBLEED
  UNITBLEED ~~~ UNITSUP ~~~ UNITSUPBP ~~~ UNITSUPT ~~~ UNITSUPB ~~~ UNITSUPC ~~~ UNITSUPPU ~~~ UNISO ~~~ UNISOA ~~~ UNISOB ~~~ UNISOEPD ~~~ UNITESD ~~~ UNIT
  UNIT ~~~ PTTSW ~~~ STOPSW ~~~ REARMSW ~~~ STOPPU ~~~ STOPC ~~~ REARMPU ~~~ REARMC ~~~ SAFEESD
  SAFEESD ~~~ STOPLOOP ~~~ REARMRAW ~~~ SUP ~~~ COND ~~~ POROR ~~~ LATCH ~~~ RSTBUF
  RSTBUF ~~~ RSTBUFBP ~~~ RSTGPU ~~~ RSTQA ~~~ RSTQB ~~~ S3RPU ~~~ C5RPU ~~~ RPRPU ~~~ GATEA ~~~ GATEB ~~~ PTTOR ~~~ STOPLEDR ~~~ STOPLED
  STOPLED ~~~ DS3 ~~~ DC5 ~~~ DN0 ~~~ DN1 ~~~ DN2
  DN2 ~~~ DCC ~~~ VOICEESD ~~~ VOICETAP ~~~ VOICEMATCH ~~~ VOICEDF ~~~ VOICEDBP ~~~ VOICEEVD ~~~ VOICEEVC ~~~ VOICEEVR ~~~ VOICESMA ~~~ DVOICE ~~~ DIR ~~~ CMPA ~~~ CMPABP ~~~ CMPB ~~~ CMPBBP
  CMPBBP ~~~ S3EVT ~~~ S3EVB ~~~ S3EVH ~~~ S3EVPU ~~~ C5EVT ~~~ C5EVB ~~~ C5EVH ~~~ C5EVPU ~~~ N0EVT ~~~ N0EVB ~~~ N0EVH ~~~ N0EVPU
  N0EVPU ~~~ N1EVT ~~~ N1EVB ~~~ N1EVH ~~~ N1EVPU ~~~ N2EVT ~~~ N2EVB ~~~ N2EVH ~~~ N2EVPU ~~~ CCEVT ~~~ CCEVB ~~~ CCEVH ~~~ CCEVPU
  CCEVPU ~~~ VOEVT ~~~ VOEVB ~~~ VOEVH ~~~ VOEVPU ~~~ IREVT2 ~~~ IREVB2 ~~~ IREVH ~~~ IREVPU ~~~ EVMASK ~~~ EVMASKBP ~~~ OR0 ~~~ OR1 ~~~ OR2 ~~~ OR3
  OR3 ~~~ ANYPU ~~~ ANYLEDR ~~~ ANYLED ~~~ EVISO ~~~ EVISOBP ~~~ C5EVMPU ~~~ IREVMPU ~~~ RPEVMPU
  USBC -->|"raw VBUS to VBUS + VBUS_IN"| PDCTRL
  USBC -->|"VBUS shunt"| VBUSPROT
  USBC <-->|"CC1/CC2 + D+/D-"| PORTPROT
  PORTPROT <-->|"protected D+"| PORTDPR <-->|"Full-Speed GPIO20"| S3
  PORTPROT <-->|"protected D-"| PORTDMR <-->|"Full-Speed GPIO19"| S3
  PORTPROT <-->|"protected CC1/CC2"| PDCTRL
  C5USBC -.->|"D+/D- ESD shunt"| C5UESD
  C5USBC <-->|"data; VBUS sense-only"| C5UMUX <-->|"22 Ω D+/D-"| C5
  RPUSBC -.->|"D+/D- ESD shunt"| RPUESD
  RPUSBC <-->|"data; VBUS sense-only"| RPUMUX <-->|"27 Ω D+/D-"| RP
  S3DBG -.->|"four-line ESD"| S3DBGE <-->|"UART0 + RESET/BOOT"| S3
  C5DBG -.->|"four-line ESD"| C5DBGE <-->|"UART0 + RESET/BOOT"| C5
  RPDBG -.->|"four-line ESD"| RPDBGE <-->|"SWD + RUN/BOOT"| RP
  PORTPROT -->|"100-nF / 100-V bias"| PORTVBIAS
  PDCTRL -->|"LDO_3V3"| PORTVPWR --> PORTPROT
  PDCTRL --> PORTFLTPU --> PORTPROT
  PDCTRL <-->|"local I²C boot image"| PDCFG
  PDCTRL <-->|"protected VBUS + local I²C/IRQ"| CHARGER
  S3 <-->|"SYS I²C0 + shared wired-low IRQ"| PDCTRL
  PDCTRL -->|"VIN_3V3 / internal LDO energy"| PVINCAP
  PDCTRL --> PL3CAP
  PDCTRL --> PL1CAP
  PDCTRL -->|"88-uF nominal PPHV bank"| PPHVC0
  PDCTRL --> PPHVC1
  PDCTRL --> PPHVC2
  PDCTRL --> PPHVC3
  PDCTRL -->|"dead-battery VBUS energy"| PVBUSCAP
  PDCTRL -->|"CC1 / CC2 shunts"| PCC1CAP
  PDCTRL --> PCC2CAP
  PDCTRL -->|"EEPROM supply bypass"| PEECAP --> PDCFG
  PDCTRL -->|"reset-high open-drain WP"| PEEWPPU --> PDCFG
  PDCTRL -->|"complete local I²C pull-ups"| PLSCLPU --> PDCFG
  PDCTRL --> PLSDAPU --> CHARGER
  S3 -->|"complete host I²C/IRQ pull-ups"| PHSCLPU --> PDCTRL
  S3 --> PHSDAPU --> PDCTRL
  S3 --> PIRQPU --> PDCTRL
  CHARGER -->|"SW1/SW2"| CHL
  CHARGER -->|"VBUS bulk/HF"| CVB0
  CHARGER --> CVB1
  CHARGER --> CVBHF
  CHARGER -->|"PMID bulk/HF"| CPM0
  CHARGER --> CPM1
  CHARGER --> CPM2
  CHARGER --> CPMHF
  CHARGER -->|"SYS bulk/HF"| CSYS0
  CHARGER --> CSYS1
  CHARGER --> CSYS2
  CHARGER --> CSYS3
  CHARGER --> CSYS4
  CHARGER --> CSYSHF
  CHARGER -->|"BAT bulk"| CBAT0
  CHARGER --> CBAT1
  CHARGER -->|"BTST1/SW1"| CBT1
  CHARGER -->|"BTST2/SW2"| CBT2
  CHARGER -->|"REGN"| CREGN
  CHARGER -->|"SDRV to ground"| CSDRV
  CHARGER -->|"2S/750-kHz POR"| CPROG
  PACKFET -->|"admitted BATP sense"| CBATP --> CHARGER
  CHARGER -->|"direct non-ignored TS"| CTSU --> CTSN
  CTSN --> CTSL
  CHARGER -->|"2.71…3.29-A hardware ceiling"| CILU --> CILL
  PDCTRL --> CINTPU --> CHARGER
  CHARGER -->|"REGN reset-high CE"| CCEPU --> CHARGER
  CELL0 -->|"polarized slot 0"| HOLDER
  CELL1 -->|"polarized slot 1"| HOLDER
  HOLDER -->|"independent slot-0 contacts"| FUSE0 --> PACKGAUGE
  NTC0 -->|"TH1"| PACKGAUGE
  HOLDER -->|"independent slot-1 contacts"| FUSE1 --> PACKGAUGE
  NTC1 -->|"TH2"| PACKGAUGE
  NTC0 -.->|"insulated compliant mid-can contact"| CELL0
  NTC1 -.->|"insulated compliant mid-can contact"| CELL1
  CTSN -.->|"one indexed thermally worst-slot contact"| HOLDER
  FUSE1 -->|"fused stack positive"| PACKINR --> PACKGAUGE
  PACKGAUGE --> PACKINC
  PACKGAUGE -->|"CP to IN"| PACKCPC
  PACKGAUGE -->|"AOLDO/REG3/REG2 local bypass"| PACKAOC
  PACKGAUGE --> PACKR3C
  PACKGAUGE --> PACKR2C
  FUSE0 -->|"2S midpoint"| PACKRB1 --> PACKGAUGE
  FUSE1 -->|"top of 2S stack"| PACKRB4 --> PACKGAUGE
  PACKGAUGE -->|"CELL1 to GND"| PACKCF1
  PACKGAUGE -->|"BATTS to shorted CELL3"| PACKCF4
  SHUNT -->|"CSP/CSN Kelvin plus force path"| PACKGAUGE
  PACKGAUGE -->|"PCKP through 1 kOhm"| PACKPCKR --> PACKFET
  PACKGAUGE -->|"CHG/DIS gates; no prequal"| PACKFET
  PACKFET --> PACKCGC
  PACKFET --> PACKDGC
  PACKFET <-->|"protected 2S power boundary"| CHARGER
  PACKHOLDPU --> PACKHOLD
  PACKRELDPD --> PACKHOLD
  PACKALRTPU --> PACKGAUGE
  PACKHOLD -->|"ALRT low by default"| PACKGAUGE
  PACKADM -->|"explicit release"| PACKHOLD
  PACKGAUGE -->|"push-pull PFAIL"| PACKSTAT -->|"safe active-low status"| PACKADM
  PACKPFAILPU --> PACKSTAT
  PACKADM -->|"high means assert"| PACKSTAT -->|"passive-drain SYS_INT_N"| S3
  PACKIRQPD --> PACKSTAT
  PACKSCLPU --> PACKGAUGE
  PACKSDAPU --> PACKGAUGE
  PACKGAUGE -->|"AOLDO"| SUPPLYOR --> PACKADM
  SYSDIODE -->|"admitted 3V3"| PACKADM
  PACKADM --> PACKMCUBULK
  PACKADM --> PACKMCUHF
  PACKADM -->|"NRST"| PACKRSTPU
  PACKADM --> PACKRSTC
  PACKGAUGE <-->|"local I²C + fault"| PACKADM
  PACKADM <-->|"SYS I²C0 + shared IRQ"| S3
  PACKADM -->|"PA22 rising edge"| DIAGTMR
  PACKADM --> DIAGTRPD
  SUPPLYOR -->|"admission VDD"| DIAGTMR
  DIAGTMR -->|"169 kΩ / 220 nF; ≤50 ms"| DIAGTR --> DIAGTC
  DIAGTMR -->|"falling Q edge; ≥350-ms hardware lockout"| DIAGLR --> DIAGLC
  DIAGTMR --> DIAGBP
  DIAGTMR -->|"bounded gate pulse"| DIAGQ
  DIAGTMR --> DIAGGPD
  FUSE1 -->|"fused full stack; 10 Ω total"| DIAGR0 --> DIAGQ
  FUSE1 --> DIAGR1 --> DIAGQ
  FUSE0 --> MIDADC0 --> MIDADC1 -->|"PA25/A2"| PACKADM
  PACKADM --> MIDADCB
  PACKADM --> MIDADCC
  FUSE1 --> STACKADC0 --> STACKADC1 --> STACKADC2 --> STACKADC3 --> STACKADC4 -->|"PA26/A1"| PACKADM
  PACKADM --> STACKADCB
  PACKADM --> STACKADCC
  CHARGER -->|"SYS"| AONBUCK --> AONL -->|"AON_RAW_3V3"| AONFUSE -->|"AON_SAFE_3V3"| SUP
  AONFUSE -->|"AON_SAFE_3V3 runtime source"| PVINCAP
  AONBUCK -->|"MODE/S-CONF"| AONMODE
  CHARGER -->|"SYS local bypass"| AONIN
  AONL -->|"raw local output"| AONOUT
  AONL --> AONFIN
  AONFUSE -->|"ILIM"| AONRILIM
  AONL -->|"OVLO divider"| AONOVT --> AONOVB
  AONFUSE --> AONFOUT
  AONFUSE -->|"PG pull-up source"| AONPGPU --> AONBUCK
  AONPGPU -->|"AON_PG_N to MR_N"| SUP
  AONFUSE -->|"POR pull-up"| PORPU --> SUP
  SUP -->|"delayed POR_N enables main"| MAINBUCK
  CHARGER -->|"SYS"| MAINBUCK --> MAINL -->|"MAIN_RAW_3V3"| MAINFUSE -->|"3V3_MAIN"| S3
  CHARGER -->|"SYS local bulk"| MAININ
  CHARGER -->|"SYS local HF"| MAINHF
  MAINL -->|"feedback"| MAINFBT --> MAINFBB
  MAINL -->|"feed-forward"| MAINFF
  MAINL -->|"local output bank"| MAINOUT0
  MAINL -->|"local output bank"| MAINOUT1
  MAINFUSE -->|"ILM"| MAINRILM
  MAINFUSE -->|"dVdt"| MAINDVDT
  MAINFUSE -->|"ITIMER"| MAINIT
  MAINL -->|"OVLO divider"| MAINOVT --> MAINOVB
  MAINFUSE -->|"PGTH divider"| MAINPGT --> MAINPGB
  MAINFUSE --> MAINFOUT
  MAINBUCK -->|"100-kOhm EN fail-low"| MAINENPD
  MAINFUSE -->|"protected PG to fault aggregate"| SLOW
  MAINFUSE -->|"POWER_FAULT_N pull-up source"| FAULTPU --> SLOW
  MAINFUSE -->|"3V3_MAIN: VCCI/VCCP"| SLOW
  MAINFUSE --> SLOWVCI --> SLOW
  MAINFUSE --> SLOWVCP --> SLOW
  MAINFUSE --> SLOWBULK --> SLOW
  MAINFUSE --> SLOWRSTPU --> SLOWRST --> SLOW
  MAINFUSE --> C5
  MAINFUSE --> RP
  MAINFUSE --> SWNRF
  MAINFUSE --> SWCC
  MAINFUSE --> SWSD
  MAINFUSE --> SWCODEC
  MAINFUSE --> SWRX
  CHARGER -->|"SYS"| VOICEBUCK --> VOICEL -->|"VVOICE_RAW_4V"| VOICEFUSE -->|"protected 4.0 V"| SA
  CHARGER -->|"SYS local bulk"| VOICEIN
  CHARGER -->|"SYS local HF"| VOICEHF
  VOICEL -->|"feedback"| VOICEFBT --> VOICEFBB
  VOICEL -->|"feed-forward"| VOICEFF
  VOICEL -->|"local output bank"| VOICEOUT0
  VOICEL -->|"local output bank"| VOICEOUT1
  VOICEFUSE -->|"ILM"| VOICERILIM
  VOICEFUSE -->|"dVdt"| VOICEDVDT
  VOICEFUSE -->|"ITIMER"| VOICEIT
  VOICEL -->|"OVLO divider"| VOICEOVT --> VOICEOVB
  VOICEFUSE -->|"PGTH divider"| VOICEPGT --> VOICEPGB
  VOICEFUSE --> VOICEFOUT
  VOICEBUCK -->|"EN fail-low"| VOICEENPD
  MAINFUSE -->|"PG pull-up"| VOICEPGPU --> VOICEFUSE
  GATEB -->|"EN"| VOICEPGBR --> VOICEPGQ
  VOICEFUSE -->|"protected PG"| VOICEPGQ -->|"qualified POWER_FAULT_N"| SLOW
  CHARGER -->|"SYS"| EXTBUCK --> EXTL
  EXTL --> EXTFUSE -->|"protected U214 5.0 V"| CAPDOCK
  EXTL --> UNITEF -->|"protected native-Unit 5.0 V"| UNIT
  CHARGER -->|"SYS local bulk"| EXTBUCKIN
  CHARGER -->|"SYS local HF"| EXTBUCKHF
  EXTL -->|"feedback"| EXTBUCKFBT --> EXTBUCKFBB
  EXTL -->|"feed-forward"| EXTBUCKFF
  EXTL -->|"local output bank"| EXTBUCKOUT0
  EXTL -->|"local output bank"| EXTBUCKOUT1
  EXTBUCK -->|"EN fail-low"| EXTENPD
  MAINFUSE -->|"PG pull-up"| EXTPGPU --> EXTBUCK
  GATEB -->|"EN"| EXTPGBR --> EXTPGQ
  EXTBUCK -->|"PG"| EXTPGQ -->|"qualified POWER_FAULT_N"| SLOW
  EXTFUSE -->|"ILM"| EXTRILM
  EXTFUSE -->|"dVdt"| EXTDVDT
  EXTFUSE -->|"ITIMER"| EXTITIMER
  EXTL -->|"OVLO divider"| EXTOVLOT --> EXTOVLOB
  EXTL --> EXTINCAP
  EXTFUSE --> EXTOUTCAP
  EXTFUSE --> EXTBLEED
  SWNRF --> NRF0
  SWNRF --> N0HB
  SWNRF --> N0RB
  SWNRF --> NRF1
  SWNRF --> N1HB
  SWNRF --> N1RB
  SWNRF --> NRF2
  SWNRF --> N2HB
  SWNRF --> N2RB
  SWCC --> CC
  SWCC --> CCHB
  SWCC --> CCRB
  SWCC --> CCBAND
  SWCC --> CCSWA
  SWCC --> CCSWB
  MAINFUSE --> SDINCAP
  SWSD -->|"switched 3.3 V + QOD"| SD
  SWSD --> SDBULK
  SWSD --> SDHFCAP
  SWSD -->|"VCC with Ioff"| SDHBUF
  SWSD -->|"VCC with Ioff"| SDMBUF
  SWSD --> SDHBUFCAP
  SWSD --> SDMBUFCAP
  SDONPD -->|"reset off"| SWSD
  SWCODEC --> CODEC
  SWRX --> SI
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
  S3 <-->|"I²C0 + interrupt"| SLOW
  LATCH -->|"Q polarity preserved"| SLOWSTOPISO --> SLOW
  AONFUSE --> SLOWSTOPBP --> SLOWSTOPISO
  MAINFUSE --> SLOWSTOPPU --> SLOW
  CMPA -->|"active-low polarity preserved"| SLOWEVISO --> SLOW
  AONFUSE --> SLOWEVBP --> SLOWEVISO
  MAINFUSE --> SLOWEVPU --> SLOW
  S3 -->|"direct QSPI + touch"| LCDCON
  LCDCON <-->|"40-contact FPC; physical mate HIL open"| LCD
  LCD -->|"integrated exact COG"| LCDTDDI
  LCDTDDI -->|"TP_INT low on touch"| TPIRQRAW
  TPIRQPU -->|"10 kOhm to 3V3_MAIN"| TPIRQRAW
  TPIRQRAW --> TPIRQ -->|"open-drain SYS_INT_N"| S3
  TPIRQBP --> TPIRQ
  SLOW -->|"P06/P07 reset release"| LCDCON
  S3 <-->|"SYS I²C0 + wired-low IRQ"| UIMATRIX
  UIMBP --> UIMATRIX
  UIR0PD -->|"reset/idle low"| UIMATRIX
  UIR1PD -->|"reset/idle low"| UIMATRIX
  UIR2PD -->|"reset/idle low"| UIMATRIX
  UIR3PD -->|"reset/idle low"| UIMATRIX
  UIMATRIX --> UIMESD
  UIMATRIX --> UIDUP --> UIUP -->|"P4 column 0"| UIMATRIX
  UIMATRIX --> UIDDN --> UIDOWN -->|"P5 column 1"| UIMATRIX
  UIMATRIX --> UIDLEFT --> UILEFT -->|"P6 column 2"| UIMATRIX
  UIMATRIX --> UIDRIGHT --> UIRIGHT -->|"P4 column 0"| UIMATRIX
  UIMATRIX --> UIDOK --> UIOK -->|"P5 column 1"| UIMATRIX
  UIMATRIX --> UIDBACK --> UIBACK -->|"P6 column 2"| UIMATRIX
  UIMATRIX --> UIDOPT --> UIOPT -->|"P4 column 0"| UIMATRIX
  UIMATRIX --> UIDF1 --> UIF1 -->|"P5 column 1"| UIMATRIX
  UIMATRIX --> UIDF2 --> UIF2 -->|"P6 column 2"| UIMATRIX
  UIMATRIX --> UIDENC -->|"push"| ENC -->|"P4 column 0"| UIMATRIX
  UIC0PU --> UIMATRIX
  UIC1PU --> UIMATRIX
  UIC2PU --> UIMATRIX
  ENCAPU --> ENC
  ENCBPU --> ENC
  ENC --> ENCPTTESD
  ENC -->|"GPIO39/GPIO47 PCNT0 quadrature"| S3
  LCDRPD -->|"RESX default low"| LCDCON
  TPRPD -->|"TP_RESXP default low"| LCDCON
  MAINFUSE -->|"protected 3.3 V logic"| LCDLBULK --> LCDCON
  MAINFUSE --> LCDLHF --> LCDCON
  MAINFUSE -->|"LEDA branch"| BLEFUSE --> LCDCON
  BLEFUSE --> BLILIM
  BLEFUSE --> BLIN
  BLEFUSE --> BLOUT
  BLEFUSE --> BLOUTHF
  BLFPU --> BLEFUSE
  LCDCON -->|"3 × LEDK"| BLR --> BLQ
  S3 -->|"GPIO40 PWM"| BLGR --> BLQ
  BLGPD -->|"reset off"| BLQ
  SDSCKPD -->|"reset low"| S3
  MAINFUSE --> SDD0PU --> S3
  MAINFUSE --> SDD1PU --> S3
  MAINFUSE --> SDHCS --> S3
  MAINFUSE --> LCDHCS --> S3
  S3 -->|"shared SCK/CMD + card CS"| SDHBUF
  SDHBUF -->|"SCK"| SDSCKR --> SD
  SDHBUF -->|"CMD"| SDCMDR --> SD
  SDHBUF -->|"CS"| SDCSR --> SD
  SD -->|"DAT0 only while CS low"| SDMBUF --> SDMISOR --> S3
  S3 -->|"SD_CS_N output enable"| SDMBUF
  SWSD --> SDCPUCMD --> SD
  SWSD --> SDCPUD0 --> SD
  SWSD --> SDCPUD1 --> SD
  SWSD --> SDCPUD2 --> SD
  SWSD --> SDCPUD3 --> SD
  SDESDA -.->|"CLK/CMD/DAT0/DAT3 shunt clamps"| SD
  SDESDB -.->|"DAT1/DAT2/VDD/detect shunt clamps"| SD
  SD -->|"always-readable detect"| SDDETR --> SLOW
  MAINFUSE --> SDDETPU --> SLOW
  SLOW --> SDDETC
  S3 <-->|"I²C0 host side"| CODECI2C <-->|"switched local bus; 0x19"| CODEC
  S3 -->|"I²S0 BCLK"| CODECBCLK --> CODEC
  S3 -->|"I²S0 WS"| CODECWS --> CODEC
  S3 -->|"I²S0 playback"| CODECDOUT --> CODEC
  CODEC -->|"I²S0 capture"| CODECDIN --> S3
  S3 <-->|"I²C0 host side"| RXI2C <-->|"switched local bus"| SI
  S3 <-->|"GPIO7/GPIO8 profile signals"| UNISO <-->|"isolated I2C/UART/GPIO"| UNIT
  UNITESD -.->|"two signal shunt clamps"| UNIT
  RXCLK --> SI
  RXCLKC0 --> SI
  RXCLKC1 --> SI
  RXSUP -->|"reset and 200-ms interface release"| RXI2C
  RXFMSMA --> RXFMESD
  RXFMSMA --> RXFML --> RXFMC -->|"FMI contact 6"| SI
  RXAMSMA --> RXAMESD
  RXAMSMA --> RXAMC -->|"AMI contact 8"| SI
  CODECSUP -->|"200-ms interface release"| CODECI2C
  CODECSUP --> CODECBCLK
  SI --> RXMUX --> CAPSEL --> BUF --> CODEC
  MIC --> CAPSEL
  SA -->|"AFOUT"| VOICEAUDIO --> RXMUX
  CODEC --> SPKSEL --> PAM
  PAM --> SPKBEADP --> SPK
  PAM --> SPKBEADN --> SPK
  CODEC --> HPJACK --> HPESD
  CODEC --> TXSEL --> VOICEAUDIO -->|"MIC_IN"| SA
  MICFILT --> MIC --> TXSEL
  AGNDLINK --> CODEC
  S3 -->|"GPIO6 AUDIO_ARM"| SAFE
  SLOW -->|"P00 capture; P01 speaker; P02 headphone; P11/P12 selectors"| SAFE
  SAFE --> SPKSEL
  SAFE --> TXSEL
  VOICESUP --> VOICEIOSW --> VOICEAUDIO
  VOICEIOSW --> VOICEPTT
  VOICEIOSW --> VOICEUART
  SLOW -->|"P14 low-or-open power request"| VOICEHL --> SA
  MAINFUSE --> IRINCAP
  MAINFUSE --> IRSW
  C5 -->|"GPIO4; reset-off"| IRONPD --> IRSW
  IRSW --> IROUTCAP
  IRSW --> IROUTBP
  IRSW --> IR0R --> IR0
  IR0R --> IR0C
  IRSW --> IR1R --> IR1
  IR1R --> IR1C
  IR1PU --> IR1
  IRSW --> IRBUF
  IRSW --> IRBUFC
  IR0 --> IRBUF --> IR0SER -->|"RMT RX0 demodulated envelope"| C5
  IR1 --> IRBUF --> IR1SER -->|"RMT RX1 measured carrier cycles"| C5
  MAINFUSE --> IR0HPU --> C5
  MAINFUSE --> IR1HPU --> C5
  RP -->|"PIO0 SM0 outputs"| N0HB --> NRF0
  NRF0 -->|"MISO + IRQ"| N0RB --> RP
  RP -->|"PIO0 SM1 outputs"| N1HB --> NRF1
  NRF1 -->|"MISO + IRQ"| N1RB --> RP
  RP -->|"PIO0 SM2 outputs"| N2HB --> NRF2
  NRF2 -->|"MISO + IRQ"| N2RB --> RP
  RP -->|"PIO0 SM3 SCLK/SI/CSN"| CCHB --> CC
  CC -->|"SO/GDO0/GDO2"| CCRB --> RP
  SLOW -->|"P03/P04; rail-off only"| CCBAND
  CCBAND -->|"same V1/V2 truth"| CCSWA
  CCBAND -->|"same V1/V2 truth"| CCSWB
  RP <-->|"UART0/PTT request"| SA
  PTTPU -->|"10 kOhm to 3V3_MAIN"| PTTRAW
  PTTC -->|"100 nF to power ground"| PTTRAW
  PTTSW -->|"NO contact to power ground"| PTTRAW
  PTTRAW --> ENCPTTESD
  PTTRAW -->|"direct GPIO21 through 1 kOhm; never in UI matrix"| PTTR --> RP
  RP -->|"PIO1/UART1 outputs"| UHBA --> CAPDOCK
  RP --> UHBB --> CAPDOCK
  CAPDOCK -->|"BUSY/IRQ/GPS-TX/MISO"| URB --> RP
  RP <-->|"I²C0"| ISO
  ISO <-->|"isolated I²C"| CAPDOCK
  UESDA -.->|"I²C/RST/GPS-RX clamps"| CAPDOCK
  UESDB -.->|"SCK/MOSI/NSS/BUSY clamps"| CAPDOCK
  UESDC -.->|"IRQ/GPS-TX/MISO clamps"| CAPDOCK
  CAPDOCK <-->|"14-pin Cap-Bus"| U214
  SLOW -->|"P17/P05 independent requests"| EXTOR --> GATEB
  GATEB --> EXTBG
  EXTBG --> EXTFUSE
  EXTBG --> UNITEF
  EXTFUSE --> USUP --> UHBA
  USUP --> ISO
  UNITEF --> UNITSUP --> UNISO
  STOPPU -->|"10 kOhm to AON_SAFE_3V3"| STOPLOOP
  STOPC -->|"10 nF to safety ground"| STOPLOOP
  STOPSW -->|"COM+NC to safety ground"| STOPLOOP
  STOPLOOP --> SAFEESD
  STOPLOOP --> COND --> LATCH
  REARMPU -->|"47 kOhm to AON_SAFE_3V3"| REARMRAW
  REARMC -->|"100 nF to safety ground"| REARMRAW
  REARMSW -->|"NO contact to safety ground"| REARMRAW
  REARMRAW --> SAFEESD
  REARMRAW --> COND
  SUP --> POROR --> LATCH
  STOPLOOP --> POROR
  LATCH -->|"RUN_PERMIT"| RSTBUF
  RSTBUF -->|"open-drain RESET_KILL_GATE"| RSTGPU
  RSTGPU --> RSTQA
  RSTGPU --> RSTQB
  RSTQA -->|"passive-drain EN"| S3
  RSTQA -->|"passive-drain CHIP_PU"| C5
  RSTQB -->|"passive-drain RUN"| RP
  LATCH --> GATEA
  LATCH --> GATEB
  LATCH --> PTTOR
  LATCH --> STOPLEDR --> STOPLED
  RP -->|"3×CE + nRF rail requests"| GATEA
  RP -->|"CC rail request"| GATEB
  C5 -->|"IR carrier request"| GATEB
  SLOW -->|"voice/accessory rail requests"| GATEB
  RP -->|"PTT request"| PTTOR --> VOICEPTT --> SA
  GATEA --> N0HB
  GATEA --> N1HB
  GATEA --> N2HB
  GATEA --> SWNRF
  GATEA --> NEVD --> NEVC
  NEVD --> NEVR
  NEVD --> DN0
  NEVD --> DN1
  NEVD --> DN2
  GATEB --> SWCC
  GATEB --> VOICEBUCK
  GATEB --> IRTXGS --> IRTXFET
  IRTXGPD --> IRTXFET
  MAINFUSE --> IRTXRLIM --> IRTX --> IRTXFET
  GATEB --> EXTBUCK
  S3 -->|"placement-qualified U.FL jumper"| S3RFJ --> S3CPL -->|"dedicated RP-SMA boundary"| S3SMA["MPN TBD<br/>S3 external reverse-polarity SMA"]
  S3CPL -->|"-20-dB forward sample"| S3CIN --> DS3 --> CMPA
  S3CPL --> S3TERM
  S3RFB --> DS3
  S3RGB --> DS3
  S3COUT --> DS3
  S3BP --> DS3
  C5 -->|"placement-qualified U.FL jumper"| C5RFJ --> C5CPL -->|"dedicated RP-SMA boundary"| C5SMA["MPN TBD<br/>C5 external reverse-polarity SMA"]
  C5CPL -->|"-20/-13-dB forward sample"| C5CIN --> DC5 --> CMPA
  C5CPL --> C5TERM
  C5RFB --> DC5
  C5RGB --> DC5
  C5COUT --> DC5
  C5BP --> DC5
  NRF0 -->|"qualified pigtail"| N0CPL -->|"dedicated SMA"| NRF0SMA["standard SMA #nRF0"]
  N0CPL --> N0TERM
  N0CPL -->|"10-dB forward sample"| N0MATCH --> DN0 --> CMPA
  NRF1 -->|"qualified pigtail"| N1CPL -->|"dedicated SMA"| NRF1SMA["standard SMA #nRF1"]
  N1CPL --> N1TERM
  N1CPL -->|"10-dB forward sample"| N1MATCH --> DN1 --> CMPA
  NRF2 -->|"qualified pigtail"| N2CPL -->|"dedicated SMA"| NRF2SMA["standard SMA #nRF2"]
  N2CPL --> N2TERM
  N2CPL -->|"10-dB forward sample"| N2MATCH --> DN2 --> CMPB
  CC --> CCCP --> CCBAL
  CC --> CCCN --> CCBAL
  CCCP --> CCDIFF
  CCCN --> CCDIFF
  CCBAL --> CCL33 --> CCL68 --> CCSWA
  CCL33 -->|"1.2-pF shunt"| CCC12
  CCSWA -->|"RF1 315 MHz"| CC315L1 --> CC315L2 --> CCSWB
  CC315L1 -->|"shunt trap"| CC315L36 --> CC315C8
  CCSWA -->|"RF2 433 MHz"| CC433L15 --> CCSWB
  CCSWA -->|"433 input shunt"| CC433C10
  CC433L15 -->|"433 output shunt"| CC433C62
  CCSWA -->|"RF3 868/915 MHz"| CC868L10 --> CCSWB
  CCSWB --> CCLOUT --> CCESD --> CCSMA
  CCLOUT -->|"0.47-pF actual-TX sample"| CCTAP --> DCC --> CMPB
  GATEB --> CCEVD --> CCEVC
  CCEVD --> CCEVR
  CCEVD --> DCC
  CCDF --> DCC
  CCDBP --> DCC
  SA -->|"short controlled 50-Ohm line"| VOICESMA
  SA -->|"24-V shunt at external boundary"| VOICEESD
  SA -->|"5.1-kOhm actual-TX sample"| VOICETAP --> DVOICE --> CMPB
  DVOICE -->|"52.3-Ohm RFIN shunt"| VOICEMATCH
  GATEB --> VOICEEVD --> VOICEEVC
  VOICEEVD --> VOICEEVR
  VOICEEVD --> DVOICE
  VOICEDF --> DVOICE
  VOICEDBP --> DVOICE
  IRTX -.->|"light-tight internal optical tunnel"| DIR --> IREVAMP --> CMPB
  AONFUSE --> IREVBP --> IREVAMP
  AONFUSE --> IREVT --> IREVB
  IREVC --> IREVAMP
  IREFBR --> IREVAMP
  IREFBC --> IREVAMP
  CMPABP --> CMPA
  CMPBBP --> CMPB
  S3EVT --> S3EVB --> CMPA
  S3EVH --> CMPA
  S3EVPU --> CMPA
  C5EVT --> C5EVB --> CMPA
  C5EVH --> CMPA
  C5EVPU --> CMPA
  N0EVT --> N0EVB --> CMPA
  N0EVH --> CMPA
  N0EVPU --> CMPA
  N1EVT --> N1EVB --> CMPA
  N1EVH --> CMPA
  N1EVPU --> CMPA
  N2EVT --> N2EVB --> CMPB
  N2EVH --> CMPB
  N2EVPU --> CMPB
  CCEVT --> CCEVB --> CMPB
  CCEVH --> CMPB
  CCEVPU --> CMPB
  VOEVT --> VOEVB --> CMPB
  VOEVH --> CMPB
  VOEVPU --> CMPB
  IREVT2 --> IREVB2 --> CMPB
  IREVH --> CMPB
  IREVPU --> CMPB
  CMPA --> EVMASK
  CMPB --> EVMASK
  EVMASKBP --> EVMASK
  CMPA --> OR0
  CMPA --> OR1
  CMPB --> OR2
  CMPB --> OR3
  OR0 --> ANYPU
  OR1 --> ANYPU
  OR2 --> ANYPU
  OR3 --> ANYPU
  ANYLEDR --> ANYLED --> ANYPU
  EVMASK <-->|"local I²C0 source mask"| RP
  CMPA -->|"C5 RF evidence"| EVISO
  CMPB -->|"IR evidence"| EVISO
  ANYPU -->|"AON aggregate"| EVISO
  EVISOBP --> EVISO
  EVISO --> C5EVMPU -->|"GPIO23 active-low"| C5
  EVISO --> IREVMPU -->|"GPIO24 active-low"| C5
  EVISO --> RPEVMPU -->|"GPIO22 active-low"| RP
```

<details>
<summary><strong>Principled pin assignment</strong></summary>

- **S3↔C5:** S3 `GPIO10,GPIO11,GPIO12,GPIO13`; C5
  `GPIO7,GPIO8,GPIO9,GPIO10` — dedicated 1-bit SDIO.
- **S3↔RP:** S3 `GPIO3,GPIO9,GPIO14,GPIO21,GPIO48`; RP
  `GPIO19,GPIO24,GPIO25,GPIO26,GPIO27` — dedicated SPI plus alert.
- **Display and microSD:** S3
  `GPIO4,GPIO5,GPIO35,GPIO36,GPIO38,GPIO40,GPIO41,GPIO42` — direct QSPI
  and the only scheduled high-rate shared pair. Card-side Ioff buffers and a
  CS-gated MISO return keep the unpowered card and display D1 from contending.
- **Local controls:** S3 `GPIO39,GPIO47` are dedicated PCNT0 quadrature inputs.
  Dedicated `TCA9534APWR` `P0…P6` scans the diode-isolated 4×3 matrix containing
  D-pad/OK, BACK, OPT, F1, F2 and encoder push; `P7` is the local growth reserve.
  All rows are low in reset/idle, so any key asserts the wired-low interrupt.
  PTT is direct on RP `GPIO21`; STOP and RE-ARM remain independent AON paths.
- **Main slow I/O:** exact `TCA6424ARGJR` runs at address `0x22` from protected
  `3V3_MAIN`; RESET is available to the fixture and product recovery can fully
  power-cycle the main rail. AON STOP/evidence observations cross through
  separate open-drain buffers, so they cannot back-power an unpowered expander.
  P03/P04 are CC1101 rail-off band truth bits; P05 independently requests native
  M5 Unit power, so all 24 contacts are now allocated.
- **Audio and Si4732:** S3 `GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18` — I²S0
  and local I²C0 through power-valid physical isolation. Slow I/O `P00,P01,P02`
  select RX/microphone capture, enable the reset-off speaker and detect
  headphone absence. The PD controller also shares the bounded host bus and
  wired-low system IRQ; it consumes no new S3 GPIO.
- **M5 expansion:** S3 `GPIO7,GPIO8` reach the native HY2.0-4P Unit port through
  `TXS0102DCUR`; P05 controls its own `TPS259470LRPWR` 5-V branch. P17 controls
  the separate U214 branch. Both use protected-rail supervisors, high-Z signal
  isolation and connector ESD; neither connector exposes a real presence pin.
- **IR:** C5 `GPIO0,GPIO1,GPIO4,GPIO6,GPIO24` — two RX, TX, power and evidence.
- **nRF24 #0:** RP `GPIO0,GPIO1,GPIO2,GPIO30,GPIO31,GPIO32`.
- **nRF24 #1:** RP `GPIO3,GPIO4,GPIO5,GPIO33,GPIO34,GPIO35`.
- **nRF24 #2:** RP `GPIO6,GPIO7,GPIO8,GPIO36,GPIO37,GPIO38`.
- **CC1101:** RP `GPIO9,GPIO10,GPIO11,GPIO23,GPIO39,GPIO42,GPIO43`.
- **SA518/PTT:** RP `GPIO16,GPIO17,GPIO18,GPIO20,GPIO21`; the eight-source
  evidence mask shares local RP I²C0 and hardware aggregate uses `GPIO22`.
  Physical ANT contact 7 feeds a direct protected 50-Ohm standard-SMA path;
  `PESD24VY1BSF` and a separate `AD8314ACPZ-RL7` resistive sample provide
  1-W-compatible ESD and actual-TX evidence without spending P05.
- **U214 LoRa/GNSS:** RP
  `GPIO12,GPIO13,GPIO14,GPIO28,GPIO29,GPIO40,GPIO41,GPIO44,GPIO45,GPIO46,GPIO47`.
- **Resource result:** S3 `33 used / 3 reserved / 0 free`, C5 `14/6/1`, RP
  `48/0/0`, main slow I/O `24/0/0`, and UI matrix I/O `7/1/0`. Independent
  SWD/USB/RUN/BOOTSEL are outside this GPIO budget.

[Complete physical pad and net atlas](docs/review/architecture/generated/G2F-3I-principled-pinout.md)

</details>

## Physical design and controls

- The display is portrait-oriented; the waterfall redraws small regions and
  never blocks radio service.
- Its QSPI/touch assembly uses a 40-position ZIF candidate with reset-low
  defaults, local logic decoupling and a separately latch-protected PWM
  backlight. The assembly contains one exact `Sitronix ST77922` display/touch
  TDDI: touch uses I²C address `0x38`, and its active-low interrupt reaches the
  shared line through a pulled-up non-inverting open-drain buffer. Final
  connector orientation still requires the real panel tail; the electrical
  map does not pretend that mechanical fit has already passed.
- The push-push microSD endpoint uses an isolated switched rail, safe reset
  levels and always-readable card detection. Firmware enters SPI mode before
  display traffic resumes after every card-power cycle. Final socket placement,
  card access, media endurance and insert/remove fault tests remain physical HIL.
- Nine labelled antenna ports retain an unambiguous association between each
  connector, radio path and active antenna profile.
- The removable U214 mounts across the rear above the batteries while keeping
  its own antennas and connectors accessible.
- The complete local set is retained: D-pad directions plus OK, BACK, OPT, F1,
  F2, rotary encoder with push, dedicated hold-to-talk PTT, hardware STOP and
  recessed RE-ARM. None is replaced by touch or a phone.
- The nine discrete ordinary buttons, PTT and RE-ARM use exact low-current
  `Y78B23214FP`; gold-clad `AEQ10410` supplies the normally-closed STOP contact.
  Matrix, encoder/PTT and safety inputs have separate exact ESD arrays, and the
  STOP/RE-ARM array returns only to safety ground.
- Physical PTT, STOP and recessed RE-ARM are separate controls. STOP has an
  independent indicator and does not depend on the display.
- Programming and diagnostic connectors remain accessible on an assembled
  prototype and do not require a healthy application image.

## Safety and measurement integrity

- Every transmitter and Lab action starts disarmed after power, reset, update,
  watchdog or brownout.
- Initial transmission uses a conservative profile. Maximum power appears only
  after an explicit choice for the current scenario.
- Physical STOP dominates firmware and inter-processor communication. Releasing
  STOP never restores a previous target, channel, power or TX lease.
- The normally-closed STOP loop asynchronously latches all three compute domains
  in reset and independently blocks nRF CE, radio/accessory rails, voice PTT and
  the IR waveform. Only a fresh recessed RE-ARM press or a full power cycle can
  begin a new TX-off boot.
- Seven separate RF detectors and one optical IR detector produce eight
  source-specific states plus a diode-isolated physical red `ANY TX` indicator.
  An accessory without its own qualified evidence remains `Unknown`.
- Every onboard evidence channel has its own first-population threshold,
  hysteresis and open-drain pull-up. A triple open-drain boundary keeps the
  always-on evidence plane from back-powering C5 or RP when main power is off;
  measured per-path calibration still gates proof-mandatory transmission.
- Commanded TX, path current, radio-reported state and independent actual-TX
  evidence remain distinct. Unknown is never promoted to success or safety.
- Unused interfaces are powered down or enter a verified quiet state so they do
  not delay or desensitize the active signal group.
- Cost reduction is accepted only when capability, performance, safety,
  reliability, autonomy, serviceability and testability remain equivalent.

## Product boundary

The base product excludes 6 GHz/Wi-Fi 6E, generic USB host, a personal
FIDO/U2F authenticator, an integrated keyboard, a motor and an onboard IMU.
BadUSB/DuckyScript may exist only as an optional Controlled-Zone software
feature over the existing USB device path and does not shape the radio
instrument's hardware architecture.

## Project documentation

- [Current hardware engineering state](docs/status/current-state.md)
- [Principled pin map](docs/review/architecture/PIN-0003-g2f-3i-principled-pinout.md)
- [Complete requirements, decisions and evidence ledger](docs/review/README.md)
- [Firmware target product](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
