# FND-0068 — U214 physical envelope is missing from the legacy layout

- Статус: **Исправлено `PHY-0001/DEC-0057`; exact mechanics передано `FND-0069`**
- Серьёзность: product envelope / antenna-access / expansion-fit blocker
- Обнаружено: 2026-08-17
- Device: `M5Stack U214 Cap LoRa-1262`, `84.0 × 24.0 × 15.2 mm`
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)
- Paper fit: [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md)

## Несоответствие

Legacy `75 × 150 mm` clamshell рисует SMA banks по верхним кромкам и не рисует
Cardputer-compatible 14-pin Cap-Bus dock или установленный U214. Текущая
архитектура, напротив, принимает U214 как реальный external accessory и хранит
его exact envelope в `devices.json`.

Official M5Stack data подтверждают:

- корпус U214 `84.0 × 24.0 × 15.2 mm`, то есть на 9 mm шире legacy платы;
- direct Cap-Bus использует двухрядный 14-pin интерфейс и механическое
  крепление;
- LoRa имеет собственный RP-SMA и 108 × 9.3 mm antenna, GNSS — встроенную
  ceramic antenna;
- модуль нельзя включать без установленной LoRa antenna;
- на самом U214 остаётся downstream HY2.0-4P Port A.

Следовательно, «поддержать U214 электрически» недостаточно. Active physical
generator обязан показывать body, connector, screws, LoRa antenna bend,
GNSS sky-view, downstream cable и hand/desk envelope. Иначе макет может пройти
board collision checks и всё равно быть непригодным с реальным Cap.

## Исправленная граница

Старый SVG остаётся immutable reference. Его active adaptation больше не
копирует top-edge placement: `DEC-0057` закрепляет заднее расположение D.
`PD-0001` исправлен: девять onboard SMA уже приняты `DEC-0049/0050`, а U214
accessory envelope — отдельный обязательный G3 input.

Official U214/Cardputer-Adv STL alignment и scaled `PHY-0001` уже закрывают
первый paper-fit пробел для rear-above-battery candidate: `4.5 mm` side
overhang, `5.5 mm` после RF-board SMA keep-outs, `9.719 mm` до holder и
`15.11 mm` rear protrusion против `18.6 mm` bare 18650. Owner choice закрыт
вариантом D в `DEC-0057`; active generator рисует принятую working placement.
Отсутствующие exact header/boss/wall данные и installed-cap HIL выделены в
отдельный `FND-0069/MEC-0001` и не маскируются закрытием этого omission.

## Источники

- [M5Stack U214 official product documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [M5Stack official U214 structure files](https://github.com/m5stack/M5_Hardware/tree/master/Products/U214_Cap_LoRa-1262/Structures)
