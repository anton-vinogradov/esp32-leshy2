# G2F-3I — generated principled pinout atlas

- Статус: **машинная принципиальная распиновка ведущего paper candidate; не target architecture**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`
- Verify: `python3 hardware/architecture/generate.py --check`

> Файл сгенерирован. Ручные изменения будут отвергнуты `--check`.

## Как читать артефакт

Диаграмма — навигатор по owners и физически независимым interface groups.
Она намеренно строится сверху вниз и остаётся живой проекцией текущей
начинки: изменение machine source обязано регенерировать этот atlas и
синхронно обновить обе стартовые диаграммы.
Каждый прямоугольник физического устройства содержит его exact/current
paper MPN и роль. Разные устройства не объединяются в один прямоугольник.
Если production part ещё не выбран, узел явно помечается `MPN TBD`;
пассивная цепь отдельно помечается как circuit, а не как заказной компонент.
Нормативные pin/net значения находятся в следующих за ней таблицах и
получены из того же JSON. `abstract:*` означает зарезервированную функцию,
для которой exact peripheral MPN/electrical circuit ещё не принят; это не
разрешение рисовать вымышленный pin в KiCad.

## Принципиальная структура owners и pin groups

```mermaid
flowchart TD
  subgraph POWER_INPUT["Sink-only USB-PD and replaceable-cell power path"]
  PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>product USB-C receptacle: protected S3 USB2 data and sink-only power"]
  PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>CC1/CC2 and USB2 D+/D- short-to-VBUS/ESD protector"]
  PRODUCT_USB_DP_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm S3 USB Full-Speed D+ series resistor"]
  PRODUCT_USB_DM_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm S3 USB Full-Speed D- series resistor"]
  PRODUCT_USB_VBIAS_CAP["TDK C1608X7S2A104K080AB<br/>100-nF 100-V port-protector VBIAS capacitor"]
  PRODUCT_USB_VPWR_CAP["TDK C1608X7R1C105K080AC<br/>1-uF 16-V port-protector VPWR capacitor"]
  PRODUCT_USB_FAULT_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm port-protector fault pull-up"]
  PD_CC1_CAP["Murata GRM1555C1H221JA01D<br/>220-pF C0G protected USB-C CC1 capacitor"]
  PD_CC2_CAP["Murata GRM1555C1H221JA01D<br/>220-pF C0G protected USB-C CC2 capacitor"]
  PD_VBUS_TVS["Texas Instruments TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection"]
  PD_CONTROLLER["Texas Instruments TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path"]
  PD_CONFIG_EEPROM["onsemi CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM"]
  NVDC_CHARGER["Texas Instruments BQ25798RQMR<br/>2S-configured buck-boost charger and NVDC system power path"]
  PACK_HOLDER["Keystone Electronics 1048P<br/>polarized dual protected-button-top 18650 retention and four independent contacts"]
  PACK_CELL0["XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #0"]
  PACK_FUSE0["Littelfuse 0451005.MRL<br/>slot-0 independent 5-A fast fuse"]
  PACK_NTC0["TDK B57332V5103F360<br/>cell-0 temperature sensor"]
  PACK_CELL1["XTAR 18650 4000mAh<br/>individually replaceable protected button-top 4-Ah cell #1"]
  PACK_FUSE1["Littelfuse 0451005.MRL<br/>slot-1 independent 5-A fast fuse"]
  PACK_NTC1["TDK B57332V5103F360<br/>cell-1 temperature sensor"]
  PACK_GAUGE["Analog Devices MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing"]
  PACK_SHUNT["Vishay WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACK_POWER_FET["Texas Instruments CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair"]
  PACK_HOLD["Diodes Incorporated 2N7002DW-7-F<br/>reset-default ALRT hold and explicit release"]
  PACK_SUPPLY_OR["onsemi BAV70LT1G<br/>AOLDO/fixture source isolation"]
  PACK_SYSTEM_DIODE["Diodes Incorporated BAT54-7-F<br/>admitted-system source isolation and priority"]
  PACK_ADMISSION["Texas Instruments MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge"]
  PACK_DIAG_TIMER["Texas Instruments TPUL2G223BQBR<br/>non-retriggerable pulse limiter and refractory lockout"]
  PACK_DIAG_TIMER_RES["Yageo RC0402FR-07169KL<br/>169-kOhm 1% diagnostic-pulse timing resistor"]
  PACK_DIAG_TIMER_CAP["Murata GRM31C5C1H224JE02L<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor"]
  PACK_DIAG_LOCKOUT_RES["Yageo RC0402FR-07620KL<br/>620-kOhm 1% refractory-lockout timing resistor"]
  PACK_DIAG_LOCKOUT_CAP["TDK C1608X7R1C105K080AC<br/>1-uF 16-V X7R refractory-lockout timing capacitor"]
  PACK_DIAG_TIMER_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R one-shot bypass capacitor"]
  PACK_DIAG_TRIGGER_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-trigger fail-low resistor"]
  PACK_DIAG_GATE_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-gate fail-low resistor"]
  PACK_DIAG_SWITCH["Diodes Incorporated DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET"]
  PACK_DIAG_RES0["Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #0"]
  PACK_DIAG_RES1["Bourns CRM2512-FX-20R0ELF<br/>20-Ohm 2-W pulse-rated diagnostic-load branch #1"]
  PACK_MID_ADC_TOP0["Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #0"]
  PACK_MID_ADC_TOP1["Yageo RC0402FR-07220KL<br/>220-kOhm 1% midpoint-divider top resistor #1"]
  PACK_MID_ADC_BOTTOM["Yageo RC0402FR-07169KL<br/>169-kOhm 1% midpoint-divider bottom resistor"]
  PACK_MID_ADC_FILTER["Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R midpoint ADC filter capacitor"]
  PACK_STACK_ADC_TOP0["Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #0"]
  PACK_STACK_ADC_TOP1["Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #1"]
  PACK_STACK_ADC_TOP2["Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #2"]
  PACK_STACK_ADC_TOP3["Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #3"]
  PACK_STACK_ADC_TOP4["Yageo RC0402FR-07220KL<br/>220-kOhm 1% stack-divider top resistor #4"]
  PACK_STACK_ADC_BOTTOM["Yageo RC0402FR-07169KL<br/>169-kOhm 1% stack-divider bottom resistor"]
  PACK_STACK_ADC_FILTER["Murata GRM155R71H103KA88D<br/>10-nF 50-V X7R stack ADC filter capacitor"]
  end
  subgraph POWER_RAILS["Independent fixed rails and quiet-state switches"]
  AON_BUCK["Texas Instruments TPS629203DRLR<br/>low-IQ always-on 3.3-V safety converter"]
  AON_INDUCTOR["Sunlord WPN201612H2R2MT<br/>2.2-uH shielded AON converter inductor"]
  AON_MODE_RES["Yageo RC0402FR-0742K2L<br/>42.2-kOhm 1% AON mode/configuration resistor"]
  AON_INPUT_CAP["TDK CGA5L1X7R1E475K160AC<br/>4.7-uF 25-V X7R AON input capacitor"]
  AON_OUTPUT_CAP["Murata GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON raw-output capacitor"]
  AON_EFUSE["Texas Instruments TPS25961DRVR<br/>independent AON overvoltage/current/short cutoff"]
  AON_EFUSE_RILIM["Yageo RC0402FR-07240KL<br/>240-kOhm 1% AON eFuse current-limit resistor"]
  AON_EFUSE_OVLO_TOP["Yageo RC0402FR-07196KL<br/>196-kOhm 1% AON eFuse OVLO top resistor"]
  AON_EFUSE_OVLO_BOTTOM["Yageo RC0402FR-07100KL<br/>100-kOhm 1% AON eFuse OVLO bottom resistor"]
  AON_EFUSE_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R AON eFuse input capacitor"]
  AON_EFUSE_OUTPUT_CAP["Murata GRM188R60J106ME47D<br/>10-uF 6.3-V X5R protected-AON output capacitor"]
  AON_PG_PULLUP["Yageo RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor"]
  MAIN_BUCK["Texas Instruments TPS564252DRLR<br/>fixed 3.3-V 4-A main converter"]
  MAIN_INDUCTOR["Sunlord MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor"]
  MAIN_INPUT_CAP["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main-converter bulk input capacitor"]
  MAIN_HF_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R main-converter HF input capacitor"]
  MAIN_FB_TOP["Yageo RC0402FR-0745K3L<br/>45.3-kOhm 1% main feedback top resistor"]
  MAIN_FB_BOTTOM["Yageo RC0402FR-0710KL<br/>10-kOhm 1% main feedback bottom resistor"]
  MAIN_FF_CAP["KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G main feed-forward capacitor"]
  MAIN_OUTPUT_CAP0["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #0"]
  MAIN_OUTPUT_CAP1["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main raw-output capacitor #1"]
  MAIN_EFUSE["Texas Instruments TPS25974LRPWR<br/>main latch-off overvoltage circuit-breaker eFuse with protected PG"]
  MAIN_EFUSE_RILM["Yageo RC0402FR-071K65L<br/>1.65-kOhm 1% main eFuse threshold resistor"]
  MAIN_EFUSE_DVDT_CAP["Murata GRM155R71H472KA01D<br/>4.7-nF 50-V X7R main eFuse slew capacitor"]
  MAIN_EFUSE_ITIMER_CAP["Murata GRM1555C1H121JA01D<br/>120-pF 50-V C0G main eFuse transient timer"]
  MAIN_EFUSE_OVLO_TOP["Yageo RT0402BRD07191KL<br/>191-kOhm 0.1% main eFuse OVLO top resistor"]
  MAIN_EFUSE_OVLO_BOTTOM["Yageo RT0402BRD07100KL<br/>100-kOhm 0.1% main eFuse OVLO bottom resistor"]
  MAIN_EFUSE_PG_TOP["Yageo RC0402FR-0745K3L<br/>45.3-kOhm 1% main protected-PG top resistor"]
  MAIN_EFUSE_PG_BOTTOM["Yageo RC0402FR-0730KL<br/>30-kOhm 1% main protected-PG bottom resistor"]
  MAIN_EFUSE_OUTPUT_CAP["Murata GRM188R60J106ME47D<br/>10-uF 6.3-V X5R protected-main output capacitor"]
  MAIN_EN_PULLDOWN["Yageo RC0402FR-07100KL<br/>100-kOhm 1% main-enable fail-low resistor"]
  POWER_FAULT_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm 1% wired-low power-fault pull-up resistor"]
  VOICE_BUCK["Texas Instruments TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter"]
  VOICE_INDUCTOR["Sunlord MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor"]
  VOICE_INPUT_CAP["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice-converter bulk input capacitor"]
  VOICE_HF_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R voice-converter HF input capacitor"]
  VOICE_FB_TOP["Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor"]
  VOICE_FB_BOTTOM["Yageo RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor"]
  VOICE_FF_CAP["KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G voice feed-forward capacitor"]
  VOICE_OUTPUT_CAP0["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #0"]
  VOICE_OUTPUT_CAP1["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice raw-output capacitor #1"]
  VOICE_EFUSE["Texas Instruments TPS25974LRPWR<br/>voice latch-off overvoltage circuit-breaker eFuse with protected PG"]
  VOICE_EFUSE_RILM["Yageo RC0402FR-073K32L<br/>3.32-kOhm 1% voice eFuse threshold resistor"]
  VOICE_EFUSE_DVDT_CAP["Murata GRM155R71H472KA01D<br/>4.7-nF 50-V X7R voice eFuse slew capacitor"]
  VOICE_EFUSE_ITIMER_CAP["Murata GRM1555C1H121JA01D<br/>120-pF 50-V C0G voice eFuse transient timer"]
  VOICE_EFUSE_OVLO_TOP["Yageo RC0402FR-07270KL<br/>270-kOhm 1% voice eFuse OVLO top resistor"]
  VOICE_EFUSE_OVLO_BOTTOM["Yageo RC0402FR-07100KL<br/>100-kOhm 1% voice eFuse OVLO bottom resistor"]
  VOICE_EFUSE_PG_TOP["Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice protected-PG top resistor"]
  VOICE_EFUSE_PG_BOTTOM["Yageo RC0402FR-0733KL<br/>33-kOhm 1% voice protected-PG bottom resistor"]
  VOICE_EFUSE_OUTPUT_CAP["Murata GRM188R60J106ME47D<br/>10-uF 6.3-V X5R protected-voice output capacitor"]
  VOICE_EN_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice-enable fail-low resistor"]
  VOICE_PG_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm 1% voice power-good pull-up resistor"]
  VOICE_PG_BASE_RES["Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice PG-qualifier base resistor"]
  VOICE_PG_QUALIFIER["Diodes Incorporated MMBT3904-7-F<br/>voice-rail enable-qualified PG fault transistor"]
  EXT_BUCK["Texas Instruments TPS564252DRLR<br/>fixed 5.0-V 4-A accessory converter"]
  EXT_INDUCTOR["Sunlord MWSA0503S-4R7MT<br/>4.7-uH accessory-rail power inductor"]
  EXT_BUCK_INPUT_CAP["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory-converter bulk input capacitor"]
  EXT_BUCK_HF_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R accessory-converter HF input capacitor"]
  EXT_BUCK_FB_TOP["Yageo RC0402FR-07220KL<br/>220-kOhm 1% accessory feedback top resistor"]
  EXT_BUCK_FB_BOTTOM["Yageo RC0402FR-0730KL<br/>30-kOhm 1% accessory feedback bottom resistor"]
  EXT_BUCK_FF_CAP["KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G accessory feed-forward capacitor"]
  EXT_BUCK_OUTPUT_CAP0["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #0"]
  EXT_BUCK_OUTPUT_CAP1["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R accessory output capacitor #1"]
  EXT_EN_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory-enable fail-low resistor"]
  EXT_PG_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm 1% accessory power-good pull-up resistor"]
  EXT_PG_BASE_RES["Yageo RC0402FR-0768KL<br/>68-kOhm 1% accessory PG-qualifier base resistor"]
  EXT_PG_QUALIFIER["Diodes Incorporated MMBT3904-7-F<br/>accessory-rail enable-qualified PG fault transistor"]
  EXT_EFUSE["Texas Instruments TPS259470LRPWR<br/>true-reverse-blocking latch-off accessory eFuse and current monitor"]
  EXT_RILM["Yageo RC0402FR-072K21L<br/>2.21-kOhm 1% eFuse current-limit resistor"]
  EXT_DVDT_CAP["Murata GRM155R71H472KA01D<br/>4.7-nF 50-V X7R eFuse startup-slew capacitor"]
  EXT_ITIMER_CAP["Murata GRM188R71E224KA88D<br/>220-nF 25-V X7R post-start transient-timer capacitor"]
  EXT_OVLO_TOP["Yageo RC0402FR-07169KL<br/>169-kOhm 1% eFuse OVLO top resistor"]
  EXT_OVLO_BOTTOM["Yageo RC0402FR-0747KL<br/>47-kOhm 1% eFuse OVLO bottom resistor"]
  EXT_INPUT_CAP["Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse input capacitor"]
  EXT_OUTPUT_CAP["Murata GRM21BR71E225KE11L<br/>2.2-uF 25-V X7R local eFuse output capacitor"]
  EXT_BLEEDER["Yageo RC0603FR-071KL<br/>1-kOhm 1% protected-output discharge resistor"]
  NRF_POWER_SWITCH["Texas Instruments TPS22919DCKR<br/>three-radio nRF quiet-state load switch"]
  CC_POWER_SWITCH["Texas Instruments TPS22919DCKR<br/>CC1101 quiet-state load switch"]
  SD_POWER_SWITCH["Texas Instruments TPS22919DCKR<br/>microSD quiet-state load switch"]
  CODEC_POWER_SWITCH["Texas Instruments TPS22919DCKR<br/>ES8311 quiet-state load switch"]
  RECEIVER_POWER_SWITCH["Texas Instruments TPS22919DCKR<br/>Si4732 quiet-state load switch"]
  end
  subgraph COMPUTE["Compute owners"]
  S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display/storage, audio, BLE/Wi-Fi owner"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, IEEE 802.15.4 and IR owner"]
  RP["RP2354B A4 (exact A4 order/lot identity required before BOM freeze)<br/>deterministic radio and voice owner"]
  end
  subgraph UI_STORAGE["UI and storage devices"]
  DISPLAY_CONNECTOR["Hirose FH12-40S-0.5SH(55)<br/>first 40-position 0.5-mm bottom-contact ZIF panel-mate candidate"]
  DISPLAY["HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  DISPLAY_LOGIC_BULK_CAP["Murata GRM188R60J106ME47D<br/>10-uF protected-main display-logic bulk capacitor"]
  DISPLAY_LOGIC_HF_CAP["TDK C1005X7R1H104K050BB<br/>100-nF display-logic high-frequency bypass capacitor"]
  DISPLAY_RESET_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm display RESX reset-default pull-down"]
  TOUCH_RESET_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm touch TP_RESXP reset-default pull-down"]
  BACKLIGHT_EFUSE["Texas Instruments TPS2553DRVR-1<br/>latch-off and reverse-blocking LEDA power switch"]
  BACKLIGHT_EFUSE_ILIM["Yageo RC0402FR-07133KL<br/>133-kOhm 1% approximately 200-mA backlight-limit resistor"]
  BACKLIGHT_EFUSE_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF backlight-switch input bypass capacitor"]
  BACKLIGHT_EFUSE_OUTPUT_BULK["Murata GRM188R60J106ME47D<br/>10-uF protected-LEDA output bulk capacitor"]
  BACKLIGHT_EFUSE_OUTPUT_HF["TDK C1005X7R1H104K050BB<br/>100-nF protected-LEDA output bypass capacitor"]
  BACKLIGHT_FAULT_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm open-drain backlight-fault pull-up"]
  BACKLIGHT_SERIES_RESISTOR["Panasonic ERJ-P08F10R0V<br/>10-Ohm 0.66-W anti-surge LED cathode resistor"]
  BACKLIGHT_MOSFET["Diodes Incorporated DMN2056U-7<br/>low-gate-drive LED cathode PWM MOSFET"]
  BACKLIGHT_GATE_SERIES["Yageo RC0402FR-07100RL<br/>100-Ohm PWM gate series resistor"]
  BACKLIGHT_GATE_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm PWM gate reset-off pull-down"]
  SD["Hirose DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SD_HOST_BUFFER["SN74LVC3G34DCUR<br/>three-channel Ioff SCK/CMD/CS card-side buffer"]
  SD_MISO_BUFFER["Texas Instruments SN74LVC1G125DCKR<br/>CS-gated Ioff DAT0/MISO return buffer"]
  SD_ESD_A["Texas Instruments TPD4E05U06DQAR<br/>four-channel low-capacitance microSD signal ESD array A"]
  SD_ESD_B["Texas Instruments TPD4E05U06DQAR<br/>four-channel low-capacitance microSD supply/signal/detect ESD array B"]
  SD_POWER_INPUT_CAP["TDK C1608X7R1C105K080AC<br/>1-uF storage-switch input bypass capacitor"]
  SD_POWER_BULK_CAP["Murata GRM21BR60J226ME39L<br/>22-uF switched-card bulk capacitor"]
  SD_POWER_HF_CAP["TDK C1005X7R1H104K050BB<br/>100-nF switched-card high-frequency bypass capacitor"]
  SD_HOST_BUFFER_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF triple-buffer bypass capacitor"]
  SD_MISO_BUFFER_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF return-buffer bypass capacitor"]
  SD_ON_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm storage-power reset-off pull-down"]
  SD_HOST_SCK_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm shared-clock reset-low pull-down"]
  SD_HOST_D0_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm shared-D0 reset-high pull-up"]
  SD_HOST_D1_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm shared-D1 reset-high pull-up"]
  SD_HOST_CS_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm card-CS reset-high pull-up"]
  LCD_HOST_CS_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm display-CS reset-high pull-up"]
  SD_CARD_CMD_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm switched-card CMD pull-up"]
  SD_CARD_DAT0_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm switched-card DAT0 pull-up"]
  SD_CARD_DAT1_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm switched-card DAT1 pull-up"]
  SD_CARD_DAT2_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm switched-card DAT2 pull-up"]
  SD_CARD_DAT3_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm switched-card DAT3/CS pull-up"]
  SD_SCK_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm buffered-card clock source-series resistor"]
  SD_CMD_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm buffered-card CMD source-series resistor"]
  SD_CS_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm buffered-card CS source-series resistor"]
  SD_MISO_SERIES["Panasonic ERJ-2RKF22R0X<br/>22-Ohm card-MISO buffer source-series resistor"]
  SD_DETECT_SERIES["Yageo RC0603FR-071KL<br/>1-kOhm card-detect input series resistor"]
  SD_DETECT_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm always-readable card-detect pull-up"]
  SD_DETECT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF card-detect hardware filter capacitor"]
  SLOW_IO["TCA6424ARGJR<br/>24-line main slow-control expander; six contacts free"]
  UI_MATRIX_IO["TCA9534APWR<br/>dedicated interrupt-capable 4x3 ordinary-control expander"]
  UI_MATRIX_IO_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF UI-expander bypass capacitor"]
  UI_MATRIX_ROW0_PULLDOWN["Yageo RC0603FR-071KL<br/>1-kOhm row-0 reset/idle pull-down"]
  UI_MATRIX_ROW1_PULLDOWN["Yageo RC0603FR-071KL<br/>1-kOhm row-1 reset/idle pull-down"]
  UI_MATRIX_ROW2_PULLDOWN["Yageo RC0603FR-071KL<br/>1-kOhm row-2 reset/idle pull-down"]
  UI_MATRIX_ROW3_PULLDOWN["Yageo RC0603FR-071KL<br/>1-kOhm row-3 reset/idle pull-down"]
  UI_MATRIX_COL0_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm ordinary-matrix column-0 pull-up"]
  UI_MATRIX_COL1_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm ordinary-matrix column-1 pull-up"]
  UI_MATRIX_COL2_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm ordinary-matrix column-2 pull-up"]
  UI_MATRIX_DIODE_UP["onsemi 1N4148WT<br/>D-pad UP matrix-isolation diode"]
  UI_MATRIX_DIODE_DOWN["onsemi 1N4148WT<br/>D-pad DOWN matrix-isolation diode"]
  UI_MATRIX_DIODE_LEFT["onsemi 1N4148WT<br/>D-pad LEFT matrix-isolation diode"]
  UI_MATRIX_DIODE_RIGHT["onsemi 1N4148WT<br/>D-pad RIGHT matrix-isolation diode"]
  UI_MATRIX_DIODE_OK["onsemi 1N4148WT<br/>D-pad OK matrix-isolation diode"]
  UI_MATRIX_DIODE_BACK["onsemi 1N4148WT<br/>BACK matrix-isolation diode"]
  UI_MATRIX_DIODE_OPT["onsemi 1N4148WT<br/>OPT matrix-isolation diode"]
  UI_MATRIX_DIODE_F1["onsemi 1N4148WT<br/>F1 matrix-isolation diode"]
  UI_MATRIX_DIODE_F2["onsemi 1N4148WT<br/>F2 matrix-isolation diode"]
  UI_MATRIX_DIODE_ENCODER["onsemi 1N4148WT<br/>encoder-push matrix-isolation diode"]
  UI_UP["MPN TBD<br/>D-pad UP ordinary control"]
  UI_DOWN["MPN TBD<br/>D-pad DOWN ordinary control"]
  UI_LEFT["MPN TBD<br/>D-pad LEFT ordinary control"]
  UI_RIGHT["MPN TBD<br/>D-pad RIGHT ordinary control"]
  UI_OK["MPN TBD<br/>D-pad OK ordinary control"]
  UI_BACK["MPN TBD<br/>BACK ordinary control"]
  UI_OPT["MPN TBD<br/>OPT ordinary control"]
  UI_F1["MPN TBD<br/>F1 ordinary control"]
  UI_F2["MPN TBD<br/>F2 ordinary control"]
  ENCODER["Alps Alpine EC11E18244AU<br/>36-detent/18-pulse rotary encoder with push"]
  ENCODER_A_PULLUP["Yageo RC0402FR-073K32L<br/>3.32-kOhm encoder-phase-A contact-current pull-up"]
  ENCODER_B_PULLUP["Yageo RC0402FR-073K32L<br/>3.32-kOhm encoder-phase-B contact-current pull-up"]
  TOUCH_IRQ_BUFFER["SN74LVC1G07DCKR<br/>open-drain touch-interrupt polarity adapter"]
  TOUCH_IRQ_BUFFER_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF touch-interrupt-buffer bypass capacitor"]
  TOUCH_IRQ_ALT["SN74LVC1G06DCKR (DNP alternative)<br/>pin-compatible active-high TP_INT inverter option"]
  end
  subgraph AUDIO_PATH["Broadcast, voice and fail-safe audio devices"]
  RECEIVER["Si4732-A10-GS<br/>AM/FM/SW/LW broadcast receiver"]
  MONOSUM["MPN-independent passive circuit<br/>Si4732 stereo-to-mono summing network"]
  AUDIO_RX_MUX["Texas Instruments SN74LVC1G3157DBVR<br/>Si4732/SA518 receive-audio source selector"]
  CAPNET["MPN-independent passive circuit<br/>high-impedance AC/bias capture network"]
  AUDIO_CAPTURE_BUFFER["Texas Instruments TLV9061IDBVR<br/>active high-impedance capture buffer"]
  ADCNET["MPN-independent passive circuit<br/>ES8311 mic-range differential input network"]
  CODEC["Everest Semiconductor ES8311<br/>mono ADC/DAC audio codec"]
  AUDIO_SPEAKER_SELECTOR["Texas Instruments TMUX1136DGSR<br/>dual differential speaker-path selector"]
  SPEAKER_AMP["Diodes Incorporated PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPEAKER["MPN TBD<br/>internal loudspeaker"]
  TXATT["MPN-independent passive circuit<br/>35–45 dB codec-to-voice attenuator/filter"]
  AUDIO_TX_SELECTOR["Texas Instruments TS5A63157DCKR<br/>electret/codec transmit-audio selector"]
  MIC["MPN TBD<br/>electret microphone"]
  AUDIO_SAFE_GATE["Texas Instruments SN74LVC2G08DCUR<br/>reset-safe dual selector-request gate"]
  VOICE["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  end
  subgraph RADIO_ACCESSORY["Radio and external-accessory devices"]
  NRF0["Ebyte E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["Ebyte E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["Ebyte E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  U214_I2C_ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  end
  subgraph IR_PATH["IR frontend devices"]
  IRDEMOD["MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver"]
  IRCARRIER["MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver"]
  IRTX["MPN TBD (TSAL6200 screened)<br/>IR transmit LED and fail-safe driver endpoint"]
  end
  subgraph SAFETY_STOP["AON hard-STOP devices"]
  PTTSW["MPN TBD<br/>separate normally-open hold-to-talk PTT control"]
  STOPSW["MPN TBD<br/>normally-closed physical STOP control"]
  REARMSW["MPN TBD<br/>normally-open recessed RE-ARM control"]
  SAFE_SUPERVISOR["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
  SAFE_POR_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm 1% AON POR pull-up resistor"]
  SAFE_CONDITIONER["74LVC2G14GW,125<br/>STOP and RE-ARM Schmitt conditioner"]
  SAFE_POR_OR["74LVC1G32GV,125<br/>STOP-dominant POR/clear combiner"]
  SAFE_LATCH["SN74LVC1G74DCUR<br/>asynchronous latched hard STOP"]
  SAFE_RESET_BUFFER["SN74LVC3G34DCUR<br/>Ioff three-domain reset fan-out"]
  SAFE_GATE_A["SN74LVC08APWR<br/>four STOP-dominant nRF request gates"]
  SAFE_GATE_B["SN74LVC08APWR<br/>four STOP-dominant rail/IR/accessory gates"]
  SAFE_PTT_OR["74LVC1G32GV,125<br/>active-low voice PTT force-RX gate"]
  STOP_LED["LTST-C190KFKT<br/>orange physical latched-STOP indicator"]
  end
  subgraph TX_EVIDENCE["Per-path physical TX-evidence devices"]
  DET_S3["LTC5532ES6#TRMPBF<br/>S3 2.4-GHz RF power detector"]
  DET_C5["LTC5532ES6#TRMPBF<br/>C5 2.4/5-GHz RF power detector"]
  DET_NRF0["LTC5532ES6#TRMPBF<br/>nRF0 2.4-GHz RF power detector"]
  DET_NRF1["LTC5532ES6#TRMPBF<br/>nRF1 2.4-GHz RF power detector"]
  DET_NRF2["LTC5532ES6#TRMPBF<br/>nRF2 2.4-GHz RF power detector"]
  DET_CC["LTC5507ES6#TRMPBF<br/>CC1101 sub-GHz RF power detector"]
  DET_VOICE["LTC5507ES6#TRMPBF<br/>SA518 VHF/UHF RF power detector"]
  DET_IR["VEMD1060X01<br/>IR optical-evidence photodiode"]
  EVIDENCE_CMP_A["TLV1824PWR<br/>S3/C5/nRF0/nRF1 evidence thresholds"]
  EVIDENCE_CMP_B["TLV1824PWR<br/>nRF2/CC/voice/IR evidence thresholds"]
  EVIDENCE_MASK["TCA9534APWR<br/>eight-bit evidence source mask on local RP I2C0"]
  EVIDENCE_OR_0["BAT54ALT1G<br/>evidence diode-OR pair 0/1"]
  EVIDENCE_OR_1["BAT54ALT1G<br/>evidence diode-OR pair 2/3"]
  EVIDENCE_OR_2["BAT54ALT1G<br/>evidence diode-OR pair 4/5"]
  EVIDENCE_OR_3["BAT54ALT1G<br/>evidence diode-OR pair 6/7"]
  ANY_TX_LED["LTST-C190KRKT<br/>red physical ANY-TX indicator"]
  end
  %% Layout-only invisible spine: these links are not electrical connections.
  PRODUCT_USB_CONNECTOR ~~~ PRODUCT_USB_PROTECTOR ~~~ PRODUCT_USB_DP_SERIES ~~~ PRODUCT_USB_DM_SERIES ~~~ PRODUCT_USB_VBIAS_CAP ~~~ PRODUCT_USB_VPWR_CAP ~~~ PRODUCT_USB_FAULT_PULLUP ~~~ PD_CC1_CAP ~~~ PD_CC2_CAP ~~~ PD_VBUS_TVS ~~~ PD_CONTROLLER ~~~ PD_CONFIG_EEPROM ~~~ NVDC_CHARGER
  NVDC_CHARGER ~~~ PACK_HOLDER ~~~ PACK_CELL0 ~~~ PACK_FUSE0 ~~~ PACK_NTC0 ~~~ PACK_CELL1 ~~~ PACK_FUSE1 ~~~ PACK_NTC1
  PACK_NTC1 ~~~ PACK_GAUGE ~~~ PACK_SHUNT ~~~ PACK_POWER_FET ~~~ PACK_HOLD ~~~ PACK_SUPPLY_OR ~~~ PACK_SYSTEM_DIODE ~~~ PACK_ADMISSION
  PACK_ADMISSION ~~~ PACK_DIAG_TIMER ~~~ PACK_DIAG_TIMER_RES ~~~ PACK_DIAG_TIMER_CAP ~~~ PACK_DIAG_LOCKOUT_RES ~~~ PACK_DIAG_LOCKOUT_CAP ~~~ PACK_DIAG_TIMER_BYPASS ~~~ PACK_DIAG_TRIGGER_PULLDOWN ~~~ PACK_DIAG_GATE_PULLDOWN
  PACK_DIAG_GATE_PULLDOWN ~~~ PACK_DIAG_SWITCH ~~~ PACK_DIAG_RES0 ~~~ PACK_DIAG_RES1 ~~~ PACK_MID_ADC_TOP0 ~~~ PACK_MID_ADC_TOP1 ~~~ PACK_MID_ADC_BOTTOM ~~~ PACK_MID_ADC_FILTER
  PACK_MID_ADC_FILTER ~~~ PACK_STACK_ADC_TOP0 ~~~ PACK_STACK_ADC_TOP1 ~~~ PACK_STACK_ADC_TOP2 ~~~ PACK_STACK_ADC_TOP3 ~~~ PACK_STACK_ADC_TOP4 ~~~ PACK_STACK_ADC_BOTTOM ~~~ PACK_STACK_ADC_FILTER
  PACK_STACK_ADC_FILTER ~~~ AON_BUCK ~~~ AON_INDUCTOR ~~~ AON_MODE_RES ~~~ AON_INPUT_CAP ~~~ AON_OUTPUT_CAP ~~~ AON_EFUSE ~~~ AON_EFUSE_RILIM ~~~ AON_EFUSE_OVLO_TOP ~~~ AON_EFUSE_OVLO_BOTTOM ~~~ AON_EFUSE_INPUT_CAP ~~~ AON_EFUSE_OUTPUT_CAP ~~~ AON_PG_PULLUP
  AON_PG_PULLUP ~~~ MAIN_BUCK ~~~ MAIN_INDUCTOR ~~~ MAIN_INPUT_CAP ~~~ MAIN_HF_INPUT_CAP ~~~ MAIN_FB_TOP ~~~ MAIN_FB_BOTTOM ~~~ MAIN_FF_CAP ~~~ MAIN_OUTPUT_CAP0 ~~~ MAIN_OUTPUT_CAP1 ~~~ MAIN_EFUSE ~~~ MAIN_EFUSE_RILM ~~~ MAIN_EFUSE_DVDT_CAP ~~~ MAIN_EFUSE_ITIMER_CAP ~~~ MAIN_EFUSE_OVLO_TOP ~~~ MAIN_EFUSE_OVLO_BOTTOM ~~~ MAIN_EFUSE_PG_TOP ~~~ MAIN_EFUSE_PG_BOTTOM ~~~ MAIN_EFUSE_OUTPUT_CAP ~~~ MAIN_EN_PULLDOWN ~~~ POWER_FAULT_PULLUP
  POWER_FAULT_PULLUP ~~~ VOICE_BUCK ~~~ VOICE_INDUCTOR ~~~ VOICE_INPUT_CAP ~~~ VOICE_HF_INPUT_CAP ~~~ VOICE_FB_TOP ~~~ VOICE_FB_BOTTOM ~~~ VOICE_FF_CAP ~~~ VOICE_OUTPUT_CAP0 ~~~ VOICE_OUTPUT_CAP1 ~~~ VOICE_EFUSE ~~~ VOICE_EFUSE_RILIM ~~~ VOICE_EFUSE_DVDT_CAP ~~~ VOICE_EFUSE_ITIMER_CAP ~~~ VOICE_EFUSE_OVLO_TOP ~~~ VOICE_EFUSE_OVLO_BOTTOM ~~~ VOICE_EFUSE_PG_TOP ~~~ VOICE_EFUSE_PG_BOTTOM ~~~ VOICE_EFUSE_OUTPUT_CAP ~~~ VOICE_EN_PULLDOWN ~~~ VOICE_PG_PULLUP ~~~ VOICE_PG_BASE_RES ~~~ VOICE_PG_QUALIFIER
  VOICE_PG_QUALIFIER ~~~ EXT_BUCK ~~~ EXT_INDUCTOR ~~~ EXT_BUCK_INPUT_CAP ~~~ EXT_BUCK_HF_INPUT_CAP ~~~ EXT_BUCK_FB_TOP ~~~ EXT_BUCK_FB_BOTTOM ~~~ EXT_BUCK_FF_CAP ~~~ EXT_BUCK_OUTPUT_CAP0 ~~~ EXT_BUCK_OUTPUT_CAP1 ~~~ EXT_EN_PULLDOWN ~~~ EXT_PG_PULLUP ~~~ EXT_PG_BASE_RES ~~~ EXT_PG_QUALIFIER ~~~ EXT_EFUSE
  EXT_EFUSE ~~~ EXT_RILM ~~~ EXT_DVDT_CAP ~~~ EXT_ITIMER_CAP ~~~ EXT_OVLO_TOP ~~~ EXT_OVLO_BOTTOM
  EXT_OVLO_BOTTOM ~~~ EXT_INPUT_CAP ~~~ EXT_OUTPUT_CAP ~~~ EXT_BLEEDER ~~~ NRF_POWER_SWITCH ~~~ CC_POWER_SWITCH ~~~ SD_POWER_SWITCH ~~~ CODEC_POWER_SWITCH ~~~ RECEIVER_POWER_SWITCH ~~~ S3 ~~~ SLOW_IO
  SLOW_IO ~~~ UI_MATRIX_IO ~~~ UI_MATRIX_IO_BYPASS ~~~ UI_MATRIX_ROW0_PULLDOWN ~~~ UI_MATRIX_ROW1_PULLDOWN ~~~ UI_MATRIX_ROW2_PULLDOWN ~~~ UI_MATRIX_ROW3_PULLDOWN ~~~ UI_MATRIX_COL0_PULLUP ~~~ UI_MATRIX_COL1_PULLUP ~~~ UI_MATRIX_COL2_PULLUP
  UI_MATRIX_COL2_PULLUP ~~~ UI_MATRIX_DIODE_UP ~~~ UI_UP ~~~ UI_MATRIX_DIODE_DOWN ~~~ UI_DOWN ~~~ UI_MATRIX_DIODE_LEFT ~~~ UI_LEFT
  UI_LEFT ~~~ UI_MATRIX_DIODE_RIGHT ~~~ UI_RIGHT ~~~ UI_MATRIX_DIODE_OK ~~~ UI_OK ~~~ UI_MATRIX_DIODE_BACK ~~~ UI_BACK
  UI_BACK ~~~ UI_MATRIX_DIODE_OPT ~~~ UI_OPT ~~~ UI_MATRIX_DIODE_F1 ~~~ UI_F1 ~~~ UI_MATRIX_DIODE_F2 ~~~ UI_F2
  UI_F2 ~~~ UI_MATRIX_DIODE_ENCODER ~~~ ENCODER ~~~ ENCODER_A_PULLUP ~~~ ENCODER_B_PULLUP ~~~ TOUCH_IRQ_BUFFER ~~~ TOUCH_IRQ_BUFFER_BYPASS ~~~ TOUCH_IRQ_ALT
  TOUCH_IRQ_ALT ~~~ AUDIO_SAFE_GATE ~~~ RECEIVER ~~~ MONOSUM
  MONOSUM ~~~ AUDIO_RX_MUX ~~~ CAPNET ~~~ AUDIO_CAPTURE_BUFFER ~~~ ADCNET
  ADCNET ~~~ CODEC ~~~ AUDIO_SPEAKER_SELECTOR ~~~ SPEAKER_AMP ~~~ SPEAKER
  SPEAKER ~~~ MIC ~~~ TXATT ~~~ AUDIO_TX_SELECTOR ~~~ DISPLAY_CONNECTOR ~~~ DISPLAY ~~~ DISPLAY_LOGIC_BULK_CAP ~~~ DISPLAY_LOGIC_HF_CAP
  DISPLAY_LOGIC_HF_CAP ~~~ DISPLAY_RESET_PULLDOWN ~~~ TOUCH_RESET_PULLDOWN ~~~ BACKLIGHT_EFUSE ~~~ BACKLIGHT_EFUSE_ILIM ~~~ BACKLIGHT_EFUSE_INPUT_CAP ~~~ BACKLIGHT_EFUSE_OUTPUT_BULK ~~~ BACKLIGHT_EFUSE_OUTPUT_HF
  BACKLIGHT_EFUSE_OUTPUT_HF ~~~ BACKLIGHT_FAULT_PULLUP ~~~ BACKLIGHT_SERIES_RESISTOR ~~~ BACKLIGHT_MOSFET ~~~ BACKLIGHT_GATE_SERIES ~~~ BACKLIGHT_GATE_PULLDOWN ~~~ SD ~~~ SD_HOST_BUFFER ~~~ SD_MISO_BUFFER ~~~ SD_ESD_A ~~~ SD_ESD_B
  SD_ESD_B ~~~ SD_POWER_INPUT_CAP ~~~ SD_POWER_BULK_CAP ~~~ SD_POWER_HF_CAP ~~~ SD_HOST_BUFFER_BYPASS ~~~ SD_MISO_BUFFER_BYPASS ~~~ SD_ON_PULLDOWN ~~~ SD_HOST_SCK_PULLDOWN ~~~ SD_HOST_D0_PULLUP ~~~ SD_HOST_D1_PULLUP
  SD_HOST_D1_PULLUP ~~~ SD_HOST_CS_PULLUP ~~~ LCD_HOST_CS_PULLUP ~~~ SD_CARD_CMD_PULLUP ~~~ SD_CARD_DAT0_PULLUP ~~~ SD_CARD_DAT1_PULLUP ~~~ SD_CARD_DAT2_PULLUP ~~~ SD_CARD_DAT3_PULLUP
  SD_CARD_DAT3_PULLUP ~~~ SD_SCK_SERIES ~~~ SD_CMD_SERIES ~~~ SD_CS_SERIES ~~~ SD_MISO_SERIES ~~~ SD_DETECT_SERIES ~~~ SD_DETECT_PULLUP ~~~ SD_DETECT_CAP ~~~ UNIT
  UNIT ~~~ C5 ~~~ IRDEMOD ~~~ IRCARRIER ~~~ IRTX ~~~ RP
  RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ VOICE
  VOICE ~~~ U214_I2C_ISO ~~~ U214 ~~~ PTTSW ~~~ STOPSW ~~~ REARMSW
  REARMSW ~~~ SAFE_SUPERVISOR ~~~ SAFE_POR_PULLUP ~~~ SAFE_CONDITIONER ~~~ SAFE_POR_OR ~~~ SAFE_LATCH
  SAFE_LATCH ~~~ SAFE_RESET_BUFFER ~~~ SAFE_GATE_A ~~~ SAFE_GATE_B ~~~ SAFE_PTT_OR ~~~ STOP_LED
  STOP_LED ~~~ DET_S3 ~~~ DET_C5 ~~~ DET_NRF0 ~~~ DET_NRF1 ~~~ DET_NRF2
  DET_NRF2 ~~~ DET_CC ~~~ DET_VOICE ~~~ DET_IR ~~~ EVIDENCE_CMP_A ~~~ EVIDENCE_CMP_B
  EVIDENCE_CMP_B ~~~ EVIDENCE_MASK ~~~ EVIDENCE_OR_0 ~~~ EVIDENCE_OR_1 ~~~ EVIDENCE_OR_2 ~~~ EVIDENCE_OR_3 ~~~ ANY_TX_LED
  PRODUCT_USB_CONNECTOR -->|"VBUS sink only"| PD_CONTROLLER
  PRODUCT_USB_CONNECTOR -->|"VBUS shunt"| PD_VBUS_TVS
  PRODUCT_USB_CONNECTOR <-->|"CC1/CC2 + D+/D-"| PRODUCT_USB_PROTECTOR
  PRODUCT_USB_PROTECTOR <-->|"protected D+"| PRODUCT_USB_DP_SERIES <-->|"Full-Speed GPIO20"| S3
  PRODUCT_USB_PROTECTOR <-->|"protected D-"| PRODUCT_USB_DM_SERIES <-->|"Full-Speed GPIO19"| S3
  PRODUCT_USB_PROTECTOR <-->|"protected CC1/CC2"| PD_CONTROLLER
  PRODUCT_USB_PROTECTOR --> PRODUCT_USB_VBIAS_CAP
  PD_CONTROLLER -->|"LDO_3V3"| PRODUCT_USB_VPWR_CAP --> PRODUCT_USB_PROTECTOR
  PD_CONTROLLER --> PRODUCT_USB_FAULT_PULLUP --> PRODUCT_USB_PROTECTOR
  PD_CONTROLLER -->|"protected CC shunts"| PD_CC1_CAP
  PD_CONTROLLER --> PD_CC2_CAP
  PD_CONTROLLER <-->|"local I²C boot image"| PD_CONFIG_EEPROM
  PD_CONTROLLER <-->|"protected VBUS + local I²C/IRQ"| NVDC_CHARGER
  S3 <-->|"SYS I²C0 + shared wired-low IRQ"| PD_CONTROLLER
  PACK_CELL0 -->|"protected button-top contacts"| PACK_HOLDER
  PACK_CELL1 -->|"protected button-top contacts"| PACK_HOLDER
  PACK_HOLDER -->|"independent slot-0 contacts"| PACK_FUSE0 --> PACK_GAUGE
  PACK_NTC0 -->|"TH1"| PACK_GAUGE
  PACK_HOLDER -->|"independent slot-1 contacts"| PACK_FUSE1 --> PACK_GAUGE
  PACK_NTC1 -->|"TH2"| PACK_GAUGE
  PACK_NTC0 -.->|"insulated compliant mid-can contact"| PACK_CELL0
  PACK_NTC1 -.->|"insulated compliant mid-can contact"| PACK_CELL1
  CHARGER_TS_NTC -.->|"indexed thermally worst-slot contact"| PACK_HOLDER
  PACK_SHUNT -->|"CSP/CSN Kelvin evidence"| PACK_GAUGE
  PACK_GAUGE -->|"CHG/DIS gates; no prequal"| PACK_POWER_FET
  PACK_POWER_FET <-->|"protected 2S power boundary"| NVDC_CHARGER
  PACK_HOLD -->|"ALRT low by default"| PACK_GAUGE
  PACK_ADMISSION -->|"explicit release"| PACK_HOLD
  PACK_GAUGE -->|"AOLDO"| PACK_SUPPLY_OR --> PACK_ADMISSION
  PACK_SYSTEM_DIODE -->|"admitted 3V3"| PACK_ADMISSION
  PACK_GAUGE <-->|"local I²C + fault"| PACK_ADMISSION
  PACK_ADMISSION <-->|"SYS I²C0 + shared IRQ"| S3
  PACK_ADMISSION -->|"PA22 edge"| PACK_DIAG_TIMER
  PACK_ADMISSION --> PACK_DIAG_TRIGGER_PULLDOWN
  PACK_SUPPLY_OR -->|"admission VDD"| PACK_DIAG_TIMER
  PACK_DIAG_TIMER -->|"169 kΩ / 220 nF; ≤50 ms"| PACK_DIAG_TIMER_RES --> PACK_DIAG_TIMER_CAP
  PACK_DIAG_TIMER -->|"falling Q edge; ≥350-ms lockout"| PACK_DIAG_LOCKOUT_RES --> PACK_DIAG_LOCKOUT_CAP
  PACK_DIAG_TIMER --> PACK_DIAG_TIMER_BYPASS
  PACK_DIAG_TIMER -->|"bounded gate pulse"| PACK_DIAG_SWITCH
  PACK_DIAG_TIMER --> PACK_DIAG_GATE_PULLDOWN
  PACK_DIAG_RES0 -->|"fused full-stack load; 10 Ω total"| PACK_DIAG_SWITCH
  PACK_DIAG_RES1 --> PACK_DIAG_SWITCH
  PACK_FUSE0 --> PACK_MID_ADC_TOP0 --> PACK_MID_ADC_TOP1 -->|"PA25/A2"| PACK_ADMISSION
  PACK_ADMISSION --> PACK_MID_ADC_BOTTOM
  PACK_ADMISSION --> PACK_MID_ADC_FILTER
  PACK_FUSE1 --> PACK_STACK_ADC_TOP0 --> PACK_STACK_ADC_TOP1 --> PACK_STACK_ADC_TOP2 --> PACK_STACK_ADC_TOP3 --> PACK_STACK_ADC_TOP4 -->|"PA26/A1"| PACK_ADMISSION
  PACK_ADMISSION --> PACK_STACK_ADC_BOTTOM
  PACK_ADMISSION --> PACK_STACK_ADC_FILTER
  NVDC_CHARGER -->|"SYS"| AON_BUCK --> AON_INDUCTOR -->|"AON_RAW_3V3"| AON_EFUSE -->|"AON_SAFE_3V3"| SAFE_SUPERVISOR
  AON_BUCK -->|"MODE/S-CONF"| AON_MODE_RES
  NVDC_CHARGER -->|"SYS local bypass"| AON_INPUT_CAP
  AON_INDUCTOR -->|"raw local bypass"| AON_OUTPUT_CAP
  AON_INDUCTOR --> AON_EFUSE_INPUT_CAP
  AON_EFUSE -->|"ILIM"| AON_EFUSE_RILIM
  AON_INDUCTOR -->|"OVLO divider"| AON_EFUSE_OVLO_TOP --> AON_EFUSE_OVLO_BOTTOM
  AON_EFUSE --> AON_EFUSE_OUTPUT_CAP
  AON_EFUSE -->|"PG pull-up source"| AON_PG_PULLUP --> AON_BUCK
  AON_PG_PULLUP -->|"AON_PG_N to MR_N"| SAFE_SUPERVISOR
  AON_EFUSE -->|"POR pull-up"| SAFE_POR_PULLUP --> SAFE_SUPERVISOR
  SAFE_SUPERVISOR -->|"delayed POR_N enables main"| MAIN_BUCK
  NVDC_CHARGER -->|"SYS"| MAIN_BUCK --> MAIN_INDUCTOR -->|"MAIN_RAW_3V3"| MAIN_EFUSE -->|"3V3_MAIN"| S3
  NVDC_CHARGER -->|"SYS local bulk"| MAIN_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| MAIN_HF_INPUT_CAP
  MAIN_INDUCTOR -->|"feedback"| MAIN_FB_TOP --> MAIN_FB_BOTTOM
  MAIN_INDUCTOR -->|"feed-forward"| MAIN_FF_CAP
  MAIN_INDUCTOR -->|"local output bank"| MAIN_OUTPUT_CAP0
  MAIN_INDUCTOR -->|"local output bank"| MAIN_OUTPUT_CAP1
  MAIN_EFUSE -->|"ILM"| MAIN_EFUSE_RILM
  MAIN_EFUSE -->|"dVdt"| MAIN_EFUSE_DVDT_CAP
  MAIN_EFUSE -->|"ITIMER"| MAIN_EFUSE_ITIMER_CAP
  MAIN_INDUCTOR -->|"OVLO divider"| MAIN_EFUSE_OVLO_TOP --> MAIN_EFUSE_OVLO_BOTTOM
  MAIN_EFUSE -->|"PGTH divider"| MAIN_EFUSE_PG_TOP --> MAIN_EFUSE_PG_BOTTOM
  MAIN_EFUSE --> MAIN_EFUSE_OUTPUT_CAP
  MAIN_BUCK -->|"100-kOhm EN fail-low"| MAIN_EN_PULLDOWN
  MAIN_EFUSE -->|"protected PG to fault aggregate"| SLOW_IO
  MAIN_EFUSE -->|"POWER_FAULT_N pull-up source"| POWER_FAULT_PULLUP --> SLOW_IO
  MAIN_EFUSE -->|"3V3_MAIN"| C5
  MAIN_EFUSE -->|"3V3_MAIN"| RP
  MAIN_EFUSE --> NRF_POWER_SWITCH
  MAIN_EFUSE --> CC_POWER_SWITCH
  MAIN_EFUSE --> SD_POWER_SWITCH
  MAIN_EFUSE --> CODEC_POWER_SWITCH
  MAIN_EFUSE --> RECEIVER_POWER_SWITCH
  NVDC_CHARGER -->|"SYS"| VOICE_BUCK --> VOICE_INDUCTOR -->|"VVOICE_RAW_4V"| VOICE_EFUSE -->|"protected 4.0 V"| VOICE
  NVDC_CHARGER -->|"SYS local bulk"| VOICE_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| VOICE_HF_INPUT_CAP
  VOICE_INDUCTOR -->|"feedback"| VOICE_FB_TOP --> VOICE_FB_BOTTOM
  VOICE_INDUCTOR -->|"feed-forward"| VOICE_FF_CAP
  VOICE_INDUCTOR -->|"local output bank"| VOICE_OUTPUT_CAP0
  VOICE_INDUCTOR -->|"local output bank"| VOICE_OUTPUT_CAP1
  VOICE_EFUSE -->|"ILM"| VOICE_EFUSE_RILM
  VOICE_EFUSE -->|"dVdt"| VOICE_EFUSE_DVDT_CAP
  VOICE_EFUSE -->|"ITIMER"| VOICE_EFUSE_ITIMER_CAP
  VOICE_INDUCTOR -->|"OVLO divider"| VOICE_EFUSE_OVLO_TOP --> VOICE_EFUSE_OVLO_BOTTOM
  VOICE_EFUSE -->|"PGTH divider"| VOICE_EFUSE_PG_TOP --> VOICE_EFUSE_PG_BOTTOM
  VOICE_EFUSE --> VOICE_EFUSE_OUTPUT_CAP
  VOICE_BUCK -->|"EN fail-low"| VOICE_EN_PULLDOWN
  MAIN_EFUSE -->|"PG pull-up"| VOICE_PG_PULLUP --> VOICE_EFUSE
  SAFE_GATE_B -->|"EN"| VOICE_PG_BASE_RES --> VOICE_PG_QUALIFIER
  VOICE_EFUSE -->|"protected PG"| VOICE_PG_QUALIFIER -->|"qualified open collector"| SLOW_IO
  NVDC_CHARGER -->|"SYS"| EXT_BUCK --> EXT_INDUCTOR --> EXT_EFUSE -->|"protected fixed 5.0 V"| U214
  NVDC_CHARGER -->|"SYS local bulk"| EXT_BUCK_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| EXT_BUCK_HF_INPUT_CAP
  EXT_INDUCTOR -->|"feedback"| EXT_BUCK_FB_TOP --> EXT_BUCK_FB_BOTTOM
  EXT_INDUCTOR -->|"feed-forward"| EXT_BUCK_FF_CAP
  EXT_INDUCTOR -->|"local output bank"| EXT_BUCK_OUTPUT_CAP0
  EXT_INDUCTOR -->|"local output bank"| EXT_BUCK_OUTPUT_CAP1
  EXT_BUCK -->|"EN fail-low"| EXT_EN_PULLDOWN
  MAIN_EFUSE -->|"PG pull-up"| EXT_PG_PULLUP --> EXT_BUCK
  SAFE_GATE_B -->|"EN"| EXT_PG_BASE_RES --> EXT_PG_QUALIFIER
  EXT_BUCK -->|"PG"| EXT_PG_QUALIFIER -->|"qualified open collector"| SLOW_IO
  EXT_EFUSE -->|"ILM"| EXT_RILM
  EXT_EFUSE -->|"dVdt"| EXT_DVDT_CAP
  EXT_EFUSE -->|"ITIMER"| EXT_ITIMER_CAP
  EXT_INDUCTOR -->|"OVLO divider"| EXT_OVLO_TOP --> EXT_OVLO_BOTTOM
  EXT_INDUCTOR --> EXT_INPUT_CAP
  EXT_EFUSE --> EXT_OUTPUT_CAP
  EXT_EFUSE --> EXT_BLEEDER
  NRF_POWER_SWITCH --> NRF0
  NRF_POWER_SWITCH --> NRF1
  NRF_POWER_SWITCH --> NRF2
  CC_POWER_SWITCH --> CC
  MAIN_EFUSE --> SD_POWER_SWITCH -->|"switched 3.3 V"| SD
  MAIN_EFUSE -->|"local input bypass"| SD_POWER_INPUT_CAP
  SLOW_IO -->|"P20 session enable"| SD_POWER_SWITCH
  SD_ON_PULLDOWN -->|"reset off"| SD_POWER_SWITCH
  SD_POWER_SWITCH --> SD_POWER_BULK_CAP
  SD_POWER_SWITCH --> SD_POWER_HF_CAP
  SD_POWER_SWITCH --> SD_HOST_BUFFER_BYPASS
  SD_POWER_SWITCH --> SD_MISO_BUFFER_BYPASS
  SD_POWER_SWITCH -->|"VCC with Ioff"| SD_HOST_BUFFER
  SD_POWER_SWITCH -->|"VCC with Ioff"| SD_MISO_BUFFER
  SD_HOST_SCK_PULLDOWN -->|"reset low"| S3
  MAIN_EFUSE --> SD_HOST_D0_PULLUP --> S3
  MAIN_EFUSE --> SD_HOST_D1_PULLUP --> S3
  MAIN_EFUSE --> SD_HOST_CS_PULLUP --> S3
  MAIN_EFUSE --> LCD_HOST_CS_PULLUP --> S3
  S3 -->|"shared SCK/CMD + card CS"| SD_HOST_BUFFER
  SD_HOST_BUFFER -->|"SCK"| SD_SCK_SERIES --> SD
  SD_HOST_BUFFER -->|"CMD"| SD_CMD_SERIES --> SD
  SD_HOST_BUFFER -->|"CS"| SD_CS_SERIES --> SD
  SD -->|"DAT0 only while CS low"| SD_MISO_BUFFER --> SD_MISO_SERIES --> S3
  S3 -->|"SD_CS_N output enable"| SD_MISO_BUFFER
  SD_POWER_SWITCH --> SD_CARD_CMD_PULLUP --> SD
  SD_POWER_SWITCH --> SD_CARD_DAT0_PULLUP --> SD
  SD_POWER_SWITCH --> SD_CARD_DAT1_PULLUP --> SD
  SD_POWER_SWITCH --> SD_CARD_DAT2_PULLUP --> SD
  SD_POWER_SWITCH --> SD_CARD_DAT3_PULLUP --> SD
  SD_ESD_A -.->|"CLK/CMD/DAT0/DAT3 shunt clamps"| SD
  SD_ESD_B -.->|"DAT1/DAT2/VDD/detect shunt clamps"| SD
  SD -->|"normally-open detect"| SD_DETECT_SERIES --> SLOW_IO
  MAIN_EFUSE --> SD_DETECT_PULLUP --> SLOW_IO
  SLOW_IO --> SD_DETECT_CAP
  CODEC_POWER_SWITCH --> CODEC
  RECEIVER_POWER_SWITCH --> RECEIVER
  S3 <-->|"1-bit SDIO: S3 GPIO10,GPIO11,GPIO12,GPIO13 ↔ C5 GPIO7,GPIO8,GPIO9,GPIO10"| C5
  S3 <-->|"SPI3+alert: S3 GPIO3,GPIO9,GPIO14,GPIO21,GPIO48 ↔ RP GPIO19,GPIO24,GPIO25,GPIO26,GPIO27"| RP
  S3 <-->|"I²C0+INT: GPIO1,GPIO2"| SLOW_IO
  S3 -->|"QSPI/touch/PWM: GPIO4,GPIO35,GPIO36,GPIO38,GPIO40,GPIO41,GPIO42"| DISPLAY_CONNECTOR
  DISPLAY_CONNECTOR <-->|"40-contact FPC; physical mate HIL open"| DISPLAY
  DISPLAY_CONNECTOR -->|"TP_INT raw"| TOUCH_IRQ_BUFFER -->|"open-drain SYS_INT_N"| S3
  TOUCH_IRQ_ALT -.->|"same SC70-5 footprint; populate only after polarity HIL"| TOUCH_IRQ_BUFFER
  SLOW_IO -->|"P06/P07 reset release"| DISPLAY_CONNECTOR
  S3 <-->|"SYS I²C0 + shared wired-low IRQ"| UI_MATRIX_IO
  UI_MATRIX_IO_BYPASS --> UI_MATRIX_IO
  UI_MATRIX_ROW0_PULLDOWN -->|"reset/idle low"| UI_MATRIX_IO
  UI_MATRIX_ROW1_PULLDOWN -->|"reset/idle low"| UI_MATRIX_IO
  UI_MATRIX_ROW2_PULLDOWN -->|"reset/idle low"| UI_MATRIX_IO
  UI_MATRIX_ROW3_PULLDOWN -->|"reset/idle low"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_UP --> UI_UP -->|"P4 column 0"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_DOWN --> UI_DOWN -->|"P5 column 1"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_LEFT --> UI_LEFT -->|"P6 column 2"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_RIGHT --> UI_RIGHT -->|"P4 column 0"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_OK --> UI_OK -->|"P5 column 1"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_BACK --> UI_BACK -->|"P6 column 2"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_OPT --> UI_OPT -->|"P4 column 0"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_F1 --> UI_F1 -->|"P5 column 1"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_F2 --> UI_F2 -->|"P6 column 2"| UI_MATRIX_IO
  UI_MATRIX_IO --> UI_MATRIX_DIODE_ENCODER -->|"push"| ENCODER -->|"P4 column 0"| UI_MATRIX_IO
  UI_MATRIX_COL0_PULLUP --> UI_MATRIX_IO
  UI_MATRIX_COL1_PULLUP --> UI_MATRIX_IO
  UI_MATRIX_COL2_PULLUP --> UI_MATRIX_IO
  ENCODER_A_PULLUP --> ENCODER
  ENCODER_B_PULLUP --> ENCODER
  ENCODER -->|"GPIO39/GPIO47 PCNT0 quadrature"| S3
  DISPLAY_RESET_PULLDOWN -->|"RESX default low"| DISPLAY_CONNECTOR
  TOUCH_RESET_PULLDOWN -->|"TP_RESXP default low"| DISPLAY_CONNECTOR
  MAIN_EFUSE -->|"protected 3.3 V logic"| DISPLAY_LOGIC_BULK_CAP --> DISPLAY_CONNECTOR
  MAIN_EFUSE --> DISPLAY_LOGIC_HF_CAP --> DISPLAY_CONNECTOR
  MAIN_EFUSE -->|"LEDA branch"| BACKLIGHT_EFUSE --> DISPLAY_CONNECTOR
  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_ILIM
  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_INPUT_CAP
  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_OUTPUT_BULK
  BACKLIGHT_EFUSE --> BACKLIGHT_EFUSE_OUTPUT_HF
  BACKLIGHT_FAULT_PULLUP --> BACKLIGHT_EFUSE
  DISPLAY_CONNECTOR -->|"3 x LEDK"| BACKLIGHT_SERIES_RESISTOR --> BACKLIGHT_MOSFET
  S3 -->|"GPIO40 PWM"| BACKLIGHT_GATE_SERIES --> BACKLIGHT_MOSFET
  BACKLIGHT_GATE_PULLDOWN -->|"reset off"| BACKLIGHT_MOSFET
  S3 -.->|"logical scheduler contract; no electrical bypass: GPIO4,GPIO5,GPIO35,GPIO36"| SD
  S3 <-->|"I²S0/I²C: GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18"| CODEC
  S3 <-->|"I²C0"| RECEIVER
  S3 <-->|"profile port: GPIO7,GPIO8"| UNIT
  C5 <-->|"RMT RX0/power: GPIO0,GPIO1,GPIO4,GPIO6,GPIO24"| IRDEMOD
  C5 <-->|"RMT RX1/power"| IRCARRIER
  RP <-->|"PIO0 SM0 + direct control: GPIO0,GPIO1,GPIO2,GPIO30,GPIO31,GPIO32"| NRF0
  RP <-->|"PIO0 SM1 + direct control: GPIO3,GPIO4,GPIO5,GPIO33,GPIO34,GPIO35"| NRF1
  RP <-->|"PIO0 SM2 + direct control: GPIO6,GPIO7,GPIO8,GPIO36,GPIO37,GPIO38"| NRF2
  RP <-->|"PIO0 SM3 + GDO/power: GPIO9,GPIO10,GPIO11,GPIO23,GPIO39,GPIO42,GPIO43"| CC
  RP <-->|"UART0/PTT request: GPIO16,GPIO17,GPIO18,GPIO20,GPIO21"| VOICE
  PTTSW -->|"direct GPIO21; never in UI matrix"| RP
  RP <-->|"PIO1/UART1: GPIO12,GPIO13,GPIO14,GPIO28,GPIO29,GPIO40,GPIO41,GPIO44,GPIO45,GPIO46,GPIO47"| U214
  RP <-->|"I²C0"| U214_I2C_ISO
  U214_I2C_ISO <-->|"isolated external I²C"| U214
  RECEIVER --> MONOSUM --> AUDIO_RX_MUX
  VOICE -->|"AFOUT"| AUDIO_RX_MUX
  SLOW_IO -->|"P27 source request"| AUDIO_RX_MUX
  AUDIO_RX_MUX -->|"analog bypass"| AUDIO_SPEAKER_SELECTOR
  AUDIO_RX_MUX --> CAPNET --> AUDIO_CAPTURE_BUFFER --> ADCNET --> CODEC
  CODEC -->|"OUTP/OUTN"| AUDIO_SPEAKER_SELECTOR
  AUDIO_SPEAKER_SELECTOR --> SPEAKER_AMP --> SPEAKER
  CODEC --> TXATT --> AUDIO_TX_SELECTOR
  MIC --> AUDIO_TX_SELECTOR -->|"MIC_IN"| VOICE
  SLOW_IO -->|"P11/P12 requests"| AUDIO_SAFE_GATE
  S3 -->|"GPIO6 AUDIO_ARM"| AUDIO_SAFE_GATE
  AUDIO_SAFE_GATE --> AUDIO_SPEAKER_SELECTOR
  AUDIO_SAFE_GATE --> AUDIO_TX_SELECTOR
  STOPSW --> SAFE_CONDITIONER --> SAFE_LATCH
  REARMSW --> SAFE_CONDITIONER
  SAFE_SUPERVISOR --> SAFE_POR_OR --> SAFE_LATCH
  STOPSW --> SAFE_POR_OR
  SAFE_LATCH -->|"RUN_PERMIT"| SAFE_RESET_BUFFER
  SAFE_RESET_BUFFER -->|"CHIP_PU"| S3
  SAFE_RESET_BUFFER -->|"CHIP_PU"| C5
  SAFE_RESET_BUFFER -->|"RUN"| RP
  SAFE_LATCH --> SAFE_GATE_A
  SAFE_LATCH --> SAFE_GATE_B
  SAFE_LATCH --> SAFE_PTT_OR
  SAFE_LATCH --> STOP_LED
  RP -->|"3×CE + nRF rail requests"| SAFE_GATE_A
  RP -->|"CC rail request"| SAFE_GATE_B
  C5 -->|"IR carrier request"| SAFE_GATE_B
  SLOW_IO -->|"voice/accessory rail requests"| SAFE_GATE_B
  RP -->|"PTT request"| SAFE_PTT_OR --> VOICE
  SAFE_GATE_A --> NRF0
  SAFE_GATE_A --> NRF1
  SAFE_GATE_A --> NRF2
  SAFE_GATE_A --> NRF_POWER_SWITCH
  SAFE_GATE_B --> CC_POWER_SWITCH
  SAFE_GATE_B --> VOICE_BUCK
  SAFE_GATE_B --> IRTX
  SAFE_GATE_B --> EXT_BUCK
  SAFE_GATE_B --> EXT_EFUSE
  S3 --> DET_S3 --> EVIDENCE_CMP_A
  C5 --> DET_C5 --> EVIDENCE_CMP_A
  NRF0 --> DET_NRF0 --> EVIDENCE_CMP_A
  NRF1 --> DET_NRF1 --> EVIDENCE_CMP_A
  NRF2 --> DET_NRF2 --> EVIDENCE_CMP_B
  CC --> DET_CC --> EVIDENCE_CMP_B
  VOICE --> DET_VOICE --> EVIDENCE_CMP_B
  IRTX --> DET_IR --> EVIDENCE_CMP_B
  EVIDENCE_CMP_A --> EVIDENCE_MASK
  EVIDENCE_CMP_B --> EVIDENCE_MASK
  EVIDENCE_CMP_A --> EVIDENCE_OR_0
  EVIDENCE_CMP_A --> EVIDENCE_OR_1
  EVIDENCE_CMP_B --> EVIDENCE_OR_2
  EVIDENCE_CMP_B --> EVIDENCE_OR_3
  EVIDENCE_OR_0 --> ANY_TX_LED
  EVIDENCE_OR_1 --> ANY_TX_LED
  EVIDENCE_OR_2 --> ANY_TX_LED
  EVIDENCE_OR_3 --> ANY_TX_LED
  EVIDENCE_MASK <-->|"local I²C0 source mask"| RP
  ANY_TX_LED -->|"RP.GPIO22 RP_ANY_TX_N"| RP
```

## Сводный pin budget

| Domain | Exact exposed boundary | Used | Reserved | Free | Total |
|---|---|---:|---:|---:|---:|
| `s3` | `ESP32-S3-WROOM-1U-N16R2` | 33 | 3 | 0 | 36 |
| `c5` | `ESP32-C5-WROOM-1U-N8R8` | 14 | 6 | 1 | 21 |
| `rp` | `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)` | 48 | 0 | 0 | 48 |
| `slow_io` | `TCA6424ARGJR` | 18 | 0 | 6 | 24 |

`RP=0 free` является текущим честным результатом после direct quiet-state
controls `NRF_GROUP_PWR_EN` и `CC_PWR_EN`, а не ошибкой округления. Новый
direct RP endpoint требует явного remap/review; service pins SWD/USB/RUN/
BOOTSEL не входят в GPIO budget и остаются выведенными независимо.

## Ещё абстрактные electrical endpoints

Следующие функции имеют pin reservation, но не exact production MPN/circuit:

- `3V3_MAIN`
- `AON_RAW_3V3`
- `AON_SAFE_3V3`
- `AON_SAFE_3V3-via-2k2`
- `C5-qualified-RF-tap`
- `CC-qualified-RF-tap`
- `MAIN_RAW_3V3`
- `NC-stop-loop-10k-pullup-10nF`
- `NO-rearm-loop-47k-pullup-100nF`
- `NRF0-qualified-RF-tap`
- `NRF1-qualified-RF-tap`
- `NRF2-qualified-RF-tap`
- `RX-AM-LW-loop-pod`
- `RX-FM-SW-SMA-front-end`
- `S3-GPIO4-shared-D1`
- `S3-qualified-RF-tap`
- `SYS_INT_N_WIRED_LOW`
- `TP_EVIDENCE_MASK_INT_N`
- `TP_EXT_5V_ILM`
- `TP_LCD_BACKLIGHT_FAULT_N`
- `TP_USB_PROTECTOR_FAULT_N`
- `UI_MATRIX_COL0_WITH_SWITCHES_AND_DIODES`
- `UI_MATRIX_COL1_WITH_SWITCHES_AND_DIODES`
- `UI_MATRIX_COL2_WITH_SWITCHES_AND_DIODES`
- `UI_MATRIX_ROW0_UP_DOWN_LEFT`
- `UI_MATRIX_ROW1_RIGHT_OK_BACK`
- `UI_MATRIX_ROW2_OPT_F1_F2`
- `UI_MATRIX_ROW3_ENCODER_PUSH`
- `UI_SWITCH_BACK_COL_CONTACT`
- `UI_SWITCH_BACK_ROW_CONTACT`
- `UI_SWITCH_DOWN_COL_CONTACT`
- `UI_SWITCH_DOWN_ROW_CONTACT`
- `UI_SWITCH_F1_COL_CONTACT`
- `UI_SWITCH_F1_ROW_CONTACT`
- `UI_SWITCH_F2_COL_CONTACT`
- `UI_SWITCH_F2_ROW_CONTACT`
- `UI_SWITCH_LEFT_COL_CONTACT`
- `UI_SWITCH_LEFT_ROW_CONTACT`
- `UI_SWITCH_OK_COL_CONTACT`
- `UI_SWITCH_OK_ROW_CONTACT`
- `UI_SWITCH_OPT_COL_CONTACT`
- `UI_SWITCH_OPT_ROW_CONTACT`
- `UI_SWITCH_RIGHT_COL_CONTACT`
- `UI_SWITCH_RIGHT_ROW_CONTACT`
- `UI_SWITCH_UP_COL_CONTACT`
- `UI_SWITCH_UP_ROW_CONTACT`
- `VOICE-qualified-RF-tap`
- `VVOICE_RAW_4V`
- `accessory-present`
- `admitted-system-3v3`
- `always-available-quiet-audio-rail`
- `audio-ground`
- `cc-filtered-3v3`
- `chassis-ground-at-product-usb-entry`
- `codec-adcvref-decoupling`
- `codec-address-high-3v3`
- `codec-audio-ground`
- `codec-dac-to-sa518-35-45db-attenuator`
- `codec-dacvref-decoupling`
- `codec-digital-ground`
- `codec-vmid-decoupling`
- `electret-microphone-bias-and-ac-coupling`
- `exact carrier-learning IR receiver`
- `exact robust-demod IR receiver`
- `exact-value-hold-gate-pullup`
- `fail-safe-IR-LED-driver`
- `high-z-ac-coupled-capture-network`
- `i2c-mode-strap`
- `isolated-pack-fixture-3v3`
- `main-raw-converter-pg-test`
- `matched-bypass-ac-reference`
- `no-connect`
- `no-connect-open-vset`
- `off-safe IR frontend load switch`
- `pack service fixture`
- `pack-admission reset-safe open-drain IRQ circuit`
- `pd-eeprom-factory-scl-pad`
- `pd-eeprom-factory-sda-pad`
- `pd-eeprom-factory-wp-pad`
- `physical PTT switch`
- `power-current-thermal-fault`
- `power-ground`
- `power-ground-dedicated-via`
- `power-ground-multivia`
- `protected configurable M5 Unit contact`
- `protected-2s-midpoint`
- `protected-accessory-power-good`
- `qualified-2s-positive`
- `qualified-32k-clock`
- `qualified-codec-3v3-analog`
- `qualified-codec-3v3-digital`
- `qualified-es8311-mic-range-differential-input-network`
- `qualified-evidence-threshold-0`
- `qualified-evidence-threshold-1`
- `qualified-evidence-threshold-2`
- `qualified-evidence-threshold-3`
- `qualified-evidence-threshold-4`
- `qualified-evidence-threshold-5`
- `qualified-evidence-threshold-6`
- `qualified-evidence-threshold-7`
- `qualified-speaker-amp-supply`
- `qualified-speaker-enable-default-on`
- `receiver-power-reset-isolation`
- `reserved-local-control-expansion-pad`
- `rx-audio-bypass-and-capture-node`
- `safety-ground`
- `safety-ground-via-10k`
- `service USB connector`
- `service fixture`
- `shielded-ir-evidence-front-end`
- `si4732-10k-left-mono-sum`
- `si4732-10k-right-mono-sum`
- `si4732-passive-mono-sum-output`
- `speaker-negative`
- `speaker-positive`
- `stop-led-series-2k2`
- `voice-power-reset-domain`
- `voice-raw-converter-pg-test`
- `voice-update-fixture`

Эти строки блокируют final schematic/BOM, но не нарушают проверенную
арифметику MCU pins. Их нельзя молча удалить либо объявить реализованными.

## Exact pin/net tables

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `slow_io.SDA`, `ui_matrix_io.SDA`, `receiver.SDIO`, `display_connector.PIN_2`, `codec.CDATA`, `pd_controller.I2Ct_SDA`, `pack_admission.PA0` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `slow_io.SCL`, `ui_matrix_io.SCL`, `receiver.SCLK`, `display_connector.PIN_1`, `codec.CCLK`, `pd_controller.I2Ct_SCL`, `pack_admission.PA11` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO19` | RP is held reset/high-Z through S3 strap sampling; an external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `DISPLAY_SD_SPI_D1` | `io` | `SPI2` | `sd_miso_series.END_2`, `sd_host_d1_pullup.END_1`, `display_connector.PIN_10` | — |
| `GPIO5` | 5 | `SD_SPI_CS_N` | `o` | `SPI2` | `sd_host_buffer.3A`, `sd_miso_buffer.OE_N`, `sd_host_cs_pullup.END_1` | — |
| `GPIO6` | 6 | `AUDIO_ARM` | `o` | `GPIO` | `audio_safe_gate.1B`, `audio_safe_gate.2B` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `I2C1_OR_UART1_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `I2C1_OR_UART1_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO9` | 17 | `S3_RP_IPC_CS_N` | `o` | `SPI3` | `rp.GPIO25` | — |
| `GPIO10` | 18 | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_1BIT` | `c5.GPIO9` | — |
| `GPIO11` | 19 | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO10` | — |
| `GPIO12` | 20 | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO8` | — |
| `GPIO13` | 21 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO7` | — |
| `GPIO14` | 22 | `S3_RP_IPC_MISO` | `i` | `SPI3` | `rp.GPIO27` | — |
| `GPIO15` | 8 | `I2S_BCLK` | `o` | `I2S0` | `codec.SCLK` | — |
| `GPIO16` | 9 | `I2S_WS` | `o` | `I2S0` | `codec.LRCK` | — |
| `GPIO17` | 10 | `I2S_DOUT` | `o` | `I2S0` | `codec.DSDIN` | — |
| `GPIO18` | 11 | `I2S_DIN` | `i` | `I2S0` | `codec.ASDOUT` | — |
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `product_usb_dm_series.END_2` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `product_usb_dp_series.END_2` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | `sd_host_buffer.1A`, `sd_host_sck_pulldown.END_1`, `display_connector.PIN_11` | — |
| `GPIO36` | 29 | `DISPLAY_SD_SPI_D0` | `o` | `SPI2` | `sd_host_buffer.2A`, `sd_host_d0_pullup.END_1`, `display_connector.PIN_13` | — |
| `GPIO37` | 30 | `SYS_INT_N` | `i` | `GPIO_IRQ` | `slow_io.INT`, `ui_matrix_io.INT_N`, `pd_controller.I2Ct_IRQ`, `touch_irq_buffer.Y`, `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `display_connector.PIN_9`, `lcd_host_cs_pullup.END_1` | — |
| `GPIO39` | 32 | `ENCODER_A` | `i` | `PCNT0` | `encoder.A`, `encoder_a_pullup.END_1` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `backlight_gate_series.END_1` | — |
| `GPIO41` | 34 | `LCD_QSPI_D2` | `o` | `SPI2` | `display_connector.PIN_17` | — |
| `GPIO42` | 35 | `LCD_QSPI_D3` | `o` | `SPI2` | `display_connector.PIN_18` | — |
| `GPIO43` | 37 | `S3_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO44` | 36 | `S3_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO47` | 24 | `ENCODER_B` | `i` | `PCNT0` | `encoder.B`, `encoder_b_pullup.END_1` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **33 used + 3 reserved + 0 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: none.

### `c5` — `ESP32-C5-WROOM-1U-N8R8`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 6 | `IR_RX_DEMOD` | `i` | `RMT_RX0` | `abstract:exact robust-demod IR receiver` | — |
| `GPIO1` | 7 | `IR_RX_CARRIER` | `i` | `RMT_RX1` | `abstract:exact carrier-learning IR receiver` | — |
| `GPIO4` | 17 | `IR_FRONTEND_PWR_EN` | `o` | `GPIO` | `abstract:off-safe IR frontend load switch` | — |
| `GPIO6` | 8 | `IR_TX_CARRIER` | `o` | `RMT_TX0` | `safe_gate_b.3A` | — |
| `GPIO7` | 9 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDIO_SLAVE` | `s3.GPIO13` | external pull-up and documented SDIO edge profile are verified before runtime ownership |
| `GPIO8` | 10 | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE` | `s3.GPIO12` | — |
| `GPIO9` | 11 | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE` | `s3.GPIO10` | — |
| `GPIO10` | 12 | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE` | `s3.GPIO11` | — |
| `GPIO11` | 25 | `C5_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO12` | 24 | `C5_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO13` | 13 | `C5_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO14` | 14 | `C5_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO23` | 21 | `C5_RF_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | `evidence_cmp_a.OUT2` | — |
| `GPIO24` | 23 | `IR_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | `evidence_cmp_b.OUT4` | — |

Budget: **14 used + 6 reserved + 1 free = 21 exposed GPIO**.
Reserved: `GPIO2`, `GPIO3`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO28`. Free: `GPIO5`.

### `rp` — `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 77 | `NRF0_CSN_N` | `o` | `GPIO` | `nrf0.CSN` | — |
| `GPIO1` | 78 | `NRF0_CE_REQ` | `o` | `GPIO` | `safe_gate_a.1A` | — |
| `GPIO2` | 79 | `NRF0_IRQ_N` | `i` | `GPIO_IRQ` | `nrf0.IRQ` | — |
| `GPIO3` | 80 | `NRF1_CSN_N` | `o` | `GPIO` | `nrf1.CSN` | — |
| `GPIO4` | 1 | `NRF1_CE_REQ` | `o` | `GPIO` | `safe_gate_a.2A` | — |
| `GPIO5` | 2 | `NRF1_IRQ_N` | `i` | `GPIO_IRQ` | `nrf1.IRQ` | — |
| `GPIO6` | 3 | `NRF2_CSN_N` | `o` | `GPIO` | `nrf2.CSN` | — |
| `GPIO7` | 4 | `NRF2_CE_REQ` | `o` | `GPIO` | `safe_gate_a.3A` | — |
| `GPIO8` | 6 | `NRF2_IRQ_N` | `i` | `GPIO_IRQ` | `nrf2.IRQ` | — |
| `GPIO9` | 7 | `CC_CSN_N` | `o` | `GPIO` | `cc.CSN` | — |
| `GPIO10` | 8 | `CC_GDO0` | `i` | `GPIO_IRQ` | `cc.GDO0` | — |
| `GPIO11` | 9 | `CC_GDO2` | `i` | `GPIO_IRQ` | `cc.GDO2` | — |
| `GPIO12` | 11 | `U214_BUSY` | `i` | `GPIO_IRQ` | `u214.LORA_BUSY` | — |
| `GPIO13` | 12 | `U214_IRQ` | `i` | `GPIO_IRQ` | `u214.LORA_IRQ` | — |
| `GPIO14` | 13 | `U214_RST_N` | `o` | `GPIO` | `u214.LORA_RST` | — |
| `GPIO15` | 14 | `NRF_GROUP_PWR_EN` | `o` | `GPIO` | `safe_gate_a.4A` | — |
| `GPIO16` | 16 | `VOICE_UART_TX` | `o` | `UART0` | `voice.UART_RX` | — |
| `GPIO17` | 17 | `VOICE_UART_RX` | `i` | `UART0` | `voice.UART_TX` | — |
| `GPIO18` | 18 | `VOICE_PTT_REQ_N` | `o` | `GPIO` | `safe_ptt_or.1A` | — |
| `GPIO19` | 19 | `RP_ALERT_N` | `od` | `GPIO_IRQ` | `s3.GPIO3` | — |
| `GPIO20` | 20 | `VOICE_ACTIVITY` | `i` | `GPIO_IRQ` | `voice.AUDIO_ON` | — |
| `GPIO21` | 21 | `PTT_BUTTON_N` | `i` | `GPIO_IRQ` | `abstract:physical PTT switch` | — |
| `GPIO22` | 22 | `RP_ANY_TX_N` | `i` | `GPIO_IRQ` | `evidence_or_0.A_COMMON`, `evidence_or_1.A_COMMON`, `evidence_or_2.A_COMMON`, `evidence_or_3.A_COMMON`, `any_tx_led.K` | — |
| `GPIO23` | 23 | `CC_PWR_EN` | `o` | `GPIO` | `safe_gate_b.1A` | — |
| `GPIO24` | 25 | `S3_RP_IPC_MOSI` | `i` | `SPI1_IPC` | `s3.GPIO21` | — |
| `GPIO25` | 26 | `S3_RP_IPC_CS_N` | `i` | `SPI1_IPC` | `s3.GPIO9` | — |
| `GPIO26` | 27 | `S3_RP_IPC_SCK` | `i` | `SPI1_IPC` | `s3.GPIO48` | — |
| `GPIO27` | 28 | `S3_RP_IPC_MISO` | `o` | `SPI1_IPC` | `s3.GPIO14` | — |
| `GPIO28` | 36 | `U214_I2C_SDA_IN` | `io` | `I2C0_EXT` | `u214_i2c_iso.SDAIN`, `evidence_mask.SDA` | — |
| `GPIO29` | 37 | `U214_I2C_SCL_IN` | `o` | `I2C0_EXT` | `u214_i2c_iso.SCLIN`, `evidence_mask.SCL` | — |
| `GPIO30` | 38 | `NRF0_MISO` | `i` | `PIO0_SM0_RF_SPI` | `nrf0.MISO` | — |
| `GPIO31` | 39 | `NRF0_SCK` | `o` | `PIO0_SM0_RF_SPI` | `nrf0.SCK` | — |
| `GPIO32` | 40 | `NRF0_MOSI` | `o` | `PIO0_SM0_RF_SPI` | `nrf0.MOSI` | — |
| `GPIO33` | 42 | `NRF1_MISO` | `i` | `PIO0_SM1_RF_SPI` | `nrf1.MISO` | — |
| `GPIO34` | 43 | `NRF1_SCK` | `o` | `PIO0_SM1_RF_SPI` | `nrf1.SCK` | — |
| `GPIO35` | 44 | `NRF1_MOSI` | `o` | `PIO0_SM1_RF_SPI` | `nrf1.MOSI` | — |
| `GPIO36` | 45 | `NRF2_MISO` | `i` | `PIO0_SM2_RF_SPI` | `nrf2.MISO` | — |
| `GPIO37` | 46 | `NRF2_SCK` | `o` | `PIO0_SM2_RF_SPI` | `nrf2.SCK` | — |
| `GPIO38` | 47 | `NRF2_MOSI` | `o` | `PIO0_SM2_RF_SPI` | `nrf2.MOSI` | — |
| `GPIO39` | 48 | `CC_MISO` | `i` | `PIO0_SM3_RF_SPI` | `cc.SO_GDO1` | — |
| `GPIO40` | 49 | `U214_GPS_TX` | `o` | `UART1` | `u214.GPS_RX` | — |
| `GPIO41` | 52 | `U214_GPS_RX` | `i` | `UART1` | `u214.GPS_TX` | — |
| `GPIO42` | 53 | `CC_SCK` | `o` | `PIO0_SM3_RF_SPI` | `cc.SCLK` | — |
| `GPIO43` | 54 | `CC_MOSI` | `o` | `PIO0_SM3_RF_SPI` | `cc.SI` | — |
| `GPIO44` | 55 | `U214_MISO` | `i` | `PIO1_SM0_EXT_SPI` | `u214.MISO` | — |
| `GPIO45` | 56 | `U214_SCK` | `o` | `PIO1_SM0_EXT_SPI` | `u214.SCK` | — |
| `GPIO46` | 57 | `U214_MOSI` | `o` | `PIO1_SM0_EXT_SPI` | `u214.MOSI` | — |
| `GPIO47` | 58 | `U214_NSS_N` | `o` | `GPIO` | `u214.NSS` | — |

Budget: **48 used + 0 reserved + 0 free = 48 exposed GPIO**.
Reserved: none. Free: none.

### `pd_controller` — `Texas Instruments TPS25751DREFR`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 5 | `PD_EEPROM_WP` | `od` | `GPIO` | `pd_config_eeprom.WP` | — |
| `GPIO1` | 6 | `CHARGE_EN_N` | `od` | `GPIO` | `nvdc_charger.CE` | — |
| `I2Ct_IRQ` | 10 (I2C target IRQ / GPIO10) | `SYS_INT_N` | `od` | `I2C_TARGET` | `s3.GPIO37` | — |
| `I2Ct_SCL` | 9 (fixed I2C target clock) | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | `s3.GPIO2` | — |
| `I2Ct_SDA` | 8 (fixed I2C target data) | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | `s3.GPIO1` | — |

Budget: **5 used + 5 reserved + 0 free = 10 exposed GPIO**.
Reserved: `GPIO2`, `GPIO3`, `GPIO6`, `GPIO7`, `GPIO11`. Free: none.

### `pack_admission` — `Texas Instruments MSPM0C1104SDGS20R`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `PA0` | 4 | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | `s3.GPIO1` | — |
| `PA2` | 8 | `PACK_GAUGE_I2C_SCL` | `io` | `BITBANG_I2C` | `pack_gauge.SCL_OD` | — |
| `PA4` | 9 | `PACK_GAUGE_I2C_SDA` | `io` | `BITBANG_I2C` | `pack_gauge.SDA_DQ` | — |
| `PA6` | 10 | `PACK_FET_HOLD_RELEASE` | `o` | `GPIO` | `pack_hold.G2` | — |
| `PA11` | 11 | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | `s3.GPIO2` | — |
| `PA17` | 13 | `PACK_SERVICE_UART_TX` | `o` | `UART0` | `abstract:pack service fixture` | — |
| `PA23` | 18 | `PACK_SYS_INT_REQ_N` | `o` | `GPIO` | `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `PA16_A8` | 12 | `PACK_PFAIL_N` | `i` | `GPIO_IRQ` | `pack_gauge.PFAIL` | — |
| `PA18_A7` | 14 | `PACK_SERVICE_UART_RX` | `i` | `UART0` | `abstract:pack service fixture` | — |
| `PA22_A4` | 17 | `PACK_DIAG_TRIGGER` | `o` | `GPIO` | `pack_diag_timer.CH1_T`, `pack_diag_trigger_pulldown.END_1` | — |
| `PA25_A2` | 20 | `PACK_CELL0_ADC` | `i` | `ADC` | `pack_mid_adc_top1.END_2`, `pack_mid_adc_bottom.END_1`, `pack_mid_adc_filter.END_1` | — |
| `PA26_A1` | 1 | `PACK_STACK_ADC` | `i` | `ADC` | `pack_stack_adc_top4.END_2`, `pack_stack_adc_bottom.END_1`, `pack_stack_adc_filter.END_1` | — |

Budget: **12 used + 3 reserved + 3 free = 18 exposed GPIO**.
Reserved: `PA19_SWDIO`, `PA1_NRST`, `PA20_A6_SWCLK`. Free: `PA24_A3`, `PA27_A0`, `PA28_A5`.

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
| `USB_C_VBUS_RAW` | `product_usb_connector.A4_VBUS` | `product_usb_connector.A9_VBUS` | both A-side VBUS contacts join one short wide connector-side copper region |
| `USB_C_VBUS_RAW` | `product_usb_connector.A9_VBUS` | `product_usb_connector.B4_VBUS` | all four exact receptacle VBUS contacts share the raw input plane |
| `USB_C_VBUS_RAW` | `product_usb_connector.B4_VBUS` | `product_usb_connector.B9_VBUS` | all four exact receptacle VBUS contacts are electrically present and independently soldered |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_controller.VBUS` | the separate controller VBUS pins power dead-battery attach detection, safe discharge and the internal startup LDO before any application rail exists |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_controller.VBUS_IN` | the separate VBUS_IN pins feed only the protected PPHV input path; SafeMode keeps that path off until a valid configuration is loaded |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_vbus_tvs.IN` | TVS2200DRVR is a shunt clamp physically adjacent to the receptacle, not a series element |
| `USB_C_VBUS_TVS_RETURN` | `pd_vbus_tvs.GND` | `abstract:power-ground` | short low-inductance surge return; exact placement and return geometry remain I4/layout gates |
| `POWER_GROUND` | `product_usb_connector.A1_GND` | `product_usb_connector.A12_GND` | both A-side ground contacts reach the local connector return plane |
| `POWER_GROUND` | `product_usb_connector.A12_GND` | `product_usb_connector.B1_GND` | all four signal/power ground contacts share the low-impedance local return |
| `POWER_GROUND` | `product_usb_connector.B1_GND` | `product_usb_connector.B12_GND` | all four exact ground contacts remain independently soldered |
| `POWER_GROUND` | `product_usb_connector.B12_GND` | `abstract:power-ground` | connector ground reaches the product power-ground plane through a short low-inductance region |
| `USB_C_SHIELD` | `product_usb_connector.SHIELD` | `abstract:chassis-ground-at-product-usb-entry` | four shell locks terminate at the entry-zone chassis/ESD structure; the final chassis-to-power-ground network remains a placement/HIL item |
| `USB_C_CC1_CONNECTOR` | `product_usb_connector.A5_CC1` | `product_usb_protector.C_CC1` | connector-side CC1 reaches only the 28-V short-to-VBUS and IEC-ESD protector input |
| `USB_C_CC2_CONNECTOR` | `product_usb_connector.B5_CC2` | `product_usb_protector.C_CC2` | connector-side CC2 reaches only the 28-V short-to-VBUS and IEC-ESD protector input |
| `USB_C_CC1_PROTECTED` | `product_usb_protector.CC1` | `pd_controller.CC1` | protected sink-only Type-C/PD detection; source, VCONN and power-bank roles are disabled |
| `USB_C_CC2_PROTECTED` | `product_usb_protector.CC2` | `pd_controller.CC2` | protected sink-only Type-C/PD detection; source, VCONN and power-bank roles are disabled |
| `USB_C_CC1_CONNECTOR` | `product_usb_protector.RPD_G1` | `product_usb_protector.C_CC1` | TI dead-battery ground-loop contact stays on connector-side CC1 exactly as required |
| `USB_C_CC2_CONNECTOR` | `product_usb_protector.RPD_G2` | `product_usb_protector.C_CC2` | TI dead-battery ground-loop contact stays on connector-side CC2 exactly as required |
| `USB2_DP_CONNECTOR` | `product_usb_connector.A6_DP` | `product_usb_connector.B6_DP` | both orientation-dependent D+ contacts join at the receptacle before protection |
| `USB2_DP_CONNECTOR` | `product_usb_connector.B6_DP` | `product_usb_protector.C_SBU1` | the first explicitly USB2-capable protector channel carries D+; it is not an Alt-Mode SBU route |
| `USB2_DP_PROTECTED` | `product_usb_protector.SBU1` | `product_usb_dp_series.END_1` | protected USB2 D+ reaches the exact 22-Ohm first-target source-termination position |
| `S3_USB_DP` | `product_usb_dp_series.END_2` | `s3.GPIO20` | series termination stays close to the S3 module; a 0402 shunt-capacitor position is reserved DNP pending Full-Speed signal-integrity HIL |
| `USB2_DM_CONNECTOR` | `product_usb_connector.A7_DM` | `product_usb_connector.B7_DM` | both orientation-dependent D- contacts join at the receptacle before protection |
| `USB2_DM_CONNECTOR` | `product_usb_connector.B7_DM` | `product_usb_protector.C_SBU2` | the second explicitly USB2-capable protector channel carries D-; it is not an Alt-Mode SBU route |
| `USB2_DM_PROTECTED` | `product_usb_protector.SBU2` | `product_usb_dm_series.END_1` | protected USB2 D- reaches the exact 22-Ohm first-target source-termination position |
| `S3_USB_DM` | `product_usb_dm_series.END_2` | `s3.GPIO19` | series termination stays close to the S3 module; a 0402 shunt-capacitor position is reserved DNP pending Full-Speed signal-integrity HIL |
| `NO_CONNECT` | `product_usb_connector.A8_SBU1` | `abstract:no-connect` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `NO_CONNECT` | `product_usb_connector.B8_SBU2` | `abstract:no-connect` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `product_usb_protector.VPWR` | the port protector is powered from the autonomous TPS local rail during dead-battery attach |
| `PD_LOCAL_3V3` | `product_usb_protector.VPWR` | `product_usb_vpwr_cap.END_1` | exact 1-uF 16-V X7R bypass follows the protector VPWR requirement |
| `POWER_GROUND` | `product_usb_vpwr_cap.END_2` | `abstract:power-ground` | VPWR bypass return is short and local |
| `USB_PROTECTOR_VBIAS` | `product_usb_protector.VBIAS` | `product_usb_vbias_cap.END_1` | exact 100-nF 100-V X7S capacitor provides the required high-voltage bias reservoir |
| `POWER_GROUND` | `product_usb_vbias_cap.END_2` | `abstract:power-ground` | VBIAS reservoir return is short and local |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `product_usb_fault_pullup.END_1` | fault evidence is pulled only to the protector supply and cannot back-power a disabled main rail |
| `USB_PROTECTOR_FAULT_N` | `product_usb_fault_pullup.END_2` | `product_usb_protector.FLT` | exact 10-kOhm pull-up exposes the open-drain fault without consuming a scarce MCU GPIO |
| `USB_PROTECTOR_FAULT_N` | `product_usb_protector.FLT` | `abstract:TP_USB_PROTECTOR_FAULT_N` | protected fixture test point provides automated electrical evidence; runtime detach and PD status remain the product-visible fault path |
| `POWER_GROUND` | `product_usb_protector.GND_8` | `abstract:power-ground` | first protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_13` | `abstract:power-ground` | second protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_18` | `abstract:power-ground` | third protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_PAD` | `abstract:power-ground` | exposed pad uses the datasheet thermal/ESD via structure |
| `NO_CONNECT` | `product_usb_protector.NC_16` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_17` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_19` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_20` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `nvdc_charger.VBUS` | accepted profiles stop at 15 V/2 A; the integrated protected path remains off above the negotiated envelope |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `pd_controller.VIN_3V3` | after autonomous dead-battery startup the PD controller runs from the admitted always-on rail; maximum active load is included in the 15-mA continuous budget |
| `PD_VIN_3V3` | `pd_controller.VIN_3V3` | `pd_vin_cap.END_1` | one exact 10-uF 6.3-V X5R capacitor is placed at VIN_3V3 |
| `POWER_GROUND` | `pd_vin_cap.END_2` | `abstract:power-ground` | VIN capacitor return is short and local |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_ldo3v3_cap.END_1` | one exact 10-uF capacitor stays inside the allowed 5-25-uF LDO_3V3 range |
| `POWER_GROUND` | `pd_ldo3v3_cap.END_2` | `abstract:power-ground` | LDO_3V3 capacitor return is short and local |
| `PD_LOCAL_1V5` | `pd_controller.LDO_1V5` | `pd_ldo1v5_cap.END_1` | one exact 10-uF capacitor stays inside the allowed 4.5-12-uF LDO_1V5 range |
| `POWER_GROUND` | `pd_ldo1v5_cap.END_2` | `abstract:power-ground` | LDO_1V5 capacitor return is short and local |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap0.END_1` | first exact 22-uF 25-V X7R output capacitor supports the protected path |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap1.END_1` | second physical 22-uF output capacitor is independent |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap2.END_1` | third physical 22-uF output capacitor is independent |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap3.END_1` | fourth physical 22-uF output capacitor brings nominal PPHV bulk to 88 uF inside the 47-100-uF requirement |
| `POWER_GROUND` | `pd_pphv_cap0.END_2` | `abstract:power-ground` | PPHV bulk return stays in the high-current local plane |
| `POWER_GROUND` | `pd_pphv_cap1.END_2` | `abstract:power-ground` | second PPHV capacitor has its own short return |
| `POWER_GROUND` | `pd_pphv_cap2.END_2` | `abstract:power-ground` | third PPHV capacitor has its own short return |
| `POWER_GROUND` | `pd_pphv_cap3.END_2` | `abstract:power-ground` | fourth PPHV capacitor has its own short return |
| `USB_C_VBUS_RAW` | `pd_controller.VBUS` | `pd_vbus_cap.END_1` | one exact 4.7-uF 25-V capacitor supports dead-battery attach and safe-discharge operation |
| `POWER_GROUND` | `pd_vbus_cap.END_2` | `abstract:power-ground` | VBUS capacitor is placed directly at the separate VBUS pins |
| `USB_C_CC1_PROTECTED` | `pd_controller.CC1` | `pd_cc1_cap.END_1` | 220-pF +/-5% C0G plus 120-pF TPS input and 40-120-pF protector totals 369-471 pF before route parasitics, leaving 129 pF to the USB-PD 600-pF ceiling |
| `POWER_GROUND` | `pd_cc1_cap.END_2` | `abstract:power-ground` | CC1 shunt stays adjacent and on the same layer as the controller contact |
| `USB_C_CC2_PROTECTED` | `pd_controller.CC2` | `pd_cc2_cap.END_1` | the identical 220-pF protected CC2 network preserves the same 369-471-pF paper range and route-parasitic margin |
| `POWER_GROUND` | `pd_cc2_cap.END_2` | `abstract:power-ground` | CC2 shunt stays adjacent and on the same layer as the controller contact |
| `PD_ADCIN1_SAFE_MODE_HIGH` | `pd_controller.LDO_3V3` | `pd_controller.ADCIN1` | decoded strap 7 selects the TI SafeMode boot row and target address index 1 |
| `PD_ADCIN2_SAFE_MODE_LOW` | `pd_controller.ADCIN2` | `abstract:power-ground` | decoded strap 0 completes the hardware SafeMode selection |
| `POWER_GROUND` | `pd_controller.PP5V` | `abstract:power-ground` | unused source/VCONN rail is grounded for the accepted sink-only application |
| `PD_DRAIN_COPPER` | `pd_controller.DRAIN_15` | `pd_controller.DRAIN_30` | both exposed drain contacts share the compact high-current thermal copper required by the integrated PPHV path |
| `PD_DRAIN_COPPER` | `pd_controller.DRAIN_30` | `pd_controller.DRAIN_PAD` | the exposed drain pad joins the same local drain copper and is not tied to ground |
| `POWER_GROUND` | `pd_controller.GND_11` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_12` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_14` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_31` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_PAD` | `abstract:power-ground` | the exposed ground pad receives the datasheet via array and thermal return |
| `POWER_GROUND` | `pd_controller.GPIO2` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO3` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO6` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO7` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO11` | `abstract:power-ground` | unused GPIO is never left floating |
| `CHARGER_VBUS_SENSE` | `nvdc_charger.VBUS` | `nvdc_charger.VAC1` | VAC1 is tied to VBUS exactly as required when the first external ACFET/RBFET pair is omitted |
| `CHARGER_VBUS_SENSE` | `nvdc_charger.VBUS` | `nvdc_charger.VAC2` | VAC2 is also tied to VBUS exactly as required when the second external ACFET/RBFET pair is omitted |
| `POWER_GROUND` | `nvdc_charger.ACDRV1` | `abstract:power-ground` | unused input-FET driver 1 is tied to ground per the exact pin requirement |
| `POWER_GROUND` | `nvdc_charger.ACDRV2` | `abstract:power-ground` | unused input-FET driver 2 is tied to ground per the exact pin requirement |
| `POWER_GROUND` | `nvdc_charger.GND` | `abstract:power-ground` | charger exposed ground return joins the compact converter ground plane |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_cap0.END_1` | first physical 10-uF 25-V X7R input capacitor supports the accepted 15-V source |
| `POWER_GROUND` | `charger_vbus_cap0.END_2` | `abstract:power-ground` | VBUS bulk return uses the short local charger power-ground path |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_cap1.END_1` | second independent 10-uF 25-V X7R input capacitor completes the required VBUS bank |
| `POWER_GROUND` | `charger_vbus_cap1.END_2` | `abstract:power-ground` | second VBUS bulk return stays local to the charger |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_hf_cap.END_1` | one exact 100-nF 50-V capacitor is placed directly at the VBUS pins |
| `POWER_GROUND` | `charger_vbus_hf_cap.END_2` | `abstract:power-ground` | VBUS HF return is direct and low inductance |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap0.END_1` | first physical 10-uF 25-V X7R PMID capacitor supports discontinuous buck current |
| `POWER_GROUND` | `charger_pmid_cap0.END_2` | `abstract:power-ground` | PMID bulk return stays inside the high-frequency converter loop |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap1.END_1` | second independent 10-uF 25-V X7R PMID capacitor is not collapsed into a quantity label |
| `POWER_GROUND` | `charger_pmid_cap1.END_2` | `abstract:power-ground` | second PMID bulk return stays local |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap2.END_1` | third independent 10-uF 25-V X7R PMID capacitor completes the required bank |
| `POWER_GROUND` | `charger_pmid_cap2.END_2` | `abstract:power-ground` | third PMID bulk return stays local |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_hf_cap.END_1` | one exact 100-nF 50-V capacitor sits directly at PMID and ground |
| `POWER_GROUND` | `charger_pmid_hf_cap.END_2` | `abstract:power-ground` | PMID HF return minimizes the switching-current loop |
| `CHARGER_SW1` | `nvdc_charger.SW1` | `charger_inductor.END_1` | the 750-kHz buck-side switching node reaches only the exact 2.2-uH power inductor |
| `CHARGER_SW2` | `charger_inductor.END_2` | `nvdc_charger.SW2` | 7-A saturation rating exceeds the calculated <=6.42-A device-limited peak before HIL margin |
| `CHARGER_BTST1` | `nvdc_charger.BTST1` | `charger_btst1_cap.END_1` | first exact 47-nF 25-V bootstrap capacitor follows the 750-kHz converter requirement |
| `CHARGER_SW1` | `charger_btst1_cap.END_2` | `nvdc_charger.SW1` | BTST1 capacitor returns directly to SW1 |
| `CHARGER_BTST2` | `nvdc_charger.BTST2` | `charger_btst2_cap.END_1` | second exact 47-nF 25-V bootstrap capacitor drives the SYS-side high switch |
| `CHARGER_SW2` | `charger_btst2_cap.END_2` | `nvdc_charger.SW2` | BTST2 capacitor returns directly to SW2 |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap0.END_1` | first physical 10-uF 25-V X7R SYS capacitor supports boost-output ripple |
| `POWER_GROUND` | `charger_sys_cap0.END_2` | `abstract:power-ground` | first SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap1.END_1` | second independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap1.END_2` | `abstract:power-ground` | second SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap2.END_1` | third independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap2.END_2` | `abstract:power-ground` | third SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap3.END_1` | fourth independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap3.END_2` | `abstract:power-ground` | fourth SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap4.END_1` | fifth independent 10-uF SYS capacitor completes the required bank |
| `POWER_GROUND` | `charger_sys_cap4.END_2` | `abstract:power-ground` | fifth SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_hf_cap.END_1` | one exact 100-nF 50-V capacitor sits directly at SYS and ground |
| `POWER_GROUND` | `charger_sys_hf_cap.END_2` | `abstract:power-ground` | SYS HF return minimizes the boost switching loop |
| `PROTECTED_PACK_POSITIVE` | `nvdc_charger.BAT` | `charger_bat_cap0.END_1` | first physical 10-uF 25-V X7R BAT capacitor stabilizes the admitted 2S boundary |
| `POWER_GROUND` | `charger_bat_cap0.END_2` | `abstract:power-ground` | first BAT bulk return stays local |
| `PROTECTED_PACK_POSITIVE` | `nvdc_charger.BAT` | `charger_bat_cap1.END_1` | second independent 10-uF BAT capacitor completes the required bank |
| `POWER_GROUND` | `charger_bat_cap1.END_2` | `abstract:power-ground` | second BAT bulk return stays local |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_regn_cap.END_1` | one exact 4.7-uF 25-V X7R capacitor stabilizes the internal gate-driver and TS-bias regulator |
| `POWER_GROUND` | `charger_regn_cap.END_2` | `abstract:power-ground` | REGN return follows the dedicated short-via layout rule |
| `CHARGER_SDRV_UNUSED` | `nvdc_charger.SDRV` | `charger_sdrv_cap.END_1` | latest Rev-C requirement for no external ship FET is exactly 1 nF, 50 V, 0402 to ground |
| `POWER_GROUND` | `charger_sdrv_cap.END_2` | `abstract:power-ground` | SDRV has no resistor and no BAT connection in the accepted no-ship-FET path |
| `CHARGER_PROG_2S_750KHZ` | `nvdc_charger.PROG` | `charger_prog_res.END_1` | 8.2-kOhm 1% strap selects 2S and 750 kHz at every POR and register reset |
| `POWER_GROUND` | `charger_prog_res.END_2` | `abstract:power-ground` | PROG strap is a permanent physical default rather than firmware state |
| `PROTECTED_PACK_POSITIVE` | `pack_power_fet.S2` | `charger_batp_res.END_1` | BATP senses the admitted pack boundary rather than a raw holder contact |
| `CHARGER_BATP_SENSE` | `charger_batp_res.END_2` | `nvdc_charger.BATP` | exact 100-Ohm series resistor follows the BATP pin requirement |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ts_top.END_1` | 5.23-kOhm 1% top resistor biases the direct charger thermistor gate |
| `CHARGER_TS` | `charger_ts_top.END_2` | `nvdc_charger.TS` | TS feedback remains enabled and independent of host firmware |
| `CHARGER_TS` | `nvdc_charger.TS` | `charger_ts_bottom.END_1` | 30.1-kOhm 1% bottom resistor completes the JEITA threshold network |
| `POWER_GROUND` | `charger_ts_bottom.END_2` | `abstract:power-ground` | fixed TS lower leg preserves open/short fault detection |
| `CHARGER_TS` | `nvdc_charger.TS` | `charger_ts_ntc.END_1` | third independent B57332V5103F360 gives BQ25798 a direct battery-temperature gate without loading either MAX17320 cell sensor |
| `POWER_GROUND` | `charger_ts_ntc.END_2` | `abstract:power-ground` | the third sensor is populated at one of two indexed compliant-contact locations on the thermally worst slot; open, short, lift and response-time behavior remain HIL gates |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ilim_top.END_1` | 44.2-kOhm 1% upper leg begins the independent hardware input-current ceiling |
| `CHARGER_ILIM_HIZ` | `charger_ilim_top.END_2` | `nvdc_charger.ILIM_HIZ` | physical target spans about 2.71-3.29 A over REGN and resistor corners and never replaces negotiated IINDPM |
| `CHARGER_ILIM_HIZ` | `nvdc_charger.ILIM_HIZ` | `charger_ilim_bottom.END_1` | 100-kOhm 1% lower leg keeps the pin above HIZ and below the 3.3-A recommended input ceiling |
| `POWER_GROUND` | `charger_ilim_bottom.END_2` | `abstract:power-ground` | hardware ILIM reference is independent of controller software |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_local_scl_pullup.END_1` | local-bus pull-up remains inside TPS, EEPROM and BQ digital voltage ranges |
| `PD_LOCAL_I2C_SCL` | `pd_local_scl_pullup.END_2` | `nvdc_charger.SCL` | one exact 2.2-kOhm pull-up follows the complete TPS25751 plus EEPROM plus charger bus reference |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_local_sda_pullup.END_1` | local data pull-up uses the autonomous TPS switched 3.3-V rail |
| `PD_LOCAL_I2C_SDA` | `pd_local_sda_pullup.END_2` | `nvdc_charger.SDA` | one exact 2.2-kOhm pull-up bounds rise time on the complete local multi-device bus |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `charger_int_pullup.END_1` | charger interrupt pull-up stays valid while the TPS local controller is active |
| `CHARGER_INT_N` | `charger_int_pullup.END_2` | `nvdc_charger.INT` | one physical 10-kOhm pull-up preserves the 256-us active-low interrupt pulse |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ce_pullup.END_1` | REGN rises before converter start and makes reset/default charge-disable independent of TPS firmware |
| `CHARGE_EN_N` | `charger_ce_pullup.END_2` | `nvdc_charger.CE` | 10-kOhm keeps CE high while TPS GPIO1 is Hi-Z; a valid image uses GPIO1 only as an open-drain active-low enable |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_i2c_scl_pullup.END_1` | the host I2C pull-up exists only with the S3 application domain and cannot back-power an off host |
| `SYS_I2C_SCL` | `sys_i2c_scl_pullup.END_2` | `s3.GPIO2` | one exact 2.2-kOhm pull-up serves the complete scheduled host-control bus |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_i2c_sda_pullup.END_1` | host data pull-up uses the common live logic domain |
| `SYS_I2C_SDA` | `sys_i2c_sda_pullup.END_2` | `s3.GPIO1` | one exact 2.2-kOhm pull-up serves the complete scheduled host-control bus |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_int_pullup.END_1` | the shared interrupt pull-up exists only with the host domain |
| `SYS_INT_N` | `sys_int_pullup.END_2` | `s3.GPIO37` | one exact 10-kOhm pull-up completes the wired-low interrupt tree without consuming another dedicated GPIO |
| `CHARGER_QON_NC` | `nvdc_charger.QON` | `abstract:no-connect` | QON uses its specified internal pull-up; no external system-reset or ship-FET function is claimed |
| `CHARGER_STAT_NC` | `nvdc_charger.STAT` | `abstract:no-connect` | unused open-drain STAT is disabled in the charger image; status and faults use INT/I2C |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `pd_config_eeprom.SDA` | dedicated address-0x50 boot image; one EEPROM per controller |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `pd_config_eeprom.SCL` | controller loads patch/config autonomously before S3 availability is assumed |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `nvdc_charger.SDA` | charger is controlled through the officially supported TPS25751D local-controller topology |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `nvdc_charger.SCL` | charger transactions never occupy an RF, display or storage bus |
| `PACK_AOLDO` | `pack_gauge.AOLDO` | `pack_supply_or.A1` | AOLDO supplies only measured low-clock admission below the MAX17320 2-mA source budget; BAV70LT1G blocks fixture/system backfeed |
| `PACK_FIXTURE_3V3` | `abstract:isolated-pack-fixture-3v3` | `pack_supply_or.A2` | fixture supply is isolated from USB/system power and is used for blank-device programming and recovery |
| `PACK_ADMISSION_VDD` | `pack_supply_or.K_COMMON` | `pack_admission.VDD` | common cathode passively ORs AOLDO and fixture sources without firmware control |
| `PACK_SYSTEM_3V3` | `abstract:admitted-system-3v3` | `pack_system_diode.A` | system source exists only after complete pair admission and uses the lower-drop branch |
| `PACK_ADMISSION_VDD` | `pack_system_diode.K` | `pack_admission.VDD` | BAT54-7-F blocks admission VDD from back-powering the admitted system rail |
| `PACK_ADMISSION_VDD` | `pack_supply_or.K_COMMON` | `pack_diag_timer.VCC` | the hardware pulse limiter is alive whenever the admission MCU can request a diagnostic; its ready-state current remains inside the AOLDO budget |
| `PACK_DIAG_TIMER_VCC` | `pack_diag_timer.VCC` | `pack_diag_timer_bypass.END_1` | one exact 100-nF local bypass capacitor supports one-shot switching without coupling the diagnostic edge into the admission ADC reference |
| `PACK_LOCAL_GND` | `pack_diag_timer_bypass.END_2` | `pack_gauge.GND` | timer bypass return stays local to the admission controller and gauge |
| `PACK_LOCAL_GND` | `pack_diag_timer.GND` | `pack_gauge.GND` | one-shot and admission MCU share the same pack-side logic reference |
| `PACK_DIAG_TRIGGER` | `pack_admission.PA22_A4` | `pack_diag_timer.CH1_T` | firmware emits a rising edge only; holding or repeatedly toggling the pin cannot extend an active non-retriggerable pulse |
| `PACK_DIAG_TRIGGER` | `pack_admission.PA22_A4` | `pack_diag_trigger_pulldown.END_1` | the exact 10-kOhm pull-down prevents a reset-default high-impedance contact from producing a diagnostic pulse |
| `PACK_LOCAL_GND` | `pack_diag_trigger_pulldown.END_2` | `pack_gauge.GND` | trigger default is low in reset, fixture handover and unpowered-MCU states |
| `PACK_DIAG_CH1_FALLING_TRIGGER_DISABLED` | `pack_diag_timer.CH1_T_N` | `pack_gauge.GND` | the unused falling-edge trigger is fixed low for rising-edge-only operation |
| `PACK_DIAG_REFRACTORY_CLEAR_N` | `pack_diag_timer.CH2_Q_N` | `pack_diag_timer.CH1_CLR_N` | complementary channel-2 output is high while ready and asynchronously holds channel 1 clear throughout every hardware refractory interval |
| `PACK_DIAG_TIMER_RC_SUPPLY` | `pack_diag_timer.VCC` | `pack_diag_timer_res.END_1` | 169-kOhm 1% timing resistance reuses an existing BOM line |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer_res.END_2` | `pack_diag_timer.CH1_RC` | the timing node follows the TPUL2G223 manufacturer connection |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer.CH1_RC` | `pack_diag_timer_cap.END_1` | 169-kOhm with 220-nF yields about 34.4 ms typical |
| `PACK_DIAG_TIMER_C` | `pack_diag_timer_cap.END_2` | `pack_diag_timer.CH1_C` | the exact C0G timing capacitor bounds both sides of the paper pulse window without X7R DC-bias or aging ambiguity |
| `PACK_LOCAL_GND` | `pack_diag_timer.CH1_C` | `pack_gauge.GND` | the optional external C-terminal ground is used to give the timing capacitor an explicit local return |
| `PACK_DIAG_GATE` | `pack_diag_timer.CH1_Q` | `pack_diag_switch.G` | only the hardware one-shot output, never a direct MCU level, can hold the diagnostic MOSFET on |
| `PACK_DIAG_GATE` | `pack_diag_switch.G` | `pack_diag_gate_pulldown.END_1` | the MOSFET gate remains low if the one-shot supply is absent or its output is high impedance |
| `PACK_LOCAL_GND` | `pack_diag_gate_pulldown.END_2` | `pack_gauge.GND` | 10-kOhm gate pull-down fails the diagnostic load off |
| `PACK_DIAG_CH1_Q_N_NC` | `pack_diag_timer.CH1_Q_N` | `abstract:no-connect` | unused push-pull complementary channel-1 output is left open as required |
| `PACK_DIAG_PULSE_ACTIVE` | `pack_diag_timer.CH1_Q` | `pack_diag_timer.CH2_T_N` | the falling edge at the natural end of channel 1 starts channel 2; the rising edge at pulse start cannot trigger the falling-edge input |
| `PACK_DIAG_CH2_RISING_GATE_HIGH` | `pack_diag_timer.VCC` | `pack_diag_timer.CH2_T` | the channel-2 rising-edge gate is fixed high so only the channel-1 Q falling edge is accepted |
| `PACK_DIAG_CH2_CLEAR_RELEASED` | `pack_diag_timer.VCC` | `pack_diag_timer.CH2_CLR_N` | channel 2 remains independently non-retriggerable and cannot be shortened by firmware |
| `PACK_DIAG_LOCKOUT_RC_SUPPLY` | `pack_diag_timer.VCC` | `pack_diag_lockout_res.END_1` | exact 620-kOhm 1% resistance begins the bounded hardware refractory timer |
| `PACK_DIAG_LOCKOUT_RC` | `pack_diag_lockout_res.END_2` | `pack_diag_timer.CH2_RC` | the channel-2 timing node follows the manufacturer connection |
| `PACK_DIAG_LOCKOUT_RC` | `pack_diag_timer.CH2_RC` | `pack_diag_lockout_cap.END_1` | 620-kOhm and 1-uF yield about 569 ms typical and remain inside the TPUL2G223 supported pulse-width range |
| `PACK_DIAG_LOCKOUT_C` | `pack_diag_lockout_cap.END_2` | `pack_diag_timer.CH2_C` | the exact TDK X7R part is screened with initial, temperature and 3.3-V DC-bias loss for at least 350 ms hardware lockout |
| `PACK_LOCAL_GND` | `pack_diag_timer.CH2_C` | `pack_gauge.GND` | the channel-2 timing capacitor has an explicit local return |
| `PACK_DIAG_CH2_Q_NC` | `pack_diag_timer.CH2_Q` | `abstract:no-connect` | unused push-pull active-high channel-2 output is left open as required |
| `PACK_LOCAL_GND` | `pack_admission.VSS` | `pack_gauge.GND` | local controller, gauge and fixture share one bounded pack-side reference; USB/system isolation and touch-safe access remain exact circuit gates |
| `PACK_HOLD_PULLUP_SOURCE` | `pack_gauge.AOLDO` | `abstract:exact-value-hold-gate-pullup` | exact-value resistor pulls Q1 gate high without exceeding the AOLDO budget |
| `PACK_HOLD_GATE` | `abstract:exact-value-hold-gate-pullup` | `pack_hold.G1` | reset or unpowered admission MCU turns Q1 on and asserts the hold |
| `PACK_FET_OVERRIDE_N` | `pack_hold.D1` | `pack_gauge.ALRT` | Q1 asserts ALRT low before MCU code; release follows protected gauge image/readback and complete pair admission only |
| `PACK_LOCAL_GND` | `pack_hold.S1` | `pack_gauge.GND` | Q1 has a local pack-side return |
| `PACK_HOLD_GATE` | `pack_hold.D2` | `pack_hold.G1` | Q2 can pull the Q1 gate low only after PA6 explicitly requests release |
| `PACK_LOCAL_GND` | `pack_hold.S2` | `pack_gauge.GND` | Q2 has a local pack-side return; its gate has an exact-value reset pulldown still to be frozen |
| `SYS_INT_N` | `abstract:pack-admission reset-safe open-drain IRQ circuit` | `s3.GPIO37` | reset, unpowered admission MCU and push-pull faults cannot drive the shared IRQ high or back-power the system bus |
| `PACK_CHG_GATE` | `pack_gauge.CHG` | `pack_power_fet.G1` | CSD87313DMST FET1 source is the cell-stack side required by MAX17320 CHG referenced to IN; exact 0.1-uF gate-source capacitor remains a schematic value |
| `PACK_DIS_GATE` | `pack_gauge.DIS` | `pack_power_fet.G2` | CSD87313DMST FET2 source is the pack side required by MAX17320 DIS referenced to PCKP |
| `PACK_ZVC_UNUSED` | `pack_gauge.ZVC` | `abstract:no-connect` | DEC-0067 forbids in-device zero-volt recovery; the datasheet requires ZVC open when unused |
| `BATTERY_STACK_POSITIVE` | `abstract:qualified-2s-positive` | `pack_power_fet.S1` | battery-side source enters a common-drain back-to-back pair; zero-volt and prequal recovery remain disabled |
| `PROTECTED_PACK_POSITIVE` | `pack_power_fet.S2` | `nvdc_charger.BAT` | pack-side source reaches the charger only after complete admission and MAX17320 protection permission |
| `PACK_SHUNT_CSP` | `pack_gauge.CSP` | `pack_shunt.END_1` | Kelvin pickup follows the ADI Figure-24 current-sense orientation |
| `PACK_SHUNT_CSN` | `pack_shunt.END_2` | `pack_gauge.CSN` | 5-mOhm shunt yields the accepted measurement range; force/kelvin copper geometry remains an I4 gate |
| `PACK_CELL0_TEMP` | `pack_gauge.TH1` | `pack_ntc0.END_1` | one exact 10-kOhm NTC uses a dedicated insulated compliant contact through the open holder window to the middle third of cell 0; compression and response remain I8/HIL gates |
| `PACK_LOCAL_GND` | `pack_ntc0.END_2` | `pack_gauge.GND` | TH1 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_CELL1_TEMP` | `pack_gauge.TH2` | `pack_ntc1.END_1` | one exact 10-kOhm NTC uses a dedicated insulated compliant contact through the open holder window to the middle third of cell 1; compression and response remain I8/HIL gates |
| `PACK_LOCAL_GND` | `pack_ntc1.END_2` | `pack_gauge.GND` | TH2 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_SLOT0_POSITIVE_RAW` | `pack_cell0.POS` | `pack_holder.SLOT0_POS` | only the exact protected button-top qualification target is modeled; physical polarity and received-lot identity remain admission prerequisites |
| `PACK_LOCAL_GND` | `pack_cell0.NEG` | `pack_holder.SLOT0_NEG` | the exact cell negative end reaches local pack ground only through the mechanically polarized holder contact |
| `PACK_SLOT1_POSITIVE_RAW` | `pack_cell1.POS` | `pack_holder.SLOT1_POS` | the upper exact protected cell remains a separately replaceable physical device with its own holder contact and fuse path |
| `PACK_2S_MIDPOINT` | `pack_cell1.NEG` | `pack_holder.SLOT1_NEG` | the upper cell negative end forms the supervised midpoint only after correct physical insertion into the exact holder |
| `PACK_SLOT0_POSITIVE_RAW` | `pack_holder.SLOT0_POS` | `pack_fuse0.END_1` | the polarized holder exposes the lower-cell positive contact separately and the adjacent 5-A fuse remains slot-specific |
| `PACK_2S_MIDPOINT` | `pack_fuse0.END_2` | `abstract:protected-2s-midpoint` | slot-0 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_LOCAL_GND` | `pack_holder.SLOT0_NEG` | `pack_gauge.GND` | the lower-cell negative contact is independently exposed; reverse insertion remains open before this local reference is reached |
| `PACK_2S_MIDPOINT` | `pack_holder.SLOT1_NEG` | `abstract:protected-2s-midpoint` | the upper-cell negative contact is independently exposed and forms the supervised 2S midpoint only in the PCB routing |
| `PACK_SLOT1_POSITIVE_RAW` | `pack_holder.SLOT1_POS` | `pack_fuse1.END_1` | the polarized holder exposes the upper-cell positive contact separately and the adjacent 5-A fuse remains slot-specific |
| `BATTERY_STACK_POSITIVE` | `pack_fuse1.END_2` | `abstract:qualified-2s-positive` | slot-1 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_DIAG_LOAD_POSITIVE` | `abstract:qualified-2s-positive` | `pack_diag_res0.END_1` | the first 20-Ohm 2-W pulse-rated branch samples the fused full stack ahead of the normally-open CHG/DIS pair |
| `PACK_DIAG_LOAD_POSITIVE` | `abstract:qualified-2s-positive` | `pack_diag_res1.END_1` | the second equal branch provides exact 10-Ohm total resistance and shares both pulse and hostile-repetition heat |
| `PACK_DIAG_LOAD_DRAIN` | `pack_diag_res0.END_2` | `pack_diag_switch.D` | one-percent matched-value branches bound effective load resistance to 9.9-10.1 Ohm before MOSFET resistance |
| `PACK_DIAG_LOAD_DRAIN` | `pack_diag_res1.END_2` | `pack_diag_switch.D` | each resistor sees half the approximately 7.82-W worst-screen load and remains below the official 50-ms pulse curve |
| `PACK_LOCAL_GND` | `pack_diag_switch.S` | `pack_gauge.GND` | the 20-V low-gate-drive MOSFET closes only the bounded pre-admission diagnostic path |
| `PACK_MID_DIV_TOP` | `abstract:protected-2s-midpoint` | `pack_mid_adc_top0.END_1` | first 220-kOhm series element begins the protected midpoint divider |
| `PACK_MID_DIV_SERIES` | `pack_mid_adc_top0.END_2` | `pack_mid_adc_top1.END_1` | two physical top resistors limit fault and injection current rather than relying on one high-side element |
| `PACK_CELL0_ADC` | `pack_mid_adc_top1.END_2` | `pack_admission.PA25_A2` | 2x220-kOhm over 169-kOhm keeps the 4.3-V screen corner below 1.21 V with 1% resistor tolerance |
| `PACK_CELL0_ADC` | `pack_admission.PA25_A2` | `pack_mid_adc_bottom.END_1` | 169-kOhm bottom resistor reuses an active stocked BOM value |
| `PACK_LOCAL_GND` | `pack_mid_adc_bottom.END_2` | `pack_gauge.GND` | midpoint divider return shares the quiet admission ADC reference |
| `PACK_CELL0_ADC` | `pack_admission.PA25_A2` | `pack_mid_adc_filter.END_1` | 10-nF filter supports a bounded settled sample rather than sampling the load edge |
| `PACK_LOCAL_GND` | `pack_mid_adc_filter.END_2` | `pack_gauge.GND` | midpoint ADC filter return stays at the admission reference |
| `PACK_STACK_DIV_TOP` | `abstract:qualified-2s-positive` | `pack_stack_adc_top0.END_1` | first of five 220-kOhm series elements begins the fused full-stack divider |
| `PACK_STACK_DIV_SERIES_01` | `pack_stack_adc_top0.END_2` | `pack_stack_adc_top1.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_12` | `pack_stack_adc_top1.END_2` | `pack_stack_adc_top2.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_23` | `pack_stack_adc_top2.END_2` | `pack_stack_adc_top3.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_34` | `pack_stack_adc_top3.END_2` | `pack_stack_adc_top4.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_ADC` | `pack_stack_adc_top4.END_2` | `pack_admission.PA26_A1` | 5x220-kOhm over 169-kOhm keeps the 8.6-V screen corner below 1.17 V with 1% resistor tolerance |
| `PACK_STACK_ADC` | `pack_admission.PA26_A1` | `pack_stack_adc_bottom.END_1` | 169-kOhm bottom resistor completes the full-stack divider |
| `PACK_LOCAL_GND` | `pack_stack_adc_bottom.END_2` | `pack_gauge.GND` | stack divider return shares the quiet admission ADC reference |
| `PACK_STACK_ADC` | `pack_admission.PA26_A1` | `pack_stack_adc_filter.END_1` | 10-nF filter supports a bounded settled sample and rejects the load-switch edge |
| `PACK_LOCAL_GND` | `pack_stack_adc_filter.END_2` | `pack_gauge.GND` | stack ADC filter return stays at the admission reference |
| `CHARGER_INT_N` | `nvdc_charger.INT` | `pd_controller.I2Cc_IRQ` | active-low charger status/fault returns to the PD controller without a new MCU contact |
| `PD_EEPROM_WP` | `pd_controller.GPIO0` | `pd_config_eeprom.WP` | external pull-up protects the image at reset; TPS may drive low only inside an S3-authorized signed update window |
| `CHARGE_EN_N` | `pd_controller.GPIO1` | `nvdc_charger.CE` | GPIO1 is open-drain only; exact REGN pull-up disables charge while TPS configuration is absent/invalid and valid policy sinks only after IINDPM is written |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_config_eeprom.VCC` | the boot EEPROM is powered by the controller LDO during raw-VBUS dead-battery startup |
| `PD_LOCAL_3V3` | `pd_config_eeprom.VCC` | `pd_eeprom_bypass.END_1` | one exact 100-nF 50-V X7R bypass is placed at the EEPROM supply |
| `POWER_GROUND` | `pd_eeprom_bypass.END_2` | `abstract:power-ground` | EEPROM bypass return is short and local |
| `POWER_GROUND` | `pd_config_eeprom.VSS` | `abstract:power-ground` | EEPROM ground is explicit for both product and recovery fixtures |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_eeprom_wp_pullup.END_1` | WP defaults high whenever the EEPROM is powered |
| `PD_EEPROM_WP` | `pd_eeprom_wp_pullup.END_2` | `pd_config_eeprom.WP` | exact 10-kOhm pull-up dominates reset Hi-Z while allowing the controller open-drain output to authorize writes |
| `PD_EEPROM_A0_LOW` | `abstract:power-ground` | `pd_config_eeprom.A0` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A1_LOW` | `abstract:power-ground` | `pd_config_eeprom.A1` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A2_LOW` | `abstract:power-ground` | `pd_config_eeprom.A2` | fixed 7-bit address 0x50 |
| `PD_USB_P_UNUSED_LOW` | `pd_controller.GPIO4_USB_P_LD1` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D+ remains direct to S3; datasheet requires unused contact low |
| `PD_USB_N_UNUSED_LOW` | `pd_controller.GPIO5_USB_N_LD2` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D- remains direct to S3; datasheet requires unused contact low |
| `CHARGER_DP_NC` | `nvdc_charger.D_PLUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `CHARGER_DM_NC` | `nvdc_charger.D_MINUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_buck.VIN` | the AON source is independent of every application rail and remains available on admitted battery or valid USB system power |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_input_cap.END_1` | one exact 4.7-uF 25-V X7R input capacitor is the TPS629203 nominal local input target |
| `POWER_GROUND` | `aon_input_cap.END_2` | `abstract:power-ground` | the AON input-capacitor loop must be placed directly at VIN and GND |
| `AON_BUCK_EN` | `nvdc_charger.SYS` | `aon_buck.EN` | direct hardware strap is manufacturer-valid, has no uncertain divider against the internal fail-low pull-down and enables AON without application firmware |
| `AON_BUCK_SW` | `aon_buck.SW` | `aon_inductor.END_1` | 2.2-uH shielded inductor is the manufacturer-nominal 2.5-MHz first target |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `abstract:AON_RAW_3V3` | regulated converter output is deliberately separated from the safety rail by an independent overvoltage/current boundary |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_output_cap.END_1` | one exact 22-uF 10-V X7R capacitor provides the recommended nominal converter output capacitance before the protection boundary |
| `POWER_GROUND` | `aon_output_cap.END_2` | `abstract:power-ground` | VOS senses the capacitor positive terminal and its return remains local to the converter |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse.IN` | TPS25961 is an independent series cutoff for a shorted converter high-side switch, overload, short and thermal fault |
| `AON_EFUSE_EN` | `aon_inductor.END_2` | `aon_efuse.EN_UVLO` | direct raw-rail tie is manufacturer-valid below 5 V and gives firmware no bypass path |
| `POWER_GROUND` | `aon_efuse.GND` | `abstract:power-ground` | exposed pad and ground contact share the short local power return |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse_input_cap.END_1` | 100-nF 50-V X7R sits directly at the eFuse input in addition to the converter output bank |
| `POWER_GROUND` | `aon_efuse_input_cap.END_2` | `abstract:power-ground` | local high-frequency eFuse input return |
| `AON_EFUSE_ILIM` | `aon_efuse.ILIM` | `aon_efuse_rilim.END_1` | 240-kOhm sets about 0.208-A nominal limit, above protected AON startup and load demand but below converter capability |
| `POWER_GROUND` | `aon_efuse_rilim.END_2` | `abstract:power-ground` | one exact current-limit resistor; open moves TPS25961 toward its minimum limit rather than disabling protection |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse_ovlo_top.END_1` | 196-kOhm 1% starts the independent AON overvoltage divider |
| `AON_EFUSE_OVLO` | `aon_efuse_ovlo_top.END_2` | `aon_efuse.OVLO` | 196/100-kOhm divider yields a 3.505-to-3.809-V full-corner cutoff window |
| `AON_EFUSE_OVLO` | `aon_efuse.OVLO` | `aon_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `aon_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 1% completes the OVLO divider |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `abstract:AON_SAFE_3V3` | only the independently protected output powers the supervisor, hard-STOP logic and PD VIN_3V3 |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `aon_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact protected-side hold-up and local output capacitor |
| `POWER_GROUND` | `aon_efuse_output_cap.END_2` | `abstract:power-ground` | protected AON local return |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `aon_pg_pullup.END_1` | 47-kOhm pull-up exists only after the independent cutoff and limits the always-on PG load to about 70 uA |
| `AON_PG_N` | `aon_pg_pullup.END_2` | `aon_buck.PG` | open-drain AON evidence has a defined high only after its own output rail exists |
| `AON_RAW_3V3_SENSE` | `abstract:AON_RAW_3V3` | `aon_buck.VOS` | converter remote sense remains at its own pre-eFuse output capacitor; the supervisor independently validates the protected output |
| `AON_VSET_3V3_NC` | `abstract:no-connect-open-vset` | `aon_buck.FB_VSET` | FB/VSET is deliberately left open; the datasheet decodes open or at least 249 kOhm as fixed 3.3 V |
| `AON_MODE_SET` | `aon_buck.MODE_SCONF` | `aon_mode_res.END_1` | 42.2-kOhm 1% selects VSET, up-to-2.5-MHz auto-PFM/PWM AEE and disabled output discharge |
| `POWER_GROUND` | `aon_mode_res.END_2` | `abstract:power-ground` | fixed resistor strap is read at startup and cannot be changed by application firmware |
| `AON_PG_N` | `aon_buck.PG` | `safe_supervisor.MR_N` | the pulled-up converter PG directly holds the exact AON supervisor in manual reset until the converter reports valid output; there is no programmable source-sequencer dependency |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_buck.VIN` | independent fixed converter prevents compute transients from changing voice or accessory voltage |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor exceeds the TPS564252 nominal input recommendation |
| `POWER_GROUND` | `main_input_cap.END_2` | `abstract:power-ground` | main bulk input return stays inside the high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency VIN current |
| `POWER_GROUND` | `main_hf_input_cap.END_2` | `abstract:power-ground` | main high-frequency input return is placed directly at converter ground |
| `POR_N` | `safe_supervisor.RESET_N` | `main_buck.EN` | the exact open-drain AON supervisor releases the main converter only after AON PG, the 3.07-V SENSE threshold and the CT delay all pass |
| `POR_N` | `main_buck.EN` | `main_en_pulldown.END_1` | external 100-kOhm reset-low default with the exact 10-kOhm POR pull-up releases to about 3.0V, above the converter's 1.25-V maximum rising threshold |
| `POWER_GROUND` | `main_en_pulldown.END_2` | `abstract:power-ground` | main converter stays disabled if the AON POR pull-up or AON source is absent |
| `MAIN_BUCK_SW` | `main_buck.SW` | `main_inductor.END_1` | 3.3-uH exact first target keeps the 3-A load-step peak below its minimum saturation current |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `abstract:MAIN_RAW_3V3` | regulated output is a raw converter rail until the independent latch-off protection accepts it |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_fb_top.END_1` | active 45.3-kOhm replacement for the obsolete 45.0-kOhm table value starts the fixed main feedback divider |
| `MAIN_3V3_FB` | `main_fb_top.END_2` | `main_buck.FB` | 45.3-kOhm over 10-kOhm sets nominal 3.318 V without a selector or firmware control |
| `MAIN_3V3_FB` | `main_buck.FB` | `main_fb_bottom.END_1` | 1% bottom resistor completes the fixed main feedback divider |
| `POWER_GROUND` | `main_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin feedback return must not share the switching-current return |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_ff_cap.END_1` | 33-pF C0G feed-forward capacitor stays inside the datasheet 10-to-100-pF high-output range |
| `MAIN_3V3_FB` | `main_ff_cap.END_2` | `main_buck.FB` | feed-forward element is physically across the top divider resistor |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_output_cap0.END_1` | first physical 22-uF 25-V X7R pre-eFuse capacitor contributes to the recommended 44-uF nominal converter bank |
| `POWER_GROUND` | `main_output_cap0.END_2` | `abstract:power-ground` | first main output capacitor closes the local power loop |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_output_cap1.END_1` | second independent 22-uF 25-V X7R pre-eFuse capacitor preserves DC-bias and transient margin |
| `POWER_GROUND` | `main_output_cap1.END_2` | `abstract:power-ground` | second main output capacitor closes the local power loop |
| `MAIN_RAW_3V3_PG_N` | `main_buck.PG` | `abstract:main-raw-converter-pg-test` | raw converter PG is a fixture-pulled diagnostic point and cannot certify the protected load side |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_efuse.IN` | independent latch-off circuit breaker interrupts converter high-side short overvoltage and downstream overload faults |
| `MAIN_EFUSE_EN` | `main_inductor.END_2` | `main_efuse.EN_UVLO` | direct sub-5-V raw-rail tie is manufacturer-valid and cannot be bypassed by firmware |
| `POWER_GROUND` | `main_efuse.GND` | `abstract:power-ground` | short low-inductance protection return |
| `MAIN_EFUSE_ILM` | `main_efuse.ILM` | `main_efuse_rilm.END_1` | 1.65-kOhm sets a guaranteed 3.2-to-3.715-A circuit-breaker threshold above the accepted 3.0-A step |
| `POWER_GROUND` | `main_efuse_rilm.END_2` | `abstract:power-ground` | ILM open or short are both detected fail-safe single-point states by TPS25974 |
| `MAIN_EFUSE_DVDT` | `main_efuse.DVDT` | `main_efuse_dvdt_cap.END_1` | 4.7-nF controls protected-output rise to about 4.7 ms at 3.3 V |
| `POWER_GROUND` | `main_efuse_dvdt_cap.END_2` | `abstract:power-ground` | exact slew capacitor limits protected-side inrush |
| `MAIN_EFUSE_ITIMER` | `main_efuse.ITIMER` | `main_efuse_itimer_cap.END_1` | 120-pF C0G permits only about 0.09-ms nominal sub-fast-trip overload before latch-off |
| `POWER_GROUND` | `main_efuse_itimer_cap.END_2` | `abstract:power-ground` | bounded timer does not defeat the independent fast-trip path |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_efuse_ovlo_top.END_1` | 191-kOhm 0.1% thin-film top resistor begins the tight main-rail OVLO divider |
| `MAIN_EFUSE_OVLO` | `main_efuse_ovlo_top.END_2` | `main_efuse.OVLO` | precision divider keeps full-corner cutoff between 3.438 and 3.578 V |
| `MAIN_EFUSE_OVLO` | `main_efuse.OVLO` | `main_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `main_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 0.1% thin-film bottom resistor completes the narrow safe window |
| `3V3_MAIN` | `main_efuse.OUT` | `abstract:3V3_MAIN` | only the protected output supplies compute, UI and quiet-state switches at 2.5-A continuous and 3.0-A step demand |
| `3V3_MAIN` | `main_efuse.OUT` | `main_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact local protected-side capacitor |
| `POWER_GROUND` | `main_efuse_output_cap.END_2` | `abstract:power-ground` | protected main local return |
| `3V3_MAIN` | `main_efuse.OUT` | `main_efuse_pg_top.END_1` | 45.3-kOhm 1% starts the protected-output power-good divider |
| `MAIN_EFUSE_PGTH` | `main_efuse_pg_top.END_2` | `main_efuse.PGTH` | 45.3/30-kOhm divider asserts only after the protected rail crosses approximately 3.0 V |
| `MAIN_EFUSE_PGTH` | `main_efuse.PGTH` | `main_efuse_pg_bottom.END_1` | PGTH directly measures protected output, not raw converter output |
| `POWER_GROUND` | `main_efuse_pg_bottom.END_2` | `abstract:power-ground` | 30-kOhm 1% completes the PG divider |
| `MAIN_3V3_PG_N` | `main_efuse.PG` | `abstract:power-current-thermal-fault` | protected-rail PG replaces raw converter PG as the diagnostic aggregate source |
| `3V3_MAIN` | `main_efuse.OUT` | `power_fault_pullup.END_1` | one exact pull-up serves the entire wired-low fault aggregate only while its protected diagnostic domain is powered |
| `POWER_FAULT_N` | `power_fault_pullup.END_2` | `abstract:power-current-thermal-fault` | 10-kOhm limits any asserting PG, FLT or qualifier sink to about 0.33 mA |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_buck.VIN` | voice has a physically independent fixed-voltage converter rather than a shared 4/5-V selector |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor keeps the voice switching loop independent |
| `POWER_GROUND` | `voice_input_cap.END_2` | `abstract:power-ground` | voice bulk input return stays inside its own high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency voice-converter VIN current |
| `POWER_GROUND` | `voice_hf_input_cap.END_2` | `abstract:power-ground` | voice high-frequency input return is placed directly at converter ground |
| `VOICE_BUCK_SW` | `voice_buck.SW` | `voice_inductor.END_1` | 3.3-uH exact first target has margin over the qualified 1.5-A transient peak current |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `abstract:VVOICE_RAW_4V` | fixed 4.0-V converter output is raw until the independent latch-off protection accepts it |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_fb_top.END_1` | 68-kOhm 1% top resistor starts the physically fixed voice feedback divider |
| `VOICE_4V_FB` | `voice_fb_top.END_2` | `voice_buck.FB` | 68-kOhm over 12-kOhm sets nominal 4.000 V without a selector |
| `VOICE_4V_FB` | `voice_buck.FB` | `voice_fb_bottom.END_1` | 12-kOhm 1% bottom resistor completes the fixed voice divider |
| `POWER_GROUND` | `voice_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin return prevents load current from shifting the voice set point |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_ff_cap.END_1` | 33-pF C0G feed-forward capacitor follows the datasheet high-output recommendation |
| `VOICE_4V_FB` | `voice_ff_cap.END_2` | `voice_buck.FB` | feed-forward element is physically across the voice top divider resistor |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_output_cap0.END_1` | first physical 22-uF 25-V X7R pre-eFuse capacitor supports converter stability and startup |
| `POWER_GROUND` | `voice_output_cap0.END_2` | `abstract:power-ground` | first voice output capacitor closes its local power loop |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_output_cap1.END_1` | second independent 22-uF 25-V X7R pre-eFuse capacitor completes the 44-uF nominal converter bank |
| `POWER_GROUND` | `voice_output_cap1.END_2` | `abstract:power-ground` | second voice output capacitor closes its local power loop |
| `VOICE_RAW_4V_PG_N` | `voice_buck.PG` | `abstract:voice-raw-converter-pg-test` | raw converter PG is fixture-only and cannot certify the protected module supply |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_efuse.IN` | independent latch-off circuit breaker interrupts converter high-side short overvoltage and downstream overload faults |
| `VOICE_EFUSE_EN` | `voice_inductor.END_2` | `voice_efuse.EN_UVLO` | direct sub-5-V raw-rail tie is manufacturer-valid and cannot be bypassed by firmware |
| `POWER_GROUND` | `voice_efuse.GND` | `abstract:power-ground` | short low-inductance protection return |
| `VOICE_EFUSE_ILM` | `voice_efuse.ILM` | `voice_efuse_rilm.END_1` | 3.32-kOhm sets a guaranteed 1.55-to-1.905-A circuit-breaker threshold above the accepted 1.5-A transient |
| `POWER_GROUND` | `voice_efuse_rilm.END_2` | `abstract:power-ground` | ILM open or short are both detected fail-safe single-point states by TPS25974 |
| `VOICE_EFUSE_DVDT` | `voice_efuse.DVDT` | `voice_efuse_dvdt_cap.END_1` | 4.7-nF controls protected-output rise to about 5.7 ms at 4.0 V |
| `POWER_GROUND` | `voice_efuse_dvdt_cap.END_2` | `abstract:power-ground` | exact slew capacitor limits module-side inrush |
| `VOICE_EFUSE_ITIMER` | `voice_efuse.ITIMER` | `voice_efuse_itimer_cap.END_1` | 120-pF C0G permits only about 0.09-ms nominal sub-fast-trip overload before latch-off |
| `POWER_GROUND` | `voice_efuse_itimer_cap.END_2` | `abstract:power-ground` | bounded timer preserves fast-trip short protection |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_efuse_ovlo_top.END_1` | 270-kOhm 1% starts the independent voice-rail overvoltage divider |
| `VOICE_EFUSE_OVLO` | `voice_efuse_ovlo_top.END_2` | `voice_efuse.OVLO` | 270/100-kOhm divider yields a 4.314-to-4.610-V full-corner cutoff window |
| `VOICE_EFUSE_OVLO` | `voice_efuse.OVLO` | `voice_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `voice_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 1% completes the OVLO divider |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice.VCC` | only the protected fixed 4.0-V rail powers the SA518; it can never be switched to the 5-V accessory setting |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact local protected-side capacitor |
| `POWER_GROUND` | `voice_efuse_output_cap.END_2` | `abstract:power-ground` | protected voice local return |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice_efuse_pg_top.END_1` | 68-kOhm 1% starts the protected-output power-good divider |
| `VOICE_EFUSE_PGTH` | `voice_efuse_pg_top.END_2` | `voice_efuse.PGTH` | 68/33-kOhm divider asserts only after the protected rail crosses approximately 3.67 V |
| `VOICE_EFUSE_PGTH` | `voice_efuse.PGTH` | `voice_efuse_pg_bottom.END_1` | PGTH directly measures protected output, not raw converter output |
| `POWER_GROUND` | `voice_efuse_pg_bottom.END_2` | `abstract:power-ground` | 33-kOhm 1% completes the PG divider |
| `VOICE_4V_PG_N` | `voice_efuse.PG` | `abstract:voice-power-reset-domain` | PD remains asserted until the protected 4-V rail and internal eFuse power path are valid |
| `3V3_MAIN` | `main_efuse.OUT` | `voice_pg_pullup.END_1` | voice protected-PG is referenced only to the powered diagnostic domain |
| `VOICE_4V_PG_N` | `voice_pg_pullup.END_2` | `voice_efuse.PG` | 10-kOhm draws at most about 0.33 mA when the open-drain protected PG is low |
| `VOICE_4V_PG_N` | `voice_efuse.PG` | `voice_pg_qualifier.E` | the protected-rail PG input is qualified by the same STOP-dominant enable request |
| `VOICE_4V_FAULT_QUAL_N` | `voice_pg_qualifier.C` | `abstract:power-current-thermal-fault` | open collector sinks only for EN=1 and PG=0; a normally disabled voice rail releases POWER_FAULT_N |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck.VIN` | external 5 V has a dedicated converter and cannot disturb fixed voice voltage |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor keeps accessory load steps out of the other converter loops |
| `POWER_GROUND` | `ext_buck_input_cap.END_2` | `abstract:power-ground` | accessory-buck bulk input return stays inside its own switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency accessory-converter VIN current |
| `POWER_GROUND` | `ext_buck_hf_input_cap.END_2` | `abstract:power-ground` | accessory-buck high-frequency input return is placed directly at converter ground |
| `EXT_BUCK_SW` | `ext_buck.SW` | `ext_inductor.END_1` | 4.7-uH exact first target limits ripple while preserving the 2-A transient envelope |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_efuse.IN` | the eFuse is the final series element before the externally accessible connector |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_fb_top.END_1` | 220-kOhm 1% top resistor starts the physically fixed accessory feedback divider |
| `EXT_5V_FB` | `ext_buck_fb_top.END_2` | `ext_buck.FB` | 220-kOhm over 30-kOhm sets nominal 5.000 V without a shared voice/accessory selector |
| `EXT_5V_FB` | `ext_buck.FB` | `ext_buck_fb_bottom.END_1` | 30-kOhm 1% bottom resistor completes the fixed accessory divider |
| `POWER_GROUND` | `ext_buck_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin feedback return prevents connector current from shifting the set point |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_ff_cap.END_1` | 33-pF C0G feed-forward capacitor follows the datasheet 5-V recommendation |
| `EXT_5V_FB` | `ext_buck_ff_cap.END_2` | `ext_buck.FB` | feed-forward element is physically across the accessory top divider resistor |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_output_cap0.END_1` | first physical 22-uF 25-V X7R output capacitor supports eFuse startup and post-start load steps |
| `POWER_GROUND` | `ext_buck_output_cap0.END_2` | `abstract:power-ground` | first accessory-buck output capacitor closes its local power loop |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_output_cap1.END_1` | second independent 22-uF 25-V X7R output capacitor completes the recommended 44-uF nominal bank |
| `POWER_GROUND` | `ext_buck_output_cap1.END_2` | `abstract:power-ground` | second accessory-buck output capacitor closes its local power loop |
| `3V3_MAIN` | `main_efuse.OUT` | `ext_pg_pullup.END_1` | accessory PG is referenced only to the protected powered diagnostic domain |
| `EXT_5V_PG_N` | `ext_pg_pullup.END_2` | `ext_buck.PG` | 10-kOhm draws at most about 0.33 mA when the open-drain PG is low, far below its 4-mA rating |
| `EXT_5V_PG_N` | `ext_buck.PG` | `ext_pg_qualifier.E` | the open-drain PG emitter input is qualified by the same STOP-dominant enable request; PG is pulled up only inside the powered 3V3_MAIN diagnostic domain |
| `EXT_5V_FAULT_QUAL_N` | `ext_pg_qualifier.C` | `abstract:power-current-thermal-fault` | open collector sinks only for EN=1 and PG=0; a normally disabled accessory converter releases POWER_FAULT_N |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `u214.5V_IN` | true reverse-current blocking, bounded inrush and active current limit sit between the connector and converter |
| `U214_5V_OUT_NC` | `u214.5V_OUT` | `abstract:no-connect` | the base is the only source in this profile; the cap output contact is not paralleled back into the protected rail |
| `EXT_EFUSE_FAULT_N` | `ext_efuse.FLT` | `abstract:power-current-thermal-fault` | active-low open-drain current/thermal/voltage fault joins POWER_FAULT_N |
| `EXT_5V_CURRENT_MONITOR` | `ext_efuse.ILM` | `abstract:TP_EXT_5V_ILM` | analog current evidence is accessible at a protected test point without consuming another MCU GPIO |
| `EXT_EFUSE_ILM_SET` | `ext_efuse.ILM` | `ext_rilm.END_1` | 2.21-kOhm 1% resistor sets a nominal 1.509-A current limit that is active during startup and steady operation |
| `POWER_GROUND` | `ext_rilm.END_2` | `abstract:power-ground` | short quiet return preserves the current-limit accuracy |
| `EXT_EFUSE_DVDT` | `ext_efuse.DVDT` | `ext_dvdt_cap.END_1` | 4.7-nF 10% capacitor controls the startup slew instead of relying on ITIMER |
| `POWER_GROUND` | `ext_dvdt_cap.END_2` | `abstract:power-ground` | local return completes the controlled-slew network |
| `EXT_EFUSE_ITIMER` | `ext_efuse.ITIMER` | `ext_itimer_cap.END_1` | 220-nF 10% capacitor bounds only post-start operation between ILIM and 2xILIM; it does not defer startup limiting |
| `POWER_GROUND` | `ext_itimer_cap.END_2` | `abstract:power-ground` | local return completes the post-start transient timer |
| `5V_EXT_PREPROTECT` | `ext_efuse.IN` | `ext_ovlo_top.END_1` | 169-kOhm 1% top element begins the fixed OVLO divider |
| `EXT_EFUSE_OVLO_SENSE` | `ext_ovlo_top.END_2` | `ext_efuse.OVLO` | divider sets about 5.515-V nominal input overvoltage cutoff |
| `EXT_EFUSE_OVLO_SENSE` | `ext_efuse.OVLO` | `ext_ovlo_bottom.END_1` | 47-kOhm 1% bottom element completes the fixed OVLO divider |
| `POWER_GROUND` | `ext_ovlo_bottom.END_2` | `abstract:power-ground` | fixed OVLO return has no firmware-controlled overvoltage setting |
| `5V_EXT_PREPROTECT` | `ext_efuse.IN` | `ext_input_cap.END_1` | local 2.2-uF 25-V X7R capacitor exceeds the eFuse input bypass minimum and retains voltage-rating margin |
| `POWER_GROUND` | `ext_input_cap.END_2` | `abstract:power-ground` | input bypass return stays local to the eFuse high-current path |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `ext_output_cap.END_1` | local 2.2-uF 25-V X7R capacitor provides the required close output capacitance |
| `POWER_GROUND` | `ext_output_cap.END_2` | `abstract:power-ground` | output bypass return stays local to the eFuse high-current path |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `ext_bleeder.END_1` | 1-kOhm 1% bleeder discharges the unplugged connector without creating an external backfeed sink path |
| `POWER_GROUND` | `ext_bleeder.END_2` | `abstract:power-ground` | 5-mA nominal passive discharge remains active whenever protected 5 V is present |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `nrf_power_switch.IN` | one 1.5-A protected branch serves all three simultaneously active nRF modules |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf0.VCC` | all three modules share one commanded quiet-state domain but retain independent data, CE and IRQ |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf1.VCC` | full three-radio PTX/PRX mix remains an accepted simultaneous load |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf2.VCC` | full three-radio PTX/PRX mix remains an accepted simultaneous load |
| `NRF_QOD` | `nrf_power_switch.QOD` | `nrf_power_switch.VOUT` | internal 24-Ohm discharge removes the unused radio rail; capacitance and fall time remain HIL gates |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `cc_power_switch.IN` | compatibility radio receives an independent reset-off branch |
| `3V3_CC_SWITCHED` | `cc_power_switch.VOUT` | `abstract:cc-filtered-3v3` | exact RF decoupling/matching follows the switch and remains an I6 circuit gate |
| `CC_QOD` | `cc_power_switch.QOD` | `cc_power_switch.VOUT` | internal discharge produces a measured quiet state |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_input_cap.END_1` | exact 1-uF local switch-input bypass follows the TPS22919 evaluation profile |
| `POWER_GROUND` | `sd_power_input_cap.END_2` | `abstract:power-ground` | short local input-capacitor return |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_switch.IN` | controlled-rise self-protected switch isolates card inrush and hard shorts from the shared compute rail |
| `POWER_GROUND` | `sd_power_switch.GND` | `abstract:power-ground` | short local switch return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd.VDD` | card rail exists only during a bounded storage session |
| `SD_QOD` | `sd_power_switch.QOD` | `sd_power_switch.VOUT` | direct internal 24-Ohm QOD discharges card, buffer and local bulk after a qualified flush/unmount sequence |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_power_bulk_cap.END_1` | exact 22-uF 6.3-V X5R local bulk supports card write-current transients |
| `POWER_GROUND` | `sd_power_bulk_cap.END_2` | `abstract:power-ground` | bulk return stays beside the socket and signal isolators |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_power_hf_cap.END_1` | exact 100-nF high-frequency card-rail bypass |
| `POWER_GROUND` | `sd_power_hf_cap.END_2` | `abstract:power-ground` | high-frequency return stays local |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_host_buffer.VCC` | host-to-card buffer disappears electrically with the card rail and uses Ioff against live host signals |
| `POWER_GROUND` | `sd_host_buffer.GND` | `abstract:power-ground` | short logic return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_host_buffer_bypass.END_1` | one exact local 100-nF bypass per physical buffer |
| `POWER_GROUND` | `sd_host_buffer_bypass.END_2` | `abstract:power-ground` | local triple-buffer bypass return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_miso_buffer.VCC` | return buffer powers down with the card and exposes an Ioff high-Z host output |
| `POWER_GROUND` | `sd_miso_buffer.GND` | `abstract:power-ground` | short return-buffer ground |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_miso_buffer_bypass.END_1` | separate exact 100-nF return-buffer bypass |
| `POWER_GROUND` | `sd_miso_buffer_bypass.END_2` | `abstract:power-ground` | local return-buffer bypass return |
| `POWER_GROUND` | `sd_host_sck_pulldown.END_2` | `abstract:power-ground` | 10-kOhm host-side default keeps shared SPI2 clock low across reset |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_d0_pullup.END_2` | 10-kOhm host default prevents a powered card buffer from seeing floating MOSI across S3 reset |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_d1_pullup.END_2` | 10-kOhm host default prevents the shared QSPI D1/MISO node from floating |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_cs_pullup.END_2` | 10-kOhm host default deselects the card and disables its return buffer before firmware |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `lcd_host_cs_pullup.END_2` | 10-kOhm host default keeps the display deselected during card SPI-mode admission |
| `SD_CLK_BUFFERED` | `sd_host_buffer.1Y` | `sd_sck_series.END_1` | first Ioff channel drives only the powered card branch |
| `SD_CLK_PROTECTED` | `sd_sck_series.END_2` | `sd.CLK` | exact 22-Ohm source series limits clock ringing at the removable socket |
| `SD_CLK_PROTECTED` | `sd_sck_series.END_2` | `sd_esd_a.D1_PLUS` | first low-capacitance IEC channel clamps the exposed clock contact |
| `SD_CMD_BUFFERED` | `sd_host_buffer.2Y` | `sd_cmd_series.END_1` | second Ioff channel drives CMD/MOSI only while card power is present |
| `SD_CMD_PROTECTED` | `sd_cmd_series.END_2` | `sd.CMD` | exact 22-Ohm source series limits CMD edge energy |
| `SD_CMD_PROTECTED` | `sd_cmd_series.END_2` | `sd_esd_a.D1_MINUS` | second low-capacitance IEC channel clamps the exposed CMD contact |
| `SD_CS_BUFFERED_N` | `sd_host_buffer.3Y` | `sd_cs_series.END_1` | third Ioff channel carries the reset-high card select |
| `SD_DAT3_CS_PROTECTED_N` | `sd_cs_series.END_2` | `sd.CD_DAT3` | exact 22-Ohm source series terminates the card-select branch |
| `SD_DAT3_CS_PROTECTED_N` | `sd_cs_series.END_2` | `sd_esd_a.D2_PLUS` | third IEC channel clamps the exposed DAT3/CS contact |
| `SD_DAT0_MISO_PROTECTED` | `sd.DAT0` | `sd_miso_buffer.A` | only the card's selected DAT0 return reaches the explicit tri-state buffer |
| `SD_DAT0_MISO_PROTECTED` | `sd.DAT0` | `sd_esd_a.D2_MINUS` | fourth IEC channel clamps the exposed DAT0 contact |
| `SD_MISO_BUFFERED` | `sd_miso_buffer.Y` | `sd_miso_series.END_1` | buffer output is high-Z whenever SD_CS_N is high or the card rail is absent |
| `DISPLAY_SD_SPI_D1` | `sd_miso_series.END_2` | `abstract:S3-GPIO4-shared-D1` | exact 22-Ohm source series bounds the return edge before the shared display D1 node |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_cmd_pullup.END_1` | switched-rail pull cannot back-power an off card |
| `SD_CMD_PROTECTED` | `sd_card_cmd_pullup.END_2` | `sd.CMD` | exact 10-kOhm CMD pull-up required for ESP32-S3 SD SPI mode |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat0_pullup.END_1` | switched-rail DAT0 pull-up |
| `SD_DAT0_MISO_PROTECTED` | `sd_card_dat0_pullup.END_2` | `sd.DAT0` | exact 10-kOhm DAT0 pull-up required for ESP32-S3 SD SPI mode |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat1_pullup.END_1` | unused card data pins still receive required switched-rail pulls |
| `SD_DAT1_PROTECTED` | `sd_card_dat1_pullup.END_2` | `sd.DAT1` | exact 10-kOhm DAT1 pull-up prevents an invalid card state |
| `SD_DAT1_PROTECTED` | `sd.DAT1` | `sd_esd_b.D1_PLUS` | fifth card-signal IEC channel clamps DAT1 |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat2_pullup.END_1` | unused card data pins still receive required switched-rail pulls |
| `SD_DAT2_PROTECTED` | `sd_card_dat2_pullup.END_2` | `sd.DAT2` | exact 10-kOhm DAT2 pull-up prevents an invalid card state |
| `SD_DAT2_PROTECTED` | `sd.DAT2` | `sd_esd_b.D1_MINUS` | sixth card-signal IEC channel clamps DAT2 |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat3_pullup.END_1` | switched DAT3 pull follows the SD SPI requirement without leaking into an off rail |
| `SD_DAT3_CS_PROTECTED_N` | `sd_card_dat3_pullup.END_2` | `sd.CD_DAT3` | exact 10-kOhm DAT3/CS pull-up keeps the card deselected during rail rise |
| `SD_CARD_3V3` | `sd.VDD` | `sd_esd_b.D2_PLUS` | seventh required ESD channel protects the exposed 2.6-to-3.3-V card supply contact |
| `POWER_GROUND` | `sd.VSS` | `abstract:power-ground` | short card return beside the socket |
| `SD_SHIELD_GROUND` | `sd.SHIELD` | `abstract:power-ground-multivia` | four shield tabs use a short multi-via ESD return outside the protected signal path |
| `SD_ESD_GROUND_A` | `sd_esd_a.GND_3` | `abstract:power-ground-dedicated-via` | first independent shortest-path IEC return |
| `SD_ESD_GROUND_A` | `sd_esd_a.GND_8` | `abstract:power-ground-dedicated-via` | both array ground contacts receive local vias |
| `SD_ESD_GROUND_B` | `sd_esd_b.GND_3` | `abstract:power-ground-dedicated-via` | second independent shortest-path IEC return |
| `SD_ESD_GROUND_B` | `sd_esd_b.GND_8` | `abstract:power-ground-dedicated-via` | both array ground contacts receive local vias |
| `SD_ESD_A_NC6` | `sd_esd_a.NC_6` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC7` | `sd_esd_a.NC_7` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC9` | `sd_esd_a.NC_9` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC10` | `sd_esd_a.NC_10` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC6` | `sd_esd_b.NC_6` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC7` | `sd_esd_b.NC_7` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC9` | `sd_esd_b.NC_9` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC10` | `sd_esd_b.NC_10` | `abstract:no-connect` | manufacturer no-connect remains open |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `codec_power_switch.IN` | codec branch is independently reset-off and cannot back-power the common I2C/I2S buses |
| `3V3_CODEC_SWITCHED` | `codec_power_switch.VOUT` | `abstract:qualified-codec-3v3-digital` | digital and analog filtering split only after the exact protected load switch |
| `3V3_CODEC_SWITCHED` | `codec_power_switch.VOUT` | `abstract:qualified-codec-3v3-analog` | analog filtering and return-current geometry remain a schematic/HIL gate |
| `CODEC_QOD` | `codec_power_switch.QOD` | `codec_power_switch.VOUT` | powered-off codec rail is actively discharged before interface isolation is relaxed |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `receiver_power_switch.IN` | receive-only radio has its own reset-off branch for desense control |
| `3V3_RECEIVER_SWITCHED` | `receiver_power_switch.VOUT` | `receiver.VDD` | local filtering and RST sequencing follow the exact switch |
| `RECEIVER_QOD` | `receiver_power_switch.QOD` | `receiver_power_switch.VOUT` | powered-off receiver rail is discharged and verified quiet |
| `NRF_SWITCH_NC` | `nrf_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `CC_SWITCH_NC` | `cc_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `SD_SWITCH_NC` | `sd_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `CODEC_SWITCH_NC` | `codec_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `RECEIVER_SWITCH_NC` | `receiver_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `PD_LOCAL_I2C_SDA` | `pd_config_eeprom.SDA` | `abstract:pd-eeprom-factory-sda-pad` | blank-device programming and recovery remain possible without booted product firmware |
| `PD_LOCAL_I2C_SCL` | `pd_config_eeprom.SCL` | `abstract:pd-eeprom-factory-scl-pad` | blank-device programming and recovery remain possible without booted product firmware |
| `PD_EEPROM_WP` | `pd_config_eeprom.WP` | `abstract:pd-eeprom-factory-wp-pad` | fixture can verify protected and writable states; normal reset state remains protected |
| `U214_I2C_SDA_OUT` | `u214_i2c_iso.SDAOUT` | `u214.SDA` | hot-swap isolation and stuck-low recovery keep the external branch off the controller-side domain |
| `U214_I2C_SCL_OUT` | `u214_i2c_iso.SCLOUT` | `u214.SCL` | hot-swap isolation and stuck-low recovery keep the external branch off the controller-side domain |
| `U214_I2C_ISO_EN` | `abstract:protected-accessory-power-good` | `u214_i2c_iso.EN` | off until protected accessory power is stable |
| `U214_I2C_READY` | `u214_i2c_iso.READY` | `slow_io.P16` | read-only status; no safety function depends on firmware polling |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_io.VCC` | dedicated ordinary-control expander shares the protected SYS-I2C logic domain |
| `POWER_GROUND` | `ui_matrix_io.GND` | `abstract:power-ground` | short local digital return |
| `SYS_I2C_SDA` | `s3.GPIO1` | `ui_matrix_io.SDA` | bounded ordinary-control transactions share the internal bus but no encoder or PTT edge depends on them |
| `SYS_I2C_SCL` | `s3.GPIO2` | `ui_matrix_io.SCL` | candidate 400-kHz service; physical bus timing remains HIL |
| `SYS_INT_N` | `ui_matrix_io.INT_N` | `abstract:SYS_INT_N_WIRED_LOW` | open-drain interrupt asserts on any column change while every row is held low in idle |
| `UI_MATRIX_ADDR_A0_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A0` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_MATRIX_ADDR_A1_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A1` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_MATRIX_ADDR_A2_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A2` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_ROW0_N` | `ui_matrix_io.P0` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW1_N` | `ui_matrix_io.P1` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW2_N` | `ui_matrix_io.P2` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW3_N` | `ui_matrix_io.P3` | `abstract:UI_MATRIX_ROW3_ENCODER_PUSH` | 1-kOhm reset pull-down makes the encoder-push row low before firmware |
| `UI_COL0` | `ui_matrix_io.P4` | `abstract:UI_MATRIX_COL0_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_COL1` | `ui_matrix_io.P5` | `abstract:UI_MATRIX_COL1_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_COL2` | `ui_matrix_io.P6` | `abstract:UI_MATRIX_COL2_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_MATRIX_P7_RESERVE` | `ui_matrix_io.P7` | `abstract:reserved-local-control-expansion-pad` | single local growth contact is reserved until all physical-control wishes close |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_io_bypass.END_1` | 100-nF local expander bypass |
| `POWER_GROUND` | `ui_matrix_io_bypass.END_2` | `abstract:power-ground` | short local bypass return |
| `UI_ROW0_N` | `ui_matrix_io.P0` | `ui_matrix_row0_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row0_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW1_N` | `ui_matrix_io.P1` | `ui_matrix_row1_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row1_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW2_N` | `ui_matrix_io.P2` | `ui_matrix_row2_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row2_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW3_N` | `ui_matrix_io.P3` | `ui_matrix_row3_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row3_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col0_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL0` | `ui_matrix_col0_pullup.END_2` | `ui_matrix_io.P4` | 10-kOhm column pull-up |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col1_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL1` | `ui_matrix_col1_pullup.END_2` | `ui_matrix_io.P5` | 10-kOhm column pull-up |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col2_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL2` | `ui_matrix_col2_pullup.END_2` | `ui_matrix_io.P6` | 10-kOhm column pull-up |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_up.K` | one exact diode isolates D-pad UP from other rows |
| `UI_UP_ROW_SIDE` | `ui_matrix_diode_up.A` | `abstract:UI_SWITCH_UP_ROW_CONTACT` | ordinary normally-open D-pad UP mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_UP_COL_CONTACT` | `ui_matrix_io.P4` | D-pad UP occupies row 0, column 0 |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_down.K` | one exact diode isolates D-pad DOWN from other rows |
| `UI_DOWN_ROW_SIDE` | `ui_matrix_diode_down.A` | `abstract:UI_SWITCH_DOWN_ROW_CONTACT` | ordinary normally-open D-pad DOWN mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_DOWN_COL_CONTACT` | `ui_matrix_io.P5` | D-pad DOWN occupies row 0, column 1 |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_left.K` | one exact diode isolates D-pad LEFT from other rows |
| `UI_LEFT_ROW_SIDE` | `ui_matrix_diode_left.A` | `abstract:UI_SWITCH_LEFT_ROW_CONTACT` | ordinary normally-open D-pad LEFT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_LEFT_COL_CONTACT` | `ui_matrix_io.P6` | D-pad LEFT occupies row 0, column 2 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_right.K` | one exact diode isolates D-pad RIGHT from other rows |
| `UI_RIGHT_ROW_SIDE` | `ui_matrix_diode_right.A` | `abstract:UI_SWITCH_RIGHT_ROW_CONTACT` | ordinary normally-open D-pad RIGHT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_RIGHT_COL_CONTACT` | `ui_matrix_io.P4` | D-pad RIGHT occupies row 1, column 0 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_ok.K` | one exact diode isolates D-pad OK from other rows |
| `UI_OK_ROW_SIDE` | `ui_matrix_diode_ok.A` | `abstract:UI_SWITCH_OK_ROW_CONTACT` | ordinary normally-open D-pad OK mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_OK_COL_CONTACT` | `ui_matrix_io.P5` | D-pad OK occupies row 1, column 1 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_back.K` | one exact diode isolates BACK from other rows |
| `UI_BACK_ROW_SIDE` | `ui_matrix_diode_back.A` | `abstract:UI_SWITCH_BACK_ROW_CONTACT` | ordinary normally-open BACK mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_BACK_COL_CONTACT` | `ui_matrix_io.P6` | BACK occupies row 1, column 2 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_opt.K` | one exact diode isolates OPT from other rows |
| `UI_OPT_ROW_SIDE` | `ui_matrix_diode_opt.A` | `abstract:UI_SWITCH_OPT_ROW_CONTACT` | ordinary normally-open OPT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_OPT_COL_CONTACT` | `ui_matrix_io.P4` | OPT occupies row 2, column 0 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_f1.K` | one exact diode isolates F1 from other rows |
| `UI_F1_ROW_SIDE` | `ui_matrix_diode_f1.A` | `abstract:UI_SWITCH_F1_ROW_CONTACT` | ordinary normally-open F1 mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_F1_COL_CONTACT` | `ui_matrix_io.P5` | F1 occupies row 2, column 1 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_f2.K` | one exact diode isolates F2 from other rows |
| `UI_F2_ROW_SIDE` | `ui_matrix_diode_f2.A` | `abstract:UI_SWITCH_F2_ROW_CONTACT` | ordinary normally-open F2 mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_F2_COL_CONTACT` | `ui_matrix_io.P6` | F2 occupies row 2, column 2 |
| `UI_ROW3_N` | `abstract:UI_MATRIX_ROW3_ENCODER_PUSH` | `ui_matrix_diode_encoder.K` | one exact diode isolates encoder push from other rows |
| `UI_ENCODER_PUSH_ROW` | `ui_matrix_diode_encoder.A` | `encoder.SW1` | integrated push switch is the tenth ordinary matrix control |
| `POWER_GROUND` | `encoder.C` | `abstract:power-ground` | quadrature common is a short local digital return |
| `UI_COL0` | `encoder.SW2` | `abstract:UI_MATRIX_COL0_WITH_SWITCHES_AND_DIODES` | encoder push occupies row 3, column 0 |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `encoder_a_pullup.END_1` | external phase pull-up keeps the direct PCNT input deterministic |
| `ENCODER_A` | `encoder_a_pullup.END_2` | `encoder.A` | exact 3.32-kOhm pull-up targets approximately 1 mA closed-contact current at 3.3 V; chatter and EMI remain HIL |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `encoder_b_pullup.END_1` | external phase pull-up keeps the direct PCNT input deterministic |
| `ENCODER_B` | `encoder_b_pullup.END_2` | `encoder.B` | exact 3.32-kOhm pull-up targets approximately 1 mA closed-contact current at 3.3 V; chatter and EMI remain HIL |
| `SYS_I2C_SCL` | `display_connector.PIN_1` | `display.TP_I2C_SCL` | logical contact 1 maps one-to-one; physical tail orientation remains specimen HIL |
| `SYS_I2C_SDA` | `display_connector.PIN_2` | `display.TP_I2C_SDA` | one existing exact 2.2-kOhm host pull-up pair serves the complete bus; no duplicate panel pull-ups |
| `LCD_TOUCH_INT_RAW` | `display_connector.PIN_3` | `display.TP_INT` | panel contact is kept separate from SYS_INT_N until specimen polarity/type is handled by the population option |
| `LCD_TOUCH_INT_RAW` | `display_connector.PIN_3` | `touch_irq_buffer.A` | first target is non-inverting open drain for active-low TP_INT; pin-compatible inverter is populated if specimen HIL proves active-high |
| `SYS_INT_N` | `touch_irq_buffer.Y` | `abstract:SYS_INT_N_WIRED_LOW` | open-drain output joins the existing shared interrupt without consuming another GPIO |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `touch_irq_buffer.VCC` | Ioff-capable buffer is supplied from protected main logic |
| `POWER_GROUND` | `touch_irq_buffer.GND` | `abstract:power-ground` | short local digital return |
| `TOUCH_IRQ_BUFFER_NC` | `touch_irq_buffer.NC` | `abstract:no-connect` | SC70 pin 1 is intentionally unconnected |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `touch_irq_buffer_bypass.END_1` | 100-nF local buffer bypass |
| `POWER_GROUND` | `touch_irq_buffer_bypass.END_2` | `abstract:power-ground` | short local bypass return |
| `TOUCH_RST_N` | `slow_io.P07` | `display_connector.PIN_4` | TP_RESXP is held low by a physical pull-down and released only after display power is stable |
| `TOUCH_RST_N` | `display_connector.PIN_4` | `display.TP_RESET` | official ST77922 timing requires a reset pulse of at least 10 us and at least 100 ms after release before touch operation |
| `TOUCH_RST_N` | `display_connector.PIN_4` | `touch_reset_pulldown.END_1` | separate physical reset-default resistor remains effective while the slow-I/O output is high-impedance |
| `POWER_GROUND` | `touch_reset_pulldown.END_2` | `abstract:power-ground` | 10-kOhm exact pull-down makes touch reset assert by default |
| `POWER_GROUND` | `display_connector.PIN_5` | `display.GND_5` | first panel return contact |
| `POWER_GROUND` | `display_connector.PIN_5` | `abstract:power-ground` | short local return at the connector |
| `LCD_VDDI_3V3` | `abstract:3V3_MAIN` | `display_connector.PIN_6` | protected common main rail avoids back-power through live QSPI/I2C when a separate display switch would trip |
| `LCD_VDDI_3V3` | `display_connector.PIN_6` | `display.VDDI` | ST77922 VDDI accepts the protected 3.3-V rail |
| `LCD_VDD_3V3` | `abstract:3V3_MAIN` | `display_connector.PIN_7` | VDD and VDDI may be applied in either order; both are one protected source here |
| `LCD_VDD_3V3` | `display_connector.PIN_7` | `display.VDD` | ST77922 VDD accepts the protected 3.3-V rail |
| `LCD_LOGIC_3V3` | `abstract:3V3_MAIN` | `display_logic_bulk_cap.END_1` | exact 10-uF local bulk target at the connector |
| `POWER_GROUND` | `display_logic_bulk_cap.END_2` | `abstract:power-ground` | display logic bulk return stays local |
| `LCD_LOGIC_3V3` | `abstract:3V3_MAIN` | `display_logic_hf_cap.END_1` | exact 100-nF high-frequency bypass at the connector |
| `POWER_GROUND` | `display_logic_hf_cap.END_2` | `abstract:power-ground` | display logic high-frequency return stays local |
| `LCD_TE_NC` | `display_connector.PIN_8` | `display.TE` | tearing-effect output is not required by the bounded dirty-region renderer |
| `LCD_TE_NC` | `display_connector.PIN_8` | `abstract:no-connect` | board-side contact deliberately open; S3 GPIO43 remains service UART TX |
| `LCD_CS_N` | `display_connector.PIN_9` | `display.QSPI_CS` | dedicated panel chip select; CS-high high-Z remains shared-bus HIL |
| `DISPLAY_SD_SPI_D1` | `display_connector.PIN_10` | `display.QSPI_D1` | direct QSPI data lane; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `DISPLAY_SD_SPI_SCK` | `display_connector.PIN_11` | `display.QSPI_CLK` | direct QSPI clock; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `LCD_RD_NC` | `display_connector.PIN_12` | `display.RD_UNUSED` | RD is unused in the selected QSPI strap |
| `LCD_RD_NC` | `display_connector.PIN_12` | `abstract:no-connect` | board-side contact deliberately open |
| `DISPLAY_SD_SPI_D0` | `display_connector.PIN_13` | `display.QSPI_D0` | direct QSPI data lane; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `LCD_NC_14` | `display_connector.PIN_14` | `display.NC_14` | manufacturer-declared no-connect remains open |
| `LCD_NC_14` | `display_connector.PIN_14` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_RST_N` | `slow_io.P06` | `display_connector.PIN_15` | RESX is held low by a physical pull-down and released only after the protected rail is stable |
| `LCD_RST_N` | `display_connector.PIN_15` | `display.RESET` | official ST77922 timing requires at least 10-us reset pulse and at least 120 ms before Sleep Out after release |
| `LCD_RST_N` | `display_connector.PIN_15` | `display_reset_pulldown.END_1` | separate physical reset-default resistor remains effective while the slow-I/O output is high-impedance |
| `POWER_GROUND` | `display_reset_pulldown.END_2` | `abstract:power-ground` | 10-kOhm exact pull-down makes display reset assert by default |
| `POWER_GROUND` | `display_connector.PIN_16` | `display.GND_16` | second panel return contact |
| `POWER_GROUND` | `display_connector.PIN_16` | `abstract:power-ground` | short local return at the connector |
| `LCD_QSPI_D2` | `display_connector.PIN_17` | `display.QSPI_D2` | direct fourth-lane QSPI contact |
| `LCD_QSPI_D3` | `display_connector.PIN_18` | `display.QSPI_D3` | direct fourth-lane QSPI contact |
| `LCD_DB2_LOW` | `display_connector.PIN_19` | `display.DB2_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB3_LOW` | `display_connector.PIN_20` | `display.DB3_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB4_LOW` | `display_connector.PIN_21` | `display.DB4_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB5_LOW` | `display_connector.PIN_22` | `display.DB5_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB6_LOW` | `display_connector.PIN_23` | `display.DB6_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB7_LOW` | `display_connector.PIN_24` | `display.DB7_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB2_LOW` | `display_connector.PIN_19` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB3_LOW` | `display_connector.PIN_20` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB4_LOW` | `display_connector.PIN_21` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB5_LOW` | `display_connector.PIN_22` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB6_LOW` | `display_connector.PIN_23` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB7_LOW` | `display_connector.PIN_24` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_NC_25` | `display_connector.PIN_25` | `display.NC_25` | manufacturer-declared no-connect remains open |
| `LCD_NC_26` | `display_connector.PIN_26` | `display.NC_26` | manufacturer-declared no-connect remains open |
| `LCD_NC_27` | `display_connector.PIN_27` | `display.NC_27` | manufacturer-declared no-connect remains open |
| `LCD_NC_28` | `display_connector.PIN_28` | `display.NC_28` | manufacturer-declared no-connect remains open |
| `LCD_NC_29` | `display_connector.PIN_29` | `display.NC_29` | manufacturer-declared no-connect remains open |
| `LCD_NC_30` | `display_connector.PIN_30` | `display.NC_30` | manufacturer-declared no-connect remains open |
| `LCD_NC_31` | `display_connector.PIN_31` | `display.NC_31` | manufacturer-declared no-connect remains open |
| `LCD_NC_32` | `display_connector.PIN_32` | `display.NC_32` | manufacturer-declared no-connect remains open |
| `LCD_NC_25` | `display_connector.PIN_25` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_26` | `display_connector.PIN_26` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_27` | `display_connector.PIN_27` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_28` | `display_connector.PIN_28` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_29` | `display_connector.PIN_29` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_30` | `display_connector.PIN_30` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_31` | `display_connector.PIN_31` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_32` | `display_connector.PIN_32` | `abstract:no-connect` | board-side contact deliberately open |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_efuse.IN` | only the LEDA branch receives independent latch-off protection; panel logic remains on common protected power to prevent interface back-power |
| `LCD_BACKLIGHT_EFUSE_EN` | `abstract:3V3_MAIN` | `backlight_efuse.EN` | hardware-enabled whenever main power exists; firmware cannot auto-retry a latched LED fault |
| `POWER_GROUND` | `backlight_efuse.GND` | `abstract:power-ground` | short local WSON return |
| `POWER_GROUND` | `backlight_efuse.POWERPAD` | `abstract:power-ground` | PowerPAD is externally tied to ground as required |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_efuse_input_cap.END_1` | exact 100-nF local input bypass required by TI |
| `POWER_GROUND` | `backlight_efuse_input_cap.END_2` | `abstract:power-ground` | local high-frequency input return |
| `LCD_BACKLIGHT_ILIM` | `backlight_efuse.ILIM` | `backlight_efuse_ilim.END_1` | 133-kOhm exact resistor sets about 200-mA nominal latch threshold |
| `POWER_GROUND` | `backlight_efuse_ilim.END_2` | `abstract:power-ground` | TI table gives approximately 174-to-234-mA system threshold including 1% resistor corners |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_fault_pullup.END_1` | exact 10-kOhm pull-up makes the open-drain fault observable |
| `LCD_BACKLIGHT_FAULT_N` | `backlight_fault_pullup.END_2` | `backlight_efuse.FAULT_N` | fixture-visible only; no scarce S3 GPIO is consumed |
| `LCD_BACKLIGHT_FAULT_N` | `backlight_efuse.FAULT_N` | `abstract:TP_LCD_BACKLIGHT_FAULT_N` | latched-fault diagnostic test point |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `display_connector.PIN_33` | reverse-blocking latch-off source protects the 120-mA reference backlight branch |
| `LCD_LEDA_PROTECTED` | `display_connector.PIN_33` | `display.LEDA` | exact panel anode contact |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `backlight_efuse_output_bulk.END_1` | exact 10-uF local output bulk supports PWM current edges |
| `POWER_GROUND` | `backlight_efuse_output_bulk.END_2` | `abstract:power-ground` | backlight bulk return stays beside the connector and switch |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `backlight_efuse_output_hf.END_1` | exact 100-nF high-frequency output bypass |
| `POWER_GROUND` | `backlight_efuse_output_hf.END_2` | `abstract:power-ground` | backlight high-frequency return stays local |
| `LCD_LEDK` | `display_connector.PIN_34` | `display.LEDK_1` | first cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_35` | `display.LEDK_2` | second cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_36` | `display.LEDK_3` | third cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_34` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK` | `display_connector.PIN_35` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK` | `display_connector.PIN_36` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK_LIMITED` | `backlight_series_resistor.END_2` | `backlight_mosfet.D` | 0.66-W anti-surge resistor has wide margin over the approximately 0.144-W 120-mA reference load |
| `POWER_GROUND` | `backlight_mosfet.S` | `abstract:power-ground` | short low-side PWM return |
| `LCD_BACKLIGHT_GATE` | `backlight_gate_series.END_2` | `backlight_mosfet.G` | exact 100-Ohm gate resistor limits edge current and ringing |
| `LCD_BACKLIGHT_GATE` | `backlight_mosfet.G` | `backlight_gate_pulldown.END_1` | gate is forced low before S3 configures GPIO40 |
| `POWER_GROUND` | `backlight_gate_pulldown.END_2` | `abstract:power-ground` | exact 10-kOhm reset-off default |
| `POWER_GROUND` | `display_connector.PIN_37` | `display.GND_37` | third panel return contact |
| `POWER_GROUND` | `display_connector.PIN_37` | `abstract:power-ground` | short local return at the connector |
| `LCD_IM0_LOW` | `display_connector.PIN_38` | `display.IM0` | fixed QSPI interface strap |
| `LCD_IM0_LOW` | `display_connector.PIN_38` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_IM1_HIGH` | `abstract:3V3_MAIN` | `display_connector.PIN_39` | fixed QSPI interface strap |
| `LCD_IM1_HIGH` | `display_connector.PIN_39` | `display.IM1` | fixed QSPI interface strap |
| `LCD_IM2_LOW` | `display_connector.PIN_40` | `display.IM2` | fixed QSPI interface strap |
| `LCD_IM2_LOW` | `display_connector.PIN_40` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `CODEC_PWR_EN` | `slow_io.P10` | `codec_power_switch.ON` | external off-safe pull; ES8311 has no hardware enable/reset pin and CE is only the I2C address strap |
| `CODEC_PVDD` | `abstract:qualified-codec-3v3-digital` | `codec.PVDD` | switched quiet rail with local decoupling; no back-power through I2C/I2S when off |
| `CODEC_DVDD` | `abstract:qualified-codec-3v3-digital` | `codec.DVDD` | switched quiet rail with local decoupling and manufacturer-valid sequencing |
| `CODEC_AVDD` | `abstract:qualified-codec-3v3-analog` | `codec.AVDD` | filtered switched analog rail; return-current and RF-noise layout remain gates |
| `CODEC_DGND` | `codec.DGND` | `abstract:codec-digital-ground` | joined to audio ground at the reviewed single-point/plane boundary |
| `CODEC_AGND` | `codec.AGND` | `abstract:codec-audio-ground` | quiet analog return |
| `CODEC_EPAD_AGND` | `codec.EPAD` | `abstract:codec-audio-ground` | manufacturer user guide requires the exposed thermal pad on audio ground |
| `CODEC_DACVREF` | `abstract:codec-dacvref-decoupling` | `codec.DACVREF` | exact capacitor/value/layout follow current product brief and HIL |
| `CODEC_ADCVREF` | `abstract:codec-adcvref-decoupling` | `codec.ADCVREF` | exact capacitor/value/layout follow current product brief and HIL |
| `CODEC_VMID` | `abstract:codec-vmid-decoupling` | `codec.VMID` | quiet local reference; not a general-purpose rail |
| `CODEC_I2C_ADDR_0X19` | `abstract:codec-address-high-3v3` | `codec.CE` | 10 kOhm reference strap selects documented 7-bit address 0x19; complete bus address scan remains HIL |
| `CODEC_MCLK_NC` | `codec.MCLK` | `abstract:no-connect` | current four-wire I2S contract selects BCLK/SCLK as internal master-clock source; no hidden S3 GPIO |
| `RX_AUDIO_L` | `receiver.LOUT_DFS` | `abstract:si4732-10k-left-mono-sum` | 10-kOhm-class summing branch; exact source level, capacitor and impedance remain schematic/HIL gates |
| `RX_AUDIO_R` | `receiver.ROUT_DOUT` | `abstract:si4732-10k-right-mono-sum` | 10-kOhm-class summing branch; exact source level, capacitor and impedance remain schematic/HIL gates |
| `RX_SI4732_MONO` | `abstract:si4732-passive-mono-sum-output` | `audio_rx_mux.B1` | logic-low/default receive source; component values and low-band response remain schematic/HIL gates |
| `RX_SA518_AFOUT` | `voice.AFOUT` | `audio_rx_mux.B2` | voice receive source; muted and isolated before voice rail transitions |
| `RX_AUDIO_SOURCE_SEL` | `slow_io.P27` | `audio_rx_mux.S` | ordinary non-TX source selection; external pull-down selects Si4732 B1 at reset |
| `AUDIO_RX_MUX_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_rx_mux.VCC` | selector remains available independently of codec power |
| `AUDIO_RX_MUX_GND` | `audio_rx_mux.GND` | `abstract:audio-ground` | quiet analog return |
| `RX_AUDIO_SELECTED` | `audio_rx_mux.A_COM` | `abstract:rx-audio-bypass-and-capture-node` | one selected RX source feeds independent bypass and high-impedance capture branches |
| `SPK_BYPASS_P` | `abstract:rx-audio-bypass-and-capture-node` | `audio_speaker_selector.S1B` | logic-low/default path; qualified AC coupling and PAM input network remain schematic gates |
| `SPK_BYPASS_M` | `abstract:matched-bypass-ac-reference` | `audio_speaker_selector.S2B` | matched AC reference for PAM differential input in ordinary bypass mode |
| `CODEC_CAPTURE_TAP` | `abstract:rx-audio-bypass-and-capture-node` | `abstract:high-z-ac-coupled-capture-network` | 100-kOhm-class source-loading target; exact bias, capacitor and RF filter remain schematic/HIL gates |
| `CODEC_CAPTURE_BUFFER_IN` | `abstract:high-z-ac-coupled-capture-network` | `audio_capture_buffer.IN_PLUS` | biased inside TLV9061 valid common-mode range; no source back-power when codec branch is off |
| `CODEC_CAPTURE_BUFFER_FB` | `audio_capture_buffer.OUT` | `audio_capture_buffer.IN_MINUS` | unity-gain baseline; qualified gain may change only with repeated analog review |
| `CODEC_CAPTURE_BUFFER_VCC` | `abstract:qualified-codec-3v3-analog` | `audio_capture_buffer.V_PLUS` | switched with codec analog domain; input series network prevents powered-off loading/back-power |
| `CODEC_CAPTURE_BUFFER_GND` | `audio_capture_buffer.V_MINUS` | `abstract:codec-audio-ground` | quiet analog return |
| `CODEC_CAPTURE_BUFFER_OUT` | `audio_capture_buffer.OUT` | `abstract:qualified-es8311-mic-range-differential-input-network` | buffer output is AC-coupled, biased and attenuated into a manufacturer-valid ES8311 microphone-range interface |
| `CODEC_ADC_IN_P` | `abstract:qualified-es8311-mic-range-differential-input-network` | `codec.MIC1P` | exact gain, common mode, AC coupling and anti-RF values remain schematic/HIL gates |
| `CODEC_ADC_IN_N` | `abstract:qualified-es8311-mic-range-differential-input-network` | `codec.MIC1N` | matched reference and conditioning remain an exact schematic/HIL gate |
| `CODEC_DAC_OUT_P` | `codec.OUTP` | `audio_speaker_selector.S1A` | full differential DAC positive leg; never grounded or silently discarded |
| `CODEC_DAC_OUT_N` | `codec.OUTN` | `audio_speaker_selector.S2A` | full differential DAC negative leg |
| `PAM_AUDIO_IN_P` | `audio_speaker_selector.D1` | `speaker_amp.IN_PLUS` | paired selector poles always change together under one safe control |
| `PAM_AUDIO_IN_M` | `audio_speaker_selector.D2` | `speaker_amp.IN_MINUS` | paired selector poles always change together under one safe control |
| `AUDIO_SPK_SEL_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_speaker_selector.VDD` | selector remains powered while codec rail is off so analog bypass survives |
| `AUDIO_SPK_SEL_GND` | `audio_speaker_selector.GND` | `abstract:audio-ground` | quiet analog return |
| `PAM_VDD` | `abstract:qualified-speaker-amp-supply` | `speaker_amp.VDD` | exact rail, decoupling, current and EMI remain schematic/HIL gates |
| `PAM_GND` | `speaker_amp.GND` | `abstract:audio-ground` | short quiet return; class-D output currents stay out of codec input return |
| `PAM_SD` | `abstract:qualified-speaker-enable-default-on` | `speaker_amp.SD` | ordinary bypass remains available after reset; startup pop and fault behavior remain HIL gates |
| `PAM_NC` | `speaker_amp.NC` | `abstract:no-connect` | physical MSOP-8 pin 2 is no-connect |
| `SPEAKER_P` | `speaker_amp.VO_PLUS` | `abstract:speaker-positive` | BTL/class-D output; never tie to ground |
| `SPEAKER_M` | `speaker_amp.VO_MINUS` | `abstract:speaker-negative` | BTL/class-D output; never tie to ground |
| `CODEC_TX_DAC_TAP` | `codec.OUTP` | `abstract:codec-dac-to-sa518-35-45db-attenuator` | separate high-impedance AC-coupled low-pass branch; exact attenuation is set by measured SA518 deviation |
| `VOICE_CODEC_INJECT` | `abstract:codec-dac-to-sa518-35-45db-attenuator` | `audio_tx_selector.NO` | codec injection is the non-default selected input |
| `VOICE_ELECTRET_DEFAULT` | `abstract:electret-microphone-bias-and-ac-coupling` | `audio_tx_selector.NC` | logic-low/default path preserves ordinary microphone operation |
| `VOICE_MIC_IN` | `audio_tx_selector.COM` | `voice.MIC_IN` | audio selection cannot assert PTT; input level and deviation remain measured gates |
| `AUDIO_TX_SEL_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_tx_selector.VCC` | selector remains powered independently of codec rail |
| `AUDIO_TX_SEL_GND` | `audio_tx_selector.GND` | `abstract:audio-ground` | quiet analog return |
| `AUDIO_SPK_CODEC_REQ` | `slow_io.P11` | `audio_safe_gate.1A` | external pull-down requests ordinary analog bypass while expander is input or high-Z |
| `AUDIO_TX_CODEC_REQ` | `slow_io.P12` | `audio_safe_gate.2A` | external pull-down requests electret default while expander is input or high-Z |
| `AUDIO_SPK_SEL_SAFE` | `audio_safe_gate.1Y` | `audio_speaker_selector.SEL1` | low selects bypass S1B; external pull-down holds default if gate rail is absent |
| `AUDIO_SPK_SEL_SAFE` | `audio_safe_gate.1Y` | `audio_speaker_selector.SEL2` | both differential poles share the same reset-safe control |
| `AUDIO_TX_SEL_SAFE` | `audio_safe_gate.2Y` | `audio_tx_selector.IN` | low selects normally-closed electret path; external pull-down holds default if gate rail is absent |
| `AUDIO_SAFE_GATE_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_safe_gate.VCC` | gate and selectors share a sequenced always-available rail |
| `AUDIO_SAFE_GATE_GND` | `audio_safe_gate.GND` | `abstract:audio-ground` | quiet logic return |
| `VOICE_DOMAIN_REQ` | `slow_io.P13` | `safe_gate_b.2A` | request only; RUN_PERMIT and a 10-kOhm output pull-down make the downstream rail enable STOP-dominant |
| `VOICE_PD_N` | `abstract:voice-power-reset-domain` | `voice.PD` | off-safe sequencer keeps the exact module in power-down until the qualified 4 V rail is valid |
| `VOICE_HL` | `slow_io.P14` | `voice.HL` | external conservative-power pull |
| `VOICE_UPDATE` | `voice.UPDATE` | `abstract:voice-update-fixture` | fixture-only; no runtime drive until the rev-1.1 direction/description conflict is resolved by specimen proof |
| `RX_DOMAIN_EN` | `slow_io.P15` | `receiver_power_switch.ON` | off-safe pull; exact switch removes receiver power while the following reset/isolation circuit prevents I2C back-power |
| `RX_DOMAIN_POWER_VALID` | `receiver_power_switch.VOUT` | `abstract:receiver-power-reset-isolation` | reset remains asserted until switched power and I2C isolation are valid |
| `RX_RST_N` | `abstract:receiver-power-reset-isolation` | `receiver.RST` | reset remains asserted until the qualified receiver rail and I2C isolation are valid |
| `RX_STATUS_N` | `receiver.GPO2_INTB` | `slow_io.P24` | exact interrupt source; bounded latency and pulse width remain HIL gates |
| `RX_SENB_I2C` | `abstract:i2c-mode-strap` | `receiver.SENB` | fixed reset strap selects the reviewed two-wire control mode |
| `RX_RCLK` | `abstract:qualified-32k-clock` | `receiver.RCLK` | clock source and startup remain exact electrical gates |
| `RX_FMI_RF` | `receiver.FMI` | `abstract:RX-FM-SW-SMA-front-end` | dedicated external-SMA whip path; matching/ESD stays close to FMI |
| `RX_AMI_RF` | `receiver.AMI` | `abstract:RX-AM-LW-loop-pod` | dedicated short loop/pod path; generic long coax is not qualified |
| `EXT_5V_REQ` | `slow_io.P17` | `safe_gate_b.4A` | request only; RUN_PERMIT gates the reverse-safe/current-limited accessory power stage selected in I3/I7 |
| `SD_PWR_EN` | `slow_io.P20` | `sd_power_switch.ON` | ordinary session request only; exact external fail-low and switch protection remain effective across firmware reset |
| `SD_PWR_EN` | `sd_power_switch.ON` | `sd_on_pulldown.END_1` | separate exact 10-kOhm reset-off default supplements the switch smart pull-down |
| `POWER_GROUND` | `sd_on_pulldown.END_2` | `abstract:power-ground` | card, buffers and pull-ups remain off until an explicit storage session |
| `POWER_GROUND` | `sd.DETECT_B` | `abstract:power-ground` | normally-open detect pair closes to ground only with a fully inserted card |
| `SD_CARD_DETECT_RAW_N` | `sd.DETECT_A` | `sd_esd_b.D2_MINUS` | eighth available low-capacitance IEC channel protects the mechanical detect conductor |
| `SD_CARD_DETECT_RAW_N` | `sd.DETECT_A` | `sd_detect_series.END_1` | exact 1-kOhm series resistor limits residual surge and contact current into the slow expander |
| `SD_CARD_DETECT_N` | `sd_detect_series.END_2` | `slow_io.P21` | read-only active-low presence remains available while card power is off |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_detect_pullup.END_1` | presence sensing does not require or back-power SD_CARD_3V3 |
| `SD_CARD_DETECT_N` | `sd_detect_pullup.END_2` | `slow_io.P21` | exact 10-kOhm pull-up reports absent/open wiring as high |
| `SD_CARD_DETECT_N` | `slow_io.P21` | `sd_detect_cap.END_1` | exact 100-nF hardware filter suppresses the shortest contact chatter before software debounce |
| `POWER_GROUND` | `sd_detect_cap.END_2` | `abstract:power-ground` | local detect-filter return |
| `STOP_LATCH_SENSE` | `safe_latch.Q` | `slow_io.P22` | diagnostic mirror only; non-programmable hard-stop dominance never depends on the expander |
| `S3_RF_TX_EVIDENCE_N` | `evidence_cmp_a.OUT1` | `slow_io.P23` | direct read-only mirror of the exact S3 evidence comparator |
| `POWER_FAULT_N` | `abstract:power-current-thermal-fault` | `slow_io.P25` | hardware protection acts independently; this is diagnostic evidence |
| `ACCESSORY_PRESENT_N` | `abstract:accessory-present` | `slow_io.P26` | read-only, protected and debounced |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_supervisor.VDD` | always-on source and hold-up are selected and budgeted in I3 |
| `AON_SAFE_SENSE` | `abstract:AON_SAFE_3V3` | `safe_supervisor.SENSE` | factory G33 threshold supervises the actual safety rail |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_por_pullup.END_1` | one exact 10-kOhm resistor is the sole external pull-up on the supervisor's open-drain POR output |
| `POR_N` | `safe_por_pullup.END_2` | `safe_supervisor.RESET_N` | POR_N is pulled only to AON_SAFE_3V3; a missing AON rail cannot produce a main-enable high |
| `POR_N` | `safe_supervisor.RESET_N` | `safe_por_or.1A` | power-good clear input; STOP remains dominant through the second OR input |
| `STOP_LOOP_SENSE` | `abstract:NC-stop-loop-10k-pullup-10nF` | `safe_conditioner.1A` | healthy closed contact is low; press, disconnect or open wire is high |
| `STOP_LOOP_SENSE` | `abstract:NC-stop-loop-10k-pullup-10nF` | `safe_por_or.1B` | high forces CLR_N inactive so preset and clear cannot be asserted together |
| `STOP_ASSERT_N` | `safe_conditioner.1Y` | `safe_latch.PRE_N` | active-low asynchronous preset; software and clocks are outside the path |
| `REARM_RAW` | `abstract:NO-rearm-loop-47k-pullup-100nF` | `safe_conditioner.2A` | fresh press pulls raw input low and produces one or more harmless rising edges at the Schmitt output |
| `REARM_CLK` | `safe_conditioner.2Y` | `safe_latch.CLK` | only a fresh physical edge can clock fixed D=0 |
| `STOP_DOMINANT_CLR_N` | `safe_por_or.1Y` | `safe_latch.CLR_N` | CLR_N = POR_N OR STOP_LOOP_SENSE |
| `SAFE_D_LOW` | `abstract:safety-ground-via-10k` | `safe_latch.D` | fixed logic low; no MCU, expander or connector endpoint |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.1A` | one non-programmable permit fans out through an Ioff buffer |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.2A` | one non-programmable permit fans out through an Ioff buffer |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.3A` | one non-programmable permit fans out through an Ioff buffer |
| `S3_RUN_SAFE` | `safe_reset_buffer.1Y` | `s3.EN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds CHIP_PU low |
| `C5_RUN_SAFE` | `safe_reset_buffer.2Y` | `c5.EN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds CHIP_PU low |
| `RP_RUN_SAFE` | `safe_reset_buffer.3Y` | `rp.RUN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds RUN low |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.1B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.2B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.3B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.4B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.1B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.2B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.3B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.4B` | STOP-dominant active-high gate permit |
| `NRF0_CE_SAFE` | `safe_gate_a.1Y` | `nrf0.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF1_CE_SAFE` | `safe_gate_a.2Y` | `nrf1.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF2_CE_SAFE` | `safe_gate_a.3Y` | `nrf2.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF_GROUP_PWR_EN_SAFE` | `safe_gate_a.4Y` | `nrf_power_switch.ON` | 10-kOhm pull-down; STOP and AON loss disable the exact protected load switch |
| `CC_PWR_EN_SAFE` | `safe_gate_b.1Y` | `cc_power_switch.ON` | 10-kOhm pull-down; STOP and AON loss disable the exact protected load switch |
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_buck.EN` | STOP and AON loss disable the independent fixed 4-V converter |
| `VOICE_DOMAIN_EN_SAFE` | `voice_buck.EN` | `voice_en_pulldown.END_1` | one exact 10-kOhm pull-down defines voice off even if the safety-gate output is high-impedance |
| `POWER_GROUND` | `voice_en_pulldown.END_2` | `abstract:power-ground` | external fail-low default is independent of converter internal bias |
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_pg_base_res.END_1` | the qualifier consumes the same STOP-dominant voice enable evidence |
| `VOICE_PG_QUAL_BASE` | `voice_pg_base_res.END_2` | `voice_pg_qualifier.B` | exact 68-kOhm 1% base resistor limits drive while preserving the reviewed forced-beta margin |
| `IR_TX_CARRIER_SAFE` | `safe_gate_b.3Y` | `abstract:fail-safe-IR-LED-driver` | carrier waveform is physically blocked whenever RUN_PERMIT is low |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_buck.EN` | STOP and AON loss disable the dedicated 5-V converter |
| `EXT_5V_EN_SAFE` | `ext_buck.EN` | `ext_en_pulldown.END_1` | one exact 10-kOhm pull-down defines accessory off for both converter and eFuse if the safety-gate output is high-impedance |
| `POWER_GROUND` | `ext_en_pulldown.END_2` | `abstract:power-ground` | external fail-low default is independent of the converter's internal 2-MOhm pull-down |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_pg_base_res.END_1` | the qualifier consumes the same STOP-dominant accessory enable evidence |
| `EXT_PG_QUAL_BASE` | `ext_pg_base_res.END_2` | `ext_pg_qualifier.B` | exact 68-kOhm 1% base resistor limits drive while preserving the reviewed forced-beta margin |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_efuse.EN_UVLO` | the same STOP-dominant request also disables the connector-side true-reverse-blocking eFuse |
| `TX_KILL` | `safe_latch.Q` | `safe_ptt_or.1B` | active-high kill forces active-low PTT high/RX |
| `VOICE_PTT_SAFE_N` | `safe_ptt_or.1Y` | `voice.PTT` | 10-kOhm module-side pull-up keeps RX when the AON gate is unpowered |
| `STOP_LED_DRIVE` | `safe_latch.Q` | `abstract:stop-led-series-2k2` | non-programmable visible latched-stop state |
| `STOP_LED_A` | `abstract:stop-led-series-2k2` | `stop_led.A` | 2.2-kOhm first-target current limit |
| `STOP_LED_K` | `stop_led.K` | `abstract:safety-ground` | indicator stays outside UI and firmware |
| `S3_RF_SAMPLE` | `abstract:S3-qualified-RF-tap` | `det_s3.RFIN` | tap/attenuation is selected and measured in I6 |
| `C5_RF_SAMPLE` | `abstract:C5-qualified-RF-tap` | `det_c5.RFIN` | tap covers the qualified 2.4/5-GHz path; I6 sets attenuation |
| `NRF0_RF_SAMPLE` | `abstract:NRF0-qualified-RF-tap` | `det_nrf0.RFIN` | one source-specific tap; never shared with nRF1/2 |
| `NRF1_RF_SAMPLE` | `abstract:NRF1-qualified-RF-tap` | `det_nrf1.RFIN` | one source-specific tap; never shared with nRF0/2 |
| `NRF2_RF_SAMPLE` | `abstract:NRF2-qualified-RF-tap` | `det_nrf2.RFIN` | one source-specific tap; never shared with nRF0/1 |
| `CC_RF_SAMPLE` | `abstract:CC-qualified-RF-tap` | `det_cc.RFIN` | sub-GHz tap and coupling capacitor are selected in I6 |
| `VOICE_RF_SAMPLE` | `abstract:VOICE-qualified-RF-tap` | `det_voice.RFIN` | VHF/UHF tap and coupling capacitor are selected in I6 |
| `CC_DETECT_ENABLE` | `abstract:AON_SAFE_3V3` | `det_cc.SHDN` | evidence detector remains enabled independently of the CC application rail |
| `VOICE_DETECT_ENABLE` | `abstract:AON_SAFE_3V3` | `det_voice.SHDN` | evidence detector remains enabled independently of the voice application rail |
| `IR_OPTICAL_SAMPLE` | `det_ir.ANODE` | `abstract:shielded-ir-evidence-front-end` | physical optical pickup rather than drive-current inference; exact bias/front end is I6 |
| `S3_DETECT_V` | `det_s3.VOUT` | `evidence_cmp_a.IN1_N` | RF above the qualified threshold makes active-low comparator output assert |
| `C5_DETECT_V` | `det_c5.VOUT` | `evidence_cmp_a.IN2_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF0_DETECT_V` | `det_nrf0.VOUT` | `evidence_cmp_a.IN3_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF1_DETECT_V` | `det_nrf1.VOUT` | `evidence_cmp_a.IN4_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF2_DETECT_V` | `det_nrf2.VOUT` | `evidence_cmp_b.IN1_N` | RF above the qualified threshold makes active-low comparator output assert |
| `CC_DETECT_V` | `det_cc.VOUT` | `evidence_cmp_b.IN2_N` | RF above the qualified threshold makes active-low comparator output assert |
| `VOICE_DETECT_V` | `det_voice.VOUT` | `evidence_cmp_b.IN3_N` | RF above the qualified threshold makes active-low comparator output assert |
| `IR_DETECT_V` | `abstract:shielded-ir-evidence-front-end` | `evidence_cmp_b.IN4_N` | optical energy above the qualified threshold makes active-low comparator output assert |
| `EV_THRESH_0` | `abstract:qualified-evidence-threshold-0` | `evidence_cmp_a.IN1_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_1` | `abstract:qualified-evidence-threshold-1` | `evidence_cmp_a.IN2_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_2` | `abstract:qualified-evidence-threshold-2` | `evidence_cmp_a.IN3_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_3` | `abstract:qualified-evidence-threshold-3` | `evidence_cmp_a.IN4_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_4` | `abstract:qualified-evidence-threshold-4` | `evidence_cmp_b.IN1_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_5` | `abstract:qualified-evidence-threshold-5` | `evidence_cmp_b.IN2_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_6` | `abstract:qualified-evidence-threshold-6` | `evidence_cmp_b.IN3_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_7` | `abstract:qualified-evidence-threshold-7` | `evidence_cmp_b.IN4_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_N0_S3` | `evidence_cmp_a.OUT1` | `evidence_mask.P0` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N1_C5` | `evidence_cmp_a.OUT2` | `evidence_mask.P1` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N2_NRF0` | `evidence_cmp_a.OUT3` | `evidence_mask.P2` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N3_NRF1` | `evidence_cmp_a.OUT4` | `evidence_mask.P3` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N4_NRF2` | `evidence_cmp_b.OUT1` | `evidence_mask.P4` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N5_CC` | `evidence_cmp_b.OUT2` | `evidence_mask.P5` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N6_VOICE` | `evidence_cmp_b.OUT3` | `evidence_mask.P6` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N7_IR` | `evidence_cmp_b.OUT4` | `evidence_mask.P7` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N0_S3` | `evidence_cmp_a.OUT1` | `evidence_or_0.K1` | diode-isolated hardware aggregate |
| `EV_N1_C5` | `evidence_cmp_a.OUT2` | `evidence_or_0.K2` | diode-isolated hardware aggregate |
| `EV_N2_NRF0` | `evidence_cmp_a.OUT3` | `evidence_or_1.K1` | diode-isolated hardware aggregate |
| `EV_N3_NRF1` | `evidence_cmp_a.OUT4` | `evidence_or_1.K2` | diode-isolated hardware aggregate |
| `EV_N4_NRF2` | `evidence_cmp_b.OUT1` | `evidence_or_2.K1` | diode-isolated hardware aggregate |
| `EV_N5_CC` | `evidence_cmp_b.OUT2` | `evidence_or_2.K2` | diode-isolated hardware aggregate |
| `EV_N6_VOICE` | `evidence_cmp_b.OUT3` | `evidence_or_3.K1` | diode-isolated hardware aggregate |
| `EV_N7_IR` | `evidence_cmp_b.OUT4` | `evidence_or_3.K2` | diode-isolated hardware aggregate |
| `RP_ANY_TX_N` | `evidence_or_0.A_COMMON` | `evidence_or_1.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `RP_ANY_TX_N` | `evidence_or_1.A_COMMON` | `evidence_or_2.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `RP_ANY_TX_N` | `evidence_or_2.A_COMMON` | `evidence_or_3.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `ANY_TX_LED_A` | `abstract:AON_SAFE_3V3-via-2k2` | `any_tx_led.A` | red physical indicator current is sunk by the asserting comparator through one Schottky diode |
| `EVIDENCE_MASK_INT_N_TP` | `evidence_mask.INT_N` | `abstract:TP_EVIDENCE_MASK_INT_N` | test point only; no safety claim depends on expander interrupt behavior |
| `EVIDENCE_ADDR_A0_LOW` | `abstract:safety-ground` | `evidence_mask.A0` | fixed 7-bit address 0x38 |
| `EVIDENCE_ADDR_A1_LOW` | `abstract:safety-ground` | `evidence_mask.A1` | fixed 7-bit address 0x38 |
| `EVIDENCE_ADDR_A2_LOW` | `abstract:safety-ground` | `evidence_mask.A2` | fixed 7-bit address 0x38 |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20`, `GPIO43`, `GPIO44` — native USB Serial/JTAG, permanent default UART0 RF-test/diagnostic route and physical EN/BOOT.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO11`, `GPIO12`, `GPIO13`, `GPIO14` — native USB Serial/JTAG, permanent UART0, physical CHIP_PU/BOOT and normal-boot/log strap; 1-bit SDIO leaves USB contacts independent.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.
- `pd_controller`: `I2Ct_SDA`, `I2Ct_SCL`, `I2Ct_IRQ` — S3 shared SYS_I2C0 host control plus shared wired-low IRQ; same bus is exposed on protected service pads for controller status/recovery.
- `pd_config_eeprom`: `SDA`, `SCL`, `WP` — first image uses a preprogrammed loose EEPROM or a current-limited raw-VBUS fixture. The fixture observes TPS ReadyForPatch on I2Ct and verifies I2Cc high-Z before direct SDA/SCL/WP programming; it never drives LDO_3V3 externally and does not depend on S3.
- `pack_gauge`: `ALRT`, `SCL_OD`, `SDA_DQ`, `PFAIL` — direct protected I2C/NVM and hold/fault pads with fixture ground and qualified stack-sense supply; protected image checksum and OvrdEn readback are mandatory before energized cell installation.
- `pack_admission`: `PA1_NRST`, `PA17`, `PA18_A7`, `PA19_SWDIO`, `PA20_A6_SWCLK`, `VDD`, `VSS` — permanent NRST/SWD/UART plus isolated fixture VDD/VSS; fixture or admitted system rail powers flash programming because MAX17320 AOLDO is not sized for it.
- `voice`: `UPDATE`, `UART_TX`, `UART_RX`, `PD` — permanent fixture breakout for vendor update/recovery plus UART and hardware power-down; UPDATE drive remains inhibited until exact rev-1.1 direction/timing proof.

### Non-MCU contact accounting

| Instance | Used | Reserved | Free |
|---|---:|---:|---:|
| `slow_io` | 18 | 0 | 6 |
| `ui_matrix_io` | 7 | 1 | 0 |

### Interface non-interference contracts

| Resource | Owner | Clients | Sharing | Deadline / bound | Proof gate |
|---|---|---|---|---|---|
| `NRF0_SPI` | `rp` | `nrf0` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM0 plus dedicated DMA/IRQ stress HIL |
| `NRF1_SPI` | `rp` | `nrf1` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM1 plus dedicated DMA/IRQ stress HIL |
| `NRF2_SPI` | `rp` | `nrf2` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM2 plus dedicated DMA/IRQ stress HIL |
| `CC_SPI` | `rp` | `cc` | dedicated | GDO/FIFO service completes without waiting for any nRF or U214 transfer | PIO0 SM3 plus dedicated DMA/IRQ stress HIL |
| `U214_SPI` | `rp` | `u214` | dedicated | LoRa BUSY/IRQ transaction never waits for display or compatibility-radio bus ownership | PIO1 SM0 plus dedicated DMA/IRQ stress HIL |
| `U214_UART` | `rp` | `u214` | dedicated | GNSS receive has continuous hardware UART buffering independent of SPI activity | UART1 DMA/ring overflow stress HIL |
| `U214_I2C` | `rp` | `u214`, `u214_i2c_iso` | dedicated | external stuck-low or hot-plug cannot stall internal UI/audio/receiver I2C | TCA4307 stuck-bus and hot-plug fault-injection HIL |
| `DISPLAY_SD_SPI` | `s3` | `display`, `sd` | scheduled; separate CS and per-device modes/clocks; display non-preemptible SPI2 occupancy <=1 ms with byte quantum derived from measured datasheet-valid payload rate; QSPI only while SD CS is high; bounded SD command/data chunks; critical UI priority | critical/menu first visible response <=100 ms and qualified storage >=4.0 MB/s while all radios capture; no radio FIFO or IPC deadline is placed here | HMX035CTFT-001 direct-QSPI dirty/tiled display, CS-high high-Z/contention proof, 1.5 MB/s record and 250 ms card-stall HIL |
| `S3_RP_IPC` | `s3` | `rp` | dedicated | 20 MHz SPI raw 2.5 MB/s and qualified framed payload >=1.5 MB/s; no display/storage or C5 controller ownership | SPI3 load, alert-to-read <=250 us and aggregate-radio stress HIL |
| `S3_C5_IPC` | `s3` | `c5` | dedicated | 1-bit SDIO at 20 MHz raw 2.5 MB/s with qualified framed payload >=1.5 MB/s, admitted occupancy <=70% and control RTT <=2 ms; no microSD, RP or display controller ownership | single-slot 1-bit SDMMC/SDIO throughput, control-priority, reset recovery and simultaneous Wi-Fi/802.15.4 load HIL; 4-bit fallback only if this gate fails |
| `S3_INTERNAL_I2C` | `s3` | `slow_io`, `ui_matrix_io`, `display touch`, `codec`, `receiver`, `pd_controller`, `pack_admission` | scheduled; bounded transactions; both expanders, PD, pack and touch interrupts only wake the service loop; UI initialization writes low output latches before P0..P3 become outputs, then holds all rows low in idle, scans one low row against three high rows, and restores idle; direct PCNT captures encoder phases independently | ordinary UI/control first visible response <=100 ms; PD/pack/fault status is read after shared IRQ, and no radio FIFO, encoder-edge or PTT deadline is placed here | complete physical address scan including candidate UI address 0x3F, ES8311 address/readback and power-off no-backfeed, touch IRQ polarity/reset, TCA9534A idle-row interrupt behavior, PD and pack target-interface recovery, wired-low IRQ source identification, shortest-pulse, 4x3 matrix and fault-latency HIL |
| `S3_ENCODER_PCNT` | `s3` | `encoder` | dedicated; PCNT0 owns GPIO39=A and GPIO47=B as dedicated inputs; the I2C matrix carries only encoder push and never phase edges | no lost or invented detents while display dirty-region, storage and the active signal group run at their qualified worst case | phase polarity, valid Gray transitions, full-detent semantics, contact chatter, fastest manual rotation, temperature, EMI and concurrent-load HIL |
| `PD_LOCAL_I2C` | `pd_controller` | `pd_config_eeprom`, `nvdc_charger` | scheduled; TPS25751D owns the local bus; EEPROM address 0x50 and exact charger address are collision-checked; factory access is permitted only while the product controller is held inactive | boot image completes before high-voltage negotiation or charge enable; charger faults propagate without depending on display/storage/radio buses | blank/valid/corrupt dual-region EEPROM boots, charger-IRQ latency and signed-update rollback HIL |
| `PACK_LOCAL_I2C` | `pack_admission` | `pack_gauge` | dedicated | gauge identity, protected-NVM checksum, cell/temperature/protection state and diagnostic-pulse samples complete locally before any FET-hold release; S3 availability is irrelevant | bit-banged I2C electrical timing, both MAX17320 address paths, blank/wrong NVM, stuck bus, watchdog/reset and fixture-handover HIL |
| `S3_UNIT_PORT` | `s3` | `abstract:M5 Unit` | dedicated | one selected I2C/UART/GPIO Unit profile cannot be blocked by internal or U214 I2C | profile-switch and external-fault HIL |
| `S3_I2S` | `s3` | `codec` | dedicated | continuous DMA audio without storage/display service gaps | ES8311 BCLK-derived master-clock and simultaneous full-duplex display, SD, C5 and radio event stress HIL |

### Controller GPIO-window selections

| Instance | Controllers | Selected window | Device constraint / reason |
|---|---|---|---|
| `rp` | `PIO0_SM0_RF_SPI`, `PIO0_SM1_RF_SPI`, `PIO0_SM2_RF_SPI`, `PIO0_SM3_RF_SPI` | `GPIO16..GPIO47` | RP2354B PIO0 is fixed to the shared GPIO-base 16 window, so every PIO0 data pin must remain in GPIO16..GPIO47 |
| `rp` | `PIO1_SM0_EXT_SPI` | `GPIO16..GPIO47` | RP2354B PIO1 uses GPIO-base 16 for the U214 data bus |

### Controller/DMA capacity accounting

| Capacity | Instance | Claims | Reserve / available | Basis |
|---|---|---|---:|---|
| `RP_PIO_STATE_MACHINES` | `rp` | nrf0=1, nrf1=1, nrf2=1, cc=1, u214=1 | 7 / 12 | RP2350 provides three PIO blocks with four state machines each; PIO0 consumes four and PIO1 consumes one |
| `RP_DMA_CHANNELS` | `rp` | nrf0 full-duplex PIO SPI=2, nrf1 full-duplex PIO SPI=2, nrf2 full-duplex PIO SPI=2, cc full-duplex PIO SPI=2, u214 full-duplex PIO SPI=2, S3-RP full-duplex SPI1=2, U214 GNSS continuous UART1 RX=1 | 3 / 16 | worst-case persistent allocation leaves three channels for qualified transient/service use; slow UART TX and I2C do not require permanent DMA ownership |
| `S3_GDMA_TX_CHANNELS` | `s3` | display/microSD scheduled SPI2=1, S3-RP SPI3=1, audio I2S0=1 | 2 / 5 | ESP32-S3 has five independent GDMA transmit channels; SD/MMC is not in this GDMA peripheral list |
| `S3_GDMA_RX_CHANNELS` | `s3` | display/microSD scheduled SPI2=1, S3-RP SPI3=1, audio I2S0=1 | 2 / 5 | ESP32-S3 has five independent GDMA receive channels; C5 uses the separate SD/MMC host path |

### Exact fixed-mux contracts

| Contract | Instance/controller | Exact contacts | Datasheet/device proof |
|---|---|---|---|
| `S3_NATIVE_USB` | `s3.USB_SERIAL_JTAG` | `GPIO19`, `GPIO20` | ESP32-S3 native USB D-/D+ fixed contacts on the exact WROOM-1U module |
| `S3_UART0_SERVICE` | `s3.UART0` | `GPIO43`, `GPIO44` | ESP32-S3 default U0TXD/U0RXD contacts are GPIO43/GPIO44 and remain permanently routed for RF-test and diagnostics |
| `C5_FIXED_SDIO` | `c5.SDIO_SLAVE` | `GPIO7`, `GPIO8`, `GPIO9`, `GPIO10` | ESP32-C5 1-bit SDIO slave uses fixed DAT1/IRQ, DAT0, CLK and CMD contacts; GPIO13/14 remain independent native USB |
| `C5_NATIVE_USB` | `c5.USB_SERIAL_JTAG` | `GPIO13`, `GPIO14` | ESP32-C5 native USB D-/D+ fixed contacts are restored by the 1-bit SDIO selection |
| `RP_SPI1_IPC` | `rp.SPI1_IPC` | `GPIO24`, `GPIO25`, `GPIO26`, `GPIO27` | RP2354B bank-0 mux group is SPI1 RX/CSn/SCK/TX |
| `RP_UART0_VOICE` | `rp.UART0` | `GPIO16`, `GPIO17` | RP2354B bank-0 mux pair is UART0 TX/RX |
| `RP_UART1_GNSS` | `rp.UART1` | `GPIO40`, `GPIO41` | RP2354B bank-0 mux pair is UART1 TX/RX |
| `RP_I2C0_U214` | `rp.I2C0_EXT` | `GPIO28`, `GPIO29` | RP2354B bank-0 mux pair is I2C0 SDA/SCL |
| `PACK_SYSTEM_I2C` | `pack_admission.I2C_TARGET` | `PA0`, `PA11` | DGS20 exposes I2C0 SDA on PA0 pin 4 and alternate SCL on PA11 pin 11, preserving PA1/NRST pin 5 |
| `PACK_UART0_SERVICE` | `pack_admission.UART0` | `PA17`, `PA18_A7` | DGS20 exposes UART0 TX/RX on PA17 pin 13 and PA18 pin 14 independently of SWD and reset |

### Open qualification gaps

- `u214_i2c_iso` uses `TCA4307DGKR` as `reference_only`, not an accepted production choice.
- `nrf0` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `voice` lifecycle: `current_product`.
- `receiver` lifecycle: `manufacturer_documented`.
- `slow_io` uses `TCA6424ARGJR` as `reference_only`, not an accepted production choice.
- `encoder` uses `Alps Alpine EC11E18244AU` as `verified_first_target_mechanical_fit_hil_open`, not an accepted production choice.
- `encoder` lifecycle: `active_standard`.
- `touch_irq_buffer` uses `SN74LVC1G07DCKR` as `verified_first_target_touch_polarity_hil_open`, not an accepted production choice.
- `display` lifecycle: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`.
- `display_connector` uses `Hirose FH12-40S-0.5SH(55)` as `verified_first_fit_candidate`, not an accepted production choice.
- `display_connector` lifecycle: `active; exact HMX035CTFT-001 tail thickness, exposed-contact side, stiffener and insertion fit remain specimen HIL`.
- `sd_power_input_cap` lifecycle: `active_production`.
- `codec` lifecycle: `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open`.
- `audio_rx_mux` uses `Texas Instruments SN74LVC1G3157DBVR` as `verified_reference`, not an accepted production choice.
- `audio_capture_buffer` uses `Texas Instruments TLV9061IDBVR` as `reference_only`, not an accepted production choice.
- `audio_speaker_selector` uses `Texas Instruments TMUX1136DGSR` as `reference_only`, not an accepted production choice.
- `audio_tx_selector` uses `Texas Instruments TS5A63157DCKR` as `reference_only`, not an accepted production choice.
- `audio_safe_gate` uses `Texas Instruments SN74LVC2G08DCUR` as `reference_only`, not an accepted production choice.
- `speaker_amp` uses `Diodes Incorporated PAM8302AASCR` as `verified_reference`, not an accepted production choice.
- `product_usb_vpwr_cap` lifecycle: `active_production`.
- `pack_gauge` lifecycle: `recommended_for_new_designs`.
- `pack_holder` uses `Keystone Electronics 1048P` as `verified_mechanical_reference`, not an accepted production choice.
- `pack_cell0` uses `XTAR 18650 4000mAh` as `selected_qualification_target`, not an accepted production choice.
- `pack_cell0` lifecycle: `current_catalog`.
- `pack_cell1` uses `XTAR 18650 4000mAh` as `selected_qualification_target`, not an accepted production choice.
- `pack_cell1` lifecycle: `current_catalog`.
- `pack_diag_timer` lifecycle: `active_production`.
- `pack_diag_lockout_cap` lifecycle: `active_production`.
- `safe_conditioner` lifecycle: `production`.
- `safe_por_or` lifecycle: `production`.
- `safe_ptt_or` lifecycle: `production`.
- `det_s3` lifecycle: `production`.
- `det_c5` lifecycle: `production`.
- `det_nrf0` lifecycle: `production`.
- `det_nrf1` lifecycle: `production`.
- `det_nrf2` lifecycle: `production`.
- `det_cc` lifecycle: `production`.
- `det_voice` lifecycle: `production`.
- RP2354B A4 exact lot identity, power/clock/land pattern and prototype assembly remain implementation gates; the verified QFN80 contact map is not a BOM freeze
- E01-ML01S is a geometry/interface reference, not an accepted three-module RF/power/antenna production choice; nRF24 family lifecycle remains not-recommended-for-new-designs
- CC1101 matching, oscillator, antenna path and regional proof are not represented by the bare-IC contact ledger
- TCA6424ARGJR and TCA4307DGKR are real-contact planning references; voltage domains, pulls, address, reset, shortest pulses and exact endpoint MPNs remain electrical/HIL gates
- HMX035CTFT-001 is the exact assembly marking disclosed by the QDtech reference schematic and is instantiated as a paper candidate, not a production-qualified orderable part; DEC-0084 closes exact paper power/reset/backlight and the first connector candidate, while exact drawing/FPC mechanics, lifecycle, real-tail mate and specimen HIL remain open
- DEC-0086 consumes the former free S3 GPIO47 together with GPIO39 for direct PCNT0 encoder phases, so S3 and RP retain no free GPIO, C5 retains one, and the 24-line slow plane has no reserve. New direct endpoints require an explicit remap and repeated review; exact ordinary/PTT/STOP/RE-ARM switch mechanics, touch polarity and control HIL remain open
- C5 1-bit SDIO has exclusive ownership of the S3 SD/MMC host and leaves C5 native USB GPIO13/14 independent. S3 and C5 each retain both native USB and permanent default UART service; 1-bit framed throughput, control priority and reset recovery remain HIL gates, with 4-bit plus explicit service isolation only as fallback
- display and microSD are the only scheduled high-rate pair on one SPI2 controller; DEC-0085 closes the exact isolated microSD paper endpoint with card-side Ioff buffers, CS-gated MISO, switched mandatory pulls, complete contact ESD and always-readable detect, but >=4.0 MB/s storage plus <=100 ms visible UI under card stalls remains a mandatory HIL gate
- PIO instruction memory, DMA arbitration latency and SRAM-bank contention remain executable firmware/HIL gates even though the state-machine/channel capacity arithmetic closes with explicit reserve
- DEC-0045 prohibits cross-group simultaneous signal operation but requires all three SG-N24 radios concurrently active in every independent PTX/PRX mix; DEC-0047 selects a qualified internal envelope; N24H-0001 L0 DIV-DIV is pre-HIL only and T1 TARGET must prove exact channel/power/sensitivity points
- SG-N24 3PTX is a real accepted load case, so the exact module choice and packet-rail design must prove simultaneous TX peak/average current, droop, thermal, coupling and STOP at the qualified power profile; a former RX-only hunt budget is insufficient
- DEC-0046 consumes RP GPIO15/GPIO23 and C5 GPIO4 for group-level power gates; exact load-switch/isolator MPNs, discharge, no-back-power sequencing and quiet-state EMI HIL remain open, leaving no free direct RP GPIO
- DEC-0054 instantiates ES8311, SN74LVC1G3157DBVR, TLV9061IDBVR, TMUX1136DGSR, TS5A63157DCKR, SN74LVC2G08DCUR and PAM8302AASCR as the prototype audio topology and assigns GPIO6 AUDIO_ARM; exact passive values, powered-off loading, codec power, common-mode/gain, pop/click, RF immunity and HIL remain open before schematic/BOM freeze
- DEC-0063 instantiates TPS25751DREFR, BQ25798RQMR, CAT24C512WI-GT3 and TVS2200DRVR as the sink-only 30-W USB-PD frontend; DEC-0066 adds MAX17320G20+T and MSPM0C1104SDGS20R as the fail-closed 2S manager pair; DEC-0067 disables in-device deep-cell recovery and instantiates the exact switching path. DEC-0068 adds independent fixed TPS629203/TPS564252 AON/3.3/4.0/5.0-V converters, exact Sunlord inductors and five TPS22919 quiet-state switches; DEC-0069 corrects the connector eFuse to latch-off TPS259470LRPWR; DEC-0070 adds two exact MMBT3904-7-F PG qualifiers; DEC-0071 adds eight exact eFuse passives, an immediately active 1.509-A limit, controlled startup and a bounded post-start 2-A transient; DEC-0072 adds 24 exact converter energy/configuration/feedback passives and fixed tolerance-screened outputs; DEC-0073 originally adds nine exact converter EN/PG/fault resistors and a direct hardware AON enable strap; DEC-0080 amends this to ten physical positions and exact SYS-to-AON, AON-PG/MR, SENSE/CT/POR and main-EN wiring without a programmable sequencer; DEC-0081 adds independent TPS25961DRVR AON cutoff plus two TPS25974LRPWR latch-off protected-PG circuit breakers, exact thresholds, rise/timer networks and single-fault paper containment after every internal buck; DEC-0074 establishes the 10-Ohm pre-admission function, <=50-ms hardware cutoff and corrected PA25/PA26 frontends; DEC-0075 adds the exact BQ25798 750-kHz/2.2-uH energy, TS/ILIM, reset and special-pin profile; DEC-0076 adds the exact TPS25751/CAT24 support circuit, hardware SafeMode, separate raw-VBUS startup path and complete local/host bus pulls; DEC-0077 adds exact polarized Keystone 1048P contacts and three physical NTC roles; DEC-0078 corrects the TPUL WQFN contact map, adds a >=350-ms second-channel hardware refractory lockout and splits the 10-Ohm load across two exact 20-Ohm/2-W branches; DEC-0079 selects two XTAR 18650 4000mAh protected button-top cells as the exact first qualification target and freezes a 2-A charge ceiling. Exact-cell droop thresholds, certification-document/specimen fit, continuity/thermal/hot-copper/source-handover and full injected-fault HIL remain open in I3. DEC-0083 closes the first I4 paper endpoint with exact DX07S016JA1R1500, TPD4S201RUKR, protected USB2/CC routes, exact 22-Ohm S3 terminations, reserved DNP tuning footprints and recalculated 220-pF CC shunts. DEC-0084 closes the second I4 paper endpoint with exact first display ZIF candidate, protected-main logic decoupling, reset-low defaults and a latch-protected PWM backlight. DEC-0085 closes the third I4 paper endpoint with exact DM3AT-SF-PEJM5, switched TPS22919 rail, Ioff card-side isolation, CS-gated DAT0 return, mandatory switched pulls, complete contact/detect ESD and safe shared-bus sequencing; connector placement/mate, USB/display/storage signal integrity and destructive/thermal HIL remain explicit
- HMX035CTFT-001 exact contacts and its DEC-0084 power/reset/backlight/first-mate paper circuit plus DM3AT-SF-PEJM5 and its DEC-0085 isolated storage paper circuit are instantiated, but display/storage production qualification, physical integration and electrical HIL remain open; the I2 hard-stop/evidence active circuit is paper-reviewed while detector taps/thresholds are I6; exact IR frontends and antenna placement remain open; SA518/Si4732 contact maps are instantiated, while SA518 UPDATE electrical direction/timing and both modules' surrounding power/audio/RF circuits remain specimen/electrical/HIL gates before target-architecture acceptance

## Граница проведённого ревью

Validator доказывает существование реально выведенных compute contacts,
полный used/reserved/free accounting, straps, fixed mux, service paths,
PIO/DMA capacity, independent radio/IPC resources и exact paper-level
AON hard-STOP/evidence circuit. Remaining peripheral MPN, branch power,
signal/power integrity, RF taps/layout and HIL are later gates; этот atlas
не разрешает KiCad и не является frozen BOM.
