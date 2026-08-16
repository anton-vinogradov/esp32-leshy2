# FND-0021 — nRF24 security/BLE claims смешивают discovery, exploitation и недоказанный reuse

- Статус: **Открыто; декомпозировано draft `REQ-N24-0001` и `IMP-0017`**
- Серьёзность: security boundary/capability/licence blocker
- Затрагивает: `C-N24-04`–`C-N24-09`, storage, BLE ownership и firmware reuse
- Обнаружено: 2026-08-16

## Несоответствие

Legacy объединяет под короткими именами действия с разным риском и proof:

- pseudo-promiscuous ESB discovery, capture конкретного адреса, follow/hop и software CRC — разные операции; unknown-address capture даёт false positives и не является universal raw 2.4 sniffer;
- MouseJack passive discovery не доказывает уязвимость; confirmation/keystroke injection уже даёт управление компьютером и требует Controlled Zone `AUTHORIZED_TARGET`;
- KeySniffer plaintext HID payload является чувствительным перехватом даже без TX и требует того же уровня, а не обычной Lab-записи;
- address mapper/brute-force активно посылает probes; широкий sweep может задеть неизвестные устройства и требует `BOTH`;
- nRF24 не имеет BLE controller/Link Layer. Software может лишь имитировать/принимать ограниченную часть legacy 1 Mbit/s advertising с software whitening/CRC и payload/timing limits; это не full BLE scan, connection follow или standard compliance;
- jamming не становится законным от одного разрешения владельца target: нужен conducted/RF-shielded environment и применимый regulatory basis; open-air mode не входит в product contract.

## Licence/provenance

Публичный Bastille MouseJack research firmware распространяется под GPL-3.0, а TMRh20 `RF24` — под GPL-2.0. MIT-обёртка или чужой проект, использующий эти зависимости, не превращает их код в permissive. Для целевого open firmware нужен собственный ESP-IDF driver/clean implementation либо осознанно совместимая архитектура лицензий, per-file SPDX, SBOM и provenance test vectors.

Активный firmware-репозиторий сейчас не содержит доказанного C5 nRF driver, parsers, security state machine или HIL; legacy draft не является implementation proof.

## Критерий закрытия

- `REQ-N24-0001` разносит passive metadata, sensitive payload capture, active confirmation/injection, brute-force и interference tests по отдельным gates.
- BLE compatibility получает честный support matrix и не дублирует normal BLE backend под ложным именем.
- Реализация проходит source/licence review, parser fuzzing и fixture-based HIL на exact authorized devices.
- Любая disruptive функция физически ограничена conducted/shielded test mode и общим STOP/dead-man contract.

## Первичные источники

- [Bastille MouseJack research and affected-device model](https://bastille.net/research/vulnerabilities-mousejack/)
- [Bastille MouseJack research tools, GPL-3.0](https://github.com/BastilleResearch/mousejack)
- [Bastille KeyJack/KeySniffer research boundary](https://bastille.net/research/wireless-peripherals/)
- [RF24 project licence](https://github.com/nRF24/RF24)
- [pyRF24 fake-BLE limitations](https://nrf24.github.io/pyRF24/ble_api.html)
- [FCC jammer enforcement basis](https://docs.fcc.gov/public/attachments/DA-14-1785A1_Rcd.pdf)
- [Ofcom: radio spectrum and the law](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law)

