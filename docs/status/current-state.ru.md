# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-16. Эта страница описывает, что доказано сейчас. Образ готового продукта находится в [целевом hardware README](../../README.ru.md), а готового ПО — в [целевом firmware README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md).

- Канонические доказательства: [журнал ревью](../review/README.md)
- English version: [current-state.md](current-state.md)
- Legacy только для справки: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Ход ревью

| Этап | Состояние |
|---|---|
| 0. Система ревью и baseline | Проведено ревью |
| 1. Видение и границы | Проведено ревью, включая трёхуровневое уточнение |
| 2. Возможности и исключения | В работе |
| 3–10 | Не начато |

Каноническая таблица стадий — [`docs/review/stages.md`](../review/stages.md).

## Принятые целевые решения, уже отражённые на продуктовой странице

- all-in-one профиль, акт о ненападении и три уровня функциональности (`DEC-0002`, `DEC-0010`);
- консервативные TX-дефолты и явный выбор максимальной мощности (`DEC-0003`);
- оптимизация полной стоимости без потери продукта (`DEC-0005`);
- внешний M5 GNSS и внешний U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- бортовая mono audio-архитектура ES8311 с fail-safe analog bypass (`DEC-0009`);
- целевое владение C5 для 3×nRF24 и IR (`DEC-0001`) без заявления о готовом межпроцессорном транспорте.

## Открытое инженерное состояние

- `FND-0001`: единственный GP-SPI C5 не может одновременно выполнять legacy-роли nRF-master и S3↔C5-slave.
- `FND-0002`: владелец BLE расходится между legacy-репозиториями.
- `FND-0003`: audio-архитектура принята, но pin/electrical/firmware/HIL proof ещё не выполнен.
- `FND-0006`: исходная матрица кнопок и audio-control конфликтуют на `U13.P10..P17`.
- `FND-0007`: текущий STOP — только вход I²C-экспандера, а не независимый аппаратный TX-kill.
- `FND-0008`: legacy System/UI привязывает функции к неподтверждённым SPI-, hot-plug-, USB- и update-security реализациям.
- Существующие tsCircuit/KiCad остаются legacy-артефактами реализации до ревью производящих стадий и регенерации.

## Текущая работа ревью

Аудит пререквизитов System/UI прошёл `REV-0002H`. Draft [`REQ-SYS-0001`](../review/requirements/REQ-SYS-0001-system-ui-storage.md) раскладывает все одиннадцать legacy-групп в проверяемые требования платформы без выбора окончательной pin-map.

## Текущий decision gate

[`IMP-0011`](../review/improvements/IMP-0011-signed-update-chain.md) спрашивает, должны ли все устанавливаемые S3/C5 images проходить проверку подписи и rollback validation, тогда как необратимая политика hardware Secure Boot/Flash Encryption выбирается позже — после доказанной recovery/lifecycle architecture. Набор требований остаётся **«На ревью»** до этого решения.

## Отложенный архитектурный gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) остаётся открытым, но [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) переносит выбор A/B на этап 3. Новый ответ владельца не запрашивается, пока сводный pin/GPIO/resource budget не учтёт оба MCU, экспандеры, fixed-function pins, межпроцессорный transport, audio, UI/touch, внешние модули и действительно освободившиеся линии onboard GNSS/LoRa.

`FND-0006` и `FND-0007` остаются открытыми. Перенос не выбирает `U14`/матрицу 3×3 и не доказывает аппаратный STOP.
