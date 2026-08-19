# FND-0098 — CC1101 single-ended band switching was electrically incomplete

- Статус: **Исправлено на бумажном уровне; проведено ревью finding**
- Область: `I6 / SG-CC`
- Исправление: [`CCRF-0001`](../architecture/CCRF-0001-exact-cc1101-three-band-endpoint.md), [`DEC-0093`](../decisions/DEC-0093-exact-cc1101-three-band-endpoint.md)

## Что было не так

Старый абстрактный тракт предполагал один многопозиционный RF switch после
нескольких фильтров. Такой switch отключает ветви только с одной стороны:
невыбранные сети всё равно висят stub-нагрузками на общей точке со стороны
CC1101. Это не доказывает ни согласование, ни чувствительность, ни отсутствие
взаимного влияния 315/433/868–915-МГц цепей.

Ранее рассматривавшийся `SKY13414-485LF` также нельзя было напрямую объявлять
совместимым с 3,3-В GPIO: его допустимый control-high не совпадает с таким
упрощённым интерфейсом. Проблема была в схеме, а не в бюджете ног.

## Проверка реального свежего устройства

M5Stack публикует `Cap CC1101 (U219)` как WIP-устройство с одним RP-SMA,
CC1101, balun, тремя ветвями и **двумя** SP3T `BGS13SN8`. Это подтверждает
жизнеспособность topology «переключатель с обеих сторон фильтров» и даёт
актуальный first-pass passive coupon.

Но копировать V0.3 буквально нельзя:

- страница U219 обозначает `00/01/11` как три диапазона, тогда как официальный
  truth table `BGS13SN8` определяет `00 = isolation`, `10 = RF1`, `01 = RF2`,
  `11 = RF3`;
- в опубликованной V0.3 schematic control nets V1/V2 между двумя switch
  bodies переставлены. При одинаково нумерованных RF1/RF2/RF3 ветвях это
  может выбрать разные концы разных ветвей.

Это инженерный вывод из сопоставления двух первичных документов, а не
утверждение о серийном U219: сам M5Stack явно помечает продукт как WIP.

## Исправление

`G2F-3I` теперь использует два одинаковых
`BGS13SN8E6327XTSA1` с **одинаковыми** V1/V2 на обоих телах:

| V1/V2 | Обе стороны | Ветка |
|---|---|---|
| `00` | isolation | safe-off |
| `10` | RF1 | 315 МГц |
| `01` | RF2 | 433 МГц |
| `11` | RF3 | 868/915 МГц |

P03/P04 меняются только при выключенном `3V3_CC_SWITCHED`; отдельный
switched-rail Ioff buffer и четыре pull-down возвращают оба switch в `00`.
Один оставшийся свободный main slow-I/O contact — P05.

## Источники

- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [M5Stack Cap CC1101 U219 product page](https://docs.m5stack.com/en/cap/Cap_CC1101)
- [M5Stack Cap CC1101 V0.3 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1250/SCH_Cap_CC1101_SCH_V0.3_20260528.pdf)
- [Infineon BGS13SN8 datasheet](https://www.infineon.com/dgdl/Infineon-BGS13SN8-DataSheet-v02_04-EN.pdf?fileId=5546d462584d1d4a0158cf52e3ae03a7)

