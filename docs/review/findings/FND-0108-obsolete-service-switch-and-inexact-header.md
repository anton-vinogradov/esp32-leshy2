# FND-0108 — obsolete service switch and inexact header

Статус: **исправлено в `DEC-0099`; проведено ревью выбора first target**.

## Несоответствие

`SVC-0001` называл `KMR221GULCLFS`, но актуальный authorized-distributor
поиск не дал доступного prototype quantity и показывал промышленный MOQ.
Header был записан как `FTSH-105-01-L-DV-K-TR`, хотя для автоматической сборки
выбранная keyed SMT конфигурация должна явно содержать pick-and-place pad.

## Исправление

- Шесть service controls заменены на active/mass-produced automotive
  `Alps Alpine SKQGADE010`: SPST-NO, 2.55 N, 0.25 mm travel, 100k cycles,
  `-40…90 °C`, documented low-level floor `1 V / 10 µA`.
- Три header зафиксированы как `Samtec FTSH-105-01-L-DV-K-P-TR`, где `-K`
  даёт keyed polarization, а `-P` — pick-and-place pad.
- В machine source занесены реальные 4 switch lands и все 10 контактов
  каждого header; разные физические детали не объединяются.

## Остаток

Полученные детали должны пройти footprint/coplanarity, actuator access,
recess, mating cable, insertion/retention и enclosure clearance HIL. Замена не
удаляет ни одной функции и не требует нового GPIO.

