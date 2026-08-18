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
  USBC["MPN TBD<br/>product USB-C receptacle: S3 USB2 data and sink-only power"]
  PD_VBUS_TVS["Texas Instruments TVS2200DRVR<br/>22-V flat-clamp VBUS surge protection"]
  PD_CONTROLLER["Texas Instruments TPS25751DREFR<br/>sink-only USB-PD policy and protected high-voltage path"]
  PD_CONFIG_EEPROM["onsemi CAT24C512WI-GT3<br/>dedicated PD patch/configuration EEPROM"]
  NVDC_CHARGER["Texas Instruments BQ25798RQMR<br/>2S-configured buck-boost charger and NVDC system power path"]
  CELL0["MPN TBD<br/>individually replaceable qualified 18650 cell #0"]
  PACK_FUSE0["Littelfuse 0451005.MRL<br/>slot-0 independent 5-A fast fuse"]
  PACK_NTC0["TDK B57332V5103F360<br/>cell-0 temperature sensor"]
  CELL1["MPN TBD<br/>individually replaceable qualified 18650 cell #1"]
  PACK_FUSE1["Littelfuse 0451005.MRL<br/>slot-1 independent 5-A fast fuse"]
  PACK_NTC1["TDK B57332V5103F360<br/>cell-1 temperature sensor"]
  PACK_GAUGE["Analog Devices MAX17320G20+T<br/>2S high-side protection, gauging, temperature and balancing"]
  PACK_SHUNT["Vishay WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACK_POWER_FET["Texas Instruments CSD87313DMST<br/>fully-switching common-drain CHG/DIS power pair"]
  PACK_HOLD["Diodes Incorporated 2N7002DW-7-F<br/>reset-default ALRT hold and explicit release"]
  PACK_SUPPLY_OR["onsemi BAV70LT1G<br/>AOLDO/fixture source isolation"]
  PACK_SYSTEM_DIODE["Diodes Incorporated BAT54-7-F<br/>admitted-system source isolation and priority"]
  PACK_ADMISSION["Texas Instruments MSPM0C1104SDGS20R<br/>fail-closed pair admission, watchdog and service bridge"]
  PACK_DIAG_TIMER["Texas Instruments TPUL2G223BQBR<br/>non-retriggerable hardware diagnostic-pulse limiter"]
  PACK_DIAG_TIMER_RES["Yageo RC0402FR-07169KL<br/>169-kOhm 1% diagnostic-pulse timing resistor"]
  PACK_DIAG_TIMER_CAP["Murata GRM31C5C1H224JE02L<br/>220-nF 50-V C0G diagnostic-pulse timing capacitor"]
  PACK_DIAG_TIMER_BYPASS["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R one-shot bypass capacitor"]
  PACK_DIAG_TRIGGER_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-trigger fail-low resistor"]
  PACK_DIAG_GATE_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% diagnostic-gate fail-low resistor"]
  PACK_DIAG_SWITCH["Diodes Incorporated DMN2056U-7<br/>20-V low-gate-drive diagnostic-load MOSFET"]
  PACK_DIAG_RES["Vishay CRCW251210R0JNEGIF<br/>10-Ohm 1-W pulse-proof diagnostic-load resistor"]
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
  AON_OUTPUT_CAP["Murata GRM31CR71A226KE15L<br/>22-uF 10-V X7R AON output capacitor"]
  AON_PG_PULLUP["Yageo RC0402FR-0747KL<br/>47-kOhm 1% AON power-good pull-up resistor"]
  MAIN_BUCK["Texas Instruments TPS564252DRLR<br/>fixed 3.3-V 4-A main converter"]
  MAIN_INDUCTOR["Sunlord MWSA0503S-3R3MT<br/>3.3-uH main-rail power inductor"]
  MAIN_INPUT_CAP["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main-converter bulk input capacitor"]
  MAIN_HF_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R main-converter HF input capacitor"]
  MAIN_FB_TOP["Yageo RC0402FR-0745K3L<br/>45.3-kOhm 1% main feedback top resistor"]
  MAIN_FB_BOTTOM["Yageo RC0402FR-0710KL<br/>10-kOhm 1% main feedback bottom resistor"]
  MAIN_FF_CAP["KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G main feed-forward capacitor"]
  MAIN_OUTPUT_CAP0["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main output capacitor #0"]
  MAIN_OUTPUT_CAP1["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R main output capacitor #1"]
  MAIN_EN_PULLDOWN["Yageo RC0402FR-0710KL<br/>10-kOhm 1% main-enable fail-low resistor"]
  POWER_FAULT_PULLUP["Yageo RC0402FR-0710KL<br/>10-kOhm 1% wired-low power-fault pull-up resistor"]
  VOICE_BUCK["Texas Instruments TPS564252DRLR<br/>fixed 4.0-V 4-A voice converter"]
  VOICE_INDUCTOR["Sunlord MWSA0503S-3R3MT<br/>3.3-uH voice-rail power inductor"]
  VOICE_INPUT_CAP["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice-converter bulk input capacitor"]
  VOICE_HF_INPUT_CAP["TDK C1005X7R1H104K050BB<br/>100-nF 50-V X7R voice-converter HF input capacitor"]
  VOICE_FB_TOP["Yageo RC0402FR-0768KL<br/>68-kOhm 1% voice feedback top resistor"]
  VOICE_FB_BOTTOM["Yageo RC0402FR-0712KL<br/>12-kOhm 1% voice feedback bottom resistor"]
  VOICE_FF_CAP["KEMET C0402C330J5GACTU<br/>33-pF 50-V C0G voice feed-forward capacitor"]
  VOICE_OUTPUT_CAP0["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice output capacitor #0"]
  VOICE_OUTPUT_CAP1["Murata GRM32ER71E226KE15L<br/>22-uF 25-V X7R voice output capacitor #1"]
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
  DISPLAY["HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  SD["Hirose DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SLOW_IO["TCA6424ARGJR<br/>24-line slow-control and UI expander"]
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
  STOPSW["MPN TBD<br/>normally-closed physical STOP control"]
  REARMSW["MPN TBD<br/>normally-open recessed RE-ARM control"]
  SAFE_SUPERVISOR["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
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
  USBC ~~~ PD_VBUS_TVS ~~~ PD_CONTROLLER ~~~ PD_CONFIG_EEPROM ~~~ NVDC_CHARGER
  NVDC_CHARGER ~~~ CELL0 ~~~ PACK_FUSE0 ~~~ PACK_NTC0 ~~~ CELL1 ~~~ PACK_FUSE1 ~~~ PACK_NTC1
  PACK_NTC1 ~~~ PACK_GAUGE ~~~ PACK_SHUNT ~~~ PACK_POWER_FET ~~~ PACK_HOLD ~~~ PACK_SUPPLY_OR ~~~ PACK_SYSTEM_DIODE ~~~ PACK_ADMISSION
  PACK_ADMISSION ~~~ PACK_DIAG_TIMER ~~~ PACK_DIAG_TIMER_RES ~~~ PACK_DIAG_TIMER_CAP ~~~ PACK_DIAG_TIMER_BYPASS ~~~ PACK_DIAG_TRIGGER_PULLDOWN ~~~ PACK_DIAG_GATE_PULLDOWN
  PACK_DIAG_GATE_PULLDOWN ~~~ PACK_DIAG_SWITCH ~~~ PACK_DIAG_RES ~~~ PACK_MID_ADC_TOP0 ~~~ PACK_MID_ADC_TOP1 ~~~ PACK_MID_ADC_BOTTOM ~~~ PACK_MID_ADC_FILTER
  PACK_MID_ADC_FILTER ~~~ PACK_STACK_ADC_TOP0 ~~~ PACK_STACK_ADC_TOP1 ~~~ PACK_STACK_ADC_TOP2 ~~~ PACK_STACK_ADC_TOP3 ~~~ PACK_STACK_ADC_TOP4 ~~~ PACK_STACK_ADC_BOTTOM ~~~ PACK_STACK_ADC_FILTER
  PACK_STACK_ADC_FILTER ~~~ AON_BUCK ~~~ AON_INDUCTOR ~~~ AON_MODE_RES ~~~ AON_INPUT_CAP ~~~ AON_OUTPUT_CAP ~~~ AON_PG_PULLUP
  AON_PG_PULLUP ~~~ MAIN_BUCK ~~~ MAIN_INDUCTOR ~~~ MAIN_INPUT_CAP ~~~ MAIN_HF_INPUT_CAP ~~~ MAIN_FB_TOP ~~~ MAIN_FB_BOTTOM ~~~ MAIN_FF_CAP ~~~ MAIN_OUTPUT_CAP0 ~~~ MAIN_OUTPUT_CAP1 ~~~ MAIN_EN_PULLDOWN ~~~ POWER_FAULT_PULLUP
  POWER_FAULT_PULLUP ~~~ VOICE_BUCK ~~~ VOICE_INDUCTOR ~~~ VOICE_INPUT_CAP ~~~ VOICE_HF_INPUT_CAP ~~~ VOICE_FB_TOP ~~~ VOICE_FB_BOTTOM ~~~ VOICE_FF_CAP ~~~ VOICE_OUTPUT_CAP0 ~~~ VOICE_OUTPUT_CAP1 ~~~ VOICE_EN_PULLDOWN ~~~ VOICE_PG_PULLUP ~~~ VOICE_PG_BASE_RES ~~~ VOICE_PG_QUALIFIER
  VOICE_PG_QUALIFIER ~~~ EXT_BUCK ~~~ EXT_INDUCTOR ~~~ EXT_BUCK_INPUT_CAP ~~~ EXT_BUCK_HF_INPUT_CAP ~~~ EXT_BUCK_FB_TOP ~~~ EXT_BUCK_FB_BOTTOM ~~~ EXT_BUCK_FF_CAP ~~~ EXT_BUCK_OUTPUT_CAP0 ~~~ EXT_BUCK_OUTPUT_CAP1 ~~~ EXT_EN_PULLDOWN ~~~ EXT_PG_PULLUP ~~~ EXT_PG_BASE_RES ~~~ EXT_PG_QUALIFIER ~~~ EXT_EFUSE
  EXT_EFUSE ~~~ EXT_RILM ~~~ EXT_DVDT_CAP ~~~ EXT_ITIMER_CAP ~~~ EXT_OVLO_TOP ~~~ EXT_OVLO_BOTTOM
  EXT_OVLO_BOTTOM ~~~ EXT_INPUT_CAP ~~~ EXT_OUTPUT_CAP ~~~ EXT_BLEEDER ~~~ NRF_POWER_SWITCH ~~~ CC_POWER_SWITCH ~~~ SD_POWER_SWITCH ~~~ CODEC_POWER_SWITCH ~~~ RECEIVER_POWER_SWITCH ~~~ S3 ~~~ SLOW_IO
  SLOW_IO ~~~ AUDIO_SAFE_GATE ~~~ RECEIVER ~~~ MONOSUM
  MONOSUM ~~~ AUDIO_RX_MUX ~~~ CAPNET ~~~ AUDIO_CAPTURE_BUFFER ~~~ ADCNET
  ADCNET ~~~ CODEC ~~~ AUDIO_SPEAKER_SELECTOR ~~~ SPEAKER_AMP ~~~ SPEAKER
  SPEAKER ~~~ MIC ~~~ TXATT ~~~ AUDIO_TX_SELECTOR ~~~ DISPLAY ~~~ SD ~~~ UNIT
  UNIT ~~~ C5 ~~~ IRDEMOD ~~~ IRCARRIER ~~~ IRTX ~~~ RP
  RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ VOICE
  VOICE ~~~ U214_I2C_ISO ~~~ U214 ~~~ STOPSW ~~~ REARMSW
  REARMSW ~~~ SAFE_SUPERVISOR ~~~ SAFE_CONDITIONER ~~~ SAFE_POR_OR ~~~ SAFE_LATCH
  SAFE_LATCH ~~~ SAFE_RESET_BUFFER ~~~ SAFE_GATE_A ~~~ SAFE_GATE_B ~~~ SAFE_PTT_OR ~~~ STOP_LED
  STOP_LED ~~~ DET_S3 ~~~ DET_C5 ~~~ DET_NRF0 ~~~ DET_NRF1 ~~~ DET_NRF2
  DET_NRF2 ~~~ DET_CC ~~~ DET_VOICE ~~~ DET_IR ~~~ EVIDENCE_CMP_A ~~~ EVIDENCE_CMP_B
  EVIDENCE_CMP_B ~~~ EVIDENCE_MASK ~~~ EVIDENCE_OR_0 ~~~ EVIDENCE_OR_1 ~~~ EVIDENCE_OR_2 ~~~ EVIDENCE_OR_3 ~~~ ANY_TX_LED
  USBC -->|"VBUS sink only"| PD_CONTROLLER
  USBC -->|"VBUS shunt"| PD_VBUS_TVS
  USBC <-->|"D-/D+ direct; no PD/charger tap"| S3
  PD_CONTROLLER <-->|"local I²C boot image"| PD_CONFIG_EEPROM
  PD_CONTROLLER <-->|"protected VBUS + local I²C/IRQ"| NVDC_CHARGER
  S3 <-->|"SYS I²C0 + shared wired-low IRQ"| PD_CONTROLLER
  CELL0 --> PACK_FUSE0 --> PACK_GAUGE
  PACK_NTC0 -->|"TH1"| PACK_GAUGE
  CELL1 --> PACK_FUSE1 --> PACK_GAUGE
  PACK_NTC1 -->|"TH2"| PACK_GAUGE
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
  PACK_DIAG_TIMER --> PACK_DIAG_TIMER_BYPASS
  PACK_DIAG_TIMER -->|"bounded gate pulse"| PACK_DIAG_SWITCH
  PACK_DIAG_TIMER --> PACK_DIAG_GATE_PULLDOWN
  PACK_DIAG_RES -->|"fused full-stack load"| PACK_DIAG_SWITCH
  PACK_FUSE0 --> PACK_MID_ADC_TOP0 --> PACK_MID_ADC_TOP1 -->|"PA25/A2"| PACK_ADMISSION
  PACK_ADMISSION --> PACK_MID_ADC_BOTTOM
  PACK_ADMISSION --> PACK_MID_ADC_FILTER
  PACK_FUSE1 --> PACK_STACK_ADC_TOP0 --> PACK_STACK_ADC_TOP1 --> PACK_STACK_ADC_TOP2 --> PACK_STACK_ADC_TOP3 --> PACK_STACK_ADC_TOP4 -->|"PA26/A1"| PACK_ADMISSION
  PACK_ADMISSION --> PACK_STACK_ADC_BOTTOM
  PACK_ADMISSION --> PACK_STACK_ADC_FILTER
  NVDC_CHARGER -->|"SYS"| AON_BUCK --> AON_INDUCTOR -->|"AON_SAFE_3V3"| SAFE_SUPERVISOR
  AON_BUCK -->|"MODE/S-CONF"| AON_MODE_RES
  NVDC_CHARGER -->|"SYS local bypass"| AON_INPUT_CAP
  AON_INDUCTOR -->|"AON_SAFE_3V3 local bypass"| AON_OUTPUT_CAP
  AON_INDUCTOR -->|"PG pull-up"| AON_PG_PULLUP --> AON_BUCK
  NVDC_CHARGER -->|"SYS"| MAIN_BUCK --> MAIN_INDUCTOR -->|"3V3_MAIN"| S3
  NVDC_CHARGER -->|"SYS local bulk"| MAIN_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| MAIN_HF_INPUT_CAP
  MAIN_INDUCTOR -->|"feedback"| MAIN_FB_TOP --> MAIN_FB_BOTTOM
  MAIN_INDUCTOR -->|"feed-forward"| MAIN_FF_CAP
  MAIN_INDUCTOR -->|"local output bank"| MAIN_OUTPUT_CAP0
  MAIN_INDUCTOR -->|"local output bank"| MAIN_OUTPUT_CAP1
  MAIN_BUCK -->|"EN fail-low"| MAIN_EN_PULLDOWN
  MAIN_INDUCTOR -->|"POWER_FAULT_N pull-up"| POWER_FAULT_PULLUP --> SLOW_IO
  MAIN_INDUCTOR -->|"3V3_MAIN"| C5
  MAIN_INDUCTOR -->|"3V3_MAIN"| RP
  MAIN_INDUCTOR --> NRF_POWER_SWITCH
  MAIN_INDUCTOR --> CC_POWER_SWITCH
  MAIN_INDUCTOR --> SD_POWER_SWITCH
  MAIN_INDUCTOR --> CODEC_POWER_SWITCH
  MAIN_INDUCTOR --> RECEIVER_POWER_SWITCH
  NVDC_CHARGER -->|"SYS"| VOICE_BUCK --> VOICE_INDUCTOR -->|"fixed 4.0 V"| VOICE
  NVDC_CHARGER -->|"SYS local bulk"| VOICE_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| VOICE_HF_INPUT_CAP
  VOICE_INDUCTOR -->|"feedback"| VOICE_FB_TOP --> VOICE_FB_BOTTOM
  VOICE_INDUCTOR -->|"feed-forward"| VOICE_FF_CAP
  VOICE_INDUCTOR -->|"local output bank"| VOICE_OUTPUT_CAP0
  VOICE_INDUCTOR -->|"local output bank"| VOICE_OUTPUT_CAP1
  VOICE_BUCK -->|"EN fail-low"| VOICE_EN_PULLDOWN
  MAIN_INDUCTOR -->|"PG pull-up"| VOICE_PG_PULLUP --> VOICE_BUCK
  SAFE_GATE_B -->|"EN"| VOICE_PG_BASE_RES --> VOICE_PG_QUALIFIER
  VOICE_BUCK -->|"PG"| VOICE_PG_QUALIFIER -->|"qualified open collector"| SLOW_IO
  NVDC_CHARGER -->|"SYS"| EXT_BUCK --> EXT_INDUCTOR --> EXT_EFUSE -->|"protected fixed 5.0 V"| U214
  NVDC_CHARGER -->|"SYS local bulk"| EXT_BUCK_INPUT_CAP
  NVDC_CHARGER -->|"SYS local HF"| EXT_BUCK_HF_INPUT_CAP
  EXT_INDUCTOR -->|"feedback"| EXT_BUCK_FB_TOP --> EXT_BUCK_FB_BOTTOM
  EXT_INDUCTOR -->|"feed-forward"| EXT_BUCK_FF_CAP
  EXT_INDUCTOR -->|"local output bank"| EXT_BUCK_OUTPUT_CAP0
  EXT_INDUCTOR -->|"local output bank"| EXT_BUCK_OUTPUT_CAP1
  EXT_BUCK -->|"EN fail-low"| EXT_EN_PULLDOWN
  MAIN_INDUCTOR -->|"PG pull-up"| EXT_PG_PULLUP --> EXT_BUCK
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
  SD_POWER_SWITCH --> SD
  CODEC_POWER_SWITCH --> CODEC
  RECEIVER_POWER_SWITCH --> RECEIVER
  S3 <-->|"1-bit SDIO: S3 GPIO10,GPIO11,GPIO12,GPIO13 ↔ C5 GPIO7,GPIO8,GPIO9,GPIO10"| C5
  S3 <-->|"SPI3+alert: S3 GPIO3,GPIO9,GPIO14,GPIO21,GPIO48 ↔ RP GPIO19,GPIO24,GPIO25,GPIO26,GPIO27"| RP
  S3 <-->|"I²C0+INT: GPIO1,GPIO2"| SLOW_IO
  S3 -->|"QSPI/touch: GPIO4,GPIO35,GPIO36,GPIO38,GPIO39,GPIO40,GPIO41,GPIO42"| DISPLAY
  S3 <-->|"SPI2: GPIO4,GPIO5,GPIO35,GPIO36"| SD
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
| `s3` | `ESP32-S3-WROOM-1U-N16R2` | 32 | 3 | 1 | 36 |
| `c5` | `ESP32-C5-WROOM-1U-N8R8` | 14 | 6 | 1 | 21 |
| `rp` | `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)` | 48 | 0 | 0 | 48 |
| `slow_io` | `TCA6424ARGJR` | 24 | 0 | 0 | 24 |

`RP=0 free` является текущим честным результатом после direct quiet-state
controls `NRF_GROUP_PWR_EN` и `CC_PWR_EN`, а не ошибкой округления. Новый
direct RP endpoint требует явного remap/review; service pins SWD/USB/RUN/
BOOTSEL не входят в GPIO budget и остаются выведенными независимо.

## Ещё абстрактные electrical endpoints

Следующие функции имеют pin reservation, но не exact production MPN/circuit:

- `3V3_MAIN`
- `AON_SAFE_3V3`
- `AON_SAFE_3V3-via-10k`
- `AON_SAFE_3V3-via-2k2`
- `C5-qualified-RF-tap`
- `CC-qualified-RF-tap`
- `NC-stop-loop-10k-pullup-10nF`
- `NO-rearm-loop-47k-pullup-100nF`
- `NRF0-qualified-RF-tap`
- `NRF1-qualified-RF-tap`
- `NRF2-qualified-RF-tap`
- `RX-AM-LW-loop-pod`
- `RX-FM-SW-SMA-front-end`
- `S3-qualified-RF-tap`
- `TP_EVIDENCE_MASK_INT_N`
- `TP_EXT_5V_ILM`
- `UI_COL0`
- `UI_COL1`
- `UI_COL2`
- `UI_ROW0`
- `UI_ROW1`
- `UI_ROW2`
- `VOICE-qualified-RF-tap`
- `accessory-present`
- `admitted-system-3v3`
- `always-available-quiet-audio-rail`
- `aon-power-good-sequence`
- `audio-ground`
- `cc-filtered-3v3`
- `codec-adcvref-decoupling`
- `codec-address-high-3v3`
- `codec-audio-ground`
- `codec-dac-to-sa518-35-45db-attenuator`
- `codec-dacvref-decoupling`
- `codec-digital-ground`
- `codec-vmid-decoupling`
- `display-ground`
- `electret-microphone-bias-and-ac-coupling`
- `exact carrier-learning IR receiver`
- `exact display/backlight driver`
- `exact robust-demod IR receiver`
- `exact-value-hold-gate-pullup`
- `fail-safe-IR-LED-driver`
- `high-z-ac-coupled-capture-network`
- `i2c-mode-strap`
- `isolated-pack-fixture-3v3`
- `main-rail-enable-after-source-admission`
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
- `product-usb-c-cc1`
- `product-usb-c-cc2`
- `product-usb-c-vbus`
- `protected configurable M5 Unit contact`
- `protected-2s-midpoint`
- `protected-accessory-power-good`
- `qualified-2s-positive`
- `qualified-32k-clock`
- `qualified-backlight-sink`
- `qualified-backlight-supply`
- `qualified-codec-3v3-analog`
- `qualified-codec-3v3-digital`
- `qualified-display-3v3`
- `qualified-es8311-mic-range-differential-input-network`
- `qualified-evidence-threshold-0`
- `qualified-evidence-threshold-1`
- `qualified-evidence-threshold-2`
- `qualified-evidence-threshold-3`
- `qualified-evidence-threshold-4`
- `qualified-evidence-threshold-5`
- `qualified-evidence-threshold-6`
- `qualified-evidence-threshold-7`
- `qualified-slot0-positive`
- `qualified-slot1-positive`
- `qualified-speaker-amp-supply`
- `qualified-speaker-enable-default-on`
- `receiver-power-reset-isolation`
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
- `voice-update-fixture`

Эти строки блокируют final schematic/BOM, но не нарушают проверенную
арифметику MCU pins. Их нельзя молча удалить либо объявить реализованными.

## Exact pin/net tables

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `slow_io.SDA`, `receiver.SDIO`, `display.TP_I2C_SDA`, `codec.CDATA`, `pd_controller.I2Ct_SDA`, `pack_admission.PA0` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `slow_io.SCL`, `receiver.SCLK`, `display.TP_I2C_SCL`, `codec.CCLK`, `pd_controller.I2Ct_SCL`, `pack_admission.PA11` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO19` | RP is held reset/high-Z through S3 strap sampling; an external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `DISPLAY_SD_SPI_D1` | `io` | `SPI2` | `sd.DAT0`, `display.QSPI_D1` | — |
| `GPIO5` | 5 | `SD_SPI_CS_N` | `o` | `SPI2` | `sd.CD_DAT3` | — |
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
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | `sd.CLK`, `display.QSPI_CLK` | — |
| `GPIO36` | 29 | `DISPLAY_SD_SPI_D0` | `o` | `SPI2` | `sd.CMD`, `display.QSPI_D0` | — |
| `GPIO37` | 30 | `SYS_INT_N` | `i` | `GPIO_IRQ` | `slow_io.INT`, `pd_controller.I2Ct_IRQ`, `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `display.QSPI_CS` | — |
| `GPIO39` | 32 | `LCD_TOUCH_INT` | `i` | `GPIO_IRQ` | `display.TP_INT` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `abstract:exact display/backlight driver` | — |
| `GPIO41` | 34 | `LCD_QSPI_D2` | `o` | `SPI2` | `display.QSPI_D2` | — |
| `GPIO42` | 35 | `LCD_QSPI_D3` | `o` | `SPI2` | `display.QSPI_D3` | — |
| `GPIO43` | 37 | `S3_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO44` | 36 | `S3_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **32 used + 3 reserved + 1 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: `GPIO47`.

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
| `GPIO0` | 5 | `PD_EEPROM_WP` | `o` | `GPIO` | `pd_config_eeprom.WP` | — |
| `GPIO1` | 6 | `CHARGE_EN_N` | `o` | `GPIO` | `nvdc_charger.CE` | — |
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
| `USB_C_VBUS_RAW` | `abstract:product-usb-c-vbus` | `pd_controller.VBUS_IN` | only the product S3 USB-C receptacle may power the board; current remains default-limited until a valid sink contract exists |
| `USB_C_VBUS_RAW` | `abstract:product-usb-c-vbus` | `pd_vbus_tvs.IN` | TVS2200DRVR is a shunt clamp physically adjacent to the receptacle, not a series element |
| `USB_C_VBUS_TVS_RETURN` | `pd_vbus_tvs.GND` | `abstract:power-ground` | short low-inductance surge return; exact placement and return geometry remain I4/layout gates |
| `USB_C_CC1` | `abstract:product-usb-c-cc1` | `pd_controller.CC1` | sink-only Type-C/PD detection; source and power-bank roles are disabled |
| `USB_C_CC2` | `abstract:product-usb-c-cc2` | `pd_controller.CC2` | sink-only Type-C/PD detection; source and power-bank roles are disabled |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `nvdc_charger.VBUS` | accepted profiles stop at 15 V/2 A; the integrated protected path remains off above the negotiated envelope |
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
| `PACK_DIAG_CH1_CLEAR_RELEASED` | `pack_diag_timer.CH1_CLR_N` | `pack_diag_timer.VCC` | channel 1 clear is fixed inactive; the non-retriggerable RC interval remains the independent pulse terminator |
| `PACK_DIAG_TIMER_RC_SUPPLY` | `pack_diag_timer.VCC` | `pack_diag_timer_res.END_1` | 169-kOhm 1% timing resistance reuses an existing BOM line |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer_res.END_2` | `pack_diag_timer.CH1_RC` | the timing node follows the TPUL2G223 manufacturer connection |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer.CH1_RC` | `pack_diag_timer_cap.END_1` | 169-kOhm with 220-nF yields about 34.4 ms typical |
| `PACK_DIAG_TIMER_C` | `pack_diag_timer_cap.END_2` | `pack_diag_timer.CH1_C` | the exact C0G timing capacitor bounds both sides of the paper pulse window without X7R DC-bias or aging ambiguity |
| `PACK_LOCAL_GND` | `pack_diag_timer.CH1_C` | `pack_gauge.GND` | the optional external C-terminal ground is used to give the timing capacitor an explicit local return |
| `PACK_DIAG_GATE` | `pack_diag_timer.CH1_Q` | `pack_diag_switch.G` | only the hardware one-shot output, never a direct MCU level, can hold the diagnostic MOSFET on |
| `PACK_DIAG_GATE` | `pack_diag_switch.G` | `pack_diag_gate_pulldown.END_1` | the MOSFET gate remains low if the one-shot supply is absent or its output is high impedance |
| `PACK_LOCAL_GND` | `pack_diag_gate_pulldown.END_2` | `pack_gauge.GND` | 10-kOhm gate pull-down fails the diagnostic load off |
| `PACK_DIAG_CH1_Q_N_NC` | `pack_diag_timer.CH1_Q_N` | `abstract:no-connect` | unused push-pull complementary output is left open as required |
| `PACK_DIAG_CH2_DISABLED` | `pack_diag_timer.CH2_CLR_N` | `pack_gauge.GND` | unused channel 2 is held asynchronously clear |
| `PACK_DIAG_CH2_INPUTS_LOW` | `pack_diag_timer.CH2_T_N` | `pack_gauge.GND` | unused Schmitt-trigger input is never left floating |
| `PACK_DIAG_CH2_INPUTS_LOW` | `pack_diag_timer.CH2_T` | `pack_gauge.GND` | unused Schmitt-trigger input is never left floating |
| `PACK_DIAG_CH2_Q_NC` | `pack_diag_timer.CH2_Q` | `abstract:no-connect` | unused push-pull output is left open |
| `PACK_DIAG_CH2_Q_N_NC` | `pack_diag_timer.CH2_Q_N` | `abstract:no-connect` | unused push-pull complementary output is left open |
| `PACK_DIAG_CH2_RC_NC` | `pack_diag_timer.CH2_RC` | `abstract:no-connect` | disabled channel has no external timing network |
| `PACK_DIAG_CH2_C_NC` | `pack_diag_timer.CH2_C` | `abstract:no-connect` | disabled channel C terminal uses its internal ground connection only |
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
| `PACK_CELL0_TEMP` | `pack_gauge.TH1` | `pack_ntc0.END_1` | one exact 10-kOhm NTC is mechanically coupled to cell 0; coupling remains an I8/HIL gate |
| `PACK_LOCAL_GND` | `pack_ntc0.END_2` | `pack_gauge.GND` | TH1 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_CELL1_TEMP` | `pack_gauge.TH2` | `pack_ntc1.END_1` | one exact 10-kOhm NTC is mechanically coupled to cell 1; coupling remains an I8/HIL gate |
| `PACK_LOCAL_GND` | `pack_ntc1.END_2` | `pack_gauge.GND` | TH2 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_SLOT0_POSITIVE_RAW` | `abstract:qualified-slot0-positive` | `pack_fuse0.END_1` | each replaceable slot has its own adjacent 5-A fast fuse |
| `PACK_2S_MIDPOINT` | `pack_fuse0.END_2` | `abstract:protected-2s-midpoint` | slot-0 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_SLOT1_POSITIVE_RAW` | `abstract:qualified-slot1-positive` | `pack_fuse1.END_1` | each replaceable slot has its own adjacent 5-A fast fuse |
| `BATTERY_STACK_POSITIVE` | `pack_fuse1.END_2` | `abstract:qualified-2s-positive` | slot-1 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_DIAG_LOAD_POSITIVE` | `abstract:qualified-2s-positive` | `pack_diag_res.END_1` | the bounded load samples the fused full stack ahead of the normally-open CHG/DIS pair |
| `PACK_DIAG_LOAD_DRAIN` | `pack_diag_res.END_2` | `pack_diag_switch.D` | 10-Ohm pulse-proof resistance limits the screen current to approximately 0.57-0.88 A over the defined stack and resistor corners |
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
| `CHARGE_EN_N` | `pd_controller.GPIO1` | `nvdc_charger.CE` | external pull-up disables charge while TPS configuration is absent/invalid; valid policy explicitly drives the active-low enable |
| `PD_EEPROM_A0_LOW` | `abstract:power-ground` | `pd_config_eeprom.A0` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A1_LOW` | `abstract:power-ground` | `pd_config_eeprom.A1` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A2_LOW` | `abstract:power-ground` | `pd_config_eeprom.A2` | fixed 7-bit address 0x50 |
| `PD_USB_P_UNUSED_LOW` | `pd_controller.GPIO4_USB_P_LD1` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D+ remains direct to S3; datasheet requires unused contact low |
| `PD_USB_N_UNUSED_LOW` | `pd_controller.GPIO5_USB_N_LD2` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D- remains direct to S3; datasheet requires unused contact low |
| `CHARGER_DP_NC` | `nvdc_charger.D_PLUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the direct S3 USB2 data pair |
| `CHARGER_DM_NC` | `nvdc_charger.D_MINUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the direct S3 USB2 data pair |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_buck.VIN` | the AON source is independent of every application rail and remains available on admitted battery or valid USB system power |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_input_cap.END_1` | one exact 4.7-uF 25-V X7R input capacitor is the TPS629203 nominal local input target |
| `POWER_GROUND` | `aon_input_cap.END_2` | `abstract:power-ground` | the AON input-capacitor loop must be placed directly at VIN and GND |
| `AON_BUCK_EN` | `nvdc_charger.SYS` | `aon_buck.EN` | direct hardware strap is manufacturer-valid, has no uncertain divider against the internal fail-low pull-down and enables AON without application firmware |
| `AON_BUCK_SW` | `aon_buck.SW` | `aon_inductor.END_1` | 2.2-uH shielded inductor is the manufacturer-nominal 2.5-MHz first target |
| `AON_SAFE_3V3` | `aon_inductor.END_2` | `abstract:AON_SAFE_3V3` | rated for at least 5-mA continuous and 8-mA transient safety load with an exact 22-uF local output capacitor |
| `AON_SAFE_3V3` | `aon_inductor.END_2` | `aon_output_cap.END_1` | one exact 22-uF 10-V X7R capacitor provides the recommended nominal AON output capacitance |
| `POWER_GROUND` | `aon_output_cap.END_2` | `abstract:power-ground` | VOS senses the capacitor positive terminal and its return remains local to the converter |
| `AON_SAFE_3V3` | `aon_inductor.END_2` | `aon_pg_pullup.END_1` | 47-kOhm pull-up reuses an existing BOM MPN and limits the always-on PG load to about 70 uA |
| `AON_PG_N` | `aon_pg_pullup.END_2` | `aon_buck.PG` | open-drain AON evidence has a defined high only after its own output rail exists |
| `AON_SAFE_3V3_SENSE` | `abstract:AON_SAFE_3V3` | `aon_buck.VOS` | remote sense is taken at the local AON output capacitor rather than the switching node |
| `AON_VSET_3V3_NC` | `abstract:no-connect-open-vset` | `aon_buck.FB_VSET` | FB/VSET is deliberately left open; the datasheet decodes open or at least 249 kOhm as fixed 3.3 V |
| `AON_MODE_SET` | `aon_buck.MODE_SCONF` | `aon_mode_res.END_1` | 42.2-kOhm 1% selects VSET, up-to-2.5-MHz auto-PFM/PWM AEE and disabled output discharge |
| `POWER_GROUND` | `aon_mode_res.END_2` | `abstract:power-ground` | fixed resistor strap is read at startup and cannot be changed by application firmware |
| `AON_PG_N` | `aon_buck.PG` | `abstract:aon-power-good-sequence` | open-drain evidence must be valid before the hard-STOP supervisor and downstream sequencing are released |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_buck.VIN` | independent fixed converter prevents compute transients from changing voice or accessory voltage |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor exceeds the TPS564252 nominal input recommendation |
| `POWER_GROUND` | `main_input_cap.END_2` | `abstract:power-ground` | main bulk input return stays inside the high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency VIN current |
| `POWER_GROUND` | `main_hf_input_cap.END_2` | `abstract:power-ground` | main high-frequency input return is placed directly at converter ground |
| `MAIN_3V3_EN` | `abstract:main-rail-enable-after-source-admission` | `main_buck.EN` | reset-low hardware sequencer permits main power only after an admitted battery pair or valid USB service source |
| `MAIN_3V3_EN` | `main_buck.EN` | `main_en_pulldown.END_1` | external 10-kOhm reset-low default dominates the converter's 2-MOhm internal pull-down and any high-impedance sequencer state |
| `POWER_GROUND` | `main_en_pulldown.END_2` | `abstract:power-ground` | main converter stays disabled if its sequencer output is absent or unpowered |
| `MAIN_BUCK_SW` | `main_buck.SW` | `main_inductor.END_1` | 3.3-uH exact first target keeps the 3-A load-step peak below its minimum saturation current |
| `3V3_MAIN` | `main_inductor.END_2` | `abstract:3V3_MAIN` | fixed 3.3-V rail is sized for 2.5-A continuous and 3.0-A load-step demand |
| `3V3_MAIN` | `main_inductor.END_2` | `main_fb_top.END_1` | active 45.3-kOhm replacement for the obsolete 45.0-kOhm table value starts the fixed main feedback divider |
| `MAIN_3V3_FB` | `main_fb_top.END_2` | `main_buck.FB` | 45.3-kOhm over 10-kOhm sets nominal 3.318 V without a selector or firmware control |
| `MAIN_3V3_FB` | `main_buck.FB` | `main_fb_bottom.END_1` | 1% bottom resistor completes the fixed main feedback divider |
| `POWER_GROUND` | `main_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin feedback return must not share the switching-current return |
| `3V3_MAIN` | `main_inductor.END_2` | `main_ff_cap.END_1` | 33-pF C0G feed-forward capacitor stays inside the datasheet 10-to-100-pF high-output range |
| `MAIN_3V3_FB` | `main_ff_cap.END_2` | `main_buck.FB` | feed-forward element is physically across the top divider resistor |
| `3V3_MAIN` | `main_inductor.END_2` | `main_output_cap0.END_1` | first physical 22-uF 25-V X7R output capacitor contributes to the recommended 44-uF nominal bank |
| `POWER_GROUND` | `main_output_cap0.END_2` | `abstract:power-ground` | first main output capacitor closes the local power loop |
| `3V3_MAIN` | `main_inductor.END_2` | `main_output_cap1.END_1` | second independent 22-uF 25-V X7R output capacitor preserves DC-bias and transient margin |
| `POWER_GROUND` | `main_output_cap1.END_2` | `abstract:power-ground` | second main output capacitor closes the local power loop |
| `MAIN_3V3_PG_N` | `main_buck.PG` | `abstract:power-current-thermal-fault` | open-drain loss/fault evidence joins the diagnostic aggregate without replacing hardware protection |
| `3V3_MAIN` | `main_inductor.END_2` | `power_fault_pullup.END_1` | one exact pull-up serves the entire wired-low fault aggregate only while its diagnostic domain is powered |
| `POWER_FAULT_N` | `power_fault_pullup.END_2` | `abstract:power-current-thermal-fault` | 10-kOhm limits any asserting PG, FLT or qualifier sink to about 0.33 mA |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_buck.VIN` | voice has a physically independent fixed-voltage converter rather than a shared 4/5-V selector |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor keeps the voice switching loop independent |
| `POWER_GROUND` | `voice_input_cap.END_2` | `abstract:power-ground` | voice bulk input return stays inside its own high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency voice-converter VIN current |
| `POWER_GROUND` | `voice_hf_input_cap.END_2` | `abstract:power-ground` | voice high-frequency input return is placed directly at converter ground |
| `VOICE_BUCK_SW` | `voice_buck.SW` | `voice_inductor.END_1` | 3.3-uH exact first target has margin over the qualified 1.5-A transient peak current |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice.VCC` | fixed 4.0-V rail can never be switched to the 5-V accessory setting |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice_fb_top.END_1` | 68-kOhm 1% top resistor starts the physically fixed voice feedback divider |
| `VOICE_4V_FB` | `voice_fb_top.END_2` | `voice_buck.FB` | 68-kOhm over 12-kOhm sets nominal 4.000 V without a selector |
| `VOICE_4V_FB` | `voice_buck.FB` | `voice_fb_bottom.END_1` | 12-kOhm 1% bottom resistor completes the fixed voice divider |
| `POWER_GROUND` | `voice_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin return prevents load current from shifting the voice set point |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice_ff_cap.END_1` | 33-pF C0G feed-forward capacitor follows the datasheet high-output recommendation |
| `VOICE_4V_FB` | `voice_ff_cap.END_2` | `voice_buck.FB` | feed-forward element is physically across the voice top divider resistor |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice_output_cap0.END_1` | first physical 22-uF 25-V X7R output capacitor supports voice startup and TX transients |
| `POWER_GROUND` | `voice_output_cap0.END_2` | `abstract:power-ground` | first voice output capacitor closes its local power loop |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice_output_cap1.END_1` | second independent 22-uF 25-V X7R output capacitor completes the 44-uF nominal bank |
| `POWER_GROUND` | `voice_output_cap1.END_2` | `abstract:power-ground` | second voice output capacitor closes its local power loop |
| `VOICE_4V_PG_N` | `voice_buck.PG` | `abstract:voice-power-reset-domain` | PD remains asserted until the exact fixed 4-V rail is valid |
| `3V3_MAIN` | `main_inductor.END_2` | `voice_pg_pullup.END_1` | voice PG is referenced only to the powered diagnostic domain |
| `VOICE_4V_PG_N` | `voice_pg_pullup.END_2` | `voice_buck.PG` | 10-kOhm draws at most about 0.33 mA when the open-drain PG is low, far below its 4-mA rating |
| `VOICE_4V_PG_N` | `voice_buck.PG` | `voice_pg_qualifier.E` | the open-drain PG emitter input is qualified by the same STOP-dominant enable request; PG is pulled up only inside the powered 3V3_MAIN diagnostic domain |
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
| `3V3_MAIN` | `main_inductor.END_2` | `ext_pg_pullup.END_1` | accessory PG is referenced only to the powered diagnostic domain |
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
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_switch.IN` | storage inrush and faults are isolated from the shared compute rail |
| `3V3_SD_SWITCHED` | `sd_power_switch.VOUT` | `sd.VDD` | card rail is enabled only for a bounded mounted storage session |
| `SD_QOD` | `sd_power_switch.QOD` | `sd_power_switch.VOUT` | rail discharges after a qualified flush/unmount sequence |
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
| `UI_ROW0` | `slow_io.P00` | `abstract:UI_ROW0` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_ROW1` | `slow_io.P01` | `abstract:UI_ROW1` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_ROW2` | `slow_io.P02` | `abstract:UI_ROW2` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL0` | `slow_io.P03` | `abstract:UI_COL0` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL1` | `slow_io.P04` | `abstract:UI_COL1` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL2` | `slow_io.P05` | `abstract:UI_COL2` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `LCD_RST_N` | `slow_io.P06` | `display.RESET` | external reset-safe pull; release only after qualified display rails are stable |
| `TOUCH_RST_N` | `slow_io.P07` | `display.TP_RESET` | external reset-safe pull; exact TP_RESXP polarity and timing require specimen HIL |
| `LCD_VDDI_3V3` | `abstract:qualified-display-3v3` | `display.VDDI` | local decoupling and sequencing remain electrical gates |
| `LCD_VDD_3V3` | `abstract:qualified-display-3v3` | `display.VDD` | local decoupling, inrush and sequencing remain electrical gates |
| `LCD_IM1_HIGH` | `abstract:qualified-display-3v3` | `display.IM1` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_IM0_LOW` | `display.IM0` | `abstract:display-ground` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_IM2_LOW` | `display.IM2` | `abstract:display-ground` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_DB2_LOW` | `display.DB2_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB3_LOW` | `display.DB3_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB4_LOW` | `display.DB4_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB5_LOW` | `display.DB5_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB6_LOW` | `display.DB6_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB7_LOW` | `display.DB7_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_LEDA` | `abstract:qualified-backlight-supply` | `display.LEDA` | production backlight source remains an exact current/thermal/EMI gate |
| `LCD_LEDK` | `display.LEDK_1` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
| `LCD_LEDK` | `display.LEDK_2` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
| `LCD_LEDK` | `display.LEDK_3` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
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
| `SD_PWR_EN` | `slow_io.P20` | `sd_power_switch.ON` | external off-safe pull; the exact switch controls inrush and short faults |
| `SD_CARD_DETECT_N` | `sd.DETECT_A` | `slow_io.P21` | read-only debounced input; socket switch return is tied to the qualified reference domain |
| `STOP_LATCH_SENSE` | `safe_latch.Q` | `slow_io.P22` | diagnostic mirror only; non-programmable hard-stop dominance never depends on the expander |
| `S3_RF_TX_EVIDENCE_N` | `evidence_cmp_a.OUT1` | `slow_io.P23` | direct read-only mirror of the exact S3 evidence comparator |
| `POWER_FAULT_N` | `abstract:power-current-thermal-fault` | `slow_io.P25` | hardware protection acts independently; this is diagnostic evidence |
| `ACCESSORY_PRESENT_N` | `abstract:accessory-present` | `slow_io.P26` | read-only, protected and debounced |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_supervisor.VDD` | always-on source and hold-up are selected and budgeted in I3 |
| `AON_SAFE_SENSE` | `abstract:AON_SAFE_3V3` | `safe_supervisor.SENSE` | factory G33 threshold supervises the actual safety rail |
| `AON_MR_N` | `abstract:AON_SAFE_3V3-via-10k` | `safe_supervisor.MR_N` | no firmware-controlled manual reset path |
| `POR_N` | `abstract:AON_SAFE_3V3-via-10k` | `safe_supervisor.RESET_N` | open-drain supervisor output is pulled up only to AON_SAFE_3V3 |
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
| `EVIDENCE_ADDR_A0_LOW` | `abstract:safety-ground` | `evidence_mask.A0` | fixed 7-bit address 0x20 |
| `EVIDENCE_ADDR_A1_LOW` | `abstract:safety-ground` | `evidence_mask.A1` | fixed 7-bit address 0x20 |
| `EVIDENCE_ADDR_A2_LOW` | `abstract:safety-ground` | `evidence_mask.A2` | fixed 7-bit address 0x20 |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20`, `GPIO43`, `GPIO44` — native USB Serial/JTAG, permanent default UART0 RF-test/diagnostic route and physical EN/BOOT.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO11`, `GPIO12`, `GPIO13`, `GPIO14` — native USB Serial/JTAG, permanent UART0, physical CHIP_PU/BOOT and normal-boot/log strap; 1-bit SDIO leaves USB contacts independent.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.
- `pd_controller`: `I2Ct_SDA`, `I2Ct_SCL`, `I2Ct_IRQ` — S3 shared SYS_I2C0 host control plus shared wired-low IRQ; same bus is exposed on protected service pads for controller status/recovery.
- `pd_config_eeprom`: `SDA`, `SCL`, `WP` — direct factory pads permit first-image programming and recovery independent of S3/TPS application state; GND and qualified 3.3 V accompany the fixture.
- `pack_gauge`: `ALRT`, `SCL_OD`, `SDA_DQ`, `PFAIL` — direct protected I2C/NVM and hold/fault pads with fixture ground and qualified stack-sense supply; protected image checksum and OvrdEn readback are mandatory before energized cell installation.
- `pack_admission`: `PA1_NRST`, `PA17`, `PA18_A7`, `PA19_SWDIO`, `PA20_A6_SWCLK`, `VDD`, `VSS` — permanent NRST/SWD/UART plus isolated fixture VDD/VSS; fixture or admitted system rail powers flash programming because MAX17320 AOLDO is not sized for it.
- `voice`: `UPDATE`, `UART_TX`, `UART_RX`, `PD` — permanent fixture breakout for vendor update/recovery plus UART and hardware power-down; UPDATE drive remains inhibited until exact rev-1.1 direction/timing proof.

### Non-MCU contact accounting

| Instance | Used | Reserved | Free |
|---|---:|---:|---:|
| `slow_io` | 24 | 0 | 0 |

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
| `S3_INTERNAL_I2C` | `s3` | `slow_io`, `display touch`, `codec`, `receiver`, `pd_controller`, `pack_admission` | scheduled; bounded transactions; expander, PD, pack and touch interrupts only wake the service loop; GPIO47 remains free | ordinary UI/control first visible response <=100 ms; PD/pack/fault status is read after shared IRQ, and no radio FIFO or PTT deadline is placed here | ES8311 address/readback and power-off no-backfeed, touch IRQ/reset, PD and pack target-interface recovery, wired-low IRQ source identification, shortest-pulse, matrix and fault-latency HIL |
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
- `sd` lifecycle: `current_manufacturer_page`.
- `display` lifecycle: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`.
- `codec` lifecycle: `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open`.
- `audio_rx_mux` uses `Texas Instruments SN74LVC1G3157DBVR` as `verified_reference`, not an accepted production choice.
- `audio_capture_buffer` uses `Texas Instruments TLV9061IDBVR` as `reference_only`, not an accepted production choice.
- `audio_speaker_selector` uses `Texas Instruments TMUX1136DGSR` as `reference_only`, not an accepted production choice.
- `audio_tx_selector` uses `Texas Instruments TS5A63157DCKR` as `reference_only`, not an accepted production choice.
- `audio_safe_gate` uses `Texas Instruments SN74LVC2G08DCUR` as `reference_only`, not an accepted production choice.
- `speaker_amp` uses `Diodes Incorporated PAM8302AASCR` as `verified_reference`, not an accepted production choice.
- `pack_gauge` lifecycle: `recommended_for_new_designs`.
- `pack_diag_timer` lifecycle: `active_production`.
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
- HMX035CTFT-001 is the exact assembly marking disclosed by the QDtech reference schematic and is instantiated as a paper candidate, not a production-qualified orderable part; exact drawing/FPC mechanics, lifecycle, connector, backlight/protection and specimen HIL remain open
- After DEC-0059 restores full S3/C5 service, S3 retains only GPIO47 free, C5 one and RP none. Slow_io P27 carries RX_AUDIO_SOURCE_SEL, so the 24-line slow plane has no reserve. GPIO47 remains unassigned; any new direct RP endpoint requires an explicit remap and repeated review
- C5 1-bit SDIO has exclusive ownership of the S3 SD/MMC host and leaves C5 native USB GPIO13/14 independent. S3 and C5 each retain both native USB and permanent default UART service; 1-bit framed throughput, control priority and reset recovery remain HIL gates, with 4-bit plus explicit service isolation only as fallback
- display and microSD are the only scheduled high-rate pair on one SPI2 controller; separate CS/per-device clocks and bounded transactions remove radio impact, but >=4.0 MB/s storage plus <=100 ms visible UI under card stalls remains a mandatory HIL gate
- PIO instruction memory, DMA arbitration latency and SRAM-bank contention remain executable firmware/HIL gates even though the state-machine/channel capacity arithmetic closes with explicit reserve
- DEC-0045 prohibits cross-group simultaneous signal operation but requires all three SG-N24 radios concurrently active in every independent PTX/PRX mix; DEC-0047 selects a qualified internal envelope; N24H-0001 L0 DIV-DIV is pre-HIL only and T1 TARGET must prove exact channel/power/sensitivity points
- SG-N24 3PTX is a real accepted load case, so the exact module choice and packet-rail design must prove simultaneous TX peak/average current, droop, thermal, coupling and STOP at the qualified power profile; a former RX-only hunt budget is insufficient
- DEC-0046 consumes RP GPIO15/GPIO23 and C5 GPIO4 for group-level power gates; exact load-switch/isolator MPNs, discharge, no-back-power sequencing and quiet-state EMI HIL remain open, leaving no free direct RP GPIO
- DEC-0054 instantiates ES8311, SN74LVC1G3157DBVR, TLV9061IDBVR, TMUX1136DGSR, TS5A63157DCKR, SN74LVC2G08DCUR and PAM8302AASCR as the prototype audio topology and assigns GPIO6 AUDIO_ARM; exact passive values, powered-off loading, codec power, common-mode/gain, pop/click, RF immunity and HIL remain open before schematic/BOM freeze
- DEC-0063 instantiates TPS25751DREFR, BQ25798RQMR, CAT24C512WI-GT3 and TVS2200DRVR as the sink-only 30-W USB-PD frontend; DEC-0066 adds MAX17320G20+T and MSPM0C1104SDGS20R as the fail-closed 2S manager pair; DEC-0067 disables in-device deep-cell recovery and instantiates the exact switching path. DEC-0068 adds independent fixed TPS629203/TPS564252 AON/3.3/4.0/5.0-V converters, exact Sunlord inductors and five TPS22919 quiet-state switches; DEC-0069 corrects the connector eFuse to latch-off TPS259470LRPWR; DEC-0070 adds two exact MMBT3904-7-F PG qualifiers; DEC-0071 adds eight exact eFuse passives, an immediately active 1.509-A limit, controlled startup and a bounded post-start 2-A transient; DEC-0072 adds 24 exact converter energy/configuration/feedback passives and fixed tolerance-screened outputs; DEC-0073 adds nine exact converter EN/PG/fault resistors and a direct hardware AON enable strap; DEC-0074 adds the exact 10-Ohm pre-admission load, non-retriggerable <=50-ms hardware cutoff, corrected PA25/PA26 ADC contacts and exact divider/filter networks. Exact USB-C/USB2 protection, charger passives, mechanical reverse-insertion/thermal coupling, diagnostic thresholds/cooldown, hot/fault calculations and HIL remain open before schematic/BOM freeze
- HMX035CTFT-001 exact contacts are instantiated, but display production qualification remains open; the I2 hard-stop/evidence active circuit is paper-reviewed while its AON source/hold-up is I3 and detector taps/thresholds are I6; exact IR frontends, power tree and antenna placement remain open; SA518/Si4732 contact maps are instantiated, while SA518 UPDATE electrical direction/timing and both modules' surrounding power/audio/RF circuits remain specimen/electrical/HIL gates before target-architecture acceptance

## Граница проведённого ревью

Validator доказывает существование реально выведенных compute contacts,
полный used/reserved/free accounting, straps, fixed mux, service paths,
PIO/DMA capacity, independent radio/IPC resources и exact paper-level
AON hard-STOP/evidence circuit. Remaining peripheral MPN, branch power,
signal/power integrity, RF taps/layout and HIL are later gates; этот atlas
не разрешает KiCad и не является frozen BOM.
