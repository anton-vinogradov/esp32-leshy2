# Leshy2 principle diagrams

[Home](../README.md) · [Hardware](hardware.md) · [Русский](schematics.ru.md)

The diagrams below describe the finished device by functional domain. Exact contacts, signal directions and electrical connections are in the [public pin table](pinout.md). The complete device content is in the [machine-readable BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).

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
UI_MATRIX_IO["TCA9534APWR<br/>D-pad and function-key matrix expander"]
CODEC["Everest Semiconductor ES8311<br/>audio capture and playback codec"]
RECEIVER["Si4732-A10-GSR<br/>FM/AM/SW/LW broadcast receiver"]
  UNIT["Part number not selected<br/>protected M5 Unit port"]
  S3 -->|"direct QSPI + touch"| DISPLAY
  S3 -->|"scheduled SPI + isolated rail"| SD
  S3 <-->|"I²C0 + wired-low IRQ"| SLOW_IO
  S3 <-->|"I²C0 + wired-low IRQ"| UI_MATRIX_IO
  S3 <-->|"isolated I²S0 + I²C0"| CODEC
  S3 <-->|"isolated I²C0"| RECEIVER
  S3 <-->|"isolated profile pair"| UNIT
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
  C5 -->|"RMT TX + STOP-qualified power"| IR_EMITTER
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
U214["M5Stack U214 Cap LoRa-1262<br/>removable LoRa/GNSS Cap module"]
  RP <-->|"independent PIO0 SM0"| NRF0
  RP <-->|"independent PIO0 SM1"| NRF1
  RP <-->|"independent PIO0 SM2"| NRF2
  RP <-->|"independent PIO0 SM3"| CC
  RP <-->|"UART0 + direct PTT"| VOICE
  RP <-->|"PIO1 + UART1 + I²C0"| U214
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
  NVDC_CHARGER -->|"VSYS"| AON_BUCK
  NVDC_CHARGER -->|"VSYS"| MAIN_BUCK
  NVDC_CHARGER -->|"VSYS"| VOICE_BUCK
  NVDC_CHARGER -->|"VSYS"| EXT_BUCK
```

### Hardware STOP and physical transmission evidence

```mermaid
flowchart TD
SAFE_SUPERVISOR["TPS3808G33DBVR<br/>always-on safety-rail supervisor"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>physical STOP-loop conditioner"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>asynchronous STOP/RE-ARM latch"]
SAFE_GATE_A["SN74LVC08APWR<br/>hardware permits for three nRF24 radios and their rail"]
SAFE_GATE_B["SN74LVC08APWR<br/>hardware permits for CC, voice and expansion"]
IR_SAFE_GATE["SN74LVC1G08DCKR<br/>local hardware permit for the IR carrier"]
EVIDENCE_CMP_A["TLV1824PWR<br/>UI-local physical-TX comparator for S3, C5 and IR"]
EVIDENCE_CMP_B["TLV1824PWR<br/>RF-local physical-TX comparator for 3×nRF24 and CC"]
EVIDENCE_CMP_VOICE["TLV1821DCKR<br/>dedicated RF-local physical voice-TX comparator"]
EVIDENCE_MASK["TCA9534APWR<br/>AON mask register for eight TX evidence sources"]
EVIDENCE_MAIN_ISOLATOR["SN74LVC3G07DCUR<br/>digital TX-evidence isolation into the main domain"]
  SAFE_SUPERVISOR -->|"power-on reset"| SAFE_LATCH
  SAFE_CONDITIONER -->|"STOP assertion"| SAFE_LATCH
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