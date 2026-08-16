# REV-0002V — ревью пререквизитов C5 Wi-Fi 5 GHz и IEEE 802.15.4

- Статус: **Проведено ревью пререквизитов**
- Дата: 2026-08-16
- Этап: 2 — возможности и исключения
- Входы: `C-W5-01`–`C-W5-09`, `OUT-01`, legacy hardware/firmware docs, current `c5-buses.tsx`, Espressif primary documentation
- Выходы: `FND-0022`–`FND-0025`, `IMP-0018`, draft `REQ-W5-0001`

## Проверенные пререквизиты

| Область | Проверка | Результат |
|---|---|---|
| Hardware identity | exact C5 variant, supplier candidate, RF connector/pad | legacy N8R4/`C49308183` и комментарий `ANT2=u.FL` не проходят; source безопасно исправлен на current N8R8/`C51950748`, ANT1/ANT2 разделены; final AVL/RF qualification открыт (`FND-0022`) |
| Band model | 2.4/5 GHz capabilities | 1T1R C5 переключает band; `AUTO` не simultaneous dual-band |
| Passive RX | promiscuous packet classes | management/control/data доступны; completeness/loss/radiotap/EAPOL ещё требуют target fixture |
| Public raw TX | exact frame classes | только beacon/probe request/probe response/action и non-QoS data; arbitrary management/deauth не обещаны (`FND-0023`) |
| Private patch | feasibility and openness | сторонний version-locked patched `libnet80211` доказывает возможность, но не provenance/redistribution/update baseline; отдельное решение обязательно |
| 5 GHz regulation | country/DFS/SoftAP | active non-DFS/passive DFS scan under auto policy; DFS SoftAP не поддержан; region/channel mask и hidden-SSID uncertainty обязательны (`FND-0024`) |
| Security/privacy | PMF, identifiers, capture | PMF меняет результат deauth; passive capture остаётся sensitive; уровни Main/Lab/Controlled Zone разнесены |
| Raw 802.15.4 | ED/CCA/promiscuous/TX | официально доступно на C5; passive-only legacy ceiling опровергнут |
| Full stacks | Thread/Zigbee | OpenThread и Zigbee roles технически доступны без нового RF BOM; Zigbee core proprietary prebuilt, поэтому нужен owner scope (`FND-0025`, `IMP-0018`) |
| Coexistence | Wi-Fi/BLE/802.15.4 | один shared 2.4 GHz RF path с preemption; simultaneous performance не обещается, cross-radio HIL обязателен |
| Cost | zero-loss opportunity | новый 802.15.4 RF hardware не нужен; N8R8 может улучшить availability/PSRAM без роста цены, но экономия не заявляется до AVL quote |

## Исправленные несоответствия

1. `c5-buses.tsx`: `U20` candidate N8R4/`C49308183` заменён на current-standard N8R8/`C51950748`.
2. `c5-buses.tsx`: ложный комментарий `ANT2 (u.FL feed)` заменён точным разделением module-integrated `ANT1` connector и disabled `ANT2` pad.
3. Parts-engine netlist выявил, что N8R8 thermal lands называются `EPAD1..EPAD9`; неверные legacy `GND5..GND13` заменены, все девять EPAD подключены к GND, `ANT2` остаётся намеренно `NOT_CONNECTED`.
4. `AUD-0001/OUT-01`: raw TX больше не описывается как произвольные management frames; public и patched paths разделены.
5. Draft `REQ-W5-0001`: simultaneous dual-band/full monitor/DFS SoftAP/deauth baseline и passive-only 802.15.4 ceiling не наследуются.

## Открытые элементы, не скрытые статусом ревью

- `FND-0022`: final module/antenna/power/STOP/TX-live/EMC/HIL;
- `FND-0023`: public packet proof, EAPOL/PMKID experiment и возможная private-binary boundary;
- `FND-0024`: country/DFS/PMF/privacy implementation and HIL;
- `FND-0025`: ordinary Thread/Zigbee scope и coexistence acceptance;
- `FND-0001`, `FND-0002`, `FND-0007`: transport, BLE owner и independent STOP;
- `IMP-0003`: passive EAPOL/PMKID remains proposal until target proof;
- `IMP-0018`: требуется один продуктовый ответ перед финальным requirement review.

## Итог

Пререквизиты проверены, противоречия локализованы, безопасные source/document corrections выполнены. Сам `REQ-W5-0001` остаётся **«На ревью»**, потому что выбор A/B/C по ordinary Thread/Zigbee существенно меняет целевой продукт и не может быть автоподтверждён.
