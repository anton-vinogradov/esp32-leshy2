# ⚠️ Предложение IMP-0048 — U214 dock placement versus SMA banks

- Статус: **Открыто — требуется решение владельца**
- Дата: 2026-08-17
- Finding: [`FND-0068`](../findings/FND-0068-u214-envelope-missing-from-legacy-layout.md)
- Geometry baseline: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)

## Текущее состояние и причина решения

Base clamshell остаётся `75 × 150 mm`, а U214 имеет exact width 84 mm. Верхние
кромки нужны девяти external-SMA ports: рабочий split — 4 на UI-board и 5 на
RF-board, причём три nRF занимают край/центр/край для максимального разнесения.
Direct U214 dock нельзя добавлять на ту же верхнюю кромку без перестановки
антенн и повторной RF/mechanical проверки.

## Вариант A — нижний съёмный Cap bay, base width 75 mm

14-pin dock и два крепления размещаются на нижней кромке RF-board; U214
выступает наружу на 24 mm и симметрично нависает примерно на 4.5 mm с каждой
стороны. Верхние SMA banks и base-device width не меняются. Bottom service/USB
interfaces переносятся на боковые кромки и проверяются fold/cable rules.

Плюсы: нет постоянного увеличения ширины/PCB area, U214 полностью снимается,
SMA остаются сверху, RP↔U214 signals локальны на RF-board. Минусы: accessory
удлиняет устройство; нужны защита header, screw access, hand/desk и GNSS
sky-view HIL.

## Вариант B — расширить clamshell до 84 mm

U214 становится flush по ширине. Но обе PCB и корпус расширяются на 12%,
ухудшается one-hand grip и растёт постоянная стоимость даже без accessory.
Top-SMA conflict всё равно не исчезает без отдельного выбора top/bottom dock.

## Вариант C — верхний dock, SMA уводятся на боковые/плечевые грани

Даёт естественное продолжение корпуса и хороший GNSS sky-view, но разрушает
проверенную legacy top-whip геометрию, усложняет защиту девяти разъёмов и может
ухудшить разнесение трёх nRF. Требует более глубокого перепроектирования.

## Рекомендация

Принять **A** как первый active-layout candidate. Он сохраняет base product и
antenna geometry, платит объёмом только при установленном U214 и оставляет
варианты B/C доступными, если official STL collision/hand/GNSS checks не
сойдутся.

## Вопрос владельцу

Принимаем **A: 75-mm base clamshell и съёмный U214 на нижней кромке с
симметричным 4.5-mm overhang, сохраняя все девять SMA сверху**?

