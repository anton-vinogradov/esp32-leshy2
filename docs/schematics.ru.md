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
UNIT_CONNECTOR["1125R-SMT-4P<br/>защищённый разъём M5 Unit HY2.0-4P"]
  S3 -->|"direct QSPI + touch"| DISPLAY
  S3 -->|"scheduled SPI + isolated rail"| SD
  S3 <-->|"I²C0 + wired-low IRQ"| SLOW_IO
  S3 <-->|"I²C0 + wired-low IRQ"| UI_MATRIX_IO
  S3 <-->|"isolated I²S0 + I²C0"| CODEC
  S3 <-->|"isolated I²C0"| RECEIVER
  S3 <-->|"isolated profile pair"| UNIT_CONNECTOR
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

### Органы управления: от физической кнопки до владельца

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
UI_MATRIX_IO["TCA9534APWR<br/>матрица D-pad и функциональных кнопок"]
UI_SWITCH_UP["C&K Y78B23214FP<br/>контакт ↑ под единой крестовиной D-pad"]
UI_SWITCH_DOWN["C&K Y78B23214FP<br/>контакт ↓ под единой крестовиной D-pad"]
UI_SWITCH_LEFT["C&K Y78B23214FP<br/>контакт ← под единой крестовиной D-pad"]
UI_SWITCH_RIGHT["C&K Y78B23214FP<br/>контакт → под единой крестовиной D-pad"]
UI_SWITCH_OK["C&K Y78B23214FP<br/>центральный контакт OK единого D-pad"]
UI_SWITCH_BACK["C&K Y78B23214FP<br/>кнопка BACK"]
UI_SWITCH_OPT["C&K Y78B23214FP<br/>кнопка OPT"]
UI_SWITCH_F1["C&K Y78B23214FP<br/>задняя функциональная кнопка F1"]
UI_SWITCH_F2["C&K Y78B23214FP<br/>задняя функциональная кнопка F2"]
ENCODER["Alps Alpine EC11E18244AU<br/>задний энкодер с нажатием"]
PTT_SWITCH["C&K Y78B23214FP<br/>независимая задняя кнопка PTT"]
STOP_SWITCH["Panasonic AEQ10410<br/>нормально-замкнутая аппаратная кнопка STOP"]
REARM_SWITCH["C&K Y78B23214FP<br/>утопленная аппаратная кнопка RE-ARM"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>формирователь физической линии STOP"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>асинхронная защёлка STOP/RE-ARM"]
  UI_SWITCH_UP -->|"R0/C0"| UI_MATRIX_IO
  UI_SWITCH_DOWN -->|"R0/C1"| UI_MATRIX_IO
  UI_SWITCH_LEFT -->|"R0/C2"| UI_MATRIX_IO
  UI_SWITCH_RIGHT -->|"R1/C0"| UI_MATRIX_IO
  UI_SWITCH_OK -->|"R1/C1"| UI_MATRIX_IO
  UI_SWITCH_BACK -->|"R1/C2"| UI_MATRIX_IO
  UI_SWITCH_OPT -->|"R2/C0"| UI_MATRIX_IO
  UI_SWITCH_F1 -->|"R2/C1"| UI_MATRIX_IO
  UI_SWITCH_F2 -->|"R2/C2"| UI_MATRIX_IO
  ENCODER -->|"push R3/C0"| UI_MATRIX_IO
  UI_MATRIX_IO -->|"I²C0 + IRQ"| S3
  ENCODER -->|"A/B direct PCNT"| S3
  PTT_SWITCH -->|"direct active-low PTT"| RP
  STOP_SWITCH -->|"fail-open STOP loop"| SAFE_CONDITIONER
  REARM_SWITCH -->|"fresh physical edge"| SAFE_CONDITIONER
  SAFE_CONDITIONER -->|"asynchronous set/clock"| SAFE_LATCH
```

### Аудиотракт: приём, запись, воспроизведение и передача

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
RECEIVER["Si4732-A10-GSR<br/>приёмник FM/AM/SW/LW"]
VOICE["NiceRF SA518<br/>аналоговый VHF/UHF voice transceiver"]
MICROPHONE["Same Sky CMEJ-0413-42-SMT-TR<br/>внутренний электретный микрофон"]
AUDIO_RX_MUX["Texas Instruments SN74LVC1G3157DBVR<br/>выбор источника принимаемого звука"]
AUDIO_CAPTURE_SELECTOR["Texas Instruments TS5A63157DCKR<br/>выбор microphone/RX для записи"]
AUDIO_CAPTURE_BUFFER["Texas Instruments TLV9061IDBVR<br/>буфер АЦП кодека"]
CODEC["Everest Semiconductor ES8311<br/>кодек записи и воспроизведения"]
AUDIO_SPEAKER_SELECTOR["Texas Instruments TMUX1136DGSR<br/>выбор RX-bypass/codec для динамика"]
AUDIO_TX_SELECTOR["Texas Instruments TS5A63157DCKR<br/>выбор microphone/codec для voice TX"]
SPEAKER_AMP["Diodes Incorporated PAM8302AASCR<br/>дифференциальный усилитель динамика"]
SPEAKER["PUI Audio AS02404PO<br/>внутренний 4-Ом динамик"]
HEADPHONE_JACK["Same Sky SJ1-3515-SMT-TR<br/>выход наушников 3,5 мм с detect"]
  RECEIVER -->|"FM/AM/SW/LW audio"| AUDIO_RX_MUX
  VOICE -->|"received AF"| AUDIO_RX_MUX
  AUDIO_RX_MUX -->|"selected RX"| AUDIO_CAPTURE_SELECTOR
  MICROPHONE -->|"local voice/capture"| AUDIO_CAPTURE_SELECTOR
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

### Прошивка, восстановление и диагностика трёх вычислителей

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>основной USB-C разъём"]
PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>защита CC и USB2 порта"]
S3_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>ключевой DBG10: UART0/RESET/BOOT"]
S3_RESET_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка RESET S3"]
S3_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка BOOT S3"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
C5_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only USB-C восстановления C5"]
C5_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-защищённый USB2 ключ C5"]
C5_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>ключевой DBG10: UART0/RESET/BOOT"]
C5_RESET_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка RESET C5"]
C5_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка BOOT C5"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
RP_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only USB-C восстановления RP"]
RP_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-защищённый USB2 ключ RP"]
RP_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>ключевой DBG10: SWD/RUN/USB_BOOT"]
RP_RESET_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка RUN/RESET RP"]
RP_BOOT_BUTTON["Alps Alpine SKQGADE010<br/>технологическая кнопка USB_BOOT RP"]
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

### Девять независимых антенных портов

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R2<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
S3_EXTERNAL_RP_SMA["GCT RFPC-SMA32-FN-175-A<br/>внешний RP-SMA порт S3 2,4 ГГц"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
C5_EXTERNAL_RP_SMA["GCT RFPC-SMA32-FN-175-A<br/>внешний RP-SMA порт C5 2,4/5 ГГц"]
RECEIVER["Si4732-A10-GSR<br/>приёмник FM/AM/SW/LW"]
RECEIVER_FMSW_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>приёмный SMA порт FM/SW"]
RECEIVER_AMLW_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>не-50-омный SMA порт AM/LW loop/pod"]
NRF0["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №0"]
NRF0_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>независимый SMA порт nRF24 №0"]
NRF1["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №1"]
NRF1_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>независимый SMA порт nRF24 №1"]
NRF2["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №2"]
NRF2_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>независимый SMA порт nRF24 №2"]
CC["CC1101RGPR<br/>многодиапазонный sub-GHz transceiver"]
CC_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>многодиапазонный SMA порт sub-GHz"]
VOICE["NiceRF SA518<br/>аналоговый VHF/UHF voice transceiver"]
VOICE_EXTERNAL_SMA["GCT RFPC-SMA31-FN-175-A<br/>SMA порт VHF/UHF voice"]
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
PACK_ADMISSION["Texas Instruments MSPM0C1104SDGS20R<br/>локальный fail-closed контроллер допуска 2S pack"]
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>малотоковый фиксируемый переключатель ON/OFF"]
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
  POWER_COMMAND_SWITCH -->|"low-current ON/OFF request; never load current"| PACK_ADMISSION
  PACK_ADMISSION <-->|"local gauge admission and fault evidence"| PACK_GAUGE
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