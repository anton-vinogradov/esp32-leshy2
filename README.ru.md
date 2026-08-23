# Leshy2 — аппаратная часть

[English](README.md) · [Прошивка](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)

> **Статус железа: H2 — production ECAD-схема.** Физический дизайн H1 принят.
> Работа над схемой начата; PCB routing и закупка заблокированы. Полный путь и
> текущая позиция показаны в [аппаратном роадмапе](docs/roadmap.ru.md).

## Роадмап и текущая позиция

Этот блок остаётся на стартовой странице до явной передачи производственных
файлов в печать/на фабрику. В [полном роадмапе](docs/roadmap.ru.md) приведены
зависимости и критерии выхода.

| Этап | Статус | Результат |
|---|---|---|
| H0 · Требования и функциональная архитектура | ✅ Проведено ревью | границы возможностей, вычислительные домены, владельцы, интерфейсы и safety rules |
| H1 · Физический дизайн устройства | ✅ Проведено ревью | принятая внешняя/внутренняя компоновка, реальные размеры, органы управления, подписи и сходящийся resource budget |
| **H2 · Production ECAD-схема** | **▶️ Сейчас** | точные symbols, pins, footprints, номиналы, nets и чистый ERC |
| H3 · Виртуальная электрическая проверка | ⏳ Ожидает H2 | power, transient, thermal, timing, RF и fault evidence |
| H4 · Объединённый pre-layout gate | 🔒 Ожидает H1–H3 и firmware F3 | закрытые виртуальные blockers и названные физические неопределённости |
| H5 · Образцы компонентов | 🔒 Ожидает H4 и одобрение стоимости | подтверждённые MPN, размеры и физическая совместимость |
| H6 · PCB placement и routing | 🔒 Ожидает H5 | проверенная разводка двух плат, DRC и manufacturing package |
| H7 · Печать прототипа и bring-up | 🔒 Ожидает H6 и одобрение заказа | платы-прототипы, rails, boot/recovery и smoke tests интерфейсов |
| H8 · Физическая квалификация | 🔒 Ожидает H7 | RF, power, thermal, safety, endurance и полный HIL 3×nRF24 |
| H9 · Производственный release | 🔒 Ожидает H8 и firmware F11 | воспроизводимый BOM/fab/test package и совместимые release tags |

**Железо находится на H2.** Production-схема создаётся; PCB layout и
target-прогонов в эмуляторах ещё нет, ни один заказ не разрешён.

### Текущая фаза H2 — детальная позиция

<!-- current-substep: H2.2.6 -->

**Точный маркер: `H2.2.6`** — реализовать и проверить точные цепи native-radio
C5, IR и внешнего service на `UI_20_C5_RADIO_IR_SERVICE`.

- ✅ `H1.8` — полный физический дизайн принят 23 августа 2026 года.
- `H2.0` — зафиксировать авторитетные входы схемы и структуру проектов.
  - ✅ `H2.0.1` — проверен полный реестр из 997 строк: 969 экземпляров
    основного устройства, 26 общих и 2 альтернативных экземпляра LoRa Cap.
  - ✅ `H2.0.2` — проверены четыре проекта, границы плат и имена цепей.
  - ✅ `H2.0.3` — проверены HW↔FW/BSP-контракт на 123 контакта и drift checks двух репозиториев.
- ✅ `H2.1` — созданы четыре независимых KiCad-проекта, 28 native-листов и
  репозиторные таблицы библиотек; пройдены parser/empty ERC в KiCad 10.
- `H2.2` — реализовать и проверить листы UI/control PCB.
  - ✅ `H2.2.1` — проверен корень UI: девять дочерних листов, 91 точная
    межлистовая цепь и 218 именованных pins/child labels; прямые rails приняты KiCad.
  - ✅ `H2.2.2` — проверен S3 core: 32 точных компонента реестра плюс граница
    встроенного U.FL модуля, все 41 контакт carrier и 39 hierarchy-интерфейсов.
  - ✅ `H2.2.3` — проверены 49 точных экземпляров display/touch/storage:
    40-контактная панель, 11 контактов microSD, защищённая подсветка,
    изоляция данных и все 17 hierarchy-интерфейсов.
  - ✅ `H2.2.4` — проверен 71 точный компонент controls/indicators: 15 серийных
    кнопок, slow/matrix I/O, thermal/ESD, девять actual-TX LED, аппаратный
    FAULT LED, 45 hierarchy-интерфейсов и три объяснённых NC-контакта.
  - ✅ `H2.2.5` — проверены 102 точных компонента codec/headset: все 21 контакт
    ES8311, шесть контактов CTIA jack, пять аналоговых селекторов,
    power/interface isolation, 24 hierarchy-интерфейса и восемь объяснённых NC.
  - ▶️ **`H2.2.6` — сейчас:** native-radio C5, IR и service paths.
  - ⏳ `H2.2.7–H2.2.10` — receiver; M1; TX safety;
    manufacturing/test points — по порядку.
- ⏳ `H2.3` — реализовать и проверить листы RF/power PCB.
- ⏳ `H2.4` — реализовать и проверить схемы display-adapter и LoRa Cap.
- ⏳ `H2.5` — независимо проверить питание, boot, recovery, quiet-state и
  `FAULT_KILL`.
- ⏳ `H2.6` — закрыть ERC и объяснить каждый намеренный no-connect.
- ⏳ `H2.7` — сверить контакты схемы с H1, M1 и firmware F2.
- 🔒 `H2.8` — формальная финальная приёмка перед H3.

Точный машиночитаемый план находится в
[`h2-schematic-plan.json`](hardware/ecad/h2-schematic-plan.json). После
закрытия подзадачи маркер и обе страницы роадмапа обновляются в том же commit.
Поздняя функциональная или физическая правка повторно открывает затронутые gates.

Leshy2 — открытый автономный прибор для наблюдения за радиоэфиром, связи,
диагностики и разрешённого исследования беспроводных и контактных систем.
Документация показывает целевое устройство: что оно умеет и как устроено.

## Что умеет устройство

- Одновременно управляет тремя полнофункциональными nRF24 в сочетаниях `3R`,
  `1T2R`, `2T1R` и `3T`.
- Работает с Wi‑Fi 2,4/5 ГГц, Bluetooth LE, ESP‑NOW, IEEE 802.15.4,
  Sub‑GHz 315/433/868/915 МГц, FM/AM/SW/LW, VHF/UHF voice и IR.
- Выводит все девять бортовых RF-трактов на разъёмы наружных сторон плат:
  два RP‑SMA и семь SMA. Ни одна антенная гребёнка не занимает межплатный канал.
- Использует [12-предметный профилированный комплект антенн](docs/antennas.ru.md):
  девять можно держать подключёнными одновременно, а сменные варианты точно
  подписаны для 315/433/868/915 МГц и VHF/UHF.
- Показывает меню, спектральный водопад и состояние трактов на вертикальном
  сенсорном IPS-дисплее 3,5″ `320×480` с прямым QSPI.
- Записывает данные и аудио на съёмную microSD, воспроизводит звук через
  динамик или CTIA-гарнитуру и принимает звук со встроенного либо гарнитурного
  микрофона.
- Поддерживает задний M5Stack U214 для LoRa RX/GNSS или точный
  [Leshy LoRa Cap](docs/lora-cap.ru.md) для evidence-qualified EU868/US915
  RX/TX, а также отдельный защищённый M5 Unit port для других модулей.
- Даёт владельцу независимые пути прошивки, восстановления и диагностики
  каждого программируемого контроллера.

## Как устроено

Внутри пять изолируемых вычислительных и управляющих доменов. `ESP32-S3-WROOM-1U-N16R8`
ведёт интерфейс, дисплей, storage и audio; `ESP32-C5-WROOM-1U-N8R8` — native
2,4/5‑ГГц radio, IEEE 802.15.4 и IR; `SC1512-A4` (RP2354B) — три nRF24,
Sub‑GHz, voice и U214; один `MSPM0C1106SDGS20R` независимо допускает батарейный
пакет, а второй ведёт watchdog, температурный контроль и разрешения TX.
Неиспользуемые интерфейсы отключаются и переводятся в проверяемое тихое состояние.

## Компоновка устройства

### Внешние и внутренние стороны плат

![Внешние стороны Leshy2](docs/images/current-clamshell.svg?layout=17)

![Внешний сервисный доступ Leshy2](docs/images/service-access.svg?layout=1)

Для пяти точных серийных кнопок навигации и их зазоров есть отдельный
машинно проверяемый чертёж размещения.

![Серийный блок навигации Leshy2](docs/images/navigation-cluster.svg?layout=1)

![Сменный переходник дисплея Leshy2](docs/images/display-adapter.svg?layout=1)

Первая проекция показывает только внешние, доступные пользователю стороны:
экран, органы управления, подписанные RF-разъёмы, индикаторы и боковые
интерфейсы. Вторая показывает две зеркально обращённые внутренние стороны и
точные устройства внутри бутерброда. Номер внутри компонента соответствует
указанным рядом точному MPN и роли. На том же чертеже показаны все пять
маршрутов/резервов RF-кабелей и семь выводов энкодера, входящих в межплатный
канал; финальная медь PCB остаётся гейтом DRC в KiCad.
На UI-плате сплошная зелёная линия — только съёмный 30-мм кабель от встроенной
U.FL модуля до платной U.FL-розетки; пунктирное синее продолжение показывает
будущую 50-омную дорожку через TX-ответвитель к наружному RP-SMA.
На RF-плате такие же физические участки кабелей трёх nRF24 показаны бирюзовым.
Концентрическое кольцо внутри каждого модуля S3/C5 — его встроенная U.FL;
пронумерованное кольцо на другом конце — отдельная платная розетка и видимая
граница кабеля с дорожкой. На каждом nRF тоже показан заявленный производителем
IPEX; его положение условно, поскольку точное поколение и ось проверяются на H5.
Каждый сплошной кабель изображён прямой 2D-проекцией между разъёмами. Выбранная
сборка имеет длину 30 мм, поэтому избыток над примерно 15-мм хордой S3/C5 — это
пространственный запас, а не последовательность прямоугольных поворотов.
Такие же синие topology-guides соединяют с подписанными антенными портами все
девять источников: S3, два входа Si4732, C5, три nRF24, CC1101 и SA518.

![Внутренние стороны плат Leshy2](docs/images/internal-board-layout.svg?layout=18)

### Вид сверху со стороны антенного торца

Настоящая верхняя проекция смотрит вдоль платы от антенн и показывает ширину,
глубину бутерброда, две антенные группы и симметричный вылет LoRa Cap.

![Вид Leshy2 сверху со стороны антенного торца](docs/images/top-edge-view.svg?layout=5)

### Разрезы бутерброда

Разрез A–A проходит через зону LoRa Cap, а B–B — через батареи и органы
управления. Разные продольные зоны не смешиваются в одной проекции.

![Разрезы бутерброда Leshy2](docs/images/sandwich-section.svg?layout=11)

<!-- BEGIN GENERATED PRINCIPLE DIAGRAMS -->

## Принципиальные связи компонентов

Архитектура читается от трёх вычислительных владельцев, а не от USB-порта.
Первая схема показывает только межпроцессорные связи; следующие схемы
разворачивают устройства каждого владельца и отдельный тракт питания.
Каждый прямоугольник — одно физическое устройство с выбранным партномером
или явной пометкой «партномер не выбран», а также его ролью в продукте.

### Карта вычислительных владельцев

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
```

### S3: интерфейс пользователя, storage, audio и native expansion

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
DISPLAY["HMX035CTFT-001 (QDtech schematic assembly marking)<br/>3,5-дюймовый QSPI экран и touch assembly"]
SD["Hirose DM3AT-SF-PEJM5<br/>push-push разъём microSD"]
SLOW_IO["TCA6424ARGJR<br/>24-линейный slow-control expander"]
UI_MATRIX_IO["TCA9539PWR<br/>16 прямых входов D-pad и функциональных кнопок"]
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
  C5 -->|"RMT TX + FAULT_KILL-qualified power"| IR_EMITTER
```

### RP: детерминированные радио, voice и Cap Bus

```mermaid
flowchart TD
RP["SC1512-A4<br/>детерминированные радио и voice"]
NRF0["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №0"]
NRF1["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №1"]
NRF2["Ebyte E01-ML01IPX<br/>полнофункциональное nRF24-радио №2"]
CC["CC1101RGPR<br/>многодиапазонный sub-GHz transceiver"]
VOICE["NiceRF SA518<br/>аналоговый VHF/UHF voice transceiver"]
U214_CONNECTOR["Samtec HLE-107-02-G-DV-PE-LC<br/>вертикальный 14-контактный host Cap-Bus на поднятой планке"]
U214["M5Stack U214 Cap LoRa-1262<br/>съёмный LoRa/GNSS Cap-модуль"]
  RP <-->|"independent PIO0 SM0"| NRF0
  RP <-->|"independent PIO0 SM1"| NRF1
  RP <-->|"independent PIO0 SM2"| NRF2
  RP <-->|"independent PIO0 SM3"| CC
  RP <-->|"UART0 + direct PTT"| VOICE
  RP <-->|"PIO1 + UART1 + I²C0"| U214_CONNECTOR
  U214_CONNECTOR <-->|"2×7 · 2.54 mm · contacts 1…14"| U214
```

### Органы управления: от физической кнопки до владельца

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
UI_MATRIX_IO["TCA9539PWR<br/>16 прямых входов D-pad и функциональных кнопок"]
UI_DPAD_UP["OMRON B3S-1100P<br/>отдельная кнопка навигации ВВЕРХ"]
UI_DPAD_DOWN["OMRON B3S-1100P<br/>отдельная кнопка навигации ВНИЗ"]
UI_DPAD_LEFT["OMRON B3S-1100P<br/>отдельная кнопка навигации ВЛЕВО"]
UI_DPAD_RIGHT["OMRON B3S-1100P<br/>отдельная кнопка навигации ВПРАВО"]
UI_DPAD_OK["OMRON B3S-1100P<br/>отдельная кнопка подтверждения OK"]
UI_SWITCH_BACK["OMRON B3S-1100P<br/>кнопка BACK"]
UI_SWITCH_OPT["OMRON B3S-1100P<br/>кнопка OPT"]
UI_SWITCH_F1["OMRON B3S-1100P<br/>левая кнопка у экрана F1"]
UI_SWITCH_F2["OMRON B3S-1100P<br/>левая кнопка у экрана F2"]
UI_SWITCH_F3["OMRON B3S-1100P<br/>левая кнопка у экрана F3"]
UI_SWITCH_F4["OMRON B3S-1100P<br/>левая кнопка у экрана F4"]
UI_SWITCH_F5["OMRON B3S-1100P<br/>правая кнопка у экрана F5"]
UI_SWITCH_F6["OMRON B3S-1100P<br/>правая кнопка у экрана F6"]
UI_SWITCH_F7["OMRON B3S-1100P<br/>правая кнопка у экрана F7"]
UI_SWITCH_F8["OMRON B3S-1100P<br/>правая кнопка у экрана F8"]
ENCODER["Alps Alpine EC11E18244AU<br/>задний энкодер с нажатием"]
PTT_SWITCH["OMRON B3S-1100P<br/>независимая задняя кнопка PTT"]
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>единственный малотоковый переключатель RUN/KILL"]
SAFETY_CONTROLLER["Texas Instruments MSPM0C1106SDGS20R<br/>независимый AON-контроллер watchdog, thermal и TX lease"]
SAFETY_WATCHDOG["Texas Instruments TPS3435CAKAGDDFR<br/>независимый timeout-watchdog 1,6 с"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>формирователь физического RUN и S3 fault reset"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>асинхронная защёлка FAULT_KILL"]
  UI_DPAD_UP -->|"direct P00"| UI_MATRIX_IO
  UI_DPAD_DOWN -->|"direct P01"| UI_MATRIX_IO
  UI_DPAD_LEFT -->|"direct P02"| UI_MATRIX_IO
  UI_DPAD_RIGHT -->|"direct P03"| UI_MATRIX_IO
  UI_DPAD_OK -->|"direct P04"| UI_MATRIX_IO
  UI_SWITCH_BACK -->|"direct P05"| UI_MATRIX_IO
  UI_SWITCH_OPT -->|"direct P06"| UI_MATRIX_IO
  UI_SWITCH_F3 -->|"direct P07"| UI_MATRIX_IO
  UI_SWITCH_F1 -->|"direct P10"| UI_MATRIX_IO
  UI_SWITCH_F2 -->|"direct P11"| UI_MATRIX_IO
  ENCODER -->|"push P12 across M1"| UI_MATRIX_IO
  UI_SWITCH_F4 -->|"direct P13"| UI_MATRIX_IO
  UI_SWITCH_F5 -->|"direct P14"| UI_MATRIX_IO
  UI_SWITCH_F6 -->|"direct P15"| UI_MATRIX_IO
  UI_SWITCH_F7 -->|"direct P16"| UI_MATRIX_IO
  UI_SWITCH_F8 -->|"direct P17"| UI_MATRIX_IO
  UI_MATRIX_IO -->|"I²C0 + IRQ"| S3
  ENCODER -->|"A/B direct PCNT"| S3
  PTT_SWITCH -->|"direct active-low PTT"| RP
  POWER_COMMAND_SWITCH -->|"physical KILL / RUN edge"| SAFE_CONDITIONER
  SAFETY_CONTROLLER -->|"deadline service"| SAFETY_WATCHDOG
  SAFETY_WATCHDOG -->|"WDO_N"| SAFE_LATCH
  SAFE_CONDITIONER -->|"KILL / physical re-arm clock"| SAFE_LATCH
```

### Аудиотракт: приём, запись, воспроизведение и передача

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
SLOW_IO["TCA6424ARGJR<br/>24-линейный slow-control expander"]
RECEIVER["Si4732-A10-GSR<br/>приёмник FM/AM/SW/LW"]
VOICE["NiceRF SA518<br/>аналоговый VHF/UHF voice transceiver"]
MICROPHONE["Same Sky CMEJ-0413-42-SMT-TR<br/>внутренний электретный микрофон"]
HEADSET_CONTROL_IO["TCA9534APWR<br/>выделенное управление гарнитурой и 7 резервных I/O"]
HEADSET_MIC_SELECTOR["Texas Instruments TS5A63157DCKR<br/>выбор встроенного/гарнитурного микрофона"]
AUDIO_RX_MUX["Texas Instruments SN74LVC1G3157DBVR<br/>выбор источника принимаемого звука"]
AUDIO_CAPTURE_SELECTOR["Texas Instruments TS5A63157DCKR<br/>выбор microphone/RX для записи"]
AUDIO_CAPTURE_BUFFER["Texas Instruments TLV9061IDBVR<br/>буфер АЦП кодека"]
CODEC["Everest Semiconductor ES8311<br/>кодек записи и воспроизведения"]
CODEC_SUPERVISOR["Texas Instruments TPS3839K33DBZR<br/>контроль готовности питания кодека"]
CODEC_I2S_DIN_BOOT_GATE["SN74LVC1G08DCKR<br/>аппаратный gate CODEC_READY AND AUDIO_ARM"]
CODEC_I2S_DIN_ISO["Texas Instruments SN74LVC1G126DCKR<br/>трёхстабильный буфер capture data на boot GPIO0"]
AUDIO_SPEAKER_SELECTOR["Texas Instruments TMUX1136DGSR<br/>выбор RX-bypass/codec для динамика"]
AUDIO_TX_SELECTOR["Texas Instruments TS5A63157DCKR<br/>выбор microphone/codec для voice TX"]
SPEAKER_AMP["Diodes Incorporated PAM8302AASCR<br/>дифференциальный усилитель динамика"]
SPEAKER["PUI Audio AS02404PO<br/>внутренний 4-Ом динамик"]
HEADPHONE_JACK["Same Sky SJ-43504-SMT-TR<br/>гарнитурный разъём 3,5 мм CTIA с detect"]
  RECEIVER -->|"FM/AM/SW/LW audio"| AUDIO_RX_MUX
  VOICE -->|"received AF"| AUDIO_RX_MUX
  AUDIO_RX_MUX -->|"selected RX"| AUDIO_CAPTURE_SELECTOR
  MICROPHONE -->|"guarded internal MIC_RAW across M1"| HEADSET_MIC_SELECTOR
  HEADPHONE_JACK -->|"CTIA sleeve microphone"| HEADSET_MIC_SELECTOR
  HEADPHONE_JACK -->|"detect-only tip switch"| SLOW_IO
  S3 -->|"I²C0 · address 0x39"| HEADSET_CONTROL_IO
  HEADSET_CONTROL_IO -->|"dedicated P0 source select"| HEADSET_MIC_SELECTOR
  HEADSET_MIC_SELECTOR -->|"selected microphone"| AUDIO_CAPTURE_SELECTOR
  AUDIO_CAPTURE_SELECTOR --> AUDIO_CAPTURE_BUFFER --> CODEC
  S3 -->|"I²S0 outputs + I²C0 control"| CODEC
  CODEC -->|"ASDOUT capture"| CODEC_I2S_DIN_ISO -->|"I²S DIN on GPIO0"| S3
  CODEC_SUPERVISOR -->|"CODEC_READY"| CODEC_I2S_DIN_BOOT_GATE
  S3 -->|"GPIO6 AUDIO_ARM; reset-low"| CODEC_I2S_DIN_BOOT_GATE
  CODEC_I2S_DIN_BOOT_GATE -->|"output enable"| CODEC_I2S_DIN_ISO
  AUDIO_RX_MUX -->|"reset-default receive bypass"| AUDIO_SPEAKER_SELECTOR
  CODEC -->|"differential playback"| AUDIO_SPEAKER_SELECTOR
  AUDIO_SPEAKER_SELECTOR -->|"differential low-level across M1"| SPEAKER_AMP
  SPEAKER_AMP -->|"filtered BTL"| SPEAKER
  CODEC -->|"stereo CTIA tip/ring1"| HEADPHONE_JACK
  HEADSET_MIC_SELECTOR -->|"internal/headset voice source"| AUDIO_TX_SELECTOR
  CODEC -->|"generated/processed voice source"| AUDIO_TX_SELECTOR
  AUDIO_TX_SELECTOR -->|"isolated microphone input"| VOICE
```

### Прошивка, восстановление и диагностика трёх вычислителей

```mermaid
flowchart TD
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
PRODUCT_USB_CONNECTOR["JAE DX07S016JA1R1500<br/>основной USB-C разъём"]
PRODUCT_USB_PROTECTOR["Texas Instruments TPD4S201RUKR<br/>защита CC и USB2 порта"]
S3_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>внутренний резервный DBG10: UART0/RESET/BOOT"]
S3_RESET_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка RESET S3"]
S3_BOOT_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка BOOT S3"]
C5["ESP32-C5-WROOM-1U-N8R8<br/>native 2,4/5 ГГц, IEEE 802.15.4 и IR"]
C5_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only USB-C восстановления C5"]
C5_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-защищённый USB2 ключ C5"]
C5_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>внутренний резервный DBG10: UART0/RESET/BOOT"]
C5_RESET_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка RESET C5"]
C5_BOOT_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка BOOT C5"]
RP["SC1512-A4<br/>детерминированные радио и voice"]
RP_SERVICE_USB_CONNECTOR["GCT USB4105-GF-A<br/>data-only USB-C восстановления RP"]
RP_SERVICE_USB_SWITCH["onsemi FSUSB42MUX<br/>power-off-защищённый USB2 ключ RP"]
RP_DBG_HEADER["Samtec FTSH-105-01-L-DV-K-P-TR<br/>внутренний резервный DBG10: SWD/RUN/USB_BOOT"]
RP_RESET_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка RUN/RESET RP"]
RP_BOOT_BUTTON["Alps Alpine SKRTLAE010<br/>внешняя боковая кнопка USB_BOOT RP"]
  PRODUCT_USB_CONNECTOR <-->|"USB2 data"| PRODUCT_USB_PROTECTOR <-->|"native USB"| S3
  S3_DBG_HEADER <-->|"UART0 + RESET + BOOT"| S3
  S3_RESET_BUTTON -->|"RESET"| S3
  S3_BOOT_BUTTON -->|"GPIO0; gated I²S_DIN only after boot"| S3
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
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
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
S3["ESP32-S3-WROOM-1U-N16R8<br/>приложение, UI, экран, storage, audio, BLE/Wi-Fi"]
PD_VBUS_TVS["Texas Instruments TVS2200DRVR<br/>шунтирующая защита VBUS 22 В"]
PD_CONTROLLER["Texas Instruments TPS25751DREFR<br/>sink-only USB-PD контроллер"]
NVDC_CHARGER["Texas Instruments BQ25798RQMR<br/>2S зарядка и NVDC power path"]
PACK_HOLDER["Keystone Electronics 1048P<br/>поляризованный держатель двух 18650"]
PACK_GAUGE["Analog Devices MAX17320G20+T<br/>защита и fuel gauge батареи 2S"]
PACK_ADMISSION["Texas Instruments MSPM0C1106SDGS20R<br/>локальный fail-closed контроллер допуска 2S pack"]
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>единственный малотоковый переключатель RUN/KILL"]
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
  POWER_COMMAND_SWITCH -->|"KILL: low-current pack shutdown; never load current"| PACK_ADMISSION
  PACK_ADMISSION <-->|"local gauge admission and fault evidence"| PACK_GAUGE
  NVDC_CHARGER -->|"VSYS"| AON_BUCK
  NVDC_CHARGER -->|"VSYS"| MAIN_BUCK
  NVDC_CHARGER -->|"VSYS"| VOICE_BUCK
  NVDC_CHARGER -->|"VSYS"| EXT_BUCK
```

### RUN/KILL, watchdog, thermal и подтверждение фактической передачи

```mermaid
flowchart TD
POWER_COMMAND_SWITCH["C&K JS102011SCQN<br/>единственный малотоковый переключатель RUN/KILL"]
SAFE_SUPERVISOR["TPS3808G33DBVR<br/>контроль always-on питания безопасности"]
SAFETY_CONTROLLER["Texas Instruments MSPM0C1106SDGS20R<br/>независимый AON-контроллер watchdog, thermal и TX lease"]
SAFETY_WATCHDOG["Texas Instruments TPS3435CAKAGDDFR<br/>независимый timeout-watchdog 1,6 с"]
SAFE_CONDITIONER["74LVC2G14GW,125<br/>формирователь физического RUN и S3 fault reset"]
SAFE_LATCH["SN74LVC1G74DCUR<br/>асинхронная защёлка FAULT_KILL"]
SAFE_GATE_A["SN74LVC08APWR<br/>аппаратные разрешения трёх nRF24 и их питания"]
SAFE_GATE_B["SN74LVC08APWR<br/>аппаратные разрешения CC, voice и расширений"]
IR_SAFE_GATE["SN74LVC1G08DCKR<br/>локальное аппаратное разрешение IR carrier"]
EVIDENCE_CMP_A["TLV1824PWR<br/>UI-компаратор фактического TX S3, C5 и IR"]
EVIDENCE_CMP_B["TLV1824PWR<br/>RF-компаратор фактического TX 3×nRF24 и CC"]
EVIDENCE_CMP_VOICE["TLV1821DCKR<br/>отдельный RF-компаратор фактического voice TX"]
U214_CONNECTOR["Samtec HLE-107-02-G-DV-PE-LC<br/>вертикальный 14-контактный host Cap-Bus на поднятой планке"]
EXT_EVIDENCE_BUFFER["SN74LVC1G07DCKR<br/>5-В-стойкая развязка evidence от LoRa Cap"]
EVIDENCE_MASK["TCA9535PWR<br/>16-битный AON-регистр маски девяти источников TX"]
EVIDENCE_OR_0["BAT54ALT1G<br/>диодное объединение evidence S3 и C5"]
EVIDENCE_OR_1["BAT54ALT1G<br/>диодное объединение evidence nRF24 №1 и №2"]
EVIDENCE_OR_2["BAT54ALT1G<br/>диодное объединение evidence nRF24 №3 и Sub-GHz"]
EVIDENCE_OR_3["BAT54ALT1G<br/>диодное объединение evidence voice и IR"]
EVIDENCE_OR_4["BAT54ALT1G<br/>диодное объединение evidence LoRa/EXT"]
EVIDENCE_MAIN_ISOLATOR["SN74LVC3G07DCUR<br/>развязка цифровых TX-свидетельств в main domain"]
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
  U214_CONNECTOR -->|"stock 5V_OUT high or qualified EXT_TX_EVIDENCE_N low"| EXT_EVIDENCE_BUFFER
  EXT_EVIDENCE_BUFFER -->|"ninth active-low evidence line"| EVIDENCE_MASK
  EVIDENCE_CMP_A -->|"C5 / IR evidence"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_CMP_A -->|"sources 0 / 1"| EVIDENCE_OR_0
  EVIDENCE_CMP_B -->|"sources 2 / 3"| EVIDENCE_OR_1
  EVIDENCE_CMP_B -->|"sources 4 / 5"| EVIDENCE_OR_2
  EVIDENCE_CMP_VOICE -->|"source 6"| EVIDENCE_OR_3
  EVIDENCE_CMP_A -->|"source 7"| EVIDENCE_OR_3
  EXT_EVIDENCE_BUFFER -->|"source 8"| EVIDENCE_OR_4
  EVIDENCE_OR_0 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_OR_1 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_OR_2 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_OR_3 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR
  EVIDENCE_OR_4 -->|"wired ANY_TX_AON_N"| EVIDENCE_MAIN_ISOLATOR
```

Точные контакты показаны в [распиновке](docs/pinout.ru.md), а прохождение сигналов между платами — в [карте M1](docs/interconnect.ru.md).

<!-- END GENERATED PRINCIPLE DIAGRAMS -->

## Безопасные уровни

1. **Основной режим** — приём, диагностика, обслуживание и обычная связь.
2. **Лаборатория** — пассивные, защитные и ограниченные исследовательские
   инструменты.
3. **Лаборатория → Контролируемая зона** — потенциально опасные active-функции
   только для изолированной среды или явно разрешённой цели. Каждый вход заново
   показывает обязательное предупреждение.

Фиксируемый переключатель `RUN/KILL` — единственный физический орган допуска.
Любая защёлкнутая авария запрещает передачу и требует настоящего цикла
`KILL`→`RUN`; программный автоматический перезапуск невозможен. При первичной
установке пользователь принимает акт о ненападении; он не заменяет закон,
лицензию на спектр и разрешение владельца цели.

## Документация

- [Роадмап и текущая позиция проекта](docs/roadmap.ru.md)
- [Аппаратная архитектура и компоненты](docs/hardware.ru.md)
- [Точный съёмный LoRa Cap](docs/lora-cap.ru.md)
- [Принципиальные схемы устройства](docs/schematics.ru.md)
- [Точное межплатное соединение M1](docs/interconnect.ru.md)
- [Точная распиновка контроллеров](docs/pinout.ru.md)
- [Память S3 и загрузочные линии](docs/memory.ru.md)
- [Безопасность, питание, обновление и восстановление](docs/safety.ru.md)
- [Возможности и архитектура прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
