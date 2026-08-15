# DEC-0006 — внешний GNSS через M5Stack Unit GPS v1.1

- Статус: **Принято владельцем проекта**
- Этап: 2 — scope; электрическая реализация проверяется на этапах 3–6
- Дата принятия: 2026-08-15
- Закрывает: `FND-0004`
- Затрагивает: `C-GPS-*`, expansion, BOM, питание, корпус и firmware

## Решение

Бортовой GNSS удаляется из нового Leshy2. Навигационные функции реализуются внешним M5Stack Unit через отдельный M5-compatible UART-разъём.

Первичная поддерживаемая модель — **M5Stack Unit GPS v1.1 `U032-V11`**. Старый `U032` не является целевым вариантом: производитель пометил его EOL и рекомендует v1.1.

Наличие GNSS-функций в UI условно подключённым аксессуаром. В контексте принятого all-in-one это означает один основной прибор с поддерживаемыми расширениями, а не обязательное размещение каждого сенсора на основной PCB.

## Контракт будущего UART-порта

- физический интерфейс: HY2.0-4P в формате M5Stack `PORT.C`;
- питание Unit: защищённые и управляемые `+5 V` и GND, не legacy `+3.3 V`;
- данные: host TX → Unit RX и Unit TX → host RX;
- первичный профиль: `115200 8N1`, NMEA 0183 4.1;
- заложить ESD/series protection и безопасное поведение при подключении/отключении;
- подтвердить logic levels, startup/inrush current и hot-plug режим измерением до фиксации схемы;
- legacy-кандидат S3 UART2 на GPIO18/GPIO47 проверяется на этапе 3 и пока не считается окончательной pin map.

Официальная спецификация указывает потребление `5 V / 31.64 mA`; точный бюджет порта выбирается с запасом только после измерения запуска. Порт может использоваться другими M5 UART Units лишь после отдельной проверки питания, уровней, протокола и firmware — blanket-совместимость со всем каталогом M5 не обещается.

## Стоимость

- из base BOM уходят SAM-M8Q, backup supercap/Schottky и GNSS-развязка;
- добавляются UART Grove connector и его power/protection;
- на 2026-08-15 официальный M5Stack store указывает `$9.95` за `U032-V11`, но статус — out of stock;
- экономия base device ожидается, а стоимость полного набора с внешним Unit должна считаться отдельно по `DEC-0005`.

## Источники

- [M5Stack Unit GPS v1.1 documentation](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [M5Stack Grove/PORT.C convention](https://docs.m5stack.com/en/learn/interface/grove)
- [M5Stack Unit GPS v1.1 store page](https://shop.m5stack.com/products/gps-bds-unit-v1-1-at6668)
- [M5Stack legacy Unit GPS — EOL](https://shop.m5stack.com/products/mini-gps-bds-unit)

Удаление legacy-компонентов из tsCircuit выполняется не сейчас, а при регенерации схем из проверенной спецификации на этапе 8.
