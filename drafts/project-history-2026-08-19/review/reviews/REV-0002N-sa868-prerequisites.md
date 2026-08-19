# REV-0002N — ревью пререквизитов analog voice/SA868

- Статус: **Проведено ревью**
- Подшаг: 2N — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0011`–`FND-0014`, draft `REQ-VHF-0001`, `IMP-0014`
- Дата: 2026-08-16

## Проверено

- `C-VHF-01`–`C-VHF-07`, `OUT-07` и audio/storage/GNSS/network/TX-safety пересечения получили будущие requirement IDs;
- current UHF SA868S fallback отделён от VHF variant и предложенного dual-band SA518;
- официальный конфликт 400–480 RF specification против 400–470 AT range не скрыт;
- current artifact исправлен по `FND-0011`: PTT receive-default, PD power-down-default и H/L low-power ceiling заданы аппаратно;
- high-power временно недоступен до fail-safe controllable H/L и общего pin/safety budget, а не включён firmware default;
- `FND-0007` не объявлен закрытым: PCA9555 всё ещё не является независимым STOP/PTT kill;
- channel sweep/binary carrier и raw vendor RSSI отделены от dBm и от tone scan;
- CTCSS/DCS tone scan сохранён только как conditional ES8311 host decode с filter/corpus proof;
- `FND-0013` фиксирует отсутствие mic capture: VOX честно `defer`, manual PTT не блокирован;
- CEPT PMR446 source проверен; external SMA/programmable module не выдан за licence-exempt equipment, `FND-0014` закрыт запретом ложного preset claim;
- ordinary manual voice, автоматические transmitter modes и retransmission разделены по разным gates;
- parrot/cross-band relay остаются default-off Lab, а не обычным Main auto-retransmitter;
- DTMF decode не превращён в unauthenticated command execution;
- APRS/AX.25/KISS, iGate, SSTV и beacon разделены и получили protocol/profile/privacy/STOP prerequisites;
- proprietary SA518 short data не назван AX.25/APRS;
- true duplex/digital voice не объявлены невозможными для продукта: current backend ceiling сохранён как `defer` для отдельного hardware;
- новый SA518 рассмотрен как реальный обход UHF ceiling, но его площадь, pinout, 1 W peak, supply/price и maturity не скрыты;
- на момент аудита открыт ровно один owner-level выбор: `IMP-0014`.

## Проверка артефакта

`npm run build` успешно сгенерировал объединённый tsCircuit board с тремя новыми safe-state components. `tsci export ... readable-netlist` был остановлен после длительного отсутствия результата; поэтому netlist/DRC не объявлены пройденными и повторяются на stage-8 generation environment. Source-level references к real `U31.pin7`, `SA868_PTT`, `SA868_PD`, `V3V3` и GND проверены.

## Результат

Аудит пререквизитов analog voice/modem capability-среза получил статус **«Проведено ревью»**. `REQ-VHF-0001` остаётся **«На ревью»** до решения `IMP-0014`; затем требуются decision propagation, закрытие либо уточнение `FND-0012` и отдельный финальный review artifact.

Final module/BOM, independent STOP, controllable H/L, RF/legal profiles, audio/VOX, protocol interoperability, storage/network и HIL не объявлены реализованными: это доказательства последующих стадий.

Последующее состояние: владелец принял `IMP-0014/A` в `DEC-0016`, propagation review выполнен в `REV-0002O`, а `REQ-VHF-0001` получил статус **«Проведено ревью»**.
