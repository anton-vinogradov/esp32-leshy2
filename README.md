# Leshy2 hardware

[Русский](README.ru.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware)

Leshy2 is an open, autonomous instrument for radio observation,
communications, diagnostics and authorized research of wireless and contact
systems. This documentation describes what the target device does and how it
is built.

## What the device can do

- Operate three full-function nRF24 radios concurrently in `3R`, `1T2R`,
  `2T1R` and `3T` combinations.
- Work with 2.4/5-GHz Wi-Fi, Bluetooth LE, ESP-NOW, IEEE 802.15.4,
  315/433/868/915-MHz Sub-GHz, FM/AM/SW/LW, VHF/UHF voice and IR.
- Route all nine onboard RF paths to outward-face antenna jacks: two RP-SMA
  and seven SMA ports. Neither connector bank occupies the interboard channel.
- Show menus, a spectrum waterfall and path state on a 3.5-inch portrait
  `320×480` touch IPS display driven by direct QSPI.
- Record data and audio to removable microSD, play through a speaker or
  headphones and capture from the built-in microphone.
- Accept a rear M5Stack U214 LoRa/GNSS Cap and a separately protected M5 Unit
  port for external GNSS, LoRa, NFC, iButton/1-Wire and other modules.
- Give the owner independent programming, recovery and diagnostic paths for
  every programmable controller.

## How it is built

The device contains five isolatable compute and control domains. The
`ESP32-S3-WROOM-1U-N16R2` owns UI, display, storage and audio;
`ESP32-C5-WROOM-1U-N8R8` owns native 2.4/5-GHz radio, IEEE 802.15.4 and IR;
`SC1512-A4` (RP2354B) owns the three nRF24 radios, Sub-GHz, voice and U214;
one `MSPM0C1104SDGS20R` independently admits the battery pack; a second
`MSPM0C1104SDGS20R` owns the watchdog, thermal supervision and TX leases.
Unused interfaces are powered down and placed into a verifiable quiet state.

## Device layout

### External and inner board faces

![Leshy2 external faces](docs/images/current-clamshell.svg?layout=12)

The first projection shows only the outward, user-facing PCB sides: display,
controls, labelled RF ports, indicators and side interfaces. The second shows
the two mirrored inner faces and the exact devices inside the sandwich. A
number inside a component outline maps to the adjacent exact MPN and role.

![Leshy2 inner board faces](docs/images/internal-board-layout.svg?layout=9)

### Top view from the antenna edge

The true top projection looks along the board from its antenna edge and shows
the sandwich width and depth, both antenna banks and the symmetric Cap
overhang.

![Leshy2 top view from the antenna edge](docs/images/top-edge-view.svg?layout=3)

### Sandwich sections

Section A–A crosses the LoRa Cap zone; B–B crosses the battery and rear-control
zone. Different longitudinal zones are never combined in one projection.

![Leshy2 sandwich sections](docs/images/sandwich-section.svg?layout=9)

<!-- BEGIN GENERATED PRINCIPLE DIAGRAMS -->

## Principle component interconnections

Read the architecture from its three compute owners, not from the USB port.
The first map shows only inter-processor links; the following maps expand
each owner's devices and the independent power path. Every box is one
physical device with its selected part number or an explicit ‘not selected’
mark and product role; no box combines different devices.

### Compute ownership map

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2.4/5-GHz, IEEE 802.15.4 and IR owner"]
RP["SC1512-A4<br/>deterministic radio and voice owner"]
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
```

### S3: user interface, storage, audio and native expansion

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
DISPLAY["HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3.5-inch QSPI display and touch assembly"]
SD["Hirose DM3AT-SF-PEJM5<br/>push-push microSD connector"]
SLOW_IO["TCA6424ARGJR<br/>24-line slow-control expander"]
UI_MATRIX_IO["TCA9539PWR<br/>16 direct D-pad and function-key inputs"]
CODEC["Everest Semiconductor ES8311<br/>audio capture and playback codec"]
RECEIVER["Si4732-A10-GSR<br/>FM/AM/SW/LW broadcast receiver"]
UNIT_CONNECTOR["1125R-SMT-4P<br/>protected M5 Unit HY2.0-4P connector"]
  S3 -->|"direct QSPI + touch"| DISPLAY
  S3 -->|"scheduled SPI + isolated rail"| SD
  S3 <-->|"I²C0 + wired-low IRQ"| SLOW_IO
  S3 <-->|"I²C0 + wired-low IRQ"| UI_MATRIX_IO
  S3 <-->|"isolated I²S0 + I²C0"| CODEC
  S3 <-->|"isolated I²C0"| RECEIVER
  S3 <-->|"isolated profile pair"| UNIT_CONNECTOR
```

### C5: native 2.4/5 GHz, 802.15.4 and IR

```mermaid
flowchart TD
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2.4/5-GHz, IEEE 802.15.4 and IR owner"]
IR_DEMOD["Vishay TSOP95238TT<br/>38-kHz demodulating IR receiver"]
IR_CARRIER["Vishay TSMP95000TT<br/>carrier-learning IR receiver"]
IR_EMITTER["Vishay VSMY14940<br/>940-nm IR transmitter"]
  C5 <-->|"RMT RX0"| IR_DEMOD
  C5 <-->|"RMT RX1"| IR_CARRIER
  C5 -->|"RMT TX + FAULT_KILL-qualified power"| IR_EMITTER
```

### RP: deterministic radios, voice and U214

```mermaid
flowchart TD
RP["SC1512-A4<br/>deterministic radio and voice owner"]
NRF0["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #0"]
NRF1["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #1"]
NRF2["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #2"]
CC["CC1101RGPR<br/>multi-band sub-GHz transceiver"]
VOICE["NiceRF SA518<br/>analog VHF/UHF voice transceiver"]
U214_CONNECTOR["Samtec SSW-107-02-S-D<br/>vertical 14-contact Cap-Bus host on raised rear rail"]
U214["M5Stack U214 Cap LoRa-1262<br/>removable LoRa/GNSS Cap module"]
  RP <-->|"independent PIO0 SM0"| NRF0
  RP <-->|"independent PIO0 SM1"| NRF1
  RP <-->|"independent PIO0 SM2"| NRF2
  RP <-->|"independent PIO0 SM3"| CC
  RP <-->|"UART0 + direct PTT"| VOICE
  RP <-->|"PIO1 + UART1 + I²C0"| U214_CONNECTOR
  U214_CONNECTOR <-->|"2×7 · 2.54 mm · contacts 1…14"| U214
```

### Controls: from each physical switch to its owner

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
RP["SC1512-A4<br/>deterministic radio and voice owner"]
UI_MATRIX_IO["TCA9539PWR<br/>16 direct D-pad and function-key inputs"]
UI_DPAD_SWITCH["Alps Alpine SKRHADE010<br/>four directions and centre push below the single D-pad cross"]
UI_SWITCH_BACK["OMRON B3S-1100P<br/>BACK button"]
UI_SWITCH_OPT["OMRON B3S-1100P<br/>OPT button"]
UI_SWITCH_F1["OMRON B3S-1100P<br/>rear F1 function button"]
UI_SWITCH_F2["OMRON B3S-1100P<br/>rear F2 function button"]
ENCODER["Alps Alpine EC11E18244AU<br/>rear rotary encoder with push"]
PTT_SWITCH["OMRON B3S-1100P<br/>independent rear PTT button"]
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>single maintained low-current RUN/KILL switch"]
SAFETY_CONTROLLER["Texas Instruments MSPM0C1104SDGS20R<br/>independent AON watchdog, thermal and TX-lease controller"]
SAFETY_WATCHDOG["Texas Instruments TPS3435CAKAGDDFR<br/>independent 1.6-s timeout watchdog"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>physical RUN and S3 fault-reset conditioner"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>asynchronous FAULT_KILL latch"]
  UI_DPAD_SWITCH -->|"five independent inputs"| UI_MATRIX_IO
  UI_SWITCH_BACK -->|"direct P05"| UI_MATRIX_IO
  UI_SWITCH_OPT -->|"direct P06"| UI_MATRIX_IO
  UI_SWITCH_F1 -->|"direct P10 across M1"| UI_MATRIX_IO
  UI_SWITCH_F2 -->|"direct P11 across M1"| UI_MATRIX_IO
  ENCODER -->|"push P12 across M1"| UI_MATRIX_IO
  UI_MATRIX_IO -->|"I²C0 + IRQ"| S3
  ENCODER -->|"A/B direct PCNT"| S3
  PTT_SWITCH -->|"direct active-low PTT"| RP
  POWER_COMMAND_SWITCH -->|"physical KILL / RUN edge"| SAFE_CONDITIONER
  SAFETY_CONTROLLER -->|"deadline service"| SAFETY_WATCHDOG
  SAFETY_WATCHDOG -->|"WDO_N"| SAFE_LATCH
  SAFE_CONDITIONER -->|"KILL / physical re-arm clock"| SAFE_LATCH
```

### Audio path: receive, capture, playback and transmit

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
RECEIVER["Si4732-A10-GSR<br/>FM/AM/SW/LW broadcast receiver"]
VOICE["NiceRF SA518<br/>analog VHF/UHF voice transceiver"]
MICROPHONE["Same Sky CMEJ-0413-42-SMT-TR<br/>internal electret microphone"]
AUDIO_RX_MUX["Texas Instruments SN74LVC1G3157DBVR<br/>received-audio source selector"]
AUDIO_CAPTURE_SELECTOR["Texas Instruments TS5A63157DCKR<br/>microphone/RX capture selector"]
AUDIO_CAPTURE_BUFFER["Texas Instruments TLV9061IDBVR<br/>codec ADC buffer"]
CODEC["Everest Semiconductor ES8311<br/>audio capture and playback codec"]
AUDIO_SPEAKER_SELECTOR["Texas Instruments TMUX1136DGSR<br/>RX-bypass/codec speaker selector"]
AUDIO_TX_SELECTOR["Texas Instruments TS5A63157DCKR<br/>microphone/codec voice-TX selector"]
SPEAKER_AMP["Diodes Incorporated PAM8302AASCR<br/>differential speaker amplifier"]
SPEAKER["PUI Audio AS02404PO<br/>internal 4-Ohm speaker"]
HEADPHONE_JACK["Same Sky SJ1-3515-SMT-TR<br/>3.5-mm headphone output with detect"]
  RECEIVER -->|"FM/AM/SW/LW audio"| AUDIO_RX_MUX
  VOICE -->|"received AF"| AUDIO_RX_MUX
  AUDIO_RX_MUX -->|"selected RX"| AUDIO_CAPTURE_SELECTOR
  MICROPHONE -->|"guarded MIC_RAW across M1"| AUDIO_CAPTURE_SELECTOR
  AUDIO_CAPTURE_SELECTOR --> AUDIO_CAPTURE_BUFFER --> CODEC
  CODEC <-->|"I²S0 + I²C0"| S3
  AUDIO_RX_MUX -->|"reset-default receive bypass"| AUDIO_SPEAKER_SELECTOR
  CODEC -->|"differential playback"| AUDIO_SPEAKER_SELECTOR
  AUDIO_SPEAKER_SELECTOR -->|"differential low-level across M1"| SPEAKER_AMP
  SPEAKER_AMP -->|"filtered BTL"| SPEAKER
  CODEC -->|"stereo output + detect"| HEADPHONE_JACK
  MICROPHONE -->|"ordinary voice source"| AUDIO_TX_SELECTOR
  CODEC -->|"generated/processed voice source"| AUDIO_TX_SELECTOR
  AUDIO_TX_SELECTOR -->|"isolated microphone input"| VOICE
```

### Programming, recovery and diagnostics for all three compute owners

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>product USB-C receptacle"]
PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>CC and USB2 port protector"]
S3_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>keyed DBG10: UART0/RESET/BOOT"]
S3_RESET_BUTTON["Alps Alpine SKQGADE010<br/>S3 service RESET button"]
S3_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>S3 service BOOT button"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2.4/5-GHz, IEEE 802.15.4 and IR owner"]
C5_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only C5 recovery USB-C"]
C5_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-protected C5 USB2 switch"]
C5_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>keyed DBG10: UART0/RESET/BOOT"]
C5_RESET_BUTTON["Alps Alpine SKQGADE010<br/>C5 service RESET button"]
C5_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>C5 service BOOT button"]
RP["SC1512-A4<br/>deterministic radio and voice owner"]
RP_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only RP recovery USB-C"]
RP_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-protected RP USB2 switch"]
RP_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>keyed DBG10: SWD/RUN/USB_BOOT"]
RP_RESET_BUTTON["Alps Alpine SKQGADE010<br/>RP service RUN/RESET button"]
RP_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>RP service USB_BOOT button"]
  PRODUCT_USB_CONNECTOR <-->|"USB2 data"| PRODUCT_USB_PROTECTOR <-->|"native USB"| S3
  S3_DBG_HEADER <-->|"UART0 + RESET + BOOT"| S3
  S3_RESET_BUTTON -->|"RESET"| S3
  S3_BOOT_BUTTON -->|"GPIO0"| S3
  C5_SERVICE_USB_CONNECTOR <-->|"data only; VBUS sense only"| C5_SERVICE_USB_SWITCH <-->|"native USB"| C5
  C5_DBG_HEADER <-->|"UART0 + RESET + BOOT"| C5
  C5_RESET_BUTTON -->|"RESET"| C5
  C5_BOOT_BUTTON -->|"GPIO28"| C5
  RP_SERVICE_USB_CONNECTOR <-->|"data only; VBUS sense only"| RP_SERVICE_USB_SWITCH <-->|"native USB"| RP
  RP_DBG_HEADER <-->|"SWD + RUN + USB_BOOT"| RP
  RP_RESET_BUTTON -->|"RUN"| RP
  RP_BOOT_BUTTON -->|"QSPI_SS / USB_BOOT"| RP
```

### Nine independent antenna ports

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
S3_EXTERNAL_RP_SMA["GCT RFPC-SMA32-FN-175-A<br/>external S3 2.4-GHz RP-SMA port"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2.4/5-GHz, IEEE 802.15.4 and IR owner"]
C5_EXTERNAL_RP_SMA["GCT RFPC-SMA32-FN-175-A<br/>external C5 2.4/5-GHz RP-SMA port"]
RECEIVER["Si4732-A10-GSR<br/>FM/AM/SW/LW broadcast receiver"]
RECEIVER_FMSW_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>receive-only FM/SW SMA port"]
RECEIVER_AMLW_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>non-50-Ohm AM/LW loop/pod SMA port"]
NRF0["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #0"]
NRF0_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>independent nRF24 #0 SMA port"]
NRF1["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #1"]
NRF1_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>independent nRF24 #1 SMA port"]
NRF2["Ebyte E01-ML01IPX<br/>full-function nRF24 radio #2"]
NRF2_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>independent nRF24 #2 SMA port"]
CC["CC1101RGPR<br/>multi-band sub-GHz transceiver"]
CC_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>multi-band sub-GHz SMA port"]
VOICE["NiceRF SA518<br/>analog VHF/UHF voice transceiver"]
VOICE_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>VHF/UHF voice SMA port"]
  S3 -->|"50 Ω"| S3_EXTERNAL_RP_SMA
  C5 -->|"50 Ω"| C5_EXTERNAL_RP_SMA
  RECEIVER -->|"FM/SW receive"| RECEIVER_FMSW_EXTERNAL_SMA
  RECEIVER -->|"AM/LW loop/pod"| RECEIVER_AMLW_EXTERNAL_SMA
  NRF0 -->|"50 Ω"| NRF0_EXTERNAL_SMA
  NRF1 -->|"50 Ω"| NRF1_EXTERNAL_SMA
  NRF2 -->|"50 Ω"| NRF2_EXTERNAL_SMA
  CC -->|"50 Ω"| CC_EXTERNAL_SMA
  VOICE -->|"50 Ω"| VOICE_EXTERNAL_SMA
```

### Power as an independent path

```mermaid
flowchart TD
PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>product USB-C receptacle"]
PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>CC and USB2 port protector"]
S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display, storage, audio, BLE/Wi-Fi owner"]
PD_VBUS_TVS["Texas Instruments TVS2200DRVR<br/>22-V VBUS shunt protector"]
PD_CONTROLLER["Texas Instruments TPS25751DREFR<br/>sink-only USB-PD controller"]
NVDC_CHARGER["Texas Instruments BQ25798RQMR<br/>2S charger and NVDC power path"]
PACK_HOLDER["Keystone Electronics 1048P<br/>polarized dual-18650 holder"]
PACK_GAUGE["Analog Devices MAX17320G20+T<br/>2S protection and fuel gauge"]
PACK_ADMISSION["Texas Instruments MSPM0C1104SDGS20R<br/>local fail-closed 2S pack admission controller"]
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>single maintained low-current RUN/KILL switch"]
AON_BUCK["Texas Instruments TPS629203DRLR<br/>always-on 3.3-V safety converter"]
MAIN_BUCK["Texas Instruments TPS564252DRLR<br/>main 3.3-V converter"]
VOICE_BUCK["Texas Instruments TPS564252DRLR<br/>voice 4.0-V converter"]
EXT_BUCK["Texas Instruments TPS564252DRLR<br/>accessory 5.0-V converter"]
  PRODUCT_USB_CONNECTOR <-->|"D+/D-"| PRODUCT_USB_PROTECTOR <-->|"protected USB2 GPIO19/20"| S3
  PRODUCT_USB_CONNECTOR <-->|"CC1/CC2"| PRODUCT_USB_PROTECTOR <-->|"protected CC1/CC2"| PD_CONTROLLER
  PRODUCT_USB_CONNECTOR -->|"VBUS sink only; never source"| PD_CONTROLLER
  PRODUCT_USB_CONNECTOR -->|"VBUS shunt only"| PD_VBUS_TVS
  PD_CONTROLLER -->|"negotiated protected HV input"| NVDC_CHARGER
  PACK_HOLDER -->|"two removable cells"| PACK_GAUGE -->|"supervised 2S pack"| NVDC_CHARGER
  POWER_COMMAND_SWITCH -->|"KILL: low-current pack shutdown; never load current"| PACK_ADMISSION
  PACK_ADMISSION <-->|"local gauge admission and fault evidence"| PACK_GAUGE
  NVDC_CHARGER -->|"VSYS"| AON_BUCK
  NVDC_CHARGER -->|"VSYS"| MAIN_BUCK
  NVDC_CHARGER -->|"VSYS"| VOICE_BUCK
  NVDC_CHARGER -->|"VSYS"| EXT_BUCK
```

### RUN/KILL, watchdog, thermal supervision and physical TX evidence

```mermaid
flowchart TD
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>single maintained low-current RUN/KILL switch"]
SAFE_SUPERVISOR["TPS3808G33DBVR<br/>always-on safety-rail supervisor"]
SAFETY_CONTROLLER["Texas Instruments MSPM0C1104SDGS20R<br/>independent AON watchdog, thermal and TX-lease controller"]
SAFETY_WATCHDOG["Texas Instruments TPS3435CAKAGDDFR<br/>independent 1.6-s timeout watchdog"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>physical RUN and S3 fault-reset conditioner"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>asynchronous FAULT_KILL latch"]
SAFE_GATE_A["SN74LVC08APWR<br/>hardware permits for three nRF24 radios and their rail"]
SAFE_GATE_B["SN74LVC08APWR<br/>hardware permits for CC, voice and expansion"]
IR_SAFE_GATE["SN74LVC1G08DCKR<br/>local hardware permit for the IR carrier"]
EVIDENCE_CMP_A["TLV1824PWR<br/>UI-local physical-TX comparator for S3, C5 and IR"]
EVIDENCE_CMP_B["TLV1824PWR<br/>RF-local physical-TX comparator for 3×nRF24 and CC"]
EVIDENCE_CMP_VOICE["TLV1821DCKR<br/>dedicated RF-local physical voice-TX comparator"]
EVIDENCE_MASK["TCA9534APWR<br/>AON mask register for eight TX evidence sources"]
EVIDENCE_MAIN_ISOLATOR["SN74LVC3G07DCUR<br/>digital TX-evidence isolation into the main domain"]
  SAFE_SUPERVISOR -->|"power-on reset"| SAFE_LATCH
  POWER_COMMAND_SWITCH -->|"KILL / physical RUN edge"| SAFE_CONDITIONER
  SAFETY_CONTROLLER -->|"deadline service"| SAFETY_WATCHDOG
  SAFETY_WATCHDOG -->|"WDO_N"| SAFE_LATCH
  SAFE_CONDITIONER -->|"KILL / physical re-arm clock"| SAFE_LATCH
  SAFE_LATCH -->|"RUN_PERMIT"| SAFE_GATE_A
  SAFE_LATCH -->|"RUN_PERMIT"| SAFE_GATE_B
  SAFE_LATCH -->|"one digital permit across M1"| IR_SAFE_GATE
  EVIDENCE_CMP_A -->|"three UI-local digital evidence lines"| EVIDENCE_MASK
  EVIDENCE_CMP_B -->|"four RF-local digital evidence lines"| EVIDENCE_MASK
  EVIDENCE_CMP_VOICE -->|"one RF-local digital evidence line"| EVIDENCE_MASK
  EVIDENCE_CMP_A -->|"C5 / IR evidence"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_CMP_B -->|"hardware ANY-TX aggregate"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_CMP_VOICE -->|"hardware ANY-TX aggregate"| EVIDENCE_MAIN_ISOLATOR
```

Exact contacts are in the [pin assignment](docs/pinout.md), while signals crossing the two boards are in the [M1 map](docs/interconnect.md).

<!-- END GENERATED PRINCIPLE DIAGRAMS -->

## Safety levels

1. **Normal mode** — receive, diagnostics, maintenance and ordinary
   communications.
2. **Laboratory** — passive, defensive and constrained research tools.
3. **Laboratory → Controlled Zone** — potentially dangerous active functions
   for an isolated environment or an explicitly authorized target. Every entry
   displays a fresh mandatory warning.

The maintained `RUN/KILL` switch is the only physical admission control. Any
latched fault disables transmission and requires a real `KILL`→`RUN` cycle;
software cannot restart the device automatically. Initial setup requires
acceptance of a non-aggression agreement; it does not replace law, spectrum
licensing or the target owner's permission.

## Documentation

- [Hardware architecture and components](docs/hardware.md)
- [Device principle diagrams](docs/schematics.md)
- [Exact M1 inter-board connection](docs/interconnect.md)
- [Exact controller pin assignment](docs/pinout.md)
- [Safety, power, update and recovery](docs/safety.md)
- [Firmware capabilities and architecture](https://github.com/anton-vinogradov/esp32-leshy2-firmware)
