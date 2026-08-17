# IMP-0045 — new 3.5-inch portrait QSPI display class

- Статус: **Принято владельцем — вариант A, `DEC-0053`**
- Дата: 2026-08-17
- Decision input: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md)
- Finding: [`FND-0062`](../findings/FND-0062-old-four-inch-display-is-not-qspi.md)
- Accepted decision: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)

## Текущее состояние и причина решения

QSPI-first electrical direction уже принят. Старый 4-inch ST7796S выполняет
product workload, но является только 1-bit SPI и поэтому не использует новую
шину. Готовый честный 4-inch host-QSPI reference найден только с BT817 EVE:
он стоит около `$104`, имеет square 86-mm module и добавляет coprocessor.

Новый 3.5-inch portrait `320×480` QSPI class сохраняет привычное разрешение,
помещается в старый portrait envelope и не добавляет controller/MCU. Цена —
примерно на 23% меньшая active area, которую нужно проверить в physical UI.

## Вариант A — новый 3.5-inch portrait QSPI class

- target class: IPS, `320×480`, direct QSPI, capacitive touch;
- primary HIL: Elecrow/QDtech ST77922 reference, 300 cd/m², `-30…80°C`;
- secondary HIL: Waveshare AXS15231B 3.5B for second-controller/driver evidence;
- старый 4-inch ST7796S сохраняется как A0 control и дешёвый fallback fixture,
  но не target;
- disclosed assembly candidate `HMX035CTFT-001` не замораживается как
  production part до standalone orderability/drawing, exact connector,
  two-source, brightness/cover-lens, power, shared-SD and physical-legibility
  HIL.

Это рекомендуемый вариант: он реализует `DEC-0052` с минимальным BOM и не
ломает portrait product layout.

## Вариант B — старый 4-inch ST7796S остаётся target

Самый дешёвый и уже знакомый вариант. Но он отменяет практический смысл
зарезервированных D2/D3 и возвращает низкий full-redraw ceiling. Потребуется
явно пересмотреть `DEC-0052`; улучшение ограничится новым time quantum.

Не рекомендуется, пока direct-QSPI HIL не провалился.

## Вариант C — сохранить четыре дюйма через BT817 EVE

Crystalfontz 4-inch EVE действительно принимает host QSPI и разгружает S3, но
стоит около `$104` за модуль, имеет square `86×86 mm` body и меняет firmware/
mechanics/BOM. Это разумный high-end fallback, но не zero-loss baseline.

## Рекомендация

Принять **A**. При этом речь идёт о выборе нового screen **class**, а не о
преждевременной фиксации dev board как production part. Старый 4-inch образец
не выбрасывается и будет полезен для честного A0↔QSPI сравнения.

## Решение владельца

Владелец принял вариант **A: новый 3.5-inch portrait `320×480` QSPI IPS+touch
class, ST77922 как primary HIL, AXS15231B как secondary reference, а старый
4-inch ST7796S — только контрольный стенд и fallback**. Решение и незакрытые
production MPN gates перенесены в `DEC-0053/DSP-0004`.
