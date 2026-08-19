# Принципиальные схемы Leshy2

[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](schematics.md)

Схемы ниже показывают конечное устройство по функциональным доменам. Точные контакты, направления сигналов и электрические связи находятся в [публичной таблице распиновки](pinout.ru.md). Полный состав устройства — в [машинном BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).

Архитектура читается от трёх вычислительных владельцев, а не от USB-порта.
Первая схема показывает только межпроцессорные связи; следующие схемы
разворачивают устройства каждого владельца и отдельный тракт питания.
Каждый прямоугольник — одно физическое устройство с выбранным партномером
или явной пометкой «партномер не выбран», а также его ролью в продукте.

### Карта вычислительных владельцев

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
```

### S3: интерфейс пользователя, storage, audio и native expansion

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
DISPLAY["HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3,5-дюймовый QSPI экран и touch assembly"]
SD["Hirose DM3AT-SF-PEJM5<br/>push-push разъём microSD"]
SLOW_IO["TCA6424ARGJR<br/>24-линейный slow-control expander"]
UI_MATRIX_IO["TCA9534APWR<br/>матрица D-pad и функциональных кнопок"]
CODEC["Everest Semiconductor ES8311<br/>кодек записи и воспроизведения"]
RECEIVER["Si4732-A10-GSR<br/>приёмник FM/AM/SW/LW"]
  UNIT["Партномер не выбран<br/>защищённый M5 Unit port"]
  S3 -->|"direct QSPI + touch"| DISPLAY
  S3 -->|"scheduled SPI + isolated rail"| SD
  S3 <-->|"I²C0 + wired-low IRQ"| SLOW_IO
  S3 <-->|"I²C0 + wired-low IRQ"| UI_MATRIX_IO
  S3 <-->|"isolated I²S0 + I²C0"| CODEC
  S3 <-->|"isolated I²C0"| RECEIVER
  S3 <-->|"isolated profile pair"| UNIT
```

### C5: native 2,4/5 ГГц, 802.15.4 и IR

```mermaid
flowchart TD
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
IR_DEMOD["Vishay TSOP95238TT<br/>демодулирующий IR-приёмник 38 кГц"]
IR_CARRIER["Vishay TSMP95000TT<br/>IR-приёмник обучения несущей"]
IR_EMITTER["Vishay VSMY14940<br/>IR-передатчик 940 нм"]
  C5 <-->|"RMT RX0"| IR_DEMOD
  C5 <-->|"RMT RX1"| IR_CARRIER
  C5 -->|"RMT TX + STOP-qualified power"| IR_EMITTER
```

### RP: детерминированные радио, voice и U214

```mermaid
flowchart TD
RP["SC1512-A4<br/>детерминированные радио и voice"]
NRF0["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №0"]
NRF1["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №1"]
NRF2["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №2"]
CC["CC1101RGPR<br/>многодиапазонный sub-GHz transceiver"]
VOICE["NiceRF SA518<br/>аналоговый VHF/UHF voice transceiver"]
U214["M5Stack U214 Cap LoRa-1262<br/>съёмный LoRa/GNSS Cap-модуль"]
  RP <-->|"independent PIO0 SM0"| NRF0
  RP <-->|"independent PIO0 SM1"| NRF1
  RP <-->|"independent PIO0 SM2"| NRF2
  RP <-->|"independent PIO0 SM3"| CC
  RP <-->|"UART0 + direct PTT"| VOICE
  RP <-->|"PIO1 + UART1 + I²C0"| U214
```

### Питание как отдельный тракт

```mermaid
flowchart TD
PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>основной USB-C разъём"]
PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>защита CC и USB2 порта"]
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
PD_VBUS_TVS["Texas Instruments TVS2200DRVR<br/>шунтирующая защита VBUS 22 В"]
PD_CONTROLLER["Texas Instruments TPS25751DREFR<br/>sink-only USB-PD контроллер"]
NVDC_CHARGER["Texas Instruments BQ25798RQMR<br/>2S зарядка и NVDC power path"]
PACK_HOLDER["Keystone Electronics 1048P<br/>поляризованный держатель двух 18650"]
PACK_GAUGE["Analog Devices MAX17320G20+T<br/>защита и fuel gauge батареи 2S"]
AON_BUCK["Texas Instruments TPS629203DRLR<br/>always-on преобразователь безопасности 3,3 В"]
MAIN_BUCK["Texas Instruments TPS564252DRLR<br/>основной преобразователь 3,3 В"]
VOICE_BUCK["Texas Instruments TPS564252DRLR<br/>преобразователь voice 4,0 В"]
EXT_BUCK["Texas Instruments TPS564252DRLR<br/>преобразователь расширений 5,0 В"]
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

### Аппаратный STOP и подтверждение фактической передачи

```mermaid
flowchart TD
SAFE_SUPERVISOR["TPS3808G33DBVR<br/>контроль always-on питания безопасности"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>формирователь физической линии STOP"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>асинхронная защёлка STOP/RE-ARM"]
SAFE_GATE_A["SN74LVC08APWR<br/>аппаратные разрешения трёх nRF24 и их питания"]
SAFE_GATE_B["SN74LVC08APWR<br/>аппаратные разрешения CC, voice и расширений"]
IR_SAFE_GATE["SN74LVC1G08DCKR<br/>локальное аппаратное разрешение IR carrier"]
EVIDENCE_CMP_A["TLV1824PWR<br/>UI-компаратор фактического TX S3, C5 и IR"]
EVIDENCE_CMP_B["TLV1824PWR<br/>RF-компаратор фактического TX 3×nRF24 и CC"]
EVIDENCE_CMP_VOICE["TLV1821DCKR<br/>отдельный RF-компаратор фактического voice TX"]
EVIDENCE_MASK["TCA9534APWR<br/>AON-регистр маски восьми источников TX"]
EVIDENCE_MAIN_ISOLATOR["SN74LVC3G07DCUR<br/>развязка цифровых TX-свидетельств в main domain"]
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