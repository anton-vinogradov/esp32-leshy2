# DEC-0054 — fail-safe complete audio path

- Статус: **Принято владельцем; архитектура проведена ревью, schematic/HIL открыт**
- Дата: 2026-08-17
- Owner answer: `A` / «пробуй» после подробного сравнения
- Proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)
- Facts: [`AUDIO-0002`](../architecture/AUDIO-0002-complete-audio-path-comparison.md)
- Propagation review: [`REV-0005D`](../reviews/REV-0005D-audio-decision-propagation.md)

## Решение

Для первого прототипа принимается полный вариант `IMP-0046/A`:

| Партномер | Роль в принятом тракте |
|---|---|
| `ES8311` | mono ADC/DAC codec на существующих S3 I2S0/I2C0 routes |
| `SN74LVC1G3157DBVR` | выбор RX-источника: Si4732 mono или SA518 AFOUT |
| `TLV9061IDBVR` | активный high-impedance buffer, не нагружающий обычный speaker bypass |
| `TMUX1136DGSR` | dual-SPDT выбор differential speaker source |
| `TS5A63157DCKR` | отдельный выбор electret или attenuated codec TX-audio |
| `SN74LVC2G08DCUR` | аппаратное маскирование stale P11/P12 до явного arm |
| `PAM8302AASCR` | differential-input mono Class-D speaker amplifier |

`TCA6424ARGJR P27` выбирает Si4732/SA518 receive source. `P11/P12` остаются
только requests для speaker/TX codec positions. Прямой S3 `GPIO6` становится
active-high `AUDIO_ARM` и получает внешний pull-down. Пока `AUDIO_ARM=0`,
`SN74LVC2G08DCUR` принудительно оставляет speaker на analog bypass, а SA518
TX-audio — на electret, даже если expander удерживает старые единицы после
reset/watchdog/brownout.

PTT остаётся отдельным независимым hard-stop-dominated трактом. Ни codec DAC,
ни selector state сами по себе не могут включить передачу.

## Стоимость и варианты набивки

Первый прототип получает populated `TLV9061IDBVR` path и одновременно DNP
площадки для passive E1-P capture. Удалить buffer из production BOM можно
только после сравнения обеих набивок на одной плате по bypass delta, record
SNR/THD, low-frequency response, clipping и RF immunity. Это cost-down gate,
а не обещанная экономия.

`TAC5111IRGER` остаётся comparison reference и не входит в baseline: он дороже,
требует нового firmware driver и не устраняет external fail-safe selectors.

## Pin/resource consequence

- S3: `32 used / 3 reserved / 1 free`; свободен только `GPIO43`.
- C5: `14/6/1`, без изменения.
- RP2354B: `48/0/0`, без изменения.
- TCA6424ARGJR: `24 used / 0 reserved / 0 free`.

## Что принято и что ещё не принято

Приняты topology class, exact prototype IC order codes, roles, digital control
ownership, reset default и pin accounting. Не приняты как готовая схема:

- номиналы coupling/bias/filter/attenuator/gain сетей и rail partition;
- exact microphone, speaker, power-switch and hard-PTT MPN;
- footprints, alternates, lifecycle/AVL and production price;
- powered-off loading, common mode, pop/click, RF immunity and thermal result;
- осциллограммы reset/brownout/watchdog/stale-expander и полный HIL.

До закрытия этих пунктов решение не разрешает frozen schematic/BOM или KiCad
layout sign-off.

