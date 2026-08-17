# FND-0060 — abstract electrical endpoints still block final pinout

- Статус: **Открыто; current principled map complete, final electrical map blocked**
- Серьёзность: schematic/BOM/recovery/safety blocker
- Обнаружено: 2026-08-17
- Artifact: [`PIN-0003`](../architecture/PIN-0003-g2f-3i-principled-pinout.md)

## Находка

Current machine map полностью распределяет compute GPIO, controllers and slow
contacts, но часть peers остаётся `abstract:*`. Это корректно для G2F pin
feasibility и некорректно для final schematic. Наиболее существенные gaps:

- display/touch уже имеют exact current paper endpoint `HMX035CTFT-001`, но
  production orderability/drawing/connector/backlight/protection/HIL открыты;
  mono codec всё ещё не имеет принятого exact target MPN/package;
- IR frontends/driver и actual-TX evidence не заканчиваются на exact contacts;
- hard-STOP latch, power/current/thermal supervisor и load-switch/isolation
  circuits не выбраны;
- M5 Unit protection/mux, audio selectors и service connector mechanics
  остаются function boundaries;
- nRF, CC, voice and receiver electrical/RF assemblies ещё требуют source,
  voltage, reset, matching and HIL closure.

SA518, Si4732 and HMX035CTFT-001 exact contacts are now instantiated, including
SA518 update/recovery breakout and separate Si4732 FMI/AMI routes. Это
подтверждает, что список можно сокращать по реальным devices, не меняя GPIO
арифметику догадками.

## Критерий закрытия

Для каждого target-critical `abstract:*` endpoint есть exact part/package
contact либо документированная non-programmable circuit block, voltage/reset/
safe-state contract, source and test gate. Затем regenerated atlas, electrical
review and later product/physical gates pass without hidden pin allocation.
