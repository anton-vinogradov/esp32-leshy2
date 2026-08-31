# Состояния питания R2

[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Методы](verification-methods.ru.md) · [English](power-state-register.md)

`H3-R2.1.1` прошёл ревью. Реестр детерминированно перечисляет `43` состояния источников/заряда, `56` рабочих профиля и `2266` полных разрешённых состояния R2.

## Что вошло

- единственный питающий USB-C: absent, неизвестный 5-V fallback, 5 V × 3 A, 9 V × 3 A и 15 V × 2 A;
- pack: отсутствует, изолирован, 2S low/nominal/full;
- все десять signal groups, включая три nRF24 во всех 3R/1T2R/2T1R/3T сочетаниях;
- оба взаимоисключающих Cap-профиля: U214 и receive-only U219;
- FM/SW, AM/LW и обязательный receive-only Airband как взаимоисключающие подрежимы BROADCAST_RX;
- safe-only и latched-fault состояния без payload-передачи.

## Важная граница

Это доказательство полноты состояний, а не достаточности тока. Следующий точный маркер `H3-R2.1.2` связывает каждый питаемый компонент с явной worst-case нагрузкой; неизвестный ток обязан дать `unresolved_fail`, а не скрытый запас.

[Полный машинный реестр](../hardware/verification/generated/H3-R2-power-state-register.json).
