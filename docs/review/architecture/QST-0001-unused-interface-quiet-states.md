# QST-0001 — unused-interface quiet-state contracts

- Статус: **Проведено ревью требования и всех отдельных base RF/IR paper endpoints; consolidated HIL open**
- Дата: 2026-08-17
- Decision: [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md)
- Signal groups: [`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)
- Review: [`REV-0004N`](../reviews/REV-0004N-unused-interface-quiet-state-input-review.md)

## Цель

Неактивный интерфейс не должен продолжать scans, advertising, receive polling,
bus clocks или powered frontend только потому, что driver загружен. Перед
активацией новой signal group runtime обязан доказать quiet-state всех чужих
трактов. Цель HIL — не абстрактный «ноль EMI», а отсутствие преднамеренной
активности и ограниченная измеренная деградация active receiver относительно
его isolated reference.

## Классы состояния

| State | Смысл |
|---|---|
| `TX-HARD-OFF` | non-programmable TX gate/rail запрещает излучение независимо от MCU |
| `RAIL-OFF` | отдельный load switch выключен, rail разряжен, I/O не back-power endpoint |
| `NATIVE-OFF` | powered SoC остаётся нужен, но его RF/peripheral block остановлен штатным power-down |
| `DIGITAL-QUIET` | controller clock/DMA/polling off, outputs static parked, IRQ cleared/masked |
| `ACTIVE` | interface перечислен в manifest и прошёл wake/self-test; TX всё равно требует отдельного arm |

## Контракты G2F-3I

| Interface/domain | Inactive state | Управление в paper map | Обязательное доказательство |
|---|---|---|---|
| `nrf0+nrf1+nrf2` | pre-off CE low/CSN deasserted; then common `RAIL-OFF`, all signal paths isolated/high-Z and three PIO/DMA stopped | exact `TPS22919DCKR`; per radio `74LVC126APW,118` for CE/CSN/SCK/MOSI and `74LVC2G126DC,125` for MISO/IRQ, all OEs on the switched rail with Ioff, two-domain pulls and 22-Ohm output resistors; `DEC-0091` | HIL still proves 100-ms POR, no I/O back-power, QOD discharge/current, no carrier, detector hold and active-path sensitivity under parked digital aggression |
| `CC1101` | pre-off IDLE/power-down and CSN deasserted; then `RAIL-OFF`, SPI/GDO isolated/high-Z and PIO/DMA stopped | `RP.GPIO23` request passes through exact AON gate; output pull-down and later exact load switch/isolation | no back-power through SPI/GDO, rail/current/no-carrier evidence |
| `U214` / external Cap | `RAIL-OFF`, I²C isolated, SPI/UART static | `slow_io.P17` request passes through AON gate to protected reverse-safe `EXT_5V_EN_SAFE`; TCA4307 EN follows power-good | accessory rail discharge, isolation READY/status, hot-unplug and no-back-power HIL |
| voice radio | PTT hardware-off, module power-down and qualified 4 V rail off | exact AON AND gate controls voice rail; exact OR makes `VOICE_PTT_SAFE_N = request OR TX_KILL`, with module-side pull-up | actual-TX-off, rail/current/thermal and PTT stuck/fault injection |
| `Si4732-A10-GSR` receiver / `RECEIVER_QUIET` | receiver rail/reset off, I²C branch cannot back-power, audio outputs passive; two protected RX-only ports remain harmless | `slow_io.P15 → RX_DOMAIN_EN` controls exact power/reset/isolation; separate exact FMI 56-nH/1-nF and AMI 0.47-uF/ESD paths add no control | all four bands, loop-pod parasitics, I²C back-power, wake/calibration and active-group noise-floor HIL |
| codec/audio support / `CODEC_AUDIO_QUIET` | `AUDIO_ARM=0`, selectors at reset defaults, codec rail discharged and I²S isolated, PAM8302A off, I²S clock/DMA stopped unless audio is an explicit active-group support member | direct S3 GPIO6 plus P01/P10, selector pulls, external `CODEC_PWR_EN` and exact supervisors/isolators; ES8311 `CE` remains fixed address strap | no I/O back-power, BCLK/WS, stale selector, pop/click/current and RF noise-floor HIL |
| voice signal interfaces / `VOICE_INTERFACE_QUIET` | PTT hardware-off, UART/AFOUT/MIC_IN isolated and H/L at safe low-or-open default when `SG-VOICE` is not active | P13/P14/P27, safe PTT gate and exact switched-domain digital/analog isolators | no back-power, unintended TX/audio injection, stuck-line and RF noise-floor HIL |
| IR RX/TX frontend | frontend rail off; TX remains under `HARD_STOP_N` | `C5.GPIO4 → IR_FRONTEND_PWR_EN`; RMT carrier passes through exact AON gate before the driver | dark/current/no-optical-output evidence and active-radio noise-floor HIL |
| S3 Wi-Fi/BLE/ESP-NOW | `NATIVE-OFF`; S3 CPU/UI remains alive | stop protocols/scans/advertising, disable RF block, check `S3_RF_TX_EVIDENCE` | no background frames/carrier and active receiver desense HIL |
| C5 Wi-Fi/802.15.4 | `NATIVE-OFF`; C5 may remain alive for IR/recovery | stop protocols and RF block, check `C5_RF_TX_EVIDENCE`; SDIO clocks only for bounded IPC | no background frames/carrier and active receiver desense HIL |
| microSD | `RAIL-OFF` when no storage session; SPI static | `SD_PWR_EN`; bounded flush then controller/rail off | no corruption/back-power, removal/fault and active receiver desense HIL |
| M5 Unit/high-throughput expansion | external power off and signal pins high-Z when no exact profile | `EXT_5V_EN` plus protected/isolated connector implementation | wrong accessory, hot-plug, stuck-line, ESD and no-back-power HIL |
| USB/UART/service | detached/suspended or static idle; no periodic logs | native USB/UART controllers stopped unless attached or service session; physical recovery contacts remain | recovery still works from every bad firmware state; no periodic traffic in quiet mode |
| S3↔RP and S3↔C5 IPC | `DIGITAL-QUIET` between bounded transfers, not falsely `RAIL-OFF` | dedicated SPI3/SDIO clocks stop; event line wakes service | clock spectrum, latency and active receiver desense under worst valid traffic |
| display/touch/UI | only actually used transactions run; display stays available for safety/status | dirty-region SPI, stopped clock between chunks; touch IRQ rather than polling | menu response target plus active receiver desense; dim/off policy must not hide TX state |

## Pin-budget consequence

The quiet-state requirement consumes three formerly free direct controls:

- RP2354B `GPIO15` — common power gate of the three nRF paths;
- RP2354B `GPIO23` — CC1101 power gate;
- ESP32-C5 `GPIO4` — IR frontend power gate.

After later `DEC-0052`, S3 GPIO41/42 become QSPI D2/D3. Subsequent
`AUDIO-0002/FND-0067` assigns slow P27 to the previously omitted
`RX_AUDIO_SOURCE_SEL`. Current remaining direct general-purpose reserve is
S3=0, C5=1 and RP=0. Main slow I/O retains P05 as its only free contact; the
separate UI expander retains P7 as a protected fixture/growth reserve. The
individual paper endpoints now contain exact first-target switches, isolation,
default pulls and passive frontends, but physical/HIL evidence remains open. A future direct
RP timing endpoint now requires a remap or justified expander/latch; it cannot
be silently added.

No uncounted isolator-enable GPIO is assumed. The exact circuit must either
provide powered-off protection (`Ioff`) intrinsically or derive isolation from
the same group rail/power-good sequence. If the selected parts require another
direct control, the zero-free-RP budget forces a remap and repeated review.

## Acceptance sequence

For every group transition, a HIL trace must show:

1. old TX lease revoked and hardware TX evidence inactive;
2. each non-member reaches safe pre-off levels and I/O isolation before its
   rail falls; wake keeps I/O isolated until rail/settling are valid;
3. no forbidden clock/carrier/background packet during the measurement window;
4. active receiver sensitivity/noise-floor stays inside its exact qualified
   limit with system planes exercising their maximum valid transaction load;
5. any unknown status, stuck rail/line or timeout leaves group `NONE` and TX
   disarmed.

Every separate base RF/IR paper endpoint is now marked **«Проведено ревью
subblock»** through `DEC-0091…0096/REV-0005AV…BA`. Their physical
non-interference remains HIL. Requirement review alone is not electrical or
physical acceptance, and consolidated I6 remains active.
