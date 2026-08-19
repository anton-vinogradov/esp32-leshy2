# FND-0027 — BLE protocol labels не доказывают emulation, exploit или права распространения

- Статус: **Открыто; capability/security/licence gates внесены в draft**
- Серьёзность: security/privacy/licence/compatibility blocker
- Затрагивает: `C-BLE-03`–`C-BLE-12`, `C-UX-01`, `C-UX-02`, storage/import/update/HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy-названия `AirTag/Find My`, `Continuity`, `Flipper`, `iBeacon`, `BadBLE`, `Sour Apple`, pairing spam и GATT flood смешивают:

- открытые standard GAP/GATT/HID primitives;
- изменяемые vendor-specific advertising signatures;
- trademark/specification licences и corpus provenance;
- ordinary owner use, defensive detection, impersonation, credential handling и явный DoS.

BLE controller способен передать заданный поддержанный advertising/GATT/HID payload, но это не доказывает semantic compatibility, сертификацию, уязвимость peer или законность corpus. Apple iBeacon production technology/specification имеет отдельную use licence; сторонний dump/таблица не может автоматически войти в открытый release. Find My identifiers меняются и сеть end-to-end encrypted; advertising fingerprint не даёт generic tracker identity, account access или право эмуляции.

GATT enumeration и HID также требуют разделения: обычное pairing/owner service/keyboard input может быть Main, а security enumeration, scripted HID injection и identity imitation требуют exact authorized target. Pairing/crash/connection floods и interference являются disruptive и допускаются только в Controlled Zone `BOTH` на conducted/RF-shielded fixture.

## Обязательные гейты

- каждый signature/corpus имеет source, licence/rights, version, hash, tested peer matrix и confidence;
- official Bluetooth assigned numbers отделены от эвристических vendor signatures;
- import остаётся inert, parser bounded/fuzzed, arbitrary bytes не обходят zone/target/rate gates;
- secure ordinary profiles используют LE Secure Connections, bonding/allowlist, RPA и encrypted key storage; `Just Works` явно показывает отсутствие MITM proof;
- credentials, identifiers, bond keys и location находятся в encrypted typed vault с explicit export/delete/reset;
- active tools имеют fresh banner, exact target/fixture, preview, conservative power, packet/time bound, dead-man и STOP;
- отсутствие vendor-response/crash не выдаётся за patched/safe, а успешный packet TX — за полноценную protocol emulation.

## Критерий закрытия

Profile-by-profile fixture/HIL доказывает packet schema, peer behavior, security level, rate/timeout/STOP, false-positive/negative reporting и corpus rights. Непроверенный vendor protocol маркируется `experimental/unknown`; закрытый или несовместимый corpus не попадает в release.

## Первичные источники

- [ESP-IDF BLE peripheral/security example](https://github.com/espressif/esp-idf/blob/master/examples/bluetooth/nimble/bleprph/README.md)
- [ESP-IDF BLE HID device example](https://github.com/espressif/esp-idf/blob/master/examples/bluetooth/bluedroid/ble/ble_hid_device_demo/README.md)
- [Bluetooth SIG Security and Privacy Best Practices](https://www.bluetooth.com/download/bluetooth-security-and-privacy-best-practices-guide/)
- [Apple iBeacon licence](https://developer.apple.com/ibeacon/)
- [Apple unwanted-tracker guidance](https://support.apple.com/en-us/119874)

