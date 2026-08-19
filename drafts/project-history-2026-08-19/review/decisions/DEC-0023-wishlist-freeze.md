# DEC-0023 — freeze полного wishlist после делегированного саморевью

- Статус: **Принято; проведено ревью**
- Дата: 2026-08-16
- Основание: владелец поручил провести саморевью хотелок и доверил продуктовый выбор опыту ревьюера
- Артефакты: `INV-0004`, `REV-0002AC`, `REV-0002AD`

## Решение

1. Реестр из 125 кандидатных leaf-функций считается полным и замороженным в границах `INV-0004` и reviewed `REQ-*`.
2. `W-OWN-01..15` остаются обязательными сквозными invariants.
3. Десять source-extras после устранения двух смешанных строк образуют двенадцать независимых dispositions.
4. Optional/deferred функция остаётся в product roadmap, но не увеличивает base-board BOM/resource budget и не блокирует первую версию.
5. Саморевью не выбирает MCU owner, GPIO, bus, inter-MCU transport, part placement или layout.
6. Этап 3 сравнивает несколько полных аппаратных синтезов на одном capability/concurrency/resource model; по `DEC-0027` оси S3-heavy/C5-heavy/balanced больше не задаются заранее. «Исторически принято/разведено» не даёт варианту преимущества без прохождения hard gates, бюджета и HIL plan.

## Ключевые инженерные выводы

- три полнофункциональных nRF24 остаются неизменным результатом, а их физический owner остаётся открытым;
- IR остаётся на C5, native BLE — на S3;
- Wi-Fi 2.4, Sub-GHz и внешний LoRa получили честные измеримые contracts;
- потенциально тяжёлые Bluetooth Classic/cellular/SDR/LF/second-NFC функции вынесены из base BOM в optional profiles;
- passive security возможности сохранены, active/disruptive возможности не смешаны с Main и получают actual technical containment;
- implementation mechanisms вроде DMA, dirty rectangles or raw injection API не считаются пользовательскими функциями сами по себе.

## Change control

Новая хотелка не теряется: она получает новый `W-*`, risk/level, base-or-option decision and resource-demand delta. Если delta затрагивает уже проверенный layout, его статус становится **«Требуется повторное ревью»**.
