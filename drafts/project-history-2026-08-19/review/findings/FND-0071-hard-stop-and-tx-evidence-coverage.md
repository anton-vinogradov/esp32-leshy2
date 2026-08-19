# FND-0071 — hard STOP и actual-TX evidence не покрывают актуальную архитектуру

- Статус: **Paper mismatch закрыт `DEC-0061/SAFE-0002`; `I3/I6/HIL` proof открыт**
- Серьёзность: **критичный safety prerequisite для любого TX**
- Обнаружено: 2026-08-17
- Этап: [`INT-0001/I2`](../architecture/INT-0001-internal-design-closure-sequence.md)
- Затрагивает: `DEC-0024`, `IMP-0022`, `FND-0007`, `RES-0001`, `G2F-3I`,
  hardware, firmware и HIL

## Наблюдение 1 — старое решение осталось двухдоменным

`DEC-0024` и исходный `IMP-0022` были написаны для «обоих MCU»: STOP
удерживал в reset только ESP32-S3 и ESP32-C5. Актуальная рабочая архитектура
имеет третий программируемый домен `RP2354B`; он непосредственно управляет
3×nRF24, CC1101, voice и U214. Оставить его работающим при hard STOP означает
оставить активным именно владельца большинства внешних TX-paths.

Более поздний candidate `PKG-0001` уже требует, чтобы STOP управлял `RUN`
RP2354, но эта поправка не была распространена обратно в нормативный
`DEC-0024/FND-0007`. Документационная часть несоответствия исправлена:
актуальный hard STOP обязан одновременно доминировать над S3 `CHIP_PU`, C5
`CHIP_PU`, RP `RUN` и каждым внешним TX gate/rail.

## Наблюдение 2 — четыре onboard RF-path не имеют фактического evidence

До исправления `DEC-0061` в `G2F-3I` были только следующие evidence endpoints:

| Path | Current endpoint | Что доказано сейчас |
|---|---|---|
| C5 2.4/5 GHz | `C5.GPIO23 / C5_RF_TX_EVIDENCE` | только зарезервирован GPIO и abstract detector |
| IR | `C5.GPIO24 / IR_TX_EVIDENCE` | только зарезервирован GPIO и abstract optical detector |
| voice VHF/UHF | `RP.GPIO22 / VOICE_TX_EVIDENCE` | только зарезервирован GPIO и abstract detector |
| S3 2.4 GHz | `slow_io.P23 / S3_RF_TX_EVIDENCE` | только slow input и abstract detector |
| nRF0 / nRF1 / nRF2 | отсутствует | `CE`, ток или command state не являются RF evidence |
| CC1101 | отсутствует | power/state/GDO не являются RF evidence |

Следовательно, accepted требование source-identifiable actual-TX для трёх
одновременных nRF и CC сейчас невозможно выполнить. Общий current sensor или
состояние программного arbiter не устраняют этот пробел: они могут обнаружить
аномалию, но не доказывают излучение конкретного RF path.

## Наблюдение 3 — U214 нельзя честно измерить на base board

RF-тракт, PA и антенна M5Stack `U214` находятся на съёмном Cap. Через rear dock
не проходит RF feed, на который base board могла бы поставить калиброванный
detector. Near-field pickup рядом с Cap не является source-specific proof при
работающих соседних радио.

Поэтому U214/later accessory без собственного квалифицированного hardware
evidence должен показывать `unknown/unavailable`. Профиль, которому требуется
физическое доказательство TX, остаётся fixture-only/disabled до появления
такого evidence; command/current нельзя переименовывать в actual-TX.

## Требуемое исправление

1. Выбрать AON-powered, non-programmable STOP latch/supervisor/gate topology
   с доминированием над всеми тремя compute domains.
2. Дать каждому из семи onboard RF TX-path отдельный detector и IR — отдельный
   optical detector.
3. Сохранить независимый от MCU/I²C физический `ANY_TX`, а программному
   arbiter передать source mask без добавления свободного RP GPIO.
4. Для detector front ends выбрать exact first-target MPN, а RF tap/coupling,
   thresholds, temperature envelope и false-positive/false-negative limits
   явно оставить измеряемым `I6/HIL`, а не угадывать.
5. Проверить STOP при active TX, зависании каждого MCU, stuck request,
   I²C/expander fault, brownout, loss of AON, reset/update и accessory fault.

Варианты и рекомендуемое исправление опубликованы в
[`SAFE-0001`](../architecture/SAFE-0001-aon-stop-and-tx-evidence-options.md) и
[`IMP-0050`](../improvements/IMP-0050-aon-stop-and-per-path-tx-evidence.md).
Вариант принят и exact topology распространена в machine source/diagrams;
`REV-0005O` провёл отдельное paper review. Поэтому архитектурная часть находки
закрыта. Измерительная часть остаётся открытой до `I3/I6/HIL` с заранее
указанными pass conditions и не выдаётся за доказанное product behavior.
