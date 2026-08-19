# DEC-0057 — U214 rear dock above the batteries

- Статус: **Принято владельцем; проведено ревью propagation**
- Дата: 2026-08-17
- Owner answer: `D`
- Proposal: [`IMP-0048`](../improvements/IMP-0048-u214-dock-versus-sma-placement.md)
- Paper fit: [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md)
- Mechanical facts: [`MEC-0001`](../product-design/MEC-0001-u214-cap-bus-mechanical-interface.md)
- Propagation review: [`REV-0005I`](../reviews/REV-0005I-u214-rear-dock-decision-propagation.md)

## Решение

M5Stack `U214 Cap LoRa-1262` устанавливается съёмно поперёк задней стороны RF
half над аккумуляторами. Base clamshell остаётся `75 × 150 mm`; U214 шириной
`84 mm` симметрично нависает на `4.5 mm` с каждой стороны.

Рабочий dock воспроизводит функциональную механику Cardputer-Adv:

1. host-side female `2×7`, `2.54-mm` Cap-Bus receptacle на задней mating plane;
2. два M2 retention points с `56-mm` centre pitch и симметричными `14-mm`
   offsets от торцов U214;
3. локальный rail/step, который принимает неплоский L-shaped корпус U214;
4. доступ к U214 RP-SMA, HY2.0-4P и крепежу;
5. свободная зона над встроенной GNSS ceramic antenna.

Legacy rear encoder не наследуется на прежнем месте: он пересекается с U214 и
обязан переехать при следующей общей компоновке органов управления.

## Что решение не закрывает

- exact host-receptacle MPN и footprint;
- mating depth, rail height, screw length/thread engagement и wall tolerances;
- установленный Cap в hand/desk/drop/strain/GNSS/RF HIL;
- окончательную форму корпуса и место перенесённого encoder.

`MEC-0001/FND-0069` удерживают эти пункты открытыми. Вариант A с нижним dock
остаётся fallback только если real-device HIL опровергнет D; он больше не
является параллельным active candidate.
