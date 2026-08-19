# ⚠️ Предложение IMP-0048 — U214 dock placement versus SMA banks

- Статус: **Принято D — `DEC-0057`; проведено ревью propagation**
- Дата: 2026-08-17
- Finding: [`FND-0068`](../findings/FND-0068-u214-envelope-missing-from-legacy-layout.md)
- Geometry baseline: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)
- Decision: [`DEC-0057`](../decisions/DEC-0057-u214-rear-dock-above-batteries.md)

## Текущее состояние и причина решения

Base clamshell остаётся `75 × 150 mm`, а U214 имеет exact width 84 mm. Верхние
кромки нужны девяти external-SMA ports: рабочий split — 4 на UI-board и 5 на
RF-board, причём три nRF занимают край/центр/край для максимального разнесения.
Direct U214 dock нельзя добавлять на ту же верхнюю кромку без перестановки
антенн и повторной RF/mechanical проверки.

Проверка official U214 и Cardputer-Adv STL уточнила исходную модель: U214 — не
плоская плата над обычным pin header. Его L-shaped housing охватывает торец
Cardputer-подобного rail, а установленный корпус выходит от rear datum примерно
на `15.11 mm`. Масштабированное наложение и расчёт находятся в
[`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md).

## Вариант D — задний поперечный dock над аккумуляторами, base width 75 mm

Cardputer-like raised rail с recessed female 2×7 header и двумя screw bosses
размещается на задней стороне RF half поперёк устройства. В plan view U214
занимает `84 × 15.281 mm`, симметрично нависает на `4.5 mm` с каждой стороны,
оставляет `5.5 mm` после keep-out пяти RF-board SMA и `9.719 mm` до battery
holder. Rear protrusion `15.11 mm` меньше bare-18650 silhouette `18.6 mm` на
`3.49 mm`, то есть на paper fit максимальная толщина устройства не растёт.

Плюсы: сохраняются base PCB width, девять верхних SMA и общая длина устройства;
Cap снимается, а его толщина использует уже существующий battery-backed volume.
Минусы: legacy rear encoder пересекается с Cap и должен переехать; потребуются
точные pitch/height header и bosses, локальная ступень корпуса, свободные концы
для RP-SMA/HY2.0-4P/screws и GNSS sky-view без батареи или металла.

## Вариант A — нижний съёмный Cap bay, base width 75 mm

14-pin dock и два крепления размещаются на нижней кромке RF-board; U214
выступает наружу на 24 mm и симметрично нависает примерно на 4.5 mm с каждой
стороны. Верхние SMA banks и base-device width не меняются. Bottom service/USB
interfaces переносятся на боковые кромки и проверяются fold/cable rules.

Плюсы: нет постоянного увеличения ширины/PCB area, U214 полностью снимается,
SMA остаются сверху, RP↔U214 signals локальны на RF-board. Минусы: accessory
удлиняет устройство; нужны защита header, screw access, hand/desk и GNSS
sky-view HIL. После появления rear candidate этот вариант остаётся fallback,
но уже не является рекомендуемым.

## Вариант B — расширить clamshell до 84 mm

U214 становится flush по ширине. Но обе PCB и корпус расширяются на 12%,
ухудшается one-hand grip и растёт постоянная стоимость даже без accessory.
Top-SMA conflict всё равно не исчезает без отдельного выбора top/bottom dock.

## Вариант C — верхний dock, SMA уводятся на боковые/плечевые грани

Даёт естественное продолжение корпуса и хороший GNSS sky-view, но разрушает
проверенную legacy top-whip геометрию, усложняет защиту девяти разъёмов и может
ухудшить разнесение трёх nRF. Требует более глубокого перепроектирования.

## Рекомендация

Принять **D** как первый active-layout candidate. Это единственный проверенный
на масштабе вариант, который одновременно сохраняет ширину и длину base device,
верхнюю antenna geometry и не увеличивает его максимальную battery-defined
толщину на paper fit. Вариант A оставить механическим fallback, если exact
dock/specimen или installed-cap hand/GNSS/RF HIL опровергнут D.

## Вопрос владельцу

Владелец ответил **D**. Задний поперечный dock над аккумуляторами принят как
единственный active working layout. `MEC-0001/FND-0069` сохраняют exact
connector/rail/screw/specimen gate; вариант A остаётся только fallback при
провале real-device HIL.
