# FND-0024 — 5 GHz функции требуют DFS/country/PMF/privacy gates

- Статус: **Открыто; обязательные гейты внесены в draft-требования**
- Серьёзность: regulatory/security/privacy blocker
- Затрагивает: `C-W5-01`–`C-W5-08`, scan/SoftAP/raw TX/capture/storage/UI/HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy-список каналов и общий ярлык «5 GHz» не являются разрешением на одинаковую работу во всей полосе:

- channel mask зависит от country/region profile, hardware и действующих правил;
- при automatic country policy active scan применяется на non-DFS, а DFS channels сканируются пассивно;
- C5 умеет пассивно обнаруживать radar/слушать DFS и подключаться к существующей DFS AP, но не реализует active radar detection и поэтому не может поднимать DFS SoftAP;
- hidden SSID может не обнаружиться на passive-only channel, поэтому `not found` не означает отсутствия сети;
- Protected Management Frames делают spoofed unprotected deauth/disassoc неэффективными для защищённого соединения; UI обязан показывать PMF state/unknown, а не обещать результат атаки;
- BSSID/client identifiers, location, EAPOL и payload metadata являются чувствительными данными даже при пассивном приёме.

## Обязательные гейты

- explicit region/country source, revision и effective channel/TX mask в каждой session/export;
- никакой DFS transmission/SoftAP без отдельной доказанной регуляторной реализации; текущий baseline запрещает её;
- active security tests только в Контролируемой зоне и на exact authorized target; disruptive broadcast/flood — только `BOTH` с conducted/RF-shielded no-leakage proof;
- fresh banner, non-aggression pledge, bounded duration/packet rate, local STOP и conservative power;
- identifier/payload minimization, redaction, encrypted session vault, explicit export/delete и no-background-capture default;
- PMF/hidden-SSID/packet-loss states отображаются как measured/unknown, без false certainty.

## Критерий закрытия

Region/DFS/PMF/privacy state machine реализована и проверена на target AP matrix; запрещённые каналы невозможно вооружить импортом/ручным вводом; SoftAP не стартует на DFS; capture/export/factory-reset tests подтверждают data lifecycle; Controlled-Zone TX прекращается STOP/dead-man.

## Первичные источники

- [ESP32-C5 Wi-Fi driver: 5 GHz/DFS/country behavior](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi.html)
- [ESP32-C5 Wi-Fi security: Protected Management Frames](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi-security.html)

