# FND-0011 — текущий SA868 стартовал с floating PTT/PD и аппаратной высокой мощностью

- Статус: **Исправлено консервативно в tsCircuit; проведено prerequisite-review в текущем SA868-срезе**
- Серьёзность: safety blocker для любого SA868 TX
- Затрагивает: `DEC-0003`, `FND-0007`, `IMP-0010`, `C-VHF-01`–`C-VHF-07`, stage-3 pin/safety budget
- Обнаружено и исправлено: 2026-08-16

## Несоответствие

NiceRF определяет:

- `PTT=0` — передача, `PTT=1` — приём;
- `PD=0` — power-down, `PD=1` — normal work;
- `H/L=open` — высокая мощность, `H/L=low` — низкая; подавать VDD/CMOS-high на `H/L` запрещено.

Текущий `hardware/tscircuit/audio.tsx` напрямую подключал `PTT` и `PD` к PCA9555 без внешних safe-state resistors, а `H/L` намеренно оставлял open. До инициализации expander либо при его reset выходы не давали независимого гарантированного состояния; H/L аппаратно выбирал high-power. Это противоречит `DEC-0003`, по которому любой TX-path стартует выключенным и с консервативной мощностью независимо от сохранённых настроек.

Дополнительный риск: модуль сохраняет group settings во внутренней памяти после power-off. Firmware-only запись low-power при каждой загрузке не заменяет аппаратный default и readback.

## Выполненное исправление

В `hardware/tscircuit/audio.tsx` добавлены:

- `Rsa_ptt_safe=10 kΩ` к `+3V3`: receive-default при high-Z control;
- `Rsa_pd_safe=10 kΩ` к GND: power-down-default при high-Z control;
- `Rsa_hl_safe=0 Ω` к GND: физический low-power ceiling текущего draft.

Такой draft предпочитает временно недоступную высокую мощность возможности неожиданного high-power TX. PCA9555 может явно перевести `PD` в normal и `PTT` в TX только после policy gate; H/L остаётся low до stage-3 решения.

## Что ещё не закрыто

- `FND-0007` остаётся открытым: I²C-expander не является независимым аппаратным STOP и не может гарантированно снять PTT при зависшей шине/firmware.
- Для целевого доступа к high-power нужен fail-safe управляемый `H/L` path с аппаратным low-default, который размыкается только при явном выборе разрешённого power profile. Его control resource входит в сводный pin/GPIO/safety budget по `DEC-0012`.
- Logic thresholds, power sequencing, pull strength, PTT/PD response, actual RF power и interaction аппаратного H/L с `AT+DMOSETGROUP` требуют bench/HIL proof.
- Low output 24–26 dBm на RF-порту и внешняя SMA сами по себе не создают licence-exempt PMR446 device; legal profiles проверяются отдельно.

## Acceptance последующих стадий

1. Scope/logic-analyzer trace power-on, reset, brownout, watchdog и expander reset показывает `PD=0`, `PTT=1`, `H/L=0` до arming.
2. Залипший low PTT либо отказ expander физически гасится будущим независимым STOP/TX power gate.
3. Low/high RF power измеряются на нагрузке для min/nominal/max VBAT и температур; UI показывает фактический прошедший readback profile.
4. Ни сохранённая настройка модуля, ни reboot/update не восстанавливают high-power/armed state.

## Первичный источник

- [NiceRF SA868S datasheet rev. 1.7: PTT, PD, H/L, power and persistent settings](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
