# FND-0030 — legacy 5 V voice rail exceeds the accepted SA518 1 W profile

- Статус: **Архитектурно исправлено `DEC-0025`; открыто до схемы и conducted HIL**
- Дата: 2026-08-16
- Серьёзность: power/RF/legal architecture blocker
- Затрагивает: `DEC-0016`, `DM-VHF-01`, `BUD-0001`, current `hardware/tscircuit/audio.tsx`

## Несоответствие

`DEC-0016` принимает SA518 как 0.5/1 W target. Legacy `audio.tsx` подключает voice module к `V5`, что соответствовало прежнему SA868 artifact, но не является нейтральным выбором для SA518.

Таблица производителя SA518 v1.1 показывает:

| Supply | VHF measured | UHF measured |
|---:|---:|---:|
| 4.0 V | 30.1 dBm / 777 mA | 29.8 dBm / 901 mA |
| 5.0 V | 31.5 dBm / 1,030 mA | 31.7 dBm / 1,070 mA |

31.5–31.7 dBm — примерно 1.41–1.48 W, то есть выше принятого 1 W класса. У SA518 есть только high/low selection, а не доказанный closed-loop power regulator; software label `1 W` не исправляет supply-dependent RF output.

## Последствия

- меняются conducted power, current peak, regulator/thermal budget и региональный profile;
- один общий fixed 5 V rail не может считаться доказанным zero-loss drop-in для SA518;
- 3.3 V снижает power ниже принятого 1 W target, поэтому простое переключение на 3.3 V также неэквивалентно;
- SA868S fallback и SA518 target могут требовать разные stuffing/rail profiles.

## Closure evidence

Supply topology принята как `DEC-0025`, поэтому architecture blocker закрыт и layouts могут использовать единый power envelope. Находка остаётся implementation/HIL gate до exact regulator/load-switch/STOP implementation, per-band conducted-power/current measurement over battery/temperature/tolerance и честного profile mapping; legacy 5 V artifact не считается исправленным.

## Primary source

- [NiceRF SA518 v1.1 datasheet](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
