# Историческая виртуальная электрическая проверка Leshy2 · R1

[English](virtual-verification.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Принятый H2](h2-acceptance.ru.md)

Этот H3 сохраняет воспроизводимые расчёты прежней одно-RP архитектуры R1. Он не доказывает текущую dual-RP R2; физические измерения также не подменяются.

## Принятый исходный материал

Ревизия H2 с независимыми SA818S-V/U принята 26 августа 2026 года и привязана к неизменяемому git snapshot `afe48e788adeba9fdfc9c84412f8657fe297308b` и SHA-256 его 44 файлов. Текущие R2-файлы не подменяют исторические входы; любое развитие проходит отдельную R2-цепочку H2/H3.

## Матрица проверки

| Этап | Область | Метод до изготовления | Артефакт H3 | Остаточная физическая проверка |
|---|---|---|---|---|
| `H3.1` | `steady_state_power` | analytic_envelope | rail/source/load/charge margin tables | H8 measured current and temperature |
| `H3.2` | `power_transitions` | equation_and_circuit_simulation | startup/shutdown/handover/brownout/load-step traces | H8 oscilloscope traces |
| `H3.2` | `safety_loop_dynamics` | timed_state_and_fault_injection | watchdog/latch/FAULT_KILL timing evidence | H8 injected-fault timing |
| `H3.3` | `display_and_backlight` | worst_case_corner_analysis | supply/current/timing/thermal margins | H5 received-panel identity and H8 optical/current checks |
| `H3.3` | `audio` | small_signal_power_and_corner_analysis | gain/noise/clipping/load/thermal margins | H8 acoustic and EMI measurements |
| `H3.3` | `infrared` | pulse_current_threshold_and_thermal_analysis | TX/RX/duty-cycle envelopes | H8 range and temperature measurements |
| `H3.3` | `battery_analog` | tolerance_and_threshold_analysis | sense/thermistor/fault threshold margins | H8 calibrated threshold tests |
| `H3.4` | `digital_levels_and_defaults` | static_interface_proof | levels/pulls/reset/no-back-power matrix | H8 pin-state measurements |
| `H3.4` | `digital_timing_and_bandwidth` | timing_and_occupancy_budget | display/storage/audio/radio bus margins | firmware F3 target/emulator traces and H8 logic-analyzer traces |
| `H3.4` | `interboard_and_expansion` | loading_and_boundary_analysis | M1/U214/M5/service loading margins | H5 mating evidence and H8 signal-integrity measurements |
| `H3.5` | `rf_feeds` | transmission_line_and_loss_budget | 50-ohm/matching/connector/loss constraints | H6 field-solver/layout evidence and H8 VNA |
| `H3.5` | `rf_returns_and_corridors` | prelayout_geometry_constraint_analysis | keepouts/reference-plane/return-current rules | H6 routed-board review |
| `H3.5` | `rf_coexistence` | state_space_and_isolation_budget | one-active-group and 3x-nRF24 concurrency constraints | H8 coexistence and spectrum tests |
| `H3.6` | `thermal` | lumped_worst_case_thermal_model | board/battery/enclosure temperature bounds | H8 thermocouple/thermal-camera validation |
| `H3.6` | `single_fault_tree` | fault_tree_and_fmea | independent shutdown and recovery coverage | H8 safe fault injection |
| `H3.6` | `unattended_operation` | bounded_energy_and_state_analysis | extended-operation and configurable self-test policy without a runtime claim | H8 24/48-hour qualified-USB endurance and battery-to-protected-cutoff measurements |

**Исторический маркер:** `H3.0.1-R1`. **Текущий аппаратный маркер:** `H1-R2.33`; R2 должна пройти собственный H2/H3. Закупка, PCB layout и fabrication не разрешены.

[Машинный freeze](../hardware/verification/generated/H3-VRF01-input-freeze.json).
