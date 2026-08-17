# FND-0055 — legacy Si4732 SMA hides two antenna input domains

- Статус: **Port decision исправлен `DEC-0049`; frontend/HIL closure открыт**
- Серьёзность: RF sensitivity / mechanical interface / acceptance blocker
- Обнаружено: 2026-08-17
- Затрагивает: legacy layout generator, `RF-RX`, SMA count, enclosure labels,
  Si4732 frontend/HIL
- Evidence: [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
- Proposal: [`IMP-0041`](../improvements/IMP-0041-exact-external-sma-count.md)

## Несоответствие

Legacy mockup рисует один generic `Si4732` SMA и описывает его как один
телескопический HF/CB/FM port. У exact `Si4732-A10-GS` на реальном SOIC16
выведены разные RF pins:

- pin 1 `FMI` — `FM/SW ANT`;
- pin 2 `RFGND`;
- pin 3 `AMI` — `AM/LW ANT`.

Один нарисованный SMA не задаёт, как сохраняются обе ветви, какая antenna
подключена, как переключается frontend и как выдерживается AMI capacitance.
Поэтому legacy count нельзя перенести как доказанную электрическую схему.

## Почему это materially важно

- FM/SW whip и AM/LW ferrite/air loop имеют разные electrical interfaces.
- related Skyworks Si473x guidance показывает жёсткую зависимость AMI tuning
  от total parasitic capacitance; exact Si4732 limit ещё требуется, поэтому
  обычный длинный coax нельзя принять без измерений.
- generic port label провоцирует неподходящую antenna и ложную оценку
  чувствительности.
- объединение pins без exact switch/matching/protection network не является
  допустимым исправлением.

## Выполненное исправление

- [`RFQ-0001`](../architecture/RFQ-0001-zero-based-rf-zoning-coexistence.md)
  теперь описывает `RF-RX` как один receiver session с двумя input domains;
- [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
  пересчитывает банк по реальным устройствам;
- legacy generator остаётся immutable draft; `DEC-0049` требует два labelled
  ports в его будущей active адаптации.

## Критерий закрытия

Exact endpoint count закрыт `DEC-0049`. Находка полностью закрывается после
проверки обоих Si4732 frontends на выбранных antennas/cables: sensitivity, tuning range,
noise pickup, ESD, insertion/parasitic loss, mode transition и coexistence.

## Первичные источники

- [Skyworks Si4732-A10 short datasheet](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [Skyworks AN383 antenna/layout guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf)
