# FND-0056 — exact SA518 has no dedicated SQ pin and its update contact is ambiguous

- Статус: **Paper map исправлена консервативно; exact activity/recovery proof открыт**
- Серьёзность: real-device pin provenance / diagnostics / recovery blocker
- Обнаружено: 2026-08-17
- Затрагивает: `G2F-3D`, `G2F-3I`, voice event handling, service fixture,
  exact SA518 selection

## Несоответствие

Draft maps резервировали input `VOICE_SQ` для abstract SA518/SA868 backend.
В актуальной manufacturer pin table SA518 rev 1.1 отдельного `SQ` нет. Есть:

- pin 18 `Audio_ON` — output управления внешним audio amplifier;
- программируемый squelch level через serial commands;
- pin 17 `UPDATE`, описание которого требует pull-down at power-on для входа
  в update mode, хотя колонка I/O в той же таблице помечает его как output.

Нельзя автоматически назвать `Audio_ON` аппаратным squelch indicator, а
противоречивый `UPDATE` нельзя без проверки напрямую подключить к MCU output.

## Выполненное безопасное исправление

- `VOICE_SQ` в обеих затронутых maps переименован в neutral
  `VOICE_ACTIVITY`;
- peer теперь называется exact-module activity/status input и не обещает
  squelch semantics;
- `PIN-0002` и generated ledger исправлены тем же именем;
- `devices.json` хранит фактические 20 SA518 contacts, включая отсутствие SQ;
- physical `UPDATE` access остаётся обязательным service-pad/fixture gate, но
  не считается GPIO до electrical direction/pull/update-tool proof.

## Последствия

GPIO budget не ухудшается: ранее зарезервированный input остаётся условным
activity/status input и может быть освобождён, если HIL не докажет полезную
семантику `Audio_ON`. Firmware обязан получать squelch configuration/readback
через подтверждённый serial protocol и показывать unknown, если module state
не читается. Actual-TX evidence по-прежнему отдельное внешнее измерение.

## Критерий закрытия

1. exact purchased SA518 revision/firmware identity совпадает с manifest;
2. logic-analyzer/HIL определяет pin 18 при no-carrier, carrier, squelch-open,
   RX audio, TX, sleep and reset;
3. pin 17 direction, safe pull, power-on timing, update transport/tool/image
   availability and recovery failure modes доказаны;
4. resulting contact mapping и fixture проходят повторное review.

## Первичный источник

- [NiceRF SA518 rev 1.1 specification](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)

