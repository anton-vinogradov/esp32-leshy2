# DEC-0049 — nine dedicated external SMA paths

- Статус: **Принято**
- Дата: 2026-08-17
- Основание: владелец после пояснения роли второго Si4732 input подтвердил
  продолжение с рекомендованным вариантом `IMP-0041/A`
- Proposal: [`IMP-0041`](../improvements/IMP-0041-exact-external-sma-count.md), вариант A
- Evidence: [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
- Finding: [`FND-0055`](../findings/FND-0055-si4732-two-antenna-input-domains.md)

## Решение

1. Целевой base-device antenna bank содержит **девять** доступных снаружи
   SMA endpoints с постоянными identities:
   `S3-2G4`, `C5-2G4/5`, `N24-0`, `N24-1`, `N24-2`, `CC-SUB`,
   `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`.
2. Si4732 получает две независимые внешние ветви: physical `FMI` обслуживает
   `RX-FM/SW`, physical `AMI` — `RX-AM/LW`. Между ними не ставится общий
   пользовательский RF switch, а переход режима не требует переставлять одну
   antenna между двумя электрически разными frontends.
3. Девять SMA означают девять механически одинаковых внешних interfaces, но
   **не** одинаковые электрические порты. Каждый получает неснимаемую маркировку
   path/band, допустимого antenna profile и TX/RX capability.
4. `RX-AM/LW` не объявляется generic 50-ohm coax port. Baseline — короткий
   direct plug-in loop/pod либо отдельно квалифицированный transformer/buffered
   pod. Cable capacitance, ESD, pickup и sensitivity входят в обязательный
   manifest/HIL; произвольный длинный coax не допускается по умолчанию.
5. Девятый endpoint не возвращает onboard LoRa. LoRa остаётся внешним M5
   Cap/Unit со своей antenna. В адаптированной legacy geometry лишь бывшая
   позиция LoRa может быть использована для `RX-AM/LW`; это ещё не freeze
   размещения или корпуса.
6. `CC-SUB` остаётся одним целевым endpoint только при доказанном switched
   band-specific frontend. Решение о числе разъёмов не закрывает его schematic,
   matching, filter, isolation и VNA/HIL gates.

## Последствия

- восьмипортовый shared-Si4732 вариант отклонён: экономия одного connector не
  доказана как zero-loss из-за switch/parasitics, AMI sensitivity и смены
  внешней antenna;
- machine source фиксирует count и все девять identities, чтобы generator и
  firmware manifest не возвращались к generic `RX` или старому `LoRa` port;
- exact SMA gender/mounting, pigtails, protection, antenna MPNs и физическое
  размещение остаются следующей квалификацией;
- принятое число не является доказательством RF coexistence или готовности к
  KiCad.
