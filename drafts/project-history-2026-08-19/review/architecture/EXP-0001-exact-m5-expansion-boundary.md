# EXP-0001 — exact M5 Cap/Unit power and signal boundary

Статус: **paper electrical endpoint проведено ревью; physical/HIL open**.

## Результат

База поддерживает одновременно два разных физических пути расширения:

1. задний 14-контактный Cap-Bus dock для exact `M5Stack U214 Cap LoRa-1262`;
2. отдельный native HY2.0-4P M5 Unit port на S3 `GPIO7/GPIO8`.

U214 также сохраняет собственный downstream Port A. Это не третий базовый
разъём и не отдельная ветвь Leshy2: его нагрузка входит в manifest и токовый
бюджет U214.

## Питание

Один `TPS564252DRLR` формирует фиксированные 5,0 В, но не соединяет внешние
разъёмы напрямую. `slow_io.P17` запрашивает U214, последний свободный `P05` —
native Unit. `74LVC1G32GV,125` объединяет запросы только для общего buck;
`SN74LVC2G08DCUR` после STOP-доминантного gate сохраняет две независимые ветви.

Каждая ветвь имеет собственный `TPS259470LRPWR`:

- true reverse blocking и latch-off;
- немедленный nominal 1,509-A current limit (`RC0402FR-072K21L`);
- `GRM155R71H472KA01D` dVdt и `GRM188R71E224KA88D` post-start timer;
- 169/47-kOhm fixed OVLO;
- отдельные `GRM21BR71E225KE11L` input/output capacitors;
- `RC0603FR-071KL` passive discharge.

U214 `5V_OUT` остаётся no-connect: он не запараллелен с `5V_IN`. Native Unit
также не может питать U214 или общий buck.

## Готовность питания

Каждую защищённую ветвь наблюдает отдельный `TPS3808G33DBVR`, питаемый от AON.
`RC0402FR-07110KL`/`RC0402FR-07220KL` переносят G33 threshold в окно valid 5 V;
`GRM155R71H103KA88D` задаёт примерно 57,6 мс typical delay. `RESET_N/READY`
подтянут через `RC0402FR-0710KL` только к `3V3_MAIN`, поэтому интерфейс не может
разрешиться при выключенном host-domain.

## U214 signal boundary

Три отдельные `74LVC126APW,118` реализуют Ioff/high-Z:

| Направление | Сигналы |
|---|---|
| RP → U214 | `LORA_RST`, `GPS_RX`, `SCK`, `MOSI`, `NSS` |
| U214 → RP | `LORA_BUSY`, `LORA_IRQ`, `GPS_TX`, `MISO` |

У каждого сигнала отдельный `ERJ-2RKF22R0X` source-series. Три физические
`TPD4E05U06DQAR` защищают все 11 наружных сигналов, включая I²C.

`TCA4307DGKR` получает полную цепь VCC/GND/100-nF bypass, controller-side
2,2-kOhm pulls, `EN=U214_READY` и читаемый `READY` на P16. Он отделяет hot-plug
и stuck-low external I²C; SPI/UART/control защищаются отдельными буферами, а не
приписываются возможностям TCA4307.

## Native Unit signal boundary

`TXS0102DCUR` питается с обеих сторон от `3V3_MAIN`; `OE=UNIT_READY` с
10-kOhm pull-down. Он поддерживает двунаправленные I²C/UART/GPIO profiles и
переходит в high-Z при OE low или потере питания. `TPD4E05U06DQAR` защищает
два сигнала; два свободных канала массива остаются no-connect. 1-Wire остаётся
обязательным specimen HIL profile: generic GPIO сам по себе не доказывает его
работу через auto-direction translator и реальный кабель.

## Admission и hot-plug

1. Оба запроса питания low; сигналы high-Z.
2. Пользователь/firmware выбирает exact signed accessory manifest.
3. Включается только нужная branch eFuse.
4. Ожидается branch READY и проверяется fault/current evidence.
5. Разрешается signal boundary и выполняется profile identity/readback.
6. Только после совпадения начинается нормальный session.

Unknown, wrong-voltage, miswired, externally powered, overcurrent или stuck-bus
accessory выключает ветвь и требует нового явного session. Автоповтор питания
после latch-off запрещён.

## Что намеренно не принято

- Presence без физического контакта не симулируется.
- Generic USB host/high-throughput reservation не возвращается. Конкретный
  будущий RF/SDR accessory должен сначала дать bandwidth/power/legal/isolation
  profile, который и выведет нужный transport.
- MPN Cap receptacle и native HY2.0-4P board connector не угадываются по виду.
  M5 не публикует manufacturer order code; нужны полученные U214/кабель,
  microscope/fit coupon, insertion/retention и installed-cap HIL.

## Бюджет

- MCU GPIO: без изменений.
- Main slow I/O: `24 used / 0 reserved / 0 free`; P05 = `UNIT_5V_REQ`.
- First-pass incremental electronics: около USD 4,5–6,5 при qty 100, без двух
  MPN-TBD connector bodies.

## Physical/HIL gates

- exact connector mate/polarity/retention и 84-mm U214 mechanics;
- shared-buck stability/current/thermal при U214 + его downstream Unit + native
  Unit по каждому разрешённому manifest;
- обе eFuse branch: inrush, OVLO, latch-off, discharge и reverse-source;
- READY threshold/delay/brownout/main-off;
- U214 SPI/UART/I²C/control timing, ESD, stuck-low и no-back-power;
- native I²C/UART/push-pull/open-drain/1-Wire и long-cable behavior;
- unknown/miswired/hot-plug/external-power fault injection;
- active expansion при quiet всех чужих signal groups и максимальной системной
  нагрузке.

## Источники

- [M5Stack Grove interface](https://docs.m5stack.com/en/learn/interface/grove)
- [M5Stack U214 product documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [Official U214 V1.1 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1208/U214-sche-Cap-LoRa1262_SCH_V1.1_20251029_2025_11_07_22_53_19.pdf)
- [TI TCA4307 datasheet](https://www.ti.com/lit/ds/symlink/tca4307.pdf)
- [TI TXS0102 datasheet](https://www.ti.com/lit/ds/symlink/txs0102.pdf)
- [TI TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
- [TI TPS3808 datasheet](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

