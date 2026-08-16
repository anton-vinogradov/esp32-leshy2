# INV-0004 — итоговая матрица саморевью и freeze wishlist

- Статус: **Проведено ревью прежних 125 leaves; competitor delta требует повторного ревью (`FND-0040`)**
- Дата: 2026-08-16
- Основание: делегированное владельцем саморевью, `DEC-0022`, `DEC-0023`
- Входы: `INV-0001`–`INV-0003`, все reviewed `REQ-*`, `AUD-0001`
- Полнота: **125 из 125 legacy/addition candidates получили contract; 10 source-extras декомпозированы в 12 независимых решений**

## Принцип решения

> Этот snapshot остаётся доказательством полноты прежнего source universe, но
> больше не является финальным completeness gate. Новые вопросы
> `W-EXTRA-11..17` перечислены в `INV-0002/AUD-0004`; их актуальный disposition
> ведётся ниже и не переписывает прежний 125-leaf snapshot.

Update 2026-08-16: `W-EXTRA-11` принят как external passive M5-style Port-B
profile по `DEC-0033/REQ-IBTN-0001`. M5-first Unit/Cap плюс отдельный
high-throughput class без native M5-Bus принят `DEC-0034/REQ-EXT-0001`;
`W-EXTRA-12` принят `DEC-0035/REQ-FIDO-0001`; `W-EXTRA-13` отклонён
`DEC-0036`; `W-EXTRA-14` fact review завершён `AUD-0008`, owner decision и
`W-EXTRA-15..17` открыты.

## Current competitor delta disposition

| Leaf ID | Result | Decision | Product/BOM boundary |
|---|---|---|---|
| `W-EXTRA-11` | iButton/1-Wire contact tool | `accepted-external` | protected Port-B timing/electrical profile + replaceable passive adapter; no integrated base contacts; read/emulate/write separately qualified |
| `W-EXTRA-12` | modern FIDO2/CTAP USB authenticator + U2F compatibility | `accepted-main` | `DEC-0035/REQ-FIDO-0001`: exclusive open personal authenticator; device-bound/non-exportable; no certification overclaim |
| `W-EXTRA-13` | haptic feedback through the product enclosure | `rejected-by-owner` | `DEC-0036`: no motor, special profile, mount or haptic HIL; generic Port-B remains generic |
| `W-EXTRA-14` | IMU measurement-pose metadata | `needs-owner` | `AUD-0008/FND-0045/IMP-0031`: optional external profile recommended; 6-axis ≠ heading/RF bearing |
| `W-EXTRA-15..17` | remaining current competitor questions | `needs-owner` | resolved one by one through `AUD-0004`; no silent target inclusion |

1. Полезный пользовательский результат сохраняется.
2. Нечастая функция, требующая нового radio/compute/certification class, сохраняется как optional expansion или `defer-release`, а не увеличивает base BOM.
3. Опасный сценарий не удаляется только из-за опасности: он получает Main/Lab/Controlled Zone boundary, `AUTHORIZED_TARGET`, `ISOLATED_ONLY` или `BOTH` и технический interlock.
4. Недоказуемое обещание заменяется измеримым результатом: RPD не RSSI, sequential sweep не SDR/FFT, passive capture не lossless monitor, RSSI не расстояние, module band не silicon band.
5. Конкретные MCU, GPIO, transport и placement не являются частью wishlist freeze.

## Покрытие 125 кандидатных строк

Диапазон означает каждую leaf-строку, а `REQ-*` содержит её независимый disposition и zero-loss/acceptance boundary.

| Wishlist-группа | Leaf-строки | Кол-во | Reviewed contract |
|---|---|---:|---|
| `WG-01` Platform/UI/safety/storage | `C-SYS-01..11` | 11 | `REQ-SYS-0001` |
|  | `C-X-01..04`, `C-X-07`, `C-X-09`, `C-X-11` | 7 | `REQ-X-0001`, пересечения `REQ-SYS-0001` |
|  | `C-HWX-01`, `C-HWX-03..04` | 3 | `REQ-X-0001`, `REQ-SYS-0001` |
| `WG-02` Navigation/log/sessions | `C-GPS-01..04` | 4 | `REQ-GNSS-0001` |
|  | `C-X-05..06`, `C-X-08`, `C-X-10` | 4 | `REQ-X-0001` |
|  | `C-UX-01`, `C-UX-03` | 2 | `REQ-X-0001` |
| `WG-03` Broadcast/voice | `C-RX-01..07` | 7 | `REQ-RX-0001` |
|  | `C-VHF-01..07` | 7 | `REQ-VHF-0001` |
| `WG-04` Consumer IR | `C-IR-01..05` | 5 | `REQ-IR-0001` |
| `WG-05` HF NFC/RFID | `C-NFC-01..10` | 10 | `REQ-NFC-0001` |
| `WG-06` Wi-Fi/IP | `C-W24-01..12` | 12 | `REQ-W24-0001` |
|  | `C-W5-01..08` | 8 | `REQ-W5-0001` |
| `WG-07` BLE/802.15.4 | `C-BLE-01..12` | 12 | `REQ-BLE-0001` |
|  | `C-W5-09`, `C-UX-02` | 2 | `REQ-W5-0001`, `REQ-X-0001` |
| `WG-08` 3×nRF24 | `C-N24-01..10` | 10 | `REQ-N24-0001` |
| `WG-09` Sub-GHz/LoRa | `C-SUB-01..11` | 11 | `REQ-SUB-0001` |
|  | `C-LORA-01..09`, `C-HWX-02` | 10 | `REQ-LORA-0001`, `REQ-X-0001` |
| **Итого** |  | **125** | **без пропусков и двойного resource demand** |

## Саморевью дополнительных хотелок

Две исходные строки были некорректно склеены и декомпозированы. Это не добавление scope, а устранение двусмысленности.

| Leaf ID | Самостоятельный пользовательский результат | Решение | Product/BOM boundary |
|---|---|---|---|
| `W-EXTRA-01` | passive EAPOL/PMKID capture | `conditional` | Lab, authorized network, supported Wi-Fi path and fixture proof; no onboard cracking; `REQ-W24-09`/`REQ-W5-08` |
| `W-EXTRA-02` | BLE connection-follow sniffer | `defer-release`, optional | отдельный nRF52-class accessory; selected native BLE не урезается и base BOM не растёт |
| `W-EXTRA-03` | ordinary Bluetooth Mesh | `defer-release`, optional software | selected native-BLE profile after key/flash/RAM/licence/HIL proof; no new radio |
| `W-EXTRA-04` | Bluetooth Classic/BR/EDR | `defer-release`, optional | только внешний controller при появлении конкретного use case; не base board |
| `W-EXTRA-05` | дополнительные HF/VHF/30–64/DRM paths | `defer-release`, optional | отдельный qualified receiver/SDR expansion; Si4732 claims не расширяются фиктивно |
| `W-EXTRA-06A` | digital voice | `defer-release`, optional | отдельный codec/protocol/backend может работать half-duplex; не требует автоматически второго RF path |
| `W-EXTRA-06B` | full-duplex repeater | `defer-release`, optional | отдельная dual-RF/duplex-isolation architecture; не base SA518/SA868 promise |
| `W-EXTRA-07` | wideband SDR + Linux analytics | `defer-release`, optional | внешний SDR/compute profile or companion; base device remains autonomous |
| `W-EXTRA-08` | cellular/GSM/LTE | `defer-release`, optional | tether/external certified modem profile only after use case; no base modem/SIM BOM |
| `W-EXTRA-09` | LF 125 kHz RFID | `defer-release`, optional | отдельный external frontend; U216 не переименовывается в LF device |
| `W-EXTRA-10A` | two-frontend NFC relay | `defer-release`, optional | Controlled Zone `AUTHORIZED_TARGET`; два независимых qualified frontend and timing proof |
| `W-EXTRA-10B` | heavy key-recovery compute | `defer-release`, off-device | authorized encrypted export to owner-controlled compute; no fictitious on-device performance claim |

## Что сознательно не попало в base BOM

Dedicated BLE sniffer, Bluetooth Classic controller, additional HF/VHF/SDR, second full-duplex voice path, Linux compute, cellular modem, LF 125 kHz frontend, second NFC frontend and heavy recovery compute. Их attachment requirements будут формироваться только при выпуске соответствующего optional profile. Это снижает стоимость и resource pressure базового устройства без удаления записи о желаемом результате.

## Freeze gate

- [x] 125/125 строк распределены и имеют reviewed contract;
- [x] все owner wishes `W-OWN-01..16` сохранены как invariants;
- [x] смешанные строки декомпозированы;
- [x] опасные функции получили трехуровневые gates и containment;
- [x] legacy ceilings пересмотрены на уровне продуктовых требований;
- [x] каждое дополнительное желание получило disposition;
- [x] base, optional expansion и deferred-release scope разделены;
- [x] zero-loss boundary запрещает скрытое урезание при оптимизации стоимости;
- [x] MCU/GPIO/transport/layout не зафиксированы преждевременно;
- [x] владелец делегировал полноту и решение саморевью.

**Исторический wishlist был заморожен.** `FND-0040` применяет предусмотренный
change-request путь: competitor delta обновляет demand model и переводит
затронутые product/architecture artifacts в повторное ревью до нового freeze.
