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
- microSD stores spectrum records, audio, profiles, logs and exported data.
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
- The product USB-C port keeps direct S3 USB2 data and accepts power only:
  5-V fallback, 9 V at 3 A and 15 V at 2 A, up to 30 W. It never acts as a
  power bank or USB-PD source.
- The PD controller boots autonomously from a dedicated recoverable EEPROM.
  Factory pads can program a blank device; field updates verify an
  owner-signed image and retain a rollback region.
- The 2S charger is physically strapped to an efficient `750 kHz` profile
  with a `2.2 uH / 7 A` inductor. Reset restores a conservative `1 A` charge;
  normal operation never exceeds `2 A`, first limits input current to the
  actual 5/9/15-V USB contract and stops on direct battery-temperature faults.
- The supervised 2S battery uses two individually replaceable qualified 18650
  cells; both are required for battery operation. Reverse insertion is
  mechanically blocked; hardware observes and admits the pair before it may
  reach the system, and refuses an unsafe combination instead of forcing it
  to operate or equalize. The handheld also refuses deeply discharged cells:
  zero-volt/prequalification recovery is disabled, and any recovery research
  requires a separate isolated Controlled-Zone fixture. Before admission, a
  common-path 10-Ohm diagnostic applies approximately `0.57…0.88 A` for no
  more than `50 ms`; an independent non-retriggerable hardware timer prevents
  firmware from stretching the pulse. This is a contact/cell screen, not a
  full-load qualification claim.
- Four independent fixed rails separate always-on safety, 3.3-V compute,
  4.0-V voice and protected 5.0-V accessory power. Unused radio, storage and
  audio branches are disconnected and discharged into a verified quiet state.
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
  USBC["MPN TBD<br/>product USB-C receptacle: direct S3 USB2 data and sink-only power"]
  VBUSPROT["TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection"]
  PDCTRL["TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path"]
  PDCFG["CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM"]
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
  CSCLPU["RC0402FR-0710KL #CHG-SCL<br/>10-kOhm charger SCL pull-up resistor"]
  CSDAPU["RC0402FR-0710KL #CHG-SDA<br/>10-kOhm charger SDA pull-up resistor"]
  CINTPU["RC0402FR-0710KL #CHG-INT<br/>10-kOhm charger INT pull-up resistor"]
  CCEPU["RC0402FR-0710KL #CHG-CE<br/>10-kOhm reset-high charger CE pull-up resistor"]
  CELL0["MPN TBD<br/>individually replaceable qualified 18650 cell #0"]
  FUSE0["0451005.MRL<br/>slot-0 independent 5-A fast fuse"]
  NTC0["B57332V5103F360<br/>cell-0 temperature sensor"]
  CELL1["MPN TBD<br/>individually replaceable qualified 18650 cell #1"]
  FUSE1["0451005.MRL<br/>slot-1 independent 5-A fast fuse"]
  NTC1["B57332V5103F360<br/>cell-1 temperature sensor"]
  PACKGAUGE["MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing"]
  SHUNT["WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACKFET["CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair"]
  PACKHOLD["2N7002DW-7-F<br/>reset-default ALRT hold and explicit release"]
  SUPPLYOR["BAV70LT1G<br/>AOLDO/fixture source isolation"]
  SYSDIODE["BAT54-7-F<br/>admitted-system source isolation and priority"]
  PACKADM["MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge"]
  DIAGTMR["TPUL2G223BQBR<br/>non-retriggerable hardware diagnostic-pulse limiter"]
  DIAGTR["RC0402FR-07169KL #DIAG-TIME<br/>169-kOhm 1% diagnostic-pulse timing resistor"]
  DIAGTC["GRM31C5C1H224JE02L #DIAG-TIME<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor"]
  DIAGBP["C1005X7R1H104K050BB #DIAG<br/>100-nF 50-V X7R one-shot bypass capacitor"]
  DIAGTRPD["RC0402FR-0710KL #DIAG-TRIG<br/>10-kOhm 1% diagnostic-trigger fail-low resistor"]
  DIAGGPD["RC0402FR-0710KL #DIAG-GATE<br/>10-kOhm 1% diagnostic-gate fail-low resistor"]
  DIAGQ["DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET"]
  DIAGR["CRCW251210R0JNEGIF<br/>10-Ohm 1-W pulse-proof diagnostic-load resistor"]
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
  AONOUT["GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON output capacitor"]
  AONPGPU["RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor"]
  MAINBUCK["TPS564252DRLR<br/>fixed 3.3-V 4-A main converter"]
  MAINL["MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor"]
  MAININ["GRM32ER71E226KE15L #MAIN-IN<br/>22-uF 25-V X7R main bulk input capacitor"]
  MAINHF["C1005X7R1H104K050BB #MAIN<br/>100-nF 50-V X7R main HF input capacitor"]
  MAINFBT["RC0402FR-0745K3L<br/>45.3-kOhm 1% main feedback top resistor"]
  MAINFBB["RC0402FR-0710KL<br/>10-kOhm 1% main feedback bottom resistor"]
  MAINFF["C0402C330J5GACTU #MAIN<br/>33-pF 50-V C0G main feed-forward capacitor"]
  MAINOUT0["GRM32ER71E226KE15L #MAIN-OUT0<br/>22-uF 25-V X7R main output capacitor #0"]
  MAINOUT1["GRM32ER71E226KE15L #MAIN-OUT1<br/>22-uF 25-V X7R main output capacitor #1"]
  MAINENPD["RC0402FR-0710KL #MAIN-EN<br/>10-kOhm 1% main-enable fail-low resistor"]
  FAULTPU["RC0402FR-0710KL #POWER-FAULT<br/>10-kOhm 1% wired-low power-fault pull-up resistor"]
  VOICEBUCK["TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter"]
  VOICEL["MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor"]
  VOICEIN["GRM32ER71E226KE15L #VOICE-IN<br/>22-uF 25-V X7R voice bulk input capacitor"]
  VOICEHF["C1005X7R1H104K050BB #VOICE<br/>100-nF 50-V X7R voice HF input capacitor"]
  VOICEFBT["RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor"]
  VOICEFBB["RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor"]
  VOICEFF["C0402C330J5GACTU #VOICE<br/>33-pF 50-V C0G voice feed-forward capacitor"]
  VOICEOUT0["GRM32ER71E226KE15L #VOICE-OUT0<br/>22-uF 25-V X7R voice output capacitor #0"]
  VOICEOUT1["GRM32ER71E226KE15L #VOICE-OUT1<br/>22-uF 25-V X7R voice output capacitor #1"]
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
  SLOW["TCA6424ARGJR<br/>24-line slow-control and UI expander"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  SD["DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
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
  USBC ~~~ VBUSPROT ~~~ PDCTRL ~~~ PDCFG ~~~ CHARGER
  CHARGER ~~~ CHL ~~~ CVB0 ~~~ CVB1 ~~~ CVBHF ~~~ CPM0 ~~~ CPM1 ~~~ CPM2 ~~~ CPMHF
  CPMHF ~~~ CSYS0 ~~~ CSYS1 ~~~ CSYS2 ~~~ CSYS3 ~~~ CSYS4 ~~~ CSYSHF ~~~ CBAT0 ~~~ CBAT1
  CBAT1 ~~~ CBT1 ~~~ CBT2 ~~~ CREGN ~~~ CSDRV ~~~ CPROG ~~~ CBATP ~~~ CTSU ~~~ CTSL ~~~ CTSN
  CTSN ~~~ CILU ~~~ CILL ~~~ CSCLPU ~~~ CSDAPU ~~~ CINTPU ~~~ CCEPU ~~~ CELL0 ~~~ FUSE0 ~~~ NTC0 ~~~ CELL1 ~~~ FUSE1 ~~~ NTC1
  NTC1 ~~~ PACKGAUGE ~~~ SHUNT ~~~ PACKFET ~~~ PACKHOLD ~~~ SUPPLYOR ~~~ SYSDIODE ~~~ PACKADM
  PACKADM ~~~ DIAGTMR ~~~ DIAGTR ~~~ DIAGTC ~~~ DIAGBP ~~~ DIAGTRPD ~~~ DIAGGPD ~~~ DIAGQ ~~~ DIAGR
  DIAGR ~~~ MIDADC0 ~~~ MIDADC1 ~~~ MIDADCB ~~~ MIDADCC ~~~ STACKADC0 ~~~ STACKADC1 ~~~ STACKADC2 ~~~ STACKADC3 ~~~ STACKADC4 ~~~ STACKADCB ~~~ STACKADCC
  STACKADCC ~~~ AONBUCK ~~~ AONL ~~~ AONMODE ~~~ AONIN ~~~ AONOUT ~~~ AONPGPU
  AONPGPU ~~~ MAINBUCK ~~~ MAINL ~~~ MAININ ~~~ MAINHF ~~~ MAINFBT ~~~ MAINFBB ~~~ MAINFF ~~~ MAINOUT0 ~~~ MAINOUT1 ~~~ MAINENPD ~~~ FAULTPU
  FAULTPU ~~~ VOICEBUCK ~~~ VOICEL ~~~ VOICEIN ~~~ VOICEHF ~~~ VOICEFBT ~~~ VOICEFBB ~~~ VOICEFF ~~~ VOICEOUT0 ~~~ VOICEOUT1 ~~~ VOICEENPD ~~~ VOICEPGPU ~~~ VOICEPGBR ~~~ VOICEPGQ
  VOICEPGQ ~~~ EXTBUCK ~~~ EXTL ~~~ EXTBUCKIN ~~~ EXTBUCKHF ~~~ EXTBUCKFBT ~~~ EXTBUCKFBB ~~~ EXTBUCKFF ~~~ EXTBUCKOUT0 ~~~ EXTBUCKOUT1 ~~~ EXTENPD ~~~ EXTPGPU ~~~ EXTPGBR ~~~ EXTPGQ ~~~ EXTFUSE ~~~ EXTRILM ~~~ EXTDVDT ~~~ EXTITIMER
  EXTITIMER ~~~ EXTOVLOT ~~~ EXTOVLOB ~~~ EXTINCAP ~~~ EXTOUTCAP ~~~ EXTBLEED ~~~ SWNRF ~~~ SWCC ~~~ SWSD ~~~ SWCODEC ~~~ SWRX ~~~ S3 ~~~ SLOW
  SLOW ~~~ SAFE ~~~ SI ~~~ RXMUX ~~~ BUF ~~~ CODEC
  CODEC ~~~ SPKSEL ~~~ PAM ~~~ SPK ~~~ MIC ~~~ TXSEL
  TXSEL ~~~ LCD ~~~ SD ~~~ UNIT ~~~ C5 ~~~ IR0 ~~~ IR1 ~~~ IRTX
  IRTX ~~~ RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ SA
  SA ~~~ ISO ~~~ CAPDOCK ~~~ U214 ~~~ STOPSW ~~~ REARMSW
  REARMSW ~~~ SUP ~~~ COND ~~~ POROR ~~~ LATCH ~~~ RSTBUF
  RSTBUF ~~~ GATEA ~~~ GATEB ~~~ PTTOR ~~~ STOPLED
  STOPLED ~~~ DS3 ~~~ DC5 ~~~ DN0 ~~~ DN1 ~~~ DN2
  DN2 ~~~ DCC ~~~ DVOICE ~~~ DIR ~~~ CMPA ~~~ CMPB
  CMPB ~~~ EVMASK ~~~ OR0 ~~~ OR1 ~~~ OR2 ~~~ OR3 ~~~ ANYLED
  USBC -->|"VBUS sink only"| PDCTRL
  USBC -->|"VBUS shunt"| VBUSPROT
  USBC <-->|"D-/D+ direct; no PD/charger tap"| S3
  PDCTRL <-->|"local I²C boot image"| PDCFG
  PDCTRL <-->|"protected VBUS + local I²C/IRQ"| CHARGER
  S3 <-->|"SYS I²C0 + shared wired-low IRQ"| PDCTRL
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
  PDCTRL -->|"LDO_3V3 pull-ups"| CSCLPU --> CHARGER
  PDCTRL --> CSDAPU --> CHARGER
  PDCTRL --> CINTPU --> CHARGER
  CHARGER -->|"REGN reset-high CE"| CCEPU --> CHARGER
  CELL0 --> FUSE0 --> PACKGAUGE
  NTC0 -->|"TH1"| PACKGAUGE
  CELL1 --> FUSE1 --> PACKGAUGE
  NTC1 -->|"TH2"| PACKGAUGE
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
  DIAGTMR --> DIAGBP
  DIAGTMR -->|"bounded gate pulse"| DIAGQ
  DIAGTMR --> DIAGGPD
  FUSE1 -->|"fused full stack"| DIAGR --> DIAGQ
  FUSE0 --> MIDADC0 --> MIDADC1 -->|"PA25/A2"| PACKADM
  PACKADM --> MIDADCB
  PACKADM --> MIDADCC
  FUSE1 --> STACKADC0 --> STACKADC1 --> STACKADC2 --> STACKADC3 --> STACKADC4 -->|"PA26/A1"| PACKADM
  PACKADM --> STACKADCB
  PACKADM --> STACKADCC
  CHARGER -->|"SYS"| AONBUCK --> AONL -->|"AON_SAFE_3V3"| SUP
  AONBUCK -->|"MODE/S-CONF"| AONMODE
  CHARGER -->|"SYS local bypass"| AONIN
  AONL -->|"AON local output"| AONOUT
  AONL -->|"PG pull-up"| AONPGPU --> AONBUCK
  CHARGER -->|"SYS"| MAINBUCK --> MAINL -->|"3V3_MAIN"| S3
  CHARGER -->|"SYS local bulk"| MAININ
  CHARGER -->|"SYS local HF"| MAINHF
  MAINL -->|"feedback"| MAINFBT --> MAINFBB
  MAINL -->|"feed-forward"| MAINFF
  MAINL -->|"local output bank"| MAINOUT0
  MAINL -->|"local output bank"| MAINOUT1
  MAINBUCK -->|"EN fail-low"| MAINENPD
  MAINL -->|"POWER_FAULT_N pull-up"| FAULTPU --> SLOW
  MAINL --> C5
  MAINL --> RP
  MAINL --> SWNRF
  MAINL --> SWCC
  MAINL --> SWSD
  MAINL --> SWCODEC
  MAINL --> SWRX
  CHARGER -->|"SYS"| VOICEBUCK --> VOICEL -->|"fixed 4.0 V"| SA
  CHARGER -->|"SYS local bulk"| VOICEIN
  CHARGER -->|"SYS local HF"| VOICEHF
  VOICEL -->|"feedback"| VOICEFBT --> VOICEFBB
  VOICEL -->|"feed-forward"| VOICEFF
  VOICEL -->|"local output bank"| VOICEOUT0
  VOICEL -->|"local output bank"| VOICEOUT1
  VOICEBUCK -->|"EN fail-low"| VOICEENPD
  MAINL -->|"PG pull-up"| VOICEPGPU --> VOICEBUCK
  GATEB -->|"EN"| VOICEPGBR --> VOICEPGQ
  VOICEBUCK -->|"PG"| VOICEPGQ -->|"qualified POWER_FAULT_N"| SLOW
  CHARGER -->|"SYS"| EXTBUCK --> EXTL --> EXTFUSE -->|"protected fixed 5.0 V"| U214
  CHARGER -->|"SYS local bulk"| EXTBUCKIN
  CHARGER -->|"SYS local HF"| EXTBUCKHF
  EXTL -->|"feedback"| EXTBUCKFBT --> EXTBUCKFBB
  EXTL -->|"feed-forward"| EXTBUCKFF
  EXTL -->|"local output bank"| EXTBUCKOUT0
  EXTL -->|"local output bank"| EXTBUCKOUT1
  EXTBUCK -->|"EN fail-low"| EXTENPD
  MAINL -->|"PG pull-up"| EXTPGPU --> EXTBUCK
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
  SWSD --> SD
  SWCODEC --> CODEC
  SWRX --> SI
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
  S3 <-->|"I²C0 + interrupt"| SLOW
  S3 -->|"direct QSPI + touch"| LCD
  S3 <-->|"scheduled SPI2"| SD
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
  `GPIO4,GPIO5,GPIO35,GPIO36,GPIO38,GPIO39,GPIO40,GPIO41,GPIO42` — direct QSPI
  and the only scheduled high-rate shared pair.
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
- **Resource result:** S3 `32 used / 3 reserved / 1 free`, C5 `14/6/1`, RP
  `48/0/0` and slow I/O `24/0/0`. Independent SWD/USB/RUN/BOOTSEL are outside
  this GPIO budget.

[Complete physical pad and net atlas](docs/review/architecture/generated/G2F-3I-principled-pinout.md)

</details>

## Physical design and controls

- The display is portrait-oriented; the waterfall redraws small regions and
  never blocks radio service.
- Nine labelled antenna ports retain an unambiguous association between each
  connector, radio path and active antenna profile.
- The removable U214 mounts across the rear above the batteries while keeping
  its own antennas and connectors accessible.
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
