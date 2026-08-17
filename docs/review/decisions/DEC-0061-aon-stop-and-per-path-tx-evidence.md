# DEC-0061 — AON hard STOP и отдельное evidence каждого TX-path

- Статус: **Принято владельцем; распространено; `I2` проведено ревью**
- Owner choice: `IMP-0050/A`
- Дата фиксации: 2026-08-18
- Exact circuit boundary: [`SAFE-0002`](../architecture/SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)
- Propagation review: [`REV-0005O`](../reviews/REV-0005O-i2-safety-decision-propagation.md)

## Решение

1. Hard STOP живёт на отдельной `AON_SAFE_3V3` и не зависит от firmware, I²C,
   expander, storage, UI или межпроцессорной связи.
2. Normally-closed STOP loop асинхронно защёлкивает `TX_KILL`; отпускание STOP
   не снимает защёлку. Новый запуск возможен только свежим физическим RE-ARM
   edge либо полным power cycle и всегда начинается с TX-off состояния.
3. `RUN_PERMIT` через отдельный Ioff triple buffer управляет S3 `CHIP_PU`, C5
   `CHIP_PU` и RP `RUN`. Потеря AON не может превратиться в разрешение запуска.
4. Два quad-AND devices независимо gate 3×nRF CE, nRF rail, CC rail, voice rail,
   IR carrier и accessory rail. Отдельный OR gate при kill принудительно держит
   active-low SA518 PTT в RX.
5. Семь onboard RF paths получают семь отдельных detectors: 5×LTC5532 для
   S3/C5/3×nRF и 2×LTC5507 для CC/voice. IR получает отдельный optical detector
   `VEMD1060X01`; drive state/current нельзя выдавать за optical output.
6. Два `TLV1824PWR` формируют восемь active-low hardware states. Один
   `TCA9534APWR` на local RP I²C0 даёт source mask без нового GPIO.
7. Четыре `BAT54ALT1G` hardware-OR states в direct `RP.GPIO22/RP_ANY_TX_N` и
   красный `LTST-C190KRKT`. Этот aggregate не зависит от MCU/I²C. Orange
   `LTST-C190KFKT` показывает latched STOP.
8. U214 или иной accessory без собственного qualified actual-TX evidence
   показывает `unknown/unavailable`; proof-mandatory mode остаётся
   disabled/fixture-only.
9. Параллельный per-path BAT15 detector coupon сохраняется как cost-down
   experiment. Он заменяет robust detectors только после равного HIL proof.

## Уточнение после принятия варианта A

Во время exact fan-out review к исходному списку варианта A добавлены:

- `SN74LVC3G34DCUR` — чтобы собственные pull-ups вычислительных модулей не
  обошли reset при потере `AON_SAFE_3V3`;
- 4×`BAT54ALT1G` — exact stocked common-anode diode arrays для physical
  aggregate;
- `LTST-C190KRKT` и `LTST-C190KFKT` — exact first-target critical indicators.

Это не новый продуктовый выбор и не расширение функции. Компоненты устраняют
конкретные электрические пробелы уже принятого A; их MPN/spec/availability
проверены до внесения в machine source.

## Последствия

- `I2` получает статус **«Проведено ревью»** на paper/electrical boundary.
- `I3` обязан дать exact source/hold-up `AON_SAFE_3V3`, rail tree, branch
  switches, current/loss/thermal/fault budget.
- `I6` обязан спроектировать и измерить taps, coupling, detector matching,
  thresholds/hysteresis, IR optical front end и BAT15 coupon.
- HIL обязан измерить STOP latency/decay, AON brownout, stuck request,
  open/short loop, back-power, false positive/negative и evidence timing.
- Ни `I2`, ни это решение не являются разрешением начать KiCad или BOM freeze;
  integrated atomic review остаётся `I9`.

## Reopen rule

Решение переоткрывается только если `I3/I6/HIL` покажут, что принятая topology
не обеспечивает safe-off/evidence при заявленных fault conditions. Желание
снизить цену само по себе не разрешает shared detector или command/current
inference вместо отдельного физического evidence.
