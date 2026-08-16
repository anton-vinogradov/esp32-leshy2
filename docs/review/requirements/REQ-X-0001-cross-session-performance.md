# REQ-X-0001 — cross-session, privacy, coexistence and performance contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-X-01`–`C-X-11`, `C-UX-01`–`C-UX-03`, `C-HWX-01`–`C-HWX-04`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0011`, `DEC-0012`, `DEC-0013`, `DEC-0022`, `DEC-0023`
- Пересечения: все radio `REQ-*`; `C-X-01`, `C-X-02`, `C-X-09`, `C-HWX-01`, `C-HWX-03`, `C-HWX-04` также закрыты `REQ-SYS-0001`

## Граница документа

Составная session не получает больше полномочий, чем её самый опасный leaf-action. Общий UI, parser, storage или scheduler не может обойти region, privacy, authorization, Controlled-Zone, per-tool arming, actual-TX and STOP contracts отдельных radio.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-X-01` | `C-X-01`, `C-X-02` | `include` | Сквозной safety | Install pledge, fresh Controlled-Zone banner, per-tool authorization/arming, conservative TX defaults, dead-man, actual-TX indication, STOP and reset/shutdown/update safe-state compose exactly as `DEC-0002/0003/0010`; ни один общий экран их не заменяет. |
| `REQ-X-02` | `C-X-03` | `conditional` | Сквозной coexistence | Единственный cross-radio scheduler публикует requested/active owner, priority, preemption, latency/loss and stale state. Simultaneity является отдельной измеренной capability пары трактов, не UI-обещанием. |
| `REQ-X-03` | `C-X-04` | `conditional` | Сквозной IPC | Any inter-target API is typed, bounded, versioned, authenticated where needed and idempotent; link loss/reset/update cancels leases and TX. Exact topology/transport is selected only in the future atomic architecture. |
| `REQ-X-04` | `C-X-05` | `conditional` | Основной/Лаборатория | Combined spectrum/target view объединяет only timestamped source-labelled observations. Energy, identity and protocol evidence remain distinct; stale/unknown/coverage visible. Active follow-up re-enters its own gate. |
| `REQ-X-05` | `C-X-06` | `conditional` | Лаборатория | Geo-tagged capture/wardrive — explicit foreground privacy session. Each record includes GNSS source/fix quality/age or `no fix`, minimizes identities and supports encrypted storage/export/delete/retention. |
| `REQ-X-06` | `C-X-07` | `conditional` | Основной | RTC can sync from qualified GNSS/NTP with source, uncertainty, age and monotonic event ordering. Backward time jumps do not break logs, keys, rollback or replay protection. |
| `REQ-X-07` | `C-X-08` | `conditional` | Смешанный | Unified capture library retains immutable original, provenance and exact radio profile. Decode/edit/export are separate; replay is inert until destination radio revalidates Main/Controlled gate. |
| `REQ-X-08` | `C-X-09` | `conditional` | Основной | Phone text input uses locally initiated/accepted pairing, authenticated encryption, allowlist, visible connected peer and local disconnect/revoke. Missing/disconnected/stale companion blocks only the declared text-dependent workflow. It cannot confirm pledge, Controlled entry, TX arm, destructive write, FIDO presence, recovery or firmware-trust decisions; received text and consequences are reviewed locally. |
| `REQ-X-09` | `C-X-10` | `conditional` | Основной | Remote-ID detector passively parses versioned public standards/corpus, shows raw evidence/confidence/age and never infers ownership, intent or guaranteed aircraft absence. Location records inherit privacy policy. |
| `REQ-X-10` | `C-X-11` | `conditional` | Сквозной alerts | LED/buzzer/location alerts name source, severity, age and confidence. Quiet/dim mode may suppress ordinary alerts, never active-TX, STOP failure, critical battery or unsafe state. |
| `REQ-X-11` | `C-UX-01` | `conditional` | Лаборатория | One-shot wardrive orchestrates Wi-Fi/BLE/Sub-GHz/GNSS under one explicit foreground session, scheduler and privacy record; unsupported radio/position is marked missing, not silently imputed. |
| `REQ-X-12` | `C-UX-02` | `conditional` | Main parser / Controlled execution | One bounded, fuzzed DuckyScript-compatible parser may serve BadUSB and BadBLE. Ordinary text automation and authorized injection use separate execution policies; script import cannot press consent/arm/destructive confirmation. |
| `REQ-X-13` | `C-UX-03` | `conditional` | Main/Controlled | Quick replay is Main only for immutable owner-tagged signal plus valid local profile. Unknown/edited/security record requires its radio's Controlled-Zone authorization; no global quick-replay bypass exists. |
| `REQ-X-14` | `C-HWX-01` | `conditional` | Основной/power | Manual dim/timeout enter baseline when electrically supported. Auto-brightness requires a qualified sensor/profile, hysteresis, override and readability test; simple on/off is not called brightness. |
| `REQ-X-15` | `C-HWX-02` | `conditional` | Performance | LoRa boosted gain governed exclusively by `REQ-LORA-10`; no fixed percentage is a product promise. |
| `REQ-X-16` | `C-HWX-03`, `C-HWX-04` | `acceptance`, не feature | Сквозной performance | UI latency, capture loss, waterfall continuity, SD recovery and radio deadlines get numeric budgets after architecture profiling. Dirty rectangles, DMA, double buffer, arbiter and watchdog are implementation candidates, not requirements themselves. |
| `REQ-X-17` | all sessions | `conditional` | Сквозной resource | Every session declares radios, buses, pins, DMA, interrupts, RAM/PSRAM, flash, storage bandwidth, power peak, thermal and timing demand before layout selection. Degraded modes are explicit and acceptance-tested. |
| `REQ-X-18` | all records | `conditional` | Сквозной provenance | Target README contains accepted product only; current-state points to evidence and proposals. Logs/artifacts carry schema/tool/profile/version/timestamp/source and cannot claim implementation before HIL. |
| `REQ-X-19` | all | `acceptance` | Сквозной fault/HIL | Test matrix injects SD full/corrupt, bad import, low battery, hot-plug, radio timeout, IPC loss, MCU reset/crash, clock jump, update rollback, STOP and concurrent-session conflicts. Failure is bounded, visible and recoverable. |

## Zero-loss boundary

Объединение UI/parser/storage/scheduler считается экономией только при сохранении независимых safety policies и измеренных budgets. Optional external capabilities do not burden the base BOM, but the expansion contract and discoverability remain. Any layout that cannot resource every accepted baseline leaf, or explicitly declared optional profile when attached, fails before pin assignment is accepted.
