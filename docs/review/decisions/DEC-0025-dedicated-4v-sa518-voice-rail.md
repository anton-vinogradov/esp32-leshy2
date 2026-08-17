# DEC-0025 — dedicated 4.0 V `VVOICE` для SA518

> `DEC-0064/PWR-0006` compared the input alternatives; `DEC-0065` confirms
> the `4.0 V` output is implemented by a buck from the accepted 2S input.

- Статус: **Принято; проведено ревью**
- Дата: 2026-08-16
- Основание: владелец принял рекомендуемый вариант `IMP-0023/A`
- Этап: 3 — системная архитектура и владение
- Затрагивает: `DEC-0016`, `REQ-VHF-0001`, `FND-0030`, `BUD-0001`, power/STOP tree и voice stuffing

## Решение

1. SA518 получает отдельный buck rail `VVOICE` от принятого
   `2S BAT=6.0–8.4 V`.
2. Номинал `VVOICE` — 4.0 V. Окончательное производственное окно внутри 3.9–4.1 V выбирается только по conducted RF/current qualification exact SA518 revision; это не пользовательская регулировка мощности.
3. Power stage рассчитывается не менее чем на 1.25 A continuous и 1.5 A transient, с local bulk, доступными current/voltage test points и проверкой droop/thermal margin.
4. `VVOICE` default-off и находится под независимым `TX_KILL` решения `DEC-0024`. Hardware STOP снимает питание/enable voice PA и принудительно удерживает PTT в RX независимо от MCU, UART, I²C и UI.
5. Маркировка 0.5/1 W разрешена только после per-band conducted measurement по supply tolerance, battery, temperature и exact module revision. Firmware bit `low/high` или имя профиля не считаются доказательством RF power.
6. SA868S-UHF остаётся fallback только как отдельный явно обозначенный stuffing/manifest/profile. Если его квалифицированная реализация требует 5 V, применяется отдельная regulator stuffing/configuration и собственный RF/power/HIL набор; неизвестный либо смешанный backend остаётся TX-disabled.
7. Принятый 5 V accessory rail сохраняется отдельно. Питание SA518 от legacy 5 V и замена на 3.3 V не являются эквивалентными вариантами target product.

## Бюджет и границы

- Дополнительный regulator domain является принятой ценой сохранения честного 1 W-class target и независимого STOP.
- Exact regulator/load switch/inductor/capacitor BOM, унификация детали с другими bucks, layout и поставщики выбираются на этапе 4.
- Решение закрывает архитектурную неоднозначность `FND-0030`, но не выдаёт legacy `audio.tsx` за исправленную производственную схему.

## Обязательная проверка

Stage 4–10 evidence включает startup/inrush, min/nom/max rail, simultaneous-load/fault overlap, STOP kill time, thermal soak и conducted low/high output on VHF/UHF for every supported stuffing profile. Неизвестная revision или measurement outside profile переводит TX в disabled, а не в guessed-power mode.
