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
- Three separated nRF antennas provide calibrated relative sector/RPD
  comparison. The result is never presented as absolute dBm, angle or VSWR.
- 2.4/5 GHz Wi-Fi, Bluetooth LE, ESP-NOW and IEEE 802.15.4 provide ordinary
  communication, observation and authorized diagnostic workflows.
- A dedicated Sub-GHz path handles packet systems; a broadcast receiver covers
  AM/FM/SW/LW; a VHF/UHF voice path provides analog communication and audio.
- Two IR receivers provide robust consumer decoding and unknown-carrier
  measurement at the same time; a separate transmitter replays learned profiles.
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
  SHUNT["WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACKFET["CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair"]
  PACKHOLD["2N7002DW-7-F<br/>reset-default ALRT hold and explicit release"]
  SUPPLYOR["BAV70LT1G<br/>AOLDO/fixture source isolation"]
  SYSDIODE["BAT54-7-F<br/>admitted-system source isolation and priority"]
  PACKADM["MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge"]
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
  RP["RP2354B A4<br/>deterministic radio and voice owner"]
  SLOW["TCA6424ARGJR<br/>24-line main slow-control expander; six contacts free"]
  UIMATRIX["TCA9534APWR #UI<br/>dedicated interrupt-capable 4x3 control expander"]
  UIMBP["C1005X7R1H104K050BB #UI<br/>100-nF UI-expander bypass capacitor"]
  UIR0PD["RC0603FR-071KL #UI-R0<br/>1-kOhm reset/idle row pull-down"]
  UIR1PD["RC0603FR-071KL #UI-R1<br/>1-kOhm reset/idle row pull-down"]
  UIR2PD["RC0603FR-071KL #UI-R2<br/>1-kOhm reset/idle row pull-down"]
  UIR3PD["RC0603FR-071KL #UI-R3<br/>1-kOhm reset/idle row pull-down"]
  UIC0PU["RC0402FR-0710KL #UI-C0<br/>10-kOhm matrix-column pull-up"]
  UIC1PU["RC0402FR-0710KL #UI-C1<br/>10-kOhm matrix-column pull-up"]
  UIC2PU["RC0402FR-0710KL #UI-C2<br/>10-kOhm matrix-column pull-up"]
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
  UIUP["MPN TBD<br/>D-pad UP ordinary control"]
  UIDOWN["MPN TBD<br/>D-pad DOWN ordinary control"]
  UILEFT["MPN TBD<br/>D-pad LEFT ordinary control"]
  UIRIGHT["MPN TBD<br/>D-pad RIGHT ordinary control"]
  UIOK["MPN TBD<br/>D-pad OK ordinary control"]
  UIBACK["MPN TBD<br/>BACK ordinary control"]
  UIOPT["MPN TBD<br/>OPT ordinary control"]
  UIF1["MPN TBD<br/>F1 ordinary control"]
  UIF2["MPN TBD<br/>F2 ordinary control"]
  ENC["Alps Alpine EC11E18244AU<br/>36-detent/18-pulse encoder with push"]
  ENCAPU["RC0402FR-073K32L #ENC-A<br/>3.32-kOhm encoder-phase-A contact-current pull-up"]
  ENCBPU["RC0402FR-073K32L #ENC-B<br/>3.32-kOhm encoder-phase-B contact-current pull-up"]
  TPIRQ["SN74LVC1G07DCKR<br/>open-drain touch-interrupt adapter"]
  TPIRQALT["SN74LVC1G06DCKR (DNP alternative)<br/>pin-compatible active-high TP_INT inverter option"]
  TPIRQBP["C1005X7R1H104K050BB #TP-IRQ<br/>100-nF touch-IRQ adapter bypass capacitor"]
  LCDCON["FH12-40S-0.5SH(55)<br/>first 40-position 0.5-mm bottom-contact ZIF panel-mate candidate"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
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
  SI["Si4732-A10-GS<br/>AM/FM/SW/LW broadcast receiver"]
  CODEC["ES8311<br/>mono ADC/DAC audio codec"]
  RXMUX["SN74LVC1G3157DBVR<br/>receive-audio source selector"]
  BUF["TLV9061IDBVR<br/>active high-impedance capture buffer"]
  SPKSEL["TMUX1136DGSR<br/>dual differential speaker-path selector"]
  TXSEL["TS5A63157DCKR<br/>transmit-audio selector"]
  SAFE["SN74LVC2G08DCUR<br/>reset-safe selector-request gate"]
  PAM["PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPK["MPN TBD<br/>internal loudspeaker"]
  MIC["MPN TBD<br/>electret microphone"]
  NRF0["E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  SA["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  CAPDOCK["MPN TBD<br/>2×7 female 2.54-mm host Cap-Bus receptacle"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  IR0["MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver"]
  IR1["MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver"]
  IRTX["MPN TBD (TSAL6200 screened)<br/>IR transmit LED/driver endpoint"]
  PTTSW["MPN TBD<br/>separate normally-open hold-to-talk PTT control"]
  STOPSW["MPN TBD<br/>normally-closed physical STOP control"]
  REARMSW["MPN TBD<br/>normally-open recessed RE-ARM control"]
  SUP["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
  COND["74LVC2G14GW,125<br/>STOP and RE-ARM Schmitt conditioner"]
  POROR["74LVC1G32GV,125<br/>STOP-dominant POR/clear combiner"]
  LATCH["SN74LVC1G74DCUR<br/>asynchronous latched hard STOP"]
  RSTBUF["SN74LVC3G34DCUR<br/>Ioff three-domain reset fan-out"]
  GATEA["SN74LVC08APWR #1<br/>four STOP-dominant nRF request gates"]
  GATEB["SN74LVC08APWR #2<br/>four STOP-dominant rail/IR/accessory gates"]
  PTTOR["74LVC1G32GV,125 #2<br/>active-low voice PTT force-RX gate"]
  STOPLED["LTST-C190KFKT<br/>orange physical latched-STOP indicator"]
  DS3["LTC5532ES6#TRMPBF #S3<br/>S3 2.4-GHz RF power detector"]
  DC5["LTC5532ES6#TRMPBF #C5<br/>C5 2.4/5-GHz RF power detector"]
  DN0["LTC5532ES6#TRMPBF #nRF0<br/>nRF0 2.4-GHz RF power detector"]
  DN1["LTC5532ES6#TRMPBF #nRF1<br/>nRF1 2.4-GHz RF power detector"]
  DN2["LTC5532ES6#TRMPBF #nRF2<br/>nRF2 2.4-GHz RF power detector"]
  DCC["LTC5507ES6#TRMPBF #CC<br/>CC1101 sub-GHz RF power detector"]
  DVOICE["LTC5507ES6#TRMPBF #voice<br/>SA518 VHF/UHF RF power detector"]
  DIR["VEMD1060X01<br/>IR optical-evidence photodiode"]
  CMPA["TLV1824PWR #1<br/>S3/C5/nRF0/nRF1 evidence thresholds"]
  CMPB["TLV1824PWR #2<br/>nRF2/CC/voice/IR evidence thresholds"]
  EVMASK["TCA9534APWR<br/>eight-bit evidence source mask on local RP I²C0"]
  OR0["BAT54ALT1G #0<br/>evidence diode-OR pair 0/1"]
  OR1["BAT54ALT1G #1<br/>evidence diode-OR pair 2/3"]
  OR2["BAT54ALT1G #2<br/>evidence diode-OR pair 4/5"]
  OR3["BAT54ALT1G #3<br/>evidence diode-OR pair 6/7"]
  ANYLED["LTST-C190KRKT<br/>red physical ANY-TX indicator"]
  %% Layout-only invisible spine: these links are not electrical connections.
  USBC ~~~ PORTPROT ~~~ PORTDPR ~~~ PORTDMR ~~~ PORTVBIAS ~~~ PORTVPWR ~~~ PORTFLTPU ~~~ VBUSPROT ~~~ PDCTRL ~~~ PDCFG ~~~ PVINCAP ~~~ PL3CAP ~~~ PL1CAP ~~~ PPHVC0 ~~~ PPHVC1
  PPHVC1 ~~~ PPHVC2 ~~~ PPHVC3 ~~~ PVBUSCAP ~~~ PCC1CAP ~~~ PCC2CAP ~~~ PEECAP ~~~ PEEWPPU
  PEEWPPU ~~~ PLSCLPU ~~~ PLSDAPU ~~~ PHSCLPU ~~~ PHSDAPU ~~~ PIRQPU ~~~ CHARGER
  CHARGER ~~~ CHL ~~~ CVB0 ~~~ CVB1 ~~~ CVBHF ~~~ CPM0 ~~~ CPM1 ~~~ CPM2 ~~~ CPMHF
  CPMHF ~~~ CSYS0 ~~~ CSYS1 ~~~ CSYS2 ~~~ CSYS3 ~~~ CSYS4 ~~~ CSYSHF ~~~ CBAT0 ~~~ CBAT1
  CBAT1 ~~~ CBT1 ~~~ CBT2 ~~~ CREGN ~~~ CSDRV ~~~ CPROG ~~~ CBATP ~~~ CTSU ~~~ CTSL ~~~ CTSN
  CTSN ~~~ CILU ~~~ CILL ~~~ CINTPU ~~~ CCEPU ~~~ HOLDER ~~~ CELL0 ~~~ FUSE0 ~~~ NTC0 ~~~ CELL1 ~~~ FUSE1 ~~~ NTC1
  NTC1 ~~~ PACKGAUGE ~~~ SHUNT ~~~ PACKFET ~~~ PACKHOLD ~~~ SUPPLYOR ~~~ SYSDIODE ~~~ PACKADM
  PACKADM ~~~ DIAGTMR ~~~ DIAGTR ~~~ DIAGTC ~~~ DIAGLR ~~~ DIAGLC ~~~ DIAGBP ~~~ DIAGTRPD ~~~ DIAGGPD ~~~ DIAGQ ~~~ DIAGR0 ~~~ DIAGR1
  DIAGR1 ~~~ MIDADC0 ~~~ MIDADC1 ~~~ MIDADCB ~~~ MIDADCC ~~~ STACKADC0 ~~~ STACKADC1 ~~~ STACKADC2 ~~~ STACKADC3 ~~~ STACKADC4 ~~~ STACKADCB ~~~ STACKADCC
  STACKADCC ~~~ AONBUCK ~~~ AONL ~~~ AONMODE ~~~ AONIN ~~~ AONOUT ~~~ AONFUSE ~~~ AONRILIM ~~~ AONOVT ~~~ AONOVB ~~~ AONFIN ~~~ AONFOUT ~~~ AONPGPU ~~~ PORPU
  PORPU ~~~ MAINBUCK ~~~ MAINL ~~~ MAININ ~~~ MAINHF ~~~ MAINFBT ~~~ MAINFBB ~~~ MAINFF ~~~ MAINOUT0 ~~~ MAINOUT1 ~~~ MAINFUSE ~~~ MAINRILM ~~~ MAINDVDT ~~~ MAINIT ~~~ MAINOVT ~~~ MAINOVB ~~~ MAINPGT ~~~ MAINPGB ~~~ MAINFOUT ~~~ MAINENPD ~~~ FAULTPU
  FAULTPU ~~~ VOICEBUCK ~~~ VOICEL ~~~ VOICEIN ~~~ VOICEHF ~~~ VOICEFBT ~~~ VOICEFBB ~~~ VOICEFF ~~~ VOICEOUT0 ~~~ VOICEOUT1 ~~~ VOICEFUSE ~~~ VOICERILIM ~~~ VOICEDVDT ~~~ VOICEIT ~~~ VOICEOVT ~~~ VOICEOVB ~~~ VOICEPGT ~~~ VOICEPGB ~~~ VOICEFOUT ~~~ VOICEENPD ~~~ VOICEPGPU ~~~ VOICEPGBR ~~~ VOICEPGQ
  VOICEPGQ ~~~ EXTBUCK ~~~ EXTL ~~~ EXTBUCKIN ~~~ EXTBUCKHF ~~~ EXTBUCKFBT ~~~ EXTBUCKFBB ~~~ EXTBUCKFF ~~~ EXTBUCKOUT0 ~~~ EXTBUCKOUT1 ~~~ EXTENPD ~~~ EXTPGPU ~~~ EXTPGBR ~~~ EXTPGQ ~~~ EXTFUSE ~~~ EXTRILM ~~~ EXTDVDT ~~~ EXTITIMER
  EXTITIMER ~~~ EXTOVLOT ~~~ EXTOVLOB ~~~ EXTINCAP ~~~ EXTOUTCAP ~~~ EXTBLEED ~~~ SWNRF ~~~ SWCC ~~~ SWSD ~~~ SWCODEC ~~~ SWRX ~~~ S3 ~~~ SLOW
  SLOW ~~~ UIMATRIX ~~~ UIMBP ~~~ UIR0PD ~~~ UIR1PD ~~~ UIR2PD ~~~ UIR3PD ~~~ UIC0PU ~~~ UIC1PU ~~~ UIC2PU
  UIC2PU ~~~ UIDUP ~~~ UIUP ~~~ UIDDN ~~~ UIDOWN ~~~ UIDLEFT ~~~ UILEFT
  UILEFT ~~~ UIDRIGHT ~~~ UIRIGHT ~~~ UIDOK ~~~ UIOK ~~~ UIDBACK ~~~ UIBACK
  UIBACK ~~~ UIDOPT ~~~ UIOPT ~~~ UIDF1 ~~~ UIF1 ~~~ UIDF2 ~~~ UIF2
  UIF2 ~~~ UIDENC ~~~ ENC ~~~ ENCAPU ~~~ ENCBPU ~~~ TPIRQ ~~~ TPIRQALT ~~~ TPIRQBP
  TPIRQBP ~~~ SAFE ~~~ SI ~~~ RXMUX ~~~ BUF ~~~ CODEC
  CODEC ~~~ SPKSEL ~~~ PAM ~~~ SPK ~~~ MIC ~~~ TXSEL
  TXSEL ~~~ LCDCON ~~~ LCD ~~~ LCDLBULK ~~~ LCDLHF ~~~ LCDRPD ~~~ TPRPD ~~~ BLEFUSE ~~~ BLILIM ~~~ BLIN ~~~ BLOUT ~~~ BLOUTHF
  BLOUTHF ~~~ BLFPU ~~~ BLR ~~~ BLQ ~~~ BLGR ~~~ BLGPD ~~~ SD ~~~ SDHBUF ~~~ SDMBUF ~~~ SDESDA ~~~ SDESDB
  SDESDB ~~~ SDINCAP ~~~ SDBULK ~~~ SDHFCAP ~~~ SDHBUFCAP ~~~ SDMBUFCAP ~~~ SDONPD ~~~ SDSCKPD ~~~ SDD0PU ~~~ SDD1PU
  SDD1PU ~~~ SDHCS ~~~ LCDHCS ~~~ SDCPUCMD ~~~ SDCPUD0 ~~~ SDCPUD1 ~~~ SDCPUD2 ~~~ SDCPUD3
  SDCPUD3 ~~~ SDSCKR ~~~ SDCMDR ~~~ SDCSR ~~~ SDMISOR ~~~ SDDETR ~~~ SDDETPU ~~~ SDDETC ~~~ UNIT ~~~ C5 ~~~ IR0 ~~~ IR1 ~~~ IRTX
  IRTX ~~~ RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ SA
  SA ~~~ ISO ~~~ CAPDOCK ~~~ U214 ~~~ PTTSW ~~~ STOPSW ~~~ REARMSW
  REARMSW ~~~ SUP ~~~ COND ~~~ POROR ~~~ LATCH ~~~ RSTBUF
  RSTBUF ~~~ GATEA ~~~ GATEB ~~~ PTTOR ~~~ STOPLED
  STOPLED ~~~ DS3 ~~~ DC5 ~~~ DN0 ~~~ DN1 ~~~ DN2
  DN2 ~~~ DCC ~~~ DVOICE ~~~ DIR ~~~ CMPA ~~~ CMPB
  CMPB ~~~ EVMASK ~~~ OR0 ~~~ OR1 ~~~ OR2 ~~~ OR3 ~~~ ANYLED
  USBC -->|"raw VBUS to VBUS + VBUS_IN"| PDCTRL
  USBC -->|"VBUS shunt"| VBUSPROT
  USBC <-->|"CC1/CC2 + D+/D-"| PORTPROT
  PORTPROT <-->|"protected D+"| PORTDPR <-->|"Full-Speed GPIO20"| S3
  PORTPROT <-->|"protected D-"| PORTDMR <-->|"Full-Speed GPIO19"| S3
  PORTPROT <-->|"protected CC1/CC2"| PDCTRL
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
  SHUNT -->|"CSP/CSN Kelvin evidence"| PACKGAUGE
  PACKGAUGE -->|"CHG/DIS gates; no prequal"| PACKFET
  PACKFET <-->|"protected 2S power boundary"| CHARGER
  PACKHOLD -->|"ALRT low by default"| PACKGAUGE
  PACKADM -->|"explicit release"| PACKHOLD
  PACKGAUGE -->|"AOLDO"| SUPPLYOR --> PACKADM
  SYSDIODE -->|"admitted 3V3"| PACKADM
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
  CHARGER -->|"SYS"| EXTBUCK --> EXTL --> EXTFUSE -->|"protected fixed 5.0 V"| U214
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
  SWNRF --> NRF1
  SWNRF --> NRF2
  SWCC --> CC
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
  S3 -->|"direct QSPI + touch"| LCDCON
  LCDCON <-->|"40-contact FPC; physical mate HIL open"| LCD
  LCDCON -->|"raw TP_INT"| TPIRQ -->|"open-drain SYS_INT_N"| S3
  TPIRQALT -.->|"same footprint; populate only after polarity HIL"| TPIRQ
  TPIRQBP --> TPIRQ
  SLOW -->|"P06/P07 reset release"| LCDCON
  S3 <-->|"SYS I²C0 + wired-low IRQ"| UIMATRIX
  UIMBP --> UIMATRIX
  UIR0PD -->|"reset/idle low"| UIMATRIX
  UIR1PD -->|"reset/idle low"| UIMATRIX
  UIR2PD -->|"reset/idle low"| UIMATRIX
  UIR3PD -->|"reset/idle low"| UIMATRIX
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
  S3 <-->|"I²S0 + I²C0"| CODEC
  S3 <-->|"I²C0"| SI
  S3 <-->|"profile port"| UNIT
  SI --> RXMUX --> BUF --> CODEC
  SA -->|"AFOUT"| RXMUX
  CODEC --> SPKSEL --> PAM
  PAM --> SPK
  CODEC --> TXSEL -->|"MIC_IN"| SA
  MIC --> TXSEL
  S3 -->|"GPIO6 AUDIO_ARM"| SAFE
  SLOW -->|"P11/P12 requests"| SAFE
  SAFE --> SPKSEL
  SAFE --> TXSEL
  C5 -->|"RMT RX0"| IR0
  C5 -->|"RMT RX1"| IR1
  RP <-->|"PIO0 SM0"| NRF0
  RP <-->|"PIO0 SM1"| NRF1
  RP <-->|"PIO0 SM2"| NRF2
  RP <-->|"PIO0 SM3"| CC
  RP <-->|"UART0/PTT request"| SA
  PTTSW -->|"direct GPIO21; never in UI matrix"| RP
  RP <-->|"PIO1/UART1"| CAPDOCK
  RP <-->|"I²C0"| ISO
  ISO <-->|"isolated I²C"| CAPDOCK
  CAPDOCK <-->|"14-pin Cap-Bus"| U214
  STOPSW --> COND --> LATCH
  REARMSW --> COND
  SUP --> POROR --> LATCH
  STOPSW --> POROR
  LATCH -->|"RUN_PERMIT"| RSTBUF
  RSTBUF -->|"CHIP_PU"| S3
  RSTBUF -->|"CHIP_PU"| C5
  RSTBUF -->|"RUN"| RP
  LATCH --> GATEA
  LATCH --> GATEB
  LATCH --> PTTOR
  LATCH --> STOPLED
  RP -->|"3×CE + nRF rail requests"| GATEA
  RP -->|"CC rail request"| GATEB
  C5 -->|"IR carrier request"| GATEB
  SLOW -->|"voice/accessory rail requests"| GATEB
  RP -->|"PTT request"| PTTOR --> SA
  GATEA --> NRF0
  GATEA --> NRF1
  GATEA --> NRF2
  GATEA --> SWNRF
  GATEB --> SWCC
  GATEB --> VOICEBUCK
  GATEB --> IRTX
  GATEB --> EXTBUCK
  GATEB --> EXTFUSE
  S3 --> DS3 --> CMPA
  C5 --> DC5 --> CMPA
  NRF0 --> DN0 --> CMPA
  NRF1 --> DN1 --> CMPA
  NRF2 --> DN2 --> CMPB
  CC --> DCC --> CMPB
  SA --> DVOICE --> CMPB
  IRTX --> DIR --> CMPB
  CMPA --> EVMASK
  CMPB --> EVMASK
  CMPA --> OR0
  CMPA --> OR1
  CMPB --> OR2
  CMPB --> OR3
  OR0 --> ANYLED
  OR1 --> ANYLED
  OR2 --> ANYLED
  OR3 --> ANYLED
  EVMASK <-->|"local I²C0 source mask"| RP
  ANYLED -->|"GPIO22 RP_ANY_TX_N"| RP
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
- **Audio and Si4732:** S3 `GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18` — I²S0
  and local I²C0. The PD controller also shares this bounded control bus and
  the wired-low system IRQ; it consumes no new S3 GPIO.
- **M5 Unit:** S3 `GPIO7,GPIO8` — separate configurable profile port.
- **IR:** C5 `GPIO0,GPIO1,GPIO4,GPIO6,GPIO24` — two RX, TX, power and evidence.
- **nRF24 #0:** RP `GPIO0,GPIO1,GPIO2,GPIO30,GPIO31,GPIO32`.
- **nRF24 #1:** RP `GPIO3,GPIO4,GPIO5,GPIO33,GPIO34,GPIO35`.
- **nRF24 #2:** RP `GPIO6,GPIO7,GPIO8,GPIO36,GPIO37,GPIO38`.
- **CC1101:** RP `GPIO9,GPIO10,GPIO11,GPIO23,GPIO39,GPIO42,GPIO43`.
- **SA518/PTT:** RP `GPIO16,GPIO17,GPIO18,GPIO20,GPIO21`; the eight-source
  evidence mask shares local RP I²C0 and hardware aggregate uses `GPIO22`.
- **U214 LoRa/GNSS:** RP
  `GPIO12,GPIO13,GPIO14,GPIO28,GPIO29,GPIO40,GPIO41,GPIO44,GPIO45,GPIO46,GPIO47`.
- **Resource result:** S3 `33 used / 3 reserved / 0 free`, C5 `14/6/1`, RP
  `48/0/0`, main slow I/O `18/0/6`, and UI matrix I/O `7/1/0`. Independent
  SWD/USB/RUN/BOOTSEL are outside this GPIO budget.

[Complete physical pad and net atlas](docs/review/architecture/generated/G2F-3I-principled-pinout.md)

</details>

## Physical design and controls

- The display is portrait-oriented; the waterfall redraws small regions and
  never blocks radio service.
- Its QSPI/touch assembly uses a 40-position ZIF candidate with reset-low
  defaults, local logic decoupling and a separately latch-protected PWM
  backlight. Final connector orientation still requires the real panel tail;
  the electrical map does not pretend that mechanical fit has already passed.
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
