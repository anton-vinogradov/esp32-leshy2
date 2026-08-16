# CON-0001 — hardware-neutral concurrency and failure model

- Статус: **Historical candidate/reference; active prerequisite superseded by `DEC-0032/FND-0041`**
- Дата: 2026-08-16
- Этап: 3, шаг 2
- Вход: reviewed `CAP-0001`
- Проверочные источники: reviewed `REQ-SYS/GNSS/RX/VHF/IR/NFC/W24/W5/BLE/N24/SUB/LORA/X`, accepted `DEC-0002/0003/0010/0013/0019/0024/0027`
- Не входы: legacy schematic/source, прежние owners, transports, buses, GPIO, controller counts и layouts

## Цель и граница

> Relationship classes and failure questions remain useful reference. The
> artifact depended on contaminated `CAP-0001`, so every scenario must be
> re-derived after the competitor delta and G3 product design; no current
> architecture may consume this status as final input.

Этот документ определяет, какие capability должны работать одновременно, какие могут честно делить физический ресурс по расписанию, какие несовместимы по смыслу или безопасности и как виден отказ. Он не выбирает MCU, module variant, IPC, bus, pin, expander, RF switch, память или питание.

«Входит в combined session» не означает «работает физически одновременно». Любая будущая архитектура обязана отнести каждую пару активных функций к одному из классов ниже и доказать выбранный класс измерением.

## Классы отношений

| Код | Смысл | Обязательство будущей архитектуры |
|---|---|---|
| `P` | обязательная параллельность | оба участника реально обслуживаются одновременно в заданном сценарии; заданы latency/loss/age bounds |
| `T` | управляемое time-sharing | одна session содержит оба результата, но физический ресурс переключается; UI/log показывают active owner, dwell, gaps, loss и stale |
| `Q` | параллельность только после qualification | допускается только для exact hardware pair после power/RF/timing HIL; до доказательства работает как `T` либо явно degraded |
| `X` | взаимоисключение | одновременный режим запрещён физикой, целостностью данных или safety policy |
| `A` | условно подключённый backend | требование действует только с qualified accessory; его отсутствие не считается отказом base product |
| `D` | допустимая деградация | session продолжается с явным `degraded/stale/unknown/lost`, но не подставляет выдуманный результат |

`P` не требует общего MCU или общей шины. `T` не разрешает скрывать периоды, в которых источник не наблюдался. `Q` не является обещанием до exact HIL.

## Всегда активная системная плоскость

Следующие обязанности параллельны любой пользовательской session, включая boot, maintenance и Controlled Zone:

1. физический STOP асинхронно доминирует над каждым TX-capable path и обоими принятыми MCU domains;
2. local dead-man и lease expiry прекращают новые TX независимо от UI, storage и межконтроллерной связи;
3. critical indication различает commanded TX, доступное actual-TX evidence, STOP latch, fault и unknown;
4. локальный input сохраняет путь к software cancel; hardware STOP от UI не зависит;
5. monotonic ordering, source identity, age, overflow/loss counters и bounded queues сохраняются для каждого producer;
6. storage может отставать или стать недоступным, но не блокирует STOP, dead-man, PTT release или RF safe-state;
7. watchdog/reset/brownout/update/accessory loss отменяют arming и не восстанавливают TX автоматически.

Физический STOP имеет приоритет над сохранением журнала: оборванный record допустим и восстанавливается как incomplete; задержка STOP ради flush запрещена.

## Неподвижные отношения capability

| Участники | Класс | Причина и наблюдаемый результат |
|---|---|---|
| `CA-SAFE` ↔ любой active capability | `P` с доминированием | STOP/dead-man/critical state никогда не ждут foreground tool |
| `CA-UI` ↔ любая foreground session | `P` | видимы level, armed/TX/fault/source age; телефон не является обязательным control path |
| producer ↔ `CA-STORE` | `P+D` | bounded buffering; full/slow/corrupt media даёт loss/fault, а не зависание producer |
| S3 native Wi-Fi ↔ S3 native BLE | `T` | единый принятый native 2.4 GHz domain; scheduler показывает actual dwell/preemption |
| C5 Wi-Fi 2.4 ↔ C5 Wi-Fi 5 ↔ C5 IEEE 802.15.4 | `T` | один принятый C5 RF domain не изображается как simultaneous multi-radio |
| nRF24 #1 ↔ #2 ↔ #3 в PRX/RPD hunt | `P` | три синхронных окна и три независимых состояния обязательны; radio+RF-switch substitute не проходит |
| разные роли/channel/rate/session трёх nRF24 | `P` по control/state, `Q` для simultaneous TX | full-function каждого radio сохраняется; parallel TX только contained exact-pair HIL |
| IR RX edge path ↔ IR carrier-measurement path | `P` | один captured signal обслуживается обоими C5 paths без подмены carrier guess |
| IR learn ↔ IR TX | `X` | learn и replay — разные фазы; local optical feedback не выдаётся за внешний capture |
| Si4732 RX audio ↔ codec capture/decode/storage/UI | `P` | прослушивание, запись и decode являются одной accepted receive session |
| voice RX ↔ codec/decode/storage/UI | `P` | half-duplex RX/audio/modem result сохраняется локально |
| voice RX ↔ voice TX | `X` | принятый analog voice backend half-duplex; PTT переводит session между фазами |
| voice TX ↔ PTT release/dead-man/STOP | `P` с доминированием safety | release/fault прекращает PTT независимо от application progress |
| Unit GPS ↔ U214 GNSS | `X+A` | одновременно активен ровно один GNSS backend; epochs не смешиваются |
| U214 GNSS ↔ U214 LoRa RX/TX | `Q+A+D` | единая attached session допустима; self-desense/power измеряются, fix во время TX может стать stale/unknown |
| U214 ↔ другой LoRa carrier | `X+A` | runtime активирует ровно один qualified LoRa backend |
| external NFC ↔ base device | `A+Q` | UI/storage/safety работают вместе; bus/power/field coexistence доказываются exact profile |
| USB MSC host writer ↔ firmware writer того же volume | `X` | исключено dual-writer corruption; допустим exclusive ownership либо read-only snapshot |
| update/recovery ↔ любой TX | `X` | update state всегда TX-off и disarmed |
| любой capture/import ↔ последующий replay/TX | `X` до нового arming | record остаётся inert; destination заново проверяет level/target/region/power/time |

## Radio coexistence rule без преждевременной топологии

Наличие независимых RF frontends не создаёт автоматическое право на simultaneous operation.

- mandatory receive pair из таблицы выше проектируется как `P`;
- остальные RX↔RX и RX↔TX пары из разных domains изначально `Q`: synthesis обязан оставить измеримый режим и честный `T/D` fallback;
- unqualified simultaneous TX запрещён;
- contained test может разрешить конкретную TX↔TX пару только по exact channel/power/antenna/enclosure/load fixture и no-leakage proof;
- self-desense, rail droop, interrupt latency или buffer overflow меняют capability state на `degraded/unknown`, а не молча уменьшают coverage.

Это правило не навязывает «один глобальный TX». Оно требует независимо выключать каждый TX path и не принимать параллельность до pair qualification.

## Обязательные сценарии

| ID | Сценарий | Минимально одновременный состав | Разрешённое расписание/деградация | Запрещённый ложный результат |
|---|---|---|---|---|
| `CS-01` | cold boot / recovery | safe-state, local UI, self-test, fault state | radios and accessories enumerate sequentially | boot success до проверки TX-off/STOP state |
| `CS-02` | signed update / rollback | UI, power margin, package verification, durable progress, TX-off | programmable targets update sequentially; old working image retained | restore armed state либо unsigned target ambiguity |
| `CS-03` | local file/export/service | UI, bounded parser, storage ownership, USB state | CDC/HID/MSC compose only after endpoint audit; MSC exclusive/snapshot | dual writer, import-triggered action, secret leakage |
| `CS-04` | three-sector nRF hunt | 3× simultaneous PRX/RPD, common comparison window, UI, bounded record, safety state | channel/rate sweep between windows; other 2.4 domains may be `T/D` | fake RSSI/dBm/bearing, silent skipped window or one-radio substitution |
| `CS-05` | one-shot foreground wardrive | GNSS if attached, UI, storage, privacy state, all selected producer services | S3 Wi-Fi/BLE and C5 radio modes time-share; other pairs `Q/T`; missing source explicit | protocol attribution from energy, last-known position as live, hidden gaps |
| `CS-06` | broadcast receive / record / decode | Si4732 control+RX audio, codec path, UI, storage | incompatible transmitter may mute/mark RX degraded after qualification | clean/lossless claim across mute, overflow or self-desense |
| `CS-07` | analog voice / modem | voice RX or TX phase, codec routing, UI, PTT/dead-man/STOP, bounded log | RX and TX alternate; other radios `Q/T`; storage failure does not hold PTT | full-duplex claim, TX after release/link loss, absent actual-TX proof shown as off |
| `CS-08` | IR learn and replay | during learn: both IR RX paths + UI/record; during replay: deterministic TX + safety | learn and replay phases exclusive; repeated burst bounded | 455 kHz promise, captured carrier guess as measured, sweep armed by file selection |
| `CS-09` | attached GNSS/LoRa session | selected backend, expansion identity/power state, UI/storage/safety | one GNSS and one LoRa backend; U214 pair `Q/D` around TX | mixed GNSS epochs, unknown carrier treated compatible, stale fix as live |
| `CS-10` | external NFC session | qualified frontend, local UI, protected records, removal/field fault state | sensitive operations serialized per target; relay disabled without two qualified roles | removal success, raw command bypass, one frontend called relay |
| `CS-11` | contained active security/resilience test | fresh banner, exact target/environment, action preview, selected TX path, actual-TX evidence where available, dead-man, STOP, audit | only HIL-qualified pair operation; unrelated TX remains off | banner as arming, open-air jammer, authorization standing in for spectrum law |
| `CS-12` | fault storm | STOP/dead-man, critical indication, monotonic fault record, bounded recovery | radio/accessory/storage/IPC may independently become `lost`; service resumes only disarmed | stale owner, automatic retrying TX, deadlock while logging fault |

## Scheduler semantics required by every synthesis

Each requested activity has a typed tuple:

`capability / source / requested-state / actual-state / priority / deadline-or-dwell / preemption rule / level / target / region / power / expiry`.

Each producer publishes at minimum:

`source-clock / monotonic timestamp / sync uncertainty / age / sample-or-frame count / drop count / overflow / calibration/profile ID / state`.

The state vocabulary includes `requested`, `active`, `preempted`, `degraded`, `stale`, `unsupported`, `unsampled`, `lost`, `fault` and `stopped`. Absence of evidence is never converted to `idle`, `safe`, `no target` or successful decode.

Safety priority is absolute. Voice PTT has bounded foreground real-time priority only while its separate gate is valid. Capture/UI/storage work is back-pressured or dropped with counters before safety deadlines are missed.

## Failure and conflict injection matrix

| Fault | Required immediate behavior | Required durable/visible result |
|---|---|---|
| STOP during any TX | hardware-dominant termination, no wait for IPC/UI/storage | latched STOP on independent indication; next boot disarmed |
| local owner hang or reset | local dead-man/hardware gate removes its TX | source becomes `lost/fault`; no automatic re-arm |
| controller link loss | remote leases expire; unaffected local safe RX may continue only if policy allows | requested/actual owner divergence and age visible |
| storage full/slow/corrupt/remove | producer remains bounded; drop or end session safely | incomplete/lost counts, recovery-required volume state |
| accessory remove/brownout/wrong profile | accessory TX inhibited; dependent session stops or degrades | backend unavailable, active GNSS invalid, no blanket compatibility |
| clock jump/sync loss | monotonic ordering continues; wall time marked uncertain | affected evidence carries uncertainty, no rollback/replay bypass |
| RF self-desense/coexistence failure | conflicting activity time-shares or stops | pair loses `Q` qualification until retest; coverage gap visible |
| update interruption / failed first boot | return to working image/recovery with TX-off | target identity/version/result and rollback reason visible |
| UI crash or navigation away | active action obeys its lease; BACK/panic/STOP remain effective | no hidden persistent armed state |
| low battery / rail transient / thermal limit | conservative power reduction or TX stop before undefined behavior | reason and unavailable profile visible; no maximum-power retry |

## Coverage

| Capability set | Covered by |
|---|---|
| `CA-CORE/STORE/USB/UPD/UI/SAFE/PWR/EXP` | always-active plane, `CS-01/02/03/09/10/12`, failure matrix |
| `CA-W24/BLE/W5/154/SUB/GNSS` | native-domain relations, `CS-05/09/11` |
| `CA-N24` | mandatory `P` relation, `CS-04/11` |
| `CA-RX/AUDIO` | `CS-06` |
| `CA-VOICE` | `CS-07` |
| `CA-IR` | `CS-08` |
| `CA-LORA` | U214/backend relations, `CS-09/11` |
| `CA-NFC` | external-profile relation, `CS-10` |

All 21 `CA-*` atoms from `CAP-0001` have a concurrency and failure context. No physical owner, controller count, transport, bus or GPIO was inferred. Step 2 therefore receives **«Проведено ревью»** and becomes the sole scenario input of `RES-0001`.
