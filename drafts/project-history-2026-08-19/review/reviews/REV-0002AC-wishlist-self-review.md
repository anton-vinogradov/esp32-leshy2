# REV-0002AC — саморевью полного wishlist

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Входы: `INV-0001`–`INV-0003`, `AUD-0001`, `REQ-*`, `DEC-0022`
- Выходы: `INV-0004`, `DEC-0023`

## Проверки

| Проверка | Результат |
|---|---|
| Coverage legacy/additions | 125/125 leaf ID присутствуют ровно в одной `WG-*` |
| Requirement disposition | 125/125 ссылаются на reviewed `REQ-*` |
| Grouping | 9 групп оставлены: они соответствуют пользовательским подсистемам и resource-demand classes |
| Mixed extras | `W-EXTRA-06` разделён на digital voice/full-duplex; `W-EXTRA-10` — relay/heavy compute |
| Base-cost pressure | новые radio/compute/cellular/LF/NFC-frontends вынесены в optional profiles |
| Safety | Main → Lab → Controlled Zone; disruptive cases require `BOTH` and no open-air mode |
| Physical honesty | убраны universal/lossless/realtime/precision/silicon-band/fixed-gain overclaims |
| Architecture leakage | MCU owner/GPIO/bus/placement не выбраны |
| Zero-loss | deferred/optional строка не забыта и имеет activation prerequisite |
| Owner authority | владелец явно делегировал self-review и доверил инженерный disposition |

## Исправленные несоответствия

1. Digital voice не требует по определению второго RF path; требование относится только к full-duplex repeater.
2. Heavy key recovery — compute/export задача, а two-frontend NFC relay — RF/timing architecture; их нельзя оценивать одной строкой.
3. Legacy `frequency counter`, `realtime spectrum`, `full monitor`, BLE identity/distance and U214 silicon-wide bands заменены проверяемыми boundaries.
4. Опциональный внешний hardware не объявлен частью base all-in-one BOM; автономность базового продукта при этом сохраняется.

## Вывод

Группировка, полнота и dispositions пригодны как обязательный вход этапа 3. Открытых вопросов владельцу по wishlist нет; автоматическое подтверждение применено по правилу журнала и явной делегации.
