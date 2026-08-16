# DEC-0028 — принятие zero-based architecture `SYN-3A`

- Статус: **Принято; проведено ревью**
- Дата: 2026-08-16
- Основание: прямое подтверждение владельца «давай)» в ответ на единый вопрос о принятии `PKG-0001/SYN-3A`
- Этап: 3 — системная архитектура и владение
- Нормативный package: [`PKG-0001`](../architecture/PKG-0001-zero-based-target-architecture-proposal.md)
- Метод и правило приёмки: [`DEC-0027`](DEC-0027-zero-based-capability-driven-architecture.md), [`DEC-0026`](DEC-0026-atomic-integrated-architecture-acceptance.md)

## Решение

`PKG-0001/SYN-3A` принят целиком как target architecture Leshy2:

1. `ESP32-S3-WROOM-1U-N16R2` — application/UI/storage/audio domain, native 2.4 GHz Wi-Fi/BLE и manager внешних M5 profiles.
2. `ESP32-C5-WROOM-1U-N8R8`, silicon revision ≥1.0 — native 2.4/5 GHz Wi-Fi, IEEE 802.15.4 и dual-path consumer IR.
3. `RP2354A A4`, QFN60, 2 MiB stacked flash — deterministic domain трёх полнофункциональных nRF24, CC1101, analog-voice control/PTT и local dead-man.
4. S3↔C5 использует 1-bit SDIO; S3↔RP — 20 MHz initial SPI + отдельный alert. Нормативны typed control/event/bulk/liveness/recovery channels, measured payload floor и lease-expiry behavior из package.
5. Полностью принят exact controller/pin/recovery map `PIN-0002/SYN-3A`, включая straps, physical USB/SWD/RUN access и семь свободных generic GPIO C5.
6. Приняты touch + encoder/push + BACK/HOME/OPTIONS, direct PTT, независимые latched STOP и recessed RE-ARM, а также `TCA9535PWR` только для non-safety UI/slow control.
7. Приняты memory/flash/traffic, power, RF/coexistence, storage/audio/display, open owner-signed A/B update/recovery и sourcing/cost contracts package.
8. `KG-01…08` обязательны. Провал любого gate переоткрывает весь затронутый package; `SYN-2A` является первым полным fallback для нового ревью, но не вторым скрытым target.

Ни один owner, bus, pin, UI fragment, update path или cost tradeoff из решения не принимается и не откатывается отдельно.

## Явно принятые последствия

- candidate-specific recurring premium составляет примерно `$1.10` midpoint относительно `SYN-2A`;
- появляется третий firmware/update/recovery/HIL target;
- RP2354A authorised quotes, lot traceability and qualified assembly supply остаются `KG-01`; `FND-0035` later confirms public exact-A4 stock but does not itself prove production supply;
- прямые nRF/CC/voice controls, local deadlines, fault containment и C5 GPIO reserve считаются оправдывающими premium;
- legacy owner/layout artifacts остаются справочными источниками идей и рисков, а не ограничениями target.

## Распространение и change control

- target README обоих репозиториев отражают принятую трёхдоменную архитектуру;
- firmware получает нормативный runtime/update/safety contract от hardware package;
- этап 3 закрывается только отдельным cross-repository propagation review;
- этап 4 может проверять exact components и BOM, но не вправе молча менять capability, owner, pin, power, recovery, STOP или RF contracts;
- эквивалентная BOM substitution допустима только после pin/reset/electrical/AVL/HIL proof; неэквивалентность создаёт finding и переоткрывает затронутую часть архитектуры.
