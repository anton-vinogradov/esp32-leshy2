# REV-0002X — ревью пререквизитов native Bluetooth LE

- Статус: **Проведено ревью пререквизитов**
- Дата: 2026-08-16
- Этап: 2 — возможности и исключения
- Входы: `C-BLE-01`–`C-BLE-12`, `OUT-03`, `OUT-04`, cross-repository legacy docs, current S3/C5 decisions, Espressif/Bluetooth SIG/Nordic/Apple primary sources
- Выходы: уточнённый `FND-0002`, `FND-0026`, `FND-0027`, `IMP-0019`, `IMP-0020`, draft `REQ-BLE-0001`

## Проверенные пререквизиты

| Область | Проверка | Результат |
|---|---|---|
| S3 baseline | PHY, advertising, roles | 1M/2M/Coded, advertising extensions/multiple sets, scan+advertise и central+peripheral покрывают legacy baseline |
| C5 delta | новые Link-Layer функции | technical superset имеет дополнительные unrequested features, но делит radio с accepted IEEE 802.15.4; не основание переносить baseline молча |
| Ownership | UI/IPC/coexistence/cost | S3 owner сохраняет capability без BOM, BLE IPC и C5 Thread/Zigbee contention; `IMP-0019/A` рекомендован |
| Host stack | NimBLE/Bluedroid | оба доступны; NimBLE меньше по heap/flash, но exact profile/security matrix остаётся firmware-stage proof |
| Native observation | scan vs connection follow | advertising scan поддержан; promiscuous third-party connection follow не документирован, требует отдельного nRF Sniffer path (`IMP-0004`) |
| Identity/privacy | RPA/NRPA/signatures | address/OUI/company/signature не равны stable identity; IRK resolution и confidence states обязательны |
| Proximity | RSSI/distance/direction | RSSI — rough evidence, не метры; AoA/AoD требует antenna architecture, которой нет |
| Tracker safety | AirTag/Find My | полезный conditional detector возможен, но rotating identifiers и proprietary network исключают owner/intent/universal detection claims |
| GATT/HID | ordinary vs security | official central/peripheral/GATT/SMP/HID primitives доступны; pairing/ordinary input отделены от enumeration/script injection |
| Vendor protocols | Continuity/iBeacon/Find My | packet TX не доказывает compatibility; corpus/spec licence, version и peer HIL обязательны |
| Disruptive tests | spam/crash/flood/jam | только Controlled Zone `BOTH`, conducted/RF-shielded; native jammer не обещан |
| Extra capability | Bluetooth Mesh | официально доступно без нового radio, но legacy не просил; зафиксировано как отдельное ⚠️ `IMP-0020`, не включено |
| Cost | single vs dual owner/sniffer | S3/C5 уже в BOM; single S3 owner снижает software/power/test cost. Dedicated connection sniffer — реальный дополнительный hardware/accessory cost |

## Открытые элементы

- `IMP-0019`: ровно один owner-level ответ A/B/C;
- `IMP-0017`: native BLE vs nRF24 compatibility boundary финализируется вместе с owner;
- `IMP-0004`: dedicated connection sniffer рассматривается следующим отдельным решением;
- `IMP-0020`: найденный extra Bluetooth Mesh рассматривается только после ownership;
- `FND-0007`, RF coexistence, exact host profile, storage/privacy/licence и HIL остаются implementation gates.

## Итог

Пререквизиты проверены и draft `REQ-BLE-0001` сформирован. Сам capability contract остаётся **«На ревью»**, потому что ownership меняет IPC, coexistence, identity/key custody и test surface и не может быть автоподтверждён. Рекомендуется `IMP-0019/A`: S3 — единственный baseline native-BLE owner, C5 BLE default-off, nRF24 — только limited compatibility/research.

