# CTL-0001 — slow-control budget and external-I²C fault boundary

- Статус: **Проведено ревью фактов; topology decision открыт**
- Дата: 2026-08-17
- Gate: `FLOW-0001/G2F`, control/peripheral pass
- Finding: [`FND-0052`](../findings/FND-0052-draft-maps-do-not-close-slow-control.md)
- Proposal: [`IMP-0037`](../improvements/IMP-0037-slow-control-and-external-i2c-isolation.md)

## Что именно проверено

Черновики `G2F-2R/G2F-3D` проходят проверку контактов, коллизий и полного
учёта **программируемых MCU GPIO**. Генератор пока не требует, чтобы каждый
порт `TCA9535` имел единственное семантическое назначение, и не проверяет
полноту slow-control demand. Поэтому `free_gpio.s3=[]` не доказывает, что
вся UI/audio/power/control плоскость помещается.

Текущая фактическая раскладка:

| Candidate | Портов slow expander | Уже назначено | Что не разложено по портам |
|---|---:|---:|---|
| `G2F-2R` | 16 | 5 | ordinary UI, touch policy, 2 audio selectors, card detect, STOP sense, voice status, receiver control/status, accessory isolation/status, power/fault senses |
| `G2F-3D` | 16 | 3 | тот же класс сигналов; часть voice/STOP перенесена на RP, но UI/audio selectors/accessory boundary всё равно отсутствуют |

Это не утверждает, что каждому пункту обязательно нужен отдельный expander
port. Matrix, polling, fixed-function controller, supervisor или verified
wire-OR могут уменьшить физический счёт. Но такое сжатие должно быть явно
описано и проверено, а не следовать из отсутствующей строки.

## Planning envelope до выбора exact peripherals

Ниже не final pin map, а conservative planning envelope, полученный из
reviewed функций и оставшихся exact-device развилок.

| Класс | Ожидаемые slow endpoints | Основание/вариативность |
|---|---:|---|
| ordinary UI | 6–9 | прежний проверенный набор — 9 обычных controls; diode-isolated `3×3` matrix сжимает его до 6 lines, direct wiring требует 9; физический target ещё не выбран |
| принятый audio/voice control | 5 | codec enable/reset, два independent analog selectors, voice power-down, voice high/low |
| external/display reset | 2 | U214 LoRa reset и display reset |
| status/safety observations | 3–5 | microSD detect, STOP-latch sense, voice squelch/status; receiver IRQ/status и power/fault зависят от exact devices |
| touch/receiver/accessory control | 3–6 | touch reset/IRQ policy, receiver reset/control и isolated-I²C EN/READY зависят от exact topology |

Рабочий envelope получается примерно `19…27`; центральный вариант —
`22…24`. Поэтому 16 портов не являются доказанно достаточными, а 24 порта
дают реалистичную точку следующей компоновки без увеличения MCU GPIO. Любой
более компактный вариант должен показать точную таблицу compression и HIL.

PTT, non-programmable STOP kill и actual-TX evidence в этот budget не
засчитываются: их safety function не может зависеть от slow expander.

## Latency и interrupt contract

- в активном UI обычные controls и touch могут опрашиваться по внутренней I²C;
  период и worst-case bus load должны оставить первый видимый feedback в
  пределах принятого `≤100 ms`;
- polling HIL должен поймать самый короткий принятый button pulse и каждую фазу
  выбранного encoder/detent; если это не выполняется, нужен direct IRQ либо
  dedicated local input controller, а не более оптимистичный таймер;
- IRQ touch не резервируется автоматически: он становится отдельным входом,
  только если polling не проходит latency/power/HIL;
- ordinary controls не получают скрытого wake promise. Deep-sleep wake должен
  иметь отдельный supervisor/power-button path либо доказанный expander-INT
  path; активный прибор может оставаться на polling;
- U214 `IRQ/DIO1` остаётся прямым timing endpoint: обычный LoRa IRQ status
  сохраняется до чтения/очистки, но это не основание переносить его на общий
  slow expander;
- `TCA9535/TCA6424A INT` — active-low open-drain. Изменение входа во время ACK
  может дать короткий/потерянный interrupt, поэтому INT не заменяет polling и
  source-state readback для энкодера/быстрых импульсов.

## I²C domains

U214 соединяет свои Cap-Bus `SDA/SCL` одновременно с onboard
`PI4IOE5V6408` antenna-switch controller и downstream Port A. Если эти линии
подключить напрямую к internal UI/audio bus, закороченный внешний кабель или
Unit может удержать SDA/SCL и лишить прибор внутренних controls, touch, codec
и receiver.

Проверенная candidate boundary:

1. internal `I2C0`: slow-control expander, codec, receiver и selected touch;
2. U214/Port-A branch: за powered-off-high-Z hot-swap/recovery buffer;
3. additional configurable Unit: S3 `I2C1` на GPIO7/8 либо mutually exclusive
   UART/custom profile с отдельной protection/mux qualification.

`TCA4307DGKR` — точный reference для ветви U214: 2.3–5.5 V, 400 kHz,
powered-off high-Z, `READY`, stuck-bus isolation after roughly 25–65 ms and up
to 16 recovery clocks. Он изолирует только I²C; это **не** доказательство
hot-plug всего U214, потому что SPI, UART, power/backfeed и RF-state требуют
своих gates.

## Exact reference, а не выбор компонента

`TCA6424ARGJR` проверен как один-chip 24-port reference: active part, 5×5 mm
UQFN32, 400 kHz I²C, reset и open-drain INT. Все его реальные package contacts
внесены в `devices.json`. Это доказывает существование компактного варианта,
но не выбирает его до закрытия exact touch/codec/receiver/voice/power rows.

## Recovery correction

ESP32-S3 имеет два hardware I²C controller; прежний machine source называл
GPIO7/8 только `UART0_OR_GPIO` и упускал допустимый independent `I2C1` Unit
profile. Это исправлено.

Одновременно текущие G2F-карты используют default UART0 contacts GPIO43/44 для
U214 IRQ/GNSS. Native USB Serial/JTAG + physical EN/GPIO0 BOOT остаются
независимым baseline recovery. Но UART0 нельзя объявлять сохранённым в **этих
черновиках**, пока не показаны fixture routing, accessory-off/high-Z state и
conflict isolation. Старый three-domain UART study остаётся reference, а не
доказательством active map.

## Первичные источники

- [TI TCA9535 datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf)
- [TI TCA6424A datasheet](https://www.ti.com/lit/ds/symlink/tca6424a.pdf)
- [TI TCA4307 datasheet](https://www.ti.com/lit/ds/symlink/tca4307.pdf)
- [M5Stack U214 real Cap pin map](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [ESP32-S3 I²C controller documentation](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/peripherals/i2c.html)
- [Semtech SX1262 product/datasheet page](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262)
