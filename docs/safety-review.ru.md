# Итог safety-ревью Leshy2

[English](safety-review.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

H2.5 закрыт: выбранные safety-критичные тракты совпадают с полной native KiCad-иерархией. Это ещё не заменяет симуляцию, layout и физический HIL.

| Шаг | Область | Статус |
|---|---|---|
| `H2.5.1` | источники, допуск, заряд и шины | ✅ reviewed |
| `H2.5.2` | reset, boot, service и recovery | ✅ reviewed |
| `H2.5.3` | границы no-back-power | ✅ reviewed |
| `H2.5.4` | quiet state и изоляция | ✅ reviewed |
| `H2.5.5` | watchdog, thermal и FAULT_KILL | ✅ reviewed |

## Исправленные несоответствия

- `H2.5.1-F01` — child sheets reused local R1/C1/U1-style references, making whole-project flat netlists ambiguous → deterministic sheet-scoped reference blocks now produce globally unique references in all three projects
- `H2.5.2-F01` — the reviewed service contract promised PD target-bus and direct EEPROM recovery pads, but RF60 did not instantiate them → six BOM-free 1.0-mm internal copper pads now expose SYS_I2C_SDA/SCL/SYS_INT_N and PD_LOCAL_I2C_SDA/SCL/PD_EEPROM_WP
- `H2.5.3-F01` — C5 service VBUS had a physical sense pad while the equivalent RP VBUS observation existed only in the abstract service contract → one BOM-free TP_RP_SERVICE_VBUS_SENSE copper pad now completes the symmetric data-only USB boundary
- `H2.5.4-F01` — VOICE_QUIET and VOICE_INTERFACE_QUIET retained obsolete abstract VOICE_PTT_N and VOICE_DOMAIN_EN names → the contracts now name the implemented request, safety-gated and module-side PTT nets plus request and safe domain-enable nets
- `H2.5.5-F01` — the safety contract promised watchdog, latch and safe-gate observation points but 15 distinct electrical nodes had no physical copper pad → RF60 now contains 52 BOM-free pads; WDO_N uses the shared FAULT_ASSERT_N pad, FAULT_KILL uses its implemented FAULT_LATCH_SENSE_AON name and RP reset uses TP_RP_RESET_N
- `H3.6.2-F01` — the former fan-out reused RUN_PERMIT-derived qualification for every hazardous endpoint, so one stuck-permissive latch or primary gate was not independently contained → M1 contact 34 now carries direct FAULT_ASSERT_N; separate C5/RP reset sinks, nRF/CC backup gates, the voice eFuse clamp and independent expansion-branch inputs bypass the primary latch path

## Результат H2.5.6

✅ **Проведено ревью:** открытых paper/ECAD findings нет. Следующий точный шаг — H2.6, полное закрытие ERC и каждого намеренного NC.

[Машинное evidence](../hardware/ecad/generated/H2-REV56-safety-consolidated.json).
